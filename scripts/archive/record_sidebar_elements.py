"""Record sidebar navigation testable elements in the Knowledge Database.

Elements inventoried from admin/standalone/layouts/StandaloneLayout.tsx
and verified against the live staging screenshot (S135).

Sidebar sections:
  A: Top Navigation (Dashboard, Inbox, Team members)
  B: AI Configuration Group (header, status badge, 4 nav items, wizard, 3 buttons)
  C: Post-Config Navigation (Integrations, Memory & privacy, Billing)
  D: Footer (product name, version, copyright)
  E: Sidebar Container (dimensions, style)

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
CHANGE_REASON = "S135: Sidebar element inventory per SPEC-1652/1653"

# Dimension shorthand (same labels used across all recording scripts)
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
    # ── Section A: Top Navigation ──────────────────────────────────────
    {
        "id": "EL-sidebar-001", "name": "Dashboard nav item",
        "element_type": "nav_link",
        "expected_behavior": "NavLink: icon + 'Dashboard' label, path=/. Active highlight when on dashboard.",
        "dims": [EXISTS, VALUE, STYLE, URL, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-002", "name": "Inbox nav item",
        "element_type": "nav_link",
        "expected_behavior": "NavLink: icon + 'Inbox' label, path=/inbox. Active highlight when on inbox page.",
        "dims": [EXISTS, VALUE, STYLE, URL, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-003", "name": "Team members nav item",
        "element_type": "nav_link",
        "expected_behavior": (
            "NavLink: icon + 'Team members' label, path=/team. "
            "Only visible to superadmin/admin roles (canSeeConfigGroup gate)."
        ),
        "dims": [EXISTS, VALUE, STYLE, URL, ACTION, SECURITY],
        "page": "StandaloneLayout.tsx",
    },

    # ── Section B: AI Configuration Group ──────────────────────────────
    {
        "id": "EL-sidebar-004", "name": "AI Configuration group container",
        "element_type": "container",
        "expected_behavior": (
            "Box with border, semi-transparent background containing config nav items "
            "and action buttons. Only visible to superadmin/admin roles."
        ),
        "dims": [EXISTS, STYLE, SECURITY],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-005", "name": "AI Configuration group header",
        "element_type": "text",
        "expected_behavior": "Text: 'AI CONFIGURATION' (uppercase, 10px, dimmed)",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-006", "name": "Configuration status badge",
        "element_type": "badge",
        "expected_behavior": (
            "3-state badge: green 'Active' | red 'Inactive' | yellow 'Pending'. "
            "Active=is_active && !pending_changes. Inactive=was active, now deactivated. "
            "Pending=all others."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG, FRESH],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-007", "name": "Agent configuration nav item",
        "element_type": "nav_link",
        "expected_behavior": "NavLink: icon + 'Agent configuration' label, path=/configuration",
        "dims": [EXISTS, VALUE, STYLE, URL, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-008", "name": "Knowledge base nav item",
        "element_type": "nav_link",
        "expected_behavior": "NavLink: icon + 'Knowledge base' label, path=/knowledge-base",
        "dims": [EXISTS, VALUE, STYLE, URL, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-009", "name": "Quick actions nav item",
        "element_type": "nav_link",
        "expected_behavior": "NavLink: icon + 'Quick actions' label, path=/quick-actions",
        "dims": [EXISTS, VALUE, STYLE, URL, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-010", "name": "Widget configuration nav item",
        "element_type": "nav_link",
        "expected_behavior": "NavLink: icon + 'Widget configuration' label, path=/widget",
        "dims": [EXISTS, VALUE, STYLE, URL, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-011", "name": "Setup wizard nav item",
        "element_type": "nav_link",
        "expected_behavior": (
            "NavLink: star icon + 'Setup wizard' label. Clicking re-launches "
            "the onboarding wizard modal (not a route navigation)."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, MODAL],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-012", "name": "Deactivate/Activate button",
        "element_type": "button",
        "expected_behavior": (
            "Compact button: label and color depend on activation state. "
            "Red 'Deactivate' when active+no-pending. Green 'Activate' when can_activate. "
            "Yellow 'Activate' (disabled) when blocked. Triggers POST to toggle activation."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, CONFIG, FAIL],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-013", "name": "Discard button",
        "element_type": "button",
        "expected_behavior": (
            "Compact 'Discard' button: disabled until has_pending_changes=true. "
            "POSTs to /api/config/draft/discard. Loading state shows '...'."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, CONFIG, FAIL, LOAD],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-014", "name": "Roll back button",
        "element_type": "button",
        "expected_behavior": (
            "Compact 'Roll back' button: disabled until active_version >= 2. "
            "Opens RestoreDialog for version rollback."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, MODAL, CONFIG, FAIL],
        "page": "StandaloneLayout.tsx",
    },

    # ── Section C: Post-Config Navigation ──────────────────────────────
    {
        "id": "EL-sidebar-015", "name": "Integrations nav item",
        "element_type": "nav_link",
        "expected_behavior": "NavLink: icon + 'Integrations' label, path=/integrations",
        "dims": [EXISTS, VALUE, STYLE, URL, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-016", "name": "Memory & privacy nav item",
        "element_type": "nav_link",
        "expected_behavior": (
            "NavLink: icon + 'Memory & privacy' label, path=/memory-privacy. "
            "Has minTier='professional' — shows tier badge when tier qualifies."
        ),
        "dims": [EXISTS, VALUE, STYLE, URL, ACTION, CONFIG, SECURITY],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-017", "name": "Professional tier badge on Memory & privacy",
        "element_type": "badge",
        "expected_behavior": (
            "Green badge 'Professional' shown on right side of nav item "
            "when tenant tier >= professional."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-018", "name": "Billing nav item",
        "element_type": "nav_link",
        "expected_behavior": "NavLink: icon + 'Billing' label, path=/billing",
        "dims": [EXISTS, VALUE, STYLE, URL, ACTION],
        "page": "StandaloneLayout.tsx",
    },

    # ── Section D: Footer ──────────────────────────────────────────────
    {
        "id": "EL-sidebar-019", "name": "Footer container",
        "element_type": "container",
        "expected_behavior": (
            "Box at bottom of sidebar with border-top, containing "
            "product name + version + copyright."
        ),
        "dims": [EXISTS, STYLE],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-020", "name": "Product name text",
        "element_type": "text",
        "expected_behavior": "Text: 'Agent Red Customer Experience' (center-aligned, dimmed, xs)",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-021", "name": "Version text",
        "element_type": "text",
        "expected_behavior": (
            "Text: 'v{productVersion}' (center-aligned, dimmed, xs). "
            "Dynamic from x-product-version HTTP response header."
        ),
        "dims": [EXISTS, VALUE, STYLE, FRESH, CONFIG],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-022", "name": "Copyright text",
        "element_type": "text",
        "expected_behavior": (
            "Text: '(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. "
            "All rights reserved.' (2-line, center-aligned, 10px, 0.7 opacity)"
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "StandaloneLayout.tsx",
    },

    # ── Section E: Sidebar Container ───────────────────────────────────
    {
        "id": "EL-sidebar-023", "name": "Sidebar/Navbar container",
        "element_type": "container",
        "expected_behavior": (
            "AppShell.Navbar: full-height left panel with dark background (#0c0a09 chrome), "
            "border-right, scrollable when content overflows."
        ),
        "dims": [EXISTS, STYLE, RESP],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-024", "name": "Active nav item highlight",
        "element_type": "visual_state",
        "expected_behavior": (
            "Currently selected nav item has filled background, left border accent, "
            "and bold text. Determined by current route path matching NavPage.path."
        ),
        "dims": [EXISTS, STYLE, ACTION, CONFIG],
        "page": "StandaloneLayout.tsx",
    },

    # ── Section F: Conditional/Dynamic ─────────────────────────────────
    {
        "id": "EL-sidebar-025", "name": "Nav item icons (all 10 items)",
        "element_type": "icon",
        "expected_behavior": (
            "Each nav item has a unique SVG icon from admin/shared/icons/. "
            "Icons: dashboard, inbox, team, config, knowledge, quickactions, "
            "widget, integrations, memory, billing."
        ),
        "dims": [EXISTS, STYLE],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-sidebar-026", "name": "Role-based item visibility",
        "element_type": "conditional",
        "expected_behavior": (
            "Config group + Team members hidden for 'viewer' role. "
            "canSeeConfigGroup = !userRole || ['superadmin','admin'].includes(userRole)."
        ),
        "dims": [EXISTS, SECURITY, CONFIG],
        "page": "StandaloneLayout.tsx",
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
                subsystem="sidebar",
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

    print(f"\nRecorded {inserted} sidebar elements in KB ({skipped} skipped).")


if __name__ == "__main__":
    main()
