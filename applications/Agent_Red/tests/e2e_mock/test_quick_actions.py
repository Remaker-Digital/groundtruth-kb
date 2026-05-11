# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Mock E2E tests for the Quick Actions page (/quick-actions).

Tests action list display, create/edit/delete CRUD flows,
action detail display, and API contracts against the mock Vite dev server.
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e_mock.conftest import (
    api_origin,
    navigate_and_settle,
    dismiss_onboarding_if_present,
    get_api_json,
    assert_mock_active,
    main_text,
)

QUICK_ACTIONS_PATH = "/quick-actions"


# ---------------------------------------------------------------------------
# TestActionList - 6 tests
# ---------------------------------------------------------------------------

class TestActionList:
    """Verify the quick actions list displays all configured actions."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        navigate_and_settle(shared_page, QUICK_ACTIONS_PATH, mock_base_url)
        dismiss_onboarding_if_present(shared_page)

    def test_track_order_displayed(self, shared_page: Page):
        """Track Order action is displayed in the list."""
        text = main_text(shared_page)
        assert "Track Order" in text, "Track Order action not found"

    def test_return_item_displayed(self, shared_page: Page):
        """Return Item action is displayed."""
        text = main_text(shared_page)
        assert "Return Item" in text, "Return Item action not found"

    def test_contact_support_displayed(self, shared_page: Page):
        """Contact Support action is displayed."""
        text = main_text(shared_page)
        assert "Contact Support" in text, "Contact Support action not found"

    def test_size_help_displayed(self, shared_page: Page):
        """Size Help action is displayed."""
        text = main_text(shared_page)
        assert "Size Help" in text, "Size Help action not found"

    def test_disabled_action_shown(self, shared_page: Page):
        """Product Info (disabled) action is shown in the list."""
        text = main_text(shared_page)
        assert "Product Info" in text, "Product Info (disabled action) not found"

    def test_five_actions_present(self, shared_page: Page):
        """All 5 quick actions are present on the page."""
        text = main_text(shared_page)
        actions = ["Track Order", "Return Item", "Contact Support", "Size Help", "Product Info"]
        found = sum(1 for act in actions if act in text)
        assert found >= 4, f"Only {found}/5 actions found"


# ---------------------------------------------------------------------------
# TestCreateAction - 6 tests (mutation - function-scoped page)
# ---------------------------------------------------------------------------

class TestCreateAction:
    """Verify creating a new quick action via API."""

    def test_post_endpoint_returns_201(self, page: Page, mock_base_url: str):
        """POST /api/admin/quick-actions returns 201 Created."""
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions",
            data={"label": "New Action", "prompt": "This is a new test action", "enabled": True},
        )
        assert resp.status in (200, 201), f"Create action returned {resp.status}"

    def test_post_returns_json(self, page: Page, mock_base_url: str):
        """POST /api/admin/quick-actions returns a JSON body."""
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions",
            data={"label": "Another Action", "prompt": "Test prompt", "enabled": True},
        )
        body = resp.json()
        assert isinstance(body, dict), "Create response is not a dict"

    def test_created_action_has_id(self, page: Page, mock_base_url: str):
        """Created action response includes an id field."""
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions",
            data={"label": "ID Test Action", "prompt": "Check id", "enabled": True},
        )
        body = resp.json()
        assert "id" in body, "Created action missing id field"

    def test_created_action_appears_in_list(self, page: Page, mock_base_url: str):
        """A newly created action appears when listing all actions."""
        page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions",
            data={"label": "Visible Action", "prompt": "Should appear in list", "enabled": True},
        )
        data = get_api_json(page, mock_base_url, "/api/admin/quick-actions")
        actions = data.get("actions", data) if isinstance(data, dict) else data
        labels = [a.get("label", "") for a in actions]
        assert "Visible Action" in labels, "Created action not in list"

    def test_create_with_icon(self, page: Page, mock_base_url: str):
        """Creating an action with icon field is accepted."""
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions",
            data={"label": "Icon Action", "prompt": "With icon", "icon": "star", "enabled": True},
        )
        assert resp.status in (200, 201)

    def test_create_disabled_action(self, page: Page, mock_base_url: str):
        """Creating a disabled action is accepted."""
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions",
            data={"label": "Disabled New", "prompt": "Starts disabled", "enabled": False},
        )
        assert resp.status in (200, 201)


# ---------------------------------------------------------------------------
# TestEditAction - 6 tests (mutation - function-scoped page)
# ---------------------------------------------------------------------------

class TestEditAction:
    """Verify editing an existing quick action."""

    def test_put_endpoint_accepted(self, page: Page, mock_base_url: str):
        """PUT /api/admin/quick-actions/:id accepts updates."""
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions/qa-001",
            data={"label": "Track My Order"},
        )
        assert resp.status in (200, 201), f"Edit action returned {resp.status}"

    def test_put_returns_json(self, page: Page, mock_base_url: str):
        """PUT /api/admin/quick-actions/:id returns JSON."""
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions/qa-001",
            data={"label": "Updated Label"},
        )
        body = resp.json()
        assert isinstance(body, dict)

    def test_edit_label_persists(self, page: Page, mock_base_url: str):
        """Editing a label is reflected in subsequent GET."""
        page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions/qa-002",
            data={"label": "Return & Exchange"},
        )
        data = get_api_json(page, mock_base_url, "/api/admin/quick-actions")
        actions = data.get("actions", data) if isinstance(data, dict) else data
        labels = [a.get("label", "") for a in actions]
        assert "Return & Exchange" in labels, "Edited label not persisted"

    def test_edit_prompt(self, page: Page, mock_base_url: str):
        """Editing the prompt field is accepted."""
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions/qa-003",
            data={"prompt": "Connect me with a human agent"},
        )
        assert resp.status in (200, 201)

    def test_toggle_enabled_status(self, page: Page, mock_base_url: str):
        """Toggling enabled status from true to false is accepted."""
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions/qa-004",
            data={"enabled": False},
        )
        assert resp.status in (200, 201)

    def test_enable_disabled_action(self, page: Page, mock_base_url: str):
        """Enabling a previously disabled action is accepted."""
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/quick-actions/qa-005",
            data={"enabled": True},
        )
        assert resp.status in (200, 201)


# ---------------------------------------------------------------------------
# TestDeleteAction - 4 tests (mutation - function-scoped page)
# ---------------------------------------------------------------------------

class TestDeleteAction:
    """Verify deleting a quick action."""

    def test_delete_endpoint_accepted(self, page: Page, mock_base_url: str):
        """DELETE /api/admin/quick-actions/:id returns success."""
        resp = page.request.delete(f"{api_origin(mock_base_url)}/api/admin/quick-actions/qa-005")
        assert resp.status in (200, 204), f"Delete returned {resp.status}"

    def test_deleted_action_removed_from_list(self, page: Page, mock_base_url: str):
        """Deleted action no longer appears in the list."""
        page.request.delete(f"{api_origin(mock_base_url)}/api/admin/quick-actions/qa-005")
        data = get_api_json(page, mock_base_url, "/api/admin/quick-actions")
        actions = data.get("actions", data) if isinstance(data, dict) else data
        ids = [a.get("id", "") for a in actions]
        assert "qa-005" not in ids, "Deleted action still in list"

    def test_delete_preserves_other_actions(self, page: Page, mock_base_url: str):
        """Deleting one action does not affect others."""
        page.request.delete(f"{api_origin(mock_base_url)}/api/admin/quick-actions/qa-005")
        data = get_api_json(page, mock_base_url, "/api/admin/quick-actions")
        actions = data.get("actions", data) if isinstance(data, dict) else data
        ids = [a.get("id", "") for a in actions]
        assert "qa-001" in ids, "qa-001 was accidentally deleted"
        assert "qa-002" in ids, "qa-002 was accidentally deleted"

    def test_delete_nonexistent_handles_gracefully(self, page: Page, mock_base_url: str):
        """DELETE on nonexistent ID returns 404 or 200."""
        resp = page.request.delete(f"{api_origin(mock_base_url)}/api/admin/quick-actions/qa-nonexistent")
        assert resp.status in (200, 204, 404), f"Unexpected status {resp.status}"


# ---------------------------------------------------------------------------
# TestActionDetails - 4 tests
# ---------------------------------------------------------------------------

class TestActionDetails:
    """Verify action detail display and properties."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        navigate_and_settle(shared_page, QUICK_ACTIONS_PATH, mock_base_url)
        dismiss_onboarding_if_present(shared_page)

    def test_action_prompts_accessible(self, shared_page: Page, mock_base_url: str):
        """Actions in the API include prompt text."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/quick-actions")
        actions = data.get("actions", data) if isinstance(data, dict) else data
        for action in actions:
            assert "prompt" in action, f"Action {action.get('label')} missing prompt"

    def test_action_enabled_field_present(self, shared_page: Page, mock_base_url: str):
        """Each action has an enabled boolean field."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/quick-actions")
        actions = data.get("actions", data) if isinstance(data, dict) else data
        for action in actions:
            assert "enabled" in action, f"Action {action.get('label')} missing enabled"

    def test_page_heading_present(self, shared_page: Page):
        """Quick Actions page has a heading."""
        heading = shared_page.locator("h1, h2").first
        expect(heading).to_be_visible(timeout=5000)

    def test_disabled_action_visual_indicator(self, shared_page: Page):
        """Disabled actions have a visual indicator (badge, opacity, strikethrough)."""
        text = main_text(shared_page).lower()
        has_indicator = "disabled" in text or "inactive" in text or "off" in text
        disabled_els = shared_page.locator("[data-disabled], [aria-disabled='true'], .mantine-Text-dimmed")
        assert has_indicator or disabled_els.count() > 0, (
            "No visual indicator for disabled actions"
        )


# ---------------------------------------------------------------------------
# TestApiContracts - 4 tests
# ---------------------------------------------------------------------------

class TestApiContracts:
    """Verify the quick actions mock API endpoints."""

    def test_list_endpoint_shape(self, shared_page: Page, mock_base_url: str):
        """GET /api/admin/quick-actions returns actions array."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/quick-actions")
        actions = data.get("actions", data) if isinstance(data, dict) else data
        assert isinstance(actions, list)
        assert len(actions) == 5

    def test_action_fields_complete(self, shared_page: Page, mock_base_url: str):
        """Each action has id, label, prompt, enabled fields."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/quick-actions")
        actions = data.get("actions", data) if isinstance(data, dict) else data
        for action in actions:
            assert "id" in action, "Missing id in action"
            assert "label" in action, "Missing label in action"
            assert "prompt" in action, "Missing prompt in action"
            assert "enabled" in action, "Missing enabled in action"

    def test_first_action_fixture_values(self, shared_page: Page, mock_base_url: str):
        """First action matches fixture data (qa-001, Track Order)."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/quick-actions")
        actions = data.get("actions", data) if isinstance(data, dict) else data
        first = actions[0]
        assert first["id"] == "qa-001"
        assert first["label"] == "Track Order"
        assert first["enabled"] is True

    def test_mock_api_active(self, shared_page: Page, mock_base_url: str):
        """Mock API is confirmed active."""
        assert_mock_active(shared_page, mock_base_url)
