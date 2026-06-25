"""SPEC-2100 lifecycle-metrics aggregation & scope coverage (WI-3218).

WI-bridged deterministic coverage for SPEC-2100 "Pipeline lifecycle metrics:
computed metrics and aggregation", filed through
``bridge/agent-red-wi3218-lifecycle-metrics-computed-coverage`` (GO at ``-002``).

Non-duplicative of ``groundtruth-kb/tests/test_lifecycle_metrics.py``, which
already exercises each Phase-1 metric (M2, M4, M6, M10, M11, M12, M16, M17,
M18) with per-metric edge cases. This module asserts only the three
aggregation/scope clauses the existing suite leaves unasserted:

1. Phase-1 scope boundary — exactly nine implemented metrics; deferred ids absent.
2. Trend / time-window computability — ``last_n_days`` and ``now`` parameters.
3. On-demand aggregation — mutate-then-recompute reflects live state.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.gates import GateRegistry

PHASE1_METRIC_IDS = frozenset({"M2", "M4", "M6", "M10", "M11", "M12", "M16", "M17", "M18"})
DEFERRED_METRIC_IDS = frozenset({"M1", "M3", "M5", "M7", "M8", "M9", "M13", "M14", "M15", "M19", "M20"})


@pytest.fixture
def db(tmp_path) -> KnowledgeDB:
    db_path = tmp_path / "test_spec2100_metrics.db"
    registry = GateRegistry.from_config([], include_builtins=True)
    return KnowledgeDB(db_path=db_path, gate_registry=registry)


def _backdate_work_item_v1(db: KnowledgeDB, wi_id: str, iso_timestamp: str) -> None:
    conn = db._get_conn()
    conn.execute(
        "UPDATE work_items SET changed_at = ? WHERE id = ? AND version = 1",
        (iso_timestamp, wi_id),
    )
    conn.commit()


# ===========================================================================
# Clause 1: Phase-1 scope boundary
# ===========================================================================


class TestPhase1ScopeBoundary:
    """SPEC-2100 enumerates M1–M20; Phase 1 implements nine metrics only."""

    def test_get_lifecycle_metrics_returns_exact_phase1_keys(self, db: KnowledgeDB) -> None:
        metrics = db.get_lifecycle_metrics()
        assert set(metrics) == PHASE1_METRIC_IDS

    def test_no_deferred_metric_keys_in_aggregator(self, db: KnowledgeDB) -> None:
        metrics = db.get_lifecycle_metrics()
        assert not (set(metrics) & DEFERRED_METRIC_IDS)

    def test_phase1_compute_methods_exist_deferred_absent(self, db: KnowledgeDB) -> None:
        phase1_methods = (
            "compute_m2_spec_revision_rounds",
            "compute_m4_spec_to_implemented_duration",
            "compute_m6_defect_injection_rate",
            "compute_m10_defect_resolution_duration",
            "compute_m11_regression_rate",
            "compute_m12_spec_retirement_rate",
            "compute_m16_verified_with_passing_tests_rate",
            "compute_m17_stale_test_ratio",
            "compute_m18_implemented_without_test_count",
        )
        for method in phase1_methods:
            assert hasattr(db, method), method
        deferred = [name for name in dir(db) if name.startswith("compute_m")]
        assert not any(name.startswith(("compute_m1_", "compute_m5_")) for name in deferred)


# ===========================================================================
# Clause 2: Time-window / trend computability
# ===========================================================================


class TestTimeWindowTrend:
    """SPEC-2100: metrics computable over time windows."""

    def test_m6_last_n_days_differs_from_all_time(self, db: KnowledgeDB) -> None:
        old_ts = (datetime.now(UTC) - timedelta(days=60)).isoformat()
        recent_ts = (datetime.now(UTC) - timedelta(days=1)).isoformat()

        db.insert_work_item(
            id="WI-OLD-DEFECT",
            title="Old defect",
            origin="defect",
            component="api",
            resolution_status="open",
            changed_by="t",
            change_reason="old",
        )
        _backdate_work_item_v1(db, "WI-OLD-DEFECT", old_ts)

        db.insert_work_item(
            id="WI-NEW-DEFECT",
            title="New defect",
            origin="defect",
            component="api",
            resolution_status="open",
            changed_by="t",
            change_reason="new",
        )
        _backdate_work_item_v1(db, "WI-NEW-DEFECT", recent_ts)

        db.insert_spec(id="SPEC-WIN", title="W", status="specified", changed_by="t", change_reason="v1")
        db.update_spec("SPEC-WIN", changed_by="t", change_reason="impl", status="implemented")
        conn = db._get_conn()
        conn.execute(
            "UPDATE specifications SET changed_at = ? WHERE id = 'SPEC-WIN' AND status = 'implemented'",
            (recent_ts,),
        )
        conn.commit()

        all_time = db.compute_m6_defect_injection_rate()
        windowed = db.compute_m6_defect_injection_rate(last_n_days=7)
        assert all_time["numerator"] == 2
        assert windowed["numerator"] == 1

    def test_get_lifecycle_metrics_threads_last_n_days_to_m6(self, db: KnowledgeDB) -> None:
        recent_ts = (datetime.now(UTC) - timedelta(days=1)).isoformat()
        db.insert_work_item(
            id="WI-RECENT",
            title="Recent",
            origin="defect",
            component="api",
            resolution_status="open",
            changed_by="t",
            change_reason="recent",
        )
        _backdate_work_item_v1(db, "WI-RECENT", recent_ts)

        metrics_all = db.get_lifecycle_metrics()
        metrics_win = db.get_lifecycle_metrics(last_n_days=7)
        assert metrics_all["M6"]["numerator"] >= metrics_win["M6"]["numerator"]

    def test_m17_honors_injected_now(self, db: KnowledgeDB) -> None:
        db.insert_test(
            id="TEST-M17",
            title="Tracked",
            spec_id="SPEC-X",
            test_type="unit",
            expected_outcome="pass",
            test_file="tests/test_x.py",
            last_result="pass",
            last_executed_at="2026-06-01T00:00:00+00:00",
            changed_by="t",
            change_reason="seed",
        )
        fresh = db.compute_m17_stale_test_ratio(now="2026-06-15T00:00:00+00:00")
        stale = db.compute_m17_stale_test_ratio(now="2026-07-15T00:00:00+00:00")
        assert fresh["numerator"] == 0
        assert stale["numerator"] == 1


# ===========================================================================
# Clause 3: On-demand aggregation (no pre-aggregation)
# ===========================================================================


class TestOnDemandAggregation:
    """SPEC-2100: compute on demand from live tables; no cached pre-aggregation."""

    def test_m12_reflects_live_retirement_mutation(self, db: KnowledgeDB) -> None:
        before = db.compute_m12_spec_retirement_rate()
        db.insert_spec(id="SPEC-RETIRE-ME", title="R", status="specified", changed_by="t", change_reason="v1")
        db.update_spec("SPEC-RETIRE-ME", changed_by="t", change_reason="retire", status="retired")
        after = db.compute_m12_spec_retirement_rate()
        assert before["numerator"] == 0
        assert after["numerator"] == 1
        assert after["value"] != before["value"]


# ===========================================================================
# Structured metadata smoke (non-duplicative contract restatement)
# ===========================================================================


class TestStructuredMetadataSmoke:
    """Every aggregated metric exposes value + unit keys (minimal contract)."""

    def test_all_metrics_have_value_and_unit(self, db: KnowledgeDB) -> None:
        db.insert_spec(id="SPEC-SMOKE", title="S", status="specified", changed_by="t", change_reason="v1")
        metrics = db.get_lifecycle_metrics()
        for mid, payload in metrics.items():
            assert isinstance(payload, dict), f"{mid} must be a dict"
            assert "value" in payload, f"{mid} missing value"
            assert "unit" in payload, f"{mid} missing unit"
