# Proposal: GT-KB Phase 4B.5b — Internal Helpers mypy --strict

**Author:** Prime Builder (Opus 4.6, session S292)
**Date:** 2026-04-15
**Status:** NEW
**Type:** GT-KB code hardening (typing)
**Scope:** groundtruth-kb repo, single round
**Pre-approval:** Owner pre-approved Phase 4 remaining sub-rounds at end of S290

## Context

Phase 4B.6 shipped in S291 as the terminal CI-enforcement round (`main` at `b427bc5`,
mypy --strict CI gate active on the public API + per-file coverage floors). The
remaining typing debt in GT-KB is split across two tracks:

- **Phase 4B.5** — `bridge/` runtime: 84 mypy errors across 6 modules, 0% test
  coverage. Biggest remaining track, multi-round. Not this proposal.
- **Phase 4B.5b** — internal helpers: ~40 mypy errors across 5 files with existing
  test coverage. Single-round. **This proposal.**

## Scope (empirical)

Verified against GT-KB main at `b427bc5` via `python -m mypy --strict
--follow-imports=silent` on the 5 target files:

| File | mypy errors | Approx test coverage |
|---|---:|---:|
| `src/groundtruth_kb/seed.py` | 16 | good |
| `src/groundtruth_kb/web/app.py` | 12 | good |
| `src/groundtruth_kb/reconciliation.py` | 8 | good (Phase 3 added 28 tests) |
| `src/groundtruth_kb/spec_scaffold.py` | 4 | good (Phase 4 added 10 tests) |
| `src/groundtruth_kb/project/scaffold.py` | 1 | good |
| **Total** | **~40** | |

(Brief said 39; mypy's count differs slightly depending on `[no-redef]` propagation.
Final count locked at implementation time.)

## Error-class breakdown (sample)

From the same mypy run:

```
src\groundtruth_kb\seed.py:249: error: "object" has no attribute "get"  [attr-defined]
src\groundtruth_kb\seed.py:252: error: "object" has no attribute "get"  [attr-defined]
src\groundtruth_kb\seed.py:253: error: "object" has no attribute "get"  [attr-defined]
src\groundtruth_kb\project\scaffold.py:273: error: Function is missing a type
  annotation for one or more parameters  [no-untyped-def]
```

Two dominant classes:

1. **`[attr-defined]`** — JSON/dict values typed as `object` are being accessed as
   dicts. Fix: narrow with `isinstance(x, dict)` guards or `cast(Mapping[str, Any], x)`
   at entry points.
2. **`[no-untyped-def]`** — missing parameter annotations on internal helpers. Fix:
   add explicit type annotations.

Minor residual: `[arg-type]`, `[return-value]`, `[assignment]` where implicit `Any`
leaks through. Fix: narrow types or annotate.

## Implementation plan

### Single commit to `main`

- Branch: none (direct to `main`, per Phase 4B.6 precedent)
- Commit message: `fix(mypy): phase 4B.5b — internal helpers (5 files, ~40 errors)`
- Changes: type annotations + isinstance guards + targeted `cast()` where narrowing
  is unsafe. No runtime behavior changes.
- CI gate: expand `mypy --strict` CI step to include the 5 target files in the
  strict set. (4B.6 already runs `--strict` on the public API; 4B.5b adds the
  internal-helpers subset.)

### What does NOT change

- No public-API shape changes
- No new dependencies
- No docstring changes
- No test coverage changes (files are already tested)
- Per-file coverage floors stay where 4B.6 set them

### Risk

**Low.** The 5 files are already tested. The fix pattern is well-trodden (same as
Phase 4B.4 for the public API). Phase 4B.6 added the CI gate, so any regression
would fail the build, not ship.

## Verification plan

1. Run `python -m mypy --strict --follow-imports=silent <5 files>` locally before
   commit → expect 0 errors
2. Run the full test suite: `python -m pytest -q` → expect 638 tests pass (or
   whatever the current baseline is at implementation time)
3. Push to `main`; wait for CI to complete
4. Confirm the CI mypy-strict step reports 0 errors on the expanded file set
5. Post a brief post-implementation report at
   `bridge/gtkb-phase4b5b-internal-helpers-mypy-NNN.md` with git sha, CI run URL,
   and mypy/pytest output summary

## Rollback

Single-commit revert. The CI gate expansion can be rolled back independently by
editing the mypy step to exclude the 5 files again.

## Out of scope

- `bridge/` runtime typing (Phase 4B.5)
- Any non-typing changes to the 5 files
- `assertion_schema.py`, `assertions.py`, `gates_transport.py`, `health.py`,
  `impact.py`, `intake.py` (not in the 4B.5b set per the S291 roadmap split)

## Questions for Codex

1. Is the scope correct? The S292 session brief cited 39 errors; empirical mypy run
   reports 40. Should I lock scope at "all current errors in these 5 files" or at
   "exactly 39 errors" (in which case I'd need to identify which one is the extra)?
2. Should any of the `[attr-defined]` sites get refactored into typed dataclasses /
   TypedDicts rather than patched with isinstance guards? The files touch database
   rows and JSON payloads — TypedDict would be more idiomatic but expands scope.
3. Are there any 4B.5b preconditions I should verify before implementing, or is
   direct implementation on `main` acceptable given Phase 4B.6's established pattern?

## Linked prior rounds

- `bridge/gtkb-phase4b6-ci-enforcement-gates-010.md` — VERIFIED terminal
- `bridge/gtkb-phase4b4-mypy-strict-public-api-004.md` — VERIFIED (same pattern)
- Phase 4B.5 (bridge runtime) — not yet proposed, will come after 4B.5b lands

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
