# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Add two hygiene work items to MemBase per S344 owner directive.

Owner directed via "Both please" in S344 (2026-05-11) to file:
- GTKB-AUTO-PUSH-INVESTIGATION-001
- GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001

Run: python scripts/_record_wi_s344_strategic_improvement.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB
from scripts._kb_attribution import resolve_changed_by


def main() -> int:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    changed_by = resolve_changed_by()

    item1 = db.insert_work_item(
        id="GTKB-AUTO-PUSH-INVESTIGATION-001",
        title="Investigate background auto-push of local commits to origin/develop",
        origin="hygiene",
        component="bridge-automation",
        resolution_status="open",
        changed_by=changed_by,
        change_reason=(
            "S344 strategic-self-improvement capture: between local commit 5611dc44 "
            "and a subsequent local soft-reset, the commit appeared on origin/develop. "
            "Neither the local .githooks/* nor .git/hooks/* explains the push. "
            "Source process is unidentified; reversibility claims in turn outputs "
            "are currently inaccurate. Owner directed filing during S344 wrap-up."
        ),
        description=(
            "OBSERVED (S344, 2026-05-11): commit 5611dc44 was pushed to "
            "origin/develop between local commit creation and subsequent "
            "reset --soft. Neither pre-commit, post-commit, pre-push, nor "
            "post-merge hook in .githooks/ or .git/hooks/ contains git push "
            "logic. The push must originate from outside git's hook surface "
            "(Codex session, scheduled task, cross-harness trigger spawn, "
            "or other background automation).\n\n"
            "INVESTIGATION SCOPE:\n"
            "1. Identify the process that performs the push.\n"
            "2. Determine whether the push is owner-intended or incidental.\n"
            "3. If owner-intended, document the behavior in bridge-essential.md "
            "or operating-model.md so Prime/LO turn outputs can accurately "
            "describe reversibility.\n"
            "4. If incidental, propose disposition (suppress, gate, or "
            "governance addition).\n\n"
            "RELEVANT GOVERNANCE: GOV-RELEASE-* family (push semantics); "
            "AUQ-only enforcement stack (if push is a destructive remote "
            "operation, should it gate through AUQ?); bridge-essential.md "
            "operational mode."
        ),
        priority="medium",
        stage="backlogged",
        status_detail=(
            "S344 capture; investigation not yet started. Identified via scope-bundling incident on commit 5611dc44."
        ),
        source_owner_directive=(
            "S344 owner directive: 'Both please' authorizing strategic-self-"
            "improvement filing of two observations from DELIB-S344 commit cycle."
        ),
        related_deliberation_ids="DELIB-S344-SPEC-EXPRESSIONS-TRIANGULATION-001",
        acceptance_summary=(
            "Auto-push source identified and documented; either (a) push is "
            "owner-authorized and operating-model/bridge-essential is updated "
            "to describe it accurately, or (b) push is unauthorized and "
            "disposition proposal filed via bridge protocol."
        ),
    )
    print(f"WI 1: id={item1['id']} v={item1['version']} status={item1['resolution_status']}", flush=True)

    item2 = db.insert_work_item(
        id="GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001",
        title="Pre-commit predicate to detect cross-scope bundling via mismatched approval packets",
        origin="hygiene",
        component="governance",
        resolution_status="open",
        changed_by=changed_by,
        change_reason=(
            "S344 strategic-self-improvement capture: during DELIB-S344 commit "
            "cycle, a record-script commit accidentally bundled an S343 "
            "work_list.md entry because both paths had valid approval packets "
            "in .groundtruth/formal-artifact-approvals/, and no gate detected "
            "the cross-scope union. Commit 5611dc44 carries two unrelated "
            "scopes under one commit message. Owner directed filing during "
            "S344 wrap-up."
        ),
        description=(
            "OBSERVED (S344, 2026-05-11): commit 5611dc44 bundled "
            "scripts/archive/record_delib_s344_spec_expressions_triangulation.py "
            "(DELIB-S344 scope) with a 30-line addition to memory/work_list.md "
            "(S343 bridge-protocol-guide entry scope). Both paths had valid "
            "approval packets in .groundtruth/formal-artifact-approvals/. The "
            "pre-commit check_narrative_artifact_evidence.py passed cleanly "
            "because each staged path matched its own packet -- there is no "
            "predicate that checks whether the *union* of staged packets "
            "represents a single coherent scope.\n\n"
            "PROPOSED PREDICATE: Add a pre-commit check that emits a warning "
            "(or block, owner-configurable) when staged file set spans paths "
            "whose matching approval packets reference distinct deliberation "
            "IDs, specification IDs, or bridge thread slugs. Author can "
            "override with an explicit --allow-multi-scope flag or by "
            "squashing into a single broader-scope commit with appropriate "
            "change_reason.\n\n"
            "RELATED: GTKB-BRIDGE-PROTOCOL-GUIDE-AMEND-CONCURRENT-COMMIT-ENTRY "
            "(memory/work_list.md row added S344-via-S343-bundle, same "
            "hygiene neighborhood: commit-discipline hardening). Both items "
            "address failure modes where multiple legitimate scopes "
            "accidentally collapse into one commit without authorial intent."
        ),
        priority="medium",
        stage="backlogged",
        status_detail=(
            "S344 capture; observed empirically in commit 5611dc44. Sibling "
            "to the S343 amend-with-concurrent-commit backlog entry."
        ),
        source_owner_directive=(
            "S344 owner directive: 'Both please' authorizing strategic-self-"
            "improvement filing of two observations from DELIB-S344 commit cycle."
        ),
        related_deliberation_ids="DELIB-S344-SPEC-EXPRESSIONS-TRIANGULATION-001",
        acceptance_summary=(
            "Pre-commit predicate landed in .githooks/ (or invoked from "
            ".githooks/pre-commit via a scripts/check_*.py entry) that "
            "detects multi-scope packet matches in the staged set and emits "
            "warning/block with an opt-in --allow-multi-scope override; "
            "regression test confirms detection on a fixture multi-packet "
            "staged set."
        ),
    )
    print(f"WI 2: id={item2['id']} v={item2['version']} status={item2['resolution_status']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
