"""Behavioral tests for fail-closed change-controlled artifact evaluation."""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_artifact_evaluability.py"
PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402


@pytest.fixture
def evaluator():
    spec = importlib.util.spec_from_file_location("check_artifact_evaluability", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def project(tmp_path: Path) -> tuple[Path, KnowledgeDB]:
    (tmp_path / "present.txt").write_text("ready\n", encoding="utf-8")
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    yield tmp_path, db
    db.close()


def _insert(db: KnowledgeDB, spec_id: str, assertions: list[dict]) -> dict:
    db.insert_spec(
        id=spec_id,
        title=spec_id,
        type="design_constraint",
        status="specified",
        changed_by="test",
        change_reason="test",
        assertions=assertions,
    )
    result = db.get_spec(spec_id)
    assert result is not None
    return result


def test_full_evaluation_passes_and_binds_subject_and_evaluator(evaluator, project):
    root, db = project
    spec = _insert(
        db,
        "DCL-EVAL-001",
        [{"id": "A1", "type": "file_exists", "file": "present.txt"}],
    )
    evaluated_at = datetime(2026, 7, 13, tzinfo=UTC)

    result = evaluator.evaluate_spec(spec, project_root=root, evaluated_at=evaluated_at)

    assert result["scope_result"] == "PASS"
    assert result["carrier_result"] == "PASS"
    assert result["subject_version"] == 1
    assert len(result["subject_sha256"]) == 64
    assert len(result["evaluator_sha256"]) == 64
    assert result["evaluated_at"] == evaluated_at.isoformat()
    assert result["currentness"]["invalidated_by"] == [
        "subject_version_change",
        "assertion_definition_change",
        "evaluator_change",
    ]


def test_unsupported_assertion_is_unassessed_not_pass(evaluator, project):
    root, db = project
    spec = _insert(
        db,
        "DCL-EVAL-002",
        [{"id": "A1", "type": "human_review", "description": "manual"}],
    )

    result = evaluator.evaluate_spec(spec, project_root=root)

    assert result["scope_result"] == "FAIL"
    assert result["carrier_result"] == "FAIL"
    assert result["evaluation_reason"] == "unsupported-required"
    assert result["results"][0]["passed"] is False


def test_scoped_pass_keeps_full_carrier_partial(evaluator, project):
    root, db = project
    spec = _insert(
        db,
        "DCL-EVAL-003",
        [
            {"id": "A1", "type": "file_exists", "file": "present.txt"},
            {"id": "A2", "type": "file_exists", "file": "later.txt"},
        ],
    )

    result = evaluator.evaluate_spec(spec, project_root=root, assertion_ids={"A1"})

    assert result["scope"] == "scoped"
    assert result["scope_result"] == "PASS"
    assert result["carrier_result"] == "PARTIAL"
    assert result["selected_assertion_ids"] == ["A1"]
    assert result["deferred_assertion_ids"] == ["A2"]


def test_unknown_scoped_assertion_fails_closed(evaluator, project):
    root, db = project
    spec = _insert(
        db,
        "DCL-EVAL-004",
        [{"id": "A1", "type": "file_exists", "file": "present.txt"}],
    )

    with pytest.raises(evaluator.EvaluationError, match="unknown scoped assertion ids: A9"):
        evaluator.evaluate_spec(spec, project_root=root, assertion_ids={"A9"})


def test_evaluation_does_not_record_assertion_runs(evaluator, project):
    root, db = project
    _insert(
        db,
        "DCL-EVAL-005",
        [{"id": "A1", "type": "file_exists", "file": "present.txt"}],
    )
    connection = db._get_conn()
    before = connection.execute("SELECT COUNT(*) FROM assertion_runs").fetchone()[0]

    report = evaluator.evaluate_specs(db, project_root=root, spec_ids=["DCL-EVAL-005"])

    after = connection.execute("SELECT COUNT(*) FROM assertion_runs").fetchone()[0]
    assert report["aggregate_result"] == "PASS"
    assert before == after == 0


def test_assertion_scope_requires_exactly_one_carrier(evaluator, project):
    root, db = project
    for spec_id in ("DCL-EVAL-006", "DCL-EVAL-007"):
        _insert(db, spec_id, [{"id": "A1", "type": "file_exists", "file": "present.txt"}])

    with pytest.raises(evaluator.EvaluationError, match="exactly one"):
        evaluator.evaluate_specs(
            db,
            project_root=root,
            spec_ids=["DCL-EVAL-006", "DCL-EVAL-007"],
            assertion_ids={"A1"},
        )


@pytest.mark.parametrize("evidence_state", ["stale", "unavailable", "contradictory", "unverifiable"])
def test_noncurrent_evidence_cannot_satisfy_current_gate(evaluator, project, evidence_state):
    root, db = project
    spec = _insert(
        db,
        f"DCL-EVIDENCE-{evidence_state.upper()}",
        [{"id": "A1", "type": "file_exists", "file": "present.txt"}],
    )

    result = evaluator.evaluate_spec(spec, project_root=root, evidence_state=evidence_state)

    assert result["scope_result"] == "FAIL"
    assert result["evaluation_reason"] == f"current-gate:{evidence_state}"


def test_prose_and_stored_assertion_order_reconciles(evaluator, project):
    root, db = project
    spec = _insert(
        db,
        "DCL-RECONCILE-001",
        [
            {"id": "A1", "type": "file_exists", "file": "present.txt", "description": "First exists."},
            {"id": "A2", "type": "file_exists", "file": "present.txt", "description": "Second exists."},
        ],
    )
    spec["description"] = """## Required Executable Assertions

1. First exists.
2. Second exists.
"""

    result = evaluator.evaluate_spec(spec, project_root=root)

    assert result["scope_result"] == "PASS"
    assert result["prose_stored_reconciliation"]["outer_ids"] == ["A1", "A2"]
    assert result["prose_stored_reconciliation"]["order_matches"] is True


def test_reordered_prose_and_stored_assertions_fail(evaluator, project):
    root, db = project
    spec = _insert(
        db,
        "DCL-RECONCILE-002",
        [
            {"id": "A1", "type": "file_exists", "file": "present.txt", "description": "Second exists."},
            {"id": "A2", "type": "file_exists", "file": "present.txt", "description": "First exists."},
        ],
    )
    spec["description"] = """## Required Executable Assertions

1. First exists.
2. Second exists.
"""

    result = evaluator.evaluate_spec(spec, project_root=root)

    assert result["scope_result"] == "FAIL"
    assert result["evaluation_reason"] == "prose-stored-reconciliation"


def test_historical_evidence_is_nonoperative_but_active_leakage_fails(evaluator):
    assert evaluator.classify_historical_evidence("fixtures/history/old-rule.md", active_loading_paths=set()) == {
        "classification": "KEEP",
        "reason": "historical-fixture",
    }
    assert evaluator.classify_historical_evidence("rules/current.md", active_loading_paths={"rules/current.md"}) == {
        "classification": "FAIL",
        "reason": "active-leakage",
    }
    assert evaluator.classify_historical_evidence("unclassified/old-rule.md", active_loading_paths=set()) == {
        "classification": "QUARANTINE",
        "reason": "historical-fixture",
    }


def test_partial_hard_invariant_blocks_every_governed_gate(evaluator):
    evaluation = {"carrier_result": "PARTIAL"}

    assert all(
        evaluator.satisfies_governed_gate(evaluation, gate, hard_invariant=True) is False
        for gate in ("implementation", "verification", "promotion", "closure")
    )
