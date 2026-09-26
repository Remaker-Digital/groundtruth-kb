"""The effect gate's Git rule follows every command a shell line runs (c115).

A direct Git effect must go through the ordinary gt lifecycle. Before c115 the rule missed a Git effect chained inside a
nested shell (`bash -c 'cd repo && git commit'`) or after cmd's single `&` separator, which is also the background
operator of bash and PowerShell 7. These cases pin the refusal of those forms, the rule's own fail-closed refusal of
commands it cannot inspect, and the read-only chains and redirections (`2>&1`, `>&2`, `|&`) that stay allowed. The gate
classifies command text only; no repository is touched here.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate as gate


def _decide(tmp_path: Path, command: str) -> dict[str, object]:
    return gate.gate_decision({"cwd": str(tmp_path), "tool_name": "Bash", "tool_input": {"command": command}})


@pytest.mark.parametrize(
    "command",
    [
        "bash -c 'echo ok && git commit -m x'",
        "bash -c 'cd repo; git push'",
        "bash -c 'echo ok & git commit -m x'",
        'cmd /c "echo ok & git commit -m x"',
        "cmd /c echo ok & git tag v1",
        "echo ok & git commit -m x",
        "pwsh -Command 'Set-Location x; git reset --hard'",
    ],
)
def test_git_effects_chained_in_nested_shells_or_after_a_single_ampersand_are_refused(
    tmp_path: Path, command: str
) -> None:
    result = _decide(tmp_path, command)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"


@pytest.mark.parametrize(
    "command",
    ["cmd /c " * 5 + "echo ok", "cmd /c", 'cmd /c "echo ok & pwsh -EncodedCommand ZwB0AA=="'],
)
def test_the_git_rule_refuses_commands_it_cannot_inspect(tmp_path: Path, command: str) -> None:
    assert gate._direct_git_effect_from_payload({"tool_name": "Bash", "tool_input": {"command": command}}) == (
        gate.UNINSPECTABLE_SHELL_COMMAND
    )
    assert _decide(tmp_path, command)["reason_code"] == "direct_git_effect_requires_lifecycle"


@pytest.mark.parametrize(
    "command",
    [
        "git status 2>&1",
        "git log --oneline | head -5",
        "bash -c 'git status && git log -1'",
        "cmd /c git status & git diff",
        'curl "http://x/?a=1&b=2"',
        "git status |& cat",
    ],
)
def test_read_only_git_chains_and_redirections_stay_allowed(tmp_path: Path, command: str) -> None:
    assert _decide(tmp_path, command) == {}
