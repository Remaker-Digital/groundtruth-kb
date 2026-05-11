NEW

# Post-Implementation Report — GTKB-ISOLATION-018 Sub-slice 18.E.1: Atomic Code Cluster Move

**Document:** `gtkb-isolation-018-slice-e1-atomic-code-move`
**Status:** `NEW` (post-implementation report awaiting Codex VERIFIED)
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_report
**Recommended commit type:** `refactor:` (file relocation; no behavior change; preserves git history via `git mv`)
**Predecessor:** `-016` GO (Codex Loyal Opposition, 2026-05-10)
**Implementation commits on develop:**
- `58ac3ef5 wip(isolation): E.1 Steps 0-2 + platform-files (resume at Step 3)` — Steps 0 (manifest-v3), 0.5 (write-set), 1 (precondition), 1.5 (baseline snapshot), 2 (platform files); landed at S339 prior to session-handoff.
- `<HEAD>` of this commit — Steps 3 (atomic mv), 4 (pyproject), 5 (workflows), 5b (Dockerfile-class), 6 (verification), plus owner-approved scope-expansion fixes for the discovered regression.

## Specification Links

Carried forward from `-015`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is canonical workflow state; this `-017` is filed as `NEW` and a corresponding line is inserted at top of the thread's INDEX entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cited all relevant specs; this report carries them forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires Specification-Derived Verification with spec-to-test mapping; this report provides the mapping in § Spec-to-Test Mapping.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — applications/<name>/ placement convention. Implementation satisfies: all 1,423 file moves land under `applications/Agent_Red/`.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority for nesting Agent Red under `applications/Agent_Red/`.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 — 5 binding rules; implementation satisfies all.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 — machine-checkable contract; implementation satisfies the check.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE) — migration-window waiver; this slice's commits constrain to migration scope per the waiver.
- `DELIB-S334-OQ-E3-OPTION-A` — owner decision selecting Option A for E.3 file-level platform-test disposition; this slice consumes the resulting manifest-v3.
- `DCL-APP-ROOT-MINIMIZATION-001` — minimization principle.
- `GOV-STANDING-BACKLOG-001` — work_list.md as governed work authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md` — canonical umbrella plan.
- `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md` — 18.E scoping proposal.
- `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-009.md` — E.3 disposition report.
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` — 18.C VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` — 18.D VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` — 18.B VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-002.md` through `-014.md` — 7-NO-GO chain.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-015.md` — REVISED-7.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-016.md` — Codex GO.
- `applications/Agent_Red/.gtkb-app-isolation.json` — isolation registry.
- `.tmp/e3-disposition/manifest-v3.json` — E.3 disposition manifest (42,385 bytes; consumed by Step 0.5 write-set generator).
- `.tmp/e1-drift/write-set.json` — canonical write-set (90,452 bytes; consumed by Step 3 forward executor + rollback script).
- `.tmp/e1-baseline/drift-probe-report-2026-05-10.json` — pre-implementation drift probe.
- `.claude/rules/project-root-boundary.md` — 5 binding rules; implementation satisfies (all moves stay within `E:\GT-KB`).
- `.claude/rules/operating-model.md` §1 and §2.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol gates.
- `.claude/rules/codex-review-gate.md` — review obligations.
- `.claude/rules/canonical-terminology.md` — terminology.
- `.claude/rules/deliberation-protocol.md` — deliberation-search obligation; satisfied by `-016` Prior Deliberations section.

## Prior Deliberations

Carried forward from `-015`:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (owner-decision authority).
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (active migration-window waiver).
- `DELIB-S334-OQ-E3-OPTION-A` (E.3 disposition).
- Codex 7-NO-GO chain at `-002, -004, -006, -008, -010, -012, -014` and convergence at `-016` GO.

Additional deliberations from this session (S340, 2026-05-11):

- **Owner AUQ 2026-05-11 #1** — "How to proceed with discovered 20-error regression at Step 6": Owner selected **Add tests/__init__.py (Recommended)**. Rationale: minimal scope expansion to restore pre-move pytest parent-traversal behavior. Documented as deviation from proposal's strict Step 4 list.
- **Owner AUQ 2026-05-11 #2** — "tests/__init__.py addition shifted errors 22→17 but exposed structural collision: how to proceed?": Owner selected **Commit with regression, file follow-up bridge (Recommended)**. Rationale: structural fix (two-tests-packages collision) requires architectural decision beyond this slice; commit current progress and file follow-up.

## Owner Decisions / Input

This implementation depends on owner-AUQ approvals collected during S340. Per `.claude/rules/file-bridge-protocol.md` Mandatory Owner Decisions / Input Section Gate:

1. **AskUserQuestion 2026-05-11 #1 — Regression mitigation (Step 6 collect-only errors)**
   - Question: "Step 6 surfaced a 20-error regression caused by tests/__init__.py moving to applications/Agent_Red/tests/__init__.py (breaks pytest parent-traversal for tests/scripts/* and similar staying tests). How to proceed?"
   - Selected: **Add tests/__init__.py (Recommended)**
   - Authorizes: scope expansion to add `tests/__init__.py` (1-line package marker) and `"."` to pyproject.toml pythonpath (`.` as a sibling of `applications/Agent_Red`). Both deviations from proposal `-015` Step 4's strict pyproject-only list.

2. **AskUserQuestion 2026-05-11 #2 — Path forward after structural collision exposed**
   - Question: "tests/__init__.py addition shifted errors 22→17 but exposed structural collision: both `<root>/tests/` and `applications/Agent_Red/tests/` are Python packages named 'tests' on sys.path, mutually shadowing each other. How to proceed?"
   - Selected: **Commit with regression, file follow-up bridge (Recommended)**
   - Authorizes: commit this slice with 17 documented collect-only errors (down from 22 pre-fix; pre-move baseline 2 errors) and file a follow-up bridge proposing the structural fix (tests/ → platform_tests/ rename).

## Implementation Summary

Steps 3-7 of proposal `-015` (REVISED-7) implemented on develop. Total file changes in this commit:

- **1,423 staged renames** (305 src + 361 admin + 51 widget + 67 branding + 1 config file + 638 selective tests).
- **16 modifications** (M): `.dockerignore`, 11 `.github/workflows/*.yml`, 3 `Dockerfile`-class, `docker-compose.yml`, `pyproject.toml`.
- **3 new files** (A): `scripts/run_e1_step3.py`, `scripts/run_e1_step5.py`, `tests/__init__.py`.
- **1 explicitly excluded untracked path**: `applications/Agent_Red/widget/storybook-static/` (build output; not committed; future .gitignore update pending in follow-up bridge).

Combined with predecessor commit `58ac3ef5` (Steps 0-2 + platform files), the slice as a whole exercises proposal `-015`'s 24 acceptance criteria (originally 23 carried from `-013` plus criterion 22 replacement).

## Exact Commands Run

### Step 3 (atomic git mv)

```text
python scripts/run_e1_step3.py
```

Observed: `Step 3 complete: 643 moves succeeded, 0 failures.`

### Step 4 (pyproject.toml updates)

In-place edits (no command):

- `[tool.pytest.ini_options].testpaths` extended to `["tests", "applications/Agent_Red/tests"]`.
- `[tool.pytest.ini_options].pythonpath` added as `[".", "applications/Agent_Red"]`. The `"."` entry is scope expansion beyond proposal `-015`'s `["applications/Agent_Red"]` and is owner-approved per AUQ #1.
- `[tool.coverage.run].source` rewritten to `["applications/Agent_Red/src"]`.
- `[tool.coverage.run].omit` paths rewritten under `applications/Agent_Red/src/`.
- `[tool.ruff.lint.isort].known-first-party = ["src"]` UNCHANGED per `-015` instruction.

### Step 5 + Step 5b (path-string rewrites)

```text
python scripts/run_e1_step5.py --apply
```

Observed: `Total line edits: 146` across 12 workflows + 5 Dockerfile-class files. `.github/workflows/deploy-docs.yml` and `.github/workflows/groundtruth-kb-tests.yml` legitimately required 0 edits.

The rewriter classifies `tests/<subdir>` tokens against the write-set's migration status:

- **fully_migrated** (29 subdirs): rewritten to `applications/Agent_Red/tests/<subdir>`.
- **fully_staying** (3 subdirs: hooks, scripts, skills): left unchanged.
- **split** (6 subdirs: multi_tenant, secrets, security, unit, transport, top-level test files): inline-duplicated as both paths.

### Step 6 (verification)

Governance tests baseline (pre-move):

```text
python -m pytest tests/governance/ -q
```

Observed: `16 passed in 1.03s`.

Governance tests post-move (after Steps 3-5b):

```text
python -m pytest tests/governance/ -q
```

Observed: `16 passed in 1.18s`. **Acceptance criterion satisfied** — proposal's "16 governance tests must still pass" requirement.

Step 6.5 (src.* import resolution proof):

```text
python -m pytest --collect-only applications/Agent_Red/tests/multi_tenant/ -q
```

Observed: `5983 tests collected in 11.10s` with no errors. **Acceptance criterion satisfied** — `src.*` imports resolve via pyproject pythonpath; migrated tests collect cleanly.

Full project collect:

```text
python -m pytest --collect-only --json-report --json-report-file=.tmp/e1-collect-report4.json -q
```

Observed: `10984 tests collected, 17 errors in 228.82s`. **Regression — pre-move baseline was 11,025 tests / 2 errors.** Net change: 41 fewer tests collected, 15 more errors. Root cause + breakdown in § Known Regression.

## Spec-to-Test Mapping

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Spec | Test (pytest function) | File | Verified at |
|---|---|---|---|
| Phase 0 manifest-v3 ordering | `test_step0_produces_manifest_v3_before_step05_reads_it` | `tests/governance/test_isolation_018_e1_step_order.py` | Post-Step 6 pytest |
| Phase 0.5 write-set ordering | `test_step05_produces_write_set_before_step1_reads_it` | same | same |
| Canonical artifacts exist | `test_canonical_artifacts_exist_in_repo` | same | same |
| Manifest-v3 schema | `test_manifest_v3_schema_is_complete` | same | same |
| Write-set schema | `test_write_set_schema_is_complete` | same | same |
| T-write-set-1.M1 — Write-set consumed by rollback | `test_m1_write_set_consumed_by_rollback` | `tests/governance/test_isolation_018_e1_rollback_completeness.py` | same |
| T-write-set-1.M2 — Schema required keys | `test_m2_write_set_schema_has_required_keys` | same | same |
| T-write-set-1.M3 — Source/destination symmetry | `test_m3_source_destination_symmetry_for_per_file_tests` | same | same |
| T-write-set-1.M4 — End-to-end rollback completeness | `test_m4_end_to_end_rollback_completeness` | same | same |
| T-write-set-1.M5 — Outside file rejected | `test_m5_outside_file_destination_rejected_before_unlink` | same | same |
| T-write-set-1.M6 — Outside dir rejected | `test_m6_outside_directory_destination_rejected_before_rmtree` | same | same |
| T-write-set-1.M7 — Valid in-scope file accepted | `test_m7_valid_inscope_file_destination_accepted` | same | same |
| T-write-set-1.M8 — Valid in-scope dir accepted | `test_m8_valid_inscope_directory_destination_accepted` | same | same |
| T-write-set-1.M9 — Parent traversal rejected | `test_m9_parent_traversal_rejected` | same | same |
| T-write-set-1.M10a — POSIX absolute rejected | `test_m10a_posix_absolute_path_rejected` | same | same |
| T-write-set-1.M10b — Windows absolute rejected | `test_m10b_windows_absolute_path_rejected` | same | same |

All 16 pytest functions pass. Proposal `-015` framed 18 tests / 10 M-criteria; the 18 framing counted M1-M10 as separate criteria, while the live pytest implementation parameterizes them into 11 functions in `test_isolation_018_e1_rollback_completeness.py` (M1-M3 + M4 + M5-M10 = 11 of the 16). The other 5 pytest functions are in `test_isolation_018_e1_step_order.py` (T-step-order-1 family).

## Known Regression

Full project pytest collect surfaced 17 errors (pre-move baseline: 2 errors). Owner approved commit-with-regression via AUQ #2 (Option 1).

### Pre-move baseline (2 errors)

Captured at `.tmp/e1-baseline/pytest-collect-baseline.txt` line summary only (per-error detail not preserved at baseline-snapshot time). Inferred from post-fix categories: most likely `applications/Agent_Red/tests/evaluation/test_deepeval_scaffold.py` and `applications/Agent_Red/tests/evaluation/test_quality_pilot.py` (both fail with `ModuleNotFoundError: No module named 'evaluation'` — these were already failing pre-move because the `evaluation/` location was not on sys.path).

### Post-move errors (17)

Captured at `.tmp/e1-collect-report4.json` (full JSON-report-plugin output):

| Test file | Error | Category |
|---|---|---|
| `tests/governance/test_isolation_018_e1_rollback_completeness.py` | `ModuleNotFoundError: No module named 'tests.governance'` | Two-tests-packages collision |
| `tests/governance/test_isolation_018_e1_step_order.py` | same | same |
| `tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` | `ModuleNotFoundError: No module named 'tests.hooks'` | same |
| `tests/hooks/test_credential_scan.py` | same | same |
| `tests/hooks/test_formal_artifact_approval_gate.py` | same | same |
| `tests/hooks/test_glossary_expansion.py` | same | same |
| `tests/hooks/test_narrative_artifact_approval.py` | same | same |
| `tests/hooks/test_owner_decision_tracker.py` | same | same |
| `tests/hooks/test_workstream_focus.py` | same | same |
| `tests/scripts` (whole-dir) | `ModuleNotFoundError: No module named 'tests.scripts'` | same |
| `tests/skills/test_bridge_propose_helper.py` | `ModuleNotFoundError: No module named 'tests.skills'` | same |
| `tests/test_host/test_build_contract.py` | `ModuleNotFoundError: No module named 'test_host'` | Likely same-class (sys.path collision) |
| `tests/test_loyal_opposition_file_safety_clarification.py` | `ModuleNotFoundError: No module named 'tests.test_loyal_opposition_file_safety_clarification'` | same |
| `tests/test_no_active_smart_poller_wording.py` | `ModuleNotFoundError: No module named 'tests.test_no_active_smart_poller_wording'` | same |
| `applications/Agent_Red/tests/evaluation/test_deepeval_scaffold.py` | `ModuleNotFoundError: No module named 'evaluation'` | Likely pre-existing |
| `applications/Agent_Red/tests/evaluation/test_quality_pilot.py` | `ModuleNotFoundError: No module named 'evaluation'` | Likely pre-existing |
| `applications/Agent_Red/tests/ops/test_hooks_specs.py` | `ModuleNotFoundError: No module named 'scheduler'` | Likely pre-existing (`scheduler/` not on sys.path pre- or post-move) |

### Root cause

Two `tests/` directories on Python's sys.path resolve to the same package name with different contents:

- `<root>/tests/__init__.py` (this slice restored the package marker; staying tests use it)
- `applications/Agent_Red/tests/__init__.py` (migrated; carries the original conftest.py + e2e/e2e_live/e2e_mock subdirs)

Whichever loads first wins in `sys.modules`. Subsequent imports of `tests.<X>` succeed when `<X>` is in the cached package and fail otherwise. The 14 `tests.<X>` ModuleNotFoundError entries are downstream of this collision; they trip the staying tests when the migrated `tests/` package loads first (typical for full-project collect because `applications/Agent_Red/tests/` is alphabetically searched first).

The 3 likely-pre-existing errors (`evaluation`, `scheduler`) are unrelated to the move and would have failed pre-move under the same `pytest --collect-only` invocation.

### Mitigation in this slice

`tests/__init__.py` restoration reduced the regression from 22 → 17 errors (5 fewer). Without it, the staying `tests/scripts/test_*.py` files import `from scripts.foo import bar` resolving to `tests/scripts/foo.py` (wrong package) because pytest's parent-traversal stopped at the no-init-py `tests/` directory and added it to sys.path.

### Follow-up bridge (to be filed after this commit lands)

A follow-up bridge `gtkb-tests-package-collision-resolution-001.md` (status: PLANNED for next session) will propose the structural fix: rename `<root>/tests/` → `<root>/platform_tests/`. Rationale: collision is unresolvable as long as two Python packages have the same name; renaming eliminates the conflict at the package-name layer rather than papering over it via sys.path ordering tricks. The follow-up will go through normal proposal-review-implement-verify gates.

## Deviations From Proposal `-015`

### Deviation 1 — WIP commit split (proposal acceptance criterion: ONE atomic commit; landed as TWO)

Proposal `-015` (carried from `-013`) called for a single atomic commit covering Steps 3-7. The slice landed as TWO commits:

- `58ac3ef5 wip(isolation): E.1 Steps 0-2 + platform-files (resume at Step 3)` (S339, 2026-05-10).
- `<HEAD>` of this commit (S340, 2026-05-11) covers Steps 3-6 plus the regression-mitigation fix.

The split is solely a session-handoff artifact at owner directive during S339 wrap-up. No semantic split; the slice as a whole is atomic at the GT-KB lifecycle level.

### Deviation 2 — `tests/__init__.py` scope expansion (proposal Step 4 list: pyproject only)

Proposal `-015` Step 4 enumerated four pyproject.toml edits and explicitly DID NOT include any new package-marker file creation. The discovered regression at Step 6 made `tests/__init__.py` necessary to restore parent-traversal behavior. Owner approved (AUQ #1).

### Deviation 3 — `"."` added to pyproject pythonpath (proposal: `["applications/Agent_Red"]`)

Proposal `-015` Step 4 specified `pythonpath = ["applications/Agent_Red"]`. Implementation has `pythonpath = [".", "applications/Agent_Red"]` to make the project root importable for the staying tests' `from tests.governance import ...` style. Owner approved (AUQ #1 implicit; AUQ #2 ratifies the broader regression-mitigation pathway).

### Deviation 4 — 17 collect-only errors (proposal silent on broader collect coverage)

Proposal `-015` acceptance criteria included Step 6 governance-test pass (16/16 ✓) and Step 6.5 src-import-resolution proof (✓), but did not enumerate the broader collect-only error count. The 17 errors (vs 2 pre-move baseline) constitute a regression in collect coverage. Owner approved commit-with-regression (AUQ #2) on the understanding that the follow-up bridge will propose the structural fix.

## Acceptance Criteria Status

23 criteria carry forward from `-013` + criterion 22 replacement from `-015`. Compact status:

| Criterion | Status |
|---|---|
| 1-21 (carry-forward from earlier revisions; cluster moves, write-set consumption, rollback symmetry, etc.) | **PASS** (governance tests M1-M10 cover the criteria with mechanical assertions) |
| 22 (REPLACEMENT from `-015`) — Single write-set consumed by precondition + rollback + Step 3; T-write-set-1 verifies non-drift + rollback completeness + cross-platform containment | **PASS** (16/16 governance tests pass) |
| 23 (carry-forward; single atomic commit) | **DEVIATED** (split into 2 commits at S339 session-handoff; Deviation 1) |
| 24 (carry-forward; no collect-only regression vs baseline) | **DEVIATED** (15-error net regression; owner-approved per AUQ #2; Deviation 4) |

## Risks Status

| Risk (from `-015`) | Realized? | Disposition |
|---|---|---|
| R1 — git mv cross-volume issues on Windows | No | All moves same-volume (E:); 0 failures in 643 invocations. |
| R2 — Rename detection threshold | No | Git status shows 1,423 staged renames (R), not add+delete. |
| R3 — Mid-loop failure during Step 3 | No | scripts/run_e1_step3.py completed cleanly (643/643). |
| R4 — pyproject.toml typo breaks pytest | No | 16 governance tests pass post-edit; 5,983-test collect succeeds for multi_tenant. |
| R5 — Workflow YAML rewrite breaks CI | Unverified | CI will exercise on next PR; rewriter dry-run inspected before apply. |
| R6 — Dockerfile rewrite breaks container build | Unverified | Build will exercise on next CI run; same dry-run inspection. |
| R7 — Hidden import resolution failure | **REALIZED** | 17 collect-only errors expose two-tests-packages collision; mitigated by `tests/__init__.py` (22→17); follow-up bridge proposes structural fix. |

## Files Changed (diff/stat)

`1442 files changed, 469 insertions(+), 151 deletions(-)`.

- 1,423 renames (R): `<root>/<src|admin|widget|branding>/...` → `applications/Agent_Red/<...>` and 638 paired test moves.
- 16 modifications (M): `.dockerignore`, 11 workflow YAML, 3 Dockerfile-class, `docker-compose.yml`, `pyproject.toml`.
- 3 new files (A): `scripts/run_e1_step3.py` (executor; ~110 lines), `scripts/run_e1_step5.py` (executor; ~180 lines), `tests/__init__.py` (package marker; ~14 lines).

## Codex Review Notes

Per Codex's `-016` GO implementation notes:

1. ✓ `scripts/rollback_e1_write_set.py:151` calls `validate_agent_red_destination` before both `unlink()` and `rmtree()`.
2. ✓ `tests/governance/test_isolation_018_e1_rollback_completeness.py` includes M5-M10 positive/negative coverage (live test count: 16, including all M-criteria).
3. ✓ `.tmp/e1-drift/write-set.json` is the single shared source: consumed by `scripts/check_e1_write_set_precondition.py` (Step 1; from `58ac3ef5`), `scripts/rollback_e1_write_set.py` (rollback; line 138), and `scripts/run_e1_step3.py` (Step 3; new in this commit, lines 50-71). The new Step 5 executor (`scripts/run_e1_step5.py`) also consumes the same write-set for in-place edit driving.
4. Implementation report carries forward Specification Links, spec-to-test mapping, exact commands, observed results, diff/stat, and recommended commit type per `-016` direction.

Residual note from `-016`: rollback script does NOT add the application root `applications/Agent_Red` itself to `destinations_to_clean` (verified by inspection at `scripts/rollback_e1_write_set.py:141-147`).

## Drift Surfaces Surfaced (Out-of-Scope, Follow-Up Tracked)

1. **.gitignore patterns** — lines 88, 89, 210, 345 reference old root paths (`tests/performance/load-test-report.html`, `tests/performance/load-test-results*.csv`, `tests/results/`, `widget/storybook-static/`). After the move these no longer match the relocated paths under `applications/Agent_Red/...`. Owner will need to decide whether to ADD applications/Agent_Red/... siblings, REPLACE the patterns, or rely on per-app `.gitignore` files inside `applications/Agent_Red/`. Not addressed in this slice.
2. **`applications/Agent_Red/widget/storybook-static/`** — build output not gitignored at the new path; appears as `??` in git status post-move. Not committed in this slice.
3. **`tests/test_host/test_build_contract.py`** — fails collect; may need either same-class fix as the staying-tests-package collision OR a `test_host/` rename (unclear; in follow-up scope).
4. **`config_files_in_place_edits` per-file-ignore coverage in pyproject.toml `[tool.ruff.lint.per-file-ignores]`** — `"tests/**"` still matches platform tests (correct) but does NOT match migrated tests under `applications/Agent_Red/tests/**`. May cause additional lint findings on migrated tests in CI; not in proposal scope.

All four are tracked for the follow-up bridge (`gtkb-tests-package-collision-resolution-001`) plus follow-on tier (E.2 lifecycle independence work).

## Applicability Preflight

Will be run by Codex at review time per `.claude/rules/codex-review-gate.md`. This report's bridge-document name is `gtkb-isolation-018-slice-e1-atomic-code-move` and operative file is `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md`. Expected: same specs as `-016` (preflight passed there; this report cites the same set).

## Result

`NEW` — awaiting Codex VERIFIED review.

Codex review obligations per `.claude/rules/codex-review-gate.md`:

1. Confirm proposal's linked specs carry forward (§ Specification Links).
2. Confirm tests derived from those specs were created or identified (§ Spec-to-Test Mapping).
3. Confirm those tests were executed (§ Exact Commands Run).
4. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e1-atomic-code-move`.
5. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-018-slice-e1-atomic-code-move`.
6. Include both preflight sections in the VERIFIED verdict.
7. Evaluate deviations 1-4 against the proposal's acceptance criteria.
8. Issue `VERIFIED` or `NO-GO` accordingly.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
