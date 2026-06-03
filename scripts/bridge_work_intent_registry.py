#!/usr/bin/env python3
"""Foundation work-intent registry for bridge thread coordination."""

from __future__ import annotations

import json
import os
import re
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
STATE_DIR_RELATIVE: Final[Path] = Path(".gtkb-state/work-intent")
LOCK_RETRY_SECONDS: Final[float] = 1.0
LOCK_SLEEP_SECONDS: Final[float] = 0.02
SLUG_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
INDEX_DOC_RE: Final[re.Pattern[str]] = re.compile(r"^Document:\s+(\S+)\s*$")
INDEX_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED):\s+(bridge/\S+\.md)\s*$"
)


class WorkIntentRegistryError(RuntimeError):
    """Raised when a work-intent registry operation cannot be completed."""


@dataclass(frozen=True)
class VersionState:
    latest_version: int
    next_version: int
    next_file_path: str
    next_file_exists: bool


def now_utc() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(value: str) -> datetime:
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(text)
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _validate_slug(thread_slug: str) -> str:
    slug = thread_slug.strip()
    if not slug or not SLUG_RE.fullmatch(slug) or slug in {".", ".."}:
        raise WorkIntentRegistryError(f"Invalid bridge thread slug: {thread_slug!r}")
    return slug


def _root(project_root: Path | None = None) -> Path:
    return (project_root or PROJECT_ROOT).resolve()


def _state_dir(project_root: Path | None = None) -> Path:
    return _root(project_root) / STATE_DIR_RELATIVE


def _record_path(thread_slug: str, project_root: Path | None = None) -> Path:
    return _state_dir(project_root) / f"{_validate_slug(thread_slug)}.json"


def _lock_path(thread_slug: str, project_root: Path | None = None) -> Path:
    return _state_dir(project_root) / f"{_validate_slug(thread_slug)}.lock"


@contextmanager
def _thread_lock(thread_slug: str, project_root: Path | None = None) -> Iterator[None]:
    state_dir = _state_dir(project_root)
    state_dir.mkdir(parents=True, exist_ok=True)
    path = _lock_path(thread_slug, project_root)
    deadline = time.monotonic() + LOCK_RETRY_SECONDS
    fd: int | None = None
    while fd is None:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise WorkIntentRegistryError(f"Could not acquire registry file lock for {thread_slug!r}")
            time.sleep(LOCK_SLEEP_SECONDS)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
        yield
    finally:
        path.unlink(missing_ok=True)


def _read_record(path: Path) -> dict[str, str] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkIntentRegistryError(f"Could not read work-intent record {path}") from exc
    if not isinstance(data, dict):
        raise WorkIntentRegistryError(f"Invalid work-intent record shape: {path}")
    session_id = data.get("session_id")
    acquired_at = data.get("acquired_at")
    ttl_expires_at = data.get("ttl_expires_at")
    if not all(isinstance(value, str) and value for value in (session_id, acquired_at, ttl_expires_at)):
        raise WorkIntentRegistryError(f"Invalid work-intent record fields: {path}")
    return {
        "session_id": session_id,
        "acquired_at": acquired_at,
        "ttl_expires_at": ttl_expires_at,
    }


def _is_expired(record: dict[str, str], *, now: datetime | None = None) -> bool:
    return _parse_iso(record["ttl_expires_at"]) <= (now or now_utc())


def _write_record_atomic(path: Path, record: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    tmp_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp_path, path)


def current_holder(thread_slug: str, *, project_root: Path | None = None) -> dict[str, str] | None:
    """Return the unexpired holder record for ``thread_slug``, if present."""
    path = _record_path(thread_slug, project_root)
    record = _read_record(path)
    if record is None or _is_expired(record):
        return None
    return record


def acquire(
    thread_slug: str,
    session_id: str,
    ttl_seconds: int = 30,
    *,
    project_root: Path | None = None,
) -> bool:
    """Acquire a per-thread work-intent record.

    Returns True for an absent, expired, or same-session record. Returns False
    when another non-expired session currently holds the thread intent.
    """
    if not session_id.strip():
        raise WorkIntentRegistryError("session_id must be non-empty")
    path = _record_path(thread_slug, project_root)
    with _thread_lock(thread_slug, project_root):
        existing = _read_record(path)
        if existing and not _is_expired(existing) and existing["session_id"] != session_id:
            return False
        acquired_at = now_utc()
        record = {
            "session_id": session_id,
            "acquired_at": _iso(acquired_at),
            "ttl_expires_at": _iso(acquired_at + timedelta(seconds=ttl_seconds)),
        }
        _write_record_atomic(path, record)
        return True


def release(thread_slug: str, session_id: str, *, project_root: Path | None = None) -> None:
    """Release a per-thread work-intent record when held by ``session_id``."""
    path = _record_path(thread_slug, project_root)
    with _thread_lock(thread_slug, project_root):
        record = _read_record(path)
        if record and record["session_id"] == session_id:
            path.unlink(missing_ok=True)


def _version_from_path(rel_path: str, thread_slug: str) -> int | None:
    if rel_path == f"bridge/{thread_slug}.md":
        return 1
    match = re.fullmatch(rf"bridge/{re.escape(thread_slug)}-(\d{{3,}})\.md", rel_path)
    return int(match.group(1)) if match else None


def _iter_thread_versions(index_path: Path, thread_slug: str) -> list[int]:
    if not index_path.is_file():
        raise WorkIntentRegistryError(f"bridge/INDEX.md not found: {index_path}")
    versions: list[int] = []
    in_target = False
    for raw_line in index_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        doc_match = INDEX_DOC_RE.match(line)
        if doc_match:
            if in_target:
                break
            in_target = doc_match.group(1) == thread_slug
            continue
        if not in_target:
            continue
        if not line:
            break
        status_match = INDEX_STATUS_RE.match(line)
        if status_match:
            version = _version_from_path(status_match.group(2), thread_slug)
            if version is not None:
                versions.append(version)
    if not versions:
        raise WorkIntentRegistryError(f"Document {thread_slug!r} not found in bridge/INDEX.md")
    return versions


def revalidate_thread_version(thread_slug: str, project_root: Path) -> dict[str, int | str | bool]:
    """Read live bridge state and report the next version target.

    This is the acquire-then-refresh primitive a future bridge writer can call
    while holding a work-intent record.
    """
    slug = _validate_slug(thread_slug)
    root = _root(project_root)
    versions = _iter_thread_versions(root / "bridge" / "INDEX.md", slug)
    latest_version = max(versions)
    next_version = latest_version + 1
    next_rel_path = f"bridge/{slug}-{next_version:03d}.md"
    return {
        "latest_version": latest_version,
        "next_version": next_version,
        "next_file_path": next_rel_path,
        "next_file_exists": (root / next_rel_path).exists(),
    }


__all__ = [
    "WorkIntentRegistryError",
    "acquire",
    "current_holder",
    "revalidate_thread_version",
    "release",
]
