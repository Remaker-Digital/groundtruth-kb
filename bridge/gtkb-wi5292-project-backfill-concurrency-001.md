NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=codex-desktop; goal-continuation=true
author_metadata_source: x-codex-turn-metadata

# WI-5292 - Concurrency-safe project artifact backfill

bridge_kind: prime_proposal
Document: gtkb-wi5292-project-backfill-concurrency
Version: 001
Date: 2026-07-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5292

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_project_artifacts.py"]

implementation_scope: source_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

KB Mutation: This proposal performs no MemBase mutation.

The implementation changes Python source and tests only. It does not mutate
the live MemBase database, project records, work-item records,
specifications, registry, dispatcher state, or Git state. Normal bridge
publication and work-item linkage remain supporting governance operations, not
implementation data smuggled through the implementation packet.

---

## Summary

Make the compatibility backfill that projects `current_work_items.project_name`
and `subproject_name` into first-class project and membership rows safe when
multiple processes open the same database concurrently.

The current path is an unprotected check-then-insert sequence. Every
`KnowledgeDB` construction runs `_ensure_schema()`, `_migrate_schema()`, and
`_backfill_project_artifacts_from_work_items()`. Concurrent readers can all see
the same missing project or membership and then attempt version 1. That produces
`sqlite3.IntegrityError` even though the requested CLI operation is read-only.

The repair adds an optimistic no-gap read path for the steady state. When a gap
is observed, the complete project and membership backfill is re-read and applied
inside one `BEGIN IMMEDIATE` transaction. Contenders wait under the existing
bounded SQLite busy timeout, re-read after acquiring the write lock, and observe
the rows accepted from the preceding transaction. This preserves every accepted
append-only row without treating a uniqueness error as normal flow.

## Reproduced Failure

Prime Builder reproduced the defect without modifying protected source:

- A disposable in-root runner seeded 64 work items whose project rows and
  membership rows were absent.
- Twelve Windows `spawn` processes were synchronized at the entry to the live,
  unmodified `_backfill_project_artifacts_from_work_items()` method.
- Result: 1 process succeeded and 11 failed.
- The first collision was `UNIQUE constraint failed: projects.id,
  projects.version` at `db.py:2368`; this proves a membership-only catch or
  upsert would leave the wider race intact.
- The one successful transaction produced 64 membership rows and 64 distinct
  logical `(id, version)` values. No live database or registered artifact was
  mutated.

This deterministic reproduction strengthens the two already-recorded live
recurrences in WI-5292, which failed at the membership insert after concurrent
read-only CLI starts.

## Proposed Implementation

### 1. Preserve a lock-free steady-state read path

Read the current compatibility work-item rows and determine whether any required
root project, subproject, root membership, or subproject membership is absent.
Return without beginning a write transaction when the projection is already
complete. Routine concurrent read-only CLI starts therefore do not serialize on
an unnecessary write lock.

### 2. Serialize the complete gap repair

When the optimistic read detects any gap:

1. execute `BEGIN IMMEDIATE` on the existing connection;
2. re-read the complete current work-item input after the lock is acquired;
3. repeat all existence decisions inside that transaction;
4. append only the still-missing project and membership version-1 rows;
5. commit once after the complete backfill; and
6. roll back the complete transaction on any `BaseException`, then re-raise.

The current `_project_exists`, `_project_membership_exists`, and
`_insert_project_membership_if_missing` helpers may be reused inside the locked
transaction because they resolve to the same connection. Any factoring must
keep the transaction owner explicit and must not introduce nested commits.

### 3. Do not suppress integrity defects

Do not use broad `INSERT OR IGNORE`, unqualified `ON CONFLICT DO NOTHING`, or a
blanket `IntegrityError` catch. Those approaches can hide malformed rows,
foreign-key violations, unexpected duplicate versions, or future schema defects.
Concurrency is prevented by serializing and re-reading the decision, not by
discarding database errors.

### 4. Add deterministic process and rollback coverage

Add two focused tests to `test_project_artifacts.py`:

- A spawned-process CLI regression synchronizes independent `backlog list`,
  `projects list`, and `spec list` invocations at backfill entry against one
  seeded database. Every invocation must exit zero, and the resulting history
  must contain exactly one version-1 project row and one version-1 membership
  row per logical membership.
- An injected mid-backfill exception proves the transaction rolls back all
  project and membership inserts. A subsequent unmodified retry must complete
  once and remain idempotent.

The process helper is test-local and synchronization occurs before production
transaction acquisition. The test therefore exposes the current race without
creating a barrier deadlock after the repair.

## Scope Boundaries

In scope:

- transaction ownership and no-gap detection for the compatibility project
  artifact backfill in `db.py`;
- deterministic multi-process CLI coverage and rollback/idempotency coverage in
  `test_project_artifacts.py`; and
- comments or docstrings needed to make that transaction boundary clear.

Out of scope:

- changing project or membership identity, version, ordering, or authority
  semantics;
- changing the public CLI, configuration schema, SQLite timeout, WAL mode, or
  general `KnowledgeDB` initialization sequence;
- adding retries around arbitrary database errors;
- raw mutation or repair of the live `groundtruth.db`;
- resolving or altering the older duplicate WI-5251;
- registry, bridge protocol, dispatcher, Git, branch, worktree, or release
  changes; and
- launching peer Prime Builder sessions before WI-5716 emits current
  machine-readable `SAFE`.

## Specification Links

- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v2, especially its eleventh
  executable assertion:
  concurrent MemBase operations must preserve every append-only version without
  duplicate identifiers, mixed state, lost updates, or false success.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`, especially `PROJECT-DEP-A2` and
  `PROJECT-DEP-A3`: project and membership records remain canonical,
  append-only, and atomic; failed operations append no partial affected state.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: fresh CLI reads must remain usable and
  must not depend on a lucky retry after startup corruption or collision.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`: the repair must preserve existing
  project, backlog, specification, and CLI behavior while removing the race.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`: deterministic process,
  rollback, idempotency, and quality-gate evidence make the change evaluable.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`: the active
  project-scoped PAUTH, independent GO, claim, and implementation-start packet
  remain required before either protected target changes.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: this NEW proposal is review input only and
  grants no implementation authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: this proposal carries
  concrete specification and PAUTH/project/WI linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: terminal verification must
  independently execute the mapped behavioral and non-impairment checks.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: the observed defect remains linked
  through its owner decision, current requirement, P0 work item, proposal,
  executable regressions, implementation report, and terminal verdict without
  inventing a competing authority surface.

## Prior Deliberations

- `DELIB-202667517`: the owner requires GT-KB to be highly parallel; shared
  control-plane writes must be linearizable or detect a changed preimage, and
  routine global quiescence is not acceptable.
- `DELIB-202667521`: the owner authorized the exact WI-5721 amendment that made
  the parallel-operation clauses and their eleventh executable assertion current.
- `DELIB-202666274`: owner authority behind the active project-scoped PAUTH
  cited by this proposal.

The scaffold's unrelated lifecycle-intake suggestions were reviewed and pruned.
WI-5251 is an older duplicate backlog observation, not an additional authority
or implementation thread; WI-5292 remains the P0 owner for this repair.

## Owner Decisions / Input

No new owner decision is required. The exact behavior is already required by
`DELIB-202667517`, current `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v2, WI-5292's
acceptance criteria, and the active project authorization. This proposal does
not claim that peer-worker launch is safe; WI-5716 remains the exclusive launch
readiness gate.

## Requirement Sufficiency

Existing requirements sufficient. The requirement's eleventh executable
assertion directly requires concurrent
MemBase operations to be linearizable or conflict-detected with no duplicate
identifier or lost append-only version. WI-5292 supplies the concrete defect and
acceptance boundary. No specification amendment is needed for this bounded fix.

## Current Baseline

- `pytest groundtruth-kb/tests/test_project_artifacts.py
  groundtruth-kb/tests/test_db_busy_timeout.py`: 35 passed, 1 unrelated
  third-party deprecation warning.
- `ruff check` on both target files: all checks passed.
- `ruff format --check` on both target files: both already formatted.
- Source SHA-256 before implementation:
  - `db.py`: `f30a24f1785b23bbdf70bab6af9958f49fd40b1eb285bd31d598a12e99d506f7`
  - `test_project_artifacts.py`:
    `927860cbf371056429f24291425a5c5744a1a0cc391a3a687bd971295c2655b4`

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` assertion 11; concurrent operations preserve all accepted rows | New synchronized spawned-process CLI test using `backlog list`, `projects list`, and `spec list` | Every process exits 0; no `IntegrityError`, lock failure, timeout, or lost row |
| `PROJECT-DEP-A2`; failed operation is atomic | New injected mid-backfill failure test | Complete rollback: zero partial project or membership inserts from the failed attempt |
| `PROJECT-DEP-A3`; one canonical append-only membership version | Query the temporary test database after the concurrent wave and after retry | Exactly one project version and one membership version per logical identity; every inserted version is 1 |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`; deterministic fresh reads | Repeat the CLI wave after projection completion | All reads succeed and history counts remain unchanged |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_artifacts.py groundtruth-kb/tests/test_db_busy_timeout.py -q --tb=short` | All tests pass; only disclosed unrelated warnings permitted |
| Code quality and evaluability | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/tests/test_project_artifacts.py` | Exit 0 |
| Code quality and evaluability | `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/tests/test_project_artifacts.py` | Exit 0 |
| Proposal applicability | Applicability and ADR/DCL clause preflights against this exact content | `preflight_passed: true`; no missing required specs; zero blocking clause gaps |

## Acceptance Criteria

1. At least twelve synchronized spawned CLI processes sharing one temporary
   database all complete successfully across the three read routes.
2. Exactly one version-1 project row and one version-1 membership row per
   logical identity exist after the concurrent backfill.
3. A repeat on the completed projection appends no rows and requires no write
   transaction on the no-gap path.
4. An injected failure after at least one insert rolls back the entire backfill;
   a later clean retry completes exactly once.
5. No broad conflict-ignore or blanket integrity-error suppression is added.
6. The existing busy timeout remains the bounded contention mechanism; no
   unbounded retry or sleep loop is introduced.
7. Existing project-artifact and busy-timeout tests plus focused Ruff checks
   remain clean.
8. The live database, registry, dispatcher, Git state, and unrelated worktree
   content remain unchanged by implementation and tests.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": [
    "WI-5292 version 3 records two independent production recurrences.",
    "DELIB-202667517 requires highly parallel Prime Builder operation and linearizable shared-state writes.",
    "The deterministic 12-process pre-implementation reproduction produced 1 success and 11 uniqueness failures."
  ],
  "canonical_authority": "MemBase current_work_items remains backlog authority; versioned projects and project_work_item_memberships remain the first-class project-layer authority.",
  "primary_route": "Existing gt backlog, gt projects, and gt spec reads continue through KnowledgeDB initialization and the compatibility backfill.",
  "before_behavior": "Concurrent read-only CLI starts can race through check-then-insert and fail with a project or membership UNIQUE constraint error.",
  "after_behavior": "Complete projections take the lock-free no-gap path; missing projections are re-read and appended once inside one bounded BEGIN IMMEDIATE transaction.",
  "self_descriptive_naming": "The implementation names the gap predicate, transaction owner, and test helpers after project-artifact backfill concurrency rather than a single observed constraint.",
  "obsolete_guidance_disposition": "No active guidance is replaced; the proposal rejects broad conflict-ignore and blanket IntegrityError suppression as incomplete repair patterns.",
  "history_preservation": "Existing project, membership, work-item, bridge, and test history is unchanged; the repair appends only genuinely missing version-1 compatibility rows.",
  "baseline": {
    "focused_tests": "35 passed with one unrelated third-party deprecation warning",
    "ruff": "check and format-check pass on both targets",
    "concurrency_reproduction": "12 synchronized processes: 1 success and 11 UNIQUE failures"
  },
  "expected_result": {
    "concurrency": "All 12 synchronized CLI processes exit zero",
    "row_integrity": "Exactly one version-1 project row and membership row per logical identity",
    "rollback": "An injected mid-backfill failure leaves no partial project or membership rows"
  },
  "rollback": {
    "instructions": "Revert only the bounded db.py and test_project_artifacts.py implementation diff before terminal verification.",
    "test": "Rerun the focused project-artifact and busy-timeout suite; no live data migration or repair is required."
  },
  "hard_invariants": [
    "No project or membership identity, version, ordering, or authority semantics change.",
    "No broad conflict-ignore or blanket integrity-error suppression is introduced.",
    "Routine complete-projection reads do not acquire a write transaction.",
    "No live database, registry, dispatcher, Git, or unrelated worktree mutation occurs."
  ],
  "fail_closed_conditions": [
    "The exact proposal lacks independent GO, claim, or implementation-start authority.",
    "Any protected target outside the declared two-file scope becomes necessary.",
    "The process regression, rollback regression, focused suite, or Ruff gate fails.",
    "The implementation would require an unbounded retry or partial-commit path."
  ],
  "essential_context_preservation": "The owner decision, current parallel-operation requirement, P0 work item, project PAUTH, exact target paths, deterministic red baseline, transaction design, tests, rollback, and WI-5716 launch boundary remain explicit in the numbered bridge chain."
}
```

## Risk / Rollback

The principal risk is over-serializing every read-only CLI open. The optimistic
no-gap path explicitly avoids that outcome, while the write lock is limited to
the rare interval in which compatibility rows are actually missing. A second
risk is leaving partial project rows after an unexpected exception; one explicit
transaction and rollback test address it.

Rollback is a single bounded source/test revert before terminal verification.
No live data migration, destructive cleanup, schema rewrite, or manual database
repair is part of this change. Existing rows remain valid if the code change is
rolled back.

## Implementation Start Boundary

This NEW proposal is non-executable. Prime Builder must wait for an independent
GO, acquire a fresh exact-session work-intent claim, and mint a matching
implementation-start packet for exactly the two declared target paths before
editing either file. A GO does not authorize Git commit, dispatcher mutation,
peer-worker launch, live-database mutation, or any out-of-scope path.

## Bridge Filing

This proposal is filed as the first status-bearing file in the fresh thread
`gtkb-wi5292-project-backfill-concurrency`. No older bridge file is rewritten.
Dispatcher/TAFE state plus the numbered file chain remain the live workflow
state under `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` because the bounded change removes an observed startup race without
adding a public feature or changing project/membership semantics.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
