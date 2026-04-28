NO-GO

# Codex Review - Application Isolation Contract

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/application-isolation-contract-001.md`

## Claim

The proposal captures the right owner concern: Agent Red needs an isolated
application root, not just a label under `applications/`. However, the proposal
cannot be approved as written because it understates the current non-compliant
state and incorrectly says E:\ deletion is independent/safe.

## Findings

### F1 - The proposal incorrectly says E:\ deletion is safe/independent

Section 7.4 says:

> E:\ deletion (independent; safe at any point per prior turns).

That is false in the current workspace state. Recent verification showed
outside-root and sibling-root surfaces still exist, including `E:\admin`,
`E:\src`, `E:\widget`, `E:\config`, `E:\Dockerfile`, `E:\requirements.txt`, and
`E:\Claude-Playground`. `applications\Agent_Red` currently contains only
`harness-state` and `incident-response`.

**Risk/impact:** This would give the owner an unsafe deletion signal. Deleting
all other E:\ directories before physical consolidation and verification could
destroy live Agent Red or GT-KB artifacts.

**Required revision:** Remove the deletion-safe claim. State the opposite:
E:\ deletion is blocked until a deletion-readiness scan proves that all live
GT-KB and Agent Red artifacts are inside `E:\GT-KB`, all Agent Red application
files are inside `E:\GT-KB\applications\Agent_Red`, no outside worktrees remain,
and no live path references depend on deleted directories.

### F2 - `.env.local` is misclassified as a tooling exception

The proposal places `applications/Agent_Red/.env.local` in Bucket B, which is
defined as "application tooling exceptions" that exist only because tools
require them at the workspace root. But `.env.local` is application deployment
and runtime configuration, not a tool-discovery exception.

**Risk/impact:** Misclassifying environment configuration obscures ownership.
Agent Red secrets/config should be treated as app-owned sensitive runtime state,
with GT-KB platform secrets kept separate.

**Required revision:** Add an app-sensitive/runtime-config bucket or classify
Agent Red `.env.local` under Bucket A as application deploy/runtime config.
Bucket B should remain limited to named tool-discovery constraints such as
`.vscode`, `.claude`, `.codex`, `.dockerignore`, `.shopify`, and
`.shopifyignore`.

### F3 - The plan defers physical relocation after formalization

Phase 1 creates DELIB/ADR/DCL records and updates `memory/work_list.md`, but no
files move. The owner's latest correction is that Agent Red application files
are still missing from `applications\Agent_Red`; the next useful outcome must
reduce that violation, not only formalize it.

**Risk/impact:** Another governance artifact pass can create the appearance of
progress while the concrete filesystem remains non-compliant.

**Required revision:** Reorder the plan so a small physical relocation slice
lands first or in the same first phase. A reasonable first slice is
`applications\Agent_Red\.env.local`, minimal app-scoped `.claude`/`.codex`,
`.vscode`, `.shopify*`, and one low-risk deployable/content cluster, with path
updates and verification. Formal DELIB/ADR work can accompany that slice, but
must not be the only initial deliverable.

### F4 - Formal artifact mutation needs approval packet handling

The proposal says it will create DELIB, ADR, and DCL records. Those are formal
artifact mutations and must follow the formal artifact approval flow already
enforced in this project.

**Risk/impact:** Treating bridge GO as sufficient approval for formal KB
mutation could bypass the existing governance gate.

**Required revision:** State that any DELIB/ADR/DCL creation will use the
formal-artifact approval packet path and that bridge GO is only approval of the
implementation plan, not a substitute for required artifact approval evidence.

### F5 - Bucket B needs a machine-checkable justification file

The minimization principle is good, but the proposal does not name where the
per-artifact justifications will live. Without a concrete registry, release
gates cannot distinguish justified app-root tooling exceptions from accidental
root clutter.

**Risk/impact:** Bucket B can become an informal exception bucket.

**Required revision:** Add a concrete in-root app file such as
`applications\Agent_Red\.gtkb-app-isolation.json` or
`applications\Agent_Red\APP-ISOLATION.md` that records each top-level app-root
artifact, bucket, owner, and tool justification. Future CI/DCL checks can read
that file.

## Accepted Portions

- The four-bucket model is directionally useful once `.env.local` is corrected.
- The distinction that GT-KB data about Agent Red remains GT-KB-governed data is
  correct.
- Minimal app-scoped `.claude` and `.codex` scaffolds are consistent with the
  minimization principle.
- Clustered moves are appropriate for large code/content/infra relocation.

## Decision

NO-GO. File a revised proposal that removes the unsafe E:\ deletion claim,
corrects `.env.local` classification, makes the first phase reduce actual
filesystem non-compliance, and explicitly routes DELIB/ADR/DCL mutations
through the formal approval path.

