"""Deterministic scoring for harness quality benchmark evidence.

Scores are advisory benchmark artifacts only. This module does not call
external services, mutate live GT-KB state, or change dispatcher ranking or
harness eligibility.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from scripts.benchmarks import fixture_corpus
from scripts.benchmarks import harness_quality_manifest as manifest

ADJUDICATION_UNAVAILABLE = "unavailable"
ADVISORY_ONLY = True
NO_GO_VERDICT = "NO-GO"
DISPATCH_QUALITY_SNAPSHOT_SCHEMA_VERSION = 1
DEFAULT_DISPATCH_QUALITY_TTL_SECONDS = 24 * 60 * 60
BENCHMARK_MODE_TO_ROLE = {
    "prime_builder": "prime-builder",
    "loyal_opposition": "loyal-opposition",
}


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


def build_dispatch_quality_snapshot(
    records: Iterable[dict[str, Any]],
    *,
    fixtures: tuple[fixture_corpus.BenchmarkFixture, ...] | None = None,
    generated_at: str | None = None,
    ttl_seconds: int = DEFAULT_DISPATCH_QUALITY_TTL_SECONDS,
) -> dict[str, Any]:
    """Aggregate benchmark records into compact dispatcher quality inputs.

    Raw benchmark evidence remains advisory and outside the dispatcher. This
    snapshot is the governed handoff shape for WI-4791: it carries bounded,
    traceable per-harness/role quality numbers without embedding transcripts,
    fixture bodies, artifact links, or adjudication text.
    """

    captured_at = generated_at or _now_iso()
    expires_at = _expires_at(captured_at, ttl_seconds=ttl_seconds)
    loaded = fixtures if fixtures is not None else fixture_corpus.require_valid_fixture_corpus()
    groups: dict[tuple[str, str, str], list[tuple[dict[str, Any], DeterministicScore]]] = defaultdict(list)

    for record in records:
        validated = validate_scoring_evidence(dict(record))
        score = score_evidence_record(validated, fixtures=loaded)
        harness_id = str(validated["harness_id"]).strip()
        role = _role_for_benchmark_mode(str(validated["benchmark_mode"]))
        if not harness_id or not role:
            continue
        groups[(harness_id, role, "*")].append((validated, score))

    quality_inputs: list[dict[str, Any]] = []
    for (harness_id, role, activity_type), rows in sorted(groups.items()):
        qualities = [_quality_points(validated, score) for validated, score in rows]
        run_ids = sorted({str(validated["run_id"]) for validated, _score in rows})
        fixture_ids = sorted({str(validated["fixture_id"]) for validated, _score in rows})
        quality_inputs.append(
            {
                "harness_id": harness_id,
                "role": role,
                "activity_type": activity_type,
                "dispatch_quality": round(sum(qualities) / len(qualities), 6),
                "status": "fresh",
                "captured_at": captured_at,
                "expires_at": expires_at,
                "record_count": len(rows),
                "fixture_count": len(fixture_ids),
                "run_count": len(run_ids),
                "evidence_ref": _evidence_ref(harness_id, role, activity_type, run_ids, fixture_ids),
            }
        )

    return {
        "schema_version": DISPATCH_QUALITY_SNAPSHOT_SCHEMA_VERSION,
        "snapshot_type": "dispatch_quality_inputs",
        "generated_at": captured_at,
        "quality_input_authorized": True,
        "raw_scores_advisory_only": ADVISORY_ONLY,
        "freshness": {
            "status": "fresh",
            "ttl_seconds": ttl_seconds,
            "expires_at": expires_at,
        },
        "quality_inputs": quality_inputs,
        "runtime_suppression": {
            "raw_evidence_omitted": True,
            "fixture_payloads_omitted": True,
            "artifact_links_omitted": True,
        },
    }


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _expires_at(captured_at: str, *, ttl_seconds: int) -> str | None:
    if ttl_seconds <= 0:
        return captured_at
    try:
        parsed = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return (
        (parsed.astimezone(UTC) + timedelta(seconds=ttl_seconds))
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _role_for_benchmark_mode(mode: str) -> str:
    normalized = mode.strip().lower().replace("-", "_")
    return BENCHMARK_MODE_TO_ROLE.get(normalized, normalized.replace("_", "-"))


def _optional_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _quality_points(validated: dict[str, Any], score: DeterministicScore) -> float:
    components = [score.deterministic_score]
    adjudication = _optional_float(validated.get("adjudication_score"))
    if adjudication is not None:
        components.append(max(0.0, min(1.0, adjudication)))
    quality = sum(components) / len(components)
    return round(max(0.0, min(100.0, quality * 100.0)), 6)


def _evidence_ref(
    harness_id: str,
    role: str,
    activity_type: str,
    run_ids: list[str],
    fixture_ids: list[str],
) -> str:
    payload = "|".join((harness_id, role, activity_type, ",".join(run_ids), ",".join(fixture_ids)))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"benchmark-quality:{harness_id}:{role}:{activity_type}:{digest}"


__all__ = [
    "ADJUDICATION_UNAVAILABLE",
    "ADVISORY_ONLY",
    "DEFAULT_DISPATCH_QUALITY_TTL_SECONDS",
    "DISPATCH_QUALITY_SNAPSHOT_SCHEMA_VERSION",
    "NO_GO_VERDICT",
    "DeterministicScore",
    "build_dispatch_quality_snapshot",
    "reviewer_rigor_no_go_rate",
    "score_evidence_record",
    "score_evidence_records",
    "validate_scoring_evidence",
]
