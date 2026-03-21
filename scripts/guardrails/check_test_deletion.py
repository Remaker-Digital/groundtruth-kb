#!/usr/bin/env python3
"""Pre-commit check: test file deletion guard.

Rejects commits that DELETE any test_*.py file.
Tests can be added or modified, but never removed without owner approval.

Exit codes:
  0 = pass (no test files deleted)
  1 = fail (one or more test files deleted)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_deleted_test_files() -> list[str]:
    """Return list of staged-for-deletion test_*.py files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=D"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    deleted = []
    for line in result.stdout.strip().splitlines():
        normalized = line.strip().replace("\\", "/")
        parts = normalized.split("/")
        if any(p.startswith("test_") and p.endswith(".py") for p in parts):
            deleted.append(normalized)
    return deleted


def main() -> int:
    deleted = get_deleted_test_files()
    if not deleted:
        return 0

    print("=" * 70)
    print("TEST DELETION GUARD FAILED — test files cannot be deleted")
    print("=" * 70)
    for f in deleted:
        print(f"  BLOCKED: {f}")
    print()
    print("Test files can be ADDED or MODIFIED but never DELETED.")
    print("If this is intentional, get owner approval and use:")
    print("  git commit --no-verify")
    print("=" * 70)
    return 1


if __name__ == "__main__":
    sys.exit(main())
