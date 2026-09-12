"""Specification-derived tests for KnowledgeDB connect-time schema migration guard (WI-6609)."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from groundtruth_kb.db import (
    _SCHEMA_STRUCTURAL_SENTINELS,
    _VALID_AUTHORIZATION_VALUES,
    SCHEMA_VERSION,
    KnowledgeDB,
)


def test_knowledgedb_initialization_stamps_user_version(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    _ = KnowledgeDB(db_path=db_file)
    conn = sqlite3.connect(str(db_file))
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    conn.close()
    assert version == SCHEMA_VERSION


def test_knowledgedb_reconnect_performs_no_upgrade(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    # First init stamps schema version
    _ = KnowledgeDB(db_path=db_file)

    # Re-connect
    db2 = KnowledgeDB(db_path=db_file)
    conn = db2._get_conn()
    assert KnowledgeDB._schema_version(conn) == SCHEMA_VERSION


def test_knowledgedb_read_connection_concurrency(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    # First initialization
    _ = KnowledgeDB(db_path=db_file)

    # Concurrent read connection
    db2 = KnowledgeDB(db_path=db_file)
    specs = db2.list_specs()
    assert isinstance(specs, list)


def test_knowledgedb_user_version_guard_prevents_redundant_writes(tmp_path: Path, monkeypatch) -> None:
    db_file = tmp_path / "test.db"
    _ = KnowledgeDB(db_path=db_file)

    upgrade_called = False

    def fake_upgrade(self, conn):
        nonlocal upgrade_called
        upgrade_called = True

    monkeypatch.setattr(KnowledgeDB, "_upgrade_schema", fake_upgrade)

    _ = KnowledgeDB(db_path=db_file)
    assert not upgrade_called


def test_structural_sentinels_present_after_construction(tmp_path):
    """The guard the db.py comment always claimed existed, but never did."""
    db = KnowledgeDB(tmp_path / "fresh.db")
    conn = db._get_conn()
    for table, column in _SCHEMA_STRUCTURAL_SENTINELS:
        cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        assert column in cols, f"{table}.{column} missing after construction"


# --- WI-7611: projects.authorization -------------------------------------


def test_fresh_database_carries_authorization_defaulting_to_authorized(tmp_path: Path) -> None:
    """A fresh database gets the column from SCHEMA_SQL, defaulting to authorized.

    Owner decision DELIB-20260831060012: new projects are created ``authorized``.
    """
    conn = KnowledgeDB(tmp_path / "fresh.db")._get_conn()
    cols = {row[1] for row in conn.execute("PRAGMA table_info(projects)").fetchall()}
    assert "authorization" in cols

    conn.execute(
        "INSERT INTO projects (id, version, name, changed_by, changed_at, change_reason) "
        "VALUES ('PROJECT-TEST-DEFAULT', 1, 'default probe', 'test', '2026-09-03', 'probe')"
    )
    value = conn.execute("SELECT authorization FROM projects WHERE id = 'PROJECT-TEST-DEFAULT'").fetchone()[0]
    assert value == "authorized"


def test_authorization_holds_only_the_two_canonical_values(tmp_path: Path) -> None:
    """No third state exists.

    The field replaces an object model whose status enum carried five values
    (active, inactive, completed, revoked, superseded). Collapsing to two is the
    substance of the correction, so a drifting third value is a real regression.
    """
    assert {"authorized", "not authorized"} == _VALID_AUTHORIZATION_VALUES

    conn = KnowledgeDB(tmp_path / "values.db")._get_conn()
    observed = {
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT authorization FROM projects WHERE authorization IS NOT NULL"
        ).fetchall()
    }
    assert observed <= _VALID_AUTHORIZATION_VALUES


def test_authorization_readers_agree_with_the_canonical_values() -> None:
    """Readers of the authorization field use only the two canonical values.

    This assertion replaces an ordering guard that has expired. WI-7611 added the
    field ahead of the specification correction, and asserted that *no* consumer
    read it, because while
    ``GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`` still named an authorization
    *object* as the sole bounded grant, a reader would have created two competing
    grants at once.

    That premise is void. The specification was amended to v5 under WI-7673 --
    *"Authorization is a field on the project row; no authorization instrument is
    normative"* -- so the field now **is** the authority and reading it is
    conformant rather than premature. Renaming the old assertion forward would
    have carried a contract the canonical row denies, under a name that made it
    look deliberate.

    What remains worth guarding is narrower and still true: a reader must not
    invent a third state. The two-value contract is the substance of the
    correction, and a consumer comparing against anything else is a real
    regression.
    """
    package_root = Path(__file__).resolve().parents[2] / "groundtruth-kb" / "src" / "groundtruth_kb"
    stray: list[str] = []
    for source in package_root.rglob("*.py"):
        if source.name == "db.py":
            continue  # the declaring module
        text = source.read_text(encoding="utf-8", errors="replace")
        if "authorization" not in text:
            continue
        for literal in re.findall(r"""authorization\s*==\s*["']([^"']+)["']""", text):
            if literal not in _VALID_AUTHORIZATION_VALUES:
                stray.append(f"{source.relative_to(package_root).as_posix()}: {literal!r}")
    assert stray == [], f"authorization compared against non-canonical values: {stray}"


def test_the_retired_column_name_is_gone_from_the_platform() -> None:
    """The rename is complete on the GT-KB side, and stops at the adopter boundary.

    ``applications/Agent_Red/`` has its own unrelated ``authorization`` -- tenant
    activation, not project authorization -- and renaming it would break the
    reference adopter. That exclusion is asserted here rather than left to convention.
    """
    repo_root = Path(__file__).resolve().parents[2]
    platform_hits: list[str] = []
    for source in (repo_root / "groundtruth-kb" / "src" / "groundtruth_kb").rglob("*.py"):
        if source.name == "db.py":
            # The declaring module must still name the retired column: Migration 16
            # detects it to rename it, and Migration 14's guard accepts either name
            # so it cannot re-add the field to a pre-rename database.
            continue
        if "activation_status" in source.read_text(encoding="utf-8", errors="replace"):
            platform_hits.append(source.relative_to(repo_root).as_posix())
    assert platform_hits == [], f"retired column name still present in platform source: {platform_hits}"

    adopter = repo_root / "applications" / "Agent_Red"
    if adopter.is_dir():
        preserved = [
            p for p in adopter.rglob("*.py") if "activation_status" in p.read_text(encoding="utf-8", errors="replace")
        ]
        assert preserved, "Agent Red's own authorization must NOT have been renamed by this work"
