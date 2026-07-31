NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; concurrent subagent execution; dispatcher deliberately disabled
author_metadata_source: x-codex-turn-metadata

bridge_kind: governance_review
Document: gtkb-advisory-work-intent-acquire-db-lock-recurrence
Version: 001
Date: 2026-07-30 UTC
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Related Work Item: WI-5784
target_paths: []

implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Advisory Report - Work-intent acquisition exposed a transient SQLite lock

## Executive Summary

Prime Builder encountered a live concurrency failure while beginning the
approved WI-5368 implementation in a session running parallel governed backlog
work. The canonical claim command failed before mutation with:

```text
ERROR: Database error during acquire: database is locked
```

An immediate status check returned `null`, proving no partial claim was left.
A second canonical acquisition then succeeded at `2026-07-30T13:24:56Z` and
created claim row 34984 for the exact WI-5368 thread and parent session. The
subsequent schema-v3 implementation-start packet also succeeded without bypass.

The failure is a recurrence of the database-contention class already routed to
WI-5784. This report supplies exact acquisition-side evidence and recommends
updating that existing carrier, not creating a duplicate. It does not authorize
implementation and does not activate or mutate dispatcher/TAFE.

## Classification

- Category: concurrent MemBase access, work-intent acquisition liveness.
- Severity: medium for liveness; low for integrity because failure was closed
  and left no claim.
- Affected surface: `scripts/bridge_claim_cli.py claim` and the canonical
  work-intent registry acquisition path.
- Disposition: append evidence to existing WI-5784 after independent review.

## Claim

Work-intent acquisition still exposes transient SQLite writer contention as an
operator-visible hard failure. The current safe outcome prevents false claims,
but forces agents to recognize and manually retry a concurrency condition. A
bounded deterministic acquisition service should absorb ordinary transient
contention, preserve holder safety, and return typed exhaustion diagnostics.

## Evidence

### E1 - First acquisition failed before claim creation

The exact command was:

```text
python scripts/bridge_claim_cli.py claim gtkb-wi5368-codex-git-window-command-family --session-id 019fb19b-7814-73c1-8707-204e432cbf00 --ttl-seconds 1800
```

It returned the exact `database is locked` error above. No source, test, bridge,
packet, Git, dispatcher, or TAFE mutation preceded it.

### E2 - The registry remained clean

The next canonical status query returned `null`. This proves the failed
transaction did not leave a partial holder that could falsely reserve the two
WI-5368 targets or block a later session.

### E3 - A bounded retry succeeded

The next identical canonical acquisition succeeded and returned:

- claim row: 34984;
- acquired at: `2026-07-30T13:24:56Z`;
- session: `019fb19b-7814-73c1-8707-204e432cbf00`;
- project: `PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY`;
- claim kind: `go_implementation`; and
- implementation deadline: `2026-07-30T13:54:56Z`.

The later implementation-start packet passed operation-time PAUTH evaluation
for the exact source/test cohort. This isolates the failure to transient claim
acquisition contention rather than invalid authority or target state.

### E4 - Concurrent writer identity is not observable

Other governed MemBase work was running concurrently through delegated agents.
It is an inference, not an exact attribution, that one of those transactions
held the conflicting SQLite lock: the surfaced error carries no lock-holder,
operation, elapsed wait, configured timeout, or retry evidence. The repair must
not guess the holder or weaken transaction boundaries.

## Risk And Impact

- Parallel Prime Builder work can fail at the claim boundary even when the
  bridge GO, project PAUTH, targets, and session provenance are valid.
- Manual retries are inconsistent across agents and can produce duplicate
  attempts or unnecessary abandonment of executable work.
- A long or unbounded retry would hide real deadlock, delay owner-visible work,
  and amplify pressure on the already-large append-only database.
- Weakening the lock or claim transaction would create a worse integrity flaw.

## Recommended Existing-Carrier Update

If Loyal Opposition confirms this occurrence, update WI-5784 with this exact
acquisition evidence. Its future implementation and tests should:

1. apply a short bounded busy timeout and deterministic backoff to both claim
   acquisition and release transactions;
2. revalidate current holder, session, project, and target reservation state on
   every retry;
3. leave no partial row or stolen/released peer claim on every failed attempt;
4. return typed exhaustion diagnostics with operation, attempts, elapsed time,
   database path/identity, and safe recovery, without claiming an unknown lock
   holder;
5. test concurrent acquire/acquire, acquire/release, and unrelated MemBase write
   schedules deterministically; and
6. keep retries outside dispatcher/TAFE and avoid a long-held global lock.

## Append-Only SoT And Scale Context

The authoritative database is approximately 844 MB in the current session and
continues to grow. This single occurrence does not prove file size caused the
lock, so the report makes no such claim. WI-5784 should nevertheless record
wait duration, attempt count, and transaction timing so future analysis can
separate ordinary writer overlap from size-related access latency without
discarding append-only history.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Requirement Sufficiency

**Existing requirements sufficient.** This is fresh operational evidence for
the already-established fail-closed, deterministic, project-authorized claim
contract. No new GOV, ADR, or DCL is needed before WI-5784 can incorporate it.

## Prior Deliberations And Related Evidence

- `bridge/gtkb-advisory-work-intent-release-db-lock-concurrency-001.md` and
  confirmed `-002.md` established the release-side contention class.
- WI-5784 v2 already owns bounded retry and holder-safe revalidation across
  acquisition and release; this report adds a concrete live acquisition
  recurrence.
- `bridge/gtkb-advisory-wi5757-implementation-start-orchestration-concurrency-001.md`
  and confirmed `-002.md` cover a broader orchestration boundary without
  replacing this transaction-level evidence.

## Specification-Derived Verification Outline

| Requirement | Future behavioral evidence | Required result |
| --- | --- | --- |
| Fail-closed acquisition | Inject lock on every attempt and query holder afterward | Typed exhaustion; no partial or peer claim mutation. |
| Bounded recovery | Release lock during a deterministic retry schedule | Acquisition succeeds within the budget and records attempts/elapsed time. |
| Holder safety | Race two sessions over one thread and overlapping targets | Exactly one valid holder; loser receives complete conflict evidence. |
| Acquire/release concurrency | Interleave acquisition with peer release and unrelated MemBase writes | No stolen claim, orphan claim, or false success. |
| Nonimpairment | Run with dispatcher/TAFE disabled | No activation, wake, configuration, routing, or runtime mutation. |

## Owner Decisions / Input

No owner decision is required to preserve or review this Advisory. If confirmed,
Prime Builder should update existing WI-5784 under the active Advisory
Corrections project and use the normal project-only proposal, GO, claim, start,
implementation, report, and independent verification gates.

## Explicit Non-Approval

This report is not implementation approval, PAUTH, an implementation proposal,
a claim, an implementation-start packet, commit authority, release authority,
or deployment authority. `target_paths` is empty and no implementation mutation
is performed by filing it.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
