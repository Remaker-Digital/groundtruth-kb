#!/usr/bin/env python3
"""Session-scoped mutation testing runner (SPEC-1842 / WI-1478, WI-1479).

Runs mutmut only on files modified in the current session (git diff), not the
full codebase. Reports mutation score and highlights surviving mutants.

Usage:
    python scripts/run_mutation_tests.py [--target-score 70] [--files FILE...]

If --files is not given, auto-detects changed src/ files from git status.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Minimum acceptable mutation score (killed / total mutants * 100)
DEFAULT_TARGET_SCORE = 70


def get_changed_src_files() -> list[str]:
    """Get src/ Python files modified in the working tree (staged + unstaged)."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    files = []
    for line in result.stdout.strip().splitlines():
        if line.startswith("src/") and line.endswith(".py"):
            path = PROJECT_ROOT / line
            if path.exists():
                files.append(line)

    # Also check unstaged changes
    result2 = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    for line in result2.stdout.strip().splitlines():
        if line.startswith("src/") and line.endswith(".py") and line not in files:
            path = PROJECT_ROOT / line
            if path.exists():
                files.append(line)

    return files


def run_mutmut(files: list[str], target_score: int) -> int:
    """Run mutmut on specified files and report results.

    Returns 0 if mutation score >= target, 1 otherwise.
    """
    if not files:
        print("No changed src/ files to mutate. Skipping mutation testing.")
        return 0

    print(f"Mutation testing {len(files)} file(s):")
    for f in files:
        print(f"  {f}")
    print()

    # Run mutmut for each file
    total_killed = 0
    total_survived = 0
    total_timeout = 0
    total_error = 0

    for filepath in files:
        print(f"--- Mutating: {filepath} ---")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "mutmut",
                "run",
                "--paths-to-mutate",
                filepath,
                "--no-progress",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=300,  # 5 min per file max
        )

        output = result.stdout + result.stderr
        print(output[-500:] if len(output) > 500 else output)

        # Parse results from mutmut output
        for line in output.splitlines():
            if "killed" in line.lower():
                # Try to extract counts from summary line
                pass  # mutmut output format varies; we'll use `mutmut results`

    # Get overall results
    result = subprocess.run(
        [sys.executable, "-m", "mutmut", "results"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    print("\n=== Mutation Testing Results ===")
    print(result.stdout)

    # Parse summary
    for line in result.stdout.splitlines():
        line_lower = line.lower().strip()
        if "killed" in line_lower:
            # Count killed mutants from the listing
            total_killed += 1
        elif "survived" in line_lower:
            total_survived += 1
        elif "timeout" in line_lower:
            total_timeout += 1

    total = total_killed + total_survived + total_timeout + total_error
    if total == 0:
        print("No mutants generated. Nothing to score.")
        return 0

    score = (total_killed / total) * 100
    print(f"\nMutation Score: {score:.1f}% ({total_killed}/{total} killed)")
    print(f"Target: >= {target_score}%")

    if score >= target_score:
        print("PASS: Mutation score meets target.")
        return 0
    else:
        print(f"WARN: Mutation score {score:.1f}% below target {target_score}%.")
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Session-scoped mutation testing")
    parser.add_argument(
        "--target-score",
        type=int,
        default=DEFAULT_TARGET_SCORE,
        help=f"Minimum mutation score percentage (default: {DEFAULT_TARGET_SCORE})",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        help="Specific files to mutate (default: auto-detect from git)",
    )
    args = parser.parse_args()

    files = args.files or get_changed_src_files()
    exit_code = run_mutmut(files, args.target_score)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
