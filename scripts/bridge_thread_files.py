"""Shared exact bridge-thread file helpers.

The bridge thread chain is only the canonical ``<slug>-NNN.md`` sequence.
Prefix siblings (``<slug>-child-001.md``), drafts, and other ad hoc markdown
files must not affect latest-status or post-dispatch verdict reconciliation.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

_PACKAGE_SRC = Path(__file__).resolve().parent.parent / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

from groundtruth_kb.bridge.versioned_files import status_from_bridge_text  # noqa: E402

VERSIONED_BRIDGE_FILE_RE = re.compile(
    r"^(?P<slug>[A-Za-z0-9_.-]+)-(?P<version>\d{3})\.md$"
)
# WI-6541: the module-local status-token regex was removed. It duplicated the
# canonical token list owned by
# ``groundtruth_kb.bridge.versioned_files._CANONICAL_STATUS_TOKENS`` and had
# already drifted from it (the local copy omitted ``BLOCKED``). Status parsing
# now has exactly one home: ``parse_bridge_header_block``.


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


def index_bridge_thread_files(
    project_root: Path,
) -> dict[str, list[VersionedBridgeFile]]:
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
        index.setdefault(slug, []).append(
            VersionedBridgeFile(path=path, slug=slug, version=version)
        )
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
    index = (
        file_index
        if file_index is not None
        else index_bridge_thread_files(project_root)
    )
    records: list[VersionedBridgeFile] = []
    for candidate_slug in slugs:
        records.extend(index.get(candidate_slug, ()))
    records.sort(key=lambda item: (item.version, item.path.name))
    return [record.path for record in records]


def status_from_bridge_file(path: Path) -> str | None:
    """Return the canonical bridge status token from ``path``."""

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    token = status_from_bridge_text(text)
    if token is not None:
        return token
    # WI-6541: this wrapper holds no parsing logic of its own. The former
    # fallback re-implemented the status-token regex here, which is the
    # duplicate-parser defect the work item removes. Leniency toward a
    # historically tolerated lowercase status token is preserved by retrying
    # the same packaged accessor against a case-normalized copy, rather than
    # by keeping a second parser. Uppercasing is safe for the envelope markers
    # because the accessor lowercases each line before its ``::init`` /
    # ``::open`` prefix test.
    return status_from_bridge_text(text.upper())


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
            candidates.append(
                BridgeVerdictFile(
                    path=path, status=str(status), version=version, mtime=mtime
                )
            )
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item.mtime, item.version, item.path.name))
    return candidates[0]


def index_bridge_thread_files_archive_aware(
    project_root: Path,
) -> dict[str, list[VersionedBridgeFile]]:
    """Index all exact versioned bridge files, suppressing slugs with a trusted
    committed terminal archive verdict that is strictly newer than the latest
    live bridge version.

    Historical exact-thread readers (``versioned_bridge_files`` and callers)
    remain unsuppressed.  Use this function when building current-queue
    surfaces (LO-actionable lists, dispatcher selection input, state reports).
    """
    index = index_bridge_thread_files(project_root)

    # Lazy import to avoid circular dependencies at module load.
    from groundtruth_kb.bridge.versioned_files import (  # noqa: PLC0415
        classify_committed_archive_verdicts,
    )

    try:
        archive_verdicts = classify_committed_archive_verdicts(project_root)
    except (OSError, RuntimeError, ValueError):
        return index  # fail closed — suppress nothing

    suppressed: set[str] = set()
    for slug, verdict in archive_verdicts.items():
        live = index.get(slug)
        if live is None:
            continue
        # Only suppress when the archive version is strictly newer than the
        # latest live version.
        latest_live = max(f.version for f in live)
        if verdict.version > latest_live:
            suppressed.add(slug)

    if not suppressed:
        return index

    return {slug: files for slug, files in index.items() if slug not in suppressed}
