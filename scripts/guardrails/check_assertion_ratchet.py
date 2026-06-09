#!/usr/bin/env python3
"""Pre-commit check: assertion count ratchet.

Compares assertion counts in staged test files against the committed baseline.
If any file's assertion count DECREASED, the commit is rejected.
If any file's assertion count INCREASED, the baseline is auto-updated.

Exit codes:
  0 = pass (baseline may have been auto-updated)
  1 = fail (assertion count decreased in one or more files)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Reuse the counting logic from the generator
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_assertion_baseline import count_assertions, PROJECT_ROOT

BASELINE_PATH = Path(__file__).resolve().parent / "assertion-baseline.json"


def get_staged_test_files() -> list[str]:
    """Return list of staged test_*.py files (relative paths, forward slashes)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    files = []
    for line in result.stdout.strip().splitlines():
        normalized = line.strip().replace("\\", "/")
        if normalized.startswith("tests/") and normalized.endswith(".py"):
            parts = normalized.split("/")
            if any(p.startswith("test_") for p in parts):
                files.append(normalized)
    return files


def main() -> int:
    if not BASELINE_PATH.exists():
        print("WARNING: No assertion baseline found. Run generate_assertion_baseline.py first.")
        print("Skipping assertion ratchet check.")
        return 0

    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    baselines: dict[str, int] = data.get("baselines", {})
    staged_files = get_staged_test_files()

    if not staged_files:
        return 0  # No test files staged

    violations: list[str] = []
    updates: dict[str, int] = {}

    for rel_path in staged_files:
        abs_path = PROJECT_ROOT / rel_path
        if not abs_path.exists():
            continue  # File being deleted -- handled by deletion guard

        current_count = count_assertions(abs_path)
        baseline_count = baselines.get(rel_path, 0)

        if current_count < baseline_count:
            violations.append(
                f"  FAIL: {rel_path}: assertions {baseline_count} -> {current_count} "
                f"(decreased by {baseline_count - current_count})"
            )
        elif current_count > baseline_count:
            updates[rel_path] = current_count

    if violations:
        print("=" * 70)
        print("ASSERTION RATCHET FAILED -- assertion counts decreased")
        print("=" * 70)
        for v in violations:
            print(v)
        print()
        print("Assertions can be ADDED but never REMOVED.")
        print("If this is intentional, get owner approval and regenerate the baseline:")
        print("  python scripts/guardrails/generate_assertion_baseline.py")
        print("=" * 70)
        return 1

    # Auto-update baseline for increased counts
    if updates:
        for path, new_count in updates.items():
            baselines[path] = new_count
        data["baselines"] = baselines
        data["_metadata"]["total_assertions"] = sum(baselines.values())
        data["_metadata"]["total_files"] = len(baselines)
        with open(BASELINE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        # Stage the updated baseline
        subprocess.run(
            ["git", "add", str(BASELINE_PATH)],
            cwd=PROJECT_ROOT,
        )
        print(f"Assertion ratchet: {len(updates)} file(s) increased -- baseline auto-updated.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
