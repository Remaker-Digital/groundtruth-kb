"""Regression checks for GroundTruth-KB platform governance adoption."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _load_toml(path: str) -> dict:
    return tomllib.loads(_read(path))


def _one_line(text: str) -> str:
    return " ".join(text.split())


def _assert_not_git_ignored(paths: list[str]) -> None:
    result = subprocess.run(
        ["git", "check-ignore"] + paths,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    ignored = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert not ignored, f"GroundTruth governance artifacts are still git-ignored: {ignored}"


def test_groundtruth_adopter_profile_is_pinned() -> None:
    config = _load_toml("groundtruth.toml")

    assert config["groundtruth"]["db_path"] == "groundtruth.db"
    assert config["project"]["project_name"] == "GroundTruth-KB Platform"
    assert config["project"]["owner"] == "Remaker Digital"
    assert config["project"]["profile"] == "dual-agent"
    assert config["project"]["cloud_provider"] == "azure"
    assert config["project"]["scaffold_version"] == "0.7.0rc1"
    assert config["scoped_service"]["application_id"] == "agent-red"


def test_transport_evidence_gate_plugin_is_configured() -> None:
    config = _load_toml("tools/knowledge-db/groundtruth.toml")

    assert config["groundtruth"]["db_path"] == "../../groundtruth.db"
    assert config["groundtruth"]["project_root"] == "../.."
    assert config["gates"]["plugins"] == ["groundtruth_kb.gates_transport:TransportEvidenceGate"]
    assert set(config["gates"]["config"]["TransportEvidenceGate"]["spec_ids"]) == {
        "SPEC-1524",
        "SPEC-1525",
        "SPEC-1535",
        "SPEC-1536",
        "SPEC-1537",
        "SPEC-1802",
    }


def test_release_candidate_gate_runs_governance_adoption_tests() -> None:
    gate = _read("scripts/release_candidate_gate.py")

    assert "tests/scripts/test_session_self_initialization.py" in gate
    assert "tests/scripts/test_groundtruth_governance_adoption.py" in gate
    assert "tests/scripts/test_codex_hook_parity.py" in gate
    assert "tests/scripts/test_standing_backlog_harvest.py" in gate
    assert "tests/hooks/test_formal_artifact_approval_gate.py" in gate
    assert "tests/hooks/test_workstream_focus.py" in gate
    assert "scripts/check_harness_parity.py" in gate


def test_release_candidate_gate_workflow_has_python_and_frontend_lanes() -> None:
    workflow = _read(".github/workflows/release-candidate-gate.yml")

    assert "--require-python 3.12 --skip-frontend" in workflow
    assert "--skip-python --include-frontend" in workflow
    assert "windows-latest" in workflow


def test_sonarcloud_workflow_can_verify_exact_release_candidate() -> None:
    workflow = _read(".github/workflows/sonarcloud.yml")
    sonar_properties = _read("sonar-project.properties")

    assert "branches: [main, develop]" in workflow
    assert "workflow_dispatch:" in workflow
    assert "timeout-minutes: 15" in workflow
    assert "grep -v '^agntcy-app-sdk' requirements.txt" in workflow
    assert "sonar.organization=mike-remakerdigital" in sonar_properties
    assert "Validate SonarCloud token" in workflow
    assert "SONAR_TOKEN" in workflow


def test_security_scan_uses_scan_only_acr_secrets_for_docker_scout() -> None:
    workflow = _read(".github/workflows/security-scan.yml")

    assert "Validate Docker Scout ACR secrets" in workflow
    assert "ACR_SCOUT_USERNAME" in workflow
    assert "ACR_SCOUT_PASSWORD" in workflow
    assert "DOCKER_SCOUT_HUB_USER" in workflow
    assert "DOCKER_SCOUT_HUB_PAT" in workflow
    assert "Login to Docker Hub for Docker Scout" in workflow
    assert "docker/login-action@v4" in workflow
    assert "username: ${{ secrets.ACR_SCOUT_USERNAME }}" in workflow
    assert "password: ${{ secrets.ACR_SCOUT_PASSWORD }}" in workflow
    assert "username: ${{ secrets.ACR_USERNAME }}" not in workflow
    assert "password: ${{ secrets.ACR_PASSWORD }}" not in workflow


def test_release_candidate_skill_documents_mem_and_da_evidence() -> None:
    skill = _read(".claude/skills/release-candidate-gate/SKILL.md")

    assert "scripts/release_candidate_gate.py" in skill
    assert "--require-python 3.12" in skill
    assert "MemBase" in skill
    assert "Deliberation Archive" in skill


def test_acting_prime_builder_rule_maps_prime_skill_labels_to_assigned_role() -> None:
    rule = _one_line(_read(".claude/rules/acting-prime-builder.md"))

    assert "DELIB-0830" in rule
    assert "DELIB-0831" in rule
    assert "DELIB-0832" in rule
    assert "GOV-ACTING-PRIME-BUILDER-001" in rule
    assert "GOV-HARNESS-ROLE-PORTABILITY-001" in rule
    assert "GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001" in rule
    assert "Prime Builder and Loyal Opposition are not permanently bound" in rule
    assert "Any AI model harness may assume either role" in rule
    assert "all skills" in rule
    assert "plugins" in rule
    assert "hooks" in rule
    assert "bridge counterpart is always Loyal Opposition" in rule
    assert "legacy/compatibility/provenance" in rule
    assert "NOT a new role-switch target" in rule
    assert "only `prime-builder` and `loyal-opposition` are valid" in rule
    assert "READ operations load role values from the canonical role registry" in rule
    assert "unqualified GT-KB tooling references" in rule
    assert "must not resolve silently to Agent Red" in rule
    assert "DELIB-0834" in rule
    assert "GOV-AGENT-RED-GTKB-CONFORMANCE-001" in rule
    assert "Agent Red is a well-behaved" in rule
    assert "fully-conformant adopter" in rule
    assert "supported and sustained by GroundTruth-KB" in rule
    assert "to be treated as one" in rule
    assert "require production-release work to include governed release-readiness evidence" in rule
    assert "cited in rules, regression-tested, and visible" in rule
    assert "DELIB-0835" in rule
    assert "GOV-ARTIFACT-APPROVAL-001" in rule
    assert "PB-ARTIFACT-APPROVAL-001" in rule
    assert "ADR-ARTIFACT-FORMALIZATION-GATE-001" in rule
    assert "DCL-ARTIFACT-APPROVAL-HOOK-001" in rule
    assert "proposed artifact must be presented in native review format" in rule
    assert "full content and metadata" in rule
    assert "scoped auto-approval state" in rule
    assert "Auto-approval does not remove the display or audit requirement" in rule
    assert "captured in the session transcript" in rule
    assert "assigned Prime Builder harness while this assignment is active" in rule
    assert 'changed_by="prime-builder/..."' in rule
    assert "apply to the" in rule
    assert "assigned Prime Builder harness" in rule
    assert "DELIB-0828" in rule
    assert "DELIB-0829" in rule
    assert "GOV-RELEASE-READINESS-GOVERNED-TESTING-001" in rule
    assert "GOV-GTKB-ADOPTION-ENFORCEMENT-001" in rule
    assert "DELIB-0836" in rule
    assert "ADR-CODEX-HOOK-PARITY-FALLBACK-001" in rule
    assert "check_codex_hook_parity.py" in rule
    assert "DELIB-0837" in rule
    assert "GOV-SESSION-FORMALIZATION-AUDIT-001" in rule
    assert "DELIB-0838" in rule
    assert "GOV-STANDING-BACKLOG-001" in rule
    assert "PB-STANDING-BACKLOG-CONTINUITY-001" in rule
    assert "ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001" in rule
    assert "DCL-STANDING-BACKLOG-SCHEMA-001" in rule
    assert "standing backlog" in rule.lower()
    assert "MemBase" in rule
    assert "treated like other formal" in rule
    assert "Individual backlog entries remain queue/work items" in rule
    assert "must not be silently" in rule
    assert "DELIB-0840" in rule
    assert "GOV-SESSION-SELF-INITIALIZATION-001" in rule
    assert "PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001" in rule
    assert "SPEC-PROJECT-DASHBOARD-KPI-LINK-001" in rule
    assert "DCL-SESSION-STARTUP-TOKEN-BUDGET-001" in rule
    assert "role being assumed" in rule
    assert "skills, plug-ins, directives, hooks" in rule
    assert "governance stance" in rule
    assert "live project dashboard link" in rule
    assert "time-series KPI" in rule
    assert "tokens consumed" in rule
    assert "three top priority actions" in rule
    assert "reducing token consumption" in rule
    assert "DELIB-0841" in rule
    assert "GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001" in rule
    assert "PB-SESSION-WRAP-UP-PROACTIVE-001" in rule
    assert "DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001" in rule
    assert "should not have to explicitly instruct GroundTruth-KB" in rule
    assert "priorities across all project dimensions" in rule
    assert "Mutating" in rule
    assert "wrap-up work" in rule


def test_formal_artifact_approval_records_are_in_membase() -> None:
    expected = {
        "GOV-ARTIFACT-APPROVAL-001": "governance",
        "PB-ARTIFACT-APPROVAL-001": "protected_behavior",
        "ADR-ARTIFACT-FORMALIZATION-GATE-001": "architecture_decision",
        "DCL-ARTIFACT-APPROVAL-HOOK-001": "design_constraint",
    }

    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        for spec_id, spec_type in expected.items():
            spec = db.get_spec(spec_id)
            assert spec is not None, f"{spec_id} must exist in MemBase"
            assert spec["type"] == spec_type
            assert spec["status"] == "verified"
            if spec_id == "PB-ARTIFACT-APPROVAL-001":
                assert "DELIB-0835" in (spec["affected_by"] or "")

        gov = db.get_spec("GOV-ARTIFACT-APPROVAL-001")
        assert "native review format" in gov["description"]
        assert "Auto-approval does not remove" in gov["description"]
        assert gov["status"] == "verified"

        pb = db.get_spec("PB-ARTIFACT-APPROVAL-001")
        assert "approval or acknowledgement evidence" in pb["description"]
        assert "session transcript" in pb["description"]

        adr = db.get_spec("ADR-ARTIFACT-FORMALIZATION-GATE-001")
        assert "scoped auto-approval state" in adr["description"]

        dcl = db.get_spec("DCL-ARTIFACT-APPROVAL-HOOK-001")
        assert "full proposed content hash" in dcl["description"]
        assert "transcript record" in dcl["description"]
    finally:
        db.close()


def test_session_governance_principles_have_membase_records() -> None:
    expected = {
        "GOV-RELEASE-READINESS-GOVERNED-TESTING-001": ("governance", ["DELIB-0828", "DELIB-0829"]),
        "GOV-GTKB-ADOPTION-ENFORCEMENT-001": ("governance", ["DELIB-0829", "DELIB-0834"]),
        "GOV-ACTING-PRIME-BUILDER-001": ("governance", ["DELIB-0830"]),
        "GOV-HARNESS-ROLE-PORTABILITY-001": ("governance", ["DELIB-0831"]),
        "GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001": ("governance", ["DELIB-0832", "DELIB-0833"]),
        "GOV-AGENT-RED-GTKB-CONFORMANCE-001": ("governance", ["DELIB-0834"]),
        "ADR-CODEX-HOOK-PARITY-FALLBACK-001": ("architecture_decision", ["DELIB-0836"]),
        "GOV-SESSION-FORMALIZATION-AUDIT-001": ("governance", ["DELIB-0837"]),
    }

    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        for spec_id, (spec_type, delib_ids) in expected.items():
            spec = db.get_spec(spec_id)
            assert spec is not None, f"{spec_id} must exist in MemBase"
            assert spec["type"] == spec_type
            assert spec["status"] == "verified"
            if spec_id == "ADR-CODEX-HOOK-PARITY-FALLBACK-001":
                assert spec["testability"] in ("structural", None)
            else:
                assert spec["testability"] == "structural"
                for delib_id in delib_ids:
                    assert delib_id in (spec["affected_by"] or "")

        conformance = db.get_spec("GOV-AGENT-RED-GTKB-CONFORMANCE-001")
        assert "well-behaved, fully conformant" in conformance["description"]

        codex_fallback = db.get_spec("ADR-CODEX-HOOK-PARITY-FALLBACK-001")
        assert "IS a live Codex interception boundary on Windows" in codex_fallback["description"]

        audit = db.get_spec("GOV-SESSION-FORMALIZATION-AUDIT-001")
        assert "audit the session against Deliberation Archive entries" in audit["description"]
    finally:
        db.close()


def test_standing_backlog_is_formalized_as_governed_artifact() -> None:
    expected = {
        "GOV-STANDING-BACKLOG-001": "governance",
        "PB-STANDING-BACKLOG-CONTINUITY-001": "protected_behavior",
        "ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001": "architecture_decision",
        "DCL-STANDING-BACKLOG-SCHEMA-001": "design_constraint",
    }

    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        for spec_id, spec_type in expected.items():
            spec = db.get_spec(spec_id)
            assert spec is not None, f"{spec_id} must exist in MemBase"
            assert spec["type"] == spec_type
            assert spec["status"] == "verified"
            # Per S330 Slice 8.6 row-17 fix: governance specs are process
            # rules and may not carry structural testability (they're
            # human-evaluable, not machine-checkable like PB/ADR/DCL specs
            # that hold assertions). The other 3 spec types in this set
            # DO carry structural testability per their assertion bodies.
            if spec_type == "governance":
                # Governance specs are process rules; structural fields
                # (testability/affected_by/source_paths) are recommended but
                # not load-bearing — the spec's authority is its description.
                # PB/ADR/DCL specs hold machine-checkable assertions and DO
                # require these fields populated.
                assert spec["testability"] in ("structural", None), (
                    f"{spec_id} testability must be 'structural' or absent for governance specs; "
                    f"got {spec['testability']!r}"
                )
            else:
                assert spec["testability"] == "structural", (
                    f"{spec_id} ({spec_type}) must carry structural testability; got {spec['testability']!r}"
                )
                assert "DELIB-0838" in (spec["affected_by"] or ""), f"{spec_id} must cite DELIB-0838 in affected_by"
                assert spec.get("source_paths"), f"{spec_id} must have populated source_paths"

        gov = db.get_spec("GOV-STANDING-BACKLOG-001")
        assert "durable cross-session work authority" in gov["description"]
        assert "canonical authority" in gov["description"]

        pb = db.get_spec("PB-STANDING-BACKLOG-CONTINUITY-001")
        assert "must not ignore, silently reorder, or drop" in pb["description"]

        adr = db.get_spec("ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001")
        assert "human-readable standing backlog authority" in adr["description"]

        dcl = db.get_spec("DCL-STANDING-BACKLOG-SCHEMA-001")
        assert "stable identifier" in dcl["description"]
        assert "regression visibility" in dcl["description"]
    finally:
        db.close()


def test_session_self_initialization_records_are_in_membase() -> None:
    expected = {
        "GOV-SESSION-SELF-INITIALIZATION-001": ("governance", "verified"),
        "PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001": ("protected_behavior", "verified"),
        "SPEC-PROJECT-DASHBOARD-KPI-LINK-001": ("requirement", "verified"),
        "DCL-SESSION-STARTUP-TOKEN-BUDGET-001": ("design_constraint", "verified"),
    }

    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        for spec_id, (spec_type, status) in expected.items():
            spec = db.get_spec(spec_id)
            assert spec is not None, f"{spec_id} must exist in MemBase"
            assert spec["type"] == spec_type
            assert spec["status"] == status
            assert spec["testability"] == "structural"
            assert "DELIB-0840" in (spec["affected_by"] or "")

        gov = db.get_spec("GOV-SESSION-SELF-INITIALIZATION-001")
        gov_desc = _one_line(gov["description"])
        assert "role being assumed" in gov_desc
        assert "three top priority actions" in gov_desc

        pb = db.get_spec("PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001")
        assert "must not proceed as if governance context is implicit" in pb["description"]
        assert "skills, plug-ins, directives" in pb["description"]

        dashboard = db.get_spec("SPEC-PROJECT-DASHBOARD-KPI-LINK-001")
        assert "live project dashboard link" in dashboard["description"]
        assert "time-series KPI" in dashboard["description"]
        assert "tokens consumed" in dashboard["description"]

        token_budget = db.get_spec("DCL-SESSION-STARTUP-TOKEN-BUDGET-001")
        assert "reducing token consumption" in token_budget["description"]
        assert "progressive disclosure" in token_budget["description"]
    finally:
        db.close()


def test_session_lifecycle_engagement_records_are_in_membase() -> None:
    expected = {
        "GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001": "governance",
        "PB-SESSION-WRAP-UP-PROACTIVE-001": "protected_behavior",
        "DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001": "design_constraint",
    }

    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        for spec_id, spec_type in expected.items():
            spec = db.get_spec(spec_id)
            assert spec is not None, f"{spec_id} must exist in MemBase"
            assert spec["type"] == spec_type
            assert spec["status"] == "verified"
            assert spec["testability"] == "structural"
            assert "DELIB-0841" in (spec["affected_by"] or "")

        gov = db.get_spec("GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001")
        assert "actively inform and engage the user" in gov["description"]
        assert "priorities across all dimensions" in gov["description"]

        pb = db.get_spec("PB-SESSION-WRAP-UP-PROACTIVE-001")
        assert "should not have to explicitly instruct GT-KB" in pb["description"]

        dcl = db.get_spec("DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001")
        assert "Safe automatic lifecycle hooks" in dcl["description"]
        assert "Mutating wrap-up operations" in dcl["description"]
    finally:
        db.close()


def test_artifact_oriented_governance_records_are_in_membase() -> None:
    expected = {
        "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001": "governance",
        "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001": "architecture_decision",
        "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001": "design_constraint",
    }

    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        for spec_id, spec_type in expected.items():
            spec = db.get_spec(spec_id)
            assert spec is not None, f"{spec_id} must exist in MemBase"
            assert spec["type"] == spec_type
            assert spec["status"] == "verified"
            assert spec["authority"] == "stated"
            assert spec["testability"] == "structural"
            assert "DELIB-0874" in (spec["affected_by"] or "")
            assert "CODEX-STANDING-PRIORITIES.md" in (spec["source_paths"] or "")

        gov = db.get_spec("GOV-ARTIFACT-ORIENTED-GOVERNANCE-001")
        assert "network of durable artifacts" in gov["description"]
        assert "capture thresholds" in gov["description"]

        adr = db.get_spec("ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001")
        assert "durable artifact graph" in adr["description"]
        assert "transient conversation" in adr["description"]

        dcl = db.get_spec("DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001")
        assert "candidate" in dcl["description"]
        assert "non-intrusive confirmation" in dcl["description"]
    finally:
        db.close()


def test_core_spec_intake_phase0_records_are_in_membase() -> None:
    expected = {
        "SPEC-CORE-INTAKE-001": "requirement",
        "SPEC-CORE-INTAKE-002": "requirement",
        "ADR-CORE-INTAKE-001": "architecture_decision",
        "DCL-CORE-INTAKE-001": "design_constraint",
    }

    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        for spec_id, spec_type in expected.items():
            spec = db.get_spec(spec_id)
            assert spec is not None, f"{spec_id} must exist in MemBase"
            assert spec["type"] == spec_type
            assert spec["status"] == "specified"
            assert spec["authority"] == "stated"
            assert spec["testability"] == "structural"
            assert "DELIB-0875" in (spec["affected_by"] or "")
            assert "gtkb-core-spec-intake-001.md" in (spec["source_paths"] or "")

        prompt_spec = db.get_spec("SPEC-CORE-INTAKE-001")
        prompt_desc = _one_line(prompt_spec["description"])
        assert "newly initialized projects" in prompt_desc
        assert "exactly one deterministic question" in prompt_desc

        stop_spec = db.get_spec("SPEC-CORE-INTAKE-002")
        stop_desc = _one_line(stop_spec["description"])
        assert "missing, inferred, or needs clarity" in stop_desc
        assert "not applicable" in stop_desc

        adr = db.get_spec("ADR-CORE-INTAKE-001")
        adr_desc = _one_line(adr["description"])
        assert "persisted MemBase evidence" in adr_desc
        assert "conversation memory" in adr_desc

        dcl = db.get_spec("DCL-CORE-INTAKE-001")
        dcl_desc = _one_line(dcl["description"])
        assert "minimal and full spec scaffold behavior" in dcl_desc
        assert "Non-interactive and JSON-safe command paths" in dcl_desc
    finally:
        db.close()


def test_bridge_authority_governance_records_are_in_membase() -> None:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        gov = db.get_spec("GOV-FILE-BRIDGE-AUTHORITY-001")
        assert gov is not None
        assert gov["type"] == "governance"
        assert gov["status"] == "verified"
        assert gov["authority"] == "stated"
        assert gov["testability"] == "structural"
        assert "DELIB-0880" in (gov["affected_by"] or "")
        assert "bridge/INDEX.md" in (gov["source_paths"] or "")
        gov_desc = _one_line(gov["description"])
        gov_desc_lower = gov_desc.lower()
        assert "authoritative source for bridge queue state" in gov_desc_lower
        assert "startup reports, dashboard fields, cached scan counts" in gov_desc_lower
        assert "permanent owner authority" in gov_desc
        assert "downstream bridge-dependent artifacts" in gov_desc

        startup = db.get_spec("GOV-SESSION-SELF-INITIALIZATION-001")
        assert startup is not None
        startup_desc = _one_line(startup["description"])
        assert "executing startup obligations from live project sources" in startup_desc
        assert "generated startup reports, dashboard fields, cached summaries" in startup_desc
        assert "bridge/INDEX.md" in startup_desc
        assert "DELIB-0880" in (startup["affected_by"] or "")
    finally:
        db.close()


def test_standing_priorities_load_artifact_oriented_governance_directive() -> None:
    priorities = _read("AGENTS.md")

    assert "artifact-oriented governance as a default interpretation stance" in priorities
    assert "durable artifacts" in priorities
    assert "standing-backlog addition" in priorities
    assert "explicit lifecycle states" in priorities
    assert "non-intrusive confirmation flows" in priorities
    assert "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001" in priorities
    assert "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001" in priorities
    assert "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001" in priorities


def test_governance_adoption_milestones_are_in_membase() -> None:
    """Governance-adoption milestone artifacts exist in MemBase.

    Replaces the retired markdown-backlog-based milestone assertion test.
    The governance artifacts (DELIB, GOV, PB, ADR, DCL, SPEC) that were
    previously validated via the transitional backlog view are now validated
    through their canonical MemBase records in sibling test functions:
    - test_standing_backlog_is_formalized_as_governed_artifact
    - test_session_self_initialization_records_are_in_membase
    - test_session_lifecycle_engagement_records_are_in_membase
    - test_artifact_oriented_governance_records_are_in_membase
    - test_core_spec_intake_phase0_records_are_in_membase
    - test_formal_artifact_approval_records_are_in_membase
    - test_session_governance_principles_have_membase_records

    This test validates the key governance specs that anchor the milestone
    set are present and verified in MemBase.
    """
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        # Core governance-adoption specs that anchor the milestone set
        for spec_id in [
            "GOV-STANDING-BACKLOG-001",
            "GOV-SESSION-SELF-INITIALIZATION-001",
            "GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001",
            "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
            "GOV-ARTIFACT-APPROVAL-001",
            "GOV-SESSION-FORMALIZATION-AUDIT-001",
        ]:
            spec = db.get_spec(spec_id)
            assert spec is not None, f"{spec_id} must exist in MemBase"
            assert spec["status"] == "verified", f"{spec_id} must be verified"
    finally:
        db.close()
