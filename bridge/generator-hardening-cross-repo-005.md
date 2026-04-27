GO

# GENERATOR-HARDENING-CROSS-REPO - Codex Review of REVISED-1

**Status:** GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-cross-repo-004.md`

## Claim

GO for the degrade-only revision.

This revision satisfies the owner root-boundary directive by removing the
outside-root allowlist entirely. It keeps the Slice 11 goal intact by making the
dashboard generator degrade upgrade-posture inspection when the discovered
checkout is outside `E:\GT-KB`, rather than spawning a cross-root git
subprocess.

## Evidence

The revised scope:

- changes only in-root files under `E:\GT-KB`;
- adds no runner or lane allowlist for outside paths;
- does not update `.claude/settings.json` to add an outside-root path;
- expects `audit_hook_violations: 0` because no out-of-root subprocess fires;
- uses an explicit degraded record: `error: "checkout_outside_project_root"`.

That matches `.claude/rules/project-root-boundary.md`.

## GO Conditions

Implementation must preserve these constraints:

1. No allowlist or fallback may permit live inspection outside `E:\GT-KB`.
2. The degraded record must be rendered gracefully by the dashboard.
3. The test must prove no git subprocess is spawned for a checkout path outside
   `project_root`.
4. The Slice 11 lane re-run must show `status: ok` and
   `audit_hook_violations: 0`.

## Decision Needed From Owner

None.

