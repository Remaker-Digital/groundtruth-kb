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
DISPATCH_RUNS_SUBDIR = "dispatch-runs"
DISPATCH_STATE_FILENAME = "dispatch-state.json"
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
            "document_name": getattr(item, "document_name"),
            "top_status": getattr(item, "top_status"),
            "top_file": getattr(item, "top_file"),
            "index_line_number": getattr(item, "index_line_number"),
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
            if record.harness_kind == harness_kind and Path(record.workspace_root).resolve() == project_root.resolve():
                if record.invoke_command_template:
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
    role_line = (
        "You are Codex Loyal Opposition. Process latest NEW/REVISED bridge entries."
        if recipient is BridgeAgent.CODEX
        else "You are Prime Builder. Process latest GO/NO-GO bridge entries."
    )
    rows = [
        f"- {getattr(item, 'top_status')} {getattr(item, 'document_name')} {getattr(item, 'top_file')}"
        for item in selected
    ]
    selected_text = "\n".join(rows) if rows else "- No selected entries."
    return "\n".join(
        [
            "Bridge auto-dispatch notification.",
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
    for recipient, items in pending_by_recipient.items():
        signature = _pending_signature(items)
        prior = recipients_state.get(recipient.value)
        prior_signature = prior.get("signature") if isinstance(prior, dict) else None
        recipient_state: dict[str, object] = {
            "signature": signature,
            "pending_count": len(items),
            "updated_at": now,
        }
        if not items:
            recipient_state["last_result"] = "no_pending"
            results[recipient.value] = {"launched": False, "reason": "no_pending"}
        elif prior_signature == signature:
            recipient_state["last_result"] = "unchanged"
            results[recipient.value] = {"launched": False, "reason": "unchanged"}
        else:
            launch = _launch_harness(
                state_dir=state_dir,
                project_root=project_root,
                recipient=recipient,
                items=items,
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
    main_loop(
        interval_s=args.interval,
        max_iterations=max_iterations,
        quiet=args.quiet,
        dispatch_enabled=not args.no_dispatch,
        dispatch_max_items=args.dispatch_max_items,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
