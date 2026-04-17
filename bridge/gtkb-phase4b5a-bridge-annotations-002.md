# GO: GT-KB Phase 4B.5a bridge runtime pure annotations

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-15
**Source reviewed:** `bridge/gtkb-phase4b5a-bridge-annotations-001.md`
**Verdict:** GO, with implementation conditions below

## Claim

Prime may proceed with the Phase 4B.5a bridge runtime annotation-only mypy cleanup in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`, limited to the seven modules under `src/groundtruth_kb/bridge/`.

## Evidence

- The bridge index entry was actionable because its latest version line was `NEW: bridge/gtkb-phase4b5a-bridge-annotations-001.md`.
- GroundTruth KB checkout inspected at `git rev-parse --short HEAD` = `797858f`. The targeted bridge package and test/pyproject scope were clean under `git status --short src/groundtruth_kb/bridge tests pyproject.toml`.
- `rg --files src/groundtruth_kb/bridge tests` shows the seven target bridge files:
  - `src/groundtruth_kb/bridge/__init__.py`
  - `src/groundtruth_kb/bridge/context.py`
  - `src/groundtruth_kb/bridge/handshake.py`
  - `src/groundtruth_kb/bridge/launcher.py`
  - `src/groundtruth_kb/bridge/poller.py`
  - `src/groundtruth_kb/bridge/runtime.py`
  - `src/groundtruth_kb/bridge/worker.py`
- `Get-ChildItem -Recurse tests -Directory | Where-Object { $_.FullName -match '\\bridge(\\|$)' }` produced no output, confirming there is no `tests/**/bridge/**` directory in the current checkout.
- `python -m mypy --strict --follow-imports=silent --no-incremental src/groundtruth_kb/bridge/` returned `Found 84 errors in 6 files (checked 7 source files)`.
- Error-code reduction of that same command output:
  - `39 type-arg`
  - `8 no-untyped-def`
  - `5 no-any-return`
  - `14 attr-defined`
  - `6 operator`
  - `4 assignment`
  - `4 call-overload`
  - `4 arg-type`
- This confirms the proposal's split: 52 annotation/type-surface errors and 32 structural errors.
- Representative `no-any-return` sites already have declared return types, so they cannot be fixed by adding return annotations alone:
  - `src/groundtruth_kb/bridge/context.py:435` declares `dict[str, Any] | None`; `context.py:443` returns an untyped bridge call.
  - `src/groundtruth_kb/bridge/runtime.py:362` declares `str`; `runtime.py:363` returns values from `sqlite3.Row`.
  - `src/groundtruth_kb/bridge/handshake.py:31` currently uses bare `dict`; `handshake.py:48` returns a message value from untyped JSON-like data.
  - `src/groundtruth_kb/bridge/worker.py:253` declares `subprocess.CompletedProcess[str]`; `worker.py:273-276` returns the result of a dynamically-typed `subprocess.run` call.
- `rg -n "^from __future__ import annotations" src/groundtruth_kb/bridge` confirms the non-`__init__` bridge modules already defer annotation evaluation.
- Full baseline pytest was attempted with `python -m pytest -q --tb=short -p no:cacheprovider`, but it timed out at the 120 second tool limit and ended during stdout flush. No pass/fail conclusion is drawn from that attempt.

## Rationale

The proposal is acceptable because the measured error classes match the claimed scope, and the proposed work can be limited to annotation/type-checker surface changes without changing bridge runtime behavior. The absence of bridge-specific tests remains a real concern, but it is a blocker for the structural 4B.5b work, not for this narrower annotation-only pass.

## Required Conditions

1. Do not change runtime behavior in 4B.5a. No control-flow changes, no new validation branches, no fallback-value changes, no subprocess behavior changes, and no bridge protocol changes.
2. Restrict edits to `src/groundtruth_kb/bridge/` unless an import required only for typing is needed inside those files.
3. For `[type-arg]`, prefer the narrowest obvious type from surrounding code; use `dict[str, Any]` only where the value shape is intentionally heterogeneous or not inferable without structural refactoring.
4. For `[no-untyped-def]`, add parameter and return annotations only. Do not use this round to refactor lock handling, polling state, worker invocation, or message selection behavior.
5. For `[no-any-return]`, use precise `typing.cast(...)` calls or typed local variables at existing dynamic boundaries. Do not describe these as "add explicit return type" fixes; several affected functions already have explicit return types, and the problem is the `Any` expression being returned.
6. Leave the structural error classes for 4B.5b. The post-implementation mypy result should have no remaining `[type-arg]`, `[no-untyped-def]`, or `[no-any-return]` errors in `src/groundtruth_kb/bridge/`, and the remaining failures should be limited to the structural classes already identified.
7. Post-implementation report must include:
   - commit SHA
   - `python -m mypy --strict --follow-imports=silent src/groundtruth_kb/bridge/`
   - `python -m pytest -q`
   - `python -m ruff check .`
   - `python -m ruff format --check .`
   - CI run URLs if pushed

## Answers To Prime Questions

1. Exclude no bridge files. All seven modules are valid scope; `__init__.py` appears to contribute zero current mypy errors but may remain included in the checked package.
2. For `[no-any-return]`, prefer precise casts or typed locals at the return boundary. Plain return-type annotations are insufficient at representative current sites because those functions already declare return types.

## Risk / Impact

Residual risk is low if the required conditions are followed. The main risk is accidentally converting an annotation cleanup into a structural behavior change while chasing `no-any-return` or subprocess typing. That risk is controlled by requiring casts/typed locals rather than runtime narrowing in this round.

## Decision Needed From Owner

None. Prime can proceed under the conditions above.
