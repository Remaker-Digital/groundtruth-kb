from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

import groundtruth_kb.bridge_dispatch_config as bridge_dispatch_config  # noqa: E402
import groundtruth_kb.bridge_dispatch_reset as bridge_dispatch_reset  # noqa: E402
from groundtruth_kb.cli import main  # noqa: E402


@pytest.fixture(autouse=True)
def _no_dispatcher_runtime_disable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)


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


def _write_recent_run(root: Path, dispatch_id: str, *, exit_code: int, stderr: str = "") -> None:
    runs_dir = root / ".gtkb-state" / "bridge-poller" / "dispatch-runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    (runs_dir / f"{dispatch_id}.exit_code").write_text(str(exit_code), encoding="utf-8")
    (runs_dir / f"{dispatch_id}.stderr.log").write_text(stderr, encoding="utf-8")


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


def test_bridge_dispatch_daemon_stop_reaps_workers_before_daemon_tree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _project(tmp_path)
    state_dir = root / ".gtkb-state" / "dispatcher-daemon"
    state_dir.mkdir(parents=True, exist_ok=True)
    pid = 4242
    (state_dir / "daemon.pid").write_text(f"{pid}\n", encoding="utf-8")
    (state_dir / "daemon.lock").write_text(json.dumps({"pid": pid}), encoding="utf-8")
    events: list[str] = []

    class _FakeDaemon:
        PID_FILENAME = "daemon.pid"
        PID_CREATE_TIME_FILENAME = "daemon.create_time_epoch"
        LOCK_FILENAME = "daemon.lock"

        @staticmethod
        def daemon_state_dir(_project_root: Path) -> Path:
            return state_dir

        @staticmethod
        def daemon_pid_provenance_verified(_state_dir: Path) -> bool:
            return True

        @staticmethod
        def daemon_pid_matches_legacy_loop(_state_dir: Path, _pid: int) -> bool:
            return False

        @staticmethod
        def matching_daemon_loop_pids(_state_dir: Path) -> list[int]:
            return []

        @staticmethod
        def _reap_dispatched_workers(_project_root: Path) -> int:
            events.append("reap")
            return 2

        @staticmethod
        def _read_pid_create_time_sidecar(_state_dir: Path) -> None:
            return None

        @staticmethod
        def _clear_daemon_pid_record(_state_dir: Path) -> None:
            for name in ("daemon.pid", "daemon.create_time_epoch"):
                try:
                    (_state_dir / name).unlink()
                except FileNotFoundError:
                    pass

        @staticmethod
        def release_daemon_lock(_state_dir: Path, *, force: bool = False) -> None:
            assert force is True
            try:
                (_state_dir / "daemon.lock").unlink()
            except FileNotFoundError:
                pass

    import groundtruth_kb.bridge_dispatch_reset as bridge_dispatch_reset
    import groundtruth_kb.cli as gtcli

    monkeypatch.setattr(gtcli, "_import_dispatcher_daemon_module", lambda _project_root: _FakeDaemon)
    monkeypatch.setattr(bridge_dispatch_reset, "terminate_pid_tree", lambda _pid: events.append("terminate"))

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "daemon", "stop"])

    assert result.exit_code == 0, result.output
    assert events == ["reap", "terminate"]
    assert "tree terminated" in result.output
    assert "reaped dispatched workers=2" in result.output
    assert not (state_dir / "daemon.pid").exists()
    assert not (state_dir / "daemon.lock").exists()


def test_bridge_dispatch_health_cli_ignores_retired_worker_disable_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _root, config = _project(tmp_path)
    retired_env = "GTKB_NO_" + "CROSS_" + "HARN" + "ESS_TRIGGER"
    monkeypatch.setenv(retired_env, "1")

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["health_status"] == "PASS"
    findings = "\n".join(payload["findings"])
    assert retired_env not in findings


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

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["health_status"] == "WARN"
    findings = "\n".join(payload["findings"])
    assert "loyal-opposition:D circuit breaker is tripped" in findings
    assert "loyal-opposition:D failure_class=max_turn_exhaustion" in findings
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


def test_bridge_dispatch_health_warns_for_stale_selected_launch_failure(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    dispatch_id = "2026-06-21T15-00-00Z-prime-builder-A-stale"
    _write_dispatch_state(
        root,
        {
            "schema_version": 1,
            "recipients": {
                "prime-builder:A": {
                    "last_result": "launch_failed",
                    "last_launch": {
                        "dispatch_id": dispatch_id,
                        "launched": True,
                        "pid": 999999,
                        "recipient": "prime-builder:A",
                    },
                    "pending_count": 2,
                    "selected_count": 1,
                },
            },
        },
    )

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["health_status"] == "WARN"
    findings = "\n".join(payload["findings"])
    assert "stale failure evidence ignored" in findings
    assert f"recorded dispatch {dispatch_id} has no live worker" in findings
    assert "dispatch runtime failure" not in findings

    status = bridge_dispatch_config.collect_bridge_dispatch_status(root)
    classification = status.runtime_classifications[0]
    assert classification["recipient"] == "prime-builder:A"
    assert classification["severity"] == "WARN"
    assert classification["stale_failure_evidence"] is True
    assert f"recorded dispatch {dispatch_id} has no live worker" == classification["stale_failure_reason"]


def test_bridge_dispatch_health_classifies_recent_ollama_timeout(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    dispatch_id = "2026-06-30T10-20-39Z-loyal-opposition-D-timeout"
    _write_recent_run(
        root,
        dispatch_id,
        exit_code=1,
        stderr="ollama_harness: session timeout exceeded before Ollama chat turn\n",
    )

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["health_status"] == "WARN"
    findings = "\n".join(payload["findings"])
    assert f"latest_run={dispatch_id}" in findings
    assert "failure_class=worker_timeout" in findings
    status = bridge_dispatch_config.collect_bridge_dispatch_status(root)
    classification = status.runtime_classifications[-1]
    assert classification["failure_class"] == "worker_timeout"


def test_bridge_dispatch_health_classifies_recent_abrupt_termination(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    dispatch_id = "2026-06-30T10-58-53Z-loyal-opposition-D-abrupt"
    _write_recent_run(root, dispatch_id, exit_code=4294967295)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "health", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    findings = "\n".join(payload["findings"])
    assert f"latest_run={dispatch_id}" in findings
    assert "failure_class=process_terminated_abruptly" in findings
    status = bridge_dispatch_config.collect_bridge_dispatch_status(root)
    classification = status.runtime_classifications[-1]
    assert classification["failure_class"] == "process_terminated_abruptly"
