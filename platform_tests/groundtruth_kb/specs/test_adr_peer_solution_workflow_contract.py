"""Current authority boundary for informative peer-workflow vocabulary.

These are canonical-content fitness checks. Native authority and bridge tests
separately qualify domain writes, claims and lifecycle behavior.
"""

from pathlib import Path

import pytest

from scripts.harness_projection import project_harness as projector

pytestmark = pytest.mark.integration
ADR_ID = "ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001"


def test_adr_row_structure(formal_record):
    row = formal_record(ADR_ID)
    assert row["type"] == "architecture_decision"
    assert row["description"].strip()
    for heading in (
        "## Context",
        "## Decision",
        "## Failed Approaches",
        "## Alternatives Considered",
        "## Consequences",
    ):
        assert heading in row["description"]


def test_peer_vocabulary_does_not_supply_runtime_authority(formal_record):
    constraints = formal_record(ADR_ID)["constraints"]
    assert constraints["peer_runtime_authority"] is False
    assert set(constraints["workflow_vocabulary"]) == {"nodes", "edges", "gates", "evaluators"}


def test_domain_services_carry_authority_without_message_or_decision_ledgers(formal_record):
    constraints = formal_record(ADR_ID)["constraints"]
    assert constraints["domain_authority"] == "postgresql_services"
    assert constraints["bridge_content_is_durable_authority"] is False
    assert constraints["decision_ledger_required"] is False


def test_current_architecture_information_and_evidence_contract(formal_record):
    """Structured content checks are discovery/fitness, not runtime proof."""
    row = formal_record("GOV-20")
    assert row["type"] == "governance" and row["description"].strip()
    constraints = row["constraints"]
    assert constraints["adr_information_topics"] == [
        "decision",
        "context",
        "failed_approaches",
        "alternatives",
        "consequences",
    ]
    assert constraints["observed_failure_distinct_from_rejected_alternative"] is True
    assert constraints["native_formal_writer_required"] is True
    assert constraints["structural_assertion_is_behavioral_verification"] is False
    assert constraints["separate_ipr_cvr_gate"] is False


@pytest.mark.parametrize("harness", sorted(projector.load_profiles()["harnesses"]))
def test_registered_projector_points_to_architecture_authoring_and_audit_guidance(harness):
    """The authored bodies retain the native writer duty; pointers only enable host discovery."""
    profiles = projector.load_profiles()["harnesses"]
    plan = projector.build_plan(harness)
    assert plan.writes and not plan.gaps, plan.gaps
    root = Path(__file__).resolve().parents[3]
    for skill, heading in (
        ("gtkb-adr", "# Architecture decision authoring"),
        ("gtkb-arch-audit", "# Architecture evidence review"),
    ):
        source = root / ".agents/skills" / skill / "SKILL.md"
        body = source.read_text(encoding="utf-8").split(heading, 1)[1].strip()
        assert "gt spec show" in body and "KnowledgeDB(" not in body
        outputs = {path: text for path, text in plan.writes.items() if path.endswith(f"/{skill}/SKILL.md")}
        if profiles[harness]["skills_discovery"] == "agents_skills":
            assert outputs == {}
        else:
            path = profiles[harness]["skills_stub_dir"] + f"/{skill}/SKILL.md"
            assert set(outputs) == {path}
            assert f".agents/skills/{skill}/SKILL.md" in outputs[path] and body not in outputs[path]
