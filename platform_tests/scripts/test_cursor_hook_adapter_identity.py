"""Cursor adapter identity (finding F5, confirmed on Cursor 3.21.18, 2026-09-24).

Every Cursor hook event carries ``conversation_id``, the native context the shared effect gate needs. The adapter
rebuilds a Claude-style payload without it, so it hands the identifier to the gate as GTKB_NATIVE_CONTEXT_ID and never
acts under an inherited identity. The target hook is a stub that records what it received.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "scripts" / "cursor_hook_adapter.py"
STUB = """
import json, os, sys
raw = sys.stdin.read()
record = {"payload": json.loads(raw) if raw.strip() else None, "native": os.environ.get("GTKB_NATIVE_CONTEXT_ID")}
open(os.environ["STUB_RECORD"], "w", encoding="utf-8").write(json.dumps(record))
if os.environ.get("STUB_MODE") == "deny-json":
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": "no_session_binding"}}))
"""


def _cursor_payload(**changes) -> dict:
    """A Cursor 3.21.18 preToolUse payload for a StrReplace edit (cursor.com/docs/agent/hooks)."""
    payload = {
        "conversation_id": "c0nv-123",
        "generation_id": "gen-9",
        "hook_event_name": "preToolUse",
        "tool_name": "StrReplace",
        "tool_input": {"path": "README.md", "old_string": "a", "new_string": "b"},
        "cursor_version": "3.21.18",
        "workspace_roots": ["E:/project"],
    }
    payload.update(changes)
    return {key: value for key, value in payload.items() if value is not None}


def _run(tmp_path: Path, payload: dict, *, inherited: str | None = None, mode: str = "allow"):
    stub = tmp_path / "stub_hook.py"
    stub.write_text(STUB, encoding="utf-8")
    record = tmp_path / "record.json"
    env = {k: v for k, v in os.environ.items() if k != "GTKB_NATIVE_CONTEXT_ID"}
    if inherited is not None:
        env["GTKB_NATIVE_CONTEXT_ID"] = inherited
    env.update(STUB_RECORD=str(record), STUB_MODE=mode, PYTHONIOENCODING="utf-8", CURSOR_HOOK_EVENT="preToolUse")
    done = subprocess.run(
        [sys.executable, "-B", str(ADAPTER), str(stub), "--harness", "cursor"],
        input=json.dumps(payload).encode("utf-8"),
        capture_output=True,
        env=env,
        timeout=120,
        check=False,
    )
    seen = json.loads(record.read_text(encoding="utf-8")) if record.exists() else None
    return done, seen


def test_conversation_id_is_the_native_context_and_overrides_an_inherited_one(tmp_path):
    done, seen = _run(tmp_path, _cursor_payload(), inherited="stale-context")
    assert done.returncode == 0, done.stderr
    assert seen["native"] == "c0nv-123"
    assert seen["payload"]["tool_name"] == "Edit"


def test_session_id_is_the_fallback_identifier(tmp_path):
    _done, seen = _run(tmp_path, _cursor_payload(conversation_id=None, session_id="sess-7"))
    assert seen["native"] == "sess-7"


def test_without_an_identifier_no_inherited_identity_is_used(tmp_path):
    _done, seen = _run(tmp_path, _cursor_payload(conversation_id=None), inherited="stale-context")
    assert seen["native"] is None


def test_a_gate_refusal_reaches_cursor_as_a_deny_under_the_conversation_identity(tmp_path):
    done, seen = _run(tmp_path, _cursor_payload(), mode="deny-json")
    answer = json.loads(done.stdout.decode("utf-8").strip().splitlines()[-1])
    assert answer["permission"] == "deny" and "no_session_binding" in answer["agent_message"]
    assert seen["native"] == "c0nv-123"
