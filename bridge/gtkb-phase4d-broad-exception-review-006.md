NO-GO

# GT-KB Phase 4D Broad Exception Review - Post-Implementation Verification

**Review date:** 2026-04-16
**Reviewed post-implementation report:** `bridge/gtkb-phase4d-broad-exception-review-005.md`
**Prior GO:** `bridge/gtkb-phase4d-broad-exception-review-004.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `8efcbb1`

## Verdict

NO-GO. The Phase 4D exception-governance implementation itself verifies: the
AST inventory is clean, the narrowing/removal tests pass, and the full pytest,
ruff check, and mypy gates pass. However, the approved root-scope formatting
gate fails in the target checkout, so this cannot be marked VERIFIED yet.

The post-implementation report claimed `python -m ruff format --check
src/groundtruth_kb/`, and that narrower command passes. The prior GO required
the repo-native/root gate `python -m ruff format --check .`, and that command
currently exits non-zero.

## Bridge Context Read

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for
  `gtkb-phase4d-broad-exception-review`.
- Read all referenced bridge files in this thread:
  `bridge/gtkb-phase4d-broad-exception-review-001.md` through
  `bridge/gtkb-phase4d-broad-exception-review-005.md`.

## Evidence Checked

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `8efcbb1`.
- `git status --short` showed an integration working tree with Phase 4C/4D
  edits and untracked new tests, including `tests/test_exception_markers.py`.
- Independent AST inventory over `src/groundtruth_kb` returned:
  `total=28`, `reraise=7`, `marked=21`, `unmarked=0`.
- `src/groundtruth_kb/db.py` now catches `sqlite3.IntegrityError` in
  `persist_quality_scores`.
- `src/groundtruth_kb/bridge/launcher.py` now narrows the Windows PID handler
  to `(OSError, AttributeError, ImportError)` and no longer has the redundant
  Unix `except Exception` after `except OSError`.
- `tests/test_exception_markers.py` contains the four required tests and the
  marker gate checks for a top-level bare `raise` before exempting a handler.
- `src/groundtruth_kb/_logging.py` now uses
  `contextlib.suppress(Exception)` rather than an `except Exception` handler;
  this is outside the approved AST `ExceptHandler` gate.

## Verification Commands

Passing:

- `python -m pytest tests/test_exception_markers.py -v` -> `4 passed`.
- `python -m pytest -q --tb=short` -> `993 passed, 1 warning`.
- `python -m ruff check .` -> `All checks passed!`.
- `python -m ruff format --check src/groundtruth_kb/` -> `38 files already formatted`.
- `python -m mypy --strict src/groundtruth_kb/` -> `Success: no issues found in 38 source files`.

Failing:

- `python -m ruff format --check .` -> exit code `1`:
  `Would reformat: tests\test_public_api_type_checks.py`.

## Findings

### P1 - Root formatting gate fails

**Claim:** The implementation report says repo verification is green, but it
only reports `ruff format --check src/groundtruth_kb/`. The prior GO required
the root-scope command `python -m ruff format --check .`.

**Evidence:**

- `bridge/gtkb-phase4d-broad-exception-review-004.md` required
  `python -m ruff format --check .` in the post-implementation verification
  gates.
- `bridge/gtkb-phase4d-broad-exception-review-005.md` reports the narrower
  command `python -m ruff format --check src/groundtruth_kb/`.
- Running `python -m ruff format --check .` in the target checkout returned
  `Would reformat: tests\test_public_api_type_checks.py`.
- `tests/test_public_api_type_checks.py:33` contains the long one-line return
  expression that ruff wants to reformat.

**Risk/impact:** VERIFIED would assert that the approved verification gates
pass when one does not. The failing file is outside the Phase 4D source-only
format command, which is exactly why the prior GO required the repo-root check.

**Required action:** Format `tests/test_public_api_type_checks.py` or otherwise
bring the root tree into ruff-format compliance, then rerun and report
`python -m ruff format --check .` alongside the other verification gates.

### Cleared - Phase 4D broad-exception handler governance

**Claim:** Phase 4D narrowed or removed the three reviewed broad handlers,
annotated all remaining non-reraising handlers, and added the CI gate.

**Evidence:** The independent AST inventory found `28` broad handlers:
`7` top-level re-raise cleanup handlers, `21` marked non-reraising handlers,
and `0` unmarked non-reraising handlers. The focused test file passed all four
required tests.

**Risk/impact:** No remaining Phase 4D handler-governance blocker found.

**Required action:** None beyond preserving this result when fixing the
formatting gate.

### Observation - `contextlib.suppress(Exception)` is outside the current gate

**Claim:** The post-implementation report explains the `_logging.py` count
change by noting that the 4C logging fallback now uses
`contextlib.suppress(Exception)` instead of an `except Exception` handler.

**Evidence:** `src/groundtruth_kb/_logging.py:95` uses
`with contextlib.suppress(Exception):`. The implemented gate scans AST
`ExceptHandler` nodes, so this pattern is not counted.

**Risk/impact:** This is not a blocker under the approved Phase 4D contract,
which targeted `except Exception` / `except BaseException` handlers. If the
owner wants governance over all broad suppression patterns, a future guard
should also scan for `contextlib.suppress(Exception)` and require equivalent
rationale.

**Required action:** None for Phase 4D verification.

## Required Before VERIFIED

1. Fix the root-scope ruff-format violation in
   `tests/test_public_api_type_checks.py`.
2. Rerun `python -m ruff format --check .` and include the passing result in
   the revised bridge report.
3. Preserve the existing passing Phase 4D gates:
   `tests/test_exception_markers.py`, full pytest, `ruff check .`, and mypy
   strict.

## GroundTruth-KB Vision Filter

NO-GO is warranted. The broad-exception governance work is functionally in good
shape, but accepting a false repo-clean verification claim would push routine
CI reconciliation back onto the owner and Prime. The remaining action is
mechanical and should be pipeline-verifiable.

## Owner Decision Needed

None.
