"""Frozen acceptance tests for modernization runtime interruption and recovery."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

from groundtruth_kb.runtime_recovery import (  # noqa: E402
    ClaimOutcome,
    CompletionConflict,
    OperationCollision,
    RecoveryStore,
    RuntimeStatus,
    StaleOwnership,
)


@dataclass
class ManualClock:
    value: float = 1_000.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def _claim(store: RecoveryStore, owner: str = "worker-a", *, max_attempts: int = 3):
    return store.claim(
        "op-001",
        operation_kind="implementation_slice",
        input_fingerprint="sha256:abc123",
        owner_id=owner,
        max_attempts=max_attempts,
        lease_seconds=30,
    )


def test_concurrent_attempts_have_exactly_one_owner(tmp_path: Path) -> None:
    store = RecoveryStore(tmp_path / "recovery.db")
    barrier = threading.Barrier(8)
    outcomes: list[ClaimOutcome] = []
    lock = threading.Lock()

    def compete(worker_number: int) -> None:
        barrier.wait()
        decision = store.claim(
            "concurrent-op",
            operation_kind="verification",
            input_fingerprint="sha256:shared",
            owner_id=f"worker-{worker_number}",
            max_attempts=3,
            lease_seconds=30,
        )
        with lock:
            outcomes.append(decision.outcome)

    threads = [threading.Thread(target=compete, args=(number,)) for number in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert all(not thread.is_alive() for thread in threads)
    assert outcomes.count(ClaimOutcome.ACQUIRED) == 1
    assert outcomes.count(ClaimOutcome.BUSY) == 7
    assert [event.event_type for event in store.events("concurrent-op")] == ["operation_started"]


def test_interrupted_attempt_resumes_from_durable_checkpoint(tmp_path: Path) -> None:
    clock = ManualClock()
    store = RecoveryStore(tmp_path / "recovery.db", clock=clock)
    first = _claim(store)
    assert first.claim is not None
    store.checkpoint(first.claim, {"completed_steps": ["authorize", "prepare"], "cursor": 2})

    clock.advance(31)
    observation = store.observe("op-001")
    assert observation is not None
    assert observation.recommended_action == "reclaim_interrupted"

    resumed = _claim(store, "worker-b")
    assert resumed.outcome is ClaimOutcome.ACQUIRED
    assert resumed.claim is not None
    assert resumed.claim.attempt_number == 2
    assert resumed.operation.checkpoint == {"completed_steps": ["authorize", "prepare"], "cursor": 2}
    assert [event.event_type for event in store.events("op-001")] == [
        "operation_started",
        "checkpoint_recorded",
        "ownership_reclaimed",
    ]


def test_stale_owner_cannot_mutate_after_reclaim(tmp_path: Path) -> None:
    clock = ManualClock()
    store = RecoveryStore(tmp_path / "recovery.db", clock=clock)
    first = _claim(store)
    assert first.claim is not None
    clock.advance(31)
    second = _claim(store, "worker-b")
    assert second.claim is not None

    with pytest.raises(StaleOwnership):
        store.checkpoint(first.claim, {"cursor": 99})
    with pytest.raises(StaleOwnership):
        store.heartbeat(first.claim)
    with pytest.raises(StaleOwnership):
        store.complete(first.claim, {"status": "wrong-owner"})
    with pytest.raises(StaleOwnership):
        store.fail(first.claim, "wrong owner")

    assert store.get("op-001") == second.operation


def test_retry_budget_is_bounded_and_exhaustion_quarantines(tmp_path: Path) -> None:
    clock = ManualClock()
    store = RecoveryStore(tmp_path / "recovery.db", clock=clock)

    for attempt in range(1, 4):
        decision = _claim(store, f"worker-{attempt}")
        assert decision.outcome is ClaimOutcome.ACQUIRED
        assert decision.claim is not None
        snapshot = store.fail(decision.claim, f"transient failure {attempt}", retry_delay_seconds=5)
        if attempt < 3:
            assert snapshot.status is RuntimeStatus.RETRY_WAIT
            waiting = _claim(store, "early-worker")
            assert waiting.outcome is ClaimOutcome.RETRY_WAIT
            clock.advance(5)
        else:
            assert snapshot.status is RuntimeStatus.QUARANTINED

    denied = _claim(store, "worker-4")
    assert denied.outcome is ClaimOutcome.QUARANTINED
    assert denied.operation.attempt_count == 3
    assert [event.event_type for event in store.events("op-001")] == [
        "operation_started",
        "retry_scheduled",
        "retry_started",
        "retry_scheduled",
        "retry_started",
        "operation_quarantined",
    ]


def test_nonretryable_failure_quarantines_immediately(tmp_path: Path) -> None:
    store = RecoveryStore(tmp_path / "recovery.db")
    decision = _claim(store)
    assert decision.claim is not None

    snapshot = store.fail(decision.claim, "invalid durable input", retryable=False)

    assert snapshot.status is RuntimeStatus.QUARANTINED
    observation = store.observe("op-001")
    assert observation is not None
    assert observation.recommended_action == "manual_intervention"
    assert observation.last_event.detail["reason"] == "non_retryable_failure"


def test_completion_is_idempotent_and_conflicting_result_fails_closed(tmp_path: Path) -> None:
    store = RecoveryStore(tmp_path / "recovery.db")
    decision = _claim(store)
    assert decision.claim is not None
    result = {"evidence": ["test-a", "test-b"], "status": "PASS"}

    completed = store.complete(decision.claim, result)
    repeated = store.complete(decision.claim, {"status": "PASS", "evidence": ["test-a", "test-b"]})

    assert completed == repeated
    assert completed.status is RuntimeStatus.COMPLETED
    assert [event.event_type for event in store.events("op-001")].count("operation_completed") == 1
    terminal_claim = _claim(store, "worker-b")
    assert terminal_claim.outcome is ClaimOutcome.COMPLETED
    assert terminal_claim.operation.result == result
    with pytest.raises(CompletionConflict):
        store.complete(decision.claim, {"status": "different"})


def test_operation_key_collision_fails_closed(tmp_path: Path) -> None:
    store = RecoveryStore(tmp_path / "recovery.db")
    _claim(store)

    with pytest.raises(OperationCollision):
        store.claim(
            "op-001",
            operation_kind="release",
            input_fingerprint="sha256:different",
            owner_id="worker-b",
            max_attempts=3,
            lease_seconds=30,
        )


def test_observation_exposes_recovery_state_and_ordered_events(tmp_path: Path) -> None:
    clock = ManualClock()
    store = RecoveryStore(tmp_path / "recovery.db", clock=clock)
    decision = _claim(store)
    assert decision.claim is not None
    store.checkpoint(decision.claim, {"cursor": 4})
    active = store.observe("op-001")
    assert active is not None
    assert active.recommended_action == "wait"
    assert active.reason == "operation has an active owner"
    assert active.event_count == 2
    assert active.last_event.event_type == "checkpoint_recorded"

    clock.advance(31)
    interrupted = store.observe("op-001")
    assert interrupted is not None
    assert interrupted.recommended_action == "reclaim_interrupted"
    resumed = _claim(store, "worker-b")
    assert resumed.claim is not None
    store.complete(resumed.claim, {"status": "PASS"})

    terminal = store.observe("op-001")
    assert terminal is not None
    assert terminal.recommended_action == "return_result"
    assert terminal.event_count == 4
    assert terminal.last_event.event_type == "operation_completed"
    assert [event.event_id for event in store.events("op-001")] == sorted(
        event.event_id for event in store.events("op-001")
    )
