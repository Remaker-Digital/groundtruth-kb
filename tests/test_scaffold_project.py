# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.project.scaffold — scaffold_project and ScaffoldOptions."""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project

# ---------------------------------------------------------------------------
# ScaffoldOptions validation
# ---------------------------------------------------------------------------


def test_scaffold_options_with_invalid_profile_raises(tmp_path: Path) -> None:
    """scaffold_project() with invalid profile raises ValueError."""
    options = ScaffoldOptions(
        project_name="Test",
        profile="nonexistent-profile",
        owner="Test Owner",
        target_dir=tmp_path / "myproject",
    )
    with pytest.raises(ValueError, match="profile"):
        scaffold_project(options)


def test_scaffold_options_default_spec_scaffold_is_none() -> None:
    """ScaffoldOptions.spec_scaffold defaults to None."""
    options = ScaffoldOptions(
        project_name="Test",
        profile="local-only",
        owner="Owner",
        target_dir=Path("/tmp/test"),
    )
    assert options.spec_scaffold is None


# ---------------------------------------------------------------------------
# scaffold_project — local-only profile
# ---------------------------------------------------------------------------


def test_scaffold_project_local_only_creates_expected_files(tmp_path: Path) -> None:
    """scaffold_project() with local-only creates groundtruth.toml and groundtruth.db."""
    target = tmp_path / "myproject"
    options = ScaffoldOptions(
        project_name="Test Project",
        profile="local-only",
        owner="Test Owner",
        target_dir=target,
        seed_example=False,
        include_ci=False,
    )
    result = scaffold_project(options)
    assert result == target.resolve()
    assert (target / "groundtruth.toml").exists()
    assert (target / "groundtruth.db").exists()
    assert (target / "CLAUDE.md").exists()


def test_scaffold_project_local_only_no_bridge_files(tmp_path: Path) -> None:
    """local-only profile should NOT create AGENTS.md or BRIDGE-INVENTORY.md."""
    target = tmp_path / "localproject"
    options = ScaffoldOptions(
        project_name="Local Project",
        profile="local-only",
        owner="Owner",
        target_dir=target,
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    # Bridge files should NOT exist for local-only
    assert not (target / "AGENTS.md").exists()
    assert not (target / "BRIDGE-INVENTORY.md").exists()


# ---------------------------------------------------------------------------
# scaffold_project — dual-agent profile
# ---------------------------------------------------------------------------


def test_scaffold_project_dual_agent_creates_bridge_files(tmp_path: Path) -> None:
    """scaffold_project() with dual-agent creates bridge-related files."""
    target = tmp_path / "dualproject"
    options = ScaffoldOptions(
        project_name="Dual Agent Project",
        profile="dual-agent",
        owner="Owner",
        target_dir=target,
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    # At minimum, AGENTS.md should be created for dual-agent
    assert (target / "AGENTS.md").exists()


def test_scaffold_agents_md_uses_root_memory_path(tmp_path: Path) -> None:
    """Generated AGENTS.md names root ``MEMORY.md``, not ``memory/MEMORY.md``.

    Codex GO condition (``bridge/gtkb-canonical-terminology-surface-implementation-006.md``
    P1 carried forward to ``-008``): GT-KB scaffolds ``MEMORY.md`` at repo root
    per ADR-0001, so the AGENTS.md startup checklist must reference the root
    path — not the ``memory/`` subdirectory variant.
    """
    target = tmp_path / "agents-md-path"
    options = ScaffoldOptions(
        project_name="AGENTS.md Path Check",
        profile="dual-agent",
        owner="Owner",
        target_dir=target,
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    agents_md = target / "AGENTS.md"
    assert agents_md.exists(), "dual-agent profile must create AGENTS.md"
    content = agents_md.read_text(encoding="utf-8")
    assert "memory/MEMORY.md" not in content, (
        "Generated AGENTS.md must NOT reference 'memory/MEMORY.md'; "
        "GT-KB places MEMORY.md at repo root per ADR-0001. "
        "See bridge/gtkb-canonical-terminology-surface-implementation-008.md."
    )
    assert "MEMORY.md" in content, (
        "Generated AGENTS.md must reference root 'MEMORY.md' in the startup checklist."
    )
