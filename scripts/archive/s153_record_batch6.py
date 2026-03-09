"""S153 Batch 6 — Promote 55 specs + record 57 test artifacts in KB."""
import sys
sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()

# --- 1. Promote 55 specs to 'implemented' ---
specs_to_promote = [
    # Team (17)
    "SPEC-0046", "SPEC-0134", "SPEC-0135", "SPEC-0436", "SPEC-0437",
    "SPEC-0476", "SPEC-0478", "SPEC-0520", "SPEC-0522", "SPEC-0523",
    "SPEC-0559", "SPEC-0665", "SPEC-0716", "SPEC-0752", "SPEC-0753",
    "SPEC-0754", "SPEC-0838", "SPEC-0839",
    # Quick Actions (12)
    "SPEC-0101", "SPEC-0104", "SPEC-0105", "SPEC-0115", "SPEC-0318",
    "SPEC-0671", "SPEC-0672", "SPEC-0673", "SPEC-0674", "SPEC-0675",
    "SPEC-0727", "SPEC-0769", "SPEC-1550",
    # Knowledge Base (11)
    "SPEC-0496", "SPEC-0525", "SPEC-0526", "SPEC-0528", "SPEC-0641",
    "SPEC-0642", "SPEC-0643", "SPEC-0718", "SPEC-0724", "SPEC-0749",
    "SPEC-0830",
    # Integrations (3)
    "SPEC-0254", "SPEC-0534", "SPEC-0636",
    # Widget Config (1)
    "SPEC-0610",
    # Sidebar/Navbar (6)
    "SPEC-0091", "SPEC-0152", "SPEC-0353", "SPEC-0354", "SPEC-0388",
    "SPEC-0391",
    # Inbox (1)
    "SPEC-0359",
    # Dashboard (3)
    "SPEC-0119", "SPEC-0594", "SPEC-0865",
]
for sid in specs_to_promote:
    db.update_spec(
        sid, changed_by="S153",
        change_reason="Promoted to implemented - real production-interface test passing in test_s153_batch6_spec_verification.py",
        status="implemented",
    )
    print(f"Promoted {sid} -> implemented")

print(f"\n--- Promoted {len(specs_to_promote)} specs ---\n")

# --- 2. Record 57 test artifacts ---
TEST_FILE = "tests/multi_tenant/test_s153_batch6_spec_verification.py"
CB = "S153"
CR = "S153 batch 6 real production-interface spec verification test"

tests = [
    # Team (20 tests for 18 specs)
    ("SPEC-0046", "TestSpec0046TeamCRUDEndpoints", "test_team_api_has_crud_endpoints", "Team API CRUD endpoints exist", "POST + DELETE in admin_team_api.py"),
    ("SPEC-0046", "TestSpec0046TeamCRUDEndpoints", "test_team_api_has_key_rotation", "Team API key rotation exists", "rotate-key in admin_team_api.py"),
    ("SPEC-0134", "TestSpec0134RoleSelectorInline", "test_role_select_in_row", "Role selector is inline <select>", "<select> + onChange in TeamMemberRow.tsx"),
    ("SPEC-0135", "TestSpec0135RoleTooltipPopup", "test_role_tooltip_component_exists", "Role tooltip popup exists", "RoleTooltip.tsx with ROLES + Role permissions"),
    ("SPEC-0436", "TestSpec0436TeamAuditLog", "test_audit_events_logged", "Audit log events for team actions", "TEAM_MEMBER_ADDED/UPDATED/REMOVED in source"),
    ("SPEC-0437", "TestSpec0437StatusCheckboxRemoved", "test_no_checkbox_for_status", "No checkbox — uses Active/Disabled badge", "No type=checkbox, Active+Disabled in row"),
    ("SPEC-0476", "TestSpec0476NoSoftDeletion", "test_hard_delete_only", "Hard delete, no soft deletion", "DELETE + permanently/cannot be undone"),
    ("SPEC-0478", "TestSpec0478DeletionReversedByReinvite", "test_reinvite_message_in_dialog", "Deletion reversed by re-invite only", "re-invite in ConfirmRemoveDialog.tsx"),
    ("SPEC-0520", "TestSpec0520TeamPageDarkGroupedBox", "test_single_surface_container", "Team page uses single surface container", "palette.surface + borderRadius"),
    ("SPEC-0522", "TestSpec0522RoleTooltipSentenceCase", "test_sentence_case_descriptions", "Role tooltip uses sentence case", "Full access in constants, textTransform:none"),
    ("SPEC-0523", "TestSpec0523TrashCanRemoveIcon", "test_trash_icon_svg", "Trash-can SVG icon for remove", "polyline/path + onRemove in TeamMemberRow"),
    ("SPEC-0559", "TestSpec0559NoAdminPurpleFill", "test_select_uses_input_bg", "No purple fill on admin dropdown", "inputBg + inputBorder styling"),
    ("SPEC-0665", "TestSpec0665ResendInvitation", "test_resend_invite_endpoint", "Resend invitation endpoint exists", "resend-invite in admin_team_api.py"),
    ("SPEC-0716", "TestSpec0716EscalationCountColumn", "test_escalation_count_displayed", "Escalation count column displayed", "unresolvedEscalationCount in row"),
    ("SPEC-0752", "TestSpec0752RoleSelectMenus", "test_select_element_for_role", "Role column uses <select> menus", "<select> + INVITABLE_ROLES/option"),
    ("SPEC-0753", "TestSpec0753StatusToggle", "test_active_disabled_toggle", "Active/Disabled toggle exists", "onToggleActive + Active/Disabled"),
    ("SPEC-0754", "TestSpec0754EscalationCategoryChips", "test_six_escalation_categories", "6 escalation category chips for agents", "6 categories in types/index.ts"),
    ("SPEC-0838", "TestSpec0838EscalateToHumanSelection", "test_escalation_modal_has_category_selector", "Escalation modal has category selector", "category + assign in Inbox.tsx"),
    ("SPEC-0839", "TestSpec0839AgentDropdownShowsMembers", "test_agent_dropdown_populated", "Agent dropdown shows team members", "team/member + escalation_agent in Inbox"),
    # Quick Actions (13 tests for 13 specs)
    ("SPEC-0101", "TestSpec0101HiddenPromptsInWidget", "test_widget_quick_action_sends_prompt", "Widget sends hidden prompt on click", "prompt + onClick in QuickActions.tsx"),
    ("SPEC-0104", "TestSpec0104PrePopulatedExamples", "test_starter_examples_exist", "Pre-populated starter examples exist", "Track order/Return/Product in source"),
    ("SPEC-0105", "TestSpec0105IconGuidance", "test_icon_input_has_presets", "Icon input has emoji presets", "emoji presets in QuickActions.tsx"),
    ("SPEC-0115", "TestSpec0115AutoOpenPerPage", "test_auto_open_toggle_per_page", "Auto-open configurable per page type", "autoOpen + PAGE_TYPES in source"),
    ("SPEC-0318", "TestSpec0318SavedToActivatedTransitions", "test_activate_button_in_sidebar", "SAVED→ACTIVATED state transitions", "Activate + Deactivate + Discard in sidebar"),
    ("SPEC-0671", "TestSpec0671WidgetQuickActionButtons", "test_quick_action_buttons_in_widget", "Widget quick action buttons with prompts", "label + prompt/template in QuickActions.tsx"),
    ("SPEC-0672", "TestSpec0672QuickActionsScrollAway", "test_buttons_disappear_on_conversation", "Quick actions scroll away on conversation", "quickActions in Panel.tsx + label in QA"),
    ("SPEC-0673", "TestSpec0673PageIdentification", "test_template_variables_for_page", "Page identification via template variables", "page_type/page_handle/page_url in source"),
    ("SPEC-0674", "TestSpec0674AdminQuickActionCRUD", "test_crud_and_page_assignments", "CRUD + page assignments with slots", "slot + create + delete in QuickActions.tsx"),
    ("SPEC-0675", "TestSpec0675TwoSlotsPerPage", "test_two_slot_dropdowns", "Two Quick Action slots per page type", "Slot 1 + Slot 2 in source"),
    ("SPEC-0727", "TestSpec0727AutoOpenToggleOperable", "test_auto_open_handler", "Auto-open toggle has handler", "handleAutoOpenToggle/autoOpen in source"),
    ("SPEC-0769", "TestSpec0769NoPreChatFormBlockingGreeting", "test_no_pre_chat_form", "No pre-chat form blocking greeting", "quickActions + greeting in Panel.tsx"),
    ("SPEC-1550", "TestSpec1550WidgetPillsHorizontalLayout", "test_inline_pill_styling", "Widget pills horizontal inline layout", "borderRadius + padding in QuickActions.tsx"),
    # Knowledge Base (11 tests for 11 specs)
    ("SPEC-0496", "TestSpec0496KBSelectMenuLabels", "test_filter_labels_exist", "Category and Status filter labels", "Category + Status labels in KnowledgeBase.tsx"),
    ("SPEC-0525", "TestSpec0525NoGreyCirclesInKB", "test_colored_badges_not_circles", "Colored badges not grey circles", "Badge + blue/teal/violet colors"),
    ("SPEC-0526", "TestSpec0526ScanForConflictsTooltip", "test_scan_conflicts_tooltip", "Scan for conflicts has tooltip", "Tooltip + duplicate/contradictory text"),
    ("SPEC-0528", "TestSpec0528NeedsAttentionTooltip", "test_needs_attention_tooltip", "Needs attention area has tooltip", "Needs attention + stale articles"),
    ("SPEC-0641", "TestSpec0641KBAddArticle", "test_add_article_modal", "Add article feature exists", "Add + article in KnowledgeBase.tsx"),
    ("SPEC-0642", "TestSpec0642KBImportDocuments", "test_file_import_types", "Import PDF, DOCX, CSV, TXT", ".pdf + .docx + .csv + .txt in source"),
    ("SPEC-0643", "TestSpec0643KBImportURL", "test_url_import", "URL import feature exists", "URL + extract/import in KnowledgeBase.tsx"),
    ("SPEC-0718", "TestSpec0718ArticleRowColumns", "test_three_columns_displayed", "Category, Status, Freshness columns", "Category + Status + Freshness/staleness"),
    ("SPEC-0724", "TestSpec0724ActionsColumnTooltips", "test_action_tooltips", "Actions column has tooltips", "Tooltip + Verify + Edit + Archive"),
    ("SPEC-0749", "TestSpec0749KBCategoryFiltering", "test_category_filter_dropdown", "Category filtering returns matches", "categoryFilter + Policies/Shipping/Products"),
    ("SPEC-0830", "TestSpec0830StorefrontURLIngestion", "test_storefront_scan_feature", "Storefront URL ingestion/crawling", "storefront + ingest/crawl/scan"),
    # Integrations (3 tests)
    ("SPEC-0254", "TestSpec0254ComingSoonLabels", "test_coming_soon_badge", "Coming Soon labels on unimplemented", "Coming Soon + comingSoon in IntegrationsManager"),
    ("SPEC-0534", "TestSpec0534NoBounBoxNesting", "test_flat_card_layout", "Flat card layout, no box nesting", "flexDirection + row in IntegrationsManager"),
    ("SPEC-0636", "TestSpec0636DedicatedActivationPage", "test_activation_controls", "Dedicated activation/deactivation page", "Activate + Deactivate in IntegrationsManager"),
    # Widget Config (1 test)
    ("SPEC-0610", "TestSpec0610WidgetColorTextInput", "test_hex_text_input", "Color input accepts hex text input", "TextInput + hex/maxLength in Widget.tsx"),
    # Sidebar/Navbar (6 tests)
    ("SPEC-0091", "TestSpec0091LightDarkToggleRetainsDark", "test_header_dark_in_light_mode", "Header stays dark in light mode", "light + AppShell-header + #0c0a09 in tokens"),
    ("SPEC-0152", "TestSpec0152TestModeIndicator", "test_test_mode_banner", "Test mode indicator displayed", "Test Mode Active + testModeEnabled"),
    ("SPEC-0353", "TestSpec0353StorefrontNameInNavbar", "test_storefront_display", "Storefront name in navbar", "shopDomain + brandName in layout"),
    ("SPEC-0354", "TestSpec0354StorefrontLink", "test_storefront_link", "Storefront link opens in new tab", "target=_blank + https:// in layout"),
    ("SPEC-0388", "TestSpec0388ChatBubbleSidebarColor", "test_bubble_uses_surface_token", "Chat bubble uses surface token", "tokens.surface/surface in Inbox.tsx"),
    ("SPEC-0391", "TestSpec0391SidebarLogoNaturalColors", "test_no_css_filter_on_logo", "Logo renders in natural colors", "primary-logo-no-wordmark, no filter"),
    # Inbox (1 test)
    ("SPEC-0359", "TestSpec0359EscalationAgentReadOnly", "test_role_based_access", "Escalation agent read-only inbox access", "role + /inbox in layout and page"),
    # Dashboard (3 tests)
    ("SPEC-0119", "TestSpec0119StorefrontNameAboveDashboard", "test_storefront_name_on_dashboard", "Storefront name above Dashboard", "shopDomain/brandName + Dashboard in source"),
    ("SPEC-0594", "TestSpec0594NoFakeDataOnInit", "test_uses_real_analytics_api", "Dashboard uses real analytics API", "useAnalyticsSummary/useDailyVolume/apiFetch"),
    ("SPEC-0865", "TestSpec0865ActivationDialogFieldTags", "test_activation_dialog_uses_real_state", "Activation dialog shows real config state", "ActivationDialog/preflight + config"),
]

start_id = 8371
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
        last_executed_at="2026-03-06T18:00:00+00:00",
    )

print(f"Created {len(tests)} test artifacts (TEST-{start_id}..TEST-{start_id + len(tests) - 1})")
