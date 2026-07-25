NEW
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-09-14Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Sweep S4: fix ~25 broken and ~10 silent false-green skill-rename tests

bridge_kind: prime_proposal
Document: gtkb-wi5665-skill-rename-test-recovery
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","coverage":"explicit_list","included_work_item_count":7,"specificity_rank":[1,7],"selected":true}]
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5665

target_paths: ["groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_upgrade_skills.py", "groundtruth-kb/tests/framework/test_bash_enforcement_parser.py", "platform_tests/scripts/test_harness_skill_effectiveness.py", "platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py", "platform_tests/scripts/test_gitattributes_lf_policy.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py", "platform_tests/skills/test_bridge_impl_report_helper.py", "platform_tests/skills/test_skill_catalog_contract.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "platform_tests/skills/test_verify_skill_scaffolding.py", "platform_tests/skills/test_bridge_propose_helper.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py", "platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py", "platform_tests/scripts/test_bridge_compliance_gate_disposition.py", "platform_tests/scripts/test_check_legacy_harness_language.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "platform_tests/scripts/test_fab14_directive_hook_coverage.py", "platform_tests/scripts/test_fab14_path_token_dedup.py", "platform_tests/scripts/test_groundtruth_governance_adoption.py", "platform_tests/scripts/test_no_tracked_pyc_artifacts.py", "platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py", "platform_tests/scripts/test_scan_bridge.py", "platform_tests/scripts/test_self_review_write_time_gate.py", "platform_tests/scripts/test_show_thread_bridge.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "platform_tests/skills/test_protected_write_helper.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair WI-5665 broken and false-green skill-rename tests by separating intentional negative literals from stale runtime/fixture expectations and restoring canonical cross-harness coverage.

Work item description: _No work item description supplied._

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5665` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/tests/test_managed_registry.py`, `groundtruth-kb/tests/test_upgrade_skills.py`, `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`, `platform_tests/scripts/test_harness_skill_effectiveness.py`, `platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py`, `platform_tests/scripts/test_gitattributes_lf_policy.py`, `platform_tests/scripts/test_cross_harness_protocol_parity.py`, `platform_tests/skills/test_bridge_impl_report_helper.py`, `platform_tests/skills/test_skill_catalog_contract.py`, `platform_tests/skills/test_verified_finalization_validation_hardening.py`, `platform_tests/skills/test_verify_skill_scaffolding.py`, `platform_tests/skills/test_bridge_propose_helper.py`, `platform_tests/scripts/test_gtkb_bridge_writer.py`, `platform_tests/scripts/test_generate_codex_skill_adapters.py`, `platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py`, `platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py`, `platform_tests/scripts/test_bridge_compliance_gate_disposition.py`, `platform_tests/scripts/test_check_legacy_harness_language.py`, `platform_tests/scripts/test_check_protected_commit_authorization.py`, `platform_tests/scripts/test_fab14_directive_hook_coverage.py`, `platform_tests/scripts/test_fab14_path_token_dedup.py`, `platform_tests/scripts/test_groundtruth_governance_adoption.py`, `platform_tests/scripts/test_no_tracked_pyc_artifacts.py`, `platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py`, `platform_tests/scripts/test_scan_bridge.py`, `platform_tests/scripts/test_self_review_write_time_gate.py`, `platform_tests/scripts/test_show_thread_bridge.py`, `platform_tests/scripts/test_verify_antigravity_dispatch.py`, `platform_tests/skills/test_protected_write_helper.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202667018` - LO Review - WI-5370 No-Responds Repair REVISED Proposal (wi5395-tamper-diagnostic-acceptance-residue) - Retired Archive Target
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` - Process the eight most recent skill-rename work items
- `DELIB-202667093` - LO Verification: GFR Slice D — Drift & generator hygiene
- `DELIB-202666151` - WI-5200..5202 Narrow Harness Repair - Loyal Opposition Post-Implementation Verification: VERIFIED
- `DELIB-202666154` - WI-5200..5202 Narrow Harness Repair — Loyal Opposition Post-Implementation Verification

## Owner Decisions / Input

- `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION` - active project authorization covering `WI-5665`.

## Proposed Scope

- Classify each old skill-path literal: retain only named negative-input cases, and update every load, expected managed file, fixture tree, adapter expectation, or command example to the canonical gtkb-* path.
- Restore tests that resolve or create the actual canonical helper and managed artifacts so they fail if only retired paths are present.
- Quarantine existing unowned modifications in platform_tests/skills/test_bridge_propose_helper.py, platform_tests/scripts/test_gtkb_bridge_writer.py, and platform_tests/scripts/test_generate_codex_skill_adapters.py; do not stage or attribute their current hunks.

## Cross-Harness Disposition

- **Claude/Codex/Antigravity/API harness**: Use canonical gtkb-* source, adapter, and generated-template path expectations; preserve a legacy spelling only when the test explicitly proves detection or migration behavior.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5665; PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "WI-5665 has no implemented behavior yet; this proposal defines the slice.",
  "after_behavior": "Repair WI-5665 broken and false-green skill-rename tests by separating intentional negative literals from stale runtime/fixture expectations and restoring canonical cross-harness coverage.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5665",
    "project": "GTKB-SKILL-RENAME-REFERENCE-SWEEP",
    "target_paths": [
      "groundtruth-kb/tests/test_managed_registry.py",
      "groundtruth-kb/tests/test_upgrade_skills.py",
      "groundtruth-kb/tests/framework/test_bash_enforcement_parser.py",
      "platform_tests/scripts/test_harness_skill_effectiveness.py",
      "platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py",
      "platform_tests/scripts/test_gitattributes_lf_policy.py",
      "platform_tests/scripts/test_cross_harness_protocol_parity.py",
      "platform_tests/skills/test_bridge_impl_report_helper.py",
      "platform_tests/skills/test_skill_catalog_contract.py",
      "platform_tests/skills/test_verified_finalization_validation_hardening.py",
      "platform_tests/skills/test_verify_skill_scaffolding.py",
      "platform_tests/skills/test_bridge_propose_helper.py",
      "platform_tests/scripts/test_gtkb_bridge_writer.py",
      "platform_tests/scripts/test_generate_codex_skill_adapters.py",
      "platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py",
      "platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py",
      "platform_tests/scripts/test_bridge_compliance_gate_disposition.py",
      "platform_tests/scripts/test_check_legacy_harness_language.py",
      "platform_tests/scripts/test_check_protected_commit_authorization.py",
      "platform_tests/scripts/test_fab14_directive_hook_coverage.py",
      "platform_tests/scripts/test_fab14_path_token_dedup.py",
      "platform_tests/scripts/test_groundtruth_governance_adoption.py",
      "platform_tests/scripts/test_no_tracked_pyc_artifacts.py",
      "platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py",
      "platform_tests/scripts/test_scan_bridge.py",
      "platform_tests/scripts/test_self_review_write_time_gate.py",
      "platform_tests/scripts/test_show_thread_bridge.py",
      "platform_tests/scripts/test_verify_antigravity_dispatch.py",
      "platform_tests/skills/test_protected_write_helper.py"
    ],
    "linked_specifications": [
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"
    ]
  },
  "expected_result": {
    "summary": "Repair WI-5665 broken and false-green skill-rename tests by separating intentional negative literals from stale runtime/fixture expectations and restoring canonical cross-harness coverage.",
    "scope": [
      "Classify each old skill-path literal: retain only named negative-input cases, and update every load, expected managed file, fixture tree, adapter expectation, or command example to the canonical gtkb-* path.",
      "Restore tests that resolve or create the actual canonical helper and managed artifacts so they fail if only retired paths are present.",
      "Quarantine existing unowned modifications in platform_tests/skills/test_bridge_propose_helper.py, platform_tests/scripts/test_gtkb_bridge_writer.py, and platform_tests/scripts/test_generate_codex_skill_adapters.py; do not stage or attribute their current hunks."
    ],
    "acceptance_criteria": [
      "Every production-facing path assertion and temporary fixture that models a managed skill resolves the gtkb-* path and rejects the retired path.",
      "Intentional legacy-input parser/detector fixtures are explicitly limited to negative cases and assert canonical output or rejection behavior.",
      "No recovery commit includes an unowned dirty hunk; all modified test paths have a clean governed baseline and a focused test run."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Every production-facing path assertion and temporary fixture that models a managed skill resolves the gtkb-* path and rejects the retired path.
- Intentional legacy-input parser/detector fixtures are explicitly limited to negative cases and assert canonical output or rejection behavior.
- No recovery commit includes an unowned dirty hunk; all modified test paths have a clean governed baseline and a focused test run.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/tests/test_managed_registry.py`
- `groundtruth-kb/tests/test_upgrade_skills.py`
- `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`
- `platform_tests/scripts/test_harness_skill_effectiveness.py`
- `platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py`
- `platform_tests/scripts/test_gitattributes_lf_policy.py`
- `platform_tests/scripts/test_cross_harness_protocol_parity.py`
- `platform_tests/skills/test_bridge_impl_report_helper.py`
- `platform_tests/skills/test_skill_catalog_contract.py`
- `platform_tests/skills/test_verified_finalization_validation_hardening.py`
- `platform_tests/skills/test_verify_skill_scaffolding.py`
- `platform_tests/skills/test_bridge_propose_helper.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`
- `platform_tests/scripts/test_generate_codex_skill_adapters.py`
- `platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py`
- `platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py`
- `platform_tests/scripts/test_bridge_compliance_gate_disposition.py`
- `platform_tests/scripts/test_check_legacy_harness_language.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `platform_tests/scripts/test_fab14_directive_hook_coverage.py`
- `platform_tests/scripts/test_fab14_path_token_dedup.py`
- `platform_tests/scripts/test_groundtruth_governance_adoption.py`
- `platform_tests/scripts/test_no_tracked_pyc_artifacts.py`
- `platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py`
- `platform_tests/scripts/test_scan_bridge.py`
- `platform_tests/scripts/test_self_review_write_time_gate.py`
- `platform_tests/scripts/test_show_thread_bridge.py`
- `platform_tests/scripts/test_verify_antigravity_dispatch.py`
- `platform_tests/skills/test_protected_write_helper.py`

## Recommended Commit Type

`feat`
