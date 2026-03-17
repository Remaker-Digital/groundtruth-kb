"""Tests for SPEC-1832: API Key Usage Audit Trail.

Verifies that every authenticated request logs key_id, auth_method, endpoint,
status, and client IP — buffered in memory and flushed to Cosmos.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestAPIKeyAuditBuffer:
    """SPEC-1832: API key usage buffered and flushed."""

    @pytest.mark.asyncio
    async def test_usage_recorded_per_request(self):
        """TEST-10435: Authenticated request buffers key_id, auth_method, endpoint, status, IP."""
        from src.multi_tenant.api_key_audit import APIKeyAuditBuffer

        buffer = APIKeyAuditBuffer(max_size=100, flush_interval_seconds=30)

        buffer.record(
            key_id="abcd1234",
            tenant_id="tenant-001",
            auth_method="api_key",
            endpoint="/api/chat",
            http_method="POST",
            status_code=200,
            client_ip="10.0.0.1",
        )

        assert len(buffer) == 1
        entry = buffer.peek()
        assert entry["key_id"] == "abcd1234"
        assert entry["auth_method"] == "api_key"
        assert entry["endpoint"] == "/api/chat"
        assert entry["status_code"] == 200
        assert entry["client_ip"] == "10.0.0.1"
        assert "timestamp" in entry

    @pytest.mark.asyncio
    async def test_batch_flush_at_capacity(self):
        """TEST-10436: Buffer flushes all records when capacity (100) reached."""
        from src.multi_tenant.api_key_audit import APIKeyAuditBuffer

        mock_flush = AsyncMock()
        buffer = APIKeyAuditBuffer(
            max_size=100, flush_interval_seconds=30, flush_fn=mock_flush
        )

        # Fill to capacity
        for i in range(100):
            buffer.record(
                key_id=f"key{i:04d}",
                tenant_id="tenant-001",
                auth_method="api_key",
                endpoint="/api/chat",
                http_method="POST",
                status_code=200,
                client_ip="10.0.0.1",
            )

        await buffer.flush_if_needed()
        mock_flush.assert_called_once()
        args = mock_flush.call_args[0][0]  # First positional arg = list of records
        assert len(args) == 100
        assert len(buffer) == 0  # Buffer cleared after flush

    @pytest.mark.asyncio
    async def test_no_pii_in_usage_records(self):
        """SPEC-1832 req 6: No PII (no request/response bodies, no emails)."""
        from src.multi_tenant.api_key_audit import APIKeyAuditBuffer

        buffer = APIKeyAuditBuffer(max_size=100, flush_interval_seconds=30)

        buffer.record(
            key_id="abcd1234",
            tenant_id="tenant-001",
            auth_method="api_key",
            endpoint="/api/chat",
            http_method="POST",
            status_code=200,
            client_ip="10.0.0.1",
        )

        entry = buffer.peek()
        # Must not contain any body or PII fields
        assert "request_body" not in entry
        assert "response_body" not in entry
        assert "email" not in entry
        assert "name" not in entry

    @pytest.mark.asyncio
    async def test_key_id_is_last_8_chars_of_hash(self):
        """SPEC-1832 req 1: key_id is last 8 chars of hashed key."""
        from src.multi_tenant.api_key_audit import compute_key_id

        full_key = "ar_tenant_abc123def456ghi789"
        key_id = compute_key_id(full_key)

        assert len(key_id) == 8
        # Same key always produces same key_id
        assert compute_key_id(full_key) == key_id


class TestAPIKeyAuditQuery:
    """SPEC-1832: Query endpoint for key usage."""

    @pytest.mark.asyncio
    async def test_query_by_key_id(self):
        """TEST-10437: GET /api/superadmin/audit/key-usage?key_id=XXXX returns matches."""
        from src.multi_tenant.api_key_audit import APIKeyAuditRepository

        mock_container = AsyncMock()
        mock_container.query_items.return_value = AsyncMock(
            __aiter__=AsyncMock(
                return_value=iter([
                    {"key_id": "abcd1234", "endpoint": "/api/chat", "timestamp": "2026-03-16T12:00:00Z"},
                    {"key_id": "abcd1234", "endpoint": "/api/chat", "timestamp": "2026-03-16T12:01:00Z"},
                ])
            )
        )

        repo = APIKeyAuditRepository(container=mock_container)
        results = await repo.query_by_key_id("abcd1234", start="2026-03-16", end="2026-03-17")

        assert len(results) == 2
        assert all(r["key_id"] == "abcd1234" for r in results)
