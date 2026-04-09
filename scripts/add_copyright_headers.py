#!/usr/bin/env python3
"""Add copyright headers to source files missing them.

Usage:
    python scripts/add_copyright_headers.py          # dry-run (default)
    python scripts/add_copyright_headers.py --apply   # actually write files

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import argparse
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PY_HEADER = "# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.\n"
TS_HEADER = "// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.\n"

# Directories to process
PY_DIRS = [REPO_ROOT / "src"]
TS_DIRS = [
    REPO_ROOT / "admin" / "standalone",
    REPO_ROOT / "admin" / "provider",
    REPO_ROOT / "admin" / "shopify",
    REPO_ROOT / "admin" / "shared",
    REPO_ROOT / "widget" / "src",
]

SKIP_PATTERNS = {"node_modules", "__pycache__", ".git", "dist", "build", "coverage"}
COPYRIGHT_MARKER = "Remaker Digital"


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PATTERNS for part in path.parts)


def has_copyright(content: str) -> bool:
    # Check first 5 lines for copyright marker
    for line in content.split("\n")[:5]:
        if COPYRIGHT_MARKER in line:
            return True
    return False


def add_header_python(path: Path, apply: bool) -> bool:
    content = path.read_text(encoding="utf-8")
    if has_copyright(content):
        return False

    lines = content.split("\n")
    insert_at = 0

    # Preserve shebang line
    if lines and lines[0].startswith("#!"):
        insert_at = 1

    # Preserve encoding declaration
    if len(lines) > insert_at and lines[insert_at].startswith("# -*- coding"):
        insert_at += 1

    new_lines = lines[:insert_at] + [PY_HEADER.rstrip()] + lines[insert_at:]
    new_content = "\n".join(new_lines)

    if apply:
        path.write_text(new_content, encoding="utf-8")
    return True


def add_header_typescript(path: Path, apply: bool) -> bool:
    content = path.read_text(encoding="utf-8")
    if has_copyright(content):
        return False

    new_content = TS_HEADER + content
    if apply:
        path.write_text(new_content, encoding="utf-8")
    return True


def process_directory(directory: Path, extensions: list[str], header_fn, apply: bool) -> list[Path]:
    modified = []
    if not directory.exists():
        return modified

    for ext in extensions:
        for path in directory.rglob(f"*{ext}"):
            if should_skip(path):
                continue
            if path.stat().st_size == 0:
                continue
            if header_fn(path, apply):
                modified.append(path)
    return modified


def main():
    parser = argparse.ArgumentParser(description="Add copyright headers to source files")
    parser.add_argument("--apply", action="store_true", help="Actually modify files (default: dry-run)")
    args = parser.parse_args()

    mode = "APPLYING" if args.apply else "DRY RUN"
    print(f"\n{'=' * 60}")
    print(f"  Copyright Header Tool — {mode}")
    print(f"{'=' * 60}\n")

    total = []

    # Python files
    for d in PY_DIRS:
        modified = process_directory(d, [".py"], add_header_python, args.apply)
        total.extend(modified)
        if modified:
            print(f"  Python ({d.relative_to(REPO_ROOT)}): {len(modified)} files")

    # TypeScript files
    for d in TS_DIRS:
        modified = process_directory(d, [".ts", ".tsx", ".js", ".jsx"], add_header_typescript, args.apply)
        total.extend(modified)
        if modified:
            print(f"  TypeScript ({d.relative_to(REPO_ROOT)}): {len(modified)} files")

    print(f"\n  Total: {len(total)} files {'modified' if args.apply else 'would be modified'}")

    if not args.apply and total:
        print(f"\n  Run with --apply to write changes.")

    print()


if __name__ == "__main__":
    main()
