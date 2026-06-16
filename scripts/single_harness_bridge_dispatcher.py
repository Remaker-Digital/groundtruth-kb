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

_DISPATCHER_DIR = str(Path(__file__).resolve().parent)
if _DISPATCHER_DIR not in sys.path:
    sys.path.insert(0, _DISPATCHER_DIR)

_PACKAGE_SRC = str(Path(__file__).resolve().parents[1] / "groundtruth-kb" / "src")
if _PACKAGE_SRC not in sys.path:
    sys.path.insert(0, _PACKAGE_SRC)

from bridge_lease_registry import is_lease_held  # noqa: E402
from gtkb_session_id import SESSION_ID_ENV_VARS  # noqa: E402
from implementation_authorization import (  # noqa: E402
    AuthorizationError,
    issue_dispatch_authorization_packets,
)

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

    Per Slice 1 of ``gtkb-operating-mode-transaction-001``, the applicability
    decision delegates to ``groundtruth_kb.mode_switch.derive.topology_from_role_map``
    so the dispatcher, startup, and ``workstream_focus.save_state`` all
    compute byte-identical results.

    Fail-closed: unreadable role-map -> not applicable; the dispatcher
    no-ops rather than guessing the topology.
    """
    trigger = _load_trigger_module()
    try:
        role_map = trigger._read_role_assignments(project_root)
    except ValueError:
        return (False, None)

    try:
        from groundtruth_kb.mode_switch.derive import (
            SINGLE_HARNESS,
            topology_from_role_map,
        )
    except ImportError:
        # Fail-closed fallback if the package is unavailable for any reason.
        return (False, None)

    if topology_from_role_map(role_map) != SINGLE_HARNESS:
        return (False, None)
    harnesses = role_map.get("harnesses", {})
    if not isinstance(harnesses, dict) or len(harnesses) != 1:
        return (False, None)
    ((harness_id, _record),) = harnesses.items()
    return (True, str(harness_id))


# ---------------------------------------------------------------------------
# Gated-wake applicability (FAB-01 step 4 / HYG-004)
# ---------------------------------------------------------------------------
#
# The cross-harness event-driven trigger can only fire when an active harness
# carries live event-firing hook surfaces (``can_fire_events`` — Claude Code /
# Codex CLI per ADR-CODEX-HOOK-PARITY-FALLBACK-001). In a topology where every
# active harness is event-less (``can_fire_events`` False — e.g. only ollama /
# openrouter / antigravity active), the trigger never fires and Axis-1
# auto-dispatch is dead even though launchable dispatch TARGETS exist (HYG-004).
# FAB-01 generalizes this dispatcher's scheduled-task substrate to ALSO wake in
# that degraded topology, reusing the existing actionable-signature dedup so the
# wake spawns only on a changed signature (NOT a blind interval full-spawn —
# the retired-poller defect class forbidden by bridge-essential.md and the GO
# constraints on bridge/gtkb-fab-01-dispatch-substrate-revival-002.md).
#
# Safety: when an event-source harness IS active (the normal multi-harness
# topology — e.g. codex A + claude B active and event-capable), the gated wake
# is NOT applicable and the dispatcher no-ops under the wake gate. The
# cross-harness trigger remains the sole substrate; the two stay mutually
# exclusive at runtime (parity with the single-harness/multi-harness gate).

# Event-firing harness types, mirroring
# ``groundtruth_kb.harness_projection._EVENT_FIRING_CAPABLE_TYPES``. Used only as
# a fallback when a (legacy) projection record predates the ``can_fire_events``
# split axis; current projections always carry the field.
_EVENT_FIRING_HARNESS_TYPES = frozenset({"claude", "claude-code", "codex", "codex-cli"})


def _record_is_active_event_source(record: dict[str, Any]) -> bool:
    """True iff the harness record is ``active`` AND can fire bridge dispatch events.

    Reads the honest ``can_fire_events`` axis (FAB-01 / HYG-004). The deprecated
    ``event_driven_hooks`` alias is intentionally NOT consulted here: it now
    equals ``can_receive_dispatch`` (its de-facto current meaning), so a hook-less
    dispatch target like ollama would be misread as an event source. A legacy
    record lacking ``can_fire_events`` falls back to the harness-type set.
    """
    status = record.get("status")
    if not (isinstance(status, str) and status.strip().lower() == "active"):
        return False
    can_fire = record.get("can_fire_events")
    if can_fire is True:
        return True
    if can_fire is False:
        return False
    htype = str(record.get("harness_type") or "").strip().lower()
    return htype in _EVENT_FIRING_HARNESS_TYPES


def _no_active_event_source_harness(project_root: Path) -> bool:
    """Return True iff >=1 harness is active AND none can fire bridge events.

    This is the FAB-01 degraded-topology condition: launchable dispatch targets
    exist but the cross-harness trigger has no active event source to fire it.

    Fail-closed: an unreadable role map returns False (do not justify a wake we
    cannot read).
    """
    trigger = _load_trigger_module()
    try:
        role_map = trigger._read_role_assignments(project_root)
    except ValueError:
        return False
    harnesses = role_map.get("harnesses", {})
    if not isinstance(harnesses, dict) or not harnesses:
        return False
    active = [
        record
        for record in harnesses.values()
        if isinstance(record, dict)
        and isinstance(record.get("status"), str)
        and record["status"].strip().lower() == "active"
    ]
    if not active:
        return False
    return not any(_record_is_active_event_source(record) for record in active)


def _gated_wake_applicable(project_root: Path) -> tuple[bool, str | None]:
    """Return (applicable, reason) for the gated scheduled wake.

    Applicable when EITHER:
      - single-harness topology applies (the substrate's original purpose), OR
      - no active event-source harness exists (FAB-01: the cross-harness trigger
        is structurally unable to fire).

    Returns ``(False, None)`` in the normal multi-harness-with-event-source
    topology so the wake stays inert and the cross-harness trigger remains the
    sole substrate.
    """
    applicable, _harness_id = _is_single_harness_topology_applicable(project_root)
    if applicable:
        return (True, "single_harness_topology")
    if _no_active_event_source_harness(project_root):
        return (True, "no_active_event_source_harness")
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
            "Read your durable role from harness-state/harness-registry.json (canonical role registry per Slice 1 retirement). Multi-element "
            "role sets accept BOTH `pb` and `lo` keyword modes; this dispatch carries "
            f"mode `{target_mode}` for this work item.",
            "Read current TAFE/dispatcher bridge state and status-bearing versioned bridge files before acting; do not require or recreate bridge/INDEX.md.",
            "Keep work scoped to the selected bridge entries and preserve the bridge protocol audit trail.",
            "",
            f"Selected entries, oldest-first, capped at {max_items}:",
            selected_text,
        ]
    )


def _issue_dispatch_authorization_for_selected(
    selected: list[Any],
    *,
    project_root: Path,
    state_dir: Path,
    recipient: str,
    dispatch_id: str,
    trigger,
) -> dict[str, Any]:
    """Create implementation-start packets for a selected Prime dispatch batch."""
    bridge_ids = [str(item.document_name) for item in selected]
    try:
        context = issue_dispatch_authorization_packets(project_root, bridge_ids, dispatch_id=dispatch_id)
    except AuthorizationError as exc:
        failed_slug = bridge_ids[0] if bridge_ids else None
        payload: dict[str, Any] = {
            "ts": _now_iso(),
            "dispatch_id": dispatch_id,
            "recipient": recipient,
            "launched": False,
            "reason": "implementation_authorization_packet_failed",
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "bridge_ids": bridge_ids,
        }
        if failed_slug is not None:
            payload["document_name"] = failed_slug
        trigger._record_dispatch_failure(state_dir, payload)
        return {
            "ok": False,
            "reason": "implementation_authorization_packet_failed",
            "bridge_ids": bridge_ids,
            "failed_slug": failed_slug,
            "error": str(exc),
        }
    return {"ok": True, "reason": None, "context": context}


def _resolve_dispatcher_targets(
    needed_role_label: str,
    project_root: Path,
    items: list[Any] | None = None,
) -> list[Any]:
    """Resolve active harnesses for the given role to be dispatched by the poller.

    Orthogonal to event-driven hooks capability. Returns eligible targets in
    dispatch-config ranking order.
    """
    trigger = _load_trigger_module()
    role_map = trigger._read_role_assignments(project_root)
    harnesses = role_map.get("harnesses", {})
    if not isinstance(harnesses, dict):
        raise ValueError("harness-registry projection missing 'harnesses' mapping")

    def _record_has_role(h_info: dict[str, object], wanted: str) -> bool:
        raw = h_info.get("role")
        if isinstance(raw, str):
            candidates = {raw.strip().lower()}
        elif isinstance(raw, (list, tuple, set, frozenset)):
            candidates = {str(r).strip().lower() for r in raw}
        else:
            return False
        if wanted in candidates:
            return True
        return wanted == "prime-builder" and "acting-prime-builder" in candidates

    def _is_active(h_info: dict[str, object]) -> bool:
        status = h_info.get("status")
        return isinstance(status, str) and status.strip().lower() == "active"

    role_matching = [
        (h_id, h_info)
        for h_id, h_info in harnesses.items()
        if isinstance(h_info, dict) and _record_has_role(h_info, needed_role_label)
    ]
    active_matching = [
        (h_id, h_info)
        for h_id, h_info in role_matching
        if _is_active(h_info) and trigger._record_can_receive_dispatch(h_info)
    ]
    try:
        from groundtruth_kb.bridge_dispatch_config import load_bridge_dispatch_config, select_dispatch_candidates

        dispatch_config = load_bridge_dispatch_config(project_root)
        context = trigger._dispatch_context_for_items(needed_role_label, project_root, items)
        records = []
        for h_id, h_info in active_matching:
            record = dict(h_info)
            record["id"] = str(h_id)
            records.append(record)
        ranked = select_dispatch_candidates(records, dispatch_config, context)
        ranked_ids = [str(record.get("id") or "") for record in ranked]
        by_id = {str(h_id): (h_id, h_info) for h_id, h_info in active_matching}
        if ranked_ids or dispatch_config.rules:
            active_matching = [by_id[h_id] for h_id in ranked_ids if h_id in by_id]
        else:
            active_matching = sorted(
                active_matching,
                key=lambda item: (trigger._reviewer_precedence_for_record(item[1]), str(item[0])),
            )
    except Exception:
        active_matching = sorted(
            active_matching,
            key=lambda item: (trigger._reviewer_precedence_for_record(item[1]), str(item[0])),
        )

    targets = []
    identities = trigger._read_harness_identities(project_root)
    id_to_handle = trigger._invert_identities(identities)

    for h_id, role_record in active_matching:
        identity_handle = id_to_handle.get(h_id)
        if not identity_handle:
            raise ValueError(f"harness ID {h_id!r} has no entry in harness-identities")
        role_type = str(role_record.get("harness_type") or "").strip().lower()
        if role_type != identity_handle:
            raise ValueError(
                f"harness {h_id!r} type drift: role registry says {role_type!r} but "
                f"harness-identities says {identity_handle!r}"
            )
        targets.append(
            trigger.DispatchTarget(
                needed_role_label=needed_role_label,
                harness_id=h_id,
                command_handle=identity_handle,
                canonical_mode=_LABEL_TO_CANONICAL_MODE[needed_role_label],
                invocation_surfaces=role_record.get("invocation_surfaces"),
            )
        )

    return targets


def _spawn_worker(
    *,
    target: Any,
    items: list[Any],
    project_root: Path,
    state_dir: Path,
    max_items: int,
    dry_run: bool,
    trigger,
    dispatch_id: str | None = None,
) -> dict[str, Any]:
    """Spawn a worker subprocess dynamically using the target's argv template.

    Ensures environment isolation by popping parent session IDs.
    """
    prompt = trigger._dispatch_prompt(target, items, max_items)
    command = trigger._harness_command(target, prompt, project_root)
    recipient_key = target.dispatch_state_key
    dispatch_id = (
        dispatch_id
        or f"{dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H-%M-%SZ')}-{recipient_key}-{uuid.uuid4().hex[:6]}"
    )

    if command is None:
        meta = {
            "dispatch_id": dispatch_id,
            "recipient": recipient_key,
            "launched": False,
            "reason": "unknown_recipient",
            "error_message": f"No headless surface or command template registered for harness {target.harness_id!r}",
        }
        trigger._record_dispatch_failure(state_dir, meta)
        return meta

    if dry_run:
        return {
            "dispatch_id": dispatch_id,
            "recipient": recipient_key,
            "launched": False,
            "reason": "dry_run",
            "command_head": command[:2],
        }

    packet_context: dict[str, Any] | None = None
    if target.needed_role_label == "prime-builder":
        selected = trigger._selected_oldest_first(items, max_items)
        issue_result = trigger._issue_dispatch_authorization_for_selected(
            selected,
            project_root=project_root,
            state_dir=state_dir,
            recipient=recipient_key,
            dispatch_id=dispatch_id,
        )
        if not issue_result["ok"]:
            return {
                "dispatch_id": dispatch_id,
                "recipient": recipient_key,
                "launched": False,
                "reason": issue_result["reason"],
                "failed_slug": issue_result.get("failed_slug"),
                "error_message": issue_result.get("error"),
            }
        packet_context = issue_result["context"]

    runs_dir = state_dir / DISPATCH_RUNS_SUBDIR
    runs_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = runs_dir / f"{dispatch_id}.stdout.log"
    stderr_path = runs_dir / f"{dispatch_id}.stderr.log"

    env = dict(os.environ)
    env["GTKB_PROJECT_ROOT"] = str(project_root)

    # Strip all parent session-related environment variables
    for var in SESSION_ID_ENV_VARS:
        env.pop(var, None)

    # Re-apply only worker-specific session identifiers
    env["GTKB_BRIDGE_POLLER_RUN_ID"] = dispatch_id
    env["GTKB_INHERITED_SESSION_ID"] = dispatch_id

    if packet_context is not None:
        packet_bridge_ids = [str(item) for item in packet_context.get("bridge_ids", [])]
        packet_hashes = [
            str(packet.get("packet_hash"))
            for packet in packet_context.get("packets", [])
            if isinstance(packet, dict) and packet.get("packet_hash")
        ]
        env["GTKB_IMPLEMENTATION_AUTH_DISPATCH_ID"] = dispatch_id
        env["GTKB_IMPLEMENTATION_AUTH_BRIDGE_IDS"] = ",".join(packet_bridge_ids)
        env["GTKB_IMPLEMENTATION_AUTH_CURRENT_BRIDGE_ID"] = str(packet_context.get("current_bridge_id") or "")
        env["GTKB_IMPLEMENTATION_AUTH_PACKET_HASHES"] = ",".join(packet_hashes)
    env["GTKB_BRIDGE_DISPATCH_KEYWORD"] = f"::init gtkb {target.canonical_mode}"
    env.pop(LOOP_PREVENTION_ENV_VAR, None)

    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    meta: dict[str, Any] = {
        "dispatch_id": dispatch_id,
        "recipient": recipient_key,
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
    enforce_wake_gate: bool = False,
) -> dict[str, Any]:
    """One dispatch cycle. Always succeeds (fire-and-forget).

    Returns a summary dict for diagnose/test use; never propagates exceptions
    from dispatch attempts.

    ``enforce_wake_gate`` (FAB-01 step 4): when True, the cycle no-ops unless the
    gated wake is applicable (single-harness topology OR no active event-source
    harness). This keeps the scheduled wake mutually exclusive with the
    cross-harness trigger — in the normal multi-harness-with-event-source
    topology the wake gate is closed and the dispatcher does not spawn. Default
    False preserves the original single-harness dispatch behavior for callers
    that gate applicability themselves.
    """
    if os.environ.get(LOOP_PREVENTION_ENV_VAR) == "1":
        return {"skipped": True, "reason": "loop_prevention_env_var"}

    if enforce_wake_gate:
        wake_ok, wake_reason = _gated_wake_applicable(project_root)
        if not wake_ok:
            return {"skipped": True, "reason": "wake_gate_not_applicable"}

    if not _acquire_lock(state_dir):
        return {"skipped": True, "reason": "another_instance_running"}

    try:
        trigger = _load_trigger_module()
        index_text = trigger._read_index_live(project_root)
        actionable_for_prime, actionable_for_codex = trigger._compute_actionable(index_text, project_root)

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
        resolved_targets = []
        for needed_role_label, items in pending:
            # Resolve targets
            try:
                targets = _resolve_dispatcher_targets(needed_role_label, project_root, items=items)
            except ValueError as exc:
                trigger._record_dispatch_failure(
                    state_dir,
                    {
                        "dispatch_id": f"{_now_iso()}-resolve-fail",
                        "recipient": needed_role_label,
                        "launched": False,
                        "reason": "dispatch_target_resolution_failed",
                        "error_message": str(exc),
                    },
                )
                prior = recipients_state.get(needed_role_label)
                recipient_state = dict(prior) if isinstance(prior, dict) else {}
                recipient_state["last_result"] = "dispatch_target_resolution_failed"
                recipient_state["updated_at"] = _now_iso()
                recipients_state[needed_role_label] = recipient_state
                results[needed_role_label] = {"launched": False, "reason": "dispatch_target_resolution_failed"}
                continue

            if not targets:
                trigger._record_dispatch_failure(
                    state_dir,
                    {
                        "dispatch_id": f"{_now_iso()}-no-active-target",
                        "recipient": needed_role_label,
                        "launched": False,
                        "reason": "no_active_target_for_role",
                        "error_message": f"no active harness for role {needed_role_label!r}",
                    },
                )
                prior = recipients_state.get(needed_role_label)
                recipient_state = dict(prior) if isinstance(prior, dict) else {}
                recipient_state["last_result"] = "no_active_target_for_role"
                recipient_state["updated_at"] = _now_iso()
                recipients_state[needed_role_label] = recipient_state
                results[needed_role_label] = {"launched": False, "reason": "no_active_target_for_role"}
                continue

            # Keep track of first resolved target for backward-compat keys
            for t in targets:
                resolved_targets.append(t)

            # Filter out leased items
            filtered = [it for it in items if getattr(it, "dispatchable", True)]
            non_leased = [it for it in filtered if not is_lease_held(it.document_name, state_dir=state_dir)]
            selected = trigger._selected_oldest_first(non_leased, max_items)
            signature = trigger._signature(selected)

            prior = (
                recipients_state.get(needed_role_label)
                if isinstance(recipients_state.get(needed_role_label), dict)
                else {}
            )
            prior_legacy_signature = prior.get("signature") if isinstance(prior, dict) else None
            prior_dispatched = (
                prior.get("last_dispatched_signature")
                if isinstance(prior, dict) and prior.get("last_dispatched_signature") is not None
                else prior_legacy_signature
            )

            recipient_state = {
                "signature_scope": "selected_dispatch_batch",
                "pending_count": len(non_leased),
                "selected_count": len(selected),
                "raw_pending_count": len(items),
                "updated_at": _now_iso(),
                "last_dispatched_signature": prior_dispatched,
                "signature": prior_legacy_signature,
            }
            if isinstance(prior, dict) and isinstance(prior.get("last_launch"), dict):
                recipient_state["last_launch"] = prior["last_launch"]

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
                # Spawn workers for all resolved active targets
                launches = []
                for target in targets:
                    dispatch_id = trigger._new_dispatch_id(target.dispatch_state_key)
                    work_intent_session_id = trigger._work_intent_session_id(dispatch_id)
                    spawn_items = non_leased

                    if needed_role_label == "prime-builder" and selected:
                        work_intent_filter = trigger._filter_prime_selected_by_work_intent(
                            selected,
                            project_root=project_root,
                            state_dir=state_dir,
                            recipient=needed_role_label,
                            dispatch_id=dispatch_id,
                            session_id=work_intent_session_id,
                        )
                        if not work_intent_filter["ok"]:
                            launches.append(
                                {
                                    "dispatch_id": dispatch_id,
                                    "recipient": target.dispatch_state_key,
                                    "launched": False,
                                    "reason": work_intent_filter["reason"],
                                }
                            )
                            continue

                        dispatched_selected = list(work_intent_filter["selected"])
                        if not dispatched_selected:
                            launches.append(
                                {
                                    "dispatch_id": dispatch_id,
                                    "recipient": target.dispatch_state_key,
                                    "launched": False,
                                    "reason": "work_intent_already_held",
                                }
                            )
                            continue

                        if not dry_run:
                            acquire_result = trigger._acquire_prime_work_intent_batch(
                                dispatched_selected,
                                project_root=project_root,
                                state_dir=state_dir,
                                recipient=needed_role_label,
                                dispatch_id=dispatch_id,
                                session_id=work_intent_session_id,
                            )
                            if not acquire_result["ok"]:
                                launches.append(
                                    {
                                        "dispatch_id": dispatch_id,
                                        "recipient": target.dispatch_state_key,
                                        "launched": False,
                                        "reason": acquire_result["reason"],
                                    }
                                )
                                continue
                        spawn_items = dispatched_selected

                    launch = _spawn_worker(
                        target=target,
                        items=spawn_items,
                        project_root=project_root,
                        state_dir=state_dir,
                        max_items=max_items,
                        dry_run=dry_run,
                        trigger=trigger,
                        dispatch_id=dispatch_id,
                    )
                    if launch.get("launched") and not dry_run:
                        first_bridge_id = spawn_items[0].document_name if spawn_items else ""
                        import time

                        trigger._post_dispatch_poll(
                            dispatch_id=dispatch_id,
                            bridge_id=first_bridge_id,
                            dispatch_ts=time.time(),
                            project_root=project_root,
                            state_dir=state_dir,
                        )
                    launches.append(launch)

                # Aggregate results
                any_launched = any(ln.get("launched") for ln in launches)
                recipient_state["last_result"] = "launched" if any_launched else "launch_failed"
                recipient_state["last_launch"] = launches[0] if len(launches) == 1 else {"launches": launches}
                recipient_state["last_dispatched_signature"] = signature
                recipient_state["signature"] = signature
                results[needed_role_label] = launches[0] if len(launches) == 1 else {"launches": launches}

            recipients_state[needed_role_label] = recipient_state

        payload = {
            "schema_version": 1,
            "updated_at": _now_iso(),
            "recipients": recipients_state,
        }
        trigger._write_dispatch_state(state_dir, payload)

        # Populate backward-compat keys if at least one target was resolved
        harness_id = resolved_targets[0].harness_id if resolved_targets else "unknown"
        command_handle = resolved_targets[0].command_handle if resolved_targets else "unknown"

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
    lines.append("- Applicability: ALWAYS APPLICABLE (Unified periodic dispatcher)")
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
    lines.append("- HEALTHY: unified scheduled dispatcher is active for all topologies.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Single-harness bridge dispatcher - wakes from a Windows scheduled "
            "task; reads TAFE/versioned bridge state; computes per-role actionable signatures; "
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
    parser.add_argument(
        "--enforce-wake-gate",
        action="store_true",
        help=(
            "FAB-01: only dispatch when the gated wake is applicable "
            "(single-harness topology OR no active event-source harness). "
            "No-op otherwise so the wake stays mutually exclusive with the "
            "cross-harness trigger."
        ),
    )
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
            enforce_wake_gate=args.enforce_wake_gate,
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
