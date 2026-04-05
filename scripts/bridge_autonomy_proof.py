#!/usr/bin/env python3
"""Bridge Autonomy Proof — Phase D (S259).

Proves the bridge is truly autonomous by executing a round-trip scenario:

  1. Send a valid substantive message from prime to codex
  2. Inject a malformed message (noise) at the same time
  3. Wait for codex to claim and process the valid message
  4. Verify the malformed message did NOT block processing
  5. Report pass/fail

Usage:
    python scripts/bridge_autonomy_proof.py
    python scripts/bridge_autonomy_proof.py --timeout 120
    python scripts/bridge_autonomy_proof.py --skip-malformed

Requirements:
    - Both bridge workers must be running (via scheduled tasks or manually)
    - Bridge DB must be accessible

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check_worker_health(agent: str) -> dict:
    """Check if a worker is healthy."""
    from bridge_resident_worker import resident_worker_is_healthy, resident_worker_health_snapshot
    healthy, state = resident_worker_is_healthy(agent)
    snapshot = resident_worker_health_snapshot(agent) or {}
    return {
        "agent": agent,
        "healthy": healthy,
        "state": state,
        "status": snapshot.get("status", "unknown"),
        "pid": snapshot.get("pid"),
        "last_error": snapshot.get("last_error"),
        "updated_at": snapshot.get("updated_at"),
    }


def _send_test_message(bridge, *, sender: str, recipient: str, malformed: bool = False) -> str:
    """Send a test message on the bridge. Returns message ID."""
    msg_id = str(uuid.uuid4())
    thread_id = str(uuid.uuid4())
    now = _now_iso()

    if malformed:
        # Deliberately malformed: absolute Windows path in artifact_refs that would crash rglob
        artifact_refs = json.dumps([{
            "type": "file",
            "path": "C:\\Nonexistent\\Path\\That\\Should\\Not\\Crash\\worker.md",
            "note": "AUTONOMY-PROOF: malformed artifact ref — must not crash worker"
        }])
        subject = "AUTONOMY-PROOF-MALFORMED: This message has bad artifact refs"
        body = "This message intentionally contains malformed artifact references. The worker should log a warning and skip this message without crashing."
    else:
        artifact_refs = json.dumps([{
            "type": "file",
            "path": "CLAUDE.md",
            "note": "AUTONOMY-PROOF: valid relative artifact ref"
        }])
        subject = "AUTONOMY-PROOF: Bridge round-trip test"
        body = "This is an autonomy proof test message. Please acknowledge receipt by sending a protocol acknowledgement."

    action_items = json.dumps(["Acknowledge receipt of this autonomy proof test message"])

    bridge.send_message(
        sender=sender,
        recipient=recipient,
        subject=subject,
        body=body,
        expected_response="acknowledgement",
        response_window="immediate",
        artifact_refs=artifact_refs,
        action_items=action_items,
        correlation_id=None,
        thread_id=thread_id,
    )

    # The send_message may generate a different ID, but we need to find our message
    # by subject since the MCP tool generates the ID internally
    return subject


def _find_message_by_subject(bridge, *, recipient: str, subject_prefix: str) -> dict | None:
    """Find the most recent message matching a subject prefix."""
    inbox = bridge.list_inbox(agent=recipient, status="any", limit=20)
    for item in inbox.get("items", []):
        if item.get("subject", "").startswith(subject_prefix):
            return item
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Bridge autonomy proof harness")
    parser.add_argument("--timeout", type=int, default=90, help="Max seconds to wait for processing")
    parser.add_argument("--skip-malformed", action="store_true", help="Skip the malformed message injection")
    parser.add_argument("--sender", default="prime", choices=["prime", "codex"])
    parser.add_argument("--recipient", default="codex", choices=["prime", "codex"])
    args = parser.parse_args()

    print("=" * 60)
    print("BRIDGE AUTONOMY PROOF — Phase D (S259)")
    print("=" * 60)
    print()

    # Step 0: Check worker health
    print("Step 0: Checking worker health...")
    for agent in ["prime", "codex"]:
        health = _check_worker_health(agent)
        status_str = "HEALTHY" if health["healthy"] else f"UNHEALTHY ({health['state']})"
        print(f"  {agent}: {status_str} (pid={health['pid']}, status={health['status']})")
        if health["last_error"]:
            print(f"    last_error: {health['last_error'][:100]}")
    print()

    # Step 1: Connect to bridge
    print("Step 1: Connecting to bridge DB...")
    try:
        from prime_bridge_runtime import mcp as bridge_mcp
        import sqlite3

        db_path = Path.home() / ".claude" / "prime-bridge" / "bridge.db"
        if not db_path.exists():
            print(f"  FAIL: Bridge DB not found at {db_path}")
            return 1
        print(f"  OK: {db_path}")
    except Exception as exc:
        print(f"  FAIL: {exc}")
        return 1
    print()

    # Step 2: Send test messages via canonical send_message() API
    # (raw SQL inserts bypass validation — malformed messages must go through
    #  send_message so they get properly marked 'invalid' by the runtime)
    print("Step 2: Sending test messages...")

    from prime_bridge_runtime import send_message

    valid_subject = "AUTONOMY-PROOF: Bridge round-trip test"
    valid_result = send_message(
        sender=args.sender,
        recipient=args.recipient,
        subject=valid_subject,
        body="This is an autonomy proof test. Please acknowledge receipt.",
        payload_json=json.dumps({
            "artifact_refs": [{"type": "file", "path": "CLAUDE.md", "note": "valid ref"}],
            "expected_response": "acknowledgement",
            "response_window": "immediate",
            "action_items": ["Acknowledge receipt of this autonomy proof test"],
            "message_kind": "substantive",
        }),
    )
    valid_id = valid_result["id"]
    print(f"  Valid message:    {valid_id[:12]}... (status={valid_result['status']})")

    malformed_id = None
    malformed_subject = "AUTONOMY-PROOF-MALFORMED: Bad artifact refs"
    if not args.skip_malformed:
        malformed_result = send_message(
            sender=args.sender,
            recipient=args.recipient,
            subject=malformed_subject,
            body="This message has malformed artifact refs. Must not crash worker.",
            payload_json=json.dumps({
                "artifact_refs": [{"type": "file", "path": "C:\\Nonexistent\\Path\\crash.md", "note": "bad ref"}],
                "expected_response": "acknowledgement",
                "response_window": "immediate",
                "action_items": ["This should not crash the worker"],
                "message_kind": "substantive",
            }),
            priority=3,
        )
        malformed_id = malformed_result["id"]
        malformed_status = malformed_result["status"]
        print(f"  Malformed noise:  {malformed_id[:12]}... (status={malformed_status})")
        if malformed_status == "invalid":
            print("  OK: malformed message correctly marked 'invalid' by runtime validation")
        else:
            print(f"  WARN: malformed message has status '{malformed_status}' — expected 'invalid'")

    print()

    # Step 3: Wait for processing
    print(f"Step 3: Waiting up to {args.timeout}s for {args.recipient} to process...")
    deadline = time.monotonic() + args.timeout
    valid_processed = False
    malformed_crashed_worker = False

    while time.monotonic() < deadline:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        # Check valid message status
        row = conn.execute("SELECT status, claimed_by FROM messages WHERE id=?", (valid_id,)).fetchone()
        if row and row["status"] in ("claimed", "done"):
            valid_processed = True
            print(f"  Valid message: {row['status']} by {row['claimed_by']}")

        # Check worker health
        health = _check_worker_health(args.recipient)
        if health["state"] == "error" or (health["last_error"] and "Non-relative" in str(health["last_error"])):
            malformed_crashed_worker = True
            print(f"  WARNING: {args.recipient} worker in error state: {health['last_error'][:80]}")

        conn.close()

        if valid_processed:
            break

        # Print progress dot
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(5)

    print()
    print()

    # Step 4: Results
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    passed = True

    if valid_processed:
        print("[PASS] Valid message was processed by the recipient worker")
    else:
        print("[FAIL] Valid message was NOT processed within timeout")
        passed = False

    if malformed_id:
        if malformed_crashed_worker:
            print("[FAIL] Malformed message CRASHED the worker (rglob fix not working)")
            passed = False
        else:
            print("[PASS] Malformed message did not crash the worker")

    # Check final worker health
    final_health = _check_worker_health(args.recipient)
    if final_health["healthy"]:
        print(f"[PASS] {args.recipient} worker is healthy after test")
    else:
        print(f"[WARN] {args.recipient} worker state: {final_health['state']}")
        if final_health["state"] == "error":
            passed = False

    print()
    if passed:
        print("AUTONOMY PROOF: PASS")
    else:
        print("AUTONOMY PROOF: FAIL")
    print("=" * 60)

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
