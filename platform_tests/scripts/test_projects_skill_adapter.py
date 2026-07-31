from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _canonical_hash(text: str) -> str:
    return hashlib.sha256((text.rstrip() + "\n").encode("utf-8")).hexdigest()


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
    source_hash = _canonical_hash(canonical)

    assert "name: projects" in canonical
    assert "Canonical source: .claude/skills/projects/SKILL.md" in adapter
    assert f"Canonical source sha256: {source_hash}" in adapter
    assert "<!-- GTKB-CODEX-SKILL-ADAPTER" in adapter
    assert "CLI-only backlog/project access" in adapter
    assert "--field" in adapter
    assert "Do not create new project or backlog authority tables." in adapter


def test_projects_skill_documents_cli_only_backlog_access() -> None:
    canonical = (REPO_ROOT / ".claude" / "skills" / "projects" / "SKILL.md").read_text(encoding="utf-8")

    assert "CLI-only backlog/project access" in canonical
    assert "gt backlog list" in canonical
    assert "--approval-state" in canonical
    assert "--match" in canonical
    assert "--range" in canonical
    assert "--field" in canonical
    assert "--member-of" in canonical
    assert "Do not open `groundtruth.db` with SQLite" in canonical


def test_projects_skill_adapters_are_current_across_target_harnesses() -> None:
    canonical = (REPO_ROOT / ".claude" / "skills" / "projects" / "SKILL.md").read_text(encoding="utf-8")
    source_hash = _canonical_hash(canonical)
    full_body_adapters = [
        REPO_ROOT / ".codex" / "skills" / "projects" / "SKILL.md",
        REPO_ROOT / ".agent" / "skills" / "projects" / "SKILL.md",
        REPO_ROOT / ".cursor" / "skills" / "projects" / "SKILL.md",
    ]
    for adapter_path in full_body_adapters:
        adapter = adapter_path.read_text(encoding="utf-8")
        assert f"Canonical source sha256: {source_hash}" in adapter
        assert "CLI-only backlog/project access" in adapter
        assert "gt backlog list --field source_owner_directive:DELIB-123 --json" in adapter
        assert "Do not open `groundtruth.db` with SQLite" in adapter

    api_adapter = (REPO_ROOT / ".api-harness" / "skills" / "projects" / "SKILL.md").read_text(encoding="utf-8")
    assert f"Canonical source sha256: `{source_hash}`" in api_adapter
    assert "read the canonical source file" in api_adapter
