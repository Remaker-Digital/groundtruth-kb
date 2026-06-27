#!/usr/bin/env python3
"""Claude UserPromptSubmit adapter for ::open / ::close topic-envelope routing.

Slice 5 (first conformance case) of PROJECT-GTKB-CROSS-HARNESS-PARITY. This is the
Claude-native counterpart to the Codex
``.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`` topic-command branch:
both adapters call the identical shared, harness-agnostic platform module
``groundtruth_kb.session.topic_router`` (``parse_topic_command`` /
``handle_topic_command`` / ``render_topic_context``), differing only in
``HARNESS_NAME``, harness-id resolution, and diagnostic output paths (Q1
behavioral — not identity — equivalence per ADR-CROSS-HARNESS-PARITY-001).

Scope: the ``::open`` / ``::close`` topic-envelope routing only. The Codex hook's
wrap-trigger-phrase branch is deliberately NOT ported — Claude already runs
session wrap-up via its Stop hook (``session_self_initialization --emit-wrapup``),
so a UserPromptSubmit wrap-trigger would double-fire.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

HARNESS_NAME = "claude"


def _discover_project_root() -> Path:
    """Resolve the GT-KB project root by walking up to the ``groundtruth.toml`` marker.

    Portable across the main worktree and ``.claude/worktrees/*`` linked
    worktrees (unlike a hardcoded absolute path).
    """
    for parent in Path(__file__).resolve().parents:
        if (parent / "groundtruth.toml").is_file():
            return parent
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = _discover_project_root()
OUT_DIR = PROJECT_ROOT / ".gtkb-state" / "session-topic-router" / HARNESS_NAME

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
_GT_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if _GT_SRC.is_dir() and str(_GT_SRC) not in sys.path:
    sys.path.insert(0, str(_GT_SRC))

from groundtruth_kb.session.envelope import EnvelopeError  # noqa: E402
from groundtruth_kb.session.topic_router import (  # noqa: E402
    handle_topic_command,
    parse_topic_command,
    render_topic_context,
)

from scripts.harness_identity import resolved_harness_id  # noqa: E402


def _read_stdin() -> str:
    try:
        return sys.stdin.read()
    except Exception:
        return ""


def _direct_prompt_value(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("prompt", "userPrompt", "user_prompt", "message", "content", "text", "input"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
        for value in payload.values():
            found = _direct_prompt_value(value)
            if found:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _direct_prompt_value(value)
            if found:
                return found
    return ""


def _extract_prompt(raw_input: str) -> str:
    raw_input = raw_input.strip()
    if not raw_input:
        return ""
    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError:
        return raw_input
    return _direct_prompt_value(payload) or raw_input


def _hook_payload(context: str) -> dict[str, dict[str, str]]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }


def _dump_payload(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=True)


def _emit_no_context() -> None:
    print("{}")


def _lifecycle_guard_path() -> Path:
    override = os.environ.get("GTKB_LIFECYCLE_GUARD_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return PROJECT_ROOT / "harness-state" / HARNESS_NAME / "session-lifecycle-guard.json"


def _startup_input_gate_active() -> bool:
    """True while the SessionStart init-keyword relay owns the next prompt.

    Mirrors the Codex adapter so the topic router never races the startup
    disclosure relay.
    """
    try:
        state = json.loads(_lifecycle_guard_path().read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    if not isinstance(state, dict):
        return False
    return state.get("discard_next_user_prompt") is True or state.get("startup_response_pending") is True


def _persistent_harness_id() -> str | None:
    try:
        return resolved_harness_id(PROJECT_ROOT, harness_name=HARNESS_NAME)
    except Exception:
        return None


def main() -> int:
    raw_input = _read_stdin()
    prompt = _extract_prompt(raw_input)

    if _startup_input_gate_active():
        _emit_no_context()
        return 0

    command = parse_topic_command(prompt)
    if command is None:
        _emit_no_context()
        return 0

    try:
        result = handle_topic_command(
            PROJECT_ROOT,
            command,
            harness_name=HARNESS_NAME,
            harness_id=_persistent_harness_id(),
        )
        try:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            (OUT_DIR / "last-topic-envelope-command.json").write_text(
                json.dumps(result, indent=2, sort_keys=True),
                encoding="utf-8",
            )
        except OSError:
            pass
        print(_dump_payload(_hook_payload(render_topic_context(result))))
    except EnvelopeError as exc:
        context = (
            "# GroundTruth-KB Topic Envelope Command Failed\n\n"
            f"`{command.raw}` matched the strict topic-envelope command grammar, "
            f"but the envelope runtime rejected it: {exc}"
        )
        print(_dump_payload(_hook_payload(context)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
