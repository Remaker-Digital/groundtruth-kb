#!/usr/bin/env python3
"""Foundation work-intent registry for bridge thread coordination."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import time
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
SLUG_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
BRIDGE_FILE_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|NO-ACTION|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED)$"
)
BRIDGE_PROJECT_RE: Final[re.Pattern[str]] = re.compile(r"^Project:\s*(\S+)\s*$", re.MULTILINE)

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

# WI-5784: write contention is retried inside one bounded total deadline.  A
# short per-attempt SQLite wait leaves room to reopen the connection, re-read
# the exact claim row, and make progress when a legitimate sibling writer
# releases the database inside the overall budget.
WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS: Final[float] = 10.0
WORK_INTENT_WRITE_ATTEMPT_TIMEOUT_SECONDS: Final[float] = 0.25
WORK_INTENT_WRITE_INITIAL_BACKOFF_SECONDS: Final[float] = 0.025
WORK_INTENT_WRITE_MAX_BACKOFF_SECONDS: Final[float] = 0.5

CLAIM_KIND_DRAFT: Final[str] = "draft"
CLAIM_KIND_GO_IMPLEMENTATION: Final[str] = "go_implementation"
# Explicit non-implementation claim for Prime NO-ACTION corrections after
# Loyal Opposition GO/NO-GO verdicts.
CLAIM_KIND_NO_ACTION_CORRECTION: Final[str] = "no_action_correction"
CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP: Final[str] = "project_authorization_bootstrap"
BOOTSTRAP_REQUIRED_CARRIER_TARGET: Final[str] = "groundtruth.db"
BRIDGE_WORK_ITEM_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:Work Item|Work Item ID|Backlog Item|Backlog Item ID):\s*`?([^`\s]+)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


class WorkIntentRegistryError(RuntimeError):
    """Raised when a work-intent registry operation cannot be completed."""


class WorkIntentDatabaseError(WorkIntentRegistryError):
    """Typed SQLite failure with safe operation and timing diagnostics."""

    def __init__(
        self,
        detail: str,
        *,
        operation: str,
        phase: str,
        attempts: int,
        elapsed_seconds: float,
        sqlite_errorcode: int | None,
        sqlite_errorname: str | None,
        database_path: Path,
        contention_exhausted: bool = False,
    ) -> None:
        self.operation = operation
        self.phase = phase
        self.attempts = attempts
        self.elapsed_seconds = elapsed_seconds
        self.sqlite_errorcode = sqlite_errorcode
        self.sqlite_errorname = sqlite_errorname
        self.database_path = database_path
        self.contention_exhausted = contention_exhausted
        reason = "contention_exhausted" if contention_exhausted else "non_retryable"
        super().__init__(
            f"Database error during {operation}: reason={reason} phase={phase} "
            f"attempts={attempts} elapsed_seconds={elapsed_seconds:.6f} "
            f"sqlite_errorcode={sqlite_errorcode!r} sqlite_errorname={sqlite_errorname!r} "
            f"database_path={database_path} detail={detail}"
        )

    def as_dict(self) -> dict[str, Any]:
        """Return machine-readable diagnostics without guessing lock ownership."""

        return {
            "operation": self.operation,
            "phase": self.phase,
            "attempts": self.attempts,
            "elapsed_seconds": self.elapsed_seconds,
            "sqlite_errorcode": self.sqlite_errorcode,
            "sqlite_errorname": self.sqlite_errorname,
            "database_path": str(self.database_path),
            "contention_exhausted": self.contention_exhausted,
        }


class WorkIntentWriteContentionError(WorkIntentDatabaseError):
    """Raised after the bounded SQLITE_BUSY/SQLITE_LOCKED budget is exhausted."""


class MalformedBridgeStatusError(WorkIntentRegistryError):
    """Raised when a bridge file's first-line status token cannot be parsed.

    A *permanent* per-file parse error distinct from transient errors (DB
    errors, contention). Subclass of :class:`WorkIntentRegistryError` so every
    existing ``except WorkIntentRegistryError`` call site stays
    backward-compatible. The dispatch batch-acquire surface in
    ``scripts/dispatcher_runtime.py`` catches this distinct type to
    quarantine-and-continue rather than head-of-line-blocking the entire
    headless Prime-Builder dispatch lane on a single malformed bridge file
    (WI-4658).
    """

    def __init__(
        self,
        message: str,
        *,
        path: Path | None = None,
        offending_line: str | None = None,
    ) -> None:
        super().__init__(message)
        self.path = path
        self.offending_line = offending_line


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


def _database_path(project_root: Path | None = None) -> Path:
    root = _root(project_root)
    config_path = root / "groundtruth.toml"
    if config_path.is_file():
        try:
            data = tomllib.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
            raise WorkIntentRegistryError(f"Could not read GroundTruth configuration {config_path}: {exc}") from exc
        configured = data.get("groundtruth", {}).get("db_path")
        if isinstance(configured, str) and configured.strip():
            path = Path(configured)
            return path if path.is_absolute() else root / path
    return root / "groundtruth.db"


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create or upgrade only the narrow work-intent schema.

    This hot-path helper deliberately does not execute the global GroundTruth
    ``SCHEMA_SQL``.  The registry owns one table and its additive migration;
    initializing every platform table/index on each claim operation made the
    growing append-only SoT part of routine claim latency.
    """
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
        "acting_role": "TEXT",
        "project_id": "TEXT",
        "bootstrap_owner_decision_id": "TEXT",
        "bootstrap_project_id": "TEXT",
        "bootstrap_work_item_id": "TEXT",
        "bootstrap_authorization_id": "TEXT",
        "bootstrap_carrier_targets": "TEXT",
        "bootstrap_consumed_at": "TEXT",
    }
    for name, column_type in additive_columns.items():
        if name not in columns:
            conn.execute(f"ALTER TABLE work_intent_claims ADD COLUMN {name} {column_type}")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_intent_claims_slug ON work_intent_claims(thread_slug);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_intent_claims_kind ON work_intent_claims(claim_kind);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_work_intent_claims_role_project ON work_intent_claims(acting_role, project_id);"
    )
    conn.commit()


def _monotonic() -> float:
    return time.monotonic()


def _retry_sleep(seconds: float) -> None:
    time.sleep(seconds)


def _sqlite_error_fields(exc: sqlite3.Error) -> tuple[int | None, str | None]:
    code = getattr(exc, "sqlite_errorcode", None)
    name = getattr(exc, "sqlite_errorname", None)
    return (int(code) if isinstance(code, int) else None, str(name) if name else None)


def _is_retryable_write_contention(exc: sqlite3.Error) -> bool:
    code, _ = _sqlite_error_fields(exc)
    if code is not None:
        return (code & 0xFF) in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED}
    text = str(exc).casefold()
    return "database is locked" in text or "database table is locked" in text


def _database_error(
    exc: sqlite3.Error,
    *,
    operation: str,
    phase: str,
    attempts: int,
    started_at: float,
    database_path: Path,
    contention_exhausted: bool = False,
) -> WorkIntentDatabaseError:
    code, name = _sqlite_error_fields(exc)
    error_type = WorkIntentWriteContentionError if contention_exhausted else WorkIntentDatabaseError
    return error_type(
        str(exc),
        operation=operation,
        phase=phase,
        attempts=attempts,
        elapsed_seconds=max(0.0, _monotonic() - started_at),
        sqlite_errorcode=code,
        sqlite_errorname=name,
        database_path=database_path,
        contention_exhausted=contention_exhausted,
    )


def _deadline_exhausted_error(
    *,
    operation: str,
    phase: str,
    attempts: int,
    started_at: float,
    database_path: Path,
    last_contention: sqlite3.Error | None = None,
) -> WorkIntentWriteContentionError:
    """Return a typed failure before a transaction can outlive its budget.

    A monotonic write-deadline exhaustion in this retry loop is a lock-
    contention condition (the write could not proceed because the registry
    lock was not free within budget).  When a real ``sqlite3.Error`` was
    observed during the wait, propagate its code/name; otherwise report
    ``SQLITE_BUSY`` so callers can distinguish contention exhaustion from a
    non-contention failure.  This keeps the typed error deterministic under a
    held write lock.
    """

    if last_contention is not None:
        code, name = _sqlite_error_fields(last_contention)
    else:
        code, name = sqlite3.SQLITE_BUSY, "database is locked"
    return WorkIntentWriteContentionError(
        "monotonic write deadline exhausted",
        operation=operation,
        phase=phase,
        attempts=attempts,
        elapsed_seconds=max(0.0, _monotonic() - started_at),
        sqlite_errorcode=code,
        sqlite_errorname=name,
        database_path=database_path,
        contention_exhausted=True,
    )


def _apply_remaining_busy_timeout(conn: sqlite3.Connection, *, deadline: float) -> bool:
    """Clamp the next SQLite lock wait to the remaining total write budget."""

    remaining = deadline - _monotonic()
    if remaining <= 0:
        return False
    timeout_seconds = min(WORK_INTENT_WRITE_ATTEMPT_TIMEOUT_SECONDS, remaining)
    timeout_milliseconds = max(0, int(timeout_seconds * 1000))
    conn.execute(f"PRAGMA busy_timeout = {timeout_milliseconds}")
    return True


def _get_conn(
    project_root: Path | None = None,
    *,
    timeout_seconds: float = 10.0,
    error_context: tuple[str, int, float] | None = None,
) -> sqlite3.Connection:
    db_path = _database_path(project_root)
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(str(db_path), timeout=max(0.0, timeout_seconds))
        conn.row_factory = sqlite3.Row
        _ensure_schema(conn)
        return conn
    except sqlite3.Error as exc:
        if conn is not None:
            conn.close()
        if error_context is not None:
            operation, attempts, started_at = error_context
            raise _database_error(
                exc,
                operation=operation,
                phase="open_or_schema",
                attempts=attempts,
                started_at=started_at,
                database_path=db_path,
            ) from exc
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
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except (OSError, ValueError) as exc:
        raise WorkIntentRegistryError(f"Bridge file is unreadable: {path}") from exc
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if BRIDGE_FILE_STATUS_RE.fullmatch(line):
            return line
        raise MalformedBridgeStatusError(
            f"Bridge file has unrecognized status line: {path}: {line!r}",
            path=path,
            offending_line=line,
        )
    raise MalformedBridgeStatusError(
        f"Bridge file is empty: {path}",
        path=path,
        offending_line=None,
    )


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
        try:
            status = _bridge_file_status(path)
        except MalformedBridgeStatusError as exc:
            import warnings

            warnings.warn(
                f"Skipping malformed or legacy status in bridge file: {exc.path} (offending status line: {exc.offending_line!r})",
                category=UserWarning,
                stacklevel=2,
            )
            continue
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


def _approved_proposal_path_for_go(thread_slug: str, *, project_root: Path | None = None) -> str | None:
    entries = _thread_version_entries(thread_slug, project_root=project_root)
    go_index = next((index for index, entry in enumerate(entries) if entry[1] == "GO"), None)
    if go_index is None:
        return None
    return next((entry[2] for entry in entries[go_index + 1 :] if entry[1] in {"NEW", "REVISED"}), None)


def _approved_proposal_text_for_go(thread_slug: str, *, project_root: Path | None = None) -> str:
    proposal_path = _approved_proposal_path_for_go(thread_slug, project_root=project_root)
    if proposal_path is None:
        raise WorkIntentRegistryError(f"Bridge {thread_slug!r} has no approved proposal before GO")
    try:
        return (_root(project_root) / proposal_path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise WorkIntentRegistryError(f"Could not read approved proposal {proposal_path}: {exc}") from exc


def project_id_for_thread(thread_slug: str, *, project_root: Path | None = None) -> str | None:
    """Return the bridge proposal ``Project:`` metadata for ``thread_slug``.

    The project-level guard is advisory and fail-open. Missing or unreadable
    metadata therefore returns ``None`` instead of blocking a claim.
    """
    slug = _validate_slug(thread_slug)
    root = _root(project_root)
    entries = _thread_version_entries(slug, project_root=root)
    proposal_entries = [entry for entry in entries if entry[1] in {"NEW", "REVISED"}]
    for _version, _status, rel_path in proposal_entries or entries:
        try:
            text = (root / rel_path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = BRIDGE_PROJECT_RE.search(text)
        if match:
            project_id = match.group(1).strip()
            return project_id or None
    return None


def _work_item_for_thread(thread_slug: str, *, project_root: Path | None = None) -> str | None:
    try:
        text = _approved_proposal_text_for_go(thread_slug, project_root=project_root)
    except WorkIntentRegistryError:
        return None
    match = BRIDGE_WORK_ITEM_RE.search(text)
    return match.group(1).strip() if match else None


def _bootstrap_carrier_list(raw_targets: Any) -> list[str]:
    if isinstance(raw_targets, str):
        targets = [raw_targets]
    elif isinstance(raw_targets, list):
        targets = [str(item) for item in raw_targets if str(item).strip()]
    else:
        targets = []
    normalized: list[str] = []
    for target in targets:
        clean = target.strip().replace("\\", "/").lstrip("./")
        if clean and clean not in normalized:
            normalized.append(clean)
    return normalized


def _bootstrap_claim_payload(record: dict[str, Any]) -> dict[str, Any]:
    raw_targets = record.get("bootstrap_carrier_targets")
    parsed_targets: Any = []
    if isinstance(raw_targets, str) and raw_targets.strip():
        try:
            parsed_targets = json.loads(raw_targets)
        except json.JSONDecodeError:
            parsed_targets = []
    return {
        "claim_kind": record.get("claim_kind"),
        "owner_decision_id": record.get("bootstrap_owner_decision_id"),
        "project_id": record.get("bootstrap_project_id"),
        "work_item_id": record.get("bootstrap_work_item_id"),
        "bridge_id": record.get("thread_slug"),
        "authorization_id": record.get("bootstrap_authorization_id"),
        "carrier_targets": _bootstrap_carrier_list(parsed_targets),
        "consumed_at": record.get("bootstrap_consumed_at"),
    }


def bootstrap_authority_from_claim(record: dict[str, Any]) -> dict[str, Any] | None:
    """Return stable bootstrap authority metadata for a persisted claim."""
    if record.get("claim_kind") != CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP:
        return None
    payload = _bootstrap_claim_payload(record)
    return {
        "schema_version": 1,
        "claim_kind": CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP,
        "owner_decision_id": payload["owner_decision_id"],
        "project_id": payload["project_id"],
        "work_item_id": payload["work_item_id"],
        "bridge_id": payload["bridge_id"],
        "authorization_id": payload["authorization_id"],
        "carrier_targets": payload["carrier_targets"],
        "single_use": {
            "state": "available" if not payload["consumed_at"] else "consumed",
            "consumed": bool(payload["consumed_at"]),
            "consumed_at": payload["consumed_at"],
        },
    }


def _validate_bootstrap_authority_request(
    slug: str,
    *,
    project_root: Path | None,
    acting_role: str | None,
    project_id: str | None,
    bootstrap_authority: dict[str, Any] | None,
) -> dict[str, Any]:
    if _latest_status(slug, project_root=project_root) != "GO":
        raise WorkIntentRegistryError(f"Project-authorization bootstrap claim requires latest GO for {slug!r}")
    if acting_role != "prime-builder":
        raise WorkIntentRegistryError(
            f"Project-authorization bootstrap claim requires prime-builder worker provenance; "
            f"session resolves to {acting_role or '<missing>'}"
        )
    if not isinstance(bootstrap_authority, dict):
        raise WorkIntentRegistryError("Project-authorization bootstrap claim requires explicit authority metadata")

    owner_decision_id = str(bootstrap_authority.get("owner_decision_id") or "").strip()
    requested_project_id = str(bootstrap_authority.get("project_id") or "").strip()
    work_item_id = str(bootstrap_authority.get("work_item_id") or "").strip()
    authorization_id = str(bootstrap_authority.get("authorization_id") or "").strip()
    carrier_targets = _bootstrap_carrier_list(bootstrap_authority.get("carrier_targets"))
    missing = [
        name
        for name, value in (
            ("owner_decision_id", owner_decision_id),
            ("project_id", requested_project_id),
            ("work_item_id", work_item_id),
            ("authorization_id", authorization_id),
        )
        if not value
    ]
    if missing:
        raise WorkIntentRegistryError(
            "Project-authorization bootstrap claim is missing required field(s): " + ", ".join(missing)
        )
    if not owner_decision_id.startswith("DELIB-"):
        raise WorkIntentRegistryError("Project-authorization bootstrap owner decision must cite a DELIB-* record")
    if not authorization_id.startswith("PAUTH-"):
        raise WorkIntentRegistryError("Project-authorization bootstrap authorization id must cite a PAUTH-* id")
    if BOOTSTRAP_REQUIRED_CARRIER_TARGET not in carrier_targets:
        raise WorkIntentRegistryError(
            f"Project-authorization bootstrap carrier targets must include {BOOTSTRAP_REQUIRED_CARRIER_TARGET!r}"
        )
    if project_id and requested_project_id != project_id:
        raise WorkIntentRegistryError(
            f"Project-authorization bootstrap project drift: proposal has {project_id!r}, claim requested "
            f"{requested_project_id!r}"
        )
    proposal_work_item = _work_item_for_thread(slug, project_root=project_root)
    if proposal_work_item and work_item_id != proposal_work_item:
        raise WorkIntentRegistryError(
            f"Project-authorization bootstrap work-item drift: proposal has {proposal_work_item!r}, claim requested "
            f"{work_item_id!r}"
        )

    proposal = _approved_proposal_text_for_go(slug, project_root=project_root)
    marker_text = proposal.lower().replace("-", "_")
    if "project_authorization_bootstrap" not in marker_text and "project authorization bootstrap" not in marker_text:
        raise WorkIntentRegistryError("Approved proposal does not declare a project-authorization bootstrap marker")
    return {
        "owner_decision_id": owner_decision_id,
        "project_id": requested_project_id,
        "work_item_id": work_item_id,
        "authorization_id": authorization_id,
        "carrier_targets": carrier_targets,
    }


def _validate_no_action_correction_request(
    slug: str,
    *,
    project_root: Path | None,
    acting_role: str | None,
) -> None:
    latest_status = _latest_status(slug, project_root=project_root)
    if latest_status not in {"GO", "NO-GO"}:
        raise WorkIntentRegistryError(
            f"NO-ACTION correction claim requires latest GO or NO-GO for {slug!r}; "
            f"latest is {latest_status or '<missing>'}"
        )
    if acting_role != "prime-builder":
        raise WorkIntentRegistryError(
            f"NO-ACTION correction claim requires prime-builder worker provenance; "
            f"session resolves to {acting_role or '<missing>'}"
        )


def _bootstrap_metadata_matches(existing: dict[str, Any], incoming: dict[str, Any]) -> bool:
    if existing.get("claim_kind") != CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP:
        return True
    existing_payload = _bootstrap_claim_payload(existing)
    incoming_payload = _bootstrap_claim_payload(incoming)
    return all(
        existing_payload.get(key) == incoming_payload.get(key)
        for key in ("owner_decision_id", "project_id", "work_item_id", "authorization_id", "carrier_targets")
    )


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
            1
            if rec.get("claim_kind") in {CLAIM_KIND_GO_IMPLEMENTATION, CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP}
            else 0,
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


def _normalize_claim_role(role: str | None) -> str | None:
    normalized = (role or "").strip().lower()
    if normalized in {"prime-builder", "acting-prime-builder"}:
        return "prime-builder"
    if normalized == "loyal-opposition":
        return "loyal-opposition"
    return normalized or None


def _worker_harness_selector(project_root: Path | None = None) -> str | None:
    """Return a harness name only as a worker-document selector.

    The selector narrows the canonical envelope lookup; it never supplies a
    role. A headless dispatch must not inherit the parent harness selector, so
    it falls back to the resolver's ambiguity check unless the dispatcher
    explicitly supplies ``GTKB_HARNESS_NAME`` or a durable harness id.

    Precedence:
    1. Nonblank ``GTKB_HARNESS_NAME`` (explicit document selector).
    2. ``GTKB_BRIDGE_POLLER_RUN_ID`` returns ``None`` so dispatched work
       cannot inherit the parent harness identity.
    3. ``GTKB_HARNESS_ID`` or ``GTKB_AUTHOR_HARNESS_ID`` maps the unique
       durable id through the canonical identity reader
       (``groundtruth_kb.harness_projection.read_identity``). If both are
       present and disagree, the id is unknown or non-unique, or the canonical
       projection is unavailable or malformed, this fails closed (raises
       ``ValueError``) rather than choosing a harness by guess or registration
       order.
    4. No generic id: legacy live markers — ``CLAUDE_CODE_SESSION_ID`` or
       ``CLAUDECODE`` selects Claude, ``CODEX_THREAD_ID`` selects Codex.
    5. Otherwise ``None`` (no justified selector; the canonical envelope
       resolver's exact-match/ambiguity checks govern).
    """
    configured = os.environ.get("GTKB_HARNESS_NAME", "").strip()
    if configured:
        return configured
    if os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID"):
        return None

    durable_a = os.environ.get("GTKB_HARNESS_ID", "").strip()
    durable_b = os.environ.get("GTKB_AUTHOR_HARNESS_ID", "").strip()
    if durable_a or durable_b:
        if durable_a and durable_b and durable_a != durable_b:
            raise ValueError("harness selector conflict: GTKB_HARNESS_ID and GTKB_AUTHOR_HARNESS_ID disagree")
        supplied = durable_a or durable_b
        name = _harness_name_for_durable_id(supplied, project_root)
        if name is not None:
            return name
        raise ValueError(f"harness selector: no registered harness with durable id {supplied!r}")

    if os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDECODE"):
        return "claude"
    if os.environ.get("CODEX_THREAD_ID"):
        return "codex"
    return None


def _harness_name_for_durable_id(harness_id: str, project_root: Path | None) -> str | None:
    """Map a durable harness id to its canonical harness name via the identity SoT.

    Returns ``None`` when the id is not registered. Raises ``ValueError`` when
    the canonical identity projection is unavailable, malformed, or the id maps
    to more than one harness (non-unique), per WI-5841 fail-closed contract.
    """
    try:
        from groundtruth_kb.harness_projection import read_identity
    except ImportError as exc:  # pragma: no cover - install failure is fail-closed
        raise ValueError(f"harness selector: identity projection unavailable: {exc}") from exc
    try:
        identities = read_identity(project_root)
    except Exception as exc:  # noqa: BLE001 - fail closed on any projection error
        raise ValueError(f"harness selector: identity SoT unreadable: {exc}") from exc
    harnesses = identities.get("harnesses")
    if not isinstance(harnesses, dict):
        raise ValueError("harness selector: identity SoT is missing a harness mapping")
    matches: list[str] = []
    for name, record in harnesses.items():
        if isinstance(record, dict) and str(record.get("id") or "") == harness_id:
            matches.append(str(name))
    if not matches:
        return None
    if len(matches) > 1:
        raise ValueError(f"harness selector: durable id {harness_id!r} is not unique")
    return matches[0]


def _resolve_worker_role(session_id: str, *, project_root: Path | None) -> tuple[str | None, str]:
    """Resolve the worker role from the exact validated session document.

    Dispatch metadata and interactive marker files remain useful to their own
    routing/lifecycle surfaces, but they are not claim-role authority. The
    canonical envelope resolver validates the document's identity, open state,
    provenance, and role before this registry can use it.
    """
    try:
        from groundtruth_kb.session.envelope import EnvelopeError, resolve_worker_role_provenance
    except ImportError as exc:  # pragma: no cover - installation failure is fail-closed
        return None, f"worker session document resolver unavailable: {exc}"

    try:
        provenance = resolve_worker_role_provenance(
            _root(project_root),
            current_session_id=session_id,
            harness_name=_worker_harness_selector(project_root),
        )
    except EnvelopeError as exc:
        return None, f"worker session document rejected: {exc}"
    except (OSError, ValueError) as exc:  # pragma: no cover - defensive fail-closed path
        return None, f"worker session document could not be read: {exc}"

    role = provenance.get("role")
    if not isinstance(role, str) or role not in {"prime-builder", "loyal-opposition"}:
        return None, f"worker session document contains unsupported role {role!r}"
    return role, f"worker session document role {role!r}"


def _resolve_acting_role(session_id: str, *, project_root: Path | None) -> str | None:
    """Resolve the document-authoritative role to persist with a claim."""
    role, _detail = _resolve_worker_role(session_id, project_root=project_root)
    return _normalize_claim_role(role)


def _claim_values(
    slug: str,
    session_id: str,
    *,
    ttl_seconds: int,
    project_root: Path | None,
    now: datetime,
    claim_kind: str | None,
    bootstrap_authority: dict[str, Any] | None = None,
) -> dict[str, Any]:
    acquired_at = now
    acting_role = _resolve_acting_role(session_id, project_root=project_root)
    project_id = project_id_for_thread(slug, project_root=project_root)
    if claim_kind is not None:
        if claim_kind == CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP:
            bootstrap = _validate_bootstrap_authority_request(
                slug,
                project_root=project_root,
                acting_role=acting_role,
                project_id=project_id,
                bootstrap_authority=bootstrap_authority,
            )
            ttl_expires_at = acquired_at + timedelta(seconds=ttl_seconds)
            return {
                "thread_slug": slug,
                "session_id": session_id,
                "acquired_at": _iso(acquired_at),
                "ttl_expires_at": _iso(ttl_expires_at),
                "claim_kind": CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP,
                "acting_role": acting_role,
                "project_id": project_id,
                "implementation_deadline": None,
                "implementation_grace_expires_at": None,
                "extensions_used": 0,
                "extension_cap_seconds": None,
                "extension_capped": 0,
                "bootstrap_owner_decision_id": bootstrap["owner_decision_id"],
                "bootstrap_project_id": bootstrap["project_id"],
                "bootstrap_work_item_id": bootstrap["work_item_id"],
                "bootstrap_authorization_id": bootstrap["authorization_id"],
                "bootstrap_carrier_targets": json.dumps(bootstrap["carrier_targets"], sort_keys=True),
                "bootstrap_consumed_at": None,
            }
        if claim_kind == CLAIM_KIND_NO_ACTION_CORRECTION:
            _validate_no_action_correction_request(
                slug,
                project_root=project_root,
                acting_role=acting_role,
            )
            ttl_expires_at = acquired_at + timedelta(seconds=ttl_seconds)
            return {
                "thread_slug": slug,
                "session_id": session_id,
                "acquired_at": _iso(acquired_at),
                "ttl_expires_at": _iso(ttl_expires_at),
                "claim_kind": CLAIM_KIND_NO_ACTION_CORRECTION,
                "acting_role": acting_role,
                "project_id": project_id,
                "implementation_deadline": None,
                "implementation_grace_expires_at": None,
                "extensions_used": 0,
                "extension_cap_seconds": None,
                "extension_capped": 0,
                "bootstrap_owner_decision_id": None,
                "bootstrap_project_id": None,
                "bootstrap_work_item_id": None,
                "bootstrap_authorization_id": None,
                "bootstrap_carrier_targets": None,
                "bootstrap_consumed_at": None,
            }
        else:
            raise WorkIntentRegistryError(f"Unsupported explicit claim kind: {claim_kind!r}")
    if _latest_status(slug, project_root=project_root) == "GO":
        deadline = acquired_at + timedelta(seconds=GO_IMPLEMENTATION_DEADLINE_SECONDS)
        grace_expires = deadline + timedelta(seconds=GO_IMPLEMENTATION_GRACE_SECONDS)
        return {
            "thread_slug": slug,
            "session_id": session_id,
            "acquired_at": _iso(acquired_at),
            "ttl_expires_at": _iso(grace_expires),
            "claim_kind": CLAIM_KIND_GO_IMPLEMENTATION,
            "acting_role": acting_role,
            "project_id": project_id,
            "implementation_deadline": _iso(deadline),
            "implementation_grace_expires_at": _iso(grace_expires),
            "extensions_used": 0,
            "extension_cap_seconds": GO_IMPLEMENTATION_MAX_HOLD_SECONDS,
            "extension_capped": 0,
            "bootstrap_owner_decision_id": None,
            "bootstrap_project_id": None,
            "bootstrap_work_item_id": None,
            "bootstrap_authorization_id": None,
            "bootstrap_carrier_targets": None,
            "bootstrap_consumed_at": None,
        }
    ttl_expires_at = acquired_at + timedelta(seconds=ttl_seconds)
    return {
        "thread_slug": slug,
        "session_id": session_id,
        "acquired_at": _iso(acquired_at),
        "ttl_expires_at": _iso(ttl_expires_at),
        "claim_kind": CLAIM_KIND_DRAFT,
        "acting_role": acting_role,
        "project_id": project_id,
        "implementation_deadline": None,
        "implementation_grace_expires_at": None,
        "extensions_used": 0,
        "extension_cap_seconds": None,
        "extension_capped": 0,
        "bootstrap_owner_decision_id": None,
        "bootstrap_project_id": None,
        "bootstrap_work_item_id": None,
        "bootstrap_authorization_id": None,
        "bootstrap_carrier_targets": None,
        "bootstrap_consumed_at": None,
    }


def _resolve_go_implementation_eligibility(session_id: str, *, project_root: Path | None) -> tuple[bool, str]:
    """Resolve whether ``session_id`` may hold a go_implementation claim."""
    role, detail = _resolve_worker_role(session_id, project_root=project_root)
    return role == "prime-builder", detail


def _go_implementation_eligible(session_id: str, *, project_root: Path | None = None) -> bool:
    """Return True iff ``session_id`` may hold a go_implementation claim.

    Document-authoritative role-eligibility guard (WI-5189); see
    ``_resolve_go_implementation_eligibility`` for the resolution contract.
    """
    return _resolve_go_implementation_eligibility(session_id, project_root=project_root)[0]


def _can_preempt_lingering_draft(existing: dict[str, Any], incoming: dict[str, Any]) -> bool:
    """Return true when a GO implementation claim may replace a draft claim."""
    return (
        incoming.get("claim_kind") == CLAIM_KIND_GO_IMPLEMENTATION
        and existing.get("claim_kind") != CLAIM_KIND_GO_IMPLEMENTATION
    )


def _read_claim_without_schema(thread_slug: str, *, project_root: Path | None) -> dict[str, Any] | None:
    """Read a claim without creating a database, table, column, or index."""
    db_path = _database_path(project_root)
    if not db_path.is_file():
        return None
    try:
        conn = sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute("SELECT * FROM work_intent_claims WHERE thread_slug = ?", (thread_slug,)).fetchone()
        except sqlite3.OperationalError as exc:
            if "no such table" in str(exc).lower():
                return None
            raise
        return _row_to_record(row) if row is not None else None
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Database error during pre-mutation claim read: {exc}") from exc
    finally:
        if "conn" in locals():
            conn.close()


def _claim_operation(
    existing: dict[str, Any] | None,
    incoming: dict[str, Any],
    *,
    session_id: str,
    now: datetime,
) -> str | None:
    if existing is None or _is_expired(existing, now=now) or _is_lapsed_go_implementation(existing, now=now):
        return "work_intent_acquire"
    if existing["session_id"] != session_id and not _can_preempt_lingering_draft(existing, incoming):
        return None
    if existing.get("claim_kind") != incoming.get("claim_kind"):
        return "work_intent_reclassify"
    return "work_intent_renew"


def _run_write_transaction(
    operation: str,
    action: Callable[[sqlite3.Connection], Any],
    *,
    project_root: Path | None,
) -> Any:
    """Run one claim-registry write with bounded, exact-state retry.

    Only transaction-phase ``SQLITE_BUSY``/``SQLITE_LOCKED`` failures are
    retried.  Every attempt owns a fresh connection and a fresh
    ``BEGIN IMMEDIATE`` transaction, so ``action`` must re-read the exact claim
    row before changing it.  Open/schema, corruption, and all other failures
    surface immediately as :class:`WorkIntentDatabaseError`.
    """

    database_path = _database_path(project_root)
    started_at = _monotonic()
    deadline = started_at + WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS
    attempts = 0
    backoff = WORK_INTENT_WRITE_INITIAL_BACKOFF_SECONDS
    last_contention: sqlite3.Error | None = None
    last_contention_phase = "begin_immediate"

    while True:
        if deadline - _monotonic() <= 0 and last_contention is not None:
            raise _database_error(
                last_contention,
                operation=operation,
                phase=last_contention_phase,
                attempts=attempts,
                started_at=started_at,
                database_path=database_path,
                contention_exhausted=True,
            ) from last_contention
        attempts += 1
        remaining = max(0.0, deadline - _monotonic())
        connection_timeout = min(WORK_INTENT_WRITE_ATTEMPT_TIMEOUT_SECONDS, remaining)
        conn = _get_conn(
            project_root,
            timeout_seconds=connection_timeout,
            error_context=(operation, attempts, started_at),
        )
        phase = "begin_immediate"
        try:
            if not _apply_remaining_busy_timeout(conn, deadline=deadline):
                raise _deadline_exhausted_error(
                    operation=operation,
                    phase=phase,
                    attempts=attempts,
                    started_at=started_at,
                    database_path=database_path,
                    last_contention=last_contention,
                )
            conn.execute("BEGIN IMMEDIATE")
            phase = "transaction"
            if not _apply_remaining_busy_timeout(conn, deadline=deadline):
                raise _deadline_exhausted_error(
                    operation=operation,
                    phase=phase,
                    attempts=attempts,
                    started_at=started_at,
                    database_path=database_path,
                    last_contention=last_contention,
                )
            result = action(conn)
            phase = "commit"
            if not _apply_remaining_busy_timeout(conn, deadline=deadline):
                raise _deadline_exhausted_error(
                    operation=operation,
                    phase=phase,
                    attempts=attempts,
                    started_at=started_at,
                    database_path=database_path,
                    last_contention=last_contention,
                )
            conn.commit()
            return result
        except sqlite3.Error as exc:
            try:
                conn.rollback()
            except sqlite3.Error:
                pass
            if not _is_retryable_write_contention(exc):
                raise _database_error(
                    exc,
                    operation=operation,
                    phase=phase,
                    attempts=attempts,
                    started_at=started_at,
                    database_path=database_path,
                ) from exc

            last_contention = exc
            last_contention_phase = phase
            remaining = deadline - _monotonic()
            if remaining <= 0:
                raise _database_error(
                    exc,
                    operation=operation,
                    phase=phase,
                    attempts=attempts,
                    started_at=started_at,
                    database_path=database_path,
                    contention_exhausted=True,
                ) from exc
        except Exception:
            try:
                conn.rollback()
            except sqlite3.Error:
                pass
            raise
        finally:
            conn.close()

        sleep_seconds = min(backoff, max(0.0, deadline - _monotonic()))
        if sleep_seconds <= 0:
            # The loop-top deadline gate reports the most recent SQLite code
            # and phase instead of spinning a zero-time connection.
            continue
        _retry_sleep(sleep_seconds)
        backoff = min(WORK_INTENT_WRITE_MAX_BACKOFF_SECONDS, backoff * 2)


def acquire(
    thread_slug: str,
    session_id: str,
    ttl_seconds: int = DEFAULT_DRAFT_TTL_SECONDS,
    *,
    project_root: Path | None = None,
    claim_kind: str | None = None,
    bootstrap_authority: dict[str, Any] | None = None,
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
    now = now_utc()
    values = _claim_values(
        slug,
        session_id,
        ttl_seconds=ttl_seconds,
        project_root=project_root,
        now=now,
        claim_kind=claim_kind,
        bootstrap_authority=bootstrap_authority,
    )
    existing = _read_claim_without_schema(slug, project_root=project_root)
    operation = _claim_operation(existing, values, session_id=session_id, now=now)
    if operation is None:
        return False
    if existing is not None and not _bootstrap_metadata_matches(existing, values):
        raise WorkIntentRegistryError("Existing project-authorization bootstrap claim metadata differs; release first")
    if values["claim_kind"] == CLAIM_KIND_GO_IMPLEMENTATION:
        eligible, detail = _resolve_go_implementation_eligibility(session_id, project_root=project_root)
        if not eligible:
            raise WorkIntentRegistryError(
                f"go_implementation claim requires a prime-builder harness; "
                f"session {session_id!r} resolves to {detail} (not prime-eligible)"
            )
    if operation == "work_intent_renew" and values["claim_kind"] == CLAIM_KIND_GO_IMPLEMENTATION:
        return True

    def write_claim(conn: sqlite3.Connection) -> bool:
        row = conn.execute("SELECT * FROM work_intent_claims WHERE thread_slug = ?", (slug,)).fetchone()
        transaction_existing = _row_to_record(row) if row is not None else None
        transaction_operation = _claim_operation(transaction_existing, values, session_id=session_id, now=now)
        if transaction_operation is None:
            return False
        if transaction_existing is not None and not _bootstrap_metadata_matches(transaction_existing, values):
            raise WorkIntentRegistryError(
                "Existing project-authorization bootstrap claim metadata differs; release first"
            )
        if transaction_operation != operation:
            raise WorkIntentRegistryError("Work-intent claim changed during authorization; retry the operation")
        if operation == "work_intent_renew":
            conn.execute(
                "UPDATE work_intent_claims SET ttl_expires_at = ? WHERE thread_slug = ? AND session_id = ?",
                (values["ttl_expires_at"], slug, session_id),
            )
            return True
        conn.execute(
            """
            INSERT INTO work_intent_claims
            (thread_slug, session_id, acquired_at, ttl_expires_at, claim_kind,
             acting_role, project_id,
             implementation_deadline, implementation_grace_expires_at,
             extensions_used, extension_cap_seconds, extension_capped,
             bootstrap_owner_decision_id, bootstrap_project_id, bootstrap_work_item_id,
             bootstrap_authorization_id, bootstrap_carrier_targets, bootstrap_consumed_at)
            VALUES
            (:thread_slug, :session_id, :acquired_at, :ttl_expires_at, :claim_kind,
             :acting_role, :project_id,
             :implementation_deadline, :implementation_grace_expires_at,
             :extensions_used, :extension_cap_seconds, :extension_capped,
             :bootstrap_owner_decision_id, :bootstrap_project_id, :bootstrap_work_item_id,
             :bootstrap_authorization_id, :bootstrap_carrier_targets, :bootstrap_consumed_at)
            ON CONFLICT(thread_slug) DO UPDATE SET
                session_id = excluded.session_id,
                acquired_at = excluded.acquired_at,
                ttl_expires_at = excluded.ttl_expires_at,
                claim_kind = excluded.claim_kind,
                acting_role = excluded.acting_role,
                project_id = excluded.project_id,
                implementation_deadline = excluded.implementation_deadline,
                implementation_grace_expires_at = excluded.implementation_grace_expires_at,
                extensions_used = excluded.extensions_used,
                extension_cap_seconds = excluded.extension_cap_seconds,
                extension_capped = excluded.extension_capped,
                bootstrap_owner_decision_id = excluded.bootstrap_owner_decision_id,
                bootstrap_project_id = excluded.bootstrap_project_id,
                bootstrap_work_item_id = excluded.bootstrap_work_item_id,
                bootstrap_authorization_id = excluded.bootstrap_authorization_id,
                bootstrap_carrier_targets = excluded.bootstrap_carrier_targets,
                bootstrap_consumed_at = excluded.bootstrap_consumed_at
            """,
            values,
        )
        return True

    return bool(_run_write_transaction("acquire", write_claim, project_root=project_root))


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
            raise WorkIntentRegistryError(
                f"Thread {slug!r} is not implementation-actionable; implementation timer no longer applies"
            )
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

    def delete_exact_holder(conn: sqlite3.Connection) -> None:
        row = conn.execute(
            "SELECT session_id FROM work_intent_claims WHERE thread_slug = ?",
            (slug,),
        ).fetchone()
        if row is None or str(row["session_id"]) != session_id:
            # Missing is idempotent success.  A replacement or foreign holder
            # is authoritative and must never be deleted by this caller.
            return
        conn.execute(
            "DELETE FROM work_intent_claims WHERE thread_slug = ? AND session_id = ?",
            (slug, session_id),
        )

    _run_write_transaction("release", delete_exact_holder, project_root=project_root)


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


def same_role_project_holder(
    role: str | None,
    project_id: str | None,
    session_id: str,
    *,
    project_root: Path | None = None,
) -> dict[str, Any] | None:
    """Return an active different-session holder for the same role/project.

    Missing role or project metadata fails open by returning ``None``. The guard
    is advisory only; per-thread ``acquire`` remains the correctness boundary.
    """
    canonical_role = _normalize_claim_role(role)
    normalized_project = (project_id or "").strip()
    if not canonical_role or not normalized_project or not session_id:
        return None
    conn = _get_conn(project_root)
    try:
        rows = conn.execute(
            """
            SELECT * FROM work_intent_claims
            WHERE acting_role = ? AND project_id = ? AND session_id != ?
            ORDER BY acquired_at DESC
            """,
            (canonical_role, normalized_project, session_id),
        ).fetchall()
    except sqlite3.Error as exc:
        raise WorkIntentRegistryError(f"Database error during same_role_project_holder: {exc}") from exc
    finally:
        conn.close()

    now = now_utc()
    for row in rows:
        record = _row_to_record(row)
        if _is_expired(record, now=now) or _is_lapsed_go_implementation(record, now=now):
            continue
        return record
    return None


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
    "CLAIM_KIND_NO_ACTION_CORRECTION",
    "CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP",
    "GO_IMPLEMENTATION_AUTO_EXTEND_THRESHOLD_SECONDS",
    "GO_IMPLEMENTATION_DEADLINE_SECONDS",
    "GO_IMPLEMENTATION_EXTENSION_SECONDS",
    "GO_IMPLEMENTATION_GRACE_SECONDS",
    "GO_IMPLEMENTATION_MAX_HOLD_SECONDS",
    "WORK_INTENT_WRITE_ATTEMPT_TIMEOUT_SECONDS",
    "WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS",
    "WorkIntentDatabaseError",
    "WorkIntentRegistryError",
    "WorkIntentWriteContentionError",
    "acquire",
    "bootstrap_authority_from_claim",
    "claim_status",
    "current_holder",
    "extend",
    "lapsed_go_implementation_claims",
    "maybe_auto_extend",
    "project_id_for_thread",
    "revalidate_thread_version",
    "release",
    "same_role_project_holder",
]
