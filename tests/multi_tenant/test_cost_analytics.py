"""Tests for cost analytics API (CA-01 to CA-18).

Covers the HV-2 cost/unit economics endpoints:
    - GET /api/superadmin/costs          — Cross-tenant cost overview
    - GET /api/superadmin/costs/{tenant}  — Per-tenant cost breakdown
    - Cost calculation logic
    - Edge cases: zero conversations, zero articles, missing tenants

Test plan reference: §5.11 (Cost Analytics)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.multi_tenant.cost_analytics import (
    CostBreakdown,
    CostOverview,
    TenantCostProfile,
    _AI_INPUT_COST_PER_1K,
    _AI_OUTPUT_COST_PER_1K,
    _CONTAINER_APPS_BASE_MONTHLY,
    _COSMOS_COST_PER_100K_RU,
    _RU_PER_ARTICLE,
    _RU_PER_CONVERSATION,
    _STORAGE_COST_PER_ARTICLE,
    _calculate_cost,
    get_cost_overview,
    get_tenant_cost,
)


# ---------------------------------------------------------------------------
# CA-01 to CA-06: Cost calculation logic
# ---------------------------------------------------------------------------


class TestCalculateCost:
    """Unit tests for the _calculate_cost helper."""

    def test_ca01_zero_usage(self):
        """CA-01: Zero usage produces zero costs (except compute share)."""
        result = _calculate_cost(
            conversation_count=0,
            input_tokens=0,
            output_tokens=0,
            article_count=0,
            compute_share=0.0,
        )
        assert isinstance(result, CostBreakdown)
        assert result.ai_tokens == 0.0
        assert result.cosmos_db == 0.0
        assert result.storage == 0.0
        assert result.compute == 0.0
        assert result.total == 0.0

    def test_ca02_ai_token_cost(self):
        """CA-02: AI token cost is calculated correctly."""
        result = _calculate_cost(
            conversation_count=0,
            input_tokens=10_000,
            output_tokens=5_000,
            article_count=0,
            compute_share=0.0,
        )
        expected_ai = (10_000 / 1000) * _AI_INPUT_COST_PER_1K + (5_000 / 1000) * _AI_OUTPUT_COST_PER_1K
        assert result.ai_tokens == round(expected_ai, 4)
        assert result.cosmos_db == 0.0
        assert result.storage == 0.0
        assert result.total == result.ai_tokens

    def test_ca03_cosmos_db_cost(self):
        """CA-03: Cosmos DB RU cost from conversations and articles."""
        result = _calculate_cost(
            conversation_count=100,
            input_tokens=0,
            output_tokens=0,
            article_count=50,
            compute_share=0.0,
        )
        total_ru = 100 * _RU_PER_CONVERSATION + 50 * _RU_PER_ARTICLE
        expected_cosmos = (total_ru / 100_000) * _COSMOS_COST_PER_100K_RU
        assert result.cosmos_db == round(expected_cosmos, 4)

    def test_ca04_storage_cost(self):
        """CA-04: Storage cost is per-article."""
        result = _calculate_cost(
            conversation_count=0,
            input_tokens=0,
            output_tokens=0,
            article_count=200,
            compute_share=0.0,
        )
        expected_storage = 200 * _STORAGE_COST_PER_ARTICLE
        assert result.storage == round(expected_storage, 4)

    def test_ca05_compute_share(self):
        """CA-05: Compute cost is proportional to share."""
        result = _calculate_cost(
            conversation_count=0,
            input_tokens=0,
            output_tokens=0,
            article_count=0,
            compute_share=0.5,
        )
        expected_compute = _CONTAINER_APPS_BASE_MONTHLY * 0.5
        assert result.compute == round(expected_compute, 4)

    def test_ca06_total_is_sum(self):
        """CA-06: Total equals sum of all cost components."""
        result = _calculate_cost(
            conversation_count=50,
            input_tokens=5_000,
            output_tokens=2_000,
            article_count=30,
            compute_share=0.25,
        )
        expected_total = result.ai_tokens + result.cosmos_db + result.storage + result.compute
        assert result.total == pytest.approx(expected_total, abs=0.0002)


# ---------------------------------------------------------------------------
# CA-07 to CA-12: Cross-tenant cost overview endpoint
# ---------------------------------------------------------------------------


class TestGetCostOverview:
    """Tests for GET /api/superadmin/costs."""

    @pytest.mark.asyncio
    async def test_ca07_empty_platform(self):
        """CA-07: Empty platform returns zero totals."""
        with patch("src.multi_tenant.repositories.TenantRepository") as mock_tenant_cls:
            mock_repo = AsyncMock()
            mock_repo.list_all_active.return_value = []
            mock_tenant_cls.return_value = mock_repo

            result = await get_cost_overview(days=30)

        assert isinstance(result, CostOverview)
        assert result.total_tenants == 0
        assert result.total_conversations == 0
        assert result.total_platform_cost == 0.0
        assert result.tenants == []

    @pytest.mark.asyncio
    async def test_ca08_single_tenant(self):
        """CA-08: Single tenant gets 100% compute share."""
        tenant_doc = {"tenant_id": "t1", "tier": "professional"}

        with (
            patch("src.multi_tenant.repositories.TenantRepository") as mock_tenant_cls,
            patch("src.multi_tenant.repositories.ConversationRepository") as mock_conv_cls,
            patch("src.multi_tenant.repositories.UsageRepository") as mock_usage_cls,
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository") as mock_kb_cls,
        ):
            mock_tenant = AsyncMock()
            mock_tenant.list_all_active.return_value = [tenant_doc]
            mock_tenant_cls.return_value = mock_tenant

            mock_conv = AsyncMock()
            mock_conv.count_in_period.return_value = 10
            mock_conv_cls.return_value = mock_conv

            mock_usage = AsyncMock()
            mock_usage.get_period_summary.return_value = {
                "total_input_tokens": 5000,
                "total_output_tokens": 2000,
            }
            mock_usage_cls.return_value = mock_usage

            mock_kb = AsyncMock()
            mock_kb.count.return_value = 20
            mock_kb_cls.return_value = mock_kb

            result = await get_cost_overview(days=30)

        assert result.total_tenants == 1
        assert result.total_conversations == 10
        assert len(result.tenants) == 1
        assert result.tenants[0].tenant_id == "t1"
        assert result.tenants[0].cost_share_pct == 100.0

    @pytest.mark.asyncio
    async def test_ca09_multi_tenant_share(self):
        """CA-09: Multiple tenants split compute share by conversation count."""
        tenants = [
            {"tenant_id": "t1", "tier": "starter"},
            {"tenant_id": "t2", "tier": "professional"},
        ]

        call_count = {"conv": 0}

        async def mock_count_in_period(tenant_id, since, until):
            if tenant_id == "t1":
                return 30
            return 70

        async def mock_get_period_summary(tenant_id, since, until):
            return {"total_input_tokens": 1000, "total_output_tokens": 500}

        with (
            patch("src.multi_tenant.repositories.TenantRepository") as mock_tenant_cls,
            patch("src.multi_tenant.repositories.ConversationRepository") as mock_conv_cls,
            patch("src.multi_tenant.repositories.UsageRepository") as mock_usage_cls,
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository") as mock_kb_cls,
        ):
            mock_tenant = AsyncMock()
            mock_tenant.list_all_active.return_value = tenants
            mock_tenant_cls.return_value = mock_tenant

            mock_conv = AsyncMock()
            mock_conv.count_in_period = mock_count_in_period
            mock_conv_cls.return_value = mock_conv

            mock_usage = AsyncMock()
            mock_usage.get_period_summary = mock_get_period_summary
            mock_usage_cls.return_value = mock_usage

            mock_kb = AsyncMock()
            mock_kb.count.return_value = 5
            mock_kb_cls.return_value = mock_kb

            result = await get_cost_overview(days=30)

        assert result.total_tenants == 2
        assert result.total_conversations == 100

        # t1 has 30% share, t2 has 70%
        t1_profile = next(p for p in result.tenants if p.tenant_id == "t1")
        t2_profile = next(p for p in result.tenants if p.tenant_id == "t2")
        assert t1_profile.cost_share_pct == 30.0
        assert t2_profile.cost_share_pct == 70.0

    @pytest.mark.asyncio
    async def test_ca10_cost_by_tier(self):
        """CA-10: Costs are grouped by subscription tier."""
        tenants = [
            {"tenant_id": "t1", "tier": "starter"},
            {"tenant_id": "t2", "tier": "professional"},
            {"tenant_id": "t3", "tier": "starter"},
        ]

        with (
            patch("src.multi_tenant.repositories.TenantRepository") as mock_tenant_cls,
            patch("src.multi_tenant.repositories.ConversationRepository") as mock_conv_cls,
            patch("src.multi_tenant.repositories.UsageRepository") as mock_usage_cls,
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository") as mock_kb_cls,
        ):
            mock_tenant = AsyncMock()
            mock_tenant.list_all_active.return_value = tenants
            mock_tenant_cls.return_value = mock_tenant

            mock_conv = AsyncMock()
            mock_conv.count_in_period.return_value = 10
            mock_conv_cls.return_value = mock_conv

            mock_usage = AsyncMock()
            mock_usage.get_period_summary.return_value = {
                "total_input_tokens": 1000,
                "total_output_tokens": 500,
            }
            mock_usage_cls.return_value = mock_usage

            mock_kb = AsyncMock()
            mock_kb.count.return_value = 5
            mock_kb_cls.return_value = mock_kb

            result = await get_cost_overview(days=30)

        assert "starter" in result.cost_by_tier
        assert "professional" in result.cost_by_tier
        # 2 starter tenants, 1 professional
        assert result.cost_by_tier["starter"] > result.cost_by_tier["professional"]

    @pytest.mark.asyncio
    async def test_ca11_tenant_list_failure(self):
        """CA-11: Tenant list failure returns empty overview."""
        with patch("src.multi_tenant.repositories.TenantRepository") as mock_cls:
            mock_cls.return_value.list_all_active.side_effect = Exception("DB down")

            result = await get_cost_overview(days=30)

        assert result.total_tenants == 0
        assert result.total_platform_cost == 0.0

    @pytest.mark.asyncio
    async def test_ca12_avg_cost_per_conversation(self):
        """CA-12: Average cost per conversation is computed correctly."""
        tenant_doc = {"tenant_id": "t1", "tier": "starter"}

        with (
            patch("src.multi_tenant.repositories.TenantRepository") as mock_tenant_cls,
            patch("src.multi_tenant.repositories.ConversationRepository") as mock_conv_cls,
            patch("src.multi_tenant.repositories.UsageRepository") as mock_usage_cls,
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository") as mock_kb_cls,
        ):
            mock_tenant = AsyncMock()
            mock_tenant.list_all_active.return_value = [tenant_doc]
            mock_tenant_cls.return_value = mock_tenant

            mock_conv = AsyncMock()
            mock_conv.count_in_period.return_value = 50
            mock_conv_cls.return_value = mock_conv

            mock_usage = AsyncMock()
            mock_usage.get_period_summary.return_value = {
                "total_input_tokens": 10000,
                "total_output_tokens": 5000,
            }
            mock_usage_cls.return_value = mock_usage

            mock_kb = AsyncMock()
            mock_kb.count.return_value = 10
            mock_kb_cls.return_value = mock_kb

            result = await get_cost_overview(days=30)

        assert result.avg_cost_per_conversation == round(
            result.total_platform_cost / 50, 4,
        )


# ---------------------------------------------------------------------------
# CA-13 to CA-18: Per-tenant cost breakdown endpoint
# ---------------------------------------------------------------------------


class TestGetTenantCost:
    """Tests for GET /api/superadmin/costs/{tenant_id}."""

    @pytest.mark.asyncio
    async def test_ca13_valid_tenant(self):
        """CA-13: Valid tenant returns cost profile."""
        tenant_doc = {"tenant_id": "t1", "tier": "professional"}

        with (
            patch("src.multi_tenant.repositories.TenantRepository") as mock_tenant_cls,
            patch("src.multi_tenant.repositories.ConversationRepository") as mock_conv_cls,
            patch("src.multi_tenant.repositories.UsageRepository") as mock_usage_cls,
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository") as mock_kb_cls,
        ):
            mock_tenant = AsyncMock()
            mock_tenant.read.return_value = tenant_doc
            mock_tenant_cls.return_value = mock_tenant

            mock_conv = AsyncMock()
            mock_conv.count_in_period.return_value = 25
            mock_conv_cls.return_value = mock_conv

            mock_usage = AsyncMock()
            mock_usage.get_period_summary.return_value = {
                "total_input_tokens": 8000,
                "total_output_tokens": 3000,
            }
            mock_usage_cls.return_value = mock_usage

            mock_kb = AsyncMock()
            mock_kb.count.return_value = 15
            mock_kb_cls.return_value = mock_kb

            result = await get_tenant_cost(tenant_id="t1", days=30)

        assert isinstance(result, TenantCostProfile)
        assert result.tenant_id == "t1"
        assert result.tier == "professional"
        assert result.conversation_count == 25
        assert result.total_input_tokens == 8000
        assert result.total_output_tokens == 3000
        assert result.article_count == 15
        assert result.cost_breakdown.total > 0

    @pytest.mark.asyncio
    async def test_ca14_not_found(self):
        """CA-14: Unknown tenant returns 404."""
        with patch("src.multi_tenant.repositories.TenantRepository") as mock_cls:
            mock_repo = AsyncMock()
            mock_repo.read.return_value = None
            mock_cls.return_value = mock_repo

            with pytest.raises(Exception) as exc_info:
                await get_tenant_cost(tenant_id="nonexistent", days=30)

        # FastAPI HTTPException with 404
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_ca15_zero_compute_share(self):
        """CA-15: Single-tenant view has zero compute share (not attributed)."""
        tenant_doc = {"tenant_id": "t1", "tier": "starter"}

        with (
            patch("src.multi_tenant.repositories.TenantRepository") as mock_tenant_cls,
            patch("src.multi_tenant.repositories.ConversationRepository") as mock_conv_cls,
            patch("src.multi_tenant.repositories.UsageRepository") as mock_usage_cls,
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository") as mock_kb_cls,
        ):
            mock_tenant = AsyncMock()
            mock_tenant.read.return_value = tenant_doc
            mock_tenant_cls.return_value = mock_tenant

            mock_conv = AsyncMock()
            mock_conv.count_in_period.return_value = 5
            mock_conv_cls.return_value = mock_conv

            mock_usage = AsyncMock()
            mock_usage.get_period_summary.return_value = {
                "total_input_tokens": 1000,
                "total_output_tokens": 500,
            }
            mock_usage_cls.return_value = mock_usage

            mock_kb = AsyncMock()
            mock_kb.count.return_value = 3
            mock_kb_cls.return_value = mock_kb

            result = await get_tenant_cost(tenant_id="t1", days=30)

        assert result.cost_breakdown.compute == 0.0
        assert result.cost_share_pct == 0.0

    @pytest.mark.asyncio
    async def test_ca16_zero_conversations(self):
        """CA-16: Zero conversations yields zero cost-per-conversation."""
        tenant_doc = {"tenant_id": "t1", "tier": "starter"}

        with (
            patch("src.multi_tenant.repositories.TenantRepository") as mock_tenant_cls,
            patch("src.multi_tenant.repositories.ConversationRepository") as mock_conv_cls,
            patch("src.multi_tenant.repositories.UsageRepository") as mock_usage_cls,
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository") as mock_kb_cls,
        ):
            mock_tenant = AsyncMock()
            mock_tenant.read.return_value = tenant_doc
            mock_tenant_cls.return_value = mock_tenant

            mock_conv = AsyncMock()
            mock_conv.count_in_period.return_value = 0
            mock_conv_cls.return_value = mock_conv

            mock_usage = AsyncMock()
            mock_usage.get_period_summary.return_value = {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
            }
            mock_usage_cls.return_value = mock_usage

            mock_kb = AsyncMock()
            mock_kb.count.return_value = 10
            mock_kb_cls.return_value = mock_kb

            result = await get_tenant_cost(tenant_id="t1", days=30)

        assert result.cost_per_conversation == 0.0
        # Storage cost should still exist from articles
        assert result.cost_breakdown.storage > 0

    @pytest.mark.asyncio
    async def test_ca17_db_read_failure(self):
        """CA-17: Tenant read failure returns 500."""
        with patch("src.multi_tenant.repositories.TenantRepository") as mock_cls:
            mock_cls.return_value.read.side_effect = Exception("DB error")

            with pytest.raises(Exception) as exc_info:
                await get_tenant_cost(tenant_id="t1", days=30)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_ca18_custom_period(self):
        """CA-18: Custom lookback period is respected."""
        tenant_doc = {"tenant_id": "t1", "tier": "starter"}

        with (
            patch("src.multi_tenant.repositories.TenantRepository") as mock_tenant_cls,
            patch("src.multi_tenant.repositories.ConversationRepository") as mock_conv_cls,
            patch("src.multi_tenant.repositories.UsageRepository") as mock_usage_cls,
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository") as mock_kb_cls,
        ):
            mock_tenant = AsyncMock()
            mock_tenant.read.return_value = tenant_doc
            mock_tenant_cls.return_value = mock_tenant

            mock_conv = AsyncMock()
            mock_conv.count_in_period.return_value = 100
            mock_conv_cls.return_value = mock_conv

            mock_usage = AsyncMock()
            mock_usage.get_period_summary.return_value = {
                "total_input_tokens": 50000,
                "total_output_tokens": 20000,
            }
            mock_usage_cls.return_value = mock_usage

            mock_kb = AsyncMock()
            mock_kb.count.return_value = 25
            mock_kb_cls.return_value = mock_kb

            result = await get_tenant_cost(tenant_id="t1", days=7)

        assert result.tenant_id == "t1"
        # Verify period_start and period_end are ~7 days apart
        from datetime import datetime

        start = datetime.fromisoformat(result.period_start)
        end = datetime.fromisoformat(result.period_end)
        delta = (end - start).days
        assert 6 <= delta <= 7  # Allow for rounding
