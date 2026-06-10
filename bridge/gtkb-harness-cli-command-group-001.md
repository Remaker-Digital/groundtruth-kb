# Implementation Proposal — gt harness CLI Command Group (WI-3340)

bridge_kind: prime_proposal
Version: 001 (NEW)

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_ops.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_harness_ops.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py"]

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3340

## Summary

Add the unified `gt harness` CLI command group implementing
`REQ-HARNESS-REGISTRY-001` FR3 — nine verbs:
`register` / `activate` / `suspend` / `resume` / `retire` / `set-role` /
`set-precedence` / `list` / `show`.

A new pure-DB module `groundtruth-kb/src/groundtruth_kb/harness_ops.py` holds the
harness-table transaction operations (registration, lifecycle transition,
precedence change). Each table-mutating operation follows the verified
transaction discipline — validate first, then an atomic append-only write whose
`changed_by` / `changed_at` / `change_reason` columns are the audit trail. The
new `@main.group("harness")` in `cli.py` wraps those operations, the read
accessors (`list` / `show`), and — for `set-role` — the existing verified
`mode_switch` transaction component (`apply_role_switch`). After every
table-mutating verb the CLI regenerates the FR5 hot-path projection so it never
goes stale.

`gt mode set-role` becomes a deprecated alias: it keeps working, emits a
deprecation notice, and delegates to `gt harness set-role`.

This is work item WI-3340 (A4) of the `PROJECT-HARNESS-REGISTRY-REFACTOR`
sub-project. It consumes the WI-3337 `harnesses` table + accessors (VERIFIED),
the WI-3338 projection generator (VERIFIED), and the WI-3339 lifecycle FSM
(VERIFIED).

## Scope

In scope:

1. A new module `groundtruth-kb/src/groundtruth_kb/harness_ops.py` providing:
   `HarnessOperationError`; `register_harness`; `transition_harness` (FSM-validated
   status change, with the owner-decided auto-suspend behavior for retiring an
   active harness); `set_harness_precedence`; and an internal version-append
   helper that carries every FR1 content field forward across a mutation.
2. A new `@main.group("harness")` command group in `cli.py` with the nine FR3
   verbs. Each table-mutating verb regenerates the FR5 projection via the
   WI-3338 generator after a successful write.
3. `gt mode set-role` converted to a deprecated alias that emits a deprecation
   notice and delegates to `gt harness set-role` (no behavior change beyond the
   notice; the command keeps working).
4. Spec-derived tests: `groundtruth-kb/tests/test_harness_ops.py` (module) and
   `platform_tests/groundtruth_kb/cli/test_harness_cli.py` (CLI).

Out of scope:

- FR9 — the single-prime-builder invariant and active-harness role-eligibility
  enforcement. WI-3340's `set-role` wraps `apply_role_switch` exactly as it is
  today (that component already demotes the other harnesses to the opposite
  singleton role). The explicit invariant-enforcement and verification layer is
  WI-3341.
- FR7 — seeding the `harnesses` table from the legacy `harness-state` JSON and
  migrating the readers. WI-3340 builds the CLI that operates the table; the
  table is currently empty and `gt harness register` is its population path.
  Reconciling the table with `role-assignments.json` is WI-3342.
- The new version of `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (WI-3343) and FR8
  data-driven dispatch (WI-3344).
- Updating the durable operating-role rule to recommend the new canonical
  command spelling. The `gt mode set-role` alias keeps that rule's documented
  command fully functional; a documentation sync is a small follow-on, not part
  of this code work item, and would carry its own narrative-artifact approval.
- No change to the `harnesses` table schema, `KnowledgeDB.insert_harness`, the
  `harness_lifecycle` FSM module, or the `harness_projection` generator. They
  are consumed unchanged.

## In-Root Placement Evidence

All four target paths are within `E:\GT-KB`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\harness_ops.py` — new module.
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py` — modified (new group +
  alias conversion).
- `E:\GT-KB\groundtruth-kb\tests\test_harness_ops.py` — new module tests.
- `E:\GT-KB\platform_tests\groundtruth_kb\cli\test_harness_cli.py` — new CLI tests.

No `applications/` paths; no paths outside the GT-KB platform root. Compliant
with the in-root placement constraint of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — governing requirement. FR3 specifies the
  `gt harness` command group and its nine verbs and states that each mutating
  verb wraps the existing verified `mode_switch` transaction component. FR1 is
  the `harnesses` table the verbs mutate (delivered VERIFIED by WI-3337). FR2 is
  the four-state lifecycle FSM the lifecycle verbs validate against (delivered
  VERIFIED by WI-3339). FR5 is the projection each mutating verb refreshes
  (delivered VERIFIED by WI-3338).
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the harness-registry architecture
  this requirement extends; defines the role-set wire form and the `mode_switch`
  transaction component that this proposal's `set-role` verb reuses unchanged.
- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — the specification governing the
  `mode_switch` transaction component (`apply_role_switch`) that `set-role`
  wraps; its validators-first / audit-trail / atomic-write discipline is the
  pattern the table-mutating verbs also follow.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  derives tests from FR3's verb set and the FR2 transition graph.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the file bridge is the canonical workflow
  state; this proposal is filed as a NEW bridge entry.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all four target paths are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; the CLI group and the ops
  module are governed deterministic artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the new module follows the
  established one-focused-module-per-work-item pattern of WI-3338 and WI-3339.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the proposal lifecycle is
  NEW then GO/NO-GO then VERIFIED per the file-bridge protocol.

## Prior Deliberations

- `DELIB-2079` — the consolidated owner decision for the Antigravity
  Integration design (11-question clarification grill, 2026-05-16).
  `REQ-HARNESS-REGISTRY-001` and its FR3 CLI consolidation derive from this
  decision; Q3 fixed the four-state FSM the lifecycle verbs validate against.
- `DELIB-2080` — the role-portability amendment (FR9). Relevant context only:
  `set-role` is the verb FR9/WI-3341 will constrain with the single-prime-builder
  invariant; WI-3340 wraps the existing `apply_role_switch` without adding that
  invariant.
- Owner AskUserQuestion decision, 2026-05-16 — "how should retiring an active
  harness behave?" The owner selected **Auto-suspend then retire**:
  `gt harness retire` on an active harness internally runs
  `active -> suspended -> retired`; the FSM stays the literal four-edge graph;
  no `REQ-HARNESS-REGISTRY-001` amendment. This decision directly shapes the
  `retire` verb below. It was raised because WI-3339's GO finding F1 forwarded
  the `active -> retired` question into this work item.
- Sibling VERIFIED threads `gtkb-harness-registry-table-schema` (WI-3337),
  `gtkb-harness-registry-hot-path-projection` (WI-3338), and
  `gtkb-harness-lifecycle-fsm` (WI-3339) — the table, projection, and FSM this
  CLI consumes. WI-3339's proposal explicitly named WI-3340 as the consumer that
  wires `validate_transition` into the `activate` / `suspend` / `resume` /
  `retire` verbs.
- A pre-proposal deliberation search (`gt harness CLI command group`,
  `harness registry CLI`) returned only the `DELIB-2079` design record and the
  three sibling threads; no prior deliberation proposed or rejected a
  `gt harness` CLI group, and none is in conflict.

## Owner Decisions / Input

This proposal implements owner-decided work and depends on owner approval
recorded as:

- `DELIB-2079` (`outcome=owner_decision`) — owner approved the Antigravity
  Integration design, including the FR3 consolidation of harness registration,
  lifecycle, role, and precedence operations into one `gt harness` command
  group, via an 11-answer AskUserQuestion grill on 2026-05-16.
- Owner AskUserQuestion of 2026-05-16 — for the `retire` verb the owner selected
  "Auto-suspend then retire": `gt harness retire` against an active harness
  internally performs `active -> suspended -> retired`, the FSM stays the
  literal four-edge graph, and no `REQ-HARNESS-REGISTRY-001` amendment is made.
  WI-3340's `retire` verb implements exactly this. The decision is mechanically
  recorded by the owner-decision-tracker hook (`detected_via: ask_user_question`).
- `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization for `PROJECT-HARNESS-REGISTRY-REFACTOR`,
  covering WI-3337 through WI-3344, owner-decision `DELIB-2079`.

The project authorization is owner-approval evidence for the bounded project
work; it does not replace this proposal's Loyal Opposition review or the GO
gate.

## Requirement Sufficiency

Existing requirements sufficient. `REQ-HARNESS-REGISTRY-001` FR3 enumerates the
nine verbs; FR1, FR2, and FR5 (all VERIFIED) supply the substrate. Two
interpretation notes are recorded transparently for the reviewer.

Interpretation note 1 — FR3 "wraps the existing verified `mode_switch`
transaction component." The `mode_switch` component (`apply_role_switch`, per
`SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`) mutates the role map
(`role-assignments.json`) and is intrinsically a role-switch operation; it has
no code path that mutates a `harnesses`-table `status`. A literal "every verb
calls `apply_role_switch`" reading is therefore not buildable. This proposal
reads FR3 as: (a) the role-mutating verb `set-role` wraps `apply_role_switch`
directly and literally — this is where `gt mode set-role` is re-homed; (b) the
six table-mutating verbs follow the same verified transaction discipline —
validate first, then an atomic audit-bearing write — applied to the FR1
`harnesses` table using the registry-native verified components:
`harness_lifecycle.validate_transition` (WI-3339) as the validator and
`KnowledgeDB.insert_harness` (WI-3337) as the atomic append-only write (its
`changed_by` / `changed_at` / `change_reason` columns are the audit trail; the
append-only table forbids UPDATE/DELETE). This reading composes the
WI-3337/WI-3338/WI-3339 verified primitives exactly as those work items' scope
boundaries anticipated — WI-3339's own proposal named WI-3340 as the consumer
that wires the FSM into the lifecycle verbs. If the owner intends a single
literal transaction component spanning both the role map and the harness table,
that requires generalizing `apply_role_switch` or building a new unified
component — a larger work item and a requirement clarification — and this
proposal's reading should stand unless the owner directs otherwise.

Interpretation note 2 — `activate` vs `resume`. The FR2 graph has two edges into
`active`: `registered -> active` and `suspended -> active`. FR3 lists `activate`
and `resume` as distinct verbs. This proposal maps each verb to exactly one
edge: `activate` performs `registered -> active` and rejects a non-`registered`
harness; `resume` performs `suspended -> active` and rejects a non-`suspended`
harness. Each rejection names the correct sibling verb (an `activate` on a
suspended harness points the operator to `resume`, and vice versa). This keeps
the nine verbs distinct and deterministic. The `retire` verb implements the
owner's AskUserQuestion decision: from `suspended` it performs the single
`suspended -> retired`; from `active` it performs `active -> suspended ->
retired` (two validated appends); from `registered` (never activated, no FSM
retire path) it fails with guidance; from `retired` it reports the harness is
already retired. No `active -> retired` FSM edge is added.

## Implementation Plan

### 1. New module `groundtruth-kb/src/groundtruth_kb/harness_ops.py`

Pure-DB transaction operations over the `harnesses` table. Imports the standard
library, `groundtruth_kb.harness_lifecycle`, and (type-only) the DB; opens no
file and writes no projection — projection refresh is the CLI layer's concern.

- `HarnessOperationError(RuntimeError)` — raised for an operation-level failure
  (unknown harness, duplicate registration, an FSM-invalid transition wrapped
  with verb context, a wrong-source-state verb use).
- An internal `_append_version(db, current_row, *, changed_by, change_reason,
  **overrides)` helper — decodes the JSON-text `role` and `invocation_surfaces`
  columns of `current_row` to native types (the same decode
  `harness_projection.build_projection` performs), applies `overrides`, carries
  every other FR1 content field forward unchanged, and calls
  `db.insert_harness(...)`, which appends version N+1. A unit test asserts every
  FR1 content field survives a transition.
- `register_harness(db, *, id, harness_name, harness_type, role=(),
  reviewer_precedence=None, invocation_surfaces=None, capabilities_ref=None,
  changed_by, change_reason)` — raises `HarnessOperationError` if
  `db.get_harness(id)` already exists; otherwise calls `db.insert_harness(...)`
  with the default `status="registered"`. Returns the new record.
- `transition_harness(db, harness_id, target_status, *, changed_by,
  change_reason, expected_source=None)` — loads the current harness (raises if
  absent); if `expected_source` is set and the current status differs, raises a
  `HarnessOperationError` naming the correct sibling verb; if `target_status` is
  `retired` and the current status is `active`, performs the owner-decided
  two-step `active -> suspended -> retired` (each edge validated, two appends);
  otherwise validates the single edge via `validate_transition` (wrapping its
  `ValueError`) and performs one append. Returns the final record.
- `set_harness_precedence(db, harness_id, reviewer_precedence, *, changed_by,
  change_reason)` — loads the current harness (raises if absent), appends a new
  version with the updated `reviewer_precedence` (precedence is independent of
  the FSM; no transition is validated).

### 2. New `@main.group("harness")` in `cli.py`

Nine commands. The mutating verbs resolve config, open the DB, call the
`harness_ops` function, regenerate the FR5 projection via
`harness_projection.generate_harness_projection(db, project_root)`, and echo a
JSON result; `harness_ops` errors are re-raised as `click.ClickException`. The
read verbs (`list`, `show`) echo JSON from `db.list_harnesses()` /
`db.get_harness(id)`. `register` accepts `--id`, `--name`, `--type`, and
optional `--role` (repeatable; default empty), `--precedence`,
`--capabilities-ref`, `--invocation-surfaces` (a JSON string). The lifecycle
verbs accept `--harness` and `--reason`. `set-precedence` accepts `--harness`
and `--precedence`. `set-role` carries the same options and body as today's
`mode set-role` (`--harness`, `--role`, `--reason`, `--defer-to-next-session`)
and calls `apply_role_switch` / `defer_role_switch`. `changed_by` for the
table appends is the fixed actor string `gt-harness-cli`.

### 3. `gt mode set-role` deprecated alias

The `mode set-role` command body is reduced to: emit a deprecation notice on
stderr (`gt mode set-role is deprecated; use gt harness set-role`) and delegate
to the `harness set-role` callback via `ctx.invoke`, so there is one
implementation. `mode list-pending` and `mode apply-pending` are unchanged.

### 4. Tests

`groundtruth-kb/tests/test_harness_ops.py` and
`platform_tests/groundtruth_kb/cli/test_harness_cli.py` per the Spec-to-Test
Mapping below.

## Spec-to-Test Mapping

`REQ-HARNESS-REGISTRY-001` FR3 (the nine `gt harness` verbs, each mutating verb
wrapping the verified transaction discipline) is verified as follows.

Module tests — `groundtruth-kb/tests/test_harness_ops.py` (uses the `db` fixture):

- `test_register_creates_registered_harness` — FR3 `register`: status
  `registered`, version 1.
- `test_register_rejects_duplicate_id` — re-registering an id raises
  `HarnessOperationError`.
- `test_register_persists_optional_fields` — role, precedence,
  invocation_surfaces, capabilities_ref are stored.
- `test_activate_registered_to_active` — FR3 `activate` / FR2
  `registered -> active`.
- `test_activate_rejects_non_registered` — `activate` on a suspended harness
  raises and the message names `resume`.
- `test_suspend_active_to_suspended` — FR3 `suspend` / FR2 `active -> suspended`.
- `test_resume_suspended_to_active` — FR3 `resume` / FR2 `suspended -> active`.
- `test_resume_rejects_non_suspended` — `resume` on a registered harness raises
  and the message names `activate`.
- `test_retire_suspended_to_retired` — FR3 `retire` from `suspended`, single
  edge.
- `test_retire_active_auto_suspends_then_retires` — FR3 `retire` from `active`:
  final status `retired`, and the version chain contains the intermediate
  `suspended` version (registered v1, active v2, suspended v3, retired v4). This
  verifies the owner's 2026-05-16 AskUserQuestion decision.
- `test_retire_registered_rejected` — `retire` of a never-activated harness
  raises `HarnessOperationError` (no FSM retire path from `registered`).
- `test_transition_unknown_harness_rejected` — transitioning an absent id raises.
- `test_transition_carries_forward_fr1_fields` — name, type, role, precedence,
  invocation_surfaces, capabilities_ref all survive a status transition.
- `test_set_precedence_appends_version_unchanged_status` — precedence change
  appends a new version, updates precedence, leaves `status` unchanged.
- `test_set_precedence_unknown_harness_rejected`.

CLI tests — `platform_tests/groundtruth_kb/cli/test_harness_cli.py` (CliRunner):

- `test_harness_register_cli` — `gt harness register` exits 0; the row is in the
  table; the projection file is written.
- `test_harness_lifecycle_cli` — `register` -> `activate` -> `suspend` ->
  `resume`, then `show`, asserting each status.
- `test_harness_retire_active_cli` — `register` -> `activate` -> `retire`
  through the CLI yields final status `retired` (the auto-suspend path).
- `test_harness_invalid_transition_cli` — an invalid verb use exits non-zero
  with a clear message and no DB write.
- `test_harness_list_and_show_cli` — the read verbs return JSON.
- `test_harness_set_precedence_cli` — `gt harness set-precedence` updates the
  record.
- `test_harness_set_role_defer_cli` — `gt harness set-role
  --defer-to-next-session` writes a pending mode-switch file.
- `test_harness_set_role_immediate_cli` — `gt harness set-role` against a
  prepared role-map / bridge-index / session-state fixture applies the role
  switch via `apply_role_switch`.
- `test_mode_set_role_is_deprecated_alias` — `gt mode set-role` still works and
  emits the deprecation notice.

## Risks

- **FR3 interpretation seam (note 1).** The `wraps the mode_switch transaction
  component` clause is read as set-role-wraps-directly plus
  table-verbs-follow-the-same-discipline. *Mitigation:* documented transparently
  for the reviewer; it is the only buildable reading; a literal single-component
  wrap is a larger work item and a requirement clarification.
- **`activate` / `resume` distinct-verb interpretation (note 2).** *Mitigation:*
  documented; each verb maps to one FR2 edge with a cross-pointing error; a
  different mapping is a one-line change per verb.
- **The `harnesses` table is empty and `set-role` mutates `role-assignments.json`,
  not the table.** Table / role-map reconciliation is intentionally deferred to
  WI-3342 (FR7 phased migration). *Mitigation:* WI-3340 does not claim the table
  is authoritative; the proposal states the boundary explicitly; `set-role`
  behavior is byte-identical to today's `gt mode set-role`.
- **`cli.py` is a large shared file.** *Mitigation:* the change is additive (one
  new `@main.group`) plus a minimal reduction of the `mode set-role` body to a
  warn-and-delegate; no other command is touched.
- **Projection refresh on every mutating verb adds a file write.** *Mitigation:*
  this is FR5's intent (the hot-path projection must track the table); the
  generator is VERIFIED (WI-3338) and idempotent.

## Rollback

Remove `groundtruth-kb/src/groundtruth_kb/harness_ops.py`,
`groundtruth-kb/tests/test_harness_ops.py`, and
`platform_tests/groundtruth_kb/cli/test_harness_cli.py`; revert the `@main.group("harness")`
addition in `cli.py` and restore the original `mode set-role` body. Nothing else
references the new module, so removal is clean. No schema, data, or migration is
involved.

## Verification Procedure

Run, from the project root:

- `python -m pytest groundtruth-kb/tests/test_harness_ops.py -q`
- `python -m pytest platform_tests/groundtruth_kb/cli/test_harness_cli.py -q`
- `python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_harness_lifecycle.py groundtruth-kb/tests/test_harness_projection.py -q`
  (regression — schema, accessors, FSM, and projection generator are consumed
  unchanged)
- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_pending.py -q`
  (regression — `mode set-role` now delegates; the underlying transaction
  component is unchanged)

Expected: all new tests pass and the existing suites remain green. Observed
counts are recorded in the post-implementation report.

## Acceptance Criteria

- The `gt harness` group exposes exactly the nine FR3 verbs.
- Each lifecycle verb performs only its FR2-valid transition; an invalid
  transition, a wrong-source-state verb use, and an unknown harness each fail
  with a clear message and no DB write.
- `gt harness retire` of an active harness yields final status `retired` via an
  intermediate `suspended` version, matching the owner's AskUserQuestion
  decision.
- `register` rejects a duplicate harness id.
- `set-role` applies (or defers) a role switch via the unchanged `mode_switch`
  transaction component.
- `gt mode set-role` still works and emits a deprecation notice.
- Every table-mutating verb refreshes the FR5 projection file.
- All spec-derived tests pass; `test_db.py`, `test_harness_lifecycle.py`,
  `test_harness_projection.py`, and the `mode_switch` suites remain green.
- No change to the `harnesses` table schema, `insert_harness`, the FSM module,
  or the projection generator.

## Bridge Protocol Compliance

This proposal is filed as `bridge/gtkb-harness-cli-command-group-001.md` with a
corresponding `bridge/INDEX.md` entry at `NEW` status, inserted at the top of
the entry list per the file-bridge protocol. No prior bridge version is deleted
or rewritten; `bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`. The mandatory pre-filing applicability and
clause preflights are run after the INDEX entry exists; their results are
recorded in the review verdict.

## Clause Scope Clarification

This proposal is not a bulk operation. It adds one module, one CLI command
group, and two test files, and implements exactly one work item (`WI-3340`); it
does not inventory, batch-mutate, promote, retire, or sweep multiple artifacts.
The `GOV-STANDING-BACKLOG-001` bulk-operations visibility clause therefore does
not substantively apply: no bulk-operation inventory artifact, review packet, or
`DECISION DEFERRED` marker is produced because there is no bulk action to gate.
Owner approval for the bounded project work is recorded via the
formal-artifact-approval-backed `DELIB-2079` and the active project
authorization
`PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
