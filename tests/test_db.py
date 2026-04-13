"""Tests for KnowledgeDB core CRUD and versioning."""

from __future__ import annotations

import pytest

from groundtruth_kb.db import KnowledgeDB, get_depth, get_parent_id, spec_sort_key


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
            id="SPEC-001",
            title="Original",
            status="specified",
            changed_by="test",
            change_reason="create",
        )
        result = db.update_spec(
            id="SPEC-001",
            changed_by="test",
            change_reason="update title",
            title="Updated Title",
        )
        assert result["version"] == 2
        assert result["title"] == "Updated Title"

    def test_get_returns_latest_version(self, db):
        db.insert_spec(
            id="SPEC-001",
            title="V1",
            status="specified",
            changed_by="test",
            change_reason="v1",
        )
        db.update_spec(
            id="SPEC-001",
            changed_by="test",
            change_reason="v2",
            title="V2",
        )
        result = db.get_spec("SPEC-001")
        assert result["title"] == "V2"
        assert result["version"] == 2

    def test_get_nonexistent_returns_none(self, db):
        assert db.get_spec("SPEC-MISSING") is None

    def test_history_returns_all_versions(self, db):
        db.insert_spec(
            id="SPEC-001",
            title="V1",
            status="specified",
            changed_by="test",
            change_reason="v1",
        )
        db.update_spec(
            id="SPEC-001",
            changed_by="test",
            change_reason="v2",
            title="V2",
        )
        history = db.get_spec_history("SPEC-001")
        assert len(history) == 2
        assert history[0]["version"] == 2  # newest first
        assert history[1]["version"] == 1

    def test_list_specs_filter_by_status(self, db):
        db.insert_spec(
            id="SPEC-001",
            title="Specified",
            status="specified",
            changed_by="test",
            change_reason="create",
        )
        db.insert_spec(
            id="SPEC-002",
            title="Implemented",
            status="implemented",
            changed_by="test",
            change_reason="create",
        )
        specs = db.list_specs(status="specified")
        assert len(specs) == 1
        assert specs[0]["id"] == "SPEC-001"

    def test_auto_detect_spec_type(self, db):
        db.insert_spec(
            id="GOV-01",
            title="Governance Rule",
            status="specified",
            changed_by="test",
            change_reason="create",
        )
        spec = db.get_spec("GOV-01")
        assert spec["type"] == "governance"

    def test_tags_stored_as_json(self, db):
        db.insert_spec(
            id="SPEC-001",
            title="Tagged",
            status="specified",
            changed_by="test",
            change_reason="create",
            tags=["alpha", "beta"],
        )
        spec = db.get_spec("SPEC-001")
        # Tags are stored as JSON string in the DB
        import json

        tags = json.loads(spec["tags"]) if isinstance(spec["tags"], str) else spec["tags"]
        assert tags == ["alpha", "beta"]


class TestF1SchemaEnrichment:
    """Tests for F1: Spec Schema Enrichment (authority, provisional, constraints, affected_by, testability)."""

    # --- Migration tests ---

    def test_f1_migration_fresh_db(self, db):
        """F1 columns exist after fresh init."""
        conn = db._get_conn()
        cols = {row[1] for row in conn.execute("PRAGMA table_info(specifications)").fetchall()}
        for col in ("authority", "provisional_until", "constraints", "affected_by", "testability"):
            assert col in cols, f"F1 column '{col}' missing from specifications table"

    def test_f1_migration_idempotent(self, tmp_path):
        """Double-init does not error on existing F1 columns."""
        db_path = tmp_path / "test.db"
        KnowledgeDB(db_path=db_path)  # First init
        db2 = KnowledgeDB(db_path=db_path)  # Second init — migration runs again
        cols = {row[1] for row in db2._get_conn().execute("PRAGMA table_info(specifications)").fetchall()}
        assert "authority" in cols

    # --- API compatibility ---

    def test_f1_insert_without_new_fields(self, db):
        """Pre-F1 insert call still works; authority defaults to 'stated'."""
        result = db.insert_spec(
            id="SPEC-100",
            title="Legacy",
            status="specified",
            changed_by="test",
            change_reason="compat test",
        )
        assert result["authority"] == "stated"
        assert result.get("provisional_until") is None
        assert result.get("testability") is None

    def test_f1_list_specs_without_new_filters(self, db):
        """Pre-F1 list_specs call unchanged."""
        db.insert_spec(id="SPEC-101", title="T", status="specified", changed_by="t", change_reason="t")
        specs = db.list_specs(status="specified")
        assert any(s["id"] == "SPEC-101" for s in specs)

    # --- Authority sentinel insert ---

    def test_f1_insert_omitted_authority_with_provisional(self, db):
        """Omitted authority + provisional_until auto-sets to 'provisional'."""
        result = db.insert_spec(
            id="SPEC-102",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            provisional_until="SPEC-999",
        )
        assert result["authority"] == "provisional"
        assert result["provisional_until"] == "SPEC-999"

    def test_f1_insert_stated_with_provisional_raises(self, db):
        """authority='stated' + provisional_until raises ValueError (INV-2)."""
        with pytest.raises(ValueError, match="provisional_until requires"):
            db.insert_spec(
                id="SPEC-103",
                title="T",
                status="specified",
                changed_by="test",
                change_reason="test",
                authority="stated",
                provisional_until="SPEC-999",
            )

    def test_f1_insert_explicit_none_authority(self, db):
        """Explicit authority=None stores NULL."""
        result = db.insert_spec(
            id="SPEC-104",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            authority=None,
        )
        assert result["authority"] is None

    def test_f1_insert_invalid_authority_raises(self, db):
        """Invalid authority enum raises ValueError."""
        with pytest.raises(ValueError, match="Invalid authority"):
            db.insert_spec(
                id="SPEC-105",
                title="T",
                status="specified",
                changed_by="test",
                change_reason="test",
                authority="bogus",
            )

    # --- Testability validation ---

    def test_f1_insert_valid_testability(self, db):
        """Valid testability enum accepted."""
        result = db.insert_spec(
            id="SPEC-106",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            testability="automatable",
        )
        assert result["testability"] == "automatable"

    def test_f1_insert_invalid_testability_raises(self, db):
        """Invalid testability enum raises ValueError."""
        with pytest.raises(ValueError, match="Invalid testability"):
            db.insert_spec(
                id="SPEC-107",
                title="T",
                status="specified",
                changed_by="test",
                change_reason="test",
                testability="bogus",
            )

    # --- Constraints validation ---

    def test_f1_insert_valid_constraints(self, db):
        """Valid constraints dict with known keys accepted."""
        result = db.insert_spec(
            id="SPEC-108",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            constraints={"complexity_ceiling": "simple", "custom_key": "preserved"},
        )
        assert result["constraints_parsed"]["complexity_ceiling"] == "simple"
        assert result["constraints_parsed"]["custom_key"] == "preserved"

    def test_f1_insert_non_dict_constraints_raises(self, db):
        """Non-dict constraints raises ValueError."""
        with pytest.raises(ValueError, match="constraints must be a dict"):
            db.insert_spec(
                id="SPEC-109",
                title="T",
                status="specified",
                changed_by="test",
                change_reason="test",
                constraints="not a dict",
            )

    def test_f1_insert_invalid_complexity_ceiling_raises(self, db):
        """Invalid complexity_ceiling value raises ValueError."""
        with pytest.raises(ValueError, match="complexity_ceiling"):
            db.insert_spec(
                id="SPEC-110",
                title="T",
                status="specified",
                changed_by="test",
                change_reason="test",
                constraints={"complexity_ceiling": "unbounded"},
            )

    def test_f1_insert_invalid_decision_authority_raises(self, db):
        """Invalid decision_authority value raises ValueError."""
        with pytest.raises(ValueError, match="decision_authority"):
            db.insert_spec(
                id="SPEC-111",
                title="T",
                status="specified",
                changed_by="test",
                change_reason="test",
                constraints={"decision_authority": "assistant"},
            )

    def test_f1_insert_invalid_excluded_approaches_raises(self, db):
        """Non-string excluded_approaches element raises ValueError."""
        with pytest.raises(ValueError, match="excluded_approaches"):
            db.insert_spec(
                id="SPEC-112",
                title="T",
                status="specified",
                changed_by="test",
                change_reason="test",
                constraints={"excluded_approaches": ["ok", 123]},
            )

    # --- Affected_by validation ---

    def test_f1_insert_valid_affected_by(self, db):
        """Valid affected_by list[str] accepted."""
        result = db.insert_spec(
            id="SPEC-113",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            affected_by=["ADR-001", "DCL-003"],
        )
        assert result["affected_by_parsed"] == ["ADR-001", "DCL-003"]

    def test_f1_insert_non_str_affected_by_raises(self, db):
        """List with non-string element raises ValueError."""
        with pytest.raises(ValueError, match="affected_by"):
            db.insert_spec(
                id="SPEC-114",
                title="T",
                status="specified",
                changed_by="test",
                change_reason="test",
                affected_by=["ADR-001", 42],
            )

    # --- Provisional_until validation ---

    def test_f1_insert_empty_provisional_until_raises(self, db):
        """Empty string provisional_until raises ValueError."""
        with pytest.raises(ValueError, match="provisional_until must be a non-empty"):
            db.insert_spec(
                id="SPEC-115",
                title="T",
                status="specified",
                changed_by="test",
                change_reason="test",
                authority="provisional",
                provisional_until="",
            )

    # --- Output contract ---

    def test_f1_parsed_fields_present(self, db):
        """_parsed fields present in output for JSON columns."""
        db.insert_spec(
            id="SPEC-116",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            constraints={"complexity_ceiling": "moderate"},
            affected_by=["ADR-006"],
        )
        spec = db.get_spec("SPEC-116")
        assert "constraints_parsed" in spec
        assert "affected_by_parsed" in spec
        assert spec["constraints_parsed"] == {"complexity_ceiling": "moderate"}
        assert spec["affected_by_parsed"] == ["ADR-006"]

    def test_f1_affected_by_exact_containment(self, db):
        """affected_by_parsed contains exact IDs."""
        db.insert_spec(
            id="SPEC-117",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            affected_by=["ADR-1", "ADR-10"],
        )
        spec = db.get_spec("SPEC-117")
        assert "ADR-1" in spec["affected_by_parsed"]
        assert "ADR-10" in spec["affected_by_parsed"]
        assert "ADR-100" not in spec["affected_by_parsed"]

    # --- Carry-forward ---

    def test_f1_update_preserves_fields(self, db):
        """Unrelated update preserves all F1 fields."""
        db.insert_spec(
            id="SPEC-118",
            title="Original",
            status="specified",
            changed_by="test",
            change_reason="test",
            authority="inferred",
            testability="automatable",
            constraints={"complexity_ceiling": "simple"},
            affected_by=["ADR-006"],
        )
        db.update_spec(id="SPEC-118", changed_by="test", change_reason="title change", title="Updated")
        spec = db.get_spec("SPEC-118")
        assert spec["title"] == "Updated"
        assert spec["authority"] == "inferred"
        assert spec["testability"] == "automatable"
        assert spec["constraints_parsed"] == {"complexity_ceiling": "simple"}
        assert spec["affected_by_parsed"] == ["ADR-006"]

    def test_f1_constraints_carryforward_roundtrip(self, db):
        """Carried-forward constraints decode to original dict (no double-encoding)."""
        import json

        original = {"complexity_ceiling": "simple", "custom_key": "preserved"}
        db.insert_spec(
            id="SPEC-119",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            constraints=original,
        )
        db.update_spec(id="SPEC-119", changed_by="test", change_reason="unrelated", title="T2")
        spec = db.get_spec("SPEC-119")
        assert spec["constraints_parsed"] == original
        assert json.loads(spec["constraints"]) == original

    def test_f1_affected_by_carryforward_roundtrip(self, db):
        """Carried-forward affected_by decodes to original list (no double-encoding)."""
        import json

        original = ["ADR-001", "DCL-003"]
        db.insert_spec(
            id="SPEC-120",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            affected_by=original,
        )
        db.update_spec(id="SPEC-120", changed_by="test", change_reason="unrelated", title="T2")
        spec = db.get_spec("SPEC-120")
        assert spec["affected_by_parsed"] == original
        assert json.loads(spec["affected_by"]) == original

    # --- Update provisional lifecycle (U1-U5) ---

    def test_f1_update_u1_omitted_authority_new_provisional_raises(self, db):
        """U1: Carried forward authority='stated' + new provisional_until → ValueError."""
        db.insert_spec(
            id="SPEC-121",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            authority="stated",
        )
        with pytest.raises(ValueError, match="provisional_until requires"):
            db.update_spec(id="SPEC-121", changed_by="test", change_reason="test", provisional_until="SPEC-999")

    def test_f1_update_u2_explicit_provisional_valid(self, db):
        """U2: Explicit provisional + provisional_until → valid."""
        db.insert_spec(
            id="SPEC-122",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
        )
        result = db.update_spec(
            id="SPEC-122",
            changed_by="test",
            change_reason="test",
            authority="provisional",
            provisional_until="SPEC-999",
        )
        assert result["authority"] == "provisional"
        assert result["provisional_until"] == "SPEC-999"

    def test_f1_update_u3_change_away_clears_provisional(self, db):
        """U3: Change authority from provisional to stated → auto-clear provisional_until (INV-4)."""
        db.insert_spec(
            id="SPEC-123",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            authority="provisional",
            provisional_until="SPEC-999",
        )
        result = db.update_spec(id="SPEC-123", changed_by="test", change_reason="test", authority="stated")
        assert result["authority"] == "stated"
        assert result["provisional_until"] is None

    def test_f1_update_u4_explicit_none_with_provisional_autosets(self, db):
        """U4: Explicit authority=None + provisional_until → auto-set provisional."""
        db.insert_spec(
            id="SPEC-124",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
        )
        result = db.update_spec(
            id="SPEC-124",
            changed_by="test",
            change_reason="test",
            authority=None,
            provisional_until="SPEC-999",
        )
        assert result["authority"] == "provisional"
        assert result["provisional_until"] == "SPEC-999"

    def test_f1_update_u5_unrelated_change_preserves_f1(self, db):
        """U5: Updating only title preserves all F1 fields."""
        db.insert_spec(
            id="SPEC-125",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            authority="inferred",
            constraints={"complexity_ceiling": "simple"},
            affected_by=["ADR-006"],
            testability="automatable",
        )
        result = db.update_spec(id="SPEC-125", changed_by="test", change_reason="test", title="New title")
        assert result["authority"] == "inferred"
        assert result["testability"] == "automatable"
        assert result["constraints_parsed"]["complexity_ceiling"] == "simple"
        assert result["affected_by_parsed"] == ["ADR-006"]

    # --- Update-path constraints validation ---

    def test_f1_update_new_constraints_validated(self, db):
        """Update with new constraints dict is validated."""
        db.insert_spec(id="SPEC-126", title="T", status="specified", changed_by="t", change_reason="t")
        with pytest.raises(ValueError, match="complexity_ceiling"):
            db.update_spec(
                id="SPEC-126",
                changed_by="t",
                change_reason="t",
                constraints={"complexity_ceiling": "unbounded"},
            )

    # --- Query helpers ---

    def test_f1_get_provisional_specs(self, db):
        """get_provisional_specs returns only provisional specs with provisional_until."""
        db.insert_spec(
            id="SPEC-130",
            title="Provisional",
            status="specified",
            changed_by="test",
            change_reason="test",
            authority="provisional",
            provisional_until="SPEC-999",
        )
        db.insert_spec(
            id="SPEC-131",
            title="Stated",
            status="specified",
            changed_by="test",
            change_reason="test",
            authority="stated",
        )
        provisionals = db.get_provisional_specs()
        ids = [s["id"] for s in provisionals]
        assert "SPEC-130" in ids
        assert "SPEC-131" not in ids

    def test_f1_get_specs_affected_by_exact(self, db):
        """get_specs_affected_by uses exact containment (no false positives)."""
        db.insert_spec(
            id="SPEC-132",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            affected_by=["ADR-1", "ADR-10"],
        )
        db.insert_spec(
            id="SPEC-133",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            affected_by=["ADR-10"],
        )
        # Exact match for ADR-1
        result = db.get_specs_affected_by("ADR-1")
        ids = [s["id"] for s in result]
        assert "SPEC-132" in ids
        assert "SPEC-133" not in ids  # ADR-1 != ADR-10

    # --- List filters ---

    def test_f1_list_specs_filter_authority(self, db):
        """list_specs(authority=...) filters correctly."""
        db.insert_spec(
            id="SPEC-140",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            authority="inferred",
        )
        db.insert_spec(
            id="SPEC-141",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            authority="stated",
        )
        inferred = db.list_specs(authority="inferred")
        ids = [s["id"] for s in inferred]
        assert "SPEC-140" in ids
        assert "SPEC-141" not in ids

    def test_f1_list_specs_filter_testability(self, db):
        """list_specs(testability=...) filters correctly."""
        db.insert_spec(
            id="SPEC-142",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            testability="automatable",
        )
        db.insert_spec(
            id="SPEC-143",
            title="T",
            status="specified",
            changed_by="test",
            change_reason="test",
            testability="manual" if False else "observable",
        )
        result = db.list_specs(testability="automatable")
        ids = [s["id"] for s in result]
        assert "SPEC-142" in ids
        assert "SPEC-143" not in ids


class TestVersioning:
    """Tests for append-only versioning behavior."""

    def test_unique_id_version_constraint(self, db):
        db.insert_spec(
            id="SPEC-001",
            title="V1",
            status="specified",
            changed_by="test",
            change_reason="v1",
        )
        # Second insert with same ID should get version 2, not conflict
        result = db.insert_spec(
            id="SPEC-001",
            title="V2 via insert",
            status="specified",
            changed_by="test",
            change_reason="v2",
        )
        assert result["version"] == 2


class TestWorkItems:
    """Tests for work item CRUD."""

    def test_insert_work_item(self, db):
        result = db.insert_work_item(
            id="WI-001",
            title="Fix bug",
            origin="defect",
            component="core",
            resolution_status="open",
            changed_by="test",
            change_reason="found bug",
        )
        assert result["id"] == "WI-001"
        assert result["origin"] == "defect"
        assert result["stage"] == "created"

    def test_list_open_work_items(self, db):
        db.insert_work_item(
            id="WI-001",
            title="Open",
            origin="new",
            component="core",
            resolution_status="open",
            changed_by="test",
            change_reason="create",
        )
        db.insert_work_item(
            id="WI-002",
            title="Resolved",
            origin="new",
            component="core",
            resolution_status="resolved",
            changed_by="test",
            change_reason="create",
            stage="resolved",
        )
        open_wis = db.get_open_work_items()
        open_ids = [wi["id"] for wi in open_wis]
        assert "WI-001" in open_ids


class TestTests:
    """Tests for test artifact CRUD."""

    def test_insert_test(self, db):
        db.insert_spec(
            id="SPEC-001",
            title="Target Spec",
            status="specified",
            changed_by="test",
            change_reason="create",
        )
        result = db.insert_test(
            id="TEST-001",
            title="Test Case",
            spec_id="SPEC-001",
            test_type="unit",
            expected_outcome="Should pass",
            changed_by="test",
            change_reason="create",
        )
        assert result["id"] == "TEST-001"
        assert result["spec_id"] == "SPEC-001"

    def test_get_tests_for_spec(self, db):
        db.insert_spec(
            id="SPEC-001",
            title="Target",
            status="specified",
            changed_by="test",
            change_reason="create",
        )
        db.insert_test(
            id="TEST-001",
            title="Test 1",
            spec_id="SPEC-001",
            test_type="unit",
            expected_outcome="Pass",
            changed_by="test",
            change_reason="create",
        )
        tests = db.get_tests_for_spec("SPEC-001")
        assert len(tests) == 1


class TestDocuments:
    """Tests for document CRUD."""

    def test_insert_and_get_document(self, db):
        result = db.insert_document(
            id="DOC-001",
            title="Architecture Doc",
            category="architecture",
            status="active",
            changed_by="test",
            change_reason="create",
            content="Some content",
        )
        assert result["id"] == "DOC-001"
        assert result["category"] == "architecture"


class TestGateIntegration:
    """Tests for governance gate integration with KnowledgeDB."""

    def test_adr_gate_blocks_promotion_without_assertions(self, db):
        db.insert_spec(
            id="ADR-001",
            title="Architecture Decision",
            status="specified",
            changed_by="test",
            change_reason="create",
        )
        with pytest.raises(Exception, match="non-empty assertions"):
            db.update_spec(
                id="ADR-001",
                changed_by="test",
                change_reason="promote",
                status="implemented",
            )

    def test_no_gate_registry_allows_all(self, db_no_gates):
        # Without a gate registry, no enforcement
        db_no_gates.insert_spec(
            id="ADR-001",
            title="Architecture Decision",
            status="implemented",
            changed_by="test",
            change_reason="create",
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
            id="SPEC-001",
            title="Test",
            status="specified",
            changed_by="test",
            change_reason="create",
        )
        summary = db.get_summary()
        assert summary["spec_total"] >= 1

    def test_export_json(self, db, tmp_path):
        db.insert_spec(
            id="SPEC-001",
            title="Export Test",
            status="specified",
            changed_by="test",
            change_reason="create",
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
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        expected = {
            "specifications",
            "test_procedures",
            "operational_procedures",
            "assertion_runs",
            "session_prompts",
            "environment_config",
            "documents",
            "test_coverage",
            "tests",
            "test_plans",
            "test_plan_phases",
            "work_items",
            "backlog_snapshots",
            "testable_elements",
            "quality_scores",
        }
        assert expected.issubset(tables)
        conn.close()
        db.close()

    def test_views_created(self, tmp_path):
        db_path = tmp_path / "views.db"
        db = KnowledgeDB(db_path=db_path)
        import sqlite3

        conn = sqlite3.connect(str(db_path))
        views = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()}
        assert "current_specifications" in views
        assert "current_work_items" in views
        conn.close()
        db.close()
