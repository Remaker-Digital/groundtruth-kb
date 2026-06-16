"""Platform tests for benchmark: deliberation_recall.

Each test exercises one independent contract: basic run, idempotency,
dimension keys, empty-window behavior, and output-writing.
"""

# ruff: noqa: E402  # sys.path.insert(REPO) must precede scripts.benchmarks import

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.benchmarks import deliberation_recall as bm
from scripts.benchmarks.common import BenchmarkResult, write_run_outputs

PAST = "2024-01-01T00:00:00+00:00"
FUTURE = "2027-01-01T00:00:00+00:00"
EMPTY_START = "1990-01-01T00:00:00+00:00"
EMPTY_END = "1990-01-02T00:00:00+00:00"


def _write_fixture_db(project_root: Path) -> Path:
    db_path = project_root / "groundtruth.db"
    with sqlite3.connect(str(db_path)) as con:
        con.execute(
            """CREATE TABLE deliberations (
                id TEXT NOT NULL,
                version INTEGER NOT NULL,
                spec_id TEXT,
                work_item_id TEXT,
                source_type TEXT NOT NULL,
                source_ref TEXT,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                content TEXT NOT NULL,
                outcome TEXT,
                changed_by TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                change_reason TEXT NOT NULL
            )"""
        )
        rows = [
            (
                "DELIB-0005",
                1,
                "SPEC-0005",
                "WI-0005",
                "owner_conversation",
                "fixture:unique",
                "Unique fixture recall",
                "Unique fixture recall",
                "Unique fixture recall content",
                "owner_decision",
                "test",
                "2026-01-05T00:00:00+00:00",
                "fixture",
            ),
            (
                "DELIB-0004",
                1,
                None,
                None,
                "owner_conversation",
                "fixture:shared-4",
                "Shared recall phrase",
                "Shared recall phrase",
                "Newest shared recall phrase content",
                "owner_decision",
                "test",
                "2026-01-04T00:00:00+00:00",
                "fixture",
            ),
            (
                "DELIB-0003",
                1,
                None,
                None,
                "owner_conversation",
                "fixture:shared-3",
                "Shared recall phrase",
                "Shared recall phrase",
                "Third shared recall phrase content",
                "owner_decision",
                "test",
                "2026-01-03T00:00:00+00:00",
                "fixture",
            ),
            (
                "DELIB-0002",
                1,
                None,
                None,
                "owner_conversation",
                "fixture:shared-2",
                "Shared recall phrase",
                "Shared recall phrase",
                "Second shared recall phrase content",
                "owner_decision",
                "test",
                "2026-01-02T00:00:00+00:00",
                "fixture",
            ),
            (
                "DELIB-0001",
                1,
                None,
                None,
                "owner_conversation",
                "fixture:shared-1",
                "Shared recall phrase",
                "Shared recall phrase",
                "Oldest shared recall phrase content",
                "owner_decision",
                "test",
                "2026-01-01T00:00:00+00:00",
                "fixture",
            ),
            (
                "DELIB-9999",
                1,
                None,
                None,
                "loyal_opposition_insight",
                "fixture:excluded",
                "Excluded insight",
                "Excluded insight",
                "Not an owner conversation",
                "advisory",
                "test",
                "2026-01-06T00:00:00+00:00",
                "fixture",
            ),
        ]
        con.executemany(
            """INSERT INTO deliberations (
                id,
                version,
                spec_id,
                work_item_id,
                source_type,
                source_ref,
                title,
                summary,
                content,
                outcome,
                changed_by,
                changed_at,
                change_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
    return project_root


def test_deliberation_recall_basic_run(tmp_path):
    project_root = _write_fixture_db(tmp_path)
    result = bm.run(PAST, FUTURE, project_root)
    assert isinstance(result, BenchmarkResult)
    assert result.benchmark_id == bm.BENCHMARK_ID
    assert result.window_start == PAST
    assert result.window_end == FUTURE
    assert result.value == 0.8
    assert isinstance(result.dimensions, dict)
    assert result.dimensions["sample_size"] == 5
    assert result.dimensions["hits_at_3"] == 4
    assert result.dimensions["search_failure_rate"] == 0.0


def test_deliberation_recall_idempotency_dimensions(tmp_path):
    project_root = _write_fixture_db(tmp_path)
    a = bm.run(PAST, FUTURE, project_root)
    b = bm.run(PAST, FUTURE, project_root)
    assert a.dimensions == b.dimensions
    assert a.value == b.value


def test_deliberation_recall_expected_dimension_keys(tmp_path):
    project_root = _write_fixture_db(tmp_path)
    result = bm.run(PAST, FUTURE, project_root)
    for k in ("sample_size", "hits_at_3", "search_failure_rate"):
        assert k in result.dimensions


def test_deliberation_recall_empty_window_graceful(tmp_path):
    project_root = _write_fixture_db(tmp_path)
    result = bm.run(EMPTY_START, EMPTY_END, project_root)
    assert isinstance(result, BenchmarkResult)
    assert isinstance(result.value, (int, float))
    assert result.dimensions["sample_size"] == 0


def test_deliberation_recall_output_writing(tmp_path):
    project_root = _write_fixture_db(tmp_path)
    result = bm.run(PAST, FUTURE, project_root)
    paths = write_run_outputs(result.run_id, [result], project_root=tmp_path)
    assert paths["json_path"].exists()
    assert paths["markdown_path"].exists()
    payload = json.loads(paths["json_path"].read_text(encoding="utf-8"))
    assert payload["run_id"] == result.run_id
    assert "idempotency_key" in payload
    assert len(payload["results"]) == 1


def test_deliberation_recall_default_avoids_live_semantic_search(tmp_path, monkeypatch):
    project_root = _write_fixture_db(tmp_path)

    def fail_if_loaded(root):
        raise AssertionError(f"live semantic search loaded for {root}")

    monkeypatch.setattr(bm, "_load_db", fail_if_loaded)
    result = bm.run(PAST, FUTURE, project_root)
    assert result.dimensions["sample_size"] == 5


def test_deliberation_recall_sqlite_miss(tmp_path):
    project_root = _write_fixture_db(tmp_path)
    matches = bm._search_sqlite_deliberations(
        project_root / "groundtruth.db",
        "phrase absent from fixture",
    )
    assert matches == []
