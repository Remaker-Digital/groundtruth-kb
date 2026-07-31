NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; live governed-writer observation; dispatcher deliberately disabled
author_metadata_source: x-codex-turn-metadata

bridge_kind: governance_review
Document: gtkb-advisory-bridge-propose-claim-kind-regression
Version: 001
Date: 2026-07-30 UTC
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Related Work Item: WI-5784
Work Item Candidate: not yet created
target_paths: []

implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Advisory Report — Generic Proposal Retry Reclassifies A NO-ACTION Claim Back To GO Implementation

## Summary

During governed publication of WI-5359 v011 NO-ACTION, Prime Builder explicitly
converted work-intent row 35014 from `go_implementation` to
`no_action_correction`. A retry through
`propose_bridge_codex_non_bypass(...)` then reacquired the same-session slug
without preserving the existing claim kind. Because the physical frontier was
still GO, the generic acquire route reclassified row 35014 back to
`go_implementation`, recreating implementation deadlines and authority that the
operator had deliberately surrendered.

The writer later failed on the separate control-plane lock before publication.
Prime Builder detected the reclassification through canonical claim status,
restored `claim-no-action`, and used the lower-level governed writer that
validates the existing claim without reacquiring it. V011 then published with a
consumed receipt and the claim released. No target mutation or raw DB repair
occurred.

## Classification

- Category: concurrency/retry lifecycle integrity; same-session claim-kind
  reclassification.
- Severity: high for authority integrity; no protected mutation occurred in
  this observation.
- Affected surface: the Codex non-bypass bridge-proposal helper layered over
  `bridge_work_intent_registry.acquire`.
- Distinct carriers: WI-5784 owns SQLite acquire/release liveness; this report
  owns semantic preservation of an already-held explicit claim kind.

## Exact Timeline And Evidence

1. WI-5359 v010 was the current GO. Prime Builder acquired
   `go_implementation` claim row 35014 at `2026-07-30T15:50:58Z` and minted a
   schema-v3 start packet. No protected edit followed.
2. GO review defects required PB NO-ACTION. Explicit release first failed
   closed with `SQLITE_BUSY`, then `bridge_claim_cli.py claim-no-action`
   canonically reclassified the same row to `no_action_correction` at
   `2026-07-30T15:53:27Z`.
3. A helper attempt failed during claim renewal with `SQLITE_BUSY` after 14
   attempts and 10.001308 seconds, leaving no bridge file.
4. The next helper attempt entered `_acquire_bridge_work_intent`. The helper
   recognized that the holder session matched the current session but still
   called `registry.acquire(...)` without an explicit `claim_kind`.
5. Because v010 GO remained the physical frontier, `_claim_values(...)`
   selected `go_implementation`. `_claim_operation(...)` classified the
   no-action-to-GO difference as `work_intent_reclassify`; the upsert replaced
   `claim_kind`, acquisition time, TTL, implementation deadline, and grace.
6. Canonical status then showed row 35014 as `go_implementation`, acquired at
   `2026-07-30T15:55:51Z`, deadline `16:25:51Z`, despite the operator's earlier
   explicit NO-ACTION transition.
7. The helper subsequently timed out after 30 seconds on
   `.gtkb-state/sot-registry/control-plane.lock`; v011 was not written.
8. Prime Builder restored `no_action_correction` at
   `2026-07-30T15:57:10Z`, then invoked the governed writer without helper
   reacquisition. V011 capability row 447 consumed successfully at
   `2026-07-30T15:58:22Z`, revision
   `SOTREV-A7AE603722EC4C079BCC756772750B6F`; current claim is null.

## Code Evidence

- `.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py:178-194` checks
  for a foreign holder but calls `registry.acquire(...)` even when the same
  session already holds an explicit correction claim. It passes no claim kind.
- `scripts/bridge_work_intent_registry.py:810-884` derives claim kind from the
  latest bridge status when no explicit kind is supplied; GO produces
  `go_implementation`.
- `scripts/bridge_work_intent_registry.py:953-967` treats a same-session kind
  difference as `work_intent_reclassify`, not renewal or denial.
- `scripts/bridge_work_intent_registry.py:1089-1191` upserts all incoming claim
  fields on reclassification, including claim kind and implementation timing.

## Impact

- A retry can silently broaden a deliberately narrowed correction claim back
  into implementation authority based only on the still-current GO file.
- TTL and implementation-deadline semantics change underneath the author.
- A later step that checks only current claim status could mistakenly proceed
  with protected work the operator had already stopped.
- Lock contention makes the flaw more likely because helpers repeat the
  reacquisition boundary and create longer observation windows.
- Audit evidence becomes misleading: the same row and session appear to have
  chosen GO implementation after choosing NO-ACTION, without an explicit
  operator command.

## Recommended Action

1. If a same-session unexpired holder exists, bridge-propose helpers must
   preserve and validate the exact existing claim instead of calling generic
   acquire.
2. A helper publishing status `NO-ACTION` must require
   `no_action_correction`; it must never derive GO implementation from the
   predecessor frontier.
3. Claim-kind reclassification must require an explicit requested kind and a
   typed operation; generic acquire may renew only an identical kind.
4. A same-session kind mismatch returns a deterministic denial with current and
   requested kinds rather than silently upserting.
5. Add a deterministic test: current frontier GO, same-session held
   `no_action_correction`, helper retry; assert kind, TTL, deadlines, row
   provenance, and allowed operations remain unchanged.
6. Add a contention variant that fails once before helper retry and proves the
   claim cannot widen.
7. Publication receipts should record the exact claim kind validated at mint
   and consume; any change between phases fails closed.
8. Preserve the lower-level governed-writer route, but make ordinary helper use
   safe so operators do not need implementation-detail routing knowledge.

## Recommended Disposition

After independent review, create one active Advisory Corrections project child
for explicit claim-kind preservation across helper retries. Link WI-5784 for
the contention trigger but do not merge this semantic-authority defect into the
bounded SQLite retry implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Requirement Sufficiency

**Existing requirements sufficient.** The deterministic claim lifecycle,
NO-ACTION semantics, operation-time authorization, and append-only evidence
requirements already forbid silent authority widening. The correction needs a
bounded implementation and regression suite, not a new normative carrier.

## Specification-Derived Verification Outline

| Requirement | Future behavioral evidence | Required result |
| --- | --- | --- |
| Exact claim-kind preservation | Same-session helper retry over held `no_action_correction` with current GO frontier | Claim kind, TTL, deadlines, and authority remain unchanged. |
| Explicit reclassification | Attempt generic acquire with a different incoming kind | Typed denial naming current and requested kinds; no upsert. |
| Contention recovery | Fail one helper renewal with `SQLITE_BUSY`, then retry | Retry preserves the correction claim and publishes only with the matching kind. |
| Mint/consume binding | Change claim kind between publication phases | Publication fails closed and records the mismatch; no retroactive receipt. |
| Non-bypass behavior | Publish through ordinary helper and lower-level governed writer fixtures | Both validate identical role, claim, transition, and receipt constraints. |

## Prior Deliberations

- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` defines NO-ACTION as an
  intentional Prime correction route, not a temporary synonym for GO work.
- `DELIB-202667531` authorizes advisory stress-observation capture and governed
  processing without granting implementation.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` reinforces that
  project PAUTH is necessary but does not replace exact claim-kind/start gates.

## Non-Approval

This Advisory Report records an observed authority-state regression. It grants
no implementation, claim reclassification, backlog promotion, project
authorization, target mutation, TAFE/dispatcher action, Git operation, release,
or deployment authority.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
