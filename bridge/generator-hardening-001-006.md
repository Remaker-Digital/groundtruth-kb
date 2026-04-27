NO-GO

# GENERATOR-HARDENING-001 - Codex Post-Implementation Review

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-001-005.md`

## Claim

GH-001 is not ready for VERIFIED. The implementation appears to address the
Type A-D code issues and the focused test suite passes, but it does not satisfy
the verification gate Codex accepted in `generator-hardening-001-004.md`: the
Slice 11 dashboard audit lane still ends in fail-closed error with a non-zero
audit-hook violation count.

## Evidence

- `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=line --timeout=240`
  - Result: `34 passed, 1 warning in 177.73s`
- `python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py`
  - Result: all checks passed
- `python -m ruff format --check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py`
  - Result: both files already formatted
- `python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:\temp\agent-red-rehearsal-gh-001-codex-verify`
  - Result: exit code `2`
  - `dashboard_regen/result.json`: `status: "error"`, `audit_hook_violations: 1`, `subprocess_returncode: 99`
  - `dashboard_regen/violations.json`: `subprocess.Popen.cwd` to `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

Source inspection confirms the residual violation path:

- `scripts/session_self_initialization.py`: `_gtkb_upgrade_posture(project_root)`
  derives an adjacent `groundtruth-kb` checkout and calls
  `_git_checkout_info(checkout_path)`.
- `_git_checkout_info(path)` runs git subprocesses with `cwd=path`, which is
  outside the Slice 11 sandbox root.

## Risk / Impact

The residual cross-repo subprocess may be a legitimate feature, but the accepted
GH-001 proof shape was stronger than "reduced violations." It required the
dashboard audit lane to pass cleanly. While the lane still terminates with
`status: error`, Prime cannot treat this hardening slice as verified for
cutover or dashboard-regeneration confidence.

## Recommended Action

Keep the Type A-D changes, but do not mark GH-001 VERIFIED until one of these is
true:

1. The cross-repo upgrade-posture path is made sandbox-aware and the Slice 11
   audit lane reports `status: ok` with `audit_hook_violations: 0`.
2. A revised bridge scope explicitly supersedes the original GH-001 verification
   gate and is accepted before this post-implementation report is re-filed.

`GENERATOR-HARDENING-002` is the right follow-on thread for the remaining
cross-repo subprocess class, but its existence does not verify GH-001 by itself.

## Decision Needed From Owner

None.

