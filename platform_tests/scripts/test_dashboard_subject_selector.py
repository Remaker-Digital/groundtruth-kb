"""Native landing-page observations replace the retired startup work-subject projection.

Browser qualification runs the authored JavaScript; these tests exercise the
real refresh/publisher and its failure boundaries without duplicating that JS.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb import dashboard, get_templates_dir

REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX_HTML = get_templates_dir() / "dashboard/index.html"


@pytest.fixture(autouse=True)
def isolate_unrelated_optional_consumers(monkeypatch):
    monkeypatch.setattr(dashboard, "_write_bridge_swimlane_safe", lambda *args: None)


def _model(value=7):
    return {
        "generated_at": "2026-09-12T12:00:05+00:00",
        "current_work_subject": "private legacy selection",
        "role": {"assumed_role": "private legacy role"},
        "metrics": {
            "backlog": {"active_item_count": value},
            "membase": {"open_work_items": value},
            "contention": {"actionable_count": 0},
            "work_subject": {"current_subject": "private legacy selection"},
        },
        "dashboard_intelligence": {
            "data_freshness": {
                "started_at": "2026-09-12T12:00:00+00:00",
                "sources": ["private observation details must not be exported"],
            },
        },
    }


def _page_data(root):
    return root / ".groundtruth/dashboard/dashboard-data.json"


def test_refresh_publishes_current_allowlisted_values_and_matches_sql(tmp_path):
    db = tmp_path / "dashboard.sqlite"
    model = _model()
    assert dashboard.refresh_database(db, tmp_path, model=model)["status"] == "completed"
    payload = json.loads(_page_data(tmp_path).read_text(encoding="utf-8"))
    assert set(payload) == {"status", "started_at", "generated_at", "metrics"}
    assert payload["status"] == "partial"
    assert payload["metrics"]["backlog_active_items"] == 7
    assert payload["metrics"]["contention_actionable_bridge_count"] == 0
    assert payload["metrics"]["regression_release_blocker_count"] is None
    with sqlite3.connect(db) as conn:
        assert payload["metrics"] == dict(conn.execute("SELECT metric_key,value FROM kpi_snapshots"))
    assert "private" not in json.dumps(payload)
    assert "current_work_subject" not in payload


def test_refresh_does_not_select_a_prior_or_future_history_row(tmp_path):
    model = _model()
    history = [{"generated_at": "2099-01-01T00:00:00+00:00", "backlog_active_items": 999}]
    dashboard.refresh_database(tmp_path / "dashboard.sqlite", tmp_path, model=model, history=history)
    payload = json.loads(_page_data(tmp_path).read_text())
    assert payload["generated_at"] == model["generated_at"]
    assert payload["metrics"]["backlog_active_items"] == 7
    assert "history" not in payload


def test_missing_native_sources_replace_old_page_values_without_startup_fallback(tmp_path, monkeypatch):
    dashboard._write_landing_snapshot(tmp_path, _model())
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory/gtkb-dashboard-history.json").write_text('[{"backlog_active_items":999}]')
    monkeypatch.setattr(dashboard, "_run_release_probe", lambda *a, **kw: None)
    dashboard.refresh_database(tmp_path / "dashboard.sqlite", tmp_path)
    payload = json.loads(_page_data(tmp_path).read_text())
    assert payload["status"] == "unavailable"
    assert all(value is None for value in payload["metrics"].values())
    assert payload["generated_at"] is not None


@pytest.mark.parametrize("value", [True, -1, "0", float("nan"), float("inf"), {}, []])
def test_invalid_numeric_telemetry_remains_unavailable(value):
    payload = dashboard._landing_snapshot_from_model(_model(value))
    assert payload["metrics"]["backlog_active_items"] is None
    assert payload["metrics"]["membase_open_work_items"] is None
    assert payload["metrics"]["contention_actionable_bridge_count"] == 0
    json.dumps(payload, allow_nan=False)


@pytest.mark.parametrize(
    "start,end",
    [
        (None, None),
        ("bad", "bad"),
        ("2026-09-12T12:00:00", "2026-09-12T12:00:05"),
        ("2026-09-12T12:00:06Z", "2026-09-12T12:00:05Z"),
    ],
)
def test_missing_or_invalid_collection_interval_cannot_establish_fresh_values(start, end):
    model = _model()
    model["generated_at"] = end
    model["dashboard_intelligence"]["data_freshness"]["started_at"] = start
    payload = dashboard._landing_snapshot_from_model(model)
    assert payload["status"] == "unavailable"
    assert payload["started_at"] is None and payload["generated_at"] is None
    assert all(value is None for value in payload["metrics"].values())


def test_atomic_publisher_failure_preserves_old_file_and_removes_temporary(tmp_path, monkeypatch):
    dashboard._write_landing_snapshot(tmp_path, _model())
    before = _page_data(tmp_path).read_bytes()

    def refuse_replace(source, target):
        assert source.parent == target.parent
        raise OSError("fixture publication failure")

    monkeypatch.setattr(dashboard.os, "replace", refuse_replace)
    with pytest.raises(OSError, match="fixture publication failure"):
        dashboard._write_landing_snapshot(tmp_path, _model(8))
    assert _page_data(tmp_path).read_bytes() == before
    assert list(_page_data(tmp_path).parent.glob("*.tmp")) == []


def test_failed_database_refresh_does_not_publish_new_page_values(tmp_path, monkeypatch):
    dashboard._write_landing_snapshot(tmp_path, _model())
    before = _page_data(tmp_path).read_bytes()

    def fail_db(*a, **kw):
        raise RuntimeError("fixture database failure")

    monkeypatch.setattr(dashboard, "_write_model_to_db", fail_db)
    db = tmp_path / "dashboard.sqlite"
    with pytest.raises(RuntimeError, match="fixture database failure"):
        dashboard.refresh_database(db, tmp_path, model=_model(8))
    assert _page_data(tmp_path).read_bytes() == before
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT status FROM refresh_runs").fetchone()[0] == "failed"


def test_failed_page_publication_marks_refresh_failed_after_database_update(tmp_path, monkeypatch):
    def fail_page(*a, **kw):
        raise OSError("fixture page failure")

    monkeypatch.setattr(dashboard, "_write_landing_snapshot", fail_page)
    db = tmp_path / "dashboard.sqlite"
    with pytest.raises(OSError, match="fixture page failure"):
        dashboard.refresh_database(db, tmp_path, model=_model())
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT status FROM refresh_runs").fetchone()[0] == "failed"
        assert conn.execute("SELECT count(*) FROM kpi_snapshots").fetchone()[0] > 0
    assert not _page_data(tmp_path).exists()


@pytest.mark.parametrize("entry", ["cli-explicit-db", "cli-default-db", "function-default-db", "cli-init"])
def test_refresh_cli_writes_page_only_under_explicit_project_root(tmp_path, monkeypatch, entry):
    from click.testing import CliRunner
    from groundtruth_kb.cli import main

    child = tmp_path / "requested"
    child.mkdir()
    selected = child / "chosen.toml"
    selected.write_text("[groundtruth]\n", encoding="utf-8")
    monkeypatch.setattr(dashboard, "_build_dashboard_model", lambda root, config=None: _model())
    expected_db = child / ".groundtruth/dashboard/gtkb-dashboard.sqlite"
    paths = []
    original = dashboard.initialize_database

    def initialize(path):
        assert path.is_relative_to(child), "No test may initialize the production database"
        paths.append(path)
        original(path)

    monkeypatch.setattr(dashboard, "initialize_database", initialize)
    if entry == "function-default-db":
        assert dashboard.refresh_database(project_root=child)["status"] == "completed"
    else:
        args = ["--config", str(selected), "dashboard", "init" if entry == "cli-init" else "refresh", "--json"]
        if entry == "cli-explicit-db":
            expected_db = child / "dashboard.sqlite"
            args += ["--db-path", str(expected_db)]
        result = CliRunner().invoke(main, args)
        assert result.exit_code == 0, result.output
        output = json.loads(result.output)
        assert output["status"] == "completed" and output["project_root"] == str(child)
        assert (child / ".groundtruth/dashboard/index.html").is_file()
    assert paths == [expected_db]
    assert expected_db.is_file() and _page_data(child).exists()
    assert not _page_data(tmp_path).exists()


def test_landing_page_uses_native_metrics_without_subject_or_history_inference():
    page = INDEX_HTML.read_text(encoding="utf-8")
    assert 'fetch("dashboard-data.json", { cache: "no-store" })' in page
    assert "validKpiSnapshot" in page
    for obsolete in ("current_work_subject", "Canonical subject", "subject-toolbar", "selectLatest", "SCOPE_BY_METRIC"):
        assert obsolete not in page
    for key, *_ in dashboard.KPI_DEFINITIONS:
        assert key in page


def test_landing_page_swimlane_section():
    page = INDEX_HTML.read_text(encoding="utf-8")
    assert 'id="swimlane-heading"' in page
    assert 'id="swimlane-table"' in page
