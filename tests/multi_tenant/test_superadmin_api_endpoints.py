"""Tests for superadmin_api.py — Provider Operations API endpoint coverage.

Covers 28 specs: router prefix + 27 endpoint smoke tests verifying each handler
can be called with properly mocked dependencies and returns the expected response.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ctx(
    tenant_id: str = "remaker-digital-001",
    tier: str = "professional",
) -> MagicMock:
    """Build a mock TenantContext with SUPERADMIN defaults."""
    ctx = MagicMock()
    ctx.tenant_id = tenant_id
    ctx.tier = tier
    ctx.user_id = "user-001"
    ctx.team_member_email = "admin@test.com"
    ctx.team_member_role = "superadmin"
    ctx.team_member_id = "member-001"
    ctx.auth_method = "tenant_api_key"
    ctx.shop_domain = None
    return ctx


def _mock_container(items: list[dict[str, Any]] | None = None):
    """Create a mock Cosmos container whose query_items yields items."""
    container = MagicMock()

    async def _query_items(**kwargs):
        for item in (items or []):
            yield item

    container.query_items = _query_items
    return container


def _configure_services(
    tenant_repo=None,
    audit_repo=None,
    conv_repo=None,
    usage_repo=None,
    prefs_repo=None,
    nats_mgr=None,
    secret_service=None,
    incident_repo=None,
    alert_rule_repo=None,
    alert_history_repo=None,
):
    """Wire mocks into the superadmin module via configure_superadmin_services."""
    from src.multi_tenant.superadmin_api import configure_superadmin_services

    configure_superadmin_services(
        tenant_repo=tenant_repo or MagicMock(),
        audit_repo=audit_repo or MagicMock(),
        conv_repo=conv_repo,
        usage_repo=usage_repo,
        prefs_repo=prefs_repo,
        nats_mgr=nats_mgr,
        secret_service=secret_service,
        incident_repo=incident_repo,
        alert_rule_repo=alert_rule_repo,
        alert_history_repo=alert_history_repo,
    )


# ---------------------------------------------------------------------------
# Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    """SPEC: superadmin router prefix is /api/superadmin."""

    def test_router_prefix(self):
        from src.multi_tenant.superadmin_api import router

        assert router.prefix == "/api/superadmin"


# ---------------------------------------------------------------------------
# Tenant Directory
# ---------------------------------------------------------------------------


class TestListAllTenants:
    """SPEC: GET /tenants returns paginated tenant directory."""

    @pytest.mark.asyncio
    async def test_list_all_tenants_returns_directory(self):
        from src.multi_tenant.superadmin_api import list_all_tenants

        tenant_repo = MagicMock()
        tenant_repo._container = _mock_container([
            0,  # count query
        ])
        # Override to return count then empty list — need two separate calls
        call_count = 0
        items_by_call = [[5], []]

        async def _query_items(**kwargs):
            nonlocal call_count
            idx = min(call_count, len(items_by_call) - 1)
            call_count += 1
            for item in items_by_call[idx]:
                yield item

        tenant_repo._container.query_items = _query_items
        _configure_services(tenant_repo=tenant_repo)

        result = await list_all_tenants(skip=0, limit=50)
        assert result.skip == 0
        assert result.limit == 50


# ---------------------------------------------------------------------------
# Tenant Summary
# ---------------------------------------------------------------------------


class TestTenantSummary:
    """SPEC: GET /tenants/summary returns distribution stats."""

    @pytest.mark.asyncio
    async def test_tenant_summary_returns_distribution(self):
        from src.multi_tenant.superadmin_api import tenant_summary

        tenant_repo = MagicMock()
        tenant_repo._container = _mock_container([
            {"status": "active", "tier": "starter", "billing_channel": "shopify"},
        ])
        _configure_services(tenant_repo=tenant_repo)

        result = await tenant_summary()
        assert result.total_tenants == 1
        assert "active" in result.by_status


# ---------------------------------------------------------------------------
# Tier Override
# ---------------------------------------------------------------------------


class TestOverrideTenantTier:
    """SPEC: PUT /tenants/{tenant_id}/tier changes tier."""

    @pytest.mark.asyncio
    async def test_override_tier_success(self):
        from src.multi_tenant.superadmin_api import override_tenant_tier

        tenant_repo = MagicMock()
        tenant_repo.read = AsyncMock(return_value={"tier": "starter"})
        tenant_repo.patch = AsyncMock()
        _configure_services(tenant_repo=tenant_repo)

        result = await override_tenant_tier(
            tenant_id="test-tenant-001",
            tier="professional",
        )
        assert result.new_tier == "professional"
        assert result.previous_tier == "starter"


# ---------------------------------------------------------------------------
# Create Tenant (SPA Provisioning)
# ---------------------------------------------------------------------------


class TestCreateTenant:
    """SPEC: POST /tenants provisions a new tenant."""

    @pytest.mark.asyncio
    async def test_create_tenant_success(self):
        from src.multi_tenant.superadmin_api import (
            CreateTenantRequest,
            create_tenant,
        )

        provision_result = MagicMock()
        provision_result.tenant_id = "new-tenant-001"
        provision_result.status = "active"
        provision_result.tier = "starter"
        provision_result.superadmin_email = "admin@new.com"
        provision_result.superadmin_api_key = "ar_key_xxx"
        provision_result.widget_key = "pk_live_xxx"
        provision_result.errors = []

        tenant_repo = MagicMock()
        tenant_repo.patch = AsyncMock()
        prefs_repo = MagicMock()
        prefs_repo.create = AsyncMock()
        audit_repo = MagicMock()
        audit_repo.create = AsyncMock()
        _configure_services(
            tenant_repo=tenant_repo,
            prefs_repo=prefs_repo,
            audit_repo=audit_repo,
        )

        body = CreateTenantRequest(
            merchant_name="Test Merchant",
            superadmin_email="admin@new.com",
            tier="starter",
        )

        with patch(
            "src.integrations.provisioning.spa_provision_tenant",
            new_callable=AsyncMock,
            return_value=provision_result,
        ):
            result = await create_tenant(body=body, ctx=_ctx())

        assert result.tenant_id == "new-tenant-001"
        assert result.status == "active"


# ---------------------------------------------------------------------------
# Resend Welcome Email
# ---------------------------------------------------------------------------


class TestResendWelcomeEmail:
    """SPEC: POST /tenants/{tenant_id}/resend-welcome-email."""

    @pytest.mark.asyncio
    async def test_resend_welcome_email_success(self):
        from src.multi_tenant.superadmin_api import resend_welcome_email

        tenant_repo = MagicMock()
        tenant_repo.read = AsyncMock(return_value={
            "tenant_id": "test-001",
            "customer_email": "user@test.com",
            "tier": "starter",
        })
        prefs_repo = MagicMock()
        prefs_repo.get_active = AsyncMock(return_value=None)
        _configure_services(tenant_repo=tenant_repo, prefs_repo=prefs_repo)

        with patch(
            "src.multi_tenant.welcome_email.send_welcome_email",
            new_callable=AsyncMock,
            return_value=True,
        ):
            result = await resend_welcome_email(
                tenant_id="test-001",
                ctx=_ctx(),
            )

        assert result.sent is True
        assert result.sent_to == "user@test.com"


# ---------------------------------------------------------------------------
# Set Tenant Expiry
# ---------------------------------------------------------------------------


class TestSetTenantExpiry:
    """SPEC: PATCH /tenants/{tenant_id}/expiry sets or clears access expiry."""

    @pytest.mark.asyncio
    async def test_set_expiry_success(self):
        from src.multi_tenant.superadmin_api import SetExpiryRequest, set_tenant_expiry

        tenant_repo = MagicMock()
        tenant_repo.read = AsyncMock(return_value={
            "tenant_id": "test-001",
            "expires_at": None,
            "status": "active",
        })
        tenant_repo.patch = AsyncMock()
        audit_repo = MagicMock()
        audit_repo.create = AsyncMock()
        _configure_services(tenant_repo=tenant_repo, audit_repo=audit_repo)

        body = SetExpiryRequest(expires_at="2026-12-31T23:59:59+00:00")
        result = await set_tenant_expiry(
            tenant_id="test-001",
            body=body,
            ctx=_ctx(),
        )
        assert result.new_expires_at == "2026-12-31T23:59:59+00:00"
        assert result.previous_expires_at is None


# ---------------------------------------------------------------------------
# Deployment History
# ---------------------------------------------------------------------------


class TestDeploymentHistory:
    """SPEC: GET /deployments returns deployment event history."""

    @pytest.mark.asyncio
    async def test_deployment_history_returns_events(self):
        from src.multi_tenant.superadmin_api import deployment_history

        audit_repo = MagicMock()
        audit_repo._container = _mock_container([])
        _configure_services(audit_repo=audit_repo)

        with patch(
            "src.multi_tenant.superadmin_api.PRODUCT_VERSION",
            "1.60.0",
            create=True,
        ):
            result = await deployment_history(limit=20)

        assert result.total == 0
        assert result.events == []


# ---------------------------------------------------------------------------
# Provider Dashboard
# ---------------------------------------------------------------------------


class TestProviderDashboard:
    """SPEC: GET /dashboard returns aggregate provider ops data."""

    @pytest.mark.asyncio
    async def test_provider_dashboard_returns_timestamp(self):
        from src.multi_tenant.superadmin_api import provider_dashboard

        tenant_repo = MagicMock()
        tenant_repo._container = _mock_container([])
        audit_repo = MagicMock()
        audit_repo._container = _mock_container([])
        _configure_services(tenant_repo=tenant_repo, audit_repo=audit_repo)

        result = await provider_dashboard()
        assert result.timestamp is not None
        assert isinstance(result.system_health, dict)


# ---------------------------------------------------------------------------
# Billing Health
# ---------------------------------------------------------------------------


class TestBillingHealth:
    """SPEC: GET /billing/health returns provider billing health."""

    @pytest.mark.asyncio
    async def test_billing_health_returns_response(self):
        from src.multi_tenant.superadmin_api import billing_health

        tenant_repo = MagicMock()
        tenant_repo._container = _mock_container([])
        _configure_services(tenant_repo=tenant_repo)

        result = await billing_health()
        assert result.total_tenants == 0
        assert result.tenants == []


# ---------------------------------------------------------------------------
# SLA Trends
# ---------------------------------------------------------------------------


class TestSLATrends:
    """SPEC: GET /sla/trends returns SLA trends and error budgets."""

    @pytest.mark.asyncio
    async def test_sla_trends_returns_503_when_unavailable(self):
        from fastapi import HTTPException

        from src.multi_tenant.superadmin_api import sla_trends

        _configure_services()

        with pytest.raises(HTTPException) as exc_info:
            await sla_trends(range_days=7, period_days=30)
        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# Queue Depth
# ---------------------------------------------------------------------------


class TestQueueDepth:
    """SPEC: GET /queues returns queue depth per tenant."""

    @pytest.mark.asyncio
    async def test_queue_depth_nats_not_deployed(self):
        from src.multi_tenant.superadmin_api import queue_depth

        _configure_services(nats_mgr=None)

        result = await queue_depth()
        assert result.nats_deployed is False
        assert result.total_messages == 0


# ---------------------------------------------------------------------------
# Compliance Summary
# ---------------------------------------------------------------------------


class TestComplianceSummary:
    """SPEC: GET /compliance returns cross-tenant compliance overview."""

    @pytest.mark.asyncio
    async def test_compliance_summary_empty(self):
        from src.multi_tenant.superadmin_api import compliance_summary

        tenant_repo = MagicMock()
        tenant_repo.list_active_tenant_ids = AsyncMock(return_value=[])
        _configure_services(tenant_repo=tenant_repo)

        result = await compliance_summary()
        assert result.total_tenants == 0


# ---------------------------------------------------------------------------
# Secret Posture
# ---------------------------------------------------------------------------


class TestSecretPosture:
    """SPEC: GET /secrets/posture returns secret inventory."""

    @pytest.mark.asyncio
    async def test_secret_posture_empty(self):
        from src.multi_tenant.superadmin_api import secret_posture

        tenant_repo = MagicMock()
        tenant_repo.list_active_tenant_ids = AsyncMock(return_value=[])
        secret_service = MagicMock()
        _configure_services(
            tenant_repo=tenant_repo,
            secret_service=secret_service,
        )

        result = await secret_posture()
        assert result.total_tenants == 0
        assert result.total_secrets == 0


# ---------------------------------------------------------------------------
# Integration Health
# ---------------------------------------------------------------------------


class TestIntegrationHealth:
    """SPEC: GET /integrations/health returns circuit breakers + MCP status."""

    @pytest.mark.asyncio
    async def test_integration_health_no_nats(self):
        from src.multi_tenant.superadmin_api import integration_health

        _configure_services(nats_mgr=None)

        result = await integration_health()
        assert result.nats_deployed is False
        assert result.overall_healthy is True


# ---------------------------------------------------------------------------
# Incident Management
# ---------------------------------------------------------------------------


class TestListIncidents:
    """SPEC: GET /incidents lists all incidents."""

    @pytest.mark.asyncio
    async def test_list_incidents_empty(self):
        from src.multi_tenant.superadmin_api import list_incidents

        incident_repo = MagicMock()
        incident_repo.list_all = AsyncMock(return_value=[])
        _configure_services(incident_repo=incident_repo)

        result = await list_incidents(limit=50)
        assert result.total == 0
        assert result.incidents == []


class TestCreateIncident:
    """SPEC: POST /incidents creates a new incident."""

    @pytest.mark.asyncio
    async def test_create_incident(self):
        from src.multi_tenant.superadmin_api import (
            CreateIncidentRequest,
            create_incident,
        )

        now = datetime.now(timezone.utc).isoformat()
        incident_repo = MagicMock()
        incident_repo.create_incident = AsyncMock(return_value={
            "incident_id": "INC-001",
            "title": "Test Incident",
            "description": "",
            "status": "investigating",
            "severity": "minor",
            "affected_services": [],
            "updates": [],
            "created_at": now,
            "updated_at": now,
            "created_by": "admin@test.com",
        })
        _configure_services(incident_repo=incident_repo)

        body = CreateIncidentRequest(title="Test Incident")
        result = await create_incident(body=body, ctx=_ctx())
        assert result.incident_id == "INC-001"
        assert result.status == "investigating"


class TestGetIncident:
    """SPEC: GET /incidents/{incident_id} returns a single incident."""

    @pytest.mark.asyncio
    async def test_get_incident(self):
        from src.multi_tenant.superadmin_api import get_incident

        now = datetime.now(timezone.utc).isoformat()
        incident_repo = MagicMock()
        incident_repo.find_incident = AsyncMock(return_value={
            "incident_id": "INC-001",
            "title": "Test",
            "status": "investigating",
            "severity": "minor",
            "created_at": now,
            "updated_at": now,
        })
        _configure_services(incident_repo=incident_repo)

        result = await get_incident(incident_id="INC-001")
        assert result.incident_id == "INC-001"


class TestAddIncidentUpdate:
    """SPEC: POST /incidents/{incident_id}/update adds status update."""

    @pytest.mark.asyncio
    async def test_add_incident_update(self):
        from src.multi_tenant.superadmin_api import (
            AddIncidentUpdateRequest,
            add_incident_update,
        )

        now = datetime.now(timezone.utc).isoformat()
        incident_repo = MagicMock()
        incident_repo.find_incident = AsyncMock(return_value={
            "incident_id": "INC-001",
            "status": "investigating",
        })
        incident_repo.add_update = AsyncMock(return_value={
            "incident_id": "INC-001",
            "title": "Test",
            "status": "identified",
            "severity": "minor",
            "updates": [{"timestamp": now, "status": "identified", "message": "Found it"}],
            "created_at": now,
            "updated_at": now,
        })
        _configure_services(incident_repo=incident_repo)

        body = AddIncidentUpdateRequest(status="identified", message="Found it")
        result = await add_incident_update(
            incident_id="INC-001", body=body, ctx=_ctx(),
        )
        assert result.status == "identified"


class TestResolveIncident:
    """SPEC: POST /incidents/{incident_id}/resolve marks as resolved."""

    @pytest.mark.asyncio
    async def test_resolve_incident(self):
        from src.multi_tenant.superadmin_api import resolve_incident

        now = datetime.now(timezone.utc).isoformat()
        incident_repo = MagicMock()
        incident_repo.find_incident = AsyncMock(return_value={
            "incident_id": "INC-001",
            "status": "identified",
        })
        incident_repo.resolve_incident = AsyncMock(return_value={
            "incident_id": "INC-001",
            "title": "Test",
            "status": "resolved",
            "severity": "minor",
            "resolved_at": now,
            "created_at": now,
            "updated_at": now,
        })
        _configure_services(incident_repo=incident_repo)

        result = await resolve_incident(
            incident_id="INC-001",
            message="All clear",
            ctx=_ctx(),
        )
        assert result.status == "resolved"


# ---------------------------------------------------------------------------
# Alert Rule Management
# ---------------------------------------------------------------------------


class TestListAlertRules:
    """SPEC: GET /alerts/rules lists all alert rules."""

    @pytest.mark.asyncio
    async def test_list_alert_rules_empty(self):
        from src.multi_tenant.superadmin_api import list_alert_rules

        alert_rule_repo = MagicMock()
        alert_rule_repo.list_all = AsyncMock(return_value=[])
        _configure_services(alert_rule_repo=alert_rule_repo)

        result = await list_alert_rules()
        assert result.total == 0
        assert result.rules == []


class TestCreateAlertRule:
    """SPEC: POST /alerts/rules creates an alert rule."""

    @pytest.mark.asyncio
    async def test_create_alert_rule(self):
        from src.multi_tenant.superadmin_api import (
            AlertConditionModel,
            CreateAlertRuleRequest,
            create_alert_rule,
        )

        now = datetime.now(timezone.utc).isoformat()
        alert_rule_repo = MagicMock()
        alert_rule_repo.create_rule = AsyncMock(return_value={
            "rule_id": "RULE-001",
            "rule_type": "error_rate",
            "name": "High Error Rate",
            "condition": {"metric": "error_rate", "operator": "gt", "threshold": 5.0},
            "created_at": now,
            "updated_at": now,
        })
        _configure_services(alert_rule_repo=alert_rule_repo)

        body = CreateAlertRuleRequest(
            name="High Error Rate",
            rule_type="error_rate",
            condition=AlertConditionModel(metric="error_rate", operator="gt", threshold=5.0),
        )
        result = await create_alert_rule(body=body)
        assert result.rule_id == "RULE-001"
        assert result.name == "High Error Rate"


class TestUpdateAlertRule:
    """SPEC: PUT /alerts/rules/{rule_id} updates an alert rule."""

    @pytest.mark.asyncio
    async def test_update_alert_rule(self):
        from src.multi_tenant.superadmin_api import (
            UpdateAlertRuleRequest,
            update_alert_rule,
        )

        now = datetime.now(timezone.utc).isoformat()
        alert_rule_repo = MagicMock()
        alert_rule_repo.find_rule = AsyncMock(return_value={
            "rule_id": "RULE-001",
            "rule_type": "error_rate",
            "name": "Old Name",
            "condition": {},
            "created_at": now,
            "updated_at": now,
        })
        alert_rule_repo.update_rule = AsyncMock(return_value={
            "rule_id": "RULE-001",
            "rule_type": "error_rate",
            "name": "Updated Name",
            "condition": {},
            "created_at": now,
            "updated_at": now,
        })
        _configure_services(alert_rule_repo=alert_rule_repo)

        body = UpdateAlertRuleRequest(name="Updated Name")
        result = await update_alert_rule(
            rule_id="RULE-001", body=body,
        )
        assert result.name == "Updated Name"


class TestDeleteAlertRule:
    """SPEC: DELETE /alerts/rules/{rule_id} deletes an alert rule."""

    @pytest.mark.asyncio
    async def test_delete_alert_rule(self):
        from src.multi_tenant.superadmin_api import delete_alert_rule

        alert_rule_repo = MagicMock()
        alert_rule_repo.find_rule = AsyncMock(return_value={
            "rule_id": "RULE-001",
            "rule_type": "error_rate",
        })
        alert_rule_repo.delete_rule = AsyncMock(return_value=True)
        _configure_services(alert_rule_repo=alert_rule_repo)

        result = await delete_alert_rule(rule_id="RULE-001")
        assert result.deleted is True


# ---------------------------------------------------------------------------
# Alert History
# ---------------------------------------------------------------------------


class TestAlertHistory:
    """SPEC: GET /alerts/history returns alert firing history."""

    @pytest.mark.asyncio
    async def test_alert_history_empty(self):
        from src.multi_tenant.superadmin_api import alert_history

        alert_history_repo = MagicMock()
        alert_history_repo.list_recent = AsyncMock(return_value=[])
        _configure_services(alert_history_repo=alert_history_repo)

        result = await alert_history(days=7, limit=100)
        assert result.total == 0
        assert result.alerts == []


class TestAcknowledgeAlert:
    """SPEC: POST /alerts/history/{alert_id}/acknowledge acks an alert."""

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self):
        from src.multi_tenant.superadmin_api import acknowledge_alert

        alert_history_repo = MagicMock()
        alert_history_repo.acknowledge = AsyncMock(return_value={
            "id": "ALERT-001",
            "alert_date": "2026-02-27",
            "rule_id": "RULE-001",
            "acknowledged": True,
            "acknowledged_by": "admin@test.com",
            "triggered_at": "2026-02-27T10:00:00Z",
        })
        _configure_services(alert_history_repo=alert_history_repo)

        result = await acknowledge_alert(
            alert_id="ALERT-001",
            alert_date="2026-02-27",
            ctx=_ctx(),
        )
        assert result.acknowledged is True


class TestEvaluateAlerts:
    """SPEC: POST /alerts/evaluate force-evaluates all alert rules."""

    @pytest.mark.asyncio
    async def test_evaluate_alerts_engine_not_available(self):
        from src.multi_tenant.superadmin_api import evaluate_alerts

        _configure_services()

        result = await evaluate_alerts()
        # Should return an EvaluateAlertsResponse with evaluated=False or True
        assert hasattr(result, "evaluated")


# ---------------------------------------------------------------------------
# MFA/TOTP Endpoints
# ---------------------------------------------------------------------------


class TestMfaStatus:
    """SPEC: GET /mfa/status returns MFA enrollment status."""

    @pytest.mark.asyncio
    async def test_mfa_status(self):
        from src.multi_tenant.superadmin_api import mfa_status

        mock_svc = MagicMock()
        mock_svc.get_enrollment_status = AsyncMock(return_value={
            "mfa_enabled": False,
            "backup_codes_remaining": 0,
        })

        mock_member = {
            "id": "member-001",
            "tenant_id": "remaker-digital-001",
            "mfa_enabled": False,
        }

        with (
            patch(
                "src.multi_tenant.superadmin_api._operations._get_mfa_svc",
                return_value=mock_svc,
            ),
            patch(
                "src.multi_tenant.superadmin_api._operations._get_team_member",
                new_callable=AsyncMock,
                return_value=mock_member,
            ),
        ):
            result = await mfa_status(ctx=_ctx())

        assert result.mfa_enabled is False
