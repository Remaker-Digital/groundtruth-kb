"""GT-KB's local services inventory (the GT-KB Home services page and `gt services`), exercised with a fake runner."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb import services_control
from groundtruth_kb.cli import main


class FakeRunner:
    """Records every argument vector and answers from (fragment, stdout, returncode) rules, first match wins."""

    def __init__(self, rules=()):
        self.rules = list(rules)
        self.calls: list[list[str]] = []

    def __call__(self, argv, timeout):
        self.calls.append(list(argv))
        text = " ".join(argv)
        for fragment, stdout, code in self.rules:
            if fragment in text:
                return subprocess.CompletedProcess(argv, code, stdout=stdout, stderr="" if code == 0 else stdout)
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    def scripts(self):
        return [call[-1] for call in self.calls if call[:1] == ["powershell"]]


@pytest.fixture
def installation(tmp_path):
    return services_control.Installation(root=tmp_path, authority_url="http://127.0.0.1:8765", python=Path("py.exe"))


@pytest.fixture
def ready(monkeypatch):
    """Which HTTP readiness probes answer; the wait loop evaluates its predicate once."""
    answering: set[str] = set()
    monkeypatch.setattr(services_control, "_get_ok", lambda url, timeout=5: any(url.startswith(u) for u in answering))
    monkeypatch.setattr(services_control, "_wait", lambda predicate, seconds: predicate())
    return answering


def test_status_reports_state_and_applicable_actions(installation, ready):
    ready.add("http://127.0.0.1:8765")
    runner = FakeRunner(
        [
            (
                "home.py status",
                json.dumps({"action": "status", "ok": True, "running": True, "live": True, "port": 3080}),
                0,
            ),
            ("GTKB-Ollama-Serve", "", 0),
            ("Get-ScheduledTask", "Ready", 0),
            ("Get-Service", "Stopped", 0),
        ]
    )
    rows = {row["name"]: row for row in services_control.as_json(services_control.status(installation, runner))}
    assert list(rows) == list(services_control.SERVICES)
    assert rows["authority"] | {"detail": None} == {
        "name": "authority",
        "state": "running",
        "detail": None,
        "can_start": False,
        "can_stop": True,
    }
    assert rows["home"]["state"] == "running" and rows["home"]["can_stop"]
    assert rows["dashboard"]["state"] == "stopped" and rows["dashboard"]["can_start"]
    assert rows["ollama"]["state"] == "stopped" and not rows["ollama"]["can_start"], "no logon task, nothing to start"
    assert rows["postgresql"]["state"] == "stopped" and rows["postgresql"]["can_start"]


def test_unknown_service_is_refused(installation, ready):
    with pytest.raises(services_control.ServiceControlError, match="Unknown service"):
        services_control.status(installation, FakeRunner(), only="grafana")
    for action in (services_control.start, services_control.stop):
        with pytest.raises(services_control.ServiceControlError, match="Unknown service"):
            action(installation, "grafana", FakeRunner())


def test_stopping_the_authority_pauses_its_task_before_ending_this_installations_launcher(installation, ready):
    runner = FakeRunner([("Get-CimInstance", "4242\n", 0)])
    result = services_control.stop(installation, "authority", runner)
    scripts = runner.scripts()
    assert scripts[0].startswith("Disable-ScheduledTask -TaskName 'GTKB-DomainService'")
    launcher = str(installation.root / "infrastructure" / "postgresql" / "domain_service_launcher.py")
    assert f"*{launcher}*" in scripts[1] and "*--root*" in scripts[1]
    assert result == {
        "service": "authority",
        "stopped": True,
        "ended_pids": [4242],
        "detail": "task GTKB-DomainService disabled",
    }


def test_starting_the_authority_resumes_and_runs_its_task_then_waits_for_readiness(installation, ready):
    runner = FakeRunner()
    result = services_control.start(installation, "authority", runner)
    assert [script.split(" -TaskName")[0] for script in runner.scripts()] == [
        "Enable-ScheduledTask",
        "Start-ScheduledTask",
    ]
    assert result["started"] is False and result["detail"] == "task started; not ready yet"
    ready.add("http://127.0.0.1:8765")
    assert services_control.start(installation, "authority", FakeRunner())["started"] is True


def test_a_task_that_cannot_be_paused_stops_nothing(installation, ready):
    runner = FakeRunner([("Disable-ScheduledTask", "Access is denied.", 1)])
    with pytest.raises(services_control.ServiceControlError, match="Disable-ScheduledTask GTKB-DomainService failed"):
        services_control.stop(installation, "authority", runner)
    assert not any("taskkill" in script for script in runner.scripts())


def test_postgresql_refusal_is_reported_not_worked_around(installation, ready):
    runner = FakeRunner([("Start-Service", "Cannot open gtkb-postgresql service: Access is denied.", 1)])
    with pytest.raises(services_control.ServiceControlError, match="an administrator may be required"):
        services_control.start(installation, "postgresql", runner)
    assert len(runner.calls) == 1


def test_home_runs_its_launcher_and_touches_its_task_only_when_registered(installation, ready):
    runner = FakeRunner([("Get-ScheduledTask", "", 0), ("home.py stop", json.dumps({"action": "stop", "ok": True}), 0)])
    assert services_control.stop(installation, "home", runner)["stopped"] is True
    assert runner.calls[-1] == ["py.exe", "-B", str(installation.home_script), "stop"]
    assert not any("Disable-ScheduledTask" in script for script in runner.scripts())
    registered = FakeRunner(
        [("Get-ScheduledTask", "Ready", 0), ("home.py start", json.dumps({"action": "start", "ok": True}), 0)]
    )
    assert services_control.start(installation, "home", registered)["started"] is True
    assert any(script.startswith("Enable-ScheduledTask -TaskName 'GTKB-Home'") for script in registered.scripts())


def test_home_launcher_without_json_is_an_error(installation, ready):
    with pytest.raises(services_control.ServiceControlError, match="home.py status gave no JSON"):
        services_control.status(installation, FakeRunner([("home.py", "Traceback ...", 1)]), only="home")


def test_dashboard_and_ollama_use_their_own_mechanisms(installation, ready):
    runner = FakeRunner()
    services_control.start(installation, "dashboard", runner)
    services_control.stop(installation, "dashboard", runner)
    assert runner.calls == [
        ["py.exe", "-m", "groundtruth_kb", "dashboard", "start", "--json"],
        ["py.exe", "-m", "groundtruth_kb", "dashboard", "stop", "--json"],
    ]
    ollama = FakeRunner()
    assert services_control.stop(installation, "ollama", ollama)["stopped"] is True
    assert ollama.scripts()[0].startswith("Disable-ScheduledTask -TaskName 'GTKB-Ollama-Serve'")
    assert "*ollama*" in ollama.scripts()[1] and "*serve*" in ollama.scripts()[1]


def test_quoting_keeps_names_inside_one_powershell_literal():
    assert services_control._quote("it's") == "'it''s'"


def test_cli_exposes_services_and_home(monkeypatch, tmp_path):
    runner = CliRunner()
    for group, commands in (("services", ("status", "start", "stop")), ("home", ("start", "stop", "status", "open"))):
        result = runner.invoke(main, [group, "--help"])
        assert result.exit_code == 0, result.output
        assert all(command in result.output for command in commands)
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")
    fixed = [services_control.ServiceState("dashboard", "stopped", "http://127.0.0.1:8766/health", True, False)]
    monkeypatch.setattr(services_control, "status", lambda installation, only=None: fixed)
    result = runner.invoke(main, ["--config", str(config), "services", "status", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == services_control.as_json(fixed)
