#!/usr/bin/env python3
"""Compare or update GT-KB GitHub Wiki pages from in-root source docs."""

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


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _resolve_in_root(path: Path, project_root: Path) -> Path:
    resolved_root = project_root.resolve()
    resolved_path = path.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise ValueError(f"path is outside project root: {resolved_path}")
    return resolved_path


def wiki_page_name(source_path: Path) -> str:
    """Map an in-root wiki source markdown file to its GitHub Wiki page file."""
    if source_path.name == "Home.md":
        return "Home.md"
    words = [part for part in source_path.stem.replace("_", "-").split("-") if part]
    title = "-".join(word[:1].upper() + word[1:] for word in words)
    return f"{title}.md"


def source_pages(source_dir: Path) -> list[Path]:
    return sorted(path for path in source_dir.glob("*.md") if path.is_file())


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def compare_pages(source_dir: Path = DEFAULT_SOURCE_DIR, wiki_dir: Path = DEFAULT_WIKI_DIR) -> list[dict[str, Any]]:
    """Return per-page source-vs-wiki comparison rows."""
    rows: list[dict[str, Any]] = []
    for source_path in source_pages(source_dir):
        wiki_name = wiki_page_name(source_path)
        wiki_path = wiki_dir / wiki_name
        source_text = _read_text(source_path)
        wiki_text = _read_text(wiki_path)
        if not wiki_path.exists():
            status = "missing"
        elif source_text != wiki_text:
            status = "different"
        else:
            status = "current"
        rows.append(
            {
                "source": str(source_path),
                "wiki_page": wiki_name,
                "wiki_path": str(wiki_path),
                "status": status,
                "source_sha256": _sha256_text(source_text),
                "wiki_sha256": _sha256_text(wiki_text) if wiki_path.exists() else "",
            }
        )
    return rows


def update_pages(
    source_dir: Path = DEFAULT_SOURCE_DIR,
    wiki_dir: Path = DEFAULT_WIKI_DIR,
    *,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Copy source pages into the in-root wiki checkout and return comparison rows."""
    before = compare_pages(source_dir, wiki_dir)
    if not dry_run:
        wiki_dir.mkdir(parents=True, exist_ok=True)
        for source_path in source_pages(source_dir):
            target = wiki_dir / wiki_page_name(source_path)
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
        "page_count": len(rows),
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
    print(f"GT-KB wiki source: {source_dir}")
    print(f"GT-KB wiki checkout: {wiki_dir}")
    print(f"Pages: {summary['page_count']} drift: {summary['drift_count']}")
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
