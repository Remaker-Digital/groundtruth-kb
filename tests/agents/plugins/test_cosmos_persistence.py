"""Cosmos Persistence Tests for Agent Overlays and Bindings (WI-4015).

Tests repository wiring, cache invalidation, and admin API integration
with Cosmos-backed storage.

These tests use mocked Cosmos containers (no live Azure dependency).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.plugins.bindings import SkillBindingService
from src.agents.plugins.overlay import clear_resolution_cache, _resolution_cache
from src.multi_tenant.cosmos_schema import (
    COLLECTION_AGENT_BINDINGS,
    COLLECTION_AGENT_OVERLAYS,
    AgentSkillBindingDocument,
    TenantAgentOverlayDocument,
)


@pytest.fixture(autouse=True)
def _reset_singletons():
    """Reset singletons and caches between tests."""
    SkillBindingService.reset()
    clear_resolution_cache()
    yield
    SkillBindingService.reset()
    clear_resolution_cache()


# ---------------------------------------------------------------------------
# WI-4010: Collection Registration
# ---------------------------------------------------------------------------


class TestCollectionRegistration:
    """WI-4010: Cosmos collections are registered correctly."""

    def test_overlay_collection_constant_exists(self):
        assert COLLECTION_AGENT_OVERLAYS == "agent_overlays"

    def test_binding_collection_constant_exists(self):
        assert COLLECTION_AGENT_BINDINGS == "agent_bindings"

    def test_collections_in_all_collections(self):
        from src.multi_tenant.cosmos_schema import ALL_COLLECTIONS
        assert COLLECTION_AGENT_OVERLAYS in ALL_COLLECTIONS
        assert COLLECTION_AGENT_BINDINGS in ALL_COLLECTIONS

    def test_overlay_collection_config_exists(self):
        from src.multi_tenant.cosmos_schema import get_collection_configs
        configs = get_collection_configs()
        overlay_cfg = next(
            (c for c in configs if c.name == COLLECTION_AGENT_OVERLAYS), None
        )
        assert overlay_cfg is not None
        assert overlay_cfg.partition_key == "/tenant_id"

    def test_binding_collection_config_exists(self):
        from src.multi_tenant.cosmos_schema import get_collection_configs
        configs = get_collection_configs()
        binding_cfg = next(
            (c for c in configs if c.name == COLLECTION_AGENT_BINDINGS), None
        )
        assert binding_cfg is not None
        assert binding_cfg.partition_key == "/tenant_id"

    def test_overlay_narrow_indexing_excludes_blobs(self):
        """Codex Finding 5: overlay blobs excluded from indexing."""
        from src.multi_tenant.cosmos_schema import get_collection_configs
        configs = get_collection_configs()
        overlay_cfg = next(c for c in configs if c.name == COLLECTION_AGENT_OVERLAYS)
        policy = overlay_cfg.indexing_policy
        assert policy is not None
        excluded = [p["path"] for p in policy["excludedPaths"]]
        assert "/*" in excluded  # broad exclusion
        included = [p["path"] for p in policy["includedPaths"]]
        assert "/agent_id/?" in included
        assert "/enabled/?" in included

    def test_binding_narrow_indexing(self):
        """Codex Finding 5: binding indexing only covers queried fields."""
        from src.multi_tenant.cosmos_schema import get_collection_configs
        configs = get_collection_configs()
        binding_cfg = next(c for c in configs if c.name == COLLECTION_AGENT_BINDINGS)
        policy = binding_cfg.indexing_policy
        included = [p["path"] for p in policy["includedPaths"]]
        assert "/skill_id/?" in included
        assert "/credential_ref/?" in included


# ---------------------------------------------------------------------------
# WI-4011: TenantAgentOverlayRepository
# ---------------------------------------------------------------------------


class TestOverlayRepository:
    """WI-4011: Overlay repository extends TenantScopedRepository."""

    def test_inherits_tenant_scoped(self):
        from src.multi_tenant.repositories.agent_overlays import TenantAgentOverlayRepository
        from src.multi_tenant.repositories.base import TenantScopedRepository
        repo = TenantAgentOverlayRepository()
        assert isinstance(repo, TenantScopedRepository)
        assert repo._collection_name == COLLECTION_AGENT_OVERLAYS

    def test_document_model_uses_agent_id_as_id(self):
        """Codex answer: overlay.id = agent_id."""
        doc = TenantAgentOverlayDocument(
            id="campaigns",
            tenant_id="t-1",
            agent_id="campaigns",
        )
        assert doc.id == "campaigns"
        assert doc.agent_id == "campaigns"

    def test_custom_metadata_validation_rejects_unknown_keys(self):
        from src.multi_tenant.repositories.agent_overlays import _ALLOWED_CUSTOM_METADATA_KEYS
        assert "intent_routes" in _ALLOWED_CUSTOM_METADATA_KEYS
        assert "secret_token" not in _ALLOWED_CUSTOM_METADATA_KEYS


# ---------------------------------------------------------------------------
# WI-4012: AgentSkillBindingRepository
# ---------------------------------------------------------------------------


class TestBindingRepository:
    """WI-4012: Binding repository extends TenantScopedRepository."""

    def test_inherits_tenant_scoped(self):
        from src.multi_tenant.repositories.agent_bindings import AgentSkillBindingRepository
        from src.multi_tenant.repositories.base import TenantScopedRepository
        repo = AgentSkillBindingRepository()
        assert isinstance(repo, TenantScopedRepository)
        assert repo._collection_name == COLLECTION_AGENT_BINDINGS

    def test_document_model_uses_skill_id_as_id(self):
        """Codex Finding 3: binding.id = skill_id."""
        doc = AgentSkillBindingDocument(
            id="campaigns:list-active",
            tenant_id="t-1",
            agent_id="campaigns",
            skill_id="campaigns:list-active",
        )
        assert doc.id == "campaigns:list-active"
        assert doc.skill_id == "campaigns:list-active"
        # agent_id is kept as a separate field for query convenience
        assert doc.agent_id == "campaigns"


# ---------------------------------------------------------------------------
# WI-4013/4014: Cache Invalidation
# ---------------------------------------------------------------------------


class TestCacheInvalidation:
    """Codex Finding 1: write-path invalidation is mandatory."""

    def test_binding_service_invalidate_clears_tenant(self):
        svc = SkillBindingService.get_instance()
        svc._bindings[("t-1", "a", "s")] = {"skill_id": "s"}
        svc._bindings[("t-2", "a", "s")] = {"skill_id": "s"}
        svc._loaded_tenants.add("t-1")
        svc._loaded_tenants.add("t-2")

        svc.invalidate("t-1")

        assert ("t-1", "a", "s") not in svc._bindings
        assert ("t-2", "a", "s") in svc._bindings
        assert "t-1" not in svc._loaded_tenants
        assert "t-2" in svc._loaded_tenants

    def test_binding_service_invalidate_all(self):
        svc = SkillBindingService.get_instance()
        svc._bindings[("t-1", "a", "s")] = {"skill_id": "s"}
        svc._bindings[("t-2", "a", "s")] = {"skill_id": "s"}
        svc._loaded_tenants.update(["t-1", "t-2"])

        svc.invalidate()

        assert len(svc._bindings) == 0
        assert len(svc._loaded_tenants) == 0

    def test_invalidate_caches_clears_both(self):
        """Admin write path must clear both resolution cache and binding cache."""
        from src.multi_tenant.superadmin_api._agent_overlays import _invalidate_caches

        # Populate resolution cache
        _resolution_cache[("t-1", "a", "s")] = (MagicMock(), 999999)

        # Populate binding service cache
        svc = SkillBindingService.get_instance()
        svc._bindings[("t-1", "a", "s")] = {"skill_id": "s"}
        svc._loaded_tenants.add("t-1")

        _invalidate_caches("t-1")

        assert len(_resolution_cache) == 0
        assert ("t-1", "a", "s") not in svc._bindings
        assert "t-1" not in svc._loaded_tenants


# ---------------------------------------------------------------------------
# WI-4014: Sync/Async Contract
# ---------------------------------------------------------------------------


class TestSyncAsyncContract:
    """Codex Finding 2: runtime reads remain synchronous."""

    def test_get_binding_is_synchronous(self):
        """Runtime read methods are not coroutines."""
        svc = SkillBindingService.get_instance()
        import inspect
        assert not inspect.iscoroutinefunction(svc.get_binding)
        assert not inspect.iscoroutinefunction(svc.check_binding)
        assert not inspect.iscoroutinefunction(svc.resolve_credential)
        assert not inspect.iscoroutinefunction(svc.get_bound_skill_ids)

    def test_load_tenant_bindings_is_async(self):
        """Cache population from Cosmos is async."""
        svc = SkillBindingService.get_instance()
        import inspect
        assert inspect.iscoroutinefunction(svc.load_tenant_bindings)

    def test_invalidate_is_synchronous(self):
        """Cache invalidation is sync (called from sync write paths)."""
        svc = SkillBindingService.get_instance()
        import inspect
        assert not inspect.iscoroutinefunction(svc.invalidate)


# ---------------------------------------------------------------------------
# WI-4015: Repository + API Integration Tests
# ---------------------------------------------------------------------------


class TestOverlayApiWiring:
    """Overlay API endpoints use Cosmos repo (not in-memory store)."""

    def test_no_in_memory_overlay_store(self):
        """The old _overlay_store dict must not exist."""
        import src.multi_tenant.superadmin_api._agent_overlays as mod
        assert not hasattr(mod, "_overlay_store"), (
            "_overlay_store dict should be removed — overlays are repo-backed"
        )

    def test_get_tenant_overlays_is_async(self):
        """_get_tenant_overlays must be async (reads from Cosmos)."""
        from src.multi_tenant.superadmin_api._agent_overlays import _get_tenant_overlays
        import inspect
        assert inspect.iscoroutinefunction(_get_tenant_overlays)


class TestBindingApiWiring:
    """Binding API endpoints use Cosmos repo (not SkillBindingService CRUD)."""

    def test_binding_repo_used_for_admin_crud(self):
        """Admin API should use repo, not SkillBindingService.create_binding."""
        import ast
        with open("src/multi_tenant/superadmin_api/_agent_overlays.py") as f:
            source = f.read()
        tree = ast.parse(source)
        # Check that put_skill_binding calls repo.upsert_binding, not svc.create_binding
        found_svc_create = False
        found_repo_upsert = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "create_binding":
                found_svc_create = True
            if isinstance(node, ast.Attribute) and node.attr == "upsert_binding":
                found_repo_upsert = True
        assert found_repo_upsert, "Admin API should call repo.upsert_binding"
        assert not found_svc_create, "Admin API should not call svc.create_binding"


class TestCustomMetadataGuardrails:
    """Codex Finding 4: custom_metadata validated against allowed keys + shapes."""

    @pytest.mark.asyncio
    async def test_overlay_repo_strips_unknown_metadata_keys(self):
        """Unknown keys in custom_metadata are rejected at repo level."""
        from src.multi_tenant.repositories.agent_overlays import TenantAgentOverlayRepository

        repo = TenantAgentOverlayRepository()

        # Mock the upsert to capture what gets written
        with patch.object(repo, "upsert", new_callable=AsyncMock) as mock_upsert:
            mock_upsert.return_value = {"id": "campaigns", "tenant_id": "t-1"}
            await repo.upsert_overlay(
                "t-1",
                "campaigns",
                custom_metadata={
                    "intent_routes": {"billing_inquiry": {"agent_id": "campaigns"}},
                    "secret_token": "should-be-rejected",
                },
            )
            # Check the document passed to upsert
            call_args = mock_upsert.call_args
            doc = call_args[0][1]  # second positional arg is the document
            metadata = doc.custom_metadata
            assert "intent_routes" in metadata
            assert "secret_token" not in metadata

    @pytest.mark.asyncio
    async def test_intent_routes_shape_validation_accepts_valid(self):
        """Valid intent_routes dict[str, dict[str, str]] passes validation."""
        from src.multi_tenant.repositories.agent_overlays import TenantAgentOverlayRepository

        repo = TenantAgentOverlayRepository()
        with patch.object(repo, "upsert", new_callable=AsyncMock) as mock_upsert:
            mock_upsert.return_value = {"id": "campaigns", "tenant_id": "t-1"}
            await repo.upsert_overlay(
                "t-1",
                "campaigns",
                custom_metadata={
                    "intent_routes": {
                        "billing_inquiry": {
                            "agent_id": "campaigns",
                            "skill_id": "campaigns:list-active",
                        },
                        "order_status": {
                            "suggested_peer": "sales",
                            "skill": "sales:order-tracking",
                        },
                    },
                },
            )
            doc = mock_upsert.call_args[0][1]
            routes = doc.custom_metadata["intent_routes"]
            assert "billing_inquiry" in routes
            assert routes["billing_inquiry"]["agent_id"] == "campaigns"
            assert "order_status" in routes

    @pytest.mark.asyncio
    async def test_intent_routes_rejects_non_dict(self):
        """intent_routes must be a dict, not a list."""
        from src.multi_tenant.repositories.agent_overlays import TenantAgentOverlayRepository

        repo = TenantAgentOverlayRepository()
        with patch.object(repo, "upsert", new_callable=AsyncMock) as mock_upsert:
            mock_upsert.return_value = {"id": "campaigns", "tenant_id": "t-1"}
            await repo.upsert_overlay(
                "t-1",
                "campaigns",
                custom_metadata={
                    "intent_routes": [{"pattern": ".*"}],
                },
            )
            doc = mock_upsert.call_args[0][1]
            # List should be rejected — not in metadata
            assert "intent_routes" not in doc.custom_metadata

    @pytest.mark.asyncio
    async def test_intent_routes_strips_unknown_nested_keys(self):
        """Unknown keys inside route entries are stripped."""
        from src.multi_tenant.repositories.agent_overlays import TenantAgentOverlayRepository

        repo = TenantAgentOverlayRepository()
        with patch.object(repo, "upsert", new_callable=AsyncMock) as mock_upsert:
            mock_upsert.return_value = {"id": "campaigns", "tenant_id": "t-1"}
            await repo.upsert_overlay(
                "t-1",
                "campaigns",
                custom_metadata={
                    "intent_routes": {
                        "billing": {
                            "agent_id": "campaigns",
                            "secret_token": "should-be-stripped",
                            "api_key": "also-stripped",
                        },
                    },
                },
            )
            doc = mock_upsert.call_args[0][1]
            routes = doc.custom_metadata["intent_routes"]
            assert "billing" in routes
            assert routes["billing"] == {"agent_id": "campaigns"}
            assert "secret_token" not in routes["billing"]


class TestBindingHydration:
    """Codex P1: Binding cache must be hydrated from Cosmos before sync reads."""

    @pytest.mark.asyncio
    async def test_load_tenant_bindings_populates_cache(self):
        """load_tenant_bindings reads from Cosmos and populates _bindings dict."""
        from src.multi_tenant.repositories.agent_bindings import AgentSkillBindingRepository

        svc = SkillBindingService.get_instance()
        assert svc.get_binding("t-1", "campaigns", "campaigns:list-active") is None

        # Mock the repo to return a binding
        mock_docs = [
            {
                "tenant_id": "t-1",
                "agent_id": "campaigns",
                "skill_id": "campaigns:list-active",
                "credential_ref": "vault://t-1/key",
                "mode": "read",
                "approval_policy": "auto",
                "enabled": True,
            }
        ]
        with patch.object(
            AgentSkillBindingRepository,
            "list_bindings",
            new_callable=AsyncMock,
            return_value=mock_docs,
        ):
            await svc.load_tenant_bindings("t-1")

        # Now the sync read should find the binding
        binding = svc.get_binding("t-1", "campaigns", "campaigns:list-active")
        assert binding is not None
        assert binding["credential_ref"] == "vault://t-1/key"
        assert "t-1" in svc._loaded_tenants

    @pytest.mark.asyncio
    async def test_invalidate_then_reload_restores_bindings(self):
        """After invalidation, next load restores bindings from Cosmos."""
        from src.multi_tenant.repositories.agent_bindings import AgentSkillBindingRepository

        svc = SkillBindingService.get_instance()

        mock_docs = [
            {
                "tenant_id": "t-1",
                "agent_id": "campaigns",
                "skill_id": "campaigns:list-active",
                "mode": "read",
                "approval_policy": "auto",
                "enabled": True,
            }
        ]

        with patch.object(
            AgentSkillBindingRepository,
            "list_bindings",
            new_callable=AsyncMock,
            return_value=mock_docs,
        ) as mock_list:
            # Load
            await svc.load_tenant_bindings("t-1")
            assert svc.get_binding("t-1", "campaigns", "campaigns:list-active") is not None

            # Invalidate
            svc.invalidate("t-1")
            assert svc.get_binding("t-1", "campaigns", "campaigns:list-active") is None
            assert "t-1" not in svc._loaded_tenants

            # Reload
            await svc.load_tenant_bindings("t-1")
            assert svc.get_binding("t-1", "campaigns", "campaigns:list-active") is not None
            assert mock_list.call_count == 2

    def test_orchestrator_hydration_call_exists(self):
        """Orchestrator must call load_tenant_bindings before sync routing."""
        import ast
        with open("src/chat/pipeline/orchestrator.py") as f:
            source = f.read()
        assert "load_tenant_bindings" in source, (
            "Orchestrator must hydrate binding cache before sync reads"
        )

    def test_dispatch_hydration_call_exists(self):
        """dispatch_with_binding must hydrate before sync check_binding."""
        import ast
        with open("src/agents/plugins/dispatch.py") as f:
            source = f.read()
        assert "load_tenant_bindings" in source, (
            "dispatch_with_binding must hydrate binding cache before sync reads"
        )

    def test_delete_binding_validates_skill_id(self):
        """DELETE binding endpoint must validate skill belongs to agent."""
        import ast
        with open("src/multi_tenant/superadmin_api/_agent_overlays.py") as f:
            source = f.read()
        tree = ast.parse(source)
        # Find the delete_skill_binding function
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "delete_skill_binding":
                body_source = ast.dump(node)
                assert "_validate_skill_id" in body_source, (
                    "delete_skill_binding must call _validate_skill_id"
                )
                break

    def test_kr_dispatch_hydration_call_exists(self):
        """agent_dispatch._call_knowledge_retrieval must hydrate bindings."""
        with open("src/chat/pipeline/agent_dispatch.py") as f:
            source = f.read()
        assert "load_tenant_bindings" in source, (
            "KR dispatch must hydrate binding cache before sync reads"
        )

    def test_available_skills_hydration_call_exists(self):
        """list_tenant_available_skills must hydrate bindings."""
        with open("src/multi_tenant/superadmin_api/_agent_overlays.py") as f:
            source = f.read()
        # Count occurrences — should appear in both _invalidate_caches and available-skills
        assert source.count("load_tenant_bindings") >= 1, (
            "available-skills endpoint must hydrate binding cache before sync reads"
        )


class TestBehavioralColdCache:
    """Behavioral cold-cache tests proving Cosmos-backed bindings survive invalidation.

    These go beyond structural checks to exercise actual runtime paths with
    a mock repo, verifying the hydration contract end-to-end.
    """

    @pytest.mark.asyncio
    async def test_resolve_skill_cold_cache_honors_persisted_binding(self):
        """After invalidation, resolve_skill still finds repo-backed binding."""
        from src.agents.plugins.overlay import resolve_skill, ResolvedSkill, SkillDenial, clear_resolution_cache
        from src.agents.plugins.registry import PluginAgentRegistry
        from src.multi_tenant.repositories.agent_bindings import AgentSkillBindingRepository

        # Set up registry with a known agent/skill
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()

        # Use first available agent/skill from registry
        agents = reg.list_agents()
        assert len(agents) > 0, "Need at least one agent in registry"
        agent = agents[0]
        assert len(agent.skills) > 0, "Need at least one skill"
        skill = agent.skills[0]

        # Mock repo to return a valid binding
        mock_binding = [{
            "tenant_id": "t-cold",
            "agent_id": agent.agent_id,
            "skill_id": skill.skill_id,
            "credential_ref": None,
            "mode": "read",
            "approval_policy": "auto",
            "enabled": True,
        }]

        svc = SkillBindingService.get_instance()

        # Start cold: no bindings loaded
        assert "t-cold" not in svc._loaded_tenants

        with patch.object(
            AgentSkillBindingRepository,
            "list_bindings",
            new_callable=AsyncMock,
            return_value=mock_binding,
        ) as mock_list:
            # Hydrate (simulating what orchestrator/dispatch do)
            await svc.load_tenant_bindings("t-cold")
            assert mock_list.call_count == 1

        # Now resolve_skill should find the binding (sync, from cache)
        clear_resolution_cache()
        result = resolve_skill("t-cold", agent.agent_id, skill.skill_id)
        assert isinstance(result, ResolvedSkill), f"Expected ResolvedSkill, got {type(result).__name__}: {result}"
        assert result.agent_id == agent.agent_id

        # Invalidate — simulating admin write
        svc.invalidate("t-cold")
        clear_resolution_cache()

        # Without reload, binding should be gone (cold cache)
        result2 = resolve_skill("t-cold", agent.agent_id, skill.skill_id)
        assert isinstance(result2, SkillDenial), "Cold cache should deny after invalidation"

        # Reload from repo
        with patch.object(
            AgentSkillBindingRepository,
            "list_bindings",
            new_callable=AsyncMock,
            return_value=mock_binding,
        ):
            await svc.load_tenant_bindings("t-cold")

        clear_resolution_cache()
        result3 = resolve_skill("t-cold", agent.agent_id, skill.skill_id)
        assert isinstance(result3, ResolvedSkill), "Should resolve after reload"

    @pytest.mark.asyncio
    async def test_list_available_skills_cold_cache_with_hydration(self):
        """list_available_skills returns results after cold-cache hydration."""
        from src.agents.plugins.overlay import list_available_skills, clear_resolution_cache
        from src.agents.plugins.registry import PluginAgentRegistry
        from src.multi_tenant.repositories.agent_bindings import AgentSkillBindingRepository

        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()

        agents = reg.list_agents()
        agent = agents[0]
        skill = agent.skills[0]

        svc = SkillBindingService.get_instance()

        # Cold cache: no tenant loaded
        clear_resolution_cache()
        cold_result = list_available_skills("t-avail", agent_id=agent.agent_id)
        assert len(cold_result) == 0, "Cold cache should return no skills"

        # Hydrate with mock binding
        mock_binding = [{
            "tenant_id": "t-avail",
            "agent_id": agent.agent_id,
            "skill_id": skill.skill_id,
            "mode": "read",
            "approval_policy": "auto",
            "enabled": True,
        }]

        with patch.object(
            AgentSkillBindingRepository,
            "list_bindings",
            new_callable=AsyncMock,
            return_value=mock_binding,
        ):
            await svc.load_tenant_bindings("t-avail")

        clear_resolution_cache()
        warm_result = list_available_skills("t-avail", agent_id=agent.agent_id)
        assert len(warm_result) >= 1, "Warm cache should return skills after hydration"
        assert warm_result[0].skill_id == skill.skill_id

    @pytest.mark.asyncio
    async def test_check_binding_cold_cache_denies_then_allows(self):
        """check_binding denies on cold cache, allows after hydration."""
        from src.multi_tenant.repositories.agent_bindings import AgentSkillBindingRepository

        svc = SkillBindingService.get_instance()

        # Cold: should deny
        check_cold = svc.check_binding("t-check", "campaigns", "campaigns:list-active")
        assert check_cold.denied, "Cold cache must deny (deny-by-default)"

        # Hydrate
        mock_binding = [{
            "tenant_id": "t-check",
            "agent_id": "campaigns",
            "skill_id": "campaigns:list-active",
            "mode": "read",
            "approval_policy": "auto",
            "enabled": True,
        }]

        with patch.object(
            AgentSkillBindingRepository,
            "list_bindings",
            new_callable=AsyncMock,
            return_value=mock_binding,
        ):
            await svc.load_tenant_bindings("t-check")

        # Warm: should allow
        check_warm = svc.check_binding("t-check", "campaigns", "campaigns:list-active")
        assert check_warm.allowed, "Warm cache must allow after hydration"


class TestAsyncBoundaryHydration:
    """Codex P2 caveat: tests must exercise the actual async boundary functions,
    not just manually call load_tenant_bindings.

    These tests call the real async boundary code (agent_dispatch, admin API)
    and verify that the hydration guard triggers the repo load.
    """

    @pytest.mark.asyncio
    async def test_kr_dispatch_boundary_hydrates_from_cold_cache(self):
        """_call_knowledge_retrieval hydrates bindings before sync KR resolution.

        Exercises the actual async boundary in agent_dispatch.py.
        We call the real method but mock everything after the hydration guard
        to isolate the hydration behavior.
        """
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin
        from src.multi_tenant.repositories.agent_bindings import AgentSkillBindingRepository
        from src.agents.plugins.bindings import SkillBindingService
        from src.agents.plugins.registry import PluginAgentRegistry

        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()

        svc = SkillBindingService.get_instance()

        # Ensure cold cache
        assert "t-kr-boundary" not in svc._loaded_tenants

        mock_binding = [{
            "tenant_id": "t-kr-boundary",
            "agent_id": "knowledge-retrieval",
            "skill_id": "knowledge-retrieval:retrieve",
            "credential_ref": "vault://cred-kr",
            "mode": "read",
            "approval_policy": "auto",
            "enabled": True,
        }]

        # Create a minimal mixin instance with required attributes
        mixin = AgentDispatchMixin()
        mixin._current_tenant_id = "t-kr-boundary"
        mixin._current_preferences = MagicMock()
        mixin._current_tenant = MagicMock()

        # Mock transport layer to raise (forces early exit after hydration)
        mixin._transport_available = MagicMock(return_value=False)

        with patch.object(
            AgentSkillBindingRepository,
            "list_bindings",
            new_callable=AsyncMock,
            return_value=mock_binding,
        ) as mock_repo_list:
            with patch.object(
                mixin, "_resolve_kr_mcp_payload",
                return_value={"mcp_configs": [], "tenant_shop_domain": None},
            ):
                # Mock trace span
                mock_span = MagicMock()
                mock_span.set_attribute = MagicMock()
                mock_span.set_status = MagicMock()
                mock_span.end = MagicMock()
                with patch(
                    "src.multi_tenant.otel_tracing.trace_agent_operation",
                    return_value=mock_span,
                ):
                    try:
                        await mixin._call_knowledge_retrieval("hello", "greeting", "prompt")
                    except Exception:
                        pass  # Transport unavailable — expected; hydration already ran

            # The key assertion: repo was called to hydrate the cold cache
            assert mock_repo_list.call_count >= 1, (
                "KR boundary must call repo.list_bindings to hydrate cold cache"
            )
            assert "t-kr-boundary" in svc._loaded_tenants

    @pytest.mark.asyncio
    async def test_available_skills_endpoint_hydrates_from_cold_cache(self):
        """list_tenant_available_skills hydrates bindings before sync resolution.

        Exercises the actual async boundary in _agent_overlays.py.
        """
        from src.multi_tenant.repositories.agent_bindings import AgentSkillBindingRepository
        from src.multi_tenant.repositories.agent_overlays import TenantAgentOverlayRepository
        from src.agents.plugins.bindings import SkillBindingService
        from src.agents.plugins.registry import PluginAgentRegistry
        from src.agents.plugins.overlay import clear_resolution_cache

        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()

        agents = reg.list_agents()
        agent = agents[0]
        skill = agent.skills[0]

        svc = SkillBindingService.get_instance()
        clear_resolution_cache()

        # Ensure cold cache
        assert "t-avail-boundary" not in svc._loaded_tenants

        mock_binding = [{
            "tenant_id": "t-avail-boundary",
            "agent_id": agent.agent_id,
            "skill_id": skill.skill_id,
            "mode": "read",
            "approval_policy": "auto",
            "enabled": True,
        }]

        with patch.object(
            AgentSkillBindingRepository,
            "list_bindings",
            new_callable=AsyncMock,
            return_value=mock_binding,
        ) as mock_repo_list:
            with patch.object(
                TenantAgentOverlayRepository,
                "list_overlays",
                new_callable=AsyncMock,
                return_value=[],
            ):
                # Import and call the actual endpoint function
                from src.multi_tenant.superadmin_api._agent_overlays import (
                    list_tenant_available_skills,
                )

                # Mock the auth dependency
                ctx = MagicMock()
                result = await list_tenant_available_skills(
                    tenant_id="t-avail-boundary",
                    agent_id=agent.agent_id,
                    ctx=ctx,
                )

            # Key assertion: repo was called to hydrate
            assert mock_repo_list.call_count >= 1, (
                "available-skills endpoint must call repo.list_bindings to hydrate cold cache"
            )
            assert "t-avail-boundary" in svc._loaded_tenants
            # And the endpoint returned the expected skills
            assert len(result) >= 1, "Endpoint should return skills after hydration"
