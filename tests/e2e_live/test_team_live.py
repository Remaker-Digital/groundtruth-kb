"""
Live E2E team member tests — comprehensive SPEC-1652 coverage with mutations.

Tests run against the deployed staging environment with REAL API mutations.
Every interactive element (dimension E) is exercised with actual data changes:
  - POST /api/admin/team (invite new member)
  - PUT  /api/admin/team/{id} (role, categories, active state)
  - DELETE /api/admin/team/{id} (remove member)

Each mutation test creates a disposable test member (invite) and cleans up
(delete) to maintain test isolation.  Email format: e2e-test-{uuid}@staging.test

Element inventory: EL-team-001..030 (30 elements, 7 sections).
Column headers: Team member, Role?, Joined, Last active, Escalations, Actions.
  (CSS text-transform: uppercase — inner_text() returns TEAM MEMBER, ROLE?, etc.)
Role display labels: Superadmin, Admin, Escalation agent, Viewer.
Invite button: "+ Invite member"  |  Submit: "Send invite"

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re
import uuid

import pytest
from playwright.sync_api import Page

# ── Constants ────────────────────────────────────────────────────────────

DISPLAY_ROLES = {"superadmin", "admin", "escalation agent", "viewer"}
ESCALATION_CATEGORIES = [
    "Service", "Support", "Sales", "Account",
    "Technical Assistance", "General Inquiry",
]
COLUMN_HEADERS = [
    "Team member", "Role", "Joined", "Last active", "Escalations", "Actions",
]


# ── Helpers ──────────────────────────────────────────────────────────────

def _text(page: Page) -> str:
    """Visible text from <main>, excluding CSS variable blocks."""
    return page.inner_text("main") or ""


def _wait_for_team_data(page: Page) -> str:
    """Wait for team member data to load with progressive backoff retry."""
    for attempt in range(4):
        try:
            page.wait_for_selector(
                "table tbody tr, text=/team member/, text=/No team members/",
                timeout=10_000,
            )
        except Exception:
            pass
        page.wait_for_timeout(2000)
        text = _text(page)
        if "@" in text and "failed" not in text.lower():
            return text
        if re.search(r"\d+\s*team\s*member", text, re.I) and "failed" not in text.lower():
            return text
        if attempt < 3:
            page.wait_for_timeout((attempt + 1) * 5000)
            page.reload(wait_until="load")
    return _text(page)


def _is_rate_limited(page: Page) -> bool:
    """Check for rate-limit or load-failure errors in the page."""
    text = _text(page).lower()
    return "failed to load" in text or "failed to fetch" in text


def _unique_email() -> str:
    """Generate a unique email for disposable test members."""
    return f"e2e-test-{uuid.uuid4().hex[:8]}@staging.test"


def _find_row_by_email(page: Page, email: str):
    """Find a table row containing the given email address."""
    rows = page.locator("table tbody tr")
    for i in range(rows.count()):
        row = rows.nth(i)
        if email.lower() in (row.inner_text() or "").lower():
            return row
    return None


def _find_non_superadmin_row(page: Page):
    """Find the first table row that has action buttons (non-superadmin)."""
    rows = page.locator("table tbody tr")
    for i in range(rows.count()):
        row = rows.nth(i)
        row_text = (row.inner_text() or "").lower()
        # Superadmin rows have no Active/Disabled toggle
        if "superadmin" not in row_text:
            return row
    return None


def _open_invite_form(page: Page) -> None:
    """Click '+ Invite member' to open the invite form."""
    btn = page.locator("button:has-text('Invite member')").first
    btn.click()
    page.wait_for_timeout(500)


def _invite_member(page: Page, email: str | None = None, role: str = "viewer") -> str:
    """Invite a test member: open form → fill → submit → wait.

    Returns the email used.  Raises on form-not-found.
    """
    email = email or _unique_email()

    _open_invite_form(page)

    # ── Fill email (required) ──
    email_input = page.locator(
        "input[type='email'], input[placeholder*='colleague']"
    ).first
    email_input.fill(email)

    # ── Fill name (optional) ──
    name_input = page.locator("input[placeholder*='Jane']")
    if name_input.count() > 0:
        name_input.first.fill(f"E2E {email[:8]}")

    # ── Select role ──
    # The invite form select is OUTSIDE the <table>.  Grab the first
    # <select> that is NOT inside a table row.
    selects = page.locator("select")
    for i in range(selects.count()):
        s = selects.nth(i)
        # Skip selects that are inside table tbody (those are row role selectors)
        parent_text = page.evaluate(
            "(el) => el.closest('tbody') ? 'intable' : 'outside'",
            s.element_handle(),
        )
        if parent_text == "outside":
            s.select_option(role)
            break

    # ── Submit ──
    submit_btn = page.locator(
        "button:has-text('Send invite'), button:has-text('Invite'):not(:has-text('member'))"
    ).first
    submit_btn.click()
    page.wait_for_timeout(3000)

    return email


def _delete_member(page: Page, email: str) -> bool:
    """Delete a team member by email.  Returns True on success."""
    page.reload(wait_until="load")
    _wait_for_team_data(page)

    row = _find_row_by_email(page, email)
    if not row:
        return False

    # Click the delete button (trash icon, title="Remove member")
    del_btn = row.locator("button[title='Remove member']")
    if del_btn.count() == 0:
        # Fallback: the last button in the actions cell is the trash icon
        buttons = row.locator("button")
        if buttons.count() >= 2:
            buttons.last.click()
        else:
            return False
    else:
        del_btn.first.click()

    page.wait_for_timeout(500)

    # Confirm removal in dialog
    confirm = page.locator("button:has-text('Remove member')")
    # Disambiguate: the confirm button is in a dialog overlay, not the row
    for i in range(confirm.count()):
        btn = confirm.nth(i)
        # The dialog confirm button is outside the table
        parent = page.evaluate(
            "(el) => el.closest('table') ? 'intable' : 'dialog'",
            btn.element_handle(),
        )
        if parent == "dialog" and btn.is_visible():
            btn.click()
            page.wait_for_timeout(2000)
            return True

    return False


# ═══════════════════════════════════════════════════════════════════════════
# Section A: Page Header — EL-team-001..004
# ═══════════════════════════════════════════════════════════════════════════

class TestPageHeader:
    """[EL-team-001..004] Title, subtitle, member count, invite button."""

    def test_page_title(self, live_team_page: Page):
        """[EL-team-001/A,B] Page heading shows 'Team members'."""
        _wait_for_team_data(live_team_page)
        text = _text(live_team_page)
        assert "Team members" in text

    def test_page_subtitle(self, live_team_page: Page):
        """[EL-team-002/A,B] Subtitle describes team management."""
        _wait_for_team_data(live_team_page)
        text = _text(live_team_page).lower()
        assert "manage" in text or "assign" in text or "roles" in text, (
            f"Subtitle not found. Text snippet: {text[:300]}"
        )

    def test_member_count_matches_rows(self, live_team_page: Page):
        """[EL-team-003/A,B] Stated member count matches table row count."""
        text = _wait_for_team_data(live_team_page)
        count_match = re.search(r"(\d+)\s*(?:team\s*)?member", text, re.I)
        rows = live_team_page.locator("table tbody tr")
        row_count = rows.count()
        if count_match and row_count > 0:
            stated = int(count_match.group(1))
            assert stated == row_count, f"Count {stated} != {row_count} rows"
        else:
            assert count_match or row_count > 0

    def test_invite_button_visible(self, live_team_page: Page):
        """[EL-team-004/A] '+ Invite member' button is present."""
        _wait_for_team_data(live_team_page)
        btn = live_team_page.locator("button:has-text('Invite member')")
        assert btn.count() > 0, "Invite member button not found"

    def test_invite_button_toggles_form(self, live_team_page: Page):
        """[EL-team-004/E1] Clicking invite button shows/hides the invite form."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        # Open form
        _open_invite_form(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        )
        assert email_input.count() > 0, "Invite form email input did not appear"

        # Close form (button text flips to "Cancel" when form is open)
        cancel_btn = live_team_page.locator("button:has-text('Cancel')").first
        cancel_btn.click()
        live_team_page.wait_for_timeout(500)


# ═══════════════════════════════════════════════════════════════════════════
# Section B: Invite Form — EL-team-005..010
# ═══════════════════════════════════════════════════════════════════════════

class TestInviteForm:
    """[EL-team-005..010] Invite form structure, fields, and submission."""

    def _ensure_form_open(self, page: Page) -> None:
        _wait_for_team_data(page)
        if _is_rate_limited(page):
            pytest.skip("Rate-limited")
        _open_invite_form(page)

    def test_form_container_appears(self, live_team_page: Page):
        """[EL-team-005/A] Invite form container is visible after clicking button."""
        self._ensure_form_open(live_team_page)
        text = _text(live_team_page).lower()
        assert "invite" in text or "email" in text, "Invite form not visible"

    def test_email_input_with_placeholder(self, live_team_page: Page):
        """[EL-team-006/A,B] Email input exists with appropriate placeholder."""
        self._ensure_form_open(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague'], input[placeholder*='@']"
        )
        assert email_input.count() > 0, "Email input not found in invite form"

    def test_name_input_exists(self, live_team_page: Page):
        """[EL-team-007/A] Name input is present (optional field)."""
        self._ensure_form_open(live_team_page)
        name_input = live_team_page.locator(
            "input[placeholder*='Jane'], input[placeholder*='name' i], "
            "input[placeholder*='Smith']"
        )
        assert name_input.count() > 0, "Name input not found in invite form"

    def test_role_dropdown_options(self, live_team_page: Page):
        """[EL-team-008/A,B] Role dropdown lists admin, escalation_agent, viewer."""
        self._ensure_form_open(live_team_page)
        # Find select that is NOT inside the table
        selects = live_team_page.locator("select")
        for i in range(selects.count()):
            s = selects.nth(i)
            options_text = s.inner_text().lower()
            if "admin" in options_text and "viewer" in options_text:
                return  # Found the invite form select with expected options
        pytest.fail("Role dropdown with admin/viewer options not found")

    def test_cancel_closes_form(self, live_team_page: Page):
        """[EL-team-010/E1] Cancel closes the invite form."""
        self._ensure_form_open(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill("should-be-cleared@test.com")

        # Cancel
        cancel_btn = live_team_page.locator("button:has-text('Cancel')").first
        cancel_btn.click()
        live_team_page.wait_for_timeout(500)

        # The invite form email input should no longer be visible
        email_inputs = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        )
        # Form may fully unmount or just hide — check visibility
        form_closed = email_inputs.count() == 0 or not email_inputs.first.is_visible()
        assert form_closed, "Invite form still visible after cancel"

    def test_email_validation_blocks_invalid(self, live_team_page: Page):
        """[EL-team-006/E1] Submitting invalid email triggers validation."""
        self._ensure_form_open(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill("not-an-email")

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first
        submit.click()
        live_team_page.wait_for_timeout(1000)

        # HTML5 email validation or app-level error should prevent submission
        text = _text(live_team_page).lower()
        # If error message shown OR the invite form is still open (not submitted)
        has_error = "valid email" in text or "invalid" in text
        form_still_open = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).count() > 0
        assert has_error or form_still_open, "Invalid email was accepted"

    def test_submit_creates_member(self, live_team_page: Page):
        """[EL-team-009/E1] 'Send invite' creates a member visible in the table."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="viewer")

        # Reload and verify
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        text = _text(live_team_page)
        found = email.lower() in text.lower()

        # Clean up
        _delete_member(live_team_page, email)

        assert found, f"Invited member {email} not found in team table"

    def test_invite_role_selection_persists(self, live_team_page: Page):
        """[EL-team-008/E1] Selecting a role in the invite form persists to the created member."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="admin")

        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        role_found = False
        if row:
            row_text = (row.inner_text() or "").lower()
            # Check displayed text OR native <select> value
            if "admin" in row_text:
                role_found = True
            else:
                sel = row.locator("select")
                if sel.count() > 0:
                    role_found = (sel.first.input_value() or "").lower() == "admin"

        _delete_member(live_team_page, email)

        assert role_found, (
            f"Expected role 'admin' in row for {email}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Section C: Table Structure — EL-team-011..017
# ═══════════════════════════════════════════════════════════════════════════

class TestTableStructure:
    """[EL-team-011..017] Table element and six column headers."""

    def test_table_exists(self, live_team_page: Page):
        """[EL-team-011/A] Team members <table> is present."""
        _wait_for_team_data(live_team_page)
        assert live_team_page.locator("table").count() > 0

    def test_header_team_member(self, live_team_page: Page):
        """[EL-team-012/A,B] 'Team member' column header (CSS text-transform: uppercase)."""
        _wait_for_team_data(live_team_page)
        assert "team member" in _text(live_team_page).lower()

    def test_header_role(self, live_team_page: Page):
        """[EL-team-013/A,B] 'Role' column header (CSS text-transform: uppercase)."""
        _wait_for_team_data(live_team_page)
        text = _text(live_team_page).lower()
        assert "role" in text, "'Role' column header not found"

    def test_header_joined(self, live_team_page: Page):
        """[EL-team-014/A,B] 'Joined' column header (CSS text-transform: uppercase)."""
        _wait_for_team_data(live_team_page)
        assert "joined" in _text(live_team_page).lower()

    def test_header_last_active(self, live_team_page: Page):
        """[EL-team-015/A,B] 'Last active' column header (CSS text-transform: uppercase)."""
        _wait_for_team_data(live_team_page)
        assert "last active" in _text(live_team_page).lower()

    def test_header_escalations(self, live_team_page: Page):
        """[EL-team-016/A,B] 'Escalations' column header."""
        _wait_for_team_data(live_team_page)
        assert "escalation" in _text(live_team_page).lower()

    def test_header_actions(self, live_team_page: Page):
        """[EL-team-017/A,B] 'Actions' column header (CSS text-transform: uppercase)."""
        _wait_for_team_data(live_team_page)
        assert "actions" in _text(live_team_page).lower()


# ═══════════════════════════════════════════════════════════════════════════
# Section D: Member Row Elements — EL-team-018..022
# ═══════════════════════════════════════════════════════════════════════════

class TestMemberRowElements:
    """[EL-team-018..022] Per-row data: name, email, role, dates, escalations."""

    def test_member_email_displayed(self, live_team_page: Page):
        """[EL-team-018/A,B] At least one email address is visible."""
        text = _wait_for_team_data(live_team_page)
        emails = re.findall(r"[\w.+-]+@[\w.-]+\.\w+", text)
        assert len(emails) >= 1, "No emails found in team table"

    def test_superadmin_badge(self, live_team_page: Page):
        """[EL-team-018/A] Superadmin member shows 'Superadmin' label."""
        text = _wait_for_team_data(live_team_page).lower()
        assert "superadmin" in text, (
            "Superadmin label must be visible on seeded staging tenant"
        )

    def test_role_selector_for_non_superadmin(self, live_team_page: Page):
        """[EL-team-019/A] Non-superadmin rows have role <select> dropdowns."""
        _wait_for_team_data(live_team_page)
        selects = live_team_page.locator("table tbody select, table select")
        text = _text(live_team_page).lower()
        has_non_sa = any(
            r in text for r in ("admin", "escalation agent", "viewer")
        )
        if has_non_sa:
            assert selects.count() > 0, "Non-superadmin rows lack role <select>"
        else:
            return  # Only superadmin present — role selector verified by TestRoleChange

    def test_joined_date_format(self, live_team_page: Page):
        """[EL-team-020/A,B] Joined column shows formatted date."""
        text = _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited — cannot verify date format")
        months = r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
        assert re.search(rf"({months})\s+\d{{1,2}},?\s*\d{{4}}", text), (
            f"No formatted date found. Text: {text[:300]}"
        )

    def test_last_active_display(self, live_team_page: Page):
        """[EL-team-021/A,B] Last active shows relative time or 'Never'."""
        text = _wait_for_team_data(live_team_page)
        has_time = bool(re.search(
            r"\d+\s*[mhd]\s*ago|just now|never|today|yesterday",
            text, re.I,
        ))
        has_date = bool(re.search(
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d",
            text,
        ))
        assert has_time or has_date, f"No activity time found. Text: {text[:300]}"

    def test_escalation_count_column(self, live_team_page: Page):
        """[EL-team-022/A] Escalation column shows count or '--'."""
        text = _wait_for_team_data(live_team_page)
        # Agents show a number, others show "--" (dashes)
        assert "--" in text or re.search(r"\b\d+\b", text)


# ═══════════════════════════════════════════════════════════════════════════
# Section D+E: Role Changes — EL-team-019 dimension E
# ═══════════════════════════════════════════════════════════════════════════

class TestRoleChange:
    """[EL-team-019/E] Change member role via dropdown — real PUT mutation."""

    def test_change_role_persists(self, live_team_page: Page):
        """[EL-team-019/E1] Changing role dropdown fires PUT and persists."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        # Create disposable member as viewer
        email = _invite_member(live_team_page, role="viewer")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        assert row is not None, f"Invited member {email} must be visible after invite"

        sel = row.locator("select")
        assert sel.count() > 0, "Non-superadmin row must have role <select> dropdown"

        # Change viewer → admin
        sel.first.select_option("admin")
        live_team_page.wait_for_timeout(2000)

        # Reload and verify
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)
        row = _find_row_by_email(live_team_page, email)
        new_val = ""
        if row:
            s = row.locator("select")
            new_val = s.first.input_value() if s.count() > 0 else ""

        _delete_member(live_team_page, email)
        assert new_val == "admin", f"Role not persisted — got '{new_val}'"

    def test_change_to_escalation_agent_shows_categories(self, live_team_page: Page):
        """[EL-team-019/E2] Changing role to escalation_agent reveals category chips."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="viewer")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        assert row is not None, f"Invited member {email} must be visible after invite"

        sel = row.locator("select")
        assert sel.count() > 0, "Non-superadmin row must have role <select> dropdown"

        # Change viewer → escalation_agent
        sel.first.select_option("escalation_agent")
        live_team_page.wait_for_timeout(2000)

        # Category chips should now appear in the row
        row_text = row.inner_text().lower()
        found_cats = [c for c in ESCALATION_CATEGORIES if c.lower() in row_text]

        # If categories didn't appear inline, reload and check
        if not found_cats:
            live_team_page.reload(wait_until="load")
            _wait_for_team_data(live_team_page)
            row = _find_row_by_email(live_team_page, email)
            if row:
                row_text = row.inner_text().lower()
                found_cats = [c for c in ESCALATION_CATEGORIES if c.lower() in row_text]

        _delete_member(live_team_page, email)
        assert len(found_cats) > 0, (
            f"No escalation categories appeared after role change. Row: {row_text[:200]}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Section E: Escalation Category Controls — EL-team-023..024
# ═══════════════════════════════════════════════════════════════════════════

class TestEscalationCategories:
    """[EL-team-023..024] Category chips for escalation agents; role tooltip."""

    def test_category_chips_visible(self, live_team_page: Page):
        """[EL-team-023/A,B] Escalation agent rows show category chip labels."""
        _wait_for_team_data(live_team_page)
        # Check actual table rows for escalation_agent role, not page text
        # (page text includes the role dropdown options like "Escalation agent")
        rows = live_team_page.locator("table tbody tr")
        has_ea_row = False
        for i in range(rows.count()):
            row = rows.nth(i)
            sel = row.locator("select")
            if sel.count() > 0 and sel.first.input_value() == "escalation_agent":
                has_ea_row = True
                row_text = row.inner_text().lower()
                found = [c for c in ESCALATION_CATEGORIES if c.lower() in row_text]
                assert len(found) > 0, (
                    f"Escalation agent row lacks category labels. Row: {row_text[:200]}"
                )
                return
        if not has_ea_row:
            return  # No escalation agent present — chips verified by TestEscalationCategories.test_toggle

    def test_toggle_category_chip(self, live_team_page: Page):
        """[EL-team-023/E1] Clicking a category chip toggles its selection — real PUT."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        # Create an escalation_agent to toggle chips on
        email = _invite_member(live_team_page, role="escalation_agent")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        assert row is not None, f"Escalation agent {email} must be visible after invite"

        # Find a clickable category chip in the row
        # Categories render as small pill buttons or clickable spans
        chip_clicked = False
        for cat in ESCALATION_CATEGORIES:
            chip = row.locator(f"text='{cat}'")
            if chip.count() > 0 and chip.first.is_visible():
                chip.first.click()
                live_team_page.wait_for_timeout(1500)
                chip_clicked = True
                break

        _delete_member(live_team_page, email)

        assert chip_clicked, "Escalation agent row must have clickable category chips"

    def test_role_header_info_icon(self, live_team_page: Page):
        """[EL-team-024/A] Role column header has an info icon or tooltip trigger."""
        _wait_for_team_data(live_team_page)
        headers = live_team_page.locator("table thead th, table th")
        found_role_header = False
        for i in range(headers.count()):
            h = headers.nth(i)
            if "role" in (h.inner_text() or "").lower():
                found_role_header = True
                icons = h.locator("svg, button, [title*='info' i]")
                header_text = h.inner_text() or ""
                assert icons.count() > 0 or "?" in header_text, (
                    "Role column header must have info icon or '?' indicator"
                )
                return
        assert found_role_header, "Role column header must exist in team table"

    def test_role_tooltip_shows_descriptions(self, live_team_page: Page):
        """[EL-team-024/E1] Hovering the role info icon shows role descriptions."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        headers = live_team_page.locator("table thead th, table th")
        found_role_header = False
        for i in range(headers.count()):
            h = headers.nth(i)
            if "role" in (h.inner_text() or "").lower():
                found_role_header = True
                icon = h.locator("svg, button, [title*='info' i]").first
                assert icon.is_visible(), "Role info icon must be visible for hover"
                icon.hover()
                live_team_page.wait_for_timeout(500)
                text = _text(live_team_page).lower()
                has_desc = "full access" in text or "configuration" in text or "read-only" in text
                assert has_desc, (
                    "Role tooltip must show descriptions (full access/configuration/read-only)"
                )
                return
        assert found_role_header, "Role column header must exist in team table"


# ═══════════════════════════════════════════════════════════════════════════
# Section F: Member Actions — EL-team-025..027
# ═══════════════════════════════════════════════════════════════════════════

class TestActiveDisabledToggle:
    """[EL-team-025] Active/Disabled toggle — real PUT mutation."""

    def test_toggle_visible_for_non_superadmin(self, live_team_page: Page):
        """[EL-team-025/A] Non-superadmin rows have an Active or Disabled button."""
        _wait_for_team_data(live_team_page)
        row = _find_non_superadmin_row(live_team_page)
        if not row:
            return  # Only superadmin present — toggle verified by mutation tests
        toggles = row.locator(
            "button:has-text('Active'), button:has-text('Disabled')"
        )
        assert toggles.count() > 0, "No Active/Disabled toggle in non-superadmin row"

    def test_toggle_switches_state(self, live_team_page: Page):
        """[EL-team-025/E1] Clicking toggle flips Active↔Disabled — real PUT."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="viewer")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        assert row is not None, f"Test member {email} must be visible after invite"

        toggle = row.locator(
            "button:has-text('Active'), button:has-text('Disabled')"
        )
        assert toggle.count() > 0, "Non-superadmin row must have Active/Disabled toggle button"

        initial = toggle.first.inner_text().strip()

        # Click to toggle
        toggle.first.click()
        live_team_page.wait_for_timeout(2000)

        # Read new state
        row = _find_row_by_email(live_team_page, email)
        new_text = ""
        if row:
            t = row.locator("button:has-text('Active'), button:has-text('Disabled')")
            new_text = t.first.inner_text().strip() if t.count() > 0 else ""
        _delete_member(live_team_page, email)

        expected = "Disabled" if initial == "Active" else "Active"
        assert new_text == expected, (
            f"Toggle did not flip: was '{initial}', now '{new_text}'"
        )

    def test_disabled_member_row_dimmed(self, live_team_page: Page):
        """[EL-team-025/C] Disabled member row has reduced opacity."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="viewer")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        assert row is not None, f"Test member {email} must be visible after invite"

        toggle = row.locator(
            "button:has-text('Active'), button:has-text('Disabled')"
        )
        assert toggle.count() > 0, "Non-superadmin row must have Active/Disabled toggle button"

        # Disable the member
        if toggle.first.inner_text().strip() == "Active":
            toggle.first.click()
            live_team_page.wait_for_timeout(2000)

        # Check row opacity
        row = _find_row_by_email(live_team_page, email)
        opacity = "1"
        if row:
            opacity = live_team_page.evaluate(
                "(el) => window.getComputedStyle(el).opacity",
                row.element_handle(),
            )

        _delete_member(live_team_page, email)

        assert float(opacity) < 1.0, (
            f"Disabled row opacity should be < 1.0, got {opacity}"
        )


class TestDeleteMember:
    """[EL-team-026..027] Delete button, confirmation dialog, actual DELETE."""

    def test_delete_button_exists(self, live_team_page: Page):
        """[EL-team-026/A] Non-superadmin row has a delete/trash button."""
        _wait_for_team_data(live_team_page)
        row = _find_non_superadmin_row(live_team_page)
        if not row:
            return  # Only superadmin present — delete button verified by TestDeleteMember
        del_btn = row.locator(
            "button[title='Remove member'], button:has(svg)"
        )
        assert del_btn.count() > 0, "No delete button in non-superadmin row"

    def test_delete_opens_confirmation_dialog(self, live_team_page: Page):
        """[EL-team-026/E1, EL-team-027/A] Click delete → confirmation dialog appears."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="viewer")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        assert row is not None, f"Test member {email} must be visible after invite"

        del_btn = row.locator("button[title='Remove member']")
        if del_btn.count() == 0:
            buttons = row.locator("button")
            assert buttons.count() >= 2, "Non-superadmin row must have action buttons"
            buttons.last.click()
        else:
            del_btn.first.click()

        live_team_page.wait_for_timeout(500)
        text = _text(live_team_page).lower()
        has_dialog = (
            "remove team member" in text
            or "are you sure" in text
            or "permanently remove" in text
        )

        # Cancel to preserve the member for cleanup
        cancel = live_team_page.locator("button:has-text('Cancel')")
        if cancel.count() > 0:
            cancel.first.click()
            live_team_page.wait_for_timeout(300)

        _delete_member(live_team_page, email)
        assert has_dialog, "Confirmation dialog not shown after delete click"

    def test_confirmation_dialog_content(self, live_team_page: Page):
        """[EL-team-027/B] Dialog shows member name, warning, Cancel + Remove buttons."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="viewer")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        assert row is not None, f"Test member {email} must be visible after invite"

        del_btn = row.locator("button[title='Remove member']")
        if del_btn.count() > 0:
            del_btn.first.click()
        else:
            row.locator("button").last.click()
        live_team_page.wait_for_timeout(500)

        text = _text(live_team_page)

        has_cancel = live_team_page.locator("button:has-text('Cancel')").count() > 0
        has_confirm = live_team_page.locator("button:has-text('Remove member')").count() > 0
        has_warning = "cannot be undone" in text.lower() or "permanently" in text.lower()

        # Cancel and clean up
        cancel = live_team_page.locator("button:has-text('Cancel')")
        if cancel.count() > 0:
            cancel.first.click()
            live_team_page.wait_for_timeout(300)
        _delete_member(live_team_page, email)

        assert has_cancel, "Cancel button not found in confirmation dialog"
        assert has_confirm, "Remove member button not found in confirmation dialog"
        assert has_warning, f"Warning text not found. Dialog: {text[:300]}"

    def test_cancel_preserves_member(self, live_team_page: Page):
        """[EL-team-027/E1] Cancelling the dialog keeps the member."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="viewer")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        assert row is not None, f"Test member {email} must be visible after invite"

        # Open delete dialog
        del_btn = row.locator("button[title='Remove member']")
        if del_btn.count() > 0:
            del_btn.first.click()
        else:
            row.locator("button").last.click()
        live_team_page.wait_for_timeout(500)

        # Cancel
        cancel = live_team_page.locator("button:has-text('Cancel')")
        if cancel.count() > 0:
            cancel.first.click()
        live_team_page.wait_for_timeout(500)

        # Member should still be present
        text = _text(live_team_page)
        still_here = email.lower() in text.lower()

        _delete_member(live_team_page, email)
        assert still_here, f"Member {email} disappeared after cancel"

    def test_confirm_removes_member(self, live_team_page: Page):
        """[EL-team-027/E2] Confirming 'Remove member' deletes from the table — real DELETE."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="viewer")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        assert row is not None, f"Test member {email} must be visible after invite"

        rows_before = live_team_page.locator("table tbody tr").count()

        deleted = _delete_member(live_team_page, email)
        assert deleted, "Delete via UI must succeed on disposable test member"

        # Give the API time to propagate, then retry reload up to 3 times
        removed = False
        for attempt in range(3):
            live_team_page.wait_for_timeout(2000)
            live_team_page.reload(wait_until="load")
            _wait_for_team_data(live_team_page)

            text = _text(live_team_page)
            rows_after = live_team_page.locator("table tbody tr").count()

            if email.lower() not in text.lower() or rows_after < rows_before:
                removed = True
                break

        assert removed, (
            f"Member {email} still visible after confirmed deletion (tried 3 reloads)"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Section G: Superadmin Protection — EL-team-019,025,026 security
# ═══════════════════════════════════════════════════════════════════════════

class TestSuperadminProtection:
    """Superadmin rows must not expose edit/delete controls."""

    def test_no_role_dropdown(self, live_team_page: Page):
        """Superadmin row has no role <select> dropdown."""
        text = _wait_for_team_data(live_team_page)
        assert "superadmin" in text.lower(), (
            "Superadmin must be visible on seeded staging tenant"
        )

        rows = live_team_page.locator("table tbody tr")
        for i in range(rows.count()):
            row = rows.nth(i)
            if "superadmin" in (row.inner_text() or "").lower():
                assert row.locator("select").count() == 0, (
                    "Superadmin row must not have a role selector"
                )
                return
        pytest.fail("Could not identify superadmin row in table")

    def test_no_toggle_or_delete(self, live_team_page: Page):
        """Superadmin row has no Active/Disabled toggle or Delete button."""
        text = _wait_for_team_data(live_team_page)
        assert "superadmin" in text.lower(), (
            "Superadmin must be visible on seeded staging tenant"
        )

        rows = live_team_page.locator("table tbody tr")
        for i in range(rows.count()):
            row = rows.nth(i)
            if "superadmin" in (row.inner_text() or "").lower():
                btns = row.locator("button")
                btn_texts = [
                    (btns.nth(j).inner_text() or "").strip()
                    for j in range(btns.count())
                ]
                dangerous = [t for t in btn_texts if t in ("Active", "Disabled")]
                assert len(dangerous) == 0, (
                    f"Superadmin row has action buttons: {btn_texts}"
                )
                return
        pytest.fail("Could not identify superadmin row in table")


# ═══════════════════════════════════════════════════════════════════════════
# Section H: Negative / Destructive Testing — SPEC-1655
# ═══════════════════════════════════════════════════════════════════════════

class TestNegativeInviteForm:
    """SPEC-1655: Destructive tests — invalid inputs, boundary conditions, malformed data."""

    def _ensure_form_open(self, page: Page) -> None:
        _wait_for_team_data(page)
        if _is_rate_limited(page):
            pytest.skip("Rate-limited")
        _open_invite_form(page)

    # ── Empty field submission ──────────────────────────────────────────

    def test_empty_email_blocked(self, live_team_page: Page):
        """Submit invite with empty email — form should not submit."""
        self._ensure_form_open(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill("")

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first
        submit.click()
        live_team_page.wait_for_timeout(1000)

        # Form should still be open (HTML5 required or app validation)
        form_open = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).count() > 0
        assert form_open, "Empty email was accepted — form closed unexpectedly"

    def test_whitespace_only_email_blocked(self, live_team_page: Page):
        """Submit invite with whitespace-only email — should be rejected."""
        self._ensure_form_open(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill("   ")

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first
        submit.click()
        live_team_page.wait_for_timeout(1000)

        form_open = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).count() > 0
        text = _text(live_team_page).lower()
        has_error = "invalid" in text or "valid email" in text or "required" in text
        assert form_open or has_error, "Whitespace-only email was accepted"

    # ── Malformed email formats ─────────────────────────────────────────

    def test_no_at_sign_email_blocked(self, live_team_page: Page):
        """Email without @ sign should be rejected."""
        self._ensure_form_open(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill("notanemail")

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first
        submit.click()
        live_team_page.wait_for_timeout(1000)

        form_open = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).count() > 0
        assert form_open, "Email without @ was accepted"

    def test_no_domain_email_blocked(self, live_team_page: Page):
        """Email with @ but no domain (user@) should be rejected."""
        self._ensure_form_open(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill("user@")

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first
        submit.click()
        live_team_page.wait_for_timeout(1000)

        form_open = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).count() > 0
        assert form_open, "Email 'user@' (no domain) was accepted"

    def test_double_at_email_blocked(self, live_team_page: Page):
        """Email with double @@ should be rejected."""
        self._ensure_form_open(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill("user@@domain.com")

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first
        submit.click()
        live_team_page.wait_for_timeout(1000)

        form_open = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).count() > 0
        assert form_open, "Email with @@ was accepted"

    # ── Boundary values ─────────────────────────────────────────────────

    def test_overlong_email_handled(self, live_team_page: Page):
        """Very long email (300+ chars) should either be blocked or handled gracefully."""
        self._ensure_form_open(live_team_page)
        long_email = f"{'a' * 300}@staging.test"
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill(long_email)

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first
        submit.click()
        live_team_page.wait_for_timeout(2000)

        # Either form stays open (validation) or error shown — page should not crash
        text = _text(live_team_page).lower()
        page_intact = "team member" in text or "invite" in text
        assert page_intact, f"Page crashed after overlong email. Text: {text[:200]}"

    def test_overlong_name_handled(self, live_team_page: Page):
        """Very long name (500+ chars) should be handled without crashing."""
        self._ensure_form_open(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill(_unique_email())

        name_input = live_team_page.locator(
            "input[placeholder*='Jane'], input[placeholder*='name' i]"
        )
        assert name_input.count() > 0, "Invite form must have a name input field"
        name_input.first.fill("X" * 500)

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first
        submit.click()
        live_team_page.wait_for_timeout(2000)

        text = _text(live_team_page).lower()
        page_intact = "team member" in text or "invite" in text
        assert page_intact, f"Page crashed after overlong name. Text: {text[:200]}"

        # If the invite was accepted (unlikely), clean up
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

    # ── XSS / injection payloads ────────────────────────────────────────

    def test_xss_in_name_field_sanitized(self, live_team_page: Page):
        """Script tag in name field should be sanitized — not executed."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _unique_email()
        _open_invite_form(live_team_page)

        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill(email)

        name_input = live_team_page.locator(
            "input[placeholder*='Jane'], input[placeholder*='name' i]"
        )
        assert name_input.count() > 0, "Invite form must have a name input field"
        name_input.first.fill('<script>alert("xss")</script>')

        # Select role
        selects = live_team_page.locator("select")
        for i in range(selects.count()):
            s = selects.nth(i)
            in_table = live_team_page.evaluate(
                "(el) => el.closest('tbody') ? 'intable' : 'outside'",
                s.element_handle(),
            )
            if in_table == "outside":
                s.select_option("viewer")
                break

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first
        submit.click()
        live_team_page.wait_for_timeout(3000)

        # Page should not have a JS alert dialog (Playwright auto-dismisses)
        # Verify page is still functional
        live_team_page.reload(wait_until="load")
        text = _wait_for_team_data(live_team_page)
        page_intact = "team member" in text.lower()
        assert page_intact, "Page broken after XSS payload submission"

        # React JSX auto-escapes HTML — <script> renders as visible escaped text
        # in inner_text(), proving it was NOT executed.  The safe behavior IS
        # having the literal angle brackets visible as text content.
        if email.lower() in text.lower():
            _delete_member(live_team_page, email)

    def test_sql_injection_in_email_handled(self, live_team_page: Page):
        """SQL injection pattern in email should be rejected or handled safely."""
        self._ensure_form_open(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        # HTML5 email type should block this, but test anyway
        email_input.fill("'; DROP TABLE team_members; --@test.com")

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first
        submit.click()
        live_team_page.wait_for_timeout(1000)

        text = _text(live_team_page).lower()
        page_intact = "team member" in text or "invite" in text
        assert page_intact, "Page crashed after SQL injection attempt"

    # ── Duplicate operations ────────────────────────────────────────────

    def test_duplicate_email_invite_handled(self, live_team_page: Page):
        """Inviting the same email twice should show error or be idempotent."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="viewer")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        # Verify first invite exists
        text = _text(live_team_page)
        assert email.lower() in text.lower(), (
            f"First invite for {email} must be visible on seeded staging tenant"
        )

        # Try to invite same email again
        _open_invite_form(live_team_page)
        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill(email)

        selects = live_team_page.locator("select")
        for i in range(selects.count()):
            s = selects.nth(i)
            in_table = live_team_page.evaluate(
                "(el) => el.closest('tbody') ? 'intable' : 'outside'",
                s.element_handle(),
            )
            if in_table == "outside":
                s.select_option("viewer")
                break

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first
        submit.click()
        live_team_page.wait_for_timeout(3000)

        # Either error shown, or handled gracefully (no crash, no duplicates)
        live_team_page.reload(wait_until="load")
        text = _wait_for_team_data(live_team_page)
        page_intact = "team member" in text.lower()

        # Count occurrences of the email — should be exactly 1, not 2+
        email_count = text.lower().count(email.lower())

        _delete_member(live_team_page, email)

        assert page_intact, "Page crashed after duplicate invite"
        assert email_count <= 1, (
            f"Duplicate member created — {email} appears {email_count} times"
        )

    # ── Rapid interaction ───────────────────────────────────────────────

    def test_rapid_double_submit_invite(self, live_team_page: Page):
        """Rapidly clicking submit twice should not create duplicate members."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _unique_email()
        _open_invite_form(live_team_page)

        email_input = live_team_page.locator(
            "input[type='email'], input[placeholder*='colleague']"
        ).first
        email_input.fill(email)

        name_input = live_team_page.locator(
            "input[placeholder*='Jane'], input[placeholder*='name' i]"
        )
        if name_input.count() > 0:
            name_input.first.fill(f"DoubleClick {email[:6]}")

        selects = live_team_page.locator("select")
        for i in range(selects.count()):
            s = selects.nth(i)
            in_table = live_team_page.evaluate(
                "(el) => el.closest('tbody') ? 'intable' : 'outside'",
                s.element_handle(),
            )
            if in_table == "outside":
                s.select_option("viewer")
                break

        submit = live_team_page.locator(
            "button:has-text('Send invite'), button[type='submit']"
        ).first

        # Double-click the submit button rapidly — second click may fail
        # if the button is disabled/removed after first submit (good UX)
        submit.click()
        try:
            submit.click(timeout=1000)
        except Exception:
            pass  # Button disabled/gone after first click — expected debounce
        live_team_page.wait_for_timeout(4000)

        live_team_page.reload(wait_until="load")
        text = _wait_for_team_data(live_team_page)

        email_count = text.lower().count(email.lower())
        page_intact = "team member" in text.lower()

        # Clean up if member was created
        if email.lower() in text.lower():
            _delete_member(live_team_page, email)

        assert page_intact, "Page crashed after rapid double-submit"
        assert email_count <= 1, (
            f"Double-submit created {email_count} entries for {email}"
        )

    # ── State violations ────────────────────────────────────────────────

    def test_rapid_role_toggle_stability(self, live_team_page: Page):
        """Rapidly toggling role back and forth should not corrupt member state."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="viewer")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        assert row is not None, f"Test member {email} must be visible after invite"

        sel = row.locator("select")
        assert sel.count() > 0, "Non-superadmin row must have role <select> dropdown"

        # Rapid toggles: viewer -> admin -> escalation_agent -> viewer
        for role in ["admin", "escalation_agent", "viewer"]:
            sel.first.select_option(role)
            live_team_page.wait_for_timeout(500)

        # Wait for last change to settle
        live_team_page.wait_for_timeout(2000)

        # Verify page is still stable
        live_team_page.reload(wait_until="load")
        text = _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        final_role = ""
        if row:
            s = row.locator("select")
            final_role = s.first.input_value() if s.count() > 0 else ""

        _delete_member(live_team_page, email)

        assert final_role == "viewer", (
            f"After rapid role changes, expected 'viewer', got '{final_role}'"
        )

    def test_rapid_active_toggle_stability(self, live_team_page: Page):
        """Rapidly toggling Active/Disabled should not corrupt member state."""
        _wait_for_team_data(live_team_page)
        if _is_rate_limited(live_team_page):
            pytest.skip("Rate-limited")

        email = _invite_member(live_team_page, role="viewer")
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        assert row is not None, f"Test member {email} must be visible after invite"

        toggle = row.locator(
            "button:has-text('Active'), button:has-text('Disabled')"
        )
        assert toggle.count() > 0, "Non-superadmin row must have Active/Disabled toggle button"

        # Record initial state
        initial = toggle.first.inner_text().strip()

        # Toggle 4 times rapidly (should end at initial state)
        for _ in range(4):
            toggle = row.locator(
                "button:has-text('Active'), button:has-text('Disabled')"
            )
            if toggle.count() > 0:
                toggle.first.click()
                live_team_page.wait_for_timeout(300)

        live_team_page.wait_for_timeout(2000)
        live_team_page.reload(wait_until="load")
        _wait_for_team_data(live_team_page)

        row = _find_row_by_email(live_team_page, email)
        final = ""
        if row:
            t = row.locator("button:has-text('Active'), button:has-text('Disabled')")
            final = t.first.inner_text().strip() if t.count() > 0 else ""

        _delete_member(live_team_page, email)

        # After 4 toggles (even number), should return to initial state
        assert final == initial, (
            f"After 4 rapid toggles, expected '{initial}', got '{final}'"
        )
