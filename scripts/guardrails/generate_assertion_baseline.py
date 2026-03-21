#!/usr/bin/env python3
"""Generate assertion count baseline for the test assertion ratchet.

Scans all test_*.py files under tests/, counts assertion statements in each,
and writes a JSON baseline file. The pre-commit hook compares staged changes
against this baseline — assertion counts can go UP but never DOWN.

Counted patterns:
  - assert <expr>
  - self.assert* (unittest-style)
  - pytest.raises / pytest.warns / pytest.approx
  - with raises(...) (context manager form)

Usage:
  python scripts/guardrails/generate_assertion_baseline.py [--output PATH]

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
DEFAULT_BASELINE = PROJECT_ROOT / "scripts" / "guardrails" / "assertion-baseline.json"

# Patterns that count as assertions
_ASSERTION_PATTERNS = [
    re.compile(r"^\s*assert\s+", re.MULTILINE),                    # bare assert
    re.compile(r"^\s*self\.assert\w+\s*\(", re.MULTILINE),         # unittest-style
    re.compile(r"\bpytest\.raises\s*\(", re.MULTILINE),            # pytest.raises
    re.compile(r"\bpytest\.warns\s*\(", re.MULTILINE),             # pytest.warns
    re.compile(r"\bpytest\.approx\s*\(", re.MULTILINE),            # pytest.approx
    re.compile(r"^\s*with\s+raises\s*\(", re.MULTILINE),           # from pytest import raises; with raises(...)
]


def count_assertions(file_path: Path) -> int:
    """Count assertion statements in a Python test file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0

    total = 0
    for pattern in _ASSERTION_PATTERNS:
        total += len(pattern.findall(content))
    return total


def scan_tests(tests_dir: Path) -> dict[str, int]:
    """Scan all test_*.py files and return {relative_path: assertion_count}."""
    baseline: dict[str, int] = {}
    for test_file in sorted(tests_dir.rglob("test_*.py")):
        rel_path = test_file.relative_to(PROJECT_ROOT).as_posix()
        count = count_assertions(test_file)
        if count > 0:
            baseline[rel_path] = count
    return baseline


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate assertion count baseline")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_BASELINE,
        help=f"Output file (default: {DEFAULT_BASELINE})",
    )
    args = parser.parse_args()

    baseline = scan_tests(TESTS_DIR)
    total_files = len(baseline)
    total_assertions = sum(baseline.values())

    output_path: Path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "_metadata": {
                    "description": "Assertion count baseline for pre-commit ratchet. DO NOT EDIT MANUALLY.",
                    "total_files": total_files,
                    "total_assertions": total_assertions,
                    "generator": "scripts/guardrails/generate_assertion_baseline.py",
                },
                "baselines": baseline,
            },
            f,
            indent=2,
            sort_keys=True,
        )
        f.write("\n")

    print(f"Baseline generated: {total_files} files, {total_assertions} assertions")
    print(f"Written to: {output_path}")


if __name__ == "__main__":
    main()
