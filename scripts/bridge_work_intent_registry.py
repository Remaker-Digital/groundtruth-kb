#!/usr/bin/env python3
"""Foundation work-intent registry for bridge thread coordination."""

from __future__ import annotations

import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
SLUG_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
INDEX_DOC_RE: Final[re.Pattern[str]] = re.compile(r"^Document:\s+(\S+)\s*$")
INDEX_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED):\s+(bridge/\S+\.md)\s*$"
)

DEFAULT_DRAFT_TTL_SECONDS: Final[int] = int(os.environ.get("GTKB_WORK_INTENT_TTL_SECONDS") or "600")
GO_IMPLEMENTATION_DEADLINE_SECONDS: Final[int] = 30 * 60
GO_IMPLEMENTATION_EXTENSION_SECONDS: Final[int] = 30 * 60
GO_IMPLEMENTATION_MAX_HOLD_SECONDS: Final[int] = 2 * 60 * 60
GO_IMPLEMENTATION_GRACE_SECONDS: Final[int] = 10 * 60

CLAIM_KIND_DRAFT: Final[str] = "draft"
CLAIM_KIND_GO_IMPLEMENTATION: Final[str] = "go_implementation"


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


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
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


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS work_intent_claims (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_slug TEXT NOT NULL,
            session_id TEXT NOT NULL,
            acquired_at TEXT NOT NULL,
            ttl_expires_at TEXT NOT NULL,
            UNIQUE(thread_slug)
        );
        """
    )
    columns = {row[1] for row in conn.execute("PRAGMA table_info(work_intent_claims)").fetchall()}
    additive_columns = {
        "claim_kind": "TEXT",
        "implementation_deadline": "TEXT",
        "implementation_grace_expires_at": "TEXT",
        "extensions_used": "INTEGER DEFAULT 0",
        "extension_cap_seconds": "INTEGER",
        "extension_capped": "INTEGER DEFAULT 0",
    }
    for name, column_type in additive_columns.items():
        if name not in columns:
            conn.execute(f"ALTER TABLE work_intent_claims ADD COLUMN {name} {column_type}")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_intent_claims_slug ON work_intent_claims(thread_slug);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_intent_claims_kind ON work_intent_claims(claim_kind);")
    conn.commit()


def _get_conn(project_root: Path | None = None) -> sqlite3.Connection:
    root = _root(project_root)
    db_path = root / "groundtruth.db"
    try:
        conn = sqlite3.connect(str(db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        _ensure_schema(conn)
        return conn
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Could not open database {db_path}: {exc}") from exc


def _row_to_record(row: sqlite3.Row) -> dict[str, Any]:
    record = dict(row)
    record["claim_kind"] = record.get("claim_kind") or CLAIM_KIND_DRAFT
    record["extensions_used"] = int(record.get("extensions_used") or 0)
    record["extension_capped"] = bool(record.get("extension_capped") or 0)
    return record


def _is_expired(record: dict[str, Any], *, now: datetime | None = None) -> bool:
    expires_at = _parse_iso(str(record["ttl_expires_at"]))
    return bool(expires_at and expires_at <= (now or now_utc()))


def _is_lapsed_go_implementation(record: dict[str, Any], *, now: datetime | None = None) -> bool:
    if record.get("claim_kind") != CLAIM_KIND_GO_IMPLEMENTATION:
        return False
    grace_expires_at = _parse_iso(str(record.get("implementation_grace_expires_at") or ""))
    return bool(grace_expires_at and grace_expires_at <= (now or now_utc()))


def _latest_status(thread_slug: str, *, project_root: Path | None = None) -> str | None:
    root = _root(project_root)
    index_path = root / "bridge" / "INDEX.md"
    if not index_path.is_file():
        return None
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
            return status_match.group(1)
    return None


def current_holder(thread_slug: str, *, project_root: Path | None = None) -> dict[str, Any] | None:
    """Return the unexpired holder record for ``thread_slug``, if present."""
    slug = _validate_slug(thread_slug)
    conn = _get_conn(project_root)
    try:
        row = conn.execute("SELECT * FROM work_intent_claims WHERE thread_slug = ?", (slug,)).fetchone()
        if row is None:
            return None
        record = _row_to_record(row)
        if _is_expired(record):
            return None
        return record
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Database error during current_holder: {exc}") from exc
    finally:
        conn.close()


def claim_status(thread_slug: str, *, project_root: Path | None = None) -> dict[str, Any] | None:
    """Return the raw claim record, including expired/lapsed claims."""
    slug = _validate_slug(thread_slug)
    conn = _get_conn(project_root)
    try:
        row = conn.execute("SELECT * FROM work_intent_claims WHERE thread_slug = ?", (slug,)).fetchone()
        if row is None:
            return None
        record = _row_to_record(row)
        record["latest_bridge_status"] = _latest_status(slug, project_root=project_root)
        record["expired"] = _is_expired(record)
        record["lapsed_go_implementation"] = record["latest_bridge_status"] == "GO" and _is_lapsed_go_implementation(
            record
        )
        return record
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Database error during claim_status: {exc}") from exc
    finally:
        conn.close()


def _claim_values(
    slug: str,
    session_id: str,
    *,
    ttl_seconds: int,
    project_root: Path | None,
    now: datetime,
) -> dict[str, Any]:
    latest_status = _latest_status(slug, project_root=project_root)
    acquired_at = now
    if latest_status == "GO":
        deadline = acquired_at + timedelta(seconds=GO_IMPLEMENTATION_DEADLINE_SECONDS)
        grace_expires = deadline + timedelta(seconds=GO_IMPLEMENTATION_GRACE_SECONDS)
        return {
            "thread_slug": slug,
            "session_id": session_id,
            "acquired_at": _iso(acquired_at),
            "ttl_expires_at": _iso(grace_expires),
            "claim_kind": CLAIM_KIND_GO_IMPLEMENTATION,
            "implementation_deadline": _iso(deadline),
            "implementation_grace_expires_at": _iso(grace_expires),
            "extensions_used": 0,
            "extension_cap_seconds": GO_IMPLEMENTATION_MAX_HOLD_SECONDS,
            "extension_capped": 0,
        }
    ttl_expires_at = acquired_at + timedelta(seconds=ttl_seconds)
    return {
        "thread_slug": slug,
        "session_id": session_id,
        "acquired_at": _iso(acquired_at),
        "ttl_expires_at": _iso(ttl_expires_at),
        "claim_kind": CLAIM_KIND_DRAFT,
        "implementation_deadline": None,
        "implementation_grace_expires_at": None,
        "extensions_used": 0,
        "extension_cap_seconds": None,
        "extension_capped": 0,
    }


def acquire(
    thread_slug: str,
    session_id: str,
    ttl_seconds: int = DEFAULT_DRAFT_TTL_SECONDS,
    *,
    project_root: Path | None = None,
) -> bool:
    """Acquire a per-thread work-intent record.

    Returns True for an absent, expired/lapsed, or same-session record. Returns
    False when another non-expired session currently holds the thread intent.
    GO-latest threads receive a bounded implementation-deadline claim; non-GO
    drafting claims retain the legacy TTL behavior.
    """
    if not session_id.strip():
        raise WorkIntentRegistryError("session_id must be non-empty")
    slug = _validate_slug(thread_slug)
    conn = _get_conn(project_root)
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT * FROM work_intent_claims WHERE thread_slug = ?", (slug,)).fetchone()
            now = now_utc()
            if row:
                existing = _row_to_record(row)
                if not _is_expired(existing, now=now) and existing["session_id"] != session_id:
                    return False

            values = _claim_values(slug, session_id, ttl_seconds=ttl_seconds, project_root=project_root, now=now)
            conn.execute(
                """
                INSERT OR REPLACE INTO work_intent_claims
                (thread_slug, session_id, acquired_at, ttl_expires_at, claim_kind,
                 implementation_deadline, implementation_grace_expires_at,
                 extensions_used, extension_cap_seconds, extension_capped)
                VALUES
                (:thread_slug, :session_id, :acquired_at, :ttl_expires_at, :claim_kind,
                 :implementation_deadline, :implementation_grace_expires_at,
                 :extensions_used, :extension_cap_seconds, :extension_capped)
                """,
                values,
            )
            return True
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Database error during acquire: {exc}") from exc
    finally:
        conn.close()


def extend(
    thread_slug: str,
    session_id: str,
    *,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Extend a held GO-implementation claim by the fixed self-service increment."""
    if not session_id.strip():
        raise WorkIntentRegistryError("session_id must be non-empty")
    slug = _validate_slug(thread_slug)
    conn = _get_conn(project_root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM work_intent_claims WHERE thread_slug = ?", (slug,)).fetchone()
        if row is None:
            raise WorkIntentRegistryError(f"No active work-intent claim for {slug!r}")
        record = _row_to_record(row)
        if record["session_id"] != session_id:
            raise WorkIntentRegistryError(f"Thread {slug!r} is claimed by {record['session_id']!r}")
        if _latest_status(slug, project_root=project_root) != "GO":
            raise WorkIntentRegistryError(f"Thread {slug!r} is not latest GO; implementation timer no longer applies")
        if record.get("claim_kind") != CLAIM_KIND_GO_IMPLEMENTATION:
            raise WorkIntentRegistryError(f"Thread {slug!r} is not a GO-implementation claim")

        now = now_utc()
        if _is_lapsed_go_implementation(record, now=now):
            raise WorkIntentRegistryError(f"Thread {slug!r} is lapsed past grace and must be reacquired")
        acquired_at = _parse_iso(str(record["acquired_at"]))
        current_deadline = _parse_iso(str(record.get("implementation_deadline") or ""))
        if acquired_at is None or current_deadline is None:
            raise WorkIntentRegistryError(f"Thread {slug!r} has an invalid GO-implementation deadline")
        cap_at = acquired_at + timedelta(seconds=GO_IMPLEMENTATION_MAX_HOLD_SECONDS)
        new_deadline = current_deadline + timedelta(seconds=GO_IMPLEMENTATION_EXTENSION_SECONDS)
        if new_deadline > cap_at:
            conn.execute(
                "UPDATE work_intent_claims SET extension_capped = 1 WHERE thread_slug = ?",
                (slug,),
            )
            conn.commit()
            raise WorkIntentRegistryError(
                f"Extension cap reached for {slug!r}; maximum total hold is "
                f"{GO_IMPLEMENTATION_MAX_HOLD_SECONDS // 60} minutes"
            )
        grace_expires = new_deadline + timedelta(seconds=GO_IMPLEMENTATION_GRACE_SECONDS)
        conn.execute(
            """
            UPDATE work_intent_claims
            SET implementation_deadline = ?,
                implementation_grace_expires_at = ?,
                ttl_expires_at = ?,
                extensions_used = ?,
                extension_capped = 0
            WHERE thread_slug = ?
            """,
            (
                _iso(new_deadline),
                _iso(grace_expires),
                _iso(grace_expires),
                int(record.get("extensions_used") or 0) + 1,
                slug,
            ),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM work_intent_claims WHERE thread_slug = ?", (slug,)).fetchone()
        return _row_to_record(updated)
    except sqlite3.Error as exc:
        conn.rollback()
        raise WorkIntentRegistryError(f"Database error during extend: {exc}") from exc
    except Exception:
        if conn.in_transaction:
            conn.rollback()
        raise
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
                (slug, session_id),
            )
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Database error during release: {exc}") from exc
    finally:
        conn.close()


def lapsed_go_implementation_claims(*, project_root: Path | None = None) -> list[dict[str, Any]]:
    """Return GO-latest implementation claims lapsed past deadline+grace."""
    conn = _get_conn(project_root)
    try:
        rows = conn.execute(
            "SELECT * FROM work_intent_claims WHERE claim_kind = ?",
            (CLAIM_KIND_GO_IMPLEMENTATION,),
        ).fetchall()
        lapsed: list[dict[str, Any]] = []
        now = now_utc()
        for row in rows:
            record = _row_to_record(row)
            slug = str(record["thread_slug"])
            if _latest_status(slug, project_root=project_root) != "GO":
                continue
            if _is_lapsed_go_implementation(record, now=now):
                record["lapsed_go_implementation"] = True
                lapsed.append(record)
        return lapsed
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Database error during lapsed_go_implementation_claims: {exc}") from exc
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
    """Read live bridge state and report the next version target."""
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
    "CLAIM_KIND_DRAFT",
    "CLAIM_KIND_GO_IMPLEMENTATION",
    "GO_IMPLEMENTATION_DEADLINE_SECONDS",
    "GO_IMPLEMENTATION_EXTENSION_SECONDS",
    "GO_IMPLEMENTATION_GRACE_SECONDS",
    "GO_IMPLEMENTATION_MAX_HOLD_SECONDS",
    "WorkIntentRegistryError",
    "acquire",
    "claim_status",
    "current_holder",
    "extend",
    "lapsed_go_implementation_claims",
    "revalidate_thread_version",
    "release",
]
