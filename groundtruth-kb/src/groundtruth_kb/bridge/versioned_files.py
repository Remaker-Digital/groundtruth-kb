"""Utilities for reading status-bearing numbered bridge files."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "ExpectedDocument",
    "candidate_is_archived",
    "load_acknowledged_archived_slugs",
    "scan_expected_documents",
    "status_from_bridge_file",
]

_BRIDGE_FILE_RE = re.compile(r"^(?P<slug>.+)-(?P<version>\d+)\.md$")
_TERMINAL_STATUS_TOKENS = frozenset({"VERIFIED", "WITHDRAWN", "DEFERRED", "ADVISORY", "ACCEPTED"})
_NON_TERMINAL_STATUS_TOKENS = frozenset({"NEW", "REVISED", "GO", "NO-GO"})
_CANONICAL_STATUS_TOKENS = _TERMINAL_STATUS_TOKENS | _NON_TERMINAL_STATUS_TOKENS
_LEADING_MARKER_RE = re.compile(r"^[#>*\-\s`]+")
_STATUS_TOKEN_RE = re.compile(r"^([A-Z][A-Z-]*)")
_ACKNOWLEDGED_CONFIG_REL = "config/governance/tafe-acknowledged-archived-bridges.toml"
_IMPLEMENTATION_SIBLING_SUFFIX = "-implementation"


@dataclass(frozen=True)
class ExpectedDocument:
    """One bridge-document slug observed on disk under ``bridge/``."""

    slug: str
    files: tuple[str, ...]
    latest_version: int


def _line_status_token(line: str) -> str | None:
    stripped = _LEADING_MARKER_RE.sub("", line.strip())
    match = _STATUS_TOKEN_RE.match(stripped)
    if match is not None and match.group(1) in _CANONICAL_STATUS_TOKENS:
        return match.group(1)
    return None


def status_from_bridge_file(path: Path) -> str | None:
    """Return the first canonical status token in a numbered bridge file."""

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for raw in lines:
        if raw.strip():
            return _line_status_token(raw)
    return None


def _classify_candidate(latest_file_text: str) -> str:
    lines = latest_file_text.splitlines()
    for raw in lines:
        if raw.strip():
            first_token = _line_status_token(raw)
            if first_token in _TERMINAL_STATUS_TOKENS:
                return "archived"
            return "lost"
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
