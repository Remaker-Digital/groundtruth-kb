"""Read-only helpers for inspecting numbered bridge threads."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from groundtruth_kb.bridge.versioned_files import _CANONICAL_STATUS_TOKENS, _line_status_token
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


def _first_nonblank_line(path: Path) -> str | None:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for raw in handle:
                if raw.strip():
                    return raw.strip()
    except OSError:
        return None
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
    first_line = _first_nonblank_line(path)
    status, canonical = _status_from_first_line(first_line)
    return {
        "version": int(match.group("version")),
        "path": _relative_path(path, project_root),
        "status": status,
        "status_is_canonical": canonical,
        "first_line": first_line,
    }


def show_thread(project_root: Path, slug: str) -> dict[str, Any] | None:
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


def threads_for_work_item(project_root: Path, wi_id: str) -> dict[str, Any]:
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
            first_line = _first_nonblank_line(path)
            status, canonical = _status_from_first_line(first_line)
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
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
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
        threads.append(
            {
                "slug": slug,
                "latest_status": latest["status"],
                "latest_path": latest["path"],
                "citing_paths": citing_paths,
            }
        )
    threads.sort(key=lambda item: item["slug"])

    total_threads = len(grouped)
    threads_with_metadata = sum(1 for row in grouped.values() if row["work_items"])
    return {
        "work_item": normalized_wi,
        "match_count": len(threads),
        "threads": threads,
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
