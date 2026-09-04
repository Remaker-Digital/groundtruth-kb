"""Utilities for reading status-bearing numbered bridge files."""

from __future__ import annotations

import hashlib
import re
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path

# replace the hand-maintained _CANONICAL_STATUS_TOKENS literal with:
from groundtruth_kb.bridge.vocabulary import CANONICAL_STATUSES

__all__ = [
    "BridgeHeaderBlock",
    "ExpectedDocument",
    "candidate_is_archived",
    "classify_committed_archive_verdicts",
    "load_acknowledged_archived_slugs",
    "parse_bridge_header_block",
    "scan_expected_documents",
    "status_from_bridge_file",
    "status_from_bridge_text",
]

_BRIDGE_FILE_RE = re.compile(r"^(?P<slug>.+)-(?P<version>\d+)\.md$")
_TERMINAL_STATUS_TOKENS = frozenset({"VERIFIED", "WITHDRAWN", "SUPERSEDED"})
_NON_TERMINAL_STATUS_TOKENS = frozenset(
    {"NEW", "REVISED", "GO", "NO-GO", "VERDICT-REJECTED", "ADVISORY", "READY", "NOT-READY"}
)
_EXTRA_STATUS_TOKENS = frozenset({"BLOCKED"})
_CANONICAL_STATUS_TOKENS = _TERMINAL_STATUS_TOKENS | _NON_TERMINAL_STATUS_TOKENS | _EXTRA_STATUS_TOKENS
# DCL-NO-ACTION-STATUS-SEMANTICS-001 v2: historical artifacts retain the
# obsolete spelling on disk, but every reader reconstructs the one canonical
# correction state.  New-output acceptance is deliberately owned by writers,
# not by this compatibility reader.
_STATUS_SYNONYMS: dict[str, str] = {"NO-ACTION": "VERDICT-REJECTED"}
_LEADING_MARKER_RE = re.compile(r"^[#>*\-\s`]+")
_STATUS_TOKEN_RE = re.compile(r"^([A-Z][A-Z-]*)")
_INIT_PREFIX = "::init"
_OPEN_PREFIX = "::open"
_HEADER_BLOCK_MAX_LINES = 5
_ACKNOWLEDGED_CONFIG_REL = "config/governance/tafe-acknowledged-archived-bridges.toml"
_IMPLEMENTATION_SIBLING_SUFFIX = "-implementation"
_ARCHIVE_DIR_REL = "archive/bridge-terminal-verdicts"
_DOCUMENT_FIELD_RE = re.compile(r"^Document:\s*(?P<slug>.+)$", re.MULTILINE)
_VERSION_FIELD_RE = re.compile(r"^Version:\s*(?P<version>\d+)$", re.MULTILINE)


@dataclass(frozen=True)
class ExpectedDocument:
    """One bridge-document slug observed on disk under ``bridge/``."""

    slug: str
    files: tuple[str, ...]
    latest_version: int


@dataclass(frozen=True)
class CommittedArchiveVerdict:
    """One trusted committed terminal archive verdict."""

    slug: str
    version: int
    path: str


@dataclass(frozen=True)
class BridgeHeaderBlock:
    """The first one-to-three non-blank lines of a bridge file, classified by pattern.

    Order is immaterial: ``::init``, ``::open``, and the status token are
    identified independently. A status-only block is well-formed.
    """

    status: str | None
    status_line: str | None
    init_line: str | None
    open_line: str | None
    raw_lines: tuple[str, ...]

    @property
    def status_line_exact(self) -> bool:
        return self.status is not None and self.status_line == self.status


def _line_status_token(line: str) -> str | None:
    stripped = _LEADING_MARKER_RE.sub("", line.strip())
    match = _STATUS_TOKEN_RE.match(stripped)
    if match is None:
        return None
    token = _STATUS_SYNONYMS.get(match.group(1), match.group(1))
    if token in _CANONICAL_STATUS_TOKENS:
        return token
    return None


def parse_bridge_header_block(text: str, *, max_lines: int = _HEADER_BLOCK_MAX_LINES) -> BridgeHeaderBlock:
    """Read the bridge header as a unit. Element order does not matter."""

    raw: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        raw.append(stripped)
        if len(raw) >= max_lines:
            break
    init_line = None
    open_line = None
    status = None
    status_line = None
    for line in raw:
        lowered = line.lower()
        if lowered.startswith(_INIT_PREFIX):
            if init_line is None:
                init_line = line
            continue
        if lowered.startswith(_OPEN_PREFIX):
            if open_line is None:
                open_line = line
            continue
        token = _line_status_token(line)
        if token is not None and status is None:
            status = token
            # A bare synonym token reports its canonical form so
            # ``status_line_exact`` stays true. A decorated line is kept
            # verbatim so the decorated-verdict malformation path is intact.
            status_line = token if _LEADING_MARKER_RE.sub("", line.strip()) in _STATUS_SYNONYMS else line
    return BridgeHeaderBlock(
        status=status,
        status_line=status_line,
        init_line=init_line,
        open_line=open_line,
        raw_lines=tuple(raw),
    )


def status_from_bridge_text(text: str) -> str | None:
    """Return the canonical status token from a bridge file body."""

    return parse_bridge_header_block(text).status


def test_parser_reads_every_canonical_status():
    for status in CANONICAL_STATUSES:
        assert _line_status_token(status) == status


def status_from_bridge_file(path: Path) -> str | None:
    """Return the canonical status token in a numbered bridge file."""

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return status_from_bridge_text(text)


def _classify_candidate(latest_file_text: str) -> str:
    parsed = parse_bridge_header_block(latest_file_text)
    if parsed.status in _TERMINAL_STATUS_TOKENS:
        return "archived"
    return "lost"


def _read_latest_text(doc: ExpectedDocument, project_root: Path) -> str | None:
    try:
        return (project_root / doc.files[-1]).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def load_acknowledged_archived_slugs(project_root: Path) -> frozenset[str]:
    """Load owner-acknowledged archived bridge slugs, returning empty on absence."""

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


def candidate_is_archived(
    slug: str,
    expected_docs: dict[str, ExpectedDocument],
    acknowledged: frozenset[str],
    project_root: Path,
) -> bool:
    """Return true when a non-current bridge-thread candidate is archived."""

    latest_text = _read_latest_text(expected_docs[slug], project_root)
    if latest_text is not None and _classify_candidate(latest_text) == "archived":
        return True

    sibling = expected_docs.get(f"{slug}{_IMPLEMENTATION_SIBLING_SUFFIX}")
    if sibling is not None:
        sibling_text = _read_latest_text(sibling, project_root)
        if sibling_text is not None and _classify_candidate(sibling_text) == "archived":
            return True

    return slug in acknowledged


def _git_blob_hash(project_root: Path, file_path: str) -> str | None:
    """Return the Git blob object hash for a tracked file, or None on failure.

    Uses ``git ls-tree HEAD -- <path>`` with hidden-window subprocess flags
    and a short timeout.  Returns ``None`` on any error or if the file is not
    tracked as a regular blob in HEAD.
    """
    try:
        result = subprocess.run(
            [
                "git",
                "--no-optional-locks",
                "ls-tree",
                "-z",
                "HEAD",
                "--",
                file_path,
            ],
            capture_output=True,
            cwd=str(project_root),
            timeout=10,
            creationflags=0x08000000 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None

    output = result.stdout.decode("utf-8", errors="replace").rstrip("\0")
    if not output:
        return None

    # Expected format: "<mode> blob <hash>\t<path>"
    parts = output.split("\t", 1)
    if len(parts) < 2:
        return None

    header = parts[0].split()
    if len(header) < 3 or header[1] != "blob":
        return None

    return header[2]


def _local_file_sha256(path: Path) -> str | None:
    """Return the SHA-256 of the file's bytes, or None on error."""
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    return hashlib.sha256(raw).hexdigest()


def _git_cat_file_blob(project_root: Path, blob_hash: str) -> bytes | None:
    """Return the raw blob content from Git, or None on failure."""
    try:
        result = subprocess.run(
            [
                "git",
                "--no-optional-locks",
                "cat-file",
                "blob",
                blob_hash,
            ],
            capture_output=True,
            cwd=str(project_root),
            timeout=10,
            creationflags=0x08000000 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None
    return result.stdout


def classify_committed_archive_verdicts(
    project_root: Path,
    *,
    archive_dir: str = _ARCHIVE_DIR_REL,
) -> dict[str, CommittedArchiveVerdict]:
    """Scan committed terminal archive verdicts and return trusted dispositions.

    Trusts an archive disposition only when ALL of these hold:

    - The archive path is under the canonical ``archive/bridge-terminal-verdicts/``.
    - The file is tracked as a regular blob in current ``HEAD``.
    - Local raw bytes exactly match the ``HEAD`` blob (SHA-256 comparison).
    - The first status token is in the terminal set.
    - ``Document:`` matches the filename slug.
    - ``Version:`` matches the filename version.
    - The trusted archive version is *strictly newer* than any live bridge version
      for the same slug.

    Returns a ``dict`` mapping slug to ``CommittedArchiveVerdict``.
    Callers consume this for archive-aware queue suppression.
    """
    resolved = (project_root / archive_dir).resolve()
    if not resolved.is_dir():
        return {}

    trusted: dict[str, CommittedArchiveVerdict] = {}
    for path in resolved.glob("*.md"):
        if not path.is_file():
            continue

        match = _BRIDGE_FILE_RE.match(path.name)
        if match is None:
            continue
        slug = match.group("slug")
        version = int(match.group("version"))

        # --- canonical path check ---
        try:
            rel = path.relative_to(project_root).as_posix()
        except ValueError:
            continue
        if not rel.startswith(_ARCHIVE_DIR_REL + "/"):
            continue

        # --- Git HEAD tracking ---
        blob_hash = _git_blob_hash(project_root, rel)
        if blob_hash is None:
            continue

        # --- raw-byte equality ---
        local_hash = _local_file_sha256(path)
        if local_hash is None:
            continue
        tracked_bytes = _git_cat_file_blob(project_root, blob_hash)
        if tracked_bytes is None:
            continue
        tracked_hash = hashlib.sha256(tracked_bytes).hexdigest()
        if local_hash != tracked_hash:
            continue

        # --- terminal first status ---
        status = status_from_bridge_file(path)
        if status is None or status not in _TERMINAL_STATUS_TOKENS:
            continue

        # --- metadata coherence ---
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        doc_match = _DOCUMENT_FIELD_RE.search(text)
        ver_match = _VERSION_FIELD_RE.search(text)
        if doc_match is None or ver_match is None:
            continue
        if doc_match.group("slug") != slug:
            continue
        try:
            declared_version = int(ver_match.group("version"))
        except ValueError:
            continue
        if declared_version != version:
            continue

        # --- cross-slug safety ---
        # Only trust if this exact slug/version matches the filename exactly.
        # No cross-slug or old-version archives are accepted.

        trusted[slug] = CommittedArchiveVerdict(
            slug=slug,
            version=version,
            path=rel,
        )

    return trusted


def scan_expected_documents(project_root: Path, bridge_dir: Path | None = None) -> dict[str, ExpectedDocument]:
    """Scan status-bearing numbered bridge files grouped by slug."""

    resolved_bridge_dir = bridge_dir or project_root / "bridge"
    if not resolved_bridge_dir.is_dir():
        return {}

    versions_by_slug: dict[str, list[int]] = {}
    files_by_slug: dict[str, list[tuple[int, str]]] = {}
    for path in resolved_bridge_dir.glob("*.md"):
        if not path.is_file():
            continue
        match = _BRIDGE_FILE_RE.match(path.name)
        if match is None:
            continue
        slug = match.group("slug")
        version = int(match.group("version"))
        versions_by_slug.setdefault(slug, []).append(version)
        try:
            rel_path = path.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = path.as_posix()
        files_by_slug.setdefault(slug, []).append((version, rel_path))

    expected: dict[str, ExpectedDocument] = {}
    for slug, versions in versions_by_slug.items():
        ordered_files = tuple(rel for _, rel in sorted(files_by_slug[slug]))
        expected[slug] = ExpectedDocument(
            slug=slug,
            files=ordered_files,
            latest_version=max(versions),
        )
    return expected
