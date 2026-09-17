"""Observe existing slot content without filename or content-based exemptions."""

from pathlib import Path
from typing import Any

from .registry_check import application_slot_path, has_registry_entry


def detect_occupancy(project_root: Path, app_name: str) -> dict[str, Any]:
    """Return read-only presence facts, never permission to register or remove files.

    Every top-level entry counts. No file body, historical cleanup marker,
    ignore rule, generated projection or filename implies that data is disposable.
    """
    app_dir = application_slot_path(project_root, app_name)
    registered = has_registry_entry(project_root, app_name)
    entries = sorted(child.name for child in app_dir.iterdir()) if app_dir.is_dir() else []
    if registered:
        return {
            "occupied": True,
            "trigger": "registry_entry",
            "details": "Registry entry exists"
            if app_dir.is_dir()
            else "Registry entry exists but no application directory",
            "entries": entries,
        }
    if entries:
        return {
            "occupied": True,
            "trigger": "existing_content",
            "details": f"Existing top-level content: {', '.join(entries[:3])}",
            "entries": entries,
        }
    return {"occupied": False, "trigger": None, "details": None, "entries": []}
