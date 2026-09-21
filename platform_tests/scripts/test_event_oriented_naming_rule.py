"""WI-6745: event-oriented naming rule for hook-triggered concepts.

Asserts that the naming rule is present on the always-loaded governance rule
surface, that it follows the same section grammar as the sibling principles,
and that the reifying entity-noun vocabulary the rule exists to prevent does
not reappear on that surface.

The rule itself is a judgment, not a mechanical test: whether a name is
event-shaped cannot be decided by regex. These assertions therefore cover
presence, shape, and the one concrete anti-pattern vocabulary named by the
approved proposal -- and deliberately claim nothing beyond that.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RULE_PATH = PROJECT_ROOT / ".harness-baseline-configuration" / "rules" / "governance-principles.md"

SECTION_HEADING = "## Event-Oriented Naming Principle"

# The reifying entity noun this rule exists to prevent. Scoped deliberately:
# a bare "packet" match would collide with unrelated prose already on this
# surface ("example packets" in the Deterministic Services Principle), so the
# assertion targets the specific noun that accreted a module, a lifecycle, an
# archive, and a cache around a hook-triggered concept.
ANTI_PATTERN_VOCABULARY = ("envelope",)


@pytest.fixture(scope="module")
def rule_text() -> str:
    assert RULE_PATH.is_file(), f"governance rule surface missing: {RULE_PATH}"
    return RULE_PATH.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Return the body of one '## ' section, exclusive of the next heading."""
    start = text.index(heading)
    remainder = text[start + len(heading) :]
    match = re.search(r"^## ", remainder, flags=re.MULTILINE)
    return remainder[: match.start()] if match else remainder


def test_naming_rule_section_is_present(rule_text: str) -> None:
    assert SECTION_HEADING in rule_text, (
        "Event-Oriented Naming Principle is absent from the always-loaded "
        "governance rule surface; the rule is unreachable at session start."
    )


def test_naming_rule_states_the_event_form_preference(rule_text: str) -> None:
    body = _section(rule_text, SECTION_HEADING)
    assert "init-trigger" in body
    assert "on-init" in body
    assert "open-hook" in body
    assert "when they fire" in body, "rule must state the when-does-it-fire test"


def test_naming_rule_matches_sibling_section_grammar(rule_text: str) -> None:
    """Same shape as the other principles: justification, mandate, relationship."""
    body = _section(rule_text, SECTION_HEADING)
    assert "Justification:" in body
    assert "Operational mandate:" in body
    assert "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001" in body
    # M15 (edit-m15-37): capture routes through the current backlog writer under current formal requirements;
    # a separate approval-evidence artifact is a retired carrier and is not required.
    assert "through the current backlog writer" in body, "capture must route to the backlog"
    assert "does not require a separate" in body, (
        "rule must state that owner direction needs no approval-evidence artifact"
    )
    numbered = re.findall(r"^\d+\. ", body, flags=re.MULTILINE)
    assert len(numbered) >= 3, "operational mandate must enumerate its obligations"


def test_naming_rule_does_not_overclaim_enforceability(rule_text: str) -> None:
    body = _section(rule_text, SECTION_HEADING)
    assert "is a judgment about the actual behavior" in body and "cannot establish complete" in body, (
        "rule must record that event-shapedness is a judgment rather than a "
        "mechanical test, so a future reader does not treat it as enforced"
    )


@pytest.mark.parametrize("noun", ANTI_PATTERN_VOCABULARY)
def test_anti_pattern_vocabulary_absent_from_rule_surface(rule_text: str, noun: str) -> None:
    matches = [
        line for line in rule_text.splitlines() if re.search(rf"\b{re.escape(noun)}s?\b", line, flags=re.IGNORECASE)
    ]
    assert matches == [], f"reifying vocabulary {noun!r} reappeared on the governance rule surface: {matches}"
