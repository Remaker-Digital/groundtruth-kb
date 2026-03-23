"""Superadmin API -- Self-service deployment pipeline.

Provides API endpoints for the SPA Provider Console to trigger builds,
deployments, and verification — without any local CLI involvement.

Pipeline stages:
  1. BUILD: Trigger GitHub Actions workflow via GitHub REST API
  2. DEPLOY: Update Azure Container App revision via Azure REST API (managed identity)
  3. VERIFY: Health check + optional test suite trigger
  4. ROLLBACK: Auto-rollback on verification failure

All events recorded in Cosmos audit_log for full visibility.

SPEC-1825 / S213
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import httpx
from fastapi import HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.cosmos_schema import AuditEventType

from src.multi_tenant.superadmin_api import _monolith as _state

router = _state.router
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GITHUB_OWNER = "Remaker-Digital"
GITHUB_REPO = "AGNTCY-muti-agent-deployment-customer-service"
ACR_LOGIN_SERVER = "acragentredeastus.azurecr.io"
IMAGE_REPO = "api-gateway"
TEST_HOST_IMAGE_REPO = "test-host"

AZURE_SUBSCRIPTION_ID = os.environ.get(
    "AZURE_SUBSCRIPTION_ID", "4dce2122-690a-4654-b531-cc647db62331"
)
AZURE_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "Agent-Red")

# Container app names per environment
CONTAINER_APPS = {
    "staging": {
        "gateway": "agent-red-staging",
        "test_host": "agent-red-test-host",
    },
    "production": {
        "gateway": "agent-red-api-gateway",
        "test_host": "agent-red-test-host-prod",
    },
}

GITHUB_WORKFLOWS = {
    "gateway": "build-api-gateway.yml",
    "test_host": "build-test-host.yml",
}

HEALTH_TIMEOUT_S = 120
HEALTH_POLL_INTERVAL_S = 10


# ---------------------------------------------------------------------------
# Pipeline state management
# ---------------------------------------------------------------------------
class PipelineAction(str, Enum):
    BUILD = "build"
    DEPLOY = "deploy"
    FULL = "full"  # build + deploy + verify


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineStatus(str, Enum):
    QUEUED = "queued"
    BUILDING = "building"
    DEPLOYING = "deploying"
    VERIFYING = "verifying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


# In-memory pipeline state (also persisted to Cosmos)
_active_pipelines: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
def _detect_environment() -> str:
    """Derive environment from CONTAINER_APP_FQDN. Each instance only knows its own environment."""
    fqdn = os.environ.get("CONTAINER_APP_FQDN", "")
    if "staging" in fqdn.lower():
        return "staging"
    # Default to production — the production FQDN doesn't contain "staging"
    return "production"


class TriggerRequest(CamelCaseModel):
    """Request to trigger a deployment pipeline.

    Environment is NOT accepted from the client — it is auto-detected from
    CONTAINER_APP_FQDN to enforce environment isolation (SPEC-0058).
    """
    version: str | None = Field(None, description="Version tag (e.g. v1.98.15). If omitted, uses latest from ACR.")
    action: str = Field("full", pattern="^(build|deploy|full)$")


class PipelineStep(CamelCaseModel):
    """Status of a single pipeline step."""
    name: str
    status: str = "pending"
    detail: str = ""
    started_at: str | None = None
    completed_at: str | None = None
    duration_s: float | None = None


class PipelineStatusResponse(CamelCaseModel):
    """Full pipeline status for a deployment."""
    deploy_id: str
    environment: str
    version: str
    action: str
    status: str
    triggered_by: str = "spa_console"
    started_at: str
    completed_at: str | None = None
    duration_s: float | None = None
    steps: list[PipelineStep] = Field(default_factory=list)
    error: str | None = None
    previous_image: str | None = None


class DeploymentListResponse(CamelCaseModel):
    """List of deployment records."""
    deployments: list[PipelineStatusResponse] = Field(default_factory=list)
    total: int = 0


class TriggerResponse(CamelCaseModel):
    """Response after triggering a deployment."""
    deploy_id: str
    status: str
    message: str


# ---------------------------------------------------------------------------
# Azure managed identity token acquisition
# ---------------------------------------------------------------------------
async def _get_azure_token(resource: str = "https://management.azure.com") -> str:
    """Get access token from managed identity endpoint."""
    identity_endpoint = os.environ.get("IDENTITY_ENDPOINT")
    identity_header = os.environ.get("IDENTITY_HEADER")

    if not identity_endpoint or not identity_header:
        raise RuntimeError(
            "Managed identity not available (IDENTITY_ENDPOINT not set). "
            "Ensure the container app has a managed identity assigned."
        )

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            identity_endpoint,
            params={"resource": resource, "api-version": "2019-08-01"},
            headers={"X-IDENTITY-HEADER": identity_header},
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# GitHub Actions trigger
# ---------------------------------------------------------------------------
async def _trigger_github_build(
    workflow_file: str, version: str
) -> dict[str, Any]:
    """Trigger a GitHub Actions workflow_dispatch and return run info."""
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise RuntimeError(
            "GITHUB_TOKEN not set. Cannot trigger builds. "
            "Set this env var on the container app."
        )

    url = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/actions/workflows/{workflow_file}/dispatches"
    )
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    body = {
        "ref": "main",
        "inputs": {"tag": version},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=body, headers=headers)
        if resp.status_code == 204:
            return {"triggered": True, "workflow": workflow_file, "version": version}
        else:
            raise RuntimeError(
                f"GitHub workflow dispatch failed: {resp.status_code} {resp.text}"
            )


async def _poll_github_workflow(
    workflow_file: str, version: str, timeout_s: int = 600
) -> dict[str, Any]:
    """Poll GitHub Actions for workflow completion."""
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise RuntimeError("GITHUB_TOKEN not set")

    # Wait a moment for the run to appear
    await asyncio.sleep(5)

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/actions/workflows/{workflow_file}/runs?per_page=5"
    )

    deadline = asyncio.get_event_loop().time() + timeout_s
    async with httpx.AsyncClient(timeout=30) as client:
        while asyncio.get_event_loop().time() < deadline:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                runs = resp.json().get("workflow_runs", [])
                # Find the most recent run
                for run in runs:
                    if run.get("status") == "completed":
                        conclusion = run.get("conclusion", "unknown")
                        return {
                            "completed": True,
                            "conclusion": conclusion,
                            "run_id": run.get("id"),
                            "html_url": run.get("html_url", ""),
                        }
                    elif run.get("status") in ("queued", "in_progress"):
                        break  # Still running, keep polling
            await asyncio.sleep(15)

    return {"completed": False, "conclusion": "timeout", "run_id": None}


# ---------------------------------------------------------------------------
# Azure Container App deployment
# ---------------------------------------------------------------------------
async def _deploy_container_app(
    app_name: str, image: str
) -> dict[str, Any]:
    """Update container app to use new image via Azure REST API."""
    token = await _get_azure_token()

    url = (
        f"https://management.azure.com"
        f"/subscriptions/{AZURE_SUBSCRIPTION_ID}"
        f"/resourceGroups/{AZURE_RESOURCE_GROUP}"
        f"/providers/Microsoft.App/containerApps/{app_name}"
        f"?api-version=2024-03-01"
    )

    # First, GET current config
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        get_resp = await client.get(url, headers=headers)
        get_resp.raise_for_status()
        current = get_resp.json()

    # Extract previous image for rollback info
    containers = (
        current.get("properties", {})
        .get("template", {})
        .get("containers", [])
    )
    previous_image = containers[0].get("image", "") if containers else ""

    # Update image in container spec
    if containers:
        containers[0]["image"] = image

    # PATCH with updated config
    patch_body = {
        "properties": {
            "template": current["properties"]["template"]
        }
    }

    async with httpx.AsyncClient(timeout=60) as client:
        patch_resp = await client.patch(
            url,
            json=patch_body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        patch_resp.raise_for_status()
        result = patch_resp.json()

    revision = (
        result.get("properties", {})
        .get("latestRevisionName", "unknown")
    )

    return {
        "deployed": True,
        "app_name": app_name,
        "image": image,
        "previous_image": previous_image,
        "revision": revision,
    }


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
async def _health_poll(
    fqdn: str, expected_version: str, timeout_s: int = HEALTH_TIMEOUT_S
) -> dict[str, Any]:
    """Poll /health endpoint until it returns 200 with correct version."""
    url = f"https://{fqdn}/health"
    deadline = asyncio.get_event_loop().time() + timeout_s

    async with httpx.AsyncClient(timeout=10, verify=True) as client:
        while asyncio.get_event_loop().time() < deadline:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    version_header = resp.headers.get("x-product-version", "")
                    if expected_version.lstrip("v") in version_header:
                        return {"healthy": True, "version": version_header}
            except Exception:
                pass
            await asyncio.sleep(HEALTH_POLL_INTERVAL_S)

    return {"healthy": False, "version": None, "error": "Health poll timeout"}


# ---------------------------------------------------------------------------
# Rollback
# ---------------------------------------------------------------------------
async def _rollback(app_name: str, previous_image: str) -> dict[str, Any]:
    """Roll back to previous image."""
    if not previous_image:
        return {"rolled_back": False, "reason": "No previous image available"}
    try:
        result = await _deploy_container_app(app_name, previous_image)
        return {"rolled_back": True, "image": previous_image, "revision": result.get("revision")}
    except Exception as exc:
        return {"rolled_back": False, "reason": str(exc)}


# ---------------------------------------------------------------------------
# Pipeline orchestrator (runs as background task)
# ---------------------------------------------------------------------------
def _update_step(pipeline: dict, step_name: str, **kwargs: Any) -> None:
    """Update a step in the pipeline state."""
    for step in pipeline["steps"]:
        if step["name"] == step_name:
            step.update(kwargs)
            if kwargs.get("status") in ("succeeded", "failed", "skipped"):
                step["completed_at"] = datetime.now(timezone.utc).isoformat()
                if step.get("started_at"):
                    start = datetime.fromisoformat(step["started_at"])
                    step["duration_s"] = round(
                        (datetime.now(timezone.utc) - start).total_seconds(), 1
                    )
            break


async def _record_audit_event(
    event_type: str, pipeline: dict
) -> None:
    """Record a deployment event to Cosmos audit_log."""
    if _state._audit_repo is None:
        logger.warning("Audit repo not initialized, skipping deployment event recording")
        return
    try:
        await _state._audit_repo.record_event(
            event_type=event_type,
            actor="spa_console",
            payload={
                "deploy_id": pipeline["deploy_id"],
                "environment": pipeline["environment"],
                "version": pipeline["version"],
                "action": pipeline["action"],
                "status": pipeline["status"],
                "duration_s": pipeline.get("duration_s"),
                "steps": pipeline["steps"],
                "error": pipeline.get("error"),
                "previous_image": pipeline.get("previous_image"),
            },
        )
    except Exception as exc:
        logger.error("Failed to record deployment audit event: %s", exc)


async def _persist_pipeline_state(pipeline: dict) -> None:
    """Persist pipeline state to Cosmos for SPA polling."""
    if _state._audit_repo is None:
        return
    try:
        # Use audit_log with a special event type for in-progress pipelines
        await _state._audit_repo.record_event(
            event_type="DEPLOYMENT_PIPELINE_STATE",
            actor="spa_console",
            payload=pipeline,
        )
    except Exception as exc:
        logger.error("Failed to persist pipeline state: %s", exc)


async def _run_pipeline(pipeline: dict) -> None:
    """Execute the full deployment pipeline in the background."""
    try:
        env = pipeline["environment"]
        version = pipeline["version"]
        action = pipeline["action"]
        app_config = CONTAINER_APPS.get(env, {})
        gateway_app = app_config.get("gateway", "")
        test_host_app = app_config.get("test_host", "")
        image = f"{ACR_LOGIN_SERVER}/{IMAGE_REPO}:{version}"
        test_host_image = f"{ACR_LOGIN_SERVER}/{TEST_HOST_IMAGE_REPO}:{version}"

        # ------------------------------------------------------------------
        # Step 1: Build (if action is build or full)
        # ------------------------------------------------------------------
        if action in ("build", "full"):
            pipeline["status"] = PipelineStatus.BUILDING.value
            _update_step(pipeline, "build_gateway",
                         status="running",
                         started_at=datetime.now(timezone.utc).isoformat())
            await _persist_pipeline_state(pipeline)

            try:
                await _trigger_github_build(GITHUB_WORKFLOWS["gateway"], version)
                _update_step(pipeline, "build_gateway", detail="Workflow dispatched, polling...")
                await _persist_pipeline_state(pipeline)

                result = await _poll_github_workflow(
                    GITHUB_WORKFLOWS["gateway"], version, timeout_s=600
                )
                if result.get("conclusion") == "success":
                    _update_step(pipeline, "build_gateway",
                                 status="succeeded",
                                 detail=f"Build completed (run {result.get('run_id', '?')})")
                else:
                    _update_step(pipeline, "build_gateway",
                                 status="failed",
                                 detail=f"Build {result.get('conclusion', 'failed')}")
                    pipeline["status"] = PipelineStatus.FAILED.value
                    pipeline["error"] = f"Gateway build failed: {result.get('conclusion')}"
                    await _persist_pipeline_state(pipeline)
                    await _record_audit_event("DEPLOYMENT_FAILED", pipeline)
                    return
            except Exception as exc:
                _update_step(pipeline, "build_gateway",
                             status="failed", detail=str(exc)[:200])
                pipeline["status"] = PipelineStatus.FAILED.value
                pipeline["error"] = f"Gateway build error: {str(exc)[:200]}"
                await _persist_pipeline_state(pipeline)
                await _record_audit_event("DEPLOYMENT_FAILED", pipeline)
                return

            # Build test host too
            _update_step(pipeline, "build_test_host",
                         status="running",
                         started_at=datetime.now(timezone.utc).isoformat())
            await _persist_pipeline_state(pipeline)

            try:
                await _trigger_github_build(GITHUB_WORKFLOWS["test_host"], version)
                result = await _poll_github_workflow(
                    GITHUB_WORKFLOWS["test_host"], version, timeout_s=600
                )
                if result.get("conclusion") == "success":
                    _update_step(pipeline, "build_test_host",
                                 status="succeeded",
                                 detail=f"Build completed (run {result.get('run_id', '?')})")
                else:
                    _update_step(pipeline, "build_test_host",
                                 status="failed",
                                 detail=f"Build {result.get('conclusion', 'failed')}")
                    # Test host build failure is non-fatal — continue deploy
                    logger.warning("Test host build failed, continuing with gateway deploy")
            except Exception as exc:
                _update_step(pipeline, "build_test_host",
                             status="failed", detail=str(exc)[:200])
                logger.warning("Test host build failed: %s", exc)
        else:
            # Skip build steps
            _update_step(pipeline, "build_gateway", status="skipped")
            _update_step(pipeline, "build_test_host", status="skipped")

        # ------------------------------------------------------------------
        # Step 2: Deploy (if action is deploy or full)
        # ------------------------------------------------------------------
        if action in ("deploy", "full"):
            pipeline["status"] = PipelineStatus.DEPLOYING.value
            _update_step(pipeline, "deploy_gateway",
                         status="running",
                         started_at=datetime.now(timezone.utc).isoformat())
            await _persist_pipeline_state(pipeline)

            try:
                deploy_result = await _deploy_container_app(gateway_app, image)
                pipeline["previous_image"] = deploy_result.get("previous_image")
                _update_step(pipeline, "deploy_gateway",
                             status="succeeded",
                             detail=f"Revision: {deploy_result.get('revision', '?')}")
            except Exception as exc:
                _update_step(pipeline, "deploy_gateway",
                             status="failed", detail=str(exc)[:200])
                pipeline["status"] = PipelineStatus.FAILED.value
                pipeline["error"] = f"Gateway deploy error: {str(exc)[:200]}"
                await _persist_pipeline_state(pipeline)
                await _record_audit_event("DEPLOYMENT_FAILED", pipeline)
                return

            # Deploy test host (non-fatal if it fails)
            _update_step(pipeline, "deploy_test_host",
                         status="running",
                         started_at=datetime.now(timezone.utc).isoformat())
            await _persist_pipeline_state(pipeline)

            try:
                await _deploy_container_app(test_host_app, test_host_image)
                _update_step(pipeline, "deploy_test_host", status="succeeded")
            except Exception as exc:
                _update_step(pipeline, "deploy_test_host",
                             status="failed", detail=str(exc)[:200])
                logger.warning("Test host deploy failed: %s", exc)

            # ------------------------------------------------------------------
            # Step 3: Verify health
            # ------------------------------------------------------------------
            pipeline["status"] = PipelineStatus.VERIFYING.value
            _update_step(pipeline, "health_check",
                         status="running",
                         started_at=datetime.now(timezone.utc).isoformat())
            await _persist_pipeline_state(pipeline)

            fqdn = os.environ.get("CONTAINER_APP_FQDN", "")
            if fqdn:
                health_result = await _health_poll(fqdn, version)
                if health_result.get("healthy"):
                    _update_step(pipeline, "health_check",
                                 status="succeeded",
                                 detail=f"Version {health_result.get('version', '?')} healthy")
                else:
                    _update_step(pipeline, "health_check",
                                 status="failed",
                                 detail=health_result.get("error", "Unhealthy"))

                    # Auto-rollback
                    _update_step(pipeline, "rollback",
                                 status="running",
                                 started_at=datetime.now(timezone.utc).isoformat())
                    await _persist_pipeline_state(pipeline)

                    rollback_result = await _rollback(
                        gateway_app, pipeline.get("previous_image", "")
                    )
                    if rollback_result.get("rolled_back"):
                        _update_step(pipeline, "rollback",
                                     status="succeeded",
                                     detail=f"Rolled back to {pipeline.get('previous_image', '?')}")
                        pipeline["status"] = PipelineStatus.ROLLED_BACK.value
                    else:
                        _update_step(pipeline, "rollback",
                                     status="failed",
                                     detail=rollback_result.get("reason", "Rollback failed"))
                        pipeline["status"] = PipelineStatus.FAILED.value

                    pipeline["error"] = "Health check failed after deploy"
                    await _persist_pipeline_state(pipeline)
                    await _record_audit_event(
                        AuditEventType.MODEL_ROLLED_BACK.value
                        if pipeline["status"] == PipelineStatus.ROLLED_BACK.value
                        else "DEPLOYMENT_FAILED",
                        pipeline
                    )
                    return
            else:
                _update_step(pipeline, "health_check",
                             status="skipped",
                             detail="CONTAINER_APP_FQDN not set")
        else:
            # Skip deploy steps
            _update_step(pipeline, "deploy_gateway", status="skipped")
            _update_step(pipeline, "deploy_test_host", status="skipped")
            _update_step(pipeline, "health_check", status="skipped")

        # ------------------------------------------------------------------
        # Success
        # ------------------------------------------------------------------
        _update_step(pipeline, "rollback", status="skipped", detail="Not needed")
        pipeline["status"] = PipelineStatus.SUCCEEDED.value
        pipeline["completed_at"] = datetime.now(timezone.utc).isoformat()
        start = datetime.fromisoformat(pipeline["started_at"])
        pipeline["duration_s"] = round(
            (datetime.now(timezone.utc) - start).total_seconds(), 1
        )
        await _persist_pipeline_state(pipeline)
        await _record_audit_event(AuditEventType.MODEL_DEPLOYED.value, pipeline)
        logger.info(
            "Deployment pipeline %s completed: %s %s → %s in %.1fs",
            pipeline["deploy_id"], env, version,
            pipeline["status"], pipeline["duration_s"],
        )

    except Exception as exc:
        pipeline["status"] = PipelineStatus.FAILED.value
        pipeline["error"] = f"Unexpected pipeline error: {str(exc)[:300]}"
        pipeline["completed_at"] = datetime.now(timezone.utc).isoformat()
        await _persist_pipeline_state(pipeline)
        await _record_audit_event("DEPLOYMENT_FAILED", pipeline)
        logger.exception("Deployment pipeline %s failed unexpectedly", pipeline["deploy_id"])


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/deployments/trigger",
    response_model=TriggerResponse,
    summary="Trigger deployment pipeline",
    description="Start a build, deploy, or full pipeline for an environment.",
    status_code=202,
)
async def trigger_deployment(
    request: TriggerRequest,
) -> TriggerResponse:
    """Trigger a deployment pipeline from the SPA console.

    Environment is auto-detected from CONTAINER_APP_FQDN — the client cannot
    specify it. Each environment can only deploy to itself (SPEC-0058).
    """
    deploy_id = f"deploy-{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    version = request.version or ""
    environment = _detect_environment()

    if not version:
        raise HTTPException(
            status_code=400,
            detail="Version is required (e.g. v1.98.15). Automatic latest detection not yet implemented."
        )

    # Validate version format
    if not version.startswith("v"):
        version = f"v{version}"

    # Create pipeline state
    pipeline: dict[str, Any] = {
        "deploy_id": deploy_id,
        "environment": environment,
        "version": version,
        "action": request.action,
        "status": PipelineStatus.QUEUED.value,
        "triggered_by": "spa_console",
        "started_at": now,
        "completed_at": None,
        "duration_s": None,
        "error": None,
        "previous_image": None,
        "steps": [
            {"name": "build_gateway", "status": "pending", "detail": ""},
            {"name": "build_test_host", "status": "pending", "detail": ""},
            {"name": "deploy_gateway", "status": "pending", "detail": ""},
            {"name": "deploy_test_host", "status": "pending", "detail": ""},
            {"name": "health_check", "status": "pending", "detail": ""},
            {"name": "rollback", "status": "pending", "detail": ""},
        ],
    }

    _active_pipelines[deploy_id] = pipeline

    # Launch pipeline in background
    asyncio.create_task(_run_pipeline(pipeline))

    logger.info(
        "Deployment pipeline %s triggered: %s %s %s",
        deploy_id, request.action, environment, version,
    )

    return TriggerResponse(
        deploy_id=deploy_id,
        status="queued",
        message=f"Pipeline {request.action} started for {environment} {version}",
    )


@router.get(
    "/deployments/{deploy_id}/status",
    response_model=PipelineStatusResponse,
    summary="Get deployment pipeline status",
    description="Poll the status of an active or completed deployment pipeline.",
    status_code=200,
)
async def deployment_status(
    deploy_id: str,
) -> PipelineStatusResponse:
    """Get the current status of a deployment pipeline."""
    pipeline = _active_pipelines.get(deploy_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail=f"Deployment {deploy_id} not found")

    return PipelineStatusResponse(
        deploy_id=pipeline["deploy_id"],
        environment=pipeline["environment"],
        version=pipeline["version"],
        action=pipeline["action"],
        status=pipeline["status"],
        triggered_by=pipeline.get("triggered_by", "spa_console"),
        started_at=pipeline["started_at"],
        completed_at=pipeline.get("completed_at"),
        duration_s=pipeline.get("duration_s"),
        steps=[PipelineStep(**s) for s in pipeline.get("steps", [])],
        error=pipeline.get("error"),
        previous_image=pipeline.get("previous_image"),
    )


@router.get(
    "/deployments",
    response_model=DeploymentListResponse,
    summary="List deployment records",
    description="List recent deployment events from audit log and active pipelines.",
    status_code=200,
)
async def list_deployments(
    limit: int = Query(20, ge=1, le=100),
) -> DeploymentListResponse:
    """List deployment history from Cosmos + active in-memory pipelines."""
    deployments: list[PipelineStatusResponse] = []

    # Include active in-memory pipelines first
    for pipeline in sorted(
        _active_pipelines.values(),
        key=lambda p: p.get("started_at", ""),
        reverse=True,
    ):
        deployments.append(PipelineStatusResponse(
            deploy_id=pipeline["deploy_id"],
            environment=pipeline["environment"],
            version=pipeline["version"],
            action=pipeline["action"],
            status=pipeline["status"],
            triggered_by=pipeline.get("triggered_by", "spa_console"),
            started_at=pipeline["started_at"],
            completed_at=pipeline.get("completed_at"),
            duration_s=pipeline.get("duration_s"),
            steps=[PipelineStep(**s) for s in pipeline.get("steps", [])],
            error=pipeline.get("error"),
            previous_image=pipeline.get("previous_image"),
        ))

    # Also query Cosmos for historical deployments not in memory
    if _state._audit_repo is not None:
        try:
            deploy_types = [
                AuditEventType.MODEL_DEPLOYED.value,
                AuditEventType.MODEL_ROLLED_BACK.value,
                "DEPLOYMENT_FAILED",
                "DEPLOYMENT_PIPELINE_STATE",
            ]
            query = (
                "SELECT c.event_type, c.timestamp, c.actor, c.payload "
                "FROM c WHERE c.event_type IN (@t1, @t2, @t3, @t4) "
                "ORDER BY c.timestamp DESC "
                f"OFFSET 0 LIMIT {limit}"
            )
            params = [
                {"name": "@t1", "value": deploy_types[0]},
                {"name": "@t2", "value": deploy_types[1]},
                {"name": "@t3", "value": deploy_types[2]},
                {"name": "@t4", "value": deploy_types[3]},
            ]

            seen_ids = {d.deploy_id for d in deployments}
            async for item in _state._audit_repo._container.query_items(
                query=query, parameters=params, max_item_count=limit,
            ):
                payload = item.get("payload", {})
                did = payload.get("deploy_id", "")
                if did and did not in seen_ids:
                    seen_ids.add(did)
                    deployments.append(PipelineStatusResponse(
                        deploy_id=did,
                        environment=payload.get("environment", "unknown"),
                        version=payload.get("version", "unknown"),
                        action=payload.get("action", "unknown"),
                        status=payload.get("status", item.get("event_type", "unknown")),
                        triggered_by=item.get("actor", "system"),
                        started_at=payload.get("started_at", item.get("timestamp", "")),
                        completed_at=payload.get("completed_at"),
                        duration_s=payload.get("duration_s"),
                        steps=[PipelineStep(**s) for s in payload.get("steps", [])],
                        error=payload.get("error"),
                        previous_image=payload.get("previous_image"),
                    ))
        except Exception as exc:
            logger.warning("Failed to query deployment history from Cosmos: %s", exc)

    # Sort by started_at descending and limit
    deployments.sort(key=lambda d: d.started_at or "", reverse=True)
    deployments = deployments[:limit]

    return DeploymentListResponse(
        deployments=deployments,
        total=len(deployments),
    )
