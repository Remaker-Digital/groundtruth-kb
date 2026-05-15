# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural and parity tests for the grill-me-for-clarification skill.

Derived from the behavior clauses of the operative owner-confirmed requirement
INTAKE-45c006c4 v2 / SPEC-INTAKE-1262c1 (bridge thread
``gtkb-grill-me-for-clarification-skill``, GO at -010).

The skill's interview behavior is an LLM procedure; per GOV-19 the testable
surface is the skill file itself — these tests verify the skill file declares
the contract the requirement specifies, and that the Codex parity adapter
mirrors it.
"""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLAUDE_SKILL = _REPO_ROOT / ".claude" / "skills" / "grill-me-for-clarification" / "SKILL.md"
_CODEX_ADAPTER = _REPO_ROOT / ".codex" / "skills" / "grill-me-for-clarification" / "SKILL.md"

_PHASE_MARKERS = ("Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4")


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Return ``(frontmatter, body)`` for a SKILL.md file."""
    assert text.startswith("---"), "SKILL.md must open with a YAML frontmatter block"
    parts = text.split("---", 2)
    assert len(parts) == 3, "SKILL.md frontmatter block must be closed with ---"
    return parts[1], parts[2]


def _frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    assert match, f"frontmatter is missing '{key}'"
    return match.group(1).strip()


def test_skill_file_exists_with_valid_frontmatter() -> None:
    assert _CLAUDE_SKILL.is_file(), f"missing skill file: {_CLAUDE_SKILL}"
    frontmatter, body = _split_frontmatter(_CLAUDE_SKILL.read_text(encoding="utf-8"))
    assert _frontmatter_value(frontmatter, "name") == "grill-me-for-clarification"
    description = _frontmatter_value(frontmatter, "description")
    assert "grill me for clarification" in description.lower()
    assert body.strip(), "skill body must not be empty"


def test_skill_body_declares_five_phases() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    for marker in _PHASE_MARKERS:
        assert marker in body, f"skill body is missing phase marker '{marker}'"


def test_skill_body_states_scope_required_no_default() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8").lower()
    assert "requires an explicit scope argument" in body
    assert "no default scope" in body


def test_skill_body_routes_persistence_to_capture_and_intake() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    assert "gtkb-decision-capture" in body
    assert "gtkb-spec-intake" in body


def test_skill_body_declares_non_goals() -> None:
    text = _CLAUDE_SKILL.read_text(encoding="utf-8")
    assert "## Non-goals" in text
    for phrase in ("write or modify code", "file bridge proposals", "promote specs beyond"):
        assert phrase in text, f"non-goals section is missing '{phrase}'"


def test_codex_adapter_parity() -> None:
    assert _CODEX_ADAPTER.is_file(), f"missing Codex adapter: {_CODEX_ADAPTER}"
    text = _CODEX_ADAPTER.read_text(encoding="utf-8")
    frontmatter, _ = _split_frontmatter(text)
    assert _frontmatter_value(frontmatter, "name") == "grill-me-for-clarification"
    for marker in _PHASE_MARKERS:
        assert marker in text, f"Codex adapter is missing phase marker '{marker}'"
