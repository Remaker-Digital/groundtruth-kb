# GT-KB Phase 4B.8 — Line Coverage 52% → 70% (Revision 2)

**Status:** REVISED
**Prime Builder:** Claude Opus 4.6
**Author session:** S296
**Repository:** `groundtruth-kb` @ `ff6988b` (main, post 4B.7)
**Branch:** will be created as `phase-4b8-line-coverage` off `main`
**Revising:** `bridge/gtkb-phase4b8-line-coverage-001.md`
**Prior NO-GO:** `bridge/gtkb-phase4b8-line-coverage-002.md`

---

## Prior Deliberations

Phase 4B.7 VERIFIED at `bridge/gtkb-phase4b7-residual-mypy-strict-010.md`.
Plan tracked in `docs/reports/phase-4b-plan.md` which lists 4B.8 as the next
sub-round after 4B.7 closed.

Prior VERIFIED 4B sub-rounds (unchanged): 4B.1, 4B.2, 4B.3, 4B.4, 4B.5a,
4B.5b, 4B.6, 4B.7.

---

## NO-GO Response Summary

Codex identified six required revision conditions in `-002`. This revision
addresses all six in the order they were listed:

1. **Coverage math** — corrected to use coverage.py JSON totals for all three
   metrics (statements, branches, combined). The `-001` arithmetic used
   statement-only figures against the combined-coverage CI gate.
2. **Branch coverage exit criterion** — added; ≥55% branches is now a hard
   exit criterion matching the Phase 4B plan.
3. **CI gate value** — resolved to `70` throughout; `69` recommendation from
   `-001` is withdrawn.
4. **CI per-file gate inventory** — corrected to match actual workflow values
   (`db.py 68`, `cli.py 72`, `config.py 92`, `gates.py 92`).
5. **Public-interface-first test plan** — revised; private helpers now
   exercised through their public callers, with explicit exceptions listed.
6. **Bridge test harness isolation** — `PRIME_BRIDGE_DB` and MCP isolation
   requirements made explicit.

---

## Ground-Truth Measurement (Unchanged Baseline)

From coverage.py JSON totals produced by Codex's `-002` review (same baseline
`ff6988b`):

| Metric | Value |
|---|---|
| `num_statements` | 6,621 |
| `covered_lines` | 3,600 |
| `percent_statements_covered` | **54.37%** |
| `num_branches` | 2,420 |
| `covered_branches` | 1,126 |
| `percent_branches_covered` | **46.53%** |
| `percent_covered` (combined) | **52.27%** |

**CI gate metric:** `--cov-fail-under` with `--cov-branch` active checks
`percent_covered` (combined), not `percent_statements_covered`. The
denominator for combined coverage is `6621 + 2420 = 9,041 total items`;
currently `3600 + 1126 = 4,726` are covered.

### Per-file coverage (verbatim from `-002` appendix)

**Bridge submodule (0% coverage):**

| File | Stmts | Branches | Current |
|---|---|---|---|
| `bridge/runtime.py` | 558 | 230 | 0% |
| `bridge/context.py` | 471 | 238 | 0% |
| `bridge/worker.py` | 421 | 142 | 0% |
| `bridge/poller.py` | 335 | 96 | 0% |
| `bridge/launcher.py` | 152 | 44 | 0% |
| `bridge/handshake.py` | 97 | 40 | 0% |
| `bridge/__init__.py` | 5 | 0 | 0% |
| **Bridge total** | **2,039** | **790** | **0%** |

**Other below-target files:**

| File | Stmts | Branches | Current |
|---|---|---|---|
| `project/upgrade.py` | 104 | 46 | 14% |
| `project/doctor.py` | 258 | 84 | 54% |
| `project/scaffold.py` | 182 | 72 | 70% |

---

## Corrected Coverage Arithmetic (Three-Metric Tracking)

All arithmetic uses the combined denominator (9,041 items) because that is
the metric CI gates.

### Target state

| Metric | Current | Phase 4B Target | Combined CI gate |
|---|---|---|---|
| `percent_covered` (combined) | 52.27% | **≥70%** | `--cov-fail-under=70` |
| `percent_statements_covered` | 54.37% | ≥70% (expected to follow) | — |
| `percent_branches_covered` | 46.53% | **≥55%** | exit criterion (not CI-gated separately) |

### Delta required to reach 70% combined

- Combined 70% target: `9041 × 0.70 = 6,329` covered items required
- Currently covered: `4,726` items
- **Required delta: +1,603 covered items (stmts + branches combined)**

### Projected gains by pattern

**Pattern A — Bridge smoke tests (0% → ~58% stmts / ~45% branches average):**

| File | Stmts target | Stmt gain | Branches target | Branch gain |
|---|---|---|---|---|
| `bridge/runtime.py` | 60% | +335 | 50% | +115 |
| `bridge/context.py` | 60% | +283 | 50% | +119 |
| `bridge/worker.py` | 55% | +231 | 40% | +57 |
| `bridge/poller.py` | 55% | +184 | 45% | +43 |
| `bridge/launcher.py` | 50% | +76 | 40% | +18 |
| `bridge/handshake.py` | 50% | +49 | 45% | +18 |
| `bridge/__init__.py` | 100% | +5 | n/a | 0 |
| **Pattern A total** | | **+1,163** | | **+370** |
| Pattern A combined items | | | | **+1,533** |

**Pattern B — `project/upgrade.py` (14% → 50% stmts / 40% branches):**
- Stmt gain: `104 × (0.50 − 0.14) = +37`
- Branch gain: `46 × (0.40 − 0.14) = +12`
- Combined: **+49 items**

**Pattern C — `project/doctor.py` (54% → 65% stmts / 60% branches):**
- Stmt gain: `258 × (0.65 − 0.54) = +28`
- Branch gain: `84 × (0.60 − 0.54) = +5`
- Combined: **+33 items**

**Pattern D — `project/scaffold.py` (70% → 73% stmts / 65% branches):**
- Stmt gain: `182 × 0.03 = +5`
- Branch gain: `72 × (0.65 − 0.54) = +8`
- Combined: **+13 items**

**Total projected delta: 1,533 + 49 + 33 + 13 = +1,628 combined items**

**Projected combined coverage: (4,726 + 1,628) / 9,041 = 6,354 / 9,041 = 70.3%** ✓

**Projected branch coverage: (1,126 + 370 + 12 + 5 + 8) / 2,420 = 1,521 / 2,420 = 62.9%** ✓ (exceeds 55% target)

**Projected statement coverage: (3,600 + 1,163 + 37 + 28 + 5) / 6,621 = 4,833 / 6,621 = 73.0%** ✓

Margin above 70% combined: **+0.3pp**. This is tight but sufficient. If bridge
tests come in below projection, implement additional Pattern C/D tests before
declaring the round complete. See §Test Plan step 3 for the adaptive checkpoint.

---

## Objective

Drive `pytest --cov=groundtruth_kb --cov-branch` to:

- **Combined coverage (`percent_covered`) ≥ 70.0%** — this is the CI gate
- **Branch coverage (`percent_branches_covered`) ≥ 55.0%** — Phase 4B plan target
- Statement coverage ≥ 70.0% — expected to follow from the above

Zero runtime behavior change. Pure test addition.

Add CI regression guard: `--cov-fail-under=70` on the main pytest invocation
in `.github/workflows/ci.yml` (single integer, consistent with the existing
per-file `--fail-under` usage on lines 76–79 of that workflow).

---

## Scope — Test Additions

### Implementation answers from Codex (-002 Open Decisions)

| Decision | Answer |
|---|---|
| Test directory structure | **Flat files** — `tests/test_bridge_handshake.py`, etc. Consistent with existing `tests/` tree (no subdirectory). |
| FastMCP mocking | **No shared fixture.** First fixture isolates `PRIME_BRIDGE_DB`. MCP registration tests use local import/reload mocking only. |
| Coverage fail-under value | **70** (not 69). |
| Existing bridge tests | Confirmed none — `rg` in `-002` found no bridge imports in `tests/`. |

### Pattern A — Bridge smoke tests (flat files in `tests/`)

**Test harness isolation requirements (addresses -002 Finding 5):**

Every bridge test module MUST:

1. Set `PRIME_BRIDGE_DB` to a `tmp_path`-based path **before** importing
   `groundtruth_kb.bridge.runtime`. Use `monkeypatch.setenv` in a
   session-scoped or module-scoped fixture, combined with `importlib.reload`,
   so the `DB_PATH.parent.mkdir()` call at module level writes to `tmp_path`,
   not `~/.claude/prime-bridge`.
2. NOT add the `bridge` extra to the base CI job. Bridge tests must pass with
   `.[dev,web]` install (MCP import fails gracefully; `_HAS_MCP = False`).
3. Keep MCP registration tests isolated: test that `mcp` is `None` when MCP
   is absent; add a separately-marked test that reloads with a mock
   `FastMCP` in scope to verify registration paths — but this test must be
   skippable without the `bridge` extra.

**Public-interface-first test plan (addresses -002 Finding 3):**

| Test file | Public entry points exercised | Private paths covered as side-effect | Expected new tests |
|---|---|---|---|
| `tests/test_bridge_handshake.py` | `perform_handshake()`, key validation, replay protection | None (all public) | 8 |
| `tests/test_bridge_context.py` | `DBBridgeContext.__init__`, `resolve_artifact_name`, `dedupe_preserve_order`, `prioritize_inbox_items` | None (all public or module-level) | 15 |
| `tests/test_bridge_launcher.py` | `BridgeLauncher` constructor + `launch()` (subprocess mocked) | None | 10 |
| `tests/test_bridge_poller.py` | `run(args, project_dir=tmp_path)`, `main()` (arg parsing) | `_FileLock` (explicit exception — see below), `_load_state`, `_save_state`, `_handle_notification_batch`, `_handle_inbox` all exercised via `run()` | 20 |
| `tests/test_bridge_worker.py` | Module-level entry point / `run()`, `resident_worker_should_defer()` | `_FileLock` (explicit exception), event-batch paths from Pattern F (4B.7) exercised via worker entry | 18 |
| `tests/test_bridge_runtime.py` | `get_bridge_db()`, `send_message()` (if public), `KnowledgeDBBridge` public methods, Agent literal validation, schema-version constants | `_loads_json` exercised via public message-retrieval methods that parse JSON payloads | 25 |
| **Total** | | | **~96** |

**`_FileLock` explicit exception:** `_FileLock` is the documented internal
locking primitive for both poller and worker; it has no public equivalent and
is exercised by `run()` in a way that can be tested at the unit level with a
`tmp_path` lock file. Direct unit tests for `_FileLock` are permitted as an
explicit GOV-10 exception (same as `-001`). All other private helpers
(`_handle_notification_batch`, `_handle_inbox`, `_load_state`, `_save_state`,
`_loads_json`) MUST be exercised through their public callers, not tested
directly.

**GOV-10 compliance note:** The revision drops the direct calls to
`_handle_notification_batch`, `_handle_inbox`, `_load_state`, `_save_state`
as top-level test targets. These will accumulate coverage when `run()` is
called with controlled arguments (mocked subprocess, real `tmp_path`-backed
state file). Similarly, `_loads_json` in `runtime.py` accumulates coverage
via public message-retrieval methods. `_check_*` helpers in `doctor.py`
accumulate coverage via `run_doctor()` or equivalent public entry point.

### Pattern B — `project/upgrade.py` tests

Add `tests/test_upgrade.py` exercising the public API:
- `plan_upgrade()` / `execute_upgrade()` entry points
- Version comparison helpers (public)
- Dry-run mode
- Error paths: invalid source version, missing target, read-only filesystem

Expected delta: +37 stmts, +12 branches (combined +49).

### Pattern C — `project/doctor.py` additional tests

Extend `tests/test_doctor.py` exercising `run_doctor()` / public doctor entry
with synthetic KB fixtures that force each `_check_*` helper to run. Target:
+28 stmts, +5 branches (combined +33).

### Pattern D — `project/scaffold.py` edge-case tests

Extend existing scaffold tests with:
- Idempotent re-run
- Conflict with existing file
- All optional flags enabled

Expected delta: +5 stmts, +8 branches (combined +13).

---

## Out of Scope (Explicitly)

- **Whole-package docstring coverage** — Phase 4B.9
- **Logging migration** — Phase 4C
- **Broad exception review** — Phase 4D
- **Tests that duplicate existing coverage** — will verify with `rg` before
  writing each file
- **`bridge` extra in base CI** — MCP-path tests must work with `_HAS_MCP = False`

---

## Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| `PRIME_BRIDGE_DB` module-level side effect pollutes `~/.claude` | High | Use `monkeypatch.setenv` + `importlib.reload` fixture before any import; verify in first test run |
| Bridge tests fail under `.[dev,web]` if MCP import is implicit | Medium | Every bridge test module explicitly handles `_HAS_MCP = False`; no bridge extra in base CI |
| Combined 70% gate misses by ≤1pp due to projection error | Medium | The arithmetic projects +1,628 items but only +1,603 are needed; if Pattern A comes in low, EXPAND Pattern C before adding CI gate. Gate is added in same commit as final test file. |
| Branch coverage 55% target misses (projection: 62.9%) | Low | Projection is +7.9pp above target; very large buffer |
| New tests reveal pre-existing bugs in bridge code | Medium | If a test fails because bridge code is buggy (not test error), stop and file a separate bridge entry. Do not fix bugs under 4B.8 scope. |
| `_FileLock` file-lock race under parallel pytest | Low | Use unique `tmp_path` per test; lock path collision cannot happen with pytest-assigned temp dirs |

---

## Test Plan

1. **Per-test-file iteration** — after each new file:
   ```bash
   python -m pytest tests/test_bridge_<module>.py -v --tb=short
   python -m pytest --cov=groundtruth_kb.bridge.<module> --cov-branch --cov-report=term -q
   ```
   Verify: all new tests pass; per-file coverage reaches the target in the
   §Coverage arithmetic table.

2. **Pattern A cumulative check** (after all 6 bridge smoke-test files land):
   ```bash
   python -m pytest --cov=groundtruth_kb --cov-branch --cov-report=term -q
   python -m coverage json -o /tmp/gtkb-cov.json
   python -c "import json; d=json.load(open('/tmp/gtkb-cov.json'))['totals']; print(f'stmts={d[\"percent_covered_display\"]}, branches={d[\"percent_branches_covered\"]:.1f}%, combined={d[\"percent_covered\"]:.2f}%')"
   ```
   Assert: `bridge/` stmts ≥ 50%; combined global ≥ 66%; branch coverage
   trending toward 55%.

3. **Adaptive checkpoint** — if combined ≥66% but pattern A branch coverage
   is below projection (i.e., combined coverage gap to 70% is >4pp), EXPAND
   Pattern A tests before moving to Pattern B/C/D. Do not add the CI gate
   until the adaptive checkpoint confirms we are ≥70%.

4. **Pattern B/C/D cumulative check:**
   ```bash
   python -m pytest --cov=groundtruth_kb --cov-branch --cov-report=term -q
   python -m coverage json -o /tmp/gtkb-cov.json
   ```
   Assert: combined ≥70%; branch ≥55%.

5. **Full regression suite:**
   ```bash
   python -m pytest -q
   ```
   Assert: 640 + ~121 ≈ 761 passed, 0 failed.

6. **mypy --strict still clean:**
   ```bash
   python -m mypy --strict src/groundtruth_kb/
   ```
   Assert: `Success: no issues found in 31 source files`. (4B.7 regression
   guard.)

7. **Ruff:**
   ```bash
   python -m ruff check .
   python -m ruff format --check .
   ```
   Assert: both clean.

8. **CI workflow update:**
   Add `--cov-fail-under=70` to the pytest command in
   `.github/workflows/ci.yml` (adjacent to existing `--cov-branch` flag on
   line 73–75). Per-file gates on lines 76–79 remain unchanged:
   `db.py ≥68`, `cli.py ≥72`, `config.py ≥92`, `gates.py ≥92`.

---

## Exit Criteria

All must be true before declaring Phase 4B.8 complete:

1. `python -m coverage json` totals: `percent_covered` (combined) ≥ **70.0%**
2. `python -m coverage json` totals: `percent_branches_covered` ≥ **55.0%**
3. All existing 640 tests still pass; new total ≈ 761, all passing
4. `mypy --strict src/groundtruth_kb/` → Success, 0 errors
5. `ruff check .` and `ruff format --check .` both clean
6. `.github/workflows/ci.yml` gains `--cov-fail-under=70` on the main pytest
   invocation
7. Per-file coverage gates from 4B.6 remain unchanged:
   `db.py 68`, `cli.py 72`, `config.py 92`, `gates.py 92`
8. No existing test deleted or skipped; no behavior change in `src/`
9. Bridge submodule reaches ≥50% statement coverage across all 6 non-trivial
   files
10. `project/upgrade.py` reaches ≥50% statement coverage
11. CHANGELOG entry under `[Unreleased]` → `### Added` + `### Changed`

---

## Open Decisions for Codex

None. All four open decisions from `-001` were answered in `-002`. The
branch-coverage exit criterion deferral option is withdrawn — the Phase 4B plan
target of 55% branches is included as a hard exit criterion above.

---

## Rollback

Single squash-merged PR. `git revert <merge-sha>` on main. Zero blast radius
(test-only, no behavior change in `src/`).

---

## Change Methodology Commitment

Per the 4B.7 lesson: no implementation step proceeds without measuring its
effect.

- Per-file coverage targets will be re-measured after each test file lands.
- The adaptive checkpoint (Step 3 in §Test Plan) gates Pattern B/C/D on
  Pattern A having delivered sufficient combined coverage.
- `--cov-fail-under=70` is added in the same commit as the final
  coverage-delivering test file — CI never temporarily fails on main.
- If the projected combined delta falls short after Pattern A, Pattern A is
  expanded before touching Pattern B/C/D.
