"""No scaffold rule template duplicates a neutral baseline rule (M15, D15/D34); the template-only set is named."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_RULES = REPO_ROOT / ".harness-baseline-configuration" / "rules"
TEMPLATE_RULES = REPO_ROOT / "groundtruth-kb" / "templates" / "rules"
# Rules that exist only as scaffold templates (retained for M26.6, design R-C8); a new template-only rule is a
# finding to explain here.
TEMPLATE_ONLY = {"prime-bridge-collaboration-protocol.md", "session-start-orientation.md"}


def _shared_rule_names() -> list[str]:
    return sorted(path.name for path in TEMPLATE_RULES.glob("*.md") if (BASELINE_RULES / path.name).is_file())


def test_no_rule_template_duplicates_a_baseline_rule() -> None:
    """D15/D34: the baseline rule is read on demand; a template copy of it would be a second authored carrier."""
    assert _shared_rule_names() == []
    assert BASELINE_RULES.is_dir() and any(BASELINE_RULES.glob("*.md"))


def test_template_only_rules_are_the_named_set() -> None:
    template_only = {path.name for path in TEMPLATE_RULES.glob("*.md")} - set(_shared_rule_names())
    assert template_only == TEMPLATE_ONLY


@pytest.mark.parametrize("name", sorted(TEMPLATE_ONLY))
def test_template_only_rule_exists(name: str) -> None:
    assert (TEMPLATE_RULES / name).is_file()
