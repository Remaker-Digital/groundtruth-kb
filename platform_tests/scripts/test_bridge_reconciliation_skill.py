"""Discoverability + content tests for the bridge-reconciliation operator skill (WI-4237).

WI-4237 (Option B, DELIB-2026-06-21-WI4237-OPTION-B-DELIVER-ALL-HARNESSES)
delivers the canonical Claude-native operator skill AND its adapter mirrors
across all harness surfaces (.codex / .agent / .api-harness) plus the
harness-capability-registry entry, generated through the canonical adapter
generators. These tests assert the canonical surface, the skill's operator
contract, and cross-harness discoverability.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_SKILL = REPO_ROOT / ".claude" / "skills" / "bridge-reconciliation" / "SKILL.md"


def _skill_text() -> str:
    return CANONICAL_SKILL.read_text(encoding="utf-8")


def test_canonical_skill_exists_with_frontmatter() -> None:
    assert CANONICAL_SKILL.is_file(), "canonical bridge-reconciliation SKILL.md must exist"
    lines = _skill_text().splitlines()
    assert lines and lines[0].strip() == "---", "SKILL.md must open with YAML frontmatter"
    assert any(line.startswith("name: bridge-reconciliation") for line in lines[:20])
    assert any(line.startswith("description:") for line in lines[:20])


def test_skill_cites_surviving_no_index_surfaces() -> None:
    text = _skill_text()
    for surface in (
        "gt bridge dispatch health",
        "gt bridge dispatch status",
        "wrap_scan_reconciliation.py",
        "bridge_verified_backlog_reconciler.py",
        "--dry-run",
    ):
        assert surface in text, f"SKILL.md must cite surviving surface: {surface}"


def test_skill_does_not_present_retired_index_era_commands_as_live() -> None:
    text = _skill_text()
    # The retired INDEX-era reconcile CLIs must never appear as live instructions.
    assert "gt bridge reconcile" not in text
    # bridge/INDEX.md may appear only inside a forbidding warning, never as live state.
    assert "bridge/INDEX.md" in text  # referenced...
    assert "never treat" in text.lower()  # ...only to forbid it as current bridge state


def test_skill_enforces_no_bulk_mutation_and_gates() -> None:
    lowered = _skill_text().lower()
    assert "no-bulk-mutation" in lowered
    assert "askuserquestion" in lowered
    assert "project authorization" in lowered or "project-authorization" in lowered
    assert "implementation-start" in lowered
    assert "one class at a time" in lowered or "one triage class" in lowered


def test_skill_documents_finding_classification() -> None:
    text = _skill_text()
    # The operator workflow classifies findings by the reconciler's reason taxonomy.
    for reason in (
        "umbrella_children_all_verified",
        "parent_evidence_canonical_relaxed",
        "linked_bridge_not_verified",
        "missing_parent_evidence",
    ):
        assert reason in text, f"SKILL.md must document finding class: {reason}"


def test_skill_mirrored_and_discoverable_across_all_harnesses() -> None:
    """WI-4237 Option B: the skill is delivered + discoverable on every harness surface."""
    mirrors = {
        "codex": REPO_ROOT / ".codex" / "skills" / "bridge-reconciliation" / "SKILL.md",
        "antigravity": REPO_ROOT / ".agent" / "skills" / "bridge-reconciliation" / "SKILL.md",
        "api": REPO_ROOT / ".api-harness" / "skills" / "bridge-reconciliation" / "SKILL.md",
    }
    for name, path in mirrors.items():
        assert path.is_file(), f"{name} bridge-reconciliation adapter missing: {path}"
        text = path.read_text(encoding="utf-8")
        assert "bridge-reconciliation" in text
        # generated adapters are compact pointers back to the canonical source
        assert ".claude/skills/bridge-reconciliation/SKILL.md" in text

    registry = (REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml").read_text(encoding="utf-8")
    assert "skill.bridge-reconciliation" in registry
    assert 'canonical_source = ".claude/skills/bridge-reconciliation/SKILL.md"' in registry
