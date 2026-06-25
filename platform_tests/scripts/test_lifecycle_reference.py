# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural guard for WI-3352 canonical lifecycle reference surfaces."""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_METHOD = _REPO_ROOT / "groundtruth-kb" / "docs" / "method"
_STARTUP_INDEX = _REPO_ROOT / "config" / "agent-control" / "SESSION-STARTUP-INDEX.md"

_REFERENCE = _METHOD / "14-lifecycle.md"
_OVERVIEW = _METHOD / "01-overview.md"
_README = _METHOD / "README.md"

_STAGES = (
    "deliberate",
    "plan",
    "specify",
    "propose",
    "GO",
    "implement",
    "report",
    "VERIFIED",
    "commit",
)


def test_reference_exists_and_covers_all_stages() -> None:
    text = _REFERENCE.read_text(encoding="utf-8").lower()
    assert _REFERENCE.is_file()
    for stage in _STAGES:
        assert stage.lower() in text, f"missing stage token: {stage}"


def test_overview_links_reference_and_bookends() -> None:
    text = _OVERVIEW.read_text(encoding="utf-8")
    assert "14-lifecycle.md" in text
    assert "deliberate" in text.lower()
    assert "commit" in text.lower()


def test_readme_indexes_reference() -> None:
    text = _README.read_text(encoding="utf-8")
    assert "14-lifecycle.md" in text
    assert "End-to-End Lifecycle" in text


def test_startup_index_points_to_reference() -> None:
    text = _STARTUP_INDEX.read_text(encoding="utf-8")
    assert "14-lifecycle.md" in text
    assert "new-agent" in text.lower() or "new agent" in text.lower()
