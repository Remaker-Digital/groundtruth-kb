#!/usr/bin/env python3
"""UserPromptSubmit hook - Project VERIFIED-completion automatic-transition trigger.

W1 of GTKB-GOVERNANCE-CORRECTION-S358 (WI-3365); originally IP-2 of WI-3316.

An Axis-2 (interactive notification) surface. On each ``UserPromptSubmit`` it
invokes ``ProjectLifecycleService.auto_complete_ready_authorizations()``: every
active project authorization whose gating work items all have a VERIFIED bridge
thread is transitioned to ``completed`` automatically, and its project is
retired when it was the sole active authorization. When the pass completes one
or more authorizations, the hook emits a notification of what was
auto-completed and retired as ``additionalContext``.

``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v2: completion and retirement
are automatic and require no owner ``AskUserQuestion`` confirmation - owner AUQ
governs project START (authorization creation and approval), not completion.
This hook is the prompt-time trigger plus owner-visible notification; the
transition itself is performed by
``ProjectLifecycleService.complete_project_authorization()``.

This file is kept byte-identical between ``.claude/hooks/`` and
``.codex/gtkb-hooks/`` for Claude/Codex hook parity
(``ADR-CODEX-HOOK-PARITY-FALLBACK-001``); ``parents[2]`` resolves the repo root
from either location.

Stdin:  JSON hook event payload (consumed, not inspected).
Stdout: empty (silent no-op) or a markdown additionalContext notification.
Exit:   always 0 (fire-and-forget; the hook must never crash the agent).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ENV_DISABLE = "GTKB_NO_PROJECT_COMPLETION_SURFACE"

PROJECT_ROOT = Path(
    os.environ.get("CLAUDE_PROJECT_DIR")
    or os.environ.get("GTKB_PROJECT_ROOT")
    or Path(__file__).resolve().parents[2]
).resolve()

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


def _auto_complete_ready_authorizations() -> list[dict[str, Any]]:
    """Run the automatic project-completion transition via the lifecycle service.

    Degrades to ``[]`` (silent no-op) if the service is unavailable or fails,
    so the hook never blocks or crashes the agent. The transition is idempotent:
    a completed authorization is no longer active and is not re-processed.
    """
    try:
        gt_src = PROJECT_ROOT / "groundtruth-kb" / "src"
        if gt_src.is_dir() and str(gt_src) not in sys.path:
            sys.path.insert(0, str(gt_src))
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.project.lifecycle import ProjectLifecycleService
    except Exception as exc:
        _log_error({"event": "service_unavailable", "error": str(exc)})
        return []

    db = None
    try:
        db = KnowledgeDB(PROJECT_ROOT / "groundtruth.db")
        service = ProjectLifecycleService(db)
        return service.auto_complete_ready_authorizations(project_root=PROJECT_ROOT)
    except Exception as exc:
        _log_error({"event": "auto_complete_failed", "error": str(exc)})
        return []
    finally:
        if db is not None:
            try:
                db.close()
            except Exception:
                pass


def _render_notification(completed: list[dict[str, Any]]) -> str:
    """Render the additionalContext markdown notification for the
    auto-completed authorizations."""
    lines = [
        "### Project Completion Surface - Authorizations Auto-Completed",
        "",
        f"_Detected at {_now_iso()}._",
        "",
        f"{len(completed)} project authorization(s) reached VERIFIED-completion readiness and "
        "were transitioned automatically. Per GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2, "
        "project completion and retirement are automatic and require no owner confirmation.",
        "",
    ]
    for item in completed:
        retired = " - project retired (sole active authorization)" if item.get("project_retired") else ""
        lines.append(
            f"- Authorization `{item.get('authorization_id')}` "
            f"(project `{item.get('project_id')}`) -> `completed`{retired}."
        )
    lines.append("")
    lines.append("_Notification only - the transition has already been applied; no action is required._")
    lines.append("")
    return "\n".join(lines)


def _user_prompt_handler() -> str:
    """UserPromptSubmit entry point. Returns markdown to inject (empty = silent).

    The auto-completion pass does not depend on the prompt payload.
    """
    if os.environ.get(ENV_DISABLE) == "1":
        return ""
    completed = _auto_complete_ready_authorizations()
    if not completed:
        return ""
    return _render_notification(completed)


def main() -> int:
    try:
        sys.stdin.read()  # consume the hook payload; it is not inspected
    except Exception:
        pass
    try:
        output = _user_prompt_handler()
    except Exception as exc:
        _log_error({"event": "handler_crashed", "error": str(exc)})
        output = ""
    if output:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
