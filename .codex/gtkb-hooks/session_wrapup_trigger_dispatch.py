from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(r"E:\GT-KB")
OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"
LIFECYCLE_GUARD_PATH = OUT_DIR / "session-lifecycle-guard.json"
HARNESS_NAME = "codex"
# Parity marker: prime-builder role is discovered by session_self_initialization.py.

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


def _emit_no_context() -> None:
    print("{}")


def _startup_input_gate_active() -> bool:
    try:
        state = json.loads(LIFECYCLE_GUARD_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    if not isinstance(state, dict):
        return False
    return state.get("discard_next_user_prompt") is True or state.get("startup_response_pending") is True


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_input = _read_stdin()
    prompt = _extract_prompt(raw_input)
    (OUT_DIR / "last-wrapup-trigger-input.json").write_text(raw_input, encoding="utf-8")

    if _startup_input_gate_active():
        _emit_no_context()
        return 0

    if not _is_wrapup_trigger(prompt):
        _emit_no_context()
        return 0

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "session_self_initialization.py"),
            "--project-root",
            str(PROJECT_ROOT),
            "--emit-wrapup",
            "--force-wrapup",
            "--fast-hook",
            "--harness-name",
            HARNESS_NAME,
        ],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
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
    print(json.dumps(_hook_payload(f"{directive}\n\n{context}"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
