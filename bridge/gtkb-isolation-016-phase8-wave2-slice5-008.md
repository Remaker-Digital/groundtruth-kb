NO-GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 Post-Implementation

Status: NO-GO

## Claim

Slice 5R is not verified. The focused style checks and targeted test suite pass, and the backlog splitter F1 regression appears fixed, but `_bridge_split.py` still violates the approved bridge metadata-source contract. It reads metadata from the latest indexed bridge file, which is often a Loyal Opposition response without the Prime metadata block, instead of using the most recent `NEW` or `REVISED` Prime file for that thread.

## Evidence

- Verification commands passed:
  - `python -m ruff check scripts/rehearse/_split_helper.py scripts/rehearse/_bridge_split.py scripts/rehearse/_backlog_split.py tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_bridge_split.py tests/scripts/test_rehearse_backlog_split.py` -> `All checks passed!`
  - `python -m ruff format --check scripts/rehearse/_split_helper.py scripts/rehearse/_bridge_split.py scripts/rehearse/_backlog_split.py tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_bridge_split.py tests/scripts/test_rehearse_backlog_split.py` -> `6 files already formatted`
  - `PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_bridge_split.py tests/scripts/test_rehearse_backlog_split.py tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_isolation.py tests/scripts/test_rehearse_inventory.py tests/scripts/test_rehearse_common_validation.py -q --tb=short` -> `145 passed in 2.71s`
- The approved proposal defines the bridge split source as `bridge/INDEX.md` for thread inventory and latest status, plus `bridge/*.md` metadata blocks from each thread's most recent `NEW` or `REVISED` version: `bridge/gtkb-isolation-016-phase8-wave2-slice5-003.md:47`.
- The same proposal makes `target_project` and `work_item_ids` the first two classification signals before thread-name fallback: `bridge/gtkb-isolation-016-phase8-wave2-slice5-003.md:70-76`.
- The implementation records only the latest INDEX file for each thread, regardless of status: `scripts/rehearse/_bridge_split.py:42-66`.
- The implementation then reads that latest file for metadata parsing: `scripts/rehearse/_bridge_split.py:232-247`.
- Live inspection of `bridge/INDEX.md` found 16 threads where the latest file lacks metadata but the latest `NEW` or `REVISED` file has metadata. Examples:
  - `gtkb-command-surface`: latest file `gtkb-command-surface-004.md` (`GO`), metadata file `gtkb-command-surface-003.md`, `target_project: groundtruth-kb`, `work_item_ids: [GTKB-COMMAND-SURFACE]`.
  - `gtkb-startup-enhancements-p1`: latest file `gtkb-startup-enhancements-p1-006.md` (`VERIFIED`), metadata file `gtkb-startup-enhancements-p1-005.md`, `target_project: agent-red`.
  - `gtkb-gov-owner-decision-surfacing-slice1`: latest file `gtkb-gov-owner-decision-surfacing-slice1-006.md` (`VERIFIED`), metadata file `gtkb-gov-owner-decision-surfacing-slice1-005.md`, `target_project: agent-red`.
- A live `_bridge_split.run({}, temp_output, dry_run=False)` classified those examples as `unclassified_threads` with `classification_signal: no_classification_signal`, producing a summary of `framework_count: 3`, `adopter_count: 17`, `unclassified_count: 25`, `total: 45`.

## Blocking Finding

F1 - `_bridge_split.py` selects the latest status-transition file as the metadata source instead of the latest Prime request file.

Impact: completed or reviewed bridge threads whose current top status is `GO`, `NO-GO`, or `VERIFIED` can lose their `target_project` and `work_item_ids` metadata during rehearsal splitting. That causes false unclassified output and weakens the GT-KB/adopter boundary rehearsal evidence.

## Recommended Action

Update `_parse_index_threads()` or the bridge split run path to preserve ordered status lines for each document entry. Keep the current latest status/latest version behavior from the first status line, but choose the first existing file in that same entry whose status is `NEW` or `REVISED` as the classification metadata source.

Add a regression test where an INDEX entry has a `GO` or `VERIFIED` file first and a lower `NEW` or `REVISED` file with `target_project` metadata below it. Assert that `latest_status` remains the top status, while classification uses the Prime metadata file.

## Decision Needed From Owner

None.
