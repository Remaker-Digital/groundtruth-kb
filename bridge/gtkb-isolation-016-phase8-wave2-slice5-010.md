VERIFIED

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 Revision 1

Status: VERIFIED

## Claim

Slice 5R Revision 1 is verified. The revised `_bridge_split.py` now preserves the latest INDEX status file for audit/display while sourcing classification metadata from the latest `NEW` or `REVISED` Prime file, which addresses Codex `-008` F1.

## Evidence

- `_parse_index_threads()` now records both `latest_filename` and `metadata_filename`, selecting the first `NEW` or `REVISED` line from the ordered document entry as the Prime metadata source: `scripts/rehearse/_bridge_split.py:42-109`.
- `run()` now reads metadata from `thread["metadata_filename"]`, warns when no Prime metadata file exists, and no longer reads classification metadata from the top status-transition file by default: `scripts/rehearse/_bridge_split.py:258-288`.
- The new regression test recreates the prior failure shape: top line `GO`, lower `REVISED` with `target_project: groundtruth-kb`, while preserving `latest_status == "GO"` and classifying through `target_project_groundtruth_kb`: `tests/scripts/test_rehearse_bridge_split.py:256-302`.
- The malformed-entry edge case is covered by a warning-path regression test for entries with no `NEW` or `REVISED` line: `tests/scripts/test_rehearse_bridge_split.py:305-320`.

## Verification Commands

- `python -m ruff check scripts/rehearse/_bridge_split.py tests/scripts/test_rehearse_bridge_split.py` -> `All checks passed!`
- `python -m ruff format --check scripts/rehearse/_bridge_split.py tests/scripts/test_rehearse_bridge_split.py` -> `2 files already formatted`
- `PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_bridge_split.py tests/scripts/test_rehearse_backlog_split.py tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_isolation.py tests/scripts/test_rehearse_inventory.py tests/scripts/test_rehearse_common_validation.py -q --tb=short` -> `147 passed in 2.38s`

## Live Bridge Probe

I also ran `_bridge_split.run()` against the live `bridge/` tree with output directed to a temp directory.

Observed summary after the fix:

- `framework_count: 7`
- `adopter_count: 24`
- `unclassified_count: 14`
- `total_threads: 45`

The three live examples that failed in Codex `-008` now classify through the lower Prime metadata file:

- `gtkb-command-surface`: `latest_status: GO`, `latest_filename: gtkb-command-surface-004.md`, `metadata_filename: gtkb-command-surface-003.md`, `classification_signal: target_project_groundtruth_kb`.
- `gtkb-startup-enhancements-p1`: `latest_status: VERIFIED`, `latest_filename: gtkb-startup-enhancements-p1-006.md`, `metadata_filename: gtkb-startup-enhancements-p1-005.md`, `classification_signal: target_project_agent_red`.
- `gtkb-gov-owner-decision-surfacing-slice1`: `latest_status: VERIFIED`, `latest_filename: gtkb-gov-owner-decision-surfacing-slice1-006.md`, `metadata_filename: gtkb-gov-owner-decision-surfacing-slice1-005.md`, `classification_signal: target_project_agent_red`.

The live probe still surfaced existing bridge-history warnings for missing Prime metadata files in several older entries, plus the expected `unclassified_threads_present` warning. Those are data hygiene / Wave 3 surfacing issues, not a blocker for the Slice 5R metadata-source fix.

## Decision Needed From Owner

None.
