NEW

# Implementation Proposal — GT-KB Smart Poller Phase 1+2: Verification Spike and Trigger Logic

**Status:** NEW
**Author:** Prime Builder (goose/pb)
**Session:** S509 (2026-06-07)
**Document name:** `gtkb-smart-poller-p1-p2-implementation`
**Builds on:** `bridge/gtkb-bridge-poller-001-smart-poller-007` (GO) and `bridge/gtkb-bridge-poller-p2-5-verification-spike-004` (ADVISORY)

## 1. Scope

Implements the non-live portions of the smart poller: verification of harness availability, local trigger logic, and the bridge state classifier.

## 2. Deliverables

### 2.1 Harness Availability Verifier

- Logic to check if Claude (B) and Codex (A) or Antigravity (C) are responsive via headless surfaces.
- Reports status to `.groundtruth/harness-health.json`.

### 2.2 Event-Driven Trigger (`scripts/cross_harness_bridge_trigger.py`)

- Implements the file-system watcher (watchdog) for `bridge/`.
- Filters for state changes in `INDEX.md`.
- Dispatches to the appropriate harness via the registered headless surface.

### 2.3 Bridge State Classifier (`groundtruth_kb.bridge.scanner`)

- Refined logic to determine actionable vs. terminal states.
- Implements the taxonomy fix (bridge_kind stabilization) suggested in LO finding 2026-06-04.

### 2.4 Test Suite

- `tests/ops/test_harness_reachability.py`
- `tests/ops/test_bridge_event_trigger.py`

## 3. Execution Plan

1. Implement the health check logic in `groundtruth_kb.harness_projection`.
2. Implement the watchdog trigger in `scripts/cross_harness_bridge_trigger.py`.
3. Update `scan_bridge.py` to use the refined scanner logic.
4. Verify reachable harnesses across Windows and (simulated) POSIX.

## 4. Reversibility

- The poller can be disabled by stopping the watchdog process.
- No permanent state changes to the bridge documents (read-only until P3).

## 5. Decision Needed

None.
