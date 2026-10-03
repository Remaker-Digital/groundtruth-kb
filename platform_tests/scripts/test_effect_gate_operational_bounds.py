"""Bounded controller collection does not bypass other native effect checks.

These tests mock the native CLI and do not operate services or inspect installed
controllers. Controller and native tests prove their respective effect boundaries.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from groundtruth_kb.bridge import effect_gate as gate

SELECTORS = "--activity ops --native-context-id ctx --document ops-chain --fence 7"


def _payload(root: Path, command: object) -> dict[str, object]:
    return {
        "cwd": str(root),
        "project_root": str(root),
        "session_id": "ctx",
        "tool_name": "Shell",
        "tool_input": {"command": command},
    }


@pytest.fixture
def native_answer(monkeypatch):
    calls = []
    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "ctx")

    def answer(argv, **kwargs):
        calls.append((argv, kwargs))
        if "check-program" in argv:
            response = {"status": "current", "scope": "program", "claims": 1}
        elif "--operations-json" in argv:
            requests = json.loads(argv[argv.index("--operations-json") + 1])
            checked = []
            for request in requests:
                targets = [target for target in request["targets"] if target != "service:all"]
                if "service:all" in request["targets"]:
                    targets += ["service:authority", "service:home"]
                checked.append({"operation": request["operation"], "targets": targets})
            response = {
                "status": "current",
                "scope": "operation",
                "document": "ops-chain",
                "fence": 7,
                "observed_at": "2026-10-02T00:00:00+00:00",
                "deadline": "2026-10-02T00:10:00+00:00",
                "operations": checked,
            }
            if "--path" in argv:
                response["files"] = {"status": "current", "scope": "implementation"}
        else:
            response = {"status": "current", "scope": "implementation"}
        return SimpleNamespace(returncode=0, stdout=json.dumps(response), stderr="")

    monkeypatch.setattr(gate.subprocess, "run", answer)
    return calls


def _requests(calls):
    argv = next(argv for argv, _kwargs in calls if "--operations-json" in argv)
    return json.loads(argv[argv.index("--operations-json") + 1])


@pytest.mark.parametrize(
    "command,operation,targets",
    [
        ("gt services start", "services.start-all", ["service:all"]),
        ("gt services stop all", "services.stop-all", ["service:all"]),
        ("gt services start postgresql", "services.start", ["service:postgresql"]),
        ("gt services stop home", "services.stop", ["service:home"]),
        ("gt home start", "home.start", ["service:home"]),
        ("gt home stop", "home.stop", ["service:home"]),
        ("gt home open", "home.open", ["service:home", "browser:home"]),
        ("gt home open --start-services", "home.open.start-services", ["service:all", "browser:home"]),
        ("gt dashboard start --json", "dashboard.start", ["service:dashboard"]),
        ("gt dashboard stop --json", "dashboard.stop", ["service:dashboard"]),
        ("gt dashboard serve", "dashboard.serve", ["service:dashboard"]),
        ("gt dashboard install --json", "dashboard.install", ["service:dashboard"]),
        ("python -m groundtruth_kb services start", "services.start-all", ["service:all"]),
    ],
)
def test_wired_controllers_use_explicit_initial_selectors(tmp_path, native_answer, command, operation, targets):
    assert gate.gate_decision(_payload(tmp_path, f"{command} {SELECTORS}")) == {}
    requests = _requests(native_answer)
    assert len(requests) == 1
    assert requests[0]["operation"] == operation and requests[0]["targets"] == targets
    assert requests[0]["effects"] == []


def test_default_all_does_not_guess_the_installed_aggregate(tmp_path, native_answer):
    command = f"gt services start {SELECTORS}; gt services stop {SELECTORS}"
    assert gate.gate_decision(_payload(tmp_path, command)) == {}
    requests = _requests(native_answer)
    assert [request["operation"] for request in requests] == ["services.start-all", "services.stop-all"]
    assert all(request["targets"] == ["service:all"] for request in requests)
    assert all(request["effects"] == [] for request in requests)
    assert len(native_answer) == 1


@pytest.mark.parametrize(
    "wrapper",
    [
        'pwsh -NoProfile -Command "{body}"',
        "& {{ {body} }}",
    ],
)
def test_nested_controller_commands_are_all_collected(tmp_path, wrapper):
    body = f"gt services start {SELECTORS}; gt home open {SELECTORS}"
    collected = gate._ordinary_operations_from_payload(_payload(tmp_path, wrapper.format(body=body)))
    assert "error" not in collected
    assert [operation["operation"] for operation in collected["operations"]] == ["services.start-all", "home.open"]


def test_one_exact_config_is_forwarded_to_native_transport(tmp_path, native_answer):
    config = str(tmp_path / "selected.toml")
    command = f'gt --config "{config}" services start {SELECTORS}; gt --config "{config}" home open {SELECTORS}'
    assert gate.gate_decision(_payload(tmp_path, command)) == {}
    argv, _kwargs = native_answer[0]
    assert argv[argv.index("--config") + 1] == config
    assert argv.index("--config") < argv.index("bridge")
    assert len(_requests(native_answer)) == 2


def test_shortcut_needs_its_literal_destination(tmp_path, native_answer):
    shortcut = str(tmp_path / "GT-KB.lnk")
    assert gate.gate_decision(_payload(tmp_path, f'gt home shortcut --path "{shortcut}" {SELECTORS}')) == {}
    request = _requests(native_answer)[0]
    assert request["operation"] == "services.shortcut"
    assert request["targets"] == ["shortcut:" + shortcut]
    assert request["effects"] == []


@pytest.mark.parametrize(
    "command,code",
    [
        ("gt services start", "operation_selector_required"),
        ("gt dashboard start", "operation_selector_required"),
        ("gt dashboard stop", "operation_selector_required"),
        ("gt dashboard serve", "operation_selector_required"),
        ("gt dashboard install", "operation_selector_required"),
        (f"gt services start {SELECTORS.replace('--activity ops', '--activity build')}", "operation_activity_required"),
        (f"gt services start {SELECTORS.replace('--fence 7', '--fence')}", "operation_selector_required"),
        (f"gt services start {SELECTORS.replace('--fence 7', '--fence 0')}", "operation_selector_required"),
        (
            f"gt services start {SELECTORS.replace('--document ops-chain', '--document $document')}",
            "operation_request_uninspectable",
        ),
        (f"gt services start $service {SELECTORS}", "operation_request_uninspectable"),
        (f"gt services start unknown {SELECTORS}", "operation_request_uninspectable"),
        (f"gt services start {SELECTORS} --fence 8", "operation_request_uninspectable"),
        (f"gt services start {SELECTORS} --force", "operation_request_uninspectable"),
        (f"gt --config relative.toml services start {SELECTORS}", "operation_request_uninspectable"),
        (f"gt home shortcut {SELECTORS}", "operation_selector_required"),
    ],
)
def test_missing_unreadable_or_unsupported_values_never_contact_native(tmp_path, native_answer, command, code):
    result = gate.gate_decision(_payload(tmp_path, command))
    assert result["decision"] == "block" and result["reason_code"] == code
    assert native_answer == []


@pytest.mark.parametrize(
    "replacement",
    [
        ("--native-context-id ctx", "--native-context-id other"),
        ("--document ops-chain", "--document another-chain"),
        ("--fence 7", "--fence 8"),
    ],
)
def test_every_collected_command_has_the_same_exact_selectors(tmp_path, native_answer, replacement):
    other = SELECTORS.replace(*replacement)
    result = gate.gate_decision(_payload(tmp_path, f"gt services start {SELECTORS}; gt home open {other}"))
    assert result["reason_code"] == "operation_selector_mismatch"
    assert native_answer == []


def test_configs_and_host_context_cannot_be_substituted(tmp_path, native_answer):
    first, second = str(tmp_path / "one.toml"), str(tmp_path / "two.toml")
    command = f'gt --config "{first}" services start {SELECTORS}; gt --config "{second}" home open {SELECTORS}'
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == "operation_selector_mismatch"
    command = f"gt services start {SELECTORS.replace('--native-context-id ctx', '--native-context-id other')}"
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == "invalid_native_context"
    assert native_answer == []


@pytest.mark.parametrize(
    "other",
    [
        "Stop-Process -Id 123",
        "pg_ctl start -D data",
        "gt service serve",
        "gt db postgres init",
        "gt db postgres import-current --snapshot current.json",
    ],
)
def test_a_covered_controller_never_covers_another_owner_operation(tmp_path, native_answer, other):
    result = gate.gate_decision(_payload(tmp_path, f"gt services start {SELECTORS}; {other}"))
    assert result["reason_code"] == "owner_operation_only"
    assert native_answer == []


@pytest.mark.parametrize(
    "other,code",
    [
        ("gt projects move-item --work-item-id WI-1 --from-project P1 --to-project P2", "owner_lever_only"),
        ("gt backlog record WI-1 --project-id P2 --expected-version 3", "owner_lever_only"),
        ("Get-Content .env", "credential_material_protected"),
        ("Get-ChildItem . -Recurse", "context_traversal"),
        ("Set-Content -LiteralPath $output -Value x", "unknown_effect_targets"),
    ],
)
def test_other_guards_still_apply_to_a_tool_call_with_ordinary_operations(tmp_path, native_answer, other, code):
    result = gate.gate_decision(_payload(tmp_path, f"gt services start {SELECTORS}; {other}"))
    assert result["reason_code"] == code
    assert native_answer == []


def test_gt_argument_words_are_not_cmdlets_but_redirects_are_real_writes(tmp_path, native_answer, monkeypatch):
    selectors = SELECTORS.replace("ops-chain", "set-content")
    payload = _payload(tmp_path, f"gt services start {selectors} > started.txt")
    assert gate.changed_paths(payload) == (["started.txt"], True)
    # The current response must still echo this actual document; fix the mocked answer accordingly.
    original = gate.subprocess.run

    def answer(argv, **kwargs):
        result = original(argv, **kwargs)
        response = json.loads(result.stdout)
        response["document"] = "set-content"
        return SimpleNamespace(returncode=0, stdout=json.dumps(response), stderr="")

    monkeypatch.setattr(gate.subprocess, "run", answer)
    assert gate.gate_decision(payload) == {}
    argv, _kwargs = native_answer[0]
    assert argv[argv.index("--path") + 1] == "started.txt"
    assert len(_requests(native_answer)) == 1


def test_ordinary_operations_do_not_skip_the_program_guard(tmp_path, native_answer, monkeypatch):
    observed = []

    def refuse_program(native, root, env, program):
        observed.append((native, root, program))
        return {"decision": "block", "reason_code": "program_claim_required", "reason": "No current program claim"}

    monkeypatch.setattr(gate, "_native_program_check", refuse_program)
    result = gate.gate_decision(_payload(tmp_path, f"gt services start {SELECTORS}; python worker.py"))
    assert result["reason_code"] == "program_claim_required"
    assert len(native_answer) == 1 and observed


def test_uninspectable_later_command_is_refused_before_a_native_grant(tmp_path, native_answer):
    result = gate.gate_decision(_payload(tmp_path, f"gt services start {SELECTORS}; pwsh -EncodedCommand ZwB0AA=="))
    assert result["decision"] == "block"
    assert native_answer == []


def test_native_denial_and_malformed_success_do_not_fall_back_to_owner(tmp_path, native_answer, monkeypatch):
    command = f"gt services start {SELECTORS}"
    monkeypatch.setattr(
        gate.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=1,
            stdout="",
            stderr="Error: operation_bound_required: No applicable exact bound",
        ),
    )
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == "operation_bound_required"
    monkeypatch.setattr(
        gate.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stdout='{"status":"current","scope":"operation"}',
            stderr="",
        ),
    )
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == "invalid_effect_response"


CONTROL_DIGEST = "sha256:" + "a" * 64


def _control_command(root, *, selectors=SELECTORS, config=None):
    prefix = f'gt --config "{config}"' if config is not None else "gt"
    return f'{prefix} controls set --input "{root / "proposal.toml"}" --expected-sha256 {CONTROL_DIGEST} {selectors}'


def _control_definition(value):
    # Match catalog_dict's dataclass projection, including the current field
    # names and numeric JSON values; the input TOML uses a different shape.
    return {
        "control_id": "left",
        "description": "Explicit isolated fixture control.",
        "numeric_kind": "integer",
        "unit": "seconds",
        "value": value,
        "minimum": 1,
        "maximum": 120,
        "category": "timeout",
        "scope": "per_operation",
        "zero_semantics": "forbidden",
        "rationale": "Fixture policy.",
        "tolerance_rationale": "Explicit fixture bounds.",
        "migration_state": "active",
        "consumers": ["fixture.consumer"],
        "evidence_refs": ["fixture:observation"],
        "reload_behavior": "next_operation",
        "failure_disposition": "refuse_new_operation",
        "observability": ["catalog_sha256", "refusal_code"],
        "capacity_observation_key": None,
    }


def _control_difference(*, noop=False):
    return {
        "before_sha256": CONTROL_DIGEST,
        "after_sha256": CONTROL_DIGEST if noop else "sha256:" + "b" * 64,
        "controls": {} if noop else {"left": {"before": _control_definition(2), "after": _control_definition(3)}},
        "invariants": {"before": [], "after": []},
    }


def _mock_control_diff(monkeypatch, calls, difference):
    original = gate.subprocess.run

    def answer(argv, **kwargs):
        if "controls" in argv and "diff" in argv:
            calls.append((argv, kwargs))
            return SimpleNamespace(returncode=0, stdout=json.dumps(difference), stderr="")
        return original(argv, **kwargs)

    monkeypatch.setattr(gate.subprocess, "run", answer)


def test_controls_initial_scope_uses_selected_diff_and_only_changed_keys(tmp_path, native_answer, monkeypatch):
    config = tmp_path / "selected.toml"
    _mock_control_diff(monkeypatch, native_answer, _control_difference())
    assert gate.gate_decision(_payload(tmp_path, _control_command(tmp_path, config=config))) == {}
    assert _requests(native_answer) == [{"operation": "controls.set", "targets": ["control:left"], "effects": []}]
    diff_argv, kwargs = native_answer[0]
    assert diff_argv[diff_argv.index("--config") + 1] == str(config)
    assert diff_argv[diff_argv.index("--input") + 1] == str(tmp_path / "proposal.toml")
    assert kwargs["cwd"] == tmp_path and kwargs["env"].get("GT_PROJECT_ROOT") == gate.os.environ.get("GT_PROJECT_ROOT")
    assert kwargs["timeout"] == 10 and kwargs["encoding"] == "utf-8"
    checked_argv, _kwargs = native_answer[1]
    assert checked_argv[checked_argv.index("--config") + 1] == str(config)


def test_controls_byte_noop_has_no_dummy_target_or_native_permission_call(tmp_path, native_answer, monkeypatch):
    _mock_control_diff(monkeypatch, native_answer, _control_difference(noop=True))
    assert gate.gate_decision(_payload(tmp_path, _control_command(tmp_path))) == {}
    assert len(native_answer) == 1
    assert "diff" in native_answer[0][0] and "--operations-json" not in native_answer[0][0]
    # The literal selectors remain on the actual command, whose writer CAS will
    # refuse any catalog drift between this inspection and the no-op execution.


def test_controls_noop_still_checks_redirect_and_other_program(tmp_path, native_answer, monkeypatch):
    _mock_control_diff(monkeypatch, native_answer, _control_difference(noop=True))
    observed = []
    monkeypatch.setattr(
        gate,
        "_native_program_check",
        lambda native, root, env, program: (
            observed.append(program) or {"decision": "block", "reason_code": "program_claim_required"}
        ),
    )
    command = _control_command(tmp_path) + " > applied.txt; python worker.py"
    assert gate.changed_paths(_payload(tmp_path, command)) == (["applied.txt"], True)
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == "program_claim_required"
    assert len(native_answer) == 2 and observed
    argv, _kwargs = native_answer[1]
    assert "--operations-json" not in argv and argv[argv.index("--path") + 1] == "applied.txt"


@pytest.mark.parametrize(
    "alteration,code",
    [
        ("metadata", "operation_value_scope_required"),
        ("addition", "operation_value_scope_required"),
        ("invariant", "operation_value_scope_required"),
        ("comment_noop", "operation_value_scope_required"),
        ("stale", "generation_conflict"),
        ("bare_diff_digest", "invalid_control_diff"),
        ("wrong_diff_prefix", "invalid_control_diff"),
        ("malformed", "invalid_control_diff"),
    ],
)
def test_controls_outside_value_scope_or_stale_diff_never_gets_permission(
    tmp_path, native_answer, monkeypatch, alteration, code
):
    difference = _control_difference(noop=alteration == "comment_noop")
    if alteration == "metadata":
        difference["controls"]["left"]["after"]["description"] = "Changed metadata"
    elif alteration == "addition":
        difference["controls"]["left"]["before"] = None
    elif alteration == "invariant":
        difference["invariants"]["after"] = [{"operator": "lt"}]
    elif alteration == "comment_noop":
        difference["after_sha256"] = "sha256:" + "b" * 64
    elif alteration == "stale":
        difference["before_sha256"] = "sha256:" + "c" * 64
    elif alteration == "bare_diff_digest":
        difference["before_sha256"] = "a" * 64
    elif alteration == "wrong_diff_prefix":
        difference["after_sha256"] = "sha512:" + "b" * 64
    else:
        difference.pop("controls")
    _mock_control_diff(monkeypatch, native_answer, difference)
    assert gate.gate_decision(_payload(tmp_path, _control_command(tmp_path)))["reason_code"] == code
    assert len(native_answer) == 1 and "diff" in native_answer[0][0]


@pytest.mark.parametrize(
    "alteration,code",
    [
        ("input", "operation_selector_required"),
        ("digest", "operation_selector_required"),
        ("bare_digest", "operation_selector_required"),
        ("uppercase_digest", "operation_selector_required"),
        ("wrong_digest_prefix", "operation_selector_required"),
        ("selectors", "operation_selector_required"),
        ("duplicate", "operation_request_uninspectable"),
        ("variable", "operation_request_uninspectable"),
    ],
)
def test_controls_requires_complete_literal_invocation_before_diff(tmp_path, native_answer, alteration, code):
    command = _control_command(tmp_path)
    if alteration == "input":
        command = command.replace(f'--input "{tmp_path / "proposal.toml"}"', "--input relative.toml")
    elif alteration == "digest":
        command = command.replace(CONTROL_DIGEST, "invalid")
    elif alteration == "bare_digest":
        command = command.replace(CONTROL_DIGEST, "a" * 64)
    elif alteration == "uppercase_digest":
        command = command.replace(CONTROL_DIGEST, "sha256:" + "A" * 64)
    elif alteration == "wrong_digest_prefix":
        command = command.replace(CONTROL_DIGEST, "sha512:" + "a" * 64)
    elif alteration == "selectors":
        command = command.replace(SELECTORS, "")
    elif alteration == "duplicate":
        command += " --expected-sha256 " + CONTROL_DIGEST
    else:
        command = command.replace(f'"{tmp_path / "proposal.toml"}"', "$proposal")
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == code
    assert native_answer == []


def test_controls_and_services_collect_every_scope_without_invented_effects(tmp_path, native_answer, monkeypatch):
    _mock_control_diff(monkeypatch, native_answer, _control_difference())
    command = f"gt services start {SELECTORS}; {_control_command(tmp_path)}; gt home open {SELECTORS}"
    assert gate.gate_decision(_payload(tmp_path, command)) == {}
    requests = _requests(native_answer)
    assert [request["operation"] for request in requests] == ["services.start-all", "controls.set", "home.open"]
    assert all(request["effects"] == [] for request in requests)


@pytest.mark.parametrize(
    "other,code",
    [
        ("Stop-Process -Id 123", "owner_operation_only"),
        ("gt backlog record WI-1 --project-id P2 --expected-version 3", "owner_lever_only"),
        ("Get-Content .env", "credential_material_protected"),
        ("Get-ChildItem . -Recurse", "context_traversal"),
    ],
)
def test_controls_scope_does_not_skip_existing_refusals(tmp_path, native_answer, other, code):
    assert gate.gate_decision(_payload(tmp_path, _control_command(tmp_path) + "; " + other))["reason_code"] == code
    assert native_answer == []


def test_controls_noop_requires_current_host_context_and_matching_selectors(tmp_path, native_answer):
    command = _control_command(
        tmp_path, selectors=SELECTORS.replace("--native-context-id ctx", "--native-context-id other")
    )
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == "invalid_native_context"
    assert native_answer == []


def test_controls_diff_failure_is_not_an_owner_approval_request(tmp_path, native_answer, monkeypatch):
    monkeypatch.setattr(
        gate.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=1,
            stdout="",
            stderr="Error: invalid_live_value: Invalid proposed value",
        ),
    )
    result = gate.gate_decision(_payload(tmp_path, _control_command(tmp_path)))
    assert result["decision"] == "block" and result["reason_code"] == "invalid_live_value"
    assert "owner_operation_only" not in result["reason"]


@pytest.mark.parametrize("custom", [False, True])
def test_dashboard_literal_cli_settings_do_not_create_a_second_settings_grant(tmp_path, native_answer, custom):
    config = tmp_path / "selected.toml"
    runtime = tmp_path / ("custom runtime" if custom else ".groundtruth/dashboard")
    db = runtime / ("custom.sqlite" if custom else "gtkb-dashboard.sqlite")
    grafana = tmp_path / ("custom grafana" if custom else ".groundtruth/tools/grafana")
    grafana_port, refresh_port, interval = (3300, 8866, 5) if custom else (8767, 8766, 60)
    prefix = f'gt --config "{config}"'
    start = (
        f'{prefix} dashboard start --db-path "{db}" --runtime-root "{runtime}" '
        f'--grafana-home "{grafana}" --grafana-port={grafana_port} --refresh-port {refresh_port} '
        f"--interval-minutes {interval} --json {SELECTORS}"
    )
    stop = f'{prefix} dashboard stop --runtime-root "{runtime}" --json {SELECTORS}'
    assert gate.gate_decision(_payload(tmp_path, start + "; " + stop)) == {}
    assert _requests(native_answer) == [
        {"operation": "dashboard.start", "targets": ["service:dashboard"], "effects": []},
        {"operation": "dashboard.stop", "targets": ["service:dashboard"], "effects": []},
    ]
    argv, _kwargs = native_answer[0]
    assert argv[argv.index("--config") + 1] == str(config)
    # A custom literal setting is inspectable here; the actual CLI separately
    # refuses unsupported settings before its controller performs any effect.


@pytest.mark.parametrize("verb", ["start", "stop", "serve", "install"])
def test_later_dashboard_command_still_requires_its_own_complete_selectors(tmp_path, native_answer, verb):
    command = f"gt services start {SELECTORS}; gt dashboard {verb}"
    result = gate.gate_decision(_payload(tmp_path, command))
    assert result["reason_code"] == "operation_selector_required"
    assert native_answer == []


@pytest.mark.parametrize(
    "command,code",
    [
        (f"gt dashboard start {SELECTORS} --db-path", "operation_selector_required"),
        (f"gt dashboard start {SELECTORS} --db-path $database", "operation_request_uninspectable"),
        (f"gt dashboard start {SELECTORS} --grafana-port 3000 --grafana-port 3300", "operation_request_uninspectable"),
        (f"gt dashboard start member {SELECTORS}", "operation_request_uninspectable"),
        (f"gt dashboard stop {SELECTORS} --db-path database.sqlite", "operation_request_uninspectable"),
        (f"gt dashboard stop {SELECTORS} --json --json", "operation_request_uninspectable"),
    ],
)
def test_dashboard_incomplete_dynamic_and_non_cli_options_refuse_before_native(tmp_path, native_answer, command, code):
    result = gate.gate_decision(_payload(tmp_path, command))
    assert result["reason_code"] == code
    assert native_answer == []


def test_dashboard_scope_keeps_actual_redirect_writes_in_file_check(tmp_path, native_answer):
    command = f"gt dashboard start --json {SELECTORS} > dashboard-start.txt; gt dashboard stop {SELECTORS}"
    payload = _payload(tmp_path, command)
    assert gate.changed_paths(payload) == (["dashboard-start.txt"], True)
    assert gate.gate_decision(payload) == {}
    argv, _kwargs = native_answer[0]
    assert argv[argv.index("--path") + 1] == "dashboard-start.txt"
    assert "--operations-json" not in argv and len(native_answer) == 2
    assert "--path" not in native_answer[1][0]
    assert [item["operation"] for item in _requests(native_answer)] == ["dashboard.start", "dashboard.stop"]


@pytest.mark.parametrize(
    "other,code",
    [
        ("Stop-Process -Id 123", "owner_operation_only"),
        ("gt backlog record WI-1 --project-id P2 --expected-version 3", "owner_lever_only"),
        ("Get-Content .env", "credential_material_protected"),
        ("Get-ChildItem . -Recurse", "context_traversal"),
    ],
)
@pytest.mark.parametrize("verb", ["start", "stop", "serve", "install"])
def test_dashboard_scope_keeps_mixed_command_guards(tmp_path, native_answer, other, code, verb):
    command = f"gt dashboard {verb} {SELECTORS}; {other}"
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == code
    assert native_answer == []


@pytest.mark.parametrize("controller", ["dashboard", "dashboard_install", "controls", "controls_noop"])
@pytest.mark.parametrize("explicit_config", [False, True])
@pytest.mark.parametrize("inherited_root", [False, True])
def test_operations_follow_actual_cwd_and_inherited_config_environment(
    tmp_path, native_answer, monkeypatch, controller, explicit_config, inherited_root
):
    root, cwd = tmp_path / "hook-root", tmp_path / "hook-root" / "nested"
    alternate = tmp_path / "another-installation" / "groundtruth.toml"
    configured_root = str(tmp_path / "inherited-installation")
    if inherited_root:
        monkeypatch.setenv("GT_PROJECT_ROOT", configured_root)
    else:
        monkeypatch.delenv("GT_PROJECT_ROOT", raising=False)
    monkeypatch.setenv("GT_AUTHORITY_URL", "http://selected-authority.invalid")
    monkeypatch.setenv("PYTHONIOENCODING", "cp1252")
    inherited = dict(gate.os.environ)
    selected = alternate if explicit_config else None
    if controller.startswith("controls"):
        _mock_control_diff(monkeypatch, native_answer, _control_difference(noop=controller == "controls_noop"))
        command = _control_command(cwd, config=selected)
    else:
        prefix = f'gt --config "{selected}"' if selected is not None else "gt"
        verb = "install" if controller == "dashboard_install" else "start"
        command = f"{prefix} dashboard {verb} {SELECTORS}"
    payload = _payload(root, command)
    payload["cwd"] = str(cwd)
    assert gate.gate_decision(payload) == {}
    assert len(native_answer) == (2 if controller == "controls" else 1)
    for argv, kwargs in native_answer:
        assert kwargs["cwd"] == cwd
        assert kwargs["env"] == {**inherited, "PYTHONIOENCODING": "utf-8"}
        if explicit_config:
            assert argv[argv.index("--config") + 1] == str(alternate)
        else:
            assert "--config" not in argv  # _find_config searches the actual nested cwd.
    if controller == "controls_noop":
        assert "diff" in native_answer[0][0] and "--operations-json" not in native_answer[0][0]


@pytest.mark.parametrize("verb", ["start", "install"])
def test_mixed_operations_keep_file_and_program_checks_in_the_original_environment(
    tmp_path, native_answer, monkeypatch, verb
):
    root, cwd = tmp_path / "hook-root", tmp_path / "hook-root" / "nested"
    selected = tmp_path / "another-installation" / "groundtruth.toml"
    monkeypatch.setenv("GT_PROJECT_ROOT", str(tmp_path / "inherited-installation"))
    inherited = dict(gate.os.environ)
    programs = []

    def check_program(native, observed_root, env, program):
        programs.append((native, observed_root, env, program))
        return {}

    monkeypatch.setattr(gate, "_native_program_check", check_program)
    command = f'gt --config "{selected}" dashboard {verb} {SELECTORS} > result.txt; python worker.py'
    payload = _payload(root, command)
    payload["cwd"] = str(cwd)
    assert gate.gate_decision(payload) == {}
    assert len(native_answer) == 2
    file_argv, file_kwargs = native_answer[0]
    assert "--operations-json" not in file_argv and "--config" not in file_argv
    assert file_argv[file_argv.index("--path") + 1] == "result.txt"
    assert file_argv[file_argv.index("--cwd") + 1] == str(cwd)
    assert file_kwargs["cwd"] == root
    assert file_kwargs["env"] == {**inherited, "GT_PROJECT_ROOT": str(root), "PYTHONIOENCODING": "utf-8"}
    operation_argv, operation_kwargs = native_answer[1]
    assert "--operations-json" in operation_argv and "--path" not in operation_argv
    assert operation_argv[operation_argv.index("--config") + 1] == str(selected)
    assert operation_kwargs["cwd"] == cwd
    assert operation_kwargs["env"] == {**inherited, "PYTHONIOENCODING": "utf-8"}
    assert len(programs) == 1 and programs[0][0] == "ctx" and programs[0][1] == root
    assert programs[0][2] == file_kwargs["env"]


def test_denied_mixed_file_check_does_not_reach_operation_scope(tmp_path, native_answer, monkeypatch):
    def refuse_file(argv, **kwargs):
        native_answer.append((argv, kwargs))
        assert "--path" in argv and "--operations-json" not in argv
        return SimpleNamespace(
            returncode=1, stdout="", stderr="Error: effect_scope_refused: File write is outside scope"
        )

    monkeypatch.setattr(gate.subprocess, "run", refuse_file)
    command = f"gt dashboard start {SELECTORS} > result.txt"
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == "effect_scope_refused"
    assert len(native_answer) == 1


@pytest.mark.parametrize("custom", [False, True])
def test_dashboard_serve_uses_exact_foreground_options_and_no_settings_grant(tmp_path, native_answer, custom):
    selected = tmp_path / "selected.toml"
    runtime = tmp_path / ("custom runtime" if custom else ".groundtruth/dashboard")
    db = runtime / ("custom.sqlite" if custom else "gtkb-dashboard.sqlite")
    port, grafana_port, interval = (8866, 3300, 5) if custom else (8766, 8767, 60)
    command = (
        f'gt --config "{selected}" dashboard serve --db-path "{db}" --runtime-root "{runtime}" '
        f"--port={port} --grafana-port {grafana_port} --interval-minutes {interval} {SELECTORS}"
    )
    assert gate.gate_decision(_payload(tmp_path, command)) == {}
    assert _requests(native_answer) == [
        {"operation": "dashboard.serve", "targets": ["service:dashboard"], "effects": []}
    ]
    argv, kwargs = native_answer[0]
    assert argv[argv.index("--config") + 1] == str(selected)
    assert kwargs["cwd"] == tmp_path and kwargs["env"].get("GT_PROJECT_ROOT") == gate.os.environ.get("GT_PROJECT_ROOT")
    # Settings are inspectable literals, not a second grant. The foreground CLI
    # refuses unsupported custom settings before any controller effect.


@pytest.mark.parametrize(
    "suffix,code",
    [
        ("--json", "operation_request_uninspectable"),
        ("--refresh-port 8766", "operation_request_uninspectable"),
        ("--grafana-home grafana", "operation_request_uninspectable"),
        ("--host 0.0.0.0", "operation_request_uninspectable"),
        ("--db-path", "operation_selector_required"),
        ("--runtime-root", "operation_selector_required"),
        ("--port", "operation_selector_required"),
        ("--grafana-port", "operation_selector_required"),
        ("--interval-minutes", "operation_selector_required"),
        ("--db-path $database", "operation_request_uninspectable"),
        ("--runtime-root $runtime", "operation_request_uninspectable"),
        ("--port $port", "operation_request_uninspectable"),
        ("--interval-minutes $interval", "operation_request_uninspectable"),
        ("--port 8766 --port 8866", "operation_request_uninspectable"),
        ("member", "operation_request_uninspectable"),
    ],
)
def test_dashboard_serve_unsupported_missing_or_dynamic_options_refuse_before_native(
    tmp_path, native_answer, suffix, code
):
    command = f"gt dashboard serve {SELECTORS} {suffix}"
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == code
    assert native_answer == []


@pytest.mark.parametrize("destination", ["standard", "custom", "relative"])
@pytest.mark.parametrize(
    "flags", ["", "--json", "--skip-download", "--skip-plugin", "--skip-download --skip-plugin --json"]
)
def test_dashboard_install_collects_only_scope_for_exact_literal_cli_options(
    tmp_path, native_answer, destination, flags
):
    selected = tmp_path / "selected.toml"
    home = {
        "standard": str(tmp_path / ".groundtruth/tools/grafana"),
        "custom": str(tmp_path / "custom grafana"),
        "relative": "custom-grafana",
    }[destination]
    command = f'gt --config "{selected}" dashboard install --grafana-home "{home}" {flags} {SELECTORS}'
    assert gate.gate_decision(_payload(tmp_path, command)) == {}
    assert _requests(native_answer) == [
        {"operation": "dashboard.install", "targets": ["service:dashboard"], "effects": []}
    ]
    argv, kwargs = native_answer[0]
    assert argv[argv.index("--config") + 1] == str(selected)
    assert kwargs["cwd"] == tmp_path
    assert all(flag not in argv for flag in ("--grafana-home", "--skip-download", "--skip-plugin"))
    # The CLI resolves the actual destination and refuses custom destinations or
    # skip flags before effects. The hook neither grants those settings nor names
    # the installer's transient staging paths.


@pytest.mark.parametrize(
    "suffix,code",
    [
        ("--grafana-home", "operation_selector_required"),
        ("--grafana-home $destination", "operation_request_uninspectable"),
        ("--grafana-home one --grafana-home two", "operation_request_uninspectable"),
        ("--skip-download --skip-download", "operation_request_uninspectable"),
        ("--skip-plugin=true", "operation_request_uninspectable"),
        ("--json --json", "operation_request_uninspectable"),
        ("--runtime-root runtime", "operation_request_uninspectable"),
        ("--db-path data.sqlite", "operation_request_uninspectable"),
        ("--port 8766", "operation_request_uninspectable"),
        ("--force", "operation_request_uninspectable"),
        ("member", "operation_request_uninspectable"),
    ],
)
def test_dashboard_install_missing_dynamic_or_non_cli_options_refuse_before_native(
    tmp_path, native_answer, suffix, code
):
    command = f"gt dashboard install {SELECTORS} {suffix}"
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == code
    assert native_answer == []


def test_dashboard_install_mixed_control_diff_preserves_prefixed_digest_and_selected_context(
    tmp_path, native_answer, monkeypatch
):
    selected = tmp_path / "selected.toml"
    _mock_control_diff(monkeypatch, native_answer, _control_difference())
    command = (
        _control_command(tmp_path, config=selected) + f'; gt --config "{selected}" dashboard install --json {SELECTORS}'
    )
    assert gate.gate_decision(_payload(tmp_path, command)) == {}
    assert _requests(native_answer) == [
        {"operation": "controls.set", "targets": ["control:left"], "effects": []},
        {"operation": "dashboard.install", "targets": ["service:dashboard"], "effects": []},
    ]
    assert len(native_answer) == 2
    for argv, kwargs in native_answer:
        assert argv[argv.index("--config") + 1] == str(selected) and kwargs["cwd"] == tmp_path
    mismatch = _control_command(tmp_path, config=selected).replace(CONTROL_DIGEST, "sha256:" + "b" * 64)
    prior = len(native_answer)
    command = mismatch + f'; gt --config "{selected}" dashboard install {SELECTORS}'
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == "generation_conflict"
    assert len(native_answer) == prior + 1 and "--operations-json" not in native_answer[-1][0]


@pytest.mark.parametrize(
    "replacement",
    [
        ("--native-context-id ctx", "--native-context-id other"),
        ("--document ops-chain", "--document another-chain"),
        ("--fence 7", "--fence 8"),
    ],
)
def test_dashboard_install_cannot_borrow_another_command_selectors(tmp_path, native_answer, replacement):
    command = f"gt services start {SELECTORS}; gt dashboard install {SELECTORS.replace(*replacement)}"
    assert gate.gate_decision(_payload(tmp_path, command))["reason_code"] == "operation_selector_mismatch"
    assert native_answer == []
