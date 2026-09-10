"""Deterministic string scanning over the SoT artifact inventory."""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.project.registry_control_plane import (
    RegistryControlPlaneError,
    RegistryCoverageError,
    RegistrySnapshot,
    _path_object_kind,
    _record_objects,
    load_registry_snapshot,
)
from groundtruth_kb.project.sot_registry import InvalidSoTRecord, SoTArtifact, UnknownDomain

REGISTRY_RELATIVE_PATH = Path("config") / "registry" / "sot-artifacts.toml"
DEFAULT_CRITICAL_CLASSES = {
    "bridge_protocol",
    "control_surface",
    "harness_state",
    "narrative_authority",
    "scaffold_lifecycle",
    "specifications",
}
DEFAULT_WARN_CLASSES = {"runtime_state"}


class InventoryScanError(RuntimeError):
    """Raised when the scanner cannot load inventory or match input."""


@dataclass(frozen=True)
class ArtifactRecord:
    id: str
    domain: str
    lifecycle: str
    storage_path: str
    coverage_mode: str
    mutation_api: str
    health_check_function: str | None

    @property
    def classes(self) -> set[str]:
        return {self.id, self.domain, self.lifecycle}

    @classmethod
    def from_sot(cls, record: SoTArtifact) -> ArtifactRecord:
        return cls(
            id=record.id,
            domain=record.domain,
            lifecycle=record.lifecycle,
            storage_path=record.storage_path,
            coverage_mode=record.coverage_mode,
            mutation_api=record.mutation_api,
            health_check_function=record.health_check_function,
        )


@dataclass(frozen=True)
class ArtifactExpansion:
    artifact: ArtifactRecord
    path_class: str
    status: str
    files: tuple[Path, ...]
    resolved: bool
    blocking: bool
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact.id,
            "blocking": self.blocking,
            "domain": self.artifact.domain,
            "expanded_file_count": len(self.files),
            "lifecycle": self.artifact.lifecycle,
            "path_class": self.path_class,
            "resolved": self.resolved,
            "status": self.status,
            "storage_path": self.artifact.storage_path,
            **({"detail": self.detail} if self.detail is not None else {}),
        }


def _rel(path: Path, project_root: Path) -> str:
    return path.relative_to(project_root).as_posix()


def _load_registry(
    project_root: Path,
    registry_path: Path | None = None,
    *,
    snapshot: RegistrySnapshot | None = None,
) -> list[SoTArtifact]:
    path = registry_path or project_root / REGISTRY_RELATIVE_PATH
    try:
        coherent = snapshot or load_registry_snapshot(project_root=project_root, registry_path=path)
        return list(coherent.records)
    except (FileNotFoundError, InvalidSoTRecord, RegistryControlPlaneError, UnknownDomain, OSError) as exc:
        raise InventoryScanError(f"SoT artifact registry could not be loaded from {path}: {exc}") from exc


def _path_class(artifact: SoTArtifact, project_root: Path) -> str:
    if artifact.coverage_mode == "virtual":
        return "membase" if artifact.storage_path.startswith("membase:") else "external"
    if artifact.lifecycle in {"archive", "generated", "deprecated"}:
        return artifact.lifecycle
    if artifact.coverage_mode == "opaque_container":
        return "opaque_container"
    if artifact.coverage_mode == "glob":
        return "glob"
    if artifact.coverage_mode == "recursive" or (project_root / artifact.storage_path).is_dir():
        return "directory"
    return "file"


def _expand_artifact_files(record: SoTArtifact, project_root: Path) -> ArtifactExpansion:
    """Inspect the declared objects without widening coverage or following links."""
    artifact = ArtifactRecord.from_sot(record)
    path_class = _path_class(record, project_root)
    if record.coverage_mode == "virtual":
        return ArtifactExpansion(artifact, path_class, f"declared_{path_class}", (), True, False)

    def files_under(directory: Path):
        for path in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
            kind = _path_object_kind(path)
            if kind == "directory":
                yield from files_under(path)
            elif kind == "file":
                yield path

    try:
        objects = _record_objects(project_root, record)
        present = [path for path in objects if path.exists() or path.is_symlink()]
        if record.lifecycle == "archive":
            return ArtifactExpansion(
                artifact,
                path_class,
                "archived_surface_present" if present else "archived_absent",
                (),
                not present,
                bool(present),
            )
        if not present:
            kind = {"recursive": "directory", "glob": "glob", "opaque_container": "opaque_container"}.get(
                record.coverage_mode, "file"
            )
            return ArtifactExpansion(artifact, path_class, f"missing_{record.lifecycle}_{kind}", (), False, True)
        if record.coverage_mode == "opaque_container":
            if _path_object_kind(present[0]) not in {"file", "directory"}:
                raise RegistryCoverageError("An opaque container must be an ordinary file or directory")
            return ArtifactExpansion(artifact, path_class, "opaque_present", (), True, False)
        if record.coverage_mode == "recursive":
            if _path_object_kind(present[0]) != "directory":
                raise RegistryCoverageError("Recursive coverage requires an ordinary directory")
            files = tuple(files_under(present[0]))
        else:
            # Exact directory membership does not include descendants. A glob
            # includes its actual matched files, never a match's descendants.
            files = tuple(path for path in present if _path_object_kind(path) == "file")
        status = "expanded" if record.coverage_mode in {"recursive", "glob"} else "resolved"
        if record.lifecycle == "generated":
            status = "generated_present"
        return ArtifactExpansion(artifact, path_class, status, files, True, False)
    except (OSError, RegistryCoverageError) as exc:
        return ArtifactExpansion(artifact, path_class, "invalid_identity_or_unreadable", (), False, True, str(exc))


def registered_artifact_inventory(
    project_root: Path, registry_path: Path | None = None, *, snapshot: RegistrySnapshot | None = None
) -> tuple[
    list[ArtifactRecord],
    dict[str, list[ArtifactRecord]],
    list[dict[str, Any]],
    list[ArtifactExpansion],
]:
    project_root = project_root.resolve()
    records = _load_registry(project_root, registry_path, snapshot=snapshot)
    artifacts = [ArtifactRecord.from_sot(record) for record in records]
    by_path: dict[str, list[ArtifactRecord]] = {}
    missing: list[dict[str, Any]] = []
    expansions: list[ArtifactExpansion] = []
    for record, artifact in zip(records, artifacts, strict=True):
        expansion = _expand_artifact_files(record, project_root)
        expansions.append(expansion)
        if expansion.blocking:
            missing.append(expansion.to_dict())
        for file_path in expansion.files:
            by_path.setdefault(_rel(file_path, project_root), []).append(artifact)
    return artifacts, by_path, missing, expansions


# Compatibility only. New consumers must use the public API above.
_artifact_inventory = registered_artifact_inventory


def load_match_file(path: Path) -> list[str]:
    if not path.is_file():
        raise InventoryScanError(f"match file not found: {path}")
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return []
    if stripped[0] in "[{":
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise InventoryScanError(f"match file is not valid JSON: {path}: {exc}") from exc
        if isinstance(payload, list):
            values = payload
        elif isinstance(payload, dict):
            values = payload.get("matches") or payload.get("strings") or []
        else:
            raise InventoryScanError("JSON match file must be a list or object with matches/strings")
        if not all(isinstance(value, str) for value in values):
            raise InventoryScanError("match file values must all be strings")
        return [value for value in values if value]
    return [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def _severity_for(
    artifact: ArtifactRecord,
    rel_path: str,
    *,
    critical_classes: set[str],
    warn_classes: set[str],
    critical_paths: tuple[str, ...],
    warn_paths: tuple[str, ...],
) -> str:
    if any(fnmatch.fnmatch(rel_path, pattern) for pattern in critical_paths):
        return "critical"
    if any(fnmatch.fnmatch(rel_path, pattern) for pattern in warn_paths):
        return "warn"
    if artifact.classes & critical_classes:
        return "critical"
    if artifact.classes & warn_classes:
        return "warn"
    return "warn"


def _iter_line_hits(line: str, needle: str) -> list[int]:
    columns: list[int] = []
    start = 0
    while True:
        index = line.find(needle, start)
        if index == -1:
            return columns
        columns.append(index + 1)
        start = index + max(1, len(needle))


def scan_inventory_strings(
    project_root: Path,
    matches: list[str],
    *,
    registry_path: Path | None = None,
    critical_classes: set[str] | None = None,
    warn_classes: set[str] | None = None,
    critical_paths: tuple[str, ...] = (),
    warn_paths: tuple[str, ...] = (),
) -> dict[str, Any]:
    project_root = project_root.resolve()
    literal_matches = [match for match in matches if match]
    if not literal_matches:
        raise InventoryScanError("at least one --match or --match-file value is required")
    artifacts, by_path, missing, _ = registered_artifact_inventory(project_root, registry_path)
    critical = DEFAULT_CRITICAL_CLASSES | set(critical_classes or set())
    warn = DEFAULT_WARN_CLASSES | set(warn_classes or set())
    match_ids = {value: f"M{index:03d}" for index, value in enumerate(literal_matches, start=1)}
    hits: list[dict[str, Any]] = []
    for rel_path in sorted(by_path):
        path = project_root / rel_path
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, start=1):
            for match in literal_matches:
                for column in _iter_line_hits(line, match):
                    for artifact in by_path[rel_path]:
                        severity = _severity_for(
                            artifact,
                            rel_path,
                            critical_classes=critical,
                            warn_classes=warn,
                            critical_paths=critical_paths,
                            warn_paths=warn_paths,
                        )
                        hits.append(
                            {
                                "artifact_class": artifact.domain,
                                "artifact_id": artifact.id,
                                "column": column,
                                "lifecycle": artifact.lifecycle,
                                "line": line_number,
                                "matched_string": match,
                                "matched_string_id": match_ids[match],
                                "path": rel_path,
                                "remediation_status": "untriaged",
                                "severity": severity,
                            }
                        )
    counts = {"critical": 0, "warn": 0}
    for hit in hits:
        counts[hit["severity"]] = counts.get(hit["severity"], 0) + 1
    return {
        "artifact_count": len(artifacts),
        "hits": hits,
        "match_count": len(literal_matches),
        "matches": [{"id": match_ids[value], "literal": value} for value in literal_matches],
        "missing_artifacts": missing,
        "mutated": False,
        "scanned_file_count": len(by_path),
        "summary": {
            "critical": counts.get("critical", 0),
            "total_hits": len(hits),
            "warn": counts.get("warn", 0),
        },
    }


def build_refresh_report(project_root: Path, *, registry_path: Path | None = None) -> dict[str, Any]:
    project_root = project_root.resolve()
    artifacts, by_path, missing, expansions = registered_artifact_inventory(project_root, registry_path)
    path_class_counts: dict[str, int] = {}
    lifecycle_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for expansion in expansions:
        path_class_counts[expansion.path_class] = path_class_counts.get(expansion.path_class, 0) + 1
        lifecycle = expansion.artifact.lifecycle
        lifecycle_counts[lifecycle] = lifecycle_counts.get(lifecycle, 0) + 1
        status_counts[expansion.status] = status_counts.get(expansion.status, 0) + 1
    findings = [
        {
            "artifact_id": expansion.artifact.id,
            "code": expansion.status,
            "lifecycle": expansion.artifact.lifecycle,
            "path_class": expansion.path_class,
            "severity": "blocking" if expansion.blocking else "info",
            "storage_path": expansion.artifact.storage_path,
        }
        for expansion in expansions
        if expansion.blocking or not expansion.resolved
    ]
    return {
        "artifact_count": len(artifacts),
        "artifact_statuses": [expansion.to_dict() for expansion in expansions],
        "blocking": bool(missing),
        "missing_artifacts": missing,
        "mutated": False,
        "registry_findings": findings,
        "scanned_file_count": len(by_path),
        "summary": {
            "artifact_count": len(artifacts),
            "blocking_finding_count": len(missing),
            "lifecycle_counts": dict(sorted(lifecycle_counts.items())),
            "missing_artifact_count": len(missing),
            "path_class_counts": dict(sorted(path_class_counts.items())),
            "scanned_file_count": len(by_path),
            "status_counts": dict(sorted(status_counts.items())),
        },
    }


def emit_markdown_ledger(payload: dict[str, Any]) -> str:
    lines = [
        "# Inventory String Scan Ledger",
        "",
        f"- artifacts: {payload['artifact_count']}",
        f"- scanned files: {payload['scanned_file_count']}",
        f"- total hits: {payload['summary']['total_hits']}",
        f"- critical: {payload['summary']['critical']}",
        f"- warn: {payload['summary']['warn']}",
        "",
    ]
    hits = payload.get("hits", [])
    if not hits:
        lines.append("No matches found.")
        return "\n".join(lines) + "\n"
    for severity in ("critical", "warn"):
        severity_hits = [hit for hit in hits if hit["severity"] == severity]
        if not severity_hits:
            continue
        lines.extend([f"## {severity.title()} Hits", ""])
        for hit in severity_hits:
            lines.append(
                "- "
                f"{hit['path']}:{hit['line']}:{hit['column']} "
                f"[{hit['matched_string_id']}] "
                f"{hit['artifact_id']} ({hit['artifact_class']}) "
                f"status={hit['remediation_status']}"
            )
        lines.append("")
    return "\n".join(lines)
