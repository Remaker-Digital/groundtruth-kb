"""Goose hook adapter: real Goose 1.45.0 payload shapes and Goose's deny contract (owner ruling D52; findings F6, F9).

Goose blocks a PreToolUse call only on exit 2 (reason on stderr) or {"decision": "block"}, and 1.45.0 lets the call
proceed on any other exit, a timeout or a spawn failure even under ``on_failure: block``. The adapter therefore turns
every GT-KB denial and every failure of its own into exit 2, and an allow into a silent exit 0. The target hook here is a
stub that records what it received and answers as instructed.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "scripts" / "goose_hook_adapter.py"
STUB = """
import json, os, sys
raw = sys.stdin.read()
record = {"payload": json.loads(raw) if raw.strip() else None, "native": os.environ.get("GTKB_NATIVE_CONTEXT_ID"),
          "harness": os.environ.get("GTKB_HARNESS_NAME"), "harness_id": os.environ.get("GTKB_HARNESS_ID"),
          "argv": sys.argv[1:], "cwd": os.getcwd()}
open(os.environ["STUB_RECORD"], "w", encoding="utf-8").write(json.dumps(record))
mode = os.environ.get("STUB_MODE", "allow")
if mode == "deny-json":
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": "stub refusal: no_session_binding"}}))
elif mode == "ask-json":
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                             "permissionDecisionReason": "stub asks"}}))
elif mode == "block-json":
    print(json.dumps({"decision": "block", "reason": "stub block"}))
elif mode == "exit2":
    sys.stderr.write("first line\\nstub exit-2 refusal\\n")
    sys.exit(2)
elif mode == "crash":
    sys.exit(1)
elif mode == "noise":
    print("not json")
elif mode == "hang":
    import subprocess, time
    # A grandchild that inherits this hook's output pipes and outlives it: it must not hold the adapter open.
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    open(os.environ["STUB_RECORD"] + ".child", "w", encoding="utf-8").write(str(child.pid))
    time.sleep(60)
"""


def _payload(tool: str, tool_input: dict, **extra) -> dict:
    """The PreToolUse payload Goose 1.45.0 sends (measured, F9)."""
    return {
        "event": "PreToolUse",
        "session_id": "20260924_1",
        "tool_name": tool,
        "tool_input": tool_input,
        "tool_call_id": "call-1",
        "working_dir": "E:/project",
        "matcher_context": tool,
        **extra,
    }


def _run(
    tmp_path: Path,
    payload,
    *,
    mode: str = "allow",
    inherited: str | None = None,
    raw: bytes | None = None,
    target: Path | None = None,
    leading: list[str] | None = None,
):
    stub = tmp_path / "stub_hook.py"
    stub.write_text(STUB, encoding="utf-8")
    record = tmp_path / "record.json"
    record.unlink(missing_ok=True)
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in {"GTKB_NATIVE_CONTEXT_ID", "GTKB_HARNESS_NAME", "GTKB_HARNESS_ID"}
    }
    if inherited is not None:
        env["GTKB_NATIVE_CONTEXT_ID"] = inherited
    env.update(STUB_MODE=mode, STUB_RECORD=str(record), PYTHONIOENCODING="utf-8")
    stdin = raw if raw is not None else json.dumps(payload).encode("utf-8")
    done = subprocess.run(
        [sys.executable, "-B", str(ADAPTER), *(leading or []), str(target or stub), "--harness", "goose"],
        input=stdin,
        capture_output=True,
        env=env,
        timeout=120,
        check=False,
    )
    seen = json.loads(record.read_text(encoding="utf-8")) if record.exists() else None
    return done.returncode, done.stdout.decode("utf-8", "replace"), done.stderr.decode("utf-8", "replace"), seen


def test_allow_is_a_silent_exit_zero_and_the_session_is_the_native_context(tmp_path):
    code, out, err, seen = _run(
        tmp_path, _payload("write", {"path": "notes.txt", "content": "x"}), inherited="stale-id"
    )
    assert (code, out, err) == (0, "", "")
    assert seen["payload"] == {
        "tool_name": "Write",
        "tool_input": {"file_path": "notes.txt", "content": "x"},
        "cwd": "E:/project",
    }
    assert seen["native"] == "20260924_1", "Goose's session_id overrides an inherited identity"
    assert (seen["harness"], seen["harness_id"]) == ("goose", "G")
    assert seen["argv"] == ["--harness", "goose"]
    assert Path(seen["cwd"]) == ROOT


@pytest.mark.parametrize(
    ("mode", "reason"),
    [
        ("deny-json", "stub refusal: no_session_binding"),
        ("ask-json", "stub asks"),
        ("block-json", "stub block"),
        ("exit2", "stub exit-2 refusal"),
        ("crash", "GT-KB hook failed with exit status 1"),
    ],
)
def test_every_refusal_and_failure_is_goose_exit_two_with_the_reason_on_stderr(tmp_path, mode, reason):
    code, out, err, _seen = _run(tmp_path, _payload("shell", {"command": "git rm -n --cached README.md"}), mode=mode)
    assert code == 2
    assert out == ""
    assert err.strip() == reason


def test_unparseable_target_output_with_exit_zero_is_an_allow(tmp_path):
    code, out, err, _seen = _run(tmp_path, _payload("shell", {"command": "echo hi"}), mode="noise")
    assert (code, out, err) == (0, "", "")


@pytest.mark.parametrize(
    ("tool", "tool_input", "expected"),
    [
        (
            "write",
            {"path": "a.txt", "content": "c"},
            {"tool_name": "Write", "tool_input": {"file_path": "a.txt", "content": "c"}},
        ),
        (
            "edit",
            {"path": "a.txt", "before": "x", "after": "y"},
            {"tool_name": "Edit", "tool_input": {"file_path": "a.txt"}},
        ),
        ("shell", {"command": "echo hi"}, {"tool_name": "Bash", "tool_input": {"command": "echo hi"}}),
        ("developer__shell", {"command": "dir"}, {"tool_name": "Bash", "tool_input": {"command": "dir"}}),
        (
            "developer__text_editor",
            {"command": "view", "path": "a.txt"},
            {"tool_name": "Read", "tool_input": {"file_path": "a.txt"}},
        ),
        (
            "developer__text_editor",
            {"command": "write", "path": "a.txt", "file_text": "t"},
            {"tool_name": "Write", "tool_input": {"file_path": "a.txt", "content": "t"}},
        ),
        (
            "developer__text_editor",
            {"command": "str_replace", "path": "a.txt", "old_str": "a", "new_str": "b"},
            {"tool_name": "Edit", "tool_input": {"file_path": "a.txt"}},
        ),
        (
            "developer__text_editor",
            {"command": "undo_edit", "path": "a.txt"},
            {"tool_name": "Edit", "tool_input": {"file_path": "a.txt"}},
        ),
        ("tree", {"path": "."}, {"tool_name": "tree", "tool_input": {"path": "."}}),
        ("todo_write", {"content": "- [ ] step"}, {"tool_name": "todo_write", "tool_input": {"content": "- [ ] step"}}),
    ],
)
def test_goose_tools_are_normalized_before_the_gate(tmp_path, tool, tool_input, expected):
    code, _out, _err, seen = _run(tmp_path, _payload(tool, tool_input))
    assert code == 0
    assert seen["payload"] == {**expected, "cwd": "E:/project"}


@pytest.mark.parametrize(
    ("tool", "tool_input"),
    [
        ("execute_typescript", {"code": "await shell({command: 'git rm -n --cached README.md'})"}),
        ("some_extension__writer", {"file_path": "a.txt", "text": "x"}),
        ("runner", {"script": "rm -rf build"}),
    ],
)
def test_an_unrecognized_tool_naming_a_path_command_or_code_is_refused_without_running_the_gate(
    tmp_path, tool, tool_input
):
    code, out, err, seen = _run(tmp_path, _payload(tool, tool_input))
    assert code == 2 and out == ""
    assert f"the Goose tool {tool!r} is not recognized by the GT-KB gate" in err
    assert seen is None, "the target hook must not run for an unrecognized effect-capable tool"


def test_a_missing_session_id_never_uses_an_inherited_identity(tmp_path):
    payload = _payload("write", {"path": "a.txt", "content": "x"})
    payload.pop("session_id")
    code, _out, _err, seen = _run(tmp_path, payload, inherited="inherited-context")
    assert code == 0
    assert seen["native"] is None


@pytest.mark.parametrize("raw", [b"{not json", b"[1, 2]", b"\xff\xfe"])
def test_an_unreadable_payload_blocks(tmp_path, raw):
    code, out, err, seen = _run(tmp_path, None, raw=raw)
    assert code == 2 and out == "" and "not a JSON object" in err
    assert seen is None


def test_a_missing_target_blocks(tmp_path):
    code, out, err, seen = _run(tmp_path, _payload("shell", {"command": "echo"}), target=tmp_path / "absent.py")
    assert code == 2 and out == "" and "missing hook script" in err
    assert seen is None


def _alive(pid: int) -> bool:
    if sys.platform == "win32":
        listed = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True, check=False
        )
        return str(pid) in listed.stdout
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def test_a_target_that_misses_its_deadline_is_refused_and_its_process_tree_ended(tmp_path):
    """B68: a hung check is a denial within the adapter's deadline, even when a grandchild holds its output pipes."""
    started = time.monotonic()
    code, out, err, seen = _run(
        tmp_path, _payload("shell", {"command": "echo"}), mode="hang", leading=["--deadline", "3"]
    )
    elapsed = time.monotonic() - started
    assert code == 2 and out == ""
    assert "did not answer within 3 s, so the call is refused" in err
    assert seen is not None and seen["argv"] == ["--harness", "goose"], (
        "the deadline is the adapter's, not the target's"
    )
    assert elapsed < 15, f"the adapter waited {elapsed:.1f} s for a target past its 3 s deadline"
    grandchild = int((tmp_path / "record.json.child").read_text(encoding="utf-8"))
    deadline = time.monotonic() + 10
    while _alive(grandchild) and time.monotonic() < deadline:
        time.sleep(0.2)
    assert not _alive(grandchild), "the target's process tree must be ended"


@pytest.mark.parametrize(
    "leading",
    [
        ["--deadline"],
        ["--deadline", "soon"],
        ["--deadline", "0"],
        ["--deadline", "-3"],
        ["--deadline", "inf"],
        ["--deadline", "nan"],
    ],
)
def test_a_malformed_deadline_blocks_without_running_the_target(tmp_path, leading):
    code, out, err, seen = _run(tmp_path, _payload("shell", {"command": "echo"}), leading=leading)
    assert code == 2 and out == ""
    assert "--deadline" in err
    assert seen is None


@pytest.mark.parametrize(("mode", "code_expected"), [("allow", 0), ("deny-json", 2)])
def test_an_answer_within_the_deadline_is_unchanged(tmp_path, mode, code_expected):
    code, out, err, seen = _run(
        tmp_path, _payload("shell", {"command": "echo"}), mode=mode, leading=["--deadline", "30"]
    )
    assert code == code_expected and out == ""
    assert (err.strip() == "stub refusal: no_session_binding") is (mode == "deny-json")
    assert seen["argv"] == ["--harness", "goose"]


RAISING_RUNNER = """
import runpy, subprocess, sys
def refuse_to_start(*args, **kwargs):
    raise OSError("injected adapter failure")
subprocess.Popen = refuse_to_start
sys.argv = [sys.argv[1], sys.argv[2], "--harness", "goose"]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


def test_an_exception_inside_the_adapter_blocks(tmp_path):
    """B75: Goose 1.45.0 ignores ``on_failure: block``, so the adapter's own catch-all is the fail-safe.

    The real adapter runs as ``__main__`` with its target launch made to raise (an internal failure no payload can
    cause, since every input shape is normalized); the call must end as a refusal carrying the failure, never an allow.
    """
    stub = tmp_path / "stub_hook.py"
    stub.write_text(STUB, encoding="utf-8")
    done = subprocess.run(
        [sys.executable, "-B", "-c", RAISING_RUNNER, str(ADAPTER), str(stub)],
        input=json.dumps(_payload("write", {"path": "x.txt", "content": "y"})).encode("utf-8"),
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        timeout=120,
        check=False,
    )
    assert done.returncode == 2
    assert done.stdout == b""
    assert done.stderr.decode("utf-8").strip() == "goose_hook_adapter: OSError: injected adapter failure"
