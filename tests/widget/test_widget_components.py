"""
Source inspection tests -- Widget components.

Verifies TypeScript implementation patterns for widget component specs:
  - Launcher, Panel, MessageList, MessageBubble, InputBar, QuickActions

Run with:
    pytest tests/widget/test_widget_components.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = ROOT / "widget" / "src" / "components"
THEME = ROOT / "widget" / "src" / "theme"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(filename: str) -> str:
    """Read a component source file from widget/src/components/."""
    return (COMPONENTS / filename).read_text(encoding="utf-8")


def _read_theme(filename: str) -> str:
    """Read a theme file from widget/src/theme/."""
    return (THEME / filename).read_text(encoding="utf-8")


# ===================================================================
# Launcher.tsx
# ===================================================================


class TestLauncher:
    """Widget launcher component. SPEC-1177, SPEC-1178, SPEC-1180, SPEC-1181."""

    SRC = _read("Launcher.tsx")

    def test_spec_1177_fixed_positioning(self) -> None:
        """SPEC-1177: Launcher renders with fixed positioning."""
        assert "position: 'fixed'" in self.SRC, (
            "Launcher should use position: 'fixed' for floating action button"
        )

    def test_spec_1177_shadow_dom_mention(self) -> None:
        """SPEC-1177: Launcher is rendered inside a Shadow DOM."""
        assert "Shadow DOM" in self.SRC, (
            "Launcher docstring should reference Shadow DOM isolation"
        )

    def test_spec_1177_configurable_position_bottom_right(self) -> None:
        """SPEC-1177: Launcher supports bottom-right position via prop."""
        assert "'bottom-right'" in self.SRC, (
            "Launcher should accept 'bottom-right' position option"
        )

    def test_spec_1177_configurable_position_bottom_left(self) -> None:
        """SPEC-1177: Launcher supports bottom-left position via prop."""
        assert "'bottom-left'" in self.SRC, (
            "Launcher should accept 'bottom-left' position option"
        )

    def test_spec_1177_offset_x_applied(self) -> None:
        """SPEC-1177: Launcher applies configurable X offset."""
        assert "offsetX" in self.SRC, (
            "Launcher should accept offsetX prop for horizontal positioning"
        )

    def test_spec_1177_offset_y_applied(self) -> None:
        """SPEC-1177: Launcher applies configurable Y offset via bottom style."""
        assert re.search(r"bottom:\s*`\$\{offsetY\}px`", self.SRC), (
            "Launcher should use offsetY for bottom position style"
        )

    def test_spec_1177_button_element(self) -> None:
        """SPEC-1177: Launcher renders as a <button> element."""
        assert '<button' in self.SRC, (
            "Launcher should render as a <button> element"
        )

    def test_spec_1178_chat_icon(self) -> None:
        """SPEC-1178: Launcher supports 'chat' icon option."""
        assert "ChatIcon" in self.SRC, (
            "Launcher should define a ChatIcon SVG component"
        )

    def test_spec_1178_headset_icon(self) -> None:
        """SPEC-1178: Launcher supports 'headset' icon option."""
        assert "HeadsetIcon" in self.SRC, (
            "Launcher should define a HeadsetIcon SVG component"
        )

    def test_spec_1178_help_icon(self) -> None:
        """SPEC-1178: Launcher supports 'help' icon option."""
        assert "HelpIcon" in self.SRC, (
            "Launcher should define a HelpIcon SVG component"
        )

    def test_spec_1178_three_icon_options_in_prop(self) -> None:
        """SPEC-1178: launcherIcon prop type accepts exactly 3 icon options."""
        assert re.search(
            r"launcherIcon:\s*'chat'\s*\|\s*'headset'\s*\|\s*'help'",
            self.SRC,
        ), "launcherIcon prop should accept 'chat' | 'headset' | 'help'"

    def test_spec_1178_icon_selection_logic(self) -> None:
        """SPEC-1178: Launcher selects icon component based on launcherIcon prop."""
        # The source uses a ternary chain to select the icon
        assert "launcherIcon === 'headset'" in self.SRC, (
            "Launcher should check launcherIcon === 'headset' for icon selection"
        )
        assert "launcherIcon === 'help'" in self.SRC, (
            "Launcher should check launcherIcon === 'help' for icon selection"
        )

    def test_spec_1180_unread_badge_cap_at_9_plus(self) -> None:
        """SPEC-1180: Unread badge displays '9+' when count exceeds 9."""
        assert "unreadCount > 9" in self.SRC, (
            "Launcher should check unreadCount > 9 for badge cap"
        )
        assert "'9+'" in self.SRC, (
            "Launcher should display '9+' when unread count exceeds 9"
        )

    def test_spec_1180_badge_hidden_when_open(self) -> None:
        """SPEC-1180: Unread badge is hidden when launcher is open."""
        assert "!isOpen && unreadCount > 0" in self.SRC, (
            "Badge should only render when launcher is closed and unread > 0"
        )

    def test_spec_1181_hover_color_change(self) -> None:
        """SPEC-1181: Launcher applies hover color change via onMouseEnter."""
        assert "onMouseEnter" in self.SRC, (
            "Launcher should handle onMouseEnter for hover color"
        )
        assert "colorPrimaryHover" in self.SRC, (
            "Launcher should use colorPrimaryHover on mouse enter"
        )

    def test_spec_1181_scale_transform_on_open(self) -> None:
        """SPEC-1181: Launcher applies scale transform based on open state."""
        assert "scale(0.9)" in self.SRC, (
            "Launcher should scale to 0.9 when open"
        )
        assert "scale(1)" in self.SRC, (
            "Launcher should scale to 1 when closed"
        )


# ===================================================================
# Panel.tsx
# ===================================================================


class TestPanel:
    """Widget panel component. SPEC-1182..1189, WI 255, WI 256."""

    SRC = _read("Panel.tsx")

    def test_spec_1182_composes_header(self) -> None:
        """SPEC-1182: Panel composes Header component."""
        assert "<Header" in self.SRC, (
            "Panel should render <Header /> component"
        )

    def test_spec_1182_composes_message_list(self) -> None:
        """SPEC-1182: Panel composes MessageList component."""
        assert "<MessageList" in self.SRC, (
            "Panel should render <MessageList /> component"
        )

    def test_spec_1182_composes_input_bar(self) -> None:
        """SPEC-1182: Panel composes InputBar component."""
        assert "<InputBar" in self.SRC, (
            "Panel should render <InputBar /> component"
        )

    def test_spec_1182_conditional_prechat_form(self) -> None:
        """SPEC-1182: Panel includes conditional PreChatForm view."""
        assert "<PreChatForm" in self.SRC, (
            "Panel should include conditional <PreChatForm /> view"
        )

    def test_spec_1182_conditional_chat_rating(self) -> None:
        """SPEC-1182: Panel includes conditional ChatRating view."""
        assert "<ChatRating" in self.SRC, (
            "Panel should include conditional <ChatRating /> view"
        )

    def test_spec_1182_conditional_offline_form(self) -> None:
        """SPEC-1182: Panel includes conditional OfflineForm view."""
        assert "<OfflineForm" in self.SRC, (
            "Panel should include conditional <OfflineForm /> view"
        )

    def test_spec_1183_animation_blink(self) -> None:
        """SPEC-1183: Panel defines ar-blink CSS animation."""
        assert "@keyframes ar-blink" in self.SRC, (
            "Panel should define @keyframes ar-blink animation"
        )

    def test_spec_1183_animation_typing_dot(self) -> None:
        """SPEC-1183: Panel defines ar-typing-dot CSS animation."""
        assert "@keyframes ar-typing-dot" in self.SRC, (
            "Panel should define @keyframes ar-typing-dot animation"
        )

    def test_spec_1183_animation_spin(self) -> None:
        """SPEC-1183: Panel defines ar-spin CSS animation."""
        assert "@keyframes ar-spin" in self.SRC, (
            "Panel should define @keyframes ar-spin animation"
        )

    def test_spec_1183_animation_fade_in(self) -> None:
        """SPEC-1183: Panel defines ar-fade-in CSS animation."""
        assert "@keyframes ar-fade-in" in self.SRC, (
            "Panel should define @keyframes ar-fade-in animation"
        )

    def test_spec_1183_animation_slide_up(self) -> None:
        """SPEC-1183: Panel defines ar-slide-up CSS animation."""
        assert "@keyframes ar-slide-up" in self.SRC, (
            "Panel should define @keyframes ar-slide-up animation"
        )

    def test_spec_1183_animation_shimmer(self) -> None:
        """SPEC-1183: Panel defines ar-shimmer CSS animation."""
        assert "@keyframes ar-shimmer" in self.SRC, (
            "Panel should define @keyframes ar-shimmer animation"
        )

    def test_spec_1184_connection_banner_reconnecting(self) -> None:
        """SPEC-1184: Panel shows ConnectionBanner with reconnecting state."""
        assert "type=\"reconnecting\"" in self.SRC or "type='reconnecting'" in self.SRC, (
            "Panel should render ConnectionBanner with type='reconnecting'"
        )

    def test_spec_1184_connection_banner_error(self) -> None:
        """SPEC-1184: Panel shows ConnectionBanner with error state."""
        assert "type=\"error\"" in self.SRC or "type='error'" in self.SRC, (
            "Panel should render ConnectionBanner with type='error'"
        )

    def test_spec_1184_connection_banner_component_defined(self) -> None:
        """SPEC-1184: ConnectionBanner component is defined in Panel module."""
        assert "const ConnectionBanner" in self.SRC, (
            "Panel module should define the ConnectionBanner component"
        )

    def test_spec_1186_shopify_auto_start(self) -> None:
        """SPEC-1186: Panel auto-starts conversation for Shopify customers."""
        assert "shopifyCustomer" in self.SRC, (
            "Panel should check for shopifyCustomer state"
        )

    def test_spec_1186_shopify_identity_passthrough(self) -> None:
        """SPEC-1186: Shopify auto-start passes customer identity (name, email, id, hmac)."""
        assert "shopify_customer_id" in self.SRC, (
            "Panel should pass shopify_customer_id in beginConversation"
        )
        assert "shopify_customer_hmac" in self.SRC, (
            "Panel should pass shopify_customer_hmac in beginConversation"
        )

    def test_spec_1187_otp_skip_optional_only(self) -> None:
        """SPEC-1187: OTP skip button only available when verification mode is 'optional'."""
        assert re.search(
            r"customer_email_verification.*===\s*'optional'",
            self.SRC,
        ), "Panel should check if customer_email_verification === 'optional' before showing skip"

    def test_spec_1187_otp_skip_handler(self) -> None:
        """SPEC-1187: Panel defines handleOtpSkip callback."""
        assert "handleOtpSkip" in self.SRC, (
            "Panel should define handleOtpSkip callback"
        )

    def test_spec_1189_drag_to_reposition(self) -> None:
        """SPEC-1189: Panel supports drag-to-reposition via mousedown on header."""
        assert "handleDragStart" in self.SRC, (
            "Panel should define handleDragStart for drag-to-reposition"
        )

    def test_spec_1189_drag_start_event(self) -> None:
        """SPEC-1189: Drag start posts message to parent frame."""
        assert "ar:drag-start" in self.SRC, (
            "Panel should post 'ar:drag-start' message to parent frame"
        )

    def test_spec_1189_header_receives_drag_handler(self) -> None:
        """SPEC-1189: Header component receives onDragStart prop."""
        assert "onDragStart={handleDragStart}" in self.SRC, (
            "Panel should pass handleDragStart to Header as onDragStart prop"
        )

    def test_wi_255_input_bar_min_height(self) -> None:
        """WI 255: InputBar textarea has min height for ~3 text lines."""
        # The Panel renders InputBar; the actual height constant is in InputBar.tsx.
        # Verify Panel passes through without overriding.
        input_src = _read("InputBar.tsx")
        assert "MIN_TEXTAREA_HEIGHT = 66" in input_src, (
            "InputBar should define MIN_TEXTAREA_HEIGHT = 66 (~3 text lines)"
        )

    def test_wi_256_message_list_scroll(self) -> None:
        """WI 256: MessageList scroll controls (overflow-y auto, scrollbar styles)."""
        ml_src = _read("MessageList.tsx")
        assert "overflowY: 'auto'" in ml_src, (
            "MessageList should set overflowY: 'auto' for scroll control"
        )


# ===================================================================
# MessageList.tsx
# ===================================================================


class TestMessageList:
    """Message list component. SPEC-1192..1197."""

    SRC = _read("MessageList.tsx")

    def test_spec_1192_auto_scroll_to_bottom(self) -> None:
        """SPEC-1192: Auto-scroll message list to bottom on new messages."""
        assert "scrollRef.current.scrollHeight" in self.SRC, (
            "MessageList should scroll to scrollHeight on new messages"
        )

    def test_spec_1192_scroll_when_at_bottom(self) -> None:
        """SPEC-1192: Auto-scroll only triggers when user is at bottom."""
        assert "isAtBottom" in self.SRC, (
            "MessageList should track isAtBottom state for auto-scroll gating"
        )

    def test_spec_1193_scroll_to_latest_button(self) -> None:
        """SPEC-1193: Show scroll-to-latest button when user scrolls up."""
        assert "showScrollBtn" in self.SRC, (
            "MessageList should track showScrollBtn state"
        )

    def test_spec_1193_threshold_40px(self) -> None:
        """SPEC-1193: Scroll-to-latest triggers when user scrolls up >40px."""
        assert "< 40" in self.SRC, (
            "MessageList should use 40px threshold for scroll-to-latest button"
        )

    def test_spec_1193_scroll_button_click(self) -> None:
        """SPEC-1193: Scroll-to-latest button scrolls to bottom smoothly."""
        assert "behavior: 'smooth'" in self.SRC, (
            "MessageList scrollToBottom should use smooth scrolling"
        )

    def test_spec_1194_day_separator_today(self) -> None:
        """SPEC-1194: Render day separator with 'Today' label."""
        assert "locale.today" in self.SRC, (
            "MessageList should use locale.today for today's date separator"
        )

    def test_spec_1194_day_separator_yesterday(self) -> None:
        """SPEC-1194: Render day separator with 'Yesterday' label."""
        assert "locale.yesterday" in self.SRC, (
            "MessageList should use locale.yesterday for yesterday's separator"
        )

    def test_spec_1194_day_separator_formatted_date(self) -> None:
        """SPEC-1194: Render day separator with formatted date for older messages."""
        assert "toLocaleDateString" in self.SRC, (
            "MessageList should use toLocaleDateString for older date separators"
        )

    def test_spec_1194_get_day_label_function(self) -> None:
        """SPEC-1194: getDayLabel helper handles Today, Yesterday, and formatted."""
        assert "function getDayLabel" in self.SRC, (
            "MessageList should define getDayLabel helper function"
        )

    def test_spec_1195_consecutive_agent_avatar_grouping(self) -> None:
        """SPEC-1195: Group consecutive agent messages and hide avatar on subsequent."""
        assert "shouldShowAvatar" in self.SRC, (
            "MessageList should use shouldShowAvatar for consecutive message grouping"
        )

    def test_spec_1195_avatar_logic_checks_previous_role(self) -> None:
        """SPEC-1195: shouldShowAvatar checks if previous message is from same role."""
        assert "prev.role !== 'agent'" in self.SRC, (
            "shouldShowAvatar should compare previous message role"
        )

    def test_spec_1196_typing_indicator(self) -> None:
        """SPEC-1196: Show typing indicator when agent is typing."""
        assert "<TypingIndicator" in self.SRC, (
            "MessageList should render <TypingIndicator /> when agent is typing"
        )

    def test_spec_1196_typing_gated_by_state(self) -> None:
        """SPEC-1196: Typing indicator gated by isAgentTyping prop."""
        assert "isAgentTyping" in self.SRC, (
            "MessageList should use isAgentTyping prop to gate typing indicator"
        )

    def test_spec_1197_greeting_message_area(self) -> None:
        """SPEC-1197: Display greeting message area at start of conversation."""
        assert "greetingMessage" in self.SRC, (
            "MessageList should accept greetingMessage prop"
        )

    def test_spec_1197_greeting_shown_when_no_messages(self) -> None:
        """SPEC-1197: Greeting only shown when messages list is empty."""
        assert "messages.length === 0" in self.SRC, (
            "MessageList should show greeting only when messages.length === 0"
        )

    def test_spec_1197_quick_actions_in_greeting(self) -> None:
        """SPEC-1197: Quick action buttons rendered in greeting area."""
        assert "<QuickActions" in self.SRC, (
            "MessageList should render <QuickActions /> in greeting area"
        )


# ===================================================================
# MessageBubble.tsx
# ===================================================================


class TestMessageBubble:
    """Message bubble component. SPEC-1198..1204."""

    SRC = _read("MessageBubble.tsx")

    def test_spec_1198_customer_bubble_right_aligned(self) -> None:
        """SPEC-1198: Customer bubbles are right-aligned via row-reverse."""
        assert "row-reverse" in self.SRC, (
            "MessageBubble should use flexDirection row-reverse for customer messages"
        )

    def test_spec_1198_customer_bubble_primary_color(self) -> None:
        """SPEC-1198: Customer bubbles use primary color (colorCustomerBubble)."""
        assert "colorCustomerBubble" in self.SRC, (
            "MessageBubble should use colorCustomerBubble for customer messages"
        )

    def test_spec_1198_agent_bubble_left_aligned(self) -> None:
        """SPEC-1198: Agent bubbles left-aligned (flexDirection: 'row' for non-customer)."""
        # isCustomer ? 'row-reverse' : 'row' -- the 'row' is the agent direction
        assert re.search(r"isCustomer\s*\?\s*'row-reverse'\s*:\s*'row'", self.SRC), (
            "MessageBubble should use 'row' direction for agent messages"
        )

    def test_spec_1198_agent_bubble_surface_color(self) -> None:
        """SPEC-1198: Agent bubbles use surface color (colorAgentBubble)."""
        assert "colorAgentBubble" in self.SRC, (
            "MessageBubble should use colorAgentBubble for agent messages"
        )

    def test_spec_1199_markdown_link_regex(self) -> None:
        """SPEC-1199: Parse markdown links [text](url) with regex."""
        assert "MARKDOWN_LINK_RE" in self.SRC, (
            "MessageBubble should define MARKDOWN_LINK_RE regex"
        )
        # The actual regex in source: /\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g
        assert "renderWithLinks" in self.SRC, (
            "MessageBubble should define renderWithLinks function for link parsing"
        )

    def test_spec_1199_links_target_top(self) -> None:
        """SPEC-1199: Parsed links open with target='_top' (parent frame, not iframe)."""
        assert 'target="_top"' in self.SRC, (
            "MessageBubble links should use target='_top' to open in parent frame"
        )

    def test_spec_1200_streaming_cursor_animation(self) -> None:
        """SPEC-1200: Show streaming cursor animation during token delivery."""
        assert "message.streaming" in self.SRC, (
            "MessageBubble should check message.streaming state"
        )

    def test_spec_1200_cursor_blink_animation(self) -> None:
        """SPEC-1200: Streaming cursor uses ar-blink animation."""
        assert "ar-blink" in self.SRC, (
            "MessageBubble streaming cursor should use ar-blink animation"
        )

    def test_spec_1201_retracted_opacity(self) -> None:
        """SPEC-1201: Retracted messages styled with opacity 0.7."""
        assert "opacity: 0.7" in self.SRC, (
            "MessageBubble should apply opacity: 0.7 to retracted messages"
        )

    def test_spec_1201_retracted_red_border(self) -> None:
        """SPEC-1201: Retracted messages have red (colorError) border."""
        assert re.search(r"borderLeft:.*colorError", self.SRC), (
            "MessageBubble retracted messages should have borderLeft with colorError"
        )

    def test_spec_1201_retracted_label(self) -> None:
        """SPEC-1201: Retracted messages show 'Message revised' label."""
        assert "Message revised" in self.SRC, (
            "MessageBubble should display 'Message revised' label for retracted messages"
        )

    def test_spec_1201_retracted_conditional(self) -> None:
        """SPEC-1201: Retracted styling gated by message.retracted flag."""
        assert "message.retracted" in self.SRC, (
            "MessageBubble should check message.retracted flag"
        )

    def test_spec_1202_source_citation_domains(self) -> None:
        """SPEC-1202: Extract and display source citation domains from links."""
        assert "extractSourceDomains" in self.SRC, (
            "MessageBubble should define extractSourceDomains function"
        )

    def test_spec_1202_domain_extraction_strips_www(self) -> None:
        """SPEC-1202: Source domain extraction strips 'www.' prefix."""
        assert "replace(/^www\\./, '')" in self.SRC, (
            "extractSourceDomains should strip www. prefix from hostnames"
        )

    def test_spec_1202_source_icon(self) -> None:
        """SPEC-1202: Source citations display with a globe/link icon."""
        assert "SourceIcon" in self.SRC, (
            "MessageBubble should use SourceIcon for source citations"
        )

    def test_spec_1203_max_width_75_percent(self) -> None:
        """SPEC-1203: Message bubble max width limited to 75%."""
        assert "maxWidth: '75%'" in self.SRC, (
            "MessageBubble should set maxWidth: '75%'"
        )

    def test_spec_1204_timestamp_12_hour_format(self) -> None:
        """SPEC-1204: Timestamps displayed in 12-hour format with AM/PM."""
        assert "AM" in self.SRC and "PM" in self.SRC, (
            "formatTime should produce AM/PM 12-hour format"
        )

    def test_spec_1204_format_time_function(self) -> None:
        """SPEC-1204: formatTime helper converts timestamp to 12-hour string."""
        assert "function formatTime" in self.SRC, (
            "MessageBubble should define formatTime helper"
        )

    def test_spec_1204_12_hour_modulo(self) -> None:
        """SPEC-1204: formatTime uses modulo 12 for 12-hour conversion."""
        assert "hours % 12" in self.SRC, (
            "formatTime should use hours % 12 for 12-hour conversion"
        )


# ===================================================================
# InputBar.tsx
# ===================================================================


class TestInputBar:
    """Input bar component. SPEC-1206, SPEC-1207, SPEC-1209, SPEC-1210."""

    SRC = _read("InputBar.tsx")

    def test_spec_1206_enter_to_send(self) -> None:
        """SPEC-1206: Enter key sends the message."""
        assert "e.key === 'Enter'" in self.SRC, (
            "InputBar should check e.key === 'Enter' for send"
        )

    def test_spec_1206_shift_enter_for_newline(self) -> None:
        """SPEC-1206: Shift+Enter inserts a newline (does not send)."""
        assert "!e.shiftKey" in self.SRC, (
            "InputBar should check !e.shiftKey to allow shift+enter for newline"
        )

    def test_spec_1206_prevent_default_on_enter(self) -> None:
        """SPEC-1206: Enter key triggers preventDefault to avoid default newline."""
        assert "e.preventDefault()" in self.SRC, (
            "InputBar should call e.preventDefault() on Enter key"
        )

    def test_spec_1207_max_length_2000(self) -> None:
        """SPEC-1207: Enforce 2000 character max on messages."""
        assert "MAX_MESSAGE_LENGTH = 2000" in self.SRC, (
            "InputBar should define MAX_MESSAGE_LENGTH = 2000"
        )

    def test_spec_1207_max_length_enforcement(self) -> None:
        """SPEC-1207: Text truncated to MAX_MESSAGE_LENGTH on input."""
        assert "value.length > MAX_MESSAGE_LENGTH" in self.SRC, (
            "InputBar should check input value length against MAX_MESSAGE_LENGTH"
        )

    def test_spec_1207_visual_warning_at_90_percent(self) -> None:
        """SPEC-1207: Show visual warning at 90% of max character threshold."""
        assert "MAX_MESSAGE_LENGTH * 0.9" in self.SRC, (
            "InputBar should show character count warning at 90% threshold"
        )

    def test_spec_1207_char_count_display(self) -> None:
        """SPEC-1207: Display current/max character count."""
        assert "text.length}/{MAX_MESSAGE_LENGTH}" in self.SRC, (
            "InputBar should display text.length/MAX_MESSAGE_LENGTH counter"
        )

    def test_spec_1209_file_upload_button(self) -> None:
        """SPEC-1209: Show file upload button when fileUploadEnabled is true."""
        assert "fileUploadEnabled" in self.SRC, (
            "InputBar should accept fileUploadEnabled prop"
        )

    def test_spec_1209_paperclip_icon(self) -> None:
        """SPEC-1209: File upload button uses PaperclipIcon."""
        assert "PaperclipIcon" in self.SRC, (
            "InputBar should use PaperclipIcon for file upload button"
        )

    def test_spec_1209_file_button_conditional(self) -> None:
        """SPEC-1209: File upload button conditionally rendered."""
        assert re.search(r"fileUploadEnabled\s*&&", self.SRC), (
            "InputBar should conditionally render file upload button"
        )

    def test_spec_1210_powered_by_branding(self) -> None:
        """SPEC-1210: Display 'Powered by Agent Red' branding."""
        assert "showBranding" in self.SRC, (
            "InputBar should accept showBranding prop"
        )

    def test_spec_1210_branding_link_to_agentredcx(self) -> None:
        """SPEC-1210: Branding links to agentredcx.com."""
        assert "https://agentredcx.com" in self.SRC, (
            "InputBar branding should link to https://agentredcx.com"
        )

    def test_spec_1210_branding_locale_text(self) -> None:
        """SPEC-1210: Branding text comes from locale.poweredBy."""
        assert "locale.poweredBy" in self.SRC, (
            "InputBar branding should use locale.poweredBy text"
        )

    def test_spec_1210_branding_conditional(self) -> None:
        """SPEC-1210: Branding only shown when showBranding is true."""
        assert re.search(r"showBranding\s*&&", self.SRC), (
            "InputBar branding should be conditionally rendered"
        )


# ===================================================================
# QuickActions.tsx
# ===================================================================


class TestQuickActions:
    """Quick action buttons component. SPEC-1154, SPEC-1211..1213."""

    SRC = _read("QuickActions.tsx")
    TOKENS_SRC = _read_theme("tokens.ts")

    def test_spec_1154_interface_id(self) -> None:
        """SPEC-1154: QuickActionButton interface has 'id' field."""
        assert re.search(r"interface QuickActionButton", self.TOKENS_SRC), (
            "tokens.ts should define QuickActionButton interface"
        )
        assert re.search(r"id:\s*string", self.TOKENS_SRC), (
            "QuickActionButton interface should have id: string"
        )

    def test_spec_1154_interface_label(self) -> None:
        """SPEC-1154: QuickActionButton interface has 'label' field."""
        assert re.search(r"label:\s*string", self.TOKENS_SRC), (
            "QuickActionButton interface should have label: string"
        )

    def test_spec_1154_interface_prompt_template(self) -> None:
        """SPEC-1154: QuickActionButton interface has 'prompt_template' field."""
        assert re.search(r"prompt_template:\s*string", self.TOKENS_SRC), (
            "QuickActionButton interface should have prompt_template: string"
        )

    def test_spec_1154_interface_optional_icon(self) -> None:
        """SPEC-1154: QuickActionButton interface has optional 'icon' field."""
        assert re.search(r"icon\?\s*:", self.TOKENS_SRC), (
            "QuickActionButton interface should have optional icon field"
        )

    def test_spec_1211_max_2_visible(self) -> None:
        """SPEC-1211: Render max 2 visible quick action buttons."""
        assert "actions.slice(0, 2)" in self.SRC, (
            "QuickActions should limit visible buttons to slice(0, 2)"
        )

    def test_spec_1211_pill_button_shape(self) -> None:
        """SPEC-1211: Quick action buttons render as pill-shaped (full border radius)."""
        assert "borderRadiusFull" in self.SRC, (
            "QuickActions buttons should use borderRadiusFull for pill shape"
        )

    def test_spec_1211_hover_effects(self) -> None:
        """SPEC-1211: Quick action buttons have hover background change."""
        assert "colorSurfaceHover" in self.SRC, (
            "QuickActions should use colorSurfaceHover on hover"
        )

    def test_spec_1211_hover_state_tracking(self) -> None:
        """SPEC-1211: Hover state tracked via hoveredId state."""
        assert "hoveredId" in self.SRC, (
            "QuickActions should track hoveredId state for hover effects"
        )

    def test_spec_1212_max_width_280px(self) -> None:
        """SPEC-1212: Quick action button max width limited to 280px."""
        assert "maxWidth: '280px'" in self.SRC, (
            "QuickActions buttons should set maxWidth: '280px'"
        )

    def test_spec_1212_text_overflow_ellipsis(self) -> None:
        """SPEC-1212: Long button labels truncated with text-overflow ellipsis."""
        assert "textOverflow: 'ellipsis'" in self.SRC, (
            "QuickActions should use textOverflow: 'ellipsis' for long labels"
        )

    def test_spec_1213_fade_in_animation(self) -> None:
        """SPEC-1213: Quick action buttons appear with fade-in animation."""
        assert "ar-fade-in" in self.SRC, (
            "QuickActions should use ar-fade-in animation on appearance"
        )

    def test_spec_1213_animation_duration(self) -> None:
        """SPEC-1213: fade-in animation duration is 0.3s."""
        assert "ar-fade-in 0.3s" in self.SRC, (
            "QuickActions fade-in animation should have 0.3s duration"
        )
