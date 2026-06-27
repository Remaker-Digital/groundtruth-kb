"""Tests for WI-4687 ops activity status and AUQ option rendering."""

from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.activity.ops import OPS_OPTIONS, collect_ops_snapshot, render_ops_activity_context
from groundtruth_kb.session.topic_router import render_topic_context


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_ops_context_reports_missing_sources_without_blocking(tmp_path: Path) -> None:
    rendered = render_ops_activity_context(tmp_path)

    assert "## Ops Activity Status And AUQ Options" in rendered
    assert "- status: report-only" in rendered
    assert "health | unavailable | missing optional source(s):" in rendered
    assert "support cases | unavailable | missing optional source(s): .gtkb-state/ops/support-cases.json" in rendered
    assert "- ops support cases: unavailable at `.gtkb-state/ops/support-cases.json` (missing)" in rendered
    for option in OPS_OPTIONS:
        assert option in rendered


def test_ops_context_prioritizes_approved_auq_vocabulary_in_stable_order(tmp_path: Path) -> None:
    _write_json(
        tmp_path / ".gtkb-state" / "ops" / "health.json",
        {"status": "red", "summary": "release gate blocked"},
    )
    _write_json(
        tmp_path / ".gtkb-state" / "ops" / "scale.json",
        {"current_load": 95, "scale_threshold": 90},
    )
    _write_json(
        tmp_path / ".gtkb-state" / "ops" / "support-cases.json",
        {"open_cases": 3, "urgent_cases": 1},
    )
    _write_json(
        tmp_path / ".gtkb-state" / "ops" / "user-activity.json",
        {"active_users": 120, "activity_threshold": 100},
    )
    _write_json(
        tmp_path / ".gtkb-state" / "ops" / "feedback.json",
        {"pending_feedback": 4, "negative_feedback": 2},
    )

    snapshot = collect_ops_snapshot(tmp_path)
    assert [option.text for option in snapshot.options] == list(OPS_OPTIONS)
    assert [option.priority for option in snapshot.options] == ["P1", "P1", "P1", "P1", "P1"]

    rendered = render_ops_activity_context(tmp_path)
    option_positions = [rendered.index(f"{index}. {option}") for index, option in enumerate(OPS_OPTIONS, start=1)]
    assert option_positions == sorted(option_positions)
    assert "| scale | attention | current_load=95; scale_threshold=90 |" in rendered
    assert "| ops feedback | attention | pending_feedback=4; negative_feedback=2 |" in rendered


def test_ops_context_uses_project_progress_snapshot_for_health_and_scale(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "independent-progress-assessments" / "artifacts" / "project-progress" / "latest.json",
        {
            "headlines": {"release_gate_status": "red", "open_p0_p1": 2},
            "operations": {
                "deployment_success_rate_30d": 88.6,
                "latest_verification_run": {"status": "failed"},
                "runtime_live_metrics": {"status": "unavailable"},
            },
            "quality": {"failing_tests": 1},
        },
    )

    rendered = render_ops_activity_context(tmp_path)

    assert "| health | attention | release_gate_status=red; open_p0_p1=2;" in rendered
    assert "| scale | watch | deployment_success_rate_30d=88.6;" in rendered
    snapshot_path = "independent-progress-assessments/artifacts/project-progress/latest.json"
    assert f"project progress snapshot: available at `{snapshot_path}`" in rendered


def test_topic_router_injects_ops_context_only_for_open_ops(tmp_path: Path) -> None:
    open_ops = render_topic_context(
        {
            "action": "open",
            "topic_type": "ops",
            "project_root": str(tmp_path),
            "topic": {"route_target": "operations-status-decision-service"},
        }
    )
    open_build = render_topic_context(
        {
            "action": "open",
            "topic_type": "build",
            "project_root": str(tmp_path),
            "topic": {"route_target": "build-package-scaffold-service"},
        }
    )
    close_ops = render_topic_context(
        {
            "action": "close",
            "topic_type": "ops",
            "project_root": str(tmp_path),
            "topic": {"route_target": "operations-status-decision-service"},
        }
    )

    assert "## Ops Activity Status And AUQ Options" in open_ops
    assert "## Ops Activity Status And AUQ Options" not in open_build
    assert "## Ops Activity Status And AUQ Options" not in close_ops
