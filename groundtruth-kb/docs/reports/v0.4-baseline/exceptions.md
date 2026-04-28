# Broad Exception Handling Inventory (Phase 4A)

Generated 2026-04-14 against `groundtruth-kb` commit `993f31b8d42ac272b9716c191527b599d08ba632`.

Source: `rg -n "except Exception|except BaseException|except:" src/groundtruth_kb/`

## Baseline

- **Total broad exception sites:** 31
- **Files containing broad exceptions:** 8
- **Classification:** manual, by reading one line of context before and after each `except` statement

## Classification definitions

- **safe fallback** — the catch-all is intentional for a non-critical path and does one of:
  - Rolls back a database transaction (state is preserved, error propagates via separate mechanism)
  - Returns an explicit error status to the caller (caller sees it)
  - Logs the error and continues in a loop that collects errors
  - Documented fallback to an alternative strategy (e.g., ChromaDB → SQLite LIKE)
- **silent swallow** — the catch suppresses an error that should propagate or at least be logged, with no clear "why" in the surrounding code
- **needs review** — unclear from the grep context whether the catch is safe; requires a deeper read of the function

Any site whose notes include "pass" AND "may be" or "can be rebuilt" is safe fallback because the author documented the rationale.

## Per-site inventory

### `assertions.py` (1 site)

| Line | Context | Classification | Notes |
|---:|---|---|---|
| 556 | Parse TOML file, return `_fail("json_path", ...)` on error | safe fallback | Error surface is the `_fail` return value |

### `db.py` (13 sites)

| Line | Context | Classification | Notes |
|---:|---|---|---|
| 808 | Commit + rollback pattern | safe fallback | Rollback keeps DB consistent; error raised after |
| 975 | Commit + rollback pattern | safe fallback | Same |
| 1216 | `pass  # Skip on constraint violations` (seed path) | needs review | Silent skip; no log. Seed path may hide data integrity issues |
| 2207 | Commit + rollback pattern | safe fallback | Same |
| 2285 | Commit + rollback pattern | safe fallback | Same |
| 2706 | Commit + rollback pattern | safe fallback | Same |
| 2802 | Commit + rollback pattern | safe fallback | Same |
| 3013 | Commit + rollback pattern | safe fallback | Same |
| 4007 | `pass  # Index can be rebuilt later via rebuild_deliberation_index()` | safe fallback | ChromaDB index is eventually consistent with SQLite; documented rationale |
| 4276 | `pass  # Collection may be empty or delib_id not present` | safe fallback | Idempotent delete |
| 4354 | `pass  # Fall through to SQLite LIKE` | safe fallback | Documented fallback from semantic search to text match |
| 4395 | `pass` (delete_collection cleanup) | safe fallback | Idempotent cleanup |
| 4412 | `errors.append(...)` in rebuild loop | safe fallback | Errors collected into return value |

### `bridge/context.py` (1 site)

| Line | Context | Classification | Notes |
|---:|---|---|---|
| 494 | `if log_fn is not None: log_fn(...)` | safe fallback | Logged when log_fn available |

### `bridge/poller.py` (5 sites)

| Line | Context | Classification | Notes |
|---:|---|---|---|
| 45 | `pass` in stdin-read init | safe fallback | stdin may be closed; init continues |
| 172 | `_append_log(log_file, f"wake launch failed ...")` | safe fallback | Logged |
| 370 | `summary["errors"] += 1` | safe fallback | Counted and surfaced via summary |
| 489 | `_append_log(log_file, f"once-mode error: ...")` | safe fallback | Logged |
| 583 | `_append_log(log_file, f"loop error: ...")` | safe fallback | Logged |

### `bridge/launcher.py` (6 sites)

| Line | Context | Classification | Notes |
|---:|---|---|---|
| 35 | `pass` in stdin-read init | safe fallback | Same as poller:45 |
| 56 | `return False` (process check helper) | needs review | Silent False return hides error reason; predicate check for `STILL_ACTIVE` |
| 62 | `return False` (process check fallback) | needs review | Same pattern |
| 256 | `return result.returncode == 0` fallback `return False` | safe fallback | Windows tasklist probe; False is the right default |
| 272 | `return result.returncode == 0` fallback `return False` | safe fallback | Same |
| 336 | `_run_once_wake(...)` fallback after exception in subprocess launch | safe fallback | Falls back to once-wake mode |

### `bridge/worker.py` (3 sites)

| Line | Context | Classification | Notes |
|---:|---|---|---|
| 437 | `log_fn(f"failed residue cleanup error: {exc}")` | safe fallback | Logged |
| 501 | `log_fn(f"autonomous retry error: ...")` | safe fallback | Logged |
| 768 | `log_fn(f"...")` + `consecutive_errors += 1` | safe fallback | Logged and counted |

### `project/doctor.py` (2 sites)

| Line | Context | Classification | Notes |
|---:|---|---|---|
| 242 | `return ToolCheck(status=fail, detail=str(e))` | safe fallback | Error wrapped in return value |
| 285 | `return ToolCheck(status=fail, detail=str(e))` | safe fallback | Same |

## Classification totals

| Category | Count | Share |
|---|---:|---:|
| safe fallback | 28 | 90.3% |
| needs review | 3 | 9.7% |
| silent swallow (unambiguous) | 0 | 0.0% |

## Sites needing human review in Phase 4B

Three sites are flagged for deeper review:

1. **`db.py:1216`** — `pass  # Skip on constraint violations` in seed path. The comment documents the intent, but silent skipping of constraint violations during database seeding can mask real data integrity issues. Phase 4B should decide whether to:
   - Log a warning naming the constraint violation,
   - Fail the seed run on constraint violation, or
   - Accept the current silent skip with a more explicit comment explaining which violations are expected.

2. **`bridge/launcher.py:56`** — `return False` after process-status probe. The outer function is a predicate check. A silent `False` return treats "process errored during check" the same as "process is not running". This may be correct, but should be explicit via a comment.

3. **`bridge/launcher.py:62`** — same pattern as :56. Probably the same fix applies.

None of the sites are a clear "silent swallow" anti-pattern. The codebase shows consistent discipline on exception handling:

- Database transactions always use `commit` + `rollback on error`.
- Background loops (`bridge/poller.py`, `bridge/worker.py`) always log errors before continuing.
- Tool-check helpers (`project/doctor.py`) wrap errors in structured return values.
- The single `pass`-only site in `db.py` (line 1216) is the only one that needs judgment.

## Phase 4B recommendations

1. **Do not convert existing `except Exception:` sites to narrower exceptions wholesale.** The current broad catches are mostly correct; narrowing would be noise. 
2. **Add a one-line `# {reason}` comment** to the 3 "needs review" sites to make their intent explicit.
3. **Add a log statement** to `db.py:1216` naming the caught exception type, if the silent skip is kept.
4. **Consider adding a lint rule** (e.g., ruff's `BLE001`) that flags new `except Exception:` sites and requires either `# noqa: BLE001` with justification or a narrower catch. This enforces the pattern going forward without requiring a refactor of the existing 31 sites.

## Non-blocking note

This audit is based on grep context (1 line before/after). A Phase 4B implementation would read the full function body for the 3 "needs review" sites before deciding what to change.

---

*Generated as part of the Phase 4A measurement-only audit baseline.*
