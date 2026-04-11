"""Tests for lifecycle metrics computation (SPEC-2100 Phase 1).

Covers: M2, M4, M6, M10, M11, M12, M16, M17, M18 with edge cases,
zero-denominator handling, and metadata structure per Codex conditions.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.gates import GateRegistry


@pytest.fixture
def db(tmp_path) -> KnowledgeDB:
    db_path = tmp_path / "test_metrics.db"
    registry = GateRegistry.from_config([], include_builtins=True)
    return KnowledgeDB(db_path=db_path, gate_registry=registry)


def _seed_basic(db: KnowledgeDB) -> None:
    """Seed DB with a small but varied dataset for metrics computation."""
    # Two specs: one goes specified->implemented, one goes specified->implemented->verified
    db.insert_spec(id="SPEC-A", title="A", status="specified", changed_by="t", change_reason="v1")
    db.update_spec("SPEC-A", changed_by="t", change_reason="impl", status="implemented")

    db.insert_spec(id="SPEC-B", title="B", status="specified", changed_by="t", change_reason="v1")
    db.update_spec("SPEC-B", changed_by="t", change_reason="rev", title="B2")
    db.update_spec("SPEC-B", changed_by="t", change_reason="impl", status="implemented")
    db.update_spec("SPEC-B", changed_by="t", change_reason="verify", status="verified")

    # One retired spec
    db.insert_spec(id="SPEC-C", title="C", status="specified", changed_by="t", change_reason="v1")
    db.update_spec("SPEC-C", changed_by="t", change_reason="retire", status="retired")

    # Test linked to SPEC-B (verified)
    db.insert_test(
        id="TEST-1",
        title="T1",
        spec_id="SPEC-B",
        test_type="unit",
        expected_outcome="pass",
        test_file="tests/test_b.py",
        last_result="pass",
        last_executed_at="2026-04-10T00:00:00+00:00",
        changed_by="t",
        change_reason="test",
    )

    # Defect WI (open then resolved)
    db.insert_work_item(
        id="WI-D1",
        title="Defect",
        origin="defect",
        component="api",
        resolution_status="open",
        changed_by="t",
        change_reason="bug",
    )
    db.update_work_item(
        "WI-D1",
        changed_by="t",
        change_reason="fixed",
        resolution_status="resolved",
        stage="resolved",
        owner_approved=True,
    )

    # Assertion runs
    db.insert_assertion_run("SPEC-A", 2, True, [{"r": "pass"}], "ci")
    db.insert_assertion_run("SPEC-B", 4, True, [{"r": "pass"}], "ci")
    db.insert_assertion_run("SPEC-B", 4, False, [{"r": "fail"}], "ci")


# ===========================================================================
# Metric structure tests — every metric must return structured metadata
# ===========================================================================


class TestMetricStructure:
    """All metrics must return value + metadata, not bare scalars."""

    def test_all_metrics_have_required_keys(self, db):
        _seed_basic(db)
        metrics = db.get_lifecycle_metrics()
        for mid, result in metrics.items():
            assert isinstance(result, dict), f"{mid} must return dict, got {type(result)}"
            assert "value" in result, f"{mid} missing 'value'"
            assert "unit" in result, f"{mid} missing 'unit'"

    def test_ratio_metrics_have_numerator_denominator(self, db):
        _seed_basic(db)
        metrics = db.get_lifecycle_metrics()
        ratio_metrics = ["M6", "M11", "M12", "M16", "M17"]
        for mid in ratio_metrics:
            result = metrics[mid]
            if result["value"] is not None:
                assert "numerator" in result, f"{mid} missing 'numerator'"
                assert "denominator" in result, f"{mid} missing 'denominator'"


# ===========================================================================
# M2: Spec Revision Rounds
# ===========================================================================


class TestM2:
    def test_basic(self, db):
        _seed_basic(db)
        m = db.compute_m2_spec_revision_rounds()
        assert m["value"] is not None
        assert m["unit"] == "versions"
        assert m["sample_count"] == 2  # SPEC-A and SPEC-B reached implemented

    def test_empty_db(self, db):
        m = db.compute_m2_spec_revision_rounds()
        assert m["value"] is None
        assert m["status"] == "not_applicable"

    def test_single_version_impl(self, db):
        """Spec created directly as implemented = version 1."""
        db.insert_spec(id="SPEC-FAST", title="Fast", status="implemented", changed_by="t", change_reason="direct")
        m = db.compute_m2_spec_revision_rounds()
        assert m["value"] == 1.0
        assert m["min"] == 1


# ===========================================================================
# M4: Spec-to-Implemented Duration
# ===========================================================================


class TestM4:
    def test_basic(self, db):
        _seed_basic(db)
        m = db.compute_m4_spec_to_implemented_duration()
        assert m["value"] is not None
        assert m["unit"] == "hours"
        assert m["sample_count"] == 2

    def test_empty_db(self, db):
        m = db.compute_m4_spec_to_implemented_duration()
        assert m["value"] is None

    def test_no_specified_phase(self, db):
        """Spec created directly as implemented — no specified->implemented transition."""
        db.insert_spec(id="SPEC-DIRECT", title="Direct", status="implemented", changed_by="t", change_reason="direct")
        m = db.compute_m4_spec_to_implemented_duration()
        assert m["value"] is None or m["sample_count"] == 0


# ===========================================================================
# M6: Defect Injection Rate
# ===========================================================================


class TestM6:
    def test_basic(self, db):
        _seed_basic(db)
        m = db.compute_m6_defect_injection_rate()
        assert m["value"] is not None
        assert m["numerator"] == 1  # 1 defect WI
        assert m["denominator"] == 2  # 2 specs reached implemented

    def test_zero_implementations(self, db):
        db.insert_work_item(
            id="WI-X",
            title="X",
            origin="defect",
            component="test",
            resolution_status="open",
            changed_by="t",
            change_reason="test",
        )
        m = db.compute_m6_defect_injection_rate()
        assert m["value"] is None
        assert m["status"] == "not_applicable"

    def test_zero_defects(self, db):
        db.insert_spec(id="SPEC-OK", title="OK", status="specified", changed_by="t", change_reason="v1")
        db.update_spec("SPEC-OK", changed_by="t", change_reason="impl", status="implemented")
        m = db.compute_m6_defect_injection_rate()
        assert m["value"] == 0.0
        assert m["numerator"] == 0


# ===========================================================================
# M10: Defect Resolution Duration
# ===========================================================================


class TestM10:
    def test_basic(self, db):
        _seed_basic(db)
        m = db.compute_m10_defect_resolution_duration()
        assert m["value"] is not None
        assert m["unit"] == "hours"
        assert m["sample_count"] >= 1
        assert "skipped_missing_event_count" in m

    def test_no_events(self, db):
        m = db.compute_m10_defect_resolution_duration()
        assert m["value"] is None
        assert m["status"] == "not_applicable"

    def test_unresolved_defect_skipped(self, db):
        """A defect WI without a resolved event should be counted as skipped."""
        db.insert_work_item(
            id="WI-OPEN",
            title="Open defect",
            origin="defect",
            component="test",
            resolution_status="open",
            changed_by="t",
            change_reason="bug",
        )
        m = db.compute_m10_defect_resolution_duration()
        assert m["skipped_missing_event_count"] >= 1


# ===========================================================================
# M11: Regression Rate (aggregate only)
# ===========================================================================


class TestM11:
    def test_basic(self, db):
        _seed_basic(db)
        m = db.compute_m11_regression_rate()
        assert m["unit"] == "ratio"
        assert m["denominator"] == 3  # 3 assertion runs
        assert m["numerator"] == 1  # 1 failed

    def test_empty_db(self, db):
        m = db.compute_m11_regression_rate()
        assert m["value"] is None
        assert m["status"] == "not_applicable"

    def test_all_passing(self, db):
        db.insert_spec(id="S1", title="T", status="specified", changed_by="t", change_reason="t")
        db.insert_assertion_run("S1", 1, True, [{"r": "pass"}], "ci")
        db.insert_assertion_run("S1", 1, True, [{"r": "pass"}], "ci")
        m = db.compute_m11_regression_rate()
        assert m["value"] == 0.0
        assert m["numerator"] == 0


# ===========================================================================
# M12: Spec Retirement Rate
# ===========================================================================


class TestM12:
    def test_basic(self, db):
        _seed_basic(db)
        m = db.compute_m12_spec_retirement_rate()
        assert m["numerator"] == 1  # SPEC-C retired
        assert m["denominator"] == 3  # 1 retired + 2 active (SPEC-A impl, SPEC-B verified)
        assert round(m["value"], 4) == 0.3333

    def test_no_specs(self, db):
        m = db.compute_m12_spec_retirement_rate()
        assert m["value"] is None
        assert m["status"] == "not_applicable"

    def test_no_retired(self, db):
        db.insert_spec(id="S1", title="T", status="specified", changed_by="t", change_reason="t")
        m = db.compute_m12_spec_retirement_rate()
        assert m["value"] == 0.0
        assert m["numerator"] == 0


# ===========================================================================
# M16: Verified-With-Passing-Tests Rate
# ===========================================================================


class TestM16:
    def test_basic(self, db):
        _seed_basic(db)
        m = db.compute_m16_verified_with_passing_tests_rate()
        assert m["denominator"] == 1  # SPEC-B is verified
        assert m["numerator"] == 1  # TEST-1 passes with test_file
        assert m["value"] == 1.0

    def test_verified_without_tests(self, db):
        db.insert_spec(id="S-V", title="V", status="specified", changed_by="t", change_reason="v1")
        db.update_spec("S-V", changed_by="t", change_reason="impl", status="implemented")
        db.update_spec("S-V", changed_by="t", change_reason="verify", status="verified")
        m = db.compute_m16_verified_with_passing_tests_rate()
        assert m["value"] == 0.0
        assert m["numerator"] == 0

    def test_verified_with_failing_test(self, db):
        db.insert_spec(id="S-VF", title="VF", status="specified", changed_by="t", change_reason="v1")
        db.update_spec("S-VF", changed_by="t", change_reason="v", status="verified")
        db.insert_test(
            id="T-FAIL",
            title="F",
            spec_id="S-VF",
            test_type="unit",
            expected_outcome="pass",
            test_file="tests/f.py",
            last_result="fail",
            last_executed_at="2026-04-10T00:00:00+00:00",
            changed_by="t",
            change_reason="t",
        )
        m = db.compute_m16_verified_with_passing_tests_rate()
        assert m["numerator"] == 0

    def test_verified_with_null_test_file(self, db):
        """test_file=None means no executable evidence."""
        db.insert_spec(id="S-VN", title="VN", status="specified", changed_by="t", change_reason="v1")
        db.update_spec("S-VN", changed_by="t", change_reason="v", status="verified")
        db.insert_test(
            id="T-NOFILE",
            title="NF",
            spec_id="S-VN",
            test_type="unit",
            expected_outcome="pass",
            test_file=None,
            last_result="pass",
            last_executed_at="2026-04-10T00:00:00+00:00",
            changed_by="t",
            change_reason="t",
        )
        m = db.compute_m16_verified_with_passing_tests_rate()
        assert m["numerator"] == 0

    def test_no_verified_specs(self, db):
        db.insert_spec(id="S-I", title="I", status="implemented", changed_by="t", change_reason="t")
        m = db.compute_m16_verified_with_passing_tests_rate()
        assert m["value"] is None


# ===========================================================================
# M17: Stale Test Ratio
# ===========================================================================


class TestM17:
    def test_basic_not_stale(self, db):
        db.insert_spec(id="S1", title="T", status="specified", changed_by="t", change_reason="t")
        db.insert_test(
            id="T-FRESH",
            title="Fresh",
            spec_id="S1",
            test_type="unit",
            expected_outcome="pass",
            last_result="pass",
            last_executed_at="2026-04-10T00:00:00+00:00",
            changed_by="t",
            change_reason="t",
        )
        m = db.compute_m17_stale_test_ratio(now="2026-04-11T00:00:00+00:00")
        assert m["value"] == 0.0

    def test_stale_test(self, db):
        db.insert_spec(id="S1", title="T", status="specified", changed_by="t", change_reason="t")
        db.insert_test(
            id="T-OLD",
            title="Old",
            spec_id="S1",
            test_type="unit",
            expected_outcome="pass",
            last_result="pass",
            last_executed_at="2026-01-01T00:00:00+00:00",
            changed_by="t",
            change_reason="t",
        )
        m = db.compute_m17_stale_test_ratio(now="2026-04-11T00:00:00+00:00")
        assert m["value"] == 1.0
        assert m["numerator"] == 1

    def test_null_executed_at_is_stale(self, db):
        db.insert_spec(id="S1", title="T", status="specified", changed_by="t", change_reason="t")
        db.insert_test(
            id="T-NULL",
            title="Null",
            spec_id="S1",
            test_type="unit",
            expected_outcome="pass",
            changed_by="t",
            change_reason="t",
        )
        m = db.compute_m17_stale_test_ratio(now="2026-04-11T00:00:00+00:00")
        assert m["value"] == 1.0

    def test_empty_db(self, db):
        m = db.compute_m17_stale_test_ratio()
        assert m["value"] is None


# ===========================================================================
# M18: Implemented-Without-Test Count
# ===========================================================================


class TestM18:
    def test_basic(self, db):
        _seed_basic(db)
        m = db.compute_m18_implemented_without_test_count()
        # SPEC-A is implemented without tests, SPEC-B has TEST-1
        assert m["value"] == 1
        assert "SPEC-A" in m["spec_ids"]

    def test_all_have_tests(self, db):
        db.insert_spec(id="S1", title="T", status="implemented", changed_by="t", change_reason="t")
        db.insert_test(
            id="T1",
            title="T",
            spec_id="S1",
            test_type="unit",
            expected_outcome="pass",
            changed_by="t",
            change_reason="t",
        )
        m = db.compute_m18_implemented_without_test_count()
        assert m["value"] == 0

    def test_empty_db(self, db):
        m = db.compute_m18_implemented_without_test_count()
        assert m["value"] == 0
        assert m["denominator"] == 0


# ===========================================================================
# get_lifecycle_metrics integration
# ===========================================================================


class TestGetLifecycleMetrics:
    def test_returns_all_phase1_metrics(self, db):
        _seed_basic(db)
        metrics = db.get_lifecycle_metrics()
        expected_keys = {"M2", "M4", "M6", "M10", "M11", "M12", "M16", "M17", "M18"}
        assert set(metrics.keys()) == expected_keys

    def test_empty_db_all_not_applicable(self, db):
        metrics = db.get_lifecycle_metrics()
        for mid, val in metrics.items():
            if mid == "M18":
                assert val["value"] == 0  # Count metric, not ratio
            else:
                assert val["value"] is None, f"{mid} should be None on empty DB"
