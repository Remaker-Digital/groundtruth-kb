"""Retirement regression and current native dashboard observations.

Preserve read-only observation, repeatability, isolation and useful failure
visibility through current native routes without reviving retired coordination.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess

import pytest
from groundtruth_kb import dashboard


def _ready():
    return {"reachable": True, "ready": True, "schema_catalog_matches": True}


def _report(*, claims=0, eligible=0, blocked=0):
    return {
        "active_claim_count": claims,
        "queues": {
            "pb": {"role": "pb", "eligible": [{}] * eligible, "blocked": [{}] * blocked},
            "lo": {"role": "lo", "eligible": [], "blocked": []},
        },
    }


def _probes(monkeypatch, authority, report):
    from groundtruth_kb.authority_client import AuthorityClient
    from groundtruth_kb.config import GTConfig

    calls = []

    def probe(root, args, timeout=20):
        calls.append(args)
        assert args[0] == "git"
        return subprocess.CompletedProcess(args, 0, "## test\n", "")

    def read(self, method, route, **kwargs):
        assert method == "GET" and not kwargs
        calls.append([method, route])
        assert route in ("/v1/status", "/v1/bridge/state-report")
        return authority if route == "/v1/status" else report

    monkeypatch.setattr(
        GTConfig,
        "load",
        lambda **kwargs: GTConfig(project_root=kwargs["config_path"].parent, authority_url="http://127.0.0.1:39899"),
    )
    monkeypatch.setattr(AuthorityClient, "request", read)
    monkeypatch.setattr(dashboard, "_run_release_probe", probe)
    return calls


def test_current_refresh_does_not_open_or_project_retired_state(tmp_path, monkeypatch):
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"Retired source must not be opened or changed.")
    before = sentinel.read_bytes()
    monkeypatch.setattr(dashboard, "_write_bridge_swimlane_safe", lambda *args: None)
    model = {"generated_at": "2026-09-12T18:00:00+00:00", "metrics": {}, "dashboard_intelligence": {}}
    path = tmp_path / "dashboard.sqlite"
    for _ in range(2):
        assert dashboard.refresh_database(path, tmp_path, model=model, history=[])["status"] == "completed"
    assert sentinel.read_bytes() == before
    with sqlite3.connect(path) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert not any(name.startswith("tafe_") for name in tables)
        assert conn.execute("SELECT COUNT(*) FROM refresh_runs WHERE status='completed'").fetchone()[0] == 2
    assert not (tmp_path / "harness-state").exists()
    assert not (tmp_path / ".claude").exists()


@pytest.mark.parametrize(
    "value,expected",
    [
        (_ready(), ("green", "ready")),
        ({**_ready(), "ready": False}, ("red", "not_ready")),
        ({**_ready(), "reachable": False}, ("red", "not_ready")),
        ({**_ready(), "schema_catalog_matches": False}, ("red", "not_ready")),
        ({**_ready(), "ready": "true"}, ("yellow", "live_state_unavailable")),
        ({}, ("yellow", "live_state_unavailable")),
        ([], ("yellow", "live_state_unavailable")),
        (None, ("yellow", "live_state_unavailable")),
        ({"_probe_error": "private service detail must not be relayed"}, ("yellow", "live_state_unavailable")),
    ],
)
def test_native_authority_observations_are_typed_and_bounded(monkeypatch, tmp_path, value, expected):
    calls = _probes(monkeypatch, value, _report())
    result = dashboard._native_authority_live_status(tmp_path)
    assert (result["health"], result["status"]) == expected
    assert "private service detail" not in json.dumps(result)
    assert calls == [["GET", "/v1/status"]]


def test_current_observation_routes_are_read_only_and_repeatable(monkeypatch, tmp_path):
    calls = _probes(monkeypatch, _ready(), _report())
    first = dashboard._live_release_health_findings(tmp_path)
    second = dashboard._live_release_health_findings(tmp_path)
    assert first == second
    assert (
        calls
        == [
            ["git", "status", "--short", "--branch"],
            ["GET", "/v1/status"],
            ["GET", "/v1/bridge/state-report"],
        ]
        * 2
    )
    assert not dashboard._visible_release_findings(first)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("report", [None, [], {}, {"active_claim_count": True, "queues": {}}, _report(claims=-1)])
def test_missing_or_malformed_bridge_observations_remain_visible(monkeypatch, tmp_path, report):
    _probes(monkeypatch, _ready(), report)
    findings = dashboard._live_release_health_findings(tmp_path)
    visible = dashboard._visible_release_findings(findings)
    assert len(visible) == 1 and visible[0]["source"] == "bridge"
    assert visible[0]["severity"] == "yellow"
    assert "unavailable" in visible[0]["message"] or "malformed" in visible[0]["message"]


def test_queue_observation_does_not_dispatch_or_assign_thread_ownership(monkeypatch, tmp_path):
    _probes(monkeypatch, _ready(), _report(claims=2, eligible=3, blocked=1))
    findings = dashboard._live_release_health_findings(tmp_path)
    bridge = next(row for row in findings if row["source"] == "bridge")
    assert "2 active next-artifact claim(s), 3 eligible and 1 blocked action(s)" in bridge["message"]
    assert "does not dispatch work or establish release readiness" in bridge["message"]
    assert bridge["severity"] == "yellow" and bridge["release_visible"] is True
    _probes(monkeypatch, _ready(), _report(eligible=3))
    findings = dashboard._live_release_health_findings(tmp_path)
    assert not dashboard._visible_release_findings(findings)


def test_unknown_authority_metric_is_not_a_zero_or_healthy_result():
    rows = {row[0]: row for row in dashboard._current_metric_rows({}, {}, [])}
    assert rows["native_authority_findings"][2:4] == (None, "yellow")
    assert "dispatcher_health_findings" not in rows


def test_git_probe_uses_selected_root_without_shell(monkeypatch, tmp_path):
    captured = {}

    def run(args, **kwargs):
        captured.update(args=args, kwargs=kwargs)
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(dashboard.subprocess, "run", run)
    dashboard._run_release_probe(tmp_path, ["git", "status", "--short"])
    assert captured["args"] == ["git", "status", "--short"]
    assert not captured["kwargs"].get("shell")
    assert captured["kwargs"]["cwd"] == tmp_path


def test_retired_projection_helpers_are_removed():
    for name in (
        "_refresh_tafe_projection",
        "_refresh_tafe_projection_safe",
        "_migrate_tafe_projection_schema",
        "_dispatcher_supervisor_live_status",
    ):
        assert not hasattr(dashboard, name)
