# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPEC-1840: Quality Data Normalization.

Normalizes test result values across the Knowledge Database,
links testable elements to specifications, and reports untested specs.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)

# Canonical result values
_PASS_VARIANTS = {"pass", "passed", "PASS", "PASSED"}
_FAIL_VARIANTS = {"fail", "failed", "FAIL", "FAILED"}
_SKIP_VARIANTS = {"skip", "skipped", "SKIP", "SKIPPED", "stale", "STALE"}
_NOT_RUN_VARIANTS = {"not_run", "NOT_RUN", None}

# Canonical values
CANONICAL_PASS = "PASS"
CANONICAL_FAIL = "FAIL"
CANONICAL_SKIP = "SKIP"
CANONICAL_NOT_RUN = "NOT_RUN"


def normalize_test_result(value: str | None) -> str:
    """Normalize a test last_result to one of: PASS, FAIL, SKIP, NOT_RUN.

    Args:
        value: Raw result string from the KB (case-insensitive variants accepted).

    Returns:
        Canonical result string.

    Raises:
        ValueError: If the value doesn't match any known variant.
    """
    if value in _NOT_RUN_VARIANTS:
        return CANONICAL_NOT_RUN
    if isinstance(value, str):
        if value in _PASS_VARIANTS or value.lower() in {v.lower() for v in _PASS_VARIANTS if v}:
            return CANONICAL_PASS
        if value in _FAIL_VARIANTS or value.lower() in {v.lower() for v in _FAIL_VARIANTS if v}:
            return CANONICAL_FAIL
        if value in _SKIP_VARIANTS or value.lower() in {v.lower() for v in _SKIP_VARIANTS if v}:
            return CANONICAL_SKIP
    raise ValueError(f"Unknown test result value: {value!r}")


def normalize_all_kb_results(db_path: str = "tools/knowledge-db/knowledge.db") -> dict[str, int]:
    """Migrate all last_result values in the KB to canonical form.

    Returns a summary of how many values were normalized per canonical type.
    """
    sys.path.insert(0, "tools/knowledge-db")
    from db import KnowledgeDB

    kdb = KnowledgeDB(db_path)
    tests = kdb.list_tests()
    counts: dict[str, int] = {"PASS": 0, "FAIL": 0, "SKIP": 0, "NOT_RUN": 0, "errors": 0}

    for test in tests:
        raw = test.get("last_result")
        try:
            canonical = normalize_test_result(raw)
        except ValueError:
            counts["errors"] += 1
            logger.warning("Cannot normalize test %s result: %r", test["id"], raw)
            continue

        if raw != canonical:
            # Update the test record with normalized value
            kdb.update_test_result(test["id"], canonical)
            logger.info("Normalized %s: %r -> %s", test["id"], raw, canonical)

        counts[canonical] += 1

    return counts


def auto_link_testable_elements(db_path: str = "tools/knowledge-db/knowledge.db") -> dict[str, Any]:
    """Auto-link testable elements to specifications by pattern matching.

    Scans testable elements without a spec_id and attempts to link them
    based on naming conventions and test references.

    Returns:
        Dict with 'linked', 'unlinked', and 'total' counts.
    """
    sys.path.insert(0, "tools/knowledge-db")
    from db import KnowledgeDB

    kdb = KnowledgeDB(db_path)
    elements = kdb.list_testable_elements()

    linked = 0
    unlinked = 0
    total = len(elements)

    for elem in elements:
        if elem.get("spec_id"):
            linked += 1
            continue

        # Try to infer spec_id from the element's test references or name
        spec_id = _infer_spec_id(elem, kdb)
        if spec_id:
            kdb.link_testable_element(elem["id"], spec_id)
            linked += 1
        else:
            unlinked += 1

    return {"linked": linked, "unlinked": unlinked, "total": total}


def _infer_spec_id(element: dict[str, Any], kdb: Any) -> str | None:
    """Attempt to infer a spec_id for a testable element.

    Looks at associated tests and their spec_id references.
    """
    # If the element has associated tests, use their spec_id
    tests = kdb.get_tests_for_element(element["id"]) if hasattr(kdb, "get_tests_for_element") else []
    for test in tests:
        if test.get("spec_id"):
            return test["spec_id"]
    return None
