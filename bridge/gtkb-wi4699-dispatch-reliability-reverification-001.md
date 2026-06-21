NEW

# WI-4699 Dispatch Reliability Re-Verification Proposal

bridge_kind: prime_proposal
Document: gtkb-wi4699-dispatch-reliability-reverification
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-20 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-pb-2026-06-20-cost-autodispatch-wi4699
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder session role from `::init gtkb pb`

Project Authorization: PAUTH-WI-4699-REVERIFY-DISPATCH-RELIABILITY
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4699

target_paths: ["groundtruth.db", "bridge/gtkb-wi4699-dispatch-reliability-reverification-*.md"]

implementation_scope: dispatch_reliability_reverification_and_backlog_reconciliation
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
protected_source_mutation_in_scope: false

---

## Summary

Owner deliberation `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION`
found that several dispatch-reliability work items were terminal in MemBase or
bridge evidence while the live dispatcher state still showed contradictory
failure symptoms. `WI-4699` exists because resolved-stage FSM semantics should
not rewrite those prior terminal work items in place; the appropriate path is a
fresh regression item that re-verifies whether each prior fix still holds.

This proposal requests authorization to perform that bounded re-verification
and evidence reconciliation. It does not propose source or configuration
changes. If a prior fix does not hold, Prime Builder will record the evidence
under `WI-4699` and file a fresh scoped corrective bridge item rather than
mutating unrelated source under this thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - The regression review and any resulting
  MemBase reconciliation must proceed through the numbered bridge chain and
  cannot bypass Loyal Opposition.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal
  links the governing project authorization, work item, and verification plan
  before any mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The header carries
  the active PAUTH, project, and `WI-4699` linkage for the cost-optimized
  autodispatch project.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The post-implementation
  report must map each re-verified prior fix to concrete live-state evidence
  or focused tests.
- `GOV-STANDING-BACKLOG-001` - The backlog must not claim terminal reliability
  when live evidence contradicts it; any status/evidence update must cite the
  current bridge report.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - The new PAUTH is bounded
  approval evidence only; it does not replace LO GO, implementation-start
  packets, or VERIFIED.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The regression finding must be
  preserved as durable evidence instead of being left as session memory.

## Prior Deliberations

- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - Owner decision that
  prior VERIFIED-but-contradicted dispatch reliability work must be re-verified
  against live state and reopened through fresh work when fixes do not hold.
- `bridge/gtkb-lo-review-dispatch-reliability-008.md` - Prior VERIFIED
  reliability verdict that must now be tested against current live state rather
  than accepted as self-proving.
- `bridge/gtkb-wi4616-covered-by-dispatch-reliability-reconciliation-004.md` -
  Later LO NO-GO showing the danger of using the prior reliability verdict as
  blanket closure evidence when focused tests fail in the current checkout.
- `bridge/gtkb-wi4616-covered-by-dispatch-reliability-reconciliation-008.md` -
  Example of the acceptable correction pattern: repair the focused evidence
  path, then refresh MemBase only after current verification passes.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-008.md` and
  `bridge/gtkb-wi4480-dispatch-starvation-telemetry-004.md` - Related
  reliability/fairness threads whose live behavior should be distinguished
  from the specific prior-fix regression audit in this work item.

## Owner Decisions / Input

No new owner decision is required. The owner decision in
`DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` explicitly directs this
re-verification, and `PAUTH-WI-4699-REVERIFY-DISPATCH-RELIABILITY` now bounds
the allowed mutation class to evidence, test execution, bridge proposal filing,
project artifact links, and `WI-4699` MemBase reconciliation.

## Requirement Sufficiency

Existing requirements are sufficient. The work item defines the required prior
fix set (`WI-4472`, `WI-4473`, `WI-4476`, `WI-4477`, and `WI-4557`), the
acceptance condition requires current re-verification by a reliable reviewer,
and the governing bridge/backlog specs define how to record holding versus
non-holding evidence.

## Implementation Plan

1. Acquire an implementation-start packet after LO GO for this bridge id and
   only the declared target paths.
2. Read the current backlog rows and bridge chains for `WI-4472`, `WI-4473`,
   `WI-4476`, `WI-4477`, and `WI-4557`.
3. Capture current dispatcher status and health using the supported
   `gt bridge dispatch status --json` and `gt bridge dispatch health --json`
   surfaces.
4. Re-run focused existing verification commands where the prior fix has a
   current test lane; otherwise record the live-state read that proves the
   condition is holding or non-holding.
5. Update `WI-4699` evidence in MemBase with the re-verification matrix and
   related bridge links.
6. File fresh scoped corrective bridge work for every non-holding prior fix.
7. File a post-implementation report under this thread with the command output,
   re-verification matrix, residual risks, and any follow-on bridge slugs.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: run
  `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4699-dispatch-reliability-reverification`
  and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4699-dispatch-reliability-reverification`.
  Expected: no missing required specs and no blocking clause gaps.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: produce a matrix for
  `WI-4472`, `WI-4473`, `WI-4476`, `WI-4477`, and `WI-4557` with one row per
  prior fix, current evidence command, result, and holding/non-holding
  classification. Where the prior VERIFIED report names a focused regression
  lane, rerun it with `python -m pytest <focused prior-test-node> -q --tb=short`
  and record the exact node and observed result in the matrix.
- `GOV-STANDING-BACKLOG-001`: run `gt backlog show WI-4699 --json` after the
  evidence update. Expected: `WI-4699` remains non-terminal until LO verifies
  the implementation report, and its status detail cites this bridge thread and
  the re-verification matrix.
- Dispatch health visibility: run `gt bridge dispatch status --json` and
  `gt bridge dispatch health --json`. Expected: report current health honestly;
  red health does not fail this proposal by itself, but must be disclosed and
  mapped to follow-on corrective work when relevant.
- Regression audit commands: run the focused existing tests named by the prior
  VERIFIED reports when they are still present in the checkout. Expected:
  holding fixes pass; non-holding fixes are not papered over and receive fresh
  corrective bridge work.

## Risk / Rollback

Primary risk is turning a re-verification item into a broad implementation
bucket. Mitigation: this thread does not authorize source or configuration
mutation. Non-holding fixes must become fresh scoped bridge proposals with
their own target paths.

Rollback is a normal MemBase evidence correction: if the re-verification matrix
is wrong, file a follow-on bridge revision or corrective report rather than
editing prior bridge files. No deployment, credential change, retired poller
restoration, or unrelated source mutation is in scope.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4699-dispatch-reliability-reverification`; no prior
version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore:` - the expected mutation is project evidence and backlog
reconciliation, not a source behavior change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
