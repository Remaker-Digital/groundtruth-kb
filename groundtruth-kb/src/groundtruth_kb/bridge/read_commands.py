"""Read-only helpers for inspecting numbered bridge threads."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from groundtruth_kb.bridge.versioned_files import (
    _CANONICAL_STATUS_TOKENS,
    _line_status_token,
    parse_bridge_header_block,
)
from groundtruth_kb.project.lifecycle import _WORK_ITEM_LINE_RE

WORK_ITEM_LINE_RE = _WORK_ITEM_LINE_RE

_BRIDGE_FILE_RE = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3,})\.md$")
_WI_ID_RE = re.compile(r"^(WI-AUTO-[A-Z0-9-]+|WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)$")
_RAW_TOKEN_RE = re.compile(r"^([^\s:]+)")
_LEADING_MARKER_RE = re.compile(r"^[#>*\-\s`]+")


def _bridge_dir(project_root: Path) -> Path:
    return project_root / "bridge"


def _relative_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def _version_match(path: Path) -> re.Match[str] | None:
    return _BRIDGE_FILE_RE.match(path.name)


def _first_non_marker_line(raw_lines: tuple[str, ...]) -> str | None:
    """Return the first header line that is not an ``::init`` / ``::open`` marker.

    WI-6541: the header block is order-immaterial, so the non-canonical status
    fallback below must select the line it inspects by pattern rather than by
    position. Reading ``raw_lines[0]`` unconditionally meant a marker-first
    header reported no status at all, because ``_RAW_TOKEN_RE`` cannot match a
    leading ``::``.
    """

    for line in raw_lines:
        if line.lower().startswith(("::init", "::open")):
            continue
        return line
    return None


def _status_from_first_line(first_line: str | None) -> tuple[str | None, bool]:
    if first_line is None:
        return None, False
    canonical = _line_status_token(first_line)
    if canonical is not None:
        return canonical, True
    stripped = _LEADING_MARKER_RE.sub("", first_line.strip())
    match = _RAW_TOKEN_RE.match(stripped)
    if match is None:
        return None, False
    return match.group(1), False


def _version_entry(path: Path, project_root: Path) -> dict[str, Any] | None:
    match = _version_match(path)
    if match is None:
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    parsed = parse_bridge_header_block(text)
    first_line = parsed.raw_lines[0] if parsed.raw_lines else None
    if parsed.status is not None:
        status, canonical = parsed.status, True
    else:
        status, canonical = _status_from_first_line(_first_non_marker_line(parsed.raw_lines))
    return {
        "version": int(match.group("version")),
        "path": _relative_path(path, project_root),
        "status": status,
        "status_is_canonical": canonical,
        "first_line": first_line,
    }


def show_thread(project_root: Path, slug: str, *, compact: bool = False) -> dict[str, Any] | None:
    """Return one bridge thread's version chain, latest first."""

    bridge_dir = _bridge_dir(project_root)
    if not bridge_dir.is_dir():
        return None

    versions: list[dict[str, Any]] = []
    for path in bridge_dir.glob(f"{slug}-*.md"):
        match = _version_match(path)
        if match is None or match.group("slug") != slug:
            continue
        entry = _version_entry(path, project_root)
        if entry is not None:
            versions.append(entry)
    if not versions:
        return None

    versions.sort(key=lambda row: int(row["version"]), reverse=True)
    latest = versions[0]
    if compact:
        return {
            "slug": slug,
            "latest_status": latest["status"],
            "latest_path": latest["path"],
            "version_count": len(versions),
            "compact": True,
        }
    return {
        "slug": slug,
        "latest_status": latest["status"],
        "latest_path": latest["path"],
        "version_count": len(versions),
        "version_chain": versions,
    }


def _validate_work_item_id(wi_id: str) -> str:
    normalized = wi_id.strip()
    if not _WI_ID_RE.fullmatch(normalized):
        raise ValueError(f"Malformed work item id: {wi_id!r}")
    return normalized


def threads_for_work_item(project_root: Path, wi_id: str, *, compact: bool = False) -> dict[str, Any]:
    """Return bridge threads that cite ``wi_id`` in any version."""

    normalized_wi = _validate_work_item_id(wi_id)
    bridge_dir = _bridge_dir(project_root)
    grouped: dict[str, dict[str, Any]] = {}

    if bridge_dir.is_dir():
        for path in bridge_dir.glob("*.md"):
            match = _version_match(path)
            if match is None:
                continue
            slug = match.group("slug")
            version = int(match.group("version"))
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            parsed = parse_bridge_header_block(text)
            first_line = parsed.raw_lines[0] if parsed.raw_lines else None
            if parsed.status is not None:
                status, canonical = parsed.status, True
            else:
                status, canonical = _status_from_first_line(_first_non_marker_line(parsed.raw_lines))
            rel_path = _relative_path(path, project_root)
            row = grouped.setdefault(
                slug,
                {
                    "versions": [],
                    "work_items": set(),
                    "citing_paths": [],
                },
            )
            row["versions"].append(
                {
                    "version": version,
                    "path": rel_path,
                    "status": status,
                    "status_is_canonical": canonical,
                    "first_line": first_line,
                }
            )
            matches = {match.group(1) for match in WORK_ITEM_LINE_RE.finditer(text)}
            if matches:
                row["work_items"].update(matches)
            if normalized_wi in matches:
                row["citing_paths"].append(rel_path)

    threads: list[dict[str, Any]] = []
    for slug, row in grouped.items():
        versions = sorted(row["versions"], key=lambda item: int(item["version"]), reverse=True)
        citing_paths = sorted(row["citing_paths"])
        if not citing_paths:
            continue
        latest = versions[0]
        thread_row = {
            "slug": slug,
            "latest_status": latest["status"],
            "latest_path": latest["path"],
        }
        if not compact:
            thread_row["citing_paths"] = citing_paths
        threads.append(thread_row)
    threads.sort(key=lambda item: item["slug"])

    total_threads = len(grouped)
    threads_with_metadata = sum(1 for row in grouped.values() if row["work_items"])
    payload: dict[str, Any] = {
        "work_item": normalized_wi,
        "match_count": len(threads),
        "threads": threads,
    }
    if compact:
        payload["compact"] = True
        payload["coverage_caveat"] = {
            "total_threads": total_threads,
            "threads_with_work_item_metadata": threads_with_metadata,
            "note": (
                "Compact mode omits per-version citing paths and full version chains; "
                "rerun without --compact for archival detail."
            ),
        }
        return payload
    return {
        **payload,
        "coverage_caveat": {
            "total_threads": total_threads,
            "threads_with_work_item_metadata": threads_with_metadata,
            "recognized_status_tokens": sorted(_CANONICAL_STATUS_TOKENS),
            "note": (
                "Only threads with Work Item metadata can be found by work item id; "
                "use topic-keyword search plus gt bridge show for exhaustive duplicate checks."
            ),
        },
    }
