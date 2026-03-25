from __future__ import annotations

import json
import os
import site
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_json(value: str, expected: type) -> str:
    parsed = json.loads(value)
    if not isinstance(parsed, expected):
        raise ValueError(f"Expected JSON {expected.__name__}")
    return json.dumps(parsed)


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
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
            resolution TEXT
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
    return conn


def _row_to_dict(row: sqlite3.Row) -> dict:
    item = dict(row)
    item["payload"] = json.loads(item["payload"] or "{}")
    item["tags"] = json.loads(item["tags"] or "[]")
    return item


def _recipient_matches(agent: str, recipient: str) -> bool:
    return recipient in {agent, "any"}


def _thread_correlation_id(row: sqlite3.Row) -> str:
    return row["correlation_id"] or row["id"]


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
) -> tuple[str, list[int]]:
    message_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO messages (
            id, sender, recipient, subject, body, payload, tags,
            priority, status, correlation_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?)
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
            correlation_id,
            _now(),
        ),
    )
    event_ids = []
    for target in _notification_targets(recipient):
        event_ids.append(
            _queue_notification(
                conn,
                target,
                "message.new",
                message_id,
                subject,
                {
                    "sender": sender,
                    "recipient": recipient,
                    "priority": priority,
                    "correlation_id": correlation_id,
                },
            )
        )
    return message_id, event_ids


def _claim_message_in_txn(
    conn: sqlite3.Connection,
    message_id: str,
    agent: Literal["codex", "prime"],
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
    if row["status"] != "new":
        return False, row["status"], row

    claimed_at = _now()
    cur = conn.execute(
        """
        UPDATE messages
        SET status = 'claimed', claimed_by = ?, claimed_at = ?
        WHERE id = ? AND status = 'new'
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
    if row["sender"] in {"codex", "prime"}:
        _queue_notification(
            conn,
            row["sender"],
            "message.claimed",
            message_id,
            row["subject"],
            {"claimed_by": agent, "claimed_at": claimed_at},
        )
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
        item["details"] = json.loads(item["details"] or "{}")
        items.append(item)
    return items


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
        message_id, event_ids = _insert_message(
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
        "status": "new",
        "notification_event_ids": event_ids,
    }


@mcp.tool()
def list_inbox(
    agent: Literal["codex", "prime"],
    status: Literal["new", "claimed", "done", "blocked", "all"] = "new",
    limit: int = 20,
) -> dict:
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


@mcp.tool()
def claim_next(agent: Literal["codex", "prime"]) -> dict:
    with _conn() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            """
            SELECT * FROM messages
            WHERE (recipient = ? OR recipient = 'any') AND status = 'new'
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
    agent: Literal["codex", "prime"],
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
        response_message_id, event_ids = _insert_message(
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
        "notification_event_ids": event_ids,
    }


@mcp.tool()
def negotiate_message(
    message_id: str,
    agent: Literal["codex", "prime"],
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
        response_message_id, event_ids = _insert_message(
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
        "notification_event_ids": event_ids,
    }


@mcp.tool()
def resolve_message(
    message_id: str,
    agent: Literal["codex", "prime", "owner"],
    outcome: Literal["done", "blocked"] = "done",
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
        if cur.rowcount == 1 and row["sender"] in {"codex", "prime"}:
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
                },
            )
        conn.commit()

    return {
        "ok": cur.rowcount == 1,
        "id": message_id,
        "status": outcome if cur.rowcount == 1 else "unchanged",
    }


@mcp.tool()
def list_notifications(
    agent: Literal["codex", "prime"],
    after_event_id: int = 0,
    limit: int = 20,
) -> dict:
    items = _list_notifications(agent, after_event_id, limit)
    last_event_id = items[-1]["event_id"] if items else after_event_id
    return {"count": len(items), "last_event_id": last_event_id, "items": items}


@mcp.tool()
def wait_for_notifications(
    agent: Literal["codex", "prime"],
    after_event_id: int = 0,
    timeout_seconds: int = 15,
    poll_interval_ms: int = 250,
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


@mcp.resource("bridge://health")
def health() -> str:
    with _conn() as conn:
        message_rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM messages GROUP BY status"
        ).fetchall()
        notification_rows = conn.execute(
            "SELECT agent, COUNT(*) AS n FROM notifications GROUP BY agent"
        ).fetchall()
        max_event_id = conn.execute(
            "SELECT COALESCE(MAX(event_id), 0) AS max_event_id FROM notifications"
        ).fetchone()["max_event_id"]

    return json.dumps(
        {
            "db_path": str(DB_PATH),
            "features": [
                "notifications-long-poll",
                "explicit-claim",
                "protocol-acceptance-negotiation",
            ],
            "max_event_id": max_event_id,
            "messages": {row["status"]: row["n"] for row in message_rows},
            "notifications": {row["agent"]: row["n"] for row in notification_rows},
        },
        indent=2,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
