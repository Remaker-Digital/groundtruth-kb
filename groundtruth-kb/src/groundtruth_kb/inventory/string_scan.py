"""Deterministic string scanning over the SoT artifact inventory."""

from __future__ import annotations

import fnmatch
import json
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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

    @property
    def classes(self) -> set[str]:
        return {self.id, self.domain, self.lifecycle}


def _rel(path: Path, project_root: Path) -> str:
    return path.relative_to(project_root).as_posix()


def _load_registry(project_root: Path, registry_path: Path | None = None) -> list[ArtifactRecord]:
    path = registry_path or project_root / REGISTRY_RELATIVE_PATH
    if not path.is_file():
        raise InventoryScanError(f"SoT artifact registry not found: {path}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise InventoryScanError(f"Malformed SoT artifact registry {path}: {exc}") from exc
    rows = data.get("artifacts")
    if not isinstance(rows, list):
        raise InventoryScanError(f"{path} must contain [[artifacts]] rows")
    artifacts: list[ArtifactRecord] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise InventoryScanError(f"artifact row {index} must be a table")
        try:
            artifact_id = str(row["id"])
            domain = str(row["domain"])
            lifecycle = str(row["lifecycle"])
            storage_path = str(row["storage_path"])
        except KeyError as exc:
            raise InventoryScanError(f"artifact row {index} missing required field {exc.args[0]!r}") from exc
        artifacts.append(ArtifactRecord(artifact_id, domain, lifecycle, storage_path))
    return artifacts


def _git_tracked_paths(project_root: Path) -> set[str] | None:
    proc = subprocess.run(
        ["git", "-C", str(project_root), "ls-files"],
        capture_output=True,
        check=False,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return {line.strip().replace("\\", "/") for line in proc.stdout.splitlines() if line.strip()}


def _is_tracked(path: Path, project_root: Path, tracked: set[str] | None) -> bool:
    if tracked is None:
        return True
    return _rel(path, project_root) in tracked


def _glob_has_magic(pattern: str) -> bool:
    return any(ch in pattern for ch in "*?[")


def _expand_artifact_files(
    artifact: ArtifactRecord,
    project_root: Path,
    tracked: set[str] | None,
) -> tuple[list[Path], bool]:
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
    files = [path for path in matches if path.is_file() and _is_tracked(path, project_root, tracked)]
    return files, bool(matches) or storage.startswith(".gtkb-state/")


def _artifact_inventory(
    project_root: Path, registry_path: Path | None = None
) -> tuple[list[ArtifactRecord], dict[str, list[ArtifactRecord]], list[dict[str, str]]]:
    artifacts = _load_registry(project_root, registry_path)
    tracked = _git_tracked_paths(project_root)
    by_path: dict[str, list[ArtifactRecord]] = {}
    missing: list[dict[str, str]] = []
    for artifact in artifacts:
        files, resolved = _expand_artifact_files(artifact, project_root, tracked)
        if not resolved:
            missing.append(
                {
                    "artifact_id": artifact.id,
                    "storage_path": artifact.storage_path,
                    "domain": artifact.domain,
                    "lifecycle": artifact.lifecycle,
                }
            )
        for file_path in files:
            by_path.setdefault(_rel(file_path, project_root), []).append(artifact)
    return artifacts, by_path, missing


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
    artifacts, by_path, missing = _artifact_inventory(project_root, registry_path)
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
    artifacts, by_path, missing = _artifact_inventory(project_root, registry_path)
    return {
        "artifact_count": len(artifacts),
        "missing_artifacts": missing,
        "mutated": False,
        "scanned_file_count": len(by_path),
        "summary": {
            "artifact_count": len(artifacts),
            "missing_artifact_count": len(missing),
            "scanned_file_count": len(by_path),
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
