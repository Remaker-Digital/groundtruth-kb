"""Agent Red app-root minimization validator."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

ArtifactType = Literal["FILE", "DIR"]
FindingSeverity = Literal["error", "warning"]

REGISTRY_FILENAME = ".gtkb-app-isolation.json"
ALLOWED_TYPES = frozenset({"FILE", "DIR"})
ALLOWED_BUCKETS = frozenset({"A", "B"})
FORBIDDEN_BUCKETS = frozenset({"C", "D"})


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
    tracked_only: bool = True,
) -> AppRootMinimizationResult:
    """Validate an application root against its `.gtkb-app-isolation.json`.

    The release/doctor path uses tracked top-level artifacts plus explicitly
    registered local tool surfaces, so ignored runtime files do not create false
    release blockers. Tests can set ``tracked_only=False`` to exercise the raw
    filesystem contract and prove unmatched entries fail.
    """

    resolved_app_root = Path(app_root)
    resolved_project_root = (
        Path(project_root) if project_root is not None else _discover_project_root(resolved_app_root)
    )
    registry_path = resolved_app_root / REGISTRY_FILENAME
    findings: list[AppRootFinding] = []

    payload = _load_registry(registry_path, resolved_project_root, findings)
    registry_entries = _normalize_registry_entries(payload, resolved_project_root, registry_path, findings)

    actual_entries = _collect_actual_entries(
        resolved_app_root,
        resolved_project_root,
        tracked_only=tracked_only,
        findings=findings,
    )
    if tracked_only:
        actual_entries = _with_existing_registered_local_entries(actual_entries, registry_entries, resolved_app_root)

    _compare_actual_to_registry(actual_entries, registry_entries, resolved_app_root, resolved_project_root, findings)

    return AppRootMinimizationResult(
        app_root=resolved_app_root,
        registry_path=registry_path,
        actual_entries=tuple(sorted(actual_entries, key=lambda entry: (entry.name.lower(), entry.type))),
        registry_entries=tuple(registry_entries),
        findings=tuple(findings),
    )


def _discover_project_root(app_root: Path) -> Path:
    for candidate in (app_root, *app_root.parents):
        if (candidate / ".git").exists():
            return candidate
    return app_root.parent.parent


def _load_registry(
    registry_path: Path,
    project_root: Path,
    findings: list[AppRootFinding],
) -> dict[str, Any] | None:
    if not registry_path.is_file():
        findings.append(
            AppRootFinding(
                code="registry_missing",
                message=f"{REGISTRY_FILENAME} is missing",
                path=_display_path(registry_path, project_root),
            )
        )
        return None
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        findings.append(
            AppRootFinding(
                code="registry_malformed_json",
                message=f"{REGISTRY_FILENAME} is malformed JSON: {exc}",
                path=_display_path(registry_path, project_root),
            )
        )
        return None
    if not isinstance(payload, dict):
        findings.append(
            AppRootFinding(
                code="registry_root_not_object",
                message=f"{REGISTRY_FILENAME} JSON root must be an object",
                path=_display_path(registry_path, project_root),
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

    _validate_registry_shape(payload, project_root, registry_path, findings)
    entries = payload.get("top_level_artifacts")
    if not isinstance(entries, list) or not entries:
        findings.append(
            AppRootFinding(
                code="top_level_artifacts_invalid",
                message="top_level_artifacts must be a non-empty list",
                path=_display_path(registry_path, project_root),
            )
        )
        return []

    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for index, entry in enumerate(entries):
        entry_path = f"{_display_path(registry_path, project_root)}#top_level_artifacts[{index}]"
        if not isinstance(entry, dict):
            findings.append(
                AppRootFinding(
                    code="registry_entry_not_object",
                    message="top_level_artifacts entry must be an object",
                    path=entry_path,
                )
            )
            continue

        name = _non_empty_string(entry.get("name"))
        artifact_type = _non_empty_string(entry.get("type")).upper()
        bucket = _non_empty_string(entry.get("bucket")).upper()

        if not name:
            findings.append(
                AppRootFinding(code="entry_missing_name", message="entry name is required", path=entry_path)
            )
        if not artifact_type:
            findings.append(
                AppRootFinding(code="entry_missing_type", message="entry type is required", path=entry_path)
            )
        elif artifact_type not in ALLOWED_TYPES:
            findings.append(
                AppRootFinding(
                    code="entry_invalid_type",
                    message=f"entry type must be one of {sorted(ALLOWED_TYPES)}",
                    path=entry_path,
                )
            )
        if not bucket:
            findings.append(
                AppRootFinding(code="entry_missing_bucket", message="entry bucket is required", path=entry_path)
            )
        elif bucket in FORBIDDEN_BUCKETS:
            findings.append(
                AppRootFinding(
                    code="entry_forbidden_bucket",
                    message=f"bucket {bucket} is not allowed at the Agent Red app root",
                    path=entry_path,
                )
            )
        elif bucket not in ALLOWED_BUCKETS:
            findings.append(
                AppRootFinding(
                    code="entry_invalid_bucket",
                    message=f"bucket must be one of {sorted(ALLOWED_BUCKETS)}",
                    path=entry_path,
                )
            )

        if bucket == "A" and not _non_empty_string(entry.get("purpose")):
            findings.append(
                AppRootFinding(
                    code="entry_missing_purpose",
                    message="bucket A entries require non-empty purpose",
                    path=entry_path,
                )
            )
        if bucket == "B":
            if not _non_empty_string(entry.get("tool")):
                findings.append(
                    AppRootFinding(
                        code="entry_missing_tool",
                        message="bucket B entries require non-empty tool",
                        path=entry_path,
                    )
                )
            if not _non_empty_string(entry.get("justification")):
                findings.append(
                    AppRootFinding(
                        code="entry_missing_justification",
                        message="bucket B entries require non-empty justification",
                        path=entry_path,
                    )
                )

        if name and artifact_type in ALLOWED_TYPES:
            key = (name, artifact_type)
            if key in seen:
                findings.append(
                    AppRootFinding(
                        code="entry_duplicate",
                        message=f"duplicate registry entry for {name} ({artifact_type})",
                        path=entry_path,
                    )
                )
            seen.add(key)
            normalized.append({**entry, "name": name, "type": artifact_type, "bucket": bucket})

    return normalized


def _validate_registry_shape(
    payload: dict[str, Any],
    project_root: Path,
    registry_path: Path,
    findings: list[AppRootFinding],
) -> None:
    if not _non_empty_string(payload.get("application")):
        findings.append(
            AppRootFinding(
                code="application_missing",
                message="registry application must be a non-empty string",
                path=_display_path(registry_path, project_root),
            )
        )
    validator_contract = payload.get("validator_contract")
    if not isinstance(validator_contract, dict):
        findings.append(
            AppRootFinding(
                code="validator_contract_invalid",
                message="validator_contract must be an object",
                path=_display_path(registry_path, project_root),
            )
        )
        return
    if not _non_empty_string(validator_contract.get("scan_path")):
        findings.append(
            AppRootFinding(
                code="validator_contract_missing_scan_path",
                message="validator_contract.scan_path must be a non-empty string",
                path=_display_path(registry_path, project_root),
            )
        )
    rules = validator_contract.get("rules")
    if not isinstance(rules, list) or not rules or not all(_non_empty_string(rule) for rule in rules):
        findings.append(
            AppRootFinding(
                code="validator_contract_invalid_rules",
                message="validator_contract.rules must be a non-empty string list",
                path=_display_path(registry_path, project_root),
            )
        )


def _collect_actual_entries(
    app_root: Path,
    project_root: Path,
    *,
    tracked_only: bool,
    findings: list[AppRootFinding],
) -> list[TopLevelArtifact]:
    if not app_root.is_dir():
        findings.append(
            AppRootFinding(
                code="app_root_missing",
                message="application root is missing",
                path=_display_path(app_root, project_root),
            )
        )
        return []
    if tracked_only:
        return _collect_git_tracked_entries(app_root, project_root, findings)
    return [
        TopLevelArtifact(name=entry.name, type="DIR" if entry.is_dir() else "FILE", source="filesystem")
        for entry in app_root.iterdir()
    ]


def _collect_git_tracked_entries(
    app_root: Path,
    project_root: Path,
    findings: list[AppRootFinding],
) -> list[TopLevelArtifact]:
    try:
        app_root_rel = app_root.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        findings.append(
            AppRootFinding(
                code="app_root_outside_project",
                message="application root is not under project root",
                path=_display_path(app_root, project_root),
            )
        )
        return []

    try:
        result = subprocess.run(
            ["git", "ls-files", "--", app_root_rel],
            cwd=project_root,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        findings.append(
            AppRootFinding(
                code="git_ls_files_failed",
                message=f"git ls-files failed: {exc}",
                path=app_root_rel,
            )
        )
        return []

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        findings.append(
            AppRootFinding(
                code="git_ls_files_failed",
                message=f"git ls-files exited {result.returncode}: {detail}",
                path=app_root_rel,
            )
        )
        return []

    entries: dict[str, TopLevelArtifact] = {}
    prefix = f"{app_root_rel.rstrip('/')}/"
    for tracked_path in result.stdout.splitlines():
        tracked_path = tracked_path.replace("\\", "/")
        if not tracked_path.startswith(prefix):
            continue
        remainder = tracked_path[len(prefix) :]
        if not remainder:
            continue
        name = remainder.split("/", 1)[0]
        component_path = app_root / name
        artifact_type = "DIR" if "/" in remainder or component_path.is_dir() else "FILE"
        if not component_path.exists():
            findings.append(
                AppRootFinding(
                    code="tracked_artifact_missing",
                    message=f"tracked artifact {name} is missing from the app root",
                    path=f"{app_root_rel}/{name}",
                )
            )
        entries[name] = TopLevelArtifact(name=name, type=artifact_type, source="git-tracked")

    return list(entries.values())


def _with_existing_registered_local_entries(
    actual_entries: list[TopLevelArtifact],
    registry_entries: list[dict[str, Any]],
    app_root: Path,
) -> list[TopLevelArtifact]:
    actual_by_key = {entry.key: entry for entry in actual_entries}
    for registry_entry in registry_entries:
        name = registry_entry["name"]
        registry_type = registry_entry["type"]
        key = (name, registry_type)
        if key in actual_by_key:
            continue
        path = app_root / name
        if not path.exists():
            continue
        actual_type = "DIR" if path.is_dir() else "FILE"
        actual_by_key[(name, actual_type)] = TopLevelArtifact(
            name=name,
            type=actual_type,
            source="registered-local",
        )
    return list(actual_by_key.values())


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
                    code="unregistered_top_level_artifact",
                    message=f"{entry.name} ({entry.type}) has no registry entry",
                    path=_display_path(app_root / entry.name, project_root),
                )
            )

    for key, entry in sorted(registry_by_key.items()):
        if key not in actual_by_key:
            findings.append(
                AppRootFinding(
                    code="registry_entry_without_artifact",
                    message=f"{entry['name']} ({entry['type']}) is registered but absent",
                    path=_display_path(app_root / str(entry["name"]), project_root),
                )
            )


def _non_empty_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _display_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()
