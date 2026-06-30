"""Deterministic scoring for harness quality benchmark evidence.

Scores are advisory benchmark artifacts only. This module does not call
external services, mutate live GT-KB state, or change dispatcher ranking or
harness eligibility.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from scripts.benchmarks import fixture_corpus
from scripts.benchmarks import harness_quality_manifest as manifest

ADJUDICATION_UNAVAILABLE = "unavailable"
ADVISORY_ONLY = True
NO_GO_VERDICT = "NO-GO"


@dataclass(frozen=True)
class DeterministicScore:
    """Advisory deterministic score for one benchmark evidence record."""

    fixture_id: str
    deterministic_score: float
    adjudication_score: float | None
    adjudication_status: str
    advisory_only: bool
    failure_class: str
    expected_failure_classes: tuple[str, ...]
    metrics: dict[str, float | int | bool]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_scoring_evidence(record: dict[str, Any]) -> dict[str, Any]:
    """Validate manifest field coverage and failure-class vocabulary."""

    expected_fields = set(manifest.REQUIRED_EVIDENCE_FIELDS)
    observed_fields = set(record)
    missing = expected_fields - observed_fields
    extra = observed_fields - expected_fields
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append(f"missing evidence fields: {sorted(missing)}")
        if extra:
            details.append(f"unknown evidence fields: {sorted(extra)}")
        raise ValueError("; ".join(details))

    failure_class = str(record["failure_class"])
    if failure_class not in set(manifest.FAILURE_CLASSES):
        raise ValueError(f"unknown failure_class: {failure_class!r}")
    if not record["author_model_configuration"]:
        raise ValueError("author_model_configuration is required")
    return record


def _fixture_by_id(fixtures: tuple[fixture_corpus.BenchmarkFixture, ...]) -> dict[str, fixture_corpus.BenchmarkFixture]:
    return {fixture.fixture_id: fixture for fixture in fixtures}


def _bool_score(value: bool) -> float:
    return 1.0 if value else 0.0


def score_evidence_record(
    record: dict[str, Any],
    *,
    fixtures: tuple[fixture_corpus.BenchmarkFixture, ...] | None = None,
) -> DeterministicScore:
    """Return a reproducible advisory deterministic score for one record."""

    validated = validate_scoring_evidence(record)
    loaded = fixtures if fixtures is not None else fixture_corpus.require_valid_fixture_corpus()
    fixture = _fixture_by_id(loaded).get(str(validated["fixture_id"]))
    if fixture is None:
        raise ValueError(f"unknown fixture_id: {validated['fixture_id']!r}")

    failure_class = str(validated["failure_class"])
    failure_class_match = failure_class in set(fixture.failure_classes)
    fixture_match = validated["fixture_id"] == fixture.fixture_id
    citations_present = bool(validated["required_source_citations"])
    dry_or_terminal_outcome = bool(validated["outcome"])
    verdict_present = bool(validated["verdict"])
    deterministic_checks = (
        fixture_match,
        failure_class_match,
        citations_present,
        dry_or_terminal_outcome,
        verdict_present,
    )
    deterministic_score = sum(_bool_score(check) for check in deterministic_checks) / len(deterministic_checks)
    metrics: dict[str, float | int | bool] = {
        "fixture_match": fixture_match,
        "failure_class_match": failure_class_match,
        "required_source_citations_present": citations_present,
        "outcome_present": dry_or_terminal_outcome,
        "verdict_present": verdict_present,
    }
    return DeterministicScore(
        fixture_id=fixture.fixture_id,
        deterministic_score=deterministic_score,
        adjudication_score=None,
        adjudication_status=ADJUDICATION_UNAVAILABLE,
        advisory_only=ADVISORY_ONLY,
        failure_class=failure_class,
        expected_failure_classes=fixture.failure_classes,
        metrics=metrics,
    )


def reviewer_rigor_no_go_rate(
    records: tuple[dict[str, Any], ...],
    *,
    fixtures: tuple[fixture_corpus.BenchmarkFixture, ...] | None = None,
) -> dict[str, float | int]:
    """Return NO-GO rate on seeded-defect LO benchmark records."""

    loaded = fixtures if fixtures is not None else fixture_corpus.require_valid_fixture_corpus()
    seeded_fixture_ids = {fixture.fixture_id for fixture in loaded if fixture.failure_classes}
    eligible: list[dict[str, Any]] = []
    for record in records:
        validated = validate_scoring_evidence(record)
        if validated["benchmark_mode"] == "loyal_opposition" and validated["fixture_id"] in seeded_fixture_ids:
            eligible.append(validated)

    no_go_count = sum(1 for record in eligible if str(record["verdict"]).upper() == NO_GO_VERDICT)
    total = len(eligible)
    return {
        "eligible_seeded_defect_count": total,
        "no_go_count": no_go_count,
        "no_go_rate": (no_go_count / total) if total else 0.0,
    }


def score_evidence_records(
    records: tuple[dict[str, Any], ...],
    *,
    fixtures: tuple[fixture_corpus.BenchmarkFixture, ...] | None = None,
) -> dict[str, Any]:
    """Score records and include the advisory reviewer-rigor metric."""

    loaded = fixtures if fixtures is not None else fixture_corpus.require_valid_fixture_corpus()
    scores = tuple(score_evidence_record(record, fixtures=loaded) for record in records)
    return {
        "advisory_only": ADVISORY_ONLY,
        "adjudication_status": ADJUDICATION_UNAVAILABLE,
        "scores": [score.to_dict() for score in scores],
        "reviewer_rigor": reviewer_rigor_no_go_rate(records, fixtures=loaded),
    }


__all__ = [
    "ADJUDICATION_UNAVAILABLE",
    "ADVISORY_ONLY",
    "NO_GO_VERDICT",
    "DeterministicScore",
    "reviewer_rigor_no_go_rate",
    "score_evidence_record",
    "score_evidence_records",
    "validate_scoring_evidence",
]
