"""The shared effect gate judges every PowerShell, .NET and Python write form as a write (c121).

M13 on c120 (4ab57fd), the GTKB Home's bound Q1 session, 2026-09-29 07:26: `Add-Content -Path m13-sentinel\\sentinel.txt
-Value "m13-home-bound"` ran with no claim and appended to the integration sentinel. The write signal
(MUTATING_COMMAND_RE) did not list add-content, clear-content or rename-item although the verb tables that read their
targets did, so the gate judged those commands reads. The builder's audit of the installed gate found 38 write forms
judged reads (cmdlets, aliases and cmd built-ins, .NET calls, a $(...) inside a string, Python file operations) and two
commands whose claim check covered one write and not another. Owner decisions 2026-09-29 07:32 ("Fix first: c121") and
07:56 ("All forms found"): every one needs a claim, and a command carrying a write whose target the gate cannot read is
refused whole (unknown_effect_targets). No authority is contacted: the native effect check is replaced by a recorder.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate

HOME_Q1 = 'Add-Content -Path m13-sentinel\\sentinel.txt -Value "m13-home-bound"'


@pytest.fixture(autouse=True)
def _payload_context_only(monkeypatch):
    # The gate prefers the harness's own context variable to the payload's session id; these payloads carry the id.
    monkeypatch.delenv("GTKB_NATIVE_CONTEXT_ID", raising=False)


def _payload(project: Path, command: str) -> dict:
    return {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": "write-forms-test",
        "cwd": str(project),
        "project_root": str(project),
    }


def _judged(project: Path, command: str) -> tuple[list[str], bool]:
    return effect_gate.changed_paths(_payload(project, command))


class _NativeCheck:
    """Stands in for `gt bridge check-effects`: records each call and answers as a claim would."""

    def __init__(self, claimed: bool) -> None:
        self.claimed = claimed
        self.calls: list[list[str]] = []

    def __call__(self, argv, **_kwargs):
        self.calls.append(list(argv))
        if self.claimed:
            answer = {"status": "current", "scope": "implementation"}
            return subprocess.CompletedProcess(argv, 0, json.dumps(answer), "")
        return subprocess.CompletedProcess(argv, 1, "", "implementation_claim_required: no claim covers the path")


def _checked_paths(argv: list[str]) -> list[str]:
    return [argv[index + 1] for index, token in enumerate(argv) if token == "--path"]


def test_the_home_q1_append_needs_a_claim_and_names_its_target(tmp_path, monkeypatch):
    assert _judged(tmp_path, HOME_Q1) == (["m13-sentinel/sentinel.txt"], True)
    unclaimed = _NativeCheck(claimed=False)
    monkeypatch.setattr(effect_gate.subprocess, "run", unclaimed)
    refused = effect_gate.gate_decision(_payload(tmp_path, HOME_Q1))
    assert refused["decision"] == "block" and refused["reason_code"] == "native_effect_refused", refused
    assert "implementation_claim_required" in refused["reason"]
    assert [_checked_paths(call) for call in unclaimed.calls] == [["m13-sentinel/sentinel.txt"]]
    claimed = _NativeCheck(claimed=True)
    monkeypatch.setattr(effect_gate.subprocess, "run", claimed)
    assert effect_gate.gate_decision(_payload(tmp_path, HOME_Q1)) == {}
    assert [_checked_paths(call) for call in claimed.calls] == [["m13-sentinel/sentinel.txt"]]


# Each form the audit found judged a read, with the targets the gate now checks (probe-installed-gate-20260929T074338).
WRITES_WITH_TARGETS = [
    ("Clear-Content -Path notes.txt", ["notes.txt"]),
    ("Rename-Item -Path a.txt -NewName b.txt", ["a.txt", "b.txt"]),
    ("ac notes.txt x", ["notes.txt"]),
    ("clc notes.txt", ["notes.txt"]),
    ("del notes.txt", ["notes.txt"]),
    ("erase notes.txt", ["notes.txt"]),
    ("ri notes.txt", ["notes.txt"]),
    ("ren a.txt b.txt", ["a.txt", "b.txt"]),
    ("rni a.txt b.txt", ["a.txt", "b.txt"]),
    ("copy a.txt b.txt", ["a.txt", "b.txt"]),
    ("cpi a.txt b.txt", ["a.txt", "b.txt"]),
    ("move a.txt b.txt", ["a.txt", "b.txt"]),
    ("mi a.txt b.txt", ["a.txt", "b.txt"]),
    ("ni notes.txt", ["notes.txt"]),
    ("mkdir newdir", ["newdir"]),
    ("md newdir", ["newdir"]),
    ("rd olddir", ["olddir"]),
    ("rmdir olddir", ["olddir"]),
    ("Get-Process | Export-Csv -Path procs.csv", ["procs.csv"]),
    ("Get-Process | epcsv procs.csv", ["procs.csv"]),
    ("Get-Process | Export-Clixml procs.xml", ["procs.xml"]),
    ("Get-Process | Tee-Object -FilePath procs.txt", ["procs.txt"]),
    ("Start-Transcript -Path log.txt", ["log.txt"]),
    ("Set-ItemProperty -Path notes.txt -Name IsReadOnly -Value $true", ["notes.txt"]),
    ("sp notes.txt IsReadOnly $true", ["notes.txt"]),
    ("Set-Acl -Path notes.txt -AclObject $acl", ["notes.txt"]),
    ("Unblock-File -Path notes.txt", ["notes.txt"]),
    ("Expand-Archive -Path a.zip -DestinationPath out", ["out"]),
    ("Expand-Archive -Path a.zip out", ["out"]),
    ("Expand-Archive a.zip", ["."]),
    ("Compress-Archive -Path src -DestinationPath a.zip", ["a.zip"]),
    ("Compress-Archive src a.zip", ["a.zip"]),
    ("Invoke-WebRequest -Uri https://example.invalid -OutFile page.html", ["page.html"]),
    ("iwr https://example.invalid -OutFile page.html", ["page.html"]),
    ('Write-Output "$(Set-Content notes.txt x)"', ["notes.txt"]),
    # cmd switches and POSIX flags are not targets.
    ("mkdir -p a/b", ["a/b"]),
    ("rmdir /s /q olddir", ["olddir"]),
    ("copy /y a.txt b.txt", ["a.txt", "b.txt"]),
    ("mkdir.exe newdir", ["newdir"]),
]


@pytest.mark.parametrize(("command", "targets"), WRITES_WITH_TARGETS)
def test_each_write_form_the_audit_found_is_a_write_with_its_targets(tmp_path, command, targets):
    assert _judged(tmp_path, command) == (sorted(targets), True)


# Writes whose target the gate does not read: refused whole before the native check.
UNREAD_WRITES = [
    "[IO.File]::WriteAllText('notes.txt', 'x')",
    '[System.IO.File]::AppendAllText("notes.txt", "x")',
    "[IO.File]::Delete('notes.txt')",
    "[IO.File]::Move('a.txt', 'b.txt')",
    "[IO.Directory]::CreateDirectory('newdir')",
    "$w = [IO.StreamWriter]::new('notes.txt'); $w.WriteLine('x'); $w.Close()",
    "$w = New-Object System.IO.StreamWriter('notes.txt'); $w.Close()",
    "(Get-Item notes.txt).Delete()",
    "(Get-Item notes.txt).IsReadOnly = $true",
    "$doc.Save('config.xml')",
    "1..2 | ForEach-Object { Add-Content -Path notes.txt -Value $_ }",
    "Get-ChildItem *.tmp | Remove-Item",
    "python -c \"open('notes.txt','a').write('x')\"",
    "python -c \"from pathlib import Path; Path('notes.txt').write_bytes(b'x')\"",
    "python -c \"import os; os.remove('notes.txt')\"",
    "python -c \"import shutil; shutil.copy('a.txt','notes.txt')\"",
    "python -c \"from pathlib import Path; Path('x').open('a').write('y')\"",
    "python -c \"from pathlib import Path; Path('a.txt').rename('b.txt')\"",
    "python -X utf8 -c \"import shutil; shutil.rmtree('build')\"",
    "Set-Location sub; python -c \"import os; os.makedirs('d')\"",
    "E:\\tools\\python.exe -c \"import os; os.unlink('x')\"",
]


@pytest.mark.parametrize("command", UNREAD_WRITES)
def test_a_write_whose_target_is_not_read_is_refused_whole(tmp_path, monkeypatch, command):
    assert _judged(tmp_path, command) == ([], True)
    monkeypatch.setattr(effect_gate.subprocess, "run", lambda *_a, **_k: pytest.fail("the native check must not run"))
    result = effect_gate.gate_decision(_payload(tmp_path, command))
    assert result["decision"] == "block" and result["reason_code"] == "unknown_effect_targets", result


# A claim check covers every write or none: one unread write makes the whole command unreadable.
PAIRED_WITH_AN_UNREAD_WRITE = [
    "Set-Content a.txt x; 1..2 | % { Set-Content notes.txt $_ }",
    "Set-Content a.txt x; echo y > notes.txt",
    "Set-Content a.txt x; [IO.File]::Delete('notes.txt')",
    "Set-Content a.txt ([IO.File]::Delete('notes.txt'))",
    "Set-Content a.txt x; python -c \"open('notes.txt','a')\"",
    "Copy-Item a.txt b.txt; if ($true) { Remove-Item notes.txt }",
]


@pytest.mark.parametrize("command", PAIRED_WITH_AN_UNREAD_WRITE)
def test_a_readable_write_paired_with_an_unread_write_is_refused_whole(tmp_path, monkeypatch, command):
    assert _judged(tmp_path, command) == ([], True)
    claimed = _NativeCheck(claimed=True)
    monkeypatch.setattr(effect_gate.subprocess, "run", claimed)
    result = effect_gate.gate_decision(_payload(tmp_path, command))
    assert result["reason_code"] == "unknown_effect_targets" and not claimed.calls, result


def test_every_readable_write_in_a_command_is_checked(tmp_path, monkeypatch):
    command = "Add-Content a.txt x; Rename-Item b.txt c.txt; del d.txt; mkdir e"
    assert _judged(tmp_path, command) == (["a.txt", "b.txt", "c.txt", "d.txt", "e"], True)
    claimed = _NativeCheck(claimed=True)
    monkeypatch.setattr(effect_gate.subprocess, "run", claimed)
    assert effect_gate.gate_decision(_payload(tmp_path, command)) == {}
    assert [_checked_paths(call) for call in claimed.calls] == [["a.txt", "b.txt", "c.txt", "d.txt", "e"]]


READS = [
    "Get-Content notes.txt",
    "[IO.File]::ReadAllText('notes.txt')",
    "[IO.File]::Exists('notes.txt')",
    "[IO.Directory]::GetFiles('.')",
    "'abc'.Replace('a','b')",
    "[Security.Cryptography.SHA256]::Create().ComputeHash([byte[]]@(1))",
    "Import-Csv procs.csv",
    "Write-Output 'Add-Content is a cmdlet'",
    'Write-Output "Today is $(Get-Date)"',
    "Test-Path notes.txt",
    "Invoke-WebRequest -Uri https://example.invalid",
    "Invoke-RestMethod http://127.0.0.1:8765/v1/status",
    "Get-ChildItem | Sort-Object LastWriteTime",
    "Get-ChildItem | Where-Object { $_.Attributes -eq 'Hidden' }",
    "echo copy",
    "git log --grep=del --oneline",
    "md5sum notes.txt",
    "python -c \"print(open('notes.txt').read())\"",
    "python -c \"print('a'.replace('a', 'b'))\"",
    'python -c "import webbrowser; print(webbrowser.open)"',
    "python -c \"import os; print(os.getcwd(), os.path.exists('x'))\"",
]


@pytest.mark.parametrize("command", READS)
def test_reads_stay_reads(tmp_path, command):
    assert _judged(tmp_path, command)[1] is False


def test_the_write_signal_and_the_target_tables_list_the_same_verbs():
    """The cause of the Home Q1 bypass was two lists that drifted apart; every table verb must be a write signal."""
    verbs = (
        effect_gate._POWERSHELL_PATH_ARG_VERBS
        | effect_gate._POWERSHELL_BOTH_PATHS_VERBS
        | effect_gate._POWERSHELL_DESTINATION_VERBS
        | effect_gate._DUAL_SYNTAX_WRITE_VERBS
        | set(effect_gate._POWERSHELL_WRITE_ALIASES)
    )
    for verb in sorted(verbs):
        command = f"{verb} -OutFile target.txt target.txt" if verb in {"iwr", "irm"} else f"{verb} target.txt x"
        assert effect_gate._has_mutating_signal(command), verb
        classification = effect_gate._classify_command_verb(command.split())
        assert classification is not None and classification[0](classification[1]), verb
    for verb in sorted(effect_gate._POWERSHELL_OUTFILE_VERBS):
        assert effect_gate._has_mutating_signal(f"{verb} -Uri u -OutFile target.txt"), verb
        assert not effect_gate._has_mutating_signal(f"{verb} -Uri u"), verb
