"""Owner decision D61 (observer B90): GT-KB's owner operations are refused in every harness context.

Starting and stopping GT-KB's services, Home and dashboard, and replacing its operational controls, are neither file nor
Git effects, so the gate passed them for any agent shell before D61. These cases pin the refusal, its reach through
nested and chained shell commands and shell-free argument vectors, and the read-only forms that stay allowed. The gate
classifies command text only; no service, task or control is touched here.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate as gate


def _decide(tmp_path: Path, command: object, tool_name: str = "Bash") -> dict[str, object]:
    return gate.gate_decision({"cwd": str(tmp_path), "tool_name": tool_name, "tool_input": {"command": command}})


@pytest.mark.parametrize(
    ("command", "operation"),
    [
        ("gt services stop authority", "gt services stop"),
        ("gt services start dashboard --json", "gt services start"),
        ("gt --config groundtruth.toml services stop home", "gt services stop"),
        (r"E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe services stop postgresql", "gt services stop"),
        ("python -m groundtruth_kb services stop authority", "gt services stop"),
        ("py -3 -B -m groundtruth_kb home stop", "gt home stop"),
        ("gt home start", "gt home start"),
        ("gt dashboard stop --json", "gt dashboard stop"),
        ("gt dashboard serve", "gt dashboard serve"),
        ("gt controls set --input proposal.toml --expected-sha256 0000", "gt controls set"),
        ("gt services stop m13-probe-unknown", "gt services stop"),
    ],
)
@pytest.mark.parametrize("tool_name", ["Bash", "Shell"])
def test_gt_owner_operations_are_refused(tmp_path: Path, command: str, operation: str, tool_name: str) -> None:
    result = _decide(tmp_path, command, tool_name)

    assert result["decision"] == "block"
    assert result["reason_code"] == "owner_operation_only"
    assert str(result["reason"]).startswith(operation)
    assert "GT-KB Home" in str(result["reason"])


@pytest.mark.parametrize(
    "command",
    [
        'pwsh -NoProfile -Command "gt services stop authority"',
        'cmd /c "gt.exe controls set --input p.toml --expected-sha256 00"',
        'bash -c "gt home stop"',
        "& gt.exe services stop authority",
        "Write-Output ok; gt services stop authority",
        "gt services status | Out-String; gt dashboard stop",
        ["gt", "services", "stop", "authority"],
    ],
)
def test_nested_chained_and_shell_free_owner_operations_are_refused(tmp_path: Path, command: object) -> None:
    result = _decide(tmp_path, command)

    assert result["decision"] == "block"
    assert result["reason_code"] == "owner_operation_only"


@pytest.mark.parametrize(
    "command",
    [
        "Stop-ScheduledTask -TaskName GTKB-DomainService",
        "Disable-ScheduledTask -TaskName 'GTKB-Home'",
        "Get-ScheduledTask -TaskName GTKB-DomainService | Disable-ScheduledTask",
        "Get-ScheduledTask 'GTKB*' | Stop-ScheduledTask",
        "Unregister-ScheduledTask -TaskName GTKB-BaseBackup -Confirm:$false",
        "Stop-Service -Name gtkb-postgresql",
        "Restart-Service gtkb-postgresql",
        "schtasks /End /TN GTKB-DomainService",
        "schtasks.exe /Change /TN GTKB-Home /DISABLE",
        "sc.exe stop gtkb-postgresql",
        "net stop gtkb-postgresql",
        'powershell -Command "Stop-Service -Name gtkb-postgresql"',
    ],
)
def test_raw_changes_to_gtkb_tasks_and_service_are_refused(tmp_path: Path, command: str) -> None:
    result = _decide(tmp_path, command)

    assert result["decision"] == "block"
    assert result["reason_code"] == "owner_operation_only"
    assert "GT-KB task or service" in str(result["reason"])


@pytest.mark.parametrize(
    "command",
    [
        "gt services status",
        "gt services status --json",
        "gt home status",
        "gt home open",
        "gt controls show",
        "gt controls diff --input proposal.toml",
        "gt bridge show doc --content --json",
        "Get-ScheduledTask -TaskName GTKB-DomainService",
        "Get-Service gtkb-postgresql",
        "schtasks /Query /TN GTKB-Home",
        "sc.exe query gtkb-postgresql",
    ],
)
def test_read_only_forms_stay_allowed(tmp_path: Path, command: str) -> None:
    assert _decide(tmp_path, command) == {}
