# GT-KB Phase 4D — Broad Exception Review (Revised)

**Status:** REVISED (addresses NO-GO -002 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Repo:** groundtruth-kb (main, current HEAD: `8efcbb1`, post-4C HEAD TBD)
**Bridge thread:** gtkb-phase4d-broad-exception-review

## Prior Deliberations

No prior DELIB-IDs found. Phase 4D defined in `docs/reports/phase-4b-plan.md:60`.

## NO-GO -002 Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| P1: Inventory incomplete (29 stated vs 31+ actual) | High | Fresh AST inventory at HEAD: **32 sites** (7 re-raise, 25 non-reraising). All listed with file:line. |
| P2: Counts internally inconsistent (26 defensible, 8 re-raise claimed) | Medium | Corrected: 7 re-raise exempt, 22 annotated, 3 narrowed/removed. Countable acceptance criteria. |

## Objective

Complete the final Phase 4 quality sub-round by:
1. Narrowing or removing the 3 flagged `except Exception` sites
2. Annotating 22 non-reraising broad-exception sites with `# intentional-catch:`
3. Adding a CI gate preventing unannotated broad exceptions
4. 7 re-raise cleanup handlers are **exempt** from markers (the CI gate
   exempts handlers whose body contains a bare `raise`)

## Fresh AST Inventory (machine-generated at HEAD)

**Total: 32 broad exception sites** (0 `BaseException`, 0 bare `except:`)
- **7 RERAISE** (all in `db.py` — transaction cleanup, re-raise)
- **25 non-reraising CATCH** across 8 files

**Note:** Count is 32, not 31, because Phase 4C adds `_logging.py:101`
(`except Exception: pass` in the stderr fallback). If 4C lands before 4D,
the inventory at implementation time will be 32. If 4D lands first, it
will be 31 and `_logging.py` is added when 4C lands.

### Complete inventory (sorted by file):

| # | File | Line | Type | Category | Action |
|---|------|------|------|----------|--------|
| 1 | `_logging.py` | 101 | CATCH | Startup-safe stderr fallback | Annotate `# intentional-catch: best-effort stderr warning` |
| 2 | `assertions.py` | 556 | CATCH | Parse fallback | Annotate `# intentional-catch: parse fallback, error message returned` |
| 3 | `bridge/context.py` | 650 | CATCH | Per-message isolation | Annotate `# intentional-catch: per-message isolation, error logged` |
| 4 | `bridge/launcher.py` | 36 | CATCH | Process check fallback | Annotate `# intentional-catch: process-check fallback, returns False` |
| 5 | `bridge/launcher.py` | 57 | CATCH | **NEEDS REVIEW** (Windows PID check) | **NARROW** to `(OSError, AttributeError, ImportError)` |
| 6 | `bridge/launcher.py` | 63 | CATCH | **NEEDS REVIEW** (Unix PID check) | **REMOVE** redundant handler after OSError |
| 7 | `bridge/launcher.py` | 259 | CATCH | Scheduled task check | Annotate `# intentional-catch: schtasks fallback, returns False` |
| 8 | `bridge/launcher.py` | 275 | CATCH | Scheduled task exists | Annotate `# intentional-catch: schtasks query fallback, returns False` |
| 9 | `bridge/launcher.py` | 339 | CATCH | Detached launch fallback | Annotate `# intentional-catch: detached launch fallback, logged` |
| 10 | `bridge/poller.py` | 69 | CATCH | stdin consumption | Annotate `# intentional-catch: best-effort stdin consumption` |
| 11 | `bridge/poller.py` | 208 | CATCH | Wake launch | Annotate `# intentional-catch: wake launch failure, logged and returns empty` |
| 12 | `bridge/poller.py` | 427 | CATCH | Message processing | Annotate `# intentional-catch: per-message isolation, error accumulated` |
| 13 | `bridge/poller.py` | 555 | CATCH | Once-mode execution | Annotate `# intentional-catch: once-mode boundary, error logged` |
| 14 | `bridge/poller.py` | 648 | CATCH | Main polling loop | Annotate `# intentional-catch: main loop resilience, error logged + backoff` |
| 15 | `bridge/worker.py` | 582 | CATCH | Cleanup failure | Annotate `# intentional-catch: cleanup failure, logged and returns 0` |
| 16 | `bridge/worker.py` | 646 | CATCH | Autonomous retry | Annotate `# intentional-catch: per-message error, logged and continues` |
| 17 | `bridge/worker.py` | 947 | CATCH | Main loop dispatch | Annotate `# intentional-catch: dispatch error, consecutive counter + backoff` |
| 18 | `db.py` | 831 | RERAISE | Transaction cleanup | **Exempt** (re-raises after rollback) |
| 19 | `db.py` | 1007 | RERAISE | Transaction cleanup | **Exempt** |
| 20 | `db.py` | 1248 | CATCH | **NEEDS REVIEW** (quality scores) | **NARROW** to `sqlite3.IntegrityError` |
| 21 | `db.py` | 2363 | RERAISE | Transaction cleanup | **Exempt** |
| 22 | `db.py` | 2441 | RERAISE | Transaction cleanup | **Exempt** |
| 23 | `db.py` | 2919 | RERAISE | Transaction cleanup | **Exempt** |
| 24 | `db.py` | 3015 | RERAISE | Transaction cleanup | **Exempt** |
| 25 | `db.py` | 3277 | RERAISE | Transaction cleanup | **Exempt** |
| 26 | `db.py` | 4287 | CATCH | ChromaDB sync failure | Annotate `# intentional-catch: ChromaDB optional, SQLite canonical` |
| 27 | `db.py` | 4556 | CATCH | ChromaDB delete fallback | Annotate `# intentional-catch: ChromaDB optional cleanup` |
| 28 | `db.py` | 4634 | CATCH | ChromaDB query fallback | Annotate `# intentional-catch: ChromaDB fallback to SQLite LIKE` |
| 29 | `db.py` | 4675 | CATCH | ChromaDB rebuild cleanup | Annotate `# intentional-catch: ChromaDB optional rebuild cleanup` |
| 30 | `db.py` | 4692 | CATCH | ChromaDB rebuild loop | Annotate `# intentional-catch: per-item error tracking, continues rebuild` |
| 31 | `project/doctor.py` | 255 | CATCH | Config validation check | Annotate `# intentional-catch: validation tool, error → fail status` |
| 32 | `project/doctor.py` | 298 | CATCH | KB validation check | Annotate `# intentional-catch: validation tool, error → fail status` |

## Expected Counts After Implementation

| Category | Count | Details |
|----------|-------|---------|
| **Narrowed** | 2 | `db.py:1248` → `IntegrityError`; `launcher.py:57` → `(OSError, AttributeError, ImportError)` |
| **Removed** | 1 | `launcher.py:63` — redundant after `OSError` handler |
| **Annotated** (`# intentional-catch:`) | 22 | All remaining non-reraising CATCH sites |
| **Exempt** (re-raise cleanup) | 7 | `db.py` transaction handlers — no marker needed |
| **Total accounted** | **32** | = 2 + 1 + 22 + 7 |

After implementation: **29 broad `except Exception` sites** remain
(32 − 1 removed − 2 narrowed to specific types = 29). All 22 non-reraising
sites have `# intentional-catch:` markers. 7 re-raise sites are exempt.

## The 3 "Needs Review" Sites (unchanged from -001)

### Site 1: `db.py:1248` — `persist_quality_scores()` loop
**Action: NARROW** to `sqlite3.IntegrityError`
```python
# Before:
except Exception:
    pass  # Skip on constraint violations

# After:
except sqlite3.IntegrityError:
    pass  # Skip duplicate/constraint violations
```

### Site 2: `launcher.py:57` — `_pid_is_running()` Windows branch
**Action: NARROW** to `(OSError, AttributeError, ImportError)`
```python
# Before:
except Exception:
    return False

# After:
except (OSError, AttributeError, ImportError):
    return False  # Process assumed dead on any platform-access error
```

### Site 3: `launcher.py:63` — `_pid_is_running()` Unix branch
**Action: REMOVE** redundant handler
```python
# Before:
try:
    os.kill(pid, 0)
except OSError:
    return False
except Exception:
    return False

# After:
try:
    os.kill(pid, 0)
except OSError:
    return False
```

## CI Gate: `test_exception_markers.py`

```python
def test_broad_exceptions_are_annotated():
    """Every non-reraising 'except Exception' must have an intentional-catch marker."""
```

The test:
1. Walks all `.py` files in `src/groundtruth_kb/`
2. Parses AST for `ExceptHandler` nodes with `Exception`/`BaseException`
3. Checks if the handler body contains a bare `raise` → **exempt** (no marker needed)
4. For non-reraising handlers: reads the source line and checks for `# intentional-catch:`
5. Fails with file:line for any unannotated non-reraising broad exception

**Expected result after implementation:**
- 7 re-raise handlers: exempt, no marker
- 22 non-reraising handlers: all have `# intentional-catch:` markers
- 0 unannotated → test passes

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `src/groundtruth_kb/db.py` | Modified | Narrow `:1248` to `IntegrityError`, annotate 5 CATCH sites |
| `src/groundtruth_kb/_logging.py` | Modified | Annotate 1 CATCH site (if 4C landed) |
| `src/groundtruth_kb/bridge/launcher.py` | Modified | Narrow `:57`, remove `:63`, annotate 4 CATCH sites |
| `src/groundtruth_kb/bridge/poller.py` | Modified | Annotate 5 CATCH sites |
| `src/groundtruth_kb/bridge/worker.py` | Modified | Annotate 3 CATCH sites |
| `src/groundtruth_kb/bridge/context.py` | Modified | Annotate 1 CATCH site |
| `src/groundtruth_kb/project/doctor.py` | Modified | Annotate 2 CATCH sites |
| `src/groundtruth_kb/governance/assertions.py` | Modified | Annotate 1 CATCH site |
| `tests/test_exception_markers.py` | New | AST-based CI gate |
| `docs/reports/phase-4b-plan.md` | Modified | Mark 4D as done |

## Test Requirements

1. `test_broad_exceptions_are_annotated` — baseline-clean after all 22 CATCH
   sites annotated (the primary CI gate)
2. `test_narrowed_db_persist_quality_scores` — `IntegrityError` caught,
   `TypeError` propagates
3. `test_pid_is_running_narrowed_windows` — `(OSError, AttributeError,
   ImportError)` caught on Windows path
4. `test_pid_is_running_unix_no_broad_catch` — only `OSError` caught on Unix

## Exit Criteria

1. All existing tests pass (969+ or 988+ if 4C landed)
2. New tests (4 tests) pass
3. `ruff check` clean
4. `mypy --strict src/groundtruth_kb/` clean
5. `test_broad_exceptions_are_annotated` passes (22 annotated, 7 exempt, 0 violations)
6. Phase 4D marked done in `docs/reports/phase-4b-plan.md`

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
