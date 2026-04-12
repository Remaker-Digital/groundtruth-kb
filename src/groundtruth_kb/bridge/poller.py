# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Legacy periodic notification poller for the SQLite/MCP bridge runtime.

Retained for compatibility with older database-backed bridge deployments. New
dual-agent projects should use project-owned file bridge OS pollers instead.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

# Cross-platform file locking
if os.name == "nt":
    import msvcrt
else:
    import fcntl

from groundtruth_kb.bridge.context import (
    DEFAULT_MAX_DISPATCH_TARGETS,
    dedupe_preserve_order,
    prioritize_inbox_items,
)
from groundtruth_kb.bridge.worker import resident_worker_should_defer

DIRECT_WAKE_EVENT_TYPES = {"message.failed"}
SUBSTANTIVE_WAKE_COOLDOWN_SECONDS = 5 * 60


def _now() -> str:
    return datetime.now(UTC).isoformat()


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
        if not self.path.exists() or self.path.stat().st_size == 0:
            self.path.write_bytes(b"\x00")
        self._fh = open(self.path, "r+b")
        self._fh.seek(0)
        try:
            if os.name == "nt":
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, PermissionError):
            self._fh.close()
            self._fh = None
            raise RuntimeError(f"bridge poller lock busy: {self.path}")
        return self

    def __exit__(self, *_args):
        if self._fh:
            try:
                if os.name == "nt":
                    self._fh.seek(0)
                    msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            self._fh.close()
            self._fh = None


def _load_state(path: Path) -> dict:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            raise ValueError("poller state must be a dict")
        wake_state = state.get("last_wake_by_message")
        if not isinstance(wake_state, dict):
            state["last_wake_by_message"] = {}
        return state
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"last_event_id": 0, "updated_at": _now(), "last_wake_by_message": {}}


def _save_state(path: Path, state: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def _save_json(path: Path, payload: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError:
        pass


def _append_log(path: Path, message: str) -> None:
    line = f"[{datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        pass


def _launch_agent_wake(
    agent: str,
    project_dir: Path,
    message_ids: list[str],
    log_file: Path,
    *,
    trigger: str,
) -> list[str]:
    if not message_ids:
        return []

    python_exe = Path(sys.executable)
    pythonw_exe = python_exe.with_name("pythonw.exe")
    runner = pythonw_exe if pythonw_exe.exists() else python_exe
    wake_script = project_dir / "scripts" / "codex_bridge_wake.py"
    if not wake_script.exists():
        _append_log(log_file, f"wake skipped: script missing at {wake_script}")
        return []

    unique_ids = dedupe_preserve_order(message_ids)
    launch_ids = unique_ids[:DEFAULT_MAX_DISPATCH_TARGETS]
    deferred_ids = unique_ids[DEFAULT_MAX_DISPATCH_TARGETS:]
    if deferred_ids:
        _append_log(
            log_file,
            f"wake launch capped at {DEFAULT_MAX_DISPATCH_TARGETS}; deferred_message_ids={','.join(deferred_ids)}",
        )

    cmd = [str(runner), str(wake_script), "--agent", agent, "--trigger", trigger]
    for message_id in launch_ids:
        cmd.extend(["--message-id", message_id])

    try:
        popen_kwargs: dict[str, object] = {
            "cwd": str(project_dir),
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        subprocess.Popen(cmd, **popen_kwargs)
        _append_log(
            log_file,
            f"wake launched agent={agent} trigger={trigger} message_ids={','.join(launch_ids)}",
        )
        return launch_ids
    except Exception as exc:
        _append_log(log_file, f"wake launch failed for {message_ids}: {exc}")
        return []


def _notification_message_ref(event: dict) -> str | None:
    details = event.get("details") or {}
    for candidate in (
        details.get("thread_id"),
        details.get("latest_request_message_id"),
        details.get("latest_substantive_message_id"),
        event.get("message_id"),
    ):
        if candidate:
            return str(candidate)
    return None


def _notification_should_wake(agent: str, event: dict) -> bool:
    event_type = str(event.get("event_type") or "")
    details = event.get("details") or {}
    if event_type == "message.failed":
        return details.get("sender") == agent
    return False


def _last_wake_at(state: dict, message_id: str) -> datetime | None:
    wake_state = state.get("last_wake_by_message", {})
    if not isinstance(wake_state, dict):
        return None
    value = wake_state.get(message_id)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _should_wake_substantive_item(
    item: dict,
    state: dict,
    *,
    cooldown_seconds: int = SUBSTANTIVE_WAKE_COOLDOWN_SECONDS,
) -> bool:
    message_id = str(item.get("id") or "")
    if not message_id or item.get("status") == "failed":
        return False
    last_wake = _last_wake_at(state, message_id)
    if last_wake is None:
        return True
    return (datetime.now(UTC) - last_wake).total_seconds() >= cooldown_seconds


def _record_wake_launch(state: dict, message_ids: list[str]) -> None:
    if not message_ids:
        return
    wake_state = state.setdefault("last_wake_by_message", {})
    if not isinstance(wake_state, dict):
        wake_state = {}
        state["last_wake_by_message"] = wake_state
    timestamp = _now()
    for message_id in sorted(set(message_ids)):
        wake_state[message_id] = timestamp


def _resident_worker_health(
    agent: str,
    *,
    hooks_dir: Path,
) -> tuple[bool, str]:
    return resident_worker_should_defer(agent, [], hooks_dir=hooks_dir)


def _resident_worker_should_defer_wake(
    agent: str,
    wake_candidates: list[str],
    *,
    hooks_dir: Path,
    now: datetime | None = None,
) -> tuple[bool, str]:
    return resident_worker_should_defer(
        agent,
        wake_candidates,
        hooks_dir=hooks_dir,
        now=now,
    )


def _handle_notification_batch(
    bridge,
    agent: str,
    events: list[dict],
    log_file: Path,
) -> dict:
    summary = {
        "failed_events": 0,
        "wake_refs": [],
    }

    for event in events:
        event_type = str(event.get("event_type") or "")
        if event_type not in DIRECT_WAKE_EVENT_TYPES:
            continue

        message_ref = _notification_message_ref(event)
        if not message_ref:
            continue

        if event_type == "message.failed":
            summary["failed_events"] += 1

        details = event.get("details") or {}
        _append_log(
            log_file,
            f"signal event: type={event_type} ref={message_ref} subject={event.get('subject', '')} details={json.dumps(details, sort_keys=True)}",
        )
        if _notification_should_wake(agent, event):
            summary["wake_refs"].append(message_ref)

    summary["wake_refs"] = dedupe_preserve_order(summary["wake_refs"])
    return summary


def _handle_inbox(
    bridge,
    agent: str,
    peer: str,
    log_file: Path,
    *,
    state: dict,
    project_dir: Path,
    write_enabled: bool,
    resident_worker_healthy: bool = False,
) -> dict:
    """
    Handle new inbox items for `agent`.

    - Peer messages are surfaced for a substantive reply, never auto-accepted.
    - Invalid inbox items remain visible in runtime reporting, but are not
      surfaced as fresh actionable work.
    - Repeated wake for the same unresolved substantive item is suppressed for
      a short cooldown window.
    """
    summary = {
        "detected": 0,
        "surfaced": 0,
        "failed_inbox": 0,
        "readonly_skips": 0,
        "resident_deferrals": 0,
        "errors": 0,
        "wake_candidates": [],
    }
    inbox = bridge.list_inbox(agent=agent, status="pending", limit=100)
    items = prioritize_inbox_items(inbox.get("items", []))
    wake_candidates: list[str] = []

    for item in items:
        if item.get("sender") != peer:
            continue

        message_id = item.get("id")
        subject = item.get("subject", "")
        if not message_id:
            continue
        summary["detected"] += 1

        if item.get("status") == "failed":
            summary["failed_inbox"] += 1
            _append_log(
                log_file,
                f"invalid substantive item ignored for wake: {message_id} :: {subject}",
            )
            continue

        if not write_enabled:
            summary["readonly_skips"] += 1
            _append_log(
                log_file,
                f"detected (read-only mode, no auto-response): {message_id} :: {subject}",
            )
            if not _should_wake_substantive_item(item, state):
                _append_log(
                    log_file,
                    f"suppressed repeat wake: {message_id} :: {subject}",
                )
                continue
            wake_candidates.append(message_id)
            continue

        try:
            if not _should_wake_substantive_item(item, state):
                _append_log(log_file, f"suppressed repeat wake: {message_id} :: {subject}")
                continue

            summary["surfaced"] += 1
            _append_log(log_file, f"surfaced substantive work (no auto-accept): {message_id} :: {subject}")
            wake_candidates.append(message_id)
        except Exception as exc:
            summary["errors"] += 1
            _append_log(log_file, f"error handling {message_id}: {exc}")

    summary["wake_candidates"] = dedupe_preserve_order(wake_candidates)
    return summary


def run(args: argparse.Namespace, project_dir: Path | None = None) -> int:
    if project_dir is None:
        project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))

    from groundtruth_kb.bridge import runtime as bridge

    peer_for = {"codex": "prime", "prime": "codex"}
    if args.agent not in peer_for:
        print("bridge_poller: agent must be 'codex' or 'prime'", file=sys.stderr)
        return 1
    peer = peer_for[args.agent]
    bridge_db_path = getattr(bridge, "DB_PATH", None)
    write_enabled = args.auto_actions and bool(bridge_db_path) and os.access(str(bridge_db_path), os.W_OK)

    hooks_dir = project_dir / ".claude" / "hooks"
    lock_file = hooks_dir / f".bridge-poller-{args.agent}.lock"
    state_file = hooks_dir / f".bridge-poller-state-{args.agent}.json"
    pid_file = hooks_dir / f".bridge-poller-{args.agent}.pid"
    log_file = hooks_dir / f".bridge-poller-{args.agent}.log"

    with _FileLock(lock_file):
        state = _load_state(state_file)
        last_event_id = int(state.get("last_event_id", 0) or 0)
        process_started_at = state.get("started_at") or _now()

        def _checkpoint() -> None:
            state["last_event_id"] = last_event_id
            state["updated_at"] = _now()
            if not args.once:
                state["pid"] = os.getpid()
                state["agent"] = args.agent
                state["started_at"] = process_started_at
                _save_json(
                    pid_file,
                    {
                        "pid": os.getpid(),
                        "agent": args.agent,
                        "started_at": process_started_at,
                        "updated_at": state["updated_at"],
                    },
                )
            _save_state(state_file, state)

        if args.once:
            try:
                resident_worker_healthy, resident_worker_state = _resident_worker_health(
                    args.agent,
                    hooks_dir=hooks_dir,
                )
                events = bridge.list_notifications(
                    agent=args.agent,
                    after_event_id=last_event_id,
                    limit=args.limit,
                )
                last_event_id = max(last_event_id, int(events.get("last_event_id", last_event_id)))
                event_items = events.get("items", [])
                signals = _handle_notification_batch(
                    bridge,
                    args.agent,
                    event_items,
                    log_file,
                )
                handled = _handle_inbox(
                    bridge,
                    args.agent,
                    peer,
                    log_file,
                    state=state,
                    project_dir=project_dir,
                    write_enabled=write_enabled,
                    resident_worker_healthy=resident_worker_healthy,
                )
                wake_candidates = dedupe_preserve_order([*handled["wake_candidates"], *signals["wake_refs"]])
                trigger = "poller-notification"
                wake_launched = 0
                should_defer, defer_state = _resident_worker_should_defer_wake(
                    args.agent,
                    wake_candidates,
                    hooks_dir=hooks_dir,
                )
                if wake_candidates and should_defer:
                    handled["resident_deferrals"] += len(wake_candidates)
                    _append_log(
                        log_file,
                        f"resident worker healthy ({defer_state}); fallback wake suppressed for {','.join(wake_candidates)}",
                    )
                elif wake_candidates:
                    launched_ids = _launch_agent_wake(
                        args.agent,
                        project_dir,
                        wake_candidates,
                        log_file,
                        trigger=trigger,
                    )
                    if launched_ids:
                        _record_wake_launch(state, launched_ids)
                        wake_launched = len(launched_ids)
                handled["wake_launched"] = wake_launched
                handled["signal_failed_events"] = signals["failed_events"]
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

        _checkpoint()
        _append_log(log_file, f"poller start: agent={args.agent}, last_event_id={last_event_id}")
        while True:
            try:
                resident_worker_healthy, resident_worker_state = _resident_worker_health(
                    args.agent,
                    hooks_dir=hooks_dir,
                )
                event_batch = bridge.wait_for_notifications(
                    agent=args.agent,
                    after_event_id=last_event_id,
                    timeout_seconds=args.timeout_seconds,
                    poll_interval_ms=args.poll_interval_ms,
                    limit=args.limit,
                )
                if event_batch.get("notified"):
                    event_items = event_batch.get("items", [])
                    last_event_id = max(
                        last_event_id,
                        int(event_batch.get("last_event_id", last_event_id)),
                    )
                    signals = _handle_notification_batch(
                        bridge,
                        args.agent,
                        event_items,
                        log_file,
                    )
                    handled = _handle_inbox(
                        bridge,
                        args.agent,
                        peer,
                        log_file,
                        state=state,
                        project_dir=project_dir,
                        write_enabled=write_enabled,
                        resident_worker_healthy=resident_worker_healthy,
                    )
                    wake_candidates = dedupe_preserve_order([*handled["wake_candidates"], *signals["wake_refs"]])
                    trigger = "poller-notification"
                    should_defer, defer_state = _resident_worker_should_defer_wake(
                        args.agent,
                        wake_candidates,
                        hooks_dir=hooks_dir,
                    )
                    if wake_candidates and should_defer:
                        handled["wake_launched"] = 0
                        handled["resident_deferrals"] += len(wake_candidates)
                        _append_log(
                            log_file,
                            f"resident worker healthy ({defer_state}); fallback wake suppressed for {','.join(wake_candidates)}",
                        )
                    elif wake_candidates:
                        launched_ids = _launch_agent_wake(
                            args.agent,
                            project_dir,
                            wake_candidates,
                            log_file,
                            trigger=trigger,
                        )
                        if launched_ids:
                            _record_wake_launch(state, launched_ids)
                            handled["wake_launched"] = len(launched_ids)
                        else:
                            handled["wake_launched"] = 0
                    else:
                        handled["wake_launched"] = 0
                    handled["signal_failed_events"] = signals["failed_events"]
                    if (
                        handled["detected"]
                        or handled["surfaced"]
                        or handled["signal_failed_events"]
                        or handled["readonly_skips"]
                        or handled["resident_deferrals"]
                        or handled["errors"]
                        or handled["wake_launched"]
                    ):
                        _append_log(
                            log_file,
                            "cycle: "
                            f"detected={handled['detected']} "
                            f"surfaced={handled['surfaced']} "
                            f"signal_failed_events={handled['signal_failed_events']} "
                            f"readonly_skips={handled['readonly_skips']} "
                            f"resident_deferrals={handled['resident_deferrals']} "
                            f"wake_launched={handled['wake_launched']} "
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
        help="Enable protocol-ack auto-resolve writes (substantive work is never auto-accepted).",
    )
    parser.add_argument("--once", action="store_true", help="Run one poll cycle and exit")
    parser.add_argument("--timeout-seconds", type=int, default=20, help="Long-poll timeout")
    parser.add_argument("--poll-interval-ms", type=int, default=100, help="Within-call poll interval")
    parser.add_argument("--limit", type=int, default=50, help="Max events per poll")
    parser.add_argument(
        "--error-backoff-seconds",
        type=float,
        default=2.0,
        help="Sleep duration after loop errors",
    )
    parser.add_argument(
        "--project-dir", type=str, default=None, help="Project directory (defaults to CLAUDE_PROJECT_DIR or cwd)"
    )
    return parser


def main() -> int:
    _consume_stdin_if_present()
    args = build_parser().parse_args()
    project_dir = Path(args.project_dir) if args.project_dir else None
    return run(args, project_dir=project_dir)


if __name__ == "__main__":
    raise SystemExit(main())
