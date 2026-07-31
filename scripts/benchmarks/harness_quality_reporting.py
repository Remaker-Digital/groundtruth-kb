"""Advisory cadence reporting for harness quality benchmark evidence.

The builders in this module are pure: they summarize supplied benchmark
payloads and return JSON-friendly dictionaries. They do not write files,
mutate MemBase, alter bridge state, or change dispatcher ranking or harness
eligibility.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

from scripts.benchmarks import harness_quality_manifest as manifest

ADVISORY_ONLY = True
REPORT_SCHEMA_VERSION = 1
UNSCORED_FAILURE_CLASS = "unscored"


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _payload_records(payload: Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(payload, Sequence) and not isinstance(payload, str | bytes | bytearray):
        return [_as_mapping(item) for item in payload]

    candidates = []
    if isinstance(payload, Mapping):
        for key in ("evidence_records", "records", "results"):
            value = payload.get(key)
            if isinstance(value, list | tuple):
                candidates = value
                break
    records = [_as_mapping(item) for item in candidates]
    required = set(manifest.REQUIRED_EVIDENCE_FIELDS)
    return [record for record in records if required <= set(record)]


def _score_rows(scoring_payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    payload = _as_mapping(scoring_payload)
    if isinstance(payload.get("scoring"), Mapping):
        payload = dict(payload["scoring"])
    rows = payload.get("scores", ())
    if not isinstance(rows, list | tuple):
        return []
    return [_as_mapping(row) for row in rows]


def _record_with_score(record: dict[str, Any], score_index: Mapping[str, dict[str, Any]]) -> dict[str, Any]:
    enriched = dict(record)
    score = score_index.get(str(record.get("fixture_id") or ""))
    if score:
        if enriched.get("deterministic_score") is None:
            enriched["deterministic_score"] = score.get("deterministic_score")
        if enriched.get("adjudication_score") is None:
            enriched["adjudication_score"] = score.get("adjudication_score")
    return enriched


def _telemetry_rows(payload: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None) -> list[dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, Sequence) and not isinstance(payload, str | bytes | bytearray):
        values: Iterable[Any] = payload
    elif isinstance(payload, Mapping):
        values = payload.get("telemetry_records") or payload.get("benchmark_results") or payload.get("records") or ()
    else:
        values = ()
    rows: list[dict[str, Any]] = []
    for item in values:
        row = _as_mapping(item)
        if "benchmark_result" in row and isinstance(row["benchmark_result"], Mapping):
            row = dict(row["benchmark_result"])
        if row:
            rows.append(row)
    return rows


def _counter(records: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(record.get(field) or "unknown") for record in records).items()))


def _average(values: Iterable[Any]) -> float | None:
    numeric: list[float] = []
    for value in values:
        if value is None:
            continue
        try:
            numeric.append(float(value))
        except (TypeError, ValueError):
            continue
    if not numeric:
        return None
    return round(sum(numeric) / len(numeric), 6)


def _sum_numeric(records: Sequence[Mapping[str, Any]], field: str) -> float:
    total = 0.0
    for record in records:
        try:
            total += float(record.get(field) or 0)
        except (TypeError, ValueError):
            continue
    return round(total, 6)


def _tier_summary(
    tier: manifest.RunTier,
    records: Sequence[Mapping[str, Any]],
    telemetry_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    tier_records = [record for record in records if record.get("run_tier") == tier.id]
    tier_telemetry = [record for record in telemetry_records if record.get("run_tier") == tier.id]
    return {
        "tier_id": tier.id,
        "title": tier.title,
        "cadence": tier.cadence,
        "expected_cost_profile": tier.expected_cost_profile,
        "includes_adjudication": tier.includes_adjudication,
        "record_count": len(tier_records),
        "telemetry_record_count": len(tier_telemetry),
        "harness_count": len({str(record.get("harness_id")) for record in tier_records if record.get("harness_id")}),
        "fixture_count": len({str(record.get("fixture_id")) for record in tier_records if record.get("fixture_id")}),
        "adaptation_count": len(
            {str(record.get("adaptation_id")) for record in tier_records if record.get("adaptation_id")}
        ),
        "adaptation_ids": sorted(
            {str(record.get("adaptation_id")) for record in tier_records if record.get("adaptation_id")}
        ),
        "benchmark_modes": sorted(
            {str(record.get("benchmark_mode")) for record in tier_records if record.get("benchmark_mode")}
        ),
        "outcomes": _counter(tier_records, "outcome"),
        "verdicts": _counter(tier_records, "verdict"),
        "failure_classes": _counter(tier_records, "failure_class"),
        "average_deterministic_score": _average(record.get("deterministic_score") for record in tier_records),
        "average_adjudication_score": _average(record.get("adjudication_score") for record in tier_records),
        "total_tokens": int(_sum_numeric(tier_records, "input_tokens") + _sum_numeric(tier_records, "output_tokens")),
        "estimated_cost": _sum_numeric(tier_records, "estimated_cost"),
        "duration_ms": int(_sum_numeric(tier_records, "duration_ms")),
    }


def _trend(current: Mapping[str, Any], previous: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if previous is None:
        return None
    fields = (
        "record_count",
        "average_deterministic_score",
        "average_adjudication_score",
        "total_tokens",
        "estimated_cost",
        "duration_ms",
    )
    result: dict[str, Any] = {"tier_id": current["tier_id"]}
    for field in fields:
        current_value = current.get(field)
        previous_value = previous.get(field)
        if current_value is None or previous_value is None:
            result[f"{field}_delta"] = None
            continue
        result[f"{field}_delta"] = round(float(current_value) - float(previous_value), 6)
    current_failures = sum(
        count
        for failure_class, count in current.get("failure_classes", {}).items()
        if failure_class != UNSCORED_FAILURE_CLASS
    )
    previous_failures = sum(
        count
        for failure_class, count in previous.get("failure_classes", {}).items()
        if failure_class != UNSCORED_FAILURE_CLASS
    )
    result["seeded_failure_delta"] = current_failures - previous_failures
    return result


def _remediation_suggestions(tier_summaries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    suggestions: list[dict[str, Any]] = []
    for summary in tier_summaries:
        tier_id = str(summary["tier_id"])
        if summary["record_count"] == 0:
            suggestions.append(
                {
                    "kind": "coverage_gap",
                    "tier_id": tier_id,
                    "title": f"Add {tier_id} harness benchmark evidence",
                    "candidate_work_item_title": f"Add {tier_id} benchmark run coverage",
                    "candidate_bridge_topic": f"gtkb-harness-benchmark-{tier_id}-coverage",
                    "advisory_only": ADVISORY_ONLY,
                }
            )
        if (
            summary["includes_adjudication"]
            and summary["record_count"]
            and summary["average_adjudication_score"] is None
        ):
            suggestions.append(
                {
                    "kind": "adjudication_gap",
                    "tier_id": tier_id,
                    "title": "Capture adjudication scores for calibration runs",
                    "candidate_work_item_title": "Add adjudicated calibration score capture",
                    "candidate_bridge_topic": "gtkb-harness-benchmark-adjudication-score-capture",
                    "advisory_only": ADVISORY_ONLY,
                }
            )
        for failure_class, count in summary.get("failure_classes", {}).items():
            if failure_class == UNSCORED_FAILURE_CLASS or count <= 0:
                continue
            suggestions.append(
                {
                    "kind": "seeded_failure_signal",
                    "tier_id": tier_id,
                    "failure_class": failure_class,
                    "title": f"Investigate {failure_class} benchmark failures",
                    "candidate_work_item_title": f"Reduce {failure_class} harness benchmark failures",
                    "candidate_bridge_topic": f"gtkb-harness-benchmark-{failure_class}-remediation",
                    "count": count,
                    "advisory_only": ADVISORY_ONLY,
                }
            )
    return suggestions


def build_cadence_report(
    current_payload: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    *,
    previous_payload: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
    scoring_payload: Mapping[str, Any] | None = None,
    telemetry_payload: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic advisory cadence report from benchmark payloads."""

    score_index = {str(row.get("fixture_id") or ""): row for row in _score_rows(scoring_payload)}
    current_records = [_record_with_score(record, score_index) for record in _payload_records(current_payload)]
    previous_records = _payload_records(previous_payload or {})
    telemetry_records = _telemetry_rows(telemetry_payload)
    current = _as_mapping(current_payload)
    run_id = str(current.get("run_id") or (current_records[0].get("run_id") if current_records else "unknown"))

    tier_summaries = [
        _tier_summary(tier, current_records, telemetry_records) for tier in manifest.HARNESS_QUALITY_MANIFEST.tiers
    ]
    previous_summaries = {
        summary["tier_id"]: summary
        for summary in (_tier_summary(tier, previous_records, ()) for tier in manifest.HARNESS_QUALITY_MANIFEST.tiers)
    }
    trends = [
        trend
        for trend in (_trend(summary, previous_summaries.get(summary["tier_id"])) for summary in tier_summaries)
        if trend is not None
    ]
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_type": "harness_quality_cadence",
        "run_id": run_id,
        "generated_at": generated_at or _now_iso(),
        "advisory_only": ADVISORY_ONLY,
        "mutation_boundaries": {
            "membase_mutation": False,
            "bridge_mutation": False,
            "dispatcher_ranking_mutation": False,
            "harness_eligibility_mutation": False,
        },
        "tiers": tier_summaries,
        "trends": trends,
        "remediation_suggestions": _remediation_suggestions(tier_summaries),
        "summary": {
            "record_count": len(current_records),
            "telemetry_record_count": len(telemetry_records),
            "tier_count": len(tier_summaries),
            "adaptation_count": len(
                {str(record.get("adaptation_id")) for record in current_records if record.get("adaptation_id")}
            ),
            "suggestion_count": len(_remediation_suggestions(tier_summaries)),
        },
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render a cadence report as compact markdown."""

    lines = [
        f"# Harness quality cadence report {report.get('run_id', 'unknown')}",
        "",
        f"- generated_at: `{report.get('generated_at', 'unknown')}`",
        f"- advisory_only: `{str(report.get('advisory_only')).lower()}`",
        "",
        "## Tier Summary",
        "",
        "| Tier | Records | Harnesses | Fixtures | Adaptations | Avg deterministic | Avg adjudication | Cost |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for tier in report.get("tiers", ()):
        deterministic = tier.get("average_deterministic_score")
        adjudication = tier.get("average_adjudication_score")
        lines.append(
            "| `{tier}` | {records} | {harnesses} | {fixtures} | {adaptations} | {det} | {adj} | {cost} |".format(
                tier=tier.get("tier_id"),
                records=tier.get("record_count"),
                harnesses=tier.get("harness_count"),
                fixtures=tier.get("fixture_count"),
                adaptations=tier.get("adaptation_count"),
                det="-" if deterministic is None else deterministic,
                adj="-" if adjudication is None else adjudication,
                cost=tier.get("estimated_cost"),
            )
        )
    lines.extend(["", "## Advisory Suggestions", ""])
    suggestions = report.get("remediation_suggestions", ())
    if not suggestions:
        lines.append("No advisory remediation suggestions.")
    else:
        for item in suggestions:
            lines.append(
                "- `{kind}` `{tier}`: {title} (candidate bridge: `{bridge}`)".format(
                    kind=item.get("kind"),
                    tier=item.get("tier_id"),
                    title=item.get("title"),
                    bridge=item.get("candidate_bridge_topic"),
                )
            )
    lines.append("")
    return "\n".join(lines)


__all__ = [
    "ADVISORY_ONLY",
    "REPORT_SCHEMA_VERSION",
    "build_cadence_report",
    "render_markdown",
]
