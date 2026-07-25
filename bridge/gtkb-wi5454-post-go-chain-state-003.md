REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6f8b-9fd7-7142-93a8-5696dca44d85
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; owner-declared role via ::init gtkb pb; thread_source=user
author_metadata_source: explicit current-session bridge filing metadata

# Revised Implementation Proposal - WI-5454 Post-GO Chain State

bridge_kind: prime_proposal
Document: gtkb-wi5454-post-go-chain-state
Version: 003
Responds to: bridge/gtkb-wi5454-post-go-chain-state-002.md
Date: 2026-07-21 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5454-POST-GO-CHAIN-STATE-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5454

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Reason

Version 001 proposed the correct two-file WI-5454 implementation scope, and version 002 approved that design after independent Loyal Opposition review. The current implementation-start gate now rejects version 001 as an implementation authority because version 001 contains incomplete machine-readable author-role metadata (`author_identity: codex`) rather than a Prime Builder author identity. No source or test implementation was started under that unusable GO.

This revision appends a role-correct Prime Builder proposal entry instead of editing historical bridge files. The version 002 GO is therefore treated as non-operative for implementation-start; WI-5454 must receive a fresh independent Loyal Opposition GO against this version 003 content before any target file changes begin.

## Claim

Prime Builder proposes the same bounded WI-5454 implementation slice as version 001, with corrected proposal metadata and unchanged target scope. The work remains limited to `scripts/implementation_authorization.py` and `platform_tests/scripts/test_implementation_authorization.py`.

## Requirement Sufficiency

Existing requirements remain sufficient. WI-5454 and `PAUTH-DISPATCHER-BLACK-BOX-WI5454-POST-GO-CHAIN-STATE-20260718` define the implementation boundary; this revision adds no new project membership, PAUTH, dispatcher, runtime, credential, release, deployment, or cleanup authority.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/implementation_authorization.py`, `platform_tests/scripts/test_implementation_authorization.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires role-correct status-bearing bridge authority and append-only numbered files.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - prevents PAUTH from bypassing bridge GO and implementation-start gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires operation-time authority before protected target mutation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires bounded PAUTH envelopes for implementation authority.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - preserves ordered dependent work.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - covers GO-revocation semantics for NO-ACTION chain shapes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project, work item, PAUTH, and target-path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires modernization changes to avoid platform impairment.
- `GOV-WORK-TREE-HYGIENE-001` - requires scoped ownership in dirty worktrees.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves formal artifact lifecycle discipline.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves artifact-oriented development flow.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserves lifecycle-triggered formal capture.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded carriers for in-scope fleet defect repair work, subject to normal bridge review and implementation-start gates.

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5454-POST-GO-CHAIN-STATE-20260718` - active project authorization covering WI-5454.

## Proposed Scope

- Correct the authorization chain classifier so a historical GO voided by Prime `NO-ACTION`, followed by corrected Loyal Opposition `NO-GO` and a fresh `NEW` or `REVISED` proposal, requires a fresh GO instead of being mislabeled as a post-implementation report awaiting review.
- Preserve true post-GO implementation-report `NEW` and `REVISED` awaiting-review denials.
- Preserve post-GO `NO-GO` resumability for implementation corrections after an implementation report receives an independent NO-GO.
- Preserve latest fresh GO selection and terminal `VERIFIED`, `DEFERRED`, and latest `NO-ACTION` denials with deterministic diagnostics.
- Keep dispatcher configuration/runtime, TAFE state, harness registry/state/routing/eligibility/roles, provider contact, credentials, external systems, deployment, release, Git commit/push/history rewrite, destructive cleanup, and unrelated worktree paths out of scope.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5454; PAUTH-DISPATCHER-BLACK-BOX-WI5454-POST-GO-CHAIN-STATE-20260718; bridge/gtkb-wi5454-post-go-chain-state-001.md; bridge/gtkb-wi5454-post-go-chain-state-002.md",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal flow",
  "primary_route": "append-only bridge REVISED entry after unusable historical GO metadata",
  "before_behavior": "A NO-ACTION-voided historical GO followed by corrected NO-GO and a fresh proposal can be classified as a post-implementation report awaiting review. The current WI-5454 GO is also unusable by the implementation-start gate because the reviewed proposal version has incomplete author-role metadata.",
  "after_behavior": "The implementation-start classifier requires a fresh GO for NO-ACTION-voided proposal chains, preserves real post-implementation awaiting-review and NO-GO-resume behavior, and this revised proposal can receive a fresh role-correct GO.",
  "self_descriptive_naming": "The bridge slug, WI-5454 identifier, target paths, and scope name the chain-state authorization behavior being corrected.",
  "obsolete_guidance_disposition": "No guidance is retired by this revision; implementation must explicitly disposition any obsolete code comments or tests it touches.",
  "history_preservation": "The defective metadata in version 001 and the non-operative version 002 GO remain preserved as historical bridge artifacts; this revision appends rather than edits them.",
  "baseline": {
    "work_item": "WI-5454",
    "project": "PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING",
    "target_paths": [
      "scripts/implementation_authorization.py",
      "platform_tests/scripts/test_implementation_authorization.py"
    ],
    "linked_specifications": [
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "DCL-NO-ACTION-STATUS-SEMANTICS-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"
    ]
  },
  "expected_result": {
    "summary": "A narrowly corrected implementation-start classifier and focused tests for NO-ACTION-voided proposal chains and post-implementation report chains.",
    "scope": [
      "Two approved target files only",
      "No dispatcher configuration or routing mutation",
      "No PAUTH or MemBase mutation during implementation"
    ],
    "acceptance_criteria": [
      "Fresh GO after this REVISED entry is required before source/test mutation",
      "Implementation-start packet validates the exact two approved target paths",
      "Spec-derived tests pass and post-implementation report receives independent VERIFIED"
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source/test implementation hunks under separate bridge authority if the implementation is rejected.",
    "verification": "Rerun the WI-5454 focused tests, bridge preflights, and implementation-start validation."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only declared in-root target paths are attributable to this proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain out of scope."
  ],
  "fail_closed_conditions": [
    "Fresh Loyal Opposition GO is missing after this revision.",
    "Implementation-start packet cannot validate the exact two target paths.",
    "The live worktree contains foreign dirty bytes in either approved target.",
    "Candidate or live bridge preflights fail."
  ],
  "essential_context_preservation": "This revision keeps PAUTH, project, work item, target paths, specification links, prior owner authorization, scope, verification expectations, risk, rollback, and history-preserving disposition visible."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge applicability and ADR/DCL clause preflights on this REVISED proposal and the implementation report. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Require independent GO plus `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5454-post-go-chain-state` before source/test mutation. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Validate both approved targets with `scripts/implementation_authorization.py validate --target ...` before editing. |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Add focused regression coverage for `NEW -> GO -> NO-ACTION -> NO-GO -> REVISED`, then fresh GO recovery. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map each linked spec to observed command results before LO verification. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run focused tests plus `git diff --check` and keep dispatcher config untouched. |

## Acceptance Criteria

- Fresh independent Loyal Opposition GO is filed after this REVISED proposal before implementation starts.
- `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5454-post-go-chain-state` creates a schema-v3 implementation-start packet against the fresh GO.
- `scripts/implementation_authorization.py validate` authorizes exactly `scripts/implementation_authorization.py` and `platform_tests/scripts/test_implementation_authorization.py` before mutation.
- Focused tests cover NO-ACTION-voided GO proposal chains, fresh GO recovery, true post-GO report awaiting-review state, post-GO NO-GO resumability, and terminal denial states.
- No dispatcher configuration, routing policy, credential, deployment, release, Git history, unrelated dirty file, or external system is mutated.

## Risks / Rollback

Risk is moderate because this work changes implementation-start authority classification. The revision reduces risk by requiring a fresh LO GO, operation-time target validation, focused regression tests, and independent VERIFIED before the work can unblock Slice D.

Rollback is a revert of only the approved source/test hunks under governed authority. Bridge files remain append-only historical artifacts and are not deleted.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`fix`
