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
    assert "cursor_harness.py" in text
    assert "$NONCODEX_HARNESS_SCRIPT_PATTERN" in text
    assert "$GTKB_VENV_PYTHON_PATTERN" in text


def test_watchdog_has_noncodex_threshold_trip() -> None:
    text = _watchdog_text()

    assert "$NONCODEX_THRESHOLD = 15" in text
    assert "$noncodexCount -gt $NONCODEX_THRESHOLD" in text
    # WI-4780: the watchdog still DETECTS the storm population and intervenes
    # (corpse-reaping); it no longer auto-asserts the kill-switch
    # (SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001). The kill-switch-presence
    # assertion is removed; see test_watchdog_does_not_auto_assert_kill_switch.
    assert "noncodexThreshold=$NONCODEX_THRESHOLD" in text


def test_watchdog_covers_registry_python_dispatch_harnesses() -> None:
    """The watchdog watched non-codex script set must cover every ACTIVE
    dispatch-capable python harness the registry declares (WI-4818).

    Supersedes the prior low-cost-only coverage definition, which filtered on
    the ``low-cost`` dispatch tag and therefore missed the high-quality Cursor
    harness (``dispatch_tags = ["prime-builder"]``) that nonetheless dispatches
    headless via ``scripts/cursor_harness.py``. The expected set is derived from
    active harnesses whose headless argv invokes a ``scripts/*_harness.py``
    python backend (ollama / openrouter / cursor); codex / claude / gemini
    invocations carry no ``*_harness.py`` and are excluded. ``can_receive_dispatch``
    is intentionally NOT used as a filter (it is overlay-controlled and currently
    false for all python backends). The watchdog watched-set must be a superset of
    the registry-derived set so a future python harness cannot silently regress
    coverage.
    """
    text = _watchdog_text()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    expected_scripts: set[str] = set()
    for harness in registry["harnesses"]:
        if harness.get("status") != "active":
            continue
        surfaces = harness.get("invocation_surfaces", {})
        for surface in surfaces.values():
            argv = surface.get("argv", [])
            if not any(str(part).lower().endswith(("python.exe", "python")) for part in argv):
                continue
            for part in argv:
                path = Path(str(part).replace("\\", "/"))
                if path.name.endswith("_harness.py"):
                    expected_scripts.add(path.name)

    assert expected_scripts == {
        "ollama_harness.py",
        "openrouter_harness.py",
        "cursor_harness.py",
    }, expected_scripts
    for script_name in expected_scripts:
        assert script_name in text, f"watchdog watched-set missing {script_name}"


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
    # WI-4780: kill-switch-presence assertion removed (the watchdog no longer
    # auto-asserts it); heartbeat + logrotate observability is preserved.
    assert "Move-Item $log" in text
    assert "1MB" in text


def test_watchdog_does_not_auto_assert_kill_switch() -> None:
    """WI-4780 / SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 A.1: the watchdog
    MUST NOT auto-assert the global GTKB_NO_CROSS_HARNESS_TRIGGER kill-switch.

    Storm protection is the verified concurrency cap (WI-4472) and the
    worker-lifetime timeout (WI-4806); corpse-reaping is retained but the
    set-only kill-switch latch is removed (DELIB-20265877, DELIB-20260612).
    """
    text = _watchdog_text()

    assert "SetEnvironmentVariable('GTKB_NO_CROSS_HARNESS_TRIGGER'" not in text
    assert "kill-switch=not-asserted" in text
    # corpse-reaping retained (WI-4780 option a: reap, do not latch)
    assert "Stop-Process -Id $p.ProcessId" in text
