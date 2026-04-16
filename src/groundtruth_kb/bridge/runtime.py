# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Legacy Prime Bridge Runtime - SQLite/MCP synchronous dialog model.

This module is retained for compatibility with projects that still depend on
the older database-backed bridge. New GroundTruth dual-agent projects should
use the file bridge pattern documented in
docs/method/12-file-bridge-automation.md instead.
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast

if TYPE_CHECKING:
    from mcp.server import FastMCP  # optional dep; import suppressed by pyproject.toml mypy overrides

try:
    from mcp.server import FastMCP

    _HAS_MCP = True
except ImportError:
    _HAS_MCP = False


DB_PATH = Path(
    os.environ.get(
        "PRIME_BRIDGE_DB",
        str(Path.home() / ".claude" / "prime-bridge" / "bridge.db"),
    )
)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_bridge_db() -> sqlite3.Connection:
    """Return a connection to the canonical bridge database.

    Always uses the home-directory bridge.db (or PRIME_BRIDGE_DB override).
    Never resolves relative to the workspace CWD. Use this instead of
    sqlite3.connect('bridge.db') to avoid workspace-local DB splits.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


mcp: FastMCP[Any] | None  # forward declaration for mypy --strict (FastMCP is conditionally imported)
if _HAS_MCP:
    mcp = FastMCP(
        name="prime-bridge",
        instructions=(
            "Synchronous local message bridge between Codex and Prime Builder with long-poll notification support."
        ),
    )
else:
    mcp = None

Agent = Literal["codex", "prime", "owner", "any"]
PeerAgent = Literal["codex", "prime"]

PEER_AGENTS = {"codex", "prime"}
ACTIONABLE_INBOX_STATUSES = ("pending",)
FINAL_STATUSES = {"completed", "failed"}
STRUCTURED_RESPONSE_TYPES = {
    "advisory_review",
    "go_no_go",
    "status_update",
    "task_handoff",
    "correction",
    "escalation",
}
SCHEMA_VERSION_CURRENT = 3
MAX_RETRIES = 3
RETRY_BACKOFF_BASE_SECONDS = 60


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _now() -> str:
    """Return the current UTC datetime as an ISO 8601 string."""
    return datetime.now(UTC).isoformat()


def _normalize_json(value: str, expected: type) -> str:
    """Parse ``value`` as JSON, verify it is an instance of ``expected``, and re-serialise it.

    Args:
        value: A JSON-encoded string.
        expected: The Python type the decoded value must match (e.g. ``dict`` or ``list``).

    Returns:
        The canonical JSON string representation of the validated value.

    Raises:
        ValueError: If the decoded value is not an instance of ``expected``.
        json.JSONDecodeError: If ``value`` is not valid JSON.
    """
    parsed = json.loads(value)
    if not isinstance(parsed, expected):
        raise ValueError(f"Expected JSON {expected.__name__}")
    return json.dumps(parsed)


def _loads_json(value: str | None, expected: type, default: Any) -> Any:
    """Safely parse a JSON string, returning ``default`` on failure or type mismatch.

    Args:
        value: A JSON-encoded string, or ``None`` / empty string.
        expected: The Python type the decoded value must match.
        default: Value returned when ``value`` is absent, invalid, or the wrong type.

    Returns:
        The decoded value if valid, otherwise ``default``.
    """
    if value is None or value == "":
        return default
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default
    return parsed if isinstance(parsed, expected) else default


def _parse_iso(value: str | None) -> datetime | None:
    """Parse an ISO 8601 string into a timezone-aware datetime, or return None on failure."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _peer_collaboration_message(sender: str, recipient: str) -> bool:
    """Return True if both sender and recipient are peer agents (codex or prime)."""
    return sender in PEER_AGENTS and recipient in PEER_AGENTS


def _is_absolute_path(p: str) -> bool:
    """Detect absolute paths (Windows drive letters or Unix root)."""
    return bool(p) and (p.startswith("/") or (len(p) >= 3 and p[1] == ":" and p[2] in ("/", "\\")))


def _normalize_artifact_refs(value: Any) -> list[Any]:
    """Return a validated list of artifact refs, keeping only str and dict entries."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, (str, dict))]


def _normalize_action_items(value: Any) -> list[str]:
    """Return a validated list of non-empty action item strings stripped of whitespace."""
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


# ---------------------------------------------------------------------------
# Thread ID resolution (from messages, no threads table)
# ---------------------------------------------------------------------------


def _canonical_thread_id(conn: sqlite3.Connection, correlation_id: str | None) -> str | None:
    """Resolve a correlation ID to its canonical thread ID using the messages table.

    Args:
        conn: An open SQLite connection with ``row_factory`` set.
        correlation_id: The correlation ID to resolve, or ``None``.

    Returns:
        The canonical thread ID string, or ``None`` if unresolvable.
    """
    if not correlation_id:
        return None
    row = conn.execute(
        """
        SELECT COALESCE(NULLIF(thread_id, ''), id) AS canonical_thread_id
        FROM messages
        WHERE id = ? OR thread_id = ?
        ORDER BY created_at ASC
        LIMIT 1
        """,
        (correlation_id, correlation_id),
    ).fetchone()
    if row is None:
        return correlation_id
    return str(row["canonical_thread_id"])


def _thread_id_for(
    conn: sqlite3.Connection,
    message_id: str,
    correlation_id: str | None,
) -> str:
    """Return the thread ID for a new message, falling back to the message's own ID."""
    return _canonical_thread_id(conn, correlation_id) or message_id


# ---------------------------------------------------------------------------
# Message kind inference
# ---------------------------------------------------------------------------


def _infer_message_kind(
    *,
    sender: str,
    subject: str,
    payload: dict[str, Any],
    tags: list[str],
) -> str:
    """Classify a message as ``"protocol_ack"``, ``"status_update"``, ``"system"``, or ``"substantive"``.

    Args:
        sender: The agent or user sending the message.
        subject: The message subject line.
        payload: Parsed payload dict from the message.
        tags: List of tag strings associated with the message.

    Returns:
        A message kind string used to drive bridge validation and dispatch logic.
    """
    response_type = str(payload.get("response_type", "") or "").lower()
    subject_lower = (subject or "").strip().lower()
    tag_set = {str(tag).strip().lower() for tag in tags}

    if (
        subject_lower.startswith("accepted:")
        or subject_lower.startswith("negotiation:")
        or response_type in {"accepted", "negotiation"}
        or ("protocol" in tag_set and ("accepted" in tag_set or "negotiation" in tag_set))
    ):
        return "protocol_ack"
    if response_type == "status_update":
        return "status_update"
    if "system" in tag_set or sender == "owner":
        return "system"
    return "substantive"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_message_contract(
    *,
    sender: str,
    recipient: str,
    message_kind: str,
    payload: dict[str, Any],
) -> list[str]:
    """Validate a message against the substantive-reply-only bridge contract.

    Args:
        sender: The sending agent identifier.
        recipient: The receiving agent identifier.
        message_kind: Inferred message kind (e.g. ``"substantive"``).
        payload: Parsed payload dict from the message.

    Returns:
        A list of validation error strings; empty means the message is valid.
    """
    if not _peer_collaboration_message(sender, recipient):
        return []
    if sender == recipient:
        return [f"self-addressed peer messages are not allowed: sender and recipient are both {sender}"]
    if message_kind == "protocol_ack":
        return ["protocol acknowledgements are no longer supported; send a substantive reply instead"]

    errors: list[str] = []
    expected_response = str(payload.get("expected_response", "") or "").strip()
    artifact_refs = _normalize_artifact_refs(payload.get("artifact_refs"))
    action_items = _normalize_action_items(payload.get("action_items"))

    if not expected_response:
        errors.append("missing expected_response in payload")
    elif expected_response not in STRUCTURED_RESPONSE_TYPES:
        errors.append(f"invalid expected_response: {expected_response}")

    if message_kind in ("substantive", "status_update"):
        if not artifact_refs:
            errors.append("missing artifact_refs in payload")
        if not action_items:
            errors.append("missing action_items in payload")

    for ref in artifact_refs:
        if isinstance(ref, dict):
            ref_path = str(ref.get("path", ""))
            if ref_path and _is_absolute_path(ref_path):
                errors.append(f"artifact_refs contains absolute path: {ref_path[:60]}")

    return errors


def _validate_thread_correlation(
    conn: sqlite3.Connection,
    *,
    sender: str,
    recipient: str,
    correlation_id: str | None,
    message_kind: str,
    payload: dict[str, Any],
) -> list[str]:
    """Validate that the correlation ID links both sender and recipient to an existing thread.

    Args:
        conn: An open SQLite connection with ``row_factory`` set.
        sender: The sending agent identifier.
        recipient: The receiving agent identifier.
        correlation_id: The correlation / thread ID supplied with the message.
        message_kind: Inferred message kind.
        payload: Parsed payload dict from the message.

    Returns:
        A list of validation error strings; empty means the correlation is valid.
    """
    if not _peer_collaboration_message(sender, recipient):
        return []

    response_type = str(payload.get("response_type", "") or "").lower()
    if response_type in {"status_update", "correction"} and not correlation_id:
        return ["missing correlation_id for reply-like peer message"]
    if not correlation_id:
        return []

    thread_id = _canonical_thread_id(conn, correlation_id)
    if not thread_id:
        return [f"unknown correlation_id: {correlation_id}"]

    participants = _thread_participants(conn, thread_id)
    if sender in PEER_AGENTS and sender not in participants:
        return [f"correlation_id not linked to sender thread: {correlation_id}"]
    if recipient in PEER_AGENTS and recipient not in participants:
        return [f"correlation_id not linked to recipient thread: {correlation_id}"]
    return []


def _thread_participants(conn: sqlite3.Connection, thread_id: str) -> set[str]:
    """Derive participants from messages (no threads table)."""
    rows = conn.execute(
        "SELECT DISTINCT sender, recipient FROM messages WHERE thread_id = ?",
        (thread_id,),
    ).fetchall()
    participants = set()
    for row in rows:
        if row["sender"] in PEER_AGENTS:
            participants.add(row["sender"])
        if row["recipient"] in PEER_AGENTS:
            participants.add(row["recipient"])
    return participants


# ---------------------------------------------------------------------------
# Thread state derivation (replaces cached threads table)
# ---------------------------------------------------------------------------


def _derive_thread_state(conn: sqlite3.Connection, thread_id: str) -> dict[str, Any] | None:
    """Compute thread state from messages. Replaces the old threads table cache."""
    rows = conn.execute(
        "SELECT * FROM messages WHERE thread_id = ? ORDER BY created_at ASC",
        (thread_id,),
    ).fetchall()
    if not rows:
        return None

    items = [_row_to_dict(row) for row in rows]
    root = items[0]
    latest = items[-1]
    substantive = [item for item in items if item.get("message_kind") in {"substantive", "status_update", "system"}]
    latest_substantive = substantive[-1] if substantive else root
    participants = sorted(
        {party for item in items for party in (item.get("sender"), item.get("recipient")) if party in PEER_AGENTS}
    )

    latest_status = latest_substantive.get("status") or latest.get("status", "pending")
    if latest_status in FINAL_STATUSES:
        current_assignee = None
    else:
        recipient = latest_substantive.get("recipient")
        current_assignee = recipient if recipient in PEER_AGENTS else None

    return {
        "thread_id": thread_id,
        "root_message_id": root["id"],
        "status": latest_status,
        "current_assignee": current_assignee,
        "last_message_id": latest["id"],
        "last_substantive_message_id": latest_substantive["id"],
        "last_substantive_sender": latest_substantive.get("sender"),
        "last_substantive_at": latest_substantive.get("created_at"),
        "artifact_refs": latest_substantive.get("artifact_refs", []),
        "latest_summary": latest_substantive.get("subject", ""),
        "participants": participants,
        "message_count": len(items),
        "created_at": root.get("created_at") or _now(),
        "updated_at": latest.get("created_at") or _now(),
    }


def _thread_items(conn: sqlite3.Connection, thread_id: str) -> list[dict[str, Any]]:
    """Return all messages in a thread ordered chronologically."""
    rows = conn.execute(
        "SELECT * FROM messages WHERE thread_id = ? ORDER BY created_at ASC",
        (thread_id,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


# ---------------------------------------------------------------------------
# Row conversion
# ---------------------------------------------------------------------------


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a SQLite Row to a plain dict with JSON fields decoded to Python objects."""
    item = dict(row)
    item["payload"] = _loads_json(item.get("payload"), dict, {})
    item["tags"] = _loads_json(item.get("tags"), list, [])
    item["artifact_refs"] = _loads_json(item.get("artifact_refs"), list, [])
    return item


def _recipient_matches(agent: str, recipient: str) -> bool:
    """Return True if the message recipient matches the given agent (exact or ``"any"``)."""
    return recipient in {agent, "any"}


def _thread_correlation_id(row: sqlite3.Row) -> str:
    """Return the best available thread or correlation ID from a message row."""
    return cast(str, row["thread_id"] or row["correlation_id"] or row["id"])


def _message_is_protocol_ack(item: dict[str, Any]) -> bool:
    """Return True if the message dict represents a legacy protocol acknowledgement."""
    if item.get("message_kind") == "protocol_ack":
        return True
    subject = (item.get("subject") or "").strip().lower()
    payload = item.get("payload") or {}
    tags = set(item.get("tags") or [])
    response_type = str(payload.get("response_type", "")).lower()
    if subject.startswith("accepted:") or subject.startswith("negotiation:"):
        return True
    if response_type in {"accepted", "negotiation"}:
        return True
    if "protocol" in tags and ("accepted" in tags or "negotiation" in tags):
        return True
    return False


def _notification_targets(recipient: str) -> list[str]:
    """Expand the recipient field to a list of agent notification targets.

    Args:
        recipient: The message recipient (``"codex"``, ``"prime"``, or ``"any"``).

    Returns:
        A list of agent identifiers that should receive a notification.
    """
    if recipient == "any":
        return ["codex", "prime"]
    return [recipient]


# ---------------------------------------------------------------------------
# Notification queue
# ---------------------------------------------------------------------------


def _queue_notification(
    conn: sqlite3.Connection,
    agent: str,
    event_type: str,
    message_id: str | None,
    subject: str,
    details: dict[str, Any],
) -> int:
    """Insert a notification row for an agent and return the new event ID.

    Args:
        conn: An open SQLite connection.
        agent: The agent that should receive the notification.
        event_type: The event type string (e.g. ``"message.new"``).
        message_id: The message ID the notification relates to, if any.
        subject: The message subject line for display purposes.
        details: A dict of additional event details serialised as JSON.

    Returns:
        The ``event_id`` of the newly inserted notification row.

    Raises:
        RuntimeError: If the INSERT does not return a row ID.
    """
    cur = conn.execute(
        """
        INSERT INTO notifications (agent, event_type, message_id, subject, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (agent, event_type, message_id, subject, json.dumps(details), _now()),
    )
    row_id = cur.lastrowid
    if row_id is None:
        raise RuntimeError("INSERT INTO notifications failed to return a row ID")
    return int(row_id)


# ---------------------------------------------------------------------------
# Message insert
# ---------------------------------------------------------------------------


def _insert_message(
    conn: sqlite3.Connection,
    sender: Agent,
    recipient: Agent,
    subject: str,
    body: str,
    payload: dict[str, Any],
    tags: list[str],
    priority: int,
    correlation_id: str | None,
) -> tuple[str, str, list[str], list[int]]:
    """Insert a new message into the database, validate it, queue notifications, and return metadata.

    Args:
        conn: An open SQLite connection.
        sender: The sending agent or ``"owner"``.
        recipient: The receiving agent or ``"any"``.
        subject: The message subject line.
        body: The message body text.
        payload: Parsed payload dict.
        tags: List of tag strings.
        priority: Integer priority 0–3.
        correlation_id: Thread correlation ID, or ``None`` for a new thread.

    Returns:
        A tuple of ``(message_id, status, validation_errors, event_ids)``.
    """
    message_kind = _infer_message_kind(
        sender=sender,
        subject=subject,
        payload=payload,
        tags=tags,
    )
    validation_errors = _validate_message_contract(
        sender=sender,
        recipient=recipient,
        message_kind=message_kind,
        payload=payload,
    )
    validation_errors.extend(
        _validate_thread_correlation(
            conn,
            sender=sender,
            recipient=recipient,
            correlation_id=correlation_id,
            message_kind=message_kind,
            payload=payload,
        )
    )

    status = "failed" if validation_errors else "pending"
    if validation_errors:
        payload["validation_errors"] = validation_errors

    message_id = str(uuid.uuid4())
    thread_id = _thread_id_for(conn, message_id, correlation_id)
    artifact_refs = _normalize_artifact_refs(payload.get("artifact_refs"))

    conn.execute(
        """
        INSERT INTO messages (
            id, sender, recipient, subject, body, payload, tags,
            priority, status, correlation_id, created_at, schema_version,
            thread_id, message_kind, artifact_refs
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            message_id,
            sender,
            recipient,
            subject,
            body,
            json.dumps(payload),
            json.dumps(tags),
            priority,
            status,
            correlation_id,
            _now(),
            SCHEMA_VERSION_CURRENT,
            thread_id,
            message_kind,
            json.dumps(artifact_refs),
        ),
    )

    event_ids = []
    event_type = "message.failed" if validation_errors else "message.new"
    targets = _notification_targets(recipient)
    if validation_errors and sender in PEER_AGENTS and sender not in targets:
        targets.append(sender)
    for target in targets:
        event_ids.append(
            _queue_notification(
                conn,
                target,
                event_type,
                message_id,
                subject,
                {
                    "sender": sender,
                    "recipient": recipient,
                    "priority": priority,
                    "correlation_id": correlation_id,
                    "thread_id": thread_id,
                    "message_kind": message_kind,
                    "status": status,
                    "validation_errors": validation_errors,
                },
            )
        )

    return message_id, status, validation_errors, event_ids


# ---------------------------------------------------------------------------
# Schema & migration
# ---------------------------------------------------------------------------


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create all required tables and indexes and run any pending schema migrations."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            payload TEXT NOT NULL DEFAULT '{}',
            tags TEXT NOT NULL DEFAULT '[]',
            priority INTEGER NOT NULL DEFAULT 2,
            status TEXT NOT NULL DEFAULT 'pending',
            correlation_id TEXT,
            thread_id TEXT,
            created_at TEXT NOT NULL,
            resolved_at TEXT,
            resolution TEXT,
            schema_version INTEGER NOT NULL DEFAULT 3,
            message_kind TEXT NOT NULL DEFAULT 'substantive',
            artifact_refs TEXT NOT NULL DEFAULT '[]'
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_messages_inbox
        ON messages(recipient, status, priority DESC, created_at ASC)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_messages_thread
        ON messages(thread_id, created_at ASC)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_messages_thread_covering
        ON messages(thread_id, created_at, status, sender, recipient)
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            event_type TEXT NOT NULL,
            message_id TEXT,
            subject TEXT NOT NULL DEFAULT '',
            details TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_notifications_agent_event
        ON notifications(agent, event_id)
        """
    )

    user_version = int(conn.execute("PRAGMA user_version").fetchone()[0] or 0)
    if user_version < SCHEMA_VERSION_CURRENT:
        _migrate_to_v3(conn, user_version)
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION_CURRENT}")


def _migrate_to_v3(conn: sqlite3.Connection, from_version: int) -> None:
    """One-time migration: collapse 7 states -> 3, merge structured fields into payload, drop threads."""
    columns = {row[1] for row in conn.execute("PRAGMA table_info(messages)").fetchall()}
    if not columns:
        return  # Fresh DB, no migration needed

    # Back up the DB file before destructive migration
    if DB_PATH.exists():
        backup_path = DB_PATH.with_suffix(f".v{from_version}.bak")
        if not backup_path.exists():
            shutil.copy2(DB_PATH, backup_path)

    # Phase 1: Merge structured fields into payload JSON for each row
    has_expected_response = "expected_response" in columns
    has_response_window = "response_window" in columns
    has_action_items = "action_items" in columns
    has_validation_errors = "validation_errors" in columns

    if any([has_expected_response, has_response_window, has_action_items, has_validation_errors]):
        rows = conn.execute(
            "SELECT id, payload, expected_response, response_window, action_items, validation_errors FROM messages"
        ).fetchall()
        for row in rows:
            payload = _loads_json(row["payload"], dict, {})
            changed = False
            if has_expected_response and row["expected_response"]:
                er = str(row["expected_response"]).strip()
                if er and "expected_response" not in payload:
                    payload["expected_response"] = er
                    changed = True
            if has_response_window and row["response_window"]:
                rw = str(row["response_window"]).strip()
                if rw and "response_window" not in payload:
                    payload["response_window"] = rw
                    changed = True
            if has_action_items:
                ai = _loads_json(row["action_items"], list, [])
                if ai and "action_items" not in payload:
                    payload["action_items"] = ai
                    changed = True
            if has_validation_errors:
                ve = _loads_json(row["validation_errors"], list, [])
                if ve and "validation_errors" not in payload:
                    payload["validation_errors"] = ve
                    changed = True
            if changed:
                conn.execute(
                    "UPDATE messages SET payload = ? WHERE id = ?",
                    (json.dumps(payload), row["id"]),
                )

    # Phase 2: Map statuses
    status_map = {
        "new": "pending",
        "pending": "pending",
        "claimed": "pending",
        "done": "completed",
        "blocked": "failed",
        "superseded": "failed",
        "invalid": "failed",
    }
    for old_status, new_status in status_map.items():
        conn.execute(
            "UPDATE messages SET status = ? WHERE status = ?",
            (new_status, old_status),
        )

    # Phase 3: Update schema_version
    conn.execute(f"UPDATE messages SET schema_version = {SCHEMA_VERSION_CURRENT}")

    # Phase 4: Drop deprecated columns by recreating the table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages_v3 (
            id TEXT PRIMARY KEY,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            payload TEXT NOT NULL DEFAULT '{}',
            tags TEXT NOT NULL DEFAULT '[]',
            priority INTEGER NOT NULL DEFAULT 2,
            status TEXT NOT NULL DEFAULT 'pending',
            correlation_id TEXT,
            thread_id TEXT,
            created_at TEXT NOT NULL,
            resolved_at TEXT,
            resolution TEXT,
            schema_version INTEGER NOT NULL DEFAULT 3,
            message_kind TEXT NOT NULL DEFAULT 'substantive',
            artifact_refs TEXT NOT NULL DEFAULT '[]'
        )
        """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO messages_v3
            (id, sender, recipient, subject, body, payload, tags, priority,
             status, correlation_id, thread_id, created_at, resolved_at,
             resolution, schema_version, message_kind, artifact_refs)
        SELECT id, sender, recipient, subject, body, payload, tags, priority,
               status, correlation_id, thread_id, created_at, resolved_at,
               resolution, schema_version, message_kind, artifact_refs
        FROM messages
        """
    )
    conn.execute("DROP TABLE messages")
    conn.execute("ALTER TABLE messages_v3 RENAME TO messages")

    # Recreate indexes after table replacement
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_inbox ON messages(recipient, status, priority DESC, created_at ASC)"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id, created_at ASC)")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_thread_covering ON messages(thread_id, created_at, status, sender, recipient)"
    )

    # Phase 5: Drop threads table
    conn.execute("DROP TABLE IF EXISTS threads")

    # Phase 6: Clean up stale notification event types
    conn.execute(
        "DELETE FROM notifications WHERE event_type IN ('message.claimed', 'thread.ack_breach', 'thread.response_window_breach', 'thread.updated')"
    )


def _conn() -> sqlite3.Connection:
    """Open a WAL-mode SQLite connection with the schema ensured."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _ensure_schema(conn)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Notification helpers
# ---------------------------------------------------------------------------


def _list_notifications(agent: str, after_event_id: int, limit: int) -> list[dict[str, Any]]:
    """Query notification rows for an agent after a given event ID.

    Args:
        agent: The agent identifier to filter by.
        after_event_id: Only return events with ``event_id > after_event_id``.
        limit: Maximum number of rows to return (1–200).

    Returns:
        A list of notification row dicts ordered by ascending ``event_id``.

    Raises:
        ValueError: If ``limit`` is outside the range 1–200.
    """
    if limit < 1 or limit > 200:
        raise ValueError("limit must be between 1 and 200")
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM notifications
            WHERE agent = ? AND event_id > ?
            ORDER BY event_id ASC
            LIMIT ?
            """,
            (agent, after_event_id, limit),
        ).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["details"] = _loads_json(item.get("details"), dict, {})
        items.append(item)
    return items


def _latest_notification_event_id(agent: str | None = None) -> int:
    """Return the maximum notification event ID, optionally scoped to a single agent."""
    with _conn() as conn:
        if agent:
            row = conn.execute(
                "SELECT COALESCE(MAX(event_id), 0) AS max_event_id FROM notifications WHERE agent = ?",
                (agent,),
            ).fetchone()
        else:
            row = conn.execute("SELECT COALESCE(MAX(event_id), 0) AS max_event_id FROM notifications").fetchone()
    if row is None:
        return 0
    return int(row["max_event_id"] or 0)


# ---------------------------------------------------------------------------
# Context builders (used by workers)
# ---------------------------------------------------------------------------


def resolve_message_reference(
    message_ref: str,
    recipient: Literal["codex", "prime"] | None = None,
) -> dict[str, Any] | None:
    """Resolve a message reference to a single message dict, or None if ambiguous or missing.

    Tries an exact UUID match first, then a prefix (LIKE) match.  Returns None if the
    prefix matches more than one row.

    Args:
        message_ref: Full or prefix UUID string.
        recipient: If given, restricts the lookup to messages for this agent.

    Returns:
        A deserialized message dict, or ``None``.
    """
    if not message_ref:
        return None
    with _conn() as conn:
        if recipient:
            exact_row = conn.execute(
                """
                SELECT * FROM messages
                WHERE id = ? AND (recipient = ? OR recipient = 'any' OR sender = ?)
                LIMIT 1
                """,
                (message_ref, recipient, recipient),
            ).fetchone()
        else:
            exact_row = conn.execute(
                "SELECT * FROM messages WHERE id = ? LIMIT 1",
                (message_ref,),
            ).fetchone()
        if exact_row is not None:
            return _row_to_dict(exact_row)

        like_ref = f"{message_ref}%"
        if recipient:
            rows = conn.execute(
                """
                SELECT * FROM messages
                WHERE id LIKE ? AND (recipient = ? OR recipient = 'any' OR sender = ?)
                ORDER BY created_at DESC
                LIMIT 3
                """,
                (like_ref, recipient, recipient),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM messages WHERE id LIKE ? ORDER BY created_at DESC LIMIT 3",
                (like_ref,),
            ).fetchall()

    if len(rows) == 1:
        return _row_to_dict(rows[0])
    return None


def get_thread_messages(
    message_ref: str,
    recipient: PeerAgent | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Return all messages in the thread containing the referenced message.

    Args:
        message_ref: Any message ID in the target thread.
        recipient: Optional agent filter passed to ``resolve_message_reference``.
        limit: Maximum number of messages to return.

    Returns:
        A list of deserialized message dicts ordered by creation time.
    """
    resolved = resolve_message_reference(message_ref, recipient=recipient)
    if resolved is None:
        return []
    thread_id = resolved.get("thread_id") or resolved.get("correlation_id") or resolved["id"]
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE thread_id = ? ORDER BY created_at ASC LIMIT ?",
            (thread_id, limit),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def describe_thread_context(
    message_ref: str,
    recipient: PeerAgent | None = None,
    limit: int = 100,
) -> dict[str, Any] | None:
    """Return a rich thread context dict for the referenced message, or None if not found.

    Args:
        message_ref: Any message ID in the target thread.
        recipient: Optional agent filter.
        limit: Maximum number of thread messages to retrieve.

    Returns:
        A dict with ``canonical_message``, ``thread_messages``, ``thread_state``,
        ``latest_non_protocol_codex_message``, ``latest_non_protocol_prime_message``,
        ``terminal_messages``, and ``already_resolved``; or ``None``.
    """
    resolved = resolve_message_reference(message_ref, recipient=recipient)
    if resolved is None:
        return None

    thread_messages = get_thread_messages(resolved["id"], recipient=recipient, limit=limit)
    non_protocol = [item for item in thread_messages if not _message_is_protocol_ack(item)]
    latest_non_protocol_codex = next(
        (item for item in reversed(non_protocol) if item.get("sender") == "codex"),
        None,
    )
    latest_non_protocol_prime = next(
        (item for item in reversed(non_protocol) if item.get("sender") == "prime"),
        None,
    )
    terminal_messages = [item for item in thread_messages if item.get("status") in FINAL_STATUSES]

    thread_id = resolved.get("thread_id") or resolved["id"]
    with _conn() as conn:
        thread_state = _derive_thread_state(conn, thread_id)

    return {
        "requested_ref": message_ref,
        "canonical_message": resolved,
        "thread_correlation_id": thread_id,
        "thread_state": thread_state,
        "thread_messages": thread_messages,
        "latest_thread_message": thread_messages[-1] if thread_messages else resolved,
        "latest_non_protocol_codex_message": latest_non_protocol_codex,
        "latest_non_protocol_prime_message": latest_non_protocol_prime,
        "terminal_messages": terminal_messages,
        "already_resolved": resolved.get("status") in FINAL_STATUSES,
    }


def build_worker_event_payload(
    message_ref: str,
    recipient: PeerAgent | None = None,
    limit: int = 100,
) -> dict[str, Any] | None:
    """Build a flattened worker event payload dict from the thread context.

    Args:
        message_ref: Any message ID in the target thread.
        recipient: Optional agent filter.
        limit: Maximum number of thread messages to retrieve.

    Returns:
        A dict suitable for passing to a bridge worker, or ``None`` if the thread
        cannot be resolved.
    """
    context = describe_thread_context(message_ref, recipient=recipient, limit=limit)
    if context is None:
        return None

    canonical = context.get("canonical_message") or {}
    thread_state = context.get("thread_state") or {}
    canonical_payload = canonical.get("payload") or {}
    return {
        "requested_ref": context.get("requested_ref", message_ref),
        "thread_correlation_id": context.get("thread_correlation_id"),
        "canonical_message": canonical,
        "thread_state": thread_state,
        "thread_messages": context.get("thread_messages", []),
        "latest_thread_message": context.get("latest_thread_message"),
        "latest_non_protocol_codex_message": context.get("latest_non_protocol_codex_message"),
        "latest_non_protocol_prime_message": context.get("latest_non_protocol_prime_message"),
        "terminal_messages": context.get("terminal_messages", []),
        "already_resolved": context.get("already_resolved", False),
        "artifact_refs": canonical.get("artifact_refs", []),
        "expected_response": canonical_payload.get("expected_response", ""),
        "action_items": canonical_payload.get("action_items", []),
        "latest_summary": thread_state.get("latest_summary", ""),
        "participants": thread_state.get("participants", []),
    }


# ===========================================================================
# Public API functions (usable with or without MCP)
# ===========================================================================


def send_message(
    sender: Agent,
    recipient: Agent,
    subject: str,
    body: str,
    payload_json: str = "{}",
    tags_json: str = "[]",
    priority: int = 2,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    """Send a message through the bridge."""
    if recipient not in {"codex", "prime", "any"}:
        raise ValueError("recipient must be one of: codex, prime, any")
    if sender not in {"codex", "prime", "owner"}:
        raise ValueError("sender must be one of: codex, prime, owner")
    if priority < 0 or priority > 3:
        raise ValueError("priority must be between 0 and 3")

    payload_normalized = _normalize_json(payload_json, dict)
    tags_normalized = _normalize_json(tags_json, list)

    with _conn() as conn:
        message_id, status, validation_errors, event_ids = _insert_message(
            conn,
            sender,
            recipient,
            subject,
            body,
            json.loads(payload_normalized),
            json.loads(tags_normalized),
            priority,
            correlation_id,
        )
        conn.commit()

    return {
        "ok": True,
        "id": message_id,
        "status": status,
        "validation_errors": validation_errors,
        "notification_event_ids": event_ids,
    }


def send_correction_message(
    sender: PeerAgent,
    failed_message_id: str,
    guidance: str,
    artifact_refs_json: str = "[]",
    priority: int = 1,
) -> dict[str, Any]:
    """Send a correction for a failed (formerly invalid) message."""
    if sender not in PEER_AGENTS:
        raise ValueError("sender must be one of: codex, prime")
    if priority < 0 or priority > 3:
        raise ValueError("priority must be between 0 and 3")

    artifact_refs = json.loads(_normalize_json(artifact_refs_json, list))
    guidance_text = (guidance or "").strip()

    with _conn() as conn:
        failed_row = conn.execute(
            "SELECT * FROM messages WHERE id = ?",
            (failed_message_id,),
        ).fetchone()
        if failed_row is None:
            return {
                "ok": False,
                "id": None,
                "status": "missing",
                "validation_errors": [f"unknown failed_message_id: {failed_message_id}"],
                "notification_event_ids": [],
            }
        if failed_row["status"] != "failed":
            return {
                "ok": False,
                "id": failed_message_id,
                "status": str(failed_row["status"]),
                "validation_errors": [f"message is not failed: {failed_message_id}"],
                "notification_event_ids": [],
            }
        if failed_row["sender"] not in PEER_AGENTS or failed_row["recipient"] not in PEER_AGENTS:
            return {
                "ok": False,
                "id": failed_message_id,
                "status": "unsupported",
                "validation_errors": ["correction helper only supports peer-to-peer failed messages"],
                "notification_event_ids": [],
            }

        recipient = cast(Agent, str(failed_row["sender"]))  # narrowed: sender ∈ PEER_AGENTS verified above
        thread_id = _thread_correlation_id(failed_row)

        # Dedup: check if correction already sent
        correction_rows = conn.execute(
            "SELECT * FROM messages WHERE thread_id = ? AND sender = ? AND recipient = ? ORDER BY created_at DESC",
            (thread_id, sender, recipient),
        ).fetchall()
        for row in correction_rows:
            row_dict = _row_to_dict(row)
            payload = row_dict.get("payload") or {}
            if row_dict.get("status") != "failed" and str(payload.get("response_type", "")).lower() == "correction":
                return {
                    "ok": True,
                    "id": row_dict["id"],
                    "status": row_dict["status"],
                    "validation_errors": [],
                    "notification_event_ids": [],
                    "deduped": True,
                }

        subject = f"Correction: failed bridge message {failed_message_id}"
        body = guidance_text or (
            "This message was not processed because the bridge persisted it as failed. "
            "Please review the thread and resend only if further bridge work is still needed."
        )
        payload = {
            "response_type": "correction",
            "expected_response": "status_update",
            "artifact_refs": artifact_refs,
            "action_items": [
                "Send a substantive follow-up only if further bridge action is still needed",
                "Resend the original request only if the thread still needs work after reviewing this correction",
            ],
            "failed_message_id": failed_message_id,
        }
        tags = ["bridge-sync", "correction", "system"]
        message_id, status, validation_errors, event_ids = _insert_message(
            conn,
            sender,
            recipient,
            subject,
            body,
            payload,
            tags,
            priority,
            failed_message_id,
        )
        conn.commit()

    return {
        "ok": True,
        "id": message_id,
        "status": status,
        "validation_errors": validation_errors,
        "notification_event_ids": event_ids,
        "deduped": False,
    }


def list_inbox(
    agent: PeerAgent,
    status: Literal["pending", "completed", "failed", "all"] = "pending",
    limit: int = 20,
) -> dict[str, Any]:
    """List messages for an agent's inbox."""
    if limit < 1 or limit > 200:
        raise ValueError("limit must be between 1 and 200")

    where = "(recipient = ? OR recipient = 'any')"
    params: list[object] = [agent]
    if status != "all":
        where += " AND status = ?"
        params.append(status)
    params.append(limit)

    with _conn() as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM messages
            WHERE {where}
            ORDER BY priority DESC, created_at ASC
            LIMIT ?
            """,
            params,
        ).fetchall()

    items = [_row_to_dict(row) for row in rows]
    return {"count": len(items), "items": items}


def list_stale_outbound(
    sender: PeerAgent,
    older_than_seconds: int = 180,
    limit: int = 500,
) -> dict[str, Any]:
    """List pending messages sent BY this agent that are older than a threshold.

    Used by the autonomous retry sweep to find outbound messages that haven't
    received a peer response. Unlike list_inbox (which is recipient-facing and
    capped at 200), this is sender-facing and supports higher limits.
    """
    if older_than_seconds < 1:
        raise ValueError("older_than_seconds must be at least 1")
    if limit < 1 or limit > 2000:
        raise ValueError("limit must be between 1 and 2000")

    cutoff = datetime.now(UTC)
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM messages
            WHERE sender = ? AND status = 'pending'
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (sender, limit),
        ).fetchall()

    items = []
    for row in rows:
        item = _row_to_dict(row)
        created_at = _parse_iso(item.get("created_at"))
        if created_at is None:
            continue
        age_seconds = (cutoff - created_at).total_seconds()
        if age_seconds >= older_than_seconds:
            items.append(item)

    return {"count": len(items), "items": items}


def resolve_message(
    message_id: str,
    agent: Literal["codex", "prime", "owner"],
    outcome: Literal["completed", "failed"] = "completed",
    resolution: str = "",
) -> dict[str, Any]:
    """Mark a message as completed or failed."""
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM messages WHERE id = ?",
            (message_id,),
        ).fetchone()
        if row is None:
            return {"ok": False, "id": message_id, "status": "missing"}

        row_dict = _row_to_dict(row)
        allowed = agent == "owner" or row_dict.get("recipient") == agent or row_dict.get("recipient") == "any"
        if not allowed:
            return {"ok": False, "id": message_id, "status": "forbidden"}

        cur = conn.execute(
            "UPDATE messages SET status = ?, resolution = ?, resolved_at = ? WHERE id = ?",
            (outcome, resolution, _now(), message_id),
        )
        if cur.rowcount == 1 and row["sender"] in PEER_AGENTS:
            _queue_notification(
                conn,
                row["sender"],
                "message.resolved",
                message_id,
                row["subject"],
                {
                    "resolved_by": agent,
                    "outcome": outcome,
                    "resolution": resolution,
                    "thread_id": _thread_correlation_id(row),
                },
            )
        conn.commit()

    return {
        "ok": cur.rowcount == 1,
        "id": message_id,
        "status": outcome if cur.rowcount == 1 else "unchanged",
    }


def retry_pending_message(
    message_id: str,
    agent: PeerAgent,
) -> dict[str, Any]:
    """Non-blocking persistent retry: re-queue notification for a pending message.

    Increments retry metadata in the payload. Caps at MAX_RETRIES to prevent storms.
    """
    with _conn() as conn:
        row = conn.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
        if row is None:
            return {"ok": False, "id": message_id, "reason": "missing"}
        if row["status"] != "pending":
            return {"ok": False, "id": message_id, "reason": f"status is {row['status']}, not pending"}
        if not _recipient_matches(agent, row["recipient"]):
            return {"ok": False, "id": message_id, "reason": "wrong recipient"}

        payload = _loads_json(row["payload"], dict, {})
        retry = payload.get("_retry", {"count": 0, "max": MAX_RETRIES})
        if retry.get("count", 0) >= retry.get("max", MAX_RETRIES):
            return {"ok": False, "id": message_id, "reason": "max retries exceeded", "retry_count": retry["count"]}

        retry["count"] = retry.get("count", 0) + 1
        retry["last_at"] = _now()
        retry["max"] = retry.get("max", MAX_RETRIES)
        payload["_retry"] = retry
        conn.execute(
            "UPDATE messages SET payload = ? WHERE id = ?",
            (json.dumps(payload), message_id),
        )

        event_id = _queue_notification(
            conn,
            row["recipient"] if row["recipient"] != "any" else agent,
            "message.new",
            message_id,
            row["subject"],
            {
                "sender": row["sender"],
                "recipient": row["recipient"],
                "retry_count": retry["count"],
                "thread_id": row["thread_id"],
            },
        )
        conn.commit()

    return {
        "ok": True,
        "id": message_id,
        "retry_count": retry["count"],
        "notification_event_id": event_id,
    }


def clear_failed_messages(
    agent: PeerAgent,
    older_than_minutes: int = 60,
    limit: int = 50,
    resolution: str = "auto-cleared",
) -> dict[str, Any]:
    """Bulk-clear old failed messages."""
    if older_than_minutes < 1 or older_than_minutes > 10080:
        raise ValueError("older_than_minutes must be between 1 and 10080")
    if limit < 1 or limit > 200:
        raise ValueError("limit must be between 1 and 200")

    with _conn() as conn:
        cutoff = datetime.now(UTC)
        rows = conn.execute(
            """
            SELECT * FROM messages
            WHERE (recipient = ? OR recipient = 'any') AND status = 'failed'
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (agent, limit * 2),
        ).fetchall()

        cleared_items = []
        for row in rows:
            created_at = _parse_iso(row["created_at"])
            if created_at is None:
                continue
            age_minutes = (cutoff - created_at).total_seconds() / 60
            if age_minutes < older_than_minutes:
                continue
            conn.execute(
                "UPDATE messages SET status = 'failed', resolution = ?, resolved_at = ? WHERE id = ?",
                (resolution, _now(), row["id"]),
            )
            cleared_items.append(_row_to_dict(row))
            if len(cleared_items) >= limit:
                break
        conn.commit()

    return {
        "ok": True,
        "agent": agent,
        "older_than_minutes": older_than_minutes,
        "cleared_count": len(cleared_items),
        "cleared_ids": [item["id"] for item in cleared_items],
        "cleared_items": cleared_items,
    }


def list_notifications(
    agent: PeerAgent,
    after_event_id: int = 0,
    limit: int = 20,
) -> dict[str, Any]:
    """List notifications for an agent."""
    items = _list_notifications(agent, after_event_id, limit)
    last_event_id = items[-1]["event_id"] if items else after_event_id
    return {"count": len(items), "last_event_id": last_event_id, "items": items}


def get_latest_notification_event_id(agent: PeerAgent | None = None) -> dict[str, Any]:
    """Get the latest notification event ID."""
    return {
        "agent": agent,
        "last_event_id": _latest_notification_event_id(agent),
    }


def wait_for_notifications(
    agent: PeerAgent,
    after_event_id: int = 0,
    timeout_seconds: int = 15,
    poll_interval_ms: int = 100,
    limit: int = 20,
) -> dict[str, Any]:
    """Long-poll for new notifications."""
    if timeout_seconds < 1 or timeout_seconds > 60:
        raise ValueError("timeout_seconds must be between 1 and 60")
    if poll_interval_ms < 50 or poll_interval_ms > 2000:
        raise ValueError("poll_interval_ms must be between 50 and 2000")

    deadline = time.monotonic() + timeout_seconds
    while True:
        items = _list_notifications(agent, after_event_id, limit)
        if items:
            return {
                "notified": True,
                "count": len(items),
                "last_event_id": items[-1]["event_id"],
                "items": items,
            }
        if time.monotonic() >= deadline:
            return {
                "notified": False,
                "count": 0,
                "last_event_id": after_event_id,
                "items": [],
            }
        time.sleep(poll_interval_ms / 1000)


def get_thread(thread_ref: str, agent: PeerAgent | None = None) -> dict[str, Any]:
    """Get full thread context."""
    context = describe_thread_context(thread_ref, recipient=agent)
    return {"ok": context is not None, "thread": context}


def get_worker_event_payload(thread_ref: str, agent: PeerAgent | None = None) -> dict[str, Any]:
    """Get thread context structured for worker dispatch."""
    context = build_worker_event_payload(thread_ref, recipient=agent)
    return {"ok": context is not None, "context": context}


def list_threads(
    agent: PeerAgent,
    status: Literal["open", "final", "all"] = "open",
    limit: int = 20,
) -> dict[str, Any]:
    """List threads for an agent, derived from messages."""
    if limit < 1 or limit > 200:
        raise ValueError("limit must be between 1 and 200")

    with _conn() as conn:
        thread_ids_rows = conn.execute(
            """
            SELECT DISTINCT thread_id FROM messages
            WHERE thread_id IS NOT NULL AND thread_id != ''
            ORDER BY thread_id
            """,
        ).fetchall()

        items = []
        for tid_row in thread_ids_rows:
            thread_id = tid_row["thread_id"]
            state = _derive_thread_state(conn, thread_id)
            if state is None:
                continue
            if agent not in state["participants"]:
                continue
            if status == "final" and state["status"] not in FINAL_STATUSES:
                continue
            if status == "open" and state["status"] in FINAL_STATUSES:
                continue
            items.append(state)
            if len(items) >= limit:
                break

    # Sort by most recently updated first
    items.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return {"count": len(items), "items": items}


def health() -> str:
    """Health check: message counts + notification summary."""
    with _conn() as conn:
        message_rows = conn.execute("SELECT status, COUNT(*) AS n FROM messages GROUP BY status").fetchall()
        notification_rows = conn.execute("SELECT agent, COUNT(*) AS n FROM notifications GROUP BY agent").fetchall()
        max_event_id = conn.execute("SELECT COALESCE(MAX(event_id), 0) AS max_event_id FROM notifications").fetchone()[
            "max_event_id"
        ]
        pending_by_agent = conn.execute(
            """
            SELECT recipient, COUNT(*) AS n FROM messages
            WHERE status = 'pending'
            GROUP BY recipient
            """
        ).fetchall()

    return json.dumps(
        {
            "db_path": str(DB_PATH),
            "schema_version_current": SCHEMA_VERSION_CURRENT,
            "features": [
                "synchronous-dialog",
                "notifications-long-poll",
                "substantive-replies-only",
                "non-blocking-retry",
                "thread-derived-from-messages",
            ],
            "max_event_id": max_event_id,
            "messages": {row["status"]: row["n"] for row in message_rows},
            "notifications": {row["agent"]: row["n"] for row in notification_rows},
            "pending_by_agent": {row["recipient"]: row["n"] for row in pending_by_agent},
        },
        indent=2,
    )


# ===========================================================================
# MCP Tool registration (only when FastMCP is available)
# ===========================================================================


def _register_mcp_tools() -> None:
    """Register all public API functions as MCP tools."""
    if mcp is None:
        return

    mcp.tool()(send_message)
    mcp.tool()(send_correction_message)
    mcp.tool()(list_inbox)
    mcp.tool()(list_stale_outbound)
    mcp.tool()(resolve_message)
    mcp.tool()(retry_pending_message)
    mcp.tool()(clear_failed_messages)
    mcp.tool()(list_notifications)
    mcp.tool()(get_latest_notification_event_id)
    mcp.tool()(wait_for_notifications)
    mcp.tool()(get_thread)
    mcp.tool()(get_worker_event_payload)
    mcp.tool()(list_threads)

    @mcp.resource("bridge://health")  # type: ignore[misc]
    def _health_resource() -> str:
        """Serve the bridge health JSON as an MCP resource."""
        return health()


_register_mcp_tools()


if __name__ == "__main__":
    if mcp is not None:
        mcp.run(transport="stdio")
    else:
        print("MCP (FastMCP) is not installed. Install 'mcp' package for MCP server support.")
