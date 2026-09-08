"""Ordinary CLI commands for a configured native authority service."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import quote

import click

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig
from groundtruth_kb.postgres_kernel import canonical_json_bytes, parse_json_bytes


def _config(ctx: click.Context) -> GTConfig:
    return GTConfig.load(config_path=(ctx.find_root().obj or {}).get("config"))


def _client(ctx: click.Context) -> AuthorityClient:
    config = _config(ctx)
    if not config.authority_url:
        raise click.ClickException("No authority_url is configured")
    return AuthorityClient(config.authority_url)


def _call(ctx: click.Context, method: str, path: str, **kwargs: Any) -> Any:
    try:
        return _client(ctx).request(method, path, **kwargs)
    except AuthorityClientError as error:
        raise click.ClickException(f"{error.code}: {error}") from error


def _emit(value: Any, json_output: bool) -> None:
    if json_output:
        click.echo(canonical_json_bytes(value).decode("utf-8"), nl=False)
        return
    rows = value if isinstance(value, list) else [value]
    for row in rows:
        if isinstance(row, dict):
            record = row.get("project", row.get("work_item", row))
            label = record.get("title", record.get("name", ""))
            if "id" in record:
                click.echo(f"{record['id']} v{record.get('version', '?')}: {label}")
                if record.get("description"):
                    click.echo(record["description"])
                continue
        click.echo(canonical_json_bytes(row).decode("utf-8"), nl=False)


def _fields(path: Path) -> dict[str, Any]:
    try:
        value = parse_json_bytes(path.read_bytes())
    except Exception as error:
        raise click.ClickException("The fields file must contain a UTF-8 JSON object") from error
    if not isinstance(value, dict):
        raise click.ClickException("The fields file must contain a JSON object")
    return value


def _domain_group(name: str, domain: str) -> click.Group:
    @click.group(name)
    def group() -> None:
        """Read or amend current canonical records through the authority service."""

    @group.command("show")
    @click.argument("record_id")
    @click.option("--json", "json_output", is_flag=True)
    @click.pass_context
    def show(ctx: click.Context, record_id: str, json_output: bool) -> None:
        """Read the current record, including planning relationships where relevant."""
        _emit(_call(ctx, "GET", f"/v1/{domain}/{quote(record_id, safe='')}"), json_output)

    @group.command("list")
    @click.option("--limit", type=click.IntRange(1), default=200, show_default=True)
    @click.option("--after", default=None, help="Continue after this record ID.")
    @click.option("--search", default=None)
    @click.option("--status", default=None)
    @click.option("--kind", type=click.Choice(["program", "project"]), default=None)
    @click.option("--priority", default=None)
    @click.option("--spec-id", default=None)
    @click.option("--plan-id", default=None)
    @click.option("--json", "json_output", is_flag=True)
    @click.pass_context
    def list_records(ctx: click.Context, limit: int, after: str | None, json_output: bool, **filters: Any) -> None:
        """List a bounded set of current records in deterministic ID order."""
        if domain == "work-items" and filters.get("status") is not None:
            filters["resolution_status"] = filters.pop("status")
        records = []
        while len(records) < limit:
            result = _call(
                ctx, "GET", f"/v1/{domain}", query={**filters, "after": after, "limit": min(1000, limit - len(records))}
            )
            records.extend(result["records"])
            after = result["next_after"]
            if not after:
                break
        _emit(records, json_output)

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


NATIVE_COMMANDS = {
    "spec": _domain_group("spec", "specifications"),
    "tests": _domain_group("tests", "tests"),
    "projects": _domain_group("projects", "projects"),
    "backlog": _domain_group("backlog", "work-items"),
    "test-plans": _domain_group("test-plans", "test-plans"),
    "test-phases": _domain_group("test-phases", "test-phases"),
}


@NATIVE_COMMANDS["projects"].command("move-item")
@click.option("--work-item-id", required=True)
@click.option("--from-project", "source_project_id", required=True)
@click.option("--to-project", "destination_project_id", required=True)
@click.option("--expected-version", type=click.IntRange(1), required=True, help="Current membership version.")
@click.option("--membership-order", type=int, default=None)
@click.option("--actor", required=True)
@click.option("--change-reason", "reason", required=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def move_item(ctx: click.Context, work_item_id: str, json_output: bool, **body: Any) -> None:
    """Move one open work item atomically, preserving both projects' authorization."""
    _emit(_call(ctx, "POST", f"/v1/work-items/{quote(work_item_id, safe='')}/move", body=body), json_output)


@click.group("context")
def context_group() -> None:
    """Load task-specific current knowledge through the authority service."""


@context_group.command("work-item")
@click.argument("work_item_id")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def work_context(ctx: click.Context, work_item_id: str, json_output: bool) -> None:
    """Read project, program, formal sources, test, and predecessor state together."""
    result = _call(ctx, "GET", f"/v1/work-items/{quote(work_item_id, safe='')}/context")
    if not json_output:
        for key in ("program", "project", "work_item", "specifications", "test", "predecessors"):
            if result.get(key):
                click.echo(f"{key}:")
                _emit(result[key], False)
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
    uvicorn.run(create_authority_app(AuthorityService(kernel)), host="127.0.0.1", port=port, access_log=False)


@service_group.command("status")
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def service_status(ctx: click.Context, json_output: bool) -> None:
    """Read status from the configured service; never open a client database."""
    _emit(_call(ctx, "GET", "/v1/status"), json_output)
