# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Run a Python hook script without creating a visible Windows console."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from session_start_dispatch_core import STARTUP_SERVICE_TIMEOUT_ENV, STARTUP_SERVICE_TIMEOUT_SECONDS  # noqa: E402
from windows_subprocess import no_window_subprocess_kwargs, prefer_pythonw_executable  # noqa: E402

DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_STDIN_TIMEOUT_SECONDS = 0.2
_PASS_RESPONSE = b"{}"
_DECISION_PRIORITY = {"deny": 3, "ask": 2, "allow": 1}
BATCHES: dict[str, tuple[tuple[str, ...], ...]] = {
    "user-prompt-submit": (
        ("py", ".codex/gtkb-hooks/session-init-binding.py"),
        ("cmd", ".codex/gtkb-hooks/workstream-focus.cmd"),
        ("py", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py"),
        ("py", ".claude/hooks/spec-classifier.py"),
        ("py", ".codex/gtkb-hooks/glossary-expansion.py"),
        ("py", ".codex/gtkb-hooks/project-completion-surface.py"),
    ),
    "pretooluse-bash": (
        ("cmd", ".codex/gtkb-hooks/workstream-focus.cmd"),
        ("cmd", ".codex/gtkb-hooks/destructive-gate.cmd"),
        ("cmd", ".codex/gtkb-hooks/credential-scan.cmd"),
        ("cmd", ".codex/gtkb-hooks/formal-artifact-approval.cmd"),
        ("cmd", ".codex/gtkb-hooks/bridge-compliance-gate.cmd"),
        ("cmd", ".codex/gtkb-hooks/implementation-start-gate.cmd"),
        ("cmd", ".codex/gtkb-hooks/directive-enforcement.cmd"),
        ("cmd", ".codex/gtkb-hooks/lo-file-safety-gate.cmd"),
        ("cmd", ".codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd"),
        ("cmd", ".codex/gtkb-hooks/wi-id-collision-gate.cmd"),
        ("py", ".codex/gtkb-hooks/sot-read-discipline-bash-adapter.py"),
    ),
    "pretooluse-apply-patch": (
        ("cmd", ".codex/gtkb-hooks/workstream-focus.cmd"),
        ("cmd", ".codex/gtkb-hooks/implementation-start-gate.cmd"),
        ("cmd", ".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd"),
        ("py", ".codex/gtkb-hooks/document_author_provenance_gate.py"),
    ),
    "posttooluse-bash": (
        ("cmd", ".codex/gtkb-hooks/bridge-compliance-audit.cmd"),
        ("py", ".claude/hooks/spec-event-surfacer.py"),
        ("py", "scripts/registry_observation_hook.py"),
        (
            "py",
            "scripts/bridge_verified_backlog_reconciler.py",
            "--apply",
            "--quiet",
            "--project-root",
            "{PROJECT_ROOT}",
        ),
    ),
    "posttooluse-apply-patch": (
        ("py", ".claude/hooks/spec-event-surfacer.py"),
        ("py", "scripts/registry_observation_hook.py"),
        (
            "py",
            "scripts/bridge_verified_backlog_reconciler.py",
            "--apply",
            "--quiet",
            "--project-root",
            "{PROJECT_ROOT}",
        ),
    ),
    "stop": (
        (
            "py",
            "scripts/bridge_verified_backlog_reconciler.py",
            "--apply",
            "--quiet",
            "--project-root",
            "{PROJECT_ROOT}",
        ),
        ("py", ".claude/hooks/advisory-router-scan.py"),
        ("py", "scripts/advisory_grilling_gate_lint.py", "--stop-hook"),
        ("py", "scripts/auto_finalize_sweep.py"),
    ),
}


def _is_session_start_dispatch_command(command: list[str] | None) -> bool:
    if not command or len(command) < 2:
        return False
    script = Path(command[1])
    return script.name == "session_start_dispatch.py" and script.parent.name == "gtkb-hooks"


def _startup_dispatch_timeout_seconds() -> float:
    raw = os.environ.get(STARTUP_SERVICE_TIMEOUT_ENV)
    if raw is None or not raw.strip():
        return STARTUP_SERVICE_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        return STARTUP_SERVICE_TIMEOUT_SECONDS
    return value if value > 0 else STARTUP_SERVICE_TIMEOUT_SECONDS


def _child_timeout_seconds(command: list[str] | None = None) -> float:
    raw = os.environ.get("GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS")
    if raw:
        try:
            value = float(raw)
        except ValueError:
            return DEFAULT_TIMEOUT_SECONDS
        return value if value > 0 else DEFAULT_TIMEOUT_SECONDS
    if _is_session_start_dispatch_command(command):
        return _startup_dispatch_timeout_seconds()
    return DEFAULT_TIMEOUT_SECONDS


def _stdin_timeout_seconds() -> float:
    raw = os.environ.get("GTKB_CODEX_HOOK_STDIN_TIMEOUT_SECONDS")
    if not raw:
        return DEFAULT_STDIN_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_STDIN_TIMEOUT_SECONDS
    return value if value >= 0 else DEFAULT_STDIN_TIMEOUT_SECONDS


def _read_hook_payload() -> bytes:
    if sys.stdin is None or sys.stdin.closed:
        return b""
    if sys.stdin.isatty():
        return b""
    payload: list[bytes] = []

    def _reader() -> None:
        payload.append(sys.stdin.buffer.read())

    thread = threading.Thread(target=_reader, daemon=True)
    thread.start()
    thread.join(_stdin_timeout_seconds())
    if thread.is_alive():
        return b""
    return payload[0] if payload else b""


def _kill_process_tree(pid: int) -> None:
    if sys.platform != "win32":
        return
    subprocess.run(
        ["taskkill.exe", "/PID", str(pid), "/T", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        **no_window_subprocess_kwargs(),
    )


def _run_child(command: list[str], payload: bytes) -> tuple[int, bytes, bytes]:
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **no_window_subprocess_kwargs(),
    )
    try:
        stdout, stderr = process.communicate(input=payload, timeout=_child_timeout_seconds(command))
    except subprocess.TimeoutExpired:
        _kill_process_tree(process.pid)
        try:
            process.communicate(timeout=1.0)
        except subprocess.TimeoutExpired:
            process.kill()
        return 124, b"", f"hook child timed out: {command[1] if len(command) > 1 else command[0]}\n".encode()
    return int(process.returncode), stdout or b"", stderr or b""


def _json_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def _deny_response(reason: str) -> dict[str, object]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def _parse_child_stdout(stdout: bytes, hook_name: str) -> tuple[dict[str, object] | None, str | None]:
    text = stdout.decode("utf-8-sig", errors="replace").strip()
    if not text:
        return {}, None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"{hook_name} emitted invalid hook JSON: {exc.msg}"
    if not isinstance(payload, dict):
        return None, f"{hook_name} emitted a non-object hook JSON response"
    return payload, None


def _permission_decision(payload: dict[str, object]) -> tuple[str, str | None] | None:
    hook_output = payload.get("hookSpecificOutput")
    if isinstance(hook_output, dict):
        decision = str(hook_output.get("permissionDecision") or "").strip().lower()
        if decision in _DECISION_PRIORITY:
            reason = hook_output.get("permissionDecisionReason")
            return decision, str(reason) if reason is not None else None
    if str(payload.get("decision") or "").strip().lower() == "block":
        reason = payload.get("reason")
        return "deny", str(reason) if reason is not None else "hook child returned decision=block"
    return None


def _merge_context_value(existing: object, incoming: object) -> object:
    if isinstance(existing, str) and isinstance(incoming, str):
        if not existing:
            return incoming
        if not incoming or incoming == existing:
            return existing
        return f"{existing}\n\n{incoming}"
    if isinstance(existing, list):
        return [*existing, incoming]
    if existing == incoming:
        return existing
    return [existing, incoming]


def _merged_batch_stdout(outputs: list[dict[str, object]]) -> bytes:
    strongest_decision: tuple[int, dict[str, object]] | None = None
    merged: dict[str, object] = {}
    for payload in outputs:
        if not payload:
            continue
        decision = _permission_decision(payload)
        if decision is not None:
            value, reason = decision
            priority = _DECISION_PRIORITY[value]
            normalized = payload if "hookSpecificOutput" in payload else _deny_response(reason or "hook denied")
            if strongest_decision is None or priority > strongest_decision[0]:
                strongest_decision = (priority, normalized)
            continue
        for key, value in payload.items():
            if key in {"hookSpecificOutput", "decision", "reason"}:
                continue
            if key in merged:
                merged[key] = _merge_context_value(merged[key], value)
            else:
                merged[key] = value
    if strongest_decision is not None:
        return _json_bytes(strongest_decision[1])
    if merged:
        return _json_bytes(merged)
    return _PASS_RESPONSE


def _batch_command(entry: tuple[str, ...]) -> list[str]:
    kind, raw_path, *raw_args = entry
    path = PROJECT_ROOT / raw_path
    args = [str(PROJECT_ROOT) if arg == "{PROJECT_ROOT}" else arg for arg in raw_args]
    if kind == "py":
        return [prefer_pythonw_executable(sys.executable), str(path), *args]
    if kind == "cmd":
        return [str(path), *args]
    raise ValueError(f"unknown batch entry kind: {kind}")


def _run_batch(batch_name: str, payload: bytes) -> tuple[int, bytes, bytes]:
    entries = BATCHES.get(batch_name)
    if entries is None:
        known = ", ".join(sorted(BATCHES))
        return 2, b"", f"unknown hook batch {batch_name!r}; known batches: {known}\n".encode()
    stdout_payloads: list[dict[str, object]] = []
    stderr_parts: list[bytes] = []
    for entry in entries:
        returncode, stdout, stderr = _run_child(_batch_command(entry), payload)
        stderr_parts.append(stderr)
        hook_name = entry[1] if len(entry) > 1 else entry[0]
        parsed, parse_error = _parse_child_stdout(stdout, hook_name)
        if parse_error is not None:
            stderr_parts.append(f"{parse_error}\n".encode())
            return 0, _json_bytes(_deny_response(parse_error)), b"".join(stderr_parts)
        if parsed is not None:
            stdout_payloads.append(parsed)
        if returncode != 0:
            return returncode, _merged_batch_stdout(stdout_payloads), b"".join(stderr_parts)
    return 0, _merged_batch_stdout(stdout_payloads), b"".join(stderr_parts)


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: run_py_no_window.py <hook.py> [args...] | --batch <name>", file=sys.stderr)
        return 2
    if argv[0] == "--batch":
        if len(argv) != 2:
            print("usage: run_py_no_window.py --batch <name>", file=sys.stderr)
            return 2
        hook_payload = _read_hook_payload()
        returncode, stdout, stderr = _run_batch(argv[1], hook_payload)
        if stdout:
            sys.stdout.buffer.write(stdout)
        if stderr:
            sys.stderr.buffer.write(stderr)
        return returncode
    script = Path(argv[0])
    if script.suffix.lower() != ".py":
        print(f"refusing non-.py hook target: {script}", file=sys.stderr)
        return 2
    hook_payload = _read_hook_payload()
    returncode, stdout, stderr = _run_child(
        [prefer_pythonw_executable(sys.executable), str(script), *argv[1:]],
        hook_payload,
    )
    if stdout:
        sys.stdout.buffer.write(stdout)
    if stderr:
        sys.stderr.buffer.write(stderr)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
