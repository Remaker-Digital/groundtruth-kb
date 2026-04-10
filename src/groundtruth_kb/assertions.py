"""
GroundTruth KB — Feature Assertion Runner.

Reads assertion definitions from the knowledge database, executes checks
against a project codebase, and writes results back.

Executable assertion types:
  - grep:        re.findall(pattern, file_content) count >= min_count
  - glob:        Path.glob(pattern) returns >= 1 match
  - grep_absent: re.findall(pattern, file_content) count == 0
  - file_exists: single file exists and is a file
  - count:       grep with operator comparison (==, !=, >, >=, <, <=)
  - json_path:   read JSON/TOML file, walk dotted path, compare value

Composition operators:
  - all_of:      all child assertions must pass (AND)
  - any_of:      at least one child must pass (OR)

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import operator
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from groundtruth_kb.db import KnowledgeDB

_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB — skip binary/huge files
_MAX_COMPOSITION_DEPTH = 3

_VALID_ASSERTION_TYPES = {
    "grep",
    "glob",
    "grep_absent",
    "file_exists",
    "count",
    "json_path",
    "all_of",
    "any_of",
}

# ---------------------------------------------------------------------------
# Phase 0: Path confinement
# ---------------------------------------------------------------------------

_PARENT_TRAVERSAL = re.compile(r"(^|[\\/])\.\.($|[\\/])")


def _is_absolute(path_str: str) -> bool:
    """Check if a path string is absolute on any platform."""
    return PurePosixPath(path_str).is_absolute() or PureWindowsPath(path_str).is_absolute()


def _has_parent_traversal(path_str: str) -> bool:
    """Check if a path string contains parent directory traversal (..)."""
    return bool(_PARENT_TRAVERSAL.search(path_str))


def _safe_resolve(path_str: str, project_root: Path) -> Path | None:
    """Resolve a relative file path safely within project_root.

    Returns the resolved Path, or None if the path escapes the root.
    Rejects absolute paths and parent traversal before resolution.
    """
    if _is_absolute(path_str):
        return None
    if _has_parent_traversal(path_str):
        return None
    resolved = (project_root / path_str).resolve()
    if not resolved.is_relative_to(project_root.resolve()):
        return None  # symlink escape
    return resolved


def _safe_glob(pattern: str, project_root: Path) -> list[Path] | None:
    """Execute a glob pattern confined to project_root.

    Two-layer defense:
      Layer 1 (pre-rejection): reject patterns with .. or absolute paths
                                before Path.glob() is ever called.
      Layer 2 (post-filtering): verify every match stays within root
                                 (catches symlink escapes).

    Returns list of matching Paths, or None if the pattern is unsafe.
    """
    # Layer 1: pre-rejection
    if _has_parent_traversal(pattern):
        return None
    if _is_absolute(pattern):
        return None

    # Pattern is safe — execute glob
    matches = list(project_root.glob(pattern))

    # Layer 2: post-filtering (defense-in-depth for symlinks)
    root_resolved = project_root.resolve()
    return [p for p in matches if p.resolve().is_relative_to(root_resolved)]


def _read_file_safe(file_path: Path) -> str | None:
    """Read file contents, returning None if the file doesn't exist, is too large, or can't be read."""
    try:
        if file_path.stat().st_size > _MAX_FILE_SIZE:
            return None
        return file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return None


# ---------------------------------------------------------------------------
# Phase 1: Execution context and normalization
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AssertionContext:
    """Shared execution context for assertion handlers."""

    project_root: Path
    depth: int = 0
    max_depth: int = _MAX_COMPOSITION_DEPTH


# Field alias mapping: alias → canonical name
_FILE_ALIASES = ("file", "file_pattern", "target", "path", "expected")
_PATTERN_ALIASES = ("pattern", "query")


def _normalize_assertion(assertion: dict[str, Any]) -> dict[str, Any]:
    """Normalize field aliases to canonical names.

    Creates a shallow copy with aliases resolved:
      - query → pattern
      - file_pattern / target / path / expected → file
    """
    normalized = dict(assertion)

    # Resolve pattern aliases
    if "pattern" not in normalized:
        for alias in _PATTERN_ALIASES:
            if alias in normalized and normalized[alias]:
                normalized["pattern"] = normalized[alias]
                break

    # Resolve file aliases
    if "file" not in normalized:
        for alias in _FILE_ALIASES:
            if alias in normalized and normalized[alias]:
                normalized["file"] = normalized[alias]
                break

    return normalized


def _fail(a_type: str, description: str, detail: str) -> dict[str, Any]:
    """Build a FAIL result dict."""
    return {"type": a_type, "description": description, "passed": False, "detail": detail}


def _pass(a_type: str, description: str, detail: str) -> dict[str, Any]:
    """Build a PASS result dict."""
    return {"type": a_type, "description": description, "passed": True, "detail": detail}


def _skip(a_type: str, description: str, detail: str) -> dict[str, Any]:
    """Build a skipped result dict."""
    return {"type": a_type, "description": description, "passed": True, "detail": detail, "skipped": True}


# ---------------------------------------------------------------------------
# Phase 1+2: Type handlers
# ---------------------------------------------------------------------------


def _resolve_file_or_glob(file_rel: str, ctx: AssertionContext) -> tuple[list[Path] | None, str | None]:
    """Resolve a file field that may be a direct path or glob pattern.

    Returns (file_list, error_detail). If error_detail is not None, resolution failed.
    """
    if "*" in file_rel:
        matches = _safe_glob(file_rel, ctx.project_root)
        if matches is None:
            return None, f"Unsafe glob pattern rejected: {file_rel}"
        if not matches:
            return [], None  # empty match is not an error — callers decide meaning
        return matches, None
    else:
        resolved = _safe_resolve(file_rel, ctx.project_root)
        if resolved is None:
            return None, f"Path rejected (escapes project root or is absolute): {file_rel}"
        return [resolved] if resolved.exists() else [], None


def _run_grep(a: dict[str, Any], ctx: AssertionContext) -> dict[str, Any]:
    """Handler for 'grep' assertions."""
    pattern = a.get("pattern", "")
    file_rel = a.get("file", "")
    description = a.get("description", "") or f"grep: {pattern}"
    min_count = a.get("min_count", 1)

    if not pattern:
        return _fail("grep", description, "Missing 'pattern' field")
    if not file_rel:
        return _fail("grep", description, "Missing 'file' field")

    if "*" in file_rel:
        matches = _safe_glob(file_rel, ctx.project_root)
        if matches is None:
            return _fail("grep", description, f"Unsafe glob pattern rejected: {file_rel}")
        if not matches:
            return _fail("grep", description, f"No files matching glob: {file_rel}")
        total_count = 0
        for mf in matches:
            content = _read_file_safe(mf)
            if content:
                total_count += len(re.findall(pattern, content))
        passed = total_count >= min_count
        detail = f"Found {total_count} match(es) across {len(matches)} file(s), need >= {min_count}"
    else:
        resolved = _safe_resolve(file_rel, ctx.project_root)
        if resolved is None:
            return _fail("grep", description, f"Path rejected (escapes project root or is absolute): {file_rel}")
        content = _read_file_safe(resolved)
        if content is None:
            return _fail("grep", description, f"File not found: {file_rel}")
        count = len(re.findall(pattern, content))
        passed = count >= min_count
        detail = f"Found {count} match(es), need >= {min_count}"

    return {"type": "grep", "description": description, "passed": passed, "detail": detail}


def _run_glob(a: dict[str, Any], ctx: AssertionContext) -> dict[str, Any]:
    """Handler for 'glob' assertions."""
    pattern = a.get("pattern", "")
    description = a.get("description", "") or f"glob: {pattern}"
    contains = a.get("contains", "")

    if not pattern:
        return _fail("glob", description, "Missing 'pattern' field")

    matches = _safe_glob(pattern, ctx.project_root)
    if matches is None:
        return _fail("glob", description, f"Unsafe glob pattern rejected: {pattern}")

    if contains:
        matches = [m for m in matches if m.is_file() and contains in (_read_file_safe(m) or "")]
        count = len(matches)
        passed = count >= 1
        detail = f"Found {count} file(s) matching '{pattern}' containing '{contains}'"
    else:
        count = len(matches)
        passed = count >= 1
        detail = f"Found {count} file(s) matching '{pattern}'"

    return {"type": "glob", "description": description, "passed": passed, "detail": detail}


def _run_grep_absent(a: dict[str, Any], ctx: AssertionContext) -> dict[str, Any]:
    """Handler for 'grep_absent' assertions."""
    pattern = a.get("pattern", "")
    file_rel = a.get("file", "")
    description = a.get("description", "") or f"grep_absent: {pattern}"

    if not pattern:
        return _fail("grep_absent", description, "Missing 'pattern' field")
    if not file_rel:
        return _fail("grep_absent", description, "Missing 'file' field")

    if "*" in file_rel:
        matches = _safe_glob(file_rel, ctx.project_root)
        if matches is None:
            return _fail("grep_absent", description, f"Unsafe glob pattern rejected: {file_rel}")
        if not matches:
            return _pass("grep_absent", description, f"No files matching glob (pattern trivially absent): {file_rel}")
        total_count = 0
        for mf in matches:
            content = _read_file_safe(mf)
            if content:
                total_count += len(re.findall(pattern, content))
        passed = total_count == 0
        detail = f"Found {total_count} match(es) across {len(matches)} file(s), need 0"
    else:
        resolved = _safe_resolve(file_rel, ctx.project_root)
        if resolved is None:
            return _fail("grep_absent", description, f"Path rejected (escapes project root or is absolute): {file_rel}")
        content = _read_file_safe(resolved)
        if content is None:
            return _pass("grep_absent", description, f"File not found (pattern trivially absent): {file_rel}")
        count = len(re.findall(pattern, content))
        passed = count == 0
        detail = f"Found {count} match(es), need 0"

    return {"type": "grep_absent", "description": description, "passed": passed, "detail": detail}


def _run_file_exists(a: dict[str, Any], ctx: AssertionContext) -> dict[str, Any]:
    """Handler for 'file_exists' assertions."""
    file_rel = a.get("file", "")
    description = a.get("description", "") or f"file_exists: {file_rel}"

    if not file_rel:
        return _fail("file_exists", description, "Missing 'file' (or 'path') field")

    resolved = _safe_resolve(file_rel, ctx.project_root)
    if resolved is None:
        return _fail("file_exists", description, f"Path rejected (escapes project root or is absolute): {file_rel}")

    if resolved.exists() and resolved.is_file():
        return _pass("file_exists", description, f"File exists: {file_rel}")
    else:
        return _fail("file_exists", description, f"File not found: {file_rel}")


_COUNT_OPERATORS: dict[str, Callable[[int, int], bool]] = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


def _run_count(a: dict[str, Any], ctx: AssertionContext) -> dict[str, Any]:
    """Handler for 'count' assertions — grep with operator-based comparison."""
    pattern = a.get("pattern", "")
    file_rel = a.get("file", "")
    op_str = a.get("operator", ">=")
    expected = a.get("expected", 1)
    description = a.get("description", "") or f"count: {pattern} {op_str} {expected}"

    if not pattern:
        return _fail("count", description, "Missing 'pattern' field")
    if not file_rel:
        return _fail("count", description, "Missing 'file' field")
    if op_str not in _COUNT_OPERATORS:
        return _fail("count", description, f"Invalid operator: {op_str!r} (allowed: {', '.join(_COUNT_OPERATORS)})")
    if not isinstance(expected, int):
        return _fail("count", description, f"'expected' must be an integer, got {type(expected).__name__}")

    op_fn = _COUNT_OPERATORS[op_str]

    if "*" in file_rel:
        matches = _safe_glob(file_rel, ctx.project_root)
        if matches is None:
            return _fail("count", description, f"Unsafe glob pattern rejected: {file_rel}")
        if not matches:
            return _fail("count", description, f"No files matching glob: {file_rel}")
        total_count = 0
        for mf in matches:
            content = _read_file_safe(mf)
            if content:
                total_count += len(re.findall(pattern, content))
        passed = op_fn(total_count, expected)
        detail = f"Found {total_count} match(es) across {len(matches)} file(s), expected {op_str} {expected}"
    else:
        resolved = _safe_resolve(file_rel, ctx.project_root)
        if resolved is None:
            return _fail("count", description, f"Path rejected (escapes project root or is absolute): {file_rel}")
        content = _read_file_safe(resolved)
        if content is None:
            return _fail("count", description, f"File not found: {file_rel}")
        actual = len(re.findall(pattern, content))
        passed = op_fn(actual, expected)
        detail = f"Found {actual} match(es), expected {op_str} {expected}"

    return {"type": "count", "description": description, "passed": passed, "detail": detail}


def _walk_path(data: Any, path: str) -> tuple[Any, str | None]:
    """Walk a dotted path through nested dicts/lists.

    Returns (value, error). If error is not None, navigation failed.
    """
    parts = path.split(".")
    current = data
    for i, part in enumerate(parts):
        if isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                return None, f"Key {part!r} not found at path {'.'.join(parts[: i + 1])}"
        elif isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx]
            except (ValueError, IndexError):
                return None, f"Invalid array index {part!r} at path {'.'.join(parts[: i + 1])}"
        else:
            return None, f"Cannot navigate into {type(current).__name__} at path {'.'.join(parts[: i + 1])}"
    return current, None


def _run_json_path(a: dict[str, Any], ctx: AssertionContext) -> dict[str, Any]:
    """Handler for 'json_path' assertions — read JSON/TOML, walk path, compare."""
    file_rel = a.get("file", "")
    path_expr = a.get("path", "")
    expected = a.get("expected")
    description = a.get("description", "") or f"json_path: {file_rel}:{path_expr}"

    if not file_rel:
        return _fail("json_path", description, "Missing 'file' field")
    if not path_expr:
        return _fail("json_path", description, "Missing 'path' field")

    resolved = _safe_resolve(file_rel, ctx.project_root)
    if resolved is None:
        return _fail("json_path", description, f"Path rejected (escapes project root or is absolute): {file_rel}")

    content = _read_file_safe(resolved)
    if content is None:
        return _fail("json_path", description, f"File not found: {file_rel}")

    # Parse based on extension
    suffix = resolved.suffix.lower()
    try:
        if suffix == ".toml":
            import tomllib

            data = tomllib.loads(content)
        elif suffix in (".json", ".jsonl"):
            data = json.loads(content)
        else:
            # Try JSON first, then TOML
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                import tomllib

                data = tomllib.loads(content)
    except Exception as e:
        return _fail("json_path", description, f"Failed to parse {file_rel}: {e}")

    actual, err = _walk_path(data, path_expr)
    if err:
        return _fail("json_path", description, err)

    if expected is None:
        # No expected value — just check the path exists (value is not None)
        return _pass("json_path", description, f"Path '{path_expr}' exists, value: {actual!r}")

    # Compare values — try numeric comparison if both sides look numeric
    actual_str = str(actual)
    expected_str = str(expected)
    try:
        actual_num = float(actual_str)
        expected_num = float(expected_str)
        passed = actual_num == expected_num
    except (ValueError, TypeError):
        passed = actual_str == expected_str

    if passed:
        return _pass("json_path", description, f"Path '{path_expr}' = {actual!r} (expected {expected!r})")
    else:
        return _fail("json_path", description, f"Path '{path_expr}' = {actual!r}, expected {expected!r}")


# ---------------------------------------------------------------------------
# Phase 3: Composition operators
# ---------------------------------------------------------------------------


def _run_all_of(a: dict[str, Any], ctx: AssertionContext) -> dict[str, Any]:
    """Handler for 'all_of' — all child assertions must pass."""
    description = a.get("description", "") or "all_of"
    children = a.get("assertions", [])

    if ctx.depth >= ctx.max_depth:
        return _fail("all_of", description, f"Nesting depth {ctx.depth} exceeds max {ctx.max_depth}")
    if not children:
        return _fail("all_of", description, "Empty 'assertions' array")

    child_ctx = AssertionContext(project_root=ctx.project_root, depth=ctx.depth + 1, max_depth=ctx.max_depth)
    child_results = [_dispatch_single(c, child_ctx) for c in children]
    machine_results = [r for r in child_results if not r.get("skipped")]

    if not machine_results:
        return _skip("all_of", description, "All children are non-machine — skipped")

    all_passed = all(r["passed"] for r in machine_results)
    failed_count = sum(1 for r in machine_results if not r["passed"])
    detail = f"{len(machine_results)} machine assertion(s), {failed_count} failed"

    return {
        "type": "all_of",
        "description": description,
        "passed": all_passed,
        "detail": detail,
        "children": child_results,
    }


def _run_any_of(a: dict[str, Any], ctx: AssertionContext) -> dict[str, Any]:
    """Handler for 'any_of' — at least one child must pass.

    Skipped (non-machine) children do NOT satisfy any_of.
    """
    description = a.get("description", "") or "any_of"
    children = a.get("assertions", [])

    if ctx.depth >= ctx.max_depth:
        return _fail("any_of", description, f"Nesting depth {ctx.depth} exceeds max {ctx.max_depth}")
    if not children:
        return _fail("any_of", description, "Empty 'assertions' array")

    child_ctx = AssertionContext(project_root=ctx.project_root, depth=ctx.depth + 1, max_depth=ctx.max_depth)
    child_results = [_dispatch_single(c, child_ctx) for c in children]
    machine_results = [r for r in child_results if not r.get("skipped")]

    if not machine_results:
        return _skip("any_of", description, "All children are non-machine — skipped")

    any_passed = any(r["passed"] for r in machine_results)
    passed_count = sum(1 for r in machine_results if r["passed"])
    detail = f"{len(machine_results)} machine assertion(s), {passed_count} passed"

    return {
        "type": "any_of",
        "description": description,
        "passed": any_passed,
        "detail": detail,
        "children": child_results,
    }


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_RUNNERS: dict[str, Callable[[dict[str, Any], AssertionContext], dict[str, Any]]] = {
    "grep": _run_grep,
    "glob": _run_glob,
    "grep_absent": _run_grep_absent,
    "file_exists": _run_file_exists,
    "count": _run_count,
    "json_path": _run_json_path,
    "all_of": _run_all_of,
    "any_of": _run_any_of,
}


def _dispatch_single(assertion: Any, ctx: AssertionContext) -> dict[str, Any]:
    """Dispatch a single assertion (dict or plain text) through normalization and handlers."""
    if not isinstance(assertion, dict):
        return _skip("text", str(assertion)[:120], "Non-machine assertion (plain text) — skipped")

    a_type = assertion.get("type", "")
    normalized = _normalize_assertion(assertion)
    description = normalized.get("description", "") or f"{a_type}: {normalized.get('pattern', '')}"

    if a_type not in _VALID_ASSERTION_TYPES:
        return _skip(
            a_type,
            description,
            f"Skipped non-machine assertion type: {a_type!r} (only {sorted(_VALID_ASSERTION_TYPES)} are executable)",
        )

    runner = _RUNNERS.get(a_type)
    if runner is None:  # pragma: no cover — defensive
        return _fail(a_type, description, f"No handler registered for type: {a_type!r}")

    return runner(normalized, ctx)


# ---------------------------------------------------------------------------
# Public API (backward-compatible signatures)
# ---------------------------------------------------------------------------


def run_single_assertion(assertion: dict[str, Any], project_root: Path) -> dict[str, Any]:
    """Execute one assertion definition and return the result.

    This is the public entry point. Creates an AssertionContext and dispatches.

    Args:
        assertion: Assertion definition dict.
        project_root: Resolved project root for file resolution.

    Returns:
        dict with type, description, passed (bool), detail (str), and optionally skipped/children.
    """
    ctx = AssertionContext(project_root=project_root)
    return _dispatch_single(assertion, ctx)


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

    ctx = AssertionContext(project_root=project_root)
    results = [_dispatch_single(a, ctx) for a in assertions]

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
                # Show composition children
                if "children" in r:
                    for child in r["children"]:
                        c_status = "PASS" if child["passed"] else ("SKIP" if child.get("skipped") else "FAIL")
                        lines.append(f"      [{c_status}] {child['description']}: {child['detail']}")
            lines.append("")

    # Show passes briefly
    passes = [d for d in summary["details"] if not d.get("skipped") and d["overall_passed"]]
    if passes:
        lines.append("PASSED:\n")
        for p in passes:
            lines.append(f"  [{p['spec_id']}] {p['title']} ({p['assertion_count']} assertions)")
        lines.append("")

    return "\n".join(lines)
