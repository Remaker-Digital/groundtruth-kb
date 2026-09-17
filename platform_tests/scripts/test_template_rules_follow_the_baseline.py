"""Scaffold rule templates are copies of the neutral baseline rules, never a second authored carrier."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_RULES = REPO_ROOT / ".harness-baseline-configuration" / "rules"
TEMPLATE_RULES = REPO_ROOT / "groundtruth-kb" / "templates" / "rules"
# Rules that exist only as scaffold templates today; a new template-only rule is a finding to explain here.
TEMPLATE_ONLY = {"bridge-poller-canonical.md", "prime-bridge-collaboration-protocol.md", "session-start-orientation.md"}


def _shared_rule_names() -> list[str]:
    return sorted(path.name for path in TEMPLATE_RULES.glob("*.md") if (BASELINE_RULES / path.name).is_file())


def test_every_shared_rule_template_is_byte_identical_to_the_baseline_rule() -> None:
    names = _shared_rule_names()
    assert names, "no shared rule templates found"
    diverged = [name for name in names if (TEMPLATE_RULES / name).read_bytes() != (BASELINE_RULES / name).read_bytes()]
    assert diverged == [], f"scaffold rule templates diverged from the neutral baseline: {diverged}"


def test_template_only_rules_are_the_named_set() -> None:
    template_only = {path.name for path in TEMPLATE_RULES.glob("*.md")} - set(_shared_rule_names())
    assert template_only == TEMPLATE_ONLY


@pytest.mark.parametrize("name", sorted(TEMPLATE_ONLY))
def test_template_only_rule_exists(name: str) -> None:
    assert (TEMPLATE_RULES / name).is_file()
