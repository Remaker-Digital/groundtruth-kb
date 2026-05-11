"""Static checks for the dedicated GroundTruth KB platform test workflow."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "groundtruth-kb-tests.yml"


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _on_block(workflow: dict) -> dict:
    return workflow.get("on") or workflow.get(True)


def test_groundtruth_kb_tests_workflow_triggers_on_platform_paths() -> None:
    workflow = _workflow()
    on_block = _on_block(workflow)

    assert "workflow_dispatch" in on_block
    for event in ("pull_request", "push"):
        paths = on_block[event]["paths"]
        assert "groundtruth-kb/**" in paths
        assert ".github/workflows/groundtruth-kb-tests.yml" in paths


def test_groundtruth_kb_tests_workflow_runs_platform_pytest_lane() -> None:
    workflow = _workflow()
    job = workflow["jobs"]["platform-tests"]
    steps = job["steps"]

    install_step = next(step for step in steps if step.get("name") == "Install GroundTruth KB test dependencies")
    test_step = next(step for step in steps if step.get("name") == "Run GroundTruth KB platform tests")

    assert job["runs-on"] == "ubuntu-latest"
    assert test_step["working-directory"] == "groundtruth-kb"
    assert "./groundtruth-kb[dev,search]" in install_step["run"]
    assert "python -m pytest tests/ -q --tb=short" in test_step["run"]
    assert "--junitxml=.pytest-results/groundtruth-kb-tests.xml" in test_step["run"]
