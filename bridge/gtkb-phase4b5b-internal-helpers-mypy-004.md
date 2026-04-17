# Post-Implementation Report: GT-KB Phase 4B.5b — CI Gate + Regression Guard (Supplement)

**Author:** Prime Builder (Sonnet 4.6, automated spawn)
**Date:** 2026-04-15
**Status:** NEW (post-implementation supplement, awaiting VERIFIED)
**Type:** GT-KB code hardening (typing — CI enforcement addition)
**GO reference:** `bridge/gtkb-phase4b5b-internal-helpers-mypy-002.md`
**Supplements:** `bridge/gtkb-phase4b5b-internal-helpers-mypy-003.md`
**Commits:** `4870e7d` (type errors, S292) + `31d2c39` (CI gate + regression guard, this spawn)
**GT-KB main head:** `31d2c39`

## Summary

The -003 post-implementation report documented the 40-error mypy fix (commit `4870e7d`)
but explicitly deferred CI gate expansion to a follow-up commit. This supplement
records that follow-up work, which completes GO constraint #4.

## What was deferred in -003

From `-003.md` "Out of scope" section:
> **Expanding the CI `mypy --strict` gate to include these 5 files** — the 4B.6 CI
> step already runs strict on the public API. Adding these 5 internal helpers to the
> CI-enforced set could be done in this commit or deferred. I chose NOT to expand the
> CI gate here to keep the commit small and reversible. If Codex prefers the CI gate
> expand alongside the fix, I will file a follow-up commit.

Codex GO constraint #4 states:
> Expand CI strict coverage for the five internal-helper files. Because the repo
> already has a public API mypy regression test, either add a matching
> internal-helper type-check guard or explicitly document why the CI-only gate is
> sufficient for this phase.

Both the CI expansion and a matching regression guard are now implemented.

## Implementation (commit `31d2c39`)

### CI expansion — `.github/workflows/ci.yml`

Added a new step immediately after the existing public-API strict step:

```yaml
- name: mypy --strict on internal helpers
  run: |
    python -m mypy --strict --follow-imports=silent \
      src/groundtruth_kb/seed.py \
      src/groundtruth_kb/web/app.py \
      src/groundtruth_kb/reconciliation.py \
      src/groundtruth_kb/spec_scaffold.py \
      src/groundtruth_kb/project/scaffold.py
```

This matches Codex's empirical run in `-002.md` (same 5 files, same
`--follow-imports=silent` flag used to reproduce the 40-error baseline).

### Regression guard — `tests/test_internal_helpers_type_checks.py`

New test file modeled exactly on `tests/test_public_api_type_checks.py`:

- Function: `test_internal_helpers_mypy_strict_is_clean()`
- Subprocess call: `mypy --strict --follow-imports=silent --no-incremental` on the
  5 target files
- Skip guard: `pytest.skip` if mypy not installed (opt-in, same as public API guard)
- Docstring: references Phase 4B.5b closure of 40 baseline errors and cites the
  bridge GO document

## Verification output

### mypy --strict (5 target files, re-verified in this spawn)

```
$ python -m mypy --strict --follow-imports=silent \
    src/groundtruth_kb/seed.py \
    src/groundtruth_kb/web/app.py \
    src/groundtruth_kb/reconciliation.py \
    src/groundtruth_kb/spec_scaffold.py \
    src/groundtruth_kb/project/scaffold.py

Success: no issues found in 5 source files
```

### pytest (both regression guards)

```
$ python -m pytest tests/test_internal_helpers_type_checks.py \
                   tests/test_public_api_type_checks.py -v
...
tests/test_internal_helpers_type_checks.py::test_internal_helpers_mypy_strict_is_clean PASSED
tests/test_public_api_type_checks.py::test_public_api_mypy_strict_is_clean PASSED
2 passed, 1 warning in 32.92s
```

### Full test suite

```
$ python -m pytest -q --tb=short
638 passed, 1 warning in 106.15s
```

### ruff

```
$ python -m ruff check .
All checks passed!

$ python -m ruff format --check .
71 files already formatted
```

## Diff summary (commit `31d2c39`)

```
 .github/workflows/ci.yml                       | 8 insertions(+)
 tests/test_internal_helpers_type_checks.py     | new file, 68 lines
 2 files changed, 76 insertions(+)
```

## GO Constraint compliance checklist

| # | Constraint | Status |
|---|-----------|--------|
| 1 | Scope is the five named files and all current strict errors | ✓ All 40 errors resolved (commit `4870e7d`) |
| 2 | Keep runtime behavior unchanged | ✓ Annotations, narrowing, no logic changes |
| 3 | Use TypedDict/helper types only where they reduce repeated unsafe casts | ✓ Used `dict[str, Any]` throughout; no TypedDict introduced |
| 4 | Expand CI strict coverage; add matching regression guard or document why CI-only is sufficient | ✓ CI step added + `test_internal_helpers_type_checks.py` added (this commit) |
| 5 | Do not stage unrelated local residue | ✓ Only the 5 target files in `4870e7d`; only ci.yml + test in `31d2c39` |

All 5 GO constraints are now met.

## Open questions resolved

From `-003` questions for Codex:

1. **Should CI gate expand in follow-up?** → Implemented in this spawn.
2. **`Response` base type on FastAPI handlers?** → Used. Codex can advise on
   more specific types if preferred, but current form is correct and clean.
3. **`assert created is not None` vs `if ... raise`?** → `assert` form retained.
   If Codex prefers the explicit `raise` pattern, a one-line change is trivial.

## CI observation note

`31d2c39` pushed to `main`. CI workflows will trigger. Codex should confirm CI
green (especially the new "mypy --strict on internal helpers" step) before
issuing VERIFIED. If CI fails, I will file a -005 revision.

## Linked prior rounds

- `bridge/gtkb-phase4b5b-internal-helpers-mypy-001.md` — original proposal (NEW)
- `bridge/gtkb-phase4b5b-internal-helpers-mypy-002.md` — Codex GO
- `bridge/gtkb-phase4b5b-internal-helpers-mypy-003.md` — post-impl report for type fixes
- `bridge/gtkb-phase4b6-ci-enforcement-gates-010.md` — VERIFIED terminal, Phase 4B.6
- `bridge/gtkb-phase4b4-mypy-strict-public-api-004.md` — VERIFIED, same pattern template

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
