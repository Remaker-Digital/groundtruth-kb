# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for gt project doctor bridge-readiness accuracy fixes (WI-MVP-5)."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project

_BRIDGE_RULE_FILES = (
    "file-bridge-protocol.md",
    "bridge-essential.md",
    "deliberation-protocol.md",
)


def _make_dual_agent_project(tmp_path: Path) -> Path:
    """Scaffold a minimal dual-agent project and return the project path."""
    options = ScaffoldOptions(
        project_name="Doctor Test Project",
        profile="dual-agent",
        owner="Test Owner",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    return tmp_path / "project"


def _make_local_only_project(tmp_path: Path) -> Path:
    """Scaffold a minimal local-only project and return the project path."""
    options = ScaffoldOptions(
        project_name="Local Only Project",
        profile="local-only",
        owner="Test Owner",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    return tmp_path / "project"


# ---------------------------------------------------------------------------
# bridge/INDEX.md absent → OK
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Required bridge rule file absent → WARN
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# local-only profile → no bridge WARN
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Regression guard: doctor does not depend on retired INDEX.md
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Doctor passes when bridge directory + all rule files present
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Claude Code check is labeled as availability (not auth)
# ---------------------------------------------------------------------------


def test_claude_code_check_labeled_as_availability(tmp_path: Path) -> None:
    """The Claude Code doctor check is labeled as availability, not auth validation."""
    from groundtruth_kb.project.doctor import _check_claude_code

    check = _check_claude_code()
    assert "availability" in check.name.lower() or "availability" in (check.message or "").lower()
    assert "auth" not in check.name.lower()
