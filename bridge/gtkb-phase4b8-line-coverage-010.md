# GO - GT-KB Phase 4B.8 Line Coverage Revision 5 Review

**Verdict:** GO
**Reviewed proposal:** `bridge/gtkb-phase4b8-line-coverage-009.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `ff6988b`
**Review type:** Loyal Opposition proposal review

## Claim

Revision 5 resolves the blockers from `-008`. The source inventories now match
the verified `groundtruth-kb` bridge API surface, the late `context.py` flows
are explicitly planned, the coverage targets cover all three relevant metrics,
and the import-isolation plan is good enough to proceed with implementation.

This GO has two implementation conditions. They do not require another proposal
revision, but they must be satisfied before Phase 4B.8 is reported complete.

## Evidence

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `ff6988b`.
- `git status --short` showed only pre-existing untracked files:
  `.coverage`, `_site_verify/`, `groundtruth.db-shm`, `groundtruth.db-wal`,
  and `release-notes-0.4.0.md`. This review did not modify the target checkout.
- `python -m coverage json -o $env:TEMP\gtkb-phase4b8-009-review-cov.json`
  over the existing coverage data returned:
  - `covered_lines=3600`
  - `num_statements=6621`
  - `percent_statements_covered=54.37245129134572`
  - `covered_branches=1126`
  - `num_branches=2420`
  - `percent_branches_covered=46.52892561983471`
  - `percent_covered=52.27297865280389`
- `rg -n "^def [A-Za-z]|^class [A-Za-z_]|^__all__"` over the six bridge files
  matched the proposal's revised inventories:
  - `context.py` includes 18 public functions, including
    `fast_path_session_start_requests` at
    `src/groundtruth_kb/bridge/context.py:635` and
    `repair_terminal_thread_outputs` at
    `src/groundtruth_kb/bridge/context.py:774`.
  - `runtime.py` includes the 19 public functions listed in `-009`, including
    `send_message` at `src/groundtruth_kb/bridge/runtime.py:913`,
    `list_inbox` at `src/groundtruth_kb/bridge/runtime.py:1063`, and
    `health` at `src/groundtruth_kb/bridge/runtime.py:1390`.
  - `worker.py` includes `resident_worker_should_defer` at
    `src/groundtruth_kb/bridge/worker.py:376`, `run` at
    `src/groundtruth_kb/bridge/worker.py:565`, `build_parser` at
    `src/groundtruth_kb/bridge/worker.py:803`, and `main` at
    `src/groundtruth_kb/bridge/worker.py:819`.
- Python line counting returned `context.py=980`, `worker.py=826`, and
  `runtime.py=1462`, matching the proposal's non-truncation evidence.
- `bridge/__init__.py` exports 13 names, matching the corrected proposal:
  2 type aliases plus 11 functions at `src/groundtruth_kb/bridge/__init__.py:31`.
- The CI workflow still runs pytest with `--cov-branch` and no global
  `--cov-fail-under` at `.github/workflows/ci.yml:72` through
  `.github/workflows/ci.yml:75`; current per-file gates remain `db.py 68`,
  `cli.py 72`, `config.py 92`, and `gates.py 92` at
  `.github/workflows/ci.yml:76` through `.github/workflows/ci.yml:79`.
- The Phase 4B plan states the target as `70% line / 55% branch` at
  `docs/reports/phase-4b-plan.md:25`, and the 4B.8 row repeats line coverage
  to `70%` and branch coverage to `55%` at
  `docs/reports/phase-4b-plan.md:57`.

## Resolved Prior Findings

1. `context.py` inventory is now complete. The two late-file public functions
   identified in `-008` are listed and assigned explicit direct tests.
2. The test plan explains why those two context functions should be unit-tested
   with a mock bridge instead of relying only on `worker.run()` integration
   scenarios.
3. The import-hygiene sketch now rejects the three ordinary top-level import
   forms, including `from groundtruth_kb import bridge`.
4. The `__all__` and test-count summaries are now internally consistent:
   13 exported names, Pattern A about 131 tests, total new tests about 163,
   and total suite estimate about 803 tests.

## Implementation Conditions

### 1. Tighten the importlib branch of the import-hygiene test

The proposed AST check is directionally correct, but the sketch only detects
`importlib.import_module("groundtruth_kb.bridge...")` when the call is a
top-level expression. It does not detect the same top-level import when assigned
to a name, for example:

```python
runtime = importlib.import_module("groundtruth_kb.bridge.runtime")
```

I reproduced that by applying the proposal's sketch to five snippets:

```text
import_stmt: True
from_bridge: True
from_pkg: True
expr_importlib: True
assigned_importlib: False
```

The blind spot exists because `_importlib_bridge_call` returns `False` unless
the top-level node is `ast.Expr` at
`bridge/gtkb-phase4b8-line-coverage-009.md:332` through
`bridge/gtkb-phase4b8-line-coverage-009.md:337`.

**Required implementation action:** make the hygiene test inspect top-level
`ast.Assign`, `ast.AnnAssign`, and similar statement wrappers for literal
`importlib.import_module("groundtruth_kb.bridge...")` calls, or more simply walk
each top-level statement subtree while still limiting enforcement to module
scope. Include negative-case coverage for both expression and assignment forms.

### 2. Configure context mocks with a context provider, not only send/resolve

`fast_path_session_start_requests` and `repair_terminal_thread_outputs` both
call `build_contexts(...)` before reaching `bridge.resolve_message(...)` or
`bridge.send_message(...)`:

- `fast_path_session_start_requests` calls `build_contexts` at
  `src/groundtruth_kb/bridge/context.py:644`.
- `repair_terminal_thread_outputs` calls `build_contexts` at
  `src/groundtruth_kb/bridge/context.py:783`.
- `build_contexts` resolves each explicit reference via
  `get_worker_event_payload` when present, or `describe_thread_context` as the
  fallback at `src/groundtruth_kb/bridge/context.py:436` through
  `src/groundtruth_kb/bridge/context.py:443`.

**Required implementation action:** the direct tests for these two functions
must configure the mock bridge with `get_worker_event_payload(...)` or
`describe_thread_context(...)` returning the intended context shape. A mock
that only stubs `resolve_message` and `send_message` will exercise only the
empty/no-context path.

## Approval Conditions

Prime may proceed with implementation if the post-implementation report shows:

1. `percent_covered >= 70.0%`
2. `percent_statements_covered >= 70.0%`
3. `percent_branches_covered >= 55.0%`
4. `pytest`, `mypy --strict`, `ruff check`, and `ruff format --check` pass
5. `.github/workflows/ci.yml` adds `--cov-fail-under=70`
6. No source behavior changes and no existing tests deleted or skipped
7. `tests/test_bridge_import_hygiene.py` passes and covers the importlib
   assignment case above
8. `fast_path_session_start_requests` and `repair_terminal_thread_outputs`
   have direct tests with a configured context provider

## Decision Needed From Owner

None. This remains a test-only coverage round with the existing Phase 4B
targets intact.

## Verification Notes

Full pytest, mypy, and ruff were not run for this proposal review. I verified
the proposal against source inventories, CI config, phase-plan targets, and the
existing coverage data. Full command verification belongs in the
post-implementation bridge report.
