"""Telemetry mapping for harness quality benchmark evidence.

The functions here are pure mappers. They do not persist TAFE stage attempts,
write benchmark result stores, call external services, or mutate live GT-KB
state.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from scripts.benchmarks import harness_quality_manifest as manifest

ADVISORY_ONLY = True
TELEMETRY_SCHEMA_VERSION = 1


def validate_telemetry_evidence(record: dict[str, Any]) -> dict[str, Any]:
    """Validate evidence before mapping it into telemetry shapes."""

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


def idempotency_key_for(record: dict[str, Any]) -> str:
    """Return a stable key for future telemetry persistence de-duplication."""

    validated = validate_telemetry_evidence(record)
    payload = {
        "run_id": validated["run_id"],
        "dispatch_envelope_id": validated["dispatch_envelope_id"],
        "fixture_id": validated["fixture_id"],
        "harness_id": validated["harness_id"],
        "benchmark_mode": validated["benchmark_mode"],
        "adaptation_id": validated["adaptation_id"],
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "bench-telemetry-" + hashlib.sha256(blob).hexdigest()[:24]


def _token_count(record: dict[str, Any]) -> int:
    return int(record["input_tokens"]) + int(record["output_tokens"])


def to_tafe_stage_attempt(record: dict[str, Any]) -> dict[str, Any]:
    """Map evidence into a TAFE stage-attempt-shaped dictionary."""

    validated = validate_telemetry_evidence(record)
    key = idempotency_key_for(validated)
    return {
        "schema_version": TELEMETRY_SCHEMA_VERSION,
        "idempotency_key": key,
        "stage_attempt_id": key,
        "run_id": validated["run_id"],
        "harness_id": validated["harness_id"],
        "benchmark_mode": validated["benchmark_mode"],
        "fixture_id": validated["fixture_id"],
        "started_at": validated["started_at"],
        "ended_at": validated["ended_at"],
        "duration_ms": validated["duration_ms"],
        "token_count": _token_count(validated),
        "cost": validated["estimated_cost"],
        "advisory_only": ADVISORY_ONLY,
        "metadata": {
            "provider": validated["provider"],
            "model": validated["model"],
            "author_model_configuration": validated["author_model_configuration"],
            "dispatch_envelope_id": validated["dispatch_envelope_id"],
            "run_tier": validated["run_tier"],
            "adaptation_id": validated["adaptation_id"],
            "adaptation_label": validated["adaptation_label"],
            "outcome": validated["outcome"],
            "verdict": validated["verdict"],
            "failure_class": validated["failure_class"],
        },
    }


def to_benchmark_result_record(record: dict[str, Any]) -> dict[str, Any]:
    """Map evidence into a benchmark result-store-shaped dictionary."""

    validated = validate_telemetry_evidence(record)
    key = idempotency_key_for(validated)
    return {
        "schema_version": TELEMETRY_SCHEMA_VERSION,
        "idempotency_key": key,
        "run_id": validated["run_id"],
        "harness_id": validated["harness_id"],
        "benchmark_mode": validated["benchmark_mode"],
        "fixture_id": validated["fixture_id"],
        "dispatch_envelope_id": validated["dispatch_envelope_id"],
        "run_tier": validated["run_tier"],
        "adaptation_id": validated["adaptation_id"],
        "adaptation_label": validated["adaptation_label"],
        "provider": validated["provider"],
        "model": validated["model"],
        "author_model_configuration": validated["author_model_configuration"],
        "failure_class": validated["failure_class"],
        "duration_ms": validated["duration_ms"],
        "input_tokens": validated["input_tokens"],
        "output_tokens": validated["output_tokens"],
        "token_count": _token_count(validated),
        "estimated_cost": validated["estimated_cost"],
        "deterministic_score": validated["deterministic_score"],
        "adjudication_score": validated["adjudication_score"],
        "outcome": validated["outcome"],
        "verdict": validated["verdict"],
        "required_source_citations": tuple(validated["required_source_citations"]),
        "artifact_links": tuple(validated["artifact_links"]),
        "advisory_only": ADVISORY_ONLY,
    }


def map_evidence_to_telemetry(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return both telemetry shapes without persisting either one."""

    return {
        "tafe_stage_attempt": to_tafe_stage_attempt(record),
        "benchmark_result": to_benchmark_result_record(record),
    }


__all__ = [
    "ADVISORY_ONLY",
    "TELEMETRY_SCHEMA_VERSION",
    "idempotency_key_for",
    "map_evidence_to_telemetry",
    "to_benchmark_result_record",
    "to_tafe_stage_attempt",
    "validate_telemetry_evidence",
]
