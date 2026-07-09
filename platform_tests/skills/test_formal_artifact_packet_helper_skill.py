# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural and parity tests for the formal-artifact-packet-helper skill.

Derived from WI-4842 (bridge thread
``gtkb-wi4842-formal-artifact-packet-helper-scaffold``). The skill wraps the
existing formal-artifact packet validation authority without duplicating or
replacing the canonical gate schema.

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
import importlib.util
import json
import re
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLAUDE_SKILL = _REPO_ROOT / ".claude" / "skills" / "formal-artifact-packet-helper" / "SKILL.md"
_CODEX_ADAPTER = _REPO_ROOT / ".codex" / "skills" / "formal-artifact-packet-helper" / "SKILL.md"
_REGISTRY = _REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"
_MANIFEST = _REPO_ROOT / ".codex" / "skills" / "MANIFEST.json"
_FORMAL_ARTIFACT_GATE = _REPO_ROOT / ".claude" / "hooks" / "formal-artifact-approval-gate.py"

_CAPABILITY_ID = "skill.formal-artifact-packet-helper"
_SOURCE_SHA256 = "824af14f6ace58e6a3b3423b55ad1119d6874cb2ac2ff83e5c37734903ac3855"
_GENERATED_MARKER = "<!-- GTKB-CODEX-SKILL-ADAPTER"
_GENERATED_END_MARKER = "GTKB-CODEX-SKILL-ADAPTER -->"

_REQUIRED_SECTIONS = (
    "## Authority and Scope",
    "## When To Use",
    "## When Not To Use",
    "## Required Inputs",
    "## Mandatory Steps",
    "### Packet Generation",
    "### Packet Validation",
    "## Cross-Harness Notes",
    "## Verification Checklist",
)

_REQUIRED_PHRASES = (
    "formal-artifact-approval-gate.py",
    "scripts/validate_formal_artifact_packet.py",
    "LF-only line endings",
    "REQUIRED_PACKET_FIELDS",
    "VALID_ARTIFACT_TYPES",
    "VALID_APPROVAL_MODES",
    ".groundtruth/formal-artifact-approvals/",
)

_TARGET_PATHS = (
    ".claude/skills/formal-artifact-packet-helper/SKILL.md",
    ".codex/skills/formal-artifact-packet-helper/SKILL.md",
    ".codex/skills/MANIFEST.json",
    "config/agent-control/harness-capability-registry.toml",
    "platform_tests/skills/test_formal_artifact_packet_helper_skill.py",
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


def _load_formal_artifact_gate() -> object:
    spec = importlib.util.spec_from_file_location("formal_artifact_approval_gate", _FORMAL_ARTIFACT_GATE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_canonical_skill_file_exists_with_frontmatter() -> None:
    assert _CLAUDE_SKILL.is_file(), f"missing skill file: {_CLAUDE_SKILL}"
    frontmatter, body = _split_frontmatter(_CLAUDE_SKILL.read_text(encoding="utf-8"))
    assert _frontmatter_value(frontmatter, "name") == "formal-artifact-packet-helper"
    description = _frontmatter_value(frontmatter, "description")
    assert "formal-artifact approval packets" in description
    assert "LF normalization" in description
    assert body.strip(), "skill body must not be empty"


def test_canonical_skill_declares_packet_contract() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in body, f"skill body is missing section {section!r}"
    for phrase in _REQUIRED_PHRASES:
        assert phrase in body, f"skill body is missing required phrase {phrase!r}"


def test_canonical_skill_enumerates_live_gate_constants() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    gate = _load_formal_artifact_gate()
    for field in sorted(gate.REQUIRED_PACKET_FIELDS):
        assert f"`{field}`" in body
    for artifact_type in sorted(gate.VALID_ARTIFACT_TYPES):
        assert f"`{artifact_type}`" in body
    for approval_mode in sorted(gate.VALID_APPROVAL_MODES):
        assert f"`{approval_mode}`" in body


def test_registry_entry_present_and_scoped() -> None:
    capability = _registry_capability()
    assert capability["kind"] == "skill"
    assert capability["canonical_name"] == "formal-artifact-packet-helper"
    assert capability["canonical_source"] == ".claude/skills/formal-artifact-packet-helper/SKILL.md"
    assert capability["required_for_roles"] == ["prime-builder", "loyal-opposition"]
    assert capability["claude"]["surface"] == ".claude/skills/formal-artifact-packet-helper/SKILL.md"
    assert capability["claude"]["status"] == "native"
    assert capability["codex"]["surface"] == ".codex/skills/formal-artifact-packet-helper/SKILL.md"
    assert capability["codex"]["status"] == "adapter"
    assert capability["codex"]["adapter_source"] == ".claude/skills/formal-artifact-packet-helper/SKILL.md"
    assert capability["codex"]["source_sha256"] == _SOURCE_SHA256
    for harness in ("antigravity", "cursor", "ollama", "openrouter"):
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


def test_manifest_has_adapter_entry() -> None:
    adapter = _manifest_adapter()
    assert adapter["adapter_relative_path"] == ".codex/skills/formal-artifact-packet-helper/SKILL.md"
    assert adapter["canonical_name"] == "formal-artifact-packet-helper"
    assert adapter["capability_id"] == _CAPABILITY_ID
    assert adapter["source_relative_path"] == ".claude/skills/formal-artifact-packet-helper/SKILL.md"
    assert adapter["source_sha256"] == _SOURCE_SHA256


def test_target_paths_are_inside_project_root() -> None:
    for path in _TARGET_PATHS:
        resolved = (_REPO_ROOT / path).resolve()
        assert str(resolved).startswith(str(_REPO_ROOT.resolve())), (
            f"target path {path!r} resolves outside project root"
        )


def test_no_target_path_is_orphaned() -> None:
    existing = set()
    missing = []
    for path in _TARGET_PATHS:
        target = _REPO_ROOT / path
        if target.exists():
            existing.add(path)
        else:
            missing.append(path)
    assert not missing, f"target paths do not exist: {missing}"
    assert len(existing) == len(_TARGET_PATHS), f"expected {len(_TARGET_PATHS)} target paths, found {len(existing)}"
