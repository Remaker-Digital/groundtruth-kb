NO-GO

# GENERATOR-HARDENING-CROSS-REPO - Codex Superseding Review

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-cross-repo-001.md`
**Supersedes:** `bridge/generator-hardening-cross-repo-002.md`

## Claim

The prior GO is withdrawn. The proposed cross-repo allowlist design conflicts
with the owner's explicit project-boundary directive:

> All active files for the GT-KB project MUST be within the `E:\GT-KB`
> directory. There should not be any live artifacts for GT-KB that are outside
> this root directory. There should not be any Agent Red files which are outside
> the `E:\GT-KB\applications\Agent_Red` directory. This is non-negotiable.

## Evidence

`generator-hardening-cross-repo-001.md` proposes allowing the dashboard
generator and audit-hook runner to inspect an upstream checkout such as:

`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

That is outside `E:\GT-KB`. Under the owner directive, it cannot be treated as a
live GT-KB artifact location or an allowed active dependency for GT-KB runtime
or verification.

## Risk / Impact

If this scope proceeded as previously GO'd, the audit lane would normalize an
outside-root live dependency. That would directly undermine the root isolation
boundary the owner has now made non-negotiable.

## Required Revision

Revise the design so the Slice 11 dashboard lane reaches
`audit_hook_violations: 0` without allowlisting any path outside `E:\GT-KB`.
Acceptable shapes include:

1. Always degrade upgrade-posture inspection when the discovered upstream
   checkout is outside `E:\GT-KB`.
2. Move any required GT-KB upstream checkout/artifact inside `E:\GT-KB` and
   allow only that in-root path.
3. Remove live cross-repo git inspection from the dashboard generator and
   replace it with an in-root manifest or package metadata artifact.

Any future allowlist must be constrained to resolved paths under `E:\GT-KB`.
Agent Red-specific active paths must be constrained under
`E:\GT-KB\applications\Agent_Red`.

## Decision Needed From Owner

None. The owner directive is explicit and binding.

