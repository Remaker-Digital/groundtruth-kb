GO

# Loyal Opposition Review - GTKB-STARTUP-EVIDENCE-RESTORATION

Reviewed: 2026-04-27
Subject: `bridge/gtkb-startup-evidence-restoration-001.md`
Scope: `scripts/session_self_initialization.py` import resolution and Windows UTF-8 hook output

## Claim

GO, with implementation constraints. The proposed fix addresses a real startup evidence blocker: importlib-based tests cannot resolve the relocated `_wrap_io` module, and Windows hook output can fail when non-ASCII startup context is printed to a legacy encoded console.

## Evidence

- `scripts/session_self_initialization.py` imports `sys` and `Path` at top level: `scripts/session_self_initialization.py:14` and `:18`.
- The failing import is the bare `_wrap_io` import at `scripts/session_self_initialization.py:3240`.
- Existing tests load the script through `importlib.util.spec_from_file_location()` without putting `scripts/` on `sys.path`: `tests/scripts/test_session_self_initialization.py:14` to `:19`.
- The hook context path prints JSON with `ensure_ascii=False`: `scripts/session_self_initialization.py:4900`, with another machine-readable JSON output path at `scripts/session_self_initialization.py:5103`.
- A direct-execution subprocess regression guard already exists for the actual hook command shape: `tests/scripts/test_session_self_initialization.py:1221` to `:1252`.

## Required Implementation Constraints

- Insert the script directory into `sys.path` only if it is not already present. The proposed unconditional `sys.path.insert(0, ...)` would duplicate the same path every time the test helper imports the module.
- Prefer the existing top-level `sys` and `Path` imports rather than adding `_sys` / `_Path` aliases at line 3240, unless ruff or a concrete shadowing issue requires aliases.
- Keep the change narrow to `_wrap_io` import resolution and output encoding. Do not refactor the surrounding 5k-line startup script.
- Add a regression guard for importlib loading with `scripts/` absent from `sys.path`.
- Add a regression guard for cp1252-like stdout using a controlled text stream. This should run cross-platform by substituting the stream; it does not need to be Windows-only.
- Ensure encoding mitigation covers both hook-context JSON and other machine-readable startup JSON paths that use `ensure_ascii=False`.

## Risk / Impact

This fix is startup-critical. Without it, the existing startup evidence tests remain red and a Windows fresh-session hook can fail before delivering the required startup disclosure.

## Verification Expected

- `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short`
- `python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py`
- `python -m ruff format --check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py`
- Direct smoke of `python scripts/session_self_initialization.py --emit-startup-service-payload --fast-hook --skip-bridge-maintenance` from PowerShell.

## Decision Needed From Owner

None.
