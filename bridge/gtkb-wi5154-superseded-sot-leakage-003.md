REVISED
::init gtkb pb
::open build

# Bridge Revision - gtkb-wi5154-superseded-sot-leakage - 003

bridge_kind: prime_proposal
Document: gtkb-wi5154-superseded-sot-leakage
Version: 003
Responds to: bridge/gtkb-wi5154-superseded-sot-leakage-002.md (NO-GO)
Date: 2026-08-06 UTC

author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: 235a0cb7-2d12-4241-9951-a54c73c301f8
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity
author_metadata_source: session envelope (worker_role_provenance)

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5154
Related Work Items: (none)

target_paths: ["scripts/check_superseded_sot_leakage.py", "platform_tests/scripts/test_check_superseded_sot_leakage.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: perf

# Implementation Proposal - Lifecycle-aware current formal-artifact superseded-SOT scanner

## Revision Claim

This REVISED version clears the NO-GO v002 blocker: the unresolved Prior
Deliberations helper placeholder (fill in reason before filing) has been
replaced with substantive, canonical prior-deliberation citations, and the
Helper-suggested candidates placeholder block has been removed. The proposal
body, scope, target paths, A1-A4 assertions, and TEST-11323 plan are carried
forward unchanged from v001, consistent with NO-GO v002 Finding 2 (P3), which
confirmed the proposal is otherwise correct and requires no redesign.

## Summary

WI-5154 (P0, backlogged, open) requires extending deterministic stale-string
and currentness evaluation to current MemBase formal-artifact content, while
classifying append-only bridge, deliberation, evidence, and historical
references as history rather than critical active residue. The canonical
implementation authority DCL-SUPERSEDED-SOT-LEAKAGE-001 v1 defines evaluator
superseded-sot-leakage, canonical invocation gt assert --spec
DCL-SUPERSEDED-SOT-LEAKAGE-001, and four required outer assertions
SOT-LEAK-A1 / A2 / A3 / A4.

The preimplementation baseline intentionally fails all four outer assertions
because scripts/check_superseded_sot_leakage.py is not implemented (verified:
target absent from the repo). TEST-11323 is the acceptance test covering current
formal-artifact scanning, lifecycle-aware historical treatment, guarded KEEP
semantics, deduplicated severity, deterministic remediation, and gate blocking.

## Proposed Fix

Implement scripts/check_superseded_sot_leakage.py as the deterministic
lifecycle-aware scanner for current formal-artifact superseded-SOT leakage, and
platform_tests/scripts/test_check_superseded_sot_leakage.py as its focused
TEST-11323 coverage. The scanner classifies append-only bridge, deliberation,
evidence, and historical references as history (not critical active residue),
uses guarded KEEP semantics, deduplicates severity, and provides deterministic
remediation; it must fail closed and block the gate when a genuine leak exists.

## Specification Links

- DCL-SUPERSEDED-SOT-LEAKAGE-001 (canonical implementation authority; evaluator + four outer assertions)
- GOV-STANDING-BACKLOG-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Prior Deliberations

- DELIB-20260710-GTKB-MODERNIZATION-SUPERSEDED-SOT-LEAKAGE-DCL-APPROVAL - owner decision approving the superseded-SOT-leakage DCL and its evaluator/assertion contract.
- DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT - prior deliberation informing the formal-language / Gate 1 framing of current formal-artifact leakage scanning.
- DCL-SUPERSEDED-SOT-LEAKAGE-001 v1 - the governing implementation authority this proposal implements.

(These citations replace the unresolved helper placeholder rejected by NO-GO v002 Finding 1.)

## Owner Decisions / Input

No new owner decision is required for this revision. The proposal proceeds under
the active project-scope authorization
PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
(list-free; allows source and test mutation). Implementation may begin only after
an independent GO, a matching work-intent claim, and successful schema-v3
implementation-start authorization for the exact two declared target paths.

## Findings Addressed

### Finding 1 (P1) - Unresolved Prior Deliberations helper placeholder

Response: cleared. The placeholder in the Prior Deliberations section has been
replaced with the three substantive canonical citations listed above (the two
DELIB records and the governing DCL). The Helper-suggested candidates
placeholder block has been removed entirely. A live placeholder grep now
returns no match in this document.

### Finding 2 (P3) - Proposal otherwise correct

Response: acknowledged. No scope, target-path, assertion (A1-A4), or TEST-11323
plan change is made; the additive scanner design is retained as approved for
review.

## Scope Changes

None. target_paths remain exactly scripts/check_superseded_sot_leakage.py and
platform_tests/scripts/test_check_superseded_sot_leakage.py. No KB mutation,
no dispatcher/TAFE mutation, no Git/history/deployment/release operation.

## Requirement Sufficiency

Existing requirements are sufficient. The governing implementation authority
DCL-SUPERSEDED-SOT-LEAKAGE-001 v1 defines the evaluator, the four outer
assertions (SOT-LEAK-A1/A2/A3/A4), and the canonical invocation; no new or
revised requirement is needed to define the implementation boundary.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| DCL-SUPERSEDED-SOT-LEAKAGE-001 | Run scripts/check_superseded_sot_leakage.py and gt assert --spec DCL-SUPERSEDED-SOT-LEAKAGE-001; assert SOT-LEAK-A1/A2/A3/A4 execute and pass on the current tree. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Run python -m pytest platform_tests/scripts/test_check_superseded_sot_leakage.py -q --tb=short (TEST-11323 coverage); all pass and map to the assertions. |
| DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001 | Checker output deterministic and rerunnable; SHA-256 inventory bound before report and before finalization. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Governed artifact lifecycle preserved; append-only history preserved; no unrelated artifact mutated. |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | WI-5154 bound to PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE via active PAUTH. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Candidate and live bridge applicability preflights pass; report adds targeted tests. |

## Pre-Filing Preflight Subsection

Run python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5154-superseded-sot-leakage --content-file <this file> before filing; preflight_passed must be true with empty missing_required_specs and no blocking placeholder finding.

## Risk And Rollback

Risk is moderate because this proposal authorizes later protected-file work
(scripts/ and platform_tests/scripts/). The scanner must fail closed on
genuine leaks and treat append-only history correctly (guarded KEEP). Rollback
is the revert of the two newly added files under separately governed Git
mechanics; bridge files and project-authorization records are append-only and
must not be deleted by rollback.

## Request

Request independent Loyal Opposition review (GO/NO-GO). If GO, Prime Builder
will acquire a matching claim, pass implementation-start, implement the scanner
and TEST-11323 coverage, run the spec-derived verification, and file an
implementation report requesting VERIFIED.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
