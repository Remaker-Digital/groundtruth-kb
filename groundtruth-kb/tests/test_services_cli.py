"""Service CLI outcome and Home launch contract; all controllers are mocked."""

import json
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from groundtruth_kb import cli_authority, services_control


def test_operational_effect_check_sends_selected_installation_and_observed_controllers(monkeypatch, tmp_path):
    config_path = tmp_path / "selected config.toml"
    installation = object()
    monkeypatch.setattr(cli_authority, "_config", lambda ctx: SimpleNamespace(project_root=tmp_path))
    monkeypatch.setattr(cli_authority, "_services_installation", lambda ctx: installation)
    observe = Mock(return_value={"service:home": str(tmp_path / "home.py")})
    monkeypatch.setattr(cli_authority, "_operation_controller_paths", observe)
    request = Mock(return_value={"status": "current", "scope": "operation"})
    monkeypatch.setattr(cli_authority, "_call", request)
    operations = [
        {
            "operation": "home.start",
            "targets": ["service:home"],
            "effects": [{"target": "service:home", "effect": "service.start"}],
        }
    ]
    result = CliRunner().invoke(
        cli_authority.native_bridge_group,
        [
            "check-effects",
            "--native-context-id",
            "context-1",
            "--cwd",
            str(tmp_path),
            "--activity",
            "ops",
            "--document",
            "current-attempt",
            "--fence",
            "7",
            "--operations-json",
            json.dumps(operations),
            "--json",
        ],
        obj={"config": config_path},
    )
    assert result.exit_code == 0, result.output
    body = request.call_args.kwargs["body"]
    assert body["installation_root"] == str(tmp_path.resolve())
    assert body["config_path"] == str(config_path.resolve())
    assert body["observed_controller_paths"] == {"service:home": str(tmp_path / "home.py")}
    assert body["operations"] == operations and body["paths"] == []
    assert (body["activity"], body["document"], body["fence"]) == ("ops", "current-attempt", 7)
    observe.assert_called_once_with(installation, operations)


def test_file_only_effect_check_keeps_its_existing_request(monkeypatch, tmp_path):
    request = Mock(return_value={"status": "current", "scope": "implementation"})
    monkeypatch.setattr(cli_authority, "_call", request)
    observe = Mock(side_effect=AssertionError("A file check must not inspect host controllers"))
    monkeypatch.setattr(cli_authority, "_operation_controller_paths", observe)
    result = CliRunner().invoke(
        cli_authority.native_bridge_group,
        ["check-effects", "--native-context-id", "context-1", "--cwd", str(tmp_path), "--path", "effect.py", "--json"],
    )
    assert result.exit_code == 0, result.output
    assert request.call_args.kwargs["body"] == {
        "native_context_id": "context-1",
        "cwd": str(tmp_path),
        "paths": ["effect.py"],
    }
    observe.assert_not_called()


def test_empty_effect_check_refuses_before_authority_or_host_inspection(monkeypatch, tmp_path):
    request = Mock()
    monkeypatch.setattr(cli_authority, "_call", request)
    result = CliRunner().invoke(
        cli_authority.native_bridge_group,
        ["check-effects", "--native-context-id", "context-1", "--cwd", str(tmp_path)],
    )
    assert result.exit_code == 2
    assert "Supply concrete --path targets or --operations-json" in result.output
    request.assert_not_called()


@pytest.mark.parametrize("action", ["start", "stop"])
def test_aggregate_default_reports_partial_failure_with_nonzero_exit(monkeypatch, action):
    installation = object()
    monkeypatch.setattr(cli_authority, "_services_installation", lambda ctx: installation)
    outcome = {
        "service": "all",
        "ok": False,
        "phase": "compensation",
        "initial_state_restored": False,
        "started" if action == "start" else "stopped": False,
    }
    controller = Mock(return_value=outcome)
    monkeypatch.setattr(services_control, action, controller)
    result = CliRunner().invoke(cli_authority.services_group, [action, "--json"])
    assert result.exit_code == 1
    assert json.loads(result.output) == outcome
    controller.assert_called_once_with(installation, "all")


def test_start_and_open_failure_does_not_launch_home_or_browser(monkeypatch):
    import webbrowser

    monkeypatch.setattr(cli_authority, "_services_installation", lambda ctx: object())
    monkeypatch.setattr(services_control, "start", Mock(return_value={"service": "all", "started": False}))
    home = Mock()
    browser = Mock()
    monkeypatch.setattr(cli_authority, "_home", home)
    monkeypatch.setattr(webbrowser, "open", browser)
    result = CliRunner().invoke(cli_authority.home_group, ["open", "--start-services"])
    assert result.exit_code == 1
    home.assert_not_called()
    browser.assert_not_called()


def test_start_and_open_uses_existing_private_url_route(monkeypatch):
    import webbrowser

    installation = object()
    monkeypatch.setattr(cli_authority, "_services_installation", lambda ctx: installation)
    start = Mock(return_value={"service": "all", "started": True, "ok": True})
    monkeypatch.setattr(services_control, "start", start)
    url = "http://127.0.0.1:3080/?signin=synthetic-test-value"
    home = Mock(return_value=subprocess.CompletedProcess([], 0, url, ""))
    browser = Mock(return_value=True)
    monkeypatch.setattr(cli_authority, "_home", home)
    monkeypatch.setattr(webbrowser, "open", browser)
    result = CliRunner().invoke(cli_authority.home_group, ["open", "--start-services"])
    assert result.exit_code == 0, result.output
    start.assert_called_once_with(installation, "all")
    browser.assert_called_once_with(url)
    assert "synthetic-test-value" not in result.output
    assert [call.args[1] for call in home.call_args_list] == ["url", "url"]


def test_refused_browser_launch_is_not_reported_as_opened(monkeypatch):
    import webbrowser

    url = "http://127.0.0.1:3080/?signin=synthetic-private-test-value"
    monkeypatch.setattr(cli_authority, "_home", Mock(return_value=subprocess.CompletedProcess([], 0, url, "")))
    monkeypatch.setattr(webbrowser, "open", Mock(return_value=False))
    result = CliRunner().invoke(cli_authority.home_group, ["open"])
    assert result.exit_code == 1
    assert "Opened GT-KB Home" not in result.output
    assert "http://127.0.0.1:3080/ manually" in result.output
    assert "synthetic-private-test-value" not in result.output


@pytest.mark.parametrize("action", ["start", "stop"])
@pytest.mark.parametrize("confirmed", [True, False])
def test_home_lifecycle_uses_service_controller_and_requires_confirmed_result(monkeypatch, action, confirmed):
    installation = object()
    outcome = {"service": "home", "started" if action == "start" else "stopped": confirmed, "detail": {"ok": True}}
    controller = Mock(return_value=outcome)
    raw_home = Mock(side_effect=AssertionError("Home lifecycle must use the service controller"))
    monkeypatch.setattr(cli_authority, "_services_installation", lambda ctx: installation)
    monkeypatch.setattr(services_control, action, controller)
    monkeypatch.setattr(cli_authority, "_home", raw_home)
    result = CliRunner().invoke(cli_authority.home_group, [action])
    assert result.exit_code == (0 if confirmed else 1)
    assert json.loads(result.output) == outcome
    controller.assert_called_once_with(installation, "home")
    raw_home.assert_not_called()


def _shortcut_installation(tmp_path):
    root = tmp_path / "GT KB owner's Δ installation"
    target = root / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
    target.parent.mkdir(parents=True)
    target.touch()
    selected = tmp_path / "owner's Δ selected config.toml"
    selected.write_text("# synthetic selected configuration\n", encoding="utf-8")
    installation = services_control.Installation(root, "http://127.0.0.1:8765", target, selected)
    return installation, target.resolve(), selected.resolve()


def test_services_installation_preserves_the_selected_config_for_dashboard(monkeypatch, tmp_path):
    installation, target, selected = _shortcut_installation(tmp_path)
    load = Mock(return_value=SimpleNamespace(project_root=installation.root, authority_url=installation.authority_url))
    monkeypatch.setattr(cli_authority.GTConfig, "load", load)
    context = Mock()
    context.find_root.return_value.obj = {"config": str(selected)}
    resolved = cli_authority._services_installation(context)
    assert resolved.root == installation.root and resolved.python == target
    assert resolved.config_path == selected and resolved.dashboard_config_path == selected
    load.assert_called_once_with(config_path=str(selected), discover=False)


def test_shortcut_uses_installed_python_selected_config_and_working_directory_without_launching_them(
    monkeypatch, tmp_path
):
    installation, target, selected = _shortcut_installation(tmp_path)
    destination = tmp_path / "owner's Δ Desktop" / "GT KB.lnk"
    monkeypatch.setattr(cli_authority, "_services_installation", lambda ctx: installation)
    arguments = subprocess.list2cmdline(
        ["-m", "groundtruth_kb", "--config", str(selected), "home", "open", "--start-services"]
    )
    observed = {
        "path": str(destination.resolve()),
        "target": str(target),
        "arguments": arguments,
        "working_directory": str(installation.root.resolve()),
    }
    powershell = Mock(
        side_effect=[
            subprocess.CompletedProcess([], 0, json.dumps(observed | {"created": created}, ensure_ascii=False), "")
            for created in (True, False)
        ]
    )
    monkeypatch.setattr(cli_authority.subprocess, "run", powershell)
    runner = CliRunner()
    for created in (True, False):
        result = runner.invoke(
            cli_authority.home_group, ["shortcut", "--path", str(destination), "--json"], obj={"config": str(selected)}
        )
        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == observed | {"created": created}
    assert powershell.call_count == 2
    assert powershell.call_args_list[0] == powershell.call_args_list[1], (
        "repeated creation targets the same supported route"
    )
    argv = powershell.call_args.args[0]
    assert argv[:4] == ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command"]
    script = argv[4]
    for value in (str(target), arguments, str(installation.root.resolve()), str(destination.resolve())):
        assert "'" + value.replace("'", "''") + "'" in script
    assert "--start-services" in script and "WScript.Shell" in script
    assert "readback" in script, "the command inspects the written/read existing shortcut before returning"
    assert powershell.call_args.kwargs["encoding"] == "utf-8"
    assert not destination.exists(), "mocked shortcut preparation must not create a link or invoke its target"


@pytest.mark.parametrize("missing", ["python", "config"])
def test_shortcut_missing_installed_prerequisite_refuses_before_powershell(monkeypatch, tmp_path, missing):
    installation, target, selected = _shortcut_installation(tmp_path)
    (target if missing == "python" else selected).unlink()
    monkeypatch.setattr(cli_authority, "_services_installation", lambda ctx: installation)
    powershell = Mock()
    monkeypatch.setattr(cli_authority.subprocess, "run", powershell)
    result = CliRunner().invoke(cli_authority.home_group, ["shortcut", "--json"], obj={"config": str(selected)})
    assert result.exit_code == 1
    assert "installed Python and selected" in result.output
    powershell.assert_not_called()


def test_shortcut_refused_existing_link_reports_failure_and_preserves_bytes(monkeypatch, tmp_path):
    installation, target, selected = _shortcut_installation(tmp_path)
    destination = tmp_path / "existing GT KB.lnk"
    foreign = b"synthetic foreign shortcut bytes"
    destination.write_bytes(foreign)
    monkeypatch.setattr(cli_authority, "_services_installation", lambda ctx: installation)
    powershell = Mock(
        return_value=subprocess.CompletedProcess(
            [],
            1,
            "",
            "The existing shortcut points to a different command; no change was made",
        )
    )
    monkeypatch.setattr(cli_authority.subprocess, "run", powershell)
    result = CliRunner().invoke(
        cli_authority.home_group, ["shortcut", "--path", str(destination), "--json"], obj={"config": str(selected)}
    )
    assert result.exit_code == 1
    assert "different command; no change was made" in result.output
    assert destination.read_bytes() == foreign
    powershell.assert_called_once()


def test_shortcut_requires_a_parseable_readback_result(monkeypatch, tmp_path):
    installation, target, selected = _shortcut_installation(tmp_path)
    monkeypatch.setattr(cli_authority, "_services_installation", lambda ctx: installation)
    monkeypatch.setattr(
        cli_authority.subprocess, "run", Mock(return_value=subprocess.CompletedProcess([], 0, "not JSON", ""))
    )
    result = CliRunner().invoke(cli_authority.home_group, ["shortcut", "--json"], obj={"config": str(selected)})
    assert result.exit_code == 1
    assert "did not return an inspected result" in result.output
