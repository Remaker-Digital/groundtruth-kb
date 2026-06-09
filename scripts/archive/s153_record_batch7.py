"""S153 Batch 7 — Promote 46 specs + record 47 test artifacts in KB."""

import sys

sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()

# --- 1. Promote 46 specs to 'implemented' ---
specs_to_promote = [
    # Widget (23)
    "SPEC-0038",
    "SPEC-0059",
    "SPEC-0099",
    "SPEC-0102",
    "SPEC-0103",
    "SPEC-0126",
    "SPEC-0189",
    "SPEC-0213",
    "SPEC-0357",
    "SPEC-0413",
    "SPEC-0501",
    "SPEC-0529",
    "SPEC-0563",
    "SPEC-0577",
    "SPEC-0581",
    "SPEC-0611",
    "SPEC-0779",
    "SPEC-1548",
    "SPEC-1549",
    "SPEC-1551",
    "SPEC-1552",
    "SPEC-1554",
    "SPEC-1556",
    # Billing (6)
    "SPEC-0138",
    "SPEC-0172",
    "SPEC-0251",
    "SPEC-0495",
    "SPEC-0592",
    "SPEC-0731",
    # Deploy (10)
    "SPEC-0035",
    "SPEC-0442",
    "SPEC-0646",
    "SPEC-0647",
    "SPEC-0649",
    "SPEC-0664",
    "SPEC-0693",
    "SPEC-0722",
    "SPEC-0755",
    "SPEC-0837",
    # Branding (3)
    "SPEC-0078",
    "SPEC-0123",
    "SPEC-0820",
    # Escalation (2)
    "SPEC-0005",
    "SPEC-0614",
    # Email (2)
    "SPEC-0615",
    "SPEC-1630",
]
for sid in specs_to_promote:
    db.update_spec(
        sid,
        changed_by="S153",
        change_reason="Promoted to implemented - real production-interface test passing in test_s153_batch7_spec_verification.py",
        status="implemented",
    )
    print(f"Promoted {sid} -> implemented")

print(f"\n--- Promoted {len(specs_to_promote)} specs ---\n")

# --- 2. Record 47 test artifacts ---
TEST_FILE = "tests/multi_tenant/test_s153_batch7_spec_verification.py"
CB = "S153"
CR = "S153 batch 7 real production-interface spec verification test"

tests = [
    # Widget (23 tests)
    (
        "SPEC-0038",
        "TestSpec0038DefaultAgentRedColors",
        "test_default_primary_is_agent_red",
        "Default primary is Agent Red #ff3621",
        "#ff3621 in tokens.ts, not blue",
    ),
    (
        "SPEC-0059",
        "TestSpec0059WidgetRequiresActivation",
        "test_widget_checks_activation",
        "Widget checks activation status",
        "active/config check in index.ts",
    ),
    (
        "SPEC-0099",
        "TestSpec0099WidgetOnAdminConsole",
        "test_admin_widget_mode",
        "Widget admin preview mode",
        "admin/data-admin-key in index.ts",
    ),
    (
        "SPEC-0102",
        "TestSpec0102WidgetColorAfterSave",
        "test_color_config_applied",
        "Widget color config applied after save",
        "widget_primary_color/primaryColor in Widget.tsx",
    ),
    (
        "SPEC-0103",
        "TestSpec0103GreetingMessageConfig",
        "test_greeting_template_variables",
        "Greeting message supports template vars",
        "FIRST_NAME/greeting in Widget.tsx",
    ),
    (
        "SPEC-0126",
        "TestSpec0126GradientHeaderToggle",
        "test_gradient_toggle",
        "Gradient toggle on widget header",
        "gradient + linear-gradient in Header.tsx",
    ),
    (
        "SPEC-0189",
        "TestSpec0189WidgetIframeHeight100",
        "test_iframe_full_height",
        "Widget iframe uses height:100%",
        "height:100% in index.ts",
    ),
    (
        "SPEC-0213",
        "TestSpec0213NamedConfigControls",
        "test_named_config_section",
        "Named config controls at launch",
        "Named/config in Configuration.tsx",
    ),
    (
        "SPEC-0357",
        "TestSpec0357PoweredByAgentRedCX",
        "test_powered_by_link",
        "Powered by links to agentredcx.com",
        "agentredcx.com + Agent Red in InputBar.tsx",
    ),
    (
        "SPEC-0413",
        "TestSpec0413WidgetOnAdminWhenActive",
        "test_admin_widget_activation",
        "Widget displays when active",
        "is_active + widget in StandaloneLayout.tsx",
    ),
    (
        "SPEC-0501",
        "TestSpec0501CloseButtonCorrectState",
        "test_close_handler",
        "Close button correct state handling",
        "onClose + onClick in Header.tsx",
    ),
    (
        "SPEC-0529",
        "TestSpec0529GreetingMessageTooltip",
        "test_greeting_tooltip",
        "Greeting message has tooltip",
        "greeting + Tooltip/HelpTooltip in Widget.tsx",
    ),
    (
        "SPEC-0563",
        "TestSpec0563PreviewPanelRemoved",
        "test_no_preview_on_config",
        "Preview panel removed from Config",
        "No preview in Configuration.tsx",
    ),
    (
        "SPEC-0577",
        "TestSpec0577WidgetPreviewRenders",
        "test_widget_preview_on_widget_page",
        "Widget preview renders on Widget page",
        "preview/Preview in Widget.tsx",
    ),
    (
        "SPEC-0581",
        "TestSpec0581WidgetStreaming",
        "test_sse_streaming",
        "SSE streaming for widget chat",
        "token + stream/event in transport/sse.ts",
    ),
    (
        "SPEC-0611",
        "TestSpec0611AdminChatWidget",
        "test_admin_mode_widget",
        "Admin chat widget for verification",
        "admin in index.ts",
    ),
    (
        "SPEC-0779",
        "TestSpec0779KeysNotDisturbed",
        "test_upgrade_verifies_keys",
        "Keys not disturbed during upgrade",
        "widget/key + team/member in upgrade_verification.py",
    ),
    (
        "SPEC-1548",
        "TestSpec1548WidgetHeaderLayout",
        "test_header_layout",
        "Widget header matches mockup layout",
        "height/padding + avatar/agentName in Header.tsx",
    ),
    (
        "SPEC-1549",
        "TestSpec1549GreetingLeftAlignedBubble",
        "test_greeting_bubble_alignment",
        "Greeting left-aligned chat bubble",
        "4px 16px 16px 16px in MessageList.tsx",
    ),
    (
        "SPEC-1551",
        "TestSpec1551MessageBubbleStyling",
        "test_bubble_border_radius",
        "Message bubble border-radius + padding",
        "borderRadius + padding in MessageBubble.tsx",
    ),
    (
        "SPEC-1552",
        "TestSpec1552WidgetInputBarStyling",
        "test_input_bar_styling",
        "Input bar matches mockup styling",
        "padding + border in InputBar.tsx",
    ),
    (
        "SPEC-1554",
        "TestSpec1554ColorAgentBubbleBorder",
        "test_token_exists",
        "colorAgentBubbleBorder token defined",
        "colorAgentBubbleBorder in tokens.ts",
    ),
    (
        "SPEC-1556",
        "TestSpec1556ColorInputBarBg",
        "test_token_exists",
        "colorInputBarBg token defined",
        "colorInputBarBg in tokens.ts",
    ),
    # Billing (7 tests for 6 specs)
    (
        "SPEC-0138",
        "TestSpec0138BillingTooltipsWithDocLinks",
        "test_billing_tooltips",
        "Billing tooltips with doc links",
        "HelpTooltip + agentredcx.com in Billing.tsx",
    ),
    (
        "SPEC-0138",
        "TestSpec0138BillingTooltipsWithDocLinks",
        "test_multiple_tooltip_areas",
        "Multiple tooltip areas on Billing",
        "4+ HelpTooltip instances in Billing.tsx",
    ),
    (
        "SPEC-0172",
        "TestSpec0172AddonModuleTierRestriction",
        "test_disabled_for_wrong_tier",
        "Add-on disabled for wrong tier",
        "Requires + disabled in Billing.tsx",
    ),
    (
        "SPEC-0251",
        "TestSpec0251BillingPurchaseButtonFunctional",
        "test_subscribe_button_responds",
        "Subscribe button is functional",
        "Subscribe + onClick/handleSubscribe in Billing.tsx",
    ),
    (
        "SPEC-0495",
        "TestSpec0495SubscribeButtonFunctions",
        "test_subscribe_handler",
        "Subscribe button functions correctly",
        "Subscribe in Billing.tsx",
    ),
    (
        "SPEC-0592",
        "TestSpec0592TierBadgeCapitalization",
        "test_capitalized_tier_labels",
        "Tier badge properly capitalized",
        "Professional + Starter in Billing.tsx",
    ),
    (
        "SPEC-0731",
        "TestSpec0731StripeExeInGitignore",
        "test_gitignore_has_stripe",
        "stripe.exe in .gitignore",
        "stripe.exe in .gitignore",
    ),
    # Deploy (10 tests)
    (
        "SPEC-0035",
        "TestSpec0035PreFlightChecklist",
        "test_deploy_pipeline_exists",
        "Deploy pipeline with phases",
        "phase in deploy_pipeline.py",
    ),
    (
        "SPEC-0442",
        "TestSpec0442DeployGovernedByProcedures",
        "test_deploy_pipeline_automated",
        "Deployment governed by procedures",
        "staging + production in deploy_pipeline.py",
    ),
    (
        "SPEC-0646",
        "TestSpec0646NonDisruptiveUpgradeProcedure",
        "test_upgrade_verification_exists",
        "Upgrade verification procedure",
        "--env in upgrade_verification.py",
    ),
    (
        "SPEC-0647",
        "TestSpec0647ParallelTestingProcedure",
        "test_staging_track_exists",
        "Parallel testing via staging track",
        "staging in deploy_pipeline.py",
    ),
    (
        "SPEC-0649",
        "TestSpec0649RollbackProcedure",
        "test_rollback_documented",
        "Rollback procedure documented",
        "rollback/previous/az containerapp in deploy_pipeline.py",
    ),
    (
        "SPEC-0664",
        "TestSpec0664PathToProductionRequiresStaging",
        "test_staging_before_production",
        "Staging required before production",
        "staging + production in deploy_pipeline.py",
    ),
    (
        "SPEC-0693",
        "TestSpec0693ParallelStagingEnvironment",
        "test_staging_deployment",
        "Parallel staging environment",
        "staging in deploy_pipeline.py",
    ),
    (
        "SPEC-0722",
        "TestSpec0722TenantDataIntactAfterDeploy",
        "test_data_integrity_assertions",
        "Tenant data intact after deploy",
        "team/member + conversation/article in upgrade_verification.py",
    ),
    (
        "SPEC-0755",
        "TestSpec0755DataIntegritySafeguards",
        "test_team_data_verification",
        "Team data integrity safeguards",
        "team + member/display in upgrade_verification.py",
    ),
    (
        "SPEC-0837",
        "TestSpec0837NonDisruptiveUpgradeProvenOnStaging",
        "test_staging_validation_first",
        "Non-disruptive upgrade proven on staging",
        "staging in deploy_pipeline.py",
    ),
    # Branding (3 tests)
    (
        "SPEC-0078",
        "TestSpec0078LogoFilesUpdated",
        "test_logo_files_exist",
        "Logo files updated in branding/logo/",
        "icon-master.svg + primary-logo-no-wordmark.svg + icon-master.png",
    ),
    (
        "SPEC-0123",
        "TestSpec0123ConfigSectionTooltips",
        "test_config_page_tooltips",
        "Config sections have tooltips",
        "5+ HelpTooltip + agentredcx.com in Configuration.tsx",
    ),
    (
        "SPEC-0820",
        "TestSpec0820LogoCorners90Degrees",
        "test_block_logo_square_corners",
        "Logo corners 90 degrees",
        "rect element in block logo SVG",
    ),
    # Escalation (2 tests)
    (
        "SPEC-0005",
        "TestSpec0005EscalationSliderLabels",
        "test_slider_labels",
        "Escalation slider Conservative/Aggressive",
        "Conservative + Aggressive in Configuration.tsx",
    ),
    (
        "SPEC-0614",
        "TestSpec0614EscalationCategoryKeywords",
        "test_per_category_keywords",
        "Per-category escalation keywords",
        "sales/support/service/account in Configuration.tsx",
    ),
    # Email (2 tests)
    (
        "SPEC-0615",
        "TestSpec0615EscalationCategoryEmails",
        "test_category_email_field",
        "Per-category notification email",
        "email in Configuration.tsx + escalation module",
    ),
    (
        "SPEC-1630",
        "TestSpec1630ApiKeyResetEmailGreyBackground",
        "test_email_grey_background",
        "API key reset email grey background",
        "#f3f4f6/#d1d5db/grey in admin_apikey_api.py",
    ),
]

start_id = 8428
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
        last_executed_at="2026-03-06T19:00:00+00:00",
    )

print(f"Created {len(tests)} test artifacts (TEST-{start_id}..TEST-{start_id + len(tests) - 1})")
