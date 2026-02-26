"""
Feature Assertion Runner — reads assertion definitions from the knowledge database,
executes grep/glob checks against the local codebase, and writes results back.

Three assertion types:
  - grep:        re.findall(pattern, file_content) count >= min_count
  - glob:        Path.glob(pattern) returns >= 1 match
  - grep_absent: re.findall(pattern, file_content) count == 0

Usage:
  python tools/knowledge-db/assertions.py                  # run all, manual trigger
  python tools/knowledge-db/assertions.py --pre-build      # pre-build gate
  python tools/knowledge-db/assertions.py --session-start  # session startup check
  python tools/knowledge-db/assertions.py --spec 245       # single spec only

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# Project root: 3 levels up from tools/knowledge-db/assertions.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Import sibling module
from db import KnowledgeDB


_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB — skip binary/huge files


def _read_file_safe(file_path: Path) -> str | None:
    """Read file contents, returning None if the file doesn't exist, is too large, or can't be read."""
    try:
        if file_path.stat().st_size > _MAX_FILE_SIZE:
            return None
        return file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return None


_VALID_ASSERTION_TYPES = {"grep", "glob", "grep_absent"}
_REQUIRED_FIELDS = {
    "grep": ("type", "pattern", "file", "description"),
    "glob": ("type", "pattern", "description"),
    "grep_absent": ("type", "pattern", "file", "description"),
}


def run_single_assertion(assertion: dict[str, Any]) -> dict[str, Any]:
    """Execute one assertion definition and return the result.

    Each assertion dict has:
      - type: "grep", "glob", or "grep_absent"
      - pattern: regex pattern (grep/grep_absent) or glob pattern (glob)
      - file: relative file path from project root (grep/grep_absent)
      - min_count: minimum match count (grep only, default 1)
      - description: human-readable explanation

    Returns:
      - type, description, passed (bool), detail (str)
    """
    a_type = assertion.get("type", "")
    pattern = assertion.get("pattern", "")
    description = assertion.get("description", "")

    # Validate assertion definition
    if a_type not in _VALID_ASSERTION_TYPES:
        return {
            "type": a_type, "description": description, "passed": False,
            "detail": f"Invalid assertion type: {a_type!r}. Valid: {_VALID_ASSERTION_TYPES}",
        }
    for field in _REQUIRED_FIELDS.get(a_type, ()):
        if not assertion.get(field):
            return {
                "type": a_type, "description": description, "passed": False,
                "detail": f"Missing required field '{field}' for assertion type '{a_type}'",
            }
    result: dict[str, Any] = {
        "type": a_type,
        "description": description,
        "passed": False,
        "detail": "",
    }

    if a_type == "grep":
        file_rel = assertion.get("file", "")
        min_count = assertion.get("min_count", 1)
        file_path = PROJECT_ROOT / file_rel
        content = _read_file_safe(file_path)
        if content is None:
            result["detail"] = f"File not found: {file_rel}"
            return result
        matches = re.findall(pattern, content)
        count = len(matches)
        result["passed"] = count >= min_count
        result["detail"] = f"Found {count} match(es), need >= {min_count}"

    elif a_type == "glob":
        matches = list(PROJECT_ROOT.glob(pattern))
        count = len(matches)
        result["passed"] = count >= 1
        result["detail"] = f"Found {count} file(s) matching '{pattern}'"

    elif a_type == "grep_absent":
        file_rel = assertion.get("file", "")
        file_path = PROJECT_ROOT / file_rel
        content = _read_file_safe(file_path)
        if content is None:
            # File not existing means the pattern is absent — pass
            result["passed"] = True
            result["detail"] = f"File not found (pattern trivially absent): {file_rel}"
            return result
        matches = re.findall(pattern, content)
        count = len(matches)
        result["passed"] = count == 0
        result["detail"] = f"Found {count} match(es), need 0"

    else:
        result["detail"] = f"Unknown assertion type: {a_type}"

    return result


def run_spec_assertions(
    db: KnowledgeDB, spec: dict[str, Any], triggered_by: str
) -> dict[str, Any]:
    """Run all assertions for a single spec and record results.

    Returns:
      {spec_id, title, overall_passed, results: [...], assertion_count}
    """
    spec_id = spec["id"]
    spec_version = spec["version"]
    assertions = spec.get("_assertions_parsed") or []

    if not assertions:
        return {
            "spec_id": spec_id,
            "title": spec["title"],
            "overall_passed": True,
            "results": [],
            "assertion_count": 0,
            "skipped": True,
        }

    results = [run_single_assertion(a) for a in assertions]
    overall_passed = all(r["passed"] for r in results)

    # Record in database
    db.insert_assertion_run(
        spec_id=spec_id,
        spec_version=spec_version,
        overall_passed=overall_passed,
        results=results,
        triggered_by=triggered_by,
    )

    return {
        "spec_id": spec_id,
        "title": spec["title"],
        "overall_passed": overall_passed,
        "results": results,
        "assertion_count": len(results),
        "skipped": False,
    }


def run_all_assertions(
    db: KnowledgeDB, triggered_by: str = "manual", spec_id: str | None = None
) -> dict[str, Any]:
    """Run assertions for all specs (or a single spec) and return summary.

    Returns:
      {total_specs, specs_with_assertions, passed, failed, skipped,
       details: [{spec_id, title, overall_passed, results, ...}, ...]}
    """
    if spec_id:
        spec = db.get_spec(spec_id)
        if not spec:
            return {"error": f"Spec {spec_id} not found"}
        specs = [spec]
    else:
        specs = db.list_specs()

    details = []
    passed = 0
    failed = 0
    skipped = 0

    for spec in specs:
        result = run_spec_assertions(db, spec, triggered_by)
        details.append(result)
        if result.get("skipped"):
            skipped += 1
        elif result["overall_passed"]:
            passed += 1
        else:
            failed += 1

    return {
        "total_specs": len(specs),
        "specs_with_assertions": len(specs) - skipped,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "triggered_by": triggered_by,
        "details": details,
    }


def print_summary(summary: dict[str, Any]) -> None:
    """Print a human-readable assertion summary to stdout."""
    if "error" in summary:
        print(f"ERROR: {summary['error']}")
        return

    print(f"\n{'=' * 60}")
    print(f"  Feature Assertion Results — triggered by: {summary['triggered_by']}")
    print(f"{'=' * 60}")
    print(f"  Total specs:       {summary['total_specs']}")
    print(f"  With assertions:   {summary['specs_with_assertions']}")
    print(f"  PASSED:            {summary['passed']}")
    print(f"  FAILED:            {summary['failed']}")
    print(f"  Skipped (no def):  {summary['skipped']}")
    print(f"{'=' * 60}\n")

    # Show failures in detail
    failures = [d for d in summary["details"] if not d.get("skipped") and not d["overall_passed"]]
    if failures:
        print("FAILURES:\n")
        for f in failures:
            print(f"  [{f['spec_id']}] {f['title']}")
            for r in f["results"]:
                status = "PASS" if r["passed"] else "FAIL"
                print(f"    [{status}] {r['description']}: {r['detail']}")
            print()

    # Show passes briefly
    passes = [d for d in summary["details"] if not d.get("skipped") and d["overall_passed"]]
    if passes:
        print("PASSED:\n")
        for p in passes:
            print(f"  [{p['spec_id']}] {p['title']} ({p['assertion_count']} assertions)")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run feature assertions against codebase")
    parser.add_argument("--pre-build", action="store_true", help="Pre-build gate mode")
    parser.add_argument("--session-start", action="store_true", help="Session startup check")
    parser.add_argument("--spec", type=str, default=None, help="Run assertions for a single spec ID")
    args = parser.parse_args()

    triggered_by = "manual"
    if args.pre_build:
        triggered_by = "pre-build"
    elif args.session_start:
        triggered_by = "session-start"

    db = KnowledgeDB()
    try:
        summary = run_all_assertions(db, triggered_by=triggered_by, spec_id=args.spec)
        print_summary(summary)

        # Exit code: 0 if all pass, 1 if any failures (useful for CI gates)
        if summary.get("failed", 0) > 0:
            return 1
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
