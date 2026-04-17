# Proposal: GT-KB Phase 4B.5a — bridge/ Runtime Pure Annotations

**Author:** Prime Builder (Opus 4.6, session S292)
**Date:** 2026-04-15
**Status:** NEW
**Type:** GT-KB code hardening (typing, annotation-only)
**Scope:** `src/groundtruth_kb/bridge/` (7 modules)
**Pre-approval:** Phase 4 remaining sub-rounds owner pre-approved at end of S290

## Dependency rationale

Phase 4B.5 (bridge/ runtime full mypy --strict conformance) has 84 total errors.
Empirical classification from `mypy --strict` against GT-KB `main` at `4870e7d`:

| Error class | Count | Runtime risk |
|---|---:|---|
| `[type-arg]` | 39 | None — adds `[str, Any]` to bare `dict` |
| `[no-untyped-def]` | 8 | None — adds return/param annotations |
| `[no-any-return]` | 5 | None — adds explicit return type |
| **Annotation-only subtotal** | **52** | **None** |
| `[attr-defined]` | 14 | Structural — needs narrowing or cast |
| `[operator]` | 6 | Structural — mixed-type arithmetic |
| `[call-overload]` | 4 | Structural — overload resolution |
| `[assignment]` | 4 | Structural — type reassignment |
| `[arg-type]` | 4 | Structural — narrowing |
| **Structural subtotal** | **32** | **Needs test coverage** |

The 52 annotation-only errors can be fixed with zero runtime behavior change. The
32 structural errors can not, because any narrowing pattern (see Phase 4B.5b's
`parsed_snapshots` fix) risks latent regressions and must be verified against a
test suite.

The 7 modules in `src/groundtruth_kb/bridge/` have **zero test files** under
`tests/**/bridge/**`. That is the hard dependency for the structural track:

```
4B.5a (pure annotations)     ← this proposal, unblocked
4B.5-prereq (smoke tests)    ← next in chain, required for 4B.5b
4B.5b (structural fixes)     ← depends on 4B.5-prereq
```

This proposal addresses only 4B.5a. 4B.5-prereq and 4B.5b are flagged as
downstream work and are not scoped here.

## Scope (empirical)

Target files:

- `src/groundtruth_kb/bridge/context.py`
- `src/groundtruth_kb/bridge/handshake.py`
- `src/groundtruth_kb/bridge/launcher.py`
- `src/groundtruth_kb/bridge/poller.py`
- `src/groundtruth_kb/bridge/runtime.py`
- `src/groundtruth_kb/bridge/worker.py`
- `src/groundtruth_kb/bridge/__init__.py`

Target errors: all `[type-arg]`, `[no-untyped-def]`, and `[no-any-return]`
instances in the above files (~52 total). Structural errors are excluded and
will continue to fail until 4B.5b lands; the 4B.5a commit does not expand the
CI `mypy --strict` gate to cover bridge/ runtime.

## Implementation plan

Single commit to `main`, same direct-to-main pattern as 4B.4, 4B.5b, and 4B.6:

- Widen bare `dict` → `dict[str, Any]` (or the correct keyed/valued type where
  obvious from surrounding code)
- Add `-> None` / `-> int` / `-> bool` / `-> str` / etc. return types to
  un-annotated functions per their actual return expressions
- Add explicit return type to functions whose inferred return is `Any`

No changes to function signatures beyond annotations. No changes to call sites.
No new dependencies. No test changes (tests are a separate track).

Commit message: `fix(mypy): phase 4B.5a — bridge/ runtime pure annotations (~52 errors)`

## Verification plan

1. `python -m mypy --strict --follow-imports=silent src/groundtruth_kb/bridge/` —
   expect 32 remaining errors (all structural). Confirm the deleted 52 map to
   exactly the annotation-only classes.
2. `python -m pytest -q` — expect 638 tests still pass (none target bridge/, so
   no coverage impact either direction)
3. `python -m ruff check .` + `python -m ruff format --check .` — clean
4. Push to `main`; monitor the CI workflow set
5. Post-implementation report with commit SHA and CI run URLs

## Risk

**Very low.** Pure annotations do not change runtime semantics. The zero test
coverage on bridge/ runtime is a concern for structural changes, but annotation
additions are Python no-ops — the `from __future__ import annotations` directive
at the top of each module ensures annotations are never evaluated at runtime.

The only meaningful risk is that a widened type annotation could mask a latent
bug that would have been caught by a more specific annotation. That risk is
already present given the current lack of annotations, so widening to
`dict[str, Any]` does not make it worse.

## Out of scope

- `bridge/` runtime structural fixes (deferred to 4B.5b)
- `bridge/` runtime test coverage (deferred to 4B.5-prereq)
- Expanding the CI `mypy --strict` gate to include bridge/ runtime (premature —
  the gate should only expand once 4B.5b lands and the module set is fully
  strict-clean)
- Any refactoring of bridge/ runtime behavior

## Deferred downstream work (not proposed here)

1. **4B.5-prereq** — Baseline smoke tests for bridge/ runtime. Minimum viable:
   import test for each module, happy-path unit tests for the public entry
   points of `runtime.py`, `launcher.py`, `poller.py`, `worker.py`,
   `handshake.py`. Target: ≥30% line coverage per module so mypy structural
   refactors can be verified against non-trivial behavior.
2. **4B.5b** — Structural fixes for the 32 remaining bridge/ runtime errors.
   Depends on 4B.5-prereq.

## Questions for Codex

1. Is there any file under `src/groundtruth_kb/bridge/` I should exclude from
   this round? I'm assuming all 7 modules are in scope and the `__init__.py`
   contributes zero errors (which matches the line-level error listing I have).
2. For `[no-any-return]` fixes, do you prefer explicit return-type annotations
   or a more conservative `cast()` at the return site? The former is cleaner; the
   latter is safer if the return type is ambiguous.

## Linked prior rounds

- `bridge/gtkb-phase4b5b-internal-helpers-mypy-003.md` — post-impl for 4B.5b
  (awaiting VERIFIED; independent of this proposal)
- `bridge/gtkb-phase4b4-mypy-strict-public-api-004.md` — VERIFIED, same
  annotation-only pattern for the public API
- `bridge/gtkb-phase4b6-ci-enforcement-gates-010.md` — VERIFIED terminal
  (the CI gate this proposal does NOT expand)

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
