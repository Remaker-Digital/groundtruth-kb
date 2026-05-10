# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.E.1: Atomic Code Cluster Move

**Document:** `gtkb-isolation-018-slice-e1-atomic-code-move`
**Status:** `NEW`
**Date:** 2026-05-10
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `refactor:` (file relocation; no behavior change; preserves git history via `git mv`)

## Goal

Atomically relocate Agent Red's code clusters from GT-KB root into `applications/Agent_Red/` per the GO'd 18.E scoping at `bridge/gtkb-isolation-018-slice-e-code-cluster-004.md` and the umbrella plan at `bridge/gtkb-isolation-018-agent-red-file-migration-008.md`. Six clusters move in a single commit:

| Cluster | Source path | Destination path | Live count (2026-05-10) |
|---------|-------------|------------------|--------:|
| `src/` | `src/` | `applications/Agent_Red/src/` | 305 |
| `tests/` (migrating subset) | `tests/<file>` per E.3 manifest | `applications/Agent_Red/tests/<file>` | 638 (per E.3 manifest at S334) |
| `admin/` | `admin/` | `applications/Agent_Red/admin/` | 361 |
| `widget/` | `widget/` | `applications/Agent_Red/widget/` | 51 |
| `branding/` | `branding/` | `applications/Agent_Red/branding/` | 67 |
| `config/stripe_product_ids.json` | `config/stripe_product_ids.json` | `applications/Agent_Red/config/stripe_product_ids.json` | 1 |

**Total moves: ~1,423 files** (per S334 manifest; will be re-confirmed by Step 0 drift reconciliation).

Plus: pyproject.toml updates (4 fields), in-place edits to `.github/workflows/*.yml` for path strings, and 6 new Bucket-A registry entries in `applications/Agent_Red/.gtkb-app-isolation.json`.

E.2 (scripts per-file split) and 18.F+ (infra, CI, manifests, identity, repo separation, etc.) are out of scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This proposal was filed via the bridge-propose helper which inserted a NEW entry at the top of bridge/INDEX.md per the protocol; no prior versions of this thread exist; nothing is rewritten or deleted.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires tests derived from linked specifications and executed against the implementation; this proposal includes a comprehensive spec-to-test mapping.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — applications/<name>/ placement convention. This proposal directly operationalizes the placement contract for Agent Red's code clusters.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority for the Agent Red nested-application topology; 5 binding rules.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 — 5 binding rules; waiver policy; repo-topology contract.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 — machine-checkable contract.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE) — authorizes in-flight pre-migration state during the umbrella program.
- `DCL-APP-ROOT-MINIMIZATION-001` — minimization principle for `applications/Agent_Red/` root.
- `GOV-STANDING-BACKLOG-001` — work_list.md as governed work authority; ISOLATION-018 is implicitly TOP-priority per S334 owner directive.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented development as the working model.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented governance discipline.
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md` — canonical umbrella plan (Codex GO at -009).
- `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md` — 18.E scoping proposal (Codex GO at -004).
- `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-009.md` — E.3 disposition report (Codex VERIFIED at -010).
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` — 18.C VERIFIED; pattern precedent for in-place workflow path edits.
- `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` — 18.D VERIFIED; pattern precedent.
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` — 18.B VERIFIED; pattern precedent for atomic dir-rename.
- `applications/Agent_Red/.gtkb-app-isolation.json` — current isolation registry; this proposal adds 6 new Bucket-A entries.
- `.tmp/e3-disposition/manifest-v2.json` — E.3 platform-test disposition manifest (canonical record of the 731-file disposition at S334; subject to drift reconciliation in Step 0).
- `.claude/rules/project-root-boundary.md` — 5 binding rules; this slice operationalizes Rule 3.
- `.claude/rules/operating-model.md` §1 and §2 — application/platform partition and isolation as lifecycle independence.
- `.claude/rules/file-bridge-protocol.md` — Mandatory Owner Decisions / Input Section Gate; Mandatory Pre-Filing Preflight Subsection; Mandatory Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Loyal Opposition review obligations.
- `.claude/rules/canonical-terminology.md` — application, platform, hosted application terminology.
- `.claude/rules/deliberation-protocol.md` — pre-proposal deliberation-search obligation.

## Prior Deliberations

(Helper pre-populates from glossary-source seeds and semantic search.)

Author-supplied additions:
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — S330 owner directive establishing the 5 binding rules; canonical authority for the entire ISOLATION-018 program.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — S331 active waiver authorizing in-flight pre-migration state during the umbrella program.
- S334 AUQ "18.E scope" answer "Sub-split: 18.E.1 + 18.E.2 + 18.E.3 (Recommended)" — authorized this 3-way decomposition.
- Codex GO at `bridge/gtkb-isolation-018-slice-e-code-cluster-004.md` — approves the scoping decomposition.
- Codex VERIFIED at `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-010.md` — verifies the E.3 manifest closing over 731 tests/ files.
- 18.B/18.C/18.D VERIFIED precedents establish the pattern: atomic move + in-place workflow path edits + post-move verification.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1119` — seed=search; bridge_thread; Bridge thread: gtkb-isolation-016-phase8-rehearsal-implementation (18 versions, 
- DA: `DELIB-0988` — seed=search; bridge_thread; GTKB-ISOLATION-015 Slice 2 Reconciliation Review
- DA: `DELIB-0955` — seed=search; bridge_thread; GO: GTKB-ISOLATION-016 Phase 8 rehearsal implementation
- DA: `DELIB-1137` — seed=search; bridge_thread; Bridge thread: gtkb-isolation-008-migration-plan-review (6 versions, VERIFIED)
- DA: `DELIB-1004` — seed=search; bridge_thread; GTKB-ISOLATION-015 - Loyal Opposition Review

## Owner Decisions / Input

This proposal depends on owner approval per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate:

1. **Owner AskUserQuestion answer (this session, 2026-05-10):** "Withdraw all 3; pick up 18.E (Recommended)" — directly authorizes Prime Builder to pick up 18.E implementation.
2. **Antecedent owner authorizations carried forward:**
   - S334 AUQ "18.E scope" answer "Sub-split: 18.E.1 + 18.E.2 + 18.E.3 (Recommended)" — authorized the 3-way decomposition this proposal implements.
   - S334 AUQ "Isolation move" answer (full directive approving completion of the isolation workstream as release-gating).
   - `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority for the entire program.
   - `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — active waiver authorizing in-flight pre-migration state.
3. **No new owner decisions required for this slice.** The E.3 disposition (Option A with file-level granularity) is already VERIFIED at -010; this slice executes against the disposition manifest.

## Live State Probed (2026-05-10, this session)

```text
git ls-files src/ | wc -l       → 305
git ls-files tests/ | wc -l     → 748   (drift: +17 since E.3 manifest at S334's 731)
git ls-files admin/ | wc -l     → 361
git ls-files widget/ | wc -l    → 51
git ls-files branding/ | wc -l  → 67
git ls-files config/stripe_product_ids.json | wc -l → 1
```

Drift summary: tests/ has gained 17 files since the S334 E.3 manifest was finalized. The E.3 manifest enumerated 731; live count is 748. Step 0 of this slice reconciles those 17 new files against the manifest dispositions before Step 3 moves anything.

## Implementation Plan

### Step 0 — Drift Reconciliation (NEW; required by umbrella -008's "live re-confirmation" pattern)

**Goal:** Bring the E.3 manifest current. The 17 new tests/ files since 2026-05-07 need disposition before atomic move.

Sub-steps:
1. `git ls-files tests/ | sort > /tmp/tests-live.txt`
2. Extract manifest paths: `python -c "import json; m=json.load(open('.tmp/e3-disposition/manifest-v2.json')); paths = set(); [paths.update([f['path'] for f in m.get(k, [])]) for k in ('STAYS_PLATFORM_py','STAYS_PLATFORM_nonpy','MIGRATES_AGENT_RED_py','MIGRATES_AGENT_RED_nonpy','MIGRATES_AGENT_RED_WITH_SCRIPT_DEP_py')]; print('\n'.join(sorted(paths)))" > /tmp/tests-manifest.txt`
3. `comm -23 /tmp/tests-live.txt /tmp/tests-manifest.txt > /tmp/tests-new-since-manifest.txt` — the 17 files not in manifest.
4. `comm -13 /tmp/tests-live.txt /tmp/tests-manifest.txt > /tmp/tests-removed-since-manifest.txt` — any manifest entries no longer in live tree (deleted tests).
5. **Disposition heuristic** for the 17 new files (per umbrella -008 pattern):
   - Files under `tests/hooks/` → STAYS_PLATFORM (test GT-KB hooks via `parents[2] / ".claude" / "hooks" / ...`)
   - Files under `tests/scripts/` matching platform-name patterns (test_check_*, test_codex_*, test_groundtruth_*, test_rehearse_*, test_release_*, test_workstream_*, test_session_init_*, test_bridge_*, test_harness_*) → STAYS_PLATFORM
   - All other test files → MIGRATES_AGENT_RED (or MIGRATES_AGENT_RED_WITH_SCRIPT_DEP if they import scripts/)
   - Manual review of any ambiguous files; document each disposition with rationale in the post-implementation report.
6. **Manifest update:** generate `manifest-v3.json` at `.tmp/e3-disposition/manifest-v3.json` containing the reconciled disposition. Original v2 preserved for audit. v3 carries `provenance.parent: 'manifest-v2.json'` plus the per-file disposition deltas.
7. Verify: `python -c "import json; m=json.load(open('.tmp/e3-disposition/manifest-v3.json')); buckets = {k: len(m[k]) for k in m if isinstance(m[k], list)}; print(sum(buckets.values()), 'should equal', m['totals'].get('grand_total'))"`

**Deliverable:** v3 manifest closes over the 748 live tests/ files. v2 preserved.

### Step 1 — Pre-move baseline capture

**Goal:** Establish a green baseline so post-move verification can compare.

Sub-steps:
1. `python -m pytest --collect-only -q 2>&1 | tail -3` — record count of collected tests.
2. `cd admin && npm run build 2>&1 | tail -10 ; cd ..` — record admin build success/failure baseline.
3. `cd widget && npm run build 2>&1 | tail -10 ; cd ..` — record widget build success/failure baseline.
4. Secret-scan baseline: `python scripts/scan_credentials.py src/ tests/ admin/ widget/ branding/ config/ 2>&1 | tail -10` (or equivalent per 18.C precedent).
5. `python scripts/release_candidate_gate.py 2>&1 | tail -20` — record gate baseline (any pre-existing failures noted; only NEW failures count as regression).

**Deliverable:** baseline-snapshot.json at `.tmp/e1-baseline/baseline-snapshot.json` with all 5 baseline metrics.

### Step 2 — Update isolation registry

**Goal:** Add 6 new Bucket-A entries to `applications/Agent_Red/.gtkb-app-isolation.json` BEFORE moving files (so the registry reflects the planned post-move state).

Sub-steps:
1. Edit `applications/Agent_Red/.gtkb-app-isolation.json` to append 6 new entries to `top_level_artifacts`:
   - `{"name": "src", "type": "DIR", "bucket": "A", "purpose": "Agent Red Python application code (multi_tenant, agents, integrations, chat, app, jobs, migrations, observability, presets, quality_metrics, white-label, ai-features)"}`
   - `{"name": "tests", "type": "DIR", "bucket": "A", "purpose": "Agent Red test suite (excluding 93+ platform-test files staying at GT-KB root per E.3 manifest)"}`
   - `{"name": "admin", "type": "DIR", "bucket": "A", "purpose": "Agent Red admin app (Vite + React + TypeScript)"}`
   - `{"name": "widget", "type": "DIR", "bucket": "A", "purpose": "Agent Red chat widget (Vite + Preact + TypeScript)"}`
   - `{"name": "branding", "type": "DIR", "bucket": "A", "purpose": "Agent Red product branding assets (deferred from 18.D per parents[2] dependency)"}`
   - `{"name": "config", "type": "DIR", "bucket": "A", "purpose": "Agent Red config (initially: Stripe pricing); platform configs in config/agent-control/ and config/governance/ STAY at GT-KB root per umbrella -008"}`
2. Update `last_updated` to `2026-05-10`.
3. Verify JSON is valid: `python -c "import json; json.load(open('applications/Agent_Red/.gtkb-app-isolation.json'))"`.

**Note:** This Edit happens via the narrative-artifact-approval-gate hook IF the registry file is in the protected-narrative-artifact list. Verify pre-implementation; if so, assemble formal-artifact-approval packet.

### Step 3 — Atomic git mv of all 6 clusters

**Goal:** Move the planned files in a single, ordered, atomic operation. Single staged change set. No partial-success state observable.

Sub-steps:
1. `git mv src applications/Agent_Red/src` — moves all 305 files; preserves history.
2. For each MIGRATES_AGENT_RED + MIGRATES_AGENT_RED_WITH_SCRIPT_DEP path P from manifest-v3:
   - `git mv P applications/Agent_Red/P`
   - This is a per-file mv since tests/ is not moved wholesale (93+ platform-test files stay).
   - Use a Python script driving `subprocess.run(["git", "mv", src, dst])` per path; collect errors; abort on first error and report.
3. `git mv admin applications/Agent_Red/admin` — moves all 361 files.
4. `git mv widget applications/Agent_Red/widget` — moves all 51 files.
5. `git mv branding applications/Agent_Red/branding` — moves all 67 files.
6. `git mv config/stripe_product_ids.json applications/Agent_Red/config/stripe_product_ids.json` — note: applications/Agent_Red/config/ doesn't exist yet; mkdir first OR git mv handles it.

Verify after each step: `git status --short | wc -l` should grow incrementally, never decrease.

### Step 4 — Update pyproject.toml import-path config

**Goal:** Align Python tooling configuration with new file paths.

Edit `pyproject.toml` to update 4 fields per scoping proposal:
1. `testpaths` — if Option A (file-level split): `["tests", "applications/Agent_Red/tests"]` (dual discovery). If E.3's chosen disposition is different, follow E.3.
2. `[tool.ruff].source` (or equivalent) — update to include `applications/Agent_Red/src` and remove bare `src` if all of src moved.
3. `[tool.ruff.isort].known-first-party` — update to `["applications.Agent_Red.src"]` or per project's package-resolution convention.
4. `[tool.coverage.run].source` (or `paths_to_mutate` if mutation-testing config) — analogous update.

Verify: `python -c "import tomllib; tomllib.loads(open('pyproject.toml').read())"` succeeds.

### Step 5 — In-place edits to .github/workflows/*.yml

**Goal:** Update path-string references in CI workflows so they continue to work post-move (mirrors 18.C pattern).

Sub-steps:
1. `grep -rn 'src/\|tests/\|admin/\|widget/\|branding/' .github/workflows/*.yml > /tmp/workflow-path-refs.txt`
2. For each match, decide:
   - If the workflow is Agent Red CI (per umbrella -008's .github/workflows table): update path to `applications/Agent_Red/src/...` etc. The workflow itself stays at GT-KB root for now; 18.G handles the actual migration of CI workflows.
   - If the workflow is GT-KB platform CI (`groundtruth-kb-tests.yml`, `gtkb-secrets-scan.yml`): no path edit needed (it doesn't reference Agent Red paths).
3. Apply the edits.

Verify: `grep -rn 'src/\|tests/\|admin/\|widget/\|branding/' .github/workflows/*.yml | grep -v 'applications/Agent_Red'` returns only platform paths or no matches.

### Step 6 — Run all spec-derived tests

Run each test from § Tests Derived From Linked Specifications below. Capture output. Any failure not present in baseline-snapshot.json is a regression and aborts the slice.

### Step 7 — Single commit on develop

**Goal:** Atomic commit capturing all the changes from Steps 2-5 plus the test files added in Step 6.

Commit message:

```text
refactor(isolation): relocate Agent Red code clusters into applications/Agent_Red/

Sub-slice 18.E.1 of GTKB-ISOLATION-018 umbrella program. Moves ~1,423 files via git mv (preserving history): src/ (305), tests/ MIGRATES bucket (~638 per manifest-v3), admin/ (361), widget/ (51), branding/ (67), config/stripe_product_ids.json (1).

Updates pyproject.toml import-path config (testpaths, source, known-first-party, coverage source) to align with new locations. In-place edits to .github/workflows/*.yml for path strings (Agent Red CI workflows; full migration of workflows is 18.G scope).

Adds 6 new Bucket-A entries to applications/Agent_Red/.gtkb-app-isolation.json registry: src, tests, admin, widget, branding, config.

E.3 manifest reconciled at .tmp/e3-disposition/manifest-v3.json (closes over 748 live tests/ files; +17 since manifest-v2 at S334; provenance preserved).

Authority: DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE; ACTIVE waiver DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER. Bridge: bridge/gtkb-isolation-018-slice-e1-atomic-code-move-XXX.md.
```

(Commit hash placeholder until VERIFIED step records actual hash in post-implementation report.)

## Tests Derived From Linked Specifications

| Test | Verifies | Linked spec |
|------|----------|-------------|
| **T-rule-1**: assert no Agent Red files at GT-KB-root paths post-move (`git ls-files src/ admin/ widget/ branding/` returns empty; `git ls-files config/stripe_product_ids.json` returns empty; `git ls-files tests/` returns only the 93+ platform-test subset per manifest-v3 STAYS_PLATFORM bucket) | `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` Rule 1 + `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both |
| **T-rule-2**: assert all moved files now at `applications/Agent_Red/<cluster>/` (`git ls-files applications/Agent_Red/src/` count matches; same for admin/widget/branding/config/tests-migrated subset) | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Same |
| **T-platform-stay**: assert STAYS_PLATFORM tests from manifest-v3 are still at GT-KB root (sample 5 paths from each STAYS bucket; verify via `git ls-files`) | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` Rule 1 contrapositive | Same |
| **T-secret-1**: secret-scan post-move clean (`python scripts/scan_credentials.py applications/Agent_Red/src applications/Agent_Red/tests applications/Agent_Red/admin applications/Agent_Red/widget applications/Agent_Red/branding applications/Agent_Red/config 2>&1`) — same patterns as 18.C/18.D | 18.C/18.D pattern precedents | `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` |
| **T-secret-2**: secret-scan baseline-vs-post-move regression check (no NEW credential-shaped spans introduced by the move) | Same | Same |
| **T-import-1**: no remaining bare `src/`, `tests/` (excl. STAYS_PLATFORM), `admin/`, `widget/`, `branding/` references in active code (excluding bridge/, archive/, docs/, .git/, .tmp/) — `grep -rn '\bsrc/\b\|\badmin/\b\|\bwidget/\b\|\bbranding/\b' --include='*.py' --include='*.ts' --include='*.tsx' --include='*.js' --include='*.json' --include='*.yml' --include='*.yaml' . \| grep -v 'applications/Agent_Red\|bridge/\|archive/\|docs/\|\.tmp/\|node_modules/'` returns empty (excluding documented exceptions) | `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` | Same |
| **T-pytest-collect**: `python -m pytest --collect-only -q 2>&1 \| tail -3` shows expected count post-move (baseline count from Step 1 minus zero, since no tests deleted; only relocated) and no collection errors | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Same |
| **T-pytest-subset**: smoke subset of Agent Red tests passes from new location (`python -m pytest applications/Agent_Red/tests/multi_tenant/ -q -x --ignore=applications/Agent_Red/tests/e2e_live --ignore=applications/Agent_Red/tests/e2e_mock 2>&1 \| tail -10`) — at minimum: collection succeeds and any failures match baseline (no new failures) | Same | Same |
| **T-admin-build**: `cd applications/Agent_Red/admin && npm run build 2>&1 \| tail -10` — succeeds, matches baseline | E.1 design `-001` line 113 | `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md` |
| **T-widget-build**: `cd applications/Agent_Red/widget && npm run build 2>&1 \| tail -10` — succeeds, matches baseline | Same | Same |
| **T-pyproject-1**: `python -c "import tomllib; d=tomllib.loads(open('pyproject.toml').read())"` succeeds; testpaths/source/known-first-party/coverage-source fields all reference `applications/Agent_Red/` paths | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Same |
| **T-platform-smoke**: GT-KB platform tests pass (no NEW failures vs baseline) — `python -m pytest tests/hooks/ tests/scripts/ -q 2>&1 \| tail -10` (or equivalent platform-test-set runner) | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (waiver allows in-flight; waiver post-implementation tests platform unbroken) | `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-010.md` |
| **T-history-1**: sample 5 moved files (one per cluster) and run `git log --follow applications/Agent_Red/<sample-path>` — confirms the GT-KB-root commit lineage is preserved across the move | `git mv` invariant + 18.B/18.C/18.D precedent | Same precedents |
| **T-waiver-1**: commit message cites `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` explicitly | Same waiver | Same |
| **T-registry-1**: `applications/Agent_Red/.gtkb-app-isolation.json` contains the 6 new Bucket-A entries (src, tests, admin, widget, branding, config); JSON is valid | `DCL-APP-ROOT-MINIMIZATION-001` registry-correctness invariant | Step 2 |

15 tests covering the slice's spec-derived invariants. Pass criteria: all tests pass; baseline regressions are zero.

## Verification Commands

```text
$ python -m pytest tests/governance/test_isolation_018_e1_atomic_move.py -q
(15 tests passing)
$ python -m pytest --collect-only -q 2>&1 | tail -3
(matches baseline-snapshot.json)
$ python scripts/release_candidate_gate.py 2>&1 | tail -20
(no NEW failures vs baseline)
$ git diff --stat HEAD~1 HEAD | tail -3
(~1,423 files changed; rename detection should show most as renames preserving history)
```

## Risks and Rollback

### R1 — `git mv` fails partway through Step 3 (atomic-move violation)

If a `git mv` errors mid-Step-3 (e.g., destination collision, permissions), the working tree is in a partial-move state.

**Mitigation:** Per-file `git mv` driven by Python script with explicit error capture. On first error, abort and emit a partial-state report. Use `git status --short` to inventory the partial state. The slice does NOT commit until Step 7; the partial state is fully recoverable via `git restore --staged .` and `git checkout .` to reset to pre-move tree.

**Rollback:** `git restore --staged .; git checkout .` before any commit. The branch is unchanged; only working-tree state was disturbed.

### R2 — Baseline regression in T-pytest-collect or T-platform-smoke

If post-move pytest collection or platform tests show NEW failures, the move broke something.

**Mitigation:** baseline-snapshot.json captures pre-move state with explicit failure lists. Post-move comparison only flags NEW failures, not pre-existing ones.

**Rollback:** Same as R1 (no commit yet) OR if commit landed: `git revert HEAD` for the single commit, recovers pre-move state in one step.

### R3 — `applications/Agent_Red/config/` does not yet exist; `git mv` of stripe_product_ids.json may need mkdir

**Mitigation:** Step 3 sub-step 6 mkdir's the destination first. `git mv` from POSIX paths to a non-existent destination directory errors out cleanly; the mkdir is preflight.

**Rollback:** Same as R1.

### R4 — Drift Reconciliation (Step 0) misclassifies one of the 17 new tests/ files

If a new test is misclassified as STAYS when it should MIGRATE (or vice versa), it ends up in the wrong location post-move.

**Mitigation:** Heuristic in Step 0 sub-step 5 covers the dominant patterns; ambiguous files surfaced for manual review BEFORE Step 3. Manifest-v3 includes per-file rationale field for the 17 reconciled files. Codex review verifies.

**Rollback:** Same as R2 — `git revert HEAD` for misclassified-file moves; pair with manifest-v4 correction.

### R5 — pyproject.toml import-path config breaks GT-KB platform tooling

If `[tool.ruff.isort].known-first-party` change breaks ruff's import-sorting for GT-KB platform code (`groundtruth-kb/`), ruff CI may fail.

**Mitigation:** Step 4 includes both `applications.Agent_Red.src` AND `groundtruth_kb` (the platform package). Pre-move grep confirms `groundtruth_kb` is the existing platform-package alias. Post-move, run `python -m ruff check groundtruth-kb/` to verify.

**Rollback:** Same as R2.

### R6 — In-place workflow edits (Step 5) break Agent Red CI immediately

If any .github/workflows/*.yml has a path string that refers to (e.g.) `src/multi_tenant/` and we update it to `applications/Agent_Red/src/multi_tenant/`, but the workflow's actual command-line tooling can't resolve the new path, CI breaks at next push.

**Mitigation:** Step 5 uses the same in-place-edit pattern as 18.C (which was VERIFIED). Pre-move, run `python -c "import yaml; [yaml.safe_load(open(f)) for f in glob('.github/workflows/*.yml')]"` to confirm YAML validity post-edit.

**Rollback:** Same as R2.

### R7 — Owner-decision-tracker hook fires on the bridge-propose helper output

This proposal's body has lots of "Decision needed", "Required action", etc. Pattern-matchers may fire on prose decision-asks.

**Mitigation:** The proposal does NOT ask owner decisions in prose. All owner-decision asks are pre-resolved per § Owner Decisions / Input. The post-implementation report similarly avoids prose decision-asks.

**Rollback:** N/A — hook firing is non-blocking for implementation; the gate is on bridge file Write/Edit, which already succeeded.

## Acceptance Criteria

The slice is complete and ready for VERIFIED when:

1. All 15 tests in § Tests Derived From Linked Specifications pass; no NEW baseline regressions.
2. `git ls-files src/ admin/ widget/ branding/` returns empty.
3. `git ls-files config/stripe_product_ids.json` returns empty.
4. `git ls-files tests/` returns only the STAYS_PLATFORM subset from manifest-v3 (~93 paths plus any drift-reconciled additions).
5. `git ls-files applications/Agent_Red/src/` returns 305 paths.
6. `git ls-files applications/Agent_Red/tests/` returns the MIGRATES subset (~638 from S334 + drift-reconciled additions; final count documented in post-implementation report).
7. `git ls-files applications/Agent_Red/admin/` returns 361 paths.
8. `git ls-files applications/Agent_Red/widget/` returns 51 paths.
9. `git ls-files applications/Agent_Red/branding/` returns 67 paths.
10. `git ls-files applications/Agent_Red/config/stripe_product_ids.json` returns 1 path.
11. `applications/Agent_Red/.gtkb-app-isolation.json` contains 6 new Bucket-A entries (src, tests, admin, widget, branding, config); JSON valid.
12. `pyproject.toml` testpaths, source, known-first-party, coverage-source fields all reference `applications/Agent_Red/` paths; tomllib parses without error.
13. `python -m pytest --collect-only` post-move shows expected count (no NEW collection errors).
14. `cd applications/Agent_Red/admin && npm run build` succeeds; same for widget.
15. `python scripts/release_candidate_gate.py` shows no NEW failures vs baseline-snapshot.json.
16. Single commit on `develop` carrying message per Step 7; git log --follow on sample paths preserves pre-move lineage.
17. `.tmp/e3-disposition/manifest-v3.json` exists and closes over 748 live tests/ files (drift reconciled).

## Out of Scope

- **18.E.2** — scripts per-file split (separate sub-sub-slice).
- **18.F** — infra (Dockerfiles, docker-compose, infrastructure/terraform). Separate sub-slice.
- **18.G** — full migration of `.github/workflows/*.yml` to applications/Agent_Red/.github/workflows/. Step 5 only does in-place path-string edits.
- **18.H** — manifests (package.json, pyproject.toml itself relocating, etc.). Step 4 only updates fields in the existing root pyproject.toml.
- **18.I** — identity files (README.md, CLAUDE.md, MEMORY.md, etc.) and memory/ split.
- **18.J** — repo separation (nested git checkout, gitignore boundary, agent-red remote removal).
- **18.K** — platform docs install.
- **18.L** — verification + waiver retirement.
- Any modification to `.claude/rules/`, `bridge/`, `groundtruth-kb/`, `independent-progress-assessments/`, `.codex/`, `.groundtruth/`, `tools/`, `harness-state/`, `archive/`, `.githooks/`, or any other GT-KB-platform-cluster path.

## Pre-Filing Applicability Preflight

Will run after this proposal is filed and INDEX entry is in place; final preflight result and `packet_hash` recorded post-revision in this section.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
