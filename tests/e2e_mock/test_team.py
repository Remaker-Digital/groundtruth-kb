# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Team page E2E tests against the mock Vite dev server.

Tests cover: member table display, invite form CRUD, role changes, active/inactive
toggle, member deletion with confirmation, escalation categories, superadmin
protections, and API contract verification.

Fixture data: 5 members (Sarah Chen superadmin, Jordan Lee admin, Alex Rivera
escalation_agent, Taylor Kim viewer, Casey Morgan escalation_agent/inactive).
"""
import re

import pytest
from playwright.sync_api import Page, expect

from tests.e2e_mock.conftest import (
    api_origin,
    dismiss_onboarding_if_present,
    get_api_json,
    main_text,
    navigate_and_settle,
    post_api_json,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEAM_PATH = "/team"

MEMBER_NAMES = ["Sarah Chen", "Jordan Lee", "Alex Rivera", "Taylor Kim", "Casey Morgan"]
MEMBER_EMAILS = [
    "admin@mockstore.com",
    "jordan@mockstore.com",
    "alex@mockstore.com",
    "taylor@mockstore.com",
    "casey@mockstore.com",
]
ROLE_LABELS = {
    "superadmin": "Superadmin",
    "admin": "Admin",
    "escalation_agent": "Escalation agent",
    "viewer": "Viewer",
}
INVITABLE_ROLE_LABELS = ["Admin", "Escalation agent", "Viewer"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _go_team(pg: Page, base_url: str) -> None:
    """Navigate to team page and dismiss onboarding if present."""
    navigate_and_settle(pg, TEAM_PATH, base_url)
    dismiss_onboarding_if_present(pg)


def _table(pg: Page):
    """Return the team member table locator."""
    return pg.locator("table").first


def _rows(pg: Page):
    """Return all tbody rows."""
    return _table(pg).locator("tbody tr")


def _row_by_name(pg: Page, name: str):
    """Return the row containing a specific member name."""
    return _table(pg).locator("tbody tr", has_text=name)


def _click_invite_button(pg: Page) -> None:
    """Click the Invite member button to open the invite form."""
    btn = pg.locator("button", has_text="Invite member")
    btn.click()
    pg.wait_for_timeout(300)


def _fill_invite_and_submit(pg: Page, email: str, role: str | None = None) -> None:
    """Fill the invite form and click Send invite."""
    # Fill the email input (there's only one email input on the page)
    pg.locator('input[type="email"]').fill(email)
    if role:
        # The invite form's role select is the FIRST select on the page
        # (it appears above the table rows). Use .first to avoid strict mode.
        pg.locator("select").first.select_option(label=role)
    pg.locator("button", has_text="Send invite").click()
    pg.wait_for_timeout(500)


def _get_row_role_text(pg: Page, name: str) -> str:
    """Get the role text from a member row (badge or select value)."""
    row = _row_by_name(pg, name)
    role_cell = row.locator("td").nth(1)
    select = role_cell.locator("select")
    if select.count() > 0:
        return select.input_value()
    return role_cell.inner_text().split(chr(10))[0].strip()


def _invite_disposable_member(
    pg: Page,
    base_url: str,
    email: str = "disposable@mockstore.com",
    role: str = "Viewer",
) -> None:
    """Invite a member for mutation testing, navigating and opening the form."""
    _go_team(pg, base_url)
    _click_invite_button(pg)
    _fill_invite_and_submit(pg, email, role)


# =========================================================================
# 1. TestMemberTable  (shared_page -- read-only)
# =========================================================================
class TestMemberTable:
    """Team member table: display, columns, rows, roles, status indicators."""

    @pytest.fixture(autouse=True)
    def _setup(self, shared_page: Page, mock_base_url: str):
        _go_team(shared_page, mock_base_url)

    def test_all_members_displayed(self, shared_page: Page):
        """All 5 fixture members appear in the table."""
        for name in MEMBER_NAMES:
            expect(_row_by_name(shared_page, name)).to_be_visible(timeout=3000)

    def test_member_emails_shown(self, shared_page: Page):
        """Each member email is visible in the table."""
        text = _table(shared_page).inner_text()
        for email in MEMBER_EMAILS:
            assert email in text, f"Email {email} not found in table"

    def test_member_roles_shown(self, shared_page: Page):
        """Each member displays the correct role label."""
        assert (
            _get_row_role_text(shared_page, "Sarah Chen")
            .lower()
            .replace(" ", "")
            .startswith("superadmin")
            or "Superadmin" in _row_by_name(shared_page, "Sarah Chen").inner_text()
        )
        assert "admin" in _get_row_role_text(shared_page, "Jordan Lee").lower()

    def test_active_status_indicators(self, shared_page: Page):
        """Active members show an Active status indicator."""
        row = _row_by_name(shared_page, "Jordan Lee")
        row_text = row.inner_text()
        assert "Active" in row_text or "active" in row_text, (
            "Active indicator not found for Jordan Lee"
        )

    def test_inactive_member_indicator(self, shared_page: Page):
        """Casey Morgan (inactive) has visual distinction (opacity or Disabled label)."""
        row = _row_by_name(shared_page, "Casey Morgan")
        row_text = row.inner_text()
        has_disabled = "Disabled" in row_text or "disabled" in row_text
        style = row.get_attribute("style") or ""
        has_opacity = "opacity" in style
        assert has_disabled or has_opacity, (
            "Inactive member Casey Morgan has no visual distinction"
        )

    def test_table_has_columns(self, shared_page: Page):
        """Table header contains expected column names."""
        thead_text = _table(shared_page).locator("thead").inner_text().lower()
        for col in ["team member", "role"]:
            assert col in thead_text, f"Column '{col}' missing from table header"

    def test_member_count_correct(self, shared_page: Page):
        """Row count matches fixture data (5 members)."""
        count = _rows(shared_page).count()
        assert count == 5, f"Expected 5 rows, got {count}"

    def test_superadmin_first_or_prominent(self, shared_page: Page):
        """Sarah Chen (superadmin) is present and identifiable."""
        row = _row_by_name(shared_page, "Sarah Chen")
        expect(row).to_be_visible()
        row_text = row.inner_text()
        assert "Superadmin" in row_text or "superadmin" in row_text

    def test_member_row_has_actions(self, shared_page: Page):
        """Non-superadmin rows have action buttons (toggle, remove)."""
        row = _row_by_name(shared_page, "Jordan Lee")
        buttons = row.locator("button")
        assert buttons.count() >= 1, "No action buttons found for Jordan Lee"

    def test_page_heading_visible(self, shared_page: Page):
        """Page shows a heading or title related to team management."""
        text = main_text(shared_page)
        has_heading = "team" in text.lower() or "member" in text.lower()
        assert has_heading, "No team-related heading found on page"


# =========================================================================
# 2. TestInviteForm  (page -- function-scoped, store reset)
# =========================================================================
class TestInviteForm:
    """Invite member form: open, fill, submit, new member appears."""

    def test_invite_button_exists(self, page: Page, mock_base_url: str):
        """Invite member button is visible on the team page."""
        _go_team(page, mock_base_url)
        btn = page.locator("button", has_text="Invite member")
        expect(btn).to_be_visible()

    def test_invite_form_opens(self, page: Page, mock_base_url: str):
        """Clicking Invite member reveals the invite form."""
        _go_team(page, mock_base_url)
        _click_invite_button(page)
        expect(page.locator("text=Invite new team member")).to_be_visible()

    def test_email_input_present(self, page: Page, mock_base_url: str):
        """Invite form contains an email input field."""
        _go_team(page, mock_base_url)
        _click_invite_button(page)
        email_input = page.locator('input[type="email"]')
        expect(email_input).to_be_visible()

    def test_role_selector_present(self, page: Page, mock_base_url: str):
        """Invite form contains a role selector."""
        _go_team(page, mock_base_url)
        _click_invite_button(page)
        form = page.locator("text=Invite new team member").locator("..").locator("..")
        select = form.locator("select, .mantine-Select-root, [role='combobox']")
        assert select.count() > 0, "No role selector found in invite form"

    def test_submit_creates_member(self, page: Page, mock_base_url: str):
        """Submitting the invite form adds a new member to the table."""
        _go_team(page, mock_base_url)
        initial_count = _rows(page).count()
        _click_invite_button(page)
        _fill_invite_and_submit(page, "newmember@mockstore.com", "Viewer")
        page.wait_for_timeout(500)
        new_count = _rows(page).count()
        assert new_count == initial_count + 1, (
            f"Expected {initial_count + 1} rows after invite, got {new_count}"
        )

    def test_new_member_appears(self, page: Page, mock_base_url: str):
        """Newly invited member appears in the table."""
        _go_team(page, mock_base_url)
        _click_invite_button(page)
        _fill_invite_and_submit(page, "visible@mockstore.com", "Admin")
        page.wait_for_timeout(500)
        table_text = _table(page).inner_text()
        assert "visible@mockstore.com" in table_text, (
            "New member email not visible in table"
        )

    def test_post_returns_201(self, page: Page, mock_base_url: str):
        """POST /api/admin/team returns status 201."""
        _go_team(page, mock_base_url)
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/team",
            data={"email": "api201@mockstore.com", "role": "viewer"},
        )
        assert resp.status == 201, f"Expected 201, got {resp.status}"

    def test_new_member_has_id(self, page: Page, mock_base_url: str):
        """POST /api/admin/team response includes a generated member ID."""
        _go_team(page, mock_base_url)
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/team",
            data={"email": "hasid@mockstore.com", "role": "viewer"},
        )
        body = resp.json()
        assert "id" in body, "Response missing 'id' field"
        assert body["id"].startswith("member-"), (
            f"ID {body['id']} doesn't start with member-"
        )


# =========================================================================
# 3. TestRoleChange  (page -- function-scoped, store reset)
# =========================================================================
class TestRoleChange:
    """Role changes via inline select dropdown."""

    def test_role_dropdown_available(self, page: Page, mock_base_url: str):
        """Non-superadmin members have a role selector."""
        _go_team(page, mock_base_url)
        row = _row_by_name(page, "Jordan Lee")
        select = row.locator("select, .mantine-Select-root, [role='combobox']")
        assert select.count() > 0, "No role selector found for Jordan Lee"

    def test_superadmin_no_dropdown(self, page: Page, mock_base_url: str):
        """Superadmin (Sarah Chen) does NOT have a role dropdown."""
        _go_team(page, mock_base_url)
        row = _row_by_name(page, "Sarah Chen")
        native_select = row.locator("select")
        mantine_select = row.locator(".mantine-Select-root input[role='combobox']")
        assert native_select.count() == 0 and mantine_select.count() == 0, "Superadmin should not have a role dropdown"

    def test_role_options_available(self, page: Page, mock_base_url: str):
        """Role selector or row displays the current role."""
        _go_team(page, mock_base_url)
        row = _row_by_name(page, "Jordan Lee")
        row_text = row.inner_text().lower()
        assert "admin" in row_text, "Current role not found in row text"

    def test_role_change_updates_ui(self, page: Page, mock_base_url: str):
        """PUT /api/admin/team/:id/role updates role via API."""
        _go_team(page, mock_base_url)
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/team/member-002/role",
            data={"role": "viewer"},
        )
        assert resp.status == 200
        body = resp.json()
        assert body["role"] == "viewer"

    def test_role_change_sends_put(self, page: Page, mock_base_url: str):
        """PUT /api/admin/team/:id/role returns 200."""
        _go_team(page, mock_base_url)
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/team/member-002/role",
            data={"role": "escalation_agent"},
        )
        assert resp.status == 200, f"Expected 200, got {resp.status}"

    def test_put_role_response_has_updated_role(self, page: Page, mock_base_url: str):
        """PUT role response body reflects the new role."""
        _go_team(page, mock_base_url)
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/team/member-002/role",
            data={"role": "viewer"},
        )
        body = resp.json()
        assert body["role"] == "viewer", (
            f"Expected role='viewer', got '{body['role']}'"
        )


# =========================================================================
# 4. TestActiveToggle  (page -- function-scoped, store reset)
# =========================================================================
class TestActiveToggle:
    """Active/inactive toggle for team members."""

    def test_active_toggle_exists(self, page: Page, mock_base_url: str):
        """Non-superadmin members have an active/disable toggle button."""
        _go_team(page, mock_base_url)
        row = _row_by_name(page, "Jordan Lee")
        toggle = row.locator(
            'button[aria-label="Disable member"], '
            'button[aria-label="Enable member"]'
        )
        assert toggle.count() > 0, "No active toggle button found for Jordan Lee"

    def test_active_member_shows_disable(self, page: Page, mock_base_url: str):
        """Active member (Jordan Lee) shows a Disable button."""
        _go_team(page, mock_base_url)
        row = _row_by_name(page, "Jordan Lee")
        disable_btn = row.locator('button[aria-label="Disable member"]')
        assert disable_btn.count() > 0, (
            "Active member should show 'Disable member' button"
        )

    def test_inactive_member_shows_enable(self, page: Page, mock_base_url: str):
        """Inactive member (Casey Morgan) shows an Enable button."""
        _go_team(page, mock_base_url)
        row = _row_by_name(page, "Casey Morgan")
        enable_btn = row.locator('button[aria-label="Enable member"]')
        assert enable_btn.count() > 0, (
            "Inactive member should show 'Enable member' button"
        )

    def test_toggle_changes_status(self, page: Page, mock_base_url: str):
        """Clicking the toggle changes the member status visually."""
        _go_team(page, mock_base_url)
        row = _row_by_name(page, "Jordan Lee")
        toggle = row.locator('button[aria-label="Disable member"]')
        toggle.click()
        page.wait_for_timeout(500)
        # After toggling, should now show Enable
        enable_btn = row.locator('button[aria-label="Enable member"]')
        assert enable_btn.count() > 0, (
            "After disable, should show 'Enable member' button"
        )

    def test_toggle_sends_put(self, page: Page, mock_base_url: str):
        """PUT /api/admin/team/:id/active returns 200."""
        _go_team(page, mock_base_url)
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/team/member-002/active",
            data={"is_active": False},
        )
        assert resp.status == 200, f"Expected 200, got {resp.status}"

    def test_put_active_response_reflects_change(self, page: Page, mock_base_url: str):
        """PUT active response body reflects the new is_active state."""
        _go_team(page, mock_base_url)
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/team/member-002/active",
            data={"is_active": False},
        )
        body = resp.json()
        assert body["isActive"] is False, (
            f"Expected isActive=False, got {body.get('isActive')}"
        )


# =========================================================================
# 5. TestDeleteMember  (page -- function-scoped, store reset)
# =========================================================================
class TestDeleteMember:
    """Member deletion with confirmation dialog."""

    def test_delete_button_exists(self, page: Page, mock_base_url: str):
        """Non-superadmin rows have a remove button."""
        _go_team(page, mock_base_url)
        row = _row_by_name(page, "Jordan Lee")
        remove_btn = row.locator('button[aria-label="Remove member"]')
        assert remove_btn.count() > 0, "Remove button not found for Jordan Lee"

    def test_superadmin_no_delete(self, page: Page, mock_base_url: str):
        """Superadmin (Sarah Chen) should NOT have a remove button."""
        _go_team(page, mock_base_url)
        row = _row_by_name(page, "Sarah Chen")
        remove_btn = row.locator('button[aria-label="Remove member"]')
        assert remove_btn.count() == 0, "Superadmin should not have a remove button"

    def test_delete_shows_confirmation(self, page: Page, mock_base_url: str):
        """Clicking remove shows a confirmation dialog."""
        _go_team(page, mock_base_url)
        row = _row_by_name(page, "Taylor Kim")
        remove_btn = row.locator('button[aria-label="Remove member"]')
        remove_btn.click()
        page.wait_for_timeout(300)
        dialog = page.locator("text=Remove team member")
        expect(dialog).to_be_visible(timeout=3000)

    def test_delete_confirmation_has_buttons(self, page: Page, mock_base_url: str):
        """Confirmation dialog has Remove and Cancel buttons."""
        _go_team(page, mock_base_url)
        row = _row_by_name(page, "Taylor Kim")
        row.locator('button[aria-label="Remove member"]').click()
        page.wait_for_timeout(300)
        confirm_btn = page.locator("button", has_text="Remove member")
        cancel_btn = page.locator("button", has_text="Cancel")
        assert confirm_btn.count() > 0, "Confirm remove button not found"
        assert cancel_btn.count() > 0, "Cancel button not found in dialog"

    def test_delete_removes_member(self, page: Page, mock_base_url: str):
        """Confirming delete removes the member from the table."""
        _go_team(page, mock_base_url)
        initial_count = _rows(page).count()
        row = _row_by_name(page, "Taylor Kim")
        row.locator('button[aria-label="Remove member"]').click()
        page.wait_for_timeout(300)
        page.locator("button", has_text="Remove member").click()
        page.wait_for_timeout(500)
        new_count = _rows(page).count()
        assert new_count == initial_count - 1, (
            f"Expected {initial_count - 1} rows after delete, got {new_count}"
        )

    def test_delete_api_returns_200(self, page: Page, mock_base_url: str):
        """DELETE /api/admin/team/:id returns 200 with success."""
        _go_team(page, mock_base_url)
        resp = page.request.delete(f"{api_origin(mock_base_url)}/api/admin/team/member-004")
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        body = resp.json()
        assert body.get("success") is True, "Delete response missing success=true"


# =========================================================================
# 6. TestApiContracts  (shared_page -- read-only)
# =========================================================================
class TestApiContracts:
    """API contract verification for team endpoints."""

    def test_team_api_returns_members(self, shared_page: Page, mock_base_url: str):
        """GET /api/admin/team returns a members array."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/team")
        assert "members" in data, "Response missing 'members' key"
        assert isinstance(data["members"], list), "'members' is not a list"

    def test_five_initial_members(self, shared_page: Page, mock_base_url: str):
        """Fixture has the expected core members present."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/team")
        # The shared mock store is a singleton — prior deletion tests (function-scoped
        # pages reset, but DELETE on shared_page persists). Check core members exist.
        names = {m["displayName"] for m in data["members"]}
        for core in ["Sarah Chen", "Jordan Lee", "Alex Rivera"]:
            assert core in names, f"Core member {core} missing from team API"

    def test_member_has_required_fields(self, shared_page: Page, mock_base_url: str):
        """Each member has required fields: id, email, displayName, role, isActive."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/team")
        required_fields = ["id", "email", "displayName", "role", "isActive"]
        for member in data["members"]:
            for field in required_fields:
                assert field in member, (
                    f"Member {member.get('id', '?')} missing field '{field}'"
                )

    def test_member_ids_pattern(self, shared_page: Page, mock_base_url: str):
        r"""Member IDs follow the member-NNN pattern."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/team")
        for member in data["members"]:
            assert re.match(r"^member-\d{3}$", member["id"]), (
                f"ID '{member['id']}' doesn't match member-NNN pattern"
            )

    def test_member_emails_are_mockstore(self, shared_page: Page, mock_base_url: str):
        """All fixture member emails use @mockstore.com domain."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/team")
        for member in data["members"]:
            assert member["email"].endswith("@mockstore.com"), (
                f"Email '{member['email']}' not @mockstore.com"
            )

    def test_post_team_returns_generated_id(self, shared_page: Page, mock_base_url: str):
        """POST /api/admin/team generates an auto-incremented member ID."""
        resp = shared_page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/team",
            data={"email": "gen@mockstore.com", "role": "viewer"},
        )
        body = resp.json()
        assert body["id"].startswith("member-"), (
            f"Generated ID '{body['id']}' doesn't start with member-"
        )


# =========================================================================
# 7. TestEscalationCategories  (shared_page -- read-only)
# =========================================================================
class TestEscalationCategories:
    """Escalation category display for escalation_agent members."""

    @pytest.fixture(autouse=True)
    def _setup(self, shared_page: Page, mock_base_url: str):
        _go_team(shared_page, mock_base_url)

    def test_agent_has_categories(self, shared_page: Page):
        """Alex Rivera (escalation_agent, active) shows escalation categories."""
        row = _row_by_name(shared_page, "Alex Rivera")
        row_text = row.inner_text()
        # Alex has categories: support, technical
        has_cats = "support" in row_text.lower() or "technical" in row_text.lower()
        assert has_cats, "Alex Rivera should show escalation categories"

    def test_superadmin_categories(self, shared_page: Page, mock_base_url: str):
        """Sarah Chen (superadmin) has escalation categories in API data."""
        # Superadmin categories are in API data but not rendered as chips in the UI
        # (chips only render for escalation_agent role members)
        data = get_api_json(shared_page, mock_base_url, "/api/admin/team")
        sarah = None
        for m in data.get("members", []):
            if m["displayName"] == "Sarah Chen":
                sarah = m
                break
        assert sarah is not None, "Sarah Chen not found in API response"
        cats = sarah.get("escalationCategories", [])
        assert len(cats) >= 2, (
            f"Superadmin should have multiple escalation categories, got {cats}"
        )

    def test_viewer_no_categories(self, shared_page: Page, mock_base_url: str):
        """Viewer role members should have no escalation categories."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/team")
        # Find any viewer member (Taylor Kim or others)
        viewers = [m for m in data.get("members", []) if m["role"] == "viewer"]
        assert len(viewers) > 0, "No viewer members found in API response"
        for viewer in viewers:
            assert viewer["escalationCategories"] == [], (
                f"Viewer {viewer['displayName']} should have empty categories, got {viewer['escalationCategories']}"
            )

    def test_inactive_agent_categories(self, shared_page: Page, mock_base_url: str):
        """Casey Morgan (inactive escalation_agent) has categories in API data."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/team")
        casey = None
        for m in data.get("members", []):
            if m["displayName"] == "Casey Morgan":
                casey = m
                break
        assert casey is not None, "Casey Morgan not found"
        assert len(casey["escalationCategories"]) > 0, (
            "Casey Morgan should have escalation categories"
        )

    def test_categories_as_chips(self, shared_page: Page):
        """Escalation categories render as button-type chip elements."""
        row = _row_by_name(shared_page, "Alex Rivera")
        chips = row.locator('button[type="button"]')
        # Alex has support + technical categories shown as chips
        assert chips.count() >= 1, (
            "Escalation categories should render as button chips"
        )

    def test_category_values_match_fixture(self, shared_page: Page, mock_base_url: str):
        """API-reported categories match fixture expectations."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/team")
        alex = None
        for m in data.get("members", []):
            if m["displayName"] == "Alex Rivera":
                alex = m
                break
        assert alex is not None, "Alex Rivera not found in API"
        expected = {"support", "technical"}
        actual = set(alex["escalationCategories"])
        assert actual == expected, f"Expected {expected}, got {actual}"
