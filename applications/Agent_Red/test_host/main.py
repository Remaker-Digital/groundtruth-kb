"""FastAPI entry point for the Agent Red test host."""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .cosmos_writer import CosmosWriter
from .runner import TestRunner
from .suites import get_suite, list_suites

logger = logging.getLogger("test_host")

app = FastAPI(title="Agent Red Test Host", version="1.0.0", docs_url="/docs")

_active_runner: TestRunner | None = None
_active_task: asyncio.Task | None = None


class RunRequest(BaseModel):
    run_id: str | None = None
    suite: str
    environment: str
    target_url: str
    cosmos_endpoint: str | None = None
    cosmos_key: str | None = None
    cosmos_db: str | None = None
    env_overrides: dict[str, str] | None = None


class RunResponse(BaseModel):
    run_id: str
    suite: str
    status: str
    message: str


class StatusResponse(BaseModel):
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


@app.on_event("shutdown")
async def _shutdown_cancel_active_run() -> None:
    global _active_runner, _active_task
    if _active_runner and _active_task and not _active_task.done():
        await _active_runner.cancel()
        _active_task.cancel()
        _active_runner = None
        _active_task = None


@app.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "service": "test-host",
        "timestamp": datetime.now(UTC).isoformat(),
        "active_run": _active_runner.run_id if _active_runner else None,
    }


@app.get("/suites")
async def suites() -> dict:
    return {"suites": list_suites()}


@app.post("/run", status_code=202)
async def trigger_run(body: RunRequest) -> RunResponse:
    global _active_runner, _active_task
    config = get_suite(body.suite)
    if not config:
        raise HTTPException(
            status_code=400, detail=f"Unknown suite: {body.suite}. Use GET /suites to list available suites."
        )
    if _active_runner and _active_task and not _active_task.done():
        raise HTTPException(status_code=409, detail=f"A test run is already active: {_active_runner.run_id}")
    run_id = body.run_id or f"run-{uuid.uuid4().hex[:12]}"
    cosmos_endpoint = body.cosmos_endpoint or os.environ.get("COSMOS_DB_ENDPOINT", "")
    cosmos_key = body.cosmos_key or os.environ.get("COSMOS_DB_KEY", "")
    cosmos_db = body.cosmos_db or os.environ.get("COSMOS_DB_DATABASE", "agentred-staging")
    if not cosmos_endpoint or not cosmos_key:
        raise HTTPException(status_code=500, detail="Cosmos DB credentials not configured")
    writer = CosmosWriter(
        cosmos_endpoint=cosmos_endpoint,
        cosmos_key=cosmos_key,
        cosmos_db=cosmos_db,
        run_id=run_id,
        environment=body.environment,
        suite=body.suite,
    )
    runner = TestRunner(
        run_id=run_id,
        suite=body.suite,
        environment=body.environment,
        target_url=body.target_url,
        cosmos_writer=writer,
        env_overrides=body.env_overrides,
    )
    _active_runner = runner
    _active_task = asyncio.create_task(_run_background(runner))
    return RunResponse(run_id=run_id, suite=body.suite, status="queued", message=f"Test run {run_id} started")


@app.get("/status/{run_id}")
async def get_status(run_id: str) -> StatusResponse:
    if not _active_runner or _active_runner.run_id != run_id:
        raise HTTPException(status_code=404, detail=f"No active run with ID {run_id}")
    state = _active_runner.cosmos.state
    return StatusResponse(
        run_id=state.run_id,
        suite=state.suite,
        status=state.status,
        total_tests=state.total_tests,
        completed=state.completed,
        passed=state.passed,
        failed=state.failed,
        skipped=state.skipped,
        errored=state.errored,
        duration_s=state.duration_s,
        current_phase=state.current_phase,
        phases_completed=state.phases_completed,
        phases_total=state.phases_total,
    )


@app.post("/cancel/{run_id}")
async def cancel_run(run_id: str) -> dict:
    if not _active_runner or _active_runner.run_id != run_id:
        raise HTTPException(status_code=404, detail=f"No active run with ID {run_id}")
    await _active_runner.cancel()
    return {"run_id": run_id, "status": "cancelled"}


async def _run_background(runner: TestRunner) -> None:
    try:
        await runner.run()
    except asyncio.CancelledError:
        logger.warning("Test run %s cancelled", runner.run_id)
    except Exception:
        logger.exception("Background test run %s failed", runner.run_id)
        runner.cosmos.finalize(status="error")
