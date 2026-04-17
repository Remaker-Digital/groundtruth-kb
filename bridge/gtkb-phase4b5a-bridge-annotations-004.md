# NO-GO: GT-KB Phase 4B.5a bridge runtime pure annotations verification

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-15
**Source reviewed:** `bridge/gtkb-phase4b5a-bridge-annotations-003.md`
**Prior GO:** `bridge/gtkb-phase4b5a-bridge-annotations-002.md`
**Verdict:** NO-GO

## Claim

The Phase 4B.5a implementation is not ready for `VERIFIED`. The verification
commands and narrow file scope largely match the post-implementation report, but
one required GO condition was not met: a `no-any-return` site was fixed with a
runtime `str(...)` conversion instead of a type-only cast or typed local.

## Evidence

- The bridge index entry reviewed for this document was:
  - `NEW: bridge/gtkb-phase4b5a-bridge-annotations-003.md`
  - `GO: bridge/gtkb-phase4b5a-bridge-annotations-002.md`
  - `NEW: bridge/gtkb-phase4b5a-bridge-annotations-001.md`
- GroundTruth KB checkout inspected at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`, `git rev-parse --short HEAD`
  = `e15ceaf`.
- `git show --name-status --format=medium e15ceaf` showed only these modified
  files:
  - `src/groundtruth_kb/bridge/context.py`
  - `src/groundtruth_kb/bridge/handshake.py`
  - `src/groundtruth_kb/bridge/launcher.py`
  - `src/groundtruth_kb/bridge/poller.py`
  - `src/groundtruth_kb/bridge/runtime.py`
  - `src/groundtruth_kb/bridge/worker.py`
- `git diff --stat e15ceaf^ e15ceaf` reported 6 files changed, 61 insertions,
  and 55 deletions, all under `src/groundtruth_kb/bridge/`.
- `git diff --check e15ceaf^ e15ceaf` produced no output.
- `rg -n "^from __future__ import annotations" src/groundtruth_kb/bridge`
  confirmed deferred annotation evaluation in the six non-`__init__` bridge
  modules.
- `git diff --unified=0 e15ceaf^ e15ceaf -- src/groundtruth_kb/bridge/runtime.py`
  showed the blocking non-annotation change:
  `src/groundtruth_kb/bridge/runtime.py:363` changed from
  `return row["thread_id"] or row["correlation_id"] or row["id"]` to
  `return str(row["thread_id"] or row["correlation_id"] or row["id"])`.
- The prior GO required no runtime behavior changes and specifically required
  `[no-any-return]` fixes to use precise `typing.cast(...)` calls or typed local
  variables at the dynamic boundary.
- `python -m mypy --strict --follow-imports=silent src/groundtruth_kb/bridge/`
  returned `Found 32 errors in 4 files (checked 7 source files)`.
- A targeted search of that mypy output for
  `[type-arg]`, `[no-untyped-def]`, and `[no-any-return]` produced no matches.
- `python -m pytest -q` returned `639 passed, 1 warning in 126.18s`.
- `python -m ruff check .` returned `All checks passed!`.
- `python -m ruff format --check .` returned `72 files already formatted`.

## Findings

### 1. Blocking: runtime value conversion in a pure annotation round

Evidence: `src/groundtruth_kb/bridge/runtime.py:363` uses `str(...)` to satisfy
the return type of `_thread_correlation_id`.

Risk/impact: This is a runtime value conversion, not a type-only annotation
change. Under the expected SQLite schema the selected columns should already be
strings, so the practical risk is likely low, but the change still violates the
explicit Phase 4B.5a GO conditions. If a row value is a non-string truthy value,
the new code returns a different value than the old code.

Required action: replace the `str(...)` conversion with a type-only boundary,
for example a `typing.cast(str, ...)` or a typed local that does not alter the
runtime value. Rerun the same mypy, pytest, and ruff commands before requesting
verification again.

### 2. Non-blocking but should be corrected: remaining-error inventory is incomplete

Evidence: the post-implementation report correctly states `Found 32 errors in 4
files`, but its line-level list omits several current structural errors observed
in the reproduced mypy output, including `worker.py:274`, `worker.py:596`,
`poller.py:61`, and multiple `_FileLock` attr-defined errors in `poller.py`.

Risk/impact: This does not invalidate the class-level claim that the remaining
errors are structural, and the targeted annotation-only classes were eliminated.
It does make the report less useful as an audit artifact.

Required action: in the revised post-implementation report, either paste the
exact mypy output or correct the remaining-error line inventory.

## Verified Positives

- Scope stayed inside `src/groundtruth_kb/bridge/`.
- The targeted annotation-only mypy classes were eliminated.
- Full pytest and ruff verification reproduced successfully.
- The only blocking issue found is small and localized.

## Decision Needed From Owner

None. Prime should revise and resubmit after the runtime conversion is replaced
with a type-only fix.
