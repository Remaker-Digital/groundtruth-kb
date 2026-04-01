"""
GroundTruth KB — Assertion Schema Validation.

Validates assertion definitions at write time (insert/update/import) to catch
malformed assertions before they enter the database.

Machine types are validated for required fields, allowed operators, path safety,
and composition constraints. Non-machine types pass without validation (they are
human notes and will be skipped at execution time).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from typing import Any

from groundtruth_kb.assertions import (
    _COUNT_OPERATORS,
    _MAX_COMPOSITION_DEPTH,
    _VALID_ASSERTION_TYPES,
    _has_parent_traversal,
    _is_absolute,
)

# Fields that satisfy the "file" requirement for each type (aliases accepted at rest)
_FILE_FIELD_NAMES = {"file", "file_pattern", "target", "path", "expected"}
_PATTERN_FIELD_NAMES = {"pattern", "query"}


def _has_file_field(assertion: dict[str, Any]) -> bool:
    """Check if the assertion has any recognized file field."""
    return any(assertion.get(f) for f in _FILE_FIELD_NAMES)


def _has_pattern_field(assertion: dict[str, Any]) -> bool:
    """Check if the assertion has any recognized pattern field."""
    return any(assertion.get(f) for f in _PATTERN_FIELD_NAMES)


def _get_file_values(assertion: dict[str, Any]) -> list[str]:
    """Get all non-empty file field values for path safety checks."""
    return [str(assertion[f]) for f in _FILE_FIELD_NAMES if assertion.get(f)]


def _get_pattern_values(assertion: dict[str, Any]) -> list[str]:
    """Get all non-empty pattern field values."""
    return [str(assertion[f]) for f in _PATTERN_FIELD_NAMES if assertion.get(f)]


def validate_assertion(assertion: Any, depth: int = 0) -> list[str]:
    """Validate a single assertion definition.

    Returns a list of error strings. Empty list means the assertion is valid.
    Non-machine types (not in _VALID_ASSERTION_TYPES) pass without validation.
    """
    errors: list[str] = []

    if not isinstance(assertion, dict):
        # Plain text assertions are human notes — valid
        return errors

    a_type = assertion.get("type", "")

    # Non-machine types are valid (they'll be skipped at execution time)
    if a_type not in _VALID_ASSERTION_TYPES:
        return errors

    # --- Type-specific validation ---

    if a_type in ("grep", "grep_absent"):
        if not _has_pattern_field(assertion):
            errors.append(f"{a_type}: missing 'pattern' (or 'query') field")
        if not _has_file_field(assertion):
            errors.append(f"{a_type}: missing 'file' (or alias) field")

    elif a_type == "glob":
        if not _has_pattern_field(assertion):
            errors.append("glob: missing 'pattern' field")

    elif a_type == "file_exists":
        if not _has_file_field(assertion):
            errors.append("file_exists: missing 'file' (or 'path') field")

    elif a_type == "count":
        if not _has_pattern_field(assertion):
            errors.append("count: missing 'pattern' field")
        if not _has_file_field(assertion):
            errors.append("count: missing 'file' field")
        op = assertion.get("operator", ">=")
        if op not in _COUNT_OPERATORS:
            errors.append(f"count: invalid operator {op!r} (allowed: {', '.join(sorted(_COUNT_OPERATORS))})")
        expected = assertion.get("expected")
        if expected is not None and not isinstance(expected, int):
            errors.append(f"count: 'expected' must be an integer, got {type(expected).__name__}")

    elif a_type == "json_path":
        if not _has_file_field(assertion):
            errors.append("json_path: missing 'file' field")
        if not assertion.get("path"):
            errors.append("json_path: missing 'path' field")

    elif a_type in ("all_of", "any_of"):
        if depth >= _MAX_COMPOSITION_DEPTH:
            errors.append(f"{a_type}: nesting depth {depth} exceeds max {_MAX_COMPOSITION_DEPTH}")
        children = assertion.get("assertions")
        if not isinstance(children, list) or len(children) == 0:
            errors.append(f"{a_type}: 'assertions' must be a non-empty list")
        else:
            for i, child in enumerate(children):
                child_errors = validate_assertion(child, depth=depth + 1)
                for e in child_errors:
                    errors.append(f"{a_type}.assertions[{i}]: {e}")

    # --- Path safety checks (all types with file fields) ---
    for fv in _get_file_values(assertion):
        if _is_absolute(fv):
            errors.append(f"path safety: absolute path not allowed: {fv!r}")
        if _has_parent_traversal(fv):
            errors.append(f"path safety: parent traversal (..) not allowed: {fv!r}")

    # Check glob patterns in pattern field too
    if a_type == "glob":
        for pv in _get_pattern_values(assertion):
            if _is_absolute(pv):
                errors.append(f"path safety: absolute glob pattern not allowed: {pv!r}")
            if _has_parent_traversal(pv):
                errors.append(f"path safety: parent traversal in glob pattern not allowed: {pv!r}")

    return errors


def validate_assertion_list(assertions: Any) -> list[str]:
    """Validate a list of assertion definitions.

    Returns a list of error strings. Empty list means all assertions are valid.
    Accepts None or non-list gracefully (returns empty — no assertions to validate).
    """
    if assertions is None:
        return []
    if not isinstance(assertions, list):
        return [f"assertions must be a list, got {type(assertions).__name__}"]

    all_errors: list[str] = []
    for i, assertion in enumerate(assertions):
        errors = validate_assertion(assertion)
        for e in errors:
            all_errors.append(f"assertions[{i}]: {e}")
    return all_errors
