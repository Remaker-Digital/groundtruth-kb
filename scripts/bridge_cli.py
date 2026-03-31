#!/usr/bin/env python3
"""
Bridge CLI — Direct fallback for prime-bridge when MCP is unavailable.

Imports and calls the same functions as the MCP server (prime_bridge_runtime.py)
without requiring an MCP client attachment. Use when the bridge MCP server
exits immediately (stdout-eof) because no MCP client is connected.

Usage:
  python scripts/bridge_cli.py send --from prime --to codex --subject "Review request" --body "..."
  python scripts/bridge_cli.py inbox --agent prime
  python scripts/bridge_cli.py thread <thread-ref>
  python scripts/bridge_cli.py claim <message-id> --agent prime
  python scripts/bridge_cli.py resolve <message-id> --agent prime --resolution "Done"
  python scripts/bridge_cli.py health
  python scripts/bridge_cli.py send-review --subject "G3b plan" --body "..." --artifacts "file1.md,file2.py"

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Import bridge runtime functions directly
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from prime_bridge_runtime import (
    bridge_sla_report,
    claim_message,
    get_thread,
    list_inbox,
    list_threads_at_risk,
    resolve_message,
    send_message,
    wait_for_notifications,
)


def _pp(data: dict) -> None:
    """Pretty-print a dict as JSON."""
    print(json.dumps(data, indent=2, default=str))


def cmd_send(args: argparse.Namespace) -> None:
    """Send a message via the bridge."""
    result = send_message(
        sender=args.sender,
        recipient=args.recipient,
        subject=args.subject,
        body=args.body,
        payload_json=args.payload or "{}",
        tags_json=args.tags or "[]",
        priority=args.priority,
        correlation_id=args.correlation_id,
    )
    _pp(result)


def cmd_inbox(args: argparse.Namespace) -> None:
    """List inbox messages."""
    result = list_inbox(
        agent=args.agent,
        status=args.status,
        limit=args.limit,
    )
    if result["count"] == 0:
        print(f"Inbox empty (agent={args.agent}, status={args.status})")
        return
    print(f"Inbox: {result['count']} message(s)\n")
    for item in result["items"]:
        priority_marker = ["!", "!!", "!!!", "!!!!"][min(item.get("priority", 0), 3)]
        print(f"  [{item['id'][:8]}] {priority_marker} {item.get('subject', '(no subject)')}")
        print(f"    from={item.get('sender')} status={item.get('status')} created={item.get('created_at', '')[:19]}")
        if item.get("thread_id"):
            print(f"    thread={item['thread_id'][:8]}")
        print()


def cmd_thread(args: argparse.Namespace) -> None:
    """Get thread details."""
    result = get_thread(thread_ref=args.thread_ref, agent=args.agent)
    _pp(result)


def cmd_claim(args: argparse.Namespace) -> None:
    """Claim a message."""
    result = claim_message(message_id=args.message_id, agent=args.agent)
    _pp(result)


def cmd_resolve(args: argparse.Namespace) -> None:
    """Resolve a message."""
    result = resolve_message(
        message_id=args.message_id,
        agent=args.agent,
        outcome=args.outcome,
        resolution=args.resolution,
    )
    _pp(result)


def cmd_notifications(args: argparse.Namespace) -> None:
    """Poll for notifications."""
    result = wait_for_notifications(
        agent=args.agent,
        after_event_id=args.after,
        timeout_seconds=args.timeout,
    )
    if not result.get("notified"):
        print(f"No new notifications (agent={args.agent}, after_event_id={args.after})")
        return
    print(f"Notifications: {result['count']} new (last_event_id={result.get('last_event_id')})\n")
    for item in result.get("items", []):
        print(f"  [{item.get('event_id')}] {item.get('event_type')}: {item.get('subject', '')}")
    print()


def cmd_health(args: argparse.Namespace) -> None:
    """Bridge health check — inbox counts + SLA + at-risk threads."""
    print("=== Bridge Health ===\n")

    for agent in ("prime", "codex"):
        inbox = list_inbox(agent=agent, status="new")
        print(f"  {agent} inbox: {inbox['count']} new message(s)")

    for agent in ("prime", "codex"):
        print()
        at_risk = list_threads_at_risk(agent=agent)
        risk_count = at_risk.get("count", 0)
        print(f"  {agent} threads at risk: {risk_count}")
        if risk_count > 0:
            for t in at_risk.get("items", []):
                print(f"    [{t.get('thread_id', '?')[:8]}] {t.get('risk_reason', '?')}")

        sla = bridge_sla_report(agent=agent)
        breaches = sla.get("breaches", 0)
        print(f"  {agent} SLA breaches: {breaches}")

    print()


def cmd_send_review(args: argparse.Namespace) -> None:
    """Send a structured advisory review request with required protocol fields."""
    artifact_refs = [a.strip() for a in args.artifacts.split(",") if a.strip()] if args.artifacts else []
    action_items = [a.strip() for a in args.action_items.split("|") if a.strip()] if args.action_items else []

    payload = {
        "artifact_refs": artifact_refs,
        "expected_response": "advisory_review",
        "response_window": args.response_window,
        "action_items": action_items,
    }

    result = send_message(
        sender="prime",
        recipient="codex",
        subject=args.subject,
        body=args.body,
        payload_json=json.dumps(payload),
        tags_json=json.dumps(["advisory-review", "bridge-sync"]),
        priority=args.priority,
        correlation_id=args.correlation_id,
    )
    _pp(result)
    if result.get("ok"):
        print(f"\nReview request sent: {result['id']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bridge CLI — direct fallback for prime-bridge MCP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # send
    p_send = sub.add_parser("send", help="Send a message")
    p_send.add_argument("--sender", "--from", required=True, choices=["prime", "codex", "owner"])
    p_send.add_argument("--recipient", "--to", required=True, choices=["prime", "codex", "any"])
    p_send.add_argument("--subject", "-s", required=True)
    p_send.add_argument("--body", "-b", required=True)
    p_send.add_argument("--payload", default="{}")
    p_send.add_argument("--tags", default="[]")
    p_send.add_argument("--priority", type=int, default=2)
    p_send.add_argument("--correlation-id")
    p_send.set_defaults(func=cmd_send)

    # inbox
    p_inbox = sub.add_parser("inbox", help="List inbox messages")
    p_inbox.add_argument("--agent", required=True, choices=["prime", "codex"])
    p_inbox.add_argument("--status", default="new")
    p_inbox.add_argument("--limit", type=int, default=20)
    p_inbox.set_defaults(func=cmd_inbox)

    # thread
    p_thread = sub.add_parser("thread", help="Get thread details")
    p_thread.add_argument("thread_ref")
    p_thread.add_argument("--agent", choices=["prime", "codex"])
    p_thread.set_defaults(func=cmd_thread)

    # claim
    p_claim = sub.add_parser("claim", help="Claim a message")
    p_claim.add_argument("message_id")
    p_claim.add_argument("--agent", required=True, choices=["prime", "codex"])
    p_claim.set_defaults(func=cmd_claim)

    # resolve
    p_resolve = sub.add_parser("resolve", help="Resolve a message")
    p_resolve.add_argument("message_id")
    p_resolve.add_argument("--agent", required=True, choices=["prime", "codex", "owner"])
    p_resolve.add_argument("--outcome", default="done", choices=["done", "blocked", "superseded"])
    p_resolve.add_argument("--resolution", default="")
    p_resolve.set_defaults(func=cmd_resolve)

    # notifications
    p_notif = sub.add_parser("notifications", help="Poll for notifications")
    p_notif.add_argument("--agent", required=True, choices=["prime", "codex"])
    p_notif.add_argument("--after", type=int, default=0)
    p_notif.add_argument("--timeout", type=int, default=5)
    p_notif.set_defaults(func=cmd_notifications)

    # health
    p_health = sub.add_parser("health", help="Bridge health check")
    p_health.set_defaults(func=cmd_health)

    # send-review (typed wrapper)
    p_review = sub.add_parser("send-review", help="Send structured advisory review request")
    p_review.add_argument("--subject", "-s", required=True)
    p_review.add_argument("--body", "-b", required=True)
    p_review.add_argument("--artifacts", help="Comma-separated artifact file paths")
    p_review.add_argument("--action-items", help="Pipe-separated action items")
    p_review.add_argument("--response-window", default="async", choices=["immediate", "short", "session", "async"])
    p_review.add_argument("--priority", type=int, default=2)
    p_review.add_argument("--correlation-id")
    p_review.set_defaults(func=cmd_send_review)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
