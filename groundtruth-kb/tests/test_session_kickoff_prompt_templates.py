# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for WI-4961 session kickoff prompt sequencing in scaffold guidance."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    target = _ROOT / path
    assert target.is_file(), f"missing kickoff prompt surface: {path}"
    return target.read_text(encoding="utf-8")


def _session_start_section(text: str) -> str:
    assert "### Starting a New Session" in text
    return text.split("### Starting a New Session", 1)[1].split("### Session Wrap-Up", 1)[0]


def _text_fences(section: str) -> list[str]:
    return re.findall(r"```text\r?\n(.*?)\r?\n```", section, flags=re.DOTALL)


@pytest.mark.parametrize(
    "path",
    [
        "CLAUDE.md",
        "groundtruth-kb/templates/CLAUDE.md",
        "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/CLAUDE.md",
        "groundtruth-kb/tests/fixtures/scaffold_golden/local-only/CLAUDE.md",
    ],
)
def test_starting_session_guidance_uses_separate_init_open_and_task_messages(path: str) -> None:
    section = _session_start_section(_read(path))
    fences = _text_fences(section)

    assert len(fences) >= 3
    assert fences[0].strip() == "::init gtkb pb"
    assert fences[1].strip() == "::open project"
    assert "Continue work on" in fences[2]
    assert all("Continue work on" not in fence for fence in fences[:2])
    assert all("Next:" not in fence for fence in fences[:2])


def test_codex_quick_restart_prompt_uses_separate_messages() -> None:
    text = _read(".claude/rules/codex-session-bootstrap.md")
    section = text.split("## Quick Restart Prompt", 1)[1].split("## Read-Only Review Mode Behavior", 1)[0]
    fences = _text_fences(section)

    assert len(fences) >= 3
    assert fences[0].strip() == "::init gtkb pb"
    assert fences[1].strip() == "::open project"
    assert "Resolve this harness's persistent ID" in fences[2]
    assert all("Resolve this harness's persistent ID" not in fence for fence in fences[:2])
