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
    assert hook.parse_topic_command("::open  spec") is None
    assert hook.parse_topic_command("::close unknown") is None
