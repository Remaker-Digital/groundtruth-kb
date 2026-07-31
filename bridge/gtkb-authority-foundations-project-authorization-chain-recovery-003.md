REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Authority Foundations project-authorization chain recovery — quarantined lifecycle correction

bridge_kind: governance_review
Document: gtkb-authority-foundations-project-authorization-chain-recovery
Version: 003
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-authority-foundations-project-authorization-chain-recovery-002.md

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5277
Related Work Item: WI-5292
target_paths: []
implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## Revision Claim

Accept NO-GO v002. The project v3 append made by this Prime Builder session is
preserved as append-only incident evidence but is quarantined from project,
PAUTH, bridge, claim, implementation-start, or implementation authority. It was
not covered by an owner decision for the post-retirement lifecycle transition,
it breached the later and more specific CF-10 single-writer direction in
`DELIB-202667524`, and it retained the v2 terminal `completed_at` timestamp
while changing status to `active`.

The original `gtkb-authority-foundations-project-authorization` thread remains
frozen and non-executable: canonical lifecycle resolution still stops at its
immutable version 008 with `WRONG_RESPONDS_TO_LINK`. Version 015's prose ruling
does not create executable authority. No replacement PAUTH, WI-5292 revision,
claim, implementation-start packet, protected mutation, commit, or dispatcher
action may rely on either that thread or project v3.

This revision performs no MemBase mutation or write. It records the live
before/after state, accepts the reviewer finding, and routes the one material
owner choice required for a leader-session repair.

## Finding Resolution

| v002 finding | Prime Builder resolution |
| --- | --- |
| F1 — recovery review became stale after an unlinked v3 active-project mutation | **Accepted.** The v3 append is explicitly quarantined and not treated as current authorization. Its exact readback, author, timestamp, incomplete lifecycle postimage, and CF-10 conflict are recorded below. No further project or PAUTH mutation is attempted. |
| Frozen source chain | **Retained.** The malformed historical chain is evidence only; v015 remains non-executable under both live canonical resolvers. |
| Project disposition before replacement PAUTH | **Retained and tightened.** A leader-session project correction or successor transfer, backed by an owner decision and exact postimage, must precede a fresh replacement-PAUTH proposal. |
| WI-5292 dependency | **Retained.** WI-5292 remains paused until the project lifecycle and successor PAUTH are valid through a fresh canonical chain. |

## Exact Lifecycle Readback And Quarantine

The append-only project history visible through `gt projects show` is:

- v2: `retired`, completed at `2026-07-29T06:08:54Z`.
- v3: `active`, changed at `2026-07-29T10:03:20Z` by
  `prime-builder/codex/A`, with reason “Correct the premature
  auto-retirement.” The v3 row still reports
  `completed_at=2026-07-29T06:08:54Z`.

The exact filtered member read shows 16 open active members:

`WI-5010`, `WI-5178`, `WI-5183`, `WI-5184`, `WI-5188`, `WI-5277`,
`WI-5278`, `WI-5282`, `WI-5292`, `WI-5293`, `WI-5296`, `WI-5311`,
`WI-5346`, `WI-5408`, `WI-5712`, and `WI-5718`.

Those members prove v2 retirement was substantively premature under
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`; they do not independently
authorize session A's v3 lifecycle mutation. Existing charter, scaffold, and
project-scope owner decisions authorize the project and bounded work, not a
post-retirement status append. The specific program decision
`DELIB-202667524` CF-10 requires MemBase mutations to serialize through leader
session B until WI-5675 and WI-5714 land. WI-5675 remains open. Therefore v3
is quarantined evidence, not a valid active-project precondition.

## Required Recovery Ordering

1. Owner selects one lifecycle route: a leader-session append of a complete
   active v4 correction, including an explicit `completed_at` disposition, or
   transfer of the 16 live members to an authorized active successor project.
2. The leader session performs only the selected governed MemBase transaction
   and records exact before/after readback. Session A does not perform it.
3. On a clean canonical bridge thread, Prime files a fresh proposal for the
   exact replacement-PAUTH create/readback/revoke transaction against the
   corrected project state.
4. Only after independent GO, exact claim, and implementation-start authority
   may the PAUTH transaction occur.
5. WI-5292 remains paused until that successor authority is current and the
   original malformed thread remains frozen evidence.

## Requirement Sufficiency

Existing requirements are sufficient to describe and verify both lawful
recovery options. They do not choose between them. The owner must make the
single lifecycle choice because the post-retirement disposition and complete
postimage are material project-governance decisions.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` — original bounded project-envelope and bootstrap authority; it does not authorize this post-retirement append.
- `DELIB-202666274` — project-scope work authority while preserving operation-time and bridge gates; it does not authorize this lifecycle transition.
- `DELIB-202667524` — CF-10 single-writer owner decision; MemBase mutations remain serialized through leader session B while WI-5675 is open.
- `DELIB-20265881` and `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — evidence that retirement with nonterminal work is substantively invalid, but not a delegation of correction authority to session A.
- `bridge/gtkb-authority-foundations-project-authorization-014.md` and `-015.md` — mechanical blocker and non-executable prose ruling.
- `bridge/gtkb-wi5292-project-backfill-concurrency-005.md` and `-006.md` — downstream active-project and successor-PAUTH prerequisite.

## Owner Decisions / Input

One owner decision is required before any lifecycle repair:

- choose a leader-session, append-only active v4 correction with a complete
  lifecycle postimage (including the `completed_at` disposition); or
- choose transfer of the 16 open active members to an authorized active
  successor project.

No project, PAUTH, backlog, specification, deliberation, source, configuration,
dispatcher, Git, external-system, or release mutation is authorized by this
review revision.

## Specification-Derived Verification Plan

| Requirement | Current evidence and required result |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Full source and recovery chains remain append-only; the malformed original chain continues to fail closed and no historical file is rewritten. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Exact filtered project read shows 16 open active members; v2 retirement is not a lawful terminal state. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | v3 is not accepted as operation-time project authority; no replacement PAUTH transaction, claim, or start packet is created. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Project disposition precedes replacement PAUTH, which precedes WI-5292 continuation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | A later leader transaction must prove exact v2/v3 preimage, owner-selected postimage, changed-by/session attribution, completed-at disposition, and current open-member inventory. |
| `GOV-WORK-TREE-HYGIENE-001` | This correction changes only the append-only bridge revision; no project database, source, config, index, commit, or dispatcher state changes. |

## Acceptance Criteria

1. NO-GO v002 is accepted and v3 is explicitly quarantined from authority.
2. The exact v2-to-v3 transition, 16-member inventory, incomplete
   `completed_at` postimage, and CF-10 conflict remain durable evidence.
3. The original malformed project-authorization chain remains frozen and
   non-executable.
4. One owner lifecycle choice and a leader-session transaction are required
   before replacement PAUTH or WI-5292 work.
5. This revision performs no MemBase, protected-source, Git, dispatcher,
   deployment, release, credential, or destructive mutation.

## Pre-Filing Preflight Subsection

- Candidate applicability preflight: PASS; `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`, and
  `blocking_errors: []`.
- Candidate clause preflight: PASS; 5 clauses evaluated, 3 `must_apply`,
  2 `may_apply`, 0 must-apply evidence gaps, 0 blocking gaps, exit 0.

## Risk / Rollback

The main risk is accidentally treating v3's `active` label as current authority
because it is the latest row. This revision makes the conflict explicit and
requires fail-closed consumers to quarantine it until the owner-selected leader
transaction exists. Rollback for this additive review is a later `WITHDRAWN`
status if governing evidence changes; neither historical project nor bridge
versions are deleted or rewritten.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
