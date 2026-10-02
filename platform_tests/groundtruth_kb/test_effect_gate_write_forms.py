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
        # c123 (batch design WP1, item 7): the CLI's real refusal format, click's prefix included.
        return subprocess.CompletedProcess(
            argv, 1, "", "Error: implementation_claim_required: no claim covers the path\n"
        )


def _checked_paths(argv: list[str]) -> list[str]:
    return [argv[index + 1] for index, token in enumerate(argv) if token == "--path"]


def test_the_home_q1_append_needs_a_claim_and_names_its_target(tmp_path, monkeypatch):
    assert _judged(tmp_path, HOME_Q1) == (["m13-sentinel/sentinel.txt"], True)
    unclaimed = _NativeCheck(claimed=False)
    monkeypatch.setattr(effect_gate.subprocess, "run", unclaimed)
    refused = effect_gate.gate_decision(_payload(tmp_path, HOME_Q1))
    # c123 (item 7): the native code is the reason code, and the reason carries no "Error:" prefix to double.
    assert refused["decision"] == "block" and refused["reason_code"] == "implementation_claim_required", refused
    assert refused["reason"].startswith("no claim covers the path") and "Error" not in refused["reason"]
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
    # c123 (owner decision A5, row 18): a copy's source is read, not written; these two rows named a.txt before.
    ("copy a.txt b.txt", ["b.txt"]),
    ("cpi a.txt b.txt", ["b.txt"]),
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
    # c123 (owner decision A5, row 18): the source left this row too.
    ("copy /y a.txt b.txt", ["b.txt"]),
    ("mkdir.exe newdir", ["newdir"]),
    # c123 (owner decision A5, row 18): sed's and awk's script is no target, and a copy writes only its destination.
    ("sed -i 's/a/b/' f.txt", ["f.txt"]),
    ("sed -i -e 's/a/b/' f.txt g.txt", ["f.txt", "g.txt"]),
    ("sed -i.bak -f script.sed f.txt", ["f.txt"]),
    ("sed -ni 's/a/b/p' f.txt", ["f.txt"]),
    ("sed -Ei 's/a+/b/' f.txt", ["f.txt"]),
    ("sed --in-place --expression='s/a/b/' f.txt", ["f.txt"]),
    ("awk -i inplace '{print}' f.txt", ["f.txt"]),
    ("awk -i inplace -v n=1 -f prog.awk f.txt", ["f.txt"]),
    ("cp a.txt b.txt", ["b.txt"]),
    ("cp -r src dst", ["dst"]),
    ("cp a.txt b.txt dir", ["dir"]),
    ("cp -t dir a.txt b.txt", ["dir"]),
    ("Copy-Item a.txt b.txt", ["b.txt"]),
    ("Copy-Item -Path a.txt -Destination b.txt -Recurse", ["b.txt"]),
    ("Copy-Item -Path a.txt b.txt", ["b.txt"]),
    ("Copy-Item a.txt -Destination:b.txt -ErrorAction SilentlyContinue", ["b.txt"]),
    ("Copy-ItemProperty -Path a.txt -Destination b.txt -Name p", ["b.txt"]),
    ("copy a.txt", ["."]),
    # An option the gate does not know may take the destination's place: every operand is a target, as before.
    ("Copy-Item a.txt b.txt -Frobnicate c", ["a.txt", "b.txt", "c"]),
    # c123 (owner decision A5, row 17): the system write tools name what they write.
    ("robocopy src dst /MIR", ["dst"]),
    ("robocopy src dst /PURGE", ["dst"]),
    ("robocopy src dst /MOVE", ["dst", "src"]),
    ("robocopy src dst /E /LOG:copy.log", ["copy.log", "dst"]),
    ("xcopy src dst /E /I", ["dst"]),
    ("xcopy src", ["."]),
    ("tar -czf out.tgz dir", ["out.tgz"]),
    ("tar czf out.tgz dir", ["out.tgz"]),
    ("tar -xzf in.tgz", ["."]),
    ("tar -xzf in.tgz -C outdir", ["outdir"]),
    ("tar --extract --file=in.tar --directory=outdir", ["outdir"]),
    ("7z a out.7z dir", ["out.7z"]),
    ("7z x in.7z -oout", ["out"]),
    ("7z e in.7z", ["."]),
    ("expand in.cab out.dll", ["out.dll"]),
    ("certutil -decode in.b64 out.bin", ["out.bin"]),
    ("certutil -urlcache -split -f https://example.invalid/x.exe x.exe", ["x.exe"]),
    ("mklink /J link target", ["link"]),
    ("icacls x.txt /grant user:F", ["x.txt"]),
    ("icacls dir /save acl.txt /T", ["acl.txt"]),
    ("attrib +R x.txt", ["x.txt"]),
    ("takeown /F x.txt", ["x.txt"]),
    ("fsutil file createnew x.bin 100", ["x.bin"]),
    ("fsutil hardlink create new.txt old.txt", ["new.txt"]),
    ("cipher /w:sub", ["sub"]),
    ("cipher /e x.txt", ["x.txt"]),
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
    # c123 (owner decision A5, row 17): system write tools that write what they do not name.
    "robocopy src dst /SAVE:job",
    "tar -c dir",
    "tar -xPf in.tar",
    "expand -r in.cab",
    "certutil -urlcache -f https://example.invalid/x.exe",
    "fsutil behavior set disable8dot3 1",
    "cipher /k",
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
    # c123 (B149): "Set-Content a.txt x; echo y > notes.txt" left this list: a redirect's target is now read, so both of
    # its writes are checked (test_every_readable_write_in_a_command_is_checked).
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


@pytest.mark.parametrize(
    ("command", "targets"),
    [
        ("Add-Content a.txt x; Rename-Item b.txt c.txt; del d.txt; mkdir e", ["a.txt", "b.txt", "c.txt", "d.txt", "e"]),
        # c123 (B149): moved here from PAIRED_WITH_AN_UNREAD_WRITE; the redirect's target is read.
        ("Set-Content a.txt x; echo y > notes.txt", ["a.txt", "notes.txt"]),
    ],
)
def test_every_readable_write_in_a_command_is_checked(tmp_path, monkeypatch, command, targets):
    assert _judged(tmp_path, command) == (targets, True)
    claimed = _NativeCheck(claimed=True)
    monkeypatch.setattr(effect_gate.subprocess, "run", claimed)
    assert effect_gate.gate_decision(_payload(tmp_path, command)) == {}
    assert [_checked_paths(call) for call in claimed.calls] == [targets]


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
    # c123 (owner decision A5, rows 17 and 18): the system tools' listing and display forms, and sed without -i.
    "robocopy src dst /L",
    "tar -tf in.tar",
    "tar -xOf in.tar member",
    "7z l in.7z",
    "expand -d in.cab",
    "certutil -hashfile x SHA256",
    "icacls x.txt",
    "attrib x.txt",
    "fsutil fsinfo drives",
    "fsutil file queryextents x",
    "cipher /c x.txt",
    "sed -n 'p' f.txt",
    "cat x | sed 's/a/b/'",
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
