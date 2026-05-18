"""Tests for scripts/bridge_dispatch_priority.py - bridge scheduler Slice 6
(WI-3377).

Per bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md (Loyal Opposition
GO at -002). Covers T1-T11 of the proposal's spec-to-test mapping: priority
ordering, monotonic aging, head-start values, unknown-priority default,
anti-starvation, descending-score sort, within-tier oldest-first, equal-score
tie-break, future-dated clamp, select_next, and pure-function determinism.
T12-T14 add the coverage required by GO -002 follow-on constraint 8: exact
score-and-timestamp ties preserve input order (the P3-CONSTRAINT), timezone
handling, and case-insensitive priority normalization.

The module is a pure function with no filesystem state; every test passes an
explicit `now` so results never depend on the wall clock.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "bridge_dispatch_priority.py"

NOW = "2026-05-18T12:00:00+00:00"


@pytest.fixture(scope="module")
def mod():
    """Load scripts/bridge_dispatch_priority.py as a module without side effects."""
    spec = importlib.util.spec_from_file_location("bridge_dispatch_priority", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.modules.pop(spec.name, None)


# --- T1: priority ordering at equal age --------------------------------------


def test_t1_priority_ordering_at_equal_age(mod):
    filed = "2026-05-18T10:00:00+00:00"  # 2h old, identical for every tier
    scores = [mod.dispatch_score(filed_at=filed, priority=p, now=NOW)
              for p in ("P0", "P1", "P2", "P3", "P4")]
    assert scores == sorted(scores, reverse=True)  # P0 > P1 > P2 > P3 > P4
    assert len(set(scores)) == 5  # strictly decreasing - no ties


# --- T2: dispatch_score is monotonic increasing in age -----------------------


def test_t2_score_monotonic_in_age(mod):
    s_old = mod.dispatch_score(filed_at="2026-05-18T02:00:00+00:00", priority="P2", now=NOW)
    s_mid = mod.dispatch_score(filed_at="2026-05-18T07:00:00+00:00", priority="P2", now=NOW)
    s_new = mod.dispatch_score(filed_at="2026-05-18T11:00:00+00:00", priority="P2", now=NOW)
    assert s_old > s_mid > s_new


# --- T3: priority_headstart returns the documented per-tier values -----------


def test_t3_priority_headstart_values(mod):
    hs = {p: mod.priority_headstart(p) for p in ("P0", "P1", "P2", "P3", "P4")}
    assert hs == {"P0": 96.0, "P1": 72.0, "P2": 48.0, "P3": 24.0, "P4": 0.0}
    assert hs["P0"] > hs["P1"] > hs["P2"] > hs["P3"] > hs["P4"]


# --- T4: an unknown or None priority resolves to DEFAULT_PRIORITY ------------


def test_t4_unknown_priority_defaults(mod):
    default_hs = mod.priority_headstart(mod.DEFAULT_PRIORITY)
    assert mod.priority_headstart(None) == default_hs
    assert mod.priority_headstart("nonsense") == default_hs
    assert mod.priority_headstart(123) == default_hs   # non-string - no raise
    assert mod.priority_headstart("") == default_hs


# --- T5: anti-starvation - an aged low-priority entry outranks a fresh P0 ----


def test_t5_anti_starvation(mod):
    # a P4 entry aged 100h vs a freshly-filed P0 entry
    old_p4 = mod.dispatch_score(filed_at="2026-05-14T08:00:00+00:00", priority="P4", now=NOW)
    fresh_p0 = mod.dispatch_score(filed_at=NOW, priority="P0", now=NOW)
    assert old_p4 > fresh_p0


# --- T6: sort_by_dispatch_priority orders by descending score ----------------


def test_t6_sort_descending_score(mod):
    entries = [
        {"id": "fresh-p3", "filed_at": "2026-05-18T11:00:00+00:00", "priority": "P3"},
        {"id": "old-p0", "filed_at": "2026-05-17T12:00:00+00:00", "priority": "P0"},
        {"id": "mid-p4", "filed_at": "2026-05-18T00:00:00+00:00", "priority": "P4"},
    ]
    ordered = mod.sort_by_dispatch_priority(entries, now=NOW)
    scores = [mod.dispatch_score(filed_at=e["filed_at"], priority=e["priority"], now=NOW)
              for e in ordered]
    assert scores == sorted(scores, reverse=True)


# --- T7: within one priority tier, older filed_at is ordered first -----------


def test_t7_within_tier_oldest_first(mod):
    entries = [
        {"id": "newest", "filed_at": "2026-05-18T11:00:00+00:00", "priority": "P2"},
        {"id": "oldest", "filed_at": "2026-05-18T01:00:00+00:00", "priority": "P2"},
        {"id": "middle", "filed_at": "2026-05-18T06:00:00+00:00", "priority": "P2"},
    ]
    ordered = mod.sort_by_dispatch_priority(entries, now=NOW)
    assert [e["id"] for e in ordered] == ["oldest", "middle", "newest"]


# --- T8: an identical score is broken by older filed_at first ----------------


def test_t8_equal_score_oldest_first(mod):
    # P0 filed 1h ago scores 96 + 1 = 97; P4 filed 97h ago scores 0 + 97 = 97
    p0 = {"id": "p0-fresh", "filed_at": "2026-05-18T11:00:00+00:00", "priority": "P0"}
    p4 = {"id": "p4-old", "filed_at": "2026-05-14T11:00:00+00:00", "priority": "P4"}
    assert (mod.dispatch_score(filed_at=p0["filed_at"], priority="P0", now=NOW)
            == mod.dispatch_score(filed_at=p4["filed_at"], priority="P4", now=NOW))
    ordered = mod.sort_by_dispatch_priority([p0, p4], now=NOW)
    assert [e["id"] for e in ordered] == ["p4-old", "p0-fresh"]


# --- T9: a future-dated filed_at clamps age to zero --------------------------


def test_t9_future_filed_at_clamps(mod):
    score = mod.dispatch_score(filed_at="2026-05-18T22:00:00+00:00", priority="P2", now=NOW)
    assert score == mod.priority_headstart("P2")  # bare head-start, age clamped to 0
    assert score >= 0.0


# --- T10: select_next returns the highest-scoring entry, None for empty ------


def test_t10_select_next(mod):
    entries = [
        {"id": "low", "filed_at": "2026-05-18T11:00:00+00:00", "priority": "P4"},
        {"id": "high", "filed_at": "2026-05-18T11:00:00+00:00", "priority": "P0"},
    ]
    assert mod.select_next(entries, now=NOW)["id"] == "high"
    assert mod.select_next([], now=NOW) is None


# --- T11: dispatch_score / select_next are pure and deterministic ------------


def test_t11_pure_deterministic(mod):
    kwargs = dict(filed_at="2026-05-18T06:00:00+00:00", priority="P1", now=NOW)
    first = mod.dispatch_score(**kwargs)
    for _ in range(50):
        assert mod.dispatch_score(**kwargs) == first
    entries = [
        {"id": "a", "filed_at": "2026-05-18T06:00:00+00:00", "priority": "P1"},
        {"id": "b", "filed_at": "2026-05-18T09:00:00+00:00", "priority": "P0"},
    ]
    order1 = [e["id"] for e in mod.sort_by_dispatch_priority(entries, now=NOW)]
    order2 = [e["id"] for e in mod.sort_by_dispatch_priority(entries, now=NOW)]
    assert order1 == order2
    # the module is a pure function: it performs no filesystem access
    src = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "import os" not in src
    assert "import pathlib" not in src
    assert "open(" not in src


# --- T12: an exact score-and-timestamp tie preserves input order -------------


def test_t12_exact_tie_preserves_input_order(mod):
    # identical priority and identical filed_at - identical score and tie-break
    e1 = {"id": "first", "filed_at": "2026-05-18T08:00:00+00:00", "priority": "P2"}
    e2 = {"id": "second", "filed_at": "2026-05-18T08:00:00+00:00", "priority": "P2"}
    assert [e["id"] for e in mod.sort_by_dispatch_priority([e1, e2], now=NOW)] == \
        ["first", "second"]
    assert [e["id"] for e in mod.sort_by_dispatch_priority([e2, e1], now=NOW)] == \
        ["second", "first"]


# --- T13: timezone handling - the same instant scores identically -----------


def test_t13_timezone_handling(mod):
    # the same instant (2026-05-18T00:00 UTC) expressed four ways
    offset_iso = "2026-05-18T00:00:00+00:00"
    bare_iso = "2026-05-18T00:00:00"                              # no offset -> UTC
    aware_other = datetime(2026, 5, 18, 2, 0, 0,
                           tzinfo=timezone(timedelta(hours=2)))   # 00:00 UTC
    naive_dt = datetime(2026, 5, 18, 0, 0, 0)                     # naive -> UTC
    base = mod.dispatch_score(filed_at=offset_iso, priority="P4", now=NOW)
    assert mod.dispatch_score(filed_at=bare_iso, priority="P4", now=NOW) == base
    assert mod.dispatch_score(filed_at=aware_other, priority="P4", now=NOW) == base
    assert mod.dispatch_score(filed_at=naive_dt, priority="P4", now=NOW) == base
    assert base == 12.0  # 12h age, P4 head-start 0 - host-local time never applied


# --- T14: priority normalization is case-insensitive ------------------------


def test_t14_case_insensitive_priority(mod):
    assert mod.priority_headstart("p2") == mod.priority_headstart("P2") == 48.0
    assert mod.priority_headstart(" P0 ") == 96.0
    assert mod.priority_headstart("p4") == 0.0
    # 'p2' must NOT silently degrade to the DEFAULT_PRIORITY head-start
    assert mod.priority_headstart("p2") != mod.priority_headstart(mod.DEFAULT_PRIORITY)
    # dispatch_score honors the normalized priority
    assert (mod.dispatch_score(filed_at=NOW, priority="p0", now=NOW)
            == mod.dispatch_score(filed_at=NOW, priority="P0", now=NOW) == 96.0)
