from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(r"E:\GT-KB")
OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"
STARTUP_SERVICE = PROJECT_ROOT / "scripts" / "session_self_initialization.py"
STARTUP_FRESHNESS_CONTRACT_VERSION = "gtkb-startup-freshness-v1"
HARNESS_NAME = "codex"
STARTUP_SERVICE_TIMEOUT_SECONDS = 50.0
# Parity marker for tests: Role: Prime Builder

sys.path.insert(0, str(PROJECT_ROOT))
from scripts.harness_identity import resolved_harness_id  # noqa: E402


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso8601(value: str | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def _is_ordered(earlier: str | None, later: str | None) -> bool:
    earlier_dt = _parse_iso8601(earlier)
    later_dt = _parse_iso8601(later)
    if earlier_dt is None or later_dt is None:
        return False
    return earlier_dt <= later_dt


def _purge_previous_diagnostics(*paths: Path) -> None:
    for path in paths:
        try:
            path.unlink()
        except FileNotFoundError:
            continue
        except OSError:
            pass


def _persistent_harness_id() -> str:
    harness_id = resolved_harness_id(PROJECT_ROOT, harness_name=HARNESS_NAME)
    if not harness_id:
        raise RuntimeError(f"Could not resolve persistent harness identity for {HARNESS_NAME}")
    return harness_id


def _fallback_context(reason: str) -> str:
    dashboard = "file:///E:/GT-KB/docs/gtkb-dashboard/index.html"
    return "\n".join(
        [
            "# GroundTruth-KB Startup Service Degraded",
            "",
            f"Generated: {_now_iso()}",
            "",
            "The SessionStart hook could not retrieve the programmatic startup payload.",
            f"Reason: {reason}",
            "",
            f"Dashboard: [GroundTruth-KB Project Dashboard]({dashboard})",
            "",
            "Use filesystem reads and the dashboard as the live authority before acting.",
        ]
    )


def _session_start_payload(context: str) -> dict[str, dict[str, str]]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }


def _bridge_auto_dispatch_context() -> str | None:
    run_id = os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID")
    if not run_id:
        return None
    return "\n".join(
        [
            "# GroundTruth-KB Bridge Auto-Dispatch Session",
            "",
            f"Poller run id: {run_id}",
            "",
            "This SessionStart was launched by the verified smart poller.",
            "Do not relay the normal fresh-session startup disclosure.",
            "Do not treat the initial prompt as a discarded owner session-start stimulus.",
            "Treat the initial prompt as the active bridge auto-dispatch task.",
            "Read `bridge/INDEX.md` directly before acting.",
            "Process only entries whose live latest status is actionable for the durable role.",
            "Preserve the bridge protocol audit trail.",
        ]
    )


def _dump_payload(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=True)


def _valid_session_start_payload(text: str, request_started_at: str) -> bool:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return False
    hook_output = payload.get("hookSpecificOutput")
    if not (
        isinstance(hook_output, dict)
        and hook_output.get("hookEventName") == "SessionStart"
        and isinstance(hook_output.get("additionalContext"), str)
        and "Programmatic Startup Payload" in hook_output["additionalContext"]
    ):
        return False
    startup_freshness = hook_output.get("startupFreshness")
    if not isinstance(startup_freshness, dict):
        return False
    validation = startup_freshness.get("validation")
    return (
        startup_freshness.get("contract_version") == STARTUP_FRESHNESS_CONTRACT_VERSION
        and startup_freshness.get("request_started_at") == request_started_at
        and startup_freshness.get("report_origin") == "in_memory_model_render"
        and isinstance(validation, dict)
        and validation.get("startup_payload_fresh") is True
        and validation.get("status") in {"fresh", "fresh_with_gaps"}
        and _is_ordered(request_started_at, startup_freshness.get("generated_at"))
        and _is_ordered(startup_freshness.get("generated_at"), startup_freshness.get("payload_emitted_at"))
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stdout_path = OUT_DIR / "last-session-start.json"
    stderr_path = OUT_DIR / "last-session-start.err"
    request_started_at = _now_iso()
    _purge_previous_diagnostics(stdout_path, stderr_path)
    auto_dispatch_context = _bridge_auto_dispatch_context()
    if auto_dispatch_context is not None:
        payload = _session_start_payload(auto_dispatch_context)
        serialized = _dump_payload(payload)
        stdout_path.write_text(serialized, encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        print(serialized)
        return 0
    command = [
        sys.executable,
        str(STARTUP_SERVICE),
        "--project-root",
        str(PROJECT_ROOT),
        "--emit-startup-service-payload",
        "--fast-hook",
        "--harness-name",
        HARNESS_NAME,
        "--harness-id",
        _persistent_harness_id(),
    ]
    try:
        env = dict(os.environ)
        env["GTKB_STARTUP_REQUESTED_AT"] = request_started_at
        process = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=STARTUP_SERVICE_TIMEOUT_SECONDS,
            check=False,
            env=env,
        )
        stdout_path.write_text(process.stdout, encoding="utf-8")
        stderr_path.write_text(process.stderr, encoding="utf-8")
        if process.returncode == 0 and _valid_session_start_payload(process.stdout, request_started_at):
            payload = json.loads(process.stdout)
            print(_dump_payload(_session_start_payload(payload["hookSpecificOutput"]["additionalContext"])))
            return 0
        reason = f"startup service returned exit {process.returncode}"
        if process.stderr.strip():
            reason = f"{reason}: {process.stderr.strip()[:400]}"
        elif process.returncode == 0:
            reason = "startup service freshness contract validation failed"
        print(_dump_payload(_session_start_payload(_fallback_context(reason))))
    except Exception as exc:  # noqa: BLE001 - lifecycle hook must fail soft.
        try:
            stderr_path.write_text(str(exc), encoding="utf-8")
        except OSError:
            pass
        print(_dump_payload(_session_start_payload(_fallback_context(str(exc)))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
