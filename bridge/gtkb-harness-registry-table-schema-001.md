# Implementation Proposal — Harnesses Registry Table Schema (WI-3337)

bridge_kind: prime_implementation_proposal
Version: 001 (NEW)

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_db.py"]

Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3337

## Summary

Add the append-only versioned `harnesses` table to the MemBase schema in
`db.py`, together with a `current_harnesses` latest-version view and the
read/write API methods (`insert_harness`, `get_harness`, `list_harnesses`).

This is work item WI-3337 (A1), the lead work item of the
`PROJECT-HARNESS-REGISTRY-REFACTOR` sub-project. It establishes the
DB-authoritative store mandated by `REQ-HARNESS-REGISTRY-001` FR1. The change
is strictly additive — a new table and new methods. It does NOT touch
`harness-state/*.json`, does NOT migrate any reader, and does NOT change any
existing behavior. The generated hot-path projection (WI-3338), the 4-state
lifecycle FSM (WI-3339), the `gt harness` CLI (WI-3340), and the phased reader
migration (WI-3342) are separate downstream work items and are out of scope
here.

## Scope

In scope:

1. A `CREATE TABLE IF NOT EXISTS harnesses (...)` definition added to the
   `db.py` schema initialization, following the established append-only
   versioned pattern (`UNIQUE(id, version)`, `changed_by` / `changed_at` /
   `change_reason` provenance columns) used by `specifications`,
   `work_items`, and `project_authorizations`.
2. Columns per `REQ-HARNESS-REGISTRY-001` FR1: `id`, `version`,
   `harness_name`, `harness_type`, `status` (FSM lifecycle state; default
   `registered`), `role` (JSON-encoded role-set, the wire form already used
   by `harness-state/role-assignments.json`), `reviewer_precedence` (nullable
   integer), `invocation_surfaces` (JSON: interactive + headless surfaces),
   `capabilities_ref`, plus the three provenance columns.
3. A `current_harnesses` view returning the latest version per `id`.
4. DB API methods: `insert_harness(...)` (append a new version, computing the
   next version number), `get_harness(id)` (current row), `list_harnesses()`
   (all current rows).
5. Unit tests in `groundtruth-kb/tests/test_db.py`.

Out of scope: the projection generator, the FSM transition logic, the CLI,
reader migration, and seeding the table from existing JSON state. The table is
created empty; population is WI-3342 (migration). The `status` and `role`
columns are defined here so later work items have a place to write; the
*behavior* over them (FSM validation, role-portability invariant) is WI-3339
and WI-3341.

## In-Root Placement Evidence

All target paths are within `E:\GT-KB`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py` — schema definition and API methods.
- `E:\GT-KB\groundtruth-kb\tests\test_db.py` — unit tests.

No `applications/` paths; no paths outside the GT-KB platform root. Compliant
with the in-root placement constraint of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — governing requirement; FR1 specifies the
  `harnesses` table as the single authoritative store and enumerates its
  columns. FR2 (`status`) and FR9/FR7 (`role`, `reviewer_precedence`) columns
  are defined here; their behavior is downstream.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the architecture decision this
  requirement extends; the `role` column reuses its role-set wire form.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal
  cites all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  derives tests from the linked requirement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the file bridge is the canonical workflow
  state; this proposal is filed as a NEW bridge entry.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are in-root; no
  modification to root-boundary behavior is proposed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; the change adds a governed
  append-only artifact store consistent with artifact-oriented governance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the table follows the
  established versioned-artifact pattern with full provenance.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the proposal lifecycle is
  NEW → (GO/NO-GO) → VERIFIED per the file-bridge protocol.

## Prior Deliberations

- `DELIB-2079` — the consolidated owner decision for the Antigravity
  Integration design (11-question grill, 2026-05-16). Q4 (DB table
  authoritative) and Q5 (single `harnesses` table, topology derived) directly
  authorize this table.
- `DELIB-2080` — the role-portability amendment; confirms the `role` and
  `reviewer_precedence` columns must support full role portability with a
  single-prime-builder invariant.
- The `role` column's JSON role-set wire form originates in the
  `ADR-SINGLE-HARNESS-OPERATING-MODE-001` Path-2 atomic migration (role-set
  schema). No prior deliberation proposed or rejected a `harnesses` DB table;
  the pre-proposal deliberation search (`harness registry table schema`,
  `harnesses table MemBase append-only versioned`) returned only role/session
  lifecycle and MemBase-use context, none in conflict with this proposal.

## Owner Decisions / Input

This proposal implements owner-decided work and depends on owner approval
recorded as:

- `DELIB-2079` (`outcome=owner_decision`) — owner approved the Antigravity
  Integration design via an 11-answer AskUserQuestion grill on 2026-05-16,
  including the DB-backed single-table registry.
- `DELIB-2080` — owner-confirmed role-portability amendment (AskUserQuestion:
  "Single PB, freely reassignable").
- `PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization (owner-decision `DELIB-2079`, includes
  `REQ-HARNESS-REGISTRY-001`).
- Owner AskUserQuestion "persist and kick off" (2026-05-16) authorized creating
  the project structure and beginning the bridge-proposal flow; the owner
  approved the Phase 3c work-item breakdown ("Go").

The project authorization is owner-approval evidence for the bounded project;
it does not replace this proposal's Loyal Opposition review or the GO gate.

## Requirement Sufficiency

Existing requirements sufficient. `REQ-HARNESS-REGISTRY-001` FR1 fully
specifies the table's role and columns. No new or revised requirement is
needed before implementation.

## Implementation Plan

1. In `db.py` schema initialization, add `CREATE TABLE IF NOT EXISTS
   harnesses` with columns `rowid` (autoincrement PK), `id`, `version`,
   `harness_name`, `harness_type`, `status` (`NOT NULL DEFAULT 'registered'`),
   `role`, `reviewer_precedence`, `invocation_surfaces`, `capabilities_ref`,
   `changed_by`, `changed_at`, `change_reason`, and `UNIQUE(id, version)` —
   mirroring the `project_authorizations` table pattern.
2. Add a `current_harnesses` view selecting the maximum-version row per `id`.
3. Add `insert_harness(...)`: resolve the next `version` for the given `id`
   (1 if new), stamp `changed_at`, insert the row, return the persisted row.
4. Add `get_harness(id)`: return the current (latest-version) row or `None`.
5. Add `list_harnesses()`: return all current rows.
6. Add unit tests (see Spec-to-Test Mapping).

The `role` and `invocation_surfaces` columns store JSON text; encoding/decoding
follows the existing convention used for `work_items` JSON-bearing columns. No
existing table, view, method, or caller is modified.

## Spec-to-Test Mapping

`REQ-HARNESS-REGISTRY-001` FR1 (authoritative append-only `harnesses` table) is
verified by tests added to `groundtruth-kb/tests/test_db.py`:

- `test_harnesses_table_created` — opening a DB creates the `harnesses` table
  and the `current_harnesses` view.
- `test_insert_harness_creates_v1` — first `insert_harness` for an id yields
  `version=1` with all FR1 columns persisted.
- `test_insert_harness_version_bumps` — a second `insert_harness` for the same
  id yields `version=2`; `UNIQUE(id, version)` holds.
- `test_get_harness_returns_latest` — `get_harness` returns the highest-version
  row.
- `test_list_harnesses_returns_current_set` — `list_harnesses` returns one
  current row per id across multiple ids and versions.

## Risks

- **Schema addition on existing DBs.** `CREATE TABLE IF NOT EXISTS` is
  idempotent; existing databases gain the empty table on next open with no
  effect on other tables. *Mitigation:* the table is unreferenced by any
  existing code path until WI-3338+; an empty unused table is inert.
- **JSON-column convention drift.** `role` / `invocation_surfaces` store JSON.
  *Mitigation:* reuse the exact encode/decode helper pattern already used for
  `work_items` JSON columns; tests assert round-trip fidelity.

## Rollback

Remove the `harnesses` `CREATE TABLE`, the `current_harnesses` view, the three
API methods, and the added tests. Because nothing else references them, removal
is clean. An existing DB would retain the empty `harnesses` table harmlessly;
it can be dropped manually if required.

## Verification Procedure

Run: `python -m pytest groundtruth-kb/tests/test_db.py -q`

Expected: all five new tests pass alongside the existing `test_db.py` suite
(no regressions).

## Acceptance Criteria

- The `harnesses` table and `current_harnesses` view are created with the FR1
  column set.
- `insert_harness` appends versions monotonically; `UNIQUE(id, version)` is
  enforced.
- `get_harness` / `list_harnesses` return current-version rows.
- All five spec-derived tests pass; the existing `test_db.py` suite is green.
- No existing table, method, or caller is modified.

## Bridge Protocol Compliance

This proposal is filed as `bridge/gtkb-harness-registry-table-schema-001.md`
with a corresponding `bridge/INDEX.md` entry at `NEW` status, inserted at the
top of the entry list per the file-bridge protocol. No prior bridge version is
deleted or rewritten; `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Clause Scope Clarification

This proposal is not a bulk operation. It adds exactly one MemBase table
(`harnesses`) and implements exactly one work item (`WI-3337`); it does not
inventory, batch-mutate, promote, retire, or sweep multiple artifacts. The
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause therefore does not
substantively apply: no bulk-operation inventory artifact, review packet, or
`DECISION DEFERRED` marker is produced because there is no bulk action to
gate. Owner approval for the bounded project work is recorded via the
formal-artifact-approval-backed `DELIB-2079` and the active project
authorization `PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
