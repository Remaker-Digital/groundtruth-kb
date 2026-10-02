"""The owner's levers over project authorization are refused to every agent context (c123, owner decision E1).

GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001: a project's authorization is the owner's ordering choice. Three CLI
commands act as authorization: gt projects set-authorization; gt projects move-item, which can carry intake work into an
authorized project; and gt projects record when it creates an execution project, which starts authorized. The service
does not authenticate its callers, so the effect gate is where an agent harness is stopped. Owner decision 2026-10-01
05:32 (E1, answer B, owner-only): the gate refuses all three in every harness context, bound or not, wherever they appear
in a command, like the owner operations; the owner runs them in their own terminal. Program creation, amendments of
existing records and the nested dependency and formal-link records stay with agents. Before c123, gt projects move-item
was refused only by accident (move-item is also a PowerShell write cmdlet's name) with a misleading reason. The gate
classifies command text only; no authority is contacted.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate as gate

RECORD = "--fields-file fields.json --actor agent --change-reason test"
SET_AUTHORIZATION = "gt projects set-authorization PROJECT-X --authorization authorized --expected-version 2 " + RECORD
MOVE_ITEM = (
    "gt projects move-item --work-item-id WI-1 --from-project PROJECT-GTKB-NEW-WORK-INTAKE --to-project PROJECT-X "
    "--expected-version 3 --actor agent --change-reason test"
)
CREATE = "gt projects record --id PROJECT-NEW " + RECORD


@pytest.fixture(autouse=True)
def _no_native_check(monkeypatch):
    monkeypatch.delenv("GTKB_NATIVE_CONTEXT_ID", raising=False)
    monkeypatch.setattr(gate.subprocess, "run", lambda *_a, **_k: pytest.fail("no CLI call decides an owner lever"))


def _decide(tmp_path: Path, command: object, tool_name: str = "Bash", **extra: object) -> dict[str, object]:
    payload = {"cwd": str(tmp_path), "tool_name": tool_name, "tool_input": {"command": command}, **extra}
    return gate.gate_decision(payload)


LEVERS = [
    (SET_AUTHORIZATION, "gt projects set-authorization"),
    (SET_AUTHORIZATION.replace("authorized", '"not authorized"', 1), "gt projects set-authorization"),
    (MOVE_ITEM, "gt projects move-item"),
    (CREATE + " --expected-version 0", "gt projects record"),
    (CREATE + " --expected-version=0", "gt projects record"),
    (CREATE + " --expected-version 0 --kind project", "gt projects record"),
    (CREATE + " --kind=project --expected-version 0", "gt projects record"),
    # The kind omitted, the version missing, or a version the gate cannot read: creation is assumed (fail closed).
    (CREATE, "gt projects record"),
    (CREATE + " --expected-version $version", "gt projects record"),
    (CREATE + " --expected-version 4 --expected-version 0", "gt projects record"),
    (CREATE + " --expected-version 0 --kind $kind", "gt projects record"),
    ("gt --config groundtruth.toml " + MOVE_ITEM.removeprefix("gt "), "gt projects move-item"),
    ("python -m groundtruth_kb " + SET_AUTHORIZATION.removeprefix("gt "), "gt projects set-authorization"),
    ("py -3 -B -m groundtruth_kb " + MOVE_ITEM.removeprefix("gt "), "gt projects move-item"),
    (r"E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe " + MOVE_ITEM.removeprefix("gt "), "gt projects move-item"),
]


@pytest.mark.parametrize(("command", "lever"), LEVERS)
@pytest.mark.parametrize("tool_name", ["Bash", "Shell"])
def test_owner_levers_are_refused(tmp_path: Path, command: str, lever: str, tool_name: str) -> None:
    result = _decide(tmp_path, command, tool_name)

    assert result["decision"] == "block"
    assert result["reason_code"] == "owner_lever_only"
    reason = str(result["reason"])
    assert reason.startswith(lever)
    assert "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001" in reason and "own terminal" in reason
    assert re.search(r"\(D\d+\)", reason) is None


@pytest.mark.parametrize(
    "command",
    [
        f'pwsh -NoProfile -Command "{MOVE_ITEM}"',
        f'cmd /c "{SET_AUTHORIZATION}"',
        f"bash -c '{CREATE} --expected-version 0'",
        f"Write-Output ok; {MOVE_ITEM}",
        f"echo ok && {MOVE_ITEM}",
        f"echo ok & {MOVE_ITEM}",
        MOVE_ITEM.split(),
        f"& {{ {SET_AUTHORIZATION} }}",
        f'iex "{MOVE_ITEM}"',
        f"uv run {MOVE_ITEM}",
        "Start-Process gt -ArgumentList 'projects','set-authorization','PROJECT-X','--authorization','authorized',"
        "'--expected-version','2','--actor','agent','--change-reason','test'",
        # A lever with a redirect is refused like any other: it is never asked.
        f"{MOVE_ITEM} > moved.txt",
    ],
)
def test_nested_chained_launched_and_shell_free_levers_are_refused(tmp_path: Path, command: object) -> None:
    result = _decide(tmp_path, command)

    assert result["decision"] == "block"
    assert result["reason_code"] == "owner_lever_only"


def test_a_bound_context_is_refused_as_an_unbound_one_is(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "bound-context")
    result = _decide(tmp_path, MOVE_ITEM, session_id="bound-context")

    assert result["reason_code"] == "owner_lever_only"


def test_move_item_gets_its_true_reason_and_never_unknown_effect_targets(tmp_path: Path) -> None:
    # move-item also names a PowerShell write cmdlet, so the write rule alone sees a write whose target it cannot read;
    # the lever rule runs before it.
    payload = {"cwd": str(tmp_path), "tool_name": "Bash", "tool_input": {"command": MOVE_ITEM}}
    assert gate.changed_paths({**payload, "project_root": str(tmp_path)}) == ([], True)

    result = gate.gate_decision(payload)

    assert result["reason_code"] == "owner_lever_only"
    assert result["reason_code"] != "unknown_effect_targets"


def test_a_lever_chained_with_a_git_effect_gets_the_git_rule_first(tmp_path: Path) -> None:
    result = _decide(tmp_path, f"{SET_AUTHORIZATION}; git commit -m x")

    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"


@pytest.mark.parametrize(
    "command",
    [
        "gt projects show PROJECT-X",
        "gt projects list --kind project",
        "gt projects readiness PROJECT-X",
        "gt projects --help",
        CREATE + " --expected-version 4",
        "gt projects record --id PROGRAM-NEW --kind program --expected-version 0 " + RECORD,
        "gt projects dependencies record --id DEP-NEW --expected-version 0 " + RECORD,
        "gt projects formal-links record --id LINK-NEW --expected-version 0 " + RECORD,
        "gt backlog record --id WI-NEW --project-id PROJECT-GTKB-NEW-WORK-INTAKE --expected-version 0 " + RECORD,
        "gt projects prepare-commit PROJECT-X --native-context-id ctx --expected-version 3",
        "Write-Output 'gt projects move-item is the owner''s'",
    ],
)
def test_reads_amendments_and_program_creation_stay_allowed(tmp_path: Path, command: str) -> None:
    assert _decide(tmp_path, command) == {}


@pytest.mark.parametrize(
    "command",
    ["pwsh -EncodedCommand ZwB0AA==", "cmd /c", "& $gt projects move-item", "gt projects $action PROJECT-X"],
)
def test_the_lever_rule_refuses_commands_it_cannot_inspect_on_its_own(
    tmp_path: Path, command: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The Git and owner-operation rules run first and refuse these too; without them the lever rule must still refuse.
    assert gate._owner_lever(command) == gate.UNINSPECTABLE_SHELL_COMMAND
    monkeypatch.setattr(gate, "_direct_git_effect_from_payload", lambda payload: None)
    monkeypatch.setattr(gate, "_owner_operation_from_payload", lambda payload: None)

    result = _decide(tmp_path, command)

    assert result["reason_code"] == "owner_lever_only"
    assert "may hide an owner lever" in str(result["reason"])


@pytest.mark.parametrize(
    ("arguments", "creates"),
    [
        (["--expected-version", "0"], True),
        (["--expected-version=0"], True),
        (["--expected-version", "0", "--kind", "project"], True),
        ([], True),
        (["--expected-version"], True),
        (["--expected-version", "$v"], True),
        (["--expected-version", "1"], False),
        (["--expected-version", "0", "--kind", "program"], False),
        (["--expected-version", "0", "--kind=program"], False),
        (["--expected-version", "0", "--kind", "'program'"], False),
        (["--kind", "program", "--kind", "project", "--expected-version", "0"], True),
    ],
)
def test_creation_is_read_from_the_version_and_the_kind(arguments: list[str], creates: bool) -> None:
    assert gate._creates_execution_project(["projects", "record", "--id", "PROJECT-NEW", *arguments]) is creates
