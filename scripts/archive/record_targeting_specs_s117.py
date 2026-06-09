"""Record targeting rules specifications and tests in KB — S117 Phase 1.

Creates:
- SPEC-1504..1508 (5 specifications with 17 assertions)
- TEST-2677..2685 (9 live E2E test artifacts linked to specs)
- Links WI-0813..0816 to their specs

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
import db  # noqa: E402

kdb = db.KnowledgeDB()

# ===================================================================
# PHASE 1: Specifications
# ===================================================================

print("=== Phase 1: Recording Specifications ===")

# SPEC-1504: Page rule prefix parsing (WI-0813 + WI-0814 core)
kdb.insert_spec(
    id="SPEC-1504",
    handle="page-rule-prefix-parsing",
    title="shouldShowOnPage must parse +/- prefixes for include/exclude semantics",
    section="WIDGET_UI",
    description=(
        "shouldShowOnPage() in widget/src/index.ts must parse + and - prefixes on each rule string. "
        "+ = include, - = exclude, no prefix = include (backward compat). "
        "Precedence: exclude wins over include. Only-excludes = show everywhere except matches. "
        "Only-includes = show only on matches. Both = include unless also excluded. "
        "Empty list = show everywhere (preserved). "
        "Glob pattern is the rule string AFTER stripping the +/- prefix. "
        "Glob * matches any sequence of characters. Glob ? matches any single character. "
        "Regex metacharacters in the pattern (.^${}()|[]) must be escaped before glob conversion."
    ),
    status="specified",
    type="requirement",
    changed_by="S117",
    change_reason="Targeting rules cluster WI-0813+0814. Critical bug: shouldShowOnPage does not parse +/- prefixes.",
    assertions=[
        {
            "id": "SPEC-1504-A1",
            "description": "shouldShowOnPage strips + prefix before building regex",
            "type": "specified",
        },
        {
            "id": "SPEC-1504-A2",
            "description": "shouldShowOnPage strips - prefix before building regex",
            "type": "specified",
        },
        {"id": "SPEC-1504-A3", "description": "Exclude rules take precedence over include rules", "type": "specified"},
        {
            "id": "SPEC-1504-A4",
            "description": "Only-exclude rules show widget everywhere except matches",
            "type": "specified",
        },
        {
            "id": "SPEC-1504-A5",
            "description": "Only-include rules show widget only on matching pages",
            "type": "specified",
        },
        {"id": "SPEC-1504-A6", "description": "Regex metacharacters are escaped in glob patterns", "type": "specified"},
    ],
)
print("  Created SPEC-1504 (prefix parsing, 6 assertions)")

# SPEC-1505: Full URL matching (WI-0814 extended)
kdb.insert_spec(
    id="SPEC-1505",
    handle="page-rule-full-url-matching",
    title="shouldShowOnPage must match against pathname + query string",
    section="WIDGET_UI",
    description=(
        "shouldShowOnPage() must match rules against window.location.pathname + window.location.search "
        "(not just pathname). A rule like -/checkout?step=payment must exclude only that specific URL. "
        "A rule like +/products/* must match /products/blue-widget?variant=123 (glob * matches across ? boundary). "
        "Protocol and hostname are NOT part of the match target."
    ),
    status="specified",
    type="requirement",
    changed_by="S117",
    change_reason="Targeting rules cluster WI-0814 extended. Current code only matches pathname.",
    assertions=[
        {"id": "SPEC-1505-A1", "description": "Match target includes window.location.search", "type": "specified"},
        {"id": "SPEC-1505-A2", "description": "Query-parameterized rules match specific URLs", "type": "specified"},
    ],
)
print("  Created SPEC-1505 (full URL matching, 2 assertions)")

# SPEC-1506: Admin UI page rules (WI-0815)
kdb.insert_spec(
    id="SPEC-1506",
    handle="standalone-admin-page-rules-ui",
    title="Standalone admin Widget page must include page visibility rules UI",
    section="ADMIN_UI",
    description=(
        "admin/standalone/pages/Widget.tsx must include a Page visibility rules section in the Behavior Paper. "
        "UI: section header with help tooltip, list of text inputs (one per rule) with remove buttons, "
        "Add rule button (disabled at 20 rules per fields.yaml max_items), "
        "empty state: No page rules configured. The widget will appear on all pages. "
        "Placeholder: +/products/* or -/checkout. "
        "WidgetConfig interface must include pageRules: string[] (default []). "
        "configToWidgetConfig maps widget_page_rules -> pageRules. "
        "widgetConfigToApiFields maps pageRules -> widget_page_rules."
    ),
    status="specified",
    type="requirement",
    changed_by="S117",
    change_reason="Targeting rules cluster WI-0815. Standalone admin has no page rules UI.",
    assertions=[
        {
            "id": "SPEC-1506-A1",
            "description": "Page visibility rules section visible on Widget page",
            "type": "specified",
        },
        {"id": "SPEC-1506-A2", "description": "Add rule button visible", "type": "specified"},
        {"id": "SPEC-1506-A3", "description": "Empty state message when no rules configured", "type": "specified"},
    ],
)
print("  Created SPEC-1506 (admin page rules UI, 3 assertions)")

# SPEC-1507: Exit-intent trigger (WI-0816a)
kdb.insert_spec(
    id="SPEC-1507",
    handle="widget-exit-intent-trigger",
    title="Widget exit-intent auto-open when mouse leaves viewport",
    section="WIDGET_UI",
    description=(
        "When widget_exit_intent_enabled is true and device is desktop: "
        "listen for mouseleave on document.documentElement. "
        "Auto-open widget when detected and widget is closed. "
        "Fires at most once per page session. Listener removed after trigger. "
        "Must NOT fire if widget was manually opened and closed. "
        "Must NOT fire on mobile. "
        "New field: widget_exit_intent_enabled (boolean, default false) in 4-layer pipeline."
    ),
    status="specified",
    type="requirement",
    changed_by="S117",
    change_reason="Targeting rules cluster WI-0816a. No exit-intent detection exists.",
    assertions=[
        {"id": "SPEC-1507-A1", "description": "mouseleave listener registered on documentElement", "type": "specified"},
        {"id": "SPEC-1507-A2", "description": "Trigger fires at most once (listener removed)", "type": "specified"},
        {
            "id": "SPEC-1507-A3",
            "description": "widget_exit_intent_enabled field in API config response",
            "type": "specified",
        },
    ],
)
print("  Created SPEC-1507 (exit-intent trigger, 3 assertions)")

# SPEC-1508: Scroll-depth trigger (WI-0816b)
kdb.insert_spec(
    id="SPEC-1508",
    handle="widget-scroll-depth-trigger",
    title="Widget scroll-depth auto-open at configured percentage",
    section="WIDGET_UI",
    description=(
        "When widget_scroll_depth_trigger is 1-100: listen for scroll on window. "
        "Auto-open widget when visitor scrolls past configured % of document height and widget is closed. "
        "Fires at most once per page session. Scroll listener removed after trigger. "
        "Must NOT fire if widget was manually opened and closed. "
        "New field: widget_scroll_depth_trigger (integer, default null, min 1, max 100) in 4-layer pipeline."
    ),
    status="specified",
    type="requirement",
    changed_by="S117",
    change_reason="Targeting rules cluster WI-0816b. No scroll-depth detection exists.",
    assertions=[
        {"id": "SPEC-1508-A1", "description": "scroll listener registered on window", "type": "specified"},
        {"id": "SPEC-1508-A2", "description": "Trigger fires at most once (listener removed)", "type": "specified"},
        {
            "id": "SPEC-1508-A3",
            "description": "widget_scroll_depth_trigger field in API config response",
            "type": "specified",
        },
    ],
)
print("  Created SPEC-1508 (scroll-depth trigger, 3 assertions)")

# ===================================================================
# PHASE 1b: Test Artifacts (linked to specs, BEFORE implementation)
# ===================================================================

print("\n=== Phase 1b: Recording Test Artifacts ===")

# Config Pipeline Tests (live httpx)
tests = [
    (
        "TEST-2677",
        "SPEC-1504",
        "widget_page_rules present in admin config API response",
        "e2e",
        "tests/security/test_config_pipeline_live.py",
        "TestPageRulesPipeline",
        "test_page_rules_in_admin_config",
    ),
    (
        "TEST-2678",
        "SPEC-1505",
        "widget_page_rules present in widget-facing config API response",
        "e2e",
        "tests/security/test_config_pipeline_live.py",
        "TestPageRulesPipeline",
        "test_page_rules_in_widget_config",
    ),
    (
        "TEST-2679",
        "SPEC-1507",
        "widget_exit_intent_enabled in config API response",
        "e2e",
        "tests/security/test_config_pipeline_live.py",
        "TestPageRulesPipeline",
        "test_exit_intent_field_in_config",
    ),
    (
        "TEST-2680",
        "SPEC-1508",
        "widget_scroll_depth_trigger in config API response",
        "e2e",
        "tests/security/test_config_pipeline_live.py",
        "TestPageRulesPipeline",
        "test_scroll_depth_field_in_config",
    ),
    # Admin UI Live Tests (Playwright)
    (
        "TEST-2681",
        "SPEC-1506",
        "Page visibility rules section visible on Widget page",
        "e2e",
        "tests/e2e_live/test_widget_live.py",
        "TestPageRulesUI",
        "test_page_rules_section_visible",
    ),
    (
        "TEST-2682",
        "SPEC-1506",
        "Add rule button visible in page rules section",
        "e2e",
        "tests/e2e_live/test_widget_live.py",
        "TestPageRulesUI",
        "test_add_rule_button_visible",
    ),
    (
        "TEST-2683",
        "SPEC-1506",
        "Empty state message when no rules configured",
        "e2e",
        "tests/e2e_live/test_widget_live.py",
        "TestPageRulesUI",
        "test_empty_state_message",
    ),
    (
        "TEST-2684",
        "SPEC-1507",
        "Exit-intent toggle visible in Behavior section",
        "e2e",
        "tests/e2e_live/test_widget_live.py",
        "TestPageRulesUI",
        "test_exit_intent_toggle_visible",
    ),
    (
        "TEST-2685",
        "SPEC-1508",
        "Scroll-depth control visible in Behavior section",
        "e2e",
        "tests/e2e_live/test_widget_live.py",
        "TestPageRulesUI",
        "test_scroll_depth_control_visible",
    ),
]

for test_id, spec_id, title, test_type, test_file, test_class, test_function in tests:
    kdb.insert_test(
        id=test_id,
        title=title,
        spec_id=spec_id,
        test_type=test_type,
        expected_outcome="PASS",
        changed_by="S117",
        change_reason="GOV-10: Live E2E test written BEFORE implementation for targeting rules cluster.",
        test_file=test_file,
        test_class=test_class,
        test_function=test_function,
        last_result="NOT_RUN",
    )
print(f"  Created {len(tests)} test artifacts (TEST-2677..2685)")

# ===================================================================
# PHASE 1c: Link Work Items to Specs
# ===================================================================

print("\n=== Phase 1c: Linking Work Items to Specs ===")

wi_links = [
    ("WI-0813", "Page targeting rules schema fix", "SPEC-1504"),
    ("WI-0814", "shouldShowOnPage full URL matching", "SPEC-1505"),
    ("WI-0815", "Targeting rules admin UI", "SPEC-1506"),
    ("WI-0816", "Exit-intent and scroll-depth triggers", "SPEC-1507"),
]

for wi_id, title, spec_id in wi_links:
    kdb.insert_work_item(
        id=wi_id,
        title=title,
        origin="new",
        component="customer_interface",
        resolution_status="open",
        changed_by="S117",
        change_reason=f"Linked to {spec_id}. Targeting rules cluster — specs and tests created per GOV-10.",
        source_spec_id=spec_id,
    )
print(f"  Updated {len(wi_links)} work items with spec links")

print("\nDone. 5 specs, 9 tests, 4 WI links recorded.")
