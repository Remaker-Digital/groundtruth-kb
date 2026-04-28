VERIFIED

# Codex Verification - Application Isolation Contract Sub-Slice 1

**Status:** VERIFIED
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/application-isolation-contract-007.md`
**Implements GO:** `bridge/application-isolation-contract-006.md`

## Claim

Sub-slice 1 is verified for the current checkout: the Agent Red app-root
scaffold and `.gtkb-app-isolation.json` registry exist under
`applications/Agent_Red/`, registry contents match the current top-level app
directory, placeholders are minimal, and the scoped-out moves, deletions,
secret handling, formal artifacts, release-gate work, and path updates did not
land in this slice.

This verification does not change the broader isolation state. Deletion
readiness for preserving only `E:\GT-KB` remains blocked, and outside-root C:
worktrees remain unresolved project-root-boundary issues.

## Evidence

1. `applications/Agent_Red/.gtkb-app-isolation.json` parses as valid JSON and
   uses the expected `top_level_artifacts` schema.
2. Current top-level disk entries under `applications/Agent_Red/` match the
   registry by name and type with no mismatches:
   - `.claude` DIR
   - `.codex` DIR
   - `.dockerignore` FILE
   - `.gtkb-app-isolation.json` FILE
   - `.vscode` DIR
   - `harness-state` DIR
   - `incident-response` DIR
3. Placeholder contents are minimal:
   - `.claude/settings.json` is `{}`
   - `.codex/hooks.json` is `{}`
   - `.vscode/settings.json` is `{}`
   - `.codex/config.toml` contains only a placeholder `[default]` section and
     explanatory comments
   - `.dockerignore` contains only placeholder comments
4. No `applications/Agent_Red/.env.local` exists after the slice.
5. Negative-scope checks are intact:
   - `E:\Claude-Playground` still exists and was not deleted.
   - `E:\GT-KB\.shopify` and `E:\GT-KB\.shopifyignore` still exist at the
     GT-KB root.
   - PDF cluster files still exist at the GT-KB root and were not moved.
   - `.gitignore` was not modified in this slice.
   - `git worktree list --porcelain` still reports the two outside-root C:
     worktrees, so this slice did not clean up or mask that separate issue.

## Verified Limitations

The `.vscode/settings.json` limitation in `-007` is real. Current evidence:

```text
.gitignore:90:.vscode/  applications/Agent_Red/.vscode/settings.json
.gitignore:90:.vscode/  applications/Agent_Red/.vscode/
```

Because `.gitignore` line 90 ignores `.vscode/` directories and line 91's
negation cannot take effect beneath an ignored parent directory, the
`applications/Agent_Red/.vscode/settings.json` file exists in this checkout but
is not currently git-trackable. That is not a blocker for this sub-slice because
`.gitignore` changes were explicitly out of scope, and the limitation is
documented in the registry. It remains a portability gap and should be handled
by a follow-up gitignore-hygiene bridge before anyone claims the VSCode
placeholder is durable across clones, clean worktrees, or `git clean -fdx`.

The post-implementation report also contains a non-blocking count inconsistency
("8 new artifacts" while the artifact table lists 6 rows and the on-disk
directory/file count is different depending on whether implicit directories are
counted). The actual path-level evidence is clear and verified; do not use the
summary count as authoritative.

## Decision

VERIFIED for sub-slice 1 in the current checkout.

Follow-up required before broader closure:

1. File a gitignore-hygiene bridge if `.vscode/settings.json` must become a
   durable tracked artifact.
2. Keep deletion readiness blocked until a manifest-backed cleanup process
   proves no live GT-KB or Agent Red artifacts remain outside the required
   roots.
3. Disposition the two C: outside-root Git worktrees as a separate
   project-root-boundary issue.
