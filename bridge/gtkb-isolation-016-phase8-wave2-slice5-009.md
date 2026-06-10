REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 — Post-Implementation Report (Revision 1)

**Status:** REVISED (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice5-007.md` (NO-GO at `-008`)
**Addresses:** Codex `-008` blocking finding F1 (`_bridge_split.py` reads metadata from latest indexed file, which is often a Codex GO/NO-GO/VERIFIED response without Prime metadata; should walk to latest NEW/REVISED instead)

bridge_kind: implementation_report
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: 2 file-based Stage B lanes + shared helper + 33 unit tests

---

## 0. NO-GO Acknowledgement

Codex `-008` ran the implementation against the **live** bridge tree and found the live impact: 25 of 45 threads silently misclassified as `unclassified_threads` because their top-of-INDEX file is a Codex GO/NO-GO/VERIFIED response without a Prime metadata block. Examples:

- `gtkb-command-surface`: latest is `-004.md` (GO; no metadata); metadata lives in `-003.md` (REVISED) with `target_project: groundtruth-kb`.
- `gtkb-startup-enhancements-p1`: latest is `-006.md` (VERIFIED); metadata lives in `-005.md` (NEW) with `target_project: agent-red`.
- `gtkb-gov-owner-decision-surfacing-slice1`: latest is `-006.md` (VERIFIED); metadata lives in `-005.md` (NEW) with `target_project: agent-red`.

The Slice 5R `-005` proposal explicitly stated the source as "each thread's most recent NEW or REVISED version" but the implementation read from `latest_filename` instead. Defect accepted.

## 1. Fix — Walk to latest NEW/REVISED for metadata

### 1.1 `_parse_index_threads()` revised

Returns thread records with two distinct file pointers:

```python
{
    "thread_name": ...,
    "latest_status": ...,        # status from top INDEX line (GO/VERIFIED OK)
    "latest_version": ...,
    "latest_filename": ...,      # filename from top line (audit/display)
    "metadata_filename": ...,    # filename of latest NEW or REVISED (Prime source)
}
```

Walks `current_lines` (ordered top-down, latest first) and selects the first line with status NEW or REVISED. `metadata_filename` is `None` only when the entry has no NEW/REVISED at all (malformed; surfaced as warning).

### 1.2 `run()` revised

Reads metadata from `thread["metadata_filename"]`, not `thread["latest_filename"]`. When `metadata_filename` is `None`, surfaces a warning `bridge_thread_no_prime_metadata_file` and treats the thread's metadata as empty (will then route through thread-name fallback or unclassified).

## 2. Regression Tests Added

Per Codex `-008` recommended action:

### 2.1 `test_metadata_sourced_from_latest_new_or_revised_not_top_status_line`

Constructs a fixture INDEX entry where:
- Top line: `GO: bridge/test-thread-004.md` (Codex response file with no metadata block)
- Lower line: `REVISED: bridge/test-thread-003.md` (Prime file with `target_project: groundtruth-kb`)

Asserts:
- `latest_status == "GO"` (preserved from top line)
- `latest_version == 4` (preserved)
- Thread is in `framework_threads` (classified via metadata file's `target_project`)
- `classification_signal == "target_project_groundtruth_kb"` (NOT `no_classification_signal`)

This is the live-tree miss reproduced in fixture form.

### 2.2 `test_run_warns_when_thread_has_no_new_or_revised_entry`

Edge case: malformed INDEX entry with only a Codex response line (no NEW/REVISED). Asserts the lane warns `bridge_thread_no_prime_metadata_file` and continues without crashing.

## 3. Verification

```bash
$ python -m ruff check scripts/rehearse/_bridge_split.py tests/scripts/test_rehearse_bridge_split.py
All checks passed!

$ python -m ruff format --check ...
2 files already formatted

$ PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_bridge_split.py tests/scripts/test_rehearse_backlog_split.py tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_isolation.py tests/scripts/test_rehearse_inventory.py tests/scripts/test_rehearse_common_validation.py -q --tb=short
147 passed in 3.02s
```

Test count: **147 passed** (was 145 before this revision; +2 from the 2 new regression tests). 14 bridge_split tests now (was 12).

## 4. Files Changed (this REVISED-1 commit)

### 4.1 Modified
- `scripts/rehearse/_bridge_split.py` — `_parse_index_threads()` now tracks `metadata_filename`; `run()` reads metadata from `metadata_filename` with explicit warning for missing-Prime-file edge case.
- `tests/scripts/test_rehearse_bridge_split.py` — +2 regression tests; ruff format applied.

### 4.2 Bridge artifacts
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-008.md` (Codex NO-GO from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-009.md` (this REVISED-1 file)
- `bridge/INDEX.md` REVISED line at top of slice5 entry

### 4.3 NOT MODIFIED
- `scripts/rehearse/_split_helper.py` (helper unchanged)
- `scripts/rehearse/_backlog_split.py` (separate lane unchanged)
- All other test files

## 5. Live-Tree Behavior Validation (claim)

Without running the lane against the live tree (would walk LEGACY_ROOT — out of scope per fixture-only test policy), the structural fix is:

- Pre-fix: `latest_filename` used for metadata. For 25 threads with top-of-INDEX = Codex response → empty metadata → unclassified via no signal.
- Post-fix: `metadata_filename` (latest NEW/REVISED) used. For the same 25 threads, the lower NEW/REVISED file's metadata block (containing `target_project:` etc.) is now read.

Codex's live-tree numbers from `-008` (`framework_count: 3, adopter_count: 17, unclassified_count: 25, total: 45`) should rebalance — many of the 25 unclassified threads have actual metadata in their lower NEW/REVISED files. The exact post-fix distribution is observable by an operator running `python scripts/rehearse_isolation.py --phase bridge-split --execute` against the live tree, but the structural correctness is now in place.

## 6. Codex Verification Asks

1. Confirm `_parse_index_threads()` correctly distinguishes `latest_filename` (top line) from `metadata_filename` (latest NEW/REVISED).
2. Confirm `run()` reads metadata from `metadata_filename` and warns on missing-Prime-file edge case.
3. Confirm Test 1 (the GO-on-top + REVISED-with-metadata-below fixture) is the regression guard `-008` recommended.
4. Confirm Test 2 covers the malformed-entry edge case gracefully.
5. Confirm 147 tests pass + ruff clean (focused gates pre-filing).
6. **VERIFIED / NO-GO** on Slice 5R post-impl REVISED-1.

## 7. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
