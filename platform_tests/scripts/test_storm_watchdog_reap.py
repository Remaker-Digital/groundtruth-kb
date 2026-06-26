# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/ops/storm_watchdog_reap.py (WI-4828).

The reap *decision* is a pure function; these exercise the protect/reap tiers,
the dispatched-tree safety scoping (interactive sessions are never touched), and
determinism with an injected ``now`` so there is no clock dependency.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MODULE_PATH = _REPO_ROOT / "scripts" / "ops" / "storm_watchdog_reap.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("storm_watchdog_reap_test", _MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Register before exec so frozen dataclasses can resolve cls.__module__ in
    # sys.modules (Python 3.14 dataclass processing requires this for a module
    # loaded via spec_from_file_location).
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_M = _load_module()
Process = _M.Process
Lease = _M.Lease
ProvenanceRecord = _M.ProvenanceRecord
decide_reap = _M.decide_reap

NOW = 1_000_000.0
GRACE = _M.DEFAULT_STARTUP_GRACE_SECONDS  # 120
MAX_LIFE = _M.DEFAULT_MAX_LIFETIME_SECONDS  # 900


def _old(offset: float = 300.0) -> float:
    """An epoch create-time older than the startup grace window."""
    return NOW - offset


def _root(pid: int, *, name: str = "codex", age: float = 300.0) -> Process:
    """A dispatched-worker root (codex exec / harness python)."""
    return Process(pid=pid, ppid=1, name=name, create_time_epoch=_old(age), dispatched=True)


def _helper(pid: int, ppid: int, *, name: str = "node_repl", age: float = 300.0) -> Process:
    """A non-root family helper (dispatched=False; in scope via its root)."""
    return Process(pid=pid, ppid=ppid, name=name, create_time_epoch=_old(age), dispatched=False)


def _prov(pid: int, *, root: int, age: float = 300.0):
    """A provenance record for ``pid`` (create-time matched to ``_helper`` default)."""
    return ProvenanceRecord(pid=pid, create_time_epoch=_old(age), dispatch_root_pid=root)


def test_live_lease_holder_protected() -> None:
    procs = [_root(100)]
    leases = [Lease(pid=100, acquired_at_epoch=NOW - 300, doc_slug="thread-a")]
    d = decide_reap(procs, leases, now=NOW)
    assert d.reap == []
    assert 100 in d.protect
    assert d.reasons[100] == "live_lease_holder"


def test_descendants_of_lease_holder_protected() -> None:
    # codex worker (100) holds the lease; node_repl (101) + sandbox (102) are its family.
    procs = [_root(100), _helper(101, 100), _helper(102, 101, name="codex-windows-sandbox")]
    leases = [Lease(pid=100, acquired_at_epoch=NOW - 300)]
    d = decide_reap(procs, leases, now=NOW)
    assert d.reap == []
    assert set(d.protect) == {100, 101, 102}
    assert d.reasons[101] == "descendant_of_lease_holder"
    assert d.reasons[102] == "descendant_of_lease_holder"


def test_cold_start_grace_protects_recent_process() -> None:
    # Young dispatched worker (within grace), no lease yet — mid-startup, pre-lease.
    procs = [Process(pid=200, ppid=1, name="python", create_time_epoch=NOW - 30, dispatched=True)]
    d = decide_reap(procs, [], now=NOW)
    assert d.reap == []
    assert d.reasons[200] == "cold_start_grace"


def test_orphan_without_lease_reaped() -> None:
    # A dispatched root, old, no live lease — a true corpse/orphan.
    procs = [_root(300)]
    d = decide_reap(procs, [], now=NOW)
    assert d.reap == [300]
    assert d.reasons[300] == "orphan_no_lease"


def test_over_lifetime_lease_holder_reaped() -> None:
    # Lease acquired beyond max-lifetime — a genuine hang (backstop behind WI-4806).
    procs = [_root(400, age=MAX_LIFE + 100)]
    leases = [Lease(pid=400, acquired_at_epoch=NOW - (MAX_LIFE + 100))]
    d = decide_reap(procs, leases, now=NOW)
    assert d.reap == [400]
    assert 400 not in d.protect
    assert d.reasons[400] == "over_lifetime_straggler"


def test_many_healthy_workers_none_reaped() -> None:
    # 20 healthy workers x (1 root + 3 family) = 80 processes, far over the old 15
    # raw-count threshold. None reaped: the raw-count kill is gone.
    procs: list = []
    leases: list = []
    for w in range(20):
        root = 1000 + w * 10
        procs.append(_root(root))
        leases.append(Lease(pid=root, acquired_at_epoch=NOW - 200, doc_slug=f"thread-{w}"))
        for c in range(1, 4):
            procs.append(_helper(root + c, root))
    d = decide_reap(procs, leases, now=NOW)
    assert d.reap == []
    assert len(d.protect) == 80


def test_interactive_tree_is_never_touched() -> None:
    # An interactive codex session (root dispatched=False, no 'exec') + its
    # helper family, old and lease-less: the component has NO dispatched root, so
    # it is neither reaped nor protected — left entirely untouched.
    procs = [
        Process(pid=700, ppid=1, name="codex", create_time_epoch=_old(), dispatched=False),
        _helper(701, 700),
        _helper(702, 701, name="codex-command-runner"),
    ]
    d = decide_reap(procs, [], now=NOW)
    assert d.reap == []
    assert d.protect == []
    assert d.reasons == {}


def test_orphaned_helper_family_without_dispatched_root_ignored() -> None:
    # Helpers whose dispatched root already died: the surviving component has no
    # dispatched member, so it is left untouched (safe — we do not reap ambiguous
    # families that might belong to an interactive session).
    procs = [_helper(801, 800), _helper(802, 801)]  # ppid 800 is gone (dead root)
    d = decide_reap(procs, [], now=NOW)
    assert d.reap == []
    assert d.protect == []


def test_decide_reap_is_pure_for_fixed_inputs() -> None:
    procs = [
        _root(100),
        _helper(101, 100),
        _root(300),  # dispatched orphan root
        _root(400, age=MAX_LIFE + 100),
    ]
    leases = [
        Lease(pid=100, acquired_at_epoch=NOW - 300),
        Lease(pid=400, acquired_at_epoch=NOW - (MAX_LIFE + 100)),
    ]
    d1 = decide_reap(procs, leases, now=NOW)
    d2 = decide_reap(procs, leases, now=NOW)
    assert d1 == d2
    assert d1.reap == sorted([300, 400])
    assert set(d1.protect) == {100, 101}


def test_stale_lease_not_protective() -> None:
    # A lease acquired past max-lifetime ("stale"/expired) does NOT shield its
    # pid: heartbeat freshness is irrelevant; only the lifetime budget matters.
    procs = [_root(600, age=MAX_LIFE + 1)]
    leases = [Lease(pid=600, acquired_at_epoch=NOW - (MAX_LIFE + 1))]
    d = decide_reap(procs, leases, now=NOW)
    assert 600 not in d.protect
    assert d.reap == [600]
    assert d.reasons[600] == "over_lifetime_straggler"


# --------------------------------------------------------------------------- #
# WI-4834: precise dead-root orphan attribution via the pid-provenance ledger. #
# --------------------------------------------------------------------------- #


def test_decide_reap_reaps_provenance_attributed_dead_root_orphan() -> None:
    # Orphan helpers whose dispatched root (800) has died. Recorded in provenance
    # while the root was alive, they are precisely attributable and reapable.
    procs = [_helper(801, 800), _helper(802, 801)]  # ppid 800 (root) is gone
    provenance = [_prov(801, root=800), _prov(802, root=800)]
    d = decide_reap(procs, [], now=NOW, provenance=provenance)
    assert d.reap == [801, 802]
    assert d.reasons[801] == "orphan_dead_dispatched_root"
    assert d.reasons[802] == "orphan_dead_dispatched_root"


def test_decide_reap_leaves_unattributed_orphan_untouched() -> None:
    # The same orphan family, but provenance covers only an unrelated pid. With
    # no provenance record, the orphans are left entirely untouched -- the
    # interactive-session safety boundary (an interactive tree is never recorded).
    procs = [_helper(801, 800), _helper(802, 801)]
    provenance = [_prov(999, root=998)]  # unrelated
    d = decide_reap(procs, [], now=NOW, provenance=provenance)
    assert d.reap == []
    assert d.protect == []
    assert d.reasons == {}


def test_decide_reap_provenance_requires_create_time_match() -> None:
    # pid-reuse guard: a provenance record with the same pid but a DIFFERENT
    # create_time (the recorded process exited and the pid was reused) must not
    # attribute/reap the current process.
    procs = [_helper(801, 800)]  # current create_time = _old(300)
    provenance = [ProvenanceRecord(pid=801, create_time_epoch=_old(900.0), dispatch_root_pid=800)]
    d = decide_reap(procs, [], now=NOW, provenance=provenance)
    assert d.reap == []
    assert 801 not in d.reasons


def test_decide_reap_live_dispatched_root_unchanged_with_provenance() -> None:
    # When the dispatched root is alive, the in-scope path governs and provenance
    # does not double-act: the family is protected, not reaped.
    procs = [_root(100), _helper(101, 100)]
    leases = [Lease(pid=100, acquired_at_epoch=NOW - 300)]
    provenance = [_prov(101, root=100)]  # root 100 is alive (in processes)
    d = decide_reap(procs, leases, now=NOW, provenance=provenance)
    assert d.reap == []
    assert set(d.protect) == {100, 101}


def test_decide_reap_provenance_orphan_within_grace_protected() -> None:
    # Cold-start grace is honored even for a provenance-attributed dead-root
    # orphan: a young orphan is not reaped.
    young = Process(pid=801, ppid=800, name="node_repl", create_time_epoch=NOW - 30, dispatched=False)
    provenance = [ProvenanceRecord(pid=801, create_time_epoch=NOW - 30, dispatch_root_pid=800)]
    d = decide_reap([young], [], now=NOW, provenance=provenance)
    assert d.reap == []
