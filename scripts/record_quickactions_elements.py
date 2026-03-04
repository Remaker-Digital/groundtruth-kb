"""Record Quick Actions page testable elements in the Knowledge Database.

Elements inventoried from:
  - admin/standalone/pages/QuickActions.tsx (Mantine)

Sections:
  A: Page Header & Tabs
  B: Prompt Library Tab
  C: Quick Action Table
  D: Create/Edit Modal
  E: Delete Confirmation
  F: Page Assignments Tab
  G: Empty States

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))

from db import KnowledgeDB

kb = KnowledgeDB()

CHANGED_BY = "Claude"
CHANGE_REASON = "S136: Quick Actions element inventory per SPEC-1652/1653"

# Dimension shorthand
EXISTS = "exists"
VALUE = "correct_value"
STYLE = "correct_style"
ACTION = "action_works"
FRESH = "freshness"
RESP = "responsive"
FAIL = "failure_mode"
LOAD = "load_behavior"
URL = "correct_url"
MODAL = "modal_behavior"
INPUT = "input_behavior"
CONFIG = "config_propagation"
SECURITY = "security"
PERF = "performance"

# fmt: off
ELEMENTS = [
    # ── Section A: Page Header & Tabs ────────────────────────────────────
    {
        "id": "EL-quickactions-001", "name": "Page title",
        "element_type": "text",
        "expected_behavior": "Text: 'Quick actions' — page heading.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-002", "name": "Page subtitle",
        "element_type": "text",
        "expected_behavior": (
            "Text: 'Manage contextual prompt buttons that appear in the chat widget' — dimmed."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-003", "name": "Prompt library tab",
        "element_type": "tab",
        "expected_behavior": "'Prompt library (N)' tab showing count of quick actions. Default active.",
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-004", "name": "Page assignments tab",
        "element_type": "tab",
        "expected_behavior": "'Page assignments' tab for managing which actions appear on which pages.",
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "QuickActions.tsx",
    },

    # ── Section B: Prompt Library Tab ────────────────────────────────────
    {
        "id": "EL-quickactions-005", "name": "Create quick action button",
        "element_type": "button",
        "expected_behavior": "Blue 'Create quick action' button. Opens create modal.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, MODAL],
        "page": "QuickActions.tsx",
    },

    # ── Section C: Quick Action Table ────────────────────────────────────
    {
        "id": "EL-quickactions-006", "name": "Quick actions table",
        "element_type": "table",
        "expected_behavior": "Table with columns: Icon, Label, Prompt template, Status, Actions.",
        "dims": [EXISTS, STYLE, LOAD],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-007", "name": "Action icon cell",
        "element_type": "text",
        "expected_behavior": "Emoji icon display or dash (—) if no icon set.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-008", "name": "Action label cell",
        "element_type": "text",
        "expected_behavior": "Quick action label text.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-009", "name": "Action prompt template cell",
        "element_type": "text",
        "expected_behavior": "Prompt template text truncated to 2 lines.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-010", "name": "Action status badge",
        "element_type": "badge",
        "expected_behavior": "Badge: green 'Active' or gray 'Inactive'.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-011", "name": "Edit action button",
        "element_type": "button",
        "expected_behavior": "Edit icon button opening edit modal for the action.",
        "dims": [EXISTS, STYLE, ACTION, MODAL],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-012", "name": "Delete action button",
        "element_type": "button",
        "expected_behavior": "Delete icon button opening delete confirmation modal.",
        "dims": [EXISTS, STYLE, ACTION, MODAL],
        "page": "QuickActions.tsx",
    },

    # ── Section D: Create/Edit Modal ─────────────────────────────────────
    {
        "id": "EL-quickactions-013", "name": "Create/Edit modal",
        "element_type": "modal",
        "expected_behavior": (
            "Modal titled 'Create quick action' or 'Edit quick action'. "
            "Contains label, template, icon, active toggle, preview."
        ),
        "dims": [EXISTS, VALUE, STYLE, MODAL],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-014", "name": "Button label input",
        "element_type": "input",
        "expected_behavior": "Text input for quick action label. Max 100 characters.",
        "dims": [EXISTS, VALUE, INPUT],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-015", "name": "Prompt template textarea",
        "element_type": "textarea",
        "expected_behavior": "Textarea for prompt template. 2-8 rows, max 2000 characters.",
        "dims": [EXISTS, VALUE, INPUT],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-016", "name": "Template variable buttons",
        "element_type": "button",
        "expected_behavior": (
            "Grid of 6 variable insert buttons: {{page_type}}, {{page_handle}}, "
            "{{page_title}}, {{page_url}}, {{product_title}}, {{collection_title}}. "
            "Clicking inserts variable into template."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-017", "name": "Icon input",
        "element_type": "input",
        "expected_behavior": "Optional text input for custom emoji/icon.",
        "dims": [EXISTS, VALUE, INPUT],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-018", "name": "Emoji quick-select grid",
        "element_type": "container",
        "expected_behavior": (
            "Grid of 12 preset emojis for quick selection. "
            "Clicking sets the icon field."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-019", "name": "Active toggle switch",
        "element_type": "switch",
        "expected_behavior": "Toggle switch for activating/deactivating the quick action.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-020", "name": "Action preview pill",
        "element_type": "container",
        "expected_behavior": "Inline pill preview showing icon + label as they'll appear in widget.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-021", "name": "Modal cancel button",
        "element_type": "button",
        "expected_behavior": "Cancel button closing modal.",
        "dims": [EXISTS, VALUE, ACTION, MODAL],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-022", "name": "Modal submit button",
        "element_type": "button",
        "expected_behavior": "'Create' or 'Save' button. Submits quick action form.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL],
        "page": "QuickActions.tsx",
    },

    # ── Section E: Delete Confirmation ───────────────────────────────────
    {
        "id": "EL-quickactions-023", "name": "Delete confirmation modal",
        "element_type": "modal",
        "expected_behavior": (
            "Modal titled 'Delete quick action'. Shows action label in confirmation text. "
            "Cancel and Delete buttons."
        ),
        "dims": [EXISTS, VALUE, STYLE, MODAL],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-024", "name": "Delete confirm button",
        "element_type": "button",
        "expected_behavior": "Red 'Delete' button confirming deletion.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, FAIL],
        "page": "QuickActions.tsx",
    },

    # ── Section F: Page Assignments Tab ──────────────────────────────────
    {
        "id": "EL-quickactions-025", "name": "Page assignments info banner",
        "element_type": "alert",
        "expected_behavior": "'How page assignments work' info banner with description.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-026", "name": "Assignments table",
        "element_type": "table",
        "expected_behavior": (
            "Table with columns: Page type, Slot 1, Slot 2, Auto-open, Delay (s). "
            "9 page types: All pages, Home, Product, Collection, Cart, Search, Blog, Page, Other."
        ),
        "dims": [EXISTS, STYLE],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-027", "name": "Page type badge",
        "element_type": "badge",
        "expected_behavior": "Badge showing Shopify page type (Home, Product, Collection, etc.).",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-028", "name": "Slot dropdown (per row)",
        "element_type": "dropdown",
        "expected_behavior": (
            "Dropdown to assign a quick action to slot 1 or slot 2. "
            "Lists all actions + 'None' option."
        ),
        "dims": [EXISTS, VALUE, INPUT, ACTION, CONFIG],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-029", "name": "Auto-open toggle (per row)",
        "element_type": "switch",
        "expected_behavior": "Toggle to enable auto-opening the assigned quick action on page load.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-030", "name": "Auto-open delay input (per row)",
        "element_type": "input",
        "expected_behavior": (
            "Number input for delay in seconds (1-60). "
            "Disabled when auto-open is off."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "QuickActions.tsx",
    },

    # ── Section G: Empty States ──────────────────────────────────────────
    {
        "id": "EL-quickactions-031", "name": "Empty prompt library state",
        "element_type": "container",
        "expected_behavior": (
            "'No quick actions yet...' message with grid of 4 starter examples: "
            "Track my order, Return policy, Product recommendations, Help with my order. "
            "Clicking adds the example."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "QuickActions.tsx",
    },
    {
        "id": "EL-quickactions-032", "name": "Starter example buttons",
        "element_type": "button",
        "expected_behavior": (
            "4 preset buttons with emoji + label. Clicking auto-creates a quick action."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "QuickActions.tsx",
    },
]
# fmt: on


def main():
    inserted = 0
    skipped = 0

    for el in ELEMENTS:
        try:
            kb.insert_testable_element(
                id=el["id"],
                subsystem="quick_actions",
                page_or_module=el["page"],
                name=el["name"],
                element_type=el["element_type"],
                expected_behavior=el["expected_behavior"],
                applicable_dimensions=el["dims"],
                changed_by=CHANGED_BY,
                change_reason=CHANGE_REASON,
            )
            inserted += 1
            print(f"  {el['id']}: {el['name']}")
        except Exception as exc:
            if "UNIQUE constraint" in str(exc):
                skipped += 1
                print(f"  {el['id']}: (already exists, skipped)")
            else:
                raise

    print(f"\nRecorded {inserted} quick actions elements in KB ({skipped} skipped).")


if __name__ == "__main__":
    main()
