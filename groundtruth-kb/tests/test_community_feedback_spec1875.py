"""SPEC-1875 community feedback coverage of the real host-repository carriers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _repo_read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _issue_template(relative_path: str) -> tuple[dict[str, Any], str]:
    template = _repo_read(relative_path)
    assert template.startswith("---\n")
    frontmatter, body = template[4:].split("\n---\n", 1)
    return yaml.safe_load(frontmatter), body.lower()


def test_bug_report_issue_form_captures_required_feedback() -> None:
    metadata, body = _issue_template(".github/ISSUE_TEMPLATE/bug_report.md")

    assert metadata["name"] == "Bug Report"
    assert "bug" in metadata["labels"]
    for heading in ("## description", "## steps to reproduce", "## expected behavior", "## actual behavior"):
        assert heading in body
    assert "**surface:**" in body
    assert "**scope:** gtkb" in body or "**scope:** gt-kb" in body
    assert "gt-kb platform / agent red application / other adopter" in body


def test_feature_request_issue_form_captures_method_feedback_shape() -> None:
    metadata, body = _issue_template(".github/ISSUE_TEMPLATE/feature_request.md")

    assert metadata["name"] == "Feature Request"
    assert "enhancement" in metadata["labels"]
    for heading in ("## problem / motivation", "## proposed solution", "## scope", "## alternatives considered"):
        assert heading in body
    assert "tradeoffs" in body
    assert "method-feedback" in body
    assert "hosted application" in body


def test_pull_request_template_requires_problem_rationale_and_testing_evidence() -> None:
    template = _repo_read(".github/pull_request_template.md").lower()

    for required in ("## problem", "## approach", "## rationale", "## testing evidence"):
        assert required in template
    assert "existing tests pass" in template
    assert "new tests added" in template
    assert "assertions still pass" in template
    assert "platform configuration, governance, bridge, dashboard, or workflow change" in template


def test_contributing_documents_monthly_method_feedback_triage_loop() -> None:
    contributing = _read("CONTRIBUTING.md")
    lower = contributing.lower()

    for template in ("bug_report.md", "feature_request.md"):
        assert f"template={template}" in contributing
        assert f"template={template}" in _read("docs/contributing.md")
        assert (REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / template).is_file()
    assert "method-feedback" in contributing
    assert "triaged monthly" in lower
    assert "first monday of each month" in lower
    assert "actionable" in lower
    assert "informational" in lower
    assert "needs-discussion" in lower
    assert "specifications or work items" in lower


def test_readme_points_contributors_to_feedback_loop() -> None:
    readme = _read("README.md")

    assert "CONTRIBUTING.md" in readme
    assert "method-feedback" in readme
    assert "value feedback about the engineering method itself" in readme


def test_code_of_conduct_declares_scope_and_reporting_contact() -> None:
    code_of_conduct = _read("CODE_OF_CONDUCT.md").lower()

    assert "community spaces" in code_of_conduct
    assert "officially representing the community" in code_of_conduct
    assert "support@remakerdigital.com" in code_of_conduct


def test_package_ci_guards_feedback_loop_artifacts_with_ruff_and_pytest() -> None:
    workflow = yaml.safe_load(_repo_read(".github/workflows/groundtruth-kb-tests.yml"))
    triggers = workflow.get("on") or workflow[True]
    for event in ("pull_request", "push"):
        assert ".github/ISSUE_TEMPLATE/**" in triggers[event]["paths"]
        assert ".github/pull_request_template.md" in triggers[event]["paths"]
        assert "groundtruth-kb/**" in triggers[event]["paths"]
    steps = workflow["jobs"]["platform-tests"]["steps"]
    feedback_step = next(step for step in steps if step.get("name") == "Check community feedback contract")
    assert feedback_step["working-directory"] == "groundtruth-kb"
    assert not feedback_step.get("continue-on-error", False)
    assert "python -m ruff check tests/test_community_feedback_spec1875.py" in feedback_step["run"]
    assert "python -m ruff format --check tests/test_community_feedback_spec1875.py" in feedback_step["run"]
    assert "python -m pytest tests/test_community_feedback_spec1875.py -q --tb=short" in feedback_step["run"]
    package_step = next(step for step in steps if step.get("name") == "Run GroundTruth KB platform tests")
    assert package_step["working-directory"] == "groundtruth-kb"
    assert "python -m pytest tests/ -q --tb=short" in package_step["run"]
    assert steps.index(feedback_step) < steps.index(package_step)
