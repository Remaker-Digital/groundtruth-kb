"""Substrate-agnostic bridge dispatcher reset and drain (WI-4793)."""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DISPATCH_STATE_FILENAME = "dispatch-state.json"
QUIESCE_STATE_FILENAME = "quiesce-state.json"
RESET_GUARD_FILENAME = "dispatch-state-reset.lock"
DRAIN_MARKER_FILENAME = "dispatch-drain.json"
LEASES_DIR_NAME = "leases"
PROVENANCE_LEDGER_FILENAME = "dispatch-provenance.json"
KILL_SWITCH_ENV_VAR = "GTKB_NO_CROSS_HARNESS_TRIGGER"
DEFAULT_LEASE_TTL_SECONDS = 300
COMPUTED_QUALITY_RELATIVE = Path(".gtkb-state") / "ops" / "dispatch-quality.json"

TerminateFn = Callable[[int], None]
NowFn = Callable[[], float]


@dataclass(frozen=True)
class DispatchStateDirs:
    """Dispatcher state directories under a GT-KB project root."""

    project_root: Path
    dispatch_dirs: tuple[Path, ...]
    provenance_dir: Path

    @classmethod
    def resolve(cls, project_root: Path, *, state_dir: Path | None = None) -> DispatchStateDirs:
        root = project_root.resolve()
        primary = (state_dir or root / ".gtkb-state" / "bridge-poller").resolve()
        dirs: list[Path] = [primary]
        trigger = (root / ".gtkb-state" / "cross-harness-trigger").resolve()
        if trigger not in dirs and trigger.is_dir():
            dirs.append(trigger)
        provenance = (root / ".gtkb-state" / "ops" / "dispatch-provenance").resolve()
        return cls(project_root=root, dispatch_dirs=tuple(dirs), provenance_dir=provenance)


@dataclass
class ResetResult:
    dry_run: bool
    recipients_cleared: int = 0
    quiesce_records_cleared: int = 0
    reset_guards_removed: int = 0
    lease_locks_removed: int = 0
    provenance_ledgers_removed: int = 0
    quality_surfaces_cleared: int = 0
    details: list[str] = field(default_factory=list)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "recipients_cleared": self.recipients_cleared,
            "quiesce_records_cleared": self.quiesce_records_cleared,
            "reset_guards_removed": self.reset_guards_removed,
            "lease_locks_removed": self.lease_locks_removed,
            "provenance_ledgers_removed": self.provenance_ledgers_removed,
            "quality_surfaces_cleared": self.quality_surfaces_cleared,
            "details": list(self.details),
        }


@dataclass
class DrainResult:
    dry_run: bool
    drained_pids: list[int] = field(default_factory=list)
    terminated_pids: list[int] = field(default_factory=list)
    drain_markers_written: int = 0

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "drained_pids": list(self.drained_pids),
            "terminated_pids": list(self.terminated_pids),
            "drain_markers_written": self.drain_markers_written,
        }


@dataclass(frozen=True)
class LiveLease:
    doc_slug: str
    pid: int
    path: Path


def is_drain_marker_active(state_dir: Path) -> bool:
    """Return True when ``dispatch-drain.json`` is active under ``state_dir``."""
    data = _read_json(state_dir / DRAIN_MARKER_FILENAME)
    if data is None:
        return False
    return bool(data.get("active"))


def dispatch_is_draining(project_root: Path, state_dir: Path) -> bool:
    """True when any known dispatcher state dir has an active drain marker."""
    checked: set[str] = set()
    candidates = [state_dir.resolve()]
    alt = (project_root / ".gtkb-state" / "cross-harness-trigger").resolve()
    if alt.is_dir():
        candidates.append(alt)
    for candidate in candidates:
        key = str(candidate)
        if key in checked:
            continue
        checked.add(key)
        if is_drain_marker_active(candidate):
            return True
    return False


def terminate_pid_tree(pid: int) -> None:
    """Best-effort termination of a dispatch-run pid and its descendants."""
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return
    if pid_int <= 0:
        return
    if os.name == "nt":
        with contextlib.suppress(Exception):
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid_int)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
    else:
        with contextlib.suppress(Exception):
            import signal

            os.killpg(os.getpgid(pid_int), signal.SIGKILL)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _write_json_atomic(path: Path, payload: dict[str, Any], *, dry_run: bool) -> bool:
    if dry_run:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    unique = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
    tmp = path.with_suffix(path.suffix + f".{unique}.tmp")
    try:
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, path)
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
    return True


def _clear_recipient_entry(entry: dict[str, Any]) -> bool:
    if not isinstance(entry, dict):
        return False
    changed = False
    if entry.get("failure_count", 0) != 0:
        entry["failure_count"] = 0
        changed = True
    if entry.get("circuit_breaker_tripped") is not False:
        entry["circuit_breaker_tripped"] = False
        changed = True
    for key in (
        "circuit_breaker_tripped_at",
        "circuit_breaker_half_open",
        "last_launch",
        "previous_launch_failed_logged_at",
        "previous_launch_failed",
    ):
        if key in entry:
            entry.pop(key, None)
            changed = True
    for key in ("signature", "last_dispatched_signature", "last_suppressed_signature"):
        if entry.get(key) is not None:
            entry[key] = None
            changed = True
    if changed:
        entry["updated_at"] = _now_iso()
    return changed


def _clear_dispatch_state(path: Path, *, dry_run: bool) -> int:
    state = _read_json(path)
    if state is None:
        return 0
    recipients = state.get("recipients")
    if not isinstance(recipients, dict):
        return 0
    cleared = 0
    for entry in recipients.values():
        if isinstance(entry, dict) and _clear_recipient_entry(entry):
            cleared += 1
    if cleared and not dry_run:
        _write_json_atomic(path, state, dry_run=False)
    return cleared


def _clear_quiesce_state(path: Path, *, dry_run: bool) -> int:
    state = _read_json(path)
    if state is None:
        return 0
    records = state.get("records")
    if not isinstance(records, dict) or not records:
        return 0
    count = len(records)
    if dry_run:
        return count
    state["records"] = {}
    _write_json_atomic(path, state, dry_run=False)
    return count


def _remove_path(path: Path, *, dry_run: bool) -> bool:
    if not path.exists():
        return False
    if dry_run:
        return True
    try:
        path.unlink()
    except OSError:
        return False
    return True


def _clear_lease_locks(state_dir: Path, *, dry_run: bool) -> int:
    lease_dir = state_dir / LEASES_DIR_NAME
    if not lease_dir.is_dir():
        return 0
    removed = 0
    for path in sorted(lease_dir.glob("*.lock")):
        if _remove_path(path, dry_run=dry_run):
            removed += 1
    return removed


def _clear_provenance_ledger(provenance_dir: Path, *, dry_run: bool) -> int:
    ledger = provenance_dir / PROVENANCE_LEDGER_FILENAME
    if _remove_path(ledger, dry_run=dry_run):
        return 1
    return 0


def _clear_computed_quality_surfaces(state_dirs: DispatchStateDirs, *, dry_run: bool) -> int:
    quality_path = (state_dirs.project_root / COMPUTED_QUALITY_RELATIVE).resolve()
    if _remove_path(quality_path, dry_run=dry_run):
        return 1
    return 0


def soft_reset(state_dirs: DispatchStateDirs, *, dry_run: bool = False) -> ResetResult:
    result = ResetResult(dry_run=dry_run)
    for dispatch_dir in state_dirs.dispatch_dirs:
        dispatch_state = dispatch_dir / DISPATCH_STATE_FILENAME
        if dispatch_state.is_file():
            cleared = _clear_dispatch_state(dispatch_state, dry_run=dry_run)
            result.recipients_cleared += cleared
            if cleared:
                result.details.append(f"cleared {cleared} recipient(s) in {dispatch_state}")
        quiesce_state = dispatch_dir / QUIESCE_STATE_FILENAME
        if quiesce_state.is_file():
            cleared_q = _clear_quiesce_state(quiesce_state, dry_run=dry_run)
            result.quiesce_records_cleared += cleared_q
            if cleared_q:
                result.details.append(f"cleared {cleared_q} quiesce record(s) in {quiesce_state}")
        guard = dispatch_dir / RESET_GUARD_FILENAME
        if _remove_path(guard, dry_run=dry_run):
            result.reset_guards_removed += 1
        result.lease_locks_removed += _clear_lease_locks(dispatch_dir, dry_run=dry_run)
    result.provenance_ledgers_removed += _clear_provenance_ledger(state_dirs.provenance_dir, dry_run=dry_run)
    return result


def hard_reset(state_dirs: DispatchStateDirs, *, dry_run: bool = False) -> ResetResult:
    result = soft_reset(state_dirs, dry_run=dry_run)
    result.quality_surfaces_cleared = _clear_computed_quality_surfaces(state_dirs, dry_run=dry_run)
    if result.quality_surfaces_cleared:
        result.details.append("cleared reserved computed-quality surface(s)")
    return result


def _parse_lease_record(path: Path) -> dict[str, Any] | None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return record if isinstance(record, dict) else None


def _lease_is_live(record: dict[str, Any], *, now: datetime) -> bool:
    heartbeat_raw = record.get("heartbeat_at")
    if not isinstance(heartbeat_raw, str):
        return True
    try:
        heartbeat = datetime.fromisoformat(heartbeat_raw)
    except ValueError:
        return True
    if heartbeat.tzinfo is None:
        heartbeat = heartbeat.replace(tzinfo=UTC)
    ttl_raw = record.get("ttl_seconds", DEFAULT_LEASE_TTL_SECONDS)
    try:
        ttl = float(ttl_raw)
    except (TypeError, ValueError):
        ttl = float(DEFAULT_LEASE_TTL_SECONDS)
    return (now - heartbeat).total_seconds() <= ttl


def read_live_leases(state_dirs: DispatchStateDirs) -> list[LiveLease]:
    now = datetime.now(UTC)
    leases: list[LiveLease] = []
    for dispatch_dir in state_dirs.dispatch_dirs:
        lease_dir = dispatch_dir / LEASES_DIR_NAME
        if not lease_dir.is_dir():
            continue
        for path in sorted(lease_dir.glob("*.lock")):
            record = _parse_lease_record(path)
            if record is None or not _lease_is_live(record, now=now):
                continue
            pid = record.get("pid")
            if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
                continue
            leases.append(
                LiveLease(
                    doc_slug=str(record.get("doc_slug", path.stem)),
                    pid=pid,
                    path=path,
                )
            )
    return leases


def _write_drain_marker(state_dir: Path, *, dry_run: bool) -> bool:
    payload = {
        "active": True,
        "started_at": _now_iso(),
        "reason": "gt bridge dispatch drain",
    }
    path = state_dir / DRAIN_MARKER_FILENAME
    if dry_run:
        return True
    return _write_json_atomic(path, payload, dry_run=False)


def _clear_drain_markers(state_dirs: DispatchStateDirs, *, dry_run: bool) -> None:
    for dispatch_dir in state_dirs.dispatch_dirs:
        _remove_path(dispatch_dir / DRAIN_MARKER_FILENAME, dry_run=dry_run)


def drain(
    state_dirs: DispatchStateDirs,
    *,
    timeout_seconds: float = 60.0,
    dry_run: bool = False,
    now_fn: NowFn | None = None,
    terminate_fn: TerminateFn | None = None,
    poll_interval: float = 0.05,
) -> DrainResult:
    clock = now_fn or time.time
    terminator = terminate_fn or terminate_pid_tree
    result = DrainResult(dry_run=dry_run)
    if dry_run:
        live = read_live_leases(state_dirs)
        result.drained_pids = [lease.pid for lease in live]
        return result

    markers_written = 0
    for dispatch_dir in state_dirs.dispatch_dirs:
        if _write_drain_marker(dispatch_dir, dry_run=False):
            markers_written += 1
    result.drain_markers_written = markers_written

    deadline = clock() + max(0.0, float(timeout_seconds))
    while clock() < deadline:
        live = read_live_leases(state_dirs)
        if not live:
            result.drained_pids = []
            _clear_drain_markers(state_dirs, dry_run=False)
            return result
        time.sleep(min(poll_interval, max(0.0, deadline - clock())))

    live = read_live_leases(state_dirs)
    terminated: list[int] = []
    for lease in live:
        terminator(lease.pid)
        terminated.append(lease.pid)
    result.terminated_pids = terminated
    result.drained_pids = []
    _clear_drain_markers(state_dirs, dry_run=False)
    return result
