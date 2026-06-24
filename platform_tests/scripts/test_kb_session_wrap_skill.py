from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_SKILL = PROJECT_ROOT / ".claude" / "skills" / "kb-session-wrap" / "SKILL.md"
CODEX_SKILL = PROJECT_ROOT / ".codex" / "skills" / "kb-session-wrap" / "SKILL.md"
CANONICAL_REFERENCES = PROJECT_ROOT / ".claude" / "skills" / "kb-session-wrap" / "references"
CODEX_REFERENCES = PROJECT_ROOT / ".codex" / "skills" / "kb-session-wrap" / "references"
HANDOFF_TEMPLATE = CANONICAL_REFERENCES / "handoff-template.md"
AUDIT_CHECKLIST = CANONICAL_REFERENCES / "audit-checklist.md"
CODEX_HANDOFF_TEMPLATE = CODEX_REFERENCES / "handoff-template.md"
CODEX_AUDIT_CHECKLIST = CODEX_REFERENCES / "audit-checklist.md"


REQUIRED_SKILL_TERMS = (
    "Knowledge Collection Matrix",
    "MemBase",
    "Deliberation Archive",
    "memory/MEMORY.md",
    "TAFE-backed bridge state",
    "dispatcher status/health",
    "versioned bridge files",
    "session_prompts",
    "wrap scanner outputs",
    "ignored local evidence",
    "formal-artifact approval",
    "Do not force-add `groundtruth.db`",
    "git push origin <current-branch>",
)


def test_canonical_wrap_skill_requires_knowledge_collection() -> None:
    text = CANONICAL_SKILL.read_text(encoding="utf-8")

    for term in REQUIRED_SKILL_TERMS:
        assert term in text

    assert "git push origin main" not in text
    assert "Agent Red Customer Experience" not in text
    assert "tools/knowledge-db" not in text


def test_codex_adapter_preserves_wrap_skill_contract() -> None:
    text = CODEX_SKILL.read_text(encoding="utf-8")

    assert "GTKB-CODEX-SKILL-ADAPTER" in text
    assert "Canonical source: .claude/skills/kb-session-wrap/SKILL.md" in text
    assert "references/audit-checklist.md" in text
    assert "references/handoff-template.md" in text
    for term in REQUIRED_SKILL_TERMS:
        assert term in text


def test_codex_adapter_preserves_wrap_skill_references() -> None:
    reference_pairs = (
        (AUDIT_CHECKLIST, CODEX_AUDIT_CHECKLIST),
        (HANDOFF_TEMPLATE, CODEX_HANDOFF_TEMPLATE),
    )

    for canonical_reference, codex_reference in reference_pairs:
        assert canonical_reference.is_file()
        assert codex_reference.is_file()
        assert codex_reference.read_bytes() == canonical_reference.read_bytes()


def test_handoff_template_is_gtkb_specific_and_self_contained() -> None:
    text = HANDOFF_TEMPLATE.read_text(encoding="utf-8")

    required_terms = (
        "::init gtkb pb",
        "Continue GroundTruth-KB work in E:/GT-KB",
        "Bridge state",
        "MemBase",
        "Deliberation Archive",
        "session_prompts",
        "Wrap scanner outputs",
        "Ignored local evidence",
        "Suggested Next Actions",
    )
    for term in required_terms:
        assert term in text

    assert "Agent Red Customer Experience" not in text


def test_audit_checklist_checks_freshness_and_ignored_evidence() -> None:
    text = AUDIT_CHECKLIST.read_text(encoding="utf-8")

    required_terms = (
        "Deliberation Archive Freshness",
        "Bridge Closure",
        "Session Prompt Continuity",
        "Wrap Scanner Trend",
        "Ignored Evidence And Git Hygiene",
        "TAFE-backed bridge state",
        "dispatcher status/health",
        "aggregate queue artifacts",
        "session_prompts",
        "force-added",
    )
    for term in required_terms:
        assert term in text
