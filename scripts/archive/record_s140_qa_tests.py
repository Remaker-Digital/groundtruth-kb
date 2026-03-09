"""
Record S140 Quick Actions live E2E test artifacts in KB.
36 tests covering all 32 inventoried elements (EL-quickactions-001..032).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import sys
sys.path.insert(0, "tools/knowledge-db")
import db

d = db.KnowledgeDB()

# Mapping: TEST-ID, title, spec_id, class, function, expected_outcome
TESTS = [
    # TestPageHeader (2 tests)
    ("TEST-3024", "QA page title visible", "SPEC-1652",
     "TestPageHeader", "test_page_title_visible",
     "Page title 'Quick Actions' is visible on the Quick Actions page"),
    ("TEST-3025", "QA page subtitle visible", "SPEC-1652",
     "TestPageHeader", "test_page_subtitle_visible",
     "Subtitle describing quick actions purpose is visible"),

    # TestTabs (3 tests)
    ("TEST-3026", "QA Prompt Library tab visible", "SPEC-1652",
     "TestTabs", "test_prompt_library_tab_visible",
     "Prompt Library tab is visible and contains expected text"),
    ("TEST-3027", "QA Page Assignments tab visible", "SPEC-1652",
     "TestTabs", "test_page_assignments_tab_visible",
     "Page Assignments tab is visible"),
    ("TEST-3028", "QA tab switching works", "SPEC-1652",
     "TestTabs", "test_tab_switching_works",
     "Clicking Page Assignments tab switches content, clicking Prompt Library returns"),

    # TestEmptyState (2 tests)
    ("TEST-3029", "QA empty state message", "SPEC-1652",
     "TestEmptyState", "test_empty_state_message",
     "Empty state message visible when no quick actions exist"),
    ("TEST-3030", "QA starter example buttons", "SPEC-1652",
     "TestEmptyState", "test_starter_example_buttons",
     "Starter example buttons visible in empty state"),

    # TestCreateButton (2 tests)
    ("TEST-3031", "QA create button visible", "SPEC-1652",
     "TestCreateButton", "test_create_button_visible",
     "Create quick action button is visible on page"),
    ("TEST-3032", "QA create button opens modal", "SPEC-1652",
     "TestCreateButton", "test_create_button_opens_modal",
     "Clicking create button opens the action form modal"),

    # TestCreateEditModal (8 tests)
    ("TEST-3033", "QA modal has label input", "SPEC-1652",
     "TestCreateEditModal", "test_modal_has_label_input",
     "Modal contains a text input for action label"),
    ("TEST-3034", "QA modal has prompt textarea", "SPEC-1652",
     "TestCreateEditModal", "test_modal_has_prompt_textarea",
     "Modal contains a textarea for action prompt"),
    ("TEST-3035", "QA modal has template variables", "SPEC-1652",
     "TestCreateEditModal", "test_modal_has_template_variables",
     "Modal shows template variable buttons (customer_name, etc.)"),
    ("TEST-3036", "QA modal has icon input", "SPEC-1652",
     "TestCreateEditModal", "test_modal_has_icon_input",
     "Modal contains an icon/emoji input field"),
    ("TEST-3037", "QA modal has emoji grid", "SPEC-1652",
     "TestCreateEditModal", "test_modal_has_emoji_grid",
     "Modal shows emoji picker grid for icon selection"),
    ("TEST-3038", "QA modal has active toggle", "SPEC-1652",
     "TestCreateEditModal", "test_modal_has_active_toggle",
     "Modal contains an Active switch/toggle"),
    ("TEST-3039", "QA modal has cancel and submit buttons", "SPEC-1652",
     "TestCreateEditModal", "test_modal_has_cancel_and_submit",
     "Modal has Cancel and Create/Save buttons"),
    ("TEST-3040", "QA submit disabled without required fields", "SPEC-1652",
     "TestCreateEditModal", "test_submit_disabled_without_required_fields",
     "Submit button is disabled when label and prompt fields are empty"),

    # TestCreateAction (3 tests)
    ("TEST-3041", "QA create action via modal", "SPEC-1652",
     "TestCreateAction", "test_create_action_via_modal",
     "Creating an action via modal form persists it in the table"),
    ("TEST-3042", "QA create action shows preview", "SPEC-1652",
     "TestCreateAction", "test_create_action_shows_preview",
     "Newly created action shows in prompt preview area"),
    ("TEST-3043", "QA create via starter example", "SPEC-1652",
     "TestCreateAction", "test_create_via_starter_example",
     "Clicking a starter example button creates that action"),

    # TestTableStructure (2 tests)
    ("TEST-3044", "QA table headers present", "SPEC-1652",
     "TestTableStructure", "test_table_headers",
     "Table displays expected column headers (Label, Prompt, Icon, Active, Actions)"),
    ("TEST-3045", "QA action row with data", "SPEC-1652",
     "TestTableStructure", "test_action_row_with_data",
     "Table row displays action label and prompt text"),

    # TestEditAction (2 tests)
    ("TEST-3046", "QA edit button opens modal", "SPEC-1652",
     "TestEditAction", "test_edit_button_opens_modal",
     "Clicking edit icon opens the edit form modal"),
    ("TEST-3047", "QA edit changes label", "SPEC-1652",
     "TestEditAction", "test_edit_changes_label",
     "Editing action label in modal persists the change in table"),

    # TestDeleteAction (2 tests)
    ("TEST-3048", "QA delete button opens confirm dialog", "SPEC-1652",
     "TestDeleteAction", "test_delete_button_opens_confirm_dialog",
     "Clicking delete button opens a confirmation dialog"),
    ("TEST-3049", "QA confirm delete removes action", "SPEC-1652",
     "TestDeleteAction", "test_confirm_delete_removes_action",
     "Confirming delete removes the action from the table"),

    # TestTemplateVariables (1 test)
    ("TEST-3050", "QA variable buttons insert token", "SPEC-1652",
     "TestTemplateVariables", "test_variable_buttons_insert_token",
     "Clicking a template variable button inserts its token into prompt textarea"),

    # TestEmojiGrid (1 test)
    ("TEST-3051", "QA emoji click fills icon", "SPEC-1652",
     "TestEmojiGrid", "test_emoji_click_fills_icon",
     "Clicking an emoji in the grid fills the icon input field"),

    # TestPageAssignmentsTab (5 tests)
    ("TEST-3052", "QA assignments info banner visible", "SPEC-1652",
     "TestPageAssignmentsTab", "test_info_banner_visible",
     "Page Assignments tab shows info/help banner"),
    ("TEST-3053", "QA assignments table has page types", "SPEC-1652",
     "TestPageAssignmentsTab", "test_assignments_table_has_page_types",
     "Assignments table lists page types (Home, Product, Collection, etc.)"),
    ("TEST-3054", "QA slot dropdowns exist", "SPEC-1652",
     "TestPageAssignmentsTab", "test_slot_dropdowns_exist",
     "Each page type row has slot dropdown selectors"),
    ("TEST-3055", "QA auto-open toggles exist", "SPEC-1652",
     "TestPageAssignmentsTab", "test_auto_open_toggles_exist",
     "Each page type row has auto-open toggle switches"),
    ("TEST-3056", "QA delay inputs exist", "SPEC-1652",
     "TestPageAssignmentsTab", "test_delay_inputs_exist",
     "Each page type row has delay number inputs"),

    # TestPageAssignmentMutations (2 tests)
    ("TEST-3057", "QA assign action to slot", "SPEC-1652",
     "TestPageAssignmentMutations", "test_assign_action_to_slot",
     "Selecting an action from a slot dropdown persists the assignment"),
    ("TEST-3058", "QA auto-open toggle mutation", "SPEC-1652",
     "TestPageAssignmentMutations", "test_auto_open_toggle_mutation",
     "Toggling auto-open switch changes its state"),

    # TestActiveToggle (1 test)
    ("TEST-3059", "QA create inactive action", "SPEC-1652",
     "TestActiveToggle", "test_create_inactive_action",
     "Creating an action with Active toggle OFF saves it as inactive"),
]

TEST_FILE = "tests/e2e_live/test_quick_actions_live.py"

print(f"Recording {len(TESTS)} test artifacts (TEST-3024..TEST-3059)...")

for test_id, title, spec_id, test_class, test_func, expected in TESTS:
    result = d.insert_test(
        id=test_id,
        title=title,
        spec_id=spec_id,
        test_type="e2e",
        expected_outcome=expected,
        changed_by="S140",
        change_reason="Quick Actions comprehensive live E2E tests",
        test_file=TEST_FILE,
        test_class=test_class,
        test_function=test_func,
        last_result="pass",
        last_executed_at="2026-03-04",
    )
    print(f"  {test_id}: {title}")

# Assign all to PLAN-001 Phase 3 (live E2E)
conn = d._conn
phase = conn.execute(
    "SELECT rowid, test_ids FROM test_plan_phases WHERE plan_id='PLAN-001' AND phase_number=3 ORDER BY rowid DESC LIMIT 1"
).fetchone()
if phase:
    existing_ids = phase["test_ids"] or ""
    new_ids = ",".join(t[0] for t in TESTS)
    updated = f"{existing_ids},{new_ids}" if existing_ids else new_ids
    conn.execute(
        """INSERT INTO test_plan_phases (plan_id, phase_number, title, description, test_ids, version, changed_by, changed_at, change_reason)
           SELECT plan_id, phase_number, title, description, ?, (SELECT COALESCE(MAX(version),0)+1 FROM test_plan_phases WHERE plan_id='PLAN-001' AND phase_number=3),
                  'S140', datetime('now'), 'Add 36 Quick Actions live E2E tests'
           FROM test_plan_phases WHERE rowid=?""",
        (updated, phase["rowid"])
    )
    conn.commit()
    print(f"\nPLAN-001 Phase 3 updated: +36 tests")

# Summary
summary = d.get_summary()
print(f"\nKB Summary after recording:")
for k, v in summary.items():
    if v and v != "N/A":
        print(f"  {k}: {v}")

print("\nDone.")
