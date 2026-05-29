#!/usr/bin/env python3
"""Check protected-artifact drift against the GT-KB dev environment inventory."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
import tomllib
from copy import deepcopy
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_RELATIVE_PATH = Path("config/governance/protected-artifact-inventory-drift.toml")
DEFAULT_INVENTORY_RELATIVE_PATH = Path(".groundtruth/inventory/dev-environment-inventory.json")
DEFAULT_VOLATILE_PATHS = ("generated_at",)
PASSING_OUTCOMES = {"clean", "accepted_baseline_update", "local_only_notice", "review_evidence_present"}
BRIDGE_REVIEW_EVIDENCE_PATTERNS = ("bridge/INDEX.md", "bridge/*.md")


class DriftCheckError(RuntimeError):
    """Raised for configuration or boundary errors in the drift checker."""


def _posix_path(path: str | Path) -> str:
    text = str(path).replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    return text


def _assert_relative_inside_project(path_text: str) -> str:
    normalized = _posix_path(path_text)
    path = Path(normalized)
    if path.is_absolute() or normalized == ".." or normalized.startswith("../") or "/../" in normalized:
        raise DriftCheckError(f"changed path escapes project root: {path_text}")
    return normalized


def load_registry(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            loaded = tomllib.load(handle)
    except OSError as exc:
        raise DriftCheckError(f"registry unreadable: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise DriftCheckError(f"registry malformed: {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise DriftCheckError("registry root must be a table")
    if loaded.get("schema_version") != 1:
        raise DriftCheckError("registry schema_version must be 1")
    entries = loaded.get("protected_artifacts")
    if not isinstance(entries, list) or not entries:
        raise DriftCheckError("registry must define at least one protected_artifacts entry")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise DriftCheckError("protected_artifacts entries must be tables")
        entry_id = str(entry.get("id") or "").strip()
        if not entry_id:
            raise DriftCheckError("protected artifact entry missing id")
        if entry_id in seen:
            raise DriftCheckError(f"duplicate protected artifact id: {entry_id}")
        seen.add(entry_id)
        patterns = entry.get("patterns")
        if not isinstance(patterns, list) or not all(isinstance(item, str) and item.strip() for item in patterns):
            raise DriftCheckError(f"{entry_id} patterns must be non-empty strings")
        if not str(entry.get("route") or "").strip():
            raise DriftCheckError(f"{entry_id} route is required")
    return loaded


def normalize_inventory(payload: dict[str, Any], volatile_paths: list[str] | tuple[str, ...]) -> dict[str, Any]:
    normalized = deepcopy(payload)
    for dotted_path in volatile_paths or DEFAULT_VOLATILE_PATHS:
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
    return [key for key in keys if baseline.get(key) != current.get(key)]


def _read_public_inventory(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise DriftCheckError(f"inventory unreadable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise DriftCheckError(f"inventory malformed: {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise DriftCheckError("inventory JSON root must be an object")
    return loaded


def generate_current_public_inventory(project_root: Path) -> dict[str, Any]:
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from scripts.collect_dev_environment_inventory import collect_inventory  # noqa: PLC0415

    public, _private = collect_inventory(project_root)
    return public


def _git_changed_paths(project_root: Path, *, staged: bool) -> list[str]:
    commands = [["git", "diff", "--name-only"]]
    if staged:
        commands = [["git", "diff", "--cached", "--name-only"]]
    else:
        commands.append(["git", "diff", "--cached", "--name-only"])
        commands.append(["git", "ls-files", "--others", "--exclude-standard"])
    changed: list[str] = []
    for command in commands:
        result = subprocess.run(
            command,
            cwd=project_root,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            continue
        for line in result.stdout.splitlines():
            path = _assert_relative_inside_project(line)
            if path and path not in changed:
                changed.append(path)
    return changed


def classify_changed_paths(registry: dict[str, Any], changed_paths: list[str]) -> list[dict[str, Any]]:
    entries = registry.get("protected_artifacts") or []
    matches: list[dict[str, Any]] = []
    for path_text in changed_paths:
        path = _assert_relative_inside_project(path_text)
        for entry in entries:
            patterns = [_posix_path(pattern) for pattern in entry.get("patterns", [])]
            if any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns):
                matches.append(
                    {
                        "path": path,
                        "entry_id": entry.get("id"),
                        "route": entry.get("route"),
                        "severity": entry.get("severity"),
                        "accept_with_inventory_baseline_update": bool(
                            entry.get("accept_with_inventory_baseline_update")
                        ),
                        "required_evidence": list(entry.get("required_evidence") or []),
                    }
                )
                break
    return matches


def has_bridge_review_evidence(changed_paths: list[str]) -> bool:
    return any(
        any(fnmatch.fnmatchcase(path, pattern) for pattern in BRIDGE_REVIEW_EVIDENCE_PATTERNS) for path in changed_paths
    )


def evaluate_drift(
    project_root: Path,
    *,
    registry_path: Path | None = None,
    inventory_path: Path | None = None,
    changed_paths: list[str] | None = None,
    staged: bool = False,
    current_inventory: dict[str, Any] | None = None,
    allow_review_evidence: bool = False,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    registry_file = registry_path or project_root / DEFAULT_REGISTRY_RELATIVE_PATH
    inventory_file = inventory_path or project_root / DEFAULT_INVENTORY_RELATIVE_PATH
    registry = load_registry(registry_file)
    baseline = _read_public_inventory(inventory_file)
    current = current_inventory if current_inventory is not None else generate_current_public_inventory(project_root)
    volatile_paths = tuple(registry.get("volatile_inventory_paths") or DEFAULT_VOLATILE_PATHS)
    normalized_baseline = normalize_inventory(baseline, volatile_paths)
    normalized_current = normalize_inventory(current, volatile_paths)
    diff_keys = inventory_diff_summary(normalized_baseline, normalized_current)
    material_inventory_drift = bool(diff_keys)
    paths = list(changed_paths) if changed_paths is not None else _git_changed_paths(project_root, staged=staged)
    normalized_changed_paths = [_assert_relative_inside_project(path) for path in paths]
    protected_changes = classify_changed_paths(registry, normalized_changed_paths)
    review_evidence_present = has_bridge_review_evidence(normalized_changed_paths)
    baseline_rel = DEFAULT_INVENTORY_RELATIVE_PATH.as_posix()
    baseline_changed = baseline_rel in set(normalized_changed_paths)
    blocking: list[dict[str, Any]] = []
    warnings: list[str] = []

    if material_inventory_drift:
        blocking.append(
            {
                "reason": "normalized_inventory_drift",
                "message": "current public inventory differs from committed baseline",
                "diff_keys": diff_keys,
            }
        )

    accepted_baseline_update = False
    local_only_notice = False
    review_evidence_accepted = False
    for change in protected_changes:
        route = str(change.get("route") or "")
        if route == "local_only_notice":
            local_only_notice = True
            warnings.append(f"local-only protected change: {change['path']}")
            continue
        if change.get("accept_with_inventory_baseline_update") and baseline_changed and not material_inventory_drift:
            accepted_baseline_update = True
            continue
        if allow_review_evidence and review_evidence_present:
            review_evidence_accepted = True
            warnings.append(f"protected change has staged bridge review evidence: {change['path']}")
            continue
        blocking.append(
            {
                "reason": "protected_artifact_change_requires_review",
                "path": change["path"],
                "entry_id": change["entry_id"],
                "route": route,
                "severity": change.get("severity"),
                "required_evidence": change.get("required_evidence", []),
            }
        )

    if blocking:
        status = "fail"
        outcome = "release_blocker"
    elif accepted_baseline_update:
        status = "pass"
        outcome = "accepted_baseline_update"
    elif local_only_notice:
        status = "pass"
        outcome = "local_only_notice"
    elif review_evidence_accepted:
        status = "pass"
        outcome = "review_evidence_present"
    else:
        status = "pass"
        outcome = "clean"

    return {
        "status": status,
        "outcome": outcome,
        "material_inventory_drift": material_inventory_drift,
        "diff_keys": diff_keys,
        "changed_paths": normalized_changed_paths,
        "protected_changes": protected_changes,
        "baseline_changed": baseline_changed,
        "review_evidence_present": review_evidence_present,
        "allow_review_evidence": allow_review_evidence,
        "blocking": blocking,
        "warnings": warnings,
        "registry": str(
            registry_file.relative_to(project_root) if registry_file.is_relative_to(project_root) else registry_file
        ),
        "inventory": str(
            inventory_file.relative_to(project_root) if inventory_file.is_relative_to(project_root) else inventory_file
        ),
    }


def render_summary(result: dict[str, Any]) -> str:
    lines = [
        f"Inventory drift check: {result['status'].upper()} ({result['outcome']})",
        f"Registry: {result['registry']}",
        f"Inventory: {result['inventory']}",
        f"Changed paths: {len(result['changed_paths'])}",
        f"Protected changes: {len(result['protected_changes'])}",
        f"Material inventory drift: {result['material_inventory_drift']}",
    ]
    if result.get("diff_keys"):
        lines.append("Diff keys: " + ", ".join(result["diff_keys"]))
    for item in result.get("blocking", []):
        if item.get("path"):
            lines.append(
                f"BLOCK {item['path']}: {item.get('entry_id')} requires {item.get('route')} ({item.get('severity')})"
            )
        else:
            lines.append(f"BLOCK {item.get('reason')}: {item.get('message')}")
    for warning in result.get("warnings", []):
        lines.append(f"WARN {warning}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--inventory", type=Path, default=None)
    parser.add_argument("--staged", action="store_true", help="Check only staged paths.")
    parser.add_argument(
        "--allow-review-evidence",
        action="store_true",
        help="Allow protected path changes when staged bridge review evidence is present.",
    )
    parser.add_argument("--changed-path", action="append", default=None, help="Override changed paths for tests.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    registry = args.registry
    if registry is not None and not registry.is_absolute():
        registry = project_root / registry
    inventory = args.inventory
    if inventory is not None and not inventory.is_absolute():
        inventory = project_root / inventory
    try:
        result = evaluate_drift(
            project_root,
            registry_path=registry,
            inventory_path=inventory,
            changed_paths=args.changed_path,
            staged=args.staged,
            allow_review_evidence=args.allow_review_evidence,
        )
    except DriftCheckError as exc:
        result = {
            "status": "fail",
            "outcome": "checker_error",
            "blocking": [{"reason": "checker_error", "message": str(exc)}],
            "changed_paths": [],
            "protected_changes": [],
            "material_inventory_drift": False,
            "diff_keys": [],
            "warnings": [],
            "review_evidence_present": False,
            "allow_review_evidence": args.allow_review_evidence,
            "registry": str(registry or DEFAULT_REGISTRY_RELATIVE_PATH),
            "inventory": str(inventory or DEFAULT_INVENTORY_RELATIVE_PATH),
        }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_summary(result))
    return 0 if result.get("status") == "pass" and result.get("outcome") in PASSING_OUTCOMES else 1


if __name__ == "__main__":
    raise SystemExit(main())
