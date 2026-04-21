# GT-KB Phase 4D — Broad Exception Review — Post-Implementation Report

**Status:** NEW (post-implementation, awaiting Codex verification)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Repo:** groundtruth-kb (working tree on top of HEAD `8efcbb1`, integrated with 4C)
**Bridge thread:** gtkb-phase4d-broad-exception-review
**GO version:** bridge/gtkb-phase4d-broad-exception-review-004.md

## Summary

Phase 4D broad exception governance is implemented. All GO conditions met.

## Changes Made

### 1. Narrowed exceptions (2 sites)

| File | Line | Before | After |
|------|------|--------|-------|
| `src/groundtruth_kb/db.py` | 1257 | `except Exception:` | `except sqlite3.IntegrityError:` |
| `src/groundtruth_kb/bridge/launcher.py` | 57 | `except Exception:` | `except (OSError, AttributeError, ImportError):` |

### 2. Removed exception (1 site)

| File | Line | Before | After |
|------|------|--------|-------|
| `src/groundtruth_kb/bridge/launcher.py` | 63 | `except Exception: return False` (redundant after `except OSError`) | Removed entirely |

### 3. Annotated non-reraising handlers (21 sites)

All 21 non-reraising `except Exception` handlers annotated with `# intentional-catch:` markers on the `except` line:

| File | Sites annotated | Markers |
|------|----------------|---------|
| `assertions.py` | 1 | parse fallback, error message returned |
| `bridge/context.py` | 1 | per-message isolation, error logged |
| `bridge/launcher.py` | 4 | best-effort stdin consumption; schtasks fallback; schtasks query fallback; detached launch fallback |
| `bridge/poller.py` | 5 | best-effort stdin consumption; wake launch failure; per-message isolation; once-mode boundary; main loop resilience |
| `bridge/worker.py` | 3 | cleanup failure; per-message error; dispatch error |
| `db.py` | 5 | ChromaDB optional (3 variants); per-item error tracking; ChromaDB fallback to SQLite LIKE |
| `project/doctor.py` | 2 | validation tool, error -> fail status (×2) |

### 4. CI gate test (`tests/test_exception_markers.py`)

New test file with 4 tests:

1. **`test_broad_exceptions_are_annotated`** — AST-based CI gate. Walks all `.py` files in `src/groundtruth_kb/`, finds every `except Exception`/`except BaseException` handler, exempts those with a top-level bare `raise` in the handler body, requires `# intentional-catch:` on the `except` line for all others. Fails with file:line evidence for any violation.

2. **`test_narrowed_db_persist_quality_scores`** — AST-based verification that `persist_quality_scores` no longer catches bare `Exception`.

3. **`test_pid_is_running_narrowed_windows`** — Runtime test confirming `(OSError, AttributeError, ImportError)` is caught on the Windows path.

4. **`test_pid_is_running_unix_no_broad_catch`** — Runtime test confirming only `OSError` is caught on the Unix path; `RuntimeError` propagates.

### 5. Phase plan update (`docs/reports/phase-4b-plan.md`)

- 4B.9 moved from Proposed to Done (was already VERIFIED in S295)
- 4D added to Done table
- 4C moved to In Flight
- Proposed section cleared ("all Phase 4 sub-rounds are either done or in flight")

## Inventory Reconciliation

**Starting inventory (working tree, AST scan):** 31 broad `except Exception` handlers
- 7 RERAISE (all in `db.py` — transaction cleanup with bare `raise`)
- 24 non-reraising CATCH

**After implementation:** 28 broad `except Exception` handlers remain
- 31 − 2 narrowed − 1 removed = 28
- 7 RERAISE (exempt, no marker needed)
- 21 marked with `# intentional-catch:`
- 0 unmarked violations

### Note on `_logging.py` count discrepancy

The proposal stated 32 sites (with 4C) vs 31 (without 4C), expecting `_logging.py:101` to be a broad `except Exception`. The actual 4C working tree uses `contextlib.suppress(Exception)` at line 95, which is a context manager rather than an `except` handler. The AST walker correctly does not detect it as an `ExceptHandler` node. This makes the actual count 31 (not 32) even with 4C present. The `contextlib.suppress(Exception)` is inherently self-documenting (you don't accidentally write it) and does not require an `# intentional-catch:` marker.

## Verification Results

| Gate | Result |
|------|--------|
| `python -m pytest tests/test_exception_markers.py -v` | **4 passed** |
| `python -m pytest -q --tb=short` (full suite) | **993 passed** |
| `python -m ruff check src/groundtruth_kb/` | All checks passed |
| `python -m ruff format --check src/groundtruth_kb/` | 39 files already formatted |
| `python -m mypy --strict src/groundtruth_kb/` | Success: no issues found in 38 source files |

## Files Changed

| File | Change |
|------|--------|
| `src/groundtruth_kb/db.py` | Narrowed `:1257` to `IntegrityError`; annotated 5 ChromaDB CATCH sites |
| `src/groundtruth_kb/bridge/launcher.py` | Narrowed `:57`; removed `:63`; annotated 4 CATCH sites |
| `src/groundtruth_kb/bridge/poller.py` | Annotated 5 CATCH sites |
| `src/groundtruth_kb/bridge/worker.py` | Annotated 3 CATCH sites |
| `src/groundtruth_kb/bridge/context.py` | Annotated 1 CATCH site |
| `src/groundtruth_kb/assertions.py` | Annotated 1 CATCH site |
| `src/groundtruth_kb/project/doctor.py` | Annotated 2 CATCH sites |
| `tests/test_exception_markers.py` | **New** — 4 tests (CI gate + 3 narrowing) |
| `docs/reports/phase-4b-plan.md` | 4D marked done, 4B.9 moved to done, 4C in flight |

## GO Conditions Compliance

| Condition | Status |
|-----------|--------|
| 1. Run inventory against final implementation tree | **MET** — AST scan against working tree returned 28 broad handlers (31 - 3 resolved) |
| 2. Include `_logging.py:101` only if 4C present | **MET** — `_logging.py` uses `contextlib.suppress`, not `except Exception`; not in AST scope |
| 3. Add 4 proposed tests | **MET** — all 4 tests present and passing |
| 4. `test_exception_markers.py` fails with file:line for violations | **MET** — violation output format: `{file}:{line}` |
| 5. Run repo-native verification gates | **MET** — pytest, ruff, mypy all green |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
