"""CLI ``click.Choice`` <-> ``TOPIC_TYPES`` parity tests (WI-4819).

Spec-derived regression for the vocabulary-drift defect where
``gt session topic open`` / ``close`` hardcoded a 5-member ``click.Choice``
that omitted ``ops`` while the canonical activity vocabulary
``envelope.TOPIC_TYPES`` has six members. Sourcing the CLI choices from
``TOPIC_TYPES`` repairs the bug class: a future addition to ``TOPIC_TYPES``
can no longer drift away from the CLI parse surface.

Authority: SPEC-TOPIC-ENVELOPE-ROUTER-001 v3 (six-member vocabulary);
DCL-TOPIC-ENVELOPE-ROUTING-001 v3 (open/close grammar enumerates ``ops``);
GOV-RELIABILITY-FAST-LANE-001. Bridge thread
``gtkb-session-topic-cli-ops-choice-drift-fix`` (GO at -002).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import types

import click
import groundtruth_kb.cli_session_handoff as cli
from click.testing import CliRunner
from groundtruth_kb.session.envelope import TOPIC_TYPES


def _topic_type_choice(command: click.Command) -> click.Choice:
    """Return the ``topic_type`` ``click.Choice`` for a topic command."""
    for param in command.params:
        if isinstance(param, click.Argument) and param.name == "topic_type":
            assert isinstance(param.type, click.Choice)
            return param.type
    raise AssertionError(f"{command.name!r} has no 'topic_type' Choice argument")


def test_topic_open_choice_equals_topic_types() -> None:
    # SPEC-TOPIC-ENVELOPE-ROUTER-001 v3: the open CLI must accept the full
    # six-member activity vocabulary, including ``ops``.
    assert set(_topic_type_choice(cli.topic_open_cmd).choices) == set(TOPIC_TYPES)


def test_topic_close_choice_equals_topic_types() -> None:
    # Same six-member vocabulary on the close surface.
    assert set(_topic_type_choice(cli.topic_close_cmd).choices) == set(TOPIC_TYPES)


def test_both_topic_choices_sourced_from_topic_types() -> None:
    # Anti-drift invariant: both commands source the identical tuple from
    # ``TOPIC_TYPES``, so a future vocabulary addition cannot drift the CLI.
    open_choices = tuple(_topic_type_choice(cli.topic_open_cmd).choices)
    close_choices = tuple(_topic_type_choice(cli.topic_close_cmd).choices)
    assert open_choices == close_choices == tuple(TOPIC_TYPES)


def test_cli_topic_open_ops_accepted(tmp_path, monkeypatch) -> None:
    # DCL-TOPIC-ENVELOPE-ROUTING-001 v3: ``ops`` is a valid open type at the CLI
    # parse surface (it raised click.BadParameter pre-fix). Runtime is stubbed
    # and the project root is an isolated tmp dir, so no real envelope state is
    # mutated.
    monkeypatch.setattr(cli, "_resolve_config", lambda ctx: types.SimpleNamespace(project_root=str(tmp_path)))
    monkeypatch.setattr("groundtruth_kb.session.envelope.open_topic", lambda *a, **k: {"type": "ops"})
    runner = CliRunner()
    accepted = runner.invoke(cli.session_group, ["topic", "open", "ops"])
    assert accepted.exit_code == 0, accepted.output
    # Negative control: an unknown type is still rejected as a usage error, and
    # the rejection lists ``ops`` among the valid choices.
    rejected = runner.invoke(cli.session_group, ["topic", "open", "definitely-not-a-type"])
    assert rejected.exit_code == 2
    assert "ops" in rejected.output


def test_cli_topic_close_ops_accepted(tmp_path, monkeypatch) -> None:
    # Same parse-surface acceptance for the close command.
    monkeypatch.setattr(cli, "_resolve_config", lambda ctx: types.SimpleNamespace(project_root=str(tmp_path)))
    monkeypatch.setattr("groundtruth_kb.session.envelope.close_topic", lambda *a, **k: {"type": "ops"})
    runner = CliRunner()
    accepted = runner.invoke(cli.session_group, ["topic", "close", "ops"])
    assert accepted.exit_code == 0, accepted.output
