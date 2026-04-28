---
name: BACKLOG-018 Active Implementation Plan
description: Owner-approved 6-phase feature plan (55 specified specs). DEFAULT work priority — return to this after any redirected work unless owner says otherwise. Completion = implemented + tested + staging deploy.
type: project
---

BACKLOG-018 is the active implementation plan, approved by owner on 2026-03-17 (S202). Tracked in KB as DOC-177 + BACKLOG-018 snapshot.

**Directive:** This plan is the DEFAULT work priority. If redirected to other work or investigation, RETURN to this plan when that work completes, unless the owner directs otherwise. The plan is active until all phases are complete, fully tested, debugged, and deployed to staging.

**Why:** 55 specified specs remain unimplemented. The critical path runs through Conversation Quality (Phase 1) which unblocks A/B Testing (Phase 2) which unblocks beta feedback (Release Plan Step 4). The Integration Framework (Phase 3) is the largest initiative and is an Enterprise-tier differentiator.

**How to apply:** At session start, check progress against the phase list below. Pick up where the last session left off. If the owner requests unrelated work, complete it then announce "Returning to BACKLOG-018 Phase N" and resume.

## Phase Tracker

| Phase | Area | Specs | Est. Sessions | Status |
|-------|------|-------|---------------|--------|
| 1 | Conversation Quality | SPEC-0180, 0183, 0185-0188 | 3-4 | **COMPLETE** (S202: all 6 implemented, 83 tests pass) |
| 2 | A/B Testing | SPEC-0621, 0623-0626 | 3-4 | **COMPLETE** (S202: all 5 implemented, 36 tests pass, 12 WIs resolved) |
| 3 | Integration Framework | SPEC-1761-1778 | 6-8 | **COMPLETE** (S205: all 18/18 implemented — 402 tests) |
| 4 | MCP Agents | SPEC-1706-1712 | 4-5 | **COMPLETE** (S205: all 7/7 implemented — 100 tests) |
| 5 | Pipeline Observatory | SPEC-1579-1587, 1786 | 3-4 | **COMPLETE** (S206: all 10/10 implemented — 51 tests, 10 WIs resolved) |
| 6 | Deferred Features | SPEC-0113, 0151, 0195, 0245, 0297, 0617, 0761, 0823, 1705 | as-needed | **COMPLETE** (S206: all 9/9 implemented — 27 tests, 9 WIs resolved) |

## Phase 3 Start Sequence
1. Read SPEC-1761 (Integration Framework) from KB
2. Create work items for implementation gaps
3. Create tests per GOV-12
4. Implement integration framework core
5. Proceed through SPEC-1762-1778

## Completion Criteria
All 55 specs promoted to implemented, all tests passing, deployed to staging, owner verification.
