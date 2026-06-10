from pathlib import Path

STRONG_MARKERS_FILES = {"application.toml", ".gtkb-app-isolation.json"}
STRONG_MARKERS_DIRS = {"harness-state", "src", "tests"}


def has_strong_marker(app_dir: Path) -> tuple[bool, str | None]:
    """Check if app_dir contains any strong markers.

    Returns (has_marker, marker_name).
    """
    if not app_dir.is_dir():
        return False, None

    for name in STRONG_MARKERS_FILES:
        file_path = app_dir / name
        if file_path.is_file():
            return True, name

    for name in STRONG_MARKERS_DIRS:
        dir_path = app_dir / name
        if dir_path.is_dir():
            return True, f"{name}/"

    return False, None
