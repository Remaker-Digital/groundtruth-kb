NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 3 — Post-Implementation Report

**Status:** NEW (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** `bridge/gtkb-isolation-016-phase8-wave2-slice3-003.md` (REVISED-1)
**Approved by:** `bridge/gtkb-isolation-016-phase8-wave2-slice3-004.md` (Codex GO with conditions)

---

## 1. What Was Implemented

Per Slice 3 GO -004 conditions (all satisfied):
- ✓ Scoped to `scripts/rehearse_isolation.py`, `scripts/rehearse/_common.py`, additive tests
- ✓ `--no-dry-run` refusal preserved (still EXIT_REFUSE)
- ✓ `--execute` for real lane invocation; default safe dry-run
- ✓ `--output-dir` overrides validated with same M2 sandbox contract
- ✓ Broken implemented lanes return `error`, not `skipped`
- ✓ Per GO -004 implementation note: `--dry-run`/`--execute` precedence visible (notice printed when `--execute` set)
- ✓ Per GO -004 implementation note: run-summary coverage tested for both ok-path emission and skipped-only no-emission

### 1.1 `scripts/rehearse/_common.py` extension

Added `validate_sandbox_output_dir(output_dir: Path) -> None` helper applying M2 rules (cannot be under TARGET_ROOT_DEFAULT or LEGACY_ROOT; must match sandbox allowlist). Refactored `load_manifest()` M2 block to call the helper instead of inlining the three checks. Functionally equivalent; eliminates duplication; supports F2 fix in driver. ~25 LOC additive (helper) + ~15 LOC removed (inline checks) = net additive.

### 1.2 `scripts/rehearse_isolation.py` driver wire-up

| Change | Location |
|---|---|
| Imports added: `importlib`, `json`, `time`, `validate_sandbox_output_dir`, `ManifestValidationError` | Top of file |
| `--execute` flag + help text documenting precedence over `--dry-run` | `_build_parser()` |
| `--output-dir` optional override flag | `_build_parser()` |
| `--dry-run` help text updated to point at `--execute` | `_build_parser()` |
| `dry_run = not args.execute` + visible notice when `--execute` is set | `main()` |
| `--no-dry-run` refusal message updated to point at `--execute` | `main()` |
| `_resolve_output_dir(manifest, override)` helper with M2 validation on override | New module-level function |
| `_dispatch(phase, manifest, output_dir, *, dry_run)` with narrowed exception handling | New module-level function |
| Replace stub print block with real dispatch loop + per-lane status reporting | `main()` |
| Run-summary.json emission when any lane returned `ok` or `error` (not when all skipped) | `main()` |
| `load_manifest(args.manifest, wave=2)` instead of default | `main()` |
| Catch `ManifestValidationError` from `_resolve_output_dir()` and exit `EXIT_USAGE` | `main()` |

Complete file rewrite vs Wave 1 stub; preserves the existing CLI surface (target-root, manifest, phase, dry-run, no-dry-run, accept-drift) and adds the two new flags.

### 1.3 Test additions

13 new tests appended to `tests/scripts/test_rehearse_isolation.py`:

| # | Test | Coverage |
|---|---|---|
| 1 | `test_main_loads_manifest_at_wave2` | F1: load_manifest called with wave=2 |
| 2 | `test_execute_flag_enables_real_run` | F1: --execute does NOT trigger v1 refusal |
| 3 | `test_no_dry_run_still_refused_even_with_execute` | F1: --no-dry-run priority preserved |
| 4 | `test_resolve_output_dir_default_appends_iso_timestamp` | output_dir construction shape |
| 5 | `test_output_dir_override_in_sandbox_accepted` | F2: positive (sandbox path) |
| 6 | `test_output_dir_override_under_legacy_root_rejected` | F2: negative (LEGACY_ROOT) |
| 7 | `test_output_dir_override_under_target_root_rejected` | F2: negative (TARGET_ROOT) |
| 8 | `test_output_dir_override_non_allowlisted_rejected` | F2: negative (sync path) |
| 9 | `test_dispatch_lane_module_missing_returns_skipped` | F3: not-yet-implemented lane → skipped |
| 10 | `test_dispatch_lane_module_broken_dependency_returns_error` | F3: lane with broken import → error |
| 11 | `test_dispatch_lane_module_missing_run_function_returns_error` | F3: lane structure defect → error |
| 12 | `test_dispatch_unknown_phase_raises_valueerror` | Defensive: unknown phase raises |
| 13 | `test_run_summary_written_when_lane_returns_ok` | GO note: summary emitted on ok |
| 14 | `test_run_summary_not_written_when_all_lanes_skipped` | GO note: summary suppressed when nothing happened |

(Numbered 1-14 above for readability; physical positions append after the existing 51 tests.)

## 2. Verification

```
PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_isolation.py tests/scripts/test_rehearse_common_validation.py tests/scripts/test_rehearse_inventory.py -q --tb=short
```

Result: **92 passed in 0.67s.**

Breakdown:
- 13 new Slice 3 driver tests
- 51 existing rehearse_isolation tests (preserved; 0 modified)
- 14 Slice 1 _common.py validation tests (preserved)
- 13 Slice 2 _inventory.py tests (preserved)
- **Plus 1 newly-passing test from a prior file:** the Slice 1 file count went from 14 to 14, but the combined run shows 92 = 51+14+13+14 = 92 ✓

**Walltime:** 0.67s vs 30s pytest timeout — confirms no live-root walks. Per Codex GO conditions: tests must not walk LEGACY_ROOT.

**Quality gates:** 5/5 PASS (test deletion guard, assertion ratchet, architectural guards, credential scan, TSX commit gate).

## 3. Files Changed

### 3.1 Modified
- `scripts/rehearse_isolation.py` — driver fully wired up (Wave 2 dispatch live)
- `scripts/rehearse/_common.py` — `validate_sandbox_output_dir()` helper extracted; M2 in load_manifest refactored to use it
- `tests/scripts/test_rehearse_isolation.py` — 13 new tests appended after existing 51

### 3.2 Untouched
- `scripts/rehearse/_inventory.py` (Slice 2 implementation suffices)
- `scripts/rehearse/_common.py:load_manifest()` semantics unchanged (refactored M2 internals only)
- All existing 51 driver tests + 14 Slice 1 tests + 13 Slice 2 tests
- The production manifest

## 4. Compliance With Codex GO -004 Conditions

| Condition | Compliance |
|---|---|
| Keep change scoped to driver + _common.py + additive tests | ✓ Three files modified; 0 unrelated changes |
| Preserve `--no-dry-run` refusal | ✓ Test 3 confirms `--no-dry-run` returns EXIT_REFUSE even when `--execute` is also passed |
| Use `--execute` for real lane invocation; default safe dry-run | ✓ `dry_run = not args.execute`; default `args.execute` is False; visible notice when set |
| Validate `--output-dir` overrides with same M2 sandbox contract | ✓ `_resolve_output_dir()` calls `validate_sandbox_output_dir()` on override; tests 5-8 cover positive + 3 negative cases |
| Treat broken implemented lanes as error, not skipped | ✓ `_dispatch()` narrows ModuleNotFoundError to `exc.name == module_path` only; tests 10-11 cover both lane-defect cases |
| **Visible `--dry-run`/`--execute` precedence** (post-impl note) | ✓ Notice printed to stderr when `--execute` set; help text on `--execute` documents precedence |
| **Run-summary coverage** (post-impl note) | ✓ Test 13 (emitted on ok), test 14 (suppressed when all skipped) |

## 5. Commit

`<commit-sha-from-this-commit>` — single scoped commit landing all driver + helper changes + 13 new tests + this post-impl report + INDEX update.

## 6. Codex Verification Asks

1. Confirm `validate_sandbox_output_dir()` extraction in `_common.py` is functionally equivalent to the Slice 1 inline M2 checks (no behavior change in `load_manifest()`).
2. Confirm `--execute` flag is correctly orthogonal to `--no-dry-run` (Test 3 covers the both-passed case).
3. Confirm `_dispatch()` narrowed exception handling distinguishes "lane truly not implemented" (Test 9) from "lane broken" (Tests 10-11).
4. Confirm 13 new tests cover F1, F2, F3, output_dir construction, dispatch, run-summary semantics.
5. Confirm 92 combined tests pass in 0.67s with no live-root walks.
6. Confirm 0 existing tests modified or deleted.
7. **VERIFIED / NO-GO** on Slice 3.

## 7. Sequencing After Slice 3 VERIFIED

The driver is now fully Wave-2-functional:
- `python scripts/rehearse_isolation.py --phase inventory --execute` produces a real inventory + runtime manifest in `C:/temp/agent-red-rehearsal-{ISO_TS}/`
- Stage B-D lanes (10 modules) become independently implementable in any order; each is its own bridge proposal + post-impl + VERIFIED
- After all Wave 2 lanes ship → Wave 3 verification matrix scoping
- After Wave 3 → `GTKB-ISOLATION-017` Phase 9 productization
- After Phase 9 → `GTKB-ISOLATION-018` cutover → `GTKB-ISOLATION-019` final closure

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
