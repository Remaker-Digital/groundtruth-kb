#!/usr/bin/env python3
"""
Claude Code / Codex Stop hook -- role-aware bridge active-session auto-drain.

WI-3359 -- bridge/gtkb-bridge-active-session-autodrain-005.md (Codex GO at -006).

When an interactive session ends a turn (Stop event) and there is
newly-actionable bridge work for the session's own durable operating role,
this hook emits a block decision so the session continues and drains that
work instead of going idle -- closing the owner-out-of-loop dispatch gap
(ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001) without an owner prompt.

Role-aware (GOV-HARNESS-ROLE-PORTABILITY-001): the hook resolves the active
session's durable harness identity (from the --harness arg supplied by the
hook registration) and operating role (from harness-state/role-assignments.json
via scripts/harness_roles.py), then selects actionability from that role -- a
prime-builder session drains GO/NO-GO Prime-actionable threads; a
loyal-opposition session drains NEW/REVISED LO-actionable threads; a harness
holding both roles drains the union. The hook is registered in both
.claude/settings.json and .codex/hooks.json; both registrations are role-safe
because the role is resolved at runtime, not hard-coded per vendor.

Detection: groundtruth_kb.bridge.notify.compute_actionable_pending is the
shared detection surface -- it returns the (prime-actionable, codex-actionable)
split; this hook selects by resolved role. The same function backs
.claude/hooks/bridge-axis-2-surface.py (the UserPromptSubmit Prime surface),
so the two surfaces cannot drift.

Bounding (runaway prevention):
- Signature-change gate: blocks only when the role-actionable signature has
  changed since the last drain (last_drained_signature in the per-session
  state file).
- Circuit breaker: a per-session cap on consecutive drain-blocks.
- Owner-decision deference: when an unresolved owner decision is pending in
  memory/pending-owner-decisions.md, the drain does not block -- for a pending
  decision of any age (WI-3363).
- Wrap-up-command deference: when the turn-ending owner message is a wrap-up
  command, the drain does not block (WI-3363).

Re-arm: before emitting a block the hook re-arms the active-session heartbeat
(active_session_heartbeat.py --mode tool-use) so the session-stop heartbeat --
which runs earlier in the Stop array -- cannot leave a stale-lock window for a
cross-harness dispatch race.

Fire-and-forget: always exits 0. Errors append to the state-dir errors log.

Stdin:  JSON Stop hook event payload.
Stdout: {} (allow stop) or {"decision": "block", "reason": ...} (drain).
Exit:   Always 0.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ENV_DISABLE = "GTKB_NO_BRIDGE_STOP_DRAIN"
CIRCUIT_BREAKER_CAP = 3

# WI-3363 IP-2: wrap-up-command deference. Local copy of the canonical
# WRAPUP_TRIGGER_COMMANDS tuple in scripts/session_self_initialization.py --
# copied rather than imported to avoid loading that large startup module into
# this per-turn-end hook. test_bridge_stop_drain.py carries a drift-guard test
# that imports the canonical tuple and asserts byte-equality with this copy.
WRAPUP_TRIGGER_COMMANDS = (
    "wrap up",
    "wrap up this session",
    "session wrap-up",
    "run session wrap-up",
    "close this session",
    "end this session",
    "new session",
    "fresh session",
    "start a new session",
    "start a fresh session",
    "begin a new session",
    "begin a fresh session",
    "open a new session",
    "prepare a new session",
    "initialize a new session",
    "start fresh",
    "begin fresh",
)

PROJECT_ROOT = Path(
    os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2]
).resolve()

STATE_DIR_REL = ".gtkb-state/bridge-poller/stop-drain"
ERRORS_LOG_REL = ".gtkb-state/bridge-poller/stop-drain/errors.jsonl"
PENDING_DECISIONS_REL = "memory/pending-owner-decisions.md"
HEARTBEAT_STATE_DIR_REL = ".gtkb-state/bridge-poller"

ROLE_PRIME = "prime-builder"
ROLE_LO = "loyal-opposition"


def _now() -> datetime:
    return datetime.now(UTC)


def _now_iso() -> str:
    return _now().isoformat().replace("+00:00", "Z")


def _log_error(project_root: Path, payload: dict[str, Any]) -> None:
    """Append a diagnostic record; best-effort, never raises."""
    try:
        log_path = project_root / ERRORS_LOG_REL
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({**payload, "ts": _now_iso()}) + "\n")
    except Exception:
        pass


def _bootstrap_sys_path(project_root: Path) -> None:
    """Make scripts/ and groundtruth-kb/src importable regardless of how the
    hook is invoked -- a bare hook command, importlib loading in tests, or
    ``python -m``."""
    for rel in ("scripts", "groundtruth-kb/src"):
        path = project_root / rel
        if path.is_dir() and str(path) not in sys.path:
            sys.path.insert(0, str(path))


def _resolve_roles(project_root: Path, harness_name: str) -> set[str]:
    """Resolve the durable operating-role set for the named harness.

    The harness identity (claude/codex/...) is supplied by the hook
    registration; the role is read from harness-state/role-assignments.json
    via scripts/harness_roles.py. Returns an empty set when the role cannot
    be resolved -- the caller fails closed (does not block) in that case.
    """
    try:
        import harness_roles  # type: ignore
    except Exception as exc:
        _log_error(project_root, {"event": "harness_roles_unavailable", "error": str(exc)})
        return set()
    try:
        resolved_id = harness_roles.resolved_harness_id(project_root, harness_name=harness_name)
        if not resolved_id:
            return set()
        document = harness_roles.load_role_assignments(project_root)
        record = (document.get("harnesses") or {}).get(resolved_id)
        if not isinstance(record, dict):
            return set()
        roles: set[str] = set()
        if harness_roles.is_prime_builder(record):
            roles.add(ROLE_PRIME)
        if harness_roles.is_loyal_opposition(record):
            roles.add(ROLE_LO)
        return roles
    except Exception as exc:
        _log_error(project_root, {"event": "role_resolution_failed", "error": str(exc)})
        return set()


def _compute_actionable(project_root: Path, roles: set[str]) -> tuple[str, list[Any]]:
    """Return (signature, role-actionable items) for the given role set.

    Uses groundtruth_kb.bridge.notify.compute_actionable_pending -- the same
    shared detection surface bridge-axis-2-surface.py uses -- which returns the
    (prime-actionable, codex-actionable) split. A prime-builder role selects
    the prime list; a loyal-opposition role selects the codex list; both roles
    select the de-duplicated union. The signature is a SHA-256 of the
    normalized item list, byte-compatible with the cross-harness trigger's
    signature scheme. Degrades to ("", []) -- silent no-op -- on any failure.
    """
    index_path = project_root / "bridge" / "INDEX.md"
    if not index_path.is_file():
        return "", []
    try:
        index_text = index_path.read_text(encoding="utf-8")
        from groundtruth_kb.bridge.detector import parse_index  # type: ignore
        from groundtruth_kb.bridge.notify import compute_actionable_pending  # type: ignore
        parse_result = parse_index(index_text, project_root=project_root)
        actionable_prime, actionable_codex = compute_actionable_pending(
            parse_result, project_root=project_root
        )
    except Exception as exc:
        _log_error(project_root, {"event": "actionable_detection_failed", "error": str(exc)})
        return "", []

    selected: list[Any] = []
    seen: set[str] = set()
    role_lists = []
    if ROLE_PRIME in roles:
        role_lists.append(actionable_prime)
    if ROLE_LO in roles:
        role_lists.append(actionable_codex)
    for items in role_lists:
        for item in items:
            key = f"{item.document_name}\x00{item.top_status}\x00{item.top_file}"
            if key not in seen:
                seen.add(key)
                selected.append(item)

    normalized = [
        {
            "document_name": item.document_name,
            "top_status": item.top_status,
            "top_file": item.top_file,
        }
        for item in selected
    ]
    raw = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    signature = hashlib.sha256(raw.encode("utf-8")).hexdigest() if selected else ""
    return signature, selected


_PENDING_BLOCK_RE = re.compile(r"^- id:\s*(DECISION-\S+)\s*$", re.MULTILINE)
_STATUS_RE = re.compile(r"^\s*status:\s*(\S+)\s*$", re.MULTILINE)


def _owner_decision_pending(project_root: Path) -> bool:
    """True when memory/pending-owner-decisions.md carries any unresolved owner
    decision.

    Defence rationale: an unresolved owner decision is itself a
    do-not-autonomously-drain signal -- if the session is ending while the
    owner still owes a decision, the drain must not pile "drain this bridge
    work" context on top of the owner-decision path. Deference applies to ANY
    unresolved decision regardless of its age (WI-3363): an earlier 30-minute
    recency window narrowed the deference the autodrain -005 proposal
    specified, so the drain fired over older-but-still-pending decisions. Fails
    open (returns False) when the file is absent or unparseable -- the drain
    stays bounded by its other gates, so a parse failure does not strand work.
    """
    path = project_root / PENDING_DECISIONS_REL
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return False
    # Split into per-decision blocks on the "- id: DECISION-NNNN" boundary.
    boundaries = [m.start() for m in _PENDING_BLOCK_RE.finditer(text)]
    if not boundaries:
        return False
    boundaries.append(len(text))
    for i in range(len(boundaries) - 1):
        block = text[boundaries[i]:boundaries[i + 1]]
        status_match = _STATUS_RE.search(block)
        status = (status_match.group(1).strip().lower() if status_match else "")
        if status != "resolved":
            # Any unresolved decision suppresses the drain, regardless of age.
            return True
    return False


def _read_transcript_tail(path: Path, max_events: int = 400) -> list[dict[str, Any]]:
    """Read the last N JSONL events from a Claude Code transcript file.

    Memory-bounded: transcripts can be MB-scale. Corrupt or truncated lines
    are skipped. Returns events in file order (oldest first within the tail).
    Mirrors the transcript-tail reader in owner-decision-tracker.py.
    """
    try:
        if not path.is_file():
            return []
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return []
    tail = lines[-max_events:] if len(lines) > max_events else lines
    events: list[dict[str, Any]] = []
    for line in tail:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            events.append(obj)
    return events


def _last_user_message_text(events: list[dict[str, Any]]) -> str:
    """Return the text of the most recent real owner message in the transcript.

    Scans backwards for the last ``type == "user"`` event whose content is a
    genuine owner message -- a plain string, or a content list led by a
    non-tool_result part. Tool-result continuations from agent loops also have
    ``type == "user"`` but are led by a tool_result part and are skipped.
    Returns "" when no real owner message is found. Mirrors the turn-boundary
    detection in owner-decision-tracker.py.
    """
    for ev in reversed(events):
        if ev.get("type") != "user":
            continue
        content = (ev.get("message") or {}).get("content")
        if isinstance(content, str):
            if content.strip():
                return content
            continue
        if isinstance(content, list) and content:
            first = content[0]
            if not isinstance(first, dict) or first.get("type") == "tool_result":
                continue
            text = first.get("text")
            if isinstance(text, str) and text.strip():
                return text
    return ""


def _normalize_wrapup_candidate(text: str) -> str:
    """Normalize a candidate command for wrap-up matching: lowercase, collapse
    whitespace, drop trailing punctuation, and drop an optional leading or
    trailing "please" -- the tolerance the startup disclosure documents for
    wrap-up commands."""
    norm = " ".join(text.strip().lower().split()).rstrip(".!?").strip()
    if norm.startswith("please "):
        norm = norm[len("please "):]
    if norm.endswith(" please"):
        norm = norm[: -len(" please")]
    return norm.rstrip(".!?").strip()


def _ended_on_wrapup_command(transcript_path: str | None) -> bool:
    """True when the turn-ending owner message is a wrap-up command.

    Reads the Stop-event transcript, extracts the last real owner message,
    normalizes it, and matches it against WRAPUP_TRIGGER_COMMANDS. Fails open
    (returns False) on any problem -- an unset/missing transcript path, an
    unreadable or unparseable transcript, or no owner message found -- so the
    hook then proceeds through its other gates exactly as before.
    """
    if not transcript_path:
        return False
    try:
        events = _read_transcript_tail(Path(transcript_path))
        if not events:
            return False
        candidate = _normalize_wrapup_candidate(_last_user_message_text(events))
        return bool(candidate) and candidate in WRAPUP_TRIGGER_COMMANDS
    except Exception as exc:  # fail open: never block the stop on a parse error
        _log_error(PROJECT_ROOT, {"event": "wrapup_check_failed", "error": str(exc)})
        return False


def _read_state(state_path: Path) -> dict[str, Any]:
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _write_state(project_root: Path, state_path: Path, payload: dict[str, Any]) -> None:
    """Atomic write via temp + rename; best-effort."""
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = state_path.with_name(f"{state_path.name}.{uuid.uuid4().hex[:8]}.tmp")
        tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        tmp.replace(state_path)
    except Exception as exc:
        _log_error(project_root, {"event": "state_write_failed", "error": str(exc)})


def _rearm_heartbeat(project_root: Path, harness_name: str) -> None:
    """Re-arm the active-session heartbeat so the session-stop heartbeat (which
    runs earlier in the Stop array) cannot leave a stale-lock window for a
    cross-harness dispatch race against this draining session. Best-effort."""
    script = project_root / "scripts" / "active_session_heartbeat.py"
    if not script.is_file():
        return
    try:
        subprocess.run(
            [
                sys.executable,
                str(script),
                "--mode",
                "tool-use",
                "--role",
                harness_name,
                "--state-dir",
                str(project_root / HEARTBEAT_STATE_DIR_REL),
            ],
            cwd=str(project_root),
            capture_output=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:
        _log_error(project_root, {"event": "heartbeat_rearm_failed", "error": str(exc)})


def _render_reason(items: list[Any]) -> str:
    """Render the block reason -- the surfaced actionable bridge work."""
    lines = [
        "Bridge active-session auto-drain (WI-3359): newly-actionable bridge "
        "work is pending for this session's role. Draining it now rather than "
        "going idle (the owner is out of the loop).",
        "",
    ]
    for item in items[:10]:
        lines.append(f"- {item.top_status}: {item.document_name} ({item.top_file})")
    if len(items) > 10:
        lines.append(f"- ... {len(items) - 10} more (see bridge/INDEX.md)")
    return "\n".join(lines)


def _resolve_session_id(payload: dict[str, Any]) -> str:
    sid = str(payload.get("session_id") or "").strip()
    if sid:
        return "".join(c for c in sid if c.isalnum() or c in ("-", "_"))[:64] or "default"
    return "default"


def drain_decision(
    project_root: Path,
    harness_name: str,
    session_id: str,
    transcript_path: str | None = None,
) -> dict[str, Any]:
    """Core role-aware drain decision. Returns the Stop-hook output dict:
    ``{}`` to allow the stop, or ``{"decision": "block", "reason": ...}`` to
    drain. Pure of stdin parsing so tests can drive it directly."""
    roles = _resolve_roles(project_root, harness_name)
    if not roles:
        # Fail closed: an unresolvable role must not block the stop.
        return {}

    signature, items = _compute_actionable(project_root, roles)
    if not signature or not items:
        return {}

    state_path = project_root / STATE_DIR_REL / f"{session_id}.json"
    state = _read_state(state_path)
    consecutive = int(state.get("consecutive_blocks") or 0)

    # Owner-decision deference: do not pile drain context on the owner-decision
    # path. (Checked before the signature gate so a deferral does not consume
    # the signature.)
    if _owner_decision_pending(project_root):
        state["last_result"] = "deferred_owner_decision"
        state["updated_at"] = _now_iso()
        _write_state(project_root, state_path, state)
        return {}

    # Wrap-up-command deference (WI-3363 IP-2): when the owner ended the turn
    # with a wrap-up command they are deliberately ending the session, not
    # going idle -- the drain must not block that turn-end. Checked before the
    # signature gate so a deferral does not consume the actionable signature.
    if _ended_on_wrapup_command(transcript_path):
        state["last_result"] = "deferred_wrap_up_command"
        state["updated_at"] = _now_iso()
        _write_state(project_root, state_path, state)
        return {}

    # Signature-change gate: unchanged role-actionable work does not re-block.
    if signature == str(state.get("last_drained_signature") or ""):
        state["last_result"] = "unchanged_no_reblock"
        state["consecutive_blocks"] = 0
        state["updated_at"] = _now_iso()
        _write_state(project_root, state_path, state)
        return {}

    # Circuit breaker: cap consecutive drain-blocks to prevent runaway.
    if consecutive >= CIRCUIT_BREAKER_CAP:
        state["last_result"] = "circuit_breaker_tripped"
        state["consecutive_blocks"] = 0
        state["last_drained_signature"] = signature
        state["updated_at"] = _now_iso()
        _write_state(project_root, state_path, state)
        return {}

    # Drain: re-arm the heartbeat, record state, emit the block.
    _rearm_heartbeat(project_root, harness_name)
    state["last_drained_signature"] = signature
    state["consecutive_blocks"] = consecutive + 1
    state["last_result"] = "blocked_drain"
    state["roles"] = sorted(roles)
    state["updated_at"] = _now_iso()
    _write_state(project_root, state_path, state)
    return {"decision": "block", "reason": _render_reason(items)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Role-aware bridge Stop-event auto-drain.")
    parser.add_argument(
        "--harness",
        default="claude",
        help="Durable harness name this registration runs in (claude / codex / ...).",
    )
    args = parser.parse_args(argv)

    output: dict[str, Any] = {}
    try:
        if os.environ.get(ENV_DISABLE) == "1":
            output = {}
        else:
            try:
                stdin_text = sys.stdin.read()
            except Exception:
                stdin_text = ""
            try:
                payload = json.loads(stdin_text or "{}")
            except json.JSONDecodeError:
                payload = {}
            safe_payload = payload if isinstance(payload, dict) else {}
            session_id = _resolve_session_id(safe_payload)
            transcript_path = str(safe_payload.get("transcript_path") or "") or None
            _bootstrap_sys_path(PROJECT_ROOT)
            output = drain_decision(
                PROJECT_ROOT, args.harness, session_id, transcript_path
            )
    except Exception as exc:
        _log_error(PROJECT_ROOT, {"event": "handler_crashed", "error": str(exc)})
        output = {}

    sys.stdout.write(json.dumps(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
