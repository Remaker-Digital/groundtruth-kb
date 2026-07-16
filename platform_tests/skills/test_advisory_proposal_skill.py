"""Tests for the advisory-proposal skill contract (WI-5055/WI-5059)."""

from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _assert_pending_go(slug: str, test_id: str, target_path: str) -> None:
    proposal = _read(f"bridge/{slug}-001.md")
    verdict = _read(f"bridge/{slug}-002.md")
    assert verdict.lstrip().startswith("GO")
    assert f"Linked manual test: {test_id}" in proposal
    assert target_path in proposal
    assert "Owner Decisions / Input" in proposal
    assert "advisory capture itself must not become implementation approval" in proposal


def test_advisory_proposal_skill_content_or_pending_go() -> None:
    skill_path = REPO_ROOT / ".claude" / "skills" / "advisory-proposal" / "SKILL.md"
    if not skill_path.exists():
        _assert_pending_go(
            "gtkb-wi5055-advisory-proposal-skill",
            "TEST-11293",
            ".claude/skills/advisory-proposal/SKILL.md",
        )
        return

    body = skill_path.read_text(encoding="utf-8").lower()
    required_phrases = [
        "advisory",
        "draft",
        "owner confirmation",
        "source advisory",
        "prior deliberations",
        "not implementation approval",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in body]
    assert not missing, f"advisory-proposal skill is missing required guidance: {missing}"


def test_advisory_proposal_skill_registry_and_codex_adapter_or_pending_go() -> None:
    skill_path = REPO_ROOT / ".claude" / "skills" / "advisory-proposal" / "SKILL.md"
    adapter_path = REPO_ROOT / ".codex" / "skills" / "advisory-proposal" / "SKILL.md"
    if not skill_path.exists() and not adapter_path.exists():
        _assert_pending_go(
            "gtkb-wi5055-advisory-proposal-skill",
            "TEST-11293",
            "config/agent-control/harness-capability-registry.toml",
        )
        return

    registry = tomllib.loads(
        (REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml").read_text(encoding="utf-8")
    )
    capabilities = {
        str(item.get("canonical_name")): item
        for item in registry.get("capabilities", [])
        if isinstance(item, dict) and item.get("kind") == "skill"
    }
    capability = capabilities.get("advisory-proposal")
    assert capability is not None, "advisory-proposal skill must be registered"
    assert capability.get("canonical_source") == ".claude/skills/advisory-proposal/SKILL.md"
    assert capability.get("codex", {}).get("status") == "adapter"
    assert adapter_path.is_file(), "Codex advisory-proposal adapter must exist"
    adapter = adapter_path.read_text(encoding="utf-8")
    assert "GTKB-CODEX-SKILL-ADAPTER" in adapter
    assert "Canonical source: .claude/skills/advisory-proposal/SKILL.md" in adapter
