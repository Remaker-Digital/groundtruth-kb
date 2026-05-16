# Implementation Proposal — Seed the Harnesses Registry Table (WI-3342 Slice A)

bridge_kind: prime_implementation_proposal
Version: 001 (NEW)

target_paths: ["scripts/seed_harness_registry.py", "platform_tests/scripts/test_seed_harness_registry.py", "harness-state/harness-registry.json"]

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3342

## Summary

This is Slice A of work item WI-3342, pulled ahead of WI-3341 per the owner's
2026-05-16 decision ("Seed the harnesses table first").

It adds a deterministic, idempotent migration that seeds the live AI coding
harnesses into the DB-backed `harnesses` registry table from the legacy
`harness-state` JSON. After this slice, the `harnesses` table holds harness
`A` (codex) and harness `B` (claude) at `status = active` with their current
roles, and the FR5 hot-path projection reflects them.

This unblocks WI-3341 Slice A: with the registry populated, `gt harness set-role`
can enforce FR9's active-harness eligibility gate against an authoritative
table rather than against legacy role-map membership. It is the prerequisite
the WI-3340 and WI-3341 NO-GOs both traced back to.

WI-3342's remaining work — cutting the 8+ `harness-state/*.json` readers over to
the generated projection and retiring the legacy JSON — is WI-3342 Slice B, a
separate later thread. This slice does **not** flip role authority:
`harness-state/role-assignments.json` remains the authoritative role substrate
until Slice B.

## Scope

In scope:

1. `scripts/seed_harness_registry.py` — a new migration script. It reads
   `harness-state/harness-identities.json` (harness name to durable id) and
   `harness-state/role-assignments.json` (id to role-set and harness type),
   joins them, and for each harness not already present in the `harnesses`
   table inserts a row via `KnowledgeDB.insert_harness` at `status = active`
   carrying the harness id, name, type, and role-set. It then regenerates the
   FR5 projection via `harness_projection.generate_harness_projection`. The
   migration is idempotent — a harness already present in the table is skipped,
   so a re-run is a no-op.
2. `platform_tests/scripts/test_seed_harness_registry.py` — spec-derived tests.
3. Executing the migration once against the live MemBase so the real
   `harnesses` table is seeded; the post-implementation report records the
   resulting `harnesses` table and projection state.

Out of scope:

- The WI-3342 Slice B reader migration — cutting the 8+ `harness-state/*.json`
  readers over to the generated projection and retiring
  `harness-identities.json` / `role-assignments.json`. This slice only
  populates the table; it does not change which artifact is authoritative for
  role or identity resolution.
- WI-3341 (FR9 `gt harness set-role`, the single-prime-builder invariant) and
  WI-3341 Slice B (FR7). They consume the seeded table; they are not modified
  here.
- `reviewer_precedence`, `invocation_surfaces`, and `capabilities_ref` are not
  populated — the legacy `harness-state` JSON carries no such data; those
  columns are seeded as NULL and are FR7 (WI-3341 Slice B) and FR8 (WI-3344)
  territory.
- No change to the `harnesses` table schema, `KnowledgeDB.insert_harness`, the
  FSM module, the projection generator, or any `gt harness` verb.

## In-Root Placement Evidence

All three target paths are within the GT-KB project root `E:\GT-KB`:

- `E:\GT-KB\scripts\seed_harness_registry.py`
- `E:\GT-KB\platform_tests\scripts\test_seed_harness_registry.py`
- `E:\GT-KB\harness-state\harness-registry.json`

No `applications/` paths and no paths outside the platform root; this bridge
file resides under `E:\GT-KB\bridge\`. The migration reads only in-root
`harness-state` JSON and writes only the in-root `harnesses` table and the
in-root projection file. All output paths are declared in-root, compliant with
the in-root placement constraint of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — governing requirement. FR1 specifies the
  append-only `harnesses` table as the authoritative store of harness records;
  this slice populates it from the existing live state. FR5 specifies the
  generated hot-path projection; the migration regenerates it after seeding.
  FR9 (WI-3341) consumes the seeded table for active-harness eligibility — this
  slice is its prerequisite.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the harness-registry architecture;
  the role-set wire form the seeded `role` column carries.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal
  cites all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  derives tests from FR1 (table population) and FR5 (projection regeneration).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the file bridge is the canonical workflow
  state; this proposal is filed as a NEW bridge entry.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; the migration is a
  governed deterministic artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the script follows the
  established focused-module pattern.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the proposal lifecycle is
  NEW then GO/NO-GO then VERIFIED.

## Prior Deliberations

- `DELIB-2079` — Antigravity Integration project design: a DB-backed harness
  registry plus a generated SessionStart projection. The seeded table is that
  registry.
- `DELIB-2080` — the role-portability amendment (FR9). Relevant because the
  seeded table is the substrate FR9's `gt harness set-role` will read for
  active-harness eligibility.
- Owner AskUserQuestion of 2026-05-16 ("Seed the harnesses table first") — the
  owner chose to pull the table-seeding step ahead of WI-3341 so FR9's
  `set-role` can enforce active-harness eligibility against an authoritative
  table. This slice implements that decision. The owner-decision-tracker
  records it in `memory/pending-owner-decisions.md`.
- WI-3341 Slice A NO-GO `gtkb-harness-role-portability-fr9-002.md` (finding F1)
  — established that a role-map-only `set-role` does not satisfy FR9; the
  seeded table is the resolution.
- Sibling VERIFIED threads `gtkb-harness-registry-table-schema` (WI-3337 — the
  table and `insert_harness`), `gtkb-harness-registry-hot-path-projection`
  (WI-3338 — the projection generator), `gtkb-harness-lifecycle-fsm` (WI-3339),
  and `gtkb-harness-cli-command-group` (WI-3340 — the `gt harness` CLI).
- A pre-proposal deliberation search confirmed `DELIB-2079` and `DELIB-2080`
  govern; no conflicting prior deliberation was found.

## Owner Decisions / Input

This proposal implements owner-decided work and depends on owner approval
recorded as:

- `DELIB-2079` (`outcome=owner_decision`) — owner approved the Antigravity
  Integration design including the DB-backed harness registry.
- Owner AskUserQuestion of 2026-05-16 — owner selected "Seed the harnesses
  table first," directing that the WI-3342 table-seeding step be pulled ahead
  of WI-3341. This slice is that deliverable. Recorded by the
  owner-decision-tracker hook (`detected_via: ask_user_question`).
- `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization for `PROJECT-HARNESS-REGISTRY-REFACTOR`,
  covering WI-3337 through WI-3344.

The project authorization is owner-approval evidence for the bounded project
work; it does not replace this proposal's Loyal Opposition review or the GO
gate.

## Requirement Sufficiency

Existing requirements sufficient. FR1 specifies the `harnesses` table that this
slice populates; FR5 specifies the projection it regenerates. Two
interpretation notes are recorded transparently for the reviewer.

Interpretation note 1 — seeded status. The migration seeds the two live
harnesses at `status = active`, not at the FSM's initial `registered` state.
This is the correct migration semantics: harnesses `A` and `B` are
already-live, in-service harnesses being *imported* into the registry, not
newly *registered* ones. The FR2 lifecycle FSM governs future transitions
*from* the seeded state; it does not govern the one-time import. Seeding at the
true current status (`active`) is faithful to reality and avoids a fictitious
`registered -> active` transition history that never occurred.

Interpretation note 2 — authority boundary. This slice populates the
`harnesses` table; it does **not** make the table the authoritative substrate
for role or identity resolution. `harness-state/role-assignments.json` and
`harness-state/harness-identities.json` remain authoritative until WI-3342
Slice B cuts the readers over and retires them. The seeded `role` column is
imported from `role-assignments.json` and is consistent with it at seed time;
keeping the two coherent under subsequent `set-role` operations, and ultimately
retiring the JSON, is WI-3341 Slice A and WI-3342 Slice B work, not this
slice's.

## Implementation Plan

### 1. New migration script `scripts/seed_harness_registry.py`

A deterministic, idempotent migration. Imports the standard library,
`groundtruth_kb.config`, `groundtruth_kb.db`, and
`groundtruth_kb.harness_projection`.

- `_read_legacy_harnesses(project_root)` — reads
  `harness-state/harness-identities.json` (harness name to durable id) and
  `harness-state/role-assignments.json` (id to record). Joins them keyed on the
  durable id and returns, per harness: `id`, `harness_name` (from the identity
  map, falling back to the harness type or the id), `harness_type` (from the
  role record, falling back to the name), and `role` (the role-set list,
  normalized).
- `seed_harness_registry(db, project_root, *, changed_by="harness-registry-seed")`
  — for each legacy harness, if `db.get_harness(id)` is `None`, calls
  `db.insert_harness(id=..., harness_name=..., harness_type=..., role=...,
  status="active", changed_by=..., change_reason=...)`; otherwise records it as
  skipped. After the inserts it calls
  `harness_projection.generate_harness_projection(db, project_root)` to refresh
  the FR5 projection. Returns a summary dict (`seeded`, `skipped`,
  `projection_path`).
- `main()` — resolves the project config via `GTConfig.load()`, opens the DB,
  runs `seed_harness_registry`, prints the summary, and returns an exit code.

The migration is idempotent: a second run finds every harness already present
and seeds nothing.

### 2. New tests `platform_tests/scripts/test_seed_harness_registry.py`

Spec-derived tests per the Spec-to-Test Mapping. Each test builds a temporary
project with fixture `harness-state` JSON and a fresh `KnowledgeDB`.

### 3. Execute the migration

After GO and implementation, run `python scripts/seed_harness_registry.py` once
against the live MemBase so the real `harnesses` table is seeded with harnesses
`A` and `B`, and `harness-state/harness-registry.json` is regenerated. The
post-implementation report records the resulting state
(`gt harness list` output).

## Spec-to-Test Mapping

`REQ-HARNESS-REGISTRY-001` FR1 (the authoritative `harnesses` table) and FR5
(the generated projection) are verified as follows.

Tests — `platform_tests/scripts/test_seed_harness_registry.py`:

- `test_seed_inserts_live_harnesses_at_active` — seeding a two-harness fixture
  inserts both into the `harnesses` table at `status = active` (FR1).
- `test_seed_carries_role_and_identity_from_legacy_json` — each seeded row's
  `id`, `harness_name`, `harness_type`, and `role` match the joined
  `harness-identities.json` / `role-assignments.json` source.
- `test_seed_is_idempotent` — running the migration twice leaves exactly one
  version per harness; the second run reports every harness skipped.
- `test_seed_skips_harness_already_in_table` — a harness pre-inserted into the
  table is reported skipped and not re-inserted.
- `test_seed_regenerates_projection` — after seeding, the FR5 projection file
  exists and lists the seeded harnesses (FR5).
- `test_seed_summary_reports_seeded_and_skipped` — the returned summary
  enumerates the seeded and skipped harness ids.

## Risks

- **Seeding at `status = active` (note 1).** *Mitigation:* documented as
  migration semantics; the FSM governs transitions from the seeded state, not
  the import; tests assert the seeded status explicitly.
- **Dual role data — `harnesses.role` and `role-assignments.json` (note 2).**
  *Mitigation:* at seed time the table's `role` column is imported from
  `role-assignments.json` and is consistent with it; this slice does not flip
  authority; keeping them coherent and retiring the JSON is WI-3341 / WI-3342
  Slice B scope, stated explicitly.
- **Re-running the migration.** *Mitigation:* the migration is idempotent
  (skip-if-present), verified by `test_seed_is_idempotent`.
- **A harness present in one legacy JSON but not the other.** *Mitigation:* the
  join keys on the durable id and falls back gracefully for a missing name or
  type; for the live data both harnesses are present in both files.

## Rollback

Remove `scripts/seed_harness_registry.py` and
`platform_tests/scripts/test_seed_harness_registry.py`. The seeded `harnesses`
rows are append-only MemBase versions and are not deleted (append-only
discipline); they are harmless if WI-3341 does not proceed, and the projection
can be regenerated from the table at any time. No schema change is involved.

## Verification Procedure

Run, from the project root:

- `python -m pytest platform_tests/scripts/test_seed_harness_registry.py -q`
- `python -m pytest groundtruth-kb/tests/test_harness_projection.py groundtruth-kb/tests/test_db.py -q`
  (regression — the projection generator and `insert_harness` are consumed
  unchanged)
- `python -m ruff check scripts/seed_harness_registry.py platform_tests/scripts/test_seed_harness_registry.py`
- Post-seed evidence: `python scripts/seed_harness_registry.py` then
  `gt harness list` showing harnesses `A` and `B` at `status = active`.

Expected: all new tests pass, the regression suites remain green, and the live
`harnesses` table holds the two seeded harnesses. Observed counts and the
seeded state are recorded in the post-implementation report.

## Acceptance Criteria

- `scripts/seed_harness_registry.py` reads the legacy `harness-state` JSON and
  seeds each live harness into the `harnesses` table at `status = active` with
  its id, name, type, and role-set.
- The migration is idempotent — a re-run seeds nothing and reports every
  harness skipped.
- After seeding, the FR5 projection (`harness-state/harness-registry.json`)
  reflects the seeded harnesses.
- The live `harnesses` table, after the migration is executed, holds harnesses
  `A` (codex, loyal-opposition) and `B` (claude, prime-builder) at
  `status = active`.
- All spec-derived tests pass; `test_harness_projection.py` and `test_db.py`
  remain green.
- No change to the `harnesses` schema, `insert_harness`, the FSM, the
  projection generator, or any `gt harness` verb; `role-assignments.json` and
  `harness-identities.json` remain authoritative (no reader migration here).

## Bridge Protocol Compliance

This proposal is filed as `bridge/gtkb-harness-registry-seed-001.md` with a
corresponding `bridge/INDEX.md` entry at `NEW` status, inserted at the top of
the entry list per the file-bridge protocol. It is WI-3342 Slice A; the WI-3342
reader migration is Slice B, a separate later thread. No prior bridge version
is deleted or rewritten; `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001`. The mandatory applicability and clause
preflights are run after the INDEX entry exists; their results are recorded in
the review verdict.

## Clause Scope Clarification

This proposal is not a bulk operation. It adds one migration script and one
test file and seeds two harness records that already exist in the live
`harness-state` state; it does not inventory, batch-mutate, promote, retire, or
sweep multiple unrelated artifacts. The `GOV-STANDING-BACKLOG-001`
bulk-operations visibility clause therefore does not substantively apply. Owner
approval for the bounded project work is recorded via `DELIB-2079`, the
2026-05-16 "seed the harnesses table first" decision, and the active project
authorization
`PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
