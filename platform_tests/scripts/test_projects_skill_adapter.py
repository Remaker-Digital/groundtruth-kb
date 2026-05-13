from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_projects_skill_registry_and_manifest_are_declared() -> None:
    registry = REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"
    manifest = json.loads((REPO_ROOT / ".codex" / "skills" / "MANIFEST.json").read_text(encoding="utf-8"))
    registry_text = registry.read_text(encoding="utf-8")

    assert 'id = "skill.projects"' in registry_text
    assert 'canonical_source = ".claude/skills/projects/SKILL.md"' in registry_text
    assert 'surface = ".codex/skills/projects/SKILL.md"' in registry_text
    assert any(entry["capability_id"] == "skill.projects" for entry in manifest["adapters"])


def test_projects_codex_adapter_matches_canonical_skill() -> None:
    canonical = (REPO_ROOT / ".claude" / "skills" / "projects" / "SKILL.md").read_text(encoding="utf-8")
    adapter = (REPO_ROOT / ".codex" / "skills" / "projects" / "SKILL.md").read_text(encoding="utf-8")

    assert "name: projects" in canonical
    assert "Canonical source: .claude/skills/projects/SKILL.md" in adapter
    assert "<!-- GTKB-CODEX-SKILL-ADAPTER" in adapter
    assert "Do not create new project or backlog authority tables." in adapter


def test_projects_skill_adapter_generator_check_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_codex_skill_adapters.py", "--check", "--update-registry"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
