"""Deterministic instantiation of the Scope-Transition project template (WI-4688 Slice B).

Reads ``config/project-templates/scope-transition.toml`` and instantiates a
scope-transition project (per ``GOV-SCOPE-TRANSITION-PROCEDURE-001``) whose member
work items map 1:1 to the five procedure steps. Per SPEC-1830 (operational
procedures must be code), instantiation is a deterministic helper, not a
hand-built checklist.

``plan_project`` and ``render_commands`` are pure and testable; ``instantiate``
defaults to dry-run and only mutates MemBase (via the governed ``gt`` CLI) when
``--apply`` is given.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = REPO_ROOT / "config" / "project-templates" / "scope-transition.toml"


def _slug(application: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", application.upper()).strip("-")


def load_template(path: Path) -> dict[str, Any]:
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    if "template" not in data or "work_items" not in data:
        raise ValueError(f"Malformed scope-transition template: {path}")
    return data


def plan_project(template: dict[str, Any], application: str) -> dict[str, Any]:
    """Pure: render the concrete project + member-WI plan for an application."""
    tmpl = template["template"]
    app = application.strip()
    if not app:
        raise ValueError("application must be a non-empty string")
    subst = {"application": app}
    project_id = f"PROJECT-SCOPE-TRANSITION-{_slug(app)}"
    work_items = [
        {
            "step": int(wi["step"]),
            "title": wi["title"].format(**subst),
            "component": wi["component"],
            "origin": wi["origin"],
            "priority": wi["priority"],
            "description": wi["description"].format(**subst),
        }
        for wi in template["work_items"]
    ]
    return {
        "project_id": project_id,
        "name": tmpl["name_pattern"].format(**subst),
        "purpose": tmpl["purpose"].format(**subst),
        "target_outcome": tmpl["target_outcome"].format(**subst),
        "scope_note": tmpl["scope_note"].format(**subst),
        "procedure_spec": tmpl["procedure_spec"],
        "work_items": work_items,
    }


def render_commands(plan: dict[str, Any]) -> list[list[str]]:
    """Pure: the governed ``gt`` CLI commands that would create the project + WIs."""
    commands: list[list[str]] = [
        [
            "gt",
            "projects",
            "create",
            plan["name"],
            "--id",
            plan["project_id"],
            "--purpose",
            plan["purpose"],
            "--target-outcome",
            plan["target_outcome"],
            "--scope-note",
            plan["scope_note"],
        ]
    ]
    for wi in plan["work_items"]:
        commands.append(
            [
                "gt",
                "backlog",
                "add",
                "--title",
                wi["title"],
                "--component",
                wi["component"],
                "--origin",
                wi["origin"],
                "--priority",
                wi["priority"],
                "--project",
                plan["project_id"],
            ]
        )
    return commands


def instantiate(template_path: Path, application: str, *, dry_run: bool = True) -> dict[str, Any]:
    plan = plan_project(load_template(template_path), application)
    commands = render_commands(plan)
    if not dry_run:
        for cmd in commands:
            subprocess.run(cmd, cwd=REPO_ROOT, check=True)
    return {"plan": plan, "commands": commands, "applied": not dry_run}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Instantiate the Scope-Transition project template.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--application", required=True, help="Target application name")
    parser.add_argument("--apply", action="store_true", help="Create the project (default: dry-run)")
    args = parser.parse_args(argv)
    result = instantiate(args.template, args.application, dry_run=not args.apply)
    mode = "APPLIED" if result["applied"] else "DRY-RUN"
    print(f"[{mode}] {result['plan']['project_id']} :: {result['plan']['name']}")
    for wi in result["plan"]["work_items"]:
        print(f"  - step {wi['step']}: {wi['title']} [{wi['component']}/{wi['priority']}]")
    if not result["applied"]:
        print(f"  ({len(result['commands'])} governed gt commands would run with --apply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
