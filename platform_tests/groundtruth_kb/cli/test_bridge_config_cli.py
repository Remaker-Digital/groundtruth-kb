from __future__ import annotations

import json
import sys
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
        'schema_version = 1\nselection_order = ["reviewer_precedence", "harness_id"]\nrules = []\n',
        encoding="utf-8",
    )
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "test",
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": ["prime-builder"],
                        "can_fire_events": True,
                        "can_receive_dispatch": True,
                        "event_driven_hooks": True,
                    },
                    {
                        "id": "D",
                        "harness_name": "ollama",
                        "harness_type": "ollama",
                        "status": "active",
                        "role": ["loyal-opposition"],
                        "can_fire_events": False,
                        "can_receive_dispatch": True,
                        "event_driven_hooks": True,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return root, config


def _write_dispatch_state(root: Path, state: dict[str, object]) -> None:
    path = root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(state), encoding="utf-8")


def test_bridge_dispatch_health_cli_reports_selected_targets(tmp_path: Path) -> None:
    _root, config = _project(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["health_status"] == "PASS"
    assert [row["id"] for row in payload["selected_by_role"]["prime-builder"]] == ["A"]
    assert [row["id"] for row in payload["selected_by_role"]["loyal-opposition"]] == ["D"]


def test_bridge_dispatch_status_cli_reports_health(tmp_path: Path) -> None:
    _root, config = _project(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "status"])

    assert result.exit_code == 0, result.output
    assert "Bridge dispatch health: PASS" in result.output
    assert "- prime-builder: A" in result.output


def test_direct_bridge_health_alias_matches_dispatch_health(tmp_path: Path) -> None:
    _root, config = _project(tmp_path)

    direct = CliRunner().invoke(main, ["--config", str(config), "bridge", "health", "--json"])
    nested = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])

    assert direct.exit_code == 0, direct.output
    assert nested.exit_code == 0, nested.output
    assert json.loads(direct.output) == json.loads(nested.output)


def test_bridge_dispatch_health_degrades_on_selected_runtime_failure(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_dispatch_state(
        root,
        {
            "schema_version": 1,
            "recipients": {
                "loyal-opposition:D": {
                    "circuit_breaker_tripped": True,
                    "failure_class": "max_turn_exhaustion",
                    "last_result": "provider_failure_backoff_active",
                    "pending_count": 3,
                    "selected_count": 1,
                },
                "prime-builder": {
                    "last_launch": {"reason": "work_intent_acquire_failed"},
                    "last_result": "work_intent_acquire_failed",
                    "pending_count": 2,
                    "selected_count": 1,
                },
            },
        },
    )

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])

    assert result.exit_code == 1, result.output
    payload = json.loads(result.output)
    assert payload["health_status"] == "FAIL"
    findings = "\n".join(payload["findings"])
    assert "loyal-opposition:D circuit breaker is tripped" in findings
    assert "loyal-opposition:D last_result=provider_failure_backoff_active" in findings
    assert "prime-builder last_result=work_intent_acquire_failed" in findings
    assert "prime-builder work intent acquisition failed" in findings


def test_bridge_dispatch_health_ignores_nonselected_runtime_failure(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_dispatch_state(
        root,
        {
            "schema_version": 1,
            "recipients": {
                "loyal-opposition:Z": {
                    "circuit_breaker_tripped": True,
                    "failure_class": "max_turn_exhaustion",
                    "last_result": "provider_failure_backoff_active",
                    "pending_count": 3,
                    "selected_count": 1,
                },
            },
        },
    )

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["health_status"] == "PASS"
    assert payload["findings"] == []
