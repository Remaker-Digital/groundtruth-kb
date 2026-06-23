"""Static regression coverage for the local dashboard headless launch path."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gtkb_dashboard" / "start_local_dashboard.ps1"


def _script_text() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def test_launcher_exposes_explicit_headless_mode() -> None:
    text = _script_text()

    assert "[switch]$Headless" in text
    assert "function Test-HeadlessLaunch" in text
    assert "$UseHeadlessLaunch = Test-HeadlessLaunch -Requested $Headless.IsPresent" in text
    assert "$env:GTKB_DASHBOARD_HEADLESS" in text
    assert "[Environment]::UserInteractive" in text


def test_headless_branch_does_not_use_hidden_window_style() -> None:
    text = _script_text()
    match = re.search(
        r"if \(\$UseHeadlessLaunch\) \{(?P<headless>.*?)\n    \}\n"
        r"    return Start-Process(?P<interactive>.*?)\n\}",
        text,
        re.DOTALL,
    )
    assert match, "Start-DashboardProcess must keep explicit headless and interactive branches"

    headless_branch = match.group("headless")
    interactive_branch = match.group("interactive")

    assert "-NoNewWindow" in headless_branch
    assert "-WindowStyle Hidden" not in headless_branch
    assert "-WindowStyle Hidden" in interactive_branch


def test_launcher_routes_both_services_through_headless_aware_helper() -> None:
    text = _script_text()

    assert text.count("Start-DashboardProcess `") == 2
    assert text.count("-UseHeadlessLaunch $UseHeadlessLaunch") == 2
    assert '-FilePath "python"' in text
    assert "-FilePath $grafanaFile" in text


def test_launcher_preserves_pid_writes_for_both_services() -> None:
    text = _script_text()

    assert 'Join-Path $PidDir "refresh-service.pid"' in text
    assert 'Join-Path $PidDir "grafana.pid"' in text
    assert "$refreshProcess.Id" in text
    assert "$grafanaProcess.Id" in text
