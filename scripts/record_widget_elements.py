"""Record Widget Configuration page testable elements in the Knowledge Database.

Elements inventoried from:
  - admin/standalone/pages/Widget.tsx (Mantine)

Sections:
  A: Page Header
  B: Visual Controls — Colors
  C: Visual Controls — Layout & Typography
  D: Visual Controls — Launcher
  E: Behavior Controls
  F: Content Controls — Greeting & Pre-Chat
  G: Content Controls — Header & Agent
  H: Advanced Controls — Targeting & Triggers
  I: Preview Panel
  J: Widget Key & Installation
  K: Loading & Error States

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
CHANGE_REASON = "S136: Widget Configuration element inventory per SPEC-1652/1653"

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
        "id": "EL-widget-001", "name": "Page title",
        "element_type": "text",
        "expected_behavior": "Text: 'Widget configuration' — page heading.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Widget.tsx",
    },

    # ── Section B: Visual Controls — Colors ──────────────────────────────
    {
        "id": "EL-widget-002", "name": "Primary color picker",
        "element_type": "input",
        "expected_behavior": (
            "ColorPicker + hex text input + swatch palette. "
            "Sets widget primary brand color. Propagates to preview."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG, STYLE],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-003", "name": "Header gradient end color picker",
        "element_type": "input",
        "expected_behavior": "Color picker for gradient end color in widget header.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-004", "name": "Header gradient toggle",
        "element_type": "switch",
        "expected_behavior": "Switch to enable/disable gradient on widget header.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-005", "name": "Color mode selector",
        "element_type": "dropdown",
        "expected_behavior": "Dropdown: light, dark, auto. Controls widget color scheme.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },

    # ── Section C: Visual Controls — Layout & Typography ─────────────────
    {
        "id": "EL-widget-006", "name": "Font family selector",
        "element_type": "dropdown",
        "expected_behavior": "Dropdown selecting widget font family.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-007", "name": "Border radius slider",
        "element_type": "slider",
        "expected_behavior": "Slider controlling widget border radius (rounded corners).",
        "dims": [EXISTS, VALUE, INPUT, CONFIG, STYLE],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-008", "name": "Shadow intensity selector",
        "element_type": "dropdown",
        "expected_behavior": "Dropdown: none, subtle, standard, heavy. Controls widget box shadow.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-009", "name": "Panel width selector",
        "element_type": "dropdown",
        "expected_behavior": "Dropdown: compact, standard, wide. Controls widget chat panel width.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-010", "name": "Panel height selector",
        "element_type": "dropdown",
        "expected_behavior": "Dropdown: short, standard, tall. Controls widget chat panel height.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },

    # ── Section D: Visual Controls — Launcher ────────────────────────────
    {
        "id": "EL-widget-011", "name": "Launcher size slider",
        "element_type": "slider",
        "expected_behavior": "Slider controlling the size of the launcher button.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG, STYLE],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-012", "name": "Launcher icon selector",
        "element_type": "dropdown",
        "expected_behavior": "Selector with 3 icon options: chat, headset, help.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-013", "name": "Position selector",
        "element_type": "dropdown",
        "expected_behavior": "Dropdown: bottom-right, bottom-left. Widget placement on page.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-014", "name": "Position offset X input",
        "element_type": "input",
        "expected_behavior": "Number input for horizontal offset from edge in pixels.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-015", "name": "Position offset Y input",
        "element_type": "input",
        "expected_behavior": "Number input for vertical offset from bottom in pixels.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },

    # ── Section E: Behavior Controls ─────────────────────────────────────
    {
        "id": "EL-widget-016", "name": "Locale selector",
        "element_type": "dropdown",
        "expected_behavior": "Dropdown: auto, en, es, fr, de, pt, ja, zh, ko. Widget language.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-017", "name": "Auto open toggle",
        "element_type": "switch",
        "expected_behavior": "Toggle to auto-open the widget on page load.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-018", "name": "Auto open delay slider",
        "element_type": "slider",
        "expected_behavior": "Slider for delay before auto-open in seconds. Hidden if auto-open is off.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-019", "name": "Sound toggle",
        "element_type": "switch",
        "expected_behavior": "Toggle to enable/disable widget notification sounds.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-020", "name": "Mobile fullscreen toggle",
        "element_type": "switch",
        "expected_behavior": "Toggle for fullscreen mode on mobile devices.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-021", "name": "Mobile position selector",
        "element_type": "dropdown",
        "expected_behavior": "Position selector specific to mobile viewport.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-022", "name": "Mobile offset X input",
        "element_type": "input",
        "expected_behavior": "Horizontal offset for mobile position.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-023", "name": "Mobile offset Y input",
        "element_type": "input",
        "expected_behavior": "Vertical offset for mobile position.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },

    # ── Section F: Content Controls — Greeting & Pre-Chat ────────────────
    {
        "id": "EL-widget-024", "name": "Greeting enabled toggle",
        "element_type": "switch",
        "expected_behavior": "Toggle to enable/disable greeting message.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-025", "name": "Greeting mode selector",
        "element_type": "dropdown",
        "expected_behavior": "Dropdown: static, ai_generated. Controls greeting source.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-026", "name": "Greeting message textarea",
        "element_type": "textarea",
        "expected_behavior": (
            "Textarea for static greeting message. Supports template variables. "
            "Preview of rendered template below."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-027", "name": "Pre-chat form toggle",
        "element_type": "switch",
        "expected_behavior": "Toggle to enable/disable pre-chat data collection form.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-028", "name": "Pre-chat field checkboxes",
        "element_type": "input",
        "expected_behavior": (
            "Checkboxes for pre-chat fields: name, email, phone, company. "
            "Selects which fields to show."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-029", "name": "Offline form toggle",
        "element_type": "switch",
        "expected_behavior": "Toggle to enable/disable offline contact form.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "Widget.tsx",
    },

    # ── Section G: Content Controls — Header & Agent ─────────────────────
    {
        "id": "EL-widget-030", "name": "Header title input",
        "element_type": "input",
        "expected_behavior": "Text input for widget header title.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-031", "name": "Header subtitle input",
        "element_type": "input",
        "expected_behavior": "Text input for widget header subtitle.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-032", "name": "Input placeholder input",
        "element_type": "input",
        "expected_behavior": "Text input for message input placeholder text.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-033", "name": "Agent avatar uploader",
        "element_type": "input",
        "expected_behavior": "File upload or URL input for agent avatar image.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-034", "name": "Agent display name input",
        "element_type": "input",
        "expected_behavior": "Text input for agent display name in widget.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },

    # ── Section H: Advanced Controls — Targeting & Triggers ──────────────
    {
        "id": "EL-widget-035", "name": "Page rules editor",
        "element_type": "textarea",
        "expected_behavior": (
            "JSON editor for page targeting rules (include/exclude URL patterns). "
            "Supports +/- prefix syntax."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-036", "name": "Exit intent toggle",
        "element_type": "switch",
        "expected_behavior": "Toggle to enable exit-intent trigger (show widget when user leaves).",
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-037", "name": "Scroll depth trigger",
        "element_type": "input",
        "expected_behavior": "Input for scroll depth percentage that triggers widget appearance.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "Widget.tsx",
    },

    # ── Section I: Preview Panel ─────────────────────────────────────────
    {
        "id": "EL-widget-038", "name": "Widget live preview",
        "element_type": "container",
        "expected_behavior": (
            "Live preview panel showing widget appearance with current settings. "
            "Updates in real-time as controls change."
        ),
        "dims": [EXISTS, STYLE, CONFIG, FRESH],
        "page": "Widget.tsx",
    },

    # ── Section J: Widget Key & Installation ─────────────────────────────
    {
        "id": "EL-widget-039", "name": "Installation code section",
        "element_type": "container",
        "expected_behavior": (
            "Code block showing widget embed script tag with widget key. "
            "Copy-to-clipboard functionality."
        ),
        "dims": [EXISTS, VALUE, STYLE, SECURITY],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-040", "name": "Widget key rotation modal",
        "element_type": "modal",
        "expected_behavior": (
            "Modal for rotating widget key. Warns about breaking existing installations. "
            "Requires confirmation."
        ),
        "dims": [EXISTS, VALUE, STYLE, MODAL, SECURITY],
        "page": "Widget.tsx",
    },

    # ── Section K: Loading & Error States ────────────────────────────────
    {
        "id": "EL-widget-041", "name": "Save loading overlay",
        "element_type": "loader",
        "expected_behavior": "LoadingOverlay shown while widget config is being saved.",
        "dims": [EXISTS, STYLE, LOAD],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-042", "name": "Config load error",
        "element_type": "alert",
        "expected_behavior": "Error state when widget configuration fails to load.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "Widget.tsx",
    },
    {
        "id": "EL-widget-043", "name": "Help tooltips throughout",
        "element_type": "tooltip",
        "expected_behavior": "Help tooltips with ? badges on most configuration controls.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Widget.tsx",
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
                subsystem="widget_config",
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

    print(f"\nRecorded {inserted} widget config elements in KB ({skipped} skipped).")


if __name__ == "__main__":
    main()
