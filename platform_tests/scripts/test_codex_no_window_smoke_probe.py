from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "codex_no_window_smoke_probe.py"


def _load_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("codex_no_window_smoke_probe", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_probe_writes_schema_v2_multi_command_marker_evidence(tmp_path: Path) -> None:
    module = _load_module()
    commands: list[list[str]] = []

    def fake_runner(command, **kwargs):
        commands.append(command)
        prompt = " ".join(str(part) for part in command)
        markers = [part for part in prompt.split() if part.startswith("GTKB-WI5135-")]
        return subprocess.CompletedProcess(command, 0, stdout="\n".join(markers), stderr="")

    payload = module.run_probe(
        project_root=tmp_path,
        codex_executable="codex",
        command_runner=fake_runner,
        window_observer=lambda: [{"visible_count": 0}],
    )

    assert payload["schema_version"] == 2
    assert payload["result"] == "pass"
    assert payload["visible_window_detected"] is False
    assert payload["run_count"] == 2
    assert payload["commands_per_run"] == 3
    assert len(payload["runs"]) == 2
    assert all(len(run["command_steps"]) == 3 for run in payload["runs"])
    assert all(step["stdout_contains_marker"] for run in payload["runs"] for step in run["command_steps"])
    assert len(commands) == 2

    path = module.write_payload(tmp_path, payload)
    assert path == tmp_path / ".gtkb-state" / "bridge-poller" / "codex-no-window-verification.json"
    assert path.is_file()


def test_run_probe_fails_when_marker_chain_is_missing(tmp_path: Path) -> None:
    module = _load_module()

    def fake_runner(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="no markers here", stderr="")

    payload = module.run_probe(
        project_root=tmp_path,
        codex_executable="codex",
        command_runner=fake_runner,
        window_observer=lambda: [{"visible_count": 0}],
    )

    assert payload["result"] == "fail"
    assert payload["marker_chain_ok"] is False
    assert payload["visible_window_detected"] is False


def test_run_probe_fails_when_visible_window_is_observed(tmp_path: Path) -> None:
    module = _load_module()

    def fake_runner(command, **kwargs):
        prompt = " ".join(str(part) for part in command)
        markers = [part for part in prompt.split() if part.startswith("GTKB-WI5135-")]
        return subprocess.CompletedProcess(command, 0, stdout="\n".join(markers), stderr="")

    payload = module.run_probe(
        project_root=tmp_path,
        codex_executable="codex",
        command_runner=fake_runner,
        window_observer=lambda: [{"visible_count": 1, "processes": [{"ProcessName": "pwsh"}]}],
    )

    assert payload["result"] == "fail"
    assert payload["marker_chain_ok"] is True
    assert payload["visible_window_detected"] is True
