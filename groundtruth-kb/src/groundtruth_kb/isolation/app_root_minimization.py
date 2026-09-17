"""Application artifact registry classification and boundary validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

ArtifactType = Literal["FILE", "DIR"]
FindingSeverity = Literal["error", "warning"]

REGISTRY_FILENAME = ".gtkb-app-isolation.json"
ALLOWED_TYPES = frozenset({"FILE", "DIR"})
REGISTRY_SCHEMA_VERSION = "2.0"
ALLOWED_CLASSIFICATIONS = frozenset(
    {"authoritative_input", "generated_output", "runtime_data", "bounded_temporary_output"}
)


@dataclass(frozen=True)
class TopLevelArtifact:
    """Normalized top-level app-root artifact."""

    name: str
    type: str
    source: str

    @property
    def key(self) -> tuple[str, str]:
        return self.name, self.type

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "type": self.type, "source": self.source}


@dataclass(frozen=True)
class AppRootFinding:
    """A structured app-root minimization finding."""

    code: str
    message: str
    path: str | None = None
    severity: FindingSeverity = "error"

    def to_dict(self) -> dict[str, str]:
        payload = {"code": self.code, "message": self.message, "severity": self.severity}
        if self.path:
            payload["path"] = self.path
        return payload


@dataclass(frozen=True)
class AppRootMinimizationResult:
    """Result payload for app-root minimization checks."""

    app_root: Path
    registry_path: Path
    actual_entries: tuple[TopLevelArtifact, ...]
    registry_entries: tuple[dict[str, Any], ...]
    findings: tuple[AppRootFinding, ...]

    @property
    def ok(self) -> bool:
        return not any(finding.severity == "error" for finding in self.findings)

    @property
    def status(self) -> Literal["pass", "fail"]:
        return "pass" if self.ok else "fail"

    def first_error_message(self, *, limit: int = 3) -> str:
        errors = [finding for finding in self.findings if finding.severity == "error"]
        if not errors:
            return "no errors"
        head = "; ".join(f"{finding.code}: {finding.message}" for finding in errors[:limit])
        remaining = len(errors) - limit
        if remaining > 0:
            return f"{head}; +{remaining} more"
        return head

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "app_root": str(self.app_root),
            "registry_path": str(self.registry_path),
            "actual_entries": [entry.to_dict() for entry in self.actual_entries],
            "registry_entries": list(self.registry_entries),
            "findings": [finding.to_dict() for finding in self.findings],
        }


def validate_app_root_minimization(
    app_root: str | Path,
    *,
    project_root: str | Path | None = None,
) -> AppRootMinimizationResult:
    """Check every actual top-level entry against the application's registry.

    Git tracking and ignore rules do not determine application classification.
    This is a read-only boundary check, not cleanup or lifecycle verification.
    Generated, runtime and bounded temporary outputs may be absent; declared
    authoritative inputs must exist. No entry is deleted or followed recursively.
    """
    resolved_app_root = Path(app_root).resolve()
    display_root = Path(project_root).resolve() if project_root is not None else resolved_app_root
    registry_path = resolved_app_root / REGISTRY_FILENAME
    findings: list[AppRootFinding] = []
    payload = _load_registry(registry_path, display_root, findings)
    registry_entries = _normalize_registry_entries(payload, display_root, registry_path, findings)
    actual_entries = _collect_actual_entries(resolved_app_root, display_root, findings=findings)
    _compare_actual_to_registry(actual_entries, registry_entries, resolved_app_root, display_root, findings)
    return AppRootMinimizationResult(
        app_root=resolved_app_root,
        registry_path=registry_path,
        actual_entries=tuple(sorted(actual_entries, key=lambda entry: (entry.name.lower(), entry.type))),
        registry_entries=tuple(registry_entries),
        findings=tuple(findings),
    )


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_registry(
    registry_path: Path,
    project_root: Path,
    findings: list[AppRootFinding],
) -> dict[str, Any] | None:
    try:
        if registry_path.resolve() != registry_path:
            raise ValueError("the application registry must be a direct file in its application root")
        if not registry_path.is_file():
            findings.append(
                AppRootFinding(
                    "registry_missing", f"{REGISTRY_FILENAME} is missing", _display_path(registry_path, project_root)
                )
            )
            return None
        payload = json.loads(registry_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        findings.append(
            AppRootFinding(
                "registry_unreadable",
                f"{REGISTRY_FILENAME} cannot be read: {exc}",
                _display_path(registry_path, project_root),
            )
        )
        return None
    if not isinstance(payload, dict):
        findings.append(
            AppRootFinding(
                "registry_root_not_object",
                "registry JSON root must be an object",
                _display_path(registry_path, project_root),
            )
        )
        return None
    return payload


def _normalize_registry_entries(
    payload: dict[str, Any] | None,
    project_root: Path,
    registry_path: Path,
    findings: list[AppRootFinding],
) -> list[dict[str, Any]]:
    if payload is None:
        return []
    location = _display_path(registry_path, project_root)
    if payload.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        findings.append(
            AppRootFinding(
                "registry_schema_unsupported", f"registry schema_version must be {REGISTRY_SCHEMA_VERSION}", location
            )
        )
    application = _non_empty_string(payload.get("application"))
    if not application:
        findings.append(
            AppRootFinding("application_missing", "registry application must be a non-empty string", location)
        )
    elif application != registry_path.parent.name:
        findings.append(
            AppRootFinding("application_mismatch", "registry application does not match its application slot", location)
        )
    entries = payload.get("top_level_artifacts")
    if not isinstance(entries, list) or not entries:
        findings.append(
            AppRootFinding("top_level_artifacts_invalid", "top_level_artifacts must be a non-empty list", location)
        )
        return []
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        entry_path = f"{location}#top_level_artifacts[{index}]"
        if not isinstance(entry, dict):
            findings.append(AppRootFinding("registry_entry_not_object", "registry entry must be an object", entry_path))
            continue
        name = _non_empty_string(entry.get("name"))
        artifact_type = _non_empty_string(entry.get("type"))
        classification = _non_empty_string(entry.get("classification"))
        valid_name = bool(
            name and name not in {".", ".."} and not any(c in name for c in "/\\:") and name == entry.get("name")
        )
        if not valid_name:
            findings.append(
                AppRootFinding("entry_invalid_name", "entry name must be one direct top-level name", entry_path)
            )
        elif name.casefold() in seen:
            findings.append(AppRootFinding("entry_duplicate", f"duplicate registry name: {name}", entry_path))
        seen.add(name.casefold())
        if artifact_type not in ALLOWED_TYPES or artifact_type != entry.get("type"):
            findings.append(
                AppRootFinding("entry_invalid_type", f"entry type must be one of {sorted(ALLOWED_TYPES)}", entry_path)
            )
        if classification not in ALLOWED_CLASSIFICATIONS or classification != entry.get("classification"):
            findings.append(
                AppRootFinding(
                    "entry_invalid_classification",
                    f"classification must be one of {sorted(ALLOWED_CLASSIFICATIONS)}",
                    entry_path,
                )
            )
        if "bucket" in entry:
            findings.append(
                AppRootFinding(
                    "entry_retired_bucket", "A/B/C/D buckets are retired; use the current classification", entry_path
                )
            )
        if not _non_empty_string(entry.get("purpose")):
            findings.append(
                AppRootFinding("entry_missing_purpose", "every classification requires a non-empty purpose", entry_path)
            )
        if valid_name and artifact_type in ALLOWED_TYPES:
            normalized.append(dict(entry))
    return normalized


def _collect_actual_entries(
    app_root: Path,
    project_root: Path,
    *,
    findings: list[AppRootFinding],
) -> list[TopLevelArtifact]:
    try:
        if not app_root.is_dir():
            findings.append(
                AppRootFinding("app_root_missing", "application root is missing", _display_path(app_root, project_root))
            )
            return []
        children = list(app_root.iterdir())
    except OSError as exc:
        findings.append(
            AppRootFinding(
                "app_root_unreadable",
                f"cannot enumerate application root: {exc}",
                _display_path(app_root, project_root),
            )
        )
        return []
    entries = []
    for child in children:
        try:
            if not child.resolve().is_relative_to(app_root):
                findings.append(
                    AppRootFinding(
                        "artifact_outside_application",
                        "top-level artifact resolves outside the application root",
                        _display_path(child, project_root),
                    )
                )
            if child.is_dir():
                artifact_type = "DIR"
            elif child.is_file():
                artifact_type = "FILE"
            else:
                findings.append(
                    AppRootFinding(
                        "artifact_unreadable",
                        "top-level artifact is not an accessible file or directory",
                        _display_path(child, project_root),
                    )
                )
                continue
            entries.append(TopLevelArtifact(child.name, artifact_type, "filesystem"))
        except (OSError, RuntimeError) as exc:
            findings.append(
                AppRootFinding(
                    "artifact_unreadable",
                    f"cannot inspect top-level artifact: {exc}",
                    _display_path(child, project_root),
                )
            )
    return entries


def _compare_actual_to_registry(
    actual_entries: list[TopLevelArtifact],
    registry_entries: list[dict[str, Any]],
    app_root: Path,
    project_root: Path,
    findings: list[AppRootFinding],
) -> None:
    actual_by_key = {entry.key: entry for entry in actual_entries}
    registry_by_key = {(entry["name"], entry["type"]): entry for entry in registry_entries}
    for key, entry in sorted(actual_by_key.items()):
        if key not in registry_by_key:
            findings.append(
                AppRootFinding(
                    "unregistered_top_level_artifact",
                    f"{entry.name} ({entry.type}) has no registry entry",
                    _display_path(app_root / entry.name, project_root),
                )
            )
    for registry_key, registry_entry in sorted(registry_by_key.items()):
        if registry_key not in actual_by_key and registry_entry.get("classification") == "authoritative_input":
            findings.append(
                AppRootFinding(
                    "registry_entry_without_artifact",
                    f"{registry_entry['name']} ({registry_entry['type']}) is a required input but is absent",
                    _display_path(app_root / registry_entry["name"], project_root),
                )
            )


def _non_empty_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _display_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()
