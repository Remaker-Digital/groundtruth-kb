"""
GroundTruth KB — CLI (``gt`` command).

Provides project initialization, assertion running, seed data loading,
database inspection, and import/export commands.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from groundtruth_kb import __version__
from groundtruth_kb.bootstrap import (
    DesktopBootstrapOptions,
    bootstrap_desktop_project,
    bootstrap_summary,
)
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.gates import GateRegistry

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
        click.echo(f"  Documents:          {s['document_count']}")
        a_pass, a_fail = s["assertions_passed"], s["assertions_failed"]
        click.echo(f"  Assertions run:     {s['assertions_total']} ({a_pass} passed, {a_fail} failed)")
        click.echo(f"{'=' * 50}\n")
    finally:
        db.close()


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
        "backlog_snapshots",
        "testable_elements",
        "quality_scores",
        "spec_quality_scores",
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

                cols = list(row.keys())
                placeholders = ", ".join(["?"] * len(cols))
                col_names = ", ".join(cols)

                try:
                    conn.execute(
                        f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})",
                        [row[c] for c in cols],
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


# ── gt project (Layer 2 + 3) ─────────────────────────────────────────


@main.group()
def project():
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
) -> None:
    """Scaffold a new GroundTruth project with the selected profile."""
    from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project, scaffold_summary

    target = Path(target_dir) if target_dir else Path.cwd() / project_name
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
    )
    result = scaffold_project(options)
    click.echo(scaffold_summary(result, profile))


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


@project.command("upgrade")
@click.option("--dry-run/--apply", default=True, help="Preview changes without writing (default: dry-run).")
@click.option("--force", is_flag=True, default=False, help="Overwrite customized files.")
@click.option("--dir", "target_dir", default=".", help="Project directory (default: cwd).")
def project_upgrade(dry_run: bool, force: bool, target_dir: str) -> None:
    """Update scaffold files to match the current GroundTruth version."""
    from groundtruth_kb.project.upgrade import execute_upgrade, plan_upgrade

    target = Path(target_dir).resolve()
    actions = plan_upgrade(target)

    if not actions:
        click.echo("Already at current version. Nothing to upgrade.")
        return

    for action in actions:
        status = action.action.upper()
        click.echo(f"  [{status}] {action.file} — {action.reason}")

    if dry_run:
        click.echo(f"\n{len(actions)} action(s). Run with --apply to execute.")
        return

    results = execute_upgrade(target, actions, force=force)
    for msg in results:
        click.echo(f"  {msg}")


# ── gt deliberations ──────────────────────────────────────────────


@main.group()
def deliberations():
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
