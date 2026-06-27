from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import generate_api_skill_adapters as gen


def write_registry(root: Path, skill_name: str = "example") -> None:
    registry = root / "config" / "agent-control" / "harness-capability-registry.toml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        f"""
[[capabilities]]
id = "skill.{skill_name}"
kind = "skill"
canonical_name = "{skill_name}"
canonical_source = ".claude/skills/{skill_name}/SKILL.md"
""".strip()
        + "\n",
        encoding="utf-8",
    )


def write_skill(root: Path, skill_name: str = "example", *, body: str = "UNIQUE_CANONICAL_BODY") -> None:
    skill = root / ".claude" / "skills" / skill_name / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        f"""
---
name: {skill_name}
description: Example skill description for API adapter tests.
---

# /{skill_name}

{body}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_generate_writes_compact_adapter_and_manifest(tmp_path: Path) -> None:
    write_registry(tmp_path)
    write_skill(tmp_path)

    changed, adapter_paths = gen.generate(tmp_path)

    assert adapter_paths == [".api-harness/skills/example/SKILL.md"]
    assert changed == [".api-harness/skills/example/SKILL.md", ".api-harness/skills/MANIFEST.json"]
    adapter_text = (tmp_path / ".api-harness" / "skills" / "example" / "SKILL.md").read_text(encoding="utf-8")
    assert "GTKB-API-SKILL-ADAPTER" in adapter_text
    assert "Canonical source: `.claude/skills/example/SKILL.md`" in adapter_text
    assert "Before applying this skill, read the canonical source file listed above." in adapter_text
    assert "UNIQUE_CANONICAL_BODY" not in adapter_text

    manifest = json.loads((tmp_path / ".api-harness" / "skills" / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["generated_by"] == "scripts/generate_api_skill_adapters.py"
    assert manifest["adapters"][0]["adapter_relative_path"] == ".api-harness/skills/example/SKILL.md"

    check_changed, _ = gen.generate(tmp_path, check=True)
    assert check_changed == []


def test_check_mode_reports_manual_adapter_drift(tmp_path: Path) -> None:
    write_registry(tmp_path)
    write_skill(tmp_path)
    gen.generate(tmp_path)
    adapter = tmp_path / ".api-harness" / "skills" / "example" / "SKILL.md"
    adapter.write_text(adapter.read_text(encoding="utf-8") + "\nmanual edit\n", encoding="utf-8")

    changed, _ = gen.generate(tmp_path, check=True)

    assert changed == [".api-harness/skills/example/SKILL.md"]


def test_frontmatter_validation_fails_closed(tmp_path: Path) -> None:
    write_registry(tmp_path)
    skill = tmp_path / ".claude" / "skills" / "example" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: example\n---\n", encoding="utf-8")

    with pytest.raises(gen.ApiSkillAdapterError, match="description"):
        gen.build_adapters(tmp_path)


def _assert_lf_clean_output(path: Path) -> None:
    data = path.read_bytes()
    assert b"\r" not in data, f"{path} contains CR bytes"
    for lineno, line in enumerate(data.decode("utf-8").splitlines(), start=1):
        if line != line.rstrip():
            pytest.fail(f"{path}:{lineno}: trailing whitespace")


def test_api_generated_output_is_lf_no_trailing_ws(tmp_path: Path) -> None:
    write_registry(tmp_path)
    write_skill(tmp_path)
    changed, _ = gen.generate(tmp_path)
    for rel_path in changed:
        _assert_lf_clean_output(tmp_path / rel_path)
