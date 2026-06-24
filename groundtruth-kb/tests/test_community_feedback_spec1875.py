"""SPEC-1875 community feedback harvesting loop coverage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _load_yaml(relative_path: str) -> dict[str, Any]:
    return yaml.safe_load(_read(relative_path))


def _field_by_id(form: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in form.get("body", []) if isinstance(item, dict) and "id" in item}


def test_bug_report_issue_form_captures_required_feedback() -> None:
    form = _load_yaml(".github/ISSUE_TEMPLATE/bug_report.yml")

    assert form["name"] == "Bug Report"
    assert "bug" in form["labels"]

    fields = _field_by_id(form)
    for field_id in ("component", "expected", "actual", "reproduction"):
        assert field_id in fields
        assert fields[field_id]["validations"]["required"] is True

    assert fields["component"]["type"] == "dropdown"
    assert "Knowledge DB (db.py)" in fields["component"]["attributes"]["options"]
    assert "Minimal steps to reproduce" in fields["reproduction"]["attributes"]["description"]


def test_feature_request_issue_form_captures_method_feedback_shape() -> None:
    form = _load_yaml(".github/ISSUE_TEMPLATE/feature_request.yml")

    assert form["name"] == "Feature Request"
    assert "enhancement" in form["labels"]

    fields = _field_by_id(form)
    for field_id in ("problem", "approach", "scope"):
        assert field_id in fields
        assert fields[field_id]["validations"]["required"] is True

    assert "problem or limitation" in fields["problem"]["attributes"]["description"]
    assert "tradeoffs" in fields["approach"]["attributes"]["description"]
    assert fields["scope"]["type"] == "dropdown"


def test_pull_request_template_requires_problem_rationale_and_testing_evidence() -> None:
    template = _read(".github/pull_request_template.md").lower()

    for required in ("## problem", "## approach", "## rationale", "## testing"):
        assert required in template

    assert "existing tests pass" in template
    assert "new tests added" in template
    assert "assertions still pass" in template


def test_contributing_documents_monthly_method_feedback_triage_loop() -> None:
    contributing = _read("CONTRIBUTING.md")
    lower = contributing.lower()

    assert "template=bug_report.yml" in contributing
    assert "template=feature_request.yml" in contributing
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
    workflow = _load_yaml(".github/workflows/ci.yml")
    test_base_steps = workflow["jobs"]["test-base"]["steps"]
    run_blocks = "\n".join(step.get("run", "") for step in test_base_steps if isinstance(step, dict))

    assert "ruff check ." in run_blocks
    assert "ruff format --check ." in run_blocks
    assert "pytest -v --tb=short" in run_blocks
