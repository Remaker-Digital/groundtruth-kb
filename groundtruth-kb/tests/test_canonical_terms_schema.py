"""Tests for the canonical_terms schema, insert/get round-trip, and append-only discipline.

Per `bridge/gtkb-canonical-terminology-system-context-model-001-005.md`
Specification-Derived Test Plan: T-schema-1, T-schema-2, T-schema-3, T-schema-4.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from groundtruth_kb import canonical_terms
from groundtruth_kb.db import KnowledgeDB


@pytest.fixture()
def db(tmp_path: Path) -> KnowledgeDB:
    """Fresh KnowledgeDB whose schema includes canonical_terms."""
    db_path = tmp_path / "test.db"
    return KnowledgeDB(str(db_path))


def test_schema_ddl_constant_matches_table_ddl(db: KnowledgeDB) -> None:
    """T-schema-1: SCHEMA_DDL constant matches the proposed DDL exactly.

    The module's SCHEMA_DDL is the canonical text. We assert it contains
    each required column and constraint and is a valid CREATE TABLE.
    """
    ddl = canonical_terms.SCHEMA_DDL
    # Required column names
    for col in (
        "id",
        "version",
        "canonical_term",
        "definition",
        "authority_level",
        "scope",
        "accepted_synonyms",
        "discouraged_synonyms",
        "linked_artifacts",
        "linked_services",
        "usage_examples",
        "forbidden_uses",
        "lifecycle_status",
        "source_authority",
        "changed_by",
        "changed_at",
        "change_reason",
    ):
        assert col in ddl, f"DDL missing column {col!r}"
    # CHECK constraints
    assert "authority_level IN ('platform_core', 'adopter_extension', 'project_local')" in ddl
    assert "lifecycle_status IN ('candidate', 'active', 'deprecated', 'retired')" in ddl
    assert "UNIQUE(id, version)" in ddl
    # The DDL must compile against an empty in-memory database.
    conn = sqlite3.connect(":memory:")
    conn.execute(ddl)


def test_table_present_in_initialized_database(db: KnowledgeDB) -> None:
    """KnowledgeDB initialization creates the canonical_terms table."""
    conn = db._get_conn()
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'canonical_terms'").fetchall()
    assert rows, "canonical_terms table not present after KnowledgeDB init"


def test_current_view_present_in_initialized_database(db: KnowledgeDB) -> None:
    """KnowledgeDB initialization creates current_canonical_terms view."""
    conn = db._get_conn()
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'view' AND name = 'current_canonical_terms'"
    ).fetchall()
    assert rows, "current_canonical_terms view not present after KnowledgeDB init"


def test_insert_and_get_roundtrip(db: KnowledgeDB) -> None:
    """T-schema baseline: insert returns the inserted row; get retrieves latest."""
    inserted = canonical_terms.insert_term(
        db,
        id="MEMBASE",
        canonical_term="MemBase",
        definition="The canonical store.",
        authority_level="platform_core",
        scope="platform",
        accepted_synonyms=["Knowledge Database"],
        source_authority=".claude/rules/operating-model.md §2",
        changed_by="test",
        change_reason="initial seed",
    )
    assert inserted is not None
    assert inserted["id"] == "MEMBASE"
    assert inserted["version"] == 1
    assert inserted["accepted_synonyms"] == ["Knowledge Database"]
    fetched = canonical_terms.get_term(db, "MEMBASE")
    assert fetched is not None
    assert fetched["canonical_term"] == "MemBase"


def test_append_only_two_versions(db: KnowledgeDB) -> None:
    """T-schema-2: inserting two versions of the same id returns both rows
    on list_versions, and get_term returns the latest.
    """
    canonical_terms.insert_term(
        db,
        id="MEMBASE",
        canonical_term="MemBase",
        definition="v1 definition",
        authority_level="platform_core",
        scope="platform",
        source_authority="rule@v1",
        changed_by="test",
        change_reason="initial",
    )
    canonical_terms.insert_term(
        db,
        id="MEMBASE",
        canonical_term="MemBase",
        definition="v2 definition (refined)",
        authority_level="platform_core",
        scope="platform",
        source_authority="rule@v2",
        changed_by="test",
        change_reason="refinement",
    )
    versions = canonical_terms.list_versions(db, "MEMBASE")
    assert len(versions) == 2
    assert versions[0]["version"] == 1
    assert versions[1]["version"] == 2
    latest = canonical_terms.get_term(db, "MEMBASE")
    assert latest is not None
    assert latest["version"] == 2
    assert latest["definition"] == "v2 definition (refined)"


def test_append_only_view_returns_only_latest(db: KnowledgeDB) -> None:
    """current_canonical_terms view filters to the latest version per id."""
    canonical_terms.insert_term(
        db,
        id="X",
        canonical_term="X v1",
        definition="d1",
        authority_level="platform_core",
        scope="platform",
        source_authority="rule",
        changed_by="t",
        change_reason="initial",
    )
    canonical_terms.insert_term(
        db,
        id="X",
        canonical_term="X v2",
        definition="d2",
        authority_level="platform_core",
        scope="platform",
        source_authority="rule",
        changed_by="t",
        change_reason="update",
    )
    rows = canonical_terms.list_terms(db, authority_level="platform_core")
    assert len(rows) == 1
    assert rows[0]["canonical_term"] == "X v2"


def test_authority_level_constraint_blocks_invalid(db: KnowledgeDB) -> None:
    """T-schema-3: authority_level must be one of the three allowed values.

    The Python validator raises CanonicalTermValidationError before the
    INSERT reaches sqlite, but the DB constraint also enforces it (covered
    by the next test).
    """
    with pytest.raises(canonical_terms.CanonicalTermValidationError, match="authority_level"):
        canonical_terms.insert_term(
            db,
            id="X",
            canonical_term="X",
            definition="d",
            authority_level="invalid",  # type: ignore[arg-type]
            scope="platform",
            source_authority="rule",
            changed_by="t",
            change_reason="should fail",
        )


def test_authority_level_db_constraint_blocks_raw_invalid(db: KnowledgeDB) -> None:
    """T-schema-3 (db-level): raw INSERT bypassing the validator still fails
    via the CHECK constraint.
    """
    conn = db._get_conn()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO canonical_terms (
                id, version, canonical_term, definition, authority_level, scope,
                lifecycle_status, source_authority, changed_by, changed_at, change_reason
            ) VALUES ('X', 1, 'X', 'd', 'BOGUS_LEVEL', 'platform', 'active', 'r', 't',
                      '2026-05-08T00:00:00Z', 'reason')
            """
        )


def test_lifecycle_status_constraint_blocks_invalid(db: KnowledgeDB) -> None:
    """T-schema-4: lifecycle_status must be one of the four allowed values."""
    with pytest.raises(canonical_terms.CanonicalTermValidationError, match="lifecycle_status"):
        canonical_terms.insert_term(
            db,
            id="X",
            canonical_term="X",
            definition="d",
            authority_level="platform_core",
            scope="platform",
            source_authority="rule",
            changed_by="t",
            change_reason="should fail",
            lifecycle_status="archived",  # type: ignore[arg-type]
        )


def test_lifecycle_status_db_constraint_blocks_raw_invalid(db: KnowledgeDB) -> None:
    """T-schema-4 (db-level): raw INSERT bypassing the validator still fails
    via the CHECK constraint.
    """
    conn = db._get_conn()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO canonical_terms (
                id, version, canonical_term, definition, authority_level, scope,
                lifecycle_status, source_authority, changed_by, changed_at, change_reason
            ) VALUES ('X', 1, 'X', 'd', 'platform_core', 'platform', 'archived', 'r', 't',
                      '2026-05-08T00:00:00Z', 'reason')
            """
        )


def test_required_string_validation(db: KnowledgeDB) -> None:
    """Empty/blank required fields raise CanonicalTermValidationError."""
    with pytest.raises(canonical_terms.CanonicalTermValidationError):
        canonical_terms.insert_term(
            db,
            id="",
            canonical_term="X",
            definition="d",
            authority_level="platform_core",
            scope="platform",
            source_authority="rule",
            changed_by="t",
            change_reason="should fail",
        )


def test_unique_id_version_enforced(db: KnowledgeDB) -> None:
    """UNIQUE(id, version) prevents two raw INSERTs at the same version."""
    conn = db._get_conn()
    conn.execute(
        """
        INSERT INTO canonical_terms (
            id, version, canonical_term, definition, authority_level, scope,
            lifecycle_status, source_authority, changed_by, changed_at, change_reason
        ) VALUES ('X', 1, 'X', 'd', 'platform_core', 'platform', 'active', 'r', 't', '2026-05-08T00:00:00Z', 'reason')
        """
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO canonical_terms (
                id, version, canonical_term, definition, authority_level, scope,
                lifecycle_status, source_authority, changed_by, changed_at, change_reason
            ) VALUES ('X', 1, 'X', 'd', 'platform_core', 'platform', 'active', 'r', 't',
                      '2026-05-08T00:00:00Z', 'reason')
            """
        )


def test_list_terms_filters_retired_by_default(db: KnowledgeDB) -> None:
    """list_terms excludes retired by default and includes them when asked."""
    canonical_terms.insert_term(
        db,
        id="A",
        canonical_term="A",
        definition="d",
        authority_level="platform_core",
        scope="platform",
        source_authority="rule",
        changed_by="t",
        change_reason="initial",
    )
    canonical_terms.insert_term(
        db,
        id="A",
        canonical_term="A",
        definition="d",
        authority_level="platform_core",
        scope="platform",
        source_authority="rule",
        changed_by="t",
        change_reason="retire",
        lifecycle_status="retired",
    )
    assert canonical_terms.list_terms(db) == []
    rows = canonical_terms.list_terms(db, include_retired=True)
    assert len(rows) == 1
    assert rows[0]["lifecycle_status"] == "retired"
