#!/usr/bin/env python3
"""Check semantic capability parity across GT-KB AI coding harnesses."""

from __future__ import annotations

import argparse
import hashlib
import json
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_RELATIVE_PATH = Path("config") / "agent-control" / "harness-capability-registry.toml"
PROJECT_SKILLS_RELATIVE_PATH = Path(".claude") / "skills"
KNOWN_HARNESSES = ("claude", "codex")
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


def _strip_generated_block(text: str) -> str:
    start = text.find(GENERATED_MARKER)
    if start == -1:
        return text
    end = text.find(GENERATED_END_MARKER, start)
    if end == -1:
        return text
    return text[:start] + text[end + len(GENERATED_END_MARKER) :].lstrip("\r\n")


def _canonical_hash(text: str) -> str:
    return _sha256_text(_strip_generated_block(text).rstrip() + "\n")


def _adapter_metadata(text: str) -> dict[str, str]:
    start = text.find(GENERATED_MARKER)
    if start == -1:
        return {}
    end = text.find(GENERATED_END_MARKER, start)
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


def _normalize_harness(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized not in (*KNOWN_HARNESSES, "all"):
        raise ValueError(f"unsupported harness: {value}")
    return normalized


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip().lower() for item in value if str(item).strip()]


def _frontmatter_name(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            return None
        if stripped.startswith("name:"):
            return stripped.split(":", 1)[1].strip().strip("\"'")
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


def _selected_harnesses(harness: str) -> list[str]:
    normalized = _normalize_harness(harness)
    if normalized == "all":
        return list(KNOWN_HARNESSES)
    return [normalized]


def _role_applies(capability: dict[str, Any], role: str | None, include_all: bool) -> bool:
    if include_all or role is None:
        return True
    return role in _as_string_list(capability.get("required_for_roles"))


def _status_for_surface(
    project_root: Path,
    capability: dict[str, Any],
    harness: str,
) -> CapabilityResult:
    harness_config = capability.get(harness)
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
        adapter_source = str(harness_config.get("adapter_source") or capability.get("canonical_source") or "").strip()
        if not adapter_source:
            return CapabilityResult(**common, state="STALE", note="Generated adapter lacks an adapter_source.")
        source_path = project_root / adapter_source
        if not source_path.is_file():
            return CapabilityResult(**common, state="MISSING", note=f"Adapter source is absent: {adapter_source}")
        source_hash = _canonical_hash(source_path.read_text(encoding="utf-8"))
        declared_source_hash = str(harness_config.get("source_sha256") or "").strip()
        adapter_text = surface_path.read_text(encoding="utf-8")
        metadata = _adapter_metadata(adapter_text)
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


def check_harness_parity(
    project_root: Path = PROJECT_ROOT,
    *,
    harness: str = "all",
    role: str | None = None,
    include_all: bool = False,
) -> ParityReport:
    project_root = project_root.resolve()
    selected_role = _normalize_role(role)
    selected_harnesses = _selected_harnesses(harness)
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

    results: list[CapabilityResult] = []
    for capability in capabilities:
        if not _role_applies(capability, selected_role, include_all):
            continue
        for selected_harness in selected_harnesses:
            results.append(_status_for_surface(project_root, capability, selected_harness))

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
