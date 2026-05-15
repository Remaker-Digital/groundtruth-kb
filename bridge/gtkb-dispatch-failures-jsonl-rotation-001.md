# Implementation Proposal — dispatch-failures.jsonl Rotation

bridge_kind: prime_implementation_proposal

## Summary

Add size-or-age-based rotation to `.gtkb-state/bridge-poller/dispatch-failures.jsonl`. Live inspection in S350 shows the file contains 16,075 records with no pruning since its first write; the file accumulates monotonically as the cross-harness trigger fire-and-forget logger appends every dispatch failure forever. Most recent entries are diagnostically irrelevant (single-harness-topology-skip records from a transient 2026-05-13 role-map drift) but still consume read time on every diagnose run.

## Background

Discovered during S350 (2026-05-14) liveness investigation. `python scripts/cross_harness_bridge_trigger.py --diagnose --state-dir .gtkb-state/bridge-poller` reports `Total in dispatch-failures.jsonl: 16075`. Distribution by error class:

- 15,878 "other (unknown)" — mostly topology-skip records from 2026-05-13 role-map drift.
- 147 WinError 32 (sharing violation) — last 2026-05-09.
- 23 WinError 5 (access denied) — last 2026-05-09.
- 17 WinError 2 (file not found) — last 2026-05-09.
- 4 temp-path permission denied — last 2026-05-09.
- 3 NameError / 3 AttributeError — last 2026-05-12.

The actively useful diagnostic window is the most recent ~24-48h. Earlier records are historical noise that grow unbounded.

## In-Root Placement Evidence

All target paths and runtime artifacts in-root under `E:\GT-KB`:

- `E:\GT-KB\scripts\cross_harness_bridge_trigger.py` — `_record_dispatch_failure` (the writer; gains rotation check).
- `E:\GT-KB\platform_tests\scripts\test_cross_harness_bridge_trigger.py` — rotation regression tests.
- `E:\GT-KB\.gtkb-state\bridge-poller\dispatch-failures.jsonl` — rotated in-place.
- `E:\GT-KB\.gtkb-state\bridge-poller\dispatch-failures.jsonl.<N>` — rotation rollover files (in-root).

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, all target paths and runtime artifacts are within the GT-KB platform root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — file bridge authority; dispatch-failures.jsonl is operational evidence, not bridge state, but the rotation must not destroy in-flight signal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — operational artifact lifecycle hygiene (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — rotation preserves traceability via numbered rollover files (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — record lifecycle: appended → rotated → preserved-or-pruned (advisory).
- `.claude/rules/bridge-essential.md` § Bridge Dispatch Enablement Contract — dispatch substrate health.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol invariants.
- `.claude/rules/codex-review-gate.md` — review gate.

## Prior Deliberations

- `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-003.md` GO at `-004` — established `_classify_failure_record` and the failure-distribution-not-collapsed contract. This proposal preserves both.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*` — Slice 4 retirement preserved the state path; rotation has been latent technical debt since then.
- No prior deliberation on dispatch-failures-log rotation surfaced.

## Owner Decisions / Input

Owner directive in S350 (2026-05-14): "Please continue to parallelize work" — explicit authorization to file additional captureable defects in parallel with the worker-delivery slice queue. Per `feedback_fix_problems_without_auq`, this is a clear-path protocol-hygiene fix (no scope ambiguity) and is filed directly without additional AUQ.

## Requirement Sufficiency

Existing requirements sufficient. The dispatch-failures.jsonl writer's purpose (fire-and-forget audit log) is unchanged; this proposal adds bounded-size discipline.

## target_paths

- `scripts/cross_harness_bridge_trigger.py` (`_record_dispatch_failure` rotation logic)
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` (rotation regression tests)

## Implementation Plan

1. **Rotation policy**: when `_record_dispatch_failure` is about to write and the current file size exceeds `GTKB_DISPATCH_FAILURES_MAX_BYTES` (default 1 MiB, configurable via env), rename `dispatch-failures.jsonl` to `dispatch-failures.jsonl.1` (overwriting any prior `.1`). Cap rollover history at 1 file (most recent rotation only). Total bounded disk: ~2 MiB.
2. **Atomic rename**: use the existing `_rename_with_retry` helper for Windows-safe atomic rename.
3. **Bounded read in diagnose**: separately, `_emit_diagnose_summary` reads the full file. After rotation, the function only sees current-segment records. Add a flag-controlled read-rollover option (`--include-rotated-failures`) for forensic deep dives. Default behavior is current-segment only.
4. **Regression tests**:
   - `test_dispatch_failures_rotates_when_size_exceeds_threshold`: append until file exceeds threshold; assert rotation occurred and `.1` exists with prior content.
   - `test_dispatch_failures_capped_rollover_history`: rotate twice; assert only `.1` exists (no `.2`).
   - `test_dispatch_failures_threshold_configurable_via_env`: set `GTKB_DISPATCH_FAILURES_MAX_BYTES=512` and verify rotation at the lower bound.
   - `test_diagnose_default_reads_current_segment_only`: stage rotation, assert diagnose reports the post-rotation record count.
   - `test_diagnose_include_rotated_reads_both_segments`: same fixture; assert diagnose reads both files when `--include-rotated-failures` is set.

## Spec-to-Test Mapping

- `GOV-FILE-BRIDGE-AUTHORITY-001` → `test_dispatch_failures_rotates_when_size_exceeds_threshold` (rotation preserves the audit-trail invariant via numbered rollover, not destruction).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → one test per assertion class.

## Risks

- **Forensic record loss**: with cap-1 rollover, oldest records eventually disappear. *Mitigation:* `--include-rotated-failures` reads `.1`; for longer retention, owner can manually preserve `.1` files OR a future proposal can raise the rollover cap.
- **Atomic rename on Windows during concurrent writes**: same race class as `_write_dispatch_state`. *Mitigation:* reuse `_rename_with_retry` per the established pattern.
- **Threshold too small / too large**: 1 MiB is a heuristic. *Mitigation:* env-var configurable.

## Rollback

Remove the rotation branch from `_record_dispatch_failure`, remove the `--include-rotated-failures` flag and tests, revert any rollover files manually if desired.

## Verification Procedure

1. `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short` — all existing + 5 new tests pass.
2. Manual smoke: stage failure records until rotation fires; assert two files exist and the current file is bounded.
3. Run preflights — both must pass.

## Acceptance Criteria

- Rotation fires at the configured threshold and the rollover history is capped.
- Diagnose default behavior shows only current-segment failures (or the `--include-rotated-failures` flag accesses the prior segment).
- All preflights pass.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
