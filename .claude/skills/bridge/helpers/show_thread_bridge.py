#!/usr/bin/env python3
"""Bridge thread loader: read full version chain for a given slug.

Resolves all ``bridge/<slug>-NNN.md`` files for a given thread slug, sorts by
version, and returns per-version metadata plus a bounded content preview.

The bridge protocol requires reading the full version chain before acting on
any single version. This helper provides the deterministic loader so agents
don't have to issue N separate Read calls and reconstruct ordering manually.

CLI usage:

  python .claude/skills/bridge/helpers/show_thread_bridge.py <slug> [--format json|markdown]
                                                                    [--preview-lines N]

Public API:

  from show_thread_bridge import show
  result = show("gtkb-bridge-convenience-verbs")
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_BRIDGE_DIR = PROJECT_ROOT / "bridge"
DEFAULT_INDEX_PATH = DEFAULT_BRIDGE_DIR / "INDEX.md"
DEFAULT_PREVIEW_LINES = 200

_VERSION_FILE_RE = re.compile(r"-(\d{3})\.md$")
_STATUS_LINE_RE = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY):\s*(bridge/.+\.md)\s*$"
)
_DOCUMENT_LINE_RE = re.compile(r"^Document:\s*(\S+)\s*$")


@dataclass(frozen=True)
class ThreadVersion:
    version: int
    path: str
    verdict_line: str
    content_preview: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _list_version_files(slug: str, bridge_dir: Path) -> list[tuple[int, Path]]:
    """Return sorted list of (version_int, abs_path) for ``bridge/<slug>-NNN.md`` files."""
    pattern = f"{slug}-*.md"
    results: list[tuple[int, Path]] = []
    for path in bridge_dir.glob(pattern):
        m = _VERSION_FILE_RE.search(path.name)
        if not m:
            continue
        if not path.name.startswith(f"{slug}-"):
            continue
        results.append((int(m.group(1)), path))
    results.sort(key=lambda pair: pair[0])
    return results


def _index_entry_for_slug(slug: str, index_path: Path) -> tuple[str, list[tuple[str, str]]]:
    """Return (entry_block_text, [(status, path), ...]) for the slug's Document block.

    Returns ("", []) if the slug is not present.
    """
    if not index_path.is_file():
        return "", []
    text = index_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    block_lines: list[str] = []
    status_entries: list[tuple[str, str]] = []
    in_block = False

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line and in_block:
            break
        m_doc = _DOCUMENT_LINE_RE.match(line)
        if m_doc:
            if m_doc.group(1) == slug:
                in_block = True
                block_lines.append(line)
                continue
            if in_block:
                break
            continue
        if in_block:
            block_lines.append(line)
            m_status = _STATUS_LINE_RE.match(line)
            if m_status:
                status_entries.append((m_status.group(1), m_status.group(2)))

    return "\n".join(block_lines), status_entries


def _content_preview(path: Path, max_lines: int) -> tuple[str, str]:
    """Return (first_line, preview_text) for the given file."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    first_line = lines[0] if lines else ""
    preview_lines = lines[:max_lines]
    return first_line, "\n".join(preview_lines)


def show(
    slug: str,
    bridge_dir: Path | None = None,
    index_path: Path | None = None,
    *,
    preview_lines: int = DEFAULT_PREVIEW_LINES,
) -> dict[str, Any]:
    """Load the full version chain for a bridge thread.

    Args:
        slug: Bridge thread slug (e.g., ``"gtkb-bridge-convenience-verbs"``).
        bridge_dir: Path to the bridge directory. Defaults to ``<project>/bridge/``.
        index_path: Path to INDEX.md. Defaults to ``<bridge_dir>/INDEX.md``.
        preview_lines: Per-version content preview line cap (default 200).

    Returns:
        Dict with keys:
          - ``slug``: the requested slug.
          - ``document_entry``: raw INDEX entry block text for the slug (or empty).
          - ``index_status_chain``: list of (status, path) tuples from INDEX (latest at index 0).
          - ``versions``: list of {version, path, verdict_line, content_preview} dicts,
            sorted by version ascending.
          - ``drift``: list of strings describing INDEX-vs-disk discrepancies.
          - ``found``: True if any version files exist on disk.
          - ``preview_lines_cap``: the per-version line cap applied.
    """
    bridge_dir_path = bridge_dir if bridge_dir is not None else DEFAULT_BRIDGE_DIR
    index_path_resolved = index_path if index_path is not None else bridge_dir_path / "INDEX.md"

    version_files = _list_version_files(slug, bridge_dir_path)
    document_entry, status_chain = _index_entry_for_slug(slug, index_path_resolved)

    versions: list[ThreadVersion] = []
    for version_int, path in version_files:
        first_line, preview = _content_preview(path, preview_lines)
        rel_path = path.relative_to(PROJECT_ROOT).as_posix() if PROJECT_ROOT in path.parents else path.as_posix()
        versions.append(
            ThreadVersion(
                version=version_int,
                path=rel_path,
                verdict_line=first_line,
                content_preview=preview,
            )
        )

    drift: list[str] = []
    disk_paths = {f"bridge/{path.name}" for _, path in version_files}
    index_paths = {p for _, p in status_chain}
    for missing in index_paths - disk_paths:
        drift.append(f"INDEX references {missing} but file does not exist on disk")
    for orphan in disk_paths - index_paths:
        drift.append(f"On-disk file {orphan} is not referenced by INDEX")

    return {
        "slug": slug,
        "document_entry": document_entry,
        "index_status_chain": [{"status": s, "path": p} for s, p in status_chain],
        "versions": [v.to_dict() for v in versions],
        "drift": drift,
        "found": bool(versions),
        "preview_lines_cap": preview_lines,
    }


def _format_markdown(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Bridge Thread -- {result['slug']}")
    lines.append("")
    if not result["found"]:
        lines.append(f"_No version files found on disk for slug {result['slug']!r}._")
        return "\n".join(lines)
    lines.append("## INDEX entry")
    lines.append("")
    if result["document_entry"]:
        lines.append("```")
        lines.append(result["document_entry"])
        lines.append("```")
    else:
        lines.append("_(not present in INDEX)_")
    lines.append("")
    if result["drift"]:
        lines.append("## INDEX vs. disk drift")
        lines.append("")
        for entry in result["drift"]:
            lines.append(f"- {entry}")
        lines.append("")
    lines.append(f"## Versions ({len(result['versions'])}, preview <= {result['preview_lines_cap']} lines each)")
    lines.append("")
    for v in result["versions"]:
        lines.append(f"### Version {v['version']:03d} -- {v['verdict_line']}")
        lines.append(f"`{v['path']}`")
        lines.append("")
        lines.append("```")
        lines.append(v["content_preview"])
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Bridge thread slug (e.g., gtkb-bridge-convenience-verbs)")
    parser.add_argument("--bridge-dir", default=None, help="Path to bridge/ (defaults to project bridge/)")
    parser.add_argument("--index-path", default=None, help="Path to INDEX.md (defaults to <bridge-dir>/INDEX.md)")
    parser.add_argument("--preview-lines", type=int, default=DEFAULT_PREVIEW_LINES, help=f"Per-version content preview cap (default: {DEFAULT_PREVIEW_LINES})")
    parser.add_argument("--format", default="json", choices=["json", "markdown"], help="Output format (default: json)")
    args = parser.parse_args(argv)

    bridge_dir = Path(args.bridge_dir) if args.bridge_dir else None
    index_path = Path(args.index_path) if args.index_path else None
    result = show(
        slug=args.slug,
        bridge_dir=bridge_dir,
        index_path=index_path,
        preview_lines=args.preview_lines,
    )

    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_format_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
