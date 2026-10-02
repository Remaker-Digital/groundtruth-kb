"""The shared effect gate reads each output redirection's target and judges it like a direct write (c123, B149).

Before c123 a redirect to a file named no target the gate could check, so every command carrying one was refused whole
(unknown_effect_targets), even into the context's own scratch, and a redirect after a safe-prefix read was not judged at
all until c122. Batch design WP1, B149 (owner 2026-09-30 20:11 "Batch it"): the word after each output redirection is the
write's target; a duplication or a null or standard device writes no file; a word the shell supplies when it runs is
refused whole and named; a redirection with no word, or in a command whose quotes do not close, stays unreadable. Every
command here is judged, never run; the native effect check is a recorder.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate

OWN = "SENV-00000000000000000000000000000c23"


@pytest.fixture(autouse=True)
def _own_context(monkeypatch):
    # The gate prefers the harness's own context variable to the payload's session id; these payloads carry the id.
    monkeypatch.delenv("GTKB_NATIVE_CONTEXT_ID", raising=False)
    monkeypatch.setattr(effect_gate, "_bound_session_context", lambda payload, project: (OWN, True))


class _NativeCheck:
    """Stands in for `gt bridge check-effects`: answers by scope the way the native check does."""

    def __init__(self, claimed: bool) -> None:
        self.claimed = claimed
        self.calls: list[list[str]] = []

    def __call__(self, argv, **_kwargs):
        self.calls.append(list(argv))
        paths = [argv[index + 1] for index, token in enumerate(argv) if token == "--path"]
        if all(path.startswith(f"scratchpad/{OWN}/") for path in paths):
            return subprocess.CompletedProcess(argv, 0, json.dumps({"status": "current", "scope": "scratch"}), "")
        if self.claimed:
            return subprocess.CompletedProcess(
                argv, 0, json.dumps({"status": "current", "scope": "implementation"}), ""
            )
        refusal = "Error: implementation_claim_required: Tool work edits require a live implementation-report claim\n"
        return subprocess.CompletedProcess(argv, 1, "", refusal)

    def paths(self) -> list[list[str]]:
        return [[call[index + 1] for index, token in enumerate(call) if token == "--path"] for call in self.calls]


def _payload(project: Path, command: str) -> dict:
    return {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": "redirects-test",
        "cwd": str(project),
        "project_root": str(project),
    }


# Every operator form names its target, a descriptor before the operator included.
OPERATOR_FORMS = [
    ("echo x > out.txt", ["out.txt"]),
    ("echo x >> out.txt", ["out.txt"]),
    ("echo x 1> out.txt", ["out.txt"]),
    ("git log 2> err.txt", ["err.txt"]),
    ("git log 2>> err.txt", ["err.txt"]),
    ("rg x *> out.txt", ["out.txt"]),
    ("rg x *>> out.txt", ["out.txt"]),
    ("echo x &> out.txt", ["out.txt"]),
    ("echo x &>> out.txt", ["out.txt"]),
    ("echo x >| out.txt", ["out.txt"]),
    ("echo x >& out.txt", ["out.txt"]),
    ("echo x >f", ["f"]),
    ("echo x 2>f", ["f"]),
    ("echo x>out.txt", ["out.txt"]),
    ("echo x 2>err.txt 1>out.txt", ["err.txt", "out.txt"]),
    ("git diff > patch.txt 2>&1", ["patch.txt"]),
    ("echo x > 'my file.txt'", ["my file.txt"]),
    ('echo x > "my file.txt"', ["my file.txt"]),
    ("echo x >> 'a b'.txt", ["a b.txt"]),
]


@pytest.mark.parametrize(("command", "targets"), OPERATOR_FORMS)
def test_every_operator_form_names_its_target(tmp_path, command, targets):
    assert effect_gate.changed_paths(_payload(tmp_path, command)) == (targets, True)


# The batch design's probe of the c121 gate: a safe-prefix read with a redirect is a write naming its target.
PROBED_SAFE_PREFIX = [
    ("Get-Content a.txt > b.txt", "b.txt"),
    ("git diff > patch.txt", "patch.txt"),
    ("git log 2> err.txt", "err.txt"),
    ("rg x *> out.txt", "out.txt"),
    ("python -m pytest -q > out.txt", "out.txt"),
    ('pwsh -c "Get-Content a.txt > b.txt"', "b.txt"),
]


@pytest.mark.parametrize(("command", "target"), PROBED_SAFE_PREFIX)
def test_each_probed_safe_prefix_redirect_is_a_write_naming_its_target(tmp_path, command, target):
    assert effect_gate.changed_paths(_payload(tmp_path, command)) == ([target], True)


NO_FILE = [
    "echo x >&2",
    "echo x 2>&1",
    "echo x *>&1",
    "echo x >&-",
    "Get-Content a.txt > $null",
    "Get-Content a.txt 2>$null",
    "echo x > NUL",
    "echo x > NUL:",
    "echo x > /dev/null",
    "echo x > /dev/stdout",
    "echo x > /dev/stderr",
    "echo 'a > b'",
    'echo "a > b"',
]


@pytest.mark.parametrize("command", NO_FILE)
def test_duplications_and_devices_name_no_target(tmp_path, command):
    assert effect_gate.changed_paths(_payload(tmp_path, command))[0] == []


# M13 host I, Q6 on c120 (2026-09-29 09:56:35Z), verbatim.
HOST_I_NESTED = 'cmd /c "echo m13 > m13-nested-probe.txt"'


def test_host_is_nested_redirect_names_its_file_and_needs_a_claim(tmp_path, monkeypatch):
    assert effect_gate.changed_paths(_payload(tmp_path, HOST_I_NESTED)) == (["m13-nested-probe.txt"], True)
    native = _NativeCheck(claimed=False)
    monkeypatch.setattr(effect_gate.subprocess, "run", native)
    refused = effect_gate.gate_decision(_payload(tmp_path, HOST_I_NESTED))
    assert refused["reason_code"] == "implementation_claim_required", refused
    assert "m13-nested-probe.txt" in refused["reason"]
    assert native.paths() == [["m13-nested-probe.txt"]]


def test_a_claimless_redirect_into_the_contexts_own_scratch_is_allowed(tmp_path, monkeypatch):
    native = _NativeCheck(claimed=False)
    monkeypatch.setattr(effect_gate.subprocess, "run", native)
    command = f"git diff > scratchpad/{OWN}/patch.txt"
    assert effect_gate.gate_decision(_payload(tmp_path, command)) == {}
    assert native.paths() == [[f"scratchpad/{OWN}/patch.txt"]]


@pytest.mark.parametrize(
    ("command", "word"),
    [
        ("echo x > $out", "$out"),
        ("echo x > ${HOME}/notes.txt", "${HOME}/notes.txt"),
        ('Get-Content a.txt > "$d\\b.txt"', '"$d\\b.txt"'),
        ("echo x > ~/notes.txt", "~/notes.txt"),
    ],
)
def test_a_redirect_to_a_word_the_shell_supplies_is_refused_whole_and_named(tmp_path, monkeypatch, command, word):
    monkeypatch.setattr(effect_gate.subprocess, "run", lambda *_a, **_k: pytest.fail("the native check must not run"))
    result = effect_gate.gate_decision(_payload(tmp_path, command))
    assert result["reason_code"] == "unknown_effect_targets", result
    assert word in result["reason"] and "-LiteralPath" in result["reason"]


@pytest.mark.parametrize(
    "command", ["echo x >", "echo x > 'unclosed", 'echo x > "unclosed', "Set-Content a.txt x; echo y >"]
)
def test_a_redirect_the_gate_cannot_read_is_refused_whole(tmp_path, monkeypatch, command):
    monkeypatch.setattr(effect_gate.subprocess, "run", lambda *_a, **_k: pytest.fail("the native check must not run"))
    assert effect_gate.changed_paths(_payload(tmp_path, command)) == ([], True)
    result = effect_gate.gate_decision(_payload(tmp_path, command))
    assert result["reason_code"] == "unknown_effect_targets", result


def test_every_write_in_a_command_with_a_redirect_is_checked(tmp_path, monkeypatch):
    native = _NativeCheck(claimed=True)
    monkeypatch.setattr(effect_gate.subprocess, "run", native)
    command = "Set-Content a.txt x; git diff > patch.txt; Add-Content b.txt y"
    assert effect_gate.gate_decision(_payload(tmp_path, command)) == {}
    assert native.paths() == [["a.txt", "b.txt", "patch.txt"]]
