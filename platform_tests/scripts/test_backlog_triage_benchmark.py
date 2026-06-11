"""Tests for the backlog_triage Stage 0 benchmark.

Covers each deterministic signal classifier, the platform/Agent-Red partition,
the conservative disposition labels, the standard run.json/summary.md output
contract plus the per-item companion file, determinism, and the read-only /
no-mutation guarantees. Also a regression assert that registering
``backlog_triage`` leaves every benchmark module importable with a ``run``
entry point (Codex -004 GO implementation note 3).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import ast
import importlib
import json
import sqlite3
from pathlib import Path

import pytest

from scripts.benchmarks import backlog_triage, cli

WINDOW_START = "2026-01-01T00:00:00+00:00"
WINDOW_END = "2026-06-11T00:00:00+00:00"

_WI_COLUMNS = (
    "id",
    "version",
    "resolution_status",
    "changed_by",
    "changed_at",
    "title",
    "description",
    "acceptance_summary",
    "approval_state",
    "origin",
    "component",
    "related_bridge_threads",
    "related_spec_ids_at_creation",
    "source_spec_id",
    "source_owner_directive",
    "project_name",
)


def _wi(**overrides):
    base = {
        "id": "WI-0000",
        "version": 1,
        "resolution_status": "open",
        "changed_by": "prime-builder/claude",
        "changed_at": "2026-06-01T00:00:00+00:00",
        "title": "title",
        "description": "description",
        "acceptance_summary": "",
        "approval_state": "unapproved",
        "origin": "hygiene",
        "component": "backlog",
        "related_bridge_threads": None,
        "related_spec_ids_at_creation": None,
        "source_spec_id": None,
        "source_owner_directive": None,
        "project_name": None,
    }
    base.update(overrides)
    return tuple(base[c] for c in _WI_COLUMNS)


def _build_fixture(tmp_path: Path, work_items, memberships=()):
    db = tmp_path / "groundtruth.db"
    con = sqlite3.connect(db)
    try:
        con.execute("CREATE TABLE current_work_items (" + ", ".join(f"{c} TEXT" for c in _WI_COLUMNS) + ")")
        con.executemany(
            "INSERT INTO current_work_items VALUES (" + ", ".join("?" for _ in _WI_COLUMNS) + ")",
            work_items,
        )
        con.execute(
            "CREATE TABLE current_project_work_item_memberships (work_item_id TEXT, project_id TEXT, status TEXT)"
        )
        con.executemany(
            "INSERT INTO current_project_work_item_memberships VALUES (?, ?, ?)",
            memberships,
        )
        con.commit()
    finally:
        con.close()
    return tmp_path


def _items_by_id(result, root: Path):
    items_path = root / ".gtkb-state" / "benchmarks" / result.run_id / "backlog_triage_items.json"
    payload = json.loads(items_path.read_text(encoding="utf-8"))
    return {i["id"]: i for i in payload["items"]}


@pytest.fixture
def sample_root(tmp_path):
    work_items = [
        _wi(id="WI-ROUTER-NOISE", changed_by="advisory-backlog-router/1.0", title="noise a", description="d1"),
        _wi(
            id="WI-ROUTER-SIGNAL",
            changed_by="advisory-backlog-router/1.0",
            title="router with bridge",
            description="d2",
            related_bridge_threads='["bridge/x-001.md"]',
        ),
        # Router item carrying ONLY the boilerplate source_spec_id stamp: must NOT
        # be treated as signal-bearing (the real-corpus defeat case).
        _wi(
            id="WI-ROUTER-SPECSTAMP",
            changed_by="advisory-backlog-router/1.0",
            source_spec_id="GOV-STANDING-BACKLOG-001",
            title="stamped noise",
            description="d8",
        ),
        _wi(id="WI-DUP-A", title="same title", description="same body"),
        _wi(id="WI-DUP-B", title="same title", description="same body"),
        _wi(id="WI-OWNER", source_owner_directive="owner asked for this", title="owner item", description="d3"),
        _wi(id="WI-AR-FIELD", project_name="AGENT-RED-TEST-COVERAGE-GAPS", title="ar", description="d4"),
        _wi(id="WI-AR-MEMBER", title="ar via membership", description="d5"),
        _wi(id="WI-PLATFORM-MEMBER", title="plat", description="d6"),
        _wi(id="WI-TERMINAL", resolution_status="wont_fix", title="done", description="d7"),
    ]
    memberships = [
        ("WI-AR-MEMBER", "PROJECT-AGENT-RED-FOO", "active"),
        ("WI-PLATFORM-MEMBER", "PROJECT-GTKB-RELIABILITY-FIXES", "active"),
    ]
    return _build_fixture(tmp_path, work_items, memberships)


def test_open_filter_excludes_terminal(sample_root):
    result = backlog_triage.run(WINDOW_START, WINDOW_END, sample_root)
    assert result.value == 9.0  # 10 rows, 1 terminal (wont_fix)
    assert result.dimensions["total_open"] == 9
    assert result.dimensions["total_nonopen"] == 1
    assert result.dimensions["nonopen_by_status"] == {"wont_fix": 1}


def test_router_and_signal_classification(sample_root):
    result = backlog_triage.run(WINDOW_START, WINDOW_END, sample_root)
    items = _items_by_id(result, sample_root)
    # Router + no signal + unapproved -> retire_candidate_unapproved_noise.
    assert items["WI-ROUTER-NOISE"]["router_generated"] is True
    assert items["WI-ROUTER-NOISE"]["signal_bearing"] is False
    assert items["WI-ROUTER-NOISE"]["label"] == "retire_candidate_unapproved_noise"
    # Router but bridge-linked -> signal-bearing wins, keep_signal.
    assert items["WI-ROUTER-SIGNAL"]["router_generated"] is True
    assert items["WI-ROUTER-SIGNAL"]["bridge_linked"] is True
    assert items["WI-ROUTER-SIGNAL"]["label"] == "keep_signal"
    # Owner-sourced -> signal-bearing.
    assert items["WI-OWNER"]["owner_sourced"] is True
    assert items["WI-OWNER"]["label"] == "keep_signal"


def test_boilerplate_source_spec_id_is_not_a_signal(sample_root):
    """The advisory-router's source_spec_id stamp must not confer signal."""
    result = backlog_triage.run(WINDOW_START, WINDOW_END, sample_root)
    items = _items_by_id(result, sample_root)
    item = items["WI-ROUTER-SPECSTAMP"]
    assert item["has_source_spec_id"] is True  # surfaced informationally
    assert item["spec_linked"] is False  # but NOT counted as a spec link
    assert item["signal_bearing"] is False
    assert item["label"] == "retire_candidate_unapproved_noise"


def test_duplicate_group_resolution(sample_root):
    result = backlog_triage.run(WINDOW_START, WINDOW_END, sample_root)
    items = _items_by_id(result, sample_root)
    # Canonical (lowest id) is not flagged; the other is the duplicate candidate.
    assert items["WI-DUP-A"]["duplicate_of"] is None
    assert items["WI-DUP-A"]["label"] == "review"
    assert items["WI-DUP-B"]["duplicate_of"] == "WI-DUP-A"
    assert items["WI-DUP-B"]["label"] == "retire_candidate_duplicate"
    assert result.dimensions["duplicate_groups"] == 1
    assert result.dimensions["duplicate_items"] == 1


def test_scope_partition_platform_vs_agent_red(sample_root):
    result = backlog_triage.run(WINDOW_START, WINDOW_END, sample_root)
    items = _items_by_id(result, sample_root)
    assert items["WI-AR-FIELD"]["scope"] == "agent_red"  # via project_name field
    assert items["WI-AR-MEMBER"]["scope"] == "agent_red"  # via membership project id
    assert items["WI-PLATFORM-MEMBER"]["scope"] == "platform"
    assert result.dimensions["by_scope"]["agent_red"] == 2


def test_project_name_membership_consistency(sample_root):
    result = backlog_triage.run(WINDOW_START, WINDOW_END, sample_root)
    items = _items_by_id(result, sample_root)
    # Empty field + no membership -> consistent.
    assert items["WI-ROUTER-NOISE"]["project_name_consistent"] is True
    # Empty field + has membership -> inconsistent.
    assert items["WI-PLATFORM-MEMBER"]["project_name_consistent"] is False
    assert result.dimensions["project_name_inconsistent"] >= 1


def test_standard_output_contract(sample_root):
    result = backlog_triage.run(WINDOW_START, WINDOW_END, sample_root)
    from scripts.benchmarks.common import write_run_outputs

    paths = write_run_outputs(result.run_id, [result], project_root=sample_root)
    assert paths["json_path"].name == "run.json"
    assert paths["markdown_path"].name == "summary.md"
    run_json = json.loads(paths["json_path"].read_text(encoding="utf-8"))
    bt = next(r for r in run_json["results"] if r["benchmark_id"] == "backlog_triage")
    assert bt["dimensions"]["items_file"] == "backlog_triage_items.json"
    assert bt["dimensions"]["items_count"] == 9
    # The full per-item vectors live in the companion file, not the markdown table.
    md = paths["markdown_path"].read_text(encoding="utf-8")
    assert "backlog_triage" in md


def test_determinism(sample_root):
    a = backlog_triage.run(WINDOW_START, WINDOW_END, sample_root)
    b = backlog_triage.run(WINDOW_START, WINDOW_END, sample_root)
    assert a.value == b.value
    assert a.dimensions == b.dimensions
    items_a = _items_by_id(a, sample_root)
    items_b = _items_by_id(b, sample_root)
    assert items_a == items_b


def test_read_only_row_counts_unchanged(sample_root):
    db = sample_root / "groundtruth.db"
    con = sqlite3.connect(db)
    before = con.execute("SELECT COUNT(*) FROM current_work_items").fetchone()[0]
    con.close()
    backlog_triage.run(WINDOW_START, WINDOW_END, sample_root)
    con = sqlite3.connect(db)
    after = con.execute("SELECT COUNT(*) FROM current_work_items").fetchone()[0]
    con.close()
    assert before == after


def test_no_mutation_ast():
    """The module must not contain any DB-write path."""
    source = Path(backlog_triage.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_attr_calls = {"commit", "executescript", "executemany"}
    forbidden_sql = ("insert ", "update ", "delete ", "replace ", "drop ", "create table", "alter ")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in forbidden_attr_calls, f"write call {node.func.attr}"
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            low = node.value.lower()
            for verb in forbidden_sql:
                assert verb not in low, f"write SQL fragment {verb!r} in literal"
    # And it must open the DB read-only.
    assert "mode=ro" in source


def test_missing_db_is_safe(tmp_path):
    result = backlog_triage.run(WINDOW_START, WINDOW_END, tmp_path)
    assert result.value == 0.0
    assert result.dimensions["total_open"] == 0


def test_all_benchmark_modules_importable_with_run():
    """Registering backlog_triage must not break sibling benchmarks."""
    assert "backlog_triage" in cli.BENCHMARK_MODULES
    for name in cli.BENCHMARK_MODULES:
        mod = importlib.import_module("scripts.benchmarks." + name)
        assert callable(getattr(mod, "run", None)), f"{name} missing run()"
