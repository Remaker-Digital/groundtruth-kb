"""Record Knowledge Base page testable elements in the Knowledge Database.

Elements inventoried from:
  - admin/standalone/pages/KnowledgeBase.tsx (Mantine)

Sections:
  A: Page Header & Action Bar
  B: Summary Stat Cards
  C: Knowledge Automation
  D: Articles Table
  E: Add/Edit Article Modal
  F: Import Modal
  G: Conflict Scan Modal
  H: Loading & Empty States

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
CHANGE_REASON = "S136: Knowledge Base element inventory per SPEC-1652/1653"

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
    # ── Section A: Page Header & Action Bar ──────────────────────────────
    {
        "id": "EL-kb-001", "name": "Page title",
        "element_type": "text",
        "expected_behavior": "Text: 'Knowledge base' — page heading.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-002", "name": "Page subtitle",
        "element_type": "text",
        "expected_behavior": "Text: 'Manage articles your AI uses to answer customers' — dimmed.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-003", "name": "Search articles input",
        "element_type": "input",
        "expected_behavior": (
            "TextInput with search icon. Placeholder: 'Search articles...'. "
            "Filters article table in real-time."
        ),
        "dims": [EXISTS, VALUE, STYLE, INPUT, PERF],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-004", "name": "Category filter dropdown",
        "element_type": "dropdown",
        "expected_behavior": (
            "Dropdown with options: All, Policies, Shipping, Products, Sales, "
            "Services, FAQ, Custom. Filters article table."
        ),
        "dims": [EXISTS, VALUE, INPUT, ACTION],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-005", "name": "Status filter dropdown",
        "element_type": "dropdown",
        "expected_behavior": (
            "Dropdown with options: All, Published, Draft, Archived. "
            "Filters articles by publication status."
        ),
        "dims": [EXISTS, VALUE, INPUT, ACTION],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-006", "name": "Scan for conflicts button",
        "element_type": "button",
        "expected_behavior": (
            "Button with tooltip. Triggers conflict scan analysis of KB articles. "
            "Opens conflict scan results modal on completion."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, MODAL, LOAD],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-007", "name": "Export CSV button",
        "element_type": "button",
        "expected_behavior": "Button with tooltip. Downloads KB articles as CSV file.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-008", "name": "Import button",
        "element_type": "button",
        "expected_behavior": "Button with tooltip. Opens import modal for file upload or URL import.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, MODAL],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-009", "name": "Add article button",
        "element_type": "button",
        "expected_behavior": "Blue button with + icon. Opens add article modal.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, MODAL],
        "page": "KnowledgeBase.tsx",
    },

    # ── Section B: Summary Stat Cards ────────────────────────────────────
    {
        "id": "EL-kb-010", "name": "Total articles stat card",
        "element_type": "stat_card",
        "expected_behavior": "Card showing total number of KB articles.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-011", "name": "Published count stat card",
        "element_type": "stat_card",
        "expected_behavior": "Green card showing count of published articles.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-012", "name": "Draft count stat card",
        "element_type": "stat_card",
        "expected_behavior": "Yellow card showing count of draft articles.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-013", "name": "Archived count stat card",
        "element_type": "stat_card",
        "expected_behavior": "Dimmed card showing count of archived articles.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-014", "name": "Needs attention stat card",
        "element_type": "stat_card",
        "expected_behavior": "Red card showing count of articles needing attention (stale/conflicts).",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "KnowledgeBase.tsx",
    },

    # ── Section C: Knowledge Automation ──────────────────────────────────
    {
        "id": "EL-kb-015", "name": "Knowledge automation section",
        "element_type": "container",
        "expected_behavior": (
            "Section titled 'Knowledge automation' with 'Beta' badge. "
            "Collapsible via Show/Hide toggle."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-016", "name": "Scan storefront button",
        "element_type": "button",
        "expected_behavior": "Button to trigger storefront content scanning/import.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-017", "name": "Refresh status button",
        "element_type": "button",
        "expected_behavior": "Button to refresh ingestion status.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-018", "name": "Ingestion progress panel",
        "element_type": "container",
        "expected_behavior": "IngestionPanel showing progress of storefront scanning.",
        "dims": [EXISTS, VALUE, STYLE, LOAD, PERF],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-019", "name": "Category template selector",
        "element_type": "container",
        "expected_behavior": "CategoryTemplateSelector for importing industry-specific article templates.",
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "KnowledgeBase.tsx",
    },

    # ── Section D: Articles Table ────────────────────────────────────────
    {
        "id": "EL-kb-020", "name": "Articles table",
        "element_type": "table",
        "expected_behavior": (
            "Table with columns: Title, Category, Status, Freshness, Last updated, Actions. "
            "Sortable and filterable."
        ),
        "dims": [EXISTS, STYLE, LOAD],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-021", "name": "Article title (table cell)",
        "element_type": "text",
        "expected_behavior": "Article title text. Strikethrough style if archived.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-022", "name": "Article category badge",
        "element_type": "badge",
        "expected_behavior": "Color-coded category badge (Policies, Shipping, Products, etc.).",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-023", "name": "Article status badge",
        "element_type": "badge",
        "expected_behavior": "Color-coded status badge: green=Published, yellow=Draft, gray=Archived.",
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-024", "name": "Article freshness badge",
        "element_type": "badge",
        "expected_behavior": (
            "Freshness indicator: Fresh (green), Aging (yellow), "
            "Stale (orange), Very stale (red)."
        ),
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-025", "name": "Article last updated date",
        "element_type": "text",
        "expected_behavior": "Formatted date of last article update.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-026", "name": "Article verify button",
        "element_type": "button",
        "expected_behavior": "Verify button shown for stale articles. Re-validates content.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-027", "name": "Article edit button",
        "element_type": "button",
        "expected_behavior": "Edit button opening article edit modal.",
        "dims": [EXISTS, STYLE, ACTION, MODAL],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-028", "name": "Article archive/restore button",
        "element_type": "button",
        "expected_behavior": "Toggle: 'Archive' for active articles, 'Restore' for archived.",
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-029", "name": "Empty table message",
        "element_type": "text",
        "expected_behavior": "'No articles match your filters.' when table is empty after filtering.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "KnowledgeBase.tsx",
    },

    # ── Section E: Add/Edit Article Modal ────────────────────────────────
    {
        "id": "EL-kb-030", "name": "Article modal",
        "element_type": "modal",
        "expected_behavior": (
            "Modal for creating or editing KB articles. "
            "Title changes: 'Add article' vs 'Edit article'."
        ),
        "dims": [EXISTS, VALUE, STYLE, MODAL],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-031", "name": "Article title input (modal)",
        "element_type": "input",
        "expected_behavior": "Required text input for article title.",
        "dims": [EXISTS, VALUE, INPUT],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-032", "name": "Article category dropdown (modal)",
        "element_type": "dropdown",
        "expected_behavior": "Required category selector excluding 'All' option.",
        "dims": [EXISTS, VALUE, INPUT],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-033", "name": "Article content textarea (modal)",
        "element_type": "textarea",
        "expected_behavior": "Required textarea for article content. 8+ rows.",
        "dims": [EXISTS, VALUE, INPUT],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-034", "name": "Article status dropdown (modal)",
        "element_type": "dropdown",
        "expected_behavior": "Status selector: Published, Draft, Archived.",
        "dims": [EXISTS, VALUE, INPUT],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-035", "name": "Article modal cancel button",
        "element_type": "button",
        "expected_behavior": "Cancel button closing modal without saving.",
        "dims": [EXISTS, VALUE, ACTION, MODAL],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-036", "name": "Article modal submit button",
        "element_type": "button",
        "expected_behavior": "'Create' or 'Save' button. Submits article form.",
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-037", "name": "Article save error message",
        "element_type": "text",
        "expected_behavior": "Error message shown in modal when save fails.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "KnowledgeBase.tsx",
    },

    # ── Section F: Import Modal ──────────────────────────────────────────
    {
        "id": "EL-kb-038", "name": "Import modal",
        "element_type": "modal",
        "expected_behavior": "Modal with two tabs: 'Upload file' and 'Import URL'.",
        "dims": [EXISTS, VALUE, STYLE, MODAL],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-039", "name": "Upload file tab",
        "element_type": "tab",
        "expected_behavior": (
            "Tab containing drag-and-drop zone accepting .pdf, .docx, .csv, .txt files. "
            "Shows upload progress."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-040", "name": "Import URL tab",
        "element_type": "tab",
        "expected_behavior": "Tab containing URL input and Import button for web scraping.",
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-041", "name": "File drop zone",
        "element_type": "container",
        "expected_behavior": (
            "Drag-and-drop area with icon and instructions. "
            "Hidden file input accepting .pdf/.docx/.csv/.txt."
        ),
        "dims": [EXISTS, STYLE, ACTION, INPUT],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-042", "name": "Upload progress indicator",
        "element_type": "loader",
        "expected_behavior": "Loader + progress bar shown during file upload.",
        "dims": [EXISTS, STYLE, LOAD, PERF],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-043", "name": "URL input for import",
        "element_type": "input",
        "expected_behavior": "Text input for website URL to import from.",
        "dims": [EXISTS, VALUE, INPUT],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-044", "name": "Import success state",
        "element_type": "text",
        "expected_behavior": "Confirmation message with imported entry count and 'Import done' button.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "KnowledgeBase.tsx",
    },

    # ── Section G: Conflict Scan Modal ───────────────────────────────────
    {
        "id": "EL-kb-045", "name": "Conflict scan results modal",
        "element_type": "modal",
        "expected_behavior": "Modal displaying conflict scan results with summary and detail tables.",
        "dims": [EXISTS, VALUE, STYLE, MODAL],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-046", "name": "Scan summary stat cards",
        "element_type": "stat_card",
        "expected_behavior": (
            "4 cards: Entries scanned, With embeddings, Scan time, Issues found."
        ),
        "dims": [EXISTS, VALUE, STYLE, PERF],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-047", "name": "Conflict severity badges",
        "element_type": "badge",
        "expected_behavior": "Badges showing count per severity: high (red), medium (yellow), low (gray).",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "KnowledgeBase.tsx",
    },
    {
        "id": "EL-kb-048", "name": "Conflicts detail table",
        "element_type": "table",
        "expected_behavior": (
            "Table with columns: Entry A, Entry B, Conflict type, Severity, Similarity scores. "
            "Each row includes resolution suggestion."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "KnowledgeBase.tsx",
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
                subsystem="knowledge_base",
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

    print(f"\nRecorded {inserted} knowledge base elements in KB ({skipped} skipped).")


if __name__ == "__main__":
    main()
