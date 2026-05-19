"""
GroundTruth KB — CLI (``gt`` command).

Provides project initialization, assertion running, seed data loading,
database inspection, and import/export commands.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

import click

from groundtruth_kb import __version__
from groundtruth_kb._logging import configure_cli_logging
from groundtruth_kb.bootstrap import (
    DesktopBootstrapOptions,
    bootstrap_desktop_project,
    bootstrap_summary,
)
from groundtruth_kb.cli_deliberations_record import (
    DeliberationRecordError,
    DeliberationRecordRequest,
    record_deliberation,
)
from groundtruth_kb.cli_spec_record import SPEC_RECORD_TYPES, SpecRecordError, SpecRecordRequest, record_spec
from groundtruth_kb.cli_spec_update import SpecUpdateError, SpecUpdateRequest, update_spec
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.db_snapshot import SnapshotError, create_snapshot
from groundtruth_kb.gates import GateRegistry
from groundtruth_kb.project.lifecycle import (
    PROJECTS_CHANGED_BY,
    ProjectAuthorizationSpecLinkageError,
    ProjectLifecycleError,
    ProjectLifecycleService,
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


@click.group()
@click.version_option(version=__version__, prog_name="gt")
@click.option("--config", "config_path", type=click.Path(exists=True), default=None, help="Path to groundtruth.toml")
@click.pass_context
def main(ctx: click.Context, config_path: str | None) -> None:
    """GroundTruth KB — specification-driven governance toolkit."""
    configure_cli_logging()
    ctx.ensure_object(dict)
    ctx.obj["config"] = Path(config_path) if config_path else None


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


@backlog.command("migrate-work-list")
@click.option(
    "--work-list",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Legacy memory/work_list.md path. Defaults to <project_root>/memory/work_list.md.",
)
@click.option("--dry-run", is_flag=True, help="Parse and report rows without inserting MemBase records.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--changed-by", default="gt-backlog-migration", show_default=True, help="History author for inserts.")
@click.option(
    "--change-reason",
    default="Migrate legacy markdown work_list rows into unified MemBase work_items backlog.",
    show_default=True,
    help="History reason for inserts.",
)
@click.pass_context
def backlog_migrate_work_list(
    ctx: click.Context,
    work_list: Path | None,
    dry_run: bool,
    json_output: bool,
    changed_by: str,
    change_reason: str,
) -> None:
    """Migrate legacy markdown work-list rows into the unified backlog."""
    from groundtruth_kb.backlog import migrate_work_list_items, parse_work_list_file

    config = _resolve_config(ctx)
    work_list_path = work_list or config.project_root / "memory" / "work_list.md"
    if not work_list_path.exists():
        raise click.ClickException(f"Work-list file not found: {work_list_path}")

    db = _open_db(config)
    try:
        items = parse_work_list_file(work_list_path)
        result = migrate_work_list_items(
            db,
            items,
            changed_by=changed_by,
            change_reason=change_reason,
            dry_run=dry_run,
        )
    finally:
        db.close()

    if json_output:
        click.echo(json.dumps(result.to_json_dict(), indent=2, sort_keys=True))
        return
    action = "would insert" if dry_run else "inserted"
    update_action = "would enrich" if dry_run else "enriched"
    click.echo(
        "Backlog work-list migration: "
        f"parsed {result.parsed}, {action} {len(result.inserted)}, "
        f"{update_action} {len(result.updated_existing)}, "
        f"skipped existing {len(result.skipped_existing)}."
    )
    if result.inserted:
        click.echo("Inserted:")
        for item_id in result.inserted:
            click.echo(f"  - {item_id}")
    if result.updated_existing:
        click.echo("Enriched existing:")
        for item_id in result.updated_existing:
            click.echo(f"  - {item_id}")
    if result.skipped_existing:
        click.echo("Skipped existing:")
        for item_id in result.skipped_existing:
            click.echo(f"  - {item_id}")


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
    it never mutates memory/MEMORY.md or memory/work_list.md.
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


@backlog.command("list")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--all", "include_verified", is_flag=True, help="Include verified/closed work items.")
@click.pass_context
def backlog_list(ctx: click.Context, json_output: bool, include_verified: bool) -> None:
    """List unified backlog items from MemBase work_items."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        items = db.list_work_items() if include_verified else db.get_open_work_items()
    finally:
        db.close()

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
@click.pass_context
def projects_list(ctx: click.Context, json_output: bool, include_terminal: bool) -> None:
    """List first-class project records."""
    db, service = _project_service(ctx)
    try:
        projects = service.list_projects(include_terminal=include_terminal)
    finally:
        db.close()

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
    """Link a project to a bridge thread artifact without editing bridge/INDEX.md."""
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
def project_doctor(auto_install: bool, profile: str | None, target_dir: str) -> None:
    """Check workstation readiness and optionally install missing tools."""
    from groundtruth_kb.project.doctor import format_doctor_report, run_doctor

    target = Path(target_dir).resolve()

    # Auto-detect profile from manifest
    if profile is None:
        from groundtruth_kb.project.manifest import read_manifest

        manifest = read_manifest(target / "groundtruth.toml")
        profile = manifest.profile if manifest else "local-only"

    report = run_doctor(target, profile, auto_install=auto_install)
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
hooks-point-to-wrappers, work-list-no-product-entries, chroma-regeneratable)
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
        click.echo('Error: ChromaDB is not installed. Install with:\n  pip install "groundtruth-kb[search]"')
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


@deliberations.command("get")
@click.argument("deliberation_id")
@click.option("--history", is_flag=True, default=False, help="Show the full version history")
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def deliberations_get(
    ctx: click.Context,
    deliberation_id: str,
    history: bool,
    json_output: bool,
) -> None:
    """Show a deliberation by ID (latest version by default)."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
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
                'Error: --semantic-only requires ChromaDB. Install with:\n  pip install "groundtruth-kb[search]"'
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
            "harness_id_or_name": entry.harness_id_or_name,
            "role": entry.role,
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
    """Harness registry: registration, lifecycle, role, and precedence (FR3)."""


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
    help="Durable active harness id receiving the role",
)
@click.option(
    "--role",
    "role",
    required=True,
    type=click.Choice(["prime-builder", "loyal-opposition"]),
    help="Operating role to assign to the active harness",
)
@click.option(
    "--reason",
    "reason",
    default="assign operating role via gt harness set-role",
    help="Change reason",
)
@click.pass_context
def harness_set_role(ctx: click.Context, harness_id: str, role: str, reason: str) -> None:
    """Assign one operating role to one registered and active harness.

    REQ-HARNESS-REGISTRY-001 FR9. The target must be an 'active' harness in the
    registry. The resulting role map has exactly one active Prime Builder and
    exactly one active Loyal Opposition; they are distinct when more than one
    active harness exists.
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
    # FR9 active-harness eligibility gate: the target must be an active harness
    # in the DB-backed registry (seeded by WI-3342 Slice A).
    record = db.get_harness(harness_id)
    if record is None:
        raise click.ClickException(f"unknown harness {harness_id!r}; no such harness in the registry")
    status = record.get("status")
    if status != "active":
        raise click.ClickException(
            f"harness {harness_id!r} has status {status!r}; gt harness set-role "
            f"can assign only an active harness - use 'gt harness activate' to "
            f"bring it active first"
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
                "verified_loyal_opposition": summary.loyal_opposition_id,
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
