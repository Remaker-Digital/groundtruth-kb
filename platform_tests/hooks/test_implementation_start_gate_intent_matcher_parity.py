"""Regression lock: intent-matcher parity in the harness projector profiles (WI-6542).

The implementation-start gate is registered per harness by neutral INTENT, and the
projector translates each intent into that harness's native tool-matcher vocabulary
through ``[harnesses.<name>.intent_matchers]`` in ``scripts/harness_projection/profiles.toml``.

A matcher that omits a tool the harness actually exposes is a silent authorization
bypass: the gate simply never fires for work done through the omitted tool, and
nothing reports an error. WI-5481 recorded exactly that failure for a shell tool
missing from ``shell_exec``.

That specific gap is closed in the profile today. These tests exist so it cannot
silently reopen: they assert the required-minimum tool coverage per intent against the
REAL profile file, so a future projector edit that drops a tool fails here rather than
in production. Behavioural against the live file by deliberate choice - a fixture copy
would pass while the shipped profile regressed, which is the defect class this locks.

Authority: WI-6542; SPEC-1662 (assertions must be behavioural, not structural presence
checks); DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILES_PATH = REPO_ROOT / "scripts" / "harness_projection" / "profiles.toml"

# Canonical neutral intents the projector translates. ``all`` is intentionally the
# empty matcher (match everything) and is therefore exempt from the non-empty rule.
CANONICAL_INTENTS = ("file_write", "shell_exec", "read_access", "all")
EMPTY_BY_DESIGN = frozenset({"all"})

# Required-minimum coverage per profile: tools that profile exposes and that the
# named intent MUST therefore match. A profile may legitimately match MORE than
# this; it may never match less. Keyed by profile name so a new profile does not
# silently inherit another profile's expectations.
#
# The shell entry is the WI-5481 regression lock: both shell-executing tools must
# stay in the matcher, because omitting either one silently disables the gate for
# work performed through it.
REQUIRED_COVERAGE: dict[str, dict[str, tuple[str, ...]]] = {
    "claude": {
        "file_write": ("Write", "Edit"),
        "shell_exec": ("Bash", "PowerShell"),
        "read_access": ("Read", "Grep", "Glob"),
    },
}


def _load_profiles() -> dict:
    with PROFILES_PATH.open("rb") as handle:
        return tomllib.load(handle)


def _profiles_with_matchers() -> list[str]:
    harnesses = _load_profiles().get("harnesses", {})
    return sorted(name for name, body in harnesses.items() if "intent_matchers" in body)


def _matchers(profile: str) -> dict[str, str]:
    return _load_profiles()["harnesses"][profile]["intent_matchers"]


def _alternatives(matcher: str) -> list[str]:
    return [part for part in matcher.split("|") if part]


def test_profiles_file_is_present_and_parses() -> None:
    """The lock is worthless if it silently skips a missing or malformed file."""
    assert PROFILES_PATH.is_file(), f"projector profiles missing at {PROFILES_PATH}"
    assert _profiles_with_matchers(), "no harness profile declares intent_matchers"


@pytest.mark.parametrize("profile", _profiles_with_matchers())
def test_profile_declares_every_canonical_intent(profile: str) -> None:
    """A profile that maps intents at all must map all of them.

    A missing intent key is the same silent bypass as an incomplete matcher: the
    projector has no native vocabulary to emit, so the gate is simply not registered
    for that intent on that harness.
    """
    declared = _matchers(profile)
    missing = [intent for intent in CANONICAL_INTENTS if intent not in declared]
    assert not missing, f"{profile} intent_matchers missing intents: {missing}"


@pytest.mark.parametrize("profile", _profiles_with_matchers())
def test_matchers_are_non_empty_except_where_empty_by_design(profile: str) -> None:
    """An accidentally empty matcher matches nothing and disables the gate."""
    for intent, matcher in _matchers(profile).items():
        if intent in EMPTY_BY_DESIGN:
            continue
        assert matcher.strip(), f"{profile}.{intent} is empty; the gate would never fire"


@pytest.mark.parametrize("profile", _profiles_with_matchers())
def test_matcher_alternatives_are_unique(profile: str) -> None:
    """Duplicate alternatives indicate a merge or edit error worth catching early."""
    for intent, matcher in _matchers(profile).items():
        alternatives = _alternatives(matcher)
        duplicates = sorted({alt for alt in alternatives if alternatives.count(alt) > 1})
        assert not duplicates, f"{profile}.{intent} repeats alternatives: {duplicates}"


@pytest.mark.parametrize("profile", sorted(REQUIRED_COVERAGE))
def test_required_tool_coverage_is_present(profile: str) -> None:
    """Every tool the profile exposes for an intent is matched by that intent.

    This is the WI-6542 deliverable. Dropping a tool from a matcher is invisible at
    runtime - the gate does not error, it just stops firing - so the coverage floor is
    asserted here rather than left to be discovered as a bypass.
    """
    declared = _matchers(profile)
    for intent, required_tools in REQUIRED_COVERAGE[profile].items():
        alternatives = _alternatives(declared[intent])
        missing = [tool for tool in required_tools if tool not in alternatives]
        assert not missing, (
            f"{profile}.{intent} no longer matches {missing}; "
            f"the implementation-start gate would not fire for work done through "
            f"those tools. Declared: {declared[intent]!r}"
        )


def test_shell_exec_still_covers_both_shell_tools() -> None:
    """Named regression lock for WI-5481, asserted independently of the table above.

    Kept as its own test so the failure output names the original defect directly,
    rather than surfacing only as one entry in a parametrized coverage table.
    """
    alternatives = _alternatives(_matchers("claude")["shell_exec"])
    for tool in ("Bash", "PowerShell"):
        assert tool in alternatives, (
            f"shell_exec dropped {tool!r} - this reopens the WI-5481 "
            f"implementation-start gate bypass. Declared: {alternatives}"
        )
