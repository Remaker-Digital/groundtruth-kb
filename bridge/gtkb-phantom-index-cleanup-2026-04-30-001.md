NEW

# Bridge Proposal — GTKB Phantom-INDEX + Stale-Snapshot Cleanup

**Status:** NEW (version 001)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `gtkb-phantom-index-cleanup-2026-04-30`
**Trigger:** S324 owner direction "Stop wrap; address phantom-INDEX errors first" in response to wrap-scan exit-code-2 findings on prior-session debt. The wrap-scan-consistency scanner identified 18 phantom INDEX entries citing nonexistent bridge files; the wrap-scan-hygiene scanner identified 4 stale wrap-scan reports in `.groundtruth/session/snapshots/{S319,S322}/` violating the Slice 1 manifest-only constraint. None of these errors were caused by S324; all are pre-existing prior-session debt blocking a clean wrap-scan exit.

**Owner pre-approval:** Yes for the cleanup scope per S324 AskUserQuestion answer "Stop wrap; address phantom-INDEX errors first." Standard Codex GO required before implementation per `.claude/rules/codex-review-gate.md`.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Governance specs / records that constrain this work:**
- `.claude/rules/codex-review-gate.md` — protocol authority requiring this bridge for INDEX mutation + file deletion
- `.claude/rules/file-bridge-protocol.md` — bridge structure; the canonical "INDEX cites bridge files that exist on disk" invariant being repaired here
- `.claude/rules/project-root-boundary.md` — all changes inside `E:\GT-KB`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage gate
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED gate requires spec-derived test mapping
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` — meta-rule
- `bridge/gtkb-wrapup-enhancements-slice1-006.md` (GO) — defines the snapshots-dir manifest-only constraint that the 4 stale wrap-scan reports violate

**Source basis (wrap-scan reports as evidence):**
- `.groundtruth/session/snapshots/S324/wrap-scan-consistency.md` — lists the 18 INDEX-cites-missing-bridge-file errors at lines 178-195
- `.groundtruth/session/snapshots/S324/wrap-scan-hygiene.md` — lists the 4 snapshots-non-manifest errors

**Historical context (pre-existing debt evidence):**
- `bridge/INDEX.md:196` — inline comment: "S317 phantom-INDEX (per bridge/gtkb-bridge-index-phantom-verified-references-2026-04-27): -012 absent from disk + git history. Latest on-disk version is -003; thread appears stalled; reopen is per-thread follow-up out of scope here." This documents that the phantom state has been known since S317 but the cleanup was deferred. Direct verification (`ls bridge/gtkb-root-directory-migration-*.md` excluding the unrelated `-post-verify-*` thread) returns ZERO files; all 18 INDEX entries cite missing files.

**Rule files that constrain this work:**
- `.claude/rules/file-bridge-protocol.md` (above)
- `.claude/rules/codex-review-gate.md` (above)
- `.claude/rules/project-root-boundary.md` (above)

**Distinction from related thread:**
- `gtkb-root-directory-migration-post-verify-*` is a DIFFERENT thread (suffix `-post-verify`) whose files DO exist on disk (versions -010 through -019 confirmed via `ls`). That thread is unaffected by this cleanup. Only the `gtkb-root-directory-migration` thread (without `-post-verify` suffix) is phantom.

---

## Proposed Changes

### Change 1 — Remove 18 phantom INDEX entries (1 Document block) from `bridge/INDEX.md`

**Lines to remove (per wrap-scan-consistency report):**
```
Document: gtkb-root-directory-migration
VERIFIED: bridge/gtkb-root-directory-migration-018.md
NEW: bridge/gtkb-root-directory-migration-017.md
GO: bridge/gtkb-root-directory-migration-016.md
REVISED: bridge/gtkb-root-directory-migration-015.md
NO-GO: bridge/gtkb-root-directory-migration-014.md
NEW: bridge/gtkb-root-directory-migration-013.md
GO: bridge/gtkb-root-directory-migration-012.md
REVISED: bridge/gtkb-root-directory-migration-011.md
NO-GO: bridge/gtkb-root-directory-migration-010.md
REVISED: bridge/gtkb-root-directory-migration-009.md
NO-GO: bridge/gtkb-root-directory-migration-008.md
REVISED: bridge/gtkb-root-directory-migration-007.md
NO-GO: bridge/gtkb-root-directory-migration-006.md
REVISED: bridge/gtkb-root-directory-migration-005.md
NO-GO: bridge/gtkb-root-directory-migration-004.md
REVISED: bridge/gtkb-root-directory-migration-003.md
NO-GO: bridge/gtkb-root-directory-migration-002.md
NEW: bridge/gtkb-root-directory-migration-001.md
```

Plus the trailing inline comment: `<!-- S317 phantom-INDEX (per bridge/gtkb-bridge-index-phantom-verified-references-2026-04-27): ... -->`. That comment was itself documenting the phantom state; with the entries removed, the comment is obsolete.

**Justification:** All 18 cited bridge files are confirmed missing on disk (`ls bridge/gtkb-root-directory-migration-*.md` returns empty when filtered to exclude the unrelated `-post-verify-*` thread). The bridge protocol's "audit trail must be complete" invariant is currently violated by this Document entry; removing it restores the invariant. No bridge-file deletions occur (the files don't exist).

**Risk:** Very low. The phantom thread has no on-disk audit trail to preserve; removing the INDEX entries cannot lose information that isn't there. Removal is reversible via `git revert` (the deletion is committed as a single line-removal diff).

### Change 2 — Delete 4 stale wrap-scan files from prior-session snapshot directories

**Files to delete:**
- `.groundtruth/session/snapshots/S319/wrap-scan-hygiene.md` (150010 bytes; written 2026-04-28T23:28)
- `.groundtruth/session/snapshots/S319/wrap-scan-consistency.md` (194804 bytes; written 2026-04-28T23:28)
- `.groundtruth/session/snapshots/S322/wrap-scan-hygiene.md` (136215 bytes; written 2026-04-29T19:55)
- `.groundtruth/session/snapshots/S322/wrap-scan-consistency.md` (194657 bytes; written 2026-04-29T19:55)

**Files to PRESERVE in those directories:**
- `.groundtruth/session/snapshots/S319/manifest.json` (the only Slice-1-permitted artifact in snapshot dirs)
- `.groundtruth/session/snapshots/S322/manifest.json` (same)

**Justification:** Per `bridge/gtkb-wrapup-enhancements-slice1-006.md` GO conditions, the snapshots dir is manifest-only in Slice 1. The 4 wrap-scan reports were written to the snapshot dirs by prior-session wrap-scan runs (before the manifest-only constraint was tightened or before the runs were reviewed for cleanup). They violate the constraint and trigger the wrap-scan-hygiene `snapshots_non_manifest` ERROR per scan run.

**Risk:** Very low. The files are gitignored (`.groundtruth/session/snapshots/` is gitignored); deleting them removes only local working-state artifacts. Their original content is preserved in the prior-session git history insofar as wrap-scan output was committed — but per Slice 1 manifest-only design, wrap-scan output was NOT meant to live in snapshots. Deletion is the intended hygiene step.

### Change 3 — Run wrap-scan after cleanup; expect 0 ERRORs

After Changes 1 + 2 land:
```bash
python scripts/wrap_scan_hygiene.py --report-format markdown --write-report .groundtruth/session/snapshots/S324/wrap-scan-hygiene.md
python scripts/wrap_scan_consistency.py --report-format markdown --write-report .groundtruth/session/snapshots/S324/wrap-scan-consistency.md
```

Expected results:
- W1 `snapshots_non_manifest` ERROR count: 4 → 0
- W2 `index_cites_missing_bridge_file` ERROR count: 18 → 0
- WARN counts may decrease slightly (W2 orphan warnings for the now-missing INDEX entries will go to 0; W1 bridge_files_not_in_index warnings unchanged because they're a different orphan class)
- Aggregate exit code: 2 → 0

This is the post-impl evidence that the cleanup achieved its goal.

---

## Specification-Derived Verification

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

**Spec-to-test mapping:**

| Linked spec / driver | Test / verification | Command |
|---|---|---|
| `.claude/rules/file-bridge-protocol.md` "INDEX cites files that exist" invariant | After Change 1, no INDEX line cites a missing file in the gtkb-root-directory-migration thread. Verified by wrap-scan-consistency reporting 0 `index_cites_missing_bridge_file` errors. | `python scripts/wrap_scan_consistency.py` exit 0; `grep -c "gtkb-root-directory-migration-" bridge/INDEX.md` returns count of `-post-verify-*` lines only (the unrelated real thread) |
| `bridge/gtkb-wrapup-enhancements-slice1-006.md` snapshots-manifest-only constraint | After Change 2, snapshots dirs contain only manifest.json. Verified by wrap-scan-hygiene reporting 0 `snapshots_non_manifest` errors. | `python scripts/wrap_scan_hygiene.py` exit 0; `ls .groundtruth/session/snapshots/S319/` returns only manifest.json; same for S322 |
| Aggregate wrap-scan exit code | After Changes 1 + 2, wrap-scan-{hygiene,consistency} both exit 0 | Re-run both scanners; assert non-error exit |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal's Specification Links section + bridge-compliance-gate hook approval | hook check (already passed if this Write succeeds) |
| Project root boundary | All edited paths inside `E:\GT-KB` | manual verification, see §Project Root Boundary Compliance |
| `gtkb-root-directory-migration-post-verify-*` unaffected (separate real thread) | Verify post-verify thread INDEX entries unchanged after Change 1 | `grep -c "gtkb-root-directory-migration-post-verify-" bridge/INDEX.md` before == after (count preserved) |

**Execution commands (planned for post-impl report):**
```bash
ls bridge/gtkb-root-directory-migration-*.md 2>&1 | grep -v post-verify
python scripts/wrap_scan_hygiene.py
python scripts/wrap_scan_consistency.py
ls .groundtruth/session/snapshots/S319/
ls .groundtruth/session/snapshots/S322/
```

The release-gate is NOT part of this slice's verification surface (release-gate has known infrastructure issues; this cleanup doesn't touch any code path the release-gate exercises).

---

## Project Root Boundary Compliance

Per `.claude/rules/project-root-boundary.md`:

- All edited / deleted paths inside `E:\GT-KB`:
  - `bridge/INDEX.md` (modified — 18 INDEX lines + 1 Document line + 1 inline comment removed)
  - `.groundtruth/session/snapshots/S319/wrap-scan-hygiene.md` (deleted)
  - `.groundtruth/session/snapshots/S319/wrap-scan-consistency.md` (deleted)
  - `.groundtruth/session/snapshots/S322/wrap-scan-hygiene.md` (deleted)
  - `.groundtruth/session/snapshots/S322/wrap-scan-consistency.md` (deleted)
- All cited specifications inside `E:\GT-KB` or `groundtruth.db` at the project root.
- No external paths referenced.

---

## Pre-GO Drift Disposition

Clean implementation pending GO. No source-code edits exist in worktree for this slice. Cleanup will be authored after Codex GO.

---

## Implementation Sequence (planned for after Codex GO)

1. Verify the phantom thread state still holds (`ls bridge/gtkb-root-directory-migration-*.md | grep -v post-verify` returns empty).
2. Verify the post-verify thread is unaffected (`ls bridge/gtkb-root-directory-migration-post-verify-*.md` returns 10 files).
3. Edit `bridge/INDEX.md` to remove the 18 INDEX lines + 1 Document line + 1 inline comment for the phantom `gtkb-root-directory-migration` thread.
4. Delete the 4 stale wrap-scan files from `.groundtruth/session/snapshots/{S319,S322}/`.
5. Re-run wrap-scan-hygiene + wrap-scan-consistency. Expect:
   - Both report 0 ERRORs in their respective domain (snapshots-non-manifest = 0; index-cites-missing = 0).
   - Aggregate exit code = 0.
6. Stage `bridge/INDEX.md` (the snapshot-dir files are gitignored; deletions don't affect git).
7. Commit with scoped message referencing this bridge thread.
8. File post-impl report; include before/after wrap-scan output as evidence.

---

## Rollback Notes

If post-impl reveals an unexpected issue:
- Revert the single commit via `git revert <sha>` — restores the 18 phantom INDEX entries (which are non-functional anyway, so revert is safe).
- Snapshot files are gitignored and locally deleted; they cannot be restored from git history but their content is non-canonical (just stale wrap-scan output). Re-running wrap-scan in S319/S322 contexts is not possible (those sessions are over) and not necessary (their wrap-scan output was advisory, not authoritative).

---

## Decision Needed From Owner

This bridge does not require an additional owner decision. Standard Codex GO/NO-GO flow applies; the program-level scope is already approved per S324 AskUserQuestion answer "Stop wrap; address phantom-INDEX errors first."

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
