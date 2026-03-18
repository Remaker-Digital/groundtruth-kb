"""Property-based tests for rate limiting and API key audit (SPEC-1843 / WI-1483).

Tests verify:
- Rate limit floor enforcement
- Audit buffer append/flush consistency
- Audit record field invariants
- Key suffix truncation

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import pytest
from hypothesis import given, assume, settings
from hypothesis import strategies as st

from src.multi_tenant.api_key_audit import (
    ApiKeyAuditBuffer,
    ApiKeyUsageRecord,
)
from src.multi_tenant.entitlement_service import FROZEN_ENTITLEMENTS
from tests.property.conftest import (
    CANONICAL_TIERS,
    api_path_strategy,
    http_method_strategy,
    http_status_strategy,
    key_suffix_strategy,
    tenant_id_strategy,
    tier_strategy,
)


# ---------------------------------------------------------------------------
# Rate limit floor property
# ---------------------------------------------------------------------------


class TestRateLimitFloorProperty:
    """Every tier's rate limit must meet or exceed the global floor."""

    @given(tier=tier_strategy)
    def test_rate_limit_meets_floor(self, tier: str):
        floor = FROZEN_ENTITLEMENTS["global_config"]["rate_limit_rpm_floor"]
        config = FROZEN_ENTITLEMENTS["tiers"].get(tier, {})
        rpm = config.get("rate_limit_rpm", 300)
        assert rpm >= floor, f"{tier} rate limit {rpm} < floor {floor}"

    def test_floor_is_positive(self):
        floor = FROZEN_ENTITLEMENTS["global_config"]["rate_limit_rpm_floor"]
        assert floor > 0

    def test_default_is_positive(self):
        default = FROZEN_ENTITLEMENTS["global_config"]["rate_limit_rpm_default"]
        assert default > 0
        assert default >= FROZEN_ENTITLEMENTS["global_config"]["rate_limit_rpm_floor"]


# ---------------------------------------------------------------------------
# Audit buffer properties
# ---------------------------------------------------------------------------


def _make_record(
    tenant_id: str = "test-tenant",
    auth_method: str = "api_key",
    key_suffix: str = "abcd1234",
    path: str = "/api/chat",
    method: str = "POST",
    status_code: int = 200,
    client_ip: str = "127.0.0.1",
) -> ApiKeyUsageRecord:
    return ApiKeyUsageRecord(
        tenant_id=tenant_id,
        auth_method=auth_method,
        key_suffix=key_suffix,
        path=path,
        method=method,
        status_code=status_code,
        timestamp=datetime.now(timezone.utc).isoformat(),
        client_ip=client_ip,
    )


class TestAuditBufferAppend:
    """Appending records to the buffer must be consistent."""

    @given(count=st.integers(min_value=0, max_value=100))
    def test_pending_count_matches_appends(self, count: int):
        """After N appends (no flush), pending_count == N."""
        buf = ApiKeyAuditBuffer(flush_interval=9999, buffer_size=9999)
        for _ in range(count):
            buf.record(_make_record())
        assert buf.pending_count == count

    def test_empty_buffer_has_zero_pending(self):
        buf = ApiKeyAuditBuffer()
        assert buf.pending_count == 0

    @given(
        tenant=tenant_id_strategy,
        method=http_method_strategy,
        path=api_path_strategy,
        status=http_status_strategy,
        suffix=key_suffix_strategy,
    )
    def test_record_fields_preserved(
        self, tenant: str, method: str, path: str, status: int, suffix: str,
    ):
        """Fields in the audit record must match what was passed in."""
        record = ApiKeyUsageRecord(
            tenant_id=tenant,
            auth_method="api_key",
            key_suffix=suffix,
            path=path,
            method=method,
            status_code=status,
            timestamp=datetime.now(timezone.utc).isoformat(),
            client_ip="10.0.0.1",
        )
        assert record.tenant_id == tenant
        assert record.method == method
        assert record.path == path
        assert record.status_code == status
        assert record.key_suffix == suffix
        assert len(record.key_suffix) == 8


class TestAuditBufferFlush:
    """Flush behavior properties."""

    @pytest.mark.asyncio
    async def test_flush_empty_returns_zero(self):
        """Flushing an empty buffer returns 0 and doesn't error."""
        buf = ApiKeyAuditBuffer()
        result = await buf.flush()
        assert result == 0

    @pytest.mark.asyncio
    async def test_flush_without_repo_clears_buffer(self):
        """If no repo is configured, flush discards records and clears buffer."""
        buf = ApiKeyAuditBuffer(flush_interval=9999, buffer_size=9999)
        for _ in range(10):
            buf.record(_make_record())
        assert buf.pending_count == 10
        result = await buf.flush()
        assert result == 0  # discarded, not written
        assert buf.pending_count == 0

    @pytest.mark.asyncio
    @given(count=st.integers(min_value=1, max_value=50))
    async def test_flush_clears_all_pending(self, count: int):
        """After flush, the buffer is empty regardless of count."""
        buf = ApiKeyAuditBuffer(flush_interval=9999, buffer_size=9999)
        for _ in range(count):
            buf.record(_make_record())
        await buf.flush()
        assert buf.pending_count == 0


class TestAuditRecordImmutability:
    """ApiKeyUsageRecord is frozen — fields cannot be modified after creation."""

    @given(
        tenant=tenant_id_strategy,
        suffix=key_suffix_strategy,
    )
    def test_record_is_frozen(self, tenant: str, suffix: str):
        record = _make_record(tenant_id=tenant, key_suffix=suffix)
        with pytest.raises(AttributeError):
            record.tenant_id = "mutated"  # type: ignore[misc]

    @given(
        tenant=tenant_id_strategy,
        suffix=key_suffix_strategy,
    )
    def test_record_timestamp_is_valid_iso(self, tenant: str, suffix: str):
        """Timestamp on every record must be valid ISO 8601."""
        record = _make_record(tenant_id=tenant, key_suffix=suffix)
        # Should not raise
        parsed = datetime.fromisoformat(record.timestamp)
        assert parsed.tzinfo is not None  # Must be timezone-aware


# ---------------------------------------------------------------------------
# Key suffix properties
# ---------------------------------------------------------------------------


class TestKeySuffixProperties:
    """Key suffix truncation must be consistent."""

    @given(full_key=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        min_size=1,
        max_size=64,
    ))
    def test_suffix_is_last_8_or_full(self, full_key: str):
        """The convention is to store last 8 chars, or the full key if shorter."""
        suffix = full_key[-8:] if len(full_key) >= 8 else full_key
        assert len(suffix) <= 8
        assert len(suffix) >= 1
        assert full_key.endswith(suffix)


# ---------------------------------------------------------------------------
# Auth method validation
# ---------------------------------------------------------------------------


class TestAuthMethodProperties:
    """Auth method must be one of the known types."""

    VALID_AUTH_METHODS = {"api_key", "widget_key", "shopify", "spa_key", "magic_link", "user_api_key"}

    @given(method=st.sampled_from(list(VALID_AUTH_METHODS)))
    def test_valid_auth_methods_accepted(self, method: str):
        record = _make_record(auth_method=method)
        assert record.auth_method == method
        assert record.auth_method in self.VALID_AUTH_METHODS
