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

# Implementation Proposal - Sweep S5: fix .gitignore scratch patterns, docs, and archive-vs-fix one-off scripts

bridge_kind: prime_proposal
Document: gtkb-wi5666-terminal-evidence-finalization-recovery
Version: 001
Date: 2026-07-29 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"selected","selected":true},{"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","coverage":"explicit_list","included_work_item_count":7,"specificity_rank":[1,7],"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"lower_rank","selected":false},{"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5664-WI5667-BRIDGE-REPORTS-20260729","coverage":"not_covering","included_work_item_count":2,"specificity_rank":null,"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"not_covering","selected":false},{"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5665-FINALIZATION-20260729","coverage":"not_covering","included_work_item_count":1,"specificity_rank":null,"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"not_covering","selected":false}]
Project Authorization Decision: {"actor":{"role":"prime-builder","session_context_id":"019f9329-a174-7763-8f7e-29679f39e6bd"},"allowed":true,"authorization":{"allowed_mutation_classes":["bridge","governance_evidence"],"excluded_spec_ids":[],"excluded_work_item_ids":[],"forbidden_operations":["external_system_mutation","dispatcher_mutation","credential_or_secret_mutation","git_history_rewrite","push"],"id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724","included_spec_ids":["GOV-FILE-BRIDGE-AUTHORITY-001"],"included_work_item_ids":["WI-5666"],"normalized_envelope_hash":"9345E7802BB9B3ED616560C20BC830A47E9730DE131DF96906C68F68A0424E3A","normalized_expiry":null,"owner_decision_deliberation_id":"DELIB-202667193","owner_decision_snapshot":{"id":"DELIB-202667193","outcome":"owner_decision","source_type":"owner_conversation","version":1},"status":"active","supersession_state":"current","version":1},"classified_targets":[{"mutation_class":"bridge","path":"bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-003.md"}],"decision_id":"sha256:eaa772cdf433f29cc37cbdd79e6ce49ceae04080b768ad98db938cce46f5ccf3","decision_time":"2026-07-29T19:29:43Z","envelope_decision":{"allowed":true,"authorization_id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724","authorization_version":1,"classified_targets":[{"mutation_class":"bridge","path":"bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-003.md"}],"decision_time":"2026-07-29T19:29:43Z","evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","normalized_envelope_hash":"9345E7802BB9B3ED616560C20BC830A47E9730DE131DF96906C68F68A0424E3A","normalized_operation":"bridge_proposal_filing","reason":"The requested operation and every target class are PAUTH-allowed.","reason_code":"allowed","recovery":"Correct the current PAUTH envelope or requested operation, then reevaluate before side effects.","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"},"evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","fixed_best_cohort_ids":["PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724"],"fixed_best_rank":[0,1],"invalidation_inputs":{"bridge_document":"gtkb-wi5666-terminal-evidence-finalization-recovery","latest_bridge_status":"ABSENT","latest_bridge_version":0,"membership_id":null,"membership_status":null,"membership_version":null,"planned_bridge_status":"NEW","planned_bridge_version":1,"project_completed_at":null,"project_status":"active","project_version":2,"reviewed_proposal_version":1},"normalized_operation":"bridge_proposal_filing","project_authorization_candidates":[{"coverage":"exact_singleton","currentness":"current","disposition":"selected","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724","selected":true,"specificity_rank":[0,1],"status":"active","supersession_state":"current"},{"coverage":"explicit_list","currentness":"current","disposition":"lower_rank","included_work_item_count":7,"normalized_expiry":null,"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","selected":false,"specificity_rank":[1,7],"status":"active","supersession_state":"current"},{"coverage":"not_covering","currentness":"current","disposition":"not_covering","included_work_item_count":2,"normalized_expiry":null,"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5664-WI5667-BRIDGE-REPORTS-20260729","selected":false,"specificity_rank":null,"status":"active","supersession_state":"current"},{"coverage":"not_covering","currentness":"current","disposition":"not_covering","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5665-FINALIZATION-20260729","selected":false,"specificity_rank":null,"status":"active","supersession_state":"current"}],"reason":"The selected current authorization covers the work item, operation, targets, and linked-spec exclusions.","reason_code":"allowed","recovery":"Re-evaluate from fresh state if any invalidation input changes before filing.","request":{"bridge_document":"gtkb-wi5666-terminal-evidence-finalization-recovery","linked_specifications":["GOV-FILE-BRIDGE-AUTHORITY-001","GOV-ARTIFACT-ORIENTED-GOVERNANCE-001","DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001","DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001","SPEC-AUQ-POLICY-ENGINE-001","ADR-ISOLATION-APPLICATION-PLACEMENT-001","GOV-STANDING-BACKLOG-001","ADR-CODEX-HOOK-PARITY-FALLBACK-001","ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001","DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001","GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001","DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001","PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001","GOV-WORK-TREE-HYGIENE-001"],"project_id":"GTKB-SKILL-RENAME-REFERENCE-SWEEP","target_paths":["bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-003.md"],"work_item_id":"WI-5666"},"requested_project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724","schema_version":1,"selected_project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724","selector_mode":"explicit","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"}
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5666
Latest Bridge Status: ABSENT
Reviewed Proposal Version: 1

target_paths: ["bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-003.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

This proposal performs no MemBase or KB mutation or write. Create a clean append-only recovery thread for WI-5666 terminal evidence because the prior tracked recovery v003 contains duplicate regex-visible canonical metadata and cannot be continued through strict governed writers. Preserve the committed ad19a366 four-path implementation unchanged; after independent GO, authorize only a v003 evidence report, then require independent atomic VERIFIED finalization of new-thread versions 001 through 004.

Work item description: _No work item description supplied._

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5666` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-003.md`.

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
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202667001` - NO-GO — WI-5370 missing-targets WI-5316 finalization repair (report 003)
- `DELIB-202666998` - Loyal Opposition Review - WI-5233 Missing-Targets Terminal Repair (VERIFIED)
- `DELIB-202667019` - NO-GO — WI-5370 tracked-terminal WI-4551 byte-ownership repair (report 003)
- `DELIB-202667005` - NO-GO — WI-5370 missing-targets wi5337-latest-no-go-draft-claim-state finalization repair (report 003)
- `DELIB-202667006` - NO-GO — WI-5370 missing-targets wi5341-bridge-claim-cli-import-parity finalization repair (report 003)

## Owner Decisions / Input

- `PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724` - active project authorization covering `WI-5666`.

## Proposed Scope

- Do not modify, stage, or recommit the historical four implementation paths already committed in ad19a366.
- After v002 GO, acquire an exact claim and schema-v3 start packet for only the future v003 implementation-evidence report.
- Reproduce the historical commit, four-path equality, residual-reference, ignore-probe, and scoped verification evidence and file it as v003 without source-byte mutation.
- Require the independent finalizer to include new-thread v001, v002, and v003; the helper adds v004 so the exact local commit is v001-v004 only.
- Treat both older WI-5666 NO-GO threads as quarantined evidence; never rewrite or bypass their tracked metadata defects.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5666; PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "WI-5666 has no implemented behavior yet; this proposal defines the slice.",
  "after_behavior": "This proposal performs no MemBase or KB mutation or write. Create a clean append-only recovery thread for WI-5666 terminal evidence because the prior tracked recovery v003 contains duplicate regex-visible canonical metadata and cannot be continued through strict governed writers. Preserve the committed ad19a366 four-path implementation unchanged; after independent GO, authorize only a v003 evidence report, then require independent atomic VERIFIED finalization of new-thread versions 001 through 004.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5666",
    "project": "GTKB-SKILL-RENAME-REFERENCE-SWEEP",
    "target_paths": [
      "bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-003.md"
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
      "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001",
      "GOV-WORK-TREE-HYGIENE-001"
    ]
  },
  "expected_result": {
    "summary": "This proposal performs no MemBase or KB mutation or write. Create a clean append-only recovery thread for WI-5666 terminal evidence because the prior tracked recovery v003 contains duplicate regex-visible canonical metadata and cannot be continued through strict governed writers. Preserve the committed ad19a366 four-path implementation unchanged; after independent GO, authorize only a v003 evidence report, then require independent atomic VERIFIED finalization of new-thread versions 001 through 004.",
    "scope": [
      "Do not modify, stage, or recommit the historical four implementation paths already committed in ad19a366.",
      "After v002 GO, acquire an exact claim and schema-v3 start packet for only the future v003 implementation-evidence report.",
      "Reproduce the historical commit, four-path equality, residual-reference, ignore-probe, and scoped verification evidence and file it as v003 without source-byte mutation.",
      "Require the independent finalizer to include new-thread v001, v002, and v003; the helper adds v004 so the exact local commit is v001-v004 only.",
      "Treat both older WI-5666 NO-GO threads as quarantined evidence; never rewrite or bypass their tracked metadata defects."
    ],
    "acceptance_criteria": [
      "The new v001 proposal files through the canonical writer with exactly one canonical metadata set and no historical artifact mutation.",
      "Independent v002 GO precedes an exact claim and schema-v3 implementation start for only the future v003 report.",
      "The v003 report proves commit ad19a366 contains exactly the four accepted implementation paths and the current paths remain clean.",
      "Independent v004 VERIFIED uses the governed atomic finalizer over exactly new-thread versions 001 through 004, creates one local commit, and performs no push."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Resolve the new numbered chain as NEW to GO to NEW report to atomic VERIFIED and prove old poisoned threads are not rewritten. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Reproduce historical four-path commit and focused acceptance evidence before independent atomic finalization. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Issue an exact schema-v3 start packet under the named WI-5666 bridge-only PAUTH for only the future v003 report. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-WORK-TREE-HYGIENE-001` | Show empty index and clean status for the already-committed four historical implementation paths before finalization. |

## Acceptance Criteria

- The new v001 proposal files through the canonical writer with exactly one canonical metadata set and no historical artifact mutation.
- Independent v002 GO precedes an exact claim and schema-v3 implementation start for only the future v003 report.
- The v003 report proves commit ad19a366 contains exactly the four accepted implementation paths and the current paths remain clean.
- Independent v004 VERIFIED uses the governed atomic finalizer over exactly new-thread versions 001 through 004, creates one local commit, and performs no push.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `bridge/gtkb-wi5666-terminal-evidence-finalization-recovery-003.md`

## Recommended Commit Type

`feat`
