#!/usr/bin/env python3
"""Compare or update GroundTruth KB Wiki pages and assets from in-root source docs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = PROJECT_ROOT / "groundtruth-kb" / "docs" / "wiki"
DEFAULT_WIKI_DIR = PROJECT_ROOT / ".tmp" / "groundtruth-kb.wiki"
WIKI_REPOSITORY_URL = "https://github.com/Remaker-Digital/groundtruth-kb.wiki.git"
WIKI_SOURCE_ALLOWLIST = frozenset(
    {
        "Home.md",
        "_Footer.md",
        "_Sidebar.md",
        "agent-presets.md",
        "azure-enterprise-readiness.md",
        "backup-and-restore.md",
        "controls.md",
        "core-concepts.md",
        "first-governed-change.md",
        "get-started.md",
        "git-integration.md",
        "gtkb-home.md",
        "install-on-windows.md",
        "known-issues.md",
        "models.md",
        "plugins.md",
        "product-overview.md",
        "publication.md",
        "release-health.md",
        "services.md",
        "settings.md",
        "status.md",
        "support.md",
        "system-requirements.md",
        "training.md",
        "troubleshooting.md",
        "uninstall.md",
        "upgrade.md",
        "verify-installation.md",
    }
)
WIKI_ASSET_ALLOWLIST = frozenset(
    {
        "assets/gtkb-agent-presets.png",
        "assets/gtkb-controls.png",
        "assets/gtkb-home-empty-state.png",
        "assets/gtkb-models.png",
        "assets/gtkb-plugins.png",
        "assets/gtkb-services.png",
        "assets/gtkb-settings-general.png",
        "assets/gtkb-status.png",
        "assets/gtkb-workspace-picker.png",
    }
)


def _resolve_in_root(path: Path, project_root: Path) -> Path:
    resolved_root = project_root.resolve()
    resolved_path = path.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise ValueError(f"path is outside project root: {resolved_path}")
    return resolved_path


def wiki_page_name(source_path: Path) -> str:
    """Map an in-root wiki source markdown file to its GitHub Wiki page file."""
    if source_path.name in {"Home.md", "_Footer.md", "_Sidebar.md"}:
        return source_path.name
    words = [part for part in source_path.stem.replace("_", "-").split("-") if part]
    title = "-".join(word[:1].upper() + word[1:] for word in words)
    return f"{title}.md"


def source_pages(source_dir: Path) -> list[Path]:
    return sorted(path for path in source_dir.glob("*.md") if path.is_file() and path.name in WIKI_SOURCE_ALLOWLIST)


def _publication_files(source_dir: Path) -> list[tuple[Path, str, str]]:
    files = [(path, wiki_page_name(path), "page") for path in source_pages(source_dir)]
    files.extend(
        (source_dir / name, name, "asset") for name in sorted(WIKI_ASSET_ALLOWLIST) if (source_dir / name).is_file()
    )
    return files


def _read_content(path: Path, kind: str) -> bytes:
    try:
        if kind == "asset":
            return path.read_bytes()
        return path.read_text(encoding="utf-8").encode("utf-8")
    except FileNotFoundError:
        return b""


def compare_pages(source_dir: Path = DEFAULT_SOURCE_DIR, wiki_dir: Path = DEFAULT_WIKI_DIR) -> list[dict[str, Any]]:
    """Return source-vs-wiki rows for allowlisted pages and their binary assets."""
    rows: list[dict[str, Any]] = []
    for source_path, wiki_name, kind in _publication_files(source_dir):
        wiki_path = wiki_dir / wiki_name
        source_content = _read_content(source_path, kind)
        wiki_content = _read_content(wiki_path, kind)
        if not wiki_path.exists():
            status = "missing"
        elif source_content != wiki_content:
            status = "different"
        else:
            status = "current"
        rows.append(
            {
                "source": str(source_path),
                "kind": kind,
                "wiki_page": wiki_name,
                "wiki_path": str(wiki_path),
                "status": status,
                "source_sha256": hashlib.sha256(source_content).hexdigest(),
                "wiki_sha256": hashlib.sha256(wiki_content).hexdigest() if wiki_path.exists() else "",
            }
        )
    return rows


def update_pages(
    source_dir: Path = DEFAULT_SOURCE_DIR,
    wiki_dir: Path = DEFAULT_WIKI_DIR,
    *,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Copy allowlisted pages and assets into the wiki checkout, without pushing."""
    before = compare_pages(source_dir, wiki_dir)
    if not dry_run:
        wiki_dir.mkdir(parents=True, exist_ok=True)
        for source_path, wiki_name, kind in _publication_files(source_dir):
            target = wiki_dir / wiki_name
            target.parent.mkdir(parents=True, exist_ok=True)
            if kind == "asset":
                target.write_bytes(source_path.read_bytes())
            else:
                target.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    after = compare_pages(source_dir, wiki_dir)
    status_by_page = {row["wiki_page"]: row["status"] for row in after}
    return [
        {
            **row,
            "planned_action": "write" if row["status"] != "current" else "none",
            "post_update_status": status_by_page.get(row["wiki_page"], row["status"]),
        }
        for row in before
    ]


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return {
        "repository": WIKI_REPOSITORY_URL,
        "page_count": sum(1 for row in rows if row.get("kind") != "asset"),
        "asset_count": sum(1 for row in rows if row.get("kind") == "asset"),
        "status_counts": dict(sorted(counts.items())),
        "drift_count": sum(1 for row in rows if row.get("status") != "current"),
    }


def _print_human(
    rows: list[dict[str, Any]],
    *,
    source_dir: Path,
    wiki_dir: Path,
    updated: bool = False,
) -> None:
    summary = _summary(rows)
    print(f"GroundTruth KB wiki source: {source_dir}")
    print(f"GroundTruth KB wiki checkout: {wiki_dir}")
    print(f"Pages: {summary['page_count']} assets: {summary['asset_count']} drift: {summary['drift_count']}")
    for row in rows:
        action = f" -> {row['planned_action']}" if updated else ""
        print(f"{row['status']:>9}{action}  {row['wiki_page']}")


def _args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("compare", "update"))
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--source-dir", type=Path, default=None)
    parser.add_argument("--wiki-dir", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--dry-run", action="store_true", help="For update, report writes without changing files.")
    parser.add_argument("--no-fail-on-drift", action="store_true", help="Return 0 even when compare finds drift.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _args(argv)
    project_root = args.project_root.resolve()
    source_dir = _resolve_in_root(args.source_dir or project_root / "groundtruth-kb" / "docs" / "wiki", project_root)
    wiki_dir = _resolve_in_root(args.wiki_dir or project_root / ".tmp" / "groundtruth-kb.wiki", project_root)

    if args.command == "compare":
        rows = compare_pages(source_dir, wiki_dir)
        payload = {"summary": _summary(rows), "pages": rows}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_human(rows, source_dir=source_dir, wiki_dir=wiki_dir)
        return 0 if args.no_fail_on_drift or payload["summary"]["drift_count"] == 0 else 1

    rows = update_pages(source_dir, wiki_dir, dry_run=args.dry_run)
    payload = {"summary": _summary(rows), "pages": rows, "dry_run": args.dry_run}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_human(rows, source_dir=source_dir, wiki_dir=wiki_dir, updated=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
