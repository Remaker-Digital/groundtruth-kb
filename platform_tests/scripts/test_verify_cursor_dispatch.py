from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts import cursor_harness
from scripts.verify_cursor_dispatch import evaluate_readiness


def _write_registry(root: Path, record: dict) -> None:
    state = root / "harness-state"
    state.mkdir()
    (state / "harness-registry.json").write_text(
        json.dumps({"harnesses": [record], "schema_version": 1}),
        encoding="utf-8",
    )


def _cursor_record(**overrides):
    record = {
        "can_receive_dispatch": False,
        "harness_name": "cursor",
        "harness_type": "cursor",
        "id": "E",
        "invocation_surfaces": {
            "headless": {
                "argv": [
                    "groundtruth-kb/.venv/Scripts/python.exe",
                    "scripts/cursor_harness.py",
                    "-p",
                    "{{PROMPT}}",
                    "--skill",
                    "bridge-review",
                ],
            }
        },
        "role": ["prime-builder"],
        "status": "active",
    }
    record.update(overrides)
    return record


def _write_cursor_shim(root: Path) -> None:
    scripts = root / "scripts"
    scripts.mkdir(exist_ok=True)
    (scripts / "cursor_harness.py").write_text("# fixture shim\n", encoding="utf-8")


@pytest.fixture(autouse=True)
def clear_registry_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)


def test_readiness_fails_closed_when_agent_cli_missing(tmp_path: Path) -> None:
    _write_registry(tmp_path, _cursor_record())
    _write_cursor_shim(tmp_path)

    def missing_agent() -> list[str]:
        raise cursor_harness.CursorHarnessError("Cursor Agent CLI not found")

    result = evaluate_readiness(project_root=tmp_path, agent_resolver=missing_agent)

    assert result["ready"] is False
    assert result["dispatchable_now"] is False
    assert result["first_failed_check"].startswith("headless Cursor Agent CLI")


def test_readiness_can_be_ready_without_current_dispatch_enablement(tmp_path: Path) -> None:
    _write_registry(tmp_path, _cursor_record())
    _write_cursor_shim(tmp_path)

    result = evaluate_readiness(project_root=tmp_path, agent_resolver=lambda: ["C:/Tools/cursor-agent.exe"])

    assert result["ready"] is True
    assert result["dispatchable_now"] is False
    assert result["can_receive_dispatch"] is False
    assert result["role"] == ["prime-builder"]


def test_readiness_reports_dispatchable_when_registry_is_lo_enabled(tmp_path: Path) -> None:
    _write_registry(
        tmp_path,
        _cursor_record(
            can_receive_dispatch=True,
            role=["loyal-opposition"],
        ),
    )
    _write_cursor_shim(tmp_path)

    result = evaluate_readiness(project_root=tmp_path, agent_resolver=lambda: ["C:/Tools/cursor-agent.exe"])

    assert result["ready"] is True
    assert result["dispatchable_now"] is True


def test_live_probe_requires_non_empty_output(tmp_path: Path) -> None:
    _write_registry(tmp_path, _cursor_record(can_receive_dispatch=True, role=["loyal-opposition"]))
    _write_cursor_shim(tmp_path)

    def blank_runner(command, **kwargs):
        assert kwargs["stdin"] == subprocess.DEVNULL
        assert kwargs["capture_output"] is True
        return subprocess.CompletedProcess(command, 0, stdout=" \n", stderr="")

    result = evaluate_readiness(
        project_root=tmp_path,
        agent_resolver=lambda: ["C:/Tools/cursor-agent.exe"],
        require_live=True,
        live_runner=blank_runner,
    )

    assert result["ready"] is False
    assert result["dispatchable_now"] is False
    assert result["live_probe"]["stdout_bytes"] == 2
    assert result["first_failed_check"].startswith("live bridge-review probe")
