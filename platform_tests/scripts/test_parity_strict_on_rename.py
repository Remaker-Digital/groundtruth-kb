"""Tests for --strict-on-rename flag in check_harness_parity.py (GFR Slice D Finding 4.5).

Work item: WI-5646 (TEST-11691).
Governing: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_harness_parity.py"

spec = importlib.util.spec_from_file_location("check_harness_parity", SCRIPT_PATH)
assert spec is not None
parity = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["check_harness_parity"] = parity
spec.loader.exec_module(parity)


class TestStrictOnRename:
    """Finding 4.5: --strict-on-rename should flag stale dir names."""

    def test_check_rename_map_consistency_passes_when_consistent(self, tmp_path: Path) -> None:
        # Create a minimal skills dir with a matching entry
        skills_dir = tmp_path / ".claude" / "skills"
        skill_dir = skills_dir / "gtkb-test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: gtkb-test-skill\n---\n", encoding="utf-8")

        # Create rename-map
        config_dir = tmp_path / "config" / "agent-control"
        config_dir.mkdir(parents=True)
        (config_dir / "skill-rename-map.toml").write_text(
            'schema_version = 1\n\n[[skills]]\ndir = "gtkb-test-skill"\ncanonical_name = "gtkb-test-skill"\nregistry_old_name = ""\n',
            encoding="utf-8",
        )

        results = parity._check_rename_map_consistency(tmp_path)
        assert results == []

    def test_check_rename_map_flags_stale_dir(self, tmp_path: Path) -> None:
        # Create skills dir with a DIFFERENT name than the map says
        skills_dir = tmp_path / ".claude" / "skills"
        old_skill_dir = skills_dir / "gtkb-old-name"
        old_skill_dir.mkdir(parents=True)
        (old_skill_dir / "SKILL.md").write_text("---\nname: gtkb-test-skill\n---\n", encoding="utf-8")

        config_dir = tmp_path / "config" / "agent-control"
        config_dir.mkdir(parents=True)
        (config_dir / "skill-rename-map.toml").write_text(
            'schema_version = 1\n\n[[skills]]\ndir = "gtkb-new-name"\ncanonical_name = "gtkb-test-skill"\nregistry_old_name = ""\n',
            encoding="utf-8",
        )

        results = parity._check_rename_map_consistency(tmp_path)
        assert len(results) > 0
        assert any(r.get("type") == "STALE_NAME" for r in results)

    def test_check_rename_map_flags_name_mismatch(self, tmp_path: Path) -> None:
        # Create skills dir with matching dir name but mismatched canonical_name
        skills_dir = tmp_path / ".claude" / "skills"
        skill_dir = skills_dir / "gtkb-test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: gtkb-wrong-name\n---\n", encoding="utf-8")

        config_dir = tmp_path / "config" / "agent-control"
        config_dir.mkdir(parents=True)
        (config_dir / "skill-rename-map.toml").write_text(
            'schema_version = 1\n\n[[skills]]\ndir = "gtkb-test-skill"\ncanonical_name = "gtkb-correct-name"\nregistry_old_name = ""\n',
            encoding="utf-8",
        )

        results = parity._check_rename_map_consistency(tmp_path)
        assert len(results) > 0
        assert any(r.get("type") == "NAME_MISMATCH" for r in results)
