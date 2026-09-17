#!/usr/bin/env python3
"""Generate the dashboard bridge view from one current native service observation.

The derived display grants no dispatch, claim, work ownership or terminality.
Artifact content, file timestamps and Git-message heuristics are never inputs.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.bridge.vocabulary import (
    CANONICAL_STATUSES,
    LOYAL_OPPOSITION_ACTIONABLE_STATUSES,
    PRIME_ACTIONABLE_STATUSES,
)
from groundtruth_kb.config import GTConfig, GTConfigError

_CLOSED_DISPOSITIONS = {"committed", "withdrawn", "superseded", "abandoned"}


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp_required")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp_offset_required")
    return parsed


def _count(value: Any) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("nonnegative_count_required")
    return value


def _snapshot_from_report(report: Any) -> dict[str, Any]:
    """Validate complete summary/queue coverage and keep only display fields."""
    if not isinstance(report, dict) or not isinstance(report.get("attempts"), list):
        raise ValueError("attempt_observation_required")
    observed = _timestamp(report.get("observed_at"))
    threads = []
    by_id = {}
    counts: dict[str, int] = {}
    mix: dict[str, int] = {}
    for row in report["attempts"]:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"] or row["id"] in by_id:
            raise ValueError("unique_attempt_required")
        disposition = row.get("disposition")
        if disposition not in {"active", *_CLOSED_DISPOSITIONS}:
            raise ValueError("unknown_disposition")
        version = _count(row.get("head_version"))
        status = row.get("head_status")
        if (version == 0 and status is not None) or (version > 0 and status not in CANONICAL_STATUSES):
            raise ValueError("invalid_head")
        _timestamp(row.get("created_at"))
        for key in ("closed_at", "head_created_at"):
            if row.get(key) is not None:
                _timestamp(row[key])
        for key in ("project_id", "work_item_id", "terminal_commit"):
            if row.get(key) is not None and (not isinstance(row[key], str) or not row[key]):
                raise ValueError("invalid_identity")
        if disposition == "committed" and not row.get("terminal_commit"):
            raise ValueError("commit_identity_required")
        claim = row.get("next_artifact_claim")
        if claim is not None:
            if not isinstance(claim, dict) or disposition != "active":
                raise ValueError("invalid_claim")
            if (
                _count(claim.get("next_version")) != version + 1
                or claim.get("intended_status") not in CANONICAL_STATUSES
            ):
                raise ValueError("invalid_claim_slot")
            if _timestamp(claim.get("expires_at")) <= observed:
                raise ValueError("expired_claim_in_current_observation")
            claim = {key: claim[key] for key in ("next_version", "intended_status", "expires_at")}
        head_time = row.get("head_created_at")
        elapsed = None if head_time is None else (observed - _timestamp(head_time)).total_seconds()
        thread = {
            "document": row["id"],
            "work_item_id": row.get("work_item_id"),
            "project_id": row.get("project_id"),
            "latest_status": status,
            "latest_version": version,
            "disposition": disposition,
            "terminal_commit": row.get("terminal_commit"),
            "created_at": row["created_at"],
            "closed_at": row.get("closed_at"),
            "head_created_at": head_time,
            "age_in_state_minutes": int(elapsed // 60) if elapsed is not None and elapsed >= 0 else None,
            "next_artifact_claim": claim,
            "queue": None,
        }
        threads.append(thread)
        by_id[row["id"]] = thread
        counts[disposition] = counts.get(disposition, 0) + 1
        if disposition == "active" and status is not None:
            mix[status] = mix.get(status, 0) + 1
    actual_claims = sum(row["next_artifact_claim"] is not None for row in threads)
    unfiled = sum(row["disposition"] == "active" and row["latest_status"] is None for row in threads)
    if (
        _count(report.get("active_claim_count")) != actual_claims
        or _count(report.get("unfiled_attempt_count")) != unfiled
    ):
        raise ValueError("inconsistent_counts")
    given_counts = report.get("attempt_counts")
    if not isinstance(given_counts, dict) or {k: _count(v) for k, v in given_counts.items()} != counts:
        raise ValueError("inconsistent_dispositions")
    given_mix = report.get("active_status_mix")
    if (
        not isinstance(given_mix, list)
        or len(given_mix) != len(mix)
        or {item["status"]: _count(item["count"]) for item in given_mix} != mix
    ):
        raise ValueError("inconsistent_status_counts")
    queues = report.get("queues")
    if not isinstance(queues, dict):
        raise ValueError("queues_required")
    for role in ("pb", "lo"):
        queue = queues.get(role)
        if not isinstance(queue, dict) or queue.get("role") != role:
            raise ValueError("role_queue_required")
        for state in ("eligible", "blocked"):
            if not isinstance(queue.get(state), list):
                raise ValueError("queue_observation_required")
            for item in queue[state]:
                if not isinstance(item, dict) or item.get("id") not in by_id:
                    raise ValueError("unknown_queued_attempt")
                thread = by_id[item["id"]]
                if thread["queue"] is not None or thread["disposition"] != "active" or thread["next_artifact_claim"]:
                    raise ValueError("inconsistent_queue")
                # VERIFIED may re-enter LO's queue for a native fresh-verification request.
                statuses = PRIME_ACTIONABLE_STATUSES if role == "pb" else LOYAL_OPPOSITION_ACTIONABLE_STATUSES
                if thread["latest_status"] not in statuses and not (
                    role == "lo" and thread["latest_status"] == "VERIFIED"
                ):
                    raise ValueError("non_dispatchable_queue_entry")
                thread["queue"] = {"role": role, "state": state}
    return {
        "status": "observed",
        "observed_at": report["observed_at"],
        "threads": sorted(threads, key=lambda r: r["document"]),
        "summary": {
            "thread_count": len(threads),
            "active_count": counts.get("active", 0),
            "closed_count": sum(counts.get(key, 0) for key in _CLOSED_DISPOSITIONS),
            "eligible_pb_count": len(queues["pb"]["eligible"]),
            "eligible_lo_count": len(queues["lo"]["eligible"]),
            "blocked_count": sum(len(queues[role]["blocked"]) for role in ("pb", "lo")),
            "active_claim_count": actual_claims,
            "unfiled_count": unfiled,
        },
    }


def _unavailable(code: str) -> dict[str, Any]:
    return {"status": "unavailable", "code": code, "observed_at": None, "threads": [], "summary": None}


def generate_swimlane(project_root: Path, config: GTConfig | None = None) -> dict[str, Any]:
    """One read-only service request; failure never falls back to old files."""
    try:
        config = config or GTConfig.load(config_path=project_root.resolve() / "groundtruth.toml", discover=False)
    except FileNotFoundError:
        return _unavailable("native_authority_not_configured")
    except (OSError, GTConfigError, ValueError):
        return _unavailable("native_authority_configuration_invalid")
    if not config.authority_url:
        return _unavailable("native_authority_not_configured")
    try:
        report = AuthorityClient(config.authority_url, timeout=20).request("GET", "/v1/bridge/state-report")
    except AuthorityClientError as error:
        return _unavailable(
            "invalid_native_bridge_observation" if error.code == "invalid_response" else "native_authority_unavailable"
        )
    try:
        return _snapshot_from_report(report)
    except (ValueError, TypeError, KeyError):
        return _unavailable("invalid_native_bridge_observation")


def _atomic_write_text(target: Path, text: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, target)


def write_swimlane(project_root: Path, out_path: Path, *, config: GTConfig | None = None) -> dict[str, Any]:
    snapshot = generate_swimlane(project_root, config)
    _atomic_write_text(out_path, json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    return snapshot
