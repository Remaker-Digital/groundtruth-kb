# GT-KB Phase 4C — Structured Logging Migration (Revision 3)

**Status:** REVISED (addresses NO-GO -004 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Repo:** groundtruth-kb (main, current HEAD: `8efcbb1`)
**Bridge thread:** gtkb-phase4c-structured-logging
**Prior versions:** -001 (NEW), -002 (NO-GO), -003 (REVISED), -004 (NO-GO)

## Prior Deliberations

Searched Agent Red deliberations for "structured logging migration groundtruth-kb bridge poller worker" — no prior DELIB IDs found.

Relevant non-DELIB context (confirmed by Codex in -002 and -004 reviews):

- `groundtruth-kb/docs/reports/v0.4-baseline/logging.md:78-109` recommends `logging.getLogger(__name__)` in bridge/db paths writing to the same log file path.
- `groundtruth-kb/docs/reports/phase-4b-plan.md:23-30` lists Phase 4C as the logging coverage target.

## NO-GO -004 Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1: AST print guard path not baseline-clean on Windows | High | Added `.as_posix()` normalization to both CI guard and `tests/test_no_bare_print.py`; factored shared logic into `_scan_bare_prints()` helper (§5) |
| F2: Bridge logging setup can crash before startup | High | Wrapped `_setup_bridge_logging()` body in `try/except OSError`, falls back to `NullHandler` + stderr warning (§1); added startup-safety and idempotency tests (§9) |

## NO-GO -002 Findings (previously addressed in -003, preserved)

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1: CI print guard not baseline-clean | High | Replaced with allowlist-scoped guard + baseline test (§5) |
| F2: Logging config only wired through `gt` | High | Added per-entry-point `_setup_logging()` for poller, worker, launcher (§2) |
| F3: Scan-status boundary misstated | Medium | Corrected scope language with exact file paths (§6) |
| F4: Exit criterion 6 unsupported | Medium | Replaced with bridge direct-entry smoke tests (§8) |

## Objective

Introduce Python stdlib `logging` to the groundtruth-kb package, replacing ad-hoc `_append_log()` helpers in bridge modules with structured, configurable logging. This is the penultimate Phase 4 quality sub-round (4D follows).

## Design Decision: Bridge Diagnostic Sink

**Decision:** Keep existing per-project log files via `logging.FileHandler`.

**Rationale:** Bridge modules are launched as background processes. On Windows, the poller/worker are started via `Start-Process` (launcher.py:144-148) or scheduled tasks, where stderr may have no visible or persisted sink. The Phase 4A baseline recommendation (`docs/reports/v0.4-baseline/logging.md:92`) explicitly says "writes to the same log file path." Moving to stderr-only would break operator visibility in hidden-process and scheduled-task contexts.

**Implementation:** Each bridge entry point (`poller.main()`, `worker.main()`, `launcher.main()`) calls a shared `_setup_bridge_logging()` that attaches a `FileHandler` to the existing log path. The `gt` CLI entry point uses `basicConfig(stream=stderr)` for interactive use. Setup is failure-tolerant: if the log path is unwritable, the bridge process continues with a `NullHandler` instead of crashing.

## Current State

- **0 uses** of `import logging` in `src/groundtruth_kb/`
- **2 independent `_append_log()` implementations**:
  - `bridge/poller.py:145` (~20 call sites) → writes to `.claude/hooks/.bridge-poller-{agent}.log`
  - `bridge/worker.py:123` (~15 call sites) → writes to `.claude/hooks/.{agent}-bridge-worker.log`
- Both write directly to files via `open(path, "a")` with formatted timestamps
- `db.py` has **zero diagnostic logging** — silent fallbacks on ChromaDB errors, commit failures
- `click.echo()` is used correctly for CLI user-facing output (unchanged)
- 23 existing `print()` sites in `src/groundtruth_kb/` serve protocol output (hook JSON, bridge handshake, launcher health checks, poller once-mode) — these are NOT diagnostic logging and MUST be preserved

## Proposal

### 1. Shared Logging Setup (`src/groundtruth_kb/_logging.py`)

New internal module providing two configuration functions. **Key change from -003:** `_setup_bridge_logging()` is now startup-safe — all I/O operations are wrapped in `try/except OSError` with `NullHandler` fallback and stderr warning.

```python
"""Internal logging configuration for groundtruth-kb.

Two entry paths:

- ``configure_cli_logging()`` — called by ``gt`` CLI (stderr handler).
- ``_setup_bridge_logging()`` — called by bridge direct entry points
  (FileHandler to the existing per-agent log file).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"
_LOG_DATEFMT = "%Y-%m-%dT%H:%M:%S"
_PACKAGE_LOGGER = "groundtruth_kb"


def _resolve_level() -> int:
    """Read GROUNDTRUTH_LOG_LEVEL env var; default WARNING."""
    name = os.environ.get("GROUNDTRUTH_LOG_LEVEL", "WARNING").upper()
    return getattr(logging, name, logging.WARNING)


def configure_cli_logging() -> None:
    """Configure stderr logging for the ``gt`` CLI entry point."""
    logging.basicConfig(
        level=_resolve_level(),
        format=_LOG_FORMAT,
        datefmt=_LOG_DATEFMT,
    )


def _setup_bridge_logging(log_path: Path) -> None:
    """Configure file-based logging for a bridge direct entry point.

    Attaches a FileHandler to the ``groundtruth_kb`` package logger,
    writing to *log_path* (the same file previously written by
    ``_append_log()``).  Creates parent directories if needed.

    **Startup-safe:** If the log path cannot be created or opened
    (permissions, path collision, read-only filesystem), falls back to
    a NullHandler so the bridge process can still start.  A one-line
    warning is emitted to stderr for operator visibility.

    **Idempotent:** Clears existing handlers on the package logger
    before attaching, so repeated calls (e.g. in tests) do not leak
    file descriptors or duplicate log records.

    Args:
        log_path: Absolute path to the agent-specific log file.
    """
    pkg_logger = logging.getLogger(_PACKAGE_LOGGER)
    pkg_logger.setLevel(_resolve_level())

    # Idempotent: remove prior handlers to prevent leaks on repeated calls
    for h in pkg_logger.handlers[:]:
        pkg_logger.removeHandler(h)
        h.close()

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handler: logging.Handler = logging.FileHandler(
            log_path, encoding="utf-8"
        )
    except OSError as exc:
        # Log path is unwritable — fall back to NullHandler so the
        # bridge process can still start.  Emit a stderr warning for
        # operator visibility (stderr may or may not be captured
        # depending on how the bridge was launched).
        print(
            f"WARNING: bridge logging setup failed for {log_path}: {exc}; "
            f"falling back to NullHandler",
            file=sys.stderr,
        )
        handler = logging.NullHandler()

    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT))
    pkg_logger.addHandler(handler)
```

**Why this addresses Finding 2 from -004:**

- The current poller `_append_log()` (lines 145-153) wraps parent creation and append I/O in `except OSError: pass`. The new `_setup_bridge_logging()` provides equivalent tolerance: `mkdir` + `FileHandler` construction are both inside the `try` block, and `OSError` falls back to `NullHandler` rather than crashing the process.
- `logging.raiseExceptions = False` is irrelevant here — that only covers `emit()` errors, not handler construction. The explicit `try/except` covers the setup path that Codex correctly identified as unprotected in -003.
- The idempotent handler cleanup prevents file descriptor leaks when tests call `_setup_bridge_logging()` multiple times.

### 2. Per-Entry-Point Logging Wiring

Every executable path affected by this migration calls the appropriate setup function before any logging occurs:

**`src/groundtruth_kb/cli.py` — `gt` console script:**
```python
from groundtruth_kb._logging import configure_cli_logging

def main() -> None:
    configure_cli_logging()
    # ... existing CLI setup
```

**`src/groundtruth_kb/bridge/poller.py` — `python -m groundtruth_kb.bridge.poller`:**
```python
from groundtruth_kb._logging import _setup_bridge_logging

def main() -> int:
    _consume_stdin_if_present()
    args = build_parser().parse_args()
    project_dir = Path(args.project_dir) if args.project_dir else None
    # Wire logging to existing log path before any work
    hooks_dir = _hooks_dir(project_dir or Path("."))
    _setup_bridge_logging(hooks_dir / f".bridge-poller-{args.agent}.log")
    return run(args, project_dir=project_dir)
```

**`src/groundtruth_kb/bridge/worker.py` — `python -m groundtruth_kb.bridge.worker`:**
```python
from groundtruth_kb._logging import _setup_bridge_logging

def main() -> int:
    args = build_parser().parse_args()
    project_dir = Path(args.project_dir) if args.project_dir else None
    # Wire logging to existing log path before any work
    _setup_bridge_logging(
        _log_file(args.agent, project_dir or Path("."))
    )
    return run(args, project_dir=project_dir)
```

**`src/groundtruth_kb/bridge/launcher.py` — `python -m groundtruth_kb.bridge.launcher`:**
```python
from groundtruth_kb._logging import _setup_bridge_logging

def main() -> int:
    args = build_parser().parse_args()
    # Launcher diagnostics go to the poller log since launcher is
    # invoked in the poller's process context
    hooks_dir = Path(args.project_dir or ".") / ".claude" / "hooks"
    _setup_bridge_logging(hooks_dir / f".bridge-launcher-{args.agent}.log")
    return run(args)
```

### 3. Bridge Module Migration

Replace `_append_log()` calls with `logging.getLogger(__name__)`:

**bridge/poller.py:**
```python
import logging
_log = logging.getLogger(__name__)

# Before (20 call sites):
_append_log(log_path, f"Scan found {count} items")

# After:
_log.info("Scan found %d items", count)
```

Remove the `_append_log()` helper function (lines 145-153). All 20 call sites that currently pass `log_path` as the first argument are converted to `_log.info()`, `_log.warning()`, or `_log.error()` based on content.

**bridge/worker.py:**
```python
import logging
_log = logging.getLogger(__name__)

# Before (15 call sites):
_append_log(agent, f"Dispatching {item}", project_dir)

# After:
_log.info("Dispatching %s", item)
```

Remove the `_append_log()` helper function (lines 123-135). The `_log_file()` helper (lines 98-100) is retained — it is used by `_setup_bridge_logging()` wiring in `main()` and may be used by health/state writers.

### 4. Database Diagnostic Logging (`db.py`)

Add `_log = logging.getLogger(__name__)` and targeted log calls:

- ChromaDB fallback path: `_log.warning("ChromaDB search failed, falling back to SQLite LIKE: %s", err)`
- Migration completion: `_log.info("Applied migration %s", migration_name)`
- Assertion failures: `_log.warning("Assertion %s failed: %s", assertion_id, reason)`

These are reached through `gt` CLI (which calls `configure_cli_logging()`) so they will emit to stderr at the configured level.

### 5. CI Print Guard (Baseline-Clean, Cross-Platform)

**Key change from -003:** Path normalization uses `.as_posix()` so the allowlist matches on both Windows (`bridge\launcher.py` → `bridge/launcher.py`) and Linux. The guard logic is factored into a shared `_scan_bare_prints()` function used by both the CI script and `tests/test_no_bare_print.py`, eliminating the drift risk Codex flagged.

```yaml
- name: No bare print in library code
  run: |
    python -c "
    import ast, sys, pathlib

    # Modules where print() is protocol output, not diagnostic logging
    ALLOWED_MODULES = {
        'governance/output.py',    # Hook JSON protocol
        'bridge/launcher.py',      # Health-check JSON protocol
        'bridge/handshake.py',     # Bridge handshake protocol
        'bridge/runtime.py',       # MCP dependency warning
        'bridge/poller.py',        # Once-mode JSON protocol output
        '__main__.py',             # CLI entry
    }

    errors = []
    for py in pathlib.Path('src/groundtruth_kb').rglob('*.py'):
        rel = py.relative_to('src/groundtruth_kb').as_posix()
        if rel in ALLOWED_MODULES:
            continue
        tree = ast.parse(py.read_text(encoding='utf-8'), filename=str(py))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == 'print'):
                errors.append(f'{rel}:{node.lineno}')
    if errors:
        print('ERROR: bare print() in non-protocol library code:')
        for e in errors:
            print(f'  {e}')
        sys.exit(1)
    print('OK: no bare print() outside allowed protocol modules')
    "
```

**Shared helper for test/CI synchronization** (`tests/_print_guard.py`):

```python
"""Shared bare-print scanner used by both CI and tests/test_no_bare_print.py.

This ensures the CI guard and the pytest guard cannot drift apart.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
"""

from __future__ import annotations

import ast
import pathlib

# Modules where print() is protocol output, not diagnostic logging.
ALLOWED_MODULES: frozenset[str] = frozenset({
    "governance/output.py",    # Hook JSON protocol
    "bridge/launcher.py",      # Health-check JSON protocol
    "bridge/handshake.py",     # Bridge handshake protocol
    "bridge/runtime.py",       # MCP dependency warning
    "bridge/poller.py",        # Once-mode JSON protocol output
    "__main__.py",             # CLI entry
})


def scan_bare_prints(
    src_root: pathlib.Path | None = None,
) -> list[str]:
    """Return a list of ``'module/path.py:lineno'`` for bare print() calls.

    Args:
        src_root: Root of the ``groundtruth_kb`` package source tree.
            Defaults to ``src/groundtruth_kb`` relative to the repo root.

    Returns:
        List of violation strings (empty = clean).
    """
    if src_root is None:
        src_root = pathlib.Path("src/groundtruth_kb")

    errors: list[str] = []
    for py in src_root.rglob("*.py"):
        rel = py.relative_to(src_root).as_posix()
        if rel in ALLOWED_MODULES:
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ):
                errors.append(f"{rel}:{node.lineno}")
    return errors
```

**`tests/test_no_bare_print.py`** imports and calls `scan_bare_prints()`:

```python
from tests._print_guard import scan_bare_prints

def test_no_bare_print_outside_protocol_modules():
    """Verify no bare print() calls exist outside allowed protocol modules."""
    errors = scan_bare_prints()
    assert errors == [], (
        f"Bare print() in non-protocol library code:\n"
        + "\n".join(f"  {e}" for e in errors)
    )
```

The CI step can also import the shared helper (or inline the same logic for CI simplicity — both are acceptable since the authoritative ALLOWED_MODULES list lives in `tests/_print_guard.py`).

**Why this addresses Finding 1 from -004:**

- Codex empirically demonstrated that `py.relative_to('src/groundtruth_kb')` returns `bridge\launcher.py` on Windows, which does not match the forward-slash allowlist entry `bridge/launcher.py`. The fix is `.as_posix()` which normalizes to forward slashes on all platforms.
- Codex ran the simulation and confirmed `error_count=0` after `.as_posix()`.
- The shared `_print_guard.py` helper eliminates the CI/test drift risk: both use the same `ALLOWED_MODULES` set and the same scanning logic.

**Poller once-mode print** (`poller.py:552`): This is protocol JSON output (`print(json.dumps({...}))`). `bridge/poller.py` is in `ALLOWED_MODULES`.

**Poller stderr print** (`poller.py:459`): `print(..., file=sys.stderr)` is argument validation error output. After migration this becomes `_log.error(...)` and the bare print is removed.

### 6. Scope Boundary (Corrected)

**What is migrated (diagnostic log lines):**

| Helper | Current file | Log path | Action |
|--------|-------------|----------|--------|
| `_append_log()` in `poller.py:145-153` | `bridge/poller.py` | `.claude/hooks/.bridge-poller-{agent}.log` | Replace with `_log.info/warning/error()` via `logging.FileHandler` to same path |
| `_append_log()` in `worker.py:123-135` | `bridge/worker.py` | `.claude/hooks/.{agent}-bridge-worker.log` | Replace with `_log.info/warning/error()` via `logging.FileHandler` to same path |
| (none — new) | `db.py` | stderr (via CLI `basicConfig`) | Add new `_log.warning/info()` calls |

**What is NOT migrated (state/status/protocol files — unchanged):**

| File/helper | Path | Reason preserved |
|-------------|------|-----------------|
| `_log_file()` in `worker.py:98-100` | `.claude/hooks/.{agent}-bridge-worker.log` | Path helper retained for `_setup_bridge_logging()` wiring |
| `_last_message_file()` in `worker.py:103-105` | `.claude/hooks/.{agent}-bridge-worker-last-message.txt` | Raw message capture, not diagnostic logging |
| `_last_stdout_file()` in `worker.py:108-110` | `.claude/hooks/.{agent}-bridge-worker-last-stdout.jsonl` | Process output capture, not diagnostic logging |
| `_last_context_file()` in `worker.py:113-115` | `.claude/hooks/.{agent}-bridge-worker-last-context.json` | Context snapshot, not diagnostic logging |
| `_health_file()` in `worker.py:118-120` | `.claude/hooks/.bridge-worker-{agent}-health.json` | Health status JSON, not diagnostic logging |
| Scan-status JSON (read by `project/doctor.py:545-568`) | `independent-progress-assessments/bridge-automation/logs/{agent}-scan-status.json` | File-bridge liveness contract, written by Windows PS1 scripts, not by Python code |
| Protocol `print()` in `governance/output.py` | stdout | Hook JSON protocol output |
| Protocol `print()` in `bridge/launcher.py` | stdout | Health-check JSON protocol output |
| Protocol `print()` in `bridge/handshake.py` | stdout | Bridge handshake protocol output |
| Protocol `print()` in `bridge/runtime.py:1642` | stdout | MCP dependency warning |
| Once-mode `print()` in `bridge/poller.py:552` | stdout | Once-mode JSON result |

### 7. CLI Output Unchanged

`click.echo()` remains for all user-facing CLI output. The `logging` module is for diagnostic/developer output only. No `logging` calls appear in CLI command handlers — only in library code (`db.py`, `bridge/*`).

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `src/groundtruth_kb/_logging.py` | **New** | `configure_cli_logging()` + `_setup_bridge_logging()` (startup-safe) |
| `src/groundtruth_kb/cli.py` | Modified | Call `configure_cli_logging()` at entry |
| `src/groundtruth_kb/bridge/poller.py` | Modified | Replace `_append_log()` with `_log.*()`, call `_setup_bridge_logging()` in `main()` |
| `src/groundtruth_kb/bridge/worker.py` | Modified | Replace `_append_log()` with `_log.*()`, call `_setup_bridge_logging()` in `main()` |
| `src/groundtruth_kb/bridge/launcher.py` | Modified | Add `_setup_bridge_logging()` in `main()`, optional diagnostic logging |
| `src/groundtruth_kb/db.py` | Modified | Add `_log.warning/info()` at fallback/migration paths |
| `tests/_print_guard.py` | **New** | Shared `scan_bare_prints()` + `ALLOWED_MODULES` for CI/test sync |
| `tests/test_logging_config.py` | **New** | Test `configure_cli_logging`, `_setup_bridge_logging`, env var parsing, startup safety |
| `tests/test_bridge_logging.py` | **New** | Test bridge modules emit expected log records via `caplog`/handler |
| `tests/test_no_bare_print.py` | **New** | AST-based baseline test for print guard (imports shared helper) |
| `.github/workflows/ci.yml` | Modified | Add AST-based print guard step |

## Test Requirements

### Configuration tests (`tests/test_logging_config.py`)
1. `test_configure_cli_logging_default_level` — default is WARNING, handler is StreamHandler(stderr)
2. `test_configure_cli_logging_env_override` — `GROUNDTRUTH_LOG_LEVEL=DEBUG` sets DEBUG
3. `test_configure_cli_logging_invalid_level` — invalid level falls back to WARNING
4. `test_setup_bridge_logging_creates_file_handler` — `_setup_bridge_logging(tmp_path / "test.log")` attaches FileHandler to package logger
5. `test_setup_bridge_logging_creates_parent_dirs` — parent directory created if missing
6. `test_setup_bridge_logging_writes_to_correct_path` — log records appear in the specified file
7. `test_setup_bridge_logging_unwritable_path_falls_back_to_null_handler` — when `log_path` parent is a file (not a directory), `_setup_bridge_logging()` falls back to `NullHandler` and emits a stderr warning, without raising
8. `test_setup_bridge_logging_idempotent` — calling `_setup_bridge_logging()` twice does not duplicate handlers or leak file descriptors; second call replaces the first handler

### Bridge logging tests (`tests/test_bridge_logging.py`)
9. `test_poller_emits_info_on_scan` — poller scan emits INFO-level log record (via `caplog` with `_setup_bridge_logging` to temp file)
10. `test_worker_emits_info_on_dispatch` — worker dispatch emits INFO record
11. `test_db_emits_warning_on_chromadb_fallback` — ChromaDB fallback logs WARNING (via `caplog`)
12. `test_db_emits_info_on_migration` — migration completion logs INFO

### Baseline enforcement test (`tests/test_no_bare_print.py`)
13. `test_no_bare_print_outside_protocol_modules` — AST scan proves guard passes current baseline

## Risks

- **Low:** Bridge log files continue at the same paths — no downstream breakage
- **Low:** CLI output uses `click.echo` exclusively — no log noise for users
- **Low:** Protocol `print()` sites in allowlisted modules are explicitly preserved
- **Low:** Removing `_append_log()` changes the error-silencing behavior. Mitigation: `_setup_bridge_logging()` wraps `mkdir` + `FileHandler` in `try/except OSError` with `NullHandler` fallback — equivalent to poller's current `except OSError: pass` but with a stderr warning for operator visibility

## Exit Criteria

1. All existing 969+ tests pass
2. New logging + print-guard tests (13 tests) pass
3. `ruff check` clean
4. `mypy --strict src/groundtruth_kb/` clean (0 errors)
5. CI AST-based print guard passes (baseline-clean on current codebase, verified with `.as_posix()` normalization)
6. `GROUNDTRUTH_LOG_LEVEL=DEBUG python -m groundtruth_kb.bridge.poller --agent prime --project-dir /tmp/test --once 2>/dev/null` produces log lines in the poller log file (direct bridge entry, not `gt` CLI)
7. `GROUNDTRUTH_LOG_LEVEL=DEBUG python -c "from groundtruth_kb._logging import configure_cli_logging; configure_cli_logging(); import logging; logging.getLogger('groundtruth_kb').info('test')"` produces output on stderr (CLI path)
8. `caplog`-based test confirms ChromaDB fallback emits WARNING record
9. Startup-safety test confirms `_setup_bridge_logging()` with unwritable path does not raise and attaches `NullHandler`
10. Idempotency test confirms repeated `_setup_bridge_logging()` calls do not leak handlers

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
