# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural, helper-behavior, and parity tests for the decision-capture skill.

Derived from WI-3407 (bridge thread
``gtkb-wi3407-composite-delib-workflow-skill``). WI-3407 turns the S363
composite owner-decision capture pattern into explicit decision-capture skill
guidance and helper coverage: the skill already records one owner decision as
one Deliberation Archive record; WI-3407 adds a pure ``compose_composite_content``
composer plus guidance for the cases where several AskUserQuestion answers form
one coherent composite DELIB (e.g. ``DELIB-2234`` and ``DELIB-2238``).

Linked specifications carried forward from the implementation proposal
(``bridge/gtkb-wi3407-composite-delib-workflow-skill-001.md``):

- ``GOV-FILE-BRIDGE-AUTHORITY-001`` - bridge protocol authority.
- ``SPEC-2098`` - Deliberation Archive protocol (search, citation, capture).
- ``DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`` - concrete spec
  linkage for implementation work.
- ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`` - spec-derived testing.
- ``ADR-CROSS-HARNESS-PARITY-001`` and
  ``DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`` - harness surface parity.
"""

from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLAUDE_SKILL = _REPO_ROOT / ".claude" / "skills" / "decision-capture" / "SKILL.md"
_CLAUDE_HELPER = _REPO_ROOT / ".claude" / "skills" / "decision-capture" / "helpers" / "record_decision.py"
_CODEX_SKILL = _REPO_ROOT / ".codex" / "skills" / "decision-capture" / "SKILL.md"
_CODEX_HELPER = _REPO_ROOT / ".codex" / "skills" / "decision-capture" / "helpers" / "record_decision.py"

_GENERATED_MARKER = "<!-- GTKB-CODEX-SKILL-ADAPTER"
_GENERATED_END_MARKER = "GTKB-CODEX-SKILL-ADAPTER -->"

_TARGET_PATHS = (
    ".claude/skills/decision-capture/SKILL.md",
    ".claude/skills/decision-capture/helpers/record_decision.py",
    ".codex/skills/decision-capture/SKILL.md",
    ".codex/skills/decision-capture/helpers/record_decision.py",
    "platform_tests/skills/test_decision_capture_skill.py",
    "platform_tests/scripts/test_generate_codex_skill_adapters.py",
    "platform_tests/scripts/test_groundtruth_governance_adoption.py",
)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
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


def _load_helper() -> ModuleType:
    spec = importlib.util.spec_from_file_location("wi3407_record_decision", _CLAUDE_HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Register before exec so ``@dataclass`` can resolve ``cls.__module__``.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _FakeDB:
    """Minimal KnowledgeDB stand-in capturing insert kwargs; no real writes."""

    def __init__(self, existing: dict | None = None) -> None:
        self._existing = existing
        self.insert_kwargs: dict | None = None

    def get_deliberation(self, delib_id: str) -> dict | None:
        return self._existing

    def insert_deliberation(self, **kwargs: object) -> dict:
        self.insert_kwargs = dict(kwargs)
        return {"id": kwargs.get("id"), "version": 1, **kwargs}


# --------------------------------------------------------------------------- #
# SKILL.md structural tests
# --------------------------------------------------------------------------- #
def test_canonical_skill_file_exists_with_frontmatter() -> None:
    assert _CLAUDE_SKILL.is_file(), f"missing skill file: {_CLAUDE_SKILL}"
    frontmatter, body = _split_frontmatter(_CLAUDE_SKILL.read_text(encoding="utf-8"))
    assert _frontmatter_value(frontmatter, "name") == "gtkb-decision-capture"
    description = _frontmatter_value(frontmatter, "description")
    assert "owner decision" in description.lower()
    assert body.strip(), "skill body must not be empty"


def test_skill_documents_composite_workflow_sections() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    for section in (
        "## Composite owner-decision workflow",
        "### When to consolidate vs. split",
        "### Composite content shape",
        "### source-ref and AUQ-id naming",
        "### Fixed metadata and atomic path are preserved",
    ):
        assert section in body, f"skill body is missing composite section {section!r}"


def test_skill_names_the_four_composite_content_sections() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    for named in (
        "`## Decisions`",
        "`## Composed Implications`",
        "`## Linked Artifacts`",
        "`## First Concrete Actions Authorized`",
    ):
        assert named in body, f"skill body must name composite content section {named!r}"


def test_skill_documents_consolidate_split_and_naming() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    lower = body.lower()
    # Consolidate-vs-split guidance is present and points at the exemplars.
    assert "consolidate" in lower and "split" in lower
    assert "DELIB-2234" in body and "DELIB-2238" in body
    # source-ref / AUQ-id naming guidance.
    assert "source-ref" in lower
    assert "AUQ-id" in body or "AUQ-<n>" in body
    assert "§9.1" in body


def test_skill_preserves_atomic_path_and_fixed_metadata() -> None:
    body = _CLAUDE_SKILL.read_text(encoding="utf-8")
    assert "compose_composite_content" in body
    assert "record_decision" in body
    # The composite workflow must not change the fixed write-path metadata.
    assert 'source_type="owner_conversation"' in body
    assert 'outcome="owner_decision"' in body
    # The atomic single-decision path stays available.
    assert "atomic single-decision path remains available" in body


# --------------------------------------------------------------------------- #
# helper behavior tests
# --------------------------------------------------------------------------- #
def test_helper_exports_composer_and_dataclass() -> None:
    module = _load_helper()
    assert hasattr(module, "compose_composite_content")
    assert hasattr(module, "CompositeDecision")
    assert hasattr(module, "CompositeCompositionError")
    assert hasattr(module, "record_decision")


def test_compose_produces_all_sections_and_preserves_source_refs() -> None:
    module = _load_helper()
    decisions = [
        module.CompositeDecision(source_ref="§9.1", decision="Hybrid Variant", rationale="§4 + §6 + §7"),
        module.CompositeDecision(source_ref="AUQ-2", decision="Quality-driven ship", rationale="no date pressure"),
    ]
    body = module.compose_composite_content(
        "GT-KB v1.0 Release Strategy Decisions",
        "Resolves the eight open questions.",
        decisions,
        composed_implications=["Stable core has backward-compat guarantees."],
        linked_artifacts=["DELIB-2234", "bridge/gtkb-example-001.md"],
        first_concrete_actions=["Scope the mechanical-enforcement gate."],
    )
    assert body.startswith("# GT-KB v1.0 Release Strategy Decisions")
    for section in (
        "## Decisions",
        "## Composed Implications",
        "## Linked Artifacts",
        "## First Concrete Actions Authorized",
    ):
        assert section in body, f"composed body is missing {section!r}"
    # Source-refs (AUQ-id and section-anchor forms) survive into the table.
    assert "| §9.1 |" in body
    assert "| AUQ-2 |" in body
    # First actions are a numbered list.
    assert "1. Scope the mechanical-enforcement gate." in body
    assert body.endswith("\n")


def test_compose_minimal_omits_empty_optional_sections() -> None:
    module = _load_helper()
    body = module.compose_composite_content(
        "Minimal composite",
        "Intro.",
        [module.CompositeDecision(source_ref="AUQ-1", decision="Do X", rationale="because")],
    )
    assert "## Decisions" in body
    assert "## Composed Implications" not in body
    assert "## Linked Artifacts" not in body
    assert "## First Concrete Actions Authorized" not in body


def test_compose_escapes_pipe_in_cells() -> None:
    module = _load_helper()
    body = module.compose_composite_content(
        "Pipe test",
        "Intro.",
        [module.CompositeDecision(source_ref="AUQ-1", decision="A | B", rationale="x | y")],
    )
    assert "A \\| B" in body
    assert "x \\| y" in body


def test_compose_rejects_empty_or_blank_inputs() -> None:
    module = _load_helper()
    err = module.CompositeCompositionError
    try:
        module.compose_composite_content("h", "i", [])
        raise AssertionError("empty decisions must raise CompositeCompositionError")
    except err:
        pass
    try:
        module.compose_composite_content("", "i", [module.CompositeDecision("AUQ-1", "d", "r")])
        raise AssertionError("blank heading must raise CompositeCompositionError")
    except err:
        pass
    try:
        module.compose_composite_content(
            "h", "i", [module.CompositeDecision(source_ref="  ", decision="d", rationale="r")]
        )
        raise AssertionError("blank source_ref must raise CompositeCompositionError")
    except err:
        pass


def test_record_decision_fixed_metadata_unchanged() -> None:
    module = _load_helper()
    assert module._CHANGED_BY == "prime-builder/decision-capture-skill"
    assert module._CHANGE_REASON == "owner decision captured via /gtkb-decision-capture"
    db = _FakeDB(existing=None)
    module.record_decision(db, "DELIB-TEST-3407", "t", "s", "content body")
    assert db.insert_kwargs is not None
    assert db.insert_kwargs["source_type"] == "owner_conversation"
    assert db.insert_kwargs["outcome"] == "owner_decision"
    assert db.insert_kwargs["changed_by"] == "prime-builder/decision-capture-skill"
    assert db.insert_kwargs["change_reason"] == "owner decision captured via /gtkb-decision-capture"


def test_record_decision_collision_raises() -> None:
    module = _load_helper()
    db = _FakeDB(existing={"id": "DELIB-TEST-3407", "version": 2})
    try:
        module.record_decision(db, "DELIB-TEST-3407", "t", "s", "content")
        raise AssertionError("colliding DELIB-ID must raise DeliberationIDCollisionError")
    except module.DeliberationIDCollisionError:
        pass


def test_composite_content_flows_through_atomic_write_path() -> None:
    module = _load_helper()
    decisions = [module.CompositeDecision(source_ref="AUQ-1", decision="Do X", rationale="r")]
    body = module.compose_composite_content("Composite", "Intro.", decisions)
    db = _FakeDB(existing=None)
    module.record_decision(db, "DELIB-TEST-3407-C", "t", "s", body)
    # The composed body is inserted verbatim with the same fixed metadata.
    assert db.insert_kwargs is not None
    assert db.insert_kwargs["content"] == body
    assert db.insert_kwargs["source_type"] == "owner_conversation"


# --------------------------------------------------------------------------- #
# cross-harness parity tests
# --------------------------------------------------------------------------- #
def test_codex_adapter_matches_canonical_sha() -> None:
    assert _CODEX_SKILL.is_file(), f"missing Codex adapter: {_CODEX_SKILL}"
    canonical = _CLAUDE_SKILL.read_text(encoding="utf-8")
    adapter = _CODEX_SKILL.read_text(encoding="utf-8")
    assert _GENERATED_MARKER in adapter
    assert _GENERATED_END_MARKER in adapter
    assert "Canonical source: .claude/skills/decision-capture/SKILL.md" in adapter
    assert _adapter_recorded_sha(adapter) == _canonical_normalized_sha(canonical)


def test_codex_helper_carries_composer_for_parity() -> None:
    assert _CODEX_HELPER.is_file(), f"missing Codex helper: {_CODEX_HELPER}"
    codex_helper = _CODEX_HELPER.read_text(encoding="utf-8")
    # The regenerated Codex helper must carry the same composite composer surface.
    assert "def compose_composite_content" in codex_helper
    assert "class CompositeDecision" in codex_helper
    assert "def record_decision" in codex_helper


def test_target_paths_all_within_gtkb_root() -> None:
    for relative in _TARGET_PATHS:
        resolved = (_REPO_ROOT / relative).resolve()
        assert _REPO_ROOT in resolved.parents or resolved == _REPO_ROOT
        assert "applications" not in Path(relative).parts
