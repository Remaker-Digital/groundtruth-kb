NEW

# GTKB-REHEARSAL-PACKAGE-RUFF-CLEAN — Lint + format clean for the rehearsal package

**Status:** NEW (fix; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Triggered by:** Loyal Opposition findings (S313, owner-forwarded), P2 finding: "ruff check ... reports 7 fixable issues, including unused imports at rehearse_isolation.py (line 33) and test_rehearse_common_validation.py (line 17). ruff format --check would reformat 5 files."

bridge_kind: fix
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/ + scripts/rehearse_isolation.py + tests/scripts/test_rehearse_common_validation.py — mechanical lint/format only

---

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: this fix is a candidate for service-style automation (project-wide ruff gate); for now, the slice fixes the local debt that LO surfaced.
- Slice 4-6 post-impl reports each ran ruff against the *individual slice files only* (`scripts/rehearse/_path_rewrite.py`, etc.). The package-level scan (`scripts/rehearse scripts/rehearse_isolation.py`) was not run as a verification step in those slices — that's how the debt accumulated.

## 1. Scope

Mechanical lint + format clean for the rehearsal package surface area:

- `scripts/rehearse/` (entire directory)
- `scripts/rehearse_isolation.py` (driver)
- `tests/scripts/test_rehearse_common_validation.py` (one test file with stale unused import)

**No behavior changes.** Imports may be reordered, unused imports removed, formatting normalized. Source semantics unchanged.

## 2. Evidence

```
$ python -m ruff check scripts/rehearse scripts/rehearse_isolation.py tests/scripts/test_rehearse_common_validation.py --statistics
4    I001    [*] unsorted-imports
2    F401    [*] unused-import
Found 6 errors.
[*] 6 fixable with the `--fix` option.

$ python -m ruff format --check scripts/rehearse scripts/rehearse_isolation.py
Would reformat: scripts\rehearse\_common.py
Would reformat: scripts\rehearse\_inventory.py
Would reformat: scripts\rehearse_isolation.py
3 files would be reformatted, 6 files already formatted
```

(LO report cited 7 fixable + 5 reformat; my scan returned 6 fixable + 3 reformat. Count drift is normal between scans; the underlying issue category is unchanged. The fix addresses whatever ruff reports at apply time.)

### 2.1 Specific F401 unused imports

- `scripts/rehearse_isolation.py:33` — `hash_set_walk` imported from `rehearse._common`, never referenced in driver body. The driver uses `load_manifest`, `validate_target_root`, `validate_sandbox_output_dir`, but not `hash_set_walk` (which is used inside `_inventory.py` directly).
- `tests/scripts/test_rehearse_common_validation.py:17` — `ManifestError` imported, never referenced. Sibling `ManifestValidationError` is used.

Both are stale-import debt from earlier slice iterations.

### 2.2 I001 unsorted imports

Affects `_common.py:9`, `_inventory.py:18`, `rehearse_isolation.py:30`, `test_rehearse_common_validation.py:15`. Mechanical reorder per ruff's import-section convention (stdlib → third-party → first-party).

### 2.3 ruff format

Three files have minor format drift (likely whitespace / line-break in long argument lists). Mechanical.

## 3. Proposed Change

Run `python -m ruff check scripts/rehearse scripts/rehearse_isolation.py tests/scripts/test_rehearse_common_validation.py --fix`. Then run `python -m ruff format scripts/rehearse scripts/rehearse_isolation.py`. Inspect the diff:

- Verify only the §2-cited issues are touched.
- Verify no semantic changes (no statement reordering beyond import block, no logic shifts).
- Verify the resulting file passes `ruff check` clean.

### 3.1 Anti-creep guard

If `ruff --fix` removes an import that turns out to be a legitimate side-effect import (rare but possible — e.g., a module imported only to register a handler), STOP, file a NO-GO acknowledgment, and propose the explicit removal in a follow-up bridge with side-effect-import preservation. For the cited F401s above, both are confirmed unused (no side-effect contract).

## 4. Test Plan

### 4.1 Pre-fix baseline

`pytest tests/scripts/test_rehearse_common_validation.py tests/scripts/test_rehearse_isolation.py tests/scripts/test_rehearse_inventory.py tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_bridge_split.py tests/scripts/test_rehearse_backlog_split.py tests/scripts/test_rehearse_release_readiness_split.py -q` → **177 passed** (per S312 wrap baseline).

### 4.2 Post-fix verification

Same pytest invocation must still return 177 passed (no behavior regression). Plus:

- `ruff check scripts/rehearse scripts/rehearse_isolation.py tests/scripts/test_rehearse_common_validation.py` → "All checks passed!"
- `ruff format --check scripts/rehearse scripts/rehearse_isolation.py` → "X files already formatted" (no `Would reformat` lines)

### 4.3 New regression guard

Add `tests/scripts/test_rehearse_lint_clean.py` (new) — a single test that runs `ruff check` programmatically against the rehearsal surface area and asserts zero findings. This prevents future drift from re-accumulating debt.

```python
# Sketch:
def test_rehearse_package_passes_ruff_check(repo_root):
    result = subprocess.run(
        ["python", "-m", "ruff", "check", "scripts/rehearse",
         "scripts/rehearse_isolation.py", "tests/scripts/test_rehearse_common_validation.py"],
        cwd=repo_root, capture_output=True, text=True
    )
    assert result.returncode == 0, f"ruff check found issues:\n{result.stdout}"
```

The test runs in the standard pytest collection (~1s walltime when clean).

## 5. Files Changed

### 5.1 MODIFIED (mechanical, by ruff)
- `scripts/rehearse/_common.py` — I001 import sort + format
- `scripts/rehearse/_inventory.py` — I001 import sort + format
- `scripts/rehearse_isolation.py` — I001 import sort + F401 hash_set_walk removal + format
- `tests/scripts/test_rehearse_common_validation.py` — I001 + F401 ManifestError removal

(Other files in `scripts/rehearse/` may also be touched if ruff reports them; the bridge does not pre-list specific changes beyond the §2-cited cases.)

### 5.2 NEW
- `tests/scripts/test_rehearse_lint_clean.py` — drift-prevention regression guard.
- `bridge/gtkb-rehearsal-package-ruff-clean-001.md` (this file).

### 5.3 UNTOUCHED
- All other scripts in `scripts/`.
- All other tests.
- Bridge files.
- Source semantics — verified by re-running 177 rehearsal tests.

## 6. Out of Scope

- Project-wide ruff fix (other directories may have similar debt; explicit scope is rehearsal package only).
- Adding a CI workflow that runs ruff on every commit (would be a separate proposal — `GTKB-GOV-CODE-QUALITY-BASELINE` upstream; see `memory/work_list.md` row 7).
- Changing ruff configuration (`pyproject.toml` `[tool.ruff]`).
- Re-running ruff on `session_self_initialization.py` (separate from this scope; covered in `gtkb-startup-evidence-restoration-001` test plan).

## 7. Codex Review Asks

1. Confirm the §3 mechanical-fix-then-verify approach is acceptable, vs. requiring a hand-authored diff that ruff just happens to match.
2. Confirm the §4.3 regression guard test (subprocess-invoked `ruff check`) is the right shape, vs. importing `ruff` as a library or coupling to `pyproject.toml` only.
3. Confirm the F401 unused-import removals (`hash_set_walk` at `rehearse_isolation.py:33`, `ManifestError` at `test_rehearse_common_validation.py:17`) are genuine — i.e., neither has a side-effect contract that would break.
4. **GO / NO-GO** on this fix.

## 8. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
