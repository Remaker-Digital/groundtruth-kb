# GT-KB Phase 4C — Structured Logging Migration: Revised Post-Implementation Report

**Status:** REVISED (addresses NO-GO -012 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S298
**Repo:** groundtruth-kb (main, HEAD: `8efcbb1`, uncommitted changes)
**Bridge thread:** gtkb-phase4c-structured-logging
**Prior versions:** -001 through -012 (GO at -010, post-impl -011, NO-GO -012)

## NO-GO -012 Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1: Ruff format failure in `tests/test_public_api_type_checks.py` | High | Add missing blank line before `PUBLIC_API_FILES` (PEP 8 / Ruff E303 — two blank lines required between top-level definitions). Run `ruff format` on the file. |
| F2: Non-protocol bare print at `bridge/poller.py:455` not migrated | Medium | Convert `print("bridge_poller: agent must be 'codex' or 'prime'", file=sys.stderr)` → `_log.error("bridge_poller: agent must be 'codex' or 'prime'")` + `return 1`. Tighten print guard from module-level allowlist to line-level `# print-ok` convention for the remaining protocol JSON print at line 544. |

## Exact Changes

### Change 1 — Ruff format fix (`tests/test_public_api_type_checks.py`)

Insert one blank line between the `_clean_subprocess_env()` function (ends line 33) and `PUBLIC_API_FILES` (line 35), producing the two-blank-line separation Ruff requires between top-level definitions.

Before:
```python
    return {k: v for k, v in os.environ.items() if not (k.startswith("COV_") or k.startswith("COVERAGE_"))}

PUBLIC_API_FILES = [
```

After:
```python
    return {k: v for k, v in os.environ.items() if not (k.startswith("COV_") or k.startswith("COVERAGE_"))}


PUBLIC_API_FILES = [
```

### Change 2 — Poller stderr print → `_log.error()` (`src/groundtruth_kb/bridge/poller.py`)

Before (line 455):
```python
        print("bridge_poller: agent must be 'codex' or 'prime'", file=sys.stderr)
```

After:
```python
        _log.error("bridge_poller: agent must be 'codex' or 'prime'")
```

`_log` is already `logging.getLogger(__name__)` at line 34 and `_setup_bridge_logging()` is wired in `main()` before `run()` is called. The error will route to the bridge log file (or `NullHandler` if logging setup failed) — same path as all other diagnostic messages in this module.

### Change 3 — Tighten print guard (`tests/_print_guard.py`)

Replace the module-level `ALLOWED_MODULES` exemption for `bridge/poller.py` with a line-level `# print-ok` comment convention. The single remaining protocol print (once-mode JSON output at ~line 544) gets a `# print-ok: protocol JSON output` inline comment. The scanner checks for `# print-ok` on lines containing `print(` calls in non-allowlisted modules.

Before (`tests/_print_guard.py`):
```python
ALLOWED_MODULES: frozenset[str] = frozenset(
    {
        "governance/output.py",  # Hook JSON protocol
        "bridge/launcher.py",  # Health-check JSON protocol
        "bridge/handshake.py",  # Bridge handshake protocol
        "bridge/runtime.py",  # MCP dependency warning
        "bridge/poller.py",  # Once-mode JSON protocol output
        "__main__.py",  # CLI entry
    }
)
```

After:
```python
ALLOWED_MODULES: frozenset[str] = frozenset(
    {
        "governance/output.py",  # Hook JSON protocol
        "bridge/launcher.py",  # Health-check JSON protocol
        "bridge/handshake.py",  # Bridge handshake protocol
        "bridge/runtime.py",  # MCP dependency warning
        "__main__.py",  # CLI entry
    }
)
```

Scanner update — after the `ALLOWED_MODULES` skip, add a `# print-ok` check:

```python
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
                # Check for # print-ok inline authorization
                source_lines = py.read_text(encoding="utf-8").splitlines()
                if node.lineno <= len(source_lines) and "# print-ok" in source_lines[node.lineno - 1]:
                    continue
                errors.append(f"{rel}:{node.lineno}")
```

And in `bridge/poller.py`, the once-mode JSON print gets the marker:
```python
                print(  # print-ok: protocol JSON output
                    json.dumps(
                        {
                            "ok": True,
                            ...
```

## Verification Plan

After applying all three changes:

1. `python -m ruff check src/ tests/` — expect "All checks passed!"
2. `python -m ruff format --check src/ tests/` — expect all files formatted
3. `python -m pytest tests/test_logging_config.py tests/test_bridge_logging.py tests/test_no_bare_print.py tests/test_public_api_type_checks.py -q --tb=short` — expect 20 passed
4. Grep `bridge/poller.py` for any remaining bare `print(` without `# print-ok` — expect only the once-mode JSON line with the marker

## Risk Assessment

All three changes are minimal, local, and have no behavioral impact:
- Change 1: whitespace only
- Change 2: redirects an error message from stderr to the structured log — same text, same early-return behavior
- Change 3: tightens the guard (makes it stricter, not weaker) while preserving the protocol print exemption via explicit opt-in

No owner decision needed. The poller stderr print is unambiguously diagnostic output, not user-facing protocol, so converting it to `_log.error()` is the correct Phase 4C action per the approved -009/-010 design.

---
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
