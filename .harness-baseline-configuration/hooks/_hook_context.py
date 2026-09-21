"""Root and registration identity for authored hooks running in place.

Runtime roots come from the event, the native adapter, or a project marker.
An unmarked current working directory never becomes the installation root.
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


def resolve_root(payload: Mapping[str, Any] | None = None) -> Path:
    payload = payload or {}
    for value in (payload.get("project_root"), os.environ.get("GTKB_PROJECT_ROOT")):
        if isinstance(value, str) and value.strip():
            path = Path(value).expanduser()
            if path.is_absolute():
                return path.resolve()
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd.strip() and Path(cwd).is_absolute():
        start = Path(cwd).resolve()
        for candidate in (start, *start.parents):
            if (candidate / "groundtruth.toml").is_file():
                return candidate
    return Path(__file__).absolute().parents[2]


def harness_name(argv: Sequence[str]) -> str | None:
    for index, value in enumerate(argv):
        if value == "--harness" and index + 1 < len(argv):
            candidate = argv[index + 1]
            return candidate if candidate and not candidate.startswith("-") else None
    return None
