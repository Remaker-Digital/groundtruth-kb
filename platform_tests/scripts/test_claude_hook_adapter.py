"""Claude hook adapter: every failure of a GT-KB hook is Claude Code's blocking exit 2 (c123; batch design WP2 2.4).

Claude Code treats a hook that exits nonzero other than 2 without a valid JSON decision, cannot start, prints output it
cannot read or reaches its timeout as a non-blocking error and runs the tool (hooks reference, "Exit code output" and
"Timeouts"). Under the dispatched ``--permission-mode bypassPermissions`` (owner decision B1) that would leave the tool
unguarded, so the adapter answers each of those with exit 2 and the reason on stderr, passes a structured deny through
with its reason, and passes a successful target's stdout through unchanged. The target hook here is a stub that records
what it received and answers as instructed; it lies where the adapter accepts targets, under the copied adapter's root.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TARGET = ".harness-baseline-configuration/hooks/stub_hook.py"
STUB = """
import json, os, sys
raw = sys.stdin.buffer.read().decode("utf-8")
record = {"raw": raw, "argv": sys.argv[1:], "cwd": os.getcwd(), "native": os.environ.get("GTKB_NATIVE_CONTEXT_ID"),
          "project_dir": os.environ.get("CLAUDE_PROJECT_DIR")}
open(os.environ["STUB_RECORD"], "w", encoding="utf-8").write(json.dumps(record))
mode = os.environ.get("STUB_MODE", "allow-json")
answers = json.loads(os.environ["STUB_ANSWERS"])
if mode in answers:
    sys.stdout.buffer.write(answers[mode].encode("utf-8"))
    sys.stdout.flush()
if mode == "allow-stderr":
    sys.stderr.write("stub diagnostic for the debug log\\n")
elif mode == "deny-exit1":
    sys.exit(1)
elif mode == "crash":
    raise RuntimeError("stub crashed")
elif mode == "exit1":
    sys.exit(1)
elif mode == "exit2":
    sys.stderr.write("stub exit-2 refusal\\n")
    sys.exit(2)
elif mode == "hang":
    import subprocess, time
    # A grandchild that inherits this hook's output pipes and outlives it: it must not hold the adapter open.
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    open(os.environ["STUB_RECORD"] + ".child", "w", encoding="utf-8").write(str(child.pid))
    time.sleep(60)
"""
DENY = json.dumps(
    {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "stub refusal: foreign_context_material",
        }
    }
)
ANSWERS = {
    "allow-json": "{}\n",
    "allow-stderr": "{}\n",
    "allow-context": json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "note"}}),
    "deny-json": DENY + "\n",
    "deny-exit1": DENY + "\n",
    "ask-json": json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": "stub asks the owner",
            }
        }
    ),
    # c123 (batch design WP2 2.4): sot-read-discipline's form, the deprecated top-level block with no final newline.
    "block-json": json.dumps({"decision": "block", "reason": "stub block"}),
    "deny-without-event": json.dumps(
        {"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": "stub refusal, no event"}}
    ),
    "deny-other-event": json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "stub refusal, other event",
            }
        }
    ),
    "noise": "not json\n",
    "bad-json": "{not json}\n",
    "json-list": "[1, 2]\n",
    "bad-decision": json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "maybe"}}),
    "bad-continue": json.dumps({"continue": "no"}),
    "context-text": "plain context for the session\n",
}
PAYLOAD = {
    "session_id": "claude-native-1",
    "transcript_path": "C:/Users/fixture/.claude/projects/x/transcript.jsonl",
    "cwd": "E:/project",
    "permission_mode": "bypassPermissions",
    "hook_event_name": "PreToolUse",
    "tool_name": "Write",
    "tool_input": {"file_path": "E:/project/notes.txt", "content": "x"},
    "tool_use_id": "toolu_fixture",
}


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """A disposable installation: the adapter under scripts/ and the stub where baseline hooks live."""
    installation = tmp_path / "installation"
    (installation / "scripts").mkdir(parents=True)
    shutil.copyfile(ROOT / "scripts" / "claude_hook_adapter.py", installation / "scripts" / "claude_hook_adapter.py")
    stub = installation / TARGET
    stub.parent.mkdir(parents=True)
    stub.write_text(STUB, encoding="utf-8")
    return installation


def _run(
    root: Path,
    *,
    mode: str = "allow-json",
    payload: dict | None = None,
    raw: bytes | None = None,
    target: str | None = TARGET,
    leading: list[str] | None = None,
    env: dict[str, str] | None = None,
    tail: tuple[str, ...] = ("--harness", "claude"),
):
    record = root.parent / "record.json"
    record.unlink(missing_ok=True)
    session_cwd = root.parent / "session-cwd"
    session_cwd.mkdir(exist_ok=True)
    child_env = {
        **os.environ,
        "STUB_MODE": mode,
        "STUB_RECORD": str(record),
        "STUB_ANSWERS": json.dumps(ANSWERS),
        "PYTHONIOENCODING": "utf-8",
        **(env or {}),
    }
    stdin = raw if raw is not None else json.dumps(payload or PAYLOAD).encode("utf-8")
    done = subprocess.run(
        [
            sys.executable,
            "-B",
            str(root / "scripts" / "claude_hook_adapter.py"),
            *(leading or []),
            *([target] if target is not None else []),
            *tail,
        ],
        input=stdin,
        cwd=session_cwd,
        capture_output=True,
        env=child_env,
        timeout=120,
        check=False,
    )
    seen = json.loads(record.read_text(encoding="utf-8")) if record.exists() else None
    return done.returncode, done.stdout, done.stderr.decode("utf-8", "replace"), seen


def test_an_allow_exits_zero_and_the_target_sees_claude_codes_call_unchanged(root):
    code, out, err, seen = _run(
        root,
        leading=["--deadline", "30"],
        env={"CLAUDE_PROJECT_DIR": "E:/project", "GTKB_NATIVE_CONTEXT_ID": "claude-native-1"},
    )
    assert (code, out, err) == (0, b"{}\n", "")
    assert seen["raw"] == json.dumps(PAYLOAD), "the payload reaches the target byte for byte"
    assert seen["argv"] == ["--harness", "claude"], "the deadline is the adapter's, not the target's"
    assert Path(seen["cwd"]) == root.parent / "session-cwd", "the target runs where Claude Code ran the hook"
    assert (seen["project_dir"], seen["native"]) == ("E:/project", "claude-native-1")


@pytest.mark.parametrize("mode", ["allow-context", "ask-json"])
def test_a_successful_targets_stdout_passes_through_unchanged(root, mode):
    code, out, err, _seen = _run(root, mode=mode)
    assert (code, out, err) == (0, ANSWERS[mode].encode("utf-8"), "")


def test_an_empty_answer_is_no_decision_and_exits_zero(root):
    answers = {**ANSWERS, "allow-json": ""}
    code, out, err, seen = _run(root, env={"STUB_ANSWERS": json.dumps(answers)})
    assert (code, out, err) == (0, b"", "")
    assert seen is not None


def test_a_successful_targets_stderr_is_kept_for_claude_codes_debug_log(root):
    code, out, err, _seen = _run(root, mode="allow-stderr")
    assert (code, out) == (0, b"{}\n")
    assert err.strip() == "stub diagnostic for the debug log"


@pytest.mark.parametrize(
    ("mode", "reason"),
    [
        ("deny-json", "stub refusal: foreign_context_material"),
        ("deny-exit1", "stub refusal: foreign_context_material"),
        ("block-json", "stub block"),
    ],
    ids=["deny_exit_0", "deny_exit_1", "top_level_block"],
)
def test_a_structured_deny_passes_through_with_its_reason(root, mode, reason):
    """Whatever the target's exit code, its deny reaches Claude Code unchanged, and Claude Code shows its reason."""
    code, out, err, _seen = _run(root, mode=mode)
    assert code == 0
    assert out == ANSWERS[mode].encode("utf-8")
    assert reason in out.decode("utf-8")
    assert err == ""


@pytest.mark.parametrize(
    ("mode", "reason"),
    [
        ("crash", "GT-KB: the stub_hook.py check failed (exit status 1: RuntimeError: stub crashed)"),
        ("exit1", "GT-KB: the stub_hook.py check failed (exit status 1), so the call is refused"),
        ("exit2", "stub exit-2 refusal"),
        ("noise", "GT-KB: the stub_hook.py check printed output that is not a hook decision"),
        ("bad-json", "GT-KB: the stub_hook.py check printed output that is not a hook decision"),
        ("json-list", "GT-KB: the stub_hook.py check printed output that is not a hook decision"),
        ("bad-decision", "GT-KB: the stub_hook.py check printed output that is not a hook decision"),
        ("bad-continue", "GT-KB: the stub_hook.py check printed output that is not a hook decision"),
        ("deny-without-event", "stub refusal, no event"),
        ("deny-other-event", "stub refusal, other event"),
    ],
)
def test_a_failing_target_is_claude_codes_exit_two_with_the_reason_on_stderr(root, mode, reason):
    code, out, err, seen = _run(root, mode=mode)
    assert code == 2
    assert out == b"", "a refusal prints no decision Claude Code could read instead of the stderr reason"
    assert reason in err, err
    assert seen is not None, "the target ran"


@pytest.mark.parametrize(("event", "expected"), [("SessionStart", 0), ("UserPromptSubmit", 0), ("PreToolUse", 2)])
def test_plain_text_is_context_on_context_events_and_no_decision_elsewhere(root, event, expected):
    code, out, _err, _seen = _run(root, mode="context-text", payload={**PAYLOAD, "hook_event_name": event})
    assert code == expected
    assert out == (ANSWERS["context-text"].encode("utf-8") if expected == 0 else b"")


def test_a_payload_naming_no_event_is_judged_as_pre_tool_use(root):
    """Claude Code always names the event; a payload without one gets the strictest reading."""
    payload = {key: value for key, value in PAYLOAD.items() if key != "hook_event_name"}
    assert _run(root, mode="context-text", payload=payload)[0] == 2
    code, out, _err, seen = _run(root, mode="deny-json", raw=b"{not json")
    assert (code, out) == (0, ANSWERS["deny-json"].encode("utf-8"))
    assert seen["raw"] == "{not json", "an unreadable payload still reaches the target, which judges it"


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


def test_a_target_that_misses_its_deadline_is_refused_and_its_process_tree_ended(root):
    """A hung check is a refusal within the adapter's deadline: Claude Code would let a cancelled hook's call run."""
    started = time.monotonic()
    code, out, err, seen = _run(root, mode="hang", leading=["--deadline", "3"])
    elapsed = time.monotonic() - started
    assert code == 2 and out == b""
    assert "GT-KB: the stub_hook.py check did not answer within 3 s, so the call is refused" in err
    assert seen is not None and seen["argv"] == ["--harness", "claude"]
    assert elapsed < 15, f"the adapter waited {elapsed:.1f} s for a target past its 3 s deadline"
    grandchild = int((root.parent / "record.json.child").read_text(encoding="utf-8"))
    deadline = time.monotonic() + 10
    while _alive(grandchild) and time.monotonic() < deadline:
        time.sleep(0.2)
    assert not _alive(grandchild), "the target's process tree must be ended"


@pytest.mark.parametrize(
    "leading",
    [["--deadline"], ["--deadline", "soon"], ["--deadline", "0"], ["--deadline", "-3"], ["--deadline", "inf"]],
)
def test_a_malformed_deadline_blocks_without_running_the_target(root, leading):
    code, out, err, seen = _run(root, leading=leading)
    assert code == 2 and out == b""
    assert "--deadline" in err
    assert seen is None


@pytest.mark.parametrize(
    ("target", "message"),
    [
        (None, "missing target hook script"),
        (".harness-baseline-configuration/hooks/absent.py", "is missing or redirected"),
        ("scripts/../.harness-baseline-configuration/hooks/stub_hook.py", "is redirected"),
        ("elsewhere/stub_hook.py", "is neither platform code nor a baseline hook"),
        ("outside", "lies outside"),
    ],
    ids=["no_target", "missing", "parent_relative", "other_directory", "outside_the_root"],
)
def test_a_target_that_is_not_an_installed_hook_blocks_without_running(root, target, message):
    elsewhere = root / "elsewhere" / "stub_hook.py"
    elsewhere.parent.mkdir()
    elsewhere.write_text(STUB, encoding="utf-8")
    outside = root.parent / "outside_stub.py"
    outside.write_text(STUB, encoding="utf-8")
    code, out, err, seen = _run(
        root,
        target=str(outside) if target == "outside" else target,
        tail=() if target is None else ("--harness", "claude"),
    )
    assert code == 2 and out == b""
    assert message in err, err
    assert seen is None, "the target must not run"


RAISING_RUNNER = """
import runpy, subprocess, sys
error = {"OSError": OSError, "RuntimeError": RuntimeError}[sys.argv[3]]
def refuse_to_start(*args, **kwargs):
    raise error("injected adapter failure")
subprocess.Popen = refuse_to_start
sys.argv = [sys.argv[1], sys.argv[2], "--harness", "claude"]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


@pytest.mark.parametrize(
    ("error", "message"),
    [
        ("OSError", "GT-KB: the stub_hook.py check could not start (OSError), so the call is refused."),
        ("RuntimeError", "claude_hook_adapter: RuntimeError: injected adapter failure"),
    ],
)
def test_a_target_that_cannot_start_or_an_adapter_failure_blocks(root, error, message):
    """Claude Code runs the tool of a hook that cannot start; the adapter's own catch-all is the fail-safe."""
    done = subprocess.run(
        [sys.executable, "-B", "-c", RAISING_RUNNER, str(root / "scripts" / "claude_hook_adapter.py"), TARGET, error],
        input=json.dumps(PAYLOAD).encode("utf-8"),
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        timeout=120,
        check=False,
    )
    assert done.returncode == 2
    assert done.stdout == b""
    assert done.stderr.decode("utf-8").strip() == message
