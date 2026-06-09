"""Tests for the idempotent ``_project_id_from_names`` defect fix.

Authority: bridge/gtkb-project-id-prefix-idempotent-fix-002.md (REVISED-1),
Codex GO at bridge/gtkb-project-id-prefix-idempotent-fix-003.md.

Source work items: WI-3411 (CLI symptom; member of PROJECT-GTKB-RELIABILITY-FIXES)
and WI-3355 (root-cause diagnosis; orphan).

Covers the 6-test Specification-Derived Verification Plan from the GO'd
proposal:

* T1 ``test_bare_name_prefixed`` — bare name unchanged.
* T2 ``test_qualified_id_not_doubled`` — already-qualified id not doubled.
* T3 ``test_subproject_bare`` — subproject with bare project name.
* T4 ``test_subproject_qualified_not_doubled`` — subproject with qualified
  project id.
* T5 ``test_idempotent`` — ``f(f(x)) == f(x)`` for representative inputs.
* T6 ``test_insert_work_item_no_doubled_membership`` — integration: after
  ``insert_work_item(project_name="PROJECT-GTKB-RELIABILITY-FIXES")`` the
  backfill files membership under ``PROJECT-GTKB-RELIABILITY-FIXES`` and
  NOT under the doubled-prefix ``PROJECT-PROJECT-GTKB-RELIABILITY-FIXES``.

T6 exercises the same code path that originally produced the doubled-prefix
membership rows for WI-3411 and WI-3447: ``insert_work_item`` records the
``work_items.project_name`` compatibility field, and the next call to
``_backfill_project_artifacts_from_work_items`` derives the project id via
``_project_id_from_names``. The test runs the backfill explicitly to keep
the assertion deterministic and process-restart-independent.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB, _project_id_from_names  # noqa: E402


def test_bare_name_prefixed() -> None:
    assert _project_id_from_names("GTKB-X") == "PROJECT-GTKB-X"


def test_qualified_id_not_doubled() -> None:
    assert _project_id_from_names("PROJECT-GTKB-X") == "PROJECT-GTKB-X"


def test_subproject_bare() -> None:
    assert _project_id_from_names("GTKB-X", "SUB") == "PROJECT-GTKB-X-SUB"


def test_subproject_qualified_not_doubled() -> None:
    assert _project_id_from_names("PROJECT-GTKB-X", "SUB") == "PROJECT-GTKB-X-SUB"


def test_idempotent() -> None:
    for bare in ("GTKB-X", "PROJECT-GTKB-X", "GTKB-Y-Z", "PROJECT-GTKB-Y-Z"):
        once = _project_id_from_names(bare)
        twice = _project_id_from_names(once)
        assert once == twice, f"non-idempotent for input {bare!r}: once={once!r}, twice={twice!r}"


def test_insert_work_item_no_doubled_membership(tmp_path: Path) -> None:
    db_path = tmp_path / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    try:
        db.insert_work_item(
            id="WI-9999",
            title="Test doubled-prefix membership integration path",
            origin="defect",
            component="backlog",
            resolution_status="open",
            changed_by="test-project-id-from-names-idempotent",
            change_reason=(
                "integration test for _project_id_from_names idempotent fix "
                "(bridge/gtkb-project-id-prefix-idempotent-fix-002.md)"
            ),
            project_name="PROJECT-GTKB-RELIABILITY-FIXES",
        )
        # Re-run the backfill explicitly. In production, the doubled-prefix
        # membership is created when a SUBSEQUENT KnowledgeDB() init runs the
        # backfill against the now-present work_items row; calling it here
        # reproduces that manifest path deterministically.
        db._backfill_project_artifacts_from_work_items()
    finally:
        db.close()

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT project_id, work_item_id, source FROM current_project_work_item_memberships WHERE work_item_id = ?",
            ("WI-9999",),
        ).fetchall()

    project_ids = {row["project_id"] for row in rows}
    assert "PROJECT-GTKB-RELIABILITY-FIXES" in project_ids, (
        f"expected canonical membership PROJECT-GTKB-RELIABILITY-FIXES; got project_ids={project_ids!r}"
    )
    assert "PROJECT-PROJECT-GTKB-RELIABILITY-FIXES" not in project_ids, (
        f"doubled-prefix membership present after fix; project_ids={project_ids!r}"
    )
