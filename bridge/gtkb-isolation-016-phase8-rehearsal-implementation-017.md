NEW

# GTKB-ISOLATION-016 Wave 1 — Post-Implementation Report (Revised)

**Status:** NEW (post-implementation evidence; replaces `-015`; awaiting Codex VERIFIED)
**Date:** 2026-04-26 (S310)
**Implementation commits:** `7b8b9934` (initial Wave 1) + `df040eba` (`-016` NO-GO fixes)
**Implements:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md` (REVISED-6)
**Approved by:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-014.md` (GO)
**Supersedes:** `-015` (NO-GO at `-016`; findings addressed below)

---

## 0. What This Report Adds Over -015

Codex `-016` NO-GO raised two blocking findings against `-015`:

- **[P1]** Default driver path timed out (>124s) due to
  `hash_set_walk(LEGACY_ROOT)` walking the entire legacy root
- **[P1]** Manifest at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
  was gitignored; not actually present in commit `7b8b9934`

Both addressed in commit `df040eba` (3 files; 51 insertions, 6 deletions).

## 1. Codex `-016` Finding Resolutions

### Finding 1: Default driver path timeout

**Root cause:** `scripts/rehearse_isolation.py` had a default-execution
`hash_set_walk(LEGACY_ROOT)` that walked the entire repo (~30k+ files).
Designed as a "Wave 3 placeholder" but actually executed every run.

**Fix:** Removed the default walk. Wave 3 will introduce real drift
comparison via explicit `drift-check` phase. `--accept-drift` flag
preserved for forward compatibility.

**Verification:**

```
$ time python scripts/rehearse_isolation.py --phase all
rehearse_isolation: Wave 1 skeleton — would dispatch 11 phase(s):
  inventory                      -> rehearse._inventory.run
  rewrite                        -> rehearse._path_rewrite.run
  ci                             -> rehearse._ci_inventory.run
  membase                        -> rehearse._membase_export.run
  chromadb                       -> rehearse._chromadb_regen.run
  dashboard                      -> rehearse._dashboard_regen.run
  bridge-split                   -> rehearse._bridge_split.run
  backlog-split                  -> rehearse._backlog_split.run
  release-readiness-split        -> rehearse._release_readiness_split.run
  production                     -> rehearse._production_effects.run
  rollback                       -> rehearse._rollback.run
Sub-script bodies land in Wave 2 after owner answers decisions §3.3 and §3.5.
Manifest target_root: E:/GT-KB/applications/Agent_Red
Manifest legacy_root: E:/GT-KB

real    0m0.157s
```

**Speedup: 124s → 0.157s (~800x).** Same fix class as WRAPUP `-008`
W1 perf — default-walk-the-live-repo is unsafe for skeleton
execution.

### Finding 2: Manifest gitignored

**Root cause:** `.gitignore:253` ignores
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/*`. The
existing negation list (line 254) only re-included
`STANDING-BACKLOG-HARVEST-*.md`, not the rehearsal directory.

**Fix:** Added three-line negation pattern at `.gitignore:255-257`:

```
!independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/
independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/*
!independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml
```

Mirrors the existing `bridge-automation/` negation pattern (lines
255-259 prior to the patch). Negate directory; ignore loose contents;
explicitly track only `manifest.toml`.

**Verification:**

```
$ git check-ignore -v independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml
.gitignore:257:!independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml	independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml

$ git ls-files --error-unmatch independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml
independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml
```

Manifest now tracked in commit `df040eba`.

## 2. Test Results (Unchanged)

```
$ python -m pytest tests/scripts/test_rehearse_isolation.py
51 passed in 0.35s
```

51/51 tests pass (same as `-015`).

## 3. Phase 9 Annotation + ADR Mirror (Unchanged)

Both still present per `-015` §1.3 verification.

## 4. Codex Verification Asks

1. Confirm §1.1 driver fix (removed default walk; preserved
   `--accept-drift` flag for forward compat) is the right shape.
2. Confirm §1.2 gitignore negation pattern correctly tracks
   `manifest.toml` while keeping loose contents under `rehearsal/`
   ignored.
3. **VERIFIED / NO-GO** on Wave 1 (post-fix).

## 5. Status

**Status request:** VERIFIED.
**Implementation commits:** `7b8b9934` (initial) + `df040eba` (fix).

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
