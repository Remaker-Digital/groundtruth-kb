# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Guard records for intentional dispatcher scheduled-task disables."""

from __future__ import annotations

import datetime as dt
import json
import os
import tempfile
from pathlib import Path
from typing import Any

GUARD_RELATIVE_PARTS = (".gtkb-state", "watchdog", "dispatcher-disable-guard.json")


class DispatcherDisableGuardError(ValueError):
    """Raised when a disable operation lacks bounded guard evidence."""


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(microsecond=0)


def _iso(value: dt.datetime) -> str:
    return value.astimezone(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(value: object) -> dt.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.UTC)
    return parsed.astimezone(dt.UTC)


def default_guard_path(project_root: Path) -> Path:
    """Return the runtime disable-guard record path."""
    return project_root.resolve().joinpath(*GUARD_RELATIVE_PARTS)


def _empty_doc() -> dict[str, Any]:
    return {"schema_version": 1, "records": {}}


def _read_doc(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _empty_doc(), None
    except (OSError, json.JSONDecodeError) as exc:
        return _empty_doc(), f"disable guard state is unreadable: {exc}"
    if not isinstance(payload, dict):
        return _empty_doc(), "disable guard state is not a JSON object"
    records = payload.get("records")
    if not isinstance(records, dict):
        payload["records"] = {}
    payload.setdefault("schema_version", 1)
    return payload, None


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    except OSError as exc:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise DispatcherDisableGuardError(f"disable guard state could not be persisted: {exc}") from exc


def _record_status(record: dict[str, Any] | None, *, path: Path, task_name: str, now: dt.datetime) -> dict[str, Any]:
    base: dict[str, Any] = {
        "path": str(path),
        "task_name": task_name,
        "present": record is not None,
        "active": False,
        "expired": False,
        "status": "absent",
    }
    if record is None:
        return base

    superseded_at = str(record.get("superseded_at") or "").strip()
    expires_at = _parse_iso(record.get("expires_at"))
    owner_quiesce_record = str(record.get("owner_quiesce_record") or "").strip()
    active = bool(owner_quiesce_record) and expires_at is None
    expired = False
    if expires_at is not None:
        expired = expires_at <= now
        active = not expired
    if superseded_at:
        active = False

    base.update(
        {
            "active": active,
            "expired": expired,
            "status": "superseded" if superseded_at else "active" if active else "expired" if expired else "invalid",
            "component": record.get("component"),
            "reason": record.get("reason"),
            "actor": record.get("actor"),
            "created_at": record.get("created_at"),
            "expires_at": record.get("expires_at"),
            "ttl_seconds": record.get("ttl_seconds"),
            "owner_quiesce_record": owner_quiesce_record or None,
            "superseded_at": superseded_at or None,
            "superseded_by": record.get("superseded_by"),
            "supersession_reason": record.get("supersession_reason"),
        }
    )
    return base


def disable_guard_status(
    project_root: Path,
    *,
    task_name: str,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    """Return the effective disable-guard status for one scheduled task."""
    path = default_guard_path(project_root)
    payload, error = _read_doc(path)
    if error is not None:
        return {
            "path": str(path),
            "task_name": task_name,
            "present": path.is_file(),
            "active": False,
            "expired": False,
            "status": "invalid",
            "warning": error,
        }
    records = payload.get("records") if isinstance(payload, dict) else {}
    record = records.get(task_name) if isinstance(records, dict) else None
    if not isinstance(record, dict):
        record = None
    return _record_status(record, path=path, task_name=task_name, now=now or _now_utc())


def validate_guarded_disable_request(
    *,
    task_names: list[str] | tuple[str, ...],
    ttl_seconds: int | None = None,
    owner_quiesce_record: str | None = None,
    reason: str = "",
    actor: str = "prime-builder/codex",
) -> dict[str, Any]:
    """Validate bounded-disable evidence before the platform disable runs."""
    if ttl_seconds is None and not str(owner_quiesce_record or "").strip():
        raise DispatcherDisableGuardError("disable requires --ttl-seconds or --owner-quiesce-record")
    if ttl_seconds is not None and ttl_seconds <= 0:
        raise DispatcherDisableGuardError("disable ttl_seconds must be positive")
    clean_task_names = [str(item).strip() for item in task_names if str(item).strip()]
    if not clean_task_names:
        raise DispatcherDisableGuardError("at least one task name is required")
    clean_reason = str(reason or "").strip()
    if not clean_reason:
        raise DispatcherDisableGuardError("disable reason is required")
    clean_actor = str(actor or "").strip()
    if not clean_actor:
        raise DispatcherDisableGuardError("disable actor is required")
    return {
        "task_names": clean_task_names,
        "ttl_seconds": ttl_seconds,
        "owner_quiesce_record": str(owner_quiesce_record or "").strip() or None,
        "reason": clean_reason,
        "actor": clean_actor,
    }


def record_guarded_disable(
    project_root: Path,
    *,
    task_names: list[str] | tuple[str, ...],
    component: str,
    ttl_seconds: int | None = None,
    owner_quiesce_record: str | None = None,
    reason: str = "",
    actor: str = "prime-builder/codex",
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    """Record bounded disable evidence for one or more scheduled tasks."""
    request = validate_guarded_disable_request(
        task_names=task_names,
        ttl_seconds=ttl_seconds,
        owner_quiesce_record=owner_quiesce_record,
        reason=reason,
        actor=actor,
    )

    now_utc = now or _now_utc()
    expires_at = (
        None if request["ttl_seconds"] is None else _iso(now_utc + dt.timedelta(seconds=int(request["ttl_seconds"])))
    )
    path = default_guard_path(project_root)
    payload, _error = _read_doc(path)
    records = payload.setdefault("records", {})
    if not isinstance(records, dict):
        records = {}
        payload["records"] = records

    for task_name in request["task_names"]:
        records[task_name] = {
            "task_name": task_name,
            "component": component,
            "reason": request["reason"],
            "actor": request["actor"],
            "created_at": _iso(now_utc),
            "expires_at": expires_at,
            "ttl_seconds": request["ttl_seconds"],
            "owner_quiesce_record": request["owner_quiesce_record"],
        }
    payload["updated_at"] = _iso(now_utc)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "guard_path": str(path),
        "records": [
            _record_status(records[task_name], path=path, task_name=task_name, now=now_utc)
            for task_name in request["task_names"]
        ],
    }


def supersede_guarded_disable(
    project_root: Path,
    *,
    task_names: list[str] | tuple[str, ...],
    actor: str,
    reason: str,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    """Supersede existing task guards after a successful governed enable."""
    clean_task_names = list(dict.fromkeys(str(item).strip() for item in task_names if str(item).strip()))
    clean_actor = str(actor or "").strip()
    clean_reason = str(reason or "").strip()
    if not clean_task_names:
        raise DispatcherDisableGuardError("at least one task name is required")
    if not clean_actor:
        raise DispatcherDisableGuardError("supersession actor is required")
    if not clean_reason:
        raise DispatcherDisableGuardError("supersession reason is required")

    path = default_guard_path(project_root)
    payload, error = _read_doc(path)
    if error is not None:
        raise DispatcherDisableGuardError(error)
    records = payload.get("records")
    if not isinstance(records, dict):
        records = {}

    now_utc = now or _now_utc()
    changed = False
    resolved_records: list[dict[str, Any]] = []
    for task_name in clean_task_names:
        record = records.get(task_name)
        if not isinstance(record, dict):
            resolved_records.append(_record_status(None, path=path, task_name=task_name, now=now_utc))
            continue
        if not str(record.get("superseded_at") or "").strip():
            record["superseded_at"] = _iso(now_utc)
            record["superseded_by"] = clean_actor
            record["supersession_reason"] = clean_reason
            changed = True
        resolved_records.append(_record_status(record, path=path, task_name=task_name, now=now_utc))

    if changed:
        payload["updated_at"] = _iso(now_utc)
        _atomic_write_json(path, payload)
    return {
        "ok": True,
        "changed": changed,
        "guard_path": str(path),
        "records": resolved_records,
    }


__all__ = [
    "DispatcherDisableGuardError",
    "default_guard_path",
    "disable_guard_status",
    "record_guarded_disable",
    "supersede_guarded_disable",
    "validate_guarded_disable_request",
]
