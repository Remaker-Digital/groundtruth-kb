# test_host/cosmos_writer.py — Progressive Cosmos result writer
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""
Writes test run results progressively to Azure Cosmos DB.
Reuses the same document schema as the in-process verification runner
(platform_config collection, config_type=test_runs) so the SPA's
existing polling logic works without modification.
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

logger = logging.getLogger("test_host.cosmos")


@dataclass
class TestResult:
    """Individual test result matching CheckResult schema."""

    name: str
    category: str
    status: str  # pass | fail | skip | error
    latency_ms: float = 0.0
    detail: str = ""


@dataclass
class RunState:
    """Mutable state of a test run, serializable to Cosmos."""

    run_id: str
    environment: str
    suite: str
    status: str = "queued"  # queued | running | passed | failed | error
    triggered_by: str = "spa-console"
    started_at: str = ""
    completed_at: str | None = None
    total_tests: int = 0
    completed: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errored: int = 0
    duration_s: float | None = None
    current_phase: str = ""
    phases_completed: list[str] = field(default_factory=list)
    phases_total: int = 0
    checks: list[dict] = field(default_factory=list)
    failures: list[dict] = field(default_factory=list)
    stdout_tail: str = ""  # Last 2000 chars of stdout for debugging


class CosmosWriter:
    """Progressive writer for test run results to Cosmos DB."""

    def __init__(
        self,
        cosmos_endpoint: str,
        cosmos_key: str,
        cosmos_db: str,
        run_id: str,
        environment: str,
        suite: str,
    ):
        self._client = CosmosClient(cosmos_endpoint, credential=cosmos_key)
        self._db = self._client.get_database_client(cosmos_db)
        self._container = self._db.get_container_client("platform_config")
        self._run_id = run_id
        self._state = RunState(
            run_id=run_id,
            environment=environment,
            suite=suite,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        self._last_upsert = 0.0

    @property
    def state(self) -> RunState:
        return self._state

    def mark_running(self, total_tests: int, phases_total: int = 1) -> None:
        """Mark the run as started."""
        self._state.status = "running"
        self._state.total_tests = total_tests
        self._state.phases_total = phases_total
        self._upsert()

    def set_phase(self, phase_name: str) -> None:
        """Set the currently executing phase."""
        self._state.current_phase = phase_name
        self._upsert()

    def complete_phase(self, phase_name: str) -> None:
        """Mark a phase as completed."""
        if phase_name not in self._state.phases_completed:
            self._state.phases_completed.append(phase_name)
        self._state.current_phase = ""
        self._upsert()

    def add_results(self, results: list[TestResult]) -> None:
        """Add a batch of test results and update counters."""
        for r in results:
            d = {
                "name": r.name,
                "category": r.category,
                "status": r.status,
                "latency_ms": r.latency_ms,
                "detail": r.detail[:500],  # Truncate long details
            }
            self._state.checks.append(d)
            self._state.completed += 1
            if r.status == "pass":
                self._state.passed += 1
            elif r.status == "fail":
                self._state.failed += 1
                self._state.failures.append(d)
            elif r.status == "skip":
                self._state.skipped += 1
            elif r.status == "error":
                self._state.errored += 1
                self._state.failures.append(d)

        # Throttle upserts to at most once per 2 seconds
        now = time.monotonic()
        if now - self._last_upsert >= 2.0:
            self._upsert()

    def update_stdout(self, tail: str) -> None:
        """Update the stdout tail for debugging."""
        self._state.stdout_tail = tail[-2000:]

    def finalize(self, status: str | None = None) -> None:
        """Mark the run as complete with final status."""
        if status:
            self._state.status = status
        elif self._state.failed > 0 or self._state.errored > 0:
            self._state.status = "failed"
        else:
            self._state.status = "passed"

        self._state.completed_at = datetime.now(timezone.utc).isoformat()
        started = datetime.fromisoformat(self._state.started_at)
        ended = datetime.fromisoformat(self._state.completed_at)
        self._state.duration_s = round((ended - started).total_seconds(), 2)
        self._upsert(force=True)

    def _build_check_window(self, max_checks: int = 500) -> list[dict]:
        """Build a check window that prioritizes failures over passes.

        Keeps ALL failed/error/skip checks and fills remaining slots with
        the most recent passing checks.  This prevents early-phase failures
        from being evicted by later heavy-suite passes.
        """
        all_checks = self._state.checks
        if len(all_checks) <= max_checks:
            return list(all_checks)

        # Partition: non-pass checks are always kept
        non_pass = [c for c in all_checks if c.get("status") != "pass"]
        passes = [c for c in all_checks if c.get("status") == "pass"]

        remaining_slots = max(0, max_checks - len(non_pass))
        # Keep most recent passes (from later phases)
        recent_passes = passes[-remaining_slots:] if remaining_slots > 0 else []

        # Merge: non-pass first (preserves discovery order), then recent passes
        return non_pass + recent_passes

    def _upsert(self, force: bool = False) -> None:
        """Upsert the run document to Cosmos."""
        now = time.monotonic()
        if not force and (now - self._last_upsert < 2.0):
            return
        self._last_upsert = now

        doc = {
            "id": f"test_runs:{self._run_id}",
            "config_type": "test_runs",
            "config_key": self._run_id,
            "value": {
                "run_id": self._state.run_id,
                "environment": self._state.environment,
                "suite": self._state.suite,
                "status": self._state.status,
                "triggered_by": self._state.triggered_by,
                "started_at": self._state.started_at,
                "completed_at": self._state.completed_at,
                "total_tests": self._state.total_tests,
                "completed": self._state.completed,
                "passed": self._state.passed,
                "failed": self._state.failed,
                "skipped": self._state.skipped,
                "errored": self._state.errored,
                "duration_s": self._state.duration_s,
                "current_phase": self._state.current_phase,
                "phases_completed": self._state.phases_completed,
                "phases_total": self._state.phases_total,
                "phases_run": self._state.phases_completed,  # Compat with existing SPA
                "failures": self._state.failures,  # All failures — always preserved
                # Persist up to 500 checks, but PRIORITIZE failures: keep ALL
                # failed/error checks and fill remaining slots with recent passes.
                # This ensures fast-suite failures aren't evicted by later
                # heavy-suite passes (the original [-500:] eviction lost early
                # failures when e2e_live added 272+ checks).
                "checks": self._build_check_window(500),
                "checks_total": len(self._state.checks),
                "checks_truncated": len(self._state.checks) > 500,
                "stdout_tail": self._state.stdout_tail,
            },
            "version": 1,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": "test-host",
        }

        try:
            self._container.upsert_item(doc)
        except Exception:
            logger.exception("Failed to upsert test run %s to Cosmos", self._run_id)
