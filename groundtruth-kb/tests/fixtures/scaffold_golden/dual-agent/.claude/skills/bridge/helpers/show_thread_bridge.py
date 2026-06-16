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
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_BRIDGE_DIR = PROJECT_ROOT / "bridge"
DEFAULT_PREVIEW_LINES = 200

_VERSION_FILE_RE = re.compile(r"-(\d{3})\.md$")
_FILE_STATUS_RE = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED)\b",
    re.IGNORECASE,
)


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


def _content_preview(path: Path, max_lines: int) -> tuple[str, str]:
    """Return (first_line, preview_text) for the given file."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    first_line = lines[0] if lines else ""
    preview_lines = lines[:max_lines]
    return first_line, "\n".join(preview_lines)


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = _FILE_STATUS_RE.match(stripped)
        return match.group(1).upper() if match else None
    return None


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
        index_path: Deprecated compatibility parameter; ignored for live state.
        preview_lines: Per-version content preview line cap (default 200).

    Returns:
        Dict with keys:
          - ``slug``: the requested slug.
          - ``document_entry``: synthesized status block text for the slug.
          - ``index_status_chain``: retained key containing synthesized status chain.
          - ``versions``: list of {version, path, verdict_line, content_preview} dicts,
            sorted by version ascending.
          - ``drift``: list of version-file consistency diagnostics.
          - ``found``: True if any version files exist on disk.
          - ``preview_lines_cap``: the per-version line cap applied.
    """
    bridge_dir_path = bridge_dir if bridge_dir is not None else DEFAULT_BRIDGE_DIR
    _ = index_path

    version_files = _list_version_files(slug, bridge_dir_path)

    versions: list[ThreadVersion] = []
    status_chain: list[tuple[str, str]] = []
    for version_int, path in version_files:
        first_line, preview = _content_preview(path, preview_lines)
        rel_path = path.relative_to(PROJECT_ROOT).as_posix() if PROJECT_ROOT in path.parents else path.as_posix()
        status = _status_from_bridge_file(path)
        if status is not None:
            status_chain.append((status, rel_path))
        versions.append(
            ThreadVersion(
                version=version_int,
                path=rel_path,
                verdict_line=first_line,
                content_preview=preview,
            )
        )

    status_chain.sort(
        key=lambda row: (
            int(_VERSION_FILE_RE.search(Path(row[1]).name).group(1))  # type: ignore[union-attr]
            if _VERSION_FILE_RE.search(Path(row[1]).name)
            else 0
        ),
        reverse=True,
    )
    document_entry = "\n".join([f"Document: {slug}", *[f"{status}: {path}" for status, path in status_chain]])
    drift: list[str] = []

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
    lines.append("## Versioned State")
    lines.append("")
    if result["document_entry"]:
        lines.append("```")
        lines.append(result["document_entry"])
        lines.append("```")
    else:
        lines.append("_(no status-bearing version files found)_")
    lines.append("")
    if result["drift"]:
        lines.append("## Version-File Drift")
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
    parser.add_argument("--index-path", default=None, help="Deprecated compatibility parameter; ignored for live state")
    parser.add_argument(
        "--preview-lines",
        type=int,
        default=DEFAULT_PREVIEW_LINES,
        help=f"Per-version content preview cap (default: {DEFAULT_PREVIEW_LINES})",
    )
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
