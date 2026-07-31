"""Progressive Cosmos result writer for the Agent Red test host."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime

try:
    from azure.cosmos import CosmosClient
except ImportError:  # pragma: no cover - tests patch this symbol.

    class CosmosClient:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs):
            raise RuntimeError("azure-cosmos is required for live test-host writes")


logger = logging.getLogger("test_host.cosmos")


@dataclass
class TestResult:
    name: str
    category: str
    status: str
    latency_ms: float = 0.0
    detail: str = ""


@dataclass
class RunState:
    run_id: str
    environment: str
    suite: str
    status: str = "queued"
    triggered_by: str = "spa-console"
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
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
    stdout_tail: str = ""


class CosmosWriter:
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
        self._state = RunState(run_id=run_id, environment=environment, suite=suite)
        self._last_upsert = 0.0

    @property
    def state(self) -> RunState:
        return self._state

    def mark_running(self, total_tests: int, phases_total: int = 1) -> None:
        self._state.status = "running"
        self._state.total_tests = total_tests
        self._state.phases_total = phases_total
        self._upsert()

    def set_phase(self, phase_name: str) -> None:
        self._state.current_phase = phase_name
        self._upsert()

    def complete_phase(self, phase_name: str) -> None:
        if phase_name not in self._state.phases_completed:
            self._state.phases_completed.append(phase_name)
        self._state.current_phase = ""
        self._upsert()

    def add_results(self, results: list[TestResult]) -> None:
        for result in results:
            stored = {
                "name": result.name,
                "category": result.category,
                "status": result.status,
                "latency_ms": result.latency_ms,
                "detail": result.detail[:500],
            }
            self._state.checks.append(stored)
            self._state.completed += 1
            if result.status == "pass":
                self._state.passed += 1
            elif result.status == "fail":
                self._state.failed += 1
                self._state.failures.append(stored)
            elif result.status == "skip":
                self._state.skipped += 1
            elif result.status == "error":
                self._state.errored += 1
                self._state.failures.append(stored)

        now = time.monotonic()
        if now - self._last_upsert >= 2.0:
            self._upsert()

    def update_stdout(self, tail: str) -> None:
        self._state.stdout_tail = tail[-2000:]

    def finalize(self, status: str | None = None) -> None:
        if status:
            self._state.status = status
        elif self._state.failed or self._state.errored:
            self._state.status = "failed"
        else:
            self._state.status = "passed"
        self._state.completed_at = datetime.now(UTC).isoformat()
        self._state.duration_s = round(
            (
                datetime.fromisoformat(self._state.completed_at) - datetime.fromisoformat(self._state.started_at)
            ).total_seconds(),
            2,
        )
        self._upsert(force=True)

    def _check_window(self, max_checks: int = 500) -> list[dict]:
        if len(self._state.checks) <= max_checks:
            return list(self._state.checks)
        non_pass = [check for check in self._state.checks if check.get("status") != "pass"]
        passes = [check for check in self._state.checks if check.get("status") == "pass"]
        return non_pass + passes[-max(0, max_checks - len(non_pass)) :]

    def _upsert(self, force: bool = False) -> None:
        now = time.monotonic()
        if not force and now - self._last_upsert < 2.0:
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
                "phases_run": self._state.phases_completed,
                "failures": self._state.failures[:100],
                "checks": self._check_window(),
                "stdout_tail": self._state.stdout_tail,
            },
            "version": 1,
            "updated_at": datetime.now(UTC).isoformat(),
            "updated_by": "test-host",
        }
        try:
            self._container.upsert_item(doc)
        except Exception:
            logger.exception("Failed to upsert test run %s to Cosmos", self._run_id)
