"""Native Antigravity boundary; child fixtures do not qualify the vendor host."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def runtime(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copyfile(ROOT / "scripts/antigravity_hook_adapter.py", scripts / "antigravity_hook_adapter.py")
    target = scripts / "probe.py"
    target.write_text(
        "import json, os, sys\nfrom pathlib import Path\n"
        "Path('observed.json').write_text(json.dumps({'payload': json.load(sys.stdin), "
        "'native': os.environ.get('GTKB_NATIVE_CONTEXT_ID'), 'root': os.environ.get('GTKB_PROJECT_ROOT'), "
        "'harness': os.environ.get('GTKB_HARNESS_NAME'), 'args': sys.argv[1:]}))\nprint('{}')\n",
        encoding="utf-8",
    )
    return tmp_path, target


def payload(root, name="run_command", args=None):
    return {
        "conversationId": "native-antigravity-context",
        "workspacePaths": [str(root)],
        "modelName": "observed-model",
        "transcriptPath": str(root / "never-read.jsonl"),
        "toolCall": {
            "name": name,
            "args": args if args is not None else {"CommandLine": "git status", "Cwd": str(root)},
        },
    }


def run(runtime, data, *, event="PreToolUse", target=None, timeout=2):
    root, default_target = runtime
    env = {**os.environ, "GTKB_NATIVE_CONTEXT_ID": "stale-alias", "GTKB_PROJECT_ROOT": "foreign-root"}
    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/antigravity_hook_adapter.py"),
            "--event",
            event,
            "--timeout",
            str(timeout),
            str(target or default_target),
            "literal-argument",
        ],
        input=data if isinstance(data, str) else json.dumps(data),
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return result, json.loads(result.stdout)


@pytest.mark.parametrize(
    ("name", "args", "tool", "tool_input"),
    [
        ("run_command", {"CommandLine": "git status", "Cwd": "SUBDIR"}, "Bash", {"command": "git status"}),
        (
            "write_to_file",
            {"TargetFile": "TARGET", "CodeContent": "new\n"},
            "Write",
            {"file_path": "TARGET", "content": "new\n"},
        ),
        (
            "replace_file_content",
            {"TargetFile": "TARGET", "TargetContent": "old", "ReplacementContent": "new", "AllowMultiple": False},
            "Edit",
            {"file_path": "TARGET", "old_string": "old", "new_string": "new", "replace_all": False},
        ),
        (
            "multi_replace_file_content",
            {
                "TargetFile": "TARGET",
                "ReplacementChunks": [{"TargetContent": "old", "ReplacementContent": "new", "AllowMultiple": True}],
            },
            "MultiEdit",
            {"file_path": "TARGET", "edits": [{"old_string": "old", "new_string": "new", "replace_all": True}]},
        ),
        ("view_file", {"AbsolutePath": "TARGET"}, "Read", {"file_path": "TARGET"}),
        ("list_dir", {"DirectoryPath": "TARGET"}, "Glob", {"path": "TARGET"}),
        (
            "find_by_name",
            {"SearchDirectory": "TARGET", "Pattern": "*.py"},
            "Glob",
            {"path": "TARGET", "pattern": "*.py"},
        ),
        ("grep_search", {"SearchPath": "TARGET", "Query": "word"}, "Grep", {"path": "TARGET", "pattern": "word"}),
    ],
)
def test_native_tool_fields_and_context_reach_only_selected_hook(runtime, name, args, tool, tool_input):
    root, _ = runtime
    subdir = root / "sub dir"
    subdir.mkdir()
    args = json.loads(
        json.dumps(args).replace("SUBDIR", subdir.as_posix()).replace("TARGET", (root / "target.py").as_posix())
    )
    tool_input = json.loads(json.dumps(tool_input).replace("TARGET", (root / "target.py").as_posix()))
    for key in ("file_path", "path"):
        if key in tool_input:
            tool_input[key] = str(Path(tool_input[key]))
    result, response = run(runtime, payload(root, name, args))
    assert result.returncode == 0 and response == {"decision": "allow"}
    observed = json.loads((root / "observed.json").read_text())
    assert observed["payload"]["tool_name"] == tool
    assert observed["payload"]["tool_input"] == tool_input
    assert observed["payload"]["session_id"] == observed["native"] == "native-antigravity-context"
    assert Path(observed["payload"]["cwd"]) == (subdir if name == "run_command" else root)
    assert Path(observed["payload"]["project_root"]) == Path(observed["root"]) == root
    assert observed["harness"] == "antigravity"
    assert observed["args"] == ["literal-argument"]
    assert not (root / ".claude").exists()
    assert not (root / "never-read.jsonl").exists()


@pytest.mark.parametrize(
    "response",
    [
        {"decision": "block", "reason": "current claim refused"},
        {"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": "current claim refused"}},
        {"hookSpecificOutput": {"permissionDecision": "ask", "permissionDecisionReason": "current claim refused"}},
        {"continue": False, "stopReason": "current claim refused"},
    ],
)
def test_native_pretool_denial_is_not_translated_to_allow(runtime, response):
    root, target = runtime
    target.write_text(f"print({json.dumps(json.dumps(response))})\n", encoding="utf-8")
    _, output = run(runtime, payload(root))
    assert output == {"decision": "deny", "reason": "current claim refused"}


@pytest.mark.parametrize(
    "body",
    [
        "print('{}'); raise SystemExit(7)",
        "raise RuntimeError('failed hook')",
        "print('not JSON')",
        "print('[]')",
        """print('{"decision": "unknown"}')""",
        """print('{"decision": "allow", "decision": "block"}')""",
        """print('{"hookSpecificOutput": 3}')""",
        "import time; time.sleep(10)",
    ],
)
def test_failed_or_malformed_hook_cannot_allow(runtime, body):
    root, target = runtime
    target.write_text(body, encoding="utf-8")
    _, output = run(runtime, payload(root), timeout=0.25)
    assert output["decision"] == "deny" and output["reason"]


@pytest.mark.parametrize("data", ["", "not json", "[]", "{}", '{"conversationId":"a","conversationId":"b"}'])
def test_malformed_native_input_refuses_before_child(runtime, data):
    root, _ = runtime
    _, output = run(runtime, data)
    assert output["decision"] == "deny"
    assert not (root / "observed.json").exists()


@pytest.mark.parametrize(
    ("name", "args"),
    [
        ("run_command", {}),
        ("run_command", {"CommandLine": "do something", "Cwd": "relative"}),
        ("write_to_file", {"TargetFile": "relative", "CodeContent": "hello"}),
        ("replace_file_content", {"TargetFile": "TARGET"}),
        ("multi_replace_file_content", {"TargetFile": "TARGET", "ReplacementChunks": "invalid"}),
        ("unknown_tool", {}),
        ("manage_task", {"Action": "send_input", "TaskId": "foreign", "Input": "write"}),
    ],
)
def test_unscoped_native_effect_refuses_before_child(runtime, name, args):
    root, _ = runtime
    args = json.loads(json.dumps(args).replace("TARGET", (root / "target.py").as_posix()))
    _, output = run(runtime, payload(root, name, args))
    assert output["decision"] == "deny"
    assert not (root / "observed.json").exists()


@pytest.mark.parametrize("change", ["missing_context", "foreign_workspace", "relative_workspace", "empty_workspaces"])
def test_native_context_and_workspace_are_required(runtime, change):
    root, _ = runtime
    data = payload(root)
    if change == "missing_context":
        data.pop("conversationId")
    elif change == "foreign_workspace":
        data["workspacePaths"] = [str(root.parent)]
    elif change == "relative_workspace":
        data["workspacePaths"] = ["."]
    else:
        data["workspacePaths"] = []
    _, output = run(runtime, data)
    assert output["decision"] == "deny"
    assert not (root / "observed.json").exists()


@pytest.mark.parametrize("location", [".claude/hooks", ".codex/hooks", "elsewhere", "scripts/../.claude/hooks"])
def test_peer_or_unregistered_hook_path_is_refused(runtime, location):
    root, _ = runtime
    target = root / location / "probe.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("from pathlib import Path\nPath('foreign-marker').write_text('bad')\nprint('{}')")
    _, output = run(runtime, payload(root), target=target)
    assert output["decision"] == "deny"
    assert not (root / "foreign-marker").exists()


@pytest.mark.parametrize("event", ["PostToolUse", "Stop"])
def test_native_non_pretool_events_keep_context_and_native_output(runtime, event):
    root, _ = runtime
    data = payload(root)
    if event == "Stop":
        data.pop("toolCall")
        data.update(fullyIdle=True, terminationReason="model_stop", executionNum=1)
    else:
        data["error"] = "tool failed"
    result, output = run(runtime, data, event=event)
    assert result.returncode == 0
    assert output == ({} if event == "PostToolUse" else {"decision": "allow"})
    adapted = json.loads((root / "observed.json").read_text())["payload"]
    assert adapted["hook_event_name"] == event
    assert adapted["session_id"] == data["conversationId"]
    assert adapted.get("error") == data.get("error")


@pytest.mark.parametrize(
    "body",
    [
        """print('{"decision": "block", "reason": "unfinished"}')""",
        "raise SystemExit(2)",
    ],
)
def test_stop_block_or_failure_requests_native_continuation(runtime, body):
    root, target = runtime
    target.write_text(body)
    data = payload(root)
    data.pop("toolCall")
    data["fullyIdle"] = True
    _, output = run(runtime, data, event="Stop")
    assert output["decision"] == "continue" and output["reason"]


def test_posttool_failure_is_nonzero_without_fabricated_permission(runtime):
    root, target = runtime
    target.write_text("raise SystemExit(7)")
    result, output = run(runtime, payload(root), event="PostToolUse")
    assert result.returncode != 0 and output == {} and result.stderr


def test_native_registration_keeps_unsupported_baseline_events_visible():
    from scripts.check_harness_parity import _load_projector, _registration_events, check_harness_parity

    engine = _load_projector(ROOT)
    profile = engine.load_profiles()["harnesses"]["antigravity"]
    plan = engine.build_plan("antigravity")
    registration = json.loads(plan.writes[profile["hooks_json_path"]])
    assert set(registration) == {"gtkb"}
    events = _registration_events(profile, registration)
    assert set(events) == {"PreToolUse", "PostToolUse", "Stop"}
    assert all("hooks" in group for event in ("PreToolUse", "PostToolUse") for group in events[event])
    assert all("command" in handler and "hooks" not in handler for handler in events["Stop"])
    assert all("--event Stop" in handler["command"] for handler in events["Stop"])
    assert not any(".claude" in content or "CODEX_" in content for content in [json.dumps(registration)])
    report = check_harness_parity(ROOT, harness="antigravity", installed=False)
    assert report["status"] == "fail"
    assert plan.gaps and all(
        "no native event for prompt_submit" in gap or "no native event for session_start" in gap for gap in plan.gaps
    ), plan.gaps


def test_redirected_hook_refuses_before_foreign_script(runtime):
    root, _ = runtime
    foreign = root / "foreign"
    foreign.mkdir()
    (foreign / "probe.py").write_text("from pathlib import Path\nPath('foreign-marker').write_text('bad')")
    redirect = root / "scripts/redirect"
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(redirect), str(foreign)], check=True, capture_output=True)
    else:
        redirect.symlink_to(foreign, target_is_directory=True)
    try:
        _, output = run(runtime, payload(root), target=redirect / "probe.py")
        assert output["decision"] == "deny"
        assert not (root / "foreign-marker").exists()
    finally:
        if os.name == "nt":
            os.rmdir(redirect)
        else:
            redirect.unlink()


def test_canonical_hook_recognizes_git_reset():
    from scripts.lo_file_safety_payloads import _WRITEISH_SHELL_RE

    assert _WRITEISH_SHELL_RE.search("git reset groundtruth.db")
    assert _WRITEISH_SHELL_RE.search("git reset --hard HEAD")


def test_canonical_hook_recognizes_python_whole_file():
    from scripts.lo_file_safety_payloads import _PYTHON_WHOLE_FILE_RE

    assert _PYTHON_WHOLE_FILE_RE.search("shutil.copy('a', 'b')")
    assert _PYTHON_WHOLE_FILE_RE.search("os.remove('file')")
    assert _PYTHON_WHOLE_FILE_RE.search("open('file', 'w')")


def test_canonical_hook_opaque_detection():
    from scripts.lo_file_safety_payloads import _is_opaque_shell

    assert _is_opaque_shell("rm $(find . -name '*.db')")
    assert _is_opaque_shell("git reset `cat targets.txt`")
    assert not _is_opaque_shell("git reset groundtruth.db")
    assert not _is_opaque_shell("git status")
