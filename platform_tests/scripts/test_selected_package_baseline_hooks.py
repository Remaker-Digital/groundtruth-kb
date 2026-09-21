"""Authored hooks use the selected package and cannot silently replace it.

These subprocess checks exercise current derivations, not actual host invocation.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import groundtruth_kb
import pytest

ROOT = Path(__file__).resolve().parents[2]
PROFILES = tomllib.loads((ROOT / "scripts/harness_projection/profiles.toml").read_text(encoding="utf-8"))["harnesses"]
HARNESSES = [name for name, row in PROFILES.items() if row.get("status") != "profile_pending"]
HOOKS = ("directive-enforcement-adapter.py", "code-quality-baseline-proposal-check.py")
HOOKS_ROOT = Path(".harness-baseline-configuration/hooks")


@pytest.fixture(scope="module")
def projected(tmp_path_factory):
    from scripts.check_harness_parity import _load_projector

    target = tmp_path_factory.mktemp("selected-package-hooks")
    projector = _load_projector(ROOT)
    assert len(HARNESSES) == 8
    shutil.copytree(ROOT / HOOKS_ROOT, target / HOOKS_ROOT, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for harness in HARNESSES:
        plan = projector.build_plan(harness)
        assert not plan.gaps, plan.gaps
        for relative, content in plan.writes.items():
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    # A tempting source checkout must not override the selected package or
    # repair a missing package. It is intentionally unusable.
    decoy = target / "groundtruth-kb/src/groundtruth_kb"
    decoy.mkdir(parents=True)
    (decoy / "__init__.py").write_text('raise AssertionError("source checkout was selected")\n', encoding="utf-8")
    (target / "groundtruth.toml").write_text("[groundtruth]\n", encoding="utf-8")
    return target


def hook_environment(projected, harness):
    return {
        **os.environ,
        PROFILES[harness]["project_dir_var"]: str(projected),
        "GTKB_PROJECT_ROOT": str(projected),
        "PYTHONIOENCODING": "utf-8",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


@pytest.mark.parametrize("harness", HARNESSES)
@pytest.mark.parametrize("hook", HOOKS)
def test_projected_hook_uses_selected_package_and_retains_denial(projected, tmp_path, harness, hook):
    origin_report = tmp_path / "origins.json"
    probe = """import json, runpy, sys
from pathlib import Path
try:
    runpy.run_path(sys.argv[1], run_name="__main__")
finally:
    Path(sys.argv[2]).write_text(json.dumps({name: str(Path(module.__file__).resolve())
        for name, module in sys.modules.items()
        if (name == "groundtruth_kb" or name.startswith("groundtruth_kb.")) and getattr(module, "__file__", None)}), encoding="utf-8")
"""
    payload = (
        {"tool_name": "Bash", "tool_input": {"command": "claude -p review"}, "cwd": str(projected)}
        if hook.startswith("directive")
        else {
            "tool_name": "Write",
            "tool_input": {"file_path": "bridge/proposal.md", "content": "bridge_kind: implementation_proposal\n"},
        }
    )
    result = subprocess.run(
        [sys.executable, "-B", "-P", "-c", probe, str(projected / HOOKS_ROOT / hook), str(origin_report)],
        input=json.dumps(payload),
        text=True,
        encoding="utf-8",
        capture_output=True,
        env=hook_environment(projected, harness),
        cwd=projected,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    if hook.startswith("directive"):
        assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "Direct harness-to-harness launch" in response["hookSpecificOutput"]["permissionDecisionReason"]
    else:
        assert response["decision"] == "block"
        assert "missing_heading" in response["reason"]
    origins = json.loads(origin_report.read_text(encoding="utf-8"))
    expected = Path(groundtruth_kb.__file__).resolve().parent
    assert origins
    assert all(Path(value).is_relative_to(expected) for value in origins.values()), origins
    assert not (projected / ".gtkb-state").exists()


@pytest.mark.parametrize("harness", HARNESSES)
@pytest.mark.parametrize("hook", HOOKS)
def test_unavailable_selected_package_does_not_fall_back_to_checkout(projected, harness, hook):
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            "import runpy,sys; runpy.run_path(sys.argv[1],run_name='__main__')",
            str(projected / HOOKS_ROOT / hook),
        ],
        input="{}",
        text=True,
        encoding="utf-8",
        capture_output=True,
        env=hook_environment(projected, harness),
        cwd=projected,
        timeout=30,
    )
    assert result.returncode != 0
    assert "No module named 'groundtruth_kb'" in result.stderr
    assert not result.stdout.strip()
    assert "source checkout was selected" not in result.stderr
