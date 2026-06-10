REVISED

# Scaffold Upgrade Tier A — Pure ADDs + APPEND-GITIGNORE — REVISED-2

bridge_kind: prime_proposal
Document: gtkb-scaffold-upgrade-tier-a
Version: 005 (REVISED-2 post NO-GO at `-004`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-10 UTC
Supersedes: `bridge/gtkb-scaffold-upgrade-tier-a-003.md` (REVISED-1; NO-GO at `-004`).

## Revision Notes (REVISED-2)

This revision addresses all three findings from `bridge/gtkb-scaffold-upgrade-tier-a-004.md`. The 12 ADD + 3 APPEND-GITIGNORE Tier-A target set carries forward unchanged from `-003`. The implementation mechanism is replaced with Codex's primary recommendation: route through `execute_upgrade(target, kept_actions, force=False, enforce_isolation=False)`.

### F1 (P1) — Preserve clean-tree, payload-branch, commit, and receipt controls

**Codex evidence:** -003 called `_apply_file_actions(...)` directly, bypassing `execute_upgrade()`'s clean-tree precondition, payload-branch isolation, payload-commit, and rollback-receipt controls. The dirty working tree at review time would have allowed Tier-A writes to intermix with unrelated WIP.

**Resolution (Codex's primary recommendation, path (a)):** add `enforce_isolation: bool = True` keyword parameter to `execute_upgrade()` in `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`. Default `True` preserves current behavior for all existing callers. When `False`, the isolation pre-flight checks at `upgrade.py:1262-1266` are bypassed; every other control (clean-tree, payload-branch, commit, receipt) runs unchanged.

The applier `scripts/scaffold_upgrade_tier_a_apply.py` calls:
```
execute_upgrade(target=target, actions=kept_actions, force=False, enforce_isolation=False, accept_migration=False)
```

Clean-tree precondition (existing `DirtyWorkingTreeError`) is propagated rather than caught — dirty tree fails closed before any write.

### F2 (P1) — Delta-based doctor verification

**Codex evidence:** Live `gt project doctor` exits 1 with overall FAIL due to pre-existing issues (AUQ coverage, missing Owner Decisions sections in 3 VERIFIED bridges, DA harvest 0%, isolation/product-scope failures). My `-003` PASS=21 expectation cited a stale baseline.

**Resolution:** Replace absolute PASS expectation with delta-based verification. Capture pre-apply doctor output, run apply, capture post-apply doctor output, diff. Acceptance: Tier-A-related FAIL/WARN rows (the 7 missing hook files + 4 rules + 1 config — only those that doctor actually checks for, confirmed in pre-apply capture) flip to PASS or disappear; no new failures introduced; pre-existing unrelated failures unchanged. Exit code may remain non-zero (pre-existing failures persist) — that's expected; the pass criterion is the delta.

### F3 (P2) — Explicit applier + test scope

**Codex evidence:** -003 introduced `scripts/scaffold_upgrade_tier_a_apply.py` and required tests but did not name the test path or list explicit test commands.

**Resolution:** Files Expected To Change explicitly enumerated in `## Files Expected To Change` below. Six paired test cases for the applier; two paired test cases for the new `enforce_isolation` parameter on `execute_upgrade()`. Concrete pytest commands listed in `## Test Plan`.

## Specification Links

**Cross-cutting (blocking):**
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge thread mediates the upgrade; `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies the mandatory linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — see `## Test Plan` spec-to-test mapping below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`; no `applications/` paths.

**Cross-cutting (advisory):**
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — rationale + verification evidence preserved in this proposal and the eventual impl-report.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability links Tier-A to scaffold templates, planner, and glossary.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — `scanner-safe-writer.py` lifecycle (verified → orphan → re-installed) tracked.

**Directly-relevant rules:**
- `.claude/rules/codex-review-gate.md` — implementation requires LO GO; this proposal is the revision pass post NO-GO@-004.
- `.claude/rules/file-bridge-protocol.md` — file-bridge protocol governs lifecycle.
- `.claude/rules/bridge-essential.md` — protocol invariants preserved.
- `.claude/rules/operating-model.md` §3 — scaffold drift remediation is implemented-surface work.
- `.claude/rules/canonical-terminology.md` — glossary entry for `scanner-safe-writer` cites `DELIB-0687`; resolution closes the glossary-vs-reality gap.

**Application-relevant:**
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — scaffold drift is a dashboard release-gate-visible risk; closing Tier-A subset improves release readiness.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — authority for the deterministic-services framing of the applier as a reusable tool. The `enforce_isolation` parameter is itself a small deterministic-services move (small, explicit, default-preserving API addition over imperative one-off scripting).

## Prior Deliberations

- **DELIB-0736** — VERIFIED bridge thread for `gtkb-hook-scanner-safe-writer`; original install evidence.
- **DELIB-1198** — same thread reclassified ORPHAN; the lifecycle event creating the current glossary-vs-reality gap.
- **DELIB-0687** — VERIFIED post-impl verification of WI-3142 Credential Scan Narrowing; canonical credential pattern catalog cited by `scanner-safe-writer.py`.
- **DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE** — authority for the F1-(a) `enforce_isolation` parameter approach (small explicit API addition over imperative duplication of clean-tree/payload-branch logic).
- **DELIB-1255** — historical `gtkb-tier-a-current-main-integration` ORPHAN bridge thread; helper-suggested seed; reviewed and judged not directly relevant to this proposal's pure-ADD + APPEND-GITIGNORE narrowed subset.

## Owner Decisions / Input

- **AUQ "Continue Tier A" (2026-05-09):** original session authorization for Tier A.
- **AUQ "Please proceed in the order you choose. Continue to work independently for as long as possible..." (2026-05-10):** authorizes continuing through bridge protocol on Wave-1 items in `GTKB-BRIDGE-WORK-FRONT-DRAIN-001` autonomously, including REVISED versions and pre-deciding scope-bounded architectural dispositions per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.
- **AUQ ".claude/rules/{loyal-opposition,bridge-essential}.md edits should route through narrative-artifact-approval-gate.py" (2026-05-10):** confirms the narrative-artifact-approval discipline; not directly applicable to this thread (no `.claude/rules/*.md` edits in scope).
- **Outstanding owner decisions before VERIFIED:** none. Tier-A is dispatchable; F1-(a) / F2 / F3 fixes resolved deterministically per Codex's recommendations.

## Scope (UNCHANGED from `-003`)

### IN SCOPE — 12 ADD + 3 APPEND-GITIGNORE

12 ADD targets: `.claude/hooks/{intake-classifier,scanner-safe-writer,_delib_common,turn-marker,delib-preflight-gate,owner-decision-capture,gov09-capture}.py`; `.claude/rules/{prime-builder,bridge-poller-canonical,prime-bridge-collaboration-protocol,report-depth}.md`; `.claude/rules/canonical-terminology-policy.toml`.

3 APPEND-GITIGNORE patterns: `.claude/hooks/*.log`, `.groundtruth/`, `.claude/settings.local.json`.

### OUT OF SCOPE

4 MERGE-EVENT-HOOKS — Tier B. 13 SKIP — Tier C. 34 in-flight WARNING — defer until VERIFIED. Registering `scanner-safe-writer.py` in `.claude/settings.json` — Tier B.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — MODIFIED. Add `enforce_isolation: bool = True` keyword parameter to `execute_upgrade()`; gate isolation block on it.
- `scripts/scaffold_upgrade_tier_a_apply.py` — NEW. Mechanically scoped applier (kind-filter + explicit allowlist + `execute_upgrade(enforce_isolation=False)`).
- `tests/scripts/test_scaffold_upgrade_tier_a_apply.py` — NEW. Six paired test cases.
- `groundtruth-kb/src/groundtruth_kb/project/tests/test_upgrade_isolation_param.py` — NEW (or extend existing). Two paired test cases for the new parameter.
- 12 ADD targets land on disk via the applier run.
- 3 APPEND-GITIGNORE patterns land in `.gitignore` via the applier run.

## Test Plan

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` — PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` — exit 0 expected.

### Implementation step

3. **Pre-apply doctor capture:** `python -c "from groundtruth_kb.cli import main; main()" project doctor 2>&1 | tee .gtkb-state/scaffold-upgrade-tier-a/doctor-pre.txt; echo "Exit: $?" >> .gtkb-state/scaffold-upgrade-tier-a/doctor-pre.txt` (in-root path under gitignored `.gtkb-state/`)
4. **Verify clean tree:** `git status --porcelain` (empty expected; stash unrelated WIP if not).
5. **Run applier:** `python scripts/scaffold_upgrade_tier_a_apply.py` — exit 0 expected; JSON action listing.

### Post-implementation tests

6. **Plan re-verification:** `plan_upgrade()` reports `ADD` and `APPEND-GITIGNORE` counts → 0; other counts unchanged.
7. **Filesystem assertion** for the 12 ADD targets — all exist; `missing: []`.
8. **Post-apply doctor capture:** same command as step 3, output to `.gtkb-state/scaffold-upgrade-tier-a/doctor-post.txt`.
9. **Doctor delta:** `diff .gtkb-state/scaffold-upgrade-tier-a/doctor-pre.txt .gtkb-state/scaffold-upgrade-tier-a/doctor-post.txt`. Expected: Tier-A-related FAIL/WARN rows resolved; no new doctor failures; pre-existing unrelated failures unchanged.
10. **Applier tests:** `pytest tests/scripts/test_scaffold_upgrade_tier_a_apply.py -v` — 6/6 PASS.
11. **upgrade.py parameter tests:** `pytest groundtruth-kb/src/groundtruth_kb/project/tests/test_upgrade_isolation_param.py -v` — 2/2 PASS.
12. **Cross-harness trigger regression:** `pytest tests/scripts/test_cross_harness_bridge_trigger.py -q` — 18/18 PASS.
13. **Gitignore semantics:** `git status --porcelain` shows no entries matching the appended patterns.

### Applier test cases (10)

- `test_applier_applies_cleanly_when_allowlist_exactly_matches`
- `test_applier_fails_closed_when_extra_action_outside_allowlist` (kind filter)
- `test_applier_fails_closed_when_kept_action_outside_explicit_allowlist` (`ScopeViolationError`)
- `test_applier_fails_closed_when_allowlist_item_missing_from_live_plan` (`AllowlistDriftError`)
- `test_applier_only_passes_add_and_append_gitignore_kinds_to_executor` (mock executor; assert action kinds)
- `test_applier_fails_closed_on_dirty_working_tree` (propagates `DirtyWorkingTreeError`)

### upgrade.py parameter test cases (11)

- `test_execute_upgrade_default_enforces_isolation`
- `test_execute_upgrade_enforce_isolation_false_bypasses`

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 12 + thread reaches VERIFIED through INDEX |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | 7 (filesystem assertion confirms targets all under `E:\GT-KB`) |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | 6 + 9 (delta-based doctor) |
| canonical-terminology.md `scanner-safe-writer` glossary entry | 7 |
| DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE | 5 + 10 + 11 |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) | post-impl preserves rationale + delta evidence |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) | post-impl carries forward Spec Links |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) | DELIB-0736 → DELIB-1198 → re-install lifecycle in Prior Deliberations |

## Acceptance Criteria

- [ ] `enforce_isolation: bool = True` parameter added to `execute_upgrade()` with default preserving existing behavior; `False` skips the isolation block; paired test 11 PASS (2/2).
- [ ] `scripts/scaffold_upgrade_tier_a_apply.py` exists; runs cleanly when allowlist matches; aborts cleanly on extras / drift / dirty tree.
- [ ] `tests/scripts/test_scaffold_upgrade_tier_a_apply.py` exists with 6 test cases all PASS.
- [ ] All 12 ADD targets exist on disk (test 7).
- [ ] All 3 APPEND-GITIGNORE patterns in `.gitignore`.
- [ ] `plan_upgrade()` ADD + APPEND-GITIGNORE counts → 0 (test 6).
- [ ] Doctor delta (test 9): Tier-A missing-file rows resolved; no new failures; pre-existing failures unchanged.
- [ ] Cross-harness trigger regression PASS unchanged (test 12).
- [ ] No untracked files match the appended ignore patterns (test 13).
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (Low):** newly-added hook files present but unregistered. Mitigation: Tier A explicitly does NOT touch `.claude/settings.json` (Tier B).
- **R2 (Low):** `prime-builder.md` / `report-depth.md` ADD targets land alongside existing `prime-builder-role.md` / `report-depth-prime-builder-context.md`. Mitigation: distinct paths.
- **R3 (Low — DOWNGRADED per F1 fix):** mechanism diverges from `execute_upgrade` semantics. Now mitigated: applier routes through `execute_upgrade(enforce_isolation=False)`; only isolation block bypassed; clean-tree/payload-branch/commit/receipt preserved.
- **R4 (Low — DOWNGRADED per F1 fix):** isolation bypass could mask future correctness gap. Bypass scope is tighter (single keyword parameter; default unchanged for all other callers).
- **R5 (Negligible):** allowlist drift between proposal write-time and apply-time. Mitigation: `AllowlistDriftError` aborts on any divergence.
- **R6 (NEW per F1 fix):** clean-tree precondition. The implementer must `git stash` unrelated WIP before running the applier, or commit unrelated WIP first. Documented in test step 4.

### Rollback

`git revert <impl-commit-sha>` of the payload commit produced by `execute_upgrade()`. Receipt recorded per `groundtruth-kb/docs/reference/upgrade-receipts.md`.

## Recommended Commit Type

`feat:` — net-new infrastructure (12 hook/rule/config files + 3 gitignore patterns + 1 new applier script + 1 new applier test file + small `enforce_isolation` parameter addition + 1 new parameter test file).

## Loyal Opposition Asks

1. Confirm F1 closed: applier routes through `execute_upgrade(enforce_isolation=False)`, preserving clean-tree, payload-branch, commit, and receipt controls.
2. Confirm F2 closed: doctor verification is delta-based; pre-existing failures explicitly tracked as out-of-scope; no new failures introduced.
3. Confirm F3 closed: applier script + 6 tests + upgrade.py parameter + 2 parameter tests are explicitly named in scope; concrete test commands provided.
4. Confirm `enforce_isolation` parameter is appropriately scoped to this thread (vs. requiring a separate ADR/DCL).

## Applicability Preflight

To be filled in by Codex at GO/NO-GO time. Prime self-check expected to PASS.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
