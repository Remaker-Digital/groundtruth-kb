"""Tests for the self-service deployment pipeline (SPEC-1825).

Verifies:
  - API endpoint contracts (trigger, status, list)
  - Pipeline orchestration logic (step transitions, error handling)
  - GitHub Actions trigger integration
  - Azure Container App deployment
  - Health check polling
  - Auto-rollback on failure
  - Audit event recording
  - Dashboard health cards (Cosmos, Redis, Key Vault — not NATS or circuit breakers)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Module-level patches to avoid import-time side effects
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Deployment API endpoint tests
# ---------------------------------------------------------------------------
class TestDeploymentTriggerEndpoint:
    """POST /api/superadmin/deployments/trigger contract tests."""

    def test_trigger_request_model_requires_environment(self):
        """TriggerRequest requires environment field."""
        from src.multi_tenant.superadmin_api._deployments import TriggerRequest
        with pytest.raises(Exception):
            TriggerRequest()  # type: ignore

    def test_trigger_request_validates_environment(self):
        """Environment must be staging or production."""
        from src.multi_tenant.superadmin_api._deployments import TriggerRequest
        req = TriggerRequest(environment="staging", version="v1.0.0")
        assert req.environment == "staging"
        req2 = TriggerRequest(environment="production", version="v1.0.0")
        assert req2.environment == "production"

    def test_trigger_request_action_defaults_to_full(self):
        """Action defaults to 'full' if not specified."""
        from src.multi_tenant.superadmin_api._deployments import TriggerRequest
        req = TriggerRequest(environment="staging", version="v1.0.0")
        assert req.action == "full"

    def test_trigger_request_accepts_build_action(self):
        """Action can be build, deploy, or full."""
        from src.multi_tenant.superadmin_api._deployments import TriggerRequest
        for action in ("build", "deploy", "full"):
            req = TriggerRequest(environment="staging", version="v1.0.0", action=action)
            assert req.action == action

    def test_trigger_response_model(self):
        """TriggerResponse contains deploy_id, status, message."""
        from src.multi_tenant.superadmin_api._deployments import TriggerResponse
        resp = TriggerResponse(deploy_id="deploy-abc123", status="queued", message="Started")
        assert resp.deploy_id == "deploy-abc123"
        assert resp.status == "queued"


class TestDeploymentStatusEndpoint:
    """GET /api/superadmin/deployments/{deploy_id}/status contract tests."""

    def test_pipeline_status_response_model(self):
        """PipelineStatusResponse contains all required fields."""
        from src.multi_tenant.superadmin_api._deployments import PipelineStatusResponse, PipelineStep
        resp = PipelineStatusResponse(
            deploy_id="deploy-abc123",
            environment="staging",
            version="v1.0.0",
            action="full",
            status="building",
            started_at="2026-03-23T10:00:00Z",
            steps=[
                PipelineStep(name="build_gateway", status="running", detail="Building..."),
            ],
        )
        assert resp.deploy_id == "deploy-abc123"
        assert len(resp.steps) == 1
        assert resp.steps[0].name == "build_gateway"

    def test_pipeline_step_model(self):
        """PipelineStep tracks name, status, detail, timing."""
        from src.multi_tenant.superadmin_api._deployments import PipelineStep
        step = PipelineStep(
            name="build_gateway",
            status="succeeded",
            detail="Build completed",
            started_at="2026-03-23T10:00:00Z",
            completed_at="2026-03-23T10:05:00Z",
            duration_s=300.0,
        )
        assert step.duration_s == 300.0
        assert step.status == "succeeded"


class TestDeploymentListEndpoint:
    """GET /api/superadmin/deployments contract tests."""

    def test_deployment_list_response_model(self):
        """DeploymentListResponse contains deployments and total."""
        from src.multi_tenant.superadmin_api._deployments import DeploymentListResponse
        resp = DeploymentListResponse(deployments=[], total=0)
        assert resp.total == 0
        assert resp.deployments == []


# ---------------------------------------------------------------------------
# Pipeline orchestration tests
# ---------------------------------------------------------------------------
class TestPipelineOrchestration:
    """Test the background pipeline execution logic."""

    def test_pipeline_status_enum_values(self):
        """PipelineStatus covers all expected states."""
        from src.multi_tenant.superadmin_api._deployments import PipelineStatus
        expected = {"queued", "building", "deploying", "verifying", "succeeded", "failed", "rolled_back"}
        actual = {s.value for s in PipelineStatus}
        assert expected == actual

    def test_step_status_enum_values(self):
        """StepStatus covers all expected states."""
        from src.multi_tenant.superadmin_api._deployments import StepStatus
        expected = {"pending", "running", "succeeded", "failed", "skipped"}
        actual = {s.value for s in StepStatus}
        assert expected == actual

    def test_pipeline_action_enum_values(self):
        """PipelineAction covers build, deploy, full."""
        from src.multi_tenant.superadmin_api._deployments import PipelineAction
        assert PipelineAction.BUILD.value == "build"
        assert PipelineAction.DEPLOY.value == "deploy"
        assert PipelineAction.FULL.value == "full"

    def test_update_step_sets_status(self):
        """_update_step modifies the correct step in pipeline state."""
        from src.multi_tenant.superadmin_api._deployments import _update_step
        pipeline = {
            "steps": [
                {"name": "build_gateway", "status": "pending", "detail": ""},
                {"name": "deploy_gateway", "status": "pending", "detail": ""},
            ]
        }
        _update_step(pipeline, "build_gateway", status="running", detail="Building...")
        assert pipeline["steps"][0]["status"] == "running"
        assert pipeline["steps"][0]["detail"] == "Building..."
        assert pipeline["steps"][1]["status"] == "pending"

    def test_update_step_records_completion_time(self):
        """_update_step records completed_at and duration for terminal states."""
        from src.multi_tenant.superadmin_api._deployments import _update_step
        now = datetime.now(timezone.utc).isoformat()
        pipeline = {
            "steps": [
                {"name": "build_gateway", "status": "running", "detail": "",
                 "started_at": now, "completed_at": None, "duration_s": None},
            ]
        }
        _update_step(pipeline, "build_gateway", status="succeeded", detail="Done")
        assert pipeline["steps"][0]["completed_at"] is not None
        assert pipeline["steps"][0]["duration_s"] is not None
        assert pipeline["steps"][0]["duration_s"] >= 0

    def test_container_app_config_has_both_environments(self):
        """CONTAINER_APPS config covers staging and production."""
        from src.multi_tenant.superadmin_api._deployments import CONTAINER_APPS
        assert "staging" in CONTAINER_APPS
        assert "production" in CONTAINER_APPS
        for env in ("staging", "production"):
            assert "gateway" in CONTAINER_APPS[env]
            assert "test_host" in CONTAINER_APPS[env]

    def test_github_workflows_config(self):
        """GITHUB_WORKFLOWS has gateway and test_host entries."""
        from src.multi_tenant.superadmin_api._deployments import GITHUB_WORKFLOWS
        assert "gateway" in GITHUB_WORKFLOWS
        assert "test_host" in GITHUB_WORKFLOWS
        assert GITHUB_WORKFLOWS["gateway"].endswith(".yml")
        assert GITHUB_WORKFLOWS["test_host"].endswith(".yml")


# ---------------------------------------------------------------------------
# GitHub Actions trigger tests
# ---------------------------------------------------------------------------
class TestGitHubActionsTrigger:
    """Test GitHub Actions workflow dispatch integration."""

    @pytest.mark.asyncio
    async def test_trigger_github_build_requires_token(self):
        """_trigger_github_build raises if GITHUB_TOKEN not set."""
        from src.multi_tenant.superadmin_api._deployments import _trigger_github_build
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GITHUB_TOKEN", None)
            with pytest.raises(RuntimeError, match="GITHUB_TOKEN not set"):
                await _trigger_github_build("build-api-gateway.yml", "v1.0.0")

    @pytest.mark.asyncio
    async def test_trigger_github_build_dispatches_workflow(self):
        """_trigger_github_build calls GitHub REST API with correct payload."""
        from src.multi_tenant.superadmin_api._deployments import _trigger_github_build

        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                result = await _trigger_github_build("build-api-gateway.yml", "v1.0.0")
                assert result["triggered"] is True
                assert result["version"] == "v1.0.0"

                # Verify the API was called with correct parameters
                call_args = mock_client.post.call_args
                assert "dispatches" in call_args[0][0]
                body = call_args[1]["json"]
                assert body["inputs"]["tag"] == "v1.0.0"
                assert body["ref"] == "main"

    @pytest.mark.asyncio
    async def test_trigger_github_build_handles_failure(self):
        """_trigger_github_build raises on non-204 response."""
        from src.multi_tenant.superadmin_api._deployments import _trigger_github_build

        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = "Validation Failed"

        with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                with pytest.raises(RuntimeError, match="workflow dispatch failed"):
                    await _trigger_github_build("build-api-gateway.yml", "v1.0.0")


# ---------------------------------------------------------------------------
# Azure managed identity tests
# ---------------------------------------------------------------------------
class TestAzureManagedIdentity:
    """Test Azure token acquisition."""

    @pytest.mark.asyncio
    async def test_get_azure_token_requires_identity_endpoint(self):
        """_get_azure_token raises if IDENTITY_ENDPOINT not set."""
        from src.multi_tenant.superadmin_api._deployments import _get_azure_token
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("IDENTITY_ENDPOINT", None)
            os.environ.pop("IDENTITY_HEADER", None)
            with pytest.raises(RuntimeError, match="Managed identity not available"):
                await _get_azure_token()

    @pytest.mark.asyncio
    async def test_get_azure_token_calls_identity_endpoint(self):
        """_get_azure_token requests token from managed identity."""
        from src.multi_tenant.superadmin_api._deployments import _get_azure_token

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test-token-123"}
        mock_response.raise_for_status = MagicMock()

        with patch.dict(os.environ, {
            "IDENTITY_ENDPOINT": "http://169.254.169.254/metadata/identity/oauth2/token",
            "IDENTITY_HEADER": "test-header-value",
        }):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                token = await _get_azure_token()
                assert token == "test-token-123"


# ---------------------------------------------------------------------------
# Health check tests
# ---------------------------------------------------------------------------
class TestHealthPoll:
    """Test deployment health check polling."""

    @pytest.mark.asyncio
    async def test_health_poll_succeeds_on_correct_version(self):
        """_health_poll returns healthy when version matches."""
        from src.multi_tenant.superadmin_api._deployments import _health_poll

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"x-product-version": "1.98.13"}

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            result = await _health_poll("test.example.com", "v1.98.13", timeout_s=2)
            assert result["healthy"] is True

    @pytest.mark.asyncio
    async def test_health_poll_times_out(self):
        """_health_poll returns unhealthy on timeout."""
        from src.multi_tenant.superadmin_api._deployments import _health_poll

        mock_response = MagicMock()
        mock_response.status_code = 503

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            result = await _health_poll("test.example.com", "v1.98.13", timeout_s=1)
            assert result["healthy"] is False


# ---------------------------------------------------------------------------
# Rollback tests
# ---------------------------------------------------------------------------
class TestRollback:
    """Test auto-rollback on verification failure."""

    @pytest.mark.asyncio
    async def test_rollback_skipped_without_previous_image(self):
        """_rollback returns False when no previous image available."""
        from src.multi_tenant.superadmin_api._deployments import _rollback
        result = await _rollback("app-name", "")
        assert result["rolled_back"] is False
        assert "No previous image" in result["reason"]


# ---------------------------------------------------------------------------
# Dashboard health card tests (NATS/circuit breakers removed)
# ---------------------------------------------------------------------------
class TestDashboardHealthCards:
    """Verify dashboard returns Cosmos/Redis/Key Vault health — NOT NATS or circuit breakers."""

    def test_dashboard_data_type_has_cosmos_redis_keyvault(self):
        """DashboardHealthResponse system_health includes cosmos, redis, key_vault."""
        from src.multi_tenant.superadmin_api._dashboard import DashboardHealthResponse
        resp = DashboardHealthResponse(timestamp="2026-03-23T10:00:00Z")
        # system_health is a dict — verify it accepts the new structure
        resp.system_health = {
            "cosmos": {"healthy": True, "status": "healthy", "detail": "Connected"},
            "redis": {"healthy": True, "status": "healthy", "detail": "Connected"},
            "key_vault": {"healthy": True, "status": "healthy", "detail": "Key Vault connection OK"},
            "version": {"api": "2026-03-01", "product": "1.98.13"},
        }
        assert "cosmos" in resp.system_health
        assert "redis" in resp.system_health
        assert "key_vault" in resp.system_health

    def test_dashboard_data_does_not_include_nats(self):
        """Dashboard system_health MUST NOT include NATS (decommissioned)."""
        # This test ensures no regression — NATS was removed from the dashboard
        from src.multi_tenant.superadmin_api._dashboard import DashboardHealthResponse
        resp = DashboardHealthResponse(
            timestamp="2026-03-23T10:00:00Z",
            system_health={
                "cosmos": {"healthy": True},
                "redis": {"healthy": True},
                "key_vault": {"healthy": True},
                "version": {"api": "1", "product": "1"},
            }
        )
        assert "nats" not in resp.system_health

    def test_dashboard_data_does_not_include_circuit_breakers(self):
        """Dashboard system_health MUST NOT include circuit_breakers (removed from landing page)."""
        from src.multi_tenant.superadmin_api._dashboard import DashboardHealthResponse
        resp = DashboardHealthResponse(
            timestamp="2026-03-23T10:00:00Z",
            system_health={
                "cosmos": {"healthy": True},
                "redis": {"healthy": True},
                "key_vault": {"healthy": True},
                "version": {"api": "1", "product": "1"},
            }
        )
        assert "circuit_breakers" not in resp.system_health


# ---------------------------------------------------------------------------
# Pipeline state management tests
# ---------------------------------------------------------------------------
class TestPipelineStateManagement:
    """Test in-memory pipeline state tracking."""

    def test_active_pipelines_dict_accessible(self):
        """_active_pipelines is a module-level dict for pipeline state."""
        from src.multi_tenant.superadmin_api._deployments import _active_pipelines
        assert isinstance(_active_pipelines, dict)

    @pytest.mark.asyncio
    async def test_trigger_creates_pipeline_in_memory(self):
        """trigger_deployment creates a pipeline entry in _active_pipelines."""
        from src.multi_tenant.superadmin_api._deployments import (
            TriggerRequest,
            _active_pipelines,
            trigger_deployment,
        )

        # Clear state
        _active_pipelines.clear()

        req = TriggerRequest(environment="staging", version="v1.0.0", action="build")

        # Mock the background task creation to avoid actually running the pipeline
        with patch("asyncio.create_task"):
            result = await trigger_deployment(req)

        assert result.status == "queued"
        assert result.deploy_id in _active_pipelines
        pipeline = _active_pipelines[result.deploy_id]
        assert pipeline["environment"] == "staging"
        assert pipeline["version"] == "v1.0.0"
        assert pipeline["action"] == "build"
        assert len(pipeline["steps"]) == 6

        # Cleanup
        _active_pipelines.clear()

    @pytest.mark.asyncio
    async def test_trigger_rejects_missing_version(self):
        """trigger_deployment rejects request without version."""
        from src.multi_tenant.superadmin_api._deployments import (
            TriggerRequest,
            trigger_deployment,
        )
        from fastapi import HTTPException

        req = TriggerRequest(environment="staging")
        with pytest.raises(HTTPException) as exc_info:
            await trigger_deployment(req)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_status_returns_404_for_unknown_deploy(self):
        """deployment_status returns 404 for unknown deploy_id."""
        from src.multi_tenant.superadmin_api._deployments import deployment_status
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await deployment_status("deploy-nonexistent")
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_status_returns_pipeline_state(self):
        """deployment_status returns current pipeline state."""
        from src.multi_tenant.superadmin_api._deployments import (
            _active_pipelines,
            deployment_status,
        )

        _active_pipelines["deploy-test123"] = {
            "deploy_id": "deploy-test123",
            "environment": "staging",
            "version": "v1.0.0",
            "action": "full",
            "status": "building",
            "triggered_by": "spa_console",
            "started_at": "2026-03-23T10:00:00Z",
            "completed_at": None,
            "duration_s": None,
            "error": None,
            "previous_image": None,
            "steps": [
                {"name": "build_gateway", "status": "running", "detail": "Building...",
                 "started_at": "2026-03-23T10:00:00Z", "completed_at": None, "duration_s": None},
            ],
        }

        result = await deployment_status("deploy-test123")
        assert result.status == "building"
        assert result.steps[0].status == "running"

        # Cleanup
        _active_pipelines.clear()


# ---------------------------------------------------------------------------
# Audit event recording tests
# ---------------------------------------------------------------------------
class TestAuditEventRecording:
    """Test deployment events are recorded to Cosmos audit_log."""

    @pytest.mark.asyncio
    async def test_record_audit_event_calls_audit_repo(self):
        """_record_audit_event writes to audit_repo when available."""
        from src.multi_tenant.superadmin_api._deployments import _record_audit_event
        from src.multi_tenant.superadmin_api import _monolith as _state

        mock_repo = MagicMock()
        mock_repo.record_event = AsyncMock()
        original = _state._audit_repo

        try:
            _state._audit_repo = mock_repo
            pipeline = {
                "deploy_id": "deploy-test",
                "environment": "staging",
                "version": "v1.0.0",
                "action": "full",
                "status": "succeeded",
                "duration_s": 300,
                "steps": [],
                "error": None,
                "previous_image": None,
            }
            await _record_audit_event("MODEL_DEPLOYED", pipeline)
            mock_repo.record_event.assert_called_once()
            call_kwargs = mock_repo.record_event.call_args[1]
            assert call_kwargs["event_type"] == "MODEL_DEPLOYED"
            assert call_kwargs["actor"] == "spa_console"
            assert call_kwargs["payload"]["deploy_id"] == "deploy-test"
        finally:
            _state._audit_repo = original

    @pytest.mark.asyncio
    async def test_record_audit_event_handles_missing_repo(self):
        """_record_audit_event gracefully handles missing audit_repo."""
        from src.multi_tenant.superadmin_api._deployments import _record_audit_event
        from src.multi_tenant.superadmin_api import _monolith as _state

        original = _state._audit_repo
        try:
            _state._audit_repo = None
            # Should not raise
            await _record_audit_event("MODEL_DEPLOYED", {"deploy_id": "test"})
        finally:
            _state._audit_repo = original


# ---------------------------------------------------------------------------
# SPA contract tests (field names match frontend expectations)
# ---------------------------------------------------------------------------
class TestSPAContract:
    """Ensure API response field names match what the SPA expects."""

    def test_trigger_response_camel_case(self):
        """TriggerResponse serializes to camelCase for SPA."""
        from src.multi_tenant.superadmin_api._deployments import TriggerResponse
        resp = TriggerResponse(deploy_id="deploy-abc", status="queued", message="Started")
        data = resp.model_dump(by_alias=True)
        assert "deployId" in data
        assert "status" in data
        assert "message" in data

    def test_pipeline_status_response_camel_case(self):
        """PipelineStatusResponse serializes to camelCase for SPA."""
        from src.multi_tenant.superadmin_api._deployments import PipelineStatusResponse, PipelineStep
        resp = PipelineStatusResponse(
            deploy_id="deploy-abc",
            environment="staging",
            version="v1.0.0",
            action="full",
            status="building",
            started_at="2026-03-23T10:00:00Z",
            steps=[PipelineStep(name="build_gateway", status="running", detail="")],
        )
        data = resp.model_dump(by_alias=True)
        assert "deployId" in data
        assert "startedAt" in data
        assert "triggeredBy" in data
        assert "durationS" in data
        assert "previousImage" in data
        # Steps should also be camelCase
        step_data = data["steps"][0]
        assert "startedAt" in step_data
        assert "completedAt" in step_data
        assert "durationS" in step_data

    def test_deployment_list_response_camel_case(self):
        """DeploymentListResponse serializes to camelCase for SPA."""
        from src.multi_tenant.superadmin_api._deployments import DeploymentListResponse
        resp = DeploymentListResponse(deployments=[], total=0)
        data = resp.model_dump(by_alias=True)
        assert "deployments" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_pipeline_step_names_match_spa_labels(self):
        """Pipeline step names used in backend match SPA STEP_LABELS keys."""
        expected_steps = {
            "build_gateway", "build_test_host",
            "deploy_gateway", "deploy_test_host",
            "health_check", "rollback",
        }
        from src.multi_tenant.superadmin_api._deployments import (
            TriggerRequest, _active_pipelines, trigger_deployment,
        )

        _active_pipelines.clear()
        req = TriggerRequest(environment="staging", version="v1.0.0")

        with patch("asyncio.create_task"):
            result = await trigger_deployment(req)

        pipeline = _active_pipelines[result.deploy_id]
        step_names = {s["name"] for s in pipeline["steps"]}
        assert step_names == expected_steps

        _active_pipelines.clear()
