NEW

# Implementation Proposal — GT-KB Workstream Focus Marker Race Fix

**Status:** NEW
**Author:** Prime Builder (goose/pb)
**Session:** S509 (2026-06-07)
**Document name:** `gtkb-workstream-focus-marker-race-fix`
**Builds on:** LO finding 2026-06-04 (Parallel Session Marker Race)

## 1. Scope

Fixes the concurrency race where multiple harnesses can clobber each other's session-stated-role markers in `.claude/session/active-session-role.json`.

## 2. Deliverables

### 2.1 Atomic Marker Write

- Implements atomic write with cross-session clobber rejection in `scripts/workstream_focus.py`.
- Validates that the writing session id matches the existing marker or that the marker is expired/absent.

## 3. Execution Plan

1. Update `scripts/workstream_focus.py` to use an atomic write lock pattern.
2. Add verification tests.

## 4. Reversibility

- Fall back to non-atomic writes.
