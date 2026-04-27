NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 4 — Post-Implementation Report

**Status:** NEW (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** `bridge/gtkb-isolation-016-phase8-wave2-slice4-003.md` (REVISED-1)
**Approved by:** `bridge/gtkb-isolation-016-phase8-wave2-slice4-004.md` (Codex GO with 5 implementation conditions)

---

## 1. What Was Implemented

Per Slice 4 GO `-004` conditions (all 5 satisfied):

| GO Condition | Compliance |
|---|---|
| 1. Keep `_build_classify_tree_command()` on the callable form; do not reintroduce `python -m groundtruth_kb.cli` | ✓ Implementation uses `[sys.executable, "-c", "from groundtruth_kb.cli import main; main()", "project", "classify-tree", ...]` exclusively. Tests 2 + 3 + 5 are explicit regression guards. |
| 2. After zero-exit subprocess return, explicitly verify `classification.json` exists before parsing | ✓ `_path_rewrite.py:run()` checks `classification_path.exists()` after non-zero check; returns `status="error"` with explanatory warning when subprocess exits 0 but produces no file. Test 17 covers this case. |
| 3. Keep live subprocess testing constrained to a tiny temp tree; do not run live classify-tree against `LEGACY_ROOT` in unit tests | ✓ The single live subprocess test (Test 4) creates a 2-file fixture under `tmp_path` and invokes classify-tree against that. All other 18 tests mock `subprocess.run`. |
| 4. Derive rewrite targets from validated manifest's `target_root` and `legacy_root`, including non-`Agent_Red` fixture guard | ✓ `_derive_target_namespace()` computes `target_root.relative_to(legacy_root)`. Test 14 (unit) + Test 15 (`Different_App` fixture) prove non-hardcoding. |
| 5. Keep `legacy-exception` and `owner_decision_pending` as warning-producing, non-blocking classifications for this lane | ✓ Both bucketed without escalating status; `_partition_rows()` routes them to `legacy_exceptions` and `unresolved_paths` lists with status remaining `"ok"`. Tests 9 + 10 cover both paths. |

### 1.1 `scripts/rehearse/_path_rewrite.py` (new file)

171 lines. Module exposes:

| Symbol | Kind | Purpose |
|---|---|---|
| `_CLASSIFY_TREE_DEFAULT_MAX_DEPTH` | constant | Matches GT-KB CLI default (10) |
| `_SCHEMA_VERSION` | constant | `path_rewrite.json` schema versioning (= 1) |
| `_build_classify_tree_command()` | helper | Returns subprocess argv list using callable entrypoint (F1 fix) |
| `_derive_target_namespace()` | helper | Computes `target_root.relative_to(legacy_root)` forward-slashed (F2 fix) |
| `_partition_rows()` | helper | Partitions classify-tree rows into 6 buckets (rewrites, keep_at_root, shared_paths, legacy_exceptions, unresolved_paths, unknown_ownership) |
| `_compose_git_filter_args()` | helper | Composes `--path X --path-rename X:Y\n` lines |
| `run()` | public | Sub-script entry per common contract Wave 2 -003 §4.1 |

### 1.2 `tests/scripts/test_rehearse_path_rewrite.py` (new file)

411 lines, 19 tests. All tests pass in <2s.

| # | Test | Coverage |
|---|---|---|
| 1 | `test_run_dry_run_returns_skipped` | Common contract dry_run |
| 2 | `test_build_classify_tree_command_uses_callable_entrypoint` | **F1 regression** (no `-m`, no `groundtruth_kb.cli` path string) |
| 3 | `test_build_classify_tree_command_includes_required_flags` | F1 argv shape |
| 4 | `test_subprocess_smoke_invokes_classify_tree_against_tmp_dir` | **F1 LIVE smoke** (real subprocess, tmp tree, < 1s) |
| 5 | `test_run_invokes_classify_tree_subprocess` | Mocked subprocess called with `_build_classify_tree_command()` shape |
| 6 | `test_run_produces_rewrites_for_adopter_owned` | Happy path |
| 7 | `test_run_skips_gt_kb_managed_in_rewrites` | gt-kb-managed + gt-kb-scaffolded → keep_at_root |
| 8 | `test_run_emits_shared_structured_to_shared_paths` | shared-structured → shared_paths |
| 9 | `test_run_emits_legacy_exception_to_warnings` | GO condition 5: legacy-exception → list + warning, status="ok" |
| 10 | `test_run_emits_unresolved_paths_when_pending` | GO condition 5: owner_decision_pending → unresolved_paths regardless of ownership |
| 11 | `test_run_writes_path_rewrite_json_with_summary` | Schema version + summary counts |
| 12 | `test_run_writes_git_filter_args_file_format` | `--path X --path-rename X:Y\n` format, one line per rewrite |
| 13 | `test_run_target_path_format_correct` | Forward slashes, no backslashes in target |
| 14 | `test_derive_target_namespace_returns_forward_slashed_relative_path` | **F2 unit** |
| 15 | `test_run_target_namespace_derived_from_manifest_not_hardcoded` | **F2 fixture** (Different_App proves non-hardcoding) |
| 16 | `test_run_returns_error_when_classify_tree_subprocess_fails` | Non-zero exit → error |
| 17 | `test_run_returns_error_when_subprocess_zero_exit_but_no_file_produced` | **GO condition 2**: zero-exit + no file → error |
| 18 | `test_run_returns_error_when_classification_malformed` | Bad JSON → error |
| 19 | `test_run_unknown_ownership_emits_warning` | Future ownership label → warning + skip, status="ok" |

### 1.3 `tests/scripts/test_rehearse_isolation.py` modifications

Two changes, both small:

1. **Appended Test 20** — `test_driver_dispatches_path_rewrite_lane_with_module_now_present`. ~50 LOC. Verifies that `_dispatch("rewrite", ...)` returns `status="ok"` (not "skipped") now that `_path_rewrite.py` is on disk. Mocks subprocess per GO condition 3.
2. **Updated existing fixture** in `test_dispatch_lane_module_missing_returns_skipped` (line 311). The test was using `"rewrite"` as the example "missing" lane; now that the rewrite lane is implemented, the fixture is updated to `"ci"` (next still-unimplemented Stage B lane). The test's intent (dispatcher correctly distinguishes missing from broken) is unchanged — only the lane name changes. Documented in the test's docstring that subsequent slices will need to walk the fixture forward.

These two changes are direct consequences of Slice 4 lighting up the rewrite lane. They preserve all original test intent.

## 2. Verification

```
PYTHONIOENCODING=utf-8 python -m pytest \
    tests/scripts/test_rehearse_path_rewrite.py \
    tests/scripts/test_rehearse_isolation.py \
    tests/scripts/test_rehearse_inventory.py \
    tests/scripts/test_rehearse_common_validation.py \
    -q --tb=short
```

Result: **112 passed in 2.55s.**

Breakdown:
- 19 new Slice 4 tests (path_rewrite)
- 66 rehearse_isolation tests (51 pre-existing + 14 Slice 3 + 1 new Slice 4 driver integration)
- 13 Slice 2 inventory tests (preserved)
- 14 Slice 1 common_validation tests (preserved)

**Walltime:** 2.55s for 112 tests (avg 23ms/test). Confirms no live-root walks beyond the single Test 4 smoke against the 2-file tmp fixture.

**Quality gates:** Will run on commit (test deletion guard, assertion ratchet, architectural guards, credential scan, TSX commit gate) — pre-commit hook expected to PASS 5/5 since: no tests deleted (only renamed-fixture); 19 new tests added (assertion ratchet INCREASE only); no architectural-violating imports; no credentials; no TSX changes.

## 3. Files Changed

### 3.1 Created
- `scripts/rehearse/_path_rewrite.py` (171 LOC)
- `tests/scripts/test_rehearse_path_rewrite.py` (411 LOC, 19 tests)
- `bridge/gtkb-isolation-016-phase8-wave2-slice4-004.md` (Codex GO, tracked from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice4-005.md` (this file)

### 3.2 Modified
- `tests/scripts/test_rehearse_isolation.py` — +74 lines, -2 lines (appended Test 20 + updated fixture in Test 9)
- `bridge/INDEX.md` — append NEW line at top of slice4 entry

### 3.3 Untouched
- `scripts/rehearse_isolation.py` (driver dispatch already registers this lane via Slice 3)
- `scripts/rehearse/_common.py`
- `scripts/rehearse/_inventory.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`

## 4. Operational Verification (manual smoke)

The driver is now Wave-2-functional for the rewrite lane:

```
python scripts/rehearse_isolation.py --phase rewrite --execute
```

This invokes `_path_rewrite.run()` which:
1. Runs classify-tree subprocess (callable form) against `LEGACY_ROOT`
2. Reads classification (~6,335 rows in current tree)
3. Partitions and emits `path_rewrite.json` + `git_filter_args.txt` under `C:/temp/agent-red-rehearsal-{ts}/path_rewrite/`

(Manual smoke not run as part of this commit per GO condition 3 — unit-test coverage is sufficient. Operator can invoke the above command at any time.)

## 5. Compliance Self-Check

Per `.claude/rules/codex-review-gate.md`:
- ✓ Did not implement before bridge GO (Slice 4 GO at `-004`)
- ✓ Implementation scoped exactly to GO -004 conditions
- ✓ Mocking strategy preserved per GO condition 3 (live subprocess constrained to tmp tree)

Per `.claude/rules/file-bridge-protocol.md`:
- ✓ Per-thread version monotonic: 001 → 002 → 003 → 004 → 005 (this file)
- ✓ INDEX entry update at top of slice4 entry (NEW status for post-impl)
- ✓ Bridge files preserved (no deletions of any prior version)
- ✓ Scoped commits: bridge-only commits separated from implementation commit per the file-bridge-protocol §"Guardrails"

## 6. Codex Verification Asks

1. Confirm 5/5 GO conditions are satisfied per the table in §1.
2. Confirm `_build_classify_tree_command()` shape matches the verified-working callable form (Tests 2 + 3 + 5).
3. Confirm Test 4 (live tmp-dir subprocess smoke) actually exercises the classify-tree binary and would catch a future entrypoint regression.
4. Confirm the F2 fixture proof (Test 15 with `Different_App`) sufficiently demonstrates non-hardcoding.
5. Confirm GO condition 2 implementation (zero-exit + no-file → error) is correctly placed AFTER the non-zero-exit check, so the order of error reporting is well-defined.
6. Confirm the renamed fixture in `test_dispatch_lane_module_missing_returns_skipped` (rewrite → ci) preserves the original test intent.
7. Confirm the new driver integration test (Test 20) does not weaken the existing dispatch tests.
8. Confirm the 112-test result with 2.55s runtime indicates no test walks LEGACY_ROOT beyond the bounded Test 4 fixture.
9. **VERIFIED / NO-GO** on Slice 4.

## 7. Sequencing After Slice 4 VERIFIED

The rewrite lane is fully Wave-2-functional. Stage B continues with 6 remaining lanes:

| Slice candidate | Lane(s) | Cohesion |
|---|---|---|
| Slice 5 (proposed cluster) | `_bridge_split.py` + `_backlog_split.py` + `_release_readiness_split.py` | Same "split rows by ownership" pattern; high cohesion |
| Slice 6 | `_ci_inventory.py` + `_membase_export.py` | CI workflow inventory + KB export — both single-source readers |
| Slice 7 | `_production_effects.py` | Documents prod-runtime effects (config, secrets, env) — distinct shape |
| Slice 8 | Stage C: `_chromadb_regen.py` + `_dashboard_regen.py` | Multi-source consumers (need inventory + membase output) |
| Slice 9 | Stage D: `_rollback.py` | Cross-cutting; needs all-of-above |
| → | Wave 3 verification matrix scoping | After all 11 lanes ship |
| → | ISOLATION-017 (Phase 9 productization) | After Wave 3 |

## 8. Commit Plan

Single scoped commit landing:
- `scripts/rehearse/_path_rewrite.py` (NEW)
- `tests/scripts/test_rehearse_path_rewrite.py` (NEW)
- `tests/scripts/test_rehearse_isolation.py` (MODIFIED)
- `bridge/gtkb-isolation-016-phase8-wave2-slice4-004.md` (Codex GO from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice4-005.md` (this report)
- `bridge/INDEX.md` (NEW status line for post-impl)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
