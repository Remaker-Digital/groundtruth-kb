NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Sweep S4: fix ~25 broken and ~10 silent false-green skill-rename tests

bridge_kind: prime_proposal
Document: gtkb-wi5665-cursor-fallback-hardening-test-repair
Version: 001
Date: 2026-07-29 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","coverage":"explicit_list","included_work_item_count":7,"specificity_rank":[1,7],"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"selected","selected":true},{"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724","coverage":"not_covering","included_work_item_count":1,"specificity_rank":null,"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"not_covering","selected":false}]
Project Authorization Decision: {"actor":{"role":"prime-builder","session_context_id":"019f9329-a174-7763-8f7e-29679f39e6bd"},"allowed":true,"authorization":{"allowed_mutation_classes":["source","test","configuration","documentation","governance_evidence","runtime_state","repository_metadata"],"excluded_spec_ids":[],"excluded_work_item_ids":[],"forbidden_operations":["external_system_mutation","dispatcher_mutation","credential_or_secret_mutation","push"],"id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","included_spec_ids":["GOV-FILE-BRIDGE-AUTHORITY-001"],"included_work_item_ids":["WI-5662","WI-5663","WI-5664","WI-5665","WI-5666","WI-5667","WI-5668"],"normalized_envelope_hash":"E8CAA986676F3DD9304D1B3218CC70ABA4BBBCB1E784D0628AB1D2BD9F246BF8","normalized_expiry":null,"owner_decision_deliberation_id":"DELIB-202667193","owner_decision_snapshot":{"id":"DELIB-202667193","outcome":"owner_decision","source_type":"owner_conversation","version":1},"status":"active","supersession_state":"current","version":1},"classified_targets":[{"mutation_class":"test","path":"platform_tests/skills/test_verified_finalization_validation_hardening.py"}],"decision_id":"sha256:6adf192c8a83c1527a7cf6385227221d1b80931d8d2beb9b8588ab8c5ab1fdbc","decision_time":"2026-07-29T12:43:22Z","envelope_decision":{"allowed":true,"authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","authorization_version":1,"classified_targets":[{"mutation_class":"test","path":"platform_tests/skills/test_verified_finalization_validation_hardening.py"}],"decision_time":"2026-07-29T12:43:22Z","evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","normalized_envelope_hash":"E8CAA986676F3DD9304D1B3218CC70ABA4BBBCB1E784D0628AB1D2BD9F246BF8","normalized_operation":"bridge_proposal_filing","reason":"The requested operation and every target class are PAUTH-allowed.","reason_code":"allowed","recovery":"Correct the current PAUTH envelope or requested operation, then reevaluate before side effects.","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"},"evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","fixed_best_cohort_ids":["PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION"],"fixed_best_rank":[1,7],"invalidation_inputs":{"bridge_document":"gtkb-wi5665-cursor-fallback-hardening-test-repair","latest_bridge_status":"ABSENT","latest_bridge_version":0,"membership_id":null,"membership_status":null,"membership_version":null,"planned_bridge_status":"NEW","planned_bridge_version":1,"project_completed_at":null,"project_status":"active","project_version":2,"reviewed_proposal_version":1},"normalized_operation":"bridge_proposal_filing","project_authorization_candidates":[{"coverage":"explicit_list","currentness":"current","disposition":"selected","included_work_item_count":7,"normalized_expiry":null,"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","selected":true,"specificity_rank":[1,7],"status":"active","supersession_state":"current"},{"coverage":"not_covering","currentness":"current","disposition":"not_covering","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724","selected":false,"specificity_rank":null,"status":"active","supersession_state":"current"}],"reason":"The selected current authorization covers the work item, operation, targets, and linked-spec exclusions.","reason_code":"allowed","recovery":"Re-evaluate from fresh state if any invalidation input changes before filing.","request":{"bridge_document":"gtkb-wi5665-cursor-fallback-hardening-test-repair","linked_specifications":["GOV-FILE-BRIDGE-AUTHORITY-001","GOV-ARTIFACT-ORIENTED-GOVERNANCE-001","DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001","DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001","SPEC-AUQ-POLICY-ENGINE-001","ADR-ISOLATION-APPLICATION-PLACEMENT-001","GOV-STANDING-BACKLOG-001","ADR-CODEX-HOOK-PARITY-FALLBACK-001","ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001","DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001","GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001","DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001","GOV-WORK-TREE-HYGIENE-001","GOV-RELIABILITY-FAST-LANE-001","ADR-CROSS-HARNESS-PARITY-001","DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001"],"project_id":"GTKB-SKILL-RENAME-REFERENCE-SWEEP","target_paths":["platform_tests/skills/test_verified_finalization_validation_hardening.py"],"work_item_id":"WI-5665"},"requested_project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","schema_version":1,"selected_project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","selector_mode":"explicit","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"}
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5665
Latest Bridge Status: ABSENT
Reviewed Proposal Version: 1

target_paths: ["platform_tests/skills/test_verified_finalization_validation_hardening.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the five false-red Cursor parametrizations in the WI-5662 hardening module by testing the governed fallback contract instead of loading a surface that is intentionally absent.

Work item description: _No work item description supplied._

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5665` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/skills/test_verified_finalization_validation_hardening.py`.

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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-RELIABILITY-FAST-LANE-001` - auto-linked governing or work-item specification.
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666638` - LO Review - WI-5370 No-Responds Repair for WI-5299 Reissued Finalizer Failure Repair
- `DELIB-202666640` - LO Review - WI-5370 Repair Malformed No-Responds Terminal VERIFIED (wi5354-failed-verified-finalization-repair)
- `DELIB-202666637` - LO Review - WI-5370 No-Responds Repair Implementation Report (wi5299-reissued-finalizer-failure-repair)
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` - Process the eight most recent skill-rename work items
- `DELIB-202666636` - LO Review - WI-5370 Repair Malformed No-Responds Terminal VERIFIED (wi5299-reissued-finalizer-failure-repair)

## Owner Decisions / Input

- `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION` - active project authorization covering `WI-5665`.

## Proposed Scope

- Restrict direct helper-loading behavior parametrizations to the real Claude and Codex helper copies.
- Add explicit Cursor coverage that reads config/agent-control/harness-capability-registry.toml and proves skill.verify is a declared fallback whose absent .cursor/skills/gtkb-verify surface is intentional.
- Preserve claimed-path parsing coverage for .cursor dot-directory paths; do not generate placeholder Cursor adapters or mutate any source, adapter, registry, or manifest.

## Cross-Harness Disposition

- **cursor**: deferred fallback; WI-5642 forbids placeholder generation and requires DEFERRED/WAIVED semantics

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5665; PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "WI-5665 has no implemented behavior yet; this proposal defines the slice.",
  "after_behavior": "Repair the five false-red Cursor parametrizations in the WI-5662 hardening module by testing the governed fallback contract instead of loading a surface that is intentionally absent.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5665",
    "project": "GTKB-SKILL-RENAME-REFERENCE-SWEEP",
    "target_paths": [
      "platform_tests/skills/test_verified_finalization_validation_hardening.py"
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
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "GOV-WORK-TREE-HYGIENE-001",
      "GOV-RELIABILITY-FAST-LANE-001",
      "ADR-CROSS-HARNESS-PARITY-001",
      "DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001"
    ]
  },
  "expected_result": {
    "summary": "Repair the five false-red Cursor parametrizations in the WI-5662 hardening module by testing the governed fallback contract instead of loading a surface that is intentionally absent.",
    "scope": [
      "Restrict direct helper-loading behavior parametrizations to the real Claude and Codex helper copies.",
      "Add explicit Cursor coverage that reads config/agent-control/harness-capability-registry.toml and proves skill.verify is a declared fallback whose absent .cursor/skills/gtkb-verify surface is intentional.",
      "Preserve claimed-path parsing coverage for .cursor dot-directory paths; do not generate placeholder Cursor adapters or mutate any source, adapter, registry, or manifest."
    ],
    "acceptance_criteria": [
      "The full hardening module passes without FileNotFoundError and retains meaningful Cursor contract coverage.",
      "The test proves Cursor skill.verify remains status=fallback at .cursor/skills/gtkb-verify/SKILL.md and that the surface is absent, matching WI-5642 and bridge/gtkb-skill-rename-cursor-goose-parity-002.md.",
      "Only platform_tests/skills/test_verified_finalization_validation_hardening.py changes from its verified HEAD preimage; no source, adapter, registry, manifest, or MemBase path changes."
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
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the complete hardening module and require all tests pass. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-WORK-TREE-HYGIENE-001` | Verify the target preimage, scoped diff, git diff --check, Ruff check, and Ruff format --check. |
| `GOV-RELIABILITY-FAST-LANE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CROSS-HARNESS-PARITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run the explicit Cursor fallback regression and confirm no placeholder surface is created. |

## Acceptance Criteria

- The full hardening module passes without FileNotFoundError and retains meaningful Cursor contract coverage.
- The test proves Cursor skill.verify remains status=fallback at .cursor/skills/gtkb-verify/SKILL.md and that the surface is absent, matching WI-5642 and bridge/gtkb-skill-rename-cursor-goose-parity-002.md.
- Only platform_tests/skills/test_verified_finalization_validation_hardening.py changes from its verified HEAD preimage; no source, adapter, registry, manifest, or MemBase path changes.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `platform_tests/skills/test_verified_finalization_validation_hardening.py`

## Recommended Commit Type

`feat`
