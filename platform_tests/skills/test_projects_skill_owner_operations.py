"""The projects skill shows its owner operations only where it states the boundary.

Under GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, changing a project's authorization, moving a work item between
projects and creating an execution project are owner operations: agent harnesses refuse them, and the owner runs them
in their own terminal. A section that shows one of these commands without that boundary teaches an agent to run a
command the effect gate refuses.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".harness-baseline-configuration/skills/gtkb-projects/SKILL.md"
BOUNDARY = "## Owner operations"
PROGRAM_KIND = re.compile(r"--kind[ =]program\b")
NEW_RECORD = re.compile(r"--expected-version[ =]0\b")


def _sections(text: str) -> dict[str, str]:
    """Level-two sections by heading; the frontmatter, title and lead text form the '' section."""
    sections: dict[str, list[str]] = {"": []}
    heading = ""
    for line in text.splitlines():
        if line.startswith("## "):
            heading = line.strip()
            assert heading not in sections, f"duplicate section {heading!r}"
            sections[heading] = []
        else:
            sections[heading].append(line)
    return {name: "\n".join(lines) for name, lines in sections.items()}


def _is_owner_operation(line: str) -> bool:
    """An authorization change, a move, or a `projects record` that creates a record other than a program."""
    if "set-authorization" in line or "move-item" in line:
        return True
    return "projects record" in line and bool(NEW_RECORD.search(line)) and not PROGRAM_KIND.search(line)


def _owner_operations(text: str) -> list[str]:
    """Each line of the text that names an owner operation."""
    return [line for line in text.splitlines() if _is_owner_operation(line)]


def test_the_boundary_section_states_who_runs_the_owner_operations() -> None:
    body = " ".join(_sections(SKILL.read_text(encoding="utf-8"))[BOUNDARY].split())
    assert "are owner operations" in body
    assert "Agent harnesses refuse these commands in every context" in body
    assert "state the needed change and the exact command" in body
    assert "the owner runs it in their own terminal" in body
    assert "authors BLOCKED instead" in body


def test_each_owner_operation_command_is_shown_under_the_boundary() -> None:
    lines = _owner_operations(_sections(SKILL.read_text(encoding="utf-8"))[BOUNDARY])
    assert any("gt projects set-authorization" in line and "--authorization authorized" in line for line in lines)
    assert any("gt projects set-authorization" in line and '"not authorized"' in line for line in lines)
    assert any("gt projects move-item" in line for line in lines)
    assert any("gt projects record" in line and "--kind project" in line for line in lines)


def test_no_other_section_shows_an_owner_operation() -> None:
    sections = _sections(SKILL.read_text(encoding="utf-8"))
    elsewhere = {name: _owner_operations(body) for name, body in sections.items() if name != BOUNDARY}
    assert {name: lines for name, lines in elsewhere.items() if lines} == {}


def test_agents_keep_program_creation_and_project_amendments() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert "gt projects record --id <PROGRAM-ID> --kind program" in text
    assert "gt projects record --id <PROJECT-ID> --fields-file <fields.json> --expected-version <version>" in text


def test_the_detector_tells_owner_operations_from_agent_writes() -> None:
    owner = (
        "gt projects record --id P --kind project --expected-version 0\n"
        "gt projects record --id P --expected-version=0\n"
        "gt projects move-item --work-item-id WI-1 --to-project P\n"
        "gt projects set-authorization P --authorization authorized\n"
    )
    agent = (
        "gt projects record --id P --kind program --expected-version 0\n"
        "gt projects record --id P --expected-version 4\n"
        "gt projects formal-links record --id L --expected-version 0\n"
        "gt projects dependencies record --id D --expected-version 0\n"
    )
    assert _owner_operations(owner) == owner.splitlines()
    assert _owner_operations(agent) == []
