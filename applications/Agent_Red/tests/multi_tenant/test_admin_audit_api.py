"""Tests for admin_audit_api.py — Audit Log API endpoint coverage.

Covers 1 spec: GET /export endpoint existence (SPEC-0969).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.admin_audit_api import configure_admin_audit_services, router


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.tenant_id = "test-tenant-001"
    ctx.tier = "professional"
    return ctx


# ---------------------------------------------------------------------------
# Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    def test_router_prefix_is_api_audit(self):
        assert router.prefix == "/api/audit"


# ---------------------------------------------------------------------------
# GET /export — Audit log CSV export
# ---------------------------------------------------------------------------


class TestExportAuditEvents:
    """SPEC-0969: GET /export endpoint in admin_audit_api."""

    @pytest.mark.asyncio
    async def test_export_returns_streaming_response(self):
        from src.multi_tenant.admin_audit_api import export_audit_events

        repo = MagicMock()
        repo.query_by_tenant = AsyncMock(return_value=[
            {
                "id": "evt-001",
                "event_type": "conversation.created",
                "tenant_id": "test-tenant-001",
                "timestamp": "2026-01-01T00:00:00Z",
                "data": {},
            },
        ])
        configure_admin_audit_services(audit_repo=repo)

        try:
            result = await export_audit_events(
                event_type=None,
                customer_id=None,
                date_from=None,
                date_to=None,
                ctx=_ctx(),
            )
            # StreamingResponse from starlette
            assert result.media_type == "text/csv"
        finally:
            configure_admin_audit_services(audit_repo=None)
