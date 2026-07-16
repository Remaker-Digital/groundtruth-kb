NEW

# Implementation Proposal - Stabilize workflow tamper diagnostics after envelope hardening

bridge_kind: prime_proposal
Document: gtkb-wi5367-workflow-tamper-diagnostic
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5367

target_paths: ["groundtruth-kb/src/groundtruth_kb/modernization/workflow.py", "platform_tests/scripts/test_modernization_workflow_diagnostics.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Preserve the strengthened session-envelope provenance validator while restoring
the modernization workflow's stable public distinction between a missing
runtime session and a present-but-invalid authoritative session document.

The workflow currently forwards the earlier internal validation exception, so
the frozen tamper acceptance expects a public provenance-conflict diagnostic but
receives an internal role-field conflict. The repair classifies failure from
authoritative document state rather than matching exception prose: if the exact
requested session document exists, validation failure is reported as a public
provenance conflict; if it does not exist, the existing pre-existing-session
requirement remains the public error. The original internal exception remains
the chained cause for diagnostics and testing.

The workflow source is currently an untracked WI-5315 candidate absent from
HEAD. WI-5367 implementation is prohibited until WI-5315's exact four-file
baseline is independently VERIFIED and mechanically finalized. The existing
untracked acceptance module is not a WI-5367 target; a new focused test module
keeps successor evidence and finalization separable.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` - the workflow must consume validated session role provenance and reject contradictions fail closed.
- `ADR-ENVELOPE-META-MODEL-001` - the session document is the authoritative runtime envelope in interactive and dispatched flows.
- `DCL-ENVELOPE-META-MODEL-001` - envelope invocation, intent, and payload evidence must remain coherent and attributable.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - the public workflow behavior applies uniformly to any valid Prime Builder or Loyal Opposition harness identity.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - missing and contradictory authority require stable, evaluable failure outcomes rather than incidental internal wording.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the frozen end-to-end tamper assertion remains executable and blocking.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - stronger internal validation is preserved; no acceptance assertion, provenance field, or failure gate is weakened.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness remains blocked until the end-to-end workflow activity is green.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5315 exact baseline stabilization and finalization are hard predecessors to WI-5367 source mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, predecessor, successor patch, focused tests, and verdict remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5367 remains blocked on its predecessor, then open through implementation and independent verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the newly exposed diagnostic drift is preserved as an origin=hygiene work item.
- `GOV-STANDING-BACKLOG-001` - WI-5367 durably owns this successor repair.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - both protected targets require independent GO, matching claim/start authority, reporting, and independent VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - exact source/test targets and their WI-5315 dependency are linked to governing carriers.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification executes missing, tampered, wrong-session, and frozen acceptance cases.

## Prior Deliberations

- `DELIB-202666274` - authorizes modernization at project scope while retaining predecessor, independent review, and exact Git gates.

## Owner Decisions / Input

No new owner decision is required. The active Assurance PAUTH covers this
source/test successor after WI-5315 is stable. This proposal does not authorize
early mutation of WI-5315 candidates, dispatcher/TAFE/harness mutation, direct
harness contact, manual routing, database mutation, Git staging/commit/push,
deployment, release, credentials, or cleanup.

## Requirement Sufficiency

Existing requirements are sufficient. The frozen acceptance contract already
requires both missing-envelope and tampered-envelope failures, while current
session authority carriers require fail-closed provenance validation. The gap is
public error normalization across a strengthened validation boundary, not a new
authority or workflow requirement.

## Proposed Scope

1. Require WI-5315 exact baseline VERIFIED and present in HEAD before any WI-5367 target mutation or claim/start.
2. Add a private read-only helper that checks whether the exact requested session ID has a document below any harness's canonical session-document directory without interpolating the ID into a filesystem path.
3. Catch the typed session-envelope validation exception separately from generic I/O/value errors.
4. When an exact requested document exists but validation fails, raise the stable public provenance-conflict workflow error and chain the original internal exception.
5. When no exact requested document exists, preserve the current public pre-existing-runtime-session error and chain the original exception.
6. Do not parse, pattern-match, expose, suppress, or rewrite internal validation messages.
7. Add a new focused test module covering exact-document tamper, missing document, unrelated-session document, exception chaining, and no workspace mutation.
8. Rerun the frozen tamper acceptance unchanged; do not edit or weaken the WI-5315 acceptance baseline.
9. Exclude session-envelope validator changes, PAUTH/start-packet failures owned by WI-5178, dispatcher/harness state, and all other workflow behavior.

## Cross-Harness Disposition

No typed waiver is requested. The implementation is in the shared modernization
workflow and has identical observable behavior for any registered harness. No
harness-specific hook, role map, eligibility, routing, or invocation surface is
changed. Claude, Codex, Cursor, Antigravity, Ollama, OpenRouter, and Alibaba
retain their existing runtime surfaces; only validated session-document state
determines the public error class.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5367 focused frozen-acceptance reproduction under DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "frozen AT-END-TO-END-WORKFLOW tampered-session acceptance",
  "before_behavior": "A present tampered session document is rejected early by stronger validation but leaks an internal role-field conflict through the public workflow error.",
  "after_behavior": "The same tampered document is rejected at the same boundary with a stable public authoritative-provenance conflict while the internal exception remains chained.",
  "self_descriptive_naming": "The helper asks whether the exact runtime session document exists; public errors name missing-session versus provenance-conflict states.",
  "obsolete_guidance_disposition": "No validation rule or acceptance assertion is retired; only incidental internal-message forwarding is removed from the public boundary.",
  "history_preservation": "The exact WI-5315 baseline and strengthened WI-5328 envelope validation remain unchanged and independently attributable.",
  "baseline": {
    "focused_tamper_acceptance_passed": 0,
    "focused_tamper_acceptance_failed": 1,
    "tamper_rejected": true,
    "public_error_contract_matched": false
  },
  "expected_result": {
    "focused_tamper_acceptance_passed": 1,
    "focused_tamper_acceptance_failed": 0,
    "tamper_rejected": true,
    "public_error_contract_matched": true,
    "internal_exception_chained": true
  },
  "rollback": "Revert only the post-WI-5315 workflow normalization hunk and new focused test through a separately governed transaction; preserve the WI-5315 baseline and envelope validator.",
  "hard_invariants": [
    "tampered session authority always fails before workspace mutation",
    "missing and present-invalid sessions remain distinguishable",
    "internal validation remains stronger and unchanged",
    "no error classification depends on exception text",
    "no harness role, route, eligibility, or document is mutated",
    "no WI-5367 source mutation occurs before WI-5315 finalization"
  ],
  "fail_closed_conditions": [
    "exact session-document state cannot be evaluated",
    "tamper acceptance is weakened, skipped, or xfailed",
    "internal validation details become the public contract",
    "an unrelated session document is mistaken for the requested session",
    "the predecessor baseline is absent from HEAD"
  ],
  "essential_context_preservation": "Exact session identity, authoritative document presence, strong provenance validation, public error taxonomy, predecessor ownership, and no-mutation-before-authentication remain explicit."
}
```

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Predecessor ordering | Confirm WI-5315 exact baseline is independently VERIFIED and present in HEAD before claim/start | No WI-5367 source patch is applied to an untracked foreign baseline. |
| Present-invalid classification | Focused fixture creates the exact requested session document and injects a typed validation failure | Public error states authoritative provenance conflict; original exception is chained. |
| Missing classification | Focused fixture injects the same typed failure with no exact requested document | Public error retains the pre-existing runtime-session requirement. |
| Exact identity | Focused fixture creates only another session ID's document | Unrelated state is not treated as the requested authoritative document. |
| Fail-closed behavior | Rerun the unchanged frozen tamper acceptance and assert no Git/workspace target is created | Tamper remains rejected before mutation and the public contract passes. |
| Focused regression | `python -m pytest platform_tests/scripts/test_modernization_workflow_diagnostics.py -q --tb=short` | All state-classification, chaining, and no-mutation tests pass. |
| Broader workflow | Run the full frozen end-to-end workflow activity after WI-5178 completes | The tamper case is green; no WI-5367 regression adds failures to other cases. |
| Scope isolation | Compare pre-start hashes and patch paths after the WI-5315 baseline commit | Only the workflow normalization and new focused test are owned by WI-5367. |

## Acceptance Criteria

1. WI-5315 exact baseline is VERIFIED and finalized before implementation starts.
2. Present-but-invalid exact session documents produce the stable public provenance-conflict error.
3. Missing exact session documents retain the pre-existing-session error.
4. Classification uses exact filesystem state, never internal exception text.
5. The original validation exception remains chained and the validator is unchanged.
6. The unchanged frozen tamper acceptance passes without creating a workspace Git repository or target.
7. The new focused diagnostics module passes all cases.
8. WI-5178 failures and all unrelated/concurrent bytes remain outside scope.
9. Independent Loyal Opposition review returns VERIFIED before completion is claimed.

## Risk / Rollback

The main risk is misclassifying another session's document as the requested
authority. Exact filename equality after bounded directory enumeration prevents
that. A second risk is weakening validation to recover old wording; this design
does not change the validator and normalizes only at the public workflow
boundary after validation has already failed.

Rollback reverts only the WI-5367 workflow hunk and new focused test through a
separately governed transaction. It preserves WI-5315, WI-5328, WI-5178,
session documents, database state, harness state, and bridge history.

## Bridge Filing

File this as the next append-only numbered proposal for
`gtkb-wi5367-workflow-tamper-diagnostic`. Deterministic TAFE/bridge routing is
external to this session; no manual routing or direct harness contact occurs.

## Recommended Commit Type

`fix` - stabilizes a public failure contract while retaining stronger validation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
