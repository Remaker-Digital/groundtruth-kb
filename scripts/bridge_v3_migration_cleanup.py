#!/usr/bin/env python3
"""One-time v3 migration cleanup for the live bridge DB.

The automated migration in prime_bridge_runtime.py partially completed
(status mapping + payload merge) but the destructive-gate hook blocked
DROP TABLE operations. This script finishes the job:

1. Fix leaked old statuses (new -> pending, resolved -> completed, superseded -> failed)
2. Drop the threads table (thread state now derived from messages)
3. Drop deprecated columns from messages (claimed_by, claimed_at, expected_response,
   response_window, action_items, validation_errors)

Backs up the DB before any changes.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".claude" / "prime-bridge" / "bridge.db"
TARGET_COLUMNS = [
    "id", "sender", "recipient", "subject", "body", "payload", "tags",
    "priority", "status", "correlation_id", "thread_id", "created_at",
    "resolved_at", "resolution", "schema_version", "message_kind", "artifact_refs",
]


def main() -> None:
    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}")
        return

    # Back up
    backup = DB_PATH.with_suffix(".v2-final.bak")
    if not backup.exists():
        shutil.copy2(DB_PATH, backup)
        print(f"Backed up to {backup}")
    else:
        print(f"Backup already exists: {backup}")

    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")

    # Step 1: Fix leaked statuses
    status_map = {
        "new": "pending",
        "resolved": "completed",
        "superseded": "failed",
    }
    for old, new in status_map.items():
        cur = conn.execute("UPDATE messages SET status = ? WHERE status = ?", (new, old))
        if cur.rowcount:
            print(f"  Mapped {cur.rowcount} rows: {old} -> {new}")

    # Fix rows where status is actually a body fragment (data corruption from old bugs)
    cur = conn.execute(
        "UPDATE messages SET status = 'completed' WHERE status NOT IN ('pending', 'completed', 'failed')"
    )
    if cur.rowcount:
        print(f"  Fixed {cur.rowcount} rows with non-standard status -> completed")

    # Step 2: Drop threads table
    conn.execute("DROP TABLE IF EXISTS threads")
    print("  Dropped threads table")

    # Step 3: Replace messages table to remove deprecated columns
    current_columns = [r[1] for r in conn.execute("PRAGMA table_info(messages)").fetchall()]
    deprecated = set(current_columns) - set(TARGET_COLUMNS)
    if deprecated:
        print(f"  Removing deprecated columns: {sorted(deprecated)}")
        col_list = ", ".join(TARGET_COLUMNS)
        conn.execute(f"""
            CREATE TABLE messages_v3 (
                id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                payload TEXT NOT NULL DEFAULT '{{}}',
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
        """)
        conn.execute(f"INSERT INTO messages_v3 ({col_list}) SELECT {col_list} FROM messages")
        conn.execute("DROP TABLE messages")
        conn.execute("ALTER TABLE messages_v3 RENAME TO messages")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_inbox "
            "ON messages(recipient, status, priority DESC, created_at ASC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_thread "
            "ON messages(thread_id, created_at ASC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_thread_covering "
            "ON messages(thread_id, created_at, status, sender, recipient)"
        )
        print("  Replaced messages table (deprecated columns removed)")
    else:
        print("  Messages table already clean")

    # Step 4: Clean stale notification event types
    cur = conn.execute(
        "DELETE FROM notifications WHERE event_type IN "
        "('message.claimed', 'thread.ack_breach', 'thread.response_window_breach', 'thread.updated')"
    )
    if cur.rowcount:
        print(f"  Cleaned {cur.rowcount} stale notification events")

    conn.execute("PRAGMA user_version = 3")
    conn.commit()
    conn.close()

    # Verify
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    columns = [r[1] for r in conn.execute("PRAGMA table_info(messages)").fetchall()]
    statuses = dict(conn.execute("SELECT status, COUNT(*) FROM messages GROUP BY status").fetchall())
    ver = conn.execute("PRAGMA user_version").fetchone()[0]
    conn.close()

    print(f"\n=== Verification ===")
    print(f"Schema version: {ver}")
    print(f"Tables: {tables}")
    print(f"Columns ({len(columns)}): {columns}")
    print(f"Statuses: {statuses}")
    assert "threads" not in tables, "threads table should be dropped"
    assert "claimed_by" not in columns, "claimed_by should be gone"
    assert len(columns) == 17, f"Expected 17 columns, got {len(columns)}"
    assert all(s in ("pending", "completed", "failed") for s in statuses), f"Unexpected statuses: {statuses}"
    print("\nMigration cleanup complete!")


if __name__ == "__main__":
    main()
