"""Tests for Codex UserPromptSubmit wrap/topic command recognition."""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".codex" / "gtkb-hooks" / "session_wrapup_trigger_dispatch.py"


def _load_hook():
    spec = importlib.util.spec_from_file_location("session_wrapup_trigger_dispatch", HOOK_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hook_accepts_canonical_wrap_only_without_trailing_space() -> None:
    hook = _load_hook()
    assert hook._is_wrapup_trigger("::wrap")
    assert hook._is_wrapup_trigger("\n::wrap\nnotes")
    assert not hook._is_wrapup_trigger("::wrap ")
    assert not hook._is_wrapup_trigger("::WRAP")
    assert hook._is_wrapup_trigger("wrap up")


def test_hook_recognizes_strict_topic_commands() -> None:
    hook = _load_hook()
    command = hook.parse_topic_command("::open spec")
    assert command is not None
    assert command.action == "open"
    assert command.topic_type == "spec"
    ops_open = hook.parse_topic_command("::open ops")
    assert ops_open is not None
    assert ops_open.action == "open"
    assert ops_open.topic_type == "ops"
    ops_close = hook.parse_topic_command("::close ops")
    assert ops_close is not None
    assert ops_close.action == "close"
    assert ops_close.topic_type == "ops"
    assert hook.parse_topic_command("::open  spec") is None
    assert hook.parse_topic_command("::close unknown") is None


def test_hook_render_topic_context_includes_activity_profile() -> None:
    hook = _load_hook()

    context = hook.render_topic_context(
        {
            "action": "open",
            "topic_type": "build",
            "topic": {"route_target": "build-package-scaffold-service"},
        }
    )

    assert "## Activity Disposition Profile" in context
    assert "- name: build" in context
    assert "- headless_eligibility: headless_eligible" in context
    assert "- direction.stance: implement-within-scope" in context


def test_startup_input_gate_uses_harness_state_guard_not_legacy_codex_guard(tmp_path, monkeypatch) -> None:
    hook = _load_hook()
    monkeypatch.delenv("GTKB_LIFECYCLE_GUARD_PATH", raising=False)
    monkeypatch.setattr(hook, "PROJECT_ROOT", tmp_path)

    legacy_guard = tmp_path / ".codex" / "gtkb-hooks" / "session-lifecycle-guard.json"
    legacy_guard.parent.mkdir(parents=True)
    legacy_guard.write_text(
        '{"discard_next_user_prompt": true, "startup_response_pending": true}\n',
        encoding="utf-8",
    )
    canonical_guard = tmp_path / "harness-state" / "codex" / "session-lifecycle-guard.json"
    canonical_guard.parent.mkdir(parents=True)
    canonical_guard.write_text(
        '{"discard_next_user_prompt": false, "startup_response_pending": false}\n',
        encoding="utf-8",
    )

    assert hook._lifecycle_guard_path() == canonical_guard
    assert hook._startup_input_gate_active() is False


def test_startup_input_gate_blocks_when_canonical_guard_is_active(tmp_path, monkeypatch) -> None:
    hook = _load_hook()
    monkeypatch.delenv("GTKB_LIFECYCLE_GUARD_PATH", raising=False)
    monkeypatch.setattr(hook, "PROJECT_ROOT", tmp_path)

    canonical_guard = tmp_path / "harness-state" / "codex" / "session-lifecycle-guard.json"
    canonical_guard.parent.mkdir(parents=True)
    canonical_guard.write_text(
        '{"discard_next_user_prompt": false, "startup_response_pending": true}\n',
        encoding="utf-8",
    )

    assert hook._startup_input_gate_active() is True
