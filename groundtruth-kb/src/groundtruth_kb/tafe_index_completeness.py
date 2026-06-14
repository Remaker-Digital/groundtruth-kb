"""External expected-document oracle + lost-block detection (WI-4508, Slice B).

Slice A (``tafe_index_sync.py``) delivered the lossless ``bridge/INDEX.md``
parser plus the *text-observable* integrity diagnostics, and explicitly deferred
the one class it cannot see from text alone: a document block that is *already
absent* from ``index_text``. As the Slice A docstring states, "Lost-block
(absent-from-text) detection requires an external expected-document oracle and
is explicitly deferred to Slice B."

This module is that oracle. The ``bridge/`` directory is the filesystem source
of truth for *which* bridge documents exist; this module scans it, builds the
expected-slug inventory, and diffs it against the parsed canonical INDEX:

* **lost blocks** = slugs with ``bridge/<slug>-NNN.md`` files on disk but no
  ``Document:`` entry in the canonical INDEX (the absent-from-text class Slice A
  deferred), and
* **extra blocks** = ``Document:`` entries in the INDEX with no matching
  ``bridge/<slug>-*.md`` files (a phantom-reference advisory).

Read-only contract: the canonical ``bridge/INDEX.md`` remains the sole
authoritative workflow state per ``GOV-FILE-BRIDGE-AUTHORITY-001``. This module
reads the INDEX text and scans the ``bridge/`` directory; it performs no
canonical-INDEX write, no TAFE table write, no MemBase mutation, and no
subprocess. It reuses the VERIFIED Slice A parser
(:func:`tafe_index_sync.parse_bridge_index`) for the present-slug set rather
than re-implementing INDEX parsing.

Caveat — parked drafts (per ``.claude/rules/file-bridge-protocol.md`` §
Parked-Draft Pattern): a bridge file MAY be committed without an INDEX entry as
a deliberate work-in-progress. Such slugs appear in ``lost_blocks``. This is a
benign subclass; the report surfaces the candidate set for *review* and never
mutates canonical state. Distinguishing parked drafts from genuine lost blocks
requires the originating commit-message ``parked`` tag, which is deferred to a
later cutover refinement.

Specification links: ``SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`` (the
lossless+complete "parallel view" integrity prerequisite; Slice A = lossless,
Slice B = complete/no-lost-blocks), ``GOV-FILE-BRIDGE-AUTHORITY-001`` (canonical
INDEX preserved; no write surface).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.tafe_index_sync import parse_bridge_index

__all__ = [
    "ExpectedDocument",
    "IndexCompletenessReport",
    "index_completeness_report",
    "scan_expected_documents",
]

# A versioned bridge file: ``<slug>-NNN.md``. The slug is greedy so the trailing
# ``-(\d+)\.md`` anchor captures only the final numeric group as the version
# (bridge slugs themselves contain digits and hyphens). ``INDEX.md`` and any
# non-``-NNN``-versioned file fall out because they have no trailing ``-NNN``.
_BRIDGE_FILE_RE = re.compile(r"^(?P<slug>.+)-(?P<version>\d+)\.md$")


@dataclass(frozen=True)
class ExpectedDocument:
    """One bridge-document slug as observed on disk under ``bridge/``.

    ``files`` are the relative posix paths (``bridge/<slug>-NNN.md``) of every
    versioned file for the slug, sorted ascending by version. ``latest_version``
    is the maximum observed version number.
    """

    slug: str
    files: tuple[str, ...]
    latest_version: int


@dataclass(frozen=True)
class IndexCompletenessReport:
    """Completeness diff between the canonical INDEX and the ``bridge/`` directory.

    ``present_slugs`` are the ``Document:`` names parsed from the canonical INDEX
    (the present set). ``expected_slugs`` are the slugs observed on disk (the
    expected set). ``lost_blocks`` is ``expected − present`` (the absent-from-text
    class Slice A deferred); ``extra_blocks`` is ``present − expected`` (phantom
    INDEX entries). All four tuples are sorted for determinism.
    """

    present_slugs: tuple[str, ...]
    expected_slugs: tuple[str, ...]
    lost_blocks: tuple[str, ...]
    extra_blocks: tuple[str, ...]

    @property
    def ok(self) -> bool:
        """True when no lost blocks are present (the gating completeness condition)."""
        return not self.lost_blocks

    def as_dict(self) -> dict[str, Any]:
        """A JSON-serializable view of the report."""
        return {
            "ok": self.ok,
            "present_count": len(self.present_slugs),
            "expected_count": len(self.expected_slugs),
            "present_slugs": list(self.present_slugs),
            "expected_slugs": list(self.expected_slugs),
            "lost_blocks": list(self.lost_blocks),
            "extra_blocks": list(self.extra_blocks),
        }


def scan_expected_documents(project_root: Path) -> dict[str, ExpectedDocument]:
    """Scan ``<project_root>/bridge/`` for versioned bridge files, grouped by slug.

    Globs ``bridge/*.md``, keeps only files matching ``<slug>-NNN.md`` (which
    excludes ``INDEX.md`` and any non-versioned markdown), and groups them by
    slug. The ``bridge/`` directory IS the external expected-document oracle.
    Returns an empty mapping when the ``bridge/`` directory does not exist.
    """
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return {}

    versions_by_slug: dict[str, list[int]] = {}
    files_by_slug: dict[str, list[tuple[int, str]]] = {}
    for path in bridge_dir.glob("*.md"):
        if not path.is_file():
            continue
        match = _BRIDGE_FILE_RE.match(path.name)
        if match is None:
            continue
        slug = match.group("slug")
        version = int(match.group("version"))
        versions_by_slug.setdefault(slug, []).append(version)
        files_by_slug.setdefault(slug, []).append((version, f"bridge/{path.name}"))

    expected: dict[str, ExpectedDocument] = {}
    for slug, versions in versions_by_slug.items():
        ordered_files = tuple(rel for _, rel in sorted(files_by_slug[slug]))
        expected[slug] = ExpectedDocument(
            slug=slug,
            files=ordered_files,
            latest_version=max(versions),
        )
    return expected


def index_completeness_report(index_text: str, project_root: Path) -> IndexCompletenessReport:
    """Diff the parsed canonical INDEX against the ``bridge/`` directory oracle.

    The present set is taken from :func:`tafe_index_sync.parse_bridge_index`
    (the VERIFIED Slice A parser; no re-implementation). The expected set is
    taken from :func:`scan_expected_documents`. ``lost_blocks`` = expected −
    present; ``extra_blocks`` = present − expected. Pure over its two inputs
    (the INDEX text and the on-disk scan result for ``project_root``).
    """
    parsed = parse_bridge_index(index_text)
    present = {block.name for block in parsed.blocks}
    expected = set(scan_expected_documents(project_root))

    return IndexCompletenessReport(
        present_slugs=tuple(sorted(present)),
        expected_slugs=tuple(sorted(expected)),
        lost_blocks=tuple(sorted(expected - present)),
        extra_blocks=tuple(sorted(present - expected)),
    )
