"""Tests for superadmin rate limit and retry/back-off configuration endpoints.

Validates SPEC-1819 (Code-Free Runtime Configuration — rate limits) and
SPEC-1821 (Back-off and Retry Configuration).

Endpoints tested:
  GET  /api/superadmin/rate-limits
  GET  /api/superadmin/rate-limits/{tier}
  PUT  /api/superadmin/rate-limits/{tier}
  GET  /api/superadmin/rate-limits/history
  GET  /api/superadmin/retry-configs
  GET  /api/superadmin/retry-configs/{service}
  PUT  /api/superadmin/retry-configs/{service}
  GET  /api/superadmin/retry-configs/history

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api._rate_limits import (
    RateLimitConfig,
    RateLimitListResponse,
    RateLimitResponse,
    RateLimitWriteRequest,
    RateLimitWriteResponse,
    RetryConfig,
    RetryConfigListResponse,
    RetryConfigResponse,
    RetryConfigWriteRequest,
    RetryConfigWriteResponse,
    VALID_RATE_LIMIT_TIERS,
    VALID_SERVICES,
    list_rate_limits,
    get_rate_limit,
    put_rate_limit,
    list_retry_configs,
    get_retry_config,
    put_retry_config,
    rate_limit_history,
    retry_config_history,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_platform_repo() -> AsyncMock:
    """Mock PlatformConfigRepository."""
    repo = AsyncMock()
    repo.get_config.return_value = None
    repo.set_config.return_value = {}
    return repo


@pytest.fixture
def mock_audit_repo() -> AsyncMock:
    """Mock AuditLogRepository."""
    repo = AsyncMock()
    repo.log_event.return_value = {}
    return repo


@pytest.fixture
def mock_tenant_ctx() -> MagicMock:
    """Mock TenantContext for SPA admin."""
    ctx = MagicMock()
    ctx.tenant_id = "__platform__"
    ctx.team_member_email = "admin@remaker.digital"
    ctx.tier = "enterprise"
    ctx.api_key_type = "PLATFORM_ADMIN"
    return ctx


@pytest.fixture
def sample_rate_limit_doc() -> dict[str, Any]:
    """Sample rate limit document from Cosmos."""
    return {
        "id": "rate_limits:professional",
        "config_type": "rate_limits",
        "config_key": "professional",
        "value": {
            "rpm": 300,
            "floor": 10,
            "burst_multiplier": 1.5,
            "exempt_roles": ["platform_admin"],
        },
        "version": 2,
        "updated_at": "2026-03-16T10:00:00+00:00",
        "updated_by": "admin@remaker.digital",
    }


@pytest.fixture
def sample_retry_config_doc() -> dict[str, Any]:
    """Sample retry config document from Cosmos."""
    return {
        "id": "retry_config:openai",
        "config_type": "retry_config",
        "config_key": "openai",
        "value": {
            "max_retries": 5,
            "base_delay_ms": 200,
            "max_delay_ms": 10000,
            "backoff_multiplier": 2.0,
            "circuit_breaker_threshold": 15,
            "circuit_breaker_reset_s": 300,
            "timeout_ms": 60000,
        },
        "version": 3,
        "updated_at": "2026-03-16T10:00:00+00:00",
        "updated_by": "admin@remaker.digital",
    }


# ---------------------------------------------------------------------------
# Rate Limit Model Tests
# ---------------------------------------------------------------------------


class TestRateLimitModels:
    """Test Pydantic model validation for rate limit configs."""

    def test_rate_limit_config_defaults(self):
        """Default rate limit config has expected values."""
        cfg = RateLimitConfig(rpm=300)
        assert cfg.rpm == 300
        assert cfg.floor == 10
        assert cfg.burst_multiplier == 1.0
        assert cfg.exempt_roles == ["platform_admin"]

    def test_rate_limit_config_custom(self):
        """Custom rate limit config with non-default values."""
        cfg = RateLimitConfig(rpm=500, floor=20, burst_multiplier=2.0, exempt_roles=[])
        assert cfg.rpm == 500
        assert cfg.floor == 20
        assert cfg.burst_multiplier == 2.0
        assert cfg.exempt_roles == []

    def test_rate_limit_config_minimum_rpm(self):
        """RPM must be at least 1."""
        with pytest.raises(Exception):
            RateLimitConfig(rpm=0)

    def test_valid_tiers_include_global(self):
        """Valid tiers include the 'global' pseudo-tier."""
        assert "global" in VALID_RATE_LIMIT_TIERS
        assert "professional" in VALID_RATE_LIMIT_TIERS

    def test_retry_config_defaults(self):
        """Default retry config has sensible defaults."""
        cfg = RetryConfig()
        assert cfg.max_retries == 3
        assert cfg.base_delay_ms == 100
        assert cfg.max_delay_ms == 5000
        assert cfg.backoff_multiplier == 2.0
        assert cfg.circuit_breaker_threshold == 10
        assert cfg.circuit_breaker_reset_s == 300
        assert cfg.timeout_ms == 30000

    def test_valid_services(self):
        """All expected external services are listed."""
        expected = {"openai", "cosmos", "redis", "smtp", "nats", "shopify"}
        assert VALID_SERVICES == expected


# ---------------------------------------------------------------------------
# Rate Limit GET Tests
# ---------------------------------------------------------------------------


class TestListRateLimits:
    """Tests for GET /api/superadmin/rate-limits."""

    @pytest.mark.asyncio
    async def test_list_returns_frozen_defaults(self, mock_platform_repo):
        """When no Cosmos docs exist, returns frozen defaults (300 RPM)."""
        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await list_rate_limits()

        assert isinstance(result, RateLimitListResponse)
        assert result.total == len(VALID_RATE_LIMIT_TIERS)
        for cfg_resp in result.configs:
            assert cfg_resp.config.rpm == 300
            assert cfg_resp.version == 0

    @pytest.mark.asyncio
    async def test_list_returns_live_docs(self, mock_platform_repo, sample_rate_limit_doc):
        """When Cosmos doc exists, returns live values."""
        async def get_config(config_type, config_key):
            if config_key == "professional":
                return sample_rate_limit_doc
            return None

        mock_platform_repo.get_config.side_effect = get_config

        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await list_rate_limits()

        pro_cfg = next(c for c in result.configs if c.tier == "professional")
        assert pro_cfg.config.rpm == 300
        assert pro_cfg.config.burst_multiplier == 1.5
        assert pro_cfg.version == 2


class TestGetRateLimit:
    """Tests for GET /api/superadmin/rate-limits/{tier}."""

    @pytest.mark.asyncio
    async def test_get_valid_tier_returns_frozen_default(self, mock_platform_repo):
        """Valid tier with no doc returns frozen default."""
        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_rate_limit("starter")

        assert result.tier == "starter"
        assert result.config.rpm == 300
        assert result.version == 0

    @pytest.mark.asyncio
    async def test_get_valid_tier_returns_live_doc(self, mock_platform_repo, sample_rate_limit_doc):
        """Valid tier with doc returns live values."""
        mock_platform_repo.get_config.return_value = sample_rate_limit_doc

        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_rate_limit("professional")

        assert result.tier == "professional"
        assert result.config.burst_multiplier == 1.5
        assert result.version == 2

    @pytest.mark.asyncio
    async def test_get_invalid_tier_returns_400(self, mock_platform_repo):
        """Invalid tier returns HTTP 400."""
        from fastapi import HTTPException

        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_rate_limit("nonexistent")
            assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Rate Limit PUT Tests
# ---------------------------------------------------------------------------


class TestPutRateLimit:
    """Tests for PUT /api/superadmin/rate-limits/{tier}."""

    @pytest.mark.asyncio
    async def test_put_creates_new_config(self, mock_platform_repo, mock_audit_repo, mock_tenant_ctx):
        """PUT to a tier without existing doc creates version 1."""
        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            return_value=MagicMock(invalidate_cache=MagicMock(), invalidate_redis=AsyncMock()),
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit_repo,
        ):
            body = RateLimitWriteRequest(
                config=RateLimitConfig(rpm=500, floor=15),
                change_reason="Increase capacity for launch",
            )
            result = await put_rate_limit("professional", body, mock_tenant_ctx)

        assert isinstance(result, RateLimitWriteResponse)
        assert result.tier == "professional"
        assert result.version == 1
        mock_platform_repo.set_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_put_increments_version(self, mock_platform_repo, mock_audit_repo, mock_tenant_ctx, sample_rate_limit_doc):
        """PUT to a tier with existing doc increments version."""
        mock_platform_repo.get_config.return_value = sample_rate_limit_doc

        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            return_value=MagicMock(invalidate_cache=MagicMock(), invalidate_redis=AsyncMock()),
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit_repo,
        ):
            body = RateLimitWriteRequest(
                config=RateLimitConfig(rpm=600),
            )
            result = await put_rate_limit("professional", body, mock_tenant_ctx)

        assert result.version == 3  # was 2, now 3

    @pytest.mark.asyncio
    async def test_put_invalid_tier_returns_400(self, mock_tenant_ctx):
        """PUT to invalid tier returns HTTP 400."""
        from fastapi import HTTPException

        body = RateLimitWriteRequest(config=RateLimitConfig(rpm=300))
        with pytest.raises(HTTPException) as exc_info:
            await put_rate_limit("invalid_tier", body, mock_tenant_ctx)
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Retry Config GET Tests
# ---------------------------------------------------------------------------


class TestListRetryConfigs:
    """Tests for GET /api/superadmin/retry-configs."""

    @pytest.mark.asyncio
    async def test_list_returns_defaults(self, mock_platform_repo):
        """When no Cosmos docs exist, returns default configs."""
        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await list_retry_configs()

        assert isinstance(result, RetryConfigListResponse)
        assert result.total == len(VALID_SERVICES)
        for cfg_resp in result.configs:
            assert cfg_resp.config.max_retries == 3
            assert cfg_resp.version == 0


class TestGetRetryConfig:
    """Tests for GET /api/superadmin/retry-configs/{service}."""

    @pytest.mark.asyncio
    async def test_get_valid_service_default(self, mock_platform_repo):
        """Valid service without doc returns default config."""
        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_retry_config("openai")

        assert result.service == "openai"
        assert result.config.max_retries == 3
        assert result.version == 0

    @pytest.mark.asyncio
    async def test_get_valid_service_live(self, mock_platform_repo, sample_retry_config_doc):
        """Valid service with doc returns live values."""
        mock_platform_repo.get_config.return_value = sample_retry_config_doc

        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_retry_config("openai")

        assert result.service == "openai"
        assert result.config.max_retries == 5
        assert result.config.timeout_ms == 60000
        assert result.version == 3

    @pytest.mark.asyncio
    async def test_get_invalid_service_returns_400(self, mock_platform_repo):
        """Invalid service returns HTTP 400."""
        from fastapi import HTTPException

        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_retry_config("nonexistent")
            assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Retry Config PUT Tests
# ---------------------------------------------------------------------------


class TestPutRetryConfig:
    """Tests for PUT /api/superadmin/retry-configs/{service}."""

    @pytest.mark.asyncio
    async def test_put_creates_new_config(self, mock_platform_repo, mock_audit_repo, mock_tenant_ctx):
        """PUT to a service without existing doc creates version 1."""
        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            return_value=MagicMock(invalidate_cache=MagicMock(), invalidate_redis=AsyncMock()),
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit_repo,
        ):
            body = RetryConfigWriteRequest(
                config=RetryConfig(max_retries=5, base_delay_ms=200, max_delay_ms=10000),
                change_reason="Increase retries for OpenAI rate limits",
            )
            result = await put_retry_config("openai", body, mock_tenant_ctx)

        assert isinstance(result, RetryConfigWriteResponse)
        assert result.service == "openai"
        assert result.version == 1

    @pytest.mark.asyncio
    async def test_put_base_delay_exceeds_max_returns_400(self, mock_platform_repo, mock_tenant_ctx):
        """PUT with base_delay_ms > max_delay_ms returns HTTP 400."""
        from fastapi import HTTPException

        with patch(
            "src.multi_tenant.superadmin_api._rate_limits._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            body = RetryConfigWriteRequest(
                config=RetryConfig(base_delay_ms=10000, max_delay_ms=1000),
            )
            with pytest.raises(HTTPException) as exc_info:
                await put_retry_config("openai", body, mock_tenant_ctx)
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_put_invalid_service_returns_400(self, mock_tenant_ctx):
        """PUT to invalid service returns HTTP 400."""
        from fastapi import HTTPException

        body = RetryConfigWriteRequest(config=RetryConfig())
        with pytest.raises(HTTPException) as exc_info:
            await put_retry_config("unknown_svc", body, mock_tenant_ctx)
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# History Tests
# ---------------------------------------------------------------------------


class TestRateLimitHistory:
    """Tests for GET /api/superadmin/rate-limits/history."""

    @pytest.mark.asyncio
    async def test_history_returns_empty(self, mock_audit_repo):
        """History returns empty list when no audit entries exist."""
        mock_audit_repo._container = AsyncMock()
        mock_audit_repo._container.query_items.return_value = _aiter_empty()

        with patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit_repo,
        ):
            result = await rate_limit_history(limit=50, skip=0)

        assert result["entries"] == []
        assert result["total"] == 0


class TestRetryConfigHistory:
    """Tests for GET /api/superadmin/retry-configs/history."""

    @pytest.mark.asyncio
    async def test_history_returns_empty(self, mock_audit_repo):
        """History returns empty list when no audit entries exist."""
        mock_audit_repo._container = AsyncMock()
        mock_audit_repo._container.query_items.return_value = _aiter_empty()

        with patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit_repo,
        ):
            result = await retry_config_history(limit=50, skip=0)

        assert result["entries"] == []
        assert result["total"] == 0


# ---------------------------------------------------------------------------
# Async iterator helper
# ---------------------------------------------------------------------------


async def _aiter_empty():
    """Async iterator that yields nothing."""
    return
    yield  # noqa: unreachable — makes this an async generator
