"""Substrate-agnostic bridge dispatcher reset and drain (WI-4793)."""

from __future__ import annotations

import contextlib
import hashlib
import importlib
import json
import os
import re
import subprocess
import sys
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
DISPATCH_RUNS_DIR_NAME = "dispatch-runs"
PID_CREATE_TIME_SUFFIX = ".create_time_epoch"
PID_CREATE_TIME_MATCH_TOLERANCE_SECONDS = 1.0
DEFAULT_LEASE_TTL_SECONDS = 300
COMPUTED_QUALITY_RELATIVE = Path(".gtkb-state") / "ops" / "dispatch-quality.json"
KILL_SWITCH_ENV_VAR = "GTKB_NO_CROSS_HARNESS_TRIGGER"
TARGETED_REOFFER_AUDIT_RELATIVE_PATH = Path(".gtkb-state") / "bridge-dispatch-reset-transactions" / "audit.jsonl"

_RECIPIENT_PATTERN = re.compile(r"^(?:prime-builder|loyal-opposition):[A-Za-z0-9][A-Za-z0-9_-]*$")
_DOCUMENT_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

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
        legacy_dispatch = (root / ".gtkb-state" / "cross-harness-trigger").resolve()
        if legacy_dispatch not in dirs and legacy_dispatch.is_dir():
            dirs.append(legacy_dispatch)
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
    stale_dispatch_runs_pruned: int = 0
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
            "stale_dispatch_runs_pruned": self.stale_dispatch_runs_pruned,
            "details": list(self.details),
        }


@dataclass
class TargetedReofferResult:
    """Result of rearming one exact dispatcher recipient/document pair."""

    status: str
    recipient: str
    document: str
    dry_run: bool
    mutated: bool = False
    changed_fields: list[str] = field(default_factory=list)
    state_path: Path | None = None
    before_hash: str | None = None
    after_hash: str | None = None
    audit_path: Path | None = None
    message: str = ""

    def to_json_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "recipient": self.recipient,
            "document": self.document,
            "dry_run": self.dry_run,
            "mutated": self.mutated,
            "changed_fields": list(self.changed_fields),
            "message": self.message,
        }
        if self.state_path is not None:
            payload["state_path"] = str(self.state_path)
        if self.before_hash is not None:
            payload["before_hash"] = self.before_hash
        if self.after_hash is not None:
            payload["after_hash"] = self.after_hash
        if self.audit_path is not None:
            payload["audit_path"] = str(self.audit_path)
        return payload


@dataclass
class DrainResult:
    dry_run: bool
    drained_pids: list[int] = field(default_factory=list)
    terminated_pids: list[int] = field(default_factory=list)
    drain_markers_written: int = 0
    dead_lease_locks_removed: int = 0
    stale_dispatch_runs_pruned: int = 0

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "drained_pids": list(self.drained_pids),
            "terminated_pids": list(self.terminated_pids),
            "drain_markers_written": self.drain_markers_written,
            "dead_lease_locks_removed": self.dead_lease_locks_removed,
            "stale_dispatch_runs_pruned": self.stale_dispatch_runs_pruned,
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


def _hash_json(payload: dict[str, Any]) -> str:
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(rendered).hexdigest()


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\n")


def _load_bridge_lease_registry(project_root: Path) -> Any:
    """Load the canonical scripts-side document lease primitive."""
    candidates = (
        project_root.resolve() / "scripts",
        Path(__file__).resolve().parents[3] / "scripts",
    )
    for scripts_dir in candidates:
        if not (scripts_dir / "bridge_lease_registry.py").is_file():
            continue
        scripts_dir_text = str(scripts_dir)
        if scripts_dir_text not in sys.path:
            sys.path.insert(0, scripts_dir_text)
        return importlib.import_module("bridge_lease_registry")
    raise RuntimeError("canonical bridge lease registry is unavailable")


def _targeted_reoffer_invalid(recipient: str, document: str, message: str, *, dry_run: bool) -> TargetedReofferResult:
    return TargetedReofferResult(
        status="invalid",
        recipient=recipient,
        document=document,
        dry_run=dry_run,
        message=message,
    )


def _targeted_reoffer_from_state(
    state: dict[str, Any],
    *,
    recipient: str,
    document: str,
) -> tuple[list[str], str, str]:
    before_hash = _hash_json(state)
    recipients = state.get("recipients")
    if not isinstance(recipients, dict):
        return [], before_hash, before_hash
    recipient_state = recipients.get(recipient)
    if not isinstance(recipient_state, dict):
        return [], before_hash, before_hash

    changed_fields: list[str] = []
    removed_signature: Any = None
    signature_found = False
    per_document = recipient_state.get("last_dispatched_signatures_by_document")
    if isinstance(per_document, dict) and document in per_document:
        retained = dict(per_document)
        removed_signature = retained.pop(document)
        signature_found = True
        recipient_state["last_dispatched_signatures_by_document"] = retained
        changed_fields.append(f"recipients.{recipient}.last_dispatched_signatures_by_document.{document}")

    thread_reoffers = state.get("thread_reoffers")
    if isinstance(thread_reoffers, dict) and document in thread_reoffers:
        retained_reoffers = dict(thread_reoffers)
        retained_reoffers.pop(document)
        state["thread_reoffers"] = retained_reoffers
        changed_fields.append(f"thread_reoffers.{document}")

    if signature_found and removed_signature is not None:
        for field_name in ("last_dispatched_signature", "signature", "last_suppressed_signature"):
            if recipient_state.get(field_name) == removed_signature:
                recipient_state[field_name] = None
                changed_fields.append(f"recipients.{recipient}.{field_name}")

    after_hash = _hash_json(state)
    return changed_fields, before_hash, after_hash


def targeted_reoffer(
    state_dirs: DispatchStateDirs,
    recipient: str,
    document: str,
    *,
    dry_run: bool = False,
) -> TargetedReofferResult:
    """Rearm one exact recipient/document without disturbing other runtime state."""
    recipient = str(recipient or "").strip()
    document = str(document or "").strip()
    if not _RECIPIENT_PATTERN.fullmatch(recipient):
        return _targeted_reoffer_invalid(
            recipient,
            document,
            "recipient must be an exact prime-builder:<id> or loyal-opposition:<id> key",
            dry_run=dry_run,
        )
    if not _DOCUMENT_PATTERN.fullmatch(document):
        return _targeted_reoffer_invalid(
            recipient,
            document,
            "document must be a kebab-case bridge document slug",
            dry_run=dry_run,
        )

    state_dir = state_dirs.dispatch_dirs[0]
    state_path = state_dir / DISPATCH_STATE_FILENAME
    lease_registry = _load_bridge_lease_registry(state_dirs.project_root)
    if dry_run:
        if lease_registry.is_lease_held(document, state_dir=state_dir):
            return TargetedReofferResult(
                status="lease_held",
                recipient=recipient,
                document=document,
                dry_run=True,
                state_path=state_path,
                message="the exact document has a live dispatcher lease",
            )
        state = _read_json(state_path)
        if state is None:
            return TargetedReofferResult(
                status="not_found",
                recipient=recipient,
                document=document,
                dry_run=True,
                state_path=state_path,
                message="canonical dispatcher state was not found",
            )
        changed_fields, before_hash, after_hash = _targeted_reoffer_from_state(
            state,
            recipient=recipient,
            document=document,
        )
        return TargetedReofferResult(
            status="changed" if changed_fields else "not_found",
            recipient=recipient,
            document=document,
            dry_run=True,
            changed_fields=changed_fields,
            state_path=state_path,
            before_hash=before_hash,
            after_hash=after_hash,
            message="targeted reoffer dry run; no files written",
        )

    handle = lease_registry.acquire_lease(
        document,
        action=f"targeted-reoffer:{recipient}",
        state_dir=state_dir,
    )
    if handle is None:
        return TargetedReofferResult(
            status="lease_held",
            recipient=recipient,
            document=document,
            dry_run=False,
            state_path=state_path,
            message="the exact document has a live dispatcher lease",
        )
    try:
        state = _read_json(state_path)
        if state is None:
            return TargetedReofferResult(
                status="not_found",
                recipient=recipient,
                document=document,
                dry_run=False,
                state_path=state_path,
                message="canonical dispatcher state was not found",
            )
        changed_fields, before_hash, after_hash = _targeted_reoffer_from_state(
            state,
            recipient=recipient,
            document=document,
        )
        if not changed_fields:
            return TargetedReofferResult(
                status="not_found",
                recipient=recipient,
                document=document,
                dry_run=False,
                state_path=state_path,
                before_hash=before_hash,
                after_hash=after_hash,
                message="no matching dispatch signature or thread-reoffer state was found",
            )
        _write_json_atomic(state_path, state, dry_run=False)
        audit_path = state_dirs.project_root / TARGETED_REOFFER_AUDIT_RELATIVE_PATH
        _append_jsonl(
            audit_path,
            {
                "ts": _now_iso(),
                "transaction": "targeted-reoffer",
                "status": "applied",
                "recipient": recipient,
                "document": document,
                "state_path": str(state_path),
                "before_hash": before_hash,
                "after_hash": after_hash,
                "changed_fields": changed_fields,
            },
        )
        return TargetedReofferResult(
            status="changed",
            recipient=recipient,
            document=document,
            dry_run=False,
            mutated=True,
            changed_fields=changed_fields,
            state_path=state_path,
            before_hash=before_hash,
            after_hash=after_hash,
            audit_path=audit_path,
            message="targeted reoffer applied",
        )
    finally:
        lease_registry.release_lease(handle)


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
    if "last_result" in entry and entry.get("last_result") not in ("no_pending", "substrate_mismatch_inert"):
        entry["last_result"] = "no_pending"
        changed = True
    if entry.get("pending_count", 0) != 0:
        entry["pending_count"] = 0
        changed = True
    if entry.get("selected_count", 0) != 0:
        entry["selected_count"] = 0
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


def _dispatch_run_pid_alive(pid: int) -> bool:
    """Best-effort cross-platform liveness probe for a dispatched-worker PID (WI-4861).

    Defined locally to preserve the module dependency direction. Fails closed
    to not-alive on any probe error so a malformed sidecar can never preserve a
    dead record.
    """
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return False
    if pid_int <= 0:
        return False
    try:
        import psutil  # noqa: PLC0415

        return bool(psutil.pid_exists(pid_int))
    except Exception:  # noqa: BLE001 - degrade to the OS-native probe
        pass
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid_int}", "/NH"],
                capture_output=True,
                text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return False
        return str(pid_int) in result.stdout
    try:
        os.kill(pid_int, 0)
    except OSError:
        return False
    return True


def _dispatch_run_pid_create_time(pid: int) -> float | None:
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


def _read_dispatch_run_pid(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _read_dispatch_run_create_time(path: Path) -> float | None:
    try:
        return float(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _dispatch_run_pid_provenance_matches(pid: int, expected_epoch: float | None) -> bool:
    if expected_epoch is None:
        return False
    actual = _dispatch_run_pid_create_time(pid)
    if actual is None:
        return False
    return abs(actual - expected_epoch) <= PID_CREATE_TIME_MATCH_TOLERANCE_SECONDS


def _dispatch_run_ids(runs_dir: Path) -> set[str]:
    suffixes = (
        ".pid",
        ".exit_code",
        ".stdout.log",
        ".stderr.log",
        ".prompt.txt",
        ".input.json",
        ".stdin.log",
        PID_CREATE_TIME_SUFFIX,
    )
    dispatch_ids: set[str] = set()
    for path in runs_dir.iterdir():
        if path.name == "daemon.pid":
            continue
        for suffix in suffixes:
            if path.name.endswith(suffix):
                dispatch_ids.add(path.name[: -len(suffix)])
                break
    return dispatch_ids


def _prune_stale_dispatch_runs(dispatch_dir: Path, *, dry_run: bool) -> int:
    """Prune stale/orphaned dispatch-runs sidecars so the live-worker count is
    accurate after a soft reset (WI-4861).

    A dispatch is stale iff its worker has exited (``<id>.exit_code`` present and
    non-empty) OR its PID is no longer alive (or unparseable). Stale dispatches
    have their full ``<dispatch_id>.*`` sidecar set removed. A genuinely-live
    worker (PID alive, no exit_code) is preserved -- a soft reset must not drop a
    live worker's record. Returns the count of dispatches pruned.
    """
    runs_dir = dispatch_dir / DISPATCH_RUNS_DIR_NAME
    if not runs_dir.is_dir():
        return 0
    pruned = 0
    for dispatch_id in sorted(_dispatch_run_ids(runs_dir)):
        pid_file = runs_dir / f"{dispatch_id}.pid"
        exit_code_file = runs_dir / f"{dispatch_id}.exit_code"
        try:
            exited = exit_code_file.exists() and exit_code_file.stat().st_size > 0
        except OSError:
            exited = False
        alive = False
        if not exited and pid_file.is_file():
            pid = _read_dispatch_run_pid(pid_file)
            expected = _read_dispatch_run_create_time(runs_dir / f"{dispatch_id}{PID_CREATE_TIME_SUFFIX}")
            alive = (
                pid is not None and _dispatch_run_pid_alive(pid) and _dispatch_run_pid_provenance_matches(pid, expected)
            )
        if exited or not alive:
            for suffix in (
                ".pid",
                PID_CREATE_TIME_SUFFIX,
                ".exit_code",
                ".stdout.log",
                ".stderr.log",
                ".prompt.txt",
                ".input.json",
                ".stdin.log",
            ):
                _remove_path(runs_dir / f"{dispatch_id}{suffix}", dry_run=dry_run)
            pruned += 1
    return pruned


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
        pruned = _prune_stale_dispatch_runs(dispatch_dir, dry_run=dry_run)
        result.stale_dispatch_runs_pruned += pruned
        if pruned:
            result.details.append(
                f"pruned {pruned} stale dispatch-runs record(s) in {dispatch_dir / DISPATCH_RUNS_DIR_NAME}"
            )
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


def read_live_dispatch_runs(state_dirs: DispatchStateDirs) -> list[LiveLease]:
    """Return live dispatch-run workers with provenance-verified PID sidecars."""
    workers: list[LiveLease] = []
    for dispatch_dir in state_dirs.dispatch_dirs:
        runs_dir = dispatch_dir / DISPATCH_RUNS_DIR_NAME
        if not runs_dir.is_dir():
            continue
        for dispatch_id in sorted(_dispatch_run_ids(runs_dir)):
            pid_path = runs_dir / f"{dispatch_id}.pid"
            exit_code_path = runs_dir / f"{dispatch_id}.exit_code"
            try:
                if exit_code_path.exists() and exit_code_path.stat().st_size > 0:
                    continue
            except OSError:
                continue
            if not pid_path.is_file():
                continue
            pid = _read_dispatch_run_pid(pid_path)
            expected = _read_dispatch_run_create_time(runs_dir / f"{dispatch_id}{PID_CREATE_TIME_SUFFIX}")
            if pid is None or not _dispatch_run_pid_alive(pid):
                continue
            if not _dispatch_run_pid_provenance_matches(pid, expected):
                continue
            workers.append(LiveLease(doc_slug=dispatch_id, pid=pid, path=pid_path))
    return workers


def read_live_workers(state_dirs: DispatchStateDirs) -> list[LiveLease]:
    """Return all drainable live workers, preferring dispatch-runs provenance."""
    live: list[LiveLease] = []
    seen_pids: set[int] = set()
    for worker in [*read_live_dispatch_runs(state_dirs), *read_live_leases(state_dirs)]:
        if worker.pid in seen_pids:
            continue
        seen_pids.add(worker.pid)
        live.append(worker)
    return live


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


def _lease_record_worker_alive(record: dict[str, Any] | None) -> bool:
    """True when a lease record names a currently-alive worker PID."""
    if not isinstance(record, dict):
        return False
    pid = record.get("pid")
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return False
    return _dispatch_run_pid_alive(pid)


def _prune_dead_lease_locks(dispatch_dir: Path, *, dry_run: bool) -> int:
    """Remove orphaned document-lease locks with no live worker (WI-5066).

    A lease lock is dead residue only when BOTH its heartbeat is stale
    (``_lease_is_live`` is False) AND its recorded worker PID is not alive. A
    lease that is live by heartbeat OR still backed by a live PID is preserved,
    so an in-flight (even hung-but-not-yet-reaped) worker's lease is never
    dropped. Never touches bridge files, PAUTH/project state, or quality
    surfaces. Returns the count of dead lease locks removed.
    """
    lease_dir = dispatch_dir / LEASES_DIR_NAME
    if not lease_dir.is_dir():
        return 0
    now = datetime.now(UTC)
    removed = 0
    for path in sorted(lease_dir.glob("*.lock")):
        record = _parse_lease_record(path)
        heartbeat_live = record is not None and _lease_is_live(record, now=now)
        if heartbeat_live or _lease_record_worker_alive(record):
            continue
        if _remove_path(path, dry_run=dry_run):
            removed += 1
    return removed


def _drain_residue_cleanup(state_dirs: DispatchStateDirs, *, dry_run: bool) -> tuple[int, int]:
    """Prune no-live-worker lease locks and stale dispatch-run sidecars (WI-5066).

    Returns ``(dead_lease_locks_removed, stale_dispatch_runs_pruned)`` summed
    across every dispatcher state dir, so drain leaves the same clean state a
    soft reset does. Reuses ``_prune_stale_dispatch_runs`` (its own PID/exit-code
    liveness rule) and never touches recipient/quiesce state, bridge files,
    PAUTH/project state, or quality surfaces.
    """
    dead_leases = 0
    stale_runs = 0
    for dispatch_dir in state_dirs.dispatch_dirs:
        dead_leases += _prune_dead_lease_locks(dispatch_dir, dry_run=dry_run)
        stale_runs += _prune_stale_dispatch_runs(dispatch_dir, dry_run=dry_run)
    return dead_leases, stale_runs


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
        live = read_live_workers(state_dirs)
        result.drained_pids = [lease.pid for lease in live]
        result.dead_lease_locks_removed, result.stale_dispatch_runs_pruned = _drain_residue_cleanup(
            state_dirs, dry_run=True
        )
        return result

    markers_written = 0
    for dispatch_dir in state_dirs.dispatch_dirs:
        if _write_drain_marker(dispatch_dir, dry_run=False):
            markers_written += 1
    result.drain_markers_written = markers_written

    deadline = clock() + max(0.0, float(timeout_seconds))
    while clock() < deadline:
        live = read_live_workers(state_dirs)
        if not live:
            result.drained_pids = []
            _clear_drain_markers(state_dirs, dry_run=False)
            result.dead_lease_locks_removed, result.stale_dispatch_runs_pruned = _drain_residue_cleanup(
                state_dirs, dry_run=False
            )
            return result
        time.sleep(min(poll_interval, max(0.0, deadline - clock())))

    live = read_live_workers(state_dirs)
    terminated: list[int] = []
    for lease in live:
        terminator(lease.pid)
        terminated.append(lease.pid)
    result.terminated_pids = terminated
    result.drained_pids = []
    _clear_drain_markers(state_dirs, dry_run=False)
    result.dead_lease_locks_removed, result.stale_dispatch_runs_pruned = _drain_residue_cleanup(
        state_dirs, dry_run=False
    )
    return result
