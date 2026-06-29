"""Unified policy-registry inventory for GT-KB governance gates."""

from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.policy.engine import VALID_OUTCOMES

DEFAULT_UNIFIED_REGISTRY_RELATIVE = Path("config") / "agent-control" / "unified-policy-registry.toml"
VALID_ENFORCEMENT_STATUSES = frozenset({"engine_backed", "external_gate", "inventory_only"})


@dataclass(frozen=True)
class UnifiedPolicyAction:
    """One declared action class or external gate inventory entry."""

    table_key: str
    action_class: str
    outcome: str
    message: str
    enforcement_status: str
    decision_source: str
    adapter_installed: bool
    adapter_surfaces: tuple[str, ...]
    harnesses: tuple[str, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "table_key": self.table_key,
            "action_class": self.action_class,
            "outcome": self.outcome,
            "message": self.message,
            "enforcement_status": self.enforcement_status,
            "decision_source": self.decision_source,
            "adapter_installed": self.adapter_installed,
            "adapter_surfaces": list(self.adapter_surfaces),
            "harnesses": list(self.harnesses),
        }


@dataclass(frozen=True)
class UnifiedPolicyRegistry:
    """Parsed unified policy-registry metadata plus integrity hash."""

    schema_version: int
    registry_id: str
    registry_path: Path | None
    registry_hash: str
    actions: dict[str, UnifiedPolicyAction]

    @property
    def actions_by_class(self) -> dict[str, UnifiedPolicyAction]:
        return {action.action_class: action for action in self.actions.values()}

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "registry_id": self.registry_id,
            "registry_path": str(self.registry_path) if self.registry_path else None,
            "registry_hash": self.registry_hash,
            "actions": {key: action.to_json_dict() for key, action in self.actions.items()},
        }


def load_unified_policy_registry(
    path: Path | None = None,
    *,
    start: Path | None = None,
) -> UnifiedPolicyRegistry:
    """Load the unified policy registry from an explicit path or parent search."""
    registry_path = _resolve_registry_path(path, start=start or Path.cwd())
    if registry_path is None:
        raise FileNotFoundError(f"unified policy registry not found at {DEFAULT_UNIFIED_REGISTRY_RELATIVE}")
    _reject_archive_path(registry_path)
    text = registry_path.read_text(encoding="utf-8")
    data = tomllib.loads(text)
    return _parse_registry(data, registry_path=registry_path, registry_hash=_hash_text(text))


def _resolve_registry_path(path: Path | None, *, start: Path) -> Path | None:
    if path is not None:
        return path.resolve()
    current = start.resolve()
    for candidate_root in (current, *current.parents):
        candidate = candidate_root / DEFAULT_UNIFIED_REGISTRY_RELATIVE
        if candidate.exists():
            return candidate
    return None


def _parse_registry(
    data: dict[str, Any],
    *,
    registry_path: Path,
    registry_hash: str,
) -> UnifiedPolicyRegistry:
    schema_version = int(data.get("schema_version", 0))
    if schema_version != 1:
        raise ValueError(f"unsupported unified policy registry schema_version={schema_version!r}")
    registry_id = str(data.get("registry_id", "")).strip()
    if not registry_id:
        raise ValueError("unified policy registry requires registry_id")
    raw_actions = data.get("actions", {})
    if not isinstance(raw_actions, dict) or not raw_actions:
        raise ValueError("unified policy registry requires [actions.*] entries")

    actions: dict[str, UnifiedPolicyAction] = {}
    seen_classes: dict[str, str] = {}
    for table_key, raw_action in raw_actions.items():
        if not isinstance(raw_action, dict):
            raise ValueError(f"action {table_key!r} must be a table")
        action = _parse_action(table_key, raw_action)
        previous = seen_classes.get(action.action_class)
        if previous is not None:
            raise ValueError(f"duplicate action_class {action.action_class!r} in {previous!r} and {table_key!r}")
        seen_classes[action.action_class] = table_key
        actions[table_key] = action
    return UnifiedPolicyRegistry(
        schema_version=schema_version,
        registry_id=registry_id,
        registry_path=registry_path,
        registry_hash=registry_hash,
        actions=actions,
    )


def _parse_action(table_key: str, raw_action: dict[str, Any]) -> UnifiedPolicyAction:
    action_class = str(raw_action.get("action_class", table_key)).strip()
    if not action_class:
        raise ValueError(f"action {table_key!r} requires action_class")
    outcome = str(raw_action.get("outcome", "")).upper()
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"action {table_key!r} has invalid outcome {outcome!r}")
    enforcement_status = str(raw_action.get("enforcement_status", "")).strip()
    if enforcement_status not in VALID_ENFORCEMENT_STATUSES:
        raise ValueError(f"action {table_key!r} has invalid enforcement_status {enforcement_status!r}")
    decision_source = str(raw_action.get("decision_source", "")).strip()
    if not decision_source:
        raise ValueError(f"action {table_key!r} requires decision_source")
    adapter_surfaces = _string_tuple(
        raw_action.get("adapter_surfaces", ()),
        field="adapter_surfaces",
        table_key=table_key,
    )
    harnesses = _string_tuple(raw_action.get("harnesses", ()), field="harnesses", table_key=table_key)
    return UnifiedPolicyAction(
        table_key=table_key,
        action_class=action_class,
        outcome=outcome,
        message=str(raw_action.get("message", "")).strip(),
        enforcement_status=enforcement_status,
        decision_source=decision_source,
        adapter_installed=bool(raw_action.get("adapter_installed", False)),
        adapter_surfaces=adapter_surfaces,
        harnesses=harnesses,
    )


def _string_tuple(value: object, *, field: str, table_key: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"action {table_key!r} requires non-empty {field} list")
    strings = tuple(str(item).strip() for item in value)
    if any(not item for item in strings):
        raise ValueError(f"action {table_key!r} has empty {field} entry")
    return strings


def _reject_archive_path(path: Path) -> None:
    normalized = str(path).replace("/", "\\").lower()
    if "\\claude-playground" in normalized:
        raise ValueError(f"{path} is an archive path and must not be used as the unified policy registry")


def _hash_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
