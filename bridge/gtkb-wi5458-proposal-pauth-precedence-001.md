NEW

# gtkb-wi5458-proposal-pauth-precedence - Deterministic work-item PAUTH selection

bridge_kind: prime_proposal
Document: gtkb-wi5458-proposal-pauth-precedence
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5458

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: source | test | bridge protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Make the canonical `gt bridge file-implementation-proposal` authorization
resolver choose the most-specific active PAUTH that covers the requested work
item instead of returning the first covering row in database order. Exact
singleton work-item coverage must outrank multi-work-item coverage, which must
outrank unrestricted project-membership fallback. If two covering
authorizations are equally most-specific, filing must fail closed unless a
future explicit selector is independently specified and validated.

The dry-run result must identify the selected PAUTH. A failed or ambiguous
selection must create no bridge file and publish no dispatcher/TAFE state. The
implementation must preserve the existing WI-5420 cross-harness-disposition
hunks in all three target files byte-for-byte; WI-5458 source work begins only
after WI-5420 reaches terminal verification and releases those bytes.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires the filing path to use an active, bounded project authorization rather than silently broadening the implementation envelope.
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` - establishes explicit included-work-item lists as restrictive authorization boundaries and therefore more specific than unrestricted membership fallback.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires protected implementation to remain inside the exact active PAUTH selected for the work item.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the non-bypass bridge filing and requires failed authorization resolution to produce no status-bearing bridge mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the proposal to retain its exact project linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal and its eventual implementation report to cite the governing authorization and bridge specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires TEST-11559 and the implementation report to demonstrate the specification-derived cases before VERIFIED.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - requires WI-5458 to wait for WI-5420 terminalization because both own the same source and test files.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the observed live filing defect to be preserved as WI-5458, TEST-11559, this proposal, and the resulting verification evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the selected authorization and ambiguity evidence to remain reconstructable in durable project artifacts rather than transient session state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps proposal review, implementation authorization, source mutation, implementation reporting, independent verification, and finalization as distinct lifecycle transitions.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - Mike authorized bounded PAUTH carriers and governed proposals for newly discovered fleet, bridge, TAFE, dispatcher, and harness defects while preserving every later bridge, claim, implementation-start, test, independent-verification, and focused-finalization gate. This proposal applies that authority only to WI-5458.

## Owner Decisions / Input

Owner approval is recorded by
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`. The active singleton
authorization
`PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-20260717`
includes only WI-5458, the specifications above, and the three declared target
paths. It authorizes proposal filing now and protected implementation only
after independent GO, a matching claim, and an implementation-start packet.

## Requirement Sufficiency

Existing requirements sufficient. The PAUTH-envelope and restrictive
included-work-item contracts already establish that a narrower authorization
cannot be replaced silently by a broader covering authorization. This is an
implementation defect in deterministic authority resolution, not a missing
policy decision.

## Spec-Derived Verification Plan

`TEST-11559` and focused tests in
`platform_tests/groundtruth_kb/test_cli_bridge_propose.py` must demonstrate:

| Governing requirement | Verification | Expected result |
|---|---|---|
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`; `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` | Seed covering active PAUTHs in both insertion orders: exact singleton, multi-work-item, and unrestricted membership fallback. | Exact singleton is selected in both orders; removing it selects the narrower multi-work-item row before unrestricted fallback. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Seed two equally most-specific active PAUTHs for the same work item and invoke dry-run and live filing. | Both paths fail closed with an actionable ambiguity diagnostic; no arbitrary row is selected. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Inspect the temporary bridge root and writer calls after ambiguity or requested-authority mismatch. | No bridge file, dispatcher publication, or TAFE state mutation occurs. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run the real proposal-filing test suite and both proposal preflights. | Generated proposal retains exact WI/project/PAUTH/spec metadata and both preflights pass. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --no-header --tb=short` | All existing WI-5420 coverage and new WI-5458 specificity, ambiguity, dry-run-disclosure, and no-write cases pass. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Compare pre/post hashes or scoped diff of the existing WI-5420 hunks. | WI-5420 cross-harness-disposition behavior is unchanged; WI-5458 begins only after WI-5420 terminal verification. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Inspect the WI, TEST-11559, PAUTH, full bridge chain, implementation-start packet, report, verdict, and focused commit as separate durable records. | The selected authorization and any ambiguity are reconstructable, and no later lifecycle state is inferred from proposal filing alone. |

## Risk / Rollback

Primary risk is changing authorization precedence in a shared bridge filing
chokepoint. A too-broad ranking could reject valid unrestricted projects or
silently select among equal candidates. The test matrix therefore covers each
specificity level, both insertion orders, equal-rank ambiguity, and zero-write
failure behavior. Rollback is the focused WI-5458 source/test commit only;
WI-5420 bytes must remain unchanged.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5458-proposal-pauth-precedence`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(bridge)`: this corrects a live authorization-selection defect in the
canonical proposal filing path and adds its regression coverage.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
