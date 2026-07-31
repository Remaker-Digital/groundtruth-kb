NEW
::init gtkb lo
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Fix _post_go_chain_state misclassifying a REVISED proposal after a NO-ACTION-voided GO as awaiting_review

bridge_kind: prime_proposal
Document: gtkb-wi5454-post-go-chain-state
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5454-POST-GO-CHAIN-STATE-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5454

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Correct the authorization chain classifier so a historical GO voided by Prime NO-ACTION cannot cause a later corrected NO-GO plus REVISED proposal to be mistaken for a post-implementation report awaiting review.

Work item description: scripts/implementation_authorization.py::_post_go_chain_state()/approved_files_for_go() walk back to the MOST RECENT historical GO in a bridge chain and classify everything after it by the latest status alone, per the docstring assumption that any NEW/REVISED filed after a GO is always a post-implementation report. That assumption is false when a GO is voided by NO-ACTION (no implementation ever happened) and superseded by a corrected NO-GO plus a fresh REVISED proposal: the tool still reports 'Post-implementation report is awaiting Loyal Opposition review', a spurious pre-GO dry-run failure. Confirmed live on gtkb-dispatcher-black-box-spec-foundation (chain: 014 GO, 015 NO-ACTION, 016 NO-GO, 017 REVISED) during review of -017; running 'implementation_authorization.py begin --no-write' pre-GO against the current REVISED content incorrectly reports awaiting_review even though the proposal is sound. Once a fresh GO is filed as the new latest version the classification self-corrects (go_index recomputes to the new GO), so this does not block real implementation-start, but it makes the file-bridge-protocol.md-recommended pre-GO coherence dry run unreliable for exactly the chain shape this thread exhibits, and a future reviewer could mistake the spurious error for a real blocker and issue a bogus NO-GO.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5454` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/implementation_authorization.py`, `platform_tests/scripts/test_implementation_authorization.py`.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires bounded PAUTH envelopes for new authorization state.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - auto-linked governing or work-item specification.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260704-WITHDRAW-GTKB-WI4683-ACTIVITY-VOCABULARY-RECONCILE-OPS-GO` - Withdraw stale WI-4683 router vocabulary GO
- `DELIB-20264732` - GT-KB Rollback Receipts - Codex Review of REVISED-3
- `DELIB-1032` - GTKB Work Subject And Root Enforcement - Post-Implementation Posture Review
- `DELIB-20264706` - Loyal Opposition Review - Role Enhancement Isolation Dependency Reframe Heading Fix
- `DELIB-2756` - Loyal Opposition Review - Role Enhancement Isolation Dependency Reframe Heading Fix

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5454-POST-GO-CHAIN-STATE-20260718` - active project authorization covering `WI-5454`.

## Proposed Scope

- Hard-gate implementation behind terminal focused WI-5382, clean exact target preimages, independent GO, exact claim, and schema-v3 implementation-start authorization.
- Treat NO-ACTION after a historical GO as revoking that GO for later pre-GO classification; a corrected NO-GO followed by NEW or REVISED must require a fresh GO.
- Preserve true post-GO implementation-report NEW/REVISED awaiting-review denials and post-GO NO-GO resumability.
- Preserve latest fresh GO selection and terminal VERIFIED, DEFERRED, and latest NO-ACTION denials with deterministic diagnostics.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5454; PAUTH-DISPATCHER-BLACK-BOX-WI5454-POST-GO-CHAIN-STATE-20260718; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "scripts/implementation_authorization.py::_post_go_chain_state()/approved_files_for_go() walk back to the MOST RECENT historical GO in a bridge chain and classify everything after it by the latest status alone, per the docstring assumption that any NEW/REVISED filed after a GO is always a post-implementation report. That assumption is false when a GO is voided by NO-ACTION (no implementation ever happened) and superseded by a corrected NO-GO plus a fresh REVISED proposal: the tool still reports 'Post-implementation report is awaiting Loyal Opposition review', a spurious pre-GO dry-run failure. Confirmed live on gtkb-dispatcher-black-box-spec-foundation (chain: 014 GO, 015 NO-ACTION, 016 NO-GO, 017 REVISED) during review of -017; running 'implementation_authorization.py begin --no-write' pre-GO against the current REVISED content incorrectly reports awaiting_review even though the proposal is sound. Once a fresh GO is filed as the new latest version the classification self-corrects (go_index recomputes to the new GO), so this does not block real implementation-start, but it makes the file-bridge-protocol.md-recommended pre-GO coherence dry run unreliable for exactly the chain shape this thread exhibits, and a future reviewer could mistake the spurious error for a real blocker and issue a bogus NO-GO.",
  "after_behavior": "Correct the authorization chain classifier so a historical GO voided by Prime NO-ACTION cannot cause a later corrected NO-GO plus REVISED proposal to be mistaken for a post-implementation report awaiting review.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5454",
    "project": "PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING",
    "target_paths": [
      "scripts/implementation_authorization.py",
      "platform_tests/scripts/test_implementation_authorization.py"
    ],
    "linked_specifications": [
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
      "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001",
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001",
      "DCL-PROJECT-DEPENDENCY-ORDERING-001",
      "DCL-NO-ACTION-STATUS-SEMANTICS-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
      "GOV-WORK-TREE-HYGIENE-001"
    ]
  },
  "expected_result": {
    "summary": "Correct the authorization chain classifier so a historical GO voided by Prime NO-ACTION cannot cause a later corrected NO-GO plus REVISED proposal to be mistaken for a post-implementation report awaiting review.",
    "scope": [
      "Hard-gate implementation behind terminal focused WI-5382, clean exact target preimages, independent GO, exact claim, and schema-v3 implementation-start authorization.",
      "Treat NO-ACTION after a historical GO as revoking that GO for later pre-GO classification; a corrected NO-GO followed by NEW or REVISED must require a fresh GO.",
      "Preserve true post-GO implementation-report NEW/REVISED awaiting-review denials and post-GO NO-GO resumability.",
      "Preserve latest fresh GO selection and terminal VERIFIED, DEFERRED, and latest NO-ACTION denials with deterministic diagnostics."
    ],
    "acceptance_criteria": [
      "The exact chain NEW -> GO -> NO-ACTION -> NO-GO -> REVISED fails as requiring a fresh GO and never reports that a post-implementation report awaits review.",
      "Appending a fresh independent GO to that chain authorizes the revised proposal and selects the fresh GO file.",
      "Existing true post-GO NEW, REVISED, NO-GO, VERIFIED, DEFERRED, and NO-ACTION regression cases remain unchanged.",
      "Focused tests, full implementation-authorization tests, Ruff check, Ruff format check, py_compile, and git diff --check pass."
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
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused and complete implementation-authorization test file and report exact commands and observed results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Exercise approved_files_for_go and packet creation to prove no stale GO can mint authorization while the chain awaits a fresh GO. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Verify implementation remains blocked until terminal focused WI-5382 and clean two-target preimages are observed. |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Add direct chain-state tests for a NO-ACTION-voided GO, corrected NO-GO, later REVISED proposal, and a subsequent fresh GO. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run all existing post-GO lifecycle regression cases and compare deterministic denial categories and messages. |
| `GOV-WORK-TREE-HYGIENE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- The exact chain NEW -> GO -> NO-ACTION -> NO-GO -> REVISED fails as requiring a fresh GO and never reports that a post-implementation report awaits review.
- Appending a fresh independent GO to that chain authorizes the revised proposal and selects the fresh GO file.
- Existing true post-GO NEW, REVISED, NO-GO, VERIFIED, DEFERRED, and NO-ACTION regression cases remain unchanged.
- Focused tests, full implementation-authorization tests, Ruff check, Ruff format check, py_compile, and git diff --check pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`feat`
