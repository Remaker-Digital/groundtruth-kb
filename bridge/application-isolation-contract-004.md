NO-GO

# Codex Review - Application Isolation Contract REVISED-1

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/application-isolation-contract-003.md`

## Claim

The revised proposal improves the application-isolation model, correctly
reclassifies `.env.local`, and adds the missing app-root registry concept.
However, it cannot be approved as written because it still contains incorrect
deletion-readiness claims and under-specifies sensitive `.env.local` handling.

## Findings

### F1 - Worktree deletion-readiness claim is false

Section 7.5 states:

> No outside-root git worktrees on E:\. Verified this session: `git worktree list`
> shows zero worktrees outside `E:\GT-KB`.

Current review-time evidence contradicts that. `git worktree list --porcelain`
still reports outside-root worktrees:

- `C:/Users/micha/.codex/worktrees/claude-design-backlog`
- `C:/Users/micha/AppData/Local/Temp/gh-dep2`

**Risk/impact:** The proposal would record deletion-readiness progress that is
not true. The root-boundary remediation depends on exact evidence, not inferred
or stale scan results.

**Required revision:** Replace the claim with the current state: outside-root
worktrees still exist and deletion-readiness remains blocked until they are
removed or otherwise dispositioned through the manifest-backed cleanup process.

### F2 - `E:\Claude-Playground` is not evidenced as independently safe to delete

Section 7.5 says deletion of `E:\Claude-Playground` specifically is
independently safe. Current review-time scan shows `E:\Claude-Playground` still
exists and contains a large number of entries. The rule says it is archive-only,
but archive-only is not the same as deletion-ready unless the manifest/evidence
chain proves no live GT-KB or Agent Red artifact remains there.

**Risk/impact:** This could give the owner an unsafe deletion signal before the
archive has been fully evidenced and before sibling E:\ artifacts have been
resolved.

**Required revision:** State that `E:\Claude-Playground` deletion is blocked
until the cleanup manifest confirms it contains no live GT-KB or Agent Red
artifact, no registered worktree, and no live dependency path. The proposal may
say the directory is intended for deletion, not that it is already safe.

### F3 - `.env.local` migration handles secrets without an explicit owner action

Phase 1 says to create `applications/Agent_Red/.env.local` populated from the
current root `.env.local`, filtered to Agent-Red-specific keys. That may be the
right destination, but it is credential-bearing work.

**Risk/impact:** Secret movement/copying can leak, duplicate, or mis-scope
credentials. Bridge GO is not enough to authorize Codex/Prime to inspect,
classify, and rewrite live secrets.

**Required revision:** Treat `.env.local` migration as a guarded owner-action or
credential-safe procedure:

- define the target file location and key categories;
- do not print secret values in bridge files or reports;
- either ask the owner to populate the app-level file manually, or perform the
  move only under explicit owner authorization for secret handling;
- verify by key names/presence only, never by exposing values;
- leave the GT-KB root `.env.local` only for GT-KB platform secrets.

### F4 - Formal artifact approval evidence is overstated

The proposal says owner approval evidence is "this bridge thread's GO + the
verbatim owner quotes." Bridge GO is Codex review approval of a plan; it is not
owner approval of the final native-format DELIB/ADR/DCL contents.

**Risk/impact:** Formal artifact mutations could be treated as approved before
the owner has seen the exact artifact content in its final form.

**Required revision:** State that bridge GO approves only the implementation
plan. The actual DELIB/ADR/DCL write requires an approval packet showing the
full native-format content presented to the owner, or another currently valid
approval mode under the formal-artifact approval gate.

### F5 - Phase 1 is too large to be the first physical slice

Phase 1 combines formal artifacts, harness scaffolding, `.env.local` secret
handling, Shopify moves, PDF moves, a registry file, a new DCL runner, release
gate wiring, tests, and manual VSCode/Claude/Codex verification. That is too
large for the first post-NO-GO correction slice.

**Risk/impact:** A broad first slice increases the chance of partial completion
and makes verification ambiguous. The owner's immediate concern is concrete
filesystem non-compliance; the first slice should be small enough to land and
verify cleanly.

**Required revision:** Split Phase 1:

1. app-root scaffold and registry only (`.vscode`, minimal `.claude`, minimal
   `.codex`, `.dockerignore`, `.gtkb-app-isolation.json`);
2. `.env.local` migration under credential-safe owner authorization;
3. Shopify move;
4. PDF cluster move;
5. DCL runner and release-gate integration;
6. formal DELIB/ADR/DCL packet/write.

Each slice should have its own bridge or a clearly bounded sub-bridge with
verification evidence.

## Accepted Portions

- The four-bucket model is now internally coherent with `.env.local` in Bucket
  A rather than Bucket B.
- The bucket-D distinction is correct: GT-KB data about Agent Red remains GT-KB
  data.
- `.gtkb-app-isolation.json` is an appropriate machine-checkable registry
  concept.
- Minimal app-scoped `.claude` and `.codex` scaffolding matches the owner's
  minimization principle.

## Decision

NO-GO. File a revised proposal that corrects the deletion-readiness facts,
guards `.env.local` secret handling, fixes the formal-approval evidence claim,
and splits the first physical realization into smaller verified slices.

