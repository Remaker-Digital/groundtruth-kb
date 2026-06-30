from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts.gtkb_dashboard import refresh_dashboard_db

REPO_ROOT = Path(__file__).resolve().parents[2]


def _minimal_model() -> dict:
    return {
        "generated_at": "2026-06-30T12:00:00+00:00",
        "role": {"assumed_role": "Prime Builder"},
        "dashboard_requirements": {"scope_note": "GroundTruth-KB project dashboard."},
        "metrics": {
            "contention": {"actionable_count": 0},
            "drift": {"changed_path_count": 0},
            "regression": {"release_blocker_count": 0},
        },
        "dashboard_intelligence": {
            "health": [],
            "shortcuts": [],
            "action_center": [],
            "release_readiness": {"blockers": [], "blocker_count": 0},
            "quality_rollup": {"total": 0, "failing": 0, "manual": 0, "unknown": 0, "ready_or_passing": 0},
            "risk_register": [],
            "data_freshness": {
                "generated_at": "2026-06-30T12:00:00+00:00",
                "repo_branch": "main",
                "repo_short_sha": "clean",
                "scope_version": "gtkb_v1",
                "sources": ["test"],
            },
        },
        "infrastructure": {
            "delivery_timeline": {"stage_summary": [], "timeline": []},
            "testing_service_integrations": {},
        },
    }


def test_dashboard_schema_is_self_contained_for_application_deployment_signals(tmp_path: Path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"

    refresh_dashboard_db.initialize_database(db_path)

    with sqlite3.connect(db_path) as conn:
        assert (
            conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'application_deployment_signals'"
            ).fetchone()
            is not None
        )

    result = refresh_dashboard_db.refresh_database(
        db_path=db_path,
        project_root=REPO_ROOT,
        model=_minimal_model(),
        history=[],
    )

    assert result["status"] == "completed"
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM application_deployment_signals").fetchone()[0] == 6
