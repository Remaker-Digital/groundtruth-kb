"""WI-7526: dispatched worker prompts must not name a registry as role source.

Three dispatch surfaces injected an instruction telling every dispatched worker
to resolve its role by reading ``harness-state/harness-registry.json``:

* ``scripts/dispatcher_runtime.py`` -- in the role line of every worker prompt,
  which also told the worker to resolve its identity from
  ``harness-state/harness-identities.json``;
* ``scripts/openrouter_harness.py`` and ``scripts/ollama_harness.py`` -- the same
  claim, phrased as "the role source of truth".

Both files are absent by design. ``ADR-ELIMINATE-DURABLE-ROLE-ASSIGNMENT-001``
and ``DCL-NO-DURABLE-ROLE-IN-REGISTRY-001`` retired the registry as role
authority, and Compact Operating Guidance s0.1 states that role comes only from
the owner's literal init line or the init line in the dispatched bridge item's
header -- never from a harness registry, dispatcher configuration, projection or
prior session memory.

The instruction was therefore wrong on two counts at once: it named a forbidden
authority, and it named a file that does not exist. A worker following it
literally would fail, and a worker resolving it "helpfully" would adopt a role
from the wrong source.

These tests assert the *prompt text*, because the prompt is the surface that
reaches the worker. A reader elsewhere in the module may still consult the
registry for dispatch routing, which is a different question -- routing metadata
is not role authority.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

DISPATCH_PROMPT_SOURCES = (
    REPO_ROOT / "scripts" / "dispatcher_runtime.py",
    REPO_ROOT / "scripts" / "openrouter_harness.py",
    REPO_ROOT / "scripts" / "ollama_harness.py",
)

# Phrasings that assert a registry/identities file IS the role or identity
# source for the worker being dispatched. Comments are stripped before matching,
# so a comment explaining why the instruction was removed does not trip these.
ROLE_SOURCE_CLAIMS = (
    re.compile(r"read your assigned role from", re.IGNORECASE),
    re.compile(r"harness-registry\.json[^\n]{0,80}role source", re.IGNORECASE),
    re.compile(r"role source[^\n]{0,80}harness-registry\.json", re.IGNORECASE),
    re.compile(r"resolve your durable harness identity from", re.IGNORECASE),
)


def _source_without_comments(path: Path) -> str:
    """Return the file with whole-line ``#`` comments removed.

    The corrections left comments naming the retired files to explain why the
    instruction went away. Those are documentation of forbidden drift, which the
    guidance explicitly permits; only live prompt text is under test here.
    """
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if not line.lstrip().startswith("#")]
    return "\n".join(lines)


@pytest.mark.parametrize("source", DISPATCH_PROMPT_SOURCES, ids=lambda p: p.name)
def test_dispatched_prompt_does_not_name_a_registry_role_source(source: Path) -> None:
    if not source.is_file():
        pytest.skip(f"dispatch surface not present: {source}")
    text = _source_without_comments(source)
    offenders = [pattern.pattern for pattern in ROLE_SOURCE_CLAIMS if pattern.search(text)]
    assert not offenders, f"{source.name} still instructs a worker to take its role from a registry: {offenders}"


@pytest.mark.parametrize("source", DISPATCH_PROMPT_SOURCES, ids=lambda p: p.name)
def test_dispatched_prompt_names_the_init_line_as_role_source(source: Path) -> None:
    """Positive control: removing the wrong source must not leave none at all.

    A worker with no stated role source is worse off than one with a wrong
    source, because nothing tells it where to look.
    """
    if not source.is_file():
        pytest.skip(f"dispatch surface not present: {source}")
    text = _source_without_comments(source)
    assert "::init gtkb" in text, f"{source.name} states no canonical role source for the dispatched worker"


@pytest.mark.parametrize("source", DISPATCH_PROMPT_SOURCES, ids=lambda p: p.name)
def test_dispatched_prompt_does_not_assert_a_harness_role(source: Path) -> None:
    """A harness has no operating role, so no prompt may tell a worker it has one.

    ``dispatcher_runtime`` previously opened every worker prompt with "your active
    role is <label>", sourced from the harness's registry assignment. That states
    the obsolete concept as fact, which is worse than pointing at a retired file:
    a worker has no reason to doubt it.

    Purge, not prohibition. The correction deletes the claim rather than adding a
    counter-instruction, so this test asserts the claim's ABSENCE and not the
    presence of any warning about it.
    """
    if not source.is_file():
        pytest.skip(f"dispatch surface not present: {source}")
    text = _source_without_comments(source)
    for claim in ("your active role is", "your assigned role is", "your operating role is"):
        assert claim not in text.lower(), f"{source.name} asserts a harness-held role: {claim!r}"


def test_every_dispatch_surface_is_covered() -> None:
    """Guard against a new dispatch surface escaping this test by omission."""
    present = [path for path in DISPATCH_PROMPT_SOURCES if path.is_file()]
    assert present, "no dispatch prompt surface found; the parametrization would vacuously pass"
