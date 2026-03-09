"""Record Agent Configuration page testable elements in the Knowledge Database.

Elements inventoried from:
  - admin/standalone/pages/Configuration.tsx (Mantine)

Sections:
  A: Page Header
  B: Saved Configurations
  C: Brand & Persona
  D: Policies
  E: Escalation Settings
  F: Per-Category Escalation Controls
  G: Custom Instructions & Language
  H: Save Configuration Modal
  I: AI Suggestion Controls
  J: Loading & Error States

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
CHANGE_REASON = "S136: Agent Configuration element inventory per SPEC-1652/1653"

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
        "id": "EL-config-001", "name": "Page title",
        "element_type": "text",
        "expected_behavior": "Text: 'Agent configuration' — page heading.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-002", "name": "Page subtitle",
        "element_type": "text",
        "expected_behavior": "Text: 'Fine-tune your AI agent\\'s behavior' — dimmed subtitle.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Configuration.tsx",
    },

    # ── Section B: Saved Configurations ──────────────────────────────────
    {
        "id": "EL-config-003", "name": "Saved configurations section title",
        "element_type": "text",
        "expected_behavior": "'Saved configurations' section header with help tooltip.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-004", "name": "Save current as button",
        "element_type": "button",
        "expected_behavior": "'Save current as...' button that opens the save configuration modal.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, MODAL],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-005", "name": "Saved configs table",
        "element_type": "table",
        "expected_behavior": (
            "Table with columns: Name, Saved, Fields, Actions. "
            "Shows all saved configurations."
        ),
        "dims": [EXISTS, STYLE, LOAD],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-006", "name": "Config name with Active badge",
        "element_type": "text",
        "expected_behavior": (
            "Configuration name in table row. Active config has green 'Active' badge. "
            "Default config has gray 'Default' badge."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-007", "name": "Config creation timestamp",
        "element_type": "text",
        "expected_behavior": "Formatted timestamp showing when config was saved. Has tooltip with full date.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-008", "name": "Config field count badge",
        "element_type": "badge",
        "expected_behavior": "Badge showing number of fields in the configuration.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-009", "name": "Activate config button",
        "element_type": "button",
        "expected_behavior": "'Activate' button. Shown for non-active configs. POSTs to activate.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, CONFIG, LOAD, FAIL],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-010", "name": "Delete config button",
        "element_type": "button",
        "expected_behavior": (
            "Delete button for saved configs. Hidden for default and active configs. "
            "Opens confirmation."
        ),
        "dims": [EXISTS, STYLE, ACTION, MODAL],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-011", "name": "Active configuration indicator",
        "element_type": "text",
        "expected_behavior": "Text indicating which configuration is currently active.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Configuration.tsx",
    },

    # ── Section C: Brand & Persona ───────────────────────────────────────
    {
        "id": "EL-config-012", "name": "Brand name input",
        "element_type": "input",
        "expected_behavior": (
            "TextInput for brand name. Has AI suggestion badge/button. "
            "Value propagates to widget greeting and agent persona."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-013", "name": "Brand voice textarea",
        "element_type": "textarea",
        "expected_behavior": (
            "Textarea for describing brand voice/personality. Has AI suggestion badge. "
            "Multi-line, resizable."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-014", "name": "Formality dropdown",
        "element_type": "dropdown",
        "expected_behavior": (
            "Select dropdown with options: Casual, Professional, Formal. "
            "Controls AI response tone."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-015", "name": "Response length dropdown",
        "element_type": "dropdown",
        "expected_behavior": (
            "Select dropdown with options: Concise, Moderate, Detailed. "
            "Controls AI response verbosity."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },

    # ── Section D: Policies ──────────────────────────────────────────────
    {
        "id": "EL-config-016", "name": "Return window input",
        "element_type": "input",
        "expected_behavior": (
            "Number input for return policy window with 'days' suffix label. "
            "Numeric validation."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-017", "name": "Refund policy textarea",
        "element_type": "textarea",
        "expected_behavior": "Textarea for refund policy text. Has AI suggestion badge.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-018", "name": "Shipping policy textarea",
        "element_type": "textarea",
        "expected_behavior": "Textarea for shipping policy text. Has AI suggestion badge.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },

    # ── Section E: Escalation Settings ───────────────────────────────────
    {
        "id": "EL-config-019", "name": "Escalation threshold slider",
        "element_type": "slider",
        "expected_behavior": (
            "Slider with range 0-1 and marks at 0, 0.5, 1. "
            "Controls confidence threshold for auto-escalation."
        ),
        "dims": [EXISTS, VALUE, STYLE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-020", "name": "Idle timeout input",
        "element_type": "input",
        "expected_behavior": (
            "Number input for idle conversation timeout in minutes. "
            "Affects when conversations auto-close."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-021", "name": "Max AI turns input",
        "element_type": "input",
        "expected_behavior": (
            "Number input for maximum AI conversation turns before escalation. "
            "Safety limit on AI autonomy."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },

    # ── Section F: Per-Category Escalation Controls ──────────────────────
    {
        "id": "EL-config-022", "name": "Escalation category header (per category)",
        "element_type": "container",
        "expected_behavior": (
            "Expandable header per category (Sales, Support, Service, Account, Technical, General). "
            "Contains: toggle switch, category label, keyword count badge, "
            "email indicator badge, expand/collapse chevron."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-023", "name": "Category toggle switch",
        "element_type": "switch",
        "expected_behavior": "Switch to enable/disable individual escalation category.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-024", "name": "Category keyword count badge",
        "element_type": "badge",
        "expected_behavior": "Badge showing number of keywords configured for this category.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-025", "name": "Category email indicator badge",
        "element_type": "badge",
        "expected_behavior": "Badge indicating if a notification email is configured for this category.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-026", "name": "Category notification email input",
        "element_type": "input",
        "expected_behavior": "Email input in expanded category section for notification delivery.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-027", "name": "Category keywords chips",
        "element_type": "badge",
        "expected_behavior": (
            "Chips/badges displaying configured keywords for each category. "
            "Each chip is removable."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-028", "name": "Reset keywords button",
        "element_type": "button",
        "expected_behavior": "Button to reset keywords to defaults for this category.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-029", "name": "Add keyword input",
        "element_type": "input",
        "expected_behavior": "Text input for adding new keywords. Enter/button to add.",
        "dims": [EXISTS, VALUE, INPUT, ACTION],
        "page": "Configuration.tsx",
    },

    # ── Section G: Custom Instructions & Language ────────────────────────
    {
        "id": "EL-config-030", "name": "Custom instructions textarea",
        "element_type": "textarea",
        "expected_behavior": (
            "Large textarea for custom AI instructions. "
            "Free-form text that gets appended to the system prompt."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-031", "name": "Primary language dropdown",
        "element_type": "dropdown",
        "expected_behavior": "Dropdown to select the primary language for AI responses.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-032", "name": "Supported languages multi-select",
        "element_type": "input",
        "expected_behavior": (
            "Multi-select or chips input for additional supported languages. "
            "Defines which languages the AI can respond in."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Configuration.tsx",
    },

    # ── Section H: Save Configuration Modal ──────────────────────────────
    {
        "id": "EL-config-033", "name": "Save config modal",
        "element_type": "modal",
        "expected_behavior": (
            "Modal titled 'Save configuration as'. Contains name input (64 char max), "
            "warning if name is 'default', Cancel and Save buttons."
        ),
        "dims": [EXISTS, VALUE, STYLE, MODAL],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-034", "name": "Config name input (modal)",
        "element_type": "input",
        "expected_behavior": "Text input for new configuration name. Max 64 characters.",
        "dims": [EXISTS, VALUE, INPUT],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-035", "name": "Default name warning",
        "element_type": "alert",
        "expected_behavior": "Warning text shown when name is 'default' (reserved name).",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-036", "name": "Save modal cancel button",
        "element_type": "button",
        "expected_behavior": "Cancel button in save modal. Closes without saving.",
        "dims": [EXISTS, VALUE, ACTION, MODAL],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-037", "name": "Save modal submit button",
        "element_type": "button",
        "expected_behavior": "'Save' button. Disabled if name is empty. POSTs new config.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL],
        "page": "Configuration.tsx",
    },

    # ── Section I: AI Suggestion Controls ────────────────────────────────
    {
        "id": "EL-config-038", "name": "AI suggestion badge (brand name)",
        "element_type": "button",
        "expected_behavior": (
            "Small badge/button near brand name input for AI-generated suggestion. "
            "Clicking fetches AI-suggested value."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-039", "name": "AI suggestion badge (brand voice)",
        "element_type": "button",
        "expected_behavior": "AI suggestion badge for brand voice textarea.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-040", "name": "AI suggestion badge (refund policy)",
        "element_type": "button",
        "expected_behavior": "AI suggestion badge for refund policy textarea.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-041", "name": "AI suggestion badge (shipping policy)",
        "element_type": "button",
        "expected_behavior": "AI suggestion badge for shipping policy textarea.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD],
        "page": "Configuration.tsx",
    },

    # ── Section J: Loading & Error States ────────────────────────────────
    {
        "id": "EL-config-042", "name": "Configuration loading overlay",
        "element_type": "loader",
        "expected_behavior": "LoadingOverlay shown while configuration is being saved to API.",
        "dims": [EXISTS, STYLE, LOAD],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-043", "name": "Configuration load error",
        "element_type": "alert",
        "expected_behavior": "Error state when configuration fails to load from API.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-044", "name": "Config save success notification",
        "element_type": "alert",
        "expected_behavior": "Success notification after configuration is saved or activated.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Configuration.tsx",
    },
    {
        "id": "EL-config-045", "name": "Draft auto-save indicator",
        "element_type": "text",
        "expected_behavior": (
            "Indicator showing that changes are being tracked as draft. "
            "Links to sidebar Discard/Activate buttons for draft management."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Configuration.tsx",
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
                subsystem="config",
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

    print(f"\nRecorded {inserted} config elements in KB ({skipped} skipped).")


if __name__ == "__main__":
    main()
