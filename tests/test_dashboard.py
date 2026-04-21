"""Tests for the generated GroundTruth KB operations dashboard."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB


def test_dashboard_init_generates_sqlite_and_grafana_assets(runner: CliRunner, project_dir: Path) -> None:
    db = KnowledgeDB(project_dir / "groundtruth.db")
    db.close()

    result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "dashboard", "init"])

    assert result.exit_code == 0, result.output
    dashboard_db = project_dir / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"
    dashboard_json = (
        project_dir / ".groundtruth" / "dashboard" / "grafana" / "dashboards" / "groundtruth-kb-dashboard.json"
    )
    assert dashboard_db.exists()
    assert dashboard_json.exists()

    dashboard = json.loads(dashboard_json.read_text(encoding="utf-8"))
    assert dashboard["uid"] == "groundtruth-kb"
    assert dashboard["title"].startswith("Test Project")

    with sqlite3.connect(dashboard_db) as conn:
        setup_steps = conn.execute("SELECT COUNT(*) FROM setup_steps").fetchone()[0]
        services = conn.execute("SELECT COUNT(*) FROM third_party_services").fetchone()[0]
        openai = conn.execute(
            "SELECT service_name FROM third_party_services WHERE id = 'openai'",
        ).fetchone()[0]

    assert setup_steps >= 6
    assert services >= 7
    assert openai == "OpenAI Codex"


def test_dashboard_refresh_reports_seeded_spec_counts(runner: CliRunner, project_dir: Path) -> None:
    config_flag = ["--config", str(project_dir / "groundtruth.toml")]
    seed_result = runner.invoke(main, [*config_flag, "seed"])
    assert seed_result.exit_code == 0, seed_result.output

    result = runner.invoke(main, [*config_flag, "dashboard", "refresh"])

    assert result.exit_code == 0, result.output
    dashboard_db = project_dir / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"
    with sqlite3.connect(dashboard_db) as conn:
        specs_total = conn.execute("SELECT value FROM current_metrics WHERE key = 'specs-total'").fetchone()[0]
        failed_assertions = conn.execute(
            "SELECT value FROM current_metrics WHERE key = 'assertions-failed'",
        ).fetchone()[0]

    assert specs_total == "5"
    assert failed_assertions == "0"


def test_dashboard_install_accepts_existing_grafana_home(runner: CliRunner, project_dir: Path, tmp_path: Path) -> None:
    db = KnowledgeDB(project_dir / "groundtruth.db")
    db.close()
    grafana_home = tmp_path / "grafana"
    bin_dir = grafana_home / "bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / "grafana-server.exe").write_text("", encoding="utf-8")
    (bin_dir / "grafana-server").write_text("", encoding="utf-8")

    result = runner.invoke(
        main,
        [
            "--config",
            str(project_dir / "groundtruth.toml"),
            "dashboard",
            "install",
            "--grafana-home",
            str(grafana_home),
            "--skip-download",
            "--skip-plugin",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Grafana ready" in result.output


def test_dashboard_start_explains_missing_grafana(runner: CliRunner, project_dir: Path) -> None:
    db = KnowledgeDB(project_dir / "groundtruth.db")
    db.close()

    result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "dashboard", "start"])

    assert result.exit_code == 1
    assert "Grafana is not installed" in result.output
