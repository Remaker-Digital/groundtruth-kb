# GT-KB Phase 4C — Structured Logging Migration (Revision 5)

**Status:** REVISED (addresses NO-GO -008 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Repo:** groundtruth-kb (main, current HEAD: `8efcbb1`)
**Bridge thread:** gtkb-phase4c-structured-logging
**Prior versions:** -001 (NEW), -002 (NO-GO), -003 (REVISED), -004 (NO-GO), -005 (REVISED), -006 (NO-GO), -007 (REVISED), -008 (NO-GO)

## Prior Deliberations

Searched Agent Red deliberations for "structured logging migration groundtruth-kb bridge poller worker" — no prior DELIB IDs found.

Relevant non-DELIB context (confirmed by Codex in -002, -004, -006, and -008 reviews):

- `groundtruth-kb/docs/reports/v0.4-baseline/logging.md:78-109` recommends `logging.getLogger(__name__)` in bridge/db paths writing to the same log file path.
- `groundtruth-kb/docs/reports/phase-4b-plan.md:23-30` lists Phase 4C as the logging coverage target.
- `groundtruth-kb/docs/reports/v0.4-baseline/logging.md:88-92` says bridge runtime logging is needed so operators can see what poller and worker are doing.
- `groundtruth-kb/docs/reports/v0.4-baseline/SUMMARY.md:131` says operators debug a hung poller or failing worker by reading the log files.

## NO-GO -008 Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1: Startup-safe fallback can still crash when stderr is unavailable | High | Assign `NullHandler` **before** any diagnostic write; wrap `sys.stderr.write()` in a bare `except Exception` guard so it is genuinely best-effort (§1) |
| F2: CI print guard synchronization is still ambiguous | Medium | CI step now invokes `tests/_print_guard.scan_bare_prints()` directly via `python -c "from tests._print_guard import scan_bare_prints; ..."` — zero inline duplication (§5) |

## Previously Addressed Findings (preserved)

| Finding | Source | Resolution |
|---------|--------|------------|
| `_logging.py` fallback `print()` fails the proposed no-bare-print guard | -006 F1 | `sys.stderr.write()` — not an AST `print()` call (§1) |
| Default bridge logging at WARNING suppresses current INFO log lines | -006 F2 | Split defaults: CLI=WARNING, bridge=INFO (§1, §2) |
| AST print guard path not baseline-clean on Windows | -004 F1 | `.as_posix()` normalization (§5) |
| Bridge logging setup can crash before startup | -004 F2 | `try/except OSError` with `NullHandler` fallback (§1) |
| CI print guard not baseline-clean | -002 F1 | Allowlist-scoped guard + baseline test (§5) |
| Logging config only wired through `gt` | -002 F2 | Per-entry-point `_setup_logging()` for poller, worker, launcher (§2) |
| Scan-status boundary misstated | -002 F3 | Corrected scope language with exact file paths (§6) |
| Exit criterion 6 unsupported | -002 F4 | Bridge direct-entry smoke tests (§8) |

## Objective

Introduce Python stdlib `logging` to the groundtruth-kb package, replacing ad-hoc `_append_log()` helpers in bridge modules with structured, configurable logging. This is the penultimate Phase 4 quality sub-round (4D follows).

## Design Decision: Bridge Diagnostic Sink

**Decision:** Keep existing per-project log files via `logging.FileHandler`.

**Rationale:** Bridge modules are launched as background processes. On Windows, the poller/worker are started via `Start-Process` (launcher.py:144-148) or scheduled tasks, where stderr may have no visible or persisted sink. The Phase 4A baseline recommendation (`docs/reports/v0.4-baseline/logging.md:92`) explicitly says "writes to the same log file path." Moving to stderr-only would break operator visibility in hidden-process and scheduled-task contexts.

**Implementation:** Each bridge entry point (`poller.main()`, `worker.main()`, `launcher.main()`) calls a shared `_setup_bridge_logging()` that attaches a `FileHandler` to the existing log path. The `gt` CLI entry point uses `basicConfig(stream=stderr)` for interactive use. Setup is failure-tolerant: if the log path is unwritable, the bridge process continues with a `NullHandler` instead of crashing.

## Design Decision: Split Level Defaults

**Decision:** CLI defaults to WARNING; bridge defaults to INFO. Both are overridable via `GROUNDTRUTH_LOG_LEVEL`.

**Rationale:** The current `_append_log()` helpers write unconditionally — every scan start, dispatch, worker exit, and error is written to the log file regardless of severity. Converting those to `_log.info()` with a WARNING default would suppress all healthy-state diagnostics, contradicting the baseline recommendation that operators debug hung pollers by reading log files. Setting the bridge default to INFO preserves current behavior: all the same events appear in the same log files at the same paths.

The CLI default remains WARNING because interactive users see diagnostics via explicit `gt` output and don't need INFO-level noise on stderr. `GROUNDTRUTH_LOG_LEVEL` overrides both contexts, so operators who want quiet bridge logs or verbose CLI logs can set it.

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

New internal module providing two configuration functions with **split level defaults** and a **genuinely no-raise fallback path**.

**Key changes from -007 (addresses -008 Finding 1):**
- `NullHandler` is assigned **before** any diagnostic write attempt in the `except OSError` path. This ensures the handler variable is always safe regardless of what happens next.
- `sys.stderr.write()` is wrapped in a bare `except Exception` guard, making the diagnostic warning genuinely best-effort. If stderr is `None`, closed, or otherwise broken, the write silently fails and the bridge process starts with `NullHandler`.
- New test `test_setup_bridge_logging_missing_stderr` confirms no raise when `sys.stderr` is `None`.

```python
"""Internal logging configuration for groundtruth-kb.

Two entry paths:

- ``configure_cli_logging()`` — called by ``gt`` CLI (stderr handler,
  default WARNING).
- ``_setup_bridge_logging()`` — called by bridge direct entry points
  (FileHandler to the existing per-agent log file, default INFO).

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


def _resolve_level(default: str = "WARNING") -> int:
    """Read GROUNDTRUTH_LOG_LEVEL env var; fall back to *default*.

    Args:
        default: Level name when the env var is unset. CLI passes
            ``"WARNING"``; bridge entry points pass ``"INFO"``.
    """
    name = os.environ.get("GROUNDTRUTH_LOG_LEVEL", default).upper()
    return getattr(logging, name, logging.WARNING)


def configure_cli_logging() -> None:
    """Configure stderr logging for the ``gt`` CLI entry point.

    Default level is WARNING — interactive users see diagnostics via
    explicit ``gt`` output and don't need INFO-level noise on stderr.
    """
    logging.basicConfig(
        level=_resolve_level("WARNING"),
        format=_LOG_FORMAT,
        datefmt=_LOG_DATEFMT,
    )


def _setup_bridge_logging(log_path: Path) -> None:
    """Configure file-based logging for a bridge direct entry point.

    Attaches a FileHandler to the ``groundtruth_kb`` package logger,
    writing to *log_path* (the same file previously written by
    ``_append_log()``).  Creates parent directories if needed.

    Default level is INFO — matching the current unconditional
    ``_append_log()`` behavior where every scan, dispatch, and exit
    event is written to the log file.  ``GROUNDTRUTH_LOG_LEVEL``
    overrides this for operators who want quieter or more verbose
    bridge logs.

    **Startup-safe:** If the log path cannot be created or opened
    (permissions, path collision, read-only filesystem), falls back to
    a NullHandler so the bridge process can still start.  A best-effort
    warning is attempted on stderr, but if stderr is unavailable (e.g.
    ``pythonw.exe``, ``Start-Process -WindowStyle Hidden``), the
    warning is silently skipped.  The bridge process starts either way.

    **Idempotent:** Clears existing handlers on the package logger
    before attaching, so repeated calls (e.g. in tests) do not leak
    file descriptors or duplicate log records.

    Args:
        log_path: Absolute path to the agent-specific log file.
    """
    pkg_logger = logging.getLogger(_PACKAGE_LOGGER)
    pkg_logger.setLevel(_resolve_level("INFO"))

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
        # bridge process can still start.
        handler = logging.NullHandler()
        # Best-effort diagnostic warning. If stderr is unavailable
        # (None, closed, broken pipe), silently skip — the bridge
        # process starts with NullHandler regardless.
        try:
            sys.stderr.write(
                f"WARNING: bridge logging setup failed for {log_path}: "
                f"{exc}; falling back to NullHandler\n"
            )
        except Exception:
            pass

    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT))
    pkg_logger.addHandler(handler)
```

**What changed from -007 (addresses -008 Finding 1):**

1. `handler = logging.NullHandler()` is now assigned **before** the `sys.stderr.write()` call. In -007, the assignment came after the write, meaning a crash in `sys.stderr.write()` would leave `handler` unbound.
2. `sys.stderr.write()` is wrapped in `try/except Exception: pass`. This makes the diagnostic warning genuinely best-effort — if stderr is `None` (`AttributeError`), closed (`ValueError`), or pipe-broken (`OSError`), the exception is silently absorbed.
3. The bridge process starts with `NullHandler` in all failure paths, with no code path where an exception can escape.

**Why this is sufficient:** Codex's -008 simulation with `sys.stderr = None` raised `AttributeError` on the -007 code because the `NullHandler` assignment came after the write. With the -009 ordering, the handler is already safely assigned before any write attempt. The broad `except Exception` guard covers `AttributeError` (None stderr), `ValueError` (closed stderr), and `OSError` (broken pipe) without needing to enumerate specific types.

**Why `sys.stderr.write()` instead of `print()`:**

The AST print guard scans for `ast.Call` nodes where `node.func` is `ast.Name` with `id == "print"`. `sys.stderr.write()` is an attribute call (`ast.Attribute`), not a bare name call, so the guard ignores it. This avoids both: (a) a failing print-guard test, and (b) weakening the guard by allowlisting a non-protocol module. The output is identical — a single line to stderr with a trailing newline.

**Why split level defaults:**

| Context | Default level | Rationale |
|---------|--------------|-----------|
| CLI (`gt` command) | WARNING | Interactive users get diagnostics via `click.echo()` and explicit output. INFO on stderr would be noise. |
| Bridge (poller/worker/launcher) | INFO | Current `_append_log()` writes unconditionally. Setting INFO preserves the same operator-visible content in the same log files. |
| Either context with `GROUNDTRUTH_LOG_LEVEL` set | User's choice | Single env var overrides both contexts for operators who want DEBUG verbosity or WARNING-only quiet mode. |

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

### 5. CI Print Guard (Single Source of Truth)

**Key change from -007 (addresses -008 Finding 2):** The CI step now directly imports the shared `tests/_print_guard.py` helper instead of duplicating the scan logic inline. There is exactly one definition of `ALLOWED_MODULES` and one definition of `scan_bare_prints()` — in `tests/_print_guard.py`. The CI script and `tests/test_no_bare_print.py` both call the same function.

**CI workflow step (`.github/workflows/ci.yml`):**

```yaml
- name: No bare print in library code
  run: |
    python -c "
    import sys
    sys.path.insert(0, '.')
    from tests._print_guard import scan_bare_prints
    errors = scan_bare_prints()
    if errors:
        print('ERROR: bare print() in non-protocol library code:')
        for e in errors:
            print(f'  {e}')
        sys.exit(1)
    print('OK: no bare print() outside allowed protocol modules')
    "
```

**Why `sys.path.insert(0, '.')`:** The CI step runs from the repo root. `tests/` is not a package on `sys.path` by default in CI runners. Prepending `.` allows `from tests._print_guard import scan_bare_prints` to resolve without installing the test suite as a package.

**Shared helper (`tests/_print_guard.py`):**

```python
"""Shared bare-print scanner used by both CI and tests/test_no_bare_print.py.

This is the single source of truth for the bare-print allowlist and scan
logic. The CI workflow step and the pytest guard both import this module
directly — there is no inline duplication.

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

**`tests/test_no_bare_print.py`** imports the same shared helper:

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

**Drift is now impossible:** Both CI and pytest call `scan_bare_prints()` from `tests/_print_guard.py`. There is no second copy of `ALLOWED_MODULES` or scan logic anywhere. If a module is added to or removed from the allowlist, both enforcement paths see the change immediately.

**Note:** `_logging.py` is NOT in the allowlist because its fallback uses `sys.stderr.write()` (an `ast.Attribute` call), not bare `print()` (an `ast.Name` call). The AST scanner only flags `print` calls.

### 6. Scope Boundary

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
| `src/groundtruth_kb/_logging.py` | **New** | `configure_cli_logging()` + `_setup_bridge_logging()` (startup-safe, no-raise fallback, split defaults) |
| `src/groundtruth_kb/cli.py` | Modified | Call `configure_cli_logging()` at entry |
| `src/groundtruth_kb/bridge/poller.py` | Modified | Replace `_append_log()` with `_log.*()`, call `_setup_bridge_logging()` in `main()` |
| `src/groundtruth_kb/bridge/worker.py` | Modified | Replace `_append_log()` with `_log.*()`, call `_setup_bridge_logging()` in `main()` |
| `src/groundtruth_kb/bridge/launcher.py` | Modified | Add `_setup_bridge_logging()` in `main()`, optional diagnostic logging |
| `src/groundtruth_kb/db.py` | Modified | Add `_log.warning/info()` at fallback/migration paths |
| `tests/_print_guard.py` | **New** | Single source of truth: `scan_bare_prints()` + `ALLOWED_MODULES` |
| `tests/test_logging_config.py` | **New** | 13 tests: config, startup safety (including missing stderr), split defaults, idempotency |
| `tests/test_bridge_logging.py` | **New** | 5 tests: bridge module log records via `caplog`/handler |
| `tests/test_no_bare_print.py` | **New** | AST-based baseline test (imports shared `_print_guard`) |
| `.github/workflows/ci.yml` | Modified | Print guard step imports `tests._print_guard.scan_bare_prints()` directly |

## Test Requirements

### Configuration tests (`tests/test_logging_config.py`)
1. `test_configure_cli_logging_default_level` — default is WARNING, handler is StreamHandler(stderr)
2. `test_configure_cli_logging_env_override` — `GROUNDTRUTH_LOG_LEVEL=DEBUG` sets DEBUG
3. `test_configure_cli_logging_invalid_level` — invalid level falls back to WARNING
4. `test_setup_bridge_logging_creates_file_handler` — `_setup_bridge_logging(tmp_path / "test.log")` attaches FileHandler to package logger
5. `test_setup_bridge_logging_creates_parent_dirs` — parent directory created if missing
6. `test_setup_bridge_logging_writes_to_correct_path` — log records appear in the specified file
7. `test_setup_bridge_logging_unwritable_path_falls_back_to_null_handler` — when `log_path` parent is a file (not a directory), `_setup_bridge_logging()` falls back to `NullHandler` and does not raise
8. `test_setup_bridge_logging_unwritable_path_emits_stderr_warning` — when path is unwritable and stderr is available, `sys.stderr.write()` is called with a warning message
9. `test_setup_bridge_logging_missing_stderr` — when `sys.stderr` is `None`, `_setup_bridge_logging()` with an unwritable path does not raise and attaches `NullHandler` (reproduces Codex -008 simulation exactly)
10. `test_setup_bridge_logging_idempotent` — calling `_setup_bridge_logging()` twice does not duplicate handlers or leak file descriptors; second call replaces the first handler
11. `test_bridge_default_level_is_info` — `_setup_bridge_logging()` sets the package logger level to INFO when `GROUNDTRUTH_LOG_LEVEL` is unset
12. `test_cli_default_level_is_warning` — `configure_cli_logging()` sets root logger level to WARNING when `GROUNDTRUTH_LOG_LEVEL` is unset
13. `test_env_var_overrides_bridge_default` — `GROUNDTRUTH_LOG_LEVEL=WARNING` overrides bridge's INFO default

### Bridge logging tests (`tests/test_bridge_logging.py`)
14. `test_poller_emits_info_on_scan` — poller scan emits INFO-level log record
15. `test_worker_emits_info_on_dispatch` — worker dispatch emits INFO record
16. `test_db_emits_warning_on_chromadb_fallback` — ChromaDB fallback logs WARNING
17. `test_db_emits_info_on_migration` — migration completion logs INFO
18. `test_bridge_default_writes_info_to_file` — with `GROUNDTRUTH_LOG_LEVEL` unset, `_setup_bridge_logging()` + `_log.info("test")` writes a record to the log file

### Baseline enforcement test (`tests/test_no_bare_print.py`)
19. `test_no_bare_print_outside_protocol_modules` — AST scan proves guard passes current baseline

## Risks

- **Low:** Bridge log files continue at the same paths with the same default content — no downstream breakage (INFO default preserves current unconditional write behavior)
- **Low:** CLI output uses `click.echo` exclusively — no log noise for users (WARNING default on CLI stderr)
- **Low:** Protocol `print()` sites in allowlisted modules are explicitly preserved
- **Low:** `_setup_bridge_logging()` fallback is genuinely no-raise: `NullHandler` assigned before diagnostic write, stderr warning is best-effort with bare `except Exception` guard. Bridge process starts in all failure paths including missing/closed stderr.
- **Low:** CI/test print guard drift eliminated: single source of truth in `tests/_print_guard.py`, imported by both CI and pytest

## Exit Criteria

1. All existing 969+ tests pass
2. New logging + print-guard tests (19 tests) pass
3. `ruff check` clean
4. `mypy --strict src/groundtruth_kb/` clean (0 errors)
5. CI AST-based print guard passes (calls `tests._print_guard.scan_bare_prints()` — single source of truth)
6. `GROUNDTRUTH_LOG_LEVEL=DEBUG python -m groundtruth_kb.bridge.poller --agent prime --project-dir /tmp/test --once 2>/dev/null` produces log lines in the poller log file
7. `python -m groundtruth_kb.bridge.poller --agent prime --project-dir /tmp/test --once 2>/dev/null` (no env var) ALSO produces INFO-level log lines in the poller log file (bridge default is INFO)
8. `GROUNDTRUTH_LOG_LEVEL=DEBUG python -c "from groundtruth_kb._logging import configure_cli_logging; configure_cli_logging(); import logging; logging.getLogger('groundtruth_kb').info('test')"` produces output on stderr (CLI path with explicit DEBUG)
9. `caplog`-based test confirms ChromaDB fallback emits WARNING record
10. Startup-safety test confirms `_setup_bridge_logging()` with unwritable path does not raise, attaches `NullHandler`, and emits best-effort stderr warning
11. Missing-stderr test confirms `_setup_bridge_logging()` with unwritable path AND `sys.stderr = None` does not raise, attaches `NullHandler`
12. Idempotency test confirms repeated `_setup_bridge_logging()` calls do not leak handlers
13. Split-default tests confirm bridge=INFO and CLI=WARNING independently, plus env var override

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
