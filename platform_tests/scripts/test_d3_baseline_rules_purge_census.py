"""D3 baseline-rules purge — Category B and C1 acceptance census.

Encodes the acceptance criterion stated by ``WI-6035``: a census showing zero
legacy-phrasing matches in the touched surfaces and no competing replacement
term introduced.

Authority:

- ``ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`` — obsolete-reference purge is
  a standing completion obligation.
- ``DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`` — retirement-class changes carry
  a linked, classified purge.
- ``DELIB-20260807011969`` B1 — the canonical bridge state store is named
  ``bridge state``; B2 — dated cutover references are rewritten present-tense
  with the event dropped.
- ``GOV-SOURCE-OF-TRUTH-FRESHNESS-001`` — state claims derive from fresh
  canonical reads.

Bridge thread: ``gtkb-d3-baseline-rules-b-c1-purge`` (GO at ``-004``).

The census-integrity tests exist because the ``-001`` proposal undercounted the
purge surface. Two independent defects produced that undercount, and both are
asserted here:

1. ``git grep`` searches TRACKED files only, so untracked files are invisible.
2. ``git grep -E`` is case-SENSITIVE by default, so capitalised headings such as
   ``# Dispatcher Daemon Incident Runbook`` are missed.

A census helper that fixes only one of the two still undercounts. The fixtures
below exercise both.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = PROJECT_ROOT / ".harness-baseline-configuration" / "rules"

# Category B: legacy names for the canonical bridge state store.
B_CLASS_RE = re.compile(
    r"TAFE-backed|dispatcher/TAFE|TAFE/dispatcher|TAFE bridge state|TAFE state",
    re.IGNORECASE,
)

# Category C1: dated cutover references.
C1_CLASS_RE = re.compile(r"cutover", re.IGNORECASE)

# The rejected alternative term, recorded in DELIB-20260807011969 so that a
# later slice does not reintroduce it.
COMPETING_TERM_RE = re.compile(r"canonical bridge state", re.IGNORECASE)

# A-vi false positives: rules ABOUT the token "TAFE" as topic-selection
# language. These do not assert the dispatcher is live and are deliberately
# preserved; see DELIB-20260813010010.
A_VI_ALLOWED = {"canonical-terminology.md"}


def _rule_files(root: Path = RULES_DIR) -> list[Path]:
    """Enumerate rule files from the filesystem.

    Deliberately a filesystem walk rather than ``git grep``: the census must see
    untracked files and uncommitted working-tree content.

    ``root`` exists so the census-integrity fixtures can point this *production*
    enumeration at a temporary tree instead of reimplementing it. The default
    preserves the whole-tree behaviour every other assertion in this module
    relies on.
    """
    assert root.is_dir(), f"rules dir missing: {root}"
    return sorted(root.glob("*.md"))


def _matches(pattern: re.Pattern[str], root: Path = RULES_DIR) -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    for path in _rule_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                hits.append((path.name, lineno, line.strip()))
    return hits


def test_no_b_class_state_store_wording() -> None:
    """No legacy name for the bridge state store survives outside A-vi."""
    offending = [h for h in _matches(B_CLASS_RE) if h[0] not in A_VI_ALLOWED]
    assert not offending, "Category-B legacy phrasing remains:\n" + "\n".join(
        f"  {name}:{lineno}  {line}" for name, lineno, line in offending
    )


def test_no_dated_cutover_references() -> None:
    """No dated cutover construction survives (DELIB-20260807011969 B2)."""
    offending = _matches(C1_CLASS_RE)
    assert not offending, "Category-C1 dated-cutover phrasing remains:\n" + "\n".join(
        f"  {name}:{lineno}  {line}" for name, lineno, line in offending
    )


def test_no_competing_replacement_term() -> None:
    """`bridge state` is the settled term; `canonical bridge state` was rejected."""
    offending = _matches(COMPETING_TERM_RE)
    assert not offending, "Rejected competing term reintroduced:\n" + "\n".join(
        f"  {name}:{lineno}  {line}" for name, lineno, line in offending
    )


def test_replacement_term_is_present() -> None:
    """Guard against a purge that deleted the referent instead of renaming it."""
    hits = _matches(re.compile(r"bridge state", re.IGNORECASE))
    assert hits, "No `bridge state` occurrences found; the store lost its name."


def test_a_vi_false_positives_preserved() -> None:
    """The topic-language rules about the token `TAFE` are deliberately kept."""
    text = (RULES_DIR / "canonical-terminology.md").read_text(encoding="utf-8")
    assert "bridge-, TAFE-," in text, (
        "A-vi topic-language rule at canonical-terminology.md was removed; it "
        "states a rule ABOUT the token, not a claim that the dispatcher is live."
    )


class TestCensusIntegrity:
    """The census method must see the whole working tree, case-insensitively.

    Both assertions target a *method* defect rather than a *result*, because the
    ``-001`` undercount was caused by the method. See the module docstring.
    """

    def test_census_counts_untracked_files(self, tmp_path: Path) -> None:
        """Defect class 1: `git grep` is tracked-only.

        Drives the production ``_matches``/``_rule_files`` path against a
        temporary tree. Reimplementing the walk here with ``pathlib`` would
        assert only that ``pathlib`` works and would stay green if the census
        helper regressed to a tracked-only scan.
        """
        d = tmp_path / "rules"
        d.mkdir()
        (d / "untracked.md").write_text("uses TAFE-backed bridge state\n", encoding="utf-8")

        hits = _matches(B_CLASS_RE, root=d)
        assert [(name, lineno) for name, lineno, _ in hits] == [("untracked.md", 1)], (
            "Census failed to see an untracked file. A tracked-only scan such as "
            f"`git grep` reproduces the -001 undercount. Got: {hits!r}"
        )

    def test_census_is_case_insensitive(self, tmp_path: Path) -> None:
        """Defect class 2: `git grep -E` is case-sensitive by default.

        Asserts against the module's own compiled patterns rather than a local
        probe. Every fixture line is cased differently from its pattern
        literal, so recompiling any of the three patterns without
        ``re.IGNORECASE`` turns this test red.
        """
        d = tmp_path / "rules"
        d.mkdir()
        (d / "heading.md").write_text(
            # line 1 -> B_CLASS_RE   (literal `dispatcher/TAFE`, `TAFE bridge state`)
            "# Dispatcher/TAFE Bridge State Notes\n"
            # line 2 -> C1_CLASS_RE  (literal `cutover`)
            "# Cutover Completed\n"
            # line 3 -> COMPETING_TERM_RE (literal `canonical bridge state`)
            "# Canonical Bridge State\n",
            encoding="utf-8",
        )

        for label, pattern, expected_line in (
            ("B_CLASS_RE", B_CLASS_RE, 1),
            ("C1_CLASS_RE", C1_CLASS_RE, 2),
            ("COMPETING_TERM_RE", COMPETING_TERM_RE, 3),
        ):
            hits = _matches(pattern, root=d)
            assert [lineno for _, lineno, _ in hits] == [expected_line], (
                f"{label} missed a capitalised heading, so a case-sensitive census "
                f"reproduces the -001 undercount. Got: {hits!r}"
            )

    def test_rules_dir_enumeration_is_filesystem_based(self) -> None:
        """The helper must enumerate from disk, not from a VCS index."""
        files = _rule_files()
        assert files, "No rule files enumerated."
        on_disk = {p.name for p in RULES_DIR.iterdir() if p.suffix == ".md"}
        assert {p.name for p in files} == on_disk, (
            "Enumeration diverges from the filesystem; the census would miss "
            "files that exist on disk but not in the index."
        )


@pytest.mark.parametrize(
    "expected_file",
    [
        "bridge-essential.md",
        "file-bridge-protocol.md",
        "session-bootstrap.md",
        "canonical-terminology.md",
        "way-of-working.md",
        "decision-ledger.md",
    ],
)
def test_in_scope_files_still_present(expected_file: str) -> None:
    """The purge renames; it must not delete rule files (that is A-class)."""
    assert (RULES_DIR / expected_file).is_file(), (
        f"{expected_file} is missing. The B+C1 slice renames wording only; "
        "file deletion is A-class work and is not authorised here."
    )
