# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Duplicate Source-of-Truth audit helpers.

The audit starts from the typed platform SoT registry and then performs a
deterministic project-root closure scan. It is intentionally read-only with
respect to the artifacts it audits; callers may write the returned report as
evidence.
"""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from groundtruth_kb.project.artifact_membership_reconciliation import reconcile_artifact_membership
from groundtruth_kb.project.sot_registry import SoTArtifact, default_registry_path, load_toml

Classification = Literal[
    "registered_sot",
    "permitted_derived_cache",
    "non_sot_reference",
    "registry_gap",
    "duplicate_sot_violation",
]

_DISPATCH_DUPLICATE_FIELDS = (
    "can_fire_events",
    "can_receive_dispatch",
    "dispatch_availability",
    "dispatch_cost",
    "dispatch_quality",
)

_SKIP_DIRS = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "node_modules",
    }
)

_SKIP_RELATIVE_PREFIXES = ((".gtkb-state", "sot-singleton-audit"),)


@dataclass(frozen=True)
class AuditCandidate:
    """One classified SoT-bearing or SoT-like persistent artifact."""

    candidate_id: str
    classification: Classification
    paths: tuple[str, ...]
    reason: str
    registry_ids: tuple[str, ...] = ()
    remediation_work_item_id: str | None = None
    remediation_status: str | None = None
    duplicated_fields: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "classification": self.classification,
            "paths": list(self.paths),
            "reason": self.reason,
            "registry_ids": list(self.registry_ids),
            "remediation_work_item_id": self.remediation_work_item_id,
            "remediation_status": self.remediation_status,
            "duplicated_fields": list(self.duplicated_fields),
        }


@dataclass(frozen=True)
class DuplicateSoTAuditReport:
    """Machine-readable duplicate-SoT audit result."""

    generated_at: str
    project_root: str
    registry_path: str
    registry_count: int
    persistent_file_count: int
    registered_file_count: int
    missing_registry_artifacts: tuple[dict[str, str], ...]
    candidates: tuple[AuditCandidate, ...]
    registry_membership_complete: bool
    membership_counts: dict[str, int]
    coverage_phases: tuple[str, ...] = field(
        default=(
            "typed_registry_inventory",
            "registry_path_resolution",
            "whole_project_persistent_file_closure",
            "machine_checkable_derived_cache_probe",
            "known_duplicate_fieldset_probe",
            "remediation_disposition_check",
        )
    )

    @property
    def violation_count(self) -> int:
        return sum(1 for candidate in self.candidates if candidate.classification == "duplicate_sot_violation")

    @property
    def uncovered_violation_count(self) -> int:
        return sum(
            1
            for candidate in self.candidates
            if candidate.classification == "duplicate_sot_violation" and not candidate.remediation_work_item_id
        )

    @property
    def coverage_complete(self) -> bool:
        return self.registry_membership_complete

    def as_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "project_root": self.project_root,
            "registry_path": self.registry_path,
            "registry_count": self.registry_count,
            "persistent_file_count": self.persistent_file_count,
            "registered_file_count": self.registered_file_count,
            "missing_registry_artifacts": list(self.missing_registry_artifacts),
            "membership_counts": dict(self.membership_counts),
            "coverage_phases": list(self.coverage_phases),
            "coverage_complete": self.coverage_complete,
            "violation_count": self.violation_count,
            "uncovered_violation_count": self.uncovered_violation_count,
            "candidates": [candidate.as_dict() for candidate in self.candidates],
            "mutated_audited_artifacts": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2, sort_keys=True) + "\n"


def _rel(path: Path, project_root: Path) -> str:
    return path.relative_to(project_root).as_posix()


def _glob_has_magic(pattern: str) -> bool:
    return any(ch in pattern for ch in "*?[")


def _resolve_artifact_files(artifact: SoTArtifact, project_root: Path) -> tuple[list[Path], bool]:
    storage = artifact.storage_path.strip()
    if not storage or storage.startswith("membase:"):
        return [], True
    if Path(storage).is_absolute():
        return [], False
    if _glob_has_magic(storage):
        matches = sorted(project_root.glob(storage))
    else:
        candidate = project_root / storage
        if candidate.is_dir():
            matches = sorted(path for path in candidate.rglob("*") if path.is_file())
        elif candidate.is_file():
            matches = [candidate]
        else:
            matches = []
    return [path for path in matches if path.is_file()], bool(matches) or storage.startswith(".gtkb-state/")


def _registry_file_index(
    records: list[SoTArtifact], project_root: Path
) -> tuple[dict[str, list[str]], list[dict[str, str]]]:
    by_path: dict[str, list[str]] = {}
    missing: list[dict[str, str]] = []
    for record in records:
        files, resolved = _resolve_artifact_files(record, project_root)
        if not resolved:
            missing.append(
                {
                    "artifact_id": record.id,
                    "domain": record.domain,
                    "lifecycle": record.lifecycle,
                    "storage_path": record.storage_path,
                }
            )
        for file_path in files:
            by_path.setdefault(_rel(file_path, project_root), []).append(record.id)
    return by_path, missing


def _iter_persistent_files(project_root: Path) -> tuple[str, ...]:
    files: list[str] = []
    for path in project_root.rglob("*"):
        relative_parts = path.relative_to(project_root).parts
        if any(part in _SKIP_DIRS for part in relative_parts):
            continue
        if any(relative_parts[: len(prefix)] == prefix for prefix in _SKIP_RELATIVE_PREFIXES):
            continue
        if path.is_file():
            files.append(_rel(path, project_root))
    return tuple(sorted(files))


def _safe_read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _looks_like_derived_cache(payload: Any) -> bool:
    return isinstance(payload, dict) and payload.get("cache_kind") == "derived_sot_cache"


def _cache_contract_errors(payload: dict[str, Any], path: Path) -> tuple[str, ...]:
    errors: list[str] = []
    required_text_fields = ("derived_from", "generated_by", "generated_at", "usage_context")
    for field_name in required_text_fields:
        if not isinstance(payload.get(field_name), str) or not payload[field_name].strip():
            errors.append(field_name)
    if payload.get("read_only") is not True:
        errors.append("read_only")
    if payload.get("non_authoritative") is not True:
        errors.append("non_authoritative")
    ttl = payload.get("ttl_seconds")
    expires = payload.get("expires_at")
    source_hash = payload.get("source_hash")
    if ttl is None:
        if not isinstance(source_hash, str) or not source_hash:
            errors.append("source_hash")
    elif not isinstance(ttl, int) or ttl <= 0:
        errors.append("ttl_seconds")
    if ttl is not None and (not isinstance(expires, str) or not expires.strip()):
        errors.append("expires_at")
    cache_hash = payload.get("cache_hash")
    if not isinstance(cache_hash, str) or not cache_hash:
        errors.append("cache_hash")
    return tuple(errors)


def _derived_cache_candidates(project_root: Path, persistent_files: tuple[str, ...]) -> list[AuditCandidate]:
    candidates: list[AuditCandidate] = []
    for rel_path in persistent_files:
        if not rel_path.endswith(".json"):
            continue
        path = project_root / rel_path
        text = _safe_read_text(path)
        if text is None or "derived_sot_cache" not in text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        if not _looks_like_derived_cache(payload):
            continue
        errors = _cache_contract_errors(payload, path)
        if errors:
            candidates.append(
                AuditCandidate(
                    candidate_id=f"invalid-derived-cache:{rel_path}",
                    classification="duplicate_sot_violation",
                    paths=(rel_path,),
                    reason="derived_sot_cache metadata is present but does not satisfy GOV-SOT-SINGLETON-001",
                    duplicated_fields=errors,
                )
            )
        else:
            candidates.append(
                AuditCandidate(
                    candidate_id=f"permitted-derived-cache:{rel_path}",
                    classification="permitted_derived_cache",
                    paths=(rel_path,),
                    reason="cache metadata satisfies the GOV-SOT-SINGLETON-001 machine-checkable cache contract",
                    registry_ids=(str(payload["derived_from"]),),
                )
            )
    return candidates


def _load_toml_dict(path: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def _load_json_dict(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _json_contains_all_fields(value: Any, fields: tuple[str, ...]) -> bool:
    if isinstance(value, dict):
        if all(field in value for field in fields):
            return True
        return any(_json_contains_all_fields(child, fields) for child in value.values())
    if isinstance(value, list):
        return any(_json_contains_all_fields(child, fields) for child in value)
    return False


def _dispatch_duplicate_candidate(project_root: Path) -> AuditCandidate | None:
    rules_path = project_root / "config" / "dispatcher" / "rules.toml"
    harness_path = project_root / "harness-state" / "harness-registry.json"
    if not rules_path.is_file() or not harness_path.is_file():
        return None
    rules = _load_toml_dict(rules_path)
    harness = _load_json_dict(harness_path)
    harnesses = rules.get("harnesses")
    rule_harnesses = harnesses if isinstance(harnesses, dict) else {}
    rules_has_fields = any(
        isinstance(record, dict) and all(field in record for field in _DISPATCH_DUPLICATE_FIELDS)
        for record in rule_harnesses.values()
    )
    harness_has_fields = _json_contains_all_fields(harness, _DISPATCH_DUPLICATE_FIELDS)
    if not rules_has_fields or not harness_has_fields:
        return None
    return AuditCandidate(
        candidate_id="duplicate-dispatch-harness-fields",
        classification="duplicate_sot_violation",
        paths=("config/dispatcher/rules.toml", "harness-state/harness-registry.json"),
        reason=(
            "Both persistent artifacts carry the same dispatch capability/cost/quality fields; "
            "dispatch-specific remediation is already scoped to WI-5012."
        ),
        registry_ids=("harness-registry",),
        remediation_work_item_id="WI-5012",
        remediation_status="existing_covering_work_item",
        duplicated_fields=_DISPATCH_DUPLICATE_FIELDS,
    )


def run_duplicate_sot_audit(project_root: Path, *, registry_path: Path | None = None) -> DuplicateSoTAuditReport:
    """Run the registry-plus-closure duplicate-SoT audit."""
    root = project_root.resolve()
    registry = registry_path or default_registry_path(root)
    records = load_toml(registry)
    registered_files, missing = _registry_file_index(records, root)
    persistent_files = _iter_persistent_files(root)

    candidates: list[AuditCandidate] = []
    for record in records:
        candidates.append(
            AuditCandidate(
                candidate_id=f"registered:{record.id}",
                classification="registered_sot",
                paths=(record.storage_path,),
                reason="artifact class is covered by the platform SoT registry",
                registry_ids=(record.id,),
            )
        )
    candidates.extend(_derived_cache_candidates(root, persistent_files))
    dispatch_duplicate = _dispatch_duplicate_candidate(root)
    if dispatch_duplicate is not None:
        candidates.append(dispatch_duplicate)
    membership = reconcile_artifact_membership(root)

    return DuplicateSoTAuditReport(
        generated_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        project_root=str(root),
        registry_path=_rel(registry.resolve(), root),
        registry_count=len(records),
        persistent_file_count=len(persistent_files),
        registered_file_count=len(registered_files),
        missing_registry_artifacts=tuple(missing),
        candidates=tuple(candidates),
        registry_membership_complete=bool(membership["membership_complete"]),
        membership_counts=dict(membership["counts"]),
    )


def render_markdown(report: DuplicateSoTAuditReport) -> str:
    """Render a compact human-readable audit summary."""
    data = report.as_dict()
    lines = [
        "# SoT Singleton Duplicate Audit",
        "",
        f"- generated_at: `{data['generated_at']}`",
        f"- registry_count: `{data['registry_count']}`",
        f"- persistent_file_count: `{data['persistent_file_count']}`",
        f"- registered_file_count: `{data['registered_file_count']}`",
        f"- coverage_complete: `{str(data['coverage_complete']).lower()}`",
        f"- violation_count: `{data['violation_count']}`",
        f"- uncovered_violation_count: `{data['uncovered_violation_count']}`",
        "",
        "## Coverage Phases",
        "",
    ]
    lines.extend(f"- `{phase}`" for phase in report.coverage_phases)
    lines.extend(["", "## Duplicate-SoT Violations", ""])
    violations = [candidate for candidate in report.candidates if candidate.classification == "duplicate_sot_violation"]
    if not violations:
        lines.append("No duplicate-SoT violations detected.")
    for candidate in violations:
        remediation = candidate.remediation_work_item_id or "uncovered"
        lines.append(
            f"- `{candidate.candidate_id}`: {', '.join(candidate.paths)}; remediation: `{remediation}`; "
            f"fields: `{', '.join(candidate.duplicated_fields)}`"
        )
    return "\n".join(lines) + "\n"


def write_report_files(report: DuplicateSoTAuditReport, output_dir: Path) -> tuple[Path, Path]:
    """Write JSON and markdown evidence files for an audit report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "sot-singleton-duplicate-audit.json"
    markdown_path = output_dir / "sot-singleton-duplicate-audit.md"
    json_path.write_text(report.to_json(), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path
