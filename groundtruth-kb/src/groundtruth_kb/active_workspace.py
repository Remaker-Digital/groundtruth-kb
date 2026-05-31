"""Active-workspace resolver for GT-KB control-plane boundaries."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, NamedTuple

WorkspaceValue = Literal["gt-kb", "hosted-application"]
WorkspaceSource = Literal["project_default", "harness_record", "owner_confirmed"]


class WorkspaceResolution(NamedTuple):
    active_workspace: WorkspaceValue
    hosted_application_id: str | None
    source: WorkspaceSource


VALID_WORKSPACES = {"gt-kb", "hosted-application"}


def _read_record(path: Path) -> dict[str, str] | None | str:
    if not path.exists():
        return None
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            return f"blocking diagnostic: malformed active-workspace record at {path}"
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def _resolution_from_record(record: dict[str, str], source: WorkspaceSource) -> WorkspaceResolution | str:
    workspace = record.get("active_workspace", "gt-kb")
    if workspace not in VALID_WORKSPACES:
        return f"blocking diagnostic: unsupported active_workspace value {workspace!r}"
    hosted_application_id = record.get("hosted_application_id") or None
    if workspace == "hosted-application" and not hosted_application_id:
        return "blocking diagnostic: hosted-application workspace requires hosted_application_id"
    if workspace == "gt-kb":
        hosted_application_id = None
    return WorkspaceResolution(workspace, hosted_application_id, source)  # type: ignore[arg-type]


def resolve(project_root: Path, harness_id: str | None = None) -> WorkspaceResolution | str:
    """Return an active-workspace resolution or a blocking diagnostic string."""

    root = Path(project_root)
    project_record = _read_record(root / ".claude" / "rules" / "active-workspace.md")
    if isinstance(project_record, str):
        return project_record
    if project_record is None:
        project_record = {"active_workspace": "gt-kb"}

    project_resolution = _resolution_from_record(project_record, "project_default")
    if isinstance(project_resolution, str):
        return project_resolution

    if not harness_id:
        return project_resolution

    harness_record = _read_record(root / "harness-state" / harness_id / "active-workspace.md")
    if isinstance(harness_record, str):
        return harness_record
    if harness_record is None or not harness_record:
        return project_resolution

    harness_resolution = _resolution_from_record(harness_record, "harness_record")
    if isinstance(harness_resolution, str):
        return harness_resolution
    if harness_resolution != project_resolution and harness_record.get("owner_confirmed") != "true":
        return "blocking diagnostic: divergent harness active-workspace record lacks owner_confirmed: true"
    if harness_record.get("owner_confirmed") == "true":
        return WorkspaceResolution(
            harness_resolution.active_workspace,
            harness_resolution.hosted_application_id,
            "owner_confirmed",
        )
    return harness_resolution
