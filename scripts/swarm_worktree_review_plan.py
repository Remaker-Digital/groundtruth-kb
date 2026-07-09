#!/usr/bin/env python3
"""Read-only worktree/subagent review planning helper."""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = Path("config/dispatcher/swarm-worktree-review.toml")


def _read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _as_bool(value: object) -> bool:
    return bool(value) if isinstance(value, bool) else str(value).lower() == "true"


def build_plan(config: dict[str, Any], *, project_root: Path) -> dict[str, Any]:
    defaults = dict(config.get("defaults") or {})
    lanes = list(config.get("lanes") or [])
    review_routes = list(config.get("review_routes") or [])
    approval_gates = list(config.get("approval_gates") or [])

    lane_plans = [
        {
            "name": str(lane.get("name", "")),
            "enabled": _as_bool(lane.get("enabled", False)),
            "isolated_worktree_required": _as_bool(lane.get("isolated_worktree_required", True)),
            "artifact_outputs": list(lane.get("artifact_outputs") or []),
            "worktree_creation_permitted": False,
            "agent_spawn_permitted": False,
        }
        for lane in lanes
    ]
    route_plans = [
        {
            "name": str(route.get("name", "")),
            "primary_vendor": str(route.get("primary_vendor", "")),
            "reviewer_vendor": str(route.get("reviewer_vendor", "")),
            "cross_vendor_required": _as_bool(route.get("cross_vendor_required", True)),
            "typed_waiver_required": _as_bool(route.get("typed_waiver_required", True)),
            "bridge_bypass_permitted": False,
        }
        for route in review_routes
    ]

    return {
        "schema_version": int(config.get("schema_version", 1)),
        "enabled": _as_bool(config.get("enabled", False)),
        "mode": str(config.get("mode", "planning_only")),
        "planning_only": True,
        "worktree_creation_allowed": False,
        "agent_spawn_allowed": False,
        "harness_invocation_allowed": False,
        "bridge_bypass_allowed": False,
        "git_mutation_allowed": False,
        "project_root": project_root.resolve().as_posix(),
        "root_boundary": str(defaults.get("root_boundary", project_root.resolve().as_posix())),
        "required_review_status": str(defaults.get("required_review_status", "VERIFIED")),
        "required_bridge_sequence": list(
            defaults.get("required_bridge_sequence") or ["NEW", "GO", "implementation_report", "VERIFIED"]
        ),
        "lanes": lane_plans,
        "review_routes": route_plans,
        "approval_gates": [
            {
                "name": str(gate.get("name", "")),
                "required_before": str(gate.get("required_before", "")),
                "owner_decision_required": _as_bool(gate.get("owner_decision_required", True)),
            }
            for gate in approval_gates
        ],
        "future_runtime_requirements": [
            "owner-approved worktree orchestration",
            "owner-approved harness invocation",
            "cross-vendor reviewer assignment or typed waiver",
            "bridge lifecycle preservation",
            "manual finalization approval before automation",
        ],
    }


def render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Omnigent Worktree Cross-Vendor Review Plan",
        "",
        "## Status",
        "",
        f"- Enabled: `{str(plan['enabled']).lower()}`",
        f"- Mode: `{plan['mode']}`",
        f"- Worktree creation allowed: `{str(plan['worktree_creation_allowed']).lower()}`",
        f"- Agent spawn allowed: `{str(plan['agent_spawn_allowed']).lower()}`",
        f"- Harness invocation allowed: `{str(plan['harness_invocation_allowed']).lower()}`",
        f"- Bridge bypass allowed: `{str(plan['bridge_bypass_allowed']).lower()}`",
        "",
        "## Lanes",
        "",
    ]
    for lane in plan["lanes"]:
        lines.append(
            f"- `{lane['name']}`: enabled=`{str(lane['enabled']).lower()}`, "
            f"isolated_worktree_required=`{str(lane['isolated_worktree_required']).lower()}`, "
            f"worktree_creation_permitted=`{str(lane['worktree_creation_permitted']).lower()}`"
        )
    lines.extend(["", "## Review Routes", ""])
    for route in plan["review_routes"]:
        lines.append(
            f"- `{route['name']}`: primary=`{route['primary_vendor']}`, reviewer=`{route['reviewer_vendor']}`, "
            f"cross_vendor_required=`{str(route['cross_vendor_required']).lower()}`, "
            f"typed_waiver_required=`{str(route['typed_waiver_required']).lower()}`"
        )
    lines.extend(["", "## Bridge Lifecycle", ""])
    lines.append("- Required sequence: `" + " -> ".join(plan["required_bridge_sequence"]) + "`")
    lines.extend(["", "## Approval Gates", ""])
    for gate in plan["approval_gates"]:
        lines.append(
            f"- `{gate['name']}` before `{gate['required_before']}`; "
            f"owner_decision_required=`{str(gate['owner_decision_required']).lower()}`"
        )
    lines.extend(["", "## Future Runtime Requirements", ""])
    for requirement in plan["future_runtime_requirements"]:
        lines.append(f"- {requirement}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    config = _read_toml(args.config)
    plan = build_plan(config, project_root=args.project_root)
    if args.format == "markdown":
        rendered = render_markdown(plan)
    else:
        rendered = json.dumps(plan, indent=2, sort_keys=True) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
