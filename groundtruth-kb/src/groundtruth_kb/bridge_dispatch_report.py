"""Read-only bridge dispatcher reporting helpers."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
from collections import Counter, deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.bridge_dispatch_config import (
    DISPATCH_ROLES,
    collect_bridge_dispatch_health,
    collect_bridge_dispatch_status,
)

STATE_DIR_RELATIVE_PATH = Path(".gtkb-state") / "bridge-poller"
RUNS_RELATIVE_PATH = STATE_DIR_RELATIVE_PATH / "dispatch-runs"
RUN_TIMESTAMP_RE = re.compile(r"^(?P<stamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)")
PID_CREATE_TIME_SUFFIX = ".create_time_epoch"
PID_CREATE_TIME_MATCH_TOLERANCE_SECONDS = 0.01
WORKFLOW_SCHEMA_VERSION = "gtkb.dispatch_workflow.v1"
WORKFLOW_RECORD_LIMIT = 20
METRICS_SNAPSHOT_CATEGORY = "dispatch_default_metrics_snapshot"
_METRIC_LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._:/@()+-]{0,119}$")
_WORK_ITEM_METADATA_RE = re.compile(r"^Work Item:\s*`?(?P<work_item_id>WI-[A-Za-z0-9-]+)", re.IGNORECASE | re.MULTILINE)
_PROJECT_METADATA_RE = re.compile(r"^Project:\s*`?(?P<project_id>[A-Za-z0-9_-]+)", re.IGNORECASE | re.MULTILINE)
_BRIDGE_VERSION_RE = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3,})\.md$")
_BRIDGE_SLUG_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$")
_DISPATCH_RECIPIENT_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z-(?P<role>prime-builder|loyal-opposition)-"
    r"(?P<harness_id>[^-]+)-"
)


def build_bridge_dispatch_report(
    project_root: Path,
    *,
    max_records: int = 50,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build a bounded, read-only dispatcher operations report."""
    root = project_root.resolve()
    status = collect_bridge_dispatch_status(root)
    status_payload = status.to_json_dict()
    health_rollup = collect_bridge_dispatch_health(root, routing_status=status)
    now_utc = now or datetime.now(UTC)

    state, state_warnings = _read_json(root / STATE_DIR_RELATIVE_PATH / "dispatch-state.json")
    recipients = state.get("recipients") if isinstance(state.get("recipients"), dict) else {}
    if not isinstance(recipients, dict):
        recipients = {}

    dispatch_failures, failure_warnings = _read_jsonl_glob(root, "dispatch-failures.jsonl*", max_records)
    dispatch_suppressions, suppression_warnings = _read_jsonl_glob(root, "dispatch-suppressions.jsonl*", max_records)
    trigger_diagnostics, diagnostic_warnings = _read_jsonl_glob(root, "trigger-diagnostic.jsonl*", max_records)
    starvation_telemetry, starvation_warnings = _read_json(root / STATE_DIR_RELATIVE_PATH / "starvation-telemetry.json")
    recent_runs = _collect_recent_runs(root, max_records=max_records, now=now_utc)

    selected_by_role = status_payload["selected_by_role"]
    effective_ceiling = _effective_per_cycle_ceiling(selected_by_role)
    live_runs = [run for run in recent_runs if run["state"] == "live"]
    run_counts = Counter(str(run["state"]) for run in recent_runs)
    success_count = run_counts.get("exit_0", 0)
    completed_count = success_count + run_counts.get("exit_nonzero", 0)
    success_rate = None if completed_count == 0 else success_count / completed_count

    failure_taxonomy = _failure_taxonomy(recipients, dispatch_failures, dispatch_suppressions)
    circuit_breakers = [
        {
            "recipient": key,
            "failure_class": row.get("failure_class"),
            "last_result": row.get("last_result"),
            "pending_count": row.get("pending_count"),
        }
        for key, row in sorted(recipients.items())
        if isinstance(row, dict) and row.get("circuit_breaker_tripped") is True
    ]

    warnings = state_warnings + failure_warnings + suppression_warnings + diagnostic_warnings + starvation_warnings
    runtime_failure_count = sum(1 for finding in status.health_findings if "dispatch runtime failure" in finding)
    runtime_warning_count = sum(1 for finding in status.health_findings if "dispatch runtime warning" in finding)

    return {
        "summary": {
            "health_status": health_rollup["health_status"],
            "health_finding_count": len(status.health_findings),
            "runtime_failure_count": runtime_failure_count,
            "runtime_warning_count": runtime_warning_count,
            "selected_candidate_count": {role: len(selected_by_role.get(role, [])) for role in DISPATCH_ROLES},
            "effective_per_cycle_ceiling": effective_ceiling,
            "live_worker_count": len(live_runs),
            "recent_run_count": len(recent_runs),
            "warning_count": len(warnings),
        },
        "configuration": status_payload["config"],
        "topology": {
            "harnesses": status_payload["harnesses"],
            "selected_by_role": selected_by_role,
            "effective_per_cycle_ceiling": effective_ceiling,
        },
        "performance": {
            "recent_run_counts": dict(sorted(run_counts.items())),
            "success_rate": success_rate,
            "per_recipient": _recipient_performance(recipients),
        },
        "reliability": {
            "health_status": status.health_status,
            "health_rollup": health_rollup,
            "findings": list(status.health_findings),
            "consistency_findings": list(status.consistency_findings),
            "runtime_classifications": list(status.runtime_classifications),
            "failure_taxonomy": failure_taxonomy,
            "circuit_breakers": circuit_breakers,
            "dispatch_failures_tail": dispatch_failures,
            "dispatch_suppressions_tail": dispatch_suppressions,
            "warnings": warnings,
        },
        "live_state": {
            "updated_at": state.get("updated_at"),
            "recipients": recipients,
            "live_worker_count": len(live_runs),
            "live_workers": live_runs,
            "starvation_telemetry": starvation_telemetry,
        },
        "history": {
            "recent_runs": recent_runs,
            "trigger_diagnostics_tail": trigger_diagnostics,
        },
    }


def format_bridge_dispatch_report(report: dict[str, Any]) -> str:
    """Render a compact human-readable dispatch operations report."""
    summary = report["summary"]
    lines = [
        f"Bridge dispatch report: {summary['health_status']}",
        f"Effective per-cycle ceiling: {summary['effective_per_cycle_ceiling']}",
        f"Live workers: {summary['live_worker_count']}",
        "",
        "Selected candidates:",
    ]
    for role in DISPATCH_ROLES:
        rows = report["topology"]["selected_by_role"].get(role, [])
        ids = [str(row.get("id")) for row in rows]
        lines.append(f"- {role}: {', '.join(ids) if ids else '(none)'}")
    lines.append("")
    lines.append("Recent runs:")
    for state, count in report["performance"]["recent_run_counts"].items():
        lines.append(f"- {state}: {count}")
    if report["reliability"]["findings"]:
        lines.append("")
        lines.append("Reliability findings:")
        for finding in report["reliability"]["findings"]:
            lines.append(f"- {finding}")
    return "\n".join(lines)


def build_compact_dispatch_workflow(
    project_root: Path,
    *,
    report: dict[str, Any] | None = None,
    max_records: int = WORKFLOW_RECORD_LIMIT,
) -> dict[str, Any]:
    """Build the bounded, read-only workflow projection for dispatch reporting."""
    from groundtruth_kb.bridge.status_driver import collect_bridge_status

    root = project_root.resolve()
    limit = min(max(1, max_records), WORKFLOW_RECORD_LIMIT)
    full_report = report or build_bridge_dispatch_report(root)
    queue = collect_bridge_status(root, top_n=None).queue

    prime_queues, prime_truncation = _workflow_prime_queues(root, queue.prime_actionable, limit)
    loyal_queues, loyal_truncation = _workflow_loyal_queues(queue.loyal_opposition_actionable, limit)
    in_flight, in_flight_truncated = _bounded_workflow_records(_workflow_in_flight(root, full_report), limit)
    findings, findings_truncated = _bounded_workflow_records(
        [{"finding": finding} for finding in full_report["reliability"]["findings"]],
        limit,
    )
    selected_targets, targets_truncated = _workflow_selected_targets(full_report, limit)
    recent_work_metrics = _recent_work_metrics(root, limit)
    success_ledger = _success_ledger_section(root)

    return {
        "schema_version": WORKFLOW_SCHEMA_VERSION,
        "status": {
            "health_status": full_report["summary"]["health_status"],
            "findings": findings,
            "bridge_status_counts": dict(queue.status_counts),
            "selected_targets": selected_targets,
        },
        "in_flight": in_flight,
        "queues": {
            "prime_builder": prime_queues,
            "loyal_opposition": loyal_queues,
        },
        "recent_work_metrics": recent_work_metrics,
        "success_ledger": success_ledger,
        "bounds": {
            "per_section_limit": limit,
            "truncated": {
                "status_findings": findings_truncated,
                "status_selected_targets": targets_truncated,
                "in_flight": in_flight_truncated,
                "queues": {
                    "prime_builder": prime_truncation,
                    "loyal_opposition": loyal_truncation,
                },
            },
        },
    }


def format_compact_dispatch_workflow(workflow: dict[str, Any]) -> str:
    """Render the default bounded human workflow view."""
    status = workflow["status"]
    lines = [
        f"Bridge dispatch workflow: {status['health_status']}",
        f"In-flight dispatches: {len(workflow['in_flight'])}",
        "",
    ]
    for label, key in (("Prime Builder", "prime_builder"), ("Loyal Opposition", "loyal_opposition")):
        lines.append(f"{label}:")
        queues = workflow["queues"][key]
        for category, title in (
            ("actionable_now", "Actionable now"),
            ("candidate_next", "Candidate next"),
            ("blocked", "Blocked"),
        ):
            rows = queues[category]
            if not rows:
                lines.append(f"- {title}: (none)")
                continue
            rendered = ", ".join(_format_workflow_record(row) for row in rows)
            lines.append(f"- {title}: {rendered}")
        lines.append("")
    metrics = workflow["recent_work_metrics"]
    lines.append("Recent-work metrics:")
    if metrics["availability"] in {"unavailable", "stale"}:
        lines.append(f"- {metrics['availability']}: {metrics['reason']}")
    else:
        lines.extend(
            [
                f"- Snapshot: {metrics['snapshot_id']}",
                f"- Availability: {metrics['availability']}",
                f"- Records: {metrics['record_count']}",
                f"- Coverage: {json.dumps(metrics['coverage'], sort_keys=True, separators=(',', ':'))}",
            ]
        )
    ledger = workflow.get("success_ledger") if isinstance(workflow.get("success_ledger"), dict) else {}
    if ledger:
        lines.append("")
        lines.append("Success ledger:")
        availability = str(ledger.get("availability", "unavailable"))
        if availability != "available":
            reason = ledger.get("reason", "ledger_unavailable")
            lines.append(f"- {availability}: {reason}")
        else:
            streak = ledger.get("streak")
            threshold = ledger.get("threshold")
            threshold_met = ledger.get("threshold_met")
            reset = ledger.get("first_reset_reason")
            by_harness = ledger.get("distribution", {}).get("by_harness", {})
            lines.append(f"- Streak: {streak}/{threshold} (threshold met: {threshold_met})")
            if reset:
                lines.append(f"- First reset: {reset}")
            if by_harness:
                hdist = ", ".join(f"{h}: {c}" for h, c in sorted(by_harness.items()))
                lines.append(f"- By harness: {hdist}")
    return "\n".join(lines).rstrip()


def _success_ledger_section(root: Path) -> dict[str, Any]:
    """Build the bounded success-ledger section for the compact workflow."""
    try:
        from groundtruth_kb.dispatch_default_metrics import build_success_ledger_from_root

        ledger = build_success_ledger_from_root(str(root.resolve()))
    except (OSError, ImportError, RuntimeError):
        return {
            "availability": "unavailable",
            "reason": "ledger_construction_failed",
            "streak": None,
            "threshold": None,
            "threshold_met": None,
            "sequence": {"start": None, "end": None},
            "first_reset_reason": None,
            "distribution": {"by_harness": {}, "by_role": {}},
            "generated_at": None,
        }

    streak = ledger.get("streak")
    threshold = ledger.get("threshold")
    reason = ledger.get("first_reset_reason")
    # Empty or unavailable event store
    if streak is None or reason == "canonical_event_store_unavailable" or (streak == 0 and reason is None):
        return {
            "availability": "unavailable",
            "reason": reason or "no_canonical_events",
            "streak": streak,
            "threshold": threshold,
            "threshold_met": ledger.get("threshold_met"),
            "sequence": ledger.get("sequence"),
            "first_reset_reason": reason,
            "distribution": ledger.get("distribution"),
            "generated_at": ledger.get("generated_at"),
        }

    return {
        "availability": "available",
        "reason": None,
        "streak": streak,
        "threshold": threshold,
        "threshold_met": ledger.get("threshold_met"),
        "sequence": ledger.get("sequence"),
        "first_reset_reason": ledger.get("first_reset_reason"),
        "distribution": ledger.get("distribution"),
        "generated_at": ledger.get("generated_at"),
    }


def _unavailable_recent_work_metrics(reason: str) -> dict[str, Any]:
    return {
        "availability": "unavailable",
        "reason": reason,
        "snapshot_id": None,
        "schema_id": None,
        "schema_version": None,
        "source_window": {"start": None, "end": None},
        "generated_at": None,
        "freshness": {"status": "unavailable"},
        "record_count": None,
        "coverage": None,
        "distributions": None,
        "breakouts": None,
        "cost_coverage": {
            "provider_reported": None,
            "benchmark_estimated": None,
        },
        "bounds": {"per_distribution_limit": WORKFLOW_RECORD_LIMIT},
    }


def _recent_work_metrics(root: Path, limit: int) -> dict[str, Any]:
    db_path = root / "groundtruth.db"
    if not db_path.is_file():
        return _unavailable_recent_work_metrics("canonical_snapshot_store_unavailable")
    try:
        with sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                """
                SELECT id, content, changed_at, version
                FROM current_documents
                WHERE category = ? AND status = 'active'
                ORDER BY changed_at DESC, version DESC, id DESC
                LIMIT 1
                """,
                (METRICS_SNAPSHOT_CATEGORY,),
            ).fetchone()
    except (OSError, sqlite3.Error):
        return _unavailable_recent_work_metrics("canonical_snapshot_store_unavailable")
    if row is None:
        return _unavailable_recent_work_metrics("canonical_snapshot_unavailable")
    try:
        from groundtruth_kb.dispatch_default_metrics import SNAPSHOT_SCHEMA_ID, validate_metrics_snapshot

        raw = json.loads(str(row["content"] or ""))
        snapshot = validate_metrics_snapshot(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return _unavailable_recent_work_metrics("canonical_snapshot_invalid")

    freshness = snapshot.get("freshness") if isinstance(snapshot.get("freshness"), dict) else {}
    freshness_status = str(freshness.get("status") or "unavailable")
    if freshness_status not in {"fresh", "partial", "stale", "unavailable"}:
        freshness_status = "unavailable"
    record_count = snapshot.get("source_record_count")
    usage_coverage = snapshot.get("usage_coverage") if isinstance(snapshot.get("usage_coverage"), dict) else {}
    cost_coverage = snapshot.get("cost_coverage") if isinstance(snapshot.get("cost_coverage"), dict) else {}
    coverage = {
        "turns": _metric_coverage(usage_coverage.get("turns")),
        "tool_calls": _metric_coverage(usage_coverage.get("tools")),
        "token_cache": _metric_coverage(usage_coverage.get("usage")),
        "benchmark_quality": _metric_coverage(snapshot.get("quality_coverage")),
        "adaptation": _metric_coverage(snapshot.get("adaptation_coverage")),
    }
    availability = _metrics_availability(freshness_status, record_count, coverage)
    reason = None
    if availability == "stale":
        reason = "canonical_snapshot_stale"
    elif availability == "unavailable":
        reason = "canonical_snapshot_empty"
    elif availability == "partial":
        reason = "canonical_snapshot_partial"

    return {
        "availability": availability,
        "reason": reason,
        "snapshot_id": _safe_metric_label(snapshot.get("id")),
        "schema_id": SNAPSHOT_SCHEMA_ID,
        "schema_version": 1,
        "source_window": {
            "start": _safe_metric_timestamp(snapshot.get("source_window_start")),
            "end": _safe_metric_timestamp(snapshot.get("source_window_end")),
        },
        "generated_at": _safe_metric_timestamp(snapshot.get("generated_at")),
        "freshness": {"status": freshness_status},
        "record_count": record_count,
        "coverage": coverage,
        "distributions": {
            "outcomes": _bounded_metric_counts(snapshot.get("counts_by_bridge_outcome"), limit),
            "failure_classes": _bounded_metric_counts(snapshot.get("counts_by_failure_class"), limit),
            "elapsed_time": _bounded_metric_counts(snapshot.get("elapsed_distribution"), limit),
            "turns": _bounded_metric_counts(snapshot.get("turns_distribution"), limit),
            "tool_calls": _bounded_metric_counts(snapshot.get("tools_distribution"), limit),
        },
        "breakouts": {
            "harness": _bounded_metric_counts(snapshot.get("counts_by_harness"), limit),
            "model_profile": _bounded_metric_counts(snapshot.get("counts_by_model_profile"), limit),
            "role": _bounded_metric_counts(snapshot.get("counts_by_role"), limit),
        },
        "cost_coverage": {
            "provider_reported": _metric_coverage(cost_coverage.get("provider_reported")),
            "benchmark_estimated": _metric_coverage(cost_coverage.get("benchmark_estimated")),
        },
        "bounds": {"per_distribution_limit": limit},
    }


def _bounded_metric_counts(value: Any, limit: int) -> dict[str, int | float] | None:
    if not isinstance(value, dict):
        return None
    allowed: dict[str, int | float] = {}
    for key, item in sorted(value.items(), key=lambda row: str(row[0])):
        if len(allowed) >= limit:
            break
        safe_key = _safe_metric_label(key)
        if safe_key is None or isinstance(item, bool) or not isinstance(item, (int, float)) or item < 0:
            continue
        allowed[safe_key] = item
    return allowed


def _metric_coverage(value: Any) -> dict[str, int | float] | None:
    if not isinstance(value, dict):
        return None
    result: dict[str, int | float] = {}
    for key in ("observed_count", "missing_count", "record_count", "coverage_ratio"):
        item = value.get(key)
        if isinstance(item, (int, float)) and not isinstance(item, bool) and item >= 0:
            result[key] = item
    return result or None


def _safe_metric_label(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized if _METRIC_LABEL_RE.fullmatch(normalized) else None


def _safe_metric_timestamp(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _metrics_availability(
    freshness_status: str,
    record_count: Any,
    coverage: dict[str, dict[str, Any] | None],
) -> str:
    if freshness_status == "stale":
        return "stale"
    if freshness_status == "unavailable" or not isinstance(record_count, int) or record_count <= 0:
        return "unavailable"
    if freshness_status == "partial":
        return "partial"
    for details in coverage.values():
        if isinstance(details, dict) and int(details.get("missing_count") or 0) > 0:
            return "partial"
    return "observed"


def _workflow_prime_queues(
    root: Path, items: Any, limit: int
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, bool]]:
    categories: dict[str, list[dict[str, Any]]] = {
        "actionable_now": [],
        "candidate_next": [],
        "blocked": [],
    }
    for item in items:
        record = _workflow_record(item)
        if item.top_status == "NO-GO":
            categories["actionable_now"].append(record)
            continue
        if item.top_status == "ADVISORY":
            record["reason_code"] = "advisory_requires_owner_intake"
            categories["candidate_next"].append(record)
            continue
        if item.top_status != "GO":
            continue

        reason_code, context = _workflow_go_context(root, item.top_file)
        if context:
            record.update(context)
        if reason_code is None:
            categories["actionable_now"].append(record)
        else:
            record["reason_code"] = reason_code
            categories["blocked"].append(record)
    return _bound_workflow_categories(categories, limit)


def _workflow_loyal_queues(items: Any, limit: int) -> tuple[dict[str, list[dict[str, Any]]], dict[str, bool]]:
    categories: dict[str, list[dict[str, Any]]] = {
        "actionable_now": [],
        "candidate_next": [],
        "blocked": [],
    }
    for item in items:
        record = _workflow_record(item)
        if item.top_status in {"NEW", "REVISED"}:
            categories["actionable_now"].append(record)
        else:
            record["reason_code"] = "owner_hold"
            categories["candidate_next"].append(record)
    return _bound_workflow_categories(categories, limit)


def _workflow_record(item: Any) -> dict[str, Any]:
    return {
        "id": item.document_name,
        "document_name": item.document_name,
        "title": item.document_name,
        "source_authority": item.top_file,
        "lifecycle_status": item.top_status,
        "dispatchable": item.dispatchable,
    }


def _workflow_go_context(root: Path, top_file: str) -> tuple[str | None, dict[str, Any]]:
    metadata = _read_workflow_bridge_metadata(root, top_file)
    work_item_id = metadata.get("work_item_id")
    project_id = metadata.get("project_id")
    if not work_item_id or not project_id:
        return "bridge_metadata_unresolvable", {}

    context: dict[str, Any] = {"work_item_id": work_item_id, "project_id": project_id}
    db_path = root / "groundtruth.db"
    if not db_path.is_file():
        return "bridge_metadata_unresolvable", context

    try:
        with sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True) as connection:
            connection.row_factory = sqlite3.Row
            work_item = connection.execute(
                "SELECT id, title, source_spec_id FROM current_work_items WHERE id = ? LIMIT 1",
                (work_item_id,),
            ).fetchone()
            if work_item is None:
                return "bridge_metadata_unresolvable", context
            title = str(work_item["title"] or "").strip()
            if title:
                context["title"] = title
            membership = connection.execute(
                """
                SELECT status
                FROM current_project_work_item_memberships
                WHERE project_id = ? AND work_item_id = ?
                LIMIT 1
                """,
                (project_id, work_item_id),
            ).fetchone()
            if membership is None or str(membership["status"] or "").lower() != "active":
                return "bridge_metadata_unresolvable", context
            source_spec_id = str(work_item["source_spec_id"] or "").strip()
            if not source_spec_id:
                return "missing_source_spec", context
            context["source_spec_id"] = source_spec_id
            specification = connection.execute(
                "SELECT status FROM current_specifications WHERE id = ? LIMIT 1",
                (source_spec_id,),
            ).fetchone()
            if specification is None or str(specification["status"] or "").lower() not in {
                "specified",
                "implemented",
                "verified",
            }:
                return "missing_source_spec", context
    except (OSError, sqlite3.Error):
        return "bridge_metadata_unresolvable", context

    return None, context


def _read_workflow_bridge_metadata(root: Path, top_file: str) -> dict[str, str | None]:
    top_path = root / top_file
    candidates = [top_path]
    match = _BRIDGE_VERSION_RE.match(top_path.name)
    if match and top_path.parent.is_dir():
        versions: list[tuple[int, Path]] = []
        for path in top_path.parent.glob(f"{match.group('slug')}-*.md"):
            version_match = _BRIDGE_VERSION_RE.match(path.name)
            if version_match and version_match.group("slug") == match.group("slug"):
                versions.append((int(version_match.group("version")), path))
        candidates = [path for _version, path in sorted(versions, reverse=True)]

    metadata: dict[str, str | None] = {"work_item_id": None, "project_id": None}
    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if metadata["work_item_id"] is None:
            work_item = _WORK_ITEM_METADATA_RE.search(text)
            if work_item:
                metadata["work_item_id"] = work_item.group("work_item_id").upper()
        if metadata["project_id"] is None:
            project = _PROJECT_METADATA_RE.search(text)
            if project:
                metadata["project_id"] = project.group("project_id")
        if all(metadata.values()):
            break
    return metadata


def _workflow_json_list(value: Any) -> set[str]:
    if value is None:
        return set()
    try:
        decoded = json.loads(str(value))
    except json.JSONDecodeError:
        decoded = str(value).split(",")
    if not isinstance(decoded, list):
        return set()
    return {str(item).strip() for item in decoded if str(item).strip()}


def _workflow_launch_index(report: dict[str, Any]) -> dict[str, dict[str, Any] | None]:
    recipients = report.get("live_state", {}).get("recipients", {})
    if not isinstance(recipients, dict):
        return {}

    index: dict[str, dict[str, Any] | None] = {}
    missing = object()

    def add(launch: Any) -> None:
        if not isinstance(launch, dict):
            return
        dispatch_id = launch.get("dispatch_id")
        if not isinstance(dispatch_id, str) or not dispatch_id.strip():
            return
        dispatch_id = dispatch_id.strip()
        existing = index.get(dispatch_id, missing)
        if existing is missing:
            index[dispatch_id] = launch
        elif existing is not None and existing != launch:
            index[dispatch_id] = None

    for recipient in recipients.values():
        if not isinstance(recipient, dict):
            continue
        ledger_ids: set[str] = set()
        ledger = recipient.get("launch_ledger")
        if isinstance(ledger, dict):
            ledger_groups: list[dict[str, Any]] = []
            active = ledger.get("active")
            completed = ledger.get("completed")
            if isinstance(active, dict) or isinstance(completed, dict):
                if isinstance(active, dict):
                    ledger_groups.append(active)
                if isinstance(completed, dict):
                    ledger_groups.append(completed)
            else:
                ledger_groups.append(ledger)
            for group in ledger_groups:
                for launch in group.values():
                    if isinstance(launch, dict):
                        dispatch_id = launch.get("dispatch_id")
                        if isinstance(dispatch_id, str) and dispatch_id.strip():
                            ledger_ids.add(dispatch_id.strip())
                    add(launch)

        last_launch = recipient.get("last_launch")
        if isinstance(last_launch, dict):
            dispatch_id = last_launch.get("dispatch_id")
            if isinstance(dispatch_id, str) and dispatch_id.strip() not in ledger_ids:
                add(last_launch)
    return index


def _workflow_bridge_slug(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    slug = value.strip()
    return slug if _BRIDGE_SLUG_RE.fullmatch(slug) else None


def _workflow_launch_document(launch: dict[str, Any]) -> str | None:
    lease_documents: list[str] = []
    handles = launch.get("document_lease_handles")
    if isinstance(handles, list):
        for handle in handles:
            slug = _workflow_bridge_slug(handle.get("doc_slug")) if isinstance(handle, dict) else None
            if slug and slug not in lease_documents:
                lease_documents.append(slug)

    selected_documents: list[str] = []
    for key in ("selected_documents", "document_names"):
        values = launch.get(key)
        if not isinstance(values, list):
            continue
        for value in values:
            slug = _workflow_bridge_slug(value)
            if slug and slug not in selected_documents:
                selected_documents.append(slug)

    canonical_documents = lease_documents + [slug for slug in selected_documents if slug not in lease_documents]
    primary = _workflow_bridge_slug(launch.get("primary_bridge_id"))
    if primary in canonical_documents:
        return primary
    return canonical_documents[0] if canonical_documents else None


def _workflow_numbered_bridge_file(root: Path, slug: str) -> str | None:
    bridge_dir = (root / "bridge").resolve()
    versions: list[tuple[int, Path]] = []
    for path in bridge_dir.glob(f"{slug}-*.md"):
        match = _BRIDGE_VERSION_RE.fullmatch(path.name)
        if match and match.group("slug") == slug:
            versions.append((int(match.group("version")), path.resolve()))
    if not versions:
        return None
    path = max(versions)[1]
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return None


def _workflow_in_flight(root: Path, report: dict[str, Any]) -> list[dict[str, Any]]:
    launches = _workflow_launch_index(report)
    records: list[dict[str, Any]] = []
    for run in report["history"]["recent_runs"]:
        state = str(run.get("state") or "")
        if state not in {"live", "stale", "unknown"}:
            continue
        dispatch_id = str(run.get("dispatch_id") or "")
        recipient_match = _DISPATCH_RECIPIENT_RE.match(dispatch_id)
        recipient = None
        if recipient_match:
            recipient = f"{recipient_match.group('role')}:{recipient_match.group('harness_id')}"
        bridge_document = None
        work_item_id = None
        launch = launches.get(dispatch_id) if dispatch_id else None
        if launch is not None:
            bridge_document = _workflow_launch_document(launch)
            top_file = _workflow_numbered_bridge_file(root, bridge_document) if bridge_document else None
            if top_file:
                work_item_id = _read_workflow_bridge_metadata(root, top_file)["work_item_id"]
        records.append(
            {
                "dispatch_id": dispatch_id,
                "recipient": recipient,
                "lifecycle_state": state,
                "started_at": run.get("started_at"),
                "age_seconds": run.get("age_seconds"),
                "bridge_document": bridge_document,
                "work_item_id": work_item_id,
            }
        )
    return records


def _workflow_selected_targets(report: dict[str, Any], limit: int) -> tuple[dict[str, list[dict[str, Any]]], bool]:
    selected: dict[str, list[dict[str, Any]]] = {}
    truncated = False
    for role in DISPATCH_ROLES:
        rows = report["topology"]["selected_by_role"].get(role, [])
        summaries = [
            {
                "id": row.get("id"),
                "harness_name": row.get("harness_name"),
                "dispatch_availability": row.get("dispatch_availability"),
            }
            for row in rows
        ]
        selected[role], role_truncated = _bounded_workflow_records(summaries, limit)
        truncated = truncated or role_truncated
    return selected, truncated


def _bound_workflow_categories(
    categories: dict[str, list[dict[str, Any]]], limit: int
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, bool]]:
    bounded: dict[str, list[dict[str, Any]]] = {}
    truncated: dict[str, bool] = {}
    for category, records in categories.items():
        bounded[category], truncated[category] = _bounded_workflow_records(records, limit)
    return bounded, truncated


def _bounded_workflow_records(records: list[dict[str, Any]], limit: int) -> tuple[list[dict[str, Any]], bool]:
    return records[:limit], len(records) > limit


def _format_workflow_record(record: dict[str, Any]) -> str:
    label = str(record.get("title") or record.get("document_name") or record.get("id") or "unknown")
    reason = record.get("reason_code")
    return f"{label} [{reason}]" if reason else label


def _read_json(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"unable to read {path}: {exc}"]
    if not isinstance(payload, dict):
        return {}, [f"{path} is not a JSON object"]
    return payload, []


def _read_jsonl_glob(root: Path, pattern: str, max_records: int) -> tuple[list[dict[str, Any]], list[str]]:
    state_dir = root / STATE_DIR_RELATIVE_PATH
    paths = sorted(state_dir.glob(pattern), key=lambda path: path.stat().st_mtime if path.exists() else 0)
    records: deque[dict[str, Any]] = deque(maxlen=max_records)
    warnings: list[str] = []
    for path in paths:
        file_records, file_warnings = _read_jsonl_tail(path, max_records)
        warnings.extend(file_warnings)
        records.extend(file_records)
    return list(records), warnings


def _read_jsonl_tail(path: Path, max_records: int) -> tuple[list[dict[str, Any]], list[str]]:
    records: deque[dict[str, Any]] = deque(maxlen=max_records)
    warnings: list[str] = []
    if not path.exists():
        return [], []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:
                    warnings.append(f"unable to parse {path}:{line_number}: {exc}")
                    continue
                if isinstance(payload, dict):
                    records.append(payload)
    except OSError as exc:
        warnings.append(f"unable to read {path}: {exc}")
    return list(records), warnings


def _collect_recent_runs(root: Path, *, max_records: int, now: datetime) -> list[dict[str, Any]]:
    runs_dir = root / RUNS_RELATIVE_PATH
    if not runs_dir.exists():
        return []
    runs: dict[str, dict[str, Any]] = {}
    for path in runs_dir.iterdir():
        dispatch_id = _dispatch_id_from_run_file(path)
        if dispatch_id is None:
            continue
        row = runs.setdefault(dispatch_id, {"dispatch_id": dispatch_id})
        row["last_modified_at"] = datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat()
        if path.name.endswith(".stdout.log"):
            row["stdout_bytes"] = path.stat().st_size
        elif path.name.endswith(".stderr.log"):
            row["stderr_bytes"] = path.stat().st_size
        elif path.name.endswith(".exit_code"):
            row["exit_code"] = _read_exit_code(path)
        elif path.name.endswith(".pid"):
            row["pid"] = _read_int(path)
        elif path.name.endswith(PID_CREATE_TIME_SUFFIX):
            row["pid_create_time_epoch"] = _read_float(path)
    for row in runs.values():
        started = _parse_dispatch_started_at(row["dispatch_id"])
        row["started_at"] = started.isoformat() if started is not None else None
        if "exit_code" not in row and _recent_run_live(runs_dir, row):
            row["state"] = "live"
            row["age_seconds"] = None if started is None else max(0.0, (now - started).total_seconds())
        elif "exit_code" not in row:
            row["state"] = "stale"
            row["age_seconds"] = None if started is None else max(0.0, (now - started).total_seconds())
        elif row["exit_code"] == 0:
            row["state"] = "exit_0"
        elif row["exit_code"] is None:
            row["state"] = "unknown"
        else:
            row["state"] = "exit_nonzero"
    return sorted(
        runs.values(),
        key=lambda row: str(row.get("started_at") or row.get("last_modified_at") or ""),
        reverse=True,
    )[:max_records]


def _dispatch_id_from_run_file(path: Path) -> str | None:
    for suffix in (".stdout.log", ".stderr.log", ".exit_code", ".pid", PID_CREATE_TIME_SUFFIX):
        if path.name.endswith(suffix):
            return path.name[: -len(suffix)]
    return None


def _read_int(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _read_float(path: Path) -> float | None:
    try:
        return float(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _read_exit_code(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _pid_alive(pid: int) -> bool:
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return False
    if pid_int <= 0:
        return False
    try:
        import psutil  # noqa: PLC0415

        return bool(psutil.pid_exists(pid_int))
    except Exception:  # noqa: BLE001
        pass
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid_int}", "/NH"],
                capture_output=True,
                text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return False
        return str(pid_int) in result.stdout
    try:
        os.kill(pid_int, 0)
    except OSError:
        return False
    return True


def _pid_create_time_epoch(pid: int) -> float | None:
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return None
    if pid_int <= 0:
        return None
    try:
        import psutil  # noqa: PLC0415

        return float(psutil.Process(pid_int).create_time())
    except Exception:  # noqa: BLE001
        return None


def _pid_create_time_matches(pid: int, expected_epoch: Any) -> bool:
    try:
        expected = float(expected_epoch)
    except (TypeError, ValueError):
        return False
    actual = _pid_create_time_epoch(pid)
    if actual is None:
        return False
    return abs(actual - expected) <= PID_CREATE_TIME_MATCH_TOLERANCE_SECONDS


def _recent_run_live(runs_dir: Path, row: dict[str, Any]) -> bool:
    pid = row.get("pid")
    if not isinstance(pid, int) or isinstance(pid, bool):
        return False
    if not _pid_alive(pid):
        return False
    expected = row.get("pid_create_time_epoch")
    if expected is None:
        expected = _read_float(runs_dir / f"{row['dispatch_id']}{PID_CREATE_TIME_SUFFIX}")
    return _pid_create_time_matches(pid, expected)


def _parse_dispatch_started_at(dispatch_id: str) -> datetime | None:
    match = RUN_TIMESTAMP_RE.match(dispatch_id)
    if match is None:
        return None
    try:
        return datetime.strptime(match.group("stamp"), "%Y-%m-%dT%H-%M-%SZ").replace(tzinfo=UTC)
    except ValueError:
        return None


def _effective_per_cycle_ceiling(selected_by_role: dict[str, list[dict[str, Any]]]) -> dict[str, int | None]:
    ceilings: dict[str, int | None] = {}
    for role in DISPATCH_ROLES:
        rows = selected_by_role.get(role, [])
        values = [row.get("dispatch_max_items") for row in rows if isinstance(row.get("dispatch_max_items"), int)]
        ceilings[role] = sum(values) if values else None
    return ceilings


def _recipient_performance(recipients: dict[str, Any]) -> dict[str, dict[str, Any]]:
    performance: dict[str, dict[str, Any]] = {}
    for key, row in sorted(recipients.items()):
        if not isinstance(row, dict):
            continue
        performance[key] = {
            "pending_count": row.get("pending_count"),
            "raw_pending_count": row.get("raw_pending_count"),
            "selected_count": row.get("selected_count"),
            "last_result": row.get("last_result"),
            "updated_at": row.get("updated_at"),
        }
    return performance


def _failure_taxonomy(
    recipients: dict[str, Any],
    dispatch_failures: list[dict[str, Any]],
    dispatch_suppressions: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    taxonomy: dict[str, Counter[str]] = {
        "last_result": Counter(),
        "failure_class": Counter(),
        "last_launch.reason": Counter(),
        "last_launch.exit_failure_reason": Counter(),
        "jsonl.reason": Counter(),
        "suppression.reason": Counter(),
    }
    for row in recipients.values():
        if not isinstance(row, dict):
            continue
        _count_value(taxonomy["last_result"], row.get("last_result"))
        _count_value(taxonomy["failure_class"], row.get("failure_class"))
        launch = row.get("last_launch") if isinstance(row.get("last_launch"), dict) else {}
        _count_value(taxonomy["last_launch.reason"], launch.get("reason"))
        _count_value(taxonomy["last_launch.exit_failure_reason"], launch.get("exit_failure_reason"))
    for row in dispatch_failures:
        _count_value(taxonomy["jsonl.reason"], row.get("reason") or row.get("failure_reason") or row.get("last_result"))
        _count_value(taxonomy["failure_class"], row.get("failure_class"))
    for row in dispatch_suppressions:
        _count_value(taxonomy["suppression.reason"], row.get("reason") or row.get("suppression_reason"))
    return {field: dict(sorted(counter.items())) for field, counter in taxonomy.items()}


def _count_value(counter: Counter[str], value: Any) -> None:
    if value is None:
        return
    text = str(value).strip()
    if text:
        counter[text] += 1
