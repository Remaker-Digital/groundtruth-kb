"""Record all testable elements for the sticky top navbar.

S135: SPEC-1652/1653 — Closed-loop quality process element inventory.
Covers StandaloneLayout.tsx header (lines 675-828).

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
CHANGE_REASON = "S135: Navbar element inventory per SPEC-1652/1653"

# Dimension shorthand
EXISTS = "exists"
VALUE = "correct_value"
STYLE = "correct_style"
ACTION = "action_works"
FAIL = "failure_mode"

ELEMENTS = [
    # ── Container ────────────────────────────────
    {
        "id": "EL-navbar-001",
        "name": "Navbar Container",
        "element_type": "layout",
        "expected_behavior": "AppShell.Header: height 56px, full width, sticky top, dark background (#0c0a09 dark / white light), border-bottom 1px solid border color, padding inline, margin 0.",
        "dims": [EXISTS, STYLE],
        "page": "StandaloneLayout.tsx",
    },
    # ── Left Section ─────────────────────────────
    {
        "id": "EL-navbar-002",
        "name": "Hamburger Menu Button",
        "element_type": "button",
        "expected_behavior": "Burger icon, hidden on desktop (hiddenFrom='sm'), visible on mobile/tablet. Clicking toggles sidebar.",
        "dims": [EXISTS, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-003",
        "name": "Logo Image",
        "element_type": "image",
        "expected_behavior": "SVG logo from /admin/standalone/primary-logo-no-wordmark.svg. Height 28px. Alt text 'Agent Red'.",
        "dims": [EXISTS, VALUE],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-004",
        "name": "Brand Text - Customer Experience",
        "element_type": "text",
        "expected_behavior": "Text 'Customer Experience'. Size sm, font-weight 500, color gray.4, letter-spacing 0.02em.",
        "dims": [EXISTS, VALUE],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-005",
        "name": "Logo + Brand Tooltip",
        "element_type": "tooltip",
        "expected_behavior": "Tooltip 'Agent Red Customer Experience' on hover over logo area. 500ms open delay.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    # ── Right Section ────────────────────────────
    {
        "id": "EL-navbar-006",
        "name": "Storefront Link (Shopify)",
        "element_type": "link",
        "expected_behavior": "Visible when tenant has shopDomain. Links to https://{shopDomain} in new tab. Shows storefront icon + stripped domain name (minus .myshopify.com) + external link icon. Tooltip 'Open {shopDomain}'. Max-width 180px, ellipsis overflow.",
        "dims": [EXISTS, VALUE, ACTION, FAIL],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-007",
        "name": "Brand Name (non-Shopify)",
        "element_type": "text",
        "expected_behavior": "Visible when tenant has brandName but no shopDomain. Non-clickable span with storefront icon + brand name. No external link icon.",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-008",
        "name": "Tier Badge",
        "element_type": "badge",
        "expected_behavior": "Shows tenant tier: Trial (yellow), Starter (blue), Professional (green), Enterprise (grape). Size sm, variant light. Tooltip shows current plan + pricing for all 3 paid tiers.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-009",
        "name": "Documentation Button",
        "element_type": "button",
        "expected_behavior": "ActionIcon with docs/book icon. aria-label 'Open documentation'. Clicking opens https://agentredcx.com in new tab. Tooltip 'Documentation'.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-010",
        "name": "Contact Us Button",
        "element_type": "button",
        "expected_behavior": "ActionIcon with message bubble icon. aria-label 'Contact us'. Clicking opens Contact Us modal. Tooltip 'Contact us'.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-011",
        "name": "Dark Mode Toggle",
        "element_type": "button",
        "expected_behavior": "ActionIcon that toggles color scheme. Shows sun icon in dark mode, moon icon in light mode. aria-label 'Toggle dark mode'. Clicking switches theme.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-012",
        "name": "Sign Out Button",
        "element_type": "button",
        "expected_behavior": "ActionIcon with logout/arrow-out icon. aria-label 'Sign out'. Clicking calls onLogout callback.",
        "dims": [EXISTS, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    # ── Contact Us Modal (triggered from navbar) ──
    {
        "id": "EL-navbar-013",
        "name": "Contact Modal - Topic Select",
        "element_type": "input",
        "expected_behavior": "Select dropdown with options: support, feature_request, billing, bug_report, general. Default: support.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-014",
        "name": "Contact Modal - Subject Input",
        "element_type": "input",
        "expected_behavior": "TextInput, placeholder 'Brief summary of your message', max 200 chars.",
        "dims": [EXISTS, VALUE],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-015",
        "name": "Contact Modal - Message Textarea",
        "element_type": "input",
        "expected_behavior": "Textarea, placeholder 'Describe your request in detail...', min 4 rows, max 8 rows, max 5000 chars.",
        "dims": [EXISTS, VALUE],
        "page": "StandaloneLayout.tsx",
    },
    {
        "id": "EL-navbar-016",
        "name": "Contact Modal - Submit Button",
        "element_type": "button",
        "expected_behavior": "Disabled when any field is empty. Enabled when all filled. POSTs to /api/admin/contact. Shows loading state during send. Resets form on success.",
        "dims": [EXISTS, VALUE, ACTION, FAIL],
        "page": "StandaloneLayout.tsx",
    },
]


def main():
    inserted = 0
    skipped = 0

    for el in ELEMENTS:
        existing = kb.get_testable_element(el["id"])
        if existing:
            skipped += 1
            continue

        kb.insert_testable_element(
            id=el["id"],
            subsystem="navbar",
            page_or_module=el["page"],
            name=el["name"],
            element_type=el["element_type"],
            expected_behavior=el["expected_behavior"],
            applicable_dimensions=el["dims"],
            changed_by=CHANGED_BY,
            change_reason=CHANGE_REASON,
        )
        inserted += 1

    coverage = kb.get_element_coverage_summary()
    print(f"Inserted: {inserted}, Skipped: {skipped}")
    for sub in coverage["subsystems"]:
        print(f"  {sub['subsystem']}: {sub['total']} elements ({sub['active']} active)")
    print(f"Total elements: {coverage['total_elements']}")


if __name__ == "__main__":
    main()
