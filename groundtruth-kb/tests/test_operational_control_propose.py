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
