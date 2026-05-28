"""Tests for scripts/bridge_dispatch_concurrency.py - bridge scheduler Slice 4
(WI-3375).

Per bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md (Loyal Opposition
GO at -002). Covers T1-T13 of the proposal's spec-to-test mapping: role-limit
defaults and env override, registration, at-capacity None, per-role
independence, release, in_flight_count / available_slots, stale-slot reclaim,
heartbeat refresh, token-guarded release, reclaim_stale_workers, concurrent
registration capping, and the worker_slot context manager. T14 adds the
invalid-role validation coverage required by the GO -002 P3-CONSTRAINT.
T15-T16 add malformed-slot coverage (a crash mid-create leaves an unparseable
slot file): a stale malformed slot is reclaimed, a fresh malformed slot is
retained - applying the Slice 3 INDEX-writer NO-GO -004 lesson to the sibling
slot pool.

Every test runs under an isolated pytest tmp_path state directory; the real
.gtkb-state/bridge-poller/workers directory is never touched.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "bridge_dispatch_concurrency.py"


@pytest.fixture(scope="module")
def mod():
    """Load scripts/bridge_dispatch_concurrency.py as a module without side effects."""
    spec = importlib.util.spec_from_file_location("bridge_dispatch_concurrency", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.modules.pop(spec.name, None)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Clear any GTKB_DISPATCH_CONCURRENCY_* override so a test that relies on
    the default per-role limits is not perturbed by the ambient environment."""
    monkeypatch.delenv("GTKB_DISPATCH_CONCURRENCY_PRIME_BUILDER", raising=False)
    monkeypatch.delenv("GTKB_DISPATCH_CONCURRENCY_LOYAL_OPPOSITION", raising=False)


def _slot_file(state_dir: Path, role: str, slot_index: int) -> Path:
    """The documented slot-file path: <state_dir>/workers/<role>/slot-<n>.lock."""
    return state_dir / "workers" / role / f"slot-{slot_index}.lock"


# --- T1: role_limit defaults -------------------------------------------------


def test_t1_role_limit_defaults(mod):
    assert mod.role_limit("loyal-opposition") == 3
    assert mod.role_limit("prime-builder") == 2


# --- T2: role_limit honors the per-role environment override -----------------


def test_t2_role_limit_env_override(mod, monkeypatch):
    monkeypatch.setenv("GTKB_DISPATCH_CONCURRENCY_PRIME_BUILDER", "5")
    assert mod.role_limit("prime-builder") == 5
    # a non-positive or non-integer override is ignored - the default applies
    monkeypatch.setenv("GTKB_DISPATCH_CONCURRENCY_PRIME_BUILDER", "0")
    assert mod.role_limit("prime-builder") == 2
    monkeypatch.setenv("GTKB_DISPATCH_CONCURRENCY_PRIME_BUILDER", "not-an-int")
    assert mod.role_limit("prime-builder") == 2


# --- T3: register_worker returns a WorkerSlot and creates the slot file ------


def test_t3_register_worker_creates_slot(mod, tmp_path):
    state = tmp_path / "state"
    slot = mod.register_worker("prime-builder", state_dir=state)
    assert slot is not None
    assert slot.role == "prime-builder"
    assert slot.slot_index == 0
    assert _slot_file(state, "prime-builder", 0).exists()


# --- T4: register_worker returns None once the role is at capacity -----------


def test_t4_register_worker_none_at_capacity(mod, tmp_path):
    state = tmp_path / "state"
    s0 = mod.register_worker("prime-builder", state_dir=state)
    s1 = mod.register_worker("prime-builder", state_dir=state)
    assert s0 is not None and s1 is not None  # prime-builder default limit is 2
    assert mod.register_worker("prime-builder", state_dir=state) is None


# --- T5: per-role independence -----------------------------------------------


def test_t5_per_role_independence(mod, tmp_path):
    state = tmp_path / "state"
    assert mod.register_worker("prime-builder", state_dir=state) is not None
    assert mod.register_worker("prime-builder", state_dir=state) is not None
    assert mod.register_worker("prime-builder", state_dir=state) is None  # full
    # loyal-opposition has its own slot directory and limit - unaffected
    assert mod.register_worker("loyal-opposition", state_dir=state) is not None


# --- T6: release_worker frees a slot -----------------------------------------


def test_t6_release_frees_slot(mod, tmp_path):
    state = tmp_path / "state"
    mod.register_worker("prime-builder", state_dir=state)
    s1 = mod.register_worker("prime-builder", state_dir=state)
    assert mod.register_worker("prime-builder", state_dir=state) is None  # full
    assert mod.release_worker(s1) is True
    # a slot was freed - registration succeeds again
    assert mod.register_worker("prime-builder", state_dir=state) is not None


# --- T7: in_flight_count and available_slots track register and release ------


def test_t7_in_flight_and_available(mod, tmp_path):
    state = tmp_path / "state"
    assert mod.in_flight_count("prime-builder", state_dir=state) == 0
    assert mod.available_slots("prime-builder", state_dir=state) == 2
    s0 = mod.register_worker("prime-builder", state_dir=state)
    assert mod.in_flight_count("prime-builder", state_dir=state) == 1
    assert mod.available_slots("prime-builder", state_dir=state) == 1
    mod.register_worker("prime-builder", state_dir=state)
    assert mod.in_flight_count("prime-builder", state_dir=state) == 2
    assert mod.available_slots("prime-builder", state_dir=state) == 0
    mod.release_worker(s0)
    assert mod.in_flight_count("prime-builder", state_dir=state) == 1
    assert mod.available_slots("prime-builder", state_dir=state) == 1


# --- T8: a stale worker slot is reclaimed and its index reused ---------------


def test_t8_stale_slot_reclaimed(mod, tmp_path):
    state = tmp_path / "state"
    slot_path = _slot_file(state, "prime-builder", 0)
    slot_path.parent.mkdir(parents=True, exist_ok=True)
    stale = {
        "schema_version": 1,
        "role": "prime-builder",
        "slot_index": 0,
        "worker_token": "stale-token",
        "pid": 999999,
        "acquired_at": "2020-01-01T00:00:00+00:00",
        "heartbeat_at": "2020-01-01T00:00:00+00:00",
        "ttl_seconds": 1800.0,
    }
    slot_path.write_text(json.dumps(stale), encoding="utf-8")
    slot = mod.register_worker("prime-builder", state_dir=state)
    assert slot is not None
    assert slot.slot_index == 0  # the stale slot's index was reclaimed and reused
    record = json.loads(slot_path.read_text(encoding="utf-8"))
    assert record["worker_token"] == slot.worker_token
    assert record["worker_token"] != "stale-token"


# --- T9: refresh_worker extends freshness ------------------------------------


def test_t9_refresh_extends_freshness(mod, tmp_path):
    state = tmp_path / "state"
    slot = mod.register_worker("prime-builder", state_dir=state)
    assert slot is not None
    slot_path = _slot_file(state, "prime-builder", slot.slot_index)
    # age the heartbeat so the slot is stale; preserve the worker_token so
    # refresh_worker's ownership guard still matches this handle
    record = json.loads(slot_path.read_text(encoding="utf-8"))
    record["heartbeat_at"] = "2020-01-01T00:00:00+00:00"
    slot_path.write_text(json.dumps(record), encoding="utf-8")
    assert mod.in_flight_count("prime-builder", state_dir=state) == 0  # stale
    assert mod.refresh_worker(slot) is True
    assert mod.in_flight_count("prime-builder", state_dir=state) == 1  # fresh again


# --- T10: release_worker is token-guarded ------------------------------------


def test_t10_release_token_guarded(mod, tmp_path):
    state = tmp_path / "state"
    slot = mod.register_worker("prime-builder", state_dir=state)
    assert slot is not None
    slot_path = _slot_file(state, "prime-builder", slot.slot_index)
    # simulate the slot reclaimed as stale and re-registered by another worker
    record = json.loads(slot_path.read_text(encoding="utf-8"))
    record["worker_token"] = "different-worker-token"
    slot_path.write_text(json.dumps(record), encoding="utf-8")
    assert mod.release_worker(slot) is False  # token mismatch - not freed
    assert slot_path.exists()
    survivor = json.loads(slot_path.read_text(encoding="utf-8"))
    assert survivor["worker_token"] == "different-worker-token"


# --- T11: reclaim_stale_workers removes only stale slots ---------------------


def test_t11_reclaim_stale_workers(mod, tmp_path):
    state = tmp_path / "state"

    def write_slot(role: str, idx: int, heartbeat: str, token: str) -> Path:
        path = _slot_file(state, role, idx)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "role": role,
                    "slot_index": idx,
                    "worker_token": token,
                    "pid": 1,
                    "acquired_at": heartbeat,
                    "heartbeat_at": heartbeat,
                    "ttl_seconds": 1800.0,
                }
            ),
            encoding="utf-8",
        )
        return path

    now = datetime.now(UTC).isoformat()
    old = "2020-01-01T00:00:00+00:00"
    fresh_pb = write_slot("prime-builder", 0, now, "fresh-pb")
    stale_pb = write_slot("prime-builder", 1, old, "stale-pb")
    stale_lo = write_slot("loyal-opposition", 0, old, "stale-lo")

    reclaimed = mod.reclaim_stale_workers(state)

    assert set(reclaimed) == {"prime-builder/slot-1", "loyal-opposition/slot-0"}
    assert fresh_pb.exists()
    assert not stale_pb.exists()
    assert not stale_lo.exists()


# --- T12: concurrent registration is capped at exactly role_limit ------------


def test_t12_concurrent_registration_caps_at_limit(mod, tmp_path):
    state = tmp_path / "state"
    role = "loyal-opposition"
    limit = mod.role_limit(role)  # 3
    worker_count = 16
    barrier = threading.Barrier(worker_count)
    results: list[object] = []
    results_lock = threading.Lock()
    errors: list[BaseException] = []

    def worker() -> None:
        try:
            barrier.wait(timeout=30)
            slot = mod.register_worker(role, state_dir=state)
            with results_lock:
                results.append(slot)
        except BaseException as exc:  # noqa: BLE001 - recorded and asserted below
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(worker_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors, errors
    granted = [r for r in results if r is not None]
    denied = [r for r in results if r is None]
    assert len(granted) == limit
    assert len(denied) == worker_count - limit
    assert sorted(s.slot_index for s in granted) == list(range(limit))


# --- T13: the worker_slot context manager ------------------------------------


def test_t13_worker_slot_context_manager(mod, tmp_path):
    state = tmp_path / "state"
    # registers on enter, releases on exit
    with mod.worker_slot("prime-builder", state_dir=state) as slot:
        assert slot is not None
        assert _slot_file(state, "prime-builder", slot.slot_index).exists()
        slot_index = slot.slot_index
    assert not _slot_file(state, "prime-builder", slot_index).exists()

    # releases on exception
    with pytest.raises(ValueError), mod.worker_slot("prime-builder", state_dir=state):
        raise ValueError("boom")
    assert mod.in_flight_count("prime-builder", state_dir=state) == 0

    # raises DispatchCapacityExhausted when the role is at capacity
    s0 = mod.register_worker("prime-builder", state_dir=state)
    s1 = mod.register_worker("prime-builder", state_dir=state)
    assert s0 is not None and s1 is not None
    with pytest.raises(mod.DispatchCapacityExhausted), mod.worker_slot("prime-builder", state_dir=state):
        pass


# --- T14: invalid role labels are rejected by every public entry point -------


def test_t14_invalid_role_rejected(mod, tmp_path):
    state = tmp_path / "state"
    invalid_roles = [
        "",  # empty string
        "prime-builder/extra",  # forward-slash path separator
        "loyal-opposition\\evil",  # backslash path separator
        "..",  # dot traversal
        "prime.builder",  # dot
        "PRIME-BUILDER",  # wrong case - not a canonical role
        "reviewer",  # unknown role
    ]
    for bad in invalid_roles:
        with pytest.raises(ValueError):
            mod.role_limit(bad)
        with pytest.raises(ValueError):
            mod.register_worker(bad, state_dir=state)
        with pytest.raises(ValueError):
            mod.in_flight_count(bad, state_dir=state)
        with pytest.raises(ValueError):
            mod.available_slots(bad, state_dir=state)
    # validation runs before any mkdir, so no stray worker directory was made
    workers = state / "workers"
    if workers.exists():
        assert {p.name for p in workers.iterdir()} <= {"prime-builder", "loyal-opposition"}


# --- T15: a stale malformed slot file is reclaimed ---------------------------


def test_t15_stale_malformed_slot_reclaimed(mod, tmp_path):
    """A truncated/empty slot file left by a worker that crashed mid-create
    carries no parseable heartbeat. Once aged past the default ttl it must be
    reclaimable, otherwise it would permanently burn a slot index."""
    state = tmp_path / "state"
    slot_path = _slot_file(state, "prime-builder", 0)
    slot_path.parent.mkdir(parents=True, exist_ok=True)
    slot_path.write_text("{ truncated", encoding="utf-8")  # not parseable JSON
    old = time.time() - 7200  # malformed and on disk for two hours
    os.utime(slot_path, (old, old))

    # register_worker reclaims the abandoned malformed slot and reuses index 0
    slot = mod.register_worker("prime-builder", state_dir=state)
    assert slot is not None
    assert slot.slot_index == 0
    record = json.loads(slot_path.read_text(encoding="utf-8"))
    assert record["worker_token"] == slot.worker_token

    # reclaim_stale_workers also clears a stale malformed slot
    other = _slot_file(state, "prime-builder", 1)
    other.write_text("", encoding="utf-8")  # an empty file is malformed too
    os.utime(other, (old, old))
    reclaimed = mod.reclaim_stale_workers(state)
    assert "prime-builder/slot-1" in reclaimed
    assert not other.exists()


# --- T16: a fresh malformed slot file is retained ----------------------------


def test_t16_fresh_malformed_slot_retained(mod, tmp_path):
    """A malformed slot file younger than the ttl may be a create still in
    progress and must not be deleted out from under its owner."""
    state = tmp_path / "state"
    slot_path = _slot_file(state, "prime-builder", 0)
    slot_path.parent.mkdir(parents=True, exist_ok=True)
    slot_path.write_text("{ truncated", encoding="utf-8")  # mtime left at ~now

    # register_worker treats the fresh malformed index 0 as occupied and lands
    # on the next free index rather than deleting a possible in-flight create
    slot = mod.register_worker("prime-builder", state_dir=state)
    assert slot is not None
    assert slot.slot_index == 1
    assert slot_path.exists()
    assert slot_path.read_text(encoding="utf-8") == "{ truncated"

    # reclaim_stale_workers leaves the fresh malformed slot untouched
    reclaimed = mod.reclaim_stale_workers(state)
    assert "prime-builder/slot-0" not in reclaimed
    assert slot_path.exists()
