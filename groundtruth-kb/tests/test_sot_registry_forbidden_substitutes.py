"""Tests for DCL-SOT-REGISTRY-RECORD-SCHEMA-001 v2 forbidden_substitutes column.

Verifies (a) loader accepts records with the column populated, (b) loader accepts
records without it, (c) loader rejects records where the value is not a
list-of-strings, and (d) canonical TOML round-trip preserves the column verbatim.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.project.registry_control_plane import serialize_registry
from groundtruth_kb.project.sot_registry import (
    InvalidSoTRecord,
    load_toml,
)


def _write_toml(tmp_path: Path, *, forbidden: str = "") -> Path:
    base = """\
[[artifacts]]
id = "sot-registry-toml"
domain = "control_surface"
lifecycle = "active"
storage_path = "config/registry/sot-artifacts.toml"
coverage_mode = "exact"
authority_spec_id = "GOV-PLATFORM-SOT-REGISTRY-001"
mutation_api = "gt registry amend"
versioning_policy = "git_tracked"
backup_policy = "git_tracked"
health_check_function = "_check_sot_registry_completeness"
owner_role = "owner_only"
"""
    if forbidden:
        base += forbidden + "\n"
    path = tmp_path / "registry.toml"
    path.write_text(base, encoding="utf-8")
    return path


def test_loader_accepts_populated_forbidden_substitutes(tmp_path: Path) -> None:
    path = _write_toml(tmp_path, forbidden='forbidden_substitutes = [".claude/rules/foo.md", "memory/bar.md"]')
    records = load_toml(path)
    assert len(records) == 1
    assert records[0].forbidden_substitutes == (".claude/rules/foo.md", "memory/bar.md")


def test_loader_accepts_missing_forbidden_substitutes(tmp_path: Path) -> None:
    path = _write_toml(tmp_path)
    records = load_toml(path)
    assert len(records) == 1
    assert records[0].forbidden_substitutes == ()


def test_loader_accepts_empty_forbidden_substitutes(tmp_path: Path) -> None:
    path = _write_toml(tmp_path, forbidden="forbidden_substitutes = []")
    records = load_toml(path)
    assert len(records) == 1
    assert records[0].forbidden_substitutes == ()


def test_loader_rejects_non_list_forbidden_substitutes(tmp_path: Path) -> None:
    path = _write_toml(tmp_path, forbidden='forbidden_substitutes = "just-a-string"')
    with pytest.raises((InvalidSoTRecord, TypeError, ValueError)):
        load_toml(path)


@pytest.mark.parametrize(
    "forbidden", ['forbidden_substitutes = [".claude/rules/foo.md", "memory/bar.md"]', "forbidden_substitutes = []"]
)
def test_canonical_declaration_roundtrip_preserves_forbidden_substitutes(tmp_path, forbidden):
    path = _write_toml(tmp_path, forbidden=forbidden)
    before = load_toml(path)
    path.write_bytes(serialize_registry(before))
    assert load_toml(path) == before
    assert not list(tmp_path.glob("*.db"))
