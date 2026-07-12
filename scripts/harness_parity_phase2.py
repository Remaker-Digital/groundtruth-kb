#!/usr/bin/env python3
"""Evaluate Harness Parity Phase 2 readiness without mutating project state."""

from __future__ import annotations

import argparse
import json
import tomllib
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ID = "PROJECT-HARNESS-PARITY-PHASE-2"
WORK_ITEM_ID = "WI-4899"
EVALUATOR_WORK_ITEM_ID = "WI-4900"
WAIVER_REGISTRY_WORK_ITEM_ID = "WI-4901"
PROJECT_AUTHORIZATION = "PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29"
BRIDGE_ID = "gtkb-harness-parity-phase-2-codex-baseline-matrix"
WAIVER_REGISTRY_BRIDGE_ID = "gtkb-wi4901-phase2-waiver-registry"

DEFAULT_WAIVER_PATH = Path("config") / "harness-parity" / "phase2-waivers.toml"
HARNESS_REGISTRY_PATH = Path("harness-state") / "harness-registry.json"
CAPABILITY_REGISTRY_PATH = Path("config") / "agent-control" / "harness-capability-registry.toml"
DISPATCHER_RULES_PATH = Path("config") / "dispatcher" / "rules.toml"

NO_WINDOW_EVIDENCE_PATHS_BY_HARNESS = {
    "antigravity": ("scripts/dispatcher_runtime.py",),
    "claude": ("scripts/dispatcher_runtime.py",),
    "codex": (
        "scripts/dispatcher_runtime.py",
        ".codex/hooks.json",
        ".codex/gtkb-hooks/run_cmd_no_window.py",
    ),
    "cursor": ("scripts/cursor_harness.py",),
    "ollama": ("scripts/ollama_harness.py",),
    "openrouter": ("scripts/openrouter_harness.py", "scripts/dispatcher_runtime.py"),
    "alibaba-cloud-studio": ("scripts/alibaba_cloud_studio_harness.py", "scripts/dispatcher_runtime.py"),
}
NO_WINDOW_EVIDENCE_TOKENS = (
    "create_no_window",
    "run_cmd_no_window",
    "windowstyle hidden",
    "windowstyle",
    "no-window",
    "no_window",
)

GAP_STATES = {"needs_adapter", "blocked", "impossible"}
FAILURE_STATES = GAP_STATES | {"invalid_waiver"}
WAIVER_REASON_CLASSES = {
    "impossible",
    "vendor_limitation",
    "deliberate_deferral",
    "owner_accepted_risk",
}
WAIVER_STATUSES = {"active", "retired"}
WAIVER_EVALUATOR_BEHAVIORS = {"waive"}


@dataclass(frozen=True)
class Dimension:
    id: str
    title: str
    release_blocking: bool
    work_item_template: str


@dataclass(frozen=True)
class Cell:
    harness: str
    harness_id: str
    dimension: str
    title: str
    status: str
    release_blocking: bool
    evidence: list[str]
    details: str
    waiver_id: str | None = None


@dataclass(frozen=True)
class CandidateWorkItem:
    harness: str
    dimension: str
    title: str
    description: str
    suggested_command: str


DIMENSIONS = (
    Dimension(
        id="registry_projection",
        title="Harness registry projection",
        release_blocking=True,
        work_item_template=(
            "Repair the {harness} harness registry projection so Phase 2 can evaluate identity, status, "
            "role, and invocation metadata deterministically."
        ),
    ),
    Dimension(
        id="headless_invocation",
        title="Headless invocation surface",
        release_blocking=True,
        work_item_template=(
            "Add or repair the {harness} headless invocation surface so dispatch and recurring parity probes can "
            "launch it without interactive setup."
        ),
    ),
    Dimension(
        id="dispatcher_receive",
        title="Dispatcher receive capability",
        release_blocking=True,
        work_item_template=(
            "Make the {harness} dispatcher receive configuration truthful and release-ready, or record a typed "
            "Phase 2 waiver if the harness cannot receive dispatched work."
        ),
    ),
    Dimension(
        id="event_source",
        title="Event-source capability",
        release_blocking=False,
        work_item_template=(
            "Classify and implement the {harness} event-source path, or record why this harness is receive-only "
            "for Phase 2."
        ),
    ),
    Dimension(
        id="skill_projection",
        title="Skill projection surface",
        release_blocking=True,
        work_item_template=(
            "Close the {harness} skill projection gap against the Codex baseline, including manifest or adapter "
            "evidence where the harness uses generated skills."
        ),
    ),
    Dimension(
        id="hook_projection",
        title="Hook or governed-helper surface",
        release_blocking=True,
        work_item_template=(
            "Close the {harness} hook/governed-helper parity gap so bridge, credential, and root-boundary behavior "
            "has an inspectable enforcement route."
        ),
    ),
    Dimension(
        id="bridge_write_path",
        title="Bridge write and verdict path",
        release_blocking=True,
        work_item_template=(
            "Provide {harness} bridge proposal/report/verdict helper evidence, or record a typed waiver for any "
            "unsupported bridge-write class."
        ),
    ),
    Dimension(
        id="readiness_probe",
        title="Readiness probe",
        release_blocking=True,
        work_item_template=(
            "Add a deterministic {harness} readiness probe that Phase 2 release checks can execute before "
            "dispatching work."
        ),
    ),
    Dimension(
        id="provider_settings",
        title="Provider or adapter settings",
        release_blocking=True,
        work_item_template=(
            "Add or repair provider/adapter settings for {harness}, including model/routing evidence when this "
            "harness is backed by a provider shim."
        ),
    ),
    Dimension(
        id="no_window_launch",
        title="No-window launch evidence",
        release_blocking=True,
        work_item_template=(
            "Add static or runtime no-window launch evidence for {harness} so Windows background dispatch cannot "
            "flash visible consoles."
        ),
    ),
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _exists(root: Path, rel_path: str | Path) -> bool:
    return (root / rel_path).is_file() or (root / rel_path).is_dir()


def _harness_config(capability_registry: dict[str, Any], harness_name: str) -> dict[str, Any]:
    harnesses = capability_registry.get("harnesses", {})
    if isinstance(harnesses, dict):
        value = harnesses.get(harness_name, {})
        if isinstance(value, dict):
            return value
    return {}


def _load_waivers(root: Path, waiver_path: Path) -> tuple[list[dict[str, Any]], list[Cell]]:
    full_path = waiver_path if waiver_path.is_absolute() else root / waiver_path
    if not full_path.exists():
        return [], [
            Cell(
                harness="*",
                harness_id="*",
                dimension="waiver_registry",
                title="Typed waiver registry",
                status="invalid_waiver",
                release_blocking=True,
                evidence=[_rel(root, full_path)],
                details="Typed waiver registry is missing.",
            )
        ]
    try:
        data = _load_toml(full_path)
    except tomllib.TOMLDecodeError as exc:
        return [], [
            Cell(
                harness="*",
                harness_id="*",
                dimension="waiver_registry",
                title="Typed waiver registry",
                status="invalid_waiver",
                release_blocking=True,
                evidence=[_rel(root, full_path)],
                details=f"Typed waiver registry is invalid TOML: {exc}",
            )
        ]

    raw_waivers = data.get("waivers", [])
    if raw_waivers is None:
        raw_waivers = []
    if not isinstance(raw_waivers, list):
        return [], [
            Cell(
                harness="*",
                harness_id="*",
                dimension="waiver_registry",
                title="Typed waiver registry",
                status="invalid_waiver",
                release_blocking=True,
                evidence=[_rel(root, full_path)],
                details="Typed waiver registry field 'waivers' must be an array of tables.",
            )
        ]

    waivers = [item for item in raw_waivers if isinstance(item, dict)]
    validation_cells: list[Cell] = []
    for index, raw_waiver in enumerate(raw_waivers):
        if not isinstance(raw_waiver, dict):
            validation_cells.append(
                Cell(
                    harness="*",
                    harness_id="*",
                    dimension="waiver_registry",
                    title="Typed waiver registry",
                    status="invalid_waiver",
                    release_blocking=True,
                    evidence=[f"{_rel(root, full_path)}::waivers[{index}]"],
                    details="Waiver record must be a TOML table.",
                    waiver_id=f"waiver[{index}]",
                )
            )
            continue
        waiver = raw_waiver
        errors = validate_waiver(waiver)
        if errors:
            validation_cells.append(
                Cell(
                    harness=str(waiver.get("harness") or "*"),
                    harness_id="*",
                    dimension="waiver_registry",
                    title="Typed waiver registry",
                    status="invalid_waiver",
                    release_blocking=True,
                    evidence=[f"{_rel(root, full_path)}::waivers[{index}]"],
                    details="; ".join(errors),
                    waiver_id=str(waiver.get("id") or f"waiver[{index}]"),
                )
            )
    return waivers, validation_cells


def validate_waiver(waiver: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = (
        "id",
        "harness",
        "dimension",
        "reason_class",
        "rationale",
        "owner_decision",
        "evidence",
        "evaluator_behavior",
        "status",
    )
    for field in required:
        if not str(waiver.get(field) or "").strip():
            errors.append(f"missing required field {field!r}")
    dimension = str(waiver.get("dimension") or "").strip()
    valid_dimensions = {dimension.id for dimension in DIMENSIONS} | {"*"}
    if dimension and dimension not in valid_dimensions:
        errors.append(f"invalid dimension {dimension!r}")
    reason_class = str(waiver.get("reason_class") or "").strip()
    if reason_class and reason_class not in WAIVER_REASON_CLASSES:
        errors.append(f"invalid reason_class {reason_class!r}")
    behavior = str(waiver.get("evaluator_behavior") or "").strip()
    if behavior and behavior not in WAIVER_EVALUATOR_BEHAVIORS:
        errors.append(f"invalid evaluator_behavior {behavior!r}")
    if not (str(waiver.get("review_trigger") or "").strip() or str(waiver.get("expires") or "").strip()):
        errors.append("missing review_trigger or expires")
    owner_decision = str(waiver.get("owner_decision") or "").strip()
    if owner_decision and not owner_decision.startswith(
        ("DELIB-", "bridge/", ".groundtruth/formal-artifact-approvals/")
    ):
        errors.append("owner_decision must cite a governed decision, bridge artifact, or approval packet")
    if str(waiver.get("status") or "").strip() not in WAIVER_STATUSES:
        errors.append("status must be active or retired")
    return errors


def _find_waiver(waivers: list[dict[str, Any]], harness: str, dimension: str) -> dict[str, Any] | None:
    for waiver in waivers:
        if validate_waiver(waiver):
            continue
        if str(waiver.get("status") or "").strip() != "active":
            continue
        waiver_harness = str(waiver.get("harness") or "").strip()
        waiver_dimension = str(waiver.get("dimension") or "").strip()
        if waiver_harness in {harness, "*"} and waiver_dimension in {dimension, "*"}:
            return waiver
    return None


def _with_waiver(cell: Cell, waivers: list[dict[str, Any]]) -> Cell:
    if cell.status not in GAP_STATES:
        return cell
    waiver = _find_waiver(waivers, cell.harness, cell.dimension)
    if not waiver:
        return cell
    return Cell(
        harness=cell.harness,
        harness_id=cell.harness_id,
        dimension=cell.dimension,
        title=cell.title,
        status="waived",
        release_blocking=cell.release_blocking,
        evidence=[*cell.evidence, str(waiver.get("evidence") or "")],
        details=f"{cell.details} Waived: {waiver.get('rationale')}",
        waiver_id=str(waiver.get("id") or ""),
    )


def _dimension(dim_id: str) -> Dimension:
    for dimension in DIMENSIONS:
        if dimension.id == dim_id:
            return dimension
    raise KeyError(dim_id)


def _cell(
    harness: dict[str, Any],
    dim_id: str,
    status: str,
    evidence: list[str],
    details: str,
) -> Cell:
    dimension = _dimension(dim_id)
    return Cell(
        harness=str(harness.get("harness_name") or ""),
        harness_id=str(harness.get("id") or ""),
        dimension=dimension.id,
        title=dimension.title,
        status=status,
        release_blocking=dimension.release_blocking,
        evidence=evidence,
        details=details,
    )


def _role_tags(dispatcher_rules: dict[str, Any]) -> set[str]:
    tags: set[str] = set()
    for rule in dispatcher_rules.get("rules", []) if isinstance(dispatcher_rules, dict) else []:
        if not isinstance(rule, dict):
            continue
        for role in rule.get("required_roles", []) or []:
            tags.add(str(role))
    return tags


def _skill_projection_status(
    root: Path, harness: dict[str, Any], cap_registry: dict[str, Any]
) -> tuple[str, list[str], str]:
    name = str(harness.get("harness_name") or "")
    harness_floor = _harness_config(cap_registry, name)
    manifest = harness_floor.get("skill_adapter_manifest")
    if manifest and _exists(root, str(manifest)):
        return "supported", [str(manifest)], "Harness declares an adapter manifest and the file exists."

    native_paths = {
        "claude": ".claude/skills",
        "codex": ".codex/skills/MANIFEST.json",
        "cursor": ".cursor/skills/MANIFEST.json",
        "antigravity": ".agent/skills",
        "ollama": ".api-harness/skills/MANIFEST.json",
        "openrouter": ".api-harness/skills/MANIFEST.json",
    }
    path = native_paths.get(name)
    if path and _exists(root, path):
        return "supported", [path], "Known skill projection surface exists."
    return "needs_adapter", [path or "<none>"], "No skill projection surface was found for this harness."


def _hook_projection_status(root: Path, harness: dict[str, Any]) -> tuple[str, list[str], str]:
    name = str(harness.get("harness_name") or "")
    surfaces = {
        "claude": [".claude/settings.json", ".claude/hooks"],
        "codex": [".codex/hooks.json", ".codex/gtkb-hooks"],
        "cursor": [".cursor/rules", ".cursor/gtkb-hooks"],
        "antigravity": [".agent"],
        "ollama": ["scripts/ollama_harness.py"],
        "openrouter": ["scripts/openrouter_harness.py"],
        "alibaba-cloud-studio": ["scripts/alibaba_cloud_studio_harness.py"],
    }.get(name, [])
    existing = [path for path in surfaces if _exists(root, path)]
    if existing:
        return "supported", existing, "Harness has a hook or governed-helper surface."
    return "needs_adapter", surfaces or ["<none>"], "No hook/governed-helper surface was found."


def _bridge_write_path_status(root: Path, harness: dict[str, Any]) -> tuple[str, list[str], str]:
    name = str(harness.get("harness_name") or "")
    surfaces = {
        "claude": [".claude/skills/bridge/helpers", ".claude/skills/verify/helpers"],
        "codex": [".codex/skills/bridge/helpers", ".codex/skills/verify/helpers"],
        "cursor": [".cursor/skills/bridge/helpers"],
        "antigravity": [".agent/skills/bridge"],
        "ollama": ["scripts/ollama_harness.py", ".api-harness/skills/bridge"],
        "openrouter": ["scripts/openrouter_harness.py", ".api-harness/skills/bridge"],
        "alibaba-cloud-studio": ["scripts/alibaba_cloud_studio_harness.py", ".api-harness/skills/bridge"],
    }.get(name, [])
    existing = [path for path in surfaces if _exists(root, path)]
    if existing:
        return "supported", existing, "Bridge helper or harness bridge route exists."
    return "needs_adapter", surfaces or ["<none>"], "No bridge write/verdict helper route was found."


def _readiness_probe_status(root: Path, harness: dict[str, Any]) -> tuple[str, list[str], str]:
    name = str(harness.get("harness_name") or "")
    script_name = name.replace("-", "_")
    candidates = [
        f"scripts/verify_{name}_dispatch.py",
        f"scripts/{script_name}_harness.py",
        f"scripts/check_{name}_harness.py",
    ]
    existing = [path for path in candidates if _exists(root, path)]
    if existing:
        return "supported", existing, "Readiness or harness wrapper script exists."
    return "needs_adapter", candidates, "No deterministic readiness probe was found."


def _provider_settings_status(harness: dict[str, Any], cap_registry: dict[str, Any]) -> tuple[str, list[str], str]:
    name = str(harness.get("harness_name") or "")
    floor = _harness_config(cap_registry, name)
    provider_backed = name in {"ollama", "openrouter", "alibaba-cloud-studio", "cursor"}
    if not provider_backed:
        return "supported", ["harness-state/harness-registry.json"], "Harness is not provider-shim scoped."
    fields = ("routing_schema_version", "skill_adapter_manifest", "skill_adapter_generation_supported")
    missing = [field for field in fields if field not in floor]
    if missing:
        return (
            "needs_adapter",
            [f"config/agent-control/harness-capability-registry.toml::[harnesses.{name}]"],
            f"Provider-shim floor is missing: {', '.join(missing)}.",
        )
    return (
        "supported",
        [f"config/agent-control/harness-capability-registry.toml::[harnesses.{name}]"],
        "Provider-shim capability floor is declared.",
    )


def _has_no_window_evidence(root: Path, rel_path: str) -> bool:
    path = root / rel_path
    if not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return False
    return any(token in text for token in NO_WINDOW_EVIDENCE_TOKENS)


def _no_window_status(root: Path, harness: dict[str, Any]) -> tuple[str, list[str], str]:
    name = str(harness.get("harness_name") or "")
    invocation = harness.get("invocation_surfaces", {})
    headless = invocation.get("headless", {}) if isinstance(invocation, dict) else {}
    argv = headless.get("argv", []) if isinstance(headless, dict) else []
    evidence = ["harness-state/harness-registry.json::invocation_surfaces.headless.argv"]
    if not argv:
        return "blocked", evidence, "No headless argv exists to audit for no-window launch behavior."
    joined = " ".join(str(part).lower() for part in argv)
    if any(token in joined for token in ("hidden", "nowindow", "no-window", "windowstyle")):
        return "supported", evidence, "Invocation explicitly carries no-window evidence."
    wrapper_evidence = [
        rel_path
        for rel_path in NO_WINDOW_EVIDENCE_PATHS_BY_HARNESS.get(name, ())
        if _has_no_window_evidence(root, rel_path)
    ]
    if wrapper_evidence:
        return (
            "supported",
            [*evidence, *wrapper_evidence],
            "Harness dispatch wrapper carries explicit Windows no-window evidence.",
        )
    if str(harness.get("harness_type") or "") in {"codex", "claude"}:
        return "needs_adapter", evidence, "Native CLI invocation lacks explicit no-window evidence."
    return "needs_adapter", evidence, "Provider/adapter invocation lacks explicit no-window evidence."


def evaluate(project_root: Path, *, waiver_path: Path = DEFAULT_WAIVER_PATH) -> dict[str, Any]:
    root = project_root.resolve()
    harness_doc = _load_json(root / HARNESS_REGISTRY_PATH)
    dispatcher_rules = _load_toml(root / DISPATCHER_RULES_PATH)
    capability_registry = _load_toml(root / CAPABILITY_REGISTRY_PATH)
    waivers, waiver_validation = _load_waivers(root, waiver_path)
    required_roles = _role_tags(dispatcher_rules)

    cells: list[Cell] = [*waiver_validation]
    harnesses = [h for h in harness_doc.get("harnesses", []) if isinstance(h, dict)]
    for harness in harnesses:
        name = str(harness.get("harness_name") or "")
        status = str(harness.get("status") or "")
        roles = [str(role) for role in harness.get("role", []) or []]
        headless = (harness.get("invocation_surfaces", {}) or {}).get("headless", {})
        headless_argv = headless.get("argv", []) if isinstance(headless, dict) else []

        cells.append(
            _cell(
                harness,
                "registry_projection",
                "supported" if name and harness.get("id") and status else "blocked",
                [_rel(root, root / HARNESS_REGISTRY_PATH)],
                f"status={status or '<missing>'}; roles={roles or []}",
            )
        )
        cells.append(
            _cell(
                harness,
                "headless_invocation",
                "supported" if headless_argv else "blocked",
                [_rel(root, root / HARNESS_REGISTRY_PATH)],
                "Headless argv is declared." if headless_argv else "No headless argv is declared.",
            )
        )
        currently_eligible = bool(harness.get("can_receive_dispatch"))
        receive_capable = bool(headless_argv and set(roles).intersection(required_roles))
        receive_status = "supported" if receive_capable else ("needs_adapter" if status == "active" else "blocked")
        cells.append(
            _cell(
                harness,
                "dispatcher_receive",
                receive_status,
                [_rel(root, root / DISPATCHER_RULES_PATH), _rel(root, root / HARNESS_REGISTRY_PATH)],
                (
                    f"receive_capable={receive_capable}; current_eligibility={currently_eligible}; "
                    f"dispatcher required roles={sorted(required_roles)}"
                ),
            )
        )
        can_fire = bool(harness.get("can_fire_events"))
        cells.append(
            _cell(
                harness,
                "event_source",
                "supported" if can_fire else ("needs_adapter" if status == "active" else "blocked"),
                [_rel(root, root / HARNESS_REGISTRY_PATH)],
                f"can_fire_events={can_fire}",
            )
        )

        for dim_id, status_value, evidence, details in (
            ("skill_projection", *_skill_projection_status(root, harness, capability_registry)),
            ("hook_projection", *_hook_projection_status(root, harness)),
            ("bridge_write_path", *_bridge_write_path_status(root, harness)),
            ("readiness_probe", *_readiness_probe_status(root, harness)),
            ("provider_settings", *_provider_settings_status(harness, capability_registry)),
            ("no_window_launch", *_no_window_status(root, harness)),
        ):
            cells.append(_cell(harness, dim_id, status_value, evidence, details))

    cells = [_with_waiver(cell, waivers) for cell in cells]
    counts = Counter(cell.status for cell in cells)
    unwaived_release_gaps = [
        cell for cell in cells if cell.status in FAILURE_STATES and cell.release_blocking and not cell.waiver_id
    ]
    unwaived_gaps = [cell for cell in cells if cell.status in FAILURE_STATES and not cell.waiver_id]

    report = {
        "metadata": {
            "project_id": PROJECT_ID,
            "work_item_id": WORK_ITEM_ID,
            "evaluator_work_item_id": EVALUATOR_WORK_ITEM_ID,
            "waiver_registry_work_item_id": WAIVER_REGISTRY_WORK_ITEM_ID,
            "project_authorization": PROJECT_AUTHORIZATION,
            "bridge_id": BRIDGE_ID,
            "waiver_registry_bridge_id": WAIVER_REGISTRY_BRIDGE_ID,
            "project_root": str(root),
            "waiver_path": _rel(root, waiver_path if waiver_path.is_absolute() else root / waiver_path),
            "read_only": True,
        },
        "overall_status": "FAIL" if unwaived_release_gaps else ("WARN" if unwaived_gaps else "PASS"),
        "counts": dict(sorted(counts.items())),
        "summary": {
            "harness_count": len(harnesses),
            "cell_count": len(cells),
            "unwaived_gap_count": len(unwaived_gaps),
            "unwaived_release_blocking_gap_count": len(unwaived_release_gaps),
            "waiver_count": len(waivers),
            "active_waiver_count": sum(
                1
                for waiver in waivers
                if not validate_waiver(waiver) and str(waiver.get("status") or "").strip() == "active"
            ),
            "retired_waiver_count": sum(
                1
                for waiver in waivers
                if not validate_waiver(waiver) and str(waiver.get("status") or "").strip() == "retired"
            ),
            "invalid_waiver_count": len(waiver_validation),
        },
        "harnesses": [
            {
                "id": harness.get("id"),
                "name": harness.get("harness_name"),
                "type": harness.get("harness_type"),
                "status": harness.get("status"),
                "role": harness.get("role") or [],
            }
            for harness in harnesses
        ],
        "cells": [asdict(cell) for cell in sorted(cells, key=lambda c: (c.harness, c.dimension))],
        "candidate_work_items": [asdict(candidate) for candidate in build_candidate_work_items(cells)],
    }
    return report


def build_candidate_work_items(cells: list[Cell]) -> list[CandidateWorkItem]:
    candidates: list[CandidateWorkItem] = []
    seen: set[tuple[str, str]] = set()
    for cell in cells:
        if cell.status not in FAILURE_STATES or cell.waiver_id:
            continue
        key = (cell.harness, cell.dimension)
        if key in seen or cell.harness == "*":
            continue
        seen.add(key)
        dimension = _dimension(cell.dimension)
        title = f"Close {cell.harness} {dimension.title.lower()} gap"
        description = (
            f"{dimension.work_item_template.format(harness=cell.harness)} Evidence: {'; '.join(cell.evidence)}."
        )
        command_title = title.replace('"', "'")
        command_desc = description.replace('"', "'")
        candidates.append(
            CandidateWorkItem(
                harness=cell.harness,
                dimension=cell.dimension,
                title=title,
                description=description,
                suggested_command=(
                    f'gt backlog add "{command_title}" --description "{command_desc}" '
                    f'--project "{PROJECT_ID}" --origin defect --component harness-parity'
                ),
            )
        )
    return candidates


def format_markdown(report: dict[str, Any], *, include_supported: bool = False) -> str:
    metadata = report["metadata"]
    candidate_by_cell = {
        (candidate["harness"], candidate["dimension"]): candidate
        for candidate in report.get("candidate_work_items", [])
    }
    lines = [
        "# Harness Parity Phase 2 Codex Baseline Matrix",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Project: {metadata['project_id']}",
        f"- Work item: {metadata['work_item_id']}",
        f"- Evaluator source work item: {metadata['evaluator_work_item_id']}",
        f"- Waiver registry work item: {metadata['waiver_registry_work_item_id']}",
        f"- Project authorization: {metadata['project_authorization']}",
        f"- Bridge: {metadata['bridge_id']}",
        f"- Waiver registry bridge: {metadata['waiver_registry_bridge_id']}",
        f"- Counts: {', '.join(f'{key}: {value}' for key, value in report['counts'].items()) or 'none'}",
        (
            "- Waivers: "
            f"active={report['summary']['active_waiver_count']}, "
            f"retired={report['summary']['retired_waiver_count']}, "
            f"invalid={report['summary']['invalid_waiver_count']}"
        ),
        "",
        "## Findings",
        "",
        "| Harness | Dimension | State | Release Blocking | Evidence | Disposition | Details |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    rows = report["cells"] if include_supported else [cell for cell in report["cells"] if cell["status"] != "supported"]
    if rows:
        for cell in rows:
            evidence = "<br>".join(cell["evidence"])
            details = str(cell["details"]).replace("|", "\\|")
            if cell.get("waiver_id"):
                disposition = f"Waiver: {cell['waiver_id']}"
            elif cell["status"] in FAILURE_STATES:
                candidate = candidate_by_cell.get((cell["harness"], cell["dimension"]))
                disposition = f"Candidate: {candidate['title']}" if candidate else "Registry correction required"
            else:
                disposition = "Supported"
            lines.append(
                f"| {cell['harness']} | {cell['title']} | {cell['status']} | "
                f"{cell['release_blocking']} | {evidence} | {disposition} | {details} |"
            )
    else:
        lines.append("| all | all | supported | False | n/a | Supported | No unwaived gaps found. |")

    candidates = report.get("candidate_work_items", [])
    if candidates:
        lines.extend(["", "## Candidate Work Items", ""])
        for candidate in candidates:
            lines.append(f"- {candidate['title']}: {candidate['description']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--waivers", type=Path, default=DEFAULT_WAIVER_PATH)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--include-supported", action="store_true")
    args = parser.parse_args(argv)

    report = evaluate(args.project_root, waiver_path=args.waivers)
    if args.format == "json":
        payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    else:
        payload = format_markdown(report, include_supported=args.include_supported)

    if args.output:
        output_path = args.output if args.output.is_absolute() else args.project_root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")

    return 1 if args.strict and report["overall_status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
