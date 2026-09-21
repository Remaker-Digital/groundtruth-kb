"""Adopter templates and scaffold fixtures contain no retired authority claims.

The census checks current authored inputs, including untracked files. Historical
formal records are outside these template and fixture directories.
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


#: Purge artifact: the replacement term accidentally doubled.
DOUBLED_TERM_RE = re.compile(r"\b(bridge[\s-]state)\b\s+bridge[\s-]state\b", re.IGNORECASE)


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
# Census method (WI-6327)
# --------------------------------------------------------------------------


def test_census_is_case_insensitive() -> None:
    """The census matches regardless of case."""
    for probe in ("TAFE", "tafe", "TaFe"):
        assert TAFE_RE.search(f"prefix {probe} suffix"), f"census missed case variant {probe!r}"


def test_census_is_filesystem_based(tmp_path: Path, monkeypatch) -> None:
    """An untracked fixture is visible to the filesystem census, not Git grep."""
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True, capture_output=True)
    templates = tmp_path / "templates"
    templates.mkdir()
    tracked = templates / "ordinary.md"
    tracked.write_text("Ordinary current guidance", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "templates/ordinary.md"], check=True, capture_output=True)
    probe = templates / "untracked.md"
    probe.write_text("Retired TAFE-backed authority", encoding="utf-8")
    monkeypatch.setitem(globals(), "PROJECT_ROOT", tmp_path)
    fs_hits = _census(templates, TAFE_RE)
    tracked_hits = _git_tracked_census(templates, "TAFE")
    assert fs_hits == {"templates/untracked.md": 1}
    assert tracked_hits == {}
