"""Adopter templates and golden fixtures carry no retired-substrate authority wording.

WI-6018 / `bridge/gtkb-d3-adopter-templates-purge` (GO at `-006`).

CENSUS CRITERION (owner decision, 2026-08-15). The approved proposal asserted a
flat "zero legacy-wording matches" across the template tree. That criterion is
unsatisfiable as written: ``templates/rules/bridge-poller-canonical.md`` and
``templates/bridge-os-poller-setup-prompt.md`` are deprecation stubs whose
*subject* is the retired poller, and whose retained content includes a real
archive path (``archive/smart-poller-2026-05-09/``) and real record identifiers
(``DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09``). The GO simultaneously
required those stubs to keep their retention sentence and their Slice 4
Open Follow-On section 7 reference.

The owner resolved this by adopting the semantic GT-KB's own baseline already
uses: purge retired-substrate *authority claims*, keep accurate history.
Concretely, and mechanically:

* ``TAFE`` must not appear at all. It names a retired coordination substrate and
  never appears in the purged baseline tree.
* ``smart poller`` / ``OS poller`` may appear, but only as past-tense history,
  archive paths, or record identifiers — which is exactly what the two
  deprecation stubs and the retirement narrative require.

METHOD (per ``WI-6327``). The census walks the filesystem and matches
case-insensitively. ``git grep`` is tracked-only and would miss untracked files;
``test_census_is_filesystem_based`` demonstrates that difference rather than
asserting it.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = PROJECT_ROOT / "groundtruth-kb" / "templates"
GOLDEN_ROOT = PROJECT_ROOT / "groundtruth-kb" / "tests" / "fixtures" / "scaffold_golden"

TEXT_SUFFIXES = {".md", ".py", ".toml", ".json", ".txt"}

#: Retired coordination substrate. Never legitimate in an adopter template.
TAFE_RE = re.compile(r"TAFE", re.IGNORECASE)

#: Retired poller mechanisms. Legitimate only as history / paths / record ids.
POLLER_RE = re.compile(r"(?:smart[\s-]poller|\bOS[\s-]poller)", re.IGNORECASE)

#: Purge artifact: the replacement term accidentally doubled.
DOUBLED_TERM_RE = re.compile(r"\b(bridge[\s-]state)\b\s+bridge[\s-]state\b", re.IGNORECASE)

POLLER_CANONICAL = TEMPLATE_ROOT / "rules" / "bridge-poller-canonical.md"
POLLER_SETUP_PROMPT = TEMPLATE_ROOT / "bridge-os-poller-setup-prompt.md"


def _text_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _census(root: Path, pattern: re.Pattern[str]) -> dict[str, int]:
    """Filesystem-walk census. Sees untracked files; case-insensitive."""
    hits: dict[str, int] = {}
    for path in _text_files(root):
        count = len(pattern.findall(_read(path)))
        if count:
            hits[path.relative_to(PROJECT_ROOT).as_posix()] = count
    return hits


def _git_tracked_census(root: Path, pattern: str) -> dict[str, int]:
    """Deliberately tracked-only census, used as the negative control."""
    try:
        completed = subprocess.run(
            ["git", "grep", "-c", "-i", "-E", pattern, "--", str(root.relative_to(PROJECT_ROOT).as_posix())],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError):  # pragma: no cover - git absent
        pytest.skip("git unavailable")
    hits: dict[str, int] = {}
    for line in completed.stdout.splitlines():
        path, _, count = line.rpartition(":")
        if path and count.isdigit():
            hits[path] = int(count)
    return hits


# --------------------------------------------------------------------------
# Authority-claim purge
# --------------------------------------------------------------------------


def test_templates_carry_no_tafe_references() -> None:
    """No adopter template names the retired TAFE substrate."""
    hits = _census(TEMPLATE_ROOT, TAFE_RE)
    assert hits == {}, f"TAFE references remain in adopter templates: {hits}"


def test_golden_fixtures_carry_no_tafe_references() -> None:
    """Scaffold output snapshots carry no TAFE either (lockstep with templates)."""
    hits = _census(GOLDEN_ROOT, TAFE_RE)
    assert hits == {}, f"TAFE references remain in golden fixtures: {hits}"


def test_no_doubled_replacement_term() -> None:
    """The purge did not leave a doubled `bridge state bridge state` artifact.

    This regression exists because the GT-KB baseline's own D3 purge produced
    exactly that artifact in ``rules/file-bridge-protocol.md``.
    """
    for root, label in ((TEMPLATE_ROOT, "templates"), (GOLDEN_ROOT, "golden fixtures")):
        hits = _census(root, DOUBLED_TERM_RE)
        assert hits == {}, f"doubled replacement term in {label}: {hits}"


def test_settled_replacement_term_is_adopted() -> None:
    """`bridge state` is the settled term and is actually used in the bridge rules.

    CRITERION REFINEMENT (second one on this thread; see module docstring for the
    first). The proposal specified this as "``canonical bridge state`` absent".
    That literal form is not implementable, because it cannot distinguish a
    *coined competing term* from ordinary adjectival prose. Six pre-existing
    occurrences in the template tree are the latter, e.g.::

        > artifact is not canonical bridge-state or dispatcher authority.

    Removing "canonical" there inverts the sentence's meaning: the point is that
    the artifact is *not* the canonical authority. Those six predate this change
    and are correct English.

    Exactly one true competing-term occurrence was introduced by this change's
    mechanical substitution — ``Read canonical dispatcher/TAFE state`` became
    ``Read canonical bridge state`` in ``project/AGENTS.md`` — and it was
    corrected to ``Read bridge state``.

    This test therefore asserts the settled term is positively adopted, which is
    the ``DELIB-20260807011969`` B1 intent, rather than asserting absence of a
    string that legitimately appears.
    """
    rules = TEMPLATE_ROOT / "rules"
    settled = re.compile(r"\bbridge state\b", re.IGNORECASE)
    adopters = [p.name for p in _text_files(rules) if settled.search(_read(p))]
    assert adopters, "settled term 'bridge state' is not present anywhere in the rule templates"


# --------------------------------------------------------------------------
# Retention contract (the F1 narrowing: inverted, not dropped)
# --------------------------------------------------------------------------


def test_poller_templates_retained() -> None:
    """Both poller templates still exist. The narrowing retained them."""
    assert POLLER_CANONICAL.is_file(), f"missing retained template: {POLLER_CANONICAL}"
    assert POLLER_SETUP_PROMPT.is_file(), f"missing retained template: {POLLER_SETUP_PROMPT}"


def test_poller_templates_carry_no_tafe() -> None:
    """The retained stubs describe retired mechanisms without naming TAFE."""
    for path in (POLLER_CANONICAL, POLLER_SETUP_PROMPT):
        assert not TAFE_RE.search(_read(path)), f"TAFE reference retained in {path.name}"


def test_poller_history_is_permitted_and_present() -> None:
    """Poller history is retained, not purged.

    Guards the opposite failure from the one above: a later slice that strips the
    deprecation stub's subject matter would leave a stub that no longer explains
    what was retired.
    """
    text = _read(POLLER_CANONICAL)
    assert POLLER_RE.search(text), (
        "bridge-poller-canonical.md no longer references the mechanism it deprecates; "
        "historical references are retained deliberately"
    )


def test_retention_contract_text_preserved() -> None:
    """The retention sentence and its follow-on reference survive the purge."""
    text = _read(POLLER_CANONICAL)
    assert "two release cycles" in text, "retention sentence removed from bridge-poller-canonical.md"
    assert "Open Follow-On" in text, "Slice 4 Open Follow-On reference removed"


# --------------------------------------------------------------------------
# Census method (WI-6327)
# --------------------------------------------------------------------------


def test_census_is_case_insensitive() -> None:
    """The census matches regardless of case."""
    for probe in ("TAFE", "tafe", "TaFe"):
        assert TAFE_RE.search(f"prefix {probe} suffix"), f"census missed case variant {probe!r}"


def test_census_is_filesystem_based(tmp_path: Path) -> None:
    """The filesystem census sees an untracked file; a tracked-only census does not.

    Demonstrated rather than asserted, per the GO's expectation that an assertion
    never observed failing is not yet evidence. An untracked file is written into
    the template tree, both censuses run, and the tracked-only census is shown to
    miss what the filesystem census finds.
    """
    probe = TEMPLATE_ROOT / "_census_probe_untracked.md"
    assert not probe.exists(), "probe path unexpectedly present; refusing to overwrite"
    probe.write_text("# probe\n\nTAFE-backed bridge state\n", encoding="utf-8")
    try:
        fs_hits = _census(TEMPLATE_ROOT, TAFE_RE)
        tracked_hits = _git_tracked_census(TEMPLATE_ROOT, "TAFE")
        rel = probe.relative_to(PROJECT_ROOT).as_posix()

        assert rel in fs_hits, "filesystem census failed to see an untracked file"
        assert rel not in tracked_hits, (
            "tracked-only census unexpectedly saw an untracked file; "
            "the negative control is not demonstrating the WI-6327 defect"
        )
    finally:
        probe.unlink(missing_ok=True)

    assert not probe.exists(), "census probe was not cleaned up"
