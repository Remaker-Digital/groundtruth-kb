"""Record Memory & Privacy page testable elements in the Knowledge Database.

Elements inventoried from:
  - admin/standalone/pages/MemoryPrivacy.tsx (Mantine)

Sections:
  A: Page Header
  B: Layer 1 — Customer Context
  C: Layer 2 — Conversation Memory
  D: Layer 3 — Cross-Session Learning
  E: Layer 4 — Dedicated Model Training
  F: Customer Identification
  G: Data Retention & Privacy
  H: Actions & Tier Gating

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
CHANGE_REASON = "S136: Memory & Privacy element inventory per SPEC-1652/1653"

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
        "id": "EL-memory-001", "name": "Page title",
        "element_type": "text",
        "expected_behavior": "Text: 'Memory & privacy' — page heading.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "MemoryPrivacy.tsx",
    },

    # ── Section B: Layer 1 — Customer Context ────────────────────────────
    {
        "id": "EL-memory-002", "name": "Layer 1 section header",
        "element_type": "text",
        "expected_behavior": "'Customer Context' section title (Layer 1, all tiers).",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-003", "name": "Layer 1 toggle",
        "element_type": "switch",
        "expected_behavior": (
            "Switch to enable/disable customer context collection. "
            "Available on all tiers. Disabling disables downstream layers."
        ),
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-004", "name": "Layer 1 help tooltip",
        "element_type": "tooltip",
        "expected_behavior": "Help tooltip with documentation link for Layer 1.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "MemoryPrivacy.tsx",
    },

    # ── Section C: Layer 2 — Conversation Memory ─────────────────────────
    {
        "id": "EL-memory-005", "name": "Layer 2 section header",
        "element_type": "text",
        "expected_behavior": "'Conversation Memory' section title (Layer 2, all tiers).",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-006", "name": "Layer 2 toggle",
        "element_type": "switch",
        "expected_behavior": (
            "Switch for conversation memory. Disabled when Layer 1 is off. "
            "Controls within-conversation memory retention."
        ),
        "dims": [EXISTS, VALUE, ACTION, CONFIG],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-007", "name": "Layer 2 help tooltip",
        "element_type": "tooltip",
        "expected_behavior": "Help tooltip for conversation memory.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "MemoryPrivacy.tsx",
    },

    # ── Section D: Layer 3 — Cross-Session Learning ──────────────────────
    {
        "id": "EL-memory-008", "name": "Layer 3 section header",
        "element_type": "text",
        "expected_behavior": "'Cross-Session Learning' section title (Layer 3, Professional+).",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-009", "name": "Layer 3 toggle",
        "element_type": "switch",
        "expected_behavior": (
            "Switch for cross-session learning. "
            "Disabled if tier < Professional."
        ),
        "dims": [EXISTS, VALUE, ACTION, CONFIG, SECURITY],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-010", "name": "Pattern decay slider",
        "element_type": "slider",
        "expected_behavior": (
            "Slider with range 30-365 days with marks. "
            "Controls how long learned patterns persist. "
            "Only shown when Layer 3 is enabled."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG, STYLE],
        "page": "MemoryPrivacy.tsx",
    },

    # ── Section E: Layer 4 — Dedicated Model Training ────────────────────
    {
        "id": "EL-memory-011", "name": "Layer 4 section header",
        "element_type": "text",
        "expected_behavior": "'Dedicated Model Training' section title (Layer 4, Enterprise add-on).",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-012", "name": "Layer 4 fine-tuning toggle",
        "element_type": "switch",
        "expected_behavior": (
            "'Enable fine-tuning' switch. Enterprise tier only. "
            "Disabled for non-Enterprise tenants."
        ),
        "dims": [EXISTS, VALUE, ACTION, CONFIG, SECURITY],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-013", "name": "Training schedule selector",
        "element_type": "segmented_control",
        "expected_behavior": (
            "SegmentedControl: Monthly, Weekly, Manual. "
            "Only shown when fine-tuning is enabled and tier is Enterprise."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-014", "name": "Minimum conversations input",
        "element_type": "input",
        "expected_behavior": "NumberInput for minimum conversations before training starts.",
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-015", "name": "Trigger training button",
        "element_type": "button",
        "expected_behavior": "'Trigger training now' button. Only shown for Enterprise with fine-tuning enabled.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-016", "name": "Active model info alert",
        "element_type": "alert",
        "expected_behavior": "Alert showing active model ID & version when a trained model exists.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-017", "name": "Enterprise upgrade alert",
        "element_type": "alert",
        "expected_behavior": "Blue alert prompting upgrade to Enterprise for fine-tuning access.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "MemoryPrivacy.tsx",
    },

    # ── Section F: Customer Identification ───────────────────────────────
    {
        "id": "EL-memory-018", "name": "Customer identification section header",
        "element_type": "text",
        "expected_behavior": "'Customer Identification' section header (all tiers).",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-019", "name": "Identification level selector",
        "element_type": "segmented_control",
        "expected_behavior": (
            "SegmentedControl: Off, Gentle, Standard, Aggressive. "
            "Controls how aggressively the AI requests customer identity."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-020", "name": "Identification level description",
        "element_type": "text",
        "expected_behavior": "Dynamic description text that changes based on selected level.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-021", "name": "Layer 1 disabled warning",
        "element_type": "alert",
        "expected_behavior": "Warning alert shown when Layer 1 is disabled (identification ineffective).",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "MemoryPrivacy.tsx",
    },

    # ── Section G: Data Retention & Privacy ──────────────────────────────
    {
        "id": "EL-memory-022", "name": "Data retention accordion",
        "element_type": "container",
        "expected_behavior": "Accordion section for data retention and privacy settings.",
        "dims": [EXISTS, STYLE, ACTION],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-023", "name": "Retention period dropdown",
        "element_type": "dropdown",
        "expected_behavior": (
            "Select dropdown: 30 days, 90 days, 180 days, 365 days, 2 years. "
            "Controls data retention period."
        ),
        "dims": [EXISTS, VALUE, INPUT, CONFIG, SECURITY],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-024", "name": "PII scrubbing toggle",
        "element_type": "switch",
        "expected_behavior": "Switch to enable/disable PII scrubbing from stored conversations.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG, SECURITY],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-025", "name": "Consent required toggle",
        "element_type": "switch",
        "expected_behavior": "Switch requiring explicit consent before data collection.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG, SECURITY],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-026", "name": "Automatic deletion toggle",
        "element_type": "switch",
        "expected_behavior": "Switch for automatic data deletion on customer request.",
        "dims": [EXISTS, VALUE, ACTION, CONFIG, SECURITY],
        "page": "MemoryPrivacy.tsx",
    },

    # ── Section H: Actions & Tier Gating ─────────────────────────────────
    {
        "id": "EL-memory-027", "name": "Save draft inputs button",
        "element_type": "button",
        "expected_behavior": "'Save draft inputs' button to persist memory configuration changes.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL, CONFIG],
        "page": "MemoryPrivacy.tsx",
    },
    {
        "id": "EL-memory-028", "name": "Tier upgrade banner",
        "element_type": "alert",
        "expected_behavior": (
            "Upgrade banner shown for sub-Professional tiers. "
            "Prompts upgrade for full memory capabilities."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "MemoryPrivacy.tsx",
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
                subsystem="memory_privacy",
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

    print(f"\nRecorded {inserted} memory & privacy elements in KB ({skipped} skipped).")


if __name__ == "__main__":
    main()
