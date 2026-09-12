"""Spec-derived tests for WI-4814 report skill self-disclosure (SPEC-REPORT-SKILL-DISCLOSURE-001)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EMITTER_PATH = REPO_ROOT / "scripts" / "skill_disclosure.py"
WRITE_VERDICT = REPO_ROOT / ".claude" / "skills" / "verify" / "helpers" / "write_verdict.py"
CODEX_REPORT_SKILL = REPO_ROOT / ".claude" / "skills" / "codex-report" / "SKILL.md"
SESSION_WRAP_SKILL = REPO_ROOT / ".claude" / "skills" / "kb-session-wrap" / "SKILL.md"
CODEX_ADAPTER_REPORT = REPO_ROOT / ".codex" / "skills" / "codex-report" / "SKILL.md"
CODEX_ADAPTER_WRAP = REPO_ROOT / ".codex" / "skills" / "kb-session-wrap" / "SKILL.md"
PARITY_SCRIPT = REPO_ROOT / "scripts" / "check_harness_parity.py"


def _load_emitter():
    spec = importlib.util.spec_from_file_location("skill_disclosure", EMITTER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["skill_disclosure"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def emitter():
    return _load_emitter()


def test_ac1_format_and_round_trip(emitter) -> None:
    line = emitter.format_skills_applied(["gtkb-bridge", "verify"])
    assert line == "Skills applied: gtkb-bridge, verify"
    assert emitter.parse_skills_applied(line) == ["gtkb-bridge", "verify"]
    assert emitter.parse_skills_applied(f"prefix\n{line}\nsuffix") == ["gtkb-bridge", "verify"]


def test_ac5_deterministic_no_side_effects(emitter) -> None:
    args = (["a", "b", "a"],)
    first = emitter.format_skills_applied(*args)
    second = emitter.format_skills_applied(*args)
    assert first == second == "Skills applied: a, b"


def test_ac6_empty_and_missing_line(emitter) -> None:
    assert emitter.format_skills_applied([]) == "Skills applied: (none)"
    assert emitter.parse_skills_applied("no disclosure here") == []
