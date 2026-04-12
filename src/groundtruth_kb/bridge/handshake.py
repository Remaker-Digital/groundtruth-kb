# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Legacy Codex session-start handshake with Prime.

This module uses the archived SQLite/MCP bridge runtime. New dual-agent
projects should use the file bridge protocol and OS pollers instead.
"""

from __future__ import annotations

import argparse
import json
import math
import time

from groundtruth_kb.bridge.runtime import (
    get_bridge_db,
    get_latest_notification_event_id,
    get_thread,
    resolve_message,
    retry_pending_message,
    send_message,
    wait_for_notifications,
)

REQUEST_TEXT = "Report your current operating state"
REQUEST_SUBJECT = "Session start: report current operating state"
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_POLL_SECONDS = 15


def _extract_prime_reply(thread_payload: dict) -> dict | None:
    thread = thread_payload.get("thread") or {}
    messages = thread.get("thread_messages") or []
    for message in reversed(messages):
        if message.get("sender") != "prime":
            continue
        if message.get("recipient") not in {"codex", "any"}:
            continue
        if message.get("status") == "failed":
            continue
        body = str(message.get("body", "") or "").strip().lower()
        if "thread completed with outcome" in body:
            continue
        if "closure-only" in body or "receipt-only" in body:
            continue
        if "session-start probe:" in body and "reply sent" in body:
            continue
        return message
    return None


def _find_existing_pending_thread() -> str | None:
    with get_bridge_db() as conn:
        row = conn.execute(
            """
            SELECT id
            FROM messages
            WHERE sender = 'codex'
              AND recipient = 'prime'
              AND status = 'pending'
              AND subject = ?
              AND body IN (?, ?)
            ORDER BY created_at ASC
            LIMIT 1
            """,
            (REQUEST_SUBJECT, REQUEST_TEXT, f"{REQUEST_TEXT}."),
        ).fetchone()
    if row is None:
        return None
    return str(row["id"])


def _format_success(thread_id: str, reply: dict) -> dict:
    body = str(reply.get("body", "") or "").strip()
    first_line = body.splitlines()[0] if body else "(empty reply body)"
    return {
        "ok": True,
        "thread_id": thread_id,
        "reply_id": reply.get("id"),
        "reply_subject": reply.get("subject"),
        "reply_created_at": reply.get("created_at"),
        "reply_summary": first_line,
    }


def _format_timeout(thread_id: str, timeout_seconds: int) -> dict:
    return {
        "ok": False,
        "thread_id": thread_id,
        "timeout_seconds": timeout_seconds,
        "error": (
            "Prime did not reply to the mandatory session-start operating-state "
            f"request within {timeout_seconds} seconds."
        ),
    }


def run_handshake(
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    poll_seconds: int = DEFAULT_POLL_SECONDS,
    json_output: bool = False,
) -> int:
    """Execute the Codex->Prime session-start handshake.

    Returns 0 on success (reply received), 1 on failure/timeout.
    """
    if timeout_seconds < 1:
        raise ValueError("timeout_seconds must be at least 1")
    if poll_seconds < 1:
        raise ValueError("poll_seconds must be at least 1")

    cursor = get_latest_notification_event_id(agent="codex").get("last_event_id", 0)
    payload = {
        "expected_response": "status_update",
        "artifact_refs": ["AGENTS.md"],
        "action_items": [
            "Reply with a concise summary of your current operating state.",
        ],
    }
    existing_thread_id = _find_existing_pending_thread()
    if existing_thread_id:
        retry_pending_message(message_id=existing_thread_id, agent="prime")
        thread_id = existing_thread_id
    else:
        send_result = send_message(
            sender="codex",
            recipient="prime",
            subject=REQUEST_SUBJECT,
            body=REQUEST_TEXT,
            payload_json=json.dumps(payload),
            priority=1,
        )
        if not send_result.get("ok") or send_result.get("status") == "failed":
            failure = {
                "ok": False,
                "error": "Failed to send the session-start operating-state request to Prime.",
                "send_result": send_result,
            }
            if json_output:
                print(json.dumps(failure))
            else:
                print(failure["error"])
                print(json.dumps(send_result, indent=2))
            return 1
        thread_id = str(send_result["id"])
    deadline = time.monotonic() + timeout_seconds

    while True:
        thread_payload = get_thread(thread_ref=thread_id, agent="codex")
        reply = _extract_prime_reply(thread_payload)
        if reply is not None:
            resolve_message(
                message_id=str(reply.get("id") or ""),
                agent="codex",
                outcome="completed",
                resolution="Session-start operating-state reply received by handshake script.",
            )
            success = _format_success(thread_id, reply)
            if json_output:
                print(json.dumps(success))
            else:
                print(f"Prime operating-state reply received: {success['reply_summary']}")
            return 0

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timeout = _format_timeout(thread_id, timeout_seconds)
            if json_output:
                print(json.dumps(timeout))
            else:
                print(timeout["error"])
                print(f"Bridge thread: {thread_id}")
            return 1

        wait_seconds = max(1, min(60, int(math.ceil(min(poll_seconds, remaining)))))
        notification_batch = wait_for_notifications(
            agent="codex",
            after_event_id=int(cursor or 0),
            timeout_seconds=wait_seconds,
            poll_interval_ms=500,
            limit=20,
        )
        cursor = notification_batch.get("last_event_id", cursor)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send the mandatory Codex->Prime session-start handshake request.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--poll-seconds", type=int, default=DEFAULT_POLL_SECONDS)
    parser.add_argument("--json-output", action="store_true")
    args = parser.parse_args()

    if args.timeout_seconds < 1:
        raise SystemExit("--timeout-seconds must be at least 1")
    if args.poll_seconds < 1:
        raise SystemExit("--poll-seconds must be at least 1")

    return run_handshake(
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
        json_output=args.json_output,
    )


if __name__ == "__main__":
    raise SystemExit(main())
