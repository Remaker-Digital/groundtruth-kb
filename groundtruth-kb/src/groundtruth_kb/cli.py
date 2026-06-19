"""
GroundTruth KB — CLI (``gt`` command).

Provides project initialization, assertion running, seed data loading,
database inspection, and import/export commands.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import contextlib
import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import click

from groundtruth_kb import __version__
from groundtruth_kb._logging import configure_cli_logging
from groundtruth_kb.bootstrap import (
    DesktopBootstrapOptions,
    bootstrap_desktop_project,
    bootstrap_summary,
)
from groundtruth_kb.cli_approval_packet import (
    GenerateApprovalPacketError,
    GenerateApprovalPacketRequest,
    format_result,
    run_generate_approval_packet,
)
from groundtruth_kb.cli_backlog_update import BacklogUpdateError, BacklogUpdateRequest, update_backlog_item
from groundtruth_kb.cli_bridge_propose import bridge_group
from groundtruth_kb.cli_deliberations_record import (
    DeliberationRecordError,
    DeliberationRecordRequest,
    record_deliberation,
)
from groundtruth_kb.cli_session_handoff import session_group
from groundtruth_kb.cli_spec_record import SPEC_RECORD_TYPES, SpecRecordError, SpecRecordRequest, record_spec
from groundtruth_kb.cli_spec_update import SpecUpdateError, SpecUpdateRequest, update_spec
from groundtruth_kb.coherence import (
    CoherenceRuleError,
)
from groundtruth_kb.coherence import (
    emit_json as emit_coherence_json,
)
from groundtruth_kb.coherence import (
    emit_markdown as emit_coherence_markdown,
)
from groundtruth_kb.coherence import (
    load_rules as load_coherence_rules,
)
from groundtruth_kb.coherence import (
    load_specs_from_db as load_coherence_specs_from_db,
)
from groundtruth_kb.coherence import (
    make_result as make_coherence_result,
)
from groundtruth_kb.coherence import (
    run_all as run_coherence_checks,
)
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.db_snapshot import SnapshotError, create_snapshot
from groundtruth_kb.gates import GateRegistry
from groundtruth_kb.hygiene import PatternSetError, emit_json, emit_markdown, run_sweep
from groundtruth_kb.project.core_spec_intake import next_missing_slot, next_question, slot_statuses
from groundtruth_kb.project.lifecycle import (
    PROJECTS_CHANGED_BY,
    ProjectAuthorizationSpecLinkageError,
    ProjectLifecycleError,
    ProjectLifecycleService,
)
from groundtruth_kb.project.sot_registry import (
    InvalidSoTRecord,
    UnknownDomain,
    default_registry_path,
    load_projection,
    sync_projection,
    validate_projection_parity,
)
from groundtruth_kb.project.sot_registry import (
    load_toml as load_sot_toml,
)
from groundtruth_kb.typed_artifact_flow import (
    TypedArtifactFlowService,
    canonical_reviewed_task_flow_definitions,
)

if TYPE_CHECKING:
    from groundtruth_kb.dashboard import DashboardPaths

_DEFAULT_TOML = """\
# GroundTruth KB project configuration
# Docs: https://github.com/Remaker-Digital/groundtruth-kb

[groundtruth]
db_path = "./groundtruth.db"
project_root = "."
app_title = "{project_name}"
brand_mark = "GT"
brand_color = "#2563eb"
# logo_url = ""
# legal_footer = ""

[gates]
# Plug-in governance gates (dotted import paths)
# plugins = ["my_package.gates:MyCustomGate"]

[backup]
# Optional database snapshot settings. Defaults keep snapshots outside the
# adopter root and stage them in a non-synced user-local directory.
# snapshot_output_dir = ""
# snapshot_staging_dir = ""
# retain_recent = 7
# retain_daily_days = 30
# include_chroma = false
# sync_paths = []
"""


def _resolve_config(ctx: click.Context) -> GTConfig:
    """Resolve GTConfig from the click context or auto-discover."""
    config_path = ctx.obj.get("config") if ctx.obj else None
    return GTConfig.load(config_path=config_path)


def _open_db(config: GTConfig, *, check_same_thread: bool = True) -> KnowledgeDB:
    """Open a KnowledgeDB from resolved config, wiring governance gates."""
    registry = GateRegistry.from_config(
        config.governance_gates,
        include_builtins=True,
        gate_config=config.gate_config,
        project_root=config.project_root,
    )
    return KnowledgeDB(db_path=config.db_path, gate_registry=registry, check_same_thread=check_same_thread)


def _ensure_utf8_streams() -> None:
    """Make CLI stdout/stderr UTF-8 so non-cp1252 content never crashes (WI-4250).

    On Windows, ``sys.stdout`` defaults to the cp1252 locale codec, so printing a
    stored value containing a BOM or any non-cp1252 glyph raises
    ``UnicodeEncodeError`` (observed in ``gt deliberations search``). Reconfiguring
    the streams to UTF-8 at the single ``main()`` entry both ``gt`` and
    ``python -m groundtruth_kb`` pass through fixes the whole CLI at once.

    Guarded to be a safe no-op when the active streams are redirected or captured
    (pytest ``capsys``, Click's ``CliRunner``, a closed pipe): such streams expose
    no ``reconfigure`` method and are left untouched. ``errors="backslashreplace"``
    is belt-and-suspenders — UTF-8 encodes every code point, so it only guarantees
    no crash should a future stream still reject a character.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        with contextlib.suppress(ValueError, OSError):
            reconfigure(encoding="utf-8", errors="backslashreplace")


@click.group()
@click.version_option(version=__version__, prog_name="gt")
@click.option("--config", "config_path", type=click.Path(exists=True), default=None, help="Path to groundtruth.toml")
@click.pass_context
def main(ctx: click.Context, config_path: str | None) -> None:
    """GroundTruth KB — specification-driven governance toolkit."""
    _ensure_utf8_streams()
    configure_cli_logging()
    ctx.ensure_object(dict)
    ctx.obj["config"] = Path(config_path) if config_path else None


main.add_command(bridge_group)
main.add_command(session_group)


@main.group("admin")
def admin_group() -> None:
    """Administrative project tooling."""


@admin_group.group("inventory")
def admin_inventory_group() -> None:
    """SoT artifact inventory utilities."""


@admin_inventory_group.command("refresh")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def admin_inventory_refresh_cmd(ctx: click.Context, json_output: bool) -> None:
    """Check the declared SoT artifact inventory without mutating artifacts."""
    from groundtruth_kb.inventory import InventoryScanError, build_refresh_report

    config = _resolve_config(ctx)
    try:
        payload = build_refresh_report(config.project_root)
    except InventoryScanError as exc:
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
        return
    summary = payload["summary"]
    click.echo("Inventory refresh check")
    click.echo(f"- artifacts: {summary['artifact_count']}")
    click.echo(f"- scanned files: {summary['scanned_file_count']}")
    click.echo(f"- missing artifacts: {summary['missing_artifact_count']}")


@admin_inventory_group.command("scan-strings")
@click.option("--match", "matches", multiple=True, help="Literal string to scan for; repeatable.")
@click.option(
    "--match-file",
    "match_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Newline or JSON list of literal strings.",
)
@click.option(
    "--critical-class", "critical_classes", multiple=True, help="Artifact id/domain/lifecycle to classify critical."
)
@click.option("--warn-class", "warn_classes", multiple=True, help="Artifact id/domain/lifecycle to classify warn.")
@click.option("--critical-path", "critical_paths", multiple=True, help="Path glob to classify critical.")
@click.option("--warn-path", "warn_paths", multiple=True, help="Path glob to classify warn.")
@click.option("--report-only", is_flag=True, default=False, help="Return success even when critical hits exist.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def admin_inventory_scan_strings_cmd(
    ctx: click.Context,
    matches: tuple[str, ...],
    match_file: Path | None,
    critical_classes: tuple[str, ...],
    warn_classes: tuple[str, ...],
    critical_paths: tuple[str, ...],
    warn_paths: tuple[str, ...],
    report_only: bool,
    json_output: bool,
) -> None:
    """Scan declared inventory artifacts for literal strings."""
    from groundtruth_kb.inventory import (
        InventoryScanError,
        emit_markdown_ledger,
        load_match_file,
        scan_inventory_strings,
    )

    config = _resolve_config(ctx)
    literals = list(matches)
    if match_file is not None:
        literals.extend(load_match_file(match_file))
    try:
        payload = scan_inventory_strings(
            config.project_root,
            literals,
            critical_classes=set(critical_classes),
            warn_classes=set(warn_classes),
            critical_paths=tuple(critical_paths),
            warn_paths=tuple(warn_paths),
        )
    except InventoryScanError as exc:
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
    else:
        click.echo(emit_markdown_ledger(payload), nl=False)
    if payload["summary"]["critical"] and not report_only:
        ctx.exit(1)


def _emit_cli_payload(payload: dict[str, Any], *, json_output: bool) -> None:
    if json_output:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = payload.get("summary")
        if summary:
            click.echo(summary)


@bridge_group.group("dispatch")
def bridge_dispatch_group() -> None:
    """Bridge dispatch configuration, status, and health."""


def _emit_bridge_dispatch_config(ctx: click.Context, *, json_output: bool) -> None:
    from groundtruth_kb.bridge_dispatch_config import load_bridge_dispatch_config

    config = _resolve_config(ctx)
    dispatch_config = load_bridge_dispatch_config(config.project_root)
    payload = dispatch_config.to_json_dict()
    if json_output:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
        return
    click.echo(f"Bridge dispatch config: {payload['path']}")
    click.echo(f"Schema version: {payload['schema_version']}")
    click.echo(f"Harness overlays: {len(payload['harnesses'])}")
    click.echo(f"Rules: {len(payload['rules'])}")
    if payload["errors"]:
        click.echo("Errors:")
        for error in payload["errors"]:
            click.echo(f"- {error}")


def _emit_bridge_dispatch_status(ctx: click.Context, *, json_output: bool) -> None:
    from groundtruth_kb.bridge_dispatch_config import collect_bridge_dispatch_status, format_bridge_dispatch_status

    config = _resolve_config(ctx)
    status = collect_bridge_dispatch_status(config.project_root)
    if json_output:
        click.echo(json.dumps(status.to_json_dict(), indent=2, sort_keys=True))
        return
    click.echo(format_bridge_dispatch_status(status))


def _emit_bridge_dispatch_health(ctx: click.Context, *, json_output: bool) -> None:
    from groundtruth_kb.bridge_dispatch_config import collect_bridge_dispatch_status

    config = _resolve_config(ctx)
    status = collect_bridge_dispatch_status(config.project_root)
    payload = {
        "health_status": status.health_status,
        "findings": list(status.health_findings),
        "selected_by_role": status.selected_by_role,
        "config_path": str(status.config.path),
    }
    if json_output:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
    else:
        click.echo(f"Bridge dispatch health: {status.health_status}")
        for role, candidates in status.selected_by_role.items():
            ids = [str(row.get("id")) for row in candidates]
            click.echo(f"- {role}: {', '.join(ids) if ids else '(none)'}")
        if status.health_findings:
            click.echo("Findings:")
            for finding in status.health_findings:
                click.echo(f"- {finding}")
    ctx.exit(0 if status.health_status != "FAIL" else 1)


@bridge_group.command("config")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def bridge_config_cmd(ctx: click.Context, json_output: bool) -> None:
    """Show the canonical bridge dispatch configuration."""
    _emit_bridge_dispatch_config(ctx, json_output=json_output)


@bridge_group.command("status")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def bridge_status_cmd(ctx: click.Context, json_output: bool) -> None:
    """Show current harness eligibility and selected dispatch candidates."""
    _emit_bridge_dispatch_status(ctx, json_output=json_output)


@bridge_group.command("health")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def bridge_health_cmd(ctx: click.Context, json_output: bool) -> None:
    """Check whether bridge dispatch has eligible targets for both roles."""
    _emit_bridge_dispatch_health(ctx, json_output=json_output)


@bridge_group.command("show")
@click.argument("slug")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def bridge_show_cmd(ctx: click.Context, slug: str, json_output: bool) -> None:
    """Show one bridge thread's version chain."""
    from groundtruth_kb.bridge.read_commands import show_thread

    config = _resolve_config(ctx)
    payload = show_thread(config.project_root, slug)
    if payload is None:
        if json_output:
            click.echo(json.dumps({"error": "bridge_thread_not_found", "slug": slug}, indent=2, sort_keys=True))
        else:
            click.echo(f"Bridge thread not found: {slug}", err=True)
        ctx.exit(1)
    if json_output:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
        return
    click.echo(f"Bridge thread: {payload['slug']}")
    click.echo(f"Latest status: {payload['latest_status']}")
    click.echo(f"Latest path: {payload['latest_path']}")
    click.echo("Versions:")
    for version in payload["version_chain"]:
        status = version["status"] or "(unknown)"
        click.echo(f"- {version['version']:03d} {status} {version['path']}")


@bridge_group.command("threads")
@click.option("--wi", "wi_id", required=True, help="Work item id to search for, e.g. WI-4634.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def bridge_threads_cmd(ctx: click.Context, wi_id: str, json_output: bool) -> None:
    """List bridge threads that cite a work item."""
    from groundtruth_kb.bridge.read_commands import threads_for_work_item

    config = _resolve_config(ctx)
    try:
        payload = threads_for_work_item(config.project_root, wi_id)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        ctx.exit(2)
    if json_output:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
        return
    click.echo(f"Bridge threads citing {payload['work_item']}: {payload['match_count']}")
    caveat = payload["coverage_caveat"]
    click.echo(
        "Coverage: "
        f"{caveat['threads_with_work_item_metadata']} of {caveat['total_threads']} threads carry Work Item metadata."
    )
    if not payload["threads"]:
        click.echo("- (none)")
        return
    for thread in payload["threads"]:
        click.echo(f"- {thread['slug']} ({thread['latest_status']} at {thread['latest_path']})")
        for citing_path in thread["citing_paths"]:
            click.echo(f"  cites: {citing_path}")


@bridge_dispatch_group.command("config")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def bridge_dispatch_config_cmd(ctx: click.Context, json_output: bool) -> None:
    """Show the canonical bridge dispatch configuration."""
    _emit_bridge_dispatch_config(ctx, json_output=json_output)


@bridge_dispatch_group.command("status")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def bridge_dispatch_status_cmd(ctx: click.Context, json_output: bool) -> None:
    """Show current harness eligibility and selected dispatch candidates."""
    _emit_bridge_dispatch_status(ctx, json_output=json_output)


@bridge_dispatch_group.command("health")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def bridge_dispatch_health_cmd(ctx: click.Context, json_output: bool) -> None:
    """Check whether bridge dispatch has eligible targets for both roles."""
    _emit_bridge_dispatch_health(ctx, json_output=json_output)


def _flow_service(ctx: click.Context) -> tuple[KnowledgeDB, TypedArtifactFlowService]:
    config = _resolve_config(ctx)
    db = _open_db(config)
    return db, TypedArtifactFlowService(db)


def _flow_noop_payload(command: str, *, detail: str) -> dict[str, Any]:
    return {
        "command": command,
        "mutated": False,
        "phase": "phase-0",
        "status": "phase0_noop",
        "summary": f"{command}: no-op in TAFE Phase 0; {detail}",
    }


def _flow_lease_payload(command: str, stage_instance_id: str, lease: dict[str, Any], *, summary: str) -> dict[str, Any]:
    return {
        "command": command,
        "holder_harness_id": lease["holder_harness_id"],
        "holder_session_id": lease["holder_session_id"],
        "lease": lease,
        "lease_id": lease["id"],
        "mutated": True,
        "phase": "phase-1",
        "stage_instance_id": stage_instance_id,
        "status": lease["lease_status"],
        "summary": summary,
    }


def _flow_lease_error_payload(command: str, stage_instance_id: str, error: Exception) -> dict[str, Any]:
    return {
        "command": command,
        "error": str(error),
        "mutated": False,
        "phase": "phase-1",
        "stage_instance_id": stage_instance_id,
        "status": "error",
        "summary": f"{command}: {error}",
    }


@main.group("flow")
def flow_group() -> None:
    """Typed Artifact-Flow Engine command skeleton."""


@flow_group.command("define")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def flow_define_cmd(ctx: click.Context, json_output: bool) -> None:
    """Read canonical Phase 0 reviewed-task flow definitions."""
    db, service = _flow_service(ctx)
    try:
        current_by_id = {row["id"]: row for row in service.list_flow_definitions(lifecycle_status="active")}
        definitions = []
        for seed in canonical_reviewed_task_flow_definitions():
            current = current_by_id.get(seed["id"])
            definitions.append(
                {
                    "id": seed["id"],
                    "flow_type": seed["flow_type"],
                    "stage_sequence": list(seed["stage_sequence"]),
                    "seeded": current is not None,
                    "version": current["version"] if current else None,
                }
            )
    finally:
        db.close()

    payload = {
        "definitions": definitions,
        "mutated": False,
        "status": "phase0_read_only",
        "summary": "TAFE canonical definitions: " + ", ".join(row["id"] for row in definitions),
    }
    _emit_cli_payload(payload, json_output=json_output)


@flow_group.command("list")
@click.option("--flow-definition-id", default=None, help="Filter by flow definition id.")
@click.option("--flow-type", default=None, help="Filter by flow type.")
@click.option("--status", "flow_status", default=None, help="Filter by flow-instance status.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def flow_list_cmd(
    ctx: click.Context,
    flow_definition_id: str | None,
    flow_type: str | None,
    flow_status: str | None,
    json_output: bool,
) -> None:
    """Read current TAFE flow instances."""
    db, service = _flow_service(ctx)
    try:
        rows = service.list_flow_instances(
            flow_definition_id=flow_definition_id,
            flow_type=flow_type,
            status=flow_status,
        )
    finally:
        db.close()
    if rows:
        summary = "\n".join(f"{row['id']}: {row['flow_type']} {row['status']}" for row in rows)
    else:
        summary = "No TAFE flow instances found."
    _emit_cli_payload(
        {"flow_instances": rows, "mutated": False, "status": "phase0_read_only", "summary": summary},
        json_output=json_output,
    )


@flow_group.command("show")
@click.argument("flow_instance_id")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def flow_show_cmd(ctx: click.Context, flow_instance_id: str, json_output: bool) -> None:
    """Read one current TAFE flow instance."""
    db, service = _flow_service(ctx)
    try:
        row = service.get_flow_instance(flow_instance_id)
    finally:
        db.close()
    if row is None:
        payload = {
            "flow_instance": None,
            "found": False,
            "mutated": False,
            "status": "not_found",
            "summary": f"TAFE flow instance not found: {flow_instance_id}",
        }
        _emit_cli_payload(payload, json_output=json_output)
        raise SystemExit(1)
    _emit_cli_payload(
        {
            "flow_instance": row,
            "found": True,
            "mutated": False,
            "status": "phase0_read_only",
            "summary": f"{row['id']}: {row['flow_type']} {row['status']}",
        },
        json_output=json_output,
    )


@flow_group.command("status")
@click.argument("flow_instance_id", required=False)
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def flow_status_cmd(ctx: click.Context, flow_instance_id: str | None, json_output: bool) -> None:
    """Read a current TAFE flow status or an aggregate Phase 0 status."""
    db, service = _flow_service(ctx)
    try:
        if flow_instance_id:
            row = service.get_flow_instance(flow_instance_id)
            if row is None:
                payload: dict[str, Any] = {
                    "flow_instance": None,
                    "found": False,
                    "mutated": False,
                    "status": "not_found",
                    "summary": f"TAFE flow instance not found: {flow_instance_id}",
                }
                _emit_cli_payload(payload, json_output=json_output)
                raise SystemExit(1)
            payload = {
                "flow_instance": row,
                "found": True,
                "mutated": False,
                "status": row["status"],
                "summary": f"{row['id']}: {row['status']}",
            }
        else:
            rows = service.list_flow_instances()
            by_status: dict[str, int] = {}
            for row in rows:
                by_status[row["status"]] = by_status.get(row["status"], 0) + 1
            payload = {
                "flow_instance_count": len(rows),
                "mutated": False,
                "phase": "phase-0",
                "status": "phase0_read_only",
                "status_counts": by_status,
                "summary": f"TAFE Phase 0 flow status: {len(rows)} current instance(s).",
            }
    finally:
        db.close()
    _emit_cli_payload(payload, json_output=json_output)


@flow_group.command("start")
@click.argument("flow_definition_id")
@click.option("--subject-type", required=True, help="Future flow subject type.")
@click.option("--subject-id", required=True, help="Future flow subject id.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
def flow_start_cmd(flow_definition_id: str, subject_type: str, subject_id: str, json_output: bool) -> None:
    """No-op Phase 0 placeholder for starting a TAFE flow."""
    payload = _flow_noop_payload(
        "flow start",
        detail="flow creation is reserved for a later governed runtime slice.",
    )
    payload.update(
        {
            "flow_definition_id": flow_definition_id,
            "subject_id": subject_id,
            "subject_type": subject_type,
        }
    )
    _emit_cli_payload(payload, json_output=json_output)


@flow_group.command("claim")
@click.argument("stage_instance_id")
@click.option("--holder-harness-id", required=True, help="Harness id acquiring the stage lease.")
@click.option("--holder-session-id", required=True, help="Session/context id acquiring the stage lease.")
@click.option("--ttl-seconds", type=int, default=600, show_default=True, help="Lease TTL in seconds.")
@click.option("--lease-id", default=None, help="Optional explicit lease id; defaults to LEASE-<stage_instance_id>.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def flow_claim_cmd(
    ctx: click.Context,
    stage_instance_id: str,
    holder_harness_id: str,
    holder_session_id: str,
    ttl_seconds: int,
    lease_id: str | None,
    json_output: bool,
) -> None:
    """Acquire one active TAFE stage lease."""
    db, service = _flow_service(ctx)
    try:
        try:
            lease = service.claim_stage_lease(
                stage_instance_id=stage_instance_id,
                holder_harness_id=holder_harness_id,
                holder_session_id=holder_session_id,
                ttl_seconds=ttl_seconds,
                lease_id=lease_id,
                changed_by="gt-flow-lease-cli",
                change_reason="gt flow claim",
            )
        except ValueError as exc:
            _emit_cli_payload(_flow_lease_error_payload("flow claim", stage_instance_id, exc), json_output=json_output)
            raise SystemExit(1) from exc
    finally:
        db.close()
    _emit_cli_payload(
        _flow_lease_payload(
            "flow claim", stage_instance_id, lease, summary=f"Claimed {lease['id']} for {stage_instance_id}."
        ),
        json_output=json_output,
    )


@flow_group.command("release")
@click.argument("stage_instance_id")
@click.option("--holder-harness-id", required=True, help="Harness id holding the stage lease.")
@click.option("--holder-session-id", required=True, help="Session/context id holding the stage lease.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def flow_release_cmd(
    ctx: click.Context,
    stage_instance_id: str,
    holder_harness_id: str,
    holder_session_id: str,
    json_output: bool,
) -> None:
    """Release the active TAFE stage lease held by this holder."""
    db, service = _flow_service(ctx)
    try:
        try:
            lease = service.release_stage_lease(
                stage_instance_id=stage_instance_id,
                holder_harness_id=holder_harness_id,
                holder_session_id=holder_session_id,
                changed_by="gt-flow-lease-cli",
                change_reason="gt flow release",
            )
        except ValueError as exc:
            _emit_cli_payload(
                _flow_lease_error_payload("flow release", stage_instance_id, exc), json_output=json_output
            )
            raise SystemExit(1) from exc
    finally:
        db.close()
    _emit_cli_payload(
        _flow_lease_payload(
            "flow release", stage_instance_id, lease, summary=f"Released {lease['id']} for {stage_instance_id}."
        ),
        json_output=json_output,
    )


@flow_group.command("heartbeat")
@click.argument("stage_instance_id")
@click.option("--holder-harness-id", required=True, help="Harness id holding the stage lease.")
@click.option("--holder-session-id", required=True, help="Session/context id holding the stage lease.")
@click.option("--ttl-seconds", type=int, default=None, help="Optional replacement lease TTL in seconds.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def flow_heartbeat_cmd(
    ctx: click.Context,
    stage_instance_id: str,
    holder_harness_id: str,
    holder_session_id: str,
    ttl_seconds: int | None,
    json_output: bool,
) -> None:
    """Renew the active TAFE stage lease heartbeat for this holder."""
    db, service = _flow_service(ctx)
    try:
        try:
            lease = service.heartbeat_stage_lease(
                stage_instance_id=stage_instance_id,
                holder_harness_id=holder_harness_id,
                holder_session_id=holder_session_id,
                ttl_seconds=ttl_seconds,
                changed_by="gt-flow-lease-cli",
                change_reason="gt flow heartbeat",
            )
        except ValueError as exc:
            _emit_cli_payload(
                _flow_lease_error_payload("flow heartbeat", stage_instance_id, exc), json_output=json_output
            )
            raise SystemExit(1) from exc
    finally:
        db.close()
    _emit_cli_payload(
        _flow_lease_payload(
            "flow heartbeat",
            stage_instance_id,
            lease,
            summary=f"Renewed heartbeat for {lease['id']} on {stage_instance_id}.",
        ),
        json_output=json_output,
    )


@flow_group.command("recover-leases")
@click.option("--as-of", default=None, help="Recover active leases expiring at or before this ISO timestamp.")
@click.option("--limit", type=int, default=None, help="Maximum number of expired leases to recover.")
@click.option("--dry-run", is_flag=True, default=False, help="Report recoverable leases without mutation.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def flow_recover_leases_cmd(
    ctx: click.Context,
    as_of: str | None,
    limit: int | None,
    dry_run: bool,
    json_output: bool,
) -> None:
    """Recover expired active TAFE stage leases and requeue their stages."""

    db, service = _flow_service(ctx)
    try:
        try:
            if dry_run:
                candidates = service.list_expired_stage_leases(as_of=as_of, limit=limit)
                payload = {
                    "as_of": as_of,
                    "candidates": candidates,
                    "command": "flow recover-leases",
                    "limit": limit,
                    "mutated": False,
                    "phase": "phase-1",
                    "recovered_count": 0,
                    "status": "dry_run",
                    "summary": f"Found {len(candidates)} expired active stage lease(s); no mutation performed.",
                }
            else:
                recovered = service.recover_expired_stage_leases(
                    as_of=as_of,
                    limit=limit,
                    changed_by="gt-flow-lease-cli",
                    change_reason="gt flow recover-leases",
                )
                payload = {
                    "as_of": as_of,
                    "command": "flow recover-leases",
                    "limit": limit,
                    "mutated": bool(recovered),
                    "phase": "phase-1",
                    "recovered": recovered,
                    "recovered_count": len(recovered),
                    "status": "recovered" if recovered else "no_expired_leases",
                    "summary": f"Recovered {len(recovered)} expired active stage lease(s).",
                }
        except ValueError as exc:
            _emit_cli_payload(
                {
                    "as_of": as_of,
                    "command": "flow recover-leases",
                    "error": str(exc),
                    "limit": limit,
                    "mutated": False,
                    "phase": "phase-1",
                    "status": "error",
                    "summary": f"flow recover-leases: {exc}",
                },
                json_output=json_output,
            )
            raise SystemExit(1) from exc
    finally:
        db.close()
    _emit_cli_payload(payload, json_output=json_output)


@flow_group.command("advance")
@click.argument("stage_instance_id")
@click.option("--to-stage", default=None, help="Future destination stage id.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
def flow_advance_cmd(stage_instance_id: str, to_stage: str | None, json_output: bool) -> None:
    """No-op Phase 0 placeholder for stage advancement."""
    payload = _flow_noop_payload("flow advance", detail="stage transitions are reserved for later flow-engine work.")
    payload["stage_instance_id"] = stage_instance_id
    payload["to_stage"] = to_stage
    _emit_cli_payload(payload, json_output=json_output)


@flow_group.group("dispatch")
def flow_dispatch_group() -> None:
    """Evaluate non-mutating TAFE dispatch readiness."""


@flow_dispatch_group.command("tick")
@click.option("--subject-scope", default=None, help="Restrict evaluation to one flow subject scope.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def flow_dispatch_tick_cmd(ctx: click.Context, subject_scope: str | None, json_output: bool) -> None:
    """Evaluate need-driven dispatch (SPEC-TAFE-R5) for eligible unclaimed stages.

    Read-only: reports what would be dispatched; never claims, spawns, or mutates.
    """
    from groundtruth_kb.tafe_dispatch_runtime import (
        evaluate_dispatch_tick,
        tick_report_to_payload,
    )

    db, service = _flow_service(ctx)
    try:
        report = evaluate_dispatch_tick(service, subject_scope=subject_scope)
        payload = tick_report_to_payload(report)
    finally:
        db.close()
    _emit_cli_payload(payload, json_output=json_output)


@flow_dispatch_group.command("health")
@click.option("--subject-scope", default=None, help="Restrict aggregation to one flow subject scope.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def flow_dispatch_health_cmd(ctx: click.Context, subject_scope: str | None, json_output: bool) -> None:
    """Aggregate dispatch readiness across pending unclaimed stages.

    Read-only: reports readiness counts; never claims, spawns, or mutates.
    """
    from groundtruth_kb.tafe_dispatch_runtime import (
        evaluate_dispatch_health,
        health_report_to_payload,
    )

    db, service = _flow_service(ctx)
    try:
        report = evaluate_dispatch_health(service, subject_scope=subject_scope)
        payload = health_report_to_payload(report)
    finally:
        db.close()
    _emit_cli_payload(payload, json_output=json_output)


@flow_group.command("stuck")
@click.option("--subject-scope", default=None, help="Restrict detection to one flow subject scope.")
@click.option("--stalled-seconds", type=int, default=None, help="Override stalled-pending threshold (seconds).")
@click.option(
    "--owner-gate-stalled-seconds", type=int, default=None, help="Override owner-gate-stalled threshold (seconds)."
)
@click.option(
    "--lease-expiry-grace-seconds", type=int, default=None, help="Override expired-lease grace window (seconds)."
)
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def flow_stuck_cmd(
    ctx: click.Context,
    subject_scope: str | None,
    stalled_seconds: int | None,
    owner_gate_stalled_seconds: int | None,
    lease_expiry_grace_seconds: int | None,
    json_output: bool,
) -> None:
    """Detect and self-diagnose stuck TAFE flows (SPEC-TAFE-R3).

    Read-only: classifies why each active stage is stuck (expired lease, stalled
    pending, owner-gate stalled, failed-unrecovered) and attaches an advisory
    self-diagnosis from the per-stage-attempt telemetry. Never actuates recovery.
    """
    from groundtruth_kb.tafe_stuck_flow import (
        StuckThresholds,
        detect_stuck_flows,
        stuck_report_to_payload,
    )

    defaults = StuckThresholds()
    thresholds = StuckThresholds(
        stalled_seconds=stalled_seconds if stalled_seconds is not None else defaults.stalled_seconds,
        owner_gate_stalled_seconds=(
            owner_gate_stalled_seconds
            if owner_gate_stalled_seconds is not None
            else defaults.owner_gate_stalled_seconds
        ),
        lease_expiry_grace_seconds=(
            lease_expiry_grace_seconds
            if lease_expiry_grace_seconds is not None
            else defaults.lease_expiry_grace_seconds
        ),
    )

    db, service = _flow_service(ctx)
    try:
        report = detect_stuck_flows(service, thresholds=thresholds, subject_scope=subject_scope)
        payload = stuck_report_to_payload(report)
    finally:
        db.close()
    _emit_cli_payload(payload, json_output=json_output)


@flow_group.command("pilot")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
def flow_pilot_cmd(json_output: bool) -> None:
    """No-op Phase 0 placeholder for pilot mode."""
    _emit_cli_payload(
        _flow_noop_payload("flow pilot", detail="pilot activation requires later governed eligibility and approval."),
        json_output=json_output,
    )


@main.group("application")
def application_group() -> None:
    """GT-KB application registration and management."""
    pass


@application_group.command("register")
@click.argument("name")
@click.pass_context
def application_register_cmd(ctx: click.Context, name: str) -> None:
    """Register a developed application and enforce slot occupancy constraint."""
    import tomllib

    from groundtruth_kb.isolation.doctor_verdicts import evaluate_isolation_state
    from groundtruth_kb.isolation.validation import ValidationError, validate_self_completion_preflight

    config = _resolve_config(ctx)
    project_root = Path(config.project_root)

    # 1. Cardinality check: verify if there is any OTHER occupied slot
    state = evaluate_isolation_state(project_root)
    other_occupied = [slot for slot in state["occupied_slots"] if slot != name]
    if other_occupied:
        other_name = other_occupied[0]
        other_status = state["slots_status"][other_name]
        if other_status["trigger"] == "non_allowlisted_content":
            files_list = ", ".join(other_status["non_allowlisted_files"])
            click.echo(
                f"Error: Non-allowlisted content present in applications/{other_name}/: {files_list}. "
                f"Platform supports only one developed application at a time. "
                f"Run `gt application unregister {other_name}` to remove {other_name}.",
                err=True,
            )
        else:
            click.echo(
                f"Error: Platform supports only one developed application at a time. "
                f"Run `gt application unregister {other_name}` to remove {other_name}.",
                err=True,
            )
        raise SystemExit(1)

    # 2. Preflight validation check for the slot itself
    try:
        validate_self_completion_preflight(project_root, name)
    except ValidationError as exc:
        click.echo(f"Error: {str(exc)}", err=True)
        raise SystemExit(1) from exc

    # 3. Proceed with registration
    app_dir = project_root / "applications" / name
    app_dir.mkdir(parents=True, exist_ok=True)

    # Write application.toml if absent
    toml_path = app_dir / "application.toml"
    if not toml_path.is_file():
        content = f'[application]\nname = "{name}"\n'
        toml_path.write_text(content, encoding="utf-8")

    # Ensure harness-state exists
    harness_state_dir = app_dir / "harness-state"
    harness_state_dir.mkdir(parents=True, exist_ok=True)

    # Add to registry.toml
    registry_path = project_root / "applications" / "registry.toml"
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    apps = {}
    if registry_path.is_file():
        try:
            with open(registry_path, "rb") as f:
                data = tomllib.load(f)
            apps = data.get("applications", {})
            if not isinstance(apps, dict):
                apps = {}
        except Exception:  # intentional-catch: autogenerated check fix
            apps = {}

    apps[name] = {"slot": name}

    # Write back registry.toml
    lines = ["[applications]"]
    for k in sorted(apps.keys()):
        lines.append(f'{k} = {{ slot = "{k}" }}')
    registry_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    click.echo(f"Successfully registered application '{name}' in slot applications/{name}/")


@application_group.command("unregister")
@click.argument("name")
@click.pass_context
def application_unregister_cmd(ctx: click.Context, name: str) -> None:
    """Unregister a developed application slot."""
    import tomllib

    config = _resolve_config(ctx)
    project_root = Path(config.project_root)

    registry_path = project_root / "applications" / "registry.toml"
    if registry_path.is_file():
        try:
            with open(registry_path, "rb") as f:
                data = tomllib.load(f)
            apps = data.get("applications", {})
            if isinstance(apps, dict) and name in apps:
                del apps[name]
                lines = ["[applications]"]
                for k in sorted(apps.keys()):
                    lines.append(f'{k} = {{ slot = "{k}" }}')
                registry_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                click.echo(f"Successfully unregistered application '{name}'")
                return
        except Exception as e:  # intentional-catch: autogenerated check fix
            click.echo(f"Error reading registry: {e}", err=True)
            raise SystemExit(1) from e

    click.echo(f"Application '{name}' is not registered.")


@main.group("authority")
def authority_group() -> None:
    """Resolve GT-KB authority/source-of-truth terms."""


@authority_group.command("resolve")
@click.argument("subject")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def authority_resolve_cmd(ctx: click.Context, subject: str, json_output: bool) -> None:
    """Resolve an owner-facing term against the governed system-interface map."""
    from groundtruth_kb.authority import AuthorityResolutionError, format_resolution, resolve_subject

    config = _resolve_config(ctx)
    try:
        result = resolve_subject(subject, project_root=Path(config.project_root))
    except AuthorityResolutionError as exc:
        result = {"status": "error", "term": subject, "message": str(exc)}
    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    else:
        click.echo(format_resolution(result))
    if result.get("status") != "resolved":
        raise SystemExit(1)


@authority_group.command("status")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def authority_status_cmd(ctx: click.Context, json_output: bool) -> None:
    """Report compact system-interface map health."""
    from groundtruth_kb.authority import AuthorityResolutionError, compact_status, format_resolution

    config = _resolve_config(ctx)
    try:
        result = compact_status(project_root=Path(config.project_root))
    except AuthorityResolutionError as exc:
        result = {"status": "error", "message": str(exc), "errors": [str(exc)]}
    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    else:
        click.echo(format_resolution(result))
    if result.get("status") != "pass":
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# gt hygiene — deterministic repository hygiene services (WI-3420)
# ---------------------------------------------------------------------------


@main.group("hygiene")
def hygiene_group() -> None:
    """Repository hygiene services (drift discovery, sweeps)."""


@hygiene_group.command("sweep")
@click.option(
    "--root",
    type=click.Path(file_okay=False),
    default=".",
    show_default=True,
    help="Repository root to scan.",
)
@click.option(
    "--patterns-path",
    type=click.Path(dir_okay=False),
    default="config/governance/hygiene-sweep-patterns.toml",
    show_default=True,
    help="Pattern-set TOML registry path (resolved relative to --root if not absolute).",
)
@click.option("--pattern-set", default=None, help="Limit to a single pattern by id; default scans all.")
@click.option(
    "--output",
    type=click.Path(file_okay=False),
    default=None,
    help="Output directory; default: .gtkb-state/hygiene-sweep/<run-id>/.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "md", "both"]),
    default="both",
    show_default=True,
    help="Output formats to emit.",
)
@click.option(
    "--report-only/--fail-on-findings",
    default=True,
    show_default=True,
    help="Exit-code policy: --report-only always exits 0; --fail-on-findings exits 2 when any findings emitted.",
)
def hygiene_sweep(
    root: str,
    patterns_path: str,
    pattern_set: str | None,
    output: str | None,
    fmt: str,
    report_only: bool,
) -> None:
    """Run a deterministic hygiene sweep against the repository.

    Walks ``--root`` against the pattern-set TOML registry and emits findings
    as JSON + markdown to ``--output``. Read-only against the repo; mutates
    only its own output directory. No MemBase, bridge, or governance artifact
    creation.
    """
    root_path = Path(root).resolve()
    patterns_full = Path(patterns_path)
    if not patterns_full.is_absolute():
        patterns_full = root_path / patterns_full
    try:
        result = run_sweep(root_path, patterns_full, pattern_set)
    except PatternSetError as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(2) from exc
    out_dir = Path(output) if output else root_path / ".gtkb-state" / "hygiene-sweep" / result.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    if fmt in ("json", "both"):
        emit_json(result, out_dir / "findings.json")
    if fmt in ("md", "both"):
        emit_markdown(result, out_dir / "summary.md")
    click.echo(f"hygiene sweep: {result.finding_count} finding(s); output: {out_dir}")
    if not report_only and result.finding_count > 0:
        raise SystemExit(2)


# ---------------------------------------------------------------------------
# gt validate - deterministic validation services
# ---------------------------------------------------------------------------


@main.group("validate")
def validate_group() -> None:
    """Deterministic validation services."""


@validate_group.command("spec-coherence")
@click.option("--rule-set", default=None, help="Limit to one coherence rule id; default loads all rules.")
@click.option(
    "--output",
    type=click.Path(file_okay=False),
    default=None,
    help="Output directory; default: .gtkb-state/spec-coherence/<run-id>/.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "md", "both"]),
    default="both",
    show_default=True,
    help="Output formats to emit.",
)
@click.option("--fail-on-findings", is_flag=True, default=False, help="Exit 5 when findings are emitted.")
@click.option("--db-path", type=click.Path(dir_okay=False), default=None, help="Override GroundTruth DB path.")
@click.pass_context
def validate_spec_coherence(
    ctx: click.Context,
    rule_set: str | None,
    output: str | None,
    fmt: str,
    fail_on_findings: bool,
    db_path: str | None,
) -> None:
    """Run deterministic Layer A spec-coherence checks.

    Reads ``current_specifications`` only and emits review-candidate findings as
    JSON and/or markdown. It does not mutate MemBase or file remediation work.
    """
    config = _resolve_config(ctx)
    rules_path = config.project_root / "config" / "governance" / "spec-coherence-rules.toml"
    db = Path(db_path) if db_path else config.db_path
    if not db.is_absolute():
        db = config.project_root / db
    try:
        rules = load_coherence_rules(rules_path, name=rule_set)
        specs = load_coherence_specs_from_db(db)
        findings = run_coherence_checks(specs, rules)
    except CoherenceRuleError as exc:
        raise click.ClickException(str(exc)) from exc
    result = make_coherence_result(db_path=db, rule_set_path=rules_path, specs=specs, rules=rules, findings=findings)
    out_dir = Path(output) if output else config.project_root / ".gtkb-state" / "spec-coherence" / result.run_id
    if not out_dir.is_absolute():
        out_dir = config.project_root / out_dir
    if fmt in ("json", "both"):
        emit_coherence_json(result, out_dir / "findings.json")
    if fmt in ("md", "both"):
        emit_coherence_markdown(result, out_dir / "summary.md")
    click.echo(f"spec coherence: {result.finding_count} finding(s); output: {out_dir}")
    if fail_on_findings and result.finding_count > 0:
        raise SystemExit(5)


# ---------------------------------------------------------------------------
# gt generate-approval-packet
# ---------------------------------------------------------------------------


@main.command("generate-approval-packet")
@click.option("--kind", type=click.Choice(["narrative", "formal"]), required=True, help="Packet kind to generate.")
@click.option("--target", type=click.Path(), default=None, help="Narrative target path to read.")
@click.option("--artifact-id", required=True, help="Approval packet artifact id.")
@click.option("--action", type=click.Choice(["create", "update", "delete"]), required=True, help="Artifact action.")
@click.option("--source-ref", required=True, help="Bridge id or deliberation reference authorizing the change.")
@click.option("--explicit-change-request", required=True, help="Owner-visible change request text.")
@click.option("--change-reason", required=True, help="Short rationale for the packet.")
@click.option(
    "--approval-mode",
    type=click.Choice(["approve", "acknowledge", "edit-and-approve", "auto"]),
    required=True,
    help="Approval mode recorded in the packet.",
)
@click.option("--changed-by", required=True, help="Harness or actor id recording the packet.")
@click.option("--out", type=click.Path(), default=None, help="Packet output path.")
@click.option("--stage/--no-stage", default=False, show_default=True, help="Stage the packet and narrative target.")
@click.option(
    "--validate-after/--no-validate-after",
    default=True,
    show_default=True,
    help="Read back and validate the written packet.",
)
@click.option("--artifact-type", default=None, help="Formal artifact type, required for --kind formal.")
@click.option("--content-file", type=click.Path(), default=None, help="Formal artifact content file.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def generate_approval_packet(
    ctx: click.Context,
    kind: str,
    target: str | None,
    artifact_id: str,
    action: str,
    source_ref: str,
    explicit_change_request: str,
    change_reason: str,
    approval_mode: str,
    changed_by: str,
    out: str | None,
    stage: bool,
    validate_after: bool,
    artifact_type: str | None,
    content_file: str | None,
    json_output: bool,
) -> None:
    """Generate formal or narrative-artifact approval packets."""
    config = _resolve_config(ctx)
    request = GenerateApprovalPacketRequest(
        kind=kind,
        target=Path(target) if target else None,
        artifact_id=artifact_id,
        action=action,
        source_ref=source_ref,
        explicit_change_request=explicit_change_request,
        change_reason=change_reason,
        approval_mode=approval_mode,
        changed_by=changed_by,
        out=Path(out) if out else None,
        stage=stage,
        validate_after=validate_after,
        artifact_type=artifact_type,
        content_file=Path(content_file) if content_file else None,
    )
    try:
        result = run_generate_approval_packet(config, request)
    except GenerateApprovalPacketError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(format_result(result, json_output=json_output))


# ---------------------------------------------------------------------------
# gt init
# ---------------------------------------------------------------------------


@main.command()
@click.argument("project_name", default="my-project")
@click.option("--dir", "target_dir", type=click.Path(), default=None, help="Target directory (default: ./<name>)")
@click.pass_context
def init(ctx: click.Context, project_name: str, target_dir: str | None) -> None:
    """Create a new GroundTruth project with config and empty database."""
    target = Path(target_dir) if target_dir else Path.cwd() / project_name
    target.mkdir(parents=True, exist_ok=True)

    toml_path = target / "groundtruth.toml"
    if toml_path.exists():
        click.echo(f"groundtruth.toml already exists in {target}")
        raise SystemExit(1)

    toml_content = _DEFAULT_TOML.format(project_name=project_name)
    toml_path.write_text(toml_content, encoding="utf-8")

    # Create empty database
    db_path = target / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    db.close()

    click.echo(f"Initialized GroundTruth project in {target}")
    click.echo(f"  Config: {toml_path}")
    click.echo(f"  Database: {db_path}")
    click.echo(f"\nNext: cd {target} && gt seed --example")


# ---------------------------------------------------------------------------
# gt bootstrap-desktop
# ---------------------------------------------------------------------------


@main.command("bootstrap-desktop")
@click.argument("project_name")
@click.option("--dir", "target_dir", type=click.Path(), default=None, help="Target directory (default: ./<name>)")
@click.option("--owner", default="Your Organization", show_default=True, help="Project owner or client name")
@click.option(
    "--project-type",
    default="AI Service Prototype",
    show_default=True,
    help="Project type label written into the scaffold",
)
@click.option("--brand-mark", default="GT", show_default=True, help="Short brand mark for the KB UI")
@click.option("--brand-color", default="#2563eb", show_default=True, help="Primary brand color for the KB UI")
@click.option(
    "--copyright",
    "copyright_notice",
    default=None,
    help="Copyright notice to write into scaffolded files",
)
@click.option("--include-ci/--no-include-ci", default=True, show_default=True, help="Copy CI workflow templates")
@click.option("--init-git", is_flag=True, help="Initialize a git repository in the target directory")
@click.option(
    "--seed-example/--no-seed-example",
    default=True,
    show_default=True,
    help="Seed governance specs plus the example domain specs/tests",
)
def bootstrap_desktop_cmd(
    project_name: str,
    target_dir: str | None,
    owner: str,
    project_type: str,
    brand_mark: str,
    brand_color: str,
    copyright_notice: str | None,
    include_ci: bool,
    init_git: bool,
    seed_example: bool,
) -> None:
    """Create a same-day desktop prototype scaffold for a new GroundTruth project."""
    target = Path(target_dir) if target_dir else Path.cwd() / project_name
    options = DesktopBootstrapOptions(
        project_name=project_name,
        owner=owner,
        project_type=project_type,
        target_dir=target,
        brand_mark=brand_mark,
        brand_color=brand_color,
        copyright_notice=copyright_notice or "",
        include_ci=include_ci,
        init_git=init_git,
        seed_example=seed_example,
    )
    try:
        created = bootstrap_desktop_project(options)
    except FileNotFoundError as exc:
        raise click.ClickException(f"Required tool not found: {exc.filename}") from exc
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    except OSError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(bootstrap_summary(created, include_ci=include_ci, init_git=init_git, seed_example=seed_example))


# ---------------------------------------------------------------------------
# gt assert
# ---------------------------------------------------------------------------


@main.command("assert")
@click.option("--spec", "spec_id", default=None, help="Run assertions for a single spec ID")
@click.option("--triggered-by", default="cli", help="Trigger label (default: cli)")
@click.pass_context
def assert_cmd(ctx: click.Context, spec_id: str | None, triggered_by: str) -> None:
    """Run feature assertions against the project codebase."""
    from groundtruth_kb.assertions import format_summary, run_all_assertions

    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        project_root = config.project_root.resolve()
        summary = run_all_assertions(db, project_root, triggered_by=triggered_by, spec_id=spec_id)
        click.echo(format_summary(summary))
        if summary.get("failed", 0) > 0:
            raise SystemExit(1)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# gt seed
# ---------------------------------------------------------------------------


@main.command()
@click.option("--example", is_flag=True, help="Load example domain specs and tests")
@click.pass_context
def seed(ctx: click.Context, example: bool) -> None:
    """Load generic governance starter data (and optionally example specs)."""
    from groundtruth_kb.seed import load_example_seeds, load_governance_seeds

    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        gov_count = load_governance_seeds(db)
        click.echo(f"Loaded {gov_count} governance specs.")

        if example:
            ex_count = load_example_seeds(db)
            click.echo(f"Loaded {ex_count} example specs + tests.")

        summary = db.get_summary()
        click.echo(
            f"\nDatabase now has {summary['spec_total']} specs, "
            f"{summary['test_artifact_count']} tests, "
            f"{summary['work_item_total']} work items."
        )
    finally:
        db.close()


# ---------------------------------------------------------------------------
# gt summary
# ---------------------------------------------------------------------------


@main.command()
@click.pass_context
def summary(ctx: click.Context) -> None:
    """Print spec/test/work-item counts."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        s = db.get_summary()
        click.echo(f"\n{'=' * 50}")
        click.echo(f"  {config.app_title} — Summary")
        click.echo(f"{'=' * 50}")
        click.echo(f"  Specifications:     {s['spec_total']} total")
        for status, count in sorted(s["spec_counts"].items()):
            click.echo(f"    {status}: {count}")
        click.echo(f"  Tests:              {s['test_artifact_count']}")
        click.echo(f"  Test procedures:    {s['test_procedure_count']}")
        click.echo(f"  Work items:         {s['work_item_total']}")
        for status, count in sorted(s["work_item_counts"].items()):
            click.echo(f"    {status}: {count}")
        click.echo(f"  Projects:           {s['project_total']}")
        for status, count in sorted(s["project_counts"].items()):
            click.echo(f"    {status}: {count}")
        click.echo(f"  Documents:          {s['document_count']}")
        a_pass, a_fail = s["assertions_passed"], s["assertions_failed"]
        click.echo(f"  Assertions run:     {s['assertions_total']} ({a_pass} passed, {a_fail} failed)")
        click.echo(f"{'=' * 50}\n")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# gt status
# ---------------------------------------------------------------------------


@main.command("status")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.option("--startup", is_flag=True, default=False, help="Emit compact startup-safe status.")
@click.option(
    "--component",
    "components",
    multiple=True,
    type=click.Choice(
        [
            "project",
            "db",
            "chroma",
            "bridge",
            "bridge-dispatch",
            "dashboard",
            "hooks",
            "resource-registry",
            "system-interface-map",
            "startup",
        ],
        case_sensitive=False,
    ),
    help="Limit output to one component; repeat for multiple components.",
)
@click.pass_context
def status_cmd(ctx: click.Context, json_output: bool, startup: bool, components: tuple[str, ...]) -> None:
    """Report deterministic local operating state."""
    from groundtruth_kb.operating_state import (
        collect_operating_state,
        format_operating_state_text,
        format_startup_operating_state,
    )

    config = _resolve_config(ctx)
    selected = tuple(component.lower() for component in components) or None
    try:
        state = collect_operating_state(config.project_root, config=config, startup=startup, components=selected)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(state.to_json_dict(), indent=2, sort_keys=True))
    elif startup:
        click.echo(format_startup_operating_state(state))
    else:
        click.echo(format_operating_state_text(state))

    if state.overall_status == "FAIL":
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# gt backlog
# ---------------------------------------------------------------------------


@main.group()
def backlog() -> None:
    """Unified backlog commands backed by MemBase work_items."""


@backlog.command("add")
@click.option("--title", required=True, help="Work item title.")
@click.option(
    "--origin",
    required=True,
    type=click.Choice(["new", "hygiene", "improvement", "defect", "regression"]),
    help="Work item origin classification.",
)
@click.option("--component", required=True, help="Component taxonomy value.")
@click.option(
    "--priority",
    type=click.Choice(["P0", "P1", "P2", "P3"]),
    default="P3",
    show_default=True,
    help="Candidate priority.",
)
@click.option("--project-name", default=None, help="Project grouping for the candidate.")
@click.option("--subproject-name", default=None, help="Sub-project grouping for the candidate.")
@click.option("--description", default=None, help="Longer description of the candidate work.")
@click.option("--source-owner-directive", default=None, help="Owner directive that motivated this candidate.")
@click.option("--source-spec-id", default=None, help="Specification this work item relates to.")
@click.option("--source-deliberation-query", default=None, help="Deliberation search query that surfaced this work.")
@click.option("--related-spec-ids", default=None, help="JSON array of related spec ids.")
@click.option("--related-deliberation-ids", default=None, help="JSON array of related DELIB ids.")
@click.option("--related-bridge-threads", default=None, help="JSON array of related bridge file paths.")
@click.option("--depends-on-work-items", default=None, help="JSON array of WI ids this candidate depends on.")
@click.option("--acceptance-summary", default=None, help="Acceptance summary for the candidate.")
@click.option("--regression-visibility", default=None, help="Regression-visibility note for the candidate.")
@click.option("--change-reason", required=True, help="History reason for the insert.")
@click.option("--dry-run", is_flag=True, help="Report the allocated id without writing the row.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def backlog_add(
    ctx: click.Context,
    title: str,
    origin: str,
    component: str,
    priority: str,
    project_name: str | None,
    subproject_name: str | None,
    description: str | None,
    source_owner_directive: str | None,
    source_spec_id: str | None,
    source_deliberation_query: str | None,
    related_spec_ids: str | None,
    related_deliberation_ids: str | None,
    related_bridge_threads: str | None,
    depends_on_work_items: str | None,
    acceptance_summary: str | None,
    regression_visibility: str | None,
    change_reason: str,
    dry_run: bool,
    json_output: bool,
) -> None:
    """Capture a single MemBase work_items backlog candidate row.

    Capture is not implementation approval — the new row records a candidate
    for future consideration. The command writes only to MemBase work_items;
    it never mutates memory/MEMORY.md.
    """
    from groundtruth_kb.cli_backlog_add import BacklogAddError, BacklogAddRequest, add_backlog_item

    config = _resolve_config(ctx)
    request = BacklogAddRequest(
        title=title,
        origin=origin,
        component=component,
        priority=priority,
        project_name=project_name,
        subproject_name=subproject_name,
        description=description,
        source_owner_directive=source_owner_directive,
        source_spec_id=source_spec_id,
        source_deliberation_query=source_deliberation_query,
        related_spec_ids_at_creation=related_spec_ids,
        related_deliberation_ids=related_deliberation_ids,
        related_bridge_threads=related_bridge_threads,
        depends_on_work_items=depends_on_work_items,
        acceptance_summary=acceptance_summary,
        regression_visibility=regression_visibility,
        change_reason=change_reason,
        dry_run=dry_run,
    )
    try:
        result = add_backlog_item(config, request)
    except (BacklogAddError, RuntimeError) as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True, default=str))
        return
    action = "Would create" if result["dry_run"] else "Created"
    click.echo(f"{action} {result['id']}")


@backlog.command("authorize-implementation")
@click.argument("work_item_id")
@click.option(
    "--owner-decision",
    default=None,
    help="Existing owner-authority deliberation id (DELIB-NNNN) to cite as the authorization basis.",
)
@click.option("--auq-id", default=None, help="Fresh AUQ evidence id (records a new owner_conversation deliberation).")
@click.option("--auq-answer", default=None, help="Owner answer text for the fresh AUQ evidence.")
@click.option(
    "--decision-content-file",
    default=None,
    help="In-root file whose contents become the fresh owner-decision deliberation body.",
)
@click.option("--decision-title", default=None, help="Title for the fresh deliberation (fresh-AUQ path only).")
@click.option("--decision-summary", default=None, help="Summary for the fresh deliberation (fresh-AUQ path only).")
@click.option(
    "--project",
    "project_id",
    default=None,
    help="Project to authorize (defaults to the work item's sole active project membership).",
)
@click.option(
    "--include-spec",
    "include_spec_ids",
    multiple=True,
    help="Governing specification to include (repeatable; at least one required).",
)
@click.option(
    "--allowed-mutation",
    "allowed_mutation_classes",
    multiple=True,
    help="Allowed mutation class (repeatable; at least one required).",
)
@click.option("--forbid", "forbidden_operations", multiple=True, help="Forbidden operation (repeatable).")
@click.option("--id", "authorization_id", default=None, help="Explicit authorization id.")
@click.option("--name", "authorization_name", default=None, help="Authorization name.")
@click.option("--scope", "scope_summary", default=None, help="Bounded authorization scope summary.")
@click.option("--change-reason", required=True, help="History reason for the authorization and deliberation writes.")
@click.option("--session-id", default=None, help="Session id for the fresh deliberation (fresh-AUQ path only).")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Resolve and validate, then report the proposed authorization without writing.",
)
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def backlog_authorize_implementation(
    ctx: click.Context,
    work_item_id: str,
    owner_decision: str | None,
    auq_id: str | None,
    auq_answer: str | None,
    decision_content_file: str | None,
    decision_title: str | None,
    decision_summary: str | None,
    project_id: str | None,
    include_spec_ids: tuple[str, ...],
    allowed_mutation_classes: tuple[str, ...],
    forbidden_operations: tuple[str, ...],
    authorization_id: str | None,
    authorization_name: str | None,
    scope_summary: str | None,
    change_reason: str,
    session_id: str | None,
    dry_run: bool,
    json_output: bool,
) -> None:
    """Authorize a single owner-selected work item for implementation.

    Collapses the record-owner-decision-deliberation plus
    create-project-authorization plumbing into one governed command. Requires
    owner-decision evidence (an existing owner-authority deliberation via
    --owner-decision, or fresh AUQ evidence) and fails closed without it; it does
    not let Prime self-authorize and it changes no gate logic.
    """
    from groundtruth_kb.cli_backlog_authorize_implementation import (
        AuthorizeImplementationError,
        AuthorizeImplementationRequest,
        authorize_implementation,
    )

    config = _resolve_config(ctx)
    request = AuthorizeImplementationRequest(
        work_item_id=work_item_id,
        owner_decision=owner_decision,
        auq_id=auq_id,
        auq_answer=auq_answer,
        decision_content_file=decision_content_file,
        decision_title=decision_title,
        decision_summary=decision_summary,
        project_id=project_id,
        include_spec_ids=include_spec_ids,
        allowed_mutation_classes=allowed_mutation_classes,
        forbidden_operations=forbidden_operations,
        authorization_id=authorization_id,
        authorization_name=authorization_name,
        scope_summary=scope_summary,
        change_reason=change_reason,
        session_id=session_id,
        dry_run=dry_run,
    )
    try:
        result = authorize_implementation(config, request)
    except (AuthorizeImplementationError, RuntimeError) as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True, default=str))
        return
    if result["dry_run"]:
        click.echo(
            f"Would authorize {result['work_item_id']} in {result['project_id']} "
            f"(owner decision {result['owner_decision']})."
        )
        return
    click.echo(
        f"Authorized {result['work_item_id']} in {result['project_id']} with "
        f"{result['authorization_id']} (owner decision {result['owner_decision']})."
    )


@backlog.command("add-work-item")
@click.option("--title", required=True, help="Work item title.")
@click.option(
    "--origin",
    required=True,
    type=click.Choice(["new", "hygiene", "improvement", "defect", "regression"]),
    help="Work item origin classification.",
)
@click.option("--component", required=True, help="Component taxonomy value.")
@click.option(
    "--priority",
    type=click.Choice(["P0", "P1", "P2", "P3"]),
    default="P3",
    show_default=True,
    help="Candidate priority.",
)
@click.option("--project-name", default=None, help="Project grouping for the work item.")
@click.option("--subproject-name", default=None, help="Sub-project grouping for the work item.")
@click.option("--description", default=None, help="Longer description of the work.")
@click.option("--source-owner-directive", default=None, help="Owner directive that motivated this work.")
@click.option("--source-spec-id", default=None, help="Specification this work item relates to.")
@click.option("--test-title", required=True, help="GOV-12 linked test title.")
@click.option(
    "--test-type",
    required=True,
    type=click.Choice(["assertion", "e2e", "integration", "unit", "manual"]),
    help="GOV-12 linked test type.",
)
@click.option("--test-expected-outcome", required=True, help="GOV-03 unambiguous expected outcome for the test.")
@click.option("--test-spec-id", default=None, help="Spec the test links to (defaults to --source-spec-id).")
@click.option(
    "--test-plan-phase",
    default=None,
    help="GOV-13 test-plan phase id to assign the test to (REQUIRED for non-dry-run creation).",
)
@click.option("--change-reason", required=True, help="History reason for the inserts.")
@click.option("--dry-run", is_flag=True, help="Report allocated ids + validate the phase without writing.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def backlog_add_work_item(
    ctx: click.Context,
    title: str,
    origin: str,
    component: str,
    priority: str,
    project_name: str | None,
    subproject_name: str | None,
    description: str | None,
    source_owner_directive: str | None,
    source_spec_id: str | None,
    test_title: str,
    test_type: str,
    test_expected_outcome: str,
    test_spec_id: str | None,
    test_plan_phase: str | None,
    change_reason: str,
    dry_run: bool,
    json_output: bool,
) -> None:
    """Create a work item + linked test (GOV-12) + test-plan phase assignment (GOV-13).

    Deterministic single-invocation replacement for the kb-work-item skill's
    inline ``db.insert_*`` snippets. ``--test-plan-phase`` is REQUIRED for
    non-dry-run creation (GOV-13 fail-closed); a missing or unresolvable phase
    exits non-zero before any work-item/test/phase mutation.
    """
    from groundtruth_kb.cli_backlog_add_work_item import (
        AddWorkItemError,
        AddWorkItemRequest,
        add_work_item_with_test,
    )

    config = _resolve_config(ctx)
    request = AddWorkItemRequest(
        title=title,
        origin=origin,
        component=component,
        priority=priority,
        project_name=project_name,
        subproject_name=subproject_name,
        description=description,
        source_owner_directive=source_owner_directive,
        source_spec_id=source_spec_id,
        change_reason=change_reason,
        test_title=test_title,
        test_type=test_type,
        test_expected_outcome=test_expected_outcome,
        test_spec_id=test_spec_id,
        test_plan_phase=test_plan_phase,
        dry_run=dry_run,
    )
    try:
        result = add_work_item_with_test(config, request)
    except (AddWorkItemError, RuntimeError) as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True, default=str))
        return
    action = "Would create" if result["dry_run"] else "Created"
    click.echo(f"{action} {result['work_item_id']} + {result['test_id']} -> phase {result['phase_id']}")


_PROJECT_CONTAINS_FIELDS = (
    "id",
    "name",
    "status",
    "purpose",
    "target_outcome",
    "scope_note",
    "notes",
    "source_project_name",
    "source_subproject_name",
)
_WORK_ITEM_CONTAINS_FIELDS = (
    "id",
    "title",
    "description",
    "project_name",
    "subproject_name",
    "stage",
    "resolution_status",
    "status_detail",
    "origin",
    "component",
    "priority",
    "acceptance_summary",
)


def _matches_any_exact(row: dict[str, object], key: str, accepted: tuple[str, ...]) -> bool:
    if not accepted:
        return True
    value = row.get(key)
    return value is not None and str(value) in set(accepted)


def _matches_exact(row: dict[str, object], key: str, expected: str | None) -> bool:
    if expected is None:
        return True
    value = row.get(key)
    return value is not None and str(value) == expected


def _matches_contains(row: dict[str, object], fields: tuple[str, ...], terms: tuple[str, ...]) -> bool:
    normalized_terms = tuple(term.casefold() for term in terms if term.strip())
    if not normalized_terms:
        return True
    haystack = " ".join(str(row.get(field) or "") for field in fields).casefold()
    return all(term in haystack for term in normalized_terms)


def _apply_limit(rows: list[dict[str, object]], limit: int | None) -> list[dict[str, object]]:
    if limit is None:
        return rows
    return rows[:limit]


# ---------------------------------------------------------------------------
# gt core-specs
# ---------------------------------------------------------------------------


@main.group(name="core-specs")
def core_specs_cmd() -> None:
    """Read core application specification intake state."""


def _resolve_core_specs_project(
    db: KnowledgeDB,
    *,
    project_id: str | None,
    project_name: str | None,
) -> dict[str, object]:
    if bool(project_id) == bool(project_name):
        raise click.UsageError("Provide exactly one of --project-id or --project-name.")
    if project_id:
        project = db.get_project(project_id)
        if project is None:
            raise click.ClickException(f"Project not found: {project_id}")
        return project

    assert project_name is not None
    needle = project_name.casefold()
    matches = [
        project
        for project in db.list_projects(include_terminal=True)
        if str(project.get("name", "")).casefold() == needle
    ]
    if not matches:
        raise click.ClickException(f"Project not found by name: {project_name}")
    if len(matches) > 1:
        ids = ", ".join(str(project["id"]) for project in matches)
        raise click.ClickException(f"Project name is ambiguous: {project_name} ({ids})")
    return matches[0]


def _core_specs_project_payload(project: dict[str, object]) -> dict[str, object]:
    return {"id": project.get("id"), "name": project.get("name")}


@core_specs_cmd.command("status")
@click.option("--project-id", default=None, help="Project id to inspect.")
@click.option("--project-name", default=None, help="Project name to inspect.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--no-fail", is_flag=True, help="Exit zero even when intake is incomplete.")
@click.pass_context
def core_specs_status_cmd(
    ctx: click.Context,
    project_id: str | None,
    project_name: str | None,
    json_output: bool,
    no_fail: bool,
) -> None:
    """Report baseline core-spec intake completion state."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        project = _resolve_core_specs_project(db, project_id=project_id, project_name=project_name)
        resolved_project_id = str(project["id"])
        slots = list(slot_statuses(db, resolved_project_id))
        missing_slot = next_missing_slot(db, resolved_project_id)
    finally:
        db.close()

    completed_count = sum(1 for slot in slots if slot["complete"])
    payload = {
        "project": _core_specs_project_payload(project),
        "complete": missing_slot is None,
        "completed_slots": completed_count,
        "total_slots": len(slots),
        "next_slot": missing_slot,
        "slots": slots,
    }
    if json_output:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
    else:
        status = "complete" if payload["complete"] else "incomplete"
        click.echo(f"{project['id']}: {status} ({completed_count}/{len(slots)} slots complete)")
        if missing_slot is not None:
            question = next(slot for slot in slots if slot["name"] == missing_slot)
            click.echo(f"Next question: {question['label']} ({question['name']})")
            click.echo(str(question["prompt"]))
        for slot in slots:
            slot_status = "complete" if slot["complete"] else "missing"
            click.echo(f"{slot_status}\t{slot['name']}\t{slot['label']}")

    if missing_slot is not None and not no_fail:
        raise SystemExit(1)


@core_specs_cmd.command("next-question")
@click.option("--project-id", default=None, help="Project id to inspect.")
@click.option("--project-name", default=None, help="Project name to inspect.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def core_specs_next_question_cmd(
    ctx: click.Context,
    project_id: str | None,
    project_name: str | None,
    json_output: bool,
) -> None:
    """Report the next missing core-spec intake question."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        project = _resolve_core_specs_project(db, project_id=project_id, project_name=project_name)
        question = next_question(db, str(project["id"]))
    finally:
        db.close()

    payload = {
        "project": _core_specs_project_payload(project),
        "complete": question is None,
        "slot": question,
        "question": question["prompt"] if question else None,
    }
    if json_output:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
        return
    if question is None:
        click.echo(f"All core spec slots are complete for {project['id']}.")
        return
    click.echo(f"{question['label']} ({question['name']})")
    click.echo(question["prompt"])


@backlog.command("list")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--all", "include_verified", is_flag=True, help="Include verified/closed work items.")
@click.option("--id", "work_item_ids", multiple=True, help="Limit to an explicit work item id; repeatable.")
@click.option("--project", "project_name", default=None, help="Limit to a project_name value.")
@click.option("--subproject", "subproject_name", default=None, help="Limit to a subproject_name value.")
@click.option("--priority", "priorities", multiple=True, help="Limit to one priority; repeatable.")
@click.option(
    "--resolution-status",
    "resolution_statuses",
    multiple=True,
    help="Limit to one resolution_status; repeatable.",
)
@click.option("--stage", "stages", multiple=True, help="Limit to one stage; repeatable.")
@click.option("--origin", "origins", multiple=True, help="Limit to one origin; repeatable.")
@click.option("--component", "components", multiple=True, help="Limit to one component; repeatable.")
@click.option("--contains", "contains_terms", multiple=True, help="Case-insensitive text filter; repeatable.")
@click.option("--limit", type=click.IntRange(min=1), default=None, help="Return at most N rows.")
@click.pass_context
def backlog_list(
    ctx: click.Context,
    json_output: bool,
    include_verified: bool,
    work_item_ids: tuple[str, ...],
    project_name: str | None,
    subproject_name: str | None,
    priorities: tuple[str, ...],
    resolution_statuses: tuple[str, ...],
    stages: tuple[str, ...],
    origins: tuple[str, ...],
    components: tuple[str, ...],
    contains_terms: tuple[str, ...],
    limit: int | None,
) -> None:
    """List unified backlog items from MemBase work_items."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        include_terminal = include_verified or bool(work_item_ids) or bool(resolution_statuses)
        items = db.list_work_items() if include_terminal else db.get_open_work_items()
    finally:
        db.close()
    items = [
        item
        for item in items
        if _matches_any_exact(item, "id", work_item_ids)
        and _matches_exact(item, "project_name", project_name)
        and _matches_exact(item, "subproject_name", subproject_name)
        and _matches_any_exact(item, "priority", priorities)
        and _matches_any_exact(item, "resolution_status", resolution_statuses)
        and _matches_any_exact(item, "stage", stages)
        and _matches_any_exact(item, "origin", origins)
        and _matches_any_exact(item, "component", components)
        and _matches_contains(item, _WORK_ITEM_CONTAINS_FIELDS, contains_terms)
    ]
    items = _apply_limit(items, limit)

    if json_output:
        click.echo(json.dumps(items, indent=2, sort_keys=True))
        return
    if not items:
        click.echo("No backlog items found.")
        return
    for item in items:
        order = item.get("implementation_order")
        order_prefix = "-" if order is None else str(order)
        status = item.get("status_detail") or item.get("resolution_status")
        title = item.get("title") or item["id"]
        click.echo(f"{order_prefix}\t{item['id']}\t{status}\t{title}")


def _format_work_item_detail(item: dict[str, object], history: list[dict[str, object]] | None = None) -> str:
    """Render a current work item row for human CLI output."""
    fields = [
        ("ID", "id"),
        ("Version", "version"),
        ("Title", "title"),
        ("Priority", "priority"),
        ("Project", "project_name"),
        ("Subproject", "subproject_name"),
        ("Stage", "stage"),
        ("Resolution Status", "resolution_status"),
        ("Status Detail", "status_detail"),
        ("Origin", "origin"),
        ("Component", "component"),
        ("Implementation Order", "implementation_order"),
    ]
    lines: list[str] = []
    for label, key in fields:
        value = item.get(key)
        if value is not None and value != "":
            lines.append(f"{label}: {value}")

    for label, key in (("Description", "description"), ("Acceptance Summary", "acceptance_summary")):
        value = str(item.get(key) or "").strip()
        lines.append("")
        lines.append(f"{label}:")
        if value:
            lines.extend(f"  {line}" for line in value.splitlines())
        else:
            lines.append("  (none)")

    if history is not None:
        lines.append("")
        lines.append("Version History:")
        if not history:
            lines.append("  (none)")
        for row in history:
            version = row.get("version")
            changed_at = row.get("changed_at") or ""
            changed_by = row.get("changed_by") or ""
            reason = row.get("change_reason") or ""
            lines.append(f"  - v{version} {changed_at} {changed_by}: {reason}")

    return "\n".join(lines)


@backlog.command("show")
@click.argument("work_item_id")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--history", is_flag=True, help="Include the full work-item version chain.")
@click.pass_context
def backlog_show(ctx: click.Context, work_item_id: str, json_output: bool, history: bool) -> None:
    """Show one unified backlog item from MemBase work_items."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        item = db.get_work_item(work_item_id)
        if item is None:
            raise click.ClickException(f"Work item not found: {work_item_id}")
        history_rows = db.get_work_item_history(work_item_id) if history else None
    finally:
        db.close()

    if json_output:
        payload: dict[str, object] | list[dict[str, object]] | object
        payload = {"current": item, "history": history_rows or []} if history else item
        click.echo(json.dumps(payload, indent=2, sort_keys=True, default=str))
        return

    click.echo(_format_work_item_detail(item, history_rows))


@backlog.command("status")
@click.option(
    "--project",
    "project",
    default=None,
    help="Limit the report to a single project id (e.g. PROJECT-GTKB-X).",
)
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option(
    "--with-orphans",
    is_flag=True,
    help="Include work items with no active project membership row.",
)
@click.option(
    "--with-retire-ready",
    is_flag=True,
    help="Annotate completion-ready project authorizations via the canonical scanner module.",
)
@click.option(
    "--with-verified-coverage",
    is_flag=True,
    help="Annotate per-work-item VERIFIED-bridge coverage via the canonical scanner module.",
)
@click.pass_context
def backlog_status(
    ctx: click.Context,
    project: str | None,
    json_output: bool,
    with_orphans: bool,
    with_retire_ready: bool,
    with_verified_coverage: bool,
) -> None:
    """Report unified backlog status: projects, work-item rollups, optional scanner-backed annotations.

    Read-only: no MemBase writes and no bridge artifact mutation. Base output
    reports raw resolution_status counts and does not invent a
    terminal/non-terminal definition. Scanner-backed flags
    (``--with-retire-ready`` / ``--with-verified-coverage``) attach a
    ``scanner_caveat`` field naming the canonical in-flight scanner-fix
    thread.
    """
    from groundtruth_kb.cli_backlog_status import (
        BacklogStatusRequest,
        build_backlog_status,
    )

    config = _resolve_config(ctx)
    request = BacklogStatusRequest(
        project=project,
        with_orphans=with_orphans,
        with_retire_ready=with_retire_ready,
        with_verified_coverage=with_verified_coverage,
    )
    result = build_backlog_status(config, request)

    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True, default=str))
        return

    summary = result["summary"]
    click.echo(
        f"Projects: {summary['project_count']} "
        f"(doubled-prefix: {summary['doubled_prefix_project_count']}) | "
        f"Active memberships: {summary['total_active_memberships']}"
    )
    for project_row in result["projects"]:
        flag = " [DOUBLED-PREFIX]" if project_row["doubled_prefix_flag"] else ""
        breakdown = ", ".join(f"{k}={v}" for k, v in project_row["resolution_status_breakdown"].items())
        click.echo(
            f"  {project_row['id']} ({project_row['status']}) "
            f"wi={project_row['work_item_count']}{flag}" + (f" :: {breakdown}" if breakdown else "")
        )
    if with_orphans and "orphan_work_items" in result:
        click.echo(f"Orphan work items: {len(result['orphan_work_items'])}")
    if "scanner_caveat" in result:
        click.echo(f"\n[scanner_caveat] {result['scanner_caveat']}")


@backlog.command("update")
@click.argument("work_item_id")
@click.option("--resolution-status", default=None, help="New resolution status.")
@click.option("--stage", default=None, help="New stage.")
@click.option("--priority", default=None, type=click.Choice(["P0", "P1", "P2", "P3"]), help="New priority.")
@click.option("--related-bridge-threads", default=None, help="JSON array of related bridge file paths.")
@click.option("--status-detail", default=None, help="New status detail.")
@click.option(
    "--title",
    default=None,
    help="New title. Subject to the disjunctive text-edit gate (WI-4357).",
)
@click.option(
    "--description",
    default=None,
    help="New description. Subject to the disjunctive text-edit gate (WI-4357).",
)
@click.option("--source-spec-id", default=None, help="New source specification id (set, backfill, or correct).")
@click.option("--owner-approved", is_flag=True, help="Flag proving owner approval.")
@click.option("--change-reason", required=True, help="History reason for the update.")
@click.option("--dry-run", is_flag=True, help="Validate and report would-be changes without writing.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def backlog_update(
    ctx: click.Context,
    work_item_id: str,
    resolution_status: str | None,
    stage: str | None,
    priority: str | None,
    related_bridge_threads: str | None,
    status_detail: str | None,
    title: str | None,
    description: str | None,
    source_spec_id: str | None,
    owner_approved: bool,
    change_reason: str,
    dry_run: bool,
    json_output: bool,
) -> None:
    """Update field values of a single backlog work item."""
    config = _resolve_config(ctx)
    request = BacklogUpdateRequest(
        work_item_id=work_item_id,
        resolution_status=resolution_status,
        stage=stage,
        priority=priority,
        related_bridge_threads=related_bridge_threads,
        status_detail=status_detail,
        owner_approved=owner_approved,
        change_reason=change_reason,
        dry_run=dry_run,
        title=title,
        description=description,
        source_spec_id=source_spec_id,
    )
    try:
        result = update_backlog_item(config, request)
    except (BacklogUpdateError, RuntimeError) as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True, default=str))
        return

    action = "Would update" if result["dry_run"] else "Updated"
    click.echo(f"{action} work item {result['work_item_id']}.")


@backlog.command("resolve")
@click.argument("work_item_id")
@click.option("--priority", default=None, type=click.Choice(["P0", "P1", "P2", "P3"]), help="New priority.")
@click.option("--related-bridge-threads", default=None, help="JSON array of related bridge file paths.")
@click.option("--status-detail", default=None, help="New status detail.")
@click.option("--owner-approved", is_flag=True, help="Flag proving owner approval.")
@click.option("--change-reason", required=True, help="History reason for the update.")
@click.option("--dry-run", is_flag=True, help="Validate and report would-be changes without writing.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def backlog_resolve(
    ctx: click.Context,
    work_item_id: str,
    priority: str | None,
    related_bridge_threads: str | None,
    status_detail: str | None,
    owner_approved: bool,
    change_reason: str,
    dry_run: bool,
    json_output: bool,
) -> None:
    """Resolve a work item (shortcut for update --resolution-status resolved --stage resolved)."""
    config = _resolve_config(ctx)
    request = BacklogUpdateRequest(
        work_item_id=work_item_id,
        resolution_status="resolved",
        stage="resolved",
        priority=priority,
        related_bridge_threads=related_bridge_threads,
        status_detail=status_detail,
        owner_approved=owner_approved,
        change_reason=change_reason,
        dry_run=dry_run,
    )
    try:
        result = update_backlog_item(config, request)
    except (BacklogUpdateError, RuntimeError) as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True, default=str))
        return

    action = "Would resolve" if result["dry_run"] else "Resolved"
    click.echo(f"{action} work item {result['work_item_id']}.")


# ---------------------------------------------------------------------------
# gt registry
# ---------------------------------------------------------------------------


@main.group(name="registry")
def registry_cmd() -> None:
    """SoT artifact registry commands (GOV-PLATFORM-SOT-REGISTRY-001)."""


def _registry_paths(ctx: click.Context) -> tuple[Path, Path]:
    config = _resolve_config(ctx)
    return default_registry_path(config.project_root), config.db_path


def _record_to_dict(rec: Any) -> dict[str, Any]:
    return {
        "id": rec.id,
        "domain": rec.domain,
        "lifecycle": rec.lifecycle,
        "storage_path": rec.storage_path,
        "authority_spec_id": rec.authority_spec_id,
        "mutation_api": rec.mutation_api,
        "versioning_policy": rec.versioning_policy,
        "backup_policy": rec.backup_policy,
        "health_check_function": rec.health_check_function,
        "owner_role": rec.owner_role,
        "depends_on": list(rec.depends_on),
        "forbidden_substitutes": list(rec.forbidden_substitutes),
        "notes": rec.notes,
    }


@registry_cmd.command("list")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--domain", default=None, help="Filter by domain value.")
@click.option("--lifecycle", default=None, help="Filter by lifecycle value.")
@click.pass_context
def registry_list(ctx: click.Context, json_output: bool, domain: str | None, lifecycle: str | None) -> None:
    """List all SoT artifact records from the TOML registry."""
    toml_path, _db = _registry_paths(ctx)
    try:
        records = load_sot_toml(toml_path)
    except (InvalidSoTRecord, UnknownDomain, FileNotFoundError) as exc:
        raise click.ClickException(str(exc)) from exc
    if domain:
        records = [r for r in records if r.domain == domain]
    if lifecycle:
        records = [r for r in records if r.lifecycle == lifecycle]
    if json_output:
        click.echo(json.dumps([_record_to_dict(r) for r in records], indent=2))
        return
    for rec in records:
        click.echo(f"{rec.id}  [{rec.domain}]  {rec.lifecycle}  {rec.storage_path}")


@registry_cmd.command("show")
@click.argument("entry_id")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def registry_show(ctx: click.Context, entry_id: str, json_output: bool) -> None:
    """Show details of a single SoT artifact record by id."""
    toml_path, _db = _registry_paths(ctx)
    try:
        records = load_sot_toml(toml_path)
    except (InvalidSoTRecord, UnknownDomain, FileNotFoundError) as exc:
        raise click.ClickException(str(exc)) from exc
    for rec in records:
        if rec.id == entry_id:
            if json_output:
                click.echo(json.dumps(_record_to_dict(rec), indent=2))
            else:
                for key, val in _record_to_dict(rec).items():
                    click.echo(f"{key}: {val}")
            return
    raise click.ClickException(f"No registry entry with id={entry_id!r}")


@registry_cmd.command("validate")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def registry_validate(ctx: click.Context, json_output: bool) -> None:
    """Check parity between TOML registry and MemBase projection."""
    toml_path, db_path = _registry_paths(ctx)
    try:
        toml_records = load_sot_toml(toml_path)
    except (InvalidSoTRecord, UnknownDomain, FileNotFoundError) as exc:
        raise click.ClickException(str(exc)) from exc
    proj_records = load_projection(db_path)
    report = validate_projection_parity(toml_records, proj_records)
    result: dict[str, Any] = {
        "in_sync": report.in_sync,
        "toml_count": report.toml_count,
        "projection_count": report.projection_count,
        "missing_in_projection": list(report.missing_in_projection),
        "missing_in_toml": list(report.missing_in_toml),
        "field_divergences": [[pair[0], pair[1]] for pair in report.field_divergences],
    }
    if json_output:
        click.echo(json.dumps(result, indent=2))
        return
    status = "IN SYNC" if report.in_sync else "OUT OF SYNC"
    click.echo(f"Registry parity: {status}")
    click.echo(f"  TOML records:       {report.toml_count}")
    click.echo(f"  Projection records: {report.projection_count}")
    if report.missing_in_projection:
        click.echo(f"  Missing in projection: {', '.join(report.missing_in_projection)}")
    if report.missing_in_toml:
        click.echo(f"  Missing in TOML:       {', '.join(report.missing_in_toml)}")
    if report.field_divergences:
        click.echo(f"  Field divergences ({len(report.field_divergences)}):")
        for rec_id, field in report.field_divergences:
            click.echo(f"    {rec_id}.{field}")
    if not report.in_sync:
        raise SystemExit(1)


@registry_cmd.command("sync")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--changed-by", default="gt-registry-sync", show_default=True)
@click.option("--change-reason", default="gt registry sync", show_default=True)
@click.pass_context
def registry_sync(ctx: click.Context, json_output: bool, changed_by: str, change_reason: str) -> None:
    """Sync MemBase sot_artifacts projection from the TOML registry."""
    toml_path, db_path = _registry_paths(ctx)
    try:
        toml_records = load_sot_toml(toml_path)
    except (InvalidSoTRecord, UnknownDomain, FileNotFoundError) as exc:
        raise click.ClickException(str(exc)) from exc
    report = sync_projection(toml_records, db_path, changed_by=changed_by, change_reason=change_reason)
    result: dict[str, Any] = {
        "inserted": list(report.inserted),
        "updated": list(report.updated),
        "unchanged": list(report.unchanged),
    }
    if json_output:
        click.echo(json.dumps(result, indent=2))
        return
    click.echo(
        f"Registry sync: {len(report.inserted)} inserted, "
        f"{len(report.updated)} updated, {len(report.unchanged)} unchanged."
    )


@registry_cmd.command("diff")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def registry_diff(ctx: click.Context, json_output: bool) -> None:
    """Show diff between TOML and MemBase projection (non-mutating validate)."""
    ctx.invoke(registry_validate, json_output=json_output)


# ---------------------------------------------------------------------------
# gt projects
# ---------------------------------------------------------------------------


@main.group(name="projects")
def projects_cmd() -> None:
    """Project artifact commands backed by MemBase projects over work_items."""


def _project_service(ctx: click.Context) -> tuple[KnowledgeDB, ProjectLifecycleService]:
    config = _resolve_config(ctx)
    db = _open_db(config)
    return db, ProjectLifecycleService(db)


@projects_cmd.command("list")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--all", "include_terminal", is_flag=True, help="Include completed/retired/cancelled projects.")
@click.option("--id", "project_ids", multiple=True, help="Limit to an explicit project id; repeatable.")
@click.option("--status", default=None, help="Limit to a project status.")
@click.option("--contains", "contains_terms", multiple=True, help="Case-insensitive text filter; repeatable.")
@click.option("--limit", type=click.IntRange(min=1), default=None, help="Return at most N rows.")
@click.pass_context
def projects_list(
    ctx: click.Context,
    json_output: bool,
    include_terminal: bool,
    project_ids: tuple[str, ...],
    status: str | None,
    contains_terms: tuple[str, ...],
    limit: int | None,
) -> None:
    """List first-class project records."""
    db, service = _project_service(ctx)
    try:
        include_terminal = include_terminal or bool(project_ids) or status is not None
        projects = service.list_projects(include_terminal=include_terminal, status=status)
    finally:
        db.close()
    projects = [
        project
        for project in projects
        if _matches_any_exact(project, "id", project_ids)
        and _matches_contains(project, _PROJECT_CONTAINS_FIELDS, contains_terms)
    ]
    projects = _apply_limit(projects, limit)

    if json_output:
        click.echo(json.dumps(projects, indent=2, sort_keys=True))
        return
    if not projects:
        click.echo("No projects found.")
        return
    for project in projects:
        rank = project.get("rank")
        rank_prefix = "-" if rank is None else str(rank)
        click.echo(f"{rank_prefix}\t{project['id']}\t{project['status']}\t{project['name']}")


@projects_cmd.command("show")
@click.argument("project_id")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_show(ctx: click.Context, project_id: str, json_output: bool) -> None:
    """Show a project with its work items, dependencies, and artifact links."""
    db, service = _project_service(ctx)
    try:
        payload = service.show_project(project_id)
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    project = payload["project"]
    work_items = payload["work_items"]
    dependencies = payload["dependencies"]
    artifact_links = payload["artifact_links"]
    authorizations = payload["authorizations"]
    if json_output:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
        return

    click.echo(f"{project['id']}: {project['name']} [{project['status']}]")
    if work_items:
        click.echo("Work items:")
        for item in work_items:
            status = item.get("status_detail") or item.get("resolution_status")
            click.echo(f"  - {item['work_item_id']}: {status} - {item['work_item_title']}")
    if dependencies:
        click.echo("Dependencies:")
        for dep in dependencies:
            click.echo(
                f"  - {dep['from_project_id']} {dep['dependency_type']} {dep['to_project_id']}"
                f" [{dep['blocking_status']}]"
            )
    if artifact_links:
        click.echo("Artifact links:")
        for link in artifact_links:
            click.echo(f"  - {link['artifact_type']}:{link['artifact_ref']} ({link['relationship']})")
    if authorizations:
        click.echo("Authorizations:")
        for authorization in authorizations:
            click.echo(f"  - {authorization['id']}: {authorization['status']} - {authorization['authorization_name']}")


@projects_cmd.command("create")
@click.argument("name")
@click.option("--id", "project_id", default=None, help="Explicit project id. Defaults to stable id from name.")
@click.option("--rank", type=int, default=None, help="Project ordering rank.")
@click.option("--parent-project-id", default=None, help="Parent project id for sub-project grouping.")
@click.option("--purpose", default=None, help="Project purpose.")
@click.option("--target-outcome", default=None, help="Expected project outcome.")
@click.option("--scope-note", default=None, help="Scope boundary note.")
@click.option("--start-date", default=None, help="Project start date.")
@click.option("--target-date", default=None, help="Project target date.")
@click.option("--notes", default=None, help="Project notes.")
@click.option("--source-project-name", default=None, help="Compatibility source project name.")
@click.option("--source-subproject-name", default=None, help="Compatibility source sub-project name.")
@click.option("--changed-by", default=PROJECTS_CHANGED_BY, show_default=True, help="History author.")
@click.option("--change-reason", required=True, help="History reason for the new project version.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_create(
    ctx: click.Context,
    name: str,
    project_id: str | None,
    rank: int | None,
    parent_project_id: str | None,
    purpose: str | None,
    target_outcome: str | None,
    scope_note: str | None,
    start_date: str | None,
    target_date: str | None,
    notes: str | None,
    source_project_name: str | None,
    source_subproject_name: str | None,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Create a first-class project record."""
    db, service = _project_service(ctx)
    try:
        project = service.create_project(
            name,
            project_id=project_id,
            rank=rank,
            parent_project_id=parent_project_id,
            purpose=purpose,
            target_outcome=target_outcome,
            scope_note=scope_note,
            start_date=start_date,
            target_date=target_date,
            notes=notes,
            source_project_name=source_project_name,
            source_subproject_name=source_subproject_name,
            changed_by=changed_by,
            change_reason=change_reason,
        )
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(project, indent=2, sort_keys=True))
        return
    click.echo(f"Created project {project['id']}: {project['name']}")


@projects_cmd.command("update")
@click.argument("project_id")
@click.option("--name", default=None, help="New project name.")
@click.option("--status", default=None, help="New project status.")
@click.option("--rank", type=int, default=None, help="New project ordering rank.")
@click.option("--parent-project-id", default=None, help="New parent project id.")
@click.option("--purpose", default=None, help="New project purpose.")
@click.option("--target-outcome", default=None, help="New expected project outcome.")
@click.option("--scope-note", default=None, help="New scope boundary note.")
@click.option("--start-date", default=None, help="New project start date.")
@click.option("--target-date", default=None, help="New project target date.")
@click.option("--completed-at", default=None, help="Completion timestamp/date.")
@click.option("--notes", default=None, help="New project notes.")
@click.option("--source-project-name", default=None, help="Compatibility source project name.")
@click.option("--source-subproject-name", default=None, help="Compatibility source sub-project name.")
@click.option("--changed-by", default=PROJECTS_CHANGED_BY, show_default=True, help="History author.")
@click.option("--change-reason", required=True, help="History reason for the new project version.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_update(
    ctx: click.Context,
    project_id: str,
    name: str | None,
    status: str | None,
    rank: int | None,
    parent_project_id: str | None,
    purpose: str | None,
    target_outcome: str | None,
    scope_note: str | None,
    start_date: str | None,
    target_date: str | None,
    completed_at: str | None,
    notes: str | None,
    source_project_name: str | None,
    source_subproject_name: str | None,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Update a project by appending a new project version."""
    updates = {
        key: value
        for key, value in {
            "name": name,
            "status": status,
            "rank": rank,
            "parent_project_id": parent_project_id,
            "purpose": purpose,
            "target_outcome": target_outcome,
            "scope_note": scope_note,
            "start_date": start_date,
            "target_date": target_date,
            "completed_at": completed_at,
            "notes": notes,
            "source_project_name": source_project_name,
            "source_subproject_name": source_subproject_name,
        }.items()
        if value is not None
    }
    if not updates:
        raise click.ClickException("At least one update option is required.")

    db, service = _project_service(ctx)
    try:
        project = service.update_project(
            project_id,
            changed_by=changed_by,
            change_reason=change_reason,
            **updates,
        )
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(project, indent=2, sort_keys=True))
        return
    click.echo(f"Updated project {project['id']}: {project['name']} [{project['status']}]")


@projects_cmd.command("add-item")
@click.argument("project_id")
@click.argument("work_item_id")
@click.option("--role", "membership_role", default="member", show_default=True, help="Membership role.")
@click.option("--order", "membership_order", type=int, default=None, help="Membership order.")
@click.option("--source", default="gt projects add-item", show_default=True, help="Membership source.")
@click.option("--changed-by", default=PROJECTS_CHANGED_BY, show_default=True, help="History author.")
@click.option("--change-reason", required=True, help="History reason for the new membership version.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_add_item(
    ctx: click.Context,
    project_id: str,
    work_item_id: str,
    membership_role: str,
    membership_order: int | None,
    source: str | None,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Add one work item to a project."""
    db, service = _project_service(ctx)
    try:
        membership = service.add_project_item(
            project_id,
            work_item_id,
            membership_role=membership_role,
            membership_order=membership_order,
            source=source,
            changed_by=changed_by,
            change_reason=change_reason,
        )
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(membership, indent=2, sort_keys=True))
        return
    click.echo(f"Linked {membership['work_item_id']} to {membership['project_id']} as {membership['membership_role']}")


@projects_cmd.command("remove-item")
@click.argument("project_id")
@click.argument("work_item_id")
@click.option("--status", default="removed", show_default=True, help="Non-active membership status to set.")
@click.option("--changed-by", default=PROJECTS_CHANGED_BY, show_default=True, help="History author.")
@click.option("--change-reason", required=True, help="History reason for the removal version.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_remove_item(
    ctx: click.Context,
    project_id: str,
    work_item_id: str,
    status: str,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Detach one work item from a project (append-only, non-active membership)."""
    db, service = _project_service(ctx)
    try:
        membership = service.remove_project_item(
            project_id,
            work_item_id,
            status=status,
            changed_by=changed_by,
            change_reason=change_reason,
        )
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(membership, indent=2, sort_keys=True))
        return
    click.echo(
        f"Removed {membership['work_item_id']} from {membership['project_id']} (status={membership.get('status')})"
    )


@projects_cmd.command("reorder")
@click.argument("project_id")
@click.argument("work_item_ids", nargs=-1)
@click.option("--start-at", type=int, default=1, show_default=True, help="First membership_order value.")
@click.option("--changed-by", default=PROJECTS_CHANGED_BY, show_default=True, help="History author.")
@click.option("--change-reason", required=True, help="History reason for the new membership versions.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_reorder(
    ctx: click.Context,
    project_id: str,
    work_item_ids: tuple[str, ...],
    start_at: int,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Reorder all active work-item memberships in one project."""
    if not work_item_ids:
        raise click.ClickException("At least one work item id is required.")
    db, service = _project_service(ctx)
    try:
        memberships = service.reorder_project_items(
            project_id,
            list(work_item_ids),
            start_at=start_at,
            changed_by=changed_by,
            change_reason=change_reason,
        )
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(memberships, indent=2, sort_keys=True))
        return
    click.echo(f"Reordered {len(memberships)} work item(s) in {project_id}.")


@projects_cmd.command("retire")
@click.argument("project_id")
@click.option("--completed-at", default=None, help="Completion timestamp/date. Defaults to current UTC time.")
@click.option("--changed-by", default=PROJECTS_CHANGED_BY, show_default=True, help="History author.")
@click.option("--change-reason", required=True, help="History reason for the retired project version.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_retire(
    ctx: click.Context,
    project_id: str,
    completed_at: str | None,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Retire a project by appending a terminal project version."""
    db, service = _project_service(ctx)
    try:
        project = service.retire_project(
            project_id,
            completed_at=completed_at,
            changed_by=changed_by,
            change_reason=change_reason,
        )
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(project, indent=2, sort_keys=True))
        return
    click.echo(f"Retired project {project['id']}: {project['name']}")


@projects_cmd.command("reconcile-doubled-prefix")
@click.option(
    "--apply",
    "apply_flag",
    is_flag=True,
    default=False,
    help="Execute the reconciliation. Without this flag the command is dry-run only.",
)
@click.option(
    "--project",
    "project_id",
    default=None,
    help="Limit reconciliation to phantoms whose canonical id is this project or one of its child ids.",
)
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_reconcile_doubled_prefix(
    ctx: click.Context,
    apply_flag: bool,
    project_id: str | None,
    json_output: bool,
) -> None:
    """Reconcile doubled-leading-segment phantom projects.

    The original phantoms are historical ``PROJECT-PROJECT-*`` artifacts of
    the pre-fix ``_project_id_from_names`` doubling defect (fixed in commit
    ``281fa28f``). The same service now also handles project-specific doubled
    leading segments such as ``PROJECT-X-PROJECT-X-*``. It re-links each
    affected work item to its canonical project (if needed), supersedes each
    phantom membership row, and retires each phantom project. Idempotent on
    rerun.

    Default mode (no ``--apply``) is dry-run: builds the per-phantom plan
    and prints/emits it without mutating MemBase.
    """
    # Lazy import keeps the reconciliation module out of the click command
    # registration import path; matches the pattern in ``cli_backlog_status``.
    from groundtruth_kb.cli_projects_reconcile import (  # noqa: PLC0415
        ReconcileRequest,
        build_reconcile_plan,
    )

    # Resolve the GTConfig the same way every other projects_cmd does;
    # ctx.obj["config"] holds the raw Path, not a config object.
    config = _resolve_config(ctx)
    request = ReconcileRequest(apply=apply_flag, project_id=project_id)
    report = build_reconcile_plan(config, request)

    if json_output:
        click.echo(json.dumps(report, indent=2, sort_keys=True))
        return

    totals = report["totals"]
    mode = "APPLY" if report["apply"] else "DRY-RUN"
    click.echo(f"Phantom reconciliation [{mode}]")
    if report.get("project_id"):
        click.echo(f"  project scope: {report['project_id']}")
    click.echo(f"  phantoms found: {totals['phantom_count']} (skipped: {totals['skipped_count']})")
    if report["apply"]:
        click.echo(f"  canonical links created: {totals['canonical_links_created']}")
        click.echo(f"  phantom memberships superseded: {totals['phantom_memberships_superseded']}")
        click.echo(f"  phantom projects retired: {totals['phantom_projects_retired']}")
    else:
        planned_links = sum(len(e["plan"]["canonical_links_to_create"]) for e in report["phantoms"])
        planned_supers = sum(len(e["plan"]["phantom_memberships_to_supersede"]) for e in report["phantoms"])
        planned_retires = sum(1 for e in report["phantoms"] if e["plan"]["retire_phantom"])
        click.echo(f"  planned canonical links: {planned_links}")
        click.echo(f"  planned phantom-membership supersessions: {planned_supers}")
        click.echo(f"  planned phantom retirements: {planned_retires}")
        click.echo("  (re-run with --apply to execute)")


@projects_cmd.command("link-bridge")
@click.argument("project_id")
@click.argument("bridge_id")
@click.option("--relationship", default="related", show_default=True, help="Artifact relationship.")
@click.option("--notes", default=None, help="Optional link note.")
@click.option("--changed-by", default=PROJECTS_CHANGED_BY, show_default=True, help="History author.")
@click.option("--change-reason", required=True, help="History reason for the new artifact-link version.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_link_bridge(
    ctx: click.Context,
    project_id: str,
    bridge_id: str,
    relationship: str,
    notes: str | None,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Link a project to a bridge thread artifact without editing bridge files."""
    db, service = _project_service(ctx)
    try:
        link = service.link_bridge_thread(
            project_id,
            bridge_id,
            relationship=relationship,
            notes=notes,
            changed_by=changed_by,
            change_reason=change_reason,
        )
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(link, indent=2, sort_keys=True))
        return
    click.echo(f"Linked bridge thread {link['artifact_ref']} to {link['project_id']}.")


@projects_cmd.command("authorize")
@click.argument("project_id")
@click.option("--id", "authorization_id", default=None, help="Explicit authorization id.")
@click.option("--owner-decision", required=True, help="Owner-decision deliberation id.")
@click.option("--name", required=True, help="Authorization name.")
@click.option("--scope", "scope_summary", required=True, help="Bounded authorization scope summary.")
@click.option("--allowed-mutation", "allowed_mutation_classes", multiple=True, help="Allowed mutation class.")
@click.option("--forbid", "forbidden_operations", multiple=True, help="Forbidden operation.")
@click.option("--include-work-item", "included_work_item_ids", multiple=True, help="Explicitly included work item.")
@click.option("--exclude-work-item", "excluded_work_item_ids", multiple=True, help="Explicitly excluded work item.")
@click.option("--include-spec", "included_spec_ids", multiple=True, help="Explicitly included spec.")
@click.option("--exclude-spec", "excluded_spec_ids", multiple=True, help="Explicitly excluded spec.")
@click.option("--expires-at", default=None, help="Optional ISO-8601 expiration timestamp.")
@click.option("--changed-by", default=PROJECTS_CHANGED_BY, show_default=True, help="History author.")
@click.option("--change-reason", required=True, help="History reason for the authorization version.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_authorize(
    ctx: click.Context,
    project_id: str,
    authorization_id: str | None,
    owner_decision: str,
    name: str,
    scope_summary: str,
    allowed_mutation_classes: tuple[str, ...],
    forbidden_operations: tuple[str, ...],
    included_work_item_ids: tuple[str, ...],
    excluded_work_item_ids: tuple[str, ...],
    included_spec_ids: tuple[str, ...],
    excluded_spec_ids: tuple[str, ...],
    expires_at: str | None,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Authorize a bounded project for implementation work."""
    db, service = _project_service(ctx)
    try:
        authorization = service.authorize_project(
            project_id,
            authorization_id=authorization_id,
            owner_decision=owner_decision,
            name=name,
            scope=scope_summary,
            allowed_mutation_classes=list(allowed_mutation_classes) or None,
            forbidden_operations=list(forbidden_operations) or None,
            included_work_item_ids=list(included_work_item_ids) or None,
            excluded_work_item_ids=list(excluded_work_item_ids) or None,
            included_spec_ids=list(included_spec_ids) or None,
            excluded_spec_ids=list(excluded_spec_ids) or None,
            expires_at=expires_at,
            changed_by=changed_by,
            change_reason=change_reason,
        )
    except ProjectAuthorizationSpecLinkageError as exc:
        # WI-3312: spec-linkage rejection is an owner-correctable usage error.
        raise click.UsageError(str(exc)) from exc
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(authorization, indent=2, sort_keys=True))
        return
    click.echo(f"Authorized project {authorization['project_id']} with {authorization['id']}.")


@projects_cmd.command("authorizations")
@click.argument("project_id")
@click.option("--all", "include_terminal", is_flag=True, help="Include revoked/terminal authorizations.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_authorizations(ctx: click.Context, project_id: str, include_terminal: bool, json_output: bool) -> None:
    """List project-scoped implementation authorizations."""
    db, service = _project_service(ctx)
    try:
        authorizations = service.list_project_authorizations(project_id, include_terminal=include_terminal)
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(authorizations, indent=2, sort_keys=True))
        return
    if not authorizations:
        click.echo("No project authorizations found.")
        return
    for authorization in authorizations:
        click.echo(
            f"{authorization['id']}\t{authorization['project_id']}\t"
            f"{authorization['status']}\t{authorization['authorization_name']}"
        )


@projects_cmd.command("show-authorization")
@click.argument("authorization_id")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_show_authorization(ctx: click.Context, authorization_id: str, json_output: bool) -> None:
    """Show one current project authorization by ID."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        authorization = db.get_project_authorization(authorization_id)
    finally:
        db.close()
    if authorization is None:
        click.echo(f"Project authorization {authorization_id} not found.")
        raise SystemExit(1)
    if json_output:
        click.echo(json.dumps(authorization, indent=2, sort_keys=True))
        return
    click.echo(
        f"{authorization['id']}\t{authorization['project_id']}\t"
        f"{authorization['status']}\t{authorization['authorization_name']}"
    )
    click.echo(f"  scope: {authorization.get('scope_summary') or ''}")
    click.echo(f"  owner decision: {authorization.get('owner_decision_deliberation_id') or ''}")


@projects_cmd.command("revoke-authorization")
@click.argument("authorization_id")
@click.option("--changed-by", default=PROJECTS_CHANGED_BY, show_default=True, help="History author.")
@click.option("--change-reason", required=True, help="History reason for revocation.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_revoke_authorization(
    ctx: click.Context,
    authorization_id: str,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Revoke a project-scoped implementation authorization."""
    db, service = _project_service(ctx)
    try:
        authorization = service.revoke_project_authorization(
            authorization_id,
            changed_by=changed_by,
            change_reason=change_reason,
        )
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(authorization, indent=2, sort_keys=True))
        return
    click.echo(f"Revoked project authorization {authorization['id']}.")


@projects_cmd.command("complete-authorization")
@click.argument("authorization_id")
@click.option("--changed-by", default=PROJECTS_CHANGED_BY, show_default=True, help="History author.")
@click.option("--change-reason", required=True, help="History reason for completion.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def projects_complete_authorization(
    ctx: click.Context,
    authorization_id: str,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Complete a project-scoped implementation authorization.

    ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v2: project completion
    and retirement are automatic once every membership-linked work item is
    VERIFIED. This subcommand is the explicit-invocation surface; it does not
    gate on an owner decision. The owner-directed ``retire`` subcommand is the
    separate path for retirements outside the automatic VERIFIED gate.
    """
    config = _resolve_config(ctx)
    db, service = _project_service(ctx)
    try:
        result = service.complete_project_authorization(
            authorization_id,
            project_root=config.project_root,
            changed_by=changed_by,
            change_reason=change_reason,
        )
    except ProjectLifecycleError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True))
        return
    authorization = result["authorization"]
    retired = " Project retired." if result["project_retired"] else ""
    click.echo(f"Completed project authorization {authorization['id']}.{retired}")


# ---------------------------------------------------------------------------
# gt secrets
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# gt canonical-terms (Phase 1 backing-registry CLI)
# ---------------------------------------------------------------------------


@main.group(name="canonical-terms")
def canonical_terms_cmd() -> None:
    """Canonical Terminology System backing-registry commands.

    Phase 1: ``.claude/rules/canonical-terminology.md`` and the matching
    ``.toml`` profile remain the startup-readable authority. These commands
    populate and inspect the structured backing registry in MemBase used
    by tools (collision detection, parity checks, future retrieval surfaces).
    """


@canonical_terms_cmd.command("seed")
@click.option("--dry-run", "dry_run", is_flag=True, help="Plan without applying. Default behavior.")
@click.option("--apply", "apply_flag", is_flag=True, help="Apply the planned operations.")
@click.option(
    "--markdown",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Glossary markdown path. Defaults to <project_root>/.claude/rules/canonical-terminology.md.",
)
@click.option(
    "--changed-by",
    default=None,
    help="History author for inserts/updates. Defaults to canonical-terms-seed.",
)
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def canonical_terms_seed(
    ctx: click.Context,
    dry_run: bool,
    apply_flag: bool,
    markdown: Path | None,
    changed_by: str | None,
    json_output: bool,
) -> None:
    """Seed (or plan to seed) canonical_terms from the markdown glossary.

    Idempotent: running ``--apply`` against an unchanged markdown produces
    all-unchanged operations. Append-only: revisions append a new version;
    removals append a ``lifecycle_status='retired'`` row. Never DELETE.
    """
    from groundtruth_kb import canonical_terms as _ct

    if dry_run and apply_flag:
        raise click.ClickException("Specify either --dry-run or --apply, not both.")
    actually_apply = bool(apply_flag) and not dry_run

    config = _resolve_config(ctx)
    md_path = markdown or config.project_root / ".claude" / "rules" / "canonical-terminology.md"
    if not md_path.exists():
        raise click.ClickException(f"Glossary markdown not found: {md_path}")

    db = _open_db(config)
    try:
        plan = _ct.seed_from_markdown(
            db,
            md_path,
            dry_run=not actually_apply,
            changed_by=changed_by or "canonical-terms-seed",
        )
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(plan.to_dict(), indent=2, sort_keys=True))
        return

    mode = "APPLIED" if actually_apply else "DRY-RUN"
    click.echo(f"canonical-terms seed [{mode}]")
    click.echo(f"  source: {plan.source_path}")
    click.echo(f"  hash:   {plan.source_hash}")
    summary = plan.summary()
    parts = ", ".join(f"{op}={n}" for op, n in sorted(summary.items()))
    click.echo(f"  summary: {parts or '(no operations)'}")
    for op in plan.operations:
        click.echo(f"    {op.op:<10} {op.id:<40} {op.canonical_term}")


@canonical_terms_cmd.command("list")
@click.option(
    "--authority-level",
    type=click.Choice(["platform_core", "adopter_extension", "project_local"]),
    default=None,
)
@click.option("--scope", default=None, help="Filter by scope (e.g., platform, adopter:agent_red).")
@click.option("--include-retired", is_flag=True, help="Include retired terms in the output.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def canonical_terms_list(
    ctx: click.Context,
    authority_level: str | None,
    scope: str | None,
    include_retired: bool,
    json_output: bool,
) -> None:
    """List canonical_terms current state (latest version per id)."""
    from groundtruth_kb import canonical_terms as _ct

    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        rows = _ct.list_terms(
            db,
            authority_level=authority_level,
            scope=scope,
            include_retired=include_retired,
        )
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(rows, indent=2, sort_keys=True, default=str))
        return

    click.echo(f"canonical-terms list ({len(rows)} terms)")
    for r in rows:
        click.echo(
            f"  [{r.get('authority_level')}/{r.get('scope')}] "
            f"{r.get('id')} ({r.get('lifecycle_status')}): {r.get('canonical_term')}"
        )


@canonical_terms_cmd.command("history")
@click.argument("term_id")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def canonical_terms_history(ctx: click.Context, term_id: str, json_output: bool) -> None:
    """Show all versions of a canonical term, oldest first."""
    from groundtruth_kb import canonical_terms as _ct

    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        versions = _ct.list_versions(db, term_id)
    finally:
        db.close()

    if not versions:
        raise click.ClickException(f"No versions found for term id: {term_id}")

    if json_output:
        click.echo(json.dumps(versions, indent=2, sort_keys=True, default=str))
        return

    click.echo(f"canonical-terms history: {term_id}")
    for v in versions:
        click.echo(
            f"  v{v.get('version')} [{v.get('lifecycle_status')}] "
            f"{v.get('changed_at')} by {v.get('changed_by')}: {v.get('change_reason')}"
        )


# ---------------------------------------------------------------------------
# gt secrets
# ---------------------------------------------------------------------------


_SECRET_SCAN_FINDINGS_EXIT = 5


@main.group()
def secrets() -> None:
    """Secret scanning and redacted credential-inventory commands."""


def _parse_secret_fail_on(raw: str) -> tuple[Any, ...]:
    from groundtruth_kb.secrets import Severity

    if not raw.strip():
        return ()
    parsed = []
    valid = {item.value: item for item in Severity}
    for item in raw.split(","):
        key = item.strip()
        if not key:
            continue
        if key not in valid:
            allowed = ", ".join(sorted(valid))
            raise click.UsageError(f"Unknown severity {key!r}; expected one of: {allowed}")
        parsed.append(valid[key])
    return tuple(parsed)


def _format_secret_scan_markdown(result: Any) -> str:
    lines = [f"Secret scan ({result.mode}): {len(result.findings)} finding(s), {result.paths_scanned} path(s) scanned."]
    for finding in result.findings:
        lines.append(
            f"- {finding.path}:{finding.line} `{finding.provider_class}` "
            f"{finding.severity.value} {finding.fingerprint_prefix} - {finding.description}"
        )
    return "\n".join(lines)


def _default_secret_allowlist(repo_root: Path) -> Any:
    from groundtruth_kb.secrets import Allowlist

    return Allowlist.load(repo_root / "tests" / "secrets" / "fixtures" / "allowlist.toml")


@secrets.command("scan")
@click.option("--staged", is_flag=True, help="Scan staged git blobs for the pre-commit gate.")
@click.option("--range", "range_spec", default=None, help="Scan changed blobs in <base>..<head> form.")
@click.option("--paths", "paths_mode", is_flag=True, help="Scan the path arguments that follow this flag.")
@click.option("--tracked", is_flag=True, help="Scan current tracked working-tree files for Slice 1 inventory.")
@click.option(
    "--all-refs",
    is_flag=True,
    help="Scan blobs reachable from locally known refs; does not fetch or rewrite.",
)
@click.option("--redacted", is_flag=True, help="Emit redacted findings; raw secret output is not supported.")
@click.option("--json", "json_output", is_flag=True, help="Write redacted structured output to stdout.")
@click.option("--report-json", "report_json", type=click.Path(), default=None, help="Write redacted JSON report.")
@click.option(
    "--fail-on",
    default="verified-provider",
    show_default=True,
    help="Comma-separated severities that produce exit code 5; pass an empty value for report-only scans.",
)
@click.argument("path_args", nargs=-1, type=click.Path())
def secrets_scan(
    staged: bool,
    range_spec: str | None,
    paths_mode: bool,
    tracked: bool,
    all_refs: bool,
    redacted: bool,
    json_output: bool,
    report_json: str | None,
    fail_on: str,
    path_args: tuple[str, ...],
) -> None:
    """Run the shared scanner without exposing raw matched values."""
    from groundtruth_kb.secrets import (
        GitScanError,
        scan_all_refs,
        scan_paths,
        scan_range,
        scan_staged,
        scan_tracked,
        write_json_report,
    )

    del redacted  # Raw output is intentionally unsupported; all output is redacted.
    selected = sum(1 for value in (staged, range_spec is not None, paths_mode, tracked, all_refs) if value)
    if selected != 1:
        raise click.UsageError("Choose exactly one scan mode: --staged, --range, --paths, --tracked, or --all-refs.")
    if not paths_mode and path_args:
        raise click.UsageError("Path arguments are only valid after --paths.")
    if paths_mode and not path_args:
        raise click.UsageError("--paths requires at least one path argument.")
    repo_root = Path.cwd().resolve()
    try:
        allowlist = _default_secret_allowlist(repo_root)
        if staged:
            result = scan_staged(repo_root=repo_root, allowlist=allowlist)
        elif range_spec is not None:
            result = scan_range(range_spec, repo_root=repo_root, allowlist=allowlist)
        elif tracked:
            result = scan_tracked(repo_root=repo_root, allowlist=allowlist)
        elif all_refs:
            result = scan_all_refs(repo_root=repo_root, allowlist=allowlist)
        else:
            result = scan_paths((Path(path) for path in path_args), repo_root=repo_root, allowlist=allowlist)
    except GitScanError as exc:
        raise click.ClickException(str(exc)) from exc

    if report_json:
        write_json_report(result, Path(report_json))
    if json_output:
        click.echo(json.dumps(result.to_json_dict(), indent=2, sort_keys=True))
    else:
        click.echo(_format_secret_scan_markdown(result))

    if result.has_findings_at_or_above(_parse_secret_fail_on(fail_on)):
        raise SystemExit(_SECRET_SCAN_FINDINGS_EXIT)


# ---------------------------------------------------------------------------
# gt policy
# ---------------------------------------------------------------------------


@main.group()
def policy() -> None:
    """Deterministic policy-gate checks."""


@policy.command("check")
@click.option("--action", required=True, help="Policy action class to evaluate.")
@click.option("--scope", required=True, help="Active scope, such as platform or application.")
@click.option("--path", "--paths", "paths", multiple=True, help="Path touched by the action; repeat as needed.")
@click.option("--registry", type=click.Path(exists=True), default=None, help="Policy registry TOML path.")
@click.option("--receipt", type=click.Path(exists=True), default=None, help="Scoped approval receipt JSON path.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
def policy_check(
    action: str,
    scope: str,
    paths: tuple[str, ...],
    registry: str | None,
    receipt: str | None,
    json_output: bool,
) -> None:
    """Evaluate a policy decision without installing an adapter."""
    from groundtruth_kb.policy.engine import check_policy, load_policy_registry, load_receipt

    try:
        loaded_registry = load_policy_registry(Path(registry) if registry else None)
        decision = check_policy(
            action=action,
            scope=scope,
            paths=tuple(Path(path) for path in paths),
            registry=loaded_registry,
            receipt=load_receipt(Path(receipt) if receipt else None),
        )
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(decision.to_json_dict(), indent=2, sort_keys=True))
    else:
        click.echo(f"{decision.outcome}: {decision.message}")
        if decision.ask_options:
            for index, option in enumerate(decision.ask_options, start=1):
                click.echo(f"  {index}. {option}")
        for reason in decision.reasons:
            click.echo(f"  reason: {reason}")

    if decision.outcome == "ASK":
        raise SystemExit(2)
    if decision.outcome == "DENY":
        raise SystemExit(3)


# ---------------------------------------------------------------------------
# gt history
# ---------------------------------------------------------------------------


@main.command()
@click.option("--limit", default=20, help="Number of recent changes to show")
@click.pass_context
def history(ctx: click.Context, limit: int) -> None:
    """Print recent changes across all artifact types."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        changes = db.get_history(limit=limit)
        if not changes:
            click.echo("No changes recorded yet.")
            return
        click.echo(f"\nRecent changes (last {limit}):\n")
        for c in changes:
            click.echo(
                f"  [{c['changed_at'][:19]}] {c['table_name']}/{c['record_id']} "
                f"v{c['version']} — {c.get('title', '')[:60]}"
            )
            click.echo(f"    by {c['changed_by']}: {c['change_reason'][:80]}")
        click.echo()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# gt export
# ---------------------------------------------------------------------------


@main.command("export")
@click.option("--output", "output_file", type=click.Path(), default=None, help="Output JSON file path")
@click.pass_context
def export_cmd(ctx: click.Context, output_file: str | None) -> None:
    """Export the entire database to JSON."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        path = db.export_json(output_path=output_file)
        click.echo(f"Exported to: {path}")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# gt import
# ---------------------------------------------------------------------------

_IMPORTABLE_TABLES = frozenset(
    {
        "specifications",
        "test_procedures",
        "operational_procedures",
        "assertion_runs",
        "session_prompts",
        "environment_config",
        "documents",
        "test_coverage",
        "tests",
        "test_plans",
        "test_plan_phases",
        "work_items",
        "projects",
        "project_work_item_memberships",
        "project_dependencies",
        "project_artifact_links",
        "project_authorizations",
        "backlog_snapshots",
        "testable_elements",
        "quality_scores",
        "spec_quality_scores",
        "session_snapshots",
    }
)


@main.command("import")
@click.argument("file", type=click.Path(exists=True))
@click.option("--merge", is_flag=True, help="Merge into existing DB (skip duplicates)")
@click.pass_context
def import_cmd(ctx: click.Context, file: str, merge: bool) -> None:
    """Import database from a JSON export file."""
    import sqlite3

    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        data = json.loads(Path(file).read_text(encoding="utf-8"))
        tables = data.get("tables", {})
        counts: dict[str, int] = {}
        skipped_tables: list[str] = []

        conn = db._get_conn()

        # Build column allowlist from live schema
        schema_cols: dict[str, set[str]] = {}
        for table in _IMPORTABLE_TABLES:
            cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
            schema_cols[table] = cols - {"rowid"}

        for table_name, rows in tables.items():
            if table_name not in _IMPORTABLE_TABLES:
                skipped_tables.append(table_name)
                continue

            allowed = schema_cols[table_name]
            imported = 0
            rejected = 0
            for row in rows:
                row.pop("rowid", None)
                row = {k: v for k, v in row.items() if not k.endswith("_parsed")}

                # Reject rows with unknown columns
                unknown = set(row.keys()) - allowed
                if unknown:
                    rejected += 1
                    if not merge:
                        raise click.ClickException(
                            f"Unknown columns in table '{table_name}': {sorted(unknown)}. "
                            f"Valid columns: {sorted(allowed)}"
                        )
                    continue

                # Validate assertions in specifications rows
                if table_name == "specifications" and "assertions" in row and row["assertions"]:
                    from groundtruth_kb.assertion_schema import validate_assertion_list

                    try:
                        raw = row["assertions"]
                        parsed_assertions = json.loads(raw) if isinstance(raw, str) else raw
                        validation_errors = validate_assertion_list(parsed_assertions)
                        if validation_errors:
                            spec_id = row.get("id", "unknown")
                            if not merge:
                                raise click.ClickException(
                                    f"Invalid assertions in {spec_id}: {'; '.join(validation_errors)}"
                                )
                            click.echo(
                                f"  WARNING: {spec_id}: invalid assertions skipped ({len(validation_errors)} error(s))",
                                err=True,
                            )
                            rejected += 1
                            continue
                    except (json.JSONDecodeError, TypeError) as exc:
                        if not merge:
                            raise click.ClickException(
                                f"Malformed assertions JSON in {row.get('id', 'unknown')}"
                            ) from exc
                        rejected += 1
                        continue

                # F3: Validate flags JSON in spec_quality_scores rows
                if table_name == "spec_quality_scores" and "flags" in row and row["flags"] is not None:
                    try:
                        parsed_flags = json.loads(row["flags"]) if isinstance(row["flags"], str) else row["flags"]
                        if not isinstance(parsed_flags, list):
                            raise ValueError("flags must be a JSON list")
                    except (json.JSONDecodeError, ValueError, TypeError) as exc:
                        spec_ref = f"{row.get('spec_id', '?')}v{row.get('spec_version', '?')}"
                        if not merge:
                            raise click.ClickException(f"Invalid flags in quality score {spec_ref}: {exc}") from exc
                        click.echo(
                            f"  WARNING: {spec_ref}: invalid flags skipped ({exc})",
                            err=True,
                        )
                        rejected += 1
                        continue

                # F7: Validate data JSON in session_snapshots rows
                if table_name == "session_snapshots" and "data" in row and row["data"] is not None:
                    try:
                        parsed_data = json.loads(row["data"]) if isinstance(row["data"], str) else row["data"]
                        if not isinstance(parsed_data, dict):
                            raise ValueError("session snapshot data must be a JSON object")
                    except (json.JSONDecodeError, ValueError, TypeError) as exc:
                        sid = row.get("session_id", "?")
                        if not merge:
                            raise click.ClickException(f"Invalid snapshot data for {sid}: {exc}") from exc
                        click.echo(
                            f"  WARNING: {sid}: invalid snapshot data skipped ({exc})",
                            err=True,
                        )
                        rejected += 1
                        continue

                row_cols = list(row.keys())
                placeholders = ", ".join(["?"] * len(row_cols))
                col_names = ", ".join(row_cols)

                try:
                    conn.execute(
                        f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})",
                        [row[c] for c in row_cols],
                    )
                    imported += 1
                except sqlite3.IntegrityError:
                    if not merge:
                        raise
                    # In merge mode, skip duplicate-key conflicts only

            counts[table_name] = imported
            if rejected > 0:
                click.echo(f"  WARNING: {table_name}: {rejected} rows rejected (unknown columns)", err=True)

        if skipped_tables:
            click.echo(f"  WARNING: Skipped unknown tables: {sorted(skipped_tables)}", err=True)

        conn.commit()
        total = sum(counts.values())
        click.echo(f"Imported {total} rows from {file}")
        for tbl, cnt in sorted(counts.items()):
            if cnt > 0:
                click.echo(f"  {tbl}: {cnt}")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# gt db
# ---------------------------------------------------------------------------


@main.group("db")
def db_cmd() -> None:
    """Database operations."""


@db_cmd.command("snapshot")
@click.option("--output-dir", type=click.Path(path_type=Path), default=None, help="Snapshot publish directory")
@click.option("--staging-dir", type=click.Path(path_type=Path), default=None, help="Temporary staging directory")
@click.option("--retain", "retain_recent", type=int, default=None, help="Recent snapshots to retain")
@click.option("--daily-days", "retain_daily_days", type=int, default=None, help="Daily snapshot retention window")
@click.option("--fast", is_flag=True, help="Use sqlite3 backup API instead of VACUUM INTO")
@click.option("--include-chroma", is_flag=True, help="Also snapshot ChromaDB data; fails closed in this slice")
@click.option("--json", "json_output", is_flag=True, help="Emit structured JSON")
@click.pass_context
def db_snapshot_cmd(
    ctx: click.Context,
    output_dir: Path | None,
    staging_dir: Path | None,
    retain_recent: int | None,
    retain_daily_days: int | None,
    fast: bool,
    include_chroma: bool,
    json_output: bool,
) -> None:
    """Create a consistent, integrity-checked SQLite snapshot."""
    cfg = _resolve_config(ctx)
    try:
        result = create_snapshot(
            cfg,
            output_dir=output_dir,
            staging_dir=staging_dir,
            retain_recent=retain_recent,
            retain_daily_days=retain_daily_days,
            fast=fast,
            include_chroma=include_chroma or None,
        )
    except SnapshotError as exc:
        if json_output:
            click.echo(json.dumps({"status": "error", "exit_code": exc.exit_code, "message": str(exc)}, indent=2))
        else:
            click.echo(f"ERROR: {exc}", err=True)
        raise SystemExit(exc.exit_code) from exc

    if json_output:
        click.echo(json.dumps(result.to_json_dict(), indent=2, sort_keys=True))
        return

    click.echo(f"Snapshot created: {result.final_path}")
    click.echo(f"Manifest: {result.manifest_path}")
    click.echo(f"Method: {result.method}")
    click.echo(f"Integrity: {result.integrity_result}")
    if result.warnings:
        for warning in result.warnings:
            click.echo(f"WARNING: {warning}", err=True)
    click.echo(f"Retention: retained {result.retained_count}, deleted {result.deleted_count}")


# ---------------------------------------------------------------------------
# gt config
# ---------------------------------------------------------------------------


@main.command()
@click.pass_context
def config(ctx: click.Context) -> None:
    """Show resolved configuration."""
    cfg = _resolve_config(ctx)
    click.echo(f"\n{'=' * 50}")
    click.echo("  GroundTruth KB — Resolved Config")
    click.echo(f"{'=' * 50}")
    click.echo(f"  db_path:           {cfg.db_path}")
    click.echo(f"  project_root:      {cfg.project_root}")
    click.echo(f"  app_title:         {cfg.app_title}")
    click.echo(f"  brand_mark:        {cfg.brand_mark}")
    click.echo(f"  brand_color:       {cfg.brand_color}")
    click.echo(f"  logo_url:          {cfg.logo_url}")
    click.echo(f"  legal_footer:      {cfg.legal_footer or '(none)'}")
    if cfg.chroma_path is not None:
        click.echo(f"  chroma_path:       {cfg.chroma_path}")
    else:
        try:
            import chromadb as _chromadb  # noqa: F401

            fallback = cfg.db_path.parent / ".groundtruth-chroma"
            click.echo(f"  chroma_path:       (unset — runtime fallback: {fallback})")
        except ImportError:
            click.echo("  chroma_path:       (unset — chromadb not installed)")
    click.echo(f"  governance_gates:  {cfg.governance_gates or '(builtins only)'}")
    click.echo(f"  backup_output_dir: {cfg.backup.snapshot_output_dir or '(default)'}")
    click.echo(f"  backup_staging_dir:{cfg.backup.snapshot_staging_dir or '(default)'}")
    click.echo(f"  backup_retain:     {cfg.backup.retain_recent} recent, {cfg.backup.retain_daily_days} daily days")
    click.echo(f"{'=' * 50}\n")


# ---------------------------------------------------------------------------
# gt serve
# ---------------------------------------------------------------------------


@main.command()
@click.option("--port", default=8090, help="Port for the web UI")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.pass_context
def serve(ctx: click.Context, port: int, host: str) -> None:
    """Start the GroundTruth KB web UI (requires groundtruth-kb[web])."""
    try:
        from groundtruth_kb.web import create_app
    except ImportError as exc:
        click.echo("Web UI requires extra dependencies. Install with [web] extra.")
        raise SystemExit(1) from exc

    import os

    try:
        import uvicorn
    except ImportError as exc:
        click.echo("Web UI requires uvicorn. Install with [web] extra.")
        raise SystemExit(1) from exc

    config = _resolve_config(ctx)
    db = _open_db(config, check_same_thread=False)
    app = create_app(config, db)

    # Respect PORT env var (for preview tools), then --port flag
    effective_port = int(os.environ.get("PORT", 0)) or port

    click.echo(f"\n  {config.app_title} — Web UI")
    click.echo(f"  http://{host}:{effective_port}")
    click.echo(f"  Database: {config.db_path}\n")

    uvicorn.run(app, host=host, port=effective_port, log_level="info")


# ---------------------------------------------------------------------------
# gt dashboard
# ---------------------------------------------------------------------------


@main.group()
def dashboard() -> None:
    """Generate and run the local Grafana operations dashboard."""


def _resolve_dashboard_config(ctx: click.Context, target_dir: str | None) -> GTConfig:
    if target_dir:
        project_root = Path(target_dir).resolve()
        config_path = project_root / "groundtruth.toml"
        if not config_path.exists():
            raise click.ClickException(f"groundtruth.toml not found in {project_root}")
        return GTConfig.load(config_path=config_path)
    return _resolve_config(ctx)


def _dashboard_paths(
    config: GTConfig,
    db_path: str | None,
    runtime_root: str | None,
    grafana_home: str | None,
) -> DashboardPaths:
    from groundtruth_kb.dashboard import resolve_dashboard_paths

    return resolve_dashboard_paths(
        config,
        db_path=Path(db_path) if db_path else None,
        runtime_root=Path(runtime_root) if runtime_root else None,
        grafana_home=Path(grafana_home) if grafana_home else None,
    )


@dashboard.command("init")
@click.option(
    "--dir", "target_dir", type=click.Path(), default=None, help="Project directory (default: config auto-discovery)"
)
@click.option("--db-path", type=click.Path(), default=None, help="Dashboard SQLite path")
@click.option("--runtime-root", type=click.Path(), default=None, help="Dashboard runtime directory")
@click.option("--grafana-home", type=click.Path(), default=None, help="Grafana install/home directory")
@click.pass_context
def dashboard_init(
    ctx: click.Context,
    target_dir: str | None,
    db_path: str | None,
    runtime_root: str | None,
    grafana_home: str | None,
) -> None:
    """Create dashboard DB, Grafana provisioning, and dashboard JSON."""
    from groundtruth_kb.dashboard import initialize_dashboard

    config = _resolve_dashboard_config(ctx, target_dir)
    paths = _dashboard_paths(config, db_path, runtime_root, grafana_home)
    initialize_dashboard(paths, config)
    click.echo("GroundTruth KB dashboard initialized.")
    click.echo(f"  Dashboard DB: {paths.db_path}")
    click.echo(f"  Grafana provisioning: {paths.provisioning_dir}")
    click.echo(f"  Dashboard JSON: {paths.dashboards_dir / 'groundtruth-kb-dashboard.json'}")


@dashboard.command("refresh")
@click.option(
    "--dir", "target_dir", type=click.Path(), default=None, help="Project directory (default: config auto-discovery)"
)
@click.option("--db-path", type=click.Path(), default=None, help="Dashboard SQLite path")
@click.option("--runtime-root", type=click.Path(), default=None, help="Dashboard runtime directory")
@click.pass_context
def dashboard_refresh(
    ctx: click.Context,
    target_dir: str | None,
    db_path: str | None,
    runtime_root: str | None,
) -> None:
    """Refresh the generated dashboard SQLite database."""
    from groundtruth_kb.dashboard import refresh_dashboard_db, write_grafana_assets

    config = _resolve_dashboard_config(ctx, target_dir)
    paths = _dashboard_paths(config, db_path, runtime_root, None)
    refresh_dashboard_db(paths, config)
    write_grafana_assets(paths, config)
    click.echo(f"Dashboard data refreshed: {paths.db_path}")


@dashboard.command("install")
@click.option(
    "--dir", "target_dir", type=click.Path(), default=None, help="Project directory (default: config auto-discovery)"
)
@click.option("--db-path", type=click.Path(), default=None, help="Dashboard SQLite path")
@click.option("--runtime-root", type=click.Path(), default=None, help="Dashboard runtime directory")
@click.option("--grafana-home", type=click.Path(), default=None, help="Grafana install/home directory")
@click.option("--skip-download", is_flag=True, help="Do not download Grafana; require an existing installation")
@click.option("--skip-plugin", is_flag=True, help="Do not install the SQLite datasource plugin")
@click.pass_context
def dashboard_install(
    ctx: click.Context,
    target_dir: str | None,
    db_path: str | None,
    runtime_root: str | None,
    grafana_home: str | None,
    skip_download: bool,
    skip_plugin: bool,
) -> None:
    """Install local Grafana OSS and the SQLite datasource plugin."""
    from groundtruth_kb.dashboard import initialize_dashboard, install_grafana

    config = _resolve_dashboard_config(ctx, target_dir)
    paths = _dashboard_paths(config, db_path, runtime_root, grafana_home)
    initialize_dashboard(paths, config)
    try:
        grafana_bin = install_grafana(paths, skip_download=skip_download, skip_plugin=skip_plugin)
    except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Grafana ready: {grafana_bin}")


@dashboard.command("start")
@click.option(
    "--dir", "target_dir", type=click.Path(), default=None, help="Project directory (default: config auto-discovery)"
)
@click.option("--db-path", type=click.Path(), default=None, help="Dashboard SQLite path")
@click.option("--runtime-root", type=click.Path(), default=None, help="Dashboard runtime directory")
@click.option("--grafana-home", type=click.Path(), default=None, help="Grafana install/home directory")
@click.option("--grafana-port", type=int, default=3000, show_default=True, help="Grafana HTTP port")
@click.option("--refresh-port", type=int, default=8766, show_default=True, help="Refresh service HTTP port")
@click.option("--interval-minutes", type=int, default=60, show_default=True, help="Scheduled refresh interval")
@click.pass_context
def dashboard_start(
    ctx: click.Context,
    target_dir: str | None,
    db_path: str | None,
    runtime_root: str | None,
    grafana_home: str | None,
    grafana_port: int,
    refresh_port: int,
    interval_minutes: int,
) -> None:
    """Start Grafana and the local dashboard refresh service."""
    from groundtruth_kb.dashboard import start_dashboard

    config = _resolve_dashboard_config(ctx, target_dir)
    paths = _dashboard_paths(config, db_path, runtime_root, grafana_home)
    try:
        info = start_dashboard(
            paths,
            config,
            grafana_port=grafana_port,
            refresh_port=refresh_port,
            interval_minutes=interval_minutes,
        )
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo("GroundTruth KB dashboard started.")
    click.echo(f"  Grafana: {info.grafana_url} (pid {info.grafana_pid})")
    click.echo(f"  Refresh service: {info.refresh_url} (pid {info.refresh_pid})")


@dashboard.command("stop")
@click.option(
    "--dir", "target_dir", type=click.Path(), default=None, help="Project directory (default: config auto-discovery)"
)
@click.option("--runtime-root", type=click.Path(), default=None, help="Dashboard runtime directory")
@click.option("--grafana-home", type=click.Path(), default=None, help="Grafana install/home directory")
@click.pass_context
def dashboard_stop(
    ctx: click.Context,
    target_dir: str | None,
    runtime_root: str | None,
    grafana_home: str | None,
) -> None:
    """Stop dashboard processes started by ``gt dashboard start``."""
    from groundtruth_kb.dashboard import stop_dashboard

    config = _resolve_dashboard_config(ctx, target_dir)
    paths = _dashboard_paths(config, None, runtime_root, grafana_home)
    stopped = stop_dashboard(paths)
    if stopped:
        click.echo(f"Stopped dashboard processes: {', '.join(str(pid) for pid in stopped)}")
    else:
        click.echo("No dashboard processes were recorded as running.")


# ── gt project (Layer 2 + 3) ─────────────────────────────────────────


@main.group()
def project() -> None:
    """Project scaffold, doctor, and upgrade commands."""


@project.command("init")
@click.argument("project_name")
@click.option(
    "--profile",
    type=click.Choice(["local-only", "dual-agent", "dual-agent-webapp"]),
    default="local-only",
    help="Scaffold profile (default: local-only).",
)
@click.option("--owner", default="", help="Organization or owner name.")
@click.option("--copyright", "copyright_notice", default="", help="Copyright notice.")
@click.option(
    "--cloud-provider",
    type=click.Choice(["azure", "aws", "gcp", "none"]),
    default="none",
    help="Cloud provider for infrastructure stubs.",
)
@click.option("--dir", "target_dir", default=None, help="Target directory (default: ./<project_name>).")
@click.option("--init-git/--no-init-git", default=False, help="Initialize a git repository.")
@click.option("--include-ci/--no-include-ci", default=True, help="Include CI workflows.")
@click.option("--seed-example/--no-seed-example", default=True, help="Seed example specs.")
@click.option("--prime-provider", default="claude-code", help="Prime Builder provider ID.")
@click.option("--lo-provider", default="codex", help="Loyal Opposition provider ID.")
@click.option(
    "--integrations/--no-integrations",
    default=False,
    help="Generate optional integration config files (Dependabot, CodeRabbit).",
)
@click.option(
    "--python-version",
    default="3.11",
    show_default=True,
    help="Python version for generated CI workflows.",
)
@click.option(
    "--opt-out-core-spec-intake",
    is_flag=True,
    default=False,
    help="Skip default core-spec intake enrollment for this project (automation/unusual cases).",
)
@click.option(
    "--gt-kb-root",
    "gt_kb_root_arg",
    default=None,
    help=(
        "GT-KB host root path. Source checkouts require this to resolve to the "
        "active workspace root; installed wheels accept this as the adopter host "
        "root and default to the current directory. Per "
        "ADR-ISOLATION-APPLICATION-PLACEMENT-001, applications are created at "
        "<gt-kb-root>/applications/<project_name>/."
    ),
)
def project_init(
    project_name: str,
    profile: str,
    owner: str,
    copyright_notice: str,
    cloud_provider: str,
    target_dir: str | None,
    init_git: bool,
    include_ci: bool,
    seed_example: bool,
    prime_provider: str,
    lo_provider: str,
    integrations: bool,
    python_version: str,
    opt_out_core_spec_intake: bool,
    gt_kb_root_arg: str | None,
) -> None:
    """Scaffold a new GroundTruth project with the selected profile."""
    from groundtruth_kb.project.scaffold import (
        ScaffoldOptions,
        _resolve_gt_kb_host_root,
        scaffold_project,
        scaffold_summary,
    )
    from groundtruth_kb.providers.schema import get_provider

    # Validate provider IDs and bridge roles
    try:
        prime_prov = get_provider(prime_provider)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    if prime_prov.bridge_role != "prime":
        raise click.UsageError(
            f"Provider '{prime_provider}' has role '{prime_prov.bridge_role}'"
            " but --prime-provider requires bridge_role='prime'"
        )

    try:
        lo_prov = get_provider(lo_provider)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    if lo_prov.bridge_role != "loyal-opposition":
        raise click.UsageError(
            f"Provider '{lo_provider}' has role '{lo_prov.bridge_role}'"
            " but --lo-provider requires bridge_role='loyal-opposition'"
        )

    # GTKB-ISOLATION-017 Slice 3: bind gt-kb-root to literal in-root workspace
    # path. Resolution rejects mismatched explicit roots. The resolved value is
    # then threaded into ScaffoldOptions to enforce
    # _validate_application_target at scaffold time.
    explicit_root = Path(gt_kb_root_arg) if gt_kb_root_arg else None
    try:
        host_root = _resolve_gt_kb_host_root(explicit_root)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc

    target = Path(target_dir) if target_dir else host_root / "applications" / project_name

    options = ScaffoldOptions(
        project_name=project_name,
        profile=profile,
        owner=owner,
        target_dir=target,
        copyright_notice=copyright_notice,
        cloud_provider=cloud_provider,
        init_git=init_git,
        include_ci=include_ci,
        seed_example=seed_example,
        prime_provider_id=prime_provider,
        lo_provider_id=lo_provider,
        integrations=integrations,
        python_version=python_version,
        opt_out_core_spec_intake=opt_out_core_spec_intake,
        gt_kb_root=host_root,
    )
    try:
        result = scaffold_project(options)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    click.echo(scaffold_summary(result, profile))


@project.group("chroma")
def project_chroma() -> None:
    """Manage disposable project ChromaDB caches."""


@project_chroma.command("regenerate")
@click.option("--dir", "target_dir", default=".", help="Adopter project directory (default: cwd).")
@click.option("--dry-run", is_flag=True, default=False, help="Report what would be regenerated without writing.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
def project_chroma_regenerate(target_dir: str, dry_run: bool, json_output: bool) -> None:
    """Regenerate the disposable ChromaDB cache from groundtruth.db."""
    from groundtruth_kb.project.chroma import regenerate

    try:
        result = regenerate(Path(target_dir), dry_run=dry_run)
    except (FileNotFoundError, OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(result.to_json_dict(), indent=2, sort_keys=True))
    else:
        click.echo(f"ChromaDB cache {result.status}: {result.chroma_path}")
        click.echo(f"  source: {result.db_path}")
        if result.removed_paths:
            click.echo(f"  stale files replaced: {len(result.removed_paths)}")
        if result.indexed or result.chunks:
            click.echo(f"  indexed deliberations: {result.indexed}")
            click.echo(f"  chunks: {result.chunks}")
        for error in result.errors:
            click.echo(f"  error: {error}", err=True)

    if result.status == "skipped":
        raise SystemExit(2)
    if result.status == "error":
        raise SystemExit(1)


@project.command("doctor")
@click.option("--auto-install", is_flag=True, default=False, help="Auto-install safe tools.")
@click.option("--profile", default=None, help="Profile to check against (auto-detected if omitted).")
@click.option("--dir", "target_dir", default=".", help="Project directory (default: cwd).")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
def project_doctor(auto_install: bool, profile: str | None, target_dir: str, json_output: bool) -> None:
    """Check workstation readiness and optionally install missing tools."""
    from groundtruth_kb.project.doctor import format_doctor_report, format_doctor_report_json, run_doctor

    target = Path(target_dir).resolve()

    # Auto-detect profile from manifest
    if profile is None:
        from groundtruth_kb.project.manifest import read_manifest

        manifest = read_manifest(target / "groundtruth.toml")
        profile = manifest.profile if manifest else "local-only"

    report = run_doctor(target, profile, auto_install=auto_install)

    from groundtruth_kb.isolation.doctor_verdicts import evaluate_isolation_state
    from groundtruth_kb.project.doctor import ToolCheck

    iso_state = evaluate_isolation_state(target)
    if iso_state["verdicts"]:
        for v in iso_state["verdicts"]:
            status: Literal["pass", "fail", "warning", "info"] = "fail" if v["severity"] in {"P0", "P1"} else "warning"
            required = v["severity"] in {"P0", "P1"}
            check = ToolCheck(
                name=f"isolation:{v['verdict'].lower().replace(' ', '-')}",
                required=required,
                found=True,
                status=status,
                message=f"{v['verdict']} severity {v['severity']}: {v['details']}. {v['remediation']}",
            )
            report.checks.append(check)
    else:
        check = ToolCheck(
            name="isolation:application-registry",
            required=True,
            found=True,
            status="pass",
            message="Application slot cardinality and markers: clean",
        )
        report.checks.append(check)

    report._compute_overall()

    if json_output:
        click.echo(json.dumps(format_doctor_report_json(report), indent=2, sort_keys=True))
    else:
        click.echo(format_doctor_report(report))

    if report.overall == "fail":
        raise SystemExit(1)


_REHEARSAL_RECIPE_BLOCK = """
========================================================================
ISOLATION MIGRATION RECIPE (Phase 8 rehearsal — out-of-band)
========================================================================
Before running `gt project upgrade --apply --accept-migration`, run the
rehearsal driver to preview the migration outcome:

  python scripts/rehearse_isolation.py --execute \\
      --output-dir <sandbox-path>

The sandbox path must be outside the GT-KB project root per
DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE (e.g.,
C:/temp/agent-red-rehearsal* on Windows or /tmp/agent-red-rehearsal*
on POSIX).

After reviewing the rehearsal preview, re-run:

  gt project upgrade --apply --accept-migration

This will run the 4 isolation auto-fixers (service-endpoint, work-subject,
workstream-focus-hook-absent, release-readiness-app-subject-header) inside
a payload branch. A rollback receipt is written; `gt project rollback`
reverses any failed migration.

Needs-adopter-input checks (no-writable-product-paths,
hooks-point-to-wrappers, chroma-regeneratable)
require manual inspection — upgrade refuses these even with
--accept-migration. For hooks-point-to-wrappers: inspect
.claude/settings.json for hook commands that aren't wrapper-shaped (i.e.,
not under .claude/hooks/, not invoking groundtruth_kb, not using
${CLAUDE_PLUGIN_ROOT}); either delete the customization or rewrap it.
========================================================================
""".strip()


@project.command("upgrade")
@click.option("--dry-run/--apply", default=True, help="Preview changes without writing (default: dry-run).")
@click.option("--force", is_flag=True, default=False, help="Overwrite customized files.")
@click.option("--dir", "target_dir", default=".", help="Project directory (default: cwd).")
@click.option(
    "--ignore-inflight-bridges",
    is_flag=True,
    default=False,
    help="Suppress the 'bridge in-flight' pre-flight warning (automation).",
)
@click.option(
    "--accept-migration",
    is_flag=True,
    default=False,
    help=(
        "GTKB-ISOLATION-017 Slice 4: opt in to one-shot isolation migration of "
        "auto-fixable in-place defects (service endpoint, work_subject, "
        "workstream-focus deletion, release-readiness banner). Required when "
        "isolation doctor checks fail; without it the upgrade refuses with the "
        "rehearsal recipe. Per DELIB-S328 mandatory_at_upgrade decision."
    ),
)
def project_upgrade(
    dry_run: bool,
    force: bool,
    target_dir: str,
    ignore_inflight_bridges: bool,
    accept_migration: bool,
) -> None:
    """Update scaffold files to match the current GroundTruth version.

    ``--apply`` runs the upgrade inside a short-lived payload branch that
    merges back into the current branch to produce a rollback receipt
    anchored on a real merge commit. Requires a git work tree with a clean
    index; see ``docs/reference/upgrade-receipts.md``.

    Dry-run surfaces non-mutating pre-flight diagnostics (``[WARNING]``
    for in-flight bridges; ``[INFORMATIONAL]`` for scaffold-coverage
    delta). Those rows are filtered out before apply so pre-flight
    reporting never triggers git or file writes, even with ``--force``.

    GTKB-ISOLATION-017 Slice 4: ``--apply`` refuses when isolation doctor
    checks fail unless ``--accept-migration`` is set. With the flag, the
    five in-place auto-fixers run inside the same payload branch + rollback
    receipt. Adopter-root-placement violations (check #1) refuse
    unconditionally. Needs-adopter-input checks (#4 / #7 / #9) refuse even
    with ``--accept-migration``.
    """
    from groundtruth_kb.project.upgrade import (
        _NON_MUTATING_ACTION_KINDS,
        DirtyWorkingTreeError,
        IsolationLocationFailureError,
        IsolationMigrationRequiredError,
        IsolationNonAutoFixableError,
        IsolationPolicyOverrideViolation,
        MalformedSettingsError,
        MergeFailedError,
        NotAGitRepositoryError,
        _has_malformed_settings_skip,
        execute_upgrade,
        plan_upgrade,
    )

    target = Path(target_dir).resolve()
    actions = plan_upgrade(target, ignore_inflight_bridges=ignore_inflight_bridges)

    if not actions:
        click.echo("Already at current version. Nothing to upgrade.")
        return

    for action in actions:
        status = action.action.upper()
        click.echo(f"  [{status}] {action.file} — {action.reason}")

    if dry_run:
        click.echo(f"\n{len(actions)} action(s). Run with --apply to execute.")
        return

    # Halt before execute_upgrade if ``.claude/settings.json`` is malformed.
    # This is the CLI-side arm of the C2 contract — ``execute_upgrade`` also
    # raises :class:`MalformedSettingsError` as defense in depth for library
    # callers, but catching it here keeps the adopter-facing error local.
    malformed = _has_malformed_settings_skip(actions)
    if malformed is not None:
        click.echo(
            f"\nError: Malformed .claude/settings.json — repair and re-run.\nPlanner reason: {malformed.reason}",
            err=True,
        )
        raise SystemExit(4)

    # Filter pre-flight ``warning`` and ``informational`` rows out of the
    # action list before handing it to ``execute_upgrade``. Per C1, these
    # must never reach the git/manifest write path — even with ``--force``.
    mutating_actions = [a for a in actions if a.action not in _NON_MUTATING_ACTION_KINDS]

    if not mutating_actions:
        click.echo("\nPre-flight only — no mutating actions to apply.")
        # Slice 4: even without mutating routine actions, isolation gating may
        # still need to run via execute_upgrade if accept_migration was set.
        # However, if isolation pre-flight is clean too (already covered by
        # informational [ISOLATION] all-checks-pass row), there's nothing to do.
        # Detection of failing isolation rows in `actions` indicates work needed.
        has_isolation_warning = any(a.action == "warning" and a.file.startswith("<isolation:") for a in actions)
        if not has_isolation_warning:
            return
        # Fall through to execute_upgrade with empty mutating_actions so the
        # isolation pre-flight gating + auto-fixer dispatch path runs.

    try:
        results = execute_upgrade(
            target,
            mutating_actions,
            force=force,
            accept_migration=accept_migration,
        )
    except MalformedSettingsError as exc:
        click.echo(f"\nError: {exc}", err=True)
        raise SystemExit(4) from exc
    except NotAGitRepositoryError as exc:
        click.echo(f"\nError: {exc}", err=True)
        raise SystemExit(2) from exc
    except DirtyWorkingTreeError as exc:
        click.echo(f"\nError: {exc}", err=True)
        raise SystemExit(2) from exc
    except MergeFailedError as exc:
        click.echo(f"\nError: {exc}", err=True)
        raise SystemExit(3) from exc
    except IsolationLocationFailureError as exc:
        click.echo(f"\nError: {exc}", err=True)
        click.echo(
            "\nThis check cannot be auto-fixed by `gt project upgrade`. "
            "Relocate the adopter directory to <gt-kb-root>/applications/<name>/.",
            err=True,
        )
        raise SystemExit(5) from exc
    except IsolationMigrationRequiredError as exc:
        click.echo(f"\nError: {exc}", err=True)
        click.echo(f"\n{_REHEARSAL_RECIPE_BLOCK}", err=True)
        raise SystemExit(5) from exc
    except IsolationNonAutoFixableError as exc:
        click.echo(f"\nError: {exc}", err=True)
        click.echo(
            "\nNeeds-adopter-input checks require manual inspection. "
            "See each check's reported message for the offending file/state.",
            err=True,
        )
        raise SystemExit(5) from exc
    except IsolationPolicyOverrideViolation as exc:
        # Defense-in-depth signal — should never fire in production.
        click.echo(f"\nInternal error (please report): {exc}", err=True)
        raise SystemExit(5) from exc

    for msg in results:
        click.echo(f"  {msg}")


# ---------------------------------------------------------------------------
# C3: gt project rollback — consume a receipt to revert an upgrade
# ---------------------------------------------------------------------------


@project.command("rollback")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help=(
        "Plan the rollback without executing. Default behavior if neither "
        "--dry-run nor --apply is supplied. Mutually exclusive with --apply."
    ),
)
@click.option(
    "--apply",
    is_flag=True,
    default=False,
    help=(
        "Execute the rollback: git revert -m 1 <merge_commit> --no-commit. "
        "Leaves the revert staged for review. Mutually exclusive with --dry-run."
    ),
)
@click.option(
    "--commit",
    is_flag=True,
    default=False,
    help=(
        "When combined with --apply, commits the revert automatically with "
        "message 'gt: rollback upgrade payload {receipt_id}'. Requires --apply."
    ),
)
@click.option(
    "--receipt-id",
    default=None,
    help=(
        "Specific receipt ID to roll back. If omitted, the latest receipt "
        "(by created_at desc, tie-break on receipt_id desc) is used."
    ),
)
@click.option(
    "--target-dir",
    default=".",
    help="Directory containing .claude/upgrade-receipts/ to consume. Defaults to current directory.",
)
@click.pass_context
def project_rollback(
    ctx: click.Context,
    dry_run: bool,
    apply: bool,
    commit: bool,
    receipt_id: str | None,
    target_dir: str,
) -> None:
    """Roll back a previously-applied ``gt project upgrade --apply``.

    Consumes a rollback receipt (written by ``gt project upgrade --apply``)
    and runs ``git revert -m 1 <merge_commit>`` against the adopter's
    working tree. By default leaves the revert staged for review; pass
    ``--commit`` with ``--apply`` to auto-commit.

    See docs/reference/cli.md and docs/reference/upgrade-receipts.md for
    full workflow + receipt schema.
    """
    from pathlib import Path as _Path

    from groundtruth_kb.project.rollback import (
        DirtyWorkingTreeError,
        MergeCommitNotInHistoryError,
        NotAMergeCommitError,
        ReceiptMalformedError,
        ReceiptNotFoundError,
        ReceiptSchemaVersionMismatchError,
        RollbackFailedError,
        execute_rollback,
        plan_rollback,
    )

    # Flag validation (C3 -005 F4 required: explicit mutual exclusion).
    if dry_run and apply:
        raise click.UsageError("--dry-run and --apply are mutually exclusive. Pick one.")
    if commit and not apply:
        raise click.UsageError("--commit requires --apply.")
    # Default to dry-run if neither flag supplied.
    if not dry_run and not apply:
        dry_run = True

    root = _Path(target_dir).resolve()

    try:
        plan = plan_rollback(root, receipt_id=receipt_id)
    except ReceiptNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(2)
        return
    except ReceiptSchemaVersionMismatchError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(3)
        return
    except ReceiptMalformedError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(3)
        return
    except NotAMergeCommitError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(4)
        return
    except MergeCommitNotInHistoryError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(5)
        return

    receipt = plan.receipt
    click.echo(f"Rollback plan — receipt {receipt['receipt_id']} ({receipt['mode']} mode)")
    click.echo(f"  target merge commit: {plan.merge_commit}")
    click.echo(f"  target branch:       {receipt['target_branch']}")
    click.echo(f"  from_version:        {receipt['from_version']}")
    click.echo(f"  to_version:          {receipt['to_version']}")
    click.echo(f"  created_at:          {receipt['created_at']}")
    click.echo(f"  files to revert:     {len(plan.files_to_revert)}")
    for entry in plan.files_to_revert:
        click.echo(f"    [{entry.status}] {entry.path}")

    if dry_run:
        click.echo("")
        click.echo("Dry run — no changes applied. Pass --apply to execute.")
        return

    # Apply path.
    try:
        result = execute_rollback(root, plan, commit=commit)
    except DirtyWorkingTreeError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(6)
        return
    except RollbackFailedError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(7)
        return

    click.echo("")
    click.echo(f"Rollback executed — mode={result.mode}")
    if result.commit_sha is not None:
        click.echo(f"  new commit: {result.commit_sha}")
    else:
        click.echo("  revert is staged; run `git commit` (or reset) to finalize.")


@project.command("classify-tree")
@click.option(
    "--dir",
    "target_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Target tree root to classify (does NOT require groundtruth.toml).",
)
@click.option(
    "--output",
    "output_path",
    required=True,
    type=click.Path(dir_okay=False),
    help="Output report path (written relative to CWD).",
)
@click.option("--max-depth", "max_depth", type=int, default=10, show_default=True, help="Maximum walk depth.")
@click.option(
    "--ignore-glob",
    "ignore_globs",
    multiple=True,
    help="Additive ignore glob (may be repeated).",
)
@click.option(
    "--format",
    "report_format",
    type=click.Choice(["markdown", "json"]),
    default="markdown",
    show_default=True,
    help="Report format.",
)
def project_classify_tree(
    target_dir: str,
    output_path: str,
    max_depth: int,
    ignore_globs: tuple[str, ...],
    report_format: str,
) -> None:
    """Classify every file under --dir against the ownership matrix.

    Manifest-independent: does NOT require ``groundtruth.toml`` in the target
    tree, and does NOT call ``gt project doctor`` or any manifest / DB
    checks. READ-ONLY: no writes are made to the target tree. The
    classification report is written to ``--output``.
    """
    import subprocess

    from groundtruth_kb import __version__
    from groundtruth_kb.project.ownership import (
        _DEFAULT_IGNORE_GLOBS,
        OwnershipResolver,
        render_classification_report_json,
        render_classification_report_markdown,
    )

    target = Path(target_dir).resolve()

    resolver = OwnershipResolver()
    combined_ignores = tuple(_DEFAULT_IGNORE_GLOBS) + tuple(ignore_globs)
    rows = resolver.classify_tree(target, max_depth=max_depth, ignore_globs=combined_ignores)

    # Best-effort HEAD-SHA resolution. Failures (no git, detached HEAD, etc.)
    # fall back to the literal string "unknown".
    def _git_head(path: Path) -> str:
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(path),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if r.returncode == 0:
                return r.stdout.strip() or "unknown"
            return "unknown"
        except (OSError, subprocess.TimeoutExpired):
            return "unknown"

    gt_kb_root = Path(__file__).parent.parent.parent
    gt_kb_head = _git_head(gt_kb_root)
    target_head = _git_head(target)

    if report_format == "json":
        content = render_classification_report_json(
            rows,
            gt_kb_version=__version__,
            gt_kb_head=gt_kb_head,
            target_tree=str(target),
            target_head=target_head,
        )
    else:
        content = render_classification_report_markdown(
            rows,
            gt_kb_version=__version__,
            gt_kb_head=gt_kb_head,
            target_tree=str(target),
            target_head=target_head,
        )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")

    click.echo(f"Wrote {len(rows)} classification row(s) to {output}")


# --- gt spec -----------------------------------------------------------------


@main.group("spec")
def spec_cmd() -> None:
    """Governed specification artifact commands."""


def _echo_spec_row(row: dict[str, Any]) -> None:
    click.echo(f"{row['id']} (version {row.get('version', '?')})")
    click.echo(f"  title:       {row.get('title', '')}")
    click.echo(f"  status:      {row.get('status', '')}")
    if row.get("type"):
        click.echo(f"  type:        {row['type']}")
    if row.get("priority"):
        click.echo(f"  priority:    {row['priority']}")
    if row.get("section"):
        click.echo(f"  section:     {row['section']}")
    if row.get("handle"):
        click.echo(f"  handle:      {row['handle']}")
    if row.get("authority"):
        click.echo(f"  authority:   {row['authority']}")
    if row.get("testability"):
        click.echo(f"  testability: {row['testability']}")
    description = row.get("description", "") or ""
    if description:
        click.echo("  description:")
        for line in description.splitlines():
            click.echo(f"    {line}")


@spec_cmd.command("show")
@click.argument("spec_id")
@click.option("--history", is_flag=True, default=False, help="Show the full version history.")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def spec_show_cmd(ctx: click.Context, spec_id: str, history: bool, json_output: bool) -> None:
    """Show a specification by ID."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    try:
        if history:
            rows = db.get_spec_history(spec_id)
            if not rows:
                click.echo(f"Specification {spec_id} not found.")
                raise SystemExit(1)
            if json_output:
                click.echo(json.dumps(rows, indent=2, default=str))
                return
            click.echo(f"Version history for {spec_id} ({len(rows)} version(s)):")
            for row in rows:
                click.echo(f"--- version {row.get('version', '?')} ---")
                _echo_spec_row(row)
            return

        row = db.get_spec(spec_id)
        if row is None:
            click.echo(f"Specification {spec_id} not found.")
            raise SystemExit(1)
        if json_output:
            click.echo(json.dumps(row, indent=2, default=str))
            return
        _echo_spec_row(row)
    finally:
        db.close()


@spec_cmd.command("list")
@click.option("--status", default=None, help="Filter by lifecycle status.")
@click.option("--priority", default=None, help="Filter by priority.")
@click.option("--section", default=None, help="Filter by section substring.")
@click.option("--handle", default=None, help="Filter by exact handle.")
@click.option("--tag", default=None, help="Filter by tag.")
@click.option("--search", default=None, help="Search title and description.")
@click.option("--type", "spec_type", default=None, help="Filter by spec type.")
@click.option("--authority", default=None, help="Filter by authority.")
@click.option("--testability", default=None, help="Filter by testability.")
@click.option("--limit", type=int, default=None, help="CLI-side slice; returns the first N rows.")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def spec_list_cmd(
    ctx: click.Context,
    status: str | None,
    priority: str | None,
    section: str | None,
    handle: str | None,
    tag: str | None,
    search: str | None,
    spec_type: str | None,
    authority: str | None,
    testability: str | None,
    limit: int | None,
    json_output: bool,
) -> None:
    """List current specifications with deterministic filters."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    try:
        rows = db.list_specs(
            status=status,
            priority=priority,
            section=section,
            handle=handle,
            tag=tag,
            search=search,
            type=spec_type,
            authority=authority,
            testability=testability,
        )
    finally:
        db.close()
    if limit is not None and limit >= 0:
        rows = rows[:limit]
    if json_output:
        click.echo(json.dumps(rows, indent=2, default=str))
        return
    if not rows:
        click.echo("No specifications match the given filters.")
        return
    click.echo(f"{len(rows)} specification(s):")
    for row in rows:
        click.echo(f"  {row['id']} v{row.get('version', '?')} [{row.get('status', '')}]: {row.get('title', '')}")


@spec_cmd.command("record")
@click.option("--id", "spec_id", required=True, help="Specification ID, e.g. GOV-FOO-001 or REQ-FOO-001")
@click.option("--title", required=True, help="Human-readable title")
@click.option("--status", required=True, help="Specification lifecycle status")
@click.option(
    "--content-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="In-root file whose contents become the spec description",
)
@click.option("--change-reason", required=True, help="Reason to store with the spec version")
@click.option("--auq-id", required=True, help="AskUserQuestion / AUQ evidence identifier")
@click.option("--auq-answer", required=True, help="Owner answer text or concise answer summary")
@click.option("--owner-presented", is_flag=True, default=False, help="Assert native-format content was shown to owner")
@click.option("--approved-by", default=None, help="Manual approval identity (default: owner)")
@click.option("--type", "spec_type", type=click.Choice(SPEC_RECORD_TYPES), default=None, help="Explicit spec type")
@click.option("--priority", default=None)
@click.option("--scope", default=None)
@click.option("--section", default=None)
@click.option("--handle", default=None)
@click.option("--tags-json", default=None, help="JSON list of tag strings")
@click.option("--assertions-json", default=None, help="JSON list of assertion objects")
@click.option("--constraints-json", default=None, help="JSON object of constraint metadata")
@click.option("--affected-by-json", default=None, help="JSON list of spec IDs affecting this spec")
@click.option(
    "--testability",
    type=click.Choice(["automatable", "observable", "structural", "untestable"]),
    default=None,
)
@click.option("--source-paths-json", default=None, help="JSON list of source path strings")
@click.option("--dry-run", is_flag=True, default=False, help="Validate and print the proposed packet without writing")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def spec_record_cmd(
    ctx: click.Context,
    spec_id: str,
    title: str,
    status: str,
    content_file: Path,
    change_reason: str,
    auq_id: str,
    auq_answer: str,
    owner_presented: bool,
    approved_by: str | None,
    spec_type: str | None,
    priority: str | None,
    scope: str | None,
    section: str | None,
    handle: str | None,
    tags_json: str | None,
    assertions_json: str | None,
    constraints_json: str | None,
    affected_by_json: str | None,
    testability: str | None,
    source_paths_json: str | None,
    dry_run: bool,
    json_output: bool,
) -> None:
    """Record an AUQ-backed specification through the governed service path."""

    config = _resolve_config(ctx)
    request = SpecRecordRequest(
        spec_id=spec_id,
        title=title,
        status=status,
        content_file=content_file,
        change_reason=change_reason,
        auq_id=auq_id,
        auq_answer=auq_answer,
        owner_presented=owner_presented,
        approved_by=approved_by,
        spec_type=spec_type,
        priority=priority,
        scope=scope,
        section=section,
        handle=handle,
        tags_json=tags_json,
        assertions_json=assertions_json,
        constraints_json=constraints_json,
        affected_by_json=affected_by_json,
        testability=testability,
        source_paths_json=source_paths_json,
        dry_run=dry_run,
    )
    try:
        result = record_spec(config, request)
    except SpecRecordError as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(result, indent=2, default=str))
        return
    if dry_run:
        click.echo(f"Dry run: would record spec {result['id']}.")
        click.echo(f"Approval packet path: {result['approval_packet_path']}")
        click.echo(json.dumps(result["approval_packet"], indent=2, sort_keys=True))
        return
    click.echo(result["id"])


@spec_cmd.command("update")
@click.option("--id", "spec_id", required=True, help="Existing specification ID to version")
@click.option(
    "--content-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="In-root file whose contents become the new spec description",
)
@click.option("--change-reason", required=True, help="Reason to store with the new spec version")
@click.option("--auq-id", required=True, help="AskUserQuestion / AUQ evidence identifier")
@click.option("--auq-answer", required=True, help="Owner answer text or concise answer summary")
@click.option("--owner-presented", is_flag=True, default=False, help="Assert native-format content was shown to owner")
@click.option("--approved-by", default=None, help="Manual approval identity (default: owner)")
@click.option("--title", default=None, help="Updated title (carried forward when omitted)")
@click.option("--status", default=None, help="Updated lifecycle status (carried forward when omitted)")
@click.option("--priority", default=None)
@click.option("--scope", default=None)
@click.option("--section", default=None)
@click.option("--handle", default=None)
@click.option(
    "--testability",
    type=click.Choice(["automatable", "observable", "structural", "untestable"]),
    default=None,
)
@click.option("--tags-json", default=None, help="JSON list of tag strings")
@click.option("--assertions-json", default=None, help="JSON list of assertion objects")
@click.option("--constraints-json", default=None, help="JSON object of constraint metadata")
@click.option("--affected-by-json", default=None, help="JSON list of spec IDs affecting this spec")
@click.option("--source-paths-json", default=None, help="JSON list of source path strings")
@click.option("--dry-run", is_flag=True, default=False, help="Validate and print the proposed packet without writing")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def spec_update_cmd(
    ctx: click.Context,
    spec_id: str,
    content_file: Path,
    change_reason: str,
    auq_id: str,
    auq_answer: str,
    owner_presented: bool,
    approved_by: str | None,
    title: str | None,
    status: str | None,
    priority: str | None,
    scope: str | None,
    section: str | None,
    handle: str | None,
    testability: str | None,
    tags_json: str | None,
    assertions_json: str | None,
    constraints_json: str | None,
    affected_by_json: str | None,
    source_paths_json: str | None,
    dry_run: bool,
    json_output: bool,
) -> None:
    """Create a new version of an existing AUQ-backed specification."""

    config = _resolve_config(ctx)
    request = SpecUpdateRequest(
        spec_id=spec_id,
        content_file=content_file,
        change_reason=change_reason,
        auq_id=auq_id,
        auq_answer=auq_answer,
        owner_presented=owner_presented,
        approved_by=approved_by,
        title=title,
        status=status,
        priority=priority,
        scope=scope,
        section=section,
        handle=handle,
        testability=testability,
        tags_json=tags_json,
        assertions_json=assertions_json,
        constraints_json=constraints_json,
        affected_by_json=affected_by_json,
        source_paths_json=source_paths_json,
        dry_run=dry_run,
    )
    try:
        result = update_spec(config, request)
    except SpecUpdateError as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(result, indent=2, default=str))
        return
    if dry_run:
        click.echo(f"Dry run: would update spec {result['id']} to version {result['to_version']}.")
        click.echo(f"Approval packet path: {result['approval_packet_path']}")
        click.echo(json.dumps(result["approval_packet"], indent=2, sort_keys=True))
        return
    click.echo(f"{result['id']} v{result['to_version']}")


# --- gt tests ----------------------------------------------------------------


@main.group("tests")
def tests_cmd() -> None:
    """Governed test artifact read commands."""


def _echo_test_row(row: dict[str, Any]) -> None:
    click.echo(f"{row['id']} (version {row.get('version', '?')})")
    click.echo(f"  title:       {row.get('title', '')}")
    click.echo(f"  spec_id:     {row.get('spec_id', '')}")
    click.echo(f"  type:        {row.get('test_type', '')}")
    if row.get("last_result"):
        click.echo(f"  last_result: {row['last_result']}")
    if row.get("test_file"):
        click.echo(f"  test_file:   {row['test_file']}")
    if row.get("test_function"):
        click.echo(f"  function:    {row['test_function']}")
    expected = row.get("expected_outcome", "") or ""
    if expected:
        click.echo(f"  expected:    {expected}")


@tests_cmd.command("show")
@click.argument("test_id")
@click.option("--history", is_flag=True, default=False, help="Show the full version history.")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def tests_show_cmd(ctx: click.Context, test_id: str, history: bool, json_output: bool) -> None:
    """Show a test artifact by ID."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    try:
        if history:
            rows = db.get_test_history(test_id)
            if not rows:
                click.echo(f"Test {test_id} not found.")
                raise SystemExit(1)
            if json_output:
                click.echo(json.dumps(rows, indent=2, default=str))
                return
            click.echo(f"Version history for {test_id} ({len(rows)} version(s)):")
            for row in rows:
                click.echo(f"--- version {row.get('version', '?')} ---")
                _echo_test_row(row)
            return

        row = db.get_test(test_id)
        if row is None:
            click.echo(f"Test {test_id} not found.")
            raise SystemExit(1)
        if json_output:
            click.echo(json.dumps(row, indent=2, default=str))
            return
        _echo_test_row(row)
    finally:
        db.close()


@tests_cmd.command("list")
@click.option("--spec-id", default=None, help="Filter by linked specification.")
@click.option("--test-type", default=None, help="Filter by test type.")
@click.option("--last-result", default=None, help="Filter by last result.")
@click.option("--limit", type=int, default=None, help="CLI-side slice; returns the first N rows.")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def tests_list_cmd(
    ctx: click.Context,
    spec_id: str | None,
    test_type: str | None,
    last_result: str | None,
    limit: int | None,
    json_output: bool,
) -> None:
    """List current test artifacts with deterministic filters."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    try:
        rows = db.list_tests(spec_id=spec_id, test_type=test_type, last_result=last_result)
    finally:
        db.close()
    if limit is not None and limit >= 0:
        rows = rows[:limit]
    if json_output:
        click.echo(json.dumps(rows, indent=2, default=str))
        return
    if not rows:
        click.echo("No tests match the given filters.")
        return
    click.echo(f"{len(rows)} test(s):")
    for row in rows:
        click.echo(
            f"  {row['id']} v{row.get('version', '?')} "
            f"[{row.get('test_type', '')}/{row.get('last_result') or '-'}]: {row.get('title', '')}"
        )


# ── gt deliberations ──────────────────────────────────────────────


@main.group()
def deliberations() -> None:
    """Deliberation archive commands."""


@deliberations.command("rebuild-index")
@click.pass_context
def deliberations_rebuild_index(ctx: click.Context) -> None:
    """Rebuild the ChromaDB semantic search index from SQLite.

    Drops and recreates the ChromaDB collection, re-indexing all current
    deliberations. SQLite remains the source of truth.
    """
    config = _resolve_config(ctx)
    db = KnowledgeDB(
        db_path=config.db_path,
        chroma_path=config.chroma_path,
    )
    result = db.rebuild_deliberation_index()
    if result.get("errors") and result["errors"] == ["ChromaDB not installed"]:
        click.echo("Error: ChromaDB is not installed. Install it into the gt venv with:\n  uv pip install chromadb")
        raise SystemExit(1)
    click.echo(f"Indexed {result['indexed']} deliberation(s), {result['chunks']} chunk(s).")
    if result.get("errors"):
        click.echo(f"Errors ({len(result['errors'])}):")
        for err in result["errors"]:
            click.echo(f"  {err}")


# Shared constants for deliberation commands -----------------------------------

_DELIB_SOURCE_TYPES = [
    "lo_review",
    "proposal",
    "owner_conversation",
    "report",
    "session_harvest",
    "bridge_thread",
]

_DELIB_OUTCOMES = ["go", "no_go", "deferred", "owner_decision", "informational"]


def _load_content(content: str | None, content_file: Path | None) -> str:
    """Resolve --content or --content-file into a single string.

    Raises click.UsageError if both or neither are provided.
    """
    if content is not None and content_file is not None:
        raise click.UsageError("Cannot specify both --content and --content-file.")
    if content is None and content_file is None:
        raise click.UsageError("Must provide either --content or --content-file.")
    if content_file is not None:
        return content_file.read_text(encoding="utf-8")
    assert content is not None  # narrow for type checker
    return content


def _parse_participants(raw: str | None) -> list[str] | None:
    """Parse a comma-separated participants list into a trimmed list."""
    if not raw:
        return None
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return parts or None


def _echo_deliberation_row(row: dict[str, Any]) -> None:
    """Render a deliberation row as a human-readable block."""
    click.echo(f"{row['id']} (version {row.get('version', '?')})")
    click.echo(f"  title:       {row.get('title', '')}")
    click.echo(f"  source:      {row.get('source_type', '')}: {row.get('source_ref', '') or '-'}")
    click.echo(f"  summary:     {row.get('summary', '')}")
    if row.get("outcome"):
        click.echo(f"  outcome:     {row['outcome']}")
    if row.get("spec_id"):
        click.echo(f"  spec_id:     {row['spec_id']}")
    if row.get("work_item_id"):
        click.echo(f"  work_item:   {row['work_item_id']}")
    if row.get("session_id"):
        click.echo(f"  session:     {row['session_id']}")
    if row.get("participants"):
        click.echo(f"  participants: {row['participants']}")
    click.echo(f"  changed_by:  {row.get('changed_by', '')}")
    click.echo(f"  reason:      {row.get('change_reason', '')}")
    content = row.get("content", "") or ""
    if content:
        click.echo("  content:")
        for line in content.splitlines():
            click.echo(f"    {line}")


@deliberations.command("add")
@click.option("--id", "deliberation_id", required=True, help="Deliberation ID (e.g. DELIB-0123)")
@click.option("--source-type", type=click.Choice(_DELIB_SOURCE_TYPES), required=True)
@click.option("--source-ref", required=True, help="Source artifact reference (path, URL, bridge file)")
@click.option("--title", required=True, help="Human-readable title")
@click.option("--summary", required=True, help="One- or two-sentence summary")
@click.option("--content", default=None, help="Inline content body")
@click.option(
    "--content-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to a file whose contents become the deliberation body",
)
@click.option("--outcome", type=click.Choice(_DELIB_OUTCOMES), default=None)
@click.option("--spec-id", default=None, help="Link to an existing spec at insert time")
@click.option("--work-item-id", default=None, help="Link to an existing work item at insert time")
@click.option("--session-id", default=None, help="Session identifier (e.g. S290)")
@click.option("--participants", default=None, help="Comma-separated participants list")
@click.option("--changed-by", default="gt-cli", show_default=True)
@click.option("--change-reason", default="Created via gt deliberations add", show_default=True)
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit the inserted row as JSON")
@click.pass_context
def deliberations_add(
    ctx: click.Context,
    deliberation_id: str,
    source_type: str,
    source_ref: str,
    title: str,
    summary: str,
    content: str | None,
    content_file: Path | None,
    outcome: str | None,
    spec_id: str | None,
    work_item_id: str | None,
    session_id: str | None,
    participants: str | None,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Add a new deliberation (append-only; requires --id).

    This is a thin wrapper over ``KnowledgeDB.insert_deliberation`` for cases
    where the caller owns the identifier. For source-content idempotency use
    ``gt deliberations upsert`` instead.
    """
    body = _load_content(content, content_file)
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    row = db.insert_deliberation(
        id=deliberation_id,
        source_type=source_type,
        title=title,
        summary=summary,
        content=body,
        changed_by=changed_by,
        change_reason=change_reason,
        spec_id=spec_id,
        work_item_id=work_item_id,
        source_ref=source_ref,
        participants=_parse_participants(participants),
        outcome=outcome,
        session_id=session_id,
    )
    if row is None:
        raise click.ClickException(f"Unexpected error: inserted deliberation {deliberation_id} not found on readback.")
    if json_output:
        click.echo(json.dumps(row, indent=2, default=str))
        return
    click.echo(f"Added deliberation {row['id']} (version {row.get('version', '?')}).")


@deliberations.command("upsert")
@click.option("--source-type", type=click.Choice(_DELIB_SOURCE_TYPES), required=True)
@click.option("--source-ref", required=True, help="Source artifact reference used for idempotency")
@click.option("--title", required=True, help="Human-readable title")
@click.option("--summary", required=True, help="One- or two-sentence summary")
@click.option("--content", default=None, help="Inline content body")
@click.option(
    "--content-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to a file whose contents become the deliberation body",
)
@click.option("--outcome", type=click.Choice(_DELIB_OUTCOMES), default=None)
@click.option("--spec-id", default=None)
@click.option("--work-item-id", default=None)
@click.option("--session-id", default=None)
@click.option("--participants", default=None, help="Comma-separated participants list")
@click.option("--changed-by", default="gt-cli", show_default=True)
@click.option("--change-reason", default="Upserted via gt deliberations upsert", show_default=True)
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def deliberations_upsert(
    ctx: click.Context,
    source_type: str,
    source_ref: str,
    title: str,
    summary: str,
    content: str | None,
    content_file: Path | None,
    outcome: str | None,
    spec_id: str | None,
    work_item_id: str | None,
    session_id: str | None,
    participants: str | None,
    changed_by: str,
    change_reason: str,
    json_output: bool,
) -> None:
    """Upsert a deliberation keyed by (source_type, source_ref, content_hash).

    The database auto-generates a DELIB-NNNN identifier when no matching
    source/content hash exists. This command has no ``--id`` flag; use
    ``gt deliberations add`` when the caller owns the identifier.
    """
    body = _load_content(content, content_file)
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    row = db.upsert_deliberation_source(
        source_type=source_type,
        source_ref=source_ref,
        content=body,
        title=title,
        summary=summary,
        changed_by=changed_by,
        change_reason=change_reason,
        spec_id=spec_id,
        work_item_id=work_item_id,
        participants=_parse_participants(participants),
        outcome=outcome,
        session_id=session_id,
    )
    if row is None:
        raise click.ClickException("Unexpected error: upserted deliberation not found on readback.")
    if json_output:
        click.echo(json.dumps(row, indent=2, default=str))
        return
    # Per Codex Condition 4: do not infer inserted vs matched from the return
    # row. Print the ID only and let callers inspect via ``gt deliberations get``.
    click.echo(row["id"])


@deliberations.command("record")
@click.option("--source-type", type=click.Choice(_DELIB_SOURCE_TYPES), required=True)
@click.option("--source-ref", required=True, help="Source artifact reference used for idempotency")
@click.option("--title", required=True, help="Human-readable title")
@click.option("--summary", required=True, help="One- or two-sentence summary")
@click.option(
    "--content-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="In-root file whose contents become the deliberation body",
)
@click.option("--change-reason", required=True, help="Reason to store with the deliberation version")
@click.option("--auq-id", required=True, help="AskUserQuestion / AUQ evidence identifier")
@click.option("--auq-answer", required=True, help="Owner answer text or concise answer summary")
@click.option("--owner-presented", is_flag=True, default=False, help="Assert native-format content was shown to owner")
@click.option("--approved-by", default=None, help="Manual approval identity (default: owner)")
@click.option("--spec-id", default=None)
@click.option("--work-item-id", default=None)
@click.option("--session-id", default=None)
@click.option("--participants", default=None, help="Comma-separated participants list")
@click.option("--outcome", type=click.Choice(_DELIB_OUTCOMES), default=None)
@click.option("--dry-run", is_flag=True, default=False, help="Validate and print the proposed packet without writing")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def deliberations_record(
    ctx: click.Context,
    source_type: str,
    source_ref: str,
    title: str,
    summary: str,
    content_file: Path,
    change_reason: str,
    auq_id: str,
    auq_answer: str,
    owner_presented: bool,
    approved_by: str | None,
    spec_id: str | None,
    work_item_id: str | None,
    session_id: str | None,
    participants: str | None,
    outcome: str | None,
    dry_run: bool,
    json_output: bool,
) -> None:
    """Record an AUQ-backed deliberation through the governed service path."""

    config = _resolve_config(ctx)
    request = DeliberationRecordRequest(
        source_type=source_type,
        source_ref=source_ref,
        title=title,
        summary=summary,
        content_file=content_file,
        change_reason=change_reason,
        auq_id=auq_id,
        auq_answer=auq_answer,
        owner_presented=owner_presented,
        approved_by=approved_by,
        spec_id=spec_id,
        work_item_id=work_item_id,
        participants=_parse_participants(participants),
        outcome=outcome,
        session_id=session_id,
        dry_run=dry_run,
    )
    try:
        result = record_deliberation(config, request)
    except DeliberationRecordError as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(result, indent=2, default=str))
        return
    if dry_run:
        click.echo(f"Dry run: would record deliberation {result['id']}.")
        click.echo(f"Approval packet path: {result['approval_packet_path']}")
        click.echo(json.dumps(result["approval_packet"], indent=2, sort_keys=True))
        return
    click.echo(result["id"])


def _show_deliberation(
    ctx: click.Context,
    deliberation_id: str,
    history: bool,
    json_output: bool,
) -> None:
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    try:
        if history:
            rows = db.get_deliberation_history(deliberation_id)
            if not rows:
                click.echo(f"Deliberation {deliberation_id} not found.")
                raise SystemExit(1)
            if json_output:
                click.echo(json.dumps(rows, indent=2, default=str))
                return
            click.echo(f"Version history for {deliberation_id} ({len(rows)} version(s)):")
            for row in rows:
                click.echo(f"--- version {row.get('version', '?')} ---")
                _echo_deliberation_row(row)
            return

        single_row = db.get_deliberation(deliberation_id)
        if single_row is None:
            click.echo(f"Deliberation {deliberation_id} not found.")
            raise SystemExit(1)
        if json_output:
            click.echo(json.dumps(single_row, indent=2, default=str))
            return
        _echo_deliberation_row(single_row)
    finally:
        db.close()


@deliberations.command("get")
@click.argument("deliberation_id")
@click.option("--history", is_flag=True, default=False, help="Show the full version history")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def deliberations_get(ctx: click.Context, deliberation_id: str, history: bool, json_output: bool) -> None:
    """Show a deliberation by ID (latest version by default)."""
    _show_deliberation(ctx, deliberation_id, history, json_output)


@deliberations.command("show")
@click.argument("deliberation_id")
@click.option("--history", is_flag=True, default=False, help="Show the full version history")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def deliberations_show(ctx: click.Context, deliberation_id: str, history: bool, json_output: bool) -> None:
    """Show a deliberation by ID (alias for get)."""
    _show_deliberation(ctx, deliberation_id, history, json_output)


@deliberations.command("list")
@click.option("--spec-id", default=None, help="Filter by linked spec")
@click.option("--work-item-id", default=None, help="Filter by linked work item")
@click.option("--source-type", type=click.Choice(_DELIB_SOURCE_TYPES), default=None)
@click.option("--session-id", default=None)
@click.option("--source-ref", default=None)
@click.option("--outcome", type=click.Choice(_DELIB_OUTCOMES), default=None)
@click.option("--limit", type=int, default=None, help="CLI-side slice; returns the first N rows")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def deliberations_list(
    ctx: click.Context,
    spec_id: str | None,
    work_item_id: str | None,
    source_type: str | None,
    session_id: str | None,
    source_ref: str | None,
    outcome: str | None,
    limit: int | None,
    json_output: bool,
) -> None:
    """List deliberations with optional filters.

    ``--limit`` performs a CLI-side slice; the underlying API returns all
    matching rows.
    """
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    rows = db.list_deliberations(
        spec_id=spec_id,
        work_item_id=work_item_id,
        source_type=source_type,
        session_id=session_id,
        source_ref=source_ref,
        outcome=outcome,
    )
    if limit is not None and limit >= 0:
        rows = rows[:limit]
    if json_output:
        click.echo(json.dumps(rows, indent=2, default=str))
        return
    if not rows:
        click.echo("No deliberations match the given filters.")
        return
    click.echo(f"{len(rows)} deliberation(s):")
    for row in rows:
        outcome_label = f" [{row['outcome']}]" if row.get("outcome") else ""
        click.echo(f"  {row['id']} v{row.get('version', '?')}{outcome_label}: {row.get('title', '')}")
        click.echo(
            f"      source={row.get('source_type', '')}:{row.get('source_ref', '') or '-'}  "
            f"summary={row.get('summary', '')[:80]}"
        )


@deliberations.command("search")
@click.argument("query")
@click.option("--limit", type=int, default=5, show_default=True)
@click.option(
    "--semantic-only",
    is_flag=True,
    default=False,
    help=("Require ChromaDB and reject SQLite LIKE fallback rows. Exits with code 1 if ChromaDB is not installed."),
)
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def deliberations_search(
    ctx: click.Context,
    query: str,
    limit: int,
    semantic_only: bool,
    json_output: bool,
) -> None:
    """Search deliberations by semantic similarity (with SQLite text fallback).

    The default path preserves ``KnowledgeDB.search_deliberations`` behavior:
    ChromaDB is used when available, otherwise SQLite LIKE fallback. Use
    ``--semantic-only`` to opt into a stricter contract that refuses fallback.
    """
    # Per Codex Condition 3: enforce --semantic-only as an explicit
    # no-fallback mode. We check the module-level HAS_CHROMADB flag because the
    # DB method's own contract is to *always* fall back; we filter the CLI
    # layer to match the opt-in promise.
    if semantic_only:
        from groundtruth_kb import db as _db_mod

        if not getattr(_db_mod, "HAS_CHROMADB", False):
            click.echo(
                "Error: --semantic-only requires ChromaDB. Install it into the gt venv with:\n  uv pip install chromadb"
            )
            raise SystemExit(1)

    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    rows = db.search_deliberations(query, limit=limit)

    if semantic_only:
        rows = [r for r in rows if r.get("search_method") == "semantic"]

    if json_output:
        click.echo(json.dumps(rows, indent=2, default=str))
        return

    if not rows:
        method_note = " (semantic-only mode)" if semantic_only else ""
        click.echo(f"No deliberations match '{query}'{method_note}.")
        return

    click.echo(f"{len(rows)} deliberation(s) for '{query}':")
    for row in rows:
        method = row.get("search_method", "?")
        score = row.get("score")
        score_note = f" score={score:.3f}" if isinstance(score, (int, float)) else ""
        click.echo(f"  [{method}{score_note}] {row['id']} v{row.get('version', '?')}: {row.get('title', '')}")
        click.echo(f"      {row.get('summary', '')[:100]}")


@deliberations.command("link")
@click.argument("deliberation_id")
@click.option("--spec", "spec_id", default=None, help="Link to this spec ID")
@click.option("--work-item", "work_item_id", default=None, help="Link to this work item ID")
@click.option("--role", default="related", show_default=True, help="Relationship role")
@click.pass_context
def deliberations_link(
    ctx: click.Context,
    deliberation_id: str,
    spec_id: str | None,
    work_item_id: str | None,
    role: str,
) -> None:
    """Link an existing deliberation to a spec or work item.

    Exactly one of ``--spec`` or ``--work-item`` must be supplied. The CLI
    layer validates that both the deliberation and the target artifact exist
    before writing the link row, because the underlying DB API is permissive.
    """
    if bool(spec_id) == bool(work_item_id):
        raise click.UsageError("Provide exactly one of --spec or --work-item.")

    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)

    # Per Codex Condition 5: CLI-layer validation of all three entities.
    delib = db.get_deliberation(deliberation_id)
    if delib is None:
        click.echo(f"Error: deliberation {deliberation_id} not found.")
        raise SystemExit(1)

    if spec_id is not None:
        if db.get_spec(spec_id) is None:
            click.echo(f"Error: spec {spec_id} not found.")
            raise SystemExit(1)
        db.link_deliberation_spec(deliberation_id, spec_id, role=role)
        click.echo(f"Linked {deliberation_id} to spec {spec_id} (role={role}).")
        return

    assert work_item_id is not None  # mutually exclusive branch
    if db.get_work_item(work_item_id) is None:
        click.echo(f"Error: work item {work_item_id} not found.")
        raise SystemExit(1)
    db.link_deliberation_work_item(deliberation_id, work_item_id, role=role)
    click.echo(f"Linked {deliberation_id} to work item {work_item_id} (role={role}).")


# ── F7: Health dashboard commands ─────────────────────────────────────


@main.group(invoke_without_command=True)
@click.pass_context
def health(ctx: click.Context) -> None:
    """Session health dashboard commands."""
    if ctx.invoked_subcommand is not None:
        return
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    delta = db.compute_session_delta()
    from groundtruth_kb.health import render_health_text

    click.echo(render_health_text(delta.get("current", {})))
    if delta.get("no_prior"):
        click.echo("\n  (No prior snapshot for comparison)")
    elif delta.get("deltas"):
        click.echo("\n  Deltas from last snapshot:")
        for k, v in delta["deltas"].items():
            sign = "+" if v >= 0 else ""
            click.echo(f"    {k}: {sign}{v}")


@health.command("snapshot")
@click.argument("session_id")
@click.pass_context
def health_snapshot(ctx: click.Context, session_id: str) -> None:
    """Capture a health snapshot for a session and display it."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    snap = db.capture_session_snapshot(session_id)
    from groundtruth_kb.health import render_health_text

    click.echo(render_health_text(snap))


@health.command("trends")
@click.option("-n", "--limit", default=5, help="Number of recent snapshots.")
@click.pass_context
def health_trends(ctx: click.Context, limit: int) -> None:
    """Show recent health snapshots with per-snapshot metric deltas."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    history = db.get_snapshot_history(limit=limit)
    if not history:
        click.echo("No health snapshots recorded yet.")
        return
    from groundtruth_kb.health import render_health_text

    click.echo(f"Health trends (latest {len(history)} snapshots, newest first):")
    for snap in history:
        click.echo(f"\n--- {snap['session_id']} ({snap['captured_at']}) ---")
        click.echo(render_health_text(snap.get("data_parsed", {})))

        delta = db.compute_session_delta(current_session=snap["session_id"])
        if delta.get("no_prior"):
            click.echo("  (no prior snapshot to diff against)")
            continue
        deltas = delta.get("deltas") or {}
        if not deltas:
            click.echo("  (no metric changes)")
            continue
        click.echo("  Deltas vs previous snapshot:")
        for key, val in deltas.items():
            sign = "+" if val >= 0 else ""
            click.echo(f"    {key}: {sign}{val}")


# ── F5: Requirement intake commands ────────────────────────────────────


@main.group()
def intake() -> None:
    """Requirement intake pipeline commands."""


@intake.command("classify")
@click.argument("text")
@click.pass_context
def intake_classify(ctx: click.Context, text: str) -> None:
    """Classify owner intent and show related specs."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    from groundtruth_kb.intake import classify_requirement

    result = classify_requirement(db, text)
    click.echo(f"Classification: {result['classification']}")
    click.echo(f"Confidence:     {result['confidence']}")
    if result["related_specs"]:
        click.echo("\nRelated specs:")
        for s in result["related_specs"]:
            click.echo(f"  {s['id']}: {s['title']}")
    else:
        click.echo("\nNo related specs found.")


@intake.command("capture")
@click.argument("text")
@click.option("--title", required=True, help="Proposed spec title")
@click.option("--section", required=True, help="Proposed section")
@click.option("--scope", default=None, help="Proposed scope")
@click.option(
    "--type",
    "spec_type",
    default="requirement",
    help="Spec type (requirement, governance, etc.)",
)
@click.option("--authority", default="stated", help="Spec authority")
@click.pass_context
def intake_capture(
    ctx: click.Context,
    text: str,
    title: str,
    section: str,
    scope: str | None,
    spec_type: str,
    authority: str,
) -> None:
    """Capture a requirement candidate for later review."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    from groundtruth_kb.intake import capture_requirement

    result = capture_requirement(
        db,
        text,
        proposed_title=title,
        proposed_section=section,
        proposed_scope=scope,
        proposed_type=spec_type,
        proposed_authority=authority,
    )
    click.echo(f"Captured: {result['deliberation_id']}")
    click.echo(f"  Classification: {result['content']['classification']}")
    click.echo(f"  Confidence:     {result['content']['confidence']}")


@intake.command("confirm")
@click.argument("deliberation_id")
@click.pass_context
def intake_confirm(ctx: click.Context, deliberation_id: str) -> None:
    """Confirm a captured candidate and create a KB spec."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    from groundtruth_kb.intake import confirm_intake

    result = confirm_intake(db, deliberation_id)
    if "error" in result:
        click.echo(f"Error: {result['error']}")
        raise SystemExit(1)
    if result.get("already_confirmed"):
        click.echo(f"Already confirmed: {result['confirmed_spec_id']}")
        return
    click.echo(f"Confirmed: {result['confirmed_spec_id']}")
    quality = result.get("quality", {})
    if quality:
        click.echo(f"  Quality tier:  {quality.get('tier', 'n/a')}")
        click.echo(f"  Quality score: {quality.get('overall', 'n/a')}")
    impact = result.get("impact", {})
    if impact:
        click.echo(f"  Blast radius:  {impact.get('blast_radius', 'n/a')}")
    constraints = result.get("constraints", [])
    if constraints:
        click.echo(f"  Constraints:   {len(constraints)}")


@intake.command("reject")
@click.argument("deliberation_id")
@click.option("--reason", required=True, help="Rejection reason")
@click.pass_context
def intake_reject(ctx: click.Context, deliberation_id: str, reason: str) -> None:
    """Reject a captured candidate with a reason."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    from groundtruth_kb.intake import reject_intake

    result = reject_intake(db, deliberation_id, reason)
    if "error" in result:
        click.echo(f"Error: {result['error']}")
        raise SystemExit(1)
    click.echo(f"Rejected: {deliberation_id}")


@intake.command("list")
@click.option("--pending", is_flag=True, help="Show only pending intakes")
@click.pass_context
def intake_list(ctx: click.Context, pending: bool) -> None:
    """List intake candidates."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    from groundtruth_kb.intake import list_intakes

    intakes = list_intakes(db, pending_only=pending)
    if not intakes:
        click.echo("No intake candidates found.")
        return
    for i in intakes:
        status = i.get("intake_status", "?")
        click.echo(
            f"{i['deliberation_id']}  [{status}]  {i.get('proposed_title', '')}"
            f"  ({i.get('classification', '?')}, conf={i.get('confidence', 0)})"
        )


# ── F8: Reconciliation (gt kb reconcile) ───────────────────────────────


@main.group()
def kb() -> None:
    """Knowledge base maintenance commands."""


@kb.command("reconcile")
@click.option("--orphans", "run_orphans", is_flag=True, default=False, help="Run orphaned-assertion detector.")
@click.option(
    "--stale",
    "stale_threshold",
    type=int,
    default=None,
    help="Run stale-spec detector with the given N session threshold.",
)
@click.option("--authority", "run_authority", is_flag=True, default=False, help="Run authority-conflict detector.")
@click.option("--duplicates", "run_duplicates", is_flag=True, default=False, help="Run duplicate-spec detector.")
@click.option(
    "--provisionals",
    "run_provisionals",
    is_flag=True,
    default=False,
    help="Run expired-provisional detector.",
)
@click.option("--all", "run_all", is_flag=True, default=False, help="Run every detector.")
@click.option(
    "--project-root",
    "project_root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=None,
    help="Project root for orphaned-assertion file resolution. Defaults to cwd.",
)
@click.pass_context
def kb_reconcile(
    ctx: click.Context,
    run_orphans: bool,
    stale_threshold: int | None,
    run_authority: bool,
    run_duplicates: bool,
    run_provisionals: bool,
    run_all: bool,
    project_root: str | None,
) -> None:
    """Reconcile specs against the current project state.

    Runs one or more provenance/consistency detectors against the KB and
    prints each report. Pass ``--all`` to run every detector in the
    standard order: orphans, stale, authority, duplicates, provisionals.
    """
    from groundtruth_kb import reconciliation

    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)

    # Default-selection semantics:
    #   --all selects every detector (overriding individual flags).
    #   No flags at all is treated as --all for convenience.
    #   Any combination of individual flags runs just those detectors.
    nothing_selected = not any(
        [run_orphans, stale_threshold is not None, run_authority, run_duplicates, run_provisionals]
    )
    if run_all or nothing_selected:
        run_orphans = True
        run_authority = True
        run_duplicates = True
        run_provisionals = True
        if stale_threshold is None:
            stale_threshold = 5

    root = Path(project_root) if project_root else None

    reports = []
    if run_orphans:
        reports.append(reconciliation.find_orphaned_assertions(db, project_root=root))
    if stale_threshold is not None:
        reports.append(reconciliation.find_stale_specs(db, staleness_threshold_sessions=stale_threshold))
    if run_authority:
        reports.append(reconciliation.find_authority_conflicts(db))
    if run_duplicates:
        reports.append(reconciliation.find_duplicate_specs(db))
    if run_provisionals:
        reports.append(reconciliation.find_expired_provisionals(db))

    total_findings = 0
    for report in reports:
        click.echo(f"\n[{report.category}] {len(report.findings)} finding(s)")
        total_findings += len(report.findings)
        for finding in report.findings[:50]:
            spec_id = finding.get("spec_id") or finding.get("spec_a") or "?"
            click.echo(f"  - {spec_id}: {finding}")
        if len(report.findings) > 50:
            click.echo(f"  ... ({len(report.findings) - 50} more)")

    click.echo(f"\nTotal findings across {len(reports)} detector(s): {total_findings}")


# ── F6: Spec scaffold generator ────────────────────────────────────────


@main.group()
def scaffold() -> None:
    """Specification scaffold commands (F6)."""


@scaffold.command("specs")
@click.option(
    "--profile",
    type=click.Choice(["minimal", "full", "azure-enterprise"]),
    default="minimal",
    help=(
        "Scaffold profile: minimal (governance + infra), full (all phases), "
        "or azure-enterprise (13 Azure category specs + ADR template + "
        "verification plan + taxonomy document)."
    ),
)
@click.option(
    "--apply/--dry-run",
    default=False,
    help="Apply scaffold changes to the database (default: dry-run).",
)
@click.pass_context
def scaffold_specs_cmd(ctx: click.Context, profile: str, apply: bool) -> None:
    """Generate a starter set of specs for the current project.

    Default behavior is dry-run: shows what would be generated and the
    per-spec quality scores, without writing to the database. Pass
    ``--apply`` to persist generated specs with ``authority='inferred'``
    so owners can review and promote to ``authority='stated'`` later.

    The ``azure-enterprise`` profile generates a MIXED artifact set: 15
    specs + 1 taxonomy document. Spec counts and document counts are
    reported separately so callers cannot conflate them.
    """
    from groundtruth_kb.spec_scaffold import (
        SpecScaffoldConfig,
    )
    from groundtruth_kb.spec_scaffold import (
        scaffold_specs as run_scaffold_specs,
    )

    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    scaffold_config = SpecScaffoldConfig(profile=profile)
    report = run_scaffold_specs(db, scaffold_config, dry_run=not apply)

    mode = "DRY RUN" if report.dry_run else "APPLIED"
    click.echo(f"Scaffold specs — profile={profile} — {mode}")
    click.echo(f"  generated specs:     {len(report.generated)}")
    click.echo(f"  skipped specs:       {len(report.skipped)}")
    click.echo(f"  generated documents: {len(report.generated_documents)}")
    click.echo(f"  skipped documents:   {len(report.skipped_documents)}")
    click.echo(f"  quality:             {report.quality_summary}")

    if report.skipped:
        click.echo("\nSkipped specs (pre-existing handles):")
        for s in report.skipped:
            click.echo(f"  - {s['id']} (handle={s.get('handle')!r}): {s['reason']}")

    if report.skipped_documents:
        click.echo("\nSkipped documents (already exist):")
        for d in report.skipped_documents:
            click.echo(f"  - {d['id']}: {d['reason']}")

    if report.low_quality_warnings:
        click.echo("\nLow quality warnings:")
        for w in report.low_quality_warnings:
            click.echo(f"  - {w['id']}: tier={w['tier']} score={w.get('score')}")

    if report.generated:
        click.echo("\nGenerated specs:")
        for spec in report.generated:
            tier = spec.get("quality", {}).get("tier", "?")
            click.echo(f"  - {spec['id']}: {spec['title']}  [{tier}]")

    if report.generated_documents:
        click.echo("\nGenerated documents:")
        for doc in report.generated_documents:
            cat = doc.get("category", "?")
            click.echo(f"  - {doc['id']}: {doc.get('title', '?')}  [category={cat}]")


# ---------------------------------------------------------------------------
# D2: gt scaffold adrs --profile azure-enterprise
# ---------------------------------------------------------------------------


@scaffold.command("adrs")
@click.option(
    "--profile",
    type=click.Choice(["azure-enterprise"]),
    default="azure-enterprise",
    help=(
        "ADR scaffold profile. Currently only 'azure-enterprise' is supported "
        "(13 instance-ADR skeletons per Azure readiness category)."
    ),
)
@click.option(
    "--apply/--dry-run",
    default=False,
    help="Apply scaffold changes to the database (default: dry-run).",
)
@click.pass_context
def scaffold_adrs_cmd(ctx: click.Context, profile: str, apply: bool) -> None:
    """Generate instance-ADR skeletons for the given profile (D2).

    For ``azure-enterprise``, generates 13 ADR skeletons (one per taxonomy
    category) with the 9-section template body and
    ``<<ADOPTER-ANSWER-REQUIRED>>`` placeholders in the sections that require
    owner input (Decision, Rationale, Rejected alternatives).

    After scaffolding, the adopter-owner edits each ADR's description to
    replace the placeholders with their actual answers, then optionally
    promotes status via ``db.update_spec()``. Use ``gt check adrs
    --profile azure-enterprise`` to verify all 13 are answered.
    """
    from groundtruth_kb.adr_scaffold import (
        AdrScaffoldConfig,
    )
    from groundtruth_kb.adr_scaffold import (
        scaffold_adrs as run_scaffold_adrs,
    )

    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    adr_config = AdrScaffoldConfig(profile=profile)
    report = run_scaffold_adrs(db, adr_config, dry_run=not apply)

    mode = "DRY RUN" if report.dry_run else "APPLIED"
    click.echo(f"Scaffold adrs — profile={profile} — {mode}")
    click.echo(f"  generated ADRs: {len(report.generated)}")
    click.echo(f"  skipped ADRs:   {len(report.skipped)}")

    if report.skipped:
        click.echo("\nSkipped (pre-existing handles):")
        for s in report.skipped:
            click.echo(f"  - {s['id']} (handle={s.get('handle')!r}): {s['reason']}")

    if report.generated:
        click.echo("\nGenerated ADRs:")
        for adr in report.generated:
            click.echo(f"  - {adr['id']}: {adr['title']}")


# ---------------------------------------------------------------------------
# D3: gt scaffold iac --profile azure-enterprise
# ---------------------------------------------------------------------------


@scaffold.command("iac")
@click.option(
    "--profile",
    type=click.Choice(["azure-enterprise"]),
    default="azure-enterprise",
    help=(
        "IaC scaffold profile. Currently only 'azure-enterprise' is supported "
        "(45 Terraform skeleton files: 6 top-level + 13 modules x 3 files)."
    ),
)
@click.option(
    "--apply/--dry-run",
    default=False,
    help="Apply scaffold changes to the filesystem (default: dry-run).",
)
@click.option(
    "--target-dir",
    type=click.Path(path_type=Path),
    default=".",
    help="Target directory where the iac/azure/ tree is written (default: current directory).",
)
def scaffold_iac_cmd(profile: str, apply: bool, target_dir: Path) -> None:
    """Generate Terraform skeleton files for the given profile (D3).

    For ``azure-enterprise``, generates 45 Terraform files under ``iac/azure/``:

    - 6 top-level: main.tf, variables.tf, outputs.tf, providers.tf,
      README.md, terraform.tfvars.example
    - 13 modules (one per Azure readiness taxonomy category), each with
      main.tf / variables.tf / outputs.tf = 39 files.

    **Scaffold is one-shot and adopter-owned.** Existing files are skipped
    (never overwritten). If you want to reset a file to skeleton state,
    delete it first and re-run scaffold.

    Pair each module with the matching ADR-Azure-* instance from D2
    (``gt scaffold adrs``): each skeleton references its ADR handle in a
    TODO marker.
    """
    from groundtruth_kb.iac_scaffold import (
        IacScaffoldConfig,
        scaffold_azure_iac,
    )

    iac_config = IacScaffoldConfig(profile=profile, target_dir=target_dir)
    report = scaffold_azure_iac(iac_config, dry_run=not apply)

    mode = "DRY RUN" if report.dry_run else "APPLIED"
    click.echo(f"Scaffold iac — profile={profile} — target={target_dir} — {mode}")
    click.echo(f"  generated files: {len(report.generated)}")
    click.echo(f"  skipped files:   {len(report.skipped)}")

    if report.skipped:
        click.echo("\nSkipped (already exist; adopter-owned):")
        for s in report.skipped:
            click.echo(f"  - {s['target_path']}: {s['reason']}")

    if report.generated:
        click.echo("\nGenerated files:")
        for g in report.generated:
            click.echo(f"  - {g['target_path']}")


# ---------------------------------------------------------------------------
# D4: gt scaffold cicd --profile azure-enterprise
# ---------------------------------------------------------------------------


@scaffold.command("cicd")
@click.option(
    "--profile",
    type=click.Choice(["azure-enterprise"]),
    default="azure-enterprise",
    help=(
        "CI/CD scaffold profile. Currently only 'azure-enterprise' is supported "
        "(12 GitHub Actions CI/CD skeleton files: 2 composite actions + 4 workflow "
        "YAML + 1 workflow README + 5 adopter docs)."
    ),
)
@click.option(
    "--apply/--dry-run",
    default=False,
    help="Apply scaffold changes to the filesystem (default: dry-run).",
)
@click.option(
    "--target-dir",
    type=click.Path(path_type=Path),
    default=".",
    help="Target directory where the .github/ and docs/azure/ trees are written (default: current directory).",
)
def scaffold_cicd_cmd(profile: str, apply: bool, target_dir: Path) -> None:
    """Generate GitHub Actions CI/CD skeleton files for the given profile (D4).

    For ``azure-enterprise``, generates 12 files under ``.github/`` and
    ``docs/azure/``:

    - 2 composite actions: ``azure-oidc-login``, ``deploy-evidence``.
    - 4 workflows: ``iac-validate``, ``iac-apply-staging``,
      ``iac-apply-production``, ``drift-detection``.
    - 1 workflow README.
    - 5 adopter docs under ``docs/azure/``.

    **Scaffold is one-shot and adopter-owned.** Existing files are skipped
    (never overwritten). If you want to reset a file to skeleton state,
    delete it first and re-run scaffold.

    Pair with the D3 IaC scaffold (``gt scaffold iac``). The workflows
    default ``TF_WORKING_DIR`` to ``iac/azure``, which matches the D3
    tree; override via a GitHub Environment variable if your layout
    differs.
    """
    from groundtruth_kb.cicd_scaffold import (
        CicdScaffoldConfig,
        scaffold_azure_cicd,
    )

    cicd_config = CicdScaffoldConfig(profile=profile, target_dir=target_dir)
    report = scaffold_azure_cicd(cicd_config, dry_run=not apply)

    mode = "DRY RUN" if report.dry_run else "APPLIED"
    click.echo(f"Scaffold cicd — profile={profile} — target={target_dir} — {mode}")
    click.echo(f"  generated files: {len(report.generated)}")
    click.echo(f"  skipped files:   {len(report.skipped)}")

    if report.skipped:
        click.echo("\nSkipped (already exist; adopter-owned):")
        for s in report.skipped:
            click.echo(f"  - {s['target_path']}: {s['reason']}")

    if report.generated:
        click.echo("\nGenerated files:")
        for g in report.generated:
            click.echo(f"  - {g['target_path']}")


# ---------------------------------------------------------------------------
# D2: gt check adrs --profile azure-enterprise
# ---------------------------------------------------------------------------


@main.group()
def check() -> None:
    """Verification commands (D2+)."""


@check.command("adrs")
@click.option(
    "--profile",
    type=click.Choice(["azure-enterprise"]),
    default="azure-enterprise",
    help="ADR verification profile.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Emit machine-readable JSON output suitable for CI consumption.",
)
@click.pass_context
def check_adrs_cmd(ctx: click.Context, profile: str, json_output: bool) -> None:
    """Verify all 13 instance ADRs have been answered by the adopter-owner.

    Exit code 0 only when all 13 ADRs are answered (non-empty, non-placeholder
    Decision + Rationale + Rejected alternatives sections, plus all 9
    template headings present). Exit non-zero if any are missing or
    unanswered.
    """
    import json as _json

    from groundtruth_kb.adr_harness import verify_azure_adrs

    if profile != "azure-enterprise":  # pragma: no cover — only one profile today
        raise click.UsageError(f"Unsupported profile: {profile!r}")

    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path)
    report = verify_azure_adrs(db)

    if json_output:
        payload = {
            "total": report.total,
            "answered_count": report.answered_count,
            "unanswered_count": report.unanswered_count,
            "missing_count": report.missing_count,
            "entries": [
                {
                    "adr_id": e.adr_id,
                    "status": e.status,
                    "missing_headings": list(e.missing_headings),
                    "unanswered_sections": list(e.unanswered_sections),
                    "spec_status": e.spec_status,
                }
                for e in report.entries
            ],
        }
        click.echo(_json.dumps(payload, indent=2))
    else:
        click.echo(f"Azure ADR verification — profile={profile}")
        click.echo(f"  total:              {report.total}")
        click.echo(f"  answered:           {report.answered_count}")
        click.echo(f"  unanswered:         {report.unanswered_count}")
        click.echo(f"  missing:            {report.missing_count}")
        click.echo("")
        for entry in report.entries:
            click.echo(f"  [{entry.status:<10}] {entry.adr_id}")
            if entry.missing_headings:
                click.echo(f"    missing headings: {', '.join(entry.missing_headings)}")
            if entry.unanswered_sections:
                click.echo(f"    unanswered sections: {', '.join(entry.unanswered_sections)}")

    ctx.exit(0 if report.all_answered() else 1)


# ---------------------------------------------------------------------------
# `gt mode` subcommands (Operating-Mode Transaction Component, Slice 1)
# Per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 and bridge thread
# gtkb-operating-mode-transaction-001 (Codex GO@017 on REVISED-7 at -016).
# ---------------------------------------------------------------------------


@main.group("mode")
def mode_group() -> None:
    """Operating-mode transaction component (Slice 1)."""


@mode_group.command("set-role")
@click.option("--harness", "harness", required=True, help="Harness id or name")
@click.option(
    "--role",
    "role",
    required=True,
    type=click.Choice(["prime-builder", "loyal-opposition"]),
    help="Role to assign",
)
@click.option("--reason", "reason", default="manual role-switch via gt mode set-role")
@click.option(
    "--defer-to-next-session",
    "defer",
    is_flag=True,
    help="Queue for SessionStart application instead of mid-session apply",
)
@click.pass_context
def mode_set_role(ctx: click.Context, harness: str, role: str, reason: str, defer: bool) -> None:
    """Apply (or defer) a role-switch transaction."""
    import json as _json
    from pathlib import Path

    from groundtruth_kb.mode_switch.pending import defer_role_switch
    from groundtruth_kb.mode_switch.transaction import (
        TransactionValidationError,
        apply_role_switch,
    )

    config = _resolve_config(ctx)
    root = Path(config.project_root)
    if defer:
        path = defer_role_switch(root, harness, role, change_reason=reason)
        click.echo(_json.dumps({"deferred": True, "pending_path": str(path)}, indent=2))
        return
    try:
        result = apply_role_switch(root, harness, role, change_reason=reason)
    except TransactionValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(
        _json.dumps(
            {
                "applied": True,
                "harness_id": result.harness_id,
                "new_role_set": list(result.new_role_set),
                "previous_role_set": list(result.previous_role_set),
                "derived_topology": result.derived_topology,
                "audit_record_path": str(result.audit_record_path),
                "applied_at": result.applied_at.isoformat().replace("+00:00", "Z"),
            },
            indent=2,
        )
    )


@mode_group.command("set-bridge-substrate")
@click.option(
    "--substrate",
    "substrate",
    required=True,
    type=click.Choice(["cross_harness_trigger", "single_harness_dispatcher", "none"]),
    help="Bridge dispatch substrate to assign",
)
@click.option("--reason", "reason", default="manual substrate-switch via gt mode set-bridge-substrate")
@click.option(
    "--defer-to-next-session",
    "defer",
    is_flag=True,
    help="Queue for SessionStart application instead of mid-session apply",
)
@click.pass_context
def mode_set_bridge_substrate(ctx: click.Context, substrate: str, reason: str, defer: bool) -> None:
    """Apply (or defer) a bridge-substrate transaction."""
    import json as _json
    from pathlib import Path

    from groundtruth_kb.mode_switch.bridge_substrate import (
        apply_bridge_substrate_switch,
        defer_bridge_substrate_switch,
    )
    from groundtruth_kb.mode_switch.transaction import TransactionValidationError

    config = _resolve_config(ctx)
    root = Path(config.project_root)
    if defer:
        path = defer_bridge_substrate_switch(root, substrate, change_reason=reason)
        click.echo(_json.dumps({"deferred": True, "pending_path": str(path)}, indent=2))
        return
    try:
        audit_path = apply_bridge_substrate_switch(root, substrate, change_reason=reason)
    except TransactionValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(
        _json.dumps(
            {
                "applied": True,
                "substrate": substrate,
                "audit_record_path": str(audit_path),
            },
            indent=2,
        )
    )


@mode_group.command("list-pending")
@click.pass_context
def mode_list_pending(ctx: click.Context) -> None:
    """List pending mode-switch transactions."""
    import json as _json
    from pathlib import Path

    from groundtruth_kb.mode_switch.pending import list_pending

    config = _resolve_config(ctx)
    root = Path(config.project_root)
    pending = list_pending(root)
    payload = [
        {
            "path": str(entry.path),
            "axis": entry.axis,
            "harness_id_or_name": entry.harness_id_or_name,
            "role": entry.role,
            "substrate": entry.substrate,
            "change_reason": entry.change_reason,
            "scheduled_at": entry.scheduled_at.isoformat().replace("+00:00", "Z"),
        }
        for entry in pending
    ]
    click.echo(_json.dumps(payload, indent=2))


@mode_group.command("apply-pending")
@click.pass_context
def mode_apply_pending(ctx: click.Context) -> None:
    """Drain the pending queue."""
    import json as _json
    from pathlib import Path

    from groundtruth_kb.mode_switch.pending import apply_pending

    config = _resolve_config(ctx)
    root = Path(config.project_root)
    results = apply_pending(root)
    payload = [
        {
            "pending_path": str(r.pending_path),
            "applied": r.applied,
            "error": r.error,
            "applied_path": str(r.applied_path) if r.applied_path else None,
        }
        for r in results
    ]
    click.echo(_json.dumps(payload, indent=2))


# ---------------------------------------------------------------------------
# gt harness — harness registry command group (REQ-HARNESS-REGISTRY-001 FR3)
# ---------------------------------------------------------------------------

_HARNESS_CLI_ACTOR = "gt-harness-cli"


@main.group("harness")
def harness_group() -> None:
    """Harness registry: registration, lifecycle, role, and precedence (FR3).

    WI-4327 Phase-1 Foundation also exposes the 3 canonical reader subcommands
    `roles`, `identity`, and `capabilities` under this same group. They
    delegate to `groundtruth_kb.harness_projection.{read_roles, read_identity,
    read_capabilities}` per DCL-HARNESS-STATE-SOT-READER-CONTRACT-001.
    """


@harness_group.command("roles")
@click.pass_context
def harness_roles_cmd(ctx: click.Context) -> None:
    """Print the harness-state ``harness-registry.json`` content (WI-4327)."""
    from groundtruth_kb.harness_projection import HarnessStateError, read_roles  # noqa: PLC0415

    config = _resolve_config(ctx)
    try:
        data = read_roles(project_root=Path(config.project_root))
    except HarnessStateError as exc:
        click.echo(json.dumps({"status": "error", "message": str(exc)}, indent=2, sort_keys=True))
        raise SystemExit(1) from exc
    click.echo(json.dumps(data, indent=2, sort_keys=True))


@harness_group.command("identity")
@click.pass_context
def harness_identity_cmd(ctx: click.Context) -> None:
    """Print the harness-state ``harness-identities.json`` content (WI-4327)."""
    from groundtruth_kb.harness_projection import HarnessStateError, read_identity  # noqa: PLC0415

    config = _resolve_config(ctx)
    try:
        data = read_identity(project_root=Path(config.project_root))
    except HarnessStateError as exc:
        click.echo(json.dumps({"status": "error", "message": str(exc)}, indent=2, sort_keys=True))
        raise SystemExit(1) from exc
    click.echo(json.dumps(data, indent=2, sort_keys=True))


@harness_group.command("capabilities")
@click.pass_context
def harness_capabilities_cmd(ctx: click.Context) -> None:
    """Print the harness-state ``harness-capability-registry.toml`` as JSON (WI-4327)."""
    from groundtruth_kb.harness_projection import HarnessStateError, read_capabilities  # noqa: PLC0415

    config = _resolve_config(ctx)
    try:
        data = read_capabilities(project_root=Path(config.project_root))
    except HarnessStateError as exc:
        click.echo(json.dumps({"status": "error", "message": str(exc)}, indent=2, sort_keys=True))
        raise SystemExit(1) from exc
    click.echo(json.dumps(data, indent=2, sort_keys=True))


def _harness_emit(record: object) -> None:
    """Echo a harness record (or list of records) as indented, key-sorted JSON."""
    import json as _json

    click.echo(_json.dumps(record, indent=2, sort_keys=True, default=str))


def _run_harness_transition(
    ctx: click.Context,
    harness_id: str,
    target_status: str,
    expected_source: str | None,
    reason: str,
) -> None:
    """Apply a lifecycle transition, refresh the FR5 projection, and echo the record."""
    from groundtruth_kb import harness_ops
    from groundtruth_kb.harness_projection import generate_harness_projection

    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        record = harness_ops.transition_harness(
            db,
            harness_id,
            target_status,
            changed_by=_HARNESS_CLI_ACTOR,
            change_reason=reason,
            expected_source=expected_source,
        )
    except harness_ops.HarnessOperationError as exc:
        raise click.ClickException(str(exc)) from exc
    generate_harness_projection(db, config.project_root)
    _harness_emit(record)


@harness_group.command("register")
@click.option("--id", "harness_id", required=True, help="Durable harness id (e.g. A, B, C)")
@click.option("--name", "harness_name", required=True, help="Harness name")
@click.option("--type", "harness_type", required=True, help="Harness type (e.g. claude-code, codex-cli)")
@click.option(
    "--role",
    "roles",
    multiple=True,
    hidden=True,
    help="Deprecated; registration is separate from role assignment",
)
@click.option("--precedence", "precedence", type=int, default=None, help="Reviewer precedence (integer)")
@click.option("--capabilities-ref", "capabilities_ref", default=None, help="Capabilities registry reference")
@click.option(
    "--invocation-surfaces",
    "invocation_surfaces_json",
    default=None,
    help="Invocation surfaces as a JSON object string",
)
@click.option("--reason", "reason", default="register harness via gt harness register", help="Change reason")
@click.pass_context
def harness_register(
    ctx: click.Context,
    harness_id: str,
    harness_name: str,
    harness_type: str,
    roles: tuple[str, ...],
    precedence: int | None,
    capabilities_ref: str | None,
    invocation_surfaces_json: str | None,
    reason: str,
) -> None:
    """Register a new harness at status 'registered'."""
    import json as _json

    from groundtruth_kb import harness_ops
    from groundtruth_kb.harness_projection import generate_harness_projection

    surfaces: dict[str, object] | None = None
    if invocation_surfaces_json is not None:
        try:
            parsed = _json.loads(invocation_surfaces_json)
        except _json.JSONDecodeError as exc:
            raise click.ClickException(f"--invocation-surfaces is not valid JSON: {exc}") from exc
        if not isinstance(parsed, dict):
            raise click.ClickException("--invocation-surfaces must be a JSON object")
        surfaces = parsed
    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        record = harness_ops.register_harness(
            db,
            id=harness_id,
            harness_name=harness_name,
            harness_type=harness_type,
            role=list(roles),
            reviewer_precedence=precedence,
            invocation_surfaces=surfaces,
            capabilities_ref=capabilities_ref,
            changed_by=_HARNESS_CLI_ACTOR,
            change_reason=reason,
        )
    except harness_ops.HarnessOperationError as exc:
        raise click.ClickException(str(exc)) from exc
    generate_harness_projection(db, config.project_root)
    _harness_emit(record)


@harness_group.command("activate")
@click.option("--harness", "harness_id", required=True, help="Harness id")
@click.option("--reason", "reason", default="activate harness via gt harness activate", help="Change reason")
@click.pass_context
def harness_activate(ctx: click.Context, harness_id: str, reason: str) -> None:
    """Activate a registered or suspended harness."""
    _run_harness_transition(ctx, harness_id, "active", None, reason)


@harness_group.command("suspend")
@click.option("--harness", "harness_id", required=True, help="Harness id")
@click.option("--reason", "reason", default="suspend harness via gt harness suspend", help="Change reason")
@click.option(
    "--cause",
    "cause",
    type=click.Choice(["owner-declared", "non-operating-detected"]),
    default="owner-declared",
    show_default=True,
    help="Suspension cause",
)
@click.pass_context
def harness_suspend(ctx: click.Context, harness_id: str, reason: str, cause: str) -> None:
    """Suspend an active harness (active -> suspended)."""
    _run_harness_transition(ctx, harness_id, "suspended", "active", f"{reason} [cause={cause}]")


@harness_group.command("resume")
@click.option("--harness", "harness_id", required=True, help="Harness id")
@click.option("--reason", "reason", default="resume harness via gt harness resume", help="Change reason")
@click.pass_context
def harness_resume(ctx: click.Context, harness_id: str, reason: str) -> None:
    """Resume a suspended harness (suspended -> active)."""
    _run_harness_transition(ctx, harness_id, "active", "suspended", reason)


@harness_group.command("retire")
@click.option("--harness", "harness_id", required=True, help="Harness id")
@click.option("--reason", "reason", default="retire harness via gt harness retire", help="Change reason")
@click.pass_context
def harness_retire(ctx: click.Context, harness_id: str, reason: str) -> None:
    """Retire a harness. A suspended harness retires directly; an active harness auto-suspends first."""
    _run_harness_transition(ctx, harness_id, "retired", None, reason)


@harness_group.command("set-precedence")
@click.option("--harness", "harness_id", required=True, help="Harness id")
@click.option("--precedence", "precedence", type=int, required=True, help="Reviewer precedence (integer)")
@click.option(
    "--reason",
    "reason",
    default="set reviewer precedence via gt harness set-precedence",
    help="Change reason",
)
@click.pass_context
def harness_set_precedence(ctx: click.Context, harness_id: str, precedence: int, reason: str) -> None:
    """Set a harness's reviewer precedence."""
    from groundtruth_kb import harness_ops
    from groundtruth_kb.harness_projection import generate_harness_projection

    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        record = harness_ops.set_harness_precedence(
            db,
            harness_id,
            precedence,
            changed_by=_HARNESS_CLI_ACTOR,
            change_reason=reason,
        )
    except harness_ops.HarnessOperationError as exc:
        raise click.ClickException(str(exc)) from exc
    generate_harness_projection(db, config.project_root)
    _harness_emit(record)


@harness_group.command("set-role")
@click.option(
    "--harness",
    "harness_id",
    required=True,
    help="Durable harness id receiving default role metadata",
)
@click.option(
    "--role",
    "role",
    required=True,
    type=click.Choice(["prime-builder", "loyal-opposition"]),
    help="Default operating role metadata to assign",
)
@click.option(
    "--reason",
    "reason",
    default="assign operating role via gt harness set-role",
    help="Change reason",
)
@click.pass_context
def harness_set_role(ctx: click.Context, harness_id: str, role: str, reason: str) -> None:
    """Assign one default operating-role metadata value to one harness.

    REQ-HARNESS-REGISTRY-001 FR9. The target must be a known, non-retired
    harness in the registry. The candidate role map must leave at least one
    active Prime Builder and at least one active Loyal Opposition; no active
    harness may hold both roles when more than one active harness exists.
    """
    import json as _json
    from pathlib import Path

    from groundtruth_kb.mode_switch.invariants import (
        RolePartitionViolation,
        verify_active_role_partition,
    )
    from groundtruth_kb.mode_switch.transaction import (
        TransactionValidationError,
        apply_role_switch,
    )

    config = _resolve_config(ctx)
    db = _open_db(config)
    record = db.get_harness(harness_id)
    if record is None:
        raise click.ClickException(f"unknown harness {harness_id!r}; no such harness in the registry")
    status = record.get("status")
    if status == "retired":
        raise click.ClickException(
            f"harness {harness_id!r} has status {status!r}; gt harness set-role "
            "cannot update retired harness role metadata"
        )
    root = Path(config.project_root)
    try:
        result = apply_role_switch(root, harness_id, role, change_reason=reason)
    except TransactionValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    try:
        summary = verify_active_role_partition(root)
    except RolePartitionViolation as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(
        _json.dumps(
            {
                "harness_id": result.harness_id,
                "new_role_set": list(result.new_role_set),
                "previous_role_set": list(result.previous_role_set),
                "derived_topology": result.derived_topology,
                "audit_record_path": str(result.audit_record_path),
                "verified_prime_builder": summary.prime_builder_id,
                "verified_prime_builders": list(summary.prime_builder_ids),
                "verified_loyal_opposition": summary.loyal_opposition_id,
                "verified_loyal_oppositions": list(summary.loyal_opposition_ids),
                "verified_active_harnesses": list(summary.active_harness_ids),
            },
            indent=2,
            sort_keys=True,
        )
    )


@harness_group.command("list")
@click.pass_context
def harness_list(ctx: click.Context) -> None:
    """List all harness registry records (current versions)."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    _harness_emit(db.list_harnesses())


@harness_group.command("show")
@click.option("--harness", "harness_id", required=True, help="Harness id")
@click.pass_context
def harness_show(ctx: click.Context, harness_id: str) -> None:
    """Show one harness registry record (current version)."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    record = db.get_harness(harness_id)
    if record is None:
        raise click.ClickException(f"unknown harness {harness_id!r}; no such harness in the registry")
    _harness_emit(record)


if __name__ == "__main__":
    main()
