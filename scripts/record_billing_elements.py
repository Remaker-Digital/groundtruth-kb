"""Record Billing page testable elements in the Knowledge Database.

Elements inventoried from:
  - admin/standalone/pages/Billing.tsx (Mantine)
  - admin/shared/BillingPortal.tsx (inline styles)

Sections:
  A: Current Plan Card
  B: Usage Overview Stats
  C: Usage Chart
  D: Active Alerts
  E: Conversation Packs
  F: Add-on Modules
  G: Tier Comparison & Upgrade
  H: Manage Billing (Stripe)
  I: Loading & Error States

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
CHANGE_REASON = "S136: Billing element inventory per SPEC-1652/1653"

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
    # ── Section A: Current Plan Card ─────────────────────────────────────
    {
        "id": "EL-billing-001", "name": "Page title",
        "element_type": "text",
        "expected_behavior": "Text: 'Billing' — page heading.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-002", "name": "Current plan card",
        "element_type": "container",
        "expected_behavior": (
            "Card showing current subscription plan with plan name, tier badge, "
            "billing channel, status, and renewal date."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG, FRESH],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-003", "name": "Plan name",
        "element_type": "text",
        "expected_behavior": "Current plan name text.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-004", "name": "Tier badge",
        "element_type": "badge",
        "expected_behavior": (
            "Color-coded tier badge: Trial, Starter, Professional, Enterprise. "
            "Matches tenant's subscription tier."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-005", "name": "Billing channel display",
        "element_type": "text",
        "expected_behavior": "Shows billing channel: 'Shopify' or 'Stripe'.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-006", "name": "Subscription status badge",
        "element_type": "badge",
        "expected_behavior": (
            "Status badge: green=Active, yellow=Suspended, red=Cancelled, gray=Trial expired."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG, FRESH],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-007", "name": "Renewal date display",
        "element_type": "text",
        "expected_behavior": "Next renewal/billing date formatted.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-008", "name": "Manage subscription button",
        "element_type": "button",
        "expected_behavior": (
            "'Manage subscription' button. Only shown for Stripe-billed tenants. "
            "Opens Stripe billing portal."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, CONFIG],
        "page": "Billing.tsx",
    },

    # ── Section B: Usage Overview Stats ──────────────────────────────────
    {
        "id": "EL-billing-009", "name": "Conversations used stat card",
        "element_type": "stat_card",
        "expected_behavior": (
            "Card showing conversations used with progress ring. "
            "Shows used/total ratio."
        ),
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-010", "name": "Pack balance stat card",
        "element_type": "stat_card",
        "expected_behavior": "Card showing remaining conversation pack balance.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-011", "name": "Current overage stat card",
        "element_type": "stat_card",
        "expected_behavior": "Card showing current overage conversation count.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-012", "name": "Estimated overage cost stat card",
        "element_type": "stat_card",
        "expected_behavior": "Card showing estimated $ cost of overage conversations.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Billing.tsx",
    },

    # ── Section C: Usage Chart ───────────────────────────────────────────
    {
        "id": "EL-billing-013", "name": "Usage area chart",
        "element_type": "chart",
        "expected_behavior": (
            "Recharts AreaChart with 30-day daily conversation volume. "
            "Dual series: red 'Total' and blue 'Billable'. Legend below."
        ),
        "dims": [EXISTS, VALUE, STYLE, FRESH, PERF],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-014", "name": "Chart legend",
        "element_type": "text",
        "expected_behavior": "Legend showing 'Total' (red) and 'Billable' (blue) series labels.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-015", "name": "Chart empty state",
        "element_type": "text",
        "expected_behavior": "Message shown when no usage data available for chart.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Billing.tsx",
    },

    # ── Section D: Active Alerts ─────────────────────────────────────────
    {
        "id": "EL-billing-016", "name": "Usage alert banner",
        "element_type": "alert",
        "expected_behavior": (
            "Alert banner with yellow/error colors. "
            "Dynamic alerts based on usage thresholds (80%, 100%, overage)."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG, FRESH],
        "page": "Billing.tsx",
    },

    # ── Section E: Conversation Packs ────────────────────────────────────
    {
        "id": "EL-billing-017", "name": "Conversation packs section",
        "element_type": "container",
        "expected_behavior": "Section with 3 pack purchase cards.",
        "dims": [EXISTS, STYLE],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-018", "name": "Pack card: 1000 conversations",
        "element_type": "container",
        "expected_behavior": "Card showing 1,000 conversation pack at $29. Rate per conversation displayed.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-019", "name": "Pack card: 5000 conversations",
        "element_type": "container",
        "expected_behavior": "Card showing 5,000 conversation pack at $99.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-020", "name": "Pack card: 20000 conversations",
        "element_type": "container",
        "expected_behavior": "Card showing 20,000 conversation pack at $249.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-021", "name": "Pack purchase button",
        "element_type": "button",
        "expected_behavior": "'Purchase' button on each pack card. Initiates Stripe checkout.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL],
        "page": "Billing.tsx",
    },

    # ── Section F: Add-on Modules ────────────────────────────────────────
    {
        "id": "EL-billing-022", "name": "Add-on modules grid",
        "element_type": "container",
        "expected_behavior": "3-column grid of add-on module cards.",
        "dims": [EXISTS, STYLE, RESP],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-023", "name": "Add-on module card",
        "element_type": "container",
        "expected_behavior": (
            "Card showing module title, description, price/month, "
            "tier requirement badge, and Subscribe button."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-024", "name": "Add-on tier requirement badge",
        "element_type": "badge",
        "expected_behavior": "Badge showing minimum tier required (e.g., 'Professional+', 'Enterprise').",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-025", "name": "Add-on subscribe button",
        "element_type": "button",
        "expected_behavior": "'Subscribe' button. Tier-gated — disabled if tier insufficient.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, CONFIG],
        "page": "Billing.tsx",
    },

    # ── Section G: Tier Comparison & Upgrade ─────────────────────────────
    {
        "id": "EL-billing-026", "name": "Tier comparison section",
        "element_type": "container",
        "expected_behavior": "Section with tier comparison cards for upgrade path.",
        "dims": [EXISTS, STYLE],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-027", "name": "Tier card",
        "element_type": "container",
        "expected_behavior": (
            "Tier card showing: tier name, 'Current plan' badge (if applicable), "
            "monthly/annual price, included conversations, overage rate, "
            "feature list with checkmarks."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-028", "name": "Current plan badge (on tier card)",
        "element_type": "badge",
        "expected_behavior": "'Current plan' badge shown on the card matching tenant's active tier.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-029", "name": "Tier feature list",
        "element_type": "text",
        "expected_behavior": "List of features with checkmark icons for each tier.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-030", "name": "Upgrade button",
        "element_type": "button",
        "expected_behavior": (
            "'Upgrade to [Tier]' button on higher-tier cards. "
            "Hidden on current or lower tiers."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, CONFIG],
        "page": "Billing.tsx",
    },

    # ── Section H: Manage Billing (Stripe) ───────────────────────────────
    {
        "id": "EL-billing-031", "name": "Manage billing section",
        "element_type": "container",
        "expected_behavior": (
            "Section for Stripe-billed tenants to view invoices and update payment methods."
        ),
        "dims": [EXISTS, STYLE, CONFIG],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-032", "name": "Manage billing button",
        "element_type": "button",
        "expected_behavior": "'Manage billing' button opening Stripe customer portal.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, URL],
        "page": "Billing.tsx",
    },

    # ── Section I: Loading & Error States ────────────────────────────────
    {
        "id": "EL-billing-033", "name": "Billing page loading state",
        "element_type": "loader",
        "expected_behavior": "Loading spinner while billing data is fetched from API.",
        "dims": [EXISTS, STYLE, LOAD],
        "page": "Billing.tsx",
    },
    {
        "id": "EL-billing-034", "name": "Billing API error state",
        "element_type": "alert",
        "expected_behavior": "Error banner when billing data fetch fails.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "Billing.tsx",
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
                subsystem="billing",
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

    print(f"\nRecorded {inserted} billing elements in KB ({skipped} skipped).")


if __name__ == "__main__":
    main()
