#!/usr/bin/env python3
"""Pre-commit check: TSX commit gate.

Requires a SPEC-ID (e.g., SPEC-1234) in the commit message when any .tsx
file is modified. This prevents unauthorized UI changes — every frontend
modification must trace to a specification.

The check reads the commit message from .git/COMMIT_EDITMSG (written by git
before pre-commit runs for `git commit -m "..."`).

Exit codes:
  0 = pass (no TSX changes, or SPEC-ID present in message)
  1 = fail (TSX changes without SPEC-ID)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SPEC_PATTERN = re.compile(r"SPEC-\d+", re.IGNORECASE)


def get_staged_tsx_files() -> list[str]:
    """Return list of staged .tsx files (added, modified, renamed)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    return [
        line.strip()
        for line in result.stdout.strip().splitlines()
        if line.strip().endswith(".tsx")
    ]


def get_commit_message() -> str:
    """Read the pending commit message from COMMIT_EDITMSG."""
    msg_file = PROJECT_ROOT / ".git" / "COMMIT_EDITMSG"
    if msg_file.exists():
        try:
            return msg_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            pass
    return ""


def main() -> int:
    tsx_files = get_staged_tsx_files()
    if not tsx_files:
        return 0  # No TSX files staged

    message = get_commit_message()

    if SPEC_PATTERN.search(message):
        return 0  # SPEC-ID found in commit message

    # Also check if "Co-Authored-By" exists — auto-generated commits from
    # session work always include context. Still require SPEC-ID.
    print("=" * 70)
    print("TSX COMMIT GATE FAILED — UI changes require a SPEC-ID")
    print("=" * 70)
    print(f"  {len(tsx_files)} .tsx file(s) staged:")
    for f in tsx_files[:10]:
        print(f"    {f}")
    if len(tsx_files) > 10:
        print(f"    ... and {len(tsx_files) - 10} more")
    print()
    print("Every frontend change must reference a specification.")
    print('Include SPEC-NNNN in the commit message, e.g.:')
    print('  git commit -m "feat(SPEC-1234): update login form layout"')
    print("=" * 70)
    return 1


if __name__ == "__main__":
    sys.exit(main())
