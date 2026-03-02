"""Record SPEC-1614, WI-0936, and TEST-2940 for widget preview visual attribute tests.

S131 continuation: GOV-09 specification for widget/chat UI attribute verification
and E2E tests targeting the WidgetPreview component dark mode toggle + visual tokens.

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
    # SPEC-1614: Widget preview visual attribute verification
    # ------------------------------------------------------------------
    print("Recording SPEC-1614...")
    kdb.insert_spec(
        id="SPEC-1614",
        title="Widget preview visual attribute verification — dark mode toggle and all visual tokens",
        description=(
            "All widget and chat UI attribute variable values rendered in the "
            "admin WidgetPreview component must be individually verified by "
            "visual inspection. This includes: displayed text (header title, "
            "subtitle, greeting message, input placeholder, agent name, branding), "
            "colors (primary color, dark/light mode panel backgrounds, bubble "
            "colors, input colors), size (panel width, border radius), shadow "
            "settings (panel shadow), quick action pills, connection status "
            "(online indicator), avatar (initials fallback), and welcome message "
            "(greeting enabled, static/AI mode). The color mode SegmentedControl "
            "(Light/Dark/Auto) must reactively update all preview color tokens "
            "when toggled."
        ),
        status="implemented",
        section="ADMIN_UI",
        type="requirement",
        assertions=[
            {
                "id": "SPEC-1614-A1",
                "description": "WidgetPreview in light mode displays correct background colors (#fff panel, #fafafa msg area)",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1614-A2",
                "description": "Clicking 'Dark' in color mode SegmentedControl changes preview panel background to dark tokens (#292524 panel, #1c1917 msg area)",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1614-A3",
                "description": "Preview header displays config.headerTitle and config.headerSubtitle text",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1614-A4",
                "description": "Preview greeting message displays config.greetingMessage when greetingEnabled=True",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1614-A5",
                "description": "Preview input bar displays config.inputPlaceholder text",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1614-A6",
                "description": "Preview avatar shows 2-letter initials from config.agentDisplayName",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1614-A7",
                "description": "Preview header background uses config.primaryColor",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1614-A8",
                "description": "Preview online indicator dot and 'Online' text are visible",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1614-A9",
                "description": "Preview quick action pills display labels from quick actions API",
                "type": "e2e",
                "status": "implemented",
            },
            {
                "id": "SPEC-1614-A10",
                "description": "Preview branding text 'Powered by Agent Red' is visible",
                "type": "e2e",
                "status": "implemented",
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="GOV-09: Owner specification — all widget/chat UI attribute values must be visually verified",
    )
    print("  SPEC-1614 recorded.")

    # ------------------------------------------------------------------
    # WI-0936: Implement widget preview visual attribute tests
    # ------------------------------------------------------------------
    print("Recording WI-0936...")
    kdb.insert_work_item(
        id="WI-0936",
        title="Widget preview visual attribute E2E tests — dark mode toggle and all visual tokens",
        description=(
            "Implement Playwright E2E tests that verify every visual attribute "
            "rendered in the WidgetPreview component matches the expected config "
            "values. Covers dark mode toggle reactivity, header colors, text "
            "content, avatar initials, greeting message, quick action pills, "
            "online indicator, input placeholder, and branding. "
            "Total: ~25 tests in test_widget_preview_display_values.py."
        ),
        source_spec_id="SPEC-1614",
        origin="new",
        component="customer_interface",
        resolution_status="resolved",
        stage="resolved",
        changed_by=CHANGED_BY,
        change_reason="Widget preview visual attribute verification per owner specification",
    )
    print("  WI-0936 recorded.")

    # ------------------------------------------------------------------
    # TEST-2940: Test artifact for widget preview tests
    # ------------------------------------------------------------------
    print("Recording TEST-2940...")
    kdb.insert_test(
        id="TEST-2940",
        spec_id="SPEC-1614",
        title="Widget preview display value verification (~25 tests)",
        test_type="e2e",
        expected_outcome="All preview visual attributes match config mock data (Playwright assertions PASS)",
        test_file="tests/e2e/test_widget_preview_display_values.py",
        description=(
            "~25 Playwright E2E tests verifying the WidgetPreview component "
            "displays correct visual attributes: light/dark mode backgrounds, "
            "header text, greeting message, avatar initials, online indicator, "
            "quick action pills, input placeholder, branding, and dark mode "
            "toggle reactivity."
        ),
        changed_by=CHANGED_BY,
        change_reason="Widget preview visual attribute verification — test_widget_preview_display_values.py",
    )
    print("  TEST-2940 recorded.")

    # ------------------------------------------------------------------
    # Assign TEST-2940 to PHASE-002 (GOV-13)
    # ------------------------------------------------------------------
    print("\nAssigning TEST-2940 to PHASE-002 (GOV-13)...")
    phase = kdb.get_test_plan_phase("PHASE-002")
    if phase:
        existing_ids = json.loads(phase["test_ids"]) if phase["test_ids"] else []
        if "TEST-2940" not in existing_ids:
            combined = existing_ids + ["TEST-2940"]
            kdb.update_test_plan_phase(
                id="PHASE-002",
                changed_by=CHANGED_BY,
                change_reason="Add TEST-2940 (widget preview visual attribute verification)",
                test_ids=combined,
            )
            print(f"  PHASE-002 updated: {len(existing_ids)} -> {len(combined)} test IDs")
        else:
            print("  TEST-2940 already in PHASE-002")
    else:
        print("  WARNING: PHASE-002 not found!")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Spec:  SPEC-1614 (10 assertions)")
    print(f"  WI:    WI-0936 (resolved)")
    print(f"  Test:  TEST-2940 (1 artifact, ~25 tests)")
    print(f"  Phase: PHASE-002 (assigned per GOV-13)")
    print()


if __name__ == "__main__":
    main()
