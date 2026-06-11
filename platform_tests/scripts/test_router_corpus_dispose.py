"""Tests for the Stage 2 router-corpus disposition tool."""

from __future__ import annotations

import ast
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

from scripts.hygiene import router_corpus_dispose as dispose  # noqa: E402


def _item(
    item_id: str,
    *,
    label: str = dispose.LABEL_RETIRE_UNAPPROVED_NOISE,
    scope: str = dispose.PLATFORM_SCOPE,
    approval_state: str = "unapproved",
) -> dict:
    return {
        "id": item_id,
        "label": label,
        "scope": scope,
        "router_generated": True,
        "approval_state": approval_state,
    }


def _write_run(
    benchmarks_dir: Path,
    run_id: str,
    items: list[dict],
    *,
    complete: bool = True,
    mismatch: bool = False,
) -> Path:
    run_dir = benchmarks_dir / run_id
    run_dir.mkdir(parents=True)
    if complete:
        (run_dir / "run.json").write_text(
            json.dumps(
                {
                    "idempotency_key": f"idem-{run_id}",
                    "results": [
                        {
                            "benchmark_id": "backlog_triage",
                            "run_id": f"{run_id}-other" if mismatch else run_id,
                            "source_commit": f"commit-{run_id}",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
    (run_dir / "backlog_triage_items.json").write_text(
        json.dumps({"run_id": run_id, "items": items}),
        encoding="utf-8",
    )
    return run_dir


def _minimal_db(tmp_path: Path, rows: list[dict]) -> Path:
    db_path = tmp_path / "groundtruth.db"
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            "CREATE TABLE current_work_items ("
            "id TEXT, title TEXT, changed_at TEXT, source_spec_id TEXT, priority TEXT, "
            "origin TEXT, component TEXT, resolution_status TEXT)"
        )
        con.executemany(
            "INSERT INTO current_work_items VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    row["id"],
                    row.get("title", f"title {row['id']}"),
                    row.get("changed_at", "2026-06-11T00:00:00+00:00"),
                    row.get("source_spec_id", "GOV-STANDING-BACKLOG-001"),
                    row.get("priority", "P3"),
                    row.get("origin", "hygiene"),
                    row.get("component", "backlog"),
                    row.get("resolution_status", "open"),
                )
                for row in rows
            ],
        )
        con.commit()
    finally:
        con.close()
    return db_path


def _knowledge_db(tmp_path: Path, rows: list[dict]) -> Path:
    db_path = tmp_path / "groundtruth.db"
    db = KnowledgeDB(db_path)
    for row in rows:
        db.insert_work_item(
            row["id"],
            row.get("title", f"title {row['id']}"),
            row.get("origin", "hygiene"),
            row.get("component", "backlog"),
            row.get("resolution_status", "open"),
            "test",
            "seed",
            description=row.get("description", f"description {row['id']}"),
            source_spec_id=row.get("source_spec_id", "GOV-STANDING-BACKLOG-001"),
            source_test_id=row.get("source_test_id"),
            failure_description=row.get("failure_description"),
            priority=row.get("priority", "P3"),
            stage=row.get("stage", "backlogged"),
            approval_state=row.get("approval_state", "unapproved"),
            project_name=row.get("project_name", "PROJECT-GTKB-LO-ADVISORY-ROUTING"),
            subproject_name=row.get("subproject_name", "router"),
            implementation_order=row.get("implementation_order", 10),
            status_detail=row.get("status_detail", "seeded"),
            source_owner_directive=row.get("source_owner_directive", "owner directive"),
            source_deliberation_query=row.get("source_deliberation_query", "query"),
            related_deliberation_ids=row.get("related_deliberation_ids", "[]"),
            related_spec_ids_at_creation=row.get("related_spec_ids_at_creation", '["GOV-STANDING-BACKLOG-001"]'),
            related_bridge_threads=row.get("related_bridge_threads", "[]"),
            depends_on_work_items=row.get("depends_on_work_items", "[]"),
            blocks_work_items=row.get("blocks_work_items", "[]"),
            acceptance_summary=row.get("acceptance_summary", "accept"),
            regression_visibility=row.get("regression_visibility", "visible"),
            completion_evidence=row.get("completion_evidence", ""),
        )
    return db_path


def _approved_batch(path: Path, ids: list[str], run_id: str, auq_id: str = "AUQ-STAGE2-001") -> Path:
    packet = {
        "auq_id": auq_id,
        "manifest_run_id": run_id,
        "idempotency_key": f"idem-{run_id}",
        "ids": ids,
        "batch_hash": dispose.compute_batch_hash(ids, run_id, auq_id),
    }
    path.write_text(json.dumps(packet, sort_keys=True), encoding="utf-8")
    return path


def test_selects_newest_complete_manifest_skipping_partial_and_mismatched(tmp_path: Path) -> None:
    bench = tmp_path / "benchmarks"
    _write_run(bench, "20260611-120000", [_item("WI-1")])
    _write_run(bench, "20260611-130000", [_item("WI-2")], complete=False)
    _write_run(bench, "20260611-140000", [_item("WI-3")], mismatch=True)
    _write_run(bench, "20260611-150000", [_item("WI-4")])

    manifest = dispose.load_latest_manifest(bench)

    assert manifest.run_id == "20260611-150000"
    assert [item["id"] for item in manifest.items] == ["WI-4"]


def test_dry_run_enriches_candidates_and_reports_missing_db_rows(tmp_path: Path) -> None:
    bench = tmp_path / "benchmarks"
    _write_run(bench, "20260611-150000", [_item("WI-1"), _item("WI-MISSING")])
    db_path = _minimal_db(tmp_path, [{"id": "WI-1", "title": "Enriched title", "priority": "P0"}])

    payload = dispose.build_dry_run(db_path=db_path, benchmarks_dir=bench)

    assert payload["status"] == "defect"
    assert payload["defects"]["missing_current_work_items"] == ["WI-MISSING"]
    assert payload["candidates"][0]["title"] == "Enriched title"
    assert payload["candidates"][0]["source_spec_id"] == "GOV-STANDING-BACKLOG-001"
    assert payload["candidates"][0]["priority"] == "P0"


def test_prepare_batch_writes_packet_and_enforces_size_cap(tmp_path: Path) -> None:
    bench = tmp_path / "benchmarks"
    ids = [f"WI-{i:04d}" for i in range(51)]
    _write_run(bench, "20260611-150000", [_item(wid) for wid in ids])
    db_path = _minimal_db(tmp_path, [{"id": wid} for wid in ids])

    packet = dispose.prepare_batch(tmp_path / "batch.json", db_path=db_path, benchmarks_dir=bench, max_batch_size=50)

    assert len(packet["ids"]) == 50
    assert packet["auq_id"] is None
    with pytest.raises(dispose.DispositionError, match="between 0 and 50"):
        dispose.prepare_batch(tmp_path / "bad.json", db_path=db_path, benchmarks_dir=bench, max_batch_size=51)


def test_apply_refuses_batch_hash_mismatch(tmp_path: Path) -> None:
    bench = tmp_path / "benchmarks"
    _write_run(bench, "20260611-150000", [_item("WI-1")])
    db_path = _knowledge_db(tmp_path, [{"id": "WI-1"}])
    batch = _approved_batch(tmp_path / "batch.json", ["WI-1"], "20260611-150000")
    packet = json.loads(batch.read_text(encoding="utf-8"))
    packet["batch_hash"] = "wrong"
    batch.write_text(json.dumps(packet), encoding="utf-8")

    with pytest.raises(dispose.DispositionError, match="batch hash mismatch"):
        dispose.apply_batch(
            batch_file=batch,
            confirm_manifest="20260611-150000",
            db_path=db_path,
            benchmarks_dir=bench,
        )


def test_apply_refuses_stale_manifest(tmp_path: Path) -> None:
    bench = tmp_path / "benchmarks"
    _write_run(bench, "20260611-140000", [_item("WI-1")])
    _write_run(bench, "20260611-150000", [_item("WI-1")])
    db_path = _knowledge_db(tmp_path, [{"id": "WI-1"}])
    batch = _approved_batch(tmp_path / "batch.json", ["WI-1"], "20260611-140000")

    with pytest.raises(dispose.DispositionError, match="newest complete manifest"):
        dispose.apply_batch(
            batch_file=batch,
            confirm_manifest="20260611-140000",
            db_path=db_path,
            benchmarks_dir=bench,
        )


def test_apply_refuses_unknown_id_not_in_cohort(tmp_path: Path) -> None:
    bench = tmp_path / "benchmarks"
    _write_run(bench, "20260611-150000", [_item("WI-1")])
    db_path = _knowledge_db(tmp_path, [{"id": "WI-1"}, {"id": "WI-X"}])
    batch = _approved_batch(tmp_path / "batch.json", ["WI-X"], "20260611-150000")

    with pytest.raises(dispose.DispositionError, match="not in retire-candidate platform cohort"):
        dispose.apply_batch(
            batch_file=batch,
            confirm_manifest="20260611-150000",
            db_path=db_path,
            benchmarks_dir=bench,
        )


def test_refined_batch_applies_only_subset_and_preserves_fields(tmp_path: Path) -> None:
    bench = tmp_path / "benchmarks"
    _write_run(bench, "20260611-150000", [_item("WI-1"), _item("WI-2")])
    db_path = _knowledge_db(
        tmp_path,
        [
            {"id": "WI-1", "title": "Keep my fields", "priority": "P0"},
            {"id": "WI-2", "title": "Excluded", "priority": "P1"},
        ],
    )
    db = KnowledgeDB(db_path)
    before = db.get_work_item("WI-1")
    batch = _approved_batch(tmp_path / "batch.json", ["WI-1"], "20260611-150000")

    result = dispose.apply_batch(
        batch_file=batch,
        confirm_manifest="20260611-150000",
        db_path=db_path,
        benchmarks_dir=bench,
        changed_by="test",
    )

    assert result["updated_ids"] == ["WI-1"]
    after = db.get_work_item("WI-1")
    excluded = db.get_work_item("WI-2")
    assert after["resolution_status"] == "wont_fix"
    assert excluded["resolution_status"] == "open"
    for field in (
        "title",
        "description",
        "origin",
        "component",
        "priority",
        "project_name",
        "subproject_name",
        "related_spec_ids_at_creation",
        "related_bridge_threads",
        "related_deliberation_ids",
        "source_spec_id",
        "source_owner_directive",
        "source_deliberation_query",
        "acceptance_summary",
        "regression_visibility",
        "approval_state",
    ):
        assert after[field] == before[field], field


def test_apply_refuses_non_open_id(tmp_path: Path) -> None:
    bench = tmp_path / "benchmarks"
    _write_run(bench, "20260611-150000", [_item("WI-1")])
    db_path = _knowledge_db(tmp_path, [{"id": "WI-1", "resolution_status": "wont_fix"}])
    batch = _approved_batch(tmp_path / "batch.json", ["WI-1"], "20260611-150000")

    with pytest.raises(dispose.DispositionError, match="no longer open"):
        dispose.apply_batch(
            batch_file=batch,
            confirm_manifest="20260611-150000",
            db_path=db_path,
            benchmarks_dir=bench,
        )


def test_agent_red_scope_items_are_excluded_from_cohort(tmp_path: Path) -> None:
    bench = tmp_path / "benchmarks"
    _write_run(bench, "20260611-150000", [_item("WI-1"), _item("WI-AR", scope="agent_red")])
    db_path = _minimal_db(tmp_path, [{"id": "WI-1"}, {"id": "WI-AR"}])

    payload = dispose.build_dry_run(db_path=db_path, benchmarks_dir=bench)

    assert [item["id"] for item in payload["candidates"]] == ["WI-1"]


def test_dry_run_is_deterministic_and_read_only(tmp_path: Path) -> None:
    bench = tmp_path / "benchmarks"
    _write_run(bench, "20260611-150000", [_item("WI-2"), _item("WI-1")])
    db_path = _minimal_db(tmp_path, [{"id": "WI-1"}, {"id": "WI-2"}])

    con = sqlite3.connect(db_path)
    before = con.execute("SELECT COUNT(*) FROM current_work_items").fetchone()[0]
    con.close()
    first = dispose.build_dry_run(db_path=db_path, benchmarks_dir=bench)
    second = dispose.build_dry_run(db_path=db_path, benchmarks_dir=bench)
    con = sqlite3.connect(db_path)
    after = con.execute("SELECT COUNT(*) FROM current_work_items").fetchone()[0]
    con.close()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert after == before


def test_apply_uses_update_work_item_and_default_path_uses_read_only_uri() -> None:
    tree = ast.parse((REPO_ROOT / "scripts" / "hygiene" / "router_corpus_dispose.py").read_text(encoding="utf-8"))
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Attribute) and node.attr == "update_work_item"]
    assert len(calls) == 1
    text = (REPO_ROOT / "scripts" / "hygiene" / "router_corpus_dispose.py").read_text(encoding="utf-8")
    assert "mode=ro" in text
