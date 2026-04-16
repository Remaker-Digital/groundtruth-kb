# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Legacy bridge resident worker for the SQLite/MCP bridge runtime.

Retained for compatibility with older database-backed bridge deployments. New
dual-agent projects should use project-owned file bridge OS pollers instead.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, BinaryIO, cast

# Cross-platform file locking
if sys.platform == "win32":
    import msvcrt
else:
    import fcntl

from groundtruth_kb.bridge.context import (
    DEFAULT_MAX_DISPATCH_TARGETS,
    build_context_snapshot,
    build_contexts,
    build_prompt,
    context_requires_action,
    fast_path_session_start_requests,
    repair_terminal_thread_outputs,
    select_dispatch_batch,
)

_log = logging.getLogger(__name__)

DIRECT_CONTEXT_EVENT_TYPES = {
    "message.failed",
    # "message.resolved" intentionally excluded — resolution is informational,
    # not actionable. Including it caused an echo loop: resolved -> worker wakes
    # -> repair_terminal_thread_outputs sends reply -> notification -> loop.
    # Aligned with bridge_poller.py DIRECT_WAKE_EVENT_TYPES which also excludes it.
}
BUSY_GRACE_SECONDS = 60
HEALTHY_IDLE_SECONDS = 90
FAILED_RESIDUE_MAX_AGE_MINUTES = 15
FAILED_RESIDUE_CLEANUP_INTERVAL_SECONDS = 10 * 60
FAILED_RESIDUE_CLEANUP_LIMIT = 200
RETRY_SWEEP_INTERVAL_SECONDS = 5 * 60
RETRY_STALE_THRESHOLD_SECONDS = 3 * 60


def _now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


def _now_iso() -> str:
    """Return the current UTC datetime as an ISO 8601 string."""
    return _now().isoformat()


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


def _agent_model(agent: str) -> str:
    """Return the model identifier string for the given agent name."""
    return "opus" if agent == "prime" else "codex"


def _hooks_dir(project_dir: Path) -> Path:
    """Return the path to the .claude/hooks directory inside the project."""
    return project_dir / ".claude" / "hooks"


def _state_file(agent: str, project_dir: Path) -> Path:
    """Return the path to the persistent state file for the given agent worker."""
    return _hooks_dir(project_dir) / f".{agent}-bridge-worker-state.json"


def _lock_file(agent: str, project_dir: Path) -> Path:
    """Return the path to the advisory lock file for the given agent worker."""
    return _hooks_dir(project_dir) / f".{agent}-bridge-worker.lock"


def _log_file(agent: str, project_dir: Path) -> Path:
    """Return the path to the append-only log file for the given agent worker."""
    return _hooks_dir(project_dir) / f".{agent}-bridge-worker.log"


def _last_message_file(agent: str, project_dir: Path) -> Path:
    """Return the path to the file used to capture the agent's last raw message output."""
    return _hooks_dir(project_dir) / f".{agent}-bridge-worker-last-message.txt"


def _last_stdout_file(agent: str, project_dir: Path) -> Path:
    """Return the path to the JSONL file capturing the last stdout from the agent process."""
    return _hooks_dir(project_dir) / f".{agent}-bridge-worker-last-stdout.jsonl"


def _last_context_file(agent: str, project_dir: Path) -> Path:
    """Return the path to the file holding the last dispatched context snapshot."""
    return _hooks_dir(project_dir) / f".{agent}-bridge-worker-last-context.json"


def _health_file(agent: str, project_dir: Path) -> Path:
    """Return the path to the health status JSON file for the given agent worker."""
    return _hooks_dir(project_dir) / f".bridge-worker-{agent}-health.json"


def _load_state(agent: str, project_dir: Path) -> dict[str, Any]:
    """Load persisted worker state from disk, returning defaults on any read or parse error."""
    try:
        state = json.loads(_state_file(agent, project_dir).read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            raise ValueError("worker state must be a dict")
        if not isinstance(state.get("last_wake_by_message"), dict):
            state["last_wake_by_message"] = {}
        return state
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return {"last_event_id": 0, "last_wake_by_message": {}}


def _save_state(agent: str, state: dict[str, Any], project_dir: Path) -> None:
    """Persist the worker state dict to disk as pretty-printed JSON."""
    hooks = _hooks_dir(project_dir)
    hooks.mkdir(parents=True, exist_ok=True)
    _state_file(agent, project_dir).write_text(json.dumps(state, indent=2), encoding="utf-8")


class _FileLock:
    """Cross-platform advisory file lock used to prevent concurrent worker runs."""

    def __init__(self, path: Path) -> None:
        """Initialise the lock with the path of the lock file to use."""
        self.path = path
        self._fh: BinaryIO | None = None

    def __enter__(self) -> _FileLock:
        """Acquire the exclusive lock, raising OSError if already held."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists() or self.path.stat().st_size == 0:
            self.path.write_bytes(b"\x00")
        fh: BinaryIO = open(self.path, "r+b")
        fh.seek(0)
        if sys.platform == "win32":
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        self._fh = fh
        return self

    def __exit__(self, *_args: object) -> None:
        """Release the file lock and close the underlying file handle."""
        fh = self._fh
        if fh is None:
            return
        try:
            if sys.platform == "win32":
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        fh.close()
        self._fh = None


def _find_codex_exe() -> Path:
    """Locate the Codex CLI executable, raising FileNotFoundError if absent.

    Returns:
        Path to the Codex shim binary.

    Raises:
        FileNotFoundError: If the Codex shim has not been installed.
    """
    candidate = (
        Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
        / "OpenAI"
        / "Codex"
        / "bin"
        / "codex.exe"
    )
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"Codex shim not found at {candidate}. Run scripts/install_codex_exec_shim.ps1 first.")


def _find_claude_exe() -> Path:
    """Locate the Claude CLI executable, raising FileNotFoundError if absent.

    Returns:
        Path to the Claude CLI binary.

    Raises:
        FileNotFoundError: If the Claude Code CLI is not installed on PATH.
    """
    resolved = shutil.which("claude")
    if resolved:
        return Path(resolved)
    fallback = Path.home() / ".local" / "bin" / "claude.exe"
    if fallback.exists():
        return fallback
    raise FileNotFoundError("Claude CLI not found on PATH. Install Claude Code CLI first.")


def _notification_message_ref(event: dict[str, Any]) -> str | None:
    """Extract the most specific message reference from a notification event dict.

    Args:
        event: A notification event dict from the bridge runtime.

    Returns:
        The first non-empty reference found, or None if none exist.
    """
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


def _explicit_refs_for(agent: str, event_batch: dict[str, Any]) -> list[str]:
    """Collect deduplicated message references that directly concern this agent from a notification batch.

    Args:
        agent: The agent identifier whose references should be collected.
        event_batch: The notification event batch dict from the bridge.

    Returns:
        Ordered list of unique message reference strings.
    """
    refs: list[str] = []
    if not event_batch.get("notified"):
        return refs
    for event in event_batch.get("items", []):
        event_type = str(event.get("event_type") or "")
        details = event.get("details") or {}
        if event_type in DIRECT_CONTEXT_EVENT_TYPES:
            if event_type == "message.failed" and details.get("sender") != agent:
                continue
        elif event.get("agent") != agent:
            continue
        ref = _notification_message_ref(event)
        if ref:
            refs.append(ref)
    deduped_refs: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        deduped_refs.append(ref)
    return deduped_refs


def _invoke_codex(prompt: str, timeout_seconds: int, project_dir: Path) -> subprocess.CompletedProcess[str]:
    """Launch the Codex CLI with the given prompt and return the completed process.

    Args:
        prompt: The prompt text to pass to the Codex CLI.
        timeout_seconds: Maximum seconds to wait before raising TimeoutExpired.
        project_dir: Project root directory passed as the working directory.

    Returns:
        The completed subprocess result.
    """
    cmd = [
        str(_find_codex_exe()),
        "-a",
        "never",
        "exec",
        "-C",
        str(project_dir),
        "--sandbox",
        "danger-full-access",
        "--json",
        "--output-last-message",
        str(_last_message_file("codex", project_dir)),
        prompt,
    ]
    popen_kwargs: dict[str, object] = {
        "cwd": str(project_dir),
        "text": True,
        "timeout": timeout_seconds,
    }
    if sys.platform == "win32":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    completed = cast(subprocess.CompletedProcess[str], subprocess.run(cmd, **cast(Any, popen_kwargs)))
    return completed


def _invoke_prime(prompt: str, timeout_seconds: int, project_dir: Path) -> subprocess.CompletedProcess[str]:
    """Launch the Claude CLI (Prime) with the given prompt and return the completed process.

    Args:
        prompt: The prompt text to pass to the Claude CLI.
        timeout_seconds: Maximum seconds to wait before raising TimeoutExpired.
        project_dir: Project root directory used as the working directory.

    Returns:
        The completed subprocess result.
    """
    cmd = [
        str(_find_claude_exe()),
        "-p",
        "--model",
        _agent_model("prime"),
        "--permission-mode",
        "bypassPermissions",
        "--output-format",
        "json",
        prompt,
    ]
    popen_kwargs: dict[str, object] = {
        "cwd": str(project_dir),
        "capture_output": True,
        "text": True,
        "timeout": timeout_seconds,
    }
    if sys.platform == "win32":
        popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    completed = cast(subprocess.CompletedProcess[str], subprocess.run(cmd, **cast(Any, popen_kwargs)))
    _last_stdout_file("prime", project_dir).write_text(completed.stdout or "", encoding="utf-8")
    _last_message_file("prime", project_dir).write_text(completed.stdout or "", encoding="utf-8")
    return completed


def _write_health(
    agent: str,
    project_dir: Path,
    *,
    status: str,
    last_event_id: int,
    active_message_ids: list[str] | None = None,
    last_thread_id: str | None = None,
    dispatch_started_at: str | None = None,
    dispatch_timeout_seconds: int | None = None,
    last_error: str | None = None,
) -> None:
    """Write a health status JSON file for the agent worker.

    Args:
        agent: The agent identifier.
        project_dir: Project root directory.
        status: Worker lifecycle status (e.g. ``"idle"``, ``"busy"``, ``"error"``).
        last_event_id: Most recently processed notification event ID.
        active_message_ids: Message IDs currently being dispatched, if any.
        last_thread_id: Thread correlation ID from the most recent dispatch.
        dispatch_started_at: ISO timestamp when the current dispatch started.
        dispatch_timeout_seconds: Configured timeout for the current dispatch.
        last_error: Error string from the most recent failure, if any.
    """
    doc = {
        "agent": agent,
        "status": status,
        "pid": os.getpid(),
        "updated_at": _now_iso(),
        "last_event_id": last_event_id,
        "last_notification_event_id": last_event_id,
        "active_message_ids": active_message_ids or [],
        "in_flight_thread_ids": active_message_ids or [],
        "last_thread_id": last_thread_id,
        "dispatch_started_at": dispatch_started_at,
        "dispatch_timeout_seconds": dispatch_timeout_seconds,
        "last_error": last_error,
        "healthy_idle_seconds": HEALTHY_IDLE_SECONDS,
        "busy_grace_seconds": BUSY_GRACE_SECONDS,
    }
    hooks = _hooks_dir(project_dir)
    hooks.mkdir(parents=True, exist_ok=True)
    _health_file(agent, project_dir).write_text(json.dumps(doc, indent=2), encoding="utf-8")


def resident_worker_is_healthy(
    agent: str,
    *,
    hooks_dir: Path | None = None,
    project_dir: Path | None = None,
    now: datetime | None = None,
) -> tuple[bool, str]:
    """Determine whether the resident worker for the given agent is currently healthy.

    Reads the agent's health JSON file and checks whether the reported status and
    timestamps are within acceptable freshness bounds.

    Args:
        agent: The agent identifier (``"codex"`` or ``"prime"``).
        hooks_dir: Explicit hooks directory; derived from ``project_dir`` if omitted.
        project_dir: Project root directory; required when ``hooks_dir`` is omitted.
        now: Optional datetime to use as the current time (for testing).

    Returns:
        A tuple of ``(is_healthy, state_label)`` where ``state_label`` is a
        short string such as ``"idle"``, ``"busy"``, or ``"idle-stale"``.

    Raises:
        ValueError: If neither ``hooks_dir`` nor ``project_dir`` is provided.
    """
    now_value = now or _now()
    if hooks_dir is None:
        if project_dir is None:
            raise ValueError("Either hooks_dir or project_dir must be provided")
        hooks_dir = _hooks_dir(project_dir)
    path = hooks_dir / f".bridge-worker-{agent}-health.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False, "missing-health"

    status = str(payload.get("status") or "")
    updated_at = _parse_iso(payload.get("updated_at"))
    if status == "busy":
        started = _parse_iso(payload.get("dispatch_started_at")) or updated_at
        timeout_seconds = int(payload.get("dispatch_timeout_seconds") or 0)
        if started is None:
            return False, "busy-without-timestamp"
        age = (now_value - started).total_seconds()
        if age <= timeout_seconds + BUSY_GRACE_SECONDS:
            return True, "busy"
        return False, "busy-stale"

    if status in {"idle", "running", "noop", "recovering"}:
        if updated_at is None:
            return False, "missing-updated-at"
        age = (now_value - updated_at).total_seconds()
        if age <= HEALTHY_IDLE_SECONDS:
            return True, status
        return False, "idle-stale"

    return False, f"status={status or 'unknown'}"


def resident_worker_health_snapshot(
    agent: str,
    *,
    hooks_dir: Path | None = None,
    project_dir: Path | None = None,
) -> dict[str, Any] | None:
    """Return the raw health JSON dict for the given agent worker, or None if unreadable.

    Args:
        agent: The agent identifier (``"codex"`` or ``"prime"``).
        hooks_dir: Explicit hooks directory; derived from ``project_dir`` if omitted.
        project_dir: Project root directory; required when ``hooks_dir`` is omitted.

    Returns:
        The health payload dict, or ``None`` if the file is missing or invalid.

    Raises:
        ValueError: If neither ``hooks_dir`` nor ``project_dir`` is provided.
    """
    if hooks_dir is None:
        if project_dir is None:
            raise ValueError("Either hooks_dir or project_dir must be provided")
        hooks_dir = _hooks_dir(project_dir)
    path = hooks_dir / f".bridge-worker-{agent}-health.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def resident_worker_should_defer(
    agent: str,
    target_ids: list[str],
    *,
    hooks_dir: Path | None = None,
    project_dir: Path | None = None,
    now: datetime | None = None,
) -> tuple[bool, str]:
    """Decide whether the poller should defer a wake launch because the resident worker is active.

    When the worker is healthy and either idle or handling the same target messages,
    the poller should skip launching a separate wake subprocess.

    Args:
        agent: The agent identifier.
        target_ids: Message IDs the poller is about to dispatch.
        hooks_dir: Explicit hooks directory; derived from ``project_dir`` if omitted.
        project_dir: Project root directory; required when ``hooks_dir`` is omitted.
        now: Optional current datetime override (for testing).

    Returns:
        A tuple of ``(should_defer, state_label)``.
    """
    healthy, state = resident_worker_is_healthy(agent, hooks_dir=hooks_dir, project_dir=project_dir, now=now)
    if not healthy:
        return False, state

    if state != "busy":
        return True, state

    payload = resident_worker_health_snapshot(agent, hooks_dir=hooks_dir, project_dir=project_dir) or {}
    active_ids = {
        str(message_id).strip() for message_id in (payload.get("active_message_ids") or []) if str(message_id).strip()
    }
    requested_ids = {str(message_id).strip() for message_id in target_ids if str(message_id).strip()}
    if requested_ids and active_ids and requested_ids.issubset(active_ids):
        return True, "busy-same-targets"
    return False, "busy-other-targets"


def _record_dispatch(state: dict[str, Any], message_ids: list[str], trigger: str) -> None:
    """Update the persisted state with timestamps for a new dispatch, recording which messages were handled."""
    timestamp = _now_iso()
    wake_state = state.setdefault("last_wake_by_message", {})
    if not isinstance(wake_state, dict):
        wake_state = {}
        state["last_wake_by_message"] = wake_state
    for message_id in sorted(set(message_ids)):
        wake_state[message_id] = timestamp
    state["last_triggered_at"] = timestamp
    state["last_triggered_ids"] = sorted(set(message_ids))
    state["last_trigger"] = trigger


def _maybe_clear_failed_residue(
    agent: str,
    bridge: Any,
    state: dict[str, Any],
    *,
    log_fn: Callable[[str], None],
    force: bool = False,
) -> int:
    """Periodically purge old failed messages from the bridge to keep the inbox clean.

    Args:
        agent: The agent whose failed messages should be cleared.
        bridge: The bridge runtime module providing ``clear_failed_messages``.
        state: Mutable worker state dict; ``last_failed_cleanup_at`` is updated on run.
        log_fn: Callable used to write log lines.
        force: Skip the interval check and clean up immediately.

    Returns:
        Number of failed messages cleared, or 0 if the interval has not elapsed.
    """
    last_cleanup_at = _parse_iso(state.get("last_failed_cleanup_at"))
    now = _now()
    if (
        not force
        and last_cleanup_at is not None
        and (now - last_cleanup_at).total_seconds() < FAILED_RESIDUE_CLEANUP_INTERVAL_SECONDS
    ):
        return 0

    cleaner = getattr(bridge, "clear_failed_messages", None)
    if not callable(cleaner):
        state["last_failed_cleanup_at"] = now.isoformat()
        return 0

    try:
        result = cleaner(
            agent=agent,
            older_than_minutes=FAILED_RESIDUE_MAX_AGE_MINUTES,
            limit=FAILED_RESIDUE_CLEANUP_LIMIT,
        )
    except Exception as exc:  # intentional-catch: cleanup failure, logged and returns 0
        log_fn(f"failed residue cleanup error: {exc}")
        return 0

    state["last_failed_cleanup_at"] = now.isoformat()
    cleared_count = int((result or {}).get("cleared_count", 0) or 0)
    if cleared_count > 0:
        log_fn(
            f"cleared historical failed residue: agent={agent} cleared_count={cleared_count}",
        )
    return cleared_count


def _maybe_retry_stale_pending(
    agent: str,
    bridge: Any,
    state: dict[str, Any],
    *,
    log_fn: Callable[[str], None],
) -> int:
    """Autonomous persistent retry: re-queue notifications for stale pending outbound messages.

    This is the background driver for the owner's "non-blocking persistent retry"
    requirement. It runs each poll cycle and retries any pending message sent BY
    this agent that has been pending longer than RETRY_STALE_THRESHOLD_SECONDS
    without a peer response.
    """
    last_retry_at = _parse_iso(state.get("last_retry_sweep_at"))
    now = _now()
    if last_retry_at is not None and (now - last_retry_at).total_seconds() < RETRY_SWEEP_INTERVAL_SECONDS:
        return 0

    state["last_retry_sweep_at"] = now.isoformat()

    # Find pending messages sent BY this agent (outbound) that are stale.
    # Uses list_stale_outbound (sender-facing, high limit) instead of
    # list_inbox (recipient-facing, capped at 200) so all stale outbound
    # messages are visible regardless of inbox size.
    retrier = getattr(bridge, "retry_pending_message", None)
    stale_lister = getattr(bridge, "list_stale_outbound", None)
    if not callable(retrier) or not callable(stale_lister):
        return 0

    peer = "codex" if agent == "prime" else "prime"
    stale_result = stale_lister(
        sender=agent,
        older_than_seconds=RETRY_STALE_THRESHOLD_SECONDS,
        limit=500,
    )
    items = stale_result.get("items", [])
    retried = 0

    for item in items:
        message_id = item.get("id")
        if not message_id:
            continue

        try:
            result = retrier(message_id=message_id, agent=peer)
            if result.get("ok"):
                retried += 1
                log_fn(f"autonomous retry: message={message_id} retry_count={result.get('retry_count')}")
            elif "max retries exceeded" in str(result.get("reason", "")):
                log_fn(f"autonomous retry exhausted: message={message_id}")
        except Exception as exc:  # intentional-catch: per-message error, logged and continues
            log_fn(f"autonomous retry error: message={message_id} error={exc}")

    if retried > 0:
        log_fn(f"autonomous retry sweep: {retried} message(s) re-queued")
    return retried


def _capture_target_state(
    bridge: Any,
    agent: str,
    target_ids: list[str],
) -> dict[str, dict[str, Any]]:
    """Snapshot the current bridge state for a set of target message IDs.

    Used before and after a dispatch to detect whether the agent made progress.

    Args:
        bridge: The bridge runtime module providing ``get_worker_event_payload``.
        agent: The agent identifier.
        target_ids: Message IDs whose state should be captured.

    Returns:
        A dict mapping each target ID to a state summary dict.
    """
    snapshot: dict[str, dict[str, Any]] = {}
    for target_id in sorted(set(target_ids)):
        payload = bridge.get_worker_event_payload(target_id, agent=agent)
        if isinstance(payload, dict) and "context" in payload:
            payload = payload.get("context")
        if not isinstance(payload, dict):
            snapshot[target_id] = {"missing": True}
            continue
        canonical = payload.get("canonical_message") or {}
        latest = payload.get("latest_thread_message") or {}
        thread_messages = payload.get("thread_messages") or []
        snapshot[target_id] = {
            "canonical_status": canonical.get("status"),
            "resolved_at": canonical.get("resolved_at"),
            "latest_thread_message_id": latest.get("id"),
            "message_count": len(thread_messages),
        }
    return snapshot


def _seed_last_event_id(
    agent: str,
    bridge: Any,
    state: dict[str, Any],
) -> int:
    """Initialise the notification cursor from the bridge when no prior state exists.

    Args:
        agent: The agent identifier.
        bridge: The bridge runtime module providing ``get_latest_notification_event_id``.
        state: Mutable worker state dict; ``last_event_id`` is updated when seeded.

    Returns:
        The current ``last_event_id`` to use for the first poll.
    """
    current = int(state.get("last_event_id", 0) or 0)
    if current > 0:
        return current

    getter = getattr(bridge, "get_latest_notification_event_id", None)
    if not callable(getter):
        return current

    payload = getter(agent=agent)
    seeded = 0
    if isinstance(payload, dict):
        seeded = int(payload.get("last_event_id", 0) or 0)
    elif payload is not None:
        seeded = int(payload)
    if seeded > 0:
        state["last_event_id"] = seeded
        _log.info("seeded resident worker notification cursor: last_event_id=%d", seeded)
    return seeded


def run(args: argparse.Namespace, project_dir: Path | None = None) -> int:
    """Start the long-lived resident bridge worker loop for the configured agent.

    Acquires the worker lock, seeds the notification cursor, and processes bridge
    events in a tight poll loop until interrupted or a fatal error occurs.

    Args:
        args: Parsed CLI arguments from :func:`build_parser`.
        project_dir: Project root directory; resolved from environment if ``None``.

    Returns:
        Exit code: ``0`` on clean exit (including lock-busy), or ``1`` on setup failure.
    """
    if project_dir is None:
        project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))

    from groundtruth_kb.bridge import runtime as bridge

    try:
        with _FileLock(_lock_file(args.agent, project_dir)):
            state = _load_state(args.agent, project_dir)
            last_event_id = _seed_last_event_id(args.agent, bridge, state)
            _log.info("resident worker start: last_event_id=%d", last_event_id)
            _save_state(args.agent, state, project_dir)
            _write_health(args.agent, project_dir, status="idle", last_event_id=last_event_id)
            startup_scan_pending = True
            consecutive_errors = 0  # Phase C: track repeated failures

            event_batch: dict[str, Any]  # forward declaration for mypy --strict
            while True:
                try:
                    if startup_scan_pending:
                        event_batch = {
                            "notified": False,
                            "count": 0,
                            "last_event_id": last_event_id,
                            "items": [],
                        }
                        startup_scan_pending = False
                    else:
                        event_batch = bridge.wait_for_notifications(
                            agent=args.agent,
                            after_event_id=last_event_id,
                            timeout_seconds=args.timeout_seconds,
                            poll_interval_ms=args.poll_interval_ms,
                            limit=args.limit,
                        )
                    if event_batch.get("notified"):
                        last_event_id = max(last_event_id, int(event_batch.get("last_event_id", last_event_id)))

                    state["last_event_id"] = last_event_id
                    _maybe_clear_failed_residue(
                        args.agent,
                        bridge,
                        state,
                        log_fn=_log.info,
                    )
                    _maybe_retry_stale_pending(
                        args.agent,
                        bridge,
                        state,
                        log_fn=_log.info,
                    )
                    explicit_refs = _explicit_refs_for(args.agent, event_batch)
                    new_items = bridge.list_inbox(agent=args.agent, status="pending", limit=100).get("items", [])
                    contexts = build_contexts(
                        bridge,
                        agent=args.agent,
                        explicit_refs=explicit_refs,
                        new_items=new_items,
                        project_dir=project_dir,
                        log_fn=_log.info,
                        max_contexts=args.max_dispatch_targets,
                    )
                    pending_ids = {
                        str(item.get("id") or "").strip() for item in new_items if str(item.get("id") or "").strip()
                    }
                    contexts = [
                        context
                        for context in contexts
                        if str((context.get("canonical_message") or {}).get("id") or "").strip() in pending_ids
                        or context_requires_action(args.agent, context)
                    ]

                    batch = select_dispatch_batch(
                        contexts,
                        new_items,
                        max_targets=args.max_dispatch_targets,
                    )
                    batch_contexts = batch["contexts"]
                    batch_new_items = batch["new_items"]
                    targets = batch["target_ids"]
                    deferred_targets = batch["deferred_ids"]

                    if not batch_new_items and not batch_contexts:
                        _save_state(args.agent, state, project_dir)
                        _write_health(args.agent, project_dir, status="idle", last_event_id=last_event_id)
                        continue

                    if deferred_targets:
                        _log.info(
                            "dispatch batch capped at %d; deferred_targets=%s",
                            args.max_dispatch_targets,
                            ",".join(deferred_targets),
                        )

                    pre_repair_count = repair_terminal_thread_outputs(
                        bridge,
                        agent=args.agent,
                        target_refs=targets,
                        project_dir=project_dir,
                        log_fn=_log.info,
                    )
                    if pre_repair_count > 0:
                        _log.info(
                            "pre-dispatch terminal repair handled %d target(s); re-evaluating queue",
                            pre_repair_count,
                        )
                        _write_health(args.agent, project_dir, status="running", last_event_id=last_event_id)
                        startup_scan_pending = True  # force immediate inbox re-scan
                        continue

                    fast_path_count = fast_path_session_start_requests(
                        bridge,
                        agent=args.agent,
                        target_refs=targets,
                        project_dir=project_dir,
                        log_fn=_log.info,
                    )
                    if fast_path_count > 0:
                        _log.info(
                            "session-start fast path handled %d target(s); re-evaluating queue",
                            fast_path_count,
                        )
                        _write_health(args.agent, project_dir, status="running", last_event_id=last_event_id)
                        startup_scan_pending = True
                        continue

                    payload = build_context_snapshot(
                        trigger="resident-worker",
                        contexts=batch_contexts,
                        new_items=batch_new_items,
                    )
                    hooks = _hooks_dir(project_dir)
                    hooks.mkdir(parents=True, exist_ok=True)
                    context_file = _last_context_file(args.agent, project_dir)
                    context_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

                    prompt = build_prompt(
                        args.agent,
                        context_file,
                        batch_new_items,
                        batch_contexts,
                        project_dir=project_dir,
                    )
                    _record_dispatch(state, targets, "resident-worker")
                    _save_state(args.agent, state, project_dir)

                    dispatch_started_at = _now_iso()
                    _write_health(
                        args.agent,
                        project_dir,
                        status="busy",
                        last_event_id=last_event_id,
                        active_message_ids=targets,
                        last_thread_id=batch_contexts[0]["thread_correlation_id"] if batch_contexts else None,
                        dispatch_started_at=dispatch_started_at,
                        dispatch_timeout_seconds=args.exec_timeout_seconds,
                    )
                    _log.info(
                        "dispatching resident worker run: targets=%s new=%d contexts=%d",
                        ",".join(targets),
                        len(batch_new_items),
                        len(batch_contexts),
                    )
                    pre_dispatch_state = _capture_target_state(bridge, args.agent, targets)

                    if args.agent == "codex":
                        completed = _invoke_codex(prompt, args.exec_timeout_seconds, project_dir)
                    else:
                        completed = _invoke_prime(prompt, args.exec_timeout_seconds, project_dir)

                    repair_count = repair_terminal_thread_outputs(
                        bridge,
                        agent=args.agent,
                        target_refs=targets,
                        project_dir=project_dir,
                        log_fn=_log.info,
                    )
                    post_dispatch_state = _capture_target_state(bridge, args.agent, targets)
                    made_progress = pre_dispatch_state != post_dispatch_state or repair_count > 0

                    if completed.stderr:
                        _log.warning("worker stderr: %s", completed.stderr.strip())
                    _log.info("worker exit=%d", completed.returncode)
                    if completed.returncode == 0 and not made_progress:
                        _log.warning(
                            "worker made no bridge progress: targets=%s",
                            ",".join(targets),
                        )
                    post_status = (
                        "running"
                        if completed.returncode == 0 and made_progress
                        else "idle"
                        if completed.returncode == 0
                        else "error"
                    )
                    if completed.returncode == 0:
                        consecutive_errors = 0  # Phase C: reset on success
                    _write_health(
                        args.agent,
                        project_dir,
                        status=post_status,
                        last_event_id=last_event_id,
                        last_thread_id=batch_contexts[0]["thread_correlation_id"] if batch_contexts else None,
                        last_error=(((completed.stderr or "").strip() or None) if completed.returncode else None),
                    )
                    if completed.returncode != 0:
                        time.sleep(args.error_backoff_seconds)
                except Exception as exc:  # intentional-catch: dispatch error, consecutive counter + backoff
                    consecutive_errors += 1
                    _log.error("loop error (%d): %s", consecutive_errors, exc)
                    # Phase C: Distinguish message-level from worker-level failure.
                    # A single context/dispatch error should not permanently stop the worker.
                    if consecutive_errors >= 5:
                        _write_health(
                            args.agent,
                            project_dir,
                            status="error",
                            last_event_id=last_event_id,
                            last_error=f"repeated error ({consecutive_errors}x): {exc}",
                        )
                        # Longer backoff for repeated failures
                        time.sleep(args.error_backoff_seconds * min(consecutive_errors, 12))
                    else:
                        _write_health(
                            args.agent,
                            project_dir,
                            status="recovering",
                            last_event_id=last_event_id,
                            last_error=str(exc),
                        )
                        time.sleep(args.error_backoff_seconds)
    except OSError:
        _log.info("resident worker lock busy; another run is active")
        return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser for the resident worker.

    Returns:
        Configured :class:`argparse.ArgumentParser` instance.
    """
    parser = argparse.ArgumentParser(description="Long-lived resident bridge worker")
    parser.add_argument("--agent", choices=["codex", "prime"], default="codex")
    parser.add_argument("--cadence-minutes", type=int, default=9)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--poll-interval-ms", type=int, default=100)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--max-dispatch-targets", type=int, default=DEFAULT_MAX_DISPATCH_TARGETS)
    parser.add_argument("--exec-timeout-seconds", type=int, default=900)
    parser.add_argument("--error-backoff-seconds", type=int, default=5)
    parser.add_argument(
        "--project-dir", type=str, default=None, help="Project directory (defaults to CLAUDE_PROJECT_DIR or cwd)"
    )
    return parser


def main() -> int:
    """Parse arguments and run the resident bridge worker.

    Returns:
        Exit code forwarded from :func:`run`.
    """
    from groundtruth_kb._logging import _setup_bridge_logging

    args = build_parser().parse_args()
    project_dir = Path(args.project_dir) if args.project_dir else None
    _setup_bridge_logging(
        _log_file(args.agent, project_dir or Path(os.environ.get("CLAUDE_PROJECT_DIR", str(Path.cwd()))))
    )
    return run(args, project_dir=project_dir)


if __name__ == "__main__":
    raise SystemExit(main())
