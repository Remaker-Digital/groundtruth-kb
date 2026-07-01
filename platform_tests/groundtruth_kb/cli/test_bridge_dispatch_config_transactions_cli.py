from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402


def _project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n', encoding="utf-8")
    (root / "config" / "dispatcher").mkdir(parents=True)
    (root / "config" / "dispatcher" / "rules.toml").write_text(
        """
schema_version = 1
selection_order = ["quality", "cost", "availability", "harness_id"]
owner_note = "preserve-me"

[harnesses.A]
description = "Codex"
can_receive_dispatch = true
can_fire_events = true
dispatch_cost = 60
dispatch_quality = 90
dispatch_availability = 90
tags = ["prime-builder"]

[harnesses.D]
description = "LO"
can_receive_dispatch = true
can_fire_events = false
dispatch_cost = 30
dispatch_quality = 80
dispatch_availability = 95
max_items = 2
tags = ["loyal-opposition"]

[[rules]]
id = "bridge-prime-builder-default"
required_roles = ["prime-builder"]
statuses = ["GO", "NO-GO"]
prefer = ["quality", "cost", "availability", "harness_id"]

[[rules]]
id = "bridge-loyal-opposition-default"
required_roles = ["loyal-opposition"]
statuses = ["NEW", "REVISED"]
prefer = ["quality", "cost", "availability", "harness_id"]
""".lstrip(),
        encoding="utf-8",
    )
    return root, config


def _invoke(config: Path, *args: str) -> object:
    return CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "config", *args])


def _rules(root: Path) -> dict:
    return tomllib.loads((root / "config" / "dispatcher" / "rules.toml").read_text(encoding="utf-8"))


def _audit_records(root: Path) -> list[dict]:
    path = root / ".gtkb-state" / "bridge-dispatch-config-transactions" / "audit.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_config_read_command_still_reports_and_subcommands_are_discoverable(tmp_path: Path) -> None:
    _, config = _project(tmp_path)

    read = _invoke(config)
    help_result = _invoke(config, "--help")

    assert read.exit_code == 0, read.output
    assert "Bridge dispatch config:" in read.output
    assert help_result.exit_code == 0, help_result.output
    for command in ("set-eligibility", "set-weights", "set-caps", "set-rule", "add-harness", "remove-harness"):
        assert command in help_result.output


def test_transaction_commands_update_known_schema_and_append_audit(tmp_path: Path) -> None:
    root, config = _project(tmp_path)

    commands = [
        (
            "set-eligibility",
            "A",
            "--no-can-receive-dispatch",
            "--can-fire-events",
        ),
        ("set-weights", "A", "--quality", "91", "--cost", "55", "--availability", "88"),
        ("set-caps", "A", "--max-items", "4"),
        (
            "set-rule",
            "bridge-loyal-opposition-default",
            "--status",
            "NEW",
            "--status",
            "REVISED",
            "--prefer",
            "cost",
            "--prefer",
            "availability",
            "--prefer",
            "harness_id",
        ),
        (
            "add-harness",
            "F",
            "--description",
            "OpenRouter",
            "--can-receive-dispatch",
            "--no-can-fire-events",
            "--quality",
            "80",
            "--cost",
            "20",
            "--availability",
            "90",
            "--tag",
            "loyal-opposition",
        ),
        ("remove-harness", "D"),
    ]

    for command in commands:
        result = _invoke(config, *command, "--json")
        assert result.exit_code == 0, result.output
        assert json.loads(result.output)["status"] == "applied"

    payload = _rules(root)
    assert payload["owner_note"] == "preserve-me"
    assert payload["harnesses"]["A"]["can_receive_dispatch"] is False
    assert payload["harnesses"]["A"]["can_fire_events"] is True
    assert payload["harnesses"]["A"]["dispatch_quality"] == 91
    assert payload["harnesses"]["A"]["dispatch_cost"] == 55
    assert payload["harnesses"]["A"]["dispatch_availability"] == 88
    assert payload["harnesses"]["A"]["max_items"] == 4
    assert "D" not in payload["harnesses"]
    assert payload["harnesses"]["F"]["dispatch_cost"] == 20
    lo_rule = next(rule for rule in payload["rules"] if rule["id"] == "bridge-loyal-opposition-default")
    assert lo_rule["prefer"] == ["cost", "availability", "harness_id"]
    assert [row["transaction"] for row in _audit_records(root)] == [
        "set-eligibility",
        "set-weights",
        "set-caps",
        "set-rule",
        "add-harness",
        "remove-harness",
    ]


def test_dry_run_reports_without_writing_config_or_audit(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    rules_path = root / "config" / "dispatcher" / "rules.toml"
    before = rules_path.read_bytes()

    result = _invoke(config, "set-weights", "A", "--quality", "77", "--dry-run", "--json")

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "dry_run"
    assert rules_path.read_bytes() == before
    assert not (root / ".gtkb-state" / "bridge-dispatch-config-transactions" / "audit.jsonl").exists()


def test_defer_records_pending_transaction_without_changing_config(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    rules_path = root / "config" / "dispatcher" / "rules.toml"
    before = rules_path.read_bytes()

    result = _invoke(config, "set-caps", "D", "--max-items", "3", "--defer-to-next-session", "--json")

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "deferred"
    assert rules_path.read_bytes() == before
    pending_path = root / ".gtkb-state" / "bridge-dispatch-config-transactions" / "pending.jsonl"
    assert json.loads(pending_path.read_text(encoding="utf-8").splitlines()[0])["transaction"] == "set-caps"
    assert _audit_records(root)[0]["status"] == "deferred"


def test_invalid_transactions_fail_closed_without_writing(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    rules_path = root / "config" / "dispatcher" / "rules.toml"
    before = rules_path.read_bytes()

    result = _invoke(config, "set-rule", "missing-rule", "--status", "NEW")

    assert result.exit_code != 0
    assert "does not exist" in result.output
    assert rules_path.read_bytes() == before
    assert not (root / ".gtkb-state" / "bridge-dispatch-config-transactions" / "audit.jsonl").exists()
