#!/usr/bin/env python3
"""Foundation work-intent registry for bridge thread coordination."""

from __future__ import annotations

import json
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
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


def _get_conn(project_root: Path | None = None) -> sqlite3.Connection:
    root = _root(project_root)
    db_path = root / "groundtruth.db"
    try:
        conn = sqlite3.connect(str(db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        # Ensure database schema is initialized dynamically (robust fallback)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS work_intent_claims (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_slug TEXT NOT NULL,
            session_id TEXT NOT NULL,
            acquired_at TEXT NOT NULL,
            ttl_expires_at TEXT NOT NULL,
            UNIQUE(thread_slug)
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_work_intent_claims_slug ON work_intent_claims(thread_slug);")
        conn.commit()
        return conn
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Could not open database {db_path}: {exc}") from exc


def _is_expired(record: dict[str, str], *, now: datetime | None = None) -> bool:
    return _parse_iso(record["ttl_expires_at"]) <= (now or now_utc())


def current_holder(thread_slug: str, *, project_root: Path | None = None) -> dict[str, str] | None:
    """Return the unexpired holder record for ``thread_slug``, if present."""
    slug = _validate_slug(thread_slug)
    conn = _get_conn(project_root)
    try:
        row = conn.execute(
            "SELECT session_id, acquired_at, ttl_expires_at FROM work_intent_claims WHERE thread_slug = ?",
            (slug,)
        ).fetchone()
        if row is None:
            return None
        record = {
            "session_id": row["session_id"],
            "acquired_at": row["acquired_at"],
            "ttl_expires_at": row["ttl_expires_at"],
        }
        if _is_expired(record):
            return None
        return record
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Database error during current_holder: {exc}") from exc
    finally:
        conn.close()


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
    slug = _validate_slug(thread_slug)
    conn = _get_conn(project_root)
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT session_id, acquired_at, ttl_expires_at FROM work_intent_claims WHERE thread_slug = ?",
                (slug,)
            ).fetchone()
            now = now_utc()
            if row:
                existing = {
                    "session_id": row["session_id"],
                    "acquired_at": row["acquired_at"],
                    "ttl_expires_at": row["ttl_expires_at"],
                }
                if not _is_expired(existing, now=now) and existing["session_id"] != session_id:
                    return False
            
            acquired_at = now
            ttl_expires_at = now + timedelta(seconds=ttl_seconds)
            conn.execute(
                """
                INSERT OR REPLACE INTO work_intent_claims (thread_slug, session_id, acquired_at, ttl_expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (slug, session_id, _iso(acquired_at), _iso(ttl_expires_at))
            )
            return True
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Database error during acquire: {exc}") from exc
    finally:
        conn.close()


def release(thread_slug: str, session_id: str, *, project_root: Path | None = None) -> None:
    """Release a per-thread work-intent record when held by ``session_id``."""
    slug = _validate_slug(thread_slug)
    conn = _get_conn(project_root)
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "DELETE FROM work_intent_claims WHERE thread_slug = ? AND session_id = ?",
                (slug, session_id)
            )
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Database error during release: {exc}") from exc
    finally:
        conn.close()


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
