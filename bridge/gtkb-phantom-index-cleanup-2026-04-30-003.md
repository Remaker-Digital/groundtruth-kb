REVISED

# Bridge Proposal — GTKB Phantom-INDEX + Stale-Snapshot Cleanup (REVISED-1)

**Status:** REVISED (version 003)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `gtkb-phantom-index-cleanup-2026-04-30`
**Reviewed prior version:** `bridge/gtkb-phantom-index-cleanup-2026-04-30-002.md` (Codex NO-GO with F1, F2, plus a non-blocking accuracy note).

**REVISED-1 summary:** Closes -002 F1 (cleanup scope expanded from 4 to 6 stale snapshot files; adds S324 wrap-scan reports to deletion list). Closes -002 F2 (post-cleanup verification switches to stdout-only `--report-format json`; no `--write-report` into the snapshots-dir governed by the manifest-only invariant). Corrects the non-blocking accuracy note (post-verify thread file count 10 → 9; `-011.md` is missing).

---

## Closure of NO-GO Findings (-002)

### F1 Closure — Cleanup Scope Includes S324 Snapshot Files

**Original finding:** Change 2 of `-001` deleted only 4 stale snapshot files (S319 + S322 wrap-scan reports). The live filesystem also has `.groundtruth/session/snapshots/S324/wrap-scan-hygiene.md` and `.groundtruth/session/snapshots/S324/wrap-scan-consistency.md` (the reports generated this turn during wrap-scan execution). Without including them, the post-cleanup wrap-scan-hygiene check would still report 2 `snapshots_non_manifest` ERRORs.

**Closure:** Change 2 (below) is updated to delete 6 stale snapshot files. The 2 S324 wrap-scan reports are added to the deletion list. After Change 2 + 1 land, the snapshot tree contains only `manifest.json` files for each session, satisfying the Slice 1 manifest-only invariant.

### F2 Closure — Verification Commands Use Stdout, Not `--write-report` Into Snapshots Dir

**Original finding:** Change 3 of `-001` planned to write fresh wrap-scan reports to `.groundtruth/session/snapshots/S324/wrap-scan-{hygiene,consistency}.md` for post-cleanup verification. That destination is governed by the same manifest-only invariant the cleanup is repairing — re-introducing the violation in the verification step.

**Closure:** Change 3 is rewritten to run scanners with `--report-format json` (stdout output) only. Exit-code parsing is sufficient evidence: exit 0 = ERRORs cleared. JSON stdout content can be captured ad-hoc into the post-impl bridge report's evidence section without persisting any non-manifest files into the snapshots tree. No `--write-report` flag is used.

### Minor Accuracy Correction (non-blocking)

`-001` claimed the `gtkb-root-directory-migration-post-verify-*` thread has 10 files (`-010` through `-019`). Codex's direct check revealed only 9 files; `-011.md` is missing from disk. The corrected count is reflected throughout this REVISED proposal. This thread (the `-post-verify` variant) remains UNCHANGED by this cleanup — only the phantom non-`-post-verify` thread's INDEX entries are removed.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate (carried forward from `-001` with no changes):

**Governance specs / records that constrain this work:**
- `.claude/rules/codex-review-gate.md` — protocol authority requiring this bridge for INDEX mutation + file deletion
- `.claude/rules/file-bridge-protocol.md` — bridge structure; the canonical "INDEX cites bridge files that exist on disk" invariant being repaired here
- `.claude/rules/project-root-boundary.md` — all changes inside `E:\GT-KB`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage gate
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED gate requires spec-derived test mapping
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` — meta-rule
- `bridge/gtkb-wrapup-enhancements-slice1-006.md` (GO) — defines the snapshots-dir manifest-only constraint that this cleanup is enforcing

**Source basis (wrap-scan reports as evidence):**
- `.groundtruth/session/snapshots/S324/wrap-scan-consistency.md` (will be deleted by Change 2; cited here as evidence-of-finding) — listed the 18 INDEX-cites-missing-bridge-file errors at lines 178-195
- `.groundtruth/session/snapshots/S324/wrap-scan-hygiene.md` (will be deleted by Change 2; cited here as evidence-of-finding) — listed the 6 snapshots-non-manifest errors (4 from S319+S322; 2 from S324)

**Historical context:**
- `bridge/INDEX.md:196` (current) — inline comment from S317 documenting the phantom state.

**Distinction from related thread:**
- `gtkb-root-directory-migration-post-verify-*` is a DIFFERENT thread whose files DO exist on disk (versions -010, -012, -013, -014, -015, -016, -017, -018, -019; **9 files total — `-011.md` is missing**). That thread is unaffected by this cleanup.

---

## Proposed Changes

### Change 1 — Remove 18 phantom INDEX entries (1 Document block) from `bridge/INDEX.md`

UNCHANGED from `-001`. Lines to remove (per wrap-scan-consistency report):
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

Plus the trailing inline comment block referencing the S317 phantom-INDEX context, which becomes obsolete once the entries are gone.

**Risk:** Very low. Phantom thread has no on-disk audit trail; the deletion preserves nothing existing.

### Change 2 — Delete 6 stale wrap-scan files from snapshot directories (REVISED in -003)

**Files to delete (UPDATED to 6 from prior -001's 4):**
- `.groundtruth/session/snapshots/S319/wrap-scan-hygiene.md`
- `.groundtruth/session/snapshots/S319/wrap-scan-consistency.md`
- `.groundtruth/session/snapshots/S322/wrap-scan-hygiene.md`
- `.groundtruth/session/snapshots/S322/wrap-scan-consistency.md`
- **`.groundtruth/session/snapshots/S324/wrap-scan-hygiene.md`** (new in REVISED-1; per F1 closure)
- **`.groundtruth/session/snapshots/S324/wrap-scan-consistency.md`** (new in REVISED-1; per F1 closure)

**Files to PRESERVE in those directories:**
- `.groundtruth/session/snapshots/S319/manifest.json`
- `.groundtruth/session/snapshots/S322/manifest.json`
- `.groundtruth/session/snapshots/S324/manifest.json`

**Justification:** The Slice 1 manifest-only constraint (per `bridge/gtkb-wrapup-enhancements-slice1-006.md`) governs the entire snapshots tree, not just specific session directories. All non-manifest files in the snapshots tree are violations regardless of when they were generated. The S324 reports were generated this turn for the express purpose of identifying the violation; once the violation is identified and recorded in this bridge's evidence section, the reports are themselves redundant and should be deleted.

**Risk:** Very low. The files are gitignored; deletion removes only local working-state artifacts. Their content is captured in this bridge proposal's evidence section.

### Change 3 — Post-cleanup verification (REVISED in -003 — stdout-only)

**Verification commands (UPDATED to use --report-format json + stdout; no --write-report):**
```bash
python scripts/wrap_scan_hygiene.py --report-format json
python scripts/wrap_scan_consistency.py --report-format json
```

**Expected results:**
- Both commands exit 0 (no error-severity findings).
- `wrap_scan_hygiene.py` JSON has zero `snapshots_non_manifest` ERRORs (4 from S319+S322 → 0; 2 from S324 → 0).
- `wrap_scan_consistency.py` JSON has zero `index_cites_missing_bridge_file` ERRORs (18 → 0; the orphan-warning count drops by 18 corresponding entries as well).
- WARN counts may decrease but are not the binding gate; ERROR-count = 0 is the target.

**Why stdout-only:** The Slice 1 snapshots-manifest-only invariant means there is no governed location inside `.groundtruth/session/snapshots/` for non-manifest scan output. Stdout is the canonical alternative — JSON content can be quoted directly into the post-impl bridge report.

---

## Specification-Derived Verification

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate (UPDATED to reflect Change 3 stdout pivot):

**Spec-to-test mapping:**

| Linked spec / driver | Test / verification | Command |
|---|---|---|
| `.claude/rules/file-bridge-protocol.md` "INDEX cites files that exist" invariant | After Change 1, no INDEX line cites a missing file in the gtkb-root-directory-migration thread. | `python scripts/wrap_scan_consistency.py --report-format json` exit 0 |
| `bridge/gtkb-wrapup-enhancements-slice1-006.md` snapshots-manifest-only constraint | After Change 2, snapshots dirs contain only manifest.json | `python scripts/wrap_scan_hygiene.py --report-format json` exit 0; manual `ls .groundtruth/session/snapshots/{S319,S322,S324}/` returns only manifest.json each |
| Aggregate wrap-scan exit code | After Changes 1 + 2, both scanners exit 0 | re-run both scanners with `--report-format json`; assert exit 0 |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal's Specification Links section + bridge-compliance-gate hook approval | hook check (already passed) |
| Project root boundary | All edited paths inside `E:\GT-KB` | manual verification |
| `gtkb-root-directory-migration-post-verify-*` unaffected | Verify post-verify thread INDEX entries unchanged | `grep -c "gtkb-root-directory-migration-post-verify-" bridge/INDEX.md` before == after |

**Execution commands (planned for post-impl report — stdout only):**
```bash
ls bridge/gtkb-root-directory-migration-*.md 2>&1 | grep -v post-verify
ls bridge/gtkb-root-directory-migration-post-verify-*.md
ls .groundtruth/session/snapshots/S319/
ls .groundtruth/session/snapshots/S322/
ls .groundtruth/session/snapshots/S324/
python scripts/wrap_scan_hygiene.py --report-format json
python scripts/wrap_scan_consistency.py --report-format json
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
  - `.groundtruth/session/snapshots/S324/wrap-scan-hygiene.md` (deleted; new in REVISED-1)
  - `.groundtruth/session/snapshots/S324/wrap-scan-consistency.md` (deleted; new in REVISED-1)
- All cited specifications inside `E:\GT-KB` or `groundtruth.db` at the project root.
- No external paths referenced.

---

## Pre-GO Drift Disposition

Clean implementation pending GO. No source-code edits exist in worktree for this slice. Cleanup will be authored after Codex GO.

---

## Implementation Sequence (planned for after Codex GO; UPDATED to 6-file deletion + stdout verification)

1. Verify the phantom thread state still holds (`ls bridge/gtkb-root-directory-migration-*.md | grep -v post-verify` returns empty).
2. Verify the post-verify thread is unaffected (`ls bridge/gtkb-root-directory-migration-post-verify-*.md` returns 9 files: -010, -012, -013, -014, -015, -016, -017, -018, -019).
3. Edit `bridge/INDEX.md` to remove the 18 INDEX lines + 1 Document line + 1 inline comment.
4. Delete the 6 stale wrap-scan files from `.groundtruth/session/snapshots/{S319,S322,S324}/`.
5. Re-run wrap-scan with stdout output:
   - `python scripts/wrap_scan_hygiene.py --report-format json` → expect exit 0
   - `python scripts/wrap_scan_consistency.py --report-format json` → expect exit 0
6. Stage `bridge/INDEX.md`. The 6 deleted snapshot files are gitignored; deletions don't affect git.
7. Commit with scoped message referencing this bridge thread.
8. File post-impl report; quote relevant JSON output snippets as evidence (no persisted non-manifest files in snapshots tree).

---

## Rollback Notes

If post-impl reveals an unexpected issue:
- Revert the single commit via `git revert <sha>` — restores the 18 phantom INDEX entries (which are non-functional anyway).
- Snapshot files are gitignored and locally deleted; their content is non-canonical wrap-scan output and is captured in this bridge proposal's evidence.

---

## Decision Needed From Owner

This bridge does not require an additional owner decision. Standard Codex GO/NO-GO flow applies; the program-level scope is approved per S324 AskUserQuestion answer "Stop wrap; address phantom-INDEX errors first."

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
