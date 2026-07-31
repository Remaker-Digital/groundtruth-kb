# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural and parity tests for the managed-skill-adoption-review skill.

Derived from WI-4841 (bridge thread
``gtkb-wi4841-managed-skill-adoption-review-scaffold``). The skill provides a
deterministic structural review checklist for managed-artifact (skill, template,
adopter) proposals; it is review evidence, not a bridge verdict.

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
_CLAUDE_SKILL = _REPO_ROOT / ".claude" / "skills" / "managed-skill-adoption-review" / "SKILL.md"
_CODEX_ADAPTER = _REPO_ROOT / ".codex" / "skills" / "managed-skill-adoption-review" / "SKILL.md"
_ANTIGRAVITY_ADAPTER = _REPO_ROOT / ".agent" / "skills" / "managed-skill-adoption-review" / "SKILL.md"
_REGISTRY = _REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"
_MANIFEST = _REPO_ROOT / ".codex" / "skills" / "MANIFEST.json"
_ANTIGRAVITY_MANIFEST = _REPO_ROOT / ".agent" / "skills" / "MANIFEST.json"

_CAPABILITY_ID = "skill.managed-skill-adoption-review"
_SOURCE_SHA256 = "b9c8a7e0f81a893ef98de6b7e28b9b9057d5bb79a3d8b4025d70b1a8998614e9"
_GENERATED_MARKER = "<!-- GTKB-CODEX-SKILL-ADAPTER"
_ANTIGRAVITY_GENERATED_MARKER = "<!-- GTKB-ANTIGRAVITY-SKILL-ADAPTER"
_GENERATED_END_MARKER = "GTKB-CODEX-SKILL-ADAPTER -->"

_REQUIRED_SECTIONS = (
    "## When To Use",
    "## When Not To Use",
    "## Required Context",
    "## Structural Review Checklist",
    "### 1. Registry Authority",
    "### 2. Target-Path Completeness",
    "### 3. Stale-Assumption Detection",
    "### 4. Specification Linkage",
    "### 5. Lifecycle Compliance",
    "### 6. Artifact Quality",
    "## Output",
    "## Artifact Routing",
)

_REQUIRED_PHRASES = (
    "managed-artifact registry",
    "stale Tier A registry",
    "Registry Authority Assessment",
    "Target-Path Completeness Assessment",
    "OWNER-DECISION-NEEDED",
    "advisory evidence for the bridge verdict",
)

_TARGET_PATHS = (
    ".claude/skills/managed-skill-adoption-review/SKILL.md",
    ".codex/skills/managed-skill-adoption-review/SKILL.md",
    ".codex/skills/MANIFEST.json",
    ".agent/skills/managed-skill-adoption-review/SKILL.md",
    ".agent/skills/MANIFEST.json",
    "config/agent-control/harness-capability-registry.toml",
    "platform_tests/skills/test_managed_skill_adoption_review_skill.py",
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


def _manifest_adapter(manifest_path: Path) -> dict:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    for adapter in data.get("adapters", []):
        if adapter.get("capability_id") == _CAPABILITY_ID:
            return adapter
    raise AssertionError(f"{manifest_path} has no adapter for {_CAPABILITY_ID!r}")


def test_canonical_skill_file_exists_with_frontmatter() -> None:
    assert _CLAUDE_SKILL.is_file(), f"missing skill file: {_CLAUDE_SKILL}"
    frontmatter, body = _split_frontmatter(_CLAUDE_SKILL.read_text(encoding="utf-8"))
    assert _frontmatter_value(frontmatter, "name") == "managed-skill-adoption-review"
    description = _frontmatter_value(frontmatter, "description")
    assert "Structural review of managed-artifact proposals" in description
    assert body.strip(), "skill body must not be empty"


def test_canonical_skill_declares_review_checklist() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in body, f"skill body is missing section {section!r}"
    for phrase in _REQUIRED_PHRASES:
        assert phrase in body, f"skill body is missing required phrase {phrase!r}"


def test_registry_entry_present_and_scoped() -> None:
    capability = _registry_capability()
    assert capability["kind"] == "skill"
    assert capability["canonical_name"] == "managed-skill-adoption-review"
    assert capability["canonical_source"] == ".claude/skills/managed-skill-adoption-review/SKILL.md"
    assert capability["required_for_roles"] == ["prime-builder", "loyal-opposition"]
    assert capability["claude"]["surface"] == ".claude/skills/managed-skill-adoption-review/SKILL.md"
    assert capability["claude"]["status"] == "native"
    assert capability["codex"]["surface"] == ".codex/skills/managed-skill-adoption-review/SKILL.md"
    assert capability["codex"]["status"] == "adapter"
    assert capability["codex"]["adapter_source"] == ".claude/skills/managed-skill-adoption-review/SKILL.md"
    assert capability["codex"]["source_sha256"] == _SOURCE_SHA256
    assert capability["antigravity"]["surface"] == ".agent/skills/managed-skill-adoption-review/SKILL.md"
    assert capability["antigravity"]["status"] == "adapter"
    assert capability["antigravity"]["adapter_source"] == ".claude/skills/managed-skill-adoption-review/SKILL.md"
    assert capability["antigravity"]["source_sha256"] == _SOURCE_SHA256
    for harness in ("cursor", "ollama", "openrouter"):
        assert capability[harness]["status"] == "unsupported"
        assert capability[harness]["reason"]


def test_codex_adapter_exists_and_matches_canonical_normalized_sha() -> None:
    assert _CODEX_ADAPTER.is_file(), f"missing Codex adapter: {_CODEX_ADAPTER}"
    adapter_text = _CODEX_ADAPTER.read_text(encoding="utf-8")
    assert _GENERATED_MARKER in adapter_text, "Codex adapter is missing generated marker"
    recorded_sha = _adapter_recorded_sha(adapter_text)
    canonical_text = _CLAUDE_SKILL.read_text(encoding="utf-8")
    computed_sha = _canonical_normalized_sha(canonical_text)
    assert recorded_sha == computed_sha, f"adapter SHA ({recorded_sha}) != canonical normalized SHA ({computed_sha})"
    assert recorded_sha == _SOURCE_SHA256, f"adapter SHA ({recorded_sha}) != pinned SHA ({_SOURCE_SHA256})"


def test_manifest_has_adapter_entry() -> None:
    adapter = _manifest_adapter(_MANIFEST)
    assert adapter["adapter_relative_path"] == ".codex/skills/managed-skill-adoption-review/SKILL.md"
    assert adapter["canonical_name"] == "managed-skill-adoption-review"
    assert adapter["capability_id"] == _CAPABILITY_ID
    assert adapter["source_relative_path"] == ".claude/skills/managed-skill-adoption-review/SKILL.md"
    assert adapter["source_sha256"] == _SOURCE_SHA256


def test_antigravity_adapter_and_manifest_entry_exist() -> None:
    assert _ANTIGRAVITY_ADAPTER.is_file(), f"missing Antigravity adapter: {_ANTIGRAVITY_ADAPTER}"
    adapter_text = _ANTIGRAVITY_ADAPTER.read_text(encoding="utf-8")
    assert _ANTIGRAVITY_GENERATED_MARKER in adapter_text, "Antigravity adapter is missing generated marker"
    recorded_sha = _adapter_recorded_sha(adapter_text)
    canonical_text = _CLAUDE_SKILL.read_text(encoding="utf-8")
    computed_sha = _canonical_normalized_sha(canonical_text)
    assert recorded_sha == computed_sha, f"adapter SHA ({recorded_sha}) != canonical normalized SHA ({computed_sha})"
    assert recorded_sha == _SOURCE_SHA256, f"adapter SHA ({recorded_sha}) != pinned SHA ({_SOURCE_SHA256})"

    adapter = _manifest_adapter(_ANTIGRAVITY_MANIFEST)
    assert adapter["adapter_relative_path"] == ".agent/skills/managed-skill-adoption-review/SKILL.md"
    assert adapter["canonical_name"] == "managed-skill-adoption-review"
    assert adapter["capability_id"] == _CAPABILITY_ID
    assert adapter["source_relative_path"] == ".claude/skills/managed-skill-adoption-review/SKILL.md"
    assert adapter["source_sha256"] == _SOURCE_SHA256


def test_target_paths_are_inside_project_root() -> None:
    for path in _TARGET_PATHS:
        resolved = (_REPO_ROOT / path).resolve()
        assert str(resolved).startswith(str(_REPO_ROOT.resolve())), (
            f"target path {path!r} resolves outside project root"
        )


def test_no_target_path_is_orphaned() -> None:
    missing = [path for path in _TARGET_PATHS if not (_REPO_ROOT / path).exists()]
    assert not missing, f"target paths do not exist: {missing}"
