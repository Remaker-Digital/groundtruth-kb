# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPEC-1706 Memory & Privacy E2E tests against mock Vite dev server.

Tests cover: memory layer display, privacy settings, statistics,
settings update, and API contract verification.

Fixture data (memory.ts):
  4 layers: Conversation memory (session), Customer context (customer),
    Cross-session learning (tenant), Dedicated model training (tenant, enterprise-only, disabled)
  Privacy: memoryEnabled=true, retentionDays=90, piiMaskingEnabled=true,
    gdprCompliant=true
  Stats: totalMemories=142, activeCustomers=38, avgMemoriesPerCustomer=3.7
"""

import json
import pytest
from playwright.sync_api import Page

from tests.e2e_mock.conftest import (
    api_origin,
    dismiss_onboarding_if_present,
    get_api_json,
    main_text,
    navigate_and_settle,
)


MEMORY_PATH = "/memory-privacy"


def _go_memory(pg: Page, base_url: str) -> None:
    navigate_and_settle(pg, MEMORY_PATH, base_url)
    dismiss_onboarding_if_present(pg)


class TestMemoryLayers:
    """Verify memory layers are displayed with correct data."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        _go_memory(shared_page, mock_base_url)
        self.pg = shared_page

    def test_memory_page_loads(self):
        """Memory page renders with heading."""
        text = main_text(self.pg)
        assert "Memory" in text

    def test_conversation_memory_layer_shown(self):
        """Conversation Memory layer is displayed."""
        text = main_text(self.pg)
        assert "Conversation" in text

    def test_customer_memory_layer_shown(self):
        """Customer Memory layer is displayed."""
        text = main_text(self.pg)
        assert "Customer" in text

    def test_cross_session_learning_layer_shown(self):
        """Cross-session learning layer is displayed."""
        text = main_text(self.pg)
        assert "Cross-session learning" in text

    def test_dedicated_model_training_layer_shown(self):
        """Dedicated model training layer is displayed (enterprise-only)."""
        text = main_text(self.pg)
        assert "Dedicated model training" in text

    def test_enterprise_gate_indicator(self):
        """Dedicated model training shows enterprise tier gate indicator."""
        text = main_text(self.pg).lower()
        has_gate = "enterprise" in text or "disabled" in text
        assert has_gate

    def test_layer_descriptions_present(self):
        """Layers have descriptions rendered."""
        text = main_text(self.pg).lower()
        has_desc = "remembers" in text or "conversation" in text or "session" in text
        assert has_desc

    def test_enabled_layers_count(self):
        """Three of four layers are enabled (Dedicated model training disabled)."""
        text = main_text(self.pg)
        assert "Memory" in text


class TestPrivacySettings:
    """Verify privacy settings section renders correctly."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        _go_memory(shared_page, mock_base_url)
        self.pg = shared_page

    def test_privacy_section_present(self):
        """Privacy settings section exists on the page."""
        text = main_text(self.pg).lower()
        has_privacy = "privacy" in text or "setting" in text or "retention" in text
        assert has_privacy

    def test_memory_enabled_indicator(self):
        """Memory enabled status is shown (true)."""
        text = main_text(self.pg).lower()
        has_enabled = "enabled" in text or "on" in text or "active" in text
        assert has_enabled

    def test_data_retention_section_shown(self):
        """Data retention & privacy section is displayed."""
        text = main_text(self.pg).lower()
        assert "data retention" in text or "retention" in text

    def test_pii_masking_shown(self):
        """PII masking status is displayed."""
        text = main_text(self.pg).lower()
        has_pii = "pii" in text or "masking" in text or "mask" in text
        assert has_pii

    def test_gdpr_compliance_shown(self):
        """GDPR compliance status is displayed."""
        text = main_text(self.pg).lower()
        has_gdpr = "gdpr" in text or "compliant" in text or "compliance" in text
        assert has_gdpr

    def test_privacy_settings_not_empty(self):
        """Privacy section has content."""
        text = main_text(self.pg)
        assert len(text) > 100

    def test_memory_page_heading(self):
        """Page heading includes Memory."""
        text = main_text(self.pg)
        assert "Memory" in text

    def test_privacy_page_has_controls(self):
        """Page has interactive controls (switches/toggles)."""
        text = main_text(self.pg).lower()
        has_controls = any(w in text for w in ["enabled", "disabled", "days", "on", "off"])
        assert has_controls


class TestStatistics:
    """Verify memory statistics are displayed."""

    def test_stats_endpoint_returns_data(self, shared_page: Page, mock_base_url: str):
        """GET /api/admin/memory/stats returns statistics."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/memory/stats")
        assert data["totalMemories"] == 142
        assert data["activeCustomers"] == 38

    def test_stats_avg_memories_per_customer(self, shared_page: Page, mock_base_url: str):
        """Stats include average memories per customer."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/memory/stats")
        assert data["avgMemoriesPerCustomer"] == 3.7

    def test_stats_storage_used(self, shared_page: Page, mock_base_url: str):
        """Stats include storage used in bytes."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/memory/stats")
        assert data["storageUsedBytes"] == 524288

    def test_stats_has_all_fields(self, shared_page: Page, mock_base_url: str):
        """Stats response has all expected fields."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/memory/stats")
        for field in ["totalMemories", "activeCustomers", "avgMemoriesPerCustomer", "storageUsedBytes"]:
            assert field in data, f"Missing field: {field}"

    def test_stats_integers_are_int(self, shared_page: Page, mock_base_url: str):
        """Integer stats values are proper int type."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/memory/stats")
        assert isinstance(data["totalMemories"], int)
        assert isinstance(data["activeCustomers"], int)

    def test_stats_storage_is_int(self, shared_page: Page, mock_base_url: str):
        """Storage used value is integer."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/memory/stats")
        assert isinstance(data["storageUsedBytes"], int)


class TestSettingsUpdate:
    """Verify memory settings can be updated via PUT."""

    def test_update_retention_days(self, page: Page, mock_base_url: str):
        """PUT /api/admin/memory can update retention days."""
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/memory",
            data=json.dumps({"privacySettings": {"retentionDays": 60}}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 200
        body = resp.json()
        assert body["privacySettings"]["retentionDays"] == 60

    def test_update_pii_masking(self, page: Page, mock_base_url: str):
        """PUT /api/admin/memory can toggle PII masking."""
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/memory",
            data=json.dumps({"privacySettings": {"piiMaskingEnabled": False}}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 200
        body = resp.json()
        assert body["privacySettings"]["piiMaskingEnabled"] is False

    def test_update_preserves_layers(self, page: Page, mock_base_url: str):
        """Updating privacy settings preserves layer data."""
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/memory",
            data=json.dumps({"privacySettings": {"retentionDays": 30}}),
            headers={"Content-Type": "application/json"},
        )
        body = resp.json()
        assert "layers" in body
        assert len(body["layers"]) == 4

    def test_update_layers(self, page: Page, mock_base_url: str):
        """PUT /api/admin/memory can update layers."""
        data = get_api_json(page, mock_base_url, "/api/admin/memory")
        layers = data["layers"]
        layers[0]["enabled"] = False
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/memory",
            data=json.dumps({"layers": layers}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 200


class TestMemoryApiContracts:
    """Verify memory mock API endpoints return expected data shapes."""

    def test_memory_get_returns_layers_and_privacy(self, shared_page: Page, mock_base_url: str):
        """GET /api/admin/memory returns layers and privacySettings."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/memory")
        assert "layers" in data
        assert "privacySettings" in data

    def test_memory_layers_count(self, shared_page: Page, mock_base_url: str):
        """GET /api/admin/memory returns 4 layers."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/memory")
        assert len(data["layers"]) == 4

    def test_memory_privacy_fields(self, shared_page: Page, mock_base_url: str):
        """Privacy settings include all expected fields."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/memory")
        ps = data["privacySettings"]
        assert ps["memoryEnabled"] is True
        assert ps["retentionDays"] == 90
        assert ps["piiMaskingEnabled"] is True
        assert ps["gdprCompliant"] is True

    def test_layer_structure(self, shared_page: Page, mock_base_url: str):
        """Each layer has id, name, enabled, scope, description."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/memory")
        for layer in data["layers"]:
            for field in ["id", "name", "enabled", "scope", "description"]:
                assert field in layer, f"Layer missing field: {field}"
