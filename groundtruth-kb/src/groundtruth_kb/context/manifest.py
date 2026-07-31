"""Deterministic registry-derived session and activity context manifests."""

from __future__ import annotations

import hashlib
import json
import os
import tomllib
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.activity.profiles import CANONICAL_ACTIVITY_ORDER, load_activity_profiles
from groundtruth_kb.context.freshness import HIGH_CHURN_CLASSES, evaluate_extract
from groundtruth_kb.context.resource_routing import ResourceRoutingError, validate_resource_contract

PACKAGED_REGISTRY_VERSION = 1
PACKAGED_REGISTRY_ROOT = Path(__file__).resolve().parent / "registries" / f"v{PACKAGED_REGISTRY_VERSION}"
DEFAULT_REGISTRY = PACKAGED_REGISTRY_ROOT / "context-manifests.toml"
PROJECT_REGISTRY_RELATIVE_PATH = Path("config/registry/context-manifests.toml")
ACTIVITY_PROFILES_RELATIVE_PATH = Path("config/agent-control/activity-disposition-profiles.toml")
ACTIVITY_SHARDING_RELATIVE_PATH = Path("config/agent-control/activity-envelope-sharding.toml")
REQUIRED_CATEGORIES = (
    "glossary",
    "skills",
    "cli",
    "source_of_truth",
    "project_and_backlog",
    "operating_context",
    "work_subject",
)
STACK_ORDER = ("native_hints", "session_baseline", "role_bootstrap", "activity_overlay")
REQUIRED_RESOURCE_ITEM_SEMANTICS = {
    "baseline.project-and-backlog": {
        "source_id": "membase-project-and-backlog-state",
        "authority_class": "canonical_live_state",
        "read_route": "gt projects list; gt backlog list",
    },
    "activity.project-and-backlog": {
        "source_id": "membase-project-and-backlog-state",
        "authority_class": "canonical_live_state",
        "read_route": "gt projects show; gt backlog list",
    },
    "baseline.work-subject": {
        "source_id": "membase-work-item-state",
        "authority_class": "canonical_live_state",
        "read_route": "gt backlog list",
    },
    "activity.work-subject": {
        "source_id": "membase-work-item-state",
        "authority_class": "canonical_live_state",
        "read_route": "gt backlog list",
    },
}


class ContextManifestError(RuntimeError):
    """Raised when context cannot be assembled without ambiguity or omission."""


@dataclass(frozen=True)
class ContextRegistryResolution:
    """Closed registry and source-root selection for one assembly."""

    registry_path: Path
    source_root: Path
    origin: str


@dataclass(frozen=True)
class RegistryItem:
    id: str
    layer: str
    category: str
    source_id: str
    source_path: str
    authority_class: str
    lifecycle: str
    churn_class: str
    embedding: str
    ttl_seconds: int | None
    read_route: str
    mutation_route: str
    recovery_route: str
    applicability: tuple[str, ...]
    projection: str
    token_cost: int
    priority: int
    essential: bool


@dataclass(frozen=True)
class ContextRegistry:
    version: int
    categories: tuple[str, ...]
    activities: tuple[str, ...]
    soft_token_budget: int
    hard_token_budget: int
    resource_contract: dict[str, Any]
    items: tuple[RegistryItem, ...]


def _source_checkout_root() -> Path | None:
    """Return the deterministic repository root only for the source layout."""

    module_path = Path(__file__).resolve()
    if module_path.parents[2].name != "src" or module_path.parents[3].name != "groundtruth-kb":
        return None
    candidate = module_path.parents[4]
    expected = candidate / "groundtruth-kb" / "src" / "groundtruth_kb" / "context" / "manifest.py"
    if expected.resolve() != module_path or not (candidate / PROJECT_REGISTRY_RELATIVE_PATH).is_file():
        return None
    return candidate


def _resolve_project_root(project_root: Path | None) -> Path:
    if project_root is not None:
        return project_root.resolve()
    if configured := os.environ.get("GTKB_PROJECT_ROOT"):
        return Path(configured).resolve()
    working_root = Path.cwd().resolve()
    if (working_root / PROJECT_REGISTRY_RELATIVE_PATH).is_file():
        return working_root
    return _source_checkout_root() or working_root


def resolve_context_registry(
    *,
    project_root: Path | None = None,
    registry_path: Path | None = None,
) -> ContextRegistryResolution:
    """Resolve an explicit registry, a project override, or the packaged default.

    An explicit registry is strict and uses ``project_root`` for all source
    references. A project override is selected only when the canonical
    project-relative path exists. Missing sources in either mode fail closed;
    they never fall through to package data. With no override, the immutable
    versioned package resources provide both the registry and its source set.
    """

    resolved_project_root = _resolve_project_root(project_root)
    if registry_path is not None:
        explicit_path = registry_path if registry_path.is_absolute() else resolved_project_root / registry_path
        return ContextRegistryResolution(
            registry_path=explicit_path.resolve(),
            source_root=resolved_project_root,
            origin="explicit",
        )

    project_registry = resolved_project_root / PROJECT_REGISTRY_RELATIVE_PATH
    if project_registry.is_file():
        return ContextRegistryResolution(
            registry_path=project_registry,
            source_root=resolved_project_root,
            origin="project_override",
        )

    return ContextRegistryResolution(
        registry_path=DEFAULT_REGISTRY,
        source_root=PACKAGED_REGISTRY_ROOT,
        origin="packaged_default",
    )


def _required_string(raw: dict[str, Any], field: str, item_id: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ContextManifestError(f"{item_id}: missing {field}")
    return value.strip()


def load_context_registry(
    path: Path | None = None,
    *,
    project_root: Path | None = None,
) -> ContextRegistry:
    resolution = resolve_context_registry(project_root=project_root, registry_path=path)
    try:
        payload = tomllib.loads(resolution.registry_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ContextManifestError(f"context registry unreadable: {exc}") from exc
    if payload.get("schema_version") != 1:
        raise ContextManifestError("context registry schema_version must be 1")
    meta = payload.get("manifest")
    if not isinstance(meta, dict):
        raise ContextManifestError("context registry manifest metadata is missing")
    categories = tuple(meta.get("categories") or [])
    activities = tuple(meta.get("activities") or [])
    if categories != REQUIRED_CATEGORIES:
        raise ContextManifestError(f"categories must be exactly {list(REQUIRED_CATEGORIES)}")
    if activities != CANONICAL_ACTIVITY_ORDER:
        raise ContextManifestError(f"activities must be exactly {list(CANONICAL_ACTIVITY_ORDER)}")
    try:
        resource_contract = validate_resource_contract(payload.get("resource_contract"))
    except ResourceRoutingError as exc:
        raise ContextManifestError(str(exc)) from exc

    items: list[RegistryItem] = []
    for index, raw in enumerate(payload.get("items") or []):
        if not isinstance(raw, dict):
            raise ContextManifestError(f"item {index + 1} must be a table")
        item_id = _required_string(raw, "id", f"item-{index + 1}")
        item = RegistryItem(
            id=item_id,
            layer=_required_string(raw, "layer", item_id),
            category=_required_string(raw, "category", item_id),
            source_id=_required_string(raw, "source_id", item_id),
            source_path=_required_string(raw, "source_path", item_id),
            authority_class=_required_string(raw, "authority_class", item_id),
            lifecycle=_required_string(raw, "lifecycle", item_id),
            churn_class=_required_string(raw, "churn_class", item_id),
            embedding=_required_string(raw, "embedding", item_id),
            ttl_seconds=raw.get("ttl_seconds"),
            read_route=_required_string(raw, "read_route", item_id),
            mutation_route=_required_string(raw, "mutation_route", item_id),
            recovery_route=_required_string(raw, "recovery_route", item_id),
            applicability=tuple(raw.get("applicability") or []),
            projection=_required_string(raw, "projection", item_id),
            token_cost=int(raw.get("token_cost") or 0),
            priority=int(raw.get("priority") or 0),
            essential=raw.get("essential") is True,
        )
        if item.layer not in {"session_baseline", "activity_overlay"}:
            raise ContextManifestError(f"{item.id}: invalid layer {item.layer}")
        if item.category not in REQUIRED_CATEGORIES:
            raise ContextManifestError(f"{item.id}: invalid category {item.category}")
        if item.embedding not in {"embedded", "live_query_only"}:
            raise ContextManifestError(f"{item.id}: invalid embedding {item.embedding}")
        if item.churn_class in HIGH_CHURN_CLASSES and item.embedding != "live_query_only":
            raise ContextManifestError(f"{item.id}: high-churn items must be live_query_only")
        if item.token_cost < 1 or not item.applicability:
            raise ContextManifestError(f"{item.id}: invalid token cost or applicability")
        items.append(item)
    ids = [item.id for item in items]
    if len(ids) != len(set(ids)):
        raise ContextManifestError("context registry item ids must be unique")
    for layer in ("session_baseline", "activity_overlay"):
        layer_categories = {item.category for item in items if item.layer == layer}
        if layer_categories != set(REQUIRED_CATEGORIES):
            raise ContextManifestError(f"{layer} must classify all seven categories")
    items_by_id = {item.id: item for item in items}
    for item_id, expected in REQUIRED_RESOURCE_ITEM_SEMANTICS.items():
        item = items_by_id.get(item_id)
        if item is None:
            raise ContextManifestError(f"{item_id}: required resource descriptor is missing")
        for field, value in expected.items():
            if getattr(item, field) != value:
                raise ContextManifestError(
                    f"{item_id}: {field} must be {value!r}; backlog and bridge routes cannot be swapped or aliased"
                )
    return ContextRegistry(
        version=int(meta.get("version") or 1),
        categories=categories,
        activities=activities,
        soft_token_budget=int(meta.get("soft_token_budget") or 0),
        hard_token_budget=int(meta.get("hard_token_budget") or 0),
        resource_contract=resource_contract,
        items=tuple(items),
    )


def _source_hash(project_root: Path, item: RegistryItem) -> str:
    source = project_root / item.source_path
    if not source.is_file():
        raise ContextManifestError(f"{item.id}: source is missing; recovery={item.recovery_route}")
    return hashlib.sha256(source.read_bytes()).hexdigest().upper()


def _project_content(item: RegistryItem, activity: str, profiles: dict[str, Any]) -> Any:
    if item.embedding == "live_query_only":
        return None
    profile = profiles[activity]
    projections = {
        "profile.terminology": profile.terminology,
        "profile.skills": profile.skills,
        "profile.history_state": profile.history_state,
        "profile.direction": profile.direction,
    }
    return projections.get(item.projection, {"source": item.source_id, "route": item.read_route})


def assemble_context_manifest(
    *,
    activity: str,
    role: str,
    generated_at: datetime | None = None,
    evaluated_at: datetime | None = None,
    registry_path: Path | None = None,
    project_root: Path | None = None,
    soft_token_budget: int | None = None,
    hard_token_budget: int | None = None,
) -> dict[str, Any]:
    resolution = resolve_context_registry(project_root=project_root, registry_path=registry_path)
    registry = load_context_registry(resolution.registry_path, project_root=resolution.source_root)
    if activity not in registry.activities:
        raise ContextManifestError(f"one-active activity must be one of {list(registry.activities)}")
    if not isinstance(role, str) or not role.strip():
        raise ContextManifestError("role-bootstrap requires an explicit role before-activity")
    generation_time = (generated_at or datetime.now(UTC)).astimezone(UTC)
    evaluation_time = (evaluated_at or generation_time).astimezone(UTC)
    profiles = load_activity_profiles(
        path=resolution.source_root / ACTIVITY_PROFILES_RELATIVE_PATH,
        sharding_path=resolution.source_root / ACTIVITY_SHARDING_RELATIVE_PATH,
    )
    candidates: list[dict[str, Any]] = []
    conflict_keys: dict[tuple[str, str, str], tuple[str, str]] = {}
    for item in registry.items:
        if "*" not in item.applicability and activity not in item.applicability:
            continue
        key = (item.layer, item.category, item.source_id)
        authority_route = (item.authority_class, item.read_route)
        if key in conflict_keys and conflict_keys[key] != authority_route:
            raise ContextManifestError(f"conflict for {item.source_id}; recovery={item.recovery_route}")
        conflict_keys[key] = authority_route
        content = _project_content(item, activity, profiles)
        source_version = (
            "live-query" if item.embedding == "live_query_only" else _source_hash(resolution.source_root, item)
        )
        freshness_record = {
            "source_id": item.source_id,
            "source_path": item.source_path,
            "authority_class": item.authority_class,
            "source_version_or_hash": source_version,
            "churn_class": item.churn_class,
            "generated_at": generation_time.isoformat(),
            "ttl_seconds": item.ttl_seconds,
            "bounded_usage_context": f"session:{activity}",
            "live_query_route": item.read_route,
            "recovery_route": item.recovery_route,
            "embedded_content": content,
        }
        freshness = evaluate_extract(freshness_record, now=evaluation_time)
        if not freshness["eligible_as_current"]:
            raise ContextManifestError(
                f"{item.id}: unavailable/expired/conflict context; "
                f"reasons={freshness['reasons']}; recovery={item.recovery_route}"
            )
        candidates.append(
            {
                **asdict(item),
                "applicability": list(item.applicability),
                "source_version_or_hash": source_version,
                "content": content,
                "disposition": "live-query-only" if content is None else "embedded",
                "freshness": freshness,
                "inclusion_reason": f"{item.layer}:{item.category}:{activity}",
            }
        )

    candidates.sort(key=lambda item: (STACK_ORDER.index(item["layer"]), -item["priority"], item["id"]))
    soft_budget = registry.soft_token_budget if soft_token_budget is None else soft_token_budget
    hard_budget = registry.hard_token_budget if hard_token_budget is None else hard_token_budget
    essential_cost = sum(item["token_cost"] for item in candidates if item["essential"])
    if essential_cost > hard_budget:
        raise ContextManifestError("essential-context exceeds token-budget and must-not-discard")
    included: list[dict[str, Any]] = []
    omitted: list[dict[str, Any]] = []
    token_total = 0
    for item in candidates:
        if not item["essential"] and token_total + item["token_cost"] > soft_budget:
            omitted.append({"id": item["id"], "reason": "soft token-budget"})
            continue
        included.append(item)
        token_total += item["token_cost"]
    if token_total > hard_budget:
        raise ContextManifestError("token-budget exceeds hard limit")
    layer_categories = {
        layer: sorted({item["category"] for item in included if item["layer"] == layer})
        for layer in ("session_baseline", "activity_overlay")
    }
    if any(set(categories) != set(REQUIRED_CATEGORIES) for categories in layer_categories.values()):
        raise ContextManifestError("essential-context category omission must-not-discard")
    return {
        "schema_version": 1,
        "registry_version": registry.version,
        "generated_at": generation_time.isoformat(),
        "stack_order": list(STACK_ORDER),
        "role_bootstrap": {"role": role.strip(), "cannot_alter_role": True},
        "resource_contract": registry.resource_contract,
        "active_activity": activity,
        "categories_by_layer": layer_categories,
        "token_budget": {"soft": soft_budget, "hard": hard_budget, "actual": token_total},
        "items": included,
        "omissions": omitted,
    }


def validate_manifest_resource_semantics(manifest: object) -> None:
    """Validate semantic resource closure in one assembled manifest."""

    if not isinstance(manifest, dict):
        raise ContextManifestError("assembled context manifest must be an object")
    try:
        validate_resource_contract(manifest.get("resource_contract"))
    except ResourceRoutingError as exc:
        raise ContextManifestError(str(exc)) from exc
    items = manifest.get("items")
    if not isinstance(items, list):
        raise ContextManifestError("assembled context manifest items are missing")
    items_by_id = {item.get("id"): item for item in items if isinstance(item, dict)}
    for item_id, expected in REQUIRED_RESOURCE_ITEM_SEMANTICS.items():
        item = items_by_id.get(item_id)
        if item is None:
            raise ContextManifestError(f"{item_id}: required resource descriptor is missing")
        for field, value in expected.items():
            if item.get(field) != value:
                raise ContextManifestError(
                    f"{item_id}: {field} must be {value!r}; backlog and bridge routes cannot be swapped or aliased"
                )


def canonical_manifest_bytes(manifest: dict[str, Any]) -> bytes:
    return json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
