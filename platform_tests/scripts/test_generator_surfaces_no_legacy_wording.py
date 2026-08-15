"""D3 generator-surfaces purge — no retired-substrate wording in generators.

The proposal generators emit text into governed bridge artifacts. While they
carry retired-substrate wording, the D3 purge is self-undoing: every newly
authored proposal inherits the phrasing being purged. The defect was found the
honest way — the scaffold emitted the offending line into the draft for the very
thread whose subject was removing it.

Authority:

- ``ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`` — a generator that re-emits an
  obsolete reference prevents the purge obligation from ever being discharged.
- ``DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`` — classified purge required.
- ``DELIB-20260807011969`` B1 — the store is named ``bridge state``.
- ``GOV-SOURCE-OF-TRUTH-FRESHNESS-001`` — emitted claims naming a retired
  substrate propagate a stale claim into every new artifact.

Bridge thread: ``gtkb-d3-generator-surfaces-purge`` (GO at ``-002``).

Pattern width is deliberate, per the ``-002`` P2 finding. The ``-001``
acceptance criterion keyed on the token ``TAFE`` and therefore guarded only two
of the four sites the slice edits; ``gtkb_propose_scaffold.py`` lines 13 and 265
carry ``dispatcher publication`` with no ``TAFE`` token. With dispatch disabled
and manual advancement in force, a checklist instructing authors to use a helper
for "dispatcher publication" describes a substrate that is not running — live
direction, not documentation. The pattern below fails on any retired-substrate
reference so all four sites are guarded.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GENERATOR_MODULES = (
    PROJECT_ROOT / "scripts" / "gtkb_propose_scaffold.py",
    PROJECT_ROOT / "scripts" / "gtkb_bridge_writer.py",
)

# Any reference to the retired dispatch substrate, not only TAFE-bearing ones.
RETIRED_SUBSTRATE_RE = re.compile(
    r"TAFE"
    r"|dispatcher/TAFE"
    r"|TAFE/dispatcher"
    r"|dispatcher[ _-]daemon"
    r"|dispatcher publication"
    r"|smart poller"
    r"|OS poller",
    re.IGNORECASE,
)

COMPETING_TERM_RE = re.compile(r"canonical bridge state", re.IGNORECASE)


def _offenses(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return [
        f"{path.name}:{n}: {line.strip()}"
        for n, line in enumerate(text.splitlines(), start=1)
        if RETIRED_SUBSTRATE_RE.search(line)
    ]


@pytest.mark.parametrize("module", GENERATOR_MODULES, ids=lambda p: p.name)
def test_generator_module_has_no_retired_substrate_wording(module: Path) -> None:
    """No generator module references the retired dispatch substrate."""
    assert module.is_file(), f"generator module missing: {module}"
    offenses = _offenses(module)
    assert not offenses, (
        "Retired-substrate wording found in a generator module. These modules "
        "emit text into governed bridge artifacts, so the wording propagates "
        "into every artifact they generate:\n  " + "\n  ".join(offenses)
    )


def test_scaffold_emitted_template_is_clean() -> None:
    """The emitted proposal template carries no retired-substrate wording.

    Guards the operative site specifically: line 233 lives inside the emitted
    ``## Bridge Filing`` block, so any wording there is written into every draft
    the scaffold produces, not merely documented in the module.
    """
    text = (PROJECT_ROOT / "scripts" / "gtkb_propose_scaffold.py").read_text(encoding="utf-8")
    # Anchor on the emitted body text, not the "## Bridge Filing" heading: that
    # heading also appears in the required-sections tuple, whose first
    # occurrence precedes the template and would locate the wrong region.
    anchor = "This proposal is filed under"
    assert anchor in text, (
        "The emitted Bridge Filing body is absent from the scaffold; the "
        "operative site this guard protects no longer exists in expected form."
    )
    marker = text.index(anchor)
    block = text[marker : marker + 400]
    assert not RETIRED_SUBSTRATE_RE.search(block), (
        "Retired-substrate wording inside the emitted Bridge Filing template. "
        "This text is written into every generated draft."
    )
    assert "Bridge state" in block or "bridge state" in block, (
        "The emitted template no longer names the bridge state store; the purge "
        "must rename the referent, not delete it."
    )


@pytest.mark.parametrize("module", GENERATOR_MODULES, ids=lambda p: p.name)
def test_no_competing_replacement_term(module: Path) -> None:
    """`canonical bridge state` was rejected by DELIB-20260807011969."""
    text = module.read_text(encoding="utf-8", errors="replace")
    assert not COMPETING_TERM_RE.search(text), (
        f"{module.name} reintroduces the rejected competing term "
        "'canonical bridge state'; the settled term is 'bridge state'."
    )


def test_pattern_would_have_caught_the_untokened_sites() -> None:
    """Regression guard on the guard itself (per the -002 P2 finding).

    The superseded criterion keyed on ``TAFE`` and missed the two
    ``dispatcher publication`` sites. This asserts the widened pattern catches a
    retired-substrate reference that carries no ``TAFE`` token, so the guard
    cannot silently narrow back to the defect it was written to close.
    """
    untokened = "credential-scanned write and dispatcher publication (do NOT write"
    assert "TAFE" not in untokened
    assert RETIRED_SUBSTRATE_RE.search(untokened), (
        "The pattern narrowed back to TAFE-only matching and would again leave two of the four sites unguarded."
    )
