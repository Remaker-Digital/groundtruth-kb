NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: reasoning_effort=unspecified-by-host; thread_source=CODEX_THREAD_ID
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Work-intent claim registry locks under concurrent workers: harden acquire and release

bridge_kind: prime_proposal
Document: gtkb-wi5784-work-intent-claim-lock-retry
Version: 001
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"selected","selected":true},{"project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI5760-SLICEB-20260729","coverage":"not_covering","included_work_item_count":1,"specificity_rank":null,"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"not_covering","selected":false},{"project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI5764-RECOVERY-20260730","coverage":"not_covering","included_work_item_count":1,"specificity_rank":null,"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"not_covering","selected":false},{"project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI5765-20260729","coverage":"not_covering","included_work_item_count":1,"specificity_rank":null,"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"not_covering","selected":false},{"project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI5765-CORRECTED-20260729","coverage":"not_covering","included_work_item_count":1,"specificity_rank":null,"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"not_covering","selected":false}]
Project Authorization Decision: {"actor":{"role":"prime-builder","session_context_id":"019fb1f2-2f91-7b82-ac15-acdd56e13d1e"},"allowed":true,"authorization":{"allowed_mutation_classes":["source","test","test_addition","configuration","metadata","governance_evidence","bridge"],"excluded_spec_ids":[],"excluded_work_item_ids":[],"forbidden_operations":["dispatcher_mutation","external_system_mutation","credential_lifecycle","push","history_rewrite","deployment","release","destructive_cleanup"],"id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM","included_spec_ids":["GOV-FILE-BRIDGE-AUTHORITY-001","GOV-ARTIFACT-APPROVAL-001"],"included_work_item_ids":[],"normalized_envelope_hash":"3E17BC2695828B5EB6E5A636E86BF024D18D1B93DB5A2096A0BE19728B59BE4F","normalized_expiry":null,"owner_decision_deliberation_id":"DELIB-202667533","owner_decision_snapshot":{"id":"DELIB-202667533","outcome":"owner_decision","source_type":"owner_conversation","version":1},"status":"active","supersession_state":"current","version":5},"classified_targets":[{"mutation_class":"source","path":"scripts/bridge_work_intent_registry.py"},{"mutation_class":"test","path":"platform_tests/scripts/test_bridge_work_intent_registry.py"}],"decision_id":"sha256:52e10f014a7821c221dbe1367f3b587d85e10de0a1234030ef6501f52cb00a37","decision_time":"2026-07-30T14:14:43Z","envelope_decision":{"allowed":true,"authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM","authorization_version":5,"classified_targets":[{"mutation_class":"source","path":"scripts/bridge_work_intent_registry.py"},{"mutation_class":"test","path":"platform_tests/scripts/test_bridge_work_intent_registry.py"}],"decision_time":"2026-07-30T14:14:43Z","evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","normalized_envelope_hash":"3E17BC2695828B5EB6E5A636E86BF024D18D1B93DB5A2096A0BE19728B59BE4F","normalized_operation":"bridge_proposal_filing","reason":"The requested operation and every target class are PAUTH-allowed.","reason_code":"allowed","recovery":"Correct the current PAUTH envelope or requested operation, then reevaluate before side effects.","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"},"evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","fixed_best_cohort_ids":["PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM"],"fixed_best_rank":[2,0],"invalidation_inputs":{"bridge_document":"gtkb-wi5784-work-intent-claim-lock-retry","latest_bridge_status":"ABSENT","latest_bridge_version":0,"membership_id":null,"membership_status":null,"membership_version":null,"planned_bridge_status":"NEW","planned_bridge_version":1,"project_completed_at":null,"project_status":"active","project_version":1,"reviewed_proposal_version":1},"normalized_operation":"bridge_proposal_filing","project_authorization_candidates":[{"coverage":"project_membership_fallback","currentness":"current","disposition":"selected","included_work_item_count":null,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM","selected":true,"specificity_rank":[2,0],"status":"active","supersession_state":"current"},{"coverage":"not_covering","currentness":"current","disposition":"not_covering","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI5760-SLICEB-20260729","selected":false,"specificity_rank":null,"status":"active","supersession_state":"current"},{"coverage":"not_covering","currentness":"current","disposition":"not_covering","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI5764-RECOVERY-20260730","selected":false,"specificity_rank":null,"status":"active","supersession_state":"current"},{"coverage":"not_covering","currentness":"current","disposition":"not_covering","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI5765-20260729","selected":false,"specificity_rank":null,"status":"active","supersession_state":"current"},{"coverage":"not_covering","currentness":"current","disposition":"not_covering","included_work_item_count":1,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI5765-CORRECTED-20260729","selected":false,"specificity_rank":null,"status":"active","supersession_state":"current"}],"reason":"The selected current authorization covers the work item, operation, targets, and linked-spec exclusions.","reason_code":"allowed","recovery":"Re-evaluate from fresh state if any invalidation input changes before filing.","request":{"bridge_document":"gtkb-wi5784-work-intent-claim-lock-retry","linked_specifications":["GOV-FILE-BRIDGE-AUTHORITY-001","GOV-ARTIFACT-ORIENTED-GOVERNANCE-001","DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001","DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001","SPEC-AUQ-POLICY-ENGINE-001","ADR-ISOLATION-APPLICATION-PLACEMENT-001","GOV-STANDING-BACKLOG-001","ADR-CODEX-HOOK-PARITY-FALLBACK-001","ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001","DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001","GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001","DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001","DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001","GOV-SOURCE-OF-TRUTH-FRESHNESS-001","GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001","GOV-10","GOV-12","SPEC-1662","GOV-15"],"project_id":"PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729","target_paths":["scripts/bridge_work_intent_registry.py","platform_tests/scripts/test_bridge_work_intent_registry.py"],"work_item_id":"WI-5784"},"requested_project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM","schema_version":1,"selected_project_authorization_id":"PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM","selector_mode":"explicit","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"}
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5784
Latest Bridge Status: ABSENT
Reviewed Proposal Version: 1

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Bound work-intent acquire/release SQLite contention without weakening exact-holder safety or activating dispatcher/TAFE.

Work item description: Work-intent claim-registry SQLite contention affects both claim acquisition and explicit release. Acquisition failed during the 2026-07-30 parallel proposal wave with `Database error during acquire: database is locked` and later succeeded. The independently reviewed acquire-side recurrence in `bridge/gtkb-advisory-work-intent-acquire-db-lock-recurrence-001.md` records a null post-failure claim state, a successful bounded operator retry, and no partial claim; Loyal Opposition accepted routing that evidence into WI-5784 in `bridge/gtkb-advisory-work-intent-acquire-db-lock-recurrence-002.md`. The reviewed release-side advisory records two post-WI-5759 release failures after the registry's approximately 10-second wait, followed by a successful third retry; each failure preserved the exact claim, so behavior was fail-closed but operationally stranded cleanup.

Correct the shared `bridge_work_intent_registry` boundary with a bounded total retry/backoff contract for transient SQLITE_BUSY/locked results, exact slug-plus-session revalidation on every attempt, idempotent missing-claim success, foreign-holder preservation, phase/attempt/elapsed/error-code diagnostics, minimal hot-path schema work, and deterministic two-connection concurrency tests for unlock-within-budget, deadline exhaustion, holder replacement, idempotence, and connection/schema failure. Preserve TTL only as a final abandonment bound.

Dispatcher cleanup durability and bridge-writer compensation after post-write release failure are explicit caller-policy questions and must not be silently changed with the primitive retry repair. No process killing, lock-file deletion, raw database surgery, dispatcher/TAFE activation, or implementation authority is created by this backlog disposition. Mike approved governed processing of WI-5784 under its active parent project in `DELIB-20260730-WI5784-GOVERNED-PROCESSING-APPROVAL`; all normal proposal, review, work-intent claim, implementation-start, test, report, and independent-verification gates remain required.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5784` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_work_intent_registry.py`, `platform_tests/scripts/test_bridge_work_intent_registry.py`.

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
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - auto-linked governing or work-item specification.
- `GOV-10` - auto-linked governing or work-item specification.
- `GOV-12` - auto-linked governing or work-item specification.
- `SPEC-1662` - auto-linked governing or work-item specification.
- `GOV-15` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666542` - Loyal Opposition Proposal Review - GO - WI-5337 Latest NO-GO Draft Claim State
- `DELIB-202666965` - Loyal Opposition Verdict - GO - WI-5343 LO Review Authority Packet (Collision-Cleared Revision)
- `DELIB-202666916` - Loyal Opposition Corrected Verdict - NO-GO - WI-5178 Diagnostic Proof Confirmed; Full-Scope Implementation And Sibling-Thread Reconciliation Required
- `DELIB-202667002` - NO-GO — WI-5370 missing-targets WI-5318 finalization repair (report 003)
- `DELIB-202665288` - OPS Lifecycle Protocol Foundation — NO-GO Verdict (v008)

## Owner Decisions / Input

- `DELIB-20260730-WI5784-GOVERNED-PROCESSING-APPROVAL` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` - active project authorization covering `WI-5784`.

## Proposed Scope

- Replace the single SQLite write attempt in acquire and release with one monotonic total deadline and deterministic capped backoff limited to SQLITE_BUSY and SQLITE_LOCKED.
- Reopen and close the database on each retry; re-read the exact slug and session inside every transaction so acquire cannot overwrite changed ownership and release preserves foreign holders while treating a missing claim as idempotent success.
- Remove avoidable execution of the global GroundTruth SCHEMA_SQL from the narrow work-intent hot path while retaining idempotent work_intent_claims table, additive-column, and index migration.
- Expose safe typed exhaustion diagnostics carrying operation, phase, attempt count, elapsed time, SQLite code/name, and database path without claiming to identify the lock holder.
- Exclude dispatcher/TAFE activation or mutation, dispatcher caller durability, bridge-writer compensation policy, extend semantics, process termination, lock-file deletion, raw database surgery, Git publication, deployment, credentials, and external systems.

## Cross-Harness Disposition

- **shared-registry**: The work-intent registry is a shared in-root service used by all harnesses; one implementation and one shared behavioral test suite apply identically, with no harness-local fork or waiver.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5784; PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Work-intent claim-registry SQLite contention affects both claim acquisition and explicit release. Acquisition failed during the 2026-07-30 parallel proposal wave with `Database error during acquire: database is locked` and later succeeded. The independently reviewed acquire-side recurrence in `bridge/gtkb-advisory-work-intent-acquire-db-lock-recurrence-001.md` records a null post-failure claim state, a successful bounded operator retry, and no partial claim; Loyal Opposition accepted routing that evidence into WI-5784 in `bridge/gtkb-advisory-work-intent-acquire-db-lock-recurrence-002.md`. The reviewed release-side advisory records two post-WI-5759 release failures after the registry's approximately 10-second wait, followed by a successful third retry; each failure preserved the exact claim, so behavior was fail-closed but operationally stranded cleanup.\n\nCorrect the shared `bridge_work_intent_registry` boundary with a bounded total retry/backoff contract for transient SQLITE_BUSY/locked results, exact slug-plus-session revalidation on every attempt, idempotent missing-claim success, foreign-holder preservation, phase/attempt/elapsed/error-code diagnostics, minimal hot-path schema work, and deterministic two-connection concurrency tests for unlock-within-budget, deadline exhaustion, holder replacement, idempotence, and connection/schema failure. Preserve TTL only as a final abandonment bound.\n\nDispatcher cleanup durability and bridge-writer compensation after post-write release failure are explicit caller-policy questions and must not be silently changed with the primitive retry repair. No process killing, lock-file deletion, raw database surgery, dispatcher/TAFE activation, or implementation authority is created by this backlog disposition. Mike approved governed processing of WI-5784 under its active parent project in `DELIB-20260730-WI5784-GOVERNED-PROCESSING-APPROVAL`; all normal proposal, review, work-intent claim, implementation-start, test, report, and independent-verification gates remain required.",
  "after_behavior": "Bound work-intent acquire/release SQLite contention without weakening exact-holder safety or activating dispatcher/TAFE.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5784",
    "project": "PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729",
    "target_paths": [
      "scripts/bridge_work_intent_registry.py",
      "platform_tests/scripts/test_bridge_work_intent_registry.py"
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
      "DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001",
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
      "GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001",
      "GOV-10",
      "GOV-12",
      "SPEC-1662",
      "GOV-15"
    ]
  },
  "expected_result": {
    "summary": "Bound work-intent acquire/release SQLite contention without weakening exact-holder safety or activating dispatcher/TAFE.",
    "scope": [
      "Replace the single SQLite write attempt in acquire and release with one monotonic total deadline and deterministic capped backoff limited to SQLITE_BUSY and SQLITE_LOCKED.",
      "Reopen and close the database on each retry; re-read the exact slug and session inside every transaction so acquire cannot overwrite changed ownership and release preserves foreign holders while treating a missing claim as idempotent success.",
      "Remove avoidable execution of the global GroundTruth SCHEMA_SQL from the narrow work-intent hot path while retaining idempotent work_intent_claims table, additive-column, and index migration.",
      "Expose safe typed exhaustion diagnostics carrying operation, phase, attempt count, elapsed time, SQLite code/name, and database path without claiming to identify the lock holder.",
      "Exclude dispatcher/TAFE activation or mutation, dispatcher caller durability, bridge-writer compensation policy, extend semantics, process termination, lock-file deletion, raw database surgery, Git publication, deployment, credentials, and external systems."
    ],
    "acceptance_criteria": [
      "Acquire succeeds when a real two-connection lock clears inside the total deadline and leaves no partial claim when the deadline expires.",
      "Every acquire retry revalidates the transactional holder and operation; changed or foreign ownership is never overwritten.",
      "Release succeeds idempotently for an absent row, deletes only the exact slug-plus-session holder after retry, and preserves a replacement or foreign holder.",
      "Only SQLITE_BUSY and SQLITE_LOCKED are retried; schema, corruption, open, and other failures surface immediately with typed phase/attempt/elapsed/code diagnostics and all connections closed.",
      "The uncontended acquire/release hot path avoids global SCHEMA_SQL while retaining narrow idempotent schema compatibility; the existing focused suite stays green."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run deterministic real-SQLite two-connection tests proving exact-holder preservation, idempotent release, no partial claim, and bounded exhaustion. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Map every linked requirement to the focused test cases and record exact commands and results in the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Re-read holder state inside each retrying transaction and assert replacement-holder preservation under an induced interleaving. |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | Use monotonic deadlines and deterministic injected timing/lock fixtures; no wall-clock sleeps beyond bounded test coordination. |
| `GOV-10` | Exercise the public acquire and release interfaces against real SQLite connections rather than implementation-shape mocks. |
| `GOV-12` | Land focused regression tests in the same change as the retry primitive. |
| `SPEC-1662` | Assert behavior: success, exhaustion, diagnostics, idempotence, ownership preservation, and non-retryable failure semantics. |
| `GOV-15` | The implementation changes no dispatcher/TAFE or external-system state and performs no autonomous cleanup outside the exact claim row. |

## Acceptance Criteria

- Acquire succeeds when a real two-connection lock clears inside the total deadline and leaves no partial claim when the deadline expires.
- Every acquire retry revalidates the transactional holder and operation; changed or foreign ownership is never overwritten.
- Release succeeds idempotently for an absent row, deletes only the exact slug-plus-session holder after retry, and preserves a replacement or foreign holder.
- Only SQLITE_BUSY and SQLITE_LOCKED are retried; schema, corruption, open, and other failures surface immediately with typed phase/attempt/elapsed/code diagnostics and all connections closed.
- The uncontended acquire/release hot path avoids global SCHEMA_SQL while retaining narrow idempotent schema compatibility; the existing focused suite stays green.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_work_intent_registry.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`

## Recommended Commit Type

`feat`
