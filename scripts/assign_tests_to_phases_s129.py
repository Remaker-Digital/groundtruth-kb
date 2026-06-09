#!/usr/bin/env python3
"""S129: Assign all orphan Test artifacts to PLAN-001 phases.

Implements SPEC-1603/1604: every Test must be in at least one plan phase.
After running, the union of all phase test_ids equals the full set of
Test artifact IDs — zero orphans.

Strategy:
- Categorize each orphan test by its spec_id, test_type, and test_file
- Assign to the most appropriate existing phase
- Update phases via db.update_test_plan_phase() (append-only versioning)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))
import db as kb

SESSION = "S129"
CHANGED_BY = f"claude/{SESSION}"
CHANGE_REASON = "SPEC-1603/1604: assign orphan tests to plan phases — zero orphan target"


def classify_test(test: dict) -> str:
    """Determine which PLAN-001 phase a test belongs to.

    Returns the phase ID (PHASE-001 through PHASE-016).
    """
    spec_id = test.get("spec_id") or ""
    test_type = test.get("test_type") or ""
    test_file = test.get("test_file") or ""
    title = test.get("title") or ""
    test_id = test.get("id") or ""

    # ── Visual regression baselines → Phase 16 ──
    if spec_id.startswith("VR-"):
        return "PHASE-016"

    # ── Governance process rules → Phase 15 (Manual Verification) ──
    if spec_id.startswith("GOV-"):
        return "PHASE-015"

    # ── Test procedure completeness specs → Phase 1 (Pre-flight) ──
    if spec_id in ("SPEC-1603", "SPEC-1604", "SPEC-1605"):
        return "PHASE-001"

    # ── Shopify app config → Phase 1 (Pre-flight) ──
    if spec_id == "SPEC-1567":
        return "PHASE-001"

    # ── Scale target / transport centrality → Phase 1 (Pre-flight) ──
    if spec_id in ("SPEC-1516", "SPEC-1517"):
        return "PHASE-001"

    # ── Dashboard billable-only filtering → Phase 2 (Unit & Integration) ──
    if "SPEC-1593" <= spec_id <= "SPEC-1600":
        return "PHASE-002"

    # ── Co-Pilot design decisions → Phase 2 (Unit & Integration) ──
    if "SPEC-1563" <= spec_id <= "SPEC-1566":
        return "PHASE-002"

    # ── AGNTCY SDK / containerized deployment / transport → Phase 2 ──
    if "SPEC-1534" <= spec_id <= "SPEC-1546":
        return "PHASE-002"

    # ── Fine-tuning pipeline (SPEC-1519..1523) ──
    if "SPEC-1519" <= spec_id <= "SPEC-1523":
        if test_type == "e2e":
            return "PHASE-003"  # Production Regression
        return "PHASE-002"  # Unit & Integration

    # ── SLIM/A2A transport (SPEC-1524..1525) ──
    if spec_id in ("SPEC-1524", "SPEC-1525"):
        return "PHASE-002"

    # ── Load test / KEDA / baseline performance (SPEC-1527..1529) ──
    if spec_id in ("SPEC-1527", "SPEC-1528", "SPEC-1529"):
        return "PHASE-010"  # Load Testing

    # ── Conversation tracing (SPEC-1530..1533) ──
    if "SPEC-1530" <= spec_id <= "SPEC-1533":
        if test_type == "e2e":
            return "PHASE-003"
        return "PHASE-002"

    # ── Secret posture (SPEC-1568..1582) ──
    if "SPEC-1568" <= spec_id <= "SPEC-1582":
        if "security" in test_file:
            return "PHASE-006"  # API Security
        return "PHASE-002"

    # ── Pipeline observatory (SPEC-1583..1587) ──
    if "SPEC-1583" <= spec_id <= "SPEC-1587":
        return "PHASE-002"

    # ── Contact Us persistence (SPEC-1588..1592) ──
    if "SPEC-1588" <= spec_id <= "SPEC-1592":
        if test_type == "e2e":
            return "PHASE-003"
        return "PHASE-002"

    # ── Co-Pilot knowledge (SPEC-1547..1556) ──
    if "SPEC-1547" <= spec_id <= "SPEC-1556":
        return "PHASE-002"

    # ── Live E2E tests → Phase 3 (Production Regression) ──
    if test_type == "e2e" or "e2e" in test_file:
        return "PHASE-003"

    # ── Security tests → Phase 6 ──
    if test_type == "security" or "security" in test_file:
        return "PHASE-006"

    # ── Performance tests → Phase 10 ──
    if test_type == "performance":
        return "PHASE-010"

    # ── Manual tests → Phase 15 ──
    if test_type == "manual":
        return "PHASE-015"

    # ── Default: Phase 2 (Unit & Integration) ──
    return "PHASE-002"


def main():
    database = kb.KnowledgeDB()

    # Get current phase test_ids
    phase_data = {}
    for phase_id in [f"PHASE-{i:03d}" for i in range(1, 17)]:
        phase = database.get_test_plan_phase(phase_id)
        if phase:
            existing_ids = []
            if phase.get("test_ids"):
                try:
                    existing_ids = (
                        json.loads(phase["test_ids"]) if isinstance(phase["test_ids"], str) else phase["test_ids"]
                    )
                except (json.JSONDecodeError, TypeError):
                    existing_ids = []
            phase_data[phase_id] = {
                "title": phase["title"],
                "existing_ids": set(existing_ids),
                "new_ids": set(),
            }

    # Get ALL test IDs
    conn = database._get_conn()
    all_tests = conn.execute(
        "SELECT id, title, spec_id, test_type, test_file FROM current_tests ORDER BY id"
    ).fetchall()

    # Find orphans (not in any phase)
    all_phase_ids = set()
    for pd in phase_data.values():
        all_phase_ids.update(pd["existing_ids"])

    orphans = []
    for t in all_tests:
        test = {"id": t[0], "title": t[1], "spec_id": t[2], "test_type": t[3], "test_file": t[4]}
        if test["id"] not in all_phase_ids:
            orphans.append(test)

    print(f"Total tests: {len(all_tests)}")
    print(f"Already in phases: {len(all_phase_ids)}")
    print(f"Orphans to assign: {len(orphans)}")
    print()

    # Classify each orphan
    for test in orphans:
        phase_id = classify_test(test)
        phase_data[phase_id]["new_ids"].add(test["id"])

    # Report assignments
    print("Phase assignments:")
    for phase_id in sorted(phase_data.keys()):
        pd = phase_data[phase_id]
        if pd["new_ids"]:
            print(f"  {phase_id} ({pd['title']}): +{len(pd['new_ids'])} new (was {len(pd['existing_ids'])})")

    # Update each phase with new test IDs
    print()
    updated = 0
    for phase_id in sorted(phase_data.keys()):
        pd = phase_data[phase_id]
        if not pd["new_ids"]:
            continue

        merged = sorted(pd["existing_ids"] | pd["new_ids"])
        try:
            database.update_test_plan_phase(
                id=phase_id,
                changed_by=CHANGED_BY,
                change_reason=CHANGE_REASON,
                test_ids=merged,
            )
            print(f"  OK  {phase_id}: {len(pd['existing_ids'])} -> {len(merged)} tests")
            updated += 1
        except Exception as e:
            print(f"  ERR {phase_id}: {e}")

    print(f"\nPhases updated: {updated}")

    # Verify: count remaining orphans
    all_phase_ids_after = set()
    for phase_id in [f"PHASE-{i:03d}" for i in range(1, 17)]:
        phase = database.get_test_plan_phase(phase_id)
        if phase and phase.get("test_ids"):
            try:
                ids = json.loads(phase["test_ids"]) if isinstance(phase["test_ids"], str) else phase["test_ids"]
                all_phase_ids_after.update(ids)
            except:
                pass

    all_test_ids = set(t[0] for t in all_tests)
    remaining_orphans = all_test_ids - all_phase_ids_after
    print(f"\n{'=' * 60}")
    print(f"Total tests: {len(all_test_ids)}")
    print(f"Tests in phases: {len(all_phase_ids_after)}")
    print(f"Remaining orphans: {len(remaining_orphans)}")
    if remaining_orphans:
        for oid in sorted(remaining_orphans)[:10]:
            print(f"  {oid}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
