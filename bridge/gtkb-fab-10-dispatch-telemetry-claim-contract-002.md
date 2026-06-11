GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-10-dispatch-telemetry-claim-contract
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-001.md

# Loyal Opposition Review - FAB-10 Dispatch Telemetry Claim Contract

## Review Scope

Reviewed the operative Prime Builder proposal
`bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-001.md` for WI-4422 /
PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory bridge preflights,
owner-decision evidence, project authorization, backlog state, and dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `07ef97df-2cb3-45a4-9c32-be60d702f29c`.

## Dependency And Precedence Check

FAB-10 is coupled to FAB-01. The FAB-01 dispatch-substrate revival thread is already latest
`GO` with no bridge drift, so the FAB-10 reliability, measurement, breaker, and INDEX-lint work
can proceed as the follow-on substrate hardening. This review does not approve the later
helper-only INDEX write migration; that remains a follow-on slice per the proposal and owner
decision.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-10-dispatch-telemetry-claim-contract`
  passed with `missing_required_specs=[]`; advisory omissions were limited to the
  artifact-oriented governance trio.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-10-dispatch-telemetry-claim-contract`
  passed with 4 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB10-REMEDIATION-20260610` confirms the owner selected the
  bare-id claim contract, colon-safe dispatch filenames plus durable telemetry, half-open
  breaker with `GTKB_DISPATCH_*` knobs, and INDEX well-formedness lint now with helper-only
  writes later.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB10-20260610` for WI-4422, allowing source/config/test changes and forbidding
  any weakening of `bridge/INDEX.md` as canonical workflow state or retired poller restoration.
- `gt backlog list --json --id WI-4422` confirms WI-4422 is open/backlogged and linked to
  the Fable Investigation advisory and chartering deliberations.

## Implementation Constraints

- Do not re-enable the retired OS poller or retired smart poller.
- Do not weaken `bridge/INDEX.md` as canonical workflow state. The HYG-039 work must add
  well-formedness protection, not a competing write path.
- Keep helper-only CAS-protected INDEX writes out of this implementation; the owner decision
  routes that to a follow-on slice.
- The proposal mentions optional repair of the grandfathered non-canonical first line in
  `gtkb-architecture-governance-hygiene-investigation-001.md`, but that bridge artifact is not in
  `target_paths`. Do not edit that bridge file under this GO unless a revised bridge scope adds
  the exact path.

## Verdict

GO for implementation within the proposal's scoped paths and constraints above.
