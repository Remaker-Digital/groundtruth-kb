"""Each shared effect gate refusal names the cause the gate observed, not another one (c123, batch design WP1, item 9).

The class (iii) sweep of the batch design found fallback texts that named a cause the gate had not observed: a
traversal from a directory the shell supplies was described as a walk from here, a failed binding lookup always asked
to restore a connection, a wildcard was said to belong to another context, unknown_effect_targets named no cause at all,
an invalid payload dropped the reader's detail, and a native refusal arrived under a generic code with click's prefix
(item 7). Codes and the substrings other tests pin are kept. Every command here is judged, never run.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate

OWN = "SENV-00000000000000000000000000000c23"
# The real binding lookup, kept before the autouse fixture replaces it for the gate's own calls.
REAL_LOOKUP = effect_gate._bound_session_context


@pytest.fixture(autouse=True)
def _own_context(monkeypatch):
    monkeypatch.delenv("GTKB_NATIVE_CONTEXT_ID", raising=False)
    monkeypatch.setattr(effect_gate, "_bound_session_context", lambda payload, project: (OWN, True))
    monkeypatch.setattr(effect_gate.subprocess, "run", lambda *_a, **_k: pytest.fail("the native check must not run"))


def _decide(project: Path, command: str = "", tool: str = "Bash", data: dict | None = None) -> dict:
    return effect_gate.gate_decision(
        {
            "tool_name": tool,
            "tool_input": data if data is not None else {"command": command},
            "session_id": "refusal-text-test",
            "cwd": str(project),
            "project_root": str(project),
        }
    )


# Entry 6: unknown_effect_targets names what it observed.
UNKNOWN_TARGET_CAUSES = [
    ("[IO.File]::WriteAllText('notes.txt', 'x')", "a .NET write call ([IO.File]::WriteAllText)"),
    ("python -c \"open('notes.txt','a').write('x')\"", "a Python file write"),
    ("1..2 | ForEach-Object { Add-Content -Path notes.txt -Value $_ }", "a write inside a script block"),
    ("echo x >", "a redirect with no target the gate can read"),
    ("& { git diff --output=o.patch }", "git --output with no file the gate can read"),
]


@pytest.mark.parametrize(("command", "cause"), UNKNOWN_TARGET_CAUSES)
def test_unknown_effect_targets_names_its_cause(tmp_path, command, cause):
    result = _decide(tmp_path, command)
    assert result["reason_code"] == "unknown_effect_targets", result
    assert cause in result["reason"] and "Use an explicit tool target" not in result["reason"]


@pytest.mark.parametrize(
    ("tool", "data", "cause"),
    [
        ("Move", {"file_path": "a.txt"}, "the move tool's payload does not name both of its paths"),
        ("Copy", {"file_path": "a.txt"}, "the copy tool's payload does not name both of its paths"),
        ("Write", {}, "the write tool named no path"),
    ],
)
def test_a_tool_without_its_paths_says_so(tmp_path, tool, data, cause):
    result = _decide(tmp_path, tool=tool, data=data)
    assert result["reason_code"] == "unknown_effect_targets" and cause in result["reason"], result


# Entry 2: a walk from a directory the shell supplies has its own first sentence; the guidance tail stays.
def test_a_traversal_from_a_shell_supplied_directory_says_so(tmp_path):
    result = _decide(tmp_path, "Get-ChildItem $root -Recurse")
    assert result["reason_code"] == "context_traversal", result
    assert result["reason"].startswith("A recursive listing or search from a directory the shell supplies")
    assert "name the directory literally" in result["reason"] and "git grep" in result["reason"]
    literal = _decide(tmp_path, "Get-ChildItem . -Recurse")
    assert literal["reason"].startswith("A recursive listing or search from here walks into other contexts'")


# Entry 3: a failed binding lookup names its observed cause.
def test_an_unavailable_binding_lookup_names_its_cause(tmp_path, monkeypatch):
    timed_out = effect_gate._LookupUnavailable("gt session show did not answer within 10 seconds")
    monkeypatch.setattr(effect_gate, "_bound_session_context", lambda payload, project: (None, timed_out))
    result = _decide(tmp_path, tool="Read", data={"file_path": f"scratchpad/{OWN}/notes.txt"})
    assert result["reason_code"] == "context_isolation_unavailable", result
    assert "did not answer within 10 seconds" in result["reason"]


LOOKUP_ANSWERS = [
    (
        subprocess.CompletedProcess([], 2, "", "Traceback (most recent call last):\nboom\n"),
        "gt session show exited 2: Traceback (most recent call last):",
    ),
    (subprocess.CompletedProcess([], 0, "not json", ""), "gt session show printed output that is not a JSON object"),
    (subprocess.CompletedProcess([], 1, "", "Error: no_session_binding: none\n"), None),
]


@pytest.mark.parametrize(("completed", "cause"), LOOKUP_ANSWERS)
def test_the_binding_lookup_reports_what_it_observed(tmp_path, monkeypatch, completed, cause):
    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "lookup-test")
    monkeypatch.setattr(effect_gate.subprocess, "run", lambda *_a, **_k: completed)
    context, available = REAL_LOOKUP({}, tmp_path)
    assert context is None
    if cause is None:
        assert available is True
    else:
        assert not available and available.cause == cause


def test_a_binding_lookup_that_cannot_start_or_times_out_says_which(tmp_path, monkeypatch):
    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "lookup-test")

    def timeout(*_a, **_k):
        raise subprocess.TimeoutExpired("gt", 10)

    def missing(*_a, **_k):
        raise FileNotFoundError("gt")

    monkeypatch.setattr(effect_gate.subprocess, "run", timeout)
    assert REAL_LOOKUP({}, tmp_path)[1].cause == "gt session show did not answer within 10 seconds"
    monkeypatch.setattr(effect_gate.subprocess, "run", missing)
    assert REAL_LOOKUP({}, tmp_path)[1].cause == "gt session show could not start (FileNotFoundError)"


# Entry 5: a wildcard child reaches every context's scratch, this one's included; it belongs to no single other one.
def test_a_wildcard_child_is_said_to_reach_other_contexts(tmp_path):
    result = _decide(tmp_path, tool="Read", data={"file_path": "scratchpad/*/notes.txt"})
    assert result["reason_code"] == "foreign_context_material", result
    assert "reaches other contexts' scratch or checkouts" in result["reason"]
    assert "belongs to another context" not in result["reason"] and "its own scratch and checkout" in result["reason"]


# Entry 7: an invalid payload keeps the reader's detail.
def test_an_invalid_payload_keeps_the_readers_detail(tmp_path):
    result = effect_gate.gate_decision({effect_gate.INVALID_HOOK_PAYLOAD_KEY: "Hook input was empty."})
    assert result["reason_code"] == "invalid_hook_payload"
    assert result["reason"].endswith("payload: Hook input was empty.")


# Entry 4: each failure of the native effect check names its cause; the code stays effect_check_unavailable.
@pytest.mark.parametrize(
    ("behaviour", "cause"),
    [
        ("timeout", "did not answer within 10 seconds"),
        ("missing", "could not start (FileNotFoundError)"),
        ("not-json", "exited 0 but printed output that is not JSON"),
    ],
)
def test_an_unavailable_effect_check_names_its_cause(tmp_path, monkeypatch, behaviour, cause):
    def run(argv, **_kwargs):
        if behaviour == "timeout":
            raise subprocess.TimeoutExpired(argv, 10)
        if behaviour == "missing":
            raise FileNotFoundError(argv[0])
        return subprocess.CompletedProcess(argv, 0, "not json", "")

    monkeypatch.setattr(effect_gate.subprocess, "run", run)
    result = _decide(tmp_path, "Set-Content -Path notes.txt -Value x")
    assert result["reason_code"] == "effect_check_unavailable" and cause in result["reason"], result


# Entry 8 (item 7) is in platform_tests/scripts/test_implementation_start_gate.py; the emitter's prefix (B148) is in
# test_packaged_native_effect_gate.py. Here: the answer of a current check is unchanged.
def test_a_current_effect_check_still_allows(tmp_path, monkeypatch):
    answer = json.dumps({"status": "current", "scope": "implementation"})
    monkeypatch.setattr(
        effect_gate.subprocess, "run", lambda argv, **_k: subprocess.CompletedProcess(argv, 0, answer, "")
    )
    assert _decide(tmp_path, "Set-Content -Path notes.txt -Value x") == {}
