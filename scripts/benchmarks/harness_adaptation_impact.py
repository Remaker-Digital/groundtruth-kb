"""Pure harness-adaptation impact measurement primitives.

The functions here compare paired benchmark evidence records for the same
harness, fixture, mode, and run tier. They are advisory-only and do not mutate
dispatcher eligibility, durable harness roles, bridge state, MemBase, or files.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

from scripts.benchmarks import harness_quality_manifest as manifest

ADVISORY_ONLY = True
IMPACT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class AdaptationIdentity:
    """Compact identity for one harness adaptation version."""

    adaptation_id: str
    harness_id: str
    label: str
    version: str
    metadata: tuple[tuple[str, str], ...]
    input_fingerprints: tuple[tuple[str, str], ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["metadata"] = dict(self.metadata)
        payload["input_fingerprints"] = dict(self.input_fingerprints)
        payload["raw_inputs_included"] = False
        return payload

    def evidence_fields(self) -> dict[str, str]:
        return {
            "adaptation_id": self.adaptation_id,
            "adaptation_label": self.label,
        }


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _require_nonblank(value: str, *, label: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{label} is required")
    return normalized


def _normalize_pairs(values: Mapping[str, Any] | None) -> tuple[tuple[str, str], ...]:
    if not values:
        return ()
    pairs = [(_require_nonblank(key, label="metadata key"), str(value)) for key, value in values.items()]
    return tuple(sorted(pairs))


def fingerprint_text(name: str, text: str) -> tuple[str, str]:
    """Return a stable fingerprint without retaining raw input text."""

    normalized_name = _require_nonblank(name, label="fingerprint name")
    digest = hashlib.sha256(str(text).encode("utf-8")).hexdigest()
    return normalized_name, f"sha256:{digest}"


def create_adaptation_identity(
    *,
    harness_id: str,
    label: str,
    version: str,
    metadata: Mapping[str, Any] | None = None,
    source_texts: Mapping[str, str] | None = None,
    source_fingerprints: Mapping[str, str] | None = None,
) -> AdaptationIdentity:
    """Create a stable, compact adaptation identity."""

    normalized_sources = dict(source_fingerprints or {})
    for source_name, source_text in (source_texts or {}).items():
        name, digest = fingerprint_text(source_name, source_text)
        normalized_sources[name] = digest
    fingerprints = tuple(sorted((str(key), str(value)) for key, value in normalized_sources.items()))
    payload = {
        "harness_id": _require_nonblank(harness_id, label="harness_id"),
        "label": _require_nonblank(label, label="label"),
        "version": _require_nonblank(version, label="version"),
        "metadata": _normalize_pairs(metadata),
        "input_fingerprints": fingerprints,
    }
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:16]
    return AdaptationIdentity(
        adaptation_id=f"adapt-{digest}",
        harness_id=payload["harness_id"],
        label=payload["label"],
        version=payload["version"],
        metadata=payload["metadata"],
        input_fingerprints=fingerprints,
    )


def validate_adaptation_evidence(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one manifest-complete evidence record with adaptation fields."""

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
    adaptation_id = _require_nonblank(str(record["adaptation_id"]), label="adaptation_id")
    adaptation_label = _require_nonblank(str(record["adaptation_label"]), label="adaptation_label")
    out = dict(record)
    out["adaptation_id"] = adaptation_id
    out["adaptation_label"] = adaptation_label
    return out


def _comparison_key(record: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(record["harness_id"]),
        str(record["benchmark_mode"]),
        str(record["fixture_id"]),
        str(record["run_tier"]),
    )


def _score_delta(candidate: Any, baseline: Any) -> float | None:
    if candidate is None or baseline is None:
        return None
    return round(float(candidate) - float(baseline), 6)


def _token_count(record: Mapping[str, Any]) -> int:
    return int(record["input_tokens"]) + int(record["output_tokens"])


def compute_adaptation_delta(
    baseline_record: Mapping[str, Any],
    candidate_record: Mapping[str, Any],
) -> dict[str, Any]:
    """Return an advisory before/after delta for one paired fixture record."""

    baseline = validate_adaptation_evidence(baseline_record)
    candidate = validate_adaptation_evidence(candidate_record)
    if _comparison_key(baseline) != _comparison_key(candidate):
        raise ValueError("baseline and candidate records must share harness, mode, fixture, and run tier")
    if baseline["adaptation_id"] == candidate["adaptation_id"]:
        raise ValueError("baseline and candidate adaptation_id values must differ")
    return {
        "harness_id": baseline["harness_id"],
        "benchmark_mode": baseline["benchmark_mode"],
        "fixture_id": baseline["fixture_id"],
        "run_tier": baseline["run_tier"],
        "baseline_adaptation_id": baseline["adaptation_id"],
        "baseline_adaptation_label": baseline["adaptation_label"],
        "candidate_adaptation_id": candidate["adaptation_id"],
        "candidate_adaptation_label": candidate["adaptation_label"],
        "deterministic_score_delta": _score_delta(
            candidate["deterministic_score"],
            baseline["deterministic_score"],
        ),
        "adjudication_score_delta": _score_delta(
            candidate["adjudication_score"],
            baseline["adjudication_score"],
        ),
        "token_delta": _token_count(candidate) - _token_count(baseline),
        "estimated_cost_delta": round(float(candidate["estimated_cost"]) - float(baseline["estimated_cost"]), 6),
        "duration_ms_delta": int(candidate["duration_ms"]) - int(baseline["duration_ms"]),
        "advisory_only": ADVISORY_ONLY,
    }


def compute_adaptation_deltas(
    baseline_records: Sequence[Mapping[str, Any]],
    candidate_records: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    """Compare equal baseline/candidate fixture sets in deterministic order."""

    baseline_index = {_comparison_key(validate_adaptation_evidence(record)): record for record in baseline_records}
    candidate_index = {_comparison_key(validate_adaptation_evidence(record)): record for record in candidate_records}
    if set(baseline_index) != set(candidate_index):
        missing_candidate = sorted(set(baseline_index) - set(candidate_index))
        missing_baseline = sorted(set(candidate_index) - set(baseline_index))
        raise ValueError(
            "baseline and candidate fixture sets differ: "
            f"missing_candidate={missing_candidate}; missing_baseline={missing_baseline}"
        )
    return tuple(compute_adaptation_delta(baseline_index[key], candidate_index[key]) for key in sorted(baseline_index))


def _average(values: Sequence[Any]) -> float | None:
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return None
    return round(sum(numeric) / len(numeric), 6)


def build_adaptation_impact_report(
    baseline_records: Sequence[Mapping[str, Any]],
    candidate_records: Sequence[Mapping[str, Any]],
    *,
    run_id: str,
    generated_at: str,
) -> dict[str, Any]:
    """Build a compact advisory report for paired adaptation deltas."""

    deltas = compute_adaptation_deltas(baseline_records, candidate_records)
    return {
        "schema_version": IMPACT_SCHEMA_VERSION,
        "report_type": "harness_adaptation_impact",
        "run_id": _require_nonblank(run_id, label="run_id"),
        "generated_at": _require_nonblank(generated_at, label="generated_at"),
        "advisory_only": ADVISORY_ONLY,
        "mutation_boundaries": {
            "membase_mutation": False,
            "bridge_mutation": False,
            "dispatcher_ranking_mutation": False,
            "harness_eligibility_mutation": False,
            "durable_role_assignment_mutation": False,
        },
        "deltas": list(deltas),
        "summary": {
            "pair_count": len(deltas),
            "harness_ids": sorted({str(delta["harness_id"]) for delta in deltas}),
            "baseline_adaptation_ids": sorted({str(delta["baseline_adaptation_id"]) for delta in deltas}),
            "candidate_adaptation_ids": sorted({str(delta["candidate_adaptation_id"]) for delta in deltas}),
            "average_deterministic_score_delta": _average([delta["deterministic_score_delta"] for delta in deltas]),
            "average_adjudication_score_delta": _average([delta["adjudication_score_delta"] for delta in deltas]),
            "token_delta": sum(int(delta["token_delta"]) for delta in deltas),
            "estimated_cost_delta": round(sum(float(delta["estimated_cost_delta"]) for delta in deltas), 6),
        },
    }


__all__ = [
    "ADVISORY_ONLY",
    "IMPACT_SCHEMA_VERSION",
    "AdaptationIdentity",
    "build_adaptation_impact_report",
    "compute_adaptation_delta",
    "compute_adaptation_deltas",
    "create_adaptation_identity",
    "fingerprint_text",
    "validate_adaptation_evidence",
]
