#!/usr/bin/env python3
"""Check semantic capability parity across GT-KB AI coding harnesses."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tomllib
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent
REGISTRY_RELATIVE_PATH = Path("config") / "agent-control" / "harness-capability-registry.toml"
PROJECT_SKILLS_RELATIVE_PATH = Path(".claude") / "skills"


def _load_sibling_script_module(module_name: str) -> Any:
    module_path = SCRIPT_DIR / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ModuleNotFoundError(f"cannot load local script module {module_name!r} from {module_path}")

    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        if previous is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous
        raise
    return module


load_harness_projection = _load_sibling_script_module("harness_projection_reader").load_harness_projection
codex_adapter_generator = _load_sibling_script_module("generate_codex_skill_adapters")
antigravity_adapter_generator = _load_sibling_script_module("generate_antigravity_skill_adapters")
api_adapter_generator = _load_sibling_script_module("generate_api_skill_adapters")

_FALLBACK_KNOWN_HARNESSES = ("claude", "codex")

# Capability-floor required fields per GOV-HARNESS-ONBOARDING-CONTRACT-001 Layer 3
# (forward-referenced; spec inserted by Child 4 of PROJECT-GTKB-OLLAMA-INTEGRATION).
# Evaluated for registered/no-active-role harnesses by _evaluate_capability_floor().
CAPABILITY_FLOOR_REQUIRED_FIELDS = (
    "bridge_compliance_gate_respect",
    "root_boundary_respect",
    "author_metadata_env_var_setting",
    "destructive_gate_delegation",
    "advertised_tool_subset",
    "tool_guard_adapter_fail_closed",
)
CANONICAL_TOOL_SUBSET = frozenset({"Read", "Write", "Edit", "Grep", "Glob", "Bash"})
ENVELOPE_MODE_FIELDS = {
    "activity_envelope_projection_mode": "Activity envelope projection mode",
    "compact_result_envelope_mode": "Compact result-envelope mode",
    "compact_session_envelope_mode": "Compact session-envelope mode",
}
VALID_ENVELOPE_MODES = frozenset(
    {
        "native",
        "fallback",
        "adapter",
        "generated-adapter",
        "compact-provider",
        "optimized-startup",
        "typed-waiver",
        "documented-limitation",
    }
)

# ── Cross-harness parity schema (Slice 2 of PROJECT-GTKB-CROSS-HARNESS-PARITY) ──
# Additive surface derived from ADR-CROSS-HARNESS-PARITY-001 +
# DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 (assertions PARITY-WAIVER-SCHEMA and
# PARITY-APPLICABILITY-RULE). These accessors/validators are consumed by the
# Slice-3 discovery-diff and the Slice-6 release/CI gate; they do NOT change the
# existing per-capability per-harness parity matrix evaluated by
# check_harness_parity().
PARITY_SCHEMA_VERSION = 1
VALID_APPLICABILITY = frozenset({"role-relative", "universal"})
WAIVER_REASON_CLASSES = frozenset({"hard-limitation", "harness-surface-difference", "deliberate-deferral"})
WAIVER_REQUIRED_FIELDS = (
    "capability_id",
    "harness",
    "reason_class",
    "rationale",
    "owner_approval_ref",
)
OPERATING_ROLES = ("prime-builder", "loyal-opposition")


def _load_known_harnesses_from_projection(project_root: Path | None = None) -> tuple[str, ...]:
    """Derive KNOWN_HARNESSES from registry projection per REQ-HARNESS-REGISTRY-001 FR5.

    Uses scripts.harness_projection_reader (stdlib-only, fail-safe) to satisfy
    the active reader-migration invariant; direct reads of harness-identities.json
    are forbidden under the planted-detector fixture in
    platform_tests/scripts/test_harness_registry_reader_migration.py.
    """
    if project_root is None:
        project_root = PROJECT_ROOT
    projection = load_harness_projection(project_root)
    names = tuple(
        sorted(
            str(record.get("harness_name"))
            for record in projection.get("harnesses", [])
            if isinstance(record, dict) and record.get("harness_name")
        )
    )
    return names if names else _FALLBACK_KNOWN_HARNESSES


KNOWN_HARNESSES = _load_known_harnesses_from_projection()
VALID_STATES = {
    "PASS",
    "DEGRADED",
    "MISSING",
    "STALE",
    "EXTRA",
    "UNSUPPORTED",
    "OWNER_ACTION_REQUIRED",
    "DEFERRED",
}
WARNING_STATES = {
    "DEGRADED",
    "STALE",
    "EXTRA",
    "UNSUPPORTED",
    "OWNER_ACTION_REQUIRED",
}
REQUIRED_PARITY_CLASSES = {"required"}
ROLE_ALIASES = {
    "acting-prime-builder": "prime-builder",
}
GENERATED_MARKER = "<!-- GTKB-CODEX-SKILL-ADAPTER"
GENERATED_END_MARKER = "GTKB-CODEX-SKILL-ADAPTER -->"
ADAPTER_GENERATOR_BY_MARKER = {
    "GTKB-CODEX-SKILL-ADAPTER": "scripts/generate_codex_skill_adapters.py",
    "GTKB-ANTIGRAVITY-SKILL-ADAPTER": "scripts/generate_antigravity_skill_adapters.py",
    "GTKB-API-SKILL-ADAPTER": "scripts/generate_api_skill_adapters.py",
}
FRONTMATTER_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


@dataclass(frozen=True)
class CapabilityResult:
    harness: str
    capability_id: str
    capability_name: str
    parity_class: str
    required_for_roles: list[str]
    configured_status: str
    state: str
    evidence: str
    note: str


@dataclass(frozen=True)
class ExtraResult:
    kind: str
    name: str
    state: str
    evidence: str
    note: str


@dataclass(frozen=True)
class ParityReport:
    overall_status: str
    project_root: str
    registry_path: str
    selected_harnesses: list[str]
    selected_role: str | None
    counts: dict[str, int]
    results: list[CapabilityResult]
    extras: list[ExtraResult]
    errors: list[str]


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _find_markers(text: str, expected_marker: str | None = None) -> tuple[str, str] | None:
    if expected_marker:
        match = re.search(r"<!--\s*(" + re.escape(expected_marker) + r")", text)
    else:
        match = re.search(r"<!--\s*(GTKB-[A-Z0-9_-]+-SKILL-ADAPTER)", text)
    if not match:
        return None
    marker_name = match.group(1)
    start_idx = text.find(marker_name)
    if start_idx == -1:
        return None
    prefix_idx = text.rfind("<!--", 0, start_idx)
    if prefix_idx == -1:
        return None
    start_marker = text[prefix_idx : start_idx + len(marker_name)]
    suffix_match = re.search(re.escape(marker_name) + r"\s*-->", text)
    if not suffix_match:
        return None
    end_marker = suffix_match.group(0)
    return start_marker, end_marker


def _strip_generated_block(text: str, expected_marker: str | None = None) -> str:
    markers = _find_markers(text, expected_marker)
    if not markers:
        return text
    start_marker, end_marker = markers
    start = text.find(start_marker)
    if start == -1:
        return text
    end = text.find(end_marker, start)
    if end == -1:
        return text
    return text[:start] + text[end + len(end_marker) :].lstrip("\r\n")


def _canonical_hash(text: str, expected_marker: str | None = None) -> str:
    return _sha256_text(_strip_generated_block(text, expected_marker).rstrip() + "\n")


def _adapter_metadata(text: str, expected_marker: str | None = None) -> dict[str, str]:
    markers = _find_markers(text, expected_marker)
    if not markers:
        return {}
    start_marker, end_marker = markers
    start = text.find(start_marker)
    if start == -1:
        return {}
    end = text.find(end_marker, start)
    if end == -1:
        return {}
    metadata: dict[str, str] = {}
    for line in text[start:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def _normalized_adapter_semantics(text: str, expected_marker: str) -> str:
    return _strip_generated_block(text, expected_marker).lstrip("\ufeff").rstrip() + "\n"


def _render_expected_adapter(
    *,
    capability: dict[str, Any],
    adapter_source: str,
    surface: str,
    source_text: str,
    source_hash: str,
    expected_marker: str,
) -> str | None:
    """Render the canonical adapter shape without trusting declared hashes alone."""

    generated_at = "1970-01-01T00:00:00Z"
    common = {
        "capability_id": str(capability.get("id") or ""),
        "canonical_name": str(capability.get("canonical_name") or ""),
        "source_relative_path": adapter_source,
        "adapter_relative_path": surface,
        "source_sha256": source_hash,
    }
    if expected_marker == "GTKB-CODEX-SKILL-ADAPTER":
        adapter = codex_adapter_generator.SkillAdapter(**common)
        return codex_adapter_generator.render_adapter(source_text, adapter, generated_at=generated_at)
    if expected_marker == "GTKB-ANTIGRAVITY-SKILL-ADAPTER":
        adapter = antigravity_adapter_generator.SkillAdapter(**common)
        return antigravity_adapter_generator.render_adapter(source_text, adapter, generated_at=generated_at)
    if expected_marker == "GTKB-API-SKILL-ADAPTER":
        canonical_text = api_adapter_generator._strip_generated_block(source_text).lstrip("\ufeff")
        frontmatter = api_adapter_generator.validate_skill_frontmatter(canonical_text, adapter_source)
        adapter = api_adapter_generator.ApiSkillAdapter(description=frontmatter["description"], **common)
        return api_adapter_generator.render_adapter(adapter, generated_at=generated_at)
    return None


def _normalize_role(role: str | None) -> str | None:
    normalized = str(role or "").strip().lower()
    if not normalized:
        return None
    return ROLE_ALIASES.get(normalized, normalized)


def _normalize_harness(value: str, known_harnesses: tuple[str, ...]) -> str:
    normalized = str(value or "").strip().lower()
    if normalized not in (*known_harnesses, "all"):
        raise ValueError(f"unsupported harness: {value}")
    return normalized


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip().lower() for item in value if str(item).strip()]


def _frontmatter_name(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].lstrip("\ufeff").strip() != "---":
        return None
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            return None
        if stripped.startswith("name:"):
            return stripped.split(":", 1)[1].strip().strip("\"'")
    return None


def _skill_frontmatter_error(text: str, path: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].lstrip("\ufeff").strip() != "---":
        return f"{path}: missing opening YAML frontmatter delimiter"

    closing_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        return f"{path}: missing closing YAML frontmatter delimiter"

    fields: dict[str, str] = {}
    for offset, line in enumerate(lines[1:closing_index], start=2):
        if line.startswith((" ", "\t")):
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            continue
        if ":" not in stripped:
            return f"{path}:{offset}: malformed frontmatter line"
        key, value = stripped.split(":", 1)
        key = key.strip()
        if not FRONTMATTER_KEY_RE.match(key):
            return f"{path}:{offset}: invalid frontmatter key {key!r}"
        fields[key] = value.strip().strip("\"'")

    for required in ("name", "description"):
        if not fields.get(required):
            return f"{path}: missing non-empty {required!r} frontmatter field"
    return None


def inventory_project_skills(project_root: Path) -> dict[str, str]:
    """Return project skill directory names mapped to relative SKILL.md paths."""

    skills_root = project_root / PROJECT_SKILLS_RELATIVE_PATH
    if not skills_root.is_dir():
        return {}

    inventory: dict[str, str] = {}
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        skill_name = _frontmatter_name(text) or skill_file.parent.name
        inventory[skill_file.parent.name] = _relative_path(project_root, skill_file)
        inventory.setdefault(skill_name, _relative_path(project_root, skill_file))
    return inventory


def load_registry(project_root: Path) -> tuple[dict[str, Any], Path]:
    registry_path = project_root / REGISTRY_RELATIVE_PATH
    return _load_toml(registry_path), registry_path


def _selected_harnesses(harness: str, known_harnesses: tuple[str, ...]) -> list[str]:
    normalized = _normalize_harness(harness, known_harnesses)
    if normalized == "all":
        return list(known_harnesses)
    return [normalized]


def _assigned_roles_by_harness(project_root: Path) -> dict[str, list[str]]:
    projection = load_harness_projection(project_root)
    assigned: dict[str, list[str]] = {}
    for record in projection.get("harnesses", []):
        if not isinstance(record, dict):
            continue
        if record.get("status") != "active":
            continue
        harness_name = str(record.get("harness_name") or "").strip().lower()
        if not harness_name:
            continue
        roles = [_normalize_role(role) for role in _as_string_list(record.get("role"))]
        assigned[harness_name] = [role for role in roles if role]
    return assigned


def _scope_harnesses_for_role(
    selected_harnesses: list[str],
    *,
    selected_role: str | None,
    explicit_harness: bool,
    include_all: bool,
    project_root: Path,
) -> list[str]:
    if not selected_role or explicit_harness or include_all:
        return selected_harnesses
    assigned_roles = _assigned_roles_by_harness(project_root)
    return [harness for harness in selected_harnesses if selected_role in assigned_roles.get(harness, [])]


def _role_applies(capability: dict[str, Any], role: str | None, include_all: bool) -> bool:
    if include_all or role is None:
        return True
    if resolve_applicability(capability) == "universal":
        return True
    return role in _as_string_list(capability.get("required_for_roles"))


def _active_harnesses_from_selection(selected_harnesses: list[str], project_root: Path) -> list[str]:
    active: list[str] = []
    for selected_harness in selected_harnesses:
        lifecycle = _harness_lifecycle_class(selected_harness, project_root)
        if lifecycle in {"suspended", "registered_no_role", "retired", "other"}:
            continue
        active.append(selected_harness)
    return active


def _coverage_blocking_states() -> set[str]:
    return {"MISSING", "OWNER_ACTION_REQUIRED"}


def _base_result(
    capability: dict[str, Any],
    harness: str,
    *,
    configured_status: str,
    evidence: str,
    state: str,
    note: str,
) -> CapabilityResult:
    return CapabilityResult(
        harness=harness,
        capability_id=str(capability.get("id") or ""),
        capability_name=str(capability.get("canonical_name") or ""),
        parity_class=str(capability.get("parity_class") or "baseline"),
        required_for_roles=_as_string_list(capability.get("required_for_roles")),
        configured_status=configured_status,
        state=state,
        evidence=evidence,
        note=note,
    )


def _status_for_surface(
    project_root: Path,
    capability: dict[str, Any],
    harness: str,
    manifest_adapters: dict[str, dict[str, Any]] | None = None,
) -> CapabilityResult:
    harness_config = capability.get(harness)
    if not isinstance(harness_config, dict):
        if manifest_adapters and harness in manifest_adapters:
            kind = capability.get("kind")
            if kind == "hook":
                return _base_result(
                    capability,
                    harness,
                    configured_status="unsupported",
                    evidence="no hook surface declared",
                    state="UNSUPPORTED",
                    note=(
                        "Skill adapter manifests do not prove hook registration or invocation; "
                        "add an explicit harness hook surface if this capability is supported."
                    ),
                )
            elif kind == "skill":
                cap_id = capability.get("id")
                harness_config = manifest_adapters[harness].get(cap_id)

    if not isinstance(harness_config, dict):
        return _base_result(
            capability,
            harness,
            configured_status="missing-config",
            evidence="registry lacks harness-specific capability surface",
            state="MISSING",
            note="Add a harness-specific registry entry.",
        )

    configured_status = str(harness_config.get("status") or "").strip().lower()
    surface = str(harness_config.get("surface") or "").strip()
    surface_path = project_root / surface if surface else project_root / "__missing_surface__"
    surface_exists = bool(surface and surface_path.is_file())
    evidence = surface if surface else "no surface declared"

    common = {
        "harness": harness,
        "capability_id": str(capability.get("id") or ""),
        "capability_name": str(capability.get("canonical_name") or ""),
        "parity_class": str(capability.get("parity_class") or "baseline"),
        "required_for_roles": _as_string_list(capability.get("required_for_roles")),
        "configured_status": configured_status or "unspecified",
        "evidence": evidence,
    }

    if configured_status == "native":
        if surface_exists:
            return CapabilityResult(**common, state="PASS", note="Native surface exists.")
        return CapabilityResult(**common, state="MISSING", note="Native surface is declared but absent.")

    if configured_status == "fallback":
        if surface_exists:
            return CapabilityResult(
                **common,
                state="DEGRADED",
                note=str(harness_config.get("fallback") or "Fallback surface exists."),
            )
        return CapabilityResult(
            **common,
            state="DEFERRED",
            note="Fallback surface is declared but absent (deferred; dedicated generator tracked separately).",
        )

    if configured_status == "adapter":
        if not surface_exists:
            return CapabilityResult(**common, state="MISSING", note="Generated adapter surface is absent.")
        adapter_text = surface_path.read_text(encoding="utf-8")
        load_error = _skill_frontmatter_error(adapter_text, surface)
        if load_error is not None:
            return CapabilityResult(
                **common,
                state="MISSING",
                note=f"Generated adapter is not Codex-loadable: {load_error}",
            )
        adapter_source = str(harness_config.get("adapter_source") or capability.get("canonical_source") or "").strip()
        if not adapter_source:
            return CapabilityResult(**common, state="STALE", note="Generated adapter lacks an adapter_source.")
        source_path = project_root / adapter_source
        if not source_path.is_file():
            return CapabilityResult(**common, state="MISSING", note=f"Adapter source is absent: {adapter_source}")
        if manifest_adapters and harness in manifest_adapters:
            expected_marker = "GTKB-API-SKILL-ADAPTER"
            source_expected_marker = "GTKB-API-SKILL-ADAPTER"
        else:
            expected_marker = f"GTKB-{harness.upper()}-SKILL-ADAPTER"
            source_expected_marker = "GTKB-CODEX-SKILL-ADAPTER"
        source_hash = _canonical_hash(source_path.read_text(encoding="utf-8"), source_expected_marker)
        declared_source_hash = str(harness_config.get("source_sha256") or "").strip()
        metadata = _adapter_metadata(adapter_text, expected_marker)
        expected_generator = ADAPTER_GENERATOR_BY_MARKER.get(expected_marker)
        if metadata.get("Generated by") != expected_generator:
            return CapabilityResult(
                **common,
                state="STALE",
                note=f"Generated adapter has an unsupported or missing generator identity for {expected_marker}.",
            )
        if not metadata.get("Generated at"):
            return CapabilityResult(
                **common,
                state="STALE",
                note="Generated adapter lacks a generation timestamp.",
            )
        adapter_source_hash = metadata.get("Canonical source sha256", "")
        adapter_source_path = metadata.get("Canonical source", "")
        if declared_source_hash and declared_source_hash != source_hash:
            return CapabilityResult(
                **common,
                state="STALE",
                note="Registry source_sha256 does not match the canonical source.",
            )
        if adapter_source_path != adapter_source:
            return CapabilityResult(
                **common,
                state="STALE",
                note="Adapter metadata points at a different canonical source.",
            )
        if adapter_source_hash != source_hash:
            return CapabilityResult(
                **common,
                state="STALE",
                note="Generated adapter hash does not match the canonical source.",
            )
        try:
            expected_adapter = _render_expected_adapter(
                capability=capability,
                adapter_source=adapter_source,
                surface=surface,
                source_text=source_path.read_text(encoding="utf-8"),
                source_hash=source_hash,
                expected_marker=expected_marker,
            )
        except (TypeError, ValueError) as exc:
            return CapabilityResult(
                **common,
                state="STALE",
                note=f"Canonical adapter semantics could not be rendered: {exc}",
            )
        if expected_adapter is None:
            return CapabilityResult(
                **common,
                state="STALE",
                note=f"No semantic adapter renderer is registered for {expected_marker}.",
            )
        if _normalized_adapter_semantics(adapter_text, expected_marker) != _normalized_adapter_semantics(
            expected_adapter, expected_marker
        ):
            return CapabilityResult(
                **common,
                state="STALE",
                note="Generated adapter semantics do not match the canonical generator output.",
            )
        return CapabilityResult(**common, state="PASS", note="Generated adapter matches the canonical source.")

    if configured_status == "unsupported":
        return CapabilityResult(
            **common,
            state="UNSUPPORTED",
            note=str(harness_config.get("reason") or "Unsupported state is explicitly registered."),
        )

    if configured_status == "owner-action-required":
        return CapabilityResult(
            **common,
            state="OWNER_ACTION_REQUIRED",
            note=str(harness_config.get("reason") or "External owner-controlled setup is required."),
        )

    return CapabilityResult(
        **common,
        state="STALE",
        note=f"Unknown configured status {configured_status!r}; update the registry schema or entry.",
    )


def _registry_skill_dirs(capabilities: list[dict[str, Any]]) -> set[str]:
    skill_dirs: set[str] = set()
    for capability in capabilities:
        if capability.get("kind") != "skill":
            continue
        canonical_source = str(capability.get("canonical_source") or "")
        path = Path(canonical_source)
        if path.name == "SKILL.md" and path.parent.name:
            skill_dirs.add(path.parent.name)
        canonical_name = str(capability.get("canonical_name") or "").strip()
        if canonical_name:
            skill_dirs.add(canonical_name)
    return skill_dirs


def _extra_project_skills(project_root: Path, capabilities: list[dict[str, Any]]) -> list[ExtraResult]:
    registry_skill_names = _registry_skill_dirs(capabilities)
    extras: list[ExtraResult] = []
    for skill_name, skill_path in inventory_project_skills(project_root).items():
        if skill_name in registry_skill_names:
            continue
        extras.append(
            ExtraResult(
                kind="skill",
                name=skill_name,
                state="EXTRA",
                evidence=skill_path,
                note="Project skill exists but is not declared in the harness capability registry.",
            )
        )
    return sorted(extras, key=lambda item: item.name)


def _count_states(results: list[CapabilityResult], extras: list[ExtraResult], errors: list[str]) -> dict[str, int]:
    counts = {state: 0 for state in sorted(VALID_STATES)}
    for result in results:
        counts[result.state] = counts.get(result.state, 0) + 1
    for extra in extras:
        counts[extra.state] = counts.get(extra.state, 0) + 1
    if errors:
        counts["MISSING"] = counts.get("MISSING", 0) + len(errors)
    return {state: count for state, count in counts.items() if count}


def _overall_status(results: list[CapabilityResult], extras: list[ExtraResult], errors: list[str]) -> str:
    if errors:
        return "FAIL"
    for result in results:
        if result.state == "MISSING" and result.parity_class in REQUIRED_PARITY_CLASSES:
            return "FAIL"
    if any(result.state in WARNING_STATES for result in results):
        return "WARN"
    if any(extra.state in WARNING_STATES for extra in extras):
        return "WARN"
    return "PASS"


def _harness_lifecycle_class(harness_name: str, project_root: Path = PROJECT_ROOT) -> str | None:
    """Return the harness lifecycle class from the registry projection.

    Used by check_harness_parity() to route registered/no-active-role harnesses (status=registered
    AND role=[]) through the capability-floor evaluation path instead of per-capability checks.
    """
    projection = load_harness_projection(project_root)
    for record in projection.get("harnesses", []):
        if not isinstance(record, dict) or record.get("harness_name") != harness_name:
            continue
        status = record.get("status")
        role = record.get("role") or []
        if status == "suspended":
            return "suspended"
        if status == "retired":
            return "retired"
        if status == "registered" and role == []:
            return "registered_no_role"
        if status == "active":
            return "active"
        return "other"
    return None


def _evaluate_capability_floor(harness_name: str, registry_data: dict[str, Any]) -> list[CapabilityResult]:
    """For registered/no-active-role harnesses, evaluate the top-level [harnesses.<name>] floor.

    Returns a list of CapabilityResult rows (NOT ExtraResult) so the existing _overall_status()
    MISSING-fails-required-parity semantic applies. Per F8 fix (Codex NO-GO -008): modeling
    floor checks as CapabilityResult with parity_class='required' makes missing/incomplete
    floor data mechanically force overall_status='FAIL' and CLI exit code 1.
    """
    floor = registry_data.get("harnesses", {}).get(harness_name, {}) if isinstance(registry_data, dict) else {}
    results: list[CapabilityResult] = []
    for field in CAPABILITY_FLOOR_REQUIRED_FIELDS:
        present = isinstance(floor, dict) and field in floor
        results.append(
            CapabilityResult(
                harness=harness_name,
                capability_id=f"capability_floor.{field}",
                capability_name=f"Capability floor: {field}",
                parity_class="required",
                required_for_roles=["registered_no_role"],
                configured_status="declared" if present else "missing",
                state="PASS" if present else "MISSING",
                evidence=f"config/agent-control/harness-capability-registry.toml::[harnesses.{harness_name}].{field}",
                note=("" if present else f"Required capability-floor field '{field}' not declared"),
            )
        )
    # Advertised-tool-subset extra-tools check: non-canonical entries also MISSING (FAIL).
    if isinstance(floor, dict):
        advertised = floor.get("advertised_tool_subset", [])
        if advertised:
            try:
                extras = set(advertised) - CANONICAL_TOOL_SUBSET
            except TypeError:
                extras = {"<unhashable>"}
            if extras:
                results.append(
                    CapabilityResult(
                        harness=harness_name,
                        capability_id="capability_floor.advertised_tool_subset.canonical",
                        capability_name="Capability floor: advertised_tool_subset is subset of canonical 6-tuple",
                        parity_class="required",
                        required_for_roles=["registered_no_role"],
                        configured_status="extra_tools",
                        state="MISSING",
                        evidence=f"[harnesses.{harness_name}].advertised_tool_subset",
                        note=f"Non-canonical tools in advertised_tool_subset: {sorted(extras)}",
                    )
                )
    return results


def _activity_envelope_projection_results(
    selected_harnesses: list[str],
    registry_data: dict[str, Any],
) -> list[CapabilityResult]:
    """Verify each selected harness declares activity/result/session envelope posture."""
    harnesses_config = registry_data.get("harnesses", {}) if isinstance(registry_data, dict) else {}
    results: list[CapabilityResult] = []
    for harness_name in selected_harnesses:
        floor = harnesses_config.get(harness_name, {}) if isinstance(harnesses_config, dict) else {}
        floor = floor if isinstance(floor, dict) else {}
        if not (any(field in floor for field in ENVELOPE_MODE_FIELDS) or "full_transcript_archive_required" in floor):
            continue
        for field, label in ENVELOPE_MODE_FIELDS.items():
            value = str(floor.get(field) or "").strip()
            valid = value in VALID_ENVELOPE_MODES
            results.append(
                CapabilityResult(
                    harness=harness_name,
                    capability_id=f"activity_envelope.{field}",
                    capability_name=label,
                    parity_class="required",
                    required_for_roles=["prime-builder", "loyal-opposition"],
                    configured_status=value or "missing",
                    state="PASS" if valid else "MISSING",
                    evidence=f"config/agent-control/harness-capability-registry.toml::[harnesses.{harness_name}].{field}",
                    note=("" if valid else f"Required activity-envelope field '{field}' is missing or invalid."),
                )
            )
        transcript_required = floor.get("full_transcript_archive_required")
        transcript_independent = transcript_required is False
        results.append(
            CapabilityResult(
                harness=harness_name,
                capability_id="activity_envelope.full_transcript_archive_independence",
                capability_name="Full transcript archive independence",
                parity_class="required",
                required_for_roles=["prime-builder", "loyal-opposition"],
                configured_status=str(transcript_required).lower()
                if isinstance(transcript_required, bool)
                else "missing",
                state="PASS" if transcript_independent else "MISSING",
                evidence=(
                    "config/agent-control/harness-capability-registry.toml::"
                    f"[harnesses.{harness_name}].full_transcript_archive_required"
                ),
                note=(
                    ""
                    if transcript_independent
                    else "Harness must be assessable through compact result/session envelopes without full transcript archives."
                ),
            )
        )
    return results


def resolve_applicability(capability: dict[str, Any]) -> str:
    """Resolve a capability's parity applicability (PARITY-APPLICABILITY-RULE).

    An explicit valid ``applicability`` field wins. Otherwise the default is
    ``role-relative`` when ``required_for_roles`` is non-empty (the capability
    is role-specific) and ``universal`` when it is empty (session/governance).
    """
    explicit = str(capability.get("applicability") or "").strip().lower()
    if explicit in VALID_APPLICABILITY:
        return explicit
    return "role-relative" if _as_string_list(capability.get("required_for_roles")) else "universal"


def build_surface_map(registry: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    """Per-capability per-harness surface map: ``id -> {harness: {surface, status}}``.

    Formalizes the per-harness surface map the ADR demotes the registry to. The
    harness subtables are detected structurally (any capability value that is a
    table carrying a ``surface`` key), so the map tracks whatever harnesses a
    capability declares without a hardcoded harness list.
    """
    raw = registry.get("capabilities")
    capabilities = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []
    surface_map: dict[str, dict[str, dict[str, Any]]] = {}
    for capability in capabilities:
        cap_id = str(capability.get("id") or "")
        if not cap_id:
            continue
        harness_surfaces: dict[str, dict[str, Any]] = {}
        for key, value in capability.items():
            if isinstance(value, dict) and "surface" in value:
                harness_surfaces[key] = {
                    "surface": value.get("surface"),
                    "status": value.get("status"),
                }
        surface_map[cap_id] = harness_surfaces
    return surface_map


def load_parity_waivers(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the typed ``[[parity_waivers]]`` records (empty list when absent)."""
    raw = registry.get("parity_waivers")
    return [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []


def _waiver_lookup(registry: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for waiver in load_parity_waivers(registry):
        cap_id = str(waiver.get("capability_id") or "").strip()
        harness = str(waiver.get("harness") or "").strip().lower()
        if cap_id and harness:
            lookup[(cap_id, harness)] = waiver
    return lookup


def _apply_waiver(result: CapabilityResult, waiver: dict[str, Any] | None) -> CapabilityResult:
    if result.state != "MISSING" or waiver is None:
        return result
    reason_class = str(waiver.get("reason_class") or "").strip()
    owner_ref = str(waiver.get("owner_approval_ref") or "").strip()
    rationale = str(waiver.get("rationale") or "").strip()
    state = "OWNER_ACTION_REQUIRED" if reason_class == "deliberate-deferral" else "UNSUPPORTED"
    note_parts = ["Approved parity waiver"]
    if owner_ref:
        note_parts.append(owner_ref)
    if reason_class:
        note_parts.append(f"({reason_class})")
    if rationale:
        note_parts.append(f": {rationale}")
    return replace(
        result,
        configured_status=f"waived:{reason_class or 'unspecified'}",
        state=state,
        note=" ".join(note_parts),
    )


def _fleet_role_coverage_results(
    project_root: Path,
    *,
    selected_harnesses: list[str],
    capabilities: list[dict[str, Any]],
    waivers: dict[tuple[str, str], dict[str, Any]],
    manifest_adapters: dict[str, dict[str, dict[str, Any]]],
    selected_role: str | None,
    explicit_harness: bool,
) -> list[CapabilityResult]:
    """Return fleet-level proof rows for role readiness.

    The row is PASS when at least one active harness assigned the role has no
    unwaived required role-relative capability blocker. Explicit single-harness
    diagnostics stay harness-local and do not emit fleet rows.
    """
    if explicit_harness:
        return []

    roles = [selected_role] if selected_role else list(OPERATING_ROLES)
    assigned_roles = _assigned_roles_by_harness(project_root)
    active_selected = _active_harnesses_from_selection(selected_harnesses, project_root)
    results: list[CapabilityResult] = []

    for role in roles:
        if role not in OPERATING_ROLES:
            continue
        candidates = [harness for harness in active_selected if role in assigned_roles.get(harness, [])]
        ready: list[str] = []
        blocked_notes: list[str] = []
        for harness in candidates:
            blockers: list[str] = []
            for capability in capabilities:
                if resolve_applicability(capability) != "role-relative":
                    continue
                if role not in _as_string_list(capability.get("required_for_roles")):
                    continue
                result = _status_for_surface(project_root, capability, harness, manifest_adapters)
                result = _apply_waiver(result, waivers.get((result.capability_id, harness)))
                if result.parity_class in REQUIRED_PARITY_CLASSES and result.state in _coverage_blocking_states():
                    blockers.append(f"{result.capability_id}:{result.state}")
            if blockers:
                blocked_notes.append(f"{harness} blocked by {', '.join(sorted(blockers))}")
            else:
                ready.append(harness)

        if ready:
            state = "PASS"
            note = f"At least one active harness assigned `{role}` covers required role-relative capabilities: {', '.join(ready)}."
        elif candidates:
            state = "MISSING"
            note = "No active assigned harness covers required role-relative capabilities after waivers."
            if blocked_notes:
                note += " " + "; ".join(blocked_notes)
        else:
            state = "MISSING"
            note = f"No active harness is assigned `{role}`."

        results.append(
            CapabilityResult(
                harness="fleet",
                capability_id=f"fleet.role-coverage.{role}",
                capability_name=f"Fleet role coverage: {role}",
                parity_class="required",
                required_for_roles=[role],
                configured_status="computed",
                state=state,
                evidence="harness-state/harness-registry.json + config/agent-control/harness-capability-registry.toml",
                note=note,
            )
        )

    return results


def validate_parity_waiver(waiver: dict[str, Any]) -> list[str]:
    """Validate one typed waiver record (PARITY-WAIVER-SCHEMA). Empty list = valid."""
    if not isinstance(waiver, dict):
        return ["waiver is not a table"]
    errors: list[str] = []
    for field in WAIVER_REQUIRED_FIELDS:
        value = waiver.get(field)
        if not (isinstance(value, str) and value.strip()):
            errors.append(f"missing required waiver field {field!r}")
    reason_class = str(waiver.get("reason_class") or "").strip()
    if reason_class and reason_class not in WAIVER_REASON_CLASSES:
        errors.append(f"invalid reason_class {reason_class!r} (expected one of {sorted(WAIVER_REASON_CLASSES)})")
    has_trigger = bool(str(waiver.get("review_trigger") or "").strip())
    has_expiry = bool(str(waiver.get("expiry") or "").strip())
    if not (has_trigger or has_expiry):
        errors.append("waiver must declare a review_trigger or an expiry")
    return errors


def validate_parity_schema(
    registry: dict[str, Any],
    *,
    known_harnesses: tuple[str, ...] | set[str] | None = None,
) -> list[str]:
    """Validate the cross-harness parity schema. Empty list = valid.

    Checks: ``parity_schema_version`` present and current; every capability's
    explicit ``applicability`` (when set) is a valid value; every waiver record
    validates and references a registered capability id and a known harness.
    """
    if not isinstance(registry, dict):
        return ["registry is not a table"]
    errors: list[str] = []

    version = registry.get("parity_schema_version")
    if version != PARITY_SCHEMA_VERSION:
        errors.append(f"parity_schema_version is {version!r}; expected {PARITY_SCHEMA_VERSION}")

    raw_caps = registry.get("capabilities")
    capabilities = [item for item in raw_caps if isinstance(item, dict)] if isinstance(raw_caps, list) else []
    capability_ids: set[str] = set()
    for capability in capabilities:
        cap_id = str(capability.get("id") or "")
        if cap_id:
            capability_ids.add(cap_id)
        explicit = capability.get("applicability")
        if explicit is not None and str(explicit).strip().lower() not in VALID_APPLICABILITY:
            errors.append(
                f"capability {cap_id!r} has invalid applicability {explicit!r} "
                f"(expected one of {sorted(VALID_APPLICABILITY)})"
            )

    if known_harnesses is None:
        known = set(_load_known_harnesses_from_projection())
    else:
        known = set(known_harnesses)
    for index, waiver in enumerate(load_parity_waivers(registry)):
        for err in validate_parity_waiver(waiver):
            errors.append(f"parity_waivers[{index}]: {err}")
        cap_ref = str(waiver.get("capability_id") or "")
        if cap_ref and cap_ref not in capability_ids:
            errors.append(f"parity_waivers[{index}]: capability_id {cap_ref!r} matches no registered capability")
        harness_ref = str(waiver.get("harness") or "")
        if harness_ref and known and harness_ref not in known:
            errors.append(f"parity_waivers[{index}]: harness {harness_ref!r} is not a known harness {sorted(known)}")
    return errors


def _check_rename_map_consistency(project_root: Path) -> list[dict[str, str]]:
    """Compare on-disk skill dirs against skill-rename-map.toml (GFR Slice D Finding 4.5)."""
    import tomllib

    rename_map_path = project_root / "config" / "agent-control" / "skill-rename-map.toml"
    if not rename_map_path.is_file():
        return []
    with rename_map_path.open("rb") as f:
        payload = tomllib.load(f)
    skills_dir = project_root / ".claude" / "skills"
    findings: list[dict[str, str]] = []
    for entry in payload.get("skills", []):
        expected_dir = entry.get("dir", "")
        canonical_name = entry.get("canonical_name", "")
        if not expected_dir:
            continue
        expected_path = skills_dir / expected_dir
        if not expected_path.is_dir():
            # Check if a dir with a different name exists
            actual_dirs = [d.name for d in skills_dir.iterdir() if d.is_dir()] if skills_dir.is_dir() else []
            for actual in actual_dirs:
                skill_md = skills_dir / actual / "SKILL.md"
                if skill_md.is_file():
                    content = skill_md.read_text(encoding="utf-8")
                    name_match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
                    if name_match and name_match.group(1).strip() == canonical_name:
                        findings.append(
                            {
                                "type": "STALE_NAME",
                                "expected_dir": expected_dir,
                                "actual_dir": actual,
                                "canonical_name": canonical_name,
                            }
                        )
                        break
        # Check frontmatter name matches canonical_name
        skill_md = expected_path / "SKILL.md"
        if skill_md.is_file():
            content = skill_md.read_text(encoding="utf-8")
            name_match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
            if name_match:
                actual_name = name_match.group(1).strip()
                if actual_name != canonical_name:
                    findings.append(
                        {
                            "type": "NAME_MISMATCH",
                            "dir": expected_dir,
                            "canonical_name": canonical_name,
                            "actual_name": actual_name,
                        }
                    )
    return findings


def check_harness_parity(
    project_root: Path = PROJECT_ROOT,
    *,
    harness: str = "all",
    role: str | None = None,
    include_all: bool = False,
) -> ParityReport:
    project_root = project_root.resolve()
    known_harnesses = _load_known_harnesses_from_projection(project_root)
    selected_role = _normalize_role(role)
    normalized_harness = _normalize_harness(harness, known_harnesses)
    explicit_harness = normalized_harness != "all"
    base_selected_harnesses = _selected_harnesses(normalized_harness, known_harnesses)
    selected_harnesses = list(base_selected_harnesses)
    selected_harnesses = _scope_harnesses_for_role(
        selected_harnesses,
        selected_role=selected_role,
        explicit_harness=explicit_harness,
        include_all=include_all,
        project_root=project_root,
    )
    errors: list[str] = []

    try:
        registry, registry_path = load_registry(project_root)
    except FileNotFoundError:
        registry_path = project_root / REGISTRY_RELATIVE_PATH
        registry = {}
        errors.append(f"missing registry: {_relative_path(project_root, registry_path)}")
    except tomllib.TOMLDecodeError as exc:
        registry_path = project_root / REGISTRY_RELATIVE_PATH
        registry = {}
        errors.append(f"invalid registry TOML: {exc}")

    raw_capabilities = registry.get("capabilities")
    capabilities = (
        [item for item in raw_capabilities if isinstance(item, dict)] if isinstance(raw_capabilities, list) else []
    )
    if registry and not capabilities:
        errors.append("registry has no capability entries")
    waivers = _waiver_lookup(registry)

    # Split selected harnesses by lifecycle class so registered/no-active-role harnesses
    # are evaluated against the top-level [harnesses.<name>] capability floor rather than
    # the per-capability per-harness subtable matrix (which only applies to active harnesses
    # with role assignments). Per Codex GO at gtkb-ollama-integration-phase-1-foundation-010.
    active_harnesses: list[str] = []
    registered_floor_harnesses: list[str] = []
    for selected_harness in selected_harnesses:
        lifecycle = _harness_lifecycle_class(selected_harness, project_root)
        if lifecycle == "suspended":
            continue
        if lifecycle == "registered_no_role":
            registered_floor_harnesses.append(selected_harness)
        elif lifecycle in {"retired", "other"} and not explicit_harness:
            continue
        else:
            active_harnesses.append(selected_harness)
    operative_harnesses = set(active_harnesses) | set(registered_floor_harnesses)
    report_selected_harnesses = [
        selected_harness for selected_harness in selected_harnesses if selected_harness in operative_harnesses
    ]
    universal_active_harnesses = _active_harnesses_from_selection(base_selected_harnesses, project_root)

    harness_manifest_adapters: dict[str, dict[str, dict[str, Any]]] = {}
    harnesses_config = registry.get("harnesses", {})
    for selected_harness in sorted(set(active_harnesses) | set(universal_active_harnesses)):
        floor = harnesses_config.get(selected_harness, {})
        manifest_path_str = floor.get("skill_adapter_manifest") if isinstance(floor, dict) else None
        if manifest_path_str:
            manifest_path = project_root / manifest_path_str
            if manifest_path.is_file():
                try:
                    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
                    adapters_list = manifest_data.get("adapters", [])
                    adapters_map = {}
                    for entry in adapters_list:
                        cap_id = entry.get("capability_id")
                        if cap_id:
                            adapters_map[cap_id] = {
                                "surface": entry.get("adapter_relative_path"),
                                "status": "adapter",
                                "adapter_source": entry.get("source_relative_path"),
                                "source_sha256": entry.get("source_sha256"),
                            }
                    harness_manifest_adapters[selected_harness] = adapters_map
                except Exception as exc:
                    errors.append(f"failed to load manifest for {selected_harness} at {manifest_path_str}: {exc}")

    results: list[CapabilityResult] = []
    for capability in capabilities:
        if not _role_applies(capability, selected_role, include_all):
            continue
        applicability = resolve_applicability(capability)
        capability_harnesses = (
            universal_active_harnesses
            if applicability == "universal" and selected_role and not explicit_harness and not include_all
            else active_harnesses
        )
        for selected_harness in capability_harnesses:
            result = _status_for_surface(project_root, capability, selected_harness, harness_manifest_adapters)
            results.append(_apply_waiver(result, waivers.get((result.capability_id, selected_harness))))
    for floor_harness in registered_floor_harnesses:
        results.extend(_evaluate_capability_floor(floor_harness, registry))
    envelope_harnesses = (
        universal_active_harnesses if selected_role and not explicit_harness and not include_all else active_harnesses
    )
    results.extend(_activity_envelope_projection_results(envelope_harnesses, registry))
    results.extend(
        _fleet_role_coverage_results(
            project_root,
            selected_harnesses=base_selected_harnesses,
            capabilities=capabilities,
            waivers=waivers,
            manifest_adapters=harness_manifest_adapters,
            selected_role=selected_role,
            explicit_harness=explicit_harness,
        )
    )

    extras = _extra_project_skills(project_root, capabilities) if not errors else []
    counts = _count_states(results, extras, errors)
    return ParityReport(
        overall_status=_overall_status(results, extras, errors),
        project_root=str(project_root),
        registry_path=_relative_path(project_root, registry_path),
        selected_harnesses=report_selected_harnesses,
        selected_role=selected_role,
        counts=counts,
        results=results,
        extras=extras,
        errors=errors,
    )


def _markdown_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{state}: {count}" for state, count in sorted(counts.items()))


def format_markdown(report: ParityReport, *, show_pass: bool = False) -> str:
    scope_role = report.selected_role or "all roles"
    lines = [
        "# Harness Parity Review",
        "",
        f"- Overall status: {report.overall_status}",
        f"- Project root: {report.project_root}",
        f"- Registry: {report.registry_path}",
        f"- Harnesses: {', '.join(report.selected_harnesses)}",
        f"- Role scope: {scope_role}",
        f"- Counts: {_markdown_counts(report.counts)}",
    ]

    if report.errors:
        lines.extend(["", "## Errors"])
        lines.extend(f"- {error}" for error in report.errors)

    displayed_results = [result for result in report.results if show_pass or result.state != "PASS"]
    if displayed_results:
        lines.extend(
            [
                "",
                "## Capability Findings",
                "",
                "| Harness | Capability | Class | State | Evidence | Note |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for result in displayed_results:
            note = result.note.replace("|", "\\|")
            lines.append(
                f"| {result.harness} | {result.capability_name} | {result.parity_class} | "
                f"{result.state} | {result.evidence} | {note} |"
            )

    if report.extras:
        lines.extend(
            [
                "",
                "## Undeclared Project Surfaces",
                "",
                "| Kind | Name | State | Evidence | Note |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for extra in report.extras:
            note = extra.note.replace("|", "\\|")
            lines.append(f"| {extra.kind} | {extra.name} | {extra.state} | {extra.evidence} | {note} |")

    if not displayed_results and not report.extras and not report.errors:
        lines.extend(["", "No parity issues found in the selected scope."])

    return "\n".join(lines) + "\n"


def _json_default(value: Any) -> Any:
    if isinstance(value, ParityReport):
        payload = asdict(value)
        payload["results"] = [asdict(result) for result in value.results]
        payload["extras"] = [asdict(extra) for extra in value.extras]
        return payload
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--harness", default="all", choices=[*KNOWN_HARNESSES, "all"])
    parser.add_argument("--role", default=None)
    parser.add_argument("--all", action="store_true", help="Check every registered capability regardless of role.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown.")
    parser.add_argument("--show-pass", action="store_true", help="Include PASS rows in Markdown output.")
    parser.add_argument(
        "--validate-schema",
        action="store_true",
        help="Validate the cross-harness parity schema (applicability + waiver records) and exit.",
    )
    parser.add_argument(
        "--strict-on-rename",
        action="store_true",
        help="Compare on-disk skill dirs against skill-rename-map.toml and flag stale names.",
    )
    args = parser.parse_args(argv)

    if args.validate_schema:
        try:
            registry, _ = load_registry(args.project_root.resolve())
        except FileNotFoundError:
            print("parity schema INVALID:\n  - registry file not found")
            return 1
        except tomllib.TOMLDecodeError as exc:
            print(f"parity schema INVALID:\n  - invalid registry TOML: {exc}")
            return 1
        schema_errors = validate_parity_schema(registry)
        if schema_errors:
            print("parity schema INVALID:")
            for err in schema_errors:
                print(f"  - {err}")
            return 1
        print("parity schema OK")
        return 0

    if args.strict_on_rename:
        findings = _check_rename_map_consistency(args.project_root.resolve())
        if findings:
            print("STALE NAME / NAME_MISMATCH findings:")
            for f in findings:
                print(f"  - {f['type']}: {f}")
            return 1
        print("strict-on-rename: all skill dirs consistent with skill-rename-map.toml")
        return 0

    report = check_harness_parity(
        args.project_root,
        harness=args.harness,
        role=args.role,
        include_all=args.all,
    )

    if args.json:
        print(json.dumps(report, default=_json_default, indent=2, sort_keys=True))
    else:
        print(format_markdown(report, show_pass=args.show_pass), end="")

    return 1 if report.overall_status == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
