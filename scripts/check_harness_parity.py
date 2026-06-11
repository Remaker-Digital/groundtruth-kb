#!/usr/bin/env python3
"""Check semantic capability parity across GT-KB AI coding harnesses."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_RELATIVE_PATH = Path("config") / "agent-control" / "harness-capability-registry.toml"
PROJECT_SKILLS_RELATIVE_PATH = Path(".claude") / "skills"

# Guarded import — direct script execution may not have repo root on sys.path.
# Pattern mirrored from scripts/harness_identity.py:14-16 + scripts/harness_roles.py:47-49.
try:
    from scripts.harness_projection_reader import load_harness_projection
except ModuleNotFoundError:
    from harness_projection_reader import load_harness_projection  # type: ignore[no-redef]

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


def _role_applies(capability: dict[str, Any], role: str | None, include_all: bool) -> bool:
    if include_all or role is None:
        return True
    return role in _as_string_list(capability.get("required_for_roles"))


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
                harness_config = {
                    "surface": capability.get("canonical_source"),
                    "status": "native",
                }
            elif kind == "skill":
                cap_id = capability.get("id")
                harness_config = manifest_adapters[harness].get(cap_id)

    if not isinstance(harness_config, dict):
        return CapabilityResult(
            harness=harness,
            capability_id=str(capability.get("id") or ""),
            capability_name=str(capability.get("canonical_name") or ""),
            parity_class=str(capability.get("parity_class") or "baseline"),
            required_for_roles=_as_string_list(capability.get("required_for_roles")),
            configured_status="missing-config",
            state="MISSING",
            evidence="registry lacks harness-specific capability surface",
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
        return CapabilityResult(**common, state="MISSING", note="Fallback surface is declared but absent.")

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
    """Return 'active' | 'registered_no_role' | 'suspended' | 'other' | None from the registry projection.

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
    selected_harnesses = _selected_harnesses(harness, known_harnesses)
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
        else:
            active_harnesses.append(selected_harness)

    harness_manifest_adapters: dict[str, dict[str, dict[str, Any]]] = {}
    harnesses_config = registry.get("harnesses", {})
    for selected_harness in active_harnesses:
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
        for selected_harness in active_harnesses:
            results.append(_status_for_surface(project_root, capability, selected_harness, harness_manifest_adapters))
    for floor_harness in registered_floor_harnesses:
        results.extend(_evaluate_capability_floor(floor_harness, registry))

    extras = _extra_project_skills(project_root, capabilities) if not errors else []
    counts = _count_states(results, extras, errors)
    return ParityReport(
        overall_status=_overall_status(results, extras, errors),
        project_root=str(project_root),
        registry_path=_relative_path(project_root, registry_path),
        selected_harnesses=selected_harnesses,
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
    args = parser.parse_args(argv)

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
