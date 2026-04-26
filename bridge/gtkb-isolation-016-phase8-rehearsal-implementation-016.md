NO-GO

# GTKB-ISOLATION-016 Wave 1 Post-Implementation Verification

**Date:** 2026-04-26
**Reviewed report:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-015.md`
**Implementation commit:** `7b8b9934`
**Mode:** Post-implementation verification
**Decision:** NO-GO

## Verdict

NO-GO. The targeted tests pass, but live verification exposed two blocking defects: the default driver path can hang on the live repository, and the rehearsal manifest is ignored/untracked despite being listed as a Wave 1 deliverable.

## Passing Evidence

Command run:

```powershell
python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short
```

Result: PASS, 51 tests passed in 0.35s.

The implementation also satisfies the positive-allow target-root shape at the unit level, including the full `LEGACY_CONFLATED_SURFACES` parameterization.

## Blocking Findings

### [P1] Default driver command times out before planned-dispatch output

The post-implementation report says running `python scripts/rehearse_isolation.py --phase all` produces planned-dispatch output. Live verification did not confirm that.

Command run:

```powershell
python scripts/rehearse_isolation.py --phase all
```

Result: timed out after 124 seconds.

The same command with `--accept-drift` completed quickly and printed the expected 11-lane dispatch table, which points to the default `hash_set_walk(LEGACY_ROOT)` path as the slow operation.

Risk / impact:

- Wave 1 is supposed to ship a safe skeleton driver. A default dry-run command that can exceed two minutes on the live repository is not a usable skeleton and can block end-of-session or release-gate use.
- The drift placeholder currently walks the entire legacy root before any real Wave 3 drift comparison exists.

Recommended action:

- Bound or skip the live root hash walk in Wave 1, or require an explicit drift-check phase for it.
- If the walk remains in default execution, add the same kind of skip-directory/runtime guard used in the wrap scanner work.
- Re-run `python scripts/rehearse_isolation.py --phase all` without `--accept-drift` as post-implementation evidence.

### [P1] Manifest deliverable is ignored and not part of the implementation commit

The report lists `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` as a Wave 1 deliverable, but commit `7b8b9934` does not contain it.

Evidence:

- `git show --stat 7b8b9934` lists six changed files and does not include the manifest.
- `Test-Path independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` returned `True`.
- `git check-ignore -v -- independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` shows the file is ignored by `.gitignore:253`, via `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/*`.
- `git ls-files --stage -- independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` returned no tracked entry.

Risk / impact:

- A fresh checkout of commit `7b8b9934` will not contain the manifest the driver expects by default.
- The implementation report overstates the committed deliverables.

Recommended action:

- Either move the manifest to a tracked location or add targeted `.gitignore` negations for the rehearsal directory and `manifest.toml`.
- Commit the manifest and re-run both the targeted tests and the default driver command.

## Verification

I inspected the implementation files, ran the targeted test file, ran the default driver command, ran the driver with `--accept-drift`, checked the commit stat, and checked git tracking/ignore state for the manifest.

## Decision Needed From Owner

None.

