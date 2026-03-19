# test_host/main.py — Test Host API Server
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""
Lightweight FastAPI server that accepts test run requests from the main
Agent Red API gateway, executes pytest/Locust/Playwright as subprocesses,
and writes results progressively to Cosmos DB.

Endpoints:
    POST /run          — Start a test run (returns 202 Accepted)
    GET  /status/{id}  — Get run progress (in-memory, faster than Cosmos)
    POST /cancel/{id}  — Cancel a running test
    GET  /health       — Liveness probe
    GET  /suites       — List available suites with metadata
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .cosmos_writer import CosmosWriter
from .runner import TestRunner
from .suites import list_suites, get_suite

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("test_host")

app = FastAPI(
    title="Agent Red Test Host",
    version="1.0.0",
    docs_url="/docs",
)

# ---------------------------------------------------------------------------
# In-memory state — single-worker, single-run-at-a-time
# ---------------------------------------------------------------------------
_active_runner: TestRunner | None = None
_active_task: asyncio.Task | None = None


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class RunRequest(BaseModel):
    """Request to start a test run."""
    run_id: str | None = None
    suite: str
    environment: str
    target_url: str
    cosmos_endpoint: str | None = None
    cosmos_key: str | None = None
    cosmos_db: str | None = None
    env_overrides: dict[str, str] | None = None


class RunResponse(BaseModel):
    """Response from starting a test run."""
    run_id: str
    suite: str
    status: str
    message: str


class StatusResponse(BaseModel):
    """Response from status check."""
    run_id: str
    suite: str
    status: str
    total_tests: int
    completed: int
    passed: int
    failed: int
    skipped: int
    errored: int
    duration_s: float | None
    current_phase: str
    phases_completed: list[str]
    phases_total: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Liveness probe."""
    return {
        "status": "healthy",
        "service": "test-host",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_run": _active_runner.run_id if _active_runner else None,
    }


@app.get("/suites")
async def suites():
    """List available test suites with metadata."""
    return {"suites": list_suites()}


@app.post("/run", status_code=202)
async def trigger_run(body: RunRequest) -> RunResponse:
    """Start a test run. Only one run at a time."""
    global _active_runner, _active_task

    # Validate suite
    config = get_suite(body.suite)
    if not config:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown suite: {body.suite}. Use GET /suites to list available suites.",
        )

    # Check for existing run
    if _active_runner and _active_task and not _active_task.done():
        raise HTTPException(
            status_code=409,
            detail=f"A test run is already active: {_active_runner.run_id}",
        )

    # Generate run ID
    run_id = body.run_id or f"run-{uuid.uuid4().hex[:12]}"

    # Resolve Cosmos credentials (from request body or container env)
    cosmos_endpoint = body.cosmos_endpoint or os.environ.get("COSMOS_DB_ENDPOINT", "")
    cosmos_key = body.cosmos_key or os.environ.get("COSMOS_DB_KEY", "")
    cosmos_db = body.cosmos_db or os.environ.get("COSMOS_DB_DATABASE", "agentred-staging")

    if not cosmos_endpoint or not cosmos_key:
        raise HTTPException(
            status_code=500,
            detail="Cosmos DB credentials not configured (set COSMOS_DB_ENDPOINT and COSMOS_DB_KEY)",
        )

    # Create Cosmos writer
    cosmos_writer = CosmosWriter(
        cosmos_endpoint=cosmos_endpoint,
        cosmos_key=cosmos_key,
        cosmos_db=cosmos_db,
        run_id=run_id,
        environment=body.environment,
        suite=body.suite,
    )

    # Create runner
    runner = TestRunner(
        run_id=run_id,
        suite=body.suite,
        environment=body.environment,
        target_url=body.target_url,
        cosmos_writer=cosmos_writer,
        env_overrides=body.env_overrides,
    )

    _active_runner = runner
    _active_task = asyncio.create_task(_run_background(runner))

    return RunResponse(
        run_id=run_id,
        suite=body.suite,
        status="queued",
        message=f"Test run {run_id} started for suite '{body.suite}' against {body.environment}",
    )


@app.get("/status/{run_id}")
async def get_status(run_id: str) -> StatusResponse:
    """Get the current status of a run (from in-memory state)."""
    if not _active_runner or _active_runner.run_id != run_id:
        raise HTTPException(
            status_code=404,
            detail=f"No active run with ID {run_id}. Check Cosmos for historical runs.",
        )

    s = _active_runner.cosmos.state
    return StatusResponse(
        run_id=s.run_id,
        suite=s.suite,
        status=s.status,
        total_tests=s.total_tests,
        completed=s.completed,
        passed=s.passed,
        failed=s.failed,
        skipped=s.skipped,
        errored=s.errored,
        duration_s=s.duration_s,
        current_phase=s.current_phase,
        phases_completed=s.phases_completed,
        phases_total=s.phases_total,
    )


@app.post("/cancel/{run_id}")
async def cancel_run(run_id: str):
    """Cancel a running test."""
    if not _active_runner or _active_runner.run_id != run_id:
        raise HTTPException(status_code=404, detail=f"No active run with ID {run_id}")

    await _active_runner.cancel()
    return {"run_id": run_id, "status": "cancelled"}


# ---------------------------------------------------------------------------
# Background task
# ---------------------------------------------------------------------------

async def _run_background(runner: TestRunner) -> None:
    """Execute a test run in the background."""
    try:
        result = await runner.run()
        logger.info("Test run %s completed: %s", runner.run_id, result.get("status", "unknown"))
    except Exception:
        logger.exception("Background test run %s failed", runner.run_id)
