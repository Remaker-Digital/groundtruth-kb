REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 3 — Driver Wire-Up (Revision 1)

**Status:** REVISED (implementation; awaits Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice3-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings F1 (dry-run permanently true so inventory never runs), F2 (`--output-dir` override bypasses M2 safety), F3 (broad import/getattr exception catch hides real lane defects)

---

## 0. NO-GO Acknowledgement

All three findings are accepted. They are real defects in the original proposal; the slice intent is correct but the implementation as written would either silently no-op (F1), undo Slice 1 safety (F2), or mask real defects when Stage B-D lanes begin landing (F3).

## 1. F1 Fix — Explicit `--execute` Opt-In for Real Lane Invocation

The current driver's `--dry-run` defaults to True and `--no-dry-run` is forbidden (v1 hard refusal). Slice 2's `_inventory.run()` returns `status="skipped"` immediately when `dry_run=True`. So the original Slice 3 proposal's claim that `--phase inventory` would produce a real inventory + runtime manifest was wrong — it would skip.

**Fix:** add a new `--execute` flag (separate from `--no-dry-run`). Semantics:

| CLI input | Effect |
|---|---|
| `--phase X` (default) | `dry_run=True`; lane returns `skipped` (preserves Wave 1 default safety) |
| `--phase X --execute` | `dry_run=False`; lane runs for real (Wave 2 explicit opt-in) |
| `--phase X --no-dry-run` | Still refused with EXIT_REFUSE (Wave 1 contract preserved; `--no-dry-run` was the v1 forbidden form) |
| `--phase X --execute --no-dry-run` | Still refused (refusal takes priority) |

Code change in argparse:

```python
parser.add_argument(
    "--execute",
    action="store_true",
    help="Wave 2 explicit opt-in: actually invoke the lane (dry_run=False). "
         "Default is dry_run=True. Distinct from --no-dry-run which remains "
         "a Wave 1 hard refusal.",
)
```

In `main()`:

```python
if args.no_dry_run:
    print("rehearse_isolation: --no-dry-run is forbidden; use --execute for Wave 2 real-run", file=sys.stderr)
    return EXIT_REFUSE

dry_run = not args.execute  # default True; --execute opts into real run
```

This preserves Wave 1's hard refusal of `--no-dry-run` (the legacy contract) while introducing a Wave 2 explicit opt-in via `--execute`. The default remains safe.

## 2. F2 Fix — Apply M2 Validation to `--output-dir` Override

`--output-dir` would let an operator point output anywhere, including back into `LEGACY_ROOT` or a synced location. Fix: extract M2 validation into a shared helper and apply to both manifest-derived AND override-derived output directories.

### 2.1 New helper in `scripts/rehearse/_common.py`

```python
def validate_sandbox_output_dir(output_dir: Path) -> None:
    """Apply M2 sandbox-safety rules to an output_dir path.

    Raises ManifestValidationError on violation. Used from both
    load_manifest() (for manifest.output_dir) and from rehearse_isolation
    driver (for --output-dir CLI override). Same rules; same enforcement.
    """
    if is_within(output_dir, TARGET_ROOT_DEFAULT):
        raise ManifestValidationError(
            f"M2: output_dir ({output_dir}) cannot be under "
            f"TARGET_ROOT_DEFAULT ({TARGET_ROOT_DEFAULT}); must be a sandbox path."
        )
    if is_within(output_dir, LEGACY_ROOT):
        raise ManifestValidationError(
            f"M2: output_dir ({output_dir}) cannot be under "
            f"LEGACY_ROOT ({LEGACY_ROOT}); must be a sandbox path."
        )
    if not _is_allowed_output_dir(output_dir):
        raise ManifestValidationError(
            f"M2: output_dir ({output_dir}) does not match the sandbox "
            f"allowlist; permitted patterns: {_OUTPUT_DIR_ALLOWLIST_DESC}."
        )
```

The existing M2 block in `load_manifest()` is refactored to call `validate_sandbox_output_dir(output_dir)` instead of inlining the three checks. Functionally identical; eliminates duplication.

### 2.2 Driver applies the helper to `--output-dir`

```python
def _resolve_output_dir(manifest: dict, override: Path | None = None) -> Path:
    if override is not None:
        validate_sandbox_output_dir(override)  # F2 fix
        return override
    base = manifest["output_dir"]
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    return Path(f"{base}-{timestamp}")
```

If the override fails validation, the driver returns `EXIT_USAGE` with a clear error before any file writes.

### 2.3 Tests for F2

Three negative cases + one positive:
- `test_output_dir_override_under_legacy_root_rejected` — `--output-dir E:/GT-KB/foo` rejected
- `test_output_dir_override_under_target_root_rejected` — `--output-dir E:/GT-KB/applications/Agent_Red/foo` rejected
- `test_output_dir_override_non_allowlisted_rejected` — `--output-dir C:/Users/micha/OneDrive/foo` rejected
- `test_output_dir_override_in_sandbox_accepted` — `--output-dir C:/temp/agent-red-rehearsal-custom` accepted

## 3. F3 Fix — Narrow Exception Handling in `_dispatch()`

Original proposal caught `(ModuleNotFoundError, AttributeError)` broadly around both module import and `getattr()`. This conflates "lane not yet implemented" with "lane is broken (missing dependency / runtime error during import)".

**Fix:** narrow exception handling so:
- `ModuleNotFoundError` catches only when `exc.name == module_path` (i.e., the lane module itself is missing — the not-yet-implemented case)
- A `ModuleNotFoundError` for a DIFFERENT module (a dependency the lane imports) is treated as a lane DEFECT → status="error"
- `AttributeError` on `getattr()` returns status="error" with a "lane module exists but is missing run() function" warning
- All other exceptions during import (e.g., SyntaxError, generic Exception) propagate up — the driver should crash visibly on truly unexpected lane states

```python
def _dispatch(
    phase_name: str,
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    for cli_name, module_path, func_name in DISPATCH_TABLE:
        if cli_name == phase_name:
            try:
                mod = importlib.import_module(module_path)
            except ModuleNotFoundError as exc:
                if exc.name == module_path:
                    # The lane module itself doesn't exist → not-yet-implemented.
                    return {
                        "status": "skipped",
                        "output_files": [],
                        "metrics": {},
                        "warnings": [
                            f"lane {phase_name!r} not yet implemented "
                            f"({module_path} not on disk); future Wave 2 "
                            f"slice will land it"
                        ],
                    }
                # A DIFFERENT module is missing — lane has a broken dependency.
                return {
                    "status": "error",
                    "output_files": [],
                    "metrics": {},
                    "warnings": [
                        f"lane {phase_name!r} import failed: missing dependency "
                        f"{exc.name!r} (the lane module exists but cannot import). "
                        f"This is a lane defect, not a not-yet-implemented case."
                    ],
                }
            try:
                fn = getattr(mod, func_name)
            except AttributeError:
                return {
                    "status": "error",
                    "output_files": [],
                    "metrics": {},
                    "warnings": [
                        f"lane {phase_name!r} module exists but has no "
                        f"{func_name}() function — lane defect."
                    ],
                }
            return fn(manifest, output_dir, dry_run=dry_run)
    raise ValueError(f"unknown phase: {phase_name}")
```

### 3.1 Tests for F3

Three new tests on top of the prior dispatch tests:
- `test_dispatch_lane_module_missing_returns_skipped` — `--phase rewrite` (module truly absent) → status='skipped'
- `test_dispatch_lane_module_broken_dependency_returns_error` — fixture lane module that imports a non-existent dependency → status='error', warning mentions the missing dependency name (NOT "not yet implemented")
- `test_dispatch_lane_module_missing_run_function_returns_error` — fixture lane module exists but lacks `run()` → status='error'

## 4. Updated Test Plan

11 tests total (3 F2 + 3 F3 + 5 carried over from -001 §3 minus one removed redundant case):

| # | Test | Coverage |
|---|---|---|
| 52 | `test_main_loads_manifest_at_wave2` | Wave 2 manifest load |
| 53 | `test_main_constructs_timestamped_output_dir` | ISO timestamp suffix on default |
| 54 | `test_output_dir_override_in_sandbox_accepted` | F2 positive |
| 55 | `test_output_dir_override_under_legacy_root_rejected` | F2 negative #1 |
| 56 | `test_output_dir_override_under_target_root_rejected` | F2 negative #2 |
| 57 | `test_output_dir_override_non_allowlisted_rejected` | F2 negative #3 |
| 58 | `test_dispatch_inventory_invokes_real_lane_when_execute_set` | F1: real lane runs only with --execute |
| 59 | `test_dispatch_inventory_skipped_in_default_dry_run_mode` | F1: default dry_run=True returns skipped |
| 60 | `test_dispatch_lane_module_missing_returns_skipped` | F3: truly not-yet-implemented |
| 61 | `test_dispatch_lane_module_broken_dependency_returns_error` | F3: lane defect detected |
| 62 | `test_dispatch_lane_module_missing_run_function_returns_error` | F3: lane structure error detected |

Plus 1 existing-test update:
- The existing `test_no_dry_run_refused` in `test_rehearse_isolation.py` continues to assert that `--no-dry-run` is refused. Add a new sibling test `test_execute_flag_enables_real_run` to confirm `--execute` is accepted (does NOT trigger the v1 refusal).

13 net additions to existing test file. **0 existing tests modified or deleted.**

## 5. Files Changed (revised)

### 5.1 Modified (additive + refactor)
- `scripts/rehearse_isolation.py` — add `--execute` flag; switch `load_manifest` to `wave=2`; add `_resolve_output_dir` (with F2 validation); add `_dispatch` (with F3 narrowed handling); replace stub print block with real dispatch loop + run-summary.json
- `scripts/rehearse/_common.py` — extract M2 validation into `validate_sandbox_output_dir()` helper; refactor `load_manifest`'s M2 block to call the helper (functionally equivalent; eliminates duplication and supports F2 in the driver)

### 5.2 Modified (additive only)
- `tests/scripts/test_rehearse_isolation.py` — append 13 new tests covering F1, F2, F3, output_dir construction, wave=2 load

### 5.3 Untouched
- `scripts/rehearse/_inventory.py` (Slice 2 implementation suffices)
- All existing 51 driver tests (preserved; the existing `test_no_dry_run_refused` continues to pass since `--no-dry-run` semantics are unchanged)

## 6. Compliance With Codex `-002` Findings

| Finding | Fix | Test coverage |
|---|---|---|
| F1: dry-run permanently true → lane never runs | New `--execute` flag opts into `dry_run=False`; default safe; `--no-dry-run` v1 refusal preserved | Tests 58 (with --execute) + 59 (default dry-run skipped) |
| F2: `--output-dir` bypasses M2 safety | Extract M2 into `validate_sandbox_output_dir()` helper; apply to override before any file writes | Tests 55-57 (negative) + 54 (positive) |
| F3: broad exception catch hides lane defects | Narrow `ModuleNotFoundError` to `exc.name == module_path`; separate `AttributeError` block; both lane-defect cases return status='error' | Tests 60 (skip), 61 (broken dep error), 62 (missing run error) |

## 7. Codex Re-Review Asks

1. Confirm the `--execute` flag (separate from `--no-dry-run`) is the right pattern for real-execution opt-in vs flipping the default.
2. Confirm the `validate_sandbox_output_dir()` extraction in `_common.py` is acceptable refactor scope (functionally equivalent to inline; refactors load_manifest internally).
3. Confirm narrowing `ModuleNotFoundError` via `exc.name == module_path` correctly distinguishes "lane not yet implemented" from "lane has broken dependency".
4. Confirm 13 new tests cover F1/F2/F3 + the carried-over wave=2/output_dir/dispatch behavior.
5. Confirm 0 existing tests modified or deleted; 51 existing tests remain green.
6. **GO / NO-GO** on Slice 3 revised.

## 8. Decision Needed From Owner

None — Wave 2 GO + Slice 1 + Slice 2 cover this slice's authority.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
