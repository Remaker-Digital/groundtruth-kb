"""The ``gt db postgres`` command group carries no PAUTH surface (WI-7743, F1).

Canon v7.7 retires project authorizations: PAUTH is gone and every reference to it is erroneous. The
``db postgres`` group was merged into ``cli.py`` after that retirement, so it never carried the
surface -- and nothing asserts that it stays that way. Today's zero is a measurement, not an
invariant: a future edit could reintroduce ``--pauth-id`` and no test would notice.

This file contains exactly one test, per the ruling at
``bridge/gtkb-wi7707-cohort-cli-postgres-group-merge-004.md`` F1. The registration half of the
originally-declared module was rejected there as duplicate coverage -- the twenty newly-passing CLI
tests in ``groundtruth-kb/tests/test_postgres_kernel.py`` exercise the registered commands directly,
which is stronger than a smoke test asserting five names. Only the unasserted property is added.

**Scope is the group, not the file.** The ruling's wording is "assert that ``cli.py`` carries zero
PAUTH surface tokens." Taken literally that is false on arrival: ``cli.py`` carries twelve such lines
today, all of them in the separate retired PAUTH command group around lines 4418 and 5584-5863, none
in the postgres group. The property the implementation report actually claimed, and the one that is
both true and worth defending, is the group-scoped one. That residual file-wide surface is a real
canon-conformance gap, but it belongs to the PAUTH command group and not to this thread.

**Behavioural, not textual.** The check introspects the live ``click`` group -- its commands, their
parameters, their help text, and their callback source -- rather than grepping a line range. A line
range drifts on the next edit above it and would then assert nothing while still passing. Reaching
the command objects a user actually reaches is what makes this a guard rather than a coincidence.

No test artifact is bound yet. The governed binding route, ``gt tests update``, accepts only a latest
bridge status of ``GO`` and this chain sits at ``NOT-READY``, which is WI-7746. The binding is owed and is
recorded as owed in the implementation report rather than asserted here.
"""

from __future__ import annotations

import inspect
import re

import pytest

#: Any spelling of the retired instrument. Matched case-insensitively against parameter names, help
#: text, and callback source. ``project_authorization`` and ``project-authorization`` are included
#: because the retired CLI used both the snake and kebab forms for the same concept.
PAUTH_TOKEN_RE = re.compile(r"(?i)pauth|project[_-]authorization")


def _postgres_group():
    """The live ``db postgres`` group, reached the way a user reaches it.

    Resolved through ``main`` rather than imported by name so that a group which is defined but never
    registered fails here, rather than passing a test that never touched the CLI.
    """
    try:
        from groundtruth_kb.cli import main
    except ImportError as exc:  # pragma: no cover - the group is landed; this guards a regression
        pytest.skip(f"groundtruth_kb.cli not importable: {exc}")
    db = main.commands.get("db")
    assert db is not None, "the 'db' command group is not registered on main"
    group = db.commands.get("postgres")
    assert group is not None, "the 'db postgres' command group is not registered under 'db'"
    return group


def test_the_postgres_command_group_exposes_no_pauth_surface() -> None:
    """No command, parameter, help string, or callback under ``db postgres`` mentions PAUTH.

    Fails the moment someone reintroduces the retired instrument into this group -- which is the
    point. It says nothing about the rest of ``cli.py``, where a retired PAUTH command group still
    lives; that surface is out of scope here and is tracked separately.
    """
    group = _postgres_group()

    offenders: list[str] = []

    for name, command in sorted(group.commands.items()):
        if PAUTH_TOKEN_RE.search(name):
            offenders.append(f"command name: db postgres {name}")

        for param in command.params:
            for opt in list(param.opts) + list(param.secondary_opts) + [param.name or ""]:
                if PAUTH_TOKEN_RE.search(opt):
                    offenders.append(f"parameter on 'db postgres {name}': {opt}")
            help_text = getattr(param, "help", None)
            if help_text and PAUTH_TOKEN_RE.search(help_text):
                offenders.append(f"parameter help on 'db postgres {name}': {help_text[:60]}")

        if command.help and PAUTH_TOKEN_RE.search(command.help):
            offenders.append(f"command help: db postgres {name}")

        callback = command.callback
        if callback is not None:
            try:
                source = inspect.getsource(callback)
            except (OSError, TypeError):  # pragma: no cover - source is available for these callbacks
                continue
            for line_number, line in enumerate(source.splitlines(), start=1):
                if PAUTH_TOKEN_RE.search(line):
                    offenders.append(f"callback source, db postgres {name} line {line_number}: {line.strip()[:60]}")

    if group.help and PAUTH_TOKEN_RE.search(group.help):
        offenders.append("group help: db postgres")

    assert offenders == [], (
        "the 'db postgres' command group has acquired a PAUTH surface, which canon v7.7 retires:\n  "
        + "\n  ".join(offenders)
    )
