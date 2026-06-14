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
import shutil
import subprocess
import sys
import time
import tomllib
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# WI-3344: the function-level ``import harness_projection_reader`` in
# _resolve_dispatch_target resolves a sibling module under scripts/. A bare
# ``python scripts/cross_harness_bridge_trigger.py`` hook invocation puts
# scripts/ on sys.path[0] automatically, but importlib loading (tests) and
# ``python -m`` do not — so ensure this script's own directory is on sys.path
# before that import runs.
_TRIGGER_DIR = str(Path(__file__).resolve().parent)
if _TRIGGER_DIR not in sys.path:
    sys.path.insert(0, _TRIGGER_DIR)

from harness_projection_reader import load_harness_projection  # noqa: E402

# WI-3360: the lazy ``import groundtruth_kb`` calls in the dispatch/detection
# paths require ``groundtruth-kb/src`` on sys.path. The PostToolUse/Stop hook
# registrations run ``python scripts/cross_harness_bridge_trigger.py`` without
# PYTHONPATH set, so those imports raised ``ModuleNotFoundError: No module
# named 'groundtruth_kb'`` and the trigger could not dispatch. Add the package
# root alongside the sibling-scripts bootstrap above.
_PACKAGE_SRC = str(Path(__file__).resolve().parents[1] / "groundtruth-kb" / "src")
if _PACKAGE_SRC not in sys.path:
    sys.path.insert(0, _PACKAGE_SRC)

from bridge_lease_registry import is_lease_held  # noqa: E402, I001
from bridge_work_intent_registry import (  # noqa: E402, I001
    WorkIntentRegistryError,
    acquire as acquire_work_intent,
    current_holder as current_work_intent_holder,
    release as release_work_intent,
)
from implementation_authorization import (  # noqa: E402
    AuthorizationError,
    issue_dispatch_authorization_packets,
)

# WI-4480 Slice A: per-entry dispatch-starvation telemetry (observational).
# Guarded so a telemetry-module import failure can never break trigger import
# or dispatch; the call site is additionally exception-swallowed.
try:
    from bridge_dispatch_starvation_telemetry import record_starvation  # noqa: E402, I001
except Exception:  # noqa: BLE001 - telemetry import must never break dispatch
    record_starvation = None  # type: ignore[assignment]

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
BRIDGE_POLLER_STATE_SUBDIR = (".gtkb-state", "bridge-poller")
DISPATCH_STATE_FILENAME = "dispatch-state.json"
QUIESCE_STATE_FILENAME = "quiesce-state.json"
DISPATCH_FAILURES_FILENAME = "dispatch-failures.jsonl"
DISPATCH_RUNS_SUBDIR = "dispatch-runs"
DISPATCH_FAILURES_MAX_BYTES_ENV_VAR = "GTKB_DISPATCH_FAILURES_MAX_BYTES"
DEFAULT_JSONL_MAX_BYTES = 10 * 1024 * 1024
DEFAULT_JSONL_ROLLOVERS = 5
DEFAULT_DISPATCH_FAILURES_MAX_BYTES = DEFAULT_JSONL_MAX_BYTES
DEFAULT_DISPATCH_RUNS_RETENTION_DAYS = 14
DEFAULT_DISPATCH_RUNS_MAX_BYTES = 200 * 1024 * 1024
DEFAULT_GTKB_STATE_GC_AGE_DAYS = 14
RUNTIME_RETENTION_CONFIG_REL = Path("config") / "governance" / "runtime-evidence-retention.toml"
# WI-4472: hard global concurrency cap on live dispatched headless harness
# processes. The 2026-06-11 dispatch storm accumulated ~300 hung codex
# sessions because nothing bounded the total live-process count. Default 8 is
# well above normal steady-state (2 roles x a few harnesses) and far below the
# incident peak; env-tunable, fail-safe to the default on invalid/non-positive.
MAX_LIVE_DISPATCHED_PROCESSES_ENV_VAR = "GTKB_MAX_LIVE_DISPATCHED_PROCESSES"
DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES = 8

# Selected-batch cap mirrors the smart-poller's default per
# ``groundtruth-kb/scripts/bridge_poller_runner.py:670-673``. Bumping this
# requires a separate bridge proposal — Codex F1 on
# ``-008`` flagged unilateral cap changes as scope creep.
DEFAULT_MAX_ITEMS = 2
QUIESCE_WINDOW_SECONDS = 5.0
QUIESCE_WINDOW_ENV_VAR = "GTKB_TRIGGER_QUIESCE_SECONDS"
CLAUDE_WORKER_ALLOWED_TOOLS = "Read Edit Write Glob Grep Bash TodoWrite NotebookEdit"
WORK_INTENT_TRIGGER_SESSION_PREFIX = "trigger-dispatched-"
WORK_INTENT_TRIGGER_TTL_SECONDS = 600
WORK_INTENT_HELD_DEDUPE_FILENAME = "work-intent-held-dedupe.json"
DEFAULT_DISPATCH_MAX_RETRIES = 3
DEFAULT_DISPATCH_RETRY_DELAY_SECONDS = 300
IMPLEMENTATION_AUTH_ENV_VARS = (
    "GTKB_IMPLEMENTATION_AUTH_DISPATCH_ID",
    "GTKB_IMPLEMENTATION_AUTH_BRIDGE_IDS",
    "GTKB_IMPLEMENTATION_AUTH_CURRENT_BRIDGE_ID",
    "GTKB_IMPLEMENTATION_AUTH_PACKET_HASHES",
)
FATAL_WORKER_OUTPUT_MARKERS = (
    ("max-turn exhaustion", "max_turn_exhaustion"),
    ("guard denied Write", "guard_denied_write"),
    ("guard denied", "guard_denial"),
)
PRIOR_LAUNCH_LOG_READ_LIMIT_BYTES = 64 * 1024

# WI-3265 (bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md, Codex
# GO at -004): per-invocation diagnostic instrumentation. Observational only —
# the trigger's dispatch behavior is unchanged. Records are appended to
# ``<state-dir>/trigger-diagnostic.jsonl`` (runtime state; not committed).
TRIGGER_DIAGNOSTIC_FILENAME = "trigger-diagnostic.jsonl"

# Diagnostic classification vocabulary. ``missed_stop_recovered`` is reserved
# for the future behavior-changing fix proposal and is intentionally NOT
# emitted by this observational pass (which only records the outcomes of
# existing dispatch branches; detecting a missed Stop would require new
# behavior that the -004 GO explicitly excludes from scope).
TRIGGER_DIAGNOSTIC_CLASSIFICATIONS = frozenset(
    {
        "active_session_suppressed",
        "dispatch_blocked",
        "dispatched",
        "no_change",
        "selected_batch_skipped",
        "missed_stop_recovered",
        "author_meets_reviewer_refused",
        "other",
    }
)

TARGET_ACTIVE_SESSION_RESULT = "target_active_session_present"
LEGACY_COUNTERPART_ACTIVE_SESSION_RESULT = "counterpart_active_session_present"

# Maps a per-recipient ``last_result`` (the existing dispatch-branch outcome)
# to a diagnostic classification. Unmapped results classify as ``other``.
# ``launch_failed`` maps to ``dispatched`` because it means the dispatch branch
# was entered (dry-run or a real spawn failure); the raw ``last_result`` is
# also recorded verbatim so the two remain distinguishable.
_LAST_RESULT_TO_DIAGNOSTIC_CLASSIFICATION = {
    TARGET_ACTIVE_SESSION_RESULT: "active_session_suppressed",
    LEGACY_COUNTERPART_ACTIVE_SESSION_RESULT: "active_session_suppressed",
    "launched": "dispatched",
    "launch_failed": "dispatched",
    "ollama_dispatch_not_ready": "dispatch_blocked",
    "unchanged": "no_change",
    "no_pending_after_filter": "selected_batch_skipped",
    "author_meets_reviewer_refused": "author_meets_reviewer_refused",
}


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


def _load_dispatch_state(state_dir: Path, project_root: Path | None = None) -> dict[str, Any]:
    target = state_dir / DISPATCH_STATE_FILENAME
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    if isinstance(raw, dict):
        recipients = raw.get("recipients", {})
        if isinstance(recipients, dict):
            raw["recipients"] = _migrate_recipients_state_keys(recipients, project_root)
        return raw
    return {}


def _load_quiesce_state(state_dir: Path) -> dict[str, Any]:
    target = state_dir / QUIESCE_STATE_FILENAME
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return raw if isinstance(raw, dict) else {}


# IP-3c: dispatch-state-key migration.
#
# Legacy keys in dispatch-state.json's recipients map are ``"prime"`` and
# ``"codex"`` (hardcoded by the smart-poller and pre-canonical-init-keyword
# trigger code). New keys are durable role labels ``"prime-builder"`` and
# ``"loyal-opposition"`` per DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001.
#
# Migration plan:
#   - Backward-compat read via ``_migrate_recipients_state_keys``: legacy
#     keys are translated to new keys on read so in-memory state uses only
#     new keys.
#   - Forward writes use only new keys; legacy keys disappear from the
#     file after the first dispatch cycle.
#   - One-shot migration; subsequent runs operate purely on new keys.
LEGACY_TO_NEW_STATE_KEY = {
    "prime": "prime-builder",
    "codex": "loyal-opposition",
}
ROLE_STATE_KEYS = ("prime-builder", "loyal-opposition")


def _migrate_recipients_state_keys(recipients: dict[str, Any], project_root: Path | None = None) -> dict[str, Any]:
    """Translate legacy state-keys to durable role labels on read, suffixing with active IDs.

    Per IP-3c: legacy ``"prime"`` and ``"codex"`` recipient keys are migrated.
    Unsuffixed role keys are resolved to active roles: ``role_label:harness_id``.
    """
    active_by_role: dict[str, str] = {}
    if project_root is not None:
        try:
            role_map = _read_role_assignments(project_root)
            harnesses = role_map.get("harnesses", {})
            for h_id, h_info in harnesses.items():
                if isinstance(h_info, dict) and h_info.get("status") == "active":
                    raw = h_info.get("role")
                    if isinstance(raw, str):
                        roles = {raw.strip().lower()}
                    elif isinstance(raw, (list, tuple, set, frozenset)):
                        roles = {str(r).strip().lower() for r in raw}
                    else:
                        roles = set()
                    for r in roles:
                        if r not in active_by_role:
                            active_by_role[r] = h_id
        except Exception:
            pass

    migrated: dict[str, Any] = {}
    for key, value in recipients.items():
        base_key = LEGACY_TO_NEW_STATE_KEY.get(key, key)
        if ":" not in base_key:
            if base_key in active_by_role:
                new_key = f"{base_key}:{active_by_role[base_key]}"
            else:
                new_key = base_key
        else:
            new_key = base_key

        if not isinstance(value, dict):
            migrated[new_key] = value
            continue

        if new_key in migrated and isinstance(migrated[new_key], dict):
            existing = migrated[new_key]
            existing_ts = str(existing.get("updated_at") or "")
            value_ts = str(value.get("updated_at") or "")
            if value_ts > existing_ts:
                migrated[new_key] = value
        else:
            migrated[new_key] = value
    return migrated


def _diagnose_recipient_state(
    recipients: dict[str, Any],
    project_root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Return diagnose recipients plus display annotations for legacy-only state."""

    has_new_keys = any(key in recipients for key in ROLE_STATE_KEYS)
    legacy_annotations: dict[str, str] = {}
    if not has_new_keys:
        for legacy_key, new_key in LEGACY_TO_NEW_STATE_KEY.items():
            if legacy_key in recipients:
                legacy_annotations[new_key] = " (legacy key)"
    return _migrate_recipients_state_keys(recipients, project_root), legacy_annotations


def _rename_with_retry(
    src: Path,
    dst: Path,
    *,
    total_attempts: int = 5,
    initial_backoff_s: float = 0.05,
) -> None:
    """Atomic rename with backoff on transient Windows access errors.

    Per ``bridge/gtkb-cross-harness-trigger-windows-rename-race-001-003.md``
    GO at ``-004`` (REVISED-1):

    Retries ``PermissionError`` only. This covers:
    - WinError 32 (sharing violation; target file held briefly by another
      process — concurrent trigger invocations, doctor probe, AV scanner).
    - WinError 5 (access denied; transient AV scanner hold or filesystem
      reorganization).

    Does NOT retry ``FileNotFoundError`` (WinError 2). With per-invocation
    temp paths (see ``_write_dispatch_state``), our temp cannot be racing
    another writer's removal; a missing temp indicates a different bug
    class (caller deleted our temp) and is raised immediately for
    diagnosis rather than silently retrying.

    Timing: ``total_attempts=5`` means up to 5 tries. Sleeps occur AFTER
    attempts 1-4 only (4 sleeps before the 5th attempt's potential raise):
    50ms / 100ms / 200ms / 400ms = ~750ms total worst-case sleep.
    """
    backoff = initial_backoff_s
    for attempt in range(1, total_attempts + 1):
        try:
            src.replace(dst)
            return
        except PermissionError:
            if attempt == total_attempts:
                raise
            time.sleep(backoff)
            backoff *= 2.0


def _write_dispatch_state(state_dir: Path, payload: dict[str, Any]) -> None:
    """Atomically write dispatch state under per-invocation temp path.

    Per ``bridge/gtkb-cross-harness-trigger-windows-rename-race-001-003.md``
    GO at ``-004`` (REVISED-1):

    Uses a per-invocation temp path ``dispatch-state.json.<pid>-<uuid8>.tmp``
    so concurrent trigger invocations cannot collide on a shared temp file.
    The shared-temp anti-pattern was the root of 191 historical failures
    (147 WinError 32 + 23 WinError 5 + 17 WinError 2 + 4 temp-perm).

    The rename to the canonical target uses ``_rename_with_retry`` to
    handle transient Windows file-in-use / access-denied races.

    On any error during write or rename, the temp file is best-effort
    cleaned up in a ``finally`` block so the per-invocation path doesn't
    accumulate orphans. Cleanup errors are swallowed so the original
    exception propagates.
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    target = state_dir / DISPATCH_STATE_FILENAME
    unique = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
    tmp = target.with_suffix(target.suffix + f".{unique}.tmp")
    try:
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        _rename_with_retry(tmp, target)
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def _write_quiesce_state(state_dir: Path, payload: dict[str, Any]) -> None:
    """Atomically write quiesce state under a per-invocation temp path."""
    state_dir.mkdir(parents=True, exist_ok=True)
    target = state_dir / QUIESCE_STATE_FILENAME
    unique = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
    tmp = target.with_suffix(target.suffix + f".{unique}.tmp")
    try:
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        _rename_with_retry(tmp, target)
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def _quiesce_window_seconds() -> float:
    raw = os.environ.get(QUIESCE_WINDOW_ENV_VAR)
    if raw is None or raw.strip() == "":
        return QUIESCE_WINDOW_SECONDS
    try:
        parsed = float(raw)
    except ValueError:
        return QUIESCE_WINDOW_SECONDS
    return max(0.0, parsed)


def _hook_context_value(hook_context: dict[str, str] | None, key: str) -> str:
    if not hook_context:
        return ""
    value = hook_context.get(key)
    return value if isinstance(value, str) else ""


def _env_positive_int(primary: str, legacy: str | None, default: int) -> int:
    for name in (primary, legacy):
        if not name:
            continue
        raw = os.environ.get(name)
        if raw is None or raw.strip() == "":
            continue
        try:
            value = int(raw)
        except ValueError:
            continue
        if value > 0:
            return value
    return default


def _dispatch_max_retries() -> int:
    return _env_positive_int("GTKB_DISPATCH_MAX_RETRIES", "OLLAMA_MAX_RETRIES", DEFAULT_DISPATCH_MAX_RETRIES)


def _dispatch_retry_delay_seconds() -> int:
    return _env_positive_int(
        "GTKB_DISPATCH_RETRY_DELAY_SECONDS",
        "OLLAMA_RETRY_DELAY_SECONDS",
        DEFAULT_DISPATCH_RETRY_DELAY_SECONDS,
    )


def _parse_iso_timestamp(value: Any) -> dt.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.UTC)
    return parsed.astimezone(dt.UTC)


def _circuit_breaker_half_open_allowed(recipient_state: dict[str, Any], retry_delay_seconds: int) -> bool:
    candidates: list[Any] = [recipient_state.get("circuit_breaker_tripped_at")]
    last_launch = recipient_state.get("last_launch")
    if isinstance(last_launch, dict):
        candidates.append(last_launch.get("launched_at"))
    candidates.append(recipient_state.get("updated_at"))

    for raw_timestamp in candidates:
        timestamp = _parse_iso_timestamp(raw_timestamp)
        if timestamp is None:
            continue
        return (dt.datetime.now(dt.UTC) - timestamp).total_seconds() >= retry_delay_seconds

    # Legacy tripped records had no timestamp. Allow one probe rather than
    # preserving an unrecoverable fail-closed state forever.
    return True


def _record_dispatch_failure(state_dir: Path, payload: dict[str, Any]) -> None:
    """Append a fire-and-forget failure record to the JSONL diagnosis log."""
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        target = state_dir / DISPATCH_FAILURES_FILENAME
        _rotate_dispatch_failures_if_needed(target)
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
    except OSError:
        pass


def _read_recent_text(path: Path, *, byte_limit: int = PRIOR_LAUNCH_LOG_READ_LIMIT_BYTES) -> str:
    try:
        raw = path.read_bytes()
    except OSError:
        return ""
    return raw[-byte_limit:].decode("utf-8", errors="replace")


def _detect_previous_launch_failure(
    prior: dict[str, Any],
    *,
    recipient: str,
    signature: str,
) -> dict[str, Any] | None:
    """Return failure evidence when prior worker logs show a fatal marker."""
    launch = prior.get("last_launch")
    if not isinstance(launch, dict):
        return None

    exit_code = launch.get("exit_code")
    if isinstance(exit_code, int) and exit_code != 0:
        error_type = "process_terminated_abruptly" if exit_code == 4294967295 else "subprocess_execution_failed"
        return {
            "ts": _now_iso(),
            "dispatch_id": _now_iso() + "-previous-launch-failed",
            "recipient": recipient,
            "launched": False,
            "reason": "previous_launch_failed",
            "error_type": error_type,
            "exit_code": exit_code,
            "prior_dispatch_id": launch.get("dispatch_id"),
            "prior_launched_at": launch.get("launched_at"),
            "signature": signature,
            "matched_markers": [{"field": "exit_code", "marker": str(exit_code), "label": error_type}],
        }

    matched: list[dict[str, str]] = []
    inspected_paths: dict[str, str] = {}
    for field in ("stdout_path", "stderr_path"):
        raw_path = launch.get(field)
        if not isinstance(raw_path, str) or not raw_path.strip():
            continue
        path = Path(raw_path)
        inspected_paths[field] = str(path)
        text = _read_recent_text(path)
        if not text:
            continue
        lowered = text.lower()
        for marker, label in FATAL_WORKER_OUTPUT_MARKERS:
            if marker.lower() in lowered:
                matched.append({"field": field, "marker": marker, "label": label})

    if not matched:
        return None

    return {
        "ts": _now_iso(),
        "dispatch_id": _now_iso() + "-previous-launch-failed",
        "recipient": recipient,
        "launched": False,
        "reason": "previous_launch_failed",
        "error_type": "fatal_worker_output_marker",
        "prior_dispatch_id": launch.get("dispatch_id"),
        "prior_launched_at": launch.get("launched_at"),
        "signature": signature,
        "matched_markers": matched,
        **inspected_paths,
    }


def _new_dispatch_id(recipient_key: str) -> str:
    safe_recipient = str(recipient_key or "").replace(":", "-")
    return f"{dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H-%M-%SZ')}-{safe_recipient}-{uuid.uuid4().hex[:6]}"


def _work_intent_session_id(dispatch_id: str) -> str:
    return dispatch_id


def _mark_work_intent_held_recorded(state_dir: Path, *, document_name: str, holder_session_id: str) -> bool:
    key = f"{document_name}|{holder_session_id}"
    now = time.time()
    dedupe_path = state_dir / WORK_INTENT_HELD_DEDUPE_FILENAME
    payload: dict[str, float] = {}
    try:
        raw = json.loads(dedupe_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            for raw_key, raw_expiry in raw.items():
                try:
                    expiry = float(raw_expiry)
                except (TypeError, ValueError):
                    continue
                if expiry > now:
                    payload[str(raw_key)] = expiry
    except (OSError, json.JSONDecodeError):
        payload = {}

    if payload.get(key, 0.0) > now:
        return False

    payload[key] = now + WORK_INTENT_TRIGGER_TTL_SECONDS
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        dedupe_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError:
        pass
    return True


def _record_prime_work_intent_held(
    *,
    state_dir: Path,
    recipient: str,
    dispatch_id: str,
    item: Any,
    holder: dict[str, str],
) -> None:
    holder_session_id = holder.get("session_id") or ""
    if not _mark_work_intent_held_recorded(
        state_dir,
        document_name=item.document_name,
        holder_session_id=holder_session_id,
    ):
        return
    _record_dispatch_failure(
        state_dir,
        {
            "ts": _now_iso(),
            "dispatch_id": dispatch_id,
            "recipient": recipient,
            "launched": False,
            "reason": "work_intent_already_held",
            "document_name": item.document_name,
            "top_status": item.top_status,
            "top_file": item.top_file,
            "holder_session_id": holder_session_id,
            "holder_ttl_expires_at": holder.get("ttl_expires_at"),
        },
    )


def _filter_prime_selected_by_work_intent(
    selected: list[Any],
    *,
    project_root: Path,
    state_dir: Path,
    recipient: str,
    dispatch_id: str,
    session_id: str,
) -> dict[str, Any]:
    """Drop Prime selected entries held by a different work-intent session."""
    unheld: list[Any] = []
    held_count = 0
    for item in selected:
        try:
            holder = current_work_intent_holder(item.document_name, project_root=project_root)
        except WorkIntentRegistryError as exc:
            _record_dispatch_failure(
                state_dir,
                {
                    "ts": _now_iso(),
                    "dispatch_id": dispatch_id,
                    "recipient": recipient,
                    "launched": False,
                    "reason": "work_intent_registry_error",
                    "document_name": item.document_name,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                },
            )
            return {
                "ok": False,
                "reason": "work_intent_registry_error",
                "selected": [],
                "held_count": held_count,
            }
        if holder is not None and holder.get("session_id") != session_id:
            held_count += 1
            _record_prime_work_intent_held(
                state_dir=state_dir,
                recipient=recipient,
                dispatch_id=dispatch_id,
                item=item,
                holder=holder,
            )
            continue
        unheld.append(item)
    return {"ok": True, "reason": None, "selected": unheld, "held_count": held_count}


def _release_prime_work_intents(slugs: list[str], *, project_root: Path, session_id: str) -> None:
    for slug in slugs:
        try:
            release_work_intent(slug, session_id, project_root=project_root)
        except WorkIntentRegistryError:
            pass


def _acquire_prime_work_intent_batch(
    selected: list[Any],
    *,
    project_root: Path,
    state_dir: Path,
    recipient: str,
    dispatch_id: str,
    session_id: str,
) -> dict[str, Any]:
    """Acquire all Prime selected slugs as an all-or-nothing batch."""
    acquired_slugs: list[str] = []
    for item in selected:
        slug = item.document_name
        try:
            acquired = acquire_work_intent(
                slug,
                session_id,
                ttl_seconds=WORK_INTENT_TRIGGER_TTL_SECONDS,
                project_root=project_root,
            )
        except WorkIntentRegistryError as exc:
            acquired = False
            error_type = type(exc).__name__
            error_message = str(exc)
        else:
            error_type = None
            error_message = None
        if not acquired:
            _release_prime_work_intents(acquired_slugs, project_root=project_root, session_id=session_id)
            payload: dict[str, Any] = {
                "ts": _now_iso(),
                "dispatch_id": dispatch_id,
                "recipient": recipient,
                "launched": False,
                "reason": "work_intent_acquire_failed",
                "document_name": slug,
                "released_slugs": acquired_slugs,
            }
            if error_type is not None:
                payload["error_type"] = error_type
            if error_message is not None:
                payload["error_message"] = error_message
            _record_dispatch_failure(state_dir, payload)
            return {
                "ok": False,
                "reason": "work_intent_acquire_failed",
                "acquired_slugs": acquired_slugs,
                "failed_slug": slug,
            }
        acquired_slugs.append(slug)
    return {"ok": True, "reason": None, "acquired_slugs": acquired_slugs}


def _issue_dispatch_authorization_for_selected(
    selected: list[Any],
    *,
    project_root: Path,
    state_dir: Path,
    recipient: str,
    dispatch_id: str,
) -> dict[str, Any]:
    """Create implementation-start packets for a selected Prime dispatch batch."""
    go_items = [item for item in selected if getattr(item, "top_status", "").upper() == "GO"]
    bridge_ids = [str(item.document_name) for item in go_items]
    if not bridge_ids:
        # All selected items are NO-GO revision tasks; no impl-auth packet needed.
        return {"ok": True, "reason": None, "context": {}}
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
        _record_dispatch_failure(state_dir, payload)
        return {
            "ok": False,
            "reason": "implementation_authorization_packet_failed",
            "bridge_ids": bridge_ids,
            "failed_slug": failed_slug,
            "error": str(exc),
        }
    return {"ok": True, "reason": None, "context": context}


def _dispatch_failures_max_bytes() -> int:
    raw = os.environ.get(DISPATCH_FAILURES_MAX_BYTES_ENV_VAR)
    if raw is None or raw.strip() == "":
        return DEFAULT_DISPATCH_FAILURES_MAX_BYTES
    try:
        parsed = int(raw)
    except ValueError:
        return DEFAULT_DISPATCH_FAILURES_MAX_BYTES
    return parsed if parsed > 0 else DEFAULT_DISPATCH_FAILURES_MAX_BYTES


def _runtime_retention_policy(project_root: Path) -> dict[str, int]:
    """Load FAB-13 runtime retention horizons with fail-safe defaults."""
    policy = {
        "dispatch_runs_retention_days": DEFAULT_DISPATCH_RUNS_RETENTION_DAYS,
        "dispatch_runs_max_bytes": DEFAULT_DISPATCH_RUNS_MAX_BYTES,
        "jsonl_max_bytes": DEFAULT_JSONL_MAX_BYTES,
        "jsonl_rollovers": DEFAULT_JSONL_ROLLOVERS,
        "gtkb_state_gc_age_days": DEFAULT_GTKB_STATE_GC_AGE_DAYS,
    }
    config_path = project_root / RUNTIME_RETENTION_CONFIG_REL
    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return policy

    runtime = data.get("cross_harness_trigger", {})
    gc = data.get("gtkb_state_gc", {})
    raw_values = {
        "dispatch_runs_retention_days": runtime.get("dispatch_runs_retention_days"),
        "dispatch_runs_max_bytes": runtime.get("dispatch_runs_max_bytes"),
        "jsonl_max_bytes": runtime.get("jsonl_max_bytes"),
        "jsonl_rollovers": runtime.get("jsonl_rollovers"),
        "gtkb_state_gc_age_days": gc.get("age_days"),
    }
    for key, raw in raw_values.items():
        try:
            parsed = int(raw)
        except (TypeError, ValueError):
            continue
        if parsed > 0:
            policy[key] = parsed
    return policy


def _jsonl_rollover_path(target: Path, index: int) -> Path:
    return target.with_name(f"{target.name}.{index}")


def _rotate_jsonl_if_needed(
    target: Path,
    *,
    max_bytes: int = DEFAULT_JSONL_MAX_BYTES,
    max_rollovers: int = DEFAULT_JSONL_ROLLOVERS,
) -> None:
    """Rotate ``target`` through ``.1``..``.N`` when it exceeds ``max_bytes``."""
    try:
        size = target.stat().st_size
    except FileNotFoundError:
        return
    except OSError:
        return
    if size <= max_bytes:
        return

    max_rollovers = max(1, max_rollovers)
    _safe_unlink(_jsonl_rollover_path(target, max_rollovers))
    for index in range(max_rollovers - 1, 0, -1):
        src = _jsonl_rollover_path(target, index)
        if src.exists():
            try:
                _rename_with_retry(src, _jsonl_rollover_path(target, index + 1))
            except OSError:
                return
    try:
        _rename_with_retry(target, _jsonl_rollover_path(target, 1))
    except OSError:
        return


def _dispatch_id_from_run_artifact(path: Path) -> str:
    name = path.name
    for suffix in (".stdout.log", ".stderr.log", ".exit_code", ".pid", ".prompt.txt", ".input.json"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return path.stem


def _run_artifact_live(path: Path, runs_dir: Path) -> bool:
    dispatch_id = _dispatch_id_from_run_artifact(path)
    pid_file = runs_dir / f"{dispatch_id}.pid"
    if not pid_file.is_file():
        return False
    status_file = runs_dir / f"{dispatch_id}.exit_code"
    try:
        if status_file.exists() and status_file.stat().st_size > 0:
            return False
        pid = int(pid_file.read_text(encoding="utf-8").strip())
    except (OSError, TypeError, ValueError):
        return False
    return _pid_alive(pid)


def _path_size(path: Path) -> int:
    try:
        if path.is_dir() and not path.is_symlink():
            return sum(child.stat().st_size for child in path.rglob("*") if child.is_file())
        return path.stat().st_size
    except OSError:
        return 0


def _remove_path_best_effort(path: Path) -> None:
    try:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()
    except OSError:
        pass


def _prune_dispatch_runs(
    runs_dir: Path,
    *,
    max_age_days: int,
    max_total_bytes: int,
    now_epoch: float | None = None,
) -> dict[str, int]:
    """Prune inactive dispatch-run artifacts by age, then oldest-first by size."""
    if not runs_dir.is_dir():
        return {"deleted_count": 0, "deleted_bytes": 0}

    now = time.time() if now_epoch is None else now_epoch
    cutoff = now - (max_age_days * 86400)
    candidates: list[tuple[float, int, Path]] = []
    deleted_count = 0
    deleted_bytes = 0

    for path in sorted(runs_dir.iterdir()):
        if _run_artifact_live(path, runs_dir):
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        size = _path_size(path)
        if mtime < cutoff:
            _remove_path_best_effort(path)
            deleted_count += 1
            deleted_bytes += size
            continue
        candidates.append((mtime, size, path))

    remaining_total = sum(size for _, size, path in candidates if path.exists())
    for _mtime, size, path in sorted(candidates, key=lambda item: item[0]):
        if remaining_total <= max_total_bytes:
            break
        if not path.exists() or _run_artifact_live(path, runs_dir):
            continue
        _remove_path_best_effort(path)
        remaining_total -= size
        deleted_count += 1
        deleted_bytes += size

    return {"deleted_count": deleted_count, "deleted_bytes": deleted_bytes}


def _gc_gtkb_state_runtime_dirs(state_root: Path, *, age_days: int, now_epoch: float | None = None) -> dict[str, int]:
    """Remove stale pytest/uv-cache runtime directories under .gtkb-state only."""
    if not state_root.is_dir():
        return {"deleted_count": 0, "deleted_bytes": 0}
    now = time.time() if now_epoch is None else now_epoch
    cutoff = now - (age_days * 86400)
    deleted_count = 0
    deleted_bytes = 0
    for path in sorted(state_root.rglob("*")):
        if not path.is_dir() or path.is_symlink():
            continue
        name = path.name.lower()
        if not any(token in name for token in ("pytest-tmp", "pytest_tmp", "pytest-cache", "uv-cache")):
            continue
        try:
            if path.stat().st_mtime >= cutoff:
                continue
        except OSError:
            continue
        size = _path_size(path)
        _remove_path_best_effort(path)
        deleted_count += 1
        deleted_bytes += size
    return {"deleted_count": deleted_count, "deleted_bytes": deleted_bytes}


def _apply_runtime_evidence_retention(project_root: Path, state_dir: Path) -> dict[str, Any]:
    """FAB-13 retention pass for regenerable trigger/runtime evidence."""
    policy = _runtime_retention_policy(project_root)
    state_dirs = [state_dir, project_root.joinpath(*BRIDGE_POLLER_STATE_SUBDIR)]
    seen: set[Path] = set()
    pruned: dict[str, dict[str, int]] = {}
    for candidate_state_dir in state_dirs:
        resolved = candidate_state_dir.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        _rotate_jsonl_if_needed(
            candidate_state_dir / DISPATCH_FAILURES_FILENAME,
            max_bytes=policy["jsonl_max_bytes"],
            max_rollovers=policy["jsonl_rollovers"],
        )
        _rotate_jsonl_if_needed(
            candidate_state_dir / TRIGGER_DIAGNOSTIC_FILENAME,
            max_bytes=policy["jsonl_max_bytes"],
            max_rollovers=policy["jsonl_rollovers"],
        )
        pruned[str(candidate_state_dir)] = _prune_dispatch_runs(
            candidate_state_dir / DISPATCH_RUNS_SUBDIR,
            max_age_days=policy["dispatch_runs_retention_days"],
            max_total_bytes=policy["dispatch_runs_max_bytes"],
        )

    gc_result = _gc_gtkb_state_runtime_dirs(
        project_root / ".gtkb-state",
        age_days=policy["gtkb_state_gc_age_days"],
    )
    return {"policy": policy, "dispatch_runs": pruned, "gtkb_state_gc": gc_result}


def _max_live_dispatched_processes() -> int:
    """Resolve the hard global concurrency cap (WI-4472).

    Reads ``GTKB_MAX_LIVE_DISPATCHED_PROCESSES``; fail-safe to
    ``DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES`` on missing/blank/invalid input
    and on non-positive values (a zero or negative cap would disable all
    dispatch, which is never the intended configuration).
    """
    raw = os.environ.get(MAX_LIVE_DISPATCHED_PROCESSES_ENV_VAR)
    if raw is None or raw.strip() == "":
        return DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES
    try:
        parsed = int(raw)
    except ValueError:
        return DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES
    return parsed if parsed > 0 else DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES


def _safe_unlink(path: Path) -> None:
    """Best-effort sidecar removal; never raises."""
    try:
        path.unlink()
    except OSError:
        pass


def _pid_alive(pid: int) -> bool:
    """Best-effort cross-platform process-liveness check (WI-4472).

    Prefers ``psutil.pid_exists`` when importable. Falls back to the Win32
    ``OpenProcess`` + ``GetExitCodeProcess`` pair on Windows and ``os.kill(pid,
    0)`` on POSIX. Any unknown/parse failure returns ``False`` (fail-closed to
    not-alive) so a malformed sidecar can never inflate the live-process count.
    """
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return False
    if pid_int <= 0:
        return False
    try:
        import psutil  # noqa: PLC0415

        return bool(psutil.pid_exists(pid_int))
    except Exception:  # noqa: BLE001 - degrade to the OS-native fallback
        pass
    if os.name == "nt":
        try:
            import ctypes  # noqa: PLC0415

            process_query_limited_information = 0x1000
            still_active = 259
            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            handle = kernel32.OpenProcess(process_query_limited_information, False, pid_int)
            if not handle:
                return False
            try:
                exit_code = ctypes.c_ulong()
                if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                    return exit_code.value == still_active
                return True
            finally:
                kernel32.CloseHandle(handle)
        except Exception:  # noqa: BLE001 - fail-closed to not-alive
            return False
    try:
        os.kill(pid_int, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _count_live_dispatched_processes(runs_dir: Path) -> int:
    """Count live dispatched headless harness processes via ``.pid`` sidecars.

    Each successful ``_spawn_harness`` launch writes ``<dispatch_id>.pid``.
    A dispatch is LIVE iff its sidecar exists, its ``<dispatch_id>.exit_code``
    status file (written by ``run_with_status.py`` only on child EXIT) is
    absent/empty, and the PID is alive. Sidecars whose process has exited or
    died (or whose contents are malformed) are pruned during the count pass so
    the runs dir does not grow unbounded.
    """
    if not runs_dir.is_dir():
        return 0
    live = 0
    for pid_file in sorted(runs_dir.glob("*.pid")):
        dispatch_id = pid_file.name[: -len(".pid")]
        try:
            pid_text = pid_file.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        try:
            pid = int(pid_text)
        except (TypeError, ValueError):
            _safe_unlink(pid_file)
            continue
        status_file = runs_dir / f"{dispatch_id}.exit_code"
        try:
            exited = status_file.exists() and status_file.stat().st_size > 0
        except OSError:
            exited = False
        if exited or not _pid_alive(pid):
            _safe_unlink(pid_file)
            continue
        live += 1
    return live


def _rotate_dispatch_failures_if_needed(target: Path) -> None:
    """Rotate dispatch-failures.jsonl through 5 rollovers when oversized."""
    _rotate_jsonl_if_needed(
        target,
        max_bytes=_dispatch_failures_max_bytes(),
        max_rollovers=DEFAULT_JSONL_ROLLOVERS,
    )


def _path_mtime_iso(path: Path) -> str | None:
    """Return ``path``'s mtime as a UTC ISO-8601 string, or None if unavailable.

    Used by WI-3265 diagnostic instrumentation; read-only, never raises.
    """
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return None
    return dt.datetime.fromtimestamp(mtime, dt.UTC).isoformat(timespec="seconds")


def _dispatch_state_mtime(state_dir: Path) -> float | None:
    try:
        return (state_dir / DISPATCH_STATE_FILENAME).stat().st_mtime
    except FileNotFoundError:
        return None


def _resolve_diagnose_state_dir(project_root: Path) -> Path:
    """Prefer the newest live dispatch-state directory for no-flag diagnose."""

    default_state_dir = project_root.joinpath(*DEFAULT_STATE_SUBDIR)
    candidates = [
        project_root.joinpath(*BRIDGE_POLLER_STATE_SUBDIR),
        default_state_dir,
    ]
    existing = [
        (mtime, state_dir) for state_dir in candidates if (mtime := _dispatch_state_mtime(state_dir)) is not None
    ]
    if not existing:
        return default_state_dir
    return max(existing, key=lambda item: item[0])[1]


def _classify_invocation_outcome(last_result: str) -> str:
    """Map a per-recipient ``last_result`` to a WI-3265 diagnostic class.

    Vocabulary per bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md
    (Codex GO at -004). ``missed_stop_recovered`` is reserved for a future
    behavior-changing fix proposal and is never produced by this observational
    pass. Unmapped results (e.g. ``no_pending``,
    ``dispatch_target_resolution_failed``) classify as ``other``.
    """
    if last_result.endswith("_dispatch_not_ready"):
        return "dispatch_blocked"
    return _LAST_RESULT_TO_DIAGNOSTIC_CLASSIFICATION.get(last_result, "other")


def _should_refuse_self_review(
    bridge_id: str,
    dispatched_harness_id: str,
    project_root: Path,
) -> bool:
    """Check if the latest version of the proposal for bridge_id was written by dispatched_harness_id."""
    import fnmatch
    import re

    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return False

    pattern1 = f"gtkb-{bridge_id}-*.md"
    pattern2 = f"{bridge_id}-*.md"

    candidate_files = []
    for file in bridge_dir.glob("*.md"):
        name = file.name
        if fnmatch.fnmatch(name, pattern1) or fnmatch.fnmatch(name, pattern2):
            candidate_files.append(file)

    if not candidate_files:
        return False

    # Sort to find the latest version
    candidate_files.sort(key=lambda f: f.name)
    latest_file = candidate_files[-1]

    try:
        content = latest_file.read_text(encoding="utf-8")
        # Parse first 30 lines for author_harness_id:
        lines = content.splitlines()[:30]
        for line in lines:
            match = re.match(r"^author_harness_id:\s*(\S+)", line.strip())
            if match:
                author_id = match.group(1).strip().strip('"').strip("'")
                if author_id == dispatched_harness_id:
                    return True
                break
    except Exception:
        pass

    return False


def _poll_dispatch_verdict(
    dispatch_ts: float,
    bridge_id: str,
    project_root: Path,
    timeout: float = 240.0,
    poll_interval: float = 5.0,
) -> tuple[str | None, float | None]:
    """Poll for a verdict file created after dispatch_ts. Returns (path, latency)."""
    import fnmatch
    import time

    start_time = time.monotonic()
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return None, None

    pattern1 = f"gtkb-{bridge_id}-*.md"
    pattern2 = f"{bridge_id}-*.md"

    while (time.monotonic() - start_time) < timeout:
        candidate_files = []
        for file in bridge_dir.glob("*.md"):
            name = file.name
            if fnmatch.fnmatch(name, pattern1) or fnmatch.fnmatch(name, pattern2):
                try:
                    mtime = file.stat().st_mtime
                    if mtime >= dispatch_ts:
                        candidate_files.append((file, mtime))
                except OSError:
                    continue

        if candidate_files:
            candidate_files.sort(key=lambda x: x[1])
            chosen_file, chosen_mtime = candidate_files[0]
            rel_path = f"bridge/{chosen_file.name}"
            latency = max(0.0, chosen_mtime - dispatch_ts)
            return rel_path, latency

        time.sleep(poll_interval)

    return None, None


def _poll_and_log_verdict(
    dispatch_id: str,
    bridge_id: str,
    dispatch_ts: float,
    project_root: Path,
    state_dir: Path,
) -> None:
    """Poll for verdict file in bridge/ and log results to dispatch-diagnostic-post.jsonl."""
    verdict_path, latency = _poll_dispatch_verdict(
        dispatch_ts=dispatch_ts,
        bridge_id=bridge_id,
        project_root=project_root,
    )
    log_file = state_dir / "dispatch-diagnostic-post.jsonl"
    record = {
        "timestamp": _now_iso(),
        "dispatch_id": dispatch_id,
        "bridge_id": bridge_id,
        "dispatch_timestamp": dt.datetime.fromtimestamp(dispatch_ts, dt.UTC).isoformat(timespec="seconds"),
        "verdict_path": verdict_path,
        "verdict_latency_seconds": latency,
    }
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass


def _post_dispatch_poll(
    dispatch_id: str,
    bridge_id: str,
    dispatch_ts: float,
    project_root: Path,
    state_dir: Path,
) -> None:
    """Spawn a durable subprocess to poll for dispatch verdict in background."""
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--project-root",
        str(project_root),
        "--state-dir",
        str(state_dir),
        "--post-dispatch-poll",
        "--post-dispatch-id",
        dispatch_id,
        "--post-dispatch-bridge-id",
        bridge_id,
        "--post-dispatch-timestamp",
        str(dispatch_ts),
    ]
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    else:
        creationflags = 0
    try:
        subprocess.Popen(
            command,
            cwd=str(project_root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
            close_fds=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        _record_dispatch_failure(
            state_dir,
            {
                "ts": _now_iso(),
                "dispatch_id": dispatch_id,
                "bridge_id": bridge_id,
                "launched": False,
                "reason": "post_dispatch_poll_spawn_failed",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
        )


def _emit_trigger_diagnostic(state_dir: Path, record: dict[str, Any]) -> None:
    """Append one fire-and-forget diagnostic record to trigger-diagnostic.jsonl.

    WI-3265 (bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md, Codex
    GO at -004): observational instrumentation only. Mirrors
    ``_record_dispatch_failure`` — never raises, so an instrumentation I/O
    error cannot perturb the trigger's fire-and-forget dispatch contract.
    """
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        target = state_dir / TRIGGER_DIAGNOSTIC_FILENAME
        _rotate_jsonl_if_needed(target)
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
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


def _effective_max_items_for_target(target: DispatchTarget, max_items: int) -> int:
    if max_items <= 0:
        return 0
    if isinstance(target.invocation_surfaces, dict):
        headless = target.invocation_surfaces.get("headless")
        if isinstance(headless, dict):
            limit = headless.get("max_items")
            if isinstance(limit, int):
                return min(max_items, limit)
    return max_items


def _dispatch_prompt(target: DispatchTarget, items: list[Any], max_items: int) -> str:
    """Build the dispatch prompt mirroring the smart-poller phrasing.

    Per IP-3b of bridge/gtkb-canonical-init-keyword-syntax-001-007.md
    (Codex GO at -008): emits the canonical init-keyword
    ``::init gtkb <mode>`` as the first line per
    SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (regex
    ``^::init gtkb (pb|lo)$``; closed vocabulary; first-line-only). The
    mode is derived from the resolved ``target.canonical_mode``.

    The existing prose role-line is retained as defense-in-depth per
    DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (keyword is authority;
    prose is informational).
    """
    selected = _selected_oldest_first(items, max_items)
    rows = [f"- {item.top_status} {item.document_name} {item.top_file}" for item in selected]
    selected_text = "\n".join(rows) if rows else "- No selected entries."
    harness_info_line = (
        f"Your resolved harness ID is {target.harness_id!r} ({target.command_handle!r}) "
        f"and your active role is {target.needed_role_label!r} (canonical mode: {target.canonical_mode!r})."
    )
    role_line = (
        f"{harness_info_line}\n"
        "Resolve your durable harness identity from `harness-state/harness-identities.json`, "
        "then read your assigned role from `harness-state/harness-registry.json` "
        "through the canonical `groundtruth_kb.harness_projection` or `gt harness roles` reader. "
        "Process the bridge entries selected below according to your declared role: "
        "Loyal Opposition reviews latest NEW or REVISED entries; "
        "Prime Builder acts on latest GO or NO-GO entries assigned to its harness. "
        "Latest VERIFIED entries are bridge closure for both roles and are not "
        "queue work; do not process them as actionable."
    )
    worker_context_line = (
        "Worker context: this auto-dispatched harness cannot interactively ask "
        "the owner for input. If a required owner decision blocks the selected "
        "work, record the blocker in the bridge artifact and stop instead of "
        "asking in prose."
    )
    loyal_opposition_preflight_line = (
        "Loyal Opposition verdict requirement: before writing GO or VERIFIED, "
        "run `python scripts/bridge_applicability_preflight.py --bridge-id <document-name>` "
        "and `python scripts/adr_dcl_clause_preflight.py --bridge-id <document-name>`, "
        "then include the clean Applicability Preflight section in the verdict artifact."
    )
    canonical_keyword = f"::init gtkb {target.canonical_mode}"
    return "\n".join(
        [
            canonical_keyword,
            "",
            "Bridge auto-dispatch notification (cross-harness trigger).",
            "",
            (
                "This is an automated bridge dispatch, not a fresh-session owner stimulus; "
                "do not wait for another owner message before processing the selected entries."
            ),
            "",
            role_line,
            worker_context_line,
            loyal_opposition_preflight_line,
            "Read bridge/INDEX.md directly before acting. Treat the live latest status as authoritative.",
            "If any listed entry is no longer actionable for your role, do not act on that stale entry.",
            "Keep work scoped to the selected bridge entries and preserve the bridge protocol audit trail.",
            "",
            f"Selected entries, oldest-first, capped at {max_items}:",
            selected_text,
        ]
    )


def _normalize_argv_head(head: str, project_root: Path) -> str:
    """Normalize and resolve an argv executable head for reliable launch.

    HYG-001 (FAB-01): registry argv heads fail ``CreateProcess`` with
    ``WinError 2`` in two distinct ways on Windows:

    - **Relative forward-slash paths** (e.g. ``groundtruth-kb/.venv/Scripts/python.exe``):
      ``CreateProcess`` cannot resolve a relative path whose separators are
      forward slashes. ``os.path.normpath`` rewrites them to the native
      separator.
    - **Bare command names** (e.g. ``gemini``) that exist on disk only as
      ``gemini.ps1`` / ``gemini.cmd``: ``subprocess`` performs no ``PATHEXT``
      resolution, so the bare name is not found. ``shutil.which`` is
      ``PATHEXT``-aware and resolves the launchable variant.

    Strategy: ``normpath`` the head; for a relative path that contains a
    directory separator, resolve it against ``project_root`` so ``which`` sees
    the same file the dispatched subprocess (``cwd=project_root``) would; then
    run ``shutil.which`` to confirm/resolve an absolute launchable path.

    Additive and fail-safe: when no resolution succeeds the normalized head is
    returned (and the original head if normalization itself is empty), so a
    host where ``which`` cannot see the command still receives the registry
    literal rather than a broken value. Normalization never raises.
    """
    if not head:
        return head
    normalized = os.path.normpath(head)
    # A relative path with a directory component is resolved against the
    # project root (the subprocess cwd) so PATHEXT/existence resolution matches
    # launch context. A bare command name (no separator) is left for PATH
    # lookup by shutil.which.
    candidate = normalized
    if (os.sep in normalized or (os.altsep and os.altsep in normalized)) and not os.path.isabs(normalized):
        candidate = os.path.normpath(str(project_root / normalized))
    resolved = shutil.which(candidate)
    if resolved:
        return resolved
    # Fall back to resolving the (un-rooted) normalized form too — covers a
    # bare PATHEXT command and any host where the rooted candidate is absent
    # but the command is on PATH.
    if candidate != normalized:
        resolved = shutil.which(normalized)
        if resolved:
            return resolved
    return normalized


def _dispatch_target_argv_head(target: DispatchTarget) -> str | None:
    """Return a dispatch target's headless argv executable head, or ``None``.

    Mirrors the extraction the doctor launchability check (FAB-01 / HYG-001)
    performs on raw registry records, but operates on the already-resolved
    ``DispatchTarget``. Placeholder tokens are not real executables, so they
    yield ``None`` and the pre-spawn gate (WI-4525) skips them rather than
    false-failing.
    """
    surfaces = target.invocation_surfaces
    headless = surfaces.get("headless") if isinstance(surfaces, dict) else None
    argv = headless.get("argv") if isinstance(headless, dict) else None
    if not isinstance(argv, list) or not argv or not isinstance(argv[0], str):
        return None
    head = argv[0]
    if head in ("{{PROMPT}}", "{{PROJECT_ROOT}}"):
        return None
    return head


def _argv_head_launchable(head: str, project_root: Path) -> bool:
    """Return True when a normalized argv head resolves to a launchable file.

    Reuses ``_normalize_argv_head`` then models the ``CreateProcess`` executable
    lookup the same way the doctor launchability check does: ``shutil.which``
    (PATHEXT-aware) OR an existing file. Resolution failure IS the WinError-2
    launch failure the WI-4525 pre-spawn gate exists to catch.
    """
    resolved = _normalize_argv_head(head, project_root)
    return bool(shutil.which(resolved)) or os.path.isfile(resolved)


def _harness_command(target: DispatchTarget, prompt: str, project_root: Path) -> list[str] | None:
    """Build the recipient harness invocation command, data-driven from the
    harness-registry projection.

    Per WI-3344 / REQ-HARNESS-REGISTRY-001 FR8 / DELIB-2079 Q9: the command is
    built from ``target.invocation_surfaces``. Its ``headless`` entry carries
    an ordered ``argv`` template whose elements are literal strings or the
    placeholder tokens ``{{PROMPT}}`` and ``{{PROJECT_ROOT}}``, each substituted
    as a single individual argv element. No shell is invoked and no per-harness
    command fallback is hard-coded.

    The only role-specific overlay is the approved Prime-worker Claude
    permission profile from ``gtkb-prime-worker-permission-profile-slice-1``:
    Claude headless workers get ``acceptEdits`` plus an explicit authoring-tool
    allow-list so Edit/Write calls do not hang on interactive permission
    prompts. PreToolUse governance hooks remain the safety floor, and the
    allow-list intentionally excludes ``AskUserQuestion``, web tools, and MCP
    tools.

    Fails closed to ``None`` ("unknown_recipient") for EVERY harness — Claude
    and Codex included — when ``invocation_surfaces`` is missing, has no
    ``headless`` entry, or carries a malformed ``argv`` (absent, empty, not a
    list, or containing a non-string element).
    """
    surfaces = target.invocation_surfaces
    if not isinstance(surfaces, dict):
        return None
    headless = surfaces.get("headless")
    if not isinstance(headless, dict):
        return None
    argv_template = headless.get("argv")
    if not isinstance(argv_template, list) or not argv_template:
        return None
    command: list[str] = []
    for element in argv_template:
        if not isinstance(element, str):
            return None
        if element == "{{PROMPT}}":
            if target.command_handle == "antigravity":
                command.append("")
            else:
                command.append(prompt)
        elif element == "{{PROJECT_ROOT}}":
            command.append(str(project_root))
        else:
            command.append(element)
    # HYG-001: normalize/resolve the executable head so a forward-slash-relative
    # path or a bare PATHEXT command launches under CreateProcess. Applied to
    # command[0] (the harness executable) before any role overlay appends flags.
    command[0] = _normalize_argv_head(command[0], project_root)
    if target.command_handle == "claude":
        if "--permission-mode" not in command:
            command.extend(["--permission-mode", "acceptEdits"])
        if "--allowed-tools" not in command and "--allowedTools" not in command:
            command.extend(["--allowed-tools", CLAUDE_WORKER_ALLOWED_TOOLS])

    if os.name == "nt" and command:
        new_command: list[str] = []
        skip = False
        for i in range(len(command)):
            if skip:
                skip = False
                continue
            if command[i] in {"-p", "--prompt"} and i + 1 < len(command) and command[i + 1] == "":
                new_command.append("--prompt=")
                skip = True
            else:
                new_command.append(command[i])
        command = new_command

    return command


# ---------------------------------------------------------------------------
# Active-session suppression (cross-harness-trigger-active-session-suppression
# at -005 GO at -006).
#
# When the target harness holds an active foreground session (its heartbeat
# lock file is present and fresh), suppress dispatch to that
# role to prevent duplicate auto-dispatched parallel-revision work. The
# suppression state-machine uses two signature fields:
#
# - last_dispatched_signature: the signature actually spawned. Slice 2
#   dedup field — current signature == last_dispatched_signature → skip.
# - last_suppressed_signature: marker that suppression fired. Allows
#   retry after target exits because last_dispatched_signature was
#   never updated.
#
# Legacy ``signature`` field is preserved for backward-compat readers and
# is updated only on real dispatch (not on suppression).
#
# Lock files live in the same ``--state-dir`` the trigger uses (typically
# ``.gtkb-state/bridge-poller``). The hook commands MUST pass identical
# ``--state-dir`` values to both ``active_session_heartbeat.py`` and this
# script. Heartbeat script enforces ``--state-dir`` as REQUIRED so the
# coupling is explicit at config time.
# ---------------------------------------------------------------------------


HEARTBEAT_LOCK_TEMPLATE = "active-{role}-session.lock"


# ---------------------------------------------------------------------------
# IP-3a: Routing data model and durable-record-driven dispatch resolution.
#
# Per ``bridge/gtkb-canonical-init-keyword-syntax-001-007.md`` (Codex GO at
# ``-008``) and SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 +
# DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (both inserted into MemBase).
#
# DispatchTarget is the single source of truth for recipient-keyed routing
# decisions. Constructed by ``_resolve_dispatch_target(needed_role_label)``
# and consumed by callers that previously took a hardcoded ``recipient``
# parameter (migration to consumption is IP-3b).
#
# Authority chain (per DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001):
#   1. harness-registry.json: needed_role_label -> harness_id  (canonical role authority)
#   2. harness-identities.json (inverted): harness_id -> harness_command_handle
#      (identity authority)
#   3. Drift check: role_record["harness_type"] (denormalized) MUST match
#      identity-derived handle.
#
# The role record's ``harness_type`` field is OPTIONAL drift-detection
# metadata, NOT command-handle authority.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DispatchTarget:
    """Resolved dispatch target for a needed durable role.

    Single source of truth for recipient-keyed routing decisions. Constructed
    by ``_resolve_dispatch_target(needed_role_label)`` per
    DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001. Consumed by:

      - ``_dispatch_prompt`` (uses ``canonical_mode`` for ``::init gtkb <mode>``
        keyword first-line per SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001).
      - ``_harness_command`` (uses ``command_handle`` for invocation choice).
      - ``check_target_active`` (uses ``active_session_lock_name``).
      - dispatch-state operations (use ``dispatch_state_key``).
    """

    needed_role_label: str  # "prime-builder" or "loyal-opposition"
    harness_id: str  # "A", "B", etc. — durable identity from harness-identities.json
    command_handle: str  # "claude" / "codex" — from inverted harness-identities.json
    canonical_mode: str  # "pb" / "lo" — the canonical-init-keyword mode
    reviewer_precedence: int | None = None
    invocation_surfaces: dict[str, Any] | None = (
        None  # WI-3344: headless argv template from the harness-registry projection; None when the projection carries no record for this harness
    )

    @property
    def active_session_lock_name(self) -> str:
        """Target harness active-session lock file name.

        Per the existing suppression contract (VERIFIED at
        ``bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md``):
        receiver harnesses write ``active-{command_handle}-session.lock`` to
        signal foreground activity. Naming is unchanged from
        ``HEARTBEAT_LOCK_TEMPLATE``; only its construction is now derived
        from the resolved command handle rather than a hardcoded recipient
        map.
        """
        return HEARTBEAT_LOCK_TEMPLATE.format(role=self.command_handle)

    @property
    def dispatch_state_key(self) -> str:
        """Key used in ``dispatch-state.json`` recipients map."""
        return f"{self.needed_role_label}:{self.harness_id}"


class DispatchTargetNotReady(RuntimeError):
    """Raised when an active dispatch target exists but is temporarily unusable."""

    def __init__(self, reason: str, harness_id: str) -> None:
        super().__init__(reason)
        self.reason = reason
        self.harness_id = harness_id


_LABEL_TO_CANONICAL_MODE = {
    "prime-builder": "pb",
    "loyal-opposition": "lo",
}


def _reviewer_precedence_for_record(record: dict[str, object]) -> int:
    """Return deterministic LO reviewer order; missing or invalid sorts last."""
    try:
        return int(record.get("reviewer_precedence"))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 1_000_000


def _dispatch_target_evidence(target: DispatchTarget) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "recipient": target.dispatch_state_key,
        "needed_role_label": target.needed_role_label,
        "harness_id": target.harness_id,
        "command_handle": target.command_handle,
    }
    if target.reviewer_precedence is not None:
        evidence["reviewer_precedence"] = target.reviewer_precedence
    return evidence


def _evaluate_ollama_dispatch_readiness(project_root: Path) -> dict[str, Any]:
    """Evaluate ollama dispatch readiness. Backward compatible wrapper for tests monkeypatching."""
    helper_path = project_root / "scripts" / "verify_ollama_dispatch.py"
    if not helper_path.is_file():
        return {"ready": True}
    try:
        import importlib

        module = importlib.import_module("verify_ollama_dispatch")
        evaluate_fn = getattr(module, "evaluate_dispatch_readiness", None)
        if evaluate_fn is None:
            return {"ready": True}
        return evaluate_fn(project_root)
    except Exception as exc:
        raise RuntimeError(f"Failed to evaluate dispatch readiness for harness type 'ollama': {exc}") from exc


def _evaluate_harness_dispatch_readiness(harness_type: str, project_root: Path) -> dict[str, Any]:
    """Evaluate harness-specific dispatch substrate if a helper exists, fail-closed on errors, default to ready."""
    harness_type = str(harness_type or "").strip().lower()
    if not harness_type:
        return {"ready": True}

    if harness_type == "ollama":
        return _evaluate_ollama_dispatch_readiness(project_root)

    helper_path = project_root / "scripts" / f"verify_{harness_type}_dispatch.py"
    if not helper_path.is_file():
        return {"ready": True}

    try:
        import importlib  # noqa: PLC0415

        module_name = f"verify_{harness_type}_dispatch"
        module = importlib.import_module(module_name)  # noqa: PLC0415
        evaluate_fn = getattr(module, "evaluate_dispatch_readiness", None)
        if evaluate_fn is None:
            return {"ready": True}
        return evaluate_fn(project_root)
    except Exception as exc:
        raise RuntimeError(f"Failed to evaluate dispatch readiness for harness type {harness_type!r}: {exc}") from exc


def _harness_state_dir(project_root: Path) -> Path:
    return project_root / "harness-state"


def _read_role_assignments(project_root: Path) -> dict[str, Any]:
    """Return the harness role map sourced from the registry projection.

    WI-3342 IP-4: migrated from a direct read of the retired role mirror to
    the DB-backed registry
    projection ``harness-state/harness-registry.json``. The projection stores
    ``harnesses`` as a LIST; this function returns the legacy document shape
    ``{"harnesses": {harness_id: record}}`` so every consumer
    (``_resolve_dispatch_target``, ``_is_single_harness_topology``, the
    single-harness dispatcher's applicability gate) keeps working unchanged.
    Each record carries the full projection fields (``role``, ``harness_type``,
    ``invocation_surfaces``, ...). Raises ValueError on a missing or unreadable
    projection, so callers fail closed.
    """
    projection = load_harness_projection(project_root)
    harnesses = {
        str(record["id"]): record
        for record in projection.get("harnesses", [])
        if isinstance(record, dict) and record.get("id")
    }
    return {"harnesses": harnesses}


def _read_harness_identities(project_root: Path) -> dict[str, Any]:
    """Return the harness identity map sourced from the registry projection.

    WI-3342 IP-4: migrated from a direct read of
    ``harness-state/harness-identities.json`` to the DB-backed registry
    projection ``harness-state/harness-registry.json``. Returns the legacy
    document shape ``{"harnesses": {harness_name: {"id": harness_id}}}`` so
    ``_invert_identities`` and the single-harness dispatcher keep working
    unchanged. Raises ValueError on a missing or unreadable projection.
    """
    projection = load_harness_projection(project_root)
    harnesses = {
        str(record["harness_name"]): {"id": record["id"]}
        for record in projection.get("harnesses", [])
        if isinstance(record, dict) and record.get("harness_name") and record.get("id")
    }
    return {"harnesses": harnesses}


def _invert_identities(identities: dict[str, Any]) -> dict[str, str]:
    """Invert the projected harness identity map: harness ID -> command handle.

    Example fixture::

        {"harnesses": {"claude": {"id": "B"}, "codex": {"id": "A"}}}

    Returns::

        {"B": "claude", "A": "codex"}
    """
    return {info["id"]: name for name, info in identities["harnesses"].items()}


def _role_label_for_record(record: dict[str, Any]) -> str:
    raw = record.get("role")
    if isinstance(raw, str):
        return raw.strip().lower()
    if isinstance(raw, (list, tuple, set, frozenset)):
        normalized = sorted(str(role).strip().lower() for role in raw if str(role).strip())
        return "+".join(normalized)
    return ""


def _resolve_origin_identity(project_root: Path) -> tuple[str, str]:
    """Best-effort origin harness identity for quiesce scoping.

    Hook registrations do not pass an explicit harness argument. Prefer the
    durable harness env vars when present, fall back to common harness process
    indicators, then fail soft to ``unknown`` components. The quiesce key still
    includes session/event, so unknown origin does not affect dispatch safety.
    """
    env_harness_id = (
        os.environ.get("GTKB_HARNESS_ID") or os.environ.get("CODEX_HARNESS_ID") or os.environ.get("CLAUDE_HARNESS_ID")
    )
    env_harness_name = os.environ.get("GTKB_HARNESS_NAME")
    if not env_harness_name:
        if os.environ.get("CLAUDE_PROJECT_DIR"):
            env_harness_name = "claude"
        elif os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_HOME"):
            env_harness_name = "codex"

    try:
        identities = _read_harness_identities(project_root)
        name_to_id = {
            str(name): str(info.get("id"))
            for name, info in identities.get("harnesses", {}).items()
            if isinstance(info, dict) and info.get("id")
        }
    except ValueError:
        name_to_id = {}

    harness_id = str(env_harness_id or name_to_id.get(str(env_harness_name or ""), "") or "")
    role_label = ""
    if harness_id:
        try:
            role_map = _read_role_assignments(project_root)
            record = role_map.get("harnesses", {}).get(harness_id)
            if isinstance(record, dict):
                role_label = _role_label_for_record(record)
        except ValueError:
            role_label = ""

    return harness_id or "unknown", role_label or "unknown"


def _quiesce_key(
    *,
    project_root: Path,
    invocation_source: str,
    hook_context: dict[str, str] | None,
) -> str:
    session_id = _hook_context_value(hook_context, "session_id") or os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID", "")
    hook_event_name = _hook_context_value(hook_context, "hook_event_name") or invocation_source
    harness_id, role_label = _resolve_origin_identity(project_root)
    return f"{hook_event_name}:{session_id}:{harness_id}:{role_label}"


def _quiesce_marker(
    actionable_for_prime: list[Any],
    actionable_for_codex: list[Any],
    *,
    max_items: int,
) -> dict[str, Any]:
    prime_selected = _selected_oldest_first(
        [item for item in actionable_for_prime if getattr(item, "dispatchable", True)],
        max_items,
    )
    codex_selected = _selected_oldest_first(
        [item for item in actionable_for_codex if getattr(item, "dispatchable", True)],
        max_items,
    )
    return {
        "prime-builder": {
            "selected_count": len(prime_selected),
            "signature": _signature(prime_selected),
        },
        "loyal-opposition": {
            "selected_count": len(codex_selected),
            "signature": _signature(codex_selected),
        },
    }


def _record_can_receive_dispatch(h_info: dict[str, object]) -> bool:
    """True if a harness record can be a headless dispatch TARGET.

    Reads the honest ``can_receive_dispatch`` axis (FAB-01 / HYG-004), falling
    back to the deprecated ``event_driven_hooks`` alias for legacy / hand-built
    records (e.g. test fixtures) that predate the split. Both currently carry
    the same all-launchable-types value, so the fallback preserves behavior.
    """
    if "can_receive_dispatch" in h_info:
        return h_info.get("can_receive_dispatch") is True
    return h_info.get("event_driven_hooks") is True


def _record_can_fire_events(h_info: dict[str, object]) -> bool:
    """True if a harness record can FIRE bridge dispatch events (an event source).

    Reads the honest ``can_fire_events`` axis (FAB-01 / HYG-004), falling back to
    the deprecated ``event_driven_hooks`` alias for legacy / hand-built records
    that predate the split. The fallback intentionally over-includes (the legacy
    alias was always-true for launchable types) so legacy fixtures keep their
    prior behavior; honest callers run against projected records carrying the
    split field, where only hook-bearing harnesses (Claude Code, Codex CLI)
    report ``can_fire_events: true``.
    """
    if "can_fire_events" in h_info:
        return h_info.get("can_fire_events") is True
    return h_info.get("event_driven_hooks") is True


def _is_dispatch_ready(
    h_id: str,
    h_info: dict[str, object],
    project_root: Path,
    state_dir: Path | None,
    needed_role_label: str,
) -> bool:
    harness_type = str(h_info.get("harness_type") or "unknown").strip().lower()
    try:
        result = _evaluate_harness_dispatch_readiness(harness_type, project_root)
    except Exception as exc:  # noqa: BLE001
        if state_dir is not None:
            _record_dispatch_failure(
                state_dir,
                {
                    "dispatch_id": _now_iso() + f"-{harness_type}-dispatch-readiness",
                    "recipient": needed_role_label,
                    "harness_id": h_id,
                    "launched": False,
                    "reason": f"{harness_type}_dispatch_not_ready",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                },
            )
        return False
    if result.get("ready") is True:
        return True
    if state_dir is not None:
        _record_dispatch_failure(
            state_dir,
            {
                "dispatch_id": _now_iso() + f"-{harness_type}-dispatch-readiness",
                "recipient": needed_role_label,
                "harness_id": h_id,
                "launched": False,
                "reason": f"{harness_type}_dispatch_not_ready",
                "readiness": result,
            },
        )
    return False


def _resolve_dispatch_targets(
    needed_role_label: str,
    project_root: Path,
    state_dir: Path | None = None,
) -> list[DispatchTarget]:
    """Resolve which harnesses should receive work needing the given durable role.

    Allows multiple active harnesses per role concurrently. Returns a list of
    resolved DispatchTarget objects.
    """
    if needed_role_label not in _LABEL_TO_CANONICAL_MODE:
        raise ValueError(f"unknown role label: {needed_role_label!r}")
    mode = _LABEL_TO_CANONICAL_MODE[needed_role_label]

    role_map = _read_role_assignments(project_root)
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
    # Dispatch TARGET eligibility reads the receive axis (FAB-01 verification
    # plan: "_is_event_capable reads can_receive_dispatch"). A target must be
    # launchable/dispatchable; it does NOT need to fire events itself.
    active_matching = [
        (h_id, h_info) for h_id, h_info in role_matching if _is_active(h_info) and _record_can_receive_dispatch(h_info)
    ]
    if needed_role_label == "loyal-opposition":
        active_matching = sorted(
            active_matching,
            key=lambda item: (_reviewer_precedence_for_record(item[1]), str(item[0])),
        )

    if not active_matching:
        if state_dir is not None:
            inactive_ids = sorted(h_id for h_id, _ in role_matching)
            note = (
                f" (role-set members exist but none active and event-capable: {inactive_ids})" if inactive_ids else ""
            )
            _record_dispatch_failure(
                state_dir,
                {
                    "dispatch_id": _now_iso() + "-no-active-target",
                    "recipient": needed_role_label,
                    "launched": False,
                    "reason": "no_active_target_for_role",
                    "error_message": f"no active harness for role {needed_role_label!r}{note}",
                },
            )
        return []

    identities = _read_harness_identities(project_root)
    id_to_handle = _invert_identities(identities)

    from harness_projection_reader import load_harness_projection

    projection = load_harness_projection(project_root)

    resolved_targets = []
    for harness_id, role_record in active_matching:
        if harness_id not in id_to_handle:
            raise ValueError(
                f"harness-registry projection references harness ID {harness_id!r} not present in identity projection"
            )
        identity_handle = id_to_handle[harness_id]

        role_record_handle = role_record.get("harness_type")
        if role_record_handle is not None and role_record_handle != identity_handle:
            raise ValueError(
                f"drift detected: harness-registry projection harness_type={role_record_handle!r} "
                f"disagrees with harness-identities resolution to {identity_handle!r} "
                f"for harness ID {harness_id!r}"
            )

        invocation_surfaces: dict[str, Any] | None = None
        for record in projection.get("harnesses", []):
            if record.get("id") == harness_id:
                surfaces = record.get("invocation_surfaces")
                if isinstance(surfaces, dict):
                    invocation_surfaces = surfaces
                break

        resolved_targets.append(
            DispatchTarget(
                needed_role_label=needed_role_label,
                harness_id=harness_id,
                command_handle=identity_handle,
                canonical_mode=mode,
                reviewer_precedence=_reviewer_precedence_for_record(role_record)
                if needed_role_label == "loyal-opposition"
                else None,
                invocation_surfaces=invocation_surfaces,
            )
        )
    return resolved_targets


def _resolve_dispatch_target(
    needed_role_label: str,
    project_root: Path,
    state_dir: Path | None = None,
) -> DispatchTarget | None:
    """Resolve a single dispatch target for backward compatibility in tests.

    If multiple active targets exist, raises ValueError matching test assertions.
    """
    targets = _resolve_dispatch_targets(needed_role_label, project_root, state_dir)
    if not targets:
        return None
    if len(targets) > 1:
        ids_str = ", ".join(f"'{t.harness_id}'" for t in targets)
        raise ValueError(f"multiple active harnesses match role {needed_role_label!r}: {ids_str}")
    target = targets[0]
    role_map = _read_role_assignments(project_root)
    harnesses = role_map.get("harnesses", {})
    h_info = harnesses.get(target.harness_id) or {}
    harness_type = str(h_info.get("harness_type") or "unknown").strip().lower()
    if not _is_dispatch_ready(target.harness_id, h_info, project_root, state_dir, needed_role_label):
        raise DispatchTargetNotReady(f"{harness_type}_dispatch_not_ready", target.harness_id)
    return target


def check_target_active(target: DispatchTarget, state_dir: Path) -> bool:
    """Return True if the dispatch target's harness has a fresh active-session lock.

    Per IP-3b of bridge/gtkb-canonical-init-keyword-syntax-001-007.md (Codex
    GO at -008): the legacy ``_counterpart_role`` recipient-handle map has
    been removed; the lock file name is now derived from
    ``target.active_session_lock_name`` which uses
    ``HEARTBEAT_LOCK_TEMPLATE.format(role=target.command_handle)``. This
    preserves the existing active-session suppression contract (VERIFIED
    at bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md)
    end-to-end while enabling correct lock resolution under harness role-switch.

    Reads ``<state-dir>/<target.active_session_lock_name>`` and treats the
    target as active when:

    - The lock file exists, AND
    - Its mtime is within ``GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS``
      (default 120, matching the owner-stated value in
      ``DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09``).

    Locks older than the sanity TTL are treated as orphaned (the harness
    crashed without firing its Stop hook) and the function returns False.
    Locks that are unreadable due to OSError also return False (fail open
    rather than falsely suppress).
    """
    lock_path = state_dir / target.active_session_lock_name
    if not lock_path.exists():
        return False
    try:
        mtime = lock_path.stat().st_mtime
    except OSError:
        return False
    age_seconds = time.time() - mtime
    try:
        sanity_ttl = int(os.environ.get("GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS", "120"))
    except (TypeError, ValueError):
        sanity_ttl = 120
    if sanity_ttl <= 0:
        sanity_ttl = 120
    return age_seconds <= sanity_ttl


def check_counterpart_active(target: DispatchTarget, state_dir: Path) -> bool:
    """Compatibility wrapper for callers still using the legacy predicate name."""
    return check_target_active(target, state_dir)


def _spawn_harness(
    *,
    target: DispatchTarget,
    items: list[Any],
    project_root: Path,
    state_dir: Path,
    max_items: int,
    dry_run: bool,
    dispatch_id: str | None = None,
) -> dict[str, Any]:
    """Fire-and-forget dispatch a harness subprocess.

    Per IP-3b of bridge/gtkb-canonical-init-keyword-syntax-001-007.md
    (Codex GO at -008): takes a resolved ``DispatchTarget`` instead of a
    legacy ``recipient`` string. The target carries the durable role label,
    harness ID, command handle, and canonical mode required by downstream
    callers.

    The ``recipient`` field in returned meta dicts is preserved as
    ``target.dispatch_state_key`` (the durable role label) so dispatch logs
    record durable identity rather than legacy aliases.

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
    prompt = _dispatch_prompt(target, items, max_items)
    command = _harness_command(target, prompt, project_root)
    recipient_key = target.dispatch_state_key
    dispatch_id = dispatch_id or _new_dispatch_id(recipient_key)

    if command is None:
        meta = {
            "dispatch_id": dispatch_id,
            "recipient": recipient_key,
            "launched": False,
            "reason": "unknown_recipient",
        }
        _record_dispatch_failure(state_dir, meta)
        return meta

    if dry_run:
        return {
            "dispatch_id": dispatch_id,
            "recipient": recipient_key,
            "launched": False,
            "reason": "dry_run",
            "command_head": command[:2],
        }

    # WI-4472: hard global concurrency cap. Count live dispatched processes
    # before issuing any authorization packet or spawning; fail-closed (skip
    # the dispatch, logged) when at/over the cap. This bounds the hung-but-
    # launched class that the circuit breaker (launch-failure count only) and
    # active-session suppression (per-target liveness) both miss.
    runs_dir = state_dir / DISPATCH_RUNS_SUBDIR
    cap = _max_live_dispatched_processes()
    live_count = _count_live_dispatched_processes(runs_dir)
    if live_count >= cap:
        meta = {
            "dispatch_id": dispatch_id,
            "recipient": recipient_key,
            "launched": False,
            "reason": "concurrency_cap_reached",
            "live_count": live_count,
            "cap": cap,
        }
        _record_dispatch_failure(state_dir, meta)
        return meta

    packet_context: dict[str, Any] | None = None
    if target.needed_role_label == "prime-builder":
        selected = _selected_oldest_first(items, max_items)
        issue_result = _issue_dispatch_authorization_for_selected(
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

    # runs_dir is computed in the concurrency-cap gate above (WI-4472).
    runs_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = runs_dir / f"{dispatch_id}.stdout.log"
    stderr_path = runs_dir / f"{dispatch_id}.stderr.log"

    env = dict(os.environ)
    env["GTKB_PROJECT_ROOT"] = str(project_root)
    # Per Slice 4 D9b (Codex F1 on -006): the SessionStart hooks at
    # .claude/hooks/session_start_dispatch.py and .codex/gtkb-hooks/session_start_dispatch.py
    # enter bridge auto-dispatch mode (suppressing the normal startup disclosure
    # and treating the initial prompt as the dispatch task) only when
    # ``GTKB_BRIDGE_POLLER_RUN_ID`` is set on the child env. The retired smart
    # poller used to set this; with smart-poller archived in Slice 4, the
    # cross-harness trigger must set it itself or the dispatch chain breaks.
    # The env-var name is reused (cosmetic rename to GTKB_BRIDGE_TRIGGER_RUN_ID
    # is tracked as Open Follow-On 6 of slice-4 retirement).
    env["GTKB_BRIDGE_POLLER_RUN_ID"] = dispatch_id
    # Compatibility for bridge work-intent surfaces that predate the poller-run
    # variable. The shared resolver now prefers GTKB_BRIDGE_POLLER_RUN_ID, but
    # keeping the inherited session aligned prevents older worker surfaces from
    # claiming under a different id.
    env["GTKB_INHERITED_SESSION_ID"] = dispatch_id
    for key in IMPLEMENTATION_AUTH_ENV_VARS:
        env.pop(key, None)
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
    # Per IP-4 of bridge/gtkb-canonical-init-keyword-syntax-001-005.md
    # (Codex GO at -008): pass the canonical init-keyword to the spawned
    # harness's SessionStart hook via env var so the receiver-side
    # set-membership check has access to the keyword without parsing the
    # prompt at SessionStart time (Claude Code's SessionStart stdin does
    # not include user-prompt content; the prompt arrives at
    # UserPromptSubmit). The keyword itself remains the prompt's first
    # line for the receiving model's runtime interpretation; this env var
    # is the SessionStart-time companion that the hook reads as the
    # first-line signal per DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001.
    env["GTKB_BRIDGE_DISPATCH_KEYWORD"] = f"::init gtkb {target.canonical_mode}"
    # Per Codex F2 on -008: do NOT set GTKB_NO_CROSS_HARNESS_TRIGGER on the
    # child harness env. The signature-state file provides loop prevention
    # (unchanged signature → no spawn); blanket env var would also suppress
    # the legitimate reciprocal dispatch when the dispatched harness writes
    # a new bridge response that flips the counterpart's signature.
    # Explicitly strip in case the parent has it set:
    env.pop(LOOP_PREVENTION_ENV_VAR, None)
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    else:
        creationflags = 0

    selected = _selected_oldest_first(items, max_items)
    sig = _signature(selected)
    status_file_path = runs_dir / f"{dispatch_id}.exit_code"
    wrapped_command = [
        sys.executable,
        str(project_root / "scripts" / "run_with_status.py"),
        "--stdout",
        str(stdout_path),
        "--stderr",
        str(stderr_path),
    ]
    if target.command_handle == "antigravity":
        stdin_path = runs_dir / f"{dispatch_id}.stdin.log"
        try:
            stdin_path.write_text(prompt, encoding="utf-8")
        except OSError:
            pass
        wrapped_command.extend(["--stdin", str(stdin_path)])
    wrapped_command.append(str(status_file_path))
    wrapped_command += command

    meta: dict[str, Any] = {
        "dispatch_id": dispatch_id,
        "recipient": recipient_key,
        "launched_at": _now_iso(),
        "command_head": command[:2],
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "signature": sig,
        "needed_role_label": target.needed_role_label,
        "status_file_path": str(status_file_path),
    }
    try:
        try:
            process = subprocess.Popen(
                wrapped_command,
                cwd=str(project_root),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
                creationflags=creationflags,
            )
        except Exception as e:
            # Re-raise to be handled by the outer try-except block
            raise e
        meta.update({"launched": True, "pid": process.pid})
        # WI-4472: live-process accounting sidecar. Written only for a
        # successful launch; consumed by _count_live_dispatched_processes.
        try:
            (runs_dir / f"{dispatch_id}.pid").write_text(str(process.pid), encoding="utf-8")
        except OSError:
            pass
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


def _is_cross_harness_trigger_active_substrate(project_root: Path) -> bool:
    """Return True if cross_harness_trigger is the active substrate.

    Reads harness-state/bridge-substrate.json when present.
    If substrate is registered but not 'cross_harness_trigger', returns False.
    If file is missing or invalid, default to True (fail open for backwards compatibility).
    """
    path = project_root / "harness-state" / "bridge-substrate.json"
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                substrate = data.get("substrate")
                if substrate and substrate != "cross_harness_trigger":
                    return False
        except Exception:
            pass
    return True


def _record_substrate_mismatch_skip(state_dir: Path, active_substrate: str) -> None:
    """Write durable audit + dispatch-state evidence for the substrate mismatch skip."""
    ts = _now_iso()
    error_message = (
        f"Cross-harness trigger inert because the active bridge substrate is configured as {active_substrate!r} "
        "in harness-state/bridge-substrate.json."
    )
    for role_label in ("prime-builder", "loyal-opposition"):
        _record_dispatch_failure(
            state_dir,
            {
                "ts": ts,
                "dispatch_id": f"{ts}-{role_label}-substrate-mismatch",
                "recipient": role_label,
                "launched": False,
                "reason": "substrate_mismatch_inert",
                "error_message": error_message,
            },
        )


def _is_single_harness_topology(project_root: Path) -> bool:
    """Return True iff the role map records a single harness ID with both
    ``prime-builder`` AND ``loyal-opposition`` in its role-set AND that harness
    carries ``status == "active"`` AND ``event_driven_hooks is True``
    (DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 assertion 7 and v2 capability
    gate: single-harness mode requires an active event-capable harness).

    Per IP-8 of ``bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md``
    (Codex GO at ``-006``): the cross-harness trigger goes inert in
    single-harness topology because the single-harness bridge dispatcher
    (Slice 2 thread; Windows scheduled task substrate) is the active
    substrate when one harness holds a multi-element role-set.

    Fail-closed semantic: if the role map is unreadable, returns False so
    the gate is inactive and the trigger proceeds with its normal multi-
    harness path. This avoids accidental inertness on configuration drift.
    """
    try:
        role_map = _read_role_assignments(project_root)
    except ValueError:
        return False
    harnesses = role_map.get("harnesses", {})
    if not isinstance(harnesses, dict) or len(harnesses) != 1:
        return False
    ((_, record),) = harnesses.items()
    if not isinstance(record, dict):
        return False
    raw_role = record.get("role")
    if isinstance(raw_role, list):
        role_set = {str(r).strip().lower() for r in raw_role if isinstance(r, str)}
        has_both = "prime-builder" in role_set and "loyal-opposition" in role_set
        # DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 assertion 7 plus WI-4213:
        # single-harness mode is applicable only when the single harness is
        # status==active and event-capable. Missing/unknown status or missing/
        # false event capability -> not single-harness (the trigger then
        # proceeds on its normal multi-harness path, where the resolver finds
        # zero active event-capable target -> sentinel + audit).
        status = record.get("status")
        is_active = isinstance(status, str) and status.strip().lower() == "active"
        # Topology derivation reads the event-FIRING axis (FAB-01 verification
        # plan: "topology derivation reads can_fire_events"). A single-harness
        # operating mode is only meaningful when the lone harness can fire the
        # events that drive in-process dispatch; a receive-only harness is not
        # treated as an event source.
        is_event_capable = _record_can_fire_events(record)
        return has_both and is_active and is_event_capable
    return False


def _record_single_harness_topology_skip(state_dir: Path) -> None:
    """Write durable audit + dispatch-state evidence for the topology skip.

    Per ``SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`` § Coexistence: in
    single-harness topology the cross-harness trigger is registered but
    spawns nothing AND ``resolution fails with an audit-log entry``. This
    function preserves the audit-log invariant by recording the topology
    skip in BOTH durable surfaces:

    - ``<state-dir>/dispatch-failures.jsonl`` — one entry per role label
      (``prime-builder`` and ``loyal-opposition``), each with a SPEC-cited
      ``error_message``. Liveness diagnosis tools that read the failures
      log see explicit topology-skip evidence rather than inferring
      inertness from missing data.
    - ``<state-dir>/dispatch-state.json`` — per-recipient
      ``last_result = "single_harness_topology_not_applicable"`` records
      so ``--diagnose`` mode + doctor surface the skip without parsing
      the failures log.

    Per F1 of ``bridge/gtkb-single-harness-bridge-dispatcher-slice-2-004.md``
    closure in REVISED-2 (``-005``; Codex GO at ``-006``).
    """
    ts = _now_iso()
    error_message = (
        "Cross-harness trigger inert in single-harness topology per "
        "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 Coexistence clause. The "
        "single-harness bridge dispatcher is the active substrate when one "
        "harness ID holds a multi-element role-set."
    )
    for role_label in ("prime-builder", "loyal-opposition"):
        _record_dispatch_failure(
            state_dir,
            {
                "ts": ts,
                "dispatch_id": f"{ts}-{role_label}-topology-skip",
                "recipient": role_label,
                "launched": False,
                "reason": "single_harness_topology_not_applicable",
                "error_message": error_message,
            },
        )

    state = _load_dispatch_state(state_dir)
    recipients_state = state.get("recipients") if isinstance(state, dict) else {}
    if not isinstance(recipients_state, dict):
        recipients_state = {}
    recipients_state = _migrate_recipients_state_keys(recipients_state)
    for role_label in ("prime-builder", "loyal-opposition"):
        prior = recipients_state.get(role_label)
        if not isinstance(prior, dict):
            prior = {}
        prior["last_result"] = "single_harness_topology_not_applicable"
        prior["updated_at"] = ts
        recipients_state[role_label] = prior
    payload = {
        "schema_version": 1,
        "updated_at": ts,
        "recipients": recipients_state,
    }
    _write_dispatch_state(state_dir, payload)


def _cleanup_stale_tmp_files(state_dir: Path) -> None:
    """Clean up any *.tmp files in state_dir that are older than 5 minutes (300 seconds).

    Per Observability and Hygiene proposal: ensures concurrent active writes
    are not disrupted.
    """
    if not state_dir.is_dir():
        return
    now = time.time()
    for entry in state_dir.glob("*.tmp"):
        if not entry.is_file():
            continue
        try:
            mtime = entry.stat().st_mtime
            if now - mtime > 300:
                entry.unlink()
        except OSError:
            pass


def _process_pending_exit_codes(recipients_state: dict[str, Any], state_dir: Path) -> None:
    """Check prior launch status files and update signature state."""
    for recipient, recipient_state in list(recipients_state.items()):
        if not isinstance(recipient_state, dict):
            continue
        last_launch = recipient_state.get("last_launch")
        if not isinstance(last_launch, dict) or not last_launch.get("launched"):
            continue

        # If already processed, skip
        if last_launch.get("exit_code_processed"):
            continue

        dispatch_id = last_launch.get("dispatch_id")
        if not dispatch_id:
            continue

        runs_dir = state_dir / DISPATCH_RUNS_SUBDIR
        status_file = runs_dir / f"{dispatch_id}.exit_code"
        if not status_file.is_file():
            pid = last_launch.get("pid")
            if pid and not _pid_alive(pid):
                exit_code = 4294967295
            else:
                continue
        else:
            try:
                exit_code_str = status_file.read_text(encoding="utf-8").strip()
                exit_code = int(exit_code_str)
            except (ValueError, OSError):
                continue

        # Process the exit code
        launch_signature = last_launch.get("signature")
        # Mark exit code as processed in the state
        last_launch["exit_code"] = exit_code
        last_launch["exit_code_processed"] = True

        max_retries = _dispatch_max_retries()

        if exit_code == 0:
            # Success: keep signature state aligned for every recipient role.
            if launch_signature:
                recipient_state["last_dispatched_signature"] = launch_signature
                recipient_state["signature"] = launch_signature
                recipient_state["last_suppressed_signature"] = None

            # Reset failure count and circuit breaker
            recipient_state["failure_count"] = 0
            recipient_state["circuit_breaker_tripped"] = False
            recipient_state.pop("circuit_breaker_tripped_at", None)
            recipient_state.pop("circuit_breaker_half_open", None)
        else:
            # Failure!
            failure_count = recipient_state.get("failure_count", 0) + 1
            recipient_state["failure_count"] = failure_count
            if failure_count >= max_retries:
                recipient_state["circuit_breaker_tripped"] = True
                recipient_state["circuit_breaker_tripped_at"] = _now_iso()

            # Since it failed, write to dispatch failures log as well
            _record_dispatch_failure(
                state_dir,
                {
                    "ts": _now_iso(),
                    "dispatch_id": dispatch_id,
                    "recipient": recipient,
                    "launched": True,
                    "reason": "subprocess_execution_failed",
                    "exit_code": exit_code,
                    "failure_count": failure_count,
                    "circuit_breaker_tripped": recipient_state.get("circuit_breaker_tripped", False),
                },
            )


def run_trigger(
    *,
    project_root: Path,
    state_dir: Path,
    max_items: int = DEFAULT_MAX_ITEMS,
    dry_run: bool = False,
    invocation_source: str = "manual",
    hook_context: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Run one detection + dispatch cycle.

    Returns a summary dict. Always succeeds (fire-and-forget); errors during
    dispatch are surfaced via the per-recipient ``last_result`` field but the
    function returns normally.

    ``invocation_source`` (``"PostToolUse"`` / ``"Stop"`` / ``"manual"``)
    controls the quiesce gate. Only PostToolUse invocations are quiesced;
    Stop and manual reconciliation bypass quiesce and use the normal signature
    dedup path. ``hook_context`` is the fail-soft parsed hook stdin payload.
    """
    if os.environ.get(LOOP_PREVENTION_ENV_VAR) == "1":
        return {"skipped": True, "reason": "loop_prevention_env_var"}

    _cleanup_stale_tmp_files(state_dir)
    retention_result = _apply_runtime_evidence_retention(project_root, state_dir)

    # Substrate check: if cross_harness_trigger is not the active substrate,
    # record substrate mismatch skip and exit inertly.
    if not _is_cross_harness_trigger_active_substrate(project_root):
        active_substrate = "none"
        sub_path = project_root / "harness-state" / "bridge-substrate.json"
        if sub_path.is_file():
            try:
                active_substrate = json.loads(sub_path.read_text(encoding="utf-8")).get("substrate", "none")
            except Exception:
                pass
        _record_substrate_mismatch_skip(state_dir, active_substrate)
        return {"skipped": True, "reason": "substrate_mismatch_inert", "active_substrate": active_substrate}

    # Slice 1 of gtkb-operating-mode-transaction-001: drain any pending
    # mode-switch transactions BEFORE recipient resolution so a deferred
    # role/topology change takes effect for the dispatch target selection
    # below. Fail-soft per design: failures do not abort the trigger.
    try:
        from groundtruth_kb.mode_switch.pending import apply_pending as _apply_pending

        _apply_pending(project_root)
    except Exception:  # noqa: BLE001 - fail-soft per spec acceptance criterion #6
        pass

    # IP-8 of bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md
    # (Codex GO at -006): trigger is inert in single-harness topology per
    # SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 Coexistence clause. The
    # short-circuit records SPEC-required audit evidence (failures.jsonl +
    # dispatch-state.json per-recipient last_result) before exiting.
    if _is_single_harness_topology(project_root):
        _record_single_harness_topology_skip(state_dir)
        return {"skipped": True, "reason": "single_harness_topology_not_applicable"}

    # WI-3265 diagnostic instrumentation: capture the baseline at the start of
    # the normal (multi-harness) dispatch path. Observational only — these
    # locals never influence the dispatch decision. Per
    # bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md (Codex GO -004).
    _diag_start = time.monotonic()
    _diag_index_mtime = _path_mtime_iso(project_root / "bridge" / "INDEX.md")
    _diag_dispatch_state_mtime_pre = _path_mtime_iso(state_dir / DISPATCH_STATE_FILENAME)

    index_text = _read_index_live(project_root)
    _diag_index_signature_pre = hashlib.sha256(index_text.encode("utf-8")).hexdigest()
    actionable_for_prime, actionable_for_codex = _compute_actionable(index_text, project_root)

    quiesce_key = _quiesce_key(
        project_root=project_root,
        invocation_source=invocation_source,
        hook_context=hook_context,
    )
    if invocation_source == "PostToolUse":
        now_epoch = time.time()
        window_seconds = _quiesce_window_seconds()
        quiesce_state = _load_quiesce_state(state_dir)
        records = quiesce_state.get("records") if isinstance(quiesce_state, dict) else {}
        if not isinstance(records, dict):
            records = {}
        record = records.get(quiesce_key)
        marker = _quiesce_marker(
            actionable_for_prime,
            actionable_for_codex,
            max_items=max_items,
        )
        if isinstance(record, dict) and now_epoch < float(record.get("quiesce_until") or 0):
            records[quiesce_key] = {
                "last_postooluse_seen_at": now_epoch,
                "quiesce_until": now_epoch + window_seconds,
                "pending_quiesce_marker": marker,
            }
            _write_quiesce_state(
                state_dir,
                {
                    "schema_version": 1,
                    "updated_at": _now_iso(),
                    "records": records,
                },
            )
            return {
                "skipped": True,
                "reason": "quiesce_window_active",
                "quiesce_key": quiesce_key,
                "pending_quiesce_marker": marker,
            }

    state = _load_dispatch_state(state_dir, project_root)
    recipients_state = state.get("recipients") if isinstance(state, dict) else {}
    if not isinstance(recipients_state, dict):
        recipients_state = {}
    recipients_state = _migrate_recipients_state_keys(recipients_state, project_root)
    _process_pending_exit_codes(recipients_state, state_dir)

    # IP-3b: resolve dispatch targets from the durable role record. The
    # mapping from actionable-classification to needed-role is fixed:
    # NEW/REVISED → Loyal Opposition; GO/NO-GO → Prime Builder.
    # Build targets defensively: if resolution fails (drift, missing
    # identity entry, etc.), record the failure and skip that recipient
    # for this cycle without aborting the whole run.
    pending_by_target: list[tuple[DispatchTarget | None, list[Any], str, str | None, list[dict[str, Any]] | None]] = []

    role_map = _read_role_assignments(project_root)
    harnesses = role_map.get("harnesses", {})
    if not isinstance(harnesses, dict):
        harnesses = {}

    for _legacy_recipient, needed_role_label, items in (
        ("prime", "prime-builder", actionable_for_prime),
        ("codex", "loyal-opposition", actionable_for_codex),
    ):
        try:
            targets = _resolve_dispatch_targets(needed_role_label, project_root, state_dir)
        except ValueError as exc:
            # DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 assertion 3: config errors (drift, unknown label, missing identity)
            # raise; the caller records dispatch_target_resolution_failed.
            _record_dispatch_failure(
                state_dir,
                {
                    "dispatch_id": _now_iso() + "-resolve-fail",
                    "recipient": needed_role_label,
                    "launched": False,
                    "reason": "dispatch_target_resolution_failed",
                    "error_message": str(exc),
                },
            )
            pending_by_target.append((None, items, needed_role_label, "dispatch_target_resolution_failed", None))
            continue

        if not targets:
            # DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 assertion 2: zero-ACTIVE
            # sentinel. _resolve_dispatch_targets already emitted the
            # no_active_target_for_role audit record; do NOT double-record here.
            pending_by_target.append((None, items, needed_role_label, "no_active_target_for_role", None))
            continue

        if needed_role_label == "loyal-opposition":
            skipped_candidates: list[dict[str, Any]] = []
            selected_target: DispatchTarget | None = None
            for target in targets:
                h_info = harnesses.get(target.harness_id) or {}
                harness_type = str(h_info.get("harness_type") or "unknown").strip().lower()
                if not _is_dispatch_ready(target.harness_id, h_info, project_root, state_dir, needed_role_label):
                    reason = f"{harness_type}_dispatch_not_ready"
                    skip = _dispatch_target_evidence(target)
                    skip["reason"] = reason
                    skipped_candidates.append(skip)
                    pending_by_target.append((target, items, target.dispatch_state_key, reason, None))
                    continue
                target_max_items = _effective_max_items_for_target(target, max_items)
                selected_for_target = _selected_oldest_first(
                    [item for item in items if getattr(item, "dispatchable", True)],
                    target_max_items,
                )
                if selected_for_target and _should_refuse_self_review(
                    bridge_id=selected_for_target[0].document_name,
                    dispatched_harness_id=target.harness_id,
                    project_root=project_root,
                ):
                    reason = "author_meets_reviewer_refused"
                    skip = _dispatch_target_evidence(target)
                    skip["reason"] = reason
                    skipped_candidates.append(skip)
                    pending_by_target.append((target, items, target.dispatch_state_key, reason, None))
                    continue
                selected_target = target
                break
            if selected_target is None:
                pending_by_target.append(
                    (None, items, needed_role_label, "no_ready_target_for_role", skipped_candidates)
                )
            else:
                pending_by_target.append(
                    (selected_target, items, selected_target.dispatch_state_key, None, skipped_candidates)
                )
            continue

        if len(targets) > 1:
            ids_str = ", ".join(f"'{target.harness_id}'" for target in targets)
            error_message = f"multiple active harnesses match role {needed_role_label!r}: {ids_str}"
            _record_dispatch_failure(
                state_dir,
                {
                    "dispatch_id": _now_iso() + "-resolve-fail",
                    "recipient": needed_role_label,
                    "launched": False,
                    "reason": "dispatch_target_resolution_failed",
                    "error_message": error_message,
                },
            )
            pending_by_target.append((None, items, needed_role_label, "dispatch_target_resolution_failed", None))
            continue

        for target in targets:
            h_info = harnesses.get(target.harness_id) or {}
            harness_type = str(h_info.get("harness_type") or "unknown").strip().lower()
            if not _is_dispatch_ready(target.harness_id, h_info, project_root, state_dir, needed_role_label):
                pending_by_target.append(
                    (target, items, target.dispatch_state_key, f"{harness_type}_dispatch_not_ready", None)
                )
            else:
                pending_by_target.append((target, items, target.dispatch_state_key, None, None))

    results: dict[str, Any] = {}
    for target, items, recipient, failure_reason, fallback_skipped_candidates in pending_by_target:
        if target is None or failure_reason is not None:
            # Resolution produced no dispatch target (multi-active ValueError or
            # zero-active sentinel) or target is not ready. Reflect the per-recipient
            # last_result in dispatch-state.json per the DCL resolution table, then keep going.
            reason = failure_reason or "dispatch_target_resolution_failed"
            prior = recipients_state.get(recipient)
            recipient_state = dict(prior) if isinstance(prior, dict) else {}
            recipient_state["last_result"] = reason
            recipient_state["updated_at"] = _now_iso()
            result: dict[str, Any] = {"launched": False, "reason": reason}
            if target is not None:
                candidate = _dispatch_target_evidence(target)
                recipient_state["candidate"] = candidate
                result["candidate"] = candidate
            if fallback_skipped_candidates:
                recipient_state["fallback_skipped_candidates"] = fallback_skipped_candidates
                result["fallback_skipped_candidates"] = fallback_skipped_candidates
            recipients_state[recipient] = recipient_state
            results[recipient] = result
            continue

        target_max_items = _effective_max_items_for_target(target, max_items)
        # Filter by dispatchable per smart-poller-kind-aware-routing -009 §1.5.
        # Terminal-kind GO entries are not dispatched.
        filtered = [it for it in items if getattr(it, "dispatchable", True)]

        # Per Codex F1 on -008: sign the SELECTED dispatch batch (post-cap,
        # post-reverse-for-oldest-first), NOT the full filtered list. This
        # matches ``bridge_poller_runner._pending_signature(_selected_items_
        # for_prompt(filtered, max_items))`` byte-for-byte. Signing the full
        # list would let entries outside the cap flip the signature without
        # changing the dispatch payload, causing redundant dispatches.
        selected = _selected_oldest_first(filtered, target_max_items)
        signature = _signature(selected)

        # WI-4480 Slice A: observational dispatch-starvation telemetry. Reads
        # the already-computed (and signed) ``filtered``/``selected`` lists and
        # writes only to a separate ``starvation-telemetry.json``. It does NOT
        # mutate ``filtered``, ``selected``, ``signature``, dispatch-state's
        # signature-bearing fields, or any dispatch decision. Fail-safe by
        # construction: ``record_starvation`` swallows its own errors and the
        # call is exception-guarded so telemetry can never perturb dispatch.
        if record_starvation is not None:
            try:
                record_starvation(
                    recipient,
                    [it.document_name for it in filtered],
                    [it.document_name for it in selected],
                    project_root=project_root,
                    now_iso=_now_iso(),
                )
            except Exception:  # noqa: BLE001 - telemetry must never break dispatch
                pass

        prior = recipients_state.get(recipient) if isinstance(recipients_state.get(recipient), dict) else {}
        # Active-session suppression state model:
        # - last_dispatched_signature: dedup field. Slice 2 invariant —
        #   current_signature == last_dispatched_signature → "unchanged".
        # - last_suppressed_signature: retry-pending marker. Set when
        #   suppression fires; cleared when dispatch finally succeeds.
        # - signature (legacy): preserved for back-compat readers; updated
        #   ONLY on real dispatch.
        prior_legacy_signature = prior.get("signature") if isinstance(prior, dict) else None
        # Backward compatibility: pre-suppression dispatch-state.json files
        # have only the legacy `signature` field. Fall back to it as the
        # dedup signal when `last_dispatched_signature` is absent, so
        # rolling deployment does not produce duplicate dispatches for
        # already-handled entries. After the first run that takes the
        # dispatch branch, last_dispatched_signature is populated and the
        # fallback is no longer used for that recipient.
        prior_dispatched = (
            prior.get("last_dispatched_signature")
            if isinstance(prior, dict) and prior.get("last_dispatched_signature") is not None
            else prior_legacy_signature
        )
        prior_suppressed = prior.get("last_suppressed_signature") if isinstance(prior, dict) else None

        # Carry forward prior values; update conditionally per branch below.
        recipient_state: dict[str, Any] = {
            "signature_scope": "selected_dispatch_batch",
            "pending_count": len(filtered),
            "selected_count": len(selected),
            "raw_pending_count": len(items),
            "updated_at": _now_iso(),
            "last_dispatched_signature": prior_dispatched,
            "last_suppressed_signature": prior_suppressed,
            # Legacy field updated only on real dispatch; carry forward here.
            "signature": prior_legacy_signature,
            "failure_count": prior.get("failure_count", 0),
            "circuit_breaker_tripped": prior.get("circuit_breaker_tripped", False),
            "circuit_breaker_tripped_at": prior.get("circuit_breaker_tripped_at"),
        }
        if isinstance(prior, dict) and prior.get("circuit_breaker_half_open"):
            recipient_state["circuit_breaker_half_open"] = prior.get("circuit_breaker_half_open")
        if isinstance(prior, dict) and isinstance(prior.get("last_launch"), dict):
            recipient_state["last_launch"] = prior["last_launch"]

        if not selected:
            recipient_state["last_result"] = "no_pending_after_filter" if items else "no_pending"
            # Empty pending: keep legacy `signature` aligned to the empty
            # state for back-compat with Slice 2 readers (which expected
            # the field to track current signature, including empty).
            recipient_state["signature"] = signature
            results[recipient] = {"launched": False, "reason": recipient_state["last_result"]}
        else:
            leased_items = [it for it in selected if is_lease_held(it.document_name, state_dir=state_dir)]

            if len(leased_items) == len(selected):
                # Target-active suppression: all selected documents are
                # already leased by active target-side work. Record the
                # signature in the suppressed field (NOT the dispatched field)
                # so it remains retryable when the target exits. Do NOT update
                # legacy `signature`.
                recipient_state["last_suppressed_signature"] = signature
                recipient_state["last_result"] = TARGET_ACTIVE_SESSION_RESULT
                results[recipient] = {
                    "launched": False,
                    "reason": TARGET_ACTIVE_SESSION_RESULT,
                }
            else:
                dispatched_filtered = [
                    it for it in filtered if not is_lease_held(it.document_name, state_dir=state_dir)
                ]
                dispatched_selected = _selected_oldest_first(dispatched_filtered, target_max_items)
                dispatched_signature = _signature(dispatched_selected)
                spawn_items = dispatched_filtered
                dispatch_id: str | None = None
                work_intent_session_id: str | None = None
                acquired_work_intent_slugs: list[str] = []

                recipient_state["selected_count"] = len(dispatched_selected)
                recipient_state["pending_count"] = len(dispatched_filtered)

                if target.needed_role_label == "prime-builder" and dispatched_selected:
                    dispatch_id = _new_dispatch_id(target.dispatch_state_key)
                    work_intent_session_id = _work_intent_session_id(dispatch_id)
                    work_intent_filter = _filter_prime_selected_by_work_intent(
                        dispatched_selected,
                        project_root=project_root,
                        state_dir=state_dir,
                        recipient=recipient,
                        dispatch_id=dispatch_id,
                        session_id=work_intent_session_id,
                    )
                    recipient_state["work_intent_held_filtered_count"] = work_intent_filter["held_count"]
                    if not work_intent_filter["ok"]:
                        recipient_state["last_result"] = work_intent_filter["reason"]
                        results[recipient] = {
                            "launched": False,
                            "reason": work_intent_filter["reason"],
                            "dispatch_id": dispatch_id,
                            "work_intent_session_id": work_intent_session_id,
                        }
                        recipients_state[recipient] = recipient_state
                        continue
                    dispatched_selected = list(work_intent_filter["selected"])
                    dispatched_signature = _signature(dispatched_selected)
                    # _spawn_harness expects newest-first input and applies
                    # _selected_oldest_first itself before building the prompt.
                    spawn_items = list(reversed(dispatched_selected))
                    recipient_state["selected_count"] = len(dispatched_selected)

                if target.needed_role_label == "prime-builder" and not dispatched_selected:
                    recipient_state["last_result"] = "work_intent_already_held"
                    results[recipient] = {
                        "launched": False,
                        "reason": "work_intent_already_held",
                        "dispatch_id": dispatch_id,
                        "work_intent_session_id": work_intent_session_id,
                    }
                else:
                    previous_launch_failure = None
                    if prior_dispatched == dispatched_signature and isinstance(prior, dict):
                        previous_launch_failure = _detect_previous_launch_failure(
                            prior,
                            recipient=recipient,
                            signature=dispatched_signature,
                        )
                        if previous_launch_failure is not None:
                            _record_dispatch_failure(state_dir, previous_launch_failure)
                            recipient_state["previous_launch_failed"] = previous_launch_failure

                    if prior_dispatched == dispatched_signature and previous_launch_failure is None:
                        # Slice 2 dedup: this exact signature was already dispatched.
                        # Skip without spawning. Legacy `signature` stays in sync.
                        recipient_state["signature"] = dispatched_signature
                        recipient_state["last_result"] = "unchanged"
                        results[recipient] = {"launched": False, "reason": "unchanged"}
                    else:
                        # Dispatch path. Covers:
                        #   - first dispatch ever
                        #   - signature changed since last dispatch
                        #   - prior_suppressed == signature (retry after target exit)
                        retry_delay_seconds = _dispatch_retry_delay_seconds()
                        if recipient_state.get("circuit_breaker_tripped"):
                            if not _circuit_breaker_half_open_allowed(recipient_state, retry_delay_seconds):
                                recipient_state["last_result"] = "circuit_breaker_active"
                                results[recipient] = {
                                    "launched": False,
                                    "reason": "circuit_breaker_active",
                                }
                                recipients_state[recipient] = recipient_state
                                continue
                            recipient_state["circuit_breaker_half_open"] = True

                        is_retry_pending = recipient_state.get("failure_count", 0) > 0
                        is_delay_active = False

                        if is_retry_pending:
                            # WI-4459: re-baseline the retry-delay window on the last
                            # LAUNCH timestamp, not on ``updated_at``. ``updated_at`` is
                            # rewritten on every trigger evaluation - including the
                            # delay-only evaluations that ``continue`` below - so under
                            # continuous activity the elapsed window is always < the retry
                            # delay and the recipient is wedged forever (``failure_count``
                            # frozen at its first value, circuit breaker unreachable).
                            # ``last_launch.launched_at`` is written only on an actual
                            # launch attempt and is stable across delay-only evaluations.
                            prior_last_launch = prior.get("last_launch") if isinstance(prior, dict) else None
                            prior_launched_at = (
                                prior_last_launch.get("launched_at") if isinstance(prior_last_launch, dict) else None
                            )
                            if prior_launched_at:
                                try:
                                    launched_time = dt.datetime.fromisoformat(prior_launched_at.replace("Z", "+00:00"))
                                    elapsed = (dt.datetime.now(dt.UTC) - launched_time).total_seconds()
                                    if elapsed < retry_delay_seconds:
                                        is_delay_active = True
                                except Exception:
                                    pass
                            # No recorded launch while failure_count > 0 should not occur
                            # (failure_count increments only after a launch that sets
                            # last_launch); fail open to dispatch rather than wedge.
                            if recipient_state.get("circuit_breaker_half_open"):
                                is_delay_active = False

                        if is_delay_active:
                            recipient_state["last_result"] = "retry_delay_enforced"
                            results[recipient] = {
                                "launched": False,
                                "reason": "retry_delay_enforced",
                            }
                            recipients_state[recipient] = recipient_state
                            continue

                        if target.needed_role_label == "loyal-opposition" and dispatched_selected:
                            first_item = dispatched_selected[0]
                            if _should_refuse_self_review(
                                bridge_id=first_item.document_name,
                                dispatched_harness_id=target.harness_id,
                                project_root=project_root,
                            ):
                                recipient_state["last_result"] = "author_meets_reviewer_refused"
                                results[recipient] = {
                                    "launched": False,
                                    "reason": "author_meets_reviewer_refused",
                                }
                                recipients_state[recipient] = recipient_state
                                continue

                        # WI-4525 pre-spawn launchability gate. A static dispatch
                        # config defect (a hollow venv interpreter, an unresolvable
                        # argv head) must surface loudly HERE rather than spawning
                        # into a WinError-2 / exit-127 that the per-recipient
                        # circuit breaker then trips as if it were a transient (the
                        # masking failure mode of the 2026-06-13 dispatch jam).
                        # Reuses the same normalize+resolve logic the doctor
                        # launchability check (FAB-01 / HYG-001) uses, applied in
                        # the dispatch hot-path. Placed before the prime work-intent
                        # acquisition so an unlaunchable target acquires no claim and
                        # issues no authorization packet. Skipping the spawn means
                        # the post-dispatch failure path never runs, so failure_count
                        # is untouched and genuine-transient breaker semantics hold.
                        if not dry_run:
                            unlaunchable_head = _dispatch_target_argv_head(target)
                            if unlaunchable_head is not None and not _argv_head_launchable(
                                unlaunchable_head, project_root
                            ):
                                unlaunchable_meta = {
                                    "ts": _now_iso(),
                                    "dispatch_id": dispatch_id or _new_dispatch_id(target.dispatch_state_key),
                                    "recipient": target.dispatch_state_key,
                                    "launched": False,
                                    "reason": "target_unlaunchable",
                                    "argv_head": unlaunchable_head,
                                    "resolved_head": _normalize_argv_head(unlaunchable_head, project_root),
                                }
                                _record_dispatch_failure(state_dir, unlaunchable_meta)
                                recipient_state["last_result"] = "target_unlaunchable"
                                recipient_state["last_launch"] = unlaunchable_meta
                                results[recipient] = unlaunchable_meta
                                recipients_state[recipient] = recipient_state
                                continue
                        if target.needed_role_label == "prime-builder" and not dry_run:
                            if dispatch_id is None:
                                dispatch_id = _new_dispatch_id(target.dispatch_state_key)
                            if work_intent_session_id is None:
                                work_intent_session_id = _work_intent_session_id(dispatch_id)
                            acquire_result = _acquire_prime_work_intent_batch(
                                dispatched_selected,
                                project_root=project_root,
                                state_dir=state_dir,
                                recipient=recipient,
                                dispatch_id=dispatch_id,
                                session_id=work_intent_session_id,
                            )
                            if not acquire_result["ok"]:
                                recipient_state["last_result"] = acquire_result["reason"]
                                recipient_state["last_launch"] = {
                                    "dispatch_id": dispatch_id,
                                    "recipient": recipient,
                                    "launched": False,
                                    "reason": acquire_result["reason"],
                                    "work_intent_session_id": work_intent_session_id,
                                    "failed_slug": acquire_result.get("failed_slug"),
                                    "released_slugs": acquire_result.get("acquired_slugs", []),
                                }
                                results[recipient] = recipient_state["last_launch"]
                                recipients_state[recipient] = recipient_state
                                continue
                            acquired_work_intent_slugs = list(acquire_result["acquired_slugs"])
                        launch = _spawn_harness(
                            target=target,
                            items=spawn_items,
                            project_root=project_root,
                            state_dir=state_dir,
                            max_items=target_max_items,
                            dry_run=dry_run,
                            dispatch_id=dispatch_id,
                        )
                        if launch.get("launched") and not dry_run:
                            _post_dispatch_poll(
                                dispatch_id=dispatch_id or launch.get("dispatch_id") or "",
                                bridge_id=spawn_items[0].document_name if spawn_items else "",
                                dispatch_ts=time.time(),
                                project_root=project_root,
                                state_dir=state_dir,
                            )
                        if work_intent_session_id is not None:
                            launch["work_intent_session_id"] = work_intent_session_id
                        if acquired_work_intent_slugs:
                            launch["work_intent_slugs"] = acquired_work_intent_slugs
                        if (
                            target.needed_role_label == "prime-builder"
                            and acquired_work_intent_slugs
                            and not launch.get("launched")
                        ):
                            _release_prime_work_intents(
                                acquired_work_intent_slugs,
                                project_root=project_root,
                                session_id=work_intent_session_id or "",
                            )
                        recipient_state["last_result"] = "launched" if launch.get("launched") else "launch_failed"
                        recipient_state["last_launch"] = launch
                        if dry_run or launch.get("launched"):
                            recipient_state["last_suppressed_signature"] = None
                            recipient_state["last_dispatched_signature"] = dispatched_signature
                            recipient_state["signature"] = dispatched_signature
                        results[recipient] = launch

        selected_candidate = _dispatch_target_evidence(target)
        recipient_state["selected_candidate"] = selected_candidate
        if fallback_skipped_candidates:
            recipient_state["fallback_skipped_candidates"] = fallback_skipped_candidates
        if isinstance(results.get(recipient), dict):
            results[recipient]["selected_candidate"] = selected_candidate
            if fallback_skipped_candidates:
                results[recipient]["fallback_skipped_candidates"] = fallback_skipped_candidates
            results[target.needed_role_label] = results[recipient]
            recipients_state[target.needed_role_label] = recipient_state

        recipients_state[recipient] = recipient_state

    compat_recipients_state = dict(recipients_state)
    compat_results = dict(results)
    for key, val in list(recipients_state.items()):
        if ":" in key:
            role_label = key.split(":", 1)[0]
            if role_label not in compat_recipients_state:
                compat_recipients_state[role_label] = val
    for key, val in list(results.items()):
        if ":" in key:
            role_label = key.split(":", 1)[0]
            if role_label not in compat_results:
                compat_results[role_label] = val

    payload = {
        "schema_version": 1,
        "updated_at": _now_iso(),
        "recipients": compat_recipients_state,
    }
    _write_dispatch_state(state_dir, payload)

    if invocation_source == "PostToolUse":
        now_epoch = time.time()
        quiesce_state = _load_quiesce_state(state_dir)
        records = quiesce_state.get("records") if isinstance(quiesce_state, dict) else {}
        if not isinstance(records, dict):
            records = {}
        records[quiesce_key] = {
            "last_postooluse_seen_at": now_epoch,
            "quiesce_until": now_epoch + _quiesce_window_seconds(),
            "pending_quiesce_marker": None,
        }
        _write_quiesce_state(
            state_dir,
            {
                "schema_version": 1,
                "updated_at": _now_iso(),
                "records": records,
            },
        )

    # WI-3265 diagnostic instrumentation: emit one observational record per
    # recipient processed this invocation. The cross-harness trigger handles
    # two recipients per invocation with independent outcomes, so the GO'd
    # schema's per-recipient fields (classification, last_*_signature) are
    # realized as one record per recipient. Emission runs after dispatch state
    # is written and never alters the return value. Per
    # bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md (Codex GO -004).
    _diag_common = {
        "timestamp": _now_iso(),
        "invocation_source": invocation_source,
        "pid": os.getpid(),
        "session_id": _hook_context_value(hook_context, "session_id")
        or os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID", ""),
        "hook_event_name": _hook_context_value(hook_context, "hook_event_name"),
        "index_mtime": _diag_index_mtime,
        "index_signature_pre": _diag_index_signature_pre,
        "index_signature_post": hashlib.sha256(_read_index_live(project_root).encode("utf-8")).hexdigest(),
        "dispatch_state_mtime_pre": _diag_dispatch_state_mtime_pre,
        "dispatch_state_mtime_post": _path_mtime_iso(state_dir / DISPATCH_STATE_FILENAME),
        "elapsed_ms": int((time.monotonic() - _diag_start) * 1000),
    }
    for _diag_recipient in sorted(compat_results.keys()):
        if ":" in _diag_recipient:
            continue
        _diag_state = compat_recipients_state.get(_diag_recipient)
        if not isinstance(_diag_state, dict):
            _diag_state = {}
        _diag_last_result = str(_diag_state.get("last_result") or "")
        _emit_trigger_diagnostic(
            state_dir,
            {
                **_diag_common,
                "recipient": _diag_recipient,
                "last_result": _diag_last_result,
                "classification": _classify_invocation_outcome(_diag_last_result),
                "last_dispatched_signature": _diag_state.get("last_dispatched_signature"),
                "last_suppressed_signature": _diag_state.get("last_suppressed_signature"),
            },
        )
    return {"skipped": False, "results": compat_results, "dispatch_state": payload, "retention": retention_result}


def _classify_failure_record(record: dict[str, Any]) -> str:
    """Classify a dispatch-failures.jsonl record by error class.

    Per ``bridge/gtkb-cross-harness-trigger-windows-rename-race-001-003.md``:
    failure distribution must NOT be collapsed to a single error type.
    """
    msg = str(record.get("error_message") or "")
    if "WinError 32" in msg:
        return "WinError 32 (sharing violation)"
    if "WinError 5" in msg:
        return "WinError 5 (access denied)"
    if "WinError 2" in msg:
        return "WinError 2 (file not found)"
    if ".tmp" in msg and ("Permission" in msg or "denied" in msg.lower()):
        return "temp-path permission denied"
    return f"other ({record.get('error_type') or 'unknown'})"


def _read_dispatch_failure_records(state_dir: Path, *, include_rotated_failures: bool = False) -> list[dict[str, Any]]:
    paths = [state_dir / DISPATCH_FAILURES_FILENAME]
    if include_rotated_failures:
        paths.append(state_dir / f"{DISPATCH_FAILURES_FILENAME}.1")

    records: list[dict[str, Any]] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            raw = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in raw:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(rec, dict):
                records.append(rec)
    return records


def _emit_diagnose_summary(state_dir: Path, *, include_rotated_failures: bool = False) -> str:
    """Render a structured liveness summary; read-only.

    Sections:
      - Trigger infrastructure
      - Dispatch state
      - Per-recipient state
      - Failure distribution (NOT collapsed)
      - Liveness assessment per recipient
      - Overall verdict

    Per ``bridge/gtkb-cross-harness-trigger-windows-rename-race-001`` GO
    at ``-004``.
    """
    lines: list[str] = []
    lines.append(f"Cross-harness trigger diagnose — {_now_iso()}")
    lines.append("")

    try:
        project_root = _resolve_project_root(None)
    except Exception:
        project_root = None

    # Trigger infrastructure
    lines.append("== Trigger infrastructure ==")
    script_path = Path(__file__).resolve()
    lines.append(f"- Script: {script_path}")
    lines.append(f"- State dir: {state_dir}")
    lines.append("")

    # Dispatch state
    lines.append("== Dispatch state ==")
    state = _load_dispatch_state(state_dir, project_root)
    if not state:
        lines.append("- File: ABSENT (no dispatches recorded)")
        lines.append("")
        lines.append("== Overall ==")
        lines.append("- DEGRADED: dispatch-state.json absent (cold start or wiped state).")
        return "\n".join(lines)
    state_path = state_dir / DISPATCH_STATE_FILENAME
    lines.append(f"- File: {state_path}")
    updated_at = state.get("updated_at", "(missing)")
    lines.append(f"- Last update: {updated_at}")
    lines.append(f"- Schema version: {state.get('schema_version', '(missing)')}")
    lines.append("")

    # Per-recipient state
    lines.append("== Per-recipient state ==")
    recipients = state.get("recipients", {}) or {}
    if isinstance(recipients, dict):
        recipients, recipient_annotations = _diagnose_recipient_state(recipients, project_root)
    else:
        recipients = {}
        recipient_annotations = {}

    expected_keys: set[str] = set()
    if project_root is not None:
        try:
            role_map = _read_role_assignments(project_root)
            harnesses = role_map.get("harnesses", {})
            for h_id, h_info in harnesses.items():
                if isinstance(h_info, dict) and h_info.get("status") == "active":
                    raw = h_info.get("role")
                    if isinstance(raw, str):
                        roles = {raw.strip().lower()}
                    elif isinstance(raw, (list, tuple, set, frozenset)):
                        roles = {str(r).strip().lower() for r in raw}
                    else:
                        roles = set()
                    for r in roles:
                        expected_keys.add(f"{r}:{h_id}")
        except Exception:
            pass

    all_keys = sorted(set(recipients.keys()) | expected_keys)

    for name in all_keys:
        annotation = recipient_annotations.get(name, "")
        rec = recipients.get(name) or {}
        if not rec:
            display_name = name.split(":", 1)[0] if ":" in name else name
            lines.append(f"- {display_name}: (no state recorded){annotation}")
            continue
        sig = (rec.get("signature") or "")[:8]
        last_dispatched = (rec.get("last_dispatched_signature") or "")[:8] or "(none)"
        display_name = name.split(":", 1)[0] if ":" in name else name
        harness_suffix = f" (harness {name.split(':', 1)[1]})" if ":" in name else ""
        lines.append(
            f"- {display_name}: last_result={rec.get('last_result', '?')}, "
            f"pending={rec.get('pending_count', '?')}, "
            f"selected={rec.get('selected_count', '?')}{harness_suffix}{annotation}"
        )
        lines.append(f"  signature {sig}... last_dispatched={last_dispatched}...")

    lines.append("")

    # Failure distribution
    lines.append("== Recent failures ==")
    failures_path = state_dir / DISPATCH_FAILURES_FILENAME
    if not failures_path.is_file():
        lines.append("- dispatch-failures.jsonl absent (no failures recorded).")
    else:
        records = _read_dispatch_failure_records(
            state_dir,
            include_rotated_failures=include_rotated_failures,
        )
        total = len(records)
        if include_rotated_failures:
            lines.append(f"- Total in dispatch-failures.jsonl (current + rotated): {total}")
        else:
            lines.append(f"- Total in dispatch-failures.jsonl: {total}")
        # Distribution by error class — NOT collapsed.
        class_counts: dict[str, int] = {}
        last_ts_by_class: dict[str, str] = {}
        for rec in records:
            cls = _classify_failure_record(rec)
            class_counts[cls] = class_counts.get(cls, 0) + 1
            ts = str(rec.get("ts") or "")
            if ts and ts > last_ts_by_class.get(cls, ""):
                last_ts_by_class[cls] = ts
        for cls in sorted(class_counts, key=lambda k: -class_counts[k]):
            last_ts = last_ts_by_class.get(cls, "(unknown)")
            lines.append(f"  - {cls}: {class_counts[cls]} (last: {last_ts})")
    lines.append("")

    # Liveness assessment
    lines.append("== Liveness ==")
    overall_healthy = True
    for name in all_keys:
        annotation = recipient_annotations.get(name, "")
        rec = recipients.get(name) or {}
        sig = rec.get("signature") or ""
        last_dispatched = rec.get("last_dispatched_signature") or ""
        last_result = rec.get("last_result") or ""
        if not rec:
            lines.append(f"- {name}: (no liveness info; no state recorded){annotation}")
            overall_healthy = False
        elif last_result == "no_pending":
            lines.append(f"- {name}: idle (no actionable work).{annotation}")
        elif last_result == "no_pending_after_filter":
            lines.append(f"- {name}: idle (no dispatchable work after filtering).{annotation}")
        elif last_result == "single_harness_topology_not_applicable":
            lines.append(
                f"- {name}: inert (single-harness topology; cross-harness dispatch not applicable).{annotation}"
            )
        elif last_result in {TARGET_ACTIVE_SESSION_RESULT, LEGACY_COUNTERPART_ACTIVE_SESSION_RESULT}:
            lines.append(f"- {name}: suppressed (target active session detected; by design).{annotation}")
        elif sig == last_dispatched and sig:
            lines.append(f"- {name}: dispatched (signature matches last_dispatched).{annotation}")
        elif last_result == "unchanged":
            lines.append(f"- {name}: idempotent (signature unchanged from last successful dispatch).{annotation}")
        else:
            lines.append(f"- {name}: state={last_result or '?'} (no liveness rule matched).{annotation}")
            overall_healthy = False
    lines.append("")

    # Overall
    lines.append("== Overall ==")
    if overall_healthy:
        lines.append("- HEALTHY: dispatch state is current; recipients functioning per design.")
    else:
        lines.append("- DEGRADED: one or more recipients in an unrecognized state.")
    return "\n".join(lines)


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
        help=("Dispatch-state directory. Default: <project_root>/.gtkb-state/cross-harness-trigger/."),
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
        help=("Compute signatures and update dispatch-state but do NOT spawn the recipient harness."),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print the run summary to stdout (default: silent fire-and-forget).",
    )
    parser.add_argument(
        "--stop-hook",
        action="store_true",
        help=(
            "Stop-event hook mode. Runs trigger reconciliation as usual, then "
            "emits exactly '{}' (a parseable JSON object) to stdout and exits 0. "
            "Required for Codex Stop hook registrations per the OpenAI Codex "
            "hooks contract; also valid for Claude Stop hook registrations. "
            "Mutually exclusive with --verbose: when --stop-hook is set, --verbose "
            "is ignored so the JSON contract isn't violated by extra summary text."
        ),
    )
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help=(
            "Diagnostic mode. Emits a structured liveness summary to stdout and "
            "exits 0 WITHOUT performing dispatch or modifying state. Reports "
            "trigger infrastructure, dispatch state, per-recipient liveness, and "
            "failure distribution by error class (WinError 32 / 5 / 2 / temp-perm "
            "/ other) — NOT collapsed to a single error type. Per "
            "bridge/gtkb-cross-harness-trigger-windows-rename-race-001 GO at -004."
        ),
    )
    parser.add_argument(
        "--include-rotated-failures",
        action="store_true",
        help=(
            "In --diagnose mode, include dispatch-failures.jsonl.1 in the failure "
            "distribution. Default diagnose reads only the current segment."
        ),
    )
    parser.add_argument(
        "--reset-recipient",
        type=str,
        default=None,
        help="Clear circuit breakers/failure count for a recipient.",
    )
    parser.add_argument(
        "--post-dispatch-poll",
        action="store_true",
        help="Internal mode: poll for a just-dispatched bridge verdict and append dispatch-diagnostic-post.jsonl.",
    )
    parser.add_argument("--post-dispatch-id", type=str, default="")
    parser.add_argument("--post-dispatch-bridge-id", type=str, default="")
    parser.add_argument("--post-dispatch-timestamp", type=float, default=0.0)
    return parser


def _read_hook_context_from_stdin() -> dict[str, str] | None:
    """Read hook JSON payload from stdin without blocking manual invocations."""
    try:
        if sys.stdin.isatty():
            return None
        raw = sys.stdin.read()
    except Exception:  # noqa: BLE001 - hook payload parsing is fail-soft
        return None
    if not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    session_id = payload.get("session_id")
    hook_event_name = payload.get("hook_event_name")
    return {
        "session_id": session_id if isinstance(session_id, str) else "",
        "hook_event_name": hook_event_name if isinstance(hook_event_name, str) else "",
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Always returns 0 per fire-and-forget contract.

    Output behavior:
      - Default (no flags): silent stdout (fire-and-forget; hooks must not
        stall tool use).
      - ``--verbose``: prints the run summary as pretty-printed JSON.
      - ``--stop-hook``: prints exactly ``{}`` (parseable JSON object, no
        extra text) to stdout. Required by the OpenAI Codex Stop hook
        contract; also valid for Claude Stop. Overrides ``--verbose`` to
        avoid violating the JSON contract.
    """
    args = _build_argparser().parse_args(argv)
    hook_context = _read_hook_context_from_stdin()
    try:
        project_root = _resolve_project_root(args.project_root)
        if args.state_dir is not None:
            state_dir = args.state_dir.resolve()
        elif args.diagnose:
            state_dir = _resolve_diagnose_state_dir(project_root)
        else:
            state_dir = project_root.joinpath(*DEFAULT_STATE_SUBDIR)

        if args.post_dispatch_poll:
            if args.post_dispatch_id and args.post_dispatch_bridge_id and args.post_dispatch_timestamp > 0:
                _poll_and_log_verdict(
                    dispatch_id=args.post_dispatch_id,
                    bridge_id=args.post_dispatch_bridge_id,
                    dispatch_ts=args.post_dispatch_timestamp,
                    project_root=project_root,
                    state_dir=state_dir,
                )
            return 0

        if args.reset_recipient:
            state = _load_dispatch_state(state_dir, project_root)
            recipients_state = state.get("recipients") if isinstance(state, dict) else {}
            if not isinstance(recipients_state, dict):
                recipients_state = {}
            target_recipient = args.reset_recipient.strip()
            reset_count = 0
            for key in list(recipients_state.keys()):
                if key == target_recipient or key.startswith(target_recipient + ":"):
                    if isinstance(recipients_state[key], dict):
                        recipients_state[key]["failure_count"] = 0
                        recipients_state[key]["circuit_breaker_tripped"] = False
                        recipients_state[key]["updated_at"] = _now_iso()
                        reset_count += 1
            if reset_count > 0:
                state["recipients"] = recipients_state
                _write_dispatch_state(state_dir, state)
                if args.verbose or not args.stop_hook:
                    print(
                        f"Reset circuit breaker and failure count for recipient '{target_recipient}' (updated {reset_count} entries)."
                    )
            else:
                if args.verbose or not args.stop_hook:
                    print(f"No active entries found matching recipient '{target_recipient}'.")
            return 0

        if args.diagnose:
            # Diagnose mode: read-only liveness summary; no dispatch, no state mutation.
            print(_emit_diagnose_summary(state_dir, include_rotated_failures=args.include_rotated_failures))
            return 0
        summary = run_trigger(
            project_root=project_root,
            state_dir=state_dir,
            max_items=args.max_items,
            dry_run=args.dry_run,
            invocation_source=("Stop" if args.stop_hook else "PostToolUse"),
            hook_context=hook_context,
        )
        if args.stop_hook:
            # Codex Stop contract: exactly one parseable JSON object on stdout,
            # no extra text. {} is the minimal valid payload (current Codex
            # docs also accept exit 0 with empty stdout, but {} is clearer
            # for a deliberately Stop-specific mode).
            print("{}")
        elif args.verbose:
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
