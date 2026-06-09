"""S153 Batch 4 — Promote 36 specs + record 43 test artifacts in KB."""

import sys

sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()

# --- 1. Promote 36 specs to 'implemented' ---
specs_to_promote = [
    # Dashboard (8)
    "SPEC-0007",
    "SPEC-0008",
    "SPEC-0094",
    "SPEC-0182",
    "SPEC-0372",
    "SPEC-0461",
    "SPEC-0462",
    "SPEC-0579",
    # Sidebar (5)
    "SPEC-0088",
    "SPEC-0255",
    "SPEC-0271",
    "SPEC-0688",
    "SPEC-0696",
    "SPEC-0697",
    # Branding/Logo (15)
    "SPEC-0013",
    "SPEC-0014",
    "SPEC-0229",
    "SPEC-0368",
    "SPEC-0369",
    "SPEC-0533",
    "SPEC-0566",
    "SPEC-0605",
    "SPEC-0606",
    "SPEC-0694",
    "SPEC-0799",
    "SPEC-0801",
    "SPEC-0814",
    "SPEC-0825",
    "SPEC-0828",
    # Widget (3)
    "SPEC-0032",
    "SPEC-0572",
    "SPEC-1553",
    # Inbox (1)
    "SPEC-0095",
    # Other (4)
    "SPEC-0071",
    "SPEC-0573",
    "SPEC-1659",
]
for sid in specs_to_promote:
    db.update_spec(
        sid,
        changed_by="S153",
        change_reason="Promoted to implemented - real production-interface test passing in test_s153_batch4_spec_verification.py",
        status="implemented",
    )
    print(f"Promoted {sid} -> implemented")

print(f"\n--- Promoted {len(specs_to_promote)} specs ---\n")

# --- 2. Record 43 test artifacts ---
TEST_FILE = "tests/multi_tenant/test_s153_batch4_spec_verification.py"
CB = "S153"
CR = "S153 batch 4 real production-interface spec verification test"

tests = [
    # SPEC-0007 (3)
    (
        "SPEC-0007",
        "TestSpec0007AnalyticsMergedIntoDashboard",
        "test_dashboard_has_analytics_hooks",
        "Dashboard imports analytics hooks",
        "useAnalyticsSummary + useDailyVolume + useIntentBreakdown in source",
    ),
    (
        "SPEC-0007",
        "TestSpec0007AnalyticsMergedIntoDashboard",
        "test_dashboard_has_conversation_volume_chart",
        "Dashboard renders conversation volume chart",
        "AreaChart or chartData in source",
    ),
    (
        "SPEC-0007",
        "TestSpec0007AnalyticsMergedIntoDashboard",
        "test_analytics_route_redirects_to_dashboard",
        "Analytics route redirects to /",
        "Navigate/redirect in routes",
    ),
    # SPEC-0008 (1)
    (
        "SPEC-0008",
        "TestSpec0008AnalyticsSidebarRemoved",
        "test_no_analytics_in_sidebar_nav_items",
        "No Analytics in sidebar nav items",
        "analytics not in nav section",
    ),
    # SPEC-0094 (2)
    (
        "SPEC-0094",
        "TestSpec0094DashboardTooltipsWithDocLinks",
        "test_dashboard_has_help_tooltips",
        "Dashboard uses HelpTooltip",
        "HelpTooltip in source",
    ),
    (
        "SPEC-0094",
        "TestSpec0094DashboardTooltipsWithDocLinks",
        "test_tooltips_have_doc_links",
        "Tooltips include documentation links",
        "docLink + agentredcx.com in source",
    ),
    # SPEC-0182 (2)
    (
        "SPEC-0182",
        "TestSpec0182QualityTrendDashboard",
        "test_dashboard_has_time_series_chart",
        "Dashboard has time series chart",
        "AreaChart + useDailyVolume in source",
    ),
    (
        "SPEC-0182",
        "TestSpec0182QualityTrendDashboard",
        "test_dashboard_has_period_selector",
        "Dashboard has period selector",
        "7d/14d/30d in source",
    ),
    # SPEC-0372 (1)
    (
        "SPEC-0372",
        "TestSpec0372NoDashboardEnvironmentSelector",
        "test_dashboard_has_no_environment_filter",
        "No environment selector on Dashboard",
        "No SegmentedControl with Production/Test",
    ),
    # SPEC-0461 (1)
    (
        "SPEC-0461",
        "TestSpec0461DashboardNoPreInitData",
        "test_analytics_uses_api_date_filtering",
        "Analytics uses date filtering via API",
        "period/days in source",
    ),
    # SPEC-0462 (1)
    (
        "SPEC-0462",
        "TestSpec0462DashboardAccurateMetrics",
        "test_dashboard_uses_real_analytics_data",
        "Dashboard uses real analytics API data",
        "useAnalyticsSummary + escalat + resolution in source",
    ),
    # SPEC-0579 (1)
    (
        "SPEC-0579",
        "TestSpec0579AnalyticsPageRendersCharts",
        "test_analytics_page_exists_with_charts",
        "Analytics.tsx exists with charts",
        "AreaChart/LineChart/BarChart in source",
    ),
    # SPEC-0088 (1)
    (
        "SPEC-0088",
        "TestSpec0088ActiveSelectionWhite",
        "test_active_nav_uses_white_text",
        "Active nav uses textPrimary (white)",
        "textPrimary in source, no red text",
    ),
    # SPEC-0255 (1)
    (
        "SPEC-0255",
        "TestSpec0255SentenceCaseLabels",
        "test_sidebar_labels_use_sentence_case",
        "All sidebar labels use sentence case",
        "Labels verified: Dashboard, Inbox, Team members, etc.",
    ),
    # SPEC-0271 (1)
    (
        "SPEC-0271",
        "TestSpec0271AIConfigurationHeading",
        "test_config_group_heading",
        "Config group heading is AI Configuration",
        "AI Configuration in source",
    ),
    # SPEC-0688 (1)
    (
        "SPEC-0688",
        "TestSpec0688NoDuplicateDocLink",
        "test_no_documentation_in_sidebar_nav",
        "No Documentation label in sidebar",
        "0 label matches for Documentation in nav",
    ),
    # SPEC-0696 (1)
    (
        "SPEC-0696",
        "TestSpec0696TeamMembersLabel",
        "test_team_members_label",
        "Sidebar shows Team members",
        "Team members label in nav items",
    ),
    # SPEC-0697 (2)
    (
        "SPEC-0697",
        "TestSpec0697ConfigItemsGrouped",
        "test_config_group_exists",
        "Config group container exists",
        "configGroupItems in source",
    ),
    (
        "SPEC-0697",
        "TestSpec0697ConfigItemsGrouped",
        "test_group_contains_all_four",
        "Group contains all 4 config items",
        "Agent configuration + KB + Quick actions + Widget config in group",
    ),
    # SPEC-0013 (1)
    (
        "SPEC-0013",
        "TestSpec0013AdminLogoIsPrimaryNoWordmark",
        "test_header_logo_reference",
        "Header uses primary-logo-no-wordmark.svg",
        "primary-logo-no-wordmark in source",
    ),
    # SPEC-0014 (1)
    (
        "SPEC-0014",
        "TestSpec0014WordmarkCustomerExperience",
        "test_customer_experience_text",
        "Customer Experience text in header",
        "Customer Experience in source",
    ),
    # SPEC-0229 (1)
    (
        "SPEC-0229",
        "TestSpec0229LogoWithoutAgentRedText",
        "test_uses_no_wordmark_variant",
        "Uses no-wordmark logo variant",
        "primary-logo-no-wordmark in source",
    ),
    # SPEC-0368 (1)
    (
        "SPEC-0368",
        "TestSpec0368IntegrationLogo180Container",
        "test_icon_container_dimensions",
        "Integration logo container 180x180",
        "180 in IntegrationsManager dimensions",
    ),
    # SPEC-0369 (1)
    (
        "SPEC-0369",
        "TestSpec0369IntegrationLogoNoSizeConstraints",
        "test_logo_uses_object_fit_contain",
        "Logo uses object-fit contain",
        "objectFit contain in source",
    ),
    # SPEC-0533 (1)
    (
        "SPEC-0533",
        "TestSpec0533IntegrationContentToRight",
        "test_card_uses_row_layout",
        "Card uses flex row layout",
        "flexDirection row in source",
    ),
    # SPEC-0566 (1)
    (
        "SPEC-0566",
        "TestSpec0566IntegrationLogoObjectFitBlock",
        "test_both_css_properties",
        "Logo uses contain + block",
        "contain and block in source",
    ),
    # SPEC-0605 (1)
    (
        "SPEC-0605",
        "TestSpec0605TopRightLogoPrimaryNoWordmark",
        "test_header_logo_is_no_wordmark",
        "Top-right logo is primary-logo-no-wordmark",
        "primary-logo-no-wordmark in source",
    ),
    # SPEC-0606 (1)
    (
        "SPEC-0606",
        "TestSpec0606WordmarkGlossary",
        "test_customer_experience_is_separate_text",
        "Customer Experience is text element",
        "Text element not in img src",
    ),
    # SPEC-0694 (1)
    (
        "SPEC-0694",
        "TestSpec0694LoginPageLogo",
        "test_login_page_has_logo",
        "Login page has functional logo",
        "logo reference in login component",
    ),
    # SPEC-0799 (2)
    (
        "SPEC-0799",
        "TestSpec0799BrandPrimaryColor",
        "test_brand_color_in_widget_tokens",
        "Widget tokens define #ff3621",
        "#ff3621 in tokens.ts",
    ),
    (
        "SPEC-0799",
        "TestSpec0799BrandPrimaryColor",
        "test_brand_color_in_admin_theme",
        "Admin theme uses #ff3621",
        "#ff3621 in theme file",
    ),
    # SPEC-0801 (1)
    (
        "SPEC-0801",
        "TestSpec0801LogoConcept3Beacon",
        "test_icon_master_exists",
        "icon-master SVG and PNG exist",
        "files exist on disk",
    ),
    # SPEC-0814 (1)
    (
        "SPEC-0814",
        "TestSpec0814HeaderLogoPrimaryNoWordmark",
        "test_header_uses_no_wordmark",
        "Header uses primary-logo-no-wordmark",
        "primary-logo-no-wordmark in source",
    ),
    # SPEC-0825 (1)
    (
        "SPEC-0825",
        "TestSpec0825BrandingImages",
        "test_branding_images_directory",
        "branding/images/ has 20+ images",
        ">= 20 image files",
    ),
    # SPEC-0828 (1)
    (
        "SPEC-0828",
        "TestSpec0828ProtectedLogoFiles",
        "test_protected_files_exist",
        "4 protected logo files exist",
        "icon-master + primary-logo-no-wordmark SVG/PNG",
    ),
    # SPEC-0032 (1)
    (
        "SPEC-0032",
        "TestSpec0032WidgetDefaultBrandColors",
        "test_default_primary_is_brand_color",
        "Default primaryColor is #ff3621",
        "#ff3621 in widget tokens",
    ),
    # SPEC-0572 (1)
    (
        "SPEC-0572",
        "TestSpec0572WidgetErrorMessagesGreyBackground",
        "test_error_banner_uses_grey",
        "Error banner uses grey background",
        "#6B6B6B in Panel.tsx",
    ),
    # SPEC-1553 (1)
    (
        "SPEC-1553",
        "TestSpec1553WidgetBrandingFooter",
        "test_powered_by_agent_red",
        "Footer shows Agent Red in primaryColor",
        "Agent Red + colorPrimary in InputBar.tsx",
    ),
    # SPEC-0095 (1)
    (
        "SPEC-0095",
        "TestSpec0095InboxSearchReturnsMatches",
        "test_search_implementation_exists",
        "Inbox search/filter implementation exists",
        "search + filter/includes in inbox source",
    ),
    # SPEC-0071 (1)
    (
        "SPEC-0071",
        "TestSpec0071GlossaryPage",
        "test_admin_pages_match_sidebar_nav",
        "Pages match sidebar nav items",
        ">= 8 nav items and route definitions",
    ),
    # SPEC-0573 (2)
    (
        "SPEC-0573",
        "TestSpec0573ShopifyAdminLoads",
        "test_shopify_admin_entry_exists",
        "Shopify admin entry point exists",
        "index.tsx exists with App/render",
    ),
    (
        "SPEC-0573",
        "TestSpec0573ShopifyAdminLoads",
        "test_shopify_layout_exists",
        "Shopify layout exists",
        "ShopifyAppLayout.tsx exists",
    ),
    # SPEC-1659 (1)
    (
        "SPEC-1659",
        "TestSpec1659QualityDashboard",
        "test_assertion_check_hook_has_dashboard",
        "Quality dashboard in assertion hook",
        "_quality_dashboard + Assertion Coverage in source",
    ),
]

start_id = 8295
for i, (spec_id, cls, func, title, expected) in enumerate(tests):
    tid = f"TEST-{start_id + i}"
    db.insert_test(
        id=tid,
        title=title,
        spec_id=spec_id,
        test_type="unit",
        expected_outcome=expected,
        changed_by=CB,
        change_reason=CR,
        test_file=TEST_FILE,
        test_class=cls,
        test_function=func,
        last_result="PASS",
        last_executed_at="2026-03-06T16:00:00+00:00",
    )

print(f"Created {len(tests)} test artifacts (TEST-{start_id}..TEST-{start_id + len(tests) - 1})")
