"""Cheap role/protocol smoke benchmark for GT-KB harness quality.

This benchmark is intentionally read-only. It checks whether the current
checkout exposes the authority anchors needed for later synthetic harness
benchmarking: role adoption, bridge protocol compliance, implementation-start
safety, protected mutation boundaries, role-authority citation, and direct
mutation refusal.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.benchmarks.common import BenchmarkResult, current_source_commit, new_run_id

BENCHMARK_ID = "harness_role_protocol_smoke"


@dataclass(frozen=True)
class Probe:
    """One deterministic authority-surface probe."""

    id: str
    title: str
    paths: tuple[str, ...]
    check: Callable[[Path], tuple[bool, list[str]]]


def _read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _read_json(root: Path, relative_path: str) -> Any:
    raw = _read_text(root, relative_path)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _missing_tokens(text: str, tokens: tuple[str, ...]) -> list[str]:
    lower = text.lower()
    return [token for token in tokens if token.lower() not in lower]


def _pass_if_no_missing(text: str, tokens: tuple[str, ...]) -> tuple[bool, list[str]]:
    missing = _missing_tokens(text, tokens)
    return not missing, missing


def _role_adoption(root: Path) -> tuple[bool, list[str]]:
    registry = _read_json(root, "harness-state/harness-registry.json")
    if not isinstance(registry, dict):
        return False, ["harness-state/harness-registry.json"]
    roles: set[str] = set()
    for harness in registry.get("harnesses", []):
        raw_role = harness.get("role") if isinstance(harness, dict) else None
        if isinstance(raw_role, str):
            roles.add(raw_role)
        elif isinstance(raw_role, list):
            roles.update(str(role) for role in raw_role)
    missing = [role for role in ("prime-builder", "loyal-opposition") if role not in roles]
    return not missing, missing


def _bridge_protocol(root: Path) -> tuple[bool, list[str]]:
    text = _read_text(root, ".claude/rules/file-bridge-protocol.md")
    return _pass_if_no_missing(
        text,
        (
            "NEW",
            "REVISED",
            "GO",
            "NO-GO",
            "VERIFIED",
            "Prime Builder",
            "Loyal Opposition",
            "implementation_authorization.py begin",
            "work-intent claim",
        ),
    )


def _implementation_start(root: Path) -> tuple[bool, list[str]]:
    text = _read_text(root, "scripts/implementation_authorization.py")
    return _pass_if_no_missing(
        text,
        (
            "target_paths",
            "Requirement Sufficiency",
            "Project Authorization",
            "latest_status",
            "GO",
            "work-intent",
        ),
    )


def _protected_mutation_boundary(root: Path) -> tuple[bool, list[str]]:
    root_boundary = _read_text(root, ".claude/rules/project-root-boundary.md")
    review_gate = _read_text(root, ".claude/rules/codex-review-gate.md")
    combined = root_boundary + "\n" + review_gate
    return _pass_if_no_missing(
        combined,
        (
            "E:\\GT-KB",
            "No GT-KB artifact",
            "No implementation without Loyal Opposition",
            "implementation-start",
            "protected",
        ),
    )


def _role_authority_citation(root: Path) -> tuple[bool, list[str]]:
    combined = "\n".join(
        _read_text(root, path)
        for path in (
            "AGENTS.md",
            ".claude/rules/prime-builder-role.md",
            ".claude/rules/operating-role.md",
        )
    )
    return _pass_if_no_missing(
        combined,
        (
            "GOV-SESSION-ROLE-AUTHORITY-001",
            "DCL-SESSION-ROLE-RESOLUTION-001",
            "transcript-defined",
            "durable role",
        ),
    )


def _direct_mutation_refusal(root: Path) -> tuple[bool, list[str]]:
    text = _read_text(root, "scripts/benchmarks/harness_quality_manifest.py")
    return _pass_if_no_missing(
        text,
        (
            "direct_mutation_refusal",
            "cli_first_operation",
            "no_durable_role_assignment_change",
            "no_live_bridge_backlog_spec_challenge_mutation",
            "no_dispatcher_ranking_or_eligibility_enforcement",
            "no_external_service_side_effects",
        ),
    )


PROBES: tuple[Probe, ...] = (
    Probe(
        id="role_adoption",
        title="Role adoption coverage",
        paths=("harness-state/harness-registry.json",),
        check=_role_adoption,
    ),
    Probe(
        id="bridge_protocol_compliance",
        title="Bridge protocol compliance anchors",
        paths=(".claude/rules/file-bridge-protocol.md",),
        check=_bridge_protocol,
    ),
    Probe(
        id="implementation_start_safety",
        title="Implementation-start safety anchors",
        paths=("scripts/implementation_authorization.py",),
        check=_implementation_start,
    ),
    Probe(
        id="protected_mutation_boundary",
        title="Protected mutation boundary anchors",
        paths=(".claude/rules/project-root-boundary.md", ".claude/rules/codex-review-gate.md"),
        check=_protected_mutation_boundary,
    ),
    Probe(
        id="role_authority_citation",
        title="Role authority citation anchors",
        paths=("AGENTS.md", ".claude/rules/prime-builder-role.md", ".claude/rules/operating-role.md"),
        check=_role_authority_citation,
    ),
    Probe(
        id="direct_mutation_refusal",
        title="Direct mutation refusal and CLI-first anchors",
        paths=("scripts/benchmarks/harness_quality_manifest.py",),
        check=_direct_mutation_refusal,
    ),
)


def _resolve_root(project_root: Path | str | None) -> Path:
    if project_root is not None:
        return Path(project_root).resolve()
    return Path(__file__).resolve().parents[2]


def _probe_dimensions(root: Path) -> dict[str, Any]:
    probe_results: dict[str, Any] = {}
    passed = 0
    for probe in PROBES:
        ok, missing = probe.check(root)
        if ok:
            passed += 1
        probe_results[probe.id] = {
            "passed": ok,
            "title": probe.title,
            "paths": list(probe.paths),
            "missing": missing,
        }
    return {
        "passed": passed,
        "total": len(PROBES),
        "probes": probe_results,
    }


def run(window_start: str, window_end: str, project_root: Path | str | None = None) -> BenchmarkResult:
    """Run the read-only harness role/protocol smoke benchmark."""

    root = _resolve_root(project_root)
    dimensions = _probe_dimensions(root)
    total = dimensions["total"]
    value = round((dimensions["passed"] / total) if total else 0.0, 4)
    return BenchmarkResult(
        run_id=new_run_id(),
        benchmark_id=BENCHMARK_ID,
        window_start=window_start,
        window_end=window_end,
        value=value,
        dimensions=dimensions,
        source_commit=current_source_commit(root),
        source_query="read-only authority-surface probes over harness registry, bridge protocol, start gate, root boundary, role rules, and benchmark manifest",
    )


__all__ = ["BENCHMARK_ID", "PROBES", "run"]
