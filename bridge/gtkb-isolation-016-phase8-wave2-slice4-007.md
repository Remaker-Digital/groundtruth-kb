REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 4 — Post-Implementation Report (Revision 1)

**Status:** REVISED (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice4-005.md` (NO-GO at `-006`)
**Addresses:** Codex `-006` blocking findings F1 (focused quality gates) + F2 (`result.json` artifact missing)

---

## 0. NO-GO Acknowledgement

Codex `-006` identified two real defects:

1. **F1 — Blocking:** Focused quality gates fail. `python -m ruff check` reported 5 issues (4× I001 import-block sort/format, 1× F401 unused `LEGACY_ROOT` import in test file). `python -m ruff format --check` reported 3 files would be reformatted. The pre-commit gate's broad checks pass, but the file-focused gates that match what CI runs do not. Verification cannot pass until the focused gates are clean.
2. **F2 — Blocking:** Approved output contract omits `result.json`. Wave 2 -003 §4.2 + umbrella -001 §4.2 explicitly require `{output_dir}/{module_short_name}/result.json` containing the structured result returned by `run()`. The implementation wrote `classification.json`, `path_rewrite.json`, and `git_filter_args.txt` but not `result.json`, and `output_files` did not include it. Contract drift between approved design and operator-facing artifacts.

Both findings are accepted in full. Fixes below.

## 1. Fix 1 — Focused quality gates clean

Applied `python -m ruff check --fix` and `python -m ruff format` to the three files. Re-verified:

```bash
$ python -m ruff check scripts/rehearse/_path_rewrite.py \
    tests/scripts/test_rehearse_path_rewrite.py \
    tests/scripts/test_rehearse_isolation.py
All checks passed!

$ python -m ruff format --check scripts/rehearse/_path_rewrite.py \
    tests/scripts/test_rehearse_path_rewrite.py \
    tests/scripts/test_rehearse_isolation.py
3 files already formatted
```

Specific changes:
- `scripts/rehearse/_path_rewrite.py`: imports re-sorted; line-length wrapping normalized (notably the `_compose_git_filter_args()` join expression and several long error-warning strings)
- `tests/scripts/test_rehearse_path_rewrite.py`: imports re-sorted; `LEGACY_ROOT` import removed (was unused — F401); long lines wrapped
- `tests/scripts/test_rehearse_isolation.py`: imports re-sorted in the second import block (line 217-219); long-line normalization in the new Slice 4 driver test

No semantic changes. The unused `LEGACY_ROOT` removal is a side-effect of the original test file accidentally importing the constant without ever using it (I used `tmp_path` for all path construction).

## 2. Fix 2 — `result.json` artifact added

### 2.1 Implementation change

Added `_emit_result(lane_dir, result)` helper to `_path_rewrite.py`:

```python
def _emit_result(lane_dir: Path, result: dict[str, Any]) -> dict[str, Any]:
    """Write the structured result to ``{lane_dir}/result.json``.

    Per Wave 2 -003 §4.2 + umbrella -001 §4.2 common contract: each
    sub-script writes ``result.json`` under its lane dir containing the
    structured result returned by ``run()``. Per slice4 NO-GO ``-006`` F2:
    the post-impl must include this artifact and list it in
    ``output_files``.

    Mutates ``result["output_files"]`` to append the result.json path
    BEFORE serialization, so result.json's content correctly references
    its own path. Returns the (now-augmented) result dict for the caller
    to ``return``.
    """
    result_path = lane_dir / "result.json"
    result["output_files"] = [*result["output_files"], str(result_path)]
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
```

Wrapped all 5 non-dry-run returns in `run()` with `_emit_result(lane_dir, ...)`:

| Return path | Status |
|---|---|
| OSError on subprocess spawn | error → `_emit_result()` |
| Non-zero subprocess exit | error → `_emit_result()` |
| Zero-exit + no classification.json (GO -004 condition 2) | error → `_emit_result()` |
| Classification JSON unreadable | error → `_emit_result()` |
| Classification rows missing/malformed | error → `_emit_result()` |
| Happy path | ok → `_emit_result()` |

The dry-run path is intentionally unwrapped: nothing was executed, no result to capture. `output_files` remains empty for dry-run, matching the existing `test_run_dry_run_returns_skipped` assertion.

### 2.2 Self-reference in `result.json`

`_emit_result()` mutates `result["output_files"]` to include the `result.json` path itself BEFORE serialization. So the on-disk `result.json` content correctly lists itself in `output_files`. This makes the artifact self-describing and matches the structural intent of "result.json contains the returned result dict."

### 2.3 Two new tests

Added between T12 and T13 in `tests/scripts/test_rehearse_path_rewrite.py`:

| Test | Purpose |
|---|---|
| `test_run_writes_result_json_containing_returned_dict` | Happy path: result.json exists at `{output_dir}/path_rewrite/result.json`, content equals the returned dict (incl. self-reference in output_files), status="ok" |
| `test_run_writes_result_json_on_error_path` | Error path (mocked non-zero subprocess exit): result.json still written for operator forensics, status="error", warnings include the original error string |

## 3. Updated Test Count

Pre-revision: 19 unit tests (path_rewrite) + 1 driver integration = 20 Slice 4 tests
Post-revision: 21 unit tests (path_rewrite, +2 result.json) + 1 driver integration = 22 Slice 4 tests

Combined run total: 112 → **114 tests, 2.66s walltime, 0 failures.**

## 4. Verification

```bash
$ PYTHONIOENCODING=utf-8 python -m pytest \
    tests/scripts/test_rehearse_path_rewrite.py \
    tests/scripts/test_rehearse_isolation.py \
    tests/scripts/test_rehearse_inventory.py \
    tests/scripts/test_rehearse_common_validation.py \
    -q --tb=short

114 passed in 2.66s
```

Breakdown:
- 21 path_rewrite tests (19 from -005 + 2 new result.json tests)
- 66 rehearse_isolation tests (preserved)
- 13 inventory tests (preserved)
- 14 common_validation tests (preserved)

Focused quality gates:

```bash
$ python -m ruff check ...      # All checks passed!
$ python -m ruff format --check ... # 3 files already formatted
```

## 5. Files Changed (this REVISED commit)

### 5.1 Modified
- `scripts/rehearse/_path_rewrite.py` — added `_emit_result()` helper; wrapped 6 non-dry-run returns; ruff format applied
- `tests/scripts/test_rehearse_path_rewrite.py` — added 2 new result.json tests; removed unused LEGACY_ROOT import; ruff format applied
- `tests/scripts/test_rehearse_isolation.py` — ruff format applied to imports + Slice 4 driver test (no semantic changes)

### 5.2 Bridge artifacts
- `bridge/gtkb-isolation-016-phase8-wave2-slice4-006.md` (Codex NO-GO; tracked from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice4-007.md` (this file, REVISED)
- `bridge/INDEX.md` — REVISED line at top of slice4 entry

### 5.3 Untouched
- `scripts/rehearse_isolation.py`
- `scripts/rehearse/_common.py`
- `scripts/rehearse/_inventory.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`

## 6. Compliance With Codex `-006` Recommended Actions

| Action | Compliance |
|---|---|
| 1. `ruff check --fix` and `ruff format` (or equivalent), then rerun focused gates | ✓ Both gates clean post-fix |
| 2. Write `{output_dir}/path_rewrite/result.json` for non-dry-run executions; include in `output_files`; test asserts file exists and contains structured result | ✓ `_emit_result()` writes it; `output_files` includes it; 2 tests assert existence + content equality + self-reference |
| 3. Rerun the 112-test pytest target and the focused ruff gates | ✓ 114 tests pass (was 112 + 2 new); ruff clean |

## 7. Codex Verification Asks

1. Confirm focused `ruff check` and `ruff format --check` are now clean for the three files.
2. Confirm `_emit_result()` correctly handles all 6 non-dry-run return paths (1 happy + 5 error).
3. Confirm result.json self-reference (output_files includes the result.json path) is the right shape for the contract.
4. Confirm 2 new tests (Test 12a + 12b) cover both ok + error paths for result.json artifact.
5. Confirm 114-test result with 2.66s runtime indicates no regression.
6. **VERIFIED / NO-GO** on Slice 4 post-impl.

## 8. Sequencing After Slice 4 VERIFIED

Unchanged from `-005` §7. Next slice candidate: **Slice 5 cluster** of 3 split-pattern lanes (`_bridge_split.py` + `_backlog_split.py` + `_release_readiness_split.py`).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
