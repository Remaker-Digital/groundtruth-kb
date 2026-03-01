"""
Source inspection tests -- Widget core modules.

Verifies TypeScript implementation patterns for widget core specs:
  - Shadow DOM mounting, config fetch, auto-open, notification sound
  - State management, design tokens, transport layer
  - Locale strings, template variables

Run with:
    pytest tests/widget/test_widget_core.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIDGET_SRC = ROOT / "widget" / "src"


# ---------------------------------------------------------------------------
# index.ts -- Shadow DOM, data attributes, config fetch, ready event,
#             auto-open, notification sound, drag-to-reposition
# ---------------------------------------------------------------------------


class TestWidgetShadowDOM:
    """Verify Shadow DOM mounting and initialization. SPEC-1125, 1129, 1131, 1133-1136, WI 253."""

    def test_shadow_dom_mount_attach_shadow(self) -> None:
        """SPEC-1125: Widget must call attachShadow to create Shadow DOM."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "attachShadow" in source, \
            "Widget must mount launcher via attachShadow"

    def test_shadow_dom_closed_mode(self) -> None:
        """SPEC-1125: Shadow DOM must use 'closed' mode for merchant CSS isolation."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "mode: 'closed'" in source, \
            "Shadow DOM must be created with mode: 'closed'"

    def test_shadow_dom_host_element(self) -> None:
        """SPEC-1125: Widget creates a host element with id 'agent-red-widget'."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "agent-red-widget" in source, \
            "Shadow DOM host must have id 'agent-red-widget'"

    def test_data_attribute_overrides_count(self) -> None:
        """SPEC-1129: Support at least 10 data-attribute overrides for Shopify."""
        source = (WIDGET_SRC / "index.ts").read_text()
        # Count 'data-' entries in the attrMap object
        data_attrs = re.findall(r"'data-[a-z-]+'", source)
        # The attrMap has data-color, data-position, data-auto-open, data-auto-open-delay,
        # data-mobile-enabled, data-sound-enabled, data-greeting, data-header-text,
        # data-agent-name, data-context, data-customer-name = 11 in attrMap.
        # Plus Shopify identity: data-shopify-customer-id, data-shopify-customer-hmac,
        # data-shopify-customer-email, data-shopify-customer-name = 4 more.
        # Also data-widget-key, data-api-url, data-page-type, data-page-handle,
        # data-product-title, data-collection-title from other files.
        # The attrMap alone has 11 entries (>= 10).
        attr_map_entries = re.findall(
            r"'data-[a-z-]+'\s*:\s*'widget_", source
        )
        assert len(attr_map_entries) >= 10, (
            f"Expected >= 10 data-attribute overrides in attrMap, found {len(attr_map_entries)}"
        )

    def test_data_attribute_specific_keys(self) -> None:
        """SPEC-1129: Specific data attributes must be present (color, position, auto-open, etc.)."""
        source = (WIDGET_SRC / "index.ts").read_text()
        required_attrs = [
            "data-color",
            "data-position",
            "data-auto-open",
            "data-auto-open-delay",
            "data-mobile-enabled",
            "data-sound-enabled",
            "data-greeting",
            "data-header-text",
            "data-agent-name",
            "data-context",
        ]
        for attr in required_attrs:
            assert attr in source, f"Missing data attribute: {attr}"

    def test_config_fetch_api_endpoint(self) -> None:
        """SPEC-1131: Fetch widget config from /api/config endpoint."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "fetchWidgetConfig" in source, \
            "Widget must call fetchWidgetConfig during initialization"

    def test_config_fetch_page_params(self) -> None:
        """SPEC-1131: Config fetch includes page_type and page_handle params."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        assert "page_type" in source, "fetchWidgetConfig must send page_type param"
        assert "page_handle" in source, "fetchWidgetConfig must send page_handle param"
        assert "/api/config" in source, "fetchWidgetConfig must target /api/config endpoint"

    def test_ready_event_dispatch(self) -> None:
        """SPEC-1133: Dispatch agentred:ready CustomEvent on window after initialization."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "agentred:ready" in source, \
            "Widget must dispatch 'agentred:ready' event"
        assert "CustomEvent" in source, \
            "Ready event must be a CustomEvent"
        assert "dispatchEvent" in source, \
            "Widget must call window.dispatchEvent"

    def test_auto_open_with_delay(self) -> None:
        """SPEC-1134: Support auto-open behavior with configurable delay from widget_auto_open_delay."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "widget_auto_open" in source, \
            "Widget must check widget_auto_open config"
        assert "widget_auto_open_delay" in source, \
            "Widget must read widget_auto_open_delay config"
        assert "setTimeout" in source, \
            "Auto-open must use setTimeout for delay"

    def test_auto_open_default_delay_3s(self) -> None:
        """SPEC-1134: Default auto-open delay is 3 seconds (multiplied by 1000)."""
        source = (WIDGET_SRC / "index.ts").read_text()
        # The code: (config.widget_auto_open_delay ?? 3) * 1000
        assert "widget_auto_open_delay ?? 3" in source, \
            "Auto-open delay must default to 3 seconds"
        assert "* 1000" in source, \
            "Delay must be converted from seconds to milliseconds"

    def test_notification_sound_audio_context(self) -> None:
        """SPEC-1135: Play notification sound via AudioContext."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "AudioContext" in source, \
            "Notification sound must use AudioContext"

    def test_notification_sound_800hz(self) -> None:
        """SPEC-1135: Notification frequency is 800Hz."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "frequency.value = 800" in source, \
            "Oscillator frequency must be set to 800Hz"

    def test_notification_sound_gain_01(self) -> None:
        """SPEC-1135: Notification gain is 0.1."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "gain.value = 0.1" in source, \
            "Gain must be set to 0.1"

    def test_notification_sound_duration_015s(self) -> None:
        """SPEC-1135: Notification duration is 0.15 seconds."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "currentTime + 0.15" in source, \
            "Oscillator must stop at currentTime + 0.15"

    def test_drag_reposition_session_storage(self) -> None:
        """SPEC-1136 / WI 253: Drag-to-reposition persists position in sessionStorage."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "sessionStorage" in source, \
            "Drag position must persist via sessionStorage"
        assert "ar_panel_position" in source, \
            "Storage key must be 'ar_panel_position'"

    def test_drag_reposition_save_and_load(self) -> None:
        """SPEC-1136 / WI 253: saveDragPosition and loadDragPosition functions exist."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "saveDragPosition" in source, \
            "Must have saveDragPosition function"
        assert "loadDragPosition" in source, \
            "Must have loadDragPosition function"

    def test_drag_reposition_clamp_to_viewport(self) -> None:
        """SPEC-1136 / WI 253: Dragged position must be clamped to viewport bounds."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "clampToViewport" in source, \
            "Must clamp drag position to viewport"

    def test_drag_message_handler(self) -> None:
        """SPEC-1136 / WI 253: Listen for ar:drag-start messages from panel iframe."""
        source = (WIDGET_SRC / "index.ts").read_text()
        assert "ar:drag-start" in source, \
            "Must handle 'ar:drag-start' message for drag initiation"


# ---------------------------------------------------------------------------
# state/store.ts -- Message types, conversation reset
# ---------------------------------------------------------------------------


class TestWidgetStore:
    """Verify state management patterns. SPEC-1137, SPEC-1140."""

    def test_message_roles_customer_agent_system(self) -> None:
        """SPEC-1137: Define message types with roles customer, agent, system."""
        source = (WIDGET_SRC / "state" / "store.ts").read_text()
        assert "'customer'" in source, "Message role 'customer' must be defined"
        assert "'agent'" in source, "Message role 'agent' must be defined"
        assert "'system'" in source, "Message role 'system' must be defined"

    def test_message_streaming_flag(self) -> None:
        """SPEC-1137: Messages must support a streaming flag."""
        source = (WIDGET_SRC / "state" / "store.ts").read_text()
        assert "streaming?" in source or "streaming?:" in source, \
            "Message interface must include optional streaming flag"

    def test_message_retracted_flag(self) -> None:
        """SPEC-1137: Messages must support a retracted flag."""
        source = (WIDGET_SRC / "state" / "store.ts").read_text()
        assert "retracted?" in source or "retracted?:" in source, \
            "Message interface must include optional retracted flag"

    def test_reset_preserves_shopify_customer(self) -> None:
        """SPEC-1140: resetConversation must preserve shopifyCustomer identity."""
        source = (WIDGET_SRC / "state" / "store.ts").read_text()
        # The code has a comment: "shopifyCustomer is NOT reset"
        # and the resetConversation method does not set shopifyCustomer to null
        assert "resetConversation" in source, \
            "Store must have resetConversation method"
        # Verify the comment about preservation exists
        assert "shopifyCustomer is NOT reset" in source, \
            "resetConversation must explicitly note shopifyCustomer preservation"

    def test_reset_clears_conversation_fields(self) -> None:
        """SPEC-1140: resetConversation clears conversationId, messages, typing, error."""
        source = (WIDGET_SRC / "state" / "store.ts").read_text()
        # Find the resetConversation method body
        reset_match = re.search(
            r"resetConversation\(\).*?\{(.*?)\n\s{2}\}", source, re.DOTALL
        )
        assert reset_match, "resetConversation method must exist"
        body = reset_match.group(1)
        assert "conversationId: null" in body, "Must reset conversationId to null"
        assert "messages: []" in body, "Must reset messages to empty array"
        assert "isAgentTyping: false" in body, "Must reset isAgentTyping to false"


# ---------------------------------------------------------------------------
# theme/tokens.ts -- Design tokens, color modes, shadows, launcher shapes, z-index
# ---------------------------------------------------------------------------


class TestDesignTokens:
    """Verify design token system. SPEC-1141, 1142, 1144, 1147, 1148, 1151, 1152."""

    def test_design_tokens_interface_exists(self) -> None:
        """SPEC-1141: Define DesignTokens interface."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "interface DesignTokens" in source, \
            "Must define DesignTokens interface"

    def test_design_tokens_colors(self) -> None:
        """SPEC-1141: DesignTokens must include color tokens."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        color_tokens = [
            "colorPrimary:", "colorBackground:", "colorSurface:",
            "colorBorder:", "colorText:", "colorError:",
        ]
        for token in color_tokens:
            assert token in source, f"DesignTokens missing color token: {token}"

    def test_design_tokens_typography(self) -> None:
        """SPEC-1141: DesignTokens must include typography tokens."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        typography_tokens = [
            "fontFamily:", "fontSizeMd:", "fontWeightNormal:", "lineHeightNormal:",
        ]
        for token in typography_tokens:
            assert token in source, f"DesignTokens missing typography token: {token}"

    def test_design_tokens_spacing(self) -> None:
        """SPEC-1141: DesignTokens must include spacing tokens."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        spacing_tokens = ["space1:", "space2:", "space4:", "space8:"]
        for token in spacing_tokens:
            assert token in source, f"DesignTokens missing spacing token: {token}"

    def test_design_tokens_borders(self) -> None:
        """SPEC-1141: DesignTokens must include border tokens."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        border_tokens = ["borderRadius:", "borderRadiusSm:", "borderRadiusLg:", "borderWidth:"]
        for token in border_tokens:
            assert token in source, f"DesignTokens missing border token: {token}"

    def test_design_tokens_shadows(self) -> None:
        """SPEC-1141: DesignTokens must include shadow tokens."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        shadow_tokens = ["shadowSm:", "shadowMd:", "shadowLg:"]
        for token in shadow_tokens:
            assert token in source, f"DesignTokens missing shadow token: {token}"

    def test_design_tokens_sizes(self) -> None:
        """SPEC-1141: DesignTokens must include sizing tokens."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        size_tokens = ["launcherSize:", "panelWidth:", "panelHeight:", "avatarSize:"]
        for token in size_tokens:
            assert token in source, f"DesignTokens missing sizing token: {token}"

    def test_resolve_tokens_function(self) -> None:
        """SPEC-1142: resolveTokens function converts WidgetConfig to DesignTokens."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "export function resolveTokens" in source, \
            "Must export resolveTokens function"
        assert "config: WidgetConfig" in source, \
            "resolveTokens must accept WidgetConfig parameter"
        assert "DesignTokens" in source, \
            "resolveTokens must return DesignTokens"

    def test_4px_base_grid(self) -> None:
        """SPEC-1144: 4px base grid spacing system."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        # Verify the base grid values
        assert "space1: '4px'" in source, "space1 must be 4px"
        assert "space2: '8px'" in source, "space2 must be 8px"
        assert "space3: '12px'" in source, "space3 must be 12px"
        assert "space4: '16px'" in source, "space4 must be 16px"

    def test_color_modes_light_dark_auto(self) -> None:
        """SPEC-1147: Support three color modes -- light, dark, auto (prefers-color-scheme)."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "'light'" in source, "Must support 'light' color mode"
        assert "'dark'" in source, "Must support 'dark' color mode"
        assert "'auto'" in source, "Must support 'auto' color mode"
        assert "prefers-color-scheme" in source, \
            "Auto mode must use prefers-color-scheme media query"

    def test_color_mode_widget_config_field(self) -> None:
        """SPEC-1147: WidgetConfig must declare widget_color_mode field."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "widget_color_mode" in source, \
            "WidgetConfig must include widget_color_mode field"

    def test_shadow_levels_four(self) -> None:
        """SPEC-1148: Support four shadow levels -- none, subtle, standard, heavy."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        shadow_levels = ["'none'", "'subtle'", "'standard'", "'heavy'"]
        for level in shadow_levels:
            assert level in source, f"Missing shadow level: {level}"

    def test_shadow_dark_mode_variants(self) -> None:
        """SPEC-1148: Shadow levels must have dark mode variants."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "isDark" in source, "Shadow resolution must check isDark flag"
        # The resolveShadowLg function takes isDark parameter
        assert "resolveShadowLg" in source, \
            "Must have resolveShadowLg function for shadow resolution"

    def test_launcher_shapes_three(self) -> None:
        """SPEC-1151: Support three launcher shapes -- circle, rounded-square (16px), pill (28px)."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "'circle'" in source, "Must support circle launcher shape"
        assert "'rounded-square'" in source, "Must support rounded-square launcher shape"
        assert "'pill'" in source, "Must support pill launcher shape"

    def test_launcher_shape_border_radii(self) -> None:
        """SPEC-1151: Rounded-square uses 16px, pill uses 28px."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        # launcherBorderRadius: launcherShape === 'rounded-square' ? '16px'
        #   : launcherShape === 'pill' ? '28px'
        #   : '9999px', // circle
        assert "'16px'" in source, "Rounded-square must use 16px border radius"
        assert "'28px'" in source, "Pill must use 28px border radius"

    def test_z_index_launcher(self) -> None:
        """SPEC-1152: z-index for launcher starts at 2147483640."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "2147483640" in source, \
            "Launcher z-index must be 2147483640"

    def test_z_index_panel(self) -> None:
        """SPEC-1152: z-index for panel is 2147483641."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "2147483641" in source, \
            "Panel z-index must be 2147483641"

    def test_z_index_order(self) -> None:
        """SPEC-1152: Panel z-index must be higher than launcher z-index."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        launcher_match = re.search(r"zIndexLauncher:\s*(\d+)", source)
        panel_match = re.search(r"zIndexPanel:\s*(\d+)", source)
        assert launcher_match and panel_match, \
            "Must define zIndexLauncher and zIndexPanel"
        assert int(panel_match.group(1)) > int(launcher_match.group(1)), \
            "zIndexPanel must be greater than zIndexLauncher"


# ---------------------------------------------------------------------------
# transport/http.ts -- Authentication, config fetch, 409 handling, visitor
# ---------------------------------------------------------------------------


class TestHTTPTransport:
    """Verify HTTP transport patterns. SPEC-1163, 1164, 1166, 1167."""

    def test_x_widget_key_header(self) -> None:
        """SPEC-1163: Authenticate HTTP requests with X-Widget-Key header."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        assert "'X-Widget-Key'" in source, \
            "HTTP requests must include X-Widget-Key header"

    def test_widget_key_from_config(self) -> None:
        """SPEC-1163: X-Widget-Key header value comes from transport config widgetKey."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        assert "widgetKey" in source, \
            "Widget key must be read from transport config"
        # SPEC-1566: Widget key is conditionally set (adminApiKey takes precedence).
        # The request function uses headers['X-Widget-Key'] = widgetKey when no admin key.
        assert "headers['X-Widget-Key'] = widgetKey" in source, \
            "X-Widget-Key header must use widgetKey from config"

    def test_fetch_widget_config_function(self) -> None:
        """SPEC-1164: fetchWidgetConfig function exists and is exported."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        assert "export async function fetchWidgetConfig" in source, \
            "fetchWidgetConfig must be an exported async function"

    def test_fetch_widget_config_page_params(self) -> None:
        """SPEC-1164: fetchWidgetConfig sends page_type and page_handle query params."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        assert "page_type=" in source, \
            "fetchWidgetConfig must include page_type query param"
        assert "page_handle=" in source, \
            "fetchWidgetConfig must include page_handle query param"

    def test_409_status_handling(self) -> None:
        """SPEC-1166: Handle 409 HTTP status for escalated conversations."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        # The SendMessageResult interface documents 409
        assert "409" in source, \
            "HTTP transport must reference 409 status code"

    def test_send_message_result_status(self) -> None:
        """SPEC-1166: SendMessageResult includes status field for 409 detection."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        assert "interface SendMessageResult" in source, \
            "Must define SendMessageResult interface"
        assert "status: number" in source, \
            "SendMessageResult must include status field"

    def test_visitor_object_construction(self) -> None:
        """SPEC-1167: Construct visitor object with Shopify, email, and OTP identity signals."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        assert "visitor" in source, "Must construct visitor object"
        assert "shopify_customer_id" in source, \
            "Visitor must handle Shopify customer ID"
        assert "shopify_customer_hmac" in source, \
            "Visitor must handle Shopify customer HMAC"

    def test_visitor_email_name_fields(self) -> None:
        """SPEC-1167: Visitor object includes email and name from pre-chat fields."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        assert "visitor.email" in source, "Visitor must include email field"
        assert "visitor.name" in source, "Visitor must include name field"

    def test_visitor_otp_customer_token(self) -> None:
        """SPEC-1167: Visitor supports OTP customer token for verified identity."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        assert "customer_token" in source, \
            "Must support customer_token for OTP verification"
        assert "customerToken" in source, \
            "Must accept customerToken parameter"


# ---------------------------------------------------------------------------
# transport/sse.ts -- Tab ID, reconnect limits
# ---------------------------------------------------------------------------


class TestSSETransport:
    """Verify SSE transport patterns. SPEC-1158, SPEC-1160."""

    def test_tab_id_query_param(self) -> None:
        """SPEC-1158: Include tab_id query param for multi-tab coordination."""
        source = (WIDGET_SRC / "transport" / "sse.ts").read_text()
        assert "tab_id" in source, \
            "SSE connection must include tab_id query parameter"

    def test_tab_id_session_storage(self) -> None:
        """SPEC-1158: Tab ID persisted in sessionStorage for reconnection consistency."""
        source = (WIDGET_SRC / "transport" / "sse.ts").read_text()
        assert "sessionStorage" in source, \
            "Tab ID must be persisted in sessionStorage"
        assert "__agentred_tab_id" in source, \
            "Tab ID storage key must be '__agentred_tab_id'"

    def test_max_reconnect_10_attempts(self) -> None:
        """SPEC-1160: Limit SSE reconnect to max 10 attempts."""
        source = (WIDGET_SRC / "transport" / "sse.ts").read_text()
        assert "maxReconnectAttempts = 10" in source, \
            "SSE must limit reconnect to 10 attempts"

    def test_reconnect_base_delay_1s(self) -> None:
        """SPEC-1160: SSE reconnect uses 1 second base delay."""
        source = (WIDGET_SRC / "transport" / "sse.ts").read_text()
        assert "reconnectBaseDelay = 1000" in source, \
            "SSE reconnect base delay must be 1000ms (1s)"

    def test_reconnect_max_30s(self) -> None:
        """SPEC-1160: SSE reconnect caps at 30 seconds max delay."""
        source = (WIDGET_SRC / "transport" / "sse.ts").read_text()
        assert "30000" in source, "SSE reconnect must cap at 30000ms (30s)"

    def test_exponential_backoff(self) -> None:
        """SPEC-1160: SSE reconnect uses exponential backoff."""
        source = (WIDGET_SRC / "transport" / "sse.ts").read_text()
        assert "Math.pow(2," in source, \
            "SSE reconnect must use exponential backoff (Math.pow(2, ...))"


# ---------------------------------------------------------------------------
# transport/ws.ts -- WebSocket endpoint, ping, typing, reconnect, events
# ---------------------------------------------------------------------------


class TestWSTransport:
    """Verify WebSocket transport patterns. SPEC-1169, 1170, 1171, 1172, 1173."""

    def test_ws_endpoint_path(self) -> None:
        """SPEC-1169: Connect WebSocket to /api/chat/ws/{conversation_id}."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "/api/chat/ws/" in source, \
            "WebSocket must connect to /api/chat/ws/ path"

    def test_ws_protocol_conversion(self) -> None:
        """SPEC-1169: Convert http(s) to ws(s) for WebSocket URL."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "wss:" in source, "Must convert https: to wss:"
        assert "ws:" in source, "Must convert http: to ws:"

    def test_ping_30_second_interval(self) -> None:
        """SPEC-1170: Send 30-second ping keepalive messages."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "30000" in source, "Ping interval must be 30000ms (30s)"
        assert "'ping'" in source, "Must send ping message type"

    def test_ping_uses_set_interval(self) -> None:
        """SPEC-1170: Ping keepalive uses setInterval."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "setInterval" in source, "Ping must use setInterval"

    def test_typing_indicator_5s_debounce(self) -> None:
        """SPEC-1171: Typing indicator with 5-second auto-stop debounce."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "5000" in source, "Typing auto-stop must use 5000ms (5s) timeout"

    def test_typing_indicator_customer_typing_event(self) -> None:
        """SPEC-1171: Send customer_typing event type."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "'customer_typing'" in source, \
            "Must send 'customer_typing' event type"

    def test_ws_max_reconnect_10_attempts(self) -> None:
        """SPEC-1172: Limit WebSocket reconnect to max 10 attempts."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "maxReconnectAttempts = 10" in source, \
            "WebSocket must limit reconnect to 10 attempts"

    def test_ws_reconnect_base_2s(self) -> None:
        """SPEC-1172: WebSocket reconnect uses 2 second base delay."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "reconnectBaseDelay = 2000" in source, \
            "WebSocket reconnect base delay must be 2000ms (2s)"

    def test_ws_reconnect_max_30s(self) -> None:
        """SPEC-1172: WebSocket reconnect caps at 30 seconds max."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "30000" in source, "WebSocket reconnect must cap at 30000ms (30s)"

    def test_ws_event_agent_typing(self) -> None:
        """SPEC-1173: Handle agent_typing WebSocket event."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "'agent_typing'" in source, \
            "Must handle 'agent_typing' event"

    def test_ws_event_agent_stopped_typing(self) -> None:
        """SPEC-1173: Handle agent_stopped_typing WebSocket event."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "'agent_stopped_typing'" in source, \
            "Must handle 'agent_stopped_typing' event"

    def test_ws_event_agent_message(self) -> None:
        """SPEC-1173: Handle agent_message WebSocket event."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "'agent_message'" in source, \
            "Must handle 'agent_message' event"

    def test_ws_event_conversation_ended(self) -> None:
        """SPEC-1173: Handle conversation_ended WebSocket event."""
        source = (WIDGET_SRC / "transport" / "ws.ts").read_text()
        assert "'conversation_ended'" in source, \
            "Must handle 'conversation_ended' event"


# ---------------------------------------------------------------------------
# utils/templateVars.ts -- Page type detection, template variables
# ---------------------------------------------------------------------------


class TestTemplateVars:
    """Verify template variable patterns. SPEC-1174, 1175, 1176."""

    def test_detect_8_page_types(self) -> None:
        """SPEC-1174: Detect 8 page types from Shopify data attributes or URL patterns."""
        source = (WIDGET_SRC / "utils" / "templateVars.ts").read_text()
        page_types = ["home", "product", "collection", "cart", "search", "blog", "page", "other"]
        for pt in page_types:
            assert f"'{pt}'" in source, f"Must detect page type: {pt}"

    def test_page_type_url_detection(self) -> None:
        """SPEC-1174: detectPageTypeFromUrl function uses URL pathname patterns."""
        source = (WIDGET_SRC / "utils" / "templateVars.ts").read_text()
        assert "detectPageTypeFromUrl" in source, \
            "Must have detectPageTypeFromUrl function"
        url_patterns = ["/products/", "/collections/", "/cart", "/search", "/blogs/", "/pages/"]
        for pattern in url_patterns:
            assert pattern in source, f"Must detect URL pattern: {pattern}"

    def test_page_type_data_attribute_fallback(self) -> None:
        """SPEC-1174: Fall back to URL detection when Shopify data attributes absent."""
        source = (WIDGET_SRC / "utils" / "templateVars.ts").read_text()
        assert "data-page-type" in source, \
            "Must check data-page-type attribute"
        assert "detectPageTypeFromUrl" in source, \
            "Must fall back to URL-based detection"

    def test_6_template_variables(self) -> None:
        """SPEC-1175: Substitute 6 template variables in quick action prompts."""
        source = (WIDGET_SRC / "utils" / "templateVars.ts").read_text()
        template_vars = [
            "page_type", "page_handle", "page_title",
            "page_url", "product_title", "collection_title",
        ]
        for var in template_vars:
            assert var in source, f"Must support template variable: {var}"

    def test_resolve_template_function(self) -> None:
        """SPEC-1175: resolveTemplate function replaces {{variable}} placeholders."""
        source = (WIDGET_SRC / "utils" / "templateVars.ts").read_text()
        assert "resolveTemplate" in source, \
            "Must have resolveTemplate function"
        # Check the regex for {{variable}} pattern
        assert "{{" in source or r"\{\{" in source, \
            "Must use {{variable}} placeholder syntax"

    def test_unresolved_variables_left_as_is(self) -> None:
        """SPEC-1176: Leave unresolved template variables as-is."""
        source = (WIDGET_SRC / "utils" / "templateVars.ts").read_text()
        # The code returns `match` (the original {{var}}) when value is undefined/null
        assert "return value !== undefined && value !== null" in source \
            or ": match" in source, \
            "Unresolved variables must be left as-is (return original match)"

    def test_unresolved_comment_documentation(self) -> None:
        """SPEC-1176: Source documents that unresolved variables are left as-is."""
        source = (WIDGET_SRC / "utils" / "templateVars.ts").read_text()
        assert "unresolved" in source.lower() or "left as-is" in source.lower(), \
            "Source must document that unresolved variables are preserved"


# ---------------------------------------------------------------------------
# locale/en.ts -- English locale strings
# ---------------------------------------------------------------------------


class TestLocaleStrings:
    """Verify English locale coverage. SPEC-1155."""

    def test_locale_interface_defined(self) -> None:
        """SPEC-1155: Locale interface must be defined and exported."""
        source = (WIDGET_SRC / "locale" / "en.ts").read_text()
        assert "export interface Locale" in source, \
            "Must export Locale interface"

    def test_en_locale_exported(self) -> None:
        """SPEC-1155: English locale object must be exported."""
        source = (WIDGET_SRC / "locale" / "en.ts").read_text()
        assert "export const en: Locale" in source, \
            "Must export 'en' constant of type Locale"

    def test_locale_string_count(self) -> None:
        """SPEC-1155: Provide English locale strings (49 in current implementation)."""
        source = (WIDGET_SRC / "locale" / "en.ts").read_text()
        # Count fields in the Locale interface (lines with "field: string;")
        interface_fields = re.findall(r"^\s+\w+:\s*string;", source, re.MULTILINE)
        # Current implementation has 49 locale strings covering: header, input,
        # connection, rating, prechat, offline, conversation, fields, files,
        # issue reporting, OTP, and consent categories.
        assert len(interface_fields) >= 49, (
            f"Locale interface must have >= 49 string fields, found {len(interface_fields)}"
        )

    def test_locale_key_categories(self) -> None:
        """SPEC-1155: Locale must cover header, input, offline, rating, prechat, OTP, consent."""
        source = (WIDGET_SRC / "locale" / "en.ts").read_text()
        required_keys = [
            "headerTitle",
            "inputPlaceholder",
            "sendButton",
            "offlineMessage",
            "typingIndicator",
            "connectionLost",
            "ratingPrompt",
            "preChatTitle",
            "reportIssue",
            "otpPrompt",
            "consentPrompt",
        ]
        for key in required_keys:
            assert key in source, f"Locale must include key: {key}"

    def test_locale_en_object_values_populated(self) -> None:
        """SPEC-1155: All locale values in the en object must be non-empty strings."""
        source = (WIDGET_SRC / "locale" / "en.ts").read_text()
        # Extract the en object block
        en_match = re.search(r"export const en: Locale = \{(.*?)\};", source, re.DOTALL)
        assert en_match, "Must have en locale object"
        en_body = en_match.group(1)
        # Check there are no empty string values
        empty_values = re.findall(r":\s*''", en_body)
        assert len(empty_values) == 0, \
            f"All locale values must be non-empty, found {len(empty_values)} empty strings"


# ---------------------------------------------------------------------------
# Widget color pipeline (WI-0792 regression guard)
# ---------------------------------------------------------------------------


class TestWidgetColorPipeline:
    """End-to-end widget color pipeline verification — WI-0792 regression guard.

    The S103 gradient toggle bug demonstrated that a field can exist in
    fields.yaml and the admin UI can save it, but if it's missing from
    any pipeline layer the widget never sees it.  This class verifies
    the entire color pipeline: config interface → resolveTokens →
    Header background → Panel gradient wiring → API fetch.

    © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
    """

    # -- WidgetConfig interface (tokens.ts) ----------------------------------

    def test_widget_config_has_primary_color_field(self) -> None:
        """WidgetConfig must declare widget_primary_color optional field."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "widget_primary_color" in source, \
            "WidgetConfig must include widget_primary_color field"

    def test_widget_config_has_gradient_enabled_field(self) -> None:
        """WidgetConfig must declare widget_header_gradient_enabled field."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "widget_header_gradient_enabled" in source, \
            "WidgetConfig must include widget_header_gradient_enabled"

    def test_widget_config_has_gradient_end_field(self) -> None:
        """WidgetConfig must declare widget_header_gradient_end field."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "widget_header_gradient_end" in source, \
            "WidgetConfig must include widget_header_gradient_end"

    def test_widget_config_has_bubble_color_fields(self) -> None:
        """WidgetConfig must declare agent and customer bubble color fields."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        bubble_fields = [
            "widget_agent_bubble_color",
            "widget_agent_bubble_text_color",
            "widget_customer_bubble_color",
            "widget_customer_bubble_text_color",
        ]
        for field in bubble_fields:
            assert field in source, f"WidgetConfig must include {field}"

    # -- resolveTokens() color mapping (tokens.ts) ---------------------------

    def test_resolve_tokens_reads_primary_color(self) -> None:
        """resolveTokens() must read config.widget_primary_color for colorPrimary."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "config.widget_primary_color" in source, \
            "resolveTokens must read config.widget_primary_color"

    def test_resolve_tokens_default_primary_color(self) -> None:
        """resolveTokens() must fall back to #ff3621 (Agent Red brand) as default."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "'#ff3621'" in source, \
            "Default primary color must be #ff3621"
        # Verify it's used as a fallback with ||
        assert re.search(
            r"config\.widget_primary_color\s*\|\|\s*DEFAULTS\.primaryColor",
            source,
        ), "Must use config.widget_primary_color || DEFAULTS.primaryColor pattern"

    def test_resolve_tokens_maps_to_color_primary(self) -> None:
        """resolveTokens() must set colorPrimary from the resolved primary color."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        # Both light and dark mode paths must include colorPrimary: primary
        color_primary_assignments = re.findall(r"colorPrimary:\s*primary", source)
        assert len(color_primary_assignments) >= 2, (
            f"Must assign colorPrimary: primary in both light and dark mode paths, "
            f"found {len(color_primary_assignments)}"
        )

    def test_resolve_tokens_contrast_text_for_primary(self) -> None:
        """resolveTokens() must compute contrast text color for primary background."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "contrastText(primary)" in source or "contrastText" in source, \
            "Must compute contrast text color for primary"
        assert "colorPrimaryText" in source, \
            "Must set colorPrimaryText from contrast computation"

    def test_resolve_tokens_primary_hover(self) -> None:
        """resolveTokens() must derive a hover color from primary."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "colorPrimaryHover" in source, \
            "Must derive colorPrimaryHover from primary"
        # Should use darken() function
        assert "darken(primary" in source, \
            "Must use darken() to derive hover color"

    def test_resolve_tokens_bubble_colors_from_config(self) -> None:
        """resolveTokens() must read bubble colors from config with defaults."""
        source = (WIDGET_SRC / "theme" / "tokens.ts").read_text()
        assert "config.widget_agent_bubble_color" in source, \
            "Must read config.widget_agent_bubble_color"
        assert "config.widget_customer_bubble_color" in source, \
            "Must read config.widget_customer_bubble_color"

    # -- Header.tsx consumes tokens ------------------------------------------

    def test_header_uses_color_primary(self) -> None:
        """Header.tsx must use tokens.colorPrimary for its background."""
        source = (WIDGET_SRC / "components" / "Header.tsx").read_text()
        assert "tokens.colorPrimary" in source, \
            "Header must use tokens.colorPrimary"

    def test_header_supports_gradient(self) -> None:
        """Header.tsx must support gradient background via gradientEnd prop."""
        source = (WIDGET_SRC / "components" / "Header.tsx").read_text()
        assert "gradientEnd" in source, \
            "Header must accept gradientEnd prop"
        assert "linear-gradient" in source, \
            "Header must apply linear-gradient when gradientEnd is set"

    def test_header_gradient_uses_primary_as_start(self) -> None:
        """Header gradient must use colorPrimary as the start color."""
        source = (WIDGET_SRC / "components" / "Header.tsx").read_text()
        assert re.search(
            r"tokens\.colorPrimary.*gradientEnd|gradientEnd.*tokens\.colorPrimary",
            source,
            re.DOTALL,
        ), "Gradient must use tokens.colorPrimary as one endpoint"

    # -- Panel.tsx wires gradient from config --------------------------------

    def test_panel_passes_gradient_end_to_header(self) -> None:
        """Panel.tsx must pass gradientEnd prop to Header from config."""
        source = (WIDGET_SRC / "components" / "Panel.tsx").read_text()
        assert "gradientEnd" in source, \
            "Panel must pass gradientEnd to Header"
        assert "widget_header_gradient_end" in source, \
            "Panel must read widget_header_gradient_end from config"

    def test_panel_conditionalizes_gradient_on_enabled_flag(self) -> None:
        """Panel.tsx must only pass gradient when widget_header_gradient_enabled is not false."""
        source = (WIDGET_SRC / "components" / "Panel.tsx").read_text()
        assert "widget_header_gradient_enabled" in source, \
            "Panel must check widget_header_gradient_enabled before passing gradient"

    # -- HTTP transport fetches config with correct structure -----------------

    def test_fetch_config_returns_widget_config_type(self) -> None:
        """fetchWidgetConfig returns WidgetConfig type from /api/config."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        assert "Promise<WidgetConfig | null>" in source, \
            "fetchWidgetConfig must return Promise<WidgetConfig | null>"
        assert "'/api/config'" in source, \
            "fetchWidgetConfig must request /api/config endpoint"

    def test_fetch_config_extracts_config_from_response(self) -> None:
        """fetchWidgetConfig extracts resp.data.config from the API response."""
        source = (WIDGET_SRC / "transport" / "http.ts").read_text()
        assert "resp.data.config" in source, \
            "Must extract config from resp.data.config"

    # -- Python-side field pipeline ------------------------------------------

    def test_python_field_registry_has_primary_color(self) -> None:
        """widget_primary_color must exist in the Python field registry."""
        from src.multi_tenant.config.field_mapping import get_field_registry
        registry = get_field_registry()
        assert "widget_primary_color" in registry, \
            "widget_primary_color missing from field registry"

    def test_python_field_registry_has_gradient_fields(self) -> None:
        """gradient fields must exist in the Python field registry."""
        from src.multi_tenant.config.field_mapping import get_field_registry
        registry = get_field_registry()
        assert "widget_header_gradient_enabled" in registry, \
            "widget_header_gradient_enabled missing from field registry"
        assert "widget_header_gradient_end" in registry, \
            "widget_header_gradient_end missing from field registry"

    def test_python_preferences_to_config_extracts_color(self) -> None:
        """_preferences_to_config extracts widget_primary_color from a Cosmos doc."""
        from src.multi_tenant.config.field_mapping import _preferences_to_config
        mock_doc = {"widget_primary_color": "#0000FF", "irrelevant_field": "ignored"}
        result = _preferences_to_config(mock_doc)
        assert result.get("widget_primary_color") == "#0000FF", \
            "Must extract widget_primary_color from preferences document"

    def test_python_preferences_to_config_extracts_gradient(self) -> None:
        """_preferences_to_config extracts gradient fields from a Cosmos doc."""
        from src.multi_tenant.config.field_mapping import _preferences_to_config
        mock_doc = {
            "widget_header_gradient_enabled": True,
            "widget_header_gradient_end": "#FF9900",
        }
        result = _preferences_to_config(mock_doc)
        assert result.get("widget_header_gradient_enabled") is True, \
            "Must extract widget_header_gradient_enabled"
        assert result.get("widget_header_gradient_end") == "#FF9900", \
            "Must extract widget_header_gradient_end"

    def test_python_preferences_to_config_skips_none_values(self) -> None:
        """_preferences_to_config must skip None values (not override defaults)."""
        from src.multi_tenant.config.field_mapping import _preferences_to_config
        mock_doc = {"widget_primary_color": None}
        result = _preferences_to_config(mock_doc)
        assert "widget_primary_color" not in result, \
            "Must skip None values — they should fall back to tier defaults"


# ---------------------------------------------------------------------------
# WI-0813 / SPEC-1504: shouldShowOnPage +/- prefix parsing
# WI-0814 / SPEC-1505: Match against pathname + search
# ---------------------------------------------------------------------------


class TestTargetingRulesParsing:
    """Source inspection tests for targeting rule prefix parsing and URL matching."""

    INDEX_TS = WIDGET_SRC / "index.ts"

    def _read_index(self) -> str:
        return self.INDEX_TS.read_text(encoding="utf-8")

    # -- Prefix parsing (SPEC-1504) --

    def test_strips_plus_prefix(self) -> None:
        """shouldShowOnPage strips + prefix before building regex (SPEC-1504-A1)."""
        src = self._read_index()
        assert "trimmed.startsWith('+')" in src or "startsWith('+')" in src

    def test_strips_minus_prefix(self) -> None:
        """shouldShowOnPage strips - prefix before building regex (SPEC-1504-A2)."""
        src = self._read_index()
        assert "trimmed.startsWith('-')" in src or "startsWith('-')" in src

    def test_exclude_wins_over_include(self) -> None:
        """Exclude rules take precedence over include rules (SPEC-1504-A3)."""
        src = self._read_index()
        # Exclude check happens before include check
        exclude_pos = src.find("for (const re of excludes)")
        include_pos = src.find("for (const re of includes)")
        assert exclude_pos > 0, "Expected excludes loop in shouldShowOnPage"
        assert include_pos > 0, "Expected includes loop in shouldShowOnPage"
        assert exclude_pos < include_pos, "Excludes must be checked before includes"

    def test_only_exclude_shows_everywhere_except_matches(self) -> None:
        """Only-exclude rules show widget everywhere except matches (SPEC-1504-A4)."""
        src = self._read_index()
        # When includes array is empty, return true (show everywhere unless excluded)
        assert "if (includes.length === 0) return true" in src

    def test_only_include_shows_only_on_matches(self) -> None:
        """Only-include rules show widget only on matching pages (SPEC-1504-A5)."""
        src = self._read_index()
        # After includes loop, return false (no match = don't show)
        lines = src.split('\n')
        found_return_false = False
        in_function = False
        for line in lines:
            if 'function shouldShowOnPage' in line:
                in_function = True
            if in_function and 'return false' in line:
                found_return_false = True
        assert found_return_false, "shouldShowOnPage must return false at end (no include match)"

    def test_escapes_regex_metacharacters(self) -> None:
        """Regex metacharacters are escaped in glob patterns (SPEC-1504-A6)."""
        src = self._read_index()
        # The pattern should escape regex specials like . ^ $ { } ( ) | [ ]
        assert r"[.^${}()|[\]\\]" in src or "replace(/[" in src

    # -- URL matching (SPEC-1505) --

    def test_matches_pathname_plus_search(self) -> None:
        """Match target includes window.location.search (SPEC-1505-A1)."""
        src = self._read_index()
        assert "window.location.search" in src

    def test_match_target_includes_query_string(self) -> None:
        """matchTarget is built from pathname + search (SPEC-1505-A2)."""
        src = self._read_index()
        assert "pathname + window.location.search" in src or \
               "location.pathname + window.location.search" in src

    # -- Structural correctness --

    def test_include_exclude_arrays(self) -> None:
        """shouldShowOnPage uses separate include/exclude arrays."""
        src = self._read_index()
        assert "const includes:" in src or "includes: RegExp[]" in src
        assert "const excludes:" in src or "excludes: RegExp[]" in src

    def test_glob_star_to_regex(self) -> None:
        """Glob * is converted to regex .* for matching."""
        src = self._read_index()
        # After escaping, convert * to .*
        assert ".replace(/\\*/g, '.*')" in src

    def test_glob_question_to_regex(self) -> None:
        """Glob ? is converted to regex . for matching."""
        src = self._read_index()
        assert ".replace(/\\?/g, '.')" in src


# ===========================================================================
# WI-0816 — Engagement triggers (exit-intent + scroll-depth)
# ===========================================================================

class TestEngagementTriggers:
    """Source inspection tests for SPEC-1507 (exit-intent) and SPEC-1508 (scroll-depth)."""

    INDEX_TS = Path(__file__).resolve().parents[2] / "widget" / "src" / "index.ts"
    TOKENS_TS = Path(__file__).resolve().parents[2] / "widget" / "src" / "theme" / "tokens.ts"

    def _read_index(self) -> str:
        return self.INDEX_TS.read_text(encoding="utf-8")

    # --- Exit-intent (SPEC-1507) ---

    def test_exit_intent_mouseleave_listener(self) -> None:
        """Exit-intent registers mouseleave on documentElement (SPEC-1507-A1)."""
        src = self._read_index()
        assert "document.documentElement.addEventListener('mouseleave'" in src

    def test_exit_intent_listener_removed_after_trigger(self) -> None:
        """Exit-intent listener is removed after triggering (SPEC-1507-A2)."""
        src = self._read_index()
        assert "document.documentElement.removeEventListener('mouseleave'" in src

    def test_exit_intent_config_field_in_interface(self) -> None:
        """widget_exit_intent_enabled field exists in WidgetConfig (SPEC-1507-A3)."""
        src = self.TOKENS_TS.read_text(encoding="utf-8")
        assert "widget_exit_intent_enabled" in src

    def test_exit_intent_desktop_only(self) -> None:
        """Exit-intent is desktop-only — guarded by isMobile() check."""
        src = self._read_index()
        assert "widget_exit_intent_enabled && !isMobile()" in src

    def test_exit_intent_respects_manual_close(self) -> None:
        """Exit-intent does not fire if widget was manually closed."""
        src = self._read_index()
        # The exit intent handler checks userManuallyClosedWidget
        assert "!userManuallyClosedWidget" in src

    # --- Scroll-depth (SPEC-1508) ---

    def test_scroll_depth_scroll_listener(self) -> None:
        """Scroll-depth registers scroll listener on window (SPEC-1508-A1)."""
        src = self._read_index()
        assert "window.addEventListener('scroll', scrollHandler" in src

    def test_scroll_depth_listener_removed_after_trigger(self) -> None:
        """Scroll-depth listener removed after triggering (SPEC-1508-A2)."""
        src = self._read_index()
        assert "window.removeEventListener('scroll', scrollHandler)" in src

    def test_scroll_depth_config_field_in_interface(self) -> None:
        """widget_scroll_depth_trigger field exists in WidgetConfig (SPEC-1508-A3)."""
        src = self.TOKENS_TS.read_text(encoding="utf-8")
        assert "widget_scroll_depth_trigger" in src

    def test_scroll_depth_percentage_calculation(self) -> None:
        """Scroll depth calculates scrollPercent from scrollTop / docHeight."""
        src = self._read_index()
        assert "scrollPercent" in src
        assert "scrollHeight" in src

    def test_scroll_depth_passive_listener(self) -> None:
        """Scroll listener uses passive: true to avoid jank."""
        src = self._read_index()
        assert "{ passive: true }" in src

    def test_scroll_depth_respects_manual_close(self) -> None:
        """Scroll-depth does not fire if widget was manually closed."""
        src = self._read_index()
        # The scroll handler checks the same userManuallyClosedWidget flag
        # Count occurrences — should appear in both exit-intent and scroll handlers
        count = src.count("!userManuallyClosedWidget")
        assert count >= 2, f"Expected at least 2 occurrences, found {count}"

    def test_manual_close_flag_in_close_widget(self) -> None:
        """closeWidget sets userManuallyClosedWidget = true."""
        src = self._read_index()
        assert "userManuallyClosedWidget = true" in src
