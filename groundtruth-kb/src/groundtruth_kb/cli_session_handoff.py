"""``gt session handoff`` deterministic handoff-prompt CLI.

Thin wrappers around ``groundtruth_kb.session.handoff.generate`` and the
``session_prompts`` MemBase read APIs. Echoes the deterministic prompt body
to stdout so the third spec-required output surface (terminal echo) lands
without the Python API needing to know anything about the terminal.

Authority: SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001; bridge thread
``gtkb-handoff-prompt-deterministic-service-impl-004`` (GO at -005).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from groundtruth_kb.config import GTConfig


def _resolve_config(ctx: click.Context) -> GTConfig:
    config_path = ctx.obj.get("config") if ctx.obj else None
    return GTConfig.load(config_path=config_path)


@click.group("session")
def session_group() -> None:
    """Deterministic session-services commands."""


@session_group.group("handoff")
def handoff_group() -> None:
    """Generate and inspect deterministic handoff prompts."""


@handoff_group.command("generate")
@click.option(
    "--session-id",
    default=None,
    help="Session identifier. Defaults to a deterministic id derived from the latest archived envelope.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Emit a machine-readable JSON summary instead of the prompt body.",
)
@click.pass_context
def generate_cmd(
    ctx: click.Context,
    session_id: str | None,
    json_output: bool,
) -> None:
    """Generate the deterministic handoff prompt for a session.

    Reads the latest archived session envelope plus the live bridge index,
    writes a new ``session_prompts`` MemBase row (idempotent on identical
    canonical inputs), writes the prompt markdown to
    ``.claude/session/handoff-<session-id>.md``, and echoes the prompt body
    to stdout.
    """
    from groundtruth_kb.session.handoff import HandoffError, generate

    config = _resolve_config(ctx)
    try:
        result = generate(
            session_id=session_id,
            project_root=Path(config.project_root),
        )
    except HandoffError as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(
            json.dumps(
                {
                    "session_id": result["session_id"],
                    "session_prompts_id": result["session_prompts_id"],
                    "output_files": result["output_files"],
                },
                indent=2,
                sort_keys=True,
            ),
        )
        return

    click.echo(result["prompt_markdown"], nl=False)


@handoff_group.command("get")
@click.argument("session_id")
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Emit the row as JSON instead of plain text.",
)
@click.pass_context
def get_cmd(
    ctx: click.Context,
    session_id: str,
    json_output: bool,
) -> None:
    """Print the latest ``session_prompts`` row for ``session_id``."""
    from groundtruth_kb.db import KnowledgeDB

    config = _resolve_config(ctx)
    db_path = Path(config.project_root) / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    row = db.get_session_prompt(session_id)
    if row is None:
        raise click.ClickException(f"No handoff prompt found for session_id={session_id!r}.")
    if json_output:
        click.echo(json.dumps(row, indent=2, sort_keys=True, default=str))
        return
    prompt_text = row.get("prompt_text") or ""
    click.echo(prompt_text, nl=False)
