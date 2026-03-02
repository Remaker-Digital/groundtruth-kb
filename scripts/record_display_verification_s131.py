"""Record SPEC-1613, WI-0935, and TEST-2932..2939 for display value verification tests.

S131 continuation: 227 Playwright E2E tests verifying every displayed value
across all 12 admin UI surfaces matches mock API data.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
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
    # SPEC-1613: Display value verification
    # ------------------------------------------------------------------
    print("Recording SPEC-1613...")
    kdb.insert_spec(
        id="SPEC-1613",
        title="Display value verification — every UI value must be present and accurate",
        description=(
            "Every value intended for display in all admin UI surfaces "
            "(configuration, state, metrics, version information, tenant "
            "information variables) must be both (1) present in the DOM and "
            "(2) accurate — matching the data returned by the API. Back-end "
            "tests are not sufficient; verification of displayed data must "
            "be performed by visual inspection of all UI elements via "
            "Playwright E2E tests with deterministic mock API responses."
        ),
        status="implemented",
        section="ADMIN_UI",
        type="requirement",
        assertions=[
            {
                "id": "SPEC-1613-A1",
                "description": "Dashboard stat cards display correct values from analytics API",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1613-A2",
                "description": "Configuration page form fields render correct API values",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1613-A3",
                "description": "Widget configuration controls display correct API values",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1613-A4",
                "description": "Team table renders all member data values correctly",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1613-A5",
                "description": "Layout sidebar and footer display correct navigation and version info",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1613-A6",
                "description": "Inbox conversation list displays all conversation data values",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1613-A7",
                "description": "Analytics page stat cards and topic table display correct values",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1613-A8",
                "description": "KB, Billing, Quick Actions, Integrations, Memory pages display correct values",
                "type": "e2e",
                "status": "implemented",
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="Owner specification: every displayed UI value must be verified present and accurate",
    )
    print("  SPEC-1613 recorded.")

    # ------------------------------------------------------------------
    # WI-0935: Implement display value verification tests
    # ------------------------------------------------------------------
    print("Recording WI-0935...")
    kdb.insert_work_item(
        id="WI-0935",
        title="Display value verification tests — 227 E2E tests across all admin UI surfaces",
        description=(
            "Implement Playwright E2E tests that verify every displayed value "
            "in all admin UI surfaces matches the expected mock API data. "
            "Covers Dashboard (57), Configuration (29), Widget (30), Team (22), "
            "Layout (19), Inbox (18), Analytics (25), and remaining pages (27). "
            "Total: 227 tests across 8 test files."
        ),
        source_spec_id="SPEC-1613",
        origin="new",
        component="customer_interface",
        resolution_status="resolved",
        stage="resolved",
        changed_by=CHANGED_BY,
        change_reason="Display value verification per owner specification",
    )
    print("  WI-0935 recorded.")

    # ------------------------------------------------------------------
    # TEST-2932..2939: Test artifacts (one per file)
    # ------------------------------------------------------------------
    test_files = [
        {
            "id": "TEST-2932",
            "title": "Dashboard display value verification (57 tests)",
            "file": "tests/e2e/test_dashboard_display_values.py",
            "description": (
                "57 Playwright E2E tests verifying Dashboard stat cards, "
                "recent conversations, top topics, knowledge gaps, setup "
                "checklist, and period filter display correct mock data values."
            ),
        },
        {
            "id": "TEST-2933",
            "title": "Configuration display value verification (29 tests)",
            "file": "tests/e2e/test_configuration_display_values.py",
            "description": (
                "29 Playwright E2E tests verifying Configuration page brand, "
                "policies, escalation, language, custom instructions, and "
                "named configs display correct mock data values."
            ),
        },
        {
            "id": "TEST-2934",
            "title": "Widget configuration display value verification (30 tests)",
            "file": "tests/e2e/test_widget_display_values.py",
            "description": (
                "30 Playwright E2E tests verifying Widget configuration "
                "installation, appearance, behavior, and content sections "
                "display correct mock data values."
            ),
        },
        {
            "id": "TEST-2935",
            "title": "Team page display value verification (22 tests)",
            "file": "tests/e2e/test_team_display_values.py",
            "description": (
                "22 Playwright E2E tests verifying Team page member count "
                "and table values for 3 mock members (superadmin, escalation "
                "agent, viewer) display correct data."
            ),
        },
        {
            "id": "TEST-2936",
            "title": "Layout display value verification (19 tests)",
            "file": "tests/e2e/test_layout_display_values.py",
            "description": (
                "19 Playwright E2E tests verifying Layout sidebar navigation "
                "items, tier badge, brand name, AI Configuration status badge, "
                "footer copyright, and version display."
            ),
        },
        {
            "id": "TEST-2937",
            "title": "Inbox display value verification (18 tests)",
            "file": "tests/e2e/test_inbox_display_values.py",
            "description": (
                "18 Playwright E2E tests verifying Inbox conversation list "
                "displays correct customer names, message counts, status "
                "badges, and assignment data for 3 mock conversations."
            ),
        },
        {
            "id": "TEST-2938",
            "title": "Analytics display value verification (25 tests)",
            "file": "tests/e2e/test_analytics_display_values.py",
            "description": (
                "25 Playwright E2E tests verifying Analytics page stat cards "
                "and topic breakdown table display correct mock values."
            ),
        },
        {
            "id": "TEST-2939",
            "title": "Remaining pages display value verification (27 tests)",
            "file": "tests/e2e/test_remaining_display_values.py",
            "description": (
                "27 Playwright E2E tests verifying KB (8), Billing (5), "
                "Quick Actions (3), Integrations (2), and Memory & Privacy (9) "
                "pages display correct mock data values."
            ),
        },
    ]

    new_test_ids = []
    for t in test_files:
        print(f"Recording {t['id']}...")
        kdb.insert_test(
            id=t["id"],
            spec_id="SPEC-1613",
            title=t["title"],
            test_type="e2e",
            expected_outcome="All display values match mock API data (Playwright assertions PASS)",
            test_file=t["file"],
            description=t["description"],
            changed_by=CHANGED_BY,
            change_reason=f"Display value verification — {t['file']}",
        )
        new_test_ids.append(t["id"])
        print(f"  {t['id']} recorded.")

    # ------------------------------------------------------------------
    # GOV-13: Assign tests to PHASE-002 (E2E tests phase)
    # ------------------------------------------------------------------
    print("\nAssigning to PHASE-002 (GOV-13)...")
    phase = kdb.get_test_plan_phase("PHASE-002")
    if phase:
        existing_ids = json.loads(phase["test_ids"]) if phase["test_ids"] else []
        combined = existing_ids + new_test_ids
        kdb.update_test_plan_phase(
            id="PHASE-002",
            changed_by=CHANGED_BY,
            change_reason="Add TEST-2932..2939 (display value verification, 227 tests)",
            test_ids=combined,
        )
        print(f"  PHASE-002 updated: {len(existing_ids)} -> {len(combined)} test IDs")
    else:
        print("  WARNING: PHASE-002 not found!")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Spec:  SPEC-1613 (8 assertions)")
    print(f"  WI:    WI-0935 (resolved)")
    print(f"  Tests: TEST-2932..2939 (8 artifacts, 227 total tests)")
    print(f"  Phase: PHASE-002 (all assigned per GOV-13)")
    print()


if __name__ == "__main__":
    main()
