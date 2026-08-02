"""Canonical, privacy-bounded default dispatch metrics events and snapshots.

This module is observational only. It accepts a deliberately small allowlist,
persists canonical rows through :class:`KnowledgeDB`, and never calls a
provider or touches dispatcher selection state.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

EVENT_SCHEMA_ID = "gtkb.dispatch_default_metric_event.v1"
SNAPSHOT_SCHEMA_ID = "gtkb.dispatch_default_metrics_snapshot.v1"
LEDGER_SCHEMA_ID = "gtkb.dispatch_success_ledger.v1"
DEFAULT_MAX_RECORDS = 50
LEDGER_DEFAULT_THRESHOLD = 60

_SUCCESS_OUTCOMES: frozenset[str] = frozenset({"reviewed", "implemented", "completed", "verified"})
_CLEAN_STOP_REASONS: frozenset[str | None] = frozenset({"completed", "turn_limit", "end_turn", None})

_ERROR_CLASSES: frozenset[str] = frozenset(
    {
        "provider_failure",
        "process_failure",
        "timeout",
        "publication_failure",
        "attribution_failure",
        "duplicate_dispatch",
        "partial_batch",
        "malformed_provenance",
        "dispatch_error",
    }
)

_COVERAGE_FAMILIES = ("turns", "tools", "usage", "cost", "quality", "adaptation")
_COUNT_FIELDS = {
    "turns": "turns_used",
    "tools": "tool_calls_total",
    "usage": "total_tokens",
    "cost": "provider_cost",
    "quality": "quality_score",
    "adaptation": "adaptation_score",
}
_DIMENSION_FIELDS = {
    "counts_by_harness": "harness_name",
    "counts_by_model_profile": "model_profile",
    "counts_by_role": "role",
    "counts_by_bridge_outcome": "queue_outcome",
    "counts_by_failure_class": "failure_class",
}


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def _timestamp(value: Any, *, field: str, required: bool = False) -> str | None:
    if value is None:
        if required:
            raise ValueError(f"{field} must be a UTC timestamp")
        return None
    if isinstance(value, datetime):
        parsed = value if value.tzinfo else value.replace(tzinfo=UTC)
        return parsed.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    text = _text(value)
    if text is None:
        if required:
            raise ValueError(f"{field} must be a UTC timestamp")
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _number(value: Any, *, integer: bool = False, minimum: float = 0) -> int | float | None:
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = int(value) if integer else float(value)
    if not math.isfinite(value) or value < minimum:
        return None
    return value


def _safe_refs(value: Any) -> dict[str, str | list[str]]:
    if not isinstance(value, Mapping):
        return {}
    result: dict[str, str | list[str]] = {}
    for key in ("telemetry", "benchmark", "adaptation", "quality"):
        raw = value.get(key)
        if isinstance(raw, str) and raw.strip():
            result[key] = raw.strip()
        elif isinstance(raw, (list, tuple)):
            refs = [item.strip() for item in raw if isinstance(item, str) and item.strip()]
            if refs:
                result[key] = sorted(set(refs))
    return result


def _safe_tool_counts(value: Any) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    counts: dict[str, int] = {}
    for name, count in value.items():
        tool_name = _text(name)
        normalized = _number(count, integer=True)
        if tool_name is not None and normalized is not None:
            counts[tool_name] = int(normalized)
    return dict(sorted(counts.items()))


def _coverage(observed: bool, *, reason: str | None = None) -> dict[str, Any]:
    return {
        "status": "observed" if observed else "unavailable",
        "observed": observed,
        "reason": None if observed else (reason or "measurement_unavailable"),
    }


def _coverage_map(raw: Mapping[str, Any], event: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    supplied = raw.get("coverage")
    supplied_map = supplied if isinstance(supplied, Mapping) else {}
    coverage: dict[str, dict[str, Any]] = {}
    for family in _COVERAGE_FAMILIES:
        field = _COUNT_FIELDS[family]
        observed = event.get(field) is not None
        candidate = supplied_map.get(family)
        if isinstance(candidate, Mapping):
            status = _text(candidate.get("status"))
            if status == "unavailable":
                observed = False
            elif status in {"observed", "partial"}:
                pass
            reason = _text(candidate.get("reason"))
        else:
            status = None
            reason = None
        coverage[family] = _coverage(observed, reason=reason)
        if status == "partial":
            coverage[family]["status"] = "partial"
    return coverage


def normalize_metric_event(raw: Mapping[str, Any], *, event_id: str | None = None) -> dict[str, Any]:
    """Return the safe canonical event projection from an observational input."""
    if not isinstance(raw, Mapping):
        raise TypeError("metric event must be a mapping")
    resolved_id = _text(event_id) or _text(raw.get("id")) or _text(raw.get("dispatch_id")) or _text(raw.get("run_id"))
    if resolved_id is None:
        raise ValueError("metric event requires an id, dispatch_id, or run_id")

    event_at = (
        _timestamp(raw.get("event_at") or raw.get("ended_at") or raw.get("started_at"), field="event_at") or _now()
    )
    started_at = _timestamp(raw.get("started_at"), field="started_at")
    ended_at = _timestamp(raw.get("ended_at"), field="ended_at")
    elapsed_ms = _number(raw.get("elapsed_ms"), integer=True)
    if elapsed_ms is None and started_at and ended_at:
        elapsed_ms = max(
            0,
            int(
                (
                    datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
                    - datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                ).total_seconds()
                * 1000
            ),
        )

    tool_counts = _safe_tool_counts(raw.get("tool_counts"))
    tool_calls_total = _number(raw.get("tool_calls_total"), integer=True)
    if tool_calls_total is None and tool_counts:
        tool_calls_total = sum(tool_counts.values())

    event: dict[str, Any] = {
        "id": resolved_id,
        "event_schema_id": EVENT_SCHEMA_ID,
        "event_at": event_at,
        "dispatch_id": _text(raw.get("dispatch_id")),
        "run_id": _text(raw.get("run_id")),
        "bridge_document_id": _text(raw.get("bridge_document_id")),
        "work_item_id": _text(raw.get("work_item_id")),
        "harness_session_id": _text(raw.get("harness_session_id")),
        "benchmark_id": _text(raw.get("benchmark_id")),
        "adaptation_id": _text(raw.get("adaptation_id")),
        "harness_id": _text(raw.get("harness_id")),
        "harness_name": _text(raw.get("harness_name")),
        "provider": _text(raw.get("provider")),
        "model_profile": _text(raw.get("model_profile")),
        "role": _text(raw.get("role")),
        "role_source": _text(raw.get("role_source")) or "document",
        "intended_role": _text(raw.get("intended_role")),
        "actual_role": _text(raw.get("actual_role")),
        "queue_outcome": _text(raw.get("queue_outcome")),
        "selection_outcome": _text(raw.get("selection_outcome")),
        "started_at": started_at,
        "ended_at": ended_at,
        "elapsed_ms": elapsed_ms,
        "exit_status": _number(raw.get("exit_status"), integer=True),
        "stop_reason": _text(raw.get("stop_reason")),
        "failure_class": _text(raw.get("failure_class")),
        "turns_used": _number(raw.get("turns_used"), integer=True),
        "tool_calls_total": tool_calls_total,
        "tool_counts": tool_counts,
        "input_tokens": _number(raw.get("input_tokens"), integer=True),
        "output_tokens": _number(raw.get("output_tokens"), integer=True),
        "cached_tokens": _number(raw.get("cached_tokens"), integer=True),
        "total_tokens": _number(raw.get("total_tokens"), integer=True),
        "provider_cost": _number(raw.get("provider_cost")),
        "benchmark_estimated_cost": _number(raw.get("benchmark_estimated_cost")),
        "quality_score": _number(raw.get("quality_score")),
        "quality_source": _text(raw.get("quality_source")),
        "adaptation_score": _number(raw.get("adaptation_score")),
        "adaptation_source": _text(raw.get("adaptation_source")),
        "source_refs": _safe_refs(raw.get("source_refs")),
    }
    event["coverage"] = _coverage_map(raw, event)
    event["freshness"] = {"status": "fresh", "as_of": event_at}
    event["unavailable_reasons"] = {
        family: details["reason"] for family, details in event["coverage"].items() if details["reason"] is not None
    }
    return event


def _bucket(value: int | float | None, buckets: tuple[tuple[str, float | None, float | None], ...]) -> str:
    if value is None:
        return "unknown"
    for label, lower, upper in buckets:
        if (lower is None or value >= lower) and (upper is None or value < upper):
            return label
    return "unknown"


def _distribution(
    values: Sequence[int | float | None],
    buckets: tuple[tuple[str, float | None, float | None], ...],
) -> dict[str, int]:
    counts = Counter(_bucket(value, buckets) for value in values)
    return {label: counts.get(label, 0) for label, _lower, _upper in buckets} | {"unknown": counts.get("unknown", 0)}


def _dimension_counts(events: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    counts = Counter(_text(event.get(field)) or "unknown" for event in events)
    return dict(sorted(counts.items()))


def _coverage_summary(events: Sequence[Mapping[str, Any]], family: str) -> dict[str, Any]:
    observed = sum(1 for event in events if event.get("coverage", {}).get(family, {}).get("observed") is True)
    total = len(events)
    return {
        "observed_count": observed,
        "missing_count": total - observed,
        "record_count": total,
        "coverage_ratio": (observed / total) if total else 0.0,
    }


def build_metrics_snapshot(
    events: Sequence[Mapping[str, Any]],
    *,
    max_records: int = DEFAULT_MAX_RECORDS,
    source_window_start: str | None = None,
    source_window_end: str | None = None,
    generated_at: str | None = None,
    snapshot_id: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic bounded snapshot from canonical event records."""
    if max_records <= 0:
        raise ValueError("max_records must be positive")
    normalized = [normalize_metric_event(event) for event in events]
    start = _timestamp(source_window_start, field="source_window_start")
    end = _timestamp(source_window_end, field="source_window_end")
    if start and end and start > end:
        raise ValueError("source window start must not be after its end")
    selected = [
        event
        for event in normalized
        if (start is None or event["event_at"] >= start) and (end is None or event["event_at"] <= end)
    ]
    selected.sort(key=lambda event: (event["event_at"], event["id"]))
    selected = selected[-max_records:]
    event_ids = [event["id"] for event in selected]
    window_start = start or (selected[0]["event_at"] if selected else None)
    window_end = end or (selected[-1]["event_at"] if selected else None)
    generated = _timestamp(generated_at, field="generated_at") or window_end or _now()
    if snapshot_id is None:
        digest = hashlib.sha256(
            json.dumps(
                {
                    "event_ids": event_ids,
                    "window_start": window_start,
                    "window_end": window_end,
                    "max_records": max_records,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:24]
        snapshot_id = f"dispatch-metrics-{digest}"

    freshness = {
        "status": "fresh" if selected else "unavailable",
        "generated_at": generated,
        "source_window_start": window_start,
        "source_window_end": window_end,
    }
    snapshot: dict[str, Any] = {
        "id": _text(snapshot_id),
        "snapshot_schema_id": SNAPSHOT_SCHEMA_ID,
        "generated_at": generated,
        "source_window_start": window_start,
        "source_window_end": window_end,
        "source_event_ids": event_ids,
        "source_record_count": len(selected),
        "max_records": max_records,
        "counts_by_harness": _dimension_counts(selected, "harness_name"),
        "counts_by_model_profile": _dimension_counts(selected, "model_profile"),
        "counts_by_role": _dimension_counts(selected, "role"),
        "counts_by_bridge_outcome": _dimension_counts(selected, "queue_outcome"),
        "counts_by_failure_class": _dimension_counts(selected, "failure_class"),
        "elapsed_distribution": _distribution(
            [event.get("elapsed_ms") for event in selected],
            (("under_1s", None, 1000), ("1_to_5s", 1000, 5000), ("5_to_30s", 5000, 30000), ("30s_plus", 30000, None)),
        ),
        "turns_distribution": _distribution(
            [event.get("turns_used") for event in selected],
            (("under_10", None, 10), ("10_to_50", 10, 51), ("51_to_100", 51, 101), ("101_plus", 101, None)),
        ),
        "tools_distribution": _distribution(
            [event.get("tool_calls_total") for event in selected],
            (("zero", 0, 1), ("1_to_10", 1, 11), ("11_to_50", 11, 51), ("51_plus", 51, None)),
        ),
        "usage_coverage": {family: _coverage_summary(selected, family) for family in ("turns", "tools", "usage")},
        "cost_coverage": {
            "provider_reported": _coverage_summary(
                [{"coverage": {"cost": {"observed": event.get("provider_cost") is not None}}} for event in selected],
                "cost",
            ),
            "benchmark_estimated": {
                "observed_count": sum(event.get("benchmark_estimated_cost") is not None for event in selected),
                "missing_count": sum(event.get("benchmark_estimated_cost") is None for event in selected),
                "record_count": len(selected),
                "coverage_ratio": (
                    sum(event.get("benchmark_estimated_cost") is not None for event in selected) / len(selected)
                    if selected
                    else 0.0
                ),
            },
        },
        "quality_coverage": _coverage_summary(selected, "quality"),
        "adaptation_coverage": _coverage_summary(selected, "adaptation"),
        "freshness": freshness,
        "provenance": {
            "source": "canonical_dispatch_default_metric_events",
            "source_schema_id": EVENT_SCHEMA_ID,
            "generator": "groundtruth_kb.dispatch_default_metrics",
        },
    }
    if snapshot["id"] is None:
        raise ValueError("snapshot_id must be a non-empty string")
    return snapshot


def validate_metric_event(event: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return the canonical event projection."""
    normalized = normalize_metric_event(event)
    if normalized["event_schema_id"] != EVENT_SCHEMA_ID:
        raise ValueError("unsupported default metric event schema")
    return normalized


def validate_metrics_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the bounded snapshot shape without accepting raw content."""
    if not isinstance(snapshot, Mapping) or snapshot.get("snapshot_schema_id") != SNAPSHOT_SCHEMA_ID:
        raise ValueError("unsupported default metrics snapshot schema")
    snapshot_id = _text(snapshot.get("id"))
    source_ids = snapshot.get("source_event_ids")
    count = snapshot.get("source_record_count")
    max_records = snapshot.get("max_records")
    if snapshot_id is None or not isinstance(source_ids, list):
        raise ValueError("snapshot id and source_event_ids are required")
    if not isinstance(count, int) or not isinstance(max_records, int) or count != len(source_ids):
        raise ValueError("snapshot record bounds are invalid")
    if count < 0 or max_records <= 0 or count > max_records:
        raise ValueError("snapshot record bounds are invalid")
    return dict(snapshot)


def persist_metric_event(db: Any, raw: Mapping[str, Any], changed_by: str, change_reason: str) -> dict[str, Any]:
    event = validate_metric_event(raw)
    result = db.insert_dispatch_default_metric_event(event["id"], event, changed_by, change_reason)
    if result is None:
        raise RuntimeError("canonical metric event insert returned no row")
    return result


def persist_metrics_snapshot(
    db: Any,
    events: Sequence[Mapping[str, Any]] | None,
    changed_by: str,
    change_reason: str,
    **kwargs: Any,
) -> dict[str, Any]:
    if events is None:
        events = db.list_dispatch_default_metric_events(limit=DEFAULT_MAX_RECORDS)
    snapshot = build_metrics_snapshot(events, **kwargs)
    validate_metrics_snapshot(snapshot)
    result = db.insert_dispatch_default_metrics_snapshot(snapshot["id"], snapshot, changed_by, change_reason)
    if result is None:
        raise RuntimeError("canonical metrics snapshot insert returned no row")
    return result


record_metric_event = persist_metric_event
generate_metrics_snapshot = build_metrics_snapshot


def _event_is_terminal_success(event: Mapping[str, Any]) -> bool:
    """Return True when the canonical event represents terminal dispatch success."""
    outcome = _text(event.get("queue_outcome"))
    if outcome is None or outcome not in _SUCCESS_OUTCOMES:
        return False
    failure_class = _text(event.get("failure_class"))
    if failure_class is not None and failure_class in _ERROR_CLASSES:
        return False
    exit_status = event.get("exit_status")
    if exit_status is not None and exit_status != 0:
        return False
    stop_reason = _text(event.get("stop_reason"))
    return not (stop_reason is not None and stop_reason not in _CLEAN_STOP_REASONS)


def _event_binds_provenance(event: Mapping[str, Any]) -> bool:
    """Return True when the event binds all required provenance fields."""
    dispatch_id = _text(event.get("dispatch_id"))
    harness_id = _text(event.get("harness_id"))
    role_field = _text(event.get("role"))
    bridge_document_id = _text(event.get("bridge_document_id"))
    return all((dispatch_id, harness_id, role_field, bridge_document_id))


def _event_reset_reason(event: Mapping[str, Any]) -> str:
    """Return a canonical reset-reason label for the event."""
    failure_class = _text(event.get("failure_class"))
    if failure_class is not None and failure_class in _ERROR_CLASSES:
        return f"failure_class:{failure_class}"
    outcome = _text(event.get("queue_outcome"))
    if outcome is not None and outcome not in _SUCCESS_OUTCOMES:
        return f"non_success_outcome:{outcome}"
    exit_status = event.get("exit_status")
    if exit_status is not None and exit_status != 0:
        return f"exit_status:{exit_status}"
    stop_reason = _text(event.get("stop_reason"))
    if stop_reason is not None and stop_reason not in _CLEAN_STOP_REASONS:
        return f"stop_reason:{stop_reason}"
    prov_ok = _event_binds_provenance(event)
    if not prov_ok:
        return "missing_provenance_binding"
    return "unknown_reset"


def build_success_ledger(
    db: Any,
    *,
    threshold: int = LEDGER_DEFAULT_THRESHOLD,
    max_scan: int = 500,
) -> dict[str, Any]:
    """Derive the canonical consecutive dispatcher-item success ledger.

    Reads canonical persisted metric events from *db* (a :class:`KnowledgeDB`),
    orders them deterministically, and computes the consecutive success streak.
    The ledger is observational only — never reads or mutates dispatcher runtime
    state, logs, claims, leases, or scratch artifacts.

    Returns a dict with ``schema_id``, ``streak``, ``threshold_met``, ``sequence``
    bounds, ``reset_reason``, ``distribution``, and ``generated_at``.
    """
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    events = list(db.list_dispatch_default_metric_events(limit=max(max_scan, threshold * 4)))
    normalized = [normalize_metric_event(event) for event in events]
    normalized.sort(key=lambda e: (e["event_at"] or "", e["id"] or ""))

    streak_count = 0
    first_reset_reason: str | None = None
    sequence_start: dict[str, str] | None = None
    last_success_event: dict[str, Any] | None = None
    harness_count: Counter[str] = Counter()
    role_count: Counter[str] = Counter()
    seen: set[str] = set()

    for event in normalized:
        seen_key = event["id"] or ""
        if not seen_key:
            continue
        if seen_key in seen:
            continue
        seen.add(seen_key)

        if not _event_binds_provenance(event):
            if first_reset_reason is None:
                first_reset_reason = "missing_provenance_binding"
            streak_count = 0
            harness_count.clear()
            role_count.clear()
            sequence_start = None
            last_success_event = None
            continue

        if not _event_is_terminal_success(event):
            if first_reset_reason is None:
                first_reset_reason = _event_reset_reason(event)
            streak_count = 0
            harness_count.clear()
            role_count.clear()
            sequence_start = None
            last_success_event = None
            continue

        streak_count += 1
        hid = _text(event.get("harness_id")) or "unknown"
        rid = _text(event.get("role")) or "unknown"
        harness_count[hid] += 1
        role_count[rid] += 1
        last_success_event = event
        if sequence_start is None:
            sequence_start = {
                "dispatch_id": _text(event.get("dispatch_id")) or "",
                "event_at": _text(event.get("event_at")) or "",
            }

    sequence_end = None
    if last_success_event is not None:
        sequence_end = {
            "dispatch_id": _text(last_success_event.get("dispatch_id")) or "",
            "event_at": _text(last_success_event.get("event_at")) or "",
        }

    return {
        "schema_id": LEDGER_SCHEMA_ID,
        "schema_version": 1,
        "streak": streak_count,
        "threshold": threshold,
        "threshold_met": streak_count >= threshold,
        "sequence": {
            "start": sequence_start,
            "end": sequence_end,
        },
        "first_reset_reason": first_reset_reason,
        "distribution": {
            "by_harness": dict(sorted(harness_count.items())),
            "by_role": dict(sorted(role_count.items())),
        },
        "generated_at": _now(),
    }


def build_success_ledger_from_root(
    project_root_str: str,
    *,
    threshold: int = LEDGER_DEFAULT_THRESHOLD,
    max_scan: int = 500,
) -> dict[str, Any]:
    """Build the success ledger from a project root path string.

    Opens a read-only connection to ``groundtruth.db`` under the root,
    wraps it in a :class:`KnowledgeDB`, and delegates to
    :func:`build_success_ledger`.
    """
    from pathlib import Path as _Path

    from groundtruth_kb.db import KnowledgeDB

    db_path = _Path(project_root_str) / "groundtruth.db"
    if not db_path.is_file():
        return {
            "schema_id": LEDGER_SCHEMA_ID,
            "schema_version": 1,
            "streak": 0,
            "threshold": threshold,
            "threshold_met": False,
            "sequence": {"start": None, "end": None},
            "first_reset_reason": "canonical_event_store_unavailable",
            "distribution": {"by_harness": {}, "by_role": {}},
            "generated_at": _now(),
        }
    db = KnowledgeDB(db_path)
    return build_success_ledger(db, threshold=threshold, max_scan=max_scan)


__all__ = [
    "DEFAULT_MAX_RECORDS",
    "EVENT_SCHEMA_ID",
    "SNAPSHOT_SCHEMA_ID",
    "LEDGER_SCHEMA_ID",
    "LEDGER_DEFAULT_THRESHOLD",
    "build_metrics_snapshot",
    "build_success_ledger",
    "build_success_ledger_from_root",
    "generate_metrics_snapshot",
    "normalize_metric_event",
    "persist_metric_event",
    "persist_metrics_snapshot",
    "record_metric_event",
    "validate_metric_event",
    "validate_metrics_snapshot",
]
