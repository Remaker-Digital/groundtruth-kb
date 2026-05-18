# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural and parity tests for the /verify verdict-author skill.

Derived from WI-3261 Slice 1 (bridge thread
``gtkb-verify-verdict-author-skill-slice-1``). The verdict-authoring procedure
is an LLM procedure; per GOV-19 the testable surface is the skill file, its
Codex parity adapter, and the harness-capability registry entry — these tests
verify those artifacts declare the structural conventions the proposal
requires.

Linked specifications (carried forward from
``bridge/gtkb-verify-verdict-author-skill-slice-1-001.md`` Specification Links
and the ``-002`` GO verdict):

- ``GOV-FILE-BRIDGE-AUTHORITY-001`` — bridge protocol authority.
- ``DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`` — spec linkage.
- ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`` — spec-to-test mapping.
- ``GOV-STANDING-BACKLOG-001`` — implements MemBase backlog item WI-3261.
- ``ADR-ISOLATION-APPLICATION-PLACEMENT-001`` — in-root, non-``applications/``.
- ``ADR-CODEX-HOOK-PARITY-FALLBACK-001`` — generated Codex adapter parity.
- ``ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`` — the skill is itself an artifact.
- ``GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`` — manifest/registry registration.
- ``DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`` — the When-to-invoke lifecycle trigger.
- ``GOV-ARTIFACT-APPROVAL-001`` — no protected narrative artifact mutated.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLAUDE_SKILL = _REPO_ROOT / ".claude" / "skills" / "verify" / "SKILL.md"
_CODEX_ADAPTER = _REPO_ROOT / ".codex" / "skills" / "verify" / "SKILL.md"
_REGISTRY = _REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"
_MANIFEST = _REPO_ROOT / ".codex" / "skills" / "MANIFEST.json"

_CAPABILITY_ID = "skill.verify"

# Generated-block markers — must match scripts/generate_codex_skill_adapters.py.
_GENERATED_MARKER = "<!-- GTKB-CODEX-SKILL-ADAPTER"
_GENERATED_END_MARKER = "GTKB-CODEX-SKILL-ADAPTER -->"

# Required H2 sections in the canonical skill body (IP-1 structural conventions).
_REQUIRED_SECTIONS = (
    "## Non-bypass guarantees",
    "## When to invoke",
    "## Mandatory pre-write steps",
    "## Verdict file template",
    "## Gate enforcement",
    "## Cross-harness implementation notes",
    "## Companion skills",
)

# The four mandated columns of the spec-to-test mapping table.
_SPEC_TO_TEST_COLUMNS = (
    "Specification",
    "Test or Verification Command",
    "Executed",
    "Result",
)

# Declared target paths for the slice (test-fixture mirror of the proposal).
_TARGET_PATHS = (
    ".claude/skills/verify/SKILL.md",
    ".codex/skills/verify/SKILL.md",
    ".codex/skills/MANIFEST.json",
    "config/agent-control/harness-capability-registry.toml",
    "platform_tests/skills/test_verify_skill_scaffolding.py",
)


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Return ``(frontmatter, body)`` for a SKILL.md file."""
    assert text.startswith("---"), "SKILL.md must open with a YAML frontmatter block"
    parts = text.split("---", 2)
    assert len(parts) == 3, "SKILL.md frontmatter block must be closed with ---"
    return parts[1], parts[2]


def _frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    assert match, f"frontmatter is missing '{key}'"
    return match.group(1).strip()


def _strip_generated_block(text: str) -> str:
    """Mirror generate_codex_skill_adapters.py::_strip_generated_block."""
    start = text.find(_GENERATED_MARKER)
    if start == -1:
        return text
    end = text.find(_GENERATED_END_MARKER, start)
    if end == -1:
        return text
    return text[:start] + text[end + len(_GENERATED_END_MARKER) :].lstrip("\r\n")


def _adapter_recorded_sha(text: str) -> str:
    """Return the canonical-source SHA recorded in an adapter's generated block."""
    match = re.search(r"^Canonical source sha256:\s*([0-9a-f]{64})\s*$", text, re.MULTILINE)
    assert match, "adapter generated block is missing the 'Canonical source sha256:' line"
    return match.group(1)


def _canonical_normalized_sha(text: str) -> str:
    """Return sha256 of the canonical normalized body, matching the generator."""
    import hashlib

    normalized = _strip_generated_block(text).rstrip() + "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _registry_capability(cap_id: str) -> dict:
    data = tomllib.loads(_REGISTRY.read_text(encoding="utf-8"))
    for cap in data.get("capabilities", []):
        if cap.get("id") == cap_id:
            return cap
    raise AssertionError(f"registry has no capability '{cap_id}'")


def _manifest_adapter(capability_id: str) -> dict:
    data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    for adapter in data.get("adapters", []):
        if adapter.get("capability_id") == capability_id:
            return adapter
    raise AssertionError(f"manifest has no adapter for '{capability_id}'")


def test_canonical_skill_file_exists() -> None:
    """Test #1 — canonical skill file exists and is in-root."""
    assert _CLAUDE_SKILL.is_file(), f"missing skill file: {_CLAUDE_SKILL}"
    assert _REPO_ROOT in _CLAUDE_SKILL.resolve().parents, "skill must be in-root"
    assert "applications" not in _CLAUDE_SKILL.relative_to(_REPO_ROOT).parts


def test_canonical_skill_frontmatter_present() -> None:
    """Test #2 — YAML frontmatter parses; name + non-empty description."""
    frontmatter, body = _split_frontmatter(_CLAUDE_SKILL.read_text(encoding="utf-8"))
    assert _frontmatter_value(frontmatter, "name") == "gtkb-verify"
    assert _frontmatter_value(frontmatter, "description"), "description must not be empty"
    assert body.strip(), "skill body must not be empty"


def test_canonical_skill_required_sections() -> None:
    """Test #3 — body contains all required H2 sections."""
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in body, f"skill body is missing section '{section}'"


def test_verdict_template_includes_spec_to_test_table() -> None:
    """Test #4 — verdict template documents the spec-to-test table columns."""
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    assert "## Spec-to-Test Mapping" in body, "verdict template missing Spec-to-Test Mapping"
    for column in _SPEC_TO_TEST_COLUMNS:
        assert column in body, f"spec-to-test table missing column '{column}'"


def test_verdict_template_includes_applicability_preflight_section() -> None:
    """Test #5 — verdict template documents the Applicability Preflight section."""
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    assert "## Applicability Preflight" in body, "verdict template missing Applicability Preflight"
    assert "verbatim" in body, "Applicability Preflight section must document verbatim-output convention"


def test_verdict_template_includes_clause_applicability_section() -> None:
    """Test #6 — verdict template documents Clause Applicability + Blocking Gaps."""
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    assert "## Clause Applicability" in body, "verdict template missing Clause Applicability"
    assert "Blocking Gaps" in body, "verdict template must document the Blocking Gaps subsection"


def test_skill_documents_no_index_mutation() -> None:
    """Test #7 — body explicitly states the skill does NOT mutate bridge/INDEX.md."""
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    assert "bridge/INDEX.md" in body, "skill must reference bridge/INDEX.md"
    pattern = re.compile(r"(does\s+\*?\*?NOT\*?\*?|not).{0,80}bridge/INDEX\.md", re.IGNORECASE | re.DOTALL)
    assert pattern.search(body), "skill body must state it does NOT mutate bridge/INDEX.md"


def test_skill_documents_preflight_invocations() -> None:
    """Test #8 — body cites the exact preflight script invocations."""
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    assert "scripts/bridge_applicability_preflight.py" in body, "missing applicability preflight invocation"
    assert "scripts/adr_dcl_clause_preflight.py" in body, "missing clause preflight invocation"


def test_codex_adapter_file_exists() -> None:
    """Test #9 — Codex adapter file exists."""
    assert _CODEX_ADAPTER.is_file(), f"missing Codex adapter: {_CODEX_ADAPTER}"


def test_codex_adapter_body_matches_canonical_normalized_sha() -> None:
    """Test #10 — adapter records the canonical normalized-body SHA.

    Per the ``_strip_generated_block`` contract in
    ``scripts/generate_codex_skill_adapters.py``, the canonical normalized-body
    SHA — ``sha256(_strip_generated_block(text).rstrip() + "\\n")`` — is the
    value the generator stamps into the adapter's generated block, the
    ``.codex/skills/MANIFEST.json`` adapter entry, and the registry
    ``[capabilities.codex] source_sha256`` field. This test asserts those three
    recordings agree with the canonical, which is the parity contract the
    generator maintains.
    """
    canonical = _CLAUDE_SKILL.read_text(encoding="utf-8")
    adapter = _CODEX_ADAPTER.read_text(encoding="utf-8")
    expected = _canonical_normalized_sha(canonical)
    assert _adapter_recorded_sha(adapter) == expected, (
        "adapter generated block must record the canonical normalized-body SHA"
    )
    assert _manifest_adapter(_CAPABILITY_ID)["source_sha256"] == expected, (
        "MANIFEST.json adapter SHA must equal the canonical normalized-body SHA"
    )
    assert _registry_capability(_CAPABILITY_ID)["codex"]["source_sha256"] == expected, (
        "registry codex source_sha256 must equal the canonical normalized-body SHA"
    )


def test_codex_adapter_has_generated_marker() -> None:
    """Test #11 — adapter carries the GTKB-CODEX-SKILL-ADAPTER marker."""
    adapter = _CODEX_ADAPTER.read_text(encoding="utf-8")
    assert _GENERATED_MARKER in adapter, "adapter missing GTKB-CODEX-SKILL-ADAPTER marker"
    assert _GENERATED_END_MARKER in adapter, "adapter missing GTKB-CODEX-SKILL-ADAPTER end marker"


def test_manifest_entry_present() -> None:
    """Test #12 — MANIFEST.json includes the gtkb-verify adapter with stored SHA."""
    adapter = _manifest_adapter(_CAPABILITY_ID)
    assert adapter["canonical_name"] == "gtkb-verify"
    assert adapter["source_relative_path"] == ".claude/skills/verify/SKILL.md"
    assert adapter["adapter_relative_path"] == ".codex/skills/verify/SKILL.md"
    assert re.fullmatch(r"[0-9a-f]{64}", adapter["source_sha256"]), "stored SHA must be a 64-hex digest"
    # The manifest SHA is the normalized-body SHA of the canonical skill.
    expected = _canonical_normalized_sha(_CLAUDE_SKILL.read_text(encoding="utf-8"))
    assert adapter["source_sha256"] == expected, "manifest SHA must equal the canonical normalized-body SHA"


def test_registry_entry_present() -> None:
    """Test #13 — registry has a skill.verify capability for loyal-opposition."""
    cap = _registry_capability(_CAPABILITY_ID)
    assert cap["kind"] == "skill"
    assert cap["canonical_name"] == "gtkb-verify"
    assert "loyal-opposition" in cap["required_for_roles"], "skill must be required for loyal-opposition"
    assert cap["claude"]["surface"] == ".claude/skills/verify/SKILL.md"
    assert cap["claude"]["status"] == "native"
    assert cap["codex"]["surface"] == ".codex/skills/verify/SKILL.md"
    assert cap["codex"]["status"] == "adapter"
    assert cap["codex"]["adapter_source"] == ".claude/skills/verify/SKILL.md"


def test_skill_documents_NO_GO_findings_structure() -> None:
    """Test #14 — body cites report-depth rules for NO-GO finding structure."""
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    assert ".claude/rules/report-depth.md" in body, "skill must cite report-depth.md for finding structure"
    assert "NO-GO" in body, "skill body must reference the NO-GO verdict"


def test_target_paths_all_within_gtkb_root() -> None:
    """Test #15 — every declared target path resolves under the GT-KB root."""
    for relative in _TARGET_PATHS:
        resolved = (_REPO_ROOT / relative).resolve()
        assert _REPO_ROOT in resolved.parents or resolved == _REPO_ROOT, (
            f"target path escapes GT-KB root: {relative}"
        )
        assert "applications" not in Path(relative).parts, (
            f"target path must not be under applications/: {relative}"
        )
