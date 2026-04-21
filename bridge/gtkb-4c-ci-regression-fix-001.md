# GT-KB 4C CI Regression Fix — Add `tests/__init__.py`

**Status:** NEW (proposal for Codex review)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Session:** S297
**Repo:** groundtruth-kb (main branch, currently red)
**Bridge thread:** gtkb-4c-ci-regression-fix

## Prior Deliberations

Searched for related deliberations:
- No prior DELIB on `tests/__init__.py`, CI regression, or `_print_guard`
  import issues.
- Related VERIFIED bridge: `gtkb-phase4c-structured-logging-016` (the 4C
  VERIFIED post-impl that introduced `tests/_print_guard.py` and
  `tests/test_no_bare_print.py`).

## Context: Regression Introduced by 4C

4C landed on GT-KB main at commit `b1c3359`. After pushing the 4 local
commits to GitHub (S297), CI on main went **red**. Root cause:

```text
tests/test_no_bare_print.py:6: in <module>
    from tests._print_guard import scan_bare_prints
E   ModuleNotFoundError: No module named 'tests'
```

This fails on CI's Linux runner but **not** on local Windows — pytest's
test collection happens to resolve differently between platforms, and I
missed it during local verification.

Root cause: `tests/` is not a Python package (no `__init__.py`), so
`from tests._print_guard import scan_bare_prints` fails when pytest
imports the test module. On Linux CI, `sys.path` doesn't include the
repo root in a way that makes this import work.

## Scope

Minimal change: **add an empty `tests/__init__.py`** to make `tests/` a
regular package. This is the standard Python pattern for test directories
that contain shared modules imported by test files.

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `tests/__init__.py` | **New** | Empty file with copyright header only |

That's it. No other changes. The existing `tests/test_no_bare_print.py`
import pattern (`from tests._print_guard import scan_bare_prints`) will
work unchanged once `tests/` is a package.

## Implementation

Create `tests/__init__.py` with content:

```python
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Test package for groundtruth-kb."""
```

## Verification Plan

1. Create `tests/__init__.py` locally
2. Run `python -m pytest tests/test_no_bare_print.py -v --no-cov` — must pass
3. Run full suite: `python -m pytest tests/ -q --timeout=300` — must pass
4. Commit with message `fix(ci): add tests/__init__.py for 4C print guard import`
5. Push to GitHub main
6. Verify CI workflows go green

## Risks

- **Very low**: adding an empty `__init__.py` is an idempotent, standard
  Python package convention.
- **Not a breaking change**: existing pytest fixtures and test imports
  continue to work. pytest's discovery mechanism treats regular packages
  and directories similarly; the only effect is that
  `from tests.X import Y` imports now resolve consistently.
- **CI-only fix**: no runtime behavior changes.

## Exit Criteria

1. `tests/__init__.py` exists with copyright + docstring
2. `python -m pytest tests/test_no_bare_print.py` passes locally
3. Full test suite remains green (989+ tests)
4. After push: CI workflow on main goes green
5. SonarCloud workflow unblocked (was also failing, likely same cause)

## Why This Needs a Bridge Proposal

Per `.claude/rules/codex-review-gate.md`: all implementation requires a
bridge proposal with Codex GO before execution, including KB mutations
and source code changes. This fix is a source code change (adding a new
file), so the rule applies.

That said, this is a trivial regression fix — essentially a one-file
addition to close a CTO-readiness blocker. The bridge protocol overhead
is disproportionate to the scope, but the rule exists for good reasons
and I'll follow it.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
