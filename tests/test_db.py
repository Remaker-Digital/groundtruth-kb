"""Tests for KnowledgeDB core CRUD and versioning."""

from __future__ import annotations

import pytest

from groundtruth_kb.db import KnowledgeDB, get_depth, get_parent_id, spec_sort_key
from groundtruth_kb.gates import GateRegistry


@pytest.fixture
def db(tmp_path) -> KnowledgeDB:
    """Create a fresh in-memory-like DB in a temp directory."""
    db_path = tmp_path / "test.db"
    registry = GateRegistry.from_config([], include_builtins=True)
    return KnowledgeDB(db_path=db_path, gate_registry=registry)


@pytest.fixture
def db_no_gates(tmp_path) -> KnowledgeDB:
    """DB without any gates for testing raw behavior."""
    db_path = tmp_path / "test_nogates.db"
    return KnowledgeDB(db_path=db_path)


class TestSpecifications:
    """Tests for specification CRUD."""

    def test_insert_and_get(self, db):
        result = db.insert_spec(
            id="SPEC-001",
            title="Test Specification",
            status="specified",
            changed_by="test",
            change_reason="initial creation",
        )
        assert result["id"] == "SPEC-001"
        assert result["title"] == "Test Specification"
        assert result["status"] == "specified"
        assert result["version"] == 1

    def test_update_creates_new_version(self, db):
        db.insert_spec(
            id="SPEC-001", title="Original", status="specified",
            changed_by="test", change_reason="create",
        )
        result = db.update_spec(
            id="SPEC-001", changed_by="test", change_reason="update title",
            title="Updated Title",
        )
        assert result["version"] == 2
        assert result["title"] == "Updated Title"

    def test_get_returns_latest_version(self, db):
        db.insert_spec(
            id="SPEC-001", title="V1", status="specified",
            changed_by="test", change_reason="v1",
        )
        db.update_spec(
            id="SPEC-001", changed_by="test", change_reason="v2",
            title="V2",
        )
        result = db.get_spec("SPEC-001")
        assert result["title"] == "V2"
        assert result["version"] == 2

    def test_get_nonexistent_returns_none(self, db):
        assert db.get_spec("SPEC-MISSING") is None

    def test_history_returns_all_versions(self, db):
        db.insert_spec(
            id="SPEC-001", title="V1", status="specified",
            changed_by="test", change_reason="v1",
        )
        db.update_spec(
            id="SPEC-001", changed_by="test", change_reason="v2",
            title="V2",
        )
        history = db.get_spec_history("SPEC-001")
        assert len(history) == 2
        assert history[0]["version"] == 2  # newest first
        assert history[1]["version"] == 1

    def test_list_specs_filter_by_status(self, db):
        db.insert_spec(
            id="SPEC-001", title="Specified", status="specified",
            changed_by="test", change_reason="create",
        )
        db.insert_spec(
            id="SPEC-002", title="Implemented", status="implemented",
            changed_by="test", change_reason="create",
        )
        specs = db.list_specs(status="specified")
        assert len(specs) == 1
        assert specs[0]["id"] == "SPEC-001"

    def test_auto_detect_spec_type(self, db):
        db.insert_spec(
            id="GOV-01", title="Governance Rule", status="specified",
            changed_by="test", change_reason="create",
        )
        spec = db.get_spec("GOV-01")
        assert spec["type"] == "governance"

    def test_tags_stored_as_json(self, db):
        db.insert_spec(
            id="SPEC-001", title="Tagged", status="specified",
            changed_by="test", change_reason="create",
            tags=["alpha", "beta"],
        )
        spec = db.get_spec("SPEC-001")
        # Tags are stored as JSON string in the DB
        import json
        tags = json.loads(spec["tags"]) if isinstance(spec["tags"], str) else spec["tags"]
        assert tags == ["alpha", "beta"]


class TestVersioning:
    """Tests for append-only versioning behavior."""

    def test_unique_id_version_constraint(self, db):
        db.insert_spec(
            id="SPEC-001", title="V1", status="specified",
            changed_by="test", change_reason="v1",
        )
        # Second insert with same ID should get version 2, not conflict
        result = db.insert_spec(
            id="SPEC-001", title="V2 via insert", status="specified",
            changed_by="test", change_reason="v2",
        )
        assert result["version"] == 2


class TestWorkItems:
    """Tests for work item CRUD."""

    def test_insert_work_item(self, db):
        result = db.insert_work_item(
            id="WI-001", title="Fix bug", origin="defect",
            component="core", resolution_status="open",
            changed_by="test", change_reason="found bug",
        )
        assert result["id"] == "WI-001"
        assert result["origin"] == "defect"
        assert result["stage"] == "created"

    def test_list_open_work_items(self, db):
        db.insert_work_item(
            id="WI-001", title="Open", origin="new",
            component="core", resolution_status="open",
            changed_by="test", change_reason="create",
        )
        db.insert_work_item(
            id="WI-002", title="Resolved", origin="new",
            component="core", resolution_status="resolved",
            changed_by="test", change_reason="create",
            stage="resolved",
        )
        open_wis = db.get_open_work_items()
        open_ids = [wi["id"] for wi in open_wis]
        assert "WI-001" in open_ids


class TestTests:
    """Tests for test artifact CRUD."""

    def test_insert_test(self, db):
        db.insert_spec(
            id="SPEC-001", title="Target Spec", status="specified",
            changed_by="test", change_reason="create",
        )
        result = db.insert_test(
            id="TEST-001", title="Test Case", spec_id="SPEC-001",
            test_type="unit", expected_outcome="Should pass",
            changed_by="test", change_reason="create",
        )
        assert result["id"] == "TEST-001"
        assert result["spec_id"] == "SPEC-001"

    def test_get_tests_for_spec(self, db):
        db.insert_spec(
            id="SPEC-001", title="Target", status="specified",
            changed_by="test", change_reason="create",
        )
        db.insert_test(
            id="TEST-001", title="Test 1", spec_id="SPEC-001",
            test_type="unit", expected_outcome="Pass",
            changed_by="test", change_reason="create",
        )
        tests = db.get_tests_for_spec("SPEC-001")
        assert len(tests) == 1


class TestDocuments:
    """Tests for document CRUD."""

    def test_insert_and_get_document(self, db):
        result = db.insert_document(
            id="DOC-001", title="Architecture Doc", category="architecture",
            status="active", changed_by="test", change_reason="create",
            content="Some content",
        )
        assert result["id"] == "DOC-001"
        assert result["category"] == "architecture"


class TestGateIntegration:
    """Tests for governance gate integration with KnowledgeDB."""

    def test_adr_gate_blocks_promotion_without_assertions(self, db):
        db.insert_spec(
            id="ADR-001", title="Architecture Decision", status="specified",
            changed_by="test", change_reason="create",
        )
        with pytest.raises(Exception, match="non-empty assertions"):
            db.update_spec(
                id="ADR-001", changed_by="test", change_reason="promote",
                status="implemented",
            )

    def test_no_gate_registry_allows_all(self, db_no_gates):
        # Without a gate registry, no enforcement
        db_no_gates.insert_spec(
            id="ADR-001", title="Architecture Decision", status="implemented",
            changed_by="test", change_reason="create",
        )
        spec = db_no_gates.get_spec("ADR-001")
        assert spec["status"] == "implemented"


class TestHelpers:
    """Tests for spec_sort_key, get_depth, get_parent_id."""

    def test_sort_key_numeric(self):
        assert spec_sort_key("245") == (1, 245)
        assert spec_sort_key("245.2") == (1, 245, 2)
        assert spec_sort_key("245.10") == (1, 245, 10)

    def test_sort_key_prefix(self):
        assert spec_sort_key("PB-001") == (0, "PB-001")

    def test_sort_order(self):
        ids = ["245.10", "245.2", "PB-001", "100"]
        sorted_ids = sorted(ids, key=spec_sort_key)
        assert sorted_ids == ["PB-001", "100", "245.2", "245.10"]

    def test_get_depth(self):
        assert get_depth("245") == 0
        assert get_depth("245.1") == 1
        assert get_depth("245.1.3") == 2

    def test_get_parent_id(self):
        assert get_parent_id("245") is None
        assert get_parent_id("245.1") == "245"
        assert get_parent_id("245.1.3") == "245.1"


class TestSummaryAndExport:
    """Tests for summary and export functionality."""

    def test_get_summary(self, db):
        db.insert_spec(
            id="SPEC-001", title="Test", status="specified",
            changed_by="test", change_reason="create",
        )
        summary = db.get_summary()
        assert summary["spec_total"] >= 1

    def test_export_json(self, db, tmp_path):
        db.insert_spec(
            id="SPEC-001", title="Export Test", status="specified",
            changed_by="test", change_reason="create",
        )
        output_path = tmp_path / "export.json"
        db.export_json(str(output_path))
        assert output_path.exists()
        import json
        data = json.loads(output_path.read_text())
        assert "tables" in data
        assert "specifications" in data["tables"]


class TestSchema:
    """Tests for schema creation and migration."""

    def test_fresh_db_creates_all_tables(self, tmp_path):
        db_path = tmp_path / "fresh.db"
        db = KnowledgeDB(db_path=db_path)
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        tables = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        expected = {
            "specifications", "test_procedures", "operational_procedures",
            "assertion_runs", "session_prompts", "environment_config",
            "documents", "test_coverage", "tests", "test_plans",
            "test_plan_phases", "work_items", "backlog_snapshots",
            "testable_elements", "quality_scores",
        }
        assert expected.issubset(tables)
        conn.close()
        db.close()

    def test_views_created(self, tmp_path):
        db_path = tmp_path / "views.db"
        db = KnowledgeDB(db_path=db_path)
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        views = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view'"
        ).fetchall()}
        assert "current_specifications" in views
        assert "current_work_items" in views
        conn.close()
        db.close()
