import os
from pathlib import Path
from typing import Any

from .allowlist import is_allowlisted_file
from .registry_check import has_registry_entry
from .strong_markers import has_strong_marker


def detect_occupancy(project_root: Path, app_name: str) -> dict[str, Any]:
    """Detect occupancy status for the given application slot.

    Returns a dict with:
        occupied: bool
        trigger: str | None ("strong_marker", "non_allowlisted_content", "registry_entry", None)
        details: str | None (e.g. filename, or list of unrecognized files)
        strong_marker: str | None
        non_allowlisted_files: list[str]
    """
    app_dir = project_root / "applications" / app_name

    # 1. Check strong markers
    has_marker, marker_name = has_strong_marker(app_dir)
    if has_marker:
        return {
            "occupied": True,
            "trigger": "strong_marker",
            "details": f"Strong marker present: {marker_name}",
            "strong_marker": marker_name,
            "non_allowlisted_files": [],
        }

    # 2. Check non-allowlisted contents
    non_allowlisted = []
    if app_dir.is_dir():
        for root, _dirs, files in os.walk(app_dir):
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                if not is_allowlisted_file(file_path):
                    # Compute relative path to app_dir
                    rel = file_path.relative_to(app_dir).as_posix()
                    non_allowlisted.append(rel)

    if non_allowlisted:
        non_allowlisted.sort()
        details = f"Non-allowlisted content present: {', '.join(non_allowlisted[:3])}"
        if len(non_allowlisted) > 3:
            details += f", and {len(non_allowlisted) - 3} more"
        return {
            "occupied": True,
            "trigger": "non_allowlisted_content",
            "details": details,
            "strong_marker": None,
            "non_allowlisted_files": non_allowlisted,
        }

    # 3. Check registry entry
    if has_registry_entry(project_root, app_name):
        return {
            "occupied": True,
            "trigger": "registry_entry",
            "details": "Registry entry exists but no application directory"
            if not app_dir.is_dir()
            else "Registry entry exists",
            "strong_marker": None,
            "non_allowlisted_files": [],
        }

    return {"occupied": False, "trigger": None, "details": None, "strong_marker": None, "non_allowlisted_files": []}
