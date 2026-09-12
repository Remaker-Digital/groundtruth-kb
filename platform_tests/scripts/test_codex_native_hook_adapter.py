"""Exercise the rendered Windows launcher, native adapter and real child scripts.

The vendor host's hook trust and execution are separate qualification obligations.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from scripts.check_harness_parity import _commands, _load_projector, _references_script

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def runtime(tmp_path):
    root = tmp_path / "installed workspace"
    (root / "scripts").mkdir(parents=True)
    (root / ".codex/hooks").mkdir(parents=True)
    (root / "groundtruth-kb").mkdir()
    (root / "nested cwd").mkdir()
    subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
    shutil.copyfile(ROOT / "scripts/codex_hook_adapter.py", root / "scripts/codex_hook_adapter.py")
    venv = root / "groundtruth-kb/.venv"
    subprocess.run(["cmd", "/c", "mklink", "/J", str(venv), sys.prefix], check=True, capture_output=True)
    target = root / ".codex/hooks/probe.py"
    target.write_text(
        "import json, os, sys\nfrom pathlib import Path\n"
        "data=json.load(sys.stdin)\nPath('observed.json').write_text(json.dumps({'payload':data,"
        "'args':sys.argv[1:],'native':os.environ.get('GTKB_NATIVE_CONTEXT_ID'),"
        "'root':os.environ.get('GTKB_PROJECT_ROOT'),'harness':os.environ.get('GTKB_HARNESS_NAME')}))\n"
        "print('{}')\n",
        encoding="utf-8",
    )
    try:
        yield root, target
    finally:
        os.rmdir(venv)  # Remove the fixture junction only.


def command(event="PreToolUse", args=(), timeout=8):
    engine = _load_projector(ROOT)
    profile = engine.load_profiles()["harnesses"]["codex"]
    gaps = []
    hook = {"script": "probe.py", "args": list(args)}
    rendered = engine._native_cwd_hook_command(profile, hook, event, timeout, {}, gaps)
    assert not gaps
    assert str(ROOT) not in rendered and "$CODEX_PROJECT_DIR" not in rendered
    assert _references_script(rendered, ".codex/hooks/probe.py", profile["project_dir_var"])
    return rendered


def payload(root, event="PreToolUse"):
    return {
        "session_id": "native-context",
        "cwd": str(root / "nested cwd"),
        "hook_event_name": event,
        "tool_name": "apply_patch",
        "tool_input": {"command": "*** Begin Patch\n*** Add File: café.py\n+é = 1\n*** End Patch\n"},
        "prompt": "::init gtkb pb",
        "model": "observed-model",
    }


def run(runtime, data, *, event="PreToolUse", args=(), timeout=8):
    root, _ = runtime
    # Run the exact generated shell command, including both Windows and
    # PowerShell quoting boundaries, from outside the installed workspace.
    result = subprocess.run(
        command(event, args, timeout),
        shell=True,
        cwd=root.parent,
        input=data if isinstance(data, str) else json.dumps(data, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
        env={**os.environ, "GTKB_NATIVE_CONTEXT_ID": "stale-alias", "GTKB_PROJECT_ROOT": "foreign-root"},
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize("event", ["PreToolUse", "PostToolUse", "SessionStart", "UserPromptSubmit", "Stop"])
def test_rendered_native_events_preserve_identity_utf8_cwd_and_literal_arguments(runtime, event):
    root, _ = runtime
    supplied = payload(root, event)
    args = ("argument with spaces", "a&b;literal", "an'apostrophe", "café")
    assert run(runtime, supplied, event=event, args=args) == {}
    observed = json.loads((root / "observed.json").read_text())
    assert observed["payload"] == {**supplied, "project_root": str(root)}
    assert observed["native"] == supplied["session_id"]
    assert observed["root"] == str(root) and observed["harness"] == "codex"
    assert observed["args"] == list(args)
    assert not (root / "nested cwd/café.py").exists()
    assert not (root / ".claude").exists()


@pytest.mark.parametrize(
    "response",
    [
        {"decision": "block", "reason": "scope refused"},
        {"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": "scope refused"}},
        {"continue": False, "stopReason": "scope refused"},
    ],
)
def test_pretool_denials_use_the_supported_native_shape(runtime, response):
    root, target = runtime
    target.write_text(f"print({json.dumps(json.dumps(response))})")
    result = run(runtime, payload(root))
    assert result == {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "scope refused",
        }
    }


@pytest.mark.parametrize(
    "body",
    [
        "print('{}'); raise SystemExit(7)",
        "print('not JSON')",
        "print('[]')",
        'print(\'{"decision": "allow", "decision": "block"}\')',
        "print('{\"decision\": []}')",
        "import time; time.sleep(5)",
    ],
)
def test_failure_malformed_output_and_timeout_cannot_allow(runtime, body):
    root, target = runtime
    target.write_text(body)
    result = run(runtime, payload(root), timeout=4)
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize(
    "change",
    ["bad_json", "duplicate", "missing_native", "wrong_event", "missing_cwd", "missing_runtime", "missing_target"],
)
def test_invalid_native_envelope_or_runtime_refuses_without_child_effect(runtime, change):
    root, target = runtime
    data = payload(root)
    if change == "bad_json":
        data = "bad json"
    elif change == "duplicate":
        data = json.dumps(data)[:-1] + ', "session_id":"other"}'
    elif change == "missing_native":
        data.pop("session_id")
    elif change == "wrong_event":
        data["hook_event_name"] = "Stop"
    elif change == "missing_cwd":
        data["cwd"] = "relative"
    elif change == "missing_runtime":
        (root / "scripts/codex_hook_adapter.py").unlink()
    else:
        target.unlink()
    result = run(runtime, data)
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert not (root / "observed.json").exists()


def test_command_enumeration_never_rewrites_shell_code():
    raw = r"powershell.exe -Command $value.EndsWith('\')"
    assert list(_commands({"command": raw})) == [raw]


def test_native_registration_covers_bash_and_patch_once():
    engine = _load_projector(ROOT)
    profile = engine.load_profiles()["harnesses"]["codex"]
    plan = engine.build_plan("codex")
    assert not plan.gaps
    document = json.loads(plan.writes[profile["hooks_json_path"]])
    manifest = tomllib.loads((ROOT / ".harness-baseline-configuration/hooks/manifest.toml").read_text(encoding="utf-8"))
    expected_events = {profile["hook_events"][hook["event"]] for hook in manifest["hook"]}
    assert set(document["hooks"]) == expected_events
    assert "PreToolUse" in expected_events
    gates = [
        g
        for g in document["hooks"]["PreToolUse"]
        if any(
            _references_script(c, "scripts/implementation_start_gate.py", profile["project_dir_var"])
            for c in _commands(g)
        )
    ]
    assert len(gates) == 1
    assert set(gates[0]["matcher"].split("|")) == {"apply_patch", "Bash"}


def test_each_registered_hook_uses_the_native_adapter_without_batch_or_finalizer():
    engine = _load_projector(ROOT)
    profile = engine.load_profiles()["harnesses"]["codex"]
    plan = engine.build_plan("codex")
    assert not plan.gaps
    document = json.loads(plan.writes[profile["hooks_json_path"]])
    commands = list(_commands(document))
    assert commands
    for command in commands:
        assert _references_script(command, "scripts/codex_hook_adapter.py", profile["project_dir_var"])
        assert "--batch" not in command
        for retired in ("run_py_no_window", "auto_finalize_sweep", "bridge_verified_backlog_reconciler", ".claude/"):
            assert retired not in command


@pytest.mark.parametrize("event", ["PreToolUse", "PostToolUse", "SessionStart", "UserPromptSubmit", "Stop"])
def test_one_selected_child_produces_one_native_response(runtime, event):
    root, target = runtime
    target.write_text(
        "from pathlib import Path\n"
        "p=Path('invocations.txt')\n"
        "p.write_text(p.read_text()+'child\\n' if p.exists() else 'child\\n')\n"
        "print('{}')\n",
        encoding="utf-8",
    )
    assert run(runtime, payload(root, event), event=event) == {}
    assert (root / "invocations.txt").read_text() == "child\n"


@pytest.mark.parametrize(
    "response",
    [{"systemMessage": "current hook context"}, {"hookSpecificOutput": {"additionalContext": "current hook context"}}],
)
def test_selected_hook_context_is_preserved_without_aggregation(runtime, response):
    root, target = runtime
    target.write_text(f"print({json.dumps(json.dumps(response))})", encoding="utf-8")
    result = run(runtime, payload(root))
    assert result == {
        "hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "current hook context"}
    }
