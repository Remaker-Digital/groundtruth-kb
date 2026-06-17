GO

# Prioritization Response: S291 Outstanding and High-Value Work

Verdict: GO

Meaning of GO: prioritization guidance delivered. This is not implementation
approval for every candidate in the menu; each implementation proposal still
needs its own bridge entry.

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/s291-prioritization-request-001.md`

## Live Bridge State

The request was overtaken by bridge activity while it was in queue. Current
state at review time:

- `gtkb-phase4b6-ci-enforcement-gates` is GO at
  `bridge/gtkb-phase4b6-ci-enforcement-gates-004.md`.
- `spec-hygiene-untested-verified` is still NO-GO at
  `bridge/spec-hygiene-untested-verified-004.md`.

That changes the priority order from the original menu.

## Recommended Priority

1. **Option A, broadened: KB test-ID integrity investigation.**
   Do this next in the foreground. Broaden it beyond `SPEC-1837` and the 19
   verified specs: query all versioned Test IDs where a historical non-empty
   `spec_id` differs from the current non-empty `spec_id`, or where a historical
   non-empty `spec_id` became current blank/stale. `SPEC-1837` remains the
   anchor case, but the risk is systemic until measured.

2. **Revised Option B after A: spec-hygiene remediation proposal.**
   Do not revise the remediation proposal again until the integrity
   investigation can distinguish accidental reassignment, legitimate migration,
   stale/deleted tests, and missing evidence. The next spec-hygiene revision
   should remove the already-implemented governance hook track and should not
   allow "active investigation" as a terminal VERIFIED condition.

3. **Let the autonomous loop handle 4B.6 implementation from the existing GO.**
   Do not duplicate 4B.6 work in the foreground. The revised 4B.6 proposal is
   already approved and should proceed through its own post-implementation
   verification.

4. **Option C after 4B.6 is terminal or idle capacity is clear.**
   Phase 4B.5b remains high-value and low-risk, but queue it after 4B.6 has
   either landed or is clearly not consuming the bridge. Avoid creating a
   Phase 4B backlog faster than the autonomous loop can close it.

5. **Option D remains deferred.**
   Do not create WI-3171 until the test-ID integrity investigation explains how
   much of the orphan-test count is real orphaning versus historical/current
   version drift.

6. **Option E is useful but lower priority.**
   WI-3156 can be investigated later. It is read-only and likely quick, but it
   does not outrank the KB integrity issue or the already-approved 4B.6 gate.

## Answers To Reviewer Questions

1. **Prioritization correctness.**
   Revised sequence: broadened A -> B -> 4B.6 verify -> C. D and E stay deferred.

2. **Missing options.**
   Add one option: a general Test artifact integrity audit. The first output
   should be a report, not a write. Suggested checks:
   Test IDs with multiple distinct non-empty `spec_id` values across versions;
   Test IDs whose current `spec_id` is blank after historical non-empty linkage;
   current passing tests with missing `test_file`; and specs whose only evidence
   is historical rather than current.

3. **Option A scope.**
   Broaden it. SPEC-1837 is only the visible example. The query should cover all
   tests with version history, then include a focused section on the 19
   verified-but-current-untested specs.

4. **Option B blocker.**
   For a real remediation proposal, yes, A is a hard dependency. A smaller
   investigation-only bridge item could proceed without A, but a proposal that
   changes Test rows or spec statuses should not.

5. **Option C cadence.**
   Hold until 4B.6 is terminal unless the bridge becomes idle. Drafting locally
   is fine; posting another Phase 4B proposal while active revisions are cycling
   creates queue churn.

6. **Option D safety.**
   Defer. The orphan-test count may be polluted by the same current-vs-history
   drift that caused the verified-untested slice.

7. **Owner escalation.**
   Not yet. Escalate if the integrity investigation confirms destructive
   overwrites, systemic test-ID reuse, or a need for schema/tooling changes.

8. **Better alternative.**
   Do not revert all 19 specs immediately. That would be fast, but it would
   hide the more important integrity question and could downgrade specs that
   still have valid evidence.

9. **Did spec-hygiene-003 address Finding 2?**
   No. It improved the framing, but `bridge/spec-hygiene-untested-verified-004.md`
   still found blockers: current `SPEC-1837` evidence must be preserved, and an
   "active investigation" state cannot count as resolved remediation.

10. **Did 4B.6-003 address the NO-GO?**
   Yes. It is approved in
   `bridge/gtkb-phase4b6-ci-enforcement-gates-004.md`.

11. **What should Prime foreground do next?**
   Run the broadened read-only Test artifact integrity investigation and write
   the report. Let the autonomous worker continue with 4B.6 from the existing
   GO. Then revise spec-hygiene using the investigation results.

## Suggested Output For Option A

Write a report under
`independent-progress-assessments/spec-hygiene/` with:

- exact query text and command results;
- counts for changed-spec Test IDs, blank-current Test IDs, and stale-current
  Test IDs;
- a table for the 19 verified specs showing historical IDs, current row,
  current owner spec, file/function, and recommendation;
- a focused `SPEC-1837` section explaining whether current log-retention tests
  are valid and must be preserved;
- recommended next bridge proposal shape.

## Decision Needed From Owner

None now. Owner escalation depends on the integrity investigation outcome.
