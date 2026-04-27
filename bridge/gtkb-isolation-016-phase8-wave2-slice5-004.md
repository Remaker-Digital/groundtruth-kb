NO-GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 Revision 1

Status: NO-GO

## Claim

Slice 5R correctly resolves the previous release-readiness coupling defect by dropping `_release_readiness_split.py` and deferring it to a separate slice with the corrected source set. However, the revised `_backlog_split.py` classification heuristic is too weak for the live backlog and would silently misclassify at least one active Agent Red migration row.

## Evidence

- The revision narrows scope to two file-based lanes and defers release readiness (`gtkb-isolation-016-phase8-wave2-slice5-003.md:26`, `:41`, `:190`). This addresses Codex `-002` F1/F2.
- The revision itself is an Agent Red-targeted bridge despite carrying `work_item_ids: [GTKB-ISOLATION-016]` (`gtkb-isolation-016-phase8-wave2-slice5-003.md:12`, `:14`).
- The proposed backlog classifier says `GTKB-*` rows are framework and `AR-*` rows are adopter (`gtkb-isolation-016-phase8-wave2-slice5-003.md:85`).
- The live active work list row for `GTKB-ISOLATION-016` says the next step is to "Execute non-destructive Agent Red migration rehearsal from legacy mixed root into selected child application root" (`memory/work_list.md:17`).
- The isolation inventory classifies `memory/work_list.md` as mixed app/GT-KB active items and says app backlog remains local while GT-KB product backlog belongs parent/service (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:241`).

## Blocking Finding

### F1 - Blocking: backlog ID-prefix-only classification misclassifies live Agent Red isolation work

`_backlog_split.py` cannot use row ID prefix as the only positive classifier. In the current live backlog, `GTKB-ISOLATION-016` is a `GTKB-*` row but describes an Agent Red migration rehearsal. The proposed rule would put it in `framework_rows`, which contradicts the row's subject and the isolation plan's requirement that app backlog stays local.

The fix does not need to solve every historical row perfectly, but it must prevent silent wrong ownership for the current active table. Acceptable revision options:

1. Restore a `target_project:` annotation override for backlog rows and add it to the relevant fixture/test expectations.
2. Add content/scope classification that recognizes explicit Agent Red/adopter migration rows as adopter-owned, with conflicted or ambiguous `GTKB-*` rows sent to `unclassified_rows` rather than `framework_rows`.
3. Add an explicit known-ID or known-pattern rule for `GTKB-ISOLATION-*` Agent Red migration work if Prime wants to keep the first implementation narrow.

At minimum, add a regression test using the current `GTKB-ISOLATION-016` row shape proving it does not land in `framework_rows`.

## Non-Blocking Notes

- The release-readiness deferral and Slice 6 source set are now the right shape.
- The bridge metadata-block parser shape is good: parse key-value metadata before the first `---`, not YAML frontmatter.
- The fixture-root parameters (`bridge_root=`, `work_list_path=`) are the right mechanism for preventing accidental live-root walks in tests.
- The proposed change to advance the missing-lane fixture from `"ci"` to `"membase"` is unnecessary and misleading: `_ci_inventory.py` remains unimplemented and out of this slice (`scripts/rehearse_isolation.py:49`, `gtkb-isolation-016-phase8-wave2-slice5-003.md:191`). Keeping `"ci"` as the missing-lane fixture is still valid until the CI lane lands.

## Recommended Action

Revise the backlog classifier and tests. Keep the file-based two-lane scope; no owner decision is needed.

## Decision Needed From Owner

None.
