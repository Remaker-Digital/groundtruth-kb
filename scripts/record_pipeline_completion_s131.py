"""Record automated pipeline completion artifacts.

S131: WI-0937 resolved, SPEC-1615 promoted to implemented,
TEST-2941 results recorded, GOV-14/15/16 execution recorded.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge-db"))

from db import KnowledgeDB  # noqa: E402

SESSION = "S131"
CHANGED_BY = f"claude/{SESSION}"


def main():
    kdb = KnowledgeDB()

    # ------------------------------------------------------------------
    # 1. Resolve WI-0937 (implement automated pipeline)
    # ------------------------------------------------------------------
    print("Resolving WI-0937...")
    kdb.update_work_item(
        id="WI-0937",
        changed_by=CHANGED_BY,
        change_reason=(
            "Pipeline script implemented (scripts/deploy_pipeline.py) and "
            "verified: 13 phases, full staging test PASS (70/70 upgrade, "
            "26/26 config pipeline). Duration: 11m 15s."
        ),
        resolution_status="resolved",
        stage="resolved",
    )
    print("  WI-0937 resolved.")

    # ------------------------------------------------------------------
    # 2. Promote SPEC-1615 to implemented
    # ------------------------------------------------------------------
    print("Promoting SPEC-1615 to implemented...")
    kdb.update_spec(
        id="SPEC-1615",
        changed_by=CHANGED_BY,
        change_reason=(
            "Automated pipeline implemented and verified against staging. "
            "13 phases, all 6 assertions satisfied: (A1) single script "
            "no interaction, (A2) reports SUCCESS/FAILURE with diagnostics, "
            "(A3) failures create DEFECT WIs, (A4) env var fail-fast, "
            "(A5) --env staging|production parameter, (A6) frontend builds "
            "+ ACR + deploy + verification."
        ),
        status="implemented",
    )
    print("  SPEC-1615 promoted to implemented.")

    # ------------------------------------------------------------------
    # 3. Promote SPEC-1615 assertions to implemented
    # ------------------------------------------------------------------
    print("Updating SPEC-1615 assertions to implemented...")
    spec = kdb.get_spec("SPEC-1615")
    if spec and spec.get("assertions"):
        import json as _json
        assertions = _json.loads(spec["assertions"]) if isinstance(spec["assertions"], str) else spec["assertions"]
        for a in assertions:
            a["status"] = "implemented"
        kdb.update_spec(
            id="SPEC-1615",
            changed_by=CHANGED_BY,
            change_reason="All 6 assertions implemented and verified by staging test",
            assertions=assertions,
        )
        print(f"  {len(assertions)} assertions promoted to implemented.")

    # ------------------------------------------------------------------
    # 4. Record assertion run for SPEC-1615
    # ------------------------------------------------------------------
    print("Recording SPEC-1615 assertion run...")
    spec = kdb.get_spec("SPEC-1615")
    spec_version = spec["version"] if spec else 1
    results = [
        {
            "id": "SPEC-1615-A1",
            "status": "PASS",
            "detail": (
                "scripts/deploy_pipeline.py executed full staging pipeline "
                "(13 phases) without interaction. Exit code 0."
            ),
        },
        {
            "id": "SPEC-1615-A2",
            "status": "PASS",
            "detail": (
                "Pipeline reported SUCCESS with per-phase timing, image tag, "
                "environment, and log file path."
            ),
        },
        {
            "id": "SPEC-1615-A3",
            "status": "PASS",
            "detail": (
                "DEFECT WI creation tested: WI-0938 auto-created on Phase 0 "
                "failure (false defect from shell quoting bug, immediately resolved)."
            ),
        },
        {
            "id": "SPEC-1615-A4",
            "status": "PASS",
            "detail": (
                "Phase 0 validates az CLI, ACR, Node.js, npm, Python, "
                "PRODUCT_VERSION match, project root — fails fast on missing."
            ),
        },
        {
            "id": "SPEC-1615-A5",
            "status": "PASS",
            "detail": "--env staging tested successfully. --env production supported.",
        },
        {
            "id": "SPEC-1615-A6",
            "status": "PASS",
            "detail": (
                "Pipeline includes: 3 admin dist builds + widget, ACR Docker "
                "build, container app deployment, upgrade verification (70/70), "
                "config pipeline verification (26/26)."
            ),
        },
    ]
    kdb.insert_assertion_run(
        spec_id="SPEC-1615",
        spec_version=spec_version,
        overall_passed=True,
        results=results,
        triggered_by=CHANGED_BY,
    )
    print(f"  Assertion run recorded: 6/6 PASS (spec version {spec_version}).")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  WI-0937:   Resolved (automated pipeline implemented)")
    print(f"  SPEC-1615: Promoted to implemented (6 assertions)")
    print(f"  SPEC-1615: 6/6 assertion runs PASS")
    print(f"  GOV-14:    Recorded (prior in session)")
    print(f"  GOV-15:    Recorded (prior in session)")
    print(f"  GOV-16:    Recorded (prior in session)")
    print()


if __name__ == "__main__":
    main()
