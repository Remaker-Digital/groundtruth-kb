# Implementation Proposal — Harness Role Portability and Single-Prime-Builder Invariant (WI-3341 Slice A, FR9)

bridge_kind: prime_implementation_proposal
Version: 001 (NEW)

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "platform_tests/groundtruth_kb/test_mode_switch_invariants.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py"]

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3341

## Summary

This is Slice A of work item WI-3341. It implements the role-assignment half of
`REQ-HARNESS-REGISTRY-001` FR9: the operational `gt harness set-role` command
and the single-prime-builder invariant.

`gt harness set-role --harness X` promotes harness X to `prime-builder` and
atomically demotes every other harness to `loyal-opposition`, through the
verified `mode_switch` transaction component (`apply_role_switch`). This
replaces the guarded placeholder stub WI-3340 registered for the verb. A new
`mode_switch/invariants.py` module provides `verify_single_prime_builder`, an
explicit invariant check confirming the role map holds exactly one
`prime-builder` after the switch.

FR9's role-portability property — every harness is eligible for either role,
no harness is statically bound — holds because `set-role` can target any
harness at any time. FR9's other half, the FR7 reviewer-precedence
primary/fallback counterpart-selection model, is **WI-3341 Slice B**, a
separate bridge thread; FR7 also depends on the `harnesses` table carrying
`reviewer_precedence` data, which the WI-3342 reader migration seeds.

## Scope

In scope:

1. `groundtruth-kb/src/groundtruth_kb/cli.py` — replace the guarded
   `gt harness set-role` stub with an operational command. It takes `--harness`
   (required, the promotion target) and `--reason`, calls
   `apply_role_switch(project_root, harness, "prime-builder", change_reason=...)`,
   then `verify_single_prime_builder(project_root)`, and echoes the result.
2. `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py` — a new module
   providing `prime_builder_ids`, `verify_single_prime_builder`, and a
   `SinglePrimeBuilderViolation` error. The verify function loads
   `harness-state/role-assignments.json` and raises when the count of
   `prime-builder` harnesses is not exactly one.
3. Spec-derived tests: a new `platform_tests/groundtruth_kb/test_mode_switch_invariants.py`
   for the invariant module, and an update to the existing
   `platform_tests/groundtruth_kb/cli/test_harness_cli.py` replacing the
   WI-3340 guarded-stub test with operational `set-role` tests.

Out of scope:

- FR7 — the `reviewer_precedence` primary/fallback counterpart-selection model
  in the cross-harness trigger. This is WI-3341 Slice B (a separate thread).
  FR7's precedence data lives in the `harnesses` table, seeded by WI-3342.
- The harnesses-table `status`-based "active harness" eligibility gate on
  `set-role`. Pre-WI-3342 the table is not the authoritative role substrate;
  `set-role` operates on `role-assignments.json`. See Requirement Sufficiency.
- Deprecating `gt mode set-role`. It is left operational and undeprecated, as
  in WI-3340; re-homing it as an alias is a later documentation-sync concern.
- No change to `apply_role_switch`, `scripts/harness_roles.py`, the `harnesses`
  table, the lifecycle FSM, or the projection generator.

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

- `REQ-HARNESS-REGISTRY-001` — governing requirement. FR9 specifies full role
  portability and the single-prime-builder invariant: `gt harness set-role` may
  assign `prime-builder` to any active harness at any time, atomically demoting
  every other harness, and the role map must never hold zero or multiple
  `prime-builder` harnesses. FR3 is the `gt harness` command group that hosts
  the verb (delivered as a guarded stub by WI-3340, made operational here).
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
  derives tests from FR9's invariant and the `set-role` behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the file bridge is the canonical workflow
  state; this proposal is filed as a NEW bridge entry.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all four target paths are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; the command and the
  invariant module are governed deterministic artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the new module follows
  the established focused-module pattern.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the proposal lifecycle is
  NEW then GO/NO-GO then VERIFIED.

## Prior Deliberations

- `DELIB-2080` — "Antigravity Integration amendment — full role portability
  with single prime-builder invariant." This is the direct governing
  deliberation for FR9: the owner amended the design to require that every
  registered harness be freely re-roleable with exactly one prime-builder held
  at all times.
- `DELIB-2079` — "Antigravity Integration project design — 3-harness model,
  DB-backed harness registry, gt harness CLI FSM." The parent design decision
  from which `REQ-HARNESS-REGISTRY-001` derives.
- WI-3340 bridge thread `gtkb-harness-cli-command-group` (Codex VERIFIED at
  `-008`) — registered `gt harness set-role` as a guarded stub and explicitly
  deferred the operational command to WI-3341 per owner decision
  `DECISION-0649`. This Slice A delivers that deferred command.
- Sibling VERIFIED threads `gtkb-harness-registry-table-schema` (WI-3337),
  `gtkb-harness-registry-hot-path-projection` (WI-3338),
  `gtkb-harness-lifecycle-fsm` (WI-3339).
- A pre-proposal deliberation search confirmed `DELIB-2079` and `DELIB-2080`
  exist and govern this work; no conflicting prior deliberation was found. The
  WI-3340 verdicts independently performed the same search with the same
  result.

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
  This Slice A is that deliverable.
- `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization for `PROJECT-HARNESS-REGISTRY-REFACTOR`,
  covering WI-3337 through WI-3344.

The project authorization is owner-approval evidence for the bounded project
work; it does not replace this proposal's Loyal Opposition review or the GO
gate.

## Requirement Sufficiency

Existing requirements sufficient. FR9 fully specifies the role-portability
property and the single-prime-builder invariant. Two interpretation notes are
recorded transparently for the reviewer.

Interpretation note 1 — `set-role` is a promote-to-prime-builder operation.
FR9 states `gt harness set-role` "may assign `prime-builder` to any active
harness at any time, atomically demoting every other harness to
`loyal-opposition`." It describes the verb only as assigning `prime-builder`;
in the single-prime-builder model a harness becomes `loyal-opposition` solely
as the automatic demotion when another harness is promoted. This proposal
therefore implements `gt harness set-role --harness X` as "promote X to
`prime-builder`" — the command takes `--harness` and no `--role`, because
`prime-builder` is the only role `set-role` assigns and `loyal-opposition` is
the structural consequence for every other harness. This makes the
single-prime-builder invariant structural: `apply_role_switch` with
`role="prime-builder"` sets the target to `prime-builder` and demotes every
other harness, so the operation always yields exactly one `prime-builder`. The
`verify_single_prime_builder` check is the explicit post-condition enforcement
FR9 calls for. `gt mode set-role`, which retains its `--role` option, is left
unchanged and is out of scope.

Interpretation note 2 — migration-window "active harness" eligibility. FR9
says "each active harness is eligible for either operating role." `active` is a
`harnesses`-table lifecycle status (FR2). The `harnesses` table does not become
the authoritative role substrate until the WI-3342 reader migration; until
then the authoritative role substrate is `harness-state/role-assignments.json`.
Slice A's `set-role` therefore operates on `role-assignments.json` through
`apply_role_switch` and treats role-map membership as eligibility; a
table-`status`-based eligibility gate becomes meaningful once WI-3342 makes the
table authoritative, and is out of scope here. This mirrors the documented
migration-window interpretations the reviewer accepted in WI-3339 and WI-3340.

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

Replace the guarded `harness set-role` command body. New definition: `--harness`
(required) and `--reason` (defaulted). The body resolves config, calls
`apply_role_switch(project_root, harness, "prime-builder", change_reason=reason)`
(re-raising `TransactionValidationError` as `click.ClickException`), then calls
`verify_single_prime_builder(project_root)` (re-raising
`SinglePrimeBuilderViolation` as `click.ClickException`), and echoes a JSON
result carrying the harness id, the new and previous role sets, the derived
topology, the audit-record path, and the verified single `prime-builder` id.
No other `gt harness` verb and no part of the `gt mode` group is changed.

### 3. Tests

`platform_tests/groundtruth_kb/test_mode_switch_invariants.py` (new) and an
update to `platform_tests/groundtruth_kb/cli/test_harness_cli.py` per the
Spec-to-Test Mapping.

## Spec-to-Test Mapping

`REQ-HARNESS-REGISTRY-001` FR9 (operational `set-role`, atomic demotion, the
single-prime-builder invariant) is verified as follows.

Invariant-module tests — `platform_tests/groundtruth_kb/test_mode_switch_invariants.py`:

- `test_prime_builder_ids_single` — a one-`prime-builder` role map yields a
  one-element list.
- `test_prime_builder_ids_handles_legacy_scalar_role` — a legacy scalar
  `"role": "prime-builder"` record is counted.
- `test_verify_single_prime_builder_accepts_exactly_one` — returns the
  `prime-builder` id without raising.
- `test_verify_single_prime_builder_rejects_zero` — a role map with no
  `prime-builder` raises `SinglePrimeBuilderViolation`.
- `test_verify_single_prime_builder_rejects_multiple` — a role map with two
  `prime-builder` harnesses raises `SinglePrimeBuilderViolation`, message names
  both ids.

CLI tests — `platform_tests/groundtruth_kb/cli/test_harness_cli.py` (updated):

- `test_harness_set_role_promotes_and_demotes` — `gt harness set-role --harness B`
  against a two-harness role map sets B to `prime-builder` and the other harness
  to `loyal-opposition`; the role map has exactly one `prime-builder` after.
- `test_harness_set_role_reassigns_prime_builder` — promoting the harness that
  was previously `loyal-opposition` moves `prime-builder` to it and demotes the
  former `prime-builder`, demonstrating role portability.
- `test_harness_set_role_unknown_harness_rejected` — an unknown `--harness`
  exits non-zero with a clear message.
- `test_harness_set_role_emits_single_prime_builder` — the command output
  reports the verified single `prime-builder` id.
- The WI-3340 test `test_harness_set_role_is_guarded_and_mutates_nothing` is
  removed: it asserted the guarded-stub behavior WI-3340's own proposal
  declared temporary and "delivered by WI-3341." Replacing it when the
  operational command lands is the planned lifecycle of that test, not an
  unapproved removal of coverage — the operational tests above supersede it.

## Risks

- **`set-role` promote-to-prime-builder interpretation (note 1).** *Mitigation:*
  documented transparently; it is the FR9-faithful reading; if the owner wants
  a `--role`-style form, it is a small additive change.
- **Migration-window eligibility (note 2).** *Mitigation:* documented; mirrors
  the WI-3339/WI-3340 pattern the reviewer accepted; the table-based gate is
  WI-3342-dependent and explicitly out of scope.
- **`apply_role_switch` symmetric-demotion behavior for `role="loyal-opposition"`.**
  `apply_role_switch` demotes/promotes the *opposite* role; with three or more
  harnesses, calling it with `role="loyal-opposition"` can leave multiple
  `prime-builder` harnesses. Slice A's `set-role` only ever calls
  `apply_role_switch` with `role="prime-builder"` (target promoted, all others
  demoted), which always yields exactly one `prime-builder`, so Slice A does
  not exercise that path. The pre-existing behavior is noted for transparency;
  it is not introduced or worsened here and is out of scope.
- **Removing the WI-3340 guarded-stub test.** *Mitigation:* the removed test
  asserted an explicitly temporary behavior; the operational tests provide
  strictly greater coverage of the same verb.

## Rollback

Remove `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py` and
`platform_tests/groundtruth_kb/test_mode_switch_invariants.py`; revert the
`harness set-role` command body in `cli.py` to the guarded stub and restore the
WI-3340 guarded-stub test in `test_harness_cli.py`. Nothing else references the
new module. No schema, data, or migration is involved.

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
- After the switch, the role map holds exactly one `prime-builder`;
  `verify_single_prime_builder` confirms it and the command reports it.
- `verify_single_prime_builder` raises `SinglePrimeBuilderViolation` for a
  zero-`prime-builder` or multiple-`prime-builder` role map.
- Promoting a harness that was previously `loyal-opposition` reassigns
  `prime-builder` to it — demonstrating role portability with no static
  binding.
- An unknown `--harness` fails with a clear message and no role-map mutation
  beyond what `apply_role_switch`'s own validation already guarantees.
- `gt mode set-role` and every other `gt harness` verb are unchanged.
- All spec-derived tests pass; the `mode_switch` and `test_harness_ops`
  regression suites remain green.
- No change to `apply_role_switch`, `scripts/harness_roles.py`, the `harnesses`
  table, the FSM, or the projection generator.

## Bridge Protocol Compliance

This proposal is filed as `bridge/gtkb-harness-role-portability-fr9-001.md` with
a corresponding `bridge/INDEX.md` entry at `NEW` status, inserted at the top of
the entry list per the file-bridge protocol. It is WI-3341 Slice A; Slice B
(FR7) will be a separate thread. No prior bridge version is deleted or
rewritten; `bridge/INDEX.md` remains the canonical workflow state per
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
