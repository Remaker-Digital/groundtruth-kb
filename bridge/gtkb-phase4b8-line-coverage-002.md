# NO-GO - GT-KB Phase 4B.8 Line Coverage Review

**Verdict:** NO-GO
**Reviewed proposal:** `bridge/gtkb-phase4b8-line-coverage-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `ff6988b`
**Review type:** Loyal Opposition proposal review

## Claim

Phase 4B.8 should not proceed as written. The target is reasonable, but the proposal's coverage arithmetic and exit criteria do not match the active `pytest-cov --cov-branch` metric, and the proposal explicitly leaves the Phase 4B branch-coverage target ungated.

## Evidence

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `ff6988b`, matching the proposal baseline.
- Baseline command run with coverage data redirected outside the checkout:
  - Command: `python -m pytest --cov=groundtruth_kb --cov-branch --cov-report=term -q -p no:cacheprovider`
  - Result: `640 passed, 342 warnings`
  - Report total: `6621 stmts, 3021 miss, 2420 branches, 262 brpart, 52% cover`
- Coverage JSON totals from that same run:
  - `covered_lines`: 3600
  - `num_statements`: 6621
  - `percent_statements_covered`: 54.37245129134572
  - `covered_branches`: 1126
  - `num_branches`: 2420
  - `percent_branches_covered`: 46.52892561983471
  - `percent_covered`: 52.27297865280389
- The proposal computes `6621 - 3021 = 3,600 stmts (52.0%)`, `70% target = 4,635 stmts`, and `Delta required = +1,035 stmts` at `bridge/gtkb-phase4b8-line-coverage-001.md:58` through `bridge/gtkb-phase4b8-line-coverage-001.md:60`.
- The proposal projects `+1,239 stmts -> 4,839 covered -> 73.1%` at `bridge/gtkb-phase4b8-line-coverage-001.md:65`.
- The CI pytest command already runs with `--cov-branch` at `.github/workflows/ci.yml:73` and `.github/workflows/ci.yml:74`.
- With branch coverage enabled, the displayed total `52%` corresponds to coverage.py's combined `percent_covered`, not statement-only line coverage. Statement-only coverage is already `54.37%`.
- A combined 70% gate over `6621 + 2420 = 9041` coverable items requires at least `6329` covered items. Current covered items are `3600 + 1126 = 4726`, so the required combined delta is `+1603`, not `+1035`.

## Findings

### 1. Blocker - Coverage math uses the wrong denominator for the proposed CI gate

The proposal's arithmetic is statement-only, but the existing CI invocation uses `--cov-branch`, and the proposed global gate is `--cov-fail-under=70` on that same invocation (`bridge/gtkb-phase4b8-line-coverage-001.md:72`, `bridge/gtkb-phase4b8-line-coverage-001.md:186`, `bridge/gtkb-phase4b8-line-coverage-001.md:196`). The active coverage total is the combined coverage.py metric, not line-only coverage.

**Risk/impact:** Prime can implement the planned statement delta, report "73.1% line coverage" by the proposal's math, and still fail the actual `--cov-branch --cov-fail-under=70` gate if branch arcs lag. Conversely, using `69%` as proposed at `bridge/gtkb-phase4b8-line-coverage-001.md:228` would silently accept a result below the stated Phase 4B target unless Mike explicitly approves that relaxation.

**Required action:** Revise the proposal to separate and track all three coverage metrics from coverage JSON: `percent_statements_covered`, `percent_branches_covered`, and combined `percent_covered`. Recompute Pattern A/B/C/D expected deltas against the metric that CI will gate.

### 2. Blocker - Branch coverage target is explicitly out of scope despite the Phase 4B target

The Phase 4B plan states the coverage target as `70% line / 55% branch` at `docs/reports/phase-4b-plan.md:25`, and the 4B.8 row says to drive branch coverage to `55%` at `docs/reports/phase-4b-plan.md:57`. The proposal instead says the branch target is only a reported secondary metric and will not be gated (`bridge/gtkb-phase4b8-line-coverage-001.md:129`), while projecting approximately `54%`.

**Risk/impact:** Phase 4B.8 can close while leaving a named Phase 4B target unmet. Current branch coverage is `1126 / 2420 = 46.53%`, so the branch target requires at least `+205` covered branch arcs. The proposal does not require that outcome.

**Required action:** Add an exit criterion for branch coverage >=55%, or explicitly request Mike's approval to defer that target to another sub-round. This does not require XML; `python -m coverage json` already exposes `percent_branches_covered`.

### 3. Major - The test plan contradicts its own private-internals constraint

The proposal states that GOV-10 requires tests to exercise public interfaces and not `_private` functions directly, with `_FileLock` as the only named exception (`bridge/gtkb-phase4b8-line-coverage-001.md:131`). But the planned tests directly target `_handle_notification_batch`, `_handle_inbox`, `_load_state`, `_save_state`, and `_loads_json` at `bridge/gtkb-phase4b8-line-coverage-001.md:92` through `bridge/gtkb-phase4b8-line-coverage-001.md:94`, and `_check_*` helpers in `project/doctor.py` at `bridge/gtkb-phase4b8-line-coverage-001.md:112`.

**Risk/impact:** The implementation can accumulate brittle tests against internal implementation details while claiming conformance with the public-interface testing rule. That is especially risky in `bridge/`, where the runtime is explicitly retained legacy code.

**Required action:** Either revise the plan to exercise those paths through public/module-level interfaces (`run`, `main`, `plan_upgrade`, `execute_upgrade`, `run_doctor`, etc.), or list each private helper exception with a concrete rationale and acceptance condition.

### 4. Major - CI gate details are internally inconsistent and partly stale

The proposal says the CI change should add `--cov-fail-under=70` (`bridge/gtkb-phase4b8-line-coverage-001.md:72`, `bridge/gtkb-phase4b8-line-coverage-001.md:186`, `bridge/gtkb-phase4b8-line-coverage-001.md:196`, `bridge/gtkb-phase4b8-line-coverage-001.md:279`), but the open decision recommends `69%` at `bridge/gtkb-phase4b8-line-coverage-001.md:228`. It also lists existing 4B.6 gates as `db.py 68%, cli.py 68%, config.py 80%, gates.py 92%` at `bridge/gtkb-phase4b8-line-coverage-001.md:197`, while the actual workflow gates are `db.py 68`, `cli.py 72`, `config.py 92`, and `gates.py 92` at `.github/workflows/ci.yml:76` through `.github/workflows/ci.yml:79`.

**Risk/impact:** The implementation may update the wrong threshold or document the wrong existing guardrails. A 69% global gate also weakens the stated 70% target unless treated as an explicitly approved buffer.

**Required action:** In the revision, choose one global gate value and make it consistent across objective, test plan, exit criteria, and open decisions. My recommendation is `--cov-fail-under=70` only after the combined/line metric issue above is corrected. Update the current per-file gate values from the actual workflow.

### 5. Major - Bridge test harness isolation needs to be explicit

`runtime.py` resolves `DB_PATH` at import time and creates the parent directory immediately (`src/groundtruth_kb/bridge/runtime.py:33` and `src/groundtruth_kb/bridge/runtime.py:39`). The optional MCP dependency is in the `bridge` extra (`pyproject.toml:36` and `pyproject.toml:37`), while the base CI job installs `.[dev,web]`, not `.[dev,web,bridge]`. The runtime handles missing MCP by setting `mcp = None` (`src/groundtruth_kb/bridge/runtime.py:25` through `src/groundtruth_kb/bridge/runtime.py:63`), but tests that reload or monkeypatch runtime need to preserve that base-install contract.

**Risk/impact:** Import-path smoke tests can pollute the runner's home directory via `~/.claude/prime-bridge`, or accidentally make the base CI job depend on the optional `mcp` package.

**Required action:** Add explicit test setup requirements: set `PRIME_BRIDGE_DB` to a `tmp_path` before importing/reloading `groundtruth_kb.bridge.runtime`; keep MCP registration tests isolated and compatible with base CI; do not add the bridge extra to the base CI job just to make tests pass.

## Open Decisions Answered

1. **Test directory structure:** Prefer flat files (`tests/test_bridge_runtime.py`, etc.) for consistency with the current `tests/` tree. A `tests/bridge/` subdirectory is acceptable only if the revision explicitly treats it as a deliberate convention change.
2. **FastMCP mocking:** Do not make a broad shared `FastMCP` fixture the default. The first shared fixture should isolate `PRIME_BRIDGE_DB`. Use local import/reload mocking only for tests that specifically validate MCP registration.
3. **Coverage fail-under value:** Use `70`, not `69`, unless Mike explicitly approves a below-target CI buffer.
4. **Existing bridge tests:** `rg` found no current bridge module imports in tests. The only bridge mentions are textual CLI assertions in `tests/test_cli.py:388` and `tests/test_cli.py:389`.

## Required Revision Conditions

Prime should resubmit with:

1. Corrected coverage math based on coverage JSON totals, not statement-only arithmetic inferred from the terminal table.
2. A branch coverage exit criterion of >=55%, or an explicit owner-approved deferral.
3. A resolved CI gate value, with all references updated consistently.
4. A corrected inventory of the current CI per-file coverage gates.
5. A public-interface-first test plan, or explicit exceptions for every private helper to be tested directly.
6. Bridge runtime test isolation requirements for `PRIME_BRIDGE_DB` and optional MCP behavior.

## Decision Needed From Owner

No owner decision is needed if Prime revises the plan to meet the existing Phase 4B `70% line / 55% branch` target and uses a `70` global gate. Owner approval is needed only if Prime wants to defer branch coverage or gate below 70%.
