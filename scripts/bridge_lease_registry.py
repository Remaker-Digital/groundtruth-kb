# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Per-document advisory lease registry for the GT-KB bridge scheduler.

Slice 2 of the bridge scheduler program (WI-3373; GO at
``bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-002.md``). Provides an
atomic, file-backed, per-document lease so that no two bridge workers process
or write a verdict for the same bridge document concurrently.

A lease is a small JSON file at ``<state_dir>/leases/<doc-slug>.lock``.
Acquisition is atomic via ``os.open`` with ``O_CREAT | O_EXCL``: exactly one
caller wins the create, and the rest observe ``FileExistsError``. A held lease
is *fresh* until its heartbeat ages past ``ttl_seconds``; a stale lease is
reclaimable. Every delete path -- ``release_lease`` and stale reclamation --
is guarded by the lease token, so a worker can never delete a lease that went
stale, was reclaimed, and is now held by a different worker.

Slice 2 is the standalone primitive only. The cross-harness trigger and the
single-harness dispatcher consume this registry in a later scheduler slice;
this module imports nothing from the dispatch path and runs no polling loop.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

LEASE_SCHEMA_VERSION = 1
DEFAULT_LEASE_TTL_SECONDS = 300

_LEASE_DIR_NAME = "leases"
_LEASE_SUFFIX = ".lock"
# Kebab-case bridge-document slug: lowercase alphanumeric segments joined by
# single hyphens. Rejects path separators, dots, ``..``, drive letters,
# whitespace, and uppercase -- the lease filename is derived from the slug, so
# this pattern is the path-traversal defense.
_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# ``os.O_BINARY`` exists only on Windows; 0 is a no-op flag on POSIX. Opening
# the exclusive-create fd in binary mode keeps newline handling out of the
# fd layer so the JSON payload is written byte-for-byte.
_O_BINARY = getattr(os, "O_BINARY", 0)


class LeaseUnavailable(RuntimeError):
    """Raised by ``document_lease`` when a fresh lease is already held."""


@dataclass(frozen=True)
class LeaseHandle:
    """An acquired lease.

    Returned by ``acquire_lease``. ``lease_token`` identifies this exact
    acquisition so the delete paths can verify ownership before unlinking.
    """

    doc_slug: str
    lease_token: str
    action: str
    ttl_seconds: int
    path: Path

    def release(self) -> None:
        """Release this lease (ownership-guarded; see ``release_lease``)."""
        release_lease(self)

    def refresh(self) -> None:
        """Extend this lease's freshness (ownership-guarded; see ``refresh_lease``)."""
        refresh_lease(self)


def _validate_slug(doc_slug: str) -> None:
    if not isinstance(doc_slug, str) or not _SLUG_PATTERN.fullmatch(doc_slug):
        raise ValueError(
            f"invalid bridge document slug {doc_slug!r}: expected kebab-case [a-z0-9] segments joined by single hyphens"
        )


def _lease_dir(state_dir: Path | str) -> Path:
    """The leases subdirectory under ``state_dir`` (this helper does not
    create it)."""
    return Path(state_dir) / _LEASE_DIR_NAME


def _lease_path(state_dir: Path | str, doc_slug: str) -> Path:
    return _lease_dir(state_dir) / f"{doc_slug}{_LEASE_SUFFIX}"


def _now() -> datetime:
    return datetime.now(UTC)


def _read_lease(path: Path) -> dict | None:
    """Parse a lease file. Returns the record dict, or ``None`` when the file
    is missing, empty, not valid JSON, or not a JSON object."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.strip():
        return None
    try:
        record = json.loads(text)
    except json.JSONDecodeError:
        return None
    return record if isinstance(record, dict) else None


def _is_stale(record: dict, *, now: datetime) -> bool:
    """A parsed lease record is stale when its heartbeat has aged past the
    lease's own ``ttl_seconds``. A record with a missing or unparseable
    heartbeat is treated as stale -- it carries no liveness signal."""
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
    return (now - heartbeat).total_seconds() > ttl


def _remove_lease_if_token(path: Path, expected_token: str) -> bool:
    """Delete the lease file only when its on-disk ``lease_token`` matches
    ``expected_token``.

    This is the shared ownership/identity guard for every delete path:
    ``release_lease`` and stale reclamation both route through it, so a handle
    whose lease went stale and was reclaimed by another worker can never
    delete the new holder's lease. Returns ``True`` when the file was removed.
    """
    record = _read_lease(path)
    if record is None or record.get("lease_token") != expected_token:
        return False
    try:
        path.unlink()
    except FileNotFoundError:
        return False
    return True


def _try_create(path: Path, doc_slug: str, action: str, ttl_seconds: int) -> LeaseHandle | None:
    """Attempt the atomic exclusive create. Returns a handle on success, or
    ``None`` when the lease file already exists."""
    token = uuid.uuid4().hex
    timestamp = _now().isoformat()
    record = {
        "schema_version": LEASE_SCHEMA_VERSION,
        "doc_slug": doc_slug,
        "lease_token": token,
        "pid": os.getpid(),
        "acquired_at": timestamp,
        "heartbeat_at": timestamp,
        "action": action,
        "ttl_seconds": ttl_seconds,
    }
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | _O_BINARY)
    except FileExistsError:
        return None
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
    return LeaseHandle(
        doc_slug=doc_slug,
        lease_token=token,
        action=action,
        ttl_seconds=ttl_seconds,
        path=path,
    )


def acquire_lease(
    doc_slug: str,
    *,
    action: str,
    state_dir: Path | str,
    ttl_seconds: int = DEFAULT_LEASE_TTL_SECONDS,
) -> LeaseHandle | None:
    """Atomically acquire the lease for ``doc_slug``.

    Returns a ``LeaseHandle`` on success, or ``None`` when a fresh lease is
    already held by another worker. When the existing lease is parseable and
    stale it is reclaimed (token-guarded) and acquisition is retried once.
    An existing lease file that cannot be parsed is treated as held -- it may
    be mid-creation by the winning worker -- so it is never reclaimed here.

    Raises ``ValueError`` when ``doc_slug`` is not a valid kebab-case bridge
    document slug.
    """
    _validate_slug(doc_slug)
    path = _lease_path(state_dir, doc_slug)
    path.parent.mkdir(parents=True, exist_ok=True)

    handle = _try_create(path, doc_slug, action, ttl_seconds)
    if handle is not None:
        return handle

    existing = _read_lease(path)
    if existing is None or not _is_stale(existing, now=_now()):
        return None
    _remove_lease_if_token(path, str(existing.get("lease_token")))

    # Retry once. A loss here means another worker won the reclaimed slot.
    return _try_create(path, doc_slug, action, ttl_seconds)


def release_lease(handle: LeaseHandle) -> None:
    """Release a lease.

    Ownership-guarded: the lease file is removed only when its on-disk token
    still matches the handle's token, so a stale-and-reclaimed handle cannot
    delete the new holder's lease. A no-op when the lease is already gone or
    is owned by someone else.
    """
    _remove_lease_if_token(handle.path, handle.lease_token)


def refresh_lease(handle: LeaseHandle) -> None:
    """Rewrite the lease's heartbeat so a long-running holder does not go
    stale.

    Ownership-guarded and a no-op when the lease is gone or no longer owned by
    this handle. The rewrite is atomic: a sibling temp file is written and
    then ``os.replace``-d over the lease file.
    """
    record = _read_lease(handle.path)
    if record is None or record.get("lease_token") != handle.lease_token:
        return
    record["heartbeat_at"] = _now().isoformat()
    tmp_path = handle.path.with_name(handle.path.name + ".tmp")
    tmp_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp_path, handle.path)


def is_lease_held(doc_slug: str, *, state_dir: Path | str) -> bool:
    """Return ``True`` iff a fresh (non-stale) lease file exists for the slug.

    Raises ``ValueError`` when ``doc_slug`` is invalid.
    """
    _validate_slug(doc_slug)
    record = _read_lease(_lease_path(state_dir, doc_slug))
    if record is None:
        return False
    return not _is_stale(record, now=_now())


def reclaim_stale_leases(state_dir: Path | str) -> list[str]:
    """Sweep the lease directory and remove every stale lease file.

    Returns the sorted slugs of the leases reclaimed. Fresh leases are kept;
    files that cannot be parsed (possibly mid-creation) are left untouched.
    Each removal is token-guarded against the record just read.
    """
    lease_dir = _lease_dir(state_dir)
    if not lease_dir.is_dir():
        return []
    now = _now()
    reclaimed: list[str] = []
    for path in sorted(lease_dir.glob(f"*{_LEASE_SUFFIX}")):
        slug = path.name[: -len(_LEASE_SUFFIX)]
        if not _SLUG_PATTERN.fullmatch(slug):
            continue
        record = _read_lease(path)
        if record is None or not _is_stale(record, now=now):
            continue
        if _remove_lease_if_token(path, str(record.get("lease_token"))):
            reclaimed.append(slug)
    return reclaimed


@contextlib.contextmanager
def document_lease(
    doc_slug: str,
    *,
    action: str,
    state_dir: Path | str,
    ttl_seconds: int = DEFAULT_LEASE_TTL_SECONDS,
) -> Iterator[LeaseHandle]:
    """Context manager that acquires the lease on enter and releases it on
    exit, including when the body raises.

    Raises ``LeaseUnavailable`` when a fresh lease is already held.
    """
    handle = acquire_lease(doc_slug, action=action, state_dir=state_dir, ttl_seconds=ttl_seconds)
    if handle is None:
        raise LeaseUnavailable(f"a fresh lease is already held for bridge document {doc_slug!r}")
    try:
        yield handle
    finally:
        release_lease(handle)
