"""Isolated DBOS foundation probe for Dispatcher Next.

This module is intentionally not wired into the production CLI or dispatcher.
It exercises durable workflow recovery and idempotent local domain mutations
against pytest-owned SQLite databases.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import sqlite3
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from contextlib import suppress
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

from dbos import DBOS, DBOSConfig, SetWorkflowID

DBOS_DISTRIBUTION: Final[str] = "dbos"
A2A_DISTRIBUTION: Final[str] = "a2a-sdk"
EXPECTED_DBOS_VERSION: Final[str] = "2.27.0"
EXPECTED_A2A_VERSION: Final[str] = "1.1.1"
ADOPT_DBOS_A2A: Final[str] = "adopt_dbos_a2a"
REJECT_AND_EVALUATE_HATCHET: Final[str] = "reject_and_evaluate_hatchet"
REQUIRED_PREDICATES: Final[tuple[str, ...]] = (
    "python_3_14",
    "durable_recovery",
    "a2a_task_artifact_round_trip",
    "atomic_intersecting_caps",
    "semantic_idempotency",
    "live_system_nonimpairment",
)
TRANSIENT_RETRY_INTERVAL_SECONDS: Final[float] = 0.01
TRANSIENT_RETRY_MAX_ATTEMPTS: Final[int] = 3


class TransientProbeError(RuntimeError):
    """Purpose-built retryable failure for the isolated DBOS probe."""


def _evidence_supports_adoption(evidence: Mapping[str, Any]) -> bool:
    records = evidence.get("verification_manifest")
    if not isinstance(records, list) or len(records) != len(REQUIRED_PREDICATES):
        return False

    seen: set[str] = set()
    for record in records:
        if not isinstance(record, Mapping):
            return False
        predicate = record.get("predicate")
        if predicate not in REQUIRED_PREDICATES or predicate in seen:
            return False
        exit_code = record.get("exit_code")
        if type(exit_code) is not int or exit_code != 0:
            return False
        if record.get("satisfied") is not True:
            return False
        cleanup = record.get("cleanup")
        if not isinstance(cleanup, Mapping) or cleanup.get("status") != "complete":
            return False
        seen.add(predicate)
    return seen == set(REQUIRED_PREDICATES)


@dataclass(frozen=True)
class AdoptionManifest:
    """Binary adoption result plus evidence for every mandatory predicate."""

    schema_version: int
    outcome: str
    predicates: dict[str, bool]
    evidence: dict[str, Any]

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("adoption manifest schema_version must be 1")
        if self.outcome not in {ADOPT_DBOS_A2A, REJECT_AND_EVALUATE_HATCHET}:
            raise ValueError(f"unknown adoption manifest outcome: {self.outcome!r}")
        if not isinstance(self.predicates, dict) or set(self.predicates) != set(REQUIRED_PREDICATES):
            raise ValueError("adoption manifest predicates must contain exactly the required keys")
        if any(type(value) is not bool for value in self.predicates.values()):
            raise ValueError("adoption manifest predicate values must be boolean")
        if not isinstance(self.evidence, dict):
            raise ValueError("adoption manifest evidence must be a mapping")

        predicates = {name: self.predicates[name] for name in REQUIRED_PREDICATES}
        evidence = dict(self.evidence)
        adoption_proven = all(predicates.values()) and _evidence_supports_adoption(evidence)
        expected_outcome = ADOPT_DBOS_A2A if adoption_proven else REJECT_AND_EVALUATE_HATCHET
        if self.outcome != expected_outcome:
            raise ValueError(
                f"adoption manifest outcome {self.outcome!r} is inconsistent with its "
                "predicates and verification evidence"
            )
        object.__setattr__(self, "predicates", predicates)
        object.__setattr__(self, "evidence", evidence)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationRecord:
    """Machine-readable evidence for one mandatory adoption predicate."""

    predicate: str
    command: str
    exit_code: int
    observed_value: Any
    satisfied: bool
    cleanup: dict[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.predicate, str) or self.predicate not in REQUIRED_PREDICATES:
            raise ValueError(f"unknown verification predicate: {self.predicate!r}")
        if not isinstance(self.command, str) or not self.command.strip():
            raise ValueError("verification command must not be empty")
        if isinstance(self.exit_code, bool) or not isinstance(self.exit_code, int):
            raise TypeError("verification exit_code must be an integer")
        if not isinstance(self.satisfied, bool):
            raise TypeError("verification satisfied flag must be boolean")
        if not isinstance(self.cleanup, dict) or not self.cleanup:
            raise ValueError("verification cleanup evidence must be a non-empty mapping")
        object.__setattr__(self, "cleanup", dict(self.cleanup))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def dependency_versions() -> dict[str, str]:
    """Return the installed versions of the two spike dependencies."""

    return {
        DBOS_DISTRIBUTION: importlib.metadata.version(DBOS_DISTRIBUTION),
        A2A_DISTRIBUTION: importlib.metadata.version(A2A_DISTRIBUTION),
    }


def evaluate_adoption(
    predicates: Mapping[str, bool],
    *,
    evidence: Mapping[str, Any] | None = None,
) -> AdoptionManifest:
    """Produce the only two valid spike outcomes.

    Missing predicates fail closed rather than being inferred from adjacent
    evidence.
    """

    exact_predicate_schema = set(predicates) == set(REQUIRED_PREDICATES) and all(
        type(value) is bool for value in predicates.values()
    )
    normalized = {name: predicates.get(name) is True for name in REQUIRED_PREDICATES}
    normalized_evidence = dict(evidence or {})
    adoption_proven = (
        exact_predicate_schema and all(normalized.values()) and _evidence_supports_adoption(normalized_evidence)
    )
    outcome = ADOPT_DBOS_A2A if adoption_proven else REJECT_AND_EVALUATE_HATCHET
    return AdoptionManifest(
        schema_version=1,
        outcome=outcome,
        predicates=normalized,
        evidence=normalized_evidence,
    )


def evaluate_verification_records(
    records: Sequence[VerificationRecord],
) -> AdoptionManifest:
    """Evaluate complete command evidence and fail closed on missing records."""

    by_predicate: dict[str, VerificationRecord] = {}
    for record in records:
        if not isinstance(record, VerificationRecord):
            raise TypeError("records must contain VerificationRecord instances")
        if record.predicate in by_predicate:
            raise ValueError(f"duplicate verification predicate: {record.predicate!r}")
        by_predicate[record.predicate] = record

    predicates: dict[str, bool] = {}
    manifest_records: list[dict[str, Any]] = []
    for predicate in REQUIRED_PREDICATES:
        record = by_predicate.get(predicate)
        if record is None:
            predicates[predicate] = False
            manifest_records.append(
                {
                    "predicate": predicate,
                    "command": "",
                    "exit_code": 1,
                    "observed_value": "missing",
                    "satisfied": False,
                    "cleanup": {"status": "missing"},
                }
            )
            continue
        cleanup_complete = record.cleanup.get("status") == "complete"
        predicates[predicate] = record.exit_code == 0 and record.satisfied and cleanup_complete
        manifest_records.append(record.to_dict())

    return evaluate_adoption(
        predicates,
        evidence={"verification_manifest": manifest_records},
    )


def _operation_connection(path: str | Path) -> sqlite3.Connection:
    database = Path(path).resolve()
    database.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database, timeout=30, isolation_level=None)
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def _initialize_operation_database(path: str | Path) -> None:
    conn = _operation_connection(path)
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = FULL")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS semantic_operations (
                operation_id TEXT PRIMARY KEY,
                result_json TEXT NOT NULL,
                completed_at REAL NOT NULL
            )
            """
        )
    finally:
        conn.close()


def semantic_operation_count(path: str | Path) -> int:
    """Return the number of durable semantic mutations in the probe DB."""

    _initialize_operation_database(path)
    conn = _operation_connection(path)
    try:
        row = conn.execute("SELECT COUNT(*) FROM semantic_operations").fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


def _record_semantic_operation(
    path: str | Path,
    operation_id: str,
    result: Mapping[str, Any],
) -> dict[str, Any]:
    encoded = json.dumps(dict(result), sort_keys=True, separators=(",", ":"))
    conn = _operation_connection(path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            """
            INSERT OR IGNORE INTO semantic_operations
                (operation_id, result_json, completed_at)
            VALUES (?, ?, ?)
            """,
            (operation_id, encoded, time.time()),
        )
        row = conn.execute(
            "SELECT result_json FROM semantic_operations WHERE operation_id = ?",
            (operation_id,),
        ).fetchone()
        conn.commit()
        if row is None:
            raise RuntimeError(f"semantic operation {operation_id!r} was not persisted")
        decoded = json.loads(str(row[0]))
        if not isinstance(decoded, dict):
            raise RuntimeError(f"semantic operation {operation_id!r} has a non-object result")
        return decoded
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _write_crash_marker(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(descriptor, b"crash-once\n")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _read_attempt_count(counter_path: str | Path) -> int:
    path = Path(counter_path).resolve()
    if not path.exists():
        return 0
    raw_value = path.read_text(encoding="ascii").strip()
    try:
        attempt_count = int(raw_value)
    except ValueError as error:
        raise ValueError(f"invalid transient retry counter value: {raw_value!r}") from error
    if attempt_count < 0:
        raise ValueError("transient retry counter must not be negative")
    return attempt_count


def _increment_attempt_count(counter_path: str | Path) -> int:
    path = Path(counter_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    attempt_count = _read_attempt_count(path) + 1
    path.write_text(f"{attempt_count}\n", encoding="ascii")
    return attempt_count


def _should_retry_transient_probe(error: BaseException) -> bool:
    return isinstance(error, TransientProbeError)


@DBOS.step(
    name="dispatcher-next-transient-retry-probe",
    retries_allowed=True,
    interval_seconds=TRANSIENT_RETRY_INTERVAL_SECONDS,
    max_attempts=TRANSIENT_RETRY_MAX_ATTEMPTS,
    backoff_rate=1.0,
    should_retry=_should_retry_transient_probe,
)
def _transient_retry_probe_step(
    counter_path: str,
    transient_failures: int,
) -> dict[str, Any]:
    attempt_count = _increment_attempt_count(counter_path)
    if attempt_count <= transient_failures:
        raise TransientProbeError(f"purpose-built transient failure on attempt {attempt_count}")
    return {
        "attempt_count": attempt_count,
        "transient_failures": transient_failures,
    }


@DBOS.step(name="dispatcher-next-run-stub-subprocess")
def _run_stub_subprocess(
    operation_database: str,
    operation_id: str,
    payload: dict[str, Any],
    delay_seconds: float,
    crash_once_marker: str | None,
    start_barrier_directory: str | None = None,
    start_barrier_count: int = 0,
) -> dict[str, Any]:
    stub = """
import json
import os
from pathlib import Path
import sys
import time

payload = json.loads(sys.argv[1])
delay_seconds = float(sys.argv[2])
barrier_directory = sys.argv[3]
barrier_count = int(sys.argv[4])
if barrier_directory:
    barrier = Path(barrier_directory)
    (barrier / f"{os.getpid()}.ready").touch()
    deadline = time.monotonic() + 20.0
    while len(tuple(barrier.glob("*.ready"))) < barrier_count:
        if time.monotonic() >= deadline:
            raise TimeoutError("subprocess start barrier timed out")
        time.sleep(0.005)

started_at = time.time()
time.sleep(delay_seconds)
finished_at = time.time()
print(
    json.dumps(
        {
            "echo": payload,
            "finished_at": finished_at,
            "started_at": started_at,
            "worker_pid": os.getpid(),
        },
        sort_keys=True,
    )
)
"""
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            stub,
            json.dumps(payload, sort_keys=True),
            str(delay_seconds),
            start_barrier_directory or "",
            str(start_barrier_count),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    result = json.loads(completed.stdout)
    if not isinstance(result, dict):
        raise RuntimeError("stub subprocess returned a non-object result")
    persisted_result = _record_semantic_operation(operation_database, operation_id, result)

    # Exercise the ambiguous recovery window: the domain mutation is durable,
    # but this DBOS step has not returned and therefore has no recorded result.
    if crash_once_marker:
        marker = Path(crash_once_marker)
        if not marker.exists():
            _write_crash_marker(marker)
            os._exit(91)

    return persisted_result


@DBOS.workflow(name="dispatcher-next-transient-retry-workflow")
def transient_retry_workflow(
    counter_path: str,
    transient_failures: int,
) -> dict[str, Any]:
    """Exercise the explicitly bounded retry policy in an isolated workflow."""

    return _transient_retry_probe_step(counter_path, transient_failures)


@DBOS.workflow(name="dispatcher-next-durable-stub-workflow")
def durable_stub_workflow(
    operation_database: str,
    operation_id: str,
    payload: dict[str, Any],
    delay_seconds: float = 0.0,
    crash_once_marker: str | None = None,
    start_barrier_directory: str | None = None,
    start_barrier_count: int = 0,
    before_step_delay_seconds: float = 0.0,
) -> dict[str, Any]:
    """Run one durable workflow around an opaque local stub subprocess."""

    if before_step_delay_seconds:
        DBOS.sleep(before_step_delay_seconds)
    return _run_stub_subprocess(
        operation_database,
        operation_id,
        payload,
        delay_seconds,
        crash_once_marker,
        start_barrier_directory,
        start_barrier_count,
    )


def _sqlite_url(path: str | Path) -> str:
    return f"sqlite:///{Path(path).resolve().as_posix()}"


def _ensure_database_parent(path: str | Path) -> None:
    Path(path).resolve().parent.mkdir(parents=True, exist_ok=True)


def _dbos_config(system_database: str | Path, *, executor_id: str) -> DBOSConfig:
    return {
        "name": "gtkb-dispatcher-next",
        "system_database_url": _sqlite_url(system_database),
        "application_version": "wi5617-foundation-v1",
        "executor_id": executor_id,
        "run_admin_server": False,
        "enable_otlp": False,
        "console_log_level": "WARNING",
        "max_executor_threads": 32,
        "notification_listener_polling_interval_sec": 0.05,
    }


def run_workflow_batch(
    *,
    system_database: str | Path,
    operation_database: str | Path,
    workflow_prefix: str,
    count: int,
    delay_seconds: float = 0.0,
    executor_id: str = "batch",
) -> dict[str, Any]:
    """Execute ``count`` durable workflows and return compact evidence."""

    if count < 1:
        raise ValueError("count must be positive")
    _ensure_database_parent(system_database)
    _ensure_database_parent(operation_database)
    _initialize_operation_database(operation_database)
    start_barrier = Path(operation_database).resolve().parent / ".dispatcher-next-start-barrier"
    start_barrier.mkdir(parents=True, exist_ok=True)
    for ready_path in start_barrier.glob("*.ready"):
        ready_path.unlink()
    dbos = DBOS(config=_dbos_config(system_database, executor_id=executor_id))
    dbos.launch()
    try:
        handles = []
        for index in range(count):
            workflow_id = f"{workflow_prefix}-{index:03d}"
            with SetWorkflowID(workflow_id):
                handle = DBOS.start_workflow(
                    durable_stub_workflow,
                    str(Path(operation_database).resolve()),
                    workflow_id,
                    {"index": index, "workflow_id": workflow_id},
                    delay_seconds,
                    None,
                    str(start_barrier),
                    count,
                )
            handles.append((workflow_id, handle))

        results = {workflow_id: handle.get_result(polling_interval_sec=0.05) for workflow_id, handle in handles}
        return {
            "schema_version": 1,
            "workflow_count": count,
            "semantic_operation_count": semantic_operation_count(operation_database),
            "workflow_ids": sorted(results),
            "results": results,
        }
    finally:
        dbos.destroy()
        for ready_path in start_barrier.glob("*.ready"):
            ready_path.unlink()
        with suppress(OSError):
            start_barrier.rmdir()


def run_transient_retry_probe(
    *,
    system_database: str | Path,
    counter_path: str | Path,
    workflow_id: str,
    transient_failures: int,
    executor_id: str = "transient-retry-probe",
) -> dict[str, Any]:
    """Run the bounded transient probe and return success or exhaustion evidence."""

    if not workflow_id.strip():
        raise ValueError("workflow_id must not be empty")
    if transient_failures < 0:
        raise ValueError("transient_failures must not be negative")

    system_database_path = Path(system_database).resolve()
    counter = Path(counter_path).resolve()
    _ensure_database_parent(system_database_path)
    _ensure_database_parent(counter)
    if counter.exists():
        raise FileExistsError(f"transient retry counter already exists: {counter}")

    dbos = DBOS(config=_dbos_config(system_database_path, executor_id=executor_id))
    dbos.launch()
    try:
        try:
            with SetWorkflowID(workflow_id):
                handle = DBOS.start_workflow(
                    transient_retry_workflow,
                    str(counter),
                    transient_failures,
                )
            step_result = handle.get_result(polling_interval_sec=0.01)
        except Exception as error:
            return {
                "attempt_count": _read_attempt_count(counter),
                "error": str(error),
                "error_type": type(error).__name__,
                "max_attempts": TRANSIENT_RETRY_MAX_ATTEMPTS,
                "retry_interval_seconds": TRANSIENT_RETRY_INTERVAL_SECONDS,
                "schema_version": 1,
                "succeeded": False,
                "transient_failures": transient_failures,
                "workflow_id": workflow_id,
            }

        return {
            "attempt_count": int(step_result["attempt_count"]),
            "max_attempts": TRANSIENT_RETRY_MAX_ATTEMPTS,
            "retry_interval_seconds": TRANSIENT_RETRY_INTERVAL_SECONDS,
            "schema_version": 1,
            "succeeded": True,
            "transient_failures": transient_failures,
            "workflow_id": workflow_id,
        }
    finally:
        dbos.destroy()


def _workflow_ids(workflow_prefix: str, count: int) -> list[str]:
    if not workflow_prefix.strip():
        raise ValueError("workflow_prefix must not be empty")
    if count < 1:
        raise ValueError("count must be positive")
    return [f"{workflow_prefix}-{index:03d}" for index in range(count)]


def _start_crash_once_workflows(
    *,
    system_database: str | Path,
    operation_database: str | Path,
    workflows: Sequence[tuple[str, dict[str, Any]]],
    crash_marker: str | Path,
    pending_delay_seconds: float,
    executor_id: str,
) -> None:
    if not workflows:
        raise ValueError("at least one workflow is required")
    if pending_delay_seconds < 0:
        raise ValueError("pending_delay_seconds must not be negative")

    _ensure_database_parent(system_database)
    _ensure_database_parent(operation_database)
    _ensure_database_parent(crash_marker)
    _initialize_operation_database(operation_database)
    dbos = DBOS(config=_dbos_config(system_database, executor_id=executor_id))
    dbos.launch()

    crash_index = len(workflows) - 1
    crash_handle = None
    for index, (workflow_id, payload) in enumerate(workflows):
        is_crash_workflow = index == crash_index
        with SetWorkflowID(workflow_id):
            handle = DBOS.start_workflow(
                durable_stub_workflow,
                str(Path(operation_database).resolve()),
                workflow_id,
                payload,
                0.0,
                str(Path(crash_marker).resolve()) if is_crash_workflow else None,
                None,
                0,
                0.0 if is_crash_workflow else pending_delay_seconds,
            )
        if is_crash_workflow:
            crash_handle = handle

    if crash_handle is None:  # pragma: no cover - guarded by workflows validation
        dbos.destroy()
        raise RuntimeError("no crash workflow was started")

    # The designated workflow exits after its semantic operation commits. The
    # other workflows have already been started and remain recoverable.
    crash_handle.get_result(polling_interval_sec=0.05)
    dbos.destroy()
    raise RuntimeError("crash-once workflow completed without terminating its executor")


def start_crash_once_workflow(
    *,
    system_database: str | Path,
    operation_database: str | Path,
    workflow_id: str,
    crash_marker: str | Path,
    executor_id: str = "durable-probe-executor",
) -> None:
    """Start one workflow that exits after its domain mutation commits."""

    _start_crash_once_workflows(
        system_database=system_database,
        operation_database=operation_database,
        workflows=[
            (
                workflow_id,
                {"mode": "crash-recovery", "workflow_id": workflow_id},
            )
        ],
        crash_marker=crash_marker,
        pending_delay_seconds=0.0,
        executor_id=executor_id,
    )


def start_crash_once_workflow_batch(
    *,
    system_database: str | Path,
    operation_database: str | Path,
    workflow_prefix: str,
    count: int,
    crash_marker: str | Path,
    pending_delay_seconds: float = 5.0,
    executor_id: str = "durable-probe-executor",
) -> None:
    """Start multiple workflows, then exit after the last domain commit."""

    workflow_ids = _workflow_ids(workflow_prefix, count)
    _start_crash_once_workflows(
        system_database=system_database,
        operation_database=operation_database,
        workflows=[
            (
                workflow_id,
                {
                    "index": index,
                    "mode": "crash-recovery-batch",
                    "workflow_id": workflow_id,
                },
            )
            for index, workflow_id in enumerate(workflow_ids)
        ],
        crash_marker=crash_marker,
        pending_delay_seconds=pending_delay_seconds,
        executor_id=executor_id,
    )


def recover_workflow(
    *,
    system_database: str | Path,
    operation_database: str | Path,
    workflow_id: str,
    executor_id: str = "durable-probe-executor",
) -> dict[str, Any]:
    """Launch a new executor and retrieve the recovered workflow result."""

    _ensure_database_parent(system_database)
    _ensure_database_parent(operation_database)
    _initialize_operation_database(operation_database)
    dbos = DBOS(config=_dbos_config(system_database, executor_id=executor_id))
    dbos.launch()
    try:
        handle = DBOS.retrieve_workflow(workflow_id)
        result = handle.get_result(polling_interval_sec=0.05)
        return {
            "schema_version": 1,
            "workflow_id": workflow_id,
            "result": result,
            "semantic_operation_count": semantic_operation_count(operation_database),
        }
    finally:
        dbos.destroy()


def recover_workflow_batch(
    *,
    system_database: str | Path,
    operation_database: str | Path,
    workflow_prefix: str,
    count: int,
    executor_id: str = "durable-probe-executor",
) -> dict[str, Any]:
    """Launch a new executor and retrieve a batch of pending workflows."""

    workflow_ids = _workflow_ids(workflow_prefix, count)
    _ensure_database_parent(system_database)
    _ensure_database_parent(operation_database)
    _initialize_operation_database(operation_database)
    dbos = DBOS(config=_dbos_config(system_database, executor_id=executor_id))
    dbos.launch()
    try:
        handles = {workflow_id: DBOS.retrieve_workflow(workflow_id) for workflow_id in workflow_ids}
        results = {
            workflow_id: handles[workflow_id].get_result(polling_interval_sec=0.05) for workflow_id in workflow_ids
        }
        return {
            "schema_version": 1,
            "workflow_count": count,
            "semantic_operation_count": semantic_operation_count(operation_database),
            "workflow_ids": workflow_ids,
            "results": results,
        }
    finally:
        dbos.destroy()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    batch = subparsers.add_parser("batch")
    batch.add_argument("--system-database", required=True)
    batch.add_argument("--operation-database", required=True)
    batch.add_argument("--workflow-prefix", required=True)
    batch.add_argument("--count", type=int, required=True)
    batch.add_argument("--delay-seconds", type=float, default=0.0)
    batch.add_argument("--executor-id", default="batch")

    crash = subparsers.add_parser("crash")
    crash.add_argument("--system-database", required=True)
    crash.add_argument("--operation-database", required=True)
    crash.add_argument("--workflow-id", required=True)
    crash.add_argument("--crash-marker", required=True)
    crash.add_argument("--executor-id", default="durable-probe-executor")

    crash_batch = subparsers.add_parser("crash-batch")
    crash_batch.add_argument("--system-database", required=True)
    crash_batch.add_argument("--operation-database", required=True)
    crash_batch.add_argument("--workflow-prefix", required=True)
    crash_batch.add_argument("--count", type=int, required=True)
    crash_batch.add_argument("--crash-marker", required=True)
    crash_batch.add_argument("--pending-delay-seconds", type=float, default=5.0)
    crash_batch.add_argument("--executor-id", default="durable-probe-executor")

    recover = subparsers.add_parser("recover")
    recover.add_argument("--system-database", required=True)
    recover.add_argument("--operation-database", required=True)
    recover.add_argument("--workflow-id", required=True)
    recover.add_argument("--executor-id", default="durable-probe-executor")

    recover_batch = subparsers.add_parser("recover-batch")
    recover_batch.add_argument("--system-database", required=True)
    recover_batch.add_argument("--operation-database", required=True)
    recover_batch.add_argument("--workflow-prefix", required=True)
    recover_batch.add_argument("--count", type=int, required=True)
    recover_batch.add_argument("--executor-id", default="durable-probe-executor")

    retry_probe = subparsers.add_parser("retry-probe")
    retry_probe.add_argument("--system-database", required=True)
    retry_probe.add_argument("--counter-path", required=True)
    retry_probe.add_argument("--workflow-id", required=True)
    retry_probe.add_argument("--transient-failures", type=int, required=True)
    retry_probe.add_argument("--executor-id", default="transient-retry-probe")

    versions = subparsers.add_parser("versions")
    versions.set_defaults(command="versions")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "batch":
        result = run_workflow_batch(
            system_database=args.system_database,
            operation_database=args.operation_database,
            workflow_prefix=args.workflow_prefix,
            count=args.count,
            delay_seconds=args.delay_seconds,
            executor_id=args.executor_id,
        )
    elif args.command == "crash":
        start_crash_once_workflow(
            system_database=args.system_database,
            operation_database=args.operation_database,
            workflow_id=args.workflow_id,
            crash_marker=args.crash_marker,
            executor_id=args.executor_id,
        )
        return 1
    elif args.command == "crash-batch":
        start_crash_once_workflow_batch(
            system_database=args.system_database,
            operation_database=args.operation_database,
            workflow_prefix=args.workflow_prefix,
            count=args.count,
            crash_marker=args.crash_marker,
            pending_delay_seconds=args.pending_delay_seconds,
            executor_id=args.executor_id,
        )
        return 1
    elif args.command == "recover":
        result = recover_workflow(
            system_database=args.system_database,
            operation_database=args.operation_database,
            workflow_id=args.workflow_id,
            executor_id=args.executor_id,
        )
    elif args.command == "recover-batch":
        result = recover_workflow_batch(
            system_database=args.system_database,
            operation_database=args.operation_database,
            workflow_prefix=args.workflow_prefix,
            count=args.count,
            executor_id=args.executor_id,
        )
    elif args.command == "retry-probe":
        result = run_transient_retry_probe(
            system_database=args.system_database,
            counter_path=args.counter_path,
            workflow_id=args.workflow_id,
            transient_failures=args.transient_failures,
            executor_id=args.executor_id,
        )
        print(json.dumps(result, sort_keys=True))
        return 0 if result["succeeded"] else 2
    else:
        result = dependency_versions()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
