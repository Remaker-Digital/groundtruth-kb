#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Smart-poller notification-based trigger runner.

Per ``bridge/gtkb-bridge-poller-p3-notify-2026-04-29-008.md`` GO at REVISED-3,
this script runs a headless polling loop that:

1. Parses ``bridge/INDEX.md`` via P1 ``detector.parse_index``.
2. Computes per-recipient actionable pending entries via
   ``notify.compute_actionable_pending`` (current-state from top statuses).
3. Updates recipient notification files via ``notify.update_notification``
   (write or remove per file-absent semantic).
4. Writes a fresh checkpoint (audit-only) and emits an audit event.
5. Dispatches the registered AI harness when a recipient's pending-action
   signature changes after dispatch bootstrap.
6. Sleeps and repeats.

The runner is the automation path for bridge notifications: notification files
are the durable signal, and changed notification signatures launch the
recipient harness without owner intervention.

Default interval: 15 seconds (configurable via ``--interval``). Bootstrap
(first iteration on fresh state) writes no notification files; iteration 2
onwards writes notifications for all currently-actionable top statuses
(Option A; per ``-007 §1`` and the owner directive).
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

# Cross-platform exclusive file lock for single-instance runner enforcement.
# Per smart-poller-kind-aware-routing-2026-04-30-012 F1 fix: two long-running
# poller daemons sharing the same state directory race over dispatch-state.json
# and trigger spurious Prime launches via signature churn.
_USE_FCNTL = False
try:
    import fcntl

    _USE_FCNTL = True
except ImportError:
    import msvcrt

from groundtruth_kb.bridge.audit import (  # noqa: E402  - imports follow conditional fcntl/msvcrt block above
    emit_audit_event,
)
from groundtruth_kb.bridge.checkpoint import (  # noqa: E402
    diff_against_checkpoint,
    load_checkpoint,
    write_checkpoint,
)
from groundtruth_kb.bridge.detector import parse_index  # noqa: E402
from groundtruth_kb.bridge.notify import (  # noqa: E402
    _kind_aware_routing_enabled,
    compute_actionable_pending,
    update_notification,
)
from groundtruth_kb.bridge.paths import get_state_dir, resolve_project_root  # noqa: E402
from groundtruth_kb.bridge.routing import BridgeAgent  # noqa: E402

DEFAULT_INTERVAL_S = 15
POLLER_RUNS_SUBDIR = "poller-runs"
DISPATCH_RUNS_SUBDIR = "dispatch-runs"
DISPATCH_STATE_FILENAME = "dispatch-state.json"
INDEX_RELATIVE_PATH = ("bridge", "INDEX.md")

# Single-instance enforcement lock file (per smart-poller-kind-aware-routing
# -2026-04-30-012 F1 fix). Lives in the state directory; held for the lifetime
# of one main_loop call.
RUNNER_LOCK_FILENAME = "bridge-poller-runner.lock"

# Exit code when another runner already holds the lock. Distinct from 0 so
# scheduled-task health checks can detect the duplicate-instance case.
EXIT_CODE_ALREADY_RUNNING = 75


class RunnerAlreadyRunningError(RuntimeError):
    """Raised when another bridge_poller_runner.py instance holds the runner lock.

    Per smart-poller-kind-aware-routing-2026-04-30-012 F1 fix: prevents two
    long-running daemons from racing over dispatch-state.json.
    """


def _acquire_runner_lock(state_dir: Path) -> int:
    """Acquire exclusive non-blocking lock on the runner-instance lock file.

    Returns the file descriptor on success (caller releases via
    `_release_runner_lock`). Raises ``RunnerAlreadyRunningError`` if another
    runner instance currently holds the lock.

    The lock file is `<state_dir>/bridge-poller-runner.lock`. fcntl.flock on
    POSIX, msvcrt.locking on Windows. Non-blocking — fails immediately rather
    than queueing — so a duplicate launch is loud, not silent.
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = state_dir / RUNNER_LOCK_FILENAME
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        # Ensure file has at least 1 byte for msvcrt byte-range lock.
        if os.fstat(fd).st_size == 0:
            os.write(fd, b"\0")
            os.lseek(fd, 0, 0)
        if _USE_FCNTL:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                os.close(fd)
                raise RunnerAlreadyRunningError(
                    f"Another bridge_poller_runner is already running (lock held at {lock_path})"
                ) from exc
        else:
            os.lseek(fd, 0, 0)
            try:
                # LK_NBLCK: non-blocking exclusive lock
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                os.close(fd)
                raise RunnerAlreadyRunningError(
                    f"Another bridge_poller_runner is already running (lock held at {lock_path})"
                ) from exc
        # Write our PID to the lock file for diagnostics. Truncate first so
        # we don't leave stale PID bytes from a prior holder past the new PID.
        os.lseek(fd, 0, 0)
        # Some platforms restrict ftruncate on locked fd; ignore.
        with contextlib.suppress(OSError):
            os.ftruncate(fd, 0)
        os.write(fd, f"{os.getpid()}\n".encode("ascii"))
        return fd
    except RunnerAlreadyRunningError:
        raise
    except Exception:
        with contextlib.suppress(OSError):
            os.close(fd)
        raise


def _release_runner_lock(fd: int) -> None:
    """Release and close the runner instance lock fd. Idempotent on errors."""
    if _USE_FCNTL:
        with contextlib.suppress(OSError):
            fcntl.flock(fd, fcntl.LOCK_UN)
    else:
        with contextlib.suppress(OSError):
            os.lseek(fd, 0, 0)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    with contextlib.suppress(OSError):
        os.close(fd)


# Module-level shutdown flag toggled by SIGINT/SIGTERM handlers.
_shutdown_requested = False


def _request_shutdown(*_args: object) -> None:
    global _shutdown_requested
    _shutdown_requested = True


def _install_signal_handlers() -> None:
    signal.signal(signal.SIGINT, _request_shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _request_shutdown)


def _make_run_id() -> str:
    ts = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    return f"{ts}-{uuid.uuid4().hex[:6]}"


def _log_iteration(state_dir: Path, run_id: str, payload: dict[str, object]) -> None:
    log_dir = state_dir / POLLER_RUNS_SUBDIR
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{run_id}.jsonl"
    line = json.dumps(
        {**payload, "ts": dt.datetime.now(dt.UTC).isoformat(timespec="seconds")},
        ensure_ascii=False,
    )
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _dispatch_state_path(state_dir: Path) -> Path:
    return state_dir / DISPATCH_STATE_FILENAME


def _load_dispatch_state(state_dir: Path) -> dict[str, object]:
    path = _dispatch_state_path(state_dir)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _write_dispatch_state(state_dir: Path, payload: dict[str, object]) -> None:
    target = _dispatch_state_path(state_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(target)


def _pending_signature(items: list[object]) -> str:
    normalized = [
        {
            "document_name": item.document_name,
            "top_status": item.top_status,
            "top_file": item.top_file,
        }
        for item in items
    ]
    raw = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _recipient_harness_kind(recipient: BridgeAgent) -> str:
    if recipient is BridgeAgent.CODEX:
        return "codex"
    return "claude-code"


def _default_invoke_template(harness_kind: str) -> tuple[str, ...]:
    if harness_kind == "codex":
        return ("codex", "exec", "{prompt}", "--cd", "{workspace_root}")
    if harness_kind == "claude-code":
        return ("claude", "-p", "{prompt}", "--add-dir", "{workspace_root}", "--output-format", "json")
    return ()


def _latest_template_for(harness_kind: str, project_root: Path) -> tuple[str, ...]:
    try:
        from groundtruth_kb.bridge.registry import list_all_registrations

        for record in list_all_registrations(since_days=7):
            if (
                record.harness_kind == harness_kind
                and Path(record.workspace_root).resolve() == project_root.resolve()
                and record.invoke_command_template
            ):
                return record.invoke_command_template
    except Exception:
        pass
    return _default_invoke_template(harness_kind)


def _format_command(template: tuple[str, ...], *, prompt: str, project_root: Path) -> list[str]:
    return [part.format(prompt=prompt, workspace_root=str(project_root)) for part in template]


def _selected_items_for_prompt(items: list[object], max_items: int) -> list[object]:
    # INDEX is newest-first. Bridge work should be processed oldest-first.
    if max_items <= 0:
        return []
    return list(reversed(items))[:max_items]


def _dispatch_prompt(recipient: BridgeAgent, items: list[object], *, max_items: int) -> str:
    selected = _selected_items_for_prompt(items, max_items)
    # Per DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001.A1: defer to the
    # durable role record rather than hard-coding role assertions in the
    # dispatch prompt. Per DCL-SMART-POLLER-AUTO-TRIGGER-001 + the existing
    # ACTIONABLE_STATUSES_FOR_PRIME = {GO, NO-GO} contract in notify.py:
    # VERIFIED is bridge closure for both roles and is not queue work.
    role_line = (
        "Read your durable role from `.claude/rules/operating-role.md` "
        "(or the harness-local override at `harness-state/{harness}/operating-role.md` "
        "if present, which takes precedence per `.claude/rules/operating-role.md`). "
        "Process the bridge entries selected below according to your declared role: "
        "Loyal Opposition reviews latest NEW or REVISED entries; "
        "Prime Builder acts on latest GO or NO-GO entries assigned to its harness. "
        "Latest VERIFIED entries are bridge closure for both roles and are not "
        "queue work; do not process them as actionable."
    )
    rows = [f"- {item.top_status} {item.document_name} {item.top_file}" for item in selected]
    selected_text = "\n".join(rows) if rows else "- No selected entries."
    return "\n".join(
        [
            "Bridge auto-dispatch notification.",
            "",
            (
                "This is an automated bridge dispatch, not a fresh-session owner stimulus; "
                "do not wait for another owner message before processing the selected entries."
            ),
            "",
            role_line,
            "Read bridge/INDEX.md directly before acting. Treat the live latest status as authoritative.",
            "If any listed entry is no longer actionable for your role, do not act on that stale entry.",
            "Keep work scoped to the selected bridge entries and preserve the bridge protocol audit trail.",
            "",
            f"Selected entries, oldest-first, capped at {max_items}:",
            selected_text,
        ]
    )


def _launch_harness(
    *,
    state_dir: Path,
    project_root: Path,
    recipient: BridgeAgent,
    items: list[object],
    poller_run_id: str,
    max_items: int,
) -> dict[str, object]:
    harness_kind = _recipient_harness_kind(recipient)
    template = _latest_template_for(harness_kind, project_root)
    if not template:
        return {
            "recipient": recipient.value,
            "harness_kind": harness_kind,
            "launched": False,
            "reason": "no_invoke_template",
        }

    prompt = _dispatch_prompt(recipient, items, max_items=max_items)
    command = _format_command(template, prompt=prompt, project_root=project_root)
    dispatch_dir = state_dir / DISPATCH_RUNS_SUBDIR
    dispatch_dir.mkdir(parents=True, exist_ok=True)
    dispatch_id = f"{dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H-%M-%SZ')}-{recipient.value}-{uuid.uuid4().hex[:6]}"
    stdout_path = dispatch_dir / f"{dispatch_id}.stdout.log"
    stderr_path = dispatch_dir / f"{dispatch_id}.stderr.log"
    meta_path = dispatch_dir / f"{dispatch_id}.json"
    env = dict(os.environ)
    env["GTKB_PROJECT_ROOT"] = str(project_root)
    env["GTKB_BRIDGE_POLLER_RUN_ID"] = poller_run_id
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    meta: dict[str, object] = {
        "dispatch_id": dispatch_id,
        "recipient": recipient.value,
        "harness_kind": harness_kind,
        "poller_run_id": poller_run_id,
        "selected_count": len(_selected_items_for_prompt(items, max_items)),
        "pending_count": len(items),
        "launched_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "command_head": command[:2],
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }
    try:
        stdout = stdout_path.open("w", encoding="utf-8")
        stderr = stderr_path.open("w", encoding="utf-8")
        try:
            process = subprocess.Popen(
                command,
                cwd=str(project_root),
                env=env,
                stdout=stdout,
                stderr=stderr,
                text=True,
                creationflags=creationflags,
            )
        finally:
            stdout.close()
            stderr.close()
        meta.update({"launched": True, "pid": process.pid})
    except Exception as exc:
        meta.update(
            {
                "launched": False,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
        )
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
    return meta


def _dispatch_if_needed(
    *,
    state_dir: Path,
    project_root: Path,
    run_id: str,
    pending_by_recipient: dict[BridgeAgent, list[object]],
    max_items: int,
) -> dict[str, object]:
    state = _load_dispatch_state(state_dir)
    recipients_state = state.get("recipients")
    if not isinstance(recipients_state, dict):
        recipients_state = {}

    now = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
    results: dict[str, object] = {}
    kind_aware = _kind_aware_routing_enabled()
    for recipient, items in pending_by_recipient.items():
        # Per smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4 §1.5:
        # filter items on dispatchable BEFORE signature check + spawn so terminal-
        # kind GO verdicts don't spawn redundant Prime harnesses. Feature flag
        # GTKB_NOTIFY_KIND_AWARE_ROUTING (default 1) gates the filter.
        filtered_items = [it for it in items if getattr(it, "dispatchable", True)] if kind_aware else list(items)
        filtered_terminal_count = len(items) - len(filtered_items)

        selected_items = _selected_items_for_prompt(filtered_items, max_items)
        signature = _pending_signature(selected_items)
        prior = recipients_state.get(recipient.value)
        prior_signature = prior.get("signature") if isinstance(prior, dict) else None
        recipient_state: dict[str, object] = {
            "signature": signature,
            "signature_scope": "selected_dispatch_batch",
            "pending_count": len(filtered_items),
            "raw_pending_count": len(items),
            "selected_count": len(selected_items),
            "filtered_terminal_count": filtered_terminal_count,
            "updated_at": now,
        }
        if not filtered_items:
            # Distinguish "raw list was empty" from "filter removed everything".
            # The latter records the cumulative-token-cost reduction in the audit.
            reason = "no_pending_after_filter" if items else "no_pending"
            recipient_state["last_result"] = reason
            results[recipient.value] = {
                "launched": False,
                "reason": reason,
                "filtered_terminal_count": filtered_terminal_count,
            }
        elif prior_signature == signature:
            recipient_state["last_result"] = "unchanged"
            results[recipient.value] = {"launched": False, "reason": "unchanged"}
        else:
            launch = _launch_harness(
                state_dir=state_dir,
                project_root=project_root,
                recipient=recipient,
                items=filtered_items,
                poller_run_id=run_id,
                max_items=max_items,
            )
            recipient_state["last_result"] = "launched" if launch.get("launched") else "launch_failed"
            recipient_state["last_launch"] = launch
            results[recipient.value] = launch
        recipients_state[recipient.value] = recipient_state

    _write_dispatch_state(
        state_dir,
        {
            "schema_version": 1,
            "updated_at": now,
            "recipients": recipients_state,
        },
    )
    return results


def run_one_iteration(
    *,
    state_dir: Path,
    project_root: Path,
    run_id: str,
    iteration: int,
    dispatch_enabled: bool = False,
    dispatch_max_items: int = 2,
) -> dict[str, object]:
    """Run one polling iteration. Returns a payload describing the iteration outcome."""
    index_path = project_root.joinpath(*INDEX_RELATIVE_PATH)
    index_text = index_path.read_text(encoding="utf-8")
    parse_result = parse_index(index_text, project_root=project_root)
    cp_load = load_checkpoint(state_dir)

    if cp_load.is_bootstrap:
        # Bootstrap: write checkpoint, emit audit, write NO notification files.
        write_checkpoint(state_dir, parse_result.documents)
        emit_audit_event(
            state_dir,
            "bootstrap",
            {
                "run_id": run_id,
                "iteration": iteration,
                "documents_seen": len(parse_result.documents),
                "transitions_routable": 0,
                "corrupt_checkpoint_recovered": cp_load.corrupt_checkpoint_recovered,
            },
        )
        return {
            "kind": "bootstrap",
            "run_id": run_id,
            "iteration": iteration,
            "documents_seen": len(parse_result.documents),
            "actionable_prime_count": 0,
            "actionable_codex_count": 0,
        }

    # Post-bootstrap: compute current-state notifications + audit transitions.
    actionable_for_prime, actionable_for_codex = compute_actionable_pending(parse_result, project_root=project_root)
    update_notification(state_dir, BridgeAgent.PRIME, actionable_for_prime, poller_run_id=run_id)
    update_notification(state_dir, BridgeAgent.CODEX, actionable_for_codex, poller_run_id=run_id)
    dispatch_results: dict[str, object] = {}
    if dispatch_enabled:
        dispatch_results = _dispatch_if_needed(
            state_dir=state_dir,
            project_root=project_root,
            run_id=run_id,
            pending_by_recipient={
                BridgeAgent.PRIME: list(actionable_for_prime),
                BridgeAgent.CODEX: list(actionable_for_codex),
            },
            max_items=dispatch_max_items,
        )

    # Audit-only transition diff (per -005 §1.2 / -007 §3 preserved contract):
    # observability for "what changed since last scan" without affecting
    # notification contents (which remain current-state via compute_actionable_pending).
    transitions = diff_against_checkpoint(parse_result.documents, cp_load.checkpoint, is_bootstrap=False)
    write_checkpoint(state_dir, parse_result.documents)
    emit_audit_event(
        state_dir,
        "scan",
        {
            "run_id": run_id,
            "iteration": iteration,
            "documents_seen": len(parse_result.documents),
            "transitions_count": len(transitions),
            "actionable_prime_count": len(actionable_for_prime),
            "actionable_codex_count": len(actionable_for_codex),
            "dispatch_results": dispatch_results,
        },
    )
    return {
        "kind": "scan",
        "run_id": run_id,
        "iteration": iteration,
        "documents_seen": len(parse_result.documents),
        "transitions_count": len(transitions),
        "actionable_prime_count": len(actionable_for_prime),
        "actionable_codex_count": len(actionable_for_codex),
        "dispatch_results": dispatch_results,
    }


def main_loop(
    *,
    interval_s: int = DEFAULT_INTERVAL_S,
    max_iterations: int | None = None,
    quiet: bool = False,
    state_dir: Path | None = None,
    project_root: Path | None = None,
    dispatch_enabled: bool = False,
    dispatch_max_items: int = 2,
) -> int:
    """Run the polling loop until ``max_iterations`` or SIGINT/SIGTERM.

    Returns the iteration count actually completed (useful for tests). Raises
    ``RunnerAlreadyRunningError`` if another runner instance currently holds
    the single-instance lock at ``<state_dir>/bridge-poller-runner.lock`` (per
    smart-poller-kind-aware-routing-2026-04-30-012 F1 fix).
    """
    global _shutdown_requested
    _shutdown_requested = False
    _install_signal_handlers()

    resolved_state = state_dir if state_dir is not None else get_state_dir()
    resolved_root = project_root if project_root is not None else resolve_project_root()

    # Single-instance enforcement: acquire the runner lock before any state
    # mutation. Duplicate daemons would otherwise race over dispatch-state.json.
    lock_fd = _acquire_runner_lock(resolved_state)

    run_id = _make_run_id()
    iteration = 0

    try:
        while not _shutdown_requested:
            if max_iterations is not None and iteration >= max_iterations:
                break
            try:
                payload = run_one_iteration(
                    state_dir=resolved_state,
                    project_root=resolved_root,
                    run_id=run_id,
                    iteration=iteration,
                    dispatch_enabled=dispatch_enabled,
                    dispatch_max_items=dispatch_max_items,
                )
                _log_iteration(resolved_state, run_id, payload)
                if not quiet:
                    sys.stdout.write(json.dumps(payload) + "\n")
                    sys.stdout.flush()
            except Exception as exc:
                err_payload: dict[str, object] = {
                    "kind": "error",
                    "run_id": run_id,
                    "iteration": iteration,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
                _log_iteration(resolved_state, run_id, err_payload)
                if not quiet:
                    sys.stderr.write(json.dumps(err_payload) + "\n")
                    sys.stderr.flush()
            iteration += 1
            if max_iterations is None or iteration < max_iterations:
                if _shutdown_requested:
                    break
                # Sleep responsively to SIGINT.
                slept = 0.0
                while slept < interval_s and not _shutdown_requested:
                    step = min(0.5, interval_s - slept)
                    time.sleep(step)
                    slept += step

        _log_iteration(
            resolved_state,
            run_id,
            {
                "kind": "shutdown",
                "run_id": run_id,
                "completed_iterations": iteration,
                "shutdown_via_signal": _shutdown_requested,
            },
        )
        return iteration
    finally:
        _release_runner_lock(lock_fd)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bridge_poller_runner.py",
        description="Smart-poller notification-based trigger (no spawning).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL_S,
        help=f"Seconds between polling iterations (default {DEFAULT_INTERVAL_S}).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single iteration and exit. Equivalent to --max-iterations 1.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Optional cap on iteration count (for testing or scripted invocations).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress stdout/stderr output (audit log still written).",
    )
    parser.add_argument(
        "--no-dispatch",
        action="store_true",
        help="Write notifications but do not launch AI harnesses.",
    )
    parser.add_argument(
        "--enable-dispatch",
        action="store_true",
        help=(
            "Override the verification-safe default for --once. By default, "
            "--once disables dispatch so notification-state checks don't launch "
            "real harnesses. Pass --once --enable-dispatch to dispatch in one-shot mode. "
            "Per smart-poller-kind-aware-routing-2026-04-30-012 F2 fix."
        ),
    )
    parser.add_argument(
        "--dispatch-max-items",
        type=int,
        default=2,
        help="Maximum selected bridge entries to pass to one automatic harness dispatch (default 2).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    max_iterations = args.max_iterations
    if args.once:
        max_iterations = 1

    # Per smart-poller-kind-aware-routing-2026-04-30-012 F2 fix:
    # --once defaults to verification-safe (no dispatch). Continuous mode
    # keeps the historical default of dispatch enabled unless --no-dispatch.
    dispatch_enabled = (args.enable_dispatch and not args.no_dispatch) if args.once else (not args.no_dispatch)

    try:
        main_loop(
            interval_s=args.interval,
            max_iterations=max_iterations,
            quiet=args.quiet,
            dispatch_enabled=dispatch_enabled,
            dispatch_max_items=args.dispatch_max_items,
        )
    except RunnerAlreadyRunningError as exc:
        # Single-instance enforcement: another daemon already holds the lock.
        # Per smart-poller-kind-aware-routing-2026-04-30-012 F1 fix.
        if not args.quiet:
            sys.stderr.write(f"{exc}\n")
            sys.stderr.flush()
        return EXIT_CODE_ALREADY_RUNNING
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
