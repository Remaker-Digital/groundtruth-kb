#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Single-harness bridge dispatcher — wake routine for single-harness topology.

Per ``bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md`` (Codex GO
at ``-006``):

This script is the single-harness counterpart to the cross-harness event-driven
trigger (``scripts/cross_harness_bridge_trigger.py``). Where the cross-harness
trigger fires from PostToolUse + Stop hooks of active interactive sessions in
multi-harness topology, this dispatcher fires from a Windows Task Scheduler
task (per ``DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001``) on a fixed
interval in single-harness topology — owner-out-of-loop by design.

Substrate selection at runtime:

- Multi-harness topology (two harnesses with singleton role-sets): the
  cross-harness trigger is active; this dispatcher's applicability check
  returns False; this dispatcher no-ops.
- Single-harness topology (one harness ID with a multi-element role-set
  containing both ``prime-builder`` and ``loyal-opposition``): the
  cross-harness trigger's IP-8 topology gate inerts it; this dispatcher's
  applicability check returns True; this dispatcher performs in-process
  dispatch.

The two substrates are mutually exclusive at runtime; both honor the same
actionable-signature scheme, active-session-suppression contract, and
fire-and-forget audit-log discipline.

Specs:

- ``SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`` v1 — behavior contract.
- ``DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`` v1 — wake-substrate
  constraint (Windows scheduled task primary).
- ``ADR-SINGLE-HARNESS-OPERATING-MODE-001`` v1 — operating-mode topology
  decision.
- ``SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`` v1 +
  ``DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`` v1 — keyword the dispatcher
  emits.
- ``PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001`` v2 — audit-log
  discipline preserved via shared ``dispatch-failures.jsonl``.

This script reuses the cross-harness trigger's signature scheme + state-path
+ audit-log path so the two substrates share durable state cleanly (their
applicability gates ensure no double-dispatch in any topology).
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_STATE_SUBDIR = (".gtkb-state", "bridge-poller")  # shared with cross-harness trigger
DISPATCH_STATE_FILENAME = "dispatch-state.json"
DISPATCH_FAILURES_FILENAME = "dispatch-failures.jsonl"
DISPATCH_RUNS_SUBDIR = "dispatch-runs"
LOCK_FILENAME = "dispatcher.lock"
LOCK_SANITY_TTL_ENV_VAR = "GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS"
LOCK_SANITY_TTL_DEFAULT_SECONDS = 120
DEFAULT_MAX_ITEMS = 2  # matches cross-harness trigger DEFAULT_MAX_ITEMS

# Manual-disable env var (parity with cross-harness trigger's
# GTKB_NO_CROSS_HARNESS_TRIGGER). Used as an operator opt-out, never as
# automatic loop prevention.
LOOP_PREVENTION_ENV_VAR = "GTKB_NO_SINGLE_HARNESS_DISPATCHER"

_LABEL_TO_CANONICAL_MODE = {"prime-builder": "pb", "loyal-opposition": "lo"}


# ---------------------------------------------------------------------------
# Trigger-module imports
# ---------------------------------------------------------------------------
#
# Reuse the cross-harness trigger's signature scheme, audit-log helpers,
# active-session-suppression contract, and dispatch-state I/O. Per IP-1 of
# bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md, the two
# substrates share state-path + signature scheme so future liveness diagnosis
# does not need substrate-specific parsing.


def _load_trigger_module():
    """Import scripts/cross_harness_bridge_trigger.py as a module.

    Direct import is preferred over copy-paste duplication: the trigger is
    the canonical source for the signature scheme + audit-log helpers, and
    any future change there should automatically propagate here.
    """
    name = "_cross_harness_bridge_trigger_for_dispatcher"
    if name in sys.modules:
        return sys.modules[name]
    trigger_path = Path(__file__).resolve().parent / "cross_harness_bridge_trigger.py"
    spec = importlib.util.spec_from_file_location(name, trigger_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load cross-harness trigger from {trigger_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Project-root + role-map resolution (mirror trigger pattern)
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def _resolve_project_root(explicit: Path | None) -> Path:
    """Resolve the GT-KB project root.

    Order:
      1. Explicit ``--project-root`` flag.
      2. Lazy import of ``groundtruth_kb.bridge.paths.resolve_project_root``.
      3. ``GTKB_PROJECT_ROOT`` env var.

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


# ---------------------------------------------------------------------------
# Applicability gate (inverse of cross-harness trigger's IP-8 gate)
# ---------------------------------------------------------------------------


def _is_single_harness_topology_applicable(project_root: Path) -> tuple[bool, str | None]:
    """Return (applicable, harness_id_if_applicable).

    Single-harness topology is applicable iff the role map has exactly one
    harness ID whose role-set contains BOTH ``prime-builder`` AND
    ``loyal-opposition`` (multi-element set).

    Fail-closed: unreadable role-map -> not applicable; the dispatcher
    no-ops rather than guessing the topology.
    """
    trigger = _load_trigger_module()
    try:
        role_map = trigger._read_role_assignments(project_root)
    except ValueError:
        return (False, None)
    harnesses = role_map.get("harnesses", {})
    if not isinstance(harnesses, dict) or len(harnesses) != 1:
        return (False, None)
    ((harness_id, record),) = harnesses.items()
    if not isinstance(record, dict):
        return (False, None)
    raw_role = record.get("role")
    if not isinstance(raw_role, list):
        return (False, None)
    role_set = {str(r).strip().lower() for r in raw_role if isinstance(r, str)}
    if "prime-builder" in role_set and "loyal-opposition" in role_set:
        return (True, str(harness_id))
    return (False, None)


# ---------------------------------------------------------------------------
# Lock management
# ---------------------------------------------------------------------------


def _acquire_lock(state_dir: Path) -> bool:
    """Attempt to acquire the single-instance dispatcher lock.

    Returns True on success, False if another instance holds a fresh lock.
    Stale-lock reclamation: a lock older than GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS
    (default 120 s) is considered abandoned and reclaimed.
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = state_dir / LOCK_FILENAME
    try:
        sanity_ttl = int(os.environ.get(LOCK_SANITY_TTL_ENV_VAR, LOCK_SANITY_TTL_DEFAULT_SECONDS))
    except (TypeError, ValueError):
        sanity_ttl = LOCK_SANITY_TTL_DEFAULT_SECONDS
    if sanity_ttl <= 0:
        sanity_ttl = LOCK_SANITY_TTL_DEFAULT_SECONDS
    if lock_path.exists():
        try:
            age_seconds = dt.datetime.now().timestamp() - lock_path.stat().st_mtime
        except OSError:
            age_seconds = sanity_ttl + 1
        if age_seconds <= sanity_ttl:
            return False
    try:
        lock_path.write_text(
            json.dumps({"pid": os.getpid(), "acquired_at": _now_iso()}),
            encoding="utf-8",
        )
    except OSError:
        return False
    return True


def _release_lock(state_dir: Path) -> None:
    lock_path = state_dir / LOCK_FILENAME
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Active-session suppression (foreground session held by active harness)
# ---------------------------------------------------------------------------


def _foreground_session_active(state_dir: Path, harness_id: str, project_root: Path) -> bool:
    """Return True iff the active harness has a fresh foreground-session lock.

    Lock file path: ``<state-dir>/active-<command-handle>-session.lock``,
    where command_handle is resolved from harness-identities.json. Lock is
    "fresh" if its mtime is within GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS
    (default 120 s).
    """
    trigger = _load_trigger_module()
    try:
        identities = trigger._read_harness_identities(project_root)
        id_to_handle = trigger._invert_identities(identities)
    except (ValueError, KeyError):
        return False
    handle = id_to_handle.get(harness_id)
    if not handle:
        return False
    lock_path = state_dir / f"active-{handle}-session.lock"
    if not lock_path.exists():
        return False
    try:
        sanity_ttl = int(os.environ.get(LOCK_SANITY_TTL_ENV_VAR, LOCK_SANITY_TTL_DEFAULT_SECONDS))
    except (TypeError, ValueError):
        sanity_ttl = LOCK_SANITY_TTL_DEFAULT_SECONDS
    if sanity_ttl <= 0:
        sanity_ttl = LOCK_SANITY_TTL_DEFAULT_SECONDS
    try:
        age_seconds = dt.datetime.now().timestamp() - lock_path.stat().st_mtime
    except OSError:
        return False
    return age_seconds <= sanity_ttl


def _resolve_command_handle(project_root: Path, harness_id: str) -> str | None:
    """Resolve harness_id -> command_handle via harness-identities.json."""
    trigger = _load_trigger_module()
    try:
        identities = trigger._read_harness_identities(project_root)
        id_to_handle = trigger._invert_identities(identities)
    except (ValueError, KeyError):
        return None
    return id_to_handle.get(harness_id)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def _build_prompt(target_mode: str, items: list[Any], max_items: int, trigger) -> str:
    """Construct the canonical init-keyword prompt for a target role/mode."""
    selected = trigger._selected_oldest_first(items, max_items)
    rows = [f"- {item.top_status} {item.document_name} {item.top_file}" for item in selected]
    selected_text = "\n".join(rows) if rows else "- No selected entries."
    canonical_keyword = f"::init gtkb {target_mode}"
    return "\n".join(
        [
            canonical_keyword,
            "",
            "Single-harness bridge dispatcher notification (Slice 2 scheduled task).",
            "",
            (
                "This is an automated bridge dispatch from the single-harness dispatcher, "
                "not a fresh-session owner stimulus; do not wait for another owner "
                "message before processing the selected entries."
            ),
            "",
            "Read your durable role from harness-state/role-assignments.json. Multi-element "
            "role sets accept BOTH `pb` and `lo` keyword modes; this dispatch carries "
            f"mode `{target_mode}` for this work item.",
            "Read bridge/INDEX.md directly before acting. Treat the live latest status as authoritative.",
            "Keep work scoped to the selected bridge entries and preserve the bridge protocol audit trail.",
            "",
            f"Selected entries, oldest-first, capped at {max_items}:",
            selected_text,
        ]
    )


def _spawn_worker(
    *,
    command_handle: str,
    needed_role_label: str,
    target_mode: str,
    items: list[Any],
    project_root: Path,
    state_dir: Path,
    max_items: int,
    dry_run: bool,
    trigger,
) -> dict[str, Any]:
    """Fire-and-forget spawn a worker subprocess.

    Per SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Wake Mechanism step 4-5:
    invoke ``claude -p <prompt>`` or ``codex exec <prompt> --cd <root>`` with
    the canonical init keyword as first line + dispatch env vars set.
    """
    prompt = _build_prompt(target_mode, items, max_items, trigger)
    dispatch_id = f"{dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H-%M-%SZ')}-{needed_role_label}-{uuid.uuid4().hex[:6]}"

    if command_handle == "codex":
        command = ["codex", "exec", prompt, "--cd", str(project_root)]
    elif command_handle == "claude":
        command = [
            "claude",
            "-p",
            prompt,
            "--add-dir",
            str(project_root),
            "--output-format",
            "json",
        ]
    else:
        meta = {
            "dispatch_id": dispatch_id,
            "recipient": needed_role_label,
            "launched": False,
            "reason": "unknown_command_handle",
        }
        trigger._record_dispatch_failure(state_dir, meta)
        return meta

    if dry_run:
        return {
            "dispatch_id": dispatch_id,
            "recipient": needed_role_label,
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
    env["GTKB_BRIDGE_POLLER_RUN_ID"] = dispatch_id
    env["GTKB_BRIDGE_DISPATCH_KEYWORD"] = f"::init gtkb {target_mode}"
    env.pop(LOOP_PREVENTION_ENV_VAR, None)

    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    meta: dict[str, Any] = {
        "dispatch_id": dispatch_id,
        "recipient": needed_role_label,
        "launched_at": _now_iso(),
        "command_head": command[:2],
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }
    try:
        with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
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
        trigger._record_dispatch_failure(state_dir, meta)
    return meta


# ---------------------------------------------------------------------------
# Main dispatch routine
# ---------------------------------------------------------------------------


def run_dispatcher(
    *,
    project_root: Path,
    state_dir: Path,
    max_items: int = DEFAULT_MAX_ITEMS,
    dry_run: bool = False,
) -> dict[str, Any]:
    """One dispatch cycle. Always succeeds (fire-and-forget).

    Returns a summary dict for diagnose/test use; never propagates exceptions
    from dispatch attempts.
    """
    if os.environ.get(LOOP_PREVENTION_ENV_VAR) == "1":
        return {"skipped": True, "reason": "loop_prevention_env_var"}

    applicable, harness_id = _is_single_harness_topology_applicable(project_root)
    if not applicable:
        return {"skipped": True, "reason": "not_applicable_multi_harness_topology"}
    assert harness_id is not None

    if _foreground_session_active(state_dir, harness_id, project_root):
        return {"skipped": True, "reason": "foreground_session_active"}

    if not _acquire_lock(state_dir):
        return {"skipped": True, "reason": "another_instance_running"}

    try:
        trigger = _load_trigger_module()
        index_text = trigger._read_index_live(project_root)
        actionable_for_prime, actionable_for_codex = trigger._compute_actionable(index_text, project_root)

        command_handle = _resolve_command_handle(project_root, harness_id)
        if command_handle is None:
            trigger._record_dispatch_failure(
                state_dir,
                {
                    "dispatch_id": f"{_now_iso()}-resolve-fail",
                    "recipient": "unknown",
                    "launched": False,
                    "reason": "command_handle_resolution_failed",
                    "error_message": (
                        f"Could not resolve command handle for harness ID {harness_id!r}. "
                        "Check harness-state/harness-identities.json."
                    ),
                },
            )
            return {
                "skipped": True,
                "reason": "command_handle_resolution_failed",
                "harness_id": harness_id,
            }

        state = trigger._load_dispatch_state(state_dir)
        recipients_state = state.get("recipients") if isinstance(state, dict) else {}
        if not isinstance(recipients_state, dict):
            recipients_state = {}
        recipients_state = trigger._migrate_recipients_state_keys(recipients_state)

        results: dict[str, Any] = {}
        pending = [
            ("prime-builder", actionable_for_prime),
            ("loyal-opposition", actionable_for_codex),
        ]
        for needed_role_label, items in pending:
            mode = _LABEL_TO_CANONICAL_MODE[needed_role_label]
            filtered = [it for it in items if getattr(it, "dispatchable", True)]
            selected = trigger._selected_oldest_first(filtered, max_items)
            signature = trigger._signature(selected)

            prior = recipients_state.get(needed_role_label)
            prior_legacy_signature = prior.get("signature") if isinstance(prior, dict) else None
            prior_dispatched = (
                prior.get("last_dispatched_signature")
                if isinstance(prior, dict) and prior.get("last_dispatched_signature") is not None
                else prior_legacy_signature
            )

            recipient_state: dict[str, Any] = {
                "signature_scope": "selected_dispatch_batch",
                "pending_count": len(filtered),
                "selected_count": len(selected),
                "raw_pending_count": len(items),
                "updated_at": _now_iso(),
                "last_dispatched_signature": prior_dispatched,
                "signature": prior_legacy_signature,
            }

            if not selected:
                recipient_state["last_result"] = "no_pending_after_filter" if items else "no_pending"
                recipient_state["signature"] = signature
                results[needed_role_label] = {
                    "launched": False,
                    "reason": recipient_state["last_result"],
                }
            elif prior_dispatched == signature:
                recipient_state["signature"] = signature
                recipient_state["last_result"] = "unchanged"
                results[needed_role_label] = {
                    "launched": False,
                    "reason": "unchanged",
                }
            else:
                launch = _spawn_worker(
                    command_handle=command_handle,
                    needed_role_label=needed_role_label,
                    target_mode=mode,
                    items=filtered,
                    project_root=project_root,
                    state_dir=state_dir,
                    max_items=max_items,
                    dry_run=dry_run,
                    trigger=trigger,
                )
                recipient_state["last_result"] = "launched" if launch.get("launched") else "launch_failed"
                recipient_state["last_launch"] = launch
                recipient_state["last_dispatched_signature"] = signature
                recipient_state["signature"] = signature
                results[needed_role_label] = launch

            recipients_state[needed_role_label] = recipient_state

        payload = {
            "schema_version": 1,
            "updated_at": _now_iso(),
            "recipients": recipients_state,
        }
        trigger._write_dispatch_state(state_dir, payload)
        return {
            "skipped": False,
            "harness_id": harness_id,
            "command_handle": command_handle,
            "results": results,
            "dispatch_state": payload,
        }
    finally:
        _release_lock(state_dir)


# ---------------------------------------------------------------------------
# Diagnose mode (mirrors cross-harness trigger _emit_diagnose_summary)
# ---------------------------------------------------------------------------


def _emit_diagnose_summary(state_dir: Path, project_root: Path) -> str:
    """Render a structured liveness summary; read-only.

    Mirrors ``scripts/cross_harness_bridge_trigger.py::_emit_diagnose_summary``
    structure so operator UX is uniform across substrates.
    """
    lines: list[str] = []
    lines.append(f"Single-harness bridge dispatcher diagnose - {_now_iso()}")
    lines.append("")
    lines.append("== Trigger infrastructure ==")
    script_path = Path(__file__).resolve()
    lines.append(f"- Script: {script_path}")
    lines.append(f"- State dir: {state_dir}")
    applicable, harness_id = _is_single_harness_topology_applicable(project_root)
    lines.append(f"- Applicability: {applicable} (harness_id={harness_id})")
    lines.append("")

    trigger = _load_trigger_module()
    lines.append("== Dispatch state ==")
    state = trigger._load_dispatch_state(state_dir)
    if not state:
        lines.append("- File: ABSENT (no dispatches recorded)")
        lines.append("")
        lines.append("== Overall ==")
        lines.append("- DEGRADED: dispatch-state.json absent (cold start or wiped state).")
        return "\n".join(lines)
    state_path = state_dir / DISPATCH_STATE_FILENAME
    lines.append(f"- File: {state_path}")
    lines.append(f"- Last update: {state.get('updated_at', '(missing)')}")
    lines.append("")

    lines.append("== Per-recipient state ==")
    recipients = state.get("recipients", {}) or {}
    for name in ("prime-builder", "loyal-opposition"):
        rec = recipients.get(name) or {}
        if not rec:
            lines.append(f"- {name}: (no state recorded)")
            continue
        sig = (rec.get("signature") or "")[:8] or "(none)"
        last_dispatched = (rec.get("last_dispatched_signature") or "")[:8] or "(none)"
        lines.append(
            f"- {name}: last_result={rec.get('last_result', '?')}, "
            f"pending={rec.get('pending_count', '?')}, "
            f"selected={rec.get('selected_count', '?')}"
        )
        lines.append(f"  signature {sig}... last_dispatched={last_dispatched}...")
    lines.append("")

    lines.append("== Recent failures ==")
    failures_path = state_dir / DISPATCH_FAILURES_FILENAME
    if not failures_path.is_file():
        lines.append("- dispatch-failures.jsonl absent (no failures recorded).")
    else:
        try:
            raw = failures_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            raw = []
        records: list[dict[str, Any]] = []
        for line in raw:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(rec, dict):
                records.append(rec)
        lines.append(f"- Total in dispatch-failures.jsonl: {len(records)}")
        class_counts: dict[str, int] = {}
        for rec in records:
            cls = str(rec.get("reason") or rec.get("error_type") or "unknown")
            class_counts[cls] = class_counts.get(cls, 0) + 1
        for cls, count in sorted(class_counts.items(), key=lambda kv: -kv[1]):
            lines.append(f"  - {cls}: {count}")
    lines.append("")

    lines.append("== Overall ==")
    if applicable:
        lines.append("- HEALTHY (applicable): dispatcher is the active substrate for this topology.")
    else:
        lines.append("- NOT APPLICABLE: multi-harness topology; cross-harness trigger is the active substrate.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Single-harness bridge dispatcher - wakes from a Windows scheduled "
            "task; reads bridge/INDEX.md; computes per-role actionable signatures; "
            "spawns subprocess workers in single-harness topology when work waits."
        )
    )
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--state-dir", type=Path, default=None)
    parser.add_argument(
        "--max-items",
        type=int,
        default=DEFAULT_MAX_ITEMS,
        help=f"Cap on selected entries per dispatch (default {DEFAULT_MAX_ITEMS}).",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help=("Emit a structured liveness summary to stdout WITHOUT performing dispatch or mutating state."),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Always returns 0 per fire-and-forget contract."""
    args = _build_argparser().parse_args(argv)
    try:
        project_root = _resolve_project_root(args.project_root)
        state_dir = (
            args.state_dir.resolve() if args.state_dir is not None else project_root.joinpath(*DEFAULT_STATE_SUBDIR)
        )
        if args.diagnose:
            print(_emit_diagnose_summary(state_dir, project_root))
            return 0
        summary = run_dispatcher(
            project_root=project_root,
            state_dir=state_dir,
            max_items=args.max_items,
            dry_run=args.dry_run,
        )
        if args.verbose:
            print(json.dumps(summary, indent=2, sort_keys=True))
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - fire-and-forget contract
        print(f"single-harness dispatcher error (suppressed): {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
