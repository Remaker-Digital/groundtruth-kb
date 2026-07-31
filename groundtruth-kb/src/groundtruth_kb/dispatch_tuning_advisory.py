"""Deterministic advisory-only dispatch tuning evaluation."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

SCHEMA_ID = "gtkb.dispatch_tuning_advisory.v1"
SCHEMA_VERSION = 1
OUTCOMES = frozenset({"recommend", "do_not_recommend", "insufficient_evidence"})
ISOLATION_MODES = frozenset({"offline", "synthetic", "benchmark", "shadow"})
MAX_FIXTURES = 50
MAX_FILTERS = 20
_EVIDENCE_KEYS = ("metrics_snapshot", "benchmark", "adaptation", "scoring_snapshot")
_DIRECTIONS = frozenset({"increase", "decrease", "not_increase", "not_decrease"})
_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_SAFE_TEXT_RE = re.compile(r"^[^\x00-\x1f\x7f]{1,240}$")


class ProductionActivationRefused(RuntimeError):
    """Raised because advisory evidence cannot activate production tuning."""


def _text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized if _SAFE_TEXT_RE.fullmatch(normalized) else None


def _number(value: Any, *, minimum: float | None = None) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    if minimum is not None and value < minimum:
        return None
    return value


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _timestamp(value: Any) -> str | None:
    text = _text(value)
    if text is None:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _immutable_ref(
    value: Any,
    *,
    require_approved: bool = False,
    required_schema: str | None = None,
) -> dict[str, Any] | None:
    raw = _mapping(value)
    reference_id = _text(raw.get("id"))
    digest = _text(raw.get("sha256"))
    if reference_id is None or digest is None or _DIGEST_RE.fullmatch(digest) is None:
        return None
    schema_id = _text(raw.get("schema_id"))
    if required_schema is not None and schema_id != required_schema:
        return None
    if require_approved and raw.get("approved") is not True:
        return None
    result: dict[str, Any] = {"id": reference_id, "sha256": digest}
    if schema_id is not None:
        result["schema_id"] = schema_id
    if require_approved:
        result["approved"] = True
    return result


def _safe_filters(value: Any) -> dict[str, str]:
    raw = _mapping(value)
    result: dict[str, str] = {}
    for key, item in sorted(raw.items(), key=lambda row: str(row[0])):
        if len(result) >= MAX_FILTERS:
            break
        safe_key = _text(key)
        safe_value = _text(item)
        if safe_key is not None and safe_value is not None:
            result[safe_key] = safe_value
    return result


def _metric(value: Any) -> dict[str, Any] | None:
    raw = _mapping(value)
    name = _text(raw.get("name"))
    baseline = _number(raw.get("baseline"))
    candidate = _number(raw.get("candidate"))
    direction = _text(raw.get("expected_direction"))
    minimum_delta = _number(raw.get("minimum_delta", 0), minimum=0)
    if name is None or baseline is None or candidate is None or direction not in _DIRECTIONS or minimum_delta is None:
        return None
    delta = candidate - baseline
    if direction == "increase":
        passed = delta >= minimum_delta
    elif direction == "decrease":
        passed = -delta >= minimum_delta
    elif direction == "not_increase":
        passed = delta <= minimum_delta
    else:
        passed = -delta <= minimum_delta
    return {
        "name": name,
        "baseline": baseline,
        "candidate": candidate,
        "delta": delta,
        "expected_direction": direction,
        "minimum_delta": minimum_delta,
        "passed": passed,
    }


def _metrics(value: Any) -> tuple[list[dict[str, Any]], bool]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return [], False
    rows = [_metric(item) for item in value]
    valid = bool(rows) and all(row is not None for row in rows)
    return sorted((row for row in rows if row is not None), key=lambda row: row["name"]), valid


def _cost(value: Any) -> dict[str, Any] | None:
    raw = _mapping(value)
    baseline = _number(raw.get("baseline"), minimum=0)
    candidate = _number(raw.get("candidate"), minimum=0)
    currency = _text(raw.get("currency"))
    if baseline is None or candidate is None or currency is None:
        return None
    return {"baseline": baseline, "candidate": candidate, "currency": currency, "delta": candidate - baseline}


def _canonical_payload(raw: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    blocking_reasons: list[str] = []
    hypothesis = _text(raw.get("hypothesis"))
    target_dimension = _text(raw.get("target_dimension"))
    mode = _text(raw.get("mode"))
    baseline = _immutable_ref(raw.get("baseline"))
    candidate = _immutable_ref(raw.get("candidate"))
    if hypothesis is None:
        blocking_reasons.append("hypothesis_missing_or_invalid")
    if target_dimension is None:
        blocking_reasons.append("target_dimension_missing_or_invalid")
    if mode not in ISOLATION_MODES:
        blocking_reasons.append("comparison_mode_not_isolated")
    if baseline is None or candidate is None:
        blocking_reasons.append("baseline_or_candidate_not_content_addressed")

    evidence_raw = _mapping(raw.get("evidence"))
    evidence: dict[str, Any] = {}
    for key in _EVIDENCE_KEYS:
        reference = _immutable_ref(
            evidence_raw.get(key),
            require_approved=key == "scoring_snapshot",
            required_schema="gtkb.dispatch_default_metrics_snapshot.v1" if key == "metrics_snapshot" else None,
        )
        if reference is None:
            blocking_reasons.append(f"{key}_missing_or_untraceable")
        else:
            evidence[key] = reference

    population_raw = _mapping(raw.get("population"))
    population_ref = _immutable_ref(population_raw)
    fixture_values = population_raw.get("fixture_ids")
    fixture_ids = []
    if isinstance(fixture_values, Sequence) and not isinstance(fixture_values, (str, bytes)):
        fixture_ids = sorted({_text(item) for item in fixture_values if _text(item) is not None})[:MAX_FIXTURES]
    if population_ref is None or not fixture_ids:
        blocking_reasons.append("population_missing_empty_or_untraceable")

    window_raw = _mapping(raw.get("source_window"))
    window_start = _timestamp(window_raw.get("start"))
    window_end = _timestamp(window_raw.get("end"))
    if window_start is None or window_end is None or window_start > window_end:
        blocking_reasons.append("source_window_invalid")

    sample_raw = _mapping(raw.get("sample_sufficiency"))
    observed = _number(sample_raw.get("observed"), minimum=0)
    minimum = _number(sample_raw.get("minimum"), minimum=1)
    if observed is None or minimum is None or observed < minimum:
        blocking_reasons.append("sample_insufficient")

    coverage_raw = _mapping(raw.get("coverage_requirement"))
    observed_ratio = _number(coverage_raw.get("observed_ratio"), minimum=0)
    minimum_ratio = _number(coverage_raw.get("minimum_ratio"), minimum=0)
    if (
        observed_ratio is None
        or minimum_ratio is None
        or observed_ratio > 1
        or minimum_ratio > 1
        or observed_ratio < minimum_ratio
    ):
        blocking_reasons.append("coverage_insufficient")

    freshness_status = _text(_mapping(raw.get("freshness")).get("status"))
    if freshness_status != "fresh":
        blocking_reasons.append("evidence_stale_or_freshness_unknown")

    quality, quality_valid = _metrics(raw.get("primary_quality_metrics"))
    guardrails, guardrails_valid = _metrics(raw.get("operational_guardrails"))
    failures, failures_valid = _metrics(raw.get("failure_metrics"))
    if not quality_valid:
        blocking_reasons.append("primary_quality_metrics_incomplete")
    if not guardrails_valid:
        blocking_reasons.append("operational_guardrails_incomplete")
    if not failures_valid:
        blocking_reasons.append("failure_metrics_incomplete")

    costs_raw = _mapping(raw.get("costs"))
    provider_cost = _cost(costs_raw.get("provider_reported"))
    benchmark_cost = _cost(costs_raw.get("benchmark_estimated"))
    if provider_cost is None or benchmark_cost is None:
        blocking_reasons.append("cost_labels_incomplete")

    declared: list[str] = []
    declared_limitations = raw.get("limitations")
    if isinstance(declared_limitations, Sequence) and not isinstance(declared_limitations, (str, bytes)):
        declared.extend(_text(item) for item in declared_limitations if _text(item) is not None)

    payload = {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "hypothesis": hypothesis,
        "target_dimension": target_dimension,
        "comparison": {
            "mode": mode if mode in ISOLATION_MODES else None,
            "baseline": baseline,
            "candidate": candidate,
            "population": {
                **(population_ref or {"id": None, "sha256": None}),
                "fixture_ids": fixture_ids,
                "record_count": len(fixture_ids),
            },
            "profile_filters": _safe_filters(raw.get("profile_filters")),
            "source_window": {"start": window_start, "end": window_end},
            "sample_sufficiency": {"observed": observed, "minimum": minimum},
            "coverage_requirement": {"observed_ratio": observed_ratio, "minimum_ratio": minimum_ratio},
        },
        "evidence": evidence,
        "measurements": {
            "primary_quality_metrics": quality,
            "operational_guardrails": guardrails,
            "failure_metrics": failures,
            "costs": {"provider_reported": provider_cost, "benchmark_estimated": benchmark_cost},
        },
        "freshness": {"status": freshness_status if freshness_status == "fresh" else "unavailable"},
        "coverage": {"observed_ratio": observed_ratio, "minimum_ratio": minimum_ratio},
        "uncertainty": {"method": "bounded_threshold_comparison"},
        "limitations": sorted(set(blocking_reasons + declared)),
        "insufficiency_reasons": sorted(set(blocking_reasons)),
        "privacy_classification": "allowlisted_observational_metadata",
        "advisory_only": True,
        "production_activation_allowed": False,
        "production_boundary": "separate_spec_pauth_go_and_fail_closed_activation_gate_required",
    }
    return payload, payload["insufficiency_reasons"]


def evaluate_dispatch_tuning(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Return one reproducible advisory without mutating any production state."""
    if not isinstance(raw, Mapping):
        raw = {}
    payload, limitations = _canonical_payload(raw)
    if limitations:
        outcome = "insufficient_evidence"
        rationale = "evidence_did_not_satisfy_required_contract"
    else:
        metric_groups = payload["measurements"]
        all_pass = all(
            row["passed"]
            for group in ("primary_quality_metrics", "operational_guardrails", "failure_metrics")
            for row in metric_groups[group]
        )
        outcome = "recommend" if all_pass else "do_not_recommend"
        rationale = "candidate_meets_quality_and_guardrails" if all_pass else "candidate_failed_quality_or_guardrail"
    payload["outcome"] = outcome
    payload["rationale"] = rationale
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    payload["advisory_id"] = f"dispatch-tuning-advisory-{digest[:24]}"
    return payload


def assert_production_activation_forbidden(*_args: Any, **_kwargs: Any) -> None:
    """Fail closed until a future complete production-activation authority chain exists."""
    raise ProductionActivationRefused(
        "dispatch tuning advisories cannot activate production; "
        "a separate specification, PAUTH, GO, and gate are required"
    )


__all__ = [
    "ISOLATION_MODES",
    "OUTCOMES",
    "ProductionActivationRefused",
    "SCHEMA_ID",
    "SCHEMA_VERSION",
    "assert_production_activation_forbidden",
    "evaluate_dispatch_tuning",
]
