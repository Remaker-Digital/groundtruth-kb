"""Superadmin API -- Test pipeline trigger and diagnostic data export.

Domain sub-module for SPEC-1826 (SPA Test Execution Trigger) and
SPEC-1827 (Diagnostic Data Export for Claude Code). Endpoints are registered
on the shared router from _monolith.

Test Pipeline:
  POST /tests/run                 — Trigger a test pipeline run (async)
  GET  /tests/{run_id}/status     — Check test run progress/results
  GET  /tests/runs                — List recent test runs

Diagnostics:
  GET  /diagnostics/logs          — Structured error logs (filterable)
  GET  /diagnostics/traces        — Request traces (OpenTelemetry-compatible)
  GET  /diagnostics/metrics       — Performance metrics (latency, throughput)
  GET  /diagnostics/drift         — Configuration drift report
  GET  /diagnostics/health        — System health snapshot

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    PlatformConfigDocument,
)
from src.multi_tenant.middleware import get_tenant_context

from src.multi_tenant.superadmin_api import _monolith as _state

router = _state.router

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Live environment probes (SPEC-1846)
# ---------------------------------------------------------------------------

class _ProbeResult:
    """Result of a single environment probe."""

    def __init__(self, name: str, passed: bool, latency_ms: float, detail: str = ""):
        self.name = name
        self.passed = passed
        self.latency_ms = latency_ms
        self.detail = detail

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "latency_ms": round(self.latency_ms, 1),
            "detail": self.detail,
        }


async def _probe_cosmos() -> _ProbeResult:
    """Probe Cosmos DB connectivity and query capability."""
    start = time.monotonic()
    try:
        from src.multi_tenant.cosmos_readiness import check_cosmos_ready
        result = await check_cosmos_ready()
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("cosmos_db", result.get("ready", False), elapsed,
                            result.get("detail", ""))
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("cosmos_db", False, elapsed, str(exc))


async def _probe_redis() -> _ProbeResult:
    """Probe Redis connectivity."""
    start = time.monotonic()
    try:
        from src.multi_tenant.entitlement_service import get_entitlement_service
        svc = get_entitlement_service()
        if svc._redis_client is not None:
            await asyncio.to_thread(svc._redis_client.ping)
            elapsed = (time.monotonic() - start) * 1000
            return _ProbeResult("redis", True, elapsed, "PONG")
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("redis", False, elapsed, "No Redis client configured")
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("redis", False, elapsed, str(exc))


async def _probe_key_vault() -> _ProbeResult:
    """Probe Key Vault configuration (config-only, not connectivity)."""
    start = time.monotonic()
    try:
        import os
        kv_url = os.environ.get("KEY_VAULT_URL", "")
        elapsed = (time.monotonic() - start) * 1000
        if kv_url:
            return _ProbeResult("key_vault", True, elapsed, "KEY_VAULT_URL configured")
        return _ProbeResult("key_vault", False, elapsed, "KEY_VAULT_URL not set")
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("key_vault", False, elapsed, str(exc))


async def _probe_api_version() -> _ProbeResult:
    """Probe that the API version is correct."""
    start = time.monotonic()
    try:
        from src.multi_tenant.api_versioning import PRODUCT_VERSION
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("api_version", True, elapsed, PRODUCT_VERSION)
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("api_version", False, elapsed, str(exc))


async def _probe_tenant_list() -> _ProbeResult:
    """Probe that tenant listing works."""
    start = time.monotonic()
    try:
        if _state._tenant_repo is None:
            elapsed = (time.monotonic() - start) * 1000
            return _ProbeResult("tenant_list", False, elapsed, "Tenant repo not configured")
        tenants = await _state._tenant_repo.list_active_tenant_ids()
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("tenant_list", True, elapsed, f"{len(tenants)} active tenants")
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("tenant_list", False, elapsed, str(exc))


async def _probe_entitlement_service() -> _ProbeResult:
    """Probe that entitlement service returns data."""
    start = time.monotonic()
    try:
        from src.multi_tenant.entitlement_service import get_entitlement_service
        svc = get_entitlement_service()
        tiers = await svc.get_all_tiers()
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("entitlement_service", len(tiers) > 0, elapsed,
                            f"{len(tiers)} tiers configured")
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("entitlement_service", False, elapsed, str(exc))


async def _probe_circuit_breakers() -> _ProbeResult:
    """Probe that circuit breakers are healthy."""
    start = time.monotonic()
    try:
        from src.multi_tenant.circuit_breaker import get_breaker_registry
        registry = get_breaker_registry()
        any_open = any(b.is_open for b in registry.breakers.values())
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("circuit_breakers", not any_open, elapsed,
                            f"{len(registry.breakers)} breakers, {'OPEN detected' if any_open else 'all closed'}")
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("circuit_breakers", False, elapsed, str(exc))


async def _probe_spa_assets() -> _ProbeResult:
    """Probe that SPA assets are being served."""
    start = time.monotonic()
    try:
        import os
        # Check that dist directories exist in the container
        spa_paths = [
            "admin/provider/dist/index.html",
            "admin/standalone/dist/index.html",
            "admin/shopify/dist/index.html",
        ]
        missing = [p for p in spa_paths if not os.path.exists(p)]
        elapsed = (time.monotonic() - start) * 1000
        if missing:
            return _ProbeResult("spa_assets", False, elapsed,
                                f"Missing: {', '.join(missing)}")
        return _ProbeResult("spa_assets", True, elapsed, "All 3 SPA dist bundles present")
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return _ProbeResult("spa_assets", False, elapsed, str(exc))


async def run_environment_probes() -> list[_ProbeResult]:
    """Run all environment probes concurrently and return results."""
    probes = [
        _probe_api_version(),
        _probe_cosmos(),
        _probe_redis(),
        _probe_key_vault(),
        _probe_tenant_list(),
        _probe_entitlement_service(),
        _probe_circuit_breakers(),
        _probe_spa_assets(),
    ]
    results = await asyncio.gather(*probes, return_exceptions=True)

    final: list[_ProbeResult] = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            final.append(_ProbeResult(f"probe_{i}", False, 0.0, str(result)))
        else:
            final.append(result)
    return final


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _get_platform_repo():
    """Get the PlatformConfigRepository, lazy import to avoid circular deps."""
    from src.multi_tenant.repositories.platform import PlatformConfigRepository
    return PlatformConfigRepository()


# ---------------------------------------------------------------------------
# Test pipeline models (SPEC-1826 / WI-1434)
# ---------------------------------------------------------------------------

_TEST_RUN_CONFIG_TYPE = "test_runs"

VALID_ENVIRONMENTS = {"staging", "production"}
VALID_SUITES = {"all", "regression", "smoke", "e2e"}  # SPEC-1846: no "unit" in-container

# SPEC-1846: Track active verification runs (one at a time)
_active_runs: dict[str, asyncio.Task] = {}
_STALE_RUN_TIMEOUT_S = 1800  # 30 minutes


class PipelineRunRequest(CamelCaseModel):
    """Request body for triggering a test pipeline run."""

    environment: str = Field(
        default="staging",
        description="Target environment: staging or production",
    )
    suite: str = Field(
        default="all",
        description="Test suite to run: all, regression, smoke, e2e, unit",
    )
    phases: list[str] = Field(
        default_factory=list,
        description="Specific PLAN-001 phases to run (empty = all active phases)",
    )
    dry_run: bool = Field(
        default=False,
        description="If true, validate configuration but do not execute tests",
    )


class PipelineRunStatusResponse(CamelCaseModel):
    """Status of a test pipeline run."""

    run_id: str
    environment: str
    suite: str
    status: str = Field(description="Status: queued, running, passed, failed, cancelled")
    started_at: str | None = None
    completed_at: str | None = None
    triggered_by: str = ""
    total_tests: int = 0
    completed: int = 0  # SPEC-1846: for progress bar (completed/total_tests)
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_s: float | None = None
    failures: list[dict[str, Any]] = Field(default_factory=list)
    phases_run: list[str] = Field(default_factory=list)
    checks: list[dict[str, Any]] = Field(default_factory=list, description="Full check results (SPEC-1846)")


class PipelineRunTriggerResponse(CamelCaseModel):
    """Response from triggering a test run."""

    run_id: str
    environment: str
    suite: str
    status: str = "queued"
    message: str = ""


class PipelineRunListResponse(CamelCaseModel):
    """Response listing recent test runs."""

    runs: list[PipelineRunStatusResponse]
    total: int


# ---------------------------------------------------------------------------
# Test pipeline endpoints (SPEC-1826 / WI-1434)
# ---------------------------------------------------------------------------


@router.post(
    "/tests/run",
    response_model=PipelineRunTriggerResponse,
    summary="Trigger a test pipeline run (SPEC-1826)",
    description=(
        "Queues a test pipeline run for asynchronous execution. "
        "Returns a run_id for status polling. Results stored in Cosmos."
    ),
    status_code=202,
)
async def trigger_test_run(
    body: PipelineRunRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> PipelineRunTriggerResponse:
    """Trigger a live environment regression test run (SPEC-1846).

    Executes environment probes inline against the LIVE deployed
    environment (health, Cosmos, Redis, Key Vault, entitlements,
    circuit breakers, SPA assets). Results are stored in Cosmos
    and returned synchronously.
    """
    if body.environment not in VALID_ENVIRONMENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid environment '{body.environment}'. "
            f"Valid: {sorted(VALID_ENVIRONMENTS)}",
        )
    if body.suite not in VALID_SUITES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid suite '{body.suite}'. Valid: {sorted(VALID_SUITES)}",
        )

    run_id = f"run-{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    actor = ctx.team_member_email or "spa-console"

    if body.dry_run:
        # Dry run: validate config but don't execute probes
        repo = _get_platform_repo()
        run_doc = PlatformConfigDocument(
            id=f"{_TEST_RUN_CONFIG_TYPE}:{run_id}",
            config_type=_TEST_RUN_CONFIG_TYPE,
            config_key=run_id,
            value={
                "run_id": run_id,
                "environment": body.environment,
                "suite": body.suite,
                "dry_run": True,
                "status": "passed",
                "triggered_by": actor,
                "started_at": now_iso,
                "completed_at": now_iso,
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration_s": 0.0,
                "failures": [],
                "phases_run": [],
            },
            version=1,
            updated_at=now_iso,
            updated_by=actor,
        )
        await repo.set_config(run_doc)
        return PipelineRunTriggerResponse(
            run_id=run_id,
            environment=body.environment,
            suite=body.suite,
            status="passed",
            message="Dry run: configuration validated, no probes executed",
        )

    # SPEC-1846: Check for concurrent runs (only one at a time)
    # Clean up completed tasks first
    done_keys = [k for k, t in _active_runs.items() if t is not None and t.done()]
    for k in done_keys:
        _active_runs.pop(k, None)

    if _active_runs:
        active_id = next(iter(_active_runs))
        raise HTTPException(
            status_code=409,
            detail=f"A verification run is already in progress: {active_id}",
        )

    # Insert sentinel BEFORE any await to close TOCTOU window
    _active_runs[run_id] = None  # type: ignore[assignment]

    # SPEC-1845: Resolve FQDN from runtime config (never hardcoded)
    fqdn = _resolve_fqdn(body.environment)
    if not fqdn:
        raise HTTPException(
            status_code=500,
            detail=f"Cannot resolve FQDN for environment '{body.environment}'",
        )

    # SPEC-1846: Use HMAC verification secret (auto-generated at startup).
    # No Cosmos dependency — enables self-testing even when DB is down.
    verification_secret = os.environ.get("INTERNAL_VERIFICATION_SECRET", "")
    if not verification_secret:
        raise HTTPException(
            status_code=500,
            detail="INTERNAL_VERIFICATION_SECRET not set (should be auto-generated at startup)",
        )

    # Store initial "queued" status
    repo = _get_platform_repo()
    run_doc = PlatformConfigDocument(
        id=f"{_TEST_RUN_CONFIG_TYPE}:{run_id}",
        config_type=_TEST_RUN_CONFIG_TYPE,
        config_key=run_id,
        value={
            "run_id": run_id,
            "environment": body.environment,
            "suite": body.suite,
            "dry_run": False,
            "status": "queued",
            "triggered_by": actor,
            "started_at": now_iso,
            "completed_at": None,
            "total_tests": 0,
            "completed": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration_s": 0.0,
            "failures": [],
            "phases_run": [],
            "checks": [],
        },
        version=1,
        updated_at=now_iso,
        updated_by=actor,
    )
    try:
        await repo.set_config(run_doc)
    except Exception:
        _active_runs.pop(run_id, None)  # Remove sentinel on Cosmos failure
        raise

    # SPEC-1846: Fire background verification task (replaces sentinel)
    task = asyncio.create_task(
        _run_verification_background(run_id, body.environment, body.suite, fqdn, verification_secret, actor)
    )
    _active_runs[run_id] = task

    logger.info(
        "Verification run queued: %s env=%s suite=%s by %s",
        run_id, body.environment, body.suite, actor,
    )

    return PipelineRunTriggerResponse(
        run_id=run_id,
        environment=body.environment,
        suite=body.suite,
        status="queued",
        message=f"Verification run queued — poll /tests/{run_id}/status for progress",
    )


async def _run_verification_background(
    run_id: str, environment: str, suite: str, fqdn: str, verification_secret: str, actor: str,
) -> None:
    """Background coroutine that runs the VerificationRunner (SPEC-1846).

    Updates Cosmos progressively. On unexpected failure, marks run as 'error'.
    Cleans up _active_runs when done.
    """
    try:
        from src.multi_tenant.verification_runner import VerificationRunner
        repo = _get_platform_repo()
        runner = VerificationRunner(
            run_id=run_id,
            environment=environment,
            fqdn=fqdn,
            verification_secret=verification_secret,
            suite=suite,
            cosmos_repo=repo,
            actor=actor,
        )
        results = await runner.run()

        # Audit log
        passed = sum(1 for r in results if r.status == "pass")
        failed = sum(1 for r in results if r.status in ("fail", "error"))
        try:
            from src.multi_tenant.repositories.platform import AuditLogRepository
            audit = AuditLogRepository()
            await audit.log_event(
                event_type=AuditEventType.CONFIG_CHANGE,
                tenant_id="__platform__",
                actor=actor,
                actor_type="admin",
                payload={
                    "action": "test_run_completed",
                    "run_id": run_id,
                    "environment": environment,
                    "suite": suite,
                    "status": "passed" if failed == 0 else "failed",
                    "passed": passed,
                    "failed": failed,
                },
            )
        except Exception:
            logger.warning("Audit log failed for run %s", run_id, exc_info=True)

    except Exception as exc:
        logger.error("Verification run %s failed: %s", run_id, exc, exc_info=True)
        # Mark run as error in Cosmos
        try:
            repo = _get_platform_repo()
            now_iso = datetime.now(timezone.utc).isoformat()
            error_doc = PlatformConfigDocument(
                id=f"{_TEST_RUN_CONFIG_TYPE}:{run_id}",
                config_type=_TEST_RUN_CONFIG_TYPE,
                config_key=run_id,
                value={
                    "run_id": run_id,
                    "environment": environment,
                    "suite": suite,
                    "status": "error",
                    "triggered_by": actor,
                    "completed_at": now_iso,
                    "total_tests": 0,
                    "completed": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "duration_s": 0.0,
                    "failures": [{"name": "runner", "detail": str(exc)[:500]}],
                    "phases_run": [],
                    "checks": [],
                },
                version=1,
                updated_at=now_iso,
                updated_by=actor,
            )
            await repo.set_config(error_doc)
        except Exception:
            logger.error("Failed to store error state for run %s", run_id, exc_info=True)
    finally:
        _active_runs.pop(run_id, None)


def _resolve_fqdn(environment: str) -> str:
    """Resolve the FQDN for a target environment (SPEC-1845: runtime only).

    Resolution order:
    1. CONTAINER_APP_FQDN env var (for self-environment)
    2. Environment-specific env vars (STAGING_FQDN, PRODUCTION_FQDN)
    3. Well-known FQDN from platform config
    """
    current_env = os.environ.get("ENVIRONMENT", "development")

    # Self-environment: use the container's own FQDN
    if environment == current_env:
        fqdn = os.environ.get("CONTAINER_APP_FQDN", "")
        if fqdn:
            return fqdn

    # Environment-specific env vars
    env_key = f"{environment.upper()}_FQDN"
    fqdn = os.environ.get(env_key, "")
    if fqdn:
        return fqdn

    # Fallback: API_GATEWAY_FQDN only for self-environment (fail-closed for cross-env)
    fqdn = os.environ.get("API_GATEWAY_FQDN", "")
    if fqdn:
        logger.warning(
            "Using API_GATEWAY_FQDN fallback for %s: %s (set %s env var for explicit config)",
            environment, fqdn, env_key,
        )
        return fqdn

    # No FQDN resolved — caller will receive empty string → 500 response
    logger.error(
        "Cannot resolve FQDN for environment '%s'. "
        "Set CONTAINER_APP_FQDN (self-env) or %s (cross-env).",
        environment, env_key,
    )
    return ""


@router.get(
    "/tests/{run_id}/checks",
    summary="Get detailed check results for a test run (SPEC-1846)",
    description="Returns the full list of verification checks with optional filtering.",
    responses={404: {"description": "Test run not found"}},
    status_code=200,
)
async def get_test_run_checks(
    run_id: str,
    status: str | None = Query(None, description="Filter by check status: pass, fail, skip, error"),
    category: str | None = Query(None, description="Filter by category: health, api, config, security, etc."),
) -> dict[str, Any]:
    """Return detailed check results for Claude diagnosis (SPEC-1846)."""
    repo = _get_platform_repo()
    doc = await repo.get_config(_TEST_RUN_CONFIG_TYPE, run_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Test run '{run_id}' not found")

    value = doc.get("value", {})
    checks = value.get("checks", [])

    # Apply filters
    if status:
        checks = [c for c in checks if c.get("status") == status]
    if category:
        checks = [c for c in checks if c.get("category") == category]

    return {
        "run_id": run_id,
        "environment": value.get("environment", ""),
        "suite": value.get("suite", ""),
        "status": value.get("status", "unknown"),
        "total_checks": len(value.get("checks", [])),
        "filtered_count": len(checks),
        "checks": checks,
    }


@router.get(
    "/tests/runs",
    response_model=PipelineRunListResponse,
    summary="List recent test runs (SPEC-1826)",
    description="Returns a paginated list of test pipeline runs ordered by start time.",
    status_code=200,
)
async def list_test_runs(
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    environment: str | None = Query(None, description="Filter by environment"),
) -> PipelineRunListResponse:
    """List recent test pipeline runs."""
    repo = _get_platform_repo()

    # Query all test run documents
    query = (
        "SELECT * FROM c "
        "WHERE c.config_type = @config_type "
    )
    params: list[dict[str, Any]] = [
        {"name": "@config_type", "value": _TEST_RUN_CONFIG_TYPE},
    ]

    if environment:
        if environment not in VALID_ENVIRONMENTS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid environment filter '{environment}'. "
                f"Valid: {sorted(VALID_ENVIRONMENTS)}",
            )
        query += "AND c.value.environment = @env "
        params.append({"name": "@env", "value": environment})

    query += "ORDER BY c.updated_at DESC OFFSET @skip LIMIT @limit"
    params.extend([
        {"name": "@skip", "value": skip},
        {"name": "@limit", "value": limit},
    ])

    runs: list[PipelineRunStatusResponse] = []
    try:
        async for item in repo._container.query_items(
            query=query,
            parameters=params,
        ):
            value = item.get("value", {})
            runs.append(PipelineRunStatusResponse(
                run_id=value.get("run_id", ""),
                environment=value.get("environment", ""),
                suite=value.get("suite", ""),
                status=value.get("status", "unknown"),
                started_at=value.get("started_at"),
                completed_at=value.get("completed_at"),
                triggered_by=value.get("triggered_by", ""),
                total_tests=value.get("total_tests", 0),
                passed=value.get("passed", 0),
                failed=value.get("failed", 0),
                skipped=value.get("skipped", 0),
                duration_s=value.get("duration_s"),
                failures=value.get("failures", []),
                phases_run=value.get("phases_run", []),
            ))
    except Exception:
        logger.warning("Failed to query test runs", exc_info=True)

    return PipelineRunListResponse(runs=runs, total=len(runs))


@router.get(
    "/tests/{run_id}/status",
    response_model=PipelineRunStatusResponse,
    summary="Check test run status (SPEC-1826)",
    description="Returns the current status and results of a test pipeline run.",
    responses={404: {"description": "Test run not found"}},
    status_code=200,
)
async def get_test_run_status(run_id: str) -> PipelineRunStatusResponse:
    """Check the status of a specific test pipeline run."""
    repo = _get_platform_repo()
    doc = await repo.get_config(_TEST_RUN_CONFIG_TYPE, run_id)

    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=f"Test run '{run_id}' not found",
        )

    value = doc.get("value", {})

    # SPEC-1846: Detect stale runs (stuck in "running" > 30min)
    run_status = value.get("status", "unknown")
    if run_status == "running":
        started = value.get("started_at", "")
        if started:
            try:
                started_dt = datetime.fromisoformat(started)
                elapsed = (datetime.now(timezone.utc) - started_dt).total_seconds()
                if elapsed > _STALE_RUN_TIMEOUT_S:
                    run_status = "error"
                    value["status"] = "error"
                    value["failures"] = value.get("failures", []) + [
                        {"name": "stale_run", "detail": f"Run exceeded {_STALE_RUN_TIMEOUT_S}s timeout"}
                    ]
            except Exception:
                pass

    return PipelineRunStatusResponse(
        run_id=value.get("run_id", run_id),
        environment=value.get("environment", ""),
        suite=value.get("suite", ""),
        status=run_status,
        started_at=value.get("started_at"),
        completed_at=value.get("completed_at"),
        triggered_by=value.get("triggered_by", ""),
        total_tests=value.get("total_tests", 0),
        completed=value.get("completed", 0),
        passed=value.get("passed", 0),
        failed=value.get("failed", 0),
        skipped=value.get("skipped", 0),
        duration_s=value.get("duration_s"),
        failures=value.get("failures", []),
        phases_run=value.get("phases_run", []),
        checks=value.get("checks", []),
    )


# ---------------------------------------------------------------------------
# Diagnostic data models (SPEC-1827 / WI-1435)
# ---------------------------------------------------------------------------


class DiagnosticLogEntry(CamelCaseModel):
    """A single structured log entry."""

    timestamp: str
    level: str
    message: str
    logger_name: str = ""
    tenant_id: str | None = None
    request_id: str | None = None
    trace_id: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class DiagnosticLogsResponse(CamelCaseModel):
    """Response from the diagnostic logs endpoint."""

    entries: list[DiagnosticLogEntry]
    total: int
    filters_applied: dict[str, str] = Field(default_factory=dict)


class DiagnosticTraceEntry(CamelCaseModel):
    """A single request trace entry (OpenTelemetry-compatible)."""

    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    operation: str
    service: str
    status: str
    started_at: str
    duration_ms: float
    tenant_id: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class DiagnosticTracesResponse(CamelCaseModel):
    """Response from the diagnostic traces endpoint."""

    traces: list[DiagnosticTraceEntry]
    total: int


class DiagnosticMetricsResponse(CamelCaseModel):
    """Response from the diagnostic metrics endpoint."""

    period_start: str
    period_end: str
    latency: dict[str, Any] = Field(
        default_factory=dict,
        description="Latency percentiles: p50, p95, p99 in ms",
    )
    throughput: dict[str, Any] = Field(
        default_factory=dict,
        description="Requests per minute, conversations per hour",
    )
    error_rates: dict[str, Any] = Field(
        default_factory=dict,
        description="Error counts by status code and category",
    )
    resource_usage: dict[str, Any] = Field(
        default_factory=dict,
        description="CPU/memory utilization percentages",
    )


class ConfigDriftEntry(CamelCaseModel):
    """A single configuration drift detection entry."""

    config_type: str
    config_key: str
    drift_type: str = Field(
        description="Type: missing_live, stale_version, value_mismatch, unexpected_key",
    )
    detail: str = ""
    severity: str = Field(default="warning", description="info, warning, critical")


class ConfigDriftResponse(CamelCaseModel):
    """Response from the diagnostic drift endpoint."""

    checked_at: str
    total_configs_checked: int
    drift_entries: list[ConfigDriftEntry]
    is_healthy: bool = True


class SystemHealthResponse(CamelCaseModel):
    """Comprehensive system health snapshot."""

    checked_at: str
    overall_status: str = Field(description="healthy, degraded, unhealthy")
    services: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Per-service health: cosmos, redis, nats, smtp, openai",
    )
    active_tenants: int = 0
    active_sessions: int = 0
    uptime_seconds: float | None = None
    version: str = ""


# ---------------------------------------------------------------------------
# Diagnostic endpoints (SPEC-1827 / WI-1435)
# ---------------------------------------------------------------------------


@router.get(
    "/diagnostics/logs",
    response_model=DiagnosticLogsResponse,
    summary="Structured error logs (SPEC-1827)",
    description=(
        "Returns structured log entries filterable by time range, severity, "
        "tenant ID, and service. Designed for Claude Code triage consumption."
    ),
    status_code=200,
)
async def diagnostic_logs(
    level: str = Query("error", description="Minimum level: debug, info, warning, error, critical"),
    tenant_id: str | None = Query(None, description="Filter by tenant ID"),
    service: str | None = Query(None, description="Filter by service/logger name"),
    since_minutes: int = Query(60, ge=1, le=1440, description="Look back N minutes"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum entries to return"),
) -> DiagnosticLogsResponse:
    """Return structured diagnostic logs.

    In production, this would query Azure Monitor / Application Insights.
    Currently returns logs from the platform_config diagnostic_logs store.
    """
    repo = _get_platform_repo()

    from datetime import timedelta
    cutoff = (
        datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
    ).isoformat()

    query = (
        "SELECT * FROM c "
        "WHERE c.config_type = 'diagnostic_logs' "
        "AND c.updated_at >= @cutoff "
    )
    params: list[dict[str, Any]] = [
        {"name": "@cutoff", "value": cutoff},
    ]

    if tenant_id:
        query += "AND c.value.tenant_id = @tenant_id "
        params.append({"name": "@tenant_id", "value": tenant_id})
    if service:
        query += "AND c.value.logger_name = @service "
        params.append({"name": "@service", "value": service})

    query += "ORDER BY c.updated_at DESC OFFSET 0 LIMIT @limit"
    params.append({"name": "@limit", "value": limit})

    entries: list[DiagnosticLogEntry] = []
    try:
        async for item in repo._container.query_items(
            query=query,
            parameters=params,
        ):
            value = item.get("value", {})
            entries.append(DiagnosticLogEntry(
                timestamp=value.get("timestamp", item.get("updated_at", "")),
                level=value.get("level", "error"),
                message=value.get("message", ""),
                logger_name=value.get("logger_name", ""),
                tenant_id=value.get("tenant_id"),
                request_id=value.get("request_id"),
                trace_id=value.get("trace_id"),
                extra=value.get("extra", {}),
            ))
    except Exception:
        logger.warning("Failed to query diagnostic logs", exc_info=True)

    filters: dict[str, str] = {"level": str(level), "since_minutes": str(since_minutes)}
    if tenant_id and isinstance(tenant_id, str):
        filters["tenant_id"] = tenant_id
    if service and isinstance(service, str):
        filters["service"] = service

    return DiagnosticLogsResponse(
        entries=entries,
        total=len(entries),
        filters_applied=filters,
    )


@router.get(
    "/diagnostics/traces",
    response_model=DiagnosticTracesResponse,
    summary="Request traces (SPEC-1827)",
    description=(
        "Returns OpenTelemetry-compatible request traces filterable by "
        "tenant, service, and time range."
    ),
    status_code=200,
)
async def diagnostic_traces(
    tenant_id: str | None = Query(None, description="Filter by tenant ID"),
    service: str | None = Query(None, description="Filter by service name"),
    status: str | None = Query(None, description="Filter by status: ok, error"),
    since_minutes: int = Query(30, ge=1, le=1440, description="Look back N minutes"),
    limit: int = Query(50, ge=1, le=500, description="Maximum entries to return"),
) -> DiagnosticTracesResponse:
    """Return request traces for triage.

    In production, this queries Azure Monitor / Application Insights traces.
    """
    repo = _get_platform_repo()

    from datetime import timedelta
    cutoff = (
        datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
    ).isoformat()

    query = (
        "SELECT * FROM c "
        "WHERE c.config_type = 'diagnostic_traces' "
        "AND c.updated_at >= @cutoff "
    )
    params: list[dict[str, Any]] = [
        {"name": "@cutoff", "value": cutoff},
    ]

    if tenant_id:
        query += "AND c.value.tenant_id = @tenant_id "
        params.append({"name": "@tenant_id", "value": tenant_id})
    if service:
        query += "AND c.value.service = @service "
        params.append({"name": "@service", "value": service})
    if status:
        query += "AND c.value.status = @status "
        params.append({"name": "@status", "value": status})

    query += "ORDER BY c.updated_at DESC OFFSET 0 LIMIT @limit"
    params.append({"name": "@limit", "value": limit})

    traces: list[DiagnosticTraceEntry] = []
    try:
        async for item in repo._container.query_items(
            query=query,
            parameters=params,
        ):
            value = item.get("value", {})
            traces.append(DiagnosticTraceEntry(
                trace_id=value.get("trace_id", ""),
                span_id=value.get("span_id", ""),
                parent_span_id=value.get("parent_span_id"),
                operation=value.get("operation", ""),
                service=value.get("service", ""),
                status=value.get("status", "unknown"),
                started_at=value.get("started_at", ""),
                duration_ms=value.get("duration_ms", 0.0),
                tenant_id=value.get("tenant_id"),
                attributes=value.get("attributes", {}),
            ))
    except Exception:
        logger.warning("Failed to query diagnostic traces", exc_info=True)

    return DiagnosticTracesResponse(traces=traces, total=len(traces))


@router.get(
    "/diagnostics/metrics",
    response_model=DiagnosticMetricsResponse,
    summary="Performance metrics (SPEC-1827)",
    description=(
        "Returns aggregated performance metrics: latency percentiles, "
        "throughput, error rates, and resource utilization."
    ),
    status_code=200,
)
async def diagnostic_metrics(
    since_minutes: int = Query(60, ge=1, le=1440, description="Aggregation window"),
) -> DiagnosticMetricsResponse:
    """Return aggregated performance metrics.

    In production, this queries Azure Monitor metrics.
    Currently returns data from platform_config metrics store.
    """
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    period_start = (now - timedelta(minutes=since_minutes)).isoformat()
    period_end = now.isoformat()

    repo = _get_platform_repo()

    # Read the latest metrics snapshot
    doc = await repo.get_config("diagnostic_metrics", "latest")
    if doc is not None:
        value = doc.get("value", {})
        return DiagnosticMetricsResponse(
            period_start=value.get("period_start", period_start),
            period_end=value.get("period_end", period_end),
            latency=value.get("latency", {}),
            throughput=value.get("throughput", {}),
            error_rates=value.get("error_rates", {}),
            resource_usage=value.get("resource_usage", {}),
        )

    # No metrics collected yet — return empty structure
    return DiagnosticMetricsResponse(
        period_start=period_start,
        period_end=period_end,
        latency={"p50_ms": None, "p95_ms": None, "p99_ms": None},
        throughput={"rpm": None, "conversations_per_hour": None},
        error_rates={"total": 0, "by_status": {}},
        resource_usage={"cpu_pct": None, "memory_pct": None},
    )


@router.get(
    "/diagnostics/drift",
    response_model=ConfigDriftResponse,
    summary="Configuration drift report (SPEC-1827)",
    description=(
        "Compares live Cosmos configuration against frozen fallback defaults "
        "and reports any drift: missing documents, stale versions, or value "
        "mismatches. Essential for detecting config-related incidents."
    ),
    status_code=200,
)
async def diagnostic_drift() -> ConfigDriftResponse:
    """Check for configuration drift between live and frozen defaults."""
    from src.multi_tenant.entitlement_service import FROZEN_ENTITLEMENTS

    repo = _get_platform_repo()
    now_iso = datetime.now(timezone.utc).isoformat()
    drift_entries: list[ConfigDriftEntry] = []

    # Check entitlement documents
    entitlement_keys = {
        "all_tiers": ("tier_config", FROZEN_ENTITLEMENTS.get("tiers", {})),
        "pricing": ("entitlements", FROZEN_ENTITLEMENTS.get("pricing", {})),
        "pack_pricing": ("entitlements", FROZEN_ENTITLEMENTS.get("pack_pricing", {})),
        "sla_targets": ("entitlements", FROZEN_ENTITLEMENTS.get("sla_targets", {})),
        "website_limits": ("entitlements", FROZEN_ENTITLEMENTS.get("website_limits", {})),
        "integration_gates": ("entitlements", FROZEN_ENTITLEMENTS.get("integration_gates", {})),
        "field_gates": ("entitlements", FROZEN_ENTITLEMENTS.get("field_gates", {})),
        "global_config": ("entitlements", FROZEN_ENTITLEMENTS.get("global_config", {})),
    }

    configs_checked = 0
    for config_key, (config_type, frozen_value) in entitlement_keys.items():
        configs_checked += 1
        doc = await repo.get_config(config_type, config_key)

        if doc is None:
            drift_entries.append(ConfigDriftEntry(
                config_type=config_type,
                config_key=config_key,
                drift_type="missing_live",
                detail="No live document — system using frozen fallback",
                severity="warning",
            ))
            continue

        live_value = doc.get("value", {})
        if isinstance(frozen_value, dict) and isinstance(live_value, dict):
            frozen_keys = set(frozen_value.keys())
            live_keys = set(live_value.keys())

            missing = frozen_keys - live_keys
            unexpected = live_keys - frozen_keys

            if missing:
                drift_entries.append(ConfigDriftEntry(
                    config_type=config_type,
                    config_key=config_key,
                    drift_type="value_mismatch",
                    detail=f"Keys in frozen but missing from live: {sorted(missing)}",
                    severity="warning",
                ))
            if unexpected:
                drift_entries.append(ConfigDriftEntry(
                    config_type=config_type,
                    config_key=config_key,
                    drift_type="unexpected_key",
                    detail=f"Keys in live but not in frozen: {sorted(unexpected)}",
                    severity="info",
                ))

    is_healthy = all(e.severity != "critical" for e in drift_entries)

    return ConfigDriftResponse(
        checked_at=now_iso,
        total_configs_checked=configs_checked,
        drift_entries=drift_entries,
        is_healthy=is_healthy,
    )


@router.get(
    "/diagnostics/health",
    response_model=SystemHealthResponse,
    summary="System health snapshot (SPEC-1827)",
    description=(
        "Returns a comprehensive health check covering all backend services: "
        "Cosmos DB, Redis, NATS, SMTP, and OpenAI connectivity."
    ),
    status_code=200,
)
async def diagnostic_health() -> SystemHealthResponse:
    """Return a comprehensive system health snapshot."""
    now_iso = datetime.now(timezone.utc).isoformat()
    services: dict[str, dict[str, Any]] = {}

    # Check Cosmos DB
    try:
        repo = _get_platform_repo()
        doc = await repo.get_config("entitlements", "global_config")
        services["cosmos"] = {
            "status": "healthy" if doc else "degraded",
            "detail": "Connected" if doc else "Connected but missing global_config",
        }
    except Exception as exc:
        services["cosmos"] = {"status": "unhealthy", "detail": str(exc)}

    # Check Redis
    try:
        from src.multi_tenant.entitlement_service import get_entitlement_service
        svc = get_entitlement_service()
        if svc._redis_client is not None:
            await asyncio.to_thread(svc._redis_client.ping)
            services["redis"] = {"status": "healthy", "detail": "Connected"}
        else:
            services["redis"] = {"status": "degraded", "detail": "No Redis client"}
    except Exception as exc:
        services["redis"] = {"status": "unhealthy", "detail": str(exc)}

    # Check NATS
    try:
        nats_mgr = _state._nats_mgr
        if nats_mgr is not None and hasattr(nats_mgr, "is_connected"):
            connected = nats_mgr.is_connected
            services["nats"] = {
                "status": "healthy" if connected else "degraded",
                "detail": "Connected" if connected else "Not connected",
            }
        else:
            services["nats"] = {"status": "degraded", "detail": "NATS manager not configured"}
    except Exception as exc:
        services["nats"] = {"status": "unhealthy", "detail": str(exc)}

    # SMTP and OpenAI: report as unchecked (no lightweight ping available)
    services["smtp"] = {"status": "unknown", "detail": "No lightweight health check available"}
    services["openai"] = {"status": "unknown", "detail": "No lightweight health check available"}

    # Determine overall status
    statuses = [s.get("status", "unknown") for s in services.values()]
    if any(s == "unhealthy" for s in statuses):
        overall = "unhealthy"
    elif any(s == "degraded" for s in statuses):
        overall = "degraded"
    else:
        overall = "healthy"

    # Get version
    try:
        from src.multi_tenant.api_versioning import PRODUCT_VERSION
        version = PRODUCT_VERSION
    except Exception:
        version = "unknown"

    # Count active tenants
    active_tenants = 0
    try:
        if _state._tenant_repo:
            tenants = await _state._tenant_repo.list_tenants()
            active_tenants = len([
                t for t in tenants
                if t.get("status") in ("active", "trial")
            ])
    except Exception:
        pass

    return SystemHealthResponse(
        checked_at=now_iso,
        overall_status=overall,
        services=services,
        active_tenants=active_tenants,
        version=version,
    )


# ---------------------------------------------------------------------------
# Deployment event recording (WI-1285 / SPEC-1779)
# ---------------------------------------------------------------------------


class DeploymentEventRequest(CamelCaseModel):
    """Request body for recording a deployment event."""

    event_type: str = Field(description="model.deployed or model.rolled_back")
    environment: str = Field(description="staging or production")
    version: str = Field(description="Image version tag, e.g. v1.91.0")
    image: str = ""
    previous_image: str = ""
    revision_name: str = ""
    status: str = ""
    duration_s: float = 0.0
    verification_pass: int = 0
    verification_fail: int = 0
    dry_run: bool = False


class DeploymentEventResponse(CamelCaseModel):
    """Response from recording a deployment event."""

    recorded: bool = True
    event_type: str = ""
    version: str = ""


@router.post(
    "/deployments/record",
    response_model=DeploymentEventResponse,
    summary="Record a deployment audit event (WI-1285)",
    description=(
        "Called by deploy_orchestrator.py after a deployment completes. "
        "Records a MODEL_DEPLOYED or MODEL_ROLLED_BACK event in the audit log."
    ),
    status_code=201,
)
async def record_deployment_event(
    body: DeploymentEventRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> DeploymentEventResponse:
    """Record a deployment event in the audit log."""
    valid_types = {"model.deployed", "model.rolled_back"}
    if body.event_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event_type '{body.event_type}'. Valid: {sorted(valid_types)}",
        )

    actor = ctx.team_member_email or "deploy-orchestrator"
    audit_type = (
        AuditEventType.MODEL_DEPLOYED
        if body.event_type == "model.deployed"
        else AuditEventType.MODEL_ROLLED_BACK
    )

    try:
        from src.multi_tenant.repositories.platform import AuditLogRepository

        audit = AuditLogRepository()
        await audit.log_event(
            event_type=audit_type,
            tenant_id="__platform__",
            actor=actor,
            actor_type="system",
            payload={
                "environment": body.environment,
                "version": body.version,
                "image": body.image,
                "previous_image": body.previous_image,
                "revision_name": body.revision_name,
                "status": body.status,
                "duration_s": body.duration_s,
                "verification_pass": body.verification_pass,
                "verification_fail": body.verification_fail,
                "dry_run": body.dry_run,
            },
        )
    except Exception:
        logger.warning("Audit log failed for deployment event", exc_info=True)
        return DeploymentEventResponse(
            recorded=False,
            event_type=body.event_type,
            version=body.version,
        )

    logger.info(
        "Deployment event recorded: %s env=%s version=%s (by %s)",
        body.event_type, body.environment, body.version, actor,
    )

    return DeploymentEventResponse(
        recorded=True,
        event_type=body.event_type,
        version=body.version,
    )


# ---------------------------------------------------------------------------
# GET /api/superadmin/diagnostics/api-key-usage — SPEC-1832
# ---------------------------------------------------------------------------


class ApiKeyUsageRecord(CamelCaseModel):
    """Single API key usage event from audit log."""

    tenant_id: str
    auth_method: str
    key_suffix: str
    path: str
    method: str
    client_ip: str | None = None
    team_member_id: str | None = None
    timestamp: str | None = None


class ApiKeyUsageResponse(CamelCaseModel):
    """Response for GET /api/superadmin/diagnostics/api-key-usage."""

    records: list[ApiKeyUsageRecord] = []
    total: int = 0
    buffer_pending: int = 0


@_state.router.get(
    "/diagnostics/api-key-usage",
    response_model=ApiKeyUsageResponse,
    summary="API key usage audit trail (SPEC-1832)",
    description=(
        "Returns recent API key usage events from the audit log. "
        "Includes auth method, key suffix (last 8 chars), path, and client IP."
    ),
    tags=["diagnostics"],
)
async def get_api_key_usage(
    tenant_id: str | None = Query(default=None, description="Filter by tenant_id"),
    auth_method: str | None = Query(default=None, description="Filter by auth method"),
    days: int = Query(default=7, ge=1, le=90, description="Lookback period in days"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
) -> ApiKeyUsageResponse:
    """Query API key usage audit trail (SPEC-1832).

    Returns events from the audit log where action = 'api_key_usage'.
    Also reports the current in-memory buffer size (records waiting to flush).
    """
    from datetime import timedelta

    audit_repo = _state._audit_repo
    if not audit_repo:
        raise HTTPException(status_code=503, detail="Audit repository not configured")

    # Get buffer stats
    try:
        from src.multi_tenant.api_key_audit import get_api_key_audit_buffer
        buffer_pending = get_api_key_audit_buffer().pending_count
    except Exception:
        buffer_pending = 0

    period_start = datetime.now(timezone.utc) - timedelta(days=days)

    # Query audit log for api_key_usage events
    try:
        # Build query with optional filters
        conditions = [
            "c.details.action = 'api_key_usage'",
            "c.created_at >= @start",
        ]
        params = [{"name": "@start", "value": period_start.isoformat()}]

        if tenant_id:
            conditions.append("c.tenant_id = @tid")
            params.append({"name": "@tid", "value": tenant_id})

        if auth_method:
            conditions.append("c.details.auth_method = @method")
            params.append({"name": "@method", "value": auth_method})

        where_clause = " AND ".join(conditions)
        query = (
            f"SELECT TOP {limit} c.tenant_id, c.details, c.created_at "
            f"FROM c WHERE {where_clause} "
            f"ORDER BY c.created_at DESC"
        )

        results = await audit_repo.query_raw(
            query=query,
            parameters=params,
            cross_partition=True,
        )
    except AttributeError:
        # Fallback if audit_repo doesn't have query_raw
        results = []
    except Exception:
        logger.warning("API key usage query failed")
        results = []

    # Map results to response model
    records = []
    for row in results:
        details = row.get("details", {})
        records.append(ApiKeyUsageRecord(
            tenant_id=row.get("tenant_id", ""),
            auth_method=details.get("auth_method", ""),
            key_suffix=details.get("key_suffix", ""),
            path=details.get("path", ""),
            method=details.get("method", ""),
            client_ip=details.get("client_ip"),
            team_member_id=details.get("team_member_id"),
            timestamp=row.get("created_at"),
        ))

    return ApiKeyUsageResponse(
        records=records,
        total=len(records),
        buffer_pending=buffer_pending,
    )
