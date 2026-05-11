"""GTKB-TESTS-PACKAGE-COLLISION-RESOLUTION Step C path-string rewriter.

After `git mv tests platform_tests` (Step B), this executor rewrites
workflow YAML and other text-only references to the staying-platform-tests
root from `tests/` to `platform_tests/`.

Substitution rule:
- Match `tests/` only when it refers to the platform tests root (NOT when
  it's part of `applications/Agent_Red/tests/`, which is the migrated
  application tests dir and stays as-is).
- The regex uses a negative lookbehind: the token preceding `tests/` must
  not end with `Agent_Red/`. This excludes the application tests dir.

Target files (per proposal -003 Step C):
- `.github/workflows/python-tests.yml`
- `.github/workflows/sonarcloud.yml`
- `.github/workflows/lint.yml`
- `.github/workflows/groundtruth-kb-tests.yml`

Other workflows may also be affected; the executor processes ALL files
under `.github/workflows/` defensively and reports per-file edit counts.

Authorized by Codex GO at
`bridge/gtkb-tests-package-collision-resolution-004.md`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable


WORKFLOWS_DIR = Path(".github/workflows")

# Rewrite rule: `tests/` -> `platform_tests/` when the immediate preceding
# context does NOT contain `Agent_Red/` (the migrated application tests
# dir) and does NOT contain `groundtruth-kb/` (the platform-package
# vendored tests dir under groundtruth-kb/). Both have their own
# tests/ subdirectories that are unrelated to the staying platform tests
# at the GT-KB root.
TESTS_TOKEN = re.compile(r"(?<!Agent_Red/)(?<!groundtruth-kb/)\btests/")


def rewrite_line(line: str) -> str:
    """Apply path-string substitution for the platform-tests rename."""
    return TESTS_TOKEN.sub("platform_tests/", line)


def rewrite_file(path: Path, dry_run: bool) -> tuple[int, str]:
    """Rewrite a single file. Return (changes, diff-summary)."""
    if not path.is_file():
        return 0, ""
    original_text = path.read_text(encoding="utf-8")
    new_lines: list[str] = []
    changes = 0
    diff_lines: list[str] = []
    for idx, line in enumerate(original_text.splitlines(keepends=True), start=1):
        new_line = rewrite_line(line)
        if new_line != line:
            changes += 1
            diff_lines.append(f"  L{idx}: - {line.rstrip()}")
            diff_lines.append(f"  L{idx}: + {new_line.rstrip()}")
        new_lines.append(new_line)
    new_text = "".join(new_lines)

    if not dry_run and new_text != original_text:
        path.write_text(new_text, encoding="utf-8")

    return changes, "\n".join(diff_lines)


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="Apply edits (default: dry-run)")
    args = ap.parse_args(list(argv) if argv is not None else None)
    dry_run = not args.apply

    print(f"Mode: {'DRY-RUN (no writes)' if dry_run else 'APPLY (writes)'}")
    print()

    total_changes = 0
    print("=== Workflows (.github/workflows/*.yml) ===")
    for yml in sorted(WORKFLOWS_DIR.glob("*.yml")):
        changes, diff = rewrite_file(yml, dry_run)
        total_changes += changes
        if changes:
            print(f"  {yml}: {changes} line edit(s)")
            print(diff)
    print()

    print(f"Total line edits: {total_changes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
