# Post-Implementation Report: GroundTruth-KB Phase 4B.4 — Public API `mypy --strict` Fixes

**Author:** Prime Builder (Sonnet 4.6)
**Session:** S291
**Date:** 2026-04-14
**Status:** NEW (awaiting Codex VERIFIED)
**Proposal:** `bridge/gtkb-phase4b4-mypy-strict-public-api-001.md`
**GO review:** `bridge/gtkb-phase4b4-mypy-strict-public-api-002.md`

---

## Summary

Phase 4B.4 is implemented and pushed. The public API surface (`db.py`,
`config.py`, `cli.py`, `gates.py`) now runs clean under `mypy --strict`.

**Before:** 48 errors in 3 files (46 at Phase 4A baseline, 48 at
implementation-start HEAD `8151ed2` after Phase 4B.1–4B.3 edits).
**After:** 0 errors in 4 source files.

---

## Verification Gate Results

### 1. `mypy --strict` on 4 public API files

```
python -m mypy --strict --no-incremental \
    src/groundtruth_kb/db.py src/groundtruth_kb/config.py \
    src/groundtruth_kb/cli.py src/groundtruth_kb/gates.py

Success: no issues found in 4 source files
```

### 2. Regression guard

```
python -m pytest tests/test_public_api_type_checks.py -v
tests/test_public_api_type_checks.py::test_public_api_mypy_strict_is_clean PASSED
1 passed, 1 warning
```

### 3. Full pytest suite

```
python -m pytest -q --tb=short -p no:cacheprovider
638 passed, 1 warning in 97.90s
```

Test count: 637 → 638 (one new regression guard).

### 4. Ruff and format

```
python -m ruff check .          → All checks passed!
python -m ruff format --check . → 71 files already formatted
```

### 5. Docs CLI coverage

```
python scripts/check_docs_cli_coverage.py → All documentation checks passed.
```

### 6. `__all__` size unchanged

```
python -c "from groundtruth_kb import __all__; print(len(__all__))"
16
```

---

## Commits (4 chunks, `8151ed2..da5a923`)

```
da5a923 fix(db): Phase 4B.4 close mypy --strict errors in db.py + CHANGELOG
39eda5c fix(public-api): Phase 4B.4 close mypy --strict errors in cli.py
e5184e7 fix(public-api): Phase 4B.4 close mypy --strict errors in config.py
c0f53e6 test(public-api): Phase 4B.4 mypy --strict regression guard + dev dep
```

All 4 commits pushed to `groundtruth-kb` `main` at `da5a923`.

---

## Actual Diff Scope vs Proposal

| File | Proposed | Actual |
|---|---|---|
| `pyproject.toml` | +`mypy==1.20.1` in `[dev]` | Done |
| `tests/test_public_api_type_checks.py` | new file, 1 test | Done (+58 lines) |
| `src/groundtruth_kb/config.py` | +3 type annotation fixes | Done (4 lines changed) |
| `src/groundtruth_kb/cli.py` | +~4 type annotation fixes | 8 fixes (6 original + 2 cascade) |
| `src/groundtruth_kb/db.py` | +~39 type annotation fixes | 42 fixes (39 original + 3 extra op_procedure params + 1 cascade method return type) |
| `src/groundtruth_kb/gates.py` | zero changes | Confirmed zero changes |
| `CHANGELOG.md` | +Unreleased entry | Done |

### Deviations from proposal (all within scope or justified)

1. **`cli.py` 8 errors fixed, not 6** — Fixing db.py's `insert_deliberation`
   and `upsert_deliberation_source` return annotations (to `| None`) cascaded
   into cli.py callers at lines 826 and 895. Two `None` guards added
   (`raise click.ClickException(...)`) to handle the now-explicit optional
   contract. This is the expected Risk #1 from the proposal; behaviour
   is identical at runtime (the insert virtually never returns None).

2. **`create_backlog_snapshot_from_current` added to return-annotation fixes**
   (not in original list) — This method calls `self.insert_backlog_snapshot()`
   and is annotated `-> dict[str, Any]`. After `insert_backlog_snapshot`
   gained `| None`, this method needed to follow. 1 additional fix (total
   return-value fixes: 22).

3. **`insert_op_procedure` params fixed (variables, steps, known_failure_modes)**
   — These were bare `dict | None` / `list[dict] | None` parameters that
   showed up when mypy rechecked the file. 3 additional `type-arg` fixes
   (total type-arg fixes: 15). Error count was 39 at recount; the extra
   fixes were needed to reach 0.

4. **Before/after count: 48 → 0, not 46 → 0** — Proposal acknowledged
   drift; actual at implementation start was 48 (confirmed in GO review).
   Post-implementation is 0.

---

## Untracked files not committed

Per GO review Finding 4, the following untracked files were not included
in any commit:
- `.coverage`
- `_site_verify/`
- `release-notes-0.4.0.md`

---

## Codex Verification Checklist

1. `git log --oneline 8151ed2..HEAD` — expect 4 commits (`c0f53e6` → `da5a923`).
2. `git diff --stat 8151ed2..HEAD` — expect the files above.
3. `python -m mypy --strict --no-incremental src/groundtruth_kb/db.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/gates.py` — expect `Success: no issues found in 4 source files`.
4. `python -m pytest tests/test_public_api_type_checks.py -v` — expect `1 passed` (not skipped).
5. `python -m pytest -q --tb=short -p no:cacheprovider` — expect `638 passed`.
6. `python -m ruff check .` — all checks passed.
7. `python -m ruff format --check .` — no reformatting needed.
8. `python scripts/check_docs_cli_coverage.py` — all documentation checks passed.
9. `python -c "from groundtruth_kb import __all__; print(len(__all__))"` — expect `16`.
10. `git diff --name-only 8151ed2..HEAD` — expect only:
    `CHANGELOG.md`, `pyproject.toml`, `src/groundtruth_kb/cli.py`,
    `src/groundtruth_kb/config.py`, `src/groundtruth_kb/db.py`,
    `tests/test_public_api_type_checks.py`.
    No unrelated files.
