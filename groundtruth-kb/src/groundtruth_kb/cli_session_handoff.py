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
from groundtruth_kb.session.envelope import TOPIC_TYPES


def _resolve_config(ctx: click.Context) -> GTConfig:
    config_path = ctx.obj.get("config") if ctx.obj else None
    return GTConfig.load(config_path=config_path)


@click.group("session")
def session_group() -> None:
    """Deterministic session-services commands."""


@session_group.group("handoff")
def handoff_group() -> None:
    """Generate and inspect deterministic handoff prompts."""


@session_group.group("envelope")
def envelope_group() -> None:
    """Open and inspect per-harness session envelopes."""


@envelope_group.command("open")
@click.option("--harness-name", default="codex", show_default=True)
@click.option("--harness-id", default=None)
@click.option("--init-keyword", default=None)
@click.option("--subject", default=None)
@click.option("--role", default=None)
@click.option("--active-work-item-id", default=None)
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def envelope_open_cmd(
    ctx: click.Context,
    harness_name: str,
    harness_id: str | None,
    init_keyword: str | None,
    subject: str | None,
    role: str | None,
    active_work_item_id: str | None,
    json_output: bool,
) -> None:
    """Open a current per-harness session-envelope file."""
    from groundtruth_kb.session.envelope import open_session

    config = _resolve_config(ctx)
    envelope = open_session(
        Path(config.project_root),
        harness_name=harness_name,
        harness_id=harness_id,
        init_keyword=init_keyword,
        subject=subject,
        role=role,
        active_work_item_id=active_work_item_id,
    )
    if json_output:
        click.echo(json.dumps(envelope, indent=2, sort_keys=True))
    else:
        click.echo(envelope["session_id"])


@envelope_group.command("show")
@click.option("--harness-name", default="codex", show_default=True)
@click.pass_context
def envelope_show_cmd(ctx: click.Context, harness_name: str) -> None:
    """Print the current per-harness session envelope as JSON."""
    from groundtruth_kb.session.envelope import load_current

    config = _resolve_config(ctx)
    envelope = load_current(Path(config.project_root), harness_name)
    if envelope is None:
        raise click.ClickException(f"No current session envelope for harness {harness_name!r}.")
    click.echo(json.dumps(envelope, indent=2, sort_keys=True))


@session_group.group("topic")
def topic_group() -> None:
    """Open and close topic envelopes."""


@topic_group.command("open")
@click.argument("topic_type", type=click.Choice(list(TOPIC_TYPES)))
@click.option("--harness-name", default="codex", show_default=True)
@click.option("--harness-id", default=None)
@click.pass_context
def topic_open_cmd(ctx: click.Context, topic_type: str, harness_name: str, harness_id: str | None) -> None:
    """Open one topic envelope for the given type."""
    from groundtruth_kb.session.envelope import open_topic

    config = _resolve_config(ctx)
    topic = open_topic(Path(config.project_root), topic_type, harness_name=harness_name, harness_id=harness_id)
    click.echo(json.dumps(topic, indent=2, sort_keys=True))


@topic_group.command("close")
@click.argument("topic_type", type=click.Choice(list(TOPIC_TYPES)))
@click.option("--harness-name", default="codex", show_default=True)
@click.option("--harness-id", default=None)
@click.pass_context
def topic_close_cmd(ctx: click.Context, topic_type: str, harness_name: str, harness_id: str | None) -> None:
    """Close one open topic envelope for the given type."""
    from groundtruth_kb.session.envelope import close_topic

    config = _resolve_config(ctx)
    topic = close_topic(Path(config.project_root), topic_type, harness_name=harness_name, harness_id=harness_id)
    click.echo(json.dumps(topic, indent=2, sort_keys=True))


@session_group.command("wrap")
@click.option("--harness-name", default="codex", show_default=True)
@click.option("--harness-id", default=None)
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def wrap_cmd(ctx: click.Context, harness_name: str, harness_id: str | None, json_output: bool) -> None:
    """Run the deterministic wrap service used by the canonical ::wrap trigger."""
    from groundtruth_kb.session.wrap import run_wrap

    config = _resolve_config(ctx)
    result = run_wrap(Path(config.project_root), harness_name=harness_name, harness_id=harness_id)
    if json_output:
        payload = {**result, "archive_path": str(result["archive_path"])}
        click.echo(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        click.echo(result["summary"])


@session_group.group("dispatcher")
def dispatcher_group() -> None:
    """Validate and tick dispatch-envelope rules."""


@dispatcher_group.command("validate")
@click.option("--rules-path", type=click.Path(path_type=Path), default=None)
@click.pass_context
def dispatcher_validate_cmd(ctx: click.Context, rules_path: Path | None) -> None:
    """Load dispatch-envelope rules and fail on schema errors."""
    from groundtruth_kb.dispatcher.rules_loader import default_rules_path, load_rules

    config = _resolve_config(ctx)
    path = rules_path or default_rules_path(Path(config.project_root))
    rules = load_rules(path)
    click.echo(json.dumps({"rules_path": str(path), "rule_count": len(rules)}, indent=2, sort_keys=True))


@dispatcher_group.command("tick")
@click.option("--rules-path", type=click.Path(path_type=Path), default=None)
@click.option("--execute", is_flag=True, default=False, help="Disable dry-run mode.")
@click.pass_context
def dispatcher_tick_cmd(ctx: click.Context, rules_path: Path | None, execute: bool) -> None:
    """Evaluate dispatch-envelope activity gates and persist scheduler state."""
    from groundtruth_kb.dispatcher.rules_loader import default_rules_path
    from groundtruth_kb.dispatcher.scheduler import tick

    config = _resolve_config(ctx)
    project_root = Path(config.project_root)
    state = tick(project_root, rules_path=rules_path or default_rules_path(project_root), dry_run=not execute)
    click.echo(json.dumps(state, indent=2, sort_keys=True))


@handoff_group.command("generate")
@click.option(
    "--session-id",
    default=None,
    help="Session identifier. Defaults to a deterministic id derived from the latest archived envelope.",
)
@click.option(
    "--harness-name",
    default=None,
    help=(
        "Optional explicit registered harness override. When omitted, explicit "
        "--session-id scans registered harness archives for the matching envelope."
    ),
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
    harness_name: str | None,
    json_output: bool,
) -> None:
    """Generate the deterministic handoff prompt for a session.

    Reads the latest archived session envelope plus live bridge state,
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
            harness_name=harness_name,
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
