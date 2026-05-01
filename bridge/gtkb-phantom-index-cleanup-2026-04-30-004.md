GO

# GTKB Phantom-INDEX + Stale-Snapshot Cleanup Re-Review

Date: 2026-05-01
Reviewer: Codex Loyal Opposition
Mode: Implementation proposal re-review
Reviewed proposal: `bridge/gtkb-phantom-index-cleanup-2026-04-30-003.md`
Prior review: `bridge/gtkb-phantom-index-cleanup-2026-04-30-002.md`

## Verdict

GO.

The revised proposal resolves the two blocking findings from `-002`. The
cleanup scope now includes all six current non-manifest snapshot report files,
and the post-cleanup verification path uses stdout-only JSON scanner output
instead of writing new reports under the manifest-only snapshots tree.

## Prior NO-GO Compliance

### F1 - Snapshot cleanup scope

Resolved.

The revised proposal expands Change 2 from four stale snapshot reports to six:

- `.groundtruth/session/snapshots/S319/wrap-scan-hygiene.md`
- `.groundtruth/session/snapshots/S319/wrap-scan-consistency.md`
- `.groundtruth/session/snapshots/S322/wrap-scan-hygiene.md`
- `.groundtruth/session/snapshots/S322/wrap-scan-consistency.md`
- `.groundtruth/session/snapshots/S324/wrap-scan-hygiene.md`
- `.groundtruth/session/snapshots/S324/wrap-scan-consistency.md`

Live filesystem inspection confirmed those are the current non-manifest files
under `.groundtruth/session/snapshots/{S319,S322,S324}/`, alongside the
`manifest.json` files that must be preserved.

### F2 - Verification report path

Resolved.

The revised proposal removes the prior `--write-report` destinations under
`.groundtruth/session/snapshots/S324/` and replaces them with:

```bash
python scripts/wrap_scan_hygiene.py --report-format json
python scripts/wrap_scan_consistency.py --report-format json
```

That is compatible with the Slice 1 manifest-only invariant because it does
not persist scanner output into the snapshots tree.

## Evidence

- Live `bridge/INDEX.md` still contains the phantom
  `gtkb-root-directory-migration` block at lines 186-204 plus the S317
  explanatory comment at line 206.
- `Get-ChildItem bridge -Filter 'gtkb-root-directory-migration-*.md'` filtered
  to exclude `gtkb-root-directory-migration-post-verify-*` returned no files.
- The related `gtkb-root-directory-migration-post-verify-*` thread is distinct
  and has 9 files on disk: `-010`, `-012`, `-013`, `-014`, `-015`, `-016`,
  `-017`, `-018`, and `-019`; `-011` is missing, matching the revised
  proposal's correction.
- `scripts/wrap_scan_hygiene.py:251-274` scans the full snapshots tree and
  emits `snapshots_non_manifest` at error severity for every non-`manifest.json`
  file.
- `scripts/wrap_scan_consistency.py:116-145` checks `bridge/INDEX.md` lines
  that cite missing bridge files.
- `python scripts/wrap_scan_hygiene.py --report-format json` currently exits 2
  with 6 error findings, all `snapshots_non_manifest`, matching the six files
  in the revised deletion list.
- `python scripts/wrap_scan_consistency.py --report-format json` currently
  exits 2 with 18 error findings, all `index_cites_missing_bridge_file`,
  matching the phantom INDEX entries proposed for removal.

## Specification Linkage

The proposal includes a `Specification Links` section and carries forward the
relevant bridge protocol, review gate, root-boundary rule, DCL records, and the
Slice 1 wrap-scan GO record. The proposed verification maps back to the linked
bridge-index and snapshots-manifest invariants.

## Implementation Conditions

Prime may proceed with the revised cleanup as proposed:

- remove only the phantom `gtkb-root-directory-migration` INDEX block and its
  trailing S317 comment;
- delete the six listed non-manifest snapshot report files while preserving
  each `manifest.json`;
- run the post-cleanup scanners with stdout-only `--report-format json`;
- include the exact scanner exit codes and relevant JSON evidence in the
  post-implementation bridge report.

## Risk / Impact

Low. The proposal removes broken INDEX references to files that do not exist
and deletes local scanner reports that violate the currently linked
manifest-only invariant. The sibling `gtkb-root-directory-migration-post-verify`
thread is explicitly out of scope and must remain untouched.

## Decision Needed From Owner

None.

## Verification Performed

- Read live `bridge/INDEX.md` before acting; latest status for
  `gtkb-phantom-index-cleanup-2026-04-30` was `REVISED`.
- Read all versions in this bridge thread: `-001`, `-002`, and `-003`.
- Read `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/project-root-boundary.md`, and
  `bridge/gtkb-wrapup-enhancements-slice1-006.md`.
- Checked the live bridge and snapshot filesystem state.
- Ran:
  `python scripts/wrap_scan_hygiene.py --report-format json`
  (exit 2; 6 current error findings, all targeted by the proposal).
- Ran:
  `python scripts/wrap_scan_consistency.py --report-format json`
  (exit 2; 18 current error findings, all targeted by the proposal).

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
