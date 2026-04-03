"""Tests for Preset Service — G6 Vertical Template Starter Kits (SPEC-1878).

Covers:
    - Preset YAML loading and caching
    - list_presets returns all 4 verticals
    - get_preset returns full detail
    - get_preset returns None for unknown ID
    - CONFIG_SAVE_FIELDS allowlist enforcement
    - _extract_config_fields extracts preferences + widget fields
    - apply_preset calls all 4 write surfaces
    - apply_preset raises ValueError for unknown preset

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.presets.preset_service import (
    CONFIG_SAVE_FIELDS,
    ApplyResult,
    PresetService,
    PresetSummary,
    get_preset_service,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "t-preset-test-001"
EXPECTED_PRESET_IDS = {"knowledge_only", "returns_agent", "presales_copilot", "order_support"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def service() -> PresetService:
    """Create a fresh PresetService for each test."""
    return PresetService()


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------


class TestPresetLoading:
    """Tests for YAML file loading and caching."""

    def test_list_presets_returns_all_four_verticals(self, service: PresetService) -> None:
        presets = service.list_presets()
        ids = {p.id for p in presets}
        assert ids == EXPECTED_PRESET_IDS

    def test_list_presets_returns_preset_summary_type(self, service: PresetService) -> None:
        presets = service.list_presets()
        for p in presets:
            assert isinstance(p, PresetSummary)
            assert p.display_name
            assert p.description
            assert p.quick_action_count >= 2
            assert p.article_count >= 1

    def test_get_preset_returns_full_detail(self, service: PresetService) -> None:
        preset = service.get_preset("returns_agent")
        assert preset is not None
        assert preset["id"] == "returns_agent"
        assert "preferences" in preset
        assert "quick_actions" in preset
        assert "knowledge_seed" in preset
        assert "widget" in preset

    def test_get_preset_unknown_returns_none(self, service: PresetService) -> None:
        assert service.get_preset("nonexistent") is None

    def test_preset_caching(self, service: PresetService) -> None:
        """Second call should use cache."""
        service.list_presets()
        assert service._loaded is True
        # Mutate cache to prove second call doesn't reload
        service._cache["_test"] = {
            "id": "_test", "display_name": "Test", "description": "Test",
            "quick_actions": [], "knowledge_seed": [],
        }
        presets = service.list_presets()
        ids = {p.id for p in presets}
        assert "_test" in ids

    def test_all_presets_have_required_fields(self, service: PresetService) -> None:
        for preset_id in EXPECTED_PRESET_IDS:
            preset = service.get_preset(preset_id)
            assert preset is not None, f"Missing preset: {preset_id}"
            assert "id" in preset
            assert "display_name" in preset
            assert "description" in preset
            assert "preferences" in preset
            assert "quick_actions" in preset
            assert "widget" in preset
            assert "knowledge_seed" in preset

    def test_preset_summary_to_dict(self, service: PresetService) -> None:
        presets = service.list_presets()
        for p in presets:
            d = p.to_dict()
            assert "id" in d
            assert "display_name" in d
            assert "quick_action_count" in d
            assert "article_count" in d
            assert "agents_recommended" in d


# ---------------------------------------------------------------------------
# Config field extraction
# ---------------------------------------------------------------------------


class TestConfigFieldExtraction:
    """Tests for CONFIG_SAVE_FIELDS allowlist and extraction."""

    def test_config_save_fields_allowlist_is_frozen(self) -> None:
        assert isinstance(CONFIG_SAVE_FIELDS, frozenset)

    def test_config_save_fields_contains_expected(self) -> None:
        expected = {
            "brand_voice", "formality_level", "response_length",
            "escalation_threshold", "escalation_keywords",
            "custom_instructions", "widget_greeting_message",
            "widget_input_placeholder",
        }
        assert CONFIG_SAVE_FIELDS == expected

    def test_extract_config_fields_preferences(self, service: PresetService) -> None:
        preset = service.get_preset("returns_agent")
        assert preset is not None
        fields = service._extract_config_fields(preset)
        assert "brand_voice" in fields
        assert fields["brand_voice"] == "professional and empathetic"
        assert "formality_level" in fields
        assert "escalation_keywords" in fields

    def test_extract_config_fields_includes_widget(self, service: PresetService) -> None:
        preset = service.get_preset("returns_agent")
        assert preset is not None
        fields = service._extract_config_fields(preset)
        assert "widget_greeting_message" in fields
        assert "widget_input_placeholder" in fields

    def test_extract_config_fields_excludes_unknown(self, service: PresetService) -> None:
        """Fields not in CONFIG_SAVE_FIELDS must not leak through."""
        preset = {
            "preferences": {
                "brand_voice": "test",
                "unknown_field": "should_not_appear",
            },
            "widget": {},
        }
        fields = service._extract_config_fields(preset)
        assert "brand_voice" in fields
        assert "unknown_field" not in fields


# ---------------------------------------------------------------------------
# apply_preset
# ---------------------------------------------------------------------------


class TestApplyPreset:
    """Tests for the apply_preset orchestration."""

    @pytest.mark.asyncio
    async def test_apply_preset_unknown_raises(self, service: PresetService) -> None:
        with pytest.raises(ValueError, match="not found"):
            await service.apply_preset(TENANT_ID, "nonexistent")

    @pytest.mark.asyncio
    async def test_apply_preset_calls_all_surfaces(self, service: PresetService) -> None:
        """Verify apply_preset calls config save, QA create, assignments, KB seed, and agent provisioning."""
        with (
            patch.object(service, "_save_config_draft", new_callable=AsyncMock) as mock_config,
            patch.object(service, "_create_quick_actions", new_callable=AsyncMock) as mock_qa,
            patch.object(service, "_create_assignments", new_callable=AsyncMock) as mock_assign,
            patch.object(service, "_seed_kb_articles", new_callable=AsyncMock) as mock_kb,
            patch.object(service, "_provision_agents", new_callable=AsyncMock) as mock_agents,
        ):
            mock_qa.return_value = ["id-1", "id-2"]
            mock_kb.return_value = 2
            mock_agents.return_value = (["sales", "schedule"], [])

            result = await service.apply_preset(TENANT_ID, "returns_agent")

            mock_config.assert_called_once()
            mock_qa.assert_called_once()
            mock_assign.assert_called_once()
            mock_kb.assert_called_once()
            mock_agents.assert_called_once()

            assert result.draft_created is True
            assert result.quick_actions_created == 2
            assert result.assignments_created is True
            assert result.articles_created == 2
            assert result.agents_enabled == ["sales", "schedule"]
            assert result.agents_skipped == []

    @pytest.mark.asyncio
    async def test_apply_preset_no_quick_actions_skips_assignments(
        self, service: PresetService,
    ) -> None:
        """If no QA created, assignments should not be called."""
        with (
            patch.object(service, "_save_config_draft", new_callable=AsyncMock),
            patch.object(service, "_create_quick_actions", new_callable=AsyncMock) as mock_qa,
            patch.object(service, "_create_assignments", new_callable=AsyncMock) as mock_assign,
            patch.object(service, "_seed_kb_articles", new_callable=AsyncMock) as mock_kb,
            patch.object(service, "_provision_agents", new_callable=AsyncMock) as mock_agents,
        ):
            mock_qa.return_value = []
            mock_kb.return_value = 0
            mock_agents.return_value = ([], [])

            # Use a preset with no quick actions via cache manipulation
            service._ensure_loaded()
            service._cache["empty_qa"] = {
                "id": "empty_qa",
                "display_name": "Empty",
                "description": "Test",
                "preferences": {"brand_voice": "test"},
                "quick_actions": [],
                "widget": {},
                "knowledge_seed": [],
                "agents_recommended": [],
            }

            result = await service.apply_preset(TENANT_ID, "empty_qa")
            mock_assign.assert_not_called()
            assert result.assignments_created is False

    @pytest.mark.asyncio
    async def test_apply_result_to_dict(self) -> None:
        result = ApplyResult(
            draft_created=True,
            quick_actions_created=3,
            assignments_created=True,
            articles_created=2,
            agents_recommended=[{"agent_id": "sales", "tier_required": "professional"}],
            agents_enabled=["sales"],
            agents_skipped=["schedule"],
        )
        d = result.to_dict()
        assert d["draft_created"] is True
        assert d["quick_actions_created"] == 3
        assert d["assignments_created"] is True
        assert d["articles_created"] == 2
        assert len(d["agents_recommended"]) == 1
        assert d["agents_enabled"] == ["sales"]
        assert d["agents_skipped"] == ["schedule"]


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Agent provisioning (WI-3025)
# ---------------------------------------------------------------------------


class TestAgentProvisioning:
    """Tests for _provision_agents — overlay/binding provisioning."""

    @pytest.fixture
    def mock_registry(self):
        """Mock PluginAgentRegistry with a few test agents."""
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class FakeSkill:
            skill_id: str
            mode: str = "read"

        @dataclass(frozen=True)
        class FakeAgent:
            agent_id: str
            tier_gate: str = "professional"
            skills: tuple = ()

        registry = MagicMock()
        agents = {
            "sales": FakeAgent(
                agent_id="sales",
                tier_gate="professional",
                skills=(
                    FakeSkill(skill_id="sales:search-products", mode="read"),
                    FakeSkill(skill_id="sales:create-checkout", mode="mutate"),
                ),
            ),
            "gateway": FakeAgent(
                agent_id="gateway",
                tier_gate="starter",
                skills=(
                    FakeSkill(skill_id="gateway:check-availability", mode="read"),
                ),
            ),
        }
        registry.get.side_effect = lambda aid: agents.get(aid)
        return registry

    @pytest.fixture
    def mock_overlay_repo(self):
        repo = AsyncMock()
        repo.get_overlay.return_value = None  # no existing overlay
        return repo

    @pytest.fixture
    def mock_binding_repo(self):
        repo = AsyncMock()
        repo.get_binding.return_value = None  # no existing binding
        return repo

    @pytest.mark.asyncio
    async def test_provision_professional_tier_creates_overlays(
        self, service: PresetService, mock_registry, mock_overlay_repo, mock_binding_repo,
    ) -> None:
        """Professional tier should enable agents gated at professional."""
        with (
            patch("src.agents.plugins.registry.PluginAgentRegistry.get_instance", return_value=mock_registry),
            patch("src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository", return_value=mock_overlay_repo),
            patch("src.multi_tenant.repositories.agent_bindings.AgentSkillBindingRepository", return_value=mock_binding_repo),
            patch("src.agents.plugins.overlay.clear_resolution_cache"),
            patch("src.agents.plugins.bindings.SkillBindingService.get_instance") as mock_svc,
        ):
            mock_svc.return_value = MagicMock()
            enabled, skipped = await service._provision_agents(
                TENANT_ID,
                [{"agent_id": "sales"}, {"agent_id": "gateway"}],
                "professional",
            )
            assert "sales" in enabled
            assert "gateway" in enabled
            assert len(skipped) == 0
            # sales overlay + gateway overlay = 2 upsert calls
            assert mock_overlay_repo.upsert_overlay.call_count == 2

    @pytest.mark.asyncio
    async def test_provision_starter_tier_gates_professional_agents(
        self, service: PresetService, mock_registry, mock_overlay_repo, mock_binding_repo,
    ) -> None:
        """Starter tier should only enable agents gated at starter or free."""
        with (
            patch("src.agents.plugins.registry.PluginAgentRegistry.get_instance", return_value=mock_registry),
            patch("src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository", return_value=mock_overlay_repo),
            patch("src.multi_tenant.repositories.agent_bindings.AgentSkillBindingRepository", return_value=mock_binding_repo),
            patch("src.agents.plugins.overlay.clear_resolution_cache"),
            patch("src.agents.plugins.bindings.SkillBindingService.get_instance") as mock_svc,
        ):
            mock_svc.return_value = MagicMock()
            enabled, skipped = await service._provision_agents(
                TENANT_ID,
                [{"agent_id": "sales"}, {"agent_id": "gateway"}],
                "starter",
            )
            assert "gateway" in enabled  # starter gate passes
            assert "sales" in skipped    # professional gate fails
            assert mock_overlay_repo.upsert_overlay.call_count == 1

    @pytest.mark.asyncio
    async def test_provision_uses_registry_skill_mode(
        self, service: PresetService, mock_registry, mock_overlay_repo, mock_binding_repo,
    ) -> None:
        """Binding mode must come from registry skill definition, not hardcoded."""
        with (
            patch("src.agents.plugins.registry.PluginAgentRegistry.get_instance", return_value=mock_registry),
            patch("src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository", return_value=mock_overlay_repo),
            patch("src.multi_tenant.repositories.agent_bindings.AgentSkillBindingRepository", return_value=mock_binding_repo),
            patch("src.agents.plugins.overlay.clear_resolution_cache"),
            patch("src.agents.plugins.bindings.SkillBindingService.get_instance") as mock_svc,
        ):
            mock_svc.return_value = MagicMock()
            await service._provision_agents(
                TENANT_ID, [{"agent_id": "sales"}], "professional",
            )
            # Check binding calls have correct modes
            calls = mock_binding_repo.upsert_binding.call_args_list
            modes = {c.kwargs.get("mode") or c.args[3] for c in calls}
            assert "read" in modes     # search-products
            assert "mutate" in modes   # create-checkout

    @pytest.mark.asyncio
    async def test_provision_create_if_absent_skips_existing_overlay(
        self, service: PresetService, mock_registry, mock_binding_repo,
    ) -> None:
        """Existing overlay should not be overwritten on re-apply."""
        overlay_repo = AsyncMock()
        overlay_repo.get_overlay.return_value = {"agent_id": "sales", "enabled": False}  # already exists
        with (
            patch("src.agents.plugins.registry.PluginAgentRegistry.get_instance", return_value=mock_registry),
            patch("src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository", return_value=overlay_repo),
            patch("src.multi_tenant.repositories.agent_bindings.AgentSkillBindingRepository", return_value=mock_binding_repo),
            patch("src.agents.plugins.overlay.clear_resolution_cache"),
            patch("src.agents.plugins.bindings.SkillBindingService.get_instance") as mock_svc,
        ):
            mock_svc.return_value = MagicMock()
            enabled, skipped = await service._provision_agents(
                TENANT_ID, [{"agent_id": "sales"}], "professional",
            )
            assert "sales" in skipped
            assert len(enabled) == 0
            overlay_repo.upsert_overlay.assert_not_called()

    @pytest.mark.asyncio
    async def test_provision_create_if_absent_skips_existing_binding(
        self, service: PresetService, mock_registry, mock_overlay_repo,
    ) -> None:
        """Existing binding should not be overwritten on re-apply."""
        binding_repo = AsyncMock()
        binding_repo.get_binding.side_effect = lambda tid, sid: (
            {"skill_id": sid} if sid == "sales:search-products" else None
        )
        with (
            patch("src.agents.plugins.registry.PluginAgentRegistry.get_instance", return_value=mock_registry),
            patch("src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository", return_value=mock_overlay_repo),
            patch("src.multi_tenant.repositories.agent_bindings.AgentSkillBindingRepository", return_value=binding_repo),
            patch("src.agents.plugins.overlay.clear_resolution_cache"),
            patch("src.agents.plugins.bindings.SkillBindingService.get_instance") as mock_svc,
        ):
            mock_svc.return_value = MagicMock()
            await service._provision_agents(
                TENANT_ID, [{"agent_id": "sales"}], "professional",
            )
            # Only 1 binding created (create-checkout), not 2
            assert binding_repo.upsert_binding.call_count == 1

    @pytest.mark.asyncio
    async def test_provision_empty_agents_recommended(
        self, service: PresetService,
    ) -> None:
        """Empty agents_recommended should return empty lists."""
        enabled, skipped = await service._provision_agents(TENANT_ID, [], "professional")
        assert enabled == []
        assert skipped == []

    @pytest.mark.asyncio
    async def test_provision_unknown_agent_skipped(
        self, service: PresetService, mock_registry, mock_overlay_repo, mock_binding_repo,
    ) -> None:
        """Agent not in registry should be skipped."""
        with (
            patch("src.agents.plugins.registry.PluginAgentRegistry.get_instance", return_value=mock_registry),
            patch("src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository", return_value=mock_overlay_repo),
            patch("src.multi_tenant.repositories.agent_bindings.AgentSkillBindingRepository", return_value=mock_binding_repo),
        ):
            enabled, skipped = await service._provision_agents(
                TENANT_ID, [{"agent_id": "nonexistent"}], "professional",
            )
            assert len(enabled) == 0
            assert len(skipped) == 0  # unknown agent is not "skipped" — it's ignored
            mock_overlay_repo.upsert_overlay.assert_not_called()

    @pytest.mark.asyncio
    async def test_provision_invalidates_cache_after_writes(
        self, service: PresetService, mock_registry, mock_overlay_repo, mock_binding_repo,
    ) -> None:
        """Cache must be invalidated after provisioning overlays/bindings."""
        with (
            patch("src.agents.plugins.registry.PluginAgentRegistry.get_instance", return_value=mock_registry),
            patch("src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository", return_value=mock_overlay_repo),
            patch("src.multi_tenant.repositories.agent_bindings.AgentSkillBindingRepository", return_value=mock_binding_repo),
            patch("src.agents.plugins.overlay.clear_resolution_cache") as mock_clear,
            patch("src.agents.plugins.bindings.SkillBindingService.get_instance") as mock_svc,
        ):
            mock_binding_svc = MagicMock()
            mock_svc.return_value = mock_binding_svc
            await service._provision_agents(
                TENANT_ID, [{"agent_id": "gateway"}], "starter",
            )
            mock_clear.assert_called_once()
            mock_binding_svc.invalidate.assert_called_once_with(TENANT_ID)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_get_preset_service_returns_same_instance(self) -> None:
        # Reset singleton for test isolation
        import src.presets.preset_service as mod
        mod._preset_service = None
        svc1 = get_preset_service()
        svc2 = get_preset_service()
        assert svc1 is svc2
        mod._preset_service = None  # cleanup
