"""Tests for DCL-SOT-REGISTRY-RECORD-SCHEMA-001 v2 forbidden_substitutes column.

Verifies (a) loader accepts records with the column populated, (b) loader accepts
records without it, (c) loader rejects records where the value is not a
list-of-strings, (d) projection round-trip preserves the column verbatim per
DCL-SOT-REGISTRY-PROJECTION-PARITY-001.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from groundtruth_kb.project.sot_registry import (
    InvalidSoTRecord,
    load_projection,
    load_toml,
    sync_projection,
)


def _write_toml(tmp_path: Path, *, forbidden: str = "") -> Path:
    base = """\
[[artifacts]]
id = "sot-registry-toml"
domain = "control_surface"
lifecycle = "active"
storage_path = "config/registry/sot-artifacts.toml"
authority_spec_id = "GOV-PLATFORM-SOT-REGISTRY-001"
mutation_api = "Edit config/registry/sot-artifacts.toml + gt registry sync"
versioning_policy = "git_tracked"
backup_policy = "git_tracked"
health_check_function = "_check_sot_registry_completeness"
owner_role = "owner_only"
"""
    if forbidden:
        base += forbidden + "\n"
    path = tmp_path / "registry.toml"
    path.write_text(base, encoding="utf-8")
    return path


def test_loader_accepts_populated_forbidden_substitutes(tmp_path: Path) -> None:
    path = _write_toml(tmp_path, forbidden='forbidden_substitutes = [".claude/rules/foo.md", "memory/bar.md"]')
    records = load_toml(path)
    assert len(records) == 1
    assert records[0].forbidden_substitutes == (".claude/rules/foo.md", "memory/bar.md")


def test_loader_accepts_missing_forbidden_substitutes(tmp_path: Path) -> None:
    path = _write_toml(tmp_path)
    records = load_toml(path)
    assert len(records) == 1
    assert records[0].forbidden_substitutes == ()


def test_loader_accepts_empty_forbidden_substitutes(tmp_path: Path) -> None:
    path = _write_toml(tmp_path, forbidden="forbidden_substitutes = []")
    records = load_toml(path)
    assert len(records) == 1
    assert records[0].forbidden_substitutes == ()


def test_loader_rejects_non_list_forbidden_substitutes(tmp_path: Path) -> None:
    path = _write_toml(tmp_path, forbidden='forbidden_substitutes = "just-a-string"')
    with pytest.raises((InvalidSoTRecord, TypeError, ValueError)):
        load_toml(path)


def _init_db(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE sot_artifacts (
                id TEXT NOT NULL,
                version INTEGER NOT NULL,
                domain TEXT NOT NULL,
                lifecycle TEXT NOT NULL,
                storage_path TEXT NOT NULL,
                authority_spec_id TEXT NOT NULL,
                mutation_api TEXT NOT NULL,
                versioning_policy TEXT NOT NULL,
                backup_policy TEXT NOT NULL,
                health_check_function TEXT,
                owner_role TEXT NOT NULL,
                depends_on TEXT,
                forbidden_substitutes TEXT,
                notes TEXT,
                changed_by TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                change_reason TEXT NOT NULL,
                PRIMARY KEY (id, version)
            );
            CREATE VIEW current_sot_artifacts AS
            SELECT a.* FROM sot_artifacts a
            INNER JOIN (SELECT id, MAX(version) AS max_v FROM sot_artifacts GROUP BY id) m
            ON a.id = m.id AND a.version = m.max_v;
            """
        )
        conn.commit()
    finally:
        conn.close()


def test_projection_roundtrip_preserves_forbidden_substitutes(tmp_path: Path) -> None:
    toml_path = _write_toml(tmp_path, forbidden='forbidden_substitutes = [".claude/rules/foo.md", "memory/bar.md"]')
    db_path = tmp_path / "test.db"
    _init_db(db_path)
    records = load_toml(toml_path)
    report = sync_projection(records, db_path)
    assert report.inserted == ("sot-registry-toml",)
    projection = load_projection(db_path)
    assert len(projection) == 1
    assert projection[0].forbidden_substitutes == (".claude/rules/foo.md", "memory/bar.md")


def test_projection_roundtrip_empty_substitutes(tmp_path: Path) -> None:
    toml_path = _write_toml(tmp_path)
    db_path = tmp_path / "test.db"
    _init_db(db_path)
    records = load_toml(toml_path)
    sync_projection(records, db_path)
    projection = load_projection(db_path)
    assert projection[0].forbidden_substitutes == ()
