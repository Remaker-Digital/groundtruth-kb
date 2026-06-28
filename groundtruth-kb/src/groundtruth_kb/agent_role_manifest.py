"""Declarative agent/role manifest inventory loader for WI-4552."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_AGENT_ROLE_MANIFEST_RELATIVE = Path("config") / "agent-control" / "declarative-agent-role-manifest.yaml"
VALID_AUTHORITY_STATUSES = frozenset({"inventory_only"})
VALID_DISPATCH_MODES = frozenset({"dispatch_target", "event_source", "manual_only", "unavailable"})
VALID_ROLE_IDS = frozenset({"loyal-opposition", "prime-builder"})


@dataclass(frozen=True)
class AgentRoleManifestRole:
    """One declarative role inventory record."""

    role_id: str
    title: str
    counterpart_role: str
    prompt_surfaces: tuple[str, ...]
    tool_surfaces: tuple[str, ...]
    review_surfaces: tuple[str, ...]
    harness_applicability: tuple[str, ...]
    authority_notes: tuple[str, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "role_id": self.role_id,
            "title": self.title,
            "counterpart_role": self.counterpart_role,
            "prompt_surfaces": list(self.prompt_surfaces),
            "tool_surfaces": list(self.tool_surfaces),
            "review_surfaces": list(self.review_surfaces),
            "harness_applicability": list(self.harness_applicability),
            "authority_notes": list(self.authority_notes),
        }


@dataclass(frozen=True)
class AgentRoleManifestHarness:
    """One declarative harness inventory record."""

    harness_id: str
    harness_name: str
    harness_type: str
    status: str
    roles: tuple[str, ...]
    dispatch_mode: str
    can_fire_events: bool
    can_receive_dispatch: bool
    invocation_surfaces: tuple[str, ...]
    hook_surfaces: tuple[str, ...]
    notes: tuple[str, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "harness_id": self.harness_id,
            "harness_name": self.harness_name,
            "harness_type": self.harness_type,
            "status": self.status,
            "roles": list(self.roles),
            "dispatch_mode": self.dispatch_mode,
            "can_fire_events": self.can_fire_events,
            "can_receive_dispatch": self.can_receive_dispatch,
            "invocation_surfaces": list(self.invocation_surfaces),
            "hook_surfaces": list(self.hook_surfaces),
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class AgentRoleManifest:
    """Parsed manifest plus integrity hash for inventory consumers."""

    schema_version: int
    manifest_id: str
    authority_status: str
    manifest_path: Path | None
    manifest_hash: str
    description: str
    source_of_truth_refs: tuple[str, ...]
    canonical_reader_refs: tuple[str, ...]
    role_schema_anchors: tuple[str, ...]
    roles: dict[str, AgentRoleManifestRole]
    harnesses: dict[str, AgentRoleManifestHarness]

    @property
    def dispatch_targets(self) -> dict[str, AgentRoleManifestHarness]:
        return {key: harness for key, harness in self.harnesses.items() if harness.can_receive_dispatch}

    @property
    def event_sources(self) -> dict[str, AgentRoleManifestHarness]:
        return {key: harness for key, harness in self.harnesses.items() if harness.can_fire_events}

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "manifest_id": self.manifest_id,
            "authority_status": self.authority_status,
            "manifest_path": str(self.manifest_path) if self.manifest_path else None,
            "manifest_hash": self.manifest_hash,
            "description": self.description,
            "source_of_truth_refs": list(self.source_of_truth_refs),
            "canonical_reader_refs": list(self.canonical_reader_refs),
            "role_schema_anchors": list(self.role_schema_anchors),
            "roles": {key: role.to_json_dict() for key, role in self.roles.items()},
            "harnesses": {key: harness.to_json_dict() for key, harness in self.harnesses.items()},
        }


def load_agent_role_manifest(
    path: Path | None = None,
    *,
    start: Path | None = None,
) -> AgentRoleManifest:
    """Load the inventory-only declarative role manifest."""

    manifest_path = _resolve_manifest_path(path, start=start or Path.cwd())
    if manifest_path is None:
        raise FileNotFoundError(f"agent role manifest not found at {DEFAULT_AGENT_ROLE_MANIFEST_RELATIVE}")
    _reject_archive_path(manifest_path)
    text = manifest_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("agent role manifest requires a mapping at top level")
    return _parse_manifest(data, manifest_path=manifest_path, manifest_hash=_hash_text(text))


def _resolve_manifest_path(path: Path | None, *, start: Path) -> Path | None:
    if path is not None:
        return path.resolve()
    current = start.resolve()
    for candidate_root in (current, *current.parents):
        candidate = candidate_root / DEFAULT_AGENT_ROLE_MANIFEST_RELATIVE
        if candidate.exists():
            return candidate
    return None


def _parse_manifest(
    data: dict[str, Any],
    *,
    manifest_path: Path,
    manifest_hash: str,
) -> AgentRoleManifest:
    schema_version = int(data.get("schema_version", 0))
    if schema_version != 1:
        raise ValueError(f"unsupported agent role manifest schema_version={schema_version!r}")
    manifest_id = _required_string(data, field="manifest_id", context="manifest")
    authority_status = _required_string(data, field="authority_status", context="manifest")
    if authority_status not in VALID_AUTHORITY_STATUSES:
        raise ValueError(f"manifest has invalid authority_status {authority_status!r}")

    roles = _parse_roles(data.get("roles"))
    if set(roles) != VALID_ROLE_IDS:
        raise ValueError(f"manifest roles must be exactly {sorted(VALID_ROLE_IDS)}")

    harnesses = _parse_harnesses(data.get("harnesses"))
    return AgentRoleManifest(
        schema_version=schema_version,
        manifest_id=manifest_id,
        authority_status=authority_status,
        manifest_path=manifest_path,
        manifest_hash=manifest_hash,
        description=_required_string(data, field="description", context="manifest"),
        source_of_truth_refs=_string_tuple(
            data.get("source_of_truth_refs"),
            field="source_of_truth_refs",
            context="manifest",
        ),
        canonical_reader_refs=_string_tuple(
            data.get("canonical_reader_refs"),
            field="canonical_reader_refs",
            context="manifest",
        ),
        role_schema_anchors=_string_tuple(
            data.get("role_schema_anchors"),
            field="role_schema_anchors",
            context="manifest",
        ),
        roles=roles,
        harnesses=harnesses,
    )


def _parse_roles(raw_roles: object) -> dict[str, AgentRoleManifestRole]:
    if not isinstance(raw_roles, list) or not raw_roles:
        raise ValueError("manifest requires non-empty roles list")
    roles: dict[str, AgentRoleManifestRole] = {}
    for raw_role in raw_roles:
        if not isinstance(raw_role, dict):
            raise ValueError("role entries must be mappings")
        role = _parse_role(raw_role)
        if role.role_id in roles:
            raise ValueError(f"duplicate role_id {role.role_id!r}")
        roles[role.role_id] = role
    return roles


def _parse_role(raw_role: dict[str, Any]) -> AgentRoleManifestRole:
    role_id = _required_string(raw_role, field="role_id", context="role")
    if role_id not in VALID_ROLE_IDS:
        raise ValueError(f"unknown role_id {role_id!r}")
    counterpart_role = _required_string(raw_role, field="counterpart_role", context=role_id)
    if counterpart_role not in VALID_ROLE_IDS or counterpart_role == role_id:
        raise ValueError(f"role {role_id!r} has invalid counterpart_role {counterpart_role!r}")
    return AgentRoleManifestRole(
        role_id=role_id,
        title=_required_string(raw_role, field="title", context=role_id),
        counterpart_role=counterpart_role,
        prompt_surfaces=_string_tuple(raw_role.get("prompt_surfaces"), field="prompt_surfaces", context=role_id),
        tool_surfaces=_string_tuple(raw_role.get("tool_surfaces"), field="tool_surfaces", context=role_id),
        review_surfaces=_string_tuple(raw_role.get("review_surfaces"), field="review_surfaces", context=role_id),
        harness_applicability=_string_tuple(
            raw_role.get("harness_applicability"),
            field="harness_applicability",
            context=role_id,
        ),
        authority_notes=_string_tuple(raw_role.get("authority_notes"), field="authority_notes", context=role_id),
    )


def _parse_harnesses(raw_harnesses: object) -> dict[str, AgentRoleManifestHarness]:
    if not isinstance(raw_harnesses, list) or not raw_harnesses:
        raise ValueError("manifest requires non-empty harnesses list")
    harnesses: dict[str, AgentRoleManifestHarness] = {}
    for raw_harness in raw_harnesses:
        if not isinstance(raw_harness, dict):
            raise ValueError("harness entries must be mappings")
        harness = _parse_harness(raw_harness)
        if harness.harness_id in harnesses:
            raise ValueError(f"duplicate harness_id {harness.harness_id!r}")
        harnesses[harness.harness_id] = harness
    return harnesses


def _parse_harness(raw_harness: dict[str, Any]) -> AgentRoleManifestHarness:
    harness_id = _required_string(raw_harness, field="harness_id", context="harness")
    roles = _role_tuple(raw_harness.get("roles"), context=harness_id)
    dispatch_mode = _required_string(raw_harness, field="dispatch_mode", context=harness_id)
    if dispatch_mode not in VALID_DISPATCH_MODES:
        raise ValueError(f"harness {harness_id!r} has invalid dispatch_mode {dispatch_mode!r}")
    return AgentRoleManifestHarness(
        harness_id=harness_id,
        harness_name=_required_string(raw_harness, field="harness_name", context=harness_id),
        harness_type=_required_string(raw_harness, field="harness_type", context=harness_id),
        status=_required_string(raw_harness, field="status", context=harness_id),
        roles=roles,
        dispatch_mode=dispatch_mode,
        can_fire_events=_bool_field(raw_harness, field="can_fire_events", context=harness_id),
        can_receive_dispatch=_bool_field(raw_harness, field="can_receive_dispatch", context=harness_id),
        invocation_surfaces=_string_tuple(
            raw_harness.get("invocation_surfaces"),
            field="invocation_surfaces",
            context=harness_id,
        ),
        hook_surfaces=_string_tuple(
            raw_harness.get("hook_surfaces"),
            field="hook_surfaces",
            context=harness_id,
            allow_empty=True,
        ),
        notes=_string_tuple(raw_harness.get("notes"), field="notes", context=harness_id),
    )


def _role_tuple(value: object, *, context: str) -> tuple[str, ...]:
    roles = _string_tuple(value, field="roles", context=context)
    unknown = sorted(role for role in roles if role not in VALID_ROLE_IDS)
    if unknown:
        raise ValueError(f"{context} references unknown role token(s): {', '.join(unknown)}")
    return roles


def _required_string(data: dict[str, Any], *, field: str, context: str) -> str:
    value = str(data.get(field, "")).strip()
    if not value:
        raise ValueError(f"{context} requires {field}")
    return value


def _string_tuple(
    value: object,
    *,
    field: str,
    context: str,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{context} requires {field} list")
    if not value and not allow_empty:
        raise ValueError(f"{context} requires non-empty {field} list")
    strings = tuple(str(item).strip() for item in value)
    if any(not item for item in strings):
        raise ValueError(f"{context} has empty {field} entry")
    return strings


def _bool_field(data: dict[str, Any], *, field: str, context: str) -> bool:
    value = data.get(field)
    if not isinstance(value, bool):
        raise ValueError(f"{context} requires boolean {field}")
    return value


def _reject_archive_path(path: Path) -> None:
    normalized = str(path).replace("/", "\\").lower()
    if "\\claude-playground" in normalized:
        raise ValueError(f"{path} is an archive path and must not be used as an agent role manifest")


def _hash_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
