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
import tomllib
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

# Per DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001: a completeness candidate (an
# on-disk slug absent from the INDEX) is classified by the canonical status token
# on the first non-blank line of its latest on-disk version file. Terminal-status
# threads are *legitimately archived* (the file-bridge protocol trims terminal
# entries from the INDEX while keeping the files on disk; GOV-FILE-BRIDGE-AUTHORITY-001)
# and are NOT lost blocks; non-terminal threads remain lost blocks.
_TERMINAL_STATUS_TOKENS = frozenset({"VERIFIED", "WITHDRAWN", "DEFERRED", "ADVISORY", "ACCEPTED"})
_NON_TERMINAL_STATUS_TOKENS = frozenset({"NEW", "REVISED", "GO", "NO-GO"})
_CANONICAL_STATUS_TOKENS = _TERMINAL_STATUS_TOKENS | _NON_TERMINAL_STATUS_TOKENS
# Strip leading markdown heading/emphasis/list/quote markers so a first line like
# "# VERIFIED: ..." or "**NO-GO**" still surfaces its status token.
_LEADING_MARKER_RE = re.compile(r"^[#>*\-\s`]+")
_STATUS_TOKEN_RE = re.compile(r"^([A-Z][A-Z-]*)")

# Per DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001 (v2) rule 3: a candidate slug
# listed in this owner-curated, append-only governed config is classified
# ``archived`` (legitimately absent), not ``lost``. The config is the auditable
# disposition record for reviewed historical/abandoned threads; removing an
# entry re-surfaces its slug as a ``lost_block`` (reversible). Read-only input.
_ACKNOWLEDGED_CONFIG_REL = "config/governance/tafe-acknowledged-archived-bridges.toml"

# Per DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001 (v2) rule 2: a non-terminal
# candidate whose ``<slug>-implementation`` sibling's latest on-disk version is
# terminal (by the rule-1 test) is classified ``archived``. GT-KB splits a
# proposal thread from its implementation thread; a terminal ``-implementation``
# sibling means the work completed, so the proposal thread's trimming from the
# INDEX is protocol-sanctioned archival.
_IMPLEMENTATION_SIBLING_SUFFIX = "-implementation"


def _line_status_token(line: str) -> str | None:
    """Return the canonical bridge status token a line starts with, else ``None``.

    Leading markdown heading/emphasis/list/quote markers are stripped first so a
    heading-style status line (``# VERIFIED: ...``) still resolves to its token.
    Only tokens in the canonical set are recognized; prose returns ``None``.
    """
    stripped = _LEADING_MARKER_RE.sub("", line.strip())
    match = _STATUS_TOKEN_RE.match(stripped)
    if match is not None and match.group(1) in _CANONICAL_STATUS_TOKENS:
        return match.group(1)
    return None


def _classify_candidate(latest_file_text: str) -> str:
    """Classify a candidate as ``"archived"`` or ``"lost"`` from its latest file.

    Per DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001: the first non-blank line's
    canonical status token decides. A terminal token (VERIFIED/WITHDRAWN/DEFERRED/
    ADVISORY/ACCEPTED) classifies the thread as legitimately archived; a
    non-terminal token (NEW/REVISED/GO/NO-GO) classifies it as a lost block. When
    the first non-blank line carries no canonical token (status-indeterminate,
    e.g. an old pre-status-token-rule file whose first line is prose), the full
    file is scanned for any line beginning with a terminal token: found ->
    archived; otherwise -> lost (conservative; fail-toward-surfacing).
    """
    lines = latest_file_text.splitlines()
    first_token: str | None = None
    for raw in lines:
        if raw.strip():
            first_token = _line_status_token(raw)
            break
    if first_token in _TERMINAL_STATUS_TOKENS:
        return "archived"
    if first_token in _NON_TERMINAL_STATUS_TOKENS:
        return "lost"
    # Status-indeterminate: scan the whole file for any terminal-token line.
    for raw in lines:
        if _line_status_token(raw) in _TERMINAL_STATUS_TOKENS:
            return "archived"
    return "lost"


def _read_latest_text(doc: ExpectedDocument, project_root: Path) -> str | None:
    """Read a document's latest on-disk version file, or ``None`` if unreadable.

    Read-only: uses ``Path.read_text`` (the same sanctioned read the rule-1 path
    uses); never calls ``open()`` or any write surface.
    """
    try:
        return (project_root / doc.files[-1]).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _load_acknowledged_slugs(project_root: Path) -> frozenset[str]:
    """Load the owner-acknowledged-archived slug set (rule 3); empty when absent.

    Reads ``config/governance/tafe-acknowledged-archived-bridges.toml`` via
    ``Path.read_text`` + ``tomllib.loads`` (a string parse — no ``open()``, so the
    module's read-only AST guard is preserved). Returns an empty frozenset when
    the config is absent or malformed (config-absent => graceful: no acknowledged
    entries, no crash, every such candidate stays ``lost``).
    """
    config_path = project_root / _ACKNOWLEDGED_CONFIG_REL
    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError:
        return frozenset()
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return frozenset()
    entries = data.get("acknowledged", [])
    if not isinstance(entries, list):
        return frozenset()
    slugs: set[str] = set()
    for entry in entries:
        if isinstance(entry, dict):
            slug = entry.get("slug")
            if isinstance(slug, str) and slug:
                slugs.add(slug)
    return frozenset(slugs)


def _candidate_is_archived(
    slug: str,
    expected_docs: dict[str, ExpectedDocument],
    acknowledged: frozenset[str],
    project_root: Path,
) -> bool:
    """Classify a completeness candidate as archived per DCL v2 rules 1->2->3.

    Returns ``True`` (archived; legitimately absent, not a lost block) when ANY
    rule holds, evaluated in precedence order:

    1. Terminal-token rule (v1): the candidate's own latest version is terminal.
    2. Implementation-sibling rule (v2): the candidate is non-terminal but a
       ``<slug>-implementation`` sibling exists on disk whose latest version is
       terminal (by the rule-1 test).
    3. Acknowledged-archived config rule (v2): the candidate slug appears in the
       governed acknowledged-archived config.

    A candidate matching none of the three stays a lost block (conservative;
    fail-toward-surfacing). An unreadable candidate file skips only rule 1; rules
    2 and 3 are still evaluated (rule 3 is config-driven and needs no file read).
    """
    # Rule 1 -- terminal token on the candidate's own latest version.
    latest_text = _read_latest_text(expected_docs[slug], project_root)
    if latest_text is not None and _classify_candidate(latest_text) == "archived":
        return True

    # Rule 2 -- terminal implementation sibling.
    sibling = expected_docs.get(f"{slug}{_IMPLEMENTATION_SIBLING_SUFFIX}")
    if sibling is not None:
        sibling_text = _read_latest_text(sibling, project_root)
        if sibling_text is not None and _classify_candidate(sibling_text) == "archived":
            return True

    # Rule 3 -- owner-acknowledged-archived config.
    return slug in acknowledged


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
    # Per DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001: candidates (expected − present)
    # whose latest on-disk version is terminal-status are legitimately archived, not
    # lost. ``archived_blocks`` is informational; it does NOT gate ``ok``.
    archived_blocks: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        """True when no lost blocks are present (the gating completeness condition).

        Gates on the refined ``lost_blocks`` (non-terminal-orphan-only) set;
        ``archived_blocks`` is informational and never fails the gate.
        """
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
            "archived_blocks": list(self.archived_blocks),
            "archived_count": len(self.archived_blocks),
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
    taken from :func:`scan_expected_documents`. ``extra_blocks`` = present −
    expected. Each candidate in ``expected − present`` is classified by
    :func:`_candidate_is_archived` per DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001
    v2 (rule 1 terminal-token -> rule 2 implementation-sibling -> rule 3
    acknowledged-archived config); candidates matching a rule land in
    ``archived_blocks`` (informational, ungated), the rest in ``lost_blocks`` (the
    gated completeness set). Read-only: the additional v2 inputs are the sibling
    thread's latest on-disk file and the acknowledged-archived config, both read
    via ``Path.read_text``; no write surface, no subprocess, no MemBase mutation.
    """
    parsed = parse_bridge_index(index_text)
    present = {block.name for block in parsed.blocks}
    expected_docs = scan_expected_documents(project_root)
    expected = set(expected_docs)
    acknowledged = _load_acknowledged_slugs(project_root)

    lost: list[str] = []
    archived: list[str] = []
    for slug in expected - present:
        if _candidate_is_archived(slug, expected_docs, acknowledged, project_root):
            archived.append(slug)
        else:
            lost.append(slug)

    return IndexCompletenessReport(
        present_slugs=tuple(sorted(present)),
        expected_slugs=tuple(sorted(expected)),
        lost_blocks=tuple(sorted(lost)),
        extra_blocks=tuple(sorted(present - expected)),
        archived_blocks=tuple(sorted(archived)),
    )
