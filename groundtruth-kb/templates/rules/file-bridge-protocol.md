# File Bridge Protocol

The bridge between Prime Builder and Loyal Opposition uses a shared directory
of versioned markdown files plus dispatcher/TAFE bridge state.

> **GT-KB host note (2026-06-15):** In the GT-KB host after the TAFE/dispatcher
> cutover, retired bridge-index artifacts are not canonical bridge-state or
> dispatcher authority.

## Directory

`bridge/` at project root. All proposal, review, and verification documents
live here as numbered markdown files.

## Mandatory Specification Linkage Gate

Every implementation proposal must include a `Specification Links` section
before it can receive `GO`. The section must cite every relevant governing
specification, rule, ADR, DCL, proposal standard, or other durable specification
artifact that constrains the proposed implementation. A proposal with no linked
specification surface is invalid and must receive `NO-GO`.

Codex/Loyal Opposition MUST reject all implementation proposals that are not
linked to specifications. Without linked specifications, there MUST NOT be an
approved implementation plan.

The proposal must also state how the proposed tests derive from those linked
specifications. Codex/Loyal Opposition review must independently check the list
for omissions. If any relevant specification is missing, or if the proposed tests
do not map back to the linked specifications, the only valid verdict is `NO-GO`.

## Mandatory Specification-Derived Verification Gate

An implementation cannot receive `VERIFIED` unless the verification procedure
creates or identifies tests derived from the specifications linked in the
implementation proposal and executes those tests against the implementation.

The post-implementation report must include:

- the linked specifications carried forward from the proposal;
- a spec-to-test mapping showing which tests cover which specification clauses
  or acceptance criteria;
- the exact commands used to execute those tests;
- the observed results.

If a linked specification has no executed test coverage, Codex/Loyal Opposition
must issue `NO-GO` unless the owner explicitly approves a documented waiver for
that specific specification and risk.

## File Naming

`{descriptive-name}-{NNN}.md`

- `descriptive-name`: kebab-case description of the proposal or review topic
- `NNN`: zero-padded version number starting at 001, incremented for each
  revision or review response

Examples:
- `widget-refactor-001.md` (Prime's initial proposal)
- `widget-refactor-002.md` (Codex's review with GO or NO-GO)
- `widget-refactor-003.md` (Prime's revision after NO-GO)

## Statuses

| Status | Set by | Meaning |
|--------|--------|---------|
| NEW | Prime | Fresh proposal awaiting review |
| REVISED | Prime | Updated proposal after a NO-GO |
| GO | Codex | Proposal approved for implementation |
| NO-GO | Codex | Proposal requires changes before approval |
| VERIFIED | Codex | Post-implementation verification passed |
| ADVISORY | Loyal Opposition | Owner-initiated advisory report; non-dispatchable. |
| DEFERRED | Owner | Owner-directed parked bridge state; non-actionable until the clear/resume condition is met. |
| WITHDRAWN | Owner / governed correction | Terminal withdrawal or retirement state. |

## DEFERRED Status

`DEFERRED` is owner-only bridge parking state. It is indexed workflow state,
not a parked draft and not a Loyal Opposition verdict. A `DEFERRED` bridge file
must start with `DEFERRED`, include concrete Owner Decisions / Input evidence,
state a deferral reason, and state a clear/resume condition.

## Prime Workflow

1. Write the proposal as `bridge/{name}-001.md` through the governed bridge
   writer path.
2. Let the governed writer publish dispatcher/TAFE bridge state for the new
   versioned bridge file.
3. Continue working on other tasks
4. Periodically scan canonical bridge state for GO or NO-GO responses; skip ADVISORY, DEFERRED, WITHDRAWN, and VERIFIED as non-actionable
5. On GO: proceed with implementation
6. On NO-GO: read the NO-GO file, address findings, save revised file with
   incremented version, and use the governed writer to publish a REVISED entry

## Codex Workflow

1. Periodically scan canonical bridge state for NEW or REVISED entries; skip ADVISORY, DEFERRED, WITHDRAWN, and VERIFIED as non-actionable
2. Process entries starting from the oldest actionable item
3. Read the indicated file and perform the review
4. Save review findings as a new version with incremented number
5. Use the governed writer to publish the verdict line for that thread (GO or NO-GO)

## Post-Implementation Verification

After Prime implements a GO'd proposal:
1. Prime saves a post-implementation report as a new version with incremented number
2. Prime uses the governed writer to publish a NEW verification-request entry
3. Codex reviews and responds with VERIFIED or NO-GO

## Bridge State Maintenance

Dispatcher/TAFE bridge state is maintained through governed bridge writer and
reconcile paths. Archived entries and their corresponding bridge files remain
on disk for historical reference.

## Guardrails

- Both agents must read the full entry (all versions) before acting on any
  single version
- Never delete bridge files — they form the audit trail
- In current GT-KB hosts, TAFE-backed bridge state is the source of truth for
  workflow state.
