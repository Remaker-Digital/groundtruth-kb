"""Tests for the Stage 3 advisory candidate promotion tool."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GTKB_SRC = REPO_ROOT / "groundtruth-kb" / "src"
for path in (REPO_ROOT, GTKB_SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

from scripts.hygiene import advisory_candidate_promote as promote  # noqa: E402


def _store_path(project_root: Path) -> Path:
    return project_root / ".gtkb-state" / "advisory-candidates" / "candidates.jsonl"


def _append_candidate(
    project_root: Path,
    source_key: str,
    *,
    status: str = "staged",
    title: str | None = None,
    priority: str = "high",
) -> None:
    store = _store_path(project_root)
    store.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "event": status,
        "status": status,
        "source": "dropbox",
        "source_key": source_key,
        "relative_path": f"independent-progress-assessments/CODEX-INSIGHT-DROPBOX/{source_key}",
        "proposed_title": title or f"Route LO advisory: {source_key}",
        "description": f"Description for {source_key}",
        "priority": priority,
        "severity_token": "P1",
        "related_bridge_threads": None,
        "advisory_date": "2026-06-11",
        "origin": "hygiene",
        "component": "backlog",
        "source_spec_id": "GOV-STANDING-BACKLOG-001",
        "recorded_at": "2026-06-11T00:00:00Z",
    }
    with store.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def _events(project_root: Path) -> list[dict]:
    store = _store_path(project_root)
    return [json.loads(line) for line in store.read_text(encoding="utf-8").splitlines() if line.strip()]


def _approved_batch(
    path: Path,
    source_keys: list[str],
    *,
    auq_id: str = "AUQ-STAGE3-001",
    decision: str = "approve",
) -> Path:
    packet = {
        "auq_id": auq_id,
        "source_keys": source_keys,
        "batch_hash": promote.compute_batch_hash(source_keys, auq_id),
    }
    if decision != "approve":
        packet["decision"] = decision
    path.write_text(json.dumps(packet, sort_keys=True), encoding="utf-8")
    return path


def _work_item_rows(db_path: Path) -> list[dict]:
    db = KnowledgeDB(db_path)
    rows = db._get_conn().execute("SELECT * FROM current_work_items ORDER BY id").fetchall()
    return [dict(row) for row in rows]


def test_dry_run_is_deterministic_and_read_only(tmp_path: Path) -> None:
    _append_candidate(tmp_path, "INSIGHTS-2026-06-11-A.md")
    _append_candidate(tmp_path, "INSIGHTS-2026-06-11-B.md", priority="medium")
    _append_candidate(tmp_path, "INSIGHTS-2026-06-11-C.md", status="rejected")
    db_path = tmp_path / "groundtruth.db"
    before = len(_work_item_rows(db_path))

    first = promote.build_dry_run(tmp_path)
    second = promote.build_dry_run(tmp_path)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["candidate_count"] == 2
    assert [item["source_key"] for item in first["candidates"]] == [
        "INSIGHTS-2026-06-11-A.md",
        "INSIGHTS-2026-06-11-B.md",
    ]
    assert len(_work_item_rows(db_path)) == before


def test_prepare_batch_writes_packet_and_enforces_size_cap(tmp_path: Path) -> None:
    keys = [f"INSIGHTS-2026-06-11-{index:02d}.md" for index in range(51)]
    for key in keys:
        _append_candidate(tmp_path, key)

    packet = promote.prepare_batch(tmp_path / "batch.json", project_root=tmp_path, max_batch_size=50)

    assert len(packet["source_keys"]) == 50
    assert packet["auq_id"] is None
    assert packet["batch_hash"] == promote.compute_batch_hash(packet["source_keys"], "")
    with pytest.raises(promote.PromotionError, match="between 0 and 50"):
        promote.prepare_batch(tmp_path / "bad.json", project_root=tmp_path, max_batch_size=51)


def test_apply_refuses_batch_hash_mismatch(tmp_path: Path) -> None:
    _append_candidate(tmp_path, "INSIGHTS-2026-06-11-A.md")
    batch = _approved_batch(tmp_path / "batch.json", ["INSIGHTS-2026-06-11-A.md"])
    packet = json.loads(batch.read_text(encoding="utf-8"))
    packet["batch_hash"] = "wrong"
    batch.write_text(json.dumps(packet), encoding="utf-8")

    with pytest.raises(promote.PromotionError, match="batch hash mismatch"):
        promote.apply_batch(batch_file=batch, project_root=tmp_path, db_path=tmp_path / "groundtruth.db")


def test_apply_refuses_unknown_source_key(tmp_path: Path) -> None:
    _append_candidate(tmp_path, "INSIGHTS-2026-06-11-A.md")
    batch = _approved_batch(tmp_path / "batch.json", ["INSIGHTS-2026-06-11-UNKNOWN.md"])

    with pytest.raises(promote.PromotionError, match="unknown source_key"):
        promote.apply_batch(batch_file=batch, project_root=tmp_path, db_path=tmp_path / "groundtruth.db")


def test_apply_refuses_non_staged_source_key(tmp_path: Path) -> None:
    _append_candidate(tmp_path, "INSIGHTS-2026-06-11-A.md", status="promoted")
    batch = _approved_batch(tmp_path / "batch.json", ["INSIGHTS-2026-06-11-A.md"])

    with pytest.raises(promote.PromotionError, match="not staged"):
        promote.apply_batch(batch_file=batch, project_root=tmp_path, db_path=tmp_path / "groundtruth.db")


def test_apply_refuses_oversize_batch(tmp_path: Path) -> None:
    keys = [f"INSIGHTS-2026-06-11-{index:02d}.md" for index in range(51)]
    batch = _approved_batch(tmp_path / "batch.json", keys)

    with pytest.raises(promote.PromotionError, match="maximum is 50"):
        promote.apply_batch(batch_file=batch, project_root=tmp_path, db_path=tmp_path / "groundtruth.db")


def test_apply_promotes_with_auq_and_hash_evidence(tmp_path: Path) -> None:
    source_key = "INSIGHTS-2026-06-11-A.md"
    _append_candidate(tmp_path, source_key)
    batch = _approved_batch(tmp_path / "batch.json", [source_key], auq_id="AUQ-STAGE3-PROMOTE")
    packet = json.loads(batch.read_text(encoding="utf-8"))

    result = promote.apply_batch(
        batch_file=batch,
        project_root=tmp_path,
        db_path=tmp_path / "groundtruth.db",
        changed_by="test",
    )

    assert result["promoted_count"] == 1
    assert result["promoted_source_keys"] == [source_key]
    rows = _work_item_rows(tmp_path / "groundtruth.db")
    assert len(rows) == 1
    row = rows[0]
    assert row["resolution_status"] == "open"
    assert row["origin"] == "hygiene"
    assert row["component"] == "backlog"
    assert row["source_spec_id"] == "GOV-STANDING-BACKLOG-001"
    assert row["approval_state"] == "auq_resolved"
    assert row["related_deliberation_ids"] == source_key
    assert "AUQ-STAGE3-PROMOTE" in row["change_reason"]
    assert packet["batch_hash"] in row["change_reason"]
    current = promote._latest_candidates_with_order(tmp_path)[0]
    assert current["status"] == "promoted"
    assert current["promoted_work_item_id"] == row["id"]


def test_refine_promotes_subset(tmp_path: Path) -> None:
    _append_candidate(tmp_path, "INSIGHTS-2026-06-11-A.md")
    _append_candidate(tmp_path, "INSIGHTS-2026-06-11-B.md")
    batch = _approved_batch(tmp_path / "batch.json", ["INSIGHTS-2026-06-11-B.md"], decision="refine")

    result = promote.apply_batch(batch_file=batch, project_root=tmp_path, db_path=tmp_path / "groundtruth.db")

    assert result["decision"] == "refine"
    assert result["promoted_source_keys"] == ["INSIGHTS-2026-06-11-B.md"]
    statuses = {
        candidate["source_key"]: candidate["status"] for candidate in promote._latest_candidates_with_order(tmp_path)
    }
    assert statuses == {
        "INSIGHTS-2026-06-11-A.md": "staged",
        "INSIGHTS-2026-06-11-B.md": "promoted",
    }


def test_reject_promotes_nothing_and_marks_rejected(tmp_path: Path) -> None:
    source_key = "INSIGHTS-2026-06-11-A.md"
    _append_candidate(tmp_path, source_key)
    batch = _approved_batch(tmp_path / "batch.json", [source_key], decision="reject")

    result = promote.apply_batch(batch_file=batch, project_root=tmp_path, db_path=tmp_path / "groundtruth.db")

    assert result["decision"] == "reject"
    assert result["promoted_count"] == 0
    assert len(_work_item_rows(tmp_path / "groundtruth.db")) == 0
    assert promote._latest_candidates_with_order(tmp_path)[0]["status"] == "rejected"


def test_double_apply_refused(tmp_path: Path) -> None:
    source_key = "INSIGHTS-2026-06-11-A.md"
    _append_candidate(tmp_path, source_key)
    batch = _approved_batch(tmp_path / "batch.json", [source_key])

    promote.apply_batch(batch_file=batch, project_root=tmp_path, db_path=tmp_path / "groundtruth.db")

    with pytest.raises(promote.PromotionError, match="not staged"):
        promote.apply_batch(batch_file=batch, project_root=tmp_path, db_path=tmp_path / "groundtruth.db")


def test_promote_uses_insert_work_item_only_and_default_is_read_only(tmp_path: Path) -> None:
    script = REPO_ROOT / "scripts" / "hygiene" / "advisory_candidate_promote.py"
    tree = ast.parse(script.read_text(encoding="utf-8"))
    insert_calls = [
        node for node in ast.walk(tree) if isinstance(node, ast.Attribute) and node.attr == "insert_work_item"
    ]
    update_calls = [
        node for node in ast.walk(tree) if isinstance(node, ast.Attribute) and node.attr == "update_work_item"
    ]
    assert len(insert_calls) == 1
    assert update_calls == []

    _append_candidate(tmp_path, "INSIGHTS-2026-06-11-A.md")
    before_events = _events(tmp_path)
    before_rows = len(_work_item_rows(tmp_path / "groundtruth.db"))
    promote.build_dry_run(tmp_path)
    assert _events(tmp_path) == before_events
    assert len(_work_item_rows(tmp_path / "groundtruth.db")) == before_rows
