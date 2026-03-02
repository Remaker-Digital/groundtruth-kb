"""S131 — Record spec, WI, and test artifacts for team invite email link defect.

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
# Specification (GOV-09: owner spec language triggers spec-first workflow)
# ---------------------------------------------------------------------------

kdb.insert_spec(
    id="SPEC-1610",
    title="Team invitation email must contain admin console link",
    description=(
        "The email sent to a new team member via send_team_invite_alert() "
        "must always contain a clickable link to the merchant admin console. "
        "The admin URL is resolved via cascading fallback: APP_BASE_URL env → "
        "STANDALONE_ADMIN_URL env → PROD_URL env → hardcoded API gateway FQDN. "
        "The link appears both as a styled 'Open Admin Dashboard' button and "
        "as a plaintext URL in the message body. The email must never be sent "
        "without a link, even if no environment variable is configured."
    ),
    status="implemented",
    changed_by=BY,
    change_reason="Owner defect: team invite email missing admin console link",
    priority="P1",
    scope="email",
    section="EMAIL",
    assertions=[
        {
            "description": "send_team_invite_alert uses cascading URL fallback (not just APP_BASE_URL)",
            "type": "grep",
            "pattern": "STANDALONE_ADMIN_URL",
            "path": "src/multi_tenant/alert_delivery.py",
        },
        {
            "description": "Hardcoded FQDN fallback ensures link is always present",
            "type": "grep",
            "pattern": "agent-red-api-gateway.orangeglacier",
            "path": "src/multi_tenant/alert_delivery.py",
        },
    ],
)
print("SPEC-1610 recorded")

# ---------------------------------------------------------------------------
# Work Item
# ---------------------------------------------------------------------------

kdb.insert_work_item(
    id="WI-0932",
    title="Team invite email missing admin console link",
    description=(
        "The send_team_invite_alert() function derives the admin console URL "
        "solely from APP_BASE_URL env var. When this env var is not set (as in "
        "the current production and staging Container App configuration), the "
        "email is sent without any link — the 'Open Admin Dashboard' button "
        "disappears and the message text omits the URL. Fix: adopt the same "
        "cascading URL resolution as welcome_email._build_admin_login_url() "
        "(APP_BASE_URL → STANDALONE_ADMIN_URL → PROD_URL → FQDN fallback)."
    ),
    origin="defect",
    component="external_integration",
    source_spec_id="SPEC-1610",
    resolution_status="open",
    priority="P1",
    changed_by=BY,
    change_reason="Owner defect report: team invite email has no link to admin console",
    stage="created",
)
print("WI-0932 recorded")

# ---------------------------------------------------------------------------
# Test Artifacts (GOV-12)
# ---------------------------------------------------------------------------

kdb.insert_test(
    id="TEST-2920",
    title="send_team_invite_alert uses cascading URL fallback",
    spec_id="SPEC-1610",
    test_type="unit",
    expected_outcome="alert_delivery.py references STANDALONE_ADMIN_URL for cascading fallback",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0932",
    test_file="tests/multi_tenant/test_team_invite_email.py",
    test_class="TestTeamInviteEmailLink",
    test_function="test_cascading_url_fallback_pattern",
)
print("TEST-2920 recorded")

kdb.insert_test(
    id="TEST-2921",
    title="Team invite email always includes hardcoded FQDN fallback",
    spec_id="SPEC-1610",
    test_type="unit",
    expected_outcome="alert_delivery.py contains hardcoded API gateway FQDN as final fallback",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0932",
    test_file="tests/multi_tenant/test_team_invite_email.py",
    test_class="TestTeamInviteEmailLink",
    test_function="test_fqdn_fallback_always_present",
)
print("TEST-2921 recorded")

kdb.insert_test(
    id="TEST-2922",
    title="Team invite alert admin_url metadata is always non-empty",
    spec_id="SPEC-1610",
    test_type="unit",
    expected_outcome="send_team_invite_alert sets non-empty admin_url in alert metadata even without env vars",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0932",
    test_file="tests/multi_tenant/test_team_invite_email.py",
    test_class="TestTeamInviteEmailLink",
    test_function="test_admin_url_never_empty",
)
print("TEST-2922 recorded")

kdb.insert_test(
    id="TEST-2923",
    title="Team invite message body always contains admin URL",
    spec_id="SPEC-1610",
    test_type="unit",
    expected_outcome="The alert message text always includes the admin URL string",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0932",
    test_file="tests/multi_tenant/test_team_invite_email.py",
    test_class="TestTeamInviteEmailLink",
    test_function="test_message_always_contains_url",
)
print("TEST-2923 recorded")

# ---------------------------------------------------------------------------
# GOV-13: Assign tests to PLAN-001 phases
# ---------------------------------------------------------------------------

# Email tests — assign to Phase 2 (multi-tenant / integration tests)
conn = sqlite3.connect(str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db" / "knowledge.db"))
row = conn.execute(
    "SELECT test_ids FROM current_test_plan_phases WHERE id = 'PHASE-002'"
).fetchone()

if row and row[0]:
    existing_ids = json.loads(row[0])
else:
    existing_ids = []

new_test_ids = ["TEST-2920", "TEST-2921", "TEST-2922", "TEST-2923"]
updated_ids = existing_ids + [tid for tid in new_test_ids if tid not in existing_ids]

kdb.update_test_plan_phase(
    id="PHASE-002",
    changed_by=BY,
    change_reason="GOV-13: assign S131 team invite email test artifacts to Phase 2",
    test_ids=updated_ids,
)
print(f"PHASE-002 updated: {len(updated_ids)} tests (added {len(new_test_ids)})")

conn.close()
print("\nAll S131 team invite email defect artifacts recorded successfully.")
