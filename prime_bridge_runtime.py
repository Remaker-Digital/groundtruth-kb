from __future__ import annotations

import json
import os
import site
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal


PROJECT_ROOT = Path(__file__).resolve().parent
VENDORED_DEPS = PROJECT_ROOT / ".codex_pydeps"
if VENDORED_DEPS.exists():
    site.addsitedir(str(VENDORED_DEPS))

from mcp.server import FastMCP


DB_PATH = Path(
    os.environ.get(
        "PRIME_BRIDGE_DB",
        str(Path.home() / ".claude" / "prime-bridge" / "bridge.db"),
    )
)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

mcp = FastMCP(
    name="prime-bridge",
    instructions=(
        "Asynchronous local message bridge between Codex and Prime Builder "
        "with long-poll notification support."
    ),
)

Agent = Literal["codex", "prime", "owner", "any"]
PeerAgent = Literal["codex", "prime"]

PEER_AGENTS = {"codex", "prime"}
ACTIONABLE_INBOX_STATUSES = ("new", "pending")
CLAIMABLE_STATUSES = ("new", "pending")
FINAL_STATUSES = {"done", "blocked", "superseded"}
STRUCTURED_RESPONSE_TYPES = {
    "advisory_review",
    "go_no_go",
    "acknowledgement",
    "status_update",
    "task_handoff",
    "negotiation",
    "correction",
    "escalation",
}
STRUCTURED_RESPONSE_WINDOWS = {"immediate", "short", "session", "async"}
SCHEMA_VERSION_LEGACY = 1
SCHEMA_VERSION_CURRENT = 2
ACK_DEADLINE_SECONDS = 60
CLAIMED_THREAD_SILENCE_SECONDS = 10 * 60
RESPONSE_WINDOW_SECONDS = {
    "immediate": 2 * 60,
    "short": 10 * 60,
    "session": 8 * 60 * 60,
    "async": 24 * 60 * 60,
}
REPLY_LIKE_RESPONSE_TYPES = {"accepted", "negotiation", "status_update", "correction"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_json(value: str, expected: type) -> str:
    parsed = json.loads(value)
    if not isinstance(parsed, expected):
        raise ValueError(f"Expected JSON {expected.__name__}")
    return json.dumps(parsed)


def _loads_json(value: str | None, expected: type, default: Any) -> Any:
    if value in (None, ""):
        return default
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default
    return parsed if isinstance(parsed, expected) else default


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _peer_collaboration_message(sender: str, recipient: str) -> bool:
    return sender in PEER_AGENTS and recipient in PEER_AGENTS


def _canonical_thread_id(conn: sqlite3.Connection, correlation_id: str | None) -> str | None:
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
    return _canonical_thread_id(conn, correlation_id) or message_id


def _normalize_artifact_refs(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, (str, dict))]


def _normalize_action_items(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _extract_structured_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_refs": _normalize_artifact_refs(payload.get("artifact_refs")),
        "expected_response": str(payload.get("expected_response", "") or "").strip(),
        "response_window": str(payload.get("response_window", "") or "").strip(),
        "action_items": _normalize_action_items(payload.get("action_items")),
    }


def _response_window_seconds(response_window: str) -> int | None:
    return RESPONSE_WINDOW_SECONDS.get((response_window or "").strip().lower())


def _reply_like_peer_message(
    *,
    sender: str,
    recipient: str,
    message_kind: str,
    payload: dict[str, Any],
    structured: dict[str, Any],
) -> bool:
    if not _peer_collaboration_message(sender, recipient):
        return False
    if message_kind in {"protocol_ack", "status_update"}:
        return True

    response_type = str(payload.get("response_type", "") or "").strip().lower()
    if response_type in REPLY_LIKE_RESPONSE_TYPES:
        return True
    return False


def _infer_message_kind(
    *,
    sender: str,
    subject: str,
    payload: dict[str, Any],
    tags: list[str],
    expected_response: str,
) -> str:
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
    if expected_response == "status_update" or response_type == "status_update":
        return "status_update"
    if "system" in tag_set or sender == "owner":
        return "system"
    return "substantive"


def _validate_message_contract(
    *,
    sender: str,
    recipient: str,
    message_kind: str,
    structured: dict[str, Any],
) -> list[str]:
    if not _peer_collaboration_message(sender, recipient):
        return []
    if message_kind == "protocol_ack":
        return []

    errors: list[str] = []
    expected_response = structured["expected_response"]
    response_window = structured["response_window"]
    artifact_refs = structured["artifact_refs"]
    action_items = structured["action_items"]

    if not expected_response:
        errors.append("missing expected_response")
    elif expected_response not in STRUCTURED_RESPONSE_TYPES:
        errors.append(f"invalid expected_response: {expected_response}")

    if not response_window:
        errors.append("missing response_window")
    elif response_window not in STRUCTURED_RESPONSE_WINDOWS:
        errors.append(f"invalid response_window: {response_window}")

    if message_kind == "substantive":
        if not artifact_refs:
            errors.append("missing artifact_refs")
        if not action_items:
            errors.append("missing action_items")

    return errors


def _validate_thread_correlation(
    conn: sqlite3.Connection,
    *,
    sender: str,
    recipient: str,
    correlation_id: str | None,
    message_kind: str,
    payload: dict[str, Any],
    structured: dict[str, Any],
) -> list[str]:
    if not _peer_collaboration_message(sender, recipient):
        return []

    reply_like = _reply_like_peer_message(
        sender=sender,
        recipient=recipient,
        message_kind=message_kind,
        payload=payload,
        structured=structured,
    )
    if reply_like and not correlation_id:
        return ["missing correlation_id for reply-like peer message"]
    if not correlation_id:
        return []

    thread_id = _canonical_thread_id(conn, correlation_id)
    if not thread_id:
        return [f"unknown correlation_id: {correlation_id}"]

    row = conn.execute(
        "SELECT participants FROM threads WHERE thread_id = ?",
        (thread_id,),
    ).fetchone()
    if row is None:
        rebuilt = _upsert_thread_state(conn, thread_id, emit_notifications=False)
        if rebuilt is not None:
            row = conn.execute(
                "SELECT participants FROM threads WHERE thread_id = ?",
                (thread_id,),
            ).fetchone()
    if row is None:
        return [f"unknown correlation_id: {correlation_id}"]

    participants = _loads_json(row["participants"], list, [])
    if sender in PEER_AGENTS and sender not in participants:
        return [f"correlation_id not linked to sender thread: {correlation_id}"]
    if recipient in PEER_AGENTS and recipient not in participants:
        return [f"correlation_id not linked to recipient thread: {correlation_id}"]
    return []


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {str(row[1]) for row in rows}


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    if column not in _table_columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def _compute_thread_snapshot(conn: sqlite3.Connection, thread_id: str) -> dict[str, Any] | None:
    rows = conn.execute(
        "SELECT * FROM messages WHERE thread_id = ? ORDER BY created_at ASC",
        (thread_id,),
    ).fetchall()
    if not rows:
        return None

    items = [_row_to_dict(row) for row in rows]
    root = items[0]
    substantive = [
        item
        for item in items
        if item.get("message_kind") in {"substantive", "status_update", "system"}
    ]
    latest = items[-1]
    latest_substantive = substantive[-1] if substantive else root
    latest_claimed = next(
        (
            item
            for item in reversed(items)
            if item.get("status") == "claimed" and item.get("claimed_by") in PEER_AGENTS
        ),
        None,
    )
    latest_final = next(
        (
            item
            for item in reversed(items)
            if item.get("status") in FINAL_STATUSES
        ),
        None,
    )
    participants = sorted(
        {
            party
            for item in items
            for party in (item.get("sender"), item.get("recipient"))
            if party in PEER_AGENTS
        }
    )
    if latest_final is not None:
        current_status = latest_final.get("status") or "done"
        current_assignee = None
        current_claimed_at = None
    elif latest_claimed is not None:
        current_status = "claimed"
        current_assignee = latest_claimed.get("claimed_by")
        current_claimed_at = latest_claimed.get("claimed_at")
    else:
        current_status = latest_substantive.get("status") or latest.get("status") or "new"
        current_assignee = latest_substantive.get("claimed_by")
        current_claimed_at = latest_substantive.get("claimed_at")
    if not current_assignee and current_status not in FINAL_STATUSES:
        recipient = latest_substantive.get("recipient")
        current_assignee = recipient if recipient in PEER_AGENTS else None

    return {
        "thread_id": thread_id,
        "root_message_id": root["id"],
        "status": current_status,
        "current_assignee": current_assignee,
        "current_claimed_at": current_claimed_at,
        "last_message_id": latest["id"],
        "last_substantive_message_id": latest_substantive["id"],
        "last_substantive_sender": latest_substantive.get("sender"),
        "last_substantive_at": latest_substantive.get("created_at"),
        "expected_response": latest_substantive.get("expected_response", ""),
        "response_window": latest_substantive.get("response_window", ""),
        "artifact_refs": latest_substantive.get("artifact_refs", []),
        "latest_summary": latest_substantive.get("subject", ""),
        "participants": participants,
        "message_count": len(items),
        "created_at": root.get("created_at") or _now(),
        "updated_at": latest.get("created_at") or _now(),
    }


def _thread_row_to_dict(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
    item = dict(row)
    if not isinstance(item.get("artifact_refs"), list):
        item["artifact_refs"] = _loads_json(item.get("artifact_refs"), list, [])
    if not isinstance(item.get("participants"), list):
        item["participants"] = _loads_json(item.get("participants"), list, [])
    return item


def _thread_items(conn: sqlite3.Connection, thread_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM messages WHERE thread_id = ? ORDER BY created_at ASC",
        (thread_id,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def _thread_sla_snapshot(
    conn: sqlite3.Connection,
    thread: sqlite3.Row | dict[str, Any],
    *,
    now: datetime | None = None,
    silence_seconds: int = CLAIMED_THREAD_SILENCE_SECONDS,
) -> dict[str, Any]:
    thread_item = _thread_row_to_dict(thread)
    items = _thread_items(conn, thread_item["thread_id"])
    now = now or datetime.now(timezone.utc)

    latest_substantive = next(
        (
            item
            for item in reversed(items)
            if item.get("message_kind") in {"substantive", "status_update", "system"}
        ),
        None,
    )
    assignee = thread_item.get("current_assignee")
    current_status = thread_item.get("status")
    sla_eligible = current_status not in FINAL_STATUSES and current_status != "invalid"
    latest_request = None
    latest_assignee_response = None
    if assignee in PEER_AGENTS:
        latest_request = next(
            (
                item
                for item in reversed(items)
                if item.get("sender") != assignee
                and item.get("sender") in PEER_AGENTS
                and item.get("recipient") in PEER_AGENTS
                and item.get("message_kind") in {"substantive", "status_update", "system"}
            ),
            None,
        )
        if latest_request is not None:
            request_at = _parse_iso(latest_request.get("created_at"))
            latest_assignee_response = next(
                (
                    item
                    for item in items
                    if item.get("sender") == assignee
                    and (request_at is None or (_parse_iso(item.get("created_at")) or now) > request_at)
                ),
                None,
            )

    ack_breach = False
    ack_overdue_seconds = 0
    ack_due_at = None
    response_window_breach = False
    response_overdue_seconds = 0
    response_due_at = None
    if latest_request is not None and latest_assignee_response is None and sla_eligible:
        request_at = _parse_iso(latest_request.get("created_at"))
        if request_at is not None:
            age_seconds = int((now - request_at).total_seconds())
            ack_due_at = (request_at.timestamp() + ACK_DEADLINE_SECONDS)
            if age_seconds > ACK_DEADLINE_SECONDS:
                ack_breach = True
                ack_overdue_seconds = age_seconds - ACK_DEADLINE_SECONDS
            window_seconds = _response_window_seconds(
                latest_request.get("response_window") or thread_item.get("response_window", "")
            )
            if window_seconds is not None:
                response_due_at = request_at.timestamp() + window_seconds
                if age_seconds > window_seconds:
                    response_window_breach = True
                    response_overdue_seconds = age_seconds - window_seconds

    silence_breach = False
    silence_overdue_seconds = 0
    silence_due_at = None
    last_assignee_activity_at = None
    if current_status == "claimed" and assignee in PEER_AGENTS:
        baseline = _parse_iso(thread_item.get("current_claimed_at"))
        latest_assignee_activity_at = next(
            (
                _parse_iso(item.get("created_at"))
                for item in reversed(items)
                if item.get("sender") == assignee and not _message_is_protocol_ack(item)
            ),
            None,
        )
        if latest_assignee_activity_at is not None and (
            baseline is None or latest_assignee_activity_at > baseline
        ):
            baseline = latest_assignee_activity_at
        if baseline is not None:
            silence_seconds_elapsed = int((now - baseline).total_seconds())
            silence_due_at = baseline.timestamp() + silence_seconds
            if silence_seconds_elapsed > silence_seconds:
                silence_breach = True
                silence_overdue_seconds = silence_seconds_elapsed - silence_seconds

    risk_types: list[str] = []
    if ack_breach:
        risk_types.append("ack_breach")
    if response_window_breach:
        risk_types.append("response_window_breach")
    if silence_breach:
        risk_types.append("claimed_thread_silence_breach")

    return {
        "thread_id": thread_item["thread_id"],
        "responsible_agent": assignee,
        "latest_substantive_message_id": latest_substantive.get("id") if latest_substantive else None,
        "latest_request_message_id": latest_request.get("id") if latest_request else None,
        "latest_assignee_response_message_id": latest_assignee_response.get("id") if latest_assignee_response else None,
        "ack_breach": ack_breach,
        "ack_due_at": datetime.fromtimestamp(ack_due_at, tz=timezone.utc).isoformat() if ack_due_at else None,
        "ack_overdue_seconds": ack_overdue_seconds,
        "response_window_breach": response_window_breach,
        "response_due_at": datetime.fromtimestamp(response_due_at, tz=timezone.utc).isoformat()
        if response_due_at
        else None,
        "response_overdue_seconds": response_overdue_seconds,
        "claimed_thread_silence_breach": silence_breach,
        "silence_due_at": datetime.fromtimestamp(silence_due_at, tz=timezone.utc).isoformat()
        if silence_due_at
        else None,
        "silence_overdue_seconds": silence_overdue_seconds,
        "last_assignee_activity_at": last_assignee_activity_at.isoformat()
        if last_assignee_activity_at
        else None,
        "risk_types": risk_types,
    }


def _queue_thread_breach_notifications(
    conn: sqlite3.Connection,
    snapshot: dict[str, Any],
) -> None:
    thread_row = conn.execute(
        """
        SELECT ack_breach_notified_at, response_breach_notified_at, silence_breach_notified_at
        FROM threads
        WHERE thread_id = ?
        """,
        (snapshot["thread_id"],),
    ).fetchone()
    if thread_row is None:
        return

    sla = _thread_sla_snapshot(conn, snapshot)
    thread_item = _thread_row_to_dict(snapshot)
    now = _now()
    checks = [
        (
            "ack_breach",
            sla["ack_breach"],
            "ack_breach_notified_at",
            "thread.ack_breach",
            {
                "thread_id": snapshot["thread_id"],
                "current_assignee": snapshot.get("current_assignee"),
                "latest_request_message_id": sla.get("latest_request_message_id"),
                "ack_due_at": sla.get("ack_due_at"),
                "ack_overdue_seconds": sla.get("ack_overdue_seconds"),
            },
        ),
        (
            "response_window_breach",
            sla["response_window_breach"],
            "response_breach_notified_at",
            "thread.response_window_breach",
            {
                "thread_id": snapshot["thread_id"],
                "current_assignee": snapshot.get("current_assignee"),
                "latest_request_message_id": sla.get("latest_request_message_id"),
                "response_window": snapshot.get("response_window"),
                "response_due_at": sla.get("response_due_at"),
                "response_overdue_seconds": sla.get("response_overdue_seconds"),
            },
        ),
        (
            "claimed_thread_silence_breach",
            sla["claimed_thread_silence_breach"],
            "silence_breach_notified_at",
            "thread.claimed_silence_breach",
            {
                "thread_id": snapshot["thread_id"],
                "current_assignee": snapshot.get("current_assignee"),
                "last_assignee_activity_at": sla.get("last_assignee_activity_at"),
                "silence_due_at": sla.get("silence_due_at"),
                "silence_overdue_seconds": sla.get("silence_overdue_seconds"),
            },
        ),
    ]

    updates: dict[str, Any] = {}
    for _, active, column, event_type, details in checks:
        notified_at = thread_row[column]
        if active and not notified_at:
            for agent in thread_item.get("participants", []):
                _queue_notification(
                    conn,
                    agent,
                    event_type,
                    snapshot.get("last_substantive_message_id"),
                    snapshot.get("latest_summary", ""),
                    details,
                )
            updates[column] = now
        elif not active and notified_at:
            updates[column] = None

    if updates:
        assignments = ", ".join(f"{column} = ?" for column in updates)
        conn.execute(
            f"UPDATE threads SET {assignments} WHERE thread_id = ?",
            (*updates.values(), snapshot["thread_id"]),
        )


def _queue_thread_update_notifications(
    conn: sqlite3.Connection,
    previous: dict[str, Any] | None,
    current: dict[str, Any],
) -> None:
    changed = previous is None or any(
        previous.get(key) != current.get(key)
        for key in (
            "status",
            "current_assignee",
            "current_claimed_at",
            "last_substantive_at",
            "last_substantive_message_id",
        )
    )
    if not changed:
        return

    details = {
        "thread_id": current["thread_id"],
        "status": current["status"],
        "current_assignee": current["current_assignee"],
        "last_substantive_message_id": current["last_substantive_message_id"],
        "last_substantive_at": current["last_substantive_at"],
    }
    for agent in current.get("participants", []):
        _queue_notification(
            conn,
            agent,
            "thread.updated",
            current.get("last_substantive_message_id"),
            current.get("latest_summary", ""),
            details,
        )


def _upsert_thread_state(
    conn: sqlite3.Connection,
    thread_id: str,
    *,
    emit_notifications: bool,
) -> dict[str, Any] | None:
    snapshot = _compute_thread_snapshot(conn, thread_id)
    if snapshot is None:
        return None

    previous_row = conn.execute(
        "SELECT * FROM threads WHERE thread_id = ?",
        (thread_id,),
    ).fetchone()
    previous = None
    if previous_row is not None:
        previous = dict(previous_row)
        previous["artifact_refs"] = _loads_json(previous.get("artifact_refs"), list, [])
        previous["participants"] = _loads_json(previous.get("participants"), list, [])

    conn.execute(
        """
        INSERT INTO threads (
            thread_id,
            root_message_id,
            status,
            current_assignee,
            current_claimed_at,
            last_message_id,
            last_substantive_message_id,
            last_substantive_sender,
            last_substantive_at,
            expected_response,
            response_window,
            artifact_refs,
            latest_summary,
            participants,
            message_count,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(thread_id) DO UPDATE SET
            root_message_id = excluded.root_message_id,
            status = excluded.status,
            current_assignee = excluded.current_assignee,
            current_claimed_at = excluded.current_claimed_at,
            last_message_id = excluded.last_message_id,
            last_substantive_message_id = excluded.last_substantive_message_id,
            last_substantive_sender = excluded.last_substantive_sender,
            last_substantive_at = excluded.last_substantive_at,
            expected_response = excluded.expected_response,
            response_window = excluded.response_window,
            artifact_refs = excluded.artifact_refs,
            latest_summary = excluded.latest_summary,
            participants = excluded.participants,
            message_count = excluded.message_count,
            updated_at = excluded.updated_at
        """,
        (
            snapshot["thread_id"],
            snapshot["root_message_id"],
            snapshot["status"],
            snapshot["current_assignee"],
            snapshot["current_claimed_at"],
            snapshot["last_message_id"],
            snapshot["last_substantive_message_id"],
            snapshot["last_substantive_sender"],
            snapshot["last_substantive_at"],
            snapshot["expected_response"],
            snapshot["response_window"],
            json.dumps(snapshot["artifact_refs"]),
            snapshot["latest_summary"],
            json.dumps(snapshot["participants"]),
            snapshot["message_count"],
            snapshot["created_at"],
            snapshot["updated_at"],
        ),
    )

    if emit_notifications:
        _queue_thread_update_notifications(conn, previous, snapshot)
        _queue_thread_breach_notifications(conn, snapshot)
    return snapshot


def _backfill_messages(conn: sqlite3.Connection) -> None:
    rows = conn.execute("SELECT * FROM messages ORDER BY created_at ASC").fetchall()
    for row in rows:
        item = dict(row)
        payload = _loads_json(item.get("payload"), dict, {})
        tags = _loads_json(item.get("tags"), list, [])
        structured = _extract_structured_fields(payload)
        thread_id = _thread_id_for(conn, item["id"], item.get("correlation_id"))
        message_kind = _infer_message_kind(
            sender=str(item.get("sender", "")),
            subject=str(item.get("subject", "")),
            payload=payload,
            tags=tags,
            expected_response=structured["expected_response"],
        )
        conn.execute(
            """
            UPDATE messages
            SET thread_id = ?,
                message_kind = COALESCE(NULLIF(message_kind, ''), ?),
                schema_version = COALESCE(schema_version, ?),
                artifact_refs = COALESCE(NULLIF(artifact_refs, ''), ?),
                expected_response = COALESCE(NULLIF(expected_response, ''), ?),
                response_window = COALESCE(NULLIF(response_window, ''), ?),
                action_items = COALESCE(NULLIF(action_items, ''), ?),
                validation_errors = COALESCE(NULLIF(validation_errors, ''), '[]')
            WHERE id = ?
            """,
            (
                thread_id,
                message_kind,
                SCHEMA_VERSION_LEGACY,
                json.dumps(structured["artifact_refs"]),
                structured["expected_response"],
                structured["response_window"],
                json.dumps(structured["action_items"]),
                item["id"],
            ),
        )


def _backfill_threads(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        "SELECT DISTINCT thread_id FROM messages WHERE thread_id IS NOT NULL AND thread_id != ''"
    ).fetchall()
    for row in rows:
        _upsert_thread_state(conn, str(row[0]), emit_notifications=False)


def _ensure_schema(conn: sqlite3.Connection) -> None:
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
            status TEXT NOT NULL DEFAULT 'new',
            correlation_id TEXT,
            created_at TEXT NOT NULL,
            claimed_by TEXT,
            claimed_at TEXT,
            resolved_at TEXT,
            resolution TEXT,
            schema_version INTEGER NOT NULL DEFAULT 1,
            thread_id TEXT,
            message_kind TEXT NOT NULL DEFAULT 'substantive',
            artifact_refs TEXT NOT NULL DEFAULT '[]',
            expected_response TEXT NOT NULL DEFAULT '',
            response_window TEXT NOT NULL DEFAULT '',
            action_items TEXT NOT NULL DEFAULT '[]',
            validation_errors TEXT NOT NULL DEFAULT '[]'
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS threads (
            thread_id TEXT PRIMARY KEY,
            root_message_id TEXT NOT NULL,
            status TEXT NOT NULL,
            current_assignee TEXT,
            current_claimed_at TEXT,
            last_message_id TEXT,
            last_substantive_message_id TEXT,
            last_substantive_sender TEXT,
            last_substantive_at TEXT,
            expected_response TEXT NOT NULL DEFAULT '',
            response_window TEXT NOT NULL DEFAULT '',
            artifact_refs TEXT NOT NULL DEFAULT '[]',
            latest_summary TEXT NOT NULL DEFAULT '',
            participants TEXT NOT NULL DEFAULT '[]',
            message_count INTEGER NOT NULL DEFAULT 0,
            ack_breach_notified_at TEXT,
            response_breach_notified_at TEXT,
            silence_breach_notified_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_threads_status_assignee
        ON threads(status, current_assignee, updated_at DESC)
        """
    )
    _ensure_column(conn, "messages", "schema_version", "INTEGER NOT NULL DEFAULT 1")
    _ensure_column(conn, "messages", "thread_id", "TEXT")
    _ensure_column(conn, "messages", "message_kind", "TEXT NOT NULL DEFAULT 'substantive'")
    _ensure_column(conn, "messages", "artifact_refs", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(conn, "messages", "expected_response", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "messages", "response_window", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "messages", "action_items", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(conn, "messages", "validation_errors", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(conn, "threads", "ack_breach_notified_at", "TEXT")
    _ensure_column(conn, "threads", "response_breach_notified_at", "TEXT")
    _ensure_column(conn, "threads", "silence_breach_notified_at", "TEXT")
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_messages_thread
        ON messages(thread_id, created_at ASC)
        """
    )
    user_version = int(conn.execute("PRAGMA user_version").fetchone()[0] or 0)
    thread_count = int(conn.execute("SELECT COUNT(*) FROM threads").fetchone()[0] or 0)
    message_count = int(conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0] or 0)
    null_thread_count = int(
        conn.execute(
            "SELECT COUNT(*) FROM messages WHERE thread_id IS NULL OR thread_id = ''"
        ).fetchone()[0] or 0
    )
    if user_version < SCHEMA_VERSION_CURRENT:
        _backfill_messages(conn)
        _backfill_threads(conn)
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION_CURRENT}")
    elif null_thread_count > 0:
        _backfill_messages(conn)
        _backfill_threads(conn)
    elif thread_count == 0 and message_count > 0:
        _backfill_threads(conn)


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _ensure_schema(conn)
    conn.commit()
    return conn


def _row_to_dict(row: sqlite3.Row) -> dict:
    item = dict(row)
    item["payload"] = _loads_json(item.get("payload"), dict, {})
    item["tags"] = _loads_json(item.get("tags"), list, [])
    item["artifact_refs"] = _loads_json(item.get("artifact_refs"), list, [])
    item["action_items"] = _loads_json(item.get("action_items"), list, [])
    item["validation_errors"] = _loads_json(item.get("validation_errors"), list, [])
    return item


def _recipient_matches(agent: str, recipient: str) -> bool:
    return recipient in {agent, "any"}


def _thread_correlation_id(row: sqlite3.Row) -> str:
    return row["thread_id"] or row["correlation_id"] or row["id"]


def _message_is_protocol_ack(item: dict) -> bool:
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
    if recipient == "any":
        return ["codex", "prime"]
    return [recipient]


def _queue_notification(
    conn: sqlite3.Connection,
    agent: str,
    event_type: str,
    message_id: str | None,
    subject: str,
    details: dict,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO notifications (agent, event_type, message_id, subject, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (agent, event_type, message_id, subject, json.dumps(details), _now()),
    )
    return int(cur.lastrowid)


def _insert_message(
    conn: sqlite3.Connection,
    sender: Agent,
    recipient: Agent,
    subject: str,
    body: str,
    payload: dict,
    tags: list[str],
    priority: int,
    correlation_id: str | None,
) -> tuple[str, str, list[str], list[int]]:
    structured = _extract_structured_fields(payload)
    message_kind = _infer_message_kind(
        sender=sender,
        subject=subject,
        payload=payload,
        tags=tags,
        expected_response=structured["expected_response"],
    )
    validation_errors = _validate_message_contract(
        sender=sender,
        recipient=recipient,
        message_kind=message_kind,
        structured=structured,
    )
    validation_errors.extend(
        _validate_thread_correlation(
            conn,
            sender=sender,
            recipient=recipient,
            correlation_id=correlation_id,
            message_kind=message_kind,
            payload=payload,
            structured=structured,
        )
    )
    status = "invalid" if validation_errors else "new"
    message_id = str(uuid.uuid4())
    thread_id = _thread_id_for(conn, message_id, correlation_id)
    conn.execute(
        """
        INSERT INTO messages (
            id, sender, recipient, subject, body, payload, tags,
            priority, status, correlation_id, created_at, schema_version,
            thread_id, message_kind, artifact_refs, expected_response,
            response_window, action_items, validation_errors
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            json.dumps(structured["artifact_refs"]),
            structured["expected_response"],
            structured["response_window"],
            json.dumps(structured["action_items"]),
            json.dumps(validation_errors),
        ),
    )
    event_ids = []
    event_type = "message.invalid" if validation_errors else "message.new"
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
    _upsert_thread_state(conn, thread_id, emit_notifications=True)
    return message_id, status, validation_errors, event_ids


def _claim_message_in_txn(
    conn: sqlite3.Connection,
    message_id: str,
    agent: PeerAgent,
) -> tuple[bool, str, sqlite3.Row | None]:
    row = conn.execute(
        "SELECT * FROM messages WHERE id = ?",
        (message_id,),
    ).fetchone()
    if row is None:
        return False, "missing", None
    if not _recipient_matches(agent, row["recipient"]):
        return False, "wrong-recipient", row
    if row["status"] == "claimed" and row["claimed_by"] == agent:
        return True, "already-claimed", row
    if row["status"] == "invalid":
        return False, "invalid", row
    if row["status"] not in CLAIMABLE_STATUSES:
        return False, row["status"], row

    claimed_at = _now()
    cur = conn.execute(
        """
        UPDATE messages
        SET status = 'claimed', claimed_by = ?, claimed_at = ?
        WHERE id = ? AND status IN ('new', 'pending')
        """,
        (agent, claimed_at, message_id),
    )
    if cur.rowcount != 1:
        current = conn.execute(
            "SELECT * FROM messages WHERE id = ?",
            (message_id,),
        ).fetchone()
        return False, "race-lost", current

    claimed = conn.execute(
        "SELECT * FROM messages WHERE id = ?",
        (message_id,),
    ).fetchone()
    if row["sender"] in PEER_AGENTS:
        _queue_notification(
            conn,
            row["sender"],
            "message.claimed",
            message_id,
            row["subject"],
            {"claimed_by": agent, "claimed_at": claimed_at, "thread_id": _thread_correlation_id(row)},
        )
    _upsert_thread_state(conn, _thread_correlation_id(row), emit_notifications=True)
    return True, "claimed", claimed


def _list_notifications(agent: str, after_event_id: int, limit: int) -> list[dict]:
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
    with _conn() as conn:
        if agent:
            row = conn.execute(
                """
                SELECT COALESCE(MAX(event_id), 0) AS max_event_id
                FROM notifications
                WHERE agent = ?
                """,
                (agent,),
            ).fetchone()
        else:
            row = conn.execute(
                """
                SELECT COALESCE(MAX(event_id), 0) AS max_event_id
                FROM notifications
                """
            ).fetchone()
    if row is None:
        return 0
    return int(row["max_event_id"] or 0)


def resolve_message_reference(
    message_ref: str,
    recipient: Literal["codex", "prime"] | None = None,
) -> dict | None:
    """
    Resolve a full bridge message row from an exact ID or a unique short-id prefix.
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
                """
                SELECT * FROM messages
                WHERE id LIKE ?
                ORDER BY created_at DESC
                LIMIT 3
                """,
                (like_ref,),
            ).fetchall()

    if len(rows) == 1:
        return _row_to_dict(rows[0])
    return None


def get_thread_messages(
    message_ref: str,
    recipient: PeerAgent | None = None,
    limit: int = 100,
) -> list[dict]:
    resolved = resolve_message_reference(message_ref, recipient=recipient)
    if resolved is None:
        return []

    thread_id = resolved.get("thread_id") or resolved.get("correlation_id") or resolved["id"]
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM messages
            WHERE thread_id = ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (thread_id, limit),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def describe_thread_context(
    message_ref: str,
    recipient: PeerAgent | None = None,
    limit: int = 100,
) -> dict | None:
    resolved = resolve_message_reference(message_ref, recipient=recipient)
    if resolved is None:
        return None

    thread_messages = get_thread_messages(
        resolved["id"],
        recipient=recipient,
        limit=limit,
    )

    non_protocol = [item for item in thread_messages if not _message_is_protocol_ack(item)]
    latest_non_protocol_codex = next(
        (
            item
            for item in reversed(non_protocol)
            if item.get("sender") == "codex"
        ),
        None,
    )
    latest_non_protocol_prime = next(
        (
            item
            for item in reversed(non_protocol)
            if item.get("sender") == "prime"
        ),
        None,
    )
    terminal_messages = [
        item for item in thread_messages if item.get("status") in FINAL_STATUSES
    ]

    thread_state = None
    thread_sla = None
    with _conn() as conn:
        thread_row = conn.execute(
            "SELECT * FROM threads WHERE thread_id = ?",
            (resolved.get("thread_id") or resolved["id"],),
        ).fetchone()
        if thread_row is not None:
            thread_state = _thread_row_to_dict(thread_row)
            thread_sla = _thread_sla_snapshot(conn, thread_state)

    return {
        "requested_ref": message_ref,
        "canonical_message": resolved,
        "thread_correlation_id": resolved.get("thread_id") or resolved.get("correlation_id") or resolved["id"],
        "thread_state": thread_state,
        "thread_sla": thread_sla,
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
) -> dict | None:
    context = describe_thread_context(message_ref, recipient=recipient, limit=limit)
    if context is None:
        return None

    canonical = context.get("canonical_message") or {}
    thread_state = context.get("thread_state") or {}
    return {
        "requested_ref": context.get("requested_ref", message_ref),
        "thread_correlation_id": context.get("thread_correlation_id"),
        "canonical_message": canonical,
        "thread_state": thread_state,
        "thread_sla": context.get("thread_sla"),
        "thread_messages": context.get("thread_messages", []),
        "latest_thread_message": context.get("latest_thread_message"),
        "latest_non_protocol_codex_message": context.get("latest_non_protocol_codex_message"),
        "latest_non_protocol_prime_message": context.get("latest_non_protocol_prime_message"),
        "terminal_messages": context.get("terminal_messages", []),
        "already_resolved": context.get("already_resolved", False),
        "artifact_refs": canonical.get("artifact_refs", []),
        "expected_response": canonical.get("expected_response", ""),
        "response_window": canonical.get("response_window", ""),
        "action_items": canonical.get("action_items", []),
        "latest_summary": thread_state.get("latest_summary", ""),
        "participants": thread_state.get("participants", []),
    }


@mcp.tool()
def send_correction_message(
    sender: PeerAgent,
    invalid_message_id: str,
    guidance: str,
    artifact_refs_json: str = "[]",
    priority: int = 1,
) -> dict:
    if sender not in PEER_AGENTS:
        raise ValueError("sender must be one of: codex, prime")
    if priority < 0 or priority > 3:
        raise ValueError("priority must be between 0 and 3")

    artifact_refs = json.loads(_normalize_json(artifact_refs_json, list))
    guidance_text = (guidance or "").strip()

    with _conn() as conn:
        invalid_row = conn.execute(
            "SELECT * FROM messages WHERE id = ?",
            (invalid_message_id,),
        ).fetchone()
        if invalid_row is None:
            return {
                "ok": False,
                "id": None,
                "status": "missing",
                "validation_errors": [f"unknown invalid_message_id: {invalid_message_id}"],
                "notification_event_ids": [],
            }
        if invalid_row["status"] != "invalid":
            return {
                "ok": False,
                "id": invalid_message_id,
                "status": str(invalid_row["status"]),
                "validation_errors": [f"message is not invalid: {invalid_message_id}"],
                "notification_event_ids": [],
            }
        if invalid_row["sender"] not in PEER_AGENTS or invalid_row["recipient"] not in PEER_AGENTS:
            return {
                "ok": False,
                "id": invalid_message_id,
                "status": "unsupported",
                "validation_errors": ["correction helper only supports peer-to-peer invalid messages"],
                "notification_event_ids": [],
            }

        recipient = str(invalid_row["sender"])
        thread_id = _thread_correlation_id(invalid_row)
        correction_rows = conn.execute(
            """
            SELECT * FROM messages
            WHERE thread_id = ? AND sender = ? AND recipient = ?
            ORDER BY created_at DESC
            """,
            (thread_id, sender, recipient),
        ).fetchall()
        for row in correction_rows:
            row_dict = _row_to_dict(row)
            payload = row_dict.get("payload") or {}
            if row_dict.get("status") != "invalid" and str(payload.get("response_type", "")).lower() == "correction":
                return {
                    "ok": True,
                    "id": row_dict["id"],
                    "status": row_dict["status"],
                    "validation_errors": row_dict.get("validation_errors", []),
                    "notification_event_ids": [],
                    "deduped": True,
                }

        subject = f"Correction: invalid bridge message {invalid_message_id}"
        body = guidance_text or (
            "This message was not processed because the bridge persisted it as invalid. "
            "Please review the thread and resend only if further bridge work is still needed."
        )
        payload = {
            "response_type": "correction",
            "expected_response": "acknowledgement",
            "response_window": "short",
            "artifact_refs": artifact_refs,
            "action_items": [
                "Acknowledge receipt of this correction guidance",
                "Resend the original request only if further bridge action is still needed",
            ],
            "invalid_message_id": invalid_message_id,
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
            invalid_message_id,
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


@mcp.tool()
def send_message(
    sender: Agent,
    recipient: Agent,
    subject: str,
    body: str,
    payload_json: str = "{}",
    tags_json: str = "[]",
    priority: int = 2,
    correlation_id: str | None = None,
) -> dict:
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


@mcp.tool()
def list_inbox(
    agent: PeerAgent,
    status: Literal["new", "invalid", "pending", "claimed", "done", "blocked", "superseded", "all"] = "new",
    limit: int = 20,
) -> dict:
    if limit < 1 or limit > 200:
        raise ValueError("limit must be between 1 and 200")

    where = "(recipient = ? OR recipient = 'any')"
    params: list[object] = [agent]
    if status != "all":
        if status == "new":
            where += " AND status IN ('new', 'pending')"
        else:
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


@mcp.tool()
def claim_next(agent: Literal["codex", "prime"]) -> dict:
    with _conn() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            """
            SELECT * FROM messages
            WHERE (recipient = ? OR recipient = 'any') AND status IN ('new', 'pending')
            ORDER BY priority DESC, created_at ASC
            LIMIT 1
            """,
            (agent,),
        ).fetchone()

        if row is None:
            conn.commit()
            return {"claimed": False}

        ok, status, claimed = _claim_message_in_txn(conn, row["id"], agent)
        conn.commit()

    return {
        "claimed": ok,
        "status": status,
        "item": _row_to_dict(claimed) if claimed is not None else None,
    }


@mcp.tool()
def claim_message(message_id: str, agent: Literal["codex", "prime"]) -> dict:
    with _conn() as conn:
        conn.execute("BEGIN IMMEDIATE")
        ok, status, claimed = _claim_message_in_txn(conn, message_id, agent)
        conn.commit()

    return {
        "claimed": ok,
        "status": status,
        "item": _row_to_dict(claimed) if claimed is not None else None,
    }


@mcp.tool()
def accept_message(
    message_id: str,
    agent: PeerAgent,
    note: str = "",
    payload_json: str = "{}",
) -> dict:
    payload = json.loads(_normalize_json(payload_json, dict))
    with _conn() as conn:
        conn.execute("BEGIN IMMEDIATE")
        ok, status, row = _claim_message_in_txn(conn, message_id, agent)
        if not ok or row is None:
            conn.commit()
            return {
                "ok": False,
                "message_id": message_id,
                "status": status,
                "response_message_id": None,
            }
        if row["sender"] not in {"codex", "prime"}:
            conn.commit()
            return {
                "ok": False,
                "message_id": message_id,
                "status": "unsupported-sender",
                "response_message_id": None,
            }

        response_body = note or (
            f"{agent} accepted this task and will proceed without waiting for owner "
            "approval unless a new blocker appears."
        )
        response_payload = {
            "response_type": "accepted",
            "accepted_by": agent,
            "accepted_message_id": message_id,
            "claim_status": status,
            **payload,
        }
        response_message_id, response_status, validation_errors, event_ids = _insert_message(
            conn,
            agent,
            row["sender"],
            f"Accepted: {row['subject']}",
            response_body,
            response_payload,
            ["protocol", "accepted", "bridge-sync"],
            row["priority"],
            _thread_correlation_id(row),
        )
        conn.commit()

    return {
        "ok": True,
        "message_id": message_id,
        "status": status,
        "response_message_id": response_message_id,
        "response_status": response_status,
        "validation_errors": validation_errors,
        "notification_event_ids": event_ids,
    }


@mcp.tool()
def negotiate_message(
    message_id: str,
    agent: PeerAgent,
    body: str,
    payload_json: str = "{}",
) -> dict:
    payload = json.loads(_normalize_json(payload_json, dict))
    with _conn() as conn:
        conn.execute("BEGIN IMMEDIATE")
        ok, status, row = _claim_message_in_txn(conn, message_id, agent)
        if not ok or row is None:
            conn.commit()
            return {
                "ok": False,
                "message_id": message_id,
                "status": status,
                "response_message_id": None,
            }
        if row["sender"] not in {"codex", "prime"}:
            conn.commit()
            return {
                "ok": False,
                "message_id": message_id,
                "status": "unsupported-sender",
                "response_message_id": None,
            }

        response_payload = {
            "response_type": "negotiation",
            "negotiated_by": agent,
            "negotiated_message_id": message_id,
            "claim_status": status,
            **payload,
        }
        response_message_id, response_status, validation_errors, event_ids = _insert_message(
            conn,
            agent,
            row["sender"],
            f"Negotiation: {row['subject']}",
            body,
            response_payload,
            ["protocol", "negotiation", "bridge-sync"],
            row["priority"],
            _thread_correlation_id(row),
        )
        conn.commit()

    return {
        "ok": True,
        "message_id": message_id,
        "status": status,
        "response_message_id": response_message_id,
        "response_status": response_status,
        "validation_errors": validation_errors,
        "notification_event_ids": event_ids,
    }


@mcp.tool()
def resolve_message(
    message_id: str,
    agent: Literal["codex", "prime", "owner"],
    outcome: Literal["done", "blocked", "superseded"] = "done",
    resolution: str = "",
) -> dict:
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM messages WHERE id = ?",
            (message_id,),
        ).fetchone()
        if row is None:
            return {"ok": False, "id": message_id, "status": "missing"}

        cur = conn.execute(
            """
            UPDATE messages
            SET status = ?, resolution = ?, resolved_at = ?
            WHERE id = ? AND (claimed_by = ? OR ? = 'owner')
            """,
            (outcome, resolution, _now(), message_id, agent, agent),
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
            _upsert_thread_state(conn, _thread_correlation_id(row), emit_notifications=True)
        conn.commit()

    return {
        "ok": cur.rowcount == 1,
        "id": message_id,
        "status": outcome if cur.rowcount == 1 else "unchanged",
    }


@mcp.tool()
def list_notifications(
    agent: PeerAgent,
    after_event_id: int = 0,
    limit: int = 20,
) -> dict:
    items = _list_notifications(agent, after_event_id, limit)
    last_event_id = items[-1]["event_id"] if items else after_event_id
    return {"count": len(items), "last_event_id": last_event_id, "items": items}


@mcp.tool()
def get_latest_notification_event_id(agent: PeerAgent | None = None) -> dict:
    return {
        "agent": agent,
        "last_event_id": _latest_notification_event_id(agent),
    }


@mcp.tool()
def wait_for_notifications(
    agent: PeerAgent,
    after_event_id: int = 0,
    timeout_seconds: int = 15,
    poll_interval_ms: int = 100,
    limit: int = 20,
) -> dict:
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


@mcp.tool()
def get_thread(thread_ref: str, agent: PeerAgent | None = None) -> dict:
    context = describe_thread_context(thread_ref, recipient=agent)
    return {"ok": context is not None, "thread": context}


@mcp.tool()
def get_worker_event_payload(thread_ref: str, agent: PeerAgent | None = None) -> dict:
    context = build_worker_event_payload(thread_ref, recipient=agent)
    return {"ok": context is not None, "context": context}


@mcp.tool()
def list_threads(
    agent: PeerAgent,
    status: Literal["open", "claimed", "final", "all"] = "open",
    limit: int = 20,
) -> dict:
    if limit < 1 or limit > 200:
        raise ValueError("limit must be between 1 and 200")

    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM threads ORDER BY updated_at DESC LIMIT ?",
            (max(limit * 5, limit),),
        ).fetchall()

    items = []
    for row in rows:
        item = _thread_row_to_dict(row)
        if agent not in item["participants"]:
            continue
        if status == "claimed" and item.get("status") != "claimed":
            continue
        if status == "final" and item.get("status") not in FINAL_STATUSES:
            continue
        if status == "open" and item.get("status") in FINAL_STATUSES:
            continue
        items.append(item)
        if len(items) >= limit:
            break
    return {"count": len(items), "items": items}


@mcp.tool()
def list_threads_at_risk(
    agent: PeerAgent,
    silence_minutes: int = 10,
    limit: int = 20,
) -> dict:
    if silence_minutes < 1 or silence_minutes > 240:
        raise ValueError("silence_minutes must be between 1 and 240")

    items = []
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM threads
            ORDER BY updated_at ASC
            LIMIT ?
            """,
            (limit * 10,),
        ).fetchall()
        for row in rows:
            item = _thread_row_to_dict(row)
            if (
                item.get("status") in FINAL_STATUSES
                or item.get("status") == "invalid"
                or agent not in item["participants"]
            ):
                continue
            sla = _thread_sla_snapshot(conn, item, silence_seconds=silence_minutes * 60)
            if sla.get("responsible_agent") != agent or not sla.get("risk_types"):
                continue
            item["risk_types"] = sla["risk_types"]
            item["ack_overdue_seconds"] = sla["ack_overdue_seconds"]
            item["response_overdue_seconds"] = sla["response_overdue_seconds"]
            item["silence_overdue_seconds"] = sla["silence_overdue_seconds"]
            item["sla"] = sla
            items.append(item)
            if len(items) >= limit:
                break
    return {"count": len(items), "items": items}


@mcp.tool()
def bridge_sla_report(
    agent: PeerAgent,
    silence_minutes: int = 10,
    limit: int = 20,
) -> dict:
    if silence_minutes < 1 or silence_minutes > 240:
        raise ValueError("silence_minutes must be between 1 and 240")
    if limit < 1 or limit > 200:
        raise ValueError("limit must be between 1 and 200")

    with _conn() as conn:
        thread_rows = conn.execute(
            "SELECT * FROM threads ORDER BY updated_at DESC"
        ).fetchall()
        invalid_rows = conn.execute(
            """
            SELECT * FROM messages
            WHERE (recipient = ? OR recipient = 'any') AND status = 'invalid'
            ORDER BY priority DESC, created_at ASC
            LIMIT ?
            """,
            (agent, limit),
        ).fetchall()

        ack_breaches: list[dict[str, Any]] = []
        response_breaches: list[dict[str, Any]] = []
        silence_breaches: list[dict[str, Any]] = []
        at_risk_items: list[dict[str, Any]] = []
        open_threads = 0
        claimed_threads = 0
        responsible_threads = 0

        for row in thread_rows:
            item = _thread_row_to_dict(row)
            if (
                agent not in item["participants"]
                or item.get("status") in FINAL_STATUSES
                or item.get("status") == "invalid"
            ):
                continue
            sla = _thread_sla_snapshot(conn, item, silence_seconds=silence_minutes * 60)
            if sla.get("responsible_agent") != agent:
                continue
            responsible_threads += 1
            if item.get("status") == "claimed":
                claimed_threads += 1
            else:
                open_threads += 1

            enriched = {
                "thread_id": item["thread_id"],
                "status": item["status"],
                "current_assignee": item.get("current_assignee"),
                "latest_summary": item.get("latest_summary", ""),
                "updated_at": item.get("updated_at"),
                "artifact_refs": item.get("artifact_refs", []),
                "risk_types": sla["risk_types"],
                "sla": sla,
            }
            if sla["ack_breach"]:
                ack_breaches.append(enriched)
            if sla["response_window_breach"]:
                response_breaches.append(enriched)
            if sla["claimed_thread_silence_breach"]:
                silence_breaches.append(enriched)
            if sla["risk_types"]:
                at_risk_items.append(enriched)

    risk_items = sorted(
        at_risk_items,
        key=lambda item: (
            -len(item.get("risk_types", [])),
            -(item.get("sla", {}).get("silence_overdue_seconds", 0)),
            -(item.get("sla", {}).get("response_overdue_seconds", 0)),
            -(item.get("sla", {}).get("ack_overdue_seconds", 0)),
        ),
    )

    return {
        "agent": agent,
        "ack_deadline_seconds": ACK_DEADLINE_SECONDS,
        "claimed_thread_silence_seconds": silence_minutes * 60,
        "response_windows_seconds": RESPONSE_WINDOW_SECONDS,
        "responsible_open_threads": responsible_threads,
        "claimed_threads": claimed_threads,
        "unclaimed_open_threads": open_threads,
        "ack_breach_count": len(ack_breaches),
        "response_window_breach_count": len(response_breaches),
        "claimed_thread_silence_breach_count": len(silence_breaches),
        "invalid_inbox_count": len(invalid_rows),
        "invalid_messages": [_row_to_dict(row) for row in invalid_rows],
        "at_risk_threads": risk_items[:limit],
    }


@mcp.resource("bridge://health")
def health() -> str:
    with _conn() as conn:
        message_rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM messages GROUP BY status"
        ).fetchall()
        notification_rows = conn.execute(
            "SELECT agent, COUNT(*) AS n FROM notifications GROUP BY agent"
        ).fetchall()
        thread_rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM threads GROUP BY status"
        ).fetchall()
        max_event_id = conn.execute(
            "SELECT COALESCE(MAX(event_id), 0) AS max_event_id FROM notifications"
        ).fetchone()["max_event_id"]
        sla_by_agent = {
            agent: bridge_sla_report(agent=agent, silence_minutes=10, limit=10)
            for agent in sorted(PEER_AGENTS)
        }

    return json.dumps(
        {
            "db_path": str(DB_PATH),
            "schema_version_current": SCHEMA_VERSION_CURRENT,
            "features": [
                "notifications-long-poll",
                "explicit-claim",
                "thread-state",
                "message-kinds",
                "invalid-state",
            ],
            "max_event_id": max_event_id,
            "messages": {row["status"]: row["n"] for row in message_rows},
            "notifications": {row["agent"]: row["n"] for row in notification_rows},
            "threads": {row["status"]: row["n"] for row in thread_rows},
            "sla": {
                agent: {
                    "responsible_open_threads": report["responsible_open_threads"],
                    "ack_breach_count": report["ack_breach_count"],
                    "response_window_breach_count": report["response_window_breach_count"],
                    "claimed_thread_silence_breach_count": report["claimed_thread_silence_breach_count"],
                    "invalid_inbox_count": report["invalid_inbox_count"],
                }
                for agent, report in sla_by_agent.items()
            },
        },
        indent=2,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
