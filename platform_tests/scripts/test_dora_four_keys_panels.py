"""GTKB-DORA-002: DORA four-keys metric computation and dashboard panels.

Verifies the four-keys consumer of the DORA-001 telemetry foundation:
- deployment frequency, change failure rate, and MTTR compute from the
  authoritative ``delivery_timeline_events`` + ``incidents`` telemetry;
- lead time renders null/annotated (the foundation lacks per-commit authored
  timestamps) rather than a fabricated value
  (``GOV-SESSION-SELF-INITIALIZATION-001``);
- all four keys render null/annotated states when telemetry is insufficient;
- the generated Grafana dashboard exposes the four stat panels against the
  SQLite ``current_metrics`` source.
"""

from __future__ import annotations

import sqlite3

from groundtruth_kb.dashboard import _dora_four_keys_metric_rows
from groundtruth_kb.dashboard_grafana import build_dashboard

_DORA_KEYS = (
    "dora_deployment_frequency",
    "dora_lead_time_hours",
    "dora_change_failure_rate",
    "dora_mttr_hours",
)


def _seed_conn() -> sqlite3.Connection:
    """In-memory DB with only the columns the DORA helpers query."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE delivery_timeline_events (
            event_kind TEXT NOT NULL DEFAULT 'change',
            deployable_change_id TEXT NOT NULL DEFAULT '',
            rollback_of_deploy_id TEXT NOT NULL DEFAULT '',
            hotfix_of_deploy_id TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE incidents (
            caused_by_deploy_id TEXT NOT NULL DEFAULT '',
            detected_at TEXT NOT NULL DEFAULT '',
            mitigated_at TEXT NOT NULL DEFAULT '',
            closed_at TEXT NOT NULL DEFAULT ''
        )
        """
    )
    return conn


def _rows_by_key(conn: sqlite3.Connection) -> dict[str, tuple]:
    return {row[0]: row for row in _dora_four_keys_metric_rows(conn)}


def test_dora_rows_null_when_no_telemetry() -> None:
    conn = _seed_conn()
    rows = _rows_by_key(conn)

    assert set(rows) == set(_DORA_KEYS)
    for key in _DORA_KEYS:
        # (metric_key, metric_label, value, status, description)
        assert rows[key][2] is None, f"{key} must be null when no telemetry"
        assert rows[key][3] == "yellow"
        assert rows[key][4].strip(), f"{key} must carry an explanatory annotation"


def test_dora_metrics_computed_from_seeded_telemetry() -> None:
    conn = _seed_conn()
    # Three authoritative deployments.
    conn.executemany(
        "INSERT INTO delivery_timeline_events (event_kind, deployable_change_id) VALUES (?, ?)",
        [
            ("canonical_deploy", "chg-1"),
            ("canonical_deploy", "chg-2"),
            ("canonical_deploy", "chg-3"),
        ],
    )
    # chg-1 was rolled back -> counts as a failed change.
    conn.execute(
        "INSERT INTO delivery_timeline_events (event_kind, rollback_of_deploy_id) VALUES (?, ?)",
        ("rollback", "chg-1"),
    )
    # chg-2 caused an incident mitigated in 2h; a second incident closed in 4h.
    conn.executemany(
        "INSERT INTO incidents (caused_by_deploy_id, detected_at, mitigated_at, closed_at) VALUES (?, ?, ?, ?)",
        [
            ("chg-2", "2026-01-01T00:00:00Z", "2026-01-01T02:00:00Z", ""),
            ("", "2026-01-01T00:00:00Z", "", "2026-01-01T04:00:00Z"),
        ],
    )
    rows = _rows_by_key(conn)

    assert rows["dora_deployment_frequency"][2] == 3
    # failed changes = {chg-1 (rollback), chg-2 (incident)} of 3 -> 66.7%
    assert rows["dora_change_failure_rate"][2] == 66.7
    # MTTR = mean(2h, 4h) = 3.0h
    assert rows["dora_mttr_hours"][2] == 3.0
    # Lead time remains null: no per-commit authored timestamps in the foundation.
    assert rows["dora_lead_time_hours"][2] is None
    assert rows["dora_lead_time_hours"][3] == "yellow"


def test_change_failure_rate_zero_when_no_failures() -> None:
    conn = _seed_conn()
    conn.executemany(
        "INSERT INTO delivery_timeline_events (event_kind, deployable_change_id) VALUES (?, ?)",
        [("canonical_deploy", "chg-1"), ("canonical_deploy", "chg-2")],
    )
    rows = _rows_by_key(conn)

    assert rows["dora_deployment_frequency"][2] == 2
    assert rows["dora_change_failure_rate"][2] == 0.0
    assert rows["dora_change_failure_rate"][3] == "green"
    # No incidents -> MTTR stays null.
    assert rows["dora_mttr_hours"][2] is None


def test_generated_dashboard_exposes_dora_four_keys_panels() -> None:
    dashboard = build_dashboard()

    def walk(panels: list[dict]) -> list[dict]:
        found: list[dict] = []
        for panel in panels:
            found.append(panel)
            found.extend(walk(panel.get("panels", [])))
        return found

    all_panels = walk(dashboard["panels"])
    titles = {panel["title"] for panel in all_panels}
    assert {
        "Deployment Frequency",
        "Lead Time for Changes",
        "Change Failure Rate",
        "MTTR",
    } <= titles

    by_title = {panel["title"]: panel for panel in all_panels}
    expected_metric_keys = {
        "Deployment Frequency": "dora_deployment_frequency",
        "Lead Time for Changes": "dora_lead_time_hours",
        "Change Failure Rate": "dora_change_failure_rate",
        "MTTR": "dora_mttr_hours",
    }
    for title, metric_key in expected_metric_keys.items():
        panel = by_title[title]
        assert panel["type"] == "stat"
        query = panel["targets"][0]["rawQueryText"]
        assert f"metric_key = '{metric_key}'" in query
        assert "current_metrics" in query
