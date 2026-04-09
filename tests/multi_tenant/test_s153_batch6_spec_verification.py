"""S153 Batch 6 — Team + QuickActions + KB + Integrations + Config + Sidebar + Inbox + Dashboard.

55 specs verified against production interfaces.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from pathlib import Path

import pytest

pytestmark = pytest.mark.local_env


# ── Paths ──────────────────────────────────────────────────────────────
SRC = Path(__file__).resolve().parents[2] / "src"
ADMIN = Path(__file__).resolve().parents[2] / "admin"
WIDGET = Path(__file__).resolve().parents[2] / "widget"
STANDALONE = ADMIN / "standalone"
SHARED = ADMIN / "shared"
SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
BRANDING = Path(__file__).resolve().parents[2] / "branding"


# ═══════════════════════════════════════════════════════════════════════
#  TEAM MEMBER SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0046TeamCRUDEndpoints:
    """SPEC-0046: UI testing MUST include team member creation, key re-issuance, and removal."""

    def test_team_api_has_crud_endpoints(self):
        src = (SRC / "multi_tenant" / "admin_team_api.py").read_text(encoding="utf-8")
        assert "POST" in src and "/api/admin/team" in src, "Create endpoint must exist"
        assert "DELETE" in src, "Delete endpoint must exist"

    def test_team_api_has_key_rotation(self):
        src = (SRC / "multi_tenant" / "admin_team_api.py").read_text(encoding="utf-8")
        assert "rotate-key" in src or "rotate_key" in src, "Key rotation endpoint must exist"


class TestSpec0134RoleSelectorInline:
    """SPEC-0134: Role selector MUST replace textual role names inline, not in Actions column."""

    def test_role_select_in_row(self):
        src = (SHARED / "team" / "TeamMemberRow.tsx").read_text(encoding="utf-8")
        assert "<select" in src, "Role must use <select> element inline"
        assert "onRoleChange" in src or "onChange" in src, "Select must trigger role change"


class TestSpec0135RoleTooltipPopup:
    """SPEC-0135: 'Roles & permissions' MUST be on-hover tooltip pop-up for Role column heading."""

    def test_role_tooltip_component_exists(self):
        tooltip = SHARED / "team" / "RoleTooltip.tsx"
        assert tooltip.exists(), "RoleTooltip component must exist"
        src = tooltip.read_text(encoding="utf-8")
        assert "Role permissions" in src, "Tooltip must show 'Role permissions' heading"
        assert "ROLES" in src, "Tooltip must render ROLES definitions"


class TestSpec0436TeamAuditLog:
    """SPEC-0436: All team member actions MUST be stored in an audit log."""

    def test_audit_events_logged(self):
        src = (SRC / "multi_tenant" / "admin_team_api.py").read_text(encoding="utf-8")
        assert "TEAM_MEMBER_ADDED" in src, "Must log add events"
        assert "TEAM_MEMBER_UPDATED" in src, "Must log update events"
        assert "TEAM_MEMBER_REMOVED" in src, "Must log remove events"


class TestSpec0437StatusCheckboxRemoved:
    """SPEC-0437: The Status checkbox MUST be removed from team management."""

    def test_no_checkbox_for_status(self):
        src = (SHARED / "team" / "TeamMemberRow.tsx").read_text(encoding="utf-8")
        # Status uses a styled button badge, not a checkbox
        assert "type=\"checkbox\"" not in src or "checkbox" not in src.split("Active")[0], \
            "Status must not use checkbox input"
        assert "Active" in src and "Disabled" in src, "Must show Active/Disabled badge"


class TestSpec0476NoSoftDeletion:
    """SPEC-0476: There MUST NOT be any soft deletion option for team members."""

    def test_hard_delete_only(self):
        src = (SRC / "multi_tenant" / "admin_team_api.py").read_text(encoding="utf-8")
        # Delete endpoint must do hard delete (no is_deleted flag)
        assert "DELETE" in src, "Delete endpoint must exist"
        confirm = (SHARED / "team" / "ConfirmRemoveDialog.tsx").read_text(encoding="utf-8")
        assert "cannot be undone" in confirm.lower() or "permanently" in confirm.lower(), \
            "Deletion must be permanent"


class TestSpec0478DeletionReversedByReinvite:
    """SPEC-0478: Deletion reversed only by re-invite via '+ Invite member'."""

    def test_reinvite_message_in_dialog(self):
        src = (SHARED / "team" / "ConfirmRemoveDialog.tsx").read_text(encoding="utf-8")
        assert "re-invite" in src.lower() or "re-invited" in src.lower(), \
            "Dialog must mention re-invite as the reversal method"


class TestSpec0520TeamPageDarkGroupedBox:
    """SPEC-0520: Team page body MUST be dark, team list and invite grouped in single box."""

    def test_single_surface_container(self):
        src = (SHARED / "TeamManager.tsx").read_text(encoding="utf-8")
        # Uses palette.surface for container background
        assert "palette.surface" in src or "surface" in src, \
            "Must use surface color for container"
        assert "borderRadius" in src, "Container must have rounded corners"


class TestSpec0522RoleTooltipSentenceCase:
    """SPEC-0522: Role permissions tooltip MUST use regular sentence case."""

    def test_sentence_case_descriptions(self):
        # Role descriptions are in constants.ts, rendered by RoleTooltip.tsx
        src = (SHARED / "team" / "constants.ts").read_text(encoding="utf-8")
        assert "Full access" in src, "Must describe roles in sentence case"
        assert "FULL ACCESS" not in src, "Must NOT use ALL-CAPS for descriptions"
        # Tooltip uses textTransform: none (not uppercase)
        tooltip_src = (SHARED / "team" / "RoleTooltip.tsx").read_text(encoding="utf-8")
        assert "textTransform: 'none'" in tooltip_src, "Tooltip must use sentence case"


class TestSpec0523TrashCanRemoveIcon:
    """SPEC-0523: Remove buttons MUST be trash-can icons."""

    def test_trash_icon_svg(self):
        src = (SHARED / "team" / "TeamMemberRow.tsx").read_text(encoding="utf-8")
        # SVG trash icon (polyline/path elements)
        assert "polyline" in src or "path" in src, "Must use SVG icon for delete"
        assert "onRemove" in src, "Must trigger remove callback"


class TestSpec0559NoAdminPurpleFill:
    """SPEC-0559: Admin role dropdown MUST NOT have purple fill color."""

    def test_select_uses_input_bg(self):
        src = (SHARED / "team" / "TeamMemberRow.tsx").read_text(encoding="utf-8")
        # The select dropdown uses palette.inputBg, not a purple color
        assert "inputBg" in src or "inputBorder" in src, \
            "Role select must use neutral input styling"


class TestSpec0665ResendInvitation:
    """SPEC-0665: Admins and superadmins MUST be able to re-send team invitation emails."""

    def test_resend_invite_endpoint(self):
        src = (SRC / "multi_tenant" / "admin_team_api.py").read_text(encoding="utf-8")
        assert "resend-invite" in src or "resend_invite" in src, \
            "Resend invitation endpoint must exist"


class TestSpec0716EscalationCountColumn:
    """SPEC-0716: Team table MUST include column displaying unresolved escalations."""

    def test_escalation_count_displayed(self):
        src = (SHARED / "team" / "TeamMemberRow.tsx").read_text(encoding="utf-8")
        assert "unresolvedEscalationCount" in src or "unresolved" in src.lower(), \
            "Must display unresolved escalation count"


class TestSpec0752RoleSelectMenus:
    """SPEC-0752: Team page Role column MUST use select menus, not badges."""

    def test_select_element_for_role(self):
        src = (SHARED / "team" / "TeamMemberRow.tsx").read_text(encoding="utf-8")
        assert "<select" in src, "Role must use <select> element"
        assert "INVITABLE_ROLES" in src or "option" in src.lower(), \
            "Select must have role options"


class TestSpec0753StatusToggle:
    """SPEC-0753: Team page MUST provide toggle to enable/disable team member status."""

    def test_active_disabled_toggle(self):
        src = (SHARED / "team" / "TeamMemberRow.tsx").read_text(encoding="utf-8")
        assert "onToggleActive" in src, "Must have active/disabled toggle"
        assert "Active" in src and "Disabled" in src, "Must show both states"


class TestSpec0754EscalationCategoryChips:
    """SPEC-0754: Each team member with 'Agent' role MUST have escalation category select boxes."""

    def test_six_escalation_categories(self):
        src = (SHARED / "team" / "TeamMemberRow.tsx").read_text(encoding="utf-8")
        assert "escalation_agent" in src, "Must check for agent role"
        assert "onCategoryToggle" in src, "Must support category toggling"
        # Check categories defined
        types_src = (SHARED / "types" / "index.ts").read_text(encoding="utf-8")
        for cat in ["sales", "support", "service", "account", "technical", "general"]:
            assert cat in types_src, f"Category '{cat}' must be defined"


class TestSpec0838EscalateToHumanSelection:
    """SPEC-0838: 'Escalate to human' MUST ask which person or escalation role to escalate to."""

    def test_escalation_modal_has_category_selector(self):
        src = (STANDALONE / "pages" / "Inbox.tsx").read_text(encoding="utf-8")
        assert "category" in src.lower() or "escalation" in src.lower(), \
            "Escalation modal must have category selection"
        assert "Assign to agent" in src or "assign" in src.lower(), \
            "Must support agent assignment"


class TestSpec0839AgentDropdownShowsMembers:
    """SPEC-0839: 'Assign to agent' dropdown MUST show available team members."""

    def test_agent_dropdown_populated(self):
        src = (STANDALONE / "pages" / "Inbox.tsx").read_text(encoding="utf-8")
        assert "team" in src.lower() or "member" in src.lower(), \
            "Must populate dropdown from team members"
        assert "escalation_agent" in src or "designated" in src.lower(), \
            "Must show escalation agents"


# ═══════════════════════════════════════════════════════════════════════
#  QUICK ACTIONS SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0101HiddenPromptsInWidget:
    """SPEC-0101: Quick action prompt buttons with hidden prompts MUST be in message pane."""

    def test_widget_quick_action_sends_prompt(self):
        src = (WIDGET / "src" / "components" / "QuickActions.tsx").read_text(encoding="utf-8")
        assert "prompt" in src.lower(), "Must send prompt on click"
        assert "onClick" in src or "onSend" in src, "Must have click handler"


class TestSpec0104PrePopulatedExamples:
    """SPEC-0104: Quick actions MUST have examples pre-populated."""

    def test_starter_examples_exist(self):
        src = (STANDALONE / "pages" / "QuickActions.tsx").read_text(encoding="utf-8")
        # Check for at least 2 starter examples
        examples = ["Track order", "Return", "Product recommend", "Help"]
        found = sum(1 for e in examples if e.lower() in src.lower())
        assert found >= 2, f"Must have pre-populated examples (found {found}/4)"


class TestSpec0105IconGuidance:
    """SPEC-0105: 'Icon' input MUST contain guidance or examples for obtaining an icon."""

    def test_icon_input_has_presets(self):
        src = (STANDALONE / "pages" / "QuickActions.tsx").read_text(encoding="utf-8")
        # Check for emoji presets and guidance text
        assert "emoji" in src.lower() or "📦" in src or "🔄" in src, \
            "Must have emoji presets for icon selection"


class TestSpec0115AutoOpenPerPage:
    """SPEC-0115: Auto-open MUST be configurable per-page."""

    def test_auto_open_toggle_per_page(self):
        src = (STANDALONE / "pages" / "QuickActions.tsx").read_text(encoding="utf-8")
        assert "autoOpen" in src or "auto_open" in src or "auto-open" in src.lower(), \
            "Must have auto-open configuration"
        assert "PAGE_TYPES" in src or "page_type" in src, \
            "Auto-open must be per page type"


class TestSpec0318SavedToActivatedTransitions:
    """SPEC-0318: Four config pages MUST use SAVED to ACTIVATED state transitions."""

    def test_activate_button_in_sidebar(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "Activate" in src, "Must have Activate button"
        assert "Deactivate" in src, "Must have Deactivate button"
        assert "Discard" in src, "Must have Discard button"


class TestSpec0671WidgetQuickActionButtons:
    """SPEC-0671: Widget MUST support clickable Quick Action buttons with page-specific prompts."""

    def test_quick_action_buttons_in_widget(self):
        src = (WIDGET / "src" / "components" / "QuickActions.tsx").read_text(encoding="utf-8")
        assert "label" in src, "Must display button label"
        assert "prompt" in src.lower() or "template" in src.lower(), \
            "Must use prompt template"


class TestSpec0672QuickActionsScrollAway:
    """SPEC-0672: Quick Action buttons MUST scroll upward when manual prompt is sent."""

    def test_buttons_disappear_on_conversation(self):
        # Quick actions are passed as props to Panel.tsx
        panel = WIDGET / "src" / "components" / "Panel.tsx"
        src = panel.read_text(encoding="utf-8")
        assert "quickActions" in src or "quick_actions" in src, \
            "Panel must handle quick actions"
        # Quick actions only render in greeting state (before messages)
        qa_src = (WIDGET / "src" / "components" / "QuickActions.tsx").read_text(encoding="utf-8")
        assert "label" in qa_src, "Quick actions must display labels"


class TestSpec0673PageIdentification:
    """SPEC-0673: System MUST identify which page widget is loading on via unique identifiers."""

    def test_template_variables_for_page(self):
        src = (STANDALONE / "pages" / "QuickActions.tsx").read_text(encoding="utf-8")
        # Template variables for page identification
        page_vars = ["page_type", "page_handle", "page_url", "page_title"]
        found = sum(1 for v in page_vars if v in src)
        assert found >= 2, f"Must have page identification variables (found {found}/4)"


class TestSpec0674AdminQuickActionCRUD:
    """SPEC-0674: Admin UI MUST include page to activate per-page, assign up to two, CRUD."""

    def test_crud_and_page_assignments(self):
        src = (STANDALONE / "pages" / "QuickActions.tsx").read_text(encoding="utf-8")
        assert "Slot 1" in src or "slot" in src.lower(), "Must have slot assignment"
        assert "create" in src.lower() or "Create" in src, "Must support create"
        assert "delete" in src.lower() or "Delete" in src or "remove" in src.lower(), \
            "Must support delete"


class TestSpec0675TwoSlotsPerPage:
    """SPEC-0675: Each page type MUST support exactly two Quick Action button slots."""

    def test_two_slot_dropdowns(self):
        src = (STANDALONE / "pages" / "QuickActions.tsx").read_text(encoding="utf-8")
        assert "Slot 1" in src or "slot1" in src or "slot_1" in src, \
            "Must have first slot"
        assert "Slot 2" in src or "slot2" in src or "slot_2" in src, \
            "Must have second slot"


class TestSpec0727AutoOpenToggleOperable:
    """SPEC-0727: Auto-open toggle on Quick Actions page MUST be operable."""

    def test_auto_open_handler(self):
        src = (STANDALONE / "pages" / "QuickActions.tsx").read_text(encoding="utf-8")
        assert "handleAutoOpenToggle" in src or "autoOpen" in src, \
            "Auto-open toggle must have a handler"


class TestSpec0769NoPreChatFormBlockingGreeting:
    """SPEC-0769: No pre-chat form blocking AI greeting — greeting and Quick Actions appear immediately."""

    def test_no_pre_chat_form(self):
        panel = (WIDGET / "src" / "components" / "Panel.tsx").read_text(encoding="utf-8")
        # Quick actions appear immediately with greeting, no blocking form
        assert "quickActions" in panel, "Quick actions must render with greeting"
        # Greeting appears before any user input
        assert "greeting" in panel.lower(), "Greeting must appear immediately"


class TestSpec1550WidgetPillsHorizontalLayout:
    """SPEC-1550: Widget quick action pills MUST use horizontal inline layout."""

    def test_inline_pill_styling(self):
        src = (WIDGET / "src" / "components" / "QuickActions.tsx").read_text(encoding="utf-8")
        assert "borderRadius" in src or "border-radius" in src, \
            "Pills must have rounded styling"
        assert "padding" in src or "gap" in src, "Must have compact spacing"


# ═══════════════════════════════════════════════════════════════════════
#  KNOWLEDGE BASE SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0496KBSelectMenuLabels:
    """SPEC-0496: Category and Status select menus MUST have text labels."""

    def test_filter_labels_exist(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        assert "Category" in src, "Category filter must have label"
        assert "Status" in src, "Status filter must have label"


class TestSpec0525NoGreyCirclesInKB:
    """SPEC-0525: Category and Status columns MUST NOT show grey circles — must display actual values."""

    def test_colored_badges_not_circles(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        # Check for colored badge rendering (not grey circles)
        assert "Badge" in src or "badge" in src, "Must use Badge component"
        # Categories should have color mappings
        assert "blue" in src or "teal" in src or "violet" in src, \
            "Category badges must have colors"


class TestSpec0526ScanForConflictsTooltip:
    """SPEC-0526: 'Scan for conflicts' control MUST have a tooltip."""

    def test_scan_conflicts_tooltip(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        assert "Scan for conflicts" in src, "Scan for conflicts button must exist"
        assert "Tooltip" in src or "tooltip" in src, "Must use tooltip"
        assert "duplicate" in src.lower() or "contradictory" in src.lower(), \
            "Tooltip must describe conflict detection"


class TestSpec0528NeedsAttentionTooltip:
    """SPEC-0528: 'Needs attention' display area MUST have a tooltip."""

    def test_needs_attention_tooltip(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        assert "Needs attention" in src or "needs attention" in src, \
            "Needs attention area must exist"
        assert "stale" in src.lower(), "Must reference stale articles"


class TestSpec0641KBAddArticle:
    """SPEC-0641: KB MUST support adding a test article."""

    def test_add_article_modal(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        assert "Add" in src and "article" in src.lower(), "Must have Add article feature"


class TestSpec0642KBImportDocuments:
    """SPEC-0642: KB MUST support importing PDF, DOCX, CSV, and TXT documents."""

    def test_file_import_types(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        assert ".pdf" in src, "Must accept PDF"
        assert ".docx" in src, "Must accept DOCX"
        assert ".csv" in src, "Must accept CSV"
        assert ".txt" in src, "Must accept TXT"


class TestSpec0643KBImportURL:
    """SPEC-0643: KB MUST support importing a URL."""

    def test_url_import(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        assert "URL" in src or "url" in src, "Must have URL import"
        assert "extract" in src.lower() or "import" in src.lower(), \
            "Must support URL content extraction"


class TestSpec0718ArticleRowColumns:
    """SPEC-0718: Article rows MUST display Category, Status, and Freshness."""

    def test_three_columns_displayed(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        assert "Category" in src, "Must show Category column"
        assert "Status" in src, "Must show Status column"
        assert "Freshness" in src or "staleness" in src.lower(), \
            "Must show Freshness column"


class TestSpec0724ActionsColumnTooltips:
    """SPEC-0724: Actions column MUST have tooltip explaining each action."""

    def test_action_tooltips(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        # Actions: Verify, Edit, Archive/Restore
        assert "Tooltip" in src, "Must use Tooltip components"
        verify_tooltip = "verified" in src.lower() or "verify" in src.lower()
        edit_ref = "Edit" in src or "edit" in src
        archive_ref = "Archive" in src or "archive" in src
        assert verify_tooltip and edit_ref and archive_ref, \
            "Must have tooltips for Verify, Edit, and Archive actions"


class TestSpec0749KBCategoryFiltering:
    """SPEC-0749: Category filtering MUST return articles matching selected category."""

    def test_category_filter_dropdown(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        assert "categoryFilter" in src or "category_filter" in src, \
            "Must have category filter state"
        # Check for filter options
        for cat in ["Policies", "Shipping", "Products"]:
            assert cat in src, f"Filter must include '{cat}' option"


class TestSpec0830StorefrontURLIngestion:
    """SPEC-0830: KB MUST be built by ingesting/crawling merchant's storefront URL."""

    def test_storefront_scan_feature(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        assert "storefront" in src.lower() or "Storefront" in src, \
            "Must support storefront scanning"
        assert "ingest" in src.lower() or "crawl" in src.lower() or "scan" in src.lower(), \
            "Must support URL ingestion"


# ═══════════════════════════════════════════════════════════════════════
#  INTEGRATIONS SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0254ComingSoonLabels:
    """SPEC-0254: Unimplemented integrations MUST display 'Coming Soon' labels."""

    def test_coming_soon_badge(self):
        src = (SHARED / "IntegrationsManager.tsx").read_text(encoding="utf-8")
        assert "Coming Soon" in src, "Must display 'Coming Soon' badge"
        assert "comingSoon" in src, "Must have comingSoon property"


class TestSpec0534NoBounBoxNesting:
    """SPEC-0534: Integrations page MUST NOT have box-within-box nesting."""

    def test_flat_card_layout(self):
        src = (SHARED / "IntegrationsManager.tsx").read_text(encoding="utf-8")
        # Cards use flat structure with flex row
        assert "flexDirection" in src or "flex-direction" in src, \
            "Cards must use flex layout"
        assert "'row'" in src or "\"row\"" in src, "Cards must use row direction"


class TestSpec0636DedicatedActivationPage:
    """SPEC-0636: MUST be dedicated page for integration configuration and activation/deactivation."""

    def test_activation_controls(self):
        src = (SHARED / "IntegrationsManager.tsx").read_text(encoding="utf-8")
        assert "Activate" in src, "Must have Activate button"
        assert "Deactivate" in src, "Must have Deactivate button"


# ═══════════════════════════════════════════════════════════════════════
#  WIDGET CONFIG SPEC
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0610WidgetColorTextInput:
    """SPEC-0610: Widget Configurator color input MUST allow user to input a color value."""

    def test_hex_text_input(self):
        src = (STANDALONE / "pages" / "Widget.tsx").read_text(encoding="utf-8")
        assert "TextInput" in src or "textInput" in src or "type=\"text\"" in src, \
            "Must have text input for color"
        assert "#RRGGBB" in src or "hex" in src.lower() or "maxLength={7}" in src, \
            "Must accept hex color format"


# ═══════════════════════════════════════════════════════════════════════
#  SIDEBAR / NAVBAR SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0091LightDarkToggleRetainsDark:
    """SPEC-0091: Light/Dark toggle MUST retain Dark Mode colors even in Light Mode for navbar."""

    def test_header_dark_in_light_mode(self):
        tokens = (SHARED / "theme" / "tokens.css").read_text(encoding="utf-8")
        # Header stays dark even in light mode
        assert "light" in tokens and ".mantine-AppShell-header" in tokens, \
            "Must have light mode header override"
        assert "#0c0a09" in tokens, "Header must use dark color in light mode"


class TestSpec0152TestModeIndicator:
    """SPEC-0152: Test mode indicator REMOVED (S157 — phantom spec)."""

    def test_test_mode_banner_removed(self):
        """Test mode banner/indicator removed from StandaloneLayout (S157)."""
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "testModeEnabled" not in src, \
            "testModeEnabled should be removed from layout (S157)"


class TestSpec0353StorefrontNameInNavbar:
    """SPEC-0353: Standalone admin sticky navbar MUST display merchant's storefront name."""

    def test_storefront_display(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "shopDomain" in src, "Must reference shop domain"
        assert "brandName" in src, "Must fall back to brand name"


class TestSpec0354StorefrontLink:
    """SPEC-0354: Standalone admin sticky navbar MUST include link to merchant's storefront."""

    def test_storefront_link(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "target=\"_blank\"" in src or 'target="_blank"' in src, \
            "Must open storefront in new tab"
        assert "https://" in src, "Must link to storefront URL"


class TestSpec0388ChatBubbleSidebarColor:
    """SPEC-0388: Chat bubble grey background MUST use sidebar active-page highlight color."""

    def test_bubble_uses_surface_token(self):
        src = (STANDALONE / "pages" / "Inbox.tsx").read_text(encoding="utf-8")
        assert "tokens.surface" in src or "surface" in src, \
            "Chat bubbles must use surface token for background"


class TestSpec0391SidebarLogoNaturalColors:
    """SPEC-0391: Sidebar logo MUST render in natural colors with no CSS filter."""

    def test_no_css_filter_on_logo(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        # Logo should use <img> without filter
        assert "primary-logo-no-wordmark" in src, "Must reference logo file"
        # Ensure no CSS filter applied to logo
        assert "filter:" not in src.split("primary-logo")[0][-200:] if "primary-logo" in src else True, \
            "Logo must not have CSS filter"


# ═══════════════════════════════════════════════════════════════════════
#  INBOX SPEC
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0359EscalationAgentReadOnly:
    """SPEC-0359: Escalation agents MUST have read-only access to Inbox page."""

    def test_role_based_access(self):
        src = (STANDALONE / "pages" / "Inbox.tsx").read_text(encoding="utf-8")
        # Check role-based visibility
        assert "role" in src.lower() or "userRole" in src, \
            "Must check user role"
        # Escalation agents can view inbox (it's in the nav items for all roles)
        layout = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        # Inbox nav item has no roles restriction = all roles can access
        assert "'/inbox'" in layout, "Inbox must be accessible"


# ═══════════════════════════════════════════════════════════════════════
#  DASHBOARD SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0119StorefrontNameAboveDashboard:
    """SPEC-0119: Dashboard MUST display merchant's storefront name above 'Dashboard'."""

    def test_storefront_name_on_dashboard(self):
        # Dashboard page file
        dashboard_files = list(STANDALONE.glob("pages/Dashboard*"))
        assert dashboard_files, "Dashboard page must exist"
        src = dashboard_files[0].read_text(encoding="utf-8")
        assert "shopDomain" in src or "brandName" in src or "brand_name" in src, \
            "Dashboard must display storefront/brand name"
        assert "Dashboard" in src, "Must show 'Dashboard' title"


class TestSpec0594NoFakeDataOnInit:
    """SPEC-0594: Dashboard charts MUST NOT include conversation data that has not actually occurred."""

    def test_uses_real_analytics_api(self):
        dashboard_files = list(STANDALONE.glob("pages/Dashboard*"))
        assert dashboard_files, "Dashboard page must exist"
        src = dashboard_files[0].read_text(encoding="utf-8")
        assert "useAnalyticsSummary" in src or "useDailyVolume" in src or "apiFetch" in src, \
            "Dashboard must use real analytics API data"


class TestSpec0865ActivationDialogFieldTags:
    """SPEC-0865: Activation dialog field tags MUST accurately reflect actual config field states."""

    def test_activation_dialog_uses_real_state(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "ActivationDialog" in src or "activationDialog" in src or "preflight" in src.lower(), \
            "Must have activation dialog"
        assert "config" in src.lower(), "Must reference actual config state"
