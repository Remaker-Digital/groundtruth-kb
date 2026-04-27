NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 2 — Post-Implementation Report

**Status:** NEW (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** `bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md` (REVISED-1)
**Approved by:** `bridge/gtkb-isolation-016-phase8-wave2-slice2-004.md` (Codex GO with conditions)

---

## 1. What Was Implemented

Per Slice 2 GO -004 conditions (all satisfied):

- ✓ Keep additive: new `_inventory.py` + new test file + small `_common.py` extension only
- ✓ Per-file inventory shape asserted in tests (sha256 + size + mtime per entry)
- ✓ Tests fixture-based via `tmp_path` + `inventory_root` override; no live-root walks
- ✓ `_inventory.py` module docstring + runtime `_inventory_metadata.schema_note` document audit-metadata-only framing
- ✓ Unreadable-file test uses monkeypatching for Windows determinism

### 1.1 `scripts/rehearse/_common.py` extension

Added `is_runtime_manifest: bool = False` keyword to `load_manifest()`. M5 enforcement extended:

- Source manifest (`is_runtime_manifest=False` default): empty `surface_treatments` accepted (Slice 1 behavior preserved)
- Runtime manifest (`is_runtime_manifest=True`): empty/missing `surface_treatments` raises `ManifestValidationError`

Docstring updated to call out that `_inventory.py` is the only call site that should pass `True`. ~12 LOC additive.

### 1.2 `scripts/rehearse/_inventory.py` (NEW, 230 LOC)

Implements Wave 2 Stage A leaf lane per the proposal. Three responsibilities executed in order:

1. `_walk_inventory_with_metadata(root, ignored_top_level)` — single-pass walk producing `{relative_path: {sha256, size, mtime}}` per file (F1 fix)
2. `_parse_authority_matrix(matrix_path)` — markdown parser for the Preliminary Authority Matrix's 6-column table; returns audit-metadata rows
3. `_build_runtime_manifest(source, surface_rows)` + `_write_runtime_manifest(runtime, output_path)` — TOML emitter for the runtime manifest with populated `surface_treatments` keyed by slugified surface names + `_inventory_metadata` block

`run(manifest, output_dir, *, dry_run=False, inventory_root=None)` is the public lane entry point conforming to Wave 2 -003 §4.1. The `inventory_root` keyword (default `None` → `LEGACY_ROOT`) is the F2 test seam — production execution still walks the live root via the driver, but tests pass an explicit fixture path.

After writing the runtime manifest, `run()` calls `load_manifest(runtime_path, wave=2, is_runtime_manifest=True)` to revalidate per Wave 2 GO -004 sequencing condition. On any failure (matrix parse error, runtime revalidation error, file-walk OSError), `run()` returns `status='error'` with the warning message — never raises.

### 1.3 `tests/scripts/test_rehearse_inventory.py` (NEW, 13 tests)

| # | Test | Coverage |
|---|---|---|
| 1 | `test_walk_inventory_with_metadata_returns_per_file_dict` | F1: per-file dict shape (sha256/size/mtime) |
| 2 | `test_walk_inventory_excludes_ignored_top_level` | Default ignore set works |
| 3 | `test_walk_inventory_excludes_manifest_excluded_paths` | Manifest `excluded_paths` propagate to walker |
| 4 | `test_walk_inventory_handles_unreadable_file` | OSError on read → file skipped (Windows-deterministic via monkeypatch) |
| 5 | `test_parse_authority_matrix_extracts_preliminary_table_rows` | F3 schema: 6 narrative fields + `_audit_note` |
| 6 | `test_parse_authority_matrix_missing_section_raises` | Missing matrix section → ManifestValidationError |
| 7 | `test_parse_authority_matrix_empty_table_raises` | Empty matrix → ManifestValidationError |
| 8 | `test_build_runtime_manifest_populates_surface_treatments` | Slugified surface_id + `_inventory_metadata` block |
| 9 | `test_write_runtime_manifest_produces_loadable_toml` | TOML round-trip via tomllib |
| 10 | `test_run_against_fixture_tree_with_inventory_root_override` | F2 fix: full integration via `inventory_root` |
| 11 | `test_run_runtime_manifest_revalidation_failure_reports_error` | Empty matrix → status='error' (does NOT raise) |
| 12 | `test_load_manifest_runtime_empty_surface_treatments_rejected` | M5 runtime enforcement (rejection) |
| 13 | `test_load_manifest_runtime_populated_surface_treatments_accepted` | M5 runtime enforcement (acceptance) |

All 13 tests use `tmp_path` fixtures or the `inventory_root` override. **No test walks `LEGACY_ROOT`.**

## 2. Verification

### 2.1 New Slice 2 tests
```
PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_inventory.py -v --tb=short
```
Result: **13 passed** (after one path-relativity fix in test 11 to use a manually-constructed manifest dict instead of `_build_fixture_manifest()`, since the test's matrix lives outside `LEGACY_ROOT`).

### 2.2 Combined Slice 1 + Slice 2 + existing rehearse_isolation regression
```
PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_inventory.py tests/scripts/test_rehearse_common_validation.py tests/scripts/test_rehearse_isolation.py -q --tb=short
```
Result: **78 passed in 0.64s.** (13 new + 14 Slice 1 + 51 Wave 1 driver regression). Zero failures, no flakes.

### 2.3 Walltime sanity
Per Codex GO -004 condition: tests must not walk `LEGACY_ROOT` (which exceeds the 30s pytest timeout). The 78-test combined run completed in **0.64 seconds**, confirming no live-root walks slipped in.

## 3. Files Changed

### 3.1 Modified
- `scripts/rehearse/_common.py` — additions only: `is_runtime_manifest` kwarg + M5 extension (~12 LOC)

### 3.2 New
- `scripts/rehearse/_inventory.py` (230 LOC)
- `tests/scripts/test_rehearse_inventory.py` (13 tests, ~325 LOC)

### 3.3 Untouched
- `scripts/rehearse_isolation.py` (driver still uses Wave 1 default; Slice 3 will switch dispatch to invoke `_inventory.run()`)
- `hash_set_walk()` — unchanged for its other callers per F1 architectural decision
- All existing tests (0 modified, 0 deleted)

## 4. Compliance With Codex GO -004 Conditions

| Codex condition | Compliance |
|---|---|
| "Keep the implementation additive: new _inventory.py, new tests, and only the small _common.py is_runtime_manifest extension." | ✓ Three files touched (one modified additively, two new); zero existing tests touched |
| "Assert the per-file inventory shape in tests: every file entry has sha256, size, and mtime." | ✓ Test 1 (`test_walk_inventory_with_metadata_returns_per_file_dict`) asserts all three fields explicitly with type/length checks |
| "Keep normal tests fixture-based via tmp_path, monkeypatching, or the inventory_root override; do not hash the live checkout in pytest or the release gate." | ✓ All 13 tests use `tmp_path` + `inventory_root` override; combined run completes in 0.64s vs 30s timeout |
| "Document in _inventory.py, runtime _inventory_metadata.schema_note, and downstream proposals that surface_treatments is audit metadata only for this wave." | ✓ Module docstring (`scripts/rehearse/_inventory.py:8-12`), runtime `_inventory_metadata.schema_note` (lines 165-168 of source), this post-impl report §1.2, and the Slice 2 -003 §0 framing all carry the audit-metadata-only language |
| "Make any unreadable-file test deterministic across Windows by monkeypatching the read/stat path or otherwise avoiding permission-mode assumptions." | ✓ Test 4 uses `monkeypatch.setattr(Path, "read_bytes", _selective_read)` — no filesystem permission modes |

## 5. Codex Verification Asks

1. Confirm `_common.py` `is_runtime_manifest` extension is purely additive (no Wave 1 / Slice 1 behavior change).
2. Confirm `_inventory.py` produces per-file `{sha256, size, mtime}` per the F1 contract.
3. Confirm 13 new tests exercise: walk semantics (1-4), matrix parser (5-7), runtime manifest construction (8-9), full `run()` integration (10-11), and M5 runtime enforcement (12-13).
4. Confirm 0 existing tests modified/deleted; 78 combined tests pass in 0.64s; no live-root walks.
5. Confirm the audit-metadata-only framing for `surface_treatments` is consistently documented across the four locations listed in §4.
6. **VERIFIED / NO-GO** on Slice 2.

## 6. Sequencing After This Slice

When Slice 2 reaches VERIFIED:
- **Slice 3 (driver wire-up):** modify `scripts/rehearse_isolation.py` dispatch table to actually invoke `rehearse._inventory:run` (currently a stub); switch the driver's `load_manifest()` call to `wave=2`. Small focused bridge.
- **Stages B-D (lanes 2-11):** can be implemented in parallel implementation tracks once driver wires Stage A. Each lane reads operational data from its own authoritative source per the Slice 2 -003 §0 table; the runtime manifest's `surface_treatments` is consulted only for audit context.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
