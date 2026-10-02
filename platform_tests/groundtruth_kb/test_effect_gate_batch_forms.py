"""The shared effect gate judges the command forms of the batch design's WP1 core (c123).

Owner decision 2026-09-30 20:11 ("Batch it"); batch design WP1 (wp1-effect-gate.md), the items that need no owner
answer: item 3 (Git forms that read or write by their arguments, and pathspecs written without --), item 4's table
(gt service serve and gt dashboard install; python's valued options before -m), and c121's stated residuals that the
design closes (rows 1 to 7, 9, 13, 14 and 16; row 10 is accepted and stated in the gate). Every command here is judged,
never run; the native effect check is a recorder.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate

OWN = "SENV-" + "0" * 32
# Host I's contexts in the c119 and c120 sessions whose commands are quoted below.
HOST_I_C120_CHECKOUT = "SENV-a4f94f5415374018a51f112f4efadcf7"
HOST_I_C120_Q6 = "SENV-33325758c0474d39bb8341429e0cc819"


class _NativeCheck:
    """Stands in for `gt bridge check-effects`: records each call and answers as a claim would.

    c123 (owner decision A1): it answers `gt bridge check-program` too, as a live claim would (Start-Process python is a
    program run), and paths() reads the last effect check.
    """

    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, argv, **_kwargs):
        self.calls.append(list(argv))
        if "check-program" in argv:
            answer = {"status": "current", "scope": "program", "claims": 1}
            return subprocess.CompletedProcess(argv, 0, json.dumps(answer), "")
        return subprocess.CompletedProcess(argv, 0, json.dumps({"status": "current", "scope": "implementation"}), "")

    def paths(self) -> list[str] | None:
        effects = [call for call in self.calls if "check-effects" in call]
        if not effects:
            return None
        call = effects[-1]
        return [call[index + 1] for index, token in enumerate(call) if token == "--path"]


@pytest.fixture
def project(tmp_path: Path) -> Path:
    for folder in (".git", "scratchpad", ".worktrees", "sub", "m13-sentinel"):
        (tmp_path / folder).mkdir()
    return tmp_path


@pytest.fixture
def native(monkeypatch) -> _NativeCheck:
    check = _NativeCheck()
    monkeypatch.delenv("GTKB_NATIVE_CONTEXT_ID", raising=False)
    monkeypatch.setattr(effect_gate.subprocess, "run", check)
    monkeypatch.setattr(effect_gate, "_bound_session_context", lambda payload, root: (OWN, True))
    return check


def _decide(project: Path, command: str, **extra: object) -> dict:
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": "batch-forms-test",
        "cwd": str(project),
        "project_root": str(project),
        **extra,
    }
    return effect_gate.gate_decision(payload)


# ---- item 3: Git forms that read or write by their arguments, and pathspecs without -- ------------------------------
HOST_I_READS = [
    ("git diff -- groundtruth.toml; Write-Output '---'; git status --short --ignored m13-sentinel", OWN),
    (
        "$wt = 'E:\\GTKB-realignment-runtemp\\m13-checkout-9a8c98f\\.worktrees\\SENV-a4f94f5415374018a51f112f4efadcf7';"
        " git -C $wt hash-object m13-sentinel/sentinel.txt; git -C $wt hash-object"
        " platform_tests/groundtruth_kb/test_native_authority_service.py",
        HOST_I_C120_CHECKOUT,
    ),
    (
        "git -C . config --get core.autocrlf; git -C . config --get core.eol; git -C . check-attr text eol --"
        " m13-sentinel/sentinel.txt; git -C . check-attr text eol --"
        " platform_tests/groundtruth_kb/test_native_authority_service.py",
        HOST_I_C120_Q6,
    ),
    ("git worktree list", OWN),
]
GIT_READS = [
    "git hash-object -t blob --path=x.txt m13-sentinel/sentinel.txt",
    "git worktree list --porcelain",
    "git config --get-regexp core",
    "git config --list",
    "git config -l --show-origin",
    "git config get core.eol",
    "git ls-files -o m13-sentinel",
    "git grep --no-index -n x m13-sentinel",
    "git status --ignored m13-sentinel",
]
GIT_WRITES = [
    "git hash-object -w x",
    "git hash-object -wt blob x",
    "git hash-object --stdin -w",
    "git worktree add ../w",
    "git worktree remove w",
    "git worktree prune",
    "git config --unset x",
    "git config set x y",
    "git config x y",
    "git config -e",
    "git config core.eol",
    "git config --get x --frobnicate",
]
GIT_REACHES = [
    "git status --ignored :/",
    "git status --ignored scratchpad",
    'git ls-files -o "*.txt"',
    "git grep --no-index x :/",
    "git ls-files -o -x keep scratchpad",
]


@pytest.mark.parametrize(("command", "context"), HOST_I_READS)
def test_host_i_git_reads_are_allowed(project, native, monkeypatch, command, context) -> None:
    monkeypatch.setattr(effect_gate, "_bound_session_context", lambda payload, root: (context, True))

    assert _decide(project, command) == {}
    assert native.calls == []


@pytest.mark.parametrize("command", GIT_READS)
def test_git_read_forms_are_allowed(project, native, command) -> None:
    assert _decide(project, command) == {}
    assert native.calls == []


@pytest.mark.parametrize("command", GIT_WRITES)
def test_git_write_forms_and_unknown_options_are_refused(project, native, command) -> None:
    assert _decide(project, command)["reason_code"] == "direct_git_effect_requires_lifecycle"


@pytest.mark.parametrize("command", GIT_REACHES)
def test_pathspecs_without_double_dash_and_magic_reach_the_shared_roots(project, native, command) -> None:
    assert _decide(project, command)["reason_code"] == "context_traversal"


def test_a_magic_pathspec_from_inside_a_checkout_stays_in_that_checkout(project, native) -> None:
    checkout = project / ".worktrees" / OWN
    (checkout / ".git").mkdir(parents=True)
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "git status --ignored :/"},
        "session_id": "batch-forms-test",
        "cwd": str(checkout),
        "project_root": str(project),
    }

    assert effect_gate.gate_decision(payload) == {}


# ---- item 4: the owner table and python's valued options -------------------------------------------------------------
@pytest.mark.parametrize(
    "command",
    [
        "gt service serve",
        "gt dashboard install",
        "python -X utf8 -m groundtruth_kb services stop",
        "python -W ignore -m groundtruth_kb dashboard install",
        "& { gt service serve }",
    ],
)
def test_service_operations_are_owner_operations(project, native, command) -> None:
    assert _decide(project, command)["reason_code"] == "owner_operation_only"


@pytest.mark.parametrize(
    "command", ["gt services status", "gt dashboard status", "python -X utf8 -m groundtruth_kb services status"]
)
def test_service_reads_stay_allowed(project, native, command) -> None:
    assert _decide(project, command) == {}


# ---- rows 1 to 3: the write rule judges every line the walk finds -----------------------------------------------------
@pytest.mark.parametrize(
    "command",
    [
        'for f in *.txt; do rm "$f"; done',
        "find sub -name x -exec rm {} \\;",
        "find sub -name '*.tmp' -execdir rm {} +",
        "find sub -delete",
        "ls | xargs rm",
    ],
)
def test_loops_find_and_xargs_writes_are_refused_whole(project, native, command) -> None:
    assert _decide(project, command)["reason_code"] == "unknown_effect_targets"
    assert native.calls == []


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("FOO=1 rm x.txt", ["x.txt"]),
        ("env rm x.txt", ["x.txt"]),
        ("env FOO=1 rm x.txt", ["x.txt"]),
        ("if true; then rm x.txt; fi", ["x.txt"]),
        ("nohup rm x.txt", ["x.txt"]),
        ("find sub -fprint out.txt", ["out.txt"]),
    ],
)
def test_writes_after_prefixes_and_launchers_reach_the_native_check(project, native, command, expected) -> None:
    assert _decide(project, command) == {}
    assert native.paths() == expected


# ---- row 4: a change of directory ------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("cd sub; Set-Content x.txt y", ["sub/x.txt"]),
        ("Set-Location sub; Set-Content x.txt y", ["sub/x.txt"]),
        ("cd sub && echo x > out.txt", ["sub/out.txt"]),
        ("cd sub; Set-Content ../x.txt y", ["x.txt"]),
        ('cd "sub"; rm x.txt', ["sub/x.txt"]),
    ],
)
def test_a_leading_change_of_directory_moves_the_targets(project, native, command, expected) -> None:
    assert _decide(project, command) == {}
    assert native.paths() == expected


@pytest.mark.parametrize(
    "command",
    [
        "cd $d; Set-Content x y",
        "Set-Content a.txt x; cd sub; Set-Content b.txt y",
        "cd sub; cd x; rm y",
        "popd; rm x",
        "(cd sub; rm x)",
        "cd; rm x",
        "cd -; rm x",
    ],
)
def test_any_other_change_of_directory_refuses_relative_writes(project, native, command) -> None:
    decision = _decide(project, command)

    assert decision["reason_code"] == "unknown_effect_targets"
    assert "change of directory" in decision["reason"] or "$d" in decision["reason"]
    assert native.calls == []


def test_a_change_of_directory_before_a_read_is_a_read(project, native) -> None:
    assert _decide(project, "cd sub; Get-Content x.txt") == {}
    assert native.calls == []


# ---- row 4 across calls: a persistent shell (c123, owner decision A6) ---------------------------------------------------
# The DeepSeek SDK host's and the GT-KB Home's pwsh tool keeps its working directory across calls, while the gate judges
# each call from the payload's cwd, so a payload marked "persistent_shell": true may not change the directory its
# session keeps. PowerShell's location belongs to the whole runspace: a change inside a script block, a group, a
# subexpression or Invoke-Expression text persists as well. A command handed to another process changes only that
# process's directory.
PERSISTING_DIRECTORY_CHANGES = [
    "Set-Location sub",
    "cd sub; Set-Content x.txt y",
    "Get-ChildItem; sl ..",
    "chdir sub",
    "Push-Location sub; Get-ChildItem; Pop-Location",
    "Get-Item sub | Set-Location",
    "Microsoft.PowerShell.Management\\Set-Location sub",
    "& { Set-Location sub }",
    ". { cd sub }",
    "Get-ChildItem -Directory | ForEach-Object { Push-Location $_.FullName; Get-ChildItem; Pop-Location }",
    "if ($true) { cd sub }",
    "(Set-Location sub)",
    'Write-Output "$(Set-Location sub)"',
    'iex "Set-Location sub"',
    "Invoke-Expression 'cd sub'",
    "[Environment]::CurrentDirectory = 'E:\\x'",
    "[System.Environment]::CurrentDirectory=$PWD",
    "[IO.Directory]::SetCurrentDirectory('E:\\x')",
    "$ExecutionContext.SessionState.Path.SetLocation('E:\\x')",
    "& { iex \"[Environment]::CurrentDirectory = 'x'\" }",
]


@pytest.mark.parametrize("command", PERSISTING_DIRECTORY_CHANGES)
def test_a_persistent_shell_may_not_change_its_directory(project, native, command) -> None:
    decision = _decide(project, command, persistent_shell=True)

    assert decision["reason_code"] == "persistent_shell_directory_change"
    assert "keeps its working directory across calls" in decision["reason"] and "-LiteralPath" in decision["reason"]
    assert native.calls == []


@pytest.mark.parametrize(
    "command",
    [
        'pwsh -NoProfile -Command "Set-Location sub; Get-ChildItem"',
        'cmd /c "cd sub && dir"',
        "bash -c 'cd sub && ls'",
        'Start-Process pwsh -ArgumentList "-NoProfile -Command Set-Location sub"',
        "Get-Location",
        "Get-ChildItem -LiteralPath sub",
        "Write-Output 'Set-Location sub'",
    ],
)
def test_a_persistent_shell_may_hand_a_change_of_directory_to_another_process(project, native, command) -> None:
    assert _decide(project, command, persistent_shell=True) == {}
    assert native.calls == []


def test_only_a_true_mark_makes_a_shell_persistent(project, native) -> None:
    assert _decide(project, "Set-Location sub", persistent_shell="true") == {}
    assert _decide(project, "cd sub; Set-Content x.txt y", persistent_shell=False) == {}
    assert native.paths() == ["sub/x.txt"]


# ---- rows 5 and 6: sc, Set-Item and Clear-Item ------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("sc notes.txt x", ["notes.txt"]),
        ("Set-Item -Path x.txt -Value y", ["x.txt"]),
        ("Clear-Item x.txt", ["x.txt"]),
        ("si x.txt y", ["x.txt"]),
    ],
)
def test_item_writes_and_sc_as_set_content_name_their_targets(project, native, command, expected) -> None:
    assert _decide(project, command) == {}
    assert native.paths() == expected


@pytest.mark.parametrize(
    "command",
    [
        "sc query x",
        "sc.exe query x",
        "sc \\\\server query x",
        "Set-Item Env:X y",
        "Set-Item -Path Env:X -Value y",
        "si Variable:x 1",
        "Clear-Item Alias:foo",
    ],
)
def test_sc_exe_and_session_state_items_are_not_file_writes(project, native, command) -> None:
    assert _decide(project, command) == {}
    assert native.calls == []


@pytest.mark.parametrize(
    "command",
    [
        "Set-Item -Path HKCU:\\Software\\x -Value y",
        "Clear-Item WSMan:\\localhost\\x",
        "Set-ItemProperty -Path HKLM:\\SOFTWARE\\x -Name y -Value z",
        "New-Item -Path Cert:\\CurrentUser\\My",
    ],
)
def test_machine_configuration_writes_are_owner_operations(project, native, command) -> None:
    decision = _decide(project, command)

    assert decision["reason_code"] == "owner_operation_only"
    assert "machine configuration" in decision["reason"]


# ---- rows 7 and 9: curl, wget and Start-Process -------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("curl -o out.txt https://example.invalid", ["out.txt"]),
        ("curl -sSLo out.txt https://example.invalid", ["out.txt"]),
        ("curl --output=out.txt https://example.invalid", ["out.txt"]),
        ("curl -H 'X: y' -o out.txt https://example.invalid", ["out.txt"]),
        ("wget -O out.html https://example.invalid", ["out.html"]),
        ("wget --output-document=out.html https://example.invalid", ["out.html"]),
        ("Start-Process python -RedirectStandardOutput out.txt", ["out.txt"]),
        ("Start-Process python -RedirectStandardError:err.txt -NoNewWindow", ["err.txt"]),
    ],
)
def test_option_writes_name_their_files(project, native, command, expected) -> None:
    assert _decide(project, command) == {}
    assert native.paths() == expected


@pytest.mark.parametrize(
    "command",
    [
        "curl -O https://example.invalid/x",
        "wget https://example.invalid/x",
        "wget -P dl https://example.invalid/x",
        "curl -o $out https://example.invalid",
        "Start-Process python -RedirectStandardOutput $o",
    ],
)
def test_option_writes_without_a_readable_file_are_refused_whole(project, native, command) -> None:
    assert _decide(project, command)["reason_code"] == "unknown_effect_targets"
    assert native.calls == []


@pytest.mark.parametrize(
    "command",
    [
        "curl https://example.invalid",
        "curl -o - https://example.invalid",
        "wget -O - https://example.invalid",
        "wget -qO- https://example.invalid",
        "wget --spider https://example.invalid",
        "New-TemporaryFile",
    ],
)
def test_downloads_to_standard_output_and_temporary_files_are_reads(project, native, command) -> None:
    assert _decide(project, command) == {}
    assert native.calls == []


# ---- rows 13 and 14: Python ----------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "source",
    [
        "from shutil import copy; copy('a', 'b')",
        "import shutil as sh; sh.rmtree('x')",
        "from os import remove as rm; rm('x')",
        "m = 'w'; open('x', m).write('y')",
        "import os; os.open('x', flags)",
        "import os; os.open('x', 1)",
        "from io import open; open('x', 'a')",
    ],
)
def test_python_writes_through_imports_and_computed_modes_are_refused(project, native, source) -> None:
    assert _decide(project, f'python -c "{source}"')["reason_code"] == "unknown_effect_targets"


@pytest.mark.parametrize(
    "source",
    [
        "print(open('x').read())",
        "import os; os.open('x', os.O_RDONLY)",
        "from os import path; path.join('a')",
        "from pathlib import Path; print(Path('x').read_text())",
    ],
)
def test_python_reads_stay_allowed(project, native, source) -> None:
    assert _decide(project, f'python -c "{source}"') == {}


# ---- row 16: a write cmdlet's name given to a help or lookup command ---------------------------------------------------
@pytest.mark.parametrize(
    "command", ["Get-Help Export-Csv", "Get-Command Remove-Item", "help Set-Content -Full", "gcm Set-Item"]
)
def test_help_and_lookup_arguments_are_not_writes(project, native, command) -> None:
    assert _decide(project, command) == {}
    assert native.calls == []


def test_a_write_after_a_help_command_is_still_judged(project, native) -> None:
    assert _decide(project, "Get-Help x; Remove-Item y.txt") == {}
    assert native.paths() == ["y.txt"]


# ---- what stays as it was -------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("Set-Content a.txt x", ["a.txt"]),
        ("rm a.txt", ["a.txt"]),
        ("echo x > out.txt", ["out.txt"]),
        # c123 (owner decision A5, row 18): a copy's source is read, so only the destination is checked.
        ("Copy-Item a.txt b.txt", ["b.txt"]),
        ("git diff --output=x.patch", ["x.patch"]),
    ],
)
def test_plain_writes_still_reach_the_native_check(project, native, command, expected) -> None:
    assert _decide(project, command) == {}
    assert native.paths() == expected


@pytest.mark.parametrize(
    "command", ["Get-Content a.txt", "git log --oneline", "rg x", "ls -la", "Write-Output 'rm x'", "echo 'cd sub'"]
)
def test_plain_reads_stay_allowed(project, native, command) -> None:
    assert _decide(project, command) == {}
    assert native.calls == []


@pytest.mark.parametrize("command", ["& { Set-Content x.txt y }", "if ($a) { Remove-Item x }"])
def test_a_write_inside_a_block_is_still_refused_whole(project, native, command) -> None:
    assert _decide(project, command)["reason_code"] == "unknown_effect_targets"
