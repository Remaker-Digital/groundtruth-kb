"""Regression tests for the tracked cross-harness storm watchdog."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WATCHDOG_PATH = PROJECT_ROOT / "scripts" / "ops" / "harness_storm_watchdog.ps1"
REGISTRY_PATH = PROJECT_ROOT / "harness-state" / "harness-registry.json"


def _watchdog_text() -> str:
    return WATCHDOG_PATH.read_text(encoding="utf-8")


def test_watchdog_lands_on_tracked_path() -> None:
    assert WATCHDOG_PATH.exists()
    assert WATCHDOG_PATH.relative_to(PROJECT_ROOT).as_posix() == "scripts/ops/harness_storm_watchdog.ps1"

    ignored = subprocess.run(
        ["git", "check-ignore", "--quiet", WATCHDOG_PATH.relative_to(PROJECT_ROOT).as_posix()],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert ignored.returncode == 1, ignored.stderr


def test_watchdog_detects_ollama_and_openrouter_backends() -> None:
    text = _watchdog_text()

    assert "Get-CimInstance Win32_Process" in text
    assert "ollama_harness.py" in text
    assert "openrouter_harness.py" in text
    assert "$NONCODEX_HARNESS_SCRIPT_PATTERN" in text
    assert "$GTKB_VENV_PYTHON_PATTERN" in text


def test_watchdog_has_noncodex_threshold_trip() -> None:
    text = _watchdog_text()

    assert "$NONCODEX_THRESHOLD = 15" in text
    assert "$noncodexCount -gt $NONCODEX_THRESHOLD" in text
    assert "GTKB_NO_CROSS_HARNESS_TRIGGER" in text
    assert "noncodexThreshold=$NONCODEX_THRESHOLD" in text


def test_watchdog_covers_registry_lowcost_backends() -> None:
    text = _watchdog_text()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    expected_scripts: set[str] = set()
    for harness in registry["harnesses"]:
        surfaces = harness.get("invocation_surfaces", {})
        for surface in surfaces.values():
            argv = surface.get("argv", [])
            if not any(str(part).lower().endswith(("python.exe", "python")) for part in argv):
                continue
            for part in argv:
                path = Path(str(part).replace("\\", "/"))
                if path.name.endswith("_harness.py"):
                    expected_scripts.add(path.name)

    assert expected_scripts == {"ollama_harness.py", "openrouter_harness.py"}
    for script_name in expected_scripts:
        assert script_name in text


def test_watchdog_never_kills_claude() -> None:
    text = _watchdog_text()
    active_script = "\n".join(line for line in text.splitlines() if not line.strip().startswith("#"))

    assert "claude" not in active_script.lower()
    assert "OpenAI\\\\Codex" in text
    assert "Stop-Process -Id $p.ProcessId" in text
    assert "$NONCODEX_HARNESS_SCRIPT_PATTERN" in text
    assert "$GTKB_VENV_PYTHON_PATTERN" in text


def test_watchdog_preserves_heartbeat_and_logrotate() -> None:
    text = _watchdog_text()

    assert "$ErrorActionPreference = 'SilentlyContinue'" in text
    assert "Set-Content $beat" in text
    assert "codex=$codexCount" in text
    assert "family=$familyCount" in text
    assert "noncodex=$noncodexCount" in text
    assert "GTKB_NO_CROSS_HARNESS_TRIGGER" in text
    assert "Move-Item $log" in text
    assert "1MB" in text
