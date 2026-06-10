# Post-Implementation Report — Harness Role Portability and Single-Prime-Builder Invariant (WI-3341 Slice A, FR9)

bridge_kind: implementation_report
Version: 009 (NEW)

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/groundtruth_kb/test_mode_switch_invariants.py", "platform_tests/groundtruth_kb/test_mode_switch_transaction.py"]

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3341

## Summary

WI-3341 Slice A is implemented per the GO'd proposal
`bridge/gtkb-harness-role-portability-fr9-007.md` (Loyal Opposition GO at
`-008`). `REQ-HARNESS-REGISTRY-001` FR9's role-assignment half is now
operational: `gt harness set-role --harness X` promotes X to `prime-builder`,
enforces an active-harness eligibility gate against the seeded `harnesses`
registry table, and atomically demotes every other recorded harness to
`loyal-opposition` — producing FR9's full role partition. The
`apply_role_switch` transaction component's `prime-builder` branch was refined
to demote every non-target unconditionally, and a new
`verify_role_partition` postcondition confirms the full partition after the
switch.

All 28 spec-derived tests pass (invariant module 6, transaction 9, CLI 13); the
three regression suites are green (31 passed); the linter is clean for the new
and changed code, with two pre-existing findings outside this slice's diff
documented under Verification Evidence.

## Implementation Authorization

The implementation-start authorization packet was created from the `-008` GO
before any source edit:

- Command: `python scripts/implementation_authorization.py begin --bridge-id gtkb-harness-role-portability-fr9`
- `go_file`: `bridge/gtkb-harness-role-portability-fr9-008.md`; `latest_status`: `GO`
- `packet_hash`: `sha256:4ed177baf1262561c436094bee7253144c9ec230f28ccf6353941cda29a0d8a5`
- All six `target_paths` authorized; project authorization
  `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  active, bound to `WI-3341`.
- Under concurrent Prime-session contention for the shared
  `current.json` packet pointer, the packet was re-activated
  (`python scripts/implementation_authorization.py activate --bridge-id gtkb-harness-role-portability-fr9`)
  before each protected edit; every protected edit landed under a live,
  WI-3341-scoped packet.

## Files Changed

| File | Status | Lines | Purpose |
|------|--------|-------|---------|
| `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` | modified | +8 / -0 | `apply_role_switch`'s `role == "prime-builder"` branch now writes every non-target recorded harness to `["loyal-opposition"]` unconditionally — the FR9 full-partition fix. |
| `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py` | new | 113 | `RolePartitionViolation`, `prime_builder_ids`, `verify_role_partition` — the FR9 role-partition postcondition. |
| `groundtruth-kb/src/groundtruth_kb/cli.py` | modified | +70 / -12 | The guarded `gt harness set-role` stub replaced by the operational command: active-harness eligibility gate, `apply_role_switch`, `verify_role_partition`, JSON result. |
| `platform_tests/groundtruth_kb/test_mode_switch_invariants.py` | new | 104 | 6 spec-derived tests for the invariant module. |
| `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` | modified | +26 / -0 | 1 new full-partition regression test (`-006` F1 empty-role non-target). |
| `platform_tests/groundtruth_kb/cli/test_harness_cli.py` | modified | +139 / -23 | 6 operational `set-role` CLI tests added; the WI-3340 guarded-stub test removed; 3 test helpers added. |

## In-Root Placement Evidence

All six changed files are within the GT-KB project root `E:\GT-KB`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\mode_switch\invariants.py`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\mode_switch\transaction.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\cli\test_harness_cli.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\test_mode_switch_invariants.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\test_mode_switch_transaction.py`

No `applications/` paths and no paths outside the platform root; this bridge
report resides under `E:\GT-KB\bridge\`. Compliant with the in-root placement
constraint of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — FR9 (operational `gt harness set-role`,
  active-harness eligibility, atomic full-partition demotion, the
  single-prime-builder invariant); FR3 (the `gt harness` command group); FR6
  (no two-harness assumption).
- `GOV-HARNESS-ROLE-PORTABILITY-001` — Prime Builder and Loyal Opposition are
  portable harness-assigned roles; `set-role` resolves and assigns by durable
  harness id and no code path branches on `harness_type`.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the harness role-set model.
- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — the `apply_role_switch`
  transaction discipline; the validator chain, audit-trail record, and atomic
  role-map write order are unchanged by this slice.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` —
  cross-cutting bridge / isolation specs.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory.

## Implementation Notes

- `transaction.py` — `apply_role_switch`'s non-target loop gained a
  `role == "prime-builder"` branch that writes each non-target recorded
  harness's `role` to `["loyal-opposition"]` unconditionally (replacing the
  prior behavior of rewriting a non-target only when it already held the
  requested role). The `role == "loyal-opposition"` branch, the validator
  chain, the audit-trail record, and the atomic role-map write are unchanged.
  This makes the transaction yield FR9's full role partition atomically,
  including a non-target whose prior role set was empty.
- `invariants.py` — a new standard-library-only module.
  `prime_builder_ids` returns the harness ids holding `prime-builder` or the
  READ-compatible `acting-prime-builder` provenance token.
  `verify_role_partition` raises `RolePartitionViolation` unless exactly one
  harness holds a prime-builder-class role and every other harness's role set
  is exactly `["loyal-opposition"]`.
- `cli.py` — the guarded `gt harness set-role` stub was replaced by the
  operational command: `--harness` (required) and `--reason`. It opens the DB,
  applies the FR9 active-harness eligibility gate via `KnowledgeDB.get_harness`
  (fails closed when the harness is absent or its `status` is not `active`),
  calls `apply_role_switch(..., "prime-builder", ...)`, then
  `verify_role_partition`, and echoes a JSON result. The stub's `--role` option
  was removed; neither the gate nor the command inspects `harness_type`.
- Tests — `test_mode_switch_invariants.py` is new (6 tests);
  `test_mode_switch_transaction.py` gained one full-partition regression test;
  `test_harness_cli.py` gained 6 operational `set-role` tests and 3 helpers,
  and the WI-3340 guarded-stub test `test_harness_set_role_is_guarded_and_mutates_nothing`
  was removed (it asserted the explicitly-temporary stub behavior; the
  operational tests supersede it).

## Spec-to-Test Mapping

| Specification clause | Covering tests | Observed |
|---|---|---|
| FR9 — `apply_role_switch` produces the full partition (every non-target to `loyal-opposition`, including an empty-role non-target) | `test_apply_role_switch_prime_builder_demotes_all_non_targets` | PASS |
| FR9 — single-prime-builder invariant verified as a full partition | `test_verify_role_partition_accepts_valid_partition`, `test_verify_role_partition_rejects_zero_prime_builder`, `test_verify_role_partition_rejects_multiple_prime_builder`, `test_verify_role_partition_rejects_non_target_without_loyal_opposition` | PASS |
| FR9 — legacy scalar role wire form counted | `test_prime_builder_ids_handles_legacy_scalar_role`, `test_prime_builder_ids_single` | PASS |
| FR9 — `set-role` promotes target, demotes others | `test_harness_set_role_promotes_and_demotes`, `test_harness_set_role_emits_single_prime_builder` | PASS |
| FR9 — role portability, no static binding | `test_harness_set_role_reassigns_prime_builder` | PASS |
| FR9 — active-harness eligibility gate | `test_harness_set_role_rejects_non_active_harness`, `test_harness_set_role_unknown_harness_rejected` | PASS |
| FR9 + FR6 — atomic demotion of every other harness, no two-harness assumption | `test_harness_set_role_three_harness_demotes_all_non_targets` | PASS |
| `GOV-HARNESS-ROLE-PORTABILITY-001` — roles are portable harness-assigned, not model/vendor-bound | `test_harness_set_role_reassigns_prime_builder`, `test_harness_set_role_three_harness_demotes_all_non_targets` | PASS |

## Verification Evidence

Commands executed from the project root:

- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/cli/test_harness_cli.py -q` — observed `28 passed in 2.89s`. Per suite: `test_mode_switch_invariants.py` 6 passed (new); `test_mode_switch_transaction.py` 9 passed (8 pre-existing + 1 new full-partition regression); `test_harness_cli.py` 13 passed (6 lifecycle/precedence + 6 operational `set-role` + 1 `gt mode set-role` unaffected).
- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/test_mode_switch_validation.py groundtruth-kb/tests/test_harness_ops.py -q` — observed `31 passed in 2.55s` (regression). Per suite: `test_mode_switch_pending.py` 6 passed; `test_mode_switch_validation.py` 10 passed; `test_harness_ops.py` 15 passed. The pending and validation suites exercise `apply_role_switch` and the validators unchanged; `test_harness_ops.py` confirms the WI-3340 harness operations module is untouched.
- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_invariants.py -q` — observed `6 passed` (re-run after the import-ordering fix below).
- `python -m ruff check` on the six changed files — clean for all new and changed code. Two findings remain, both pre-existing and outside this slice's diff:
  - `transaction.py:89:9 SIM105` in `_atomic_write_json` — a `try`/`except`/`pass` block. The diff to `transaction.py` is the 8-line addition at the `apply_role_switch` non-target loop (`@@ -166,6 +166,14 @@`); `_atomic_write_json` (lines 79-93) is untouched.
  - `test_mode_switch_transaction.py:10:1 I001` — the import block. The diff to that file is the 26-line append at `@@ -144,0 +145,26 @@`; the import block is untouched.
  Both findings pre-date this slice; the GO'd `-007` proposal scopes the `transaction.py` change to the demotion-branch refinement and the test-file change to appending one test, so neither finding is in scope for this slice and a scoped change does not reformat unrelated lines. The one ruff finding this slice introduced — `I001` in the new `test_mode_switch_invariants.py` — was fixed (the blank line between the `pytest` and `groundtruth_kb` imports was removed) and the file re-tested (`6 passed`).

## Acceptance Criteria Check

| Acceptance criterion (from `-007`) | Status | Evidence |
|---|---|---|
| `gt harness set-role --harness X` promotes X to `prime-builder` and demotes every other recorded harness — including an empty-role non-target — to `loyal-opposition` via `apply_role_switch`, within one transaction. | met | `test_harness_set_role_promotes_and_demotes`, `test_harness_set_role_three_harness_demotes_all_non_targets`, `test_apply_role_switch_prime_builder_demotes_all_non_targets`. |
| `set-role` rejects a target absent from the registry or whose `status` is not `active`, with a non-zero exit and no role-map mutation. | met | `test_harness_set_role_rejects_non_active_harness`, `test_harness_set_role_unknown_harness_rejected`. |
| After the switch the role map is a valid FR9 partition; `verify_role_partition` confirms it and the command reports the `prime-builder` id. | met | `test_harness_set_role_emits_single_prime_builder`; `verify_role_partition` accept test. |
| `verify_role_partition` raises for zero, multiple, and non-target-without-`loyal-opposition` states. | met | `test_verify_role_partition_rejects_zero_prime_builder`, `..._rejects_multiple_prime_builder`, `..._rejects_non_target_without_loyal_opposition`. |
| Promoting a previously-`loyal-opposition` harness reassigns `prime-builder` to it — role portability with no static binding. | met | `test_harness_set_role_reassigns_prime_builder`. |
| Role assignment attaches to the durable harness id; no `set-role` code path branches on `harness_type`. | met | `test_harness_set_role_reassigns_prime_builder` and `..._three_harness_demotes_all_non_targets` use distinctly-typed harnesses; the command code reads only `status` and the harness id. |
| Three registered, active harnesses: promoting one makes it the sole `prime-builder`, both others `loyal-opposition`. | met | `test_harness_set_role_three_harness_demotes_all_non_targets`. |
| `gt mode set-role` and every other `gt harness` verb behave correctly; the `apply_role_switch` `loyal-opposition` branch, validator chain, and audit-record writer are unchanged. | met | `test_gt_mode_set_role_command_unaffected`; `test_harness_cli.py` T-HC-1..6; regression suites `31 passed`. |
| All spec-derived tests pass; the regression suites remain green. | met | `28 passed`; `31 passed`. |
| No change to `harness_ops.py`, `scripts/harness_roles.py`, the `harnesses` table, the FSM, or the projection generator. | met | The diff touches only the six `target_paths`; `test_harness_ops.py` (15 passed) confirms `harness_ops.py` is untouched. |

## Recommended Commit Type

`feat:` — this change adds net-new capability: an operational `gt harness
set-role` command with an active-harness eligibility gate, a new
`mode_switch/invariants.py` module (113 lines), a refinement to
`apply_role_switch` that produces FR9's full role partition, and new
spec-derived tests. It is not a repair (`fix:`), a behavior-preserving
restructure (`refactor:`), or maintenance (`chore:`).

## Owner Decisions / Input

- `DELIB-2079` (`outcome=owner_decision`) — owner approved the Antigravity
  Integration design.
- `DELIB-2080` (`outcome=owner_decision`) — owner approved the role-portability
  amendment that became FR9.
- `DELIB-0831` (`outcome=owner_decision`) — owner decision that Prime Builder
  and Loyal Opposition are portable harness-assigned roles; the owner decision
  behind `GOV-HARNESS-ROLE-PORTABILITY-001`.
- Owner AskUserQuestion of 2026-05-16 (`DECISION-0649`) — the owner deferred
  the operational `gt harness set-role` from WI-3340 to WI-3341.
- Owner AskUserQuestion of 2026-05-16 ("Seed the harnesses table first") — the
  owner pulled WI-3342 Slice A ahead of WI-3341 so the eligibility gate could
  read the seeded `harnesses` table.
- `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization covering WI-3337 through WI-3344.

## Prior Deliberations

- `DELIB-2079` / `DELIB-2080` / `DELIB-0831` — the Antigravity Integration
  design, the role-portability amendment (FR9), and the portable-role owner
  decision.
- The `-008` GO on the `-007` proposal — this report implements the GO'd scope.
- `bridge/gtkb-harness-role-portability-fr9-002.md`, `-004.md`, `-006.md` — the
  three prior NO-GO verdicts (active-harness eligibility gate, missing
  `GOV-HARNESS-ROLE-PORTABILITY-001` linkage, full role partition); all are
  resolved in the GO'd `-007` proposal this report implements.
- `bridge/gtkb-harness-registry-seed-004.md` — the VERIFIED WI-3342 Slice A
  seed thread that populated the `harnesses` table the eligibility gate reads.
- Sibling VERIFIED threads `gtkb-harness-registry-table-schema` (WI-3337),
  `gtkb-harness-registry-hot-path-projection` (WI-3338),
  `gtkb-harness-lifecycle-fsm` (WI-3339), `gtkb-harness-cli-command-group`
  (WI-3340).

## Clause Scope Clarification

This implementation is not a bulk operation. It modifies two source modules,
adds one source module, adds or updates three test files, and implements one
slice of one work item (`WI-3341`); it does not inventory, batch-mutate,
promote, retire, or sweep multiple artifacts. The `GOV-STANDING-BACKLOG-001`
bulk-operations visibility clause therefore does not substantively apply.

## Bridge Protocol Compliance

This report is filed as `bridge/gtkb-harness-role-portability-fr9-009.md` with
a `NEW` line inserted at the top of this entry's version list in
`bridge/INDEX.md` for post-implementation verification, per the file-bridge
protocol. The full version chain (`-001` NEW, `-002` NO-GO, `-003` REVISED,
`-004` NO-GO, `-005` REVISED, `-006` NO-GO, `-007` REVISED, `-008` GO, `-009`
report) is preserved; no prior bridge version is deleted or rewritten.
`bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
