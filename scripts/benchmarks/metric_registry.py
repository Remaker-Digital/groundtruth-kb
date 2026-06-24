"""Experimental effectiveness metric registry for GT-KB benchmark reports.

The registry is intentionally advisory: it explains how existing benchmark
values can inform owner-facing effectiveness questions without turning those
values into gates, SLOs, or release criteria.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

MetricStatus = Literal["experimental_advisory"]
ValueDirection = Literal["higher_is_better", "lower_is_better", "contextual"]


@dataclass(frozen=True)
class MetricDefinition:
    """One advisory effectiveness metric derived from an existing benchmark."""

    metric_id: str
    source_benchmark_id: str
    headline: str
    decision_informed: str
    interpretation: str
    guardrails: tuple[str, ...]
    known_failure_modes: tuple[str, ...]
    value_direction: ValueDirection
    status: MetricStatus = "experimental_advisory"

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["guardrails"] = list(self.guardrails)
        payload["known_failure_modes"] = list(self.known_failure_modes)
        return payload


METRIC_DEFINITIONS: tuple[MetricDefinition, ...] = (
    MetricDefinition(
        metric_id="advisory_acknowledgement_latency",
        source_benchmark_id="advisory_latency",
        headline="Median latency from advisory filing to first Prime acknowledgement.",
        decision_informed=(
            "Whether Loyal Opposition advisories are being routed quickly enough to avoid owner follow-up work."
        ),
        interpretation=(
            "Lower values suggest advisory intake is moving promptly; higher "
            "values identify routing or prioritization backlog pressure."
        ),
        guardrails=(
            "This is not an implementation-quality metric.",
            "Sparse advisory samples can make the median jumpy.",
            "A fast acknowledgement can still lead to a weak disposition.",
        ),
        known_failure_modes=(
            "Advisories without a machine-detectable acknowledgement appear as missing samples.",
            "Backfilled historical advisories can distort time-window comparisons.",
        ),
        value_direction="lower_is_better",
    ),
    MetricDefinition(
        metric_id="artifact_linkage_density",
        source_benchmark_id="linkage_heatmap",
        headline="Cross-artifact reference survival across governed surfaces.",
        decision_informed=(
            "Whether specs, work items, deliberations, bridge files, and related "
            "artifacts are linked enough for future sessions to recover context."
        ),
        interpretation=(
            "Higher values suggest better traceability; low values identify weak "
            "knowledge reuse and review-context risk."
        ),
        guardrails=(
            "High linkage density does not prove the links are semantically complete.",
            "A narrow time window may miss valid historical context.",
        ),
        known_failure_modes=(
            "References in generated summaries can inflate apparent linkage.",
            "Malformed or legacy IDs can be missed by the benchmark parser.",
        ),
        value_direction="higher_is_better",
    ),
    MetricDefinition(
        metric_id="assertion_signal_ratio",
        source_benchmark_id="assertion_signal_noise",
        headline="Fraction of categorized assertions outside chronic-noise status.",
        decision_informed=(
            "Whether architecture and governance assertions are producing useful "
            "signal rather than recurring owner/operator noise."
        ),
        interpretation=(
            "Higher values suggest assertion triage is preserving useful checks; "
            "lower values point toward retirement, repair, or categorization work."
        ),
        guardrails=(
            "Uncategorized assertions are outside this metric.",
            "A healthy ratio can hide one severe chronic-noise assertion.",
        ),
        known_failure_modes=(
            "Missing triage category files produce a zero-sample result.",
            "Stale category files can make current assertion health look better than it is.",
        ),
        value_direction="higher_is_better",
    ),
    MetricDefinition(
        metric_id="bridge_iteration_load",
        source_benchmark_id="versions_per_landed_change",
        headline="Average bridge versions filed per unique bridge thread.",
        decision_informed=("Whether proposal/report structure is causing repeated bridge churn before work lands."),
        interpretation=(
            "Lower values usually mean less avoidable revise/review churn; higher "
            "values call for better scaffolds, preflights, or narrower scope."
        ),
        guardrails=(
            "Complex work can legitimately require more versions.",
            "This metric does not distinguish productive design iteration from avoidable format churn.",
        ),
        known_failure_modes=(
            "File modification time is an approximation for window membership.",
            "Parked drafts and historical repairs can inflate iteration counts.",
        ),
        value_direction="lower_is_better",
    ),
)


def metric_definitions() -> tuple[MetricDefinition, ...]:
    """Return metric definitions in stable report order."""
    return METRIC_DEFINITIONS


def metric_definitions_by_source() -> dict[str, MetricDefinition]:
    """Return definitions keyed by source benchmark id."""
    return {definition.source_benchmark_id: definition for definition in METRIC_DEFINITIONS}


def registry_payload() -> list[dict[str, object]]:
    """Return a JSON-friendly registry snapshot."""
    return [definition.to_dict() for definition in METRIC_DEFINITIONS]
