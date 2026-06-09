"""
Insert Batch 6 (WIDGET_UI) test coverage mappings into the Knowledge DB.

87 specs covered by 253 source-inspection tests across 3 test files:
  - tests/widget/test_widget_core.py (81 tests, 30 specs)
  - tests/widget/test_widget_components.py (101 tests, 33 specs)
  - tests/widget/test_widget_forms_admin.py (71 tests, 24 specs)

Idempotent: skips existing (spec_id, test_file, test_function) combinations.

Session: S112
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "groundtruth.db"

CREATED_BY = "batch6_widget_ui_s112"

# (spec_handle, test_file, test_class, test_function, confidence, match_reason)
MAPPINGS: list[tuple[str, str, str, str, str, str]] = [
    # =========================================================================
    # test_widget_core.py — 30 specs
    # =========================================================================
    # SPEC-1125: Shadow DOM mounting
    (
        "SPEC-1125",
        "tests/widget/test_widget_core.py",
        "TestWidgetShadowDOM",
        "test_shadow_dom_mount_attach_shadow",
        "high",
        "Verifies attachShadow, closed mode, host element ID",
    ),
    # SPEC-1129: Data-attribute overrides
    (
        "SPEC-1129",
        "tests/widget/test_widget_core.py",
        "TestWidgetShadowDOM",
        "test_data_attribute_overrides_count",
        "high",
        "Counts >= 10 data-attribute entries in attrMap",
    ),
    # SPEC-1131: Config fetch from /api/config
    (
        "SPEC-1131",
        "tests/widget/test_widget_core.py",
        "TestWidgetShadowDOM",
        "test_config_fetch_api_endpoint",
        "high",
        "Verifies fetchWidgetConfig call and /api/config endpoint",
    ),
    # SPEC-1133: agentred:ready CustomEvent
    (
        "SPEC-1133",
        "tests/widget/test_widget_core.py",
        "TestWidgetShadowDOM",
        "test_ready_event_dispatch",
        "high",
        "Verifies agentred:ready event, CustomEvent, dispatchEvent",
    ),
    # SPEC-1134: Auto-open with configurable delay
    (
        "SPEC-1134",
        "tests/widget/test_widget_core.py",
        "TestWidgetShadowDOM",
        "test_auto_open_with_delay",
        "high",
        "Verifies widget_auto_open, widget_auto_open_delay, setTimeout, 3s default",
    ),
    # SPEC-1135: Notification sound (800Hz, 0.1 gain, 0.15s)
    (
        "SPEC-1135",
        "tests/widget/test_widget_core.py",
        "TestWidgetShadowDOM",
        "test_notification_sound_audio_context",
        "high",
        "Verifies AudioContext, 800Hz freq, 0.1 gain, 0.15s duration",
    ),
    # SPEC-1136: Drag-to-reposition with sessionStorage
    (
        "SPEC-1136",
        "tests/widget/test_widget_core.py",
        "TestWidgetShadowDOM",
        "test_drag_reposition_session_storage",
        "high",
        "Verifies sessionStorage, ar_panel_position, save/load, clampToViewport, ar:drag-start",
    ),
    # WI 253: Drag-to-reposition (same implementation as SPEC-1136)
    (
        "253",
        "tests/widget/test_widget_core.py",
        "TestWidgetShadowDOM",
        "test_drag_reposition_session_storage",
        "high",
        "WI 253 drag-to-reposition tested via SPEC-1136 implementation",
    ),
    # SPEC-1137: Message types (customer, agent, system + streaming/retracted)
    (
        "SPEC-1137",
        "tests/widget/test_widget_core.py",
        "TestWidgetStore",
        "test_message_roles_customer_agent_system",
        "high",
        "Verifies customer/agent/system roles, streaming?, retracted? flags",
    ),
    # SPEC-1140: Conversation reset preserves Shopify identity
    (
        "SPEC-1140",
        "tests/widget/test_widget_core.py",
        "TestWidgetStore",
        "test_reset_preserves_shopify_customer",
        "high",
        "Verifies resetConversation preserves shopifyCustomer, clears conv fields",
    ),
    # SPEC-1141: Design token system
    (
        "SPEC-1141",
        "tests/widget/test_widget_core.py",
        "TestDesignTokens",
        "test_design_tokens_interface_exists",
        "high",
        "Verifies DesignTokens interface with colors, typography, spacing, borders, shadows, sizes",
    ),
    # SPEC-1142: resolveTokens function
    (
        "SPEC-1142",
        "tests/widget/test_widget_core.py",
        "TestDesignTokens",
        "test_resolve_tokens_function",
        "high",
        "Verifies resolveTokens(config: WidgetConfig) -> DesignTokens",
    ),
    # SPEC-1144: 4px base grid spacing
    (
        "SPEC-1144",
        "tests/widget/test_widget_core.py",
        "TestDesignTokens",
        "test_4px_base_grid",
        "high",
        "Verifies space1=4px, space2=8px, space3=12px, space4=16px",
    ),
    # SPEC-1147: Color modes (light, dark, auto)
    (
        "SPEC-1147",
        "tests/widget/test_widget_core.py",
        "TestDesignTokens",
        "test_color_modes_light_dark_auto",
        "high",
        "Verifies light/dark/auto modes, prefers-color-scheme, widget_color_mode",
    ),
    # SPEC-1148: Shadow levels (none, subtle, standard, heavy)
    (
        "SPEC-1148",
        "tests/widget/test_widget_core.py",
        "TestDesignTokens",
        "test_shadow_levels_four",
        "high",
        "Verifies 4 shadow levels with dark mode variants",
    ),
    # SPEC-1151: Launcher shapes (circle, rounded-square 16px, pill 28px)
    (
        "SPEC-1151",
        "tests/widget/test_widget_core.py",
        "TestDesignTokens",
        "test_launcher_shapes_three",
        "high",
        "Verifies 3 shapes with correct border radii",
    ),
    # SPEC-1152: z-index values (launcher 2147483640, panel 2147483641)
    (
        "SPEC-1152",
        "tests/widget/test_widget_core.py",
        "TestDesignTokens",
        "test_z_index_launcher",
        "high",
        "Verifies z-index values and panel > launcher ordering",
    ),
    # SPEC-1163: X-Widget-Key authentication header
    (
        "SPEC-1163",
        "tests/widget/test_widget_core.py",
        "TestHTTPTransport",
        "test_x_widget_key_header",
        "high",
        "Verifies X-Widget-Key header from widgetKey config",
    ),
    # SPEC-1164: fetchWidgetConfig function
    (
        "SPEC-1164",
        "tests/widget/test_widget_core.py",
        "TestHTTPTransport",
        "test_fetch_widget_config_function",
        "high",
        "Verifies exported async fetchWidgetConfig with page_type/page_handle params",
    ),
    # SPEC-1166: 409 HTTP status handling for escalated conversations
    (
        "SPEC-1166",
        "tests/widget/test_widget_core.py",
        "TestHTTPTransport",
        "test_409_status_handling",
        "high",
        "Verifies 409 reference and SendMessageResult interface with status field",
    ),
    # SPEC-1167: Visitor object with identity signals
    (
        "SPEC-1167",
        "tests/widget/test_widget_core.py",
        "TestHTTPTransport",
        "test_visitor_object_construction",
        "high",
        "Verifies Shopify, email, name, OTP customer_token in visitor object",
    ),
    # SPEC-1158: Tab ID for SSE multi-tab coordination
    (
        "SPEC-1158",
        "tests/widget/test_widget_core.py",
        "TestSSETransport",
        "test_tab_id_query_param",
        "high",
        "Verifies tab_id param, sessionStorage persistence, __agentred_tab_id key",
    ),
    # SPEC-1160: SSE reconnect limits (10 attempts, 1s base, 30s max, exp backoff)
    (
        "SPEC-1160",
        "tests/widget/test_widget_core.py",
        "TestSSETransport",
        "test_max_reconnect_10_attempts",
        "high",
        "Verifies maxReconnectAttempts=10, 1000ms base, 30000ms max, Math.pow(2,...)",
    ),
    # SPEC-1169: WebSocket endpoint /api/chat/ws/{conversation_id}
    (
        "SPEC-1169",
        "tests/widget/test_widget_core.py",
        "TestWSTransport",
        "test_ws_endpoint_path",
        "high",
        "Verifies /api/chat/ws/ path and http->ws protocol conversion",
    ),
    # SPEC-1170: 30-second ping keepalive
    (
        "SPEC-1170",
        "tests/widget/test_widget_core.py",
        "TestWSTransport",
        "test_ping_30_second_interval",
        "high",
        "Verifies 30000ms interval, ping message type, setInterval",
    ),
    # SPEC-1171: Typing indicator with 5s debounce
    (
        "SPEC-1171",
        "tests/widget/test_widget_core.py",
        "TestWSTransport",
        "test_typing_indicator_5s_debounce",
        "high",
        "Verifies 5000ms auto-stop, customer_typing event type",
    ),
    # SPEC-1172: WebSocket reconnect limits
    (
        "SPEC-1172",
        "tests/widget/test_widget_core.py",
        "TestWSTransport",
        "test_ws_max_reconnect_10_attempts",
        "high",
        "Verifies maxReconnectAttempts=10, 2000ms base, 30000ms max",
    ),
    # SPEC-1173: WebSocket event types
    (
        "SPEC-1173",
        "tests/widget/test_widget_core.py",
        "TestWSTransport",
        "test_ws_event_agent_typing",
        "high",
        "Verifies agent_typing, agent_stopped_typing, agent_message, conversation_ended",
    ),
    # SPEC-1174: 8 page type detection
    (
        "SPEC-1174",
        "tests/widget/test_widget_core.py",
        "TestTemplateVars",
        "test_detect_8_page_types",
        "high",
        "Verifies 8 page types, URL patterns, data-page-type fallback",
    ),
    # SPEC-1175: 6 template variables
    (
        "SPEC-1175",
        "tests/widget/test_widget_core.py",
        "TestTemplateVars",
        "test_6_template_variables",
        "high",
        "Verifies 6 vars, resolveTemplate function, {{variable}} syntax",
    ),
    # SPEC-1176: Unresolved template variables left as-is
    (
        "SPEC-1176",
        "tests/widget/test_widget_core.py",
        "TestTemplateVars",
        "test_unresolved_variables_left_as_is",
        "high",
        "Verifies unresolved {{var}} preserved, documented in source",
    ),
    # SPEC-1155: English locale strings (49 keys)
    (
        "SPEC-1155",
        "tests/widget/test_widget_core.py",
        "TestLocaleStrings",
        "test_locale_interface_defined",
        "high",
        "Verifies Locale interface, en export, 49+ strings, key categories, non-empty values",
    ),
    # =========================================================================
    # test_widget_components.py — 33 specs
    # =========================================================================
    # SPEC-1177: Launcher fixed positioning
    (
        "SPEC-1177",
        "tests/widget/test_widget_components.py",
        "TestLauncher",
        "test_spec_1177_fixed_positioning",
        "high",
        "Verifies fixed position, bottom-left/right, offsetX/Y, button element",
    ),
    # SPEC-1178: Launcher icon options (chat, headset, help)
    (
        "SPEC-1178",
        "tests/widget/test_widget_components.py",
        "TestLauncher",
        "test_spec_1178_chat_icon",
        "high",
        "Verifies 3 icon SVG components, launcherIcon prop type, selection logic",
    ),
    # SPEC-1180: Unread badge capped at 9+
    (
        "SPEC-1180",
        "tests/widget/test_widget_components.py",
        "TestLauncher",
        "test_spec_1180_unread_badge_cap_at_9_plus",
        "high",
        "Verifies 9+ cap, badge hidden when open",
    ),
    # SPEC-1181: Launcher hover/scale animations
    (
        "SPEC-1181",
        "tests/widget/test_widget_components.py",
        "TestLauncher",
        "test_spec_1181_hover_color_change",
        "high",
        "Verifies colorPrimaryHover on mouseEnter, scale(0.9)/scale(1) transform",
    ),
    # SPEC-1182: Panel composition (Header, MessageList, InputBar, forms)
    (
        "SPEC-1182",
        "tests/widget/test_widget_components.py",
        "TestPanel",
        "test_spec_1182_composes_header",
        "high",
        "Verifies Header, MessageList, InputBar, PreChatForm, ChatRating, OfflineForm",
    ),
    # SPEC-1183: CSS animations (blink, typing-dot, spin, fade-in, slide-up, shimmer)
    (
        "SPEC-1183",
        "tests/widget/test_widget_components.py",
        "TestPanel",
        "test_spec_1183_animation_blink",
        "high",
        "Verifies 6 @keyframes animations defined in Panel",
    ),
    # SPEC-1184: Connection banner (reconnecting, error)
    (
        "SPEC-1184",
        "tests/widget/test_widget_components.py",
        "TestPanel",
        "test_spec_1184_connection_banner_reconnecting",
        "high",
        "Verifies ConnectionBanner component with reconnecting/error types",
    ),
    # SPEC-1186: Shopify auto-start conversation
    (
        "SPEC-1186",
        "tests/widget/test_widget_components.py",
        "TestPanel",
        "test_spec_1186_shopify_auto_start",
        "high",
        "Verifies shopifyCustomer check and identity passthrough (id, hmac)",
    ),
    # SPEC-1187: OTP skip for optional mode
    (
        "SPEC-1187",
        "tests/widget/test_widget_components.py",
        "TestPanel",
        "test_spec_1187_otp_skip_optional_only",
        "high",
        "Verifies optional-only gating and handleOtpSkip callback",
    ),
    # SPEC-1189: Panel drag-to-reposition
    (
        "SPEC-1189",
        "tests/widget/test_widget_components.py",
        "TestPanel",
        "test_spec_1189_drag_to_reposition",
        "high",
        "Verifies handleDragStart, ar:drag-start message, Header onDragStart prop",
    ),
    # WI 255: InputBar min height (~3 text lines)
    (
        "255",
        "tests/widget/test_widget_components.py",
        "TestPanel",
        "test_wi_255_input_bar_min_height",
        "high",
        "Verifies MIN_TEXTAREA_HEIGHT = 66 in InputBar.tsx",
    ),
    # WI 256: MessageList scroll controls
    (
        "256",
        "tests/widget/test_widget_components.py",
        "TestPanel",
        "test_wi_256_message_list_scroll",
        "high",
        "Verifies overflowY: auto in MessageList.tsx",
    ),
    # SPEC-1192: Auto-scroll to bottom on new messages
    (
        "SPEC-1192",
        "tests/widget/test_widget_components.py",
        "TestMessageList",
        "test_spec_1192_auto_scroll_to_bottom",
        "high",
        "Verifies scrollHeight usage, isAtBottom gating",
    ),
    # SPEC-1193: Scroll-to-latest button (40px threshold, smooth)
    (
        "SPEC-1193",
        "tests/widget/test_widget_components.py",
        "TestMessageList",
        "test_spec_1193_scroll_to_latest_button",
        "high",
        "Verifies showScrollBtn state, 40px threshold, smooth scroll",
    ),
    # SPEC-1194: Day separators (Today, Yesterday, formatted)
    (
        "SPEC-1194",
        "tests/widget/test_widget_components.py",
        "TestMessageList",
        "test_spec_1194_day_separator_today",
        "high",
        "Verifies locale.today/yesterday, toLocaleDateString, getDayLabel helper",
    ),
    # SPEC-1195: Consecutive agent message avatar grouping
    (
        "SPEC-1195",
        "tests/widget/test_widget_components.py",
        "TestMessageList",
        "test_spec_1195_consecutive_agent_avatar_grouping",
        "high",
        "Verifies shouldShowAvatar, previous role comparison",
    ),
    # SPEC-1196: Typing indicator
    (
        "SPEC-1196",
        "tests/widget/test_widget_components.py",
        "TestMessageList",
        "test_spec_1196_typing_indicator",
        "high",
        "Verifies TypingIndicator component, isAgentTyping gating",
    ),
    # SPEC-1197: Greeting message area with quick actions
    (
        "SPEC-1197",
        "tests/widget/test_widget_components.py",
        "TestMessageList",
        "test_spec_1197_greeting_message_area",
        "high",
        "Verifies greetingMessage prop, messages.length===0 gate, QuickActions",
    ),
    # SPEC-1198: Customer/agent bubble alignment and colors
    (
        "SPEC-1198",
        "tests/widget/test_widget_components.py",
        "TestMessageBubble",
        "test_spec_1198_customer_bubble_right_aligned",
        "high",
        "Verifies row-reverse/row direction, colorCustomerBubble/colorAgentBubble",
    ),
    # SPEC-1199: Markdown link parsing
    (
        "SPEC-1199",
        "tests/widget/test_widget_components.py",
        "TestMessageBubble",
        "test_spec_1199_markdown_link_regex",
        "high",
        "Verifies MARKDOWN_LINK_RE, renderWithLinks, target=_top",
    ),
    # SPEC-1200: Streaming cursor animation
    (
        "SPEC-1200",
        "tests/widget/test_widget_components.py",
        "TestMessageBubble",
        "test_spec_1200_streaming_cursor_animation",
        "high",
        "Verifies message.streaming check, ar-blink animation",
    ),
    # SPEC-1201: Retracted message styling
    (
        "SPEC-1201",
        "tests/widget/test_widget_components.py",
        "TestMessageBubble",
        "test_spec_1201_retracted_opacity",
        "high",
        "Verifies opacity 0.7, colorError border, 'Message revised' label",
    ),
    # SPEC-1202: Source citation domains
    (
        "SPEC-1202",
        "tests/widget/test_widget_components.py",
        "TestMessageBubble",
        "test_spec_1202_source_citation_domains",
        "high",
        "Verifies extractSourceDomains, www. stripping, SourceIcon",
    ),
    # SPEC-1203: Message bubble max width 75%
    (
        "SPEC-1203",
        "tests/widget/test_widget_components.py",
        "TestMessageBubble",
        "test_spec_1203_max_width_75_percent",
        "high",
        "Verifies maxWidth: 75%",
    ),
    # SPEC-1204: 12-hour timestamp format
    (
        "SPEC-1204",
        "tests/widget/test_widget_components.py",
        "TestMessageBubble",
        "test_spec_1204_timestamp_12_hour_format",
        "high",
        "Verifies AM/PM, formatTime function, hours % 12",
    ),
    # SPEC-1206: Enter to send, Shift+Enter for newline
    (
        "SPEC-1206",
        "tests/widget/test_widget_components.py",
        "TestInputBar",
        "test_spec_1206_enter_to_send",
        "high",
        "Verifies Enter key send, shiftKey newline, preventDefault",
    ),
    # SPEC-1207: 2000 char max with 90% warning
    (
        "SPEC-1207",
        "tests/widget/test_widget_components.py",
        "TestInputBar",
        "test_spec_1207_max_length_2000",
        "high",
        "Verifies MAX_MESSAGE_LENGTH=2000, 90% threshold, char count display",
    ),
    # SPEC-1209: File upload button (conditional, PaperclipIcon)
    (
        "SPEC-1209",
        "tests/widget/test_widget_components.py",
        "TestInputBar",
        "test_spec_1209_file_upload_button",
        "high",
        "Verifies fileUploadEnabled prop, PaperclipIcon, conditional render",
    ),
    # SPEC-1210: Powered by Agent Red branding
    (
        "SPEC-1210",
        "tests/widget/test_widget_components.py",
        "TestInputBar",
        "test_spec_1210_powered_by_branding",
        "high",
        "Verifies showBranding prop, agentredcx.com link, locale.poweredBy",
    ),
    # SPEC-1154: QuickActionButton interface (id, label, prompt_template, icon?)
    (
        "SPEC-1154",
        "tests/widget/test_widget_components.py",
        "TestQuickActions",
        "test_spec_1154_interface_id",
        "high",
        "Verifies QuickActionButton interface fields in tokens.ts",
    ),
    # SPEC-1211: Max 2 visible quick action buttons
    (
        "SPEC-1211",
        "tests/widget/test_widget_components.py",
        "TestQuickActions",
        "test_spec_1211_max_2_visible",
        "high",
        "Verifies slice(0,2), pill shape, hover effects",
    ),
    # SPEC-1212: Quick action max width 280px, ellipsis
    (
        "SPEC-1212",
        "tests/widget/test_widget_components.py",
        "TestQuickActions",
        "test_spec_1212_max_width_280px",
        "high",
        "Verifies maxWidth 280px, textOverflow ellipsis",
    ),
    # SPEC-1213: Quick action fade-in 0.3s animation
    (
        "SPEC-1213",
        "tests/widget/test_widget_components.py",
        "TestQuickActions",
        "test_spec_1213_fade_in_animation",
        "high",
        "Verifies ar-fade-in animation with 0.3s duration",
    ),
    # =========================================================================
    # test_widget_forms_admin.py — 24 specs
    # =========================================================================
    # SPEC-1214: Chat rating thumbs up/down
    (
        "SPEC-1214",
        "tests/widget/test_widget_forms_admin.py",
        "TestChatRating",
        "test_thumbs_up_down_buttons",
        "high",
        "Verifies ThumbUp/Down icons, 56px circles, comment textarea, positive/negative",
    ),
    # SPEC-1215: Chat rating success state
    (
        "SPEC-1215",
        "tests/widget/test_widget_forms_admin.py",
        "TestChatRating",
        "test_success_state_with_checkmark",
        "high",
        "Verifies CheckIcon, submitted state, thank-you, new conversation button",
    ),
    # SPEC-1216: 4 issue report types
    (
        "SPEC-1216",
        "tests/widget/test_widget_forms_admin.py",
        "TestIssueReport",
        "test_four_issue_types_defined",
        "high",
        "Verifies 4 issue types, radio-circle indicators, ISSUE_TYPES constant",
    ),
    # SPEC-1217: Issue report textarea constraints
    (
        "SPEC-1217",
        "tests/widget/test_widget_forms_admin.py",
        "TestIssueReport",
        "test_textarea_max_length_2000",
        "high",
        "Verifies maxLength=2000, 80px min, 160px max, vertical resize",
    ),
    # SPEC-1218: Offline form fields (name, email, message)
    (
        "SPEC-1218",
        "tests/widget/test_widget_forms_admin.py",
        "TestOfflineForm",
        "test_name_email_message_fields",
        "high",
        "Verifies 3 required fields, EMAIL_REGEX, handleSubmit",
    ),
    # SPEC-1219: Custom offline message from config
    (
        "SPEC-1219",
        "tests/widget/test_widget_forms_admin.py",
        "TestOfflineForm",
        "test_offline_message_from_config",
        "high",
        "Verifies offlineMessage prop, conditional rendering",
    ),
    # SPEC-1220: Dynamic pre-chat form from config
    (
        "SPEC-1220",
        "tests/widget/test_widget_forms_admin.py",
        "TestPreChatForm",
        "test_dynamic_form_from_config",
        "high",
        "Verifies formConfig.fields, text/email/textarea types, validation",
    ),
    # SPEC-1222: Continue as guest skip link
    (
        "SPEC-1222",
        "tests/widget/test_widget_forms_admin.py",
        "TestPreChatForm",
        "test_continue_as_guest_skip_link",
        "high",
        "Verifies onSkip callback, locale.preChatSkip, conditional render",
    ),
    # SPEC-1223: 6-digit OTP input boxes
    (
        "SPEC-1223",
        "tests/widget/test_widget_forms_admin.py",
        "TestOtpVerification",
        "test_six_digit_input_boxes",
        "high",
        "Verifies 6 digit slots, maxLength=1, numeric inputMode, auto-advance",
    ),
    # SPEC-1224: OTP backspace navigation + paste
    (
        "SPEC-1224",
        "tests/widget/test_widget_forms_admin.py",
        "TestOtpVerification",
        "test_backspace_navigation",
        "high",
        "Verifies Backspace nav, handlePaste, clipboardData, slice(0,6), strip non-digits",
    ),
    # SPEC-1225: 60-second OTP resend cooldown
    (
        "SPEC-1225",
        "tests/widget/test_widget_forms_admin.py",
        "TestOtpVerification",
        "test_60_second_resend_cooldown",
        "high",
        "Verifies 60s cooldown, decrement timer, disabled during cooldown",
    ),
    # SPEC-1226: PCM consent banner (Allow + No thanks)
    (
        "SPEC-1226",
        "tests/widget/test_widget_forms_admin.py",
        "TestConsentBanner",
        "test_allow_and_decline_buttons",
        "high",
        "Verifies onAccept/onDecline, locale text, fade-in animation",
    ),
    # SPEC-1227: Consent banner styling
    (
        "SPEC-1227",
        "tests/widget/test_widget_forms_admin.py",
        "TestConsentBanner",
        "test_surface_background",
        "high",
        "Verifies colorSurface background, borderBottom separator",
    ),
    # SPEC-1327: Widget configurator two-column layout
    (
        "SPEC-1327",
        "tests/widget/test_widget_forms_admin.py",
        "TestWidgetConfiguratorLayout",
        "test_two_column_layout",
        "high",
        "Verifies formPanel/previewPanel, flex:1, width:340, maxWidth:1200",
    ),
    # SPEC-1328: Live preview with browser chrome
    (
        "SPEC-1328",
        "tests/widget/test_widget_forms_admin.py",
        "TestWidgetConfiguratorLayout",
        "test_live_preview_with_simulated_browser_chrome",
        "high",
        "Verifies previewFrame, 'Live preview' title, light/dark backgrounds",
    ),
    # SPEC-1332: Custom HSV color picker
    (
        "SPEC-1332",
        "tests/widget/test_widget_forms_admin.py",
        "TestWidgetConfiguratorColorPicker",
        "test_color_picker_field_component",
        "high",
        "Verifies ColorPickerField, hex validation, swatch, HSV, SV area, hue bar, presets",
    ),
    # SPEC-1333: Multiple color picker instances for gradient
    (
        "SPEC-1333",
        "tests/widget/test_widget_forms_admin.py",
        "TestWidgetConfiguratorColorPicker",
        "test_multiple_color_picker_instances",
        "high",
        "Verifies >= 2 ColorPickerField, primary and background color pickers",
    ),
    # SPEC-1338: Avatar URL field and preview
    (
        "SPEC-1338",
        "tests/widget/test_widget_forms_admin.py",
        "TestWidgetConfiguratorAvatar",
        "test_avatar_url_field",
        "high",
        "Verifies widget_agent_avatar_url field, label, objectFit:cover preview",
    ),
    # SPEC-1339: 25 widget_* field mapping
    (
        "SPEC-1339",
        "tests/widget/test_widget_forms_admin.py",
        "TestWidgetConfiguratorFieldMapping",
        "test_widget_config_interface_field_count",
        "high",
        "Verifies >= 25 widget_* fields in WidgetConfig, DEFAULT_CONFIG, extractWidgetConfig",
    ),
    # SPEC-1340: Save/discard actions
    (
        "SPEC-1340",
        "tests/widget/test_widget_forms_admin.py",
        "TestWidgetConfiguratorActions",
        "test_save_draft_button",
        "high",
        "Verifies Save draft, handleSave, handleDiscard, unsaved changes indicator",
    ),
    # SPEC-1341: Sticky preview panel
    (
        "SPEC-1341",
        "tests/widget/test_widget_forms_admin.py",
        "TestWidgetConfiguratorPreview",
        "test_sticky_positioning_on_preview",
        "high",
        "Verifies position:sticky, top:16, alignSelf:flex-start",
    ),
    # SPEC-1343: Decorative-only preview launcher
    (
        "SPEC-1343",
        "tests/widget/test_widget_forms_admin.py",
        "TestWidgetConfiguratorPreview",
        "test_launcher_decorative_only",
        "high",
        "Verifies cursor:default, no onClick on preview launcher",
    ),
]


def main() -> None:
    if not DB_PATH.exists():
        print(f"ERROR: DB not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    now = datetime.now(tz=timezone.utc).isoformat()

    inserted = 0
    skipped = 0

    for spec_id, test_file, test_class, test_func, confidence, reason in MAPPINGS:
        # Verify spec exists by ID (spec_id IS the specifications.id column)
        cursor.execute(
            "SELECT id FROM specifications WHERE id = ? LIMIT 1",
            (spec_id,),
        )
        row = cursor.fetchone()
        if not row:
            print(f"  WARN: spec id '{spec_id}' not found in KB — skipping")
            skipped += 1
            continue

        # Idempotency check
        cursor.execute(
            """SELECT 1 FROM test_coverage
               WHERE spec_id = ? AND test_file = ? AND test_function = ?""",
            (spec_id, test_file, test_func),
        )
        if cursor.fetchone():
            skipped += 1
            continue

        cursor.execute(
            """INSERT INTO test_coverage
               (spec_id, test_file, test_class, test_function, confidence,
                match_reason, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (spec_id, test_file, test_class, test_func, confidence, reason, now, CREATED_BY),
        )
        inserted += 1

    conn.commit()

    # Report coverage
    cursor.execute("SELECT COUNT(DISTINCT spec_id) FROM test_coverage")
    covered = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM specifications WHERE status != 'retired'")
    total = cursor.fetchone()[0]
    pct = (covered / total * 100) if total else 0

    conn.close()

    print(f"\nBatch 6 (WIDGET_UI) coverage insertion complete.")
    print(f"  Inserted: {inserted}")
    print(f"  Skipped:  {skipped}")
    print(f"  Coverage: {covered}/{total} specs ({pct:.1f}%)")


if __name__ == "__main__":
    main()
