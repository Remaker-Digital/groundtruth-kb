# GT-KB Phase 4B.8 — Line Coverage 52% → 70%

**Status:** NEW
**Prime Builder:** Claude Opus 4.6
**Author session:** S295 (worktree `elegant-brattain`)
**Repository:** `groundtruth-kb` @ `ff6988b` (main, post 4B.7)
**Branch:** will be created as `phase-4b8-line-coverage` off `main`

## Prior Deliberations

This is the next sub-round after **Phase 4B.7** (residual `mypy --strict` errors 39 → 0), committed as `f59dad4` and VERIFIED at `bridge/gtkb-phase4b7-residual-mypy-strict-010.md`. Plan tracked in `docs/reports/phase-4b-plan.md` which lists 4B.8 as the next proposed sub-round after 4B.7 closed.

Methodology lesson from the 4B.7 bridge cycle: **never propose a fix pattern without empirical verification first**. For mypy/type sub-rounds the verification is `mypy --strict` against a standalone snippet. For coverage, the equivalent is concrete measurement of current state and arithmetic estimate of target delta — both included below.

Prior VERIFIED 4B sub-rounds (unchanged): 4B.1, 4B.2, 4B.3, 4B.4, 4B.5a, 4B.5b, 4B.6, 4B.7.

## Ground-Truth Measurement

Run verbatim against `ff6988b` (current main) immediately before drafting:

```bash
cd /e/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
python -m pytest --cov=groundtruth_kb --cov-branch --cov-report=term -q
# 640 passed, 342 warnings in 150.50s
# TOTAL: 6621 stmts, 3021 miss, 2420 branches, 262 brpart, 52% cover
```

### Per-file coverage distribution

**Bridge submodule (0% coverage — the biggest gap):**

| File | Stmts | Branches | Current | Target (4B.8) |
|---|---|---|---|---|
| `bridge/runtime.py` | 558 | 230 | 0% | 60% |
| `bridge/context.py` | 471 | 238 | 0% | 60% |
| `bridge/worker.py` | 421 | 142 | 0% | 55% |
| `bridge/poller.py` | 335 | 96 | 0% | 55% |
| `bridge/launcher.py` | 152 | 44 | 0% | 50% |
| `bridge/handshake.py` | 97 | 40 | 0% | 50% |
| `bridge/__init__.py` | 5 | 0 | 0% | 100% |
| **Bridge total** | **2039** | **790** | **0%** | **~58%** |

**Other below-target files:**

| File | Stmts | Current | Target (4B.8) |
|---|---|---|---|
| `project/upgrade.py` | 104 | 14% | 50% |
| `project/doctor.py` | 258 | 54% | 60% |
| `project/scaffold.py` | 182 | 70% | 72% |
| `cli.py` | 785 | 73% | 73% (no change — already at 4B.6 per-file gate) |
| `db.py` | 1608 | 73% | 73% (no change — already at 4B.6 per-file gate) |

**Already-good files (≥80% — no action):**
`assertion_schema.py` 91%, `assertions.py` 85%, `bootstrap.py` 93%, `config.py` 95%, `gates.py` 94%, `gates_transport.py` 97%, `health.py` 92%, `impact.py` 92%, `intake.py` 85%, `reconciliation.py` 82%, `seed.py` 100%, `spec_scaffold.py` 97%, `web/app.py` 92%.

### Coverage arithmetic (pre-validated)

- Current covered: 6621 − 3021 = **3,600 stmts (52.0%)**
- 70% target: 6621 × 0.70 = **4,635 stmts**
- Delta required: **+1,035 stmts**
- Covering `bridge/` at 58% average: 2039 × 0.58 = **+1,183 stmts**
- Plus `project/upgrade.py` at 50%: +(104 × 0.36) = **+37 stmts**
- Plus `project/doctor.py` at 60%: +(258 × 0.06) = **+15 stmts**
- Plus `project/scaffold.py` at 72%: +(182 × 0.02) = **+4 stmts**
- **Projected delta: +1,239 stmts → 4,839 covered → 73.1%**
- Margin above 70%: **3.1 percentage points**, enough to absorb coverage measurement noise from integration-test overlap.

## Objective

Drive `pytest --cov=groundtruth_kb --cov-branch` global line coverage from **52% → 70%** (firm target; Phase 4A baseline), with branch coverage as a secondary metric (Phase 4A target 55%; current global branch % not explicitly in the default term report — will be measured and reported in the post-impl report). Zero runtime behavior change; this is pure test addition.

Add a CI regression guard: `pytest-cov --cov-fail-under=70` on the main pytest invocation in `.github/workflows/ci.yml`.

## Scope — Test Additions

### Pattern A — Bridge smoke tests (`tests/bridge/` new directory)

For each of the 6 non-trivial bridge files (`runtime.py`, `context.py`, `worker.py`, `poller.py`, `launcher.py`, `handshake.py`), add a smoke test module under `tests/bridge/` that exercises:

1. **Import path** — `import groundtruth_kb.bridge.<module>` succeeds
2. **Public class/function instantiation** — each public class can be instantiated with valid arguments; each public function can be called with valid arguments
3. **Happy-path behavior** — one end-to-end call with a realistic input, asserting the output shape and key fields
4. **Error-path behavior** — one invalid input that triggers the documented error handling (matches the guards from 4B.7's Pattern C intake work)

**Test files to add:**

| Test file | Targets | Expected new tests |
|---|---|---|
| `tests/bridge/test_handshake.py` | `bridge.handshake.perform_handshake`, key validation, replay protection | 8 |
| `tests/bridge/test_context.py` | `DBBridgeContext`, `resolve_artifact_name`, `dedupe_preserve_order`, `prioritize_inbox_items` | 15 |
| `tests/bridge/test_launcher.py` | `BridgeLauncher`, argument parsing, process spawning (subprocess mocked) | 10 |
| `tests/bridge/test_poller.py` | `_FileLock` (using temp file), `_handle_notification_batch`, `_handle_inbox`, `_load_state`, `_save_state`, poller summary TypedDicts (verify 4B.7 shapes) | 20 |
| `tests/bridge/test_worker.py` | `_FileLock` (same pattern), `resident_worker_should_defer`, event batch forward-declaration (verify 4B.7 Pattern F), `wait_for_notifications` (bridge mocked) | 18 |
| `tests/bridge/test_runtime.py` | `KnowledgeDBBridge`, message insert/get, `send_correction_message`, JSON `_loads_json` narrowing (verify 4B.7 Pattern E), Agent literal validation | 25 |
| **Total new tests** | | **~96** |

Test count estimate is conservative: smoke tests typically achieve 40-60% file coverage per ~10 tests, depending on branching density. Bridge files are medium-branching (branches ≈ 30-45% of statements).

### Pattern B — `project/upgrade.py` tests (`tests/project/test_upgrade.py`)

`project/upgrade.py` is at 14% coverage with 104 statements — the lowest-coverage file of meaningful size. Add ~12 tests covering:

- Version comparison helpers
- Upgrade plan construction
- Dry-run mode
- Error paths: invalid source version, missing target, read-only filesystem

Expected delta: +37 stmts (+0.56pp global).

### Pattern C — `project/doctor.py` additional tests (`tests/project/test_doctor.py` extension)

`project/doctor.py` is at 54%. Add ~10 tests covering the uncovered `_check_*` helper functions (likely check_specs, check_tests, check_links, check_orphans, etc.) with synthetic KB fixtures.

Expected delta: +15 stmts (+0.23pp global).

### Pattern D — `project/scaffold.py` edge-case tests

`project/scaffold.py` is at 70% (already close). Add ~3 tests for the 2% gap:
- Idempotent scaffold re-run
- Conflict with existing file
- Scaffold with all optional flags enabled

Expected delta: +4 stmts (+0.06pp global).

## Out of Scope (Explicitly)

- **Whole-package docstring coverage.** That's Phase 4B.9, next sub-round.
- **Logging migration.** That's Phase 4C.
- **Branch coverage separate target.** The Phase 4A baseline names 55% branch as a target; this proposal tracks branch coverage as a reported secondary metric (measured in post-impl report) but does not gate on it. Rationale: line coverage gate is the blunt instrument that guarantees behavioral exercise; branch-specific gating adds measurement complexity and tooling (requires `cov-report=xml` + separate branch extraction) disproportionate to the 55% target which is ~54% at projection with the proposed tests.
- **Tests that duplicate existing coverage.** The test plan avoids writing bridge integration tests that duplicate what `test_bridge_collaboration_protocol.py` already covers (if present — will be checked during implementation).
- **Tests that exercise private internals.** GOV-10 rule: tests exercise public interfaces, not `_private` functions directly. The `_FileLock` test is an exception — it is the documented internal locking primitive and has no public equivalent.

## Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Bridge runtime tests require DB setup + bridge table creation | High | Use the existing bridge test fixtures from `tests/test_bridge_collaboration_protocol.py` (or similar); inherit the `tmp_path` + `KnowledgeDB(path=...)` pattern used elsewhere |
| MCP tool registration (`KnowledgeDBBridge.list_tools`) may require live FastMCP runtime | Medium | Mock `FastMCP` at the module level; assert on registered tool names, not live MCP invocation |
| Subprocess-spawning code (`poller.run()`, `launcher.BridgeLauncher`) is hard to test | Medium | Mock `subprocess.Popen` / `subprocess.run`; assert on command-line construction rather than execution |
| Coverage measurement noise from integration test overlap | Low | The 3.1pp margin above 70% absorbs expected ±2pp measurement variation |
| File-lock tests race under parallel pytest | Low | Use unique `tmp_path` per test; mark explicit `pytest.mark.skip_win32` or similar if lock path collides |
| New tests reveal pre-existing bugs in bridge code | Medium | If a test fails because the bridge code is buggy (not because the test is wrong), stop and file a separate bridge entry for the bug. Do not fix the bug under 4B.8's scope. |
| Target 70% misses by ≤2pp due to projection error | Low | The arithmetic projection is +3.1pp above target. If actual delta is +1.1pp, global = 70.0% exactly. Acceptable. |

## Test Plan

1. **Per-test-file:** After each new test file, run:
   ```bash
   python -m pytest tests/bridge/test_<module>.py -v --tb=short
   python -m pytest --cov=groundtruth_kb.bridge.<module> --cov-report=term
   ```
   Assert: 100% new test pass rate; per-file coverage reaches the target stated in the §Per-file coverage distribution table.

2. **Pattern A cumulative check** (after all 6 bridge smoke-test files land):
   ```bash
   python -m pytest --cov=groundtruth_kb --cov-branch --cov-report=term -q
   ```
   Assert: `bridge/` total coverage ≥ 50%; global coverage ≥ 66% (short of 70% target before project/ additions).

3. **Pattern B/C/D cumulative check:**
   ```bash
   python -m pytest --cov=groundtruth_kb --cov-branch --cov-report=term -q
   ```
   Assert: global coverage ≥ 70%.

4. **Full regression suite:**
   ```bash
   python -m pytest -q
   ```
   Assert: 640 + ~96 + ~25 = ~761 passed, 0 failed.

5. **mypy --strict still clean:**
   ```bash
   python -m mypy --strict src/groundtruth_kb/
   ```
   Assert: `Success: no issues found in 31 source files`. (4B.7 regression check.)

6. **Ruff:**
   ```bash
   python -m ruff check .
   python -m ruff format --check .
   ```
   Assert: both clean.

7. **CI workflow update:**
   Add `--cov-fail-under=70` to the pytest command in `.github/workflows/ci.yml`, adjacent to the existing pytest run. Verify the CI file passes the existing per-file coverage gates from 4B.6 AND the new global gate.

## Exit Criteria

All must be true:

1. `pytest --cov=groundtruth_kb --cov-branch --cov-report=term` → global line coverage ≥ **70.0%**
2. All existing tests still pass (638 + 2 from 4B.7 = 640 prior; new total = 640 + ~121 = ~761)
3. `mypy --strict src/groundtruth_kb/` → Success, 0 errors (4B.7 regression guard)
4. `ruff check .` and `ruff format --check .` both clean
5. `.github/workflows/ci.yml` gains `--cov-fail-under=70` on the main pytest invocation
6. Per-file coverage gates from 4B.6 (`db.py` 68%, `cli.py` 68%, `config.py` 80%, `gates.py` 92%) are NOT tightened in this PR (separate concern)
7. CHANGELOG entry under `[Unreleased]` → `### Added` for new tests; `### Changed` for CI gate update
8. No existing test deleted or skipped; no behavior change in `src/`
9. Bridge submodule reaches at least 50% coverage across all 6 non-trivial files
10. `project/upgrade.py` reaches at least 50% coverage

## Rollback

Single squash-merged PR. `git revert <merge-sha>` on main. Rollback loses ~121 tests but no production behavior. Test-only PR — zero blast radius.

## Estimated Effort

- Drafting + measurement: already done (this proposal, ~45 min)
- Bridge smoke tests (Pattern A, 6 files, ~96 tests): **~4 hours focused work**
  - `test_handshake.py` and `test_context.py` first (lowest risk)
  - `test_poller.py` and `test_worker.py` (file-lock complexity)
  - `test_runtime.py` (MCP mocking complexity, largest file)
  - `test_launcher.py` (subprocess mocking)
- Pattern B/C/D (project/ tests, ~25 tests): **~1.5 hours**
- Per-test-file iteration and per-file coverage verification: **~1 hour**
- CI gate + CHANGELOG: **~15 min**
- **Total: ~7 hours wall-clock**

This is the largest 4B sub-round yet. Proposing that it proceed incrementally: Pattern A bridge tests first (most of the work + most of the coverage delta), then Pattern B/C/D as a tail.

## Open Decisions Requested From Codex

1. **Test directory structure.** Current `tests/` is flat (no subdirectories for existing test files). Should bridge tests go in `tests/bridge/` or stay flat as `tests/test_bridge_<module>.py`? Flat is consistent with existing convention; subdirectory is cleaner for 6 related files. **Recommendation: `tests/bridge/` subdirectory.**

2. **FastMCP mocking approach.** `bridge/runtime.py` imports FastMCP at module level. Two mocking options: (a) `unittest.mock.patch("groundtruth_kb.bridge.runtime.FastMCP")` at each test; (b) a shared fixture in `conftest.py`. **Recommendation: (b) shared fixture.**

3. **Coverage fail-under value.** 70% is Phase 4A target. Should CI gate at exactly 70%, or 69% (1pp buffer) to absorb measurement noise? **Recommendation: 69%** — matches the 4B.6 convention of gating ~1pp below target to avoid CI flakes.

4. **Existing bridge tests (if any).** If the repo already has `tests/test_bridge_*.py` files that happen to exercise bridge/ code, the per-file 0% coverage measurement suggests they either don't exist or don't import the bridge modules. Implementation should verify with `grep -r "from groundtruth_kb.bridge" tests/` and not duplicate coverage. Proposal assumes 0% really means "0% — no bridge tests exist yet"; if that's wrong, scope shrinks by the overlap amount.

## Appendix A — Current coverage report verbatim

```
Name                                     Stmts   Miss Branch BrPart  Cover
--------------------------------------------------------------------------
src\groundtruth_kb\__init__.py              17      2      4      2    81%
src\groundtruth_kb\__main__.py               4      4      2      0     0%
src\groundtruth_kb\assertion_schema.py      80      6     66      7    91%
src\groundtruth_kb\assertions.py           423     49    196     33    85%
src\groundtruth_kb\bootstrap.py            105      4     30      6    93%
src\groundtruth_kb\bridge\__init__.py        5      5      0      0     0%
src\groundtruth_kb\bridge\context.py       471    471    238      0     0%
src\groundtruth_kb\bridge\handshake.py      97     97     40      0     0%
src\groundtruth_kb\bridge\launcher.py      152    152     44      0     0%
src\groundtruth_kb\bridge\poller.py        335    335     96      0     0%
src\groundtruth_kb\bridge\runtime.py       558    558    230      0     0%
src\groundtruth_kb\bridge\worker.py        421    421    142      0     0%
src\groundtruth_kb\cli.py                  785    176    218     45    73%
src\groundtruth_kb\config.py                93      3     36      3    95%
src\groundtruth_kb\db.py                  1608    419    526     72    73%
src\groundtruth_kb\gates.py                 74      3     30      3    94%
src\groundtruth_kb\gates_transport.py       46      1     22      1    97%
src\groundtruth_kb\health.py                52      3     14      2    92%
src\groundtruth_kb\impact.py               121      6     70     10    92%
src\groundtruth_kb\intake.py               143     18     58     12    85%
src\groundtruth_kb\project\__init__.py       3      0      0      0   100%
src\groundtruth_kb\project\doctor.py       258    108     84     19    54%
src\groundtruth_kb\project\manifest.py      51     11     20      6    70%
src\groundtruth_kb\project\profiles.py      20      3      2      1    82%
src\groundtruth_kb\project\scaffold.py     182     47     72     15    70%
src\groundtruth_kb\project\upgrade.py      104     83     46      0    14%
src\groundtruth_kb\reconciliation.py       188     27     94     22    82%
src\groundtruth_kb\seed.py                  29      0     12      0   100%
src\groundtruth_kb\spec_scaffold.py         70      1     16      2    97%
src\groundtruth_kb\web\__init__.py           2      0      0      0   100%
src\groundtruth_kb\web\app.py              124      8     12      1    92%
--------------------------------------------------------------------------
TOTAL                                     6621   3021   2420    262    52%
640 passed, 342 warnings in 150.50s (0:02:30)
```

## Change Methodology Commitment

Per the 4B.7 lesson: no implementation step will be taken without measuring its effect. Specifically:

- Per-file coverage targets in the §Per-file coverage distribution table will be re-measured after each test file lands, and any test file that fails to reach its named target will be revisited before the next file begins.
- Global coverage will be re-measured after Pattern A completes (all bridge tests) and before Pattern B/C/D begin.
- The CI `--cov-fail-under=70` gate will be added in the SAME commit as the final coverage-delivering test file, so CI never temporarily fails on main.
- If the projected global delta falls short, implementation will EXPAND Pattern A's bridge tests before touching Pattern B/C/D — bridge is the highest-ROI cluster.
