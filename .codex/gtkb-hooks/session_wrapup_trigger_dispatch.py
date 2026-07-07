from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(r"E:\GT-KB")
OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"
HARNESS_NAME = "codex"
# Parity marker: prime-builder role is discovered by session_self_initialization.py.

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))
from groundtruth_kb.session.envelope import (  # noqa: E402
    EnvelopeError,
    load_current,
    open_session,
    resolve_harness_identity,
)
from groundtruth_kb.session.topic_router import (  # noqa: E402
    handle_topic_command,
    parse_topic_command,
    render_topic_context,
)
from groundtruth_kb.session.wrap import is_canonical_wrap_trigger, run_wrap  # noqa: E402

from scripts.gtkb_session_id import MARKER_CONTINUITY_ORDER, resolve_session_id  # noqa: E402
from scripts.harness_identity import resolved_harness_id  # noqa: E402
from scripts.session_role_resolution import resolve_interactive_session_role_details  # noqa: E402

ACCEPTED_TRIGGER_PHRASES = {
    "wrap up",
    "wrap up this session",
    "wrap up the session",
    "wrap up the current session",
    "session wrap up",
    "run session wrap up",
    "perform session wrap up",
    "do session wrap up",
    "close this session",
    "close the session",
    "close the current session",
    "end this session",
    "end the session",
    "end the current session",
    "new session",
    "fresh session",
    "start a new session",
    "start a fresh session",
    "begin a new session",
    "begin a fresh session",
    "open a new session",
    "open a fresh session",
    "prepare a new session",
    "prepare a fresh session",
    "initialize a new session",
    "initialize a fresh session",
    "start fresh",
    "begin fresh",
}
_VALID_ROLE_PROFILES = frozenset({"prime-builder", "loyal-opposition"})


def _no_window_subprocess_kwargs() -> dict[str, object]:
    kwargs: dict[str, object] = {}
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return kwargs


def _read_stdin() -> str:
    try:
        return sys.stdin.read()
    except Exception:
        return ""


def _direct_prompt_value(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("prompt", "userPrompt", "user_prompt", "message", "content", "text", "input"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
        for value in payload.values():
            found = _direct_prompt_value(value)
            if found:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _direct_prompt_value(value)
            if found:
                return found
    return ""


def _extract_prompt(raw_input: str) -> str:
    raw_input = raw_input.strip()
    if not raw_input:
        return ""
    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError:
        return raw_input
    return _direct_prompt_value(payload) or raw_input


def _is_wrapup_trigger(prompt: str) -> bool:
    if is_canonical_wrap_trigger(prompt):
        return True
    normalized = " ".join(prompt.strip().split()).lower()
    normalized = normalized.replace("wrap-up", "wrap up")
    normalized = re.sub(r"[.!?]+$", "", normalized).strip()
    normalized = re.sub(r"^please\s+", "", normalized).strip()
    normalized = re.sub(r"\s+please$", "", normalized).strip()
    return normalized in ACCEPTED_TRIGGER_PHRASES


def _hook_payload(context: str) -> dict[str, dict[str, str]]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }


def _dump_payload(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=True)


def _emit_no_context() -> None:
    print("{}")


def _lifecycle_guard_path() -> Path:
    override = os.environ.get("GTKB_LIFECYCLE_GUARD_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return PROJECT_ROOT / "harness-state" / HARNESS_NAME / "session-lifecycle-guard.json"


def _startup_input_gate_active() -> bool:
    try:
        state = json.loads(_lifecycle_guard_path().read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    if not isinstance(state, dict):
        return False
    return state.get("discard_next_user_prompt") is True or state.get("startup_response_pending") is True


def _persistent_harness_id() -> str:
    harness_id = resolved_harness_id(PROJECT_ROOT, harness_name=HARNESS_NAME)
    if not harness_id:
        raise RuntimeError(f"Could not resolve persistent harness identity for {HARNESS_NAME}")
    return harness_id


def _current_session_id() -> str | None:
    try:
        session_id = resolve_session_id(order=MARKER_CONTINUITY_ORDER)
    except Exception:  # noqa: BLE001 - prompt hook must fail soft.
        return None
    return session_id or None


def _interactive_role_details() -> dict[str, str | None]:
    try:
        return resolve_interactive_session_role_details(
            PROJECT_ROOT,
            current_session_id=_current_session_id(),
            harness_name=HARNESS_NAME,
        )
    except Exception:  # noqa: BLE001 - role evidence must not block normal prompt handling.
        return {}


def _interactive_role_profile() -> str | None:
    role = _interactive_role_details().get("interactive_resolved_role")
    return role if role in _VALID_ROLE_PROFILES else None


def _write_role_latch_diagnostic(
    *,
    details: dict[str, str | None],
    current_role: str | None,
    opened_envelope: bool,
) -> None:
    try:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / "last-session-role-latch.json").write_text(
            json.dumps(
                {
                    "harness_name": HARNESS_NAME,
                    "interactive_resolved_role": details.get("interactive_resolved_role"),
                    "interactive_role_source": details.get("interactive_role_source"),
                    "durable_registry_role": details.get("durable_registry_role"),
                    "authority_mode": details.get("authority_mode"),
                    "current_envelope_role": current_role,
                    "opened_envelope": opened_envelope,
                },
                ensure_ascii=True,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def _ensure_session_role_latched() -> str | None:
    """Ensure hook-created envelopes start from session-role evidence."""

    details = _interactive_role_details()
    role = details.get("interactive_resolved_role")
    if role not in _VALID_ROLE_PROFILES:
        return None
    try:
        harness_id = _persistent_harness_id()
        resolved_name, resolved_id = resolve_harness_identity(
            PROJECT_ROOT,
            harness_name=HARNESS_NAME,
            harness_id=harness_id,
        )
        current = load_current(PROJECT_ROOT, resolved_name)
        current_role = str(current.get("role_resolved") or current.get("role") or "") if current else None
        opened_envelope = False
        if not (isinstance(current, dict) and current.get("status") == "open"):
            open_session(
                PROJECT_ROOT,
                harness_name=resolved_name,
                harness_id=resolved_id,
                role=role,
            )
            opened_envelope = True
        _write_role_latch_diagnostic(
            details=details,
            current_role=current_role or None,
            opened_envelope=opened_envelope,
        )
    except Exception:  # noqa: BLE001 - prompt hook must not block topic/wrap handling.
        return role
    return role


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_input = _read_stdin()
    prompt = _extract_prompt(raw_input)
    (OUT_DIR / "last-wrapup-trigger-input.json").write_text(raw_input, encoding="utf-8")

    if _startup_input_gate_active():
        _emit_no_context()
        return 0

    topic_command = parse_topic_command(prompt)
    if topic_command is not None:
        try:
            _ensure_session_role_latched()
            result = handle_topic_command(
                PROJECT_ROOT,
                topic_command,
                harness_name=HARNESS_NAME,
                harness_id=_persistent_harness_id(),
            )
            (OUT_DIR / "last-topic-envelope-command.json").write_text(
                json.dumps(result, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            print(_dump_payload(_hook_payload(render_topic_context(result))))
        except EnvelopeError as exc:
            context = (
                "# GroundTruth-KB Topic Envelope Command Failed\n\n"
                f"`{topic_command.raw}` matched the strict topic-envelope command grammar, "
                f"but the envelope runtime rejected it: {exc}"
            )
            print(_dump_payload(_hook_payload(context)))
        return 0

    if not _is_wrapup_trigger(prompt):
        _emit_no_context()
        return 0

    runtime_context = ""
    if is_canonical_wrap_trigger(prompt):
        try:
            _ensure_session_role_latched()
            wrap_result = run_wrap(
                PROJECT_ROOT,
                harness_name=HARNESS_NAME,
                harness_id=_persistent_harness_id(),
                wrap_outcome="canonical_wrap",
            )
            (OUT_DIR / "last-session-envelope-wrap.json").write_text(
                json.dumps(
                    {
                        "archive_path": str(wrap_result["archive_path"]),
                        "session_id": wrap_result["session_id"],
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            runtime_context = str(wrap_result["summary"])
        except EnvelopeError as exc:
            runtime_context = f"# GroundTruth-KB Session Envelope Wrap Failed\n\n{exc}"

    command = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "session_self_initialization.py"),
        "--project-root",
        str(PROJECT_ROOT),
        "--emit-wrapup",
        "--force-wrapup",
        "--fast-hook",
        "--harness-name",
        HARNESS_NAME,
        "--harness-id",
        _persistent_harness_id(),
    ]
    role_profile = _interactive_role_profile()
    if role_profile:
        command.extend(["--role-profile", role_profile])

    result = subprocess.run(
        command,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
        **_no_window_subprocess_kwargs(),
    )
    (OUT_DIR / "last-wrapup-trigger.json").write_text(result.stdout, encoding="utf-8")
    (OUT_DIR / "last-wrapup-trigger.err").write_text(result.stderr, encoding="utf-8")

    context = result.stdout.strip()
    try:
        payload = json.loads(context)
        context = str(payload.get("additionalContext") or context)
    except json.JSONDecodeError:
        pass

    if result.returncode != 0:
        context = (
            "# GroundTruth-KB Wrap-Up Trigger Failed\n\n"
            f"The explicit session wrap-up trigger matched, but wrap-up generation exited {result.returncode}.\n\n"
            f"Diagnostics: `{OUT_DIR / 'last-wrapup-trigger.err'}`"
        )

    directive = (
        "# GroundTruth-KB Explicit Wrap-Up Trigger\n\n"
        "Mike used an explicit phrase indicating intent to begin a new session. "
        "Before normal task work, present the wrap-up report below and ask whether to proceed into fresh-session startup."
    )
    full_context = "\n\n".join(part for part in (directive, runtime_context, context) if part)
    print(_dump_payload(_hook_payload(full_context)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
