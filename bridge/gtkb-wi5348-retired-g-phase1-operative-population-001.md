NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bff-bdfc-7c42-a63c-1663409f04d7
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Exclude retired nonexistent Goose G from operative Phase 1 harness parity

bridge_kind: prime_proposal
Document: gtkb-wi5348-retired-g-phase1-operative-population
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5348-RETIRED-G-PHASE1-PARITY-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5348

target_paths: ["scripts/check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Correct Phase 1 parity population selection so the implicit all-harness audit evaluates operative active lanes and registered onboarding-floor rows, not retired nonexistent Goose G. The change is sequenced after WI-5144 finalization because both exact targets currently contain WI-5144's independently verified candidate bytes.

Work item description: scripts/check_harness_parity.py --all currently derives its all-harness population from every durable registry row, then treats lifecycle class other (including retired G/Goose) as active. The required Phase 1 audit therefore emits 69 false MISSING rows and FAIL even though Goose does not exist and G is retired. Exclude retired and suspended rows from the implicit operative all-harness population while retaining active A/B/C/D/E/F/H and registered onboarding-floor rows. Permit retired rows only through an explicit harness-specific historical query; do not create a Goose harness, delete historical evidence, hide real active Cursor degradation, or weaken typed UNSUPPORTED/waiver distinctions.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5348` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/check_harness_parity.py`, `platform_tests/scripts/test_check_harness_parity.py`.

## Specification Links

- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
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

## Prior Deliberations

- `DELIB-20262495` - Loyal Opposition Verification - FAB-16 Harness Parity Remediation
- `DELIB-20266094` - Owner decision: verify-by-reference resolution of PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION (6 done-but-unlinked WIs)
- `DELIB-202666187` - Loyal Opposition Verdict — WI-5219 Exclude inactive harnesses from Phase 2 release-blocking parity evaluation
- `DELIB-20266563` - Separation Check
- `DELIB-20264388` - Loyal Opposition Verdict - Ollama Phase 1 Foundation REVISED-3

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5348-RETIRED-G-PHASE1-PARITY-20260716` - active project authorization covering `WI-5348`.

## Proposed Scope

- Wait for WI-5144 to become VERIFIED and committed, then require both target paths to be clean at HEAD before WI-5348 implementation starts.
- For implicit harness=all selection, include lifecycle active rows and registered rows with no active role for capability-floor onboarding checks; exclude suspended, retired, and other non-operative lifecycle rows.
- Retain explicit --harness goose as a historical inspection query without reactivating G or allowing it to contribute to the operative fleet result.
- Add focused fixture coverage for active, registered-no-role, suspended, and retired registry rows; preserve active A/B/C/D/E/F/H findings, Cursor degradation, and typed UNSUPPORTED/waiver behavior.
- Do not mutate harness registry, dispatcher/TAFE configuration or runtime, eligibility, leases, historical Goose artifacts, or unrelated WI-5144 semantics.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run the focused Phase 1 parity tests and the repository --all Markdown audit; assert the selected harness set excludes retired G but preserves operative active and registered onboarding-floor populations and genuine findings. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- python scripts/check_harness_parity.py --all --markdown emits no Goose/G rows and no retired-G MISSING contribution while continuing to report every genuine active-harness finding.
- The focused parity test module passes, including a regression where implicit all excludes retired and suspended rows, retains active and registered-no-role rows, and explicit goose remains queryable historically.
- WI-5144 candidate semantics remain byte-preserved before the small WI-5348 lifecycle-selection and regression-test hunks are applied.
- No dispatcher, TAFE, harness eligibility, registry lifecycle, lease, credential, push, deployment, or release state changes.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/check_harness_parity.py`
- `platform_tests/scripts/test_check_harness_parity.py`

## Recommended Commit Type

`feat`
