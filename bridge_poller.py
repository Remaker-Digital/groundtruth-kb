#!/usr/bin/env python3
"""
Prime Bridge periodic notification poller.

Runs as a lightweight background process that long-polls bridge notifications
and automatically handles new peer messages to keep bridge coordination fluid
without manual inbox checks.

Behavior:
- Polls notifications with wait_for_notifications() in a timed loop.
- Auto-accepts new non-ack peer messages (codex<->prime).
- Auto-resolves pure protocol acknowledgements ("Accepted:" / "Negotiation:").
- Persists last processed notification event ID to disk.
- Uses a file lock to prevent duplicate pollers per agent.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import msvcrt


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _consume_stdin_if_present() -> None:
    """Hook compatibility: consume stdin JSON payload if present."""
    try:
        if not sys.stdin.isatty():
            _ = sys.stdin.read()
    except Exception:
        pass


class _FileLock:
    """Single-process lock for a given agent poller."""

    def __init__(self, path: Path):
        self.path = path
        self._fh = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Open in r+b (or create with w+b) so we can seek to byte 0 for locking.
        # msvcrt.locking needs at least 1 byte in the file to lock.
        if not self.path.exists() or self.path.stat().st_size == 0:
            self.path.write_bytes(b"\x00")
        self._fh = open(self.path, "r+b")
        self._fh.seek(0)
        try:
            msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
        except (OSError, PermissionError):
            self._fh.close()
            self._fh = None
            raise RuntimeError(f"bridge poller lock busy: {self.path}")
        return self

    def __exit__(self, *_args):
        if self._fh:
            try:
                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
            self._fh.close()
            self._fh = None


def _load_state(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"last_event_id": 0, "updated_at": _now()}


def _save_state(path: Path, state: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def _append_log(path: Path, message: str) -> None:
    line = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        pass


def _is_protocol_ack(item: dict) -> bool:
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


def _handle_inbox(bridge, agent: str, peer: str, log_file: Path, *, write_enabled: bool) -> dict:
    """
    Handle new inbox items for `agent`.

    - Protocol acks are claimed and auto-resolved.
    - Non-ack peer messages are auto-accepted.
    """
    summary = {
        "detected": 0,
        "accepted": 0,
        "resolved_acks": 0,
        "readonly_skips": 0,
        "errors": 0,
    }
    inbox = bridge.list_inbox(agent=agent, status="new", limit=100)
    items = inbox.get("items", [])

    for item in items:
        if item.get("sender") != peer:
            continue

        message_id = item.get("id")
        subject = item.get("subject", "")
        if not message_id:
            continue
        summary["detected"] += 1

        if not write_enabled:
            summary["readonly_skips"] += 1
            _append_log(
                log_file,
                f"detected (read-only mode, no auto-ack): {message_id} :: {subject}",
            )
            continue

        try:
            if _is_protocol_ack(item):
                claimed = bridge.claim_message(message_id=message_id, agent=agent)
                if claimed.get("claimed"):
                    bridge.resolve_message(
                        message_id=message_id,
                        agent=agent,
                        outcome="done",
                        resolution="Auto-resolved by periodic bridge poller (protocol acknowledgement).",
                    )
                    summary["resolved_acks"] += 1
                    _append_log(log_file, f"resolved ack: {message_id} :: {subject}")
                continue

            accepted = bridge.accept_message(
                message_id=message_id,
                agent=agent,
                note=(
                    f"Auto-accepted by {agent} periodic bridge poller at {_now()}. "
                    "Codex/Prime will continue execution without manual inbox polling."
                ),
            )
            if accepted.get("ok"):
                summary["accepted"] += 1
                _append_log(log_file, f"accepted: {message_id} :: {subject}")
            else:
                summary["errors"] += 1
                _append_log(
                    log_file,
                    f"accept failed: {message_id} :: status={accepted.get('status')}",
                )
        except Exception as exc:
            summary["errors"] += 1
            _append_log(log_file, f"error handling {message_id}: {exc}")

    return summary


def run(args: argparse.Namespace) -> int:
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parent))
    sys.path.insert(0, str(project_dir))

    try:
        import prime_bridge_runtime as bridge
    except Exception as exc:
        print(f"bridge_poller: import failed: {exc}", file=sys.stderr)
        return 1

    peer_for = {"codex": "prime", "prime": "codex"}
    if args.agent not in peer_for:
        print("bridge_poller: agent must be 'codex' or 'prime'", file=sys.stderr)
        return 1
    peer = peer_for[args.agent]
    bridge_db_path = getattr(bridge, "DB_PATH", None)
    write_enabled = args.auto_actions and bool(bridge_db_path) and os.access(
        str(bridge_db_path), os.W_OK
    )

    hooks_dir = project_dir / ".claude" / "hooks"
    lock_file = hooks_dir / f".bridge-poller-{args.agent}.lock"
    state_file = hooks_dir / f".bridge-poller-state-{args.agent}.json"
    log_file = hooks_dir / f".bridge-poller-{args.agent}.log"

    with _FileLock(lock_file):
        state = _load_state(state_file)
        last_event_id = int(state.get("last_event_id", 0) or 0)

        def _checkpoint() -> None:
            state["last_event_id"] = last_event_id
            state["updated_at"] = _now()
            _save_state(state_file, state)

        if args.once:
            try:
                events = bridge.list_notifications(
                    agent=args.agent,
                    after_event_id=last_event_id,
                    limit=args.limit,
                )
                last_event_id = max(last_event_id, int(events.get("last_event_id", last_event_id)))
                handled = _handle_inbox(
                    bridge, args.agent, peer, log_file, write_enabled=write_enabled
                )
                _checkpoint()
                print(
                    json.dumps(
                        {
                            "ok": True,
                            "agent": args.agent,
                            "last_event_id": last_event_id,
                            "handled": handled,
                        }
                    )
                )
                return 0
            except Exception as exc:
                _append_log(log_file, f"once-mode error: {exc}")
                _checkpoint()
                return 1

        _append_log(log_file, f"poller start: agent={args.agent}, last_event_id={last_event_id}")
        while True:
            try:
                event_batch = bridge.wait_for_notifications(
                    agent=args.agent,
                    after_event_id=last_event_id,
                    timeout_seconds=args.timeout_seconds,
                    poll_interval_ms=args.poll_interval_ms,
                    limit=args.limit,
                )
                if event_batch.get("notified"):
                    last_event_id = max(
                        last_event_id,
                        int(event_batch.get("last_event_id", last_event_id)),
                    )
                    handled = _handle_inbox(
                        bridge, args.agent, peer, log_file, write_enabled=write_enabled
                    )
                    if (
                        handled["detected"]
                        or handled["accepted"]
                        or handled["resolved_acks"]
                        or handled["readonly_skips"]
                        or handled["errors"]
                    ):
                        _append_log(
                            log_file,
                            "cycle: "
                            f"detected={handled['detected']} "
                            f"accepted={handled['accepted']} "
                            f"resolved_acks={handled['resolved_acks']} "
                            f"readonly_skips={handled['readonly_skips']} "
                            f"errors={handled['errors']} "
                            f"last_event_id={last_event_id}",
                        )
                _checkpoint()
            except Exception as exc:
                _append_log(log_file, f"loop error: {exc}")
                _checkpoint()
                time.sleep(args.error_backoff_seconds)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Periodic Prime Bridge notification poller")
    parser.add_argument("--agent", choices=["codex", "prime"], required=True)
    parser.add_argument(
        "--auto-actions",
        action="store_true",
        help="Enable auto-accept/auto-resolve writes (requires bridge DB write access).",
    )
    parser.add_argument("--once", action="store_true", help="Run one poll cycle and exit")
    parser.add_argument("--timeout-seconds", type=int, default=20, help="Long-poll timeout")
    parser.add_argument("--poll-interval-ms", type=int, default=500, help="Within-call poll interval")
    parser.add_argument("--limit", type=int, default=50, help="Max events per poll")
    parser.add_argument(
        "--error-backoff-seconds",
        type=float,
        default=2.0,
        help="Sleep duration after loop errors",
    )
    return parser


def main() -> int:
    _consume_stdin_if_present()
    parser = build_parser()
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
