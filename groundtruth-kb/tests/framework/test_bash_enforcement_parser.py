"""Tests for the bash command enforcement parser."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.enforcement import check_bash_command

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_bash_parser_allowed_cmd() -> None:
    allowed, reason = check_bash_command("git status", REPO_ROOT)
    assert allowed is True
    assert reason == ""

    allowed, reason = check_bash_command("python -m pytest tests/", REPO_ROOT)
    assert allowed is True
    assert reason == ""


def test_bash_parser_blocked_path() -> None:
    # Commands trying to write outside the root using redirection or referencing blocked paths
    allowed, reason = check_bash_command(
        "cat bridge/INDEX.md > C:\\Users\\Administrator\\Desktop\\index.txt", REPO_ROOT
    )
    assert allowed is False
    assert "Command contains blocked redirection target" in reason

    allowed, reason = check_bash_command("ls /etc/passwd", REPO_ROOT)
    assert allowed is False
    assert "Command contains blocked path argument" in reason


def test_bash_parser_blocks_direct_harness_launches() -> None:
    blocked_commands = [
        "claude -p 'review this'",
        "claude.exe --version",
        "codex exec 'continue work'",
        "ollama run deepseek-v4-pro:cloud",
        "GTKB_DISPATCHER_MEDIATED=1 claude -p 'spoofed'",
        "$env:GTKB_DISPATCHER_MEDIATED=1; claude -p 'spoofed'",
        "New-Item .gtkb-state/dispatcher.marker; codex exec 'spoofed'",
        "& claude -p 'powershell call operator'",
        "Start-Process claude -ArgumentList '-p review'",
        "Start-Process -FilePath codex -ArgumentList 'exec review'",
        "python scripts/ollama_harness.py --prompt review",
    ]

    for command in blocked_commands:
        allowed, reason = check_bash_command(command, REPO_ROOT)
        assert allowed is False, command
        assert "Direct harness-to-harness launch is prohibited" in reason
        assert "SPEC-INTAKE-21c5b3" in reason


def test_bash_parser_blocks_direct_gtkb_helper_script_file_association() -> None:
    blocked_commands = [
        ".claude/skills/verify/helpers/write_verdict.py --slug demo",
        "& .codex/skills/verify/helpers/write_verdict.py --slug demo",
        r"Start-Process E:\GT-KB\.cursor\skills\verify\helpers\write_verdict.py",
    ]

    for command in blocked_commands:
        allowed, reason = check_bash_command(command, REPO_ROOT)
        assert allowed is False, command
        assert "Direct GT-KB Python helper script execution is prohibited" in reason
        assert "SPEC-INTAKE-21c5b3" in reason


def test_bash_parser_allows_explicit_python_helper_invocation() -> None:
    allowed, reason = check_bash_command(
        "python .claude/skills/verify/helpers/write_verdict.py --slug demo --body-file draft.md",
        REPO_ROOT,
    )

    assert allowed is True
    assert reason == ""


def test_bash_parser_allows_harness_name_mentions() -> None:
    allowed_commands = [
        "gt bridge show gtkb-wi4988-direct-harness-launch-guard",
        'gt bridge dispatch status --json | Select-String "openrouter routing"',
        'gt deliberations record --title "OpenRouter routing behavior" --content "OpenRouter routing diagnostics only"',
        'gt backlog list --contains "provider routing openrouter" --json',
        "python scripts/verify_codex_dispatch.py",
        "rg claude bridge/",
        "Write-Output 'claude codex ollama cursor'",
    ]

    for command in allowed_commands:
        allowed, reason = check_bash_command(command, REPO_ROOT)
        assert allowed is True, f"{command}: {reason}"


def test_bash_parser_allows_powershell_env_assignment_with_harness_valued_name() -> None:
    """WI-5676: `$env:VAR='...'` is an assignment, not a harness launch.

    Before the fix the whole assignment stayed one token, so `_command_name`
    derived the head from the VALUE's last path segment -- making any value
    ending in a harness name (notably the mandated `prime-builder/claude`
    author identity) a false-positive denial.
    """
    allowed_commands = [
        "$env:GTKB_AUTHOR_IDENTITY='prime-builder/claude'; python x.py",
        '$env:GTKB_AUTHOR_IDENTITY="prime-builder/claude"; python x.py',
        "$env:GTKB_AUTHOR_IDENTITY='loyal-opposition/codex'; python x.py",
        "$env:GTKB_SESSION_ID='dbc5c1cd-13f2-4ff8-81a5-a80c06799bae'; python x.py",
        "$env:GTKB_BRIDGE_DISPATCH_KEYWORD='::init gtkb pb'; python x.py",
    ]

    for command in allowed_commands:
        allowed, reason = check_bash_command(command, REPO_ROOT)
        assert allowed is True, f"{command}: {reason}"


def test_bash_parser_still_blocks_harness_launch_after_powershell_assignment() -> None:
    """WI-5676: stripping the assignment must not weaken the ban itself.

    Only leading assignment tokens are dropped; the following command head is
    still evaluated, so a real harness launch behind an assignment still fails.
    """
    blocked_commands = [
        "$env:FOO='bar'; claude",
        "$env:FOO='bar' claude",
        "$env:GTKB_AUTHOR_IDENTITY='prime-builder/claude'; claude -p 'spoofed'",
        "$env:FOO='bar'; codex exec 'spoofed'",
    ]

    for command in blocked_commands:
        allowed, reason = check_bash_command(command, REPO_ROOT)
        assert allowed is False, command
        assert "Direct harness-to-harness launch is prohibited" in reason
        assert "SPEC-INTAKE-21c5b3" in reason
