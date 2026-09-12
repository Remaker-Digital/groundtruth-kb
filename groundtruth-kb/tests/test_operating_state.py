"""Tests for deterministic operating-state collection."""

from __future__ import annotations

import inspect
import json
import sqlite3
from pathlib import Path

import pytest
from click.testing import CliRunner

import groundtruth_kb.operating_state as operating_state
from groundtruth_kb.cli import main
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.operating_state import collect_operating_state, format_startup_operating_state


def _config(project_dir: Path) -> GTConfig:
    return GTConfig.load(project_dir / "groundtruth.toml")


def test_collect_operating_state_reports_project_and_db(project_dir: Path) -> None:
    KnowledgeDB(project_dir / "groundtruth.db").close()
    state = collect_operating_state(project_dir, config=_config(project_dir), components=("project", "db"))
    by_name = {component.name: component for component in state.components}

    assert state.schema_version == 1
    assert by_name["project"].status == "PASS"
    assert by_name["db"].status == "PASS"
    assert by_name["db"].evidence["integrity_check"] == "ok"


def test_archive_path_is_rejected(tmp_path: Path) -> None:
    archive = tmp_path / "Claude-Playground" / "archived-project"
    archive.mkdir(parents=True)
    config = GTConfig(project_root=archive, db_path=archive / "groundtruth.db")

    with pytest.raises(ValueError, match="archive path"):
        collect_operating_state(archive, config=config)


def test_missing_chromadb_is_unknown_not_crash(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(operating_state._db_module, "HAS_CHROMADB", False)

    state = collect_operating_state(project_dir, config=_config(project_dir), components=("chroma",))

    assert state.components[0].status == "UNKNOWN"
    assert "not installed" in state.components[0].detail


def test_absent_dashboard_cache_is_unknown_with_regeneration_guidance(project_dir: Path) -> None:
    dashboard_db = project_dir / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"
    assert not dashboard_db.exists()

    state = collect_operating_state(project_dir, config=_config(project_dir), components=("dashboard",))
    dashboard = state.components[0]

    assert dashboard.status == "UNKNOWN"
    assert "regenerated" in dashboard.detail
    assert "gt dashboard refresh" in dashboard.detail
    assert dashboard.detail != "dashboard SQLite database not generated"


def test_absent_dashboard_cache_does_not_crash_and_keeps_source_path(project_dir: Path) -> None:
    dashboard_db = project_dir / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"

    state = collect_operating_state(project_dir, config=_config(project_dir), components=("dashboard",))
    dashboard = state.components[0]

    assert dashboard.status == "UNKNOWN"
    assert dashboard.source == str(dashboard_db)
    assert dashboard.evidence == {}


def test_present_dashboard_cache_reports_pass_with_table_count(project_dir: Path) -> None:
    dashboard_db = project_dir / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"
    dashboard_db.parent.mkdir(parents=True)
    with sqlite3.connect(dashboard_db) as conn:
        conn.execute("CREATE TABLE sample_metric (id INTEGER PRIMARY KEY)")

    state = collect_operating_state(project_dir, config=_config(project_dir), components=("dashboard",))
    dashboard = state.components[0]

    assert dashboard.status == "PASS"
    assert dashboard.detail == "dashboard SQLite database readable"
    assert dashboard.evidence["tables"] == 1


def test_status_cli_json_and_startup_use_same_collector(project_dir: Path, runner: CliRunner) -> None:
    KnowledgeDB(project_dir / "groundtruth.db").close()

    result = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "status", "--startup", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema_version"] == 1
    assert payload["startup"] is True
    assert {component["name"] for component in payload["components"]} >= {
        "project",
        "db",
        "bridge",
        "resource-registry",
        "system-interface-map",
    }
    db_component = next(component for component in payload["components"] if component["name"] == "db")
    assert db_component["evidence"]["quick_check"] is True

    state = collect_operating_state(project_dir, config=_config(project_dir), startup=True)
    rendered = format_startup_operating_state(state)
    assert "Operating State" in rendered
    assert str(project_dir.resolve()) in rendered


@pytest.mark.parametrize("report_content", [None, "", "# Startup: PASS\nAll previous inputs were current.\n"])
def test_startup_status_cannot_certify_context_from_a_historical_report(project_dir, runner, report_content):
    KnowledgeDB(project_dir / "groundtruth.db").close()
    if report_content is not None:
        report = project_dir / "docs" / "gtkb-dashboard" / "session-startup-report.md"
        report.parent.mkdir(parents=True)
        report.write_text(report_content, encoding="utf-8")
    result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "status", "--startup", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "startup" not in {component["name"] for component in payload["components"]}
    assert "session-startup-report.md" not in result.output


def test_operating_state_module_has_no_llm_or_network_dependency() -> None:
    source = inspect.getsource(operating_state)

    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "api_key" not in source.lower()
    assert "urllib" not in source.lower()
