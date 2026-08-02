NEW
::init gtkb pb
::open build
author_identity: claude
author_harness_id: B
author_session_context_id: 0f38ea76-2b25-4e4e-8913-45f97c849364
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Recursive-container coverage for high-churn test trees; restore registry membership_complete

bridge_kind: prime_proposal
Document: gtkb-wi5925-registry-recursive-container-coverage
Version: 001
Date: 2026-08-02 UTC

Project Authorization: PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-2026-08-01","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"status":"revoked","normalized_expiry":null,"currentness":"inactive","supersession_state":"current","disposition":"best_rank_inactive","selected":false},{"project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"selected","selected":true}]
Project Authorization Decision: {"actor":{"role":"prime-builder","session_context_id":"0f38ea76-2b25-4e4e-8913-45f97c849364"},"allowed":true,"authorization":{"allowed_mutation_classes":["configuration","runtime_state"],"excluded_spec_ids":[],"excluded_work_item_ids":[],"forbidden_operations":["git_push","git_history_rewrite","production_deployment","release","external_system_mutation","destructive_cleanup"],"id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01","included_spec_ids":["GOV-PLATFORM-SOT-REGISTRY-001"],"included_work_item_ids":["WI-5925"],"normalized_envelope_hash":"09E3C6F4638659FF631F6EC6F8BA69F3CE38239D4DB5F3BF59A5F09DFCE3F26D","normalized_expiry":null,"owner_decision_deliberation_id":"DELIB-202668162","owner_decision_snapshot":{"id":"DELIB-202668162","outcome":"owner_decision","source_type":"owner_conversation","version":1},"status":"active","supersession_state":"current","version":1},"classified_targets":[{"mutation_class":"configuration","path":"config/registry/sot-artifacts.toml"},{"mutation_class":"configuration","path":"groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"}],"decision_id":"sha256:474649f9d801ab592cb245205e42eb52601ed3cefe07d7fd49962e5ad629bfc5","decision_time":"2026-08-02T04:43:15Z","envelope_decision":{"allowed":true,"authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01","authorization_version":1,"classified_targets":[{"mutation_class":"configuration","path":"config/registry/sot-artifacts.toml"},{"mutation_class":"configuration","path":"groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"}],"decision_time":"2026-08-02T04:43:15Z","evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","normalized_envelope_hash":"09E3C6F4638659FF631F6EC6F8BA69F3CE38239D4DB5F3BF59A5F09DFCE3F26D","normalized_operation":"bridge_proposal_filing","reason":"The requested operation and every target class are PAUTH-allowed.","reason_code":"allowed","recovery":"Correct the current PAUTH envelope or requested operation, then reevaluate before side effects.","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"},"evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","fixed_best_cohort_ids":["PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-2026-08-01","PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01"],"fixed_best_rank":[0,1],"invalidation_inputs":{"bridge_document":"gtkb-wi5925-registry-recursive-container-coverage","latest_bridge_status":"ABSENT","latest_bridge_version":0,"membership_id":null,"membership_status":null,"membership_version":null,"planned_bridge_status":"NEW","planned_bridge_version":1,"project_completed_at":null,"project_status":"active","project_version":1,"reviewed_proposal_version":1},"normalized_operation":"bridge_proposal_filing","project_authorization_candidates":[{"coverage":"exact_singleton","currentness":"inactive","disposition":"best_rank_inactive","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-2026-08-01","selected":false,"specificity_rank":[0,1],"status":"revoked","supersession_state":"current"},{"coverage":"exact_singleton","currentness":"current","disposition":"selected","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01","selected":true,"specificity_rank":[0,1],"status":"active","supersession_state":"current"}],"reason":"The selected current authorization covers the work item, operation, targets, and linked-spec exclusions.","reason_code":"allowed","recovery":"Re-evaluate from fresh state if any invalidation input changes before filing.","request":{"bridge_document":"gtkb-wi5925-registry-recursive-container-coverage","linked_specifications":["GOV-PLATFORM-SOT-REGISTRY-001","GOV-FILE-BRIDGE-AUTHORITY-001","GOV-ARTIFACT-ORIENTED-GOVERNANCE-001","DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001","DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001","SPEC-AUQ-POLICY-ENGINE-001","ADR-ISOLATION-APPLICATION-PLACEMENT-001","GOV-STANDING-BACKLOG-001","ADR-CODEX-HOOK-PARITY-FALLBACK-001","ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001","DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001","DCL-SOT-REGISTRY-PROJECTION-PARITY-001"],"project_id":"PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT","target_paths":["config/registry/sot-artifacts.toml","groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"],"work_item_id":"WI-5925"},"requested_project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01","schema_version":1,"selected_project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01","selector_mode":"explicit","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"}
Project: PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT
Work Item: WI-5925
Latest Bridge Status: ABSENT
Reviewed Proposal Version: 1

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Convert platform_tests/ and groundtruth-kb/tests/ from per-file exact to recursive SoT-registry coverage to close the 26 unregistered_load_bearing membership gap and prevent per-file drift recurrence. Reconciler evidence (HEAD 364b4ce93): registered=18184, unregistered_disposable=1749, unregistered_load_bearing=26, membership_complete=False.

Work item description: Phase-2 registry coverage-model refinement (owner-authorized 2026-08-01 via AUQ: Both test trees, one governed change). Post-sweep gt registry reconcile shows membership_complete=False solely from 26 unregistered_load_bearing files, NOT the raw-audit 2567 (which double-counts the 1749 disposable/boundary the reconciler already classifies: applications=hosted_application_boundary; memory and .gtkb-state non-authoritative). ~22 of 26 are platform_tests files that drift because that tree is registered per-file exact. Fix: convert platform_tests (651 exact) and groundtruth-kb/tests (324 exact) to recursive coverage_mode (removes 975 redundant exact rows per the one-declaration-per-path no-overlap invariant, covers the 26 collectively AND prevents future per-file drift), add 4 exact rows for non-test drift (config/agent-control/goose-execution-floor.toml, operational_control_config.py, timer_config.py, scripts/goose_execution_guard.py), and de-register ~11 stale-absent entries (bridge/INDEX.md + generated dashboard artifacts). src (253) and scripts (356) keep per-file exact identity. Net: registry 2348 to ~1368 records. Governed via bridge proposal, LO GO, impl-start packet, PAUTH, register/validate/reconcile-verify, report, VERIFIED. Authority: GOV-PLATFORM-SOT-REGISTRY-001; DCL-SOT-REGISTRY-PROJECTION-PARITY-001. Prior art: WI-5441 resolved membership reconciliation per-file exact.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5925` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `config/registry/sot-artifacts.toml`, `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` - auto-linked governing or work-item specification.
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
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202668162` - Owner authorization: registry coverage-model recursive-container conversion (WI-5925)
- `DELIB-20264811` - GT-KB C4 Settings-Merge + Gitignore Drift - Loyal Opposition Review
- `DELIB-1819` - Loyal Opposition Verification - GTKB-ISOLATION-017 Slice 2 Registry Isolation
- `DELIB-202665544` - Loyal Opposition Verification — WI-5019 Narrative, Docs, Dashboard, and Scaffold Duplicate-SoT Audit
- `DELIB-20264810` - GT-KB C4 Settings-Merge + Gitignore Drift - Post-Implementation Verification

## Owner Decisions / Input

- `PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01` - active project authorization covering `WI-5925`.

## Proposed Scope

- De-register 975 exact rows under platform_tests (651) and groundtruth-kb/tests (324); MANDATORY under the registry one-declaration-per-path no-overlap invariant (_validate_overlaps rejects exact-under-recursive)
- Add 2 recursive containers (platform_tests/, groundtruth-kb/tests/) modeled on the config/governance/ recursive precedent; git_tracked, git_restore, authority GOV-PLATFORM-SOT-REGISTRY-001
- Add 4 exact rows for genuine non-test drift: goose-execution-floor.toml, operational_control_config.py, timer_config.py, scripts/goose_execution_guard.py
- De-register ~11 stale-absent entries (bridge/INDEX.md + generated dashboard artifacts), confirmed against live gt registry validate at implementation time
- src/ (253 exact) and scripts/ (356 exact) RETAIN per-file exact identity; applications/ untouched (single hosted_application_boundary). Net registry 2348 to ~1368 records
- Mechanism: deterministic TOML transform then gt registry validate then journalled projection regeneration; register --dry-run + validate prove the generation BEFORE commit; single-commit git revert rollback

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5925; PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Phase-2 registry coverage-model refinement (owner-authorized 2026-08-01 via AUQ: Both test trees, one governed change). Post-sweep gt registry reconcile shows membership_complete=False solely from 26 unregistered_load_bearing files, NOT the raw-audit 2567 (which double-counts the 1749 disposable/boundary the reconciler already classifies: applications=hosted_application_boundary; memory and .gtkb-state non-authoritative). ~22 of 26 are platform_tests files that drift because that tree is registered per-file exact. Fix: convert platform_tests (651 exact) and groundtruth-kb/tests (324 exact) to recursive coverage_mode (removes 975 redundant exact rows per the one-declaration-per-path no-overlap invariant, covers the 26 collectively AND prevents future per-file drift), add 4 exact rows for non-test drift (config/agent-control/goose-execution-floor.toml, operational_control_config.py, timer_config.py, scripts/goose_execution_guard.py), and de-register ~11 stale-absent entries (bridge/INDEX.md + generated dashboard artifacts). src (253) and scripts (356) keep per-file exact identity. Net: registry 2348 to ~1368 records. Governed via bridge proposal, LO GO, impl-start packet, PAUTH, register/validate/reconcile-verify, report, VERIFIED. Authority: GOV-PLATFORM-SOT-REGISTRY-001; DCL-SOT-REGISTRY-PROJECTION-PARITY-001. Prior art: WI-5441 resolved membership reconciliation per-file exact.",
  "after_behavior": "Convert platform_tests/ and groundtruth-kb/tests/ from per-file exact to recursive SoT-registry coverage to close the 26 unregistered_load_bearing membership gap and prevent per-file drift recurrence. Reconciler evidence (HEAD 364b4ce93): registered=18184, unregistered_disposable=1749, unregistered_load_bearing=26, membership_complete=False.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5925",
    "project": "PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT",
    "target_paths": [
      "config/registry/sot-artifacts.toml",
      "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"
    ],
    "linked_specifications": [
      "GOV-PLATFORM-SOT-REGISTRY-001",
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
      "DCL-SOT-REGISTRY-PROJECTION-PARITY-001"
    ]
  },
  "expected_result": {
    "summary": "Convert platform_tests/ and groundtruth-kb/tests/ from per-file exact to recursive SoT-registry coverage to close the 26 unregistered_load_bearing membership gap and prevent per-file drift recurrence. Reconciler evidence (HEAD 364b4ce93): registered=18184, unregistered_disposable=1749, unregistered_load_bearing=26, membership_complete=False.",
    "scope": [
      "De-register 975 exact rows under platform_tests (651) and groundtruth-kb/tests (324); MANDATORY under the registry one-declaration-per-path no-overlap invariant (_validate_overlaps rejects exact-under-recursive)",
      "Add 2 recursive containers (platform_tests/, groundtruth-kb/tests/) modeled on the config/governance/ recursive precedent; git_tracked, git_restore, authority GOV-PLATFORM-SOT-REGISTRY-001",
      "Add 4 exact rows for genuine non-test drift: goose-execution-floor.toml, operational_control_config.py, timer_config.py, scripts/goose_execution_guard.py",
      "De-register ~11 stale-absent entries (bridge/INDEX.md + generated dashboard artifacts), confirmed against live gt registry validate at implementation time",
      "src/ (253 exact) and scripts/ (356 exact) RETAIN per-file exact identity; applications/ untouched (single hosted_application_boundary). Net registry 2348 to ~1368 records",
      "Mechanism: deterministic TOML transform then gt registry validate then journalled projection regeneration; register --dry-run + validate prove the generation BEFORE commit; single-commit git revert rollback"
    ],
    "acceptance_criteria": [
      "gt registry reconcile --json: membership_complete=true, unregistered_load_bearing=0, invalid_unknown=0",
      "gt registry validate: coherent schema, projection parity, no coverage overlap, currentness, journal, reverse coverage",
      "no platform_tests/ or groundtruth-kb/tests/ exact rows remain; net record count ~1368"
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
| `GOV-PLATFORM-SOT-REGISTRY-001` | gt registry reconcile --json shows membership_complete=true and unregistered_load_bearing=0 |
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
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | gt registry validate --json passes schema parity overlap currentness journal reverse-coverage |

## Acceptance Criteria

- gt registry reconcile --json: membership_complete=true, unregistered_load_bearing=0, invalid_unknown=0
- gt registry validate: coherent schema, projection parity, no coverage overlap, currentness, journal, reverse coverage
- no platform_tests/ or groundtruth-kb/tests/ exact rows remain; net record count ~1368

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`

## Recommended Commit Type

`feat`
