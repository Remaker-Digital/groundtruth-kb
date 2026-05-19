"""Tests for scripts/generate_antigravity_skill_adapters.py (WI-3347).

Covers the Antigravity-specific behaviour that distinguishes this generator
from the Codex generator: the loyal-opposition role filter, BOM-aware
frontmatter placement, check mode, the manifest, and the insert-or-rewrite
[capabilities.antigravity] registry update.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "generate_antigravity_skill_adapters.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("generate_antigravity_skill_adapters", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_antigravity_skill_adapters"] = module
    spec.loader.exec_module(module)
    return module


def _write_skill(project_root: Path, directory: str, *, name: str | None = None, bom: bool = False) -> None:
    skill_dir = project_root / ".claude" / "skills" / directory
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_name = name or directory
    content = f"---\nname: {skill_name}\ndescription: Test skill {skill_name}.\n---\n\n# {skill_name}\n\nBody.\n"
    if bom:
        content = chr(0xFEFF) + content
    skill_dir.joinpath("SKILL.md").write_text(content, encoding="utf-8")


def _write_registry(project_root: Path, *, existing_antigravity_block: bool = False) -> None:
    registry_path = project_root / "config" / "agent-control" / "harness-capability-registry.toml"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    antigravity = ""
    if existing_antigravity_block:
        antigravity = (
            "\n\n[capabilities.antigravity]\n"
            'surface = ".agent/skills/review/SKILL.md"\n'
            'status = "adapter"\n'
            'adapter_source = ".claude/skills/review/SKILL.md"\n'
            'source_sha256 = "stalehash"'
        )
    registry_path.write_text(
        f'''registry_id = "test-registry"
purpose = "test"

[[capabilities]]
id = "skill.review"
kind = "skill"
canonical_name = "review"
canonical_source = ".claude/skills/review/SKILL.md"
required_for_roles = ["loyal-opposition", "prime-builder"]
parity_class = "required"

[capabilities.claude]
surface = ".claude/skills/review/SKILL.md"
status = "native"

[capabilities.codex]
surface = ".codex/skills/review/SKILL.md"
status = "adapter"
adapter_source = ".claude/skills/review/SKILL.md"
source_sha256 = "codexhash"{antigravity}

[[capabilities]]
id = "skill.build"
kind = "skill"
canonical_name = "build"
canonical_source = ".claude/skills/build/SKILL.md"
required_for_roles = ["prime-builder"]
parity_class = "baseline"

[capabilities.claude]
surface = ".claude/skills/build/SKILL.md"
status = "native"

[capabilities.codex]
surface = ".codex/skills/build/SKILL.md"
status = "adapter"
adapter_source = ".claude/skills/build/SKILL.md"
source_sha256 = "codexhash2"
''',
        encoding="utf-8",
    )


def test_role_filter_excludes_prime_builder_only_skills(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_skill(tmp_path, "build")
    _write_registry(tmp_path)

    changed, adapters = module.generate(tmp_path)

    assert adapters == [".agent/skills/review/SKILL.md"]
    assert (tmp_path / ".agent" / "skills" / "review" / "SKILL.md").is_file()
    assert not (tmp_path / ".agent" / "skills" / "build").exists()
    assert ".agent/skills/review/SKILL.md" in changed
    assert ".agent/skills/MANIFEST.json" in changed


def test_marker_block_follows_frontmatter_for_bom_source(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review", bom=True)
    _write_registry(tmp_path)

    module.generate(tmp_path)

    adapter_text = (tmp_path / ".agent" / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
    assert not adapter_text.startswith(chr(0xFEFF))
    assert adapter_text.startswith("---\nname: review\n")
    assert "\n---\n<!-- GTKB-ANTIGRAVITY-SKILL-ADAPTER" in adapter_text
    assert "Canonical source: .claude/skills/review/SKILL.md" in adapter_text
    assert "Canonical source sha256:" in adapter_text


def test_check_mode_reports_drift_without_writing(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)

    changed, _adapters = module.generate(tmp_path, check=True)

    assert ".agent/skills/review/SKILL.md" in changed
    assert not (tmp_path / ".agent").exists()


def test_current_adapters_pass_check_mode(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)
    module.generate(tmp_path)

    changed, adapters = module.generate(tmp_path, check=True)

    assert changed == []
    assert adapters == [".agent/skills/review/SKILL.md"]


def test_manifest_lists_only_lo_scoped_adapters(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_skill(tmp_path, "build")
    _write_registry(tmp_path)
    module.generate(tmp_path)

    manifest = json.loads((tmp_path / ".agent" / "skills" / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["harness"] == "antigravity"
    assert [a["adapter_relative_path"] for a in manifest["adapters"]] == [".agent/skills/review/SKILL.md"]


def test_update_registry_inserts_antigravity_block(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_skill(tmp_path, "build")
    _write_registry(tmp_path)

    adapters = module.build_adapters(tmp_path)
    changed = module.update_registry(tmp_path, adapters)

    registry_text = (tmp_path / "config" / "agent-control" / "harness-capability-registry.toml").read_text(
        encoding="utf-8"
    )
    assert changed is True
    assert registry_text.count("[capabilities.antigravity]") == 1
    assert 'surface = ".agent/skills/review/SKILL.md"' in registry_text
    parsed = tomllib.loads(registry_text)
    review = next(c for c in parsed["capabilities"] if c["id"] == "skill.review")
    build = next(c for c in parsed["capabilities"] if c["id"] == "skill.build")
    assert review["antigravity"]["status"] == "adapter"
    assert review["antigravity"]["adapter_source"] == ".claude/skills/review/SKILL.md"
    assert "antigravity" not in build


def test_update_registry_rewrites_existing_block(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_skill(tmp_path, "build")
    _write_registry(tmp_path, existing_antigravity_block=True)

    adapters = module.build_adapters(tmp_path)
    changed = module.update_registry(tmp_path, adapters)

    registry_text = (tmp_path / "config" / "agent-control" / "harness-capability-registry.toml").read_text(
        encoding="utf-8"
    )
    assert changed is True
    assert registry_text.count("[capabilities.antigravity]") == 1
    assert "stalehash" not in registry_text
    parsed = tomllib.loads(registry_text)
    review = next(c for c in parsed["capabilities"] if c["id"] == "skill.review")
    assert review["antigravity"]["source_sha256"] != "stalehash"


def test_update_registry_is_idempotent(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_skill(tmp_path, "build")
    _write_registry(tmp_path)

    adapters = module.build_adapters(tmp_path)
    assert module.update_registry(tmp_path, adapters) is True
    assert module.update_registry(tmp_path, adapters) is False
