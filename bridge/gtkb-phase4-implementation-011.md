# Phase 4: F6 + F8 + Depth Guard — POST-IMPLEMENTATION REPORT

**Author:** Prime Builder (Opus 4.6)
**Session:** S289
**Date:** 2026-04-13
**Type:** Post-implementation report (seeking VERIFIED)
**GO reference:** bridge/gtkb-phase4-implementation-010.md (Codex GO on v5 revision)
**Proposal reference:** bridge/gtkb-phase4-implementation-007.md + -009.md

## Implementation Status: COMPLETE

- **Commit:** `87e7bd7` on `groundtruth-kb` main
- **Files changed:** 9 (4 new, 5 modified)
- **Lines added:** 2,258 (vs. proposal estimate ~1,810 — higher because test files have more scaffolding than estimated, plus a CLI smoke test)
- **Test result:** **600 pass, 1 warning, 0 fail** (561 baseline + 38 Phase 4 new + 1 CLI smoke)
- **Ruff check:** `All checks passed!`
- **Ruff format:** `65 files already formatted`
- **Docs CLI coverage:** `All documentation checks passed.`

## Commit manifest

```
$ git diff --stat b2d425c..87e7bd7
 docs/reference/cli.md                      |   92 ++
 src/groundtruth_kb/assertions.py           |   17 +-
 src/groundtruth_kb/cli.py                  |  194 +++
 src/groundtruth_kb/project/scaffold.py     |   26 +
 src/groundtruth_kb/reconciliation.py       |  538 ++++++++
 src/groundtruth_kb/spec_scaffold.py        |  372 ++++++
 tests/test_impact.py                       |   47 +-
 tests/test_reconciliation.py               |  706 +++++++++++
 tests/test_spec_scaffold.py                |  307 +++++
 9 files changed, 2258 insertions(+), 6 deletions(-)
```

## Test pass manifest

| Test file | Tests added | Result |
|-----------|-------------|--------|
| `tests/test_impact.py` | +1 (`test_extract_respects_max_composition_depth`) | 29 pass (was 28) |
| `tests/test_spec_scaffold.py` | 10 (new file) | 10 pass |
| `tests/test_reconciliation.py` | 28 (new file, 27 detector + 1 CLI smoke) | 28 pass |
| **Full suite total** | **+39** | **600 pass** |

**Note on the +39 vs proposal's +38:** The proposal committed to 38 new tests (F6: 10, F8: 27, shared extractor: 1). During implementation I added one additional test — the `gt kb reconcile` CLI smoke test in `TestReconcileCLI::test_gt_kb_reconcile_all_runs_every_detector`. The F8 subagent I delegated to could not add this test (its scope forbade touching `cli.py`), and I chose to add it after landing the CLI rather than leave a CLI dispatch code path untested. This is an additive change, not a deviation from proposal scope; total is 600 vs the proposal's 599 target.

## Binding GO conditions — each honored

The GO at `-010` listed 7 implementation conditions. Each verified:

| # | Condition | Evidence |
|---|-----------|----------|
| 1 | Implement Phase 4 as `-007` scope + `-009` expired-provisional correction | F6 module + F8 detectors + CLI + 38 tests land per `-007`/`-009` specification |
| 2 | Keep `ScaffoldOptions.spec_scaffold` optional; default `gt project init` unchanged | `src/groundtruth_kb/project/scaffold.py:40` adds field with `= None` default; integration at line 103 runs only `if options.spec_scaffold is not None` |
| 3 | Generated scaffold specs at `authority='inferred'` until owner promotion | `src/groundtruth_kb/spec_scaffold.py:~325` passes `authority='inferred'` to `insert_spec`; verified by `test_generated_specs_have_authority_inferred` |
| 4 | Populate `assertions_parsed` or `_assertions_parsed` for dry-run quality scoring | `spec_scaffold.py:~305` populates BOTH `assertions_parsed` and `_assertions_parsed` on synthetic; verified by `test_dry_run_quality_scores_executable_assertions` |
| 5 | Shared `_extract_assertion_targets()` depth guard + over-depth regression test | `src/groundtruth_kb/assertions.py:73-118` adds `depth: int = 0` kwarg with `_MAX_COMPOSITION_DEPTH` guard; `tests/test_impact.py` test #16 is the regression test |
| 6 | Stale snapshot evidence-window rule + `changed_at`/`section_activity_days` fallback | `reconciliation.py:241` implements `find_stale_specs` with `T_window_start = S_N[-1].captured_at`; both paths tested |
| 7 | `find_expired_provisionals(db)`, `--provisionals` CLI, documented inclusion in `--all` | `reconciliation.py:485` iterates `db.get_provisional_specs()` and filters replacement lifecycle; CLI at `cli.py` exposes `--provisionals` and `--all`; `docs/reference/cli.md` documents the `--all` category order explicitly |

## Implementation notes and decisions

### 1. CLI wiring contract for orphan detection

`find_orphaned_assertions` accepts an optional `project_root: Path | None` kwarg. The proposal didn't specify the exact CLI plumbing, so I chose:
- CLI exposes `--project-root <path>` (click.Path with `exists=True, dir_okay=True`)
- When omitted, defaults to `cwd`
- The detector itself falls back through `project_root arg → db.project_root attribute → Path.cwd()`

This matches the F8-003 proposal's project-root injection precedent and keeps the detector independently callable from Python without CLI.

### 2. Stale finding shape includes `reason`

The subagent added a `reason` key to stale findings (`"snapshot_window"` or `"changed_at_fallback"`) so tests can assert which code path was taken. This is a test-harness convenience; the proposal didn't prescribe the dict shape beyond "findings list".

### 3. Duplicate pair canonicalization

Duplicate findings canonicalize pairs with `spec_a < spec_b` (lexicographic) for deterministic output across runs. This is not explicitly required by the proposal but is needed for stable test assertions.

### 4. `file_exists` / `json_path` glob handling

For orphan detection, the detector treats `*` in a `file_exists` or `json_path` file target as a literal character (no glob dispatch). This mirrors the runtime handlers in `assertions.py` — those types are not glob-aware at execution time, so the reconciler follows suit to avoid false positives where the runtime would succeed but the reconciler reports orphan.

### 5. Stale detection section replaced `test_stale_cli_smoke`

The proposal's stale section included a `test_stale_cli_smoke` (test #23 in `-007`). The F8 subagent could not add it (its scope forbade `cli.py` modification). Two choices:
- **(a)** Leave the section at 5 tests and drop CLI coverage for stale.
- **(b)** Add a functionally equivalent test covering a different edge case that doesn't need CLI.

Choice (b): the subagent added `test_stale_insufficient_snapshots_uses_fallback`, which exercises the snapshot→fallback handoff (proving the boundary between paths works). After I added the `gt kb reconcile` CLI, I added `test_gt_kb_reconcile_all_runs_every_detector` as a class-scoped CLI smoke test under `TestReconcileCLI`, which covers `--all` dispatch of every detector including stale.

Net: stale gets 6 tests (5 detector + 1 insufficient-snapshots fallback), and there's 1 dedicated CLI smoke test in a new test class. Proposal gets 6 stale tests and CLI coverage — both conditions met via a cleaner split than the `-007` original.

### 6. Test seeding with `validate_assertions=False`

The F8 tests for plain-text safety and non-machine dict children need to install assertions that would fail the schema validator. They use `validate_assertions=False` to bypass validation at insert time — this matches how the runtime's plain-text handling works: plain-text assertions are valid schema-wise (human notes), and non-machine dicts are silently skipped by the extractor.

## Deviations from proposal: NONE material

The only deltas from `-007`/`-009` are:
- **+1 test**: the CLI smoke test I added (total 39 new tests vs proposal's 38; 600 total vs proposal target 599)
- **Stale test substitution**: `test_stale_cli_smoke` → `test_stale_insufficient_snapshots_uses_fallback` + class-scoped CLI smoke test (both boundaries covered)

Both additions are additive and strictly strengthen coverage. No scope was removed or silently weakened.

## Verification commands (all passed)

```bash
cd groundtruth-kb

python -m pytest -q --tb=short -p no:cacheprovider
# → 600 passed, 1 warning in 77.18s

python -m ruff check . --no-cache
# → All checks passed!

python -m ruff format --check . --no-cache
# → 65 files already formatted

python scripts/check_docs_cli_coverage.py
# → All documentation checks passed.
```

## Request for VERIFIED

Codex verification requested. Verify against:
1. Commit `87e7bd7` on `groundtruth-kb` main
2. The 7 binding conditions in `-010` "Conditions For Implementation"
3. The test count +38 (the proposal target; +39 is Prime's additive choice)
4. The binding scope in `-007` + the expired-provisional correction in `-009`

If verification reveals any non-compliance, please cite specific file/line
references so I can patch that single point rather than restructuring.
