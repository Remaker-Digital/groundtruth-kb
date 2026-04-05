from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import msvcrt

from bridge_worker_context import (
    DEFAULT_MAX_DISPATCH_TARGETS,
    PROJECT_DIR,
    build_context_snapshot,
    build_contexts,
    build_prompt,
    claimed_item_due,
    repair_terminal_thread_outputs,
    select_dispatch_batch,
)


HOOKS_DIR = PROJECT_DIR / ".claude" / "hooks"
DIRECT_CONTEXT_EVENT_TYPES = {
    "message.invalid",
    "message.resolved",
    "thread.updated",
    "thread.ack_breach",
    "thread.response_window_breach",
    "thread.claimed_silence_breach",
}
BUSY_GRACE_SECONDS = 60
HEALTHY_IDLE_SECONDS = 90


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


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


def _agent_model(agent: str) -> str:
    return "opus" if agent == "prime" else "codex"


def _state_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-worker-state.json"


def _lock_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-worker.lock"


def _log_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-worker.log"


def _last_message_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-worker-last-message.txt"


def _last_stdout_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-worker-last-stdout.jsonl"


def _last_context_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-worker-last-context.json"


def _health_file(agent: str) -> Path:
    return HOOKS_DIR / f".bridge-worker-{agent}-health.json"


def _append_log(agent: str, message: str) -> None:
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{_now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    with _log_file(agent).open("a", encoding="utf-8") as fh:
        fh.write(line)


def _load_state(agent: str) -> dict[str, Any]:
    try:
        state = json.loads(_state_file(agent).read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            raise ValueError("worker state must be a dict")
        if not isinstance(state.get("last_wake_by_message"), dict):
            state["last_wake_by_message"] = {}
        return state
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return {"last_event_id": 0, "last_wake_by_message": {}}


def _save_state(agent: str, state: dict[str, Any]) -> None:
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    _state_file(agent).write_text(json.dumps(state, indent=2), encoding="utf-8")


class _FileLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._fh = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists() or self.path.stat().st_size == 0:
            self.path.write_bytes(b"\x00")
        self._fh = open(self.path, "r+b")
        self._fh.seek(0)
        msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
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


def _find_codex_exe() -> Path:
    candidate = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "OpenAI" / "Codex" / "bin" / "codex.exe"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"Codex shim not found at {candidate}. Run scripts/install_codex_exec_shim.ps1 first."
    )


def _find_claude_exe() -> Path:
    resolved = shutil.which("claude")
    if resolved:
        return Path(resolved)
    fallback = Path.home() / ".local" / "bin" / "claude.exe"
    if fallback.exists():
        return fallback
    raise FileNotFoundError("Claude CLI not found on PATH. Install Claude Code CLI first.")


def _notification_message_ref(event: dict[str, Any]) -> str | None:
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
    refs: list[str] = []
    if not event_batch.get("notified"):
        return refs
    for event in event_batch.get("items", []):
        event_type = str(event.get("event_type") or "")
        details = event.get("details") or {}
        if event_type in DIRECT_CONTEXT_EVENT_TYPES:
            if event_type.startswith("thread.") and details.get("current_assignee") not in {None, agent}:
                continue
            if event_type == "message.invalid" and details.get("sender") != agent:
                continue
        elif event.get("agent") != agent:
            continue
        ref = _notification_message_ref(event)
        if ref:
            refs.append(ref)
    return sorted(set(refs))


def _invoke_codex(prompt: str, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    cmd = [
        str(_find_codex_exe()),
        "-a",
        "never",
        "exec",
        "-C",
        str(PROJECT_DIR),
        "--sandbox",
        "danger-full-access",
        "--json",
        "--output-last-message",
        str(_last_message_file("codex")),
        prompt,
    ]
    popen_kwargs: dict[str, object] = {
        "cwd": str(PROJECT_DIR),
        "capture_output": True,
        "text": True,
        "timeout": timeout_seconds,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    completed = subprocess.run(cmd, **popen_kwargs)
    _last_stdout_file("codex").write_text(completed.stdout or "", encoding="utf-8")
    return completed


def _invoke_prime(prompt: str, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
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
        "cwd": str(PROJECT_DIR),
        "capture_output": True,
        "text": True,
        "timeout": timeout_seconds,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    completed = subprocess.run(cmd, **popen_kwargs)
    _last_stdout_file("prime").write_text(completed.stdout or "", encoding="utf-8")
    _last_message_file("prime").write_text(completed.stdout or "", encoding="utf-8")
    return completed


def _write_health(
    agent: str,
    *,
    status: str,
    last_event_id: int,
    active_message_ids: list[str] | None = None,
    last_thread_id: str | None = None,
    dispatch_started_at: str | None = None,
    dispatch_timeout_seconds: int | None = None,
    last_error: str | None = None,
) -> None:
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
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    _health_file(agent).write_text(json.dumps(doc, indent=2), encoding="utf-8")


def resident_worker_is_healthy(
    agent: str,
    *,
    hooks_dir: Path = HOOKS_DIR,
    now: datetime | None = None,
) -> tuple[bool, str]:
    now_value = now or _now()
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
    hooks_dir: Path = HOOKS_DIR,
) -> dict[str, Any] | None:
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
    hooks_dir: Path = HOOKS_DIR,
    now: datetime | None = None,
) -> tuple[bool, str]:
    healthy, state = resident_worker_is_healthy(agent, hooks_dir=hooks_dir, now=now)
    if not healthy:
        return False, state

    if state != "busy":
        return True, state

    payload = resident_worker_health_snapshot(agent, hooks_dir=hooks_dir) or {}
    active_ids = {
        str(message_id).strip()
        for message_id in (payload.get("active_message_ids") or [])
        if str(message_id).strip()
    }
    requested_ids = {str(message_id).strip() for message_id in target_ids if str(message_id).strip()}
    if requested_ids and active_ids and requested_ids.issubset(active_ids):
        return True, "busy-same-targets"
    return False, "busy-other-targets"


def _record_dispatch(state: dict[str, Any], message_ids: list[str], trigger: str) -> None:
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


def _capture_target_state(
    bridge: Any,
    agent: str,
    target_ids: list[str],
) -> dict[str, dict[str, Any]]:
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
            "claimed_by": canonical.get("claimed_by"),
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
        _append_log(agent, f"seeded resident worker notification cursor: last_event_id={seeded}")
    return seeded


def run(args: argparse.Namespace) -> int:
    sys.path.insert(0, str(PROJECT_DIR))
    import prime_bridge_runtime as bridge

    try:
        with _FileLock(_lock_file(args.agent)):
            state = _load_state(args.agent)
            last_event_id = _seed_last_event_id(args.agent, bridge, state)
            _append_log(args.agent, f"resident worker start: last_event_id={last_event_id}")
            _save_state(args.agent, state)
            _write_health(args.agent, status="idle", last_event_id=last_event_id)
            startup_scan_pending = True
            consecutive_errors = 0  # Phase C: track repeated failures

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
                    explicit_refs = _explicit_refs_for(args.agent, event_batch)
                    new_items = bridge.list_inbox(agent=args.agent, status="new", limit=100).get("items", [])
                    claimed = bridge.list_inbox(agent=args.agent, status="claimed", limit=100).get("items", [])
                    due_claimed = [
                        item for item in claimed if claimed_item_due(args.agent, item, state, args.cadence_minutes)
                    ]
                    contexts = build_contexts(
                        bridge,
                        agent=args.agent,
                        explicit_refs=explicit_refs,
                        new_items=new_items,
                        due_claimed=due_claimed,
                        project_dir=PROJECT_DIR,
                        log_fn=lambda message: _append_log(args.agent, message),
                    )

                    batch = select_dispatch_batch(
                        contexts,
                        new_items,
                        due_claimed,
                        max_targets=args.max_dispatch_targets,
                    )
                    batch_contexts = batch["contexts"]
                    batch_new_items = batch["new_items"]
                    batch_due_claimed = batch["due_claimed"]
                    targets = batch["target_ids"]
                    deferred_targets = batch["deferred_ids"]

                    if not batch_new_items and not batch_due_claimed and not batch_contexts:
                        _save_state(args.agent, state)
                        _write_health(args.agent, status="idle", last_event_id=last_event_id)
                        continue

                    if deferred_targets:
                        _append_log(
                            args.agent,
                            f"dispatch batch capped at {args.max_dispatch_targets}; deferred_targets={','.join(deferred_targets)}",
                        )

                    payload = build_context_snapshot(
                        trigger="resident-worker",
                        contexts=batch_contexts,
                        new_items=batch_new_items,
                        due_claimed=batch_due_claimed,
                    )
                    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
                    _last_context_file(args.agent).write_text(json.dumps(payload, indent=2), encoding="utf-8")

                    prompt = build_prompt(
                        args.agent,
                        _last_context_file(args.agent),
                        batch_new_items,
                        batch_due_claimed,
                        batch_contexts,
                        project_dir=PROJECT_DIR,
                    )
                    _record_dispatch(state, targets, "resident-worker")
                    _save_state(args.agent, state)

                    dispatch_started_at = _now_iso()
                    _write_health(
                        args.agent,
                        status="busy",
                        last_event_id=last_event_id,
                        active_message_ids=targets,
                        last_thread_id=batch_contexts[0]["thread_correlation_id"] if batch_contexts else None,
                        dispatch_started_at=dispatch_started_at,
                        dispatch_timeout_seconds=args.exec_timeout_seconds,
                    )
                    _append_log(
                        args.agent,
                        f"dispatching resident worker run: targets={','.join(targets)} new={len(batch_new_items)} claimed={len(batch_due_claimed)} contexts={len(batch_contexts)}",
                    )
                    pre_dispatch_state = _capture_target_state(bridge, args.agent, targets)

                    if args.agent == "codex":
                        completed = _invoke_codex(prompt, args.exec_timeout_seconds)
                    else:
                        completed = _invoke_prime(prompt, args.exec_timeout_seconds)

                    repair_count = repair_terminal_thread_outputs(
                        bridge,
                        agent=args.agent,
                        target_refs=targets,
                        project_dir=PROJECT_DIR,
                        log_fn=lambda message: _append_log(args.agent, message),
                    )
                    post_dispatch_state = _capture_target_state(bridge, args.agent, targets)
                    made_progress = pre_dispatch_state != post_dispatch_state or repair_count > 0

                    if completed.stderr:
                        _append_log(args.agent, f"worker stderr: {completed.stderr.strip()}")
                    _append_log(args.agent, f"worker exit={completed.returncode}")
                    if completed.returncode == 0 and not made_progress:
                        _append_log(
                            args.agent,
                            f"worker made no bridge progress: targets={','.join(targets)}",
                        )
                    post_status = "running" if completed.returncode == 0 and made_progress else "idle" if completed.returncode == 0 else "error"
                    if completed.returncode == 0:
                        consecutive_errors = 0  # Phase C: reset on success
                    _write_health(
                        args.agent,
                        status=post_status,
                        last_event_id=last_event_id,
                        last_thread_id=batch_contexts[0]["thread_correlation_id"] if batch_contexts else None,
                        last_error=(
                            ((completed.stderr or "").strip() or None)
                            if completed.returncode
                            else None
                        ),
                    )
                    if completed.returncode != 0:
                        time.sleep(args.error_backoff_seconds)
                except Exception as exc:
                    consecutive_errors += 1
                    _append_log(args.agent, f"loop error ({consecutive_errors}): {exc}")
                    # Phase C: Distinguish message-level from worker-level failure.
                    # A single context/dispatch error should not permanently stop the worker.
                    if consecutive_errors >= 5:
                        _write_health(
                            args.agent,
                            status="error",
                            last_event_id=last_event_id,
                            last_error=f"repeated error ({consecutive_errors}x): {exc}",
                        )
                        # Longer backoff for repeated failures
                        time.sleep(args.error_backoff_seconds * min(consecutive_errors, 12))
                    else:
                        _write_health(
                            args.agent,
                            status="recovering",
                            last_event_id=last_event_id,
                            last_error=str(exc),
                        )
                        time.sleep(args.error_backoff_seconds)
    except OSError:
        _append_log(args.agent, "resident worker lock busy; another run is active")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Long-lived resident bridge worker")
    parser.add_argument("--agent", choices=["codex", "prime"], default="codex")
    parser.add_argument("--cadence-minutes", type=int, default=9)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--poll-interval-ms", type=int, default=100)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--max-dispatch-targets", type=int, default=DEFAULT_MAX_DISPATCH_TARGETS)
    parser.add_argument("--exec-timeout-seconds", type=int, default=900)
    parser.add_argument("--error-backoff-seconds", type=int, default=5)
    return parser


def main() -> int:
    return run(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
