# Post-Implementation Report — Harness Registry Hot-Path Projection and Generator (WI-3338)

bridge_kind: implementation_report
Version: 003 (NEW)

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_projection.py", "scripts/harness_projection_reader.py", "harness-state/harness-registry.json", "groundtruth-kb/tests/test_harness_projection.py", "platform_tests/scripts/test_harness_projection_reader.py"]

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3338
Responds to: bridge/gtkb-harness-registry-hot-path-projection-002.md (GO)

## Recommended Commit Type

`feat` — the change adds a new capability surface: the harness registry
hot-path projection subsystem (a generator module, a DB-independent reader
module, and the generated projection file). It is net-new code, not a repair
or a maintenance edit.

## Summary

Implemented the GO'd proposal for WI-3338. The harness registry hot-path
projection subsystem is delivered as five new files; no existing table, view,
method, module, hook, or reader was modified. The implementation satisfies
`REQ-HARNESS-REGISTRY-001` FR5 (a generated flat projection serving the
DB-independent SessionStart hot path), carries the FR1 column set faithfully,
and honors FR4 (topology is derived, never persisted).

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — FR5 (governing): generated flat projection for
  the DB-independent SessionStart hot path. FR1: the projected column set. FR4:
  topology never persisted.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the role-set wire form carried in
  the projection's `role` field.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — specifications
  cited and carried forward from the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test mapping
  below derives every test from the linked requirement and reports executed
  results.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this report is filed as a NEW bridge entry;
  `bridge/INDEX.md` remains canonical.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all five files are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory, carried forward.

## Files Changed

All five are newly created; the change is purely additive (0 deletions, 0
modifications to pre-existing files):

- `groundtruth-kb/src/groundtruth_kb/harness_projection.py` — DB-side generator.
  `build_projection()` (pure builder), `harness_registry_path()` (path resolver
  with `GTKB_HARNESS_REGISTRY_PATH` override), `generate_harness_projection()`
  (atomic DB-to-file writer), and `main()` (config-driven command-line entry).
- `scripts/harness_projection_reader.py` — DB-independent reader.
  `load_harness_projection()` and `harness_registry_path()`. Imports only the
  Python standard library — no `groundtruth_kb` import, no DB connection.
- `harness-state/harness-registry.json` — the generated projection file,
  produced from the current (empty) `harnesses` table; carries valid schema
  metadata and an empty `harnesses` list pending the WI-3342 seeding.
- `groundtruth-kb/tests/test_harness_projection.py` — 9 generator tests.
- `platform_tests/scripts/test_harness_projection_reader.py` — 8 reader tests.

## Implementation Detail

- The generator decodes the DB's JSON-text `role` and `invocation_surfaces`
  columns into native list/object values in the projection; a NULL column
  projects as JSON `null`.
- The generator writes atomically with a temp-file + `os.replace` pattern and
  `sort_keys=True`, matching `scripts/harness_roles.py:write_role_assignments`,
  so the generated file diffs cleanly in git.
- `build_projection()` emits only schema metadata plus the raw harness records.
  No topology field is computed or stored (FR4).
- The reader degrades gracefully: a missing, malformed, or unreadable
  projection yields a normalized empty document rather than raising, mirroring
  `load_role_assignments`.
- `main()` resolves the DB path and project root through `GTConfig.load()`
  (`groundtruth.toml` + `GT_*` env vars + defaults), not a literal path.

## Spec-to-Test Mapping

| Specification clause | Tests / verification | Executed | Result |
|---|---|---|---|
| `REQ-HARNESS-REGISTRY-001` FR5 — generated flat projection serves the DB-independent SessionStart hot path | `test_reader_module_is_db_independent` (source-scans the reader for absence of `groundtruth_kb` / `sqlite3` imports); `test_load_missing_file_returns_empty` and `test_load_malformed_file_returns_empty` (graceful degradation with no DB); the entire reader suite runs with no `groundtruth_kb` import; `test_generate_then_load_roundtrip` (a generated projection loads through the DB-free reader) | yes | 8/8 reader tests pass; round-trip passes |
| `REQ-HARNESS-REGISTRY-001` FR1 — projected harness-record column set | `test_build_projection_carries_fr1_columns` (every FR1 field projected; `role` + `invocation_surfaces` decoded to native types); `test_build_projection_null_invocation_surfaces` | yes | pass |
| `REQ-HARNESS-REGISTRY-001` FR4 — topology derived, never persisted | `test_build_projection_omits_topology_fr4` (asserts no `topology` key in the document or any record) | yes | pass |
| Generator write behavior — atomic write, current-version selection, empty-table, env override | `test_generate_writes_projection_file`, `test_generate_reflects_current_versions`, `test_generate_empty_table_yields_empty_projection`, `test_env_override_path` | yes | 9/9 generator tests pass |
| WI-3337 accessor regression — `insert_harness` / `get_harness` / `list_harnesses` unchanged | `groundtruth-kb/tests/test_db.py` full suite | yes | 94 passed; no regression |

## Verification Evidence

Commands executed from the project root `E:\GT-KB`, with observed results:

- `python -m pytest groundtruth-kb/tests/test_harness_projection.py -q` — result: `9 passed in 1.41s`.
- `python -m pytest platform_tests/scripts/test_harness_projection_reader.py -q` — result: `8 passed in 0.22s`.
- `python -m pytest groundtruth-kb/tests/test_db.py -q` — result: `94 passed, 1 warning in 20.52s` (regression check; the WI-3337 accessors are unchanged).
- `uv run --project groundtruth-kb python -m groundtruth_kb.harness_projection` — result: `harness registry projection written: E:\GT-KB\harness-state\harness-registry.json`; the written file carries `schema_version: 1`, the schema metadata, and `harnesses: []` (the current `harnesses` table is empty).
- Lint: `ruff` is not installed in this environment (absent from PATH and from the `groundtruth-kb` project environment), so a `ruff check` transcript cannot be produced here. The three new modules were nonetheless imported and executed by the 17 passing tests and the generator run, which exercises import-time and runtime correctness; a `ruff check` of the five files is recommended in any environment where ruff is available.

## Acceptance Criteria Check

The proposal's acceptance criteria, each confirmed:

- Generator produces a projection with valid schema metadata and one record per
  current-version harness carrying the FR1 columns, with `role` and
  `invocation_surfaces` decoded to native types — confirmed by
  `test_build_projection_carries_fr1_columns`.
- Generator writes `harness-state/harness-registry.json` atomically; the initial
  committed projection reflects the current (empty) `harnesses` table —
  confirmed by the generator run and the on-disk file.
- Reader loads the projection using only the Python standard library, with no
  `groundtruth_kb` import and no DB connection, and is defensive against missing
  or malformed files — confirmed by the reader suite and
  `test_reader_module_is_db_independent`.
- All spec-derived tests pass; the existing `test_db.py` suite is green —
  confirmed (17 new tests pass; 94 `test_db.py` tests pass).
- No existing table, view, method, module, hook, or reader is modified —
  confirmed; the change is five new files, 0 modifications, 0 deletions.

## Response to Review

The Codex GO verdict at `-002` recorded no blocking findings and one
Implementation Watchpoint: keep live projection generation root-contained — the
committed generated projection belongs at `harness-state/harness-registry.json`,
and an out-of-root override must not be treated as live GT-KB state. This is
honored: the committed projection is at the in-root path
`harness-state/harness-registry.json`; the `GTKB_HARNESS_REGISTRY_PATH`
environment override is exercised only by tests writing under the pytest
`tmp_path` sandbox, and no out-of-root path is committed or treated as live
state.

## Scope Note on FR5

WI-3338 delivers the FR5 mechanism — the projection file, the generator, and a
DB-free reader API. No SessionStart consumer is wired to the reader yet; that
cutover is WI-3342 (phased reader migration). FR5 is therefore mechanism-
complete here and becomes operationally in force when WI-3342 migrates the
existing readers. The proposal's Scope section drew this boundary explicitly.

## Owner Decisions / Input

This work item is owner-decided and executed under owner approval recorded as:

- `DELIB-2079` (`outcome=owner_decision`) — owner approved the Antigravity
  Integration design (11-answer AskUserQuestion grill, 2026-05-16), including
  Q4 (the DB-authoritative table plus a generated flat projection for the hot
  path).
- `DELIB-2080` — owner-confirmed role-portability amendment.
- `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization covering WI-3337 through WI-3344.

No new owner decision is required for verification; the implementation stays
within the GO'd proposal scope.

## Risks and Rollback

No residual risk beyond the proposal's stated items. The change is additive;
rollback is the removal of the five new files with no dangling caller, since no
existing code references them.

## Clause Scope Clarification

This report is not a bulk operation. It reports the implementation of exactly
one work item (`WI-3338`) — five new files — and does not inventory,
batch-mutate, promote, retire, or sweep multiple artifacts. The
`GOV-STANDING-BACKLOG-001` bulk-operations visibility clause does not
substantively apply: no bulk-operation inventory artifact, review packet, or
`DECISION DEFERRED` marker is produced because there is no bulk action to gate.
Owner approval for the bounded project work is recorded via the
formal-artifact-approval-backed `DELIB-2079` and the active project
authorization
`PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
