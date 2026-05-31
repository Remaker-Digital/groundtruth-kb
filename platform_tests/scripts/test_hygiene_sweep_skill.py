"""Tests for the gtkb-hygiene-sweep skill.

Verifies WI-3421 implementation per bridge/gtkb-hygiene-sweep-skill-004.md (GO):
canonical SKILL.md frontmatter and body shape, registry entry presence and
adapter-sha256 contract, harness-parity invariants, and the lifecycle-trigger
DCL citation requirement that REVISED-2 F1 added.
"""

from __future__ import annotations

import hashlib
import re
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CANONICAL_SKILL = PROJECT_ROOT / ".claude" / "skills" / "gtkb-hygiene-sweep" / "SKILL.md"
CODEX_SKILL = PROJECT_ROOT / ".codex" / "skills" / "gtkb-hygiene-sweep" / "SKILL.md"
REGISTRY = PROJECT_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"

CAPABILITY_ID = "skill.gtkb-hygiene-sweep"
SKILL_NAME = "gtkb-hygiene-sweep"

GENERATED_MARKER = "<!-- GTKB-CODEX-SKILL-ADAPTER"
GENERATED_END_MARKER = "GTKB-CODEX-SKILL-ADAPTER -->"


def _load_capability() -> dict | None:
    registry = tomllib.loads(REGISTRY.read_text(encoding="utf-8"))
    for cap in registry.get("capabilities", []):
        if cap.get("id") == CAPABILITY_ID:
            return cap
    return None


def _strip_generated_block(text: str) -> str:
    """Mirror scripts/generate_codex_skill_adapters.py:_strip_generated_block."""
    start = text.find(GENERATED_MARKER)
    if start == -1:
        return text
    end = text.find(GENERATED_END_MARKER, start)
    if end == -1:
        return text
    return text[:start] + text[end + len(GENERATED_END_MARKER) :].lstrip("\r\n")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_skill_frontmatter_valid_yaml() -> None:
    text = CANONICAL_SKILL.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0].strip() == "---", "SKILL.md must start with YAML frontmatter delimiter"

    closing_index = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = i
            break
    assert closing_index is not None, "SKILL.md frontmatter must close with ---"

    frontmatter = "\n".join(lines[1:closing_index])
    assert re.search(r"^name:", frontmatter, re.MULTILINE), "frontmatter must declare 'name:'"
    assert re.search(r"^description:", frontmatter, re.MULTILINE), "frontmatter must declare 'description:'"


def test_skill_name_matches_directory() -> None:
    text = CANONICAL_SKILL.read_text(encoding="utf-8")
    match = re.search(r"^name:\s*(\S+)", text, re.MULTILINE)
    assert match is not None, "frontmatter must have 'name:' line"
    assert match.group(1) == SKILL_NAME, f"frontmatter name must be '{SKILL_NAME}'"


def test_registry_entry_exists() -> None:
    cap = _load_capability()
    assert cap is not None, f"registry must contain capability '{CAPABILITY_ID}'"
    assert cap.get("kind") == "skill"
    assert cap.get("canonical_name") == SKILL_NAME
    assert cap.get("parity_class") == "baseline"


def test_registry_canonical_source_path_exists() -> None:
    cap = _load_capability()
    assert cap is not None
    canonical_source = cap.get("canonical_source")
    assert canonical_source, "registry entry must declare canonical_source"
    path = PROJECT_ROOT / canonical_source
    assert path.is_file(), f"canonical_source must resolve to existing file: {path}"


def test_codex_adapter_generated() -> None:
    assert CODEX_SKILL.is_file(), "Codex adapter SKILL.md must exist"
    text = CODEX_SKILL.read_text(encoding="utf-8")
    assert GENERATED_MARKER in text, "Codex adapter must carry GTKB-CODEX-SKILL-ADAPTER marker"
    assert "Canonical source: .claude/skills/gtkb-hygiene-sweep/SKILL.md" in text


def test_codex_adapter_sha256_matches_canonical() -> None:
    cap = _load_capability()
    assert cap is not None
    codex_block = cap.get("codex")
    assert codex_block is not None, "registry must have [capabilities.codex] block"
    declared_sha = codex_block.get("source_sha256")
    assert declared_sha, "Codex block must declare source_sha256"

    canonical_text = CANONICAL_SKILL.read_text(encoding="utf-8")
    expected_sha = _sha256_text(_strip_generated_block(canonical_text).rstrip() + "\n")
    assert declared_sha == expected_sha, (
        f"Registry source_sha256 must match canonical normalized-body sha256 "
        f"(declared {declared_sha[:16]}...; expected {expected_sha[:16]}...)"
    )


def test_registry_required_for_roles_includes_prime_builder() -> None:
    cap = _load_capability()
    assert cap is not None
    roles = cap.get("required_for_roles", [])
    assert "prime-builder" in roles, "required_for_roles must include 'prime-builder'"


def test_skill_directory_layout_matches_precedent() -> None:
    skill_dir = PROJECT_ROOT / ".claude" / "skills" / "gtkb-hygiene-sweep"
    assert skill_dir.is_dir(), "skill directory must exist under .claude/skills/"
    assert (skill_dir / "SKILL.md").is_file(), "skill directory must contain SKILL.md"

    precedent_dirs = [
        PROJECT_ROOT / ".claude" / "skills" / "bridge",
        PROJECT_ROOT / ".claude" / "skills" / "assertion-triage",
    ]
    for precedent in precedent_dirs:
        assert (precedent / "SKILL.md").is_file(), f"precedent skill directory must exist: {precedent}"


def test_skill_body_cites_lifecycle_trigger_dcl() -> None:
    """REVISED-2 F1: SKILL.md body must cite the DCL and the workflow phrase."""
    text = CANONICAL_SKILL.read_text(encoding="utf-8")
    assert "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001" in text, (
        "SKILL.md body must cite DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (per REVISED-2 F1)"
    )
    assert "lifecycle trigger" in text, (
        "SKILL.md body must contain 'lifecycle trigger' workflow language (per REVISED-2 F1)"
    )
