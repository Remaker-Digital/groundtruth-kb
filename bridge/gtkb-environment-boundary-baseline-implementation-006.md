NO-GO

# GTKB Environment Boundary Baseline Verification Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed report:** `bridge/gtkb-environment-boundary-baseline-implementation-005.md`

## Verdict

NO-GO for verification.

Revision 2 fixes the prior `./config` regression from `-004`, and the focused
checker/test lane is green. The remaining blocker is that the compose checker
still does not enforce the approved host-bind boundary on this Windows repo:
a drive-letter absolute host bind such as `C:/temp/config:/app/config:ro`
passes with zero findings, so absolute binds outside the app repo are not
fully rejected yet.

## Verified Evidence

- Live checker run succeeded with zero findings on the current repo:
  `python scripts/check_environment_isolation.py --json`
- Focused regression suite succeeded in the live repo:
  `python -m pytest tests/scripts/test_check_environment_isolation.py tests/scripts/test_release_candidate_gate.py -q --tb=short`
  Result: `41 passed in 0.79s`.
- The sibling GT-KB checkout still contains the governance/runtime surfaces
  this Phase 3 boundary is meant to keep out of app-local build/runtime paths;
  a direct root listing of
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` shows entries including
  `.claude`, `.groundtruth-chroma`, and `groundtruth.db`.

## Findings

### 1. Blocking: Windows drive-letter absolute host binds bypass the compose boundary check

**Severity:** High

**Evidence**

- The approved proposal requires initial compose checks for "Compose host-bind
  scope and read-only source-mount expectations" and states that
  `docker-compose.yml` host bind mounts must stay within the app repo while
  source binds remain read-only unless a later explicit writable path is
  allowed:
  `bridge/gtkb-environment-boundary-baseline-implementation-001.md:99-103`,
  `bridge/gtkb-environment-boundary-baseline-implementation-001.md:168-170`
- The revised report claims the checker now runs read-only enforcement for all
  repo-local binds and that absolute paths are still handled by the existing
  compose host-path/out-of-app logic:
  `bridge/gtkb-environment-boundary-baseline-implementation-005.md:24-34`
- The compose parser still splits volume specs on `:` using a regex that cannot
  represent Windows drive-letter binds, and `_is_host_path()` only treats
  values starting with `.` or `/` or containing `/` as host paths:
  `scripts/check_environment_isolation.py:211-217`,
  `scripts/check_environment_isolation.py:220-263`
- The new regression tests added in Revision 2 cover `./config:/app/config`
  and `./config:/app/config:ro`, but there is still no coverage for a Windows
  absolute host bind form:
  `tests/scripts/test_check_environment_isolation.py:204-226`
- Direct repro on this Windows workspace shows the gap is real. I created a
  temporary root whose `docker-compose.yml` contained
  `C:/temp/config:/app/config:ro` and ran
  `python scripts/check_environment_isolation.py --json --root <tempdir>`.
  Result: `findings: []` and exit code `0`.

**Impact**

On Windows, a future absolute host bind outside the app repo can be added to
`docker-compose.yml` without triggering `COMPOSE_HOST_BIND_OUT_OF_APP`, so the
approved Phase 3 compose boundary is not fully enforced in the current
execution environment.

## Required Action Items

1. Update compose volume parsing / host-path detection so Windows drive-letter
   absolute host binds are recognized as host binds and rejected by
   `COMPOSE_HOST_BIND_OUT_OF_APP`.
2. Add focused regression coverage for Windows absolute host bind forms
   (`C:/...` at minimum, plus any additional form the checker intends to
   support).
3. Re-run the live checker and focused pytest suite and submit a revised
   post-implementation report for verification.

## Owner Decision Needed

None.
