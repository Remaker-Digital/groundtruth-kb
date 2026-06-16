# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for no-index bridge scaffolding in dual-agent projects (WI-MVP-1)."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project


def _make_options(profile: str, tmp_path: Path, **kwargs: object) -> ScaffoldOptions:
    return ScaffoldOptions(
        project_name="My Test Project",
        profile=profile,
        owner="Test Owner",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
        **kwargs,  # type: ignore[arg-type]
    )


def test_bridge_directory_marker_created_for_dual_agent(tmp_path: Path) -> None:
    """scaffold_project() with dual-agent profile creates bridge/.gitkeep."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    assert (tmp_path / "project" / "bridge" / ".gitkeep").exists()
    assert not (tmp_path / "project" / "bridge" / "INDEX.md").exists()


def test_bridge_directory_marker_created_for_dual_agent_webapp(tmp_path: Path) -> None:
    """scaffold_project() with dual-agent-webapp profile creates bridge/.gitkeep."""
    options = _make_options("dual-agent-webapp", tmp_path)
    scaffold_project(options)
    assert (tmp_path / "project" / "bridge" / ".gitkeep").exists()
    assert not (tmp_path / "project" / "bridge" / "INDEX.md").exists()


def test_file_bridge_protocol_contains_statuses_table(tmp_path: Path) -> None:
    """The scaffolded bridge rule contains the Statuses table."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    content = (tmp_path / "project" / ".claude" / "rules" / "file-bridge-protocol.md").read_text(
        encoding="utf-8",
    )
    assert "Statuses" in content
    assert "| NEW |" in content
    assert "| GO |" in content
    assert "| VERIFIED |" in content


def test_file_bridge_protocol_contains_prime_workflow(tmp_path: Path) -> None:
    """The scaffolded bridge rule contains the Prime Workflow section."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    content = (tmp_path / "project" / ".claude" / "rules" / "file-bridge-protocol.md").read_text(
        encoding="utf-8",
    )
    assert "Prime Workflow" in content


def test_bridge_rules_describe_loyal_opposition_workflow(tmp_path: Path) -> None:
    """The scaffolded bridge rule describes Loyal Opposition review routing."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    content = (tmp_path / "project" / ".claude" / "rules" / "file-bridge-protocol.md").read_text(
        encoding="utf-8",
    )
    assert "NEW or REVISED" in content
    assert "dispatcher/TAFE bridge state" in content


def test_bridge_index_absent_for_local_only(tmp_path: Path) -> None:
    """scaffold_project() with local-only profile does NOT create bridge/INDEX.md."""
    options = _make_options("local-only", tmp_path)
    scaffold_project(options)
    assert not (tmp_path / "project" / "bridge" / "INDEX.md").exists()


def test_bridge_inventory_no_agent_red_leakage(tmp_path: Path) -> None:
    """BRIDGE-INVENTORY.md contains no 'Agent Red' or 'ACS' references."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    content = (tmp_path / "project" / "BRIDGE-INVENTORY.md").read_text(encoding="utf-8")
    assert "Agent Red" not in content
    assert "ACS" not in content
