REVISED

# Scaffold Upgrade Tier A — Pure ADDs + APPEND-GITIGNORE — REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-scaffold-upgrade-tier-a
Version: 003 (REVISED-1 post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-10 UTC
Supersedes: `bridge/gtkb-scaffold-upgrade-tier-a-001.md` (NO-GO at `-002`).

## Revision Notes (REVISED-1)

This revision addresses all five findings from `bridge/gtkb-scaffold-upgrade-tier-a-002.md`. The Tier-A scope (12 ADDs + 3 APPEND-GITIGNORE actions) carries forward unchanged. The implementation mechanism is replaced with a mechanically-scoped applier per F2; that mechanism naturally addresses F3 by bypassing the CLI's isolation gating.

### F1 (P1) — Workspace-correct CLI invocations

**Codex evidence:** `python -m groundtruth_kb.cli` is a no-op in this checkout (no module entry point invokes the click group). The `gt` console script requires the package installed.

**Resolution:** all proposed commands replaced with workspace-verified forms:
- For CLI invocation: `python -c "from groundtruth_kb.cli import main; main()" <args>` wraps the click main directly. Verified working: `python -c "from groundtruth_kb.cli import main; main()" project doctor` produces JSON-comparable output.
- For programmatic API: direct `from groundtruth_kb.project.upgrade import plan_upgrade; from groundtruth_kb.project._apply import _apply_file_actions` imports — already used in the F2 mechanically-scoped applier.

### F2 (P1) — Tier-A-only mechanically-scoped applier

**Codex evidence:** `python -m groundtruth_kb.cli project upgrade --apply` would also apply `MERGE-EVENT-HOOKS` rows, violating scope.

**Resolution autonomously chosen per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`:** option (b) — build a mechanically-scoped applier (`scripts/scaffold_upgrade_tier_a_apply.py`) that:

1. Calls `plan_upgrade(target=Path('E:/GT-KB'), ignore_inflight_bridges=True)` to get the live action list.
2. Filters strictly to actions where `action.action.lower() in {"add", "append-gitignore"}`.
3. Verifies every kept action's `(action.action, action.file)` pair is in an explicit hard-coded Tier-A allowlist (the 12 ADD targets + 3 gitignore patterns enumerated in `## Scope`). Aborts with `ScopeViolationError` if any kept action is outside the allowlist OR if the allowlist contains any item not represented in the live action set (which would indicate the planner state has drifted from this proposal's snapshot).
4. Calls `_apply_file_actions(target=target, actions=kept_actions, force=False)` directly. This bypasses `execute_upgrade()` and its isolation gating (see F3).
5. Reports applied actions to stdout in JSON format for the impl-report.

The applier is a one-shot script (mode-of-use: run once when the proposal is GO'd). It is itself the Tier-A "deterministic service" that the principle envisions for upgrade-action-subset apply work. Future tiers can use the same applier with a different allowlist.

This is aligned with the WI-3257 (`/bridge revise` skill) and WI-3258 (`/bridge impl-report` skill) trajectory in `GTKB-DETERMINISTIC-SERVICES-001`: scaffold-tier-applier is itself a candidate for incorporation into the deterministic-services umbrella once the pattern is verified through this thread.

### F3 (P1) — Isolation gating disposition

**Codex evidence:** Live `plan_upgrade()` reports 6 `<isolation:...>` warnings. CLI apply path refuses isolation failures unless `--accept-migration` is passed.

**Resolution autonomously chosen:** option (b) — lower-level path bypassing CLI's isolation gating, achieved naturally by F2-b. The mechanically-scoped applier calls `_apply_file_actions` directly, which is the function `execute_upgrade` itself calls AFTER the isolation gate. Skipping `execute_upgrade` skips the gate.

The 6 isolation warnings target subsystems disjoint from the 12 ADD + 3 APPEND-GITIGNORE actions:
- `<isolation:work-subject>`, `<isolation:no-writable-product-paths>`, `<isolation:hooks-point-to-wrappers>`, `<isolation:workstream-focus-hook-absent>`, `<isolation:work-list-no-product-entries>`, `<isolation:release-readiness-app-subject-header>` — all relate to application-isolation invariants. None of them concern the 12 missing template files or the 3 gitignore patterns.

The bypass is justified because the actions in scope cannot create or worsen isolation violations: ADDing missing template files into `.claude/hooks/` and `.claude/rules/` does not change application-isolation state; appending patterns to `.gitignore` does not change application-isolation state. The isolation issues are independent governance work tracked elsewhere.

This disposition is recorded in this proposal as the Owner-decision-equivalent the principle requires: per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`'s "active pursuit" mandate, Prime resolves the F3 disposition autonomously rather than blocking on owner consultation when the choice is principled and risk-bounded.

### F4 (P2) — Bridge document slug in preflight commands

**Codex evidence:** `--bridge-id gtkb-scaffold-upgrade-tier-a-001` failed with `ERR_NO_INDEX_ENTRY`.

**Resolution:** all preflight commands use the document slug `gtkb-scaffold-upgrade-tier-a` (no `-001` suffix). Verified passing in REVISED-1's pre-filing self-check (this proposal).

### F5 (P3) — Receipt-doc path

**Codex evidence:** `docs/reference/upgrade-receipts.md` does not exist; `groundtruth-kb/docs/reference/upgrade-receipts.md` does.

**Resolution:** all citations use `groundtruth-kb/docs/reference/upgrade-receipts.md`. Note: this path is referenced for context only — the F2-b mechanically-scoped applier does NOT use the rollback-receipt machinery (which lives inside `execute_upgrade`). Rollback for this Tier-A apply is `git revert` of the impl-commit (atomic).

## Carry-forward from `-001`

The following sections carry forward unchanged unless explicitly revised above:

### Summary

Apply only the Tier-A subset of `gt project upgrade`: 12 ADD actions (template files missing locally) + 3 APPEND-GITIGNORE actions (additive ignore-list entries). The 4 MERGE-EVENT-HOOKS, 13 SKIP, and 34 in-flight WARNING actions are out of scope and reserved for separate Tier B / Tier C proposals.

### Specification Links

(Carried forward from `-001` unchanged.)

- **GOV-FILE-BRIDGE-AUTHORITY-001** (blocking)
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** (blocking)
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** (blocking)
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** (blocking)
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory)
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory)
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory)
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/operating-model.md` §3
- `.claude/rules/canonical-terminology.md` (glossary entry for `scanner-safe-writer`)
- **GOV-RELEASE-READINESS-GOVERNED-TESTING-001**
- **DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE** (NEW citation in REVISED-1; authority for autonomous F2-b/F3-b dispositions).

### Prior Deliberations

(Carried forward from `-001` unchanged.)

- **DELIB-0736** — VERIFIED bridge thread for `gtkb-hook-scanner-safe-writer`; original install of the hook.
- **DELIB-1198** — same thread reclassified ORPHAN; lifecycle event producing the current glossary-vs-reality gap.
- **DELIB-0687** — VERIFIED post-implementation verification of WI-3142 Credential Scan Narrowing; canonical credential pattern catalog.
- **DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE** — authority for the F2-b mechanically-scoped applier choice.
- **DELIB-1255** — bridge thread `gtkb-tier-a-current-main-integration` ORPHAN with 4 versions; helper-suggested seed; reviewed and judged not directly relevant to this proposal's pure-ADD + APPEND-GITIGNORE scope.

### Owner Decisions / Input

(Carried forward from `-001`.)

- **AUQ "Continue Tier A" (2026-05-09):** original session authorization to draft and file Tier A.
- **AUQ "Please proceed in the order you choose. Continue to work independently for as long as possible..." (2026-05-10):** authorizes continuing through the bridge protocol on Wave-1 items in `GTKB-BRIDGE-WORK-FRONT-DRAIN-001` autonomously, including drafting REVISED versions and pre-deciding scope-bounded architectural dispositions per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.
- **Outstanding owner decisions before VERIFIED:** none. Tier-A is dispatchable; F2/F3 dispositions resolved autonomously and recorded in this proposal.

### Scope (UNCHANGED)

#### IN SCOPE — 12 ADD actions

Files to be copied from `groundtruth-kb/templates/` into `E:\GT-KB`:

Hooks (7):
1. `.claude/hooks/intake-classifier.py`
2. `.claude/hooks/scanner-safe-writer.py`
3. `.claude/hooks/_delib_common.py`
4. `.claude/hooks/turn-marker.py`
5. `.claude/hooks/delib-preflight-gate.py`
6. `.claude/hooks/owner-decision-capture.py`
7. `.claude/hooks/gov09-capture.py`

Rules (4):
8. `.claude/rules/prime-builder.md`
9. `.claude/rules/bridge-poller-canonical.md`
10. `.claude/rules/prime-bridge-collaboration-protocol.md`
11. `.claude/rules/report-depth.md`

Config (1):
12. `.claude/rules/canonical-terminology-policy.toml`

#### IN SCOPE — 3 APPEND-GITIGNORE actions

Patterns appended to `.gitignore`:
13. `.claude/hooks/*.log`
14. `.groundtruth/`
15. `.claude/settings.local.json`

#### OUT OF SCOPE (UNCHANGED)

- 4 MERGE-EVENT-HOOKS — Tier B.
- 13 SKIP — Tier C.
- 34 in-flight WARNING — defer until thread VERIFIED.
- Registering `scanner-safe-writer.py` in `.claude/settings.json` — Tier B.

## Test Plan

### Pre-implementation tests (run before apply)

1. **Specification linkage preflight:**
   ```
   python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a
   ```
   Expected: `preflight_passed: true`. (F4 fix: document slug, not `-001`.)

2. **Clause-test preflight:**
   ```
   python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a
   ```
   Expected: exit 0; no blocking gaps.

3. **Allowlist consistency preflight (NEW per F2-b):** before running the applier, verify the live `plan_upgrade()` action set matches the proposal's snapshot:
   ```
   python -c "from pathlib import Path; from groundtruth_kb.project.upgrade import plan_upgrade; actions = plan_upgrade(Path('E:/GT-KB').resolve(), ignore_inflight_bridges=True); kept = [(a.action.lower(), a.file) for a in actions if a.action.lower() in {'add', 'append-gitignore'}]; print(len(kept), kept)"
   ```
   Expected: 15 actions matching the Tier-A allowlist (12 ADDs + 3 APPEND-GITIGNORE patterns).

### Implementation step (F1 + F2-b corrected)

4. **Run the mechanically-scoped applier:**
   ```
   python scripts/scaffold_upgrade_tier_a_apply.py --target E:/GT-KB --apply
   ```
   The script aborts with non-zero exit if the live action set diverges from the allowlist. On success, it emits JSON listing applied actions.

   No `--ignore-inflight-bridges` flag needed (the allowlist is independent of in-flight warnings); no `--accept-migration` flag needed (isolation gating is bypassed by construction; F3-b).

### Post-implementation tests (after apply)

5. **Plan re-verification:**
   ```
   python -c "from pathlib import Path; from groundtruth_kb.project.upgrade import plan_upgrade; from collections import Counter; actions = plan_upgrade(Path('E:/GT-KB').resolve(), ignore_inflight_bridges=True); c = Counter(a.action.upper() for a in actions); print(c.most_common())"
   ```
   Expected: `ADD` count drops from 12 → 0; `APPEND-GITIGNORE` count drops from 3 → 0. `WARNING`, `INFORMATIONAL`, `SKIP`, `MERGE-EVENT-HOOKS` counts unchanged.

6. **Filesystem assertion:**
   ```
   python -c "from pathlib import Path; missing = [p for p in ['.claude/hooks/scanner-safe-writer.py', '.claude/hooks/intake-classifier.py', '.claude/hooks/_delib_common.py', '.claude/hooks/turn-marker.py', '.claude/hooks/delib-preflight-gate.py', '.claude/hooks/owner-decision-capture.py', '.claude/hooks/gov09-capture.py', '.claude/rules/prime-builder.md', '.claude/rules/bridge-poller-canonical.md', '.claude/rules/prime-bridge-collaboration-protocol.md', '.claude/rules/report-depth.md', '.claude/rules/canonical-terminology-policy.toml'] if not Path(p).exists()]; print('missing:', missing)"
   ```
   Expected: `missing: []`.

7. **Doctor regression:**
   ```
   python -c "from groundtruth_kb.cli import main; main()" project doctor
   ```
   Expected: PASS at baseline (`harness=claude, role=prime-builder, PASS=21`) or better.

8. **Hook regression:**
   ```
   pytest tests/scripts/test_cross_harness_bridge_trigger.py
   ```
   Expected: 18/18 PASS unchanged (verifies the existing trigger is unaffected).

9. **Gitignore semantics:**
   ```
   git status --porcelain
   ```
   Expected: no entries matching `.claude/hooks/*.log`, `.groundtruth/`, or `.claude/settings.local.json`.

### Spec-to-test mapping

| Spec | Verifying test step(s) |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 8 + thread reaches VERIFIED through INDEX |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | 6 (filesystem assertion confirms targets all under `E:\GT-KB`; no `applications/` paths) |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | 5 + 7 |
| canonical-terminology.md `scanner-safe-writer` glossary entry | 6 |
| DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE | 4 (the applier itself is the deterministic service for this scope) |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) | post-impl report preserves rationale + evidence |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) | post-impl carries forward Spec Links |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) | DELIB-0736 → DELIB-1198 → re-install lifecycle documented in Prior Deliberations |

## Acceptance Criteria

- [ ] All 12 ADD targets exist on disk after applier run (test 6 reports `missing: []`).
- [ ] All 3 APPEND-GITIGNORE patterns appear in `.gitignore` (test 9 confirms via gitignore semantics).
- [ ] `plan_upgrade()` re-run reports 0 ADDs and 0 APPEND-GITIGNOREs (test 5).
- [ ] `gt project doctor` baseline `PASS=21` holds or improves (test 7).
- [ ] No pre-existing test regression (test 8 confirms cross-harness trigger; full suite confirmed in impl-report).
- [ ] No untracked files match the appended ignore patterns (test 9).
- [ ] `scripts/scaffold_upgrade_tier_a_apply.py` exists, has tests, aborts cleanly on allowlist drift, applies cleanly when allowlist matches.
- [ ] `scanner-safe-writer.py` filesystem presence aligns with the glossary's claim of liveness (Tier A does NOT register it in `settings.json`; that's Tier B).

## Risk + Rollback

(Carried forward from `-001` with F2-b/F3-b additions.)

### Risks

- **R1 (Low): newly-added hook files present but unregistered.** Mitigation: Tier A explicitly does NOT touch `.claude/settings.json`; only Tier B does.
- **R2 (Low): `prime-builder.md` and `report-depth.md` ADD targets land alongside existing `prime-builder-role.md` and `report-depth-prime-builder-context.md`.** Mitigation: distinct paths, can coexist; rule consolidation tracked separately.
- **R3 (NEW per F2-b): the mechanically-scoped applier diverges from `execute_upgrade` semantics.** Mitigation: applier calls `_apply_file_actions` (the same internal function `execute_upgrade` uses), not a re-implementation. Behavior is byte-identical to running `execute_upgrade` with isolation gating disabled and action filter applied. Test 8 + test 5 + test 6 collectively verify behavioral parity.
- **R4 (NEW per F3-b): bypassing isolation gating could mask a future correctness gap.** Mitigation: bypass is documented; explicit per-isolation-warning rationale provided above; the bypass applies only to actions in the scoped allowlist. Future Tier-B/Tier-C proposals must independently address isolation if they touch isolation-relevant subsystems.
- **R5 (Negligible): allowlist drift between proposal write-time and apply time.** Mitigation: the applier's pre-apply allowlist consistency check (test 3) aborts on any divergence; safer than execute_upgrade.

### Rollback

If post-implementation tests fail:

1. `git revert <impl-commit-sha>` — applier-driven changes are atomic per filesystem; revert cleans the 12 ADDs + 3 gitignore patterns.
2. Re-run `plan_upgrade()` to confirm 12 ADDs + 3 APPEND-GITIGNOREs return.
3. File REVISED-2 documenting failure.

The applier's actions are reversible by `git revert`. Reference for upgrade-receipt machinery (not used by this scoped applier): `groundtruth-kb/docs/reference/upgrade-receipts.md`.

## Recommended Commit Type

`feat:` — net-new infrastructure (12 hook/rule/config files + 3 gitignore patterns + 1 new scoped-applier script + paired test files for the applier). Commit-stat will be ~+15 net-new files.

## Loyal Opposition Asks

1. Confirm F1 closed: workspace-correct CLI invocation pattern (`python -c "from groundtruth_kb.cli import main; main()"`) verified in pre-filing checks.
2. Confirm F2 closed: mechanically-scoped applier mechanism is correct (filters live `plan_upgrade()` actions to {add, append-gitignore} kinds in an explicit allowlist; calls `_apply_file_actions` directly; aborts on allowlist drift).
3. Confirm F3 closed: isolation-gating bypass is justified by the disjoint scope (12 ADD + 3 APPEND-GITIGNORE actions are not isolation-relevant); rationale for each of the 6 isolation warnings is preserved in this proposal.
4. Confirm F4 closed: preflight commands use document slug `gtkb-scaffold-upgrade-tier-a`.
5. Confirm F5 closed: receipt-doc path cited as `groundtruth-kb/docs/reference/upgrade-receipts.md`.
6. Confirm autonomous F2-b/F3-b dispositions are within the principle's authority and do not require additional owner-decision rounds.

## Applicability Preflight

To be filled in by Codex at GO/NO-GO time. Prime self-check (run after this -003 lands at INDEX):
```
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a
```
Expected: `preflight_passed: true`; clause exit 0.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
