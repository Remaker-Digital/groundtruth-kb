"""Read-only cross-harness diagnostic projection.

The active harness registry supplies the coverage inventory and identity
metadata. Worker role is resolved exclusively from the validated session
document; dispatcher configuration is intentionally not read here.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_ID = "gtkb.harness_diagnostic.v1"
SCHEMA_VERSION = 1
MAX_RECENT_RECORDS = 50
_SAFE_TOOL_NAMES = frozenset({"Read", "Write", "Edit", "Grep", "Glob", "Bash"})
_NUMERIC_USAGE_FIELDS = ("input_tokens", "output_tokens", "total_tokens", "cache_read_tokens", "cache_write_tokens")


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _safe_id(value: Any) -> str | None:
    return _text(value)


def _read_registry(project_root: Path) -> dict[str, Any]:
    from groundtruth_kb.harness_projection import HarnessStateError, read_roles

    try:
        data = read_roles(project_root=project_root)
    except HarnessStateError as exc:
        raise ValueError(f"harness registry unavailable: {exc}") from exc
    return data if isinstance(data, dict) else {}


def _registry_record(project_root: Path, harness_id: str) -> dict[str, Any] | None:
    rows = _read_registry(project_root).get("harnesses")
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and str(row.get("id") or "") == harness_id:
            return row
    return None


def _worker_document(project_root: Path, harness_name: str) -> tuple[Path | None, dict[str, Any] | None]:
    root = project_root / "harness-state" / harness_name
    # WI-6067: the shared per-harness pointer is no longer written or read. The
    # authoritative per-session documents are the only candidates.
    candidates = list((root / "session-envelopes").glob("*.json"))
    loaded: list[tuple[str, Path, dict[str, Any]]] = []
    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict) or data.get("status") != "open":
            continue
        loaded.append((str(data.get("opened_at") or data.get("session_id") or ""), path, data))
    if not loaded:
        return None, None
    _sort_key, path, data = sorted(loaded, key=lambda item: (item[0], item[1].name), reverse=True)[0]
    return path, data


def _document_role(project_root: Path, harness_name: str) -> dict[str, Any]:
    path, document = _worker_document(project_root, harness_name)
    if path is None or document is None:
        return {
            "role": None,
            "source": None,
            "document": None,
            "status": "unavailable",
            "reason": "worker_session_document_missing",
        }
    session_id = _text(document.get("session_id"))
    if session_id is None:
        return {
            "role": None,
            "source": path.as_posix(),
            "document": path.as_posix(),
            "status": "unavailable",
            "reason": "worker_session_document_missing_session_id",
        }
    try:
        from groundtruth_kb.session.envelope import EnvelopeError, resolve_worker_role_provenance

        provenance = resolve_worker_role_provenance(
            project_root,
            current_session_id=session_id,
            harness_name=harness_name,
        )
    except (EnvelopeError, OSError, ValueError) as exc:
        return {
            "role": None,
            "source": path.as_posix(),
            "document": path.as_posix(),
            "status": "unavailable",
            "reason": type(exc).__name__,
        }
    return {
        "role": _text(provenance.get("role")),
        "source": "worker_session_document",
        "document": path.as_posix(),
        "status": "observed",
        "reason": None,
    }


def _configuration_projection(record: dict[str, Any]) -> dict[str, Any]:
    surfaces = record.get("invocation_surfaces")
    surface_keys = sorted(surfaces) if isinstance(surfaces, dict) else []
    return {
        key: record.get(key)
        for key in (
            "id",
            "harness_name",
            "harness_type",
            "status",
            "capabilities_ref",
            "activity_envelope_projection_mode",
            "compact_result_envelope_mode",
            "compact_session_envelope_mode",
            "full_transcript_archive_required",
            "can_receive_dispatch",
            "can_fire_events",
        )
    } | {"invocation_surface_keys": surface_keys}


def _fingerprint(record: dict[str, Any]) -> str:
    material = json.dumps(_configuration_projection(record), sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _model_identity(record: dict[str, Any]) -> str | None:
    surfaces = _mapping(record.get("invocation_surfaces"))
    headless = _mapping(surfaces.get("headless"))
    argv = headless.get("argv")
    if not isinstance(argv, list):
        return None
    for index, value in enumerate(argv):
        if value == "--model" and index + 1 < len(argv):
            return _text(argv[index + 1])
        if isinstance(value, str) and value.startswith("--model="):
            return _text(value.partition("=")[2])
    return None


def _telemetry_projection(record: dict[str, Any]) -> dict[str, Any]:
    correlation = _mapping(record.get("correlation"))
    worker = _mapping(record.get("worker"))
    timing = _mapping(record.get("timing"))
    budget = _mapping(record.get("budget"))
    tool_calls = _mapping(record.get("tool_calls"))
    outcome = _mapping(record.get("outcome"))
    usage = _mapping(record.get("usage"))
    cost = _mapping(record.get("cost"))
    tools = _mapping(tool_calls.get("by_name"))
    safe_tools = {
        name: value
        for name, value in sorted(tools.items())
        if name in _SAFE_TOOL_NAMES and isinstance(value, int) and not isinstance(value, bool) and value >= 0
    }
    return {
        "correlation": {
            key: correlation.get(key)
            for key in (
                "dispatch_id",
                "run_id",
                "bridge_document_id",
                "bridge_thread_id",
                "session_context_id",
                "claim_id",
            )
        }
        | {
            "related_work_item_ids": [
                value for value in correlation.get("related_work_item_ids", []) if isinstance(value, str)
            ]
        },
        "worker": {
            "harness_id": _safe_id(worker.get("harness_id")),
            "harness_name": _safe_id(worker.get("harness_name")),
            "provider": _safe_id(worker.get("provider")),
            "model_id": _safe_id(worker.get("model_id")),
            "model_version": _safe_id(worker.get("model_version")),
        },
        "timing": {key: timing.get(key) for key in ("started_at", "completed_at", "elapsed_ms")},
        "budget": {key: budget.get(key) for key in ("turn_budget", "turns_used")},
        "turns": [
            {
                "index": turn.get("index"),
                "tool_names": [name for name in turn.get("tool_names", []) if name in _SAFE_TOOL_NAMES],
            }
            for turn in record.get("turns", [])
            if isinstance(turn, dict)
        ][:MAX_RECENT_RECORDS],
        "tool_calls": {"total": tool_calls.get("total"), "by_name": safe_tools},
        "outcome": {
            key: outcome.get(key)
            for key in ("stop_reason", "exit_status", "exit_code", "bridge_status", "failure_class")
        },
        "usage": {"coverage": usage.get("coverage"), **{field: usage.get(field) for field in _NUMERIC_USAGE_FIELDS}},
        "cost": {
            "amount": cost.get("amount"),
            "currency": _text(cost.get("currency")),
            "source": _text(cost.get("source")),
        },
    }


def _recent_telemetry(project_root: Path, harness_id: str, harness_name: str) -> list[dict[str, Any]]:
    from groundtruth_kb.shim_dispatch_telemetry import read_dispatch_telemetry_records

    records = read_dispatch_telemetry_records(
        project_root,
        harness_id=harness_id,
        harness_name=harness_name,
        limit=MAX_RECENT_RECORDS,
    )
    return [_telemetry_projection(record) for record in records]


def _field(status: str, *, reason: str | None = None, record_count: int = 0) -> dict[str, Any]:
    return {
        "status": status,
        "coverage": "observed" if status == "observed" else "unavailable",
        "freshness": "local",
        "record_count": record_count,
        "unavailable_reason": reason,
    }


def diagnose_harness(project_root: Path, harness_id: str) -> dict[str, Any]:
    """Return one bounded local diagnostic projection without provider calls."""
    root = project_root.resolve()
    normalized_id = _text(harness_id)
    if normalized_id is None:
        raise ValueError("harness_id must be non-empty")
    record = _registry_record(root, normalized_id)
    if record is None:
        return {
            "schema_id": SCHEMA_ID,
            "schema_version": SCHEMA_VERSION,
            "status": "error",
            "errors": ["harness_not_registered"],
            "harness": {"harness_id": normalized_id},
        }
    harness_name = _text(record.get("harness_name")) or "unknown"
    role = _document_role(root, harness_name)
    _worker_path, worker_document = _worker_document(root, harness_name)
    recent = _recent_telemetry(root, normalized_id, harness_name)
    recent_correlation = _mapping(recent[0].get("correlation")) if recent else {}
    surfaces = record.get("invocation_surfaces")
    surface_keys = sorted(surfaces) if isinstance(surfaces, dict) else []
    status = _text(record.get("status")) or "unknown"
    provider_identity = _text(record.get("provider")) or _text(record.get("harness_type"))
    model_identity = _model_identity(record)
    return {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(),
        "status": "ok" if status == "active" else "partial",
        "errors": [] if status == "active" else ["harness_not_active"],
        "harness": {
            "harness_id": normalized_id,
            "harness_name": harness_name,
            "harness_type": _text(record.get("harness_type")),
            "provider_identity": provider_identity,
            "model_identity": model_identity,
            "lifecycle_status": status,
            "configuration_fingerprint": _fingerprint(record),
            "capabilities": {
                "invocation_surface_keys": surface_keys,
                "can_receive_dispatch": record.get("can_receive_dispatch"),
                "can_fire_events": record.get("can_fire_events"),
            },
        },
        "role": role,
        "correlation": {
            "session_id": _text(worker_document.get("session_id")) if worker_document else None,
            "dispatch_id": _safe_id(recent_correlation.get("dispatch_id")),
            "run_id": _safe_id(recent_correlation.get("run_id")),
            "bridge_document_id": _safe_id(recent_correlation.get("bridge_document_id")),
            "claim_id": _safe_id(recent_correlation.get("claim_id")),
        },
        "checks": {
            "session_document": _field(role["status"], reason=role["reason"]),
            "role_provenance": _field(role["status"], reason=role["reason"]),
            "guard": _field("unavailable", reason="diagnostic_does_not_execute_mutating_guards"),
            "hooks": _field("observed" if record.get("invocation_surfaces") is not None else "unavailable"),
            "tool_surface": _field(
                "observed" if surface_keys else "unavailable",
                reason=None if surface_keys else "tool_surface_unavailable",
            ),
            "adapter_readiness": _field("observed" if record.get("harness_type") else "unavailable"),
        },
        "provider_health": {
            "mode": "local",
            "status": "unavailable",
            "freshness": "local",
            "coverage": "not_requested",
            "unavailable_reason": "provider_request_forbidden",
        },
        "recent_runs": recent,
        "recent_runs_bounds": {"record_limit": MAX_RECENT_RECORDS, "records_returned": len(recent)},
        "parity": {
            "status": "implemented",
            "contract": SCHEMA_ID,
            "coverage_inventory": "active_harness_registry",
            "waiver": None,
        },
        "field_status": {
            "identity": _field("observed"),
            "provider_identity": _field(
                "observed" if provider_identity else "unavailable",
                reason=None if provider_identity else "provider_identity_unavailable",
            ),
            "model_identity": _field(
                "observed" if model_identity else "unavailable",
                reason=None if model_identity else "model_identity_unavailable",
            ),
            "role": _field(role["status"], reason=role["reason"]),
            "telemetry": _field(
                "observed" if recent else "unavailable",
                reason=None if recent else "telemetry_unavailable",
            ),
            "provider_health": _field("unavailable", reason="provider_request_forbidden"),
        },
    }


collect_harness_diagnostic = diagnose_harness
diagnostic_report = diagnose_harness


__all__ = [
    "MAX_RECENT_RECORDS",
    "SCHEMA_ID",
    "SCHEMA_VERSION",
    "collect_harness_diagnostic",
    "diagnose_harness",
    "diagnostic_report",
]
