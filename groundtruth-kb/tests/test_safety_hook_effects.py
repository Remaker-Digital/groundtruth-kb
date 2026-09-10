"""Actual safety-hook subprocesses must deny effects without exposing secrets."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from groundtruth_kb import get_templates_dir

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(params=["baseline", "package"])
def hooks(request):
    return (
        ROOT / ".harness-baseline-configuration/hooks" if request.param == "baseline" else get_templates_dir() / "hooks"
    )


def run(hooks, name, payload):
    result = subprocess.run(
        [sys.executable, str(hooks / name)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    return result, json.loads(result.stdout)


@pytest.mark.parametrize("tool", ["Write", "Edit", "MultiEdit", "NotebookEdit", "apply_patch", "Bash", "PowerShell"])
def test_credential_effect_refusal_covers_all_declared_tool_payloads(hooks, tool):
    secret = "sk-" + "ant-api03-" + "c" * 20
    fields = {
        "Write": {"file_path": "docs-site/example.md", "content": secret},
        "Edit": {"file_path": ".env.local", "new_string": secret},
        "MultiEdit": {"file_path": "src/config.py", "edits": [{"new_string": "safe"}, {"new_string": secret}]},
        "NotebookEdit": {"file_path": "analysis.ipynb", "new_source": secret},
        "apply_patch": {"patch": "*** Begin Patch\n+" + secret + "\n*** End Patch"},
        "Bash": {"command": "echo " + secret},
        "PowerShell": {"command": "Write-Output " + secret},
    }
    result, output = run(hooks, "credential-scan.py", {"tool_name": tool, "tool_input": fields[tool]})
    denial = output["hookSpecificOutput"]
    assert denial["permissionDecision"] == "deny"
    assert "credential_detected" in denial["permissionDecisionReason"]
    assert secret not in result.stdout + result.stderr


@pytest.mark.parametrize("filename", ["credential-scan.py", "destructive-gate.py"])
@pytest.mark.parametrize(
    "payload", [[], {"tool_name": "Bash", "tool_input": None}, {"tool_name": "Bash", "tool_input": {"command": []}}]
)
def test_malformed_effect_refuses_with_native_diagnostic(hooks, filename, payload):
    _, output = run(hooks, filename, payload)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "input_invalid" in output["hookSpecificOutput"]["permissionDecisionReason"]


@pytest.mark.parametrize("tool", ["Bash", "PowerShell"])
def test_destructive_command_denies_and_read_only_command_passes(hooks, tool):
    _, refused = run(hooks, "destructive-gate.py", {"tool_name": tool, "tool_input": {"command": "git reset --hard"}})
    assert refused["hookSpecificOutput"]["permissionDecision"] == "deny"
    _, allowed = run(hooks, "destructive-gate.py", {"tool_name": tool, "tool_input": {"command": "git status --short"}})
    assert allowed == {}
    _, clean = run(hooks, "credential-scan.py", {"tool_name": tool, "tool_input": {"command": "git status --short"}})
    assert clean == {}
