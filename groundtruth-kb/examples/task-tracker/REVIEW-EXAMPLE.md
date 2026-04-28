# Review Example — Loyal Opposition Cycle

This document shows one complete review cycle from the Task Tracker project,
demonstrating the GO/NO-GO pattern described in the
[Dual-Agent Collaboration guide](../../docs/method/06-dual-agent.md).

## Context

Prime Builder implemented SPEC-001 through SPEC-005. All 7 tests pass.
Assertions clean. Submitted for Loyal Opposition review.

## Review Submission

> 5 specs implemented, 7 tests pass, assertions clean.
> ADR-001 (in-memory store) documented with DCL-001 constraint.
> Requesting advisory review for initial implementation.

## Reviewer Finding

**P2 — SPEC-001 accepts unbounded title length**

- **Claim:** SPEC-001 says "title (required)" but the implementation accepts a
  title of any length, including 10,000+ characters.
- **Evidence:** `src/task_tracker/models.py` — `TaskCreate.title` has no
  `max_length` constraint.
- **Severity:** P2 (important — data quality issue, not a security risk)
- **Impact:** Users could accidentally or maliciously submit very long titles,
  causing display issues and storage waste.
- **Recommended action:** Add `max_length=200` to the `title` field in both
  `TaskCreate` and `TaskUpdate` models.

## Verdict: NO-GO

One P2 finding. The implementation is functional but the input validation gap
should be fixed before closure.

## Remediation

**Work item created:** WI-001 — "Add input validation for task title length"
(origin: defect, component: api, source_spec: SPEC-001)

**Fix applied:** Added `max_length=200` to `TaskCreate.title` and
`TaskUpdate.title` fields in `models.py`.

**Test added:** TEST-008 ("POST /tasks with title > 200 chars returns error")
verifies the max_length constraint. TEST-002 covers the missing-title case separately.

## Re-Review

> WI-001 resolved. Title length now capped at 200 characters via Pydantic
> Field(max_length=200). All 7 tests pass. Assertions clean.

## Verdict: GO

The finding is closed. Work item WI-001 resolved. Implementation accepted.

---

**What this demonstrates:**

1. **Structured findings** — each finding has claim, evidence, severity, impact, recommended action
2. **Work item creation** — review findings become tracked work items, not ad-hoc fixes
3. **NO-GO → fix → GO cycle** — the review loop continues until all blockers are resolved
4. **Evidence-based verdicts** — the GO is based on verification, not opinion
