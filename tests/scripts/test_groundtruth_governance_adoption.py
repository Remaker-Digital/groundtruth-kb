"""Regression checks for Agent Red's GroundTruth-KB governance adoption."""

from __future__ import annotations

import json
import subprocess
import tomllib
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _load_toml(path: str) -> dict:
    return tomllib.loads(_read(path))


def _assert_not_git_ignored(paths: list[str]) -> None:
    ignored: list[str] = []
    for path in paths:
        result = subprocess.run(
            ["git", "check-ignore", "-q", path],
            cwd=REPO_ROOT,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            ignored.append(path)
    assert not ignored, f"GroundTruth governance artifacts are still git-ignored: {ignored}"


def test_groundtruth_adopter_profile_is_pinned() -> None:
    config = _load_toml("groundtruth.toml")

    assert config["groundtruth"]["db_path"] == "groundtruth.db"
    assert config["project"]["project_name"] == "Agent Red Customer Experience"
    assert config["project"]["owner"] == "Remaker Digital"
    assert config["project"]["profile"] == "dual-agent"
    assert config["project"]["cloud_provider"] == "azure"
    assert config["project"]["scaffold_version"] == "0.6.1"


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


def test_groundtruth_governance_artifacts_are_present_and_not_ignored() -> None:
    required_paths = [
        ".groundtruth/formal-artifact-approvals/2026-04-20-codex-hook-parity-decision.json",
        ".groundtruth/formal-artifact-approvals/2026-04-20-session-formalization-audit-batch.json",
        ".groundtruth/formal-artifact-approvals/2026-04-20-standing-backlog-harvest.json",
        ".groundtruth/formal-artifact-approvals/2026-04-20-standing-backlog-formalization.json",
        ".groundtruth/formal-artifact-approvals/2026-04-20-session-self-initialization-directive.json",
        ".groundtruth/formal-artifact-approvals/2026-04-20-session-lifecycle-engagement-principle.json",
        ".groundtruth/formal-artifact-approvals/2026-04-20-gtkb-gov-011-implementation-verification.json",
        ".codex/config.toml",
        ".codex/hooks.json",
        ".claude/settings.json",
        ".claude/hooks/assertion-check.py",
        ".claude/hooks/credential-scan.py",
        ".claude/hooks/destructive-gate.py",
        ".claude/hooks/formal-artifact-approval-gate.py",
        ".claude/hooks/poller-freshness.py",
        ".claude/hooks/scheduler.py",
        ".claude/hooks/spec-classifier.py",
        ".claude/rules/bridge-essential.md",
        ".claude/rules/acting-prime-builder.md",
        ".claude/rules/codex-review-gate.md",
        ".claude/rules/deliberation-protocol.md",
        ".claude/rules/file-bridge-protocol.md",
        ".claude/rules/loyal-opposition.md",
        ".claude/rules/report-depth-prime-builder-context.md",
        ".claude/skills/alternatives-investigation/SKILL.md",
        ".claude/skills/arch-audit/SKILL.md",
        ".claude/skills/check-deliberations/SKILL.md",
        ".claude/skills/code-review-audit/SKILL.md",
        ".claude/skills/codex-report/SKILL.md",
        ".claude/skills/bridge-propose/SKILL.md",
        ".claude/skills/bridge-propose/helpers/write_bridge.py",
        ".claude/skills/decision-capture/SKILL.md",
        ".claude/skills/decision-capture/helpers/record_decision.py",
        ".claude/skills/deploy/SKILL.md",
        ".claude/skills/kb-adr/SKILL.md",
        ".claude/skills/kb-assert/SKILL.md",
        ".claude/skills/kb-batch/SKILL.md",
        ".claude/skills/kb-promote/SKILL.md",
        ".claude/skills/kb-query/SKILL.md",
        ".claude/skills/kb-session-wrap/SKILL.md",
        ".claude/skills/kb-spec/SKILL.md",
        ".claude/skills/kb-work-item/SKILL.md",
        ".claude/skills/proposal-review/SKILL.md",
        ".claude/skills/release-candidate-gate/SKILL.md",
        ".claude/skills/run-tests/SKILL.md",
        ".claude/skills/seed-tenant/SKILL.md",
        ".claude/skills/send-review/SKILL.md",
        ".claude/skills/spec-intake/SKILL.md",
        ".claude/skills/spec-intake/helpers/spec_intake.py",
        "scripts/check_codex_hook_parity.py",
        "scripts/session_self_initialization.py",
        "docs/gtkb-dashboard/index.html",
        "docs/gtkb-dashboard/dashboard-data.json",
        "docs/gtkb-dashboard/session-startup-report.md",
        "docs/gtkb-dashboard/session-wrapup-report.md",
        "memory/gtkb-dashboard-history.json",
        "scripts/audit_standing_backlog_sources.py",
        "tests/scripts/test_codex_hook_parity.py",
        "tests/scripts/test_session_self_initialization.py",
        "tests/scripts/test_standing_backlog_harvest.py",
        "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-04-20.md",
    ]

    missing = [path for path in required_paths if not (REPO_ROOT / path).is_file()]
    assert not missing, f"Missing GroundTruth governance artifacts: {missing}"
    _assert_not_git_ignored(required_paths)


def test_project_settings_registers_bridge_visibility_hook() -> None:
    settings = json.loads(_read(".claude/settings.json"))

    prompt_commands = [
        hook["command"]
        for group in settings["hooks"]["UserPromptSubmit"]
        for hook in group["hooks"]
    ]
    pre_tool_commands = [
        hook["command"]
        for group in settings["hooks"]["PreToolUse"]
        for hook in group["hooks"]
    ]

    assert any("poller-freshness.py" in command for command in prompt_commands)
    assert any("formal-artifact-approval-gate.py" in command for command in pre_tool_commands)
    assert any(
        "session_self_initialization.py" in hook["command"]
        and "--emit-report" in hook["command"]
        and "--fast-hook" in hook["command"]
        for group in settings["hooks"]["SessionStart"]
        for hook in group["hooks"]
    )
    assert any(
        "session_self_initialization.py" in hook["command"]
        and "--emit-wrapup" in hook["command"]
        and "--fast-hook" in hook["command"]
        for group in settings["hooks"]["Stop"]
        for hook in group["hooks"]
    )


def test_codex_config_registers_formal_artifact_approval_hook_intent() -> None:
    config = _load_toml(".codex/config.toml")
    hooks = json.loads(_read(".codex/hooks.json"))

    assert config["features"]["codex_hooks"] is True
    pre_tool_groups = hooks["hooks"]["PreToolUse"]
    formal_groups = [
        group
        for group in pre_tool_groups
        if any("formal-artifact-approval.cmd" in hook["command"] for hook in group["hooks"])
    ]
    assert formal_groups
    assert all(group["matcher"] == "Bash" for group in formal_groups)
    assert any(
        "agent-red-hooks" in hook["command"]
        and "formal-artifact-approval.cmd" in hook["command"]
        for group in formal_groups
        for hook in group["hooks"]
    )
    assert any(
        "agent-red-hooks" in hook["command"]
        and "session_start_dispatch.py" in hook["command"]
        for group in hooks["hooks"]["SessionStart"]
        for hook in group["hooks"]
    )
    assert any(
        "agent-red-hooks" in hook["command"]
        and "session_wrapup_trigger_dispatch.py" in hook["command"]
        for group in hooks["hooks"]["UserPromptSubmit"]
        for hook in group["hooks"]
    )
    assert "Stop" not in hooks["hooks"]


def test_release_candidate_gate_runs_governance_adoption_tests() -> None:
    gate = _read("scripts/release_candidate_gate.py")

    assert "tests/scripts/test_session_self_initialization.py" in gate
    assert "tests/scripts/test_groundtruth_governance_adoption.py" in gate
    assert "tests/scripts/test_codex_hook_parity.py" in gate
    assert "tests/scripts/test_standing_backlog_harvest.py" in gate
    assert "tests/hooks/test_formal_artifact_approval_gate.py" in gate
    assert "scripts/check_codex_hook_parity.py" in gate


def test_release_candidate_gate_workflow_has_python_and_frontend_lanes() -> None:
    workflow = _read(".github/workflows/release-candidate-gate.yml")

    assert "--require-python 3.12 --skip-frontend" in workflow
    assert "--skip-python --include-frontend" in workflow
    assert "windows-latest" in workflow


def test_release_candidate_skill_documents_mem_and_da_evidence() -> None:
    skill = _read(".claude/skills/release-candidate-gate/SKILL.md")

    assert "scripts/release_candidate_gate.py" in skill
    assert "--require-python 3.12" in skill
    assert "MemBase" in skill
    assert "Deliberation Archive" in skill


def test_acting_prime_builder_rule_maps_prime_skill_labels_to_assigned_role() -> None:
    rule = _read(".claude/rules/acting-prime-builder.md")

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
    assert "When GroundTruth-KB is installed" in rule
    assert "fully configured for the role of Prime Builder" in rule
    assert "configuration should be" in rule
    assert "prepared for all capable harnesses" in rule
    assert "The owner assigns the Prime Builder role" in rule
    assert "not Prime Builder" in rule
    assert "DELIB-0834" in rule
    assert "GOV-AGENT-RED-GTKB-CONFORMANCE-001" in rule
    assert "Agent Red is a well-behaved" in rule
    assert "fully-conformant application" in rule
    assert "supported and sustained by GroundTruth-KB" in rule
    assert "not be treated as an ad hoc exception" in rule
    assert "Release-readiness work should preserve and enforce GT-KB" in rule
    assert "documented, and regression-tested where possible" in rule
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
    assert "owner-assigned active AI harness assumes the Prime Builder role" in rule
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
    assert "memory/work_list.md" in rule
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
            assert "DELIB-0835" in (spec["affected_by"] or "")

        gov = db.get_spec("GOV-ARTIFACT-APPROVAL-001")
        assert "native review format" in gov["description"]
        assert "Auto-approval does not remove" in gov["description"]
        assert "verified" == gov["status"]

        pb = db.get_spec("PB-ARTIFACT-APPROVAL-001")
        assert "approval or acknowledgement evidence" in pb["description"]
        assert "session transcript" in pb["description"]

        adr = db.get_spec("ADR-ARTIFACT-FORMALIZATION-GATE-001")
        assert "scoped auto-approval state" in adr["description"]

        dcl = db.get_spec("DCL-ARTIFACT-APPROVAL-HOOK-001")
        assert "full proposed content hash" in dcl["description"]
        assert "preserve it in the session transcript" in dcl["description"]
    finally:
        db.close()


def test_codex_hook_limitation_decision_is_archived() -> None:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        decision = db.get_deliberation("DELIB-0836")
        assert decision is not None
        assert decision["outcome"] == "owner_decision"
        assert decision["source_type"] == "owner_conversation"
        assert "Codex hooks are currently disabled on Windows" in decision["content"]
        assert "scripts/check_codex_hook_parity.py" in decision["content"]
        assert "live Windows interception boundary" in decision["content"]
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
            assert spec["testability"] == "structural"
            for delib_id in delib_ids:
                assert delib_id in (spec["affected_by"] or "")

        conformance = db.get_spec("GOV-AGENT-RED-GTKB-CONFORMANCE-001")
        assert "well-behaved, fully conformant" in conformance["description"]

        codex_fallback = db.get_spec("ADR-CODEX-HOOK-PARITY-FALLBACK-001")
        assert "not represent .codex/hooks.json as a live Windows interception boundary" in codex_fallback["description"]

        audit = db.get_spec("GOV-SESSION-FORMALIZATION-AUDIT-001")
        assert "audit the session against Deliberation Archive entries" in audit["description"]
    finally:
        db.close()


def test_session_formalization_audit_is_archived() -> None:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        audit = db.get_deliberation("DELIB-0837")
        assert audit is not None
        assert audit["outcome"] == "informational"
        assert "DELIB-0828" in audit["content"]
        assert "DELIB-0836" in audit["content"]
        assert "GOV-SESSION-FORMALIZATION-AUDIT-001" in audit["content"]
        assert "Residual scope notes" in audit["content"]
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
            assert spec["testability"] == "structural"
            assert "DELIB-0838" in (spec["affected_by"] or "")
            assert "memory/work_list.md" in (spec["source_paths"] or "")

        gov = db.get_spec("GOV-STANDING-BACKLOG-001")
        assert "durable cross-session queue" in gov["description"]
        assert "Future sessions must inspect the standing backlog" in gov["description"]

        pb = db.get_spec("PB-STANDING-BACKLOG-CONTINUITY-001")
        assert "must not ignore, silently reorder, or drop" in pb["description"]

        adr = db.get_spec("ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001")
        assert "human-readable standing backlog authority" in adr["description"]

        dcl = db.get_spec("DCL-STANDING-BACKLOG-SCHEMA-001")
        assert "stable identifier" in dcl["description"]
        assert "regression visibility" in dcl["description"]
    finally:
        db.close()


def test_standing_backlog_decision_is_archived() -> None:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        decision = db.get_deliberation("DELIB-0838")
        assert decision is not None
        assert decision["outcome"] == "owner_decision"
        assert "treated like other GroundTruth-KB specifications" in decision["content"]
        assert "Individual backlog entries remain queue/work items" in decision["content"]
        assert "Future sessions must inspect the standing backlog" in decision["content"]
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
        assert "role being assumed" in gov["description"]
        assert "three top priority actions" in gov["description"]

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


def test_session_self_initialization_decision_is_archived() -> None:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        decision = db.get_deliberation("DELIB-0840")
        assert decision is not None
        assert decision["outcome"] == "owner_decision"
        assert decision["source_type"] == "owner_conversation"
        assert "role being assumed" in decision["content"]
        assert "live link to the project dashboard" in decision["content"]
        assert "three top priority actions" in decision["content"]
        assert "reducing token consumption" in decision["content"]
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


def test_session_lifecycle_engagement_decisions_are_archived() -> None:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        decision = db.get_deliberation("DELIB-0841")
        assert decision is not None
        assert decision["outcome"] == "owner_decision"
        assert "should not have to explicitly instruct GT-KB" in decision["content"]
        assert "priorities across all dimensions" in decision["content"]
        assert "simplify user input" in decision["content"]

        implementation = db.get_deliberation("DELIB-0842")
        assert implementation is not None
        assert implementation["outcome"] == "informational"
        assert "GTKB-GOV-011" in implementation["content"]
        assert "session_self_initialization.py" in implementation["content"]
    finally:
        db.close()


def test_work_queue_prioritizes_candidate_skill_and_doctor_items() -> None:
    work_list = _read("memory/work_list.md")

    strict_gate = work_list.index("GTKB-GOV-000")
    session_start = work_list.index("GTKB-GOV-011")
    first_insert = work_list.index("GTKB-GOV-001")
    prior_item = work_list.index("DA-gov dispatch loop")
    assert strict_gate < first_insert
    assert strict_gate < session_start < first_insert
    assert first_insert < prior_item
    assert "GTKB-GOV-000 — DONE" in work_list
    assert "strict formal artifact approval gate" in work_list
    assert "scoped auto-approval mode" in work_list
    assert "transcript capture" in work_list
    assert ".groundtruth/formal-artifact-approvals/2026-04-20-strict-gov-enforcement-verified.json" in work_list
    assert "GTKB-GOV-000A" in work_list
    assert "Codex hook parity package" in work_list
    assert "check_codex_hook_parity.py" in work_list
    assert "DELIB-0836" in work_list
    assert "2026-04-20-codex-hook-parity-decision.json" in work_list
    assert "GTKB-GOV-000B" in work_list
    assert "DELIB-0837" in work_list
    assert "GOV-SESSION-FORMALIZATION-AUDIT-001" in work_list
    assert "2026-04-20-session-formalization-audit-batch.json" in work_list
    assert "GTKB-GOV-000C" in work_list
    assert "DELIB-0838" in work_list
    assert "GOV-STANDING-BACKLOG-001" in work_list
    assert "PB-STANDING-BACKLOG-CONTINUITY-001" in work_list
    assert "ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001" in work_list
    assert "DCL-STANDING-BACKLOG-SCHEMA-001" in work_list
    assert "Individual backlog entries remain queue/work items" in work_list
    assert "2026-04-20-standing-backlog-formalization.json" in work_list
    assert "GTKB-GOV-011" in work_list
    assert "DONE" in work_list[work_list.index("GTKB-GOV-011"):work_list.index("GTKB-GOV-001")]
    assert "DELIB-0840" in work_list
    assert "DELIB-0841" in work_list
    assert "GOV-SESSION-SELF-INITIALIZATION-001" in work_list
    assert "GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001" in work_list
    assert "PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001" in work_list
    assert "PB-SESSION-WRAP-UP-PROACTIVE-001" in work_list
    assert "SPEC-PROJECT-DASHBOARD-KPI-LINK-001" in work_list
    assert "DCL-SESSION-STARTUP-TOKEN-BUDGET-001" in work_list
    assert "DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001" in work_list
    assert "live project dashboard link" in work_list
    assert "time-series KPI" in work_list
    assert "three top priority user actions" in work_list
    assert "token-budget" in work_list
    assert "GTKB-GOV-002" in work_list
    assert "release-candidate gate" in work_list
    assert "GTKB-GOV-003" in work_list
    assert "governance-adoption doctor" in work_list
