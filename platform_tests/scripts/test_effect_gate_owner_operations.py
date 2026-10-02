"""Owner decision D61 (observer B90): GT-KB's owner operations are refused in every harness context.

Starting and stopping GT-KB's services, Home and dashboard, and replacing its operational controls, are neither file nor
Git effects, so the gate passed them for any agent shell before D61. These cases pin the refusal, its reach through
nested and chained shell commands and shell-free argument vectors, and the read-only forms that stay allowed. The gate
classifies command text only; no service, task or control is touched here.

c115 adds the single `&` as a command separator (cmd's separator, the background operator of bash and PowerShell 7),
nesting to the inspection cap, and the rule's own fail-closed refusal of commands it cannot inspect (observer B102), so
the refusal does not depend on the Git rule running first. Redirections such as `2>&1` stay what they are.
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
        # c123 (owner decision A2): gt home open starts the Home when it is down (it left the read-only list below);
        # gt db postgres init and import-current administer the authority database directly.
        ("gt home open", "gt home open"),
        ("gt db postgres init", "gt db postgres init"),
        ("gt db postgres import-current --input m.json --actor a --reason r", "gt db postgres import-current"),
        ("python -m groundtruth_kb db postgres init --upgrade-from 00", "gt db postgres init"),
        # c123 (owner decision A2): ending a process, whatever the process, and controlling or reaching the PostgreSQL
        # cluster directly.
        ("Stop-Process -Name postgres", "Stop-Process"),
        ("spps -Id 4242", "spps"),
        ("kill 4242", "kill"),
        ("kill -9 4242", "kill"),
        ("taskkill /F /IM postgres.exe", "taskkill"),
        ("tskill 4242", "tskill"),
        ("pkill postgres", "pkill"),
        ("killall node", "killall"),
        ("wmic process where name='postgres.exe' delete", "wmic process"),
        ("pg_ctl -D data stop", "pg_ctl stop"),
        ("pg_ctl start -D data -l log.txt", "pg_ctl start"),
        ("pg_ctl.exe restart -D data", "pg_ctl.exe restart"),
        ("postgres -D data", "postgres"),
        ("initdb -D data", "initdb"),
        ("pg_resetwal -D data", "pg_resetwal"),
        ("psql -c 'select 1'", "psql"),
        ("pg_dump gtkb", "pg_dump"),
        ("dropdb gtkb", "dropdb"),
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
        "echo ok & gt services stop authority",
        'cmd /c "echo ok & gt services stop authority"',
        "cmd /c echo ok & gt home stop",
        "bash -c 'echo ok & gt dashboard stop'",
        "cmd /c cmd /c gt services stop authority",
        "cmd /c cmd /c cmd /c cmd /c gt controls set --input p.toml --expected-sha256 00",
        # c123 (owner decision A2): the new operations through nested shells, chains, launchers, Invoke-Expression,
        # script blocks, subexpressions and argument lists, and .Kill() or Terminate calls wherever they run.
        'pwsh -NoProfile -Command "Stop-Process -Name postgres"',
        'cmd /c "taskkill /F /IM postgres.exe"',
        "bash -c 'kill 4242'",
        "Get-Process postgres | Stop-Process",
        "uv run gt home open",
        "Start-Process taskkill -ArgumentList '/F','/IM','postgres.exe'",
        'iex "pg_ctl -D data stop"',
        "& { psql -c 'select 1' }",
        'Write-Output "$(gt db postgres init)"',
        ["pg_ctl", "stop", "-D", "data"],
        "(Get-Process postgres).Kill()",
        "$p = Get-Process postgres; $p.Kill()",
        'Write-Output "$((Get-Process postgres).Kill())"',
        'pwsh -c "(Get-Process postgres).Kill()"',
        "Get-CimInstance Win32_Process -Filter \"Name='postgres.exe'\" | Invoke-CimMethod -MethodName Terminate",
    ],
)
def test_nested_chained_and_shell_free_owner_operations_are_refused(tmp_path: Path, command: object) -> None:
    result = _decide(tmp_path, command)

    assert result["decision"] == "block"
    assert result["reason_code"] == "owner_operation_only"


@pytest.mark.parametrize(
    "command",
    [
        "cmd /c " * 5 + "gt services stop authority",
        "cmd /c " * 7 + "gt home stop",
        "pwsh -EncodedCommand ZwB0AA==",
        "cmd /c",
        'cmd /c "echo ok & pwsh -EncodedCommand ZwB0AA=="',
    ],
)
def test_the_owner_rule_refuses_commands_it_cannot_inspect_on_its_own(
    tmp_path: Path, command: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The Git rule runs first and refuses these too; with it out of the way the owner rule must still refuse them.
    assert gate._owner_operation(command) == gate.UNINSPECTABLE_SHELL_COMMAND
    assert _decide(tmp_path, command)["decision"] == "block"
    monkeypatch.setattr(gate, "_direct_git_effect_from_payload", lambda payload: None)

    result = _decide(tmp_path, command)

    assert result["decision"] == "block"
    assert result["reason_code"] == "owner_operation_only"
    assert "may hide an owner operation" in str(result["reason"])


@pytest.mark.parametrize(
    "command",
    [
        "gt services status 2>&1",
        "gt home status >&2",
        "gt controls show |& cat",
        "cmd /c gt services status & gt home status",
    ],
)
def test_redirections_and_read_only_chains_are_not_owner_operations(tmp_path: Path, command: str) -> None:
    assert _decide(tmp_path, command) == {}


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
        # c123 (owner decision A2): "gt home open" left this list; it is refused above.
        "gt controls show",
        "gt controls diff --input proposal.toml",
        "gt bridge show doc --content --json",
        "Get-ScheduledTask -TaskName GTKB-DomainService",
        "Get-Service gtkb-postgresql",
        "schtasks /Query /TN GTKB-Home",
        "sc.exe query gtkb-postgresql",
        # c123 (owner decision A2): reads of process and cluster state, and the shell's own jobs, stay allowed.
        "gt service status",
        "gt db postgres status",
        "pg_ctl status -D data",
        "pg_isready",
        "Get-Process postgres",
        "tasklist",
        'tasklist /FI "IMAGENAME eq postgres.exe"',
        "Stop-Job 1",
        "Remove-Job -Id 1",
        "kill %1",
        "kill -9 %1",
        "kill -l",
        "psql --version",
        "pg_dump -V",
        "wmic process list brief",
    ],
)
def test_read_only_forms_stay_allowed(tmp_path: Path, command: str) -> None:
    assert _decide(tmp_path, command) == {}
