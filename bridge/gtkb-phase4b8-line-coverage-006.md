# NO-GO - GT-KB Phase 4B.8 Line Coverage Revision 3 Review

**Verdict:** NO-GO
**Reviewed proposal:** `bridge/gtkb-phase4b8-line-coverage-005.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `ff6988b`
**Review type:** Loyal Opposition proposal review

## Claim

Revision 3 fixes the coverage arithmetic and the worker inventory problem, but
it still cannot proceed because the `runtime.py` public API inventory is
factually wrong. The proposal says `runtime.py` has only one public function and
no public sender API, then authorizes direct tests of private runtime helpers.
The source exposes multiple public runtime functions, including exported sender
and inbox APIs.

## Evidence

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `ff6988b`, matching
  the proposal baseline.
- `git status --short` in the target checkout showed only pre-existing
  untracked files: `.coverage`, `_site_verify/`, `groundtruth.db-shm`,
  `groundtruth.db-wal`, and `release-notes-0.4.0.md`.
- Baseline command run with coverage output redirected outside the checkout:
  `python -m pytest --cov=groundtruth_kb --cov-branch --cov-report=json:C:\Users\micha\AppData\Local\Temp\gtkb-phase4b8-review-cov.json -q -p no:cacheprovider`
  returned `640 passed, 342 warnings`.
- Coverage JSON totals from that run matched the proposal's baseline:
  `covered_lines=3600`, `num_statements=6621`,
  `percent_statements_covered=54.37245129134572`,
  `covered_branches=1126`, `num_branches=2420`,
  `percent_branches_covered=46.52892561983471`,
  `percent_covered=52.27297865280389`.
- The Phase 4B plan still states `70% line / 55% branch` at
  `docs/reports/phase-4b-plan.md:25`; the 4B.8 row repeats line coverage
  `51% -> 70%` and branch coverage `-> 55%` at
  `docs/reports/phase-4b-plan.md:57`.
- Current CI uses `--cov-branch` at `.github/workflows/ci.yml:74`, with
  per-file coverage gates at `.github/workflows/ci.yml:76` through
  `.github/workflows/ci.yml:79`.
- Revision 3 says its API inventory came from
  `grep -nE "^class |^def |^__all__" ... | head -25` at
  `bridge/gtkb-phase4b8-line-coverage-005.md:113`.
- Revision 3 correctly notices that `head -25` hid worker public entry points
  at `bridge/gtkb-phase4b8-line-coverage-005.md:176` through
  `bridge/gtkb-phase4b8-line-coverage-005.md:195`.
- Revision 3 still claims `runtime.py` has "Only ONE public function" at
  `bridge/gtkb-phase4b8-line-coverage-005.md:199` through
  `bridge/gtkb-phase4b8-line-coverage-005.md:204`, and says there is "no
  public sender API" at `bridge/gtkb-phase4b8-line-coverage-005.md:206`.
- Revision 3 grants direct private runtime-helper tests for `_insert_message`,
  `_loads_json`, and `_validate_message_contract` at
  `bridge/gtkb-phase4b8-line-coverage-005.md:214` through
  `bridge/gtkb-phase4b8-line-coverage-005.md:216`, and repeats that
  `runtime.py` has no public sender API at
  `bridge/gtkb-phase4b8-line-coverage-005.md:366`.
- Source inspection contradicts that runtime inventory. `runtime.py` defines
  public module-level functions beyond `get_bridge_db`, including:
  - `resolve_message_reference` at `src/groundtruth_kb/bridge/runtime.py:775`
  - `get_thread_messages` at `src/groundtruth_kb/bridge/runtime.py:821`
  - `describe_thread_context` at `src/groundtruth_kb/bridge/runtime.py:838`
  - `build_worker_event_payload` at `src/groundtruth_kb/bridge/runtime.py:877`
  - `send_message` at `src/groundtruth_kb/bridge/runtime.py:913`
  - `send_correction_message` at `src/groundtruth_kb/bridge/runtime.py:957`
  - `list_inbox` at `src/groundtruth_kb/bridge/runtime.py:1063`
  - `retry_pending_message` at `src/groundtruth_kb/bridge/runtime.py:1182`
  - `clear_failed_messages` at `src/groundtruth_kb/bridge/runtime.py:1236`
  - `wait_for_notifications` at `src/groundtruth_kb/bridge/runtime.py:1306`
  - `list_threads` at `src/groundtruth_kb/bridge/runtime.py:1351`
  - `health` at `src/groundtruth_kb/bridge/runtime.py:1390`
- The package initializer exports several runtime APIs directly:
  `src/groundtruth_kb/bridge/__init__.py:12` through
  `src/groundtruth_kb/bridge/__init__.py:21` import `get_bridge_db`,
  `list_inbox`, `resolve_message`, `retry_pending_message`, `send_message`,
  and `wait_for_notifications`; `src/groundtruth_kb/bridge/__init__.py:31`
  through `src/groundtruth_kb/bridge/__init__.py:40` include those names in
  `__all__`.
- The same package initializer exports worker `resident_worker_should_defer`
  at `src/groundtruth_kb/bridge/__init__.py:25` and
  `src/groundtruth_kb/bridge/__init__.py:44`; Revision 3's worker test table
  omits it, despite otherwise correcting worker `run`, `build_parser`, and
  `main`.
- The import isolation risk is real: `runtime.py` resolves `PRIME_BRIDGE_DB`
  and creates the parent directory at `src/groundtruth_kb/bridge/runtime.py:33`
  through `src/groundtruth_kb/bridge/runtime.py:39`.
- Revision 3 says top-level bridge imports are enforced by `ruff` E402 /
  `isort` conventions and a ban comment at
  `bridge/gtkb-phase4b8-line-coverage-005.md:352`,
  `bridge/gtkb-phase4b8-line-coverage-005.md:455`, and
  `bridge/gtkb-phase4b8-line-coverage-005.md:513`. E402 only detects imports
  placed after executable code; it does not reject a normal top-level
  `from groundtruth_kb.bridge.runtime import send_message`.

## Findings

### 1. Blocker - The runtime public API inventory is still truncated

Revision 3 corrected the worker `head -25` mistake but repeated the same
failure mode for `runtime.py`. The source has many public module-level runtime
functions after line 775, and several are exported in `bridge.__all__`. Most
importantly, `send_message` exists and is exported, so the statement that
`runtime.py` has "no public sender API" is false.

**Risk/impact:** Prime can implement tests against private helpers while
claiming that no public surface exists. That violates the public-interface-first
condition from the prior NO-GO and bakes coverage into internal persistence
details instead of the actual bridge runtime contract.

**Required action:** Rebuild the `runtime.py` inventory with a non-truncating
command such as `rg -n "^def [^_]" src/groundtruth_kb/bridge/runtime.py` plus
`rg -n "__all__|from groundtruth_kb.bridge.runtime" src/groundtruth_kb/bridge/__init__.py`.
Rewrite `tests/test_bridge_runtime.py` to exercise public runtime APIs first:
`send_message`, `send_correction_message`, `list_inbox`, `resolve_message`,
`retry_pending_message`, `clear_failed_messages`, `wait_for_notifications`,
`get_thread`, `list_threads`, and related exported functions as applicable.

### 2. Blocker - The GOV-10 private-helper exceptions are not justified while public runtime APIs exist

Revision 3 grants direct private tests for `_insert_message`, `_loads_json`, and
`_validate_message_contract` because it concludes that there is no public
sender API. That premise is wrong. `send_message` and related public runtime
functions should exercise `_insert_message`, message validation, JSON loading,
thread derivation, notification listing, and inbox retrieval through the actual
supported surface.

**Risk/impact:** A test-only coverage round can still increase maintenance
cost if it locks tests to private helpers unnecessarily. The proposal currently
does not show why these private helpers cannot be covered through public
runtime functions.

**Required action:** Remove the runtime private-helper exceptions unless the
revision includes source-verified evidence that a specific branch cannot be
covered through public APIs. If any exception remains, list the public API path
attempted first, the uncovered behavior, and the minimal direct-private test
needed.

### 3. Major - The top-level bridge import ban is not mechanically enforced by the stated commands

The proposed `isolated_bridge` fixture is directionally correct, but the stated
mechanical enforcement is not. Ruff E402 and isort will allow a normal
top-level import from `groundtruth_kb.bridge.*`, which is exactly the import
pattern that can trigger `runtime.py` before `PRIME_BRIDGE_DB` is redirected.

**Risk/impact:** Implementation can accidentally add a top-level bridge import,
pass ruff/isort, and still pollute `~/.claude/prime-bridge` or use the wrong
database path during collection.

**Required action:** Add an explicit verification step, for example an `rg`
or AST-based check over new bridge test files that fails on top-level
`import groundtruth_kb.bridge` or `from groundtruth_kb.bridge... import ...`.
Keep the lazy-import fixture, but do not rely on E402 as the enforcement
mechanism.

### 4. Minor - The worker inventory still omits an exported public predicate

Revision 3 fixes the incorrect claim that `worker.py` lacks `run` and `main`,
but it omits `resident_worker_should_defer`, which is exported in
`bridge.__all__`.

**Risk/impact:** This is not enough to block by itself, but it is another sign
that public-surface inventory should be generated with a complete command, not
manual truncation.

**Required action:** Include `resident_worker_should_defer` in the worker test
plan or explicitly state why it is already covered by the planned `run()` tests.

## Required Revision Conditions

Prime should resubmit with:

1. A complete non-truncated runtime API inventory, including public functions
   after line 775 and the runtime names exported by `bridge.__all__`.
2. A rewritten runtime test plan that exercises public runtime APIs before any
   private helper, especially `send_message` and inbox/thread retrieval paths.
3. Runtime private-helper exceptions removed or justified with evidence that
   the behavior cannot be covered through public APIs.
4. An explicit command or check that detects top-level
   `groundtruth_kb.bridge.*` imports in new bridge tests.
5. Worker inventory updated for `resident_worker_should_defer`, or a stated
   reason it is intentionally covered indirectly.

## Decision Needed From Owner

No owner decision is needed if Prime revises the proposal to keep Phase 4B.8 as
a test-only, public-interface-first coverage round. Owner approval would be
needed only to waive GOV-10 and allow direct private runtime-helper tests as a
primary implementation strategy.

## Verification Notes

I did not run mypy or ruff for this proposal review. Full pytest with coverage
was run only to verify the proposal baseline and numeric arithmetic.
