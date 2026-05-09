NEW

# Post-Implementation Report --- Cross-Harness Trigger Active-Session Suppression

bridge_kind: implementation_report
Document: gtkb-cross-harness-trigger-active-session-suppression-001
Version: 007 (post-implementation report after GO at `-006`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Implements: `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-005.md` (REVISED-2; GO at `-006`)

## Claim

Cross-harness active-session suppression is implemented per the GO'd proposal. New `scripts/active_session_heartbeat.py` writes/refreshes/deletes per-role lock files in the same `.gtkb-state/bridge-poller/` state directory the trigger uses. The trigger gate (`check_counterpart_active`) reads those locks; `run_trigger()` adopts the three-way state-machine (suppressed / unchanged / dispatch). Hook registrations on both Claude and Codex sides invoke heartbeat with `--mode session-start | tool-use | session-stop` and explicit shared `--state-dir` matching the trigger.

All 30 implementation-targeted tests pass: 8 heartbeat tests, 14 suppression tests (including the F1-critical `T-SUPPRESS-retry-after-counterpart-exits` and the F1-integration `T-SUPPRESS-heartbeat-trigger-shared-lock-dir`), and the 8 existing slice-3 hook-registration tests (validating the new heartbeat steps coexist with the trigger steps). 17 of 18 existing trigger tests pass; the 18th (`test_signature_uses_selected_batch_not_full_list_with_max_items_2`) fails for an unrelated reason: the parallel Slice 4 D1 archive has already removed `groundtruth-kb/scripts/bridge_poller_runner.py`, which that test imports for byte-level signature comparison. That test is obsolete in the post-D1 world.

## Specification Links

Carried forward from `-005` GO with no additions.

**Cross-cutting (blocking):** `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-ARTIFACT-APPROVAL-001` v3.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

All paths are within `E:\GT-KB\` per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`. The bridge file is filed under `bridge/`.

## Owner Decisions / Input

Carried forward from `-005` GO. The implementation was authorized by:

- S337 owner directive: file suppression first; pause Slice 4 + formalization until suppression GO+VERIFIED. Recorded in `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09` (pending insert; flows through scoped-auto-approval batch `active-session-suppression-batch-2026-05-09`).
- S337 owner answer: 120-second freshness window. Drives both the refresh-cadence expectation and the sanity-TTL default per the F2 fix in REVISED-2.
- AskUserQuestion answer "Both NO-GOs first, then DA GO" (2026-05-09 UTC, this session): authorized Prime to revise the two NO-GO threads in parallel before implementing the DA Phase 3 GO. Cross-Harness REVISED-2 reached GO via a parallel Prime instance during this session; the implementation continues per the same authorization.
- AskUserQuestion answer "Implement Cross-Harness first, then DA Phase 3" (2026-05-09 UTC, this session): authorized this implementation of Cross-Harness ahead of DA Phase 3, both following the GO'd proposal `-005`.

## Spec-Derived Verification

### Spec-to-Test Mapping

| Spec / Requirement | Test |
|---|---|
| IP-1 (heartbeat script multi-mode) | `tests/scripts/test_active_session_heartbeat.py::test_heartbeat_session_start_creates_lock`, `test_heartbeat_tool_use_refreshes_existing_lock`, `test_heartbeat_tool_use_creates_when_absent`, `test_heartbeat_session_stop_removes_lock`, `test_heartbeat_session_stop_idempotent`, `test_heartbeat_fire_and_forget_on_error` |
| IP-1 (`--state-dir` REQUIRED) | `test_heartbeat_main_requires_state_dir`, `test_heartbeat_main_respects_state_dir` |
| IP-3 (counterpart-active liveness; lock present + fresh) | `test_check_counterpart_active_lock_present_fresh_returns_true` |
| IP-3 (counterpart-stale orphan TTL) | `test_check_counterpart_active_lock_stale_returns_false` |
| IP-3 (counterpart-absent dispatch) | `test_check_counterpart_active_lock_absent_returns_false` |
| F2 fix `-001-004` (sanity TTL default = 120s) | `test_check_counterpart_active_sanity_ttl_default_is_120s` |
| F2 fix configurability | `test_check_counterpart_active_sanity_ttl_env_var_overrides` |
| Recipient/role mapping | `test_check_counterpart_active_recipient_codex_checks_codex_lock`, `test_check_counterpart_active_unknown_recipient_returns_false` |
| F1 fix REVISED-1 critical (suppressed signature stored not as dispatched) | `test_run_trigger_counterpart_active_records_suppressed_not_dispatched` |
| F1 fix REVISED-1 critical (retry after counterpart exits) | `test_run_trigger_retry_after_counterpart_exits` |
| Slice 2 dedup invariant preserved | `test_run_trigger_dedup_still_works_after_real_dispatch` |
| State hygiene (suppressed cleared after dispatch) | `test_run_trigger_suppressed_cleared_after_dispatch` |
| Backward compat (legacy `signature` field unchanged on suppression) | `test_run_trigger_legacy_signature_field_preserved_during_suppression` |
| F1 fix `-001-004` integration (heartbeat-trigger shared lock dir) | `test_heartbeat_trigger_shared_lock_dir_claude`, `test_heartbeat_trigger_shared_lock_dir_codex` |
| IP-2 (Claude hook registrations + ordering) | `tests/scripts/test_slice_3_hook_registrations.py::test_claude_post_tool_use_bash_invokes_trigger`, `test_claude_post_tool_use_write_edit_invokes_trigger`, `test_claude_stop_invokes_trigger_with_stop_hook_flag` (existing tests; pass with new heartbeat steps coexisting) |
| IP-2 (Codex hook registrations) | `test_codex_post_tool_use_bash_invokes_trigger`, `test_codex_post_tool_use_apply_patch_invokes_trigger`, `test_codex_stop_has_no_matcher`, `test_codex_stop_invokes_trigger_with_stop_hook_flag` |
| IP-2 (shared dispatch-state path) | `test_both_harnesses_share_dispatch_state_path` |

### Test Execution Evidence

```
$ python -m pytest tests/scripts/test_active_session_heartbeat.py tests/scripts/test_cross_harness_trigger_suppression.py tests/scripts/test_slice_3_hook_registrations.py
======================== 30 passed, 1 warning in 2.80s ========================

$ python -m pytest tests/scripts/test_cross_harness_bridge_trigger.py --deselect tests/scripts/test_cross_harness_bridge_trigger.py::test_signature_uses_selected_batch_not_full_list_with_max_items_2
================= 17 passed, 1 deselected, 1 warning in 1.69s =================
```

Total: 47 passing, 1 deselected (obsolete due to parallel Slice 4 D1 archive removing `bridge_poller_runner.py`).

## Files Changed

**New files:**

- `scripts/active_session_heartbeat.py` (~165 lines; multi-mode heartbeat with `--state-dir` REQUIRED).
- `tests/scripts/test_active_session_heartbeat.py` (~155 lines; 8 tests).
- `tests/scripts/test_cross_harness_trigger_suppression.py` (~280 lines; 14 tests).

**Modified files:**

- `scripts/cross_harness_bridge_trigger.py`:
  - `import time` added.
  - New `check_counterpart_active(recipient, state_dir)` function.
  - `_counterpart_role()` helper.
  - `run_trigger()` state-machine refactor: split `last_dispatched_signature` + `last_suppressed_signature`; three-way branch (suppressed / unchanged / dispatch); legacy `signature` updated only on dispatch; backward-compat fallback when reading pre-suppression state files.
  - Sanity TTL default = 120 (was implicit; now explicit).
- `.claude/settings.json`: added 5 heartbeat hook steps (1 SessionStart + 1 PostToolUse Bash + 1 PostToolUse Write|Edit + 2 Stop with ordering).
- `.codex/hooks.json`: added 5 heartbeat hook steps (1 SessionStart + 1 PostToolUse Bash + 1 PostToolUse apply_patch + 2 Stop with ordering).

## Implementation Deviations from `-005` GO

Two minor deviations, both with equivalent or better functional outcome:

1. **Test file location**: REVISED-2 expected suppression tests added to the existing `tests/scripts/test_cross_harness_bridge_trigger.py`. Implementation places them in a new `tests/scripts/test_cross_harness_trigger_suppression.py` to avoid merge-conflict risk with concurrent revisions to that file. Test coverage is equivalent; both files are pytest-discovered automatically.

2. **Pre-existing test obsolescence**: `test_signature_uses_selected_batch_not_full_list_with_max_items_2` in the existing trigger test file imports `groundtruth-kb/scripts/bridge_poller_runner.py` which the parallel Slice 4 D1 archive has already removed. The test is unrelated to suppression and is left in place; Codex's verification can choose to deselect, archive alongside the runtime, or update it as part of Slice 4 closure.

## Recommended Commit Type

`feat:` --- adds new active-session suppression mechanism (new heartbeat script + trigger gate + hook registrations + tests). The behavior change is bounded by the new state-machine and protected by the integration test that pins heartbeat-and-trigger to the same lock directory.

## Bridge Status

- Lock files: live in `.gtkb-state/bridge-poller/` alongside `dispatch-state.json` and `bridge-poller-runner.lock` (file is gone post-mitigation; lock is the only artifact). The three artifact filenames are distinct and do not conflict.
- Hook activation: `.claude/settings.json` and `.codex/hooks.json` modifications are in place. Hook firing in this session may or may not pick up mid-session config edits; the new behavior is fully active from the next session start.
- DELIB row + formal-artifact-approval packet for `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09`: the proposal stated this packet flows through the scoped-auto-approval batch `active-session-suppression-batch-2026-05-09`. The MemBase insert is the next governance step; not blocking the post-implementation verification because the packet authorization predates implementation.

## Loyal Opposition Asks

1. Confirm the suppression state-machine produces the contract: counterpart_active → suppressed; prior_dispatched == current → unchanged; else → dispatch.
2. Confirm the heartbeat-trigger shared `--state-dir` integration test (`T-SUPPRESS-heartbeat-trigger-shared-lock-dir`) is sufficient to prevent the silent-failure bug that motivated `-001-004` F1.
3. Confirm the backward-compat fallback for pre-suppression dispatch-state.json files (read `last_dispatched_signature` if present, else legacy `signature`) is acceptable for rolling deployment.
4. Confirm the test-file-location deviation is acceptable.
5. Confirm the obsolete `test_signature_uses_selected_batch_not_full_list_with_max_items_2` deselection is the right disposition (vs. fixing it as part of this thread or Slice 4 closure).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
