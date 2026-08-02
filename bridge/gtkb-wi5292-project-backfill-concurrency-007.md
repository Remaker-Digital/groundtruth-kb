REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: OpenAI Codex Desktop
author_model_version: Codex Desktop interactive runtime; exact foundation-model identifier is not exposed to this task
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; ordinary per-WI authority only; former CF-10 all-program serialization authority rescinded; dispatcher and TAFE deliberately disabled
author_metadata_source: task-local interactive transcript and current session envelope

bridge_kind: prime_proposal
Document: gtkb-wi5292-project-backfill-concurrency
Version: 007
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5292-project-backfill-concurrency-006.md
Responds-to SHA-256: 686BE2B04E60A9B9FD8E7A12DDF3E079DC3A2CFD5D12A99CBDF289572540A50C

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5292
Related Work Items: WI-5251, WI-5370, WI-5675, WI-5716, WI-5717, WI-5761, WI-5915

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_project_artifacts.py"]

implementation_scope: source_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
source_mutation_expected: true

KB-mutation completeness: this implementation performs no MemBase mutation.
It does not write `groundtruth.db`; the implementation changes only the two
declared source/test files, and all transaction behavior is exercised against
isolated test databases.

# Revised Proposal — WI-5292 Concurrency-Safe Project Artifact Backfill

## Revision Claim

This revision accepts v006's operation-time authority findings and preserves
the independently accepted v003 two-file transaction design. The stale
Authority Foundations route is not reused: that project is currently `active`
v4 but retains non-null `completed_at=""`, so WI-5761's project-reactivation
invariant remains applicable to it.

WI-5292 is now an active member of
`PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`, membership version 1, row
4298. That project is active v2 with `completed_at=NULL`. Its list-free project
PAUTH named above is active v5, unexpired, covers source and test, and retains
all bridge, claim, implementation-start, verification, nonimpairment, and
forbidden-operation gates. This is a rehome, not an inference that backlog
openness reactivated the retired or scarred route.

The defect reproduced again on 2026-08-01 while this Prime session used three
ordinary readback commands in parallel after creating WI-5915. One process
failed during `KnowledgeDB._ensure_schema()` -> `_migrate_schema()` ->
`_backfill_project_artifacts_from_work_items()` ->
`_insert_project_membership_if_missing()` with:

```text
sqlite3.IntegrityError: UNIQUE constraint failed:
project_work_item_memberships.id, project_work_item_memberships.version
```

The same commands succeeded when repeated serially. This is current production
evidence of the exact WI-5292 race, not a timer failure and not justification
for global worker serialization.

This v007 remains non-executable until a fresh independent `GO`, exact
`go_implementation` claim, and fresh schema-v3 start packet bind these exact
two targets. It does not mutate protected source/test files, live MemBase,
dispatcher/TAFE, or Git merely by being filed.

## Exact Predecessor And Authority Binding

- v003 accepted technical proposal: 24,240 bytes, SHA-256
  `AB645567E200CFEE58C31B604D4DE98A20BE67A4BC6CB1541D10D6FC0104308B`;
- v004 historical independent `GO`: accepted the bounded transaction design
  but is no longer implementation authority;
- v005 Prime `NO-ACTION`: correctly rejected stale operation-time authority;
- v006 independent `NO-GO`: 7,129 bytes, SHA-256
  `686BE2B04E60A9B9FD8E7A12DDF3E079DC3A2CFD5D12A99CBDF289572540A50C`;
- current project: `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE` v2,
  `active`, `completed_at=NULL`;
- current WI membership: version 1, active, row 4298;
- current PAUTH: exact named project-scope record v5, active, unexpired,
  list-free, source/test allowed;
- former Authority Foundations route: not relied upon; its lifecycle remains
  within WI-5761's separate correction scope.

Any predecessor, project, membership, PAUTH, target, claim, packet, or
worktree drift fails closed before implementation.

## Preserved Technical Design

The source repair remains the exact v003 design:

1. **Lock-free complete-projection path.** Read compatibility work-item rows
   and return without a write transaction when every required project,
   subproject, and membership row already exists.
2. **One short gap-repair transaction.** When a gap is observed, execute
   `BEGIN IMMEDIATE`, re-read the complete current input after lock acquisition,
   repeat every existence decision on the same connection, append only rows
   still missing, commit once, and roll back the whole transaction on any
   `BaseException` before re-raising.
3. **No exception laundering.** Do not add broad `INSERT OR IGNORE`,
   unqualified conflict-ignore, blanket `IntegrityError` suppression, an
   arbitrary retry loop, or a global process/worker leader. Concurrency is
   resolved by the short locked re-read and atomic decision.
4. **No nested commit.** Helpers reused inside the transaction must use the
   same connection and leave commit/rollback ownership with the explicit
   backfill transaction.

The implementation must not change project or membership identity, version,
ordering, authority, public CLI, SQLite timeout, WAL mode, general
`KnowledgeDB` construction, or live database rows. Timer and broader common
transaction-policy work stays with its separately governed WIs.

## Current Target Evidence

| Target | Current SHA-256 | Git state |
| --- | --- | --- |
| `groundtruth-kb/src/groundtruth_kb/db.py` | `F30A24F1785B23BBDF70BAB6AF9958F49FD40B1EB285BD31D598A12E99D506F7` | clean |
| `groundtruth-kb/tests/test_project_artifacts.py` | `927860CBF371056429F24291425A5C5744A1A0CC391A3A687BD971295C2655B4` | clean |

Focused current baseline:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest
  groundtruth-kb/tests/test_project_artifacts.py
  groundtruth-kb/tests/test_db_busy_timeout.py -q --tb=short
```

Result: `35 passed, 1 unrelated third-party deprecation warning` in 19.41
seconds. The red condition is the concurrent missing-projection wave, now
confirmed by the new live recurrence and the earlier deterministic 12-process
v003 reproduction.

## Required Test Additions

Add deterministic coverage in `test_project_artifacts.py`:

1. A synchronized Windows `spawn` wave starts at least twelve independent
   `backlog list`, `projects list`, and `spec list` processes against one
   temporary database with missing compatibility project/membership rows.
   Every process exits zero. History contains exactly one version-1 project row
   and one version-1 membership row per logical identity.
2. An injected exception after at least one project insert proves the same
   `_get_conn()` connection contains no partial project or membership rows and
   has no open transaction after rollback. A clean retry appends exactly once;
   a repeat remains idempotent.
3. A normalized SQLite trace on a completed projection proves no `BEGIN
   IMMEDIATE`, project insert, or membership insert occurs and row/version
   counts remain unchanged.
4. Existing malformed-row, busy-timeout, project-artifact, and lifecycle tests
   remain unchanged and green.

Test synchronization occurs before production transaction acquisition so the
test does not introduce a barrier deadlock after the fix. Generous external
test time budgets must not replace deterministic completion or hide deadlock.

## Scope Separation

- WI-5292 owns only compatibility project/membership backfill atomicity in
  `db.py` and its focused project-artifact tests.
- WI-5251 remains the duplicate historical observation and receives no source
  implementation from this thread.
- WI-5915 is evidence-trigger-only: creating its work-item row exposed the
  existing compatibility-backfill race, but WI-5915 owns only the separate
  WI-5370 invalid-terminal incident repair and receives no implementation from
  this thread.
- WI-5675 owns work-item/test identifier allocation plus measured broad
  MemBase/replacement-store capacity.
- WI-5717 owns the cross-service MemBase mutation audit and common transaction
  contract.
- WI-5716 owns end-to-end parallel Prime Builder launch readiness.
- WI-5761 owns project reactivation lifecycle coherence, including the scarred
  Authority Foundations route that v007 deliberately avoids.

No registry, bridge resolver, dispatcher/TAFE, claim service, publication
service, project/PAUTH lifecycle, live `groundtruth.db`, Git/index/ref,
credential, deployment, release, or external-system mutation is absorbed.

## Specification Links

- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — concurrent MemBase operations
  preserve every accepted append-only version without duplicate identifiers,
  mixed state, lost updates, or false success.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` — project and membership rows remain
  append-only, canonical, and atomic; failed operations append no partial
  affected state.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — fresh read commands remain usable and
  do not rely on lucky serialization or retry.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — preserve public behavior and
  unrelated bytes while removing the exact race.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — deterministic process,
  rollback, no-gap, idempotency, and quality evidence make the change
  independently evaluable.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — active project,
  exact membership, PAUTH, GO, claim, and start authority are conjunctive.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — v007 is fresh Prime review input only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — exact specifications,
  project, PAUTH, WI, and targets are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — terminal verification
  requires every mapped executed test.
- `GOV-WORK-TREE-HYGIENE-001` — both targets begin clean and unrelated dirty
  work remains foreign.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the recurrence, rehome, proposal,
  tests, report, and verdict remain durable and forward-only.
- `GOV-STANDING-BACKLOG-001` — WI-5292, WI-5251, WI-5675, WI-5716, WI-5717,
  and WI-5761 retain separate ownership.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all artifacts and temporary test
  roots remain inside `E:/GT-KB`.

## Prior Deliberations

- `DELIB-202667517` — owner requires highly parallel Prime Builder operation;
  shared control-plane changes use short linearizable or conflict-detected
  transactions, not global quiescence.
- `DELIB-202667521` — formal parallel-operation requirement and executable
  assertion amendment.
- `DELIB-202666274` and `DELIB-202667714` — modernization authorization and
  current Assurance PAUTH provenance; every later bridge/start gate remains.
- WI-5292 v001-v006 — complete design, independent review, stale-authority
  stop, and exact recovery requirements.

## Owner Decisions / Input

No new owner decision is required. The owner has explicitly required highly
parallel SoT operation and correction or replacement of MemBase bottlenecks.
This revision implements the already independently accepted narrow race repair
under a coherent active project rather than expanding policy or weakening a
gate.

## Requirement Sufficiency

Existing requirements are sufficient. The live 2026-08-01 recurrence confirms
the existing WI-5292 defect; the v003/v004 technical design was independently
accepted; v006 required fresh active project and successor authorization, now
provided through the separate active Assurance membership and PAUTH. No new
specification or owner tradeoff is introduced.

## Specification-Derived Verification Plan

| Requirement | Executed evidence required | Expected result |
| --- | --- | --- |
| Concurrent preservation | synchronized >=12-process mixed CLI wave | every process exits zero; no integrity/lock/timeout failure or lost row |
| Atomic failure | injected mid-backfill exception observed on same connection | zero partial project/membership rows and no open transaction |
| Canonical versioning | query temporary history after wave and retry | exactly one version-1 row per logical project and membership |
| No-gap read behavior | normalized trace on complete projection | no `BEGIN IMMEDIATE` or project/membership insert; counts unchanged |
| Idempotency | repeat complete wave and clean retry | zero additional rows or changed decisions |
| Nonimpairment | focused project-artifact and busy-timeout suites | all pass; only disclosed unrelated warning permitted |
| Static quality | Ruff check and format check on both targets | exit 0 |
| Scope/currentness | exact hashes, Git status, PAUTH, claim/start, diff census | only two authorized targets change; no foreign bytes absorbed |
| Governance | factual report and independent verification | role-valid report/verdict and terminal finalization after all evidence |

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5292 v003/v004/v005/v006; 2026-08-01 live parallel readback recurrence; DELIB-202667517; DELIB-202667521; Assurance membership row 4298",
  "canonical_authority": "Versioned MemBase projects and project_work_item_memberships, current work-item compatibility input, and current project authorization evaluation",
  "primary_route": "KnowledgeDB initialization performs a lock-free complete-projection check and one short BEGIN IMMEDIATE re-read transaction only when compatibility rows are missing",
  "before_behavior": "Concurrent read-only CLI starts can race through schema compatibility check-then-insert and one fails with a duplicate project or membership version IntegrityError.",
  "after_behavior": "Complete projections remain read-only and parallel; missing projections are re-read under one short write lock and appended exactly once without partial state or swallowed defects.",
  "self_descriptive_naming": "project_artifact_gap, backfill_transaction_owner, project_id, membership_id, logical_version, rollback_probe, no_gap_trace, and concurrent_cli_wave",
  "obsolete_guidance_disposition": "The retired/scarred Authority Foundations authority route is not reused; broad conflict-ignore, blanket IntegrityError suppression, arbitrary retry, and global worker serialization are rejected.",
  "history_preservation": "Existing work-item, project, membership, bridge, specification, and test history remains append-only; only genuinely missing compatibility version-1 rows are created by ordinary runtime behavior.",
  "baseline": {
    "current_focused_suite": "35 passed with one unrelated third-party deprecation warning",
    "live_recurrence": "one of three parallel readback commands failed on project_work_item_memberships id/version uniqueness",
    "target_hashes": "db.py F30A24F1...506F7; test_project_artifacts.py 927860CB...655B4"
  },
  "expected_result": {
    "concurrent_wave": "all processes exit zero with one logical version per row",
    "rollback": "zero partial rows and no open transaction after injected failure",
    "no_gap": "no write transaction or insert on complete projections"
  },
  "rollback": {
    "instructions": "Before terminal verification, revert only the exact bounded two-target implementation through a separately authorized focused Git operation.",
    "verification": "Rerun concurrent-wave, rollback, no-gap, focused suite, Ruff, exact hash/status, and changed-path census; no live data repair is required."
  },
  "hard_invariants": [
    "no project or membership identity, version, ordering, or authority semantics change",
    "complete-projection reads never acquire a write transaction",
    "gap repair owns one short transaction and one commit or full rollback",
    "unexpected integrity and foreign-key errors remain visible",
    "no global leader, unbounded wait, arbitrary retry loop, or broad conflict-ignore",
    "no live database, dispatcher, TAFE, Git, project, PAUTH, credential, deployment, release, or unrelated mutation"
  ],
  "fail_closed_conditions": [
    "project, membership, PAUTH, predecessor, target hash, claim, or schema-v3 packet is stale or missing",
    "either target is foreign-dirty or an additional target becomes necessary",
    "any concurrent, rollback, no-gap, idempotency, focused, or Ruff check fails",
    "the change would suppress a non-race integrity defect or partially commit",
    "the implementation would depend on Authority Foundations lifecycle inference or global quiescence"
  ],
  "essential_context_preservation": "Preserve v003's full design and red baselines, v006's authority findings, the new live recurrence, exact current target hashes, active Assurance membership/PAUTH, separate WI ownership, transaction boundaries, residual bounded-lock behavior, and all independent review/start/finalization gates."
}
```

## Acceptance Criteria

1. At least twelve synchronized spawned CLI processes sharing one temporary
   database all complete successfully across backlog, project, and spec reads.
2. Exactly one version-1 project row and one version-1 membership row exist per
   logical identity after the concurrent wave.
3. A completed projection performs no write transaction or insert and appends
   no row on repeat.
4. An injected exception after at least one insert rolls back the entire
   backfill on the same connection; clean retry completes once and remains
   idempotent.
5. No broad conflict-ignore, blanket integrity-error suppression, arbitrary
   retry, global leader, or unbounded wait is added.
6. Focused project-artifact and busy-timeout tests plus Ruff check/format pass.
7. Only the two declared protected targets change under a current GO, exact
   claim, and fresh schema-v3 packet; live MemBase and foreign work remain
   unchanged by implementation/tests.
8. A factual report records exact diff and executed evidence, and a distinct
   Loyal Opposition session independently verifies before terminalization.

## Risks And Rollback

- **Over-serialization:** the optimistic no-gap trace must prove ordinary reads
  remain free of write transactions.
- **Partial transaction:** same-connection failure injection must prove full
  rollback and closed transaction state.
- **Hidden corruption:** unexpected integrity errors remain visible; conflict
  suppression is forbidden.
- **Contention:** the existing bounded SQLite lock policy remains observable;
  this WI fixes the uniqueness race, not every prolonged-lock source.
- **Rollback:** before terminal verification, revert only the exact two-target
  diff through separately authorized focused Git work and rerun the complete
  matrix. No live database rewrite is part of rollback.

## Candidate Pre-Filing Gates

Before filing, rerun exact candidate applicability, mandatory clause,
credential, pattern, duplicate-thread, WI-collision, citation, project/PAUTH,
claim, target-currentness, and writer-compliance checks. Filing requires the
exact next-version draft claim, receipt-consumed publication, canonical v007
readback, released claim, and no pending sidecar.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/tests/test_project_artifacts.py`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
