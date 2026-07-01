from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

import groundtruth_kb.bridge_dispatch_reset as bridge_dispatch_reset  # noqa: E402
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


def _write_live_dispatch_run(
    root: Path,
    dispatch_id: str,
    *,
    pid: int = 999999,
    create_time_epoch: float = 1234.5,
) -> None:
    runs_dir = root / ".gtkb-state" / "bridge-poller" / "dispatch-runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    (runs_dir / f"{dispatch_id}.pid").write_text(str(pid), encoding="utf-8")
    (runs_dir / f"{dispatch_id}.create_time_epoch").write_text(f"{create_time_epoch:.6f}", encoding="utf-8")


def test_bridge_dispatch_health_cli_reports_selected_targets(tmp_path: Path) -> None:
    _root, config = _project(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["health_status"] == "PASS"
    assert [row["id"] for row in payload["selected_by_role"]["prime-builder"]] == ["A"]
    assert [row["id"] for row in payload["selected_by_role"]["loyal-opposition"]] == ["D"]


def test_bridge_dispatch_drain_dry_run_reports_live_dispatch_run_worker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _project(tmp_path)
    _write_live_dispatch_run(root, "2026-06-30T23-10-00Z-loyal-opposition-D-live")
    monkeypatch.setattr(bridge_dispatch_reset, "_dispatch_run_pid_alive", lambda pid: int(pid) == 999999)
    monkeypatch.setattr(
        bridge_dispatch_reset,
        "_dispatch_run_pid_provenance_matches",
        lambda pid, expected: int(pid) == 999999 and float(expected) == 1234.5,
    )

    result = CliRunner().invoke(
        main,
        ["--config", str(config), "bridge", "dispatch", "drain", "--dry-run", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["drained_pids"] == [999999]
    assert payload["terminated_pids"] == []


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
