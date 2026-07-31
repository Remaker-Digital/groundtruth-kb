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

# Implementation Proposal - Decompose Harness Parity modernization packages

bridge_kind: prime_proposal
Document: gtkb-wi5144-hp08-current-head-finalization-recovery
Version: 001
Date: 2026-07-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"status":"active","normalized_expiry":null,"currentness":"current","supersession_state":"current","disposition":"selected","selected":true}]
Project Authorization Decision: {"actor":{"role":"prime-builder","session_context_id":"019f9329-a174-7763-8f7e-29679f39e6bd"},"allowed":true,"authorization":{"allowed_mutation_classes":["bridge","metadata","source","test","configuration","documentation","runtime_state","governance_evidence"],"excluded_spec_ids":[],"excluded_work_item_ids":[],"forbidden_operations":["credential_lifecycle","destructive_cleanup","dispatcher_mutation","external_system_mutation","git_commit","git_history_rewrite","git_push","production_deployment","release"],"id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE","included_spec_ids":["ADR-CROSS-HARNESS-PARITY-001","DCL-CROSS-HARNESS-ENFORCEMENT-001","DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001","GOV-DOCUMENT-AUTHOR-PROVENANCE-001","GOV-SESSION-ROLE-AUTHORITY-001","DCL-SESSION-ROLE-RESOLUTION-001","GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","GOV-FILE-BRIDGE-AUTHORITY-001","DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001","DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001","DCL-PROJECT-DEPENDENCY-ORDERING-001","ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001","DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001","GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"],"included_work_item_ids":[],"normalized_envelope_hash":"11AFFF8C76CB9EBCAFFA9923350652707CE329584FFA7005B52555ADA5D50327","normalized_expiry":null,"owner_decision_deliberation_id":"DELIB-202666274","owner_decision_snapshot":{"id":"DELIB-202666274","outcome":"owner_decision","source_type":"owner_conversation","version":1},"status":"active","supersession_state":"current","version":2},"classified_targets":[{"mutation_class":"bridge","path":"bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-003.md"}],"decision_id":"sha256:301b2b06c27c9e207afa0e6bf6464d1e4140d7c15627f64405a6f8ebc1166674","decision_time":"2026-07-29T19:42:23Z","envelope_decision":{"allowed":true,"authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE","authorization_version":2,"classified_targets":[{"mutation_class":"bridge","path":"bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-003.md"}],"decision_time":"2026-07-29T19:42:23Z","evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","normalized_envelope_hash":"11AFFF8C76CB9EBCAFFA9923350652707CE329584FFA7005B52555ADA5D50327","normalized_operation":"bridge_proposal_filing","reason":"The requested operation and every target class are PAUTH-allowed.","reason_code":"allowed","recovery":"Correct the current PAUTH envelope or requested operation, then reevaluate before side effects.","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"},"evaluator_id":"project-authorization-operation-time-enforcement","evaluator_sha256":"2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D","evaluator_version":"1","fixed_best_cohort_ids":["PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE"],"fixed_best_rank":[2,0],"invalidation_inputs":{"bridge_document":"gtkb-wi5144-hp08-current-head-finalization-recovery","latest_bridge_status":"ABSENT","latest_bridge_version":0,"membership_id":null,"membership_status":null,"membership_version":null,"planned_bridge_status":"NEW","planned_bridge_version":1,"project_completed_at":null,"project_status":"active","project_version":1,"reviewed_proposal_version":1},"normalized_operation":"bridge_proposal_filing","project_authorization_candidates":[{"coverage":"project_membership_fallback","currentness":"current","disposition":"selected","included_work_item_count":null,"normalized_expiry":null,"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE","selected":true,"specificity_rank":[2,0],"status":"active","supersession_state":"current"}],"reason":"The selected current authorization covers the work item, operation, targets, and linked-spec exclusions.","reason_code":"allowed","recovery":"Re-evaluate from fresh state if any invalidation input changes before filing.","request":{"bridge_document":"gtkb-wi5144-hp08-current-head-finalization-recovery","linked_specifications":["ADR-CROSS-HARNESS-PARITY-001","GOV-FILE-BRIDGE-AUTHORITY-001","GOV-ARTIFACT-ORIENTED-GOVERNANCE-001","DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001","DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001","SPEC-AUQ-POLICY-ENGINE-001","ADR-ISOLATION-APPLICATION-PLACEMENT-001","GOV-STANDING-BACKLOG-001","ADR-CODEX-HOOK-PARITY-FALLBACK-001","ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001","DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001","DCL-CROSS-HARNESS-ENFORCEMENT-001","DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001","GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","GOV-DOCUMENT-AUTHOR-PROVENANCE-001","GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001","DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001","GOV-WORK-TREE-HYGIENE-001"],"project_id":"PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY","target_paths":["bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-003.md"],"work_item_id":"WI-5144"},"requested_project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE","schema_version":1,"selected_project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE","selector_mode":"explicit","taxonomy_sha256":"7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233","taxonomy_version":"1"}
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5144
Latest Bridge Status: ABSENT
Reviewed Proposal Version: 1

target_paths: ["bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-003.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

This proposal performs no MemBase or KB mutation or write. The legacy gtkb-wi5144-hp08-semantic-adapter-drift chain cannot accept a governed revision because immutable v005 lacks the canonical adjacent Responds to link required by the current lifecycle resolver. Quarantine that historical chain and use this evidence-only recovery to validate the current clean HP08 implementation at HEAD. The active project authorization permits bridge and governance evidence but forbids git_commit, so this thread must remain nonterminal until a separate narrow finalization authorization covers the two by-reference implementation paths and the atomic terminal artifacts.

Work item description: Turn MOD-HP01 through MOD-HP14 into semantic-equivalence, per-harness delivery, skill and resource discoverability, session isolation, role bootstrap, transcript corpus, fallback, and verification packages.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5144` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-003.md`.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
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
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-HARNESS-PARITY-WORK-PACKET` - Approve GT-KB Modernization Harness Context Parity work packet
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-HANDLE-MAP` - GT-KB Platform Modernization Gate 0 94-handle backlog map
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-RECONCILIATION` - GT-KB Platform Modernization Gate 0 reconciliation inventory
- `DELIB-202667371` - Loyal Opposition Verification Verdict - NO-GO - WI-5639 Scan Helper Exact Numbered Chain Fallback
- `DELIB-20266439` - Separation Check

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5144`.

## Proposed Scope

- Treat the legacy v001-v010 chain as read-only historical evidence; do not rewrite, delete, or rely on it for terminal finalization.
- Do not modify scripts/check_harness_parity.py or platform_tests/scripts/test_check_harness_parity.py; validate their current HEAD identities and clean worktree state by reference.
- After independent GO, acquire the exact go_implementation claim and implementation-start packet only for creating the v003 current-head evidence report.
- Record current HEAD, Git blob ids, SHA256 values, focused HP08 results, full-module results, Ruff results, and diff checks in v003.
- Do not stage, commit, push, deploy, release, mutate dispatcher state, or file a terminal verdict under the current authorization.

## Cross-Harness Disposition

- **codex**: HP08 semantic adapter validation is exercised through the shared checker and exact focused regressions.
- **antigravity**: HP08 semantic adapter validation is exercised through the same shared checker and exact focused regressions.
- **compact-api**: Managed compact API adapters remain covered by the shared semantic-equivalence checker; no harness-specific mutation is proposed.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5144; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Turn MOD-HP01 through MOD-HP14 into semantic-equivalence, per-harness delivery, skill and resource discoverability, session isolation, role bootstrap, transcript corpus, fallback, and verification packages.",
  "after_behavior": "This proposal performs no MemBase or KB mutation or write. The legacy gtkb-wi5144-hp08-semantic-adapter-drift chain cannot accept a governed revision because immutable v005 lacks the canonical adjacent Responds to link required by the current lifecycle resolver. Quarantine that historical chain and use this evidence-only recovery to validate the current clean HP08 implementation at HEAD. The active project authorization permits bridge and governance evidence but forbids git_commit, so this thread must remain nonterminal until a separate narrow finalization authorization covers the two by-reference implementation paths and the atomic terminal artifacts.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5144",
    "project": "PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY",
    "target_paths": [
      "bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-003.md"
    ],
    "linked_specifications": [
      "ADR-CROSS-HARNESS-PARITY-001",
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
      "DCL-CROSS-HARNESS-ENFORCEMENT-001",
      "DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
      "GOV-DOCUMENT-AUTHOR-PROVENANCE-001",
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "GOV-WORK-TREE-HYGIENE-001"
    ]
  },
  "expected_result": {
    "summary": "This proposal performs no MemBase or KB mutation or write. The legacy gtkb-wi5144-hp08-semantic-adapter-drift chain cannot accept a governed revision because immutable v005 lacks the canonical adjacent Responds to link required by the current lifecycle resolver. Quarantine that historical chain and use this evidence-only recovery to validate the current clean HP08 implementation at HEAD. The active project authorization permits bridge and governance evidence but forbids git_commit, so this thread must remain nonterminal until a separate narrow finalization authorization covers the two by-reference implementation paths and the atomic terminal artifacts.",
    "scope": [
      "Treat the legacy v001-v010 chain as read-only historical evidence; do not rewrite, delete, or rely on it for terminal finalization.",
      "Do not modify scripts/check_harness_parity.py or platform_tests/scripts/test_check_harness_parity.py; validate their current HEAD identities and clean worktree state by reference.",
      "After independent GO, acquire the exact go_implementation claim and implementation-start packet only for creating the v003 current-head evidence report.",
      "Record current HEAD, Git blob ids, SHA256 values, focused HP08 results, full-module results, Ruff results, and diff checks in v003.",
      "Do not stage, commit, push, deploy, release, mutate dispatcher state, or file a terminal verdict under the current authorization."
    ],
    "acceptance_criteria": [
      "Fresh v001 is mechanically valid, independently reviewable, and identifies the invalid historical-chain boundary.",
      "Independent v002 GO and an exact implementation-start packet precede the v003 evidence report.",
      "The v003 report proves both implementation paths are unchanged and clean at the reported HEAD and records exact reproducible verification results.",
      "The thread remains nonterminal until a separate narrow project authorization permits atomic local commit finalization of the two by-reference targets plus the report and verdict."
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
| `ADR-CROSS-HARNESS-PARITY-001` | Run the HP08-focused selection in platform_tests/scripts/test_check_harness_parity.py and require all selected semantic-adapter checks to pass. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this specification-to-test mapping and exact observed commands into the v003 report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Run the complete test_check_harness_parity.py module and disclose every result, including any unrelated registry-extra baseline. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Confirm the checker rejects hash-current but semantically contradictory managed adapters across the applicable harness projections. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Record current Git blobs and SHA256 values for both by-reference paths and prove they are unchanged before and after evidence collection. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-WORK-TREE-HYGIENE-001` | Run exact-path git status and git diff checks and require no modification or staging of the two by-reference paths. |

## Acceptance Criteria

- Fresh v001 is mechanically valid, independently reviewable, and identifies the invalid historical-chain boundary.
- Independent v002 GO and an exact implementation-start packet precede the v003 evidence report.
- The v003 report proves both implementation paths are unchanged and clean at the reported HEAD and records exact reproducible verification results.
- The thread remains nonterminal until a separate narrow project authorization permits atomic local commit finalization of the two by-reference targets plus the report and verdict.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `bridge/gtkb-wi5144-hp08-current-head-finalization-recovery-003.md`

## Recommended Commit Type

`feat`
