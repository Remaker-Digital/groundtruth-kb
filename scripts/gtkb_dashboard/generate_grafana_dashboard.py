#!/usr/bin/env python3
"""Generate the GT-KB Grafana dashboard JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_PATH = PROJECT_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "dashboards" / "gtkb-dashboard.json"
SQLITE_DATASOURCE = {"type": "frser-sqlite-datasource", "uid": "gtkb-dashboard-sqlite"}


class PanelBuilder:
    def __init__(self) -> None:
        self._next_id = 1

    def next_id(self) -> int:
        panel_id = self._next_id
        self._next_id += 1
        return panel_id


def _grid(x: int, y: int, w: int, h: int) -> dict[str, int]:
    return {"x": x, "y": y, "w": w, "h": h}


def _target(query: str, ref_id: str = "A", *, fmt: str = "table") -> dict[str, Any]:
    normalized = query.strip()
    return {
        "datasource": SQLITE_DATASOURCE,
        "format": fmt,
        "queryText": normalized,
        "queryType": "table",
        "rawQueryText": normalized,
        "refId": ref_id,
        "timeColumns": ["time", "generated_at", "started_at", "completed_at"],
    }


def _thresholds() -> dict[str, Any]:
    return {
        "mode": "absolute",
        "steps": [
            {"color": "green", "value": None},
            {"color": "yellow", "value": 1},
            {"color": "red", "value": 2},
        ],
    }


def _status_mappings() -> list[dict[str, Any]]:
    return [
        {"options": {"0": {"text": "OK", "color": "green"}}, "type": "value"},
        {"options": {"1": {"text": "Watch", "color": "yellow"}}, "type": "value"},
        {"options": {"2": {"text": "Act", "color": "red"}}, "type": "value"},
    ]


def _panel(
    builder: PanelBuilder,
    *,
    title: str,
    panel_type: str,
    grid: dict[str, int],
    targets: list[dict[str, Any]] | None = None,
    options: dict[str, Any] | None = None,
    field_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    panel: dict[str, Any] = {
        "id": builder.next_id(),
        "type": panel_type,
        "title": title,
        "gridPos": grid,
    }
    if targets is not None:
        panel["datasource"] = SQLITE_DATASOURCE
        panel["targets"] = targets
    if options is not None:
        panel["options"] = options
    if field_config is not None:
        panel["fieldConfig"] = field_config
    return panel


def _text_panel(builder: PanelBuilder, title: str, grid: dict[str, int], content: str) -> dict[str, Any]:
    return _panel(
        builder,
        title=title,
        panel_type="text",
        grid=grid,
        options={"mode": "markdown", "content": content},
    )


def _stat_panel(
    builder: PanelBuilder,
    title: str,
    grid: dict[str, int],
    query: str,
    *,
    unit: str = "short",
    decimals: int = 0,
    thresholds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _panel(
        builder,
        title=title,
        panel_type="stat",
        grid=grid,
        targets=[_target(query)],
        options={
            "colorMode": "background",
            "graphMode": "none",
            "justifyMode": "center",
            "orientation": "auto",
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "textMode": "auto",
            "wideLayout": True,
        },
        field_config={
            "defaults": {
                "color": {"mode": "thresholds"},
                "decimals": decimals,
                "thresholds": thresholds
                or {
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None},
                        {"color": "yellow", "value": 1},
                        {"color": "red", "value": 2},
                    ],
                },
                "unit": unit,
            },
            "overrides": [],
        },
    )


def _bar_gauge_panel(
    builder: PanelBuilder,
    title: str,
    grid: dict[str, int],
    query: str,
    *,
    max_value: int | None = None,
    mappings: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "color": {"mode": "thresholds"},
        "thresholds": _thresholds(),
        "unit": "short",
    }
    if max_value is not None:
        defaults["max"] = max_value
        defaults["min"] = 0
    if mappings is not None:
        defaults["mappings"] = mappings
    return _panel(
        builder,
        title=title,
        panel_type="bargauge",
        grid=grid,
        targets=[_target(query)],
        options={
            "displayMode": "gradient",
            "maxVizHeight": 34,
            "minVizHeight": 18,
            "minVizWidth": 8,
            "namePlacement": "left",
            "orientation": "horizontal",
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "showUnfilled": True,
            "valueMode": "color",
        },
        field_config={"defaults": defaults, "overrides": []},
    )


def _pie_panel(builder: PanelBuilder, title: str, grid: dict[str, int], query: str) -> dict[str, Any]:
    return _panel(
        builder,
        title=title,
        panel_type="piechart",
        grid=grid,
        targets=[_target(query)],
        options={
            "displayLabels": ["name", "value"],
            "legend": {"displayMode": "list", "placement": "right", "showLegend": True},
            "pieType": "donut",
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "tooltip": {"mode": "single", "sort": "none"},
        },
        field_config={
            "defaults": {
                "color": {"mode": "palette-classic"},
                "custom": {"hideFrom": {"legend": False, "tooltip": False, "viz": False}},
            },
            "overrides": [],
        },
    )


def _time_series_panel(builder: PanelBuilder, title: str, grid: dict[str, int], query: str) -> dict[str, Any]:
    return _panel(
        builder,
        title=title,
        panel_type="timeseries",
        grid=grid,
        targets=[_target(query, fmt="time_series")],
        options={
            "legend": {"displayMode": "table", "placement": "bottom", "showLegend": True},
            "tooltip": {"mode": "multi", "sort": "none"},
        },
        field_config={
            "defaults": {
                "color": {"mode": "palette-classic"},
                "custom": {
                    "axisBorderShow": False,
                    "axisCenteredZero": False,
                    "drawStyle": "line",
                    "fillOpacity": 10,
                    "lineInterpolation": "linear",
                    "lineWidth": 2,
                    "pointSize": 4,
                    "showPoints": "auto",
                },
            },
            "overrides": [],
        },
    )


def _table_panel(
    builder: PanelBuilder,
    title: str,
    grid: dict[str, int],
    query: str,
    *,
    links: dict[str, str] | None = None,
    hidden_columns: tuple[str, ...] = ("sort_order",),
) -> dict[str, Any]:
    overrides: list[dict[str, Any]] = [
        {
            "matcher": {"id": "byName", "options": column},
            "properties": [{"id": "custom.hidden", "value": True}],
        }
        for column in hidden_columns
    ]
    for column, link_title in (links or {}).items():
        overrides.append(
            {
                "matcher": {"id": "byName", "options": column},
                "properties": [
                    {
                        "id": "links",
                        "value": [{"title": link_title, "url": "${__value.raw}", "targetBlank": True}],
                    }
                ],
            }
        )
    return _panel(
        builder,
        title=title,
        panel_type="table",
        grid=grid,
        targets=[_target(query)],
        options={
            "cellHeight": "sm",
            "footer": {"show": False},
            "showHeader": True,
            "sortBy": [{"displayName": "sort_order", "desc": False}],
        },
        field_config={
            "defaults": {"custom": {"align": "auto", "cellOptions": {"type": "auto"}, "inspect": False}},
            "overrides": overrides,
        },
    )


def _row(builder: PanelBuilder, title: str, y: int, *, collapsed: bool = False, panels: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "id": builder.next_id(),
        "type": "row",
        "title": title,
        "collapsed": collapsed,
        "gridPos": _grid(0, y, 24, 1),
        "panels": panels or [],
    }


def _metric_query(metric_key: str) -> str:
    return f"SELECT value FROM current_metrics WHERE metric_key = '{metric_key}';"


def build_dashboard() -> dict[str, Any]:
    builder = PanelBuilder()
    panels: list[dict[str, Any]] = []

    panels.append(
        _text_panel(
            builder,
            "GT-KB Dashboard",
            _grid(0, 0, 24, 3),
            "\n".join(
                [
                    "# Agent Red GT-KB Dashboard",
                    "",
                    "SQLite-backed project health, setup, delivery, and operations view.",
                    "[Manual refresh](http://127.0.0.1:8766/) | `memory/gtkb-dashboard.sqlite` | `scripts\\gtkb_dashboard\\start_local_dashboard.ps1`",
                ]
            ),
        )
    )

    panels.extend(
        [
            _stat_panel(builder, "Project Health Issues", _grid(0, 3, 4, 4), _metric_query("project_health_issues")),
            _stat_panel(builder, "Release Blockers", _grid(4, 3, 4, 4), _metric_query("release_blockers")),
            _stat_panel(builder, "CI / Testing Failing", _grid(8, 3, 4, 4), _metric_query("ci_testing_failing")),
            _stat_panel(
                builder,
                "Governance Bridge Items",
                _grid(12, 3, 4, 4),
                _metric_query("governance_bridge_items"),
                thresholds={
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None},
                        {"color": "yellow", "value": 1},
                        {"color": "red", "value": 3},
                    ],
                },
            ),
            _stat_panel(
                builder,
                "Refresh Age",
                _grid(16, 3, 4, 4),
                """
                SELECT COALESCE(
                    CAST((julianday('now') - julianday(MAX(COALESCE(completed_at, started_at)))) * 24 * 60 AS INTEGER),
                    9999
                ) AS value
                FROM refresh_runs;
                """,
                unit="m",
                thresholds={
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None},
                        {"color": "yellow", "value": 65},
                        {"color": "red", "value": 180},
                    ],
                },
            ),
            _stat_panel(
                builder,
                "Documented Setup Steps",
                _grid(20, 3, 4, 4),
                "SELECT COUNT(*) AS value FROM setup_steps;",
                thresholds={"mode": "absolute", "steps": [{"color": "green", "value": None}]},
            ),
        ]
    )

    panels.extend(
        [
            _bar_gauge_panel(
                builder,
                "Health Signals",
                _grid(0, 7, 12, 8),
                """
                SELECT label AS metric,
                       CASE lower(status)
                           WHEN 'red' THEN 2
                           WHEN 'yellow' THEN 1
                           ELSE 0
                       END AS value
                FROM health_cards
                ORDER BY sort_order;
                """,
                max_value=2,
                mappings=_status_mappings(),
            ),
            _pie_panel(
                builder,
                "Action Severity Mix",
                _grid(12, 7, 6, 8),
                """
                SELECT upper(COALESCE(NULLIF(severity, ''), 'unknown')) AS severity,
                       COUNT(*) AS value
                FROM action_center
                GROUP BY severity
                ORDER BY value DESC, severity;
                """,
            ),
            _bar_gauge_panel(
                builder,
                "Delivery Events By Stage",
                _grid(18, 7, 6, 8),
                """
                SELECT label AS metric, event_count AS value
                FROM delivery_timeline_summary
                ORDER BY sort_order;
                """,
            ),
            _bar_gauge_panel(
                builder,
                "Quality Rollup",
                _grid(0, 15, 8, 7),
                """
                SELECT label AS metric, value
                FROM quality_rollup
                WHERE label <> 'Total'
                ORDER BY sort_order;
                """,
            ),
            _bar_gauge_panel(
                builder,
                "Integration Health",
                _grid(8, 15, 8, 7),
                """
                SELECT display_name AS metric,
                       CASE lower(health)
                           WHEN 'red' THEN 2
                           WHEN 'yellow' THEN 1
                           WHEN 'failing' THEN 2
                           WHEN 'manual' THEN 1
                           ELSE 0
                       END AS value
                FROM integration_status
                ORDER BY sort_order;
                """,
                max_value=2,
                mappings=_status_mappings(),
            ),
            _time_series_panel(
                builder,
                "KPI Trend",
                _grid(16, 15, 8, 7),
                """
                SELECT generated_at AS time, metric_label AS metric, value
                FROM kpi_snapshots
                WHERE value IS NOT NULL
                ORDER BY generated_at, metric_label;
                """,
            ),
        ]
    )

    panels.append(_row(builder, "Action Center", 22, collapsed=False))
    panels.append(
        _table_panel(
            builder,
            "Top Actions",
            _grid(0, 23, 12, 6),
            """
            SELECT sort_order,
                   upper(severity) AS severity,
                   action,
                   owner_lane AS lane,
                   shortcut_target
            FROM action_center
            ORDER BY sort_order
            LIMIT 5;
            """,
            links={"shortcut_target": "Open"},
        )
    )
    panels.append(
        _table_panel(
            builder,
            "Shortcuts",
            _grid(12, 23, 12, 6),
            """
            SELECT sort_order, label, target, kind
            FROM shortcuts
            ORDER BY sort_order;
            """,
            links={"target": "Open"},
        )
    )

    panels.append(_row(builder, "GT-KB Install and Setup", 29, collapsed=False))
    panels.extend(
        [
            _bar_gauge_panel(
                builder,
                "Setup Coverage",
                _grid(0, 30, 8, 6),
                """
                SELECT section AS metric, COUNT(*) AS value
                FROM setup_steps
                GROUP BY section
                ORDER BY MIN(sort_order);
                """,
            ),
            _bar_gauge_panel(
                builder,
                "Required Tool Categories",
                _grid(8, 30, 8, 6),
                """
                SELECT category AS metric, COUNT(*) AS value
                FROM required_tools
                GROUP BY category
                ORDER BY COUNT(*) DESC, category;
                """,
            ),
            _bar_gauge_panel(
                builder,
                "Third-Party Service Categories",
                _grid(16, 30, 8, 6),
                """
                SELECT category AS metric, COUNT(*) AS value
                FROM third_party_services
                GROUP BY category
                ORDER BY COUNT(*) DESC, category;
                """,
            ),
        ]
    )

    panels.append(_row(builder, "Delivery Timeline", 36, collapsed=False))
    panels.append(
        _bar_gauge_panel(
            builder,
            "Delivery Timeline Summary",
            _grid(0, 37, 24, 7),
            """
            SELECT label || ' - ' || latest_result AS metric,
                   event_count AS value
            FROM delivery_timeline_summary
            ORDER BY sort_order;
            """,
        )
    )

    panels.append(_row(builder, "Release Readiness", 44, collapsed=False))
    panels.extend(
        [
            _table_panel(
                builder,
                "Release Blockers",
                _grid(0, 45, 12, 6),
                "SELECT sort_order, blocker FROM release_blockers ORDER BY sort_order;",
            ),
            _pie_panel(
                builder,
                "Risk Severity Mix",
                _grid(12, 45, 6, 6),
                """
                SELECT upper(COALESCE(NULLIF(severity, ''), 'unknown')) AS severity,
                       COUNT(*) AS value
                FROM risk_register
                GROUP BY severity
                ORDER BY value DESC, severity;
                """,
            ),
            _pie_panel(
                builder,
                "Integration Status Mix",
                _grid(18, 45, 6, 6),
                """
                SELECT upper(COALESCE(NULLIF(health, ''), 'unknown')) AS health,
                       COUNT(*) AS value
                FROM integration_status
                GROUP BY health
                ORDER BY value DESC, health;
                """,
            ),
        ]
    )

    detail_panels = [
        _table_panel(
            builder,
            "Step-by-Step Setup",
            _grid(0, 0, 24, 8),
            "SELECT sort_order, section, title, instruction, command, link_label, link_url FROM setup_steps ORDER BY sort_order;",
            links={"link_url": "Open"},
        ),
        _table_panel(
            builder,
            "Required Tools, CLIs, and SDKs",
            _grid(0, 8, 24, 8),
            """
            SELECT sort_order, name, category, purpose, check_command, install_reference, status
            FROM required_tools
            ORDER BY sort_order;
            """,
            links={"install_reference": "Open"},
        ),
        _table_panel(
            builder,
            "Third-Party Test Services",
            _grid(0, 16, 24, 8),
            """
            SELECT sort_order, name, category, purpose, required_env_vars, setup_summary, console_url, health_signal
            FROM third_party_services
            ORDER BY sort_order;
            """,
            links={"console_url": "Open"},
        ),
    ]
    panels.append(_row(builder, "Setup Details", 51, collapsed=True, panels=detail_panels))

    action_details = [
        _table_panel(
            builder,
            "All Actions",
            _grid(0, 0, 24, 9),
            """
            SELECT sort_order, action, owner_lane, why, remediation, shortcut_label, shortcut_target, source, severity
            FROM action_center
            ORDER BY sort_order;
            """,
            links={"shortcut_target": "Open"},
        )
    ]
    panels.append(_row(builder, "Action Center Details", 52, collapsed=True, panels=action_details))

    delivery_details = [
        _table_panel(
            builder,
            "Delivery Timeline Details",
            _grid(0, 0, 24, 10),
            """
            SELECT sort_order, date_label, stage_label, event, version, commit_sha, branch, result, test_results, source, url
            FROM delivery_timeline_events
            ORDER BY sort_order;
            """,
            links={"url": "Open"},
        )
    ]
    panels.append(_row(builder, "Delivery Timeline Details", 53, collapsed=True, panels=delivery_details))

    kpi_details = [
        _table_panel(
            builder,
            "Current Metrics",
            _grid(0, 0, 24, 7),
            "SELECT metric_label AS metric, value, upper(status) AS status, description FROM current_metrics ORDER BY metric_key;",
            hidden_columns=(),
        ),
        _time_series_panel(
            builder,
            "KPI Snapshots",
            _grid(0, 7, 24, 9),
            """
            SELECT generated_at AS time, metric_label AS metric, value
            FROM kpi_snapshots
            WHERE value IS NOT NULL
            ORDER BY generated_at, metric_label;
            """,
        ),
    ]
    panels.append(_row(builder, "KPI History Details", 54, collapsed=True, panels=kpi_details))

    integration_details = [
        _table_panel(
            builder,
            "Testing Service Integrations",
            _grid(0, 0, 24, 9),
            """
            SELECT sort_order, display_name, health, status, latest_run_summary, gate_role, remediation
            FROM integration_status
            ORDER BY sort_order;
            """,
        )
    ]
    panels.append(_row(builder, "Integration Status Details", 55, collapsed=True, panels=integration_details))

    freshness_details = [
        _table_panel(
            builder,
            "Data Freshness",
            _grid(0, 0, 12, 6),
            "SELECT label, value FROM data_freshness ORDER BY key;",
            hidden_columns=(),
        ),
        _table_panel(
            builder,
            "Refresh Runs",
            _grid(12, 0, 12, 6),
            """
            SELECT id, started_at, completed_at, status, error
            FROM refresh_runs
            ORDER BY id DESC
            LIMIT 20;
            """,
            hidden_columns=(),
        ),
    ]
    panels.append(_row(builder, "Data Freshness Details", 56, collapsed=True, panels=freshness_details))

    return {
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": {"type": "grafana", "uid": "-- Grafana --"},
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard",
                }
            ]
        },
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "links": [],
        "panels": panels,
        "refresh": "5m",
        "schemaVersion": 41,
        "tags": ["gt-kb", "agent-red", "sqlite"],
        "templating": {"list": []},
        "time": {"from": "now-30d", "to": "now"},
        "timepicker": {},
        "timezone": "browser",
        "title": "Agent Red GT-KB Dashboard",
        "uid": "agent-red-gtkb",
        "version": 4,
        "weekStart": "",
    }


def main() -> int:
    dashboard = build_dashboard()
    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text(json.dumps(dashboard, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {DASHBOARD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
