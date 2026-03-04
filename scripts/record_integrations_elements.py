"""Record Integrations page testable elements in the Knowledge Database.

Elements inventoried from:
  - admin/standalone/pages/Integrations.tsx (Mantine)
  - admin/shared/IntegrationsManager.tsx (inline styles)

Sections:
  A: Page Header
  B: Integration Card Structure
  C: Per-Integration Details
  D: Stripe MCP Credential Management
  E: Status & Tier Gating
  F: Loading & Empty States

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
CHANGE_REASON = "S136: Integrations element inventory per SPEC-1652/1653"

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
    # ── Section A: Page Header ───────────────────────────────────────────
    {
        "id": "EL-integrations-001", "name": "Page title",
        "element_type": "text",
        "expected_behavior": "Text: 'Integrations' — page heading.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Integrations.tsx",
    },

    # ── Section B: Integration Card Structure ────────────────────────────
    {
        "id": "EL-integrations-002", "name": "Integration card",
        "element_type": "container",
        "expected_behavior": (
            "Horizontal card layout (180px logo area left, content right). "
            "One card per integration. Responsive grid."
        ),
        "dims": [EXISTS, STYLE, RESP],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-003", "name": "Integration logo/icon",
        "element_type": "icon",
        "expected_behavior": "80x80px container with integration logo. Fallback SVG if logo missing.",
        "dims": [EXISTS, STYLE],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-004", "name": "Integration name",
        "element_type": "text",
        "expected_behavior": "Integration name with help tooltip.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-005", "name": "Integration description",
        "element_type": "text",
        "expected_behavior": "Short description of what the integration does.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-006", "name": "Connection status badge",
        "element_type": "badge",
        "expected_behavior": (
            "Status badge with colored dot: green='Connected', gray='Disconnected', "
            "red='Error'."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG, FRESH],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-007", "name": "Coming Soon badge",
        "element_type": "badge",
        "expected_behavior": "'Coming Soon' badge shown on unavailable integrations.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-008", "name": "Tier gate badge",
        "element_type": "badge",
        "expected_behavior": "'Professional tier' or 'Enterprise tier' upgrade badge when tier insufficient.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG, SECURITY],
        "page": "Integrations.tsx",
    },

    # ── Section C: Per-Integration Actions ───────────────────────────────
    {
        "id": "EL-integrations-009", "name": "Activate button",
        "element_type": "button",
        "expected_behavior": "'Activate' button shown for disconnected integrations. Triggers connection flow.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-010", "name": "Deactivate button",
        "element_type": "button",
        "expected_behavior": "'Deactivate' button shown for connected integrations.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-011", "name": "Disconnect button",
        "element_type": "button",
        "expected_behavior": (
            "'Disconnect' button for removing integration. "
            "Opens confirmation dialog."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, MODAL],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-012", "name": "Disconnect confirmation dialog",
        "element_type": "modal",
        "expected_behavior": "Confirmation dialog for disconnecting integration.",
        "dims": [EXISTS, VALUE, STYLE, MODAL, ACTION],
        "page": "Integrations.tsx",
    },

    # ── Section D: Stripe MCP Credential Management ──────────────────────
    {
        "id": "EL-integrations-013", "name": "Stripe MCP credential panel",
        "element_type": "container",
        "expected_behavior": (
            "Credential management panel specific to Stripe integration. "
            "Shows MCP connection status and key management."
        ),
        "dims": [EXISTS, VALUE, STYLE, SECURITY, CONFIG],
        "page": "Integrations.tsx",
    },

    # ── Section E: Integration Summary ───────────────────────────────────
    {
        "id": "EL-integrations-014", "name": "Active integration count",
        "element_type": "text",
        "expected_behavior": "'X of Y integrations active' summary footer text.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Integrations.tsx",
    },

    # ── Section F: Per-Integration Cards ─────────────────────────────────
    {
        "id": "EL-integrations-015", "name": "Shopify integration card",
        "element_type": "container",
        "expected_behavior": "Shopify core commerce integration card.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-016", "name": "Zendesk integration card",
        "element_type": "container",
        "expected_behavior": "Zendesk escalation routing integration card.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-017", "name": "Mailchimp integration card",
        "element_type": "container",
        "expected_behavior": "Mailchimp audience sync integration card.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-018", "name": "Google Analytics integration card",
        "element_type": "container",
        "expected_behavior": "Google Analytics event tracking integration card.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Integrations.tsx",
    },
    {
        "id": "EL-integrations-019", "name": "Stripe integration card",
        "element_type": "container",
        "expected_behavior": "Stripe payment integration card with MCP credential panel.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG, SECURITY],
        "page": "Integrations.tsx",
    },

    # ── Section G: Loading States ────────────────────────────────────────
    {
        "id": "EL-integrations-020", "name": "Integrations loading state",
        "element_type": "loader",
        "expected_behavior": "Loading spinner while integration status is fetched.",
        "dims": [EXISTS, STYLE, LOAD],
        "page": "Integrations.tsx",
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
                subsystem="integrations",
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

    print(f"\nRecorded {inserted} integrations elements in KB ({skipped} skipped).")


if __name__ == "__main__":
    main()
