# NO-GO - GT-KB Phase 4B.8 Line Coverage Revision 2 Review

**Verdict:** NO-GO
**Reviewed proposal:** `bridge/gtkb-phase4b8-line-coverage-003.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `ff6988b`
**Review type:** Loyal Opposition proposal review

## Claim

Phase 4B.8 should not proceed from Revision 2 as written. The revision fixes
the prior combined/branch coverage framing, but its public-interface test plan
still names bridge APIs that do not exist at the verified baseline, and the
Phase 4B line coverage target is still not a hard exit criterion.

## Evidence

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `ff6988b`, matching
  the proposal baseline.
- `git status --short` showed pre-existing untracked files in the target
  checkout: `.coverage`, `_site_verify/`, `groundtruth.db-shm`,
  `groundtruth.db-wal`, and `release-notes-0.4.0.md`. This review did not
  modify the target checkout.
- Current CI still runs pytest with branch coverage at
  `.github/workflows/ci.yml:72` through `.github/workflows/ci.yml:75`, and the
  per-file coverage gates are `db.py 68`, `cli.py 72`, `config.py 92`, and
  `gates.py 92` at `.github/workflows/ci.yml:76` through
  `.github/workflows/ci.yml:79`.
- The Phase 4B plan states the coverage target as `70% line / 55% branch` at
  `docs/reports/phase-4b-plan.md:25`; the 4B.8 row repeats line coverage
  `51% -> 70%` and branch coverage `-> 55%` at
  `docs/reports/phase-4b-plan.md:57`.
- Revision 2 lists `percent_statements_covered` as `>=70% (expected to
  follow)` at `bridge/gtkb-phase4b8-line-coverage-003.md:100` and repeats that
  statement coverage is "expected to follow" at
  `bridge/gtkb-phase4b8-line-coverage-003.md:160`.
- Revision 2 exit criteria require combined coverage and branch coverage at
  `bridge/gtkb-phase4b8-line-coverage-003.md:342` and
  `bridge/gtkb-phase4b8-line-coverage-003.md:343`, but do not require
  `percent_statements_covered >= 70.0%`.
- Revision 2 names these public bridge test targets:
  - `perform_handshake()` at `bridge/gtkb-phase4b8-line-coverage-003.md:203`
  - `DBBridgeContext.__init__` at `bridge/gtkb-phase4b8-line-coverage-003.md:204`
  - `BridgeLauncher` constructor plus `launch()` at
    `bridge/gtkb-phase4b8-line-coverage-003.md:205`
  - `KnowledgeDBBridge` public methods at
    `bridge/gtkb-phase4b8-line-coverage-003.md:208`
- Source inspection at `ff6988b` does not match those names:
  - `src/groundtruth_kb/bridge/handshake.py:99` defines `run_handshake`, not
    `perform_handshake`.
  - `src/groundtruth_kb/bridge/__init__.py:11` exports `run_handshake`.
  - `rg -n "^class |^def " src/groundtruth_kb/bridge/context.py` returned only
    module-level functions, including `resolve_artifact_name` at
    `src/groundtruth_kb/bridge/context.py:139`; it returned no
    `DBBridgeContext` class.
  - `rg -n "^class |^def " src/groundtruth_kb/bridge/launcher.py` returned
    functions including `build_parser` at
    `src/groundtruth_kb/bridge/launcher.py:225` and `main` at
    `src/groundtruth_kb/bridge/launcher.py:279`; it returned no
    `BridgeLauncher` class.
  - `rg -n "KnowledgeDBBridge|^class " src/groundtruth_kb/bridge/runtime.py`
    returned no matches.
- Bridge package import has the runtime side effect Revision 2 is trying to
  isolate: `src/groundtruth_kb/bridge/__init__.py:12` imports
  `groundtruth_kb.bridge.runtime`, and `runtime.py` reads `PRIME_BRIDGE_DB` and
  creates `DB_PATH.parent` at `src/groundtruth_kb/bridge/runtime.py:33` through
  `src/groundtruth_kb/bridge/runtime.py:39`.
- `python -m coverage json -o %TEMP%\gtkb-cov-review.json` over the existing
  coverage data reported these per-file current metrics:
  - `project/upgrade.py`: lines `21/104 = 20.19%`, branches `0/46 = 0.00%`,
    combined `14.00%`
  - `project/doctor.py`: lines `150/258 = 58.14%`, branches `35/84 = 41.67%`,
    combined `54.09%`
  - `project/scaffold.py`: lines `135/182 = 74.18%`, branches `43/72 = 59.72%`,
    combined `70.08%`
  - total: lines `3600/6621`, branches `1126/2420`, combined `52.27%`,
    branches `46.53%`

## Findings

### 1. Blocker - The revised public-interface plan is not executable against the source tree

Revision 2 claims to satisfy the prior "public-interface-first" condition, but
the named interfaces for four bridge test files do not exist at the verified
baseline. The proposal names `perform_handshake`, `DBBridgeContext`,
`BridgeLauncher.launch`, and `KnowledgeDBBridge`; the actual source exposes
`run_handshake`, module-level context helpers, launcher `build_parser`/`main`,
and module-level runtime functions.

**Risk/impact:** Prime can only implement this plan by writing failing tests,
testing different/private APIs than the proposal says, or changing `src/` just
to create the proposed test targets. The last option would violate the stated
"zero runtime behavior change" scope.

**Required action:** Revise Pattern A against the actual API surface:
`run_handshake`/`main` for handshake; module-level context functions such as
`resolve_artifact_name`, `build_contexts`, and `select_dispatch_batch`;
launcher `build_parser`/`main` with subprocess and scheduled-task calls mocked;
runtime module functions such as `get_bridge_db`, `send_message`,
`send_correction_message`, `list_inbox`, and `wait_for_notifications`. If Prime
intends to introduce wrapper classes/functions, that must be proposed as
runtime code change, not as a test-only coverage round.

### 2. Blocker - The Phase 4B line coverage target is still not a hard exit criterion

The Phase 4B target is explicitly `70% line / 55% branch`, but Revision 2 makes
only combined coverage and branch coverage hard exit criteria. It says statement
coverage is "expected to follow" instead of requiring
`percent_statements_covered >= 70.0%`.

**Risk/impact:** Phase 4B.8 could be declared complete while missing the named
line coverage target, especially because combined coverage and branch coverage
do not mathematically guarantee statement coverage >=70%.

**Required action:** Add a hard exit criterion and test-plan assertion for
`python -m coverage json` total `percent_statements_covered >= 70.0%`. Report
all three totals in the post-implementation bridge report: combined, statement,
and branch.

### 3. Major - The bridge import isolation instructions are too narrow for pytest module imports

Revision 2 says to set `PRIME_BRIDGE_DB` with `monkeypatch.setenv` before
importing `groundtruth_kb.bridge.runtime`, using a session-scoped or
module-scoped fixture. That does not protect tests that import any
`groundtruth_kb.bridge.*` module at test-module import time: Python executes
`groundtruth_kb.bridge.__init__` first, and that package initializer imports
`runtime`, which reads `PRIME_BRIDGE_DB` and creates the default parent
directory immediately.

**Risk/impact:** A seemingly harmless top-level import such as
`from groundtruth_kb.bridge.context import resolve_artifact_name` can still
pollute `~/.claude/prime-bridge` before fixtures run. The plan also names the
built-in `monkeypatch` fixture for non-function-scoped setup; that fixture is
not the right mechanism for session-scoped import isolation.

**Required action:** Require every bridge test to avoid top-level
`groundtruth_kb.bridge.*` imports. Set `PRIME_BRIDGE_DB` before importing any
bridge package module, not just before importing `runtime`; then remove relevant
`sys.modules` entries and import/reload inside the isolated fixture or test.
Use `pytest.MonkeyPatch` directly for broader-scope setup if a function-scoped
fixture is not sufficient.

### 4. Major - Pattern B/C/D arithmetic still mixes combined terminal percentages with line/branch percentages

Revision 2 computes Pattern B/C/D gains from the terminal `Cover` percentages
as if those values were both statement and branch baselines. Coverage JSON shows
that the current statement and branch percentages differ materially:
`upgrade.py` is `20.19%` statements and `0.00%` branches, `doctor.py` is
`58.14%` statements and `41.67%` branches, and `scaffold.py` is already
`74.18%` statements and `59.72%` branches. Revision 2 nevertheless projects
`scaffold.py` statement gain from `70% -> 73%`, even though statement coverage
already exceeds 73%.

**Risk/impact:** Some of the combined-item totals happen to mostly cancel out,
but the statement and branch projections are misleading. With only a 0.3pp
combined margin in `bridge/gtkb-phase4b8-line-coverage-003.md:148`, this is too
thin for arithmetic based on mixed metrics.

**Required action:** Recompute Pattern B/C/D from coverage JSON per-file
summaries, using explicit covered-item targets for statements and branches
rather than terminal `Cover` percentages. Because the combined margin is only
about 25 items, add an adaptive stop condition that expands tests until combined
coverage clears the gate with a real buffer, not merely a rounded pass.

## Required Revision Conditions

Prime should resubmit with:

1. Pattern A rewritten against source-verified public APIs, or explicitly
   re-scoped as a runtime API change if new wrappers/classes are intended.
2. `percent_statements_covered >= 70.0%` as a hard exit criterion alongside
   combined >=70.0% and branch >=55.0%.
3. Bridge import isolation instructions that set `PRIME_BRIDGE_DB` before any
   `groundtruth_kb.bridge.*` import and forbid top-level bridge imports in the
   new tests.
4. Pattern B/C/D arithmetic recomputed from coverage JSON per-file statement
   and branch summaries, with explicit integer covered-item targets.

## Decision Needed From Owner

No owner decision is needed if Prime revises the proposal to keep Phase 4B.8 as
a test-only round and meet the existing `70% line / 55% branch` target. Owner
approval would be needed only if Prime wants to change runtime APIs as part of
this coverage round or defer the statement coverage target.

## Verification Notes

Full pytest was not run for this review. The proposal is blocked by static
source/proposal mismatches and exit-criteria gaps before implementation-level
test execution would be informative.
