from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Barrier, Event, Lock
from typing import Any

import psutil
import pytest
from groundtruth_kb.dispatcher_next.capacity import (
    CapacityLedger,
    CapacityPolicy,
    CapacityRequest,
    DuplicateLeaseError,
    InvalidCapacityPolicy,
)
from groundtruth_kb.dispatcher_next.foundation import (
    ADOPT_DBOS_A2A,
    EXPECTED_A2A_VERSION,
    EXPECTED_DBOS_VERSION,
    REJECT_AND_EVALUATE_HATCHET,
    REQUIRED_PREDICATES,
    AdoptionManifest,
    VerificationRecord,
    dependency_versions,
    evaluate_adoption,
    evaluate_verification_records,
    semantic_operation_count,
)
from groundtruth_kb.dispatcher_next.protocol import (
    A2AProtocolError,
    A2AProtocolFacade,
    InvalidTaskTransitionError,
    round_trip_task,
    run_lifecycle,
    task_to_dict,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SOURCE = REPO_ROOT / "groundtruth-kb" / "src"
PACKAGE_DIR = PACKAGE_SOURCE / "groundtruth_kb" / "dispatcher_next"
FOUNDATION_MODULE = PACKAGE_SOURCE / "groundtruth_kb" / "dispatcher_next" / "foundation.py"
STATIC_LIVE_PATHS = (
    REPO_ROOT / "config" / "dispatcher" / "rules.toml",
    REPO_ROOT / "harness-state" / "harness-registry.json",
    REPO_ROOT / ".api-harness" / "routing.toml",
)
LIVE_STATE_PATHS = (
    *STATIC_LIVE_PATHS,
    REPO_ROOT / "groundtruth.db",
    REPO_ROOT / "groundtruth.db-wal",
    REPO_ROOT / "groundtruth.db-shm",
    REPO_ROOT / ".gtkb-state" / "bridge-poller" / "dispatch-state.json",
)
LIVE_STATE_DIRECTORIES = (
    REPO_ROOT / ".gtkb-state" / "bridge-poller" / "leases",
    REPO_ROOT / ".gtkb-state" / "dispatcher-daemon" / "leases",
)
FORBIDDEN_LIVE_REFERENCES = (
    ".gtkb-state",
    ".api-harness",
    "bridge-poller",
    "config/dispatcher",
    "groundtruth.db",
    "harness-state",
)
REAL_HARNESS_COMMANDS = (
    "claude_harness.py",
    "codex_headless_dispatch.py",
    "cursor_harness.py",
    "ollama_harness.py",
    "openrouter_harness.py",
)
_VERIFICATION_COMMAND = ""
_VERIFICATION_RECORDS: dict[str, VerificationRecord] = {}
_OBSERVED_PROBE_COMMANDS: list[dict[str, Any]] = []
_OBSERVED_PROBE_OPEN_FILES: set[str] = set()
_OBSERVED_COMMANDS_LOCK = Lock()
_CAPACITY_EVIDENCE: dict[str, Any] = {}
_DBOS_EVIDENCE: dict[str, Any] = {}
_NONIMPAIRMENT_EVIDENCE: dict[str, Any] = {}
_LIVE_WRITE_AUDIT_ACTIVE = False
_LIVE_WRITE_AUDIT_COMPLETED_TESTS = 0
_LIVE_WRITE_AUDIT_EVENTS: list[dict[str, str]] = []
_LIVE_WRITE_AUDIT_VIOLATIONS: list[dict[str, str]] = []


def _path_is_live(path: object) -> bool:
    if not isinstance(path, (str, bytes, os.PathLike)):
        return False
    try:
        candidate = str(Path(path).resolve()).lower()
    except (OSError, TypeError, ValueError):
        return False
    exact_paths = {str(item.resolve()).lower() for item in LIVE_STATE_PATHS}
    directory_prefixes = [f"{str(item.resolve()).lower()}{os.sep}" for item in LIVE_STATE_DIRECTORIES]
    return candidate in exact_paths or any(candidate.startswith(prefix) for prefix in directory_prefixes)


def _write_capable_open(mode: object) -> bool:
    if isinstance(mode, str):
        return any(flag in mode for flag in "wax+")
    if isinstance(mode, int):
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
        return bool(mode & write_flags)
    return False


def _live_write_audit_hook(event: str, args: tuple[object, ...]) -> None:
    if not _LIVE_WRITE_AUDIT_ACTIVE:
        return
    candidate_paths: tuple[object, ...] = ()
    single_path_event = event == "sqlite3.connect" or event in {
        "os.remove",
        "os.rmdir",
        "os.mkdir",
    }
    if (event == "open" and len(args) >= 2 and _write_capable_open(args[1])) or (single_path_event and args):
        candidate_paths = (args[0],)
    elif event in {"os.rename", "os.replace"} and len(args) >= 2:
        candidate_paths = (args[0], args[1])
    for path in candidate_paths:
        if _path_is_live(path):
            _LIVE_WRITE_AUDIT_EVENTS.append({"event": event, "path": str(path)})


sys.addaudithook(_live_write_audit_hook)


@pytest.fixture(autouse=True)
def _reject_in_process_live_state_writes() -> Any:
    global _LIVE_WRITE_AUDIT_ACTIVE, _LIVE_WRITE_AUDIT_COMPLETED_TESTS
    assert _LIVE_WRITE_AUDIT_ACTIVE is False
    _LIVE_WRITE_AUDIT_EVENTS.clear()
    _LIVE_WRITE_AUDIT_ACTIVE = True
    yield
    _LIVE_WRITE_AUDIT_ACTIVE = False
    _LIVE_WRITE_AUDIT_COMPLETED_TESTS += 1
    _LIVE_WRITE_AUDIT_VIOLATIONS.extend(_LIVE_WRITE_AUDIT_EVENTS)
    assert _LIVE_WRITE_AUDIT_EVENTS == []


class _AdoptionManifestPlugin:
    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(
        self,
        session: pytest.Session,
        exitstatus: pytest.ExitCode,
    ) -> None:
        suite_exit_code = int(exitstatus)
        records = []
        for predicate in REQUIRED_PREDICATES:
            record = _VERIFICATION_RECORDS.get(predicate)
            if record is not None and predicate == "live_system_nonimpairment":
                observed_value = dict(record.observed_value)
                observed_value["in_process_live_write_audit"] = {
                    "completed_test_calls": _LIVE_WRITE_AUDIT_COMPLETED_TESTS,
                    "violations": list(_LIVE_WRITE_AUDIT_VIOLATIONS),
                }
                record = replace(record, observed_value=observed_value)
            if record is not None and suite_exit_code != 0:
                record = replace(
                    record,
                    exit_code=suite_exit_code,
                    satisfied=False,
                )
            if record is not None:
                records.append(record)
        manifest = evaluate_verification_records(records)
        emitted = json.dumps(
            manifest.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        )
        print(f"DISPATCHER_NEXT_ADOPTION_MANIFEST={emitted}")
        if manifest.outcome != ADOPT_DBOS_A2A and suite_exit_code == 0:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED


@pytest.fixture(scope="session", autouse=True)
def _register_adoption_manifest_plugin(
    request: pytest.FixtureRequest,
) -> None:
    global _VERIFICATION_COMMAND
    _VERIFICATION_COMMAND = f"python -m pytest {subprocess.list2cmdline(list(request.config.invocation_params.args))}"
    plugin = _AdoptionManifestPlugin()
    request.config.pluginmanager.register(
        plugin,
        "dispatcher-next-adoption-manifest",
    )


def _record_verification(predicate: str, observed_value: Any) -> None:
    assert predicate not in _VERIFICATION_RECORDS
    assert _VERIFICATION_COMMAND
    _VERIFICATION_RECORDS[predicate] = VerificationRecord(
        predicate=predicate,
        command=_VERIFICATION_COMMAND,
        exit_code=0,
        observed_value=observed_value,
        satisfied=True,
        cleanup={
            "status": "complete",
            "scope": "pytest-owned temporary databases and subprocesses",
            "live_state_mutated": False,
        },
    )


def _environment() -> dict[str, str]:
    env = os.environ.copy()
    prior = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(PACKAGE_SOURCE) if not prior else f"{PACKAGE_SOURCE}{os.pathsep}{prior}"
    return env


def _record_process_tree(process: subprocess.Popen[str]) -> None:
    try:
        root = psutil.Process(process.pid)
        processes = [root, *root.children(recursive=True)]
    except psutil.NoSuchProcess:
        return
    observations: list[dict[str, Any]] = []
    open_files: set[str] = set()
    for observed in processes:
        try:
            command = " ".join(observed.cmdline()).lower()
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        try:
            open_files.update(str(item.path).lower() for item in observed.open_files())
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            pass
        observations.append({"pid": observed.pid, "command": command})
    with _OBSERVED_COMMANDS_LOCK:
        _OBSERVED_PROBE_OPEN_FILES.update(open_files)
        for observation in observations:
            if observation not in _OBSERVED_PROBE_COMMANDS:
                _OBSERVED_PROBE_COMMANDS.append(observation)


def _kill_process_tree(process: subprocess.Popen[str]) -> None:
    try:
        descendants = psutil.Process(process.pid).children(recursive=True)
    except psutil.NoSuchProcess:
        descendants = []
    for descendant in descendants:
        try:
            descendant.kill()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    process.kill()


def _run_probe(*args: str, timeout: float = 120, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, "-m", "groundtruth_kb.dispatcher_next.foundation", *args]
    process = subprocess.Popen(
        command,
        cwd=REPO_ROOT,
        env=_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.monotonic() + timeout
    while process.poll() is None:
        _record_process_tree(process)
        if time.monotonic() >= deadline:
            _kill_process_tree(process)
            stdout, stderr = process.communicate()
            raise subprocess.TimeoutExpired(command, timeout, output=stdout, stderr=stderr)
        time.sleep(0.005)
    _record_process_tree(process)
    stdout, stderr = process.communicate()
    completed = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    if check and completed.returncode != 0:
        raise AssertionError(
            f"foundation probe failed ({completed.returncode})\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return completed


def _result(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    assert lines, f"probe emitted no JSON\nstderr:\n{completed.stderr}"
    value = json.loads(lines[-1])
    assert isinstance(value, dict)
    return value


def _hashes(paths: tuple[Path, ...] = STATIC_LIVE_PATHS) -> dict[str, str]:
    return {path.relative_to(REPO_ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def _file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _live_state_snapshot() -> dict[str, str]:
    paths = list(LIVE_STATE_PATHS)
    snapshot: dict[str, str] = {}
    for directory in LIVE_STATE_DIRECTORIES:
        relative = f"{directory.relative_to(REPO_ROOT).as_posix()}/"
        if directory.exists():
            children = sorted(path for path in directory.rglob("*") if path.is_file())
            inventory = "\n".join(path.relative_to(directory).as_posix() for path in children)
            snapshot[relative] = f"directory:{hashlib.sha256(inventory.encode()).hexdigest()}"
            paths.extend(children)
        else:
            snapshot[relative] = "<missing>"
    for path in sorted(set(paths)):
        relative = path.relative_to(REPO_ROOT).as_posix()
        snapshot[relative] = _file_hash(path) if path.is_file() else "<missing>"
    return snapshot


def _observe_live_state_probe(
    probe: Callable[[int], dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, str], dict[str, str], list[list[str]]]:
    before = _live_state_snapshot()
    result = probe(0)
    after = _live_state_snapshot()
    changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    return result, before, after, [changed] if changed else []


def _observed_real_harness_commands() -> list[dict[str, Any]]:
    return [
        observation
        for observation in _OBSERVED_PROBE_COMMANDS
        if any(fragment in observation["command"] for fragment in REAL_HARNESS_COMMANDS)
    ]


def _observed_live_file_handles() -> list[str]:
    exact_paths = {str(path.resolve()).lower() for path in LIVE_STATE_PATHS}
    directory_prefixes = [f"{str(path.resolve()).lower()}{os.sep}" for path in LIVE_STATE_DIRECTORIES]
    return sorted(
        path
        for path in _OBSERVED_PROBE_OPEN_FILES
        if path in exact_paths or any(path.startswith(prefix) for prefix in directory_prefixes)
    )


def _process_inventory_evidence() -> dict[str, Any]:
    encoded = json.dumps(
        _OBSERVED_PROBE_COMMANDS,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return {
        "live_state_open_files": _observed_live_file_handles(),
        "observed_process_count": len(_OBSERVED_PROBE_COMMANDS),
        "observed_process_inventory_sha256": hashlib.sha256(encoded).hexdigest(),
        "observed_open_file_count": len(_OBSERVED_PROBE_OPEN_FILES),
        "real_harness_commands": _observed_real_harness_commands(),
    }


def _live_harness_descendants() -> list[dict[str, Any]]:
    descendants: list[dict[str, Any]] = []
    for process in psutil.Process().children(recursive=True):
        try:
            command = " ".join(process.cmdline()).lower()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
        if any(fragment in command for fragment in REAL_HARNESS_COMMANDS):
            descendants.append({"pid": process.pid, "command": command})
    return descendants


def _capacity_policy() -> CapacityPolicy:
    limits = {
        "global": 16,
        "role:prime-builder": 8,
        "role:loyal-opposition": 8,
        "harness:A": 2,
    }
    limits.update({f"provider:provider-{index}": 5 for index in range(20)})
    limits.update({f"model:model-{index}": 3 for index in range(20)})
    limits.update({f"harness:H{index}": 16 for index in range(20)})
    return CapacityPolicy(limits)


def _capacity_request(
    index: int,
    *,
    role: str = "prime-builder",
    provider: str | None = None,
    model: str | None = None,
    harness: str | None = None,
) -> CapacityRequest:
    return CapacityRequest(
        role=role,
        provider=provider or f"provider-{index % 20}",
        model=model or f"model-{index % 20}",
        harness=harness or f"H{index % 20}",
    )


def _release_acquired(ledger: CapacityLedger, results: list[dict[str, Any]]) -> None:
    for result in results:
        if result["acquired"]:
            released = ledger.release(str(result["lease_id"]))
            assert released["released"] is True


def _acquire_wave(
    ledger: CapacityLedger,
    requests: list[CapacityRequest],
    lease_prefix: str,
) -> list[dict[str, Any]]:
    barrier = Barrier(len(requests) + 1)

    def acquire(item: tuple[int, CapacityRequest]) -> dict[str, Any]:
        index, request = item
        barrier.wait()
        return ledger.acquire(request, f"{lease_prefix}-{index}", 60)

    with ThreadPoolExecutor(max_workers=len(requests)) as executor:
        futures = [executor.submit(acquire, item) for item in enumerate(requests)]
        barrier.wait()
        return [future.result() for future in futures]


def _peak_overlap(results: dict[str, dict[str, Any]]) -> int:
    events: list[tuple[float, int]] = []
    for result in results.values():
        events.append((float(result["started_at"]), 1))
        events.append((float(result["finished_at"]), -1))
    active = 0
    peak = 0
    for _, delta in sorted(events, key=lambda event: (event[0], -event[1])):
        active += delta
        peak = max(peak, active)
    return peak


def test_pinned_dependencies_import_under_python_314() -> None:
    versions = dependency_versions()
    probe_versions = _result(_run_probe("versions"))

    assert sys.version_info[:2] == (3, 14)
    assert versions == {
        "a2a-sdk": EXPECTED_A2A_VERSION,
        "dbos": EXPECTED_DBOS_VERSION,
    }
    assert probe_versions == versions
    assert importlib.metadata.version("dbos") == EXPECTED_DBOS_VERSION
    assert importlib.metadata.version("a2a-sdk") == EXPECTED_A2A_VERSION
    _record_verification(
        "python_3_14",
        {
            "python": ".".join(str(part) for part in sys.version_info[:3]),
            "dependencies": versions,
        },
    )


@pytest.mark.timeout(180)
def test_dbos_runs_sixteen_stub_subprocess_workflows_idempotently(tmp_path: Path) -> None:
    before = _hashes()

    def run_batch_attempt(attempt: int) -> dict[str, Any]:
        system_database = tmp_path / f"batch-{attempt}" / "dbos.sqlite"
        operation_database = tmp_path / f"batch-{attempt}" / "domain.sqlite"
        arguments = (
            "batch",
            "--system-database",
            str(system_database),
            "--operation-database",
            str(operation_database),
            "--workflow-prefix",
            "batch",
            "--count",
            "16",
            "--delay-seconds",
            "0.25",
        )
        first_result = _result(_run_probe(*arguments))
        second_result = _result(_run_probe(*arguments, "--executor-id", "repeat"))
        assert second_result == first_result
        retry_root = tmp_path / f"batch-{attempt}" / "retry"
        retry_success = _result(
            _run_probe(
                "retry-probe",
                "--system-database",
                str(retry_root / "success-dbos.sqlite"),
                "--workflow-id",
                f"retry-success-{attempt}",
                "--counter-path",
                str(retry_root / "success.counter"),
                "--transient-failures",
                "2",
            )
        )
        retry_exhausted_process = _run_probe(
            "retry-probe",
            "--system-database",
            str(retry_root / "exhausted-dbos.sqlite"),
            "--workflow-id",
            f"retry-exhausted-{attempt}",
            "--counter-path",
            str(retry_root / "exhausted.counter"),
            "--transient-failures",
            "3",
            check=False,
        )
        retry_exhausted = _result(retry_exhausted_process)
        assert retry_exhausted_process.returncode == 2
        return {
            "batch": first_result,
            "retry_exhausted": retry_exhausted,
            "retry_success": retry_success,
        }

    (
        probe_result,
        live_state_before,
        live_state_after,
        concurrent_changes,
    ) = _observe_live_state_probe(run_batch_attempt)
    first = probe_result["batch"]
    retry_success = probe_result["retry_success"]
    retry_exhausted = probe_result["retry_exhausted"]

    assert first["workflow_count"] == 16
    assert first["semantic_operation_count"] == 16
    assert len(first["workflow_ids"]) == 16
    assert len({result["worker_pid"] for result in first["results"].values()}) == 16
    assert _peak_overlap(first["results"]) == 16
    assert retry_success["succeeded"] is True
    assert retry_success["attempt_count"] == 3
    assert retry_success["max_attempts"] == 3
    assert retry_exhausted["succeeded"] is False
    assert retry_exhausted["attempt_count"] == 3
    assert retry_exhausted["max_attempts"] == 3
    _DBOS_EVIDENCE.update(
        {
            "measured_peak_overlap": _peak_overlap(first["results"]),
            "retry_exhaustion_attempts": retry_exhausted["attempt_count"],
            "retry_max_attempts": retry_exhausted["max_attempts"],
            "retry_success_attempts": retry_success["attempt_count"],
        }
    )
    assert _hashes() == before

    source = FOUNDATION_MODULE.read_text(encoding="utf-8")
    assert "dispatcher_runtime" not in source
    assert "gtkb_dispatcher_daemon" not in source
    assert "ollama_harness" not in source
    assert "openrouter_harness" not in source
    package_source = (
        "\n".join(path.read_text(encoding="utf-8") for path in sorted(PACKAGE_DIR.glob("*.py")))
        .replace("\\", "/")
        .lower()
    )
    assert not {reference for reference in FORBIDDEN_LIVE_REFERENCES if reference.lower() in package_source}
    assert _live_harness_descendants() == []
    assert _observed_real_harness_commands() == []
    assert _observed_live_file_handles() == []
    _NONIMPAIRMENT_EVIDENCE.update(
        {
            "concurrent_live_state_changes_observed": concurrent_changes,
            "live_state_after": live_state_after,
            "live_state_before": live_state_before,
            "live_harness_descendants": _live_harness_descendants(),
            "process_inventory": _process_inventory_evidence(),
            "observation_intervals": 1,
            "snapshot_probe": (
                "16-worker DBOS batch, deterministic replay, and bounded transient-retry success/exhaustion"
            ),
            "static_authority_hashes": before,
        }
    )
    _record_verification(
        "live_system_nonimpairment",
        dict(_NONIMPAIRMENT_EVIDENCE),
    )


def test_dbos_recovers_interrupted_executor_without_duplicate_domain_mutation(tmp_path: Path) -> None:
    system_database = tmp_path / "recovery" / "dbos.sqlite"
    operation_database = tmp_path / "recovery" / "domain.sqlite"
    crash_marker = tmp_path / "recovery" / "crash.marker"
    workflow_prefix = "recover-batch"
    workflow_count = 4
    common = (
        "--system-database",
        str(system_database),
        "--operation-database",
        str(operation_database),
        "--workflow-prefix",
        workflow_prefix,
        "--count",
        str(workflow_count),
    )

    crashed = _run_probe(
        "crash-batch",
        *common,
        "--crash-marker",
        str(crash_marker),
        "--pending-delay-seconds",
        "2.0",
        check=False,
    )
    assert crashed.returncode != 0
    assert crash_marker.read_text(encoding="utf-8") == "crash-once\n"
    assert semantic_operation_count(operation_database) == 1

    recovered = _result(_run_probe("recover-batch", *common))
    repeated = _result(
        _run_probe(
            "recover-batch",
            *common,
            "--executor-id",
            "recovery-repeat",
        )
    )

    assert recovered["workflow_count"] == workflow_count
    assert recovered["semantic_operation_count"] == workflow_count
    assert recovered["workflow_ids"] == [f"{workflow_prefix}-{index:03d}" for index in range(workflow_count)]
    assert {result["echo"]["mode"] for result in recovered["results"].values()} == {"crash-recovery-batch"}
    assert all(result["echo"]["workflow_id"] == workflow_id for workflow_id, result in recovered["results"].items())
    assert repeated == recovered
    _record_verification(
        "durable_recovery",
        {
            **_DBOS_EVIDENCE,
            "crash_exit_code": crashed.returncode,
            "domain_commits_before_recovery": 1,
            "pending_workflows_recovered": workflow_count - 1,
            "workflow_count": workflow_count,
        },
    )
    _record_verification(
        "semantic_idempotency",
        {
            "duplicate_domain_mutations": 0,
            "repeated_recovery_identical": repeated == recovered,
            "semantic_operation_count": recovered["semantic_operation_count"],
        },
    )


def test_a2a_completed_task_and_structured_artifact_round_trip() -> None:
    max_safe_integer = (1 << 53) - 1
    facade = A2AProtocolFacade()
    submitted = facade.submit(
        "task-completed",
        "dispatcher-next",
        {
            "operation": "review",
            "sequence": max_safe_integer,
            "work_item": "WI-5617",
        },
    )
    facade.start("task-completed")
    completed = facade.complete(
        "task-completed",
        {"accepted": True, "evidence": ["dbos", "a2a"]},
    )
    result = facade.result("task-completed")

    assert round_trip_task(submitted) == submitted
    assert round_trip_task(completed) == completed
    assert task_to_dict(round_trip_task(completed)) == task_to_dict(completed)
    assert result.state == "completed"
    assert result.terminal is True
    assert result.artifact == {
        "accepted": True,
        "evidence": ["dbos", "a2a"],
    }
    assert result.diagnostic is None
    assert [item.to_state for item in result.evidence] == [
        "submitted",
        "working",
        "completed",
    ]
    assert result.evidence[-1].artifact_id == "task-completed:artifact:2"

    terminal_results = [
        run_lifecycle(
            task_id=f"task-{outcome}",
            context_id="dispatcher-next",
            request="perform isolated review",
            outcome=outcome,  # type: ignore[arg-type]
            detail=detail,
        )
        for outcome, detail in (
            ("failed", "provider unavailable"),
            ("canceled", "owner canceled"),
        )
    ]
    invalid = A2AProtocolFacade()
    invalid.submit("task-invalid-comprehensive", "dispatcher-next", "request")
    with pytest.raises(InvalidTaskTransitionError, match="cannot transition"):
        invalid.complete("task-invalid-comprehensive", {"unexpected": True})
    with pytest.raises(A2AProtocolError, match="safe-integer range"):
        facade.submit(
            "task-unsafe-request",
            "dispatcher-next",
            {"unsafe": max_safe_integer + 1},
        )
    unsafe_completion = A2AProtocolFacade()
    unsafe_completion.submit("task-unsafe-artifact", "dispatcher-next", "request")
    unsafe_completion.start("task-unsafe-artifact")
    with pytest.raises(A2AProtocolError, match="safe-integer range"):
        unsafe_completion.complete(
            "task-unsafe-artifact",
            {"unsafe": -(max_safe_integer + 1)},
        )

    _record_verification(
        "a2a_task_artifact_round_trip",
        {
            "completed_artifact": result.artifact,
            "safe_integer_boundary": max_safe_integer,
            "terminal_states": [
                result.state,
                *(terminal.state for terminal in terminal_results),
            ],
            "unsafe_integers_rejected": True,
        },
    )


@pytest.mark.parametrize(
    ("outcome", "detail"),
    [
        ("failed", "provider unavailable"),
        ("canceled", "owner canceled"),
    ],
)
def test_a2a_failure_and_cancellation_round_trip(outcome: str, detail: str) -> None:
    result = run_lifecycle(
        task_id=f"task-{outcome}",
        context_id="dispatcher-next",
        request="perform isolated review",
        outcome=outcome,  # type: ignore[arg-type]
        detail=detail,
    )

    assert result.state == outcome
    assert result.terminal is True
    assert result.artifact is None
    assert result.diagnostic == detail
    assert [item.to_state for item in result.evidence] == [
        "submitted",
        "working",
        outcome,
    ]
    assert result.evidence[-1].artifact_id is None


def test_a2a_invalid_and_repeated_terminal_transitions_fail_closed() -> None:
    facade = A2AProtocolFacade()
    facade.submit("task-invalid", "dispatcher-next", "request")

    with pytest.raises(InvalidTaskTransitionError, match="cannot transition"):
        facade.complete("task-invalid", {"unexpected": True})

    facade.start("task-invalid")
    facade.fail("task-invalid", "expected failure")

    with pytest.raises(InvalidTaskTransitionError, match="already terminal"):
        facade.cancel("task-invalid", "too late")
    with pytest.raises(InvalidTaskTransitionError, match="already terminal"):
        facade.complete("task-invalid", {"too": "late"})


def test_capacity_enforces_every_intersecting_dimension_atomically(tmp_path: Path) -> None:
    ledger = CapacityLedger(tmp_path / "capacity" / "dimensions.sqlite", _capacity_policy())

    global_results = _acquire_wave(
        ledger,
        [
            _capacity_request(
                index,
                role="prime-builder" if index % 2 == 0 else "loyal-opposition",
            )
            for index in range(16)
        ],
        "global",
    )
    global_snapshot = ledger.snapshot()
    global_denied = ledger.acquire(
        _capacity_request(16, role="prime-builder"),
        "global-denied",
        60,
    )
    assert all(result["acquired"] for result in global_results)
    assert global_denied["acquired"] is False
    assert {item["dimension"] for item in global_denied["blockers"]} == {
        "global",
        "role:prime-builder",
    }
    assert global_snapshot["counts"]["global"] == 16
    assert global_snapshot["counts"]["role:prime-builder"] == 8
    assert global_snapshot["counts"]["role:loyal-opposition"] == 8
    _release_acquired(ledger, global_results)

    for role in ("prime-builder", "loyal-opposition"):
        role_results = _acquire_wave(
            ledger,
            [_capacity_request(index, role=role) for index in range(8)],
            role,
        )
        role_snapshot = ledger.snapshot()
        role_denied = ledger.acquire(
            _capacity_request(8, role=role),
            f"{role}-denied",
            60,
        )
        assert all(result["acquired"] for result in role_results)
        assert role_denied["acquired"] is False
        assert [item["dimension"] for item in role_denied["blockers"]] == [
            f"role:{role}",
        ]
        assert role_snapshot["counts"][f"role:{role}"] == 8
        _release_acquired(ledger, role_results)

    provider_results = _acquire_wave(
        ledger,
        [_capacity_request(index, provider="provider-0") for index in range(5)],
        "provider",
    )
    provider_snapshot = ledger.snapshot()
    provider_denied = ledger.acquire(
        _capacity_request(5, provider="provider-0"),
        "provider-denied",
        60,
    )
    assert all(result["acquired"] for result in provider_results)
    assert [item["dimension"] for item in provider_denied["blockers"]] == [
        "provider:provider-0",
    ]
    assert provider_snapshot["counts"]["provider:provider-0"] == 5
    _release_acquired(ledger, provider_results)

    model_results = _acquire_wave(
        ledger,
        [_capacity_request(index, model="model-0") for index in range(3)],
        "model",
    )
    model_snapshot = ledger.snapshot()
    model_denied = ledger.acquire(
        _capacity_request(3, model="model-0"),
        "model-denied",
        60,
    )
    assert all(result["acquired"] for result in model_results)
    assert [item["dimension"] for item in model_denied["blockers"]] == [
        "model:model-0",
    ]
    assert model_snapshot["counts"]["model:model-0"] == 3
    _release_acquired(ledger, model_results)

    harness_results = _acquire_wave(
        ledger,
        [_capacity_request(index, harness="A") for index in range(2)],
        "harness-a",
    )
    harness_snapshot = ledger.snapshot()
    harness_denied = ledger.acquire(
        _capacity_request(2, harness="A"),
        "harness-a-denied",
        60,
    )
    assert all(result["acquired"] for result in harness_results)
    assert [item["dimension"] for item in harness_denied["blockers"]] == [
        "harness:A",
    ]
    assert harness_snapshot["counts"]["harness:A"] == 2
    _release_acquired(ledger, harness_results)
    assert ledger.snapshot()["active_lease_count"] == 0
    _CAPACITY_EVIDENCE["peaks"] = {
        "global": global_snapshot["counts"]["global"],
        "prime_builder": global_snapshot["counts"]["role:prime-builder"],
        "loyal_opposition": global_snapshot["counts"]["role:loyal-opposition"],
        "provider": provider_snapshot["counts"]["provider:provider-0"],
        "model": model_snapshot["counts"]["model:model-0"],
        "harness_A": harness_snapshot["counts"]["harness:A"],
    }


def test_capacity_runs_one_hundred_jobs_under_atomic_contention(tmp_path: Path) -> None:
    ledger = CapacityLedger(tmp_path / "capacity" / "contention.sqlite", _capacity_policy())
    start = Event()
    saturated = Event()
    release_first_wave = Event()
    acquired_count = 0
    acquired_count_lock = Lock()

    def run_job(index: int) -> dict[str, Any]:
        nonlocal acquired_count
        request = _capacity_request(
            index,
            role="prime-builder" if index % 2 == 0 else "loyal-opposition",
        )
        lease_id = f"job-{index:03d}"
        start.wait()
        for attempt in range(1_000):
            result = ledger.acquire(request, lease_id, 30)
            if result["acquired"]:
                snapshot = ledger.snapshot()
                with acquired_count_lock:
                    acquired_count += 1
                    if acquired_count == 16:
                        saturated.set()
                assert release_first_wave.wait(timeout=10)
                released = ledger.release(lease_id)
                assert released["released"] is True
                return {
                    "job": index,
                    "attempts": attempt + 1,
                    "snapshot": snapshot,
                }
            assert result["reason"] == "capacity_exceeded"
            assert result["blockers"]
            time.sleep(0.001)
        raise AssertionError(f"job {index} did not acquire capacity")

    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = [executor.submit(run_job, index) for index in range(100)]
        start.set()
        assert saturated.wait(timeout=10)
        time.sleep(0.05)
        release_first_wave.set()
        results = [future.result() for future in futures]

    assert [result["job"] for result in results] == list(range(100))
    assert any(result["attempts"] > 1 for result in results)
    for result in results:
        snapshot = result["snapshot"]
        for dimension, observed in snapshot["counts"].items():
            assert observed <= _capacity_policy().limits[dimension]

    events = ledger.audit_events()
    assert sum(event["event_type"] == "lease_acquired" for event in events) == 100
    assert sum(event["event_type"] == "lease_released" for event in events) == 100
    assert any(event["event_type"] == "acquire_denied" for event in events)
    assert ledger.snapshot()["active_lease_count"] == 0
    _CAPACITY_EVIDENCE["jobs_completed"] = len(results)
    _CAPACITY_EVIDENCE["contention_retries_observed"] = any(result["attempts"] > 1 for result in results)


def test_capacity_recovers_expired_crash_lease_without_reuse(tmp_path: Path) -> None:
    now = [1_000.0]
    database = tmp_path / "capacity" / "recovery.sqlite"
    policy = _capacity_policy()
    ledger = CapacityLedger(database, policy, clock=lambda: now[0])
    acquired = ledger.acquire(_capacity_request(0, harness="A"), "crashed", 5)

    assert acquired["acquired"] is True
    changed_limits = policy.to_dict()
    changed_limits["global"] = 15
    with pytest.raises(InvalidCapacityPolicy, match="different policy"):
        CapacityLedger(
            database,
            CapacityPolicy(changed_limits),
            clock=lambda: now[0],
        )
    now[0] += 10

    restarted = CapacityLedger(database, policy, clock=lambda: now[0])
    recovered = restarted.recover_expired()
    assert recovered["recovered_lease_ids"] == ["crashed"]
    assert recovered["snapshot"]["active_lease_count"] == 0
    assert any(
        event["event_type"] == "lease_expired" and event["lease_id"] == "crashed" for event in restarted.audit_events()
    )
    with pytest.raises(DuplicateLeaseError, match="already been used"):
        restarted.acquire(_capacity_request(0, harness="A"), "crashed", 5)
    _CAPACITY_EVIDENCE["expired_lease_recovered"] = recovered["recovered_lease_ids"]
    _CAPACITY_EVIDENCE["policy_mismatch_rejected"] = True
    assert set(_CAPACITY_EVIDENCE) == {
        "contention_retries_observed",
        "expired_lease_recovered",
        "jobs_completed",
        "peaks",
        "policy_mismatch_rejected",
    }
    _record_verification("atomic_intersecting_caps", dict(_CAPACITY_EVIDENCE))


def test_adoption_manifest_is_binary_emitted_and_fails_closed() -> None:
    rejected = evaluate_adoption({name: True for name in REQUIRED_PREDICATES[:-1]})
    unsubstantiated = evaluate_adoption({name: True for name in REQUIRED_PREDICATES})
    passing_record = VerificationRecord(
        predicate=REQUIRED_PREDICATES[0],
        command=_VERIFICATION_COMMAND,
        exit_code=0,
        observed_value="observed",
        satisfied=True,
        cleanup={"status": "complete"},
    )
    failed = evaluate_verification_records(
        [
            VerificationRecord(
                predicate=REQUIRED_PREDICATES[0],
                command=_VERIFICATION_COMMAND,
                exit_code=1,
                observed_value="failed",
                satisfied=False,
                cleanup={"status": "complete"},
            ),
        ]
    )
    missing = evaluate_verification_records([passing_record])

    assert rejected.outcome == REJECT_AND_EVALUATE_HATCHET
    assert rejected.predicates["live_system_nonimpairment"] is False
    assert unsubstantiated.outcome == REJECT_AND_EVALUATE_HATCHET
    assert failed.outcome == REJECT_AND_EVALUATE_HATCHET
    assert failed.predicates[REQUIRED_PREDICATES[0]] is False
    assert missing.outcome == REJECT_AND_EVALUATE_HATCHET
    assert missing.predicates[REQUIRED_PREDICATES[-1]] is False
    assert set(rejected.to_dict()) == {"schema_version", "outcome", "predicates", "evidence"}
    with pytest.raises(ValueError, match="outcome"):
        AdoptionManifest(
            schema_version=1,
            outcome=ADOPT_DBOS_A2A,
            predicates={name: True for name in REQUIRED_PREDICATES},
            evidence={},
        )
