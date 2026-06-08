NEW

# Implementation Proposal — GT-KB Bridge Advisory Message Type

**Status:** NEW
**Author:** Prime Builder (goose/pb)
**Session:** S509 (2026-06-07)
**Document name:** `gtkb-bridge-advisory-message-type-implementation`
**Builds on:** `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md`

## 1. Scope

Extends the bridge protocol with a first-class `ADVISORY` message type for Loyal Opposition reports that do not carry a GO/NO-GO verdict.

## 2. Deliverables

### 2.1 Protocol Extension

- Updates `.claude/rules/file-bridge-protocol.md` with `ADVISORY` semantics.
- Updates `groundtruth_kb.bridge.detector.BridgeStatus` with `ADVISORY` member.

### 2.2 Scanner & UI Support

- Updates `scan_bridge.py` and Dashboard generators to recognize and display `ADVISORY` entries.
- Updates kind-aware routing to treat `ADVISORY` as terminal for both agents.

## 3. Execution Plan

1. Update governance docs.
2. Update `groundtruth_kb.bridge` modules.
3. Regerate dashboard templates.

## 4. Reversibility

- Revert status enum and doc changes.
