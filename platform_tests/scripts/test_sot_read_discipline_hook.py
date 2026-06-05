"""Tests for the SoT read-discipline canonical hook.

Authority: DCL-SOT-READ-HOOK-CONTRACT-001 v1 + GOV-SOURCE-OF-TRUTH-FRESHNESS-001 v2.

Exercises the canonical hook at .claude/hooks/sot-read-discipline.py against
both Claude-shape (Read/Grep/Glob) and Codex-shape (Bash with per-verb command)
PreToolUse payloads.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_HOOK = PROJECT_ROOT / ".claude" / "hooks" / "sot-read-discipline.py"


def _run_hook(payload: dict) -> dict:
    result = subprocess.run(
        [sys.executable, str(CANONICAL_HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"hook failed: stderr={result.stderr!r}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


# ---- Claude-shape fixtures ------------------------------------------------------


def test_read_against_forbidden_substitute_blocks() -> None:
    """Read .claude/rules/bridge-essential.md should block (forbidden_substitute for harness-bridge-substrate)."""
    decision = _run_hook({"tool_name": "Read", "tool_input": {"file_path": ".claude/rules/bridge-essential.md"}})
    assert decision.get("decision") == "block", f"expected block, got {decision!r}"
    assert "harness-state/bridge-substrate.json" in decision.get("reason", "")


def test_grep_against_forbidden_substitute_blocks() -> None:
    decision = _run_hook(
        {"tool_name": "Grep", "tool_input": {"path": ".claude/rules/operating-role.md", "pattern": "role"}}
    )
    assert decision.get("decision") == "block"


def test_glob_against_forbidden_substitute_blocks() -> None:
    decision = _run_hook({"tool_name": "Glob", "tool_input": {"pattern": ".claude/rules/operating-role.md"}})
    assert decision.get("decision") == "block"


def test_read_against_unregistered_path_no_block() -> None:
    decision = _run_hook({"tool_name": "Read", "tool_input": {"file_path": "README.md"}})
    assert decision == {}


def test_read_against_canonical_sot_no_block() -> None:
    """Reading the canonical path itself (NOT a substitute) is allowed."""
    decision = _run_hook({"tool_name": "Read", "tool_input": {"file_path": "harness-state/bridge-substrate.json"}})
    assert decision == {}


# ---- Codex-shape (Bash) fixtures ------------------------------------------------


def test_bash_get_content_forbidden_blocks() -> None:
    decision = _run_hook(
        {"tool_name": "Bash", "tool_input": {"command": "Get-Content .claude/rules/bridge-essential.md"}}
    )
    assert decision.get("decision") == "block"


def test_bash_gc_alias_forbidden_blocks() -> None:
    decision = _run_hook({"tool_name": "Bash", "tool_input": {"command": "gc .claude/rules/operating-role.md"}})
    assert decision.get("decision") == "block"


def test_bash_cat_forbidden_blocks() -> None:
    decision = _run_hook({"tool_name": "Bash", "tool_input": {"command": "cat .claude/rules/operating-role.md"}})
    assert decision.get("decision") == "block"


def test_bash_select_string_forbidden_blocks() -> None:
    decision = _run_hook(
        {
            "tool_name": "Bash",
            "tool_input": {"command": "Select-String -Path .claude/rules/operating-role.md -Pattern role"},
        }
    )
    assert decision.get("decision") == "block"


def test_bash_get_childitem_recurse_forbidden_blocks() -> None:
    decision = _run_hook(
        {
            "tool_name": "Bash",
            "tool_input": {"command": "Get-ChildItem -Path .claude/rules/operating-role.md -Recurse"},
        }
    )
    assert decision.get("decision") == "block"


def test_bash_rg_forbidden_blocks() -> None:
    decision = _run_hook(
        {"tool_name": "Bash", "tool_input": {"command": "rg pattern .claude/rules/bridge-essential.md"}}
    )
    assert decision.get("decision") == "block"


def test_bash_grep_forbidden_blocks() -> None:
    decision = _run_hook(
        {"tool_name": "Bash", "tool_input": {"command": "grep pattern .claude/rules/bridge-essential.md"}}
    )
    assert decision.get("decision") == "block"


def test_bash_unrelated_command_no_block() -> None:
    decision = _run_hook({"tool_name": "Bash", "tool_input": {"command": "git status --short"}})
    assert decision == {}


def test_bash_get_content_unregistered_no_block() -> None:
    decision = _run_hook({"tool_name": "Bash", "tool_input": {"command": "Get-Content README.md"}})
    assert decision == {}


# ---- Bypass + edge cases --------------------------------------------------------


def test_bypass_env_disables_block(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GTKB_SOT_READ_DISCIPLINE_BYPASS", "1")
    result = subprocess.run(
        [sys.executable, str(CANONICAL_HOOK)],
        input=json.dumps({"tool_name": "Read", "tool_input": {"file_path": ".claude/rules/bridge-essential.md"}}),
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        env={**__import__("os").environ, "GTKB_SOT_READ_DISCIPLINE_BYPASS": "1"},
        check=False,
    )
    assert result.returncode == 0
    decision = json.loads(result.stdout) if result.stdout.strip() else {}
    assert decision == {}


def test_unknown_tool_no_block() -> None:
    decision = _run_hook({"tool_name": "Edit", "tool_input": {"file_path": "anything"}})
    assert decision == {}


def test_empty_payload_no_block() -> None:
    decision = _run_hook({})
    assert decision == {}
