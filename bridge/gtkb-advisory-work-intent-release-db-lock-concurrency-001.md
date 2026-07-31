NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

# Advisory Report - Work-intent release can retain a valid claim after bounded SQLite lock failure

bridge_kind: governance_review
Document: gtkb-advisory-work-intent-release-db-lock-concurrency
Version: 001
Date: 2026-07-30 UTC

target_paths: []
implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Summary

The explicit work-intent release operation failed twice with
`Database error during release: database is locked` immediately after the
WI-5759 implementation report was filed. Each failed invocation waited for the
registry's approximately 10-second SQLite contention bound and exited 3. The
authoritative row remained intact, so the failure was fail-closed and no other
session could silently inherit the claim. A third bounded retry at
`2026-07-30T08:27:41.5938246Z` succeeded in 1.503 seconds; its follow-up status
read returned `null` at `2026-07-30T08:27:43.0963382Z`.

This transient recovery does not close the defect. A normal post-publication
cleanup operation has no retry/backoff contract and reports neither the lock
phase nor holder provenance. During contention, a valid claim can remain live
until a manual retry or TTL expiry, lengthening cross-session serialization and
making a safely filed report appear operationally unfinished.

## Advisory Classification

- Category: SQLite concurrency, cleanup liveness, and diagnostic provenance.
- Affected operation: `bridge_claim_cli.py release` and direct callers of
  `bridge_work_intent_registry.release()`.
- Observed carrier: MemBase `work_intent_claims` in `groundtruth.db`.
- Immediate incident: post-report release for
  `gtkb-wi5759-ruff-gate-staged-blob`.
- Outcome: two bounded failures, no partial deletion, later retry success.
- Authority: review-only advisory. This artifact is not implementation
  approval and does not create or approve a corrective work item.

## Claim

Work-intent release has a concurrency correctness gap at its operational
boundary: it preserves the row on a lock failure, which is correct, but offers
only one fixed wait and a generic error. It should retain fail-closed deletion
semantics while adding bounded retry, phase-aware diagnostics, and direct
concurrency tests. A foreign process must never be killed merely to make the
release succeed.

## Source And Incident Context

The incident occurred after
`bridge/gtkb-wi5759-ruff-gate-staged-blob-003.md` was successfully filed for
independent review. The implementation claim was still held by this session and
needed to be released so the implementation-review handoff was complete.

The command shape on all three attempts was:

```text
python scripts/bridge_claim_cli.py release gtkb-wi5759-ruff-gate-staged-blob --session-id 019fb19b-7814-73c1-8707-204e432cbf00 --project-root E:\GT-KB
```

The first two attempts each emitted:

```text
ERROR: Database error during release: database is locked
```

and exited 3 after the configured contention wait. Exact wall-clock timestamps
were not emitted by the CLI for those two failures; this advisory does not
invent them. The instrumented third attempt recorded the timestamps and elapsed
time above, exited 0, and a separate authoritative status read returned `null`.

## Evidence

### E1 - Release is a single immediate-write attempt

`scripts/bridge_work_intent_registry.py:1053-1067` opens a connection, enters
the connection context, executes `BEGIN IMMEDIATE`, deletes only the row whose
thread slug and session ID both match, and closes the connection. Any SQLite
error is collapsed to `Database error during release: <message>`; no phase,
retry count, observed wait, database path, or concurrent-writer evidence is
included.

### E2 - Fixed 10-second wait and no retry/backoff

`scripts/bridge_work_intent_registry.py:180-188` calls
`sqlite3.connect(..., timeout=10)`. The release path contains no bounded retry,
jitter, or re-read-after-contention logic. The observed two failures match that
single-wait behavior.

### E3 - Every release connection performs global schema work first

`scripts/bridge_work_intent_registry.py:127-177` imports and executes the full
MemBase `SCHEMA_SQL`, then creates or migrates the work-intent table and three
indexes and commits. A read-only source count during diagnosis found the loaded
schema text to be approximately 47,232 characters / 195 statements, including
49 `CREATE TABLE` and 108 `CREATE INDEX` statements, before the explicit
release transaction begins. This increases the number of write-sensitive
phases in what should be a narrow one-row cleanup operation.

If `_ensure_schema()` fails, `_get_conn()` reports `Could not open database`;
the observed `Database error during release` instead localizes both failures to
the release transaction or its commit after connection/schema setup completed.
The current error still cannot distinguish `BEGIN IMMEDIATE`, `DELETE`, or
commit.

### E4 - Failure preserved state and later retry removed it

After each failure, `bridge_claim_cli.py status` still returned the current
WI-5759 claim. After the third attempt, the status returned `null` and a
read-only SQL count for that exact slug returned zero. There was no partial
delete, false success, foreign claim takeover, or manual database edit.

### E5 - Concurrent process census did not justify destructive intervention

The read-only process census showed multiple long-running GT-KB Python
processes, including bridge scans and a Loyal Opposition verdict worker. The
available environment did not provide reliable SQLite lock-holder attribution,
and process presence alone does not prove lock ownership. No foreign process
was killed, suspended, or mutated. The later successful retry confirms that
waiting was sufficient in this incident.

### E6 - Existing coverage does not exercise this failure

Current tests cover logical claim exclusivity and indirect uncontended cleanup,
but the diagnosis found no direct release test that holds a competing SQLite
write lock, exhausts the timeout, verifies unchanged state, releases the lock,
and then proves retry success. There is likewise no phase/provenance assertion
for a release-lock failure.

## Risk And Impact

1. A safely published implementation report can retain its implementation
   claim, delaying another session even though source work is complete.
2. TTL expiry becomes an accidental cleanup substitute rather than a bounded
   exceptional fallback.
3. Repeated manual retries create avoidable database pressure and do not tell
   the operator whether contention is progressing.
4. Generic lock errors encourage unsafe guesses about which foreign process to
   terminate. GT-KB needs evidence, not process-name inference.
5. Running the entire global schema initialization on every narrow claim
   release expands the contention surface and cost of a hot coordination path.
6. A future retry implementation could accidentally delete a reacquired or
   foreign claim unless every attempt retains the exact slug-plus-session
   predicate and revalidates state.
7. `scripts/dispatcher_runtime.py` currently swallows registry cleanup errors in
   its release helper. That can hide a retained claim until expiry instead of
   producing durable operational evidence.
8. `scripts/gtkb_bridge_writer.py` treats a claim-release failure as a
   publication failure and enters compensation. A transient cleanup lock can
   therefore undo an otherwise valid publication; whether that coupling is
   correct is a separate governance-semantic decision from retry mechanics.

## Related Work And Non-Duplication

- `WI-5031` / `gtkb-wi5031-sqlite-busy-timeout-tuning` added a 30-second
  busy timeout to `groundtruth_kb.db.KnowledgeDB`, but
  `bridge_work_intent_registry.py` opens SQLite directly with its own 10-second
  timeout. WI-5031 is resolved and did not cover this script path.
- `WI-4803` / `gtkb-wi4803-release-work-intent-on-subprocess-failure` added a
  missing release call after dispatched-worker failure. It does not make a
  release resilient or diagnosable once SQLite contention occurs.
- `WI-5758` / `gtkb-wi5758-publication-deadlock-closure` concerns publication
  capability and claim-finalization crash windows. The present incident is the
  narrower database-lock behavior of the claim release primitive itself.
- `bridge/gtkb-advisory-implementation-start-peer-scan-liveness-001.md`
  records a separate append-only SoT scale failure encountered in this session.
  That issue is algorithmic bridge-tree enumeration, not a SQLite write lock.

Corrective intake should attach this incident to an existing exact-scope active
item if one exists. It should not reopen resolved WI-5031 as if that work had
failed its approved scope, and it should not silently broaden WI-5758.

## Recommended Corrective Direction

1. Separate one-time/additive schema migration from the hot release primitive,
   or prove why schema initialization must remain on every registry connection.
2. Add a small total release deadline with bounded retry and jitter for
   transient `SQLITE_BUSY`/locked outcomes. Preserve exact slug-plus-session
   deletion on every attempt.
3. After a contention failure, re-read authoritative state before retrying. A
   missing claim is idempotent success; a different session holder is not this
   caller's claim and must never be deleted.
4. Emit structured diagnostics: operation phase, attempt count, elapsed wait,
   database path, slug, caller session, SQLite error code/name when available,
   and final state classification. Do not expose secrets.
5. Keep transactions minimal and close every created connection on schema/open
   failure as well as normal release failure.
6. Do not add automatic process killing, lock-file deletion, dispatcher
   activation, or database surgery as recovery behavior.
7. Preserve TTL as a final abandonment bound, not the expected response to a
   routine transient writer collision.
8. Make dispatcher cleanup failure durable rather than silently swallowing it,
   and explicitly decide whether post-write claim cleanup failure should
   compensate a byte-valid governed publication.

## Acceptance Evidence For A Future Correction

- A deterministic two-connection fixture holds a competing write transaction,
  invokes release, then unlocks within the retry budget; release succeeds and
  the exact claim is removed once.
- A fixture holds the lock beyond the total deadline; release fails closed with
  phase/attempt/elapsed diagnostics and the exact claim remains unchanged.
- A foreign session replaces or owns the row between attempts; no retry can
  delete that row.
- Two same-session releases are idempotent and leave no row.
- A schema/open failure closes the connection and reports the correct phase.
- Uncontended release stays fast and does not perform avoidable global schema
  work on every call.
- Existing claim acquire, extend, lapse, dispatcher cleanup, and publication
  finalization tests remain green.
- Caller-integration tests prove dispatcher cleanup emits durable failure
  evidence and pin the separately approved publication-compensation policy.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`

## Specification-Derived Verification Plan

| Requirement | Future verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Independent Loyal Opposition review of this `NEW` report | Role-correct verdict; no self-review. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Link this incident into the selected active project/WI or explicit no-op disposition | Finding remains durable and non-duplicative. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run unlock-within-budget, timeout, holder-change, idempotence, and schema-failure tests | All concurrency branches have deterministic evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Validate active project membership and inherited project PAUTH before later code/test mutation | No orphan or WI-only approval is used. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Exercise the ordinary claim CLI after correction | No bypass or direct database edit is needed. |
| `GOV-WORK-TREE-HYGIENE-001` | Run tests while unrelated workers/processes exist | No foreign process or path is mutated. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Compare exact-row deletion semantics before/after | Safety is preserved while liveness and diagnostics improve. |

## Decision Needed

No immediate owner decision is required to preserve or review this incident.
If Loyal Opposition routes the finding to a new unapproved backlog item rather
than an already approved project, Prime Builder must present that item to the
owner as a single AUQ before proposing implementation.

## Explicit Non-Approval And TAFE Exclusion

This Advisory Report is not a GO, project authorization, implementation-start
packet, or authorization to modify source, tests, configuration, metadata,
dispatcher/TAFE state, Git history, deployment, credentials, or external
systems. The TAFE dispatcher is deliberately disabled and was not activated or
mutated during diagnosis or report preparation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
