"""
Source inspection tests -- Admin contextual tooltips (WI-0773..0778 + WI-0798).

Verifies HelpTooltip presence across all admin pages:
  - HelpTooltip component exists with correct interface
  - Dashboard: stat cards & section headings (WI-0773)
  - Configuration: brand, policies, escalation, language (WI-0774)
  - Widget: appearance, behavior, pre-chat/offline form (WI-0775, WI-0798)
  - Knowledge Base: toolbar, categories, status (WI-0776)
  - Billing/Usage: tier info, metrics, upgrade (WI-0777)
  - Team Management: roles, escalation routing (WI-0778)
  - Documentation links (docLink) across all pages

Run with:
    pytest tests/widget/test_admin_tooltips.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADMIN_STANDALONE = ROOT / "admin" / "standalone" / "pages"
ADMIN_SHARED = ROOT / "admin" / "shared"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    """Read a TypeScript source file and return its content."""
    assert path.exists(), f"Source file not found: {path}"
    return path.read_text(encoding="utf-8")


def _count_pattern(source: str, pattern: str) -> int:
    """Count regex pattern occurrences in source."""
    return len(re.findall(pattern, source))


# ===========================================================================
# TestHelpTooltipComponent — Shared component interface (WI-0773 foundation)
# ===========================================================================


class TestHelpTooltipComponent:
    """Verify HelpTooltip component exists with correct props interface."""

    def test_component_file_exists(self) -> None:
        """HelpTooltip.tsx must exist in admin/shared/."""
        path = ADMIN_SHARED / "HelpTooltip.tsx"
        assert path.exists(), "HelpTooltip.tsx missing from admin/shared/"

    def test_exports_help_tooltip(self) -> None:
        """Component exports HelpTooltip as named export."""
        source = _read(ADMIN_SHARED / "HelpTooltip.tsx")
        assert "export const HelpTooltip" in source

    def test_has_text_prop(self) -> None:
        """HelpTooltip accepts a 'text' prop for tooltip content."""
        source = _read(ADMIN_SHARED / "HelpTooltip.tsx")
        assert "text: string" in source or "text:" in source

    def test_has_doc_link_prop(self) -> None:
        """HelpTooltip accepts an optional 'docLink' prop."""
        source = _read(ADMIN_SHARED / "HelpTooltip.tsx")
        assert "docLink" in source

    def test_renders_question_mark_icon(self) -> None:
        """HelpTooltip renders a circled '?' icon."""
        source = _read(ADMIN_SHARED / "HelpTooltip.tsx")
        # The component renders a literal '?' character in JSX (between > and {visible)
        assert re.search(r">\s*\?\s*[{<]", source), \
            "HelpTooltip must render a '?' character"

    def test_has_hover_show_hide(self) -> None:
        """HelpTooltip shows on mouseEnter and hides on mouseLeave."""
        source = _read(ADMIN_SHARED / "HelpTooltip.tsx")
        assert "onMouseEnter" in source
        assert "onMouseLeave" in source

    def test_has_keyboard_accessibility(self) -> None:
        """HelpTooltip supports focus/blur for keyboard users."""
        source = _read(ADMIN_SHARED / "HelpTooltip.tsx")
        assert "onFocus" in source
        assert "onBlur" in source
        assert "tabIndex" in source

    def test_has_aria_label(self) -> None:
        """HelpTooltip has aria-label for screen readers."""
        source = _read(ADMIN_SHARED / "HelpTooltip.tsx")
        assert "aria-label" in source

    def test_renders_learn_more_link(self) -> None:
        """When docLink is provided, renders a 'Learn more' anchor."""
        source = _read(ADMIN_SHARED / "HelpTooltip.tsx")
        assert "Learn more" in source
        assert "target=\"_blank\"" in source
        assert "noopener noreferrer" in source


# ===========================================================================
# TestDashboardTooltips — WI-0773: Dashboard metric & section tooltips
# ===========================================================================


class TestDashboardTooltips:
    """Verify Dashboard.tsx has contextual tooltips on all key metrics."""

    DASHBOARD = ADMIN_STANDALONE / "Dashboard.tsx"

    def test_imports_help_tooltip(self) -> None:
        """Dashboard imports HelpTooltip component."""
        source = _read(self.DASHBOARD)
        assert "HelpTooltip" in source

    def test_total_conversations_tooltip(self) -> None:
        """Total conversations stat card has a tooltip."""
        source = _read(self.DASHBOARD)
        assert "Total conversations" in source
        # Verify it has HelpTooltip nearby with meaningful text
        assert "Billable customer conversations in the selected period" in source

    def test_avg_response_time_tooltip(self) -> None:
        """Average response time stat card has a tooltip."""
        source = _read(self.DASHBOARD)
        assert "Avg response time" in source
        assert "Average time for the AI to generate" in source

    def test_resolution_rate_tooltip(self) -> None:
        """Resolution rate stat card has a tooltip."""
        source = _read(self.DASHBOARD)
        assert "Resolution rate" in source
        assert "resolved by the AI without human escalation" in source

    def test_customer_satisfaction_tooltip(self) -> None:
        """Customer satisfaction stat card has a tooltip."""
        source = _read(self.DASHBOARD)
        assert "Customer satisfaction" in source
        assert "1-5 scale" in source

    def test_escalation_rate_tooltip(self) -> None:
        """Escalation rate stat card has a tooltip."""
        source = _read(self.DASHBOARD)
        assert "Escalation rate" in source
        assert "handed off to a human" in source

    def test_conversation_volume_tooltip(self) -> None:
        """Daily usage chart has a section tooltip (SPEC-1685)."""
        source = _read(self.DASHBOARD)
        assert "Daily usage" in source
        assert "Daily conversation volume" in source

    def test_recent_conversations_tooltip(self) -> None:
        """Recent conversations section has a tooltip."""
        source = _read(self.DASHBOARD)
        assert "Recent conversations" in source
        assert "5 most recent" in source

    def test_top_topics_tooltip(self) -> None:
        """Top topics section has a tooltip."""
        source = _read(self.DASHBOARD)
        assert "Top topics" in source
        assert "Most frequent query categories" in source

    def test_topic_breakdown_tooltip(self) -> None:
        """Topic breakdown section has a tooltip."""
        source = _read(self.DASHBOARD)
        assert "Topic breakdown" in source

    def test_knowledge_gaps_tooltip(self) -> None:
        """Knowledge gaps section has a tooltip."""
        source = _read(self.DASHBOARD)
        assert "Knowledge gaps" in source
        assert "lacked sufficient knowledge" in source

    def test_dashboard_has_doc_links(self) -> None:
        """Dashboard tooltips include documentation links."""
        source = _read(self.DASHBOARD)
        doc_link_count = _count_pattern(source, r"docLink=")
        assert doc_link_count >= 8, \
            f"Dashboard should have ≥8 doc links, found {doc_link_count}"

    def test_dashboard_minimum_tooltip_count(self) -> None:
        """Dashboard has at least 10 HelpTooltip instances."""
        source = _read(self.DASHBOARD)
        tooltip_count = _count_pattern(source, r"HelpTooltip")
        # 1 import + at least 10 usage = 11 minimum
        assert tooltip_count >= 11, \
            f"Dashboard should have ≥11 HelpTooltip refs, found {tooltip_count}"


# ===========================================================================
# TestConfigurationTooltips — WI-0774: AI Configuration tooltips
# ===========================================================================


class TestConfigurationTooltips:
    """Verify Configuration.tsx has contextual tooltips on all settings sections."""

    CONFIG = ADMIN_STANDALONE / "Configuration.tsx"

    def test_imports_help_tooltip(self) -> None:
        """Configuration imports HelpTooltip component."""
        source = _read(self.CONFIG)
        assert "HelpTooltip" in source

    def test_has_multiple_tooltips(self) -> None:
        """Configuration has at least 6 tooltip instances."""
        source = _read(self.CONFIG)
        # HelpTooltip usages (excluding import line)
        usage_count = _count_pattern(source, r"<HelpTooltip|tooltip=")
        assert usage_count >= 6, \
            f"Configuration should have ≥6 tooltip usages, found {usage_count}"

    def test_has_doc_links(self) -> None:
        """Configuration tooltips include documentation links."""
        source = _read(self.CONFIG)
        doc_link_count = _count_pattern(source, r"docLink")
        assert doc_link_count >= 6, \
            f"Configuration should have ≥6 doc links, found {doc_link_count}"


# ===========================================================================
# TestWidgetTooltips — WI-0775 + WI-0798: Widget config & form tooltips
# ===========================================================================


class TestWidgetTooltips:
    """Verify Widget.tsx has tooltips on appearance, behavior, and form sections."""

    WIDGET = ADMIN_STANDALONE / "Widget.tsx"

    def test_imports_help_tooltip(self) -> None:
        """Widget page imports HelpTooltip component."""
        source = _read(self.WIDGET)
        assert "HelpTooltip" in source

    def test_appearance_section_tooltip(self) -> None:
        """Appearance section header has a tooltip."""
        source = _read(self.WIDGET)
        assert "widget-appearance" in source or "Appearance" in source

    def test_behavior_section_tooltip(self) -> None:
        """Behavior section header has a tooltip covering pre-chat and idle timeout."""
        source = _read(self.WIDGET)
        # WI-0798: pre-chat form fields mentioned in behavior tooltip
        assert "pre-chat form fields" in source

    def test_content_section_tooltip(self) -> None:
        """Content section header has a tooltip."""
        source = _read(self.WIDGET)
        # SectionHeader with "Content" has tooltip
        assert "Content" in source
        assert "widget-appearance" in source or "Header text" in source

    def test_panel_width_tooltip(self) -> None:
        """Panel width setting has a tooltip explaining compact vs wide."""
        source = _read(self.WIDGET)
        assert "Panel width" in source
        assert "Compact" in source
        assert "Wide" in source

    def test_greeting_message_tooltip(self) -> None:
        """Greeting message field has a tooltip clarifying it's static, not AI-generated."""
        source = _read(self.WIDGET)
        assert "static welcome message" in source or "not generated by the AI" in source

    def test_widget_key_tooltip(self) -> None:
        """Widget key section has a tooltip explaining authentication."""
        source = _read(self.WIDGET)
        assert "widget key authenticates" in source or "embed code" in source

    def test_prechat_form_description(self) -> None:
        """WI-0798: Pre-chat form has a description or tooltip for merchants."""
        source = _read(self.WIDGET)
        # Pre-chat form toggle has description prop
        assert "pre-chat" in source.lower()

    def test_offline_form_present(self) -> None:
        """WI-0798: Offline form is present in widget configuration."""
        source = _read(self.WIDGET)
        assert "offline" in source.lower()

    def test_widget_has_doc_links(self) -> None:
        """Widget tooltips include documentation links."""
        source = _read(self.WIDGET)
        doc_link_count = _count_pattern(source, r"docLink")
        assert doc_link_count >= 5, \
            f"Widget should have ≥5 doc links, found {doc_link_count}"

    def test_widget_minimum_tooltip_count(self) -> None:
        """Widget has at least 5 HelpTooltip/tooltip= instances."""
        source = _read(self.WIDGET)
        tooltip_count = _count_pattern(source, r"<HelpTooltip|tooltip=")
        assert tooltip_count >= 5, \
            f"Widget should have ≥5 tooltip usages, found {tooltip_count}"


# ===========================================================================
# TestKnowledgeBaseTooltips — WI-0776: Knowledge Base tooltips
# ===========================================================================


class TestKnowledgeBaseTooltips:
    """Verify KnowledgeBaseManager.tsx has tooltips on toolbar and status indicators."""

    KB = ADMIN_SHARED / "KnowledgeBaseManager.tsx"

    def test_imports_help_tooltip(self) -> None:
        """Knowledge Base Manager imports HelpTooltip component."""
        source = _read(self.KB)
        assert "HelpTooltip" in source

    def test_has_multiple_tooltips(self) -> None:
        """Knowledge Base has at least 8 tooltip instances."""
        source = _read(self.KB)
        usage_count = _count_pattern(source, r"<HelpTooltip|tooltip=")
        assert usage_count >= 8, \
            f"KB should have ≥8 tooltip usages, found {usage_count}"

    def test_has_doc_links(self) -> None:
        """Knowledge Base tooltips include documentation links."""
        source = _read(self.KB)
        doc_link_count = _count_pattern(source, r"docLink")
        assert doc_link_count >= 6, \
            f"KB should have ≥6 doc links, found {doc_link_count}"


# ===========================================================================
# TestBillingTooltips — WI-0777: Billing & Usage tooltips
# ===========================================================================


class TestBillingTooltips:
    """Verify Billing, BillingPortal, and UsageDashboard have contextual tooltips."""

    BILLING = ADMIN_STANDALONE / "Billing.tsx"
    PORTAL = ADMIN_SHARED / "BillingPortal.tsx"
    USAGE = ADMIN_SHARED / "UsageDashboard.tsx"

    # -- Billing page --

    def test_billing_imports_help_tooltip(self) -> None:
        """Billing page imports HelpTooltip component."""
        source = _read(self.BILLING)
        assert "HelpTooltip" in source

    def test_billing_has_tooltips(self) -> None:
        """Billing page has tooltip instances."""
        source = _read(self.BILLING)
        usage_count = _count_pattern(source, r"<HelpTooltip|tooltip=")
        assert usage_count >= 4, \
            f"Billing should have ≥4 tooltip usages, found {usage_count}"

    def test_billing_has_doc_links(self) -> None:
        """Billing page tooltips include documentation links."""
        source = _read(self.BILLING)
        doc_link_count = _count_pattern(source, r"docLink")
        assert doc_link_count >= 3, \
            f"Billing should have ≥3 doc links, found {doc_link_count}"

    # -- BillingPortal --

    def test_portal_imports_help_tooltip(self) -> None:
        """BillingPortal imports HelpTooltip component."""
        source = _read(self.PORTAL)
        assert "HelpTooltip" in source

    def test_portal_has_tooltips(self) -> None:
        """BillingPortal has at least 10 tooltip instances."""
        source = _read(self.PORTAL)
        usage_count = _count_pattern(source, r"<HelpTooltip|tooltip=")
        assert usage_count >= 10, \
            f"BillingPortal should have ≥10 tooltip usages, found {usage_count}"

    def test_portal_has_doc_links(self) -> None:
        """BillingPortal tooltips include documentation links."""
        source = _read(self.PORTAL)
        doc_link_count = _count_pattern(source, r"docLink")
        assert doc_link_count >= 8, \
            f"BillingPortal should have ≥8 doc links, found {doc_link_count}"

    # -- UsageDashboard --

    def test_usage_imports_help_tooltip(self) -> None:
        """UsageDashboard imports HelpTooltip component."""
        source = _read(self.USAGE)
        assert "HelpTooltip" in source

    def test_usage_has_tooltips(self) -> None:
        """UsageDashboard has tooltip instances."""
        source = _read(self.USAGE)
        usage_count = _count_pattern(source, r"<HelpTooltip|tooltip=")
        assert usage_count >= 5, \
            f"UsageDashboard should have ≥5 tooltip usages, found {usage_count}"

    def test_usage_has_doc_links(self) -> None:
        """UsageDashboard tooltips include documentation links."""
        source = _read(self.USAGE)
        doc_link_count = _count_pattern(source, r"docLink")
        assert doc_link_count >= 4, \
            f"UsageDashboard should have ≥4 doc links, found {doc_link_count}"


# ===========================================================================
# TestTeamTooltips — WI-0778: Team Management tooltips
# ===========================================================================


class TestTeamTooltips:
    """Verify Team management dialogs have contextual tooltips."""

    EDIT_DIALOG = ADMIN_SHARED / "team" / "EditMemberDialog.tsx"
    INVITE_FORM = ADMIN_SHARED / "team" / "InviteForm.tsx"

    def test_edit_dialog_imports_help_tooltip(self) -> None:
        """EditMemberDialog imports HelpTooltip component."""
        source = _read(self.EDIT_DIALOG)
        assert "HelpTooltip" in source

    def test_edit_dialog_role_tooltip(self) -> None:
        """EditMemberDialog has a tooltip explaining roles."""
        source = _read(self.EDIT_DIALOG)
        assert "Role" in source
        # Tooltip explains role differences
        assert "Owner" in source or "Viewer" in source or "read-only" in source

    def test_edit_dialog_escalation_tooltip(self) -> None:
        """EditMemberDialog has a tooltip for escalation category assignment."""
        source = _read(self.EDIT_DIALOG)
        assert "escalat" in source.lower()

    def test_edit_dialog_has_doc_links(self) -> None:
        """EditMemberDialog tooltips include documentation links."""
        source = _read(self.EDIT_DIALOG)
        doc_link_count = _count_pattern(source, r"docLink")
        assert doc_link_count >= 1, \
            f"EditMemberDialog should have ≥1 doc link, found {doc_link_count}"

    def test_invite_form_imports_help_tooltip(self) -> None:
        """InviteForm imports HelpTooltip component."""
        source = _read(self.INVITE_FORM)
        assert "HelpTooltip" in source

    def test_invite_form_has_tooltips(self) -> None:
        """InviteForm has tooltip instances."""
        source = _read(self.INVITE_FORM)
        usage_count = _count_pattern(source, r"<HelpTooltip|tooltip=")
        assert usage_count >= 2, \
            f"InviteForm should have ≥2 tooltip usages, found {usage_count}"

    def test_invite_form_has_doc_links(self) -> None:
        """InviteForm tooltips include documentation links."""
        source = _read(self.INVITE_FORM)
        doc_link_count = _count_pattern(source, r"docLink")
        assert doc_link_count >= 1, \
            f"InviteForm should have ≥1 doc link, found {doc_link_count}"


# ===========================================================================
# TestCrossPageTooltipCoverage — Aggregate validation
# ===========================================================================


class TestCrossPageTooltipCoverage:
    """Verify comprehensive tooltip coverage across all major admin pages."""

    PAGES_TO_CHECK = {
        "Dashboard": ADMIN_STANDALONE / "Dashboard.tsx",
        "Configuration": ADMIN_STANDALONE / "Configuration.tsx",
        "Widget": ADMIN_STANDALONE / "Widget.tsx",
        "KnowledgeBase": ADMIN_SHARED / "KnowledgeBaseManager.tsx",
        "Billing": ADMIN_STANDALONE / "Billing.tsx",
        "BillingPortal": ADMIN_SHARED / "BillingPortal.tsx",
        "UsageDashboard": ADMIN_SHARED / "UsageDashboard.tsx",
        "ConversationInbox": ADMIN_SHARED / "ConversationInbox.tsx",
        "MemoryPrivacy": ADMIN_STANDALONE / "MemoryPrivacy.tsx",
    }

    def test_all_major_pages_import_help_tooltip(self) -> None:
        """Every major admin page must import HelpTooltip."""
        missing = []
        for name, path in self.PAGES_TO_CHECK.items():
            source = _read(path)
            if "HelpTooltip" not in source:
                missing.append(name)
        assert not missing, \
            f"Pages missing HelpTooltip import: {missing}"

    def test_all_major_pages_have_doc_links(self) -> None:
        """Every major admin page must have at least 1 documentation link."""
        no_links = []
        for name, path in self.PAGES_TO_CHECK.items():
            source = _read(path)
            if "docLink" not in source:
                no_links.append(name)
        assert not no_links, \
            f"Pages without doc links: {no_links}"

    def test_total_tooltip_count_across_all_pages(self) -> None:
        """Aggregate: at least 60 tooltip instances across all admin pages."""
        total = 0
        for path in self.PAGES_TO_CHECK.values():
            source = _read(path)
            total += _count_pattern(source, r"<HelpTooltip|tooltip=")
        assert total >= 60, \
            f"Total tooltips across all pages should be ≥60, found {total}"

    def test_total_doc_links_across_all_pages(self) -> None:
        """Aggregate: at least 50 documentation links across all admin pages."""
        total = 0
        for path in self.PAGES_TO_CHECK.values():
            source = _read(path)
            total += _count_pattern(source, r"docLink")
        assert total >= 50, \
            f"Total doc links across all pages should be ≥50, found {total}"

    def test_help_tooltip_component_is_shared(self) -> None:
        """HelpTooltip is a single shared component, not duplicated per page."""
        component = ADMIN_SHARED / "HelpTooltip.tsx"
        assert component.exists(), "Shared HelpTooltip.tsx must exist"
        # Verify pages import from shared, not define their own
        for name, path in self.PAGES_TO_CHECK.items():
            source = _read(path)
            if "HelpTooltip" in source:
                assert "export const HelpTooltip" not in source, \
                    f"{name} must not re-define HelpTooltip (should import from shared)"
