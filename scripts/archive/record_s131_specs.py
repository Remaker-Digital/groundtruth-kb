"""S131 — Record specifications, work items, and test artifacts for billable
classification deferral + inbox zero-message filter.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))
import db  # noqa: E402

kdb = db.KnowledgeDB()
BY = "S131"

# ---------------------------------------------------------------------------
# Specifications
# ---------------------------------------------------------------------------

kdb.insert_spec(
    id="SPEC-1606",
    title="Billable classification deferred until AI response",
    description=(
        "A conversation is non-billable at creation (is_billable=False). "
        "It becomes billable only when the system generates at least one AI "
        "response for an eligible conversation (not prefixed with test_, admin_, "
        "health_, system_, and not conversation_type=admin_assistance). "
        "The finalization safety net (no AI response → non-billable) is retained. "
        "This eliminates false-positive billability for abandoned, rate-limited, "
        "or errored conversations that never receive an AI response."
    ),
    status="specified",
    changed_by=BY,
    change_reason="Defect: staging shows 404 billable conversations from orphaned load test data",
    priority="P1",
    scope="billing",
    section="BILLING",
    assertions=[
        {
            "description": "ConversationDocument created with is_billable=False",
            "type": "grep",
            "pattern": "is_billable=False",
            "path": "src/chat/session.py",
        },
        {
            "description": "add_ai_message promotes eligible conversations to billable",
            "type": "grep",
            "pattern": "is_billable.*True",
            "path": "src/chat/session.py",
        },
        {
            "description": "cosmos_schema default is_billable=False",
            "type": "grep",
            "pattern": "is_billable.*default=False",
            "path": "src/multi_tenant/cosmos_schema.py",
        },
    ],
)
print("SPEC-1606 recorded")

kdb.insert_spec(
    id="SPEC-1607",
    title="Inbox excludes zero-message conversations",
    description=(
        "The admin conversation inbox API (list_filtered, count_filtered) "
        "excludes conversations with message_count=0. Conversations with no "
        "messages are artifacts of abandoned or rate-limited connection attempts "
        "and provide no value to the merchant admin team. This filter is always "
        "applied — there is no parameter to include zero-message conversations."
    ),
    status="specified",
    changed_by=BY,
    change_reason="Owner specification: inbox should not display 0-message conversations",
    priority="P1",
    scope="admin_ui",
    section="ADMIN_UI",
    assertions=[
        {
            "description": "list_filtered excludes zero-message conversations",
            "type": "grep",
            "pattern": "message_count > 0",
            "path": "src/multi_tenant/repositories/conversation.py",
        },
        {
            "description": "count_filtered excludes zero-message conversations",
            "type": "grep",
            "pattern": "message_count > 0",
            "path": "src/multi_tenant/repositories/conversation.py",
        },
    ],
)
print("SPEC-1607 recorded")

kdb.insert_spec(
    id="SPEC-1608",
    title="Dashboard recent conversations excludes zero-message entries",
    description=(
        "The dashboard recent conversations list (fetched from the conversation "
        "API) shows only conversations with at least one message. This is "
        "a consequence of SPEC-1607 (inbox filter) and SPEC-1606 (billable "
        "classification deferral) — conversations with 0 messages are non-billable "
        "and excluded from the inbox API used by the dashboard."
    ),
    status="specified",
    changed_by=BY,
    change_reason="Derived from SPEC-1606 + SPEC-1607",
    priority="P2",
    scope="admin_ui",
    section="ADMIN_UI",
    assertions=[
        {
            "description": "Dashboard filters conversations by isBillable !== false",
            "type": "grep",
            "pattern": "isBillable.*false",
            "path": "admin/standalone/pages/Dashboard.tsx",
        },
    ],
)
print("SPEC-1608 recorded")

# ---------------------------------------------------------------------------
# Work Items
# ---------------------------------------------------------------------------

kdb.insert_work_item(
    id="WI-0928",
    title="ConversationDocument default is_billable=False + promote on AI response",
    description=(
        "Change conversation creation to default is_billable=False. Add promotion "
        "to is_billable=True in add_ai_message() for eligible conversations "
        "(non-prefixed IDs). Update cosmos_schema.py default. Fixes orphaned "
        "conversations from load tests being counted as billable."
    ),
    origin="defect",
    component="agent_implementation",
    source_spec_id="SPEC-1606",
    resolution_status="open",
    priority="P1",
    changed_by=BY,
    change_reason="Root cause of staging 404 billable count error",
    stage="created",
)
print("WI-0928 recorded")

kdb.insert_work_item(
    id="WI-0929",
    title="Inbox API excludes zero-message conversations",
    description=(
        "Add message_count > 0 condition to list_filtered() and count_filtered() "
        "in ConversationRepository. Conversations with 0 messages are abandoned "
        "connection attempts and should never appear in the merchant inbox."
    ),
    origin="defect",
    component="customer_interface",
    source_spec_id="SPEC-1607",
    resolution_status="open",
    priority="P1",
    changed_by=BY,
    change_reason="Owner spec: inbox shows 0-message timed_out conversations",
    stage="created",
)
print("WI-0929 recorded")

kdb.insert_work_item(
    id="WI-0930",
    title="Staging data cleanup: patch orphaned conversations to non-billable",
    description=(
        "Write a one-time cleanup script to patch existing orphaned conversations "
        "in staging Cosmos (is_billable=true but message_count=0) to "
        "is_billable=false. This corrects the historical data pollution from "
        "Locust load tests and verification scripts."
    ),
    origin="hygiene",
    component="database",
    source_spec_id="SPEC-1606",
    resolution_status="open",
    priority="P2",
    changed_by=BY,
    change_reason="Staging data quality: 404 false-positive billable conversations",
    stage="created",
)
print("WI-0930 recorded")

# ---------------------------------------------------------------------------
# Test Artifacts (GOV-12: WI creation triggers test creation)
# ---------------------------------------------------------------------------

kdb.insert_test(
    id="TEST-2909",
    title="ConversationDocument created with is_billable=False",
    spec_id="SPEC-1606",
    test_type="unit",
    expected_outcome="New conversation documents have is_billable=False at creation",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0928",
    test_file="tests/multi_tenant/test_billable_classification.py",
    test_class="TestBillableClassification",
    test_function="test_conversation_created_non_billable",
)
print("TEST-2909 recorded")

kdb.insert_test(
    id="TEST-2910",
    title="add_ai_message promotes eligible conversation to billable",
    spec_id="SPEC-1606",
    test_type="unit",
    expected_outcome="After AI response, eligible conversation has is_billable=True",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0928",
    test_file="tests/multi_tenant/test_billable_classification.py",
    test_class="TestBillableClassification",
    test_function="test_ai_response_promotes_billable",
)
print("TEST-2910 recorded")

kdb.insert_test(
    id="TEST-2911",
    title="Non-billable prefix conversation stays non-billable after AI response",
    spec_id="SPEC-1606",
    test_type="unit",
    expected_outcome="Conversation with test_ prefix remains is_billable=False after AI response",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0928",
    test_file="tests/multi_tenant/test_billable_classification.py",
    test_class="TestBillableClassification",
    test_function="test_prefixed_conversation_stays_non_billable",
)
print("TEST-2911 recorded")

kdb.insert_test(
    id="TEST-2912",
    title="cosmos_schema ConversationDocument default is_billable=False",
    spec_id="SPEC-1606",
    test_type="assertion",
    expected_outcome="ConversationDocument.is_billable has default=False in schema",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0928",
    test_file="tests/multi_tenant/test_billable_classification.py",
    test_class="TestBillableClassification",
    test_function="test_schema_default_non_billable",
)
print("TEST-2912 recorded")

kdb.insert_test(
    id="TEST-2913",
    title="Inbox list_filtered excludes zero-message conversations",
    spec_id="SPEC-1607",
    test_type="unit",
    expected_outcome="list_filtered query includes message_count > 0 condition",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0929",
    test_file="tests/multi_tenant/test_billable_classification.py",
    test_class="TestInboxZeroMessageFilter",
    test_function="test_list_filtered_excludes_zero_messages",
)
print("TEST-2913 recorded")

kdb.insert_test(
    id="TEST-2914",
    title="Inbox count_filtered excludes zero-message conversations",
    spec_id="SPEC-1607",
    test_type="unit",
    expected_outcome="count_filtered query includes message_count > 0 condition",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0929",
    test_file="tests/multi_tenant/test_billable_classification.py",
    test_class="TestInboxZeroMessageFilter",
    test_function="test_count_filtered_excludes_zero_messages",
)
print("TEST-2914 recorded")

kdb.insert_test(
    id="TEST-2915",
    title="Finalization safety net: no AI response → non-billable",
    spec_id="SPEC-1606",
    test_type="unit",
    expected_outcome="Conversation finalization patches is_billable=False when message_count<=1",
    changed_by=BY,
    change_reason="GOV-12: safety net verification for WI-0928",
    test_file="tests/multi_tenant/test_billable_classification.py",
    test_class="TestBillableClassification",
    test_function="test_finalization_safety_net",
)
print("TEST-2915 recorded")

# ---------------------------------------------------------------------------
# GOV-13: Assign tests to PLAN-001 phases
# ---------------------------------------------------------------------------

# These are billing/metering tests — assign to Phase 2 (unit tests)
conn = sqlite3.connect(str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db" / "knowledge.db"))
row = conn.execute(
    "SELECT test_ids FROM current_test_plan_phases WHERE id = 'PHASE-002'"
).fetchone()

if row and row[0]:
    existing_ids = json.loads(row[0])
else:
    existing_ids = []

new_test_ids = [
    "TEST-2909", "TEST-2910", "TEST-2911", "TEST-2912",
    "TEST-2913", "TEST-2914", "TEST-2915",
]
updated_ids = existing_ids + [tid for tid in new_test_ids if tid not in existing_ids]

kdb.update_test_plan_phase(
    id="PHASE-002",
    changed_by=BY,
    change_reason="GOV-13: assign S131 test artifacts to Phase 2",
    test_ids=updated_ids,
)
print(f"PHASE-002 updated: {len(updated_ids)} tests (added {len(new_test_ids)})")

conn.close()
print("\nAll S131 artifacts recorded successfully.")
