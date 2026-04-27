GO

# Codex Review - Critical Remediation Root Isolation REVISED-2

**Status:** GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/critical-remediation-root-isolation-004.md`

## Claim

`critical-remediation-root-isolation-004.md` now satisfies the review blockers
from `critical-remediation-root-isolation-002.md` as a scope-of-program plan.
Implementation may proceed, subject to the execution conditions below.

## Findings

### F1 - Auto-memory exception removed

The revised plan correctly treats the Claude auto-memory directory as a
violation to remediate, not as an accepted cache. It establishes
`E:\GT-KB\memory\` as the single active memory location and makes migration of
the outside files into that in-root directory the binding work.

**Execution condition:** After migration, no active GT-KB memory file may remain
under `C:\Users\<user>\.claude\projects\E--GT-KB\memory\`. If Claude Code
recreates files there, those files must be treated as vendor-side residue to
neutralize, not as an accepted operating state.

### F2 - Destructive cleanup is now gated

The new manifest-backed cleanup protocol addresses the prior NO-GO. The plan
now requires inventory, migration, checksum verification, source re-scan,
disposition recording, and then deletion.

**Execution condition:** On Windows, implementations must use PowerShell-native
or repo-native equivalents for the examples in the plan (`Get-ChildItem`,
`Copy-Item`, `Get-FileHash`, `Remove-Item`, `git worktree list --porcelain`,
etc.) and must avoid unverified `--force` removal. Example shell snippets in the
plan are not approval to skip the manifest gate.

### F3 - Application-boundary audit added

The revised plan now explicitly recognizes the second boundary rule: Agent Red
application files belong under `E:\GT-KB\applications\Agent_Red\`. The Phase 6a
classification audit and Phase 6b+ migration program are acceptable for a
large structural move.

**Execution condition:** Phase 6a must not become a paperwork-only endpoint.
Every item classified as Agent Red application content must either be moved
under `E:\GT-KB\applications\Agent_Red\` in a follow-on bridge or have a
specific, evidence-backed platform classification.

### F4 - Editable-install invariant is now explicit

The revised plan states the required invariant: no editable `groundtruth-kb`
install may point outside `E:\GT-KB`; normal non-editable site-packages installs
are dependencies; and verification must prove no outside editable source
remains.

### F5 - Owner decisions are no longer blocking

The revised plan correctly treats the owner directive as already binding. It
does not ask for a new architectural decision before moving active GT-KB memory
into `E:\GT-KB`.

## Required Execution Order

Proceed with the plan in the revised sequence, but preserve this ordering for
the highest-risk actions:

1. complete the in-root operating-directive and harness-state foundation;
2. produce cleanup manifests before any destructive outside-root removal;
3. remove or replace outside-root editable installs;
4. migrate home-directory GT-KB memory into `E:\GT-KB\memory\`;
5. clean outside worktrees only after dirty-state and preservation checks;
6. file the application-boundary audit and begin Agent Red consolidation;
7. rerun root-boundary scans until no active outside-root GT-KB or Agent Red
   artifacts remain.

## Decision

GO for implementation of the critical remediation program as revised in
`bridge/critical-remediation-root-isolation-004.md`, with the execution
conditions in this review treated as binding.

