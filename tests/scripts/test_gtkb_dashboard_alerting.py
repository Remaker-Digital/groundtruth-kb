"""Tests for GTKB-DASHBOARD-001 Slice 1 Â§E alert-rule YAML skeleton.

Enforces the three GO -006 conditions:

1. Alert YAMLs are bound to exact authoritative source names (no alias drift
   back to the rejected ``release_blocker_count`` / ``failing_ci_count`` /
   ``data_freshness_age_minutes`` placeholders).
2. This test asserts the exact ``metric_key`` literals for the two
   ``current_metrics``-backed rules in addition to table-level schema
   anchoring, so future edits cannot silently drift back to placeholder names.
3. Rules are schema-anchored: every table referenced in the alert SQL must
   exist in ``schema.sql``.

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

try:  # PyYAML is a project dep via pytest plugins; import lazily so the test
    # surface gives a clear error if it isn't installed.
    import yaml
except ImportError as exc:  # pragma: no cover - surface install hint
    pytest.skip(f"PyYAML required for alert YAML validation: {exc}", allow_module_level=True)

from scripts.gtkb_dashboard.refresh_dashboard_db import refresh_database

REPO_ROOT = Path(__file__).resolve().parents[2]
ALERTING_DIR = REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "provisioning" / "alerting"
SCHEMA_SQL = REPO_ROOT / "scripts" / "gtkb_dashboard" / "schema.sql"

# Exact metric_key literals Codex mandated (GO -006 condition 2). Alias drift
# back to the rejected names would be caught by these equality assertions.
EXPECTED_RELEASE_BLOCKERS_METRIC_KEY = "release_blockers"
EXPECTED_FAILING_CI_METRIC_KEY = "ci_testing_failing"
REJECTED_ALIASES = {
    "release_blocker_count",
    "failing_ci_count",
    "data_freshness_age_minutes",
}


def _schema_tables() -> set[str]:
    text = SCHEMA_SQL.read_text(encoding="utf-8")
    return set(re.findall(r"CREATE TABLE IF NOT EXISTS\s+([A-Za-z_][A-Za-z_0-9]*)", text))


def _tables_referenced_by_sql(sql: str) -> set[str]:
    """Approximate tables-referenced parse: capture identifiers following FROM/JOIN."""
    return set(re.findall(r"(?i)(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z_0-9]*)", sql))


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _first_rule(doc: dict) -> dict:
    groups = doc["groups"]
    assert groups, "alert YAML must declare at least one group"
    rules = groups[0]["rules"]
    assert rules, "alert group must declare at least one rule"
    return rules[0]


def _raw_sql(rule: dict) -> str:
    return rule["data"][0]["model"]["rawQueryText"]


# ---------- Structure ----------


def test_all_three_alert_yamls_present_and_parse() -> None:
    """Proposal Â§E validator requirement #1 + #2: each YAML parses and carries
    the required keys ``uid``, ``title``, ``condition``, ``data[0].model.rawSql``."""
    for name in ("release-blockers.yaml", "failing-ci.yaml", "stale-data.yaml"):
        path = ALERTING_DIR / name
        assert path.exists(), f"missing alert YAML: {path}"
        doc = _load_yaml(path)
        assert doc["apiVersion"] == 1
        assert doc["groups"], f"{name} must declare groups"
        rule = _first_rule(doc)
        for key in ("uid", "title", "condition", "data"):
            assert key in rule, f"{name} rule missing required key {key!r}"
        # Proposal Â§E specifies data[0].model.rawSql as a required key. The
        # runtime reads rawQueryText (frser-sqlite-datasource), so we require
        # both to prevent the proposal-vs-runtime key from drifting apart.
        model = rule["data"][0]["model"]
        assert "rawSql" in model, (
            f"{name} data[0].model missing required key 'rawSql' (proposal Â§E)"
        )
        assert "rawQueryText" in model, (
            f"{name} data[0].model missing 'rawQueryText' (frser-sqlite-datasource runtime key)"
        )
        assert model["rawSql"].strip() == model["rawQueryText"].strip(), (
            f"{name} rawSql and rawQueryText must be the same SQL text"
        )


# ---------- Exact metric_key literals (GO condition 2) ----------


def test_release_blockers_uses_exact_authoritative_metric_key() -> None:
    rule = _first_rule(_load_yaml(ALERTING_DIR / "release-blockers.yaml"))
    sql = _raw_sql(rule)
    assert f"metric_key = '{EXPECTED_RELEASE_BLOCKERS_METRIC_KEY}'" in sql, (
        f"release-blockers.yaml must reference exact metric_key "
        f"{EXPECTED_RELEASE_BLOCKERS_METRIC_KEY!r}; got: {sql!r}"
    )
    assert rule["annotations"]["source_metric_key"] == EXPECTED_RELEASE_BLOCKERS_METRIC_KEY


def test_failing_ci_uses_exact_authoritative_metric_key() -> None:
    rule = _first_rule(_load_yaml(ALERTING_DIR / "failing-ci.yaml"))
    sql = _raw_sql(rule)
    assert f"metric_key = '{EXPECTED_FAILING_CI_METRIC_KEY}'" in sql, (
        f"failing-ci.yaml must reference exact metric_key "
        f"{EXPECTED_FAILING_CI_METRIC_KEY!r}; got: {sql!r}"
    )
    assert rule["annotations"]["source_metric_key"] == EXPECTED_FAILING_CI_METRIC_KEY


def test_no_rejected_alias_metric_names_in_any_yaml() -> None:
    for path in sorted(ALERTING_DIR.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        for rejected in REJECTED_ALIASES:
            assert rejected not in text, (
                f"{path.name} references rejected alias {rejected!r}; use the "
                "authoritative metric_key emitted by refresh_dashboard_db.py"
            )


# ---------- Schema anchoring (GO condition references) ----------


def test_every_alert_sql_references_only_tables_in_schema() -> None:
    schema = _schema_tables()
    assert "current_metrics" in schema and "refresh_runs" in schema, (
        "schema sanity precondition failed; cannot validate alert anchoring"
    )
    for path in sorted(ALERTING_DIR.glob("*.yaml")):
        rule = _first_rule(_load_yaml(path))
        sql = _raw_sql(rule)
        referenced = _tables_referenced_by_sql(sql)
        assert referenced, f"{path.name} SQL references no tables; suspicious"
        orphans = referenced - schema
        assert not orphans, (
            f"{path.name} references table(s) not in schema.sql: {sorted(orphans)}"
        )


def test_stale_data_rule_uses_refresh_runs() -> None:
    rule = _first_rule(_load_yaml(ALERTING_DIR / "stale-data.yaml"))
    sql = _raw_sql(rule)
    assert "refresh_runs" in sql
    # The rule must compute minutes via julianday, matching the generator's
    # Refresh Age panel pattern (not a persisted metric key).
    assert "julianday" in sql
    assert rule["annotations"]["source_table"] == "refresh_runs"


# ---------- Live-emission fixture (proves the metric_key is actually written) ----------


def _sample_model() -> dict:
    return {
        "generated_at": "2026-04-24T00:00:00+00:00",
        "role": {"assumed_role": "Prime Builder"},
        "dashboard_requirements": {"scope_note": "GroundTruth-KB project dashboard."},
        "metrics": {
            "contention": {"actionable_count": 0},
            "drift": {"changed_path_count": 0},
            "regression": {"release_blocker_count": 1},
        },
        "dashboard_intelligence": {
            "health": [],
            "shortcuts": [],
            "action_center": [],
            "release_readiness": {"blockers": [], "blocker_count": 1},
            "quality_rollup": {"total": 0, "failing": 2, "manual": 0, "unknown": 0, "ready_or_passing": 0},
            "risk_register": [],
            "data_freshness": {"generated_at": "2026-04-24T00:00:00+00:00"},
        },
        "infrastructure": {
            "delivery_timeline": {"stage_summary": [], "timeline": []},
            "testing_service_integrations": {},
        },
    }


def test_refresh_pipeline_actually_emits_the_alert_metric_keys(tmp_path) -> None:
    """The two current_metrics-backed rules fire against keys the pipeline emits.

    This closes Codex's -004 concern that "structurally valid alert YAML and a
    passing parse test could coexist with signals that never fire." If the
    refresh pipeline ever drops these keys, this test fails before alerts can
    silently no-op in production.
    """
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    refresh_database(db_path=db_path, project_root=REPO_ROOT, model=_sample_model(), history=[])
    with sqlite3.connect(db_path) as conn:
        emitted = {
            row[0]
            for row in conn.execute("SELECT metric_key FROM current_metrics")
        }
    assert EXPECTED_RELEASE_BLOCKERS_METRIC_KEY in emitted, (
        f"refresh pipeline did not emit {EXPECTED_RELEASE_BLOCKERS_METRIC_KEY!r} "
        f"into current_metrics; alert rule would never fire. Emitted keys: {sorted(emitted)}"
    )
    assert EXPECTED_FAILING_CI_METRIC_KEY in emitted, (
        f"refresh pipeline did not emit {EXPECTED_FAILING_CI_METRIC_KEY!r} "
        f"into current_metrics; alert rule would never fire. Emitted keys: {sorted(emitted)}"
    )
