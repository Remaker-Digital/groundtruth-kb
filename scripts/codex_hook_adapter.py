#!/usr/bin/env python3
"""Translate the selected Codex hook using its actual native session envelope.

Native hooks run from the session working directory. The projector's Windows
launcher resolves the common Git installation and invokes this adapter there.
No role, project authorization or claim is supplied by this transport.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).absolute().parent.parent
EVENTS = ("PreToolUse", "PostToolUse", "SessionStart", "UserPromptSubmit", "Stop")


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate field: {key}")
        result[key] = value
    return result


def _decode(raw):
    value = json.loads(raw, object_pairs_hook=_object)
    if not isinstance(value, dict):
        raise ValueError("Hook input/output must be a JSON object")
    return value


def _refusal(event, reason):
    if event == "PreToolUse":
        return {
            "hookSpecificOutput": {
                "hookEventName": event,
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    if event == "Stop":
        return {"decision": "block", "reason": reason}
    if event == "UserPromptSubmit":
        return {"continue": False, "stopReason": reason}
    return {"systemMessage": reason}


def _target(raw):
    path = Path(raw)
    if ".." in path.parts:
        raise ValueError("Redirected hook target")
    path = path if path.is_absolute() else ROOT / path
    rel = path.relative_to(ROOT)
    if not (rel.is_relative_to("scripts") or rel.is_relative_to(".harness-baseline-configuration/hooks")):
        raise ValueError("Hook target must be platform code or an authored baseline hook")
    if not path.is_file() or path.resolve() != path:
        raise ValueError("Hook target is missing or redirected")
    return path


def _payload(data, event):
    native, cwd = data.get("session_id"), data.get("cwd")
    if not isinstance(native, str) or not native.strip():
        raise ValueError("Missing native session_id")
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        raise ValueError("Missing absolute native cwd")
    observed_event = data.get("hook_event_name")
    if observed_event is not None and observed_event != event:
        raise ValueError("Native event does not match its registration")
    if event in {"PreToolUse", "PostToolUse"}:
        if not isinstance(data.get("tool_name"), str) or not data["tool_name"].strip():
            raise ValueError("Missing native tool_name")
        if not isinstance(data.get("tool_input"), dict):
            raise ValueError("Missing native tool_input")
    return {**data, "project_root": str(ROOT), "hook_event_name": event}


def _response(data, event):
    if event != "PreToolUse":
        return data
    decision = data.get("decision")
    specific = data.get("hookSpecificOutput", {})
    if not isinstance(specific, dict) or decision not in {None, "allow", "block"}:
        raise ValueError("Invalid hook decision")
    permission = specific.get("permissionDecision")
    if permission not in {None, "allow", "deny", "ask"}:
        raise ValueError("Invalid native permission decision")
    continuing = data.get("continue", True)
    if not isinstance(continuing, bool):
        raise ValueError("Invalid hook continuation")
    if decision == "block" or permission in {"deny", "ask"} or not continuing:
        reason = data.get("reason") or specific.get("permissionDecisionReason") or data.get("stopReason")
        return _refusal(event, str(reason or "The selected GT-KB hook refused"))
    # Codex rejects common continue/stopReason fields on PreToolUse and then
    # continues the tool. Emit only its supported event-specific shape here.
    context = specific.get("additionalContext") or data.get("systemMessage")
    if context:
        if not isinstance(context, str):
            raise ValueError("Invalid hook context")
        return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}}
    return {}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", choices=EVENTS, required=True)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("script")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    event = "PreToolUse"
    try:
        options = parser.parse_args()
        event = options.event
        if not math.isfinite(options.timeout) or options.timeout <= 0:
            raise ValueError("Invalid hook timeout")
        target = _target(options.script)
        data = _payload(_decode(sys.stdin.read()), event)
        env = {
            **os.environ,
            "PYTHONIOENCODING": "utf-8",
            "GTKB_HARNESS_NAME": "codex",
            "GTKB_NATIVE_CONTEXT_ID": data["session_id"],
            "CODEX_SESSION_ID": data["session_id"],
            "GTKB_PROJECT_ROOT": str(ROOT),
            "GT_PROJECT_ROOT": str(ROOT),
            "CODEX_PROJECT_DIR": str(ROOT),
        }
        completed = subprocess.run(
            [sys.executable, "-B", str(target), *options.args],
            input=json.dumps(data),
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=options.timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if completed.stderr:
            sys.stderr.write(completed.stderr[:2000])
        if completed.returncode:
            raise ValueError(f"Selected hook failed with exit {completed.returncode}")
        raw = completed.stdout.strip()
        if raw and not raw.startswith("{") and event in {"SessionStart", "UserPromptSubmit"}:
            result = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": raw}}
        else:
            result = _response(_decode(raw) if raw else {}, event)
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired) as error:
        result = _refusal(event, f"GT-KB native hook refused: {str(error)[:2000]}")
    except SystemExit as error:
        if error.code == 0:
            return 0
        result = _refusal(event, "Invalid GT-KB hook configuration")
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
