# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural and parity tests for the lo-opportunity-radar skill.

Derived from SPEC-LO-OPPORTUNITY-RADAR-001 (bridge thread
``gtkb-lo-opportunity-radar-skill``). The radar review posture is an LLM
procedure; per GOV-19 the testable surface is the skill file, its Codex parity
adapter, and the harness-capability registry entry — these tests verify those
artifacts declare the contract the specification requires.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLAUDE_SKILL = _REPO_ROOT / ".claude" / "skills" / "lo-opportunity-radar" / "SKILL.md"
_CODEX_ADAPTER = _REPO_ROOT / ".codex" / "skills" / "lo-opportunity-radar" / "SKILL.md"
_REGISTRY = _REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"

_PASS_MARKERS = (
    "Defect pass",
    "Token-savings pass",
    "Deterministic-service pass",
    "Surface-eligibility pass",
    "Routing pass",
)


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


def _registry_capability(cap_id: str) -> dict:
    data = tomllib.loads(_REGISTRY.read_text(encoding="utf-8"))
    for cap in data.get("capabilities", []):
        if cap.get("id") == cap_id:
            return cap
    raise AssertionError(f"registry has no capability '{cap_id}'")


def test_skill_file_exists_with_valid_frontmatter() -> None:
    """T1 — SPEC-LO-OPPORTUNITY-RADAR-001: delivered as a canonical skill."""
    assert _CLAUDE_SKILL.is_file(), f"missing skill file: {_CLAUDE_SKILL}"
    frontmatter, body = _split_frontmatter(_CLAUDE_SKILL.read_text(encoding="utf-8"))
    assert _frontmatter_value(frontmatter, "name") == "lo-opportunity-radar"
    assert _frontmatter_value(frontmatter, "description"), "description must not be empty"
    assert body.strip(), "skill body must not be empty"


def test_skill_body_declares_five_passes() -> None:
    """T2 — SPEC-LO-OPPORTUNITY-RADAR-001: the five-pass review structure."""
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    for marker in _PASS_MARKERS:
        assert marker in body, f"skill body is missing pass '{marker}'"


def test_routing_pass_routes_through_advisory_router() -> None:
    """T2b — SPEC-LO-OPPORTUNITY-RADAR-001: routing pass uses the advisory-router."""
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    assert "advisory-router" in body or "advisory_backlog_router" in body, (
        "routing pass must direct material findings through the existing advisory-router"
    )


def test_codex_adapter_parity() -> None:
    """T3 — ADR-CODEX-HOOK-PARITY-FALLBACK-001: Codex adapter mirrors the skill."""
    assert _CODEX_ADAPTER.is_file(), f"missing Codex adapter: {_CODEX_ADAPTER}"
    text = _CODEX_ADAPTER.read_text(encoding="utf-8")
    frontmatter, _ = _split_frontmatter(text)
    assert _frontmatter_value(frontmatter, "name") == "lo-opportunity-radar"
    for marker in _PASS_MARKERS:
        assert marker in text, f"Codex adapter is missing pass '{marker}'"


def test_registry_marks_skill_loyal_opposition_relevant() -> None:
    """T4 — SPEC-LO-OPPORTUNITY-RADAR-001: skill is registered loyal-opposition-relevant."""
    cap = _registry_capability("skill.lo-opportunity-radar")
    assert cap["kind"] == "skill"
    assert cap["canonical_name"] == "lo-opportunity-radar"
    assert "loyal-opposition" in cap["required_for_roles"], "skill must be required for the loyal-opposition role"


def test_registry_declares_both_harness_surfaces() -> None:
    """T5 — ADR-CODEX-HOOK-PARITY-FALLBACK-001: cross-harness parity surfaces."""
    cap = _registry_capability("skill.lo-opportunity-radar")
    assert cap["claude"]["surface"] == ".claude/skills/lo-opportunity-radar/SKILL.md"
    assert cap["claude"]["status"] == "native"
    assert cap["codex"]["surface"] == ".codex/skills/lo-opportunity-radar/SKILL.md"
    assert cap["codex"]["status"] == "adapter"
    assert cap["codex"]["adapter_source"] == ".claude/skills/lo-opportunity-radar/SKILL.md"
    assert _CODEX_ADAPTER.is_file(), "Codex adapter file must exist on disk"
