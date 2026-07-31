"""Spec-derived tests for the deliberation-search backend doctor check.

The check must read canonical SQLite and ChromaDB state directly, fail loudly
when a bridge-profile semantic-search backend is degraded, and avoid creating a
missing Chroma index merely by probing it.
"""

from __future__ import annotations

import inspect
from pathlib import Path

from groundtruth_kb import db as db_mod
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project import doctor as doctor_mod


def _write_deliberation_db(root: Path, *ids: str) -> None:
    db = KnowledgeDB(root / "groundtruth.db")
    conn = db._get_conn()
    for delib_id in ids:
        conn.execute(
            """INSERT INTO deliberations
               (id, version, source_type, title, summary, content, changed_by, changed_at, change_reason)
               VALUES (?, 1, 'report', ?, 'summary', 'content', 'test', '2026-07-06T00:00:00Z', 'test')""",
            (delib_id, delib_id),
        )
    conn.commit()
    db.close()


def test_missing_chroma_index_fails_without_creating_index(monkeypatch, tmp_path: Path) -> None:
    _write_deliberation_db(tmp_path, "DELIB-READONLY-0001")

    class ForbiddenChroma:
        class PersistentClient:
            def __init__(self, *, path: str) -> None:
                raise AssertionError(f"missing index probe must not open ChromaDB client: {path}")

    monkeypatch.setattr(db_mod, "HAS_CHROMADB", True)
    monkeypatch.setattr(db_mod, "chromadb", ForbiddenChroma)

    before = sorted(path.name for path in tmp_path.iterdir())
    result = doctor_mod._check_deliberation_search_backend(tmp_path)
    after = sorted(path.name for path in tmp_path.iterdir())

    assert result.status == "fail"
    assert "index_path_missing" in result.message
    assert before == after
    assert not (tmp_path / ".groundtruth-chroma").exists()


def test_doctor_bridge_profile_wires_backend_check() -> None:
    source = inspect.getsource(doctor_mod.run_doctor)

    assert "checks.append(_check_deliberation_search_backend(target))" in source
