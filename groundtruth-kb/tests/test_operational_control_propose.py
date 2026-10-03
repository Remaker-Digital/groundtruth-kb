"""The GT-KB Home configuration edit path: propose one value as a complete artifact, preview it, apply it by digest."""

from __future__ import annotations

import json

import pytest
import tomlkit
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.project import operational_control_config as controls


def _control(ident, value):
    return {
        "id": ident,
        "description": "Explicit isolated fixture control.",
        "numeric_kind": "integer",
        "unit": "seconds",
        "value": value,
        "minimum": "1",
        "maximum": "120",
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
    }


def _pair_bytes(left="2", right="5"):
    document = tomlkit.document()
    document.add(tomlkit.comment("Owner-maintained comment that a proposal must keep."))
    document["schema_version"] = 2
    document["controls"] = [_control("left", left), _control("right", right)]
    document["invariants"] = [{"id": "pair", "left": "left", "operator": "lt", "right": "right", "margin": "0"}]
    return tomlkit.dumps(document).encode("utf-8")


def _project(tmp_path, payload=None):
    path = tmp_path / controls.CATALOG_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".git").mkdir(exist_ok=True)
    path.write_bytes(payload if payload is not None else _pair_bytes())
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")
    return path, config


def test_propose_changes_exactly_one_value_line_and_writes_nothing(tmp_path):
    path, _ = _project(tmp_path)
    original = path.read_bytes()
    proposed = controls.propose_operational_control_value(tmp_path, "left", "3")
    assert path.read_bytes() == original
    before, after = original.decode().splitlines(), proposed.decode().splitlines()
    assert len(before) == len(after)
    changed = [(old, new) for old, new in zip(before, after, strict=True) if old != new]
    assert changed == [('value = "2"', 'value = "3"')]
    assert "Owner-maintained comment" in proposed.decode()
    assert controls.validate_operational_control_bytes(proposed).definitions["left"].value == 3


@pytest.mark.parametrize(
    ("control_id", "value", "code"),
    [
        ("missing", "3", "unknown_control"),
        ("left", "500", "out_of_bounds"),
        ("left", "6", "invariant_violation"),
        ("left", "abc", "invalid_numeric"),
        ("left", "2.5", "invalid_numeric"),
    ],
)
def test_propose_refuses_what_validation_refuses(tmp_path, control_id, value, code):
    path, _ = _project(tmp_path)
    original = path.read_bytes()
    with pytest.raises(controls.OperationalControlConfigError, match=code):
        controls.propose_operational_control_value(tmp_path, control_id, value)
    assert path.read_bytes() == original


def test_cli_propose_previews_then_set_applies_the_previewed_file(tmp_path):
    path, config = _project(tmp_path)
    output = tmp_path / "proposal.toml"
    runner = CliRunner()
    shown = json.loads(runner.invoke(main, ["--config", str(config), "controls", "show"]).output)
    result = runner.invoke(
        main,
        ["--config", str(config), "controls", "propose", "--control", "left", "--value", "4", "--output", str(output)],
    )
    assert result.exit_code == 0, (result.output, result.exception)
    preview = json.loads(result.output)
    assert preview["proposal"] == str(output)
    assert preview["before_sha256"] == shown["catalog_sha256"]
    assert set(preview["controls"]) == {"left"}
    assert preview["controls"]["left"]["before"]["value"] == 2
    assert preview["controls"]["left"]["after"]["value"] == 4
    assert path.read_bytes() == _pair_bytes()
    applied = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "controls",
            "set",
            "--input",
            str(output),
            "--expected-sha256",
            preview["before_sha256"],
        ],
    )
    assert applied.exit_code == 0, (applied.output, applied.exception)
    assert json.loads(applied.output)["catalog_sha256"] == preview["after_sha256"]
    assert path.read_bytes() == output.read_bytes()


def test_cli_propose_refusal_writes_no_proposal(tmp_path):
    _, config = _project(tmp_path)
    output = tmp_path / "proposal.toml"
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "controls",
            "propose",
            "--control",
            "left",
            "--value",
            "500",
            "--output",
            str(output),
        ],
    )
    assert result.exit_code != 0
    assert "out_of_bounds" in result.output
    assert not output.exists()


def test_stale_preview_is_refused_by_digest(tmp_path):
    path, config = _project(tmp_path)
    output = tmp_path / "proposal.toml"
    runner = CliRunner()
    preview = json.loads(
        runner.invoke(
            main,
            [
                "--config",
                str(config),
                "controls",
                "propose",
                "--control",
                "left",
                "--value",
                "3",
                "--output",
                str(output),
            ],
        ).output
    )
    path.write_bytes(_pair_bytes(right="6"))
    stale = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "controls",
            "set",
            "--input",
            str(output),
            "--expected-sha256",
            preview["before_sha256"],
        ],
    )
    assert stale.exit_code != 0
    assert "generation_conflict" in stale.output
    assert path.read_bytes() == _pair_bytes(right="6")


def _bounded_native_answer(monkeypatch, root, config, *, verification_left=3):
    from datetime import UTC, datetime, timedelta
    from types import SimpleNamespace

    from groundtruth_kb import cli_authority

    requests = []

    def request(_method, _path, *, body):
        requests.append(body)
        operation = body["operations"][0]
        targets = ["control:left", "control:right"]
        bound = {
            "operation": "controls.set",
            "targets": targets,
            "preconditions": {
                "installation_root": str(root),
                "config_path": str(config),
                "controller_paths": {target: str(root / controls.CATALOG_RELATIVE_PATH) for target in targets},
                "states": {},
            },
            "permitted_effects": [
                {
                    "target": "control:left",
                    "effect": "control.set",
                    "value": requests[0]["operations"][0]["effects"][0]["value"],
                },
                {"target": "control:right", "effect": "control.set", "value": 5},
                *[{"target": target, "effect": "control.restore"} for target in targets],
            ],
            "expiry": "claim",
            "verification": {"control_values": {"left": verification_left, "right": 5}},
            "containment": {"installation_only": True, "managed_processes_only": True},
            "rollback": {"restore_initial_state": True, "only_invocation_changes": True},
        }
        now = datetime.now(UTC)
        return {
            "status": "current",
            "scope": "operation",
            "document": body["document"],
            "fence": body["fence"],
            "observed_at": now.isoformat(),
            "deadline": (now + timedelta(minutes=5)).isoformat(),
            "operations": [{**operation, "bound": bound, "formal_sources": [{"id": "SPEC-1", "version": 2}]}],
        }

    monkeypatch.setattr(cli_authority, "_client", lambda _ctx: SimpleNamespace(request=request))
    return requests


def _bounded_set(config, proposal, expected):
    return [
        "--config",
        str(config),
        "controls",
        "set",
        "--input",
        str(proposal),
        "--expected-sha256",
        expected,
        "--activity",
        "ops",
        "--native-context-id",
        "ctx",
        "--document",
        "ops-chain",
        "--fence",
        "7",
    ]


def test_bounded_cli_set_checks_actual_values_catalog_identity_and_readback(tmp_path, monkeypatch):
    path, config = _project(tmp_path)
    proposal = tmp_path / "proposal.toml"
    proposal.write_bytes(controls.propose_operational_control_value(tmp_path, "left", "3"))
    before = controls.load_operational_control_catalog(tmp_path)
    requests = _bounded_native_answer(monkeypatch, tmp_path, config)
    applied = CliRunner().invoke(main, _bounded_set(config, proposal, before.catalog_sha256))
    assert applied.exit_code == 0, (applied.output, applied.exception)
    assert path.read_bytes() == proposal.read_bytes() and len(requests) == 1
    body = requests[0]
    assert body["activity"] == "ops" and body["document"] == "ops-chain" and body["fence"] == 7
    assert body["installation_root"] == str(tmp_path) and body["config_path"] == str(config)
    assert body["observed_controller_paths"] == {"control:" + key: str(path) for key in ("left", "right")}
    assert body["operations"] == [
        {
            "operation": "controls.set",
            "targets": ["control:left"],
            "effects": [{"target": "control:left", "effect": "control.set", "value": 3}],
        }
    ]


def test_bounded_cli_cannot_claim_value_scope_for_metadata_changes(tmp_path, monkeypatch):
    path, config = _project(tmp_path)
    before = controls.load_operational_control_catalog(tmp_path)
    document = tomlkit.parse(controls.propose_operational_control_value(tmp_path, "left", "3").decode())
    document["controls"][0]["description"] = "Outside the value-only operation"
    proposal = tmp_path / "proposal.toml"
    proposal.write_bytes(tomlkit.dumps(document).encode())
    requests = _bounded_native_answer(monkeypatch, tmp_path, config)
    refused = CliRunner().invoke(main, _bounded_set(config, proposal, before.catalog_sha256))
    assert refused.exit_code != 0 and "operation_value_scope_required" in refused.output
    assert path.read_bytes() == _pair_bytes() and requests == []


def test_bounded_cli_refuses_boolean_readback_as_numeric_authority(tmp_path, monkeypatch):
    path, config = _project(tmp_path)
    before = controls.load_operational_control_catalog(tmp_path)
    proposal = tmp_path / "proposal.toml"
    proposal.write_bytes(controls.propose_operational_control_value(tmp_path, "left", "1"))
    _bounded_native_answer(monkeypatch, tmp_path, config, verification_left=True)
    refused = CliRunner().invoke(main, _bounded_set(config, proposal, before.catalog_sha256))
    assert refused.exit_code != 0 and "operation_bound_mismatch" in refused.output
    assert path.read_bytes() == _pair_bytes()


def test_bounded_cli_compensation_asks_native_for_actual_restore(tmp_path, monkeypatch):
    from groundtruth_kb import cli

    path, config = _project(tmp_path)
    before = controls.load_operational_control_catalog(tmp_path)
    proposal = tmp_path / "proposal.toml"
    proposal.write_bytes(controls.propose_operational_control_value(tmp_path, "left", "3"))
    requests = _bounded_native_answer(monkeypatch, tmp_path, config)
    original = cli._BoundedControlEffects.verify_result

    def fail_forward(self, catalog, phase):
        if phase == "forward":
            raise controls.OperationalControlConfigError("operation_verification_failed", "Controlled failure")
        original(self, catalog, phase)

    monkeypatch.setattr(cli._BoundedControlEffects, "verify_result", fail_forward)
    result = CliRunner().invoke(main, _bounded_set(config, proposal, before.catalog_sha256))
    assert result.exit_code != 0 and "operation_compensated" in result.output
    assert path.read_bytes() == _pair_bytes() and len(requests) == 2
    assert requests[1]["operations"][0]["effects"] == [{"target": "control:left", "effect": "control.restore"}]


def test_bounded_cli_refuses_deadline_expiry_during_bound_validation_before_catalog_write(tmp_path, monkeypatch):
    import time

    from groundtruth_kb import cli

    path, config = _project(tmp_path)
    original_bytes = path.read_bytes()
    before = controls.load_operational_control_catalog(tmp_path)
    proposal = tmp_path / "proposal.toml"
    proposal.write_bytes(controls.propose_operational_control_value(tmp_path, "left", "3"))
    requests = _bounded_native_answer(monkeypatch, tmp_path, config)
    clock = {"now": 100.0}
    monkeypatch.setattr(time, "monotonic", lambda: clock["now"])
    same_number = cli._BoundedControlEffects._same_number

    def finish_validation_after_deadline(left, right):
        result = same_number(left, right)
        # The native response grants five minutes; expire after its first deadline check,
        # while the otherwise-valid bound readback predicates are being inspected.
        clock["now"] = 400.0
        return result

    monkeypatch.setattr(cli._BoundedControlEffects, "_same_number", staticmethod(finish_validation_after_deadline))
    refused = CliRunner().invoke(main, _bounded_set(config, proposal, before.catalog_sha256))
    assert refused.exit_code != 0 and "operation_bound_mismatch" in refused.output
    assert "The existing operation deadline expired" in refused.output
    assert path.read_bytes() == original_bytes
    assert len(requests) == 1
    assert (requests[0]["document"], requests[0]["fence"]) == ("ops-chain", 7)


def test_control_callback_retains_discovered_config_outside_project_root(tmp_path, monkeypatch):
    import click

    from groundtruth_kb import cli
    from groundtruth_kb import config as config_module

    root = tmp_path / "project"
    selected = tmp_path / "configuration" / "groundtruth.toml"
    monkeypatch.setattr(config_module, "_find_config", lambda: selected)
    callback = cli._BoundedControlEffects(
        click.Context(click.Command("mock")),
        root,
        {"activity": "ops", "native_context_id": "pb-context", "document": "ops-chain", "fence": 7},
    )
    assert callback.config_path == str(selected.resolve())
    assert callback.root == root.resolve()
