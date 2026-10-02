"""c123 (batch design WP5, G44(c)): the session group offers no envelope route.

DCL-SESSION-ROLE-RESOLUTION-001 requires that no role-change or override route exists. The session group has exactly
three commands (bind, show and scratch-teardown), and the retired envelope route is not one of them. This replaces
test_session_envelope_cli_provenance.py, whose ten cases called that route and passed only because click refused it.
"""

from __future__ import annotations

from click.testing import CliRunner
from groundtruth_kb.cli import main


def _listed_commands(help_text: str) -> list[str]:
    lines = help_text.splitlines()
    start = lines.index("Commands:") + 1
    return [line.split()[0] for line in lines[start:] if line.startswith("  ") and not line.startswith("   ")]


def test_session_group_offers_no_envelope_route() -> None:
    runner = CliRunner()

    listed = runner.invoke(main, ["session", "--help"])
    retired = runner.invoke(main, ["session", "envelope", "open", "--json"])
    control = runner.invoke(main, ["session", "bind", "--help"])

    assert listed.exit_code == 0, listed.output
    assert _listed_commands(listed.output) == ["bind", "scratch-teardown", "show"]
    assert retired.exit_code == 2, retired.output
    assert "No such command 'envelope'" in retired.output
    assert control.exit_code == 0, control.output
    assert "--native-context-id" in control.output
