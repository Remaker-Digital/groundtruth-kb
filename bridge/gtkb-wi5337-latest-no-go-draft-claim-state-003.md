REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; reasoning=xhigh; approval_policy=never

# Revised Implementation Proposal - Guard Latest NO-GO Draft Classification Against Recurrence

bridge_kind: prime_proposal
Document: gtkb-wi5337-latest-no-go-draft-claim-state
Version: 003
Responds to: bridge/gtkb-wi5337-latest-no-go-draft-claim-state-002.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5337-LATEST-NO-GO-CLAIM-STATE-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5337
target_paths: ["platform_tests/scripts/test_bridge_work_intent_registry.py"]
implementation_scope: test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Version 002 correctly established that committed HEAD already classifies a
latest NO-GO as `draft` and that the originally named helper was never part of
the committed baseline. Since that review, WI-5307 reached independent
VERIFIED at version 018 while retaining the same latest-status behavior in the
working candidate.

This revision therefore removes all source mutation. It preserves the observed
working-tree regression as a recurrence risk and proposes one exact test-only
guard: a numbered `NEW -> GO -> NO-ACTION -> NO-GO` chain must acquire a normal
Prime `draft` claim, while a latest-GO control chain must acquire
`go_implementation`. No production predicate or claim service is changed.

## Requirement Sufficiency

Existing requirements are sufficient for this test-only recurrence guard. The
active WI-5337 PAUTH includes test mutation, and implementation remains gated by
a fresh GO, exact PB claim, implementation-start packet, independent
verification, and focused finalization.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authorization for bounded fleet-defect repair proposals while preserving normal implementation gates.
- `bridge/gtkb-wi5337-latest-no-go-draft-claim-state-001.md` - original source-and-test proposal.
- `bridge/gtkb-wi5337-latest-no-go-draft-claim-state-002.md` - independent NO-GO requiring committed-baseline correction and finalizable scope.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-018.md` - independent VERIFIED baseline disposition for the shared registry source.
- `bridge/gtkb-wi5249-prime-no-action-claim-filer-008.md` - terminal stand-down of active `no_action_correction` acquisition; this revision does not restore it.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this bounded hygiene follow-on.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5337-LATEST-NO-GO-CLAIM-STATE-20260716` remains active and includes WI-5337 test mutation.
- No new owner decision is required to file this narrower revision.

## Findings Addressed

### F1 - Defect premise did not reproduce against committed baseline

Accepted. The revision no longer claims committed production code needs a fix
and removes `scripts/bridge_work_intent_registry.py` from `target_paths`. The
scope is now a regression test for behavior that committed HEAD already has.

### F2 - Named helper existed only in uncommitted, unstable state

Accepted. The revised implementation does not reference, create, or modify
`_go_implementation_claim_applies`. The test exercises the public `acquire`
behavior against an exact committed-HEAD candidate and is finalizable as one
additive test hunk.

### F3 - Dirty-hunk ownership was incorrectly described

Corrected by eliminating the shared source target. WI-5307 versions 015 through
018 did in fact include `scripts/bridge_work_intent_registry.py` and are now
terminal VERIFIED, but this revision does not depend on adopting that dirty
source. The test file's existing WI-5279/WI-5249 hunks remain foreign and are
excluded from the exact WI-5337 candidate and any focused finalization.

### Supporting finding - No committed decision governed the transient helper

Accepted. No decision or implementation is proposed for that transient helper.
The governing claim is limited to the stable externally observable claim-kind
classification already present in committed HEAD.

## Scope Changes

- Remove `scripts/bridge_work_intent_registry.py` from the implementation scope.
- Add one focused regression test only in `platform_tests/scripts/test_bridge_work_intent_registry.py`.
- Exercise a complete numbered `NEW -> GO -> NO-ACTION -> NO-GO` chain and assert normal acquisition produces `claim_kind=draft` with no implementation deadline.
- Exercise a latest-GO control chain and assert normal acquisition still produces `claim_kind=go_implementation` with its bounded deadline.
- Preserve project-authorization bootstrap behavior, the WI-5249 stand-down, role provenance, existing claim timing, and every foreign dirty hunk.

## Pre-Filing Preflight Subsection

- Applicability command: `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5337-latest-no-go-draft-claim-state-003.md --bridge-id gtkb-wi5337-latest-no-go-draft-claim-state --json`
- Applicability result: exit 0; `preflight_passed: true`; no missing required or advisory specifications.
- Clause command: `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5337-latest-no-go-draft-claim-state-003.md --bridge-id gtkb-wi5337-latest-no-go-draft-claim-state`
- Clause result: exit 0; zero blocking gaps.

## Verification Plan

| Governing requirement | Focused verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Require exact GO, PB claim, implementation-start, report, and independent verdict before finalization. |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Build the complete GO/NO-ACTION/NO-GO chain and assert the latest NO-GO controls normal claim classification. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Assert latest GO remains an implementation claim; do not change or bypass production PAUTH gates. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused test against an exact HEAD-plus-WI-5337 candidate and carry the command and result into the implementation report. |
| Artifact lifecycle specifications | Preserve WI-5337, TEST-11466, PAUTH, proposal chain, exact-hunk evidence, and verdict as the durable record. |

## Acceptance Criteria

1. No production source file changes under WI-5337.
2. A complete latest-NO-GO chain acquires `draft` and has no implementation deadline or grace period.
3. A latest-GO control chain still acquires `go_implementation` with bounded implementation timing.
4. The focused registry test passes from committed HEAD plus only the WI-5337 test hunk.
5. Existing dirty test hunks remain excluded from the candidate, report, and focused finalization.

## Risk And Rollback

Risk is low because the revision adds only a recurrence test for existing
behavior. The main risk is accidental capture of foreign test hunks; exact
HEAD-plus-candidate verification and hunk-scoped finalization are mandatory.

Rollback is removal of the single WI-5337 test hunk. Bridge files remain
append-only. No source, dispatcher, TAFE, runtime, database, credential,
deployment, release, push, or history-rewrite operation is authorized.

## Recommended Commit Type

`test:`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
