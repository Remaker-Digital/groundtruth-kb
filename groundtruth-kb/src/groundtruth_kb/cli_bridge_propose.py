"""``gt bridge propose`` deterministic draft CLI."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from string import Template
from typing import Any

import click

from groundtruth_kb.bridge.proposal_autoload import (
    auto_owner_decisions,
    auto_prior_delibs,
    auto_project_metadata,
    auto_spec_links,
    auto_target_paths_in_root_evidence,
    get_work_item_or_raise,
)
from groundtruth_kb.bridge.taxonomy import BridgeKind
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.gates import GateRegistry

PROPOSAL_KINDS: tuple[str, ...] = (
    "implementation",
    "defect-fix",
    "scoping",
    "advisory-disposition",
    "retirement",
    "umbrella",
)
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")

KIND_INTROS = {
    "implementation": "Implementation proposal for a bounded code or platform change.",
    "defect-fix": "Defect-fix proposal focused on reproducing, correcting, and verifying a fault.",
    "scoping": "Scoping proposal that frames a future implementation slice.",
    "advisory-disposition": (
        "Advisory-disposition proposal that routes Loyal Opposition advice into a governed outcome."
    ),
    "retirement": "Retirement proposal for closing or retiring stale governed work.",
    "umbrella": "Umbrella proposal coordinating multiple related work items or dispositions.",
}

RECOMMENDED_COMMIT_TYPES = {
    "implementation": "feat",
    "defect-fix": "fix",
    "scoping": "docs",
    "advisory-disposition": "docs",
    "retirement": "chore",
    "umbrella": "docs",
}

_BASE_TEMPLATE = """NEW

# ${title_prefix} - ${wi_title}

bridge_kind: ${bridge_kind}
Document: ${slug}
Version: 001 (DRAFT; non-dispatchable)
Date: ${date}
${author_metadata_block}

Project Authorization: ${project_authorization_id}
Project: ${project_id}
Work Item: ${wi_id}

target_paths: ${target_paths_json}

${kind_specific_intro}

## Claim

${claim}

${kind_section}## In-Root Placement Evidence

${target_path_evidence}

## Specification Links

${auto_spec_links}

## Prior Deliberations

${auto_prior_delibs}

## Owner Decisions / Input

${auto_owner_decisions}

## Proposed Scope

${proposed_scope_ip_blocks}

## Specification-Derived Verification Plan

${verification_plan_table}

## Acceptance Criteria

${acceptance_criteria}

## Risks / Rollback

${risks_rollback}

## Files Expected To Change

${target_paths_bullets}

## Recommended Commit Type

`${recommended_commit_type}`
"""

TEMPLATE_CONTEXT_BY_KIND = {
    "implementation": {
        "title_prefix": "Implementation Proposal",
        "kind_section": "## Requirement Sufficiency\n\n${requirement_sufficiency}\n\n",
    },
    "defect-fix": {
        "title_prefix": "Defect-Fix Proposal",
        "kind_section": "## Defect / Reproduction\n\n${defect_reproduction}\n\n",
    },
    "scoping": {
        "title_prefix": "Scoping Proposal",
        "kind_section": "## Scope Boundary\n\n${scope_boundary}\n\n",
    },
    "advisory-disposition": {
        "title_prefix": "Advisory-Disposition Proposal",
        "kind_section": "## Advisory Disposition\n\n${advisory_disposition}\n\n",
    },
    "retirement": {
        "title_prefix": "Retirement Proposal",
        "kind_section": "## Retirement Rationale\n\n${retirement_rationale}\n\n",
    },
    "umbrella": {
        "title_prefix": "Umbrella Proposal",
        "kind_section": "## Umbrella Inventory\n\n${umbrella_inventory}\n\n",
    },
}


def _resolve_config(ctx: click.Context) -> GTConfig:
    config_path = ctx.obj.get("config") if ctx.obj else None
    return GTConfig.load(config_path=config_path)


def _open_db(config: GTConfig) -> KnowledgeDB:
    registry = GateRegistry.from_config(
        config.governance_gates,
        include_builtins=True,
        gate_config=config.gate_config,
        project_root=config.project_root,
    )
    return KnowledgeDB(db_path=config.db_path, gate_registry=registry)


def _format_bullets(values: list[str], *, empty: str) -> str:
    if not values:
        return f"- {empty}"
    return "\n".join(f"- {value}" for value in values)


def _format_spec_links(spec_ids: list[str]) -> str:
    return "\n".join(f"- `{spec_id}` - <fill relevance>" for spec_id in spec_ids)


def _validate_slug(slug: str) -> None:
    if not _SLUG_RE.fullmatch(slug):
        raise click.ClickException("Slug must be lowercase kebab-case using only a-z, 0-9, and hyphens.")


def _placeholder_author_metadata_block() -> str:
    fields = (
        "author_identity",
        "author_harness_id",
        "author_session_context_id",
        "author_model",
        "author_model_version",
        "author_model_configuration",
    )
    return "\n".join(f"{field}: TODO: <fill {field}>" for field in fields) + "\n"


def _author_metadata_block(project_root: Path) -> str:
    try:
        from scripts.bridge_author_metadata import (
            BridgeAuthorMetadataError,
            load_author_metadata,
            render_author_metadata_lines,
        )
    except Exception:
        return _placeholder_author_metadata_block()

    try:
        return "".join(render_author_metadata_lines(load_author_metadata(project_root)))
    except BridgeAuthorMetadataError:
        return _placeholder_author_metadata_block()


def build_propose_context(
    db: KnowledgeDB,
    project_root: Path,
    *,
    kind: str,
    wi_id: str,
    slug: str,
    target_paths: tuple[str, ...],
    add_specs: tuple[str, ...],
) -> dict[str, Any]:
    """Build the deterministic template context for one bridge proposal draft."""
    _validate_slug(slug)
    work_item = get_work_item_or_raise(db, wi_id)
    metadata = auto_project_metadata(db, wi_id)
    spec_links = auto_spec_links(db, project_root, wi_id, kind, target_paths, add_specs)
    prior_delibs = auto_prior_delibs(db, wi_id, slug)
    owner_decisions = auto_owner_decisions(project_root, wi_id)
    target_paths_json = json.dumps(list(target_paths), ensure_ascii=True)
    return {
        **TEMPLATE_CONTEXT_BY_KIND[kind],
        "slug": slug,
        "kind": kind,
        "date": f"{datetime.now(UTC).date().isoformat()} UTC",
        "author_metadata_block": _author_metadata_block(project_root),
        "wi_id": wi_id,
        "wi_title": str(work_item.get("title") or wi_id),
        "wi_description": str(work_item.get("description") or ""),
        "project_authorization_id": metadata["project_authorization_id"],
        "project_id": metadata["project_id"],
        "project_name": metadata["project_name"],
        "target_paths_json": target_paths_json,
        "bridge_kind": BridgeKind.PRIME_PROPOSAL.value,
        "target_paths_bullets": _format_bullets(
            [f"`{path}`" for path in target_paths],
            empty="_No target paths supplied; fill before filing._",
        ),
        "target_path_evidence": auto_target_paths_in_root_evidence(project_root, target_paths),
        "auto_spec_links": _format_spec_links(spec_links),
        "auto_prior_delibs": _format_bullets(
            prior_delibs,
            empty="_No prior deliberations auto-loaded; search and justify before filing._",
        ),
        "auto_owner_decisions": _format_bullets(
            owner_decisions,
            empty=f"`{metadata['project_authorization_id']}` - <verify owner-decision evidence before filing>",
        ),
        "kind_specific_intro": KIND_INTROS[kind],
        "recommended_commit_type": RECOMMENDED_COMMIT_TYPES[kind],
    }


def render_proposal_draft(kind: str, context: dict[str, Any]) -> str:
    if kind not in PROPOSAL_KINDS:
        raise ValueError(f"Unsupported proposal kind: {kind}")
    first_pass = Template(_BASE_TEMPLATE).safe_substitute(context)
    return Template(first_pass).safe_substitute(context).rstrip() + "\n"


@click.group("bridge")
def bridge_group() -> None:
    """Bridge protocol helper commands."""


@bridge_group.command("propose")
@click.option("--kind", required=True, type=click.Choice(PROPOSAL_KINDS), help="Bridge proposal template kind.")
@click.option("--wi", "wi_id", required=True, help="Existing MemBase work item id.")
@click.option("--slug", required=True, help="Bridge slug, lowercase kebab-case.")
@click.option("--target-path", "target_paths", multiple=True, help="Repeatable implementation target path.")
@click.option("--add-spec", "add_specs", multiple=True, help="Repeatable spec id to add to generated links.")
@click.option("--dry-run", is_flag=True, help="Print the draft without writing .gtkb-state.")
@click.pass_context
def bridge_propose(
    ctx: click.Context,
    kind: str,
    wi_id: str,
    slug: str,
    target_paths: tuple[str, ...],
    add_specs: tuple[str, ...],
    dry_run: bool,
) -> None:
    """Emit a deterministic, non-dispatchable bridge proposal draft."""
    config = _resolve_config(ctx)
    db = _open_db(config)
    try:
        context = build_propose_context(
            db,
            config.project_root,
            kind=kind,
            wi_id=wi_id,
            slug=slug,
            target_paths=target_paths,
            add_specs=add_specs,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        db.close()

    rendered = render_proposal_draft(kind, context)
    if dry_run:
        click.echo(rendered.rstrip())
        return

    draft_dir = config.project_root / ".gtkb-state" / "bridge-propose-drafts"
    output_path = draft_dir / f"{slug}-001.md"
    if output_path.exists():
        raise click.ClickException(f"Draft already exists: {output_path}. Refusing to overwrite.")
    draft_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    click.echo(f"Wrote DRAFT: {output_path}")
    click.echo("This is a NON-DISPATCHABLE draft; it is not a filed bridge proposal.")
    click.echo("Fill the AI-judgment placeholders, then file through the bridge-propose helper.")
