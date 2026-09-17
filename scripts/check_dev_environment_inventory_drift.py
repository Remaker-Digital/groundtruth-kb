#!/usr/bin/env python3
"""Compare the public operational inventory with the current installation.

Inventory is derived output. This diagnostic grants no review, authorization or
commit permission, and never inspects bridge messages or staged test presence.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from copy import deepcopy
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_RELATIVE_PATH = Path("config/governance/protected-artifact-inventory-drift.toml")
DEFAULT_INVENTORY_RELATIVE_PATH = Path(".groundtruth/inventory/dev-environment-inventory.json")
DEFAULT_VOLATILE_PATHS = ("generated_at",)


class DriftCheckError(RuntimeError):
    pass


def load_registry(path: Path) -> dict[str, Any]:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise DriftCheckError("Inventory comparison configuration is unavailable or malformed") from error
    volatile = data.get("volatile_inventory_paths", list(DEFAULT_VOLATILE_PATHS))
    if (
        data.get("schema_version") != 1
        or not isinstance(volatile, list)
        or not all(isinstance(v, str) and v for v in volatile)
    ):
        raise DriftCheckError("Invalid inventory comparison configuration")
    if set(data) - {"schema_version", "volatile_inventory_paths"}:
        raise DriftCheckError("Inventory comparison must not contain review or permission routes")
    return data


def normalize_inventory(payload: dict[str, Any], volatile_paths: list[str] | tuple[str, ...]) -> dict[str, Any]:
    normalized = deepcopy(payload)
    for dotted_path in volatile_paths:
        _delete_dotted_path(normalized, str(dotted_path))
    return normalized


def _delete_dotted_path(payload: Any, dotted_path: str) -> None:
    """Delete a dotted volatile path from the inventory payload in place.

    Supports a single-level ``*`` wildcard segment so a registry entry like
    ``toolchain.*.version`` strips the ``version`` key from every tool sub-dict
    (durable across future tools) without enumerating each tool. Non-wildcard
    components retain exact-match behavior, so existing volatile paths such as
    ``generated_at`` and ``redaction.sensitive_environment_entry_count`` are
    unaffected.
    """
    parts = [part for part in dotted_path.split(".") if part]
    if parts:
        _delete_path_parts(payload, parts)


def _delete_path_parts(current: Any, parts: list[str]) -> None:
    if not isinstance(current, dict):
        return
    head, rest = parts[0], parts[1:]
    keys = list(current.keys()) if head == "*" else [head]
    for key in keys:
        if key not in current:
            continue
        if rest:
            _delete_path_parts(current[key], rest)
        else:
            current.pop(key, None)


def inventory_diff_summary(baseline: dict[str, Any], current: dict[str, Any]) -> list[str]:
    keys = sorted(set(baseline) | set(current))
    return [key for key in keys if key not in baseline or key not in current or baseline[key] != current[key]]


def _read_public_inventory(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        raise DriftCheckError(f"inventory unreadable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise DriftCheckError(f"inventory malformed: {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise DriftCheckError("inventory JSON root must be an object")
    return loaded


def generate_current_public_inventory(project_root: Path) -> dict[str, Any]:
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from scripts.collect_dev_environment_inventory import InventoryError, collect_inventory  # noqa: PLC0415

    try:
        public, _private = collect_inventory(project_root)
    except InventoryError as error:
        raise DriftCheckError(str(error)) from error
    return public


def evaluate_drift(
    project_root: Path,
    *,
    registry_path: Path | None = None,
    inventory_path: Path | None = None,
    current_inventory: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    registry_file = registry_path or root / DEFAULT_REGISTRY_RELATIVE_PATH
    inventory_file = inventory_path or root / DEFAULT_INVENTORY_RELATIVE_PATH
    registry = load_registry(registry_file)
    baseline = _read_public_inventory(inventory_file)
    current = current_inventory if current_inventory is not None else generate_current_public_inventory(root)
    if not isinstance(current, dict):
        raise DriftCheckError("Current inventory must be an object")
    volatile = registry.get("volatile_inventory_paths", list(DEFAULT_VOLATILE_PATHS))
    differences = inventory_diff_summary(
        normalize_inventory(baseline, volatile), normalize_inventory(current, volatile)
    )
    return {
        "status": "fail" if differences else "pass",
        "outcome": "material_drift" if differences else "clean",
        "material_inventory_drift": bool(differences),
        "diff_keys": differences,
        "registry": str(registry_file),
        "inventory": str(inventory_file),
        "blocking": [
            {
                "reason": "normalized_inventory_drift",
                "message": "Current public inventory differs from recorded operational output",
            }
        ]
        if differences
        else [],
    }


def render_summary(result: dict[str, Any]) -> str:
    lines = [f"Inventory comparison: {result['status'].upper()} ({result['outcome']})"]
    if result.get("error"):
        lines.append(result["error"])
    if result.get("diff_keys"):
        lines.append("Diff keys: " + ", ".join(result["diff_keys"]))
    if result.get("material_inventory_drift"):
        lines.append(
            "Remediation: run 'python scripts/collect_dev_environment_inventory.py' to refresh the operational inventory."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    try:
        result = evaluate_drift(
            root,
            registry_path=root / args.registry if args.registry else None,
            inventory_path=root / args.inventory if args.inventory else None,
        )
    except (DriftCheckError, UnicodeError) as error:
        result = {"status": "fail", "outcome": "checker_error", "error": str(error)}
    print(json.dumps(result, indent=2) if args.json else render_summary(result))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
