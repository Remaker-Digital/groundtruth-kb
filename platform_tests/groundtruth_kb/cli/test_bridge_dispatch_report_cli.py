from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import psutil
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))
for module_name in list(sys.modules):
    if module_name == "groundtruth_kb" or module_name.startswith("groundtruth_kb."):
        del sys.modules[module_name]

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
selection_order = ["reviewer_precedence", "harness_id"]

[harnesses.A]
max_items = 3

[harnesses.D]
max_items = 2

rules = []
""".lstrip(),
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
                        "reviewer_precedence": 20,
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
                        "reviewer_precedence": 10,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return root, config


def _write_runtime(root: Path) -> None:
    state_dir = root / ".gtkb-state" / "bridge-poller"
    runs_dir = state_dir / "dispatch-runs"
    runs_dir.mkdir(parents=True)
    (state_dir / "dispatch-state.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "updated_at": "2026-06-23T10:00:00Z",
                "recipients": {
                    "loyal-opposition:D": {
                        "pending_count": 3,
                        "raw_pending_count": 4,
                        "selected_count": 1,
                        "last_result": "launch_failed",
                        "failure_class": "provider_failure",
                        "last_launch": {
                            "reason": "concurrency_cap_reached",
                            "exit_failure_reason": "no_verdict_produced",
                            "live_count": 2,
                            "cap": 2,
                        },
                        "circuit_breaker_tripped": True,
                    },
                    "prime-builder:A": {
                        "pending_count": 1,
                        "selected_count": 1,
                        "last_result": "launched",
                        "last_launch": {"reason": "started"},
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "dispatch-failures.jsonl").write_text(
        json.dumps({"reason": "provider_failure", "failure_class": "provider_failure"}) + "\n",
        encoding="utf-8",
    )
    (state_dir / "dispatch-suppressions.jsonl").write_text(
        json.dumps({"reason": "work_intent_already_held"}) + "\n",
        encoding="utf-8",
    )
    (state_dir / "trigger-diagnostic.jsonl").write_text(json.dumps({"event": "tick"}) + "\n", encoding="utf-8")
    (state_dir / "starvation-telemetry.json").write_text(json.dumps({"starved_roles": []}), encoding="utf-8")
    (runs_dir / "2026-06-23T09-59-00Z-loyal-opposition-D-demo.stdout.log").write_text("", encoding="utf-8")
    (runs_dir / "2026-06-23T09-59-00Z-loyal-opposition-D-demo.stderr.log").write_text("", encoding="utf-8")
    (runs_dir / "2026-06-23T09-59-00Z-loyal-opposition-D-demo.exit_code").write_text("1", encoding="utf-8")
    live_id = "2026-06-23T10-00-00Z-prime-builder-A-live"
    (runs_dir / f"{live_id}.stdout.log").write_text("", encoding="utf-8")
    (runs_dir / f"{live_id}.pid").write_text(str(os.getpid()), encoding="utf-8")
    create_time = float(psutil.Process(os.getpid()).create_time())
    (runs_dir / f"{live_id}.create_time_epoch").write_text(f"{create_time:.6f}", encoding="utf-8")


def test_bridge_dispatch_report_json_exposes_required_sections_and_cause_taxonomy(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_runtime(root)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert set(payload) == {
        "configuration",
        "history",
        "live_state",
        "performance",
        "reliability",
        "summary",
        "topology",
    }
    assert "consistency_findings" in payload["reliability"]
    assert "runtime_classifications" in payload["reliability"]
    assert payload["topology"]["effective_per_cycle_ceiling"] == {
        "loyal-opposition": 2,
        "prime-builder": 3,
    }
    taxonomy = payload["reliability"]["failure_taxonomy"]
    assert taxonomy["last_result"]["launch_failed"] == 1
    assert taxonomy["failure_class"]["provider_failure"] == 2
    assert taxonomy["last_launch.reason"]["concurrency_cap_reached"] == 1
    assert taxonomy["last_launch.exit_failure_reason"]["no_verdict_produced"] == 1
    assert taxonomy["suppression.reason"]["work_intent_already_held"] == 1
    assert payload["live_state"]["live_worker_count"] == 1
    assert payload["history"]["recent_runs"][0]["state"] == "live"


def test_bridge_dispatch_report_is_read_only_for_config_registry_and_runtime(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_runtime(root)
    tracked = [
        root / "config" / "dispatcher" / "rules.toml",
        root / "harness-state" / "harness-registry.json",
        root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json",
        root / ".gtkb-state" / "bridge-poller" / "dispatch-failures.jsonl",
        root / ".gtkb-state" / "bridge-poller" / "dispatch-suppressions.jsonl",
    ]
    before = {path: path.read_bytes() for path in tracked}

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--json"])

    assert result.exit_code == 0, result.output
    assert {path: path.read_bytes() for path in tracked} == before


def test_bridge_dispatch_report_human_output_is_compact(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _write_runtime(root)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report"])

    assert result.exit_code == 0, result.output
    assert "Bridge dispatch report:" in result.output
    assert "Selected candidates:" in result.output
    assert "Recent runs:" in result.output


def test_bridge_dispatch_report_does_not_count_stdout_stderr_only_sidecars_as_live(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    runs_dir = root / ".gtkb-state" / "bridge-poller" / "dispatch-runs"
    runs_dir.mkdir(parents=True)
    (runs_dir / "2026-06-23T10-01-00Z-loyal-opposition-D-ghost.stdout.log").write_text("", encoding="utf-8")
    (runs_dir / "2026-06-23T10-01-00Z-loyal-opposition-D-ghost.stderr.log").write_text("", encoding="utf-8")

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "report", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["live_state"]["live_worker_count"] == 0
    assert payload["history"]["recent_runs"][0]["state"] == "stale"
