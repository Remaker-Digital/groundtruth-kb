from __future__ import annotations

import importlib.util
import re
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


def test_run_probe_writes_schema_v3_workspace_sentinel_evidence(tmp_path: Path) -> None:
    module = _load_module()
    commands: list[list[str]] = []

    def fake_runner(command, **kwargs):
        commands.append(command)
        prompt = " ".join(str(part) for part in command)
        markers = re.findall(r"GTKB-WI5135-[A-Za-z0-9-]+", prompt)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="\n".join(marker for marker in dict.fromkeys(markers) for _ in range(2)),
            stderr="sandbox: workspace-write [workdir, test]\n",
        )

    payload = module.run_probe(
        project_root=tmp_path,
        codex_executable="codex",
        command_runner=fake_runner,
        window_observer=lambda: [{"visible_count": 0}],
    )

    assert payload["schema_version"] == 3
    assert payload["result"] == "pass"
    assert payload["visible_window_detected"] is False
    assert payload["run_count"] == 2
    assert payload["commands_per_run"] == 3
    assert len(payload["runs"]) == 2
    assert all(len(run["command_steps"]) == 3 for run in payload["runs"])
    assert all(step["stdout_contains_marker"] for run in payload["runs"] for step in run["command_steps"])
    assert len(commands) == 2
    assert all('default_permissions=":workspace"' in command for command in commands)
    assert all("--sandbox" not in command for command in commands)
    assert payload["effective_profile_ok"] is True
    assert payload["sentinel_lifecycle_ok"] is True

    path = module.write_payload(tmp_path, payload)
    # Canon s17: probe evidence is session-scoped scratch, never `.gtkb-state`
    # (and never the retired bridge-poller tree). Resolved via the same single
    # authority the probe uses, so test and implementation cannot drift apart.
    from scripts.gtkb_session_id import session_scratch_dirname

    assert path == tmp_path / "scratchpad" / session_scratch_dirname() / "codex-no-window-verification.json"
    assert ".gtkb-state" not in path.parts
    assert path.is_file()


def test_run_probe_fails_when_marker_chain_is_missing(tmp_path: Path) -> None:
    module = _load_module()

    def fake_runner(command, **kwargs):
        return subprocess.CompletedProcess(
            command, 0, stdout="no markers here", stderr="sandbox: workspace-write [workdir, test]\n"
        )

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
        markers = re.findall(r"GTKB-WI5135-[A-Za-z0-9-]+", prompt)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="\n".join(marker for marker in dict.fromkeys(markers) for _ in range(2)),
            stderr="sandbox: workspace-write [workdir, test]\n",
        )

    payload = module.run_probe(
        project_root=tmp_path,
        codex_executable="codex",
        command_runner=fake_runner,
        window_observer=lambda: [{"visible_count": 1, "processes": [{"ProcessName": "pwsh"}]}],
    )

    assert payload["result"] == "fail"
    assert payload["marker_chain_ok"] is True
    assert payload["visible_window_detected"] is True


def test_run_probe_fails_on_read_only_effective_profile(tmp_path: Path) -> None:
    module = _load_module()

    def fake_runner(command, **kwargs):
        markers = re.findall(r"GTKB-WI5135-[A-Za-z0-9-]+", " ".join(command))
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="\n".join(marker for marker in dict.fromkeys(markers) for _ in range(2)),
            stderr="sandbox: read-only [workdir]\n",
        )

    payload = module.run_probe(
        project_root=tmp_path,
        codex_executable="codex",
        command_runner=fake_runner,
        window_observer=lambda: [{"visible_count": 0}],
    )

    assert payload["result"] == "fail"
    assert payload["effective_profile_ok"] is False


def test_run_probe_fails_and_cleans_residual_sentinel(tmp_path: Path) -> None:
    module = _load_module()

    def fake_runner(command, **kwargs):
        prompt = " ".join(command)
        markers = re.findall(r"GTKB-WI5135-[A-Za-z0-9-]+", prompt)
        sentinel = Path(prompt.split("p=Path(r'")[1].split("')")[0].replace("\\\\", "\\"))
        sentinel.write_text("residual", encoding="utf-8")
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="\n".join(marker for marker in dict.fromkeys(markers) for _ in range(2)),
            stderr="sandbox: workspace-write [workdir, test]\n",
        )

    payload = module.run_probe(
        project_root=tmp_path,
        codex_executable="codex",
        command_runner=fake_runner,
        window_observer=lambda: [{"visible_count": 0}],
    )

    assert payload["result"] == "fail"
    assert payload["sentinel_lifecycle_ok"] is False
    assert all(run["sentinel_residual_before_cleanup"] for run in payload["runs"])
    assert all(run["sentinel_residual_after_cleanup"] is False for run in payload["runs"])
