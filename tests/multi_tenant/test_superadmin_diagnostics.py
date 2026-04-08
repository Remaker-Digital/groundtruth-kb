"""Tests for superadmin test pipeline trigger and diagnostic export endpoints.

Validates SPEC-1826 (SPA Test Execution Trigger) and
SPEC-1827 (Diagnostic Data Export for Claude Code).

Endpoints tested:
  POST /api/superadmin/tests/run
  GET  /api/superadmin/tests/{run_id}/status
  GET  /api/superadmin/tests/runs
  GET  /api/superadmin/diagnostics/logs
  GET  /api/superadmin/diagnostics/traces
  GET  /api/superadmin/diagnostics/metrics
  GET  /api/superadmin/diagnostics/drift
  GET  /api/superadmin/diagnostics/health

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.multi_tenant.superadmin_api._diagnostics import (
    ConfigDriftResponse,
    DiagnosticLogsResponse,
    DiagnosticMetricsResponse,
    DiagnosticTracesResponse,
    SystemHealthResponse,
    PipelineRunRequest,
    PipelineRunStatusResponse,
    PipelineRunTriggerResponse,
    VALID_ENVIRONMENTS,
    VALID_SUITES,
    diagnostic_drift,
    diagnostic_health,
    diagnostic_logs,
    diagnostic_metrics,
    diagnostic_traces,
    get_test_run_status,
    trigger_test_run,
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
    repo._container = AsyncMock()
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
def sample_test_run_doc() -> dict[str, Any]:
    """Sample test run document from Cosmos."""
    return {
        "id": "test_runs:run-abc123",
        "config_type": "test_runs",
        "config_key": "run-abc123",
        "value": {
            "run_id": "run-abc123",
            "environment": "staging",
            "suite": "all",
            "status": "passed",
            "triggered_by": "admin@remaker.digital",
            "started_at": "2026-03-16T10:00:00+00:00",
            "completed_at": "2026-03-16T10:05:00+00:00",
            "total_tests": 1050,
            "passed": 1039,
            "failed": 11,
            "skipped": 0,
            "duration_s": 300.0,
            "failures": [{"test": "ui-selector", "reason": "element not found"}],
            "phases_run": ["phase_a", "phase_b"],
        },
        "version": 2,
        "updated_at": "2026-03-16T10:05:00+00:00",
        "updated_by": "test_pipeline",
    }


# ---------------------------------------------------------------------------
# Test Pipeline Model Tests
# ---------------------------------------------------------------------------


class TestTestPipelineModels:
    """Test model validation for test pipeline."""

    def test_valid_environments(self):
        """Valid environments include staging and production."""
        assert VALID_ENVIRONMENTS == {"staging", "production"}

    def test_valid_suites(self):
        """Valid suites include all expected options."""
        assert "all" in VALID_SUITES
        assert "regression" in VALID_SUITES
        assert "smoke" in VALID_SUITES
        assert "e2e" in VALID_SUITES
        assert "unit" in VALID_SUITES

    def test_test_run_request_defaults(self):
        """Default test run request: environment is empty (server auto-detects), suite=all."""
        req = PipelineRunRequest()
        # Environment is intentionally empty — the server overrides it from
        # its own ENVIRONMENT env var (SPEC-0058 isolation).
        assert req.environment == ""
        assert req.suite == "all"
        assert req.phases == []
        assert req.dry_run is False


# ---------------------------------------------------------------------------
# Test Pipeline Trigger Tests
# ---------------------------------------------------------------------------


class TestTriggerTestRun:
    """Tests for POST /api/superadmin/tests/run."""

    @pytest.mark.asyncio
    async def test_trigger_queues_run(self, mock_platform_repo, mock_audit_repo, mock_tenant_ctx):
        """Trigger creates a queued test run."""
        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit_repo,
        ), patch.dict(
            "os.environ",
            {
                "STAGING_FQDN": "agent-red-staging.test.local",
                "ENVIRONMENT": "staging",
                "INTERNAL_VERIFICATION_SECRET": "test-secret-for-unit-tests",
            },
        ):
            body = PipelineRunRequest(environment="staging", suite="regression")
            result = await trigger_test_run(body, mock_tenant_ctx)

        assert isinstance(result, PipelineRunTriggerResponse)
        assert result.status == "queued"
        assert result.environment == "staging"
        assert result.suite == "regression"
        assert result.run_id.startswith("run-")
        mock_platform_repo.set_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_trigger_dry_run(self, mock_platform_repo, mock_audit_repo, mock_tenant_ctx):
        """Dry run creates record but notes no execution."""
        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit_repo,
        ), patch.dict(
            "os.environ",
            {"ENVIRONMENT": "staging"},
        ):
            body = PipelineRunRequest(environment="staging", dry_run=True)
            result = await trigger_test_run(body, mock_tenant_ctx)

        assert "dry run" in result.message.lower() or "Dry run" in result.message

    @pytest.mark.asyncio
    async def test_trigger_invalid_environment_returns_400(self, mock_tenant_ctx):
        """Invalid environment returns HTTP 400."""
        from fastapi import HTTPException

        body = PipelineRunRequest(environment="local")
        with pytest.raises(HTTPException) as exc_info:
            await trigger_test_run(body, mock_tenant_ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_trigger_invalid_suite_returns_400(self, mock_tenant_ctx):
        """Invalid suite returns HTTP 400."""
        from fastapi import HTTPException

        body = PipelineRunRequest(suite="custom")
        with pytest.raises(HTTPException) as exc_info:
            await trigger_test_run(body, mock_tenant_ctx)
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Test Run Status Tests
# ---------------------------------------------------------------------------


class TestGetTestRunStatus:
    """Tests for GET /api/superadmin/tests/{run_id}/status."""

    @pytest.mark.asyncio
    async def test_get_existing_run(self, mock_platform_repo, sample_test_run_doc):
        """Returns status for existing run."""
        mock_platform_repo.get_config.return_value = sample_test_run_doc

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_test_run_status("run-abc123")

        assert isinstance(result, PipelineRunStatusResponse)
        assert result.run_id == "run-abc123"
        assert result.status == "passed"
        assert result.total_tests == 1050
        assert result.passed == 1039
        assert result.failed == 11

    @pytest.mark.asyncio
    async def test_get_nonexistent_run_returns_404(self, mock_platform_repo):
        """Non-existent run returns HTTP 404."""
        from fastapi import HTTPException

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_test_run_status("run-nonexistent")
            assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Diagnostic Logs Tests
# ---------------------------------------------------------------------------


class TestDiagnosticLogs:
    """Tests for GET /api/superadmin/diagnostics/logs."""

    @pytest.mark.asyncio
    async def test_logs_returns_empty(self, mock_platform_repo):
        """Returns empty when no logs in store."""
        mock_platform_repo._container.query_items.return_value = aiter_empty()

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await diagnostic_logs(
                level="error", since_minutes=60, limit=100,
            )

        assert isinstance(result, DiagnosticLogsResponse)
        assert result.entries == []
        assert result.total == 0
        assert "level" in result.filters_applied

    @pytest.mark.asyncio
    async def test_logs_filters_applied(self, mock_platform_repo):
        """Filters are recorded in response."""
        mock_platform_repo._container.query_items.return_value = aiter_empty()

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await diagnostic_logs(
                level="warning",
                tenant_id="test-tenant",
                service="openai",
                since_minutes=30,
                limit=100,
            )

        assert result.filters_applied["level"] == "warning"
        assert result.filters_applied["tenant_id"] == "test-tenant"
        assert result.filters_applied["service"] == "openai"


# ---------------------------------------------------------------------------
# Diagnostic Traces Tests
# ---------------------------------------------------------------------------


class TestDiagnosticTraces:
    """Tests for GET /api/superadmin/diagnostics/traces."""

    @pytest.mark.asyncio
    async def test_traces_returns_empty(self, mock_platform_repo):
        """Returns empty when no traces in store."""
        mock_platform_repo._container.query_items.return_value = aiter_empty()

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await diagnostic_traces(
                since_minutes=30, limit=50,
            )

        assert isinstance(result, DiagnosticTracesResponse)
        assert result.traces == []
        assert result.total == 0


# ---------------------------------------------------------------------------
# Diagnostic Metrics Tests
# ---------------------------------------------------------------------------


class TestDiagnosticMetrics:
    """Tests for GET /api/superadmin/diagnostics/metrics."""

    @pytest.mark.asyncio
    async def test_metrics_empty_store(self, mock_platform_repo):
        """Returns empty metrics structure when no data collected."""
        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await diagnostic_metrics(since_minutes=60)

        assert isinstance(result, DiagnosticMetricsResponse)
        assert result.latency.get("p50_ms") is None
        assert result.throughput.get("rpm") is None

    @pytest.mark.asyncio
    async def test_metrics_with_data(self, mock_platform_repo):
        """Returns actual metrics when data exists."""
        mock_platform_repo.get_config.return_value = {
            "value": {
                "period_start": "2026-03-16T09:00:00Z",
                "period_end": "2026-03-16T10:00:00Z",
                "latency": {"p50_ms": 120, "p95_ms": 450, "p99_ms": 1200},
                "throughput": {"rpm": 85, "conversations_per_hour": 42},
                "error_rates": {"total": 3, "by_status": {"500": 2, "503": 1}},
                "resource_usage": {"cpu_pct": 35.2, "memory_pct": 58.7},
            },
        }

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await diagnostic_metrics(since_minutes=60)

        assert result.latency["p50_ms"] == 120
        assert result.throughput["rpm"] == 85
        assert result.error_rates["total"] == 3


# ---------------------------------------------------------------------------
# Diagnostic Drift Tests
# ---------------------------------------------------------------------------


class TestDiagnosticDrift:
    """Tests for GET /api/superadmin/diagnostics/drift."""

    @pytest.mark.asyncio
    async def test_drift_all_missing(self, mock_platform_repo):
        """Reports drift when all live documents are missing."""
        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await diagnostic_drift()

        assert isinstance(result, ConfigDriftResponse)
        assert result.total_configs_checked > 0
        assert len(result.drift_entries) > 0
        assert all(e.drift_type == "missing_live" for e in result.drift_entries)

    @pytest.mark.asyncio
    async def test_drift_no_issues(self, mock_platform_repo):
        """Reports healthy when all docs have matching keys."""
        from src.multi_tenant.entitlement_service import FROZEN_ENTITLEMENTS

        async def get_config_with_matching_keys(config_type, config_key):
            frozen_map = {
                "all_tiers": FROZEN_ENTITLEMENTS.get("tiers", {}),
                "pricing": FROZEN_ENTITLEMENTS.get("pricing", {}),
                "pack_pricing": FROZEN_ENTITLEMENTS.get("pack_pricing", {}),
                "sla_targets": FROZEN_ENTITLEMENTS.get("sla_targets", {}),
                "website_limits": FROZEN_ENTITLEMENTS.get("website_limits", {}),
                "integration_gates": FROZEN_ENTITLEMENTS.get("integration_gates", {}),
                "field_gates": FROZEN_ENTITLEMENTS.get("field_gates", {}),
                "global_config": FROZEN_ENTITLEMENTS.get("global_config", {}),
            }
            frozen = frozen_map.get(config_key)
            if frozen is not None:
                return {"value": frozen, "version": 1}
            return None

        mock_platform_repo.get_config.side_effect = get_config_with_matching_keys

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await diagnostic_drift()

        assert result.is_healthy is True
        assert len(result.drift_entries) == 0


# ---------------------------------------------------------------------------
# System Health Tests
# ---------------------------------------------------------------------------


class TestDiagnosticHealth:
    """Tests for GET /api/superadmin/diagnostics/health."""

    @pytest.mark.asyncio
    async def test_health_all_down(self, mock_platform_repo):
        """Reports unhealthy when Cosmos raises."""
        mock_platform_repo.get_config.side_effect = Exception("Cosmos unavailable")

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            side_effect=Exception("Redis unavailable"),
        ), patch(
            "src.multi_tenant.superadmin_api._diagnostics._state._nats_mgr",
            None,
        ), patch(
            "src.multi_tenant.superadmin_api._diagnostics._state._tenant_repo",
            None,
        ):
            result = await diagnostic_health()

        assert isinstance(result, SystemHealthResponse)
        assert result.overall_status in ("unhealthy", "degraded")

    @pytest.mark.asyncio
    async def test_health_cosmos_healthy(self, mock_platform_repo):
        """Reports Cosmos healthy when doc readable."""
        mock_platform_repo.get_config.return_value = {"value": {}}

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            side_effect=Exception("no redis"),
        ), patch(
            "src.multi_tenant.superadmin_api._diagnostics._state._nats_mgr",
            None,
        ), patch(
            "src.multi_tenant.superadmin_api._diagnostics._state._tenant_repo",
            None,
        ):
            result = await diagnostic_health()

        assert result.services["cosmos"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_includes_version(self, mock_platform_repo):
        """Health response includes product version."""
        mock_platform_repo.get_config.return_value = {"value": {}}

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            side_effect=Exception("no redis"),
        ), patch(
            "src.multi_tenant.superadmin_api._diagnostics._state._nats_mgr",
            None,
        ), patch(
            "src.multi_tenant.superadmin_api._diagnostics._state._tenant_repo",
            None,
        ):
            result = await diagnostic_health()

        # version should be a string (could be actual version or "unknown")
        assert isinstance(result.version, str)


# ---------------------------------------------------------------------------
# Async iterator helper
# ---------------------------------------------------------------------------


async def aiter_empty():
    """Async iterator that yields nothing."""
    return
    yield  # makes this an async generator (unreachable by design)


# ---------------------------------------------------------------------------
# Deployment event recording (WI-1285 / SPEC-1779)
# ---------------------------------------------------------------------------


class TestRecordDeploymentEvent:
    """Verify POST /deployments/record records audit events."""

    @pytest.mark.asyncio
    async def test_record_model_deployed(self, mock_tenant_ctx):
        """Successful deployment records MODEL_DEPLOYED audit event."""
        mock_audit = MagicMock()
        mock_audit.log_event = AsyncMock()

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics.get_tenant_context",
            return_value=mock_tenant_ctx,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit,
        ):
            from src.multi_tenant.superadmin_api._diagnostics import (
                DeploymentEventRequest,
                record_deployment_event,
            )

            body = DeploymentEventRequest(
                event_type="model.deployed",
                environment="production",
                version="v1.91.0",
                status="succeeded",
            )
            result = await record_deployment_event(body, ctx=mock_tenant_ctx)

        assert result.recorded is True
        assert result.event_type == "model.deployed"
        assert result.version == "v1.91.0"
        mock_audit.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_invalid_event_type_returns_400(self, mock_tenant_ctx):
        """Invalid event_type raises 400."""
        from src.multi_tenant.superadmin_api._diagnostics import (
            DeploymentEventRequest,
            record_deployment_event,
        )

        body = DeploymentEventRequest(
            event_type="invalid.type",
            environment="staging",
            version="v1.0.0",
        )

        with pytest.raises(HTTPException) as exc_info:
            await record_deployment_event(body, ctx=mock_tenant_ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_record_audit_failure_returns_not_recorded(self, mock_tenant_ctx):
        """Audit log failure returns recorded=False (best-effort)."""
        mock_audit = MagicMock()
        mock_audit.log_event = AsyncMock(side_effect=RuntimeError("Cosmos down"))

        with patch(
            "src.multi_tenant.superadmin_api._diagnostics.get_tenant_context",
            return_value=mock_tenant_ctx,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit,
        ):
            from src.multi_tenant.superadmin_api._diagnostics import (
                DeploymentEventRequest,
                record_deployment_event,
            )

            body = DeploymentEventRequest(
                event_type="model.deployed",
                environment="staging",
                version="v1.90.0",
            )
            result = await record_deployment_event(body, ctx=mock_tenant_ctx)

        assert result.recorded is False
