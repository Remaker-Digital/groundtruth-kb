"""GTKB-ISOLATION-018 sub-slice 18.E.1 Step 5/5b path-string rewriter.

Updates path strings in the 12 .github/workflows/*.yml files listed in
`workflow_files_in_place_edits` and the 5 Dockerfile-class files listed in
`dockerfile_in_place_edits`. Only path-string substitution; no behavior
change.

Substitution rules:

- `src/`, `admin/`, `widget/`, `branding/` are fully-migrated cluster roots.
  Every occurrence is rewritten to `applications/Agent_Red/<root>/`.
- `config/stripe_product_ids.json` is the lone cluster file move; literal
  rewrite.
- `tests/<subdir>` paths are migration-status-dependent. Subdirs whose
  entire tree migrated are rewritten; subdirs whose entire tree stays are
  left alone; subdirs that split between staying and migrating are
  duplicated (the staying line is preserved and an
  `applications/Agent_Red/tests/<subdir>` sibling line is added in the
  same context — implemented as side-by-side in args lists).

The write-set drives the migration-status lookup so the rewrite logic
cannot drift from the canonical move list.

Authorized by `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-016.md` GO.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable


WRITE_SET = Path(".tmp/e1-drift/write-set.json")
APPLICATION_PREFIX = "applications/Agent_Red"


def build_subdir_migration_map(write_set: dict) -> dict[str, str]:
    """Return a dict mapping `tests/<subdir>` -> 'fully_migrated' | 'fully_staying' | 'split'."""
    migrating = write_set["tests_migrating_source_paths"]
    staying = write_set["tests_staying_platform_paths"]

    migrating_subdirs: set[str] = set()
    for p in migrating:
        parts = p.split("/")
        if len(parts) >= 3 and parts[0] == "tests":
            migrating_subdirs.add(parts[1])

    staying_subdirs: set[str] = set()
    for p in staying:
        parts = p.split("/")
        if len(parts) >= 3 and parts[0] == "tests":
            staying_subdirs.add(parts[1])

    all_subdirs = migrating_subdirs | staying_subdirs
    result: dict[str, str] = {}
    for subdir in all_subdirs:
        in_migrating = subdir in migrating_subdirs
        in_staying = subdir in staying_subdirs
        if in_migrating and in_staying:
            result[subdir] = "split"
        elif in_migrating:
            result[subdir] = "fully_migrated"
        else:
            result[subdir] = "fully_staying"
    return result


CLUSTER_ROOTS = ("src", "admin", "widget", "branding")
CLUSTER_FILE = "config/stripe_product_ids.json"


def rewrite_line(line: str, subdir_status: dict[str, str]) -> str:
    """Apply path-string substitutions to a single line.

    Order of rules:
    1. Cluster file substitution (most specific).
    2. Cluster-root substitutions (src/, admin/, widget/, branding/).
       Match: word boundary OR start-of-token OR after non-alphanumeric_/.
    3. tests/<subdir> substitution based on migration status. Split subdirs:
       duplicate the path inline as two space-separated tokens.
    """
    original = line

    # Rule 1: cluster file
    line = line.replace(CLUSTER_FILE, f"{APPLICATION_PREFIX}/{CLUSTER_FILE}")

    # Rule 2: cluster roots with trailing slash (paths) or trailing word boundary
    # Use a regex with negative-lookbehind to avoid matching e.g. `xsrc/`, `myadmin/`.
    for root in CLUSTER_ROOTS:
        # Match: leading boundary + root + (slash OR end-of-token boundary)
        # Avoid matching inside identifiers like `myadmin` or `xsrc`.
        pattern = re.compile(
            r"(?<![a-zA-Z0-9_/])" + re.escape(root) + r"(?=[/\s'\"`,)\]:*]|$)"
        )
        line = pattern.sub(f"{APPLICATION_PREFIX}/{root}", line)

    # Rule 3: tests/<subdir> migration-status-aware
    # Find every `tests/<subdir>` token; decide per match.
    def replace_tests_token(match: re.Match[str]) -> str:
        prefix = match.group(1)  # boundary character that came before
        subdir = match.group(2)
        suffix = match.group(3)  # boundary or path-continuation
        status = subdir_status.get(subdir)
        if status is None:
            # Unknown subdir — could be a top-level test file like tests/test_foo.py;
            # leave alone (top-level files split similarly but are less common).
            return match.group(0)
        if status == "fully_migrated":
            return f"{prefix}{APPLICATION_PREFIX}/tests/{subdir}{suffix}"
        if status == "fully_staying":
            return match.group(0)
        # split: duplicate inline. If suffix starts with '/' or '*', keep it.
        return (
            f"{prefix}tests/{subdir}{suffix} "
            f"{APPLICATION_PREFIX}/tests/{subdir}{suffix}"
        )

    line = re.sub(
        r"(^|[^a-zA-Z0-9_/])tests/([a-zA-Z][a-zA-Z0-9_]*)(/?[*]*)",
        replace_tests_token,
        line,
    )

    return line


def rewrite_file(path: Path, subdir_status: dict[str, str], dry_run: bool) -> tuple[int, str]:
    """Rewrite a single file. Return (changes, diff-summary)."""
    original_text = path.read_text(encoding="utf-8")
    new_lines: list[str] = []
    changes = 0
    diff_lines: list[str] = []
    for idx, line in enumerate(original_text.splitlines(keepends=True), start=1):
        new_line = rewrite_line(line, subdir_status)
        if new_line != line:
            changes += 1
            diff_lines.append(f"  L{idx}: - {line.rstrip()}")
            diff_lines.append(f"  L{idx}: + {new_line.rstrip()}")
        new_lines.append(new_line)
    new_text = "".join(new_lines)

    if not dry_run and new_text != original_text:
        path.write_text(new_text, encoding="utf-8")

    return changes, "\n".join(diff_lines)


WORKFLOW_FILES_KEY = "workflow_files_in_place_edits"
DOCKERFILE_FILES_KEY = "dockerfile_in_place_edits"


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="Apply edits (default: dry-run)")
    args = ap.parse_args(list(argv) if argv is not None else None)
    dry_run = not args.apply

    if not WRITE_SET.exists():
        print(f"ERROR: write-set not found at {WRITE_SET}.")
        return 2
    write_set = json.loads(WRITE_SET.read_text(encoding="utf-8"))
    subdir_status = build_subdir_migration_map(write_set)

    print(f"Mode: {'DRY-RUN (no writes)' if dry_run else 'APPLY (writes)'}")
    print(f"subdir status: {len(subdir_status)} subdirs classified")
    print(
        f"  fully_migrated: {sum(1 for v in subdir_status.values() if v == 'fully_migrated')}"
    )
    print(
        f"  fully_staying:  {sum(1 for v in subdir_status.values() if v == 'fully_staying')}"
    )
    print(f"  split:          {sum(1 for v in subdir_status.values() if v == 'split')}")
    print()

    total_changes = 0
    for category, key in (("Workflows (Step 5)", WORKFLOW_FILES_KEY), ("Dockerfiles (Step 5b)", DOCKERFILE_FILES_KEY)):
        print(f"=== {category} ===")
        for f in write_set.get(key, []):
            p = Path(f)
            if not p.exists():
                print(f"  MISSING: {f}")
                continue
            changes, diff = rewrite_file(p, subdir_status, dry_run)
            total_changes += changes
            print(f"  {f}: {changes} line edit(s)")
            if diff and changes <= 12:  # show full diff for small changes; summary for big
                print(diff)
            elif diff:
                # Show first 6 and last 2 changes for large diffs
                diff_lines = diff.split("\n")
                print("\n".join(diff_lines[:12]))
                print(f"  ... ({len(diff_lines) - 14} more diff lines)")
                print("\n".join(diff_lines[-2:]))
        print()

    print(f"Total line edits: {total_changes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
