# Implementation Proposal — Harness Role Portability and Single-Prime-Builder Invariant (WI-3341 Slice A, FR9) — REVISED-3

bridge_kind: prime_proposal
Version: 007 (REVISED)

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/groundtruth_kb/test_mode_switch_invariants.py", "platform_tests/groundtruth_kb/test_mode_switch_transaction.py"]

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3341

## Summary

This is REVISED-3 of WI-3341 Slice A, responding to the Loyal Opposition NO-GO
at `bridge/gtkb-harness-role-portability-fr9-006.md`. It implements the
role-assignment half of `REQ-HARNESS-REGISTRY-001` FR9: the operational
`gt harness set-role` command, an active-harness eligibility gate, and the
single-prime-builder invariant — now enforced as FR9's **full role partition**.

`gt harness set-role --harness X` promotes harness X to `prime-builder` and
atomically demotes every other recorded harness to `loyal-opposition`, through
the verified `mode_switch` transaction component (`apply_role_switch`). Before
the switch, the command enforces FR9's active-harness eligibility: X must exist
in the DB-backed `harnesses` registry table at `status = active`. After the
switch, `verify_role_partition` confirms the full FR9 partition — exactly one
`prime-builder` and every other harness exactly `["loyal-opposition"]`.

The `-006` NO-GO found that REVISED-2's design verified only the
`prime-builder` count, not the full partition: `apply_role_switch`'s prior
demotion logic rewrites a non-target only when it already holds the requested
role, so a non-target with an empty role set (`[]`) would survive a
`set-role` as neither `prime-builder` nor `loyal-opposition`, and a count-only
postcondition would not catch it. REVISED-3 closes this by refining
`apply_role_switch`'s `prime-builder` branch to demote every non-target
unconditionally — inside the existing transaction boundary — and by upgrading
the postcondition to verify the full partition.

FR9's other half — the FR7 reviewer-precedence primary/fallback
counterpart-selection model — is WI-3341 Slice B, a separate bridge thread.

## Changes From Prior Versions and NO-GO Findings Addressed

The `-002` NO-GO raised two P1 blockers (F1, F2); the `-004` NO-GO raised one
(F1); the `-006` NO-GO raised one (F1). All four are resolved here.

- **`-002` F1 — the proposal omitted FR9's active-harness eligibility gate.**
  Resolved (REVISED-1): `gt harness set-role` reads the DB-backed `harnesses`
  registry table (`KnowledgeDB.get_harness`) and rejects any target absent from
  the registry or whose `status` is not `active`.
- **`-002` F2 — no three-harness / demote-all coverage.** Resolved (REVISED-1):
  added `test_harness_set_role_three_harness_demotes_all_non_targets` and
  `test_harness_set_role_rejects_non_active_harness`; FR6 cited.
- **`-004` F1 — the verified governance spec `GOV-HARNESS-ROLE-PORTABILITY-001`
  was not linked.** Resolved (REVISED-2): added to `Specification Links`, with
  `DELIB-0831` in `Prior Deliberations` / `Owner Decisions`, mapped to the
  role-portability tests.
- **`-006` F1 — the proposal verified the prime-builder count but not FR9's
  full role partition.** Resolved here (REVISED-3). `apply_role_switch`'s
  `prime-builder` branch is refined so every non-target recorded harness is
  written to `["loyal-opposition"]` (not only those already holding
  `prime-builder`); the postcondition is upgraded from a count-only check to
  `verify_role_partition`, which verifies exactly one `prime-builder` AND every
  other harness exactly `["loyal-opposition"]`; and a transaction-level
  regression test seeds a non-target with `role: []` and asserts the post-state
  is a full partition. `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py`
  and `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` are added
  to `target_paths` (4 paths to 6). The `-005` "no change to `apply_role_switch`"
  scope line is removed: implementing FR9's atomic full-partition demotion
  requires the transaction component to produce it, per the `-006` finding.

## Scope

In scope:

1. `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` — refine
   `apply_role_switch`. In the `role == "prime-builder"` branch, every
   non-target recorded harness is written to `["loyal-opposition"]`
   unconditionally, so the transaction produces FR9's full role partition
   atomically. The `role == "loyal-opposition"` branch and the
   `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` transaction discipline
   (validators first, then audit-trail record, then atomic role-map write,
   then derived-topology write) are unchanged.
2. `groundtruth-kb/src/groundtruth_kb/cli.py` — replace the guarded
   `gt harness set-role` stub with an operational command. It takes `--harness`
   (required, the durable harness id of the promotion target) and `--reason`.
   The body resolves config, opens the DB, and enforces the FR9 active-harness
   eligibility gate via `KnowledgeDB.get_harness` (fails closed if the harness
   is absent or its `status` is not `active`). On a passing gate it calls
   `apply_role_switch(project_root, harness, "prime-builder", change_reason=...)`,
   then `verify_role_partition(project_root)`, and echoes the result. The
   stub's vestigial `--role` option is removed (see Requirement Sufficiency
   note 1).
3. `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py` — a new module
   providing `prime_builder_ids`, `verify_role_partition`, and a
   `RolePartitionViolation` error. `verify_role_partition` loads
   `harness-state/role-assignments.json` and raises unless the role map is a
   valid FR9 partition: exactly one harness holds a `prime-builder`-class role,
   and every other harness's role set is exactly `["loyal-opposition"]`. The
   module imports only the standard library.
4. Spec-derived tests: a new
   `platform_tests/groundtruth_kb/test_mode_switch_invariants.py` for the
   invariant module; a new full-partition regression test added to
   `platform_tests/groundtruth_kb/test_mode_switch_transaction.py`; and an
   update to `platform_tests/groundtruth_kb/cli/test_harness_cli.py` replacing
   the WI-3340 guarded-stub test with operational `set-role` tests.

Out of scope:

- FR7 — the `reviewer_precedence` primary/fallback counterpart-selection model.
  WI-3341 Slice B, a separate thread.
- FR8 — `invocation_surfaces`-driven cross-harness dispatch. WI-3344.
- The WI-3342 Slice B reader migration — cutting the legacy `harness-state`
  JSON readers over to the generated projection and retiring the JSON.
  `set-role` reads the `harnesses` table for *eligibility* but continues to
  write the *role assignment* through `apply_role_switch` to
  `harness-state/role-assignments.json`; that file remains the authoritative
  role-map substrate until Slice B. See the Substrate Model section.
- The `apply_role_switch` `role == "loyal-opposition"` branch. Its symmetric
  behavior is a pre-existing concern; `gt harness set-role` never invokes it
  (it always promotes to `prime-builder`), so it is neither exercised nor
  changed here.
- Deprecating `gt mode set-role`. It is left operational and undeprecated.
- No change to `harness_ops.py`, `scripts/harness_roles.py`, the `harnesses`
  table schema, `KnowledgeDB.insert_harness` / `get_harness`, the lifecycle
  FSM, the projection generator, the mode-switch validators, or the
  mode-switch audit-record writer.

## Substrate Model

`gt harness set-role` consults two substrates, each authoritative for a
different concern:

- The DB-backed `harnesses` registry table (`groundtruth.db`), seeded by
  WI-3342 Slice A (VERIFIED at `bridge/gtkb-harness-registry-seed-004.md`), is
  authoritative for harness *lifecycle status*. `set-role` reads it via
  `KnowledgeDB.get_harness` to enforce FR9's "active harness" eligibility
  precondition.
- `harness-state/role-assignments.json` remains authoritative for the *role
  map* that `apply_role_switch` reads and writes. The WI-3342 Slice A seed
  thread explicitly preserved this: that slice populated the table but did not
  flip role authority.

For the current live state the two substrates are coherent: harnesses `A` and
`B` are present in both, both at `status = active`. The eligibility gate is an
additional precondition layered ahead of `apply_role_switch`; it does not
replace `apply_role_switch`'s own role-map resolution and validator chain. A
harness absent from the role map still fails closed inside `apply_role_switch`
(`TransactionValidationError`, surfaced as a non-zero CLI exit). Fully unifying
the two substrates — making the `harnesses` table the role-write authority and
retiring the legacy JSON — is the WI-3342 Slice B reader migration, not this
slice.

## In-Root Placement Evidence

All six target paths are within the GT-KB project root `E:\GT-KB`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\mode_switch\invariants.py`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\mode_switch\transaction.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\cli\test_harness_cli.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\test_mode_switch_invariants.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\test_mode_switch_transaction.py`

No `applications/` paths and no paths outside the platform root; this bridge
file resides under `E:\GT-KB\bridge\`. All output paths are declared in-root,
compliant with the in-root placement constraint of
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — governing requirement. FR9 (v2) specifies full
  role portability and the single-prime-builder invariant: each active harness
  is eligible for either operating role; `gt harness set-role` may assign
  `prime-builder` to any active harness at any time, atomically demoting every
  other harness to `loyal-opposition` within the same transaction; and the
  mechanism enforces the invariant that exactly one harness holds
  `prime-builder` and every other active harness holds `loyal-opposition` — the
  full role partition. FR3 is the `gt harness` command group that hosts the
  verb. FR6 requires that no logic hard-codes a two-harness assumption.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — the verified governance specification
  ("Prime Builder and Loyal Opposition are portable harness-assigned roles")
  establishing that the operating roles are portable harness assignments, not
  fixed model or vendor identities. `gt harness set-role` reassigns those roles
  between durable harness ids; this proposal preserves that contract — the
  command resolves and assigns by harness id, and no code path branches on
  `harness_type`.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the harness role-set model
  (`role-assignments.json` wire form, the `{prime-builder, loyal-opposition}`
  role set) this command operates within.
- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — the specification governing the
  `mode_switch` transaction component (`apply_role_switch`). This proposal
  modifies `apply_role_switch`'s `prime-builder`-branch role-set computation;
  the change stays within the spec's transaction discipline — validators run
  first, the audit-trail record is written, then the role map is written
  atomically — and refines only which non-target role sets the atomic write
  carries, to satisfy `REQ-HARNESS-REGISTRY-001` FR9's full-partition
  requirement.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  derives tests from FR9's eligibility gate, full role partition, and
  invariant, from FR6's arbitrary-harness-count requirement, and from the
  `GOV-HARNESS-ROLE-PORTABILITY-001` portable-role contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the file bridge is the canonical workflow
  state; this proposal is filed as a REVISED bridge entry.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all six target paths are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; the command, the invariant
  module, and the transaction refinement are governed deterministic artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the new module follows the
  established focused-module pattern.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the proposal lifecycle is
  NEW then NO-GO then REVISED then GO/NO-GO then VERIFIED.

## Prior Deliberations

- `DELIB-2080` — "Antigravity Integration amendment — full role portability
  with single prime-builder invariant." The direct governing deliberation for
  FR9: exactly one prime-builder, freely reassignable, every other harness
  `loyal-opposition` ("Single PB, freely reassignable").
- `DELIB-2079` — "Antigravity Integration project design — 3-harness model,
  DB-backed harness registry, gt harness CLI FSM." The parent design decision
  from which `REQ-HARNESS-REGISTRY-001` derives.
- `DELIB-0831` — "Owner decision: Prime Builder and Loyal Opposition are
  portable harness-assigned roles" (`outcome=owner_decision`). The
  owner-decision source for the verified governance spec
  `GOV-HARNESS-ROLE-PORTABILITY-001`.
- `bridge/gtkb-harness-role-portability-fr9-006.md` — the Loyal Opposition
  NO-GO on REVISED-2 this REVISED-3 responds to (finding F1: the full role
  partition must be a transaction/postcondition, not only a test name).
- `bridge/gtkb-harness-role-portability-fr9-004.md` — the NO-GO on REVISED-1
  (missing `GOV-HARNESS-ROLE-PORTABILITY-001` linkage), resolved by REVISED-2
  and carried forward.
- `bridge/gtkb-harness-role-portability-fr9-002.md` — the earliest NO-GO
  (findings F1 and F2), resolved by REVISED-1 and carried forward.
- `bridge/gtkb-harness-registry-seed-004.md` — the VERIFIED WI-3342 Slice A
  seed thread that populated the `harnesses` table, making the active-harness
  eligibility gate implementable.
- `DECISION-0649` (owner AskUserQuestion, recorded by the owner-decision-tracker)
  — the owner deferred the operational `gt harness set-role` from WI-3340 to
  WI-3341.
- WI-3340 bridge thread `gtkb-harness-cli-command-group` (Codex VERIFIED at
  `-008`) — registered `gt harness set-role` as a guarded stub.
- Sibling VERIFIED threads `gtkb-harness-registry-table-schema` (WI-3337),
  `gtkb-harness-registry-hot-path-projection` (WI-3338),
  `gtkb-harness-lifecycle-fsm` (WI-3339).
- A pre-revision deliberation search re-confirmed `DELIB-2079`, `DELIB-2080`,
  and `DELIB-0831` govern this work; no conflicting prior deliberation was
  found.

## Owner Decisions / Input

This proposal implements owner-decided work and depends on owner approval
recorded as:

- `DELIB-2079` (`outcome=owner_decision`) — owner approved the Antigravity
  Integration design.
- `DELIB-2080` (`outcome=owner_decision`) — owner approved the role-portability
  amendment that became FR9.
- `DELIB-0831` (`outcome=owner_decision`) — owner decision that Prime Builder
  and Loyal Opposition are portable harness-assigned roles; the governing owner
  decision behind `GOV-HARNESS-ROLE-PORTABILITY-001`.
- Owner AskUserQuestion of 2026-05-16 (`DECISION-0649`, `set-role` scope) — the
  owner deferred the operational `gt harness set-role` from WI-3340 to WI-3341.
- Owner AskUserQuestion of 2026-05-16 ("Seed the harnesses table first") — the
  owner pulled WI-3342 Slice A ahead of WI-3341 so `set-role` could enforce
  active-harness eligibility against the authoritative table.
- `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization for `PROJECT-HARNESS-REGISTRY-REFACTOR`,
  covering WI-3337 through WI-3344. The `-006` NO-GO confirmed the
  transaction-component change is revisable within this existing
  authorization; no new owner authorization is required.

The project authorization is owner-approval evidence for the bounded project
work; it does not replace this proposal's Loyal Opposition review or the GO
gate.

## Requirement Sufficiency

Existing requirements sufficient. FR9 (v2) fully specifies the role-portability
property, the active-harness eligibility precondition, and the full role
partition. Three interpretation notes are recorded transparently.

Interpretation note 1 — `set-role` is a promote-to-prime-builder operation.
FR9 describes `gt harness set-role` as assigning `prime-builder` to an active
harness and atomically demoting every other harness to `loyal-opposition`. The
command takes `--harness` and no `--role`, because `prime-builder` is the only
role `set-role` assigns and `loyal-opposition` is the structural consequence
for every other harness. `gt mode set-role`, which retains its `--role` option,
is unchanged. Carried unchanged from `-001`; no NO-GO contested it.

Interpretation note 2 — eligibility substrate. FR9 says "each active harness is
eligible for either operating role." `active` is a `harnesses`-table lifecycle
status (FR2). With WI-3342 Slice A VERIFIED, the `harnesses` table is seeded
and authoritative for lifecycle status, so `set-role` enforces the eligibility
gate directly against it. The broader substrate unification is WI-3342 Slice B.
Carried from REVISED-1.

Interpretation note 3 — full role partition (added at REVISED-3). FR9 requires
more than "exactly one `prime-builder`": it requires that `set-role` "atomically
demote every other harness to `loyal-opposition`" and enforces the invariant
that "every other active harness holds `loyal-opposition`." REVISED-1/-2 relied
on `apply_role_switch`'s prior demotion logic, which rewrites a non-target only
when it already holds the requested role; a non-target with an empty role set
would not be normalized. That is an implementation gap against FR9, not a
requirements gap — FR9 already required the full partition. REVISED-3 refines
`apply_role_switch` to produce the full partition and upgrades the postcondition
to verify it. No new or revised requirement is needed.

## Implementation Plan

### 1. `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` — full-partition demotion

Refine `apply_role_switch`. In the loop over non-target harness records, when
the requested `role` is `"prime-builder"`, set each non-target recorded
harness's `role` to `["loyal-opposition"]` unconditionally — replacing the
prior behavior that rewrote a non-target only when `role` was already present
in its role set. The `role == "loyal-opposition"` branch keeps its existing
conditional behavior and is not changed. The validator chain, the audit-trail
record written before the role-map write, the atomic role-map write, and the
derived-topology write are all unchanged; only the non-target role-set values
carried into the atomic write change. This makes the transaction produce FR9's
full role partition — one `prime-builder`, every other harness
`loyal-opposition` — atomically, satisfying
`SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`'s single-transaction-boundary
requirement.

### 2. New module `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py`

Role-map partition checks for the operating-mode subsystem. Imports only the
standard library; reads `harness-state/role-assignments.json`.

- `RolePartitionViolation(RuntimeError)` — raised when the role map is not a
  valid FR9 partition. Carries an operator-facing message naming the offending
  condition (wrong `prime-builder` count, or a non-target harness whose role
  set is not `["loyal-opposition"]`) and the harness ids involved.
- `prime_builder_ids(role_document)` — returns the sorted list of harness ids
  whose role set (list-or-legacy-scalar wire form) contains `prime-builder` or
  the READ-compatible `acting-prime-builder` provenance token.
- `verify_role_partition(project_root, *, role_path=None)` — loads the role
  document and raises `RolePartitionViolation` unless (a) exactly one harness
  is in `prime_builder_ids`, and (b) every other harness's role set is exactly
  `["loyal-opposition"]`. Returns the single `prime-builder` harness id on
  success.

### 3. `groundtruth-kb/src/groundtruth_kb/cli.py` — operational `gt harness set-role`

Replace the guarded `harness set-role` command body. New definition:
`--harness` (required) and `--reason` (defaulted), with `@click.pass_context`.
`--harness` is the durable harness id, consistent with the other `gt harness`
verbs. Neither the eligibility gate nor `apply_role_switch` inspects
`harness_type`; role assignment attaches to the durable harness id, preserving
`GOV-HARNESS-ROLE-PORTABILITY-001`. The body:

1. Resolves config via `_resolve_config(ctx)` and opens the DB via
   `_open_db(config)`, exactly as the sibling `gt harness show` command does.
2. Enforces the FR9 active-harness eligibility gate: `record =
   db.get_harness(harness_id)`. If `record is None`, raise
   `click.ClickException` ("unknown harness ...; no such harness in the
   registry"). If `record["status"]` is not `"active"`, raise
   `click.ClickException` naming the actual status and pointing the operator at
   `gt harness activate` / `gt harness resume`.
3. Calls `apply_role_switch(project_root, harness_id, "prime-builder",
   change_reason=reason)`, re-raising `TransactionValidationError` as
   `click.ClickException`.
4. Calls `verify_role_partition(project_root)`, re-raising
   `RolePartitionViolation` as `click.ClickException`.
5. Echoes a JSON result carrying the harness id, the new and previous role
   sets, the derived topology, the audit-record path, and the verified single
   `prime-builder` id.

The eligibility gate runs before `apply_role_switch`, so a non-active target
fails closed before any audit record or role-map write. The vestigial `--role`
option on the stub is removed. No other `gt harness` verb and no part of the
`gt mode` group is changed.

### 4. Tests

A new `platform_tests/groundtruth_kb/test_mode_switch_invariants.py`; a new
full-partition regression test in
`platform_tests/groundtruth_kb/test_mode_switch_transaction.py`; and an update
to `platform_tests/groundtruth_kb/cli/test_harness_cli.py` per the Spec-to-Test
Mapping. The CLI tests add a helper that seeds
`harness-state/role-assignments.json` and a minimal `bridge/INDEX.md`,
mirroring `test_mode_switch_transaction.py`'s `_seed_workspace`, so
`apply_role_switch`'s validator chain is satisfied; harness registry rows are
created through the existing `gt harness register` and `gt harness activate`
CLI verbs.

## Spec-to-Test Mapping

`REQ-HARNESS-REGISTRY-001` FR9 (operational `set-role`, active-harness
eligibility, atomic full-partition demotion, the single-prime-builder
invariant), FR6 (arbitrary harness count), and the
`GOV-HARNESS-ROLE-PORTABILITY-001` portable-role governance contract are
verified as follows.

| Specification clause | Covering tests |
|---|---|
| FR9 — `apply_role_switch` produces the full partition (every non-target to `loyal-opposition`, including an empty-role non-target) | `test_apply_role_switch_prime_builder_demotes_all_non_targets` |
| FR9 — single-prime-builder invariant verified as a full partition | `test_verify_role_partition_accepts_valid_partition`, `test_verify_role_partition_rejects_zero_prime_builder`, `test_verify_role_partition_rejects_multiple_prime_builder`, `test_verify_role_partition_rejects_non_target_without_loyal_opposition` |
| FR9 — legacy scalar role wire form counted | `test_prime_builder_ids_handles_legacy_scalar_role`, `test_prime_builder_ids_single` |
| FR9 — `set-role` promotes target, demotes others | `test_harness_set_role_promotes_and_demotes`, `test_harness_set_role_emits_single_prime_builder` |
| FR9 — role portability, no static binding | `test_harness_set_role_reassigns_prime_builder` |
| FR9 — active-harness eligibility gate | `test_harness_set_role_rejects_non_active_harness`, `test_harness_set_role_unknown_harness_rejected` |
| FR9 + FR6 — atomic demotion of every other harness, no two-harness assumption | `test_harness_set_role_three_harness_demotes_all_non_targets` |
| `GOV-HARNESS-ROLE-PORTABILITY-001` — roles are portable harness-assigned, not model/vendor-bound | `test_harness_set_role_reassigns_prime_builder`, `test_harness_set_role_three_harness_demotes_all_non_targets` |

Transaction-component test — `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` (new test added):

- `test_apply_role_switch_prime_builder_demotes_all_non_targets` — a
  three-harness role map seeds the target as `loyal-opposition`, one non-target
  as `prime-builder`, and one non-target with an empty role set (`role: []`).
  After `apply_role_switch(role="prime-builder")` the target holds
  `["prime-builder"]` and BOTH non-targets — including the formerly empty one —
  hold `["loyal-opposition"]`. This is the direct `-006` F1 regression.

Invariant-module tests — `platform_tests/groundtruth_kb/test_mode_switch_invariants.py` (new):

- `test_prime_builder_ids_single` — a one-`prime-builder` role map yields a
  one-element list.
- `test_prime_builder_ids_handles_legacy_scalar_role` — a legacy scalar
  `"role": "prime-builder"` record is counted.
- `test_verify_role_partition_accepts_valid_partition` — one `prime-builder`,
  every other harness `["loyal-opposition"]`: returns the `prime-builder` id
  without raising.
- `test_verify_role_partition_rejects_zero_prime_builder` — a role map with no
  `prime-builder` raises `RolePartitionViolation`.
- `test_verify_role_partition_rejects_multiple_prime_builder` — a role map with
  two `prime-builder` harnesses raises `RolePartitionViolation`; the message
  names both ids.
- `test_verify_role_partition_rejects_non_target_without_loyal_opposition` — a
  role map with exactly one `prime-builder` but a non-target whose role set is
  `[]` raises `RolePartitionViolation`. This proves the postcondition catches
  the `-006` F1 gap that a count-only check missed.

CLI tests — `platform_tests/groundtruth_kb/cli/test_harness_cli.py` (updated):

- `test_harness_set_role_promotes_and_demotes` — against a two-harness registry
  and role map, `gt harness set-role --harness B` sets B to `prime-builder` and
  the other harness to `loyal-opposition`; the role map is a valid partition
  after.
- `test_harness_set_role_reassigns_prime_builder` — the two harnesses are
  registered with distinct `harness_type` values; promoting the harness that
  was previously `loyal-opposition` moves `prime-builder` to it and demotes the
  former `prime-builder`. The test asserts the role moves by durable harness id
  irrespective of `harness_type`, proving `GOV-HARNESS-ROLE-PORTABILITY-001`'s
  contract and that no `set-role` code path branches on `harness_type`.
- `test_harness_set_role_three_harness_demotes_all_non_targets` — registers and
  activates harnesses `A`, `B`, `C`, each with a distinct `harness_type`, and
  seeds a three-harness role map in which one non-target has an empty role set
  (`role: []`); `gt harness set-role --harness C` makes `C` the sole
  `prime-builder` and demotes BOTH `A` and `B` (including the empty-role
  non-target) to `loyal-opposition`. Proves the plural "every other harness"
  demotion through the CLI path, the FR6 no-two-harness-assumption requirement,
  the `-006` F1 full-partition fix end to end, and — because the harnesses
  carry distinct types — harness-type independence.
- `test_harness_set_role_rejects_non_active_harness` — a harness in the
  registry at `status = registered`, and one at `status = suspended`, are each
  rejected by `gt harness set-role` with a non-zero exit and a clear message;
  `harness-state/role-assignments.json` is byte-identical before and after,
  proving the eligibility gate fails closed before any role-map write. The
  gate's `status != "active"` predicate equally rejects a `retired` harness.
- `test_harness_set_role_unknown_harness_rejected` — an unknown `--harness`
  (absent from the registry) exits non-zero with a clear message.
- `test_harness_set_role_emits_single_prime_builder` — the command output
  reports the verified single `prime-builder` id.
- `test_gt_mode_set_role_command_unaffected` — retained from the WI-3340 suite;
  `gt mode set-role` is unchanged.
- The WI-3340 test `test_harness_set_role_is_guarded_and_mutates_nothing` is
  removed: it asserted the guarded-stub behavior WI-3340's own proposal
  declared temporary and "delivered by WI-3341." The operational tests above
  provide strictly greater coverage of the same verb.

## Risks

- **Modifying the verified `apply_role_switch` transaction component.**
  *Mitigation:* the change is confined to the `role == "prime-builder"`
  branch's non-target role-set computation; the
  `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` transaction discipline
  (validators first, audit record, atomic write, derived topology) is
  unchanged. Existing `test_mode_switch_transaction.py` cases remain valid: the
  two-harness demotion test's non-target already held `prime-builder`, so its
  post-state is unchanged; the `loyal-opposition`-branch tests do not touch the
  modified branch. The new regression test pins the new behavior. `gt mode
  set-role --role prime-builder` gains the same full-partition demotion, which
  strengthens — does not regress — the single-prime-builder invariant.
- **`set-role` promote-to-prime-builder interpretation (note 1).**
  *Mitigation:* documented; the FR9-faithful reading; no NO-GO contested it.
- **Two-substrate model — `harnesses` table for eligibility,
  `role-assignments.json` for the role write.** *Mitigation:* documented in the
  Substrate Model section; both substrates are coherent for the live state;
  full unification is the separately-scoped WI-3342 Slice B.
- **`apply_role_switch` `role == "loyal-opposition"` branch.** Its symmetric
  behavior is pre-existing and unchanged; `gt harness set-role` never invokes
  it. Out of scope, neither exercised nor worsened here.
- **Removing the WI-3340 guarded-stub test.** *Mitigation:* the removed test
  asserted an explicitly temporary behavior; the operational tests provide
  strictly greater coverage of the same verb.

## Rollback

Revert the `role == "prime-builder"` branch of `apply_role_switch` in
`transaction.py` to its prior conditional form and remove the new
`test_mode_switch_transaction.py` test; remove
`groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py` and
`platform_tests/groundtruth_kb/test_mode_switch_invariants.py`; revert the
`harness set-role` command body in `cli.py` to the guarded stub and restore the
WI-3340 guarded-stub test in `test_harness_cli.py`. No schema, data, or
migration is involved; the `harnesses` table is read, never written, by this
slice.

## Verification Procedure

Run, from the project root:

- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_invariants.py -q`
- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py -q`
- `python -m pytest platform_tests/groundtruth_kb/cli/test_harness_cli.py -q`
- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/test_mode_switch_validation.py -q`
  (regression — the mode-switch validators and pending-queue paths consume
  `apply_role_switch` unchanged)
- `python -m pytest groundtruth-kb/tests/test_harness_ops.py -q`
  (regression — the WI-3340 harness operations module is untouched)
- `python -m ruff check` on the changed files.

Expected: all new and updated tests pass and the regression suites remain
green. Observed counts are recorded in the post-implementation report.

## Acceptance Criteria

- `gt harness set-role --harness X` promotes X to `prime-builder` and demotes
  every other recorded harness to `loyal-opposition` — including a non-target
  that previously held an empty or non-`loyal-opposition` role set — via the
  `apply_role_switch` transaction component, within a single transaction.
- `gt harness set-role` rejects a target absent from the `harnesses` registry
  or whose `status` is not `active`, with a clear message and a non-zero exit;
  `harness-state/role-assignments.json` is not mutated when the eligibility
  gate fails.
- After the switch, the role map is a valid FR9 partition — exactly one
  `prime-builder`, every other harness exactly `["loyal-opposition"]`;
  `verify_role_partition` confirms it and the command reports the
  `prime-builder` id.
- `verify_role_partition` raises `RolePartitionViolation` for a
  zero-`prime-builder` role map, a multiple-`prime-builder` role map, and a
  role map with one `prime-builder` but a non-target that is not
  `["loyal-opposition"]`.
- Promoting a harness that was previously `loyal-opposition` reassigns
  `prime-builder` to it — role portability with no static binding.
- Role assignment attaches to the durable harness id; no `gt harness set-role`
  code path branches on `harness_type`, preserving
  `GOV-HARNESS-ROLE-PORTABILITY-001`.
- With three registered, active harnesses, promoting one makes it the sole
  `prime-builder` and demotes both others to `loyal-opposition`.
- An unknown `--harness` fails with a clear message.
- `gt mode set-role` and every other `gt harness` verb behave correctly; the
  `apply_role_switch` `loyal-opposition` branch, validator chain, and
  audit-record writer are unchanged.
- All spec-derived tests pass; the `test_mode_switch_pending`,
  `test_mode_switch_validation`, and `test_harness_ops` regression suites
  remain green.
- No change to `harness_ops.py`, `scripts/harness_roles.py`, the `harnesses`
  table, the FSM, or the projection generator.

## Bridge Protocol Compliance

This proposal is filed as `bridge/gtkb-harness-role-portability-fr9-007.md`, a
REVISED version responding to the NO-GO at `-006`, with a `REVISED` line
inserted at the top of this entry's version list in `bridge/INDEX.md` per the
file-bridge protocol. The full version chain (`-001` NEW, `-002` NO-GO, `-003`
REVISED, `-004` NO-GO, `-005` REVISED, `-006` NO-GO, `-007` REVISED) is
preserved; no prior bridge version is deleted or rewritten. `bridge/INDEX.md`
remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`. The
mandatory applicability and clause preflights are run after the INDEX entry
exists; their results are recorded in the review verdict.

## Clause Scope Clarification

This proposal is not a bulk operation. It modifies two source modules, adds one
source module, adds or updates three test files, and implements one slice of
one work item (`WI-3341`); it does not inventory, batch-mutate, promote,
retire, or sweep multiple artifacts. The `GOV-STANDING-BACKLOG-001`
bulk-operations visibility clause therefore does not substantively apply. Owner
approval for the bounded project work is recorded via `DELIB-2079` /
`DELIB-2080` and the active project authorization
`PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
