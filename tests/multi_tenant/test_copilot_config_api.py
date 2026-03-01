"""Tests for Co-Pilot Configuration API (SPEC-1575, SPEC-1576).

Validates scan schedule and retrieval parameter endpoints.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api import (
    CopilotRetrievalConfigRequest,
    CopilotRetrievalConfigResponse,
    CopilotScheduleRequest,
    CopilotScheduleResponse,
    configure_copilot_knowledge_service,
    configure_superadmin_services,
    get_copilot_retrieval_config,
    get_copilot_schedule,
    update_copilot_retrieval_config,
    update_copilot_schedule,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_admin_doc_repo():
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.upsert_document = AsyncMock(return_value=None)
    return repo


@pytest.fixture()
def superadmin_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    return ctx


@pytest.fixture(autouse=True)
def _configure_services(mock_admin_doc_repo):
    configure_superadmin_services(
        tenant_repo=MagicMock(),
        audit_repo=MagicMock(),
    )
    configure_copilot_knowledge_service(
        admin_doc_repo=mock_admin_doc_repo,
    )


# ---------------------------------------------------------------------------
# TestScanSchedule -- SPEC-1575
# ---------------------------------------------------------------------------

class TestScanSchedule:
    """Tests for scan schedule configuration."""

    @pytest.mark.asyncio
    async def test_get_default_schedule(self, superadmin_ctx):
        """GET /copilot/config/schedule returns defaults (TEST-2749)."""
        result = await get_copilot_schedule(_ctx=superadmin_ctx)
        assert isinstance(result, CopilotScheduleResponse)
        assert result.scan_frequency == "manual"
        assert result.scan_scope == "docs-site"
        assert result.last_scan_at is None
        assert result.next_scan_at is None

    @pytest.mark.asyncio
    async def test_update_schedule_daily(
        self, mock_admin_doc_repo, superadmin_ctx
    ):
        """PUT /copilot/config/schedule to daily sets next_scan_at (TEST-2750)."""
        body = CopilotScheduleRequest(
            scan_frequency="daily",
            scan_scope="both",
        )
        result = await update_copilot_schedule(body=body, _ctx=superadmin_ctx)
        assert isinstance(result, CopilotScheduleResponse)
        assert result.scan_frequency == "daily"
        assert result.scan_scope == "both"
        assert result.next_scan_at is not None
        mock_admin_doc_repo.upsert_document.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_schedule_manual_clears_next(
        self, mock_admin_doc_repo, superadmin_ctx
    ):
        """Manual frequency clears next_scan_at."""
        body = CopilotScheduleRequest(
            scan_frequency="manual",
            scan_scope="docs-site",
        )
        result = await update_copilot_schedule(body=body, _ctx=superadmin_ctx)
        assert result.next_scan_at is None

    @pytest.mark.asyncio
    async def test_invalid_frequency_rejected(self, superadmin_ctx):
        """Invalid scan_frequency returns 400."""
        from fastapi import HTTPException

        body = CopilotScheduleRequest(
            scan_frequency="hourly",
            scan_scope="docs-site",
        )
        with pytest.raises(HTTPException) as exc_info:
            await update_copilot_schedule(body=body, _ctx=superadmin_ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_schedule_history_preserved(
        self, mock_admin_doc_repo, superadmin_ctx
    ):
        """Existing scan history is preserved on schedule update."""
        mock_admin_doc_repo.get_by_id = AsyncMock(return_value={
            "scan_frequency": "daily",
            "scan_scope": "docs-site",
            "scan_history": [
                {"timestamp": "2026-03-01T00:00:00Z", "created": 5},
            ],
        })
        body = CopilotScheduleRequest(
            scan_frequency="weekly",
            scan_scope="both",
        )
        result = await update_copilot_schedule(body=body, _ctx=superadmin_ctx)
        assert result.scan_frequency == "weekly"
        assert len(result.scan_history) == 1


# ---------------------------------------------------------------------------
# TestRetrievalConfig -- SPEC-1576
# ---------------------------------------------------------------------------

class TestRetrievalConfig:
    """Tests for retrieval parameter configuration."""

    @pytest.mark.asyncio
    async def test_get_default_config(self, superadmin_ctx):
        """GET /copilot/config/retrieval returns defaults (TEST-2751)."""
        result = await get_copilot_retrieval_config(_ctx=superadmin_ctx)
        assert isinstance(result, CopilotRetrievalConfigResponse)
        assert result.vector_weight == 0.7
        assert result.bm25_weight == 0.3
        assert result.rrf_k == 60
        assert result.top_k == 5
        assert result.min_score == 0.1

    @pytest.mark.asyncio
    async def test_update_retrieval_config(
        self, mock_admin_doc_repo, superadmin_ctx
    ):
        """PUT /copilot/config/retrieval saves parameters (TEST-2752)."""
        body = CopilotRetrievalConfigRequest(
            vector_weight=0.8,
            bm25_weight=0.2,
            rrf_k=40,
            top_k=10,
            min_score=0.05,
        )
        with patch(
            "src.agents.co_pilot.configure_copilot_retrieval"
        ):
            result = await update_copilot_retrieval_config(
                body=body, _ctx=superadmin_ctx
            )
        assert isinstance(result, CopilotRetrievalConfigResponse)
        assert result.vector_weight == 0.8
        assert result.bm25_weight == 0.2
        assert result.rrf_k == 40
        assert result.top_k == 10
        assert result.min_score == 0.05
        assert result.updated_at is not None
        mock_admin_doc_repo.upsert_document.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_invalid_vector_weight_rejected(self, superadmin_ctx):
        """vector_weight out of range returns 400."""
        from fastapi import HTTPException

        body = CopilotRetrievalConfigRequest(vector_weight=1.5)
        with pytest.raises(HTTPException) as exc_info:
            await update_copilot_retrieval_config(
                body=body, _ctx=superadmin_ctx
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_top_k_rejected(self, superadmin_ctx):
        """top_k out of range returns 400."""
        from fastapi import HTTPException

        body = CopilotRetrievalConfigRequest(top_k=0)
        with pytest.raises(HTTPException) as exc_info:
            await update_copilot_retrieval_config(
                body=body, _ctx=superadmin_ctx
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_config_pushes_to_copilot_agent(
        self, mock_admin_doc_repo, superadmin_ctx
    ):
        """Saving config triggers upsert (SPEC-1576)."""
        body = CopilotRetrievalConfigRequest(
            vector_weight=0.6,
            bm25_weight=0.4,
        )
        with patch(
            "src.agents.co_pilot.configure_copilot_retrieval"
        ):
            await update_copilot_retrieval_config(
                body=body, _ctx=superadmin_ctx
            )
            mock_admin_doc_repo.upsert_document.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_503_when_not_configured(self, superadmin_ctx):
        """Returns 503 when knowledge service not configured."""
        from fastapi import HTTPException

        configure_copilot_knowledge_service(admin_doc_repo=None)
        with pytest.raises(HTTPException) as exc_info:
            await get_copilot_retrieval_config(_ctx=superadmin_ctx)
        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# TestCoPilotRuntimeConfig -- SPEC-1576 (agent-side)
# ---------------------------------------------------------------------------

class TestCoPilotRuntimeConfig:
    """Tests for CoPilotAgent runtime config reads."""

    def test_configure_copilot_retrieval(self):
        """configure_copilot_retrieval updates the module-level dict."""
        from src.agents.co_pilot import (
            _get_retrieval_param,
            configure_copilot_retrieval,
        )

        # Set custom config
        configure_copilot_retrieval({
            "vector_weight": 0.9,
            "top_k": 10,
        })
        assert _get_retrieval_param("vector_weight", 0.7) == 0.9
        assert _get_retrieval_param("top_k", 5) == 10
        assert _get_retrieval_param("min_score", 0.1) == 0.1

        # Reset
        configure_copilot_retrieval(None)
        assert _get_retrieval_param("vector_weight", 0.7) == 0.7

    def test_get_retrieval_param_defaults(self):
        """_get_retrieval_param returns defaults when no config set."""
        from src.agents.co_pilot import (
            _get_retrieval_param,
            configure_copilot_retrieval,
        )

        configure_copilot_retrieval(None)
        assert _get_retrieval_param("vector_weight", 0.7) == 0.7
        assert _get_retrieval_param("bm25_weight", 0.3) == 0.3
        assert _get_retrieval_param("rrf_k", 60) == 60
