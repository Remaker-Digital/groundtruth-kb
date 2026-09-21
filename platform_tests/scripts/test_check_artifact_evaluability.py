"""Behavioral tests for fail-closed change-controlled artifact evaluation."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_artifact_evaluability.py"

from groundtruth_kb.authority_client import AuthorityClient, configured_authority_client  # noqa: E402


@pytest.fixture
def evaluator():
    spec = importlib.util.spec_from_file_location("check_artifact_evaluability", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def project(tmp_path: Path, monkeypatch):
    (tmp_path / "present.txt").write_text("ready\n", encoding="utf-8")
    specs = {}
    monkeypatch.setenv("GT_AUTHORITY_URL", "http://127.0.0.1:12345")

    def refuse(*args, **kwargs):
        pytest.fail("Artifact evaluation must not open SQLite")

    monkeypatch.setattr("sqlite3.connect", refuse)

    def request(self, method, path, *, body=None, query=None):
        assert method == "GET" and body is None
        if path == "/v1/specifications":
            # Two or more records require paging, exercising the ordinary list route.
            ordered = sorted(specs)
            remaining = [key for key in ordered if not query.get("after") or key > query["after"]]
            page = remaining[:1]
            return {
                "records": [dict(specs[key]) for key in page],
                "next_after": page[-1] if len(remaining) > 1 else None,
            }
        assert path.startswith("/v1/specifications/")
        return dict(specs[path.rsplit("/", 1)[1]])

    monkeypatch.setattr(AuthorityClient, "request", request)
    return tmp_path, specs


def _insert(specs: dict, spec_id: str, assertions: list[dict]) -> dict:
    specs[spec_id] = {
        "id": spec_id,
        "title": spec_id,
        "type": "design_constraint",
        "status": "active",
        "version": 1,
        "assertions": assertions,
    }
    return specs[spec_id]


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
    before = json.dumps(db, sort_keys=True)
    files_before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

    report = evaluator.evaluate_specs(configured_authority_client(root), project_root=root, spec_ids=["DCL-EVAL-005"])

    after = json.dumps(db, sort_keys=True)
    assert report["aggregate_result"] == "PASS"
    assert before == after
    assert sorted(path.relative_to(root).as_posix() for path in root.rglob("*")) == files_before


def test_assertion_scope_requires_exactly_one_carrier(evaluator, project):
    root, db = project
    for spec_id in ("DCL-EVAL-006", "DCL-EVAL-007"):
        _insert(db, spec_id, [{"id": "A1", "type": "file_exists", "file": "present.txt"}])

    with pytest.raises(evaluator.EvaluationError, match="exactly one"):
        evaluator.evaluate_specs(
            configured_authority_client(root),
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


def test_cli_reads_all_native_pages_without_creating_local_state(evaluator, project, capsys):
    root, specs = project
    for ident in ("DCL-EVAL-PAGE1", "DCL-EVAL-PAGE2"):
        _insert(specs, ident, [{"id": "A1", "type": "file_exists", "file": "present.txt"}])
    before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
    assert evaluator.main(["--project-root", str(root), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["carrier_count"] == 2 and report["aggregate_result"] == "PASS"
    assert sorted(path.relative_to(root).as_posix() for path in root.rglob("*")) == before


def test_cli_native_outage_is_visible_without_sqlite_fallback(evaluator, project, monkeypatch, capsys):
    from groundtruth_kb.authority_client import AuthorityClientError

    root, _specs = project

    def unavailable(self, method, path, **kwargs):
        raise AuthorityClientError("authority_unavailable", "Selected authority unavailable")

    monkeypatch.setattr(AuthorityClient, "request", unavailable)
    assert evaluator.main(["--project-root", str(root), "--json"]) == 1
    assert "Selected authority unavailable" in capsys.readouterr().err
    assert not (root / "groundtruth.db").exists()
