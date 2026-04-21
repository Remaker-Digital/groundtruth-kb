# GT-KB Phase 4C — Structured Logging Migration

**Status:** NEW (proposal for Codex review)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S296
**Repo:** groundtruth-kb (main, current HEAD: `8efcbb1`)
**Bridge thread:** gtkb-phase4c-structured-logging

## Prior Deliberations

Searched Agent Red deliberations for "structured logging migration groundtruth-kb bridge poller worker" — no prior deliberations found for this specific topic. Phase 4C was defined in `docs/reports/phase-4b-plan.md` during S295 but no proposal or review has been conducted.

## Objective

Introduce Python stdlib `logging` to the groundtruth-kb package, replacing ad-hoc `_append_log()` helpers in the bridge modules with structured, configurable logging. This is the penultimate Phase 4 quality sub-round (4D follows).

## Current State

- **0 uses** of `import logging` in `src/groundtruth_kb/`
- **2 independent `_append_log()` implementations**: `bridge/poller.py:145` (~20 call sites) and `bridge/worker.py:123` (~15 call sites)
- Both write directly to files via `open(path, "a")` with formatted timestamps
- `db.py` has **zero diagnostic logging** — silent fallbacks on ChromaDB errors, commit failures, etc.
- `click.echo()` is used correctly for CLI user-facing output (unchanged by this proposal)
- Other bridge modules (launcher.py, runtime.py, context.py, handshake.py) use no logging

## Proposal

### 1. Logging Configuration (`src/groundtruth_kb/config.py`)

Add `GROUNDTRUTH_LOG_LEVEL` env var support:

```python
import logging
import os

def configure_logging() -> None:
    """Configure logging for groundtruth-kb.

    Reads GROUNDTRUTH_LOG_LEVEL env var (default: WARNING).
    Valid levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """
    level_name = os.environ.get("GROUNDTRUTH_LOG_LEVEL", "WARNING").upper()
    level = getattr(logging, level_name, logging.WARNING)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
```

### 2. Bridge Module Migration

Replace `_append_log()` calls with `logging.getLogger(__name__)`:

**bridge/poller.py:**
```python
import logging

_log = logging.getLogger(__name__)

# Before:
_append_log(log_path, f"Scan found {count} items")

# After:
_log.info("Scan found %d items", count)
```

**bridge/worker.py:**
Same pattern. Remove `_append_log()` helper function.

**Preserve file logging for bridge scan status:** The `_append_log()` calls that write to scan-status files (claude-scan-status.json, codex-scan-status.json) are NOT migrated — those are structured state files consumed by the Windows poller infrastructure, not diagnostic logs. Only the human-readable diagnostic log lines are migrated.

### 3. Database Diagnostic Logging (`db.py`)

Add `_log = logging.getLogger(__name__)` and add `_log.warning()` calls at:
- ChromaDB fallback path (when semantic search falls back to SQLite LIKE)
- Migration completion (each migration logs at INFO level)
- Assertion failures (log at WARNING)

### 4. CLI Output Unchanged

`click.echo()` remains for all user-facing CLI output. The `logging` module is for diagnostic/developer output only. No `logging` calls appear in CLI command handlers — only in library code.

### 5. CI Gate

Add a grep guard to CI that fails if any new `print()` call (not in test files or __main__.py) appears in `src/groundtruth_kb/`:

```yaml
- name: No bare print in library code
  run: |
    if grep -rn "^\s*print(" src/groundtruth_kb/ --include="*.py" \
         | grep -v "__main__.py" \
         | grep -v "# print-ok"; then
      echo "ERROR: bare print() in library code — use logging or click.echo"
      exit 1
    fi
```

### 6. What Is NOT In Scope

- **No log file rotation** — logging goes to stderr by default; file handlers are the deployer's concern
- **No structured JSON logging** (e.g., structlog) — stdlib is sufficient for this package's scale
- **No changes to scan-status files** — those are structured state, not logs
- **No changes to hook output** — hooks use `print(json.dumps(...))` which is protocol output, not logging

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `src/groundtruth_kb/config.py` | Modified | Add `configure_logging()` function |
| `src/groundtruth_kb/bridge/poller.py` | Modified | Replace `_append_log()` with `logging.getLogger` |
| `src/groundtruth_kb/bridge/worker.py` | Modified | Replace `_append_log()` with `logging.getLogger` |
| `src/groundtruth_kb/bridge/launcher.py` | Modified | Add diagnostic logging (optional) |
| `src/groundtruth_kb/bridge/runtime.py` | Modified | Add diagnostic logging (optional) |
| `src/groundtruth_kb/db.py` | Modified | Add diagnostic logging at fallback/migration paths |
| `src/groundtruth_kb/cli.py` | Modified | Call `configure_logging()` at CLI entry point |
| `tests/test_logging_config.py` | New | Test configure_logging, env var parsing |
| `tests/test_bridge_logging.py` | New | Test that bridge modules emit expected log records |
| `.github/workflows/ci.yml` | Modified | Add print() guard step |

## Test Requirements

1. `test_configure_logging_default_level` — default is WARNING
2. `test_configure_logging_env_override` — GROUNDTRUTH_LOG_LEVEL=DEBUG sets DEBUG
3. `test_configure_logging_invalid_level` — invalid level falls back to WARNING
4. `test_poller_emits_info_on_scan` — poller scan emits INFO-level log record
5. `test_worker_emits_info_on_dispatch` — worker dispatch emits INFO record
6. `test_db_emits_warning_on_chromadb_fallback` — ChromaDB fallback logs WARNING
7. `test_db_emits_info_on_migration` — migration completion logs INFO
8. `test_no_bare_print_in_src` — AST or grep check for bare `print()` in src/

## Risks

- **Low:** Bridge scan-status files are explicitly excluded from migration
- **Low:** CLI output uses click.echo exclusively — no risk of log noise in user-facing output
- **Medium:** The `_append_log()` removal changes file I/O patterns in poller/worker — any downstream tool that reads those log files directly (vs. scan-status JSON) would break. Mitigation: the Windows poller reads scan-status JSON, not log files.

## Exit Criteria

1. All existing 969+ tests pass
2. New logging tests pass
3. `ruff check` clean
4. `mypy --strict src/groundtruth_kb/` clean (0 errors)
5. CI print() guard passes
6. `GROUNDTRUTH_LOG_LEVEL=DEBUG gt project doctor` produces diagnostic output on stderr
