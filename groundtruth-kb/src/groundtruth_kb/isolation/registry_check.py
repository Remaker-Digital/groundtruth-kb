import tomllib
from pathlib import Path


def has_registry_entry(project_root: Path, app_name: str) -> bool:
    """Return True if registry.toml exists and contains an entry for app_name."""
    registry_path = project_root / "applications" / "registry.toml"
    if not registry_path.is_file():
        return False
    try:
        with open(registry_path, "rb") as f:
            data = tomllib.load(f)
        # Check both top-level applications mapping and sub-table formats
        apps = data.get("applications", {})
        if isinstance(apps, dict) and app_name in apps:
            return True
        return False
    except Exception:
        return False
