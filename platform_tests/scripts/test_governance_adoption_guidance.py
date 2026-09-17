"""The standing guidance cites the governance-adoption records (neutral baseline, projected unchanged).

Carries the retained duty of the retired rule-wording checks: the acting-prime-builder rule and the standing
priorities name the governing records and keep the directives that still govern. Wording retired with the
approval-packet, deliberation-archive, session-lifecycle-engagement and harness-role-registry mechanisms is not
asserted; the governing records themselves are read natively in the formal corpus.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_RULE = REPO_ROOT / ".harness-baseline-configuration/rules/acting-prime-builder.md"
PROJECTED_RULE = REPO_ROOT / ".claude/rules/acting-prime-builder.md"
AGENTS = REPO_ROOT / "AGENTS.md"
GOVERNING_RECORDS = (
    "GOV-ACTING-PRIME-BUILDER-001",
    "GOV-AGENT-RED-GTKB-CONFORMANCE-001",
    "GOV-ARTIFACT-APPROVAL-001",
    "PB-ARTIFACT-APPROVAL-001",
    "ADR-ARTIFACT-FORMALIZATION-GATE-001",
    "DCL-ARTIFACT-APPROVAL-HOOK-001",
    "GOV-RELEASE-READINESS-GOVERNED-TESTING-001",
    "GOV-GTKB-ADOPTION-ENFORCEMENT-001",
    "GOV-STANDING-BACKLOG-001",
    "PB-STANDING-BACKLOG-CONTINUITY-001",
    "ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001",
    "DCL-STANDING-BACKLOG-SCHEMA-001",
    "GOV-SESSION-SELF-INITIALIZATION-001",
    "PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001",
    "DCL-SESSION-STARTUP-TOKEN-BUDGET-001",
    "PB-SESSION-WRAP-UP-PROACTIVE-001",
    "DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001",
)
RETAINED_DIRECTIVES = (
    "Prime Builder and Loyal Opposition are not permanently bound",
    "Any AI model harness may assume either role",
    "Agent Red is a well-behaved",
    "fully-conformant adopter",
    "supported and sustained by GroundTruth-KB",
    "to be treated as one",
    "require production-release work to include governed release-readiness evidence",
    "cited in rules, regression-tested, and visible",
    "standing backlog",
    "treated like other formal",
    "Individual backlog entries remain queue/work items",
)


def _one_line(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_acting_prime_builder_rule_names_the_governing_records() -> None:
    rule = _one_line(BASELINE_RULE)
    for record in GOVERNING_RECORDS:
        assert record in rule, record
    for directive in RETAINED_DIRECTIVES:
        assert directive in rule or directive.lower() in rule.lower(), directive


def test_projected_rule_carries_the_baseline_body() -> None:
    assert _one_line(BASELINE_RULE) in _one_line(PROJECTED_RULE)


def test_standing_priorities_cite_artifact_oriented_governance() -> None:
    priorities = AGENTS.read_text(encoding="utf-8")
    for record in (
        "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
        "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
        "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
    ):
        assert record in priorities, record


def test_release_candidate_gate_skill_documents_the_gate_script() -> None:
    skill = (REPO_ROOT / ".harness-baseline-configuration/skills/gtkb-release-candidate-gate/SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "scripts/release_candidate_gate.py" in skill
    assert "--skip-frontend" in skill and "--include-frontend" in skill
