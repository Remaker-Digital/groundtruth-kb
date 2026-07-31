from __future__ import annotations

import ast

import pytest

from scripts.benchmarks import fixture_corpus
from scripts.benchmarks import harness_quality_runner as runner
from scripts.benchmarks import harness_quality_scoring as scoring


def _fixtures() -> tuple[fixture_corpus.BenchmarkFixture, ...]:
    return fixture_corpus.require_valid_fixture_corpus()


def _record(
    fixture: fixture_corpus.BenchmarkFixture,
    *,
    benchmark_mode: str = "prime_builder",
    failure_class: str | None = None,
    verdict: str = "unscored",
) -> dict[str, object]:
    target = runner.BenchmarkHarnessTarget(
        harness_id="A",
        provider="codex",
        model="gpt-5-codex",
        author_model_configuration="codex desktop synthetic benchmark",
    )
    record = runner.build_dry_run_evidence_records(
        run_id="run-scoring",
        harness_targets=(target,),
        benchmark_mode=benchmark_mode,
        started_at="2026-06-30T08:00:00Z",
        ended_at="2026-06-30T08:00:01Z",
        fixtures=(fixture,),
    )[0]
    record = dict(record)
    record["failure_class"] = failure_class or fixture.failure_classes[0]
    record["verdict"] = verdict
    return record


def test_score_is_deterministic_for_fixed_evidence_and_answer_key() -> None:
    fixture = _fixtures()[0]
    record = _record(fixture)

    first = scoring.score_evidence_record(record, fixtures=(fixture,))
    second = scoring.score_evidence_record(record, fixtures=(fixture,))

    assert first == second
    assert first.deterministic_score == 1.0
    assert first.adjudication_score is None
    assert first.advisory_only is True


def test_scoring_rejects_missing_manifest_field() -> None:
    fixture = _fixtures()[0]
    record = _record(fixture)
    record.pop("author_model_configuration")

    with pytest.raises(ValueError, match="missing evidence fields"):
        scoring.score_evidence_record(record, fixtures=(fixture,))


def test_scoring_rejects_unknown_failure_class() -> None:
    fixture = _fixtures()[0]
    record = _record(fixture, failure_class="not-a-real-class")

    with pytest.raises(ValueError, match="unknown failure_class"):
        scoring.score_evidence_record(record, fixtures=(fixture,))


def test_wrong_failure_class_reduces_score_without_mutating_record() -> None:
    fixture = _fixtures()[0]
    record = _record(fixture, failure_class="unscored")

    score = scoring.score_evidence_record(record, fixtures=(fixture,))

    assert score.metrics["failure_class_match"] is False
    assert 0.0 < score.deterministic_score < 1.0
    assert record["failure_class"] == "unscored"


def test_reviewer_rigor_metric_counts_no_go_on_seeded_defects() -> None:
    fixtures = _fixtures()[:2]
    records = (
        _record(fixtures[0], benchmark_mode="loyal_opposition", verdict="NO-GO"),
        _record(fixtures[1], benchmark_mode="loyal_opposition", verdict="GO"),
    )

    metric = scoring.reviewer_rigor_no_go_rate(records, fixtures=fixtures)

    assert metric == {
        "eligible_seeded_defect_count": 2,
        "no_go_count": 1,
        "no_go_rate": 0.5,
    }


def test_score_payload_is_advisory_only_with_adjudication_seam() -> None:
    fixture = _fixtures()[0]
    payload = scoring.score_evidence_records((_record(fixture),), fixtures=(fixture,))

    assert payload["advisory_only"] is True
    assert payload["adjudication_status"] == scoring.ADJUDICATION_UNAVAILABLE
    assert payload["scores"][0]["adjudication_score"] is None
    assert "reviewer_rigor" in payload


def test_scoring_imports_no_live_mutating_surface() -> None:
    module_path = fixture_corpus.PROJECT_ROOT / "scripts/benchmarks/harness_quality_scoring.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    call_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                call_names.add(node.func.attr)
            elif isinstance(node.func, ast.Name):
                call_names.add(node.func.id)

    assert all(not module.startswith("groundtruth_kb.") for module in imported_modules)
    assert not {"write_text", "open", "run", "Popen"} & call_names
