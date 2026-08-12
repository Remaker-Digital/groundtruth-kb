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
import os
from pathlib import Path

import click

from groundtruth_kb.config import GTConfig
from groundtruth_kb.session.envelope import TOPIC_TYPES

_HOST_SESSION_ID_ENV_BY_HARNESS = {
    "codex": "CODEX_THREAD_ID",
    "cursor": "CURSOR_CONVERSATION_ID",
    "goose": "GOOSE_SESSION_ID",
}
_HOST_MODEL_METADATA_SOURCE_BY_HARNESS = {
    "codex": "x-codex-turn-metadata",
    "cursor": "cursor-conversation-metadata",
}
_PLACEHOLDER_TURN_METADATA = {
    "",
    "-",
    "n/a",
    "na",
    "none",
    "null",
    "tbd",
    "todo",
    "unknown",
    "unspecified",
}


def _resolve_config(ctx: click.Context) -> GTConfig:
    config_path = ctx.obj.get("config") if ctx.obj else None
    return GTConfig.load(config_path=config_path)


def _required_turn_metadata(value: str, option_name: str) -> str:
    normalized = value.strip()
    if (
        normalized.lower() in _PLACEHOLDER_TURN_METADATA
        or "\n" in normalized
        or "\r" in normalized
        or len(normalized) > 256
    ):
        raise click.ClickException(f"{option_name} must be non-placeholder single-line host turn metadata.")
    return normalized


def _host_session_id(harness_name: str) -> str | None:
    env_name = _HOST_SESSION_ID_ENV_BY_HARNESS.get(harness_name)
    if env_name is None:
        return None
    value = os.environ.get(env_name)
    return _required_turn_metadata(value, env_name) if value is not None else None


@click.group("session")
def session_group() -> None:
    """Deterministic session-services commands."""


@session_group.group("handoff")
def handoff_group() -> None:
    """Generate and inspect deterministic handoff prompts."""


@session_group.group("envelope")
def envelope_group() -> None:
    """Open and inspect per-harness session envelopes."""


def _only_open_worker_envelope(project_root: Path, harness_name: str, harness_id: str) -> dict[str, object] | None:
    """Return one unambiguous open worker envelope without consulting a shared pointer.

    Rebinding a dispatch-created envelope to the host's exact session id is safe
    only when the harness has exactly one open authoritative document. Concurrent
    sessions remain fail-closed rather than reviving a harness-wide "current"
    designation.
    """
    session_dir = project_root / "harness-state" / harness_name / "session-envelopes"
    candidates: list[dict[str, object]] = []
    if not session_dir.is_dir():
        return None
    for path in sorted(session_dir.glob("*.json")):
        try:
            candidate = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(candidate, dict):
            continue
        if (
            candidate.get("status") == "open"
            and candidate.get("harness_name") == harness_name
            and candidate.get("harness_id") == harness_id
        ):
            candidates.append(candidate)
    return candidates[0] if len(candidates) == 1 else None


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
    from groundtruth_kb.session.envelope import (
        EnvelopeError,
        load_worker_session,
        open_session,
        parse_canonical_init_keyword,
        resolve_harness_identity,
        resolve_worker_role_provenance,
        write_current,
    )

    parsed_keyword = parse_canonical_init_keyword(init_keyword) if init_keyword is not None else None
    if init_keyword is not None and parsed_keyword is None:
        raise click.ClickException("--init-keyword must use the exact canonical session-init grammar.")

    parsed_role = parsed_keyword["role"] if parsed_keyword is not None else None
    parsed_subject = parsed_keyword["subject"] if parsed_keyword is not None else None
    if role is not None:
        if parsed_role is None:
            raise click.ClickException("--role requires a canonical role-bearing --init-keyword.")
        if role != parsed_role:
            raise click.ClickException("--role conflicts with the role asserted by --init-keyword.")
    elif parsed_role is not None:
        role = parsed_role

    if subject is not None and parsed_subject is not None and subject != parsed_subject:
        raise click.ClickException("--subject conflicts with the subject asserted by --init-keyword.")
    if subject is None and parsed_subject is not None:
        subject = parsed_subject

    config = _resolve_config(ctx)
    project_root = Path(config.project_root)
    envelope = None
    host_session_id = None
    subject_default_upgrade = False
    normalized_harness = harness_name.strip().lower()
    try:
        host_session_id = _host_session_id(normalized_harness)
        if host_session_id is not None:
            resolved_name, resolved_id = resolve_harness_identity(
                project_root,
                harness_name=normalized_harness,
                harness_id=harness_id,
            )
            existing = load_worker_session(project_root, resolved_name, host_session_id)
            if existing is not None:
                if existing.get("session_id") != host_session_id:
                    raise EnvelopeError("Exact session envelope has a mismatched session id.")
                if existing.get("status") != "open":
                    raise EnvelopeError("Exact session envelope is not open.")
                if existing.get("harness_name") != resolved_name or existing.get("harness_id") != resolved_id:
                    raise EnvelopeError("Exact session envelope has mismatched harness identity.")
                provenance = resolve_worker_role_provenance(
                    project_root,
                    current_session_id=host_session_id,
                    harness_name=resolved_name,
                )
                if role is not None and provenance["role"] != role:
                    raise EnvelopeError("Requested role conflicts with the exact host-bound session envelope.")
                if subject is not None and existing.get("subject") != subject:
                    if existing.get("subject_asserted") is not None:
                        raise EnvelopeError("Requested subject conflicts with the exact host-bound session envelope.")
                    existing["subject_asserted"] = subject
                    existing["subject_resolved"] = subject
                    existing["subject"] = subject
                    subject_default_upgrade = True
                envelope = existing

        if envelope is None:
            envelope = open_session(
                project_root,
                harness_name=harness_name,
                harness_id=harness_id,
                init_keyword=init_keyword,
                subject=subject,
                role=role,
                active_work_item_id=active_work_item_id,
                session_id=host_session_id if parsed_role is not None else None,
                worker_role_source="transcript_init_keyword" if parsed_role is not None else None,
            )
        elif subject_default_upgrade:
            write_current(project_root, normalized_harness, envelope)
    except EnvelopeError as exc:
        raise click.ClickException(str(exc)) from exc
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


@envelope_group.command("attest-author-metadata")
@click.option("--harness-name", default="codex", show_default=True)
@click.option("--harness-id", default=None)
@click.option("--session-id", required=True)
@click.option("--model", required=True)
@click.option("--reasoning-effort", required=True)
@click.option("--thread-source", required=True)
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def envelope_attest_author_metadata_cmd(
    ctx: click.Context,
    harness_name: str,
    harness_id: str | None,
    session_id: str,
    model: str,
    reasoning_effort: str,
    thread_source: str,
    json_output: bool,
) -> None:
    """Attest host-provided model metadata for one exact open session."""
    from groundtruth_kb.session.envelope import (
        EnvelopeError,
        load_current,
        load_worker_session,
        resolve_harness_identity,
        resolve_worker_role_provenance,
        utc_now_iso,
        write_current,
    )

    normalized_harness = harness_name.strip().lower()
    metadata_source = _HOST_MODEL_METADATA_SOURCE_BY_HARNESS.get(normalized_harness)
    if metadata_source is None:
        supported = ", ".join(sorted(_HOST_MODEL_METADATA_SOURCE_BY_HARNESS))
        raise click.ClickException(f"Author metadata attestation accepts only host-attested harnesses: {supported}.")
    normalized_session_id = _required_turn_metadata(session_id, "--session-id")
    normalized_model = _required_turn_metadata(model, "--model")
    normalized_reasoning = _required_turn_metadata(reasoning_effort, "--reasoning-effort")
    normalized_thread_source = _required_turn_metadata(thread_source, "--thread-source")
    host_session_id = _host_session_id(normalized_harness)
    if normalized_harness == "cursor" and host_session_id != normalized_session_id:
        raise click.ClickException("--session-id must match CURSOR_CONVERSATION_ID for Cursor attestation.")

    config = _resolve_config(ctx)
    project_root = Path(config.project_root)
    try:
        resolved_name, resolved_id = resolve_harness_identity(
            project_root,
            harness_name=normalized_harness,
            harness_id=harness_id,
        )
        envelope = load_worker_session(project_root, resolved_name, normalized_session_id)
        current = load_current(project_root, resolved_name)
        if current is None and envelope is None and host_session_id == normalized_session_id:
            current = _only_open_worker_envelope(project_root, resolved_name, resolved_id)
        provenance_validated = False
        if current is None:
            raise EnvelopeError("Current harness session envelope is missing.")
        current_session_id = current.get("session_id")
        if current_session_id != normalized_session_id:
            if host_session_id != normalized_session_id:
                raise EnvelopeError("Exact session envelope is not the current harness session.")
            if envelope is None:
                if current.get("harness_name") != resolved_name or current.get("harness_id") != resolved_id:
                    raise EnvelopeError("Current session envelope has mismatched harness identity.")
                if current.get("status") != "open":
                    raise EnvelopeError("Current session envelope is not open.")
                resolve_worker_role_provenance(
                    project_root,
                    current_session_id=str(current_session_id),
                    harness_name=resolved_name,
                )
                provenance_validated = True
                envelope = dict(current)
                envelope["session_id"] = normalized_session_id
                provenance = dict(envelope["worker_role_provenance"])
                provenance["session_id"] = normalized_session_id
                envelope["worker_role_provenance"] = provenance
        elif envelope is None:
            raise EnvelopeError("Exact session envelope is missing.")
        if envelope.get("session_id") != normalized_session_id:
            raise EnvelopeError("Exact session envelope has a mismatched session id.")
        if envelope.get("harness_name") != resolved_name or envelope.get("harness_id") != resolved_id:
            raise EnvelopeError("Exact session envelope has mismatched harness identity.")
        if envelope.get("status") != "open":
            raise EnvelopeError("Exact session envelope is not open.")
        if not provenance_validated:
            resolve_worker_role_provenance(
                project_root,
                current_session_id=normalized_session_id,
                harness_name=resolved_name,
            )
    except EnvelopeError as exc:
        raise click.ClickException(str(exc)) from exc

    envelope["model_id"] = normalized_model
    # Host request metadata exposes one opaque model identifier, not a
    # separately versioned semantic model. Preserve that value without parsing.
    envelope["model_version"] = normalized_model
    envelope["model_configuration"] = (
        f"reasoning_effort={normalized_reasoning}; thread_source={normalized_thread_source}"
    )
    envelope["model_metadata_source"] = metadata_source
    envelope["model_metadata_attested_at"] = utc_now_iso()
    write_current(project_root, resolved_name, envelope)

    result = {
        "session_id": normalized_session_id,
        "harness_id": resolved_id,
        "harness_name": resolved_name,
        "model_id": envelope["model_id"],
        "model_version": envelope["model_version"],
        "model_configuration": envelope["model_configuration"],
        "model_metadata_source": envelope["model_metadata_source"],
        "model_metadata_attested_at": envelope["model_metadata_attested_at"],
    }
    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    else:
        click.echo(normalized_session_id)


@envelope_group.command("packet")
@click.option(
    "--kind",
    "packet_kind",
    type=click.Choice(["session-envelope", "activity-packet", "session", "activity"]),
    default="session-envelope",
    show_default=True,
    help="Packet kind to compose.",
)
@click.option("--activity", type=click.Choice(list(TOPIC_TYPES)), default=None, help="Required for activity-packet.")
@click.option("--role", default="prime-builder", show_default=True, help="Role bootstrap to include.")
@click.option("--ttl-seconds", default=300, show_default=True, type=click.IntRange(1, None))
@click.option("--cache-dir", type=click.Path(path_type=Path), default=None)
@click.option("--refresh", is_flag=True, default=False, help="Bypass any valid cached packet.")
@click.pass_context
def envelope_packet_cmd(
    ctx: click.Context,
    packet_kind: str,
    activity: str | None,
    role: str,
    ttl_seconds: int,
    cache_dir: Path | None,
    refresh: bool,
) -> None:
    """Compose a budgeted session-envelope or activity packet as JSON."""
    from groundtruth_kb.session.packet import PacketError, compose_packet

    config = _resolve_config(ctx)
    try:
        packet = compose_packet(
            project_root=Path(config.project_root),
            packet_kind=packet_kind,
            activity=activity,
            role=role,
            ttl_seconds=ttl_seconds,
            cache_dir=cache_dir,
            refresh=refresh,
        )
    except PacketError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(packet, indent=2, sort_keys=True))


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
@click.option("--harness-name", default=None, help="Harness name; auto-resolved from runtime markers when omitted.")
@click.option("--harness-id", default=None)
@click.option("--session-id", default=None, help="Invoking session-context id; auto-resolved when omitted.")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def wrap_cmd(
    ctx: click.Context,
    harness_name: str | None,
    harness_id: str | None,
    session_id: str | None,
    json_output: bool,
) -> None:
    """Run the deterministic wrap service used by the canonical ::wrap trigger.

    The invoking session-context id is auto-resolved from runtime markers /
    GTKB_SESSION_ID via the uniform resolver (marker-continuity order); a
    cross-context wrap fails closed with a clear diagnostic.
    """
    from groundtruth_kb.session.envelope import EnvelopeError, resolve_acting_harness_identity
    from groundtruth_kb.session.wrap import run_wrap

    try:
        from scripts.gtkb_session_id import MARKER_CONTINUITY_ORDER, resolve_session_id  # noqa: PLC0415
    except ImportError:  # pragma: no cover - direct-script sys.path shape
        from gtkb_session_id import (  # type: ignore[no-redef]  # noqa: PLC0415
            MARKER_CONTINUITY_ORDER,
            resolve_session_id,
        )

    config = _resolve_config(ctx)
    project_root = Path(config.project_root)

    if not harness_name:
        harness_name, resolved_id = resolve_acting_harness_identity(
            project_root,
            harness_name=None,
            harness_id=harness_id,
        )
        harness_id = harness_id or resolved_id

    resolved_session_id = resolve_session_id(explicit=session_id, order=MARKER_CONTINUITY_ORDER)

    try:
        result = run_wrap(
            project_root,
            harness_name=harness_name,
            harness_id=harness_id,
            session_id=resolved_session_id,
        )
    except EnvelopeError as exc:
        raise click.ClickException(str(exc)) from exc
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
