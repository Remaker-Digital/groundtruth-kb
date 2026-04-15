# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for bridge protocol rule file generation in dual-agent scaffold (WI-MVP-2)."""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project

_BRIDGE_RULE_FILES = (
    "file-bridge-protocol.md",
    "bridge-essential.md",
    "deliberation-protocol.md",
)


def _make_options(profile: str, tmp_path: Path, **kwargs: object) -> ScaffoldOptions:
    return ScaffoldOptions(
        project_name="Bridge Rules Project",
        profile=profile,
        owner="Test Owner",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
        **kwargs,  # type: ignore[arg-type]
    )


def test_bridge_rules_present_for_dual_agent_webapp(tmp_path: Path) -> None:
    """All 3 bridge rule files are present after dual-agent-webapp scaffold."""
    options = _make_options("dual-agent-webapp", tmp_path)
    scaffold_project(options)
    rules_dir = tmp_path / "project" / ".claude" / "rules"
    for rule_file in _BRIDGE_RULE_FILES:
        assert (rules_dir / rule_file).exists(), f"Missing bridge rule: {rule_file}"


def test_bridge_rules_present_for_dual_agent(tmp_path: Path) -> None:
    """All 3 bridge rule files are present after dual-agent scaffold."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    rules_dir = tmp_path / "project" / ".claude" / "rules"
    for rule_file in _BRIDGE_RULE_FILES:
        assert (rules_dir / rule_file).exists(), f"Missing bridge rule: {rule_file}"


def test_no_agent_red_in_generated_rule_files(tmp_path: Path) -> None:
    """No 'Agent Red' text appears in any generated bridge rule file."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    rules_dir = tmp_path / "project" / ".claude" / "rules"
    for rule_file in _BRIDGE_RULE_FILES:
        content = (rules_dir / rule_file).read_text(encoding="utf-8")
        assert "Agent Red" not in content, f"'Agent Red' found in {rule_file}"


def test_bridge_essential_contains_gt_project_doctor(tmp_path: Path) -> None:
    """Generated bridge-essential.md contains the 'gt project doctor' command string."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    content = (tmp_path / "project" / ".claude" / "rules" / "bridge-essential.md").read_text(
        encoding="utf-8"
    )
    assert "gt project doctor" in content


def test_bridge_essential_contains_scheduler_not_implemented_message(tmp_path: Path) -> None:
    """Generated bridge-essential.md contains the scheduler-not-implemented notice."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    content = (tmp_path / "project" / ".claude" / "rules" / "bridge-essential.md").read_text(
        encoding="utf-8"
    )
    assert "Bridge scheduler commands are not implemented in this release." in content


def test_local_only_does_not_include_bridge_rule_files(tmp_path: Path) -> None:
    """local-only profile should only have prime-builder.md, not the bridge-specific rules."""
    options = _make_options("local-only", tmp_path)
    scaffold_project(options)
    rules_dir = tmp_path / "project" / ".claude" / "rules"
    assert (rules_dir / "prime-builder.md").exists()
    for rule_file in _BRIDGE_RULE_FILES:
        assert not (rules_dir / rule_file).exists(), f"Bridge rule unexpectedly present: {rule_file}"
