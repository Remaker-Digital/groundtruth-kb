"""Tests for GFR Slice A PAUTH auto-resolve hint in implementation_authorization.py begin.

Governing decisions: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001.
Work item: WI-5644 (TEST-11689).
"""

from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "implementation_authorization.py"

spec = importlib.util.spec_from_file_location("implementation_authorization", SCRIPT_PATH)
assert spec is not None
auth_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["implementation_authorization"] = auth_module
spec.loader.exec_module(auth_module)


@pytest.fixture(autouse=True)
def _select_fixture_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GTKB_HARNESS_NAME", "fixture")


def _create_pauth_db(
    project_root: Path,
    *,
    pauth_id: str = "PAUTH-TEST",
    work_item_ids: list[str] | None = None,
    project_id: str = "PROJECT-TEST",
) -> Path:
    db_path = project_root / "groundtruth.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS current_project_authorizations (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            status TEXT NOT NULL,
            version INTEGER DEFAULT 1,
            name TEXT,
            scope TEXT,
            allowed_mutation_classes TEXT,
            forbidden_operations TEXT,
            included_work_item_ids TEXT,
            excluded_work_item_ids TEXT,
            included_spec_ids TEXT,
            excluded_spec_ids TEXT,
            owner_decision_deliberation_id TEXT,
            expires_at TEXT,
            supersedes TEXT,
            superseded_by TEXT,
            change_reason TEXT,
            created_at TEXT,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT,
            status TEXT DEFAULT 'active',
            version INTEGER DEFAULT 1
        );
        """
    )
    conn.execute("INSERT OR REPLACE INTO projects VALUES (?, ?, 'active', 1)", (project_id, project_id))
    conn.execute(
        "INSERT OR REPLACE INTO current_project_authorizations (id, project_id, status, included_work_item_ids, allowed_mutation_classes) VALUES (?, ?, 'active', ?, ?)",
        (
            pauth_id,
            project_id,
            json.dumps(work_item_ids or []),
            json.dumps(["source", "test", "config"]),
        ),
    )
    conn.commit()
    conn.close()
    return db_path


class TestSuggestPauthForWorkItem:
    """Finding 2.3: _suggest_pauth_for_work_item should find matching PAUTHs."""

    def test_returns_pauth_when_work_item_matches(self, tmp_path: Path) -> None:
        _create_pauth_db(tmp_path, pauth_id="PAUTH-MATCH", work_item_ids=["WI-9999"])
        result = auth_module._suggest_pauth_for_work_item(tmp_path, "WI-9999")
        assert "PAUTH-MATCH" in result

    def test_returns_empty_when_no_match(self, tmp_path: Path) -> None:
        _create_pauth_db(tmp_path, pauth_id="PAUTH-NOMATCH", work_item_ids=["WI-1111"])
        result = auth_module._suggest_pauth_for_work_item(tmp_path, "WI-9999")
        assert result == []

    def test_returns_empty_when_work_item_id_is_none(self, tmp_path: Path) -> None:
        _create_pauth_db(tmp_path, pauth_id="PAUTH-NULL", work_item_ids=["WI-1111"])
        result = auth_module._suggest_pauth_for_work_item(tmp_path, None)
        assert result == []

    def test_returns_empty_when_no_db(self, tmp_path: Path) -> None:
        result = auth_module._suggest_pauth_for_work_item(tmp_path, "WI-9999")
        assert result == []
