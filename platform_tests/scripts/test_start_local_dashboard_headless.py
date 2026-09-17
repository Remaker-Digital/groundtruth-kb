"""Behavioral replacements for the retired PowerShell launcher's four assertions.

These tests capture process creation at the installed launch boundary. Real HTTP
readiness and process-tree cleanup are qualified in test_native_dashboard.py.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from groundtruth_kb import dashboard
from groundtruth_kb.cli import main


@pytest.fixture
def launch(tmp_path, monkeypatch):
    selected = tmp_path / "chosen.toml"
    selected.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:39899"\n', encoding="utf-8")
    home = tmp_path / "grafana"
    binary = home / "bin" / ("grafana.exe" if sys.platform == "win32" else "grafana")
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"Process creation is captured; this fixture is never executed")
    (home / "conf").mkdir()
    (home / "conf/defaults.ini").write_text("fixture", encoding="utf-8")
    calls, identities, health = [], {}, []

    def popen(args, **kwargs):
        pid = 910000 + len(calls)
        calls.append({"pid": pid, "args": args, "kwargs": kwargs, "log": kwargs["stdout"].name})
        identities[pid] = {"pid": pid, "created_at": f"fixture-{pid}", "executable": str(args[0])}
        return SimpleNamespace(pid=pid, poll=lambda: None, wait=lambda **kw: 0)

    monkeypatch.setattr(dashboard.subprocess, "Popen", popen)
    monkeypatch.setattr(dashboard, "_process_identity", lambda pid: identities.get(pid))
    monkeypatch.setattr(dashboard, "_wait_dashboard_http", lambda *args, **kwargs: health.append((args, kwargs)))
    monkeypatch.delenv("GTKB_DASHBOARD_HEADLESS", raising=False)
    with socket.socket() as first, socket.socket() as second:
        first.bind(("127.0.0.1", 0))
        second.bind(("127.0.0.1", 0))
        refresh_port, grafana_port = first.getsockname()[1], second.getsockname()[1]
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(selected),
            "dashboard",
            "start",
            "--grafana-home",
            str(home),
            "--refresh-port",
            str(refresh_port),
            "--grafana-port",
            str(grafana_port),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert len(calls) == 2 and len(health) == 2
    return SimpleNamespace(
        root=tmp_path,
        selected=selected,
        binary=binary,
        calls=calls,
        identities=identities,
        reply=json.loads(result.output),
        health=health,
    )


def test_launcher_needs_no_headless_switch_or_environment_setting(launch):
    assert launch.reply["refresh_pid"] == launch.calls[0]["pid"]
    assert launch.reply["grafana_pid"] == launch.calls[1]["pid"]
    assert launch.reply["grafana_url"].startswith("http://127.0.0.1:")
    assert launch.reply["refresh_url"].startswith("http://127.0.0.1:")


def test_launcher_suppresses_child_windows_and_redirects_logs(launch):
    for call in launch.calls:
        assert call["kwargs"]["creationflags"] == getattr(subprocess, "CREATE_NO_WINDOW", 0)
        assert call["kwargs"]["stderr"] == subprocess.STDOUT
        assert call["kwargs"].get("shell", False) is False
        assert call["kwargs"]["stdout"].closed
    assert launch.calls[0]["log"].endswith("refresh-service.log")
    assert launch.calls[1]["log"].endswith("grafana.log")


def test_launcher_uses_installed_service_and_exact_selected_grafana(launch):
    service, grafana = launch.calls
    assert service["args"][:3] == [sys.executable, "-m", "groundtruth_kb.dashboard_service"]
    assert service["args"][service["args"].index("--config") + 1] == str(launch.selected)
    assert service["kwargs"]["cwd"] == launch.root
    assert grafana["args"][0] == str(launch.binary)
    assert grafana["kwargs"]["env"]["GF_SERVER_HTTP_ADDR"] == "127.0.0.1"


def test_launcher_records_creation_identity_for_both_services(launch):
    pids = launch.root / ".groundtruth/dashboard/pids"
    for name, call in zip(("refresh-service", "grafana"), launch.calls, strict=True):
        record = json.loads((pids / f"{name}.pid").read_text(encoding="utf-8"))
        assert record == launch.identities[call["pid"]]
        assert set(record) == {"pid", "created_at", "executable"}
