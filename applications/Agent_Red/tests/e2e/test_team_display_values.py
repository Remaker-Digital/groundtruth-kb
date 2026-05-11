"""
E2E tests — Team page display values.

Verifies that mock API data (MOCK_TEAM_MEMBERS) is correctly rendered into the
Team page table. Each test targets a specific data value rather than structural
presence (see test_team_page.py for structure and interaction tests).

Mock members:
  - "Test Admin" — superadmin, admin@testco.com, 0 escalations
  - "Jane Agent" — escalation_agent, agent@testco.com, categories: support+technical, 3 escalations
  - "View Only" — viewer, viewer@testco.com, 0 escalations

Run with:
    pytest tests/e2e/test_team_display_values.py -v --headed
    pytest tests/e2e/test_team_display_values.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

from .conftest import MOCK_TEAM_MEMBERS

pytestmark = pytest.mark.e2e

# Shorthand for the members list
_MEMBERS = MOCK_TEAM_MEMBERS["members"]
_ADMIN = _MEMBERS[0]   # Test Admin, superadmin
_AGENT = _MEMBERS[1]   # Jane Agent, escalation_agent
_VIEWER = _MEMBERS[2]  # View Only, viewer


# ===========================================================================
# Member Count
# ===========================================================================


class TestTeamMemberCountValue:
    """Verify the team member count reflects the mock data."""

    def test_member_count_shows_three(self, admin_team_page: Page) -> None:
        """Member count text shows '3 team members'."""
        expect(admin_team_page.get_by_text("3 team members").first).to_be_visible()

    def test_member_count_matches_mock_length(self, admin_team_page: Page) -> None:
        """Displayed count matches the number of members in MOCK_TEAM_MEMBERS."""
        count_text = f"{len(_MEMBERS)} team members"
        expect(admin_team_page.get_by_text(count_text).first).to_be_visible()


# ===========================================================================
# Team Member Table Values
# ===========================================================================


class TestTeamMemberTableValues:
    """Verify each team member's data is correctly rendered in the table."""

    # --- Test Admin (superadmin) ---

    def test_admin_display_name(self, admin_team_page: Page) -> None:
        """Superadmin row displays 'Test Admin'."""
        expect(admin_team_page.get_by_text("Test Admin").first).to_be_visible()

    def test_admin_email(self, admin_team_page: Page) -> None:
        """Superadmin row displays 'admin@testco.com'."""
        expect(admin_team_page.get_by_text("admin@testco.com").first).to_be_visible()

    def test_admin_role_badge(self, admin_team_page: Page) -> None:
        """Superadmin row shows 'Superadmin' as a badge (not a select)."""
        row = admin_team_page.locator("tr", has_text="admin@testco.com")
        badge = row.get_by_text("Superadmin")
        expect(badge).to_be_visible()
        # Should NOT be a select element
        selects = row.locator("select")
        expect(selects).to_have_count(0)

    def test_admin_escalation_count_dash(self, admin_team_page: Page) -> None:
        """Superadmin escalation column shows '--' (not an escalation agent)."""
        row = admin_team_page.locator("tr", has_text="admin@testco.com")
        expect(row.get_by_text("--").first).to_be_visible()

    def test_admin_no_category_chips(self, admin_team_page: Page) -> None:
        """Superadmin row has no escalation category chip buttons."""
        row = admin_team_page.locator("tr", has_text="admin@testco.com")
        # Superadmin has no select, no remove button, no category chips
        # Only a spacer span for alignment
        category_btns = row.locator(
            'button'
            ':not([aria-label="Remove member"])'
            ':not([aria-label="Disable member"])'
            ':not([aria-label="Enable member"])'
        )
        expect(category_btns).to_have_count(0)

    def test_admin_status_active(self, admin_team_page: Page) -> None:
        """Superadmin row does not have an Active/Disabled toggle (owner protection)."""
        row = admin_team_page.locator("tr", has_text="admin@testco.com")
        toggle = row.locator('button[aria-label="Disable member"]')
        expect(toggle).to_have_count(0)

    # --- Jane Agent (escalation_agent) ---

    def test_agent_display_name(self, admin_team_page: Page) -> None:
        """Agent row displays 'Jane Agent'."""
        expect(admin_team_page.get_by_text("Jane Agent").first).to_be_visible()

    def test_agent_email(self, admin_team_page: Page) -> None:
        """Agent row displays 'agent@testco.com'."""
        expect(admin_team_page.get_by_text("agent@testco.com").first).to_be_visible()

    def test_agent_role_select_value(self, admin_team_page: Page) -> None:
        """Agent row has a role select with 'escalation_agent' selected."""
        row = admin_team_page.locator("tr", has_text="agent@testco.com")
        role_select = row.locator("select").first
        expect(role_select).to_be_visible()
        val = role_select.input_value()
        assert val == "escalation_agent", \
            f"Agent role select should be 'escalation_agent', got: '{val}'"

    def test_agent_role_label_displayed(self, admin_team_page: Page) -> None:
        """Agent role select shows 'Escalation agent' as the visible label."""
        row = admin_team_page.locator("tr", has_text="agent@testco.com")
        role_select = row.locator("select").first
        # The selected option's text should be 'Escalation agent'
        selected_text = role_select.evaluate(
            "el => el.options[el.selectedIndex]?.text || ''"
        )
        assert selected_text == "Escalation agent", \
            f"Agent role label should be 'Escalation agent', got: '{selected_text}'"

    def test_agent_escalation_count_value(self, admin_team_page: Page) -> None:
        """Agent row shows escalation count of 3."""
        row = admin_team_page.locator("tr", has_text="agent@testco.com")
        expect(row.locator("td >> text=3").first).to_be_visible()

    def test_agent_has_category_chips(self, admin_team_page: Page) -> None:
        """Agent row shows escalation category chip buttons."""
        row = admin_team_page.locator("tr", has_text="agent@testco.com")
        category_btns = row.locator(
            'button'
            ':not([aria-label="Remove member"])'
            ':not([aria-label="Disable member"])'
            ':not([aria-label="Enable member"])'
        )
        assert category_btns.count() > 0, "Agent row should have category chips"

    def test_agent_has_remove_button(self, admin_team_page: Page) -> None:
        """Agent row has a remove member action button."""
        row = admin_team_page.locator("tr", has_text="agent@testco.com")
        remove_btn = row.locator('button[aria-label="Remove member"]')
        expect(remove_btn).to_be_visible()

    # --- View Only (viewer) ---

    def test_viewer_display_name(self, admin_team_page: Page) -> None:
        """Viewer row displays 'View Only'."""
        expect(admin_team_page.get_by_text("View Only").first).to_be_visible()

    def test_viewer_email(self, admin_team_page: Page) -> None:
        """Viewer row displays 'viewer@testco.com'."""
        expect(admin_team_page.get_by_text("viewer@testco.com").first).to_be_visible()

    def test_viewer_role_select_value(self, admin_team_page: Page) -> None:
        """Viewer row has a role select with 'viewer' selected."""
        row = admin_team_page.locator("tr", has_text="viewer@testco.com")
        role_select = row.locator("select").first
        expect(role_select).to_be_visible()
        val = role_select.input_value()
        assert val == "viewer", f"Viewer role select should be 'viewer', got: '{val}'"

    def test_viewer_role_label_displayed(self, admin_team_page: Page) -> None:
        """Viewer role select shows 'Viewer' as the visible label."""
        row = admin_team_page.locator("tr", has_text="viewer@testco.com")
        role_select = row.locator("select").first
        selected_text = role_select.evaluate(
            "el => el.options[el.selectedIndex]?.text || ''"
        )
        assert selected_text == "Viewer", \
            f"Viewer role label should be 'Viewer', got: '{selected_text}'"

    def test_viewer_escalation_count_dash(self, admin_team_page: Page) -> None:
        """Viewer escalation column shows '--' (not an escalation agent)."""
        row = admin_team_page.locator("tr", has_text="viewer@testco.com")
        expect(row.get_by_text("--").first).to_be_visible()

    def test_viewer_no_category_chips(self, admin_team_page: Page) -> None:
        """Viewer row has no escalation category chip buttons."""
        row = admin_team_page.locator("tr", has_text="viewer@testco.com")
        category_btns = row.locator(
            'button'
            ':not([aria-label="Remove member"])'
            ':not([aria-label="Disable member"])'
            ':not([aria-label="Enable member"])'
        )
        expect(category_btns).to_have_count(0)

    def test_viewer_has_remove_button(self, admin_team_page: Page) -> None:
        """Viewer row has a remove member action button."""
        row = admin_team_page.locator("tr", has_text="viewer@testco.com")
        remove_btn = row.locator('button[aria-label="Remove member"]')
        expect(remove_btn).to_be_visible()
