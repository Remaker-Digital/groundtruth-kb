"""S130: Create tier entitlement test artifacts for SPEC-1490/1491/1492."""
# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "tools/knowledge-db")
import db as dbmod

d = dbmod.KnowledgeDB()

TEST_FILE = "tests/multi_tenant/test_tier_rate_limits.py"
CHANGED_BY = "S130"
CHANGE_REASON = "Tier entitlement audit: fill test gaps for all TIER_DEFAULTS attributes"

tests = [
    # -- SPEC-1490 (Starter) --
    {
        "id": "TEST-2865", "spec_id": "SPEC-1490",
        "title": "TIER_DEFAULTS Starter included_conversations equals 1000",
        "expected": 'TIER_DEFAULTS["starter"]["included_conversations"] == 1000',
        "func": "test_starter_included_conversations", "cls": "TestStarterEntitlements",
        "desc": "Asserts Starter tier includes exactly 1,000 conversations/month.",
    },
    {
        "id": "TEST-2866", "spec_id": "SPEC-1490",
        "title": "TIER_DEFAULTS Starter max_concurrent equals 5",
        "expected": 'TIER_DEFAULTS["starter"]["max_concurrent"] == 5',
        "func": "test_starter_max_concurrent", "cls": "TestStarterEntitlements",
        "desc": "Asserts Starter tier max concurrent sessions is 5.",
    },
    {
        "id": "TEST-2867", "spec_id": "SPEC-1490",
        "title": "TIER_DEFAULTS Starter memory_layers equals [1, 2]",
        "expected": 'TIER_DEFAULTS["starter"]["memory_layers"] == [1, 2]',
        "func": "test_starter_memory_layers", "cls": "TestStarterEntitlements",
        "desc": "Asserts Starter tier has PCM Layers 1-2 only.",
    },
    {
        "id": "TEST-2868", "spec_id": "SPEC-1490",
        "title": "TIER_DEFAULTS Starter overage_rate equals 0.04",
        "expected": 'TIER_DEFAULTS["starter"]["overage_rate"] == 0.04',
        "func": "test_starter_overage_rate", "cls": "TestStarterEntitlements",
        "desc": "Asserts Starter tier overage rate is $0.04/conversation.",
    },
    {
        "id": "TEST-2869", "spec_id": "SPEC-1490",
        "title": "TIER_DEFAULTS Starter max_quick_actions equals 5",
        "expected": 'TIER_DEFAULTS["starter"]["max_quick_actions"] == 5',
        "func": "test_starter_max_quick_actions", "cls": "TestStarterEntitlements",
        "desc": "Asserts Starter tier max quick actions is 5.",
    },
    {
        "id": "TEST-2870", "spec_id": "SPEC-1490",
        "title": "TIER_DEFAULTS Starter max_quick_action_assignments equals 10",
        "expected": 'TIER_DEFAULTS["starter"]["max_quick_action_assignments"] == 10',
        "func": "test_starter_max_quick_action_assignments", "cls": "TestStarterEntitlements",
        "desc": "Asserts Starter tier max quick action assignments is 10.",
    },
    # -- SPEC-1491 (Professional) --
    {
        "id": "TEST-2871", "spec_id": "SPEC-1491",
        "title": "TIER_DEFAULTS Professional included_conversations equals 5000",
        "expected": 'TIER_DEFAULTS["professional"]["included_conversations"] == 5000',
        "func": "test_professional_included_conversations", "cls": "TestProfessionalEntitlements",
        "desc": "Asserts Professional tier includes exactly 5,000 conversations/month.",
    },
    {
        "id": "TEST-2872", "spec_id": "SPEC-1491",
        "title": "TIER_DEFAULTS Professional max_concurrent equals 10",
        "expected": 'TIER_DEFAULTS["professional"]["max_concurrent"] == 10',
        "func": "test_professional_max_concurrent", "cls": "TestProfessionalEntitlements",
        "desc": "Asserts Professional tier max concurrent sessions is 10.",
    },
    {
        "id": "TEST-2873", "spec_id": "SPEC-1491",
        "title": "TIER_DEFAULTS Professional memory_layers equals [1, 2, 3]",
        "expected": 'TIER_DEFAULTS["professional"]["memory_layers"] == [1, 2, 3]',
        "func": "test_professional_memory_layers", "cls": "TestProfessionalEntitlements",
        "desc": "Asserts Professional tier has PCM Layers 1-3.",
    },
    {
        "id": "TEST-2874", "spec_id": "SPEC-1491",
        "title": "TIER_DEFAULTS Professional overage_rate equals 0.025",
        "expected": 'TIER_DEFAULTS["professional"]["overage_rate"] == 0.025',
        "func": "test_professional_overage_rate", "cls": "TestProfessionalEntitlements",
        "desc": "Asserts Professional tier overage rate is $0.025/conversation.",
    },
    {
        "id": "TEST-2875", "spec_id": "SPEC-1491",
        "title": "TIER_DEFAULTS Professional max_quick_actions equals 20",
        "expected": 'TIER_DEFAULTS["professional"]["max_quick_actions"] == 20',
        "func": "test_professional_max_quick_actions", "cls": "TestProfessionalEntitlements",
        "desc": "Asserts Professional tier max quick actions is 20.",
    },
    {
        "id": "TEST-2876", "spec_id": "SPEC-1491",
        "title": "TIER_DEFAULTS Professional max_quick_action_assignments equals 50",
        "expected": 'TIER_DEFAULTS["professional"]["max_quick_action_assignments"] == 50',
        "func": "test_professional_max_quick_action_assignments", "cls": "TestProfessionalEntitlements",
        "desc": "Asserts Professional tier max quick action assignments is 50.",
    },
    # -- SPEC-1492 (Enterprise) --
    {
        "id": "TEST-2877", "spec_id": "SPEC-1492",
        "title": "TIER_DEFAULTS Enterprise included_conversations equals 20000",
        "expected": 'TIER_DEFAULTS["enterprise"]["included_conversations"] == 20000',
        "func": "test_enterprise_included_conversations", "cls": "TestEnterpriseEntitlements",
        "desc": "Asserts Enterprise tier includes exactly 20,000 conversations/month.",
    },
    {
        "id": "TEST-2878", "spec_id": "SPEC-1492",
        "title": "TIER_DEFAULTS Enterprise max_concurrent equals 30",
        "expected": 'TIER_DEFAULTS["enterprise"]["max_concurrent"] == 30',
        "func": "test_enterprise_max_concurrent", "cls": "TestEnterpriseEntitlements",
        "desc": "Asserts Enterprise tier max concurrent sessions is 30.",
    },
    {
        "id": "TEST-2879", "spec_id": "SPEC-1492",
        "title": "TIER_DEFAULTS Enterprise memory_layers equals [1, 2, 3, 4]",
        "expected": 'TIER_DEFAULTS["enterprise"]["memory_layers"] == [1, 2, 3, 4]',
        "func": "test_enterprise_memory_layers", "cls": "TestEnterpriseEntitlements",
        "desc": "Asserts Enterprise tier has PCM Layers 1-4 (including dedicated model training).",
    },
    {
        "id": "TEST-2880", "spec_id": "SPEC-1492",
        "title": "TIER_DEFAULTS Enterprise overage_rate equals 0.015",
        "expected": 'TIER_DEFAULTS["enterprise"]["overage_rate"] == 0.015',
        "func": "test_enterprise_overage_rate", "cls": "TestEnterpriseEntitlements",
        "desc": "Asserts Enterprise tier overage rate is $0.015/conversation.",
    },
    {
        "id": "TEST-2881", "spec_id": "SPEC-1492",
        "title": "TIER_DEFAULTS Enterprise max_quick_actions equals 50",
        "expected": 'TIER_DEFAULTS["enterprise"]["max_quick_actions"] == 50',
        "func": "test_enterprise_max_quick_actions", "cls": "TestEnterpriseEntitlements",
        "desc": "Asserts Enterprise tier max quick actions is 50.",
    },
    {
        "id": "TEST-2882", "spec_id": "SPEC-1492",
        "title": "TIER_DEFAULTS Enterprise max_quick_action_assignments equals 200",
        "expected": 'TIER_DEFAULTS["enterprise"]["max_quick_action_assignments"] == 200',
        "func": "test_enterprise_max_quick_action_assignments", "cls": "TestEnterpriseEntitlements",
        "desc": "Asserts Enterprise tier max quick action assignments is 200.",
    },
]

print(f"Creating {len(tests)} test artifacts...")
for t in tests:
    result = d.insert_test(
        id=t["id"],
        title=t["title"],
        spec_id=t["spec_id"],
        test_type="unit",
        expected_outcome=t["expected"],
        changed_by=CHANGED_BY,
        change_reason=CHANGE_REASON,
        test_file=TEST_FILE,
        test_class=t["cls"],
        test_function=t["func"],
        description=t["desc"],
    )
    print(f"  Created {result['id']} v{result['version']}: {result['title']}")

# ---- Assign all 18 to PHASE-002 ----
new_ids = [t["id"] for t in tests]
phase = d.get_test_plan_phase("PHASE-002")
current_ids = json.loads(phase["test_ids"]) if isinstance(phase["test_ids"], str) else (phase["test_ids"] or [])
for tid in new_ids:
    if tid not in current_ids:
        current_ids.append(tid)

d.update_test_plan_phase(
    "PHASE-002",
    changed_by=CHANGED_BY,
    change_reason="GOV-13: assign SPEC-1490/1491/1492 entitlement tests to phase",
    test_ids=current_ids,
)
print(f"\nPHASE-002 updated: now {len(current_ids)} tests (+{len(new_ids)} added)")

print("\nAll done. No orphan tests.")
