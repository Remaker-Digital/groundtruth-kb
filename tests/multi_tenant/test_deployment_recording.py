"""Tests for SPEC-1779: Deploy Pipeline Records Deployment Events to Audit Log.

Verifies that POST /api/superadmin/deployments/record correctly stores
deployment events in the audit log via AuditLogRepository.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestDeploymentEventEndpoint:
    """SPEC-1779: Deployment events recorded via superadmin API."""

    @pytest.mark.asyncio
    async def test_audit_log_receives_model_deployed_event(self):
        """TEST-10209: AuditLogRepository receives MODEL_DEPLOYED event."""
        from src.multi_tenant.superadmin_api._diagnostics import (
            DeploymentEventRequest,
            record_deployment_event,
        )

        body = DeploymentEventRequest(
            event_type="model.deployed",
            environment="staging",
            version="v1.91.0",
            image="api-gateway:v1.91.0",
            status="success",
            duration_s=120.0,
            verification_pass=35,
            verification_fail=0,
        )

        mock_audit = AsyncMock()
        mock_ctx = MagicMock()
        mock_ctx.team_member_email = "admin@remaker.digital"

        with patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit,
        ):
            result = await record_deployment_event(body, ctx=mock_ctx)

        assert result.recorded is True
        assert result.event_type == "model.deployed"
        assert result.version == "v1.91.0"
        mock_audit.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_event_payload_includes_required_fields(self):
        """TEST-10210: Event payload includes version, environment, status."""
        from src.multi_tenant.superadmin_api._diagnostics import (
            DeploymentEventRequest,
            record_deployment_event,
        )

        body = DeploymentEventRequest(
            event_type="model.deployed",
            environment="production",
            version="v1.91.0",
            image="api-gateway:v1.91.0",
            previous_image="api-gateway:v1.90.0",
            revision_name="api-gateway--0000115",
            status="success",
            duration_s=90.5,
            verification_pass=35,
            verification_fail=0,
        )

        mock_audit = AsyncMock()
        mock_ctx = MagicMock()
        mock_ctx.team_member_email = "deploy@remaker.digital"

        with patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit,
        ):
            await record_deployment_event(body, ctx=mock_ctx)

        call_kwargs = mock_audit.log_event.call_args
        payload = call_kwargs.kwargs.get("payload") or call_kwargs[1].get("payload")
        assert payload["version"] == "v1.91.0"
        assert payload["environment"] == "production"
        assert payload["status"] == "success"
        assert payload["image"] == "api-gateway:v1.91.0"
        assert payload["previous_image"] == "api-gateway:v1.90.0"
        assert payload["revision_name"] == "api-gateway--0000115"

    @pytest.mark.asyncio
    async def test_invalid_event_type_returns_400(self):
        """TEST-10211: Invalid event_type raises HTTPException 400."""
        from fastapi import HTTPException

        from src.multi_tenant.superadmin_api._diagnostics import (
            DeploymentEventRequest,
            record_deployment_event,
        )

        body = DeploymentEventRequest(
            event_type="invalid.type",
            environment="staging",
            version="v1.91.0",
        )

        mock_ctx = MagicMock()
        mock_ctx.team_member_email = "admin@remaker.digital"

        with pytest.raises(HTTPException) as exc_info:
            await record_deployment_event(body, ctx=mock_ctx)

        assert exc_info.value.status_code == 400
        assert "invalid.type" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_payload_includes_verification_counts(self):
        """TEST-10213: Deployment event payload includes phases_pass/fail counts."""
        from src.multi_tenant.superadmin_api._diagnostics import (
            DeploymentEventRequest,
            record_deployment_event,
        )

        body = DeploymentEventRequest(
            event_type="model.deployed",
            environment="staging",
            version="v1.91.0",
            verification_pass=30,
            verification_fail=5,
            duration_s=150.0,
        )

        mock_audit = AsyncMock()
        mock_ctx = MagicMock()
        mock_ctx.team_member_email = "admin@remaker.digital"

        with patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit,
        ):
            await record_deployment_event(body, ctx=mock_ctx)

        payload = mock_audit.log_event.call_args.kwargs.get("payload") or mock_audit.log_event.call_args[1].get("payload")
        assert payload["verification_pass"] == 30
        assert payload["verification_fail"] == 5
        assert payload["duration_s"] == 150.0

    @pytest.mark.asyncio
    async def test_audit_failure_returns_recorded_false(self):
        """TEST-10214: When audit log fails, response.recorded = False."""
        from src.multi_tenant.superadmin_api._diagnostics import (
            DeploymentEventRequest,
            record_deployment_event,
        )

        body = DeploymentEventRequest(
            event_type="model.deployed",
            environment="staging",
            version="v1.91.0",
        )

        mock_audit = AsyncMock()
        mock_audit.log_event.side_effect = Exception("Cosmos unavailable")
        mock_ctx = MagicMock()
        mock_ctx.team_member_email = "admin@remaker.digital"

        with patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit,
        ):
            result = await record_deployment_event(body, ctx=mock_ctx)

        assert result.recorded is False
        assert result.event_type == "model.deployed"

    @pytest.mark.asyncio
    async def test_rollback_event_type_accepted(self):
        """TEST-10212: model.rolled_back is a valid event type."""
        from src.multi_tenant.superadmin_api._diagnostics import (
            DeploymentEventRequest,
            record_deployment_event,
        )

        body = DeploymentEventRequest(
            event_type="model.rolled_back",
            environment="production",
            version="v1.90.0",
        )

        mock_audit = AsyncMock()
        mock_ctx = MagicMock()
        mock_ctx.team_member_email = "admin@remaker.digital"

        with patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit,
        ):
            result = await record_deployment_event(body, ctx=mock_ctx)

        assert result.recorded is True
        assert result.event_type == "model.rolled_back"
