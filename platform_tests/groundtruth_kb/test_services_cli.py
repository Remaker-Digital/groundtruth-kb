"""Mocked CLI connection tests; no workstation controller or shortcut is operated."""

from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import click
import pytest
from click.testing import CliRunner
from groundtruth_kb import cli_authority as cli
from groundtruth_kb import services_control as services
from groundtruth_kb.authority_client import AuthorityClientError

BOUND_OPTIONS = ["--activity", "ops", "--native-context-id", "pb-context", "--document", "ops-chain", "--fence", "7"]


@pytest.fixture
def facade(tmp_path, monkeypatch):
    root = tmp_path.resolve()
    config = root / "groundtruth.toml"
    config.write_text("# mocked selected installation\n", encoding="utf-8")
    python = root / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
    python.parent.mkdir(parents=True)
    python.write_bytes(b"mocked installed route")
    installation = services.Installation(root, "http://127.0.0.1:8765", python, config)
    state = {
        "service:postgresql": {"running": False, "ready": False, "task_enabled": None, "processes": []},
        "service:authority": {"running": False, "ready": False, "task_enabled": False, "processes": []},
        "service:home": {"running": False, "ready": False, "task_enabled": False, "processes": []},
    }
    paths = {
        "service:postgresql": str(installation.postgresql_data),
        "service:authority": str(installation.authority_launcher),
        "service:home": str(installation.home_script),
    }
    calls, actions, observations = [], [], []
    clock = [100.0]
    answer_transform = [None]
    request_failure = [None]

    def observe(selected, targets):
        assert selected is installation
        assert all(target in state for target in targets)
        observations.append(list(targets))
        return {
            "installation_root": str(root),
            "config_path": str(config),
            "observed_controller_paths": {target: paths[target] for target in targets},
            "states": deepcopy({target: state[target] for target in targets}),
        }

    def bound(body):
        operation = body["operations"][0]["operation"]
        targets = body["operations"][0]["targets"]
        installing = operation == "dashboard.install"
        service_targets = [] if installing else [target for target in targets if target.startswith("service:")]
        stopped = operation in {"services.stop", "services.stop-all", "home.stop", "dashboard.stop"}
        verification = {
            "states": {target: "stopped" if stopped else "running" for target in service_targets},
            "task_enabled": {
                target: not stopped for target in service_targets if state[target]["task_enabled"] is not None
            },
        }
        if installing:
            verification["installation"] = "pinned_grafana_sqlite"
        if "browser:home" in targets:
            verification["browser_origin"] = "http://127.0.0.1:3080/"
        if any(target.startswith("shortcut:") for target in targets):
            verification.update(
                shortcut_target=str(python),
                shortcut_arguments=[
                    "-m",
                    "groundtruth_kb",
                    "--config",
                    str(config),
                    "home",
                    "open",
                    "--start-services",
                ],
                shortcut_working_directory=str(root),
            )
        return {
            "operation": operation,
            "targets": targets,
            "preconditions": {
                "installation_root": str(root),
                "config_path": str(config),
                "controller_paths": body["observed_controller_paths"],
                "states": {target: "any" for target in service_targets},
            },
            "permitted_effects": body["operations"][0]["effects"]
            or (
                [
                    {"target": "service:dashboard", "effect": effect}
                    for effect in ("installation.publish", "installation.remove", "process.start", "process.stop")
                ]
                if installing
                else [
                    {"target": target, "effect": effect}
                    for target in service_targets
                    for effect in ("service.start", "service.stop")
                ]
            ),
            "expiry": "claim",
            "verification": verification,
            "containment": {"installation_only": True, "managed_processes_only": True},
            "rollback": {"restore_initial_state": True, "only_invocation_changes": True},
        }

    class Client:
        def request(self, method, path, *, body):
            assert (method, path) == ("POST", "/v1/bridge/check-effects")
            calls.append(deepcopy(body))
            if request_failure[0] is not None:
                failure = request_failure[0](body)
                if failure is not None:
                    raise failure
            now = datetime(2026, 10, 2, tzinfo=UTC)
            checked = deepcopy(body["operations"][0])
            checked.update(bound=bound(body), formal_sources=[{"id": "SPEC-OPS", "version": 2}])
            answer = {
                "status": "current",
                "scope": "operation",
                "document": "ops-chain",
                "fence": 7,
                "observed_at": now.isoformat(),
                "deadline": (now + timedelta(seconds=60)).isoformat(),
                "operations": [checked],
            }
            if answer_transform[0] is not None:
                answer_transform[0](answer)
            return answer

    def action(selected, name, *, before_effect=None, on_complete=None, desired):
        assert selected is installation
        actions.append(("start" if desired else "stop", name, before_effect is not None, on_complete is not None))
        targets = list(state) if name == "all" else ["service:" + name]
        initial = deepcopy(state)
        forward = [
            {"target": target, "effect": "service.start" if desired else "service.stop"}
            for target in targets
            if state[target]["running"] != desired
        ]
        inverse = [
            {"target": effect["target"], "effect": "service.stop" if desired else "service.start"} for effect in forward
        ]
        operation = (
            "services.start-all"
            if desired and name == "all"
            else "services.stop-all"
            if name == "all"
            else "services.start"
            if desired
            else "services.stop"
        )
        try:
            if before_effect:
                before_effect(operation, targets, [*forward, *inverse], "preflight")
                if forward:
                    before_effect(operation, targets, forward, "forward")
            for target in targets:
                state[target].update(running=desired, ready=desired)
                if state[target]["task_enabled"] is not None:
                    state[target]["task_enabled"] = desired
            if on_complete:
                on_complete()
        except services.ServiceControlError as error:
            if before_effect and inverse and state != initial:
                before_effect(operation, targets, inverse, "rollback")
                state.clear()
                state.update(initial)
            return {
                "service": name,
                "ok": False,
                "started" if desired else "stopped": False,
                "detail": str(error),
                "initial_state_restored": state == initial,
            }
        return {
            "service": name,
            "ok": True,
            "started" if desired else "stopped": True,
            "supported": [target[8:] for target in targets],
        }

    real_installation_helper = cli._services_installation
    monkeypatch.setattr(cli, "_services_installation", lambda _ctx: installation)
    monkeypatch.setattr(cli, "_client", lambda _ctx: Client())
    monkeypatch.setattr(cli.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(services, "observe_targets", observe)
    monkeypatch.setattr(
        services, "start", lambda selected, name, **kwargs: action(selected, name, desired=True, **kwargs)
    )
    monkeypatch.setattr(
        services, "stop", lambda selected, name, **kwargs: action(selected, name, desired=False, **kwargs)
    )
    return SimpleNamespace(
        root=root,
        config=config,
        installation=installation,
        python=python,
        state=state,
        calls=calls,
        actions=actions,
        observations=observations,
        clock=clock,
        answer_transform=answer_transform,
        request_failure=request_failure,
        real_installation_helper=real_installation_helper,
    )


def invoke(group, arguments):
    return CliRunner().invoke(group, arguments)


def checks(facade, **changes):
    ctx = click.Context(click.Command("mock"))
    options = {"activity": "ops", "native_context_id": "pb-context", "document": "ops-chain", "fence": 7}
    options.update(changes)
    return cli._bounded_service_effects(ctx, facade.installation, **options)


@pytest.mark.parametrize(
    "group,command",
    [
        (cli.services_group, "start"),
        (cli.services_group, "stop"),
        (cli.home_group, "start"),
        (cli.home_group, "stop"),
        (cli.home_group, "open"),
        (cli.home_group, "shortcut"),
    ],
)
def test_partial_bound_options_refuse_before_a_controller_or_authority_call(facade, group, command):
    result = invoke(group, [command, "--document", "ops-chain"])
    assert result.exit_code != 0
    assert "require --activity ops" in result.output
    assert not facade.actions and not facade.calls


def test_owner_service_commands_keep_the_offline_no_callback_route(facade):
    facade.request_failure[0] = lambda _body: AuthorityClientError("authority_unavailable", "offline")
    result = invoke(cli.services_group, ["start", "all", "--json"])
    assert result.exit_code == 0, result.output
    assert facade.actions == [("start", "all", False, False)]
    assert not facade.calls


@pytest.mark.parametrize(
    "group,args,operation",
    [
        (cli.services_group, ["start", "all"], "services.start-all"),
        (cli.services_group, ["start", "home"], "services.start"),
        (cli.home_group, ["start"], "home.start"),
    ],
)
def test_bounded_facades_use_actual_paths_full_targets_and_completion_verification(facade, group, args, operation):
    result = invoke(group, [*args, *BOUND_OPTIONS])
    assert result.exit_code == 0, result.output
    assert facade.actions[0][2:] == (True, True)
    assert len(facade.calls) >= 2
    for body in facade.calls:
        assert body["native_context_id"] == "pb-context" and body["activity"] == "ops"
        assert body["document"] == "ops-chain" and body["fence"] == 7
        assert body["installation_root"] == str(facade.root) and body["config_path"] == str(facade.config)
        assert body["operations"][0]["operation"] == operation
        assert set(body["observed_controller_paths"]) == set(body["operations"][0]["targets"])
        assert "bound" not in body and "approval" not in body


@pytest.mark.parametrize("code", ["operation_bound_required", "scope_changed", "stale_artifact_fence"])
def test_current_canonical_refusal_prevents_service_changes(facade, code):
    initial = deepcopy(facade.state)
    facade.request_failure[0] = lambda _body: AuthorityClientError(code, "current refusal")
    result = invoke(cli.services_group, ["start", "all", *BOUND_OPTIONS])
    assert result.exit_code != 0 and code in result.output
    assert facade.state == initial


@pytest.mark.parametrize(
    "change",
    [
        lambda answer: answer.update(document="another-chain"),
        lambda answer: answer.update(fence=8),
        lambda answer: answer["operations"][0].update(operation="services.stop-all"),
        lambda answer: answer["operations"][0]["targets"].pop(),
        lambda answer: answer["operations"][0]["bound"]["containment"].update(installation_only=False),
        lambda answer: answer["operations"][0]["bound"]["verification"].update(browser_origin="http://127.0.0.1:3080/"),
    ],
)
def test_unusable_current_response_is_not_a_client_grant(facade, change):
    initial = deepcopy(facade.state)
    facade.answer_transform[0] = change
    result = invoke(cli.services_group, ["start", "all", *BOUND_OPTIONS])
    assert result.exit_code != 0
    assert facade.state == initial


def test_canonical_initial_state_is_checked_before_service_effects(facade):
    initial = deepcopy(facade.state)
    facade.answer_transform[0] = lambda answer: answer["operations"][0]["bound"]["preconditions"]["states"].update(
        {"service:home": "running"}
    )
    result = invoke(cli.services_group, ["start", "all", *BOUND_OPTIONS])
    assert result.exit_code != 0 and "initial service state" in result.output
    assert facade.state == initial


def test_empty_noop_preflight_inspects_scope_without_inventing_a_native_mutation(facade):
    facade.state["service:home"].update(running=True, ready=True, task_enabled=True)
    callback = checks(facade)
    callback("services.start", ["service:home"], [], "preflight")
    assert callback.targets == ("service:home",)
    assert len(facade.calls) == 1
    assert facade.calls[0]["operations"] == [
        {"operation": "services.start", "targets": ["service:home"], "effects": []}
    ]
    assert callback.bounds["services.start"]["verification"]["states"] == {"service:home": "running"}
    callback.verify()
    facade.state["service:home"]["ready"] = False
    with pytest.raises(services.ServiceControlError, match="declared verification"):
        callback.verify()
    assert not facade.actions


def test_terminal_shutdown_continues_only_exact_same_invocation_effects_before_deadline(facade):
    callback = checks(facade, operation="services.stop-all")
    targets = ["service:authority", "service:postgresql"]
    allowed = [
        {"target": target, "effect": effect} for target in targets for effect in ("service.stop", "service.start")
    ]
    callback("services.stop-all", targets, allowed, "terminal_shutdown")
    facade.request_failure[0] = lambda _body: AuthorityClientError("authority_unavailable", "stopped authority")
    callback(
        "services.stop-all", targets, [{"target": "service:postgresql", "effect": "service.stop"}], "terminal_shutdown"
    )
    callback("services.stop-all", targets, [{"target": "service:authority", "effect": "service.start"}], "rollback")
    with pytest.raises(services.ServiceControlError, match="different command"):
        callback("services.start-all", targets, allowed, "terminal_shutdown")
    with pytest.raises(services.ServiceControlError, match="target set changed"):
        callback("services.stop-all", ["service:authority"], allowed[:1], "terminal_shutdown")
    with pytest.raises(services.ServiceControlError):
        callback(
            "services.stop-all",
            targets,
            [{"target": "service:authority", "effect": "task.disable"}],
            "terminal_shutdown",
        )
    facade.clock[0] = 160.0
    with pytest.raises(services.ServiceControlError):
        callback(
            "services.stop-all",
            targets,
            [{"target": "service:postgresql", "effect": "service.stop"}],
            "terminal_shutdown",
        )
    # A new command receives no continuation from the previous invocation.
    with pytest.raises(services.ServiceControlError):
        checks(facade, operation="services.stop-all")("services.stop-all", targets, allowed, "terminal_shutdown")


def test_terminal_continuation_never_converts_a_semantic_denial(facade):
    callback = checks(facade, operation="services.stop")
    target = ["service:authority"]
    effects = [{"target": target[0], "effect": "service.stop"}]
    callback("services.stop", target, effects, "terminal_shutdown")
    facade.request_failure[0] = lambda _body: AuthorityClientError("scope_changed", "formal changed")
    with pytest.raises(services.ServiceControlError, match="scope_changed"):
        callback("services.stop", target, effects, "terminal_shutdown")


def test_unavailable_authority_continuation_still_rechecks_exact_controller_identity(facade, monkeypatch):
    callback = checks(facade, operation="services.stop")
    target = ["service:authority"]
    effects = [{"target": target[0], "effect": "service.stop"}]
    callback("services.stop", target, effects, "terminal_shutdown")
    facade.request_failure[0] = lambda _body: AuthorityClientError("authority_unavailable", "stopped authority")
    observer = services.observe_targets

    def changed(inst, targets):
        answer = observer(inst, targets)
        answer["observed_controller_paths"]["service:authority"] = str(facade.root / "another-controller.py")
        return answer

    monkeypatch.setattr(services, "observe_targets", changed)
    with pytest.raises(services.ServiceControlError, match="installation/controllers"):
        callback("services.stop", target, effects, "terminal_shutdown")


def test_expired_or_latency_consumed_deadline_refuses_before_host_change(facade):
    initial = deepcopy(facade.state)
    facade.answer_transform[0] = lambda _answer: facade.clock.__setitem__(0, 160.0)
    result = invoke(cli.services_group, ["start", "all", *BOUND_OPTIONS])
    assert result.exit_code != 0 and "expired" in result.output
    assert facade.state == initial


def test_final_declared_verification_runs_inside_controller_compensation(facade):
    facade.answer_transform[0] = lambda _answer: None
    observer = services.observe_targets
    reads = [0]

    def fail_final(inst, targets):
        answer = observer(inst, targets)
        reads[0] += 1
        if reads[0] == 3:
            answer["states"]["service:home"]["ready"] = False
        return answer

    from pytest import MonkeyPatch

    with MonkeyPatch.context() as patch:
        patch.setattr(services, "observe_targets", fail_final)
        initial = deepcopy(facade.state)
        result = invoke(cli.services_group, ["start", "all", *BOUND_OPTIONS])
    assert result.exit_code != 0 and "declared verification" in result.output
    assert facade.state == initial


def _home_url(facade, _ctx, action):
    assert action == "url"  # Home fallback must use the identified service wrapper.
    live = facade.state["service:home"]["running"]
    return subprocess.CompletedProcess(
        [], 0 if live else 1, "http://127.0.0.1:3080/?token=private-test-value" if live else "", ""
    )


def test_home_composite_keeps_full_parent_scope_for_service_and_browser_steps(facade, monkeypatch):
    browser = []
    monkeypatch.setattr(cli, "_home", lambda ctx, action: _home_url(facade, ctx, action))
    monkeypatch.setattr("webbrowser.open", lambda url: browser.append(url) or True)
    result = invoke(cli.home_group, ["open", "--start-services", *BOUND_OPTIONS])
    assert result.exit_code == 0, result.output
    assert browser and "private-test-value" not in result.output
    assert facade.actions == [("start", "all", True, True)]
    for body in facade.calls:
        requested = body["operations"][0]
        assert requested["operation"] == "home.open.start-services"
        assert set(requested["targets"]) == {*facade.state, "browser:home"}
    assert facade.calls[-1]["operations"][0]["effects"] == [{"target": "browser:home", "effect": "browser.open"}]


@pytest.mark.parametrize("failure", ["browser_false", "native_refusal"])
def test_failed_bounded_browser_step_compensates_only_invocation_service_changes(facade, monkeypatch, failure):
    facade.state["service:postgresql"].update(running=True, ready=True)
    initial = deepcopy(facade.state)
    monkeypatch.setattr(cli, "_home", lambda ctx, action: _home_url(facade, ctx, action))
    monkeypatch.setattr("webbrowser.open", lambda _url: failure != "browser_false")
    if failure == "native_refusal":
        facade.request_failure[0] = lambda body: (
            AuthorityClientError("operation_bound_required", "browser refused")
            if any(effect["effect"] == "browser.open" for effect in body["operations"][0]["effects"])
            else None
        )
    result = invoke(cli.home_group, ["open", "--start-services", *BOUND_OPTIONS])
    assert result.exit_code != 0 and "Opened GT-KB Home" not in result.output
    assert facade.state == initial
    assert facade.actions == [("start", "all", True, True)]
    assert any(effect["effect"] == "service.stop" for effect in facade.calls[-1]["operations"][0]["effects"])


def test_home_fallback_uses_identified_callback_start(facade, monkeypatch):
    monkeypatch.setattr(cli, "_home", lambda ctx, action: _home_url(facade, ctx, action))
    monkeypatch.setattr("webbrowser.open", lambda _url: True)
    result = invoke(cli.home_group, ["open", *BOUND_OPTIONS])
    assert result.exit_code == 0, result.output
    assert facade.actions == [("start", "home", True, True)]
    assert all(body["operations"][0]["operation"] == "home.open" for body in facade.calls)


@pytest.mark.parametrize("path", [None, "relative.lnk"])
def test_bound_shortcut_requires_explicit_absolute_path_before_check_or_powershell(facade, path):
    args = ["shortcut", *BOUND_OPTIONS] + (["--path", path] if path is not None else [])
    result = invoke(cli.home_group, args)
    assert result.exit_code != 0 and "explicit absolute --path" in result.output
    assert not facade.calls


def test_bound_shortcut_checks_exact_create_effect_and_inspected_route_without_host_write(facade, monkeypatch):
    path = facade.root / "GT-KB.lnk"
    arguments = subprocess.list2cmdline(
        ["-m", "groundtruth_kb", "--config", str(facade.config), "home", "open", "--start-services"]
    )
    powershell = []

    def run(argv, **_kwargs):
        assert facade.calls  # The current native check precedes the filesystem effect.
        powershell.append(argv)
        return subprocess.CompletedProcess(
            argv,
            0,
            json.dumps(
                {
                    "path": str(path),
                    "target": str(facade.python),
                    "arguments": arguments,
                    "working_directory": str(facade.root),
                    "created": True,
                }
            ),
            "",
        )

    monkeypatch.setattr(cli.subprocess, "run", run)
    result = invoke(cli.home_group, ["shortcut", "--path", str(path), "--json", *BOUND_OPTIONS])
    assert result.exit_code == 0, result.output
    assert len(powershell) == 1 and not path.exists()
    requested = facade.calls[0]["operations"][0]
    assert requested == {
        "operation": "services.shortcut",
        "targets": ["shortcut:" + str(path)],
        "effects": [{"target": "shortcut:" + str(path), "effect": "shortcut.create"}],
    }


@pytest.mark.parametrize(
    "failure", ["save_unconfirmed", "readback_then_restored", "cleanup_denied", "cleanup_identity_changed"]
)
def test_shortcut_failure_removes_only_confirmed_new_matching_bytes_after_fresh_rollback_check(
    facade, monkeypatch, failure
):
    path = facade.root / "GT-KB.lnk"
    arguments = subprocess.list2cmdline(
        ["-m", "groundtruth_kb", "--config", str(facade.config), "home", "open", "--start-services"]
    )
    proof = {
        "sha256": "a" * 64,
        "target": str(facade.python),
        "arguments": arguments,
        "working_directory": str(facade.root),
    }
    powershell = []

    def run(argv, **_kwargs):
        powershell.append(argv)
        if len(powershell) == 1:
            confirmed = failure != "save_unconfirmed"
            return subprocess.CompletedProcess(
                argv,
                1,
                json.dumps(
                    {
                        "ok": False,
                        "path": str(path),
                        "error": "readback failed" if confirmed else "Save failed",
                        "created": confirmed,
                        "created_identity": proof if confirmed else None,
                    }
                ),
                "",
            )
        assert facade.calls[-1]["operations"][0]["effects"] == [
            {"target": "shortcut:" + str(path), "effect": "shortcut.remove"}
        ]
        cleanup = argv[-1]
        assert cleanup.index("Get-FileHash") < cleanup.index("Remove-Item -LiteralPath")
        assert "CreateShortcut" in cleanup and proof["sha256"] in cleanup
        if failure == "cleanup_identity_changed":
            return subprocess.CompletedProcess(argv, 1, "", "Residual shortcut bytes changed; no removal was performed")
        return subprocess.CompletedProcess(argv, 0, json.dumps({"removed": True, "path": str(path)}), "")

    monkeypatch.setattr(cli.subprocess, "run", run)
    if failure == "cleanup_denied":
        facade.request_failure[0] = lambda body: (
            AuthorityClientError("scope_changed", "current rollback refusal")
            if any(effect["effect"] == "shortcut.remove" for effect in body["operations"][0]["effects"])
            else None
        )
    result = invoke(cli.home_group, ["shortcut", "--path", str(path), *BOUND_OPTIONS])
    assert result.exit_code != 0
    assert not path.exists()  # The test never creates a real shortcut.
    if failure == "save_unconfirmed":
        assert len(powershell) == 1 and len(facade.calls) == 1
        assert "identity was not confirmed" in result.output
    elif failure == "readback_then_restored":
        assert len(powershell) == 2 and len(facade.calls) == 2
        assert "original absent state was restored" in result.output
    else:
        assert len(powershell) == (1 if failure == "cleanup_denied" else 2)
        assert "cleanup refused or unconfirmed" in result.output and "owner file management" in result.output


def test_existing_matching_shortcut_is_idempotent_and_never_removed(facade, monkeypatch):
    path = facade.root / "GT-KB.lnk"
    original = b"existing shortcut test preimage"
    path.write_bytes(original)
    arguments = subprocess.list2cmdline(
        ["-m", "groundtruth_kb", "--config", str(facade.config), "home", "open", "--start-services"]
    )
    powershell = []

    def run(argv, **_kwargs):
        powershell.append(argv)
        return subprocess.CompletedProcess(
            argv,
            0,
            json.dumps(
                {
                    "ok": True,
                    "path": str(path),
                    "target": str(facade.python),
                    "arguments": arguments,
                    "working_directory": str(facade.root),
                    "created": False,
                    "created_identity": None,
                }
            ),
            "",
        )

    monkeypatch.setattr(cli.subprocess, "run", run)
    result = invoke(cli.home_group, ["shortcut", "--path", str(path), *BOUND_OPTIONS])
    assert result.exit_code == 0, result.output
    assert path.read_bytes() == original and len(powershell) == 1 and len(facade.calls) == 1


@pytest.mark.parametrize("failure", ["current_refusal", "expired", "unsupported_verification"])
def test_satisfied_service_still_refuses_invalid_scope_before_any_effect(facade, failure):
    facade.state["service:home"].update(running=True, ready=True, task_enabled=True)
    initial = deepcopy(facade.state)
    if failure == "current_refusal":
        facade.request_failure[0] = lambda _body: AuthorityClientError("operation_bound_required", "current refusal")
    elif failure == "expired":
        facade.answer_transform[0] = lambda _answer: facade.clock.__setitem__(0, 160.0)
    else:
        facade.answer_transform[0] = lambda answer: answer["operations"][0]["bound"]["verification"].update(
            control_values={"control:poll_seconds": 1}
        )
    result = invoke(cli.services_group, ["start", "home", *BOUND_OPTIONS])
    assert result.exit_code != 0
    assert facade.state == initial and len(facade.calls) == 1
    assert facade.calls[0]["operations"][0]["effects"] == []


def test_deadline_consumed_during_bound_validation_refuses_before_effect(facade, monkeypatch):
    callback = checks(facade)
    original = callback._validate_bound

    def slow_validation(*args):
        original(*args)
        facade.clock[0] = 160.0

    monkeypatch.setattr(callback, "_validate_bound", slow_validation)
    with pytest.raises(services.ServiceControlError, match="expired operation check"):
        callback("services.start", ["service:home"], [], "preflight")
    assert not callback.bounds and not facade.actions


def test_shortcut_bound_accepts_equivalent_resolved_paths_and_preserves_literal_arguments(facade):
    import os

    callback = checks(facade, operation="services.shortcut")
    arguments = ["-m", "groundtruth_kb", "--config", str(facade.config), "home", "open", "--start-services"]
    callback.shortcut_route = {
        "target": str(facade.python),
        "arguments": arguments,
        "working_directory": str(facade.root),
    }

    def equivalent_paths(answer):
        verification = answer["operations"][0]["bound"]["verification"]
        verification["shortcut_target"] = str(facade.python.parent) + "/./" + facade.python.name
        verification["shortcut_working_directory"] = str(facade.root) + "/."
        if os.name == "nt":
            verification["shortcut_target"] = verification["shortcut_target"].swapcase()
            verification["shortcut_working_directory"] = verification["shortcut_working_directory"].swapcase()

    facade.answer_transform[0] = equivalent_paths
    target = "shortcut:" + str(facade.root / "GT-KB.lnk")
    callback("services.shortcut", [target], [{"target": target, "effect": "shortcut.create"}], "forward")
    assert callback.bounds and not facade.actions
    facade.answer_transform[0] = lambda answer: answer["operations"][0]["bound"]["verification"].update(
        shortcut_arguments=[*arguments, "--another-option"]
    )
    with pytest.raises(services.ServiceControlError, match="exact command"):
        callback("services.shortcut", [target], [{"target": target, "effect": "shortcut.create"}], "forward")


def test_control_path_observations_cover_current_catalog_without_inventing_effects(facade, monkeypatch):
    from groundtruth_kb.project import operational_control_config as controls

    reads = []

    def load(root):
        reads.append(root)
        return SimpleNamespace(definitions={"poll_seconds": object(), "retry_seconds": object()})

    monkeypatch.setattr(controls, "load_operational_control_catalog", load)
    operations = [{"operation": "controls.set", "targets": ["control:poll_seconds"], "effects": []}]
    paths = cli._operation_controller_paths(facade.installation, operations)
    catalog = str((facade.root / controls.CATALOG_RELATIVE_PATH).resolve())
    assert paths == {"control:poll_seconds": catalog, "control:retry_seconds": catalog}
    assert reads == [facade.root]
    assert operations[0]["effects"] == [] and not facade.calls and not facade.actions


def test_discovered_selected_config_is_retained_when_project_root_is_elsewhere(facade, monkeypatch):
    from groundtruth_kb import config as config_module

    selected = facade.root.parent / "discovery" / "groundtruth.toml"
    loads = []
    monkeypatch.setattr(config_module, "_find_config", lambda: selected)

    def load(*, config_path, discover):
        loads.append((config_path, discover))
        return SimpleNamespace(project_root=facade.root, authority_url="http://127.0.0.1:8765")

    monkeypatch.setattr(cli.GTConfig, "load", load)
    installation = facade.real_installation_helper(click.Context(click.Command("mock")))
    assert loads == [(selected, False)]
    assert installation.root == facade.root
    assert installation.dashboard_config_path == selected.resolve()


@pytest.mark.parametrize(
    "operation,callback_operation,effect",
    [
        ("dashboard.start", "services.start", "service.start"),
        ("dashboard.stop", "services.stop", "service.stop"),
    ],
)
def test_dashboard_service_callback_preserves_enclosing_operation(
    facade, monkeypatch, operation, callback_operation, effect
):
    target = "service:dashboard"
    facade.state[target] = {"running": False, "ready": False, "task_enabled": None, "processes": []}
    identity = str(facade.root / "infrastructure" / "grafana" / "bin" / "grafana-server.exe")

    def observe(inst, targets):
        assert inst is facade.installation and targets == [target]
        return {
            "installation_root": str(facade.root),
            "config_path": str(facade.config),
            "observed_controller_paths": {target: identity},
            "states": {target: deepcopy(facade.state[target])},
        }

    monkeypatch.setattr(services, "observe_targets", observe)
    callback = checks(facade, operation=operation)
    callback(callback_operation, [target], [{"target": target, "effect": effect}], "forward")
    assert facade.calls[0]["operations"][0]["operation"] == operation
    assert callback.bounds[operation]["verification"]["states"] == {
        target: "stopped" if operation.endswith("stop") else "running"
    }
    assert not facade.actions


def test_foreground_observer_checks_actual_invocation_and_readiness_without_grafana_inventory(facade):
    target = "service:dashboard"
    facade.state[target] = {"running": False, "ready": False, "task_enabled": None, "processes": []}
    controller = str(facade.python)
    observations = []

    def observe():
        observations.append("owned-foreground")
        return {
            "installation_root": str(facade.root),
            "config_path": str(facade.config),
            "observed_controller_paths": {target: controller},
            "states": {target: deepcopy(facade.state[target])},
        }

    callback = checks(facade, operation="dashboard.serve")
    with pytest.raises(services.ServiceControlError, match="actual invocation observer"):
        callback("dashboard.serve", [target], [], "preflight")
    assert not facade.calls and not facade.observations
    callback.bind_foreground_observer(observe)
    callback("dashboard.serve", [target], [{"target": target, "effect": "service.start"}], "forward")
    assert facade.calls[0]["observed_controller_paths"] == {target: controller}
    assert facade.calls[0]["operations"][0]["operation"] == "dashboard.serve"
    assert facade.calls[0]["operations"][0]["effects"] == [{"target": target, "effect": "service.start"}]
    assert callback.initial[target]["running"] is False
    facade.state[target].update(running=True, ready=True)
    callback.verify()
    assert not facade.observations and not facade.actions
    facade.state[target]["ready"] = False
    with pytest.raises(services.ServiceControlError, match="final service state"):
        callback.verify()
    with pytest.raises(services.ServiceControlError, match="target set changed"):
        callback("dashboard.serve", [target, "service:home"], [], "forward")
    with pytest.raises(services.ServiceControlError, match="Only one foreground"):
        callback.bind_foreground_observer(observe)
    ordinary = checks(facade, operation="services.start")
    with pytest.raises(services.ServiceControlError, match="Only one foreground"):
        ordinary.bind_foreground_observer(observe)
    assert observations == ["owned-foreground"] * 3


def test_foreground_scope_observes_current_python_instead_of_persistent_dashboard_pair(facade, monkeypatch):
    import sys

    def refuse_inventory(*_args, **_kwargs):
        raise AssertionError("Foreground refresh serve must not require or observe a Grafana pair")

    monkeypatch.setattr(services, "_inventory", refuse_inventory)
    operations = [{"operation": "dashboard.serve", "targets": ["service:dashboard"], "effects": []}]
    paths = cli._operation_controller_paths(facade.installation, operations)
    assert paths == {"service:dashboard": str(Path(sys.executable).resolve())}
    assert operations[0]["effects"] == [] and not facade.calls
    mixed = [*operations, {"operation": "dashboard.stop", "targets": ["service:dashboard"], "effects": []}]
    with pytest.raises(click.ClickException, match="different controllers"):
        cli._operation_controller_paths(facade.installation, mixed)


@pytest.mark.parametrize("dashboard_installed", [False, True])
def test_foreground_and_aggregate_conflict_only_when_actual_inventory_contains_dashboard(
    facade, monkeypatch, dashboard_installed
):
    controllers = [SimpleNamespace(name="authority", executable=facade.installation.authority_launcher)]
    if dashboard_installed:
        controllers.append(SimpleNamespace(name="dashboard", executable=facade.root / "grafana-server.exe"))
    inventories = []

    def inventory(installation, runner):
        assert installation is facade.installation
        inventories.append(installation)
        return controllers, {}

    monkeypatch.setattr(services, "_inventory", inventory)
    operations = [
        {"operation": "dashboard.serve", "targets": ["service:dashboard"], "effects": []},
        {"operation": "services.start-all", "targets": ["service:all"], "effects": []},
    ]
    if dashboard_installed:
        with pytest.raises(click.ClickException, match="different controllers"):
            cli._operation_controller_paths(facade.installation, operations)
    else:
        assert cli._operation_controller_paths(facade.installation, operations) == {
            "service:dashboard": str(Path(cli.sys.executable).resolve()),
            "service:authority": str(facade.installation.authority_launcher.resolve()),
        }
    assert inventories == [facade.installation] and not facade.calls and not facade.actions


def test_foreground_readiness_must_finish_within_admission_window_without_extending_deadline(facade):
    target = "service:dashboard"
    facade.state[target] = {"running": False, "ready": False, "task_enabled": None, "processes": []}

    def observe():
        return {
            "installation_root": str(facade.root),
            "config_path": str(facade.config),
            "observed_controller_paths": {target: str(facade.python)},
            "states": {target: deepcopy(facade.state[target])},
        }

    callback = checks(facade, operation="dashboard.serve")
    callback.bind_foreground_observer(observe)
    callback("dashboard.serve", [target], [{"target": target, "effect": "service.start"}], "forward")
    facade.state[target].update(running=True, ready=True)
    facade.clock[0] = 160.0
    with pytest.raises(services.ServiceControlError, match="expired before its final verification"):
        callback.verify()
    assert callback.deadline == 160.0 and len(facade.calls) == 1 and not facade.actions


def test_foreground_observed_root_must_match_effect_installation_before_bind(facade):
    target = "service:dashboard"
    facade.state[target] = {"running": False, "ready": False, "task_enabled": None, "processes": []}

    def observe():
        return {
            "installation_root": str(facade.root / "other-installation"),
            "config_path": str(facade.config),
            "observed_controller_paths": {target: str(facade.python)},
            "states": {target: deepcopy(facade.state[target])},
        }

    callback = checks(facade, operation="dashboard.serve")
    callback.bind_foreground_observer(observe)
    with pytest.raises(services.ServiceControlError, match="installation/controllers"):
        callback("dashboard.serve", [target], [{"target": target, "effect": "service.start"}], "forward")
    assert callback.initial is None and not callback.bounds and not facade.actions


@pytest.mark.parametrize("initially_pinned", [False, True])
def test_installation_observer_requires_current_pinned_result_without_service_inventory(facade, initially_pinned):
    target = "service:dashboard"
    destination = facade.root / ".groundtruth" / "tools" / "grafana"
    pinned = [initially_pinned]

    def observe():
        return {
            "installation_root": str(facade.root),
            "config_path": str(facade.config),
            "observed_controller_paths": {target: str(destination)},
            "states": {},
            "installation": {"predicate": "pinned_grafana_sqlite", "verified": pinned[0]},
        }

    callback = checks(facade, operation="dashboard.install")
    with pytest.raises(services.ServiceControlError, match="actual invocation observer"):
        callback("dashboard.install", [target], [], "preflight")
    callback.bind_installation_observer(observe)
    callback("dashboard.install", [target], [], "preflight")
    assert callback.initial == {} and callback.deadline == 160.0
    if not initially_pinned:
        with pytest.raises(services.ServiceControlError, match="final pinned Grafana/SQLite"):
            callback.verify()
    effects = [
        {"target": target, "effect": effect}
        for effect in ("installation.publish", "installation.remove", "process.start", "process.stop")
    ]
    callback("dashboard.install", [target], effects, "forward")
    pinned[0] = True
    callback.verify()
    assert len(facade.calls) == 2 and facade.calls[0]["operations"][0]["effects"] == []
    assert facade.calls[1]["operations"] == [
        {"operation": "dashboard.install", "targets": [target], "effects": effects}
    ]
    assert all(body["observed_controller_paths"] == {target: str(destination)} for body in facade.calls)
    assert not facade.actions and not facade.observations
    facade.clock[0] = 160.0
    with pytest.raises(services.ServiceControlError, match="expired before its final verification"):
        callback.verify()


def test_installation_observer_cannot_rebind_or_inspect_services_and_foreground_invocations(facade):
    target = "service:dashboard"

    def observer():
        return {
            "installation_root": str(facade.root),
            "config_path": str(facade.config),
            "observed_controller_paths": {target: str(facade.root / ".groundtruth/tools/grafana")},
            "states": {},
            "installation": {"predicate": "pinned_grafana_sqlite", "verified": True},
        }

    callback = checks(facade, operation="dashboard.install")
    callback.bind_installation_observer(observer)
    with pytest.raises(services.ServiceControlError, match="Only one Dashboard installation"):
        callback.bind_installation_observer(observer)
    with pytest.raises(services.ServiceControlError, match="another controller"):
        callback("dashboard.install", [target, "service:home"], [], "preflight")
    with pytest.raises(services.ServiceControlError, match="Only one foreground"):
        callback.bind_foreground_observer(observer)
    for operation in ("services.start", "dashboard.start", "dashboard.serve"):
        with pytest.raises(services.ServiceControlError, match="Only one Dashboard installation"):
            checks(facade, operation=operation).bind_installation_observer(observer)
    assert not facade.calls and not facade.actions and not facade.observations


@pytest.mark.parametrize(
    "predicate,reason",
    [
        ("missing", "declared pinned Grafana/SQLite"),
        ("service_states", "does not match this service command"),
        ("task", "task-enabled verification"),
        ("control", "control-value mutations"),
        ("browser", "declared browser verification"),
        ("shortcut", "declared shortcut verification"),
        ("precondition", "declared initial-state predicate"),
    ],
)
def test_installation_refuses_unsupported_declared_verification_before_effect(facade, predicate, reason):
    target = "service:dashboard"
    callback = checks(facade, operation="dashboard.install")
    callback.bind_installation_observer(
        lambda: {
            "installation_root": str(facade.root),
            "config_path": str(facade.config),
            "observed_controller_paths": {target: str(facade.root / ".groundtruth/tools/grafana")},
            "states": {},
            "installation": {"predicate": "pinned_grafana_sqlite", "verified": False},
        }
    )

    def unsupported(answer):
        bound = answer["operations"][0]["bound"]
        verification = bound["verification"]
        if predicate == "missing":
            verification.pop("installation")
        elif predicate == "service_states":
            verification["states"] = {target: "running"}
        elif predicate == "task":
            verification["task_enabled"] = {target: True}
        elif predicate == "control":
            verification["control_values"] = {"control:left": 3}
        elif predicate == "browser":
            verification["browser_origin"] = "http://127.0.0.1:3080/"
        elif predicate == "shortcut":
            verification["shortcut_arguments"] = ["home", "open"]
        else:
            bound["preconditions"]["states"] = {target: "stopped"}

    facade.answer_transform[0] = unsupported
    with pytest.raises(services.ServiceControlError, match=reason):
        callback("dashboard.install", [target], [{"target": target, "effect": "installation.publish"}], "forward")
    assert callback.initial is None and not callback.bounds and not facade.actions


@pytest.mark.parametrize(
    "bad_observation", ["root", "binary_identity", "predicate", "truthy_verified", "service_states"]
)
def test_installation_observer_refuses_nonstandard_or_unprovable_identity_before_effect(facade, bad_observation):
    target = "service:dashboard"
    observation = {
        "installation_root": str(facade.root),
        "config_path": str(facade.config),
        "observed_controller_paths": {target: str(facade.root / ".groundtruth/tools/grafana")},
        "states": {},
        "installation": {"predicate": "pinned_grafana_sqlite", "verified": False},
    }
    if bad_observation == "root":
        observation["installation_root"] = str(facade.root / "foreign")
    elif bad_observation == "binary_identity":
        observation["observed_controller_paths"][target] = str(
            facade.root / ".groundtruth/tools/grafana/bin/grafana-server.exe"
        )
    elif bad_observation == "predicate":
        observation["installation"]["predicate"] = "some_existing_installation"
    elif bad_observation == "truthy_verified":
        observation["installation"]["verified"] = 1
    else:
        observation["states"] = {target: {"running": False, "ready": False, "task_enabled": True, "processes": []}}
    callback = checks(facade, operation="dashboard.install")
    callback.bind_installation_observer(lambda: deepcopy(observation))
    reason = "installation/controllers" if bad_observation == "root" else "declared pinned Grafana/SQLite"
    with pytest.raises(services.ServiceControlError, match=reason):
        callback("dashboard.install", [target], [], "preflight")
    assert callback.initial is None and not callback.bounds and not facade.actions


def test_installation_scope_identifies_standard_destination_before_any_binary_exists(facade, monkeypatch):
    def no_inventory(*_args, **_kwargs):
        raise AssertionError("Cold installation must not require existing service controllers")

    monkeypatch.setattr(services, "_inventory", no_inventory)
    operation = {"operation": "dashboard.install", "targets": ["service:dashboard"], "effects": []}
    assert cli._operation_controller_paths(facade.installation, [operation]) == {
        "service:dashboard": str((facade.root / ".groundtruth/tools/grafana").resolve())
    }
    for other in ("dashboard.start", "dashboard.serve"):
        with pytest.raises(click.ClickException, match="different controllers"):
            cli._operation_controller_paths(facade.installation, [operation, {**operation, "operation": other}])
    assert not facade.calls and not facade.actions


@pytest.mark.parametrize(
    "code", ["operation_bound_required", "scope_changed", "stale_artifact_fence", "authority_unavailable"]
)
def test_installation_current_refusal_never_uses_service_shutdown_continuation(facade, code):
    target = "service:dashboard"
    callback = checks(facade, operation="dashboard.install")
    callback.bind_installation_observer(
        lambda: {
            "installation_root": str(facade.root),
            "config_path": str(facade.config),
            "observed_controller_paths": {target: str(facade.root / ".groundtruth/tools/grafana")},
            "states": {},
            "installation": {"predicate": "pinned_grafana_sqlite", "verified": False},
        }
    )
    callback("dashboard.install", [target], [], "preflight")
    facade.request_failure[0] = lambda _body: AuthorityClientError(code, "current installer refusal")
    for phase, effect in (("forward", "installation.publish"), ("rollback", "installation.remove")):
        with pytest.raises(services.ServiceControlError, match=code):
            callback("dashboard.install", [target], [{"target": target, "effect": effect}], phase)
    assert callback.terminal is None and len(facade.calls) == 3
    assert not facade.observations and not facade.actions


def test_persistent_service_cannot_claim_the_installation_verification_predicate(facade):
    callback = checks(facade, operation="services.start")
    facade.answer_transform[0] = lambda answer: answer["operations"][0]["bound"]["verification"].update(
        installation="pinned_grafana_sqlite"
    )
    with pytest.raises(services.ServiceControlError, match="declared installation verification"):
        callback("services.start", ["service:home"], [{"target": "service:home", "effect": "service.start"}], "forward")
    assert callback.initial is None and not callback.bounds and not facade.actions
