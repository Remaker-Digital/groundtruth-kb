from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONTRACT = PROJECT_ROOT / ".claude/rules/codex-review-operating-contract.md"
CHECKLIST = PROJECT_ROOT / ".claude/rules/codex-review-checklists.md"
TEMPLATE_CONTRACT = PROJECT_ROOT / "groundtruth-kb/templates/project/codex-bootstrap/codex-review-operating-contract.md"

CANONICAL_SKILLS = [
    PROJECT_ROOT / ".claude/skills/codex-report/SKILL.md",
    PROJECT_ROOT / ".claude/skills/lo-opportunity-radar/SKILL.md",
    PROJECT_ROOT / ".claude/skills/loyal-opposition-hygiene-assessment/SKILL.md",
]

CODEX_ADAPTERS = [
    PROJECT_ROOT / ".codex/skills/codex-report/SKILL.md",
    PROJECT_ROOT / ".codex/skills/lo-opportunity-radar/SKILL.md",
    PROJECT_ROOT / ".codex/skills/loyal-opposition-hygiene-assessment/SKILL.md",
]

GATE_PHRASE = "Required Prime Builder Owner-Grilling Gate"
DISPOSITION_TERMS = ("adopt", "adapt", "reject", "defer", "monitor")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _collapsed(text: str) -> str:
    return " ".join(text.split())


def test_review_contract_declares_advisory_report_as_fifth_output_mode() -> None:
    text = _read(CONTRACT)

    assert "Use one of these five modes for substantial work" in text
    assert "5. **Advisory Report**" in text
    assert GATE_PHRASE in _collapsed(text)
    for term in DISPOSITION_TERMS:
        assert f"`{term}`" in text


def test_template_contract_carries_advisory_disposition_and_gate() -> None:
    text = _read(TEMPLATE_CONTRACT)

    assert "**Advisory Report**" in text
    assert GATE_PHRASE in _collapsed(text)
    for term in DISPOSITION_TERMS:
        assert f"`{term}`" in text


def test_review_checklist_has_advisory_report_gate_checklist() -> None:
    text = _read(CHECKLIST)

    assert "## Advisory Report Checklist" in text
    assert GATE_PHRASE in _collapsed(text)
    assert "before any derived implementation proposal" in text


def test_advisory_emitting_skills_include_owner_grilling_gate_guidance() -> None:
    for path in CANONICAL_SKILLS:
        text = _read(path)
        assert GATE_PHRASE in _collapsed(text), path
        assert "adopt" in text and "adapt" in text, path


def test_codex_adapters_preserve_headers_and_gate_guidance() -> None:
    for path in CODEX_ADAPTERS:
        text = _read(path)
        assert "GTKB-CODEX-SKILL-ADAPTER" in text, path
        assert "Canonical source:" in text, path
        assert GATE_PHRASE in _collapsed(text), path
        assert "adopt" in text and "adapt" in text, path
