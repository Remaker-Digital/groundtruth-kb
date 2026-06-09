"""S131 — Record WI and test artifacts for widget connection-lost defect fix.

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
# Specification
# ---------------------------------------------------------------------------

kdb.insert_spec(
    id="SPEC-1609",
    title="Widget connection exhaustion clears reconnecting state",
    description=(
        "When the SSE or WebSocket transport exhausts all reconnection "
        "attempts (10 attempts with exponential backoff, max 30s), the "
        "widget must clear the 'isReconnecting' state and display a "
        "final error message ('Unable to connect. Please try again.') "
        "instead of leaving the 'Connection lost. Reconnecting...' "
        "banner visible indefinitely. The connectionFailed locale key "
        "provides the translated error message in all 8 supported languages."
    ),
    status="implemented",
    changed_by=BY,
    change_reason="Defect: 'Connection lost' banner stays forever after max reconnect attempts",
    priority="P2",
    scope="widget_ui",
    section="WIDGET_UI",
    assertions=[
        {
            "description": "SSEConnection options include onMaxReconnectsExhausted callback",
            "type": "grep",
            "pattern": "onMaxReconnectsExhausted",
            "path": "widget/src/transport/sse.ts",
        },
        {
            "description": "WSConnection options include onMaxReconnectsExhausted callback",
            "type": "grep",
            "pattern": "onMaxReconnectsExhausted",
            "path": "widget/src/transport/ws.ts",
        },
        {
            "description": "Panel.tsx wires onMaxReconnectsExhausted to clear isReconnecting",
            "type": "grep",
            "pattern": "onMaxReconnectsExhausted",
            "path": "widget/src/components/Panel.tsx",
        },
        {
            "description": "English locale has connectionFailed key",
            "type": "grep",
            "pattern": "connectionFailed",
            "path": "widget/src/locale/en.ts",
        },
    ],
)
print("SPEC-1609 recorded")

# ---------------------------------------------------------------------------
# Work Item
# ---------------------------------------------------------------------------

kdb.insert_work_item(
    id="WI-0931",
    title="Widget 'Connection lost' banner stuck forever after max reconnect attempts",
    description=(
        "When SSE/WebSocket reconnection attempts are exhausted (10 attempts with "
        "exponential backoff), the isReconnecting state is never cleared back to "
        "false. The 'Connection lost. Reconnecting...' banner stays visible "
        "permanently. Additionally, HTTP errors (400/404/503) from the SSE endpoint "
        "trigger the same reconnect loop as network disconnections, wasting attempts "
        "on an endpoint returning deterministic errors. Fix: add onMaxReconnectsExhausted "
        "callback to SSE/WS transports; Panel.tsx clears isReconnecting and shows "
        "a final 'Unable to connect' error. New connectionFailed locale key added "
        "to all 8 languages."
    ),
    origin="defect",
    component="customer_interface",
    source_spec_id="SPEC-1609",
    resolution_status="open",
    priority="P2",
    changed_by=BY,
    change_reason="Owner defect report: 'Connection is lost. Reconnecting.' stuck on staging Co-Pilot widget",
    stage="created",
)
print("WI-0931 recorded")

# ---------------------------------------------------------------------------
# Test Artifacts (GOV-12: WI creation triggers test creation)
# ---------------------------------------------------------------------------

kdb.insert_test(
    id="TEST-2916",
    title="SSEConnection.scheduleReconnect notifies on max attempts exhausted",
    spec_id="SPEC-1609",
    test_type="unit",
    expected_outcome="onMaxReconnectsExhausted callback is invoked when reconnectAttempts reaches maxReconnectAttempts",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0931",
    test_file="tests/widget/test_widget_core.py",
    test_class="TestSSEMaxReconnectExhaustion",
    test_function="test_sse_options_has_max_reconnects_exhausted_callback",
)
print("TEST-2916 recorded")

kdb.insert_test(
    id="TEST-2917",
    title="WSConnection.scheduleReconnect notifies on max attempts exhausted",
    spec_id="SPEC-1609",
    test_type="unit",
    expected_outcome="onMaxReconnectsExhausted callback is invoked when reconnectAttempts reaches maxReconnectAttempts",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0931",
    test_file="tests/widget/test_widget_core.py",
    test_class="TestWSMaxReconnectExhaustion",
    test_function="test_ws_options_has_max_reconnects_exhausted_callback",
)
print("TEST-2917 recorded")

kdb.insert_test(
    id="TEST-2918",
    title="Panel.tsx wires onMaxReconnectsExhausted to clear isReconnecting",
    spec_id="SPEC-1609",
    test_type="unit",
    expected_outcome="Panel.tsx passes onMaxReconnectsExhausted callback to SSEConnection constructor",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0931",
    test_file="tests/widget/test_widget_core.py",
    test_class="TestPanelMaxReconnectHandling",
    test_function="test_panel_wires_max_reconnect_exhausted",
)
print("TEST-2918 recorded")

kdb.insert_test(
    id="TEST-2919",
    title="connectionFailed locale key exists in all 8 language files",
    spec_id="SPEC-1609",
    test_type="unit",
    expected_outcome="All locale files (en, de, fr, es, ja, ko, zh, pt) contain connectionFailed key",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0931",
    test_file="tests/widget/test_widget_core.py",
    test_class="TestConnectionFailedLocale",
    test_function="test_connection_failed_locale_all_languages",
)
print("TEST-2919 recorded")

# ---------------------------------------------------------------------------
# GOV-13: Assign tests to PLAN-001 phases
# ---------------------------------------------------------------------------

# Widget tests — assign to Phase 3 (widget tests)
conn = sqlite3.connect(str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db" / "knowledge.db"))
row = conn.execute("SELECT test_ids FROM current_test_plan_phases WHERE id = 'PHASE-003'").fetchone()

if row and row[0]:
    existing_ids = json.loads(row[0])
else:
    existing_ids = []

new_test_ids = ["TEST-2916", "TEST-2917", "TEST-2918", "TEST-2919"]
updated_ids = existing_ids + [tid for tid in new_test_ids if tid not in existing_ids]

kdb.update_test_plan_phase(
    id="PHASE-003",
    changed_by=BY,
    change_reason="GOV-13: assign S131 widget defect test artifacts to Phase 3",
    test_ids=updated_ids,
)
print(f"PHASE-003 updated: {len(updated_ids)} tests (added {len(new_test_ids)})")

conn.close()
print("\nAll S131 widget defect artifacts recorded successfully.")
