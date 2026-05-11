"""Tests for admin agent marketplace API (SPEC-1865).

Covers: list (peer-only, tier-gate, category filter, install status),
install (happy path, already installed, tier-gated, compensating cleanup),
uninstall (happy path, not installed).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@dataclass
class FakeSkill:
    skill_id: str
    agent_id: str
    skill_name: str
    display_name: str
    description: str = ""
    mode: str = "read"


@dataclass
class FakeAgent:
    agent_id: str
    display_name: str
    description: str
    category: str
    tier_gate: str = "free"
    agent_kind: str = "peer"
    capabilities: tuple = ()
    skills: tuple = ()
    status: str = "available"
    is_external: bool = False


def _make_peer(agent_id="sales_agent", tier_gate="free", category="sales", skills=None):
    if skills is None:
        skills = (
            FakeSkill(f"{agent_id}:search", agent_id, "search", "Search"),
            FakeSkill(f"{agent_id}:cart", agent_id, "cart", "Cart"),
        )
    return FakeAgent(
        agent_id=agent_id,
        display_name=agent_id.replace("_", " ").title(),
        description=f"Test {agent_id}",
        category=category,
        tier_gate=tier_gate,
        agent_kind="peer",
        skills=skills,
    )


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "tenant-001"
    ctx.tier = MagicMock()
    ctx.tier.value = "professional"
    return ctx


@pytest.fixture
def mock_overlay_repo():
    repo = MagicMock()
    repo.get_overlay = AsyncMock(return_value=None)
    repo.upsert_overlay = AsyncMock()
    repo.delete_overlay = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def mock_binding_repo():
    repo = MagicMock()
    repo.upsert_binding = AsyncMock()
    repo.delete_binding = AsyncMock(return_value=True)
    repo.list_bindings = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_registry():
    reg = MagicMock()
    reg.get_peer_agents.return_value = [_make_peer()]
    reg.get.return_value = _make_peer()
    return reg


# ---------------------------------------------------------------------------
# Tests: list_marketplace_agents
# ---------------------------------------------------------------------------


class TestListMarketplace:
    @pytest.mark.asyncio
    async def test_lists_peer_agents(self, mock_ctx, mock_registry, mock_overlay_repo):
        with (
            patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=mock_registry),
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
        ):
            from src.multi_tenant.admin_marketplace_api import list_marketplace_agents

            result = await list_marketplace_agents(category=None, ctx=mock_ctx)

            assert result.total == 1
            assert result.agents[0].agent_id == "sales_agent"
            assert result.agents[0].installed is False

    @pytest.mark.asyncio
    async def test_marks_installed_agents(self, mock_ctx, mock_registry, mock_overlay_repo):
        mock_overlay_repo.get_overlay.return_value = {"agent_id": "sales_agent"}

        with (
            patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=mock_registry),
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
        ):
            from src.multi_tenant.admin_marketplace_api import list_marketplace_agents

            result = await list_marketplace_agents(category=None, ctx=mock_ctx)

            assert result.agents[0].installed is True

    @pytest.mark.asyncio
    async def test_filters_by_category(self, mock_ctx, mock_registry, mock_overlay_repo):
        mock_registry.get_peer_agents.return_value = [
            _make_peer("sales_agent", category="sales"),
            _make_peer("support_agent", category="support"),
        ]

        with (
            patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=mock_registry),
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
        ):
            from src.multi_tenant.admin_marketplace_api import list_marketplace_agents

            result = await list_marketplace_agents(category="support", ctx=mock_ctx)

            assert result.total == 1
            assert result.agents[0].agent_id == "support_agent"

    @pytest.mark.asyncio
    async def test_hides_tier_gated_agents(self, mock_ctx, mock_registry, mock_overlay_repo):
        mock_ctx.tier.value = "starter"
        mock_registry.get_peer_agents.return_value = [
            _make_peer("basic_agent", tier_gate="free"),
            _make_peer("pro_agent", tier_gate="professional"),
        ]

        with (
            patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=mock_registry),
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
        ):
            from src.multi_tenant.admin_marketplace_api import list_marketplace_agents

            result = await list_marketplace_agents(category=None, ctx=mock_ctx)

            assert result.total == 1
            assert result.agents[0].agent_id == "basic_agent"


# ---------------------------------------------------------------------------
# Tests: install_agent
# ---------------------------------------------------------------------------


class TestInstallAgent:
    @pytest.mark.asyncio
    async def test_install_success(self, mock_ctx, mock_registry, mock_overlay_repo, mock_binding_repo):
        with (
            patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=mock_registry),
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
            patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=mock_binding_repo),
        ):
            from src.multi_tenant.admin_marketplace_api import install_agent

            result = await install_agent("sales_agent", ctx=mock_ctx)

            assert result.agent_id == "sales_agent"
            assert result.overlay_created is True
            assert result.bindings_created == 2
            assert result.bindings_failed == 0
            mock_overlay_repo.upsert_overlay.assert_called_once()
            assert mock_binding_repo.upsert_binding.call_count == 2

    @pytest.mark.asyncio
    async def test_install_already_installed(self, mock_ctx, mock_registry, mock_overlay_repo, mock_binding_repo):
        mock_overlay_repo.get_overlay.return_value = {"agent_id": "sales_agent"}

        with (
            patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=mock_registry),
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
            patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=mock_binding_repo),
        ):
            from fastapi import HTTPException
            from src.multi_tenant.admin_marketplace_api import install_agent

            with pytest.raises(HTTPException) as exc_info:
                await install_agent("sales_agent", ctx=mock_ctx)
            assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_install_agent_not_found(self, mock_ctx, mock_registry, mock_overlay_repo, mock_binding_repo):
        mock_registry.get.return_value = None

        with (
            patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=mock_registry),
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
            patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=mock_binding_repo),
        ):
            from fastapi import HTTPException
            from src.multi_tenant.admin_marketplace_api import install_agent

            with pytest.raises(HTTPException) as exc_info:
                await install_agent("nonexistent", ctx=mock_ctx)
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_install_tier_gated(self, mock_ctx, mock_registry, mock_overlay_repo, mock_binding_repo):
        mock_ctx.tier.value = "starter"
        mock_registry.get.return_value = _make_peer("pro_agent", tier_gate="professional")

        with (
            patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=mock_registry),
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
            patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=mock_binding_repo),
        ):
            from fastapi import HTTPException
            from src.multi_tenant.admin_marketplace_api import install_agent

            with pytest.raises(HTTPException) as exc_info:
                await install_agent("pro_agent", ctx=mock_ctx)
            assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_install_compensating_cleanup(self, mock_ctx, mock_registry, mock_overlay_repo, mock_binding_repo):
        """All bindings fail → overlay is cleaned up."""
        mock_binding_repo.upsert_binding.side_effect = RuntimeError("cosmos error")

        with (
            patch("src.multi_tenant.admin_marketplace_api._get_registry", return_value=mock_registry),
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
            patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=mock_binding_repo),
        ):
            from fastapi import HTTPException
            from src.multi_tenant.admin_marketplace_api import install_agent

            with pytest.raises(HTTPException) as exc_info:
                await install_agent("sales_agent", ctx=mock_ctx)
            assert exc_info.value.status_code == 500
            mock_overlay_repo.delete_overlay.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: uninstall_agent
# ---------------------------------------------------------------------------


class TestUninstallAgent:
    @pytest.mark.asyncio
    async def test_uninstall_success(self, mock_ctx, mock_overlay_repo, mock_binding_repo):
        mock_overlay_repo.get_overlay.return_value = {"agent_id": "sales_agent"}
        mock_binding_repo.list_bindings.return_value = [
            {"skill_id": "sales_agent:search"},
            {"skill_id": "sales_agent:cart"},
        ]

        with (
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
            patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=mock_binding_repo),
        ):
            from src.multi_tenant.admin_marketplace_api import uninstall_agent

            result = await uninstall_agent("sales_agent", ctx=mock_ctx)

            assert result.agent_id == "sales_agent"
            assert result.overlay_removed is True
            assert result.bindings_removed == 2

    @pytest.mark.asyncio
    async def test_uninstall_not_installed(self, mock_ctx, mock_overlay_repo, mock_binding_repo):
        mock_overlay_repo.get_overlay.return_value = None

        with (
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
            patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=mock_binding_repo),
        ):
            from fastapi import HTTPException
            from src.multi_tenant.admin_marketplace_api import uninstall_agent

            with pytest.raises(HTTPException) as exc_info:
                await uninstall_agent("sales_agent", ctx=mock_ctx)
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_uninstall_fail_closed_on_binding_error(self, mock_ctx, mock_overlay_repo, mock_binding_repo):
        """Uninstall aborts and preserves overlay if any binding deletion fails."""
        mock_overlay_repo.get_overlay.return_value = {"agent_id": "sales_agent"}
        mock_binding_repo.list_bindings.return_value = [
            {"skill_id": "sales_agent:search"},
            {"skill_id": "sales_agent:cart"},
        ]
        # First binding succeeds, second fails
        mock_binding_repo.delete_binding.side_effect = [True, RuntimeError("cosmos")]

        with (
            patch("src.multi_tenant.admin_marketplace_api._get_overlay_repo", return_value=mock_overlay_repo),
            patch("src.multi_tenant.admin_marketplace_api._get_binding_repo", return_value=mock_binding_repo),
        ):
            from fastapi import HTTPException
            from src.multi_tenant.admin_marketplace_api import uninstall_agent

            with pytest.raises(HTTPException) as exc_info:
                await uninstall_agent("sales_agent", ctx=mock_ctx)
            assert exc_info.value.status_code == 500
            assert "Uninstall aborted" in exc_info.value.detail
            # Overlay must NOT be deleted
            mock_overlay_repo.delete_overlay.assert_not_called()
