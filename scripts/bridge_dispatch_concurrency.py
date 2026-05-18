"""Per-role bridge dispatch concurrency - bridge scheduler Slice 4 (WI-3375).

Standalone, stdlib-only module. It resolves a per-role dispatch concurrency
limit and tracks in-flight dispatch workers as a bounded pool of atomically
acquired slot files, so the bridge scheduler can replace the flat
DEFAULT_MAX_ITEMS = 2 cap with role-aware capacity (default: loyal-opposition
3, prime-builder 2). The module imports no dispatch code, the Slice 2 lease
registry, or the Slice 3 writer; wiring it into the dispatch path is
integration work deferred to a later slice, so live dispatch behavior is
unchanged by this module's existence.

Each role's in-flight workers are tracked as files
<state_dir>/workers/<role>/slot-<n>.lock for n in 0 .. role_limit(role) - 1.
register_worker walks the slot indices and atomically creates the first free
one with os.open(O_CREAT | O_EXCL | O_WRONLY) - the atomic-exclusive-create
technique proven in the VERIFIED Slice 2 lease registry - so the bounded index
range caps concurrent registration at exactly role_limit(role). A slot whose
heartbeat has aged past its ttl is reclaimed; long-running workers call
refresh_worker to extend their heartbeat.

Implements WI-3375 per bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md
(Loyal Opposition GO at -002).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import contextlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Slot-record schema version. Bumped only on an incompatible record-shape change.
SCHEMA_VERSION = 1

# Default per-role dispatch concurrency limits. The owner's S350 throughput
# directive gave the ranges "LO review workers 2-4, Prime implementation
# workers 1-3"; these defaults sit inside those ranges.
DEFAULT_ROLE_LIMITS = {"loyal-opposition": 3, "prime-builder": 2}

# The canonical scheduler role labels - the only values accepted into a
# filesystem path or an environment-variable name (GO -002 P3-CONSTRAINT).
_CANONICAL_ROLES = frozenset(DEFAULT_ROLE_LIMITS)

# A dispatched worker is a whole counterpart-harness session that may run many
# minutes, so the staleness bound is generous; long workers call refresh_worker.
DEFAULT_WORKER_TTL_SECONDS = 1800.0

# _remove_with_retry retries os.remove for up to this long: on Windows a
# concurrent reader can transiently block the delete (bridge scheduler Slice 3
# concurrency lesson). The handle is held only microseconds, so a short
# backoff succeeds almost immediately.
_REMOVE_RETRY_TIMEOUT_SECONDS = 10.0
_REMOVE_RETRY_INTERVAL_SECONDS = 0.01


class DispatchCapacityExhausted(RuntimeError):
    """Raised by worker_slot when the role is already at its concurrency limit."""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_role(role: str) -> str:
    """Return role unchanged if it is a canonical scheduler role, else raise.

    Only the two canonical scheduler roles (prime-builder, loyal-opposition)
    are accepted. Any other value - empty, containing a path separator or a
    dot, or simply unknown - raises ValueError, so a role can never be
    interpolated into a filesystem path or an environment-variable name
    without being a known-safe constant. Constraining the role set is the
    path-traversal / env-key-injection defense required by the GO -002
    P3-CONSTRAINT; it is lower-risk than sanitizing arbitrary labels.
    """
    if not isinstance(role, str) or not role:
        raise ValueError(f"dispatch role must be a non-empty string, got {role!r}")
    if role not in _CANONICAL_ROLES:
        raise ValueError(
            f"unknown dispatch role {role!r}; expected one of {sorted(_CANONICAL_ROLES)}"
        )
    return role


def _env_override_name(role: str) -> str:
    """Return the GTKB_DISPATCH_CONCURRENCY_<ROLE> override name for a role.

    role must already be validated. The suffix is the role uppercased with
    hyphens replaced by underscores: prime-builder -> PRIME_BUILDER.
    """
    return "GTKB_DISPATCH_CONCURRENCY_" + role.upper().replace("-", "_")


def role_limit(role: str) -> int:
    """Resolve the per-role dispatch concurrency limit.

    The per-role environment override GTKB_DISPATCH_CONCURRENCY_<ROLE> wins
    when it is set to a positive integer; otherwise the DEFAULT_ROLE_LIMITS
    default applies. role is validated first, so an unknown role raises
    ValueError rather than silently resolving a limit.
    """
    role = _validate_role(role)
    override = os.environ.get(_env_override_name(role))
    if override is not None:
        try:
            value = int(override)
        except (TypeError, ValueError):
            value = 0
        if value > 0:
            return value
    return DEFAULT_ROLE_LIMITS[role]


# --- slot paths --------------------------------------------------------------


def _workers_dir(state_dir: Path) -> Path:
    return Path(state_dir) / "workers"


def _role_dir(state_dir: Path, role: str) -> Path:
    # role is validated by every public entry point before reaching here.
    return _workers_dir(state_dir) / role


def _slot_path(state_dir: Path, role: str, slot_index: int) -> Path:
    return _role_dir(state_dir, role) / f"slot-{slot_index}.lock"


# --- slot records ------------------------------------------------------------


def _new_slot_record(role: str, slot_index: int, worker_token: str, ttl_seconds: float) -> dict:
    now = _utc_now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "role": role,
        "slot_index": slot_index,
        "worker_token": worker_token,
        "pid": os.getpid(),
        "acquired_at": now,
        "heartbeat_at": now,
        "ttl_seconds": ttl_seconds,
    }


def _read_slot_record(slot_path: Path) -> dict | None:
    """Read and parse a slot file. Return None if absent or unparseable."""
    try:
        raw = Path(slot_path).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
    try:
        record = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    return record if isinstance(record, dict) else None


def _record_ttl(record: dict) -> float:
    """The slot's own recorded ttl_seconds, falling back to the module default.

    A slot is judged stale against the ttl it was created with, not the
    caller's ttl, so in_flight_count and available_slots - which take no ttl
    argument - stay consistent with register_worker.
    """
    ttl = record.get("ttl_seconds")
    if isinstance(ttl, (int, float)) and not isinstance(ttl, bool) and ttl > 0:
        return float(ttl)
    return DEFAULT_WORKER_TTL_SECONDS


def _heartbeat_age_seconds(record: dict) -> float | None:
    """Seconds since the record's heartbeat, or None if it has no usable one."""
    heartbeat = record.get("heartbeat_at")
    if not isinstance(heartbeat, str):
        return None
    try:
        hb = datetime.fromisoformat(heartbeat)
    except ValueError:
        return None
    if hb.tzinfo is None:
        hb = hb.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - hb).total_seconds()


def _slot_is_stale(record: dict) -> bool:
    """Return True when a parsed slot record's heartbeat has aged past its ttl.

    A record with a missing or unparseable heartbeat is treated as stale - it
    cannot be a healthy worker. A slot file whose entire content is
    unparseable never reaches this function; that case is classified by
    _classify_slot via the slot file mtime.
    """
    age = _heartbeat_age_seconds(record)
    if age is None:
        return True
    return age > _record_ttl(record)


def _classify_slot(slot_path: Path) -> str:
    """Classify a slot file as 'absent', 'fresh', or 'reclaimable'.

    'fresh' - the index is occupied by a worker that must not be disturbed:
    a valid record within its ttl, or a malformed file young enough (by
    mtime) to be a create still in progress.
    'reclaimable' - the index is occupied by an abandoned slot: a valid
    record aged past its ttl, or a malformed file aged past
    DEFAULT_WORKER_TTL_SECONDS. A malformed slot file (a crash between the
    O_EXCL create and a complete write) has no heartbeat, so its mtime is the
    fallback staleness signal - the same correctness fix the Slice 3 INDEX
    writer NO-GO (bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-004.md)
    required for its sibling lock file.
    'absent' - no slot file at the index.
    """
    record = _read_slot_record(slot_path)
    if record is not None:
        return "reclaimable" if _slot_is_stale(record) else "fresh"
    # record is None: the file is absent or present-but-malformed.
    try:
        mtime = os.stat(str(slot_path)).st_mtime
    except (FileNotFoundError, OSError):
        return "absent"
    if (time.time() - mtime) > DEFAULT_WORKER_TTL_SECONDS:
        return "reclaimable"
    return "fresh"


# --- atomic slot file primitives --------------------------------------------


def _write_all(fd: int, payload: bytes) -> None:
    """Write the whole payload to fd.

    os.write may write fewer bytes than requested; loop until the full
    payload lands, so an ordinary short write cannot leave a truncated record
    (bridge scheduler Slice 3 concurrency lesson).
    """
    view = memoryview(payload)
    while view:
        view = view[os.write(fd, view):]


def _try_create_slot(slot_path: Path, record: dict) -> bool:
    """Atomic-exclusive create of a slot file. Return True if this caller won.

    os.open with O_CREAT | O_EXCL is the mutual-exclusion primitive: exactly
    one caller wins the create at a given index; every other caller gets
    FileExistsError.
    """
    payload = json.dumps(record).encode("utf-8")
    try:
        fd = os.open(str(slot_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    try:
        _write_all(fd, payload)
    finally:
        os.close(fd)
    return True


def _remove_with_retry(slot_path: Path) -> bool:
    """Remove a slot file, retrying os.remove on a short backoff.

    On Windows a concurrent reader can transiently block the delete; the
    handle is held only microseconds, so a retry succeeds (bridge scheduler
    Slice 3 lesson). Return True if the file is gone afterward.
    """
    deadline = time.monotonic() + _REMOVE_RETRY_TIMEOUT_SECONDS
    while True:
        try:
            os.remove(str(slot_path))
            return True
        except FileNotFoundError:
            return True
        except OSError:
            if time.monotonic() >= deadline:
                return False
            time.sleep(_REMOVE_RETRY_INTERVAL_SECONDS)


def _atomic_write_record(slot_path: Path, record: dict) -> None:
    """Write record to slot_path atomically via a sibling temp file + os.replace."""
    slot_path = Path(slot_path)
    tmp = slot_path.with_name(f"{slot_path.name}.{uuid.uuid4().hex}.tmp")
    payload = json.dumps(record).encode("utf-8")
    try:
        fd = os.open(str(tmp), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            _write_all(fd, payload)
        finally:
            os.close(fd)
        os.replace(str(tmp), str(slot_path))
    except BaseException:
        with contextlib.suppress(FileNotFoundError, OSError):
            os.remove(str(tmp))
        raise


# --- reclaim -----------------------------------------------------------------


def _reclaim_valid_slot(slot_path: Path, observed_token: object) -> bool:
    """Token-guarded removal of a stale valid slot file. Return True if removed.

    Re-reads the slot and removes it only when it still carries the token
    observed as stale AND is still stale, so two callers racing to reclaim
    cannot delete a slot a third caller has freshly re-registered.
    """
    confirm = _read_slot_record(slot_path)
    if confirm is None:
        return False
    if confirm.get("worker_token") != observed_token:
        return False
    if not _slot_is_stale(confirm):
        return False
    return _remove_with_retry(slot_path)


def _reclaim_malformed_slot(slot_path: Path) -> bool:
    """Mtime-guarded removal of a malformed slot file aged past the default ttl.

    A malformed slot file - left by a process that crashed between the
    O_EXCL create and a complete write - carries no token to guard on, so
    the slot file mtime is the fallback staleness signal. The file is removed
    only once it has been on disk longer than DEFAULT_WORKER_TTL_SECONDS, so
    a create still in progress is never deleted out from under its owner.
    This mirrors the Slice 3 INDEX-writer NO-GO -004 correctness fix.
    """
    try:
        mtime = os.stat(str(slot_path)).st_mtime
    except (FileNotFoundError, OSError):
        return False
    if _read_slot_record(slot_path) is not None:
        return False  # a fresh acquirer wrote a valid record; leave it intact
    if (time.time() - mtime) <= DEFAULT_WORKER_TTL_SECONDS:
        return False  # too fresh: possible create in progress
    return _remove_with_retry(slot_path)


def _reclaim_slot(slot_path: Path) -> bool:
    """Reclaim an abandoned slot file - valid-stale or malformed-stale.

    Return True if the slot file was removed.
    """
    record = _read_slot_record(slot_path)
    if record is not None:
        if not _slot_is_stale(record):
            return False
        return _reclaim_valid_slot(slot_path, record.get("worker_token"))
    return _reclaim_malformed_slot(slot_path)


# --- WorkerSlot --------------------------------------------------------------


class WorkerSlot:
    """A handle to one registered dispatch worker slot.

    Carries the identity needed to refresh or release the slot: the role, the
    bounded slot index, the uuid4 worker token (the release/reclaim guard),
    the state directory, and the ttl. refresh() and release() delegate to the
    module-level refresh_worker / release_worker.
    """

    def __init__(self, *, role: str, slot_index: int, worker_token: str,
                 state_dir: str | Path, ttl_seconds: float):
        self.role = role
        self.slot_index = slot_index
        self.worker_token = worker_token
        self.state_dir = Path(state_dir)
        self.ttl_seconds = float(ttl_seconds)
        self._released = False

    @property
    def slot_id(self) -> str:
        """Stable identifier for this slot: '<role>/slot-<n>'."""
        return f"{self.role}/slot-{self.slot_index}"

    def refresh(self) -> bool:
        return refresh_worker(self)

    def release(self) -> None:
        release_worker(self)

    def __repr__(self) -> str:
        return (f"WorkerSlot(role={self.role!r}, slot_index={self.slot_index}, "
                f"released={self._released})")


# --- public API --------------------------------------------------------------


def register_worker(role: str, *, state_dir: str | Path,
                     ttl_seconds: float = DEFAULT_WORKER_TTL_SECONDS) -> WorkerSlot | None:
    """Atomically claim one of the role's bounded dispatch slots.

    Walks slot indices 0 .. role_limit(role) - 1 and atomically creates the
    first free one. An index occupied by an abandoned slot (a stale heartbeat,
    or a malformed file aged past the ttl) is reclaimed and reused. Returns a
    WorkerSlot on success, or None when the role already holds role_limit
    fresh workers.
    """
    role = _validate_role(role)
    state_dir = Path(state_dir)
    _role_dir(state_dir, role).mkdir(parents=True, exist_ok=True)
    limit = role_limit(role)
    worker_token = uuid.uuid4().hex
    for slot_index in range(limit):
        slot_path = _slot_path(state_dir, role, slot_index)
        record = _new_slot_record(role, slot_index, worker_token, float(ttl_seconds))
        won = _try_create_slot(slot_path, record)
        if not won and _classify_slot(slot_path) == "reclaimable":
            # The index is held by an abandoned slot; reclaim it and retry
            # this index once before moving on.
            _reclaim_slot(slot_path)
            won = _try_create_slot(slot_path, record)
        if won:
            return WorkerSlot(role=role, slot_index=slot_index,
                              worker_token=worker_token, state_dir=state_dir,
                              ttl_seconds=float(ttl_seconds))
    return None


def release_worker(slot: WorkerSlot) -> bool:
    """Free a worker slot - token-guarded.

    Removes the slot file only when it still carries this handle's
    worker_token, so a slot that was reclaimed as stale and re-registered by
    a different worker is never removed by this handle. Return True if this
    call removed the slot file.
    """
    if slot._released:
        return False
    slot_path = _slot_path(slot.state_dir, slot.role, slot.slot_index)
    record = _read_slot_record(slot_path)
    if record is None or record.get("worker_token") != slot.worker_token:
        slot._released = True
        return False
    removed = _remove_with_retry(slot_path)
    slot._released = True
    return removed


def refresh_worker(slot: WorkerSlot) -> bool:
    """Rewrite a worker slot's heartbeat so a long worker is not reclaimed.

    Ownership-guarded: the on-disk slot must still carry this handle's
    worker_token. The updated record is written to a sibling temp file and
    os.replace'd onto the slot file, so a concurrent reader never sees a
    half-written record. Return True if refreshed, False if the slot no
    longer belongs to this handle (released, reclaimed, or never registered).
    """
    if slot._released:
        return False
    slot_path = _slot_path(slot.state_dir, slot.role, slot.slot_index)
    record = _read_slot_record(slot_path)
    if record is None or record.get("worker_token") != slot.worker_token:
        return False
    record["heartbeat_at"] = _utc_now_iso()
    _atomic_write_record(slot_path, record)
    return True


def in_flight_count(role: str, *, state_dir: str | Path) -> int:
    """Count the role's slot indices currently occupied by a fresh worker.

    A slot index counts when its file holds a valid record within ttl, or a
    malformed file young enough to be a create in progress. Stale and
    malformed-stale slots do not count: they are reclaimable, so the index is
    effectively available.
    """
    role = _validate_role(role)
    state_dir = Path(state_dir)
    if not _role_dir(state_dir, role).is_dir():
        return 0
    count = 0
    for slot_index in range(role_limit(role)):
        if _classify_slot(_slot_path(state_dir, role, slot_index)) == "fresh":
            count += 1
    return count


def available_slots(role: str, *, state_dir: str | Path) -> int:
    """Return how many fresh workers the role could still register.

    max(0, role_limit(role) - in_flight_count(role, ...)).
    """
    role = _validate_role(role)
    return max(0, role_limit(role) - in_flight_count(role, state_dir=state_dir))


def reclaim_stale_workers(state_dir: str | Path) -> list[str]:
    """Sweep every role's slot directory and remove abandoned slot files.

    Removes valid records aged past their ttl and malformed files aged past
    DEFAULT_WORKER_TTL_SECONDS. Fresh slots are left untouched. Returns the
    reclaimed slot identifiers ('<role>/slot-<n>'), sorted.
    """
    state_dir = Path(state_dir)
    reclaimed: list[str] = []
    workers_dir = _workers_dir(state_dir)
    if not workers_dir.is_dir():
        return reclaimed
    for role in sorted(_CANONICAL_ROLES):
        role_dir = workers_dir / role
        if not role_dir.is_dir():
            continue
        for slot_path in sorted(role_dir.glob("slot-*.lock")):
            if _classify_slot(slot_path) != "reclaimable":
                continue
            if _reclaim_slot(slot_path):
                reclaimed.append(f"{role}/{slot_path.stem}")
    return reclaimed


@contextlib.contextmanager
def worker_slot(role: str, *, state_dir: str | Path,
                ttl_seconds: float = DEFAULT_WORKER_TTL_SECONDS):
    """Context manager: register a worker slot on enter, release it on exit.

    Raises DispatchCapacityExhausted on enter when the role is already at
    role_limit fresh workers. The slot is released on exit, including when the
    body raises. Yields the WorkerSlot.
    """
    slot = register_worker(role, state_dir=state_dir, ttl_seconds=ttl_seconds)
    if slot is None:
        raise DispatchCapacityExhausted(
            f"dispatch role {role!r} is at capacity ({role_limit(role)} workers)"
        )
    try:
        yield slot
    finally:
        release_worker(slot)
