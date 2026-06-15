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
from datetime import UTC, datetime
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


class CrossStorePublishError(RuntimeError):
    """Raised when the ``tafe_canonical`` cross-store publish fails closed.

    Covers a pre-commit divergence (the regenerated INDEX would not match the
    intended write — nothing is committed or published) and INDEX-ahead
    contamination (the live INDEX carries content the authoritative shadow lacks —
    quarantined, never auto-ingested). WI-4510 Phase 3
    (``DCL-INDEX-GENERATED-VIEW-001`` #8 / #11).
    """


# WI-4510 Phase 3 authority-direction tokens (mirrors
# scripts/bridge_authority_cutover.py; the reader fails safe to index_canonical).
_DIRECTION_INDEX_CANONICAL = "index_canonical"
_DIRECTION_TAFE_CANONICAL = "tafe_canonical"


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


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
        heartbeat_dt = heartbeat_dt.replace(tzinfo=UTC)
    age_seconds = (datetime.now(UTC) - heartbeat_dt).total_seconds()
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


def _project_root_from_index(index_path: Path) -> Path:
    """Derive the GT-KB project root from a ``<root>/bridge/INDEX.md`` path.

    Every real caller passes ``<project_root>/bridge/INDEX.md`` (so ``parents[1]``
    is the root); test fixtures build ``<tmp>/bridge/INDEX.md`` the same way.
    """
    return Path(index_path).resolve().parents[1]


def _read_authority_direction(project_root: Path) -> str:
    """Read the bridge authority direction, failing safe to ``index_canonical``.

    The reader lives in ``scripts/bridge_authority_cutover.py`` (the WI-4510
    Phase-3 default-OFF switch). ANY failure — import error, unreadable / malformed
    state, unrecognized value — resolves to ``index_canonical`` so the default
    write path can never be broken or silently flipped by this code
    (``DCL-INDEX-GENERATED-VIEW-001`` #3, safe default).
    """
    try:
        try:
            from scripts.bridge_authority_cutover import read_authority_direction
        except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
            from bridge_authority_cutover import read_authority_direction
        return read_authority_direction(project_root)
    except Exception:  # noqa: BLE001 - the switch must fail safe, never break the writer
        return _DIRECTION_INDEX_CANONICAL


def atomic_index_update(
    index_path: str | Path,
    mutate,
    *,
    state_dir: str | Path,
    timeout_seconds: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ttl_seconds: float = DEFAULT_LOCK_TTL_SECONDS,
    project_root: str | Path | None = None,
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

    WI-4510 Phase 3: under the ``tafe_canonical`` authority direction (a separate
    gate-2 owner decision; default ``index_canonical``), this chokepoint instead
    records the authoritative write in the TAFE shadow first and regenerates a
    byte-faithful INDEX from it, via the cross-store fail-closed publish contract
    (see :func:`_tafe_canonical_publish`). All higher-level writers inherit the
    switch here. Under ``index_canonical`` the path below is byte-identical to the
    pre-flip behavior. ``project_root`` (optional) overrides the root derived from
    ``index_path`` for the direction read + shadow location.
    """
    index_path = Path(index_path)
    with index_write_lock(state_dir=state_dir, timeout_seconds=timeout_seconds, ttl_seconds=ttl_seconds):
        root = Path(project_root) if project_root is not None else _project_root_from_index(index_path)
        if _read_authority_direction(root) == _DIRECTION_TAFE_CANONICAL:
            return _tafe_canonical_publish(index_path, root, mutate)
        try:
            current_text = index_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            current_text = ""
        new_text = mutate(current_text)
        if not isinstance(new_text, str):
            raise TypeError("mutate must return a str")
        _atomic_write(index_path, new_text)
        return new_text


def _reconcile_before_write(index_path: Path, service, is_archived_extra) -> str:
    """Write-start reconcile guard: heal a leftover TAFE-ahead split before writing.

    Runs at the top of every ``tafe_canonical`` write (lock already held). If a
    previous writer committed to the shadow but crashed before publishing, the
    live INDEX is one authoritative write behind; this republishes it from the
    append-only shadow (lossless) so the new write builds on a faithful read
    surface. INDEX-ahead contamination (the INDEX carries content the authoritative
    shadow lacks) is refused — quarantined, never auto-ingested
    (``DCL-INDEX-GENERATED-VIEW-001`` #11). Returns the (possibly repaired) INDEX text.
    """
    from groundtruth_kb.tafe_bridge_ingestion import ARTIFACT_TYPE, assess_publish_state
    from groundtruth_kb.tafe_index_generator import render_index_from_flow_artifacts
    from groundtruth_kb.tafe_index_sync import parse_bridge_index

    try:
        current_text = index_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        current_text = ""
    header = "".join(parse_bridge_index(current_text).preamble_raw)
    instances = service.list_flow_instances()
    artifacts = service.list_flow_artifacts(artifact_type=ARTIFACT_TYPE)
    verdict = assess_publish_state(
        current_text, instances, artifacts, header=header, is_archived_extra=is_archived_extra
    )
    if verdict.index_ahead:
        raise CrossStorePublishError(
            "INDEX-ahead contamination before write: live bridge/INDEX.md carries content the "
            f"authoritative TAFE shadow lacks (missing_in_generated="
            f"{list(verdict.regen_verify.missing_in_generated)}); refusing to build on it. "
            "Run `gt flow publish-reconcile` and resolve the quarantined entry."
        )
    if verdict.needs_republish:
        repaired = render_index_from_flow_artifacts(instances, artifacts, header=header)
        _atomic_write(index_path, repaired)
        return repaired
    return current_text


def _post_publish_self_check(index_path: Path, service, expected_text: str, header: str, is_archived_extra) -> None:
    """In-lock post-publish self-check (``DCL-INDEX-GENERATED-VIEW-001`` #6/#9).

    Re-reads the published INDEX; if it does not equal the already-verified text
    (e.g. a transient FS issue during publish), retries the publish once from the
    in-memory text. Then re-verifies the live INDEX against the committed shadow.
    A residual ``tafe_ahead`` state is left for the next-writer guard /
    ``gt flow publish-reconcile`` (TAFE is durable and lossless to repair — never
    rolled back). An ``index_ahead`` state would be structurally impossible after a
    committed write and is surfaced as a defect.
    """
    from groundtruth_kb.tafe_bridge_ingestion import ARTIFACT_TYPE, assess_publish_state

    try:
        live = index_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        live = ""
    if live != expected_text:
        _atomic_write(index_path, expected_text)
        try:
            live = index_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            live = ""
    instances = service.list_flow_instances()
    artifacts = service.list_flow_artifacts(artifact_type=ARTIFACT_TYPE)
    verdict = assess_publish_state(live, instances, artifacts, header=header, is_archived_extra=is_archived_extra)
    if verdict.index_ahead:
        raise CrossStorePublishError(
            "post-publish self-check found an INDEX-ahead state (structurally impossible after a "
            f"committed tafe_canonical write): missing_in_generated={list(verdict.regen_verify.missing_in_generated)}"
        )


def _tafe_canonical_publish(index_path: Path, project_root: Path, mutate) -> str:
    """The ``tafe_canonical`` cross-store fail-closed publish path (WI-4510 Phase 3).

    Implements the prepare -> single-transaction commit -> atomic publish contract
    from ``bridge/gtkb-wi4510-phase-3-authority-flip-003.md`` (GO at ``-004``).
    Runs entirely inside the INDEX-write lock (held by the caller). Ordering, which
    ``DCL-INDEX-GENERATED-VIEW-001`` #6 asserts: verify the prospective INDEX BEFORE
    the DB commit, commit the affected thread in ONE transaction
    (``insert_bridge_thread_atomic``), then atomically publish the already-verified
    regenerated bytes. A pre-commit divergence fails closed with both stores
    unchanged (#8); the only post-commit failure mode is a bounded, self-healing
    TAFE-ahead window (#9/#10).
    """
    # local import keeps the verify symbol adjacent to the ordering it gates
    from groundtruth_kb.tafe_bridge_ingestion import (
        assess_publish_state,
        build_prospective_shadow,
        make_archived_extra_oracle,
        open_flow_service,
        plan_bridge_thread_writes,
        planned_to_db_kwargs,
    )
    from groundtruth_kb.tafe_index_generator import render_index_from_flow_artifacts
    from groundtruth_kb.tafe_index_sync import parse_bridge_index

    index_path = Path(index_path)
    root = Path(project_root)
    is_archived_extra = make_archived_extra_oracle(root)
    db, service = open_flow_service(root)
    try:
        # write-start reconcile guard, then read the (possibly repaired) surface
        current_text = _reconcile_before_write(index_path, service, is_archived_extra)
        header = "".join(parse_bridge_index(current_text).preamble_raw)

        # the writer's intended INDEX text (same in-memory transform as index_canonical)
        intended_text = mutate(current_text)
        if not isinstance(intended_text, str):
            raise TypeError("mutate must return a str")

        # plan the TAFE mutation from the intended text, project it, regenerate the INDEX
        planned = plan_bridge_thread_writes(intended_text, service)
        prospective_instances, prospective_artifacts = build_prospective_shadow(service, planned)
        prospective_text = render_index_from_flow_artifacts(prospective_instances, prospective_artifacts, header=header)

        # verify BEFORE any commit: fail closed on divergence (no DB write, no FS write)
        verdict = assess_publish_state(
            intended_text,
            prospective_instances,
            prospective_artifacts,
            header=header,
            is_archived_extra=is_archived_extra,
        )
        if not verdict.in_sync:
            rv = verdict.regen_verify
            raise CrossStorePublishError(
                "tafe_canonical write diverges from the intended INDEX; failing closed "
                f"(no DB commit, no INDEX publish): state={verdict.state}, "
                f"missing_in_generated={list(rv.missing_in_generated)}, "
                f"extra_divergent={list(rv.extra_divergent_in_generated)}, "
                f"version_line_mismatches={len(rv.version_line_mismatches)}"
            )

        # single-transaction DB commit (only when the write actually appends rows)
        planned_instances, planned_artifacts = planned_to_db_kwargs(planned)
        if planned_instances or planned_artifacts:
            db.insert_bridge_thread_atomic(
                planned_instances,
                planned_artifacts,
                changed_by="bridge-index-writer-tafe-canonical",
                change_reason="WI-4510 Phase-3 tafe_canonical authoritative bridge write",
            )

        # atomic publish of the already-verified regenerated INDEX (commit precedes publish)
        _atomic_write(index_path, prospective_text)

        # in-lock self-check; leaves a residual TAFE-ahead window for the guard to heal
        _post_publish_self_check(index_path, service, prospective_text, header, is_archived_extra)
        return prospective_text
    finally:
        db.close()


def reconcile_publish(
    project_root: str | Path,
    *,
    timeout_seconds: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ttl_seconds: float = DEFAULT_LOCK_TTL_SECONDS,
) -> dict:
    """Heal a TAFE-ahead publish split (or quarantine INDEX-ahead) under the lock.

    The standalone publish-reconcile entry point behind ``gt flow publish-reconcile``
    and ``scripts/bridge_authority_cutover.py reconcile``. Acquires the INDEX-write
    lock, compares the live INDEX to the authoritative shadow, and:

    - ``in_sync`` -> no-op;
    - ``tafe_ahead`` -> republish INDEX from the append-only shadow (lossless,
      idempotent: a second run is ``in_sync``);
    - ``index_ahead`` -> refuse to auto-apply; report a repair-required defect.

    Returns a JSON-serializable verdict dict. ``DCL-INDEX-GENERATED-VIEW-001`` #10/#11.
    """
    from groundtruth_kb.tafe_bridge_ingestion import (
        ARTIFACT_TYPE,
        assess_publish_state,
        make_archived_extra_oracle,
        open_flow_service,
    )
    from groundtruth_kb.tafe_index_generator import render_index_from_flow_artifacts
    from groundtruth_kb.tafe_index_sync import parse_bridge_index

    root = Path(project_root)
    index_path = root / "bridge" / "INDEX.md"
    state_dir = root / ".gtkb-state" / "bridge-index-writer"
    is_archived_extra = make_archived_extra_oracle(root)
    with index_write_lock(state_dir=state_dir, timeout_seconds=timeout_seconds, ttl_seconds=ttl_seconds):
        try:
            current_text = index_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            current_text = ""
        header = "".join(parse_bridge_index(current_text).preamble_raw)
        db, service = open_flow_service(root)
        try:
            instances = service.list_flow_instances()
            artifacts = service.list_flow_artifacts(artifact_type=ARTIFACT_TYPE)
            verdict = assess_publish_state(
                current_text, instances, artifacts, header=header, is_archived_extra=is_archived_extra
            )
            repaired = False
            if verdict.needs_republish:
                regenerated = render_index_from_flow_artifacts(instances, artifacts, header=header)
                _atomic_write(index_path, regenerated)
                repaired = True
            return {
                "state": verdict.state,
                "repaired": repaired,
                "index_ahead": verdict.index_ahead,
                "index_path": str(index_path),
                "regen_verify": verdict.regen_verify.as_dict(),
            }
        finally:
            db.close()
