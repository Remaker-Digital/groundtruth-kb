# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Project manifest — extends groundtruth.toml with a [project] section."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, fields
from datetime import UTC, datetime
from pathlib import Path

from groundtruth_kb import __version__

SCAFFOLD_VERSION = __version__


@dataclass
class ProjectManifest:
    """Metadata about how this project was scaffolded."""

    project_name: str
    owner: str
    profile: str
    copyright_notice: str = ""
    cloud_provider: str = "none"
    scaffold_version: str = SCAFFOLD_VERSION
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_manifest(toml_path: Path, manifest: ProjectManifest) -> None:
    """Append a [project] section to an existing groundtruth.toml."""
    lines: list[str] = []
    if toml_path.exists():
        lines = toml_path.read_text(encoding="utf-8").splitlines()

    # Remove any existing [project] section
    filtered: list[str] = []
    in_project = False
    for line in lines:
        stripped = line.strip()
        if stripped == "[project]":
            in_project = True
            continue
        if in_project and stripped.startswith("["):
            in_project = False
        if not in_project:
            filtered.append(line)

    # Append new [project] section
    if filtered and filtered[-1].strip():
        filtered.append("")
    filtered.append("[project]")
    for f in fields(manifest):
        val = getattr(manifest, f.name)
        filtered.append(f'{f.name} = "{val}"')
    filtered.append("")

    toml_path.write_text("\n".join(filtered), encoding="utf-8")


def read_manifest(toml_path: Path) -> ProjectManifest | None:
    """Read the [project] section from groundtruth.toml, or None if absent."""
    if not toml_path.exists():
        return None
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
    section = data.get("project")
    if not section:
        return None
    return ProjectManifest(
        project_name=section.get("project_name", ""),
        owner=section.get("owner", ""),
        profile=section.get("profile", "local-only"),
        copyright_notice=section.get("copyright_notice", ""),
        cloud_provider=section.get("cloud_provider", "none"),
        scaffold_version=section.get("scaffold_version", "0.0.0"),
        created_at=section.get("created_at", ""),
    )
