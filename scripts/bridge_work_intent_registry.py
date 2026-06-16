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
from typing import Any, Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
SLUG_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
BRIDGE_FILE_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED)$"
)

DEFAULT_DRAFT_TTL_SECONDS: Final[int] = int(os.environ.get("GTKB_WORK_INTENT_TTL_SECONDS") or "600")
GO_IMPLEMENTATION_DEADLINE_SECONDS: Final[int] = 30 * 60
GO_IMPLEMENTATION_EXTENSION_SECONDS: Final[int] = 30 * 60
GO_IMPLEMENTATION_MAX_HOLD_SECONDS: Final[int] = 2 * 60 * 60
GO_IMPLEMENTATION_GRACE_SECONDS: Final[int] = 10 * 60
# WI-4527: auto-extend an active GO-implementation claim only as the deadline
# nears. ``maybe_auto_extend`` is a no-op until the remaining time to the
# implementation deadline drops below this threshold, so a long build is
# rescued without extending on every single edit. Defaulting to the grace
# window keeps the behavior bounded and aligned with the existing timebox.
GO_IMPLEMENTATION_AUTO_EXTEND_THRESHOLD_SECONDS: Final[int] = GO_IMPLEMENTATION_GRACE_SECONDS

CLAIM_KIND_DRAFT: Final[str] = "draft"
CLAIM_KIND_GO_IMPLEMENTATION: Final[str] = "go_implementation"

# WI-4534 Slice A: role-eligibility guard on go_implementation claim acquisition.
# Cross-harness-trigger dispatch ids encode role + harness id as
# ``<compact-ISO8601>-<role>-<harness_id>-<6hex>`` (see
# ``cross_harness_bridge_trigger._new_dispatch_id``). The anchored regex captures
# the harness-id segment only; the role token is used solely to locate that
# segment and is NEVER treated as authorization (authority is the durable
# registry). Non-matching ids (interactive / raw-UUID) yield ``None``.
DISPATCH_SESSION_ID_RE: Final[re.Pattern[str]] = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z"
    r"-(?:prime-builder|loyal-opposition|acting-prime-builder)"
    r"-([A-Za-z0-9]+)-[0-9a-fA-F]{6}$"
)
# Durable roles eligible to hold a go_implementation claim. ``acting-prime-builder``
# is READ-accepted as a Prime-eligible compatibility role per the Acting-Prime
# Compatibility Contract.
PRIME_ELIGIBLE_ROLES: Final[frozenset[str]] = frozenset({"prime-builder", "acting-prime-builder"})
# Owner-declared interactive session-role marker (ephemeral; SessionStart-invalidated).
# Matches scripts/session_role_resolution.py::_SESSION_ROLE_MARKER_NAME.
SESSION_ROLE_MARKER_PARTS: Final[tuple[str, str, str]] = (".claude", "session", "active-session-role.json")


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
    import sys

    src_path = str(PROJECT_ROOT / "groundtruth-kb" / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    try:
        from groundtruth_kb.db import SCHEMA_SQL

        conn.executescript(SCHEMA_SQL)
    except ImportError:
        pass

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


def _version_from_path(rel_path: str, thread_slug: str) -> int | None:
    if rel_path == f"bridge/{thread_slug}.md":
        return 1
    match = re.fullmatch(rf"bridge/{re.escape(thread_slug)}-(\d{{3,}})\.md", rel_path)
    return int(match.group(1)) if match else None


def _bridge_file_status(path: Path) -> str:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        raise WorkIntentRegistryError(f"Bridge file is unreadable: {path}") from exc
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if BRIDGE_FILE_STATUS_RE.fullmatch(line):
            return line
        raise WorkIntentRegistryError(f"Bridge file has unrecognized status line: {path}: {line!r}")
    raise WorkIntentRegistryError(f"Bridge file is empty: {path}")


def _thread_version_entries(thread_slug: str, *, project_root: Path | None = None) -> list[tuple[int, str, str]]:
    root = _root(project_root)
    bridge_dir = root / "bridge"
    if not bridge_dir.is_dir():
        return []
    by_version: dict[int, tuple[str, str]] = {}
    for path in sorted(bridge_dir.glob(f"{thread_slug}*.md")):
        rel_path = path.relative_to(root).as_posix()
        version = _version_from_path(rel_path, thread_slug)
        if version is None:
            continue
        status = _bridge_file_status(path)
        if version in by_version:
            prior = by_version[version][1]
            raise WorkIntentRegistryError(
                f"Duplicate bridge version {version:03d} for {thread_slug}: {prior}, {rel_path}"
            )
        by_version[version] = (status, rel_path)
    return [(version, status, rel_path) for version, (status, rel_path) in sorted(by_version.items(), reverse=True)]


def _latest_status(thread_slug: str, *, project_root: Path | None = None) -> str | None:
    entries = _thread_version_entries(thread_slug, project_root=project_root)
    return entries[0][1] if entries else None


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


def current_claimed_bridge_id(session_id: str, *, project_root: Path | None = None) -> str | None:
    """Return the bridge thread slug currently claimed by ``session_id``, or None.

    WI-4443: the implementation-start gate uses this to resolve the packet for
    the session's OWN claimed bridge before consulting the global current.json
    pointer (which thrashes under concurrent Prime Builders). Read-only over the
    authoritative ``work_intent_claims`` SQLite table — the registry's canonical
    store, not the legacy ``.gtkb-state/work-intent/*.json`` path. Expired (TTL)
    and lapsed-past-grace GO-implementation claims are ignored. When a session
    holds more than one active claim, a GO-implementation claim is preferred,
    then the most recently acquired.
    """
    if not session_id:
        return None
    conn = _get_conn(project_root)
    try:
        rows = conn.execute(
            "SELECT * FROM work_intent_claims WHERE session_id = ?",
            (session_id,),
        ).fetchall()
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Database error during current_claimed_bridge_id: {exc}") from exc
    finally:
        conn.close()

    now = now_utc()
    active: list[dict[str, Any]] = []
    for row in rows:
        record = _row_to_record(row)
        if _is_expired(record, now=now) or _is_lapsed_go_implementation(record, now=now):
            continue
        active.append(record)
    if not active:
        return None
    active.sort(
        key=lambda rec: (
            1 if rec.get("claim_kind") == CLAIM_KIND_GO_IMPLEMENTATION else 0,
            str(rec.get("acquired_at") or ""),
        ),
        reverse=True,
    )
    return str(active[0]["thread_slug"])


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


def _dispatch_harness_id(session_id: str) -> str | None:
    """Return the harness id encoded in a dispatch-format session id, else ``None``.

    Parses the cross-harness-trigger dispatch id
    ``<compact-ISO8601>-<role>-<harness_id>-<6hex>``. The role token is matched
    only to anchor the harness-id capture; it is never used for authorization.
    A raw-UUID / interactive (non-dispatch) id returns ``None``.
    """
    match = DISPATCH_SESSION_ID_RE.match(session_id or "")
    return match.group(1) if match else None


def _harness_projection_reader():  # pragma: no cover - import shim
    """Lazy-import the stdlib-only harness projection reader (no DB, hook-safe)."""
    try:
        from scripts import harness_projection_reader as reader
    except ImportError:  # direct-script / scripts-dir-on-path execution
        import harness_projection_reader as reader  # type: ignore[no-redef]
    return reader


def _interactive_marker_role(project_root: Path | None, session_id: str | None = None) -> str | None:
    """Return the session-stated role from the owner-declared marker, or ``None``.

    WI-4540 (bridge -004, R-B1 + additive transition): prefer the per-session
    marker keyed under ``session_id`` (validating that the stored ``session_id``
    matches the querying id — assertion 6), then fall back to the legacy shared
    single-file marker ``.claude/session/active-session-role.json`` for the
    additive transition window. A missing/unreadable/malformed marker yields
    ``None`` (no positive Prime evidence). Keying the marker per session means a
    peer session's SessionStart can no longer clobber THIS session's marker, so
    the guard's interactive branch finds the marker written from the same
    interactive context under the canonical id.
    """
    # Per-session marker (WI-4540 authority) — only consulted when the querying
    # id is known. The path is built by the single shared authority in
    # scripts/gtkb_session_id.py so the read target cannot drift from the writer.
    if session_id:
        try:
            from scripts.gtkb_session_id import per_session_role_marker_path
        except ImportError:  # pragma: no cover - direct script execution path
            from gtkb_session_id import per_session_role_marker_path  # type: ignore[no-redef]

        per_session_path = per_session_role_marker_path(_root(project_root), session_id)
        try:
            per_session_body = json.loads(per_session_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            per_session_body = None
        if isinstance(per_session_body, dict):
            marker_session_id = per_session_body.get("session_id")
            role = per_session_body.get("role")
            if isinstance(marker_session_id, str) and marker_session_id == session_id and isinstance(role, str):
                return role
            # A present-but-mismatched per-session marker is not positive Prime
            # evidence for THIS session; fall through to the legacy marker.

    marker_path = _root(project_root).joinpath(*SESSION_ROLE_MARKER_PARTS)
    try:
        body = json.loads(marker_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    if not isinstance(body, dict):
        return None
    role = body.get("role")
    return role if isinstance(role, str) else None


def _resolve_go_implementation_eligibility(session_id: str, *, project_root: Path | None) -> tuple[bool, str]:
    """Resolve whether ``session_id`` may hold a go_implementation claim.

    Returns ``(eligible, detail)`` where ``detail`` is a human-readable
    description of the resolved authority for the rejection message.

    - **Dispatch id:** authority is the durable registry role-set for the parsed
      harness id (intersected with ``PRIME_ELIGIBLE_ROLES``). An unknown harness
      id (empty role set) is NOT eligible — no token fallback (F2). A
      token/registry mismatch resolves from the registry (token ignored) (F2/d).
    - **Non-dispatch (un-resolvable) id:** require positive Prime evidence — the
      owner-declared interactive-Prime marker. Absent/unreadable/non-Prime →
      not eligible (no fail-open) (F3).
    """
    harness_id = _dispatch_harness_id(session_id)
    if harness_id is not None:
        reader = _harness_projection_reader()
        document = reader.load_harness_projection(_root(project_root))
        role_set = reader.role_set_for_id(document, harness_id)
        eligible = bool(role_set & PRIME_ELIGIBLE_ROLES)
        roles_desc = ", ".join(sorted(role_set)) if role_set else "<harness id absent from registry>"
        return eligible, f"dispatch harness {harness_id!r} durable role-set {{{roles_desc}}}"
    marker_role = _interactive_marker_role(project_root, session_id)
    eligible = marker_role == "prime-builder"
    return eligible, f"interactive session marker role {marker_role!r}"


def _go_implementation_eligible(session_id: str, *, project_root: Path | None = None) -> bool:
    """Return True iff ``session_id`` may hold a go_implementation claim.

    Registry-authoritative role-eligibility guard (WI-4534 Slice A); see
    ``_resolve_go_implementation_eligibility`` for the resolution contract.
    """
    return _resolve_go_implementation_eligibility(session_id, project_root=project_root)[0]


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
            if values["claim_kind"] == CLAIM_KIND_GO_IMPLEMENTATION:
                # WI-4534 Slice A: registry-authoritative role-eligibility guard.
                # Only a durably prime-builder (or compat acting-prime-builder)
                # harness — or an owner-declared interactive Prime session — may
                # hold a go_implementation claim. Draft (non-GO) claims are
                # unaffected because this branch only fires for GO-latest threads.
                eligible, detail = _resolve_go_implementation_eligibility(session_id, project_root=project_root)
                if not eligible:
                    raise WorkIntentRegistryError(
                        f"go_implementation claim requires a prime-builder harness; "
                        f"session {session_id!r} resolves to {detail} (not prime-eligible)"
                    )
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


def maybe_auto_extend(
    thread_slug: str,
    session_id: str,
    *,
    project_root: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any] | None:
    """Best-effort, fail-soft auto-extension of an active GO-implementation claim.

    WI-4527: a go_implementation claim's 30 min deadline (+10 min grace) is too
    short for large multi-module builds, so a live build can lose its claim
    mid-edit. This helper rescues *active* work: when the holding session is
    making an authorized edit and its deadline is near, it calls the existing
    capped :func:`extend` so the claim survives. It is a side-effect of an
    already-authorized edit and never alters any gate's allow/deny verdict.

    Returns the updated claim record on a successful extension, or ``None`` when
    no extension was made -- which is the case for ALL of the following no-op
    conditions (each fail-soft, never raising):

    - no active claim exists for ``thread_slug`` (or it is TTL-expired / lapsed
      past grace and must be reacquired);
    - the claim is held by a different session (no unauthorized extension);
    - the claim is not a ``go_implementation`` claim (draft claims are ignored);
    - the latest bridge status for the thread is not ``GO``;
    - the remaining time to the implementation deadline is still at or above
      ``GO_IMPLEMENTATION_AUTO_EXTEND_THRESHOLD_SECONDS`` (deadline not near);
    - :func:`extend` raises (e.g. the 2 h ``MAX_HOLD`` cap is reached, or a
      concurrent race) -- the existing cap/lapse behavior then governs.

    The extension itself is pure reuse of :func:`extend`, so it inherits that
    primitive's ``MAX_HOLD`` cap and ``extensions_used`` accounting; abandoned
    claims still expire at the cap.
    """
    if not session_id.strip():
        return None
    now_value = now or now_utc()
    try:
        holder = current_holder(thread_slug, project_root=project_root)
    except WorkIntentRegistryError:
        return None
    if holder is None:
        return None
    if str(holder.get("session_id") or "") != session_id:
        return None
    if holder.get("claim_kind") != CLAIM_KIND_GO_IMPLEMENTATION:
        return None
    if _is_lapsed_go_implementation(holder, now=now_value):
        return None
    if _latest_status(thread_slug, project_root=project_root) != "GO":
        return None
    deadline = _parse_iso(str(holder.get("implementation_deadline") or ""))
    if deadline is None:
        return None
    remaining_seconds = (deadline - now_value).total_seconds()
    if remaining_seconds >= GO_IMPLEMENTATION_AUTO_EXTEND_THRESHOLD_SECONDS:
        return None
    try:
        return extend(thread_slug, session_id, project_root=project_root)
    except WorkIntentRegistryError:
        return None


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


def revalidate_thread_version(thread_slug: str, project_root: Path) -> dict[str, int | str | bool]:
    """Read live bridge state and report the next version target."""
    slug = _validate_slug(thread_slug)
    root = _root(project_root)
    versions = [version for version, _, _ in _thread_version_entries(slug, project_root=root)]
    if not versions:
        raise WorkIntentRegistryError(f"Document {slug!r} not found in versioned bridge files")
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
    "GO_IMPLEMENTATION_AUTO_EXTEND_THRESHOLD_SECONDS",
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
    "maybe_auto_extend",
    "revalidate_thread_version",
    "release",
]
