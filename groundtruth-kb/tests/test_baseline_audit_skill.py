# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Smoke tests for baseline-audit skill contract."""

from __future__ import annotations

import pytest

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


def test_managed_registry_carries_no_orientation_copy_rows() -> None:
    """M15 (D15/D34): rules and skills are never scaffolded as managed copies.

    The former orientation rule and baseline-audit skill rows are gone and no rule or skill class remains in
    the registry; their non-baseline template sources stay in place pending M26.6.
    """
    from groundtruth_kb.project.managed_registry import _load_all_artifacts, find_artifact_by_id

    for artifact_id in ("rule.session-start-orientation", "skill.baseline-audit.skill-md"):
        with pytest.raises(KeyError):
            find_artifact_by_id(artifact_id)
    assert not [artifact for artifact in _load_all_artifacts() if artifact.class_ in {"rule", "skill"}]
    templates = get_templates_dir()
    assert (templates / "rules/session-start-orientation.md").is_file()
    assert (templates / "skills/gtkb-baseline-audit/SKILL.md").is_file()


def test_baseline_audit_skill_template_exists() -> None:
    skill_path = get_templates_dir() / "skills/gtkb-baseline-audit/SKILL.md"
    assert skill_path.is_file()
    text = skill_path.read_text(encoding="utf-8")
    assert "baseline status" in text
    assert "Loyal Opposition" in text
    assert str(baseline_audit.BASELINE_AUDIT_ITEM_COUNT) in text
