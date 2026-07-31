NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5474-c61c-71a2-be00-85d5c04faa5a
author_model: GPT-5 Codex
author_model_version: 2026-07-13 runtime
author_model_configuration: Codex desktop interactive Prime Builder session

bridge_kind: governance_advisory
target_paths: ["groundtruth.db"]
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION
Work Item: WI-5138

# WI-5138 Bounded PAUTH Activation

## Summary

Activate one exact project authorization required to re-enter the six-file
modernization trust-enforcement slice through the strict bridge lifecycle.
This proposal authorizes only the append-only PAUTH row described below. It
does not authorize source or test mutation by itself, and it does not treat any
existing draft bytes as accepted implementation evidence.

## Requirement Sufficiency

Existing requirements sufficient

The frozen modernization scope, the current governing specifications, the
version 004 corrected NO-GO, and the two owner decisions cited below are
sufficient for this bounded authorization activation. No requirement or scope
change is proposed.

## Exact Proposed Mutation

After an independent Loyal Opposition GO, Prime Builder may append exactly one
active project-authorization row to `groundtruth.db` with these values:

- Authorization ID: `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5138-TRUST-ENFORCEMENT-20260713`
- Project: `PROJECT-GTKB-PLATFORM-MODERNIZATION`
- Included work item: `WI-5138`
- Owner decision: `DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY`
- Scope: bounded release-candidate evidence and strict bridge trust closure for
  `WI-5138`; later source, test, or configuration effects remain limited to the
  exact target paths of a separate independently GO-approved proposal.
- Allowed mutation classes: `bridge`, `metadata`, `source`, `test`,
  `configuration`, `runtime_state`, and `governance_evidence`.
- Forbidden operations: credential lifecycle, secret disclosure, destructive
  cleanup, Git commit, Git push, remote ref update, branch or worktree mutation,
  release, deployment, published production-state change, dispatcher mutation,
  bulk backlog mutation, formal specification mutation, unrelated mutation,
  and scope expansion without a new owner decision.
- Included specifications: every specification listed in this proposal's
  `Specification Links` section that is an approved formal specification.
- Status: active until explicitly completed, revoked, or superseded through a
  separately governed operation.

No membership, work-item, project, specification, bridge-history, source,
test, configuration, Git, dispatcher, credential, release, or deployment row or
file may change as part of this operation.

## Owner Decisions / Input

- `DELIB-20260713-MODERNIZATION-STRICT-BRIDGE-PROTOCOL` requires a GO before
  every DoT or change-controlled mutation and independent LO verification for
  every completed modernization slice.
- `DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY` authorizes
  bounded modernization source, test, and configuration work only after the
  strict bridge gates pass, while excluding Git, credentials, cleanup, release,
  and deployment.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires a current bounded
  project authorization before implementation.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires the
  current PAUTH envelope to be evaluated before claims, packets, starts, and
  protected effects.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - makes the numbered bridge chain and
  role-correct independent review mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires every
  applicable specification and test derivation to be explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed
  specification-derived evidence before this activation can be VERIFIED.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - forbids weakening existing
  controls while enabling modernization.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires the PAUTH row
  and its authority bounds to remain mechanically evaluable.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - keeps PAUTH activation before the
  dependent source proposal's claim and start.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves the owner decisions,
  proposal, PAUTH, report, and verdict as one traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires explicit lifecycle state
  rather than ambient or retroactive authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires durable, explicit
  governance evidence for this activation.

## Specification-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Exact project, work item, owner decision, status, and scope | Run `gt projects show-authorization PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5138-TRUST-ENFORCEMENT-20260713 --json` and compare every field to this proposal. |
| Exact mutation and prohibition classes | Parse the returned JSON arrays and assert exact ordered-set equality with this proposal; explicitly assert every Git, credential, cleanup, release, deployment, dispatcher, formal-specification, unrelated, and scope-expansion prohibition. |
| No collateral DoT mutation | Capture canonical before/after queries for the target project, work item, deliberations, and project authorizations; require exactly one new PAUTH row and no changed pre-existing row. |
| Operation-time consumability | After the dependent REVISED proposal receives its own GO and claim, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-modernization-trust-enforcement-slice --no-write` and require `authorized: true` before writing its packet. |
| Independent completion | File a post-implementation report with the exact commands and observed JSON, then obtain independent LO `VERIFIED`; a GO alone is not completion. |

## Acceptance Criteria

1. The exact PAUTH ID exists once, is active, and binds only the parent project
   and `WI-5138`.
2. Its owner decision, included specifications, allowed mutation classes,
   forbidden operations, and scope text match this proposal exactly.
3. No other DoT row or project file changes during activation.
4. The PAUTH cannot authorize source or test effects without a later exact
   proposal GO, matching claim, and successful implementation-start packet.
5. Git commit/push, credentials, cleanup, release, deployment, dispatcher
   mutation, unrelated work, and scope expansion remain denied.
6. This activation is not complete until a post-implementation report receives
   independent LO `VERIFIED`.

## Risk And Rollback

The principal risk is treating a project-level PAUTH as blanket source
authority. The operation-time evaluator and every later proposal's exact
`target_paths` remain the narrower controlling bounds. If any inserted field is
wrong, stop all dependent work and use a separately GO-approved successor to
revoke or supersede the authorization; do not delete or rewrite history.

## Prior Deliberations

- `bridge/gtkb-modernization-trust-enforcement-slice-004.md` requires an active
  bounded PAUTH before the six-file proposal may be revised.
- `DELIB-20260713-MODERNIZATION-STRICT-BRIDGE-PROTOCOL` restores the complete
  GO, claim, start, report, and VERIFIED chain.
- `DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY` defines the
  allowed modernization work and retained exclusions.

## Pre-Filing Preflight

- Applicability preflight must pass with no missing required or advisory
  specifications against these exact bytes.
- Mandatory ADR/DCL clause preflight must exit zero with no blocking gap.
