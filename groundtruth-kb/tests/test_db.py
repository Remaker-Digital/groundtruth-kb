"""Tests for KnowledgeDB core CRUD and versioning."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

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
            project_name="Project Alpha",
            implementation_order=7,
            status_detail="ready",
        )
        assert result["id"] == "WI-001"
        assert result["origin"] == "defect"
        assert result["stage"] == "created"
        assert result["project_name"] == "Project Alpha"
        assert result["implementation_order"] == 7
        assert result["status_detail"] == "ready"

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
        assert "WI-002" not in open_ids

    @staticmethod
    def _reopen_threads() -> str:
        return json.dumps(
            [
                "bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-007.md",
                "bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-008.md",
            ]
        )

    @staticmethod
    def _reopen_reason() -> str:
        return (
            "WI-5441 owner-approved terminal repair under "
            "PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724"
        )

    def test_reopen_terminal_work_item_appends_one_version_and_event(self, db):
        db.insert_work_item(
            id="WI-5441",
            title="Registry control plane",
            origin="defect",
            component="core",
            resolution_status="open",
            changed_by="test",
            change_reason="seed false terminal state",
            stage="resolved",
        )
        before_events = (
            db._get_conn()
            .execute(
                "SELECT COUNT(*) FROM pipeline_events WHERE artifact_id = ? AND event_type = 'wi_reopened'",
                ("WI-5441",),
            )
            .fetchone()[0]
        )

        row = db.reopen_terminal_work_item(
            "WI-5441",
            "prime-builder/codex",
            self._reopen_reason(),
            resolution_status="open",
            stage="backlogged",
            related_bridge_threads=self._reopen_threads(),
            owner_approved=True,
            bridge_evidence_validated=True,
            required_bridge_threads=set(json.loads(self._reopen_threads())),
            exact_related_bridge_threads=False,
            expected_current_version=1,
        )

        assert row is not None
        assert row["version"] == 2
        assert row["resolution_status"] == "open"
        assert row["stage"] == "backlogged"
        assert len(db.get_work_item_history("WI-5441")) == 2
        events = (
            db._get_conn()
            .execute(
                "SELECT * FROM pipeline_events WHERE artifact_id = ? AND event_type = 'wi_reopened'",
                ("WI-5441",),
            )
            .fetchall()
        )
        assert len(events) == before_events + 1
        assert events[-1]["artifact_version"] == 2

    @pytest.mark.parametrize(
        ("owner_approved", "bridge_evidence_validated"),
        [(False, True), (True, False)],
    )
    def test_reopen_terminal_work_item_rejects_incomplete_authority_without_writes(
        self, db, owner_approved, bridge_evidence_validated
    ):
        db.insert_work_item(
            id="WI-5441",
            title="Registry control plane",
            origin="defect",
            component="core",
            resolution_status="open",
            changed_by="test",
            change_reason="seed false terminal state",
            stage="resolved",
        )
        with pytest.raises(ValueError, match="Terminal reopen requires"):
            db.reopen_terminal_work_item(
                "WI-5441",
                "prime-builder/codex",
                self._reopen_reason(),
                resolution_status="open",
                stage="backlogged",
                related_bridge_threads=self._reopen_threads(),
                owner_approved=owner_approved,
                bridge_evidence_validated=bridge_evidence_validated,
                required_bridge_threads=set(json.loads(self._reopen_threads())),
                exact_related_bridge_threads=False,
                expected_current_version=1,
            )
        assert len(db.get_work_item_history("WI-5441")) == 1
        assert (
            db._get_conn()
            .execute(
                "SELECT COUNT(*) FROM pipeline_events WHERE artifact_id = ? AND event_type = 'wi_reopened'",
                ("WI-5441",),
            )
            .fetchone()[0]
            == 0
        )

    def test_reopen_terminal_work_item_requires_explicit_non_empty_path_policy(self, db):
        db.insert_work_item(
            id="WI-5441",
            title="Registry control plane",
            origin="defect",
            component="core",
            resolution_status="open",
            changed_by="test",
            change_reason="seed false terminal state",
            stage="resolved",
        )

        with pytest.raises(ValueError, match="explicit non-empty required bridge path policy"):
            db.reopen_terminal_work_item(
                "WI-5441",
                "prime-builder/codex",
                self._reopen_reason(),
                resolution_status="open",
                stage="backlogged",
                related_bridge_threads=self._reopen_threads(),
                owner_approved=True,
                bridge_evidence_validated=True,
                required_bridge_threads=set(),
                exact_related_bridge_threads=False,
                expected_current_version=1,
            )

        assert len(db.get_work_item_history("WI-5441")) == 1

    def test_reopen_terminal_work_item_enforces_exact_path_policy(self, db):
        db.insert_work_item(
            id="WI-5640",
            title="File move canonicalization",
            origin="defect",
            component="core",
            resolution_status="resolved",
            changed_by="test",
            change_reason="seed false terminal state",
            stage="resolved",
        )
        supplied = [*json.loads(self._reopen_threads()), "bridge/unrelated-001.md"]

        with pytest.raises(ValueError, match="exact related bridge path policy"):
            db.reopen_terminal_work_item(
                "WI-5640",
                "prime-builder/codex",
                "WI-5640 owner-approved terminal repair under PAUTH-WI5640-TEST",
                resolution_status="open",
                stage="implementing",
                related_bridge_threads=json.dumps(supplied),
                owner_approved=True,
                bridge_evidence_validated=True,
                required_bridge_threads=set(json.loads(self._reopen_threads())),
                exact_related_bridge_threads=True,
                expected_current_version=1,
            )

        assert len(db.get_work_item_history("WI-5640")) == 1

    def test_reopen_terminal_work_item_rejects_stale_expected_version(self, db):
        db.insert_work_item(
            id="WI-5441",
            title="Registry control plane",
            origin="defect",
            component="core",
            resolution_status="open",
            changed_by="test",
            change_reason="seed false terminal state",
            stage="resolved",
        )

        with pytest.raises(ValueError, match="version changed after live validation"):
            db.reopen_terminal_work_item(
                "WI-5441",
                "prime-builder/codex",
                self._reopen_reason(),
                resolution_status="open",
                stage="backlogged",
                related_bridge_threads=self._reopen_threads(),
                owner_approved=True,
                bridge_evidence_validated=True,
                required_bridge_threads=set(json.loads(self._reopen_threads())),
                exact_related_bridge_threads=False,
                expected_current_version=999,
            )

        assert len(db.get_work_item_history("WI-5441")) == 1


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


class TestArtifactUpdateRequestSchema:
    """WI-5183 durable idempotency receipt schema."""

    @staticmethod
    def _receipt_values(key: str = "request-1") -> tuple[object, ...]:
        return (
            key,
            1,
            "request-digest",
            "TEST-001",
            1,
            2,
            "postimage-digest",
            '{"row":{"id":"TEST-001","version":2}}',
            "receipt-digest",
            "PROJECT-001",
            "WI-001",
            "bridge-slug",
            "bridge/bridge-slug-002.md",
            "go-digest",
            "session-001",
            "2026-08-26T00:00:00Z",
            "test",
            "exercise receipt schema",
        )

    def test_receipt_table_and_indexes_exist(self, db):
        conn = db._get_conn()
        columns = {row[1] for row in conn.execute("PRAGMA table_info(test_artifact_update_requests)")}
        assert {
            "idempotency_key",
            "request_digest",
            "result_test_version",
            "result_payload_json",
            "result_receipt_digest",
            "go_sha256",
            "actor_session_context_id",
        } <= columns
        indexes = {row[1] for row in conn.execute("PRAGMA index_list(test_artifact_update_requests)")}
        assert "idx_test_artifact_update_requests_test" in indexes
        assert "idx_test_artifact_update_requests_bridge" in indexes

    def test_idempotency_key_and_result_version_are_unique(self, db):
        conn = db._get_conn()
        statement = """INSERT INTO test_artifact_update_requests
            (idempotency_key, request_schema_version, request_digest, test_id,
             expected_test_version, result_test_version, result_postimage_digest,
             result_payload_json, result_receipt_digest, project_id, work_item_id,
             bridge_slug, go_file, go_sha256, actor_session_context_id, created_at,
             changed_by, change_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        conn.execute(statement, self._receipt_values())
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(statement, self._receipt_values())
        second_key = list(self._receipt_values("request-2"))
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(statement, tuple(second_key))


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


# --- source_paths migration tests (Migration 4, governance hardening Phase 1) ---


def test_source_paths_migration_fresh_db(tmp_path):
    """source_paths column is created on a brand-new database."""
    db = KnowledgeDB(tmp_path / "fresh.db")
    cols = {row[1] for row in db._conn.execute("PRAGMA table_info(specifications)")}
    db.close()
    assert "source_paths" in cols


def test_source_paths_migration_idempotent(tmp_path):
    """Opening an already-migrated database does not raise."""
    db_path = tmp_path / "existing.db"
    db1 = KnowledgeDB(db_path)
    db1.close()
    db2 = KnowledgeDB(db_path)
    cols = {row[1] for row in db2._conn.execute("PRAGMA table_info(specifications)")}
    db2.close()
    assert "source_paths" in cols


def test_insert_spec_without_source_paths_still_works(tmp_path):
    """Specs can be inserted without supplying source_paths (column defaults to NULL)."""
    db = KnowledgeDB(tmp_path / "test.db")
    result = db.insert_spec(
        id="SPEC-TEST-NOPATHS",
        title="Test",
        status="specified",
        changed_by="test",
        change_reason="test",
    )
    assert result is not None
    row = db._conn.execute("SELECT source_paths FROM specifications WHERE id = ?", ("SPEC-TEST-NOPATHS",)).fetchone()
    db.close()
    assert row is not None
    assert row[0] is None


def test_insert_spec_with_source_paths(tmp_path):
    """source_paths is stored as JSON and read back correctly."""
    import json

    db = KnowledgeDB(tmp_path / "test.db")
    result = db.insert_spec(
        id="SPEC-TEST-PATHS",
        title="Test with paths",
        status="specified",
        changed_by="test",
        change_reason="test",
        source_paths=["src/auth.py", "src/auth_utils.py"],
    )
    assert result is not None
    row = db._conn.execute("SELECT source_paths FROM specifications WHERE id = ?", ("SPEC-TEST-PATHS",)).fetchone()
    db.close()
    assert row is not None
    assert row[0] is not None
    stored = json.loads(row[0])
    assert stored == ["src/auth.py", "src/auth_utils.py"]


def test_registry_path_observations_use_only_typed_current_fields(db):
    db.insert_spec(
        id="SPEC-PATH-OBS",
        title="Path observation",
        status="specified",
        changed_by="test",
        change_reason="fixture",
        source_paths=["src/one.py", "src/*.toml"],
    )
    db.insert_test(
        id="TEST-PATH-OBS",
        title="Path observation test",
        spec_id="SPEC-PATH-OBS",
        test_type="unit",
        expected_outcome="passes",
        changed_by="test",
        change_reason="fixture",
        test_file="tests/test_one.py::test_one",
    )
    db.insert_document(
        id="DOC-PATH-OBS",
        title="Path observation document",
        category="reference",
        status="active",
        changed_by="test",
        change_reason="fixture",
        source_path="docs/one.md",
    )

    rows = db.list_registry_path_observations()

    assert {row["path"] for row in rows} == {
        "docs/one.md",
        "src/*.toml",
        "src/one.py",
        "tests/test_one.py",
    }
    assert all(set(row) == {"path", "source_kind", "source_id", "field"} for row in rows)


def test_update_spec_preserves_source_paths(tmp_path):
    """update_spec carries forward source_paths when not explicitly changed (C1)."""
    db = KnowledgeDB(tmp_path / "test.db")
    db.insert_spec(
        id="SPEC-CARRY",
        title="Original title",
        status="specified",
        changed_by="test",
        change_reason="initial",
        source_paths=["src/auth.py"],
    )
    db.update_spec("SPEC-CARRY", changed_by="test", change_reason="title update", title="Updated title")
    spec = db.get_spec("SPEC-CARRY")
    db.close()
    assert spec is not None
    assert spec["source_paths_parsed"] == ["src/auth.py"]


def test_application_scope_migration_fresh_db(tmp_path):
    """application_scope columns are created on a brand-new database."""
    db = KnowledgeDB(tmp_path / "fresh.db")
    spec_cols = {row[1] for row in db._conn.execute("PRAGMA table_info(specifications)")}
    test_cols = {row[1] for row in db._conn.execute("PRAGMA table_info(tests)")}
    db.close()
    assert "application_scope" in spec_cols
    assert "application_scope" in test_cols


def test_application_scope_migration_idempotent(tmp_path):
    """Opening an already-migrated database does not raise."""
    db_path = tmp_path / "existing.db"
    db1 = KnowledgeDB(db_path)
    db1.close()
    db2 = KnowledgeDB(db_path)
    spec_cols = {row[1] for row in db2._conn.execute("PRAGMA table_info(specifications)")}
    test_cols = {row[1] for row in db2._conn.execute("PRAGMA table_info(tests)")}
    db2.close()
    assert "application_scope" in spec_cols
    assert "application_scope" in test_cols


def test_spec_application_scope_insert_and_carry_forward(tmp_path):
    """Specs store application_scope and preserve it on append-only update."""
    db = KnowledgeDB(tmp_path / "test.db")
    db.insert_spec(
        id="SPEC-APP-SCOPE",
        title="Agent Red app scope",
        status="specified",
        changed_by="test",
        change_reason="initial",
        source_paths=["applications/Agent_Red/app/main.py"],
        application_scope="agent_red_application",
    )
    db.update_spec("SPEC-APP-SCOPE", changed_by="test", change_reason="title update", title="Updated")
    spec = db.get_spec("SPEC-APP-SCOPE")
    db.close()
    assert spec is not None
    assert spec["application_scope"] == "agent_red_application"
    assert spec["source_paths_parsed"] == ["applications/Agent_Red/app/main.py"]


def test_test_application_scope_insert_and_carry_forward(tmp_path):
    """Tests store application_scope and preserve it on append-only update."""
    db = KnowledgeDB(tmp_path / "test.db")
    db.insert_test(
        id="TEST-APP-SCOPE",
        title="Agent Red app test",
        spec_id="SPEC-APP-SCOPE",
        test_type="unit",
        test_file="applications/Agent_Red/tests/test_app.py",
        expected_outcome="passes",
        changed_by="test",
        change_reason="initial",
        application_scope="agent_red_application",
    )
    db.update_test("TEST-APP-SCOPE", changed_by="test", change_reason="result", last_result="pass")
    test = db.get_test("TEST-APP-SCOPE")
    db.close()
    assert test is not None
    assert test["application_scope"] == "agent_red_application"
    assert test["test_file"] == "applications/Agent_Red/tests/test_app.py"


class TestProjectAuthorizationRemoved:
    """WI-7657: the project-authorization record has no database surface.

    This replaces TestProjectAuthorizationSpecLinkage and
    TestProjectAuthorizationSpecAmendment. Both exercised an append-only
    authorization row -- its spec-linkage precondition and its amendment
    path. The relation is gone and authorization is a field on the project
    row, so both classes assert absence here instead.

    Non-vacuity: each absence assertion is paired with a control that is
    still present, so a mistyped name or a failed import cannot pass.
    """

    REMOVED_WRITERS = (
        "insert_project_authorization",
        "update_project_authorization",
        "get_project_authorization",
        "list_project_authorizations",
    )

    def test_control_surface_is_present(self, db) -> None:
        assert hasattr(db, "insert_project")
        assert hasattr(db, "get_project")

    def test_authorization_writers_are_absent(self, db) -> None:
        assert hasattr(db, "insert_project"), "control method missing"
        for name in self.REMOVED_WRITERS:
            assert not hasattr(db, name), f"KnowledgeDB should no longer expose {name}"

    def test_authorization_relations_are_absent(self, db) -> None:
        names = {row[0] for row in db._get_conn().execute("SELECT name FROM sqlite_master")}
        assert "projects" in names, "control relation missing"
        assert not [name for name in names if "project_authorization" in name]

    def test_authorization_is_a_project_row_field(self, db) -> None:
        columns = {row[1] for row in db._get_conn().execute("PRAGMA table_info(projects)")}
        assert "id" in columns, "control column missing"
        assert "authorization" in columns


class TestHarnesses:
    """Tests for the harnesses registry table (REQ-HARNESS-REGISTRY-001 FR1)."""

    def test_harnesses_table_created(self, db):
        # list_harnesses() selects from the current_harnesses view, which selects
        # from the harnesses table; a clean empty result on a fresh DB proves
        # both the table and the view were created at schema initialization.
        assert db.list_harnesses() == []
        assert db.get_harness("B") is None

    def test_insert_harness_creates_v1(self, db):
        result = db.insert_harness(
            id="B",
            harness_name="claude",
            harness_type="claude",
            role=["prime-builder"],
            changed_by="test",
            change_reason="initial registration",
            invocation_surfaces={"interactive": "claude", "headless": "claude -p"},
            capabilities_ref="config/agent-control/harness-capability-registry.toml",
        )
        assert result is not None
        assert result["id"] == "B"
        assert result["version"] == 1
        assert result["harness_name"] == "claude"
        assert result["harness_type"] == "claude"
        assert result["status"] == "registered"
        assert result["role"] == '["prime-builder"]'
        assert result["reviewer_precedence"] is None
        assert result["invocation_surfaces"] == '{"interactive": "claude", "headless": "claude -p"}'
        assert result["capabilities_ref"].endswith("harness-capability-registry.toml")

    def test_insert_harness_version_bumps(self, db):
        v1 = db.insert_harness(
            id="A",
            harness_name="codex",
            harness_type="codex",
            role=["loyal-opposition"],
            changed_by="test",
            change_reason="v1",
        )
        v2 = db.insert_harness(
            id="A",
            harness_name="codex",
            harness_type="codex",
            role=["loyal-opposition"],
            changed_by="test",
            change_reason="v2",
            status="suspended",
        )
        assert v1["version"] == 1
        assert v2["version"] == 2
        assert v2["status"] == "suspended"

    def test_get_harness_returns_latest(self, db):
        db.insert_harness(
            id="C",
            harness_name="antigravity",
            harness_type="antigravity",
            role=["loyal-opposition"],
            changed_by="test",
            change_reason="v1",
        )
        db.insert_harness(
            id="C",
            harness_name="antigravity",
            harness_type="antigravity",
            role=["loyal-opposition"],
            changed_by="test",
            change_reason="v2",
            status="active",
        )
        result = db.get_harness("C")
        assert result is not None
        assert result["version"] == 2
        assert result["status"] == "active"
        assert db.get_harness("NO-SUCH-HARNESS") is None

    def test_list_harnesses_returns_current_set(self, db):
        db.insert_harness(
            id="A",
            harness_name="codex",
            harness_type="codex",
            role=["loyal-opposition"],
            changed_by="test",
            change_reason="v1",
        )
        db.insert_harness(
            id="B",
            harness_name="claude",
            harness_type="claude",
            role=["prime-builder"],
            changed_by="test",
            change_reason="v1",
        )
        db.insert_harness(
            id="B",
            harness_name="claude",
            harness_type="claude",
            role=["prime-builder"],
            changed_by="test",
            change_reason="v2",
            status="active",
        )
        harnesses = db.list_harnesses()
        assert len(harnesses) == 2
        by_id = {h["id"]: h for h in harnesses}
        assert by_id["A"]["version"] == 1
        assert by_id["B"]["version"] == 2
        assert by_id["B"]["status"] == "active"


class TestSpecLifecycleSchemaSlice1:
    def test_specifications_table_has_new_lifecycle_columns(self, db):
        cols = {row[1] for row in db._get_conn().execute("PRAGMA table_info(specifications)").fetchall()}
        assert {"implementation_verified_at", "retired_at", "parent"}.issubset(cols)

    def test_specifications_alter_table_migration_idempotent(self, tmp_path):
        db_path = tmp_path / "legacy.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            """CREATE TABLE specifications (
                rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT NOT NULL,
                version INTEGER NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                changed_by TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                change_reason TEXT NOT NULL,
                UNIQUE(id, version)
            )"""
        )
        conn.execute(
            """INSERT INTO specifications
               (id, version, title, status, changed_by, changed_at, change_reason)
               VALUES ('SPEC-LEGACY', 1, 'Legacy', 'specified', 'test', '2026-05-19T00:00:00Z', 'seed')"""
        )
        conn.commit()
        conn.close()

        db = KnowledgeDB(db_path=db_path)
        db.close()
        db2 = KnowledgeDB(db_path=db_path)
        row = db2._get_conn().execute("SELECT * FROM specifications WHERE id = 'SPEC-LEGACY'").fetchone()
        assert row["implementation_verified_at"] is None
        assert row["retired_at"] is None
        assert row["parent"] is None

    def test_specification_deliberation_sources_table_exists(self, db):
        conn = db._get_conn()
        cols = [row[1] for row in conn.execute("PRAGMA table_info(specification_deliberation_sources)").fetchall()]
        assert cols == [
            "rowid",
            "spec_id",
            "spec_version",
            "deliberation_id",
            "source_role",
            "added_at",
            "added_by",
        ]
        unique_indexes = [
            row[1] for row in conn.execute("PRAGMA index_list(specification_deliberation_sources)").fetchall() if row[2]
        ]
        indexed_columns = {
            tuple(col[2] for col in conn.execute(f'PRAGMA index_info("{index_name}")').fetchall())
            for index_name in unique_indexes
        }
        assert ("spec_id", "spec_version", "deliberation_id") in indexed_columns

    def test_link_spec_deliberation_source_inserts_row(self, db):
        row = db.link_spec_deliberation_source(
            "SPEC-001",
            1,
            "DELIB-0707",
            "test",
            source_role="source",
            added_at="2026-05-19T00:00:00Z",
        )
        assert row["spec_id"] == "SPEC-001"
        assert row["spec_version"] == 1
        assert row["deliberation_id"] == "DELIB-0707"
        assert row["source_role"] == "source"
        assert row["added_at"] == "2026-05-19T00:00:00Z"
        assert row["added_by"] == "test"
        with pytest.raises(ValueError, match="added_by is required"):
            db.link_spec_deliberation_source("SPEC-001", 1, "DELIB-0707", "")

    def test_link_spec_deliberation_source_idempotent_re_link(self, db):
        first = db.link_spec_deliberation_source("SPEC-001", 1, "DELIB-0707", "test", source_role="source")
        second = db.link_spec_deliberation_source("SPEC-001", 1, "DELIB-0707", "test-2", source_role="context")
        count = db._get_conn().execute("SELECT COUNT(*) FROM specification_deliberation_sources").fetchone()[0]
        assert first["rowid"] == second["rowid"]
        assert second["added_by"] == "test"
        assert second["source_role"] == "source"
        assert count == 1

    def test_populated_fixture_migration_zero_data_loss(self, tmp_path):
        fixture_path = Path(__file__).parent / "fixtures" / "spec_lifecycle_slice1_populated_fixture.json"
        fixture_data = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture_rows = fixture_data["rows"] if isinstance(fixture_data, dict) else fixture_data
        db_path = tmp_path / "fixture.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            """CREATE TABLE specifications (
                rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT NOT NULL,
                version INTEGER NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                changed_by TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                change_reason TEXT NOT NULL,
                UNIQUE(id, version)
            )"""
        )
        trimmed_rows = [
            {
                "id": row["id"],
                "version": row["version"],
                "title": row["title"],
                "status": row["status"],
                "changed_by": row["changed_by"],
                "changed_at": row["changed_at"],
                "change_reason": row["change_reason"],
            }
            for row in fixture_rows[:50]
        ]
        conn.executemany(
            """INSERT INTO specifications
               (id, version, title, status, changed_by, changed_at, change_reason)
               VALUES (:id, :version, :title, :status, :changed_by, :changed_at, :change_reason)""",
            trimmed_rows,
        )
        conn.commit()
        conn.row_factory = sqlite3.Row
        before = [dict(row) for row in conn.execute("SELECT * FROM specifications ORDER BY id, version").fetchall()]
        conn.close()

        db = KnowledgeDB(db_path=db_path)
        after_rows = db._get_conn().execute("SELECT * FROM specifications ORDER BY id, version").fetchall()
        assert len(after_rows) == 50
        for before_row, after_row in zip(before, after_rows, strict=True):
            for field in ("id", "version", "title", "status", "changed_by", "changed_at", "change_reason"):
                assert before_row[field] == after_row[field]
            assert after_row["implementation_verified_at"] is None
            assert after_row["retired_at"] is None
            assert after_row["parent"] is None

    def test_tracking_work_item_inserted_with_expected_fields(self, db):
        db.insert_work_item(
            "WI-SPEC-LIFECYCLE-SCHEMA-SLICE-1",
            "Spec lifecycle schema additions (Slice 1)",
            "new",
            "spec-lifecycle",
            "in_progress",
            "claude-prime-builder",
            "Track Slice 1 implementation of additive lifecycle schema per parent GO "
            "bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md (REVISED-1 of slice-1)",
            stage="implementing",
            source_spec_id=None,
            related_bridge_threads="gtkb-spec-lifecycle-schema-slice-1",
            related_deliberation_ids="DELIB-0707,DELIB-1852",
        )
        row = db.get_work_item("WI-SPEC-LIFECYCLE-SCHEMA-SLICE-1")
        assert row["title"] == "Spec lifecycle schema additions (Slice 1)"
        assert row["origin"] == "new"
        assert row["component"] == "spec-lifecycle"
        assert row["resolution_status"] == "in_progress"
        assert row["stage"] == "implementing"
        assert row["source_spec_id"] is None
        assert row["changed_by"] == "claude-prime-builder"
        assert row["related_bridge_threads"] == "gtkb-spec-lifecycle-schema-slice-1"
        assert row["related_deliberation_ids"] == "DELIB-0707,DELIB-1852"


class TestKPIViewsAndQueryMethods:
    """Tests for the Phase 1 DB instrumentation KPI views and KnowledgeDB helper methods."""

    def test_get_kpi_spec_test_mapping(self, db) -> None:
        result = db.get_kpi_spec_test_mapping()
        assert result is not None
        assert "total_specifications" in result
        assert "mapped_specifications" in result
        assert "unmapped_specifications" in result
        assert "spec_test_mapping_percentage" in result

    def test_get_kpi_deliberation_provenance(self, db) -> None:
        result = db.get_kpi_deliberation_provenance()
        assert result is not None
        assert "deliberation_linkage_percentage" in result
        assert "total_work_items" in result
        assert "unmapped_work_items" in result

    def test_get_kpi_backlog_churn(self, db) -> None:
        result = db.get_kpi_backlog_churn()
        assert result is not None
        assert "active_churn_ratio" in result
        assert "total_work_items" in result
        assert "active_unresolved_items" in result
        assert "completed_items" in result
