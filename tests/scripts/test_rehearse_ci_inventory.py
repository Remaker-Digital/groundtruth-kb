"""Tests for Wave 2 Slice 7 ``_ci_inventory.py``.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice7-003.md`` (REVISED-1)
and ``-004`` (Codex GO with cross-slice consistency constraint).

Fixture-based per the Slice 4/5/6 pattern; no test walks ``LEGACY_ROOT``
directly. The cross-slice consistency test imports Slice 6's source
constants to compare classification + signal + mechanism_origin exactly.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse import (
    _ci_inventory,  # noqa: E402
    _release_readiness_split,  # noqa: E402  (cross-slice consistency import)
)

# ---- Fixtures ----------------------------------------------------------


def _build_workflow_fixture(workflows_dir: Path, files: dict[str, str]) -> None:
    workflows_dir.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (workflows_dir / name).write_text(content, encoding="utf-8")


def _build_ci_configs_fixture(project_root: Path, files: dict[str, str]) -> None:
    for relative, content in files.items():
        path = project_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _empty_manifest() -> dict[str, Any]:
    return {"excluded_paths": []}


def _run_lane(
    tmp_path: Path,
    *,
    workflow_files: dict[str, str] | None = None,
    ci_config_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Construct fixture trees and invoke the lane. Returns the result dict."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    workflows_dir = project_root / ".github" / "workflows"
    if workflow_files:
        _build_workflow_fixture(workflows_dir, workflow_files)
    else:
        workflows_dir.mkdir(parents=True)
    if ci_config_files:
        _build_ci_configs_fixture(project_root, ci_config_files)
    output_dir = tmp_path / "output"
    return _ci_inventory.run(
        _empty_manifest(),
        output_dir,
        ci_root=workflows_dir,
        ci_configs_root=project_root,
    )


def _read_json_artifact(tmp_path: Path) -> dict[str, Any]:
    path = tmp_path / "output" / "ci_inventory" / "ci_inventory.json"
    return json.loads(path.read_text(encoding="utf-8"))


# ---- Common contract ---------------------------------------------------


def test_run_dry_run_returns_skipped(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    output_dir = tmp_path / "output"
    result = _ci_inventory.run(
        _empty_manifest(),
        output_dir,
        dry_run=True,
        ci_root=project_root,
        ci_configs_root=project_root,
    )
    assert result["status"] == "skipped"
    assert result["metrics"] == {"reason": "dry_run"}
    assert result["output_files"] == []


# ---- Classification: workflows -----------------------------------------


def test_run_classifies_release_candidate_gate_as_adopter_not_framework(tmp_path: Path) -> None:
    """Slice 6 cross-slice consistency regression guard (per -003 fix + -004 GO).

    The original Slice 7 -001 proposal incorrectly stated Slice 6 classified
    this as framework. Slice 6 actually classifies it as adopter with signal
    `application_release_gate_surface` and mechanism_origin `agent_red_local`.
    """
    result = _run_lane(
        tmp_path,
        workflow_files={"release-candidate-gate.yml": "# release gate workflow\n"},
    )
    assert result["status"] == "ok"
    payload = _read_json_artifact(tmp_path)
    rcg = next(w for w in payload["workflows"] if w["path"].endswith("release-candidate-gate.yml"))
    assert rcg["classification"] == "adopter"
    assert rcg["classification_signal"] == "application_release_gate_surface"
    assert rcg["mechanism_origin"] == "agent_red_local"


def test_run_classifies_build_agent_containers_as_adopter(tmp_path: Path) -> None:
    _run_lane(
        tmp_path,
        workflow_files={"build-agent-containers.yml": "# build adopter containers\n"},
    )
    payload = _read_json_artifact(tmp_path)
    row = payload["workflows"][0]
    assert row["classification"] == "adopter"
    assert row["classification_signal"] == "application_build_or_deploy_workflow"


def test_run_classifies_accessibility_chromatic_visual_regression_as_adopter(tmp_path: Path) -> None:
    result = _run_lane(
        tmp_path,
        workflow_files={
            "accessibility.yml": "# axe-core\n",
            "chromatic.yml": "# chromatic\n",
            "visual-regression.yml": "# playwright baselines\n",
        },
    )
    assert result["status"] == "ok"
    payload = _read_json_artifact(tmp_path)
    for row in payload["workflows"]:
        assert row["classification"] == "adopter"
        assert row["classification_signal"] == "application_ui_gate_workflow"


def test_run_classifies_deploy_docs_as_adopter(tmp_path: Path) -> None:
    _run_lane(
        tmp_path,
        workflow_files={"deploy-docs.yml": "# deploys agentredcx.com docs\n"},
    )
    payload = _read_json_artifact(tmp_path)
    row = payload["workflows"][0]
    assert row["classification"] == "adopter"
    assert row["classification_signal"] == "application_docs_workflow"


def test_run_content_scan_groundtruth_kb_reference_classifies_framework(tmp_path: Path) -> None:
    """Workflow with no filename rule but groundtruth_kb body reference → framework."""
    _run_lane(
        tmp_path,
        workflow_files={"unknown-workflow.yml": "# runs groundtruth_kb test suite\n"},
    )
    payload = _read_json_artifact(tmp_path)
    row = payload["workflows"][0]
    assert row["classification"] == "framework"
    assert row["classification_signal"] == "groundtruth_kb_reference"


def test_run_content_scan_src_reference_classifies_adopter(tmp_path: Path) -> None:
    """Workflow with no filename rule but src/ body reference → adopter."""
    _run_lane(
        tmp_path,
        workflow_files={"unknown-workflow.yml": "# runs against src/ tree\n"},
    )
    payload = _read_json_artifact(tmp_path)
    row = payload["workflows"][0]
    assert row["classification"] == "adopter"
    assert row["classification_signal"] == "agent_red_source_reference"


def test_run_lint_yml_classifies_unclassified_when_mixed_scope(tmp_path: Path) -> None:
    """lint.yml is hardcoded mixed-scope → unclassified for owner decision."""
    _run_lane(
        tmp_path,
        workflow_files={"lint.yml": "# ruff against entire tree\n"},
    )
    payload = _read_json_artifact(tmp_path)
    row = payload["workflows"][0]
    assert row["classification"] == "unclassified"
    assert row["classification_signal"] == "mixed_scope_linter_owner_decision_required"


def test_run_workflow_with_no_signal_is_unclassified(tmp_path: Path) -> None:
    """Workflow with no filename rule and no content marker → unclassified."""
    _run_lane(
        tmp_path,
        workflow_files={"opaque-workflow.yml": "# opaque\nsteps:\n  - echo hi\n"},
    )
    payload = _read_json_artifact(tmp_path)
    row = payload["workflows"][0]
    assert row["classification"] == "unclassified"
    assert row["classification_signal"] == "no_classification_signal"


# ---- Classification: CI configs ---------------------------------------


def test_run_sonar_properties_classifies_adopter(tmp_path: Path) -> None:
    _run_lane(
        tmp_path,
        ci_config_files={"sonar-project.properties": "sonar.projectKey=mike-remakerdigital_agent-red\n"},
    )
    payload = _read_json_artifact(tmp_path)
    sonar = next(c for c in payload["ci_configs"] if c["path"] == "sonar-project.properties")
    assert sonar["classification"] == "adopter"
    assert sonar["classification_signal"] == "agent_red_sonar_config"
    assert sonar["exists"] is True


def test_run_absent_ci_configs_recorded_with_exists_false(tmp_path: Path) -> None:
    """Probed-but-absent files have exists=False, classification=unclassified."""
    _run_lane(tmp_path)  # no CI configs created
    payload = _read_json_artifact(tmp_path)
    assert all(c["exists"] is False for c in payload["ci_configs"])
    assert all(c["classification"] == "unclassified" for c in payload["ci_configs"])
    assert all(c["classification_signal"] == "absent_probed" for c in payload["ci_configs"])


# ---- Output artifacts -------------------------------------------------


def test_run_writes_csv_with_correct_columns(tmp_path: Path) -> None:
    _run_lane(tmp_path, workflow_files={"accessibility.yml": "#\n"})
    csv_path = tmp_path / "output" / "ci_inventory" / "ci-command-inventory.csv"
    assert csv_path.exists()
    rows = list(csv.DictReader(csv_path.read_text(encoding="utf-8").splitlines()))
    expected_columns = {
        "path",
        "type",
        "classification",
        "classification_signal",
        "mechanism_origin",
        "size_bytes",
        "exists",
        "gt_classify_tree_ownership",
    }
    assert set(rows[0].keys()) == expected_columns


def test_run_writes_preview_markdown_with_three_sections(tmp_path: Path) -> None:
    _run_lane(
        tmp_path,
        workflow_files={
            "accessibility.yml": "#\n",  # adopter
            "lint.yml": "#\n",  # unclassified (mixed-scope)
        },
    )
    preview = (tmp_path / "output" / "ci_inventory" / "ci-rewrite-preview.md").read_text(encoding="utf-8")
    assert "## Move to `applications/Agent_Red/<path>` (adopter)" in preview
    assert "## Keep at GT-KB root (framework)" in preview
    assert "## Owner decision required (unclassified)" in preview
    assert "accessibility.yml" in preview
    assert "lint.yml" in preview


def test_run_writes_ci_inventory_json_with_summary(tmp_path: Path) -> None:
    _run_lane(tmp_path, workflow_files={"accessibility.yml": "#\n"})
    payload = _read_json_artifact(tmp_path)
    assert payload["schema_version"] == 1
    assert "summary" in payload
    assert payload["summary"]["workflow_count"] == 1
    assert payload["summary"]["adopter_count"] >= 1


def test_run_writes_result_json_on_ok_path(tmp_path: Path) -> None:
    result = _run_lane(tmp_path, workflow_files={"accessibility.yml": "#\n"})
    assert result["status"] == "ok"
    result_path = tmp_path / "output" / "ci_inventory" / "result.json"
    assert result_path.exists()
    assert any("result.json" in str(p) for p in result["output_files"])


def test_run_writes_result_json_on_error_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Probe failure path emits result.json with status=error."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    workflows_dir = project_root / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)

    def _raise_oserror(*args: object, **kwargs: object) -> None:
        raise OSError("simulated probe failure")

    monkeypatch.setattr(_ci_inventory, "_probe_workflows", _raise_oserror)
    output_dir = tmp_path / "output"
    result = _ci_inventory.run(
        _empty_manifest(),
        output_dir,
        ci_root=workflows_dir,
        ci_configs_root=project_root,
    )
    assert result["status"] == "error"
    assert (output_dir / "ci_inventory" / "result.json").exists()


# ---- Cross-reference with Slice 4 -------------------------------------


def test_run_cross_references_path_rewrite_classification_when_present(tmp_path: Path) -> None:
    """If Slice 4's classification.json exists in same output dir, look up ownership."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    workflows_dir = project_root / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "accessibility.yml").write_text("#\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    # Plant Slice 4 output under output_dir/path_rewrite/classification.json
    pr_dir = output_dir / "path_rewrite"
    pr_dir.mkdir(parents=True)
    (pr_dir / "classification.json").write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "path": ".github/workflows/accessibility.yml",
                        "ownership": "adopter-owned",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    result = _ci_inventory.run(
        _empty_manifest(),
        output_dir,
        ci_root=workflows_dir,
        ci_configs_root=project_root,
    )
    assert result["status"] == "ok"
    payload = _read_json_artifact(tmp_path)
    row = payload["workflows"][0]
    assert row["gt_classify_tree_ownership"] == "adopter-owned"


def test_run_cross_reference_absent_leaves_column_empty(tmp_path: Path) -> None:
    """Without Slice 4 output present, gt_classify_tree_ownership is empty."""
    _run_lane(tmp_path, workflow_files={"accessibility.yml": "#\n"})
    payload = _read_json_artifact(tmp_path)
    row = payload["workflows"][0]
    assert row["gt_classify_tree_ownership"] == ""


# ---- Cross-slice consistency with Slice 6 (per GO -004) ---------------


def test_run_classification_matches_slice6_for_release_candidate_gate(tmp_path: Path) -> None:
    """Slice 7 + Slice 6 must agree on release-candidate-gate.yml.

    Per Codex post-impl NO-GO -006 §"Required Revision": derive ALL three
    expected fields (classification, signal, mechanism_origin) from
    Slice 6's RUNTIME behavior, not from hardcoded string literals.
    Construct a fixture root containing the workflow file, invoke
    ``_release_readiness_split._classify_release_gate_surfaces`` against
    it, and compare Slice 7's row to Slice 6's row exactly. If Slice 6
    ever changes any of the three fields for this surface, this test
    fails immediately.
    """
    slice6_relpath = ".github/workflows/release-candidate-gate.yml"
    # Build a fixture root containing the workflow at the canonical relpath
    # so Slice 6's classifier sees `exists=True` and emits a real row.
    fixture_root = tmp_path / "slice6_fixture_root"
    workflow_in_fixture = fixture_root / slice6_relpath
    workflow_in_fixture.parent.mkdir(parents=True)
    workflow_in_fixture.write_text("# release gate workflow\n", encoding="utf-8")

    # Invoke Slice 6's runtime classifier against the fixture; pull its row.
    slice6_entries = _release_readiness_split._classify_release_gate_surfaces(fixture_root)
    slice6_row = next(e for e in slice6_entries if e["path"] == slice6_relpath)

    # Run Slice 7 against the same workflow file via its own fixture path.
    _run_lane(
        tmp_path,
        workflow_files={"release-candidate-gate.yml": "# release gate workflow\n"},
    )
    payload = _read_json_artifact(tmp_path)
    slice7_row = next(w for w in payload["workflows"] if w["path"] == slice6_relpath)

    # All three fields derived from Slice 6's runtime output. If Slice 6's
    # classifier changes any of classification / signal / mechanism_origin
    # for this surface, this test fails — the regression guard requested
    # in Codex -006 §"Required Revision".
    assert slice7_row["classification"] == slice6_row["classification"]
    assert slice7_row["classification_signal"] == slice6_row["classification_signal"]
    assert slice7_row["mechanism_origin"] == slice6_row["mechanism_origin"]


# ---- Manifest excluded_paths consumption (per Codex -008 NO-GO) -------


def test_run_excluded_paths_skip_workflow_files_under_excluded_top_level(tmp_path: Path) -> None:
    """Per proposal -001 §6.6 + Codex -008 §"Required Revision" item 1:
    when manifest excludes a top-level dir containing CI surfaces, those
    surfaces must NOT appear in the inventory.
    """
    project_root = tmp_path / "project"
    project_root.mkdir()
    workflows_dir = project_root / ".github" / "workflows"
    _build_workflow_fixture(workflows_dir, {"accessibility.yml": "# adopter UI gate\n"})
    output_dir = tmp_path / "output"
    # Manifest excludes the entire .github tree.
    result = _ci_inventory.run(
        {"excluded_paths": [".github"]},
        output_dir,
        ci_root=workflows_dir,
        ci_configs_root=project_root,
    )
    assert result["status"] == "ok"
    payload = json.loads((output_dir / "ci_inventory" / "ci_inventory.json").read_text(encoding="utf-8"))
    # accessibility.yml should NOT be in the inventory because .github excluded.
    assert payload["workflows"] == [], f"Excluded workflow appeared in inventory: {payload['workflows']}"
    # CI configs probed at root: .github/dependabot.yml is also excluded.
    rel_paths = {c["path"] for c in payload["ci_configs"]}
    assert ".github/dependabot.yml" not in rel_paths


def test_run_excluded_paths_full_path_match_skips_specific_config(tmp_path: Path) -> None:
    """A specific full-path match in excluded_paths skips that single CI config.

    Validates the second match mode in _is_path_excluded_by_manifest:
    relative_path in excluded_full (not just top-level dir match).
    """
    project_root = tmp_path / "project"
    project_root.mkdir()
    workflows_dir = project_root / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    _build_ci_configs_fixture(
        project_root,
        {"sonar-project.properties": "sonar.projectKey=mike-remakerdigital_agent-red\n"},
    )
    output_dir = tmp_path / "output"
    result = _ci_inventory.run(
        {"excluded_paths": ["sonar-project.properties"]},
        output_dir,
        ci_root=workflows_dir,
        ci_configs_root=project_root,
    )
    assert result["status"] == "ok"
    payload = json.loads((output_dir / "ci_inventory" / "ci_inventory.json").read_text(encoding="utf-8"))
    rel_paths = {c["path"] for c in payload["ci_configs"]}
    assert "sonar-project.properties" not in rel_paths


# ---- python-tests.yml content-scan classifier (per proposal §3 + Codex -008) ---


def test_run_pytest_workflow_classifies_by_pytest_target_adopter(tmp_path: Path) -> None:
    """python-tests.yml running pytest against tests/ (no groundtruth_kb subpath)
    classifies as adopter with signal agent_red_pytest_workflow."""
    _run_lane(
        tmp_path,
        workflow_files={
            "python-tests.yml": (
                "name: python-tests\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pytest tests/\n"
            )
        },
    )
    payload = json.loads((tmp_path / "output" / "ci_inventory" / "ci_inventory.json").read_text(encoding="utf-8"))
    row = next(w for w in payload["workflows"] if w["path"].endswith("python-tests.yml"))
    assert row["classification"] == "adopter"
    assert row["classification_signal"] == "agent_red_pytest_workflow"


def test_run_pytest_workflow_classifies_by_pytest_target_framework(tmp_path: Path) -> None:
    """python-tests.yml running pytest tests/groundtruth_kb classifies as framework."""
    _run_lane(
        tmp_path,
        workflow_files={
            "python-tests.yml": (
                "name: python-tests\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pytest tests/groundtruth_kb/\n"
            )
        },
    )
    payload = json.loads((tmp_path / "output" / "ci_inventory" / "ci_inventory.json").read_text(encoding="utf-8"))
    row = next(w for w in payload["workflows"] if w["path"].endswith("python-tests.yml"))
    assert row["classification"] == "framework"
    assert row["classification_signal"] == "framework_pytest_workflow"


def test_run_pytest_workflow_classifies_no_pytest_command_as_unclassified(tmp_path: Path) -> None:
    """python-tests.yml with no pytest command falls to no_classification_signal."""
    _run_lane(
        tmp_path,
        workflow_files={"python-tests.yml": "# placeholder\n"},
    )
    payload = json.loads((tmp_path / "output" / "ci_inventory" / "ci_inventory.json").read_text(encoding="utf-8"))
    row = next(w for w in payload["workflows"] if w["path"].endswith("python-tests.yml"))
    assert row["classification"] == "unclassified"
    assert row["classification_signal"] == "no_classification_signal"
