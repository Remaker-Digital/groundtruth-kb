from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "generate_codex_skill_adapters.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("generate_codex_skill_adapters", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_codex_skill_adapters"] = module
    spec.loader.exec_module(module)
    return module


def _write_skill(project_root: Path, directory: str, name: str | None = None) -> None:
    skill_dir = project_root / ".claude" / "skills" / directory
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_name = name or directory
    skill_dir.joinpath("SKILL.md").write_text(
        f"---\nname: {skill_name}\ndescription: Test skill.\n---\n\n# {skill_name}\n\nBody.\n",
        encoding="utf-8",
    )


def _write_registry(project_root: Path) -> None:
    registry_path = project_root / "config" / "agent-control" / "harness-capability-registry.toml"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        """
registry_id = "test-registry"
purpose = "test"

[[capabilities]]
id = "skill.review"
kind = "skill"
canonical_name = "review"
canonical_source = ".claude/skills/review/SKILL.md"
required_for_roles = ["loyal-opposition"]
parity_class = "required"

[capabilities.claude]
surface = ".claude/skills/review/SKILL.md"
status = "native"

[capabilities.codex]
surface = ".codex/skills/review/SKILL.md"
status = "adapter"
adapter_source = ".claude/skills/review/SKILL.md"
""".lstrip(),
        encoding="utf-8",
    )


def test_generates_codex_adapter_with_source_metadata(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)

    changed, adapters = module.generate(tmp_path)

    adapter_path = tmp_path / ".codex" / "skills" / "review" / "SKILL.md"
    adapter_text = adapter_path.read_text(encoding="utf-8")
    assert changed == [
        ".codex/skills/review/SKILL.md",
        ".codex/skills/MANIFEST.json",
    ]
    assert adapters == [".codex/skills/review/SKILL.md"]
    assert adapter_text.startswith("---\nname: review\n")
    assert "GTKB-CODEX-SKILL-ADAPTER" in adapter_text
    assert "Canonical source: .claude/skills/review/SKILL.md" in adapter_text
    assert "Canonical source sha256:" in adapter_text

    manifest = json.loads((tmp_path / ".codex" / "skills" / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["adapters"][0]["adapter_relative_path"] == ".codex/skills/review/SKILL.md"


def test_check_mode_reports_adapter_drift_without_writing(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)

    changed, _adapters = module.generate(tmp_path, check=True)

    assert changed == [
        ".codex/skills/review/SKILL.md",
        ".codex/skills/MANIFEST.json",
    ]
    assert not (tmp_path / ".codex").exists()


def _write_skill_with_frontmatter(project_root: Path, directory: str, frontmatter_lines: str) -> None:
    skill_dir = project_root / ".claude" / "skills" / directory
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_dir.joinpath("SKILL.md").write_text(
        f"---\nname: {directory}\ndescription: Test skill.\n{frontmatter_lines}---\n\n# {directory}\n\nBody.\n",
        encoding="utf-8",
    )


def test_bracketed_argument_hint_is_quoted_on_emit(tmp_path: Path) -> None:
    """WI-4461: a multi-bracket argument-hint is quoted in the generated adapter
    so Codex's strict YAML parser can load it, and the emitted frontmatter
    strict-parses.
    """
    module = _load_module()
    _write_skill_with_frontmatter(tmp_path, "review", "argument-hint: [unit|live] [options]\n")
    _write_registry(tmp_path)

    module.generate(tmp_path)

    adapter_text = (tmp_path / ".codex" / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
    assert 'argument-hint: "[unit|live] [options]"' in adapter_text
    fm = adapter_text[3 : adapter_text.index("\n---", 3)]
    yaml.safe_load(fm)  # must not raise


def test_single_bracket_argument_hint_left_unquoted(tmp_path: Path) -> None:
    """The fix is scoped to the genuinely-broken multi-bracket form; a single
    flow-sequence argument-hint is valid YAML and is left unchanged.
    """
    module = _load_module()
    _write_skill_with_frontmatter(tmp_path, "review", "argument-hint: [options]\n")
    _write_registry(tmp_path)

    module.generate(tmp_path)

    adapter_text = (tmp_path / ".codex" / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
    assert "argument-hint: [options]" in adapter_text
    fm = adapter_text[3 : adapter_text.index("\n---", 3)]
    yaml.safe_load(fm)  # still strict-valid


def test_generator_strict_validation_rejects_malformed_frontmatter() -> None:
    """WI-4461: the strict-YAML gate (the deterministic parity check WI-4264
    intended) fails closed on frontmatter that is not strict-YAML-valid.
    """
    module = _load_module()
    with pytest.raises(module.SkillFrontmatterError):
        module._assert_strict_yaml_frontmatter("name: x\nallowed-tools: [a] [b]\n", ".codex/skills/x/SKILL.md")


def test_all_generated_adapters_strict_yaml_valid() -> None:
    """WI-4461 regression guard: every committed .codex skill adapter's
    frontmatter must parse under strict YAML (Codex's parser).
    """
    adapters = sorted((REPO_ROOT / ".codex" / "skills").glob("*/SKILL.md"))
    assert adapters, "no codex skill adapters found"
    failures: list[str] = []
    for path in adapters:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        fm = text[3:end] if end != -1 else text
        try:
            yaml.safe_load(fm)
        except yaml.YAMLError as exc:
            failures.append(f"{path.relative_to(REPO_ROOT)}: {exc}")
    assert not failures, "strict-YAML-invalid adapter frontmatter:\n" + "\n".join(failures)


def test_existing_current_adapters_pass_check_mode(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)
    module.generate(tmp_path)

    changed, adapters = module.generate(tmp_path, check=True)

    assert changed == []
    assert adapters == [".codex/skills/review/SKILL.md"]


def test_update_registry_points_codex_at_generated_adapter(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)

    adapters = module.build_adapters(tmp_path)
    changed = module.update_registry(tmp_path, adapters)

    registry_text = (tmp_path / "config" / "agent-control" / "harness-capability-registry.toml").read_text(
        encoding="utf-8"
    )
    assert changed is True
    assert 'surface = ".codex/skills/review/SKILL.md"' in registry_text
    assert 'status = "adapter"' in registry_text
    assert 'adapter_source = ".claude/skills/review/SKILL.md"' in registry_text
    assert "source_sha256 =" in registry_text
