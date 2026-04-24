NO-GO

# GTKB Environment Boundary Baseline Verification Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed report:** `bridge/gtkb-environment-boundary-baseline-implementation-003.md`

## Verdict

NO-GO for verification.

The implementation lands most of the approved Phase 3 baseline cleanly: the
live checker emits zero findings, the release gate invokes it before pytest,
and the focused test suite passes. The remaining blocker is that the compose
read-only policy was approved as a general repo-local source-bind rule, but the
implementation enforces it only for `./src`, `./app`, and `./scripts`.

## Verified Evidence

- Live checker run succeeded with zero findings:
  `python scripts/check_environment_isolation.py --json`
- Focused regression suite succeeded in the live repo:
  `python -m pytest tests/scripts/test_check_environment_isolation.py tests/scripts/test_release_candidate_gate.py -q --tb=short`
  Result: `39 passed in 0.84s`.
- The boundary hardening remains grounded in a live sibling GT-KB checkout.
  A direct root listing of `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
  shows GT-KB governance/runtime surfaces including `.claude`,
  `.groundtruth-chroma`, and `groundtruth.db`.

## Findings

### 1. Blocking: compose read-only enforcement is narrower than the approved policy

**Severity:** High

**Evidence**

- The approved proposal required initial compose checks for "host-bind scope
  and read-only source-mount expectations" and stated that
  `docker-compose.yml` host binds must stay within the app repo while "source
  binds must remain read-only unless a later explicit app-local writable path
  is allowed":
  `bridge/gtkb-environment-boundary-baseline-implementation-001.md:99-103`,
  `bridge/gtkb-environment-boundary-baseline-implementation-001.md:168-170`
- The delivered implementation explicitly narrows that rule to binds starting
  with `./src`, `./app`, or `./scripts`:
  `bridge/gtkb-environment-boundary-baseline-implementation-003.md:82-91`
- The checker hard-codes those three prefixes and only enforces `ro` when one
  of them matches:
  `scripts/check_environment_isolation.py:216`,
  `scripts/check_environment_isolation.py:250-260`
- Test coverage only exercises the `./src` case and does not cover other
  repo-local binds:
  `tests/scripts/test_check_environment_isolation.py:192-201`
- Direct repro against the shipped checker shows a writable repo-local bind
  outside those prefixes is accepted without findings:

```text
$ <temp repo with docker-compose.yml containing "./config:/app/config">
$ python -  # imports scripts/check_environment_isolation.py and runs check_compose()
[]
```

**Impact**

Future repo-local writable binds such as `./config:/app/config` can be added to
`docker-compose.yml` without tripping the Phase 3 checker, so the approved
compose boundary is not fully enforced yet.

## Required Action Items

1. Generalize the read-only compose rule to all repo-local host binds by
   default, or encode an explicit allowlist of writable app-local paths and
   enforce against that list.
2. Add regression coverage showing that a writable repo-local bind outside the
   current prefix list fails the checker.
3. Re-run the live checker and focused pytest suite and submit a revised
   post-implementation report for verification.

## Owner Decision Needed

None.
