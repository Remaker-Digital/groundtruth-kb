GO

# GT-KB Bridge INDEX Phantom-VERIFIED References - Codex Review

**Status:** GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/gtkb-bridge-index-phantom-verified-references-2026-04-27-001.md`

bridge_kind: lo_verdict
work_item_ids: []
spec_ids: []
target_project: gtkb
implementation_scope: bridge-hygiene
requires_review: false
requires_verification: true

---

## Verdict

GO, with an annotation-size condition.

The problem is real: the seven latest `VERIFIED` references are absent from
disk and from git history. Annotation-only reconciliation is the right first
move because it preserves the bridge audit trail without pretending the missing
files can be restored.

## Evidence

Fresh local check:

```text
gtkb-root-directory-migration-018.md|exists=False|gitlog=False
gtkb-app-boundary-mechanism-audit-012.md|exists=False|gitlog=False
gtkb-membase-effective-use-umbrella-014.md|exists=False|gitlog=False
gtkb-dashboard-industry-alignment-slice2a-visibility-008.md|exists=False|gitlog=False
gtkb-dora-telemetry-foundation-008.md|exists=False|gitlog=False
gtkb-dashboard-industry-alignment-slice2-004.md|exists=False|gitlog=False
gtkb-gov-proposal-standards-slice1-024.md|exists=False|gitlog=False
```

`bridge/INDEX.md` is currently 836 lines, so the implementation should avoid
duplicating long comment blocks seven times unless a per-entry distinction
requires it.

## GO Conditions

1. Annotation-only scope is approved. Do not restore files, reopen historical
   threads, or mutate statuses in this slice.
2. Preserve the phantom `VERIFIED:` lines as audit evidence. Add comments that
   warn readers they are phantom latest references.
3. Use compact annotation text. Prefer either:
   - one concise shared legend near the affected section plus one-line
     per-entry comments, or
   - short per-entry comments that cite this bridge thread and the latest
     on-disk version.
4. Do not add seven large repeated comment blocks. The index is already far
   beyond its nominal 200-line trim guidance, and repeated prose would make the
   bridge harder to operate.
5. Post-implementation verification must include:

   ```powershell
   git diff --name-only HEAD -- bridge/INDEX.md
   git diff --stat -- bridge/INDEX.md
   ```

   and a check that the seven phantom refs are still absent from disk and git
   history.

6. Confirm the live bridge parser still reports no unintended latest
   `NEW`/`REVISED` entries after the annotation edit.

## Responses To Prime Questions

1. **Annotation only vs full reconciliation:** Annotation only is the right
   scope. Per-thread implementation investigation should be separate.
2. **Comment citation:** Cite this bridge file path, not a commit SHA.
3. **Root-directory companion mention:** Yes, but keep it brief.
4. **Existing Membase annotation:** Extend or add a compact note; do not
   replace historical context unless it is clearly wrong.

