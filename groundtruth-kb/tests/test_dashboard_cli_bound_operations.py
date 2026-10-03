"""Dashboard command routing; controllers, host inspection and native checks are mocked."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from groundtruth_kb import cli_authority, dashboard, dashboard_service, services_control
from groundtruth_kb import config as config_module

OPS = ["--activity", "ops", "--native-context-id", "context-1", "--document", "attempt-1", "--fence", "7"]
REAL_BOUNDED_SERVICE_EFFECTS = cli_authority._bounded_service_effects


@pytest.fixture
def route(monkeypatch, tmp_path):
    root = tmp_path / "owner's Δ installation"
    selected = tmp_path / "owner's Δ selected config.toml"
    config = SimpleNamespace(project_root=root, authority_url="http://127.0.0.1:8765")
    installation = services_control.Installation(root, config.authority_url, root / "python.exe", selected)
    paths = dashboard.resolve_dashboard_paths(config)
    monkeypatch.setattr(cli_authority, "_config", lambda ctx: config)
    monkeypatch.setattr(cli_authority, "_services_installation", lambda ctx: installation)
    find_config = Mock(side_effect=AssertionError("The explicit selected config must be preserved"))
    monkeypatch.setattr(config_module, "_find_config", find_config)
    checks = Mock()
    checks.verify = Mock(return_value=None)
    checks.deadline = 1234.5
    adapter = Mock(return_value=checks)
    monkeypatch.setattr(cli_authority, "_bounded_service_effects", adapter)
    controlled_start = Mock(return_value={"service": "dashboard", "ok": True, "started": True})
    controlled_stop = Mock(return_value={"service": "dashboard", "ok": True, "stopped": True})
    monkeypatch.setattr(services_control, "start", controlled_start)
    monkeypatch.setattr(services_control, "stop", controlled_stop)
    owner_start = Mock(
        return_value=dashboard.DashboardProcessInfo(101, 102, "http://127.0.0.1:8767/", "http://127.0.0.1:8766/")
    )
    owner_stop = Mock(return_value=[])
    owner_install = Mock(return_value=root / "grafana-server.exe")
    owner_serve = Mock()
    monkeypatch.setattr(dashboard, "start_dashboard", owner_start)
    monkeypatch.setattr(dashboard, "stop_dashboard", owner_stop)
    monkeypatch.setattr(dashboard, "install_grafana", owner_install)
    monkeypatch.setattr(dashboard_service, "run_service", owner_serve)
    return SimpleNamespace(
        config=config,
        installation=installation,
        selected=selected,
        paths=paths,
        checks=checks,
        adapter=adapter,
        controlled_start=controlled_start,
        controlled_stop=controlled_stop,
        owner_start=owner_start,
        owner_stop=owner_stop,
        owner_install=owner_install,
        owner_serve=owner_serve,
        find_config=find_config,
        invoke=lambda args: CliRunner().invoke(cli_authority.dashboard_group, args, obj={"config": selected}),
    )


@pytest.mark.parametrize("action", ["start", "stop"])
def test_standard_bound_route_retains_selected_config_and_completion_verification(route, action):
    controller = getattr(route, f"controlled_{action}")
    events = []

    def controlled(installation, name, *, before_effect, on_complete):
        assert installation is route.installation and name == "dashboard"
        assert before_effect is route.checks
        assert on_complete is route.checks.verify
        events.append("inside-controller")
        on_complete()
        events.append("confirmed")
        return {"service": name, "ok": True, "started" if action == "start" else "stopped": True}

    controller.side_effect = controlled
    explicit_defaults = ["--runtime-root", str(route.paths.runtime_root)]
    if action == "start":
        explicit_defaults.extend(
            [
                "--db-path",
                str(route.paths.db_path),
                "--grafana-home",
                str(route.paths.grafana_home),
                "--grafana-port",
                "8767",
                "--refresh-port",
                "8766",
                "--interval-minutes",
                "60",
            ]
        )
    result = route.invoke([action, *explicit_defaults, *OPS, "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["ok"] is True
    controller.assert_called_once()
    assert route.installation.config_path == route.selected
    assert route.adapter.call_args.kwargs == {
        "activity": "ops",
        "native_context_id": "context-1",
        "document": "attempt-1",
        "fence": 7,
        "operation": f"dashboard.{action}",
    }
    assert events == ["inside-controller", "confirmed"]
    route.checks.verify.assert_called_once_with()
    route.owner_start.assert_not_called()
    route.owner_stop.assert_not_called()
    route.find_config.assert_not_called()


@pytest.mark.parametrize(
    ("action", "option", "value", "setting"),
    [
        ("start", "--db-path", "custom.sqlite", "db_path"),
        ("start", "--runtime-root", "custom-runtime", "runtime_root"),
        ("start", "--grafana-home", "custom-grafana", "grafana_home"),
        ("start", "--grafana-port", "3300", "grafana_port"),
        ("start", "--refresh-port", "8866", "refresh_port"),
        ("start", "--interval-minutes", "5", "interval_minutes"),
        ("stop", "--runtime-root", "custom-runtime", "runtime_root"),
    ],
)
def test_custom_bound_settings_refuse_before_any_controller(route, action, option, value, setting):
    result = route.invoke([action, option, value, *OPS, "--json"])
    assert result.exit_code == 1
    assert "custom " in result.output and setting in result.output
    assert "selected values were not applied" in result.output
    route.controlled_start.assert_not_called()
    route.controlled_stop.assert_not_called()
    route.owner_start.assert_not_called()
    route.owner_stop.assert_not_called()
    route.checks.assert_not_called()
    route.checks.verify.assert_not_called()


@pytest.mark.parametrize("action", ["start", "stop"])
def test_partial_ops_selectors_cannot_fall_back_to_owner_route(route, monkeypatch, action):
    monkeypatch.setattr(cli_authority, "_bounded_service_effects", REAL_BOUNDED_SERVICE_EFFECTS)
    result = route.invoke([action, "--document", "attempt-1", "--json"])
    assert result.exit_code == 2
    assert "--activity ops, --native-context-id, --document and --fence together" in result.output
    route.controlled_start.assert_not_called()
    route.controlled_stop.assert_not_called()
    route.owner_start.assert_not_called()
    route.owner_stop.assert_not_called()


@pytest.mark.parametrize("action", ["start", "stop"])
def test_bound_partial_failure_has_nonzero_exit_and_truthful_result(route, action):
    outcome = {
        "service": "dashboard",
        "ok": False,
        "phase": "compensation",
        "initial_state_restored": False,
        "started" if action == "start" else "stopped": True,
    }
    getattr(route, f"controlled_{action}").return_value = outcome
    result = route.invoke([action, *OPS, "--json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout) == outcome
    assert result.stderr == ""
    route.owner_start.assert_not_called()
    route.owner_stop.assert_not_called()


def test_partial_install_selectors_cannot_fall_back_to_owner_route(route, monkeypatch):
    monkeypatch.setattr(cli_authority, "_bounded_service_effects", REAL_BOUNDED_SERVICE_EFFECTS)
    result = route.invoke(["install", "--document", "attempt-1", "--json"])
    assert result.exit_code == 2
    assert "--activity ops, --native-context-id, --document and --fence together" in result.output
    route.owner_install.assert_not_called()


def test_owner_start_retains_custom_settings_and_selected_config(route):
    custom = route.installation.root / "custom runtime"
    db = custom / "custom.sqlite"
    grafana = route.installation.root / "custom grafana"
    result = route.invoke(
        [
            "start",
            "--db-path",
            str(db),
            "--runtime-root",
            str(custom),
            "--grafana-home",
            str(grafana),
            "--grafana-port",
            "3300",
            "--refresh-port",
            "8866",
            "--interval-minutes",
            "5",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.output
    paths, config = route.owner_start.call_args.args
    assert config is route.config
    assert (paths.db_path, paths.runtime_root, paths.grafana_home) == (
        db.resolve(),
        custom.resolve(),
        grafana.resolve(),
    )
    assert route.owner_start.call_args.kwargs == {
        "grafana_port": 3300,
        "refresh_port": 8866,
        "interval_minutes": 5,
        "config_path": route.selected,
    }
    route.adapter.assert_not_called()
    route.controlled_start.assert_not_called()


def test_owner_stop_and_serve_retain_custom_runtime_and_settings(route):
    custom = route.installation.root / "custom runtime"
    db = custom / "custom.sqlite"
    result = route.invoke(["stop", "--runtime-root", str(custom), "--json"])
    assert result.exit_code == 0, result.output
    assert route.owner_stop.call_args.args[0].runtime_root == custom.resolve()
    result = route.invoke(
        [
            "serve",
            "--runtime-root",
            str(custom),
            "--db-path",
            str(db),
            "--port",
            "8866",
            "--grafana-port",
            "3300",
            "--interval-minutes",
            "5",
        ]
    )
    assert result.exit_code == 0, result.output
    route.owner_serve.assert_called_once_with(
        route.config,
        db.resolve(),
        custom.resolve(),
        port=8866,
        grafana_port=3300,
        interval_minutes=5,
        config_path=route.selected,
    )
    route.adapter.assert_not_called()
    route.controlled_stop.assert_not_called()


def test_owner_install_retains_custom_target_and_skip_flags(route):
    custom = route.installation.root / "custom grafana"
    result = route.invoke(["install", "--grafana-home", str(custom), "--skip-download", "--skip-plugin", "--json"])
    assert result.exit_code == 0, result.output
    assert route.owner_install.call_args.args[0].grafana_home == custom.resolve()
    assert route.owner_install.call_args.kwargs == {"skip_download": True, "skip_plugin": True}
    route.adapter.assert_not_called()


def test_standard_foreground_serve_wires_owned_observer_effect_and_readiness_callbacks(route):
    events = []

    def observation():
        return {"selected": "this invocation"}

    def foreground(config, db_path, runtime_root, **kwargs):
        assert config is route.config
        assert (db_path, runtime_root) == (route.paths.db_path, route.paths.runtime_root)
        assert kwargs["config_path"] == route.selected
        assert kwargs["before_effect"] is route.checks
        assert kwargs["on_observer"] is route.checks.bind_foreground_observer
        assert kwargs["ready"] is route.checks.verify
        assert callable(kwargs["deadline"]) and kwargs["deadline"]() == route.checks.deadline
        assert (kwargs["port"], kwargs["grafana_port"], kwargs["interval_minutes"]) == (8766, 8767, 60)
        kwargs["on_observer"](observation)
        kwargs["before_effect"](
            "dashboard.serve",
            ["service:dashboard"],
            [{"target": "service:dashboard", "effect": "service.start"}],
            "forward",
        )
        events.append("admitted-start")
        kwargs["ready"]()
        events.append("verified-ready")
        return {"ok": True, "ready": True, "stopped": True, "server_closed": True, "scheduler_exited": True}

    route.owner_serve.side_effect = foreground
    outcome = route.invoke(
        ["serve", "--db-path", str(route.paths.db_path), "--runtime-root", str(route.paths.runtime_root), *OPS]
    )
    assert outcome.exit_code == 0, outcome.output
    assert events == ["admitted-start", "verified-ready"]
    assert route.adapter.call_args.kwargs == {
        "activity": "ops",
        "native_context_id": "context-1",
        "document": "attempt-1",
        "fence": 7,
        "operation": "dashboard.serve",
    }
    route.checks.bind_foreground_observer.assert_called_once_with(observation)
    route.checks.verify.assert_called_once_with()
    route.controlled_start.assert_not_called()
    route.controlled_stop.assert_not_called()


@pytest.mark.parametrize("missing", ["ok", "ready", "stopped", "server_closed", "scheduler_exited", "result"])
def test_foreground_serve_never_reports_success_for_unconfirmed_start_or_cleanup(route, missing):
    result = {
        "ok": True,
        "ready": True,
        "stopped": True,
        "server_closed": True,
        "scheduler_exited": True,
        "detail": "owned scheduler remains active",
    }
    if missing != "result":
        result[missing] = False
    route.owner_serve.return_value = result if missing != "result" else None
    outcome = route.invoke(["serve", *OPS])
    assert outcome.exit_code == 1
    assert "Foreground Dashboard start or cleanup failed" in outcome.output
    assert (
        "owned scheduler remains active" if missing != "result" else "no inspected controller result"
    ) in outcome.output
    route.controlled_start.assert_not_called()
    route.controlled_stop.assert_not_called()


def test_partial_foreground_selectors_do_not_invoke_owner_service(route, monkeypatch):
    monkeypatch.setattr(cli_authority, "_bounded_service_effects", REAL_BOUNDED_SERVICE_EFFECTS)
    outcome = route.invoke(["serve", "--document", "attempt-1"])
    assert outcome.exit_code == 2
    assert "--activity ops, --native-context-id, --document and --fence together" in outcome.output
    route.owner_serve.assert_not_called()


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--db-path", "custom.sqlite"),
        ("--runtime-root", "custom-runtime"),
        ("--port", "8866"),
        ("--grafana-port", "3300"),
        ("--interval-minutes", "5"),
    ],
)
def test_custom_foreground_settings_refuse_before_bound_or_owner_effect(route, option, value):
    outcome = route.invoke(["serve", option, value, *OPS])
    assert outcome.exit_code == 1
    assert "custom " in outcome.output and "selected values were not applied" in outcome.output
    route.owner_serve.assert_not_called()
    route.checks.assert_not_called()


@pytest.mark.parametrize("already_pinned", [False, True])
def test_standard_bound_install_wires_same_adapter_and_verifies_before_success(route, already_pinned):
    events = []
    binary = route.paths.grafana_home / "bin" / "grafana-server.exe"

    def observe():
        return {
            "installation_root": str(route.installation.root),
            "config_path": str(route.selected),
            "observed_controller_paths": {"service:dashboard": str(route.paths.grafana_home)},
            "states": {},
            "installation": {"predicate": "pinned_grafana_sqlite", "verified": already_pinned},
        }

    def installer(paths, **kwargs):
        assert paths.grafana_home == route.paths.grafana_home
        assert set(kwargs) == {"config_path", "before_effect", "on_observer", "ready", "deadline"}
        assert kwargs["config_path"] == route.selected and kwargs["before_effect"] is route.checks
        assert kwargs["on_observer"] is route.checks.bind_installation_observer
        assert kwargs["ready"] is route.checks.verify and kwargs["deadline"]() == route.checks.deadline
        kwargs["on_observer"](observe)
        kwargs["before_effect"]("dashboard.install", ["service:dashboard"], [], "preflight")
        events.append("pinned-noop" if already_pinned else "cold-publication")
        kwargs["ready"]()
        events.append("verified")
        return binary

    route.owner_install.side_effect = installer
    result = route.invoke(["install", "--grafana-home", str(route.paths.grafana_home), *OPS, "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {
        "status": "Grafana installed",
        "grafana_binary": str(binary),
        "plugin_install_skipped": False,
    }
    assert route.adapter.call_args.kwargs == {
        "activity": "ops",
        "native_context_id": "context-1",
        "document": "attempt-1",
        "fence": 7,
        "operation": "dashboard.install",
    }
    assert events == ["pinned-noop" if already_pinned else "cold-publication", "verified"]
    route.checks.bind_installation_observer.assert_called_once_with(observe)
    route.checks.verify.assert_called_once_with()
    route.find_config.assert_not_called()


@pytest.mark.parametrize(
    "options,reason",
    [
        (["--grafana-home", "custom-grafana"], "custom grafana_home"),
        (["--skip-download"], "skip flags"),
        (["--skip-plugin"], "skip flags"),
    ],
)
def test_bound_install_refuses_custom_destination_or_skipped_verification(route, options, reason):
    result = route.invoke(["install", *options, *OPS, "--json"])
    assert result.exit_code == 1 and reason in result.output
    route.owner_install.assert_not_called()
    route.checks.assert_not_called()
    route.checks.verify.assert_not_called()


def test_bound_install_verification_failure_propagates_without_owner_fallback(route):
    def installer(paths, **kwargs):
        kwargs["ready"]()
        raise AssertionError("A refused verifier must not return an installation result")

    route.owner_install.side_effect = installer
    route.checks.verify.side_effect = services_control.ServiceControlError("pinned installation verification refused")
    result = route.invoke(["install", *OPS, "--json"])
    assert result.exit_code == 1 and "pinned installation verification refused" in result.output
    route.owner_install.assert_called_once()
    assert route.owner_install.call_args.kwargs["before_effect"] is route.checks
