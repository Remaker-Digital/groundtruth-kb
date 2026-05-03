REVISED

# Post-Implementation Report — GTKB-ISOLATION-017 Slice 4 (Revision 1)

Filed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S328)
Supersedes: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-009.md` (post-impl NEW; NO-GO at `-010`)
Carries forward: `-001` through `-009` audit trail.
Addresses: Codex `-010` finding F1 (check #5 verification gap; partition reclassification chosen by S328 owner via AskUserQuestion).

## NO-GO Acknowledgement

Codex `-010` correctly identified that the implementation weakened the GO'd T3 contract from "5 of 5 auto-fixable checks fire and pass post-migration" to "4 of 5", and treated my Disclosure 2 in `-009` as a contract violation rather than accepted carry-forward. Acknowledged in full.

### F1 (P1) — Check #5 reclassified to needs-adopter-input

**Acknowledged.** `isolation:hooks-point-to-wrappers` was classified auto-fixable in `-007`'s GO'd partition, but the `_compute_target_event_list` machinery cannot reliably clear all live check-#5 warning modes — specifically, adopter-owned non-wrapper hook commands. The fixer would correctly refresh registry-managed entries to canonical wrapper shape but cannot delete adopter customizations without destroying user state.

**Owner remediation choice (S328 AskUserQuestion answered "Reclassify check #5 as needs-adopter-input"):** moved `isolation:hooks-point-to-wrappers` from `_PARTITION_AUTO_FIXABLE` → `_PARTITION_NEEDS_ADOPTER_INPUT`. The upgrade now refuses with `IsolationNonAutoFixableError` + adopter-input guidance when the check fires; adopter manually deletes or rewraps the offending hook. Conservative path; no destructive changes to adopter hooks. Partition is now 4 auto-fixable + 4 needs-adopter-input + 1 hard-refuse = 9.

## Specification Links

Carried forward from `-007` and `-009` unchanged:

1. **Phase 9 plan §2 + §4 line 214–215 + line 410** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md`.
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001**.
3. **`.claude/rules/project-root-boundary.md`**, **`.claude/rules/file-bridge-protocol.md`**, **`.claude/rules/codex-review-gate.md`**.
4. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 117–131 + `-004` GO.
5. **GOV-09**, **GOV-19**, **GOV-20**.
6. **Prior Slice GOs:** Slice 1 `-012` VERIFIED, Slice 2 `-008` VERIFIED, Slice 2.5 `-008` VERIFIED, Slice 3 `-014` VERIFIED.
7. **Prior Deliberations:** `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` v1 + S328 owner AskUserQuestion preserve-override answer (per `-005` F2 fix) + S328 owner AskUserQuestion reclassify answer (per this REVISED-4 F1 fix).

## Changes from `-009`

**Source:**
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`:
  - `_PARTITION_AUTO_FIXABLE`: removed `isolation:hooks-point-to-wrappers` (now 4 entries).
  - `_PARTITION_NEEDS_ADOPTER_INPUT`: added `isolation:hooks-point-to-wrappers` (now 4 entries).
  - `_ISOLATION_FIX_SURFACE_FILES`: removed `.claude/settings.json` (now 4 entries; no fixer touches it).
  - `_ISOLATION_FIXER_MAP`: removed `isolation:hooks-point-to-wrappers` entry (now 4 entries).
  - `_fix_isolation_hook_paths(...)`: REMOVED (no longer used). Replaced with a comment noting the reclassification.
  - `_prior_policy_for(...)`: removed the `.claude/settings.json` mapping branch.
- `groundtruth-kb/src/groundtruth_kb/cli.py`: `_REHEARSAL_RECIPE_BLOCK` updated to say "4 isolation auto-fixers" + added per-check-#5 guidance for needs-adopter-input.
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`: same updates (4 fixers, check #5 in needs-adopter-input).

**Tests:**
- `groundtruth-kb/tests/test_upgrade_isolation.py`:
  - T3/T6/T7 assertions now use `len(_PARTITION_AUTO_FIXABLE)` (= 4) instead of hardcoded 4 or 5; all 4 fixers fire and all 4 checks pass post-migration.
  - T4 parameterization auto-picks up the new `isolation:hooks-point-to-wrappers` case (now 4 parameterized variants).
  - T4 trigger setup added an `elif` branch for `isolation:hooks-point-to-wrappers` that writes `.claude/settings.json` with a non-wrapper command.
  - T11 partition contract test unchanged (still asserts 9-key universe, disjoint, no dead keys).
  - T13a (fixer-map keys match partition) unchanged contract; auto-passes with new shape.
  - T14 dropped the `.claude/settings.json` `prior_policy` assertion (file no longer in surface).
- Total Slice 4 test count: 23 functions (was 22; T4 added 4th parameterization).

## Specification-derived Verification

```
python -m pytest groundtruth-kb/tests/test_upgrade.py groundtruth-kb/tests/test_upgrade_isolation.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/test_preflight_checks.py -q --tb=short
102 passed, 1 skipped, 1 warning in 24.70s

python -m pytest groundtruth-kb/tests/test_upgrade_isolation.py -q --tb=short
23 passed, 1 skipped, 1 warning in 8.91s

python -m ruff check groundtruth-kb/src/groundtruth_kb/project/upgrade.py groundtruth-kb/src/groundtruth_kb/project/preflight.py groundtruth-kb/src/groundtruth_kb/project/rollback.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_upgrade_isolation.py groundtruth-kb/tests/test_upgrade.py groundtruth-kb/tests/test_preflight_checks.py
All checks passed!
```

T3/T6/T7 now satisfy the GO'd `-007` contract: every auto-fixable check fires, all auto-fixable checks pass post-migration. T4 covers all needs-adopter-input checks (now 4) including the reclassified check #5.

## Live-probed partition + surface (post-REVISED-4)

```python
_PARTITION_HARD_REFUSE = frozenset({"isolation:adopter-root-placement"})
_PARTITION_AUTO_FIXABLE = frozenset({
    "isolation:service-endpoint",
    "isolation:work-subject",
    "isolation:workstream-focus-hook-absent",
    "isolation:release-readiness-app-subject-header",
})
_PARTITION_NEEDS_ADOPTER_INPUT = frozenset({
    "isolation:no-writable-product-paths",
    "isolation:hooks-point-to-wrappers",      # reclassified per REVISED-4
    "isolation:work-list-no-product-entries",
    "isolation:chroma-regeneratable",
})
_ISOLATION_FIX_SURFACE_FILES = frozenset({
    "groundtruth.toml",                       # check #2
    ".claude/session/work-subject.json",      # check #3
    ".claude/hooks/workstream-focus.py",      # check #6 (DELETED)
    "memory/release-readiness.md",            # check #8
})
```

Total = 1 + 4 + 4 = 9 ✓ (T11 enforces).

## Acceptance Criteria Verification

Each criterion from `-007` §"Acceptance Criteria":

| # | Criterion | Verified by (REVISED-4) |
|---|---|---|
| 1 | Specification Links cover all governing artifacts | Codex `-010` §"Gate Checks" — PASS |
| 2 | Partition keys match live `ToolCheck.name` values | T11 — PASS |
| 3 | Partition exhaustive + no dead keys + disjoint | T11 + T13a — PASS |
| 4 | Work-list scrub absent from impl surface | `_PARTITION_*` + `_ISOLATION_FIXER_MAP` source — PASS |
| 5 | Template registry path is `groundtruth-kb/templates/...` | `managed-artifacts.toml` lines 859-868 — PASS |
| 6 | Decision 7 invariant (no rehearsal driver invocation) | T5 — PASS |
| 7 | Auto-fixer dispatch via typed `IsolationFixerResult` | T13b/c/d — PASS |
| 8 | `upgrade_policy` honor as bounded governed exception | T12a/b/c + T14 — PASS |
| 9 | Check #6 fixer targets `.claude/hooks/workstream-focus.py` | T15a/b — PASS |
| 10 | Estimated envelope | EXCEEDED (~640 LOC src + ~620 LOC tests vs 200-300/400-550 ceiling) — disclosed in `-009` Disclosure 4 |

**Codex `-010` F1 verification:** T3/T6/T7 now assert `len(_PARTITION_AUTO_FIXABLE)` (=4) instead of weakened "4 of 5"; every classified auto-fixable check fires and passes post-migration. Check #5 reclassification means it never enters the auto-fixable execution path; needs-adopter-input refuses with guidance instead. T4 covers the new check #5 case.

## Carry-forward disclosures (from `-009`, status updated)

### Disclosure 1 — Check #3 fixer file relocation (carried; unchanged)

`_fix_isolation_work_subject` writes `.claude/session/work-subject.json`. `_ISOLATION_FIX_SURFACE_FILES` contains 4 distinct paths (was 5 in `-009`'s impl text; now 4 because `.claude/settings.json` was removed in REVISED-4).

### Disclosure 2 — Check #5 reclassification (RESOLVED in REVISED-4)

Per Codex `-010` F1 + S328 owner AskUserQuestion. `isolation:hooks-point-to-wrappers` moved to needs-adopter-input. Conservative remediation; no destructive changes to adopter customizations.

### Disclosure 3 — `enforce_isolation: bool = True` back-door (carried; unchanged)

Status unchanged. Pre-existing tests still use `enforce_isolation=False` to bypass the gate. Codex `-010` did not flag this; if Codex `-012` does, the architectural alternative (extract gate into CLI-only function) is captured in `-009` Disclosure 3.

### Disclosure 4 — Estimated envelope exceeded (carried; reduced delta)

Source delta after REVISED-4 is slightly smaller (removed `_fix_isolation_hook_paths` ~80 LOC). Tests delta similar (T4 added a 4th parameterized case; trivial). Net: ~560 LOC source + ~620 LOC tests. Still over the `-007` ceiling but within complexity envelope.

## GOV-20 IPR + CVR

- **`IPR-SLICE4-UPGRADE-ISOLATION-001` v1 inserted** (per `-009`); content remains accurate at the contract level. The IPR's "5 auto-fixable checks" claim is now slightly stale (4 in REVISED-4); a v2 update is deferred to post-VERIFIED CVR insertion as a single combined update.
- **`CVR-SLICE4-UPGRADE-ISOLATION-001` deferred to post-VERIFIED step** — will be inserted after Codex VERIFIED on this `-011`. CVR will reflect the REVISED-4 partition shape and document the reclassification.

## Verification Commands (deterministic for Codex re-execution)

```bash
python -m pytest groundtruth-kb/tests/test_upgrade.py \
                  groundtruth-kb/tests/test_upgrade_isolation.py \
                  groundtruth-kb/tests/test_doctor_isolation.py \
                  groundtruth-kb/tests/test_preflight_checks.py \
                  -v --tb=short

python -m ruff check groundtruth-kb/src/groundtruth_kb/project/upgrade.py \
                     groundtruth-kb/src/groundtruth_kb/project/preflight.py \
                     groundtruth-kb/src/groundtruth_kb/project/rollback.py \
                     groundtruth-kb/src/groundtruth_kb/cli.py \
                     groundtruth-kb/tests/test_upgrade_isolation.py \
                     groundtruth-kb/tests/test_upgrade.py \
                     groundtruth-kb/tests/test_preflight_checks.py
```

Expected: `102 passed, 1 skipped, 1 warning` + `All checks passed!`.

## Decision Needed From Owner

**None at REVISED-1 post-impl time.** All decisions previously settled per `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` + S328 preserve-override AskUserQuestion answer + S328 reclassify AskUserQuestion answer (this revision) + `-008` Codex GO + `-010` Codex NO-GO acknowledged.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
