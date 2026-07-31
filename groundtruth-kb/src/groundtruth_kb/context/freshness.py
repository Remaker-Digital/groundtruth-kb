"""Source-of-truth freshness decisions shared by context consumers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

RETIRED_AUTHORITY_PATHS = {
    "bridge/INDEX.md",
    "harness-state/role-assignments.json",
}
HIGH_CHURN_CLASSES = {
    "active_claims",
    "bridge_queue",
    "dispatcher_workers",
    "leases",
    "project_status",
    "runtime_health",
    "work_item_status",
}
LOW_CHURN_REQUIRED_FIELDS = {
    "source_id",
    "authority_class",
    "source_version_or_hash",
    "churn_class",
    "generated_at",
    "ttl_seconds",
    "bounded_usage_context",
    "live_query_route",
    "recovery_route",
}


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def evaluate_extract(record: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    current_time = (now or datetime.now(UTC)).astimezone(UTC)
    reasons: list[str] = []
    source_path = str(record.get("source_path") or "")
    churn_class = str(record.get("churn_class") or "")
    recovery_route = record.get("recovery_route")

    if source_path in RETIRED_AUTHORITY_PATHS:
        reasons.append("retired-authority")
    if churn_class in HIGH_CHURN_CLASSES and record.get("embedded_content") is not None:
        reasons.extend(["high-churn", "live-query-only"])

    if churn_class not in HIGH_CHURN_CLASSES:
        missing = sorted(field for field in LOW_CHURN_REQUIRED_FIELDS if record.get(field) in {None, ""})
        reasons.extend(f"missing:{field}" for field in missing)
        generated_at = _parse_timestamp(record.get("generated_at"))
        ttl_seconds = record.get("ttl_seconds")
        if generated_at is None:
            if "missing:generated_at" not in reasons:
                reasons.append("unverifiable:generated_at")
        elif not isinstance(ttl_seconds, int) or ttl_seconds < 1:
            if "missing:ttl_seconds" not in reasons:
                reasons.append("unverifiable:ttl_seconds")
        elif current_time > generated_at + timedelta(seconds=ttl_seconds):
            reasons.append("expired")

    if record.get("conflict") is True:
        reasons.append("conflict")
    if reasons and not recovery_route:
        reasons.append("missing:recovery_route")

    eligible = not reasons
    return {
        "eligible_as_current": eligible,
        "status": "current" if eligible else "recovery_required",
        "reasons": reasons,
        "live_query_route": record.get("live_query_route"),
        "recovery_route": recovery_route,
    }


def _low_churn_fixture(now: datetime) -> dict[str, Any]:
    return {
        "source_id": "GOV-EXAMPLE-001",
        "source_path": "groundtruth.db:current_specifications",
        "authority_class": "stated",
        "source_version_or_hash": "v1",
        "churn_class": "low",
        "generated_at": now.isoformat(),
        "ttl_seconds": 120,
        "bounded_usage_context": "session_start",
        "live_query_route": "gt spec show GOV-EXAMPLE-001",
        "recovery_route": "gt spec show GOV-EXAMPLE-001",
        "embedded_content": {"title": "Example"},
    }


def run_contract_fixtures(*, now: datetime | None = None) -> dict[str, Any]:
    current_time = now or datetime.now(UTC)
    retired_results = [
        evaluate_extract({**_low_churn_fixture(current_time), "source_path": path}, now=current_time)
        for path in sorted(RETIRED_AUTHORITY_PATHS)
    ]
    high_churn_results = [
        evaluate_extract(
            {
                "source_id": churn_class,
                "source_path": "groundtruth.db",
                "churn_class": churn_class,
                "embedded_content": {"state": "active"},
                "live_query_route": "gt status",
                "recovery_route": "gt status",
            },
            now=current_time,
        )
        for churn_class in sorted(HIGH_CHURN_CLASSES)
    ]
    complete = _low_churn_fixture(current_time)
    complete_result = evaluate_extract(complete, now=current_time)
    missing_field_results = []
    for field in sorted(LOW_CHURN_REQUIRED_FIELDS):
        incomplete = dict(complete)
        incomplete.pop(field)
        missing_field_results.append(evaluate_extract(incomplete, now=current_time))
    expired = {**complete, "generated_at": (current_time - timedelta(seconds=121)).isoformat()}
    conflict = {**complete, "conflict": True}
    expired_result = evaluate_extract(expired, now=current_time)
    conflict_result = evaluate_extract(conflict, now=current_time)

    assertions = [
        {
            "id": "FRESH-V4-A1",
            "status": "PASS" if all("retired-authority" in item["reasons"] for item in retired_results) else "FAIL",
            "evidence": retired_results,
        },
        {
            "id": "FRESH-V4-A2",
            "status": "PASS"
            if all(
                {"high-churn", "live-query-only"} <= set(item["reasons"]) and item["eligible_as_current"] is False
                for item in high_churn_results
            )
            else "FAIL",
            "evidence": high_churn_results,
        },
        {
            "id": "FRESH-V4-A3",
            "status": "PASS"
            if complete_result["eligible_as_current"]
            and all(item["eligible_as_current"] is False for item in missing_field_results)
            else "FAIL",
            "evidence": {"complete": complete_result, "missing_fields": missing_field_results},
        },
        {
            "id": "FRESH-V4-A4",
            "status": "PASS"
            if "expired" in expired_result["reasons"]
            and "conflict" in conflict_result["reasons"]
            and expired_result["status"] == conflict_result["status"] == "recovery_required"
            else "FAIL",
            "evidence": {"expired": expired_result, "conflict": conflict_result},
        },
    ]
    return {
        "schema_version": 1,
        "status": "PASS" if all(item["status"] == "PASS" for item in assertions) else "FAIL",
        "assertions": assertions,
    }
