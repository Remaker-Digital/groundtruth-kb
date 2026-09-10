---
name: gtkb-sweep-commit
description: Inspect pending GT-KB work and complete independently verified projects through the native CLI while preserving unrelated work. Use for commit or cleanup requests involving a dirty worktree.
metadata:
  project: groundtruth-kb
  category: operation and hygiene
---

# Complete reviewed projects

Read the current project, its single-parent work items, formal intent and review
state through the CLI. A program sequences projects; each project groups the
work product that completes and commits together. A dirty path or bridge message
does not establish ownership, review completion or permission to include it.

Preserve every unrelated staged and unstaged byte. Report unfinished projects
and foreign changes; a cleanup request does not make them verified. Do not select
new implementation work or change membership merely to produce a clean tree.

Only the independent reviewing context completes an agent project commit. Use
its actual immutable native context binding. When all project members are
VERIFIED, the native service checks the complete current reviewed artifact set,
including Git modes and object identities, before the normal Git hooks run.

1. Read current state with `gt projects show <PROJECT-ID> --json`,
   `gt backlog show <WI-ID> --json`, and the relevant `gt bridge show <document>`.
   Inspect `git status --short` for work that must be preserved.
2. Confirm the proposal-derived executable tests and exact final artifact
   identities. A failed test or changed review requires correction and fresh
   independent verification of the affected scope.
3. Write a UTF-8 commit message in the current context's scratch directory.
   Cite every work item retired by this project commit as `(WI-NNNN)`.
4. Use the current project version and actual native context:

   ```text
   gt projects commit <PROJECT-ID> --native-context-id <native-context-id> --expected-version <version> --message-file <message-file>
   ```

5. Read back the returned Git commit and canonical project/member terminal state.
   Report the actual result and preserved remaining work. Publish a commit only
   when the owner has requested publication.

The service preserves foreign index/worktree content and refuses stale or
overlapping inputs. Review follows current formal intent. Material formal-intent
changes after VERIFIED and before commit require a fresh attempt on the same
uncommitted work item; membership and work bytes remain intact, and prior GO is
not inherited. A failed or uncertain commit is recovered from canonical state
and the actual Git fact before any retry.

Normal hooks check staged work product, secrets, formatting, PowerShell syntax
and whether baseline/projector sources can produce their projections. Repair a
failure through its current source and reverify affected work. Never bypass the
hooks. The commit excludes bridge payloads, generated projections and runtime
state. Current native review and project state are the evidence; no approval
packet, staged bridge file, staged test filename or inventory snapshot substitutes
for them. Projection and inventory refresh are operational derivations.
