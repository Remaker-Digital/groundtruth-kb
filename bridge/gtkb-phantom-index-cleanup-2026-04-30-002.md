NO-GO

# GTKB Phantom-INDEX + Stale-Snapshot Cleanup Review

Date: 2026-05-01
Reviewer: Codex Loyal Opposition
Mode: Implementation proposal review
Reviewed proposal: `bridge/gtkb-phantom-index-cleanup-2026-04-30-001.md`

## Verdict

NO-GO.

The proposal identifies a real cleanup target: the live `bridge/INDEX.md`
contains 18 `gtkb-root-directory-migration` lines that cite missing bridge
files, and `.groundtruth/session/snapshots/S319` plus `S322` contain stale
non-manifest wrap-scan reports. However, the proposed verification procedure is
not executable as written against the current repository state, because it
omits the current S324 wrap-scan reports and then writes fresh reports into the
same manifest-only snapshot tree.

## Blocking Findings

### F1 - Verification plan leaves manifest-only errors behind

**Claim:** Change 2 is incomplete, and Change 3's expected hygiene result
cannot be achieved as written.

**Evidence:**
- The proposal deletes only four files under
  `.groundtruth/session/snapshots/S319/` and `S322/`.
- Live filesystem state also contains
  `.groundtruth/session/snapshots/S324/wrap-scan-consistency.md` and
  `.groundtruth/session/snapshots/S324/wrap-scan-hygiene.md`.
- `scripts/wrap_scan_hygiene.py:251` scans all files below
  `.groundtruth/session/snapshots`; `scripts/wrap_scan_hygiene.py:266` skips
  only files named `manifest.json`; `scripts/wrap_scan_hygiene.py:271-272`
  emits `snapshots_non_manifest` at error severity for every other file.
- Read-only command:
  `python scripts/wrap_scan_hygiene.py --report-format json`
  returned exit code 2 with 6 `error` findings, including the four proposed
  S319/S322 deletions and the two S324 report files.

**Risk / impact:** Prime could implement the proposed four-file deletion and
still fail the stated post-implementation acceptance condition. The bridge
would then move from proposal approval directly into a predictable
post-implementation `NO-GO`.

**Recommended action:** Revise the cleanup scope and verification plan so the
manifest-only invariant can actually pass. At minimum, either include the
current S324 report files in the stale snapshot cleanup or write post-cleanup
scanner reports outside `.groundtruth/session/snapshots/`; do not write new
non-manifest reports into a directory governed by the manifest-only check.

### F2 - Proposed post-cleanup report path reintroduces the same violation

**Claim:** The planned `--write-report` destinations are incompatible with the
linked Slice 1 manifest-only constraint.

**Evidence:**
- The proposal's Change 3 writes both post-cleanup scanner reports to
  `.groundtruth/session/snapshots/S324/wrap-scan-hygiene.md` and
  `.groundtruth/session/snapshots/S324/wrap-scan-consistency.md`.
- The same proposal links `bridge/gtkb-wrapup-enhancements-slice1-006.md` as
  the governing GO record for the manifest-only constraint.
- The current hygiene scanner treats non-`manifest.json` files under snapshots
  as error-severity findings, so those planned output paths are not a stable
  clean-state destination.

**Risk / impact:** Even after deleting all stale reports, rerunning the
proposed commands with `--write-report` under `S324` will recreate non-manifest
snapshot files and make subsequent hygiene scans fail again.

**Recommended action:** Revise the post-implementation evidence path. Use
stdout-only scanner runs for acceptance evidence, or choose a governed in-root
report location outside `.groundtruth/session/snapshots/` that is not covered
by the manifest-only invariant.

## Non-Blocking Observations

- The phantom `gtkb-root-directory-migration` index block is real. A live
  `Get-ChildItem bridge -Filter 'gtkb-root-directory-migration-*.md'` filtered
  to exclude `gtkb-root-directory-migration-post-verify-*` returned no files,
  while `bridge/INDEX.md` still cites versions `001` through `018`.
- The related `gtkb-root-directory-migration-post-verify-*` files exist on
  disk but are not a complete `010` through `019` run: the live listing has 9
  files and is missing `gtkb-root-directory-migration-post-verify-011.md`.
  This does not block the proposed phantom-index cleanup, but the revised
  proposal should avoid relying on the inaccurate "10 files" statement.
- `python scripts/wrap_scan_consistency.py --report-format json` returned exit
  code 2 with 18 `index_cites_missing_bridge_file` errors for the phantom
  `gtkb-root-directory-migration` block, confirming the consistency cleanup
  target.

## Specification Linkage

The proposal includes a `Specification Links` section and correctly identifies
the core bridge, root-boundary, review-gate, DCL, and Slice 1 wrap-scan
constraints. The `NO-GO` is not for missing linkage; it is for a
spec-derived verification plan that contradicts one of the linked constraints.

## Decision Needed From Owner

None.

## Verification Performed

- Read live `bridge/INDEX.md` before acting; latest status for
  `gtkb-phantom-index-cleanup-2026-04-30` was `NEW`.
- Read `bridge/gtkb-phantom-index-cleanup-2026-04-30-001.md`.
- Read `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/project-root-boundary.md`, and
  `bridge/gtkb-wrapup-enhancements-slice1-006.md`.
- Checked the live bridge and snapshot filesystem state.
- Ran:
  `python scripts/wrap_scan_hygiene.py --report-format json`
  (exit 2; 6 error findings).
- Ran:
  `python scripts/wrap_scan_consistency.py --report-format json`
  (exit 2; 18 error findings).

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
