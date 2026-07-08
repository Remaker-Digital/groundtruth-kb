#!/usr/bin/env python3
"""Read-only cloud-sandbox dispatch planning helper."""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = Path("config/dispatcher/sandbox-execution.toml")


def _read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _as_bool(value: object) -> bool:
    return bool(value) if isinstance(value, bool) else str(value).lower() == "true"


def build_plan(config: dict[str, Any], *, project_root: Path) -> dict[str, Any]:
    providers = list(config.get("providers") or [])
    gates = list(config.get("approval_gates") or [])
    defaults = dict(config.get("defaults") or {})

    provider_plans: list[dict[str, Any]] = []
    for provider in providers:
        provider_plans.append(
            {
                "name": str(provider.get("name", "")),
                "enabled": _as_bool(provider.get("enabled", False)),
                "credential_source": str(provider.get("credential_source", "future_owner_approval")),
                "capabilities": list(provider.get("capabilities") or []),
                "required_artifacts": list(provider.get("required_artifacts") or []),
                "launch_permitted": False,
            }
        )

    return {
        "schema_version": int(config.get("schema_version", 1)),
        "enabled": _as_bool(config.get("enabled", False)),
        "mode": str(config.get("mode", "planning_only")),
        "planning_only": True,
        "runtime_launch_allowed": False,
        "credential_access_allowed": False,
        "dispatcher_replacement_allowed": False,
        "project_root": project_root.resolve().as_posix(),
        "root_boundary": str(defaults.get("root_boundary", project_root.resolve().as_posix())),
        "artifact_retention_days": int(defaults.get("artifact_retention_days", 30)),
        "required_review_status": str(defaults.get("required_review_status", "VERIFIED")),
        "providers": provider_plans,
        "approval_gates": [
            {
                "name": str(gate.get("name", "")),
                "required_before": str(gate.get("required_before", "")),
                "owner_decision_required": _as_bool(gate.get("owner_decision_required", True)),
            }
            for gate in gates
        ],
        "future_runtime_requirements": [
            "owner-approved provider selection",
            "owner-approved credential use",
            "no-window/headless smoke evidence",
            "artifact preservation contract",
            "dispatcher daemon remains the control plane",
        ],
    }


def render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Omnigent Cloud Sandbox Dispatch Plan",
        "",
        "## Status",
        "",
        f"- Enabled: `{str(plan['enabled']).lower()}`",
        f"- Mode: `{plan['mode']}`",
        f"- Runtime launch allowed: `{str(plan['runtime_launch_allowed']).lower()}`",
        f"- Credential access allowed: `{str(plan['credential_access_allowed']).lower()}`",
        f"- Dispatcher replacement allowed: `{str(plan['dispatcher_replacement_allowed']).lower()}`",
        "",
        "## Providers",
        "",
    ]
    for provider in plan["providers"]:
        lines.extend(
            [
                f"- `{provider['name']}`: enabled=`{str(provider['enabled']).lower()}`, "
                f"launch_permitted=`{str(provider['launch_permitted']).lower()}`, "
                f"credential_source=`{provider['credential_source']}`",
            ]
        )
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
