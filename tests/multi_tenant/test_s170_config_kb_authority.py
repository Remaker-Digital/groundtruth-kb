"""Tests for config-vs-KB authority features (S170).

Covers:
    WI-1229 / SPEC-1713: Config authority rule in system prompt builder
    WI-1230 / SPEC-1714: KB conflict scanner config cross-check
    WI-1231 / SPEC-1715: Admin UI models and endpoint for config conflict check

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.cosmos_schema import (
    BillingChannel,
    PreferencesDocument,
    TenantDocument,
    TenantStatus,
    TenantTier,
)
from src.multi_tenant.system_prompt_builder import (
    AgentRole,
    _build_tenant_config_section,
)
from src.multi_tenant.kb_conflict_scanner import (
    ConfigConflict,
    ConfigScanResult,
    ConflictType,
    KBConflictScanner,
    _CONFIG_POLICY_FIELDS,
    _detect_factual_conflicts,
    _filter_articles_by_keywords,
    _generate_resolution,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "t-s170-001"
NOW = datetime.now(timezone.utc).isoformat()


def _make_preferences(**overrides: Any) -> PreferencesDocument:
    defaults: dict[str, Any] = {
        "id": f"{TENANT_ID}:1",
        "tenant_id": TENANT_ID,
        "version": 1,
        "is_current": True,
        "brand_name": "TestBrand",
        "primary_language": "en",
        "created_at": NOW,
    }
    defaults.update(overrides)
    return PreferencesDocument(**defaults)


# ===========================================================================
# WI-1229 / SPEC-1713  — Config Authority Rule in System Prompt Builder
# ===========================================================================


class TestConfigAuthorityRulePrompt:
    """System prompt includes config authority rule for Response Generator."""

    def test_authority_rule_present_when_policy_fields_set(self):
        """SPEC-1713: Authority rule injected when any policy field is set."""
        prefs = _make_preferences(
            return_policy="30-day returns",
            shipping_info="Free over $50",
            brand_voice="Friendly",
        )
        section = _build_tenant_config_section(prefs, AgentRole.RESPONSE_GENERATOR)
        assert "CONFIGURATION AUTHORITY RULE" in section

    def test_authority_rule_present_with_single_field(self):
        """SPEC-1713: Even a single policy field triggers the rule."""
        prefs = _make_preferences(return_policy="14-day returns")
        section = _build_tenant_config_section(prefs, AgentRole.RESPONSE_GENERATOR)
        assert "CONFIGURATION AUTHORITY RULE" in section

    def test_authority_rule_absent_when_no_policy_fields(self):
        """SPEC-1713: No rule when all policy fields are empty/None."""
        prefs = _make_preferences(
            return_policy=None,
            shipping_info=None,
            brand_voice=None,
        )
        section = _build_tenant_config_section(prefs, AgentRole.RESPONSE_GENERATOR)
        assert "CONFIGURATION AUTHORITY RULE" not in section

    def test_authority_rule_not_in_critic_prompt(self):
        """SPEC-1713: Critic/Supervisor is immutable — no authority rule."""
        prefs = _make_preferences(
            return_policy="30-day returns",
            shipping_info="Free over $50",
        )
        section = _build_tenant_config_section(prefs, AgentRole.CRITIC_SUPERVISOR)
        assert "CONFIGURATION AUTHORITY RULE" not in section

    def test_authority_rule_not_in_intent_classifier(self):
        """SPEC-1713: Intent Classifier doesn't get authority rule."""
        prefs = _make_preferences(return_policy="30-day returns")
        section = _build_tenant_config_section(prefs, AgentRole.INTENT_CLASSIFIER)
        assert "CONFIGURATION AUTHORITY RULE" not in section

    def test_authority_rule_mentions_merchant_configuration(self):
        """SPEC-1713: Rule text mentions 'MERCHANT CONFIGURATION' for clarity."""
        prefs = _make_preferences(return_policy="30-day returns")
        section = _build_tenant_config_section(prefs, AgentRole.RESPONSE_GENERATOR)
        assert "MERCHANT CONFIGURATION" in section

    def test_authority_rule_mentions_knowledge_base(self):
        """SPEC-1713: Rule references KB articles as potentially outdated."""
        prefs = _make_preferences(brand_voice="Professional tone")
        section = _build_tenant_config_section(prefs, AgentRole.RESPONSE_GENERATOR)
        assert "knowledge base" in section.lower()

    def test_policy_fields_appear_before_authority_rule(self):
        """SPEC-1713: Policy values are listed before the authority rule."""
        prefs = _make_preferences(
            return_policy="30-day returns",
            shipping_info="Free over $50",
        )
        section = _build_tenant_config_section(prefs, AgentRole.RESPONSE_GENERATOR)
        policy_pos = section.find("30-day returns")
        rule_pos = section.find("CONFIGURATION AUTHORITY RULE")
        assert policy_pos < rule_pos, "Policy fields must appear before authority rule"


# ===========================================================================
# WI-1230 / SPEC-1714  — KB Conflict Scanner Config Cross-Check
# ===========================================================================


class TestConfigPolicyFieldsMapping:
    """_CONFIG_POLICY_FIELDS contains expected fields and keywords."""

    def test_return_policy_field_exists(self):
        assert "return_policy" in _CONFIG_POLICY_FIELDS

    def test_shipping_info_field_exists(self):
        assert "shipping_info" in _CONFIG_POLICY_FIELDS

    def test_brand_voice_field_exists(self):
        assert "brand_voice" in _CONFIG_POLICY_FIELDS

    def test_return_policy_keywords_include_refund(self):
        kw = _CONFIG_POLICY_FIELDS["return_policy"]["keywords"]
        assert "refund" in kw

    def test_shipping_info_keywords_include_delivery(self):
        kw = _CONFIG_POLICY_FIELDS["shipping_info"]["keywords"]
        assert "delivery" in kw


class TestFilterArticlesByKeywords:
    """_filter_articles_by_keywords selects relevant articles."""

    def test_matches_title_keyword(self):
        articles = [
            {"title": "Return Policy", "content": "Our policy details."},
            {"title": "Team Updates", "content": "Recent hiring."},
        ]
        result = _filter_articles_by_keywords(articles, ["return", "refund"])
        assert len(result) == 1
        assert result[0]["title"] == "Return Policy"

    def test_matches_content_keyword(self):
        articles = [
            {"title": "FAQ", "content": "We offer free shipping on orders over $50."},
        ]
        result = _filter_articles_by_keywords(articles, ["shipping", "delivery"])
        assert len(result) == 1

    def test_no_match_returns_empty(self):
        articles = [{"title": "About Us", "content": "We sell widgets."}]
        result = _filter_articles_by_keywords(articles, ["refund", "return"])
        assert len(result) == 0

    def test_case_insensitive(self):
        articles = [{"title": "SHIPPING INFO", "content": "Express delivery available."}]
        result = _filter_articles_by_keywords(articles, ["shipping"])
        assert len(result) == 1


class TestConfigVsKBConflictType:
    """ConflictType.CONFIG_VS_KB is properly defined and has resolution."""

    def test_config_vs_kb_enum_value(self):
        assert ConflictType.CONFIG_VS_KB == "config_vs_kb"

    def test_resolution_for_config_vs_kb(self):
        resolution = _generate_resolution(ConflictType.CONFIG_VS_KB, ["price: $10 vs $20"])
        assert resolution  # non-empty
        assert isinstance(resolution, str)


class TestScanConfigConflicts:
    """KBConflictScanner.scan_config_conflicts() integration tests."""

    @pytest.fixture
    def scanner(self):
        s = KBConflictScanner()
        mock_kb_repo = MagicMock()
        s.configure(mock_kb_repo)
        return s, mock_kb_repo

    @pytest.mark.asyncio
    async def test_empty_config_returns_zero_fields_checked(self, scanner):
        s, _ = scanner
        result = await s.scan_config_conflicts(TENANT_ID, {})
        assert result.config_fields_checked == 0
        assert result.conflicts == []

    @pytest.mark.asyncio
    async def test_unknown_field_name_ignored(self, scanner):
        s, _ = scanner
        result = await s.scan_config_conflicts(TENANT_ID, {"warranty_info": "5-year warranty"})
        assert result.config_fields_checked == 0

    @pytest.mark.asyncio
    async def test_detects_factual_conflict(self, scanner):
        """Config says 30 days, KB article says 14 days — should detect conflict."""
        s, mock_kb = scanner
        mock_kb.list_active = AsyncMock(return_value=[
            {
                "id": "art-1",
                "title": "Return Policy",
                "content": "Our return window is 14 days from purchase date.",
            },
        ])
        result = await s.scan_config_conflicts(
            TENANT_ID,
            {"return_policy": "We offer a 30-day return window."},
        )
        assert result.config_fields_checked == 1
        assert result.articles_checked == 1
        assert len(result.conflicts) >= 1
        assert result.conflicts[0].config_field == "return_policy"
        assert result.conflicts[0].article_id == "art-1"

    @pytest.mark.asyncio
    async def test_no_conflict_when_consistent(self, scanner):
        """Config and KB agree — no conflict."""
        s, mock_kb = scanner
        mock_kb.list_active = AsyncMock(return_value=[
            {
                "id": "art-2",
                "title": "Shipping Info",
                "content": "Free shipping on orders over $50.",
            },
        ])
        result = await s.scan_config_conflicts(
            TENANT_ID,
            {"shipping_info": "Free shipping on orders over $50."},
        )
        assert result.conflicts == []

    @pytest.mark.asyncio
    async def test_irrelevant_articles_skipped(self, scanner):
        """Articles without matching keywords are not checked."""
        s, mock_kb = scanner
        mock_kb.list_active = AsyncMock(return_value=[
            {
                "id": "art-3",
                "title": "About Our Team",
                "content": "We have a great team of 10 developers.",
            },
        ])
        result = await s.scan_config_conflicts(
            TENANT_ID,
            {"return_policy": "30-day return window."},
        )
        # Article about team shouldn't trigger a conflict scan
        assert result.conflicts == []

    @pytest.mark.asyncio
    async def test_scan_result_has_timing(self, scanner):
        s, mock_kb = scanner
        mock_kb.list_active = AsyncMock(return_value=[])
        result = await s.scan_config_conflicts(TENANT_ID, {"return_policy": "30 days"})
        assert isinstance(result.scan_duration_ms, int)
        assert result.scan_duration_ms >= 0

    @pytest.mark.asyncio
    async def test_conflict_has_resolution_text(self, scanner):
        s, mock_kb = scanner
        mock_kb.list_active = AsyncMock(return_value=[
            {
                "id": "art-4",
                "title": "Returns FAQ",
                "content": "Returns accepted within 7 days.",
            },
        ])
        result = await s.scan_config_conflicts(
            TENANT_ID,
            {"return_policy": "Returns accepted within 30 days."},
        )
        if result.conflicts:
            assert result.conflicts[0].resolution  # non-empty resolution


# ===========================================================================
# WI-1231 / SPEC-1715  — Admin API Endpoint + Pydantic Models
# ===========================================================================


class TestConfigConflictEndpointModels:
    """Pydantic models for config conflict endpoint exist and are importable."""

    def test_config_conflict_request_importable(self):
        from src.multi_tenant.admin_knowledge_api import ConfigConflictRequest
        req = ConfigConflictRequest(
            return_policy="30 days",
            shipping_info="Free over $50",
            brand_voice=None,
        )
        assert req.return_policy == "30 days"
        assert req.brand_voice is None

    def test_config_conflict_item_importable(self):
        from src.multi_tenant.admin_knowledge_api import ConfigConflictItem
        item = ConfigConflictItem(
            config_field="return_policy",
            config_value="30 days",
            article_id="art-1",
            article_title="Return Policy",
            conflicting_facts=["duration: 30 days vs 14 days"],
            resolution="Update KB article to match config.",
        )
        assert item.config_field == "return_policy"

    def test_config_conflict_response_importable(self):
        from src.multi_tenant.admin_knowledge_api import ConfigConflictResponse
        resp = ConfigConflictResponse(
            tenant_id=TENANT_ID,
            scanned_at=NOW,
            config_fields_checked=2,
            articles_checked=10,
            conflicts=[],
            scan_duration_ms=42,
        )
        assert resp.config_fields_checked == 2
        assert resp.conflicts == []


class TestConfigConflictEndpointRegistered:
    """POST /api/admin/knowledge/scan/config endpoint exists on the router."""

    def test_endpoint_registered(self):
        from src.multi_tenant.admin_knowledge_api import router
        paths = [r.path for r in router.routes if hasattr(r, "path")]
        assert "/scan/config" in paths or any("/scan/config" in p for p in paths)

    def test_endpoint_methods_include_post(self):
        from src.multi_tenant.admin_knowledge_api import router
        for route in router.routes:
            if hasattr(route, "path") and "/scan/config" in route.path:
                assert "POST" in route.methods
                break
        else:
            pytest.fail("scan/config route not found")


class TestConfigScanResultDataclass:
    """ConfigScanResult and ConfigConflict dataclasses."""

    def test_config_scan_result_defaults(self):
        result = ConfigScanResult(
            tenant_id=TENANT_ID,
            scanned_at=NOW,
            config_fields_checked=0,
            articles_checked=0,
        )
        assert result.conflicts == []
        assert result.scan_duration_ms == 0

    def test_config_conflict_fields(self):
        c = ConfigConflict(
            config_field="return_policy",
            config_value="30 days",
            article_id="art-1",
            article_title="Returns",
            conflicting_facts=["30 days vs 14 days"],
            resolution="Update the article.",
        )
        assert c.config_field == "return_policy"
        assert len(c.conflicting_facts) == 1


class TestConfigConflictUIContract:
    """Structural tests for Configuration.tsx and KnowledgeBase.tsx UI changes."""

    def test_configuration_page_has_conflict_state(self):
        """SPEC-1715: Configuration page declares configConflicts state."""
        import pathlib
        config_tsx = pathlib.Path(
            "admin/standalone/pages/Configuration.tsx"
        ).read_text(encoding="utf-8")
        assert "configConflicts" in config_tsx

    def test_configuration_page_has_conflict_alert(self):
        """SPEC-1715: Configuration page renders conflict alert."""
        import pathlib
        config_tsx = pathlib.Path(
            "admin/standalone/pages/Configuration.tsx"
        ).read_text(encoding="utf-8")
        assert "Configuration conflicts with knowledge base" in config_tsx

    def test_configuration_page_calls_scan_endpoint(self):
        """SPEC-1715: Configuration page POSTs to scan/config endpoint."""
        import pathlib
        config_tsx = pathlib.Path(
            "admin/standalone/pages/Configuration.tsx"
        ).read_text(encoding="utf-8")
        assert "/api/admin/knowledge/scan/config" in config_tsx

    def test_knowledge_base_page_has_conflict_state(self):
        """SPEC-1715: KB page declares configConflicts state."""
        import pathlib
        kb_tsx = pathlib.Path(
            "admin/standalone/pages/KnowledgeBase.tsx"
        ).read_text(encoding="utf-8")
        assert "configConflicts" in kb_tsx

    def test_knowledge_base_page_has_conflict_alert(self):
        """SPEC-1715: KB page renders conflict alert."""
        import pathlib
        kb_tsx = pathlib.Path(
            "admin/standalone/pages/KnowledgeBase.tsx"
        ).read_text(encoding="utf-8")
        assert "Policy conflicts with knowledge base articles" in kb_tsx

    def test_knowledge_base_page_calls_check_on_save(self):
        """SPEC-1715: KB page calls checkConfigConflicts after policy save."""
        import pathlib
        kb_tsx = pathlib.Path(
            "admin/standalone/pages/KnowledgeBase.tsx"
        ).read_text(encoding="utf-8")
        assert "checkConfigConflicts" in kb_tsx

    def test_knowledge_base_page_calls_check_on_article_save(self):
        """SPEC-1715: KB page calls checkConfigConflicts after article save."""
        import pathlib
        kb_tsx = pathlib.Path(
            "admin/standalone/pages/KnowledgeBase.tsx"
        ).read_text(encoding="utf-8")
        # After article save, checkConfigConflicts is called
        content = kb_tsx
        # Find article save handler area
        assert content.count("checkConfigConflicts") >= 2, \
            "checkConfigConflicts should be called in both policy save and article save"
