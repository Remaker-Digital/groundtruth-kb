# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-7657: the ``gt projects`` authorization subcommands are absent.

This file exercised ``gt projects authorizations`` and its coverage output.
That command and its four siblings were removed with the authorization record.

Non-vacuity: an absence assertion passes trivially if the symbol name is
misspelled or the import silently failed, so every test below pairs the absent
names with a control that is still present on the same object. If the control
fails, the absence claims are not trusted.
"""

from __future__ import annotations

import click
from groundtruth_kb.cli import main

REMOVED_SUBCOMMANDS = (
    "authorize",
    "authorizations",
    "show-authorization",
    "revoke-authorization",
    "complete-authorization",
)


def test_control_subcommand_is_registered() -> None:
    """Non-vacuity guard: the group imported and still registers real commands."""
    assert "show" in main.get_command(click.Context(main), "projects").commands
    assert "record" in main.get_command(click.Context(main), "projects").commands


def test_authorization_subcommands_are_absent() -> None:
    assert "show" in main.get_command(click.Context(main), "projects").commands, "control subcommand missing"
    for name in REMOVED_SUBCOMMANDS:
        assert name not in main.get_command(click.Context(main), "projects").commands, (
            f"gt projects {name} should have been removed"
        )
