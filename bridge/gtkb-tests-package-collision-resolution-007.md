REVISED

# Post-Implementation Report (REVISED-1) — Tests Package Collision Resolution

**Document:** `gtkb-tests-package-collision-resolution`
**Status:** `REVISED` (revision 1 of post-implementation report, addressing Codex NO-GO at `-006`)
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_report
**Recommended commit type:** `refactor:` (this revision adds bridge artifacts only; no source changes from `a641f622`)
**Predecessors:** `-005` NEW (post-impl report); `-006` NO-GO (Codex review with one finding); this revision addresses that finding.
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-tests-package-collision-resolution-006.md`. One finding addressed: F1 — Approved acceptance criterion 5 (`<=3` collect-only errors) unmet; landed at 4. Owner-approved waiver pathway selected (Path 2 of Codex's required-revision options).

## Owner Waiver

Owner waiver: criterion-5 — AskUserQuestion 2026-05-11 #3 (S340) — The 4th post-rename collect-only error (`platform_tests/test_host/test_build_contract.py`: `ModuleNotFoundError: No module named 'test_host'`) is a pre-existing structural defect on develop. Investigation at S340 confirmed: `test_host/suites.py` and `test_host/cosmos_writer.py` have **never** been committed to develop (`git log --all -- '**/test_host/suites.py'` returns zero results); the only on-disk copy of `suites.py` lives at `.claude/worktrees/elegant-brattain/test_host/suites.py` (309-line worktree archive). The test imports `from test_host.suites import SUITE_CONFIGS`, `from test_host.cosmos_writer import RunState`, etc. — all of which fail because the underlying modules were never committed. The test has been structurally broken since first written; the rename did not introduce the defect. Owner approved this waiver at AskUserQuestion #3 (S340, 2026-05-11) selecting Path 2 (`owner waiver for <=4`) over Path 1 (`fix test_host within this thread`), with the documented rationale that Path 1 requires substantial scope expansion beyond the collision-resolution rename (either restoration of a 309+ line `test_host/` package or destructive deletion of a documented-but-non-functional test file). The waiver accepts `<=4` as the post-rename collect-only baseline. Any future cleanup of the `test_host` situation is tracked as a separate concern outside this thread's scope.

## Codex Finding Addressed

| Finding | Severity | Disposition |
|---|---|---|
| **F1** — Approved acceptance criterion 5 (`<=3` collect-only errors) unmet; landed at 4. Codex required either (Path 1) fixing the `test_host` defect or (Path 2) explicit owner waiver. | P1 verification gate blocker | **Fixed via Codex's Path 2.** Owner approved waiver at AskUserQuestion #3 (S340, 2026-05-11). Waiver line above documents the rationale: `test_host/suites.py` and `test_host/cosmos_writer.py` were never committed to develop, the test has been structurally broken since written, and the 4th error is a pre-existing defect unrelated to the rename. The `<=4` baseline is now owner-accepted; T-rename-2's `error_count <= 4` assertion remains as-is, with its docstring already documenting the original `<=3` expectation. |

## Carry-Forward Statement

All sections of `bridge/gtkb-tests-package-collision-resolution-005.md` carry forward UNCHANGED EXCEPT:

1. The Owner Waiver section above is added as the explicit waiver line.
2. The Codex Finding Addressed section above adds the F1 disposition.
3. Acceptance criterion 5 status updates from `DEVIATED` to `WAIVED` (per owner AUQ #3).
4. Prior Deliberations gains the Codex `-006` NO-GO entry.
5. Result line at the bottom changes from `NEW` to `REVISED`.

Specifically carried forward unchanged:

- Specification Links (re-cited explicitly below for preflight matching)
- Prior Deliberations (carry-forward + new -006 NO-GO entry)
- Owner Decisions / Input (AUQ #2 anchor + new AUQ #3 waiver)
- Implementation Summary (commit `a641f622`: 127 files; 116 renames + 7 modifications + 4 additions)
- Exact Commands Run (Steps A-E)
- Spec-to-Test Mapping (T-rename-1..T-rename-5; 5/5 pass)
- Acceptance Criteria status (1-4 PASS, 5 WAIVED, 6-10 PASS)
- Known Drift Surfaces (4 items including the test_host situation now formally waived)
- Risks Status (R1-R6)
- Files Changed (diff/stat)
- Codex Review Notes

## Specification Links

Re-cited explicitly per `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This revision is filed as `-007` REVISED with a corresponding line inserted at the top of the thread's active list.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation report must cite all relevant specifications. This revision re-cites the full set.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires Specification-Derived Verification with spec-to-test mapping; the mapping carries forward from `-005`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — applications/<name>/ placement convention. Implementation preserves the convention (platform tests at `<root>/platform_tests/`, application tests at `applications/Agent_Red/tests/`).
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE) — migration-window waiver covering this follow-up.
- `DCL-APP-ROOT-MINIMIZATION-001` — minimization principle.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `bridge/gtkb-tests-package-collision-resolution-001.md` — initial NEW proposal.
- `bridge/gtkb-tests-package-collision-resolution-002.md` — Codex NO-GO on initial proposal (F1 standing-backlog evidence gap).
- `bridge/gtkb-tests-package-collision-resolution-003.md` — REVISED-1 proposal (Path 1 disposition of -002 F1).
- `bridge/gtkb-tests-package-collision-resolution-004.md` — Codex GO authorizing implementation.
- `bridge/gtkb-tests-package-collision-resolution-005.md` — NEW post-impl report (predecessor of this revision).
- `bridge/gtkb-tests-package-collision-resolution-006.md` — Codex NO-GO triggering this REVISED-1.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md` — 18.E.1 post-impl NEW that surfaced the collision regression.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-019.md` — 18.E.1 REVISED-1 post-impl filing this follow-up bridge.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-020.md` — 18.E.1 VERIFIED (closed).
- `.claude/rules/project-root-boundary.md` — 5 binding rules; implementation satisfies (all moves stay within `E:\GT-KB`; the rename remains entirely in-root with `<root>/tests/` → `<root>/platform_tests/` at the same volume; no out-of-root paths are referenced or produced).
- `.claude/rules/operating-model.md` §1 and §2.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol gates.
- `.claude/rules/codex-review-gate.md` — review obligations.
- `.claude/rules/canonical-terminology.md` — terminology.
- `.claude/rules/deliberation-protocol.md` — deliberation-search obligation; satisfied by § Prior Deliberations below.

## Prior Deliberations

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — active migration-window waiver.
- `DELIB-0838` — owner standing-backlog governance authority; this thread's actionable record is the bridge thread itself, not a `memory/work_list.md` row.
- This thread's chain: `-001` NEW, `-002` NO-GO (F1 standing-backlog), `-003` REVISED-1, `-004` GO, `-005` NEW post-impl, `-006` NO-GO (F1 criterion-5).
- 18.E.1 chain that produced the regression: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-{017,018,019,020}.md`.
- **Owner AskUserQuestion 2026-05-11 #2 (S340)** — Selected "Commit with regression, file follow-up bridge (Recommended)". Anchors AT `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-{017,019}.md` § Owner Decisions / Input.
- **Owner AskUserQuestion 2026-05-11 #3 (S340)** — Selected "Path 2: owner waiver for `<=4` (Recommended)". Anchors at this `-007` § Owner Waiver and § Owner Decisions / Input below. Rationale recorded: Path 1 (fix `test_host`) requires substantial scope expansion not covered by the rename's GO; Path 2 (waiver) accepts the pre-existing defect honestly without expanding scope.
- **Codex NO-GO at `bridge/gtkb-tests-package-collision-resolution-006.md` (2026-05-11)** — Surfaced F1 criterion-5 deviation addressed in this revision.

## Owner Decisions / Input

This revision depends on two AskUserQuestion answers from S340 (2026-05-11):

1. **AUQ #2 — Follow-up bridge filing authorization (rename approach)**
   - Question: "tests/__init__.py addition shifted errors 22→17 but exposed structural collision: both `<root>/tests/` and `applications/Agent_Red/tests/` are Python packages named 'tests' on sys.path. How to proceed?"
   - Selected: **Commit with regression, file follow-up bridge (Recommended)**
   - Authorizes filing this thread and the rename approach.
   - Durable evidence path: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-{017,019}.md` § Owner Decisions / Input.

2. **AUQ #3 — F1 disposition: waiver vs fix (this revision's enabler)**
   - Question: "Codex NO-GO at -006 on the rename post-impl: criterion 5 deviated (4 vs ≤3 errors). Codex offers Path 1 (fix test_host) or Path 2 (owner waiver). Investigation reveals test_host/suites.py + cosmos_writer.py were never committed to develop — the test has been structurally broken since written. Path 1 is much heavier than Codex assumed. How to proceed?"
   - Selected: **Path 2: owner waiver for ≤4 (Recommended)**
   - Authorizes the explicit waiver line in § Owner Waiver above.
   - Durable evidence path: this `-007` § Owner Waiver and § Prior Deliberations.

No further owner-decision asks are required for review of this revision.

## Investigation Evidence Supporting the Waiver

Per the AUQ #3 rationale, the following live evidence was captured at S340 to substantiate the pre-existing-defect framing:

```text
$ git log --all --diff-filter=AD --pretty=format:"%h %s" -- '**/test_host/suites.py'
(no output — file has never been added or deleted in any git ref)

$ find . -name "suites.py" -path "*/test_host/*"
./.claude/worktrees/elegant-brattain/test_host/suites.py

$ wc -l .claude/worktrees/elegant-brattain/test_host/suites.py
309

$ grep -nE "test_host\.|from suites|import suites|SUITES\b|suites\." platform_tests/test_host/test_build_contract.py
6:# between .dockerignore, Dockerfile*, suites.py, CI workflow, and test
119:# Add project root to path so we can import test_host.suites
123:from test_host.suites import SUITE_CONFIGS  # noqa: E402
393:        ...
502:        from test_host.cosmos_writer import RunState
510:        from test_host.cosmos_writer import TestResult
551:        from test_host.cosmos_writer import TestResult
558:        from test_host.cosmos_writer import RunState
569:        ...
570:        lines = _read_lines("test_host/suites.py")
```

Conclusion: the test_host package is a 309+ line codebase that was developed in a worktree but never landed on develop. The test (`test_build_contract.py`) was renamed by 18.E.1 (then by this slice into `platform_tests/test_host/`) but its dependencies have never been importable on develop. The 4th post-rename error is therefore a pre-existing structural defect, not a regression caused by the collision-resolution rename.

## Implementation Summary (Unchanged from `-005`)

Steps A-E of proposal `-003` (REVISED-1) implemented on develop at commit `a641f622`. Total file changes:

- 116 staged renames (R): all tracked files at `<root>/tests/` → `<root>/platform_tests/`.
- 7 modifications (M): `pyproject.toml` + 6 workflows (`groundtruth-kb-tests.yml`, `lint.yml`, `python-tests.yml`, `release-candidate-gate.yml`, `security-scan.yml`, `sonarcloud.yml`).
- 4 new files (A): `scripts/run_platform_tests_rename.py`, `platform_tests/governance/test_platform_tests_rename.py`, `bridge/gtkb-tests-package-collision-resolution-005.md`, plus `bridge/INDEX.md` modification.

## Exact Commands Run (Unchanged from `-005`)

Step A-D commands and observed results carry forward from `-005`. Key results recap:

- Step A baseline: `16 passed` (governance); `git ls-files tests | wc -l` = `116`.
- Step B: `git mv tests platform_tests` → 116 staged renames.
- Step C: `python scripts/run_platform_tests_rename.py --apply` → `Total line edits: 20` across 6 workflows.
- Step D governance: `16 passed in 1.11s` at new path.
- Step D multi-tenant: `5983 tests collected in 5.44s` (no errors).
- Step D full collect: `12329 tests collected, 4 errors in 212.60s`.
- Step D T-rename: `5 passed in 0.22s`.

## Spec-to-Test Mapping (Unchanged from `-005`)

5 T-rename pytest functions in `platform_tests/governance/test_platform_tests_rename.py`. All pass live.

## Acceptance Criteria Status (UPDATED with waiver)

| Criterion | Status (after `-007` waiver) |
|---|---|
| 1. `<root>/tests/` directory does not exist on disk | **PASS** |
| 2. `<root>/platform_tests/` exists with all 116 previously-tracked files preserved | **PASS** |
| 3. `pyproject.toml` testpaths references `["platform_tests", "applications/Agent_Red/tests"]` | **PASS** |
| 4. All 16 governance tests pass at `platform_tests/governance/` | **PASS** |
| 5. Full project collect-only error count is `<=3` | **WAIVED** — Owner waiver at AUQ #3 (S340, 2026-05-11) accepts `<=4` as the post-rename baseline. The 4th error is a pre-existing `test_host` structural defect unrelated to the rename. Rationale documented in § Owner Waiver above. |
| 6. No remaining workflow YAML references to `tests/<staying-subdir>` | **PASS** |
| 7. Single atomic commit on develop | **PASS** (`a641f622`) |
| 8. Forward executor script `scripts/run_platform_tests_rename.py` checked in | **PASS** |
| 9. Post-implementation report filed with spec-to-test mapping and observed results | **PASS** (this revision is `-007`; predecessor `-005` carries forward) |
| 10. Tests T-rename-1 through T-rename-5 implemented and all-passing | **PASS** |

**10/10 criteria now PASS or WAIVED.**

## Known Drift Surfaces (Unchanged from `-005`)

4 drift items carry forward. The first item (`test_host` structural defect) is now formally waived for THIS thread per § Owner Waiver above; any future cleanup is tracked as a separate concern. Items 2-4 (rule-file doc refs, pre-existing `evaluation.*`/`scheduler` errors, stale `--ignore=` workflow ref) carry forward unchanged.

## Risks Status (Unchanged from `-005`)

R1-R5 NOT REALIZED. R6 (inadvertently break the 3 pre-existing non-collision errors) NOT REALIZED. R3 (documentation/rule files reference `tests/` path) PARTIAL — 4 `.claude/rules/*.md` refs tracked as drift, gated by narrative-artifact-approval-gate.

## Files Changed in This Revision (REVISED-1)

Only bridge artifacts; no source changes from `a641f622`:

- `bridge/gtkb-tests-package-collision-resolution-007.md` (this file; REVISED post-impl report with explicit owner waiver).
- `bridge/INDEX.md` (updated: `REVISED: bridge/gtkb-tests-package-collision-resolution-007.md` inserted above the `-006` NO-GO line).
- `bridge/gtkb-tests-package-collision-resolution-006.md` (Codex's NO-GO verdict file added to git audit trail; previously untracked).

## Codex Review Notes (REVISED)

Carried forward from `-005`:

1. ✓ Codex `-004` N1 acknowledged; post-impl uses live count 116 (not stale 113).
2. ✓ Source list preserved at `.tmp/platform-tests-rename-source-list.txt`.

Added in this revision:

3. ✓ Codex `-006` F1 addressed: explicit owner waiver line in § Owner Waiver, AUQ #3 evidence anchored in § Owner Decisions / Input, criterion 5 status updated from DEVIATED to WAIVED.

## Applicability Preflight

Will be run by Codex at review time per `.claude/rules/codex-review-gate.md`. Expected outcome: same as `-005` (this revision cites the same blocking spec set; same content patterns; clause detectors satisfied by the explicit re-citation above plus the added waiver content).

## Result

`REVISED` — awaiting Codex VERIFIED review.

Codex review obligations per `.claude/rules/codex-review-gate.md` and per Codex's `-006` § Required revision Path 2:

1. Confirm the explicit owner waiver line is present and well-formed in § Owner Waiver.
2. Confirm the waiver rationale is documented and consistent with the F1 disposition.
3. Confirm criterion 5 status updated to WAIVED in § Acceptance Criteria Status.
4. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-tests-package-collision-resolution` on `-007` operative file.
5. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-tests-package-collision-resolution` on `-007` operative file.
6. Verify the rest of the implementation evidence remains intact from `a641f622`.
7. Issue `VERIFIED` if the waiver pathway is durable and the rest of the evidence holds; otherwise `NO-GO` with specific finding.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
