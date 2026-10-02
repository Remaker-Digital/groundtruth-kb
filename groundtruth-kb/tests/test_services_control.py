"""GT-KB's local services inventory (the GT-KB Home services page and `gt services`), exercised with a fake runner."""

from __future__ import annotations

import inspect
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


REPO = Path(__file__).resolve().parents[2]
# c123 (batch design WP3 3.3): what a script that starts or stops a task, a process or the service runs.
CHANGES = (
    "Enable-ScheduledTask",
    "Disable-ScheduledTask",
    "Start-ScheduledTask",
    "taskkill",
    "Start-Service",
    "Stop-Service",
)


def _task_read(task: str) -> str:
    """c123 (batch design WP3 3.3): the fragment of one task's ownership read."""
    return f"Get-ScheduledTask -TaskName '{task}'"


def _registered(root: Path, *, state: str = "Ready", service: str = "Running") -> list[tuple[str, str, int]]:
    """c123 (batch design WP3 3.3): FakeRunner rules that answer every task and service read as registered for root.

    The texts have the registration scripts' form: each task action's Execute and Arguments, and pg_ctl's PathName.
    """
    pythonw = root / "groundtruth-kb" / ".venv" / "Scripts" / "pythonw.exe"
    postgresql = root / "infrastructure" / "postgresql"
    actions = {
        "GTKB-DomainService": f'{pythonw} "{postgresql / "domain_service_launcher.py"}" --root "{root}" --port 8765',
        "GTKB-Home": f'{pythonw} -B "{root / "infrastructure" / "deepseek-web" / "home.py"}" start',
        "GTKB-Ollama-Serve": "C:\\Programs\\Ollama\\ollama.exe serve",
    }
    rules = [(_task_read(task), json.dumps({"state": state, "action": action}), 0) for task, action in actions.items()]
    control = postgresql / "runtime" / "fixture" / "bin" / "pg_ctl.exe"
    path = f'"{control}" runservice -N "gtkb-postgresql" -D "{postgresql / "data"}" -w'
    return [*rules, ("Win32_Service", json.dumps({"state": service, "path": path}), 0)]


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
            # c123 (batch design WP3 3.3): every other read answers as this installation's own registration.
            *_registered(installation.root, service="Stopped"),
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
    runner = FakeRunner([*_registered(installation.root), ("Get-CimInstance", "4242\n", 0)])
    result = services_control.stop(installation, "authority", runner)
    scripts = runner.scripts()
    # c123 (batch design WP3 3.3): the ownership read comes first, then the pause, then the launcher's end.
    assert _task_read("GTKB-DomainService") in scripts[0]
    assert scripts[1].startswith("Disable-ScheduledTask -TaskName 'GTKB-DomainService'")
    launcher = str(installation.root / "infrastructure" / "postgresql" / "domain_service_launcher.py")
    assert f"*{launcher}*" in scripts[2] and "*--root*" in scripts[2]
    assert result == {
        "service": "authority",
        "stopped": True,
        "ended_pids": [4242],
        "detail": "task GTKB-DomainService disabled",
    }


def test_starting_the_authority_resumes_and_runs_its_task_then_waits_for_readiness(installation, ready):
    runner = FakeRunner(_registered(installation.root))
    result = services_control.start(installation, "authority", runner)
    # c123 (batch design WP3 3.3): the ownership read comes first; the task changes follow it.
    assert _task_read("GTKB-DomainService") in runner.scripts()[0]
    assert [script.split(" -TaskName")[0] for script in runner.scripts()[1:]] == [
        "Enable-ScheduledTask",
        "Start-ScheduledTask",
    ]
    assert result["started"] is False and result["detail"] == "task started; not ready yet"
    ready.add("http://127.0.0.1:8765")
    assert services_control.start(installation, "authority", FakeRunner(_registered(installation.root)))["started"]


def test_a_task_that_cannot_be_paused_stops_nothing(installation, ready):
    runner = FakeRunner([*_registered(installation.root), ("Disable-ScheduledTask", "Access is denied.", 1)])
    with pytest.raises(services_control.ServiceControlError, match="Disable-ScheduledTask GTKB-DomainService failed"):
        services_control.stop(installation, "authority", runner)
    assert not any("taskkill" in script for script in runner.scripts())


def test_postgresql_refusal_is_reported_not_worked_around(installation, ready):
    runner = FakeRunner(
        [
            *_registered(installation.root, service="Stopped"),
            ("Start-Service", "Cannot open gtkb-postgresql service: Access is denied.", 1),
        ]
    )
    with pytest.raises(services_control.ServiceControlError, match="an administrator may be required"):
        services_control.start(installation, "postgresql", runner)
    # c123 (batch design WP3 3.3): the ownership read, then the one refused start.
    assert len(runner.calls) == 2 and "Win32_Service" in runner.scripts()[0]


def test_home_runs_its_launcher_and_touches_its_task_only_when_registered(installation, ready):
    runner = FakeRunner([("Get-ScheduledTask", "", 0), ("home.py stop", json.dumps({"action": "stop", "ok": True}), 0)])
    assert services_control.stop(installation, "home", runner)["stopped"] is True
    assert runner.calls[-1] == ["py.exe", "-B", str(installation.home_script), "stop"]
    assert not any("Disable-ScheduledTask" in script for script in runner.scripts())
    # c123 (batch design WP3 3.3): registered means registered by this installation: the action names its home.py.
    registered = FakeRunner(
        [*_registered(installation.root), ("home.py start", json.dumps({"action": "start", "ok": True}), 0)]
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
    ollama = FakeRunner(_registered(installation.root))
    assert services_control.stop(installation, "ollama", ollama)["stopped"] is True
    # c123 (batch design WP3 3.3): the GTKB-Home ownership read comes first (Ollama follows GTKB-Home).
    assert _task_read("GTKB-Home") in ollama.scripts()[0]
    assert ollama.scripts()[1].startswith("Disable-ScheduledTask -TaskName 'GTKB-Ollama-Serve'")
    assert "*ollama*" in ollama.scripts()[2] and "*serve*" in ollama.scripts()[2]


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


def test_rows_another_installation_registered_are_status_only_and_name_their_owner(installation, ready):
    """c123 (batch design WP3 3.3): a row this installation does not own keeps its observed state, offers no action
    and names its owner. home.py stays this root's own; only the owner of the GTKB-Home task is named."""
    ready.update({"http://127.0.0.1:8765", "http://127.0.0.1:8766", "http://127.0.0.1:11434"})
    production = installation.root.parent / "GT-KB"
    report = json.dumps({"action": "status", "ok": True, "running": True, "live": True, "port": 3080})
    runner = FakeRunner([*_registered(production), ("home.py status", report, 0)])
    rows = {row.name: row for row in services_control.status(installation, runner)}
    for name in ("authority", "ollama", "postgresql"):
        row = rows[name]
        assert (row.state, row.can_start, row.can_stop) == ("running", False, False), row
        assert str(production) in row.detail and row.detail.endswith("; status only"), row
    assert "the installation that owns task GTKB-Home" in rows["ollama"].detail
    dashboard = rows["dashboard"]
    assert (dashboard.state, dashboard.can_start, dashboard.can_stop) == ("unknown", False, False)
    assert "launch record" in dashboard.detail and dashboard.detail.endswith("; status only")
    home = rows["home"]
    assert (home.state, home.can_stop) == ("running", True), "home.py is this root's own"
    assert str(production / "infrastructure" / "deepseek-web" / "home.py") in home.detail


@pytest.mark.parametrize("name", ["authority", "ollama", "postgresql"])
def test_start_and_stop_refuse_a_row_this_installation_does_not_own_before_any_change(installation, ready, name):
    """c123 (batch design WP3 3.3): one ownership read, then a refusal that names the owner or says that nothing is
    registered; no task, process or service is touched."""
    production = installation.root.parent / "GT-KB"
    for rules, named in ((_registered(production), str(production)), ([], "is not registered")):
        for action in (services_control.start, services_control.stop):
            runner = FakeRunner(rules)
            with pytest.raises(services_control.ServiceControlError, match="this installation does not") as refused:
                action(installation, name, runner)
            assert named in str(refused.value), refused.value
            assert len(runner.calls) == 1 and not any(change in runner.scripts()[0] for change in CHANGES)


def test_home_runs_this_roots_launcher_and_leaves_another_installations_task_alone(installation, ready):
    """c123 (batch design WP3 3.3): with GTKB-Home registered by another installation, start and stop run this root's
    home.py and neither resume nor pause that task."""
    production = installation.root.parent / "GT-KB"
    for verb, outcome in (("stop", "stopped"), ("start", "started")):
        answer = (f"home.py {verb}", json.dumps({"action": verb, "ok": True}), 0)
        runner = FakeRunner([*_registered(production), answer])
        assert getattr(services_control, verb)(installation, "home", runner)[outcome] is True
        assert runner.calls[-1] == ["py.exe", "-B", str(installation.home_script), verb]
        assert not [script for script in runner.scripts() if any(change in script for change in CHANGES)]


def test_a_dashboard_answering_without_this_roots_launch_record_offers_no_action(installation, ready):
    """c123 (batch design WP3 3.3): `gt dashboard` acts only on this root's own launch, so port 8766 answering without
    this root's launch record is another installation's dashboard and the row is status only."""
    ready.add("http://127.0.0.1:8766")
    (row,) = services_control.status(installation, FakeRunner(), only="dashboard")
    assert (row.state, row.can_start, row.can_stop) == ("unknown", False, False)
    assert "dashboard-launch.json" in row.detail and row.detail.endswith("; status only")
    record = installation.root / ".groundtruth" / "dashboard" / "dashboard-launch.json"
    record.parent.mkdir(parents=True)
    record.write_text("{}\n", encoding="utf-8")
    (row,) = services_control.status(installation, FakeRunner(), only="dashboard")
    assert (row.state, row.detail, row.can_start, row.can_stop) == (
        "running",
        services_control.DASHBOARD_HEALTH,
        False,
        True,
    )


def test_the_ownership_rule_mirrors_the_registration_scripts():
    """c123 (batch design WP3 3.3): services_control applies the rule these scripts apply before they change a task or
    the service. When a script's rule changes, change this mirror with it."""
    installation = services_control.Installation(
        root=Path("E:/GT-KB"), authority_url="http://127.0.0.1:8765", python=Path("py.exe")
    )
    domain = "infrastructure/postgresql/register-domain-service.ps1"
    home = "infrastructure/deepseek-web/register-home-task.ps1"
    service = "infrastructure/postgresql/register-service.ps1"
    for script, folder, name, mirrored in (
        (domain, r"infrastructure\postgresql", "domain_service_launcher.py", installation.authority_launcher),
        (home, r"infrastructure\deepseek-web", "home.py", installation.home_script),
        (service, r"infrastructure\postgresql", "data", installation.postgresql_data),
    ):
        text = (REPO / script).read_text(encoding="utf-8")
        assert f"$installation = Join-Path $resolvedRoot '{folder}'" in text, script
        assert f"Join-Path $installation '{name}'" in text, script
        assert mirrored.relative_to(installation.root).parts == (*folder.split("\\"), name), script
    action = "($existing.Actions | ForEach-Object { $_.Execute + ' ' + $_.Arguments }) -join ' '"
    for script in (domain, home):
        text = (REPO / script).read_text(encoding="utf-8")
        assert f"$current = {action}" in text and "if (-not $current.Contains($launcher))" in text, script
    assert "-not $existing.PathName.Contains($dataDirectory)" in (REPO / service).read_text(encoding="utf-8")
    assert "$_.Execute + ' ' + $_.Arguments" in inspect.getsource(services_control._task)
    assert "$s.PathName" in inspect.getsource(services_control._service)
