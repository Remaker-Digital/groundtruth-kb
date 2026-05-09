#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Cross-harness bridge trigger — event-driven replacement for the smart-poller.

Per ``bridge/gtkb-bridge-poller-event-driven-replacement-003.md`` GO at
``-004`` (Slice 2):

This script is the harness-agnostic detection + dispatch surface invoked by
PostToolUse / Stop hooks on either Claude Code or Codex. It re-reads the
**live** ``bridge/INDEX.md`` (working-tree state, NOT committed state) every
time it fires, computes a per-recipient actionable signature mirroring the
smart-poller's ``_pending_signature`` scheme, compares against the durable
dispatch-state, and dispatches the recipient harness only when its signature
changed.

Design contract:

- INDEX-as-canonical-state per ``.claude/rules/file-bridge-protocol.md`` is
  preserved. The trigger event is a tool-use hook; the dispatch predicate is
  live-INDEX-signature-changed (NOT commit-history-based — addresses Codex
  F1 finding on REVISED-1).
- Signature normalization: ``[{document_name, top_status, top_file}]`` per
  recipient, JSON sorted, SHA-256 hex. Byte-identical to
  ``groundtruth-kb/scripts/bridge_poller_runner.py::_pending_signature`` so
  Slice 4 (smart-poller retirement) does not require a signature reset.
- Loop prevention: durable per-recipient signature state in
  ``<state-dir>/dispatch-state.json``. When the dispatched harness's tool-use
  fires the trigger, the signature matches the just-written value and the
  dispatch path returns "unchanged" without spawning. Reciprocal dispatch
  (Codex's GO write produces a NEW Prime-actionable signature) flows
  naturally because the new signature differs from the prior recorded value.
  The ``GTKB_NO_CROSS_HARNESS_TRIGGER=1`` env var is a manual operator
  opt-out (debugging, emergency stop, test harness) — NOT propagated to
  child harness env per Codex F2 on ``-008`` to avoid suppressing legitimate
  reciprocal dispatch.
- Fire-and-forget: hook scripts must not stall tool use. This script always
  exits 0. Dispatch failures are appended to
  ``<state-dir>/dispatch-failures.jsonl`` for diagnosis.
- Path: defaults to ``<project_root>/.gtkb-state/cross-harness-trigger/``;
  Slice 4 may decide to repurpose the smart-poller's existing state path
  instead. Path is parameterized via ``--state-dir`` flag for tests.

Slice 2 status: NON-LIVE. Tests exercise the script directly. Hook
registrations land in Slice 3 (gated on Slice 1 VERIFIED).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

# Manual-disable env var. When set to "1", this script no-ops immediately.
# Used as an OPERATOR opt-out (debugging, emergency stop, test harness),
# NOT as automatic loop prevention.
#
# Per Codex F2 on -008: this env var is NOT propagated to the dispatched
# harness's child process. Setting it on the child would suppress
# legitimate reciprocal dispatch — example: Claude writes NEW; trigger
# dispatches Codex with env var=1; Codex writes GO; Codex's own hooks
# would skip dispatching Prime back, stalling the round-trip.
#
# The actual loop-prevention mechanism is the durable per-recipient
# signature in ``.gtkb-state/cross-harness-trigger/dispatch-state.json``:
# when the dispatched harness's tool-use fires the trigger, the signature
# matches the just-written value and the dispatch path returns "unchanged"
# without spawning. Reciprocal dispatch (Codex GO writes a NEW
# Prime-actionable signature) flows through naturally because the new
# signature differs from the prior recorded value.
LOOP_PREVENTION_ENV_VAR = "GTKB_NO_CROSS_HARNESS_TRIGGER"

# Canonical default state path. Slice 4 may decide to reuse the smart-poller
# state path instead; path is parameterized so tests don't encode it.
DEFAULT_STATE_SUBDIR = (".gtkb-state", "cross-harness-trigger")
DISPATCH_STATE_FILENAME = "dispatch-state.json"
DISPATCH_FAILURES_FILENAME = "dispatch-failures.jsonl"
DISPATCH_RUNS_SUBDIR = "dispatch-runs"

# Selected-batch cap mirrors the smart-poller's default per
# ``groundtruth-kb/scripts/bridge_poller_runner.py:670-673``. Bumping this
# requires a separate bridge proposal — Codex F1 on
# ``-008`` flagged unilateral cap changes as scope creep.
DEFAULT_MAX_ITEMS = 2


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def _resolve_project_root(explicit: Path | None) -> Path:
    """Resolve the GT-KB project root.

    Order:
      1. Explicit ``--project-root`` flag (test affordance).
      2. Lazy import of ``groundtruth_kb.bridge.paths.resolve_project_root``.
      3. ``GTKB_PROJECT_ROOT`` env var direct read (fallback when the package
         is not importable from the hook environment).

    Fail-closed: returns a directory containing ``groundtruth.toml``.
    """
    if explicit is not None:
        candidate = explicit.resolve()
        if not (candidate / "groundtruth.toml").is_file():
            raise SystemExit(f"--project-root {candidate} lacks groundtruth.toml")
        return candidate

    try:
        from groundtruth_kb.bridge.paths import resolve_project_root  # type: ignore

        return resolve_project_root()
    except Exception:
        pass

    env_root = os.environ.get("GTKB_PROJECT_ROOT")
    if env_root:
        candidate = Path(env_root).resolve()
        if (candidate / "groundtruth.toml").is_file():
            return candidate

    raise SystemExit(
        "Could not resolve GT-KB project root. Pass --project-root or set "
        "GTKB_PROJECT_ROOT to a path containing groundtruth.toml."
    )


def _signature(items: list[Any]) -> str:
    """Compute the per-recipient actionable signature.

    Byte-identical to ``bridge_poller_runner._pending_signature``: only
    ``document_name``, ``top_status``, ``top_file`` participate; sorted JSON;
    SHA-256 hex.
    """
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


def _load_dispatch_state(state_dir: Path) -> dict[str, Any]:
    target = state_dir / DISPATCH_STATE_FILENAME
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _write_dispatch_state(state_dir: Path, payload: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    target = state_dir / DISPATCH_STATE_FILENAME
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(target)


def _record_dispatch_failure(state_dir: Path, payload: dict[str, Any]) -> None:
    """Append a fire-and-forget failure record to the JSONL diagnosis log."""
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        target = state_dir / DISPATCH_FAILURES_FILENAME
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
    except OSError:
        pass


def _read_index_live(project_root: Path) -> str:
    """Read the live (working-tree) bridge/INDEX.md content.

    Per Codex F1 on REVISED-1: dispatch predicate is live INDEX, not committed
    INDEX. An uncommitted INDEX edit must be visible here.
    """
    index_path = project_root / "bridge" / "INDEX.md"
    if not index_path.is_file():
        return ""
    return index_path.read_text(encoding="utf-8")


def _compute_actionable(
    index_text: str,
    project_root: Path,
) -> tuple[list[Any], list[Any]]:
    """Parse INDEX and return (actionable_for_prime, actionable_for_codex).

    Lazy-imports the canonical detector + notify modules. Tests exercise this
    via synthetic in-root projects and a real on-disk INDEX.
    """
    from groundtruth_kb.bridge.detector import parse_index  # type: ignore
    from groundtruth_kb.bridge.notify import compute_actionable_pending  # type: ignore

    parse_result = parse_index(index_text, project_root=project_root)
    return compute_actionable_pending(parse_result, project_root=project_root)


def _selected_oldest_first(items: list[Any], max_items: int) -> list[Any]:
    """INDEX is newest-first; bridge work is processed oldest-first."""
    if max_items <= 0:
        return []
    return list(reversed(items))[:max_items]


def _dispatch_prompt(recipient: str, items: list[Any], max_items: int) -> str:
    """Build the dispatch prompt mirroring the smart-poller phrasing.

    Equivalent to ``bridge_poller_runner._dispatch_prompt`` so the dispatched
    harness's behavior is unchanged when the trigger mechanism swaps from
    timer-driven to event-driven.
    """
    selected = _selected_oldest_first(items, max_items)
    rows = [f"- {item.top_status} {item.document_name} {item.top_file}" for item in selected]
    selected_text = "\n".join(rows) if rows else "- No selected entries."
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
    return "\n".join(
        [
            "Bridge auto-dispatch notification (cross-harness trigger).",
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


def _harness_command(recipient: str, prompt: str, project_root: Path) -> list[str] | None:
    """Build the recipient harness invocation command.

    - codex   → ``codex exec <prompt> --cd <root>``
    - prime   → ``claude -p <prompt> --add-dir <root> --output-format json``
    - other   → None (unknown recipient)
    """
    if recipient == "codex":
        return ["codex", "exec", prompt, "--cd", str(project_root)]
    if recipient == "prime":
        return [
            "claude",
            "-p",
            prompt,
            "--add-dir",
            str(project_root),
            "--output-format",
            "json",
        ]
    return None


def _spawn_harness(
    *,
    recipient: str,
    items: list[Any],
    project_root: Path,
    state_dir: Path,
    max_items: int,
    dry_run: bool,
) -> dict[str, Any]:
    """Fire-and-forget dispatch a harness subprocess.

    Per Codex F2 on ``-008``: does NOT set ``GTKB_NO_CROSS_HARNESS_TRIGGER``
    on the child env (and explicitly strips it via ``env.pop`` so a parent's
    setting cannot leak). Loop prevention lives in the durable signature-state
    file: when the dispatched harness's tool-use fires the trigger, the
    signature is unchanged and no spawn happens. Reciprocal dispatch
    (counterpart-actionable signature flip after the dispatched harness writes
    its bridge response) flows naturally.

    Sets ``GTKB_PROJECT_ROOT`` on the child env so the dispatched harness
    resolves the same project root.

    Failures (subprocess error, missing executable, etc.) are recorded to
    ``dispatch-failures.jsonl`` and reported in the return meta. The caller
    treats failure as non-fatal per the fire-and-forget contract.
    """
    prompt = _dispatch_prompt(recipient, items, max_items)
    command = _harness_command(recipient, prompt, project_root)
    dispatch_id = (
        f"{dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H-%M-%SZ')}"
        f"-{recipient}-{uuid.uuid4().hex[:6]}"
    )

    if command is None:
        meta = {
            "dispatch_id": dispatch_id,
            "recipient": recipient,
            "launched": False,
            "reason": "unknown_recipient",
        }
        _record_dispatch_failure(state_dir, meta)
        return meta

    if dry_run:
        return {
            "dispatch_id": dispatch_id,
            "recipient": recipient,
            "launched": False,
            "reason": "dry_run",
            "command_head": command[:2],
        }

    runs_dir = state_dir / DISPATCH_RUNS_SUBDIR
    runs_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = runs_dir / f"{dispatch_id}.stdout.log"
    stderr_path = runs_dir / f"{dispatch_id}.stderr.log"

    env = dict(os.environ)
    env["GTKB_PROJECT_ROOT"] = str(project_root)
    # Per Codex F2 on -008: do NOT set GTKB_NO_CROSS_HARNESS_TRIGGER on the
    # child harness env. The signature-state file provides loop prevention
    # (unchanged signature → no spawn); blanket env var would also suppress
    # the legitimate reciprocal dispatch when the dispatched harness writes
    # a new bridge response that flips the counterpart's signature.
    # Explicitly strip in case the parent has it set:
    env.pop(LOOP_PREVENTION_ENV_VAR, None)
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    meta: dict[str, Any] = {
        "dispatch_id": dispatch_id,
        "recipient": recipient,
        "launched_at": _now_iso(),
        "command_head": command[:2],
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }
    try:
        with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open(
            "w", encoding="utf-8"
        ) as err:
            process = subprocess.Popen(
                command,
                cwd=str(project_root),
                env=env,
                stdout=out,
                stderr=err,
                text=True,
                creationflags=creationflags,
            )
        meta.update({"launched": True, "pid": process.pid})
    except (OSError, FileNotFoundError, subprocess.SubprocessError) as exc:
        meta.update(
            {
                "launched": False,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
        )
        _record_dispatch_failure(state_dir, meta)
    return meta


def run_trigger(
    *,
    project_root: Path,
    state_dir: Path,
    max_items: int = DEFAULT_MAX_ITEMS,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run one detection + dispatch cycle.

    Returns a summary dict. Always succeeds (fire-and-forget); errors during
    dispatch are surfaced via the per-recipient ``last_result`` field but the
    function returns normally.
    """
    if os.environ.get(LOOP_PREVENTION_ENV_VAR) == "1":
        return {"skipped": True, "reason": "loop_prevention_env_var"}

    index_text = _read_index_live(project_root)
    actionable_for_prime, actionable_for_codex = _compute_actionable(
        index_text, project_root
    )

    state = _load_dispatch_state(state_dir)
    recipients_state = state.get("recipients") if isinstance(state, dict) else {}
    if not isinstance(recipients_state, dict):
        recipients_state = {}

    pending_by_recipient = {
        "prime": actionable_for_prime,
        "codex": actionable_for_codex,
    }

    results: dict[str, Any] = {}
    for recipient, items in pending_by_recipient.items():
        # Filter by dispatchable per smart-poller-kind-aware-routing -009 §1.5.
        # Terminal-kind GO entries are not dispatched.
        filtered = [it for it in items if getattr(it, "dispatchable", True)]

        # Per Codex F1 on -008: sign the SELECTED dispatch batch (post-cap,
        # post-reverse-for-oldest-first), NOT the full filtered list. This
        # matches ``bridge_poller_runner._pending_signature(_selected_items_
        # for_prompt(filtered, max_items))`` byte-for-byte. Signing the full
        # list would let entries outside the cap flip the signature without
        # changing the dispatch payload, causing redundant dispatches.
        selected = _selected_oldest_first(filtered, max_items)
        signature = _signature(selected)

        prior = recipients_state.get(recipient)
        prior_signature = prior.get("signature") if isinstance(prior, dict) else None

        recipient_state: dict[str, Any] = {
            "signature": signature,
            "signature_scope": "selected_dispatch_batch",
            "pending_count": len(filtered),
            "selected_count": len(selected),
            "raw_pending_count": len(items),
            "updated_at": _now_iso(),
        }

        if not selected:
            recipient_state["last_result"] = (
                "no_pending_after_filter" if items else "no_pending"
            )
            results[recipient] = {"launched": False, "reason": recipient_state["last_result"]}
        elif prior_signature == signature:
            recipient_state["last_result"] = "unchanged"
            results[recipient] = {"launched": False, "reason": "unchanged"}
        else:
            launch = _spawn_harness(
                recipient=recipient,
                items=filtered,
                project_root=project_root,
                state_dir=state_dir,
                max_items=max_items,
                dry_run=dry_run,
            )
            recipient_state["last_result"] = (
                "launched" if launch.get("launched") else "launch_failed"
            )
            recipient_state["last_launch"] = launch
            results[recipient] = launch

        recipients_state[recipient] = recipient_state

    payload = {
        "schema_version": 1,
        "updated_at": _now_iso(),
        "recipients": recipients_state,
    }
    _write_dispatch_state(state_dir, payload)
    return {"skipped": False, "results": results, "dispatch_state": payload}


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Cross-harness bridge trigger — event-driven replacement for the "
            "smart-poller. Reads live bridge/INDEX.md, computes per-recipient "
            "actionable signature, dispatches recipient harness on signature change."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="GT-KB project root (must contain groundtruth.toml). Default: auto-resolve.",
    )
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=None,
        help=(
            "Dispatch-state directory. Default: <project_root>/.gtkb-state/"
            "cross-harness-trigger/."
        ),
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=DEFAULT_MAX_ITEMS,
        help=f"Cap on selected entries per dispatch (default {DEFAULT_MAX_ITEMS}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Compute signatures and update dispatch-state but do NOT spawn the "
            "recipient harness."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print the run summary to stdout (default: silent fire-and-forget).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Always returns 0 per fire-and-forget contract."""
    args = _build_argparser().parse_args(argv)
    try:
        project_root = _resolve_project_root(args.project_root)
        state_dir = (
            args.state_dir.resolve()
            if args.state_dir is not None
            else project_root.joinpath(*DEFAULT_STATE_SUBDIR)
        )
        summary = run_trigger(
            project_root=project_root,
            state_dir=state_dir,
            max_items=args.max_items,
            dry_run=args.dry_run,
        )
        if args.verbose:
            print(json.dumps(summary, indent=2, sort_keys=True))
    except SystemExit:
        # argparse's --help / config errors. Re-raise to allow normal CLI UX
        # but they are not "dispatch failures" — surface to stderr.
        raise
    except Exception as exc:  # noqa: BLE001 — fire-and-forget catch-all
        # Per fire-and-forget contract: never propagate. Best-effort log to
        # state-dir if resolvable, else stderr only.
        try:
            payload = {
                "ts": _now_iso(),
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            if "state_dir" in dir() and state_dir is not None:  # type: ignore[has-type]
                _record_dispatch_failure(state_dir, payload)  # type: ignore[has-type]
        except Exception:  # noqa: BLE001
            pass
        print(f"cross-harness trigger error (suppressed): {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
