"""GT-KB's local services inventory (the GT-KB Home services page and `gt services`), exercised with a fake runner."""

from __future__ import annotations

import inspect
import json
import subprocess
from contextlib import contextmanager
from dataclasses import replace
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
    # Legacy per-service cases fake Home's observed runtime separately from its stop JSON.
    monkeypatch.setattr(services_control, "_home_stop_state", lambda *args: services_control._Observed(False, False))
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


def test_stopping_the_authority_pauses_its_task_before_ending_this_installations_launcher(
    installation, ready, monkeypatch
):
    identity = {"pid": 4242, "created_at": "known-creation", "executable": "installed-pythonw.exe"}
    controller = services_control._Controller("authority", services_control.AUTHORITY_TASK)
    monkeypatch.setattr(services_control, "_task_stop_plan", lambda *args: (controller, (identity,)))
    monkeypatch.setattr(
        services_control,
        "_end_identified",
        lambda runner, identities: [
            runner(["taskkill", "/PID", str(item["pid"]), "/T", "/F"], 15) for item in identities
        ],
    )
    runner = FakeRunner(_registered(installation.root))
    result = services_control.stop(installation, "authority", runner)
    scripts = runner.scripts()
    # c123 (batch design WP3 3.3): the ownership read comes first, then the pause, then the launcher's end.
    assert _task_read("GTKB-DomainService") in scripts[0]
    assert scripts[1].startswith("Disable-ScheduledTask -TaskName 'GTKB-DomainService'")
    assert runner.calls[-1] == ["taskkill", "/PID", "4242", "/T", "/F"]
    assert not any("-like" in script for script in scripts)
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


def test_a_task_that_cannot_be_paused_stops_nothing(installation, ready, monkeypatch):
    monkeypatch.setattr(
        services_control,
        "_task_stop_plan",
        lambda *args: (services_control._Controller("authority", services_control.AUTHORITY_TASK), ()),
    )
    runner = FakeRunner([*_registered(installation.root), ("Disable-ScheduledTask", "Access is denied.", 1)])
    with pytest.raises(services_control.ServiceControlError, match="Disable-ScheduledTask GTKB-DomainService failed"):
        services_control.stop(installation, "authority", runner)
    assert not any("taskkill" in call for call in runner.calls)


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


def test_dashboard_and_ollama_use_their_own_mechanisms(installation, ready, monkeypatch):
    runner = FakeRunner()
    services_control.start(installation, "dashboard", runner)
    services_control.stop(installation, "dashboard", runner)
    assert runner.calls == [
        [
            "py.exe",
            "-m",
            "groundtruth_kb",
            "--config",
            str(installation.root / "groundtruth.toml"),
            "dashboard",
            "start",
            "--json",
        ],
        [
            "py.exe",
            "-m",
            "groundtruth_kb",
            "--config",
            str(installation.root / "groundtruth.toml"),
            "dashboard",
            "stop",
            "--json",
        ],
    ]
    controller = services_control._Controller("ollama", services_control.OLLAMA_TASK)
    identity = {"pid": 4242, "created_at": "known-creation", "executable": "installed-ollama.exe"}
    monkeypatch.setattr(services_control, "_task_stop_plan", lambda *args: (controller, (identity,)))
    monkeypatch.setattr(
        services_control,
        "_end_identified",
        lambda runner, identities: [
            runner(["taskkill", "/PID", str(item["pid"]), "/T", "/F"], 15) for item in identities
        ],
    )
    ollama = FakeRunner(_registered(installation.root))
    assert services_control.stop(installation, "ollama", ollama)["stopped"] is True
    # c123 (batch design WP3 3.3): the GTKB-Home ownership read comes first (Ollama follows GTKB-Home).
    assert _task_read("GTKB-Home") in ollama.scripts()[0]
    assert ollama.scripts()[1].startswith("Disable-ScheduledTask -TaskName 'GTKB-Ollama-Serve'")
    assert ollama.calls[-1] == ["taskkill", "/PID", "4242", "/T", "/F"]
    assert not any("-like" in script for script in ollama.scripts())


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


class AggregateHost:
    """A stateful controller adapter: independent observed state, partial requests and permission refusals."""

    def __init__(self, monkeypatch, states, failure=None):
        tasks = {
            "authority": services_control.AUTHORITY_TASK,
            "home": services_control.HOME_TASK,
            "ollama": services_control.OLLAMA_TASK,
        }
        self.controllers = [
            services_control._Controller(name, tasks.get(name))
            for name in services_control.START_ORDER
            if name in states
        ]
        self.states = dict(states)
        self.actions = []
        self.task_changes = []
        self.failure = failure
        self.next_pid = 1000
        monkeypatch.setattr(services_control, "_inventory", lambda *args: (self.controllers, {}))
        monkeypatch.setattr(
            services_control, "_observe", lambda installation, controller, runner: self.states[controller.name]
        )
        monkeypatch.setattr(services_control, "_aggregate_action", self.act)
        monkeypatch.setattr(services_control, "_set_task", self.set_task)
        monkeypatch.setattr(services_control, "_restore_task_enabled", self.restore_task)

    def act(self, installation, controller, action, before, runner, task_changes=None):
        self.actions.append((action, controller.name))
        desired = action == "start"
        if self.failure == (action, controller.name, "denied"):
            self.failure = None
            raise services_control.ServiceControlError("Access is denied; no effect")
        if controller.task and before.enabled != desired and task_changes is not None:
            task_changes.add(controller.name)
        processes = before.processes
        if desired and not before.running:
            self.next_pid += 1
            processes = ({"pid": self.next_pid, "created_at": str(self.next_pid), "executable": controller.name},)
        if not desired:
            processes = ()
        self.states[controller.name] = services_control._Observed(
            desired,
            desired,
            desired if controller.task else None,
            processes,
        )
        if self.failure == (action, controller.name, "partial"):
            self.failure = None
            self.states[controller.name] = replace(self.states[controller.name], ready=False)
            raise services_control.ServiceControlError("Request launched a process but readiness failed")

    def set_task(self, runner, task, *, enabled):
        controller = next(item for item in self.controllers if item.task == task)
        self.task_changes.append((controller.name, enabled))
        self.states[controller.name] = replace(self.states[controller.name], enabled=enabled)

    def restore_task(self, controller, enabled, runner):
        if self.states[controller.name].enabled != enabled:
            self.set_task(runner, controller.task, enabled=enabled)


def _observed(name, running=False, enabled=None):
    processes = (
        ({"pid": 100 + services_control.START_ORDER.index(name), "created_at": "initial", "executable": name},)
        if running
        else ()
    )
    return services_control._Observed(running, running, enabled, processes)


def test_aggregate_starts_dependencies_and_stops_consumers_in_reverse_order(installation, monkeypatch):
    states = {
        name: _observed(name, enabled=False if name in ("authority", "ollama", "home") else None)
        for name in services_control.START_ORDER
    }
    host = AggregateHost(monkeypatch, states)
    runner = FakeRunner()
    started = services_control.start(installation, "all", runner)
    assert started["ok"] and started["started"] and started["phase"] == "complete"
    assert started["supported"] == list(services_control.START_ORDER)
    assert host.actions == [("start", name) for name in services_control.START_ORDER]
    assert all(state["running"] and state["ready"] for state in started["final"].values())
    host.actions.clear()
    stopped = services_control.stop(installation, "all", runner)
    assert stopped["ok"] and stopped["stopped"]
    assert host.actions == [("stop", name) for name in reversed(services_control.START_ORDER)]
    assert all(not state["running"] and state["task_enabled"] is not True for state in stopped["final"].values())
    assert runner.calls == [], "fake adapters must not launch real services"


def test_failed_start_compensates_its_partial_launch_and_restores_preexisting_task_state(installation, monkeypatch):
    states = {
        "postgresql": _observed("postgresql", True),
        "authority": _observed("authority", True, False),
        "ollama": _observed("ollama", False, False),
        "dashboard": _observed("dashboard"),
        "home": _observed("home", False, False),
    }
    host = AggregateHost(monkeypatch, states, failure=("start", "ollama", "partial"))
    result = services_control.start_all(installation, FakeRunner())
    assert not result["ok"] and not result["started"]
    assert result["failed_service"] == "ollama" and result["initial_state_restored"]
    assert host.actions == [("start", "authority"), ("start", "ollama"), ("stop", "ollama")]
    assert host.states["postgresql"] == states["postgresql"], "preexisting database was never stopped"
    assert host.states["authority"] == states["authority"], (
        "preexisting authority process survived; its disabled task was restored"
    )
    assert host.task_changes == [("authority", False)]
    assert result["changed"] == ["authority", "ollama"] and result["compensation_errors"] == {}


def test_failed_stop_restores_only_the_controllers_it_stopped(installation, monkeypatch):
    states = {
        "postgresql": _observed("postgresql", True),
        "authority": _observed("authority", True, False),
        "home": _observed("home", True, True),
    }
    host = AggregateHost(monkeypatch, states, failure=("stop", "postgresql", "denied"))
    result = services_control.stop_all(installation, FakeRunner())
    assert not result["ok"] and not result["stopped"] and result["initial_state_restored"]
    assert host.actions == [
        ("stop", "home"),
        ("stop", "authority"),
        ("stop", "postgresql"),
        ("start", "authority"),
        ("start", "home"),
    ]
    assert host.states["postgresql"] == states["postgresql"]
    assert host.states["authority"].enabled is False and host.states["home"].enabled is True
    assert result["changed"] == ["home", "authority"]
    assert result["attempted"] == ["home", "authority", "postgresql"]
    assert result["compensation_errors"] == {}


def test_aggregate_reports_compensation_failure_and_observed_remaining_state(installation, monkeypatch):
    states = {"postgresql": _observed("postgresql"), "authority": _observed("authority", False, False)}
    host = AggregateHost(monkeypatch, states, failure=("start", "authority", "partial"))
    original_act = host.act

    def refuse_compensation(installation, controller, action, before, runner, task_changes=None):
        if action == "stop" and controller.name == "authority":
            raise services_control.ServiceControlError("Termination refused")
        return original_act(installation, controller, action, before, runner, task_changes)

    monkeypatch.setattr(services_control, "_aggregate_action", refuse_compensation)
    result = services_control.start_all(installation, FakeRunner())
    assert not result["ok"] and not result["started"] and not result["initial_state_restored"]
    assert result["final"]["authority"]["running"] is True
    assert result["final"]["postgresql"]["running"] is False
    assert "Termination refused" in result["compensation_errors"]["authority"]


def test_compensation_preserves_external_task_change_that_was_not_ours(installation, monkeypatch):
    states = {"postgresql": _observed("postgresql", True), "authority": _observed("authority", False, True)}
    host = AggregateHost(monkeypatch, states, failure=("start", "authority", "partial"))
    observations = 0

    def observe(installation, controller, runner):
        nonlocal observations
        if controller.name == "authority":
            observations += 1
            if observations == 4:  # After our captured failed request, another operator disables its task.
                host.states["authority"] = replace(host.states["authority"], enabled=False)
        return host.states[controller.name]

    monkeypatch.setattr(services_control, "_observe", observe)
    result = services_control.start_all(installation, FakeRunner())
    assert not result["ok"] and not result["initial_state_restored"]
    assert result["final"]["authority"]["task_enabled"] is False
    assert host.task_changes == [], (
        "we never changed the initially enabled task and must not undo another operator's change"
    )
    assert "State changed outside the captured request" in result["compensation_errors"]["authority"]


def test_selected_config_is_forwarded_to_dashboard_subprocesses(installation, tmp_path):
    selected = tmp_path / "owner's selected Δ config.toml"
    installation = replace(installation, config_path=selected)
    runner = FakeRunner()
    services_control.start(installation, "dashboard", runner)
    services_control.stop(installation, "dashboard", runner)
    for call, action in zip(runner.calls, ("start", "stop"), strict=True):
        assert call == ["py.exe", "-m", "groundtruth_kb", "--config", str(selected), "dashboard", action, "--json"]


def test_identity_change_never_signals_a_reused_pid(monkeypatch):
    from groundtruth_kb import job_containment

    expected = {"pid": 4242, "created_at": "initial", "executable": "installed-ollama.exe"}

    @contextmanager
    def reused(pid):
        yield expected | {"created_at": "replacement"}, (object(), 1)

    monkeypatch.setattr(job_containment, "windows_process", reused)
    runner = FakeRunner()
    with pytest.raises(services_control.ServiceControlError, match="changed identity; nothing was signalled"):
        services_control._end_identified(runner, (expected,))
    assert runner.calls == []


def test_optional_installations_are_inventoried_while_down_and_missing_controller_is_not_absence(
    installation, monkeypatch
):
    import shlex

    from groundtruth_kb import dashboard

    pythonw = installation.root / "groundtruth-kb" / ".venv" / "Scripts" / "pythonw.exe"
    postgres = installation.root / "infrastructure" / "postgresql" / "runtime" / "fixture" / "bin" / "pg_ctl.exe"
    ollama = installation.root / "tools" / "ollama.exe"
    grafana = installation.root / ".groundtruth" / "tools" / "grafana" / "bin" / "grafana.exe"
    for file in (pythonw, postgres, ollama, grafana, installation.authority_launcher):
        file.parent.mkdir(parents=True, exist_ok=True)
        file.touch()
    definitions = {
        services_control.AUTHORITY_TASK: {
            "enabled": False,
            "actions": [
                {
                    "execute": str(pythonw),
                    "arguments": f'"{installation.authority_launcher}" --root "{installation.root}" --port 8765',
                }
            ],
        },
        services_control.HOME_TASK: {
            "enabled": False,
            "actions": [{"execute": str(pythonw), "arguments": f'-B "{installation.home_script}" start'}],
        },
        services_control.OLLAMA_TASK: {"enabled": False, "actions": [{"execute": str(ollama), "arguments": "serve"}]},
    }
    monkeypatch.setattr(services_control.sys, "platform", "win32")
    monkeypatch.setattr(services_control, "_arguments", lambda command: tuple(shlex.split(command)))
    monkeypatch.setattr(services_control, "_task_definition", lambda runner, task: definitions[task])
    monkeypatch.setattr(services_control, "_require_home_installation", lambda installation: None)
    monkeypatch.setattr(
        services_control,
        "_service_definition",
        lambda runner: {
            "state": "Stopped",
            "pid": 0,
            "path": f'"{postgres}" runservice -N "gtkb-postgresql" -D "{installation.postgresql_data}" -w',
        },
    )
    monkeypatch.setattr(services_control, "_process_rows", lambda runner: [])
    monkeypatch.setattr(services_control, "_get_ok", lambda *args: False)
    monkeypatch.setattr(services_control, "_installed_ollama", lambda runner: [str(ollama)])
    monkeypatch.setattr(dashboard, "find_grafana_server", lambda home: grafana)
    runner = FakeRunner()
    controllers, excluded = services_control._inventory(installation, runner)
    assert [item.name for item in controllers] == list(services_control.START_ORDER)
    assert "dashboard" not in excluded and "ollama" not in excluded
    definitions[services_control.OLLAMA_TASK] = None
    with pytest.raises(
        services_control.ServiceControlError, match="installed or present, but its supported task is missing"
    ):
        services_control._inventory(installation, runner)
    assert runner.calls == [], "installed/down discovery and a missing-controller refusal change no service"


def test_first_creation_mismatch_refuses_same_executable_pid_reuse(monkeypatch):
    from groundtruth_kb import job_containment

    row = {"pid": 4242, "created_at": "first-process", "executable": "installed-python.exe"}

    @contextmanager
    def replaced(pid):
        yield row | {"created_at": "native-filetime-of-replacement"}, (object(), 1)

    monkeypatch.setattr(job_containment, "windows_process", replaced)
    runner = FakeRunner([("ProcessId=4242", json.dumps(row | {"created_at": "replacement"}), 0)])
    with pytest.raises(services_control.ServiceControlError, match="changed creation/executable identity"):
        services_control._identity(row, runner)
    assert not any(call[:1] == ["taskkill"] for call in runner.calls)


@pytest.mark.parametrize("wait_result, stopped", [(0, True), (258, False)])
def test_home_stop_holds_observed_objects_and_requires_confirmed_exit(installation, monkeypatch, wait_result, stopped):
    from groundtruth_kb import job_containment

    identity = {"pid": 4242, "created_at": "initial", "executable": "installed-node.exe"}
    held = set()
    waits = []

    class Kernel:
        def WaitForSingleObject(self, handle, milliseconds):
            assert held == {4242}, "exit is read before releasing the original process handle"
            waits.append((handle, milliseconds))
            return wait_result

    @contextmanager
    def hold(pid):
        held.add(pid)
        try:
            yield identity, (Kernel(), 1)
        finally:
            held.remove(pid)

    monkeypatch.setattr(job_containment, "windows_process", hold)
    monkeypatch.setattr(
        services_control,
        "_home_stop_state",
        lambda *args: services_control._Observed(True, True, processes=(identity,)),
    )

    def home(installation, runner, action):
        assert action == "stop" and held == {4242}, "the PID cannot be reused during Home's fallback"
        return {"ok": True}

    monkeypatch.setattr(services_control, "_home", home)
    result = services_control.stop(installation, "home", FakeRunner())
    assert result["stopped"] is stopped
    assert waits == [(1, 5000)]
    if not stopped:
        assert result["detail"]["ok"] is True, "the controller's optimistic JSON is preserved as an observation"
        assert result["detail"]["stop_confirmed"] is False
        assert result["detail"]["unconfirmed_pids"] == [4242]
    assert held == set()


@pytest.mark.parametrize(
    "custom_carrier", [None, "record_interval", "argv_db", "argv_port", "health_db", "unknown_health"]
)
def test_dashboard_observer_accepts_only_identified_standard_launch_settings(installation, monkeypatch, custom_carrier):
    from groundtruth_kb import dashboard, job_containment

    installation = replace(installation, config_path=installation.root / "owner's selected Δ config.toml")
    python = str(installation.root / "python.exe")
    base = str(installation.root / "base-python.exe")
    grafana = str(installation.root / "grafana.exe")
    record_path = installation.root / ".groundtruth" / "dashboard" / "dashboard-launch.json"
    identities = {
        pid: {"pid": pid, "created_at": str(pid), "executable": executable}
        for pid, executable in ((100, python), (101, base), (200, grafana))
    }
    record = {
        "job": "existing-job",
        "members": [
            identities[100] | {"role": "refresh-service"},
            identities[200] | {"role": "grafana"},
        ],
        "grafana_port": 8767,
        "refresh_port": 8766,
        "interval_seconds": 3600,
        "config_path": str(installation.dashboard_config_path),
    }
    rows = [
        identity | {"command": "refresh" if pid in (100, 101) else "grafana"} for pid, identity in identities.items()
    ]
    members = {100, 101, 200}
    refresh_argv = (
        python,
        "-m",
        "groundtruth_kb.dashboard_service",
        "--config",
        str(installation.dashboard_config_path),
        "--db-path",
        str(record_path.parent / "gtkb-dashboard.sqlite"),
        "--runtime-root",
        str(record_path.parent),
        "--host",
        "127.0.0.1",
        "--port",
        "8766",
        "--grafana-port",
        "8767",
        "--interval-minutes",
        "60",
    )
    health = {
        "status": "ok",
        "project_root": str(installation.root),
        "runtime_root": str(record_path.parent),
        "dashboard_db": str(record_path.parent / "gtkb-dashboard.sqlite"),
        "config_path": str(installation.dashboard_config_path),
        "interval_seconds": 3600,
        "grafana_port": 8767,
        "last_error": "",
        "last_result": {"status": "completed"},
    }
    if custom_carrier == "record_interval":
        record["interval_seconds"] = 60
    if custom_carrier in ("argv_db", "argv_port"):
        changed = list(refresh_argv)
        key = "--db-path" if custom_carrier == "argv_db" else "--port"
        changed[changed.index(key) + 1] = (
            str(installation.root.parent / "other-observations.sqlite") if key == "--db-path" else "8776"
        )
        refresh_argv = tuple(changed)
    if custom_carrier == "health_db":
        health["dashboard_db"] = str(installation.root.parent / "other-observations.sqlite")
    if custom_carrier == "unknown_health":
        health = None
    monkeypatch.setattr(services_control.sys, "platform", "win32")
    monkeypatch.setattr(services_control, "_process_rows", lambda runner: rows)
    monkeypatch.setattr(
        services_control, "_arguments", lambda command: refresh_argv if command == "refresh" else (grafana,)
    )
    monkeypatch.setattr(
        services_control,
        "_python_images",
        lambda installation: {services_control.os.path.abspath(path).casefold() for path in (python, base)},
    )
    monkeypatch.setattr(services_control, "_get_ok", lambda url: url == "http://127.0.0.1:8767/api/health")
    monkeypatch.setattr(services_control, "_get_health", lambda *args: (True, health))
    monkeypatch.setattr(services_control, "_dashboard_launch_record", lambda installation: record_path)
    monkeypatch.setattr(dashboard, "_read_launch_record", lambda path: record)
    monkeypatch.setattr(dashboard, "_dashboard_job_name", lambda path: "existing-job")
    monkeypatch.setattr(dashboard, "_open_dashboard_job", lambda name: 1)
    monkeypatch.setattr(dashboard, "_job_member_pids", lambda handle: members)
    monkeypatch.setattr(dashboard, "_close_handle", lambda handle: None)
    monkeypatch.setattr(job_containment, "process_identity", lambda pid: identities.get(pid))
    monkeypatch.setattr(services_control, "_identity", lambda row, runner: identities.get(row["pid"]))
    controller = services_control._Controller("dashboard", executable=grafana)
    runner = FakeRunner()
    if custom_carrier is not None:
        with pytest.raises(services_control.ServiceControlError, match="custom or unknown"):
            services_control._observe(installation, controller, runner)
        assert runner.calls == [], "scope proof refuses before any controller or host effect"
        return
    observed = services_control._observe(installation, controller, runner)
    assert observed.running and observed.ready
    assert {item["pid"] for item in observed.processes} == members
    members.remove(101)
    with pytest.raises(services_control.ServiceControlError, match="outside this controller's identified job"):
        services_control._observe(installation, controller, FakeRunner())


class GuardedHost:
    """Fake only host primitives; exercise the real callback and compensation implementation."""

    def __init__(self, monkeypatch, states, failure=None):
        action = services_control._aggregate_action
        restore = services_control._restore_task_enabled
        self.host = AggregateHost(monkeypatch, states, failure)
        self.events = []
        monkeypatch.setattr(services_control, "_aggregate_action", action)
        monkeypatch.setattr(services_control, "_restore_task_enabled", restore)
        monkeypatch.setattr(services_control, "_wait", lambda predicate, seconds: predicate())
        monkeypatch.setattr(
            services_control,
            "_single_controller",
            lambda installation, name, runner: next(
                controller for controller in self.host.controllers if controller.name == name
            ),
        )
        monkeypatch.setattr(services_control, "_task_definition", self.task_definition)
        monkeypatch.setattr(
            services_control,
            "_task_controller",
            lambda name, task, definition, args: next(
                controller for controller in self.host.controllers if controller.name == name
            ),
        )
        monkeypatch.setattr(services_control, "_set_task", self.set_task)
        monkeypatch.setattr(services_control, "_run_task", self.run_task)
        monkeypatch.setattr(services_control, "_end_identified", self.end_identified)
        monkeypatch.setattr(services_control, "_home", self.home)
        monkeypatch.setattr(services_control, "_hold_identified", self.hold)

    def task_definition(self, runner, task):
        controller = next(controller for controller in self.host.controllers if controller.task == task)
        return {"enabled": self.host.states[controller.name].enabled, "actions": []}

    def set_task(self, runner, task, *, enabled):
        controller = next(controller for controller in self.host.controllers if controller.task == task)
        self.events.append(("effect", controller.name, "task.enable" if enabled else "task.disable"))
        self.host.set_task(runner, task, enabled=enabled)

    def runtime(self, name, action):
        self.host.actions.append((action, name))
        if self.host.failure == (action, name, "denied"):
            self.host.failure = None
            raise services_control.ServiceControlError("Access is denied; no effect")
        self.events.append(("effect", name, f"service.{action}" if name == "postgresql" else f"process.{action}"))
        before = self.host.states[name]
        desired = action == "start"
        self.host.next_pid += 1
        processes = (
            ({"pid": self.host.next_pid, "created_at": str(self.host.next_pid), "executable": name},) if desired else ()
        )
        self.host.states[name] = replace(before, running=desired, ready=desired, processes=processes)
        if self.host.failure == (action, name, "partial"):
            self.host.failure = None
            self.host.states[name] = replace(self.host.states[name], ready=False)
            raise services_control.ServiceControlError("Request launched a process but readiness failed")

    def run_task(self, runner, task):
        controller = next(controller for controller in self.host.controllers if controller.task == task)
        self.runtime(controller.name, "start")

    def end_identified(self, runner, processes, *, before_terminate=None):
        for expected in processes:
            name = next(name for name, state in self.host.states.items() if expected in state.processes)
            if before_terminate is not None:
                before_terminate(expected)
            self.runtime(name, "stop")

    def home(self, installation, runner, action):
        self.runtime("home", action)
        return {"ok": True}

    @contextmanager
    def hold(self, processes):
        class Kernel:
            def WaitForSingleObject(self, handle, milliseconds):
                return 0

        yield [(Kernel(), process["pid"]) for process in processes]

    def runner(self, argv, timeout):
        if "dashboard" in argv:
            self.runtime("dashboard", argv[argv.index("dashboard") + 1])
        elif "Start-Service" in argv[-1] or "Stop-Service" in argv[-1]:
            self.runtime("postgresql", "start" if "Start-Service" in argv[-1] else "stop")
        else:
            raise AssertionError(f"Unexpected host command: {argv}")
        return subprocess.CompletedProcess(argv, 0, "", "")

    def check(self, operation, targets, effects, phase):
        self.events.append(("check", operation, tuple(targets), effects, phase))


def _assert_effects_follow_exact_checks(events):
    previous = None
    for event in events:
        if event[0] == "check":
            previous = event
        else:
            assert previous is not None
            assert {"target": f"service:{event[1]}", "effect": event[2]} in previous[3]


def test_individual_effect_denial_precedes_task_or_process_mutation(installation, monkeypatch):
    fixture = GuardedHost(monkeypatch, {"authority": _observed("authority", False, False)})

    def check(operation, targets, effects, phase):
        fixture.check(operation, targets, effects, phase)
        assert operation == "services.start" and targets == ["service:authority"]
        if phase == "forward":
            raise services_control.ServiceControlError("Current bound refuses task enable")

    result = services_control.start(installation, "authority", fixture.runner, before_effect=check)
    assert result["service"] == "authority" and not result["started"] and not result["ok"]
    assert "refuses task enable" in result["detail"] and result["initial_state_restored"]
    assert fixture.host.actions == [] and fixture.host.task_changes == []
    assert all(event[0] == "check" for event in fixture.events)


def test_aggregate_preflight_uses_actual_optional_set_and_refuses_an_ungranted_controller(installation, monkeypatch):
    states = {
        "postgresql": _observed("postgresql"),
        "authority": _observed("authority", False, False),
        "dashboard": _observed("dashboard"),
    }
    fixture = GuardedHost(monkeypatch, states)

    def check(operation, targets, effects, phase):
        assert operation == "services.start-all" and phase == "preflight"
        assert set(targets) == {f"service:{name}" for name in states}
        if "service:dashboard" in targets:
            raise services_control.ServiceControlError("Installed Dashboard is outside the declared bound")

    result = services_control.start_all(installation, fixture.runner, before_effect=check)
    assert not result["ok"] and result["phase"] == "preflight"
    assert result["attempted"] == [] and fixture.host.actions == [] and fixture.host.task_changes == []


def test_noop_aggregate_keeps_fresh_observations_and_calls_supplied_callback(installation, monkeypatch):
    states = {"postgresql": _observed("postgresql", True), "authority": _observed("authority", True, True)}
    fixture = GuardedHost(monkeypatch, states)
    result = services_control.start_all(installation, fixture.runner, before_effect=fixture.check)
    assert result["ok"] and result["started"] and result["phase"] == "complete"
    assert result["attempted"] == [] and result["changed"] == []
    assert result["initial"] == result["final"]
    assert fixture.events == [
        ("check", "services.start-all", ("service:postgresql", "service:authority"), [], "preflight")
    ]
    assert fixture.host.actions == [] and fixture.host.task_changes == []


def test_literal_false_callback_denial_never_uses_owner_path(installation, monkeypatch):
    fixture = GuardedHost(monkeypatch, {"authority": _observed("authority", False, False)})
    result = services_control.start(
        installation, "authority", fixture.runner, before_effect=lambda operation, targets, effects, phase: False
    )
    assert not result["ok"] and not result["started"] and result["phase"] == "preflight"
    assert "effect check refused" in result["detail"]
    assert fixture.host.actions == [] and fixture.host.task_changes == []


def test_aggregate_detects_controller_set_change_before_first_effect(installation, monkeypatch):
    fixture = GuardedHost(
        monkeypatch, {"postgresql": _observed("postgresql"), "authority": _observed("authority", False, False)}
    )

    def check(operation, targets, effects, phase):
        fixture.check(operation, targets, effects, phase)
        if phase == "preflight":
            fixture.host.controllers = [*fixture.host.controllers, services_control._Controller("dashboard")]

    result = services_control.start_all(installation, fixture.runner, before_effect=check)
    assert not result["ok"] and "controller set changed" in result["detail"]
    assert result["attempted"] == [] and fixture.host.actions == [] and fixture.host.task_changes == []


def test_callback_observed_external_runtime_change_is_never_compensated_as_ours(installation, monkeypatch):
    fixture = GuardedHost(monkeypatch, {"postgresql": _observed("postgresql")})

    def check(operation, targets, effects, phase):
        fixture.check(operation, targets, effects, phase)
        if phase == "forward":
            fixture.host.states["postgresql"] = _observed("postgresql", True)

    result = services_control.start_all(installation, fixture.runner, before_effect=check)
    assert not result["ok"] and not result["initial_state_restored"]
    assert fixture.host.actions == [], (
        "neither the denied start nor a compensating stop may touch another operator's process"
    )
    assert result["final"]["postgresql"]["running"] is True
    assert result["changed"] == [], "an external runtime change cannot be reported as our change"
    assert "before any controller effect was attempted" in result["compensation_errors"]["postgresql"]


def test_aggregate_callbacks_check_rollback_and_keep_enclosing_full_scope(installation, monkeypatch):
    states = {"postgresql": _observed("postgresql"), "authority": _observed("authority", False, False)}
    fixture = GuardedHost(monkeypatch, states, failure=("start", "authority", "partial"))
    result = services_control.start_all(installation, fixture.runner, before_effect=fixture.check)
    assert not result["ok"] and result["initial_state_restored"]
    checks = [event for event in fixture.events if event[0] == "check"]
    assert all(
        event[1] == "services.start-all" and set(event[2]) == {"service:authority", "service:postgresql"}
        for event in checks
    )
    rollback = [event for event in checks if event[4] == "rollback"]
    assert any({"target": "service:authority", "effect": "process.stop"} in event[3] for event in rollback)
    assert any({"target": "service:postgresql", "effect": "service.stop"} in event[3] for event in rollback)
    _assert_effects_follow_exact_checks(fixture.events)


def test_rollback_denial_leaves_a_truthful_unrestored_result(installation, monkeypatch):
    fixture = GuardedHost(
        monkeypatch, {"authority": _observed("authority", False, False)}, failure=("start", "authority", "partial")
    )

    def check(operation, targets, effects, phase):
        fixture.check(operation, targets, effects, phase)
        if phase == "rollback":
            raise services_control.ServiceControlError("Rollback bound expired")

    result = services_control.start_all(installation, fixture.runner, before_effect=check)
    assert not result["ok"] and not result["initial_state_restored"]
    assert result["final"]["authority"]["running"] is True
    assert "Rollback bound expired" in result["compensation_errors"]["authority"]
    assert fixture.host.actions == [("start", "authority")], "denied compensation cannot terminate the process"


def test_bounded_single_partial_start_uses_same_compensation_and_result_contract(installation, monkeypatch):
    fixture = GuardedHost(
        monkeypatch, {"authority": _observed("authority", False, False)}, failure=("start", "authority", "partial")
    )
    result = services_control.start(installation, "authority", fixture.runner, before_effect=fixture.check)
    assert result["service"] == "authority" and not result["started"] and not result["ok"]
    assert result["initial_state_restored"] and result["compensation_errors"] == {}
    assert fixture.host.actions == [("start", "authority"), ("stop", "authority")]
    checks = [event for event in fixture.events if event[0] == "check"]
    assert all(event[1] == "services.start" and event[2] == ("service:authority",) for event in checks)
    assert any(event[4] == "rollback" for event in checks)
    _assert_effects_follow_exact_checks(fixture.events)


@pytest.mark.parametrize("completion_failure", ["denied", "false", "exception"])
def test_completion_failure_compensates_only_its_new_service_changes(installation, monkeypatch, completion_failure):
    states = {
        "postgresql": _observed("postgresql", True),
        "authority": _observed("authority", True, False),
        "home": _observed("home", False, False),
    }
    fixture = GuardedHost(monkeypatch, states)
    completions = []

    def complete():
        completions.append("called")
        assert all(state.running and state.ready for state in fixture.host.states.values())
        if completion_failure == "denied":
            raise services_control.ServiceControlError("Native browser effect denied")
        if completion_failure == "exception":
            raise RuntimeError("Browser launch failed")
        return False

    result = services_control.start_all(installation, fixture.runner, before_effect=fixture.check, on_complete=complete)
    assert not result["ok"] and not result["started"] and result["failed_service"] == "completion"
    assert completions == ["called"] and result["initial_state_restored"]
    assert fixture.host.actions == [("start", "home"), ("stop", "home")]
    assert fixture.host.states["postgresql"] == states["postgresql"]
    assert fixture.host.states["authority"] == states["authority"]
    assert result["compensation_errors"] == {}
    _assert_effects_follow_exact_checks(fixture.events)


def test_named_home_completion_uses_captured_single_scope_and_compensation(installation, monkeypatch):
    fixture = GuardedHost(monkeypatch, {"home": _observed("home", False, False)})
    result = services_control.start(
        installation, "home", fixture.runner, before_effect=fixture.check, on_complete=lambda: False
    )
    assert result["service"] == "home" and not result["started"] and result["initial_state_restored"]
    assert fixture.host.actions == [("start", "home"), ("stop", "home")]
    assert all(
        event[1] == "services.start" and event[2] == ("service:home",)
        for event in fixture.events
        if event[0] == "check"
    )


def test_completion_is_called_on_noop_and_never_after_preflight_refusal(installation, monkeypatch):
    fixture = GuardedHost(monkeypatch, {"postgresql": _observed("postgresql", True)})
    completions = []
    result = services_control.start_all(
        installation, fixture.runner, before_effect=fixture.check, on_complete=lambda: completions.append("complete")
    )
    assert result["ok"] and completions == ["complete"] and result["changed"] == []
    denied = services_control.start_all(
        installation,
        fixture.runner,
        before_effect=lambda *args: False,
        on_complete=lambda: completions.append("must not run"),
    )
    assert not denied["ok"] and completions == ["complete"]


def test_stop_verification_failure_compensates_inside_terminal_window(installation, monkeypatch):
    states = {"postgresql": _observed("postgresql", True), "authority": _observed("authority", True, False)}
    fixture = GuardedHost(monkeypatch, states)

    def verify():
        assert all(not state.running for state in fixture.host.states.values())
        raise services_control.ServiceControlError("Declared post-operation verification failed")

    result = services_control.stop_all(installation, fixture.runner, before_effect=fixture.check, on_complete=verify)
    assert not result["ok"] and not result["stopped"] and result["failed_service"] == "completion"
    assert result["initial_state_restored"] and result["compensation_errors"] == {}
    assert fixture.host.actions == [
        ("stop", "authority"),
        ("stop", "postgresql"),
        ("start", "postgresql"),
        ("start", "authority"),
    ]
    assert fixture.host.states["authority"].enabled is False
    assert any(event[0] == "check" and event[4] == "terminal_shutdown" for event in fixture.events)
    assert any(event[0] == "check" and event[4] == "rollback" for event in fixture.events)
    _assert_effects_follow_exact_checks(fixture.events)


def test_stop_all_validates_terminal_suffix_before_authority_and_never_rediscovers_offline(installation, monkeypatch):
    states = {
        name: _observed(name, True, True if name in ("authority", "home", "ollama") else None)
        for name in services_control.START_ORDER
    }
    fixture = GuardedHost(monkeypatch, states)
    inventory = services_control._inventory
    terminal_checks = []

    def discover(installation, runner):
        assert fixture.host.states["authority"].running, "no target discovery follows the last live authority boundary"
        return inventory(installation, runner)

    def check(operation, targets, effects, phase):
        fixture.check(operation, targets, effects, phase)
        assert operation == "services.stop-all" and set(targets) == {f"service:{name}" for name in states}
        if phase == "terminal_shutdown":
            terminal_checks.append(effects)
            if len(terminal_checks) == 1:
                assert fixture.host.states["authority"].running and fixture.host.states["postgresql"].running
                assert all(not fixture.host.states[name].running for name in ("home", "dashboard", "ollama"))

    monkeypatch.setattr(services_control, "_inventory", discover)
    result = services_control.stop_all(installation, fixture.runner, before_effect=check)
    assert result["ok"] and result["stopped"]
    first_terminal = terminal_checks[0]
    assert {effect["target"] for effect in first_terminal if effect["effect"] == "service.stop"} == {
        "service:authority",
        "service:postgresql",
    }
    assert {effect["target"] for effect in first_terminal if effect["effect"] == "service.start"} == {
        f"service:{name}" for name in states
    }
    seen_terminal = False
    for event in fixture.events:
        if event[0] == "check" and event[4] == "terminal_shutdown":
            seen_terminal = True
        if seen_terminal and event[0] == "check":
            assert event[4] == "terminal_shutdown"
    _assert_effects_follow_exact_checks(fixture.events)


@pytest.mark.parametrize("name", ["authority", "postgresql"])
def test_single_foundational_stop_prepares_its_exact_terminal_inverse(installation, monkeypatch, name):
    fixture = GuardedHost(monkeypatch, {name: _observed(name, True, False if name == "authority" else None)})
    result = services_control.stop(installation, name, fixture.runner, before_effect=fixture.check)
    assert result["ok"] and result["stopped"] and result["service"] == name
    checks = [event for event in fixture.events if event[0] == "check"]
    terminal = next(event for event in checks if event[4] == "terminal_shutdown")
    assert terminal[1] == "services.stop" and terminal[2] == (f"service:{name}",)
    assert {"target": f"service:{name}", "effect": "service.stop"} in terminal[3]
    assert {"target": f"service:{name}", "effect": "service.start"} in terminal[3]
    if name == "postgresql":
        assert all(effect["effect"].startswith("service.") for effect in terminal[3])
    _assert_effects_follow_exact_checks(fixture.events)


def test_identified_termination_denial_precedes_taskkill_while_identity_is_held(monkeypatch):
    from groundtruth_kb import job_containment

    identity = {"pid": 4242, "created_at": "initial", "executable": "installed-ollama.exe"}
    held = set()

    @contextmanager
    def hold(pid):
        held.add(pid)
        try:
            yield identity, (object(), 1)
        finally:
            held.remove(pid)

    def deny(expected):
        assert held == {4242} and expected == identity
        raise services_control.ServiceControlError("Process stop refused")

    monkeypatch.setattr(job_containment, "windows_process", hold)
    runner = FakeRunner()
    with pytest.raises(services_control.ServiceControlError, match="Process stop refused"):
        services_control._end_identified(runner, (identity,), before_terminate=deny)
    assert runner.calls == [] and held == set()


def test_fresh_target_observation_uses_selected_config_and_existing_controllers_only(installation, monkeypatch):
    installation = replace(installation, config_path=installation.root / "owner's selected Δ config.toml")
    states = {"authority": _observed("authority", True, False), "postgresql": _observed("postgresql", True)}
    fixture = GuardedHost(monkeypatch, states)
    monkeypatch.setattr(
        services_control,
        "_inventory",
        lambda *args: (_ for _ in ()).throw(AssertionError("observation must not select another controller")),
    )
    observed = services_control.observe_targets(
        installation, ["service:authority", "service:postgresql"], fixture.runner
    )
    assert observed["installation_root"] == str(installation.root.resolve())
    assert observed["config_path"] == str(installation.dashboard_config_path.resolve())
    assert observed["observed_controller_paths"] == {
        "service:authority": str(installation.authority_launcher.resolve()),
        "service:postgresql": str(installation.postgresql_data.resolve()),
    }
    assert observed["states"]["service:authority"]["task_enabled"] is False
    assert observed["states"]["service:postgresql"]["running"] is True
    assert fixture.host.actions == [] and fixture.host.task_changes == []
