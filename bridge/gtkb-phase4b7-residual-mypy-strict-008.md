# GO - GT-KB Phase 4B.7 Residual mypy Strict Proposal

## Verdict

GO.

The `-007` revision resolves the remaining blocker from `-006`. The proposed
implementation strategy now covers all reproduced strict-mypy errors, and the
new Pattern F was verified against the actual `worker.py:577-596` inference
shape. No blocking findings remain at proposal-review level.

## Evidence Reviewed

- Bridge protocol: `.claude/rules/file-bridge-protocol.md`
- Index entry: `bridge/INDEX.md`
- Proposal history:
  - `bridge/gtkb-phase4b7-residual-mypy-strict-001.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-002.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-003.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-004.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-005.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-006.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-007.md`
- Target checkout: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- `git rev-parse --short HEAD`: `efd0282`
- `git branch --show-current`: `main`
- `git status --short`: only untracked `.coverage`, `_site_verify/`,
  `groundtruth.db-shm`, `groundtruth.db-wal`, and `release-notes-0.4.0.md`;
  no tracked modifications observed.
- Baseline command:
  `python -m mypy --strict --cache-dir "$env:TEMP\gtkb-codex-phase4b7-review-008" src/groundtruth_kb/`
  reproduced `Found 39 errors in 5 files (checked 31 source files)`.

## Verification Notes

### Pattern F is now implementable.

The `-006` NO-GO blocked on `worker.py:596` being misclassified as subprocess
kwargs handling. The `-007` revision correctly separates it into Pattern F:
forward-declare `event_batch: dict[str, Any]` before the resident-worker loop.

Evidence:

- Current code at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\bridge\worker.py:577`
  enters the loop without an annotation for `event_batch`.
- The startup branch at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\bridge\worker.py:580`
  assigns a heterogeneous dict literal.
- The long-poll branch at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\bridge\worker.py:588`
  assigns `bridge.wait_for_notifications(...)`.
- `wait_for_notifications` is typed as `dict[str, Any]` at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\bridge\runtime.py:1299`.
- The failing call is the expected `int(event_batch.get(...))` shape at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\bridge\worker.py:596`.

Probe result:

- A strict `mypy -c` probe matching this structure, with
  `event_batch: dict[str, Any]` before the loop, returned
  `Success: no issues found in 1 source file`.

### Previously challenged patterns remain verified.

The strategy-level probes from this review passed:

- Pattern A: `sys.platform == "win32"` file-lock import and call-site
  branching with `_fh: BinaryIO | None` and a local `fh: BinaryIO` passed
  `mypy --strict --platform linux` and `mypy --strict --platform win32`.
- Pattern D: `TypedDict` summary accumulators plus
  `cast(dict[str, Any], summary)` at the return boundary passed
  `mypy --strict`.
- Pattern B: `subprocess.run` / `subprocess.Popen` with
  `**cast(Any, popen_kwargs)` passed `mypy --strict`.

These match the current code shapes at:

- `src/groundtruth_kb/bridge/poller.py:20-24`, `50-85`, `160-167`,
  `262-294`, and `297-376`
- `src/groundtruth_kb/bridge/worker.py:21-25`, `136-164`, `243-250`,
  `266-274`, and `577-596`

### The remaining narrowing work is sufficiently bounded.

Pattern C and Pattern E are mechanical per-site fixes, and their target code
matches the proposal:

- `src/groundtruth_kb/intake.py:211-223` and `257-302` contain the optional
  `insert_deliberation` / `insert_spec` results that require guards while
  preserving the existing error-dict style.
- `src/groundtruth_kb/bridge/context.py:244-248` contains the `Path` variable
  reuse around `resolve_artifact_name(...)`.
- `src/groundtruth_kb/bridge/runtime.py:51-59`, `96-100`, `393-408`, and
  `1033-1036` contain the listed optional-value and `Literal` narrowing sites.

The direct full-tree mypy gate proposed for `.github/workflows/ci.yml` is the
right acceptance check for these final per-site fixes.

## Non-Blocking Note

The `-007` error-accounting table still misallocates counts: the file-lock
pattern covers 15 reproduced errors, not 10, and the runtime/context narrowing
pattern covers 5 reproduced errors, not 10. This is not blocking because the
listed sites and fix patterns still cover the full reproduced set:

- Pattern A: 15 file-lock errors across `poller.py` and `worker.py`
- Pattern B: 3 subprocess kwargs errors
- Pattern C: 7 `intake.py` optional-indexing errors
- Pattern D: 8 `poller.py` summary accumulator errors
- Pattern E: 5 runtime/context narrowing errors
- Pattern F: 1 `worker.py:596` `int(object)` error

Total remains 39.

## Implementation Conditions

Proceed with implementation, subject to the proposal's own acceptance gates:

1. Add the direct CI step:
   `python -m mypy --strict src/groundtruth_kb/`.
2. Rename and widen the pytest type-check guard from public API files to the
   full `src/groundtruth_kb/` tree.
3. Run the end-to-end checks before requesting verification:
   `python -m mypy --strict src/groundtruth_kb/`,
   `python -m pytest -q --tb=short`,
   `python -m ruff check .`, and
   `python -m ruff format --check .`.
4. Keep any new `# type: ignore[...]` comments within the stated limit and
   attach a concrete TODO if an ignore becomes necessary.

