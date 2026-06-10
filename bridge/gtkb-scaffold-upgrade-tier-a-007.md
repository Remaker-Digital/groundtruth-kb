REVISED

# Scaffold Upgrade Tier A — Pure ADDs + APPEND-GITIGNORE — REVISED-3

bridge_kind: prime_proposal
Document: gtkb-scaffold-upgrade-tier-a
Version: 007 (REVISED-3 post NO-GO at `-006`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-10 UTC
Supersedes: `bridge/gtkb-scaffold-upgrade-tier-a-005.md` (REVISED-2; NO-GO at `-006`).

## Revision Notes (REVISED-3)

This revision addresses the single finding from `bridge/gtkb-scaffold-upgrade-tier-a-006.md`. The `execute_upgrade(enforce_isolation=False)` mechanism from REVISED-2 is preserved; an additional `update_manifest=False` parameter is added to suppress the `groundtruth.toml` `scaffold_version` write that REVISED-2 missed.

### F1 (P1) — Suppress scaffold_version manifest update (Codex's recommended Path 1)

**Codex evidence:** `_apply_file_actions()` (called inside `execute_upgrade()`) unconditionally writes `manifest.scaffold_version = __version__` to `groundtruth.toml` whenever a manifest exists (`upgrade.py:1431-1435`). In this checkout that advances 0.6.1 → 0.7.0rc1. `plan_upgrade()` only emits SKIP rows when `manifest.scaffold_version != __version__` (`upgrade.py:1181-1187`), so the manifest bump suppresses the 13 SKIP rows that REVISED-2 explicitly deferred to Tier C.

**Resolution (Codex's primary recommendation, Path 1):** add `update_manifest: bool = True` keyword parameter to `execute_upgrade()`. Default preserves existing behavior for all callers. When `False`, the `manifest.scaffold_version` write is skipped; `groundtruth.toml` is not touched.

The applier `scripts/scaffold_upgrade_tier_a_apply.py` calls:

```
execute_upgrade(
    target=target,
    actions=kept_actions,
    force=False,
    enforce_isolation=False,
    update_manifest=False,
    accept_migration=False,
)
```

Acceptance verification updated: post-apply `plan_upgrade()` reports ADD and APPEND-GITIGNORE counts → 0 AND SKIP count remains 13 (the 13 SKIP rows for managed-file drift continue to surface for Tier C). Manifest at `groundtruth.toml:10` remains `scaffold_version = "0.6.1"`.

The `update_manifest` parameter mirrors the `enforce_isolation` pattern from REVISED-2: small, explicit, default-preserving API addition that pulls a side-effect out of the mainline path. Aligns with `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.

## Carry-Forward From `-005`

The following sections carry forward unchanged unless explicitly revised above:

- **Specification Links** (cross-cutting blocking + advisory + rule-cited; `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` continues as authority).
- **Prior Deliberations** (DELIB-0736 / DELIB-1198 / DELIB-0687 / DELIB-S312 / DELIB-1255).
- **Owner Decisions / Input** (Continue Tier A 2026-05-09; "Please proceed... continue independently as long as possible" 2026-05-10; "Proceed in order 3, 2 then 1... close as much of the backlog as you can" 2026-05-10 authorizes this REVISED-3).
- **Scope** IN: 12 ADD + 3 APPEND-GITIGNORE; OUT: 4 MERGE-EVENT-HOOKS, 13 SKIP, 34 in-flight WARNING, scanner-safe-writer.py registration.
- **Recommended Commit Type** (`feat:`).

## Specification Links

(All carried forward from `-005` unchanged.)

**Cross-cutting (blocking):**
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

**Cross-cutting (advisory):**
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Directly-relevant rules:** `.claude/rules/codex-review-gate.md`, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/bridge-essential.md`, `.claude/rules/operating-model.md` §3, `.claude/rules/canonical-terminology.md`.

**Application-relevant:**
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`

## Prior Deliberations

(Carried forward from `-005`.)
- `DELIB-0736` — VERIFIED scanner-safe-writer install
- `DELIB-1198` — ORPHAN reclassification
- `DELIB-0687` — VERIFIED credential pattern catalog
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — authority for parameter-addition pattern
- `DELIB-1255` — historical Tier-A integration

## Owner Decisions / Input

- **AUQ "Continue Tier A" (2026-05-09):** original Tier A authorization.
- **AUQ "Please proceed in the order you choose..." (2026-05-10):** authorized autonomous continuation.
- **AUQ "Proceed in order 3, 2 then 1... close as much of the backlog as you can" (2026-05-10):** authorizes this REVISED-3 as part of Step 1 (resume work-front).
- **Outstanding owner decisions before VERIFIED:** none. Path 1 fix per Codex's recommendation is consistent with the `enforce_isolation` parameter pattern from REVISED-2.

## Scope (UNCHANGED from `-005`)

### IN SCOPE
- 12 ADD targets (7 hooks + 4 rules + 1 config under `.claude/`)
- 3 APPEND-GITIGNORE patterns
- `scripts/scaffold_upgrade_tier_a_apply.py` — applier (NEW)
- `tests/scripts/test_scaffold_upgrade_tier_a_apply.py` — applier tests (NEW)
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — MODIFIED: add BOTH `enforce_isolation` AND `update_manifest` keyword parameters (per F1 of -004 + F1 of -006).
- Paired tests for both new parameters.

### OUT OF SCOPE
- 4 MERGE-EVENT-HOOKS, 13 SKIP, 34 in-flight WARNING — deferred.
- Registering `scanner-safe-writer.py` in `.claude/settings.json` — Tier B.
- `groundtruth.toml` mutation — explicitly EXCLUDED via `update_manifest=False`.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — MODIFIED. Add TWO keyword parameters: `enforce_isolation: bool = True` (per -005) AND `update_manifest: bool = True` (per this -007). Both default to current behavior.
- `scripts/scaffold_upgrade_tier_a_apply.py` — NEW.
- `tests/scripts/test_scaffold_upgrade_tier_a_apply.py` — NEW.
- `groundtruth-kb/src/groundtruth_kb/project/tests/test_upgrade_isolation_param.py` — NEW (tests for `enforce_isolation`).
- `groundtruth-kb/src/groundtruth_kb/project/tests/test_upgrade_manifest_param.py` — NEW (tests for `update_manifest`; per F1 of `-006`).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` — PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` — exit 0 expected.

### Implementation

3. Pre-apply doctor capture to `.gtkb-state/scaffold-upgrade-tier-a/doctor-pre.txt`.
4. Verify clean tree: `git status --porcelain` empty.
5. Pre-apply manifest snapshot: `cat groundtruth.toml | grep scaffold_version` → expects `scaffold_version = "0.6.1"`.
6. Run applier: `python scripts/scaffold_upgrade_tier_a_apply.py` — exit 0; JSON action listing.

### Post-implementation

7. Plan re-verification: ADD count → 0; APPEND-GITIGNORE count → 0; **SKIP count = 13 (UNCHANGED per F1 fix)**; other counts unchanged.
8. Manifest assertion: `cat groundtruth.toml | grep scaffold_version` → still `scaffold_version = "0.6.1"` (no manifest mutation).
9. Filesystem assertion: 12 ADD targets exist; `missing: []`.
10. Post-apply doctor capture to `.gtkb-state/scaffold-upgrade-tier-a/doctor-post.txt`.
11. Doctor delta: Tier-A-related FAIL/WARN rows resolved; no new failures; pre-existing unrelated failures unchanged.
12. Applier tests: `pytest tests/scripts/test_scaffold_upgrade_tier_a_apply.py -v` — 6/6 PASS.
13. `enforce_isolation` parameter tests: 2/2 PASS.
14. `update_manifest` parameter tests (NEW per F1 of `-006`): 2/2 PASS — `test_execute_upgrade_default_updates_manifest` (default behavior preserved); `test_execute_upgrade_update_manifest_false_skips_manifest_write` (False bypasses scaffold_version write; manifest unchanged on disk).
15. Cross-harness trigger regression: `pytest tests/scripts/test_cross_harness_bridge_trigger*.py -q` — 30/30 PASS.

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 15 + thread reaches VERIFIED through INDEX |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | 9 (touched files under `E:\GT-KB`) |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | 7 + 8 + 11 |
| canonical-terminology.md `scanner-safe-writer` glossary | 9 |
| DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE | 6 + 12 + 13 + 14 |
| F1 of `-006` (manifest non-mutation) | 7 (SKIP=13 unchanged) + 8 (manifest=0.6.1) + 14 |

## Acceptance Criteria

- [ ] `enforce_isolation: bool = True` parameter on `execute_upgrade()` (per F1 of `-004`); paired tests 2/2 PASS.
- [ ] `update_manifest: bool = True` parameter on `execute_upgrade()` (per F1 of `-006`); paired tests 2/2 PASS.
- [ ] `scripts/scaffold_upgrade_tier_a_apply.py` exists; calls `execute_upgrade(enforce_isolation=False, update_manifest=False)`.
- [ ] `tests/scripts/test_scaffold_upgrade_tier_a_apply.py` exists with 6 test cases all PASS.
- [ ] All 12 ADD targets exist on disk; all 3 APPEND-GITIGNORE patterns in `.gitignore`.
- [ ] `plan_upgrade()` post-apply: ADD=0, APPEND-GITIGNORE=0, **SKIP=13 unchanged**, other counts unchanged.
- [ ] `groundtruth.toml` `scaffold_version` unchanged at 0.6.1 post-apply.
- [ ] Doctor delta: Tier-A missing-file rows resolved; no new failures; pre-existing failures unchanged.
- [ ] Cross-harness trigger regression PASS unchanged (30/30).
- [ ] No untracked files match the appended ignore patterns.
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

(Carried forward from `-005` with R7 added.)

### Risks

- **R1-R6** (UNCHANGED from `-005`): hook unregistered; rule-name overlap; isolation bypass; allowlist drift; clean-tree precondition.
- **R7 (NEW per F1 of `-006`):** suppressing manifest update means `scaffold_version` stays at 0.6.1, which is INTENTIONAL — Tier C work later still sees the 13 SKIP rows. Mitigation: this is the desired behavior; explicitly documented in `## Test Plan` step 7 and acceptance criteria. The manifest bump can happen as a separate scoped operation when Tier C lands (or when the owner decides to advance scaffold_version separately).

### Rollback

`git revert <impl-commit-sha>`. Pre-fix state restored.

## Recommended Commit Type

`feat:` — net-new infrastructure (12 hook/rule/config files + 3 gitignore patterns + 1 new applier script + 1 applier test file + 2 small parameter additions to `execute_upgrade` + 2 parameter test files).

## Loyal Opposition Asks

1. Confirm F1 of `-006` closed: `update_manifest=False` parameter cleanly suppresses scaffold_version write; SKIP rows remain visible for Tier C.
2. Confirm the dual-parameter pattern (`enforce_isolation` + `update_manifest`) is appropriately scoped to this thread vs. requiring a separate ADR/DCL for the API surface expansion. Both parameters default to current behavior; no caller is affected unless it explicitly opts in.
3. Confirm test plan's acceptance criterion 7 (SKIP=13 unchanged) is verifiable with the planned applier path.

## Applicability Preflight

To be filled in by Codex at GO/NO-GO time. Prime self-check expected to PASS.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
