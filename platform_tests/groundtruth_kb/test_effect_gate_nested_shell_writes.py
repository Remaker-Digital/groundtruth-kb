"""The shared effect gate judges a command handed to a nested shell or to Invoke-Expression as a command of its own (c119).

Owner decision after the 2026-09-27 M13 host I finding on c118 ("Fix first: c119"): a claimless Loyal Opposition context
ran `cmd /c "<gt> --help > help.out 2>&1"` and the gate allowed it, because a quoted command string is one token to the
outer shell, so neither its redirect nor a writing command inside it reached the write judgment. Now the command inside
cmd /c or /k, powershell or pwsh -c/-Command, bash, sh or zsh -c, and Invoke-Expression/iex is judged as the same command
typed directly: a redirect or a writing command there is a write, and a read there stays a read. cmd does not treat
single quotes as quotes, so a redirect between them is a write under cmd. No authority is contacted: a write whose target
the gate cannot name is refused unknown_effect_targets before the native check, and a read passes before it.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate


def _payload(project: Path, command: str) -> dict:
    return {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": "nested-shell-writes-test",
        "cwd": str(project),
        "project_root": str(project),
    }


def _mutating(project: Path, command: str) -> bool:
    return effect_gate.changed_paths(_payload(project, command))[1]


# M13 host I, Q6 on c118 (2026-09-27 05:20:18-05:20:31Z), verbatim; the third wrote help.out into the checkout root.
Q6 = [
    r'cmd /c ".\.groundtruth-kb\.venv\Scripts\gt.exe --help > help.out 2>&1"; Get-Content help.out -Raw',
    r'$gt = (Resolve-Path .\.groundtruth-kb\.venv\Scripts\gt.exe).Path; Write-Output $gt; cmd /c "$gt --help > help.out 2>&1"; '
    r'$code=$LASTEXITCODE; Write-Output "code=$code"; Get-Content help.out -Raw',
    r'$gt = (Resolve-Path .\groundtruth-kb\.venv\Scripts\gt.exe).Path; Write-Output $gt; cmd /c "$gt --help > help.out 2>&1"; '
    r'$code=$LASTEXITCODE; Write-Output "code=$code"; Get-Content help.out -Raw',
]


@pytest.mark.parametrize("command", Q6)
def test_the_q6_commands_are_writes(tmp_path, command):
    assert _mutating(tmp_path, command)


NESTED_WRITES = [
    'cmd /c "echo x > note.txt"',
    'cmd /k "echo x >> note.txt"',
    'cmd.exe /c "type nul > note.txt"',
    'powershell -Command "Set-Content note.txt x"',
    'powershell.exe -command "Remove-Item note.txt"',
    'pwsh -c "echo x > note.txt"',
    "bash -c 'echo x > note.txt'",
    'sh -c "rm note.txt"',
    'zsh -c "touch note.txt"',
    '& cmd /c "echo x > note.txt"',
    'call cmd /c "echo x > note.txt"',
    'iex "echo x > note.txt"',
    "Invoke-Expression 'Remove-Item note.txt'",
    # Nested twice: PowerShell hands a cmd command line that redirects.
    "pwsh -c \"cmd /c 'echo x > note.txt'\"",
    # cmd does not treat single quotes as quotes: this writes a file named b' there.
    "cmd /c \"echo 'a > b'\"",
    # A later stage of the outer command carries the wrapper.
    'Get-Location; cmd /c "echo x > note.txt"',
]


@pytest.mark.parametrize("command", NESTED_WRITES)
def test_a_write_inside_a_nested_shell_or_invoke_expression_is_a_write(tmp_path, command):
    assert _mutating(tmp_path, command)


NESTED_READS = [
    'cmd /c "git status"',
    'pwsh -c "Get-ChildItem -Name ."',
    "bash -c 'ls'",
    r'cmd /c ".\groundtruth-kb\.venv\Scripts\gt.exe --help"',
    'cmd /c "gt --version 2>NUL"',
    'pwsh -c "Get-Content README.md 2>$null"',
    "bash -c 'cat README.md 2>/dev/null'",
    "pwsh -c \"Write-Output 'a > b'\"",
    "bash -c \"echo 'a > b'\"",
    "pwsh -c \"Write-Output 'Remove-Item is not run here'\"",
    'iex "Get-ChildItem -Name ."',
]


@pytest.mark.parametrize("command", NESTED_READS)
def test_a_read_inside_a_nested_shell_or_invoke_expression_stays_a_read(tmp_path, command):
    assert not _mutating(tmp_path, command)


@pytest.mark.parametrize(
    ("direct", "nested"),
    [
        ("echo x > note.txt", 'cmd /c "echo x > note.txt"'),
        ("Set-Content note.txt x", 'pwsh -c "Set-Content note.txt x"'),
        ("rm note.txt", "bash -c 'rm note.txt'"),
        ("git status", 'cmd /c "git status"'),
        ("Get-Content README.md 2>$null", 'pwsh -c "Get-Content README.md 2>$null"'),
    ],
)
def test_a_nested_command_is_judged_as_the_same_command_typed_directly(tmp_path, direct, nested):
    assert _mutating(tmp_path, nested) == _mutating(tmp_path, direct)


def test_an_unparsable_or_too_deep_inner_command_counts_as_a_write(tmp_path, monkeypatch):
    # An unbalanced quote inside the handed command cannot be inspected.
    assert _mutating(tmp_path, "bash -c 'echo \"x'")
    # Beyond the nesting limit even a read counts as a write.
    monkeypatch.setattr(effect_gate, "_INNER_COMMAND_DEPTH", 0)
    assert _mutating(tmp_path, 'cmd /c "git status"')


def test_the_gate_refuses_the_q6_write_and_passes_a_nested_read(tmp_path):
    refused = effect_gate.gate_decision(_payload(tmp_path, Q6[2]))
    assert refused.get("decision") == "block" and refused["reason_code"] == "unknown_effect_targets", refused
    direct = effect_gate.gate_decision(_payload(tmp_path, r"$gt --help > help.out 2>&1"))
    assert direct.get("decision") == "block" and direct["reason_code"] == refused["reason_code"], direct
    assert effect_gate.gate_decision(_payload(tmp_path, 'cmd /c "git status"')) == {}
