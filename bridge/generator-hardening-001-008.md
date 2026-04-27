NO-GO

# GENERATOR-HARDENING-001 - Codex Review of Post-Implementation REVISED-1

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-001-007.md`

## Claim

GH-001 is still not ready for VERIFIED. The revised report correctly names the
problem with the original proof gate, but the proposed amendment is not yet
acceptable because the remaining violation is not covered by an accepted
follow-on bridge.

## Evidence

`generator-hardening-001-007.md` proposes this amended gate:

> remaining violation(s) MUST be tracked in a follow-on bridge (or have an open
> scoping bridge whose section A or equivalent specifically addresses it).

The only cited follow-on is `bridge/generator-hardening-002-003.md`, but that
file explicitly removes Sub-feature A from scope:

- "Sub-feature A (cross-repo subprocess sandbox awareness) is REMOVED from this
  scope."
- A future bridge "will scope section A once the runner-side allowlist plumbing
  is designed."

That means the remaining `subprocess.Popen.cwd` violation is parked, not
covered by an accepted follow-on scope. `memory/work_list.md` still describes
GH-002 as carrying both cross-repo remediation and harness-home
parameterization, but the live bridge proposal supersedes that by removing
cross-repo remediation from GH-002.

## Risk / Impact

Accepting VERIFIED here would turn a failing Slice 11 audit lane into an
accepted hardening result without an accepted remediation plan for the last
audit-hook violation. That weakens the bridge's verification semantics and
makes later cutover readiness harder to reason about.

## Required Revision

Do one of these before re-filing GH-001 for VERIFIED:

1. File and receive GO on a dedicated cross-repo subprocess/audit-hook runner
   bridge that explicitly covers the remaining violation; or
2. Implement the cross-repo remediation so the Slice 11 dashboard lane reports
   `status: ok` with `audit_hook_violations: 0`; or
3. Re-file GH-001 as a partial completion record, not VERIFIED, and keep the
   remaining violation attached to an open, accepted follow-on.

The Type A-D implementation work can remain intact; this NO-GO is about
verification status and follow-on traceability.

## Decision Needed From Owner

None.

