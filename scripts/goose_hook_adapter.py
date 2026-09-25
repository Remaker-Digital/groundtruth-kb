#!/usr/bin/env python3
"""Adapt Goose hook stdin/stdout to GT-KB Claude-style hook contracts.

Goose (1.35 and later) blocks a PreToolUse call only when a hook exits 2 with
the reason on stderr, or prints {"decision": "block", "reason": ...}. Any other
output, including a Claude-style hookSpecificOutput deny with exit 0, is "no
decision" and the call proceeds. GT-KB hooks answer in the Claude form, so this
adapter translates every deny into exit 2 with the reason on stderr and every
allow into exit 0 with no output. Goose 1.45.0 lets a call proceed when a hook
crashes, fails to start or exceeds its timeout, even under the projected
``on_failure: block`` (finding F9), so the adapter answers every failure of its
own with exit 2. The projected command hands it ``--deadline SECONDS``, a margin
below that hook's projected timeout; a target that has not answered by then is
refused here, before Goose's own timeout would let the call run.

Goose payloads carry ``session_id``, ``tool_name``, ``tool_input`` and
``working_dir``. Built-in tools are ``write`` {path, content}, ``edit`` {path,
before, after} and ``shell`` {command}; the developer extension uses
``developer__text_editor`` (sub-command in ``tool_input.command``) and
``developer__shell``. They are normalized to Write/Edit/Read/Bash before the
target hook runs; the session id becomes the native context identifier. A tool
this adapter does not recognize is refused when its input names a path,
command, code or script (for example a code-execution tool that runs other
tools), so an unknown effect never passes ungated.

Specifications: ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

WRITE_SUBCOMMANDS = frozenset({"write", "create"})
READ_SUBCOMMANDS = frozenset({"view"})
READ_ONLY_TOOLS = frozenset({"tree", "read", "view", "list", "glob", "grep", "search"})
EFFECT_INPUT_KEYS = frozenset(
    {
        "path",
        "file_path",
        "filepath",
        "filename",
        "target",
        "destination",
        "command",
        "cmd",
        "code",
        "script",
        "program",
    }
)


def _creationflags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0


def _end_tree(process: subprocess.Popen) -> None:
    """End a target that missed its deadline and everything it started, without waiting on its output pipes.

    On Windows a killed child's descendants keep its pipes open, so waiting for them could outlast Goose's own hook
    timeout and turn this refusal back into a pass; the pipe readers are daemon threads and do not delay the exit.
    """
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True,
            check=False,
            creationflags=_creationflags(),
        )
    else:
        process.kill()


def _block(reason: str) -> int:
    sys.stderr.write((reason.strip() or "blocked by GT-KB hook")[:4000] + "\n")
    sys.stderr.flush()
    return 2


def _path(data: dict[str, Any]) -> str:
    value = data.get("path") or data.get("file_path")
    return str(value) if value else ""


def _normalize(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Return the Claude-style payload for the target hook, or None for an unrecognized effect-capable tool."""
    tool = str(payload.get("tool_name") or payload.get("matcher_context") or "")
    data = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    base = tool.rsplit("__", 1)[-1].lower()
    path = _path(data)
    if base == "write":
        adapted: dict[str, Any] = {
            "tool_name": "Write",
            "tool_input": {"file_path": path, "content": data.get("content", "")},
        }
    elif base == "edit":
        adapted = {"tool_name": "Edit", "tool_input": {"file_path": path}}
    elif base == "text_editor":
        sub = str(data.get("command") or "").lower()
        if sub in READ_SUBCOMMANDS:
            adapted = {"tool_name": "Read", "tool_input": {"file_path": path}}
        elif sub in WRITE_SUBCOMMANDS:
            adapted = {"tool_name": "Write", "tool_input": {"file_path": path, "content": data.get("file_text", "")}}
        else:
            # str_replace, insert, undo_edit and any unknown sub-command change the file.
            adapted = {"tool_name": "Edit", "tool_input": {"file_path": path}}
    elif base == "shell":
        adapted = {"tool_name": "Bash", "tool_input": {"command": str(data.get("command") or "")}}
    elif base in READ_ONLY_TOOLS or not (EFFECT_INPUT_KEYS & {str(key).lower() for key in data}):
        adapted = {"tool_name": tool, "tool_input": dict(data)}
    else:
        return None
    cwd = payload.get("working_dir") or payload.get("cwd")
    if isinstance(cwd, str) and cwd:
        adapted["cwd"] = cwd
    return adapted


def _native_context_id(payload: dict[str, Any]) -> str:
    value = payload.get("session_id")
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _deny_reason(stdout: str, returncode: int, stderr: str) -> str | None:
    """Return the deny reason in the target hook's Claude-style output, or None for allow."""
    parsed: Any = None
    if stdout:
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            parsed = None
    if isinstance(parsed, dict):
        native = parsed.get("hookSpecificOutput")
        if isinstance(native, dict) and native.get("permissionDecision") in {"deny", "ask"}:
            return str(
                native.get("permissionDecisionReason") or native.get("additionalContext") or "blocked by GT-KB hook"
            )
        if parsed.get("decision") == "block":
            return str(parsed.get("reason") or parsed.get("systemMessage") or "blocked by GT-KB hook")
    if returncode == 2:
        lines = [line.strip() for line in (stderr or "").splitlines() if line.strip()]
        return lines[-1] if lines else "blocked by GT-KB hook"
    if returncode != 0:
        return f"GT-KB hook failed with exit status {returncode}"
    return None


def _arguments(argv: list[str]) -> tuple[float | None, list[str]]:
    """Split the projector's optional leading ``--deadline SECONDS`` from the target hook and its arguments."""
    if argv[:1] != ["--deadline"]:
        return None, argv
    if len(argv) < 2:
        raise ValueError("--deadline needs a number of seconds")
    try:
        deadline = float(argv[1])
    except ValueError:
        raise ValueError(f"invalid --deadline {argv[1]!r}") from None
    if not (math.isfinite(deadline) and deadline > 0):
        raise ValueError(f"invalid --deadline {argv[1]!r}")
    return deadline, argv[2:]


def main() -> int:
    try:
        deadline, arguments = _arguments(sys.argv[1:])
    except ValueError as exc:
        return _block(f"goose_hook_adapter: {exc}")
    if not arguments:
        return _block("goose_hook_adapter: missing target hook script")
    target = Path(arguments[0])
    if not target.is_file():
        target = (PROJECT_ROOT / arguments[0]).resolve()
    if not target.is_file():
        return _block(f"goose_hook_adapter: missing hook script {arguments[0]}")
    raw = sys.stdin.buffer.read()
    try:
        payload = json.loads(raw.decode("utf-8-sig")) if raw else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _block("goose_hook_adapter: the hook payload is not a JSON object")
    if not isinstance(payload, dict):
        return _block("goose_hook_adapter: the hook payload is not a JSON object")
    adapted = _normalize(payload)
    if adapted is None:
        return _block(
            f"GT-KB: the Goose tool {payload.get('tool_name')!r} is not recognized by the GT-KB gate and its input names a "
            "path, command or code; use the write, edit or shell tool so the effect can be checked."
        )

    env = os.environ.copy()
    native = _native_context_id(payload)
    if native:
        env["GTKB_NATIVE_CONTEXT_ID"] = native
    else:
        env.pop("GTKB_NATIVE_CONTEXT_ID", None)  # never act under an inherited identity
    env.setdefault("GTKB_PROJECT_ROOT", str(PROJECT_ROOT))
    env.setdefault("GTKB_HARNESS_NAME", "goose")
    env.setdefault("GTKB_HARNESS_ID", "G")

    process = subprocess.Popen(
        [sys.executable, "-B", str(target), *arguments[1:]],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(PROJECT_ROOT),
        env=env,
        creationflags=_creationflags(),
    )
    try:
        stdout, stderr = process.communicate(json.dumps(adapted), timeout=deadline)
    except subprocess.TimeoutExpired:
        _end_tree(process)
        return _block(
            f"GT-KB: the {target.name} check did not answer within {deadline:g} s, so the call is refused; "
            "retry once GT-KB is responsive."
        )
    reason = _deny_reason((stdout or "").strip(), process.returncode, stderr or "")
    if reason is not None:
        return _block(reason)
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception as exc:  # intentional-catch: an adapter failure must block, never allow
        code = _block(f"goose_hook_adapter: {type(exc).__name__}: {exc}")
    raise SystemExit(code)
