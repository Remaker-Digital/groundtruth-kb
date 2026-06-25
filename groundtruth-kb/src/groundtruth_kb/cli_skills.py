"""``gt skills`` — deterministic skill-usage router CLI (SPEC-SKILL-USAGE-ROUTER-001 R6).

Exposes ``gt skills suggest``: a report-only advisory that maps a session scenario to
required + recommended skills plus a rationale, from the tracked
``config/agent-control/skill-scenarios.toml`` table via ``scripts/skill_usage_router.py``.
Report-only (R5): the command always exits 0; an unknown/unmatched scenario or a table
error yields an empty advisory. ``gt skills check`` is intentionally NOT provided this
slice (depends on WI-4814).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click


def _load_router() -> Any:
    """Import ``scripts.skill_usage_router``, adding the repo root to ``sys.path`` if needed.

    Mirrors the lazy scripts-import pattern in ``cli.py`` (the ``scripts.benchmarks.cli``
    loader): the router lives at the repo root under ``scripts/`` while this CLI ships in
    the installed package, so the repo root must be importable.
    """
    try:
        import scripts.skill_usage_router as router
    except ModuleNotFoundError:
        repo_root = Path(__file__).resolve().parents[3]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        import scripts.skill_usage_router as router
    return router


@click.group("skills")
def skills_group() -> None:
    """Skill-usage advisory tooling (report-only)."""


@skills_group.command("suggest")
@click.option("--scenario", default=None, help="Explicit scenario key (overrides signal matching).")
@click.option("--role", default=None, help="Resolved session role (prime-builder / loyal-opposition).")
@click.option(
    "--changed-path",
    "changed_paths",
    multiple=True,
    help="A changed path signal (repeatable).",
)
@click.option("--bridge-status", default=None, help="Bridge status signal (NEW/REVISED/GO/...).")
@click.option(
    "--bridge-kind",
    default=None,
    help="Bridge kind signal (implementation_report/loyal_opposition_advisory/...).",
)
@click.option(
    "--target-file",
    "target_files",
    multiple=True,
    help="A target file signal (repeatable).",
)
@click.option("--report-type", default=None, help="Report-type signal (advisory/session_wrap/release/...).")
@click.option("--json", "as_json", is_flag=True, help="Emit machine-readable JSON.")
def suggest_cmd(
    scenario: str | None,
    role: str | None,
    changed_paths: tuple[str, ...],
    bridge_status: str | None,
    bridge_kind: str | None,
    target_files: tuple[str, ...],
    report_type: str | None,
    as_json: bool,
) -> None:
    """Suggest required + recommended skills for a scenario (report-only; always exits 0)."""
    router = _load_router()
    try:
        result = router.suggest(
            scenario=scenario,
            role=role,
            changed_paths=list(changed_paths) or None,
            bridge_status=bridge_status,
            bridge_kind=bridge_kind,
            target_files=list(target_files) or None,
            report_type=report_type,
        )
        payload = result.as_dict()
    except router.SkillRouterError as exc:
        # Report-only (R5): a table load/validation error must not fail the CLI.
        payload = {
            "scenario": None,
            "required": [],
            "recommended": [],
            "rationale": "",
            "matched_by": None,
            "error": str(exc),
        }

    if as_json:
        click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    if payload["scenario"] is None:
        click.echo("No matching scenario — no skill suggestion (report-only).")
        if payload.get("error"):
            click.echo(f"  (router note: {payload['error']})")
        return
    click.echo(f"Scenario: {payload['scenario']} (matched by: {payload['matched_by']})")
    click.echo(f"  Required:    {', '.join(payload['required']) or '(none)'}")
    click.echo(f"  Recommended: {', '.join(payload['recommended']) or '(none)'}")
    click.echo(f"  Why: {payload['rationale']}")
