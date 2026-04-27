GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 Revision 2

Status: GO

## Claim

Slice 5R may proceed. The revision resolves the prior blocker by preventing `GTKB-*` backlog rows with explicit Agent Red/adopter migration content from being silently classified as framework-owned, and it keeps the release-readiness lane deferred to its own corrected source-design slice.

## Evidence

- The proposal keeps Slice 5 scoped to the two file-based lanes plus the shared helper (`gtkb-isolation-016-phase8-wave2-slice5-005.md:15`).
- `_release_readiness_split.py` remains deferred to Slice 6 with the corrected source set from Codex `-002`: `memory/release-readiness.md`, KnowledgeDB document records, release-gate implementation surfaces, specs/WIs, and uncapped deliberation inventory (`gtkb-isolation-016-phase8-wave2-slice5-005.md:181`).
- The revised backlog classifier identifies `GTKB-*` rows with adopter content as conflicted and routes them to `unclassified_rows` with `classification_signal = "gtkb_prefix_with_adopter_content"` rather than `framework_rows` (`gtkb-isolation-016-phase8-wave2-slice5-005.md:56`, `:61`, `:74`, `:86`).
- The required regression test uses the current `GTKB-ISOLATION-016` row shape and asserts the row is not in `framework_rows`, is in `unclassified_rows`, and carries the conflict signal (`gtkb-isolation-016-phase8-wave2-slice5-005.md:94`, `:106`, `:123`, `:126`, `:130`).
- The live row still contains the Agent Red migration wording that motivated the finding (`memory/work_list.md:17`).
- The proposal also corrects the prior non-blocking fixture issue by leaving the dispatcher missing-lane fixture as `"ci"` (`gtkb-isolation-016-phase8-wave2-slice5-005.md:139`, `:141`, `:143`, `:161`).

## Implementation Conditions

Proceed under these conditions:

1. Keep the `GTKB-*` + adopter-content conflict behavior as `unclassified`, not `framework`.
2. Preserve the `classification_signal` field for unclassified conflict rows so Wave 3 has actionable evidence.
3. Include the `GTKB-ISOLATION-016` regression test in `tests/scripts/test_rehearse_backlog_split.py`.
4. Leave `tests/scripts/test_rehearse_isolation.py`'s missing-lane fixture on `"ci"` until `_ci_inventory.py` actually lands.
5. Run focused `ruff check`, `ruff format --check`, and the relevant targeted pytest suite before filing post-implementation evidence.

## Non-Blocking Notes

- The current `_ADOPTER_CONTENT_MARKERS` list is sufficient for the live `GTKB-ISOLATION-016` row because the row contains "Agent Red migration rehearsal." If implementation scans `blocks_blocked_by` as well as `status` and `next_step`, it will be more robust without changing the approved behavior.
- Keeping ambiguous GTKB-prefixed rows visible in `unclassified_rows` is preferable to overfitting a known-ID rule at this stage.

## Decision Needed From Owner

None.
