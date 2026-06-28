# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Smoke tests for baseline-audit skill contract."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb import get_templates_dir
from groundtruth_kb.project import baseline_audit


def test_baseline_audit_skill_triggers_on_keyword_family() -> None:
    assert baseline_audit.matches_baseline_audit_trigger("Please give me baseline status")
    assert baseline_audit.matches_baseline_audit_trigger("Where do we stand on release readiness?")
    assert not baseline_audit.matches_baseline_audit_trigger("continue bridge work")


def test_baseline_audit_evidence_class_tagging() -> None:
    rows = []
    for index in range(1, baseline_audit.BASELINE_AUDIT_ITEM_COUNT + 1):
        rows.append(f"| {index} | item | answer | [evidence_class: command_output] |")
    output = "\n".join(rows)
    ok, message = baseline_audit.validate_baseline_audit_output(output)
    assert ok is True, message


def test_baseline_audit_rejects_missing_evidence_class() -> None:
    rows = [f"| {index} | item | answer | missing tag |" for index in range(1, 30)]
    ok, message = baseline_audit.validate_baseline_audit_output("\n".join(rows))
    assert ok is False
    assert "missing evidence-class tag" in message


def test_managed_registry_includes_new_orientation_rows() -> None:
    from groundtruth_kb.project.managed_registry import find_artifact_by_id

    rule = find_artifact_by_id("rule.session-start-orientation")
    skill = find_artifact_by_id("skill.baseline-audit.skill-md")
    assert rule is not None
    assert skill is not None
    assert rule.target_path.endswith("session-start-orientation.md")
    assert skill.target_path.endswith("baseline-audit/SKILL.md")


def test_baseline_audit_skill_template_exists() -> None:
    skill_path = get_templates_dir() / "skills/baseline-audit/SKILL.md"
    assert skill_path.is_file()
    text = skill_path.read_text(encoding="utf-8")
    assert "baseline status" in text
    assert "Loyal Opposition" in text
    assert str(baseline_audit.BASELINE_AUDIT_ITEM_COUNT) in text
