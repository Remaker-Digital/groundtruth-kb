"""Serialized bridge/INDEX.md writer - bridge scheduler Slice 3 (WI-3374).

Standalone, stdlib-only module. It wraps every bridge/INDEX.md mutation in a
process-exclusive file lock plus an atomic read-modify-write, so that once the
bridge scheduler raises per-role dispatch concurrency above one worker (Slice 4),
two workers can never interleave bridge/INDEX.md updates and lose an update.

Mutual exclusion is an exclusive lock file created with O_CREAT | O_EXCL - the
same atomic-exclusive-create technique proven in the VERIFIED Slice 2 lease
registry. INDEX writes are atomic via a sibling temp file plus os.replace, which
is atomic on both Windows and POSIX. The module imports no dispatch code; wiring
the writer into the dispatch path is integration work deferred to a later slice.

Implements WI-3374 per bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-001.md
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

# Default bounded-wait acquisition ceiling: an INDEX mutation is a brief,
# expected-to-complete critical section, so 10s is reached only under genuine
# contention or a crashed holder.
DEFAULT_LOCK_TIMEOUT_SECONDS = 10.0

# A lock whose heartbeat has aged past this is reclaimed by the next acquirer.
# INDEX writes are sub-millisecond per the scoping risk note, so 30s is a short
# sanity bound.
DEFAULT_LOCK_TTL_SECONDS = 30.0

# Poll-backoff interval while waiting for a contended lock.
_POLL_INTERVAL_SECONDS = 0.05

_LOCK_FILENAME = "index-writer.lock"

# A waiting acquirer re-reads the lock file to check staleness only this often,
# not on every poll: reading the lock file holds a brief handle that can block
# the holder's release on Windows. Staleness only matters after ttl_seconds, so
# an infrequent re-check is sufficient.
_STALE_RECHECK_SECONDS = 2.0

# _release retries os.remove for up to this long. A concurrent reader can
# briefly block the delete on Windows but holds the handle only microseconds,
# so a retry succeeds almost immediately.
_RELEASE_RETRY_TIMEOUT_SECONDS = 10.0
_RELEASE_RETRY_INTERVAL_SECONDS = 0.01


class IndexWriteLockTimeout(RuntimeError):
    """Raised when the INDEX-write lock cannot be acquired within the timeout."""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _lock_path(state_dir: Path) -> Path:
    return Path(state_dir) / _LOCK_FILENAME


def _read_lock_record(lock_path: Path) -> dict | None:
    """Read and parse the lock file. Return None if absent or unparseable."""
    try:
        raw = Path(lock_path).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
    try:
        record = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    return record if isinstance(record, dict) else None


def _is_stale(record: dict, ttl_seconds: float) -> bool:
    """Return True when the lock record's heartbeat has aged past ttl_seconds.

    record is always a parsed dict here. A dict whose heartbeat_at field is
    missing or not a valid ISO timestamp is treated as stale. A lock file
    whose entire content is unparseable never reaches this function; it is
    handled by _reclaim_malformed_lock via the lock file mtime.
    """
    heartbeat = record.get("heartbeat_at")
    if not isinstance(heartbeat, str):
        return True
    try:
        heartbeat_dt = datetime.fromisoformat(heartbeat)
    except ValueError:
        return True
    if heartbeat_dt.tzinfo is None:
        heartbeat_dt = heartbeat_dt.replace(tzinfo=timezone.utc)
    age_seconds = (datetime.now(timezone.utc) - heartbeat_dt).total_seconds()
    return age_seconds > ttl_seconds


def _try_create_lock(lock_path: Path, token: str) -> bool:
    """Attempt the atomic-exclusive create of the lock file. Return True if won.

    os.open with O_CREAT | O_EXCL is the mutual-exclusion primitive: exactly one
    caller wins the create; every other caller gets FileExistsError.
    """
    record = {
        "lock_token": token,
        "pid": os.getpid(),
        "acquired_at": _utc_now_iso(),
        "heartbeat_at": _utc_now_iso(),
    }
    payload = json.dumps(record).encode("utf-8")
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    try:
        # os.write may write fewer bytes than requested; loop until the full
        # payload lands, so an ordinary short write cannot leave truncated
        # JSON. A crash between this create and a complete write is the
        # residual malformed-lock case, reclaimed by _reclaim_malformed_lock.
        view = memoryview(payload)
        while view:
            view = view[os.write(fd, view) :]
    finally:
        os.close(fd)
    return True


def _reclaim_stale_lock(lock_path: Path, observed_token: object, ttl_seconds: float) -> None:
    """Token-guarded reclaim of a stale lock.

    The lock file is removed only when, on a fresh re-read, it still carries the
    same token observed as stale AND is still stale. This prevents two waiters
    racing to reclaim from deleting a lock a different waiter has since
    freshly acquired (a new acquirer writes a new lock_token).
    """
    confirm = _read_lock_record(lock_path)
    if confirm is None:
        return
    if confirm.get("lock_token") != observed_token:
        return
    if not _is_stale(confirm, ttl_seconds):
        return
    with contextlib.suppress(FileNotFoundError, OSError):
        os.remove(str(lock_path))


def _reclaim_malformed_lock(lock_path: Path, ttl_seconds: float) -> None:
    """Reclaim a present-but-malformed lock file once it has aged past ttl.

    A lock file whose content is not parseable JSON - for example an empty or
    truncated file left by a process that crashed between the exclusive create
    and writing the full payload - carries no heartbeat, so _is_stale cannot
    judge it and _reclaim_stale_lock has no token to guard on. The lock file
    mtime is the fallback staleness signal: the malformed file is removed only
    once it has been on disk longer than ttl_seconds, so a create still in
    progress is never deleted out from under its legitimate owner.

    Distinguishing this case from "file absent" is the correctness fix for the
    NO-GO at bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-004.md: without
    it a single malformed lock blocks every future bridge/INDEX.md writer.
    """
    try:
        mtime = os.stat(str(lock_path)).st_mtime
    except (FileNotFoundError, OSError):
        return  # file absent (or unreadable): nothing to reclaim
    # Re-confirm the file is still malformed. A parseable record now means a
    # fresh acquirer wrote a valid lock; leave that lock intact.
    if _read_lock_record(lock_path) is not None:
        return
    if (time.time() - mtime) <= ttl_seconds:
        return  # too fresh: may be a create still in progress
    with contextlib.suppress(FileNotFoundError, OSError):
        os.remove(str(lock_path))


def _acquire(lock_path: Path, token: str, timeout_seconds: float, ttl_seconds: float) -> None:
    """Bounded-wait acquisition of the exclusive INDEX-write lock.

    Retries the atomic-exclusive create on a short poll-backoff until the lock
    is won or timeout_seconds elapses, at which point IndexWriteLockTimeout is
    raised. A lock found stale (heartbeat aged past ttl_seconds) is reclaimed.
    """
    deadline = time.monotonic() + timeout_seconds
    next_stale_check = 0.0  # 0 -> the first failed attempt checks immediately
    while True:
        if _try_create_lock(lock_path, token):
            return
        now = time.monotonic()
        # Read the lock file to check staleness only periodically: each read
        # holds a brief handle that can block the holder's release on Windows.
        if now >= next_stale_check:
            next_stale_check = now + _STALE_RECHECK_SECONDS
            record = _read_lock_record(lock_path)
            if record is not None:
                if _is_stale(record, ttl_seconds):
                    _reclaim_stale_lock(lock_path, record.get("lock_token"), ttl_seconds)
            else:
                # record is None: the lock file is either absent (the next
                # create attempt simply wins) or present-but-malformed. A
                # malformed lock carries no heartbeat, so it is reclaimed via
                # its mtime once aged past ttl_seconds. _reclaim_malformed_lock
                # self-guards on the absent case.
                _reclaim_malformed_lock(lock_path, ttl_seconds)
        if time.monotonic() >= deadline:
            raise IndexWriteLockTimeout(f"INDEX write lock at {lock_path} not acquired within {timeout_seconds}s")
        time.sleep(_POLL_INTERVAL_SECONDS)


def _release(lock_path: Path, token: str) -> None:
    """Release the lock - remove the lock file only if it still carries our token.

    If the lock was reclaimed as stale and re-acquired by another caller, the
    on-disk token differs and we do not remove that caller's lock.
    """
    record = _read_lock_record(lock_path)
    if record is None or record.get("lock_token") != token:
        return
    # Retry os.remove: on Windows a concurrent reader can transiently block the
    # delete. The reader's handle is held only microseconds, so a retry on a
    # short backoff succeeds. If the bounded retry is somehow exhausted, the
    # heartbeat-TTL stale-reclaim path is the backstop, so we do not raise from
    # this release path.
    deadline = time.monotonic() + _RELEASE_RETRY_TIMEOUT_SECONDS
    while True:
        try:
            os.remove(str(lock_path))
            return
        except FileNotFoundError:
            return
        except OSError:
            if time.monotonic() >= deadline:
                return
            time.sleep(_RELEASE_RETRY_INTERVAL_SECONDS)


def _atomic_write(target: Path, text: str) -> None:
    """Write text to target atomically via a sibling temp file plus os.replace."""
    target = Path(target)
    tmp = target.with_name(f"{target.name}.{uuid.uuid4().hex}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(str(tmp), str(target))
    except BaseException:
        with contextlib.suppress(FileNotFoundError, OSError):
            tmp.unlink()
        raise


@contextlib.contextmanager
def index_write_lock(
    *,
    state_dir: str | Path,
    timeout_seconds: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ttl_seconds: float = DEFAULT_LOCK_TTL_SECONDS,
):
    """Context manager exposing the exclusive INDEX-write lock directly.

    Acquires the lock on enter (bounded-wait, raising IndexWriteLockTimeout on
    timeout) and releases it on exit, including when the body raises. Yields the
    uuid4 lock token. For callers that need a multi-step INDEX mutation; the
    common single-mutation case should use atomic_index_update instead.
    """
    state_dir = Path(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = _lock_path(state_dir)
    token = uuid.uuid4().hex
    _acquire(lock_path, token, float(timeout_seconds), float(ttl_seconds))
    try:
        yield token
    finally:
        _release(lock_path, token)


def atomic_index_update(
    index_path: str | Path,
    mutate,
    *,
    state_dir: str | Path,
    timeout_seconds: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ttl_seconds: float = DEFAULT_LOCK_TTL_SECONDS,
) -> str:
    """Serialized atomic read-modify-write of a bridge index file.

    Acquires the exclusive INDEX-write lock, reads index_path (treating a
    missing file as empty), calls mutate(current_text) -> new_text, writes
    new_text atomically, releases the lock, and returns the written text. The
    entire read-modify-write runs inside the lock, so two workers' updates
    serialize and neither is lost.

    mutate must be a quick in-memory text transform (str -> str). Any expensive
    analysis must happen before calling this function: the lock is held for the
    duration of mutate, and a holder that ages past ttl_seconds can be reclaimed.

    Raises IndexWriteLockTimeout if the lock cannot be acquired in time. If
    mutate raises, the lock is released and index_path is left unchanged.
    """
    index_path = Path(index_path)
    with index_write_lock(state_dir=state_dir, timeout_seconds=timeout_seconds, ttl_seconds=ttl_seconds):
        try:
            current_text = index_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            current_text = ""
        new_text = mutate(current_text)
        if not isinstance(new_text, str):
            raise TypeError("mutate must return a str")
        _atomic_write(index_path, new_text)
        return new_text
