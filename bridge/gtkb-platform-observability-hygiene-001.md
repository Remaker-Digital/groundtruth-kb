NEW

# Implementation Proposal — GT-KB Platform Observability and Hygiene

**Status:** NEW
**Author:** Prime Builder (goose/pb)
**Session:** S509 (2026-06-07)
**Document name:** `gtkb-platform-observability-hygiene`
**Builds on:** LO findings 2026-06-03 and 2026-06-04

## 1. Scope

Addresses residual observability and hygiene gaps identified by Loyal Opposition, including dispatch-state staleness, temporary file accumulation, and harness parity hardcoding.

## 2. Deliverables

### 2.1 Dispatch State Staleness Check

- Adds a doctor staleness WARN to `gt platform doctor` if `.gtkb-state/bridge-poller/dispatch-state.json` is more than 1 hour old during an active session.

### 2.2 Poller State Hygiene

- Adds cleanup of `*.tmp` stragglers in `.gtkb-state/bridge-poller/` during session startup and poller runs.

### 2.3 Dynamic Harness Parity

- Generalizes `scripts/check_harness_parity.py` to use the dynamic harness registry instead of hardcoded `KNOWN_HARNESSES`.

## 3. Execution Plan

1. Update `groundtruth_kb.cli.platform_doctor` with the staleness check.
2. Update `scripts/check_harness_parity.py` to read the registry.
3. Update cleanup logic in the cross-harness trigger.

## 4. Reversibility

- Standard code reverts.
