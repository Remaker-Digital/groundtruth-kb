# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPEC-1865 marketplace discovery and installation coverage."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from fastapi import HTTPException


@dataclass(frozen=True)
class FakeSkill:
    skill_id: str
    agent_id: str
    skill_name: str
    display_name: str
    mode: str = "read"


@dataclass(frozen=True)
class FakeAgent:
    agent_id: str
    display_name: str
    description: str
    category: str
    tier_gate: str = "free"
    agent_kind: str = "peer"
    capabilities: tuple[str, ...] = ()
    skills: tuple[FakeSkill, ...] = ()


def _skill(agent_id: str, name: str, mode: str = "read") -> FakeSkill:
    return FakeSkill(
        skill_id=f"{agent_id}:{name}",
        agent_id=agent_id,
        skill_name=name,
        display_name=name.replace("-", " ").title(),
        mode=mode,
    )


def _agent(
    agent_id: str = "sales_agent",
    *,
    tier_gate: str = "free",
    category: str = "sales",
    agent_kind: str = "peer",
    capabilities: tuple[str, ...] = ("catalog", "cart"),
    skills: tuple[FakeSkill, ...] | None = None,
) -> FakeAgent:
    if skills is None:
        skills = (_skill(agent_id, "search"), _skill(agent_id, "cart", mode="mutate"))

    return FakeAgent(
        agent_id=agent_id,
        display_name=agent_id.replace("_", " ").title(),
        description=f"{agent_id} marketplace entry",
        category=category,
        tier_gate=tier_gate,
        agent_kind=agent_kind,
        capabilities=capabilities,
        skills=skills,
    )


@pytest.fixture
def tenant_ctx():
    return SimpleNamespace(tenant_id="tenant-1865", tier=SimpleNamespace(value="starter"))


@pytest.fixture
def overlay_repo():
    repo = MagicMock()
    repo.get_overlay = AsyncMock(return_value=None)
    repo.upsert_overlay = AsyncMock()
    repo.delete_overlay = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def binding_repo():
    repo = MagicMock()
    repo.upsert_binding = AsyncMock()
    repo.delete_binding = AsyncMock(return_value=True)
    repo.list_bindings = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def registry():
    reg = MagicMock()
    reg.get.return_value = _agent()
    reg.get_peer_agents.return_value = [_agent()]
    return reg


@pytest.mark.asyncio
async def test_listing_uses_peer_registry_and_reports_tier_install_state(
    tenant_ctx,
    overlay_repo,
    registry,
):
    basic = _agent("sales_agent", tier_gate="free", category="sales")
    gated = _agent("campaigns_agent", tier_gate="professional", category="marketing")
    core = _agent("gateway_agent", tier_gate="free", agent_kind="core")
    registry.get_peer_agents.return_value = [basic, gated]
    registry.get_core_agents.return_value = [core]

    async def get_overlay(_tenant_id: str, agent_id: str):
        return {"agent_id": agent_id} if agent_id == "sales_agent" else None

    overlay_repo.get_overlay.side_effect = get_overlay

    with (
        patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=registry),
        patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=overlay_repo),
    ):
        from src.multi_tenant.admin_marketplace_api import list_marketplace_agents

        result = await list_marketplace_agents(category=None, ctx=tenant_ctx)

    registry.get_peer_agents.assert_called_once_with()
    registry.get_core_agents.assert_not_called()
    assert result.total == 1
    assert result.agents[0].agent_id == "sales_agent"
    assert result.agents[0].installed is True
    assert result.agents[0].skill_count == 2
    assert result.agents[0].capabilities == ["catalog", "cart"]


@pytest.mark.asyncio
async def test_install_creates_enabled_overlay_and_registry_skill_bindings(
    tenant_ctx,
    overlay_repo,
    binding_repo,
    registry,
):
    agent = _agent(
        "sales_agent",
        skills=(
            _skill("sales_agent", "search", mode="read"),
            _skill("sales_agent", "cart", mode="mutate"),
        ),
    )
    registry.get.return_value = agent

    with (
        patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=registry),
        patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=overlay_repo),
        patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=binding_repo),
        patch("src.multi_tenant.admin_marketplace_api._invalidate_caches") as invalidate_caches,
    ):
        from src.multi_tenant.admin_marketplace_api import install_agent

        result = await install_agent("sales_agent", ctx=tenant_ctx)

    assert result.bindings_created == 2
    assert result.bindings_failed == 0
    overlay_repo.upsert_overlay.assert_awaited_once_with(
        "tenant-1865",
        "sales_agent",
        enabled=True,
    )
    binding_repo.upsert_binding.assert_has_awaits(
        [
            call("tenant-1865", "sales_agent", "sales_agent:search", mode="read", enabled=True),
            call("tenant-1865", "sales_agent", "sales_agent:cart", mode="mutate", enabled=True),
        ]
    )
    invalidate_caches.assert_called_once_with("tenant-1865")


@pytest.mark.asyncio
async def test_install_partial_binding_failure_preserves_overlay_and_reports_counts(
    tenant_ctx,
    overlay_repo,
    binding_repo,
    registry,
):
    registry.get.return_value = _agent(
        "sales_agent",
        skills=(
            _skill("sales_agent", "search", mode="read"),
            _skill("sales_agent", "cart", mode="mutate"),
        ),
    )
    binding_repo.upsert_binding.side_effect = [None, RuntimeError("cosmos write failed")]

    with (
        patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=registry),
        patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=overlay_repo),
        patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=binding_repo),
        patch("src.multi_tenant.admin_marketplace_api._invalidate_caches") as invalidate_caches,
    ):
        from src.multi_tenant.admin_marketplace_api import install_agent

        result = await install_agent("sales_agent", ctx=tenant_ctx)

    assert result.overlay_created is True
    assert result.bindings_created == 1
    assert result.bindings_failed == 1
    overlay_repo.delete_overlay.assert_not_called()
    invalidate_caches.assert_called_once_with("tenant-1865")


@pytest.mark.asyncio
async def test_install_full_binding_failure_removes_overlay_and_skips_cache_invalidation(
    tenant_ctx,
    overlay_repo,
    binding_repo,
    registry,
):
    binding_repo.upsert_binding.side_effect = RuntimeError("cosmos write failed")

    with (
        patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=registry),
        patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=overlay_repo),
        patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=binding_repo),
        patch("src.multi_tenant.admin_marketplace_api._invalidate_caches") as invalidate_caches,
    ):
        from src.multi_tenant.admin_marketplace_api import install_agent

        with pytest.raises(HTTPException) as exc_info:
            await install_agent("sales_agent", ctx=tenant_ctx)

    assert exc_info.value.status_code == 500
    overlay_repo.delete_overlay.assert_awaited_once_with("tenant-1865", "sales_agent")
    invalidate_caches.assert_not_called()


def test_invalidate_caches_clears_resolution_cache_and_tenant_bindings():
    binding_service = MagicMock()

    with (
        patch("src.agents.plugins.overlay.clear_resolution_cache") as clear_resolution_cache,
        patch(
            "src.agents.plugins.bindings.SkillBindingService.get_instance",
            return_value=binding_service,
        ),
    ):
        from src.multi_tenant.admin_marketplace_api import _invalidate_caches

        _invalidate_caches("tenant-1865")

    clear_resolution_cache.assert_called_once_with()
    binding_service.invalidate.assert_called_once_with("tenant-1865")


@pytest.mark.asyncio
async def test_uninstall_removes_bindings_then_overlay_and_invalidates_cache(
    tenant_ctx,
    overlay_repo,
    binding_repo,
):
    overlay_repo.get_overlay.return_value = {"agent_id": "sales_agent"}
    binding_repo.list_bindings.return_value = [
        {"skill_id": "sales_agent:search"},
        {"skill_id": "sales_agent:cart"},
    ]

    with (
        patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=overlay_repo),
        patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=binding_repo),
        patch("src.multi_tenant.admin_marketplace_api._invalidate_caches") as invalidate_caches,
    ):
        from src.multi_tenant.admin_marketplace_api import uninstall_agent

        result = await uninstall_agent("sales_agent", ctx=tenant_ctx)

    binding_repo.delete_binding.assert_has_awaits(
        [
            call("tenant-1865", "sales_agent:search"),
            call("tenant-1865", "sales_agent:cart"),
        ]
    )
    overlay_repo.delete_overlay.assert_awaited_once_with("tenant-1865", "sales_agent")
    invalidate_caches.assert_called_once_with("tenant-1865")
    assert result.overlay_removed is True
    assert result.bindings_removed == 2


@pytest.mark.asyncio
async def test_uninstall_fails_closed_and_preserves_overlay_when_binding_delete_fails(
    tenant_ctx,
    overlay_repo,
    binding_repo,
):
    overlay_repo.get_overlay.return_value = {"agent_id": "sales_agent"}
    binding_repo.list_bindings.return_value = [
        {"skill_id": "sales_agent:search"},
        {"skill_id": "sales_agent:cart"},
    ]
    binding_repo.delete_binding.side_effect = [True, RuntimeError("cosmos delete failed")]

    with (
        patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=overlay_repo),
        patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=binding_repo),
        patch("src.multi_tenant.admin_marketplace_api._invalidate_caches") as invalidate_caches,
    ):
        from src.multi_tenant.admin_marketplace_api import uninstall_agent

        with pytest.raises(HTTPException) as exc_info:
            await uninstall_agent("sales_agent", ctx=tenant_ctx)

    assert exc_info.value.status_code == 500
    assert "Overlay preserved" in exc_info.value.detail
    overlay_repo.delete_overlay.assert_not_called()
    invalidate_caches.assert_not_called()
