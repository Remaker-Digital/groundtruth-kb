"""Record GOV-14: UI element test maintenance directive.

S131: When a UI element is added or removed, the tests which validate
that element must be added or retired accordingly.

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
    # GOV-14: UI element test maintenance
    # ------------------------------------------------------------------
    print("Recording GOV-14...")
    kdb.insert_spec(
        id="GOV-14",
        title="UI element test maintenance — add/retire tests when UI elements change",
        description=(
            "When a new UI element is added to or removed from any admin UI "
            "surface, the tests which validate that element must be added or "
            "retired accordingly. This applies to all dynamic data bindings "
            "(values from API responses rendered in the DOM) and to all static "
            "data (visual labels, tooltips, placeholder text, section headings, "
            "and button text). The display-value verification test suite "
            "(test_*_display_values.py) must stay synchronized with the "
            "rendered UI at all times. Failure to add tests for new elements "
            "constitutes a test coverage gap; failure to retire tests for "
            "removed elements constitutes test drift."
        ),
        status="verified",
        section="GOVERNANCE",
        type="governance",
        assertions=[
            {
                "id": "GOV-14-A1",
                "description": (
                    "Every new UI element (dynamic or static) added to an "
                    "admin page must have a corresponding E2E display-value "
                    "test added in the same session or work item"
                ),
                "type": "manual",
                "status": "verified",
            },
            {
                "id": "GOV-14-A2",
                "description": (
                    "Every UI element removed from an admin page must have "
                    "its corresponding E2E display-value test retired in the "
                    "same session or work item"
                ),
                "type": "manual",
                "status": "verified",
            },
            {
                "id": "GOV-14-A3",
                "description": (
                    "Static UI elements (labels, tooltips, placeholders, "
                    "section headings, button text) are covered by the same "
                    "test maintenance requirement as dynamic data bindings"
                ),
                "type": "manual",
                "status": "verified",
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="Owner directive: UI element changes must trigger test additions/retirements",
    )
    print("  GOV-14 recorded.")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Spec:  GOV-14 (3 assertions, verified)")
    print(f"  Type:  governance")
    print()


if __name__ == "__main__":
    main()
