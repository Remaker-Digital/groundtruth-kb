"""The governance-adoption record set exists as current canonical records (read through the native authority).

Carries the retained duty of the retired SQLite MemBase checks: every record of the adoption milestone set is a
current canonical record with its recorded type; statuses follow the native vocabulary (the SQLite-era
"verified" is "active" here; one record is superseded); phrases that still govern are asserted, phrases amended
away under the artifact-authority and retirement rulings are not.
"""

import pytest

pytestmark = pytest.mark.integration

RECORD_SET = {
    # formal artifact approval (GOV-ARTIFACT-APPROVAL-001 family, amended to native review under v2)
    "GOV-ARTIFACT-APPROVAL-001": ("governance", "active"),
    "PB-ARTIFACT-APPROVAL-001": ("protected_behavior", "active"),
    "ADR-ARTIFACT-FORMALIZATION-GATE-001": ("architecture_decision", "active"),
    "DCL-ARTIFACT-APPROVAL-HOOK-001": ("design_constraint", "active"),
    # session governance principles
    "GOV-RELEASE-READINESS-GOVERNED-TESTING-001": ("governance", "active"),
    "GOV-GTKB-ADOPTION-ENFORCEMENT-001": ("governance", "active"),
    "GOV-ACTING-PRIME-BUILDER-001": ("governance", "retired"),
    "GOV-ROLE-DETERMINATION-INIT-LINE-ONLY-001": ("governance", "active"),
    "DCL-SESSION-ROLE-RESOLUTION-001": ("design_constraint", "active"),
    "GOV-HARNESS-ROLE-PORTABILITY-001": ("governance", "retired"),
    "GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001": ("governance", "retired"),
    "GOV-AGENT-RED-GTKB-CONFORMANCE-001": ("governance", "active"),
    "ADR-CODEX-HOOK-PARITY-FALLBACK-001": ("architecture_decision", "active"),
    "GOV-SESSION-FORMALIZATION-AUDIT-001": ("governance", "active"),
    # standing backlog
    "GOV-STANDING-BACKLOG-001": ("governance", "active"),
    "PB-STANDING-BACKLOG-CONTINUITY-001": ("protected_behavior", "active"),
    "ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001": ("architecture_decision", "active"),
    "DCL-STANDING-BACKLOG-SCHEMA-001": ("design_constraint", "active"),
    # session self-initialization
    "GOV-SESSION-SELF-INITIALIZATION-001": ("governance", "active"),
    "PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001": ("protected_behavior", "active"),
    "SPEC-PROJECT-DASHBOARD-KPI-LINK-001": ("requirement", "active"),
    "DCL-SESSION-STARTUP-TOKEN-BUDGET-001": ("design_constraint", "active"),
    # session lifecycle engagement
    "GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001": ("governance", "superseded"),
    "PB-SESSION-WRAP-UP-PROACTIVE-001": ("protected_behavior", "active"),
    "DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001": ("design_constraint", "active"),
    # artifact-oriented governance
    "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001": ("governance", "active"),
    "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001": ("architecture_decision", "active"),
    "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001": ("design_constraint", "active"),
    # core specification intake phase 0
    "SPEC-CORE-INTAKE-001": ("requirement", "active"),
    "SPEC-CORE-INTAKE-002": ("requirement", "active"),
    "ADR-CORE-INTAKE-001": ("architecture_decision", "active"),
    "DCL-CORE-INTAKE-001": ("design_constraint", "active"),
    # bridge authority
    "GOV-FILE-BRIDGE-AUTHORITY-001": ("governance", "active"),
}
GOVERNING_PHRASES = {
    "GOV-AGENT-RED-GTKB-CONFORMANCE-001": ["well-behaved, fully conformant"],
    "ADR-CODEX-HOOK-PARITY-FALLBACK-001": ["IS a live Codex interception boundary on Windows"],
    "PB-STANDING-BACKLOG-CONTINUITY-001": ["must not ignore, silently reorder, or drop"],
    "ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001": ["human-readable standing backlog authority"],
    "DCL-STANDING-BACKLOG-SCHEMA-001": ["stable identifier", "regression visibility"],
    "PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001": [
        "must not proceed as if governance context is implicit",
        "skills, plug-ins, directives",
    ],
    "SPEC-PROJECT-DASHBOARD-KPI-LINK-001": ["live project dashboard link", "time-series KPI", "tokens consumed"],
    "DCL-SESSION-STARTUP-TOKEN-BUDGET-001": ["progressive disclosure"],
    "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001": ["candidate", "non-intrusive confirmation"],
}


@pytest.mark.parametrize("record_id", sorted(RECORD_SET))
def test_adoption_record_is_current_with_its_recorded_type(formal_record, record_id):
    spec_type, status = RECORD_SET[record_id]
    row = formal_record(record_id, expected_status=status)
    assert row["type"] == spec_type
    assert row["authority"] == "stated"
    assert row["description"].strip()


@pytest.mark.parametrize("record_id", sorted(GOVERNING_PHRASES))
def test_governing_phrases_still_present(formal_record, record_id):
    description = " ".join(formal_record(record_id)["description"].split())
    for phrase in GOVERNING_PHRASES[record_id]:
        assert phrase in description, (record_id, phrase)


def test_bridge_authority_governs_queue_state_and_startup_reads(formal_record):
    bridge = " ".join(formal_record("GOV-FILE-BRIDGE-AUTHORITY-001")["description"].split()).lower()
    startup = " ".join(formal_record("GOV-SESSION-SELF-INITIALIZATION-001")["description"].split()).lower()
    assert "bridge" in bridge and "authority" in bridge
    assert "startup" in startup or "session" in startup
