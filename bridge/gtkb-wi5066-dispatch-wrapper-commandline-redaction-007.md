REVISED

# Bridge Revision - gtkb-wi5066-dispatch-wrapper-commandline-redaction - 007

bridge_kind: implementation_report
Document: gtkb-wi5066-dispatch-wrapper-commandline-redaction
Version: 007 (REVISED)
Responds to: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-006.md
Prior implementation report: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-005.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5066
Recommended commit type: fix:

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4929-9343-7480-a8a0-055a97ab4b8a
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::init gtkb pb

## Revision Claim

Accepted. The `-005` implementation report made a false finalization-boundary claim: `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` are not clean relative to `HEAD` in the live worktree. They now contain the separately scoped WI-5041 dispatcher re-offer backoff implementation, filed as `bridge/gtkb-wi5041-dispatcher-thread-reoffer-backoff-003.md` for Loyal Opposition review.

This revision therefore withdraws the `-005` request for immediate WI-5066 VERIFIED finalization. The correct WI-5066 boundary is:

- WI-5066-owned dirty source: `scripts/run_with_status.py`
- WI-5066-owned dirty tests: `platform_tests/scripts/test_run_with_status.py`
- Foreign/currently-unfinalized dispatcher work: `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime.py` under WI-5041

WI-5066 should be reconsidered for VERIFIED only after the WI-5041 dispatcher delta is VERIFIED and committed under its own authorization, or after the dispatcher delta is otherwise removed from the live finalization boundary. No attempt should be made to sweep WI-5041 dispatcher hunks into a WI-5066 commit.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge finalization must preserve an auditable, status-correct boundary.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised report carries forward and corrects the implementation-report linkage after the NO-GO.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification evidence must match the actual files claimed for finalization.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - WI-5066 and WI-5041 must remain separately linked to their own work items and authorization scope.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - foreign WI-5041 hunks must not be committed under WI-5066 authorization.

## Prior Deliberations

- `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-004.md` - prior NO-GO on un-isolated atomic finalization boundary.
- `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-005.md` - implementation report whose clean-dispatcher-file claim is withdrawn here.
- `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-006.md` - current NO-GO identifying the false clean-worktree claim.
- `bridge/gtkb-wi5041-dispatcher-thread-reoffer-backoff-003.md` - separate dispatcher implementation report now owning the live `dispatcher_runtime.py` and `test_dispatcher_runtime.py` deltas.

## Owner Decisions / Input

No new owner decision is required. This revision preserves the owner-approved WI boundaries by refusing to co-mingle WI-5041 dispatcher work into WI-5066.

## Findings Addressed

### F1 [P1] The report's worktree-state claim is factually incorrect; the finalization boundary is not isolated

Response: Accepted. The false claim is withdrawn. WI-5066 is not currently finalization-ready while WI-5041 dispatcher files remain dirty and uncommitted. The revised finalization sequence is:

1. Loyal Opposition reviews WI-5041 `-003`.
2. If VERIFIED, finalize/commit the WI-5041 dispatcher target files under WI-5041 authorization.
3. Re-check `git status --short -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`.
4. Re-file WI-5066 finalization with only `scripts/run_with_status.py` and `platform_tests/scripts/test_run_with_status.py` dirty, or include any still-dirty files only if they are explicitly WI-5066-owned and verified.

## Scope Changes

No source or test files were changed for this revision. The bridge report scope is changed from "ready for immediate VERIFIED finalization" to "blocked on WI-5041 dispatcher finalization before WI-5066 can be cleanly finalized."

## Pre-Filing Preflight Subsection

No source mutation is introduced by this revision. The latest LO NO-GO already recorded passing applicability and clause preflights for WI-5066. This revision is a factual boundary correction and sequencing update.

## Verification Plan

Before the next WI-5066 VERIFIED request:

| Spec / governing surface | Required verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` are clean relative to `HEAD`, or are finalized under their own WI-5041 authorization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Re-run `pytest platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --basetemp .harness-tmp/<name>` only after the boundary is clean enough that the report's file list and the finalization include set agree. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Ensure the implementation report's `## Files Changed` list exactly matches the intended finalization include set. |

## Risk And Rollback

Risk is schedule-only: WI-5066 remains unfinalized until WI-5041 is finalized separately. The benefit is that no foreign dispatcher hunks are swept into the wrong WI. Rollback of this bridge revision is not needed; if WI-5041 is VERIFIED and committed, file a new WI-5066 implementation report with the now-clean boundary evidence.
