"""``gt bridge index`` deterministic INDEX mutation CLI."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import click

from groundtruth_kb.config import GTConfig


def _resolve_config(ctx: click.Context) -> GTConfig:
    config_path = ctx.obj.get("config") if ctx.obj else None
    return GTConfig.load(config_path=config_path)


def _load_scripts_writer(project_root: Path) -> ModuleType:
    """Import the standalone ``scripts/gtkb_bridge_writer`` module.

    The ``remove-document`` primitive lives in the standalone serialized writer
    (``scripts/gtkb_bridge_writer.py``), not in ``groundtruth_kb.bridge``. That
    module resolves its own siblings via a ``scripts.`` import with a bare-name
    fallback, so putting ``<project_root>/scripts`` on ``sys.path`` lets the
    fallback (`from bridge_index_writer import ...`) resolve when the project
    root itself is not importable as a package.
    """
    scripts_dir = str(project_root / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import gtkb_bridge_writer  # noqa: PLC0415 - lazy, project-root-relative import

    return gtkb_bridge_writer


@click.group("index")
def bridge_index_group() -> None:
    """Serialized bridge INDEX mutation commands."""


@bridge_index_group.command("add-document")
@click.argument("document_slug")
@click.option("--status", default="NEW", show_default=True, help="Status line to create for the new document.")
@click.option("--path", "bridge_path", required=True, help="Version path, e.g. bridge/<slug>-001.md.")
@click.option("--timeout", "timeout_seconds", default=10.0, show_default=True, help="INDEX lock timeout in seconds.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def add_document_cmd(
    ctx: click.Context,
    document_slug: str,
    status: str,
    bridge_path: str,
    timeout_seconds: float,
    json_output: bool,
) -> None:
    """Add a new document block to bridge/INDEX.md through the serialized writer."""
    from groundtruth_kb.bridge.index_mutation import BridgeIndexMutationError, add_document

    config = _resolve_config(ctx)
    try:
        result = add_document(
            Path(config.project_root),
            document_slug,
            status=status,
            bridge_path=bridge_path,
            timeout_seconds=timeout_seconds,
        )
    except BridgeIndexMutationError as exc:
        raise click.ClickException(str(exc)) from exc
    _emit_result("added", result, json_output=json_output)


@bridge_index_group.command("set-status")
@click.argument("document_slug")
@click.argument("status")
@click.option("--path", "bridge_path", required=True, help="Version path, e.g. bridge/<slug>-002.md.")
@click.option("--timeout", "timeout_seconds", default=10.0, show_default=True, help="INDEX lock timeout in seconds.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def set_status_cmd(
    ctx: click.Context,
    document_slug: str,
    status: str,
    bridge_path: str,
    timeout_seconds: float,
    json_output: bool,
) -> None:
    """Prepend a status line to an existing bridge/INDEX.md document block."""
    from groundtruth_kb.bridge.index_mutation import BridgeIndexMutationError, set_status

    config = _resolve_config(ctx)
    try:
        result = set_status(
            Path(config.project_root),
            document_slug,
            status,
            bridge_path=bridge_path,
            timeout_seconds=timeout_seconds,
        )
    except BridgeIndexMutationError as exc:
        raise click.ClickException(str(exc)) from exc
    _emit_result("updated", result, json_output=json_output)


@bridge_index_group.command("remove-document")
@click.argument("document_slug")
@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")
@click.pass_context
def remove_document_cmd(
    ctx: click.Context,
    document_slug: str,
    json_output: bool,
) -> None:
    """Remove a phantom (no-backing-file) document block from bridge/INDEX.md.

    Phantom-only: refuses when any bridge/<slug>-NNN.md file exists on disk, so
    a real thread's INDEX entry can never be removed by this command.
    """
    config = _resolve_config(ctx)
    project_root = Path(config.project_root)
    writer = _load_scripts_writer(project_root)
    try:
        writer.remove_document(document_slug, project_root)
    except writer.BridgeError as exc:
        raise click.ClickException(str(exc)) from exc
    index_path = project_root / "bridge" / "INDEX.md"
    if json_output:
        click.echo(
            json.dumps(
                {"document": document_slug, "removed": True, "index_path": str(index_path)},
                indent=2,
                sort_keys=True,
            )
        )
        return
    click.echo(f"removed {document_slug} from bridge/INDEX.md")


def _emit_result(action: str, result: Any, *, json_output: bool) -> None:
    if json_output:
        click.echo(json.dumps(result.to_json_dict(), indent=2, sort_keys=True))
        return
    click.echo(f"{action} {result.document}: {result.status} {result.path}")
