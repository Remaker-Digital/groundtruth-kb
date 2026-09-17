"""The packaged gate and script adapter run without checkout-only imports."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import groundtruth_kb
import pytest
from groundtruth_kb.bridge import effect_gate

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("entry", ["module", "script"])
@pytest.mark.parametrize(
    "payload,denied",
    [
        ("", True),
        ("{", True),
        ("[]", True),
        ({"tool_name": "Read", "tool_input": {"file_path": "foreign.py"}}, False),
        ({"tool_name": "Write", "tool_input": {"file_path": "foreign.py", "content": "x"}}, True),
        ({"tool_name": "Bash", "tool_input": {"command": "git add foreign.py"}}, True),
        ({"tool_name": "Write", "tool_input": {"content": "x"}}, True),
    ],
)
def test_selected_package_runs_outside_checkout_without_local_helpers(entry, payload, denied, tmp_path):
    sentinel = tmp_path / "foreign.py"
    sentinel.write_bytes(b"foreign bytes stay exact")
    adapter = tmp_path / "hook.py"
    adapter.write_bytes((ROOT / "scripts/implementation_start_gate.py").read_bytes())
    env = dict(os.environ, PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    for name in list(env):
        if name.startswith(("GT_", "GTKB_", "PG")):
            env.pop(name)
    env.update(PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    command = [sys.executable, "-P"]
    command += ["-m", "groundtruth_kb.bridge.effect_gate"] if entry == "module" else [str(adapter)]
    raw = json.dumps({**payload, "cwd": str(tmp_path)}) if isinstance(payload, dict) else payload
    result = subprocess.run(
        command,
        cwd=tmp_path,
        env=env,
        input=raw,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stderr
    assert not result.stderr
    response = json.loads(result.stdout)
    if denied:
        assert response["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
        assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
    else:
        assert response == {}
    assert sentinel.read_bytes() == b"foreign bytes stay exact"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["foreign.py", "hook.py"]


@pytest.mark.parametrize("supplied", ["none", "cwd", "environment", "project_root"])
def test_root_resolution_uses_invocation_inputs_not_package_location(supplied, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GTKB_PROJECT_ROOT", raising=False)
    payload = {}
    expected = tmp_path
    if supplied != "none":
        payload["cwd"] = str(tmp_path / "workspace")
        expected = Path(payload["cwd"])
    if supplied in {"environment", "project_root"}:
        monkeypatch.setenv("GTKB_PROJECT_ROOT", str(tmp_path / "installation"))
        expected = tmp_path / "installation"
    if supplied == "project_root":
        payload["project_root"] = str(tmp_path / "explicit")
        expected = Path(payload["project_root"])
    assert effect_gate._project_root(payload) == expected.resolve()


@pytest.mark.parametrize("entry", ["script", "scaffold-template"])
def test_missing_package_emits_explicit_denial_without_echoing_payload(entry, tmp_path):
    source = (
        ROOT / "scripts/implementation_start_gate.py"
        if entry == "script"
        else groundtruth_kb.get_templates_dir() / "hooks/bridge-compliance-gate.py"
    )
    target = tmp_path / "hook.py"
    target.write_bytes(source.read_bytes())
    payload = json.dumps(
        {"tool_name": "Write", "tool_input": {"file_path": "foreign.py", "content": "private-test-content"}}
    )
    result = subprocess.run(
        [sys.executable, "-I", "-S", str(target)],
        input=payload,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=20,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0 and not result.stderr
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse"
    assert output["permissionDecision"] == "deny"
    assert "native_effect_checker_unavailable" in output["permissionDecisionReason"]
    assert "private-test-content" not in result.stdout
    assert sorted(p.name for p in tmp_path.iterdir()) == ["hook.py"]


@pytest.mark.parametrize(
    "decision,diagnostic,expected",
    [
        ({}, False, "{}\n"),
        ({}, True, '{"decision": "allow", "diagnostic": true, "reason": "", "would_block": false}\n'),
        (
            {"decision": "block", "reason": "bound π"},
            False,
            '{"hookSpecificOutput": {"additionalContext": "bound \\u03c0", "hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "bound \\u03c0"}}\n',
        ),
        (
            {"decision": "block", "reason": "bound π"},
            True,
            '{"decision": "block", "diagnostic": true, "reason": "bound \\u03c0", "would_block": true}\n',
        ),
        (
            {"decision": "block", "reason": ""},
            False,
            '{"hookSpecificOutput": {"additionalContext": "BLOCKED (GTKB-IMPLEMENTATION-START-GATE)", "hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "BLOCKED (GTKB-IMPLEMENTATION-START-GATE)"}}\n',
        ),
        ({"decision": "allow", "detail": "a\nb"}, False, '{"decision": "allow", "detail": "a\\nb"}\n'),
    ],
)
def test_effect_entrypoint_preserves_exact_stdout_protocol(decision, diagnostic, expected, monkeypatch, capsys):
    import io

    supplied = {"tool_name": "Read", "tool_input": {"file_path": "fixture.py"}}
    monkeypatch.setattr(sys, "argv", ["effect-gate", *(["--diagnostic"] if diagnostic else [])])
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(supplied)))
    received = []

    def decide(payload):
        received.append(payload)
        return decision

    monkeypatch.setattr(effect_gate, "gate_decision", decide)
    assert effect_gate.main() == 0
    captured = capsys.readouterr()
    assert captured.out == expected and captured.err == ""
    assert received == [{**supplied, **({"__gtkb_registry_diagnostic__": True} if diagnostic else {})}]
