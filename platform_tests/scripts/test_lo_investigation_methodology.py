"""Tests for Loyal Opposition investigation-methodology rule anchors."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# The neutral baseline rule is the one authored carrier (M15, D15/D34: the byte-identical scaffold copy is
# retired; hosts read the rule on demand from the baseline).
RULE_SURFACES = (Path(".harness-baseline-configuration/rules/loyal-opposition.md"),)

METHODOLOGY_ANCHORS = (
    "read source, inspect artifacts, run the required tests and use current cli queries or diagnostics",
    "record the commands or inspections actually performed, their outcomes and what they establish",
    "execute the full applicable plan",
    "a narrow passing suite, source hash or earlier review does not prove completion",
    "do not repair the implementation during its independent review",
    "author go when the complete proposal is supported",
    "author verified only after independently establishing the complete intended result",
)

IMPLEMENTATION_TARGETS = (
    Path(".harness-baseline-configuration/rules/loyal-opposition.md"),
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
    # The rule is wrapped prose; anchors are matched on whitespace-normalized lowercase text.
    return " ".join((REPO_ROOT / path).read_text(encoding="utf-8").lower().split())


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
