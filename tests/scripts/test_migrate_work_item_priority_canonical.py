"""Regression tests for scripts/migrate_work_item_priority_canonical.py.

Per gtkb-work-item-priority-canonical-p0p3-migration-005 IP-3 + the
verification plan, this test file covers:

1. test_canonical_mapping_completeness - table-driven test covering all
   known values (and case variants) plus a control unknown asserting
   UnknownPriorityValueError.
2. test_migration_idempotent - run migration twice; second run reports
   zero migrations.
3. test_post_migration_priority_invariant - assert all resolution_status='open'
   work_items priorities are in {P0, P1, P2, P3, None} post-migration.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "migrate_work_item_priority_canonical.py"
_KB_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_KB_SRC) not in sys.path:
    sys.path.insert(0, str(_KB_SRC))


@pytest.fixture(scope="module")
def migrate_module():
    """Import the migration script as a module."""
    spec = importlib.util.spec_from_file_location("migrate_work_item_priority_canonical", _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["migrate_work_item_priority_canonical"] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# IP-3 test 1: canonical mapping completeness
# ---------------------------------------------------------------------------


def test_canonical_mapping_completeness(migrate_module):
    """All known values map; control unknown raises."""
    cases = [
        # identity
        ("P0", "P0"),
        ("P1", "P1"),
        ("P2", "P2"),
        ("P3", "P3"),
        # lowercase legacy
        ("low", "P3"),
        ("medium", "P2"),
        ("high", "P1"),
        # uppercase legacy
        ("LOW", "P3"),
        ("MEDIUM", "P2"),
        ("HIGH", "P1"),
        # mixed case legacy
        ("High", "P1"),
        ("Medium", "P2"),
        ("Low", "P3"),
        # null preservation
        (None, None),
        ("", None),
        ("   ", None),
    ]
    for input_value, expected in cases:
        result = migrate_module._canonical_mapping(input_value)
        assert result == expected, f"input={input_value!r} expected={expected!r} got={result!r}"

    # Control: unknown value raises
    with pytest.raises(migrate_module.UnknownPriorityValueError):
        migrate_module._canonical_mapping("URGENT")
    with pytest.raises(migrate_module.UnknownPriorityValueError):
        migrate_module._canonical_mapping("p4")
    with pytest.raises(migrate_module.UnknownPriorityValueError):
        migrate_module._canonical_mapping(42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# IP-3 test 2: migration idempotency (synthetic in-memory DB)
# ---------------------------------------------------------------------------


def _build_synthetic_db(tmp_path: Path) -> Path:
    """Build a fresh KnowledgeDB at tmp_path with seeded work items.

    Returns the path to the new DB.
    """
    from groundtruth_kb.db import KnowledgeDB

    db_path = tmp_path / "synthetic.db"
    db = KnowledgeDB(db_path)
    # Seed three legacy-priority WIs + one already-canonical + one null.
    db.insert_work_item(
        id="WI-TEST-LOW-001",
        title="Test low priority WI",
        origin="defect",
        component="test_infrastructure",
        resolution_status="open",
        changed_by="test-harness",
        change_reason="seed legacy low",
        priority="low",
    )
    db.insert_work_item(
        id="WI-TEST-HIGH-002",
        title="Test high priority WI",
        origin="defect",
        component="test_infrastructure",
        resolution_status="open",
        changed_by="test-harness",
        change_reason="seed legacy HIGH",
        priority="HIGH",
    )
    db.insert_work_item(
        id="WI-TEST-MEDIUM-003",
        title="Test medium priority WI",
        origin="hygiene",
        component="test_infrastructure",
        resolution_status="open",
        changed_by="test-harness",
        change_reason="seed legacy Medium",
        priority="Medium",
    )
    db.insert_work_item(
        id="WI-TEST-CANONICAL-004",
        title="Test already-canonical priority",
        origin="new",
        component="test_infrastructure",
        resolution_status="open",
        changed_by="test-harness",
        change_reason="seed canonical P2",
        priority="P2",
    )
    db.insert_work_item(
        id="WI-TEST-NULL-005",
        title="Test null priority WI",
        origin="new",
        component="test_infrastructure",
        resolution_status="open",
        changed_by="test-harness",
        change_reason="seed null priority",
        priority=None,
    )
    return db_path


def test_migration_idempotent(migrate_module, tmp_path):
    """First run migrates; second run finds zero targets."""
    from groundtruth_kb.db import KnowledgeDB

    db_path = _build_synthetic_db(tmp_path)
    db = KnowledgeDB(db_path)

    # First-pass: collect targets
    targets = migrate_module.collect_targets(db)
    assert len(targets) == 3  # low, HIGH, Medium

    # Apply
    result = migrate_module.apply_migration(db, targets, changed_by="prime-builder/test/B")
    assert result["migrated_count"] == 3

    # Second-pass: zero targets
    re_targets = migrate_module.collect_targets(db)
    assert len(re_targets) == 0, f"second pass should find no targets; got {[t['row']['id'] for t in re_targets]}"


# ---------------------------------------------------------------------------
# IP-3 test 3: post-migration priority invariant
# ---------------------------------------------------------------------------


def test_post_migration_priority_invariant(migrate_module, tmp_path):
    """All open WIs have priority in {P0, P1, P2, P3, None} post-migration."""
    from groundtruth_kb.db import KnowledgeDB

    db_path = _build_synthetic_db(tmp_path)
    db = KnowledgeDB(db_path)

    targets = migrate_module.collect_targets(db)
    migrate_module.apply_migration(db, targets, changed_by="prime-builder/test/B")

    invariant = migrate_module.post_migration_invariant_holds(db)
    assert invariant["invariant_holds"], (
        f"invariant did not hold; remaining: {invariant['noncanonical_nonnull_remaining']}"
    )
    # null is preserved (the test-null-005 WI)
    assert invariant["counts"].get("None", 0) >= 1
    # post-migration distribution only canonical + null
    for key in invariant["counts"]:
        if key == "None":
            continue
        assert key in {"P0", "P1", "P2", "P3"}, f"unexpected post-migration priority {key!r}"
