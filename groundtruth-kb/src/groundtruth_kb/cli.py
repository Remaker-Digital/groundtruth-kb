"""GT-KB CLI: native authority commands and explicit local operations.

Knowledge and bridge commands use the selected authority service. Local tools
operate on the selected project without a legacy SQLite command fallback.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved. Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any

import click

from groundtruth_kb import __version__
from groundtruth_kb._logging import configure_cli_logging
from groundtruth_kb.cli_authority import service_group
from groundtruth_kb.config import GTConfig, GTConfigError
from groundtruth_kb.project.registry_control_plane import (
    RegistryControlPlaneError,
    amend_artifact,
    inspect_registry,
    load_registry_snapshot,
    register_artifacts,
    transition_artifact,
)
from groundtruth_kb.project.registry_control_plane import validate_registry as validate_registry_control_plane
from groundtruth_kb.project.sot_registry import InvalidSoTRecord, SoTArtifact, UnknownDomain


def _resolve_config(ctx: click.Context) -> GTConfig:
    """Resolve GTConfig from the click context or auto-discover."""
    config_path = ctx.obj.get("config") if ctx.obj else None
    return GTConfig.load(config_path=config_path)


def _no_window_subprocess_kwargs() -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return kwargs


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


class _NoWindowsExpandGroup(click.Group):
    """Click Group that defaults windows_expand_args to False (WI-6697).

    Prevents Click on Windows from expanding glob-like CLI arguments into
    arbitrary file lists when taking arguments from sys.argv.
    """

    @staticmethod
    def _commands() -> dict[str, click.Command]:
        """Knowledge commands always use native authority; local tools need no database."""
        from groundtruth_kb.cli_authority import NATIVE_COMMANDS, harness_group, scaffold_specs_cmd

        return {
            **NATIVE_COMMANDS,
            "authority": authority_group,
            "service": service_group,
            "secrets": secrets,
            "push": push_group,
            "env": env_cmd,
            "config": config,
            "controls": controls_group,
            "commit": click.Group(
                "commit",
                help="Inspect local staged changes without database access.",
                commands={"preflight": commit_preflight_cmd},
            ),
            "application": click.Group(
                "application",
                help="Register hosted applications and inspect their boundaries.",
                commands={"inspect": application_inspect_cmd, "register": application_register_cmd},
            ),
            "scaffold": click.Group(
                "scaffold",
                help="Generate adopter-owned infrastructure files and starter specifications.",
                commands={"iac": scaffold_iac_cmd, "cicd": scaffold_cicd_cmd, "specs": scaffold_specs_cmd},
            ),
            "db": click.Group(
                "db", help="Explicit PostgreSQL administration and migration.", commands={"postgres": db_postgres_cmd}
            ),
            "hygiene": click.Group(
                "hygiene", help="Inspect local Git checkouts.", commands={"worktrees": hygiene_worktrees_cmd}
            ),
            "registry": click.Group(
                "registry",
                help="Read and update the canonical declaration using current authority facts.",
                commands={
                    name: registry_cmd.commands[name]
                    for name in (
                        "list",
                        "show",
                        "inspect",
                        "inventory",
                        "scan-strings",
                        "validate",
                        "reconcile",
                        "register",
                        "amend",
                        "transition",
                    )
                },
            ),
            "harness": click.Group(
                "harness",
                help="Read installation metadata or derive configuration from the canonical baseline.",
                commands={**harness_group.commands, "project": harness_project_cmd},
            ),
        }

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        command = self._commands().get(cmd_name)
        if command is None:
            raise click.ClickException(
                f"'{cmd_name}' has no native authority route. SQLite fallback is disabled. See 'gt --help'."
            )
        return command

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted(self._commands())

    def main(
        self,
        args: Any = None,
        prog_name: str | None = None,
        complete_var: str | None = None,
        standalone_mode: bool = True,
        windows_expand_args: bool = False,
        **extra: Any,
    ) -> Any:
        return super().main(
            args=args,
            prog_name=prog_name,
            complete_var=complete_var,
            standalone_mode=standalone_mode,
            windows_expand_args=windows_expand_args,
            **extra,
        )


@click.group(cls=_NoWindowsExpandGroup)
@click.version_option(version=__version__, prog_name="gt")
@click.option("--config", "config_path", type=click.Path(exists=True), default=None, help="Path to groundtruth.toml")
@click.pass_context
def main(ctx: click.Context, config_path: str | None) -> None:
    """GroundTruth KB — specification-driven governance toolkit."""
    _ensure_utf8_streams()
    configure_cli_logging()
    ctx.ensure_object(dict)
    ctx.obj["config"] = Path(config_path) if config_path else None


@main.group("env")
def env_cmd() -> None:
    """Local environment source-of-truth commands."""


def _load_env_sot_helpers() -> Any:
    from groundtruth_kb import env_sot

    return env_sot


@env_cmd.command("plan")
@click.option("--app", default="agent-red", show_default=True, help="Application env layout to inspect.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def env_plan_cmd(ctx: click.Context, app: str, json_output: bool) -> None:
    """Plan Agent Red local env SoT migration without printing values."""

    config = _resolve_config(ctx)
    env_sot = _load_env_sot_helpers()
    try:
        plan = env_sot.build_plan(Path(config.project_root), app=app)
    except env_sot.EnvSotError as exc:
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(json.dumps(plan.to_dict(), indent=2, sort_keys=True))
    else:
        click.echo(env_sot.render_plan(plan))


@env_cmd.command("check")
@click.option("--app", default="agent-red", show_default=True, help="Application env layout to inspect.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def env_check_cmd(ctx: click.Context, app: str, json_output: bool) -> None:
    """Check whether local env files are safe for app SoT migration."""

    config = _resolve_config(ctx)
    env_sot = _load_env_sot_helpers()
    try:
        plan = env_sot.check_plan(Path(config.project_root), app=app)
    except env_sot.EnvSotError as exc:
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(json.dumps(plan.to_dict(), indent=2, sort_keys=True))
    else:
        click.echo(env_sot.render_plan(plan))
    if not plan.ok_for_apply:
        raise SystemExit(1)


@env_cmd.command("migrate")
@click.option("--app", default="agent-red", show_default=True, help="Application env layout to migrate.")
@click.option("--dry-run", is_flag=True, default=False, help="Plan migration without mutating files.")
@click.option("--apply", "apply_", is_flag=True, default=False, help="Apply the migration when checks pass.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def env_migrate_cmd(ctx: click.Context, app: str, dry_run: bool, apply_: bool, json_output: bool) -> None:
    """Move app env keys to the Agent Red SoT and generate admin views."""

    if dry_run and apply_:
        raise click.UsageError("Use either --dry-run or --apply, not both.")
    config = _resolve_config(ctx)
    env_sot = _load_env_sot_helpers()
    try:
        result = env_sot.migrate(Path(config.project_root), app=app, apply=apply_)
    except env_sot.EnvSotError as exc:
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        click.echo(env_sot.render_migration_result(result))


@click.command("inspect")
@click.option(
    "--host-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Explicit host whose applications/ catalog and slots are inspected.",
)
@click.option("--json", "json_output", is_flag=True, help="Emit structured application diagnostics.")
@click.pass_context
def application_inspect_cmd(ctx: click.Context, host_root: Path, json_output: bool) -> None:
    """Read local application catalog, marker and artifact-boundary facts.

    The explicit host selects this local inspection independently of database
    configuration. Native application lifecycle qualification remains separate.
    """
    from groundtruth_kb.isolation.doctor_verdicts import evaluate_isolation_state

    try:
        root = host_root.resolve(strict=True)
        result = evaluate_isolation_state(root)
    except (OSError, RuntimeError) as exc:
        raise click.ClickException(f"Cannot inspect the selected application host: {exc}") from exc
    findings = result["verdicts"]
    if json_output:
        click.echo(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif findings:
        for finding in findings:
            click.echo(f"{finding['severity']} {finding['verdict']}: {finding['details']}")
            click.echo(f"  {finding['remediation']}")
    elif result["slots_status"]:
        click.echo(f"Application registry checks passed for {len(result['slots_status'])} applications.")
        click.echo("Native lifecycle qualification is separate.")
    else:
        click.echo("No application slots configured; no application qualification performed.")
    if findings:
        ctx.exit(1)


@click.command("register")
@click.argument("name")
@click.option(
    "--host-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Explicit platform Git checkout whose application catalog is updated.",
)
@click.option("--json", "json_output", is_flag=True, help="Emit registration result and changed paths.")
@click.pass_context
def application_register_cmd(ctx: click.Context, name: str, host_root: Path, json_output: bool) -> None:
    """Register a catalog entry and matching marker while preserving existing files."""
    from groundtruth_kb.isolation.registry_check import register_application

    try:
        result = register_application(host_root, name)
    except (OSError, RuntimeError, ValueError) as exc:
        if json_output:
            click.echo(json.dumps({"status": "refused", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
            ctx.exit(1)
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif result["status"] == "already_registered":
        click.echo(f"Application {name} is already registered.")
    else:
        click.echo(f"Successfully registered application {name}.")


@main.group("commit")
def commit_group() -> None:
    """Commit governance preflight commands."""


@commit_group.command("preflight")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.option(
    "--evidence-out",
    "--evidence-file",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write the evidence packet JSON to this path.",
)
@click.option("--python-bin", default=None, help="Python executable used for script checks.")
@click.option("--powershell-bin", default=None, help="PowerShell executable used for staged PS1 parsing.")
@click.pass_context
def commit_preflight_cmd(
    ctx: click.Context,
    json_output: bool,
    evidence_out: Path | None,
    python_bin: str | None,
    powershell_bin: str | None,
) -> None:
    """Run staged commit governance checks with structured evidence."""
    from groundtruth_kb.governance.commit_preflight import preflight_exit_code, run_commit_preflight

    config = _resolve_config(ctx)
    evidence = run_commit_preflight(
        Path(config.project_root),
        python_bin=python_bin,
        powershell_bin=powershell_bin,
        evidence_path=evidence_out,
    )
    if evidence_out is not None:
        evidence_out.parent.mkdir(parents=True, exist_ok=True)
        evidence_out.write_text(evidence.to_json() + "\n", encoding="utf-8")
    click.echo(evidence.to_json() if json_output else evidence.to_text_summary())
    ctx.exit(preflight_exit_code(evidence))


@main.group("push")
def push_group() -> None:
    """Push governance preflight and readiness commands."""


@push_group.command("preflight")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.option(
    "--evidence-out",
    "--evidence-file",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write the evidence packet JSON to this path.",
)
@click.option("--python-bin", default=None, help="Python executable used for secret range scans.")
@click.pass_context
def push_preflight_cmd(
    ctx: click.Context,
    json_output: bool,
    evidence_out: Path | None,
    python_bin: str | None,
) -> None:
    """Run pre-push redacted secret range scans from Git pre-push stdin."""
    from groundtruth_kb.governance.push_preflight import preflight_exit_code, run_push_preflight

    config = _resolve_config(ctx)
    evidence = run_push_preflight(
        Path(config.project_root),
        sys.stdin.read(),
        python_bin=python_bin,
        evidence_path=evidence_out,
    )
    if evidence_out is not None:
        evidence_out.parent.mkdir(parents=True, exist_ok=True)
        evidence_out.write_text(evidence.to_json() + "\n", encoding="utf-8")
    click.echo(evidence.to_json() if json_output else evidence.to_text_summary())
    ctx.exit(preflight_exit_code(evidence))


@push_group.command("readiness")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.option(
    "--evidence-out",
    "--evidence-file",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write the evidence packet JSON to this path.",
)
@click.option("--remote", default="origin", show_default=True, help="Git remote name to check.")
@click.option("--hostname", default="github.com", show_default=True, help="GitHub hostname for gh auth status.")
@click.option("--timeout-seconds", default=15, show_default=True, type=int, help="Per-command timeout.")
@click.pass_context
def push_readiness_cmd(
    ctx: click.Context,
    json_output: bool,
    evidence_out: Path | None,
    remote: str,
    hostname: str,
    timeout_seconds: int,
) -> None:
    """Run a read-only non-interactive push readiness diagnostic."""
    from groundtruth_kb.governance.push_readiness import readiness_exit_code, run_push_readiness

    config = _resolve_config(ctx)
    evidence = run_push_readiness(
        Path(config.project_root),
        remote=remote,
        hostname=hostname,
        timeout_seconds=timeout_seconds,
        evidence_path=evidence_out,
    )
    if evidence_out is not None:
        evidence_out.parent.mkdir(parents=True, exist_ok=True)
        evidence_out.write_text(evidence.to_json() + "\n", encoding="utf-8")
    click.echo(evidence.to_json() if json_output else evidence.to_text_summary())
    ctx.exit(readiness_exit_code(evidence))


@main.group("authority")
def authority_group() -> None:
    """Resolve current canonical terminology through the authority service."""


@authority_group.command("resolve")
@click.argument("subject")
@click.option("--scope", default=None, help="Restrict resolution to the canonical term scope.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def authority_resolve_cmd(ctx: click.Context, subject: str, scope: str | None, json_output: bool) -> None:
    """Resolve an exact current name, ID or accepted synonym without a static map."""
    from groundtruth_kb.authority import format_resolution
    from groundtruth_kb.cli_authority import _call

    result = _call(ctx, "GET", "/v1/authority/resolve", query={"subject": subject, "scope": scope})
    click.echo(json.dumps(result, indent=2, sort_keys=True) if json_output else format_resolution(result))
    if result.get("status") != "resolved":
        raise SystemExit(1)


@authority_group.command("status")
@click.option("--scope", default=None, help="Restrict the corpus check to one scope.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def authority_status_cmd(ctx: click.Context, scope: str | None, json_output: bool) -> None:
    """Check current terminology interpretation and formal-source references."""
    from groundtruth_kb.authority import format_resolution
    from groundtruth_kb.cli_authority import _call

    result = _call(ctx, "GET", "/v1/authority/status", query={"scope": scope})
    click.echo(json.dumps(result, indent=2, sort_keys=True) if json_output else format_resolution(result))
    if result.get("status") != "pass":
        raise SystemExit(1)


@main.group("hygiene")
def hygiene_group() -> None:
    """Read-only repository observations."""


@hygiene_group.command("worktrees")
@click.option("--root", type=click.Path(file_okay=False), default=".", show_default=True)
@click.option("--integration-ref", default="develop", show_default=True)
@click.option("--json", "json_output", is_flag=True, default=False)
@click.pass_context
def hygiene_worktrees_cmd(ctx: click.Context, root: str, integration_ref: str, json_output: bool) -> None:
    """Report checkout observations without inferring liveness or disposal eligibility."""
    from groundtruth_kb.session.worktree import SessionWorktreeError, classify_worktrees

    project_root = Path(root).absolute() if root != "." else Path(_resolve_config(ctx).project_root)
    try:
        states = classify_worktrees(project_root, integration_ref=integration_ref)
    except SessionWorktreeError as exc:
        raise click.ClickException(f"{exc.code}: {exc}") from exc

    if json_output:
        click.echo(json.dumps([state.as_dict() for state in states], indent=2, sort_keys=True))
        return

    if not states:
        click.echo("No other checkouts reported.")
        return
    counts: dict[str, int] = {}
    for state in states:
        counts[state.classification] = counts.get(state.classification, 0) + 1
        tracked = "unknown" if state.tracked_dirty is None else str(state.tracked_dirty)
        untracked = "unknown" if state.untracked is None else str(state.untracked)
        click.echo(
            f"{state.classification:20} {state.candidate_action:22} "
            f"dirty={tracked:<7} untracked={untracked:<7} {state.path}"
        )
    click.echo("Git observations do not establish context liveness or disposal eligibility.")
    click.echo("  ".join(f"{name}={count}" for name, count in sorted(counts.items())))


@main.group(name="registry")
def registry_cmd() -> None:
    """SoT artifact registry commands (GOV-PLATFORM-SOT-REGISTRY-001)."""


def _registry_control_kwargs(ctx: click.Context) -> dict[str, Any]:
    config = _resolve_config(ctx)
    return {"project_root": Path(config.project_root)}


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
        "restore_action": rec.restore_action,
        "coverage_mode": rec.coverage_mode,
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
    """List artifact records from the current canonical declaration."""
    try:
        records = list(load_registry_snapshot(**_registry_control_kwargs(ctx)).records)
    except (RegistryControlPlaneError, InvalidSoTRecord, UnknownDomain, FileNotFoundError) as exc:
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
    try:
        records = load_registry_snapshot(**_registry_control_kwargs(ctx)).records
    except (RegistryControlPlaneError, InvalidSoTRecord, UnknownDomain, FileNotFoundError) as exc:
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


@registry_cmd.command("inventory")
@click.option("--json", "json_output", is_flag=True, help="Emit the complete inventory report.")
@click.pass_context
def registry_inventory(ctx: click.Context, json_output: bool) -> None:
    """Inspect declared artifact coverage without changing files or domain state."""
    from groundtruth_kb.inventory import InventoryScanError, build_refresh_report

    root = Path(_resolve_config(ctx).project_root)
    try:
        report = build_refresh_report(root)
    except (InventoryScanError, OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return
    summary = report["summary"]
    click.echo(f"Registry inventory: {summary['artifact_count']} artifacts, {summary['scanned_file_count']} files")
    click.echo(f"blocking findings: {summary['blocking_finding_count']}")
    click.echo("path classes: " + ", ".join(f"{key}={value}" for key, value in summary["path_class_counts"].items()))
    for finding in report["registry_findings"]:
        click.echo(f"{finding['artifact_id']}: {finding['code']} ({finding['storage_path']})")


@registry_cmd.command("scan-strings")
@click.option("--match", "matches", multiple=True, help="Literal to find in declared files; repeat for more literals.")
@click.option(
    "--match-file", "match_files", multiple=True, type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("--critical-class", "critical_classes", multiple=True, help="Add an artifact ID, domain or lifecycle.")
@click.option("--critical-path", "critical_paths", multiple=True, help="Add a project-relative path pattern.")
@click.option("--json", "json_output", is_flag=True, help="Emit the complete scan report.")
@click.option("--report-only", is_flag=True, help="Report findings without a finding-driven nonzero exit.")
@click.pass_context
def registry_scan_strings(
    ctx: click.Context,
    matches: tuple[str, ...],
    match_files: tuple[Path, ...],
    critical_classes: tuple[str, ...],
    critical_paths: tuple[str, ...],
    json_output: bool,
    report_only: bool,
) -> None:
    """Scan declared file contents; no database, membership or work-state mutation."""
    from groundtruth_kb.inventory import (
        InventoryScanError,
        emit_markdown_ledger,
        load_match_file,
        scan_inventory_strings,
    )

    root = Path(_resolve_config(ctx).project_root)
    try:
        literals = list(matches)
        for path in match_files:
            literals.extend(load_match_file(path))
        report = scan_inventory_strings(
            root,
            literals,
            critical_classes=set(critical_classes),
            critical_paths=critical_paths,
        )
    except (InventoryScanError, OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
        if json_output
        else emit_markdown_ledger(report)
    )
    if not report_only and (report["summary"]["critical"] or report["missing_artifacts"]):
        raise click.exceptions.Exit(1)


@registry_cmd.command("validate")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def registry_validate(ctx: click.Context, json_output: bool) -> None:
    """Validate declaration schema, actual identity and current path coverage."""
    result = validate_registry_control_plane(config=_resolve_config(ctx), **_registry_control_kwargs(ctx))
    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    else:
        status = "VALID" if result["valid"] else "INVALID"
        click.echo(f"Registry control plane: {status}")
        for error in result["errors"]:
            click.echo(f"  {error}")
    if not result["valid"]:
        raise SystemExit(1)


@registry_cmd.command("inspect")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--no-census", is_flag=True, help="Skip the deterministic whole-root census.")
@click.pass_context
def registry_inspect(ctx: click.Context, json_output: bool, no_census: bool) -> None:
    """Inspect the canonical declaration, actual identity and current coverage."""
    result = inspect_registry(
        config=_resolve_config(ctx), include_census=not no_census, **_registry_control_kwargs(ctx)
    )
    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    else:
        click.echo(f"Registry coherent: {result.get('coherent', False)}")
        if result.get("record_count") is not None:
            click.echo(f"Records: {result['record_count']}")
        if result.get("error"):
            click.echo(f"Error: {result['error']}")


@registry_cmd.command("reconcile")
@click.option("--json", "json_output", is_flag=True, help="Emit the complete machine-readable report.")
@click.option("--deep", is_flag=True, help="Inspect disposable descendants instead of emitting pruned envelopes.")
@click.option(
    "--batch-output",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write explicit additive declarations to a new JSON file inside the project root.",
)
@click.pass_context
def registry_reconcile(
    ctx: click.Context,
    json_output: bool,
    deep: bool,
    batch_output: Path | None,
) -> None:
    """Reconcile registry membership through all five typed observers."""

    from groundtruth_kb.project.artifact_membership_reconciliation import (
        reconcile_artifact_membership,
    )

    config = _resolve_config(ctx)
    root = Path(config.project_root).resolve()
    try:
        report = reconcile_artifact_membership(
            root,
            db_path=Path(config.db_path),
            config=config,
            deep=deep,
        )
        if batch_output is not None:
            output = batch_output if batch_output.is_absolute() else root / batch_output
            output = output.resolve()
            output.relative_to(root)
            plan_bytes = (
                json.dumps(report["batch_records"], ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
                + b"\n"
            )
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("xb") as handle:
                handle.write(plan_bytes)
            report["batch_output"] = output.relative_to(root).as_posix()
    except (OSError, RegistryControlPlaneError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(report, indent=2, sort_keys=True))
        return
    click.echo(
        "Registry reconciliation: "
        f"membership_complete={str(report['membership_complete']).lower()}, "
        f"load_bearing_gaps={report['counts']['unregistered_load_bearing']}, "
        f"unknown={report['counts']['invalid_unknown']}, "
        f"candidates={len(report['admission_candidates'])}, "
        f"pruned={report['pruned_envelope_count']}"
    )
    if batch_output is not None:
        click.echo(f"Batch declarations: {report['batch_output']}")


def _artifact_from_payload(payload: dict[str, Any]) -> SoTArtifact:
    from groundtruth_kb.project.sot_registry import _parse_record

    if not isinstance(payload, dict):
        raise ValueError("A registry record must be a JSON object")
    return _parse_record(payload)


def _registry_write_options(function: Any) -> Any:
    function = click.option(
        "--dry-run", is_flag=True, help="Validate the current source and intended result without writing."
    )(function)
    return click.option(
        "--expected-declaration-digest",
        default=None,
        help="Refuse if the canonical declaration changed since this read.",
    )(function)


@registry_cmd.command("register")
@click.option("--record-json", default=None, help="One explicit declaration as JSON.")
@click.option(
    "--batch-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="JSON array of explicit declarations.",
)
@_registry_write_options
@click.pass_context
def registry_register(ctx: click.Context, /, record_json: str | None, batch_file: Path | None, **options: Any) -> None:
    """Register current artifact membership in the canonical declaration."""
    if (record_json is None) == (batch_file is None):
        raise click.ClickException("Provide exactly one of --record-json or --batch-file")
    config = _resolve_config(ctx)
    try:
        if batch_file is not None:
            selected = batch_file if batch_file.is_absolute() else Path(config.project_root) / batch_file
            raw = json.loads(selected.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("A registration batch must be a JSON array of declarations")
        else:
            raw = [json.loads(record_json or "")]
        result = register_artifacts(
            [_artifact_from_payload(item) for item in raw], config=config, **_registry_control_kwargs(ctx), **options
        )
    except (RegistryControlPlaneError, OSError, TypeError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2, sort_keys=True))


@registry_cmd.command("amend")
@click.argument("entry_id")
@click.option("--changes-json", required=True, help="Non-identity field changes as JSON.")
@_registry_write_options
@click.pass_context
def registry_amend(ctx: click.Context, /, entry_id: str, changes_json: str, **options: Any) -> None:
    """Amend metadata without concealing a locator or lifecycle change."""
    try:
        changes = json.loads(changes_json)
        if not isinstance(changes, dict):
            raise ValueError("--changes-json must be a JSON object")
        result = amend_artifact(
            entry_id, changes, config=_resolve_config(ctx), **_registry_control_kwargs(ctx), **options
        )
    except (RegistryControlPlaneError, OSError, TypeError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2, sort_keys=True))


@registry_cmd.command("transition")
@click.argument("entry_id")
@click.option("--changes-json", default=None, help="Locator, coverage, lifecycle or metadata postimage fields.")
@click.option(
    "--remove", is_flag=True, help="Remove membership only when existing content retains coverage or is absent."
)
@click.option("--removal", "removals", multiple=True, help="Remove a related declaration in the same atomic change.")
@click.option(
    "--removals-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="UTF-8 JSON array of related IDs to remove in the same atomic change.",
)
@_registry_write_options
@click.pass_context
def registry_transition(
    ctx: click.Context,
    /,
    entry_id: str,
    changes_json: str | None,
    remove: bool,
    removals: tuple[str, ...],
    removals_file: Path | None,
    **options: Any,
) -> None:
    """Reconcile the declaration to the actual artifact result; this does not move or delete files."""
    try:
        changes = json.loads(changes_json) if changes_json is not None else None
        if changes is not None and not isinstance(changes, dict):
            raise ValueError("--changes-json must be a JSON object")
        related = list(removals)
        if removals_file is not None:
            file_ids = json.loads(removals_file.read_text(encoding="utf-8"))
            if not isinstance(file_ids, list):
                raise ValueError("--removals-file must contain a JSON array of IDs")
            related.extend(file_ids)
        result = transition_artifact(
            entry_id,
            changes,
            remove=remove,
            removals=related,
            config=_resolve_config(ctx),
            **_registry_control_kwargs(ctx),
            **options,
        )
    except (RegistryControlPlaneError, OSError, TypeError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2, sort_keys=True))


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


@main.group("db")
def db_cmd() -> None:
    """Database operations."""


@db_cmd.group("postgres")
def db_postgres_cmd() -> None:
    """Native PostgreSQL shadow-kernel operations."""


def _emit_postgres_json(payload: dict[str, Any]) -> None:
    click.echo(json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")))


def _run_postgres_operation(ctx: click.Context, operation: Any) -> None:
    from groundtruth_kb.postgres_kernel import PostgresKernel, PostgresKernelError

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            cfg = _resolve_config(ctx)
        result = operation(PostgresKernel(cfg.postgresql), cfg)
    except GTConfigError as exc:
        _emit_postgres_json({"error": {"code": "invalid_postgresql_config", "message": str(exc)}})
        ctx.exit(1)
    except PostgresKernelError as exc:
        _emit_postgres_json(exc.to_json_dict())
        ctx.exit(1)
    _emit_postgres_json(result)


@db_postgres_cmd.command("init")
@click.option("--upgrade-from", metavar="SCHEMA_SHA256", help="Explicitly transition the supported existing schema.")
@click.pass_context
def db_postgres_init_cmd(ctx: click.Context, upgrade_from: str | None) -> None:
    """Initialize an empty schema or explicitly transition a known predecessor."""
    _run_postgres_operation(
        ctx,
        lambda kernel, _cfg: (
            kernel.initialize() if upgrade_from is None else kernel.upgrade_schema(expected_schema_sha256=upgrade_from)
        ),
    )


@db_postgres_cmd.command("status")
@click.pass_context
def db_postgres_status_cmd(ctx: click.Context) -> None:
    """Read PostgreSQL kernel status without creating or repairing objects."""
    _run_postgres_operation(ctx, lambda kernel, _cfg: kernel.status())


@db_postgres_cmd.command("export-current")
@click.option(
    "--sqlite-snapshot",
    type=click.STRING,
    metavar="PATH",
)
@click.option(
    "--transform-plan",
    type=click.STRING,
    metavar="PATH",
)
@click.option("--output", type=click.STRING, metavar="PATH")
@click.option("--preflight-only", is_flag=True)
@click.pass_context
def db_postgres_export_current_cmd(
    ctx: click.Context,
    sqlite_snapshot: str | None,
    transform_plan: str | None,
    output: str | None,
    preflight_only: bool,
) -> None:
    """Export reviewed current state from one immutable SQLite snapshot."""
    valid_preflight = preflight_only and sqlite_snapshot is not None and transform_plan is None and output is None
    valid_export = (
        not preflight_only and sqlite_snapshot is not None and transform_plan is not None and output is not None
    )
    if not valid_preflight and not valid_export:
        _emit_postgres_json(
            {
                "error": {
                    "code": "invalid_export_mode",
                    "message": (
                        "export-current requires --sqlite-snapshot with either --preflight-only "
                        "alone or both --transform-plan and --output"
                    ),
                }
            }
        )
        ctx.exit(1)

    if valid_preflight:
        assert sqlite_snapshot is not None
        _run_postgres_operation(
            ctx,
            lambda kernel, cfg: kernel.preflight_export_current(
                sqlite_snapshot=Path(sqlite_snapshot),
                live_sqlite_source=cfg.db_path,
            ),
        )
        return

    assert sqlite_snapshot is not None
    assert transform_plan is not None
    assert output is not None
    _run_postgres_operation(
        ctx,
        lambda kernel, cfg: kernel.export_current(
            sqlite_snapshot=Path(sqlite_snapshot),
            transform_plan=Path(transform_plan),
            output=Path(output),
            live_sqlite_source=cfg.db_path,
        ),
    )


@db_postgres_cmd.command("import-current")
@click.option("--input", "input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--actor", required=True)
@click.option("--reason", required=True)
@click.pass_context
def db_postgres_import_current_cmd(ctx: click.Context, input_path: Path, actor: str, reason: str) -> None:
    """Import one complete canonical current-state manifest."""
    _run_postgres_operation(
        ctx,
        lambda kernel, cfg: kernel.import_current(
            input_path=input_path, actor=actor, reason=reason, project_root=cfg.project_root
        ),
    )


@db_postgres_cmd.command("readback-current")
@click.option("--output", type=click.Path(dir_okay=False, path_type=Path), required=True)
@click.pass_context
def db_postgres_readback_current_cmd(ctx: click.Context, output: Path) -> None:
    """Publish a canonical current-state readback manifest."""
    _run_postgres_operation(ctx, lambda kernel, _cfg: kernel.readback_current(output=output))


@main.command()
@click.option("--json", "json_output", is_flag=True, help="Emit resolved settings as JSON.")
@click.pass_context
def config(ctx: click.Context, json_output: bool) -> None:
    """Show resolved settings without probing services or optional dependencies."""
    try:
        cfg = _resolve_config(ctx)
        project_root = str(cfg.project_root.resolve())
        db_path = str(cfg.db_path.resolve())
        chroma_path = str(cfg.chroma_path.resolve()) if cfg.chroma_path is not None else None
    except (GTConfigError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    postgresql = {
        "service": cfg.postgresql.service,
        "connect_timeout_seconds": cfg.postgresql.connect_timeout_seconds,
        "lock_timeout_ms": cfg.postgresql.lock_timeout_ms,
        "statement_timeout_ms": cfg.postgresql.statement_timeout_ms,
    }
    if json_output:
        click.echo(
            json.dumps(
                {
                    "app_title": cfg.app_title,
                    "project_root": project_root,
                    "authority_url": cfg.authority_url,
                    "postgresql": postgresql,
                    "legacy_paths": {"db_path": db_path, "chroma_path": chroma_path},
                },
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        return
    click.echo(f"Application title: {cfg.app_title}")
    click.echo(f"Project root: {project_root}")
    click.echo(f"Authority URL: {cfg.authority_url or '(missing; configure before knowledge operations)'}")
    click.echo(f"PostgreSQL service: {cfg.postgresql.service}")
    click.echo(f"PostgreSQL connect timeout (seconds): {cfg.postgresql.connect_timeout_seconds}")
    click.echo(f"PostgreSQL lock timeout (ms): {cfg.postgresql.lock_timeout_ms}")
    click.echo(f"PostgreSQL statement timeout (ms): {cfg.postgresql.statement_timeout_ms}")
    click.echo(f"Legacy helper db_path: {db_path}")
    click.echo(f"Legacy helper chroma_path: {chroma_path if chroma_path is not None else 'unset'}")


@main.group("controls")
def controls_group() -> None:
    """Inspect and atomically update the selected live operational-control artifact."""


def _control_proposal(path: Path) -> bytes:
    from groundtruth_kb.project.operational_control_config import MAX_CATALOG_BYTES, OperationalControlConfigError

    with path.open("rb") as stream:
        payload = stream.read(MAX_CATALOG_BYTES + 1)
    if len(payload) > MAX_CATALOG_BYTES:
        raise OperationalControlConfigError("resource_bound", "proposed artifact exceeds the format byte bound")
    return payload


def _controls_call(
    ctx: click.Context, operation: str, input_path: Path | None, expected_sha256: str | None
) -> dict[str, Any]:
    from groundtruth_kb.project.operational_control_config import (
        OperationalControlConfigError,
        catalog_dict,
        diff_operational_controls,
        load_operational_control_catalog,
        set_operational_controls,
        validate_operational_control_bytes,
    )

    try:
        root = _resolve_config(ctx).project_root
        if operation == "show":
            return catalog_dict(load_operational_control_catalog(root))
        if operation == "validate":
            catalog = (
                load_operational_control_catalog(root)
                if input_path is None
                else validate_operational_control_bytes(_control_proposal(input_path))
            )
            return {"valid": True, "catalog_sha256": catalog.catalog_sha256, "control_count": len(catalog.definitions)}
        if input_path is None:
            raise click.ClickException("A proposed control artifact is required")
        proposed = _control_proposal(input_path)
        if operation == "diff":
            return diff_operational_controls(root, proposed)
        if expected_sha256 is None:
            raise click.ClickException("The currently observed artifact SHA-256 is required")
        return set_operational_controls(root, proposed, expected_sha256=expected_sha256)
    except (GTConfigError, OperationalControlConfigError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc


@controls_group.command("show")
@click.pass_context
def controls_show(ctx: click.Context) -> None:
    """Show exact live values, units, metadata, invariants and source identity as JSON."""
    click.echo(json.dumps(_controls_call(ctx, "show", None, None), indent=2, sort_keys=True))


@controls_group.command("validate")
@click.option("--input", "input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_context
def controls_validate(ctx: click.Context, input_path: Path | None) -> None:
    """Validate the canonical artifact or an explicit proposed TOML file without writing."""
    click.echo(json.dumps(_controls_call(ctx, "validate", input_path, None), indent=2, sort_keys=True))


@controls_group.command("diff")
@click.option("--input", "input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.pass_context
def controls_diff(ctx: click.Context, input_path: Path) -> None:
    """Compare current and proposed control definitions and invariants without writing."""
    click.echo(json.dumps(_controls_call(ctx, "diff", input_path, None), indent=2, sort_keys=True))


@controls_group.command("set")
@click.option("--input", "input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option(
    "--expected-sha256", required=True, help="Current catalog_sha256 from controls show; refuses stale input."
)
@click.pass_context
def controls_set(ctx: click.Context, input_path: Path, expected_sha256: str) -> None:
    """Validate and atomically replace the selected artifact for subsequent operations."""
    click.echo(json.dumps(_controls_call(ctx, "set", input_path, expected_sha256), indent=2, sort_keys=True))


@main.group()
def scaffold() -> None:
    """Specification scaffold commands (F6)."""


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


@main.group("harness")
def harness_group() -> None:
    """Harness configuration and local projection operations."""


@harness_group.command("project")
@click.argument("harness")
@click.option("--validate", is_flag=True, help="Validate derivation without refreshing installed output.")
@click.option("--check", is_flag=True, help="Report drift without refreshing installed output.")
@click.option("--dry-run", is_flag=True, help="Show the proposed output paths without writing.")
@click.pass_context
def harness_project_cmd(ctx: click.Context, harness: str, validate: bool, check: bool, dry_run: bool) -> None:
    """Derive one harness configuration from the selected project's canonical baseline."""
    if sum((validate, check, dry_run)) > 1:
        raise click.UsageError("Choose at most one of --validate, --check and --dry-run.")
    config = _resolve_config(ctx)
    root = Path(config.project_root).resolve()
    script = root / "scripts" / "harness_projection" / "project_harness.py"
    if not script.is_file() or script.resolve() != script:
        raise click.ClickException("The harness projector is missing or redirected in the selected project.")
    command = [sys.executable, str(script), "--harness", harness]
    if validate:
        command.append("--validate")
    elif check:
        command.append("--check")
    elif dry_run:
        command.append("--dry-run")
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            **_no_window_subprocess_kwargs(),
        )
    except OSError as exc:
        raise click.ClickException(f"Could not run the selected project's harness projector: {exc}") from exc
    click.echo(completed.stdout, nl=False)
    click.echo(completed.stderr, nl=False, err=True)
    ctx.exit(completed.returncode)


if __name__ == "__main__":
    main(windows_expand_args=False)
