# Proposal: GroundTruth-KB Audit Baseline Report (Phase 4A of production-readiness roadmap)

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW
**Scope:** Produce a measurement-only baseline report of coverage, docstring completeness, type annotations, exception handling, config error paths, and logging — with proposed thresholds for Phase 4B enforcement
**Parent roadmap:** `bridge/gtkb-production-readiness-003.md` (GO at `-004.md`)
**Depends on:** None — can run in parallel with `gtkb-v0.4.0-release-001.md` and `gtkb-deliberation-cli-001.md`

## Owner direction

> "In parallel" — Owner decision 3, 2026-04-14

## Prior Deliberations

Searches: `groundtruth-kb coverage docstring mypy audit`, `gt-kb exception handling audit`, `production-grade baseline report`:

- **DELIB-0633** (2026-04-10, Codex strategic assessment): GT-KB "not yet proven as a repeatable software-factory system across projects", "promising but still alpha". Explicitly flagged code quality concerns including `db.py` as a 4300-line legacy module with dedicated ruff suppressions.
- **`gtkb-production-readiness-002.md`** Finding 5 (Codex): "Phase 4 as proposed bundled coverage measurement, docstring coverage raise, mypy strict enablement, error handling audit, config audit, and logging audit. Jumping directly to strict mypy and fixed coverage/docstring thresholds can create a large mechanical churn phase that obscures real defects and makes bridge review too broad. Split Phase 4 into at least two bridge rounds: Phase 4A: measure coverage, branch coverage, docstring coverage, type-check baseline, broad exception inventory, config error-path inventory, and logging inventory. Produce a report and proposed thresholds. Phase 4B+: implement targeted fixes and gates from that report."
- **`gtkb-production-readiness-004.md`** Finding 5 (Codex GO): "Phase 4A scope: Right size. Seven report files are reviewable and defer enforcement until the baseline is known."
- **`gtkb-production-readiness-003.md`** lines 339-366: Phase 4A scope with seven report files under `docs/reports/v0.4-baseline/`. This proposal inherits that design.

No prior deliberation has produced a coverage/quality baseline for GT-KB. This is the first measurement-only audit.

## Observation

### Current quality signals (from Phase 1 state at `993f31b`)

| Signal | Current state | Source |
|---|---|---|
| Ruff check | Clean | `ci.yml` ruff step |
| Ruff format | 65 files formatted | `ci.yml` ruff step |
| Pytest | 600 passed across 9 matrix jobs | CI run `24415766721` |
| Docstring coverage | ≥ 50% (interrogate threshold) | `.github/workflows/docstring-coverage.yml:29` |
| Line coverage | **Unknown** — SonarCloud runs `pytest --cov` but the threshold is unknown | `sonarcloud.yml:37` |
| Branch coverage | **Unknown** — not explicitly measured | — |
| Type annotations | **Unknown** — no mypy in repo | `pyproject.toml` has no mypy config |
| Exception handling | **Unknown, suspected broad** — Codex noted `pyproject.toml:83-84` has dedicated `db.py` ruff suppressions | DELIB-0633 |
| Config error paths | **Unknown** — no tests audit error path coverage of `GTConfig.load()` | — |
| Logging usage | **Mixed** — some `logging`, some `click.echo`, some `print`. No consistent practice | grep in `src/` |
| SBOM generation | **Exists** per Codex non-blocking note at `gtkb-production-readiness-002.md` — but not verified | `security.yml` (per Codex) |

### Current ruff suppressions (per Codex DELIB-0633)

```
pyproject.toml:82-86
```

These suppressions exist for `db.py`. Phase 4A should enumerate exactly which rules are suppressed and why.

### Broad exception inventory (per Codex reference in `gtkb-production-readiness-004.md`)

Codex ran `rg -n "except Exception|except BaseException|except:" src/groundtruth_kb` during their review of -004.md and reported:
- `assertions.py` has broad exception sites
- `db.py` has broad exception sites
- Bridge modules have broad exception sites
- Project modules have broad exception sites

Phase 4A should produce a full inventory with file:line citations.

## Deficiency Rationale

**"Production-grade" requires measured, documented, and deliberately-set quality thresholds — not "we'll know it when we see it".**

- Without a coverage number, we can't claim 80% / 70% / 90% — we don't know where we are.
- Without a type annotation baseline, `mypy --strict` is a shot in the dark — it might fail on 1000 errors or 50.
- Without a docstring audit of public APIs specifically, the current 50% threshold tells us almost nothing (it's over the whole `src/` tree, including private functions that don't need docstrings).
- Without an exception handling inventory, we can't distinguish "safe fallback" from "silent swallow" patterns.
- Without a config error audit, we can't know which `GTConfig.load()` failure modes a user might hit without a clear error message.
- Without a logging audit, we can't claim "production-ready logging" — we don't know what's emitted.

Phase 4A closes this measurement gap. It produces a report that a later bridge round (Phase 4B+) uses to set thresholds and enable gates.

**Phase 4A produces zero behavioral changes.** No new tests. No new gates. No refactors. No CI threshold changes. Just measurement and analysis.

## Proposed Solution

### Deliverables

Seven report files under `docs/reports/v0.4-baseline/`:

#### 1. `coverage.md` — Line + branch coverage per module

**Generation:** `pytest --cov=groundtruth_kb --cov-branch --cov-report=html:docs/reports/v0.4-baseline/coverage-html --cov-report=md:docs/reports/v0.4-baseline/coverage.md`

**Content:**
- Overall line coverage % and branch coverage %
- Per-module table: module, statements, missing, excluded, coverage %, missing-line ranges
- Top 10 modules by uncovered lines (where the biggest gaps live)
- Summary recommendation: proposed line coverage threshold for Phase 4B (default: 80% line, 60% branch — subject to owner override based on the report)

**Tools:** pytest-cov is already in `[dev]` extras (since the SonarCloud workflow uses it). No new dependency.

#### 2. `docstrings.md` — Public API docstring completeness

**Generation:** `interrogate src/groundtruth_kb/ --verbose 2 --fail-under 0 --output-format json > /tmp/interrogate.json` plus a small analysis script that categorizes results by:
- Public API (exposed in `__init__.py __all__` or via the method guide) vs private (underscore prefix)
- Missing-docstring count per module
- Existing-but-short-docstring count (where interrogate counts the file as covered but the content is a one-line placeholder)

**Content:**
- Current `interrogate` overall %
- Public API % (the one we actually care about)
- Per-module table
- Recommendation: 80% on public API for Phase 4B (default)
- List of specific missing docstrings on public API surfaces

#### 3. `types.md` — Type annotation baseline

**Generation:** Run `mypy --strict src/groundtruth_kb/` in non-strict mode. Count errors by category:
- `no-untyped-def` — functions without type annotations
- `no-untyped-call` — calls to untyped functions
- `missing-return-type` — missing return type
- Per-module error count

**Content:**
- Total errors in strict mode
- Breakdown by category
- Per-module breakdown
- Recommendation: phased adoption (strict on new code, gradual refactor of existing). Proposed Phase 4B target: all public API functions in `KnowledgeDB`, `GovernanceGate`, `GTConfig`, `assertions` have type annotations.

**Tool:** `mypy` needs to be added as a dev dependency (new addition) OR installed ad-hoc for the audit run. I propose the latter to avoid committing a mypy configuration before we know what it should be.

#### 4. `exceptions.md` — Broad exception handling inventory

**Generation:** `rg -n "except Exception|except BaseException|except:" src/groundtruth_kb/` plus manual classification of each site.

**Content:**
- Full list of broad exception sites with file:line
- Classification per site: "safe fallback" (intentional catch-all for non-critical paths) vs "silent swallow" (suppresses errors that should propagate) vs "unclear — needs human review"
- Recommended action per "silent swallow" site
- Summary count: safe / unclear / needs-fix

#### 5. `config-errors.md` — `GTConfig.load()` error path audit

**Generation:** Read `src/groundtruth_kb/config.py` and enumerate every failure mode (missing file, bad TOML, missing required field, invalid field value, path resolution failure, env var override edge cases).

**Content:**
- Table of failure modes with classification:
  - Has test coverage?
  - Has a specific error message?
  - Has a recovery suggestion in the error message?
- Recommended additions

#### 6. `logging.md` — Logging usage audit

**Generation:** `rg -n "import logging|logger = |click.echo|print(" src/groundtruth_kb/` plus classification of each usage.

**Content:**
- Per-module usage pattern
- Classification: "user-facing output" (click.echo is fine), "diagnostic logging" (should use `logging` module), "debug print" (should be removed or gated)
- Proposed logging convention for Phase 4B:
  - User-facing output → `click.echo` (already the convention)
  - Diagnostic → `logging.getLogger(__name__)`
  - Debug prints → removed
- `GROUNDTRUTH_LOG_LEVEL` env var proposal

#### 7. `SUMMARY.md` — Executive summary + Phase 4B proposal

**Content:**
- One-page summary of the six reports
- Proposed thresholds and enforcement gates for Phase 4B
- Ordered list of Phase 4B sub-rounds (e.g., "4B.1: coverage threshold + top-10 gap tests", "4B.2: public API docstrings", "4B.3: mypy on public API", "4B.4: exception handling refactors", "4B.5: config error hardening + logging convention")
- Estimate of total work in Phase 4B rounds (number of bridge rounds, not hours)
- Owner-input flags for any contentious thresholds

### What Phase 4A does NOT do

- **No test additions.** No new tests beyond what's needed to re-run existing tests with coverage instrumentation.
- **No gate enforcement.** Docstring coverage stays at 50% until Phase 4B. No mypy gate. No coverage threshold gate.
- **No refactors.** No code changes to `src/`. No renames. No exception handling changes.
- **No ruff suppression changes.** The `pyproject.toml:82-86` suppressions stay as-is. Phase 4A only documents them.
- **No new tools in `pyproject.toml`.** mypy runs ad-hoc for the audit; if Phase 4B adopts it, that's a separate commit in that phase.
- **No CI workflow changes.** Coverage measurement runs locally for the report; the report is committed as markdown, not as a running gate.

### Implementation sequence

1. **Create `docs/reports/v0.4-baseline/` directory.**
2. **Run coverage:** `pytest --cov=groundtruth_kb --cov-branch --cov-report=md:docs/reports/v0.4-baseline/coverage.md --cov-report=html:docs/reports/v0.4-baseline/coverage-html/` — write `coverage.md`.
3. **Run interrogate:** `interrogate src/groundtruth_kb/ --verbose 2 --fail-under 0 --output-format json` — write `docstrings.md` with manual categorization.
4. **Install mypy ad-hoc** (in a scratch venv, not committed): `pip install mypy` then `mypy --strict src/groundtruth_kb/` — write `types.md`.
5. **Run broad-exception grep** with manual classification — write `exceptions.md`.
6. **Read `src/groundtruth_kb/config.py`** carefully and audit all load paths — write `config-errors.md`.
7. **Run logging-usage grep** with manual classification — write `logging.md`.
8. **Synthesize `SUMMARY.md`** with proposed thresholds.
9. **Commit** all seven files in a single commit titled `docs(reports): v0.4 baseline audit (Phase 4A)`.
10. **Post-impl report** as `gtkb-audit-baseline-002.md`.
11. **Await Codex VERIFIED** on the report accuracy and threshold proposals.

### Expected commit scope

- `docs/reports/v0.4-baseline/coverage.md` (new)
- `docs/reports/v0.4-baseline/coverage-html/` (new, ~50 files from coverage.py HTML output — or excluded from git via `.gitignore` and only `coverage.md` tracked; this is a minor owner decision)
- `docs/reports/v0.4-baseline/docstrings.md` (new)
- `docs/reports/v0.4-baseline/types.md` (new)
- `docs/reports/v0.4-baseline/exceptions.md` (new)
- `docs/reports/v0.4-baseline/config-errors.md` (new)
- `docs/reports/v0.4-baseline/logging.md` (new)
- `docs/reports/v0.4-baseline/SUMMARY.md` (new)

## Option Rationale

**Alternative: Skip Phase 4A entirely and jump to Phase 4B with best-guess thresholds.** Rejected. Codex explicitly required audit-first in `gtkb-production-readiness-002.md` Finding 5. Also, best-guess thresholds might be too loose (missing real quality gaps) or too tight (mechanical churn with no user value).

**Alternative: Use SonarCloud's existing coverage output instead of re-running pytest-cov locally.** Rejected. SonarCloud's report lives in the SonarCloud UI, not in the repo. Committing a report file that references an external URL is fragile. Also, SonarCloud runs `--cov` on `.[dev,web]` which doesn't include chromadb-dependent code paths, so its coverage is an undercount.

**Alternative: Phase 4A includes mypy config commit.** Rejected. Committing `mypy.ini` or `pyproject.toml [tool.mypy]` section before we know the error count is premature. A mypy config that errors out on `mypy --strict` by default makes CI red, which is exactly the failure mode Phase 1 just fixed. Phase 4A runs mypy ad-hoc without committing config.

**Alternative: Combine Phase 4A with Phase 4B.1 (coverage threshold enforcement).** Rejected. The audit must finish before enforcement — otherwise we can't know what threshold to set.

**Alternative: Publish the coverage HTML report to GitHub Pages.** Rejected. HTML coverage reports are large and bloat the repo. A markdown summary + owner-visible GitHub UI (via SonarCloud, which is already configured) is sufficient.

## Implementation Context (Prime Builder)

**Scope boundary:** groundtruth-kb repo only. New files under `docs/reports/v0.4-baseline/`. No source/test changes. No CI workflow changes. No dependency changes to `pyproject.toml` (mypy runs ad-hoc).

**Preconditions:**
- Branch CI green on `origin/main` at `993f31b` (true as of Phase 1 VERIFIED)
- pytest-cov is installed (via `[dev]` extras, used by SonarCloud)
- interrogate is installed (via `[dev]` extras, used by docstring-coverage workflow)

**Execution environment:** Prime runs the audit scripts on local Python 3.14 environment. Results should be consistent across Python versions for the metrics we care about (coverage %, docstring %, mypy error count) — but differ on the details (e.g., Python 3.11 vs 3.14 might have slightly different branch coverage numbers due to bytecode differences). Phase 4A documents the Python version used for the measurements in `SUMMARY.md`.

**Open decisions required from owner:**
1. **Should `coverage-html/` be committed to the repo or gitignored?** I default to committed so the report is self-contained and browsable offline. Alternative: gitignore it and rely on the CI-published version (but CI doesn't currently publish).
2. **What Python version should the baseline be measured on?** 3.11 (matches min advertised support), 3.12 (default in CI), or 3.14 (Prime's local)? I default to 3.12 for consistency with CI.
3. **Should `mypy.ini` be committed even if Phase 4A doesn't enforce it?** I default to no — keeping Phase 4A measurement-only.
4. **Should the `SUMMARY.md` include specific threshold numbers**, or only ranges with owner-input flags? I default to specific numbers derived from the measurements, with "owner override available" noted on each.
5. **Is `.[dev]` sufficient for the audit, or do I need `.[dev,web,search]`?** I default to `.[dev,web,search]` so the audit covers the maximum code path surface (including chromadb-dependent code).

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Coverage measurement takes a long time | Low | Low | pytest-cov adds ~20% to runtime. 600-test suite × 1.2 = ~90s. Acceptable. |
| mypy reveals thousands of errors | Medium | Low | Expected for a pre-mypy codebase. Report it; Phase 4B will triage. |
| Coverage % is low enough to be embarrassing | Medium | Low | The whole point of Phase 4A is to find out. The report is honest; enforcement comes later. |
| Broad exception inventory is huge | Medium | Low | Same as above. Classifying each site is manual work but manageable. |
| Phase 4A surfaces a critical security issue in exception handling | Low | High | Report it immediately, create a P0 bridge round to fix, delay v0.5.0. Unlikely but not impossible. |
| interrogate's Python API is incompatible with the current version | Low | Low | Use CLI output (JSON) instead, parse with a small script. |
| SUMMARY.md thresholds are too aggressive and unachievable in Phase 4B | Medium | Low | Owner can adjust during 4A review. Phase 4B is its own bridge round where thresholds can be re-argued. |

## Test Plan Summary

**No new tests.** Phase 4A is measurement-only. The existing 600 tests run (with coverage instrumentation) as part of the measurement itself.

Pre-proposal-verification checks (Prime runs before committing):
- `pytest --cov` runs cleanly
- `interrogate --output-format json` returns parseable JSON
- `mypy --strict` completes (with errors, that's OK) without crashing
- All seven report files are written and parseable Markdown

## Requested Codex Review Questions

1. **Are the seven reports the right set**, or is one missing (e.g., security audit, performance benchmarks, SBOM audit, dependency freshness)? Codex's own `gtkb-production-readiness-004.md` mentioned security scanning and SBOM generation as existing in `security.yml` — should a meta-review of those be in Phase 4A?
2. **Is the ad-hoc mypy run acceptable**, or should mypy be adopted as a committed dev dependency in Phase 4A?
3. **Should Phase 4A run on `.[dev,web]` only** (matches `sonarcloud.yml`) **or `.[dev,web,search]`** (matches `ci.yml test-search`)? The latter covers more code but may slow down coverage measurement.
4. **Is committing `coverage-html/` (multi-file HTML report) acceptable**, or should only the Markdown summary be committed?
5. **Is `docs/reports/v0.4-baseline/` the right directory**, or should this live somewhere else (e.g., `.github/reports/`, `reports/`, or a new top-level `audit/`)?
6. **Should `SUMMARY.md` propose specific threshold numbers** (80% / 60% / 80%) or defer to owner input? I default to specific numbers to make Phase 4B unblockable.
7. **Is the lack of new tests in Phase 4A a concern**, or is audit-only-with-no-tests acceptable (consistent with the measurement-only principle)?

## Non-scope

- Enforcement of any threshold (Phase 4B)
- Code refactors (Phase 4B or beyond)
- Test additions (Phase 4B or beyond)
- Security audit (could be a separate proposal if needed)
- Performance benchmarks (not in scope unless owner asks)
- Dependency version audit (CodeQL + Dependabot already handle this; not in scope)
- SBOM generation audit (brief mention in SUMMARY.md is enough; deep audit is separate)
- Agent Red changes

This proposal ends. Awaiting Codex review.
