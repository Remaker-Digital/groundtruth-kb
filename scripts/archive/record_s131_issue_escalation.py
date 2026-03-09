"""S131 — Record spec, WI, and test artifacts for issue-report-as-escalation.

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
# Specification (GOV-09)
# ---------------------------------------------------------------------------

kdb.insert_spec(
    id="SPEC-1611",
    title="Issue report triggers escalation alert",
    description=(
        "When a customer using the chat widget submits an issue report via "
        "'Report an Issue', the system must handle it as an escalation request. "
        "Specifically, the report_issue endpoint must call send_escalation_alert() "
        "with the issue type as the reason, the issue details as context, and "
        "urgency 'medium'. This ensures the merchant team is actively notified "
        "(via email, webhook, dashboard alert) rather than the report being "
        "silently persisted in the conversation history."
    ),
    status="specified",
    changed_by=BY,
    change_reason="Owner spec: issue report should be handled as escalation request",
    priority="P1",
    scope="chat",
    section="CHAT",
    assertions=[
        {
            "description": "report_issue endpoint calls send_escalation_alert",
            "type": "grep",
            "pattern": "send_escalation_alert",
            "path": "src/chat/endpoints.py",
        },
    ],
)
print("SPEC-1611 recorded")

# ---------------------------------------------------------------------------
# Work Item
# ---------------------------------------------------------------------------

kdb.insert_work_item(
    id="WI-0933",
    title="Wire issue report to escalation alert delivery",
    description=(
        "The report_issue endpoint (POST /api/chat/conversations/{id}/issue) "
        "currently persists the issue as a system message and audit log entry, "
        "but does not notify the merchant team. Add a fire-and-forget call to "
        "send_escalation_alert() after persisting the issue, using the issue "
        "type as the escalation reason and issue details as context summary."
    ),
    origin="new",
    component="customer_interface",
    source_spec_id="SPEC-1611",
    resolution_status="open",
    priority="P1",
    changed_by=BY,
    change_reason="Owner spec: issue report should trigger escalation",
    stage="created",
)
print("WI-0933 recorded")

# ---------------------------------------------------------------------------
# Test Artifacts (GOV-12)
# ---------------------------------------------------------------------------

kdb.insert_test(
    id="TEST-2924",
    title="report_issue endpoint calls send_escalation_alert",
    spec_id="SPEC-1611",
    test_type="unit",
    expected_outcome="endpoints.py contains send_escalation_alert call in report_issue function",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0933",
    test_file="tests/unit/test_issue_report_escalation.py",
    test_class="TestIssueReportEscalation",
    test_function="test_report_issue_calls_escalation_alert",
)
print("TEST-2924 recorded")

kdb.insert_test(
    id="TEST-2925",
    title="Issue report escalation uses issue_type as reason",
    spec_id="SPEC-1611",
    test_type="unit",
    expected_outcome="The escalation alert reason includes the issue type",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0933",
    test_file="tests/unit/test_issue_report_escalation.py",
    test_class="TestIssueReportEscalation",
    test_function="test_escalation_reason_includes_issue_type",
)
print("TEST-2925 recorded")

kdb.insert_test(
    id="TEST-2926",
    title="Issue report escalation uses details as context_summary",
    spec_id="SPEC-1611",
    test_type="unit",
    expected_outcome="The escalation alert context_summary includes the issue details",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0933",
    test_file="tests/unit/test_issue_report_escalation.py",
    test_class="TestIssueReportEscalation",
    test_function="test_escalation_context_includes_details",
)
print("TEST-2926 recorded")

kdb.insert_test(
    id="TEST-2927",
    title="Issue report escalation is fire-and-forget (does not block response)",
    spec_id="SPEC-1611",
    test_type="unit",
    expected_outcome="Escalation alert failure does not prevent issue report response",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0933",
    test_file="tests/unit/test_issue_report_escalation.py",
    test_class="TestIssueReportEscalation",
    test_function="test_escalation_failure_does_not_block_response",
)
print("TEST-2927 recorded")

# ---------------------------------------------------------------------------
# GOV-13: Assign tests to PLAN-001 Phase 2
# ---------------------------------------------------------------------------

conn = sqlite3.connect(str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db" / "knowledge.db"))
row = conn.execute(
    "SELECT test_ids FROM current_test_plan_phases WHERE id = 'PHASE-002'"
).fetchone()

if row and row[0]:
    existing_ids = json.loads(row[0])
else:
    existing_ids = []

new_test_ids = ["TEST-2924", "TEST-2925", "TEST-2926", "TEST-2927"]
updated_ids = existing_ids + [tid for tid in new_test_ids if tid not in existing_ids]

kdb.update_test_plan_phase(
    id="PHASE-002",
    changed_by=BY,
    change_reason="GOV-13: assign S131 issue-report-as-escalation tests to Phase 2",
    test_ids=updated_ids,
)
print(f"PHASE-002 updated: {len(updated_ids)} tests (added {len(new_test_ids)})")

conn.close()
print("\nAll S131 issue-report-as-escalation artifacts recorded successfully.")
