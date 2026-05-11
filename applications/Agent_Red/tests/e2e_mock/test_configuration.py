# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
E2E mock tests for the Configuration page.

Tests configuration CRUD lifecycle against the mock Vite dev server:
draft config fields, edit flow, named configs, widget appearances,
version history, draft actions (activate/discard/restore), widget key
rotation, and API contract shapes.

SPEC-1706 mock-based testing -- zero-backend UI development.
"""

from playwright.sync_api import Page

from tests.e2e_mock.conftest import (
    api_origin,
    get_api_json,
    main_text,
    navigate_and_settle,
    dismiss_onboarding_if_present,
)


CONFIG_PATH = "/configuration"

DRAFT_FIELDS = {
    "brand_name": "Mock Store",
    "agent_name": "Agent Red",
    "agent_role": "Customer service assistant",
    "greeting_message": "Hi there! How can I help you today?",
    "escalation_message": "Let me connect you with a human agent.",
    "widget_primary_color": "#ff3621",
    "widget_launcher_color": "#ff3621",
    "widget_position": "bottom-right",
    "widget_launcher_size": 56,
    "widget_launcher_icon": "chat",
    "widget_border_radius": 12,
    "widget_header_text": "Chat with us",
    "widget_subtitle": "We typically reply within minutes",
    "widget_placeholder": "Type your message...",
    "tone": "friendly",
    "response_length": "medium",
    "language": "en",
    "max_turns": 20,
    "escalation_threshold": 3,
    "rate_limit_rpm": 500,
}


# -- Helpers -------------------------------------------------------------------


def _nav(page: Page, mock_base_url: str) -> str:
    """Navigate to configuration page and return visible text."""
    navigate_and_settle(page, CONFIG_PATH, mock_base_url)
    dismiss_onboarding_if_present(page)
    page.wait_for_timeout(500)
    return main_text(page)


def _api_put_config(page: Page, mock_base_url: str, fields: dict) -> dict:
    """PUT /api/config with given fields and return JSON response."""
    resp = page.request.put(
        f"{api_origin(mock_base_url)}/api/config",
        data={"fields": fields},
    )
    assert resp.status == 200, f"PUT /api/config returned {resp.status}"
    return resp.json()


def _api_post(page: Page, mock_base_url: str, path: str, data: dict = None) -> dict:
    """POST helper that returns parsed JSON."""
    resp = page.request.post(f"{api_origin(mock_base_url)}{path}", data=data or {})
    assert resp.status == 200, f"POST {path} returned {resp.status}"
    return resp.json()


def _api_delete(page: Page, mock_base_url: str, path: str) -> dict:
    """DELETE helper that returns parsed JSON."""
    resp = page.request.delete(f"{api_origin(mock_base_url)}{path}")
    assert resp.status == 200, f"DELETE {path} returned {resp.status}"
    return resp.json()


# ==========================================================================
# 1. TestDraftConfig -- read-only inspection of draft config state (10 tests)
# ==========================================================================


class TestDraftConfig:
    """Read-only tests verifying draft config fields render correctly."""

    def test_config_page_loads(self, shared_page: Page, mock_base_url: str):
        """Configuration page loads without errors."""
        text = _nav(shared_page, mock_base_url)
        assert "configuration" in text.lower() or "config" in text.lower() or "brand" in text.lower()

    def test_brand_name_visible(self, shared_page: Page, mock_base_url: str):
        """Brand name Mock Store appears in config form."""
        _nav(shared_page, mock_base_url)
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        assert data["config"]["brand_name"] == "Mock Store"

    def test_agent_name_field(self, shared_page: Page, mock_base_url: str):
        """Agent name Agent Red present in config response."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        assert data["config"]["agent_name"] == "Agent Red"

    def test_greeting_message_field(self, shared_page: Page, mock_base_url: str):
        """Greeting message present in draft config."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        assert "How can I help" in data["config"]["greeting_message"]

    def test_tone_friendly(self, shared_page: Page, mock_base_url: str):
        """Draft config tone is friendly."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        assert data["config"]["tone"] == "friendly"

    def test_language_en(self, shared_page: Page, mock_base_url: str):
        """Draft config language is en."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        assert data["config"]["language"] == "en"

    def test_response_length_medium(self, shared_page: Page, mock_base_url: str):
        """Draft config response_length is medium."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        assert data["config"]["response_length"] == "medium"

    def test_widget_primary_color(self, shared_page: Page, mock_base_url: str):
        """Widget primary color is #ff3621 (brand red)."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        assert data["config"]["widget_primary_color"] == "#ff3621"

    def test_widget_launcher_color(self, shared_page: Page, mock_base_url: str):
        """Widget launcher color is #ff3621 (separate from primary)."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        assert data["config"]["widget_launcher_color"] == "#ff3621"

    def test_draft_version_is_4(self, shared_page: Page, mock_base_url: str):
        """GET /api/config returns version 4 as the current draft version."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        assert data["version"] == 4


# ==========================================================================
# 2. TestConfigEdit -- mutation tests for PUT /api/config (8 tests)
# ==========================================================================


class TestConfigEdit:
    """Mutation tests for editing draft config via PUT /api/config."""

    def test_edit_brand_name(self, page: Page, mock_base_url: str):
        """PUT /api/config with brand_name updates the draft."""
        result = _api_put_config(page, mock_base_url, {"brand_name": "New Store Name"})
        assert result["success"] is True
        data = get_api_json(page, mock_base_url, "/api/config")
        assert data["config"]["brand_name"] == "New Store Name"

    def test_edit_returns_changes(self, page: Page, mock_base_url: str):
        """PUT response includes a changes array with field details."""
        result = _api_put_config(page, mock_base_url, {"agent_name": "New Agent"})
        assert "changes" in result
        assert len(result["changes"]) == 1
        assert result["changes"][0]["field"] == "agent_name"
        assert result["changes"][0]["after"] == "New Agent"

    def test_edit_bumps_version(self, page: Page, mock_base_url: str):
        """PUT /api/config increments draft version from 4 to 5."""
        result = _api_put_config(page, mock_base_url, {"tone": "professional"})
        assert result["version"] == 5

    def test_edit_sets_pending_changes(self, page: Page, mock_base_url: str):
        """After edit, activation status shows has_pending_changes = true."""
        _api_put_config(page, mock_base_url, {"language": "es"})
        status = get_api_json(page, mock_base_url, "/api/config/activation-status")
        assert status["has_pending_changes"] is True

    def test_edit_updates_draft_version_in_status(self, page: Page, mock_base_url: str):
        """After edit, activation status draft_version matches new version."""
        result = _api_put_config(page, mock_base_url, {"max_turns": 30})
        status = get_api_json(page, mock_base_url, "/api/config/activation-status")
        assert status["draft_version"] == result["version"]

    def test_edit_multiple_fields(self, page: Page, mock_base_url: str):
        """PUT with multiple fields updates all of them."""
        fields = {"brand_name": "Multi Edit", "tone": "formal", "language": "fr"}
        result = _api_put_config(page, mock_base_url, fields)
        assert result["success"] is True
        data = get_api_json(page, mock_base_url, "/api/config")
        assert data["config"]["brand_name"] == "Multi Edit"
        assert data["config"]["tone"] == "formal"
        assert data["config"]["language"] == "fr"

    def test_edit_preserves_unmodified_fields(self, page: Page, mock_base_url: str):
        """PUT only modifies specified fields; others remain unchanged."""
        _api_put_config(page, mock_base_url, {"brand_name": "Changed"})
        data = get_api_json(page, mock_base_url, "/api/config")
        assert data["config"]["brand_name"] == "Changed"
        assert data["config"]["agent_name"] == "Agent Red"
        assert data["config"]["tone"] == "friendly"

    def test_edit_returns_success_message(self, page: Page, mock_base_url: str):
        """PUT response includes a message string."""
        result = _api_put_config(page, mock_base_url, {"brand_name": "Msg Test"})
        assert "message" in result
        assert isinstance(result["message"], str)


# ==========================================================================
# 3. TestNamedConfigs -- named config CRUD (8 tests)
# ==========================================================================


class TestNamedConfigs:
    """Tests for named config listing, creation, activation, and deletion."""

    def test_two_named_configs_exist(self, shared_page: Page, mock_base_url: str):
        """GET /api/config/named returns 2 named configs."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/named")
        assert data["total"] == 2
        assert len(data["configs"]) == 2

    def test_default_config_present(self, shared_page: Page, mock_base_url: str):
        """Named config Default exists with isDefault=true."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/named")
        names = {c["name"]: c for c in data["configs"]}
        assert "Default" in names
        assert names["Default"]["isDefault"] is True

    def test_holiday_mode_present(self, shared_page: Page, mock_base_url: str):
        """Named config Holiday Mode exists and is inactive."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/named")
        names = {c["name"]: c for c in data["configs"]}
        assert "Holiday Mode" in names
        assert names["Holiday Mode"]["isActive"] is False

    def test_default_config_is_active(self, shared_page: Page, mock_base_url: str):
        """Default named config has isActive=true."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/named")
        names = {c["name"]: c for c in data["configs"]}
        assert names["Default"]["isActive"] is True

    def test_save_new_named_config(self, page: Page, mock_base_url: str):
        """POST /api/config/named creates a new named config."""
        result = _api_post(page, mock_base_url, "/api/config/named", {"name": "Weekend Mode"})
        assert result["success"] is True
        data = get_api_json(page, mock_base_url, "/api/config/named")
        names = [c["name"] for c in data["configs"]]
        assert "Weekend Mode" in names
        assert data["total"] == 3

    def test_activate_named_config(self, page: Page, mock_base_url: str):
        """POST /api/config/named/:name/activate switches active config."""
        result = _api_post(page, mock_base_url, "/api/config/named/Holiday%20Mode/activate")
        assert result["success"] is True
        data = get_api_json(page, mock_base_url, "/api/config/named")
        active = {c["name"]: c["isActive"] for c in data["configs"]}
        assert active["Holiday Mode"] is True
        assert active["Default"] is False

    def test_delete_named_config(self, page: Page, mock_base_url: str):
        """DELETE /api/config/named/:name removes the config."""
        result = _api_delete(page, mock_base_url, "/api/config/named/Holiday%20Mode")
        assert result["success"] is True
        data = get_api_json(page, mock_base_url, "/api/config/named")
        names = [c["name"] for c in data["configs"]]
        assert "Holiday Mode" not in names
        assert data["total"] == 1

    def test_save_existing_named_bumps_version(self, page: Page, mock_base_url: str):
        """POST /api/config/named with existing name increments version."""
        result = _api_post(page, mock_base_url, "/api/config/named", {"name": "Default"})
        assert result["success"] is True
        data = get_api_json(page, mock_base_url, "/api/config/named")
        default_cfg = next(c for c in data["configs"] if c["name"] == "Default")
        assert default_cfg["version"] == 4


# ==========================================================================
# 4. TestWidgetAppearances -- widget appearance CRUD (6 tests)
# ==========================================================================


class TestWidgetAppearances:
    """Tests for widget appearance listing, creation, activation, deletion."""

    def test_one_appearance_exists(self, shared_page: Page, mock_base_url: str):
        """GET /api/config/widget-appearances returns 1 appearance."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/widget-appearances")
        assert len(data["configs"]) == 1

    def test_default_look_present(self, shared_page: Page, mock_base_url: str):
        """Default Look appearance exists and is active."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/widget-appearances")
        assert data["configs"][0]["name"] == "Default Look"
        assert data["configs"][0]["isActive"] is True

    def test_default_look_is_default(self, shared_page: Page, mock_base_url: str):
        """Default Look has isDefault=true."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/widget-appearances")
        assert data["configs"][0]["isDefault"] is True

    def test_save_widget_appearance(self, page: Page, mock_base_url: str):
        """POST /api/config/widget-appearances creates a new appearance."""
        result = _api_post(page, mock_base_url, "/api/config/widget-appearances", {"name": "Dark Theme"})
        assert result["success"] is True
        data = get_api_json(page, mock_base_url, "/api/config/widget-appearances")
        names = [c["name"] for c in data["configs"]]
        assert "Dark Theme" in names
        assert len(data["configs"]) == 2

    def test_activate_widget_appearance(self, page: Page, mock_base_url: str):
        """POST .../widget-appearances/:name/activate switches active appearance."""
        _api_post(page, mock_base_url, "/api/config/widget-appearances", {"name": "Festive"})
        result = _api_post(page, mock_base_url, "/api/config/widget-appearances/Festive/activate")
        assert result["success"] is True
        data = get_api_json(page, mock_base_url, "/api/config/widget-appearances")
        active = {c["name"]: c["isActive"] for c in data["configs"]}
        assert active["Festive"] is True
        assert active["Default Look"] is False

    def test_delete_widget_appearance(self, page: Page, mock_base_url: str):
        """DELETE .../widget-appearances/:name removes the appearance."""
        _api_post(page, mock_base_url, "/api/config/widget-appearances", {"name": "Temp"})
        data_before = get_api_json(page, mock_base_url, "/api/config/widget-appearances")
        count_before = len(data_before["configs"])
        result = _api_delete(page, mock_base_url, "/api/config/widget-appearances/Temp")
        assert result["success"] is True
        data_after = get_api_json(page, mock_base_url, "/api/config/widget-appearances")
        assert len(data_after["configs"]) == count_before - 1


# ==========================================================================
# 5. TestVersionHistory -- version listing (6 tests)
# ==========================================================================


class TestVersionHistory:
    """Tests for config version history listing."""

    def test_two_versions_exist(self, shared_page: Page, mock_base_url: str):
        """GET /api/config/versions returns 2 versions."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/versions")
        assert len(data["versions"]) == 2

    def test_version_4_present(self, shared_page: Page, mock_base_url: str):
        """Version 4 (latest draft) exists in history."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/versions")
        version_numbers = [v["version"] for v in data["versions"]]
        assert 4 in version_numbers

    def test_version_3_present(self, shared_page: Page, mock_base_url: str):
        """Version 3 (active) exists in history."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/versions")
        version_numbers = [v["version"] for v in data["versions"]]
        assert 3 in version_numbers

    def test_versions_have_timestamps(self, shared_page: Page, mock_base_url: str):
        """Each version has a createdAt ISO timestamp."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/versions")
        for v in data["versions"]:
            assert "createdAt" in v
            assert "T" in v["createdAt"]

    def test_versions_have_actors(self, shared_page: Page, mock_base_url: str):
        """Each version has an actor email."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/versions")
        for v in data["versions"]:
            assert v["actor"] == "admin@mockstore.com"

    def test_versions_have_change_counts(self, shared_page: Page, mock_base_url: str):
        """Each version has a changeCount integer."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/versions")
        for v in data["versions"]:
            assert isinstance(v["changeCount"], int)
            assert v["changeCount"] > 0


# ==========================================================================
# 6. TestDraftActions -- activate, discard, restore (8 tests)
# ==========================================================================


class TestDraftActions:
    """Mutation tests for draft activate, discard, and restore actions."""

    def test_activate_draft(self, page: Page, mock_base_url: str):
        """POST /api/config/draft/activate succeeds."""
        result = _api_post(page, mock_base_url, "/api/config/draft/activate")
        assert result["success"] is True
        assert "activated" in result["message"].lower()

    def test_activate_clears_pending(self, page: Page, mock_base_url: str):
        """After activation, has_pending_changes is False."""
        _api_put_config(page, mock_base_url, {"brand_name": "Pre-Activate"})
        status_before = get_api_json(page, mock_base_url, "/api/config/activation-status")
        assert status_before["has_pending_changes"] is True
        _api_post(page, mock_base_url, "/api/config/draft/activate")
        status_after = get_api_json(page, mock_base_url, "/api/config/activation-status")
        assert status_after["has_pending_changes"] is False

    def test_activate_promotes_draft_version(self, page: Page, mock_base_url: str):
        """After activation, active_version equals the draft version."""
        _api_put_config(page, mock_base_url, {"tone": "casual"})
        status_before = get_api_json(page, mock_base_url, "/api/config/activation-status")
        draft_v = status_before["draft_version"]
        _api_post(page, mock_base_url, "/api/config/draft/activate")
        status_after = get_api_json(page, mock_base_url, "/api/config/activation-status")
        assert status_after["active_version"] == draft_v

    def test_discard_draft(self, page: Page, mock_base_url: str):
        """POST /api/config/draft/discard succeeds."""
        result = _api_post(page, mock_base_url, "/api/config/draft/discard")
        assert result["success"] is True
        assert "discard" in result["message"].lower()

    def test_discard_clears_pending(self, page: Page, mock_base_url: str):
        """After discard, has_pending_changes is False."""
        _api_put_config(page, mock_base_url, {"brand_name": "Pre-Discard"})
        _api_post(page, mock_base_url, "/api/config/draft/discard")
        status = get_api_json(page, mock_base_url, "/api/config/activation-status")
        assert status["has_pending_changes"] is False

    def test_discard_resets_draft_version(self, page: Page, mock_base_url: str):
        """After discard, draft_version equals active_version."""
        _api_post(page, mock_base_url, "/api/config/draft/discard")
        status = get_api_json(page, mock_base_url, "/api/config/activation-status")
        assert status["draft_version"] == status["active_version"]

    def test_restore_succeeds(self, page: Page, mock_base_url: str):
        """POST /api/config/restore succeeds."""
        result = _api_post(page, mock_base_url, "/api/config/restore")
        assert result["success"] is True
        assert "restored" in result["message"].lower()

    def test_pending_changes_toggle_lifecycle(self, page: Page, mock_base_url: str):
        """Full lifecycle: no pending -> edit -> pending -> activate -> no pending."""
        status0 = get_api_json(page, mock_base_url, "/api/config/activation-status")
        assert status0["has_pending_changes"] is False
        _api_put_config(page, mock_base_url, {"brand_name": "Lifecycle Test"})
        status1 = get_api_json(page, mock_base_url, "/api/config/activation-status")
        assert status1["has_pending_changes"] is True
        _api_post(page, mock_base_url, "/api/config/draft/activate")
        status2 = get_api_json(page, mock_base_url, "/api/config/activation-status")
        assert status2["has_pending_changes"] is False


# ==========================================================================
# 7. TestWidgetKeyRotation -- key rotation via POST (3 tests)
# ==========================================================================


class TestWidgetKeyRotation:
    """Tests for widget key rotation endpoint."""

    def test_rotate_widget_key_succeeds(self, page: Page, mock_base_url: str):
        """POST /api/keys/rotate-widget-key returns success."""
        result = _api_post(page, mock_base_url, "/api/keys/rotate-widget-key")
        assert "newWidgetKey" in result

    def test_rotate_returns_new_key(self, page: Page, mock_base_url: str):
        """Rotation returns a new widget key string."""
        result = _api_post(page, mock_base_url, "/api/keys/rotate-widget-key")
        key = result["newWidgetKey"]
        assert isinstance(key, str)
        assert len(key) > 10

    def test_rotate_key_format(self, page: Page, mock_base_url: str):
        """New key matches pk_live_mock_* format."""
        result = _api_post(page, mock_base_url, "/api/keys/rotate-widget-key")
        assert result["newWidgetKey"].startswith("pk_live_mock_")


# ==========================================================================
# 8. TestApiContracts -- response shape validation (6 tests)
# ==========================================================================


class TestApiContracts:
    """Contract tests verifying API response shapes match expectations."""

    def test_get_config_shape(self, shared_page: Page, mock_base_url: str):
        """GET /api/config returns config, version, tier, fromCache."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        assert "config" in data
        assert "version" in data
        assert "tier" in data
        assert data["tier"] == "professional"
        assert isinstance(data["config"], dict)
        assert isinstance(data["version"], int)

    def test_get_config_has_all_draft_fields(self, shared_page: Page, mock_base_url: str):
        """GET /api/config response includes all expected draft fields."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        for key in DRAFT_FIELDS:
            assert key in data["config"], f"Missing field: {key}"

    def test_named_configs_shape(self, shared_page: Page, mock_base_url: str):
        """GET /api/config/named returns configs list and total count."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/named")
        assert "configs" in data
        assert "total" in data
        assert isinstance(data["configs"], list)
        assert isinstance(data["total"], int)
        for cfg in data["configs"]:
            assert "name" in cfg
            assert "version" in cfg
            assert "isActive" in cfg
            assert "isDefault" in cfg

    def test_activation_status_shape(self, shared_page: Page, mock_base_url: str):
        """GET /api/config/activation-status has expected fields."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/activation-status")
        assert "has_pending_changes" in data
        assert "active_version" in data
        assert "draft_version" in data
        assert isinstance(data["has_pending_changes"], bool)
        assert isinstance(data["active_version"], int)
        assert isinstance(data["draft_version"], int)

    def test_draft_state_shape(self, shared_page: Page, mock_base_url: str):
        """GET /api/config/draft returns full draft state."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/draft")
        assert "has_pending_changes" in data
        assert "active_version" in data
        assert "draft_version" in data
        assert "draft_config" in data
        assert "active_config" in data
        assert isinstance(data["draft_config"], dict)

    def test_schema_shape(self, shared_page: Page, mock_base_url: str):
        """GET /api/config/schema returns fields array."""
        data = get_api_json(shared_page, mock_base_url, "/api/config/schema")
        assert "fields" in data
        assert isinstance(data["fields"], list)
        assert len(data["fields"]) > 0
        for f in data["fields"]:
            assert "key" in f
            assert "label" in f
            assert "type" in f
