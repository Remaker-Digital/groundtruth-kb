"""Tests for Knowledge Database artifact system (S113).

Verifies the 5 new artifact tables (tests, test_plans, test_plan_phases,
work_items, backlog_snapshots), the type column on specifications, and
all associated API methods.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import tempfile

import pytest

# Allow import from tools directory
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools", "knowledge-db"))

from db import KnowledgeDB


@pytest.fixture
def db():
    """Create a fresh temporary database for each test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database = KnowledgeDB(path)
    yield database
    database.close()
    os.unlink(path)


# ------------------------------------------------------------------
# Schema existence
# ------------------------------------------------------------------

class TestSchemaExists:
    """Verify all expected tables, views, and indexes exist."""

    def test_all_14_tables_exist(self, db):
        conn = db._get_conn()
        tables = sorted(
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"
            ).fetchall()
        )
        expected = sorted([
            "assertion_runs", "backlog_snapshots", "documents",
            "environment_config", "operational_procedures", "session_prompts",
            "specifications", "test_coverage", "test_plan_phases", "test_plans",
            "test_procedures", "testable_elements", "tests", "work_items",
        ])
        assert tables == expected

    def test_all_11_views_exist(self, db):
        conn = db._get_conn()
        views = sorted(
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='view'"
            ).fetchall()
        )
        expected = sorted([
            "current_backlog_snapshots", "current_documents",
            "current_environment_config", "current_operational_procedures",
            "current_specifications", "current_testable_elements",
            "current_test_plan_phases", "current_test_plans",
            "current_test_procedures", "current_tests", "current_work_items",
        ])
        assert views == expected

    def test_specifications_has_type_column(self, db):
        conn = db._get_conn()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(specifications)").fetchall()}
        assert "type" in cols


# ------------------------------------------------------------------
# Tests artifact
# ------------------------------------------------------------------

class TestTestsArtifact:
    """Verify the tests table and API methods."""

    def _seed_spec(self, db):
        return db.insert_spec("SPEC-T1", "Test spec", "specified", "test", "seed")

    def test_insert_test(self, db):
        self._seed_spec(db)
        t = db.insert_test(
            "TEST-0001", "Verify auth returns 200", "SPEC-T1", "unit",
            "API returns HTTP 200 with valid auth token",
            "test", "initial creation",
            test_file="tests/test_auth.py",
            test_function="test_auth_returns_200",
            description="Sends valid token, expects 200",
        )
        assert t["id"] == "TEST-0001"
        assert t["version"] == 1
        assert t["spec_id"] == "SPEC-T1"
        assert t["test_type"] == "unit"
        assert t["expected_outcome"] == "API returns HTTP 200 with valid auth token"
        assert t["last_result"] is None

    def test_update_test_creates_new_version(self, db):
        self._seed_spec(db)
        db.insert_test("TEST-0001", "Original", "SPEC-T1", "unit", "Pass condition", "test", "create")
        updated = db.update_test("TEST-0001", "test", "updated description",
                                 description="Improved test", last_result="PASS")
        assert updated["version"] == 2
        assert updated["description"] == "Improved test"
        assert updated["last_result"] == "PASS"
        assert updated["title"] == "Original"  # carried forward

    def test_get_test_returns_latest_version(self, db):
        self._seed_spec(db)
        db.insert_test("TEST-0001", "v1", "SPEC-T1", "unit", "outcome", "test", "v1")
        db.update_test("TEST-0001", "test", "v2", title="v2 title")
        t = db.get_test("TEST-0001")
        assert t["version"] == 2
        assert t["title"] == "v2 title"

    def test_get_test_history(self, db):
        self._seed_spec(db)
        db.insert_test("TEST-0001", "v1", "SPEC-T1", "unit", "outcome", "test", "v1")
        db.update_test("TEST-0001", "test", "v2", title="v2")
        db.update_test("TEST-0001", "test", "v3", title="v3")
        history = db.get_test_history("TEST-0001")
        assert len(history) == 3
        assert history[0]["version"] == 3  # newest first
        assert history[2]["version"] == 1

    def test_list_tests_by_spec(self, db):
        self._seed_spec(db)
        db.insert_spec("SPEC-T2", "Another spec", "specified", "test", "seed")
        db.insert_test("TEST-0001", "Test A", "SPEC-T1", "unit", "pass", "test", "create")
        db.insert_test("TEST-0002", "Test B", "SPEC-T1", "e2e", "pass", "test", "create")
        db.insert_test("TEST-0003", "Test C", "SPEC-T2", "unit", "pass", "test", "create")
        tests = db.list_tests(spec_id="SPEC-T1")
        assert len(tests) == 2
        assert {t["id"] for t in tests} == {"TEST-0001", "TEST-0002"}

    def test_list_tests_by_type(self, db):
        self._seed_spec(db)
        db.insert_test("TEST-0001", "Unit", "SPEC-T1", "unit", "pass", "test", "create")
        db.insert_test("TEST-0002", "E2E", "SPEC-T1", "e2e", "pass", "test", "create")
        tests = db.list_tests(test_type="e2e")
        assert len(tests) == 1
        assert tests[0]["id"] == "TEST-0002"

    def test_list_tests_by_result(self, db):
        self._seed_spec(db)
        db.insert_test("TEST-0001", "Pass", "SPEC-T1", "unit", "pass", "test", "create",
                        last_result="PASS")
        db.insert_test("TEST-0002", "Fail", "SPEC-T1", "unit", "pass", "test", "create",
                        last_result="FAIL")
        tests = db.list_tests(last_result="FAIL")
        assert len(tests) == 1
        assert tests[0]["id"] == "TEST-0002"

    def test_get_tests_for_spec(self, db):
        self._seed_spec(db)
        db.insert_test("TEST-0001", "Test A", "SPEC-T1", "unit", "pass", "test", "create")
        db.insert_test("TEST-0002", "Test B", "SPEC-T1", "e2e", "pass", "test", "create")
        tests = db.get_tests_for_spec("SPEC-T1")
        assert len(tests) == 2

    def test_get_untested_specs(self, db):
        db.insert_spec("SPEC-T1", "Tested", "specified", "test", "seed")
        db.insert_spec("SPEC-T2", "Untested", "specified", "test", "seed")
        db.insert_test("TEST-0001", "Test A", "SPEC-T1", "unit", "pass", "test", "create")
        untested = db.get_untested_specs()
        ids = [s["id"] for s in untested]
        assert "SPEC-T2" in ids
        assert "SPEC-T1" not in ids

    def test_get_nonexistent_test(self, db):
        assert db.get_test("NONEXISTENT") is None

    def test_update_nonexistent_test_raises(self, db):
        with pytest.raises(ValueError, match="not found"):
            db.update_test("NONEXISTENT", "test", "reason")


# ------------------------------------------------------------------
# Test Plans artifact
# ------------------------------------------------------------------

class TestTestPlansArtifact:
    """Verify the test_plans table and API methods."""

    def test_insert_test_plan(self, db):
        tp = db.insert_test_plan("TP-1.0", "1.0 GA Release", "draft", "test", "create",
                                  description="16-phase test plan")
        assert tp["id"] == "TP-1.0"
        assert tp["version"] == 1
        assert tp["status"] == "draft"
        assert tp["description"] == "16-phase test plan"

    def test_update_test_plan(self, db):
        db.insert_test_plan("TP-1.0", "1.0 GA Release", "draft", "test", "create")
        updated = db.update_test_plan("TP-1.0", "test", "activate", status="active")
        assert updated["version"] == 2
        assert updated["status"] == "active"
        assert updated["title"] == "1.0 GA Release"  # carried forward

    def test_get_active_test_plan(self, db):
        db.insert_test_plan("TP-0.9", "Old plan", "retired", "test", "create")
        db.insert_test_plan("TP-1.0", "Current", "active", "test", "create")
        active = db.get_active_test_plan()
        assert active is not None
        assert active["id"] == "TP-1.0"

    def test_get_active_test_plan_none(self, db):
        db.insert_test_plan("TP-1.0", "Draft", "draft", "test", "create")
        assert db.get_active_test_plan() is None

    def test_list_test_plans_by_status(self, db):
        db.insert_test_plan("TP-0.9", "Old", "retired", "test", "create")
        db.insert_test_plan("TP-1.0", "Current", "active", "test", "create")
        db.insert_test_plan("TP-2.0", "Next", "draft", "test", "create")
        active = db.list_test_plans(status="active")
        assert len(active) == 1
        all_plans = db.list_test_plans()
        assert len(all_plans) == 3


# ------------------------------------------------------------------
# Test Plan Phases artifact
# ------------------------------------------------------------------

class TestTestPlanPhasesArtifact:
    """Verify the test_plan_phases table and API methods."""

    def _seed_plan(self, db):
        return db.insert_test_plan("TP-1.0", "GA Plan", "active", "test", "seed")

    def test_insert_phase(self, db):
        self._seed_plan(db)
        ph = db.insert_test_plan_phase(
            "TP-1.0-PH-01", "TP-1.0", 1, "Pre-flight",
            "All 4 checks pass", "test", "create",
            test_ids=["TEST-0001", "TEST-0002"],
            description="Verify environment readiness",
        )
        assert ph["id"] == "TP-1.0-PH-01"
        assert ph["plan_id"] == "TP-1.0"
        assert ph["phase_order"] == 1
        assert ph["gate_criteria"] == "All 4 checks pass"
        assert ph["test_ids_parsed"] == ["TEST-0001", "TEST-0002"]

    def test_update_phase(self, db):
        self._seed_plan(db)
        db.insert_test_plan_phase("TP-1.0-PH-01", "TP-1.0", 1, "Pre-flight",
                                   "All checks pass", "test", "create")
        updated = db.update_test_plan_phase("TP-1.0-PH-01", "test", "record result",
                                             last_result="PASS")
        assert updated["version"] == 2
        assert updated["last_result"] == "PASS"
        assert updated["title"] == "Pre-flight"  # carried forward

    def test_list_phases_ordered(self, db):
        self._seed_plan(db)
        db.insert_test_plan_phase("TP-1.0-PH-03", "TP-1.0", 3, "Phase 3", "gate", "test", "create")
        db.insert_test_plan_phase("TP-1.0-PH-01", "TP-1.0", 1, "Phase 1", "gate", "test", "create")
        db.insert_test_plan_phase("TP-1.0-PH-02", "TP-1.0", 2, "Phase 2", "gate", "test", "create")
        phases = db.list_test_plan_phases("TP-1.0")
        assert len(phases) == 3
        assert [p["phase_order"] for p in phases] == [1, 2, 3]

    def test_phase_test_ids_json_roundtrip(self, db):
        self._seed_plan(db)
        ids = ["TEST-0001", "TEST-0002", "TEST-0003"]
        ph = db.insert_test_plan_phase("TP-1.0-PH-01", "TP-1.0", 1, "Phase", "gate",
                                        "test", "create", test_ids=ids)
        assert ph["test_ids_parsed"] == ids


# ------------------------------------------------------------------
# Work Items artifact
# ------------------------------------------------------------------

class TestWorkItemsArtifact:
    """Verify the work_items table and API methods."""

    def test_insert_work_item_defect(self, db):
        wi = db.insert_work_item(
            "WI-0001", "Auth returns 401 for valid token", "defect",
            "tenant_administration", "open", "test", "test failure",
            source_spec_id="SPEC-0100", source_test_id="TEST-0050",
            failure_description="Expected 200, got 401", priority="P1",
        )
        assert wi["id"] == "WI-0001"
        assert wi["origin"] == "defect"
        assert wi["component"] == "tenant_administration"
        assert wi["resolution_status"] == "open"
        assert wi["source_spec_id"] == "SPEC-0100"
        assert wi["failure_description"] == "Expected 200, got 401"

    def test_insert_work_item_regression(self, db):
        wi = db.insert_work_item(
            "WI-0002", "Dashboard chart broke after v1.60", "regression",
            "tenant_administration", "open", "test", "regression detected",
            source_spec_id="SPEC-0200", source_test_id="TEST-0100",
            failure_description="Chart renders blank",
        )
        assert wi["origin"] == "regression"

    def test_insert_work_item_new(self, db):
        wi = db.insert_work_item(
            "WI-0003", "Implement Stripe billing", "new",
            "external_integration", "open", "test", "new feature",
            source_spec_id="SPEC-0300",
        )
        assert wi["origin"] == "new"
        assert wi["source_test_id"] is None
        assert wi["failure_description"] is None

    def test_update_work_item_resolution(self, db):
        db.insert_work_item("WI-0001", "Bug", "defect", "database", "open", "test", "create")
        updated = db.update_work_item("WI-0001", "test", "started fix",
                                       resolution_status="in_progress")
        assert updated["version"] == 2
        assert updated["resolution_status"] == "in_progress"
        resolved = db.update_work_item("WI-0001", "test", "fix applied",
                                        resolution_status="resolved")
        assert resolved["version"] == 3
        verified = db.update_work_item("WI-0001", "test", "confirmed in test plan",
                                        resolution_status="verified")
        assert verified["version"] == 4
        assert verified["resolution_status"] == "verified"

    def test_list_work_items_by_origin(self, db):
        db.insert_work_item("WI-0001", "Defect", "defect", "database", "open", "test", "create")
        db.insert_work_item("WI-0002", "New", "new", "database", "open", "test", "create")
        db.insert_work_item("WI-0003", "Regression", "regression", "database", "open", "test", "create")
        defects = db.list_work_items(origin="defect")
        assert len(defects) == 1
        assert defects[0]["id"] == "WI-0001"

    def test_list_work_items_by_component(self, db):
        db.insert_work_item("WI-0001", "DB bug", "defect", "database", "open", "test", "create")
        db.insert_work_item("WI-0002", "UI bug", "defect", "customer_interface", "open", "test", "create")
        db_items = db.list_work_items(component="database")
        assert len(db_items) == 1

    def test_list_work_items_by_status(self, db):
        db.insert_work_item("WI-0001", "Open", "new", "database", "open", "test", "create")
        db.insert_work_item("WI-0002", "Done", "new", "database", "verified", "test", "create")
        open_items = db.list_work_items(resolution_status="open")
        assert len(open_items) == 1
        assert open_items[0]["id"] == "WI-0001"

    def test_get_open_work_items_excludes_verified(self, db):
        db.insert_work_item("WI-0001", "Open", "new", "database", "open", "test", "create")
        db.insert_work_item("WI-0002", "In progress", "defect", "database", "in_progress", "test", "create")
        db.insert_work_item("WI-0003", "Verified", "defect", "database", "verified", "test", "create")
        open_items = db.get_open_work_items()
        ids = [wi["id"] for wi in open_items]
        assert "WI-0001" in ids
        assert "WI-0002" in ids
        assert "WI-0003" not in ids

    def test_get_work_item_history(self, db):
        db.insert_work_item("WI-0001", "Bug", "defect", "database", "open", "test", "create")
        db.update_work_item("WI-0001", "test", "fix", resolution_status="resolved")
        db.update_work_item("WI-0001", "test", "verify", resolution_status="verified")
        history = db.get_work_item_history("WI-0001")
        assert len(history) == 3
        assert history[0]["resolution_status"] == "verified"
        assert history[2]["resolution_status"] == "open"


# ------------------------------------------------------------------
# Backlog Snapshots artifact
# ------------------------------------------------------------------

class TestBacklogSnapshotsArtifact:
    """Verify the backlog_snapshots table and API methods."""

    def test_insert_backlog_snapshot(self, db):
        bl = db.insert_backlog_snapshot(
            "BL-S113-start", "S113 start backlog",
            ["WI-0001", "WI-0002", "WI-0003"],
            "test", "snapshot",
            summary_by_origin={"defect": 2, "new": 1},
            summary_by_component={"database": 2, "customer_interface": 1},
        )
        assert bl["id"] == "BL-S113-start"
        assert bl["work_item_ids_parsed"] == ["WI-0001", "WI-0002", "WI-0003"]
        assert bl["summary_by_origin_parsed"] == {"defect": 2, "new": 1}

    def test_create_backlog_snapshot_from_current(self, db):
        db.insert_work_item("WI-0001", "Bug A", "defect", "database", "open", "test", "create", priority="P1")
        db.insert_work_item("WI-0002", "Feature B", "new", "customer_interface", "open", "test", "create", priority="P2")
        db.insert_work_item("WI-0003", "Done C", "defect", "database", "verified", "test", "create")
        bl = db.create_backlog_snapshot_from_current("BL-S113", "test", "auto-snapshot")
        ids = bl["work_item_ids_parsed"]
        # Only open items (WI-0001, WI-0002), not verified (WI-0003)
        assert "WI-0001" in ids
        assert "WI-0002" in ids
        assert "WI-0003" not in ids
        assert bl["summary_by_origin_parsed"]["defect"] == 1
        assert bl["summary_by_origin_parsed"]["new"] == 1
        assert bl["summary_by_component_parsed"]["database"] == 1
        assert bl["summary_by_component_parsed"]["customer_interface"] == 1

    def test_list_backlog_snapshots(self, db):
        db.insert_backlog_snapshot("BL-S110", "S110", [], "test", "create")
        db.insert_backlog_snapshot("BL-S111", "S111", [], "test", "create")
        db.insert_backlog_snapshot("BL-S112", "S112", [], "test", "create")
        snapshots = db.list_backlog_snapshots(limit=2)
        assert len(snapshots) == 2

    def test_empty_backlog_snapshot(self, db):
        bl = db.create_backlog_snapshot_from_current("BL-EMPTY", "test", "no items")
        assert bl["work_item_ids_parsed"] == []


# ------------------------------------------------------------------
# Specifications type column
# ------------------------------------------------------------------

class TestSpecificationsTypeColumn:
    """Verify the type column on specifications."""

    def test_default_type_is_requirement(self, db):
        s = db.insert_spec("SPEC-T1", "A requirement", "specified", "test", "create")
        assert s["type"] == "requirement"

    def test_explicit_governance_type(self, db):
        s = db.insert_spec("GOV-99", "A governance rule", "specified", "test", "create",
                           type="governance")
        assert s["type"] == "governance"

    def test_explicit_protected_behavior_type(self, db):
        s = db.insert_spec("PB-099", "A protected behavior", "specified", "test", "create",
                           type="protected_behavior")
        assert s["type"] == "protected_behavior"

    def test_update_preserves_type(self, db):
        db.insert_spec("GOV-99", "Gov rule", "specified", "test", "create", type="governance")
        updated = db.update_spec("GOV-99", "test", "update title", title="Updated gov rule")
        assert updated["type"] == "governance"

    def test_list_specs_can_filter_by_type_via_search(self, db):
        db.insert_spec("SPEC-T1", "Req", "specified", "test", "create", type="requirement")
        db.insert_spec("GOV-T1", "Gov", "specified", "test", "create", type="governance")
        # Direct SQL since list_specs doesn't have type filter yet
        conn = db._get_conn()
        govs = conn.execute(
            "SELECT * FROM current_specifications WHERE type = 'governance'"
        ).fetchall()
        assert len(govs) == 1
        assert govs[0]["id"] == "GOV-T1"


# ------------------------------------------------------------------
# Summary stats include new artifacts
# ------------------------------------------------------------------

class TestSummaryStats:
    """Verify get_summary() includes new artifact counts."""

    def test_summary_includes_new_artifact_keys(self, db):
        summary = db.get_summary()
        assert "test_artifact_count" in summary
        assert "test_plan_count" in summary
        assert "test_plan_phase_count" in summary
        assert "work_item_counts" in summary
        assert "work_item_total" in summary
        assert "backlog_snapshot_count" in summary

    def test_summary_counts_work_items_by_status(self, db):
        db.insert_work_item("WI-0001", "A", "new", "database", "open", "test", "create")
        db.insert_work_item("WI-0002", "B", "defect", "database", "resolved", "test", "create")
        summary = db.get_summary()
        assert summary["work_item_counts"]["open"] == 1
        assert summary["work_item_counts"]["resolved"] == 1
        assert summary["work_item_total"] == 2


# ------------------------------------------------------------------
# Global history includes new tables
# ------------------------------------------------------------------

class TestGlobalHistory:
    """Verify get_history() includes changes from new tables."""

    def test_history_includes_tests(self, db):
        db.insert_spec("SPEC-T1", "Spec", "specified", "test", "seed")
        db.insert_test("TEST-0001", "Test", "SPEC-T1", "unit", "pass", "test", "create")
        history = db.get_history(table="tests")
        assert len(history) == 1
        assert history[0]["record_id"] == "TEST-0001"

    def test_history_includes_work_items(self, db):
        db.insert_work_item("WI-0001", "Item", "new", "database", "open", "test", "create")
        history = db.get_history(table="work_items")
        assert len(history) == 1

    def test_history_includes_all_new_tables(self, db):
        db.insert_spec("SPEC-T1", "Spec", "specified", "test", "seed")
        db.insert_test("TEST-0001", "Test", "SPEC-T1", "unit", "pass", "test", "create")
        db.insert_test_plan("TP-1.0", "Plan", "draft", "test", "create")
        db.insert_test_plan_phase("TP-1.0-PH-01", "TP-1.0", 1, "Phase", "gate", "test", "create")
        db.insert_work_item("WI-0001", "Item", "new", "database", "open", "test", "create")
        db.insert_backlog_snapshot("BL-1", "Snap", [], "test", "create")
        history = db.get_history(limit=100)
        table_names = {h["table_name"] for h in history}
        assert "tests" in table_names
        assert "test_plans" in table_names
        assert "test_plan_phases" in table_names
        assert "work_items" in table_names
        assert "backlog_snapshots" in table_names


# ------------------------------------------------------------------
# Export includes new tables
# ------------------------------------------------------------------

class TestExportJson:
    """Verify export_json() includes new tables."""

    def test_export_includes_new_tables(self, db):
        db.insert_spec("SPEC-T1", "Spec", "specified", "test", "seed")
        db.insert_test("TEST-0001", "Test", "SPEC-T1", "unit", "pass", "test", "create")
        db.insert_work_item("WI-0001", "Item", "new", "database", "open", "test", "create")

        fd, export_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            db.export_json(export_path)
            with open(export_path) as f:
                data = json.load(f)
            assert "tests" in data["tables"]
            assert "test_plans" in data["tables"]
            assert "test_plan_phases" in data["tables"]
            assert "work_items" in data["tables"]
            assert "backlog_snapshots" in data["tables"]
            assert len(data["tables"]["tests"]) == 1
            assert len(data["tables"]["work_items"]) == 1
        finally:
            os.unlink(export_path)


# ------------------------------------------------------------------
# Append-only invariant
# ------------------------------------------------------------------

class TestAppendOnlyInvariant:
    """Verify that updates create new versions, never modifying existing rows."""

    def test_test_update_preserves_all_versions(self, db):
        db.insert_spec("SPEC-T1", "Spec", "specified", "test", "seed")
        db.insert_test("TEST-0001", "v1", "SPEC-T1", "unit", "outcome", "test", "v1")
        db.update_test("TEST-0001", "test", "v2", title="v2")
        db.update_test("TEST-0001", "test", "v3", title="v3")
        conn = db._get_conn()
        total_rows = conn.execute("SELECT COUNT(*) FROM tests WHERE id = 'TEST-0001'").fetchone()[0]
        assert total_rows == 3

    def test_work_item_update_preserves_all_versions(self, db):
        db.insert_work_item("WI-0001", "Bug", "defect", "database", "open", "test", "v1")
        db.update_work_item("WI-0001", "test", "v2", resolution_status="resolved")
        conn = db._get_conn()
        total_rows = conn.execute("SELECT COUNT(*) FROM work_items WHERE id = 'WI-0001'").fetchone()[0]
        assert total_rows == 2
