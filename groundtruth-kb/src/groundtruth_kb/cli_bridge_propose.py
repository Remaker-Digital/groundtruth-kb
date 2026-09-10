"""Read-only evidence inspection for the transitional file bridge.

Agent-authored messages are delivered through the native bridge CLI. This
module retains the existing embedded-evidence inspector, not a proposal
composer or publication path.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import click

from groundtruth_kb.config import GTConfig


def _resolve_config(ctx: click.Context) -> GTConfig:
    config_path = ctx.obj.get("config") if ctx.obj else None
    return GTConfig.load(config_path=config_path)


@click.group("bridge")
def bridge_group() -> None:
    """Bridge protocol helper commands."""


def _load_bridge_verify_embedded_evidence(project_root: Path) -> Any:
    script_path = project_root / "scripts" / "bridge_verify_embedded_evidence.py"
    if not script_path.is_file():
        raise click.ClickException(f"Verification helper not found: {script_path}")
    spec = importlib.util.spec_from_file_location("bridge_verify_embedded_evidence", script_path)
    if spec is None or spec.loader is None:
        raise click.ClickException(f"Unable to load verification helper: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@bridge_group.command("verify-embedded-evidence")
@click.option("--bridge-id", help="Bridge document name / versioned bridge-thread slug.")
@click.option(
    "--content-file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    help="Evaluate pending Markdown content from a file.",
)
@click.option("--json", "emit_json", is_flag=True, help="Emit JSON instead of Markdown.")
@click.pass_context
def bridge_verify_embedded_evidence(
    ctx: click.Context,
    bridge_id: str | None,
    content_file: Path | None,
    emit_json: bool,
) -> None:
    """Verify embedded appendix evidence in a bridge report."""
    if bridge_id is None and content_file is None:
        raise click.ClickException("--bridge-id is required unless --content-file is supplied")
    config = _resolve_config(ctx)
    helper = _load_bridge_verify_embedded_evidence(config.project_root)
    argv: list[str] = [
        "--bridge-dir",
        str(config.project_root / "bridge"),
        "--clauses-config",
        str(config.project_root / "config" / "governance" / "adr-dcl-clauses.toml"),
    ]
    if bridge_id is not None:
        argv.extend(["--bridge-id", bridge_id])
    if content_file is not None:
        argv.extend(["--content-file", str(content_file)])
    if emit_json:
        argv.append("--json")
    raise click.exceptions.Exit(helper.main(argv))
