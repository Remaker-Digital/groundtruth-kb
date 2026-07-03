"""Shared exact bridge-thread file helpers.

The bridge thread chain is only the canonical ``<slug>-NNN.md`` sequence.
Prefix siblings (``<slug>-child-001.md``), drafts, and other ad hoc markdown
files must not affect latest-status or post-dispatch verdict reconciliation.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

VERSIONED_BRIDGE_FILE_RE = re.compile(r"^(?P<slug>[A-Za-z0-9_.-]+)-(?P<version>\d{3})\.md$")
BRIDGE_STATUS_LINE_RE = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|NO-ACTION|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN|PAUSED|ACCEPTED|RETIRED|SUPERSEDED)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class VersionedBridgeFile:
    path: Path
    slug: str
    version: int


@dataclass(frozen=True)
class BridgeVerdictFile:
    path: Path
    status: str
    version: int
    mtime: float


StatusReader = Callable[[Path], str | None]


def parse_versioned_bridge_filename(name: str) -> tuple[str, int] | None:
    """Return ``(slug, version)`` for exact ``<slug>-NNN.md`` names only."""

    match = VERSIONED_BRIDGE_FILE_RE.match(name)
    if match is None:
        return None
    return match.group("slug"), int(match.group("version"))


def candidate_thread_slugs(slug: str) -> tuple[str, ...]:
    """Return accepted canonical slug spellings for a bridge thread reference."""

    cleaned = slug.strip()
    if not cleaned:
        return ()
    slugs = [cleaned]
    if not cleaned.startswith("gtkb-"):
        slugs.append(f"gtkb-{cleaned}")
    return tuple(dict.fromkeys(slugs))


def index_bridge_thread_files(project_root: Path) -> dict[str, list[VersionedBridgeFile]]:
    """Index all exact versioned bridge files by slug."""

    bridge_dir = Path(project_root) / "bridge"
    if not bridge_dir.is_dir():
        return {}
    index: dict[str, list[VersionedBridgeFile]] = {}
    for path in bridge_dir.glob("*.md"):
        parsed = parse_versioned_bridge_filename(path.name)
        if parsed is None:
            continue
        slug, version = parsed
        index.setdefault(slug, []).append(VersionedBridgeFile(path=path, slug=slug, version=version))
    for files in index.values():
        files.sort(key=lambda item: (item.version, item.path.name))
    return index


def versioned_bridge_files(
    project_root: Path,
    slug: str,
    *,
    file_index: dict[str, list[VersionedBridgeFile]] | None = None,
) -> list[Path]:
    """Return exact versioned files for ``slug``, sorted oldest to newest."""

    slugs = candidate_thread_slugs(slug)
    if not slugs:
        return []
    index = file_index if file_index is not None else index_bridge_thread_files(project_root)
    records: list[VersionedBridgeFile] = []
    for candidate_slug in slugs:
        records.extend(index.get(candidate_slug, ()))
    records.sort(key=lambda item: (item.version, item.path.name))
    return [record.path for record in records]


def status_from_bridge_file(path: Path) -> str | None:
    """Return the first canonical bridge status token from ``path``."""

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = BRIDGE_STATUS_LINE_RE.match(stripped)
        return match.group(1).upper() if match else None
    return None


def latest_bridge_status_for_thread(
    project_root: Path,
    slug: str,
    *,
    status_reader: StatusReader | None = None,
) -> str | None:
    """Return latest status for the exact canonical thread chain."""

    read_status = status_reader or status_from_bridge_file
    for path in reversed(versioned_bridge_files(project_root, slug)):
        status = read_status(path)
        if status is not None:
            return status
    return None


def find_bridge_verdict_after(
    *,
    project_root: Path,
    slug: str,
    dispatch_ts: float,
    verdict_statuses: frozenset[str],
    status_reader: StatusReader | None = None,
    after_version: int | None = None,
) -> BridgeVerdictFile | None:
    """Return the first exact canonical verdict file newer than ``dispatch_ts``."""

    read_status = status_reader or status_from_bridge_file
    candidates: list[BridgeVerdictFile] = []
    for path in versioned_bridge_files(project_root, slug):
        parsed = parse_versioned_bridge_filename(path.name)
        if parsed is None:
            continue
        version = parsed[1]
        if after_version is not None and version <= after_version:
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime < dispatch_ts:
            continue
        status = read_status(path)
        if status in verdict_statuses:
            candidates.append(BridgeVerdictFile(path=path, status=str(status), version=version, mtime=mtime))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item.mtime, item.version, item.path.name))
    return candidates[0]
