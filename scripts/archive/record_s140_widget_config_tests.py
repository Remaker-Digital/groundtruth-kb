"""
Record S140 Widget Config live E2E test artifacts in KB.
59 tests covering all 43 inventoried elements (EL-widget-001..043).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
import db

d = db.KnowledgeDB()

# Mapping: TEST-ID, title, spec_id, class, function, expected_outcome, last_result
TESTS = [
    # TestPageHeader (2 tests)
    (
        "TEST-3060",
        "WC page title visible",
        "SPEC-1652",
        "TestPageHeader",
        "test_page_title_visible",
        "Page title 'Widget configuration' is visible",
        "pass",
    ),
    (
        "TEST-3061",
        "WC page subtitle visible",
        "SPEC-1652",
        "TestPageHeader",
        "test_page_subtitle_visible",
        "Subtitle about customization is visible",
        "pass",
    ),
    # TestInstallation (7 tests)
    (
        "TEST-3062",
        "WC installation section visible",
        "SPEC-1652",
        "TestInstallation",
        "test_installation_section_visible",
        "Installation section header exists",
        "pass",
    ),
    (
        "TEST-3063",
        "WC widget key displayed",
        "SPEC-1652",
        "TestInstallation",
        "test_widget_key_displayed",
        "Widget key label is displayed in the Installation section",
        "pass",
    ),
    (
        "TEST-3064",
        "WC API URL displayed",
        "SPEC-1652",
        "TestInstallation",
        "test_api_url_displayed",
        "API URL is displayed in the Installation section",
        "pass",
    ),
    (
        "TEST-3065",
        "WC embed code visible",
        "SPEC-1652",
        "TestInstallation",
        "test_embed_code_visible",
        "Embed code snippet or no-widget-key alert is visible",
        "pass",
    ),
    (
        "TEST-3066",
        "WC rotate key button exists",
        "SPEC-1652",
        "TestInstallation",
        "test_rotate_key_button_exists",
        "Rotate key button exists when widget key is present",
        "skip",
    ),
    (
        "TEST-3067",
        "WC rotate key opens modal",
        "SPEC-1652",
        "TestInstallation",
        "test_rotate_key_opens_modal",
        "Clicking Rotate key opens confirmation modal with warning",
        "skip",
    ),
    (
        "TEST-3068",
        "WC copy key button",
        "SPEC-1652",
        "TestInstallation",
        "test_copy_key_button",
        "Copy button or action icon exists near widget key",
        "skip",
    ),
    # TestAppearanceColors (5 tests)
    (
        "TEST-3069",
        "WC primary color picker visible",
        "SPEC-1652",
        "TestAppearanceColors",
        "test_primary_color_picker_visible",
        "Header left color picker label is visible",
        "pass",
    ),
    (
        "TEST-3070",
        "WC gradient end color picker",
        "SPEC-1652",
        "TestAppearanceColors",
        "test_gradient_end_color_picker",
        "Header right color picker label exists",
        "pass",
    ),
    (
        "TEST-3071",
        "WC gradient toggle exists",
        "SPEC-1652",
        "TestAppearanceColors",
        "test_gradient_toggle_exists",
        "Enable header gradient toggle is visible",
        "pass",
    ),
    (
        "TEST-3072",
        "WC color picker has swatches",
        "SPEC-1652",
        "TestAppearanceColors",
        "test_color_picker_has_swatches",
        "Color picker shows swatch palette buttons",
        "pass",
    ),
    (
        "TEST-3073",
        "WC hex input exists",
        "SPEC-1652",
        "TestAppearanceColors",
        "test_hex_input_exists",
        "Hex text input with #RRGGBB placeholder exists",
        "pass",
    ),
    # TestAppearanceControls (11 tests)
    (
        "TEST-3074",
        "WC font family selector",
        "SPEC-1652",
        "TestAppearanceControls",
        "test_font_family_selector",
        "Font family selector label exists",
        "pass",
    ),
    (
        "TEST-3075",
        "WC border radius slider",
        "SPEC-1652",
        "TestAppearanceControls",
        "test_border_radius_slider",
        "Border radius slider with marks exists",
        "pass",
    ),
    (
        "TEST-3076",
        "WC launcher size slider",
        "SPEC-1652",
        "TestAppearanceControls",
        "test_launcher_size_slider",
        "Launcher size slider exists",
        "pass",
    ),
    (
        "TEST-3077",
        "WC launcher icon selector",
        "SPEC-1652",
        "TestAppearanceControls",
        "test_launcher_icon_selector",
        "Launcher icon selector exists",
        "pass",
    ),
    (
        "TEST-3078",
        "WC position segmented control",
        "SPEC-1652",
        "TestAppearanceControls",
        "test_position_segmented_control",
        "Position selector with Bottom right / Bottom left options",
        "pass",
    ),
    (
        "TEST-3079",
        "WC position offset inputs",
        "SPEC-1652",
        "TestAppearanceControls",
        "test_position_offset_inputs",
        "Horizontal and vertical offset inputs exist",
        "pass",
    ),
    (
        "TEST-3080",
        "WC color mode segmented",
        "SPEC-1652",
        "TestAppearanceControls",
        "test_color_mode_segmented",
        "Color mode selector with Light/Dark/Auto options",
        "pass",
    ),
    (
        "TEST-3081",
        "WC panel width segmented",
        "SPEC-1652",
        "TestAppearanceControls",
        "test_panel_width_segmented",
        "Panel width selector label exists",
        "pass",
    ),
    (
        "TEST-3082",
        "WC panel height segmented",
        "SPEC-1652",
        "TestAppearanceControls",
        "test_panel_height_segmented",
        "Panel height selector label exists",
        "pass",
    ),
    (
        "TEST-3083",
        "WC locale selector",
        "SPEC-1652",
        "TestAppearanceControls",
        "test_locale_selector",
        "Widget language selector exists",
        "pass",
    ),
    (
        "TEST-3084",
        "WC shadow intensity segmented",
        "SPEC-1652",
        "TestAppearanceControls",
        "test_shadow_intensity_segmented",
        "Panel shadow selector exists",
        "pass",
    ),
    # TestBehaviorSwitches (11 tests)
    (
        "TEST-3085",
        "WC greeting toggle",
        "SPEC-1652",
        "TestBehaviorSwitches",
        "test_greeting_toggle",
        "Greeting message toggle is visible",
        "pass",
    ),
    (
        "TEST-3086",
        "WC greeting mode selector",
        "SPEC-1652",
        "TestBehaviorSwitches",
        "test_greeting_mode_selector",
        "Greeting mode selector (Static/AI-generated) exists",
        "pass",
    ),
    (
        "TEST-3087",
        "WC greeting message textarea",
        "SPEC-1652",
        "TestBehaviorSwitches",
        "test_greeting_message_textarea",
        "Greeting message textarea exists when greeting enabled",
        "pass",
    ),
    (
        "TEST-3088",
        "WC pre-chat form toggle",
        "SPEC-1652",
        "TestBehaviorSwitches",
        "test_pre_chat_form_toggle",
        "Pre-chat form toggle is visible",
        "pass",
    ),
    (
        "TEST-3089",
        "WC sound toggle",
        "SPEC-1652",
        "TestBehaviorSwitches",
        "test_sound_toggle",
        "Sound notifications toggle is visible",
        "pass",
    ),
    (
        "TEST-3090",
        "WC exit-intent toggle",
        "SPEC-1652",
        "TestBehaviorSwitches",
        "test_exit_intent_toggle",
        "Exit-intent trigger toggle is visible",
        "pass",
    ),
    (
        "TEST-3091",
        "WC scroll depth input",
        "SPEC-1652",
        "TestBehaviorSwitches",
        "test_scroll_depth_input",
        "Scroll-depth trigger input is visible",
        "pass",
    ),
    (
        "TEST-3092",
        "WC mobile fullscreen toggle",
        "SPEC-1652",
        "TestBehaviorSwitches",
        "test_mobile_fullscreen_toggle",
        "Mobile fullscreen toggle is visible",
        "pass",
    ),
    (
        "TEST-3093",
        "WC mobile position selector",
        "SPEC-1652",
        "TestBehaviorSwitches",
        "test_mobile_position_selector",
        "Mobile position override selector is visible",
        "pass",
    ),
    (
        "TEST-3094",
        "WC mobile offset inputs",
        "SPEC-1652",
        "TestBehaviorSwitches",
        "test_mobile_offset_inputs",
        "Mobile horizontal and vertical offset inputs exist",
        "pass",
    ),
    (
        "TEST-3095",
        "WC offline form toggle",
        "SPEC-1652",
        "TestBehaviorSwitches",
        "test_offline_form_toggle",
        "Offline form toggle visible when present on page",
        "skip",
    ),
    # TestPageRules (3 tests)
    (
        "TEST-3096",
        "WC page rules section visible",
        "SPEC-1652",
        "TestPageRules",
        "test_page_rules_section_visible",
        "Page visibility rules section exists",
        "pass",
    ),
    (
        "TEST-3097",
        "WC add rule button exists",
        "SPEC-1652",
        "TestPageRules",
        "test_add_rule_button_exists",
        "'+ Add rule' button exists in page rules section",
        "pass",
    ),
    (
        "TEST-3098",
        "WC add rule creates input",
        "SPEC-1652",
        "TestPageRules",
        "test_add_rule_creates_input",
        "Clicking Add rule creates a URL pattern input field",
        "pass",
    ),
    # TestContentSection (6 tests)
    (
        "TEST-3099",
        "WC content section visible",
        "SPEC-1652",
        "TestContentSection",
        "test_content_section_visible",
        "Content section header exists",
        "pass",
    ),
    (
        "TEST-3100",
        "WC header title input",
        "SPEC-1652",
        "TestContentSection",
        "test_header_title_input",
        "Header title input with 'Support' placeholder exists",
        "pass",
    ),
    (
        "TEST-3101",
        "WC header subtitle input",
        "SPEC-1652",
        "TestContentSection",
        "test_header_subtitle_input",
        "Header subtitle input exists",
        "pass",
    ),
    (
        "TEST-3102",
        "WC input placeholder field",
        "SPEC-1652",
        "TestContentSection",
        "test_input_placeholder_field",
        "Input placeholder field exists",
        "pass",
    ),
    (
        "TEST-3103",
        "WC agent display name input",
        "SPEC-1652",
        "TestContentSection",
        "test_agent_display_name_input",
        "Agent display name input exists",
        "pass",
    ),
    (
        "TEST-3104",
        "WC agent avatar section",
        "SPEC-1652",
        "TestContentSection",
        "test_agent_avatar_section",
        "Agent avatar upload/display section exists",
        "pass",
    ),
    # TestActionButtons (2 tests)
    (
        "TEST-3105",
        "WC save button visible",
        "SPEC-1652",
        "TestActionButtons",
        "test_save_button_visible",
        "Save draft button is visible",
        "pass",
    ),
    (
        "TEST-3106",
        "WC reset button visible",
        "SPEC-1652",
        "TestActionButtons",
        "test_reset_button_visible",
        "Reset to defaults button is visible",
        "pass",
    ),
    # TestHelpTooltips (1 test)
    (
        "TEST-3107",
        "WC help tooltips exist",
        "SPEC-1652",
        "TestHelpTooltips",
        "test_help_tooltips_exist",
        "Multiple help tooltip '?' badges exist on the page",
        "pass",
    ),
    # TestLoadStates (2 tests)
    (
        "TEST-3108",
        "WC loading overlay not stuck",
        "SPEC-1652",
        "TestLoadStates",
        "test_loading_overlay_not_stuck",
        "LoadingOverlay is not visible after page loads",
        "pass",
    ),
    (
        "TEST-3109",
        "WC no error alert on clean load",
        "SPEC-1652",
        "TestLoadStates",
        "test_no_error_alert_on_clean_load",
        "No error alert on fresh page load",
        "pass",
    ),
    # TestMutations (9 tests)
    (
        "TEST-3110",
        "WC toggle gradient",
        "SPEC-1652",
        "TestMutations",
        "test_toggle_gradient",
        "Toggling gradient switch changes state without crashing",
        "pass",
    ),
    (
        "TEST-3111",
        "WC change color mode",
        "SPEC-1652",
        "TestMutations",
        "test_change_color_mode",
        "Switching color mode to Dark works",
        "pass",
    ),
    (
        "TEST-3112",
        "WC change panel width",
        "SPEC-1652",
        "TestMutations",
        "test_change_panel_width",
        "Switching panel width to Wide works",
        "pass",
    ),
    (
        "TEST-3113",
        "WC change position",
        "SPEC-1652",
        "TestMutations",
        "test_change_position",
        "Switching position to Bottom left works",
        "pass",
    ),
    (
        "TEST-3114",
        "WC edit header title",
        "SPEC-1652",
        "TestMutations",
        "test_edit_header_title",
        "Editing header title field persists the value",
        "pass",
    ),
    (
        "TEST-3115",
        "WC edit header subtitle",
        "SPEC-1652",
        "TestMutations",
        "test_edit_header_subtitle",
        "Editing header subtitle field persists the value",
        "pass",
    ),
    (
        "TEST-3116",
        "WC toggle pre-chat form",
        "SPEC-1652",
        "TestMutations",
        "test_toggle_pre_chat_form",
        "Toggling pre-chat form switch works",
        "pass",
    ),
    (
        "TEST-3117",
        "WC pre-chat field chips",
        "SPEC-1652",
        "TestMutations",
        "test_pre_chat_field_chips",
        "Pre-chat field chips (Name, Email, Phone, Company) exist when form enabled",
        "pass",
    ),
    (
        "TEST-3118",
        "WC save draft",
        "SPEC-1652",
        "TestMutations",
        "test_save_draft",
        "Save draft button executes API call successfully",
        "pass",
    ),
]

TEST_FILE = "tests/e2e_live/test_widget_config_live.py"

print(f"Recording {len(TESTS)} test artifacts (TEST-3060..TEST-3118)...")

for test_id, title, spec_id, test_class, test_func, expected, result in TESTS:
    d.insert_test(
        id=test_id,
        title=title,
        spec_id=spec_id,
        test_type="e2e",
        expected_outcome=expected,
        changed_by="S140",
        change_reason="Widget Config comprehensive live E2E tests",
        test_file=TEST_FILE,
        test_class=test_class,
        test_function=test_func,
        last_result=result,
        last_executed_at="2026-03-04",
    )
    print(f"  {test_id}: {title} [{result}]")

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
                  'S140', datetime('now'), 'Add 59 Widget Config live E2E tests'
           FROM test_plan_phases WHERE rowid=?""",
        (updated, phase["rowid"]),
    )
    conn.commit()
    print(f"\nPLAN-001 Phase 3 updated: +59 tests")

# Summary
summary = d.get_summary()
print(f"\nKB Summary after recording:")
for k, v in summary.items():
    if v and v != "N/A":
        print(f"  {k}: {v}")

print("\nDone.")
