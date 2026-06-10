# Implementation Proposal — Harness Role Portability and Single-Prime-Builder Invariant (WI-3341 Slice A, FR9) — REVISED-1

bridge_kind: prime_proposal
Version: 003 (REVISED)

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "platform_tests/groundtruth_kb/test_mode_switch_invariants.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py"]

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3341

## Summary

This is REVISED-1 of WI-3341 Slice A, responding to the Loyal Opposition NO-GO
at `bridge/gtkb-harness-role-portability-fr9-002.md`. It implements the
role-assignment half of `REQ-HARNESS-REGISTRY-001` FR9: the operational
`gt harness set-role` command, an active-harness eligibility gate, and the
single-prime-builder invariant.

`gt harness set-role --harness X` promotes harness X to `prime-builder` and
atomically demotes every other harness to `loyal-opposition`, through the
verified `mode_switch` transaction component (`apply_role_switch`). Before the
switch, the command enforces FR9's active-harness eligibility: X must exist in
the DB-backed `harnesses` registry table at `status = active`. This replaces
the guarded placeholder stub WI-3340 registered for the verb. A new
`mode_switch/invariants.py` module provides `verify_single_prime_builder`, the
explicit post-condition check confirming the role map holds exactly one
`prime-builder` after the switch.

The NO-GO's preferred resolution for finding F1 became available when
`gtkb-harness-registry-seed` (WI-3342 Slice A) reached VERIFIED at `-004`: the
`harnesses` table is now seeded with harnesses `A` and `B` at `status = active`,
so `set-role` can gate eligibility against an authoritative registry rather
than against legacy role-map membership.

FR9's other half — the FR7 reviewer-precedence primary/fallback
counterpart-selection model — is WI-3341 Slice B, a separate bridge thread.

## Changes From -001 and NO-GO Findings Addressed

The NO-GO at `-002` raised two P1 blocking findings. Both are resolved here.

- **F1 — the proposal omitted FR9's active-harness eligibility gate.** Resolved
  by the NO-GO's *preferred* path. `gt harness set-role` now reads the
  DB-backed `harnesses` registry table (`KnowledgeDB.get_harness`) and rejects
  any target that is absent from the registry or whose `status` is not
  `active`. The `-001` "out of scope" deferral of the eligibility gate, and the
  interpretation note that treated role-map membership as eligibility, are both
  removed. This is implementable now because `gtkb-harness-registry-seed`
  (WI-3342 Slice A) is VERIFIED — the dependency finding F1 identified.
- **F2 — the test plan did not cover the three-harness / demote-all case.**
  Resolved by adding `test_harness_set_role_three_harness_demotes_all_non_targets`
  (registers and activates harnesses `A`, `B`, `C`; promotes `C`; asserts `C`
  is the sole `prime-builder` and both `A` and `B` are `loyal-opposition`) and
  `test_harness_set_role_rejects_non_active_harness` (a registered or suspended
  harness cannot be promoted; the role map is not mutated). FR6 ("no logic
  hard-codes a two-harness assumption") is added to the Specification Links.

Target paths are unchanged from `-001`. The eligibility gate is implemented
inline in the `gt harness set-role` command body in `cli.py`, mirroring how the
sibling `gt harness show` command reads `KnowledgeDB.get_harness`; no new module
or target path is required.

## Scope

In scope:

1. `groundtruth-kb/src/groundtruth_kb/cli.py` — replace the guarded
   `gt harness set-role` stub with an operational command. It takes `--harness`
   (required, the durable harness id of the promotion target) and `--reason`.
   The body resolves config, opens the DB, and enforces the FR9 active-harness
   eligibility gate: it reads the target harness via `KnowledgeDB.get_harness`
   and fails closed if the harness is absent from the registry or its `status`
   is not `active`. On a passing gate it calls
   `apply_role_switch(project_root, harness, "prime-builder", change_reason=...)`,
   then `verify_single_prime_builder(project_root)`, and echoes the result. The
   stub's vestigial `--role` option is removed (see Requirement Sufficiency
   note 1).
2. `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py` — a new module
   providing `prime_builder_ids`, `verify_single_prime_builder`, and a
   `SinglePrimeBuilderViolation` error. The verify function loads
   `harness-state/role-assignments.json` and raises when the count of
   `prime-builder` harnesses is not exactly one. The module imports only the
   standard library.
3. Spec-derived tests: a new
   `platform_tests/groundtruth_kb/test_mode_switch_invariants.py` for the
   invariant module, and an update to
   `platform_tests/groundtruth_kb/cli/test_harness_cli.py` replacing the WI-3340
   guarded-stub test with operational `set-role` tests, including the
   three-harness demote-all test and the non-active-harness rejection test that
   finding F2 requires.

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
- Deprecating `gt mode set-role`. It is left operational and undeprecated, as
  in WI-3340.
- No change to `apply_role_switch`, `harness_ops.py`, `scripts/harness_roles.py`,
  the `harnesses` table schema, `KnowledgeDB.insert_harness` / `get_harness`,
  the lifecycle FSM, or the projection generator.

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
slice. This slice implements FR9's active-harness role-portability property; it
no longer defers it.

## In-Root Placement Evidence

All four target paths are within the GT-KB project root `E:\GT-KB`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\mode_switch\invariants.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\test_mode_switch_invariants.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\cli\test_harness_cli.py`

No `applications/` paths and no paths outside the platform root; this bridge
file resides under `E:\GT-KB\bridge\`. All output paths are declared in-root,
compliant with the in-root placement constraint of
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — governing requirement. FR9 (v2) specifies full
  role portability and the single-prime-builder invariant: each active harness
  is eligible for either operating role; `gt harness set-role` may assign
  `prime-builder` to any active harness at any time, atomically demoting every
  other harness to `loyal-opposition`; and the role map must never, transiently
  or durably, hold zero or multiple `prime-builder` harnesses. FR3 is the
  `gt harness` command group that hosts the verb (delivered as a guarded stub
  by WI-3340, made operational here). FR6 requires that no logic hard-codes a
  two-harness assumption — exercised by this proposal's three-harness test.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the harness role-set model
  (`role-assignments.json` wire form, the `{prime-builder, loyal-opposition}`
  role set) this command operates within.
- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — the specification governing the
  `mode_switch` transaction component (`apply_role_switch`) that `set-role`
  wraps: validators first, then audit-trail record, then atomic role-map write,
  then derived-topology write.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  derives tests from FR9's eligibility gate and invariant, and from FR6's
  arbitrary-harness-count requirement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the file bridge is the canonical workflow
  state; this proposal is filed as a REVISED bridge entry.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all four target paths are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; the command and the
  invariant module are governed deterministic artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the new module follows the
  established focused-module pattern.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the proposal lifecycle is
  NEW then NO-GO then REVISED then GO/NO-GO then VERIFIED.

## Prior Deliberations

- `DELIB-2080` — "Antigravity Integration amendment — full role portability
  with single prime-builder invariant." The direct governing deliberation for
  FR9: the owner amended the design to require that every registered harness be
  freely re-roleable with exactly one prime-builder held at all times ("Single
  PB, freely reassignable").
- `DELIB-2079` — "Antigravity Integration project design — 3-harness model,
  DB-backed harness registry, gt harness CLI FSM." The parent design decision
  from which `REQ-HARNESS-REGISTRY-001` derives.
- `bridge/gtkb-harness-role-portability-fr9-002.md` — the Loyal Opposition
  NO-GO this REVISED responds to (findings F1 and F2).
- `bridge/gtkb-harness-registry-seed-004.md` — the VERIFIED WI-3342 Slice A
  seed thread that populated the `harnesses` table, making the F1 preferred
  resolution implementable. The seed thread's `-001` proposal and `-003` report
  both identify this WI-3341 Slice A revision as the consumer they unblock.
- `DECISION-0649` (owner AskUserQuestion, recorded by the owner-decision-tracker)
  — the owner deferred the operational `gt harness set-role` from WI-3340 to
  WI-3341. This Slice A is that deliverable.
- WI-3340 bridge thread `gtkb-harness-cli-command-group` (Codex VERIFIED at
  `-008`) — registered `gt harness set-role` as a guarded stub and explicitly
  deferred the operational command to WI-3341.
- Sibling VERIFIED threads `gtkb-harness-registry-table-schema` (WI-3337),
  `gtkb-harness-registry-hot-path-projection` (WI-3338),
  `gtkb-harness-lifecycle-fsm` (WI-3339).
- A pre-revision deliberation search re-confirmed `DELIB-2079` and `DELIB-2080`
  govern this work; no conflicting prior deliberation was found.

## Owner Decisions / Input

This proposal implements owner-decided work and depends on owner approval
recorded as:

- `DELIB-2079` (`outcome=owner_decision`) — owner approved the Antigravity
  Integration design.
- `DELIB-2080` (`outcome=owner_decision`) — owner approved the role-portability
  amendment that became FR9. This Slice A implements FR9's role-assignment
  half.
- Owner AskUserQuestion of 2026-05-16 (`DECISION-0649`, `set-role` scope) — the
  owner deferred the operational `gt harness set-role` from WI-3340 to WI-3341.
- Owner AskUserQuestion of 2026-05-16 ("Seed the harnesses table first") — the
  owner chose to pull WI-3342 Slice A ahead of WI-3341 so `set-role` could
  enforce active-harness eligibility against the authoritative table. That
  decision is the basis for taking the NO-GO's preferred F1 resolution here.
- `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization for `PROJECT-HARNESS-REGISTRY-REFACTOR`,
  covering WI-3337 through WI-3344.

The project authorization is owner-approval evidence for the bounded project
work; it does not replace this proposal's Loyal Opposition review or the GO
gate.

## Requirement Sufficiency

Existing requirements sufficient. FR9 (v2) fully specifies the role-portability
property, the active-harness eligibility precondition, and the
single-prime-builder invariant. Two interpretation notes are recorded
transparently for the reviewer.

Interpretation note 1 — `set-role` is a promote-to-prime-builder operation.
FR9 describes `gt harness set-role` as assigning `prime-builder` to an active
harness and atomically demoting every other harness to `loyal-opposition`; in
the single-prime-builder model a harness becomes `loyal-opposition` solely as
the automatic demotion when another harness is promoted. This proposal
therefore implements `gt harness set-role --harness X` as "promote X to
`prime-builder`" — the command takes `--harness` and no `--role`, because
`prime-builder` is the only role `set-role` assigns and `loyal-opposition` is
the structural consequence for every other harness. The
`verify_single_prime_builder` check is the explicit post-condition enforcement
FR9 calls for. `gt mode set-role`, which retains its `--role` option, is
unchanged and out of scope. This note is carried unchanged from `-001`; the
NO-GO did not contest it.

Interpretation note 2 — eligibility substrate (revised from `-001`). FR9 says
"each active harness is eligible for either operating role." `active` is a
`harnesses`-table lifecycle status (FR2). `-001` deferred the table-`status`
eligibility gate and treated role-map membership as eligibility; the NO-GO's
finding F1 rejected that. With WI-3342 Slice A VERIFIED, the `harnesses` table
is seeded and authoritative for lifecycle status, so this REVISED implements
the eligibility gate directly against the table. The only element still
deferred is the broader substrate unification (making the table the role-write
authority and retiring the legacy JSON), which is the WI-3342 Slice B reader
migration and is genuinely separate from eligibility. This slice implements
FR9's active-harness eligibility property; it does not defer it.

## Implementation Plan

### 1. New module `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py`

Role-map invariant checks for the operating-mode subsystem. Imports only the
standard library; reads `harness-state/role-assignments.json`.

- `SinglePrimeBuilderViolation(RuntimeError)` — raised when the role map does
  not hold exactly one `prime-builder` harness. Carries an operator-facing
  message naming the offending count and the harness ids involved.
- `prime_builder_ids(role_document)` — returns the sorted list of harness ids
  whose role set (list-or-legacy-scalar wire form) contains `prime-builder` or
  the READ-compatible `acting-prime-builder` provenance token.
- `verify_single_prime_builder(project_root, *, role_path=None)` — loads the
  role document, computes `prime_builder_ids`, and raises
  `SinglePrimeBuilderViolation` unless exactly one is present. Returns the
  single `prime-builder` harness id on success.

### 2. `groundtruth-kb/src/groundtruth_kb/cli.py` — operational `gt harness set-role`

Replace the guarded `harness set-role` command body. New definition:
`--harness` (required) and `--reason` (defaulted), with `@click.pass_context`.
`--harness` is the durable harness id, consistent with the other `gt harness`
verbs. The body:

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
4. Calls `verify_single_prime_builder(project_root)`, re-raising
   `SinglePrimeBuilderViolation` as `click.ClickException`.
5. Echoes a JSON result carrying the harness id, the new and previous role
   sets, the derived topology, the audit-record path, and the verified single
   `prime-builder` id.

The eligibility gate runs before `apply_role_switch`, so a non-active target
fails closed before any audit record or role-map write. The vestigial `--role`
option on the stub is removed. No other `gt harness` verb and no part of the
`gt mode` group is changed.

### 3. Tests

`platform_tests/groundtruth_kb/test_mode_switch_invariants.py` (new) and an
update to `platform_tests/groundtruth_kb/cli/test_harness_cli.py` per the
Spec-to-Test Mapping. The CLI tests add a helper that seeds
`harness-state/role-assignments.json` and a minimal `bridge/INDEX.md`,
mirroring `platform_tests/groundtruth_kb/test_mode_switch_transaction.py`'s
`_seed_workspace`, so `apply_role_switch`'s validator chain is satisfied;
harness registry rows are created through the existing `gt harness register`
and `gt harness activate` CLI verbs.

## Spec-to-Test Mapping

`REQ-HARNESS-REGISTRY-001` FR9 (operational `set-role`, active-harness
eligibility, atomic demotion, the single-prime-builder invariant) and FR6
(arbitrary harness count) are verified as follows.

| Specification clause | Covering tests |
|---|---|
| FR9 — single-prime-builder invariant (exactly one) | `test_prime_builder_ids_single`, `test_verify_single_prime_builder_accepts_exactly_one`, `test_verify_single_prime_builder_rejects_zero`, `test_verify_single_prime_builder_rejects_multiple` |
| FR9 — legacy scalar role wire form counted | `test_prime_builder_ids_handles_legacy_scalar_role` |
| FR9 — `set-role` promotes target, demotes others | `test_harness_set_role_promotes_and_demotes`, `test_harness_set_role_emits_single_prime_builder` |
| FR9 — role portability, no static binding | `test_harness_set_role_reassigns_prime_builder` |
| FR9 — active-harness eligibility gate | `test_harness_set_role_rejects_non_active_harness`, `test_harness_set_role_unknown_harness_rejected` |
| FR9 + FR6 — atomic demotion of every other harness, no two-harness assumption | `test_harness_set_role_three_harness_demotes_all_non_targets` |

Invariant-module tests — `platform_tests/groundtruth_kb/test_mode_switch_invariants.py` (new):

- `test_prime_builder_ids_single` — a one-`prime-builder` role map yields a
  one-element list.
- `test_prime_builder_ids_handles_legacy_scalar_role` — a legacy scalar
  `"role": "prime-builder"` record is counted.
- `test_verify_single_prime_builder_accepts_exactly_one` — returns the
  `prime-builder` id without raising.
- `test_verify_single_prime_builder_rejects_zero` — a role map with no
  `prime-builder` raises `SinglePrimeBuilderViolation`.
- `test_verify_single_prime_builder_rejects_multiple` — a role map with two
  `prime-builder` harnesses raises `SinglePrimeBuilderViolation`; the message
  names both ids.

CLI tests — `platform_tests/groundtruth_kb/cli/test_harness_cli.py` (updated):

- `test_harness_set_role_promotes_and_demotes` — against a two-harness registry
  and role map, `gt harness set-role --harness B` sets B to `prime-builder` and
  the other harness to `loyal-opposition`; the role map holds exactly one
  `prime-builder` after.
- `test_harness_set_role_reassigns_prime_builder` — promoting the harness that
  was previously `loyal-opposition` moves `prime-builder` to it and demotes the
  former `prime-builder`, demonstrating role portability with no static
  binding.
- `test_harness_set_role_three_harness_demotes_all_non_targets` — registers and
  activates harnesses `A`, `B`, `C` and seeds a three-harness role map;
  `gt harness set-role --harness C` makes `C` the sole `prime-builder` and
  demotes BOTH `A` and `B` to `loyal-opposition`. This proves the plural "every
  other harness" demotion and the FR6 no-two-harness-assumption requirement
  (finding F2).
- `test_harness_set_role_rejects_non_active_harness` — a harness in the
  registry at `status = registered`, and one at `status = suspended`, are each
  rejected by `gt harness set-role` with a non-zero exit and a clear message;
  `harness-state/role-assignments.json` is byte-identical before and after,
  proving the eligibility gate fails closed before any role-map write
  (findings F1 and F2). The gate's `status != "active"` predicate equally
  rejects a `retired` harness.
- `test_harness_set_role_unknown_harness_rejected` — an unknown `--harness`
  (absent from the registry) exits non-zero with a clear message.
- `test_harness_set_role_emits_single_prime_builder` — the command output
  reports the verified single `prime-builder` id.
- `test_gt_mode_set_role_command_unaffected` — retained from the WI-3340 suite;
  `gt mode set-role` is unchanged.
- The WI-3340 test `test_harness_set_role_is_guarded_and_mutates_nothing` is
  removed: it asserted the guarded-stub behavior WI-3340's own proposal
  declared temporary and "delivered by WI-3341." Replacing it when the
  operational command lands is the planned lifecycle of that test; the
  operational tests above provide strictly greater coverage of the same verb.

## Risks

- **`set-role` promote-to-prime-builder interpretation (note 1).**
  *Mitigation:* documented transparently; it is the FR9-faithful reading; the
  NO-GO did not contest it; if the owner later wants a `--role`-style form it
  is a small additive change.
- **Two-substrate model — `harnesses` table for eligibility,
  `role-assignments.json` for the role write.** *Mitigation:* documented in the
  Substrate Model section; for the live state both substrates are coherent; the
  eligibility gate is an additional fail-closed precondition and does not
  replace `apply_role_switch`'s own role-map resolution; full substrate
  unification is the separately-scoped WI-3342 Slice B.
- **`apply_role_switch` symmetric-demotion behavior for
  `role="loyal-opposition"`.** `apply_role_switch` demotes the harnesses
  holding the *requested* role; Slice A's `set-role` only ever calls it with
  `role="prime-builder"` (target promoted, all others holding `prime-builder`
  demoted), which always yields exactly one `prime-builder`. The pre-existing
  `role="loyal-opposition"` behavior is noted for transparency; it is not
  introduced, exercised, or worsened here.
- **Removing the WI-3340 guarded-stub test.** *Mitigation:* the removed test
  asserted an explicitly temporary behavior; the operational tests provide
  strictly greater coverage of the same verb.

## Rollback

Remove `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py` and
`platform_tests/groundtruth_kb/test_mode_switch_invariants.py`; revert the
`harness set-role` command body in `cli.py` to the guarded stub and restore the
WI-3340 guarded-stub test in `test_harness_cli.py`. Nothing else references the
new module. No schema, data, or migration is involved; the `harnesses` table is
read, never written, by this slice.

## Verification Procedure

Run, from the project root:

- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_invariants.py -q`
- `python -m pytest platform_tests/groundtruth_kb/cli/test_harness_cli.py -q`
- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/test_mode_switch_validation.py -q`
  (regression — `apply_role_switch` and the validators are consumed unchanged)
- `python -m pytest groundtruth-kb/tests/test_harness_ops.py -q`
  (regression — the WI-3340 harness operations module is untouched)
- `python -m ruff check` on the changed files.

Expected: all new and updated tests pass and the regression suites remain
green. Observed counts are recorded in the post-implementation report.

## Acceptance Criteria

- `gt harness set-role --harness X` promotes X to `prime-builder` and demotes
  every other harness to `loyal-opposition`, via the verified `apply_role_switch`
  transaction component.
- `gt harness set-role` rejects a target that is absent from the `harnesses`
  registry or whose `status` is not `active`, with a clear message and a
  non-zero exit; `harness-state/role-assignments.json` is not mutated when the
  eligibility gate fails.
- After the switch, the role map holds exactly one `prime-builder`;
  `verify_single_prime_builder` confirms it and the command reports it.
- `verify_single_prime_builder` raises `SinglePrimeBuilderViolation` for a
  zero-`prime-builder` or multiple-`prime-builder` role map.
- Promoting a harness that was previously `loyal-opposition` reassigns
  `prime-builder` to it — demonstrating role portability with no static
  binding.
- With three registered, active harnesses, promoting one makes it the sole
  `prime-builder` and demotes both others to `loyal-opposition`.
- An unknown `--harness` fails with a clear message.
- `gt mode set-role` and every other `gt harness` verb are unchanged.
- All spec-derived tests pass; the `mode_switch` and `test_harness_ops`
  regression suites remain green.
- No change to `apply_role_switch`, `harness_ops.py`, `scripts/harness_roles.py`,
  the `harnesses` table, the FSM, or the projection generator.

## Bridge Protocol Compliance

This proposal is filed as `bridge/gtkb-harness-role-portability-fr9-003.md`, a
REVISED version responding to the NO-GO at `-002`, with a `REVISED` line
inserted at the top of this entry's version list in `bridge/INDEX.md` per the
file-bridge protocol. The full version chain (`-001` NEW, `-002` NO-GO, `-003`
REVISED) is preserved; no prior bridge version is deleted or rewritten.
`bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`. The mandatory applicability and clause
preflights are run after the INDEX entry exists; their results are recorded in
the review verdict.

## Clause Scope Clarification

This proposal is not a bulk operation. It adds one module, modifies one CLI
command, and adds or updates two test files, implementing one slice of one work
item (`WI-3341`); it does not inventory, batch-mutate, promote, retire, or
sweep multiple artifacts. The `GOV-STANDING-BACKLOG-001` bulk-operations
visibility clause therefore does not substantively apply. Owner approval for
the bounded project work is recorded via `DELIB-2079` / `DELIB-2080` and the
active project authorization
`PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
