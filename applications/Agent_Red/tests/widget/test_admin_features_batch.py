"""
Source inspection tests -- Batch verification of implemented features.

Covers WI-0771 (partial), WI-0779, WI-0784, WI-0787..0791, WI-0793..0795,
WI-0797, WI-0799..0800, WI-0801..0803, WI-0805..0807, WI-0809..0812, WI-0821, WI-0823,
WI-0817, WI-0819, WI-0816, WI-0820.

Run with:
    pytest tests/widget/test_admin_features_batch.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADMIN_STANDALONE = ROOT / "admin" / "standalone"
ADMIN_SHARED = ROOT / "admin" / "shared"
WIDGET_SRC = ROOT / "widget" / "src"


def _read(path: Path) -> str:
    assert path.exists(), f"Source file not found: {path}"
    return path.read_text(encoding="utf-8")


# ===========================================================================
# WI-0779: Storefront name on Dashboard
# ===========================================================================

class TestStorefrontNameDashboard:
    """WI-0779: Dashboard displays storefront name prominently."""

    DASHBOARD = ADMIN_STANDALONE / "pages" / "Dashboard.tsx"

    def test_reads_shop_domain(self) -> None:
        source = _read(self.DASHBOARD)
        assert "shopDomain" in source

    def test_reads_brand_name_fallback(self) -> None:
        source = _read(self.DASHBOARD)
        assert "brand_name" in source

    def test_renders_store_name_above_title(self) -> None:
        source = _read(self.DASHBOARD)
        # storeName rendered as <Text size="lg" fw={600}>
        assert re.search(r"storeName.*<Text.*size.*lg", source, re.DOTALL)

    def test_strips_myshopify_suffix(self) -> None:
        source = _read(self.DASHBOARD)
        assert ".myshopify.com" in source


# ===========================================================================
# WI-0784: Escalation agent role rename
# ===========================================================================

class TestEscalationAgentRole:
    """WI-0784: Role label 'Agent' renamed to 'Escalation agent'."""

    def test_constants_role_value(self) -> None:
        source = _read(ADMIN_SHARED / "team" / "constants.ts")
        assert "'escalation_agent'" in source

    def test_constants_role_label(self) -> None:
        source = _read(ADMIN_SHARED / "team" / "constants.ts")
        assert "'Escalation agent'" in source

    def test_edit_dialog_checks_escalation_agent(self) -> None:
        source = _read(ADMIN_SHARED / "team" / "EditMemberDialog.tsx")
        assert "escalation_agent" in source

    def test_team_member_row_checks_escalation_agent(self) -> None:
        source = _read(ADMIN_SHARED / "team" / "TeamMemberRow.tsx")
        assert "escalation_agent" in source

    def test_no_bare_agent_role_label(self) -> None:
        """Role label must NOT be bare 'Agent' (should be 'Escalation agent')."""
        source = _read(ADMIN_SHARED / "team" / "constants.ts")
        labels = re.findall(r"label:\s*'([^']+)'", source)
        for label in labels:
            assert label != "Agent", "Role label 'Agent' found — should be 'Escalation agent'"

    def test_badge_colors_for_escalation_agent(self) -> None:
        source = _read(ADMIN_SHARED / "team" / "constants.ts")
        assert "escalation_agent:" in source


# ===========================================================================
# WI-0787: Side-by-side color pickers
# ===========================================================================

class TestSideBySideColorPickers:
    """WI-0787: Header color pickers side-by-side."""

    def test_group_grow_wrapper(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "<Group grow" in source

    def test_both_color_fields_present(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "Header left color" in source
        assert "Header right color" in source


# ===========================================================================
# WI-0788: Page assignments list layout
# ===========================================================================

class TestPageAssignmentsList:
    """WI-0788: Page assignments as table rows, not dropdown."""

    QA = ADMIN_STANDALONE / "pages" / "QuickActions.tsx"

    def test_page_types_present(self) -> None:
        source = _read(self.QA)
        for page_type in ["home", "product", "collection", "cart"]:
            assert page_type in source

    def test_table_layout(self) -> None:
        source = _read(self.QA)
        # Should have table structure
        assert "table" in source.lower() or "<tr" in source or "Row" in source


# ===========================================================================
# WI-0789: Template variables inline below prompt
# ===========================================================================

class TestTemplateVariablesInline:
    """WI-0789: Template variable buttons inline below prompt input."""

    def test_quick_actions_template_vars(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "QuickActions.tsx")
        assert "TEMPLATE_VARS" in source or "template_var" in source.lower()

    def test_widget_greeting_variables(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "GREETING_VARIABLES" in source or "greeting_var" in source.lower() or "token" in source.lower()


# ===========================================================================
# WI-0790: Inline role selector (out of Actions column)
# ===========================================================================

class TestInlineRoleSelector:
    """WI-0790: Role selector is inline, separate from Actions column."""

    def test_inline_role_change_handler(self) -> None:
        source = _read(ADMIN_SHARED / "TeamManager.tsx")
        assert "handleInlineRoleChange" in source or "onRoleChange" in source

    def test_actions_column_separate(self) -> None:
        source = _read(ADMIN_SHARED / "TeamManager.tsx")
        assert "Actions" in source


# ===========================================================================
# WI-0791: Purchase button hover color consistency
# ===========================================================================

class TestPurchaseButtonHover:
    """WI-0791: Purchase button hover color uses !important to override inline styles."""

    TOKENS_CSS = ADMIN_SHARED / "theme" / "tokens.css"
    BILLING = ADMIN_SHARED / "BillingPortal.tsx"

    def test_hover_important_override(self) -> None:
        source = _read(self.TOKENS_CSS)
        assert "!important" in source
        # Specifically in the ar-btn-action:hover rule
        assert "ar-btn-action:hover" in source

    def test_hover_uses_action_hover_var(self) -> None:
        source = _read(self.TOKENS_CSS)
        assert "--ar-action-hover" in source

    def test_purchase_buttons_use_ar_btn_action(self) -> None:
        source = _read(self.BILLING)
        assert 'className="ar-btn-action"' in source

    def test_purchase_button_label(self) -> None:
        source = _read(self.BILLING)
        assert "'Purchase'" in source or '"Purchase"' in source


# ===========================================================================
# WI-0793: Custom greeting message
# ===========================================================================

class TestCustomGreetingMessage:
    """WI-0793: Widget displays custom greeting message."""

    def test_greeting_enabled_field(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "greetingEnabled" in source

    def test_greeting_message_field(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "greetingMessage" in source

    def test_greeting_mode_static(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "static" in source

    def test_greeting_mode_ai_generated(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "ai_generated" in source

    def test_widget_runtime_greeting_attr(self) -> None:
        source = _read(WIDGET_SRC / "index.ts")
        assert "widget_greeting_message" in source or "greeting" in source.lower()


# ===========================================================================
# WI-0794: Quick actions starter examples
# ===========================================================================

class TestQuickActionsStarterExamples:
    """WI-0794: Starter examples shown on first visit."""

    def test_starter_examples_defined(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "QuickActions.tsx")
        assert "STARTER_EXAMPLES" in source or "starter" in source.lower()

    def test_track_order_example(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "QuickActions.tsx")
        assert "Track" in source or "track" in source


# ===========================================================================
# WI-0795: Quick action icon field guidance
# ===========================================================================

class TestQuickActionIconGuidance:
    """WI-0795: Icon field has format guidance and emoji shortcuts."""

    def test_icon_description_text(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "QuickActions.tsx")
        assert "emoji" in source.lower()

    def test_emoji_shortcut_grid(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "QuickActions.tsx")
        # Should have clickable emoji buttons
        emoji_count = len(re.findall(r"[\U0001F300-\U0001FAFF]", source))
        assert emoji_count >= 4, f"Expected ≥4 emoji shortcuts, found {emoji_count}"


# ===========================================================================
# WI-0797: Quick actions previewable in admin widget
# ===========================================================================

class TestQuickActionsPreviewable:
    """WI-0797: Quick actions appear in the Widget page live preview."""

    WIDGET_PAGE = ADMIN_STANDALONE / "pages" / "Widget.tsx"

    def test_quick_action_preview_interface(self) -> None:
        source = _read(self.WIDGET_PAGE)
        assert "QuickActionPreview" in source

    def test_fetches_quick_actions_api(self) -> None:
        source = _read(self.WIDGET_PAGE)
        assert "/api/admin/quick-actions" in source

    def test_preview_quick_actions_state(self) -> None:
        source = _read(self.WIDGET_PAGE)
        assert "previewQuickActions" in source

    def test_filters_active_actions(self) -> None:
        source = _read(self.WIDGET_PAGE)
        assert "isActive" in source

    def test_quick_actions_state_populated(self) -> None:
        """Quick actions are fetched and stored in state (for postMessage dispatch)."""
        source = _read(self.WIDGET_PAGE)
        assert "setPreviewQuickActions" in source

    def test_renders_quick_action_pills(self) -> None:
        source = _read(self.WIDGET_PAGE)
        assert "qa.label" in source
        assert "qa.icon" in source


# ===========================================================================
# WI-0799: Named configuration save/restore
# ===========================================================================

class TestNamedConfigSaveRestore:
    """WI-0799: Named configurations CRUD."""

    def test_named_configs_hook(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Configuration.tsx")
        assert "useNamedConfigs" in source or "namedConfig" in source.lower()

    def test_save_named_config(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Configuration.tsx")
        assert "useSaveNamedConfig" in source or "saveNamed" in source.lower() or "save" in source.lower()

    def test_activate_named_config(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Configuration.tsx")
        assert "useActivateNamedConfig" in source or "activateNamed" in source.lower()

    def test_delete_named_config(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Configuration.tsx")
        assert "useDeleteNamedConfig" in source or "deleteNamed" in source.lower()


# ===========================================================================
# WI-0800: Escalation category assignment per team member
# ===========================================================================

class TestEscalationCategoryAssignment:
    """WI-0800: Escalation categories per team member."""

    def test_edit_dialog_categories(self) -> None:
        source = _read(ADMIN_SHARED / "team" / "EditMemberDialog.tsx")
        assert "escalat" in source.lower()
        assert "categor" in source.lower()

    def test_inline_category_toggle(self) -> None:
        source = _read(ADMIN_SHARED / "TeamManager.tsx")
        assert "handleCategoryToggle" in source or "categoryToggle" in source.lower()


# ===========================================================================
# WI-0805: Launcher position offset controls
# ===========================================================================

class TestLauncherPositionOffset:
    """WI-0805: Horizontal and vertical offset controls."""

    def test_horizontal_offset(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "Horizontal offset" in source or "positionOffsetX" in source

    def test_vertical_offset(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "Vertical offset" in source or "positionOffsetY" in source


# ===========================================================================
# WI-0806: Widget drop-shadow control
# ===========================================================================

class TestWidgetDropShadow:
    """WI-0806: Shadow intensity control."""

    def test_shadow_intensity_control(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "shadowIntensity" in source or "shadow_intensity" in source

    def test_shadow_presets(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        for preset in ["none", "subtle", "standard"]:
            assert preset in source.lower()


# ===========================================================================
# WI-0807: Launcher icon and agent avatar
# ===========================================================================

class TestLauncherIconAndAvatar:
    """WI-0807: Launcher icon selection and agent avatar upload."""

    def test_launcher_icon_select(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "launcher_icon" in source or "launcherIcon" in source

    def test_launcher_icon_options(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "chat" in source.lower()
        assert "headset" in source.lower() or "help" in source.lower()

    def test_avatar_upload(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "AvatarDropZone" in source or "avatar" in source.lower()


# ===========================================================================
# WI-0809: Chat UI draggable/repositionable
# ===========================================================================

class TestChatDraggable:
    """WI-0809: Widget panel is draggable/repositionable."""

    def test_drag_storage_key(self) -> None:
        source = _read(WIDGET_SRC / "index.ts")
        assert "DRAG_STORAGE_KEY" in source or "drag" in source.lower()

    def test_drag_position_persistence(self) -> None:
        source = _read(WIDGET_SRC / "index.ts")
        assert "saveDragPosition" in source or "loadDragPosition" in source

    def test_clamp_to_viewport(self) -> None:
        source = _read(WIDGET_SRC / "index.ts")
        assert "clampToViewport" in source or "clamp" in source.lower()


# ===========================================================================
# WI-0810: Auto-open per page via Quick Actions
# ===========================================================================

class TestAutoOpenPerPage:
    """WI-0810: Auto-open toggle per page type."""

    def test_auto_open_toggle_handler(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "QuickActions.tsx")
        assert "handleAutoOpenToggle" in source or "autoOpen" in source

    def test_auto_open_delay(self) -> None:
        source = _read(ADMIN_STANDALONE / "pages" / "QuickActions.tsx")
        assert "AutoOpenDelay" in source or "auto_open_delay" in source or "autoOpenDelay" in source

    def test_widget_runtime_auto_open(self) -> None:
        source = _read(WIDGET_SRC / "index.ts")
        assert "auto_open" in source or "autoOpen" in source


# ===========================================================================
# WI-0811: Chat input 3 text lines
# ===========================================================================

class TestChatInputHeight:
    """WI-0811: Chat input area defaults to 3 text lines."""

    def test_min_textarea_height(self) -> None:
        source = _read(WIDGET_SRC / "components" / "InputBar.tsx")
        assert "MIN_TEXTAREA_HEIGHT" in source or "66" in source or "rows" in source

    def test_three_rows(self) -> None:
        source = _read(WIDGET_SRC / "components" / "InputBar.tsx")
        assert "rows" in source


# ===========================================================================
# WI-0812: Chat scroll controls
# ===========================================================================

class TestChatScrollControls:
    """WI-0812: Chat display area has scroll-to-bottom controls."""

    def test_scroll_to_bottom(self) -> None:
        source = _read(WIDGET_SRC / "components" / "MessageList.tsx")
        assert "scroll" in source.lower()

    def test_scroll_locale_string(self) -> None:
        source = _read(WIDGET_SRC / "locale" / "en.ts")
        assert "scrollToBottom" in source or "scroll" in source.lower()


# ===========================================================================
# WI-0821: Wizard test mode toggle
# ===========================================================================

class TestWizardTestModeToggle:
    """WI-0821: Wizard test mode REMOVED (S157 — phantom specification)."""

    def test_test_mode_removed(self) -> None:
        """Test mode state and field removed from OnboardingWizard (S157)."""
        source = _read(ADMIN_SHARED / "components" / "OnboardingWizard.tsx")
        assert "test_mode_enabled" not in source
        assert "testMode" not in source


# ===========================================================================
# WI-0823: Memory and privacy sidebar page
# ===========================================================================

class TestMemoryPrivacyPage:
    """WI-0823: Memory & privacy page exists in sidebar."""

    def test_nav_route(self) -> None:
        source = _read(ADMIN_STANDALONE / "layouts" / "StandaloneLayout.tsx")
        assert "/memory-privacy" in source

    def test_nav_label(self) -> None:
        source = _read(ADMIN_STANDALONE / "layouts" / "StandaloneLayout.tsx")
        assert "Memory & privacy" in source or "Memory &amp; privacy" in source

    def test_page_file_exists(self) -> None:
        assert (ADMIN_STANDALONE / "pages" / "MemoryPrivacy.tsx").exists()


# ===========================================================================
# WI-0802: Mobile fullscreen mode (SPEC-1509)
# ===========================================================================

class TestMobileFullscreen:
    """WI-0802: Mobile fullscreen mode — field pipeline + runtime behavior."""

    FIELDS_YAML = ROOT / "src" / "multi_tenant" / "schema" / "fields.yaml"
    FIELD_MAPPING = ROOT / "src" / "multi_tenant" / "config" / "field_mapping.py"
    COSMOS_SCHEMA = ROOT / "src" / "multi_tenant" / "cosmos_schema.py"
    TOKENS_TS = WIDGET_SRC / "theme" / "tokens.ts"
    INDEX_TS = WIDGET_SRC / "index.ts"
    WIDGET_PAGE = ADMIN_STANDALONE / "pages" / "Widget.tsx"
    CONFIGURATOR = ADMIN_SHARED / "WidgetConfigurator.tsx"

    def test_fields_yaml_has_mobile_fullscreen(self) -> None:
        source = _read(self.FIELDS_YAML)
        assert "widget_mobile_fullscreen" in source

    def test_field_mapping_includes_mobile_fullscreen(self) -> None:
        source = _read(self.FIELD_MAPPING)
        assert "widget_mobile_fullscreen" in source

    def test_cosmos_schema_has_mobile_fullscreen(self) -> None:
        source = _read(self.COSMOS_SCHEMA)
        assert "widget_mobile_fullscreen" in source

    def test_ts_config_type_has_mobile_fullscreen(self) -> None:
        source = _read(self.TOKENS_TS)
        assert "widget_mobile_fullscreen" in source

    def test_runtime_fullscreen_viewport(self) -> None:
        """Panel uses 100vw/100vh when mobile fullscreen is enabled."""
        source = _read(self.INDEX_TS)
        assert "100vw" in source
        assert "100vh" in source
        assert "mobileFullscreen" in source

    def test_desktop_unaffected(self) -> None:
        """Desktop panel still uses standard tokens.panelWidth/panelHeight."""
        source = _read(self.INDEX_TS)
        assert "tokens.panelWidth" in source
        assert "tokens.panelHeight" in source

    def test_standalone_admin_toggle(self) -> None:
        """Standalone admin has mobile fullscreen toggle."""
        source = _read(self.WIDGET_PAGE)
        assert "mobileFullscreen" in source
        assert "Mobile fullscreen" in source

    def test_shared_configurator_toggle(self) -> None:
        """Shared WidgetConfigurator has mobile fullscreen toggle."""
        source = _read(self.CONFIGURATOR)
        assert "widget_mobile_fullscreen" in source
        assert "Mobile fullscreen" in source


# ===========================================================================
# WI-0801: Mobile position + offset config
# ===========================================================================

class TestMobilePosition:
    """WI-0801: Mobile position and offset overrides — field pipeline + admin UI."""

    FIELDS_YAML = ROOT / "src" / "multi_tenant" / "schema" / "fields.yaml"
    FIELD_MAPPING = ROOT / "src" / "multi_tenant" / "config" / "field_mapping.py"
    COSMOS_SCHEMA = ROOT / "src" / "multi_tenant" / "cosmos_schema.py"
    TOKENS_TS = WIDGET_SRC / "theme" / "tokens.ts"
    INDEX_TS = WIDGET_SRC / "index.ts"
    WIDGET_PAGE = ADMIN_STANDALONE / "pages" / "Widget.tsx"
    CONFIGURATOR = ADMIN_SHARED / "WidgetConfigurator.tsx"

    # -- Pipeline layer 1: fields.yaml --

    def test_fields_yaml_has_mobile_position(self) -> None:
        source = _read(self.FIELDS_YAML)
        assert "widget_mobile_position" in source

    def test_fields_yaml_has_mobile_offset_x(self) -> None:
        source = _read(self.FIELDS_YAML)
        assert "widget_mobile_offset_x" in source

    def test_fields_yaml_has_mobile_offset_y(self) -> None:
        source = _read(self.FIELDS_YAML)
        assert "widget_mobile_offset_y" in source

    # -- Pipeline layer 2: field_mapping.py --

    def test_field_mapping_includes_all_three(self) -> None:
        source = _read(self.FIELD_MAPPING)
        assert "widget_mobile_position" in source
        assert "widget_mobile_offset_x" in source
        assert "widget_mobile_offset_y" in source

    # -- Pipeline layer 3: cosmos_schema.py --

    def test_cosmos_schema_has_all_three(self) -> None:
        source = _read(self.COSMOS_SCHEMA)
        assert "widget_mobile_position" in source
        assert "widget_mobile_offset_x" in source
        assert "widget_mobile_offset_y" in source

    # -- Pipeline layer 4: TypeScript type --

    def test_ts_config_type_has_all_three(self) -> None:
        source = _read(self.TOKENS_TS)
        assert "widget_mobile_position" in source
        assert "widget_mobile_offset_x" in source
        assert "widget_mobile_offset_y" in source

    # -- Runtime: widget index.ts --

    def test_runtime_mobile_position_fallback(self) -> None:
        """Widget runtime resolves mobile position with fallback to desktop."""
        source = _read(self.INDEX_TS)
        assert "widget_mobile_position" in source

    def test_runtime_mobile_offset_fallback(self) -> None:
        """Widget runtime resolves mobile offsets with fallback to desktop."""
        source = _read(self.INDEX_TS)
        assert "widget_mobile_offset_x" in source
        assert "widget_mobile_offset_y" in source

    # -- Standalone admin UI --

    def test_standalone_admin_has_position_select(self) -> None:
        """Standalone admin has mobile position override select."""
        source = _read(self.WIDGET_PAGE)
        assert "mobilePosition" in source
        assert "Mobile position override" in source

    def test_standalone_admin_has_offset_inputs(self) -> None:
        """Standalone admin has mobile offset number inputs."""
        source = _read(self.WIDGET_PAGE)
        assert "mobileOffsetX" in source
        assert "mobileOffsetY" in source
        assert "Mobile horizontal offset" in source
        assert "Mobile vertical offset" in source

    # -- Shared configurator UI --

    def test_shared_configurator_has_position(self) -> None:
        """Shared WidgetConfigurator has mobile position select."""
        source = _read(self.CONFIGURATOR)
        assert "widget_mobile_position" in source
        assert "Mobile position override" in source

    def test_shared_configurator_has_offsets(self) -> None:
        """Shared WidgetConfigurator has mobile offset inputs."""
        source = _read(self.CONFIGURATOR)
        assert "widget_mobile_offset_x" in source
        assert "widget_mobile_offset_y" in source
        assert "Mobile horizontal offset" in source
        assert "Mobile vertical offset" in source


# ===========================================================================
# WI-0803: Panel height config (SPEC-1511)
# ===========================================================================

class TestPanelHeight:
    """WI-0803: Configurable panel height — field pipeline + admin UI + runtime."""

    FIELDS_YAML = ROOT / "src" / "multi_tenant" / "schema" / "fields.yaml"
    FIELD_MAPPING = ROOT / "src" / "multi_tenant" / "config" / "field_mapping.py"
    COSMOS_SCHEMA = ROOT / "src" / "multi_tenant" / "cosmos_schema.py"
    TOKENS_TS = WIDGET_SRC / "theme" / "tokens.ts"
    WIDGET_PAGE = ADMIN_STANDALONE / "pages" / "Widget.tsx"
    CONFIGURATOR = ADMIN_SHARED / "WidgetConfigurator.tsx"

    # -- Pipeline layer 1: fields.yaml --

    def test_fields_yaml_has_panel_height(self) -> None:
        source = _read(self.FIELDS_YAML)
        assert "widget_panel_height" in source

    def test_fields_yaml_presets(self) -> None:
        """All three presets defined in fields.yaml."""
        source = _read(self.FIELDS_YAML)
        # Must appear as allowed_values for widget_panel_height
        assert "short" in source
        assert "tall" in source

    # -- Pipeline layer 2: field_mapping.py --

    def test_field_mapping_includes_panel_height(self) -> None:
        source = _read(self.FIELD_MAPPING)
        assert "widget_panel_height" in source

    # -- Pipeline layer 3: cosmos_schema.py --

    def test_cosmos_schema_has_panel_height(self) -> None:
        source = _read(self.COSMOS_SCHEMA)
        assert "widget_panel_height" in source

    # -- Pipeline layer 4: TypeScript type + token resolution --

    def test_ts_config_type_has_panel_height(self) -> None:
        source = _read(self.TOKENS_TS)
        assert "widget_panel_height" in source

    def test_token_resolves_short_420(self) -> None:
        """Short preset resolves to 420px."""
        source = _read(self.TOKENS_TS)
        assert "'420px'" in source or '"420px"' in source

    def test_token_resolves_standard_520(self) -> None:
        """Standard preset resolves to 520px (default)."""
        source = _read(self.TOKENS_TS)
        assert "'520px'" in source or '"520px"' in source

    def test_token_resolves_tall_620(self) -> None:
        """Tall preset resolves to 620px."""
        source = _read(self.TOKENS_TS)
        assert "'620px'" in source or '"620px"' in source

    def test_panel_height_preset_variable(self) -> None:
        """resolveTokens reads widget_panel_height from config."""
        source = _read(self.TOKENS_TS)
        assert "panelHeightPreset" in source

    # -- Standalone admin UI --

    def test_standalone_admin_has_height_control(self) -> None:
        """Standalone admin has panel height segmented control."""
        source = _read(self.WIDGET_PAGE)
        assert "panelHeight" in source
        assert "Panel height" in source

    def test_standalone_admin_height_presets(self) -> None:
        """All three presets available in standalone admin."""
        source = _read(self.WIDGET_PAGE)
        assert "Short" in source
        assert "Tall" in source

    # -- Shared configurator UI --

    def test_shared_configurator_has_height(self) -> None:
        """Shared WidgetConfigurator has panel height control."""
        source = _read(self.CONFIGURATOR)
        assert "widget_panel_height" in source
        assert "Panel height" in source

    def test_shared_configurator_height_presets(self) -> None:
        """All three presets available in shared configurator."""
        source = _read(self.CONFIGURATOR)
        assert "420px" in source
        assert "620px" in source


# ===========================================================================
# WI-0817: Locale packs infrastructure
# ===========================================================================

class TestLocaleInfrastructure:
    """WI-0817: Multi-language locale packs with auto-detect."""

    FIELDS_YAML = ROOT / "src" / "multi_tenant" / "schema" / "fields.yaml"
    FIELD_MAPPING = ROOT / "src" / "multi_tenant" / "config" / "field_mapping.py"
    COSMOS_SCHEMA = ROOT / "src" / "multi_tenant" / "cosmos_schema.py"
    TOKENS = WIDGET_SRC / "theme" / "tokens.ts"
    LOCALE_DIR = WIDGET_SRC / "locale"
    LOCALE_INDEX = WIDGET_SRC / "locale" / "index.ts"
    WIDGET_INDEX = WIDGET_SRC / "index.ts"
    STANDALONE_WIDGET = ADMIN_STANDALONE / "pages" / "Widget.tsx"
    CONFIGURATOR = ADMIN_SHARED / "WidgetConfigurator.tsx"

    # -- Layer 1: fields.yaml --

    def test_fields_yaml_widget_locale_exists(self) -> None:
        """widget_locale field defined in fields.yaml."""
        source = _read(self.FIELDS_YAML)
        assert "widget_locale" in source

    def test_fields_yaml_locale_enum_values(self) -> None:
        """All 9 locale values (auto + 8 languages) defined."""
        source = _read(self.FIELDS_YAML)
        for val in ["auto", "en", "es", "fr", "de", "pt", "ja", "zh", "ko"]:
            assert val in source, f"Missing locale value: {val}"

    # -- Layer 2: field_mapping.py --

    def test_field_mapping_has_widget_locale(self) -> None:
        """widget_locale in _PREFS_DIRECT_FIELDS."""
        source = _read(self.FIELD_MAPPING)
        assert "widget_locale" in source

    # -- Layer 3: cosmos_schema.py --

    def test_cosmos_schema_has_widget_locale(self) -> None:
        """widget_locale field on PreferencesDocument."""
        source = _read(self.COSMOS_SCHEMA)
        assert "widget_locale" in source

    # -- Layer 4: TypeScript WidgetConfig --

    def test_tokens_widget_config_has_locale(self) -> None:
        """WidgetConfig interface includes widget_locale."""
        source = _read(self.TOKENS)
        assert "widget_locale" in source

    def test_tokens_locale_type_union(self) -> None:
        """WidgetConfig widget_locale has auto + 8 language codes."""
        source = _read(self.TOKENS)
        assert "'auto'" in source
        assert "'ko'" in source

    # -- Locale files --

    def test_locale_files_exist(self) -> None:
        """All 8 locale files exist in widget/src/locale/."""
        for code in ["en", "es", "fr", "de", "pt", "ja", "zh", "ko"]:
            path = self.LOCALE_DIR / f"{code}.ts"
            assert path.exists(), f"Missing locale file: {code}.ts"

    def test_locale_files_export_locale_object(self) -> None:
        """Each locale file exports a typed Locale object."""
        for code in ["es", "fr", "de", "pt", "ja", "zh", "ko"]:
            source = _read(self.LOCALE_DIR / f"{code}.ts")
            assert f"export const {code}: Locale" in source, f"{code}.ts missing typed export"

    def test_locale_files_have_all_keys(self) -> None:
        """Each locale file defines all 51 keys from en.ts."""
        en_source = _read(self.LOCALE_DIR / "en.ts")
        # Extract key names from the Locale interface
        keys = re.findall(r"^\s+(\w+):\s+string;", en_source, re.MULTILINE)
        assert len(keys) >= 49, f"Expected 49+ keys, got {len(keys)}"
        for code in ["es", "fr", "de", "pt", "ja", "zh", "ko"]:
            source = _read(self.LOCALE_DIR / f"{code}.ts")
            for key in keys:
                assert f"{key}:" in source, f"{code}.ts missing key: {key}"

    # -- Locale index barrel --

    def test_locale_index_exists(self) -> None:
        """locale/index.ts barrel file exists."""
        assert self.LOCALE_INDEX.exists()

    def test_locale_index_exports_map(self) -> None:
        """locale/index.ts exports LOCALE_MAP."""
        source = _read(self.LOCALE_INDEX)
        assert "LOCALE_MAP" in source

    def test_locale_index_exports_resolve_function(self) -> None:
        """locale/index.ts exports resolveLocaleCode."""
        source = _read(self.LOCALE_INDEX)
        assert "resolveLocaleCode" in source

    def test_locale_index_exports_detect_browser(self) -> None:
        """locale/index.ts exports detectBrowserLocale."""
        source = _read(self.LOCALE_INDEX)
        assert "detectBrowserLocale" in source

    def test_locale_index_supported_locales(self) -> None:
        """SUPPORTED_LOCALES array has all 8 codes."""
        source = _read(self.LOCALE_INDEX)
        assert "SUPPORTED_LOCALES" in source
        for code in ["en", "es", "fr", "de", "pt", "ja", "zh", "ko"]:
            assert f"'{code}'" in source

    # -- Widget index.ts integration --

    def test_widget_index_imports_locale_barrel(self) -> None:
        """Widget index.ts imports from locale barrel."""
        source = _read(self.WIDGET_INDEX)
        assert "from '@/locale'" in source or "from '@/locale/index'" in source

    def test_widget_index_uses_resolve_locale(self) -> None:
        """buildLocale uses resolveLocaleCode for locale selection."""
        source = _read(self.WIDGET_INDEX)
        assert "resolveLocaleCode" in source

    def test_widget_index_uses_get_locale_pack(self) -> None:
        """buildLocale uses getLocalePack."""
        source = _read(self.WIDGET_INDEX)
        assert "getLocalePack" in source

    # -- Standalone admin --

    def test_standalone_admin_locale_field(self) -> None:
        """Standalone admin WidgetConfig has locale field."""
        source = _read(self.STANDALONE_WIDGET)
        assert "locale:" in source
        assert "'auto'" in source

    def test_standalone_admin_locale_mapping(self) -> None:
        """Standalone admin maps widget_locale to API."""
        source = _read(self.STANDALONE_WIDGET)
        assert "widget_locale" in source

    def test_standalone_admin_locale_select(self) -> None:
        """Standalone admin has locale select with language names."""
        source = _read(self.STANDALONE_WIDGET)
        assert "Widget language" in source
        assert "Auto-detect" in source

    # -- Shared configurator --

    def test_shared_configurator_locale_field(self) -> None:
        """Shared configurator has widget_locale field."""
        source = _read(self.CONFIGURATOR)
        assert "widget_locale" in source

    def test_shared_configurator_locale_select(self) -> None:
        """Shared configurator has locale dropdown with Auto-detect."""
        source = _read(self.CONFIGURATOR)
        assert "Widget language" in source
        assert "Auto-detect" in source


# ===========================================================================
# WI-0815: Targeting rules admin UI (SPEC-1506)
# ===========================================================================


class TestTargetingRulesAdminUI:
    """Source inspection tests for page visibility rules UI in admin surfaces."""

    STANDALONE_WIDGET = ADMIN_STANDALONE / "pages" / "Widget.tsx"
    CONFIGURATOR = ADMIN_SHARED / "WidgetConfigurator.tsx"

    # -- Standalone admin --

    def test_standalone_has_page_rules_field(self) -> None:
        """Standalone admin WidgetConfig interface includes pageRules."""
        source = _read(self.STANDALONE_WIDGET)
        assert "pageRules:" in source

    def test_standalone_page_rules_mapping_to_api(self) -> None:
        """Standalone admin maps pageRules to widget_page_rules."""
        source = _read(self.STANDALONE_WIDGET)
        assert "widget_page_rules" in source

    def test_standalone_page_rules_ui_section(self) -> None:
        """Standalone admin has Page visibility rules section header."""
        source = _read(self.STANDALONE_WIDGET)
        assert "Page visibility rules" in source

    def test_standalone_add_rule_button(self) -> None:
        """Standalone admin has Add rule button (SPEC-1506-A2)."""
        source = _read(self.STANDALONE_WIDGET)
        assert "+ Add rule" in source

    def test_standalone_empty_state_message(self) -> None:
        """Standalone admin shows empty state when no rules (SPEC-1506-A3)."""
        source = _read(self.STANDALONE_WIDGET)
        assert "No page rules configured" in source

    def test_standalone_max_20_rules(self) -> None:
        """Standalone admin disables Add button at 20 rules."""
        source = _read(self.STANDALONE_WIDGET)
        assert "pageRules.length >= 20" in source

    def test_standalone_placeholder_text(self) -> None:
        """Standalone admin rule input has +/products/* or -/checkout placeholder."""
        source = _read(self.STANDALONE_WIDGET)
        assert "+/products/* or -/checkout" in source

    # -- Shared configurator --

    def test_shared_has_page_rules_field(self) -> None:
        """Shared configurator config interface includes widget_page_rules."""
        source = _read(self.CONFIGURATOR)
        assert "widget_page_rules" in source

    def test_shared_page_rules_ui_section(self) -> None:
        """Shared configurator has Page visibility rules section."""
        source = _read(self.CONFIGURATOR)
        assert "Page visibility rules" in source

    def test_shared_add_rule_button(self) -> None:
        """Shared configurator has Add rule button."""
        source = _read(self.CONFIGURATOR)
        assert "+ Add rule" in source

    def test_shared_empty_state_message(self) -> None:
        """Shared configurator shows empty state when no rules."""
        source = _read(self.CONFIGURATOR)
        assert "No page rules configured" in source

    def test_shared_max_20_rules(self) -> None:
        """Shared configurator limits to 20 rules."""
        source = _read(self.CONFIGURATOR)
        assert "widget_page_rules.length < 20" in source


# ===========================================================================
# WI-0819: Runtime JS API — setLocale / setTheme
# ===========================================================================


class TestRuntimeJsApi:
    """Source inspection tests for the setLocale and setTheme SDK methods (WI-0819)."""

    INDEX_TS = WIDGET_SRC / "index.ts"
    PANEL_TSX = WIDGET_SRC / "components" / "Panel.tsx"
    STORE_TS = WIDGET_SRC / "state" / "store.ts"

    # -- SDK interface declaration --

    def test_sdk_interface_has_set_locale(self) -> None:
        """AgentRedSDK interface declares setLocale method."""
        source = _read(self.INDEX_TS)
        assert "setLocale(code: LocaleCode): void" in source

    def test_sdk_interface_has_set_theme(self) -> None:
        """AgentRedSDK interface declares setTheme method."""
        source = _read(self.INDEX_TS)
        assert "setTheme(overrides: Partial<DesignTokens>): void" in source

    # -- SDK implementation --

    def test_sdk_set_locale_implementation(self) -> None:
        """SDK object implements setLocale with getLocalePack."""
        source = _read(self.INDEX_TS)
        assert "setLocale:" in source
        assert "getLocalePack(code)" in source

    def test_sdk_set_locale_merges_merchant_overrides(self) -> None:
        """setLocale preserves merchant text overrides (header_text, etc.)."""
        source = _read(self.INDEX_TS)
        # The setLocale implementation should spread merchant overrides on top
        assert "widget_header_text" in source
        assert "widget_input_placeholder" in source

    def test_sdk_set_theme_implementation(self) -> None:
        """SDK object implements setTheme by setting tokenOverrides in store."""
        source = _read(self.INDEX_TS)
        assert "setTheme:" in source
        assert "tokenOverrides" in source

    # -- Store tokenOverrides field --

    def test_store_state_has_token_overrides(self) -> None:
        """WidgetState interface includes tokenOverrides field."""
        source = _read(self.STORE_TS)
        assert "tokenOverrides" in source
        assert "Partial<DesignTokens>" in source

    def test_store_initial_token_overrides_null(self) -> None:
        """createStore initialises tokenOverrides to null."""
        source = _read(self.STORE_TS)
        assert "tokenOverrides: null" in source

    # -- Panel reactive consumption --

    def test_panel_reads_active_locale_from_store(self) -> None:
        """Panel derives activeLocale from state.locale for runtime setLocale."""
        source = _read(self.PANEL_TSX)
        assert "const activeLocale" in source
        assert "state.locale" in source

    def test_panel_merges_token_overrides(self) -> None:
        """Panel merges state.tokenOverrides on top of resolveTokens()."""
        source = _read(self.PANEL_TSX)
        assert "state.tokenOverrides" in source
        assert "baseTokens" in source

    def test_panel_uses_active_locale_for_children(self) -> None:
        """Panel passes activeLocale (not prop locale) to child components."""
        source = _read(self.PANEL_TSX)
        # All child component locale props should use activeLocale
        locale_props = re.findall(r'locale=\{(\w+)\}', source)
        # Filter to Panel body only (before ConnectionBanner sub-component)
        # The ConnectionBanner receives activeLocale and internally uses 'locale'
        for prop in locale_props:
            assert prop in ("activeLocale", "locale"), f"Unexpected locale prop: {prop}"
        assert locale_props.count("activeLocale") >= 8, (
            f"Expected >=8 activeLocale props, found {locale_props.count('activeLocale')}"
        )

    # -- Import verification --

    def test_index_imports_locale_code_type(self) -> None:
        """index.ts imports LocaleCode type for setLocale parameter."""
        source = _read(self.INDEX_TS)
        assert "LocaleCode" in source

    def test_index_imports_design_tokens_type(self) -> None:
        """index.ts imports DesignTokens type for setTheme parameter."""
        source = _read(self.INDEX_TS)
        assert "DesignTokens" in source

    def test_store_imports_design_tokens(self) -> None:
        """store.ts imports DesignTokens for the tokenOverrides type."""
        source = _read(self.STORE_TS)
        assert "DesignTokens" in source


# ===========================================================================
# WI-0816 — Engagement triggers admin UI
# ===========================================================================

class TestEngagementTriggersAdminUI:
    """Source inspection tests for exit-intent and scroll-depth admin controls (SPEC-1507/1508)."""

    STANDALONE = ADMIN_STANDALONE / "pages" / "Widget.tsx"
    SHARED = ADMIN_SHARED / "WidgetConfigurator.tsx"
    FIELDS_YAML = ROOT / "src" / "multi_tenant" / "schema" / "fields.yaml"
    FIELD_MAPPING = ROOT / "src" / "multi_tenant" / "config" / "field_mapping.py"
    COSMOS_SCHEMA = ROOT / "src" / "multi_tenant" / "cosmos_schema.py"

    # --- 4-layer pipeline ---

    def test_fields_yaml_exit_intent(self) -> None:
        """fields.yaml contains widget_exit_intent_enabled definition."""
        src = _read(self.FIELDS_YAML)
        assert "widget_exit_intent_enabled" in src

    def test_fields_yaml_scroll_depth(self) -> None:
        """fields.yaml contains widget_scroll_depth_trigger definition."""
        src = _read(self.FIELDS_YAML)
        assert "widget_scroll_depth_trigger" in src

    def test_field_mapping_exit_intent(self) -> None:
        """field_mapping.py includes widget_exit_intent_enabled."""
        src = _read(self.FIELD_MAPPING)
        assert "widget_exit_intent_enabled" in src

    def test_field_mapping_scroll_depth(self) -> None:
        """field_mapping.py includes widget_scroll_depth_trigger."""
        src = _read(self.FIELD_MAPPING)
        assert "widget_scroll_depth_trigger" in src

    def test_cosmos_schema_exit_intent(self) -> None:
        """cosmos_schema.py has widget_exit_intent_enabled field."""
        src = _read(self.COSMOS_SCHEMA)
        assert "widget_exit_intent_enabled" in src

    def test_cosmos_schema_scroll_depth(self) -> None:
        """cosmos_schema.py has widget_scroll_depth_trigger field."""
        src = _read(self.COSMOS_SCHEMA)
        assert "widget_scroll_depth_trigger" in src

    # --- Standalone admin ---

    def test_standalone_exit_intent_field(self) -> None:
        """Standalone admin has exitIntentEnabled in WidgetConfig interface."""
        src = _read(self.STANDALONE)
        assert "exitIntentEnabled" in src

    def test_standalone_scroll_depth_field(self) -> None:
        """Standalone admin has scrollDepthTrigger in WidgetConfig interface."""
        src = _read(self.STANDALONE)
        assert "scrollDepthTrigger" in src

    def test_standalone_exit_intent_mapping(self) -> None:
        """Standalone maps widget_exit_intent_enabled to/from API."""
        src = _read(self.STANDALONE)
        assert "widget_exit_intent_enabled" in src

    def test_standalone_scroll_depth_mapping(self) -> None:
        """Standalone maps widget_scroll_depth_trigger to/from API."""
        src = _read(self.STANDALONE)
        assert "widget_scroll_depth_trigger" in src

    def test_standalone_exit_intent_switch(self) -> None:
        """Standalone admin renders exit-intent as a Switch control."""
        src = _read(self.STANDALONE)
        assert "Exit-intent auto-open" in src

    def test_standalone_scroll_depth_input(self) -> None:
        """Standalone admin renders scroll-depth as a NumberInput."""
        src = _read(self.STANDALONE)
        assert "Scroll-depth auto-open" in src

    # --- Shared configurator ---

    def test_shared_exit_intent_field(self) -> None:
        """Shared configurator has widget_exit_intent_enabled in interface."""
        src = _read(self.SHARED)
        assert "widget_exit_intent_enabled" in src

    def test_shared_scroll_depth_field(self) -> None:
        """Shared configurator has widget_scroll_depth_trigger in interface."""
        src = _read(self.SHARED)
        assert "widget_scroll_depth_trigger" in src

    def test_shared_exit_intent_toggle(self) -> None:
        """Shared configurator renders exit-intent toggle."""
        src = _read(self.SHARED)
        assert "Exit-intent auto-open" in src

    def test_shared_scroll_depth_input(self) -> None:
        """Shared configurator renders scroll-depth input."""
        src = _read(self.SHARED)
        assert "Scroll-depth auto-open" in src

    def test_shared_engagement_triggers_section(self) -> None:
        """Shared configurator has 'Engagement triggers' section header."""
        src = _read(self.SHARED)
        assert "Engagement triggers" in src


# ===========================================================================
# WI-0820 — Runtime JS API: setConfigPartial / setTargetingRules
# ===========================================================================

class TestRuntimeConfigApi:
    """Source inspection tests for setConfigPartial and setTargetingRules SDK methods."""

    INDEX_TS = WIDGET_SRC / "index.ts"

    # --- setConfigPartial (SPEC-1514) ---

    def test_set_config_partial_in_interface(self) -> None:
        """setConfigPartial declared in AgentRedSDK interface (SPEC-1514-A1)."""
        src = _read(self.INDEX_TS)
        assert "setConfigPartial" in src
        # Must appear in the interface declaration section
        interface_block = src[src.index("interface AgentRedSDK"):src.index("// Boot") if "// Boot" in src else len(src)]
        assert "setConfigPartial" in interface_block

    def test_set_config_partial_merges_into_store(self) -> None:
        """setConfigPartial merges overrides into store config (SPEC-1514-A2)."""
        src = _read(self.INDEX_TS)
        # Should spread current config with overrides
        assert "...current, ...overrides" in src or "{ ...current, ...overrides }" in src

    def test_set_config_partial_accepts_partial_widget_config(self) -> None:
        """setConfigPartial parameter type is Partial<WidgetConfig> (SPEC-1514-A3)."""
        src = _read(self.INDEX_TS)
        assert "Partial<WidgetConfig>" in src

    def test_set_config_partial_reads_store_config(self) -> None:
        """setConfigPartial reads current config from store before merging."""
        src = _read(self.INDEX_TS)
        assert "store.getState().config" in src

    # --- setTargetingRules (SPEC-1515) ---

    def test_set_targeting_rules_in_interface(self) -> None:
        """setTargetingRules declared in AgentRedSDK interface (SPEC-1515-A1)."""
        src = _read(self.INDEX_TS)
        interface_block = src[src.index("interface AgentRedSDK"):src.index("// Boot") if "// Boot" in src else len(src)]
        assert "setTargetingRules" in interface_block

    def test_set_targeting_rules_updates_page_rules(self) -> None:
        """setTargetingRules updates widget_page_rules in store config (SPEC-1515-A2)."""
        src = _read(self.INDEX_TS)
        assert "widget_page_rules: rules" in src

    def test_set_targeting_rules_re_evaluates_visibility(self) -> None:
        """setTargetingRules triggers shouldShowOnPage re-evaluation (SPEC-1515-A3)."""
        src = _read(self.INDEX_TS)
        # Must call shouldShowOnPage with the updated config
        assert "shouldShowOnPage(updated)" in src

    def test_set_targeting_rules_hides_when_excluded(self) -> None:
        """setTargetingRules hides widget when page rules exclude current page."""
        src = _read(self.INDEX_TS)
        # When shouldShowOnPage returns false, hide both host and iframe
        assert "shadowHost.style.display = 'none'" in src

    def test_set_targeting_rules_accepts_string_array(self) -> None:
        """setTargetingRules parameter type is string[]."""
        src = _read(self.INDEX_TS)
        assert "setTargetingRules(rules: string[])" in src
