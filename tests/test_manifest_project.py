# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.project.manifest — read_manifest and write_manifest."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.manifest import ProjectManifest, read_manifest, write_manifest


def test_write_then_read_round_trips(tmp_path: Path) -> None:
    """write_manifest() then read_manifest() round-trips all fields correctly."""
    toml_path = tmp_path / "groundtruth.toml"
    # Start with a minimal base TOML (no [project] section yet)
    toml_path.write_text(
        "[groundtruth]\ndb_path = 'groundtruth.db'\n",
        encoding="utf-8",
    )
    manifest = ProjectManifest(
        project_name="Round Trip Test",
        owner="Test Owner",
        profile="dual-agent",
        copyright_notice="Copyright 2026",
        cloud_provider="azure",
        scaffold_version="1.2.3",
    )
    write_manifest(toml_path, manifest)

    result = read_manifest(toml_path)
    assert result is not None
    assert result.project_name == "Round Trip Test"
    assert result.owner == "Test Owner"
    assert result.profile == "dual-agent"
    assert result.copyright_notice == "Copyright 2026"
    assert result.cloud_provider == "azure"
    assert result.scaffold_version == "1.2.3"


def test_read_manifest_no_project_section_returns_none(tmp_path: Path) -> None:
    """read_manifest() on file without [project] section returns None."""
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text(
        "[groundtruth]\ndb_path = 'groundtruth.db'\n",
        encoding="utf-8",
    )
    result = read_manifest(toml_path)
    assert result is None


def test_read_manifest_missing_file_returns_none(tmp_path: Path) -> None:
    """read_manifest() on non-existent file returns None."""
    result = read_manifest(tmp_path / "nonexistent.toml")
    assert result is None


def test_write_manifest_replaces_existing_project_section(tmp_path: Path) -> None:
    """write_manifest() replaces an existing [project] section."""
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text(
        "[groundtruth]\ndb_path = 'groundtruth.db'\n\n[project]\nproject_name = \"Old Name\"\n",
        encoding="utf-8",
    )
    manifest = ProjectManifest(
        project_name="New Name",
        owner="New Owner",
        profile="local-only",
    )
    write_manifest(toml_path, manifest)

    result = read_manifest(toml_path)
    assert result is not None
    assert result.project_name == "New Name"
    assert result.owner == "New Owner"


def test_project_manifest_auto_created_at(tmp_path: Path) -> None:
    """ProjectManifest auto-sets created_at when not provided."""
    manifest = ProjectManifest(project_name="x", owner="y", profile="local-only")
    assert manifest.created_at != ""
    # Should be a parseable ISO timestamp
    from datetime import datetime

    dt = datetime.fromisoformat(manifest.created_at.replace("Z", "+00:00"))
    assert dt.year >= 2026
