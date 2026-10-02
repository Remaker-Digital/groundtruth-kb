"""The shared effect gate judges four groups of command forms it let through on c121 (c122).

The batch design's probe of the installed c121 gate (2026-09-30 20:49, probe-wp1-fail-open-20260930T204906.json) found,
in production for every harness: a safe-prefix command with a redirect was never judged (`git diff > patch.txt`); the
Git and owner rules did not look inside script blocks, groups, subexpressions, POSIX keyword stages, launchers or
Invoke-Expression, nor past a program named by a variable (`& { git clean -fdx }`, `uv run git clean -fdx`); a
variable inside a write target was read as a literal path (host I on c120, `Set-Content -Path "$d\\x.txt"`); and git
diff, log and show wrote their --output file under the read-only exemption. Owner decision 2026-09-30 20:52 ("Fix
first: c122"): those four groups only. Every command here is judged, never run; the native effect check is a recorder.
c123 (batch design WP1, B149): a redirect's target is read, so group 1's redirects reach the native check with their
target instead of being refused whole.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate

# Host I's own context in its c120 Q6 session, whose two Set-Content commands are quoted below.
OWN = "SENV-33325758c0474d39bb8341429e0cc819"


@pytest.fixture(autouse=True)
def _own_context(monkeypatch):
    # The gate prefers the harness's own context variable to the payload's session id; these payloads carry the id.
    monkeypatch.delenv("GTKB_NATIVE_CONTEXT_ID", raising=False)
    monkeypatch.setattr(effect_gate, "_bound_session_context", lambda payload, project: (OWN, True))


class _NativeCheck:
    """Stands in for `gt bridge check-effects`: records each call and answers as a claim would.

    c123 (owner decision A1): it answers `gt bridge check-program` too, as a live claim would, and paths() reads the
    effect checks only.
    """

    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, argv, **_kwargs):
        self.calls.append(list(argv))
        if "check-program" in argv:
            answer = {"status": "current", "scope": "program", "claims": 1}
            return subprocess.CompletedProcess(argv, 0, json.dumps(answer), "")
        return subprocess.CompletedProcess(argv, 0, json.dumps({"status": "current", "scope": "implementation"}), "")

    def paths(self) -> list[list[str]]:
        effects = [call for call in self.calls if "check-effects" in call]
        return [[call[index + 1] for index, token in enumerate(call) if token == "--path"] for call in effects]

    def programs(self) -> int:
        return sum("check-program" in call for call in self.calls)


@pytest.fixture
def native(monkeypatch) -> _NativeCheck:
    check = _NativeCheck()
    monkeypatch.setattr(effect_gate.subprocess, "run", check)
    return check


def _payload(project: Path, command: str) -> dict:
    return {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": "command-forms-test",
        "cwd": str(project),
        "project_root": str(project),
    }


def _decide(project: Path, command: str) -> dict:
    return effect_gate.gate_decision(_payload(project, command))


# Group 1: a redirect after a safe-prefix command writes its target. Since c123 (batch design WP1, B149) the target is
# read, so the command reaches the native check with that path, as a direct write does.
SAFE_PREFIX_REDIRECTS = [
    (
        r"Get-Content a.txt > E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py",
        "E:/GT-KB/groundtruth-kb/src/groundtruth_kb/cli.py",
    ),
    ("git diff > patch.txt", "patch.txt"),
    ("python -m pytest -q > out.txt", "out.txt"),
    ("git log 2> err.txt", "err.txt"),
    ("rg x *> out.txt", "out.txt"),
    ("git show HEAD:README.md >> notes.txt", "notes.txt"),
    # Nested: the inner command was skipped as safe before c122.
    ('pwsh -c "Get-Content a.txt > b.txt"', "b.txt"),
]


@pytest.mark.parametrize(("command", "target"), SAFE_PREFIX_REDIRECTS)
def test_a_redirect_after_a_safe_prefix_is_a_write(tmp_path, native, command, target):
    assert not effect_gate._is_safe_command(command)
    assert effect_gate.changed_paths(_payload(tmp_path, command)) == ([target], True)
    assert _decide(tmp_path, command) == {}
    assert native.paths() == [[target]]
    # c123 (owner decision A1): the test run is a program run, checked after its redirect's write.
    assert native.programs() == (1 if "pytest" in command else 0)


@pytest.mark.parametrize(
    "command", ["git status 2>$null", "rg -n x scripts 2>/dev/null", "Get-Content README.md 2>NUL"]
)
def test_a_null_sink_redirect_keeps_a_safe_read(tmp_path, native, command):
    assert effect_gate._is_safe_command(command)
    assert _decide(tmp_path, command) == {}


# Group 2: the Git and owner rules judge every command a line runs (batch design WP1, section W).
GIT_EFFECTS_INSIDE = [
    "& { git clean -fdx }",
    "(git clean -fdx)",
    "if ($true) { git clean -fdx }",
    "if true; then git clean -fdx; fi",
    "for i in 1; do git clean -fdx; done",
    "! git clean -fdx",
    "case $x in a) git clean -fdx;; esac",
    "Get-ChildItem | ForEach-Object { git clean -fdx }",
    'Write-Output "$(git clean -fdx)"',
    "Write-Output (git clean -fdx)",
    "$out = git clean -fdx",
    'iex "git clean -fdx"',
    "Invoke-Expression 'git clean -fdx'",
    "time git clean -fdx",
    "env GIT_TRACE=1 git clean -fdx",
    "uv run git clean -fdx",
    "uv run --with rich git clean -fdx",
    "Start-Process git -ArgumentList 'clean','-fdx'",
    "Start-Process -FilePath git -ArgumentList 'clean', '-fdx' -Wait",
    "start git clean -fdx",
    "git ls-files | xargs git rm",
    "find docs -name '*.tmp' -exec git rm {} ';'",
]


@pytest.mark.parametrize("command", GIT_EFFECTS_INSIDE)
def test_a_git_effect_in_any_command_the_line_runs_is_refused(tmp_path, native, command):
    assert effect_gate._direct_git_effect_from_payload(_payload(tmp_path, command)) in {"clean", "rm"}
    result = _decide(tmp_path, command)
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle", result
    assert native.calls == []


OWNER_OPERATIONS_INSIDE = [
    "& { gt services stop authority }",
    "if true; then gt services stop authority; fi",
    'Write-Output "$(gt services stop authority)"',
    'iex "gt services stop authority"',
    "$r = gt home stop",
    "env gt dashboard stop",
    "uv run gt services stop authority",
    "uv run -m groundtruth_kb services stop authority",
    "Start-Process gt -ArgumentList 'services','stop','authority'",
]


@pytest.mark.parametrize("command", OWNER_OPERATIONS_INSIDE)
def test_an_owner_operation_in_any_command_the_line_runs_is_refused(tmp_path, native, command):
    result = _decide(tmp_path, command)
    assert result["reason_code"] == "owner_operation_only", result
    assert native.calls == []


# A program the gate cannot read: a variable or an expression names it, Invoke-Expression reads it from its pipeline,
# or a launcher option the gate does not know may hide it. Both rules fail closed on their own (observer B102).
UNREADABLE_PROGRAMS = [
    "$g='git'; & $g clean -fdx",
    # M13 host I, Q6 on c118 and c120: the direct form of its `cmd /c "$gt --help > help.out 2>&1"`.
    "$gt --help > help.out 2>&1",
    "& $tool status",
    "& (Get-Command git) clean -fdx",
    "bash -c '$cmd'",
    'pwsh -c "$x = 1"',
    "iex $cmd",
    "Get-Content cmd.txt | iex",
    "Start-Process $exe",
    "uv run --not-a-uv-option pytest",
]


@pytest.mark.parametrize("command", UNREADABLE_PROGRAMS)
def test_a_program_the_gate_cannot_read_fails_both_rules_closed(tmp_path, native, command):
    payload = _payload(tmp_path, command)
    assert effect_gate._direct_git_effect_from_payload(payload) == effect_gate.UNINSPECTABLE_SHELL_COMMAND
    assert effect_gate._owner_operation_from_payload(payload) == effect_gate.UNINSPECTABLE_SHELL_COMMAND
    result = _decide(tmp_path, command)
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle", result
    assert "named by a variable" in result["reason"] and "gt project commit" in result["reason"]


@pytest.mark.parametrize(
    "command",
    [
        "$g='gt'; & $g services stop authority",
        "gt services $action authority",
        "gt $group stop",
        "python -m $module services stop",
    ],
)
def test_the_owner_rule_fails_closed_on_its_own(tmp_path, native, monkeypatch, command):
    assert effect_gate._owner_operation(command) == effect_gate.UNINSPECTABLE_SHELL_COMMAND
    monkeypatch.setattr(effect_gate, "_direct_git_effect_from_payload", lambda payload: None)
    result = _decide(tmp_path, command)
    assert result["reason_code"] == "owner_operation_only", result
    assert "may hide an owner operation" in result["reason"]


# Reads and PowerShell expressions stay allowed: the walk judges commands, not text, values or variables read.
READS = [
    "& { git status }",
    "if ($true) { git log -1 }",
    "Get-ChildItem | Where-Object { $_.Attributes -eq 'Hidden' }",
    "Write-Output '(git clean -fdx)'",
    'Write-Output "git clean -fdx; gt services stop authority"',
    "git log --format='%H (%s)' -1",
    "time git status",
    "git ls-files | xargs grep -l x",
    "find docs -name '*.py' -exec grep -l x {} +",
    "command -v git",
    # c123 (owner decision A1): "uv run pytest -q" and 'uv run --with rich python -c "print(1)"' left this list; uv
    # run is a program run (test_uv_run_is_a_program_run).
    "Start-Process notepad",
    "& 'C:\\Program Files\\Git\\cmd\\git.exe' --version 2>&1 | Out-String",
    "gt services status; gt home status",
    "$g = 'git'; Write-Output $g",
    "$out = git status --short",
    "foreach ($key in @('a')) { $key }",
    "$items = @(1, 2); $items | ForEach-Object { $_ * 2 }",
    "$env:GTKB_RUN_POSTGRES_INTEGRATION='1'",
    "arr=($a $b); echo ${arr[0]}",
]


@pytest.mark.parametrize("command", READS)
def test_reads_and_expressions_stay_allowed(tmp_path, native, command):
    assert _decide(tmp_path, command) == {}
    # c123 (owner decision A1): a read needs no claim, so no native check runs.
    assert native.calls == []


@pytest.mark.parametrize("command", ["uv run pytest -q", 'uv run --with rich python -c "print(1)"'])
def test_uv_run_is_a_program_run(tmp_path, native, command):
    # c123 (owner decision A1): uv run syncs the environment and runs a program, so it needs a live claim.
    assert _decide(tmp_path, command) == {}
    assert native.programs() == 1 and native.paths() == []


# Group 3: a write target whose value the shell supplies when it runs. Host I's two commands of its c120 Q6 session
# (2026-09-29 10:04:32Z and 10:05:33Z, verbatim) and the probe's hole form are refused whole before the native check,
# and the refusal names the target and the remedy.
HOST_I_C120_Q6 = [
    f'$d=\'scratchpad\\{OWN}\'; Set-Content -Path "$d\\m13-c120-v4-verdict-test.txt" -Value "test" -Encoding utf8; '
    'Get-Content "$d\\m13-c120-v4-verdict-test.txt"',
    f'$d=\'scratchpad\\{OWN}\'; $p="$d\\m13-c120-v4-verdict-test.txt"; Set-Content -Path $p -Value "test" '
    "-Encoding utf8; Get-Content $p",
]
UNRESOLVED_TARGETS = [
    *HOST_I_C120_Q6,
    f"$x='..\\..\\groundtruth-kb\\x.py'; Set-Content -Path \"scratchpad\\{OWN}\\$x\" -Value y",
    f'cp a.txt "scratchpad/{OWN}/$X"',
    "Remove-Item $tmp",
    "Out-File -FilePath $env:TEMP\\x.txt",
    "rm ~/notes.txt",
    "New-Item (Join-Path $root x.txt)",
    "Set-Content %TEMP%\\x.txt y",
    "Add-Content -Path @args -Value y",
    "git diff --output=$patch",
]


@pytest.mark.parametrize("command", UNRESOLVED_TARGETS)
def test_a_write_target_the_shell_supplies_is_refused_whole_and_named(tmp_path, native, command):
    assert effect_gate.changed_paths(_payload(tmp_path, command)) == ([], True)
    result = _decide(tmp_path, command)
    assert result["reason_code"] == "unknown_effect_targets", result
    assert "holds a value the shell supplies" in result["reason"] and "-LiteralPath" in result["reason"]
    assert native.calls == []


@pytest.mark.parametrize(
    ("command", "path"),
    [
        (
            f"Set-Content -Path 'scratchpad\\{OWN}\\m13-c120-v4-verdict-test.txt' -Value test",
            f"scratchpad/{OWN}/m13-c120-v4-verdict-test.txt",
        ),
        # Single-quoted text is literal: this names a file called $x.
        (f"Set-Content -Path 'scratchpad\\{OWN}\\$x' -Value y", f"scratchpad/{OWN}/$x"),
        # A value is not a target.
        ("Set-Content notes.txt $value", "notes.txt"),
    ],
)
def test_a_literal_target_reaches_the_native_check(tmp_path, native, command, path):
    assert _decide(tmp_path, command) == {}
    assert native.paths() == [[path]]


@pytest.mark.parametrize(
    ("word", "unresolved"),
    [
        ("notes.txt", False),
        ('"notes.txt"', False),
        ("'notes $x.txt'", False),
        ("100%.txt", False),
        ("$p", True),
        ('"$d\\x.txt"', True),
        ("${HOME}/x", True),
        ("$env:TEMP\\x", True),
        ("%TEMP%\\x", True),
        ("~/x", True),
        ("'~/x'", True),
        ("@args", True),
        ("(Get-Item x)", True),
        ("a`b", True),
        ('"unclosed', True),
    ],
)
def test_the_unresolved_value_rule(word, unresolved):
    assert effect_gate._unresolved_value(word) is unresolved


# Group 4: git diff, log, show and whatchanged write the file --output names; the write is checked like any other.
@pytest.mark.parametrize(
    ("command", "path"),
    [
        ("git diff --output=out.patch", "out.patch"),
        ("git log --output log.txt", "log.txt"),
        ("git show HEAD --output=show.txt", "show.txt"),
        ("git -C . --no-pager diff --stat --output=stat.txt", "stat.txt"),
        ('git diff --output="out dir/x.patch"', "out dir/x.patch"),
    ],
)
def test_git_output_is_a_write_of_its_file(tmp_path, native, command, path):
    assert not effect_gate._is_safe_command(command)
    assert effect_gate.changed_paths(_payload(tmp_path, command)) == ([path], True)
    assert _decide(tmp_path, command) == {}
    assert native.paths() == [[path]]


def test_git_output_without_a_file_or_inside_a_block_is_refused_whole(tmp_path, native):
    for command in ("git diff --output", "& { git diff --output=out.patch }"):
        assert effect_gate.changed_paths(_payload(tmp_path, command)) == ([], True), command
        assert _decide(tmp_path, command)["reason_code"] == "unknown_effect_targets", command
    assert native.calls == []


def test_an_output_indicator_option_is_not_output(tmp_path, native):
    command = "git diff --output-indicator-new=+ --stat"
    assert effect_gate._is_safe_command(command)
    assert _decide(tmp_path, command) == {}
