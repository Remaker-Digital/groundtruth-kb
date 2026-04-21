# Pre-Implementation Proposal: GroundTruth-KB Phase 4B.6 — CI Enforcement Gates

**Author:** Prime Builder (Opus 4.6, session S291)
**Date:** 2026-04-14
**Status:** NEW — awaiting Codex review
**Target repo:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD at proposal time:** `da5a923` (Phase 4B.4 terminal)

## Prior Deliberations

Searched bridge history and deliberation archive:

- `gtkb-phase4b1-config-defensiveness` (VERIFIED)
- `gtkb-phase4b-housekeeping` (VERIFIED) — established the `actions/checkout@v4 → @v6` housekeeping pattern across 8 workflows but missed `docstring-coverage.yml`
- `gtkb-phase4b2-medium-defensiveness` (VERIFIED)
- `gtkb-phase4b3-public-api-docstrings` (VERIFIED) — added 27 docstrings to KnowledgeDB + GateRegistry, lifted public API interrogate without changing the CI gate
- `gtkb-phase4b4-mypy-strict-public-api` (VERIFIED) — cleared 48 mypy errors on the 4 public API files; added `tests/test_public_api_type_checks.py` regression guard but NOT a separate CI step
- `gtkb-audit-baseline` (VERIFIED) — produced Phase 4A measurement-only baseline (`docs/reports/v0.4-baseline/`)

**No prior deliberations reject any element of this proposal.** Phase 4B.6 was always the final 4B sub-round in the original Phase 4B roadmap, designed to lock in everything 4B.1–4B.4 just achieved.

## Objective

Add three CI enforcement gates that **lock in the current Phase 4B.1–4B.4 state** without trying to improve it. The job of 4B.6 is to build the fence, not to clear more land. Phase 4B.5 / 4B.5b will lift bridge/ runtime coverage and typing; 4B.6 must not depend on or anticipate that work.

This is **not a new typing/coverage push**. Every threshold proposed here is anchored to a measured current value with minimal headroom.

## Non-Goals

- No new mypy fixes outside the existing 4-file public API surface.
- No interrogate ratcheting beyond the current measured value.
- No bridge/ coverage improvements (that is Phase 4B.5).
- No new tests.
- No refactors.
- No threshold "ambition" — pure ratchet from baseline.

## Background and Measured Baseline

All numbers below come from `docs/reports/v0.4-baseline/` (Phase 4A, commit `993f31b`) and re-verified in this session against current HEAD `da5a923`:

### mypy --strict on 4 public API files
| File | Phase 4A errors | Current (post-4B.4) | Phase 4B.6 gate |
|---|---|---|---|
| `src/groundtruth_kb/db.py` | 39 | **0** | enforce 0 |
| `src/groundtruth_kb/cli.py` | 4 (drifted to 6 by GO time) | **0** | enforce 0 |
| `src/groundtruth_kb/config.py` | 3 | **0** | enforce 0 |
| `src/groundtruth_kb/gates.py` | 0 | **0** | enforce 0 |

Verified live via `python -m mypy --strict src/groundtruth_kb/db.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/gates.py` → `Success: no issues found in 4 source files`.

### Interrogate (docstring coverage)
| Scope | Current value | Existing CI gate | Phase 4B.6 gate |
|---|---|---|---|
| `src/groundtruth_kb/` (whole tree) | **51.4%** (live, this session) | `--fail-under 50` | `--fail-under 51` |

Verified live via `python -m interrogate src/groundtruth_kb/` → `RESULT: FAILED (minimum: 80.0%, actual: 51.4%)`. The "FAILED" in that message is the **interrogate default of 80**, not the CI gate (which is 50). The CI gate is currently passing at 51.4 ≥ 50.

### pytest-cov (line + branch)
| File | Phase 4A coverage | Phase 4B.6 gate |
|---|---|---|
| `src/groundtruth_kb/db.py` | 73% (1607 stmts, 418 missed) | `--cov-fail-under` per-file: **70%** |
| `src/groundtruth_kb/cli.py` | 70% (576 stmts, 147 missed) | per-file: **68%** |
| `src/groundtruth_kb/config.py` | 82% (79 stmts, 13 missed) | per-file: **80%** |
| `src/groundtruth_kb/gates.py` | 94% (74 stmts, 3 missed) | per-file: **92%** |
| TOTAL (all source) | 51% | **NOT GATED** in 4B.6 (bridge/ is 0%, would lock in junk) |

Per-file thresholds give ~2 percentage points of headroom each — enough to absorb minor refactors without false-positive CI fails, but tight enough to catch real regressions.

## Proposal

### Change 1 — Add mypy CI step to `ci.yml` `test-base` job

**Touchpoint:** `.github/workflows/ci.yml`, between the existing `Lint with ruff` step (line 45) and `Run full test suite (base state)` step (line 50).

**Diff sketch:**

```yaml
      - name: Lint with ruff
        run: |
          ruff check .
          ruff format --check .

      - name: mypy --strict on public API surface
        run: |
          python -m mypy --strict \
            src/groundtruth_kb/db.py \
            src/groundtruth_kb/config.py \
            src/groundtruth_kb/cli.py \
            src/groundtruth_kb/gates.py

      - name: Run full test suite (base state)
        run: pytest -v --tb=short
```

**Rationale:**
- Adds mypy gate to ALL 3 Python versions in the matrix (3.11, 3.12, 3.13), not just one. mypy 1.20.1 is pinned in `[dev]` extra (Phase 4B.4) so it installs cleanly via the existing `pip install -e ".[dev,web]"` step.
- Runs BEFORE pytest so a type regression fast-fails before the slower 638-test suite.
- Does NOT add mypy to `test-search` or `test-cross-platform` — those are about install state and platform behavior, not type cleanliness, which is OS-independent.
- Mirrors the file list from `tests/test_public_api_type_checks.py:21` exactly so the regression guard test and the CI step cannot drift.

**Risk:** Per-Python-version mypy results can sometimes drift on stub availability (e.g., `typing_extensions`). Mitigation: 4B.4 already validated mypy 1.20.1 + Python 3.13 in the regression-guard test that ran in CI as part of pytest, so all three matrix Python versions are known-clean at HEAD.

### Change 2 — Ratchet `docstring-coverage.yml` from 50 → 51

**Touchpoint:** `.github/workflows/docstring-coverage.yml` line 29.

**Diff:**

```diff
-      - uses: actions/checkout@v4
+      - uses: actions/checkout@v6
       ...
-      - name: Set up Python
-        uses: actions/setup-python@v5
+      - name: Set up Python
+        uses: actions/setup-python@v6
       ...
-          interrogate src/groundtruth_kb/ --fail-under 50 -vv
+          interrogate src/groundtruth_kb/ --fail-under 51 -vv
```

**Rationale:**
- Closes the housekeeping drift left over from `gtkb-phase4b-housekeeping` (which bumped 8 other workflows to checkout@v6 but missed this one).
- Ratchets the threshold from 50 → 51, exactly 0.4pp below the current 51.4% measured value. Any docstring removal that drops below 51% will now fail CI.
- Does NOT attempt 51.4 — interrogate's `--fail-under` accepts an integer in the version pinned in `[dev]` (1.7+), and even if decimals were supported, platform/Python version drift can cause +/- 0.5pp variance in the count, which would create a flaky gate.

**Risk:** Linux/Python 3.11 in the docstring-coverage workflow may report a different actual percentage than my Windows/Python 3.14 local run. Mitigation: the proposal asks Codex to re-measure on Ubuntu 3.11 before merge to confirm 51% is below the live CI value. If CI reports < 51%, drop the gate to 50 and add a Phase 4B.6.1 sub-round to investigate the drift.

### Change 3 — Add per-file coverage gates to existing `pytest` step in `test-base`

**Touchpoint:** `.github/workflows/ci.yml` line 51.

**Diff sketch:**

```diff
       - name: Run full test suite (base state)
-        run: pytest -v --tb=short
+        run: |
+          pytest -v --tb=short \
+            --cov=groundtruth_kb \
+            --cov-branch \
+            --cov-report=term-missing \
+            --cov-fail-under=0
+          # Per-file gate (post-run check, mypy-style)
+          python scripts/check_per_file_coverage.py \
+            --threshold src/groundtruth_kb/db.py:70 \
+            --threshold src/groundtruth_kb/cli.py:68 \
+            --threshold src/groundtruth_kb/config.py:80 \
+            --threshold src/groundtruth_kb/gates.py:92
```

**Companion file:** new `scripts/check_per_file_coverage.py` (~50 lines). Reads `.coverage` SQLite database (or `coverage.xml` if more portable), extracts per-file line+branch coverage for the 4 named files, fails with non-zero exit and a clear diff message if any file is below its threshold.

**Why per-file instead of global `--cov-fail-under=51`:**
- Global gate locks in junk: 51% TOTAL is mostly anchored by the 6 bridge/ modules at literal 0%. Setting `--cov-fail-under=51` would mean any improvement to bridge/ would require simultaneous degradation of the public API to maintain the average. Backwards.
- Per-file gates on the 4 files we just secured are the minimal-risk lock-in.
- The 2pp headroom on each file absorbs refactor noise.

**Risk:** A new script is a new surface to maintain. Mitigation: it should be ~50 lines, pure stdlib (sqlite3 + argparse), with one unit test. Codex should review the script as part of this proposal.

**Reviewer questions for Codex:**
1. Is there an off-the-shelf tool (`coverage report --fail-under` per-file, or `diff-cover`, or a pytest-cov plugin) that does per-file thresholds without us writing a script? If yes, prefer that and skip the script.
2. Should `--cov-fail-under=0` be omitted entirely and let the per-file script be the only gate? `--cov-fail-under=0` is a no-op but adds noise.
3. Is `coverage.xml` more portable for the script than `.coverage` SQLite? CI runs on ubuntu-latest and the script needs to work there.

### Change 4 (out of scope, mention only) — Sonarcloud + CodeQL

`.github/workflows/sonarcloud.yml` and `codeql.yml` already exist and are independently configured. Phase 4B.6 does not touch them.

## Implementation Sequence

1. **Codex GO** on this proposal.
2. Bump `docstring-coverage.yml` (Change 2) — smallest, lowest risk. One commit.
3. Add mypy step to `ci.yml` (Change 1). One commit.
4. Write `scripts/check_per_file_coverage.py` + add a unit test for it. One commit.
5. Add coverage step to `ci.yml` (Change 3). One commit.
6. Push all 4 commits, verify GitHub Actions green on the resulting PR/develop push.
7. Post-implementation report as `gtkb-phase4b6-ci-enforcement-gates-002.md` (NEW for Codex VERIFY).

Estimated touch points: 4 commits, 4 files changed (2 workflows + 1 script + 1 script test), ~80 lines added net.

## Test Plan

- `python -m mypy --strict src/groundtruth_kb/db.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/gates.py` → `Success: no issues found in 4 source files`
- `python -m interrogate src/groundtruth_kb/ --fail-under 51` → exit 0
- `python -m pytest tests/test_public_api_type_checks.py -v` → 1 passed
- `python -m pytest -q` → 638 passed (no regressions)
- New unit test: `python -m pytest tests/test_per_file_coverage_check.py -v` → passes
- `python scripts/check_per_file_coverage.py --threshold src/groundtruth_kb/db.py:70 ...` (with current `.coverage`) → exit 0
- Local sanity: temporarily lower one file's threshold above current actual → script exits non-zero with clear message
- GitHub Actions: full CI workflow green on push

## Rollback

Each change is one commit. To roll back:
- Change 2: revert the `docstring-coverage.yml` commit
- Change 1: revert the `ci.yml` mypy step commit
- Change 3 & companion script: revert the two ci.yml + script commits

No data loss, no irreversible state. CI gates can be relaxed via PR if a true-positive fail blocks unrelated work.

## Verification Conditions (for post-implementation review)

1. All four CI workflows on the resulting commit are green: `CI`, `Docstring Coverage`, `Security Scan`, `SonarCloud`.
2. `git diff --stat 8151ed2..HEAD` shows the 4B.6 commits limited to the declared touchpoints (`.github/workflows/ci.yml`, `.github/workflows/docstring-coverage.yml`, `scripts/check_per_file_coverage.py`, `tests/test_per_file_coverage_check.py`).
3. `python -m mypy --strict` on the 4 public API files still returns `Success: no issues found in 4 source files`.
4. Local interrogate run reports >= 51% on the configured scope.
5. Local pytest --cov run reports each of the 4 public API files at or above its per-file threshold.
6. The post-impl report shows a deliberately-failing local script run to prove the gate is wired up correctly.

## Decision Needed From Owner

**None.** Proposal is GO/NO-GO at Codex's discretion under standing Phase 4 pre-approval. If Codex flags any threshold value as unsafe, I will revise without owner escalation.

The only escalation trigger would be if Codex objects to the new `scripts/check_per_file_coverage.py` file and recommends a tooling change instead — that would be a design conversation worth a quick owner sanity check before committing to a new script.
