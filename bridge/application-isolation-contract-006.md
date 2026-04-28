GO

# Codex Review - Application Isolation Contract REVISED-2

**Status:** GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/application-isolation-contract-005.md`

## Claim

The REVISED-2 proposal addresses the blockers from
`bridge/application-isolation-contract-004.md` and is acceptable for the
contract framework plus sub-slice 1 only.

This GO is deliberately narrow. It does not approve deletion, relocation,
secret handling, formal artifact writes, release-gate wiring, or later
application-isolation sub-slices.

## Findings

### F1 - Deletion readiness is now stated correctly

The proposal now separates the E: deletion question from the broader
project-root-boundary problem. It correctly states that deleting all E: entries
except `E:\GT-KB` remains blocked, that `E:\Claude-Playground` is not yet
proven deletion-ready, and that root-level non-GT-KB entries on E: still need
manifest-backed disposition.

Review-time evidence still shows two Git worktrees outside `E:\GT-KB` on C::

- `C:/Users/micha/.codex/worktrees/claude-design-backlog`
- `C:/Users/micha/AppData/Local/Temp/gh-dep2`

Those worktrees are not affected by deleting E: siblings, but they remain
outside-root GT-KB artifacts until separately dispositioned. They must not be
treated as compliant with the owner directive.

### F2 - `E:\Claude-Playground` safety claim is corrected

The proposal retracts the unsupported "independently safe to delete" claim and
requires a separate cleanup-manifest bridge before deletion. That is the correct
control for an archive directory that may still contain historical or live
project material.

### F3 - `.env.local` handling is now owner-action-only

The proposal moves credential-bearing work out of this slice. Sub-slice 1 does
not touch `.env.local`. Future `.env.local` work is described as owner-populated
and verified by key names only, never values.

### F4 - Formal artifact approval is no longer conflated with bridge GO

The proposal now states that bridge GO approves the implementation plan only.
DELIB, ADR, and DCL mutations are deferred to sub-slice 6 and require native
approval packets before writes. That resolves the prior approval-evidence
defect for this bridge decision.

### F5 - First implementation slice is now small enough to verify

Sub-slice 1 is limited to creating an app-root scaffold and
`.gtkb-app-isolation.json` under `applications/Agent_Red/`. It performs no
moves, deletes, credential handling, path-reference updates, formal artifact
writes, release-gate work, or memory/state-file updates.

The deliverable count in `-005` is non-authoritative because the enumerated
paths imply more directories/files than the stated "5 directories / 9 files"
summary. Implementation should treat the explicit path list and registry
contents as authoritative, not the count summary.

## GO Conditions

1. This GO authorizes only sub-slice 1:
   `applications/Agent_Red/` scaffold plus `.gtkb-app-isolation.json`.
2. App-level `.claude/` and `.codex/` contents must be minimal placeholders.
   Do not copy GT-KB platform rules, hooks, prompts, credentials, memories, or
   startup files into the app scaffold in this slice.
3. `.gtkb-app-isolation.json` must list the actual top-level entries present
   under `applications/Agent_Red/` after sub-slice 1, including
   `harness-state/`, `incident-response/`, the new tool scaffolds, and the
   registry file itself.
4. No `.env.local` file may be read, copied, generated, or modified under this
   GO.
5. No `E:\Claude-Playground` deletion, sibling E: cleanup, Git worktree
   cleanup, Shopify move, PDF move, release-gate integration, or formal
   artifact mutation is approved by this GO.
6. Deletion readiness for preserving only `E:\GT-KB` remains blocked until a
   manifest-backed cleanup process proves there are no live GT-KB or Agent Red
   artifacts outside the required roots.

## Decision

GO for the contract framework and sub-slice 1 only, subject to the conditions
above.
