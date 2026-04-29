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
5. Sleeps and repeats.

The runner does NOT spawn agent sessions. The notification artifacts are
read by existing agent sessions (Claude Code or Codex) via their hooks.

Default interval: 15 seconds (configurable via ``--interval``). Bootstrap
(first iteration on fresh state) writes no notification files; iteration 2
onwards writes notifications for all currently-actionable top statuses
(Option A; per ``-007 §1`` and the owner directive).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import signal
import sys
import time
import uuid
from pathlib import Path

from groundtruth_kb.bridge.audit import emit_audit_event
from groundtruth_kb.bridge.checkpoint import (
    diff_against_checkpoint,
    load_checkpoint,
    write_checkpoint,
)
from groundtruth_kb.bridge.detector import parse_index
from groundtruth_kb.bridge.notify import (
    compute_actionable_pending,
    update_notification,
)
from groundtruth_kb.bridge.paths import get_state_dir, resolve_project_root
from groundtruth_kb.bridge.routing import BridgeAgent

DEFAULT_INTERVAL_S = 15
POLLER_RUNS_SUBDIR = "poller-runs"
INDEX_RELATIVE_PATH = ("bridge", "INDEX.md")


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


def run_one_iteration(
    *,
    state_dir: Path,
    project_root: Path,
    run_id: str,
    iteration: int,
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
    }


def main_loop(
    *,
    interval_s: int = DEFAULT_INTERVAL_S,
    max_iterations: int | None = None,
    quiet: bool = False,
    state_dir: Path | None = None,
    project_root: Path | None = None,
) -> int:
    """Run the polling loop until ``max_iterations`` or SIGINT/SIGTERM.

    Returns the iteration count actually completed (useful for tests).
    """
    global _shutdown_requested
    _shutdown_requested = False
    _install_signal_handlers()

    resolved_state = state_dir if state_dir is not None else get_state_dir()
    resolved_root = project_root if project_root is not None else resolve_project_root()
    run_id = _make_run_id()
    iteration = 0

    while not _shutdown_requested:
        if max_iterations is not None and iteration >= max_iterations:
            break
        try:
            payload = run_one_iteration(
                state_dir=resolved_state,
                project_root=resolved_root,
                run_id=run_id,
                iteration=iteration,
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    max_iterations = args.max_iterations
    if args.once:
        max_iterations = 1
    main_loop(
        interval_s=args.interval,
        max_iterations=max_iterations,
        quiet=args.quiet,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
