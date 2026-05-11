NEW

# Post-Implementation Report — Tests Package Collision Resolution

**Document:** `gtkb-tests-package-collision-resolution`
**Status:** `NEW` (post-implementation report awaiting Codex VERIFIED)
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_report
**Recommended commit type:** `refactor:` (directory rename + path-string updates; preserves git history via `git mv`; no behavior change for working tests)
**Predecessor:** `-004` GO (Codex Loyal Opposition, 2026-05-11)
**Implementation commit on develop:** `<HEAD>` of this commit

## Specification Links

Carried forward from `-003`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state; this `-005` is filed as `NEW` and a corresponding line is inserted at top of the thread's INDEX entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal/report must cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires Specification-Derived Verification with spec-to-test mapping; this report provides the mapping in § Spec-to-Test Mapping.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — applications/<name>/ placement convention. Implementation preserves the convention: the platform's tests live at `<platform-root>/platform_tests/` (renamed name); the application's tests live at `applications/Agent_Red/tests/` (unchanged).
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE) — migration-window waiver. This rename is a follow-up to closed-VERIFIED 18.E.1, in-scope under the waiver.
- `DCL-APP-ROOT-MINIMIZATION-001` — minimization principle.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `bridge/gtkb-tests-package-collision-resolution-001.md` — initial NEW proposal.
- `bridge/gtkb-tests-package-collision-resolution-002.md` — Codex NO-GO (F1 standing-backlog evidence gap).
- `bridge/gtkb-tests-package-collision-resolution-003.md` — REVISED-1 proposal (Path 1 disposition of F1).
- `bridge/gtkb-tests-package-collision-resolution-004.md` — Codex GO authorizing implementation.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md` — 18.E.1 post-impl NEW that surfaced the collision regression.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-019.md` — 18.E.1 REVISED-1 post-impl filing this follow-up bridge.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-020.md` — 18.E.1 VERIFIED (closed).
- `.claude/rules/project-root-boundary.md` — 5 binding rules; implementation satisfies (all moves stay within `E:\GT-KB`).
- `.claude/rules/operating-model.md` §1 and §2.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol gates.
- `.claude/rules/codex-review-gate.md` — review obligations.
- `.claude/rules/canonical-terminology.md` — terminology.
- `.claude/rules/deliberation-protocol.md` — deliberation-search obligation; satisfied by § Prior Deliberations below.

## Prior Deliberations

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority for nesting Agent Red.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — active migration-window waiver covering this rename.
- `DELIB-0838` — owner standing-backlog governance authority. Bridge thread visibility per `GOV-FILE-BRIDGE-AUTHORITY-001` is the durable record path for this rename; no standing-backlog mutation.
- 18.E.1 chain that produced the regression this rename resolves: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-{017,018,019,020}.md`.
- This thread's chain: `-001` NEW, `-002` NO-GO (F1), `-003` REVISED-1, `-004` GO.
- **Owner AskUserQuestion 2026-05-11 #2 (S340)** — Selected "Commit with regression, file follow-up bridge (Recommended)". This implementation report fulfills the second-tier authorization (this thread is the follow-up bridge; this `-005` report is its post-impl filing).

## Owner Decisions / Input

Carried forward from `-003`. The AUQ #2 owner-decision evidence is durably anchored at:
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md` § Owner Decisions / Input.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-019.md` § Owner Decisions / Input.

No new owner decisions required for this report. Codex's `-004` GO line 16 explicitly stated "Prime Builder may proceed with the scoped package-collision fix" — no owner authorization needed within the GO'd scope.

## Implementation Summary

Steps A-E of proposal `-003` (REVISED-1) implemented on develop in this commit. Total file changes:

- **116 staged renames** (R): all tracked files at `<root>/tests/` → `<root>/platform_tests/` via single recursive `git mv`. Live count corrected per Codex `-004` N1 (proposal carry-forward had stale 113 from `-001`; live tracked count is 116).
- **6 modifications** (M): `.github/workflows/groundtruth-kb-tests.yml`, `.github/workflows/lint.yml`, `.github/workflows/python-tests.yml`, `.github/workflows/release-candidate-gate.yml`, `.github/workflows/security-scan.yml`, `.github/workflows/sonarcloud.yml` (20 line edits total via the forward executor).
- **1 modification**: `pyproject.toml` `[tool.pytest.ini_options].testpaths` updated from `["tests", "applications/Agent_Red/tests"]` → `["platform_tests", "applications/Agent_Red/tests"]`.
- **2 new files** (A): `scripts/run_platform_tests_rename.py` (forward executor, ~95 lines), `platform_tests/governance/test_platform_tests_rename.py` (T-rename-1..T-rename-5, ~155 lines).
- **1 new file** (A): `bridge/gtkb-tests-package-collision-resolution-005.md` (this report).
- **bridge/INDEX.md** updated with `NEW: bridge/gtkb-tests-package-collision-resolution-005.md` line.

## Exact Commands Run

### Step A — Pre-rename probe + baseline

```text
$ git ls-files tests | wc -l
116

$ git ls-files tests > .tmp/platform-tests-rename-source-list.txt

$ python -m pytest tests/governance/ -q
16 passed in 1.96s
```

Live tracked file count: **116** (corrects proposal `-003`'s carry-forward stale count of 113; Codex N1 acknowledged).

### Step B — Atomic `git mv`

```text
$ git mv tests platform_tests
```

Result: 116 staged renames; `<root>/tests/` removed; `<root>/platform_tests/` exists with all 116 files preserved.

### Step C — pyproject.toml + workflow rewrites

```text
$ python scripts/run_platform_tests_rename.py --apply
Total line edits: 20
```

Per-file edit summary:
- `groundtruth-kb-tests.yml`: 1 edit
- `lint.yml`: 5 edits
- `python-tests.yml`: 9 edits (including line 116 `--ignore=tests/integration_real_services.py` → `--ignore=platform_tests/integration_real_services.py`; pre-existing stale ref where the file does not exist at any path; rewriter follows the rule)
- `release-candidate-gate.yml`: 2 edits (correctly preserved `groundtruth-kb/tests/**` references via negative lookbehind for the `groundtruth-kb/` prefix)
- `security-scan.yml`: 2 edits
- `sonarcloud.yml`: 1 edit

pyproject.toml edited in-place (single line in `[tool.pytest.ini_options]`).

### Step D — Verification

```text
$ python -m pytest platform_tests/governance/ -q
16 passed in 1.11s

$ python -m pytest --collect-only applications/Agent_Red/tests/multi_tenant/ -q
5983 tests collected in 5.44s
(no errors)

$ python -m pytest --collect-only --json-report \
    --json-report-file=.tmp/platform-tests-rename-result.json -q
12329 tests collected, 4 errors in 212.60s

$ python -m pytest platform_tests/governance/test_platform_tests_rename.py -v
5 passed in 0.22s
```

Full governance suite at new path:

```text
$ python -m pytest platform_tests/governance/ -q
21 passed in 0.85s
```

(16 original governance tests + 5 new T-rename tests = 21 total.)

## Spec-to-Test Mapping

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Test ID | Verifies | Linked spec | Pytest function | File |
|---|---|---|---|---|
| **T-rename-1** | Governance tests pass at new path | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_t_rename_1_governance_tests_pass_at_new_path` | `platform_tests/governance/test_platform_tests_rename.py` |
| **T-rename-2** | Collect-only error count drops; zero collision-class errors remain | Same | `test_t_rename_2_full_collect_error_count_dropped` | Same |
| **T-rename-3** | `<root>/tests/` removed; `<root>/platform_tests/` exists with all 116 files | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `test_t_rename_3_directory_state` | Same |
| **T-rename-4** | pyproject.toml testpaths references `platform_tests` not bare `tests` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (implementation-faithfulness) | `test_t_rename_4_pyproject_testpaths` | Same |
| **T-rename-5** | No remaining workflow YAML refs to old `tests/<staying-subdir>` paths | Same | `test_t_rename_5_no_remaining_workflow_refs` | Same |

All 5 T-rename tests pass live (`5 passed in 0.22s`).

## Acceptance Criteria Status

Against the 10 criteria from `-003`:

| Criterion | Status |
|---|---|
| 1. `<root>/tests/` directory does not exist on disk | **PASS** (T-rename-3 asserts) |
| 2. `<root>/platform_tests/` exists with all 116 previously-tracked files preserved | **PASS** (T-rename-3 asserts; live count 116 corrects proposal's stale 113 per Codex N1) |
| 3. `pyproject.toml` testpaths references `["platform_tests", "applications/Agent_Red/tests"]` | **PASS** (T-rename-4 asserts) |
| 4. All 16 governance tests pass at `platform_tests/governance/` | **PASS** (live: `16 passed in 1.11s`) |
| 5. Full project collect-only error count is ≤3 | **DEVIATED** — landed at 4. The 14 collision-class errors all resolved; the remaining 4 are: `evaluation.deepeval_config` + `evaluation.pilots` + `scheduler` (3 predicted-pre-existing) + `test_host` (4th-class structural defect not anticipated as collision-class). See § Known Drift Surfaces. |
| 6. No remaining workflow YAML references to `tests/<staying-subdir>` | **PASS** (T-rename-5 asserts) |
| 7. Single atomic commit on develop | **PASS** (this commit) |
| 8. Forward executor script `scripts/run_platform_tests_rename.py` checked in | **PASS** |
| 9. Post-implementation report filed with spec-to-test mapping and observed results | **PASS** (this report) |
| 10. Tests T-rename-1 through T-rename-5 implemented and all-passing | **PASS** (5/5 pass live in 0.22s) |

**9/10 criteria PASS; 1 DEVIATED (criterion 5, off by 1; documented below).**

## Known Drift Surfaces (Out-of-Scope; Tracked)

### 4th post-rename collect error: `test_host` structural defect

The `test_host` collect-only error (`ModuleNotFoundError: No module named 'test_host'` at `platform_tests/test_host/test_build_contract.py`) was NOT anticipated by the proposal as a collision-class error. Investigation:

- The test imports `from test_host.suites import ...` which expects a top-level `test_host` Python package on sys.path.
- `test_host/suites.py` does NOT exist anywhere at project root or platform_tests root; the only `suites.py` is at `.claude/worktrees/elegant-brattain/test_host/suites.py` (worktree archive).
- Pre-rename, this same import failure manifested as `tests.test_host.suites` ModuleNotFoundError (per Codex `-018` review of 18.E.1's post-impl). The rename converted the import-path namespace but did not provide the missing `suites.py` module.
- **Conclusion:** pre-existing structural defect predating both 18.E.1 and this rename. The test has been broken since `suites.py` was removed/never-committed. Not a regression caused by this slice.

**Follow-up:** a future bridge thread can either remove `platform_tests/test_host/test_build_contract.py`, restore `suites.py`, or refactor the test to not depend on `test_host.suites`. Out of scope here.

### Rule-file documentation references to old `tests/` paths

Four `.claude/rules/*.md` files contain documentation references to old `tests/scripts/test_*.py` paths:

- `.claude/rules/acting-prime-builder.md:120`
- `.claude/rules/bridge-essential.md:230`
- `.claude/rules/canonical-terminology.md:957`
- `.claude/rules/project-root-boundary.md:56`

Updating these would require formal-artifact-approval packets per the narrative-artifact-approval-gate hook (protected paths). Out-of-scope for this rename; cosmetic-only (documentation refers to files that now live at `platform_tests/scripts/test_*.py`). Tracked for a separate maintenance bridge.

### Pre-existing non-collision collect-only errors

3 errors remain that were also present pre-18.E.1:
- `applications/Agent_Red/tests/evaluation/test_deepeval_scaffold.py` — `ModuleNotFoundError: No module named 'evaluation'`
- `applications/Agent_Red/tests/evaluation/test_quality_pilot.py` — same
- `applications/Agent_Red/tests/ops/test_hooks_specs.py` — `ModuleNotFoundError: No module named 'scheduler'`

Root cause: the `evaluation/` and `scheduler/` modules are not on sys.path. They live (or lived) inside the migrated `applications/Agent_Red/src/` subtree but are referenced via bare top-level imports. Fixing would require adding `applications/Agent_Red/src` to pyproject pythonpath OR restructuring the imports. Out of scope per proposal § Out of Scope and § R6.

### Pre-existing stale workflow ref

`.github/workflows/python-tests.yml:116` has `--ignore=tests/integration_real_services.py`. The file does not exist at any path (was probably removed/renamed long before 18.E.1). The rewriter applied the rule (`tests/` → `platform_tests/`), but the resulting `--ignore=platform_tests/integration_real_services.py` is equally stale. Pytest's `--ignore` on a non-existent path is a no-op; harmless drift.

## Risks Status

| Risk (from `-003`) | Realized? | Disposition |
|---|---|---|
| R1 — Missed workflow ref to `tests/<staying-subdir>` | No | T-rename-5 asserts no remaining refs across all 12 workflow files. |
| R2 — Code outside tests/ references `tests/` as file path | No | grep across `scripts/` and `groundtruth-kb/` returned no matches. |
| R3 — Documentation/rule files reference `tests/` path | **PARTIAL** | 4 `.claude/rules/*.md` refs exist; not updated in this commit due to narrative-artifact-approval-gate scope; tracked in Drift Surfaces above. |
| R4 — `git mv` cross-volume issue on Windows | No | Same-volume rename; clean execution. |
| R5 — Rename detection threshold | No | 116/116 staged as renames (R status); history preserved. |
| R6 — Inadvertently break the 3 pre-existing non-collision errors | No | The 3 (`evaluation.*`, `scheduler`) remain unchanged in error class. |

## Files Changed (diff/stat)

`127 files changed, ~700 insertions(+), ~700 deletions(-)` (renames balance insertion/deletion counts; net new content is bridge artifacts + tests + executor + 20 line edits).

- 116 renames (R)
- 7 modifications (M): 6 workflows + pyproject.toml
- 4 new files (A): `scripts/run_platform_tests_rename.py`, `platform_tests/governance/test_platform_tests_rename.py`, `bridge/gtkb-tests-package-collision-resolution-005.md`, `bridge/INDEX.md` (modification, not new)

## Codex Review Notes

Codex's `-004` non-blocking N1 acknowledged. The post-impl report uses the live count of 116 (not the stale 113 carry-forward). The pre-rename source list is preserved at `.tmp/platform-tests-rename-source-list.txt` (116 entries) for any reviewer-side count verification.

## Result

`NEW` — awaiting Codex VERIFIED review.

Codex review obligations per `.claude/rules/codex-review-gate.md`:

1. Confirm proposal's linked specs carry forward (§ Specification Links).
2. Confirm spec-derived tests were created (§ Spec-to-Test Mapping).
3. Confirm tests were executed (§ Exact Commands Run).
4. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-tests-package-collision-resolution`.
5. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-tests-package-collision-resolution`.
6. Include both preflight sections in the VERIFIED verdict.
7. Evaluate the 1 DEVIATED criterion (criterion 5: 4 vs ≤3) — the deviation explanation is in § Known Drift Surfaces.
8. Issue `VERIFIED` or `NO-GO` accordingly.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
