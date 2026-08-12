NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb353-97ef-74b1-9310-09761b16938a
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=not-exposed-by-host; thread_source=codex-desktop-interactive
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Systemic chain-hygiene fix: control-plane recovery command for pre-fix bridge files lacking publication capabilities

bridge_kind: prime_proposal
Document: gtkb-wi5950-strict-terminal-recovery
Version: 001
Date: 2026-08-10 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"selected","selected":true},{"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-TAXONOMY-CLEAN","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"best_rank_current","selected":false},{"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5163-SHADOW-EVALUATION-20260715","coverage":"not_covering","included_work_item_count":1,"specificity_rank":null,"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"not_covering","selected":false},{"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5165-RC-BLOCKER-REPAIR-20260715","coverage":"not_covering","included_work_item_count":1,"specificity_rank":null,"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"not_covering","selected":false}]
Project Authorization Decision: {"actor":{"role":"prime-builder","session_context_id":"019fb353-97ef-74b1-9310-09761b16938a"},"allowed":true,"authorization":{"allowed_mutation_classes":["bridge","metadata","source","test","configuration","documentation","runtime_state","governance_evidence"],"excluded_spec_ids":[],"excluded_work_item_ids":[],"forbidden_operations":["credential_lifecycle","destructive_cleanup","dispatcher_mutation","external_system_mutation","git_history_rewrite","git_push","production_deployment","release"],"id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE","included_spec_ids":["GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001","GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001","DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001","DCL-PROJECT-AUTHORIZATION-ENVELOPE-001","GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001","PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001","GOV-FILE-BRIDGE-AUTHORITY-001","DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001","DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001","DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001","DCL-PROJECT-DEPENDENCY-ORDERING-001","ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001","DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001","GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"],"included_work_item_ids":[],"normalized_envelope_hash":"DD97A64559D9963C3E4E13AD6DB8619EFCF65AC387340D22165A2A22AD6CB9A5","normalized_expiry":null,"owner_decision_deliberation_id":"DELIB-202667714","owner_decision_snapshot":{"id":"DELIB-202667714","outcome":"owner_decision","source_type":"owner_conversation","version":1},"status":"active","supersession_state":"current","version":5},"classified_targets":[{"mutation_class":"source","path":"groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py"},{"mutation_class":"test","path":"platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"}],"decision_id":"sha256:291b4d31532f60235808c084857c9af428d0ae4a9e18d36ab68d2261b4410e9e","decision_time":"2026-08-10T09:04:43Z","envelope_decision":{"allowed":true,"authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE","authorization_version":5,"classified_targets":[{"mutation_class":"source","path":"groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py"},{"mutation_class":"test","path":"platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"}],"decision_time":"2026-08-10T09:04:43Z","evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42","evaluator_version":"1","normalized_envelope_hash":"DD97A64559D9963C3E4E13AD6DB8619EFCF65AC387340D22165A2A22AD6CB9A5","normalized_operation":"bridge_proposal_filing","reason":"The requested operation and every target class are PAUTH-allowed.","reason_code":"allowed","recovery":"Correct the current PAUTH envelope or requested operation, then reevaluate before side effects.","taxonomy_sha256":"C0DA33114C9B3FD2B3DFD816043B458D8C0171143D014B79B812AA354F0EE450","taxonomy_version":"2"},"evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42","evaluator_version":"1","fixed_best_cohort_ids":["PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE","PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-TAXONOMY-CLEAN"],"fixed_best_rank":[2,0],"invalidation_inputs":{"bridge_document":"gtkb-wi5950-strict-terminal-recovery","latest_bridge_status":"ABSENT","latest_bridge_version":0,"membership_id":null,"membership_status":null,"membership_version":null,"planned_bridge_status":"NEW","planned_bridge_version":1,"project_completed_at":null,"project_status":"active","project_version":2,"reviewed_proposal_version":1},"normalized_operation":"bridge_proposal_filing","project_authorization_candidates":[{"coverage":"project_membership_fallback","currentness":"current","disposition":"selected","included_work_item_count":null,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE","selected":true,"specificity_rank":[2,0],"status":"active","supersession_state":"current"},{"coverage":"project_membership_fallback","currentness":"current","disposition":"best_rank_current","included_work_item_count":null,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-TAXONOMY-CLEAN","selected":false,"specificity_rank":[2,0],"status":"active","supersession_state":"current"},{"coverage":"not_covering","currentness":"current","disposition":"not_covering","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5163-SHADOW-EVALUATION-20260715","selected":false,"specificity_rank":null,"status":"active","supersession_state":"current"},{"coverage":"not_covering","currentness":"current","disposition":"not_covering","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5165-RC-BLOCKER-REPAIR-20260715","selected":false,"specificity_rank":null,"status":"active","supersession_state":"current"}],"reason":"The selected current authorization covers the work item, operation, targets, and linked-spec exclusions.","reason_code":"allowed","recovery":"Re-evaluate from fresh state if any invalidation input changes before filing.","request":{"bridge_document":"gtkb-wi5950-strict-terminal-recovery","linked_specifications":["GOV-FILE-BRIDGE-AUTHORITY-001","GOV-ARTIFACT-ORIENTED-GOVERNANCE-001","DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001","DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001","SPEC-AUQ-POLICY-ENGINE-001","ADR-ISOLATION-APPLICATION-PLACEMENT-001","GOV-STANDING-BACKLOG-001","ADR-CODEX-HOOK-PARITY-FALLBACK-001","ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001","DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001","DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001","GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"],"project_id":"PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE","target_paths":["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py","platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"],"work_item_id":"WI-5950"},"requested_project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE","schema_version":1,"selected_project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE","selector_mode":"explicit","taxonomy_sha256":"C0DA33114C9B3FD2B3DFD816043B458D8C0171143D014B79B812AA354F0EE450","taxonomy_version":"2"}
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5950
Latest Bridge Status: ABSENT
Reviewed Proposal Version: 1

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Create a fresh executable carrier for WI-5950 because the original v006 terminal artifact lacks mandatory atomic commit-finalization evidence; independently revalidate the existing untrusted candidate bytes and finalize only through a fresh governed chain.

Work item description: SYSTEMIC CHAIN-HYGIENE DEFECT (2026-08-06, owner decision B): pre-fix bridge filings lack consumed publication-capability receipts, blocking atomic VERIFIED finalization (WI-5825-class stranding). Affected: WI-5942 chain 001/003, WI-5314 -015, WI-5368 -023/-027/-028. mint_bridge_publication_capability refuses existing files (existing-file guard) and requires a live work-intent claim; consume_bridge_publication_capability validates aggregate_preimage_digest against the live latest aggregate revision (changes on every write). No clean control-plane recovery exists for no-capability pre-fix files. Fix: add a governed control-plane recovery command that, under explicit owner authority, recomputes the aggregate preimage at consume time, bypasses the existing-file guard, and mints+consumes a publication capability for an existing pre-fix bridge file, so atomic VERIFIED can stage the full chain. Include focused tests.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5950` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`, `platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py`.

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
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260808-WI5977-LIVE-STRAND-DURING-PROGRAM-FILING` - Live reproduction of WI-5977: filing the program's own proposal stranded its publication receipt
- `DELIB-20260806011691` - Loyal Opposition Verification — WI-5575 session-orient stable identifier (REVISED report 010)
- `DELIB-20260806011804` - Loyal Opposition Review — WI-5841 harness-selector registry-derived (REVISED 019)
- `DELIB-20260806011867` - Loyal Opposition Review — WI-5950 publication-capability recovery (NEW 001)
- `DELIB-20260807011967` - WI-5152 by-reference finalization waiver

## Owner Decisions / Input

- `DELIB-20260810-BRIDGE-VERSIONED-FILES-REGISTRY-REFRESH-AUTHORIZATION` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5950`.

## Proposed Scope

- Preserve bridge/gtkb-wi5950-publication-capability-state-recovery-001.md through -006.md byte-for-byte as historical non-executable evidence; do not edit, delete, stage, or cite that false-terminal chain as current authority.
- Require a fresh independent GO, an exact work-intent claim, and a schema-v3 implementation-start packet for the two exact target paths before adopting or changing any candidate implementation bytes.
- After implementation start, compare the existing foreign-dirty candidate bytes with the approved recovery design; retain conforming bytes or make only bounded corrections needed for the approved recovery helper and hermetic tests.
- Do not execute a live bridge-versioned-files registry recovery during this implementation slice; this slice only establishes and verifies the owner-gated recovery capability.
- Rerun focused recovery tests, the registry-control-plane regression suite, Ruff check, Ruff format check, Python compilation, exact diff review, and nonimpairment checks; then file a fresh implementation report and obtain independent atomic VERIFIED finalization.
- If ordinary finalization is blocked solely by the historical false-terminal chain, use the independently VERIFIED WI-6073 governed batch finalizer only after its exact plan digest and all protected-commit gates pass.
- Do not enable or mutate TAFE/dispatcher state; do not touch .api-harness/routing.toml, .claude/settings.json, config/dispatcher/rules.toml, config/agent-control/harness-capability-registry.toml, credentials, deployment, release, push, history, or unrelated dirty paths.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5950; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "SYSTEMIC CHAIN-HYGIENE DEFECT (2026-08-06, owner decision B): pre-fix bridge filings lack consumed publication-capability receipts, blocking atomic VERIFIED finalization (WI-5825-class stranding). Affected: WI-5942 chain 001/003, WI-5314 -015, WI-5368 -023/-027/-028. mint_bridge_publication_capability refuses existing files (existing-file guard) and requires a live work-intent claim; consume_bridge_publication_capability validates aggregate_preimage_digest against the live latest aggregate revision (changes on every write). No clean control-plane recovery exists for no-capability pre-fix files. Fix: add a governed control-plane recovery command that, under explicit owner authority, recomputes the aggregate preimage at consume time, bypasses the existing-file guard, and mints+consumes a publication capability for an existing pre-fix bridge file, so atomic VERIFIED can stage the full chain. Include focused tests.",
  "after_behavior": "Create a fresh executable carrier for WI-5950 because the original v006 terminal artifact lacks mandatory atomic commit-finalization evidence; independently revalidate the existing untrusted candidate bytes and finalize only through a fresh governed chain.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5950",
    "project": "PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py",
      "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"
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
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"
    ]
  },
  "expected_result": {
    "summary": "Create a fresh executable carrier for WI-5950 because the original v006 terminal artifact lacks mandatory atomic commit-finalization evidence; independently revalidate the existing untrusted candidate bytes and finalize only through a fresh governed chain.",
    "scope": [
      "Preserve bridge/gtkb-wi5950-publication-capability-state-recovery-001.md through -006.md byte-for-byte as historical non-executable evidence; do not edit, delete, stage, or cite that false-terminal chain as current authority.",
      "Require a fresh independent GO, an exact work-intent claim, and a schema-v3 implementation-start packet for the two exact target paths before adopting or changing any candidate implementation bytes.",
      "After implementation start, compare the existing foreign-dirty candidate bytes with the approved recovery design; retain conforming bytes or make only bounded corrections needed for the approved recovery helper and hermetic tests.",
      "Do not execute a live bridge-versioned-files registry recovery during this implementation slice; this slice only establishes and verifies the owner-gated recovery capability.",
      "Rerun focused recovery tests, the registry-control-plane regression suite, Ruff check, Ruff format check, Python compilation, exact diff review, and nonimpairment checks; then file a fresh implementation report and obtain independent atomic VERIFIED finalization.",
      "If ordinary finalization is blocked solely by the historical false-terminal chain, use the independently VERIFIED WI-6073 governed batch finalizer only after its exact plan digest and all protected-commit gates pass.",
      "Do not enable or mutate TAFE/dispatcher state; do not touch .api-harness/routing.toml, .claude/settings.json, config/dispatcher/rules.toml, config/agent-control/harness-capability-registry.toml, credentials, deployment, release, push, history, or unrelated dirty paths."
    ],
    "acceptance_criteria": [
      "The fresh chain receives independent executable GO and a schema-v3 implementation-start packet bound to exactly the two proposed target paths.",
      "The recovery function is owner-decision-gated, exact-targeted, idempotent, honest about recovery outcome, and nonimpairing to valid existing publication-capability state.",
      "Focused and regression tests pass; Ruff check, Ruff format check, and Python compilation pass for the exact implementation and test paths.",
      "The fresh implementation report records exact file hashes, diff review, specification-derived verification evidence, and the historical chain disposition.",
      "Atomic finalization commits only the fresh recovery bridge chain and the two implementation target paths, with independent VERIFIED evidence and no unrelated worktree content."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify the fresh numbered bridge chain is helper-filed, independently reviewed, bound to an exact claim and schema-v3 start packet, and never relies on the original malformed v006 as executable authority. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Record specification-to-test mappings, commands, results, exact hashes, and atomic commit-finalization evidence in the fresh report and independent VERIFIED verdict. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Recheck the active Assurance PAUTH immediately before implementation start and again before any governed local commit; confirm all target paths and mutation classes are covered and forbidden operations remain untouched. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run focused recovery tests and the full registry-control-plane regression suite, inspect exact diffs, and confirm valid publication-capability rows and unrelated registry state are unchanged. |

## Acceptance Criteria

- The fresh chain receives independent executable GO and a schema-v3 implementation-start packet bound to exactly the two proposed target paths.
- The recovery function is owner-decision-gated, exact-targeted, idempotent, honest about recovery outcome, and nonimpairing to valid existing publication-capability state.
- Focused and regression tests pass; Ruff check, Ruff format check, and Python compilation pass for the exact implementation and test paths.
- The fresh implementation report records exact file hashes, diff review, specification-derived verification evidence, and the historical chain disposition.
- Atomic finalization commits only the fresh recovery bridge chain and the two implementation target paths, with independent VERIFIED evidence and no unrelated worktree content.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py`

## Recommended Commit Type

`feat`

---

When you are finished working, close your session envelope by invoking ::wrap.
