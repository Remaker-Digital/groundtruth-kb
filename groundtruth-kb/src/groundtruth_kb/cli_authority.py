"""Ordinary CLI commands for a configured native authority service."""

from __future__ import annotations

import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

import click

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig
from groundtruth_kb.postgres_kernel import canonical_json_bytes, parse_json_bytes

if TYPE_CHECKING:
    from groundtruth_kb.services_control import Installation


def _config(ctx: click.Context) -> GTConfig:
    return GTConfig.load(config_path=(ctx.find_root().obj or {}).get("config"))


def _client(ctx: click.Context, *, config: GTConfig | None = None) -> AuthorityClient:
    config = _config(ctx) if config is None else config
    if not config.authority_url:
        raise click.ClickException("No authority_url is configured")
    return AuthorityClient(config.authority_url)


def _call(
    ctx: click.Context,
    /,
    method: str,
    path: str,
    *,
    timeout: float | None = None,
    client: AuthorityClient | None = None,
    **kwargs: Any,
) -> Any:
    try:
        client = _client(ctx) if client is None else client
        if timeout is not None:
            client.timeout = timeout
        return client.request(method, path, **kwargs)
    except AuthorityClientError as error:
        details = "\n" + canonical_json_bytes(error.details).decode("utf-8").strip() if error.details else ""
        raise click.ClickException(f"{error.code}: {error}{details}") from error


def _emit(value: Any, json_output: bool, *, complete: bool = False) -> None:
    if json_output:
        click.echo(canonical_json_bytes(value).decode("utf-8"), nl=False)
        return
    rows = value if isinstance(value, list) else [value]
    for row in rows:
        record = row.get("project", row.get("work_item", row)) if isinstance(row, dict) else None
        if isinstance(record, dict) and "id" in record:
            label = record.get("title", record.get("name", record.get("canonical_term", "")))
            if "dependent_project_id" in record:
                label = (
                    f"{record['dependent_project_id']} requires {record['prerequisite_project_id']} "
                    f"= {record['required_prerequisite_state']} at {record['affected_gate']} [{record['status']}]"
                )
            elif record.get("artifact_type") == "spec":
                label = f"{record['project_id']} -> {record['artifact_ref']} [{record['status']}]"
            elif record.get("artifact_type") in {"bridge_thread", "completion_guard"}:
                kind = f"{record['artifact_type']}:{record['artifact_ref']}"
                label = f"{record['project_id']} -> {kind} [{record['status']}]"
            click.echo(f"{record['id']} v{record.get('version', '?')}: {label}")
            description = record.get("description", record.get("definition"))
            if description:
                click.echo(description)
            if complete:
                details = {
                    key: value
                    for key, value in record.items()
                    if key not in {"id", "version", "title", "name", "description", "canonical_term", "definition"}
                }
                if record is not row:
                    details.update({key: value for key, value in row.items() if value is not record})
                for key, value in details.items():
                    click.echo(f"{key}: {canonical_json_bytes(value).decode('utf-8').strip()}")
            continue
        click.echo(canonical_json_bytes(row).decode("utf-8"), nl=False)


def _fields(path: Path) -> dict[str, Any]:
    try:
        value = parse_json_bytes(path.read_bytes())
    except Exception as error:  # intentional-catch: an unreadable fields file becomes a ClickException
        raise click.ClickException("The fields file must contain a UTF-8 JSON object") from error
    if not isinstance(value, dict):
        raise click.ClickException("The fields file must contain a JSON object")
    return value


def _domain_group(name: str, domain: str, *, read_only: bool = False, help: str | None = None) -> click.Group:
    @click.group(name)
    def group() -> None:
        """Read or amend current canonical records through the authority service."""

    if help is not None:
        group.help = help

    @group.command("show")
    @click.argument("record_id")
    @click.option("--history", "with_history", is_flag=True, help="Include the recorded version chain.")
    @click.option("--json", "json_output", is_flag=True)
    @click.pass_context
    def show(ctx: click.Context, record_id: str, with_history: bool, json_output: bool) -> None:
        """Read the current record, including planning relationships where relevant."""
        if with_history:
            result = _call(ctx, "GET", f"/v1/{domain}/{quote(record_id, safe='')}/history")
            if json_output:
                _emit(result, True)
                return
            _emit(result["current"], False, complete=True)
            click.echo("Version History:")
            for entry in result["history"]:
                click.echo(f"  v{entry['version']} {entry['changed_at']} {entry['actor']}: {entry['reason']}")
            return
        _emit(_call(ctx, "GET", f"/v1/{domain}/{quote(record_id, safe='')}"), json_output, complete=True)

    @group.command("list")
    @click.option("--limit", type=click.IntRange(1), default=200, show_default=True)
    @click.option("--after", default=None, help="Continue after this record ID.")
    @click.option("--search", default=None)
    @click.option("--status", default=None)
    @click.option("--kind", type=click.Choice(["program", "project"]), default=None)
    @click.option("--priority", default=None)
    @click.option("--spec-id", default=None)
    @click.option("--plan-id", default=None)
    @click.option("--project-id", default=None, hidden=domain != "project-formal-links")
    @click.option(
        "--artifact-type",
        "artifact_type",
        type=click.Choice(["spec", "bridge_thread", "completion_guard"]),
        default=None,
        hidden=domain != "project-formal-links",
        help="Formal-link kind to list; defaults to spec.",
    )
    @click.option(
        "--repository-ref",
        default=None,
        hidden=domain != "projects",
        help="Filter by the exact project repository reference.",
    )
    @click.option(
        "--application-scope",
        default=None,
        hidden=domain not in {"specifications", "tests"},
        help="Filter by gtkb_platform or an exact application:<catalog name> scope.",
    )
    @click.option("--scope", default=None, hidden=domain not in {"terms", "specifications"})
    @click.option("--source-type", default=None, hidden=domain != "deliberations")
    @click.option("--work-item-id", default=None, hidden=domain != "deliberations")
    @click.option("--authority-level", default=None, hidden=domain != "terms")
    @click.option("--dependent-project", "dependent_project_id", default=None, hidden=domain != "project-dependencies")
    @click.option(
        "--prerequisite-project", "prerequisite_project_id", default=None, hidden=domain != "project-dependencies"
    )
    @click.option(
        "--affected-gate",
        type=click.Choice(["readiness", "closure"]),
        default=None,
        hidden=domain != "project-dependencies",
    )
    @click.option("--json", "json_output", is_flag=True)
    @click.pass_context
    def list_records(ctx: click.Context, /, limit: int, after: str | None, json_output: bool, **filters: Any) -> None:
        """List a bounded set of current records in deterministic ID order."""
        if domain in {"work-items", "terms"} and filters.get("status") is not None:
            key = "resolution_status" if domain == "work-items" else "lifecycle_status"
            filters[key] = filters.pop("status")
        records: list[dict[str, Any]] = []
        while len(records) < limit:
            result = _call(
                ctx, "GET", f"/v1/{domain}", query={**filters, "after": after, "limit": min(1000, limit - len(records))}
            )
            records.extend(result["records"])
            after = result["next_after"]
            if not after:
                break
        _emit(records, json_output)

    if read_only:
        if help is None:
            group.help = "Read current installation metadata; roles belong to session bindings."
        return group

    @group.command("record")
    @click.option("--id", "record_id", required=True)
    @click.option(
        "--fields-file",
        type=click.Path(exists=True, dir_okay=False, path_type=Path),
        required=True,
        help="JSON object containing the authored domain fields to create or change.",
    )
    @click.option("--expected-version", type=click.IntRange(0), required=True, help="0 asserts a new record.")
    @click.option("--actor", required=True, help="Attribution for the current correction.")
    @click.option("--change-reason", "reason", required=True)
    @click.option("--project-id", default=None, help="Required when creating a work item.")
    @click.option("--kind", type=click.Choice(["program", "project"]), default=None)
    @click.option("--json", "json_output", is_flag=True)
    @click.pass_context
    def record(
        ctx: click.Context,
        record_id: str,
        fields_file: Path,
        expected_version: int,
        actor: str,
        reason: str,
        project_id: str | None,
        kind: str | None,
        json_output: bool,
    ) -> None:
        """Apply a version-checked domain amendment and return canonical readback."""
        body = {"expected_version": expected_version, "actor": actor, "reason": reason, "fields": _fields(fields_file)}
        if project_id is not None:
            body["project_id"] = project_id
        if kind is not None:
            body["kind"] = kind
        _emit(_call(ctx, "PUT", f"/v1/{domain}/{quote(record_id, safe='')}", body=body), json_output)

    return group


NATIVE_COMMANDS: dict[str, click.Command] = {
    "harness": (harness_group := _domain_group("harness", "harnesses")),
    "terms": _domain_group("terms", "terms"),
    "spec": _domain_group("spec", "specifications"),
    "tests": _domain_group("tests", "tests"),
    "projects": (projects_group := _domain_group("projects", "projects")),
    "backlog": (backlog_group := _domain_group("backlog", "work-items")),
    "test-plans": _domain_group("test-plans", "test-plans"),
    "test-phases": _domain_group("test-phases", "test-phases"),
    "deliberations": _domain_group(
        "deliberations",
        "deliberations",
        read_only=True,
        help="Read historical deliberation records; they carry no authorization, currentness or completion result.",
    ),
}


projects_group.add_command(_domain_group("dependencies", "project-dependencies"))
formal_links_group = _domain_group("formal-links", "project-formal-links")
projects_group.add_command(formal_links_group)


@click.group("validate")
def validate_group() -> None:
    """Read current authority and emit bounded review candidates."""


@validate_group.command("spec-coherence")
@click.option("--rule-set", default=None, help="Limit to one rule ID from the project's existing TOML rules.")
@click.option("--output", type=click.Path(file_okay=False, path_type=Path), required=True)
@click.option("--format", "fmt", type=click.Choice(["json", "md", "both"]), default="both", show_default=True)
@click.option("--fail-on-findings", is_flag=True, help="Exit 5 when review candidates are emitted.")
@click.pass_context
def validate_spec_coherence(
    ctx: click.Context, rule_set: str | None, output: Path, fmt: str, fail_on_findings: bool
) -> None:
    """Scan active specifications; candidates are not verdicts or verification."""
    from groundtruth_kb.coherence import (
        CoherenceRuleError,
        emit_json,
        emit_markdown,
        load_rules,
        load_specs_from_authority,
        make_result,
        run_all,
    )

    config = _config(ctx)
    rules_path = config.project_root / "config/governance/spec-coherence-rules.toml"
    try:
        rules = load_rules(rules_path, name=rule_set)
        client = _client(ctx)
        specs = load_specs_from_authority(client)
        result = make_result(
            authority_url=client.url, rule_set_path=rules_path, specs=specs, rules=rules, findings=run_all(specs, rules)
        )
        if fmt in {"json", "both"}:
            emit_json(result, output / "findings.json")
        if fmt in {"md", "both"}:
            emit_markdown(result, output / "summary.md")
    except (CoherenceRuleError, AuthorityClientError, OSError) as error:
        raise click.ClickException(str(error)) from error
    click.echo(f"spec coherence: {len(specs)} active specifications, {result.finding_count} review candidates")
    click.echo("No verification or completeness claim. Canonical records are unchanged.")
    if fail_on_findings and result.finding_count:
        ctx.exit(5)


NATIVE_COMMANDS["validate"] = validate_group


@harness_group.command("diagnostic")
@click.option("--harness-id", required=True)
@click.option("--native-context-id", default=None, help="Read only this exact context's immutable binding.")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def harness_diagnostic(ctx: click.Context, harness_id: str, native_context_id: str | None, json_output: bool) -> None:
    """Read local diagnostics; metadata does not qualify actual host behavior."""
    from groundtruth_kb.harness_diagnostic import collect_harness_diagnostic

    try:
        result = collect_harness_diagnostic(_client(ctx), harness_id, native_context_id=native_context_id)
    except ValueError as error:
        raise click.ClickException(str(error)) from error
    _emit(result, json_output)
    if result["status"] == "error":
        ctx.exit(1)


@click.command("assert")
@click.option("--spec", "spec_id", default=None, help="Evaluate one current specification.")
@click.option(
    "--scope",
    "application_scope",
    default=None,
    help=(
        "Application scope to evaluate: gtkb_platform or application:<name>. Default: application:<name> from the "
        "project root's application.toml marker, else gtkb_platform. Records with no scope are evaluated as well "
        "and counted; records of another scope are excluded."
    ),
)
@click.option("--triggered-by", default="cli", help="Label this observation; no execution history is written.")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def native_assert(
    ctx: click.Context, spec_id: str | None, application_scope: str | None, triggered_by: str, json_output: bool
) -> None:
    """Observe current definitions from one selected authority without canonical writes."""
    from groundtruth_kb.assertions import format_summary, run_all_assertions
    from groundtruth_kb.isolation.scope import ApplicationScopeError, select_application_scope

    config = _config(ctx)
    client = _client(ctx, config=config)
    project_root = config.project_root.resolve()
    try:
        scope = select_application_scope(project_root, application_scope)
    except ApplicationScopeError as error:
        raise click.ClickException(f"{error.code}: {error}") from error

    class CurrentSpecifications:
        def get_spec(self, ident: str) -> dict[str, Any]:
            record = _call(ctx, "GET", f"/v1/specifications/{quote(ident, safe='')}", client=client)
            if not isinstance(record, dict) or record.get("id") != ident:
                raise click.ClickException("invalid_response: Expected the selected specification record")
            return record

        def list_specs(self, *, status: str) -> list[dict[str, Any]]:
            records: list[dict[str, Any]] = []
            after: str | None = None
            cursors: set[str] = set()
            identities: set[str] = set()
            while True:
                page = _call(
                    ctx,
                    "GET",
                    "/v1/specifications",
                    client=client,
                    query={"status": status, "after": after, "limit": 1000},
                )
                if not isinstance(page, dict) or not isinstance(page.get("records"), list) or "next_after" not in page:
                    raise click.ClickException("invalid_response: Expected a complete specification page")
                for record in page["records"]:
                    if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
                        raise click.ClickException("invalid_response: Expected specification identities in the page")
                    if record["id"] in identities:
                        raise click.ClickException("invalid_response: Duplicate specification in the selected corpus")
                    identities.add(record["id"])
                    records.append(record)
                next_after = page["next_after"]
                if next_after is None:
                    return records
                if not isinstance(next_after, str) or not next_after or not page["records"] or next_after in cursors:
                    raise click.ClickException("invalid_response: Specification pagination did not advance")
                cursors.add(next_after)
                after = next_after

    summary = run_all_assertions(
        CurrentSpecifications(), project_root, triggered_by=triggered_by, spec_id=spec_id, application_scope=scope
    )
    current = _config(ctx)
    try:
        current_scope = select_application_scope(current.project_root.resolve(), application_scope)
    except ApplicationScopeError:
        current_scope = None
    if (current.authority_url, current.project_root.resolve(), current_scope) != (
        config.authority_url,
        project_root,
        scope,
    ):
        raise click.ClickException(
            "assertion_configuration_changed: The selected authority, project root or application scope changed "
            "during evaluation. Read the current configuration and evaluate again."
        )
    if json_output:
        _emit(summary, True)
    else:
        click.echo(format_summary(summary))
    if summary.get("aggregate_result") != "PASS":
        raise click.exceptions.Exit(1)


NATIVE_COMMANDS["assert"] = native_assert


@projects_group.command("set-authorization")
@click.argument("project_id")
@click.option("--authorization", type=click.Choice(["authorized", "not authorized"]), required=True)
@click.option("--expected-version", type=click.IntRange(1), required=True, help="Current project version.")
@click.option("--actor", required=True)
@click.option("--change-reason", "reason", required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def set_project_authorization(ctx: click.Context, /, project_id: str, json_output: bool, **body: Any) -> None:
    """Apply the owner's explicit ordering choice; existing bridge chains continue."""
    _emit(
        _call(ctx, "PUT", f"/v1/projects/{quote(project_id, safe='')}/authorization", body=body),
        json_output,
        complete=True,
    )


@projects_group.command("retire")
@click.option("--id", "record_id", required=True, help="Active program or execution project to retire.")
@click.option("--reason", required=True, help="Change reason recorded with the retired version.")
@click.option("--expected-version", type=click.IntRange(1), required=True, help="Current project version.")
@click.option("--actor", required=True, help="Attribution recorded with the retired version.")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def retire_project(ctx: click.Context, /, record_id: str, json_output: bool, **body: Any) -> None:
    """Retire one active program or project by status only, with history; authorization, memberships and links stay."""
    _emit(_call(ctx, "POST", f"/v1/projects/{quote(record_id, safe='')}/retire", body=body), json_output, complete=True)


@projects_group.command("readiness")
@click.argument("project_id")
@click.option("--gate", type=click.Choice(["readiness", "closure"]), default="readiness", show_default=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def project_readiness(ctx: click.Context, project_id: str, gate: str, json_output: bool) -> None:
    """Explain whether the project's exact prerequisite outcomes are available."""
    _emit(_call(ctx, "GET", f"/v1/projects/{quote(project_id, safe='')}/readiness", query={"gate": gate}), json_output)


@backlog_group.command("readiness")
@click.argument("work_item_id")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def work_item_readiness(ctx: click.Context, work_item_id: str, json_output: bool) -> None:
    """Explain whether this item's reviewed or committed predecessors are available."""
    _emit(_call(ctx, "GET", f"/v1/work-items/{quote(work_item_id, safe='')}/readiness"), json_output)


@backlog_group.command("retire")
@click.option("--id", "record_id", required=True, help="Open work item to retire.")
@click.option("--reason", required=True, help="Change reason recorded with the retired version.")
@click.option("--expected-version", type=click.IntRange(1), required=True, help="Current work-item version.")
@click.option("--actor", required=True, help="Attribution recorded with the retired version.")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def retire_work_item(ctx: click.Context, /, record_id: str, json_output: bool, **body: Any) -> None:
    """Retire one open work item by status only, with history; its parent, links and notes are preserved."""
    _emit(
        _call(ctx, "POST", f"/v1/work-items/{quote(record_id, safe='')}/retire", body=body), json_output, complete=True
    )


@projects_group.command("move-item")
@click.option("--work-item-id", required=True)
@click.option("--from-project", "source_project_id", required=True)
@click.option("--to-project", "destination_project_id", required=True)
@click.option("--expected-version", type=click.IntRange(1), required=True, help="Current membership version.")
@click.option("--membership-order", type=int, default=None)
@click.option("--actor", required=True)
@click.option("--change-reason", "reason", required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def move_item(ctx: click.Context, /, work_item_id: str, json_output: bool, **body: Any) -> None:
    """Move one open work item atomically, preserving both projects' authorization."""
    _emit(_call(ctx, "POST", f"/v1/work-items/{quote(work_item_id, safe='')}/move", body=body), json_output)


@click.group("context")
def context_group() -> None:
    """Load bounded startup or task-specific current knowledge through the authority service."""


@context_group.command("session")
@click.option("--native-context-id", required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def session_context(ctx: click.Context, native_context_id: str, json_output: bool) -> None:
    """Read an existing binding, current startup requirements and authored baseline."""
    result = _call(ctx, "GET", "/v1/sessions/context", query={"native_context_id": native_context_id})
    if json_output:
        _emit(result, True)
        return
    click.echo("binding:")
    _emit(result["binding"], False, complete=True)
    click.echo(result["scope"])
    for record in result["specifications"]:
        _emit(record, False, complete=True)
    for source in result["baseline"]:
        click.echo(f"{source['path']}:\n{source['content']}")
    for name, observation in result["host_observations"].items():
        click.echo(f"{name}: {observation['status']} - {observation['reason']}")
    for name, route in result["retrieval_routes"].items():
        click.echo(f"{name}: {route}")


def _finalization_command(name: str) -> None:
    def action(ctx: click.Context, /, project_id: str, json_output: bool, **body: Any) -> None:
        result = _call(ctx, "POST", f"/v1/projects/{quote(project_id, safe='')}/{name}", body=body)
        _emit(result, json_output)
        if name != "commit-failed" and result.get("status") == "fresh_verification_required":
            raise click.exceptions.Exit(1)

    command = click.pass_context(action)
    command = click.option("--json", "json_output", is_flag=True)(command)
    if name in {"confirm-commit", "check-commit"}:
        command = click.option("--commit-id", required=True)(command)
        command = click.option("--expected-parent", required=True)(command)
    if name == "check-commit":
        command = click.option("--index-tree", required=True)(command)
    if name == "commit-failed":
        command = click.option("--reason", type=click.Choice(["commit_not_confirmed"]), required=True)(command)
        command = click.option("--evidence", required=True)(command)
    command = click.option("--expected-version", type=click.IntRange(1), required=True)(command)
    command = click.option("--native-context-id", required=True)(command)
    command = click.argument("project_id")(command)
    projects_group.command(name, help="Prepare, confirm, or report failure of the complete project Git commit.")(
        command
    )


for _finalization_operation in ("prepare-commit", "check-commit", "confirm-commit", "commit-failed"):
    _finalization_command(_finalization_operation)


@projects_group.command("commit")
@click.argument("project_id")
@click.option("--native-context-id", required=True)
@click.option("--expected-version", type=click.IntRange(1), required=True)
@click.option("--message-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def commit_project(
    ctx: click.Context,
    project_id: str,
    native_context_id: str,
    expected_version: int,
    message_file: Path,
    json_output: bool,
) -> None:
    """Commit the complete reviewed project through the native service and normal hooks."""
    try:
        message = message_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise click.ClickException("The commit message must be a readable UTF-8 file") from error
    result = _call(
        ctx,
        "POST",
        f"/v1/projects/{quote(project_id, safe='')}/commit",
        timeout=180,
        body={"native_context_id": native_context_id, "expected_version": expected_version, "message": message},
    )
    _emit(result, json_output)
    if result["status"] not in {"confirmed", "already_confirmed"}:
        raise click.exceptions.Exit(1)


@context_group.command("work-item")
@click.argument("work_item_id")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def work_context(ctx: click.Context, work_item_id: str, json_output: bool) -> None:
    """Read current work, linked formal requirements, test instructions and prerequisites together."""
    result = _call(ctx, "GET", f"/v1/work-items/{quote(work_item_id, safe='')}/context")
    if not json_output:
        for key in (
            "program",
            "project",
            "work_item",
            "specifications",
            "test",
            "test_phases",
            "test_plans",
            "predecessors",
            "readiness",
            "work_item_readiness",
        ):
            if result.get(key):
                click.echo(f"{key}:")
                _emit(result[key], False, complete=True)
    else:
        _emit(result, True)


NATIVE_COMMANDS["context"] = context_group


@click.group("service")
def service_group() -> None:
    """Operate or inspect the workstation's native domain service."""


@service_group.command("serve")
@click.option("--port", type=click.IntRange(1, 65535), default=8765, show_default=True)
@click.pass_context
def serve(ctx: click.Context, port: int) -> None:
    """Serve an initialized PostgreSQL domain on IPv4 loopback only."""
    import uvicorn

    from groundtruth_kb.authority_api import create_authority_app
    from groundtruth_kb.native_authority import AuthorityService
    from groundtruth_kb.postgres_kernel import PostgresKernel

    config = _config(ctx)
    kernel = PostgresKernel(config.postgresql)
    with kernel.transaction(read_only=True):
        pass
    uvicorn.run(
        create_authority_app(AuthorityService(kernel), project_root=config.project_root),
        host="127.0.0.1",
        port=port,
        access_log=False,
    )


@click.command("status")
@click.option("--startup", is_flag=True, help="Render the compact startup text from the same collector.")
@click.option("--native-context-id", help="Report this native context's immutable binding (never inferred).")
@click.option("--component", "components", multiple=True, help="Restrict to named components; may be repeated.")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def status(
    ctx: click.Context, startup: bool, native_context_id: str | None, components: tuple[str, ...], json_output: bool
) -> None:
    """Compact read-only operating status from fresh native reads; unavailable facts are reported, never inferred."""
    from groundtruth_kb.operating_status import (
        collect_operating_status,
        format_operating_status_text,
        format_startup_operating_status,
    )

    try:
        report = collect_operating_status(
            _config(ctx), startup=startup, native_context_id=native_context_id, components=components or None
        )
    except ValueError as error:
        raise click.UsageError(str(error)) from error
    if json_output:
        _emit(report.to_json_dict(), True)
    elif startup:
        click.echo(format_startup_operating_status(report))
    else:
        click.echo(format_operating_status_text(report))


@click.group("session")
def native_session_group() -> None:
    """Resolve immutable attribution for the actual native context."""


@native_session_group.command("bind")
@click.option("--native-context-id", required=True)
@click.option("--init-keyword", "init_command", required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def bind_session(ctx: click.Context, /, json_output: bool, **body: Any) -> None:
    """Return the initialization outcome and immutable binding for the received marker."""
    _emit(_call(ctx, "POST", "/v1/sessions/bind", body=body), json_output)


@native_session_group.command("show")
@click.option("--native-context-id", required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def show_session(ctx: click.Context, native_context_id: str, json_output: bool) -> None:
    """Resolve the supplied native context, with no fallback to another session."""
    _emit(_call(ctx, "GET", "/v1/sessions/binding", query={"native_context_id": native_context_id}), json_output)


@native_session_group.command("scratch-teardown")
@click.option("--native-context-id", required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def scratch_teardown(ctx: click.Context, /, json_output: bool, **body: Any) -> None:
    """Remove exactly this context's disposable scratch directory; a partial outcome exits 1."""
    result = _call(ctx, "POST", "/v1/sessions/scratch-teardown", body=body)
    _emit(result, json_output)
    if result["status"] == "partial":
        raise click.exceptions.Exit(1)


@click.group("bridge")
def native_bridge_group() -> None:
    """Deliver disposable bridge messages through native fenced domain operations."""


@native_bridge_group.command("queue")
@click.option("--role", type=click.Choice(["pb", "lo"]), required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def bridge_queue(ctx: click.Context, role: str, json_output: bool) -> None:
    """Report eligible next actions for owner or dispatcher selection."""
    _emit(_call(ctx, "GET", "/v1/bridge/queue", query={"role": role}), json_output)


@native_bridge_group.command("state-report")
@click.option("--json", "json_output", is_flag=True)
@click.option("--markdown", "markdown_output", is_flag=True)
@click.pass_context
def bridge_state_report(ctx: click.Context, json_output: bool, markdown_output: bool) -> None:
    """Report canonical attempts, exact claims and role queues without harness configuration."""
    from groundtruth_kb.bridge.state_report import render_markdown

    if json_output and markdown_output:
        raise click.ClickException("Choose only one output mode: --json or --markdown.")
    report = _call(ctx, "GET", "/v1/bridge/state-report")
    if json_output:
        _emit(report, True)
    else:
        click.echo(render_markdown(report), nl=False)


@native_bridge_group.command("show")
@click.argument("document")
@click.option("--content", is_flag=True, help="Include disposable messages for the active attempt.")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def bridge_show(ctx: click.Context, document: str, content: bool, json_output: bool) -> None:
    """Read canonical attempt state and optionally its available bridge messages."""
    _emit(
        _call(
            ctx, "GET", f"/v1/bridge/{quote(document, safe='')}/show", query={"include_content": str(content).lower()}
        ),
        json_output,
    )


@native_bridge_group.command("check-effects")
@click.option("--native-context-id", required=True)
@click.option("--cwd", required=True, help="Actual absolute working directory of the tool.")
@click.option("--path", "paths", multiple=True, required=True, help="Concrete tool target; repeat for each target.")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def bridge_check_effects(ctx: click.Context, /, json_output: bool, **body: Any) -> None:
    """Check current scratch/implementation scope without granting or recording permission."""
    body["paths"] = list(body["paths"])
    _emit(_call(ctx, "POST", "/v1/bridge/check-effects", body=body), json_output)


@native_bridge_group.command("check-delivery")
@click.argument("document")
@click.option("--version", type=click.IntRange(1), required=True)
@click.option("--native-context-id", required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def bridge_check_delivery(
    ctx: click.Context, document: str, version: int, native_context_id: str, json_output: bool
) -> None:
    """Verify this context's exact assigned delivery, including the purged terminal head."""
    _emit(
        _call(
            ctx,
            "GET",
            f"/v1/bridge/{quote(document, safe='')}/delivery",
            query={"version": version, "native_context_id": native_context_id},
        ),
        json_output,
    )


@native_bridge_group.command("claim")
@click.argument("document")
@click.option("--work-item-id", default=None, help="Required for implementation; omit for an advisory.")
@click.option("--native-context-id", required=True)
@click.option("--expected-version", type=click.IntRange(0), required=True)
@click.option("--status", "intended_status", required=True)
@click.option("--request-id", required=True, help="Reuse only when retrying this exact claim request.")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def claim_bridge(ctx: click.Context, /, document: str, json_output: bool, **body: Any) -> None:
    """Reserve one exact successor slot for 600 seconds, without renewal."""
    _emit(_call(ctx, "POST", f"/v1/bridge/{quote(document, safe='')}/claim", body=body), json_output)


def _fence_command(name: str) -> None:
    @native_bridge_group.command(name)
    @click.argument("document")
    @click.option("--native-context-id", required=True)
    @click.option("--fence", type=click.IntRange(1), required=True)
    @click.option("--json", "json_output", is_flag=True)
    @click.pass_context
    def action(ctx: click.Context, /, document: str, json_output: bool, **body: Any) -> None:
        """Check or release only the exact current artifact claim."""
        _emit(_call(ctx, "POST", f"/v1/bridge/{quote(document, safe='')}/{name}", body=body), json_output)


for _operation in ("check", "release", "worktree"):
    _fence_command(_operation)


@native_bridge_group.command("publish-work")
@click.argument("document")
@click.option("--native-context-id", required=True)
@click.option("--fence", type=click.IntRange(1), required=True)
@click.option("--preimages-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def publish_work(ctx: click.Context, /, document: str, preimages_file: Path, json_output: bool, **body: Any) -> None:
    """Publish only the claimed artifacts from this context's registered checkout."""
    body["expected_artifacts"] = _fields(preimages_file)
    _emit(_call(ctx, "POST", f"/v1/bridge/{quote(document, safe='')}/publish-work", body=body), json_output)


@native_bridge_group.command("deliver")
@click.argument("document")
@click.option("--native-context-id", required=True)
@click.option("--fence", type=click.IntRange(1), required=True)
@click.option("--content-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--headless", is_flag=True, help="Use the headless BLOCKED response when a NEW proposal is unauthorized.")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def deliver_bridge(
    ctx: click.Context, /, document: str, content_file: Path, headless: bool, json_output: bool, **body: Any
) -> None:
    """Publish the author's complete UTF-8 bytes and consume the exact claim."""
    try:
        body["content"] = content_file.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as error:
        raise click.ClickException("The authored bridge message must be a readable UTF-8 file") from error
    body["mode"] = "headless" if headless else "interactive"
    _emit(_call(ctx, "POST", f"/v1/bridge/{quote(document, safe='')}/deliver", body=body), json_output)


@native_bridge_group.command("artifacts")
@click.argument("document")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def artifact_snapshot(ctx: click.Context, document: str, json_output: bool) -> None:
    """Identify current Git-normalized artifact bytes; this is not a verdict."""
    _emit(_call(ctx, "GET", f"/v1/bridge/{quote(document, safe='')}/artifacts"), json_output)


@native_bridge_group.command("abandon")
@click.argument("document")
@click.option("--native-context-id", required=True)
@click.option("--expected-version", type=click.IntRange(0), required=True)
@click.option("--reason", required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def abandon_attempt(ctx: click.Context, /, document: str, json_output: bool, **body: Any) -> None:
    """Abandon a broken or invalidated attempt when no live claim remains."""
    _emit(_call(ctx, "POST", f"/v1/bridge/{quote(document, safe='')}/abandon", body=body), json_output)


NATIVE_COMMANDS.update(session=native_session_group, bridge=native_bridge_group, status=status)


@service_group.command("status")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def service_status(ctx: click.Context, json_output: bool) -> None:
    """Read status from the configured service; never open a client database."""
    _emit(_call(ctx, "GET", "/v1/status"), json_output)


@click.group("dashboard")
def dashboard_group() -> None:
    """Generate local dashboard observations from the selected native authority."""


def _refresh_dashboard(
    ctx: click.Context,
    db_path: Path | None,
    runtime_root: Path | None,
    json_output: bool,
    *,
    schema_only: bool = False,
    probe_live: bool = False,
) -> None:
    from groundtruth_kb.dashboard import initialize_dashboard, resolve_dashboard_paths

    config = _config(ctx)
    paths = resolve_dashboard_paths(config, db_path=db_path, runtime_root=runtime_root)
    try:
        result = initialize_dashboard(paths, config, schema_only=schema_only, probe_live=probe_live)
    except (OSError, ValueError) as error:
        raise click.ClickException(str(error)) from error
    payload = {
        **result,
        "project_root": str(paths.project_root),
        "runtime_root": str(paths.runtime_root),
        "dashboard_db": str(paths.db_path),
    }
    if not schema_only:
        payload.update(
            landing_page=str(paths.runtime_root / "index.html"),
            grafana_dashboard=str(paths.dashboards_dir / "gtkb-dashboard.json"),
        )
    _emit(payload, json_output)


@dashboard_group.command("init")
@click.option("--schema-only", is_flag=True, help="Initialize derived schema without collecting or publishing data.")
@click.option("--db-path", type=click.Path(path_type=Path))
@click.option("--runtime-root", type=click.Path(path_type=Path))
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def dashboard_init(
    ctx: click.Context, db_path: Path | None, runtime_root: Path | None, json_output: bool, schema_only: bool
) -> None:
    """Create derived reporting data and Grafana assets without starting services."""
    _refresh_dashboard(ctx, db_path, runtime_root, json_output, schema_only=schema_only)


@dashboard_group.command("refresh")
@click.option("--probe-live", is_flag=True, help="Also read live service, bridge and GitHub workflow observations.")
@click.option("--db-path", type=click.Path(path_type=Path))
@click.option("--runtime-root", type=click.Path(path_type=Path))
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def dashboard_refresh(
    ctx: click.Context, db_path: Path | None, runtime_root: Path | None, json_output: bool, probe_live: bool
) -> None:
    """Refresh native observations and derived display assets without selecting work."""
    _refresh_dashboard(ctx, db_path, runtime_root, json_output, probe_live=probe_live)


@dashboard_group.command("install")
@click.option("--grafana-home", type=click.Path(path_type=Path))
@click.option("--skip-download", is_flag=True)
@click.option("--skip-plugin", is_flag=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def dashboard_install(
    ctx: click.Context, grafana_home: Path | None, skip_download: bool, skip_plugin: bool, json_output: bool
) -> None:
    """Install Grafana OSS and its SQLite plugin into the selected local installation."""
    from groundtruth_kb.dashboard import install_grafana, resolve_dashboard_paths

    paths = resolve_dashboard_paths(_config(ctx), grafana_home=grafana_home)
    try:
        binary = install_grafana(paths, skip_download=skip_download, skip_plugin=skip_plugin)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        raise click.ClickException(str(error)) from error
    _emit(
        {"status": "Grafana installed", "grafana_binary": str(binary), "plugin_install_skipped": skip_plugin},
        json_output,
    )


@dashboard_group.command("start")
@click.option("--db-path", type=click.Path(path_type=Path))
@click.option("--runtime-root", type=click.Path(path_type=Path))
@click.option("--grafana-home", type=click.Path(path_type=Path))
@click.option("--grafana-port", type=click.IntRange(1, 65535), default=3000, show_default=True)
@click.option("--refresh-port", type=click.IntRange(1, 65535), default=8766, show_default=True)
@click.option("--interval-minutes", type=click.IntRange(min=1), default=60, show_default=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def dashboard_start(
    ctx: click.Context,
    db_path: Path | None,
    runtime_root: Path | None,
    grafana_home: Path | None,
    grafana_port: int,
    refresh_port: int,
    interval_minutes: int,
    json_output: bool,
) -> None:
    """Start the local display and Grafana, returning only after readiness checks."""
    from groundtruth_kb.config import _find_config
    from groundtruth_kb.dashboard import resolve_dashboard_paths, start_dashboard

    config = _config(ctx)
    paths = resolve_dashboard_paths(config, db_path=db_path, runtime_root=runtime_root, grafana_home=grafana_home)
    selected_config = (ctx.find_root().obj or {}).get("config") or _find_config()
    try:
        result = start_dashboard(
            paths,
            config,
            grafana_port=grafana_port,
            refresh_port=refresh_port,
            interval_minutes=interval_minutes,
            config_path=selected_config,
        )
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        raise click.ClickException(str(error)) from error
    _emit(asdict(result), json_output)


@dashboard_group.command("stop")
@click.option("--runtime-root", type=click.Path(path_type=Path))
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def dashboard_stop(ctx: click.Context, runtime_root: Path | None, json_output: bool) -> None:
    """End every process of this runtime's dashboard job and report each one."""
    from groundtruth_kb.dashboard import resolve_dashboard_paths, stop_dashboard

    try:
        stopped = stop_dashboard(resolve_dashboard_paths(_config(ctx), runtime_root=runtime_root))
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        raise click.ClickException(str(error)) from error
    _emit({"stopped": [asdict(process) for process in stopped]}, json_output)


@dashboard_group.command("serve")
@click.option("--db-path", type=click.Path(path_type=Path))
@click.option("--runtime-root", type=click.Path(path_type=Path))
@click.option("--port", type=click.IntRange(1, 65535), default=8766, show_default=True)
@click.option("--grafana-port", type=click.IntRange(1, 65535), default=3000, show_default=True)
@click.option("--interval-minutes", type=click.IntRange(min=1), default=60, show_default=True)
@click.pass_context
def dashboard_serve(
    ctx: click.Context,
    db_path: Path | None,
    runtime_root: Path | None,
    port: int,
    grafana_port: int,
    interval_minutes: int,
) -> None:
    """Serve the installed display on loopback, refreshing the selected native authority."""
    from groundtruth_kb.config import _find_config
    from groundtruth_kb.dashboard import resolve_dashboard_paths
    from groundtruth_kb.dashboard_service import run_service

    config = _config(ctx)
    paths = resolve_dashboard_paths(config, db_path=db_path, runtime_root=runtime_root)
    selected_config = (ctx.find_root().obj or {}).get("config") or _find_config()
    try:
        run_service(
            config,
            paths.db_path,
            paths.runtime_root,
            port=port,
            interval_minutes=interval_minutes,
            config_path=selected_config,
            grafana_port=grafana_port,
        )
    except (OSError, ValueError, RuntimeError) as error:
        raise click.ClickException(str(error)) from error


NATIVE_COMMANDS["dashboard"] = dashboard_group


@click.group("services")
def services_group() -> None:
    """Start, stop and inspect GT-KB's local services (authority, home, dashboard, ollama, postgresql)."""


def _services_installation(ctx: click.Context) -> Installation:
    from groundtruth_kb.services_control import installation_from_config  # local import keeps CLI start-up light

    config = _config(ctx)
    return installation_from_config(Path(config.project_root), config.authority_url)


@services_group.command("status")
@click.argument("name", required=False)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def services_status(ctx: click.Context, name: str | None, json_output: bool) -> None:
    """Report each service's state and which actions apply."""
    from groundtruth_kb.services_control import ServiceControlError, as_json, status

    try:
        _emit(as_json(status(_services_installation(ctx), only=name)), json_output)
    except (ServiceControlError, OSError, subprocess.SubprocessError) as error:
        raise click.ClickException(str(error)) from error


@services_group.command("start")
@click.argument("name")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def services_start(ctx: click.Context, name: str, json_output: bool) -> None:
    """Start one service and wait for its readiness where it has one."""
    from groundtruth_kb.services_control import ServiceControlError, start

    try:
        _emit(start(_services_installation(ctx), name), json_output)
    except (ServiceControlError, OSError, subprocess.SubprocessError) as error:
        raise click.ClickException(str(error)) from error


@services_group.command("stop")
@click.argument("name")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def services_stop(ctx: click.Context, name: str, json_output: bool) -> None:
    """Stop one service so that it stays stopped (its logon task is paused until the next start)."""
    from groundtruth_kb.services_control import ServiceControlError, stop

    try:
        _emit(stop(_services_installation(ctx), name), json_output)
    except (ServiceControlError, OSError, subprocess.SubprocessError) as error:
        raise click.ClickException(str(error)) from error


NATIVE_COMMANDS["services"] = services_group


@click.group("home")
def home_group() -> None:
    """GT-KB Home: the DeepSeek Harness Web UI as GT-KB's primary interface (127.0.0.1:3080)."""


def _home_script(ctx: click.Context) -> tuple[Path, Path]:
    from groundtruth_kb.services_control import installation_from_config

    installation = installation_from_config(Path(_config(ctx).project_root), None)
    return installation.python, installation.home_script


def _home(ctx: click.Context, action: str) -> subprocess.CompletedProcess[str]:
    python, script = _home_script(ctx)
    if not script.is_file():
        raise click.ClickException(f"The GT-KB Home launcher is missing: {script}")
    return subprocess.run(
        [str(python), "-B", str(script), action],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )


@home_group.command("start")
@click.pass_context
def home_start(ctx: click.Context) -> None:
    """Start the Home server after proving its GT-KB guard and plugin are active."""
    result = _home(ctx, "start")
    click.echo(result.stdout.strip() or result.stderr.strip())
    ctx.exit(result.returncode)


@home_group.command("stop")
@click.pass_context
def home_stop(ctx: click.Context) -> None:
    """Stop the Home server (graceful teardown first)."""
    result = _home(ctx, "stop")
    click.echo(result.stdout.strip() or result.stderr.strip())
    ctx.exit(result.returncode)


@home_group.command("status")
@click.pass_context
def home_status(ctx: click.Context) -> None:
    """Report whether the Home server is running and answering."""
    result = _home(ctx, "status")
    click.echo(result.stdout.strip() or result.stderr.strip())
    ctx.exit(result.returncode)


@home_group.command("open")
@click.pass_context
def home_open(ctx: click.Context) -> None:
    """Open the Home UI in the default browser, starting the server first if needed."""
    import webbrowser

    if _home(ctx, "url").returncode != 0 and _home(ctx, "start").returncode != 0:
        raise click.ClickException("The GT-KB Home server could not be started; see: gt home status")
    result = _home(ctx, "url")
    if result.returncode != 0:
        raise click.ClickException("The GT-KB Home server is not running; see: gt home status")
    webbrowser.open(result.stdout.strip())  # the loopback sign-in URL goes only to the browser, never to the terminal
    click.echo("Opened GT-KB Home: http://127.0.0.1:3080/")


NATIVE_COMMANDS["home"] = home_group


@click.group("core-specs")
def core_specs_group() -> None:
    """Read missing application specifications and apply explicit owner answers."""


def _core_project(client: AuthorityClient, project_id: str | None, project_name: str | None) -> str:
    if bool(project_id) == bool(project_name):
        raise click.ClickException("Supply exactly one of --project-id or --project-name")
    if project_id:
        return project_id
    rows: list[dict[str, Any]] = []
    after = None
    while True:
        page = client.request(
            "GET", "/v1/projects", query={"kind": "project", "search": project_name, "limit": 1000, "after": after}
        )
        rows.extend(row for row in page["records"] if row["name"] == project_name)
        after = page["next_after"]
        if after is None:
            break
    if len(rows) != 1:
        raise click.ClickException("The exact project name must resolve to one execution project; use its ID")
    return str(rows[0]["id"])


def _core_read(ctx: click.Context, project_id: str | None, project_name: str | None, opt_out: bool) -> dict[str, Any]:
    from groundtruth_kb.project.core_spec_intake import intake_enabled, intake_status

    if opt_out:
        return {"status": "disabled"}
    try:
        config = _config(ctx)
        if not intake_enabled(config.project_root):
            return {"status": "disabled"}
        client = _client(ctx, config=config)
        return intake_status(client, _core_project(client, project_id, project_name))
    except (AuthorityClientError, ValueError, OSError) as error:
        raise click.ClickException(f"{getattr(error, 'code', 'invalid_intake')}: {error}") from error


@core_specs_group.command("status")
@click.option("--project-id")
@click.option("--project-name")
@click.option("--json", "json_output", is_flag=True)
@click.option("--no-fail", is_flag=True, help="Report an incomplete baseline without a failing exit code.")
@click.option("--opt-out-core-spec-intake", is_flag=True)
@click.pass_context
def core_specs_status(
    ctx: click.Context,
    project_id: str | None,
    project_name: str | None,
    json_output: bool,
    no_fail: bool,
    opt_out_core_spec_intake: bool,
) -> None:
    result = _core_read(ctx, project_id, project_name, opt_out_core_spec_intake)
    if json_output or result.get("status") == "disabled":
        _emit(result, json_output)
    else:
        state = "complete" if result["complete"] else "incomplete"
        click.echo(f"{result['project']['id']}: {state} ({result['completed_slots']}/{result['total_slots']})")
    if result.get("complete") is False and not no_fail:
        ctx.exit(1)


@core_specs_group.command("next-question")
@click.option("--project-id")
@click.option("--project-name")
@click.option("--json", "json_output", is_flag=True)
@click.option("--opt-out-core-spec-intake", is_flag=True)
@click.pass_context
def core_specs_next_question(
    ctx: click.Context,
    project_id: str | None,
    project_name: str | None,
    json_output: bool,
    opt_out_core_spec_intake: bool,
) -> None:
    result = _core_read(ctx, project_id, project_name, opt_out_core_spec_intake)
    if result.get("status") == "disabled":
        _emit(result, json_output)
        return
    slot = next((row for row in result["slots"] if not row["complete"]), None)
    value = {
        "project": result["project"],
        "complete": result["complete"],
        "slot": slot["name"] if slot else None,
        "question": slot["prompt"] if slot else None,
        "spec_id": slot["spec_id"] if slot else None,
        "expected_version": slot["version"] if slot else None,
    }
    if json_output:
        _emit(value, True)
    elif slot:
        click.echo(f"{slot['label']} ({slot['name']}): {slot['prompt']}")
    else:
        click.echo(f"{result['project']['id']}: complete")


@core_specs_group.command("answer")
@click.option("--project-id", required=True)
@click.option("--slot", required=True)
@click.option("--value", default="")
@click.option("--source", type=click.Choice(["owner_stated", "not_applicable"]), default="owner_stated")
@click.option("--spec-id")
@click.option("--expected-version", type=click.IntRange(0), required=True)
@click.option("--actor", required=True)
@click.option("--reason", required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def core_specs_answer(ctx: click.Context, /, json_output: bool, **values: Any) -> None:
    from groundtruth_kb.project.core_spec_intake import mark_slot_complete

    try:
        result = mark_slot_complete(_client(ctx), **values)
    except (AuthorityClientError, ValueError, OSError) as error:
        raise click.ClickException(f"{getattr(error, 'code', 'invalid_intake')}: {error}") from error
    _emit(result, json_output)


NATIVE_COMMANDS["core-specs"] = core_specs_group


@click.group("project")
def application_project_group() -> None:
    """Initialize and inspect files for an explicitly selected application project."""


@application_project_group.command("init")
@click.argument("application")
@click.option("--project-id", required=True)
@click.option("--host-root", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True)
@click.option("--profile", type=click.Choice(["local-only", "dual-agent", "dual-agent-webapp"]), default="local-only")
@click.option("--owner", required=True)
@click.option("--copyright", "copyright_notice", default="", help="Copyright notice written into created files.")
@click.option(
    "--cloud-provider",
    type=click.Choice(["none", "azure", "aws", "gcp"]),
    default="none",
    help="Infrastructure stubs for the dual-agent-webapp profile.",
)
@click.option(
    "--harness", "harnesses", multiple=True, help="Explicit configuration profiles; these select no agent role."
)
@click.option("--include-ci/--no-include-ci", default=True)
@click.option("--seed-example/--no-seed-example", default=False)
@click.option("--integrations/--no-integrations", default=False, help="Optional Dependabot and CodeRabbit files.")
@click.option("--python-version", default="3.11", show_default=True, help="Python version for generated CI.")
@click.option(
    "--spec-scaffold",
    type=click.Choice(["minimal", "full"]),
    default=None,
    help="Write inferred starter specifications for the project through the authority.",
)
@click.option("--opt-out-core-spec-intake", is_flag=True)
@click.option("--dry-run", is_flag=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def application_project_init(
    ctx: click.Context, /, application: str, host_root: Path, dry_run: bool, json_output: bool, **options: Any
) -> None:
    """Create application files for an explicitly selected project; no commit, no implicit writes."""
    from groundtruth_kb.isolation.registry_check import application_slot_path
    from groundtruth_kb.project.scaffold import ScaffoldOptions, initialize_application, plan_scaffold

    try:
        client = _client(ctx)
        root = host_root.resolve(strict=True)
        selected = ScaffoldOptions(
            project_name=application,
            target_dir=application_slot_path(root, application),
            gt_kb_root=root,
            authority_url=client.url,
            **options,
        )
        plan = plan_scaffold(selected)
        if dry_run:
            result: dict[str, Any] = {
                "status": "preview",
                "project_id": plan.project["id"],
                "repository_ref": plan.project["repository_ref"],
                "target": str(plan.options.target_dir),
                "paths": sorted(plan.files),
                "generated_paths": list(plan.generated_paths),
                "specifications": [row["id"] for row in plan.specifications],
                "initial_question": plan.initial_question,
                "canonical_writes": 0,
                "commits": 0,
            }
        else:
            created = initialize_application(selected, plan=plan)
            result = {
                "status": "created",
                "project_id": created.project["id"],
                "repository_ref": created.project["repository_ref"],
                "target": str(created.target),
                "paths": list(created.paths),
                "generated_paths": list(created.generated_paths),
                "specifications": created.specifications.to_json_dict() if created.specifications else None,
                "specification_error": created.specification_error,
                "initial_question": created.initial_question,
                "intake": created.intake,
                "canonical_writes": created.canonical_writes,
                "commits": created.commits,
                "warnings": list(created.warnings),
            }
    except (AuthorityClientError, ValueError, OSError) as error:
        if json_output:
            _emit(
                {
                    "status": "refused",
                    "error": {"code": getattr(error, "code", "invalid_scaffold"), "message": str(error)},
                },
                True,
            )
            ctx.exit(1)
        raise click.ClickException(str(error)) from error
    if json_output:
        _emit(result, True)
        return
    click.echo(f"{result['status']}: {result['target']}")
    for warning in result.get("warnings", []):
        click.echo(f"warning: {warning}", err=True)
    if result["initial_question"]:
        click.echo(result["initial_question"]["prompt"])


@application_project_group.group("chroma")
def application_project_chroma() -> None:
    """Manage the application's disposable search cache derived from the authority."""


@application_project_chroma.command("regenerate")
@click.option("--dir", "target_dir", default=".", help="Application directory (default: cwd).")
@click.option("--scope", "application_scope", default=None, help="Explicit application scope to index.")
@click.option("--dry-run", is_flag=True, default=False, help="Report what would be regenerated without writing.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
def application_project_chroma_regenerate(
    target_dir: str, application_scope: str | None, dry_run: bool, json_output: bool
) -> None:
    """Rebuild the optional ChromaDB cache from the authority's current records."""
    from groundtruth_kb.project.chroma import regenerate

    try:
        result = regenerate(Path(target_dir), dry_run=dry_run, application_scope=application_scope)
    except (AuthorityClientError, FileNotFoundError, OSError, ValueError) as error:
        raise click.ClickException(f"{getattr(error, 'code', 'invalid_cache_target')}: {error}") from error
    if json_output:
        _emit(result.to_json_dict(), True)
    else:
        click.echo(f"ChromaDB cache {result.status}: {result.chroma_path}")
        click.echo(f"  authority: {result.authority_url} ({result.application_scope})")
        if result.removed_paths:
            click.echo(f"  stale files replaced: {len(result.removed_paths)}")
        if result.indexed:
            click.echo(f"  indexed records: {result.indexed}")
        for message in result.errors:
            click.echo(f"  error: {message}", err=True)
    if result.status == "skipped":
        raise SystemExit(2)
    if result.status == "error":
        raise SystemExit(1)


@click.command("specs")
@click.option("--project-id", required=True)
@click.option("--profile", type=click.Choice(["minimal", "full"]), default="minimal", show_default=True)
@click.option("--apply/--dry-run", "apply_", default=False, help="Write the starter set (default: dry-run).")
@click.option("--actor", default="scaffold-generator", show_default=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def scaffold_specs_cmd(
    ctx: click.Context, project_id: str, profile: str, apply_: bool, actor: str, json_output: bool
) -> None:
    """Generate a starter set of inferred specifications for one execution project."""
    from groundtruth_kb.project.spec_scaffold import scaffold_config, scaffold_specs

    try:
        report = scaffold_specs(_client(ctx), project_id, scaffold_config(profile), dry_run=not apply_, actor=actor)
    except (AuthorityClientError, ValueError, OSError) as error:
        raise click.ClickException(f"{getattr(error, 'code', 'invalid_scaffold')}: {error}") from error
    if json_output:
        _emit(report.to_json_dict(), True)
        return
    mode = "DRY RUN" if report.dry_run else "APPLIED"
    click.echo(f"Scaffold specs - project={project_id} profile={profile} - {mode}")
    click.echo(f"  generated specs: {len(report.generated)}")
    click.echo(f"  skipped specs:   {len(report.skipped)}")
    click.echo(f"  quality:         {report.quality_summary}")
    for row in report.skipped:
        click.echo(f"  - skipped {row['id']} (handle={row['handle']}): {row['reason']}")
    for row in report.low_quality_warnings:
        click.echo(f"  - low quality {row['id']}: tier={row['tier']} score={row['score']}")
    for spec in report.generated:
        click.echo(f"  - {spec['id']}: {spec['title']}  [{spec['quality']['tier']}]")


@application_project_group.command("doctor")
@click.option("--project-id", required=True)
@click.option("--host-root", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def application_project_doctor(ctx: click.Context, project_id: str, host_root: Path, json_output: bool) -> None:
    from groundtruth_kb.project.doctor import format_native_doctor_report, inspect_native_application

    try:
        result = inspect_native_application(_client(ctx), project_id, host_root)
    except (AuthorityClientError, ValueError, OSError) as error:
        if json_output:
            _emit(
                {
                    "status": "unavailable",
                    "error": {"code": getattr(error, "code", "invalid_application"), "message": str(error)},
                },
                True,
            )
            ctx.exit(1)
        raise click.ClickException(str(error)) from error
    if json_output:
        _emit(result, True)
    else:
        click.echo(format_native_doctor_report(result))
    if result["overall"] == "fail":
        ctx.exit(1)


@application_project_group.command("classify-tree")
@click.option(
    "--dir",
    "target",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Tree root to classify.",
)
@click.option(
    "--output", type=click.Path(dir_okay=False, path_type=Path), help="Write the report here instead of stdout."
)
@click.option(
    "--format", "report_format", type=click.Choice(["markdown", "json"]), default="markdown", show_default=True
)
@click.option("--max-depth", type=int, default=10, show_default=True)
@click.option("--ignore-glob", "ignore_globs", multiple=True, help="Additional ignore glob; may be repeated.")
def classify_tree(
    target: Path, output: Path | None, report_format: str, max_depth: int, ignore_globs: tuple[str, ...]
) -> None:
    """Classify every path of a tree against the target's current declarations; read-only, no authority needed.

    The selected target's own declaration source is consulted first (the platform registry or the application's
    artifact-boundary registry); the template ownership map answers only for paths no current declaration covers.
    Undeclared and unreadable paths are reported as findings; a finding grants no ownership or authorization.
    """
    from groundtruth_kb import __version__
    from groundtruth_kb.project.ownership import (
        _DEFAULT_IGNORE_GLOBS,
        classify_target,
        render_classification_report_json,
        render_classification_report_markdown,
    )

    classification = classify_target(
        target.resolve(), max_depth=max_depth, ignore_globs=(*_DEFAULT_IGNORE_GLOBS, *ignore_globs)
    )
    render = render_classification_report_json if report_format == "json" else render_classification_report_markdown
    report = render(
        classification.rows,
        gt_kb_version=__version__,
        target_tree=classification.target,
        declaration_source=classification.declaration_source,
    )
    if output is None:
        click.echo(report, nl=False)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    findings = sum(1 for row in classification.rows if row.finding)
    click.echo(
        f"{len(classification.rows)} paths classified, {findings} findings "
        f"(declaration source: {classification.declaration_source.kind}): {output}"
    )


@application_project_group.command("upgrade")
@click.argument("application")
@click.option("--project-id", required=True)
@click.option("--host-root", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True)
@click.option(
    "--harness", "harnesses", multiple=True, help="Configuration profiles to refresh; default: those present."
)
@click.option("--apply", "apply_", is_flag=True, help="Replace managed files (default: preview only).")
@click.option("--recover", is_flag=True, help="Restore committed managed files from the application's HEAD.")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def application_project_upgrade(
    ctx: click.Context,
    application: str,
    project_id: str,
    host_root: Path,
    harnesses: tuple[str, ...],
    apply_: bool,
    recover: bool,
    json_output: bool,
) -> None:
    """Preview, apply or recover managed application files from the host baseline; no commit."""
    from groundtruth_kb.project.application_upgrade import (
        LocalWorkError,
        MalformedInputError,
        UpgradeOptions,
        apply_upgrade,
        plan_upgrade,
    )
    from groundtruth_kb.project.application_upgrade import recover as recover_managed

    if apply_ and recover:
        raise click.UsageError("--apply and --recover are mutually exclusive")
    try:
        options = UpgradeOptions(
            application=application,
            project_id=project_id,
            gt_kb_root=host_root.resolve(strict=True),
            authority_url=_client(ctx).url,
            harnesses=tuple(harnesses),
        )
        if recover:
            result: dict[str, Any] = recover_managed(options)
        else:
            plan = plan_upgrade(options)
            result = {"status": "preview", **plan.to_json_dict(), "canonical_writes": 0, "commits": 0}
            if apply_:
                result = {**result, **apply_upgrade(plan)}
    except MalformedInputError as error:
        _refuse(ctx, json_output, error.code, str(error), 4)
    except LocalWorkError as error:
        _refuse(ctx, json_output, error.code, str(error), 2)
    except (AuthorityClientError, ValueError, OSError) as error:
        _refuse(ctx, json_output, getattr(error, "code", "invalid_upgrade"), str(error), 1)
    if json_output:
        _emit(result, True)
        return
    click.echo(f"{result['status']}: {result['target']}")
    for action in result.get("actions", []):
        preserved = (
            f" (preserving {action['preserved_entries']} unmanaged entries)" if action["preserved_entries"] else ""
        )
        click.echo(f"  [{action['action'].upper()}] {action['path']} - {action['reason']}{preserved}")
    for key in ("restore", "derived", "written", "removed"):
        for path in result.get(key, []):
            click.echo(f"  {key}: {path}")


def _refuse(ctx: click.Context, json_output: bool, code: str, message: str, exit_code: int) -> None:
    if json_output:
        _emit({"status": "refused", "error": {"code": code, "message": message}}, True)
        ctx.exit(exit_code)
    click.echo(f"Error: {code}: {message}", err=True)
    ctx.exit(exit_code)


NATIVE_COMMANDS["project"] = application_project_group


@click.group("design")
def design_group() -> None:
    """Inspect local Claude Design handoffs; nothing is published."""


@design_group.command("inspect")
@click.argument("handoff", type=click.Path(exists=True, path_type=Path))
@click.option("--date", default=None, help="Handoff date (ISO); today's date when omitted.")
@click.option("--session-id", default=None, help="Session that inspected the handoff, when one is bound.")
@click.option("--owner-decision", default=None, help="Triage outcome text to include in the record.")
@click.option("--notes", default=None, help="Inspection notes to include in the record.")
@click.option("--json", "json_output", is_flag=True, help="Emit the complete report as canonical JSON.")
def design_inspect(
    handoff: Path,
    date: str | None,
    session_id: str | None,
    owner_decision: str | None,
    notes: str | None,
    json_output: bool,
) -> None:
    """Inspect a local handoff (.zip or directory): file list, sizes, D1 format warnings; publishes nothing.

    Raw design bytes are never read into the record. A path that is neither a .zip file nor a directory is refused.
    """
    from datetime import date as calendar_date

    from groundtruth_kb.design_import import build_inspection_report

    try:
        report = build_inspection_report(
            handoff,
            date=date or calendar_date.today().isoformat(),
            session_id=session_id,
            owner_decision=owner_decision,
            notes=notes,
        )
    except ValueError as error:
        raise click.BadParameter(str(error), param_hint="'HANDOFF'") from error
    if json_output:
        _emit(report.to_json_dict(), True)
        return
    click.echo(report.content, nl=False)
    if report.redaction_notes:
        click.echo(f"Redacted: {report.redaction_notes}")


NATIVE_COMMANDS["design"] = design_group


@click.group("kb")
def kb_group() -> None:
    """Read-only knowledge-base maintenance over the selected authority; nothing here writes."""


@kb_group.command("reconcile")
@click.option("--orphans", "run_orphans", is_flag=True, help="Run the orphaned-assertion detector.")
@click.option("--stale", "run_stale", is_flag=True, help="Run the stale-spec detector (changed_at windows).")
@click.option("--authority", "run_authority", is_flag=True, help="Run the authority-conflict detector.")
@click.option("--duplicates", "run_duplicates", is_flag=True, help="Run the duplicate-spec detector.")
@click.option("--provisionals", "run_provisionals", is_flag=True, help="Run the expired-provisional detector.")
@click.option("--all", "run_all", is_flag=True, help="Run every detector; also the default when none is named.")
@click.option(
    "--stale-days",
    type=click.IntRange(0),
    default=90,
    show_default=True,
    help="A spec unchanged for at least this many days may be stale.",
)
@click.option(
    "--activity-days",
    type=click.IntRange(0),
    default=30,
    show_default=True,
    help="Another change in the same section within this many days counts as section activity.",
)
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Root for orphaned-assertion file resolution; defaults to the configured project root.",
)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def kb_reconcile(
    ctx: click.Context,
    /,
    run_orphans: bool,
    run_stale: bool,
    run_authority: bool,
    run_duplicates: bool,
    run_provisionals: bool,
    run_all: bool,
    stale_days: int,
    activity_days: int,
    project_root: Path | None,
    json_output: bool,
) -> None:
    """Report provenance drift in current specifications; findings are reports, never a gate or a write.

    Detectors run in the canonical order orphans, stale, authority, duplicates, provisionals over the active
    corpus read from the selected authority. The exit code is 0 whether or not findings exist; an unavailable
    authority is an error.
    """
    from groundtruth_kb.reconciliation import (
        DETECTOR_CATEGORIES,
        NativeSpecSource,
        format_report_text,
        run_detectors,
    )

    config = _config(ctx)
    chosen = dict(
        zip(
            DETECTOR_CATEGORIES,
            (run_orphans, run_stale, run_authority, run_duplicates, run_provisionals),
            strict=True,
        )
    )
    if run_all or not any(chosen.values()):
        selected = list(DETECTOR_CATEGORIES)
    else:
        selected = [category for category, flag in chosen.items() if flag]
    root = (project_root if project_root is not None else config.project_root).resolve()
    try:
        reports = run_detectors(
            NativeSpecSource(_client(ctx, config=config)),
            selected,
            project_root=root,
            staleness_threshold_days=stale_days,
            section_activity_days=activity_days,
        )
    except AuthorityClientError as error:
        details = "\n" + canonical_json_bytes(error.details).decode("utf-8").strip() if error.details else ""
        raise click.ClickException(f"{error.code}: {error}{details}") from error
    if json_output:
        _emit(
            {
                "project_root": str(root),
                "reports": [
                    {"category": report.category, "finding_count": len(report.findings), "findings": report.findings}
                    for report in reports
                ],
                "total_findings": sum(len(report.findings) for report in reports),
            },
            True,
        )
        return
    click.echo(format_report_text(reports), nl=False)


NATIVE_COMMANDS["kb"] = kb_group
