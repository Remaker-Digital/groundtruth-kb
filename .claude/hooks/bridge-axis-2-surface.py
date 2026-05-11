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

PROJECT_ROOT = Path(
    os.environ.get("CLAUDE_PROJECT_DIR")
    or Path(__file__).resolve().parents[2]
).resolve()

STATE_DIR_REL = ".gtkb-state/bridge-poller/axis-2-surface"
DISPATCH_STATE_REL = ".gtkb-state/bridge-poller/dispatch-state.json"
ERRORS_LOG_REL = ".gtkb-state/bridge-poller/axis-2-surface/errors.jsonl"


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


def _compute_prime_actionable() -> tuple[str, list[Any]]:
    """Return (signature, actionable_items_for_prime).

    Byte-identical signature to scripts/cross_harness_bridge_trigger.py:_signature.
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
        actionable_prime, _actionable_codex = compute_actionable_pending(
            parse_result, project_root=PROJECT_ROOT
        )
    except Exception as exc:
        _log_error({"event": "parse_or_compute_failed", "error": str(exc)})
        return "", []

    import hashlib
    normalized = [
        {
            "document_name": item.document_name,
            "top_status": item.top_status,
            "top_file": item.top_file,
        }
        for item in actionable_prime
    ]
    raw = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    signature = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return signature, actionable_prime


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


def _render_surface(items: list[Any]) -> str:
    """Render the additionalContext markdown block for actionable Prime work."""
    lines = [
        "### Bridge AXIS 2 Surface — Newly-Actionable Prime Work",
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
    lines.extend(
        [
            "",
            "_To suppress re-surfacing the same signature this session, include `dismiss bridge surface` in your next prompt. To disable globally, set `GTKB_NO_AXIS_2_SURFACE=1`._",
            "",
        ]
    )
    return "\n".join(lines)


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

    signature, items = _compute_prime_actionable()
    if not signature or not items:
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
    if signature == last_surfaced or signature == dismissed:
        return ""

    # New signature with selected_count > 0. Emit + update cache.
    rendered = _render_surface(items)
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
