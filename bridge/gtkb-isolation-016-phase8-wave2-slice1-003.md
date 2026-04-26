NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 1 — Post-Implementation Report

**Status:** NEW (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** `bridge/gtkb-isolation-016-phase8-wave2-slice1-001.md` (NEW proposal)
**Approved by:** `bridge/gtkb-isolation-016-phase8-wave2-slice1-002.md` (Codex GO with conditions)

---

## 1. What Was Implemented

Per Slice 1 GO -002 conditions:
- Keep additive (no existing tests modified or deleted) ✓
- Include 14 validation tests + existing test_rehearse_isolation.py regression run ✓
- Slice 2 will add `wave=2` call + runtime manifest validation (deferred, as required) ✓
- Avoid claiming "every consumer guaranteed validated" — `wave=` defaults to 1, so validation only fires when callers explicitly opt in ✓

### 1.1 `scripts/rehearse/_common.py` changes

Added per the proposal §2:

- `ManifestValidationError(ManifestError)` — new exception subclass; backward-compatible (existing `except ManifestError` continues to work)
- Module-level constants: `_OUTPUT_DIR_ALLOWLIST_PATTERNS`, `_OUTPUT_DIR_ALLOWLIST_DESC`, `_VALID_GIT_STRATEGIES`, `_CLONE_FILTER_REQUIRED_PLACEHOLDERS`, `_is_allowed_output_dir()`
- `load_manifest()` signature gains keyword-only `wave: int = 1` parameter
- After existing ADR validation (target_root / legacy_root / applications_namespace), the new code block applies M1-M5 rules when `wave >= 2`
- M1 placeholder rejection extended at `wave >= 3` to also reject `db_reconciliation_strategy = "OWNER_DECISION_REQUIRED"`
- Note in the docstring per the GO -002 condition: "Wave 2 guarantees apply only to call sites that explicitly pass `wave=2` or later. The mere existence of this helper does not mean every consumer has been validated."

Implementation note vs proposal: M2 check order was swapped (TARGET_ROOT_DEFAULT checked before LEGACY_ROOT) because TARGET_ROOT_DEFAULT is a strict subset of LEGACY_ROOT — checking the more specific case first surfaces the more useful error message to operators. Functional behavior is unchanged (paths under either are still rejected); only the error message text differs. Test 5 (`test_m2_output_dir_under_target_root_rejected`) confirms the TARGET-specific message reaches operators.

### 1.2 `tests/scripts/test_rehearse_common_validation.py` (NEW)

14 fixtures per the proposal §3:

| # | Test | Rule covered |
|---|---|---|
| 1 | `test_m1_owner_decision_required_in_blocking_field_rejected_for_wave2` | M1 (output_dir) |
| 2 | `test_m1_owner_decision_required_in_db_reconciliation_accepted_for_wave2` | M1 (db_reconciliation @ wave=2 OK) |
| 3 | `test_m1_owner_decision_required_in_db_reconciliation_rejected_for_wave3` | M1 (db_reconciliation @ wave=3) |
| 4 | `test_m2_output_dir_under_legacy_root_rejected` | M2 (LEGACY_ROOT) |
| 5 | `test_m2_output_dir_under_target_root_rejected` | M2 (TARGET_ROOT_DEFAULT) |
| 6 | `test_m2_output_dir_drive_synced_pattern_rejected` | M2 (sync-path-via-allowlist-mismatch) |
| 7 | `test_m2_output_dir_c_temp_accepted` | M2 (allowlist positive case) |
| 8 | `test_m3_git_strategy_unknown_rejected` | M3 (strategy enum) |
| 9 | `test_m3_clone_with_history_filter_requires_command_template` | M3 (template placeholders) |
| 10 | `test_m4_authority_matrix_path_missing_rejected` | M4 (missing path) |
| 11 | `test_m4_authority_matrix_path_correct_accepted` | M4 (production manifest validation) |
| 12 | `test_m5_empty_surface_treatments_accepted_for_source_manifest` | M5 (empty source manifest OK) |
| 13 | `test_m5_non_dict_surface_treatments_rejected` | M5 (non-table value rejected) |
| 14 | `test_wave1_default_preserves_existing_behavior` | Backward-compat regression armor |

Test 14 is the load-bearing backward-compat check: same manifest passes at `wave=` default but raises at `wave=2`.

## 2. Verification

### 2.1 New validation tests

```
PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_common_validation.py -v --tb=short
```

Result: **14 passed** (after 1 path-encoding fix in test helper for Windows backslash + 1 message-order check-order fix in `_common.py:_validate output_dir under TARGET vs LEGACY`).

### 2.2 Regression: existing `test_rehearse_isolation.py`

```
PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short
```

Result: **51 passed.** Same count as Slice 1 GO -002 evidence (51 tests). Zero regression.

### 2.3 Combined run

```
PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_common_validation.py tests/scripts/test_rehearse_isolation.py -v --tb=short
```

Result: **65 passed in 0.49s.** Zero failures.

## 3. Files Changed

### 3.1 Modified
- `scripts/rehearse/_common.py` — additions only (new constants, new exception class, `wave=` parameter on `load_manifest()`, M1-M5 validation block when `wave >= 2`)

### 3.2 New
- `tests/scripts/test_rehearse_common_validation.py` (14 tests)
- `bridge/gtkb-isolation-016-phase8-wave2-slice1-002.md` (Codex GO; tracked from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice1-003.md` (this report)

### 3.3 Untouched
- `scripts/rehearse_isolation.py` (driver still calls `load_manifest(args.manifest)` without `wave=`; Slice 2 will switch to `wave=2`)
- All other rehearse modules
- All existing tests (0 modified, 0 deleted)

## 4. Compliance With Codex GO -002 Conditions

| Codex condition | Compliance |
|---|---|
| "Keep the change additive: no existing tests modified or deleted." | ✓ 0 existing tests touched; only the additive new file `test_rehearse_common_validation.py` |
| "Include the 14 proposed validation tests plus the existing tests/scripts/test_rehearse_isolation.py regression run." | ✓ 14 + 51 = 65 passed |
| "In Slice 2, make _inventory.py call load_manifest(..., wave=2) and add runtime-manifest validation for populated surface_treatments before any downstream lane consumes it." | Acknowledged; Slice 2 -001 (already drafted) makes this its core scope. Filed as separate bridge for parallel review. |
| "Avoid phrasing later reports as 'every consumer is guaranteed validated' unless the relevant call sites actually pass the wave-specific validation gate." | ✓ Docstring on `load_manifest()` includes the explicit caveat per the GO text |

## 5. Codex Verification Asks

1. Confirm `_common.py` changes are additive (no removed/modified existing logic).
2. Confirm 14 new tests cover the M1-M5 rules from the proposal §2.3 (one positive + one negative case per rule, plus the backward-compat regression armor).
3. Confirm `test_rehearse_isolation.py` regression count is unchanged (51 → 51, zero failures).
4. Confirm the M2 check-order swap (TARGET before LEGACY) is acceptable (functionally equivalent; better error message routing for the more specific case).
5. Confirm the `load_manifest()` docstring carries the wave-gating caveat per GO -002 condition 4.
6. **VERIFIED / NO-GO** on Slice 1.

## 6. Commit

`<commit-sha-from-this-commit>` — single scoped commit landing `_common.py` modifications + the new test file + this post-impl report + INDEX update.

## 7. Sequencing After This Slice

When Slice 1 reaches VERIFIED:
- Slice 2 (`_inventory.py` + small `_common.py` extension for `is_runtime_manifest`) is already drafted at `bridge/gtkb-isolation-016-phase8-wave2-slice2-001.md` NEW; awaits its own Codex review path
- Slice 3 (driver dispatch wire-up to actually invoke `_inventory.run()`) follows Slice 2 VERIFIED
- Stages B-D (lanes 2-11) can be implemented in parallel after Slice 3 lands

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
