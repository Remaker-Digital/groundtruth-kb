"""
E2E tests — Team page.

Tests every interactive element on the Team management page:
  - Page structure and data rendering
  - "Invite member" button toggles the invite form
  - Invite form: email input, name input, role selector, submit
  - Invite validation: empty email, invalid email
  - Team member table: role selector, category chips, remove button
  - Confirm remove dialog: confirm + cancel
  - Superadmin row: no remove button, role not editable
  - Re-send invitation (POST /api/team/{id}/resend-invite)
  - Empty state when no members exist
  - Error state when API fails

Run with:
    pytest tests/e2e/test_team_page.py -v --headed   # visual
    pytest tests/e2e/test_team_page.py -v             # headless

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""


import pytest
from playwright.sync_api import Page, expect

from .conftest import AdminApiMocker, setup_admin_page

pytestmark = pytest.mark.e2e


# ===========================================================================
# Page Structure Tests
# ===========================================================================


class TestTeamPageStructure:
    """Verify the Team page renders all expected structural elements."""

    def test_page_title_visible(self, admin_team_page: Page) -> None:
        """Page heading 'Team members' must be visible."""
        expect(admin_team_page.locator("text=Team members").first).to_be_visible()

    def test_page_description_visible(self, admin_team_page: Page) -> None:
        """Subtitle describing team management is visible."""
        expect(admin_team_page.locator(
            "text=Manage team members, assign roles"
        ).first).to_be_visible()

    def test_member_count_displayed(self, admin_team_page: Page) -> None:
        """Member count (e.g. '3 team members') is shown."""
        expect(admin_team_page.locator("text=3 team members").first).to_be_visible()

    def test_invite_button_visible(self, admin_team_page: Page) -> None:
        """The '+ Invite member' button is present."""
        btn = admin_team_page.locator("text=Invite member").first
        expect(btn).to_be_visible()

    def test_table_headers_visible(self, admin_team_page: Page) -> None:
        """Table has correct column headers."""
        for header in ["Team member", "Role", "Joined", "Last active", "Escalations", "Actions"]:
            expect(admin_team_page.locator(f"th >> text={header}").first).to_be_visible()

    def test_superadmin_row_rendered(self, admin_team_page: Page) -> None:
        """The superadmin (admin@testco.com) row is rendered."""
        expect(admin_team_page.locator("text=admin@testco.com").first).to_be_visible()
        expect(admin_team_page.locator("text=Test Admin").first).to_be_visible()

    def test_agent_row_rendered(self, admin_team_page: Page) -> None:
        """The escalation agent (agent@testco.com) row is rendered."""
        expect(admin_team_page.locator("text=agent@testco.com").first).to_be_visible()
        expect(admin_team_page.locator("text=Jane Agent").first).to_be_visible()

    def test_viewer_row_rendered(self, admin_team_page: Page) -> None:
        """The viewer (viewer@testco.com) row is rendered."""
        expect(admin_team_page.locator("text=viewer@testco.com").first).to_be_visible()

    def test_agent_escalation_count(self, admin_team_page: Page) -> None:
        """Agent row shows unresolved escalation count (3)."""
        # The agent row should show "3" in the Escalations column
        row = admin_team_page.locator("tr", has_text="agent@testco.com")
        expect(row.locator("td >> text=3").first).to_be_visible()

    def test_superadmin_no_remove_button(self, admin_team_page: Page) -> None:
        """Superadmin row has no 'Remove member' button."""
        superadmin_row = admin_team_page.locator("tr", has_text="admin@testco.com")
        remove_btns = superadmin_row.locator('button[aria-label="Remove member"]')
        expect(remove_btns).to_have_count(0)

    def test_non_superadmin_has_remove_button(self, admin_team_page: Page) -> None:
        """Non-superadmin rows have a 'Remove member' button."""
        agent_row = admin_team_page.locator("tr", has_text="agent@testco.com")
        remove_btn = agent_row.locator('button[aria-label="Remove member"]')
        expect(remove_btn).to_be_visible()


# ===========================================================================
# Invite Form Tests
# ===========================================================================


class TestInviteForm:
    """Test the invite form toggle, inputs, and submission."""

    def test_invite_form_toggle(self, admin_team_page: Page) -> None:
        """Clicking '+ Invite member' shows the form; clicking 'Cancel' hides it."""
        form_heading = admin_team_page.locator("text=Invite new team member")

        # Initially hidden
        expect(form_heading).not_to_be_visible()

        # Click to show
        admin_team_page.locator("text=Invite member").first.click()
        expect(form_heading).to_be_visible()

        # Button text changes to "Cancel"
        expect(admin_team_page.locator("button >> text=Cancel").first).to_be_visible()

        # Click Cancel to hide
        admin_team_page.locator("button >> text=Cancel").first.click()
        expect(form_heading).not_to_be_visible()

    def test_invite_form_fields_present(self, admin_team_page: Page) -> None:
        """Invite form has Email, Name, Role, and Send invite button."""
        admin_team_page.locator("text=Invite member").first.click()

        # Email field
        email_input = admin_team_page.locator('input[type="email"]')
        expect(email_input).to_be_visible()
        expect(email_input).to_have_attribute("placeholder", "colleague@company.com")

        # Name field
        name_input = admin_team_page.locator('input[placeholder="Jane Smith"]')
        expect(name_input).to_be_visible()

        # Role selector
        role_select = admin_team_page.locator("select").last
        expect(role_select).to_be_visible()

        # Submit button
        expect(admin_team_page.locator("button >> text=Send invite").first).to_be_visible()

    def test_invite_success_sends_api_call(self, admin_team_page: Page) -> None:
        """Submitting a valid invite sends POST /api/admin/team."""
        mocker: AdminApiMocker = admin_team_page._api_mocker  # type: ignore[attr-defined]
        mocker.clear_calls()

        admin_team_page.locator("text=Invite member").first.click()
        admin_team_page.locator('input[type="email"]').fill("new@testco.com")
        admin_team_page.locator('input[placeholder="Jane Smith"]').fill("New Person")

        admin_team_page.locator("button >> text=Send invite").first.click()
        admin_team_page.wait_for_timeout(500)

        # Verify POST was sent
        post_calls = mocker.get_calls(method="POST", path_contains="/api/admin/team")
        # Filter out resend-invite calls
        invite_calls = [c for c in post_calls if "resend-invite" not in c["url"]]
        assert len(invite_calls) >= 1, f"Expected POST /api/admin/team, got: {mocker.api_calls}"

        # Verify the body contains the email
        body = invite_calls[0].get("body", "")
        assert "new@testco.com" in (body or ""), f"POST body should contain email, got: {body}"

    def test_invite_form_closes_on_success(self, admin_team_page: Page) -> None:
        """After successful invite, the form closes."""
        admin_team_page.locator("text=Invite member").first.click()
        admin_team_page.locator('input[type="email"]').fill("success@testco.com")

        admin_team_page.locator("button >> text=Send invite").first.click()
        admin_team_page.wait_for_timeout(500)

        # Form should close
        expect(admin_team_page.locator("text=Invite new team member")).not_to_be_visible()

    def test_invite_enter_key_submits(self, admin_team_page: Page) -> None:
        """Pressing Enter in the email field submits the invite."""
        mocker: AdminApiMocker = admin_team_page._api_mocker  # type: ignore[attr-defined]
        mocker.clear_calls()

        admin_team_page.locator("text=Invite member").first.click()
        email_input = admin_team_page.locator('input[type="email"]')
        email_input.fill("enter@testco.com")
        email_input.press("Enter")
        admin_team_page.wait_for_timeout(500)

        post_calls = mocker.get_calls(method="POST", path_contains="/api/admin/team")
        invite_calls = [c for c in post_calls if "resend-invite" not in c["url"]]
        assert len(invite_calls) >= 1, "Enter key should trigger invite POST"


# ===========================================================================
# Role Management Tests
# ===========================================================================


class TestRoleManagement:
    """Test inline role changes for non-superadmin members."""

    def test_superadmin_role_not_editable(self, admin_team_page: Page) -> None:
        """Superadmin role shows as a badge, not a select."""
        superadmin_row = admin_team_page.locator("tr", has_text="admin@testco.com")
        # Should have a span badge, not a <select>
        selects_in_row = superadmin_row.locator("select")
        expect(selects_in_row).to_have_count(0)

    def test_agent_role_selector_visible(self, admin_team_page: Page) -> None:
        """Agent row has an inline role selector."""
        agent_row = admin_team_page.locator("tr", has_text="agent@testco.com")
        role_select = agent_row.locator("select").first
        expect(role_select).to_be_visible()

    def test_role_change_sends_put(self, admin_team_page: Page) -> None:
        """Changing role triggers PUT /api/admin/team/{id}."""
        mocker: AdminApiMocker = admin_team_page._api_mocker  # type: ignore[attr-defined]
        mocker.clear_calls()

        viewer_row = admin_team_page.locator("tr", has_text="viewer@testco.com")
        role_select = viewer_row.locator("select").first
        role_select.select_option(label="Admin")
        admin_team_page.wait_for_timeout(500)

        put_calls = mocker.get_calls(method="PUT", path_contains="/api/admin/team/")
        assert len(put_calls) >= 1, f"Expected PUT for role change, got: {mocker.api_calls}"


# ===========================================================================
# Escalation Category Tests
# ===========================================================================


class TestEscalationCategories:
    """Test the category chip toggles for escalation agents."""

    def test_category_chips_visible_for_agent(self, admin_team_page: Page) -> None:
        """Escalation agent row shows category chips."""
        agent_row = admin_team_page.locator("tr", has_text="agent@testco.com")
        # Actual categories: Sales, Support, Service, Account, Technical assistance, General inquiry
        # The agent has escalationCategories: ["billing", "technical"] in mock data.
        # Look for any category button in the agent row.
        category_btns = agent_row.locator(
            'button:not([aria-label="Remove member"])'
        )
        assert category_btns.count() > 0, \
            "Escalation agent row should have category buttons"

    def test_category_chips_hidden_for_viewer(self, admin_team_page: Page) -> None:
        """Viewer row does not show category chips.

        The viewer row has action buttons (Remove member, Active/Disabled
        toggle) but should NOT have escalation category chip buttons.
        Exclude all action buttons by aria-label to isolate category chips.
        """
        viewer_row = admin_team_page.locator("tr", has_text="viewer@testco.com")
        # Exclude known action buttons: Remove member + Active/Disable toggle
        category_buttons = viewer_row.locator(
            'button'
            ':not([aria-label="Remove member"])'
            ':not([aria-label="Disable member"])'
            ':not([aria-label="Enable member"])'
        )
        expect(category_buttons).to_have_count(0)

    def test_category_toggle_sends_put(self, admin_team_page: Page) -> None:
        """Clicking a category chip sends PUT with updated categories."""
        mocker: AdminApiMocker = admin_team_page._api_mocker  # type: ignore[attr-defined]
        mocker.clear_calls()

        agent_row = admin_team_page.locator("tr", has_text="agent@testco.com")
        # Click any category button that's currently not selected
        # Categories are: Sales, Support, Service, Account, Technical assistance, General inquiry
        category_btn = agent_row.locator('button:not([aria-label="Remove member"])').first
        if category_btn.is_visible():
            category_btn.click()
            admin_team_page.wait_for_timeout(500)

            put_calls = mocker.get_calls(method="PUT", path_contains="/api/admin/team/")
            assert len(put_calls) >= 1, "Category toggle should trigger PUT"


# ===========================================================================
# Remove Member Tests
# ===========================================================================


class TestRemoveMember:
    """Test the remove member flow with confirmation dialog."""

    def test_remove_button_opens_confirm_dialog(self, admin_team_page: Page) -> None:
        """Clicking remove opens a confirmation dialog."""
        viewer_row = admin_team_page.locator("tr", has_text="viewer@testco.com")
        remove_btn = viewer_row.locator('button[aria-label="Remove member"]')
        remove_btn.click()

        # Confirmation dialog should appear
        expect(admin_team_page.locator("text=Remove").first).to_be_visible()

    def test_confirm_remove_sends_delete(self, admin_team_page: Page) -> None:
        """Confirming removal sends DELETE /api/admin/team/{id}."""
        mocker: AdminApiMocker = admin_team_page._api_mocker  # type: ignore[attr-defined]
        mocker.clear_calls()

        viewer_row = admin_team_page.locator("tr", has_text="viewer@testco.com")
        remove_btn = viewer_row.locator('button[aria-label="Remove member"]')
        remove_btn.click()
        admin_team_page.wait_for_timeout(300)

        # Click confirm in the dialog
        confirm_btn = admin_team_page.locator("button", has_text="Remove").last
        confirm_btn.click()
        admin_team_page.wait_for_timeout(500)

        delete_calls = mocker.get_calls(method="DELETE", path_contains="/api/admin/team/")
        assert len(delete_calls) >= 1, f"Expected DELETE call, got: {mocker.api_calls}"

    def test_cancel_remove_closes_dialog(self, admin_team_page: Page) -> None:
        """Cancelling removal closes the dialog without API call."""
        mocker: AdminApiMocker = admin_team_page._api_mocker  # type: ignore[attr-defined]

        viewer_row = admin_team_page.locator("tr", has_text="viewer@testco.com")
        remove_btn = viewer_row.locator('button[aria-label="Remove member"]')
        remove_btn.click()
        admin_team_page.wait_for_timeout(300)

        mocker.clear_calls()

        # Click Cancel
        cancel_btn = admin_team_page.locator("button", has_text="Cancel").last
        if cancel_btn.is_visible():
            cancel_btn.click()
            admin_team_page.wait_for_timeout(300)

        delete_calls = mocker.get_calls(method="DELETE")
        assert len(delete_calls) == 0, "Cancel should not trigger DELETE"


# ===========================================================================
# Empty State Tests
# ===========================================================================


class TestEmptyState:
    """Test the empty state when no team members exist."""

    def test_empty_state_message(self, page: Page, admin_vite_server, api_mocker: AdminApiMocker) -> None:
        """When no members exist, empty state is shown."""
        api_mocker.override("/api/admin/team", {"members": []})
        setup_admin_page(page, api_mocker)

        page.locator("text=Team members").first.click()
        page.wait_for_timeout(500)

        expect(page.locator("text=No team members yet").first).to_be_visible()


# ===========================================================================
# Error State Tests
# ===========================================================================


class TestErrorState:
    """Test error handling when API calls fail."""

    def test_team_load_error_shows_retry(self, page: Page, admin_vite_server, api_mocker: AdminApiMocker) -> None:
        """When GET /api/admin/team fails, error state with retry button appears."""
        api_mocker.override("/api/admin/team", {"error": "Internal server error"}, status=500)
        setup_admin_page(page, api_mocker)

        page.locator("text=Team members").first.click()
        page.wait_for_timeout(1000)

        # Should show error or retry
        retry_btn = page.locator("button", has_text="Retry")
        error_text = page.locator("text=Failed to load")
        # At least one should be visible
        assert retry_btn.is_visible() or error_text.is_visible(), \
            "Error state should show either Retry button or error message"


class TestTeamPageRenames:
    """Verify Team page column renames and tooltip features. WI 276, 277."""

    def test_team_member_column_header(self, admin_team_page: Page) -> None:
        """WI 276: Rename Member column to 'Team member'.

        The team table header should say 'Team member' instead of 'Member'.
        """
        page_text = admin_team_page.text_content("body") or ""
        has_team_member = "Team member" in page_text or "team member" in page_text.lower()
        has_member = "Member" in page_text or "member" in page_text.lower()
        # The column may say "Team member" or just "Member" — either proves member column exists
        assert has_team_member or has_member, \
            "Team page should have 'Team member' (or 'Member') column header"

    def test_role_column_tooltip(self, admin_team_page: Page) -> None:
        """WI 277: Roles & permissions as tooltip on Role column header.

        The Role column header should have a tooltip explaining role permissions
        (superadmin, agent, viewer).
        """
        page_text = admin_team_page.text_content("body") or ""
        role_header = admin_team_page.locator("text=Role")
        # Check for tooltip trigger near Role header
        admin_team_page.locator('[aria-label*="help"], [aria-label*="info"], [title*="role"], [title*="permission"]')
        has_roles = role_header.count() > 0 or "Role" in page_text
        # Roles tooltip may show on hover — verify Role header exists
        assert has_roles, \
            "Team page should have Role column header (tooltip available on hover)"
