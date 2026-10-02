#!/usr/bin/env python3
"""Run one GT-KB hook for Claude Code and answer every failure of it with Claude Code's blocking exit 2.

c123 (batch design WP2 2.4, owner decision B1). Claude Code's hooks reference (code.claude.com/docs/en/hooks, sections
"Exit code output", "Timeouts" and "PreToolUse decision control"; read for Claude Code 2.1.281) gives a command hook
these outcomes:

- exit 0 is success, and stdout that starts with "{" and ends with "}" is read as the hook's JSON decision;
- exit 2 is a blocking error: on PreToolUse the tool call is blocked, with the reason from the JSON's blocking
  decision when it makes one and the stderr text otherwise;
- any other exit code without a valid JSON decision, a hook that cannot start, and stdout that fails to parse or to
  validate are non-blocking errors, and the action proceeds;
- a command hook cancelled at its timeout renders no decision, and the call continues through the permission flow.

Under ``--permission-mode bypassPermissions`` the GT-KB hooks are the only decider, so each non-blocking outcome would
let the tool run unguarded. This adapter runs the target hook with Claude Code's payload, environment and working
directory unchanged, then:

- passes a successful target's stdout through unchanged (an allow, an ask, context or a structured deny);
- passes a structured deny (``permissionDecision`` "deny" or "ask" with this event's ``hookEventName``, or a top-level
  ``decision`` "block") through whatever the target's exit code was;
- answers every other outcome with exit 2 and the reason on stderr: a nonzero exit, a crash, a target that cannot
  start or has not answered by ``--deadline``, and output that is not a hook decision. A deny Claude Code could not
  read (its ``hookEventName`` missing or naming another event) is also answered with exit 2 and its own reason.

The projector hands it ``--deadline SECONDS``, a margin below the hook's registered timeout, so the refusal lands before
Claude Code would cancel the hook. A target is platform code or an authored baseline hook of this installation, named
relative to its root (the projector's form, also under an application) or absolutely under the same rule.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TARGET_ROOTS = ("scripts", ".harness-baseline-configuration/hooks")
# c123 (batch design WP2 2.4): Claude Code adds plain-text stdout as context on these events; elsewhere it is ignored.
PLAIN_TEXT_CONTEXT_EVENTS = frozenset({"SessionStart", "UserPromptSubmit", "UserPromptExpansion", "PostModelSwitch"})
PERMISSION_DECISIONS = frozenset({"allow", "deny", "ask", "defer"})
TOP_LEVEL_DECISIONS = frozenset({"approve", "block"})
REASON_LIMIT = 4000


class Refusal(Exception):
    """A reason this adapter answers with Claude Code's blocking exit 2."""


def _creationflags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0


def _write(stream: Any, data: bytes) -> None:
    buffer = getattr(stream, "buffer", None)
    if buffer is not None:
        buffer.write(data)
    else:
        stream.write(data.decode("utf-8", "replace"))
    stream.flush()


def _block(reason: str) -> int:
    _write(sys.stderr, ((reason.strip() or "GT-KB: the hook refused the call")[:REASON_LIMIT] + "\n").encode("utf-8"))
    return 2


def _end_tree(process: subprocess.Popen[bytes]) -> None:
    """End a target that missed its deadline and everything it started, without waiting on its output pipes."""
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True,
            check=False,
            creationflags=_creationflags(),
        )
    else:
        process.kill()


def _arguments(argv: list[str]) -> tuple[float | None, list[str]]:
    """Split the projector's optional leading ``--deadline SECONDS`` from the target hook and its arguments."""
    if argv[:1] != ["--deadline"]:
        return None, argv
    if len(argv) < 2:
        raise Refusal("claude_hook_adapter: --deadline needs a number of seconds")
    try:
        deadline = float(argv[1])
    except ValueError:
        raise Refusal(f"claude_hook_adapter: invalid --deadline {argv[1]!r}") from None
    if not (math.isfinite(deadline) and deadline > 0):
        raise Refusal(f"claude_hook_adapter: invalid --deadline {argv[1]!r}")
    return deadline, argv[2:]


def _target(raw: str) -> Path:
    """The target hook: platform code or an authored baseline hook under this installation's root, never redirected."""
    given = Path(raw)
    if ".." in given.parts:
        raise Refusal(f"claude_hook_adapter: the hook target {raw!r} is redirected")
    path = given if given.is_absolute() else ROOT / given
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        raise Refusal(f"claude_hook_adapter: the hook target {raw!r} lies outside {ROOT}") from None
    if not any(relative.is_relative_to(root) for root in TARGET_ROOTS):
        raise Refusal(f"claude_hook_adapter: the hook target {raw!r} is neither platform code nor a baseline hook")
    if not path.is_file() or path.resolve() != path:
        raise Refusal(f"claude_hook_adapter: the hook target {raw!r} is missing or redirected")
    return path


def _event(raw: bytes) -> str:
    """The payload's hook_event_name, PreToolUse when it names none; the payload itself reaches the target unchanged."""
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "PreToolUse"
    event = value.get("hook_event_name") if isinstance(value, dict) else None
    return event if isinstance(event, str) and event else "PreToolUse"


def _read(stdout: str, event: str) -> tuple[bool, str | None, bool]:
    """(readable, deny reason, Claude Code reads the deny) for a target's stdout under Claude Code's parsing rule.

    The deny reason is None when the output makes no deny or ask decision.
    """
    text = stdout.strip()
    if not text:
        return True, None, False
    if not (text.startswith("{") and text.endswith("}")):
        return event in PLAIN_TEXT_CONTEXT_EVENTS, None, False
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return False, None, False
    if not isinstance(value, dict):
        return False, None, False
    specific = value.get("hookSpecificOutput", {})
    if not isinstance(specific, dict):
        return False, None, False
    permission = specific.get("permissionDecision")
    decision = value.get("decision")
    if permission is not None and permission not in PERMISSION_DECISIONS:
        return False, None, False
    if decision is not None and decision not in TOP_LEVEL_DECISIONS:
        return False, None, False
    if not isinstance(value.get("continue", True), bool):
        return False, None, False
    if permission in {"deny", "ask"}:
        reason = specific.get("permissionDecisionReason") or value.get("reason") or "the GT-KB hook refused the call"
        return True, str(reason), specific.get("hookEventName") == event
    if decision == "block":
        return True, str(value.get("reason") or "the GT-KB hook refused the call"), True
    return True, None, False


def _last_line(stderr: str) -> str:
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    return lines[-1][:500] if lines else ""


def _answer(name: str, event: str, returncode: int, stdout: bytes, stderr: bytes) -> int:
    """Claude Code's answer for one finished target run: its stdout unchanged, or exit 2 with the reason on stderr."""
    readable, deny, claude_reads = _read(stdout.decode("utf-8", "replace"), event)
    error_text = stderr.decode("utf-8", "replace")
    if deny is not None and claude_reads:
        _write(sys.stdout, stdout)
        if stderr:
            _write(sys.stderr, stderr)
        return 0
    if deny is not None:
        return _block(deny)
    if returncode == 0 and readable:
        _write(sys.stdout, stdout)
        if stderr:
            _write(sys.stderr, stderr)
        return 0
    if returncode == 2:
        return _block(
            error_text.strip() or f"GT-KB: the {name} check blocked the call (exit status 2) without a reason"
        )
    if returncode != 0:
        detail = _last_line(error_text)
        detail = f": {detail}" if detail else ""
        return _block(
            f"GT-KB: the {name} check failed (exit status {returncode}{detail}), so the call is refused until the "
            "hook runs cleanly."
        )
    return _block(
        f"GT-KB: the {name} check printed output that is not a hook decision, so the call is refused until the hook "
        "runs cleanly."
    )


def main(argv: list[str] | None = None) -> int:
    try:
        deadline, arguments = _arguments(list(sys.argv[1:] if argv is None else argv))
        if not arguments:
            raise Refusal("claude_hook_adapter: missing target hook script")
        target = _target(arguments[0])
    except Refusal as refusal:
        return _block(str(refusal))
    raw = sys.stdin.buffer.read()
    event = _event(raw)
    try:
        process = subprocess.Popen(
            [sys.executable, "-B", str(target), *arguments[1:]],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=_creationflags(),
        )
    except OSError as error:
        return _block(
            f"GT-KB: the {target.name} check could not start ({type(error).__name__}), so the call is refused."
        )
    try:
        stdout, stderr = process.communicate(raw, timeout=deadline)
    except subprocess.TimeoutExpired:
        _end_tree(process)
        return _block(
            f"GT-KB: the {target.name} check did not answer within {deadline:g} s, so the call is refused; retry once "
            "GT-KB is responsive."
        )
    return _answer(target.name, event, process.returncode, stdout or b"", stderr or b"")


if __name__ == "__main__":
    try:
        code = main()
    except Exception as exc:  # c123 (batch design WP2 2.4): intentional catch, an adapter failure blocks, never allows
        code = _block(f"claude_hook_adapter: {type(exc).__name__}: {exc}")
    raise SystemExit(code)
