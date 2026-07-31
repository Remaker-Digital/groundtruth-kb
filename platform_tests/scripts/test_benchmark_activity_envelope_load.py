"""Tests for the activity envelope load benchmark."""

from __future__ import annotations

import shutil
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main

from scripts.benchmarks.activity_envelope_load import build_report

ROOT = Path(__file__).resolve().parents[2]


def test_activity_envelope_load_reports_real_config() -> None:
    report = build_report(project_root=ROOT)

    assert report["benchmark_id"] == "activity_envelope_load"
    assert report["status"] == "PASS"
    assert report["summary"]["activity_count"] == 6
    assert report["global_baseline"]["surface_count"] >= 1
    assert report["never_startup"]["missing_required_forbidden_payloads"] == []
    assert report["activities"]["build"]["classification"]["skills"] == "activity_only"
    assert report["activities"]["build"]["classification"]["history_state"] == "explicit_query"


def test_activity_envelope_load_fails_on_global_activity_payload_leak(tmp_path: Path) -> None:
    config_root = tmp_path / "config" / "agent-control"
    config_root.mkdir(parents=True)
    shutil.copy(
        ROOT / "config" / "agent-control" / "activity-envelope-sharding.toml",
        config_root / "activity-envelope-sharding.toml",
    )
    profiles_path = config_root / "activity-disposition-profiles.toml"
    text = (ROOT / "config" / "agent-control" / "activity-disposition-profiles.toml").read_text(encoding="utf-8")
    text = text.replace(
        '[activities.build.classification]\nskills = "activity_only"',
        '[activities.build.classification]\nskills = "global_baseline"',
    )
    profiles_path.write_text(text, encoding="utf-8")

    report = build_report(project_root=tmp_path)

    assert report["status"] == "FAIL"
    assert any(issue["code"] == "activity_payload_in_global_baseline" for issue in report["issues"])


def test_gt_benchmarks_activity_envelope_load_json() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["benchmarks", "activity-envelope-load", "--json"])

    assert result.exit_code == 0, result.output
    assert '"benchmark_id": "activity_envelope_load"' in result.output
    assert '"status": "PASS"' in result.output
