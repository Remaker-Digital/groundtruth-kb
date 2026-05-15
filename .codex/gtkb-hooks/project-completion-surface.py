#!/usr/bin/env python3
"""UserPromptSubmit hook — Project VERIFIED-completion AUQ surface.

IP-2 of WI-3316 (bridge thread ``gtkb-project-verified-completion-auq-trigger``).

An Axis-2 (non-dispatchable, interactive notification) surface. On each
``UserPromptSubmit`` it runs the read-only project-verified-completion scanner;
when a project authorization has become completion-ready (every included work
item is covered by a bridge thread whose latest ``bridge/INDEX.md`` status is
``VERIFIED``), it surfaces ONE such authorization per prompt as
``additionalContext``, instructing the agent to confirm completion with the
owner via ``AskUserQuestion``.

This hook never mutates state. The actual transition is performed only by
``ProjectLifecycleService.complete_project_authorization()`` after owner
confirmation; auto-transition is prohibited
(``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001``).

This file is kept byte-identical between ``.claude/hooks/`` and
``.codex/gtkb-hooks/`` for Claude/Codex hook parity
(``ADR-CODEX-HOOK-PARITY-FALLBACK-001``); ``parents[2]`` resolves the repo root
from either location.

Stdin:  JSON hook event payload.
Stdout: empty (silent no-op) or a markdown additionalContext block.
Exit:   always 0 (fire-and-forget; the hook must never crash the agent).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ENV_DISABLE = "GTKB_NO_PROJECT_COMPLETION_SURFACE"

PROJECT_ROOT = Path(
    os.environ.get("CLAUDE_PROJECT_DIR")
    or os.environ.get("GTKB_PROJECT_ROOT")
    or Path(__file__).resolve().parents[2]
).resolve()

STATE_DIR_REL = ".gtkb-state/project-completion-surface"
ERRORS_LOG_REL = ".gtkb-state/project-completion-surface/errors.jsonl"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _log_error(payload: dict[str, Any]) -> None:
    """Append a diagnostic record. Best-effort; silent on failure."""
    try:
        log_path = PROJECT_ROOT / ERRORS_LOG_REL
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({**payload, "ts": _now_iso()}) + "\n")
    except Exception:
        pass


def _completion_ready_authorizations() -> list[Any]:
    """Return completion-ready authorizations via the IP-1 scanner.

    Degrades to ``[]`` (silent no-op) if the scanner is unavailable or fails,
    so the hook never blocks or crashes the agent.
    """
    try:
        scripts_dir = PROJECT_ROOT / "scripts"
        if scripts_dir.is_dir() and str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from project_verified_completion_scanner import completion_ready
    except Exception as exc:
        _log_error({"event": "scanner_unavailable", "error": str(exc)})
        return []
    try:
        return completion_ready(PROJECT_ROOT)
    except Exception as exc:
        _log_error({"event": "scan_failed", "error": str(exc)})
        return []


def _read_cache(cache_path: Path) -> dict[str, Any]:
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _write_cache(cache_path: Path, payload: dict[str, Any]) -> None:
    """Atomic write via per-invocation temp + rename."""
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = cache_path.with_name(f"{cache_path.name}.{uuid.uuid4().hex[:8]}.tmp")
        tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        tmp.replace(cache_path)
    except Exception as exc:
        _log_error({"event": "cache_write_failed", "error": str(exc), "path": str(cache_path)})


def _resolve_session_id(payload: dict[str, Any]) -> str:
    """Per-session cache key; sanitized for filesystem safety."""
    sid = str(payload.get("session_id") or "").strip()
    if sid:
        return "".join(c for c in sid if c.isalnum() or c in ("-", "_"))[:64] or "default"
    return "default"


def _render_surface(item: Any) -> str:
    """Render the additionalContext markdown block for one ready authorization."""
    included = ", ".join(item.included_work_item_ids) or "(none)"
    return "\n".join(
        [
            "### Project Completion Surface — Authorization Ready for Owner Confirmation",
            "",
            f"_Detected at {_now_iso()}._",
            "",
            f"- Project authorization **{item.authorization_id}** "
            f"(project `{item.project_id}` — {item.authorization_name}) is "
            "**completion-ready**: every included work item "
            f"({included}) is covered by a VERIFIED bridge thread.",
            "",
            "**Action:** confirm with the owner via `AskUserQuestion` whether to "
            f"transition `{item.authorization_id}` to `completed` (and retire "
            f"`{item.project_id}` if it is the sole active authorization). On owner "
            "approval, archive the owner-decision deliberation with the project or "
            "authorization id in its content, then call "
            "`ProjectLifecycleService.complete_project_authorization()`. "
            "Do NOT auto-transition without owner confirmation.",
            "",
        ]
    )


def _user_prompt_handler(stdin_text: str) -> str:
    """UserPromptSubmit entry point. Returns markdown to inject (empty = silent)."""
    if os.environ.get(ENV_DISABLE) == "1":
        return ""
    try:
        payload = json.loads(stdin_text or "{}")
    except json.JSONDecodeError:
        return ""

    session_id = _resolve_session_id(payload)
    cache_path = PROJECT_ROOT / STATE_DIR_REL / f"{session_id}.json"

    ready = _completion_ready_authorizations()
    if not ready:
        return ""

    cache = _read_cache(cache_path)
    surfaced = set(cache.get("surfaced_authorization_ids") or [])
    pending = [r for r in ready if r.authorization_id not in surfaced]
    if not pending:
        return ""

    item = pending[0]  # one-at-a-time, oldest (project/id-sorted) first
    cache["surfaced_authorization_ids"] = sorted(surfaced | {item.authorization_id})
    cache["last_surfaced_at"] = _now_iso()
    cache["session_id"] = session_id
    _write_cache(cache_path, cache)
    return _render_surface(item)


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
