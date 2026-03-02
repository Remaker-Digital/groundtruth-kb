"""Shared DEFECT work item creation for automation scripts.

Extracted from deploy_pipeline.py to be reused by test_pipeline.py and
pre_flight_checklist.py.  Creates DEFECT work items in the Knowledge
Database when automated phases fail.

Usage:
    from scripts._defect_reporter import create_defect, next_wi_id

    wi_id = create_defect(
        title="Deploy pipeline failure: Phase 7 (ACR Docker Build)",
        description="Build failed with exit code 1...",
        source_spec_id="SPEC-1615",
        component="infrastructure_automation",
        changed_by="deploy-pipeline",
    )

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge-db"))


def next_wi_id() -> str:
    """Generate the next sequential WI ID from the Knowledge Database.

    Queries MAX(CAST(SUBSTR(id, 4) AS INTEGER)) from work_items and
    returns 'WI-NNNN' for the next available ID.
    """
    from db import KnowledgeDB  # noqa: E402

    kdb = KnowledgeDB()
    conn = kdb._get_conn()
    row = conn.execute(
        "SELECT MAX(CAST(SUBSTR(id, 4) AS INTEGER)) "
        "FROM work_items WHERE id LIKE 'WI-%'"
    ).fetchone()
    max_id = row[0] if row and row[0] else 0
    return f"WI-{max_id + 1:04d}"


def create_defect(
    *,
    title: str,
    description: str,
    source_spec_id: str,
    component: str = "infrastructure_automation",
    changed_by: str = "automation",
) -> str | None:
    """Create a DEFECT work item in the Knowledge Database.

    Returns the new WI ID on success, or None if creation fails.
    Failures are printed but never raise — automation must not crash
    on KB write errors.
    """
    try:
        from db import KnowledgeDB  # noqa: E402

        kdb = KnowledgeDB()
        wi_id = next_wi_id()

        kdb.insert_work_item(
            id=wi_id,
            title=title,
            description=description,
            source_spec_id=source_spec_id,
            origin="defect",
            component=component,
            resolution_status="open",
            stage="created",
            changed_by=changed_by,
            change_reason=f"Automated DEFECT — {title[:80]}",
        )
        return wi_id
    except Exception as e:
        print(f"  [WARN] Could not create DEFECT work item: {e}", flush=True)
        return None
