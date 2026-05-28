# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Slice 2 tests for scripts/bridge_lease_registry.py.

Bridge scheduler program WI-3373; GO at
``bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-002.md``. T1-T12 cover
acquire / release / refresh, the stale -> reclaim transition, the lease
lifecycle, the token ownership guard, the context manager, slug validation,
and the single-winner property under concurrent acquisition. Every test runs
under an isolated ``tmp_path`` state directory so the real lease directory is
never touched.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "bridge_lease_registry.py"


def _load_module() -> ModuleType:
    """Load scripts/bridge_lease_registry.py via importlib (``scripts/`` is not
    a package), matching the loader idiom in test_cross_harness_bridge_trigger.py."""
    assert _MODULE_PATH.is_file(), f"Expected lease registry at {_MODULE_PATH}"
    module_name = "bridge_lease_registry"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_leases = _load_module()
acquire_lease = _leases.acquire_lease
release_lease = _leases.release_lease
refresh_lease = _leases.refresh_lease
is_lease_held = _leases.is_lease_held
reclaim_stale_leases = _leases.reclaim_stale_leases
document_lease = _leases.document_lease
LeaseUnavailable = _leases.LeaseUnavailable
DEFAULT_LEASE_TTL_SECONDS = _leases.DEFAULT_LEASE_TTL_SECONDS
LEASE_SCHEMA_VERSION = _leases.LEASE_SCHEMA_VERSION


def _backdate(lease_path: Path, *, seconds: int) -> None:
    """Rewrite a lease file's ``heartbeat_at`` to ``seconds`` in the past so a
    test can drive the stale/fresh boundary deterministically without sleeping.
    The ``lease_token`` is left intact."""
    record = json.loads(lease_path.read_text(encoding="utf-8"))
    record["heartbeat_at"] = (datetime.now(UTC) - timedelta(seconds=seconds)).isoformat()
    lease_path.write_text(json.dumps(record), encoding="utf-8")


# T1 -------------------------------------------------------------------------


def test_t1_acquire_creates_lease_file_with_metadata(tmp_path: Path) -> None:
    handle = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert handle is not None
    assert handle.path.is_file()
    record = json.loads(handle.path.read_text(encoding="utf-8"))
    assert record["schema_version"] == LEASE_SCHEMA_VERSION
    assert record["doc_slug"] == "widget-refactor"
    assert record["lease_token"] == handle.lease_token
    assert record["pid"] == os.getpid()
    assert record["action"] == "review"
    assert record["ttl_seconds"] == DEFAULT_LEASE_TTL_SECONDS
    assert isinstance(record["acquired_at"], str) and record["acquired_at"]
    assert isinstance(record["heartbeat_at"], str) and record["heartbeat_at"]


# T2 -------------------------------------------------------------------------


def test_t2_second_acquire_on_held_slug_returns_none(tmp_path: Path) -> None:
    first = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert first is not None
    second = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert second is None


# T3 -------------------------------------------------------------------------


def test_t3_release_allows_reacquire(tmp_path: Path) -> None:
    first = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert first is not None
    release_lease(first)
    assert not first.path.exists()
    second = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert second is not None


# T4 -------------------------------------------------------------------------


def test_t4_stale_lease_is_reclaimed_on_acquire(tmp_path: Path) -> None:
    first = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert first is not None
    _backdate(first.path, seconds=DEFAULT_LEASE_TTL_SECONDS + 120)
    second = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert second is not None
    assert second.lease_token != first.lease_token


# T5 -------------------------------------------------------------------------


def test_t5_fresh_lease_is_not_reclaimed(tmp_path: Path) -> None:
    handle = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert handle is not None
    assert reclaim_stale_leases(tmp_path) == []
    assert handle.path.is_file()


# T6 -------------------------------------------------------------------------


def test_t6_reclaim_removes_only_stale_and_returns_slugs(tmp_path: Path) -> None:
    stale_a = acquire_lease("alpha-thread", action="review", state_dir=tmp_path)
    stale_b = acquire_lease("beta-thread", action="verify", state_dir=tmp_path)
    fresh = acquire_lease("gamma-thread", action="review", state_dir=tmp_path)
    assert stale_a is not None and stale_b is not None and fresh is not None
    _backdate(stale_a.path, seconds=DEFAULT_LEASE_TTL_SECONDS + 120)
    _backdate(stale_b.path, seconds=DEFAULT_LEASE_TTL_SECONDS + 120)
    reclaimed = reclaim_stale_leases(tmp_path)
    assert reclaimed == ["alpha-thread", "beta-thread"]
    assert not stale_a.path.exists()
    assert not stale_b.path.exists()
    assert fresh.path.is_file()


# T7 -------------------------------------------------------------------------


def test_t7_refresh_extends_freshness(tmp_path: Path) -> None:
    handle = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert handle is not None
    _backdate(handle.path, seconds=DEFAULT_LEASE_TTL_SECONDS + 120)
    assert not is_lease_held("widget-refactor", state_dir=tmp_path)
    refresh_lease(handle)
    assert is_lease_held("widget-refactor", state_dir=tmp_path)


# T8 -------------------------------------------------------------------------


def test_t8_is_lease_held_reports_fresh_absent_stale(tmp_path: Path) -> None:
    assert is_lease_held("widget-refactor", state_dir=tmp_path) is False
    handle = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert handle is not None
    assert is_lease_held("widget-refactor", state_dir=tmp_path) is True
    _backdate(handle.path, seconds=DEFAULT_LEASE_TTL_SECONDS + 120)
    assert is_lease_held("widget-refactor", state_dir=tmp_path) is False


# T9 -------------------------------------------------------------------------


def test_t9_release_is_ownership_guarded(tmp_path: Path) -> None:
    first = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert first is not None
    _backdate(first.path, seconds=DEFAULT_LEASE_TTL_SECONDS + 120)
    second = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert second is not None
    assert second.lease_token != first.lease_token
    # first's lease went stale and was reclaimed; releasing first's stale
    # handle must NOT delete second's freshly acquired lease.
    release_lease(first)
    assert second.path.is_file()
    assert is_lease_held("widget-refactor", state_dir=tmp_path) is True


# T10 ------------------------------------------------------------------------


def test_t10_document_lease_context_manager(tmp_path: Path) -> None:
    with document_lease("widget-refactor", action="review", state_dir=tmp_path) as handle:
        assert handle is not None
        assert is_lease_held("widget-refactor", state_dir=tmp_path) is True
    # released on normal exit
    assert is_lease_held("widget-refactor", state_dir=tmp_path) is False

    # raises LeaseUnavailable when a fresh lease is already held
    blocker = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
    assert blocker is not None
    with pytest.raises(LeaseUnavailable), document_lease("widget-refactor", action="review", state_dir=tmp_path):
        pass
    release_lease(blocker)

    # released even when the body raises
    with (
        pytest.raises(RuntimeError, match="boom"),
        document_lease("widget-refactor", action="review", state_dir=tmp_path),
    ):
        raise RuntimeError("boom")
    assert is_lease_held("widget-refactor", state_dir=tmp_path) is False


# T11 ------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_slug",
    [
        "../escape",
        "with/slash",
        "with\\backslash",
        "UPPERCASE",
        "with space",
        "",
        "trailing-",
        "-leading",
        "dot.slug",
    ],
)
def test_t11_invalid_slug_raises_value_error(tmp_path: Path, bad_slug: str) -> None:
    with pytest.raises(ValueError):
        acquire_lease(bad_slug, action="review", state_dir=tmp_path)


# T12 ------------------------------------------------------------------------


def test_t12_concurrent_acquire_yields_single_winner(tmp_path: Path) -> None:
    worker_count = 8
    barrier = threading.Barrier(worker_count)
    results: list[object] = []
    results_lock = threading.Lock()

    def _worker() -> None:
        barrier.wait()
        outcome = acquire_lease("widget-refactor", action="review", state_dir=tmp_path)
        with results_lock:
            results.append(outcome)

    threads = [threading.Thread(target=_worker) for _ in range(worker_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    handles = [r for r in results if r is not None]
    losers = [r for r in results if r is None]
    assert len(handles) == 1
    assert len(losers) == worker_count - 1
