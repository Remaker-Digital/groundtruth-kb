# GT-KB Phase 4D — Broad Exception Review

**Status:** NEW (proposal for Codex review)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Repo:** groundtruth-kb (main, current HEAD: `8efcbb1`)
**Bridge thread:** gtkb-phase4d-broad-exception-review

## Prior Deliberations

No prior DELIB-IDs found. Phase 4D defined in `docs/reports/phase-4b-plan.md:60`:
"Review the 3 'needs review' `except Exception` sites flagged in Phase 4A;
for each, either narrow to specific exception classes, or add an explicit
`# intentional-catch: <rationale>` comment. CI gate: new `except Exception`
sites without the marker comment fail the commit gate."

## Objective

Complete the final Phase 4 quality sub-round by:
1. Narrowing or documenting the 3 flagged `except Exception` sites
2. Annotating 26 defensible broad-exception sites with `# intentional-catch:`
3. Adding a CI gate preventing unannotated broad exceptions

## Current State

Full audit of `src/groundtruth_kb/` found:
- **29 total `except Exception` sites** across 7 files
- **0 bare `except:` patterns** (good baseline)
- **3 flagged "needs review" sites** from Phase 4A
- **26 defensible sites** with clear architectural rationale

## The 3 "Needs Review" Sites

### Site 1: `db.py:1248` — `persist_quality_scores()` loop

```python
except Exception:
    pass  # Skip on constraint violations
```

**Context:** INSERT loop iterating over specs, scoring them, inserting into
`spec_quality_scores`. The `except Exception: pass` silently swallows ALL
errors including non-constraint bugs (malformed JSON, missing columns, etc.).

**Action: NARROW** to `sqlite3.IntegrityError`:
```python
except sqlite3.IntegrityError:
    pass  # Skip duplicate/constraint violations
```

**Rationale:** Only UNIQUE/CHECK constraint violations are expected here.
Other exceptions (OperationalError, TypeError, KeyError) indicate real bugs
that should propagate.

### Site 2: `launcher.py:57` — `_pid_is_running()` Windows branch

```python
try:
    import ctypes
    from ctypes import wintypes
    # ... Windows-specific process check logic ...
except Exception:
    return False
```

**Context:** Cross-platform process-alive check. Windows path uses ctypes
WinAPI calls. Multiple failure modes: `ImportError`, `AttributeError`,
`OSError` from kernel32 calls.

**Action: NARROW** to `(OSError, AttributeError, ImportError)`:
```python
except (OSError, AttributeError, ImportError):
    return False  # Process assumed dead on any platform-access error
```

**Rationale:** These are the three categories of platform-access failure.
A `TypeError` or `ValueError` would indicate a code bug that should
propagate.

### Site 3: `launcher.py:63` — `_pid_is_running()` Unix branch

```python
try:
    os.kill(pid, 0)
except OSError:
    return False
except Exception:
    return False
```

**Context:** Unix process-alive check using signal 0. The `OSError` handler
is correct and sufficient. The `except Exception:` after it is defensive
against an impossible case — `os.kill(pid, 0)` can only raise `OSError`
or succeed.

**Action: REMOVE** the redundant `except Exception:` handler:
```python
try:
    os.kill(pid, 0)
except OSError:
    return False
```

**Rationale:** The broad handler is unreachable given the `os.kill` contract.
Removing it eliminates dead code and removes the false impression that
non-OSError failures are expected.

## The 26 Defensible Sites

All receive `# intentional-catch: <rationale>` marker comments. Grouped by
architectural pattern:

### Pattern A: Transaction Cleanup with Re-raise (8 sites in `db.py`)

Lines: 831, 1007, 2363, 2441, 2919, 3015, 3277, and related rollback sites.

```python
except Exception:
    conn.rollback()
    raise  # intentional-catch: transaction cleanup before re-raise
```

These are already correct — they rollback and re-raise. The broad catch
ensures no transaction is left dangling regardless of exception type.

### Pattern B: ChromaDB Optional Secondary Index (4 sites in `db.py`)

Lines: 4287, 4556, 4634, 4675.

```python
except Exception:  # intentional-catch: ChromaDB optional; SQLite is canonical
    pass
```

ChromaDB is a secondary search index. If it fails, the SQLite write is
preserved. Silencing all ChromaDB errors is the correct behavior for an
optional enhancement.

### Pattern C: Message/Task Processing Loops (10 sites)

Files: `poller.py` (4 sites: 215, 431, 563, 657), `worker.py` (3 sites:
593, 657, 960), `context.py` (1 site: 650), `poller.py` (2 sites: 66).

```python
except Exception as exc:  # intentional-catch: per-item isolation, error logged
    _log.error("Failed processing %s: %s", item_id, exc)
```

Per-item error isolation is the correct pattern for batch/loop processing.
Errors are logged and processing continues with remaining items.

### Pattern D: Validation/Doctor Checks (2 sites in `doctor.py`)

Lines: 255, 298.

```python
except Exception as e:  # intentional-catch: validation tool, error → fail status
    return ToolCheck(name=..., status="fail", message=str(e))
```

Doctor checks convert any exception into a fail status for display. This
is the correct contract for a diagnostic tool.

### Pattern E: Parse Fallback (1 site in `assertions.py`)

Line: 556.

```python
except Exception as e:  # intentional-catch: parse fallback, error message returned
    return f"Error: {e}"
```

JSON/TOML parse errors are caught and returned as error messages. The caller
displays them in assertion results.

## CI Gate

Add an AST-based test that fails if any `except Exception` or
`except BaseException` (excluding re-raise patterns) appears without a
`# intentional-catch:` comment on the same or preceding line:

```python
# tests/test_exception_markers.py

def test_broad_exceptions_are_annotated():
    """Every 'except Exception' site must have an intentional-catch marker.

    Sites that re-raise (bare 'raise' in the except body) are exempt
    since they are transaction-cleanup patterns, not error-swallowing.
    """
    ...
```

The test:
1. Walks all `.py` files in `src/groundtruth_kb/`
2. Parses AST looking for `ExceptHandler` nodes with `Exception`/`BaseException`
3. For each handler, checks if the body contains a bare `raise` (exempt)
4. If no re-raise: checks the source line for `# intentional-catch:` marker
5. Fails with file:line for any unannotated non-re-raise broad exception

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `src/groundtruth_kb/db.py` | Modified | Narrow `:1248` to `IntegrityError`, add markers to 11 other sites |
| `src/groundtruth_kb/bridge/launcher.py` | Modified | Narrow `:57`, remove redundant `:63` handler |
| `src/groundtruth_kb/bridge/poller.py` | Modified | Add `# intentional-catch:` markers to 4 sites |
| `src/groundtruth_kb/bridge/worker.py` | Modified | Add `# intentional-catch:` markers to 3 sites |
| `src/groundtruth_kb/bridge/context.py` | Modified | Add `# intentional-catch:` marker to 1 site |
| `src/groundtruth_kb/project/doctor.py` | Modified | Add `# intentional-catch:` markers to 2 sites |
| `src/groundtruth_kb/governance/assertions.py` | Modified | Add `# intentional-catch:` marker to 1 site |
| `tests/test_exception_markers.py` | New | AST-based CI gate for broad exception annotation |
| `docs/reports/phase-4b-plan.md` | Modified | Mark 4D as done |

## Test Requirements

1. `test_broad_exceptions_are_annotated` — AST scan passes current baseline
   after all 26 defensible sites are annotated
2. `test_narrowed_db_persist_quality_scores` — verify `IntegrityError` is
   caught and non-IntegrityError propagates
3. `test_pid_is_running_windows_narrowed` — verify `(OSError, AttributeError,
   ImportError)` are caught on Windows path
4. `test_pid_is_running_unix_no_broad_catch` — verify only `OSError` is
   caught on Unix path

## Risks

- **Low:** Adding `# intentional-catch:` comments is documentation-only
- **Low:** Narrowing `db.py:1248` is conservative (IntegrityError is the
  only expected failure mode in a constraint-checking INSERT)
- **Low:** Removing `launcher.py:63` handler eliminates unreachable code
- **Low:** Narrowing `launcher.py:57` keeps all known failure modes covered

## Exit Criteria

1. All existing 969+ tests pass (or 980+ if 4C lands first)
2. New tests (4 tests) pass
3. `ruff check` clean
4. `mypy --strict src/groundtruth_kb/` clean
5. `test_broad_exceptions_are_annotated` passes (baseline-clean)
6. Phase 4D marked done in `docs/reports/phase-4b-plan.md`

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
