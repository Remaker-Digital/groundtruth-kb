NO-GO

# GENERATOR-HARDENING-002 - Codex Scoping Review

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-002-001.md`

## Claim

GH-002 is directionally correct, but the combined scope is not ready for GO as
written. Sub-feature B is acceptable in principle. Sub-feature A needs revision
because its proposed "with allowlist" audit-lane verification cannot pass unless
the Slice 11 audit-hook runner also understands the same allowlist.

## Findings

### F1 - Generator allowlist does not change audit-hook enforcement

Sub-feature A proposes `--allowed-cross-repo-roots` for
`session_self_initialization.py` and expects this scenario to pass:

`--phase dashboard --execute ... --allowed-cross-repo-roots <upstream-path>`

Expected result in the proposal: `violations_count: 0` and real upstream
branch/sha/dirty status.

But the current audit-hook runner enforces its own path policy:

- `scripts/rehearse/_dashboard_regen_runner.py`: `build_audit_hook(...)` calls
  `build_is_allowed(legacy_root, sandbox_root)`.
- The subprocess hook records any `subprocess.Popen.cwd` that is not allowed by
  that runner-side policy and terminates with exit code `99`.
- `scripts/rehearse/_dashboard_regen.py`: `_build_generator_argv(sandbox_root)`
  has no mechanism to pass an allowed cross-repo root to the runner or to the
  generator.

So even if the generator accepts an upstream checkout allowlist, the runner will
still see `subprocess.Popen.cwd = E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
as outside `sandbox_root` and fail closed.

### F2 - Sub-feature A must define one authority for cross-repo allowances

The design needs to choose where the cross-repo allowance is enforced and how it
is evidenced. Two viable shapes:

1. Strict sandbox default: omit the allowlist during Slice 11 rehearsal, degrade
   upgrade posture to `available: false`, and require `violations_count: 0`.
   Real cross-repo inspection remains production-only or separately tested.
2. Shared allowlist: add the same `--allowed-cross-repo-roots` concept to the
   audit-hook runner/rehearsal command path, and require the lane proof to show
   both the generator and the audit hook accepted the exact same resolved root.

The current proposal mixes these by adding the allowlist only to the generator
while expecting the audit hook to permit it.

## Sub-feature B

The `--harness-config-root` parameterization is acceptable as scoped:

- It follows the existing argparse override pattern.
- It converts harness-home reads into explicit dependencies.
- The proposed regression test is the right shape, provided it proves both a
  positive read from the supplied root and a negative absence of `Path.home()`
  reads for the covered paths.

Because the bridge uses one status line, this file remains overall NO-GO until
Sub-feature A is revised.

## Required Revision

Revise GH-002 with one of these options:

1. Split Sub-feature B into its own bridge so it can proceed independently.
2. Keep both sub-features bundled, but revise Sub-feature A to include the
   audit-hook/rehearsal allowlist plumbing or remove the "with allowlist"
   `violations_count: 0` expectation from the Slice 11 lane.

Also clarify whether `.claude/settings.json` is in implementation scope or a
post-verification adopter follow-up, because the current text states both "no
code change required in the hook itself" and that the env-driven invocation is
updated.

## Decision Needed From Owner

None.

