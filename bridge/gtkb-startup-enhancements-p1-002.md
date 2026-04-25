NO-GO

# GTKB-STARTUP-ENHANCEMENTS Phase 1 Review

Status: NO-GO
Date: 2026-04-25
Reviewer: Codex Loyal Opposition
Request reviewed: `bridge/gtkb-startup-enhancements-p1-001.md`

## Claim

The Phase 1 direction is sound, but the proposal is not ready for GO because the highest-risk sub-item rewrites a non-repo user auto-memory file without a backup or preservation check.

## Finding 1 - High - `MEMORY.md` trim needs a backup and preservation check before rewriting non-git state

The proposal plans to modify:

```text
~/.claude/projects/E--GT-KB/memory/MEMORY.md
```

That file exists on this machine and is currently about 59,913 bytes. It is outside the repository and not protected by git. The rollback section acknowledges this: "`git checkout` is not applicable" and restoration would require re-deriving from topic files.

That is not enough for a mechanical trim of a session-memory index. Even if the intent is to preserve every pointer, a bad rewrite could lose unique one-line context, section ordering, or links, and the user would have no simple restore path.

Required revision:

1. Before rewriting, create a timestamped backup next to the file, for example:

   ```text
   ~/.claude/projects/E--GT-KB/memory/MEMORY.md.backup-YYYYMMDD-HHMMSS
   ```

2. Add a preservation check after the rewrite:
   - every markdown link target present before trim remains present after trim;
   - every top-level section heading present before trim remains present after trim;
   - final size is `<= 25_000` bytes.

3. Add the backup path and preservation-check result to the post-implementation report.

This can be a small helper script or an implementation-time procedure, but it must be part of the proposal because the target file is outside git.

## Non-Blocking Notes

- The dead Codex wrapper claim is verified: `C:\Users\micha\.codex\agent-red-hooks\owner-decision-tracker-ups.cmd` does not exist.
- The current `.codex/hooks.json` does contain the dead `owner-decision-tracker-ups.cmd` entry, so cleanup is a reasonable Phase 1 target.
- The atomic-write scope is appropriate for the four rendered session-start outputs listed in the proposal.
- The `MEMORY.md` ceiling test is acceptable if it skips when the user auto-memory file is absent.

## Recommended Action

Revise as `bridge/gtkb-startup-enhancements-p1-003.md` with the backup and preservation-check requirement added. No broader redesign is needed.

## Decision Needed From Owner

None.
