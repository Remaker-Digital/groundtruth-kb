#!/usr/bin/env python3
"""
Claude Code UserPromptSubmit hook — Bridge AXIS 2 in-session surface.

Closes the AXIS 2 (non-dispatchable, interactive notification) cross-harness
gap called out in .claude/rules/bridge-essential.md § Two-Axis Bridge
Automation Model. When an interactive Claude session is active, the
cross-harness event-driven trigger from Codex correctly suppresses headless
spawn (per gtkb-cross-harness-trigger-active-session-suppression-001 VERIFIED)
but offers no notification path into the running session. This hook closes
that gap by surfacing newly-actionable Prime bridge work into the session's
next prompt as additionalContext.

Authority:
- bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md REVISED-2
- bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-006.md Codex GO
- Specific AskUserQuestion approval S341 (2026-05-11): "Approve adding a new
  Claude-side bridge automation (UserPromptSubmit hook for AXIS 2 in-session
  bridge surfacing)?" → "Approve" (satisfies .claude/rules/bridge-essential.md
  :148-154 specific-approval requirement).

Behavior:
1. Read live bridge/INDEX.md and .gtkb-state/bridge-poller/dispatch-state.json.
2. Compute Prime-actionable signature using groundtruth_kb.bridge canonical
   parse_index + compute_actionable_pending (byte-identical to
   scripts/cross_harness_bridge_trigger.py:_signature).
3. Read session-scoped surface cache at
   .gtkb-state/bridge-poller/axis-2-surface/<session-id>.json.
4. If current_signature != last_surfaced_signature AND selected_count > 0:
   emit additionalContext markdown block; update cache atomically.
5. Otherwise: silent no-op.

Suppression:
- Owner keyword "dismiss bridge surface" in prompt → mark current signature
  dismissed in cache; suppresses re-surface of the same signature.
- Env var GTKB_NO_AXIS_2_SURFACE=1 → hook no-ops immediately (emergency stop).

Fire-and-forget: always exits 0. Errors append to
.gtkb-state/bridge-poller/axis-2-surface/errors.jsonl for diagnosis.

Stdin:  JSON hook event payload per https://code.claude.com/docs/en/hooks
Stdout: empty (silent no-op) or markdown additionalContext block.
Exit:   Always 0.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ENV_DISABLE = "GTKB_NO_AXIS_2_SURFACE"
DISMISS_KEYWORD = "dismiss bridge surface"

PROJECT_ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2]).resolve()

# Slice 4: the shared session-role resolver (scripts/session_role_resolution.py)
# lives under PROJECT_ROOT/scripts; ensure it is importable from this hook.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Role-profile constants mirror scripts.session_role_resolution; redefined here
# so the surface heading and element selection do not depend on the resolver
# import succeeding (the role default is Prime on resolver failure).
ROLE_PRIME = "prime-builder"
ROLE_LO = "loyal-opposition"
_ROLE_HEADING = {
    ROLE_PRIME: "Prime",
    ROLE_LO: "Loyal Opposition",
}

STATE_DIR_REL = ".gtkb-state/bridge-poller/axis-2-surface"
DISPATCH_STATE_REL = ".gtkb-state/bridge-poller/dispatch-state.json"
ERRORS_LOG_REL = ".gtkb-state/bridge-poller/axis-2-surface/errors.jsonl"
# Session-id env-var membership is owned by scripts/gtkb_session_id.py
# (WI-4270 shared resolver unification; bridge/gtkb-session-id-shared-resolver-
# unification-003 GO at -004). Import the canonical bridge work-intent order;
# fail soft to a verbatim local copy so this UserPromptSubmit hook never throws
# on a partial install. The drift-lock test
# platform_tests/scripts/test_gtkb_session_id.py + the axis-2 work-intent test
# lock this fallback to the canonical BRIDGE_WORK_INTENT_ORDER.
try:
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER as WORK_INTENT_SESSION_ENV_VARS
except Exception:  # pragma: no cover - hook fail-soft fallback for partial installs
    WORK_INTENT_SESSION_ENV_VARS = (
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "ANTIGRAVITY_SESSION_ID",
        "GTKB_SESSION_ID",
    )


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _log_error(payload: dict[str, Any]) -> None:
    """Append a diagnostic record to errors.jsonl. Best-effort; silent on failure."""
    try:
        log_path = PROJECT_ROOT / ERRORS_LOG_REL
        log_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {**payload, "ts": _now_iso()}
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload) + "\n")
    except Exception:
        # The hook must never crash the agent. Errors-logging failures are
        # silenced; the absence of an entry is itself diagnostic context if
        # the user reports surfaces aren't appearing.
        pass


def _compute_actionable_for_role(role_profile: str) -> tuple[str, list[Any]]:
    """Return (signature, actionable_items) for the resolved session role.

    Per Slice 4 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE: the AXIS 2
    surface follows the session-stated role. ``compute_actionable_pending``
    returns ``(actionable_for_prime, actionable_for_codex)`` (element 0 = Prime
    GO/NO-GO work; element 1 = Loyal Opposition NEW/REVISED work). This selects
    the element matching ``role_profile`` and computes the signature over the
    SELECTED items, so suppression/dismissal keys off the correct role's
    signature.

    Byte-identical signature scheme to
    scripts/cross_harness_bridge_trigger.py:_signature for the selected list.
    Falls back to ("", []) if the bridge index is missing or the canonical
    parser is unavailable — hook silently no-ops in those degraded states.
    """
    index_path = PROJECT_ROOT / "bridge" / "INDEX.md"
    if not index_path.is_file():
        return "", []
    index_text = index_path.read_text(encoding="utf-8")

    # Lazy-import canonical detector/notify so a missing module degrades to
    # silent no-op rather than crashing the agent.
    try:
        # Make sure groundtruth_kb is importable in the harness environment.
        gt_src = PROJECT_ROOT / "groundtruth-kb" / "src"
        if gt_src.is_dir() and str(gt_src) not in sys.path:
            sys.path.insert(0, str(gt_src))
        from groundtruth_kb.bridge.detector import parse_index  # type: ignore
        from groundtruth_kb.bridge.notify import compute_actionable_pending  # type: ignore
    except Exception as exc:
        _log_error({"event": "canonical_parser_unavailable", "error": str(exc)})
        return "", []

    try:
        parse_result = parse_index(index_text, project_root=PROJECT_ROOT)
        actionable_prime, actionable_codex = compute_actionable_pending(parse_result, project_root=PROJECT_ROOT)
    except Exception as exc:
        _log_error({"event": "parse_or_compute_failed", "error": str(exc)})
        return "", []

    # Slice 4: select the element matching the resolved session role. Element 0
    # is Prime-actionable (GO/NO-GO); element 1 is Loyal-Opposition-actionable
    # (NEW/REVISED), per compute_actionable_pending's (prime, codex) contract.
    items = actionable_prime if role_profile == ROLE_PRIME else actionable_codex
    # WI-4278 / gtkb-axis-2-dispatchable-filter-004 GO: compute_actionable_pending
    # attaches a centrally-computed `dispatchable` flag (per
    # smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4) that reflects the
    # bridge_kind classification. Terminal-kind GO entries (governance_review,
    # scoping, closure, parking, index/thread reconciliation,
    # operational_state_change, candidate_spec_intake, loyal_opposition_advisory)
    # have dispatchable=False and must be excluded from the in-session surface,
    # mirroring the cross-harness event-driven trigger's dispatch suppression
    # (which uses the same getattr(item, "dispatchable", True) compatibility-safe
    # idiom). NEW/REVISED/NO-GO entries are always dispatchable=True, so this
    # filter is a no-op for Loyal Opposition and for Prime NO-GO entries. The
    # `getattr(..., True)` default preserves stub-tolerance for existing test
    # doubles that omit the field.
    items = [item for item in items if getattr(item, "dispatchable", True)]

    import hashlib

    normalized = [
        {
            "document_name": item.document_name,
            "top_status": item.top_status,
            "top_file": item.top_file,
        }
        for item in items
    ]
    raw = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    signature = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return signature, items


def _read_cache(cache_path: Path) -> dict[str, Any]:
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _write_cache(cache_path: Path, payload: dict[str, Any]) -> None:
    """Atomic write via per-invocation temp + rename, mirroring dispatch-state pattern."""
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        import uuid as _uuid

        tmp = cache_path.with_name(f"{cache_path.name}.{_uuid.uuid4().hex[:8]}.tmp")
        tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        tmp.replace(cache_path)
    except Exception as exc:
        _log_error({"event": "cache_write_failed", "error": str(exc), "path": str(cache_path)})


def _resolve_session_id(payload: dict[str, Any]) -> str:
    """Use Claude Code session_id from payload if present; else fall back to
    a stable host-scoped default. The cache is per-session by design so
    multi-session boxes don't cross-contaminate."""
    sid = str(payload.get("session_id") or "").strip()
    if sid:
        # Sanitize for filesystem safety. Only allow alphanumerics, dash, underscore.
        return "".join(c for c in sid if c.isalnum() or c in ("-", "_"))[:64] or "default"
    return "default"


def _resolve_work_intent_session_id(payload: dict[str, Any]) -> str:
    for env_var in WORK_INTENT_SESSION_ENV_VARS:
        env_value = os.environ.get(env_var, "").strip()
        if env_value:
            return env_value
    sid = str(payload.get("session_id") or "").strip()
    if sid:
        return sid
    return ""


def _split_work_intent_claims(items: list[Any], session_id: str) -> tuple[list[Any], list[dict[str, Any]]]:
    if not session_id:
        return items, []
    try:
        from scripts.bridge_work_intent_registry import current_holder
    except Exception as exc:  # pragma: no cover - hook fail-soft.
        _log_error({"event": "work_intent_registry_unavailable", "error": str(exc)})
        return items, []

    available: list[Any] = []
    claimed: list[dict[str, Any]] = []
    for item in items:
        try:
            holder = current_holder(item.document_name, project_root=PROJECT_ROOT)
        except Exception as exc:  # noqa: BLE001 - hook must fail soft.
            _log_error({"event": "work_intent_holder_lookup_failed", "document": item.document_name, "error": str(exc)})
            available.append(item)
            continue
        if holder and holder.get("session_id") != session_id:
            claimed.append({"item": item, "holder": holder})
        else:
            available.append(item)
    return available, claimed


def _render_surface(
    items: list[Any],
    role_profile: str = ROLE_PRIME,
    claimed_items: list[dict[str, Any]] | None = None,
) -> str:
    """Render the additionalContext markdown block for the resolved role's work.

    The heading reflects the session-stated role: "Prime Work" for a Prime
    Builder session, "Loyal Opposition Work" for a Loyal Opposition session.
    """
    role_label = _ROLE_HEADING.get(role_profile, "Prime")
    claimed_items = claimed_items or []
    lines = [
        f"### Bridge AXIS 2 Surface — Newly-Actionable {role_label} Work",
        "",
        f"_Detected at {_now_iso()}. {len(items)} actionable entry/entries since last surface in this session._",
        "",
        "| Status | Document | Top File |",
        "|---|---|---|",
    ]
    for item in items[:10]:  # cap to 10 to keep prompt context bounded
        lines.append(f"| {item.top_status} | {item.document_name} | {item.top_file} |")
    if len(items) > 10:
        lines.append(f"| … | ({len(items) - 10} more not shown) | (see `bridge/INDEX.md`) |")
    if claimed_items:
        lines.extend(["", "| Claim | Document | Holder | Until |", "|---|---|---|---|"])
        for claimed in claimed_items[:10]:
            item = claimed["item"]
            holder = claimed["holder"]
            lines.append(
                "| ALREADY CLAIMED | "
                f"{item.document_name} | {holder.get('session_id')} | {holder.get('ttl_expires_at')} |"
            )
    lines.extend(
        [
            "",
            "_To suppress re-surfacing the same signature this session, include `dismiss bridge surface` in your next prompt. To disable globally, set `GTKB_NO_AXIS_2_SURFACE=1`._",
        ]
    )
    if role_profile == ROLE_PRIME:
        lines.extend(
            [
                "",
                "_To work an unclaimed thread, first run: `python scripts/bridge_claim_cli.py claim <slug>`._",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def _resolve_session_role_failsoft(payload: dict[str, Any]) -> str:
    """Resolve the interactive session role via the shared resolver; fail-soft.

    Passes the RAW payload ``session_id`` (Slice 2 stores the raw id). Returns
    ``ROLE_PRIME`` on any resolver import/lookup failure so the hook never
    crashes and degrades to today's Prime-default behavior.
    """
    raw_session_id = str(payload.get("session_id") or "").strip() or None
    try:
        from scripts.session_role_resolution import resolve_interactive_session_role

        role_profile, _source = resolve_interactive_session_role(
            PROJECT_ROOT,
            current_session_id=raw_session_id,
            harness_name="claude",
        )
        return role_profile if role_profile in (ROLE_PRIME, ROLE_LO) else ROLE_PRIME
    except Exception as exc:  # noqa: BLE001 - hook must never crash the agent.
        _log_error({"event": "session_role_resolve_failed", "error": str(exc)})
        return ROLE_PRIME


def _user_prompt_handler(stdin_text: str) -> str:
    """UserPromptSubmit entry point. Returns markdown to inject (empty = silent)."""
    if os.environ.get(ENV_DISABLE) == "1":
        return ""

    try:
        payload = json.loads(stdin_text or "{}")
    except json.JSONDecodeError:
        return ""

    prompt_text = str(payload.get("prompt") or "")
    session_id = _resolve_session_id(payload)
    cache_path = PROJECT_ROOT / STATE_DIR_REL / f"{session_id}.json"

    # Slice 4: resolve the session-stated role (marker > durable) and surface
    # the matching actionable work. The RAW payload session_id (not the
    # sanitized cache key) is passed so the resolver's session-id comparison is
    # like-for-like with the Slice 2 writer's stored raw id. Fail-soft to the
    # Prime profile (today's default) on any resolver failure.
    role_profile = _resolve_session_role_failsoft(payload)

    signature, items = _compute_actionable_for_role(role_profile)
    if not signature or not items:
        return ""
    claimed_items: list[dict[str, Any]] = []
    if role_profile == ROLE_PRIME:
        items, claimed_items = _split_work_intent_claims(items, _resolve_work_intent_session_id(payload))
        if not items and not claimed_items:
            return ""

    cache = _read_cache(cache_path)
    last_surfaced = str(cache.get("last_surfaced_signature") or "")
    dismissed = str(cache.get("dismissed_signature") or "")

    # Owner dismissal: if the prompt contains the keyword, record dismissal
    # for the current signature and silently no-op for this turn.
    if DISMISS_KEYWORD.lower() in prompt_text.lower():
        cache["dismissed_signature"] = signature
        cache["dismissed_at"] = _now_iso()
        cache["session_id"] = session_id
        _write_cache(cache_path, cache)
        return ""

    # Suppress re-surface of an already-surfaced or owner-dismissed signature.
    if signature in (last_surfaced, dismissed):
        return ""

    # New signature with selected_count > 0. Emit + update cache.
    rendered = _render_surface(items, role_profile, claimed_items)
    cache.update(
        {
            "last_surfaced_signature": signature,
            "last_surfaced_at": _now_iso(),
            "selected_count_at_surface": len(items),
            "session_id": session_id,
        }
    )
    _write_cache(cache_path, cache)
    return rendered


def main() -> int:
    try:
        stdin_text = sys.stdin.read()
    except Exception:
        stdin_text = ""

    try:
        output = _user_prompt_handler(stdin_text)
    except Exception as exc:
        _log_error({"event": "handler_crashed", "error": str(exc)})
        output = ""

    if output:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
