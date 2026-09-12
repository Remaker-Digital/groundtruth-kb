# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural and parity tests for the advisory-disposition skill.

Derived from WI-4840 (bridge thread
``gtkb-wi4840-advisory-disposition-skill-scaffold``). The skill converts Loyal
Opposition advisory findings into the correct governed next artifact path while
keeping advisory capture separate from implementation approval.

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
_CLAUDE_SKILL = _REPO_ROOT / ".claude" / "skills" / "advisory-disposition" / "SKILL.md"
_CODEX_ADAPTER = _REPO_ROOT / ".codex" / "skills" / "advisory-disposition" / "SKILL.md"
_REGISTRY = _REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"
_MANIFEST = _REPO_ROOT / ".codex" / "skills" / "MANIFEST.json"

_CAPABILITY_ID = "skill.advisory-disposition"
_GENERATED_MARKER = "<!-- GTKB-CODEX-SKILL-ADAPTER"
_GENERATED_END_MARKER = "GTKB-CODEX-SKILL-ADAPTER -->"

_REQUIRED_SECTIONS = (
    "## When To Use",
    "## When Not To Use",
    "## Required Inputs",
    "## Advisory Disposition Decision Tree",
    "## Artifact Routing Rules",
    "## Mandatory Steps",
    "## Verification Evidence",
    "## Cross-Harness Disposition",
    "## Non-Goals",
)

_REQUIRED_ROUTES = (
    "**No-op**",
    "**Work item**",
    "**Specification intake**",
    "**Project authorization**",
    "**Bridge proposal**",
    "**Deferred candidate**",
)

_REQUIRED_PHRASES = (
    "bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-004.md",
    "Only a live bridge",
    "implementation-start packet",
    "Search existing deliberations, backlog items, specifications, and bridge",
    "AskUserQuestion",
    "clear/resume condition",
)

_TARGET_PATHS = (
    ".claude/skills/advisory-disposition/SKILL.md",
    ".codex/skills/advisory-disposition/SKILL.md",
    ".codex/skills/MANIFEST.json",
    "config/agent-control/harness-capability-registry.toml",
    "platform_tests/skills/test_advisory_disposition_skill.py",
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
    assert _frontmatter_value(frontmatter, "name") == "advisory-disposition"
    description = _frontmatter_value(frontmatter, "description")
    assert "Loyal Opposition advisory findings" in description
    assert "implementation approval" in description
    assert body.strip(), "skill body must not be empty"


def test_canonical_skill_declares_disposition_contract() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in body, f"skill body is missing section {section!r}"
    for route in _REQUIRED_ROUTES:
        assert route in body, f"skill body is missing route {route!r}"
    for phrase in _REQUIRED_PHRASES:
        assert phrase in body, f"skill body is missing required phrase {phrase!r}"


def test_codex_adapter_and_manifest_match_canonical_sha() -> None:
    assert _CODEX_ADAPTER.is_file(), f"missing Codex adapter: {_CODEX_ADAPTER}"
    canonical = _CLAUDE_SKILL.read_text(encoding="utf-8")
    adapter = _CODEX_ADAPTER.read_text(encoding="utf-8")
    expected = _canonical_normalized_sha(canonical)
    assert _GENERATED_MARKER in adapter
    assert _GENERATED_END_MARKER in adapter
    assert "Canonical source: .claude/skills/advisory-disposition/SKILL.md" in adapter
    assert _adapter_recorded_sha(adapter) == expected

    manifest = _manifest_adapter()
    assert manifest["canonical_name"] == "advisory-disposition"
    assert manifest["source_relative_path"] == ".claude/skills/advisory-disposition/SKILL.md"
    assert manifest["adapter_relative_path"] == ".codex/skills/advisory-disposition/SKILL.md"
    assert manifest["source_sha256"] == expected
    assert _registry_capability()["codex"]["source_sha256"] == expected


def test_target_paths_all_within_gtkb_root() -> None:
    for relative in _TARGET_PATHS:
        resolved = (_REPO_ROOT / relative).resolve()
        assert _REPO_ROOT in resolved.parents or resolved == _REPO_ROOT
        assert "applications" not in Path(relative).parts
