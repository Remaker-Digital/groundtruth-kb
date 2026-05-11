NEW

# Implementation Proposal — Tests Package Collision Resolution (Rename `tests/` → `platform_tests/`)

**Document:** `gtkb-tests-package-collision-resolution`
**Status:** `NEW`
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `refactor:` (directory rename; preserves git history via `git mv`; no behavior change for working tests; eliminates the structural collision exposed by 18.E.1)

## Claim

18.E.1 (`bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md`) landed with a 15-error net collect-only regression (2 pre-move → 17 post-move). Root cause: two Python packages named `tests` now exist on sys.path:

- `<root>/tests/` (the 112 platform tests that did NOT migrate; uses `tests/__init__.py` restored in 18.E.1 to make pytest parent-traversal find project root).
- `applications/Agent_Red/tests/` (the 638 migrated application tests; uses `applications/Agent_Red/tests/__init__.py` for the migrated test package).

Both packages share the import name `tests`. Whichever loads first wins in `sys.modules`. Subsequent imports of `tests.<X>` succeed when `<X>` is in the cached package and fail with `ModuleNotFoundError: No module named 'tests.<X>'` otherwise. Full-project collect-only loads both, exposing the collision; 14 of the 17 post-move errors are downstream of this single root cause.

This proposal resolves the collision at the package-name layer by renaming `<root>/tests/` → `<root>/platform_tests/`. Different names → no collision → 14 collision-class errors resolved → expected post-rename collect-only error count drops to 3 (the pre-existing `evaluation.*` and `scheduler` failures that were already present pre-18.E.1).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state; this proposal is filed as `-001` NEW and a corresponding line is inserted at top of the thread's INDEX entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires Specification-Derived Verification with spec-to-test mapping.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — the platform/application placement convention. This proposal preserves the convention: the platform's tests live at `<platform-root>/platform_tests/` (new name); the application's tests live at `applications/Agent_Red/tests/` (unchanged).
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE) — migration-window waiver. This rename is a follow-up to 18.E.1, in-scope under the waiver.
- `DCL-APP-ROOT-MINIMIZATION-001` — minimization principle. Renaming `<root>/tests/` away from a name that collides with the application's tests-package supports the principle by reducing structural ambiguity at the root.
- `GOV-STANDING-BACKLOG-001` — work_list.md as governed work authority. This proposal will add itself to the standing backlog as a follow-up to 18.E.1.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md` — predecessor post-impl report documenting the regression that this proposal resolves.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-016.md` — predecessor GO verdict (REVISED-7).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-015.md` — predecessor REVISED-7 proposal.
- `.claude/rules/project-root-boundary.md` — 5 binding rules. All moves stay within `E:\GT-KB`.
- `.claude/rules/operating-model.md` §1 and §2.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol gates.
- `.claude/rules/codex-review-gate.md` — review obligations.
- `.claude/rules/canonical-terminology.md` — terminology.
- `.claude/rules/deliberation-protocol.md` — deliberation-search obligation; satisfied by § Prior Deliberations below.

## Prior Deliberations

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority. The Agent Red migration motivates this follow-up.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — active migration-window waiver covering this rename.
- 18.E.1 7-NO-GO chain at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-{002,004,006,008,010,012,014}.md` and GO at `-016.md` — none of those reviews surfaced the two-tests-packages collision; it was discovered at Step 6 verification post-implementation.
- **Owner AskUserQuestion 2026-05-11 #2 (S340)** — owner selected **Commit with regression, file follow-up bridge (Recommended)**. The pathway explicitly authorizes filing this proposal to address the structural collision.

## Owner Decisions / Input

This proposal depends on the owner AskUserQuestion answer captured at S340 (2026-05-11) which selected **Commit with regression, file follow-up bridge (Recommended)** for the post-18.E.1 regression mitigation pathway. The AUQ explicitly anticipated this proposal as the structural fix.

Owner input captured at AUQ #2:
- Authorizes filing a new bridge proposing the structural fix (this proposal).
- Authorizes the rename approach (tests/ → platform_tests/) as the recommended option's named scope.
- Does NOT yet authorize implementation — that requires Codex GO on this proposal per standard bridge protocol.

No additional owner-decision asks are required for proposal review. If the implementation reveals further drift surfaces (e.g., undiscovered cross-references), those will surface as REVISED proposals or in-implementation AUQs.

## Live State Probed

Pre-rename probe results (live commands, 2026-05-11):

```text
$ git ls-files tests/ | wc -l
113
$ ls -1 tests/
__init__.py
governance
hooks
multi_tenant
scripts
secrets
security
skills
test_host
test_loyal_opposition_file_safety_clarification.py
test_no_active_smart_poller_wording.py
transport
unit
```

Tracked file counts per staying subdir (live):
- `tests/governance`: 3 files
- `tests/hooks`: 17 files
- `tests/scripts`: 80 files
- `tests/skills`: 2 files
- `tests/secrets`: 4 files
- `tests/security`: 1 file
- `tests/multi_tenant`: 1 file
- `tests/transport`: 1 file
- `tests/unit`: 3 files
- `tests/test_host`: 1 file
- Top-level: `__init__.py` + `test_loyal_opposition_file_safety_clarification.py` + `test_no_active_smart_poller_wording.py` (3 files)

**Total: 113 tracked files in `<root>/tests/`.**

Cross-tests imports search (live):

```text
$ grep -rnE "^from tests\." tests/ --include="*.py"
(no matches)
```

**No `from tests.<X>` imports exist in staying tests.** This is the load-bearing invariant that makes the rename safe: no staying test references the old package name through `tests.<X>` qualified imports.

Workflow references to staying-test paths (need second-pass rewrite per Step C below):
- `.github/workflows/python-tests.yml` lines 8, 9, 11 (comment refs), 90, 93, 99 (test_args refs)
- `.github/workflows/sonarcloud.yml` line 42 (`tests/unit/` in pytest invocation)

Total workflow lines to rewrite: ~8-10. Dockerfile/.dockerignore have no staying-test refs (per live grep).

Collect-only baseline at HEAD (`c1021ab0`, 2026-05-11):

```text
$ python -m pytest --collect-only --json-report --json-report-file=.tmp/e1-collect-report4.json -q
10984 tests collected, 17 errors
```

Of the 17 errors, 14 are collision-class `ModuleNotFoundError: No module named 'tests.<X>'` failures; 3 are likely-pre-existing (`evaluation.deepeval_config`, `evaluation.pilots`, `scheduler`). Pre-18.E.1 baseline (captured at `.tmp/e1-baseline/pytest-collect-baseline.txt`): 11,025 tests / 2 errors.

## Implementation Plan

### Step A — Pre-rename probe and baseline capture

```text
python -m pytest tests/governance/ -q                                  # baseline 16/16 pass at HEAD
python -m pytest --collect-only --json-report \
    --json-report-file=.tmp/platform-tests-rename-baseline.json -q     # baseline 17 errors at HEAD
git ls-files tests/ > .tmp/platform-tests-rename-source-list.txt       # canonical list of files to rename
```

### Step B — Atomic `git mv`

```text
git mv tests platform_tests
```

This is a single recursive directory rename. Git auto-detects all 113 tracked files as renames (preserves history per `R` status).

### Step C — In-place edits

**pyproject.toml:**

```toml
# Before (lands as part of 18.E.1 commit c1021ab0):
testpaths = ["tests", "applications/Agent_Red/tests"]

# After:
testpaths = ["platform_tests", "applications/Agent_Red/tests"]
```

**Workflow + tooling references** — second-pass rewriter applied via `scripts/run_platform_tests_rename.py` (forward executor; mirror of 18.E.1's `run_e1_step5.py` structure, smaller scope). Targets:
- `.github/workflows/python-tests.yml`: lines 8, 9, 11 (comment refs to staying subdirs); lines 90, 93, 99 (`test_args=tests/<staying-subdir>` → `test_args=platform_tests/<staying-subdir>`).
- `.github/workflows/sonarcloud.yml`: line 42 (`tests/unit/` → `platform_tests/unit/`).
- `.github/workflows/lint.yml`: confirm no remaining `tests/` (staying) refs after 18.E.1 (the 18.E.1 rewriter rewrote `src/ tests/` invocations as `applications/Agent_Red/src/ tests/`; the `tests/` token here is the staying root, needs rewrite).
- `tests/scripts/test_dashboard_subject_selector.py` and similar staying tests that may have hardcoded `Path("tests/...")` string refs — to be inspected via grep during Step C.

Other expected edits (~5-10 lines total):
- `.claude/rules/file-bridge-protocol.md` / similar rule files: any hardcoded `tests/` path examples (rule-cited soft authority; documentation accuracy).

### Step D — Verification (Step 6 / Step 6.5 equivalents)

```text
python -m pytest platform_tests/governance/ -q                         # 16/16 must pass at new path
python -m pytest --collect-only \
    applications/Agent_Red/tests/multi_tenant/ -q                      # confirm migrated tests still collect (no regression)
python -m pytest --collect-only --json-report \
    --json-report-file=.tmp/platform-tests-rename-result.json -q       # expect 3 errors (down from 17)
```

Acceptance: collect-only error count drops from 17 to 3 (the 3 pre-existing non-collision errors).

### Step E — Single atomic commit

```text
git commit -m "refactor(tests): rename tests/ to platform_tests/ to resolve E.1 package-name collision"
```

Includes:
- 113 staged renames (`R` status; tests/* → platform_tests/*).
- pyproject.toml testpaths update.
- ~8-10 workflow + rule-file line edits.
- `scripts/run_platform_tests_rename.py` forward executor (~50 lines).
- Post-implementation report at `bridge/gtkb-tests-package-collision-resolution-002.md`.

## Tests Derived From Linked Specifications

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Test ID | Verifies | Linked spec | Implementation |
|---|---|---|---|
| **T-rename-1** | All 16 governance tests pass at the new `platform_tests/governance/` path post-rename | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `python -m pytest platform_tests/governance/ -q`; assert all-pass. |
| **T-rename-2** | Full collect-only error count drops to ≤3 (eliminates the 14 collision-class errors) | Same | Run full `pytest --collect-only` with JSON report; assert error count `<= 3` and absence of `tests.<X>` `ModuleNotFoundError` entries. |
| **T-rename-3** | `<root>/tests/` directory removed and `<root>/platform_tests/` exists with all 113 files | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `pathlib.Path("tests").exists()` returns False; `pathlib.Path("platform_tests").is_dir()` returns True; `len(list(Path("platform_tests").rglob("*"))) >= 113`. |
| **T-rename-4** | pyproject.toml testpaths references `platform_tests` not `tests` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (implementation-faithfulness) | Parse pyproject.toml; assert `["tool"]["pytest"]["ini_options"]["testpaths"]` contains `"platform_tests"` and not `"tests"` at index 0. |
| **T-rename-5** | No remaining workflow refs to `tests/<staying-subdir>` | Same | Grep all `.github/workflows/*.yml` for `tests/(governance|hooks|scripts|skills|secrets|security|multi_tenant|transport|unit|test_host)`; assert 0 matches. |

Tests T-rename-1 through T-rename-5 will be implemented as pytest functions in a new test file at `platform_tests/governance/test_platform_tests_rename.py` (or equivalent).

## Verification Commands

```text
# Pre-rename baseline
python -m pytest tests/governance/ -q
python -m pytest --collect-only --json-report --json-report-file=.tmp/platform-tests-rename-baseline.json -q

# Post-rename verification (Step D)
python -m pytest platform_tests/governance/ -q
python -m pytest --collect-only --json-report --json-report-file=.tmp/platform-tests-rename-result.json -q
python -m pytest platform_tests/governance/test_platform_tests_rename.py -v
```

## Risks and Rollback

| Risk | Mitigation |
|------|------------|
| **R1** — Missed workflow reference to `tests/<staying-subdir>` causes CI failure on next PR | Comprehensive grep at Step C; `T-rename-5` assertion catches at verification |
| **R2** — Code outside tests/ references `tests/` as a file path string (not import) | Search via `grep -rnE "Path.*tests/|tests/[a-z]" --include="*.py"` during Step C; rewrite if found |
| **R3** — Documentation/rule files reference `tests/` path | Search via grep; rewrite cosmetic refs in `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md` |
| **R4** — `git mv` cross-volume issue on Windows | Same as 18.E.1 R1 — same volume, no issue expected |
| **R5** — Rename detection threshold | Single recursive `git mv` on a directory has been demonstrated to preserve history (18.E.1 1,423 renames) |
| **R6** — Inadvertently break the 3 pre-existing non-collision errors (`evaluation.*`, `scheduler`) | They're at `applications/Agent_Red/tests/*` and unrelated to `<root>/tests/`; rename should not touch them |

**Rollback procedure:**

```text
git mv platform_tests tests                                            # reverse rename
git checkout HEAD -- pyproject.toml                                    # revert pyproject
git checkout HEAD -- .github/workflows/*.yml                           # revert workflows
rm scripts/run_platform_tests_rename.py                                # remove executor
```

Or, for a partial-failure mid-rename: `git restore --staged --worktree tests/ platform_tests/` to undo staged renames.

## Acceptance Criteria

1. `<root>/tests/` directory does not exist on disk.
2. `<root>/platform_tests/` exists with all 113 previously-tracked files preserved (verified via `git diff --stat HEAD~ HEAD | grep "rename"` showing ≥113 R entries).
3. `pyproject.toml` testpaths references `["platform_tests", "applications/Agent_Red/tests"]`.
4. All 16 governance tests pass at `platform_tests/governance/`.
5. Full project collect-only error count is ≤3 (down from 17 at HEAD).
6. No remaining workflow YAML references to `tests/<staying-subdir>` (verified by T-rename-5).
7. Single atomic commit on develop (no WIP split unless owner explicitly directs).
8. Forward executor script `scripts/run_platform_tests_rename.py` checked in alongside the rename.
9. Post-implementation report filed at `bridge/gtkb-tests-package-collision-resolution-002.md` with spec-to-test mapping and observed test results.
10. Tests T-rename-1 through T-rename-5 implemented and all-passing.

## Out of Scope

- The 3 pre-existing non-collision collect errors (`evaluation.deepeval_config`, `evaluation.pilots`, `scheduler`). These are separate concerns; a future bridge may propose adding `applications/Agent_Red/src` to pyproject pythonpath or restructuring those modules.
- `.gitignore` stale-pattern updates (lines 88, 89, 210, 345 of `.gitignore` reference old root paths). Tracked as drift in 18.E.1's `-017.md` § Drift Surfaces; separate follow-up bridge.
- `applications/Agent_Red/widget/storybook-static/` gitignore at the new path. Same separate-follow-up.
- The migrated tests at `applications/Agent_Red/tests/` remain at their current location and keep their current `tests` package name. Only the staying root tests are renamed.
- Reverting any of the 18.E.1 mutations. This proposal builds forward from `c1021ab0`, not back.

## Pre-Filing Applicability Preflight

Will rerun after this NEW file is written and INDEX is updated. Expected outcome: passes (this proposal cites the same blocking specs as 18.E.1's chain plus the file-bridge protocol set; the proposal text includes the canonical content markers — `Specification Links`, `implementation proposal`, `Specification-Derived Verification`, `spec-to-test`).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
