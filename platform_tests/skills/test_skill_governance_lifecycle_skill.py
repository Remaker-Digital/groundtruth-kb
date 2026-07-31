# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural and parity tests for the skill-governance-lifecycle skill.

Derived from WI-4839 (bridge thread
``gtkb-wi4839-skill-governance-lifecycle-scaffold``). The skill is a
repo-native procedure for managed-skill creation; per the approved proposal, the
testable surface is the canonical skill file, generated Codex adapter, manifest
entry, registry declaration, and target-path containment.

Linked specifications carried forward from the implementation proposal:

- ``GOV-FILE-BRIDGE-AUTHORITY-001`` - bridge protocol authority.
- ``DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`` - concrete spec
  linkage for implementation work.
- ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`` - spec-derived testing.
- ``GOV-HARNESS-ONBOARDING-CONTRACT-001`` - skill registry/adapter/catalog
  invariants.
- ``ADR-CROSS-HARNESS-PARITY-001`` and
  ``DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`` - harness surface parity.
"""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLAUDE_SKILL = _REPO_ROOT / ".claude" / "skills" / "skill-governance-lifecycle" / "SKILL.md"
_CODEX_ADAPTER = _REPO_ROOT / ".codex" / "skills" / "skill-governance-lifecycle" / "SKILL.md"
_REGISTRY = _REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"
_MANIFEST = _REPO_ROOT / ".codex" / "skills" / "MANIFEST.json"

_CAPABILITY_ID = "skill.skill-governance-lifecycle"
_GENERATED_MARKER = "<!-- GTKB-CODEX-SKILL-ADAPTER"
_GENERATED_END_MARKER = "GTKB-CODEX-SKILL-ADAPTER -->"

_REQUIRED_SECTIONS = (
    "## Authority and Scope",
    "## Required Inputs",
    "## Lifecycle Recipe",
    "## Canonical Skill Checklist",
    "## Registry and Adapter Checklist",
    "## Verification Checklist",
    "## Implementation Report Evidence",
    "## Non-Goals",
)

_REQUIRED_PHRASES = (
    "scripts/generate_codex_skill_adapters.py --update-registry",
    ".codex/skills/MANIFEST.json",
    "config/agent-control/harness-capability-registry.toml",
    "test_skill_catalog_contract.py",
    "no `SKILL.md`-bearing project skill is orphaned",
    "non-target harness disposition",
)

_TARGET_PATHS = (
    ".claude/skills/skill-governance-lifecycle/SKILL.md",
    ".codex/skills/skill-governance-lifecycle/SKILL.md",
    ".codex/skills/MANIFEST.json",
    "config/agent-control/harness-capability-registry.toml",
    "platform_tests/skills/test_skill_governance_lifecycle_skill.py",
)


def _split_frontmatter(text: str) -> tuple[str, str]:
    assert text.startswith("---"), "SKILL.md must open with YAML frontmatter"
    parts = text.split("---", 2)
    assert len(parts) == 3, "SKILL.md frontmatter must close with ---"
    return parts[1], parts[2]


def _frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    assert match, f"frontmatter is missing {key!r}"
    return match.group(1).strip()


def _strip_generated_block(text: str) -> str:
    start = text.find(_GENERATED_MARKER)
    if start == -1:
        return text
    end = text.find(_GENERATED_END_MARKER, start)
    if end == -1:
        return text
    return text[:start] + text[end + len(_GENERATED_END_MARKER) :].lstrip("\r\n")


def _canonical_normalized_sha(text: str) -> str:
    normalized = _strip_generated_block(text).rstrip() + "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _adapter_recorded_sha(text: str) -> str:
    match = re.search(r"^Canonical source sha256:\s*([0-9a-f]{64})\s*$", text, re.MULTILINE)
    assert match, "adapter generated block is missing Canonical source sha256"
    return match.group(1)


def _registry_capability() -> dict:
    data = tomllib.loads(_REGISTRY.read_text(encoding="utf-8"))
    for capability in data.get("capabilities", []):
        if capability.get("id") == _CAPABILITY_ID:
            return capability
    raise AssertionError(f"registry has no capability {_CAPABILITY_ID!r}")


def _manifest_adapter() -> dict:
    data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    for adapter in data.get("adapters", []):
        if adapter.get("capability_id") == _CAPABILITY_ID:
            return adapter
    raise AssertionError(f"manifest has no adapter for {_CAPABILITY_ID!r}")


def test_canonical_skill_file_exists_with_frontmatter() -> None:
    assert _CLAUDE_SKILL.is_file(), f"missing skill file: {_CLAUDE_SKILL}"
    frontmatter, body = _split_frontmatter(_CLAUDE_SKILL.read_text(encoding="utf-8"))
    assert _frontmatter_value(frontmatter, "name") == "skill-governance-lifecycle"
    description = _frontmatter_value(frontmatter, "description")
    assert "managed-skill creation" in description
    assert body.strip(), "skill body must not be empty"


def test_canonical_skill_declares_lifecycle_contract() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in body, f"skill body is missing section {section!r}"
    for phrase in _REQUIRED_PHRASES:
        assert phrase in body, f"skill body is missing required phrase {phrase!r}"


def test_registry_entry_present_and_scoped() -> None:
    capability = _registry_capability()
    assert capability["kind"] == "skill"
    assert capability["canonical_name"] == "skill-governance-lifecycle"
    assert capability["canonical_source"] == ".claude/skills/skill-governance-lifecycle/SKILL.md"
    assert capability["required_for_roles"] == ["prime-builder"]
    assert capability["claude"]["surface"] == ".claude/skills/skill-governance-lifecycle/SKILL.md"
    assert capability["claude"]["status"] == "native"
    assert capability["codex"]["surface"] == ".codex/skills/skill-governance-lifecycle/SKILL.md"
    assert capability["codex"]["status"] == "adapter"
    assert capability["codex"]["adapter_source"] == ".claude/skills/skill-governance-lifecycle/SKILL.md"
    assert capability["antigravity"]["status"] == "unsupported"
    assert capability["cursor"]["status"] == "unsupported"


def test_codex_adapter_and_manifest_match_canonical_sha() -> None:
    assert _CODEX_ADAPTER.is_file(), f"missing Codex adapter: {_CODEX_ADAPTER}"
    canonical = _CLAUDE_SKILL.read_text(encoding="utf-8")
    adapter = _CODEX_ADAPTER.read_text(encoding="utf-8")
    expected = _canonical_normalized_sha(canonical)
    assert _GENERATED_MARKER in adapter
    assert _GENERATED_END_MARKER in adapter
    assert "Canonical source: .claude/skills/skill-governance-lifecycle/SKILL.md" in adapter
    assert _adapter_recorded_sha(adapter) == expected

    manifest = _manifest_adapter()
    assert manifest["canonical_name"] == "skill-governance-lifecycle"
    assert manifest["source_relative_path"] == ".claude/skills/skill-governance-lifecycle/SKILL.md"
    assert manifest["adapter_relative_path"] == ".codex/skills/skill-governance-lifecycle/SKILL.md"
    assert manifest["source_sha256"] == expected
    assert _registry_capability()["codex"]["source_sha256"] == expected


def test_target_paths_all_within_gtkb_root() -> None:
    for relative in _TARGET_PATHS:
        resolved = (_REPO_ROOT / relative).resolve()
        assert _REPO_ROOT in resolved.parents or resolved == _REPO_ROOT
        assert "applications" not in Path(relative).parts
