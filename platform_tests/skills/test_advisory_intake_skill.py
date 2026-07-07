"""Tests for the Prime Builder advisory-intake skill contract (WI-5056/WI-5059)."""

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
    assert "source summarization" in proposal
    assert "explicit project/WI approval" in proposal


def test_advisory_intake_skill_content_or_pending_go() -> None:
    skill_path = REPO_ROOT / ".claude" / "skills" / "advisory-intake" / "SKILL.md"
    if not skill_path.exists():
        _assert_pending_go(
            "gtkb-wi5056-prime-advisory-intake-skill",
            "TEST-11294",
            ".claude/skills/advisory-intake/SKILL.md",
        )
        return

    body = skill_path.read_text(encoding="utf-8").lower()
    required_phrases = [
        "live advisory",
        "owner-grilling",
        "project",
        "work item",
        "explicit owner approval",
        "child proposal",
        "go",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in body]
    assert not missing, f"advisory-intake skill is missing required guidance: {missing}"


def test_advisory_intake_skill_registry_and_codex_adapter_or_pending_go() -> None:
    skill_path = REPO_ROOT / ".claude" / "skills" / "advisory-intake" / "SKILL.md"
    adapter_path = REPO_ROOT / ".codex" / "skills" / "advisory-intake" / "SKILL.md"
    if not skill_path.exists() and not adapter_path.exists():
        _assert_pending_go(
            "gtkb-wi5056-prime-advisory-intake-skill",
            "TEST-11294",
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
    capability = capabilities.get("advisory-intake")
    assert capability is not None, "advisory-intake skill must be registered"
    assert capability.get("canonical_source") == ".claude/skills/advisory-intake/SKILL.md"
    assert capability.get("codex", {}).get("status") == "adapter"
    assert adapter_path.is_file(), "Codex advisory-intake adapter must exist"
    adapter = adapter_path.read_text(encoding="utf-8")
    assert "GTKB-CODEX-SKILL-ADAPTER" in adapter
    assert "Canonical source: .claude/skills/advisory-intake/SKILL.md" in adapter
