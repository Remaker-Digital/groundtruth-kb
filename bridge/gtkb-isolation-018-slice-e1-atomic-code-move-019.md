REVISED

# Post-Implementation Report (REVISED-1) — GTKB-ISOLATION-018 Sub-slice 18.E.1: Atomic Code Cluster Move

**Document:** `gtkb-isolation-018-slice-e1-atomic-code-move`
**Status:** `REVISED` (revision 1 of post-implementation report, addressing Codex NO-GO at `-018`)
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_report
**Recommended commit type:** `refactor:` (this revision adds bridge artifacts only; no source changes from `c1021ab0`)
**Predecessors:** `-017` NEW (post-impl report); `-018` NO-GO (Codex review with one finding); this revision addresses that finding.
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-018.md`. One finding addressed: FINDING-P1-001 — the owner-accepted collect-only regression depends on a follow-up bridge being filed; that follow-up bridge was not present in the live index at the time of `-018` review.

## Codex Finding Addressed

| Finding | Severity | Disposition |
|---|---|---|
| **FINDING-P1-001** — Owner-accepted collect regression has no filed follow-up bridge, so the thread cannot close yet | P1 | **Fixed.** Follow-up bridge filed at `bridge/gtkb-tests-package-collision-resolution-001.md` (NEW). `bridge/INDEX.md` updated to include the new thread entry at the top of the active list. The follow-up proposes the structural fix (`<root>/tests/` → `<root>/platform_tests/` rename) and goes through normal Codex review-implement-verify gates. The accepted regression is now represented as durable, actionable bridge work in the index. |

## Carry-Forward Statement

All sections of `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md` carry forward UNCHANGED EXCEPT:

1. The "Follow-up bridge (to be filed after this commit lands)" subsection within § Known Regression of `-017` is superseded by the "Follow-Up Bridge (Filed)" section in this revision, which directly references the now-filed `bridge/gtkb-tests-package-collision-resolution-001.md`.
2. The Codex review notes section incorporates the FINDING-P1-001 disposition table above.
3. The result line at the bottom changes from `NEW` to `REVISED` to reflect this revision's status.

Specifically carried forward unchanged:

- Specification Links (re-cited explicitly below for preflight matching)
- Prior Deliberations (carry-forward + one new entry for the `-018` NO-GO)
- Owner Decisions / Input (AUQ #1 + AUQ #2 from S340)
- Implementation Summary
- Exact Commands Run (Steps 3, 4, 5+5b, 6)
- Spec-to-Test Mapping (16 pytest functions covering 10 M-criteria + step-order tests)
- Known Regression breakdown (17 errors; 14 collision-class + 3 likely-pre-existing)
- Deviations 1-4 from proposal `-015`
- Acceptance Criteria status (1-21 PASS, 22 PASS, 23 + 24 DEVIATED)
- Risks Status (R1-R7)
- Files Changed (diff/stat from `c1021ab0`)
- Drift Surfaces Surfaced (4 follow-up items)

## Specification Links

Re-cited explicitly per `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state; this revision is filed as `-019` REVISED and a corresponding line is inserted at the top of the thread's INDEX entry above the `-018` NO-GO line.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal/report must cite all relevant specifications. This revision re-cites the full set.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires Specification-Derived Verification with spec-to-test mapping; the spec-to-test mapping in `-017` carries forward unchanged.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — applications/<name>/ placement convention; implementation in commit `c1021ab0` satisfies the convention with all 1,423 moves landing under `applications/Agent_Red/`.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority for nesting Agent Red under `applications/Agent_Red/`.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 — 5 binding rules; implementation satisfies all.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 — machine-checkable contract; implementation satisfies.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE) — migration-window waiver; this revision constrains its commit to bridge artifacts only, in-scope under the waiver.
- `DELIB-S334-OQ-E3-OPTION-A` — owner decision selecting Option A for E.3 file-level platform-test disposition.
- `DCL-APP-ROOT-MINIMIZATION-001` — minimization principle.
- `GOV-STANDING-BACKLOG-001` — work_list.md as governed work authority; the follow-up bridge filed in this revision will add itself to the backlog.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md` — canonical umbrella plan.
- `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md` — 18.E scoping proposal.
- `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-009.md` — E.3 disposition report.
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` — 18.C VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` — 18.D VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` — 18.B VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-{002,004,006,008,010,012,014}.md` — 7-NO-GO chain.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-015.md` — REVISED-7 proposal.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-016.md` — Codex GO verdict.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md` — NEW post-impl report (predecessor of this revision).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-018.md` — Codex NO-GO with FINDING-P1-001 addressed by this revision.
- `bridge/gtkb-tests-package-collision-resolution-001.md` — follow-up bridge filed in this revision (addresses FINDING-P1-001).
- `applications/Agent_Red/.gtkb-app-isolation.json` — current isolation registry.
- `.tmp/e3-disposition/manifest-v3.json` — E.3 disposition manifest (consumed by Step 0.5 write-set generator).
- `.tmp/e1-drift/write-set.json` — canonical write-set (consumed by Step 3 forward executor + rollback script + Step 5 path rewriter).
- `.tmp/e1-baseline/drift-probe-report-2026-05-10.json` — pre-implementation drift probe.
- `.claude/rules/project-root-boundary.md` — 5 binding rules; implementation satisfies (all moves stay within `E:\GT-KB`).
- `.claude/rules/operating-model.md` §1 and §2.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol gates.
- `.claude/rules/codex-review-gate.md` — review obligations.
- `.claude/rules/canonical-terminology.md` — terminology.
- `.claude/rules/deliberation-protocol.md` — deliberation-search obligation; satisfied by § Prior Deliberations below.

## Prior Deliberations

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (owner-decision authority).
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (active migration-window waiver).
- `DELIB-S334-OQ-E3-OPTION-A` (E.3 disposition).
- 18.E.1 7-NO-GO chain at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-{002,004,006,008,010,012,014}.md` and convergence at `-016` GO.
- **Owner AskUserQuestion 2026-05-11 #1 (S340)** — Selected "Add tests/__init__.py (Recommended)". Authorized scope expansion for tests/__init__.py + "." pythonpath addition.
- **Owner AskUserQuestion 2026-05-11 #2 (S340)** — Selected "Commit with regression, file follow-up bridge (Recommended)". Authorized commit-with-regression pathway and the follow-up bridge filing addressed in this revision.
- **Codex NO-GO at `-018` (2026-05-11)** — Surfaced FINDING-P1-001: follow-up bridge required but not yet filed at time of `-018` review. Addressed in this REVISED-1.

## Owner Decisions / Input

Carried forward from `-017`. No new owner decisions required. The follow-up-bridge filing addressed in this revision is a Prime Builder revision task per Codex `-018` line 132: "No new owner decision is required if Prime follows the recorded commit-with-regression-plus-follow-up-bridge path."

Substantive AUQ evidence:

1. **AskUserQuestion 2026-05-11 #1 — Regression mitigation (Step 6 collect-only errors)**
   - Question: "Step 6 surfaced a 20-error regression caused by tests/__init__.py moving to applications/Agent_Red/tests/__init__.py (breaks pytest parent-traversal for tests/scripts/* and similar staying tests). How to proceed?"
   - Selected: **Add tests/__init__.py (Recommended)**
   - Authorized scope expansion for adding `tests/__init__.py` and `"."` to pyproject pythonpath.

2. **AskUserQuestion 2026-05-11 #2 — Path forward after structural collision exposed**
   - Question: "tests/__init__.py addition shifted errors 22→17 but exposed structural collision: two `tests/` packages mutually shadowing. How to proceed?"
   - Selected: **Commit with regression, file follow-up bridge (Recommended)**
   - Authorized commit-with-regression and follow-up bridge filing.
   - **This revision completes that authorization's second half** (commit completed the first half at `c1021ab0`; follow-up bridge filed at `bridge/gtkb-tests-package-collision-resolution-001.md` and indexed completes the second).

## Follow-Up Bridge (Filed)

Per Codex `-018` recommended action and the owner's AUQ #2 authorization, the follow-up bridge is filed:

**`bridge/gtkb-tests-package-collision-resolution-001.md` (NEW)** — proposes the structural fix: rename `<root>/tests/` → `<root>/platform_tests/`. Key claims:

- Root cause of 14 of the 17 18.E.1 collect-only errors is the two-`tests`-packages collision (`<root>/tests/` and `applications/Agent_Red/tests/` share the import name `tests` on sys.path).
- Renaming `<root>/tests/` to `<root>/platform_tests/` eliminates the collision at the package-name layer.
- No `from tests.<X>` imports exist in staying tests (live grep at proposal-time confirmed; safe rename).
- 113 tracked files in `<root>/tests/` to rename via single `git mv tests platform_tests`.
- Acceptance: post-rename full collect-only drops from 17 errors to ≤3 (only the 3 pre-existing non-collision errors remain).
- Implementation plan: Step A (probe), Step B (atomic git mv), Step C (pyproject.toml + ~8-10 workflow lines), Step D (verification), Step E (atomic commit).
- 5 spec-derived tests (T-rename-1 through T-rename-5).
- 6 risks identified with mitigations.
- Specification Links section cites the same blocking spec set as 18.E.1.

The follow-up bridge goes through normal Codex review-implement-verify gates. It does NOT depend on `-019.md` being VERIFIED; the two threads run in parallel.

`bridge/INDEX.md` updated in this revision to include the new thread entry at the top of the active list:

```text
Document: gtkb-tests-package-collision-resolution
NEW: bridge/gtkb-tests-package-collision-resolution-001.md
```

## Implementation Summary (Unchanged from `-017`)

Steps 3-7 of proposal `-015` (REVISED-7) implemented on develop at commit `c1021ab0` (1,442 files changed; 800 insertions; 151 deletions; 1,423 staged renames + 19 modifications/additions). Combined with predecessor commit `58ac3ef5` (Steps 0-2 + platform files), the slice exercises proposal `-015`'s 24 acceptance criteria.

## Exact Commands Run (Unchanged from `-017`)

Step 3, 4, 5+5b, 6 commands and observed results carry forward unchanged from `-017` §"Exact Commands Run". Highlights:

- Step 3: `python scripts/run_e1_step3.py` → `Step 3 complete: 643 moves succeeded, 0 failures.`
- Step 4: pyproject.toml in-place edits per `-015` Step 4 list, with owner-approved tests/__init__.py + "." pythonpath additions.
- Step 5+5b: `python scripts/run_e1_step5.py --apply` → `Total line edits: 146` across 12 workflows + 5 Dockerfile-class files.
- Step 6 (governance): `python -m pytest tests/governance/ -q` → `16 passed in 1.18s`. **Acceptance criterion satisfied.**
- Step 6.5 (import resolution): `python -m pytest --collect-only applications/Agent_Red/tests/multi_tenant/ -q` → `5983 tests collected in 11.10s, 0 errors`. **Acceptance criterion satisfied.**
- Full collect: `10984 tests collected, 17 errors in 228.82s`. Regression noted; follow-up bridge filed.

## Spec-to-Test Mapping (Unchanged from `-017`)

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. The 16 pytest functions in `tests/governance/test_isolation_018_e1_rollback_completeness.py` and `tests/governance/test_isolation_018_e1_step_order.py` cover the 10 M-criteria (M1-M10) plus the 5 step-order tests from proposal `-015`. Full mapping table in `-017` §"Spec-to-Test Mapping" carries forward.

## Known Regression (Unchanged from `-017`)

Full project pytest collect: 10,984 tests, 17 errors (pre-move baseline 2 errors). Root cause: two-`tests`-packages collision. 14 of 17 errors are collision-class `ModuleNotFoundError: No module named 'tests.<X>'`; 3 are likely-pre-existing (`evaluation.deepeval_config`, `evaluation.pilots`, `scheduler`). Owner-approved via AUQ #2.

## Codex Review Notes (REVISED)

Carried forward from `-017` § "Codex Review Notes":

1. ✓ `scripts/rollback_e1_write_set.py:151` calls `validate_agent_red_destination` before both `unlink()` and `rmtree()`.
2. ✓ `tests/governance/test_isolation_018_e1_rollback_completeness.py` includes M5-M10 positive/negative coverage.
3. ✓ `.tmp/e1-drift/write-set.json` is the single shared source.
4. ✓ Implementation report carries forward Specification Links, spec-to-test mapping, exact commands, observed results, diff/stat, and recommended commit type.

Added in this revision:

5. ✓ Codex's `-018` FINDING-P1-001 addressed: the follow-up bridge `bridge/gtkb-tests-package-collision-resolution-001.md` is filed and visible in `bridge/INDEX.md` at the top of the active list as `Document: gtkb-tests-package-collision-resolution / NEW: bridge/gtkb-tests-package-collision-resolution-001.md`. The accepted regression is now durably represented as actionable bridge work.

## Deviations From Proposal `-015` (Unchanged from `-017`)

1. **WIP commit split** — ONE atomic commit → TWO due to S339 session-handoff.
2. **`tests/__init__.py` scope expansion** — owner-approved per AUQ #1.
3. **`"."` added to pyproject pythonpath** — owner-approved per AUQ #1 implicit / AUQ #2 ratification.
4. **17 collect-only errors** vs proposal's no-new-regression criterion — owner-approved per AUQ #2 + this revision files the required follow-up bridge.

## Acceptance Criteria Status (Updated)

23 criteria from `-013` carry forward + criterion 22 replacement from `-015`. Status updates:

| Criterion | Status (after `-019`) |
|---|---|
| 1-21 (carry-forward) | **PASS** (16/16 governance tests pass) |
| 22 (REPLACEMENT from `-015`) — Single write-set + T-write-set-1 M1-M10 | **PASS** |
| 23 (single atomic commit) | **DEVIATED** (split into 2 commits at S339 session-handoff; owner-approved) |
| 24 (no collect-only regression vs baseline) | **DEVIATED** (15-error net regression; owner-approved per AUQ #2; **follow-up bridge filed in this revision** completing the AUQ-approved pathway) |

## Risks Status (Unchanged from `-017`)

R1-R6 NOT REALIZED (cluster moves clean; rename detection clean; pyproject + workflows accepted; CI not yet exercised). R7 REALIZED (17 collect errors); mitigation: `tests/__init__.py` reduces 22→17; follow-up bridge proposes structural fix.

## Files Changed in This Revision (REVISED-1)

Only bridge artifacts; no source changes from `c1021ab0`:

- `bridge/gtkb-tests-package-collision-resolution-001.md` (new; NEW bridge proposal for the structural fix).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-019.md` (this file; REVISED post-impl report).
- `bridge/INDEX.md` (updated: new follow-up thread entry at top of active list + REVISED `-019` line on E.1 thread).

## Drift Surfaces Surfaced (Unchanged from `-017`)

4 drift items in `-017` § "Drift Surfaces Surfaced" carry forward unchanged: stale `.gitignore` patterns, storybook-static, `tests/test_host/test_build_contract.py`, and ruff per-file-ignores. The `test_host/` item may be subsumed by `gtkb-tests-package-collision-resolution` because `test_host/` will be renamed alongside the rest of `<root>/tests/`.

## Applicability Preflight

Will be run by Codex at review time per `.claude/rules/codex-review-gate.md`. Expected outcome: same as `-016`, `-017`, and `-018` (this revision cites the same blocking spec set; same content patterns; clause detectors satisfied by the explicit re-citation above).

## Result

`REVISED` — awaiting Codex VERIFIED review.

Codex review obligations per `.claude/rules/codex-review-gate.md` and per Codex's `-018` § Prime Builder Implementation Context:

1. Confirm follow-up bridge `gtkb-tests-package-collision-resolution-001.md` exists in `bridge/` and has a NEW entry in `bridge/INDEX.md`.
2. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e1-atomic-code-move` on `-019` operative file.
3. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-018-slice-e1-atomic-code-move` on `-019` operative file.
4. Verify successful evidence remains intact from `c1021ab0`: 16 governance tests pass, multi-tenant collection succeeds, placement spot-checks pass, mechanical bridge preflights pass.
5. Issue `VERIFIED` if all of the above hold and the FINDING-P1-001 remediation is durable; otherwise `NO-GO` with specific finding.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
