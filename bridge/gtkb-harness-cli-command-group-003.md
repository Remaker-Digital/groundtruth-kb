# Implementation Proposal (REVISED) — gt harness CLI Command Group (WI-3340)

bridge_kind: prime_proposal
Version: 003 (REVISED)

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_ops.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_harness_ops.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py"]

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3340

## Summary

Add the unified `gt harness` CLI command group implementing
`REQ-HARNESS-REGISTRY-001` FR3. The group exposes all nine FR3 verbs;
this work item delivers eight of them fully operational against the
DB-backed `harnesses` registry —
`register` / `activate` / `suspend` / `resume` / `retire` /
`set-precedence` / `list` / `show` — and registers the ninth verb,
`set-role`, as an explicitly guarded command.

A new pure-DB module `groundtruth-kb/src/groundtruth_kb/harness_ops.py` holds the
harness-table transaction operations (registration, lifecycle transition,
precedence change). Each table-mutating operation follows the verified
transaction discipline — validate first, then an atomic append-only write whose
`changed_by` / `changed_at` / `change_reason` columns are the audit trail. The
new `@main.group("harness")` in `cli.py` wraps those operations and the read
accessors (`list` / `show`). After every table-mutating verb the CLI
regenerates the FR5 hot-path projection so it never goes stale.

This is work item WI-3340 (A4) of the `PROJECT-HARNESS-REGISTRY-REFACTOR`
sub-project. It consumes the WI-3337 `harnesses` table + accessors (VERIFIED),
the WI-3338 projection generator (VERIFIED), and the WI-3339 lifecycle FSM
(VERIFIED).

## Response to Loyal Opposition NO-GO (gtkb-harness-cli-command-group-002.md)

The `-002` review issued NO-GO on one blocking finding:

- **F1 (P1, blocking)** — the `-001` proposal had `set-role` wrap the
  `mode_switch` component `apply_role_switch`, which mutates
  `harness-state/role-assignments.json` and not the `harnesses` table, leaving
  the DB-authoritative harness row and the FR5 projection stale. That
  contradicts FR3's purpose (converging role assignment onto the registry) and
  risks a SessionStart split-brain during the migration window.

Resolution. F1 is accepted in full. This revision removes the legacy-store
`set-role` implementation entirely. WI-3340 now registers `set-role` as an
explicitly guarded command that performs no mutation and fails closed with
guidance to `gt mode set-role`. The DB-coherent `gt harness set-role` —
atomic demotion of the other harnesses and the single-prime-builder invariant —
is `REQ-HARNESS-REGISTRY-001` FR9, which is the deliverable of WI-3341; its
substrate (the `harnesses` table as the authoritative role store) is delivered
by the WI-3342 reader migration. Deferring `set-role` to WI-3341 was the owner's
explicit decision (AskUserQuestion, 2026-05-16; see Owner Decisions / Input).
`gt mode set-role` is left entirely unchanged and remains the operational role
command; its deprecation moves to the work item where its replacement becomes
coherent. The FR3 acceptance claims are revised so WI-3340 no longer claims all
nine verbs are fully operational, and a spec-derived test proves the guarded
`set-role` mutates nothing — it cannot leave the DB `role` field or the
projection stale.

## Scope

In scope:

1. A new module `groundtruth-kb/src/groundtruth_kb/harness_ops.py` providing:
   `HarnessOperationError`; `register_harness`; `transition_harness` (FSM-validated
   status change, with the owner-decided auto-suspend behavior for retiring an
   active harness); `set_harness_precedence`; and an internal version-append
   helper that carries every FR1 content field forward across a mutation. The
   module contains no role-assignment logic.
2. A new `@main.group("harness")` command group in `cli.py` with the nine FR3
   verbs. Eight are fully operational against the `harnesses` table; each
   table-mutating verb regenerates the FR5 projection via the WI-3338 generator
   after a successful write. The ninth verb, `set-role`, is a guarded command —
   it accepts the eventual `--harness` / `--role` options so its interface is
   discoverable, performs no mutation, and exits non-zero with a message
   directing the operator to `gt mode set-role`.
3. Spec-derived tests: `groundtruth-kb/tests/test_harness_ops.py` (module) and
   `platform_tests/groundtruth_kb/cli/test_harness_cli.py` (CLI), including a
   test proving the guarded `set-role` leaves the DB and the projection
   unchanged.

Out of scope:

- The operational `gt harness set-role` — atomic demotion and the
  single-prime-builder invariant. This is `REQ-HARNESS-REGISTRY-001` FR9, the
  deliverable of WI-3341. WI-3340 only registers the verb as a guarded
  placeholder.
- Deprecating `gt mode set-role`. It is left fully operational and unchanged.
  Its deprecation belongs to WI-3341/WI-3342, where `gt harness set-role`
  becomes the coherent replacement.
- FR7 — seeding the `harnesses` table from the legacy `harness-state` JSON and
  migrating the readers. WI-3340 builds the CLI that operates the table;
  `gt harness register` is the table's population path. Reconciling the table
  with `role-assignments.json` is WI-3342.
- The new version of `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (WI-3343) and FR8
  data-driven dispatch (WI-3344).
- No change to the `harnesses` table schema, `KnowledgeDB.insert_harness`, the
  `harness_lifecycle` FSM module, the `harness_projection` generator, the
  `mode_switch` component, or the existing `gt mode` command group. They are
  consumed unchanged or untouched.

## In-Root Placement Evidence

All four target paths are within `E:\GT-KB`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\harness_ops.py` — new module.
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py` — modified (new group only).
- `E:\GT-KB\groundtruth-kb\tests\test_harness_ops.py` — new module tests.
- `E:\GT-KB\platform_tests\groundtruth_kb\cli\test_harness_cli.py` — new CLI tests.

No `applications/` paths; no paths outside the GT-KB platform root. Compliant
with the in-root placement constraint of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — governing requirement. FR3 specifies the
  `gt harness` command group and its nine verbs. FR1 is the `harnesses` table
  the verbs mutate (VERIFIED by WI-3337). FR2 is the four-state lifecycle FSM
  the lifecycle verbs validate against (VERIFIED by WI-3339). FR5 is the
  projection each table-mutating verb refreshes (VERIFIED by WI-3338). FR9
  specifies the behavior of `gt harness set-role` (assign prime-builder to an
  active harness, atomic demotion, single-prime-builder invariant); FR9 is the
  deliverable of WI-3341, so WI-3340 registers `set-role` only as a guarded
  placeholder and does not implement role assignment.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the harness-registry architecture
  this requirement extends; defines the role-set wire form and the operating
  topology the registry serves.
- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — the specification governing the
  `mode_switch` transaction component behind `gt mode set-role`. WI-3340 does
  not modify or wrap it; the guarded `set-role` stub directs operators to
  `gt mode set-role`, which remains the operational role command.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  derives tests from FR3's verb set and the FR2 transition graph, including a
  test that the guarded `set-role` mutates nothing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the file bridge is the canonical workflow
  state; this revision is filed as a REVISED bridge entry after the `-002`
  NO-GO.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all four target paths are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; the CLI group and the ops
  module are governed deterministic artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the new module follows the
  established one-focused-module-per-work-item pattern of WI-3338 and WI-3339.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the proposal lifecycle is
  NEW then NO-GO then REVISED then GO/NO-GO then VERIFIED per the file-bridge
  protocol.

## Prior Deliberations

- `DELIB-2079` — the consolidated owner decision for the Antigravity
  Integration design (11-question clarification grill, 2026-05-16). FR3's CLI
  consolidation derives from this decision; Q3 fixed the four-state FSM and Q6
  selected the unified `gt harness` command group.
- `DELIB-2080` — the role-portability amendment (FR9). It makes
  `gt harness set-role` the role-reassignment surface and requires a
  single-prime-builder invariant — the work this revision explicitly defers to
  WI-3341.
- Owner AskUserQuestion decision, 2026-05-16 (`retire` verb) — the owner
  selected "Auto-suspend then retire": `gt harness retire` on an active harness
  internally runs `active -> suspended -> retired`; the FSM stays the literal
  four-edge graph; no `REQ-HARNESS-REGISTRY-001` amendment. WI-3340's `retire`
  verb implements this.
- Owner AskUserQuestion decision, 2026-05-16 (`set-role` scope) — after the
  `-002` NO-GO, the owner selected "Defer set-role to WI-3341": WI-3340 ships
  the eight registry/lifecycle verbs and a guarded `set-role`; `gt mode set-role`
  stays operational and undeprecated. This revision implements that decision.
- The `-002` Loyal Opposition NO-GO (`gtkb-harness-cli-command-group-002.md`) —
  finding F1, resolved by this revision as described in the Response section.
- Sibling VERIFIED threads `gtkb-harness-registry-table-schema` (WI-3337),
  `gtkb-harness-registry-hot-path-projection` (WI-3338), and
  `gtkb-harness-lifecycle-fsm` (WI-3339) — the table, projection, and FSM this
  CLI consumes. WI-3338's proposal stated WI-3340 would wire projection
  regeneration into the `gt harness` mutating verbs; this proposal does so for
  the eight operational verbs.
- A pre-proposal deliberation search returned only the `DELIB-2079` /
  `DELIB-2080` design records and the sibling threads; no prior deliberation
  proposed or rejected a `gt harness` CLI group, and none is in conflict.

## Owner Decisions / Input

This proposal implements owner-decided work and depends on owner approval
recorded as:

- `DELIB-2079` (`outcome=owner_decision`) — owner approved the Antigravity
  Integration design, including the FR3 consolidation of harness registration,
  lifecycle, role, and precedence operations into one `gt harness` command
  group, via an 11-answer AskUserQuestion grill on 2026-05-16.
- Owner AskUserQuestion of 2026-05-16 (`retire` behavior) — the owner selected
  "Auto-suspend then retire". WI-3340's `retire` verb implements exactly this.
- Owner AskUserQuestion of 2026-05-16 (`set-role` scope, in response to the
  `-002` NO-GO) — the owner selected "Defer set-role to WI-3341": WI-3340 ships
  the eight registry/lifecycle verbs fully and a guarded `set-role`;
  `gt mode set-role` stays operational and undeprecated; the operational
  `gt harness set-role` is delivered by WI-3341 (FR9). This revision implements
  that decision. Both AskUserQuestion decisions are mechanically recorded by the
  owner-decision-tracker hook (`detected_via: ask_user_question`).
- `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization for `PROJECT-HARNESS-REGISTRY-REFACTOR`,
  covering WI-3337 through WI-3344, owner-decision `DELIB-2079`.

The project authorization is owner-approval evidence for the bounded project
work; it does not replace this proposal's Loyal Opposition review or the GO
gate.

## Requirement Sufficiency

Existing requirements sufficient. `REQ-HARNESS-REGISTRY-001` FR3 enumerates the
nine verbs; FR1, FR2, and FR5 (all VERIFIED) supply the substrate; FR9
specifies `set-role` and is the deliverable of WI-3341. Two interpretation notes
are recorded transparently for the reviewer.

Interpretation note 1 — the `set-role` verb and the WI-3340 / WI-3341 boundary.
FR3 lists `set-role` among the verbs the `gt harness` group exposes, but FR9
separately and fully specifies that verb's behavior — "the `gt harness set-role`
command may assign `prime-builder` to any active harness ... atomically
demoting every other harness ... [enforcing] exactly one harness holds
`prime-builder`." The owner's WI decomposition assigns FR9 to WI-3341. A
DB-coherent `set-role` further depends on the `harnesses` table being the
authoritative role substrate, which the WI-3342 reader migration delivers.
WI-3340 therefore registers `set-role` as a guarded command — it is exposed by
the group (satisfying FR3's surface requirement) and accepts the eventual
`--harness` / `--role` options so its interface is discoverable, but it
performs no mutation and exits non-zero with guidance to `gt mode set-role`.
The operational verb is WI-3341's deliverable. `gt mode set-role` and the
`mode_switch` component are left unchanged; the `-001` proposal's plan to
deprecate `gt mode set-role` is withdrawn from WI-3340 and re-sequenced to the
work item where `gt harness set-role` becomes its coherent replacement.

Interpretation note 2 — `activate` vs `resume`. The FR2 graph has two edges into
`active`: `registered -> active` and `suspended -> active`. FR3 lists `activate`
and `resume` as distinct verbs. This proposal maps each verb to exactly one
edge: `activate` performs `registered -> active` and rejects a non-`registered`
harness; `resume` performs `suspended -> active` and rejects a non-`suspended`
harness. Each rejection names the correct sibling verb. The `retire` verb
implements the owner's AskUserQuestion decision: from `suspended` it performs
the single `suspended -> retired`; from `active` it performs
`active -> suspended -> retired` (two validated appends); from `registered`
(never activated, no FSM retire path) it fails with guidance; from `retired` it
reports the harness is already retired. No `active -> retired` FSM edge is
added.

## Implementation Plan

### 1. New module `groundtruth-kb/src/groundtruth_kb/harness_ops.py`

Pure-DB transaction operations over the `harnesses` table. Imports the standard
library and `groundtruth_kb.harness_lifecycle`; opens no file and writes no
projection — projection refresh is the CLI layer's concern. Contains no
role-assignment logic.

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

Nine commands. The eight operational verbs resolve config, open the DB, call a
`harness_ops` function or a read accessor, regenerate the FR5 projection via
`harness_projection.generate_harness_projection(db, project_root)` for the
table-mutating verbs, and echo a JSON result; `harness_ops` errors are
re-raised as `click.ClickException`. `register` accepts `--id`, `--name`,
`--type`, and optional `--role` (repeatable; default empty), `--precedence`,
`--capabilities-ref`, `--invocation-surfaces` (a JSON string). The lifecycle
verbs accept `--harness` and `--reason`. `set-precedence` accepts `--harness`
and `--precedence`. `list` / `show` are read-only. `changed_by` for the table
appends is the fixed actor string `gt-harness-cli`.

The ninth command, `set-role`, accepts `--harness` and `--role` (its eventual
interface, so `--help` is accurate) and its body raises a `click.ClickException`
explaining that DB-coherent role assignment is delivered by WI-3341 (FR9) and
the WI-3342 reader migration, and directing the operator to `gt mode set-role`.
It performs no DB write, no role-map write, and no projection regeneration.

The existing `gt mode` group (`set-role`, `list-pending`, `apply-pending`) is
not touched.

### 3. Tests

`groundtruth-kb/tests/test_harness_ops.py` and
`platform_tests/groundtruth_kb/cli/test_harness_cli.py` per the Spec-to-Test
Mapping below.

## Spec-to-Test Mapping

`REQ-HARNESS-REGISTRY-001` FR3 (the `gt harness` verbs over the registry) is
verified as follows.

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
  `suspended` version. Verifies the owner's `retire` AskUserQuestion decision.
- `test_retire_registered_rejected` — `retire` of a never-activated harness
  raises `HarnessOperationError`.
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
- `test_harness_set_role_is_guarded_and_mutates_nothing` — `gt harness set-role`
  exits non-zero, the message names `gt mode set-role`, and the command leaves
  the `harnesses` table, any `harness-state/role-assignments.json`, and the
  `harness-registry.json` projection unchanged. This directly answers the `-002`
  F1 requirement that `set-role` cannot leave the DB `role` field or the
  projection stale.
- `test_gt_mode_set_role_command_unaffected` — `gt mode set-role --help` still
  resolves; the `gt mode` group is untouched by WI-3340.

## Risks

- **`activate` / `resume` distinct-verb interpretation (note 2).** *Mitigation:*
  documented; each verb maps to one FR2 edge with a cross-pointing error; a
  different mapping is a one-line change per verb.
- **WI-3340 delivers eight of nine verbs operational; `set-role` is a guarded
  placeholder.** *Mitigation:* this is the owner's explicit decision; the guard
  message names `gt mode set-role`, which remains fully operational; the
  acceptance criteria state the split plainly; the operational verb is the
  WI-3341 deliverable per FR9.
- **`cli.py` is a large shared file.** *Mitigation:* the change is purely
  additive — one new `@main.group("harness")`; no existing command, including
  the `gt mode` group, is modified.
- **Projection refresh on every table-mutating verb adds a file write.**
  *Mitigation:* this is FR5's intent (the hot-path projection must track the
  table); the generator is VERIFIED (WI-3338) and idempotent. The guarded
  `set-role` performs no mutation and therefore no projection write, so it
  cannot desynchronize the projection.

## Rollback

Remove `groundtruth-kb/src/groundtruth_kb/harness_ops.py`,
`groundtruth-kb/tests/test_harness_ops.py`, and
`platform_tests/groundtruth_kb/cli/test_harness_cli.py`; revert the
`@main.group("harness")` addition in `cli.py`. Nothing else references the new
module, and no existing command is modified, so removal is clean. No schema,
data, or migration is involved.

## Verification Procedure

Run, from the project root:

- `python -m pytest groundtruth-kb/tests/test_harness_ops.py -q`
- `python -m pytest platform_tests/groundtruth_kb/cli/test_harness_cli.py -q`
- `python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_harness_lifecycle.py groundtruth-kb/tests/test_harness_projection.py -q`
  (regression — schema, accessors, FSM, and projection generator are consumed
  unchanged)

Expected: all new tests pass and the existing suites remain green. Observed
counts are recorded in the post-implementation report.

## Acceptance Criteria

- The `gt harness` group exposes all nine FR3 verbs.
- Eight verbs — `register`, `activate`, `suspend`, `resume`, `retire`,
  `set-precedence`, `list`, `show` — are fully operational against the
  `harnesses` registry.
- Each lifecycle verb performs only its FR2-valid transition; an invalid
  transition, a wrong-source-state verb use, and an unknown harness each fail
  with a clear message and no DB write.
- `gt harness retire` of an active harness yields final status `retired` via an
  intermediate `suspended` version, matching the owner's AskUserQuestion
  decision.
- `register` rejects a duplicate harness id.
- Every table-mutating verb refreshes the FR5 projection file.
- The ninth verb, `set-role`, is registered as a guarded command: it exits
  non-zero with guidance to `gt mode set-role` and performs no DB write, no
  role-map write, and no projection regeneration. Its operational behavior is
  `REQ-HARNESS-REGISTRY-001` FR9, delivered by WI-3341.
- `gt mode set-role` and the `gt mode` group are unchanged and remain
  operational.
- All spec-derived tests pass, including the test proving the guarded
  `set-role` mutates nothing; `test_db.py`, `test_harness_lifecycle.py`, and
  `test_harness_projection.py` remain green.
- No change to the `harnesses` table schema, `insert_harness`, the FSM module,
  the projection generator, or the `mode_switch` component.

## Bridge Protocol Compliance

This revision is filed as `bridge/gtkb-harness-cli-command-group-003.md` with a
`REVISED` line inserted at the top of this entry's version list in
`bridge/INDEX.md`, above the `-002` NO-GO and the `-001` NEW, per the file-bridge
protocol. No prior bridge version is deleted or rewritten; `bridge/INDEX.md`
remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`. The
mandatory pre-filing applicability and clause preflights are run after the INDEX
entry is updated; their results are recorded in the review verdict.

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
