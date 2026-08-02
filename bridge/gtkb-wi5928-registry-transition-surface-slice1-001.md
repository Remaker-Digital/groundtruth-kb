NEW
::init gtkb pb
::open build
author_identity: claude
author_harness_id: B
author_session_context_id: eb769f27-7467-473a-b6f9-2aa9df543ef8
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Build registry identity-transition capability (transition-request/transition-apply) per DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001

bridge_kind: prime_proposal
Document: gtkb-wi5928-registry-transition-surface-slice1
Version: 001
Date: 2026-08-02 UTC

Project Authorization: PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"selected","selected":true},{"project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-2026-08-01","coverage":"not_covering","included_work_item_count":1,"specificity_rank":null,"status":"revoked","normalized_expiry":null,"currentness":"inactive","supersession_state":"current","disposition":"not_covering","selected":false},{"project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01","coverage":"not_covering","included_work_item_count":1,"specificity_rank":null,"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"not_covering","selected":false}]
Project Authorization Decision: {"actor":{"role":"prime-builder","session_context_id":"eb769f27-7467-473a-b6f9-2aa9df543ef8"},"allowed":true,"authorization":{"allowed_mutation_classes":["source","test"],"excluded_spec_ids":[],"excluded_work_item_ids":[],"forbidden_operations":["git_push","git_history_rewrite","production_deployment","release","external_system_mutation","destructive_cleanup"],"id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION","included_spec_ids":["DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001"],"included_work_item_ids":["WI-5928"],"normalized_envelope_hash":"C6C8926160004025EC8F8816C231F343385AC6E2A351DE0BA5E47F2CCCDC71ED","normalized_expiry":null,"owner_decision_deliberation_id":"DELIB-202668163","owner_decision_snapshot":{"id":"DELIB-202668163","outcome":"owner_decision","source_type":"owner_conversation","version":1},"status":"active","supersession_state":"current","version":1},"classified_targets":[{"mutation_class":"source","path":"groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py"},{"mutation_class":"source","path":"groundtruth-kb/src/groundtruth_kb/cli.py"},{"mutation_class":"test","path":"platform_tests/scripts/test_registry_transition_slice1.py"}],"decision_id":"sha256:def215ffe82d4bb6ead0bd0c05e1264c4795ca3cd45a0f6621f49f218f569aba","decision_time":"2026-08-02T06:03:51Z","envelope_decision":{"allowed":true,"authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION","authorization_version":1,"classified_targets":[{"mutation_class":"source","path":"groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py"},{"mutation_class":"source","path":"groundtruth-kb/src/groundtruth_kb/cli.py"},{"mutation_class":"test","path":"platform_tests/scripts/test_registry_transition_slice1.py"}],"decision_time":"2026-08-02T06:03:51Z","evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","normalized_envelope_hash":"C6C8926160004025EC8F8816C231F343385AC6E2A351DE0BA5E47F2CCCDC71ED","normalized_operation":"bridge_proposal_filing","reason":"The requested operation and every target class are PAUTH-allowed.","reason_code":"allowed","recovery":"Correct the current PAUTH envelope or requested operation, then reevaluate before side effects.","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"},"evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","fixed_best_cohort_ids":["PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION"],"fixed_best_rank":[0,1],"invalidation_inputs":{"bridge_document":"gtkb-wi5928-registry-transition-surface-slice1","latest_bridge_status":"ABSENT","latest_bridge_version":0,"membership_id":null,"membership_status":null,"membership_version":null,"planned_bridge_status":"NEW","planned_bridge_version":1,"project_completed_at":null,"project_status":"active","project_version":1,"reviewed_proposal_version":1},"normalized_operation":"bridge_proposal_filing","project_authorization_candidates":[{"coverage":"exact_singleton","currentness":"current","disposition":"selected","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION","selected":true,"specificity_rank":[0,1],"status":"active","supersession_state":"current"},{"coverage":"not_covering","currentness":"inactive","disposition":"not_covering","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-2026-08-01","selected":false,"specificity_rank":null,"status":"revoked","supersession_state":"current"},{"coverage":"not_covering","currentness":"current","disposition":"not_covering","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01","selected":false,"specificity_rank":null,"status":"active","supersession_state":"current"}],"reason":"The selected current authorization covers the work item, operation, targets, and linked-spec exclusions.","reason_code":"allowed","recovery":"Re-evaluate from fresh state if any invalidation input changes before filing.","request":{"bridge_document":"gtkb-wi5928-registry-transition-surface-slice1","linked_specifications":["DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001","GOV-FILE-BRIDGE-AUTHORITY-001","GOV-ARTIFACT-ORIENTED-GOVERNANCE-001","DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001","DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001","SPEC-AUQ-POLICY-ENGINE-001","ADR-ISOLATION-APPLICATION-PLACEMENT-001","GOV-STANDING-BACKLOG-001","ADR-CODEX-HOOK-PARITY-FALLBACK-001","ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001","DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001","GOV-PLATFORM-SOT-REGISTRY-001","DCL-SOT-REGISTRY-PROJECTION-PARITY-001"],"project_id":"PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT","target_paths":["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py","groundtruth-kb/src/groundtruth_kb/cli.py","platform_tests/scripts/test_registry_transition_slice1.py"],"work_item_id":"WI-5928"},"requested_project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION","schema_version":1,"selected_project_authorization_id":"PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION","selector_mode":"explicit","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"}
Project: PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT
Work Item: WI-5928
Latest Bridge Status: ABSENT
Reviewed Proposal Version: 1

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_registry_transition_slice1.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Slice 1 of WI-5928: build the gt registry transition-request/transition-apply authorized wrapper plus CLI on the existing generic apply_registry_transaction primitive and journal substrate, delivering the membership-set and coverage-mode identity-transition path per DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001. Unblocks WI-5925 and every future registry membership removal / coverage change platform-wide. Predecessor verified from LO NO-GO bridge/gtkb-wi5925-registry-recursive-container-coverage-002.

Work item description: Registry identity-transition capability is unbuilt. DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001 v2 mandates transition-request / transition-apply for any registry identity change (locator, coverage_mode, lifecycle, membership-set), but no such surface exists: (1) the registry CLI has no transition subcommand (amend/register/reconcile/recover/validate only); (2) register_artifacts in registry_control_plane around line 2215 commits snapshot-records plus additions -- adds only, never removes; (3) amend excludes coverage_mode/storage_path/lifecycle and raises require-transition-authority for identity changes; (4) no transition implementation found in the project package. Consequence: NO lawful mechanism to remove registry membership or change a coverage mode anywhere in GT-KB -- direct TOML editing is prohibited (GOV-PLATFORM-SOT-REGISTRY-001), register only adds, amend cannot touch identity. Very likely why the registry has bloated to 2348 records with stale entries. BLOCKS WI-5925 (recursive-container conversion needs 975 membership removals + 2 coverage-mode transitions). Verified against canon 2026-08-02 from the Loyal Opposition NO-GO verdict at bridge/gtkb-wi5925-registry-recursive-container-coverage-002. Scope: build the transition-request and transition-apply capability (CLI + control-plane code) per the DCL contract: OPS envelope; digest-bound request (entry id, source locator, current revision digest, operation, destination, owner evidence, intended membership result, expiry); apply gated on matching active request + matching independent bridge GO + fresh operation-time revalidation; delete-to-quarantine with membership-transition record; move/rename as one recoverable transaction updating filesystem identity + declaration + projection + revision history + journal + receipt; projection parity; shared registry resolver + identity-authorization service for hooks and gates. Owner directive 2026-08-02 (AUQ: Build the transition surface first). Predecessor to WI-5925, REVISED to use the surface once it lands. May warrant its own platform-registry project.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5928` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_registry_transition_slice1.py`.

## Specification Links

- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - auto-linked governing or work-item specification.
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
- `GOV-PLATFORM-SOT-REGISTRY-001` - auto-linked governing or work-item specification.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202668163` - Owner authorization: build registry identity-transition surface first (WI-5928, predecessor to WI-5925)
- `DELIB-202667522` - Authorize WI-5714 exact concurrent-registry repair
- `DELIB-20260976` - Loyal Opposition Review - Startup-Control Vocabulary Map
- `DELIB-20261175` - Loyal Opposition Review - Startup-Control Vocabulary Map
- `DELIB-202667662` - WI-5704 Transient Index Recurrence Prevention - VERIFIED (post-implementation)

## Owner Decisions / Input

- `PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION` - active project authorization covering `WI-5928`.

## Proposed Scope

- transition-request records a digest-bound request in sot_registry_transaction_journal (operation=transition_request) binding entry id, source locator, current revision digest, operation, destination, owner evidence, intended membership result, and expiry; returns a request handle
- transition-apply requires an OPS envelope, a matching active request, a matching independent bridge GO, and fresh operation-time revalidation (current revision digest unchanged); computes the desired record set (membership removals plus coverage-mode changes) and commits it through the existing apply_registry_transaction(desired, operation=transition)
- Add gt registry transition request and gt registry transition apply subcommands to the registry command group; reuse the existing lock, journal, digest, projection-parity, and RegistryResolver overlap validation with NO new transaction machinery
- Slice 1 scope is membership-set and coverage-mode identity transitions only (in-place declaration changes, no filesystem move/rename/delete); delete-to-quarantine, move/rename, and 30-day retention are explicitly deferred to Slice 2+
- RegistryResolver validates the desired set for exact-under-recursive overlap before commit, so an exact-to-recursive coverage conversion with the mandated exact-child removals is enforced coherent; amend continues to reject coverage-mode/lifecycle/membership changes and direct TOML editing remains prohibited
- This implementation performs no MemBase mutation and executes no groundtruth.db writes against the canonical KB: it adds source and test code only; the transition surface runtime registry-journal writes are exercised solely against test fixtures, not the live groundtruth.db

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5928; PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Registry identity-transition capability is unbuilt. DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001 v2 mandates transition-request / transition-apply for any registry identity change (locator, coverage_mode, lifecycle, membership-set), but no such surface exists: (1) the registry CLI has no transition subcommand (amend/register/reconcile/recover/validate only); (2) register_artifacts in registry_control_plane around line 2215 commits snapshot-records plus additions -- adds only, never removes; (3) amend excludes coverage_mode/storage_path/lifecycle and raises require-transition-authority for identity changes; (4) no transition implementation found in the project package. Consequence: NO lawful mechanism to remove registry membership or change a coverage mode anywhere in GT-KB -- direct TOML editing is prohibited (GOV-PLATFORM-SOT-REGISTRY-001), register only adds, amend cannot touch identity. Very likely why the registry has bloated to 2348 records with stale entries. BLOCKS WI-5925 (recursive-container conversion needs 975 membership removals + 2 coverage-mode transitions). Verified against canon 2026-08-02 from the Loyal Opposition NO-GO verdict at bridge/gtkb-wi5925-registry-recursive-container-coverage-002. Scope: build the transition-request and transition-apply capability (CLI + control-plane code) per the DCL contract: OPS envelope; digest-bound request (entry id, source locator, current revision digest, operation, destination, owner evidence, intended membership result, expiry); apply gated on matching active request + matching independent bridge GO + fresh operation-time revalidation; delete-to-quarantine with membership-transition record; move/rename as one recoverable transaction updating filesystem identity + declaration + projection + revision history + journal + receipt; projection parity; shared registry resolver + identity-authorization service for hooks and gates. Owner directive 2026-08-02 (AUQ: Build the transition surface first). Predecessor to WI-5925, REVISED to use the surface once it lands. May warrant its own platform-registry project.",
  "after_behavior": "Slice 1 of WI-5928: build the gt registry transition-request/transition-apply authorized wrapper plus CLI on the existing generic apply_registry_transaction primitive and journal substrate, delivering the membership-set and coverage-mode identity-transition path per DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001. Unblocks WI-5925 and every future registry membership removal / coverage change platform-wide. Predecessor verified from LO NO-GO bridge/gtkb-wi5925-registry-recursive-container-coverage-002.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5928",
    "project": "PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py",
      "groundtruth-kb/src/groundtruth_kb/cli.py",
      "platform_tests/scripts/test_registry_transition_slice1.py"
    ],
    "linked_specifications": [
      "DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001",
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
      "GOV-PLATFORM-SOT-REGISTRY-001",
      "DCL-SOT-REGISTRY-PROJECTION-PARITY-001"
    ]
  },
  "expected_result": {
    "summary": "Slice 1 of WI-5928: build the gt registry transition-request/transition-apply authorized wrapper plus CLI on the existing generic apply_registry_transaction primitive and journal substrate, delivering the membership-set and coverage-mode identity-transition path per DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001. Unblocks WI-5925 and every future registry membership removal / coverage change platform-wide. Predecessor verified from LO NO-GO bridge/gtkb-wi5925-registry-recursive-container-coverage-002.",
    "scope": [
      "transition-request records a digest-bound request in sot_registry_transaction_journal (operation=transition_request) binding entry id, source locator, current revision digest, operation, destination, owner evidence, intended membership result, and expiry; returns a request handle",
      "transition-apply requires an OPS envelope, a matching active request, a matching independent bridge GO, and fresh operation-time revalidation (current revision digest unchanged); computes the desired record set (membership removals plus coverage-mode changes) and commits it through the existing apply_registry_transaction(desired, operation=transition)",
      "Add gt registry transition request and gt registry transition apply subcommands to the registry command group; reuse the existing lock, journal, digest, projection-parity, and RegistryResolver overlap validation with NO new transaction machinery",
      "Slice 1 scope is membership-set and coverage-mode identity transitions only (in-place declaration changes, no filesystem move/rename/delete); delete-to-quarantine, move/rename, and 30-day retention are explicitly deferred to Slice 2+",
      "RegistryResolver validates the desired set for exact-under-recursive overlap before commit, so an exact-to-recursive coverage conversion with the mandated exact-child removals is enforced coherent; amend continues to reject coverage-mode/lifecycle/membership changes and direct TOML editing remains prohibited",
      "This implementation performs no MemBase mutation and executes no groundtruth.db writes against the canonical KB: it adds source and test code only; the transition surface runtime registry-journal writes are exercised solely against test fixtures, not the live groundtruth.db"
    ],
    "acceptance_criteria": [
      "transition request creates a digest-bound journal request carrying the DCL-required fields; transition apply is rejected when there is no matching active request, no matching independent bridge GO, or the source revision digest is stale",
      "an exact-to-recursive coverage conversion with the mandated exact-child membership removals succeeds via transition apply, and gt registry validate and gt registry reconcile pass afterward",
      "amend still rejects coverage-mode / lifecycle / membership changes (unchanged); no direct-TOML mutation path is introduced"
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
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | new tests assert transition request/apply gating (OPS envelope, matching active request, independent bridge GO, fresh revalidation) and that membership removal plus coverage-mode change succeed only through this path |
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
| `GOV-PLATFORM-SOT-REGISTRY-001` | test asserts a coverage-mode transition plus membership removal commits through gt registry transition and gt registry validate passes with no coverage overlap |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | test asserts declaration/projection parity and journal recoverability after a transition apply |

## Acceptance Criteria

- transition request creates a digest-bound journal request carrying the DCL-required fields; transition apply is rejected when there is no matching active request, no matching independent bridge GO, or the source revision digest is stale
- an exact-to-recursive coverage conversion with the mandated exact-child membership removals succeeds via transition apply, and gt registry validate and gt registry reconcile pass afterward
- amend still rejects coverage-mode / lifecycle / membership changes (unchanged); no direct-TOML mutation path is introduced

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_registry_transition_slice1.py`

## Recommended Commit Type

`feat`
