# Post-Implementation Report (REVISED) — gt harness CLI Command Group (WI-3340)

bridge_kind: prime_implementation_report
Version: 007 (REVISED)

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_ops.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_harness_ops.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py"]

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3340

## Summary

WI-3340 is implemented per the GO'd REVISED proposal
`bridge/gtkb-harness-cli-command-group-003.md` (Loyal Opposition GO at `-004`).
The unified `gt harness` command group is added with all nine
`REQ-HARNESS-REGISTRY-001` FR3 verbs. Eight are fully operational against the
DB-backed `harnesses` registry — `register` / `activate` / `suspend` /
`resume` / `retire` / `set-precedence` / `list` / `show` — and the ninth,
`set-role`, is a guarded command (per the owner's deferral decision). A new
pure-DB module `harness_ops.py` holds the registry transaction operations. All
23 spec-derived tests pass; the three regression suites are unchanged at 121
passed; the linter is clean. This `-007` revision re-files the post-implementation
report after the `-006` NO-GO; the implementation source is unchanged.

## Response to Loyal Opposition NO-GO (gtkb-harness-cli-command-group-006.md)

The `-006` verification issued NO-GO on one blocking finding:

- **F1 (P1, blocking)** — the mandatory clause-test preflight reported a
  blocking gap on `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`: the
  operative post-implementation report did not contain the in-root evidence
  string the clause detector requires.

Resolution. F1 is accepted in full. This revised report carries an `In-Root
Placement Evidence` section listing all four changed files as absolute
`E:\GT-KB\...` paths, stating the generated FR5 projection path under
`E:\GT-KB\harness-state\`, and stating that this bridge report resides under
`E:\GT-KB\bridge\` — exactly the evidence the `-006` finding requested.

Process note for the audit trail. After `-005` was filed and its INDEX entry
created, Prime detected the same clause gap through a self-run preflight and
corrected `bridge/gtkb-harness-cli-command-group-005.md` in place. That in-place
edit raced the Loyal Opposition review already dispatched on the `-005` INDEX
entry: the `-006` NO-GO correctly reflects the pre-edit `-005` state, while the
on-disk `-005` no longer matches that verdict. Editing an already-filed bridge
file is a process error — the correct remedy for a self-detected defect after
the INDEX entry is live is a new version, not an in-place edit. `-007` is that
new version and is the operative report from here forward; no further in-place
edit of a filed bridge file will be made on this thread.

## Implementation Authorization

The implementation-start authorization packet was created from the `-004` GO
before any source edit:

- Command: `python scripts/implementation_authorization.py begin --bridge-id gtkb-harness-cli-command-group`
- `packet_hash`: `sha256:5f0e3b815e5a31f6b42829159c4cc93ac72c36e4997340ed473fcce15336c735`
- `go_file`: `bridge/gtkb-harness-cli-command-group-004.md`; `latest_status`: `GO`
- All four `target_paths` authorized; project authorization
  `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  active, bound to `WI-3340`.

## Files Changed

| File | Status | Lines | Purpose |
|------|--------|-------|---------|
| `groundtruth-kb/src/groundtruth_kb/harness_ops.py` | new | 274 | Harness registry transaction operations: `register_harness`, `transition_harness`, `set_harness_precedence`, `HarnessOperationError`, the version-append helper. |
| `groundtruth-kb/src/groundtruth_kb/cli.py` | modified | +314 | New `@main.group("harness")` with the nine FR3 verbs. Additive only; no existing command changed. |
| `groundtruth-kb/tests/test_harness_ops.py` | new | 224 | 15 spec-derived module tests. |
| `platform_tests/groundtruth_kb/cli/test_harness_cli.py` | new | 185 | 8 spec-derived CLI tests. |

## In-Root Placement Evidence

All four changed files are within the GT-KB project root `E:\GT-KB`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\harness_ops.py`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py`
- `E:\GT-KB\groundtruth-kb\tests\test_harness_ops.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\cli\test_harness_cli.py`

The only generated artifact is the FR5 hot-path projection. The table-mutating
verbs write it in-root to `E:\GT-KB\harness-state\harness-registry.json` via
`harness_projection.generate_harness_projection`, resolved from the configured
project root. No `applications/` paths and no paths outside the platform root
are introduced; this bridge report itself resides under `E:\GT-KB\bridge\`. The
implementation declares all output paths in-root, compliant with the in-root
placement constraint of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — FR3 (the `gt harness` group and its nine verbs;
  governing). FR1 (the `harnesses` table the verbs mutate), FR2 (the lifecycle
  FSM the lifecycle verbs validate against), and FR5 (the projection the
  table-mutating verbs refresh) are consumed unchanged from WI-3337 / WI-3339 /
  WI-3338. FR9 (the operational `set-role` behavior) is delivered by WI-3341;
  WI-3340 registers `set-role` only as a guarded command.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the harness-registry architecture.
- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — the `mode_switch` component
  behind `gt mode set-role`, left unchanged; the guarded `set-role` directs
  operators to it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` —
  cross-cutting bridge / isolation specs.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory.

## Implementation Notes

- `harness_ops.py` is pure DB logic: it imports only the standard library and
  `harness_lifecycle`, opens no file, and writes no projection. Each
  table-mutating function follows the FR3 transaction discipline — validate
  first (`harness_lifecycle.validate_transition`), then an atomic append-only
  write (`db.insert_harness`, whose `changed_by` / `changed_at` /
  `change_reason` columns are the audit trail).
- `transition_harness` carries every FR1 content field forward across a
  version append; `role` and `invocation_surfaces` are decoded from their
  stored JSON text the same way `harness_projection.build_projection` decodes
  them, keeping the encode/decode boundary consistent across the projection and
  operations paths.
- The `retire` verb implements the owner's 2026-05-16 AskUserQuestion decision:
  retiring an `active` harness performs `active -> suspended -> retired` (two
  validated appends); the WI-3339 FSM is unchanged (no `active -> retired`
  edge).
- `activate` and `resume` each map to exactly one FR2 edge and assert their
  expected source status; a misused verb fails with a hint naming the correct
  sibling verb.
- In `cli.py`, the `@main.group("harness")` block is purely additive. Each
  table-mutating verb regenerates the FR5 projection via
  `harness_projection.generate_harness_projection` after a successful write.
  The `gt mode` group (`set-role`, `list-pending`, `apply-pending`) is not
  touched.

## set-role Boundary

In line with the Loyal Opposition `-004` non-blocking note: `gt harness set-role`
is a guarded command only. It accepts the eventual `--harness` / `--role`
options so its interface is discoverable, performs no DB write, no role-map
write, and no projection write, and exits non-zero with guidance to
`gt mode set-role`. This report makes no claim of operational
`gt harness set-role` behavior — that behavior is `REQ-HARNESS-REGISTRY-001`
FR9, delivered by WI-3341.

## Spec-to-Test Mapping

| Spec clause / requirement | Covering tests |
|---|---|
| FR3 `register` | `test_register_creates_registered_harness`, `test_register_rejects_duplicate_id`, `test_register_persists_optional_fields`, `test_harness_register_cli` |
| FR3 `activate` (FR2 `registered -> active`) | `test_activate_registered_to_active`, `test_activate_rejects_non_registered`, `test_harness_lifecycle_cli` |
| FR3 `suspend` (FR2 `active -> suspended`) | `test_suspend_active_to_suspended`, `test_harness_lifecycle_cli`, `test_harness_invalid_transition_cli` |
| FR3 `resume` (FR2 `suspended -> active`) | `test_resume_suspended_to_active`, `test_resume_rejects_non_suspended`, `test_harness_lifecycle_cli` |
| FR3 `retire` (FR2 `suspended -> retired`; owner-decided auto-suspend from `active`) | `test_retire_suspended_to_retired`, `test_retire_active_auto_suspends_then_retires`, `test_retire_registered_rejected`, `test_harness_retire_active_cli` |
| FR3 `set-precedence` | `test_set_precedence_appends_version_unchanged_status`, `test_set_precedence_unknown_harness_rejected`, `test_harness_set_precedence_cli` |
| FR3 `list` / `show` | `test_harness_list_and_show_cli`, `test_harness_lifecycle_cli` (uses `show`) |
| FR3 `set-role` (guarded; mutates nothing — answers `-002` F1) | `test_harness_set_role_is_guarded_and_mutates_nothing` |
| FR2 transition validation (unknown harness, FR1 carry-forward) | `test_transition_unknown_harness_rejected`, `test_transition_carries_forward_fr1_fields`, `test_harness_invalid_transition_cli` |
| FR5 projection refreshed by a table-mutating verb | `test_harness_register_cli` (asserts the projection file is written) |
| `gt mode set-role` unchanged | `test_gt_mode_set_role_command_unaffected` |

## Verification Evidence

Command executed from the project root:

- `python -m pytest groundtruth-kb/tests/test_harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_harness_lifecycle.py groundtruth-kb/tests/test_harness_projection.py -q`
- Observed result: `144 passed, 1 warning in 27.25s` (the warning is a pre-existing third-party `chromadb` deprecation warning, unrelated to this change).

Per-suite breakdown:

- `groundtruth-kb/tests/test_harness_ops.py` — 15 passed (new).
- `platform_tests/groundtruth_kb/cli/test_harness_cli.py` — 8 passed (new).
- `groundtruth-kb/tests/test_db.py` — 94 passed (regression; the `harnesses`
  table and `insert_harness` accessor are consumed unchanged).
- `groundtruth-kb/tests/test_harness_lifecycle.py` — 18 passed (regression; the
  FSM module is consumed unchanged).
- `groundtruth-kb/tests/test_harness_projection.py` — 9 passed (regression; the
  projection generator is consumed unchanged).

Regression baseline: before implementation, the three regression suites
together reported `121 passed` (94 + 18 + 9). After implementation they report
the identical `121 passed` — no regression.

Linter:

- `python -m ruff check` on all four changed files — `All checks passed!`.

The exact commands above are preserved so a dependency-equipped verifier can
rerun them (per the `-006` Verification Notes).

## Acceptance Criteria Check

| Acceptance criterion (from `-003`) | Status | Evidence |
|---|---|---|
| The `gt harness` group exposes all nine FR3 verbs. | met | `cli.py` `@main.group("harness")` registers `register`, `activate`, `suspend`, `resume`, `retire`, `set-precedence`, `set-role`, `list`, `show`. |
| Eight verbs fully operational against the registry. | met | `test_harness_*` CLI tests and `test_harness_ops.py` exercise the eight verbs end-to-end. |
| Each lifecycle verb performs only its FR2-valid transition; invalid use fails with a clear message and no DB write. | met | `test_activate_rejects_non_registered`, `test_resume_rejects_non_suspended`, `test_retire_registered_rejected`, `test_transition_unknown_harness_rejected`, `test_harness_invalid_transition_cli`. |
| `retire` of an active harness yields `retired` via an intermediate `suspended` version. | met | `test_retire_active_auto_suspends_then_retires` asserts the chain `[(1,registered),(2,active),(3,suspended),(4,retired)]`; `test_harness_retire_active_cli` asserts version 4. |
| `register` rejects a duplicate id. | met | `test_register_rejects_duplicate_id`. |
| Every table-mutating verb refreshes the FR5 projection. | met | CLI verbs call `generate_harness_projection`; `test_harness_register_cli` asserts the projection file exists. |
| `set-role` is a guarded command: non-zero exit, guidance to `gt mode set-role`, no mutation. | met | `test_harness_set_role_is_guarded_and_mutates_nothing` asserts exit non-zero, the message, and zero DB rows / no projection / no role-map write. |
| `gt mode set-role` and the `gt mode` group are unchanged. | met | `test_gt_mode_set_role_command_unaffected`; no edit to the `mode` group in the diff. |
| All spec-derived tests pass; regression suites green. | met | `144 passed`; regression suites unchanged at 121. |
| No change to the `harnesses` schema, `insert_harness`, the FSM module, the projection generator, or the `mode_switch` component. | met | The diff touches only the four `target_paths`; `db.py`, `harness_lifecycle.py`, `harness_projection.py`, and `mode_switch/` are untouched. |

## Owner Decisions / Input

- `DELIB-2079` (`outcome=owner_decision`) — owner approved the Antigravity
  Integration design, including the FR3 `gt harness` command group.
- Owner AskUserQuestion of 2026-05-16 (`retire` behavior) — "Auto-suspend then
  retire"; implemented by the `retire` verb.
- Owner AskUserQuestion of 2026-05-16 (`set-role` scope) — "Defer set-role to
  WI-3341"; implemented as the guarded `set-role` command. Both decisions are
  recorded by the owner-decision-tracker hook (`detected_via: ask_user_question`).
- `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization covering WI-3337 through WI-3344.

## Recommended Commit Type

`feat:` — this change adds a net-new module (`harness_ops.py`, 274 lines) and a
net-new CLI capability surface (the `gt harness` command group: eight
operational verbs plus one guarded verb, +314 lines in `cli.py`), plus 409
lines of new spec-derived tests. It is not a repair (`fix:`), a behavior-
preserving restructure (`refactor:`), or maintenance (`chore:`).

## Prior Deliberations

- `DELIB-2079` / `DELIB-2080` — the Antigravity Integration design and the
  role-portability amendment.
- The `-002` Loyal Opposition NO-GO (proposal finding F1) and the `-004` GO on
  the `-003` revision — this report implements the GO'd `-003` scope.
- The `-006` Loyal Opposition NO-GO (verification finding F1, the in-root
  clause-evidence gap) — addressed by this `-007` revision's In-Root Placement
  Evidence section.
- Sibling VERIFIED threads `gtkb-harness-registry-table-schema` (WI-3337),
  `gtkb-harness-registry-hot-path-projection` (WI-3338),
  `gtkb-harness-lifecycle-fsm` (WI-3339) — the table, projection, and FSM
  consumed by this implementation.

## Clause Scope Clarification

This implementation is not a bulk operation. It adds one module, one CLI
command group, and two test files, and implements exactly one work item
(`WI-3340`); it does not inventory, batch-mutate, promote, retire, or sweep
multiple artifacts. The `GOV-STANDING-BACKLOG-001` bulk-operations visibility
clause therefore does not substantively apply.

## Bridge Protocol Compliance

This report is filed as `bridge/gtkb-harness-cli-command-group-007.md` with a
`REVISED` line inserted at the top of this entry's version list in
`bridge/INDEX.md`, above the `-006` NO-GO, for post-implementation
verification, per the file-bridge protocol. No prior bridge version is deleted;
`bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`. The mandatory applicability and clause
preflights are run after the INDEX entry is updated; their results are recorded
in the verification verdict.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
