from __future__ import annotations

import importlib.util
import json
import re
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


def _write_reference(project_root: Path, directory: str, relative_path: str, content: bytes | str) -> None:
    reference_path = project_root / ".claude" / "skills" / directory / "references" / relative_path
    reference_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        reference_path.write_bytes(content)
    else:
        reference_path.write_text(content, encoding="utf-8")


def _write_helper(project_root: Path, directory: str, relative_path: str, content: bytes | str) -> None:
    helper_path = project_root / ".claude" / "skills" / directory / "helpers" / relative_path
    helper_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        helper_path.write_bytes(content)
    else:
        helper_path.write_text(content, encoding="utf-8")


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


def test_generate_mirrors_canonical_references(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_reference(tmp_path, "review", "nested/example.md", "Reference body.\n")
    _write_reference(tmp_path, "review", "data.bin", b"\x00\x01reference")
    _write_registry(tmp_path)

    changed, _adapters = module.generate(tmp_path)

    assert ".codex/skills/review/references/nested/example.md" in changed
    assert ".codex/skills/review/references/data.bin" in changed
    assert (tmp_path / ".codex" / "skills" / "review" / "references" / "nested" / "example.md").read_text(
        encoding="utf-8"
    ) == "Reference body.\n"
    assert (tmp_path / ".codex" / "skills" / "review" / "references" / "data.bin").read_bytes() == b"\x00\x01reference"


def test_generate_mirrors_canonical_helpers(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_helper(tmp_path, "review", "nested/tool.py", "print('helper')\n")
    _write_helper(tmp_path, "review", "data.bin", b"\x00\x01helper")
    _write_helper(tmp_path, "review", "__pycache__/tool.pyc", b"cache")
    _write_registry(tmp_path)

    changed, _adapters = module.generate(tmp_path)

    assert ".codex/skills/review/helpers/nested/tool.py" in changed
    assert ".codex/skills/review/helpers/data.bin" in changed
    assert ".codex/skills/review/helpers/__pycache__/tool.pyc" not in changed
    assert (tmp_path / ".codex" / "skills" / "review" / "helpers" / "nested" / "tool.py").read_text(
        encoding="utf-8"
    ) == "print('helper')\n"
    assert (tmp_path / ".codex" / "skills" / "review" / "helpers" / "data.bin").read_bytes() == b"\x00\x01helper"
    assert not (tmp_path / ".codex" / "skills" / "review" / "helpers" / "__pycache__" / "tool.pyc").exists()


def test_generate_rewrites_canonical_helper_paths_to_codex_adapter_paths(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    skill_path = tmp_path / ".claude" / "skills" / "review" / "SKILL.md"
    skill_path.write_text(
        skill_path.read_text(encoding="utf-8")
        + "\nUse `.claude/skills/review/helpers/tool.py` and `.claude\\skills\\review\\helpers\\win.py`.\n",
        encoding="utf-8",
    )
    _write_helper(tmp_path, "review", "tool.py", "print('slash')\n")
    _write_helper(tmp_path, "review", "win.py", "print('backslash')\n")
    _write_registry(tmp_path)

    module.generate(tmp_path)

    adapter_text = (tmp_path / ".codex" / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
    assert ".claude/skills/review/helpers/tool.py" not in adapter_text
    assert ".claude\\skills\\review\\helpers\\win.py" not in adapter_text
    assert ".codex/skills/review/helpers/tool.py" in adapter_text
    assert ".codex\\skills\\review\\helpers\\win.py" in adapter_text
    assert (tmp_path / ".codex" / "skills" / "review" / "helpers" / "tool.py").is_file()
    assert (tmp_path / ".codex" / "skills" / "review" / "helpers" / "win.py").is_file()


def test_check_reports_missing_reference_as_drift(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_reference(tmp_path, "review", "taxonomy.md", "Canonical reference.\n")
    _write_registry(tmp_path)
    module.generate(tmp_path)
    adapter_reference = tmp_path / ".codex" / "skills" / "review" / "references" / "taxonomy.md"
    adapter_reference.unlink()

    changed, _adapters = module.generate(tmp_path, check=True)

    assert ".codex/skills/review/references/taxonomy.md" in changed
    assert not adapter_reference.exists()


def test_check_reports_missing_helper_as_drift(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_helper(tmp_path, "review", "tool.py", "print('helper')\n")
    _write_registry(tmp_path)
    module.generate(tmp_path)
    adapter_helper = tmp_path / ".codex" / "skills" / "review" / "helpers" / "tool.py"
    adapter_helper.unlink()

    changed, _adapters = module.generate(tmp_path, check=True)

    assert ".codex/skills/review/helpers/tool.py" in changed
    assert not adapter_helper.exists()


def test_generate_removes_orphan_reference(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_reference(tmp_path, "review", "taxonomy.md", "Canonical reference.\n")
    _write_registry(tmp_path)
    module.generate(tmp_path)
    orphan = tmp_path / ".codex" / "skills" / "review" / "references" / "stale.md"
    orphan.write_text("stale\n", encoding="utf-8")

    changed, _adapters = module.generate(tmp_path)

    assert ".codex/skills/review/references/stale.md" in changed
    assert not orphan.exists()


def test_generate_removes_orphan_helper(tmp_path: Path) -> None:
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_helper(tmp_path, "review", "tool.py", "print('helper')\n")
    _write_registry(tmp_path)
    module.generate(tmp_path)
    orphan = tmp_path / ".codex" / "skills" / "review" / "helpers" / "stale.py"
    orphan.write_text("stale\n", encoding="utf-8")

    changed, _adapters = module.generate(tmp_path)

    assert ".codex/skills/review/helpers/stale.py" in changed
    assert not orphan.exists()


def test_generate_materializes_all_drifting_references() -> None:
    module = _load_module()
    for adapter in module.build_adapters(REPO_ROOT):
        canonical_references = (REPO_ROOT / adapter.source_relative_path).parent / "references"
        canonical_files = sorted(path for path in canonical_references.rglob("*") if path.is_file())
        if not canonical_files:
            continue
        adapter_references = (REPO_ROOT / adapter.adapter_relative_path).parent / "references"
        for canonical_file in canonical_files:
            relative_reference = canonical_file.relative_to(canonical_references)
            adapter_file = adapter_references / relative_reference
            assert adapter_file.is_file(), f"missing Codex reference mirror for {adapter_file.relative_to(REPO_ROOT)}"
            assert adapter_file.read_bytes() == canonical_file.read_bytes()


def test_generate_materializes_all_drifting_helpers() -> None:
    module = _load_module()
    for adapter in module.build_adapters(REPO_ROOT):
        canonical_helpers = (REPO_ROOT / adapter.source_relative_path).parent / "helpers"
        canonical_files = sorted(
            path
            for path in canonical_helpers.rglob("*")
            if path.is_file() and module._should_mirror_resource_file(path)
        )
        if not canonical_files:
            continue
        adapter_helpers = (REPO_ROOT / adapter.adapter_relative_path).parent / "helpers"
        for canonical_file in canonical_files:
            relative_helper = canonical_file.relative_to(canonical_helpers)
            adapter_file = adapter_helpers / relative_helper
            assert adapter_file.is_file(), f"missing Codex helper mirror for {adapter_file.relative_to(REPO_ROOT)}"
            assert adapter_file.read_bytes() == canonical_file.read_bytes()


def test_generated_adapters_do_not_name_canonical_helper_paths() -> None:
    adapters = sorted((REPO_ROOT / ".codex" / "skills").glob("*/SKILL.md"))
    assert adapters, "no codex skill adapters found"
    slash_helper_path = re.compile(r"\.claude/skills/[^/\s`\"')]+/helpers/")
    backslash_helper_path = re.compile(r"\.claude\\skills\\[^\\\s`\"')]+\\helpers\\")
    offenders: list[str] = []
    for path in adapters:
        text = path.read_text(encoding="utf-8")
        if slash_helper_path.search(text):
            offenders.append(path.relative_to(REPO_ROOT).as_posix())
        if backslash_helper_path.search(text):
            offenders.append(path.relative_to(REPO_ROOT).as_posix())
    assert not offenders, "generated Codex adapters name canonical helper paths:\n" + "\n".join(sorted(offenders))


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


# ---------------------------------------------------------------------------
# WI-4701: LF-only line-ending tests
# ---------------------------------------------------------------------------


def test_generate_emits_lf_only_line_endings(tmp_path: Path) -> None:
    """WI-4701: generate must write adapter SKILL.md and MANIFEST.json with LF only."""
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)

    module.generate(tmp_path)

    adapter_path = tmp_path / ".codex" / "skills" / "review" / "SKILL.md"
    manifest_path = tmp_path / ".codex" / "skills" / "MANIFEST.json"
    assert b"\r" not in adapter_path.read_bytes(), "adapter SKILL.md contains CR"
    assert b"\r" not in manifest_path.read_bytes(), "MANIFEST.json contains CR"
    for line in adapter_path.read_text(encoding="utf-8", newline="").splitlines():
        assert line == line.rstrip(), f"trailing whitespace in adapter line: {line!r}"


def test_check_mode_detects_crlf_contaminated_adapter(tmp_path: Path) -> None:
    """WI-4701: --check must report a CRLF-contaminated adapter as drifted."""
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)
    module.generate(tmp_path)
    adapter_path = tmp_path / ".codex" / "skills" / "review" / "SKILL.md"
    # Overwrite the LF adapter with a CRLF version to simulate contamination.
    adapter_path.write_bytes(adapter_path.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))

    changed, _ = module.generate(tmp_path, check=True)

    assert ".codex/skills/review/SKILL.md" in changed


def test_generate_corrects_crlf_contaminated_adapter(tmp_path: Path) -> None:
    """WI-4701: generate (non-check) must rewrite a CRLF adapter to LF."""
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)
    module.generate(tmp_path)
    adapter_path = tmp_path / ".codex" / "skills" / "review" / "SKILL.md"
    adapter_path.write_bytes(adapter_path.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))

    module.generate(tmp_path)

    assert b"\r" not in adapter_path.read_bytes(), "adapter still contains CR after correction"


def test_generate_idempotent_after_lf_write(tmp_path: Path) -> None:
    """WI-4701: second generate in check mode after LF write must report no drift."""
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)
    module.generate(tmp_path)

    changed, _ = module.generate(tmp_path, check=True)

    assert ".codex/skills/review/SKILL.md" not in changed
    assert ".codex/skills/MANIFEST.json" not in changed


def test_update_registry_emits_lf_only_line_endings(tmp_path: Path) -> None:
    """WI-4701: update_registry must write the registry with LF-only line endings."""
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)
    adapters = module.build_adapters(tmp_path)

    module.update_registry(tmp_path, adapters)

    registry_path = tmp_path / "config" / "agent-control" / "harness-capability-registry.toml"
    assert b"\r" not in registry_path.read_bytes(), "registry contains CR after update_registry"


def test_update_registry_corrects_crlf_contamination(tmp_path: Path) -> None:
    """WI-4701: update_registry must correct a CRLF-contaminated registry to LF."""
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)
    adapters = module.build_adapters(tmp_path)
    # First call establishes the correct sha256 state.
    module.update_registry(tmp_path, adapters)
    registry_path = tmp_path / "config" / "agent-control" / "harness-capability-registry.toml"
    # Contaminate with CRLF.
    registry_path.write_bytes(registry_path.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
    assert b"\r" in registry_path.read_bytes()

    module.update_registry(tmp_path, adapters)

    assert b"\r" not in registry_path.read_bytes(), "registry still contains CR after correction"


def test_adapter_source_sha256_stable_after_lf_correction(tmp_path: Path) -> None:
    """WI-4701: source_sha256 in MANIFEST must not change when CRLF adapters are corrected."""
    module = _load_module()
    _write_skill(tmp_path, "review")
    _write_registry(tmp_path)
    module.generate(tmp_path)
    manifest_before = json.loads((tmp_path / ".codex" / "skills" / "MANIFEST.json").read_text(encoding="utf-8"))
    sha256_before = manifest_before["adapters"][0]["source_sha256"]
    adapter_path = tmp_path / ".codex" / "skills" / "review" / "SKILL.md"
    # Contaminate adapter with CRLF.
    adapter_path.write_bytes(adapter_path.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))

    module.generate(tmp_path)

    manifest_after = json.loads((tmp_path / ".codex" / "skills" / "MANIFEST.json").read_text(encoding="utf-8"))
    sha256_after = manifest_after["adapters"][0]["source_sha256"]
    assert sha256_before == sha256_after, "source_sha256 must be stable after CRLF correction"
