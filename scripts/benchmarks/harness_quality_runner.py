"""Read-only harness quality benchmark runner primitives.

This module builds manifest-complete synthetic evidence records from the
fixture corpus. It intentionally does not call live harnesses, dispatchers,
MemBase, bridge writers, or external services.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from scripts.benchmarks import fixture_corpus
from scripts.benchmarks import harness_quality_manifest as manifest
from scripts.benchmarks.benchmark_dispatch_envelope import (
    BenchmarkDispatchEnvelope,
    create_benchmark_dispatch_envelope,
    require_benchmark_mode,
    require_run_tier,
)

DEFAULT_PROVIDER = "synthetic"
DEFAULT_MODEL = "fixture-harness"
DEFAULT_MODEL_CONFIGURATION = "synthetic benchmark dry-run"
DEFAULT_RUN_TIER = "smoke"
DRY_RUN_OUTCOME = "dry_run"
UNSCORED_SENTINEL = "unscored"


@dataclass(frozen=True)
class BenchmarkHarnessTarget:
    """Harness identity and model context used for synthetic benchmark records."""

    harness_id: str
    provider: str = DEFAULT_PROVIDER
    model: str = DEFAULT_MODEL
    author_model_configuration: str = DEFAULT_MODEL_CONFIGURATION


def _require_failure_class(failure_class: str) -> str:
    normalized = failure_class.strip()
    if normalized not in set(manifest.FAILURE_CLASSES):
        raise ValueError(f"unknown failure_class: {failure_class!r}")
    return normalized


def _require_nonnegative_int(value: int, *, label: str) -> int:
    if value < 0:
        raise ValueError(f"{label} must be non-negative")
    return value


def _require_nonnegative_float(value: float, *, label: str) -> float:
    if value < 0:
        raise ValueError(f"{label} must be non-negative")
    return value


def _evidence_field_set() -> set[str]:
    return set(manifest.REQUIRED_EVIDENCE_FIELDS)


def validate_evidence_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return ``record`` if it exactly satisfies the manifest evidence schema."""

    fields = _evidence_field_set()
    observed = set(record)
    missing = fields - observed
    extra = observed - fields
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append(f"missing evidence fields: {sorted(missing)}")
        if extra:
            details.append(f"unknown evidence fields: {sorted(extra)}")
        raise ValueError("; ".join(details))
    _require_failure_class(str(record["failure_class"]))
    return record


def build_evidence_record(
    *,
    envelope: BenchmarkDispatchEnvelope,
    fixture: fixture_corpus.BenchmarkFixture,
    started_at: str,
    ended_at: str,
    duration_ms: int = 0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    estimated_cost: float = 0.0,
    deterministic_score: float | None = None,
    adjudication_score: float | None = None,
    outcome: str = DRY_RUN_OUTCOME,
    verdict: str = UNSCORED_SENTINEL,
    failure_class: str = UNSCORED_SENTINEL,
    required_source_citations: Sequence[str] | None = None,
    artifact_links: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Build one manifest-complete benchmark evidence record."""

    record = {
        "run_id": envelope.run_id,
        "harness_id": envelope.harness_id,
        "benchmark_mode": envelope.benchmark_mode,
        "provider": envelope.provider,
        "model": envelope.model,
        "author_model_configuration": envelope.author_model_configuration,
        "dispatch_envelope_id": envelope.dispatch_envelope_id,
        "fixture_id": fixture.fixture_id,
        "run_tier": envelope.run_tier,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_ms": _require_nonnegative_int(duration_ms, label="duration_ms"),
        "input_tokens": _require_nonnegative_int(input_tokens, label="input_tokens"),
        "output_tokens": _require_nonnegative_int(output_tokens, label="output_tokens"),
        "estimated_cost": _require_nonnegative_float(estimated_cost, label="estimated_cost"),
        "deterministic_score": deterministic_score,
        "adjudication_score": adjudication_score,
        "outcome": outcome,
        "verdict": verdict,
        "failure_class": _require_failure_class(failure_class),
        "required_source_citations": tuple(required_source_citations or fixture.source_artifact_refs),
        "artifact_links": tuple(artifact_links or (fixture.fixture_root,)),
    }
    return validate_evidence_record(record)


def enumerate_benchmark_envelopes(
    *,
    run_id: str,
    harness_targets: Sequence[BenchmarkHarnessTarget],
    benchmark_mode: str,
    run_tier: str = DEFAULT_RUN_TIER,
    fixtures: Iterable[fixture_corpus.BenchmarkFixture] | None = None,
) -> tuple[BenchmarkDispatchEnvelope, ...]:
    """Return synthetic envelopes for every harness/fixture pair."""

    require_benchmark_mode(benchmark_mode)
    require_run_tier(run_tier)
    loaded = tuple(fixtures) if fixtures is not None else fixture_corpus.require_valid_fixture_corpus()
    envelopes: list[BenchmarkDispatchEnvelope] = []
    for target in harness_targets:
        for fixture in loaded:
            envelopes.append(
                create_benchmark_dispatch_envelope(
                    run_id=run_id,
                    harness_id=target.harness_id,
                    benchmark_mode=benchmark_mode,
                    provider=target.provider,
                    model=target.model,
                    author_model_configuration=target.author_model_configuration,
                    run_tier=run_tier,
                    fixture_id=fixture.fixture_id,
                )
            )
    return tuple(envelopes)


def build_dry_run_evidence_records(
    *,
    run_id: str,
    harness_targets: Sequence[BenchmarkHarnessTarget],
    benchmark_mode: str,
    started_at: str,
    ended_at: str,
    run_tier: str = DEFAULT_RUN_TIER,
    fixtures: Iterable[fixture_corpus.BenchmarkFixture] | None = None,
) -> tuple[dict[str, Any], ...]:
    """Build manifest-complete evidence records without live dispatch."""

    loaded = tuple(fixtures) if fixtures is not None else fixture_corpus.require_valid_fixture_corpus()
    fixtures_by_id = {fixture.fixture_id: fixture for fixture in loaded}
    records: list[dict[str, Any]] = []
    for envelope in enumerate_benchmark_envelopes(
        run_id=run_id,
        harness_targets=harness_targets,
        benchmark_mode=benchmark_mode,
        run_tier=run_tier,
        fixtures=loaded,
    ):
        records.append(
            build_evidence_record(
                envelope=envelope,
                fixture=fixtures_by_id[envelope.fixture_id],
                started_at=started_at,
                ended_at=ended_at,
            )
        )
    return tuple(records)


def record_to_dict(record: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-friendly copy of a validated evidence record."""

    validated = validate_evidence_record(record)
    return {key: list(value) if isinstance(value, tuple) else value for key, value in validated.items()}


__all__ = [
    "DEFAULT_MODEL",
    "DEFAULT_MODEL_CONFIGURATION",
    "DEFAULT_PROVIDER",
    "DEFAULT_RUN_TIER",
    "DRY_RUN_OUTCOME",
    "UNSCORED_SENTINEL",
    "BenchmarkHarnessTarget",
    "build_dry_run_evidence_records",
    "build_evidence_record",
    "enumerate_benchmark_envelopes",
    "record_to_dict",
    "validate_evidence_record",
]
