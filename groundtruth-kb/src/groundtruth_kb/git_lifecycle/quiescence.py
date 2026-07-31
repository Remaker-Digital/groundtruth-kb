"""Bounded dispatcher quiescence leases for Git lifecycle mutations."""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from threading import get_ident
from typing import Any

from groundtruth_kb.git_lifecycle.models import OperationDenied
from groundtruth_kb.git_lifecycle.state import canonical_json

DRAIN_MARKER = "dispatch-drain.json"
MAX_QUIESCENCE_TTL_SECONDS = 300.0

Clock = Callable[[], float]
Sleeper = Callable[[float], None]
WorkerProbe = Callable[[], int]


def _write_marker(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{get_ident()}.tmp")
    temporary.write_text(canonical_json(payload) + "\n", encoding="ascii", newline="\n")
    for attempt in range(20):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 19:
                with suppress(OSError):
                    temporary.unlink()
                raise
            time.sleep(0.01)


def _create_marker_exclusive(path: Path, payload: dict[str, Any]) -> bool:
    """Create the initial marker without a check-then-replace race."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (canonical_json(payload) + "\n").encode("ascii")
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    try:
        os.write(descriptor, data)
        os.fsync(descriptor)
    except BaseException:
        try:
            path.unlink(missing_ok=True)
        finally:
            os.close(descriptor)
        raise
    os.close(descriptor)
    return True


def _read_marker(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OperationDenied("quiescence_missing", "dispatcher quiescence marker is missing") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise OperationDenied("quiescence_malformed", "dispatcher quiescence marker is malformed") from exc
    if not isinstance(payload, dict):
        raise OperationDenied("quiescence_malformed", "dispatcher quiescence marker root must be an object")
    return payload


def _validate_marker(marker: dict[str, Any], *, operation_id: str, now: float) -> None:
    if (
        marker.get("schema_version") != 1
        or marker.get("owner") != "gtkb-git-lifecycle"
        or marker.get("active") is not True
    ):
        raise OperationDenied(
            "quiescence_malformed",
            "dispatcher quiescence marker schema or ownership is invalid",
        )
    issued = marker.get("issued_at_epoch")
    expires = marker.get("expires_at_epoch")
    if (
        not isinstance(issued, (int, float))
        or isinstance(issued, bool)
        or not isinstance(expires, (int, float))
        or isinstance(expires, bool)
        or expires <= issued
        or expires - issued > MAX_QUIESCENCE_TTL_SECONDS
    ):
        raise OperationDenied("quiescence_malformed", "dispatcher quiescence lease bounds are invalid")
    if now >= float(expires):
        raise OperationDenied("quiescence_stale", "dispatcher quiescence lease expired and requires explicit recovery")
    if marker.get("operation_id") != operation_id:
        raise OperationDenied(
            "quiescence_conflict",
            "dispatcher quiescence marker belongs to another current operation",
        )
    if marker.get("phase") != "quiesced" or marker.get("observed_workers") != 0:
        raise OperationDenied("quiescence_not_ready", "dispatcher has not reached a proven quiescent state")


def active_dispatcher_workers(state_dir: Path, *, now: float | None = None) -> int:
    """Count current lease records; malformed worker state fails closed."""
    current = time.time() if now is None else now
    active = 0
    inflight_path = state_dir / "dispatcher-runtime-inflight.lock"
    if inflight_path.exists():
        try:
            inflight = json.loads(inflight_path.read_text(encoding="utf-8"))
            acquired = inflight["acquired_at_epoch"]
            if (
                not isinstance(inflight, dict)
                or inflight.get("schema_version") != 1
                or not isinstance(inflight.get("token"), str)
                or not inflight["token"]
                or not isinstance(acquired, (int, float))
                or isinstance(acquired, bool)
            ):
                raise ValueError("invalid runtime inflight lock")
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise OperationDenied(
                "dispatcher_worker_state_malformed",
                "dispatcher runtime inflight state is malformed; quiescence cannot be inferred",
                path=str(inflight_path),
            ) from exc
        if current < float(acquired) + 600.0:
            active += 1

    leases_dir = state_dir / "leases"
    if leases_dir.is_dir():
        for path in sorted(leases_dir.glob("*.lock")):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                heartbeat_raw = record["heartbeat_at"]
                ttl = record.get("ttl_seconds", 300)
                heartbeat = datetime.fromisoformat(heartbeat_raw)
                if heartbeat.tzinfo is None:
                    heartbeat = heartbeat.replace(tzinfo=UTC)
                if not isinstance(ttl, (int, float)) or isinstance(ttl, bool) or ttl <= 0:
                    raise ValueError("invalid ttl")
            except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise OperationDenied(
                    "dispatcher_worker_state_malformed",
                    "dispatcher worker lease is malformed; quiescence cannot be inferred",
                    path=str(path),
                ) from exc
            if current < heartbeat.timestamp() + float(ttl):
                active += 1

    runs_dir = state_dir / "dispatch-runs"
    if not runs_dir.is_dir():
        return active
    for pid_path in sorted(runs_dir.glob("*.pid")):
        dispatch_id = pid_path.name.removesuffix(".pid")
        exit_path = runs_dir / f"{dispatch_id}.exit_code"
        try:
            pid = int(pid_path.read_text(encoding="utf-8").strip())
            if pid <= 0:
                raise ValueError("invalid pid")
            if exit_path.exists() and exit_path.stat().st_size > 0:
                int(exit_path.read_text(encoding="utf-8").strip())
                continue
            create_time_path = runs_dir / f"{dispatch_id}.create_time_epoch"
            expected_create_time = float(create_time_path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError) as exc:
            raise OperationDenied(
                "dispatcher_worker_state_malformed",
                "dispatcher run PID/provenance state is malformed; quiescence cannot be inferred",
                path=str(pid_path),
            ) from exc
        from groundtruth_kb.bridge_dispatch_reset import (  # noqa: PLC0415 - optional worker probe path
            _dispatch_run_pid_alive,
            _dispatch_run_pid_provenance_matches,
        )

        if _dispatch_run_pid_alive(pid) and _dispatch_run_pid_provenance_matches(pid, expected_create_time):
            active += 1
    return active


def acquire_dispatcher_quiescence(
    state_dir: Path,
    *,
    operation_id: str,
    ttl_seconds: float,
    wait_seconds: float,
    clock: Clock = time.time,
    sleep: Sleeper = time.sleep,
    worker_probe: WorkerProbe | None = None,
) -> dict[str, Any]:
    """Acquire a time-bounded drain marker and wait a bounded time for zero workers."""
    if not operation_id.strip():
        raise OperationDenied("operation_id_invalid", "quiescence requires a non-empty operation id")
    if ttl_seconds <= 0 or ttl_seconds > MAX_QUIESCENCE_TTL_SECONDS:
        raise OperationDenied("quiescence_ttl_invalid", "quiescence TTL is outside the allowed bound")
    if wait_seconds < 0 or wait_seconds >= ttl_seconds:
        raise OperationDenied(
            "quiescence_wait_invalid",
            "quiescence wait must be non-negative and shorter than its TTL",
        )
    marker_path = state_dir / DRAIN_MARKER
    now = clock()
    marker: dict[str, Any] = {
        "schema_version": 1,
        "owner": "gtkb-git-lifecycle",
        "operation_id": operation_id,
        "active": True,
        "phase": "draining",
        "issued_at_epoch": now,
        "expires_at_epoch": now + ttl_seconds,
        "observed_workers": None,
    }
    if not _create_marker_exclusive(marker_path, marker):
        existing = _read_marker(marker_path)
        _validate_marker(existing, operation_id=operation_id, now=now)
        return existing
    deadline = now + wait_seconds
    probe = worker_probe or (lambda: active_dispatcher_workers(state_dir, now=clock()))
    while True:
        workers = probe()
        if not isinstance(workers, int) or isinstance(workers, bool) or workers < 0:
            raise OperationDenied("dispatcher_worker_state_malformed", "dispatcher worker probe returned invalid state")
        marker["observed_workers"] = workers
        if workers == 0:
            marker["phase"] = "quiesced"
            _write_marker(marker_path, marker)
            _validate_marker(marker, operation_id=operation_id, now=clock())
            return marker
        if clock() >= deadline:
            marker["phase"] = "timeout"
            _write_marker(marker_path, marker)
            raise OperationDenied(
                "quiescence_timeout",
                "dispatcher did not quiesce within the bounded wait",
                observed_workers=workers,
                wait_seconds=wait_seconds,
            )
        sleep(min(0.05, max(0.0, deadline - clock())))


def verify_dispatcher_quiescence(state_dir: Path, *, operation_id: str, now: float) -> dict[str, Any]:
    marker = _read_marker(state_dir / DRAIN_MARKER)
    _validate_marker(marker, operation_id=operation_id, now=now)
    return marker


def release_dispatcher_quiescence(
    state_dir: Path,
    *,
    operation_id: str,
    now: float,
    allow_expired: bool = False,
) -> None:
    marker_path = state_dir / DRAIN_MARKER
    marker = _read_marker(marker_path)
    if allow_expired:
        if marker.get("owner") != "gtkb-git-lifecycle" or marker.get("operation_id") != operation_id:
            raise OperationDenied("quiescence_conflict", "cannot release another operation's quiescence marker")
    else:
        _validate_marker(marker, operation_id=operation_id, now=now)
    marker_path.unlink()


def recover_dispatcher_quiescence(state_dir: Path, *, now: float, reason: str) -> dict[str, Any]:
    """Explicitly clear only malformed, expired, or timed-out lifecycle markers."""
    if not reason.strip():
        raise OperationDenied("recovery_reason_required", "quiescence recovery requires a reason")
    marker_path = state_dir / DRAIN_MARKER
    malformed = False
    try:
        marker = _read_marker(marker_path)
    except OperationDenied as exc:
        if exc.code != "quiescence_malformed":
            raise
        marker = {}
        malformed = True
    recoverable = malformed or marker.get("phase") == "timeout"
    expires = marker.get("expires_at_epoch")
    if isinstance(expires, (int, float)) and not isinstance(expires, bool) and now >= float(expires):
        recoverable = True
    if not recoverable:
        raise OperationDenied("quiescence_recovery_denied", "a current active quiescence lease cannot be cleared")
    marker_path.unlink()
    event = {
        "action": "recover_quiescence",
        "at_epoch": now,
        "operation_id": marker.get("operation_id"),
        "reason": reason,
        "recovered_malformed": malformed,
    }
    audit_path = state_dir / "git-lifecycle-quiescence-recovery.jsonl"
    with audit_path.open("a", encoding="ascii", newline="\n") as handle:
        handle.write(canonical_json(event) + "\n")
    return event
