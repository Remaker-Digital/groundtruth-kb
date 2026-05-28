"""Tests for scripts/bridge_index_writer.py - bridge scheduler Slice 3 (WI-3374).

Per bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-001.md (Loyal Opposition
GO at -002). Covers T1-T10 of the proposal's spec-to-test mapping: lock
lifecycle, bounded-wait timeout, atomic update, concurrent no-lost-update,
release-on-exception, stale reclaim, fresh-lock retention, mutate-raises
safety, serialized observation order, and temp-file cleanup. T11-T12 add the
malformed-lock reclamation coverage required by the NO-GO at
bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-004.md: a stale malformed
lock is reclaimed; a fresh malformed lock is retained.

Every test runs under an isolated pytest tmp_path state directory; the real
.gtkb-state/bridge-poller/index-writer.lock is never touched.

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
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "bridge_index_writer.py"


@pytest.fixture(scope="module")
def mod():
    """Load scripts/bridge_index_writer.py as a module without side effects."""
    spec = importlib.util.spec_from_file_location("bridge_index_writer", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.modules.pop(spec.name, None)


# --- T1: lock lifecycle ------------------------------------------------------


def test_t1_lock_created_on_enter_removed_on_exit(mod, tmp_path):
    state = tmp_path / "state"
    lock_path = state / "index-writer.lock"
    assert not lock_path.exists()
    with mod.index_write_lock(state_dir=state):
        assert lock_path.exists()
    assert not lock_path.exists()


# --- T2: held lock blocks a second acquirer then times out -------------------


def test_t2_held_lock_blocks_then_times_out(mod, tmp_path):
    state = tmp_path / "state"
    with (
        mod.index_write_lock(state_dir=state),
        pytest.raises(mod.IndexWriteLockTimeout),
        mod.index_write_lock(state_dir=state, timeout_seconds=0.3),
    ):
        pass


# --- T3: atomic_index_update applies the mutation ----------------------------


def test_t3_atomic_update_applies_mutate(mod, tmp_path):
    state = tmp_path / "state"
    index = tmp_path / "INDEX.md"
    index.write_text("original\n", encoding="utf-8")
    result = mod.atomic_index_update(index, lambda t: t + "added\n", state_dir=state)
    assert result == "original\nadded\n"
    assert index.read_text(encoding="utf-8") == "original\nadded\n"


# --- T4: concurrent atomic_index_update calls lose no update -----------------


def test_t4_concurrent_updates_no_lost_update(mod, tmp_path):
    state = tmp_path / "state"
    index = tmp_path / "INDEX.md"
    index.write_text("", encoding="utf-8")
    worker_count = 20
    barrier = threading.Barrier(worker_count)
    errors: list[BaseException] = []

    def worker(i: int) -> None:
        try:
            barrier.wait(timeout=30)
            mod.atomic_index_update(
                index, lambda t: t + f"line-{i}\n", state_dir=state, timeout_seconds=30
            )
        except BaseException as exc:  # noqa: BLE001 - recorded and asserted below
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(worker_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors, errors
    lines = set(index.read_text(encoding="utf-8").splitlines())
    assert lines == {f"line-{i}" for i in range(worker_count)}


# --- T5: the lock is released when the context body raises -------------------


def test_t5_lock_released_on_exception(mod, tmp_path):
    state = tmp_path / "state"
    lock_path = state / "index-writer.lock"
    with pytest.raises(ValueError), mod.index_write_lock(state_dir=state):
        raise ValueError("boom")
    assert not lock_path.exists()
    # The lock is reusable after a body exception.
    with mod.index_write_lock(state_dir=state):
        assert lock_path.exists()
    assert not lock_path.exists()


# --- T6: a stale lock is reclaimed -------------------------------------------


def test_t6_stale_lock_is_reclaimed(mod, tmp_path):
    state = tmp_path / "state"
    state.mkdir(parents=True, exist_ok=True)
    lock_path = state / "index-writer.lock"
    stale = {
        "lock_token": "stale-token",
        "pid": 999999,
        "acquired_at": "2020-01-01T00:00:00+00:00",
        "heartbeat_at": "2020-01-01T00:00:00+00:00",
    }
    lock_path.write_text(json.dumps(stale), encoding="utf-8")
    with mod.index_write_lock(state_dir=state, timeout_seconds=2, ttl_seconds=30):
        record = json.loads(lock_path.read_text(encoding="utf-8"))
        assert record["lock_token"] != "stale-token"  # our fresh lock replaced it
    assert not lock_path.exists()


# --- T7: a fresh foreign lock is NOT reclaimed -------------------------------


def test_t7_fresh_lock_not_reclaimed(mod, tmp_path):
    state = tmp_path / "state"
    state.mkdir(parents=True, exist_ok=True)
    lock_path = state / "index-writer.lock"
    now = datetime.now(UTC).isoformat()
    fresh = {"lock_token": "fresh-token", "pid": 999999, "acquired_at": now, "heartbeat_at": now}
    lock_path.write_text(json.dumps(fresh), encoding="utf-8")
    with (
        pytest.raises(mod.IndexWriteLockTimeout),
        mod.index_write_lock(state_dir=state, timeout_seconds=0.3, ttl_seconds=30),
    ):
        pass
    # The fresh foreign lock is untouched.
    record = json.loads(lock_path.read_text(encoding="utf-8"))
    assert record["lock_token"] == "fresh-token"


# --- T8: a raising mutate releases the lock and leaves the index unchanged ---


def test_t8_mutate_raises_leaves_index_unchanged(mod, tmp_path):
    state = tmp_path / "state"
    lock_path = state / "index-writer.lock"
    index = tmp_path / "INDEX.md"
    index.write_text("keep-me\n", encoding="utf-8")

    def bad_mutate(_text: str) -> str:
        raise RuntimeError("mutate failed")

    with pytest.raises(RuntimeError):
        mod.atomic_index_update(index, bad_mutate, state_dir=state)
    assert index.read_text(encoding="utf-8") == "keep-me\n"
    assert not lock_path.exists()


# --- T9: serialized calls compose - each mutation observes the prior result --


def test_t9_serialized_calls_observe_prior_result(mod, tmp_path):
    state = tmp_path / "state"
    index = tmp_path / "INDEX.md"
    index.write_text("0\n", encoding="utf-8")

    def increment(text: str) -> str:
        last = int(text.splitlines()[-1])
        return text + f"{last + 1}\n"

    for _ in range(5):
        mod.atomic_index_update(index, increment, state_dir=state)
    # Each call read the file inside the lock and observed the prior write.
    assert index.read_text(encoding="utf-8") == "0\n1\n2\n3\n4\n5\n"


# --- T10: no sibling temp file remains after a successful update -------------


def test_t10_no_temp_file_remains(mod, tmp_path):
    state = tmp_path / "state"
    index = tmp_path / "INDEX.md"
    index.write_text("x\n", encoding="utf-8")
    mod.atomic_index_update(index, lambda t: t + "y\n", state_dir=state)
    leftover = [p for p in index.parent.iterdir() if p.suffix == ".tmp"]
    assert leftover == []


# --- T11: a stale malformed lock file is reclaimed ---------------------------


def test_t11_stale_malformed_lock_is_reclaimed(mod, tmp_path):
    """A truncated/empty lock file left by a crashed creator carries no
    parseable heartbeat. Once its mtime has aged past ttl_seconds it must be
    reclaimed, otherwise it blocks every future INDEX writer (NO-GO -004 P1)."""
    state = tmp_path / "state"
    state.mkdir(parents=True, exist_ok=True)
    lock_path = state / "index-writer.lock"
    # Not parseable JSON - a create interrupted before the full payload landed.
    lock_path.write_text("{ truncated", encoding="utf-8")
    old = time.time() - 3600  # malformed and on disk for an hour
    os.utime(lock_path, (old, old))
    with mod.index_write_lock(state_dir=state, timeout_seconds=2, ttl_seconds=30):
        # the abandoned malformed lock was reclaimed; our lock is valid JSON
        record = json.loads(lock_path.read_text(encoding="utf-8"))
        assert "lock_token" in record
    assert not lock_path.exists()


# --- T12: a fresh malformed lock file is NOT reclaimed prematurely -----------


def test_t12_fresh_malformed_lock_not_reclaimed(mod, tmp_path):
    """A malformed lock file younger than ttl_seconds may be a create still in
    progress and must not be deleted out from under its owner."""
    state = tmp_path / "state"
    state.mkdir(parents=True, exist_ok=True)
    lock_path = state / "index-writer.lock"
    lock_path.write_text("{ truncated", encoding="utf-8")
    # mtime is left at ~now: the malformed file is fresh.
    with (
        pytest.raises(mod.IndexWriteLockTimeout),
        mod.index_write_lock(state_dir=state, timeout_seconds=0.3, ttl_seconds=30),
    ):
        pass
    # the fresh malformed lock is untouched
    assert lock_path.exists()
    assert lock_path.read_text(encoding="utf-8") == "{ truncated"
