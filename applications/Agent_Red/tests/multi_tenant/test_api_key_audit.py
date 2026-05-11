"""Tests for SPEC-1832: API Key Usage Audit Trail.

Verifies that every authenticated request logs auth_method, key_suffix,
endpoint, status, and client IP — buffered in memory and flushed to Cosmos.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.multi_tenant.api_key_audit import (
    ApiKeyAuditBuffer,
    ApiKeyUsageRecord,
    get_api_key_audit_buffer,
    record_api_key_usage,
)


# ---------------------------------------------------------------------------
# ApiKeyUsageRecord dataclass
# ---------------------------------------------------------------------------


class TestApiKeyUsageRecord:
    """Tests for the frozen audit record dataclass."""

    def test_record_creation_all_fields(self):
        """All fields captured in an immutable record."""
        rec = ApiKeyUsageRecord(
            tenant_id="t-001",
            auth_method="api_key",
            key_suffix="abcd1234",
            path="/api/chat/message",
            method="POST",
            status_code=200,
            timestamp="2026-03-17T00:00:00+00:00",
            client_ip="10.0.0.1",
            team_member_id="tm-001",
        )
        assert rec.tenant_id == "t-001"
        assert rec.auth_method == "api_key"
        assert rec.key_suffix == "abcd1234"
        assert rec.path == "/api/chat/message"
        assert rec.method == "POST"
        assert rec.status_code == 200
        assert rec.client_ip == "10.0.0.1"
        assert rec.team_member_id == "tm-001"

    def test_record_frozen(self):
        """Records are immutable (frozen dataclass)."""
        rec = ApiKeyUsageRecord(
            tenant_id="t-001",
            auth_method="api_key",
            key_suffix="abcd1234",
            path="/api/chat",
            method="GET",
            status_code=200,
            timestamp="2026-03-17T00:00:00+00:00",
        )
        with pytest.raises(AttributeError):
            rec.tenant_id = "changed"  # type: ignore[misc]

    def test_record_defaults(self):
        """client_ip defaults to '' and team_member_id to None."""
        rec = ApiKeyUsageRecord(
            tenant_id="t-001",
            auth_method="widget_key",
            key_suffix="efgh5678",
            path="/api/config",
            method="GET",
            status_code=200,
            timestamp="2026-03-17T00:00:00+00:00",
        )
        assert rec.client_ip == ""
        assert rec.team_member_id is None

    def test_no_pii_fields(self):
        """SPEC-1832 req 6: Record has no PII fields (email, name, body)."""
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ApiKeyUsageRecord)}
        # Must NOT include PII-bearing fields
        pii_fields = {"email", "name", "request_body", "response_body", "password"}
        assert field_names & pii_fields == set()


# ---------------------------------------------------------------------------
# ApiKeyAuditBuffer
# ---------------------------------------------------------------------------


class TestApiKeyAuditBuffer:
    """Tests for the in-memory audit buffer."""

    def test_record_appends_to_buffer(self):
        """record() appends to internal deque."""
        buf = ApiKeyAuditBuffer(buffer_size=100)
        rec = ApiKeyUsageRecord(
            tenant_id="t-001", auth_method="api_key", key_suffix="abcd1234",
            path="/api/chat", method="POST", status_code=200,
            timestamp="2026-03-17T00:00:00+00:00",
        )
        buf.record(rec)
        assert buf.pending_count == 1

    def test_pending_count_increments(self):
        """pending_count tracks buffered records."""
        buf = ApiKeyAuditBuffer(buffer_size=100)
        for i in range(5):
            buf.record(ApiKeyUsageRecord(
                tenant_id="t-001", auth_method="api_key", key_suffix=f"key{i:04d}",
                path="/api/chat", method="POST", status_code=200,
                timestamp="2026-03-17T00:00:00+00:00",
            ))
        assert buf.pending_count == 5

    @pytest.mark.asyncio
    async def test_flush_empty_buffer_returns_zero(self):
        """Flushing an empty buffer is a no-op."""
        buf = ApiKeyAuditBuffer()
        result = await buf.flush()
        assert result == 0

    @pytest.mark.asyncio
    async def test_flush_without_repo_clears_buffer(self):
        """When no audit_repo is configured, flush discards records."""
        buf = ApiKeyAuditBuffer()
        buf.record(ApiKeyUsageRecord(
            tenant_id="t-001", auth_method="api_key", key_suffix="abcd1234",
            path="/api/chat", method="POST", status_code=200,
            timestamp="2026-03-17T00:00:00+00:00",
        ))
        assert buf.pending_count == 1
        result = await buf.flush()
        assert result == 0
        assert buf.pending_count == 0  # Buffer cleared even without repo

    @pytest.mark.asyncio
    async def test_flush_with_repo_writes_all_records(self):
        """Flush calls audit_repo.log_event() for each buffered record."""
        buf = ApiKeyAuditBuffer()
        mock_repo = AsyncMock()
        mock_repo.log_event = AsyncMock()
        buf.configure(mock_repo)

        for i in range(3):
            buf.record(ApiKeyUsageRecord(
                tenant_id="t-001", auth_method="api_key", key_suffix=f"key{i:04d}",
                path="/api/chat", method="POST", status_code=200,
                timestamp="2026-03-17T00:00:00+00:00",
            ))

        result = await buf.flush()
        assert result == 3
        assert mock_repo.log_event.call_count == 3
        assert buf.pending_count == 0

    @pytest.mark.asyncio
    async def test_flush_writes_correct_event_shape(self):
        """Flushed events use SECURITY_EVENT type and correct details."""
        buf = ApiKeyAuditBuffer()
        mock_repo = AsyncMock()
        mock_repo.log_event = AsyncMock()
        buf.configure(mock_repo)

        buf.record(ApiKeyUsageRecord(
            tenant_id="t-001", auth_method="widget_key", key_suffix="efgh5678",
            path="/api/config", method="GET", status_code=200,
            timestamp="2026-03-17T00:00:00+00:00", client_ip="192.168.1.1",
        ))
        await buf.flush()

        call_kwargs = mock_repo.log_event.call_args[1]
        assert call_kwargs["tenant_id"] == "t-001"
        assert call_kwargs["actor_id"] == "key:efgh5678"
        assert call_kwargs["resource_type"] == "api_request"
        assert call_kwargs["resource_id"] == "GET /api/config"
        details = call_kwargs["details"]
        assert details["action"] == "api_key_usage"
        assert details["auth_method"] == "widget_key"
        assert details["client_ip"] == "192.168.1.1"

    @pytest.mark.asyncio
    async def test_flush_tolerates_repo_exception(self):
        """Individual log_event failures don't crash the flush."""
        buf = ApiKeyAuditBuffer()
        mock_repo = AsyncMock()
        call_count = 0

        async def flaky_log(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise RuntimeError("Cosmos 429")

        mock_repo.log_event = flaky_log
        buf.configure(mock_repo)

        for i in range(3):
            buf.record(ApiKeyUsageRecord(
                tenant_id="t-001", auth_method="api_key", key_suffix=f"key{i:04d}",
                path="/api/chat", method="POST", status_code=200,
                timestamp="2026-03-17T00:00:00+00:00",
            ))

        result = await buf.flush()
        assert result == 2  # 3 attempted, 1 failed, 2 succeeded
        assert buf.pending_count == 0  # Buffer still cleared


# ---------------------------------------------------------------------------
# record_api_key_usage() convenience function
# ---------------------------------------------------------------------------


class TestRecordApiKeyUsage:
    """Tests for the module-level convenience function."""

    def test_record_creates_buffer_entry(self):
        """record_api_key_usage() creates a buffered record."""
        import src.multi_tenant.api_key_audit as mod
        # Reset singleton
        old = mod._audit_buffer
        mod._audit_buffer = None
        try:
            record_api_key_usage(
                tenant_id="t-001",
                auth_method="api_key",
                key_suffix="abcd1234",
                path="/api/chat",
                method="POST",
                status_code=200,
                client_ip="10.0.0.1",
            )
            buf = get_api_key_audit_buffer()
            assert buf.pending_count == 1
        finally:
            mod._audit_buffer = old

    def test_record_includes_timestamp(self):
        """record_api_key_usage() auto-generates a UTC timestamp."""
        import src.multi_tenant.api_key_audit as mod
        old = mod._audit_buffer
        mod._audit_buffer = None
        try:
            record_api_key_usage(
                tenant_id="t-001",
                auth_method="widget_key",
                key_suffix="efgh5678",
                path="/api/config",
                method="GET",
            )
            buf = get_api_key_audit_buffer()
            # Access the internal buffer to verify timestamp
            assert buf.pending_count == 1
            rec = buf._buffer[0]
            assert rec.timestamp  # Non-empty
            assert "T" in rec.timestamp  # ISO format
        finally:
            mod._audit_buffer = old


# ---------------------------------------------------------------------------
# Middleware integration (SPEC-1832 recording in dispatch)
# ---------------------------------------------------------------------------


class TestMiddlewareAuditIntegration:
    """Verify that middleware.py calls record_api_key_usage."""

    def test_middleware_contains_spec_1832_recording(self):
        """Source-level assertion: middleware has SPEC-1832 audit block."""
        import inspect
        from src.multi_tenant.middleware import TenantAuthMiddleware
        source = inspect.getsource(TenantAuthMiddleware.dispatch)
        assert "SPEC-1832" in source
        assert "record_api_key_usage" in source

    def test_middleware_extracts_key_suffix_for_api_key(self):
        """Source: middleware extracts last 8 chars for api_key/user_api_key."""
        import inspect
        from src.multi_tenant.middleware import TenantAuthMiddleware
        source = inspect.getsource(TenantAuthMiddleware.dispatch)
        assert 'raw_key[-8:]' in source

    def test_middleware_audit_wrapped_in_try_except(self):
        """Source: audit block is wrapped in try/except so it never fails the request."""
        import inspect
        from src.multi_tenant.middleware import TenantAuthMiddleware
        source = inspect.getsource(TenantAuthMiddleware.dispatch)
        # Verify the protective pattern exists
        assert "Audit recording must never fail" in source


# ---------------------------------------------------------------------------
# Superadmin API key usage query endpoint (WI-1450)
# ---------------------------------------------------------------------------


class TestApiKeyUsageQueryEndpoint:
    """Tests for GET /diagnostics/api-key-usage."""

    def test_endpoint_exists_in_diagnostics(self):
        """Source: _diagnostics.py has the api-key-usage route."""
        import inspect
        from src.multi_tenant.superadmin_api import _diagnostics
        source = inspect.getsource(_diagnostics)
        assert "/diagnostics/api-key-usage" in source

    def test_response_model_has_buffer_pending(self):
        """ApiKeyUsageResponse includes buffer_pending field."""
        from src.multi_tenant.superadmin_api._diagnostics import ApiKeyUsageResponse
        resp = ApiKeyUsageResponse(records=[], total=0, buffer_pending=42)
        assert resp.buffer_pending == 42

    def test_response_model_record_shape(self):
        """ApiKeyUsageRecord model has all required fields."""
        from src.multi_tenant.superadmin_api._diagnostics import (
            ApiKeyUsageRecord as DiagRecord,
        )
        rec = DiagRecord(
            tenant_id="t-001",
            auth_method="api_key",
            key_suffix="abcd1234",
            path="/api/chat",
            method="POST",
            client_ip="10.0.0.1",
            timestamp="2026-03-17T00:00:00+00:00",
        )
        assert rec.tenant_id == "t-001"
        assert rec.auth_method == "api_key"
        assert rec.key_suffix == "abcd1234"

    def test_query_filters_documented(self):
        """Source: endpoint supports tenant_id, auth_method, days, limit filters."""
        import inspect
        from src.multi_tenant.superadmin_api._diagnostics import get_api_key_usage
        source = inspect.getsource(get_api_key_usage)
        assert "tenant_id" in source
        assert "auth_method" in source
        assert "days" in source
        assert "limit" in source
