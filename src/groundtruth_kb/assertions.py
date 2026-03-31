"""
GroundTruth KB — Feature Assertion Runner.

Reads assertion definitions from the knowledge database, executes grep/glob
checks against a project codebase, and writes results back.

Three assertion types:
  - grep:        re.findall(pattern, file_content) count >= min_count
  - glob:        Path.glob(pattern) returns >= 1 match
  - grep_absent: re.findall(pattern, file_content) count == 0

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from groundtruth_kb.db import KnowledgeDB

_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB — skip binary/huge files

_VALID_ASSERTION_TYPES = {"grep", "glob", "grep_absent"}


def _read_file_safe(file_path: Path) -> str | None:
    """Read file contents, returning None if the file doesn't exist, is too large, or can't be read."""
    try:
        if file_path.stat().st_size > _MAX_FILE_SIZE:
            return None
        return file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return None


def run_single_assertion(assertion: dict[str, Any], project_root: Path) -> dict[str, Any]:
    """Execute one assertion definition and return the result.

    Each assertion dict has:
      - type: "grep", "glob", or "grep_absent"
      - pattern: regex pattern (grep/grep_absent) or glob pattern (glob)
      - file: relative file path from project root (grep/grep_absent)
        (also accepts file_pattern as alias for file)
      - min_count: minimum match count (grep only, default 1)
      - description: human-readable explanation
      - contains: (glob only) optional string that must appear in matched files

    Args:
        assertion: Assertion definition dict.
        project_root: Resolved project root for file resolution.

    Returns:
      dict with type, description, passed (bool), detail (str)
    """
    a_type = assertion.get("type", "")
    # Normalize field aliases: query → pattern, target/path/expected → file
    pattern = assertion.get("pattern") or assertion.get("query", "")
    description = assertion.get("description", "") or f"{a_type}: {pattern}"

    # Validate assertion definition — skip non-machine types gracefully
    if a_type not in _VALID_ASSERTION_TYPES:
        return {
            "type": a_type,
            "description": description,
            "passed": True,
            "detail": f"Skipped non-machine assertion type: {a_type!r} (only {_VALID_ASSERTION_TYPES} are executable)",
            "skipped": True,
        }
    if not pattern:
        return {
            "type": a_type,
            "description": description,
            "passed": False,
            "detail": f"Missing 'pattern' (or 'query') for assertion type '{a_type}'",
        }

    result: dict[str, Any] = {
        "type": a_type,
        "description": description,
        "passed": False,
        "detail": "",
    }

    if a_type == "grep":
        file_rel = (
            assertion.get("file")
            or assertion.get("file_pattern")
            or assertion.get("target")
            or assertion.get("path")
            or assertion.get("expected")
            or ""
        )
        min_count = assertion.get("min_count", 1)
        if not file_rel:
            result["detail"] = "Missing 'file' (or 'file_pattern') field"
            return result
        # file_pattern may be a glob (e.g., "**/cosmos_schema.py") — resolve
        if "*" in file_rel:
            matched_files = list(project_root.glob(file_rel))
            if not matched_files:
                result["detail"] = f"No files matching glob: {file_rel}"
                return result
            total_count = 0
            for mf in matched_files:
                content = _read_file_safe(mf)
                if content:
                    total_count += len(re.findall(pattern, content))
            result["passed"] = total_count >= min_count
            result["detail"] = f"Found {total_count} match(es) across {len(matched_files)} file(s), need >= {min_count}"
        else:
            file_path = project_root / file_rel
            content = _read_file_safe(file_path)
            if content is None:
                result["detail"] = f"File not found: {file_rel}"
                return result
            matches = re.findall(pattern, content)
            count = len(matches)
            result["passed"] = count >= min_count
            result["detail"] = f"Found {count} match(es), need >= {min_count}"

    elif a_type == "glob":
        matches = list(project_root.glob(pattern))
        contains = assertion.get("contains", "")
        if contains:
            matches = [m for m in matches if m.is_file() and contains in (_read_file_safe(m) or "")]
            count = len(matches)
            result["passed"] = count >= 1
            result["detail"] = f"Found {count} file(s) matching '{pattern}' containing '{contains}'"
        else:
            count = len(matches)
            result["passed"] = count >= 1
            result["detail"] = f"Found {count} file(s) matching '{pattern}'"

    elif a_type == "grep_absent":
        file_rel = (
            assertion.get("file")
            or assertion.get("file_pattern")
            or assertion.get("target")
            or assertion.get("path")
            or assertion.get("expected")
            or ""
        )
        if not file_rel:
            result["detail"] = "Missing 'file' (or 'file_pattern') field"
            return result
        if "*" in file_rel:
            matched_files = list(project_root.glob(file_rel))
            if not matched_files:
                result["passed"] = True
                result["detail"] = f"No files matching glob (pattern trivially absent): {file_rel}"
                return result
            total_count = 0
            for mf in matched_files:
                content = _read_file_safe(mf)
                if content:
                    total_count += len(re.findall(pattern, content))
            result["passed"] = total_count == 0
            result["detail"] = f"Found {total_count} match(es) across {len(matched_files)} file(s), need 0"
        else:
            file_path = project_root / file_rel
            content = _read_file_safe(file_path)
            if content is None:
                result["passed"] = True
                result["detail"] = f"File not found (pattern trivially absent): {file_rel}"
                return result
            matches = re.findall(pattern, content)
            count = len(matches)
            result["passed"] = count == 0
            result["detail"] = f"Found {count} match(es), need 0"

    return result


def run_spec_assertions(
    db: KnowledgeDB,
    spec: dict[str, Any],
    triggered_by: str,
    project_root: Path,
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

    results = [
        run_single_assertion(a, project_root)
        if isinstance(a, dict)
        else {
            "type": "text",
            "description": str(a)[:120],
            "passed": True,
            "detail": "Non-machine assertion (plain text) — skipped",
            "skipped": True,
        }
        for a in assertions
    ]

    # Only machine-checkable assertions determine overall_passed
    machine_results = [r for r in results if not r.get("skipped")]
    overall_passed = all(r["passed"] for r in machine_results) if machine_results else True

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
        "assertion_count": len(machine_results),
        "skipped": len(machine_results) == 0 and len(results) > 0,
    }


def run_all_assertions(
    db: KnowledgeDB,
    project_root: Path,
    triggered_by: str = "manual",
    spec_id: str | None = None,
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
        result = run_spec_assertions(db, spec, triggered_by, project_root)
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


def format_summary(summary: dict[str, Any]) -> str:
    """Format an assertion summary as a human-readable string."""
    if "error" in summary:
        return f"ERROR: {summary['error']}"

    lines: list[str] = []
    lines.append(f"\n{'=' * 60}")
    lines.append(f"  Assertion Results — triggered by: {summary['triggered_by']}")
    lines.append(f"{'=' * 60}")
    lines.append(f"  Total specs:       {summary['total_specs']}")
    lines.append(f"  With assertions:   {summary['specs_with_assertions']}")
    lines.append(f"  PASSED:            {summary['passed']}")
    lines.append(f"  FAILED:            {summary['failed']}")
    lines.append(f"  Skipped (no def):  {summary['skipped']}")
    lines.append(f"{'=' * 60}\n")

    # Show failures in detail
    failures = [d for d in summary["details"] if not d.get("skipped") and not d["overall_passed"]]
    if failures:
        lines.append("FAILURES:\n")
        for f in failures:
            lines.append(f"  [{f['spec_id']}] {f['title']}")
            for r in f["results"]:
                status = "PASS" if r["passed"] else "FAIL"
                lines.append(f"    [{status}] {r['description']}: {r['detail']}")
            lines.append("")

    # Show passes briefly
    passes = [d for d in summary["details"] if not d.get("skipped") and d["overall_passed"]]
    if passes:
        lines.append("PASSED:\n")
        for p in passes:
            lines.append(f"  [{p['spec_id']}] {p['title']} ({p['assertion_count']} assertions)")
        lines.append("")

    return "\n".join(lines)
