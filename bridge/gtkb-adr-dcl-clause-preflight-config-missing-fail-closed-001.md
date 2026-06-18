NEW
author_identity: prime-builder/Codex
author_harness_id: A
author_session_context_id: keep-working-20260618T0830Z
author_model: GPT-5
author_model_version: 2026-06-18
author_model_configuration: Codex desktop automation; PowerShell; approval_policy_never

# ADR/DCL Clause Preflight Missing-Config Fail-Closed Fix

bridge_kind: prime_proposal
Document: gtkb-adr-dcl-clause-preflight-config-missing-fail-closed
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4637

target_paths: ["scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py", "bridge/gtkb-adr-dcl-clause-preflight-config-missing-fail-closed-*.md"]
Recommended commit type: fix:

implementation_scope: adr_dcl_clause_preflight_fail_closed_config_missing
requires_review: true
requires_verification: true

## Claim

`WI-4637` identifies a fail-open path in the mandatory ADR/DCL clause
preflight: when `scripts/adr_dcl_clause_preflight.py` receives a missing
`--clauses-config`, it prints an error but exits `0`.

That behavior conflicts with the script's own documented mandatory-gate
contract and with the existing `EXIT_CANNOT_EVALUATE = EXIT_BLOCKING_GAP`
constant. A missing mandatory clause registry should be an inability to
evaluate the gate, not a passing state.

## Proposed Implementation After GO

1. Create a fresh implementation-start packet for this bridge thread.
2. Update `scripts/adr_dcl_clause_preflight.py` so the missing
   `--clauses-config` path exits with `EXIT_CANNOT_EVALUATE` instead of `0`.
3. Add a targeted regression test in
   `platform_tests/scripts/test_adr_dcl_clause_preflight.py` that calls
   `main()` with a missing config path and asserts exit `5`.
4. Run the focused test module and the script's self-preflights, then file a
   post-implementation report with the command output.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected source/test
  mutation must wait for Loyal Opposition `GO` and a valid implementation-start
  packet.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active May29 Hygiene
  project authorization permits autonomous implementation proposals for
  unimplemented May29 work items.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal, the eventual report, and
  verification use the versioned bridge file chain as the workflow authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes
  project authorization, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites the governing specification surfaces and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report
  must map the linked requirements to executed tests and observed results.
- `GOV-STANDING-BACKLOG-001` - `WI-4637` is the governed backlog authority for
  the observed fail-open defect.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files are in-root
  under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, proposal, test, and
  eventual report remain linked as durable lifecycle artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the test preserves the gate
  behavior as executable artifact evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the work item remains open until the
  post-implementation report is VERIFIED.

## Requirement Sufficiency

Existing requirements are sufficient. The already-implemented Slice 2 mandatory
gate defines exit `5` for blocking gaps and cannot-evaluate states. The missing
configuration file is an evaluator failure, so no new GOV/SPEC/PB/ADR/DCL
artifact is needed before this source/test fix.

## Owner Decisions / Input

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` authorizes autonomous
  proposal work for all unimplemented work items linked to
  `PROJECT-GTKB-MAY29-HYGIENE` through
  `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`.
- No new owner decision is required. This proposal does not request a waiver,
  production deployment, credential action, destructive cleanup, or formal
  artifact mutation.

## Prior Deliberations

- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md`
  - VERIFIED terminal evidence for the mandatory ADR/DCL clause gate and its
  exit-code semantics.
- `bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-008.md` - VERIFIED
  follow-on confirming the existing exit-5 clause gate remained unchanged.
- `bridge/gtkb-adr-dcl-clause-preflight-content-file-path-fix-004.md` -
  VERIFIED precedent for a focused source/test correction to
  `scripts/adr_dcl_clause_preflight.py`.
- `DELIB-20263312` - recent NO-GO record where the ADR/DCL clause preflight
  blocked a report, reinforcing that this preflight is treated as a
  fail-closed mandatory gate.
- Focused deliberation search for `"adr dcl clause preflight missing config
  fail closed WI-4637"` returned no prior decision rejecting this fix approach.

## Specification-Derived Verification Plan

This is the spec-to-test mapping for the proposed change. The
post-implementation report will include executed commands and observed results.

| Requirement / specification | Verification evidence |
|---|---|
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation-start packet created before source/test edits. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `show_thread_bridge.py gtkb-adr-dcl-clause-preflight-config-missing-fail-closed` shows no drift after report filing. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight passes for this proposal and report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` includes the new missing-config fail-closed regression. |
| `GOV-STANDING-BACKLOG-001` | Implementation report cites `WI-4637` and leaves closure to LO VERIFIED. |

## Acceptance Criteria

- Missing `--clauses-config` returns exit `5`, not exit `0`.
- The stderr diagnostic remains explicit that the clauses config was not found.
- A targeted regression test covers the missing-config path.
- Existing ADR/DCL clause preflight tests still pass.
- No production deployment, credential action, formal artifact mutation, or
  unrelated bridge/thread cleanup is included.

## Risk And Rollback

Risk is low. The behavior becomes stricter only when the mandatory clause
configuration is absent. Rollback would revert the source/test change, but doing
so would restore a fail-open gate path and should require a separate bridge
review.

