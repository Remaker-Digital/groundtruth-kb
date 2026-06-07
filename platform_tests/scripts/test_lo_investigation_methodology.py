"""Tests for Loyal Opposition investigation-methodology rule anchors."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

RULE_SURFACES = (
    Path(".claude/rules/loyal-opposition.md"),
    Path("groundtruth-kb/templates/rules/loyal-opposition.md"),
)

METHODOLOGY_ANCHORS = (
    "read-only repository inspection",
    "scripts",
    "tests",
    "cli queries",
    "membase or database reads",
    "methodology trail",
    "reproduce or exceed the review depth",
    "proposal review",
    "implementation verification",
)

IMPLEMENTATION_TARGETS = (
    Path(".claude/rules/loyal-opposition.md"),
    Path("groundtruth-kb/templates/rules/loyal-opposition.md"),
    Path("platform_tests/scripts/test_lo_investigation_methodology.py"),
    Path(
        ".groundtruth/formal-artifact-approvals/"
        "2026-06-07-claude-rules-loyal-opposition-md-investigation-methodology-slice-2.json"
    ),
)

FORBIDDEN_TARGET_FRAGMENTS = (
    "E:/Claude-Playground",
    "E:\\Claude-Playground",
    "https://github.com/mike-remakerdigital/agent-red",
)


def _rule_text(path: Path) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8").lower()


@pytest.mark.parametrize("path", RULE_SURFACES)
def test_lo_investigation_methodology_anchors_present(path: Path) -> None:
    text = _rule_text(path)

    missing = [anchor for anchor in METHODOLOGY_ANCHORS if anchor not in text]

    assert not missing, f"{path.as_posix()} missing anchors: {missing}"


def test_slice_2_target_paths_remain_in_root() -> None:
    root = REPO_ROOT.resolve()

    for target in IMPLEMENTATION_TARGETS:
        resolved = (REPO_ROOT / target).resolve()
        assert resolved.is_relative_to(root)


def test_slice_2_target_paths_do_not_reference_archive_or_external_repo() -> None:
    target_text = "\n".join(path.as_posix() for path in IMPLEMENTATION_TARGETS)

    for forbidden in FORBIDDEN_TARGET_FRAGMENTS:
        assert forbidden not in target_text
