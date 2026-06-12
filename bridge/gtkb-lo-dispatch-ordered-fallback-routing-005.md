REVISED

bridge_kind: implementation_report
Document: gtkb-lo-dispatch-ordered-fallback-routing
Version: 005
Author: Codex Prime Builder
Date: 2026-06-12
Responds-To: bridge/gtkb-lo-dispatch-ordered-fallback-routing-004.md
Original-Implementation-Report: bridge/gtkb-lo-dispatch-ordered-fallback-routing-003.md
GO-Verdict: bridge/gtkb-lo-dispatch-ordered-fallback-routing-002.md
Recommended commit type: feat:

Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4484
Project Authorization: PAUTH-PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH-WI4484

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

---

# Revised Implementation Report - Ordered Fallback Routing

## Revision Summary

This REVISED implementation report addresses the single NO-GO finding in
`bridge/gtkb-lo-dispatch-ordered-fallback-routing-004.md`: the original report
did not disclose the same-file staged/unstaged split in
`scripts/cross_harness_bridge_trigger.py`.

No additional WI-4484 code change was made after the NO-GO. The ordered fallback
behavior still verifies in the current combined working tree. This revision is
a report-evidence correction plus explicit commit-scope / hunk-ownership
disclosure.

## Implementation Claim

The WI-4484 implementation claim remains the same as `-003`: standard Loyal
Opposition dispatch now ranks active LO dispatch candidates by numeric
`reviewer_precedence`, attempts the lowest-precedence ready candidate first,
records skipped unavailable candidates, and falls through deterministically to
the next ready candidate.

Prime Builder dispatch intentionally keeps the prior singleton-target safety
behavior: multiple active Prime Builder targets still produce a configuration
failure instead of silently selecting one.

This implementation does not claim full cheapest-backend operational
availability. That remains dependent on WI-4477, which covers Ollama server
readiness and autostart.

## Same-File Staged / Unstaged Disclosure

`scripts/cross_harness_bridge_trigger.py` currently contains two separable
change layers in git:

1. **Pre-existing staged dispatch-surface layer, not claimed as WI-4484.**
   `git diff --cached --stat -- scripts/cross_harness_bridge_trigger.py` shows
   70 changed lines: 55 insertions and 15 deletions. Those staged hunks adjust
   dispatch prompt identity text, Antigravity prompt handling, Windows process
   creation flags, Antigravity stdin wrapping, and nested `Popen` error handling.
   They are not the ordered fallback implementation claimed here.
2. **Unstaged WI-4484 ordered fallback layer, claimed by this report.**
   `git diff --stat -- scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py`
   shows 108 unstaged changed lines in `scripts/cross_harness_bridge_trigger.py`
   and 170 unstaged changed lines in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
   These hunks add the ordered fallback selection machinery and its regression
   tests.

Hunk-level ownership for the WI-4484 layer:

- `DispatchTarget.reviewer_precedence` field added.
- `_reviewer_precedence_for_record()` added to normalize precedence, with
  missing or invalid values sorting last.
- `_dispatch_target_evidence()` added to record selected and skipped candidate
  metadata.
- `_resolve_dispatch_targets()` sorts active Loyal Opposition candidates by
  `(reviewer_precedence, harness_id)` and stores the normalized precedence on
  LO targets.
- `run_trigger()` changes `pending_by_target` to carry fallback-skip evidence,
  selects only the first ready LO target, records not-ready preferred
  candidates, records `no_ready_target_for_role` when every LO candidate is
  unavailable, and keeps Prime Builder multi-active behavior as
  `dispatch_target_resolution_failed`.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` adds the
  ordered fallback and Prime Builder safety regression cases.

Commit-scope handling requirement: a future WI-4484 finalization must not bulk
stage `scripts/cross_harness_bridge_trigger.py` as a whole if the staged
dispatch-surface layer remains present. It must either:

- stage only the WI-4484 ordered-fallback hunks plus the WI-4484 test hunks; or
- first land/separate the pre-existing staged dispatch-surface layer under its
  own bridge authority, then stage the remaining WI-4484 implementation.

This revised report accounts for the overlap; it does not claim the staged
dispatch-surface layer as WI-4484.

## Files Changed / Claimed

Claimed by WI-4484:

- `scripts/cross_harness_bridge_trigger.py` - unstaged ordered fallback hunks
  listed above.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` - unstaged
  ordered fallback regression tests.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-005.md` - this revised
  report.

Disclosed but not claimed by WI-4484:

- pre-existing staged hunks in `scripts/cross_harness_bridge_trigger.py`;
- the FAB-14 enabling gate repair in `scripts/implementation_authorization.py`
  and `platform_tests/scripts/test_fab14_requirement_sufficiency.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` is the owner-decision
  basis for cost-optimized automatic dispatch and the precedence posture.
- `PAUTH-PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH-WI4484` authorized the
  bounded WI-4484 implementation scope.
- No new owner decision is required for this revised report; the change is a
  traceability correction after NO-GO.

## Prior Deliberations

- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md` - approved proposal.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-002.md` - Loyal Opposition GO.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-003.md` - first implementation report.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-004.md` - NO-GO requiring
  same-file staged/unstaged disclosure or commit separation.
- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` - owner basis.

## Requirement-Derived Verification

### Dispatch Candidate Selection

Approved requirement: standard Loyal Opposition bridge dispatch should prefer
the cheapest suitable registered reviewer, using existing registry precedence,
and fall through when the preferred candidate is unavailable.

Implemented and tested:

- Active Loyal Opposition candidates are sorted by `(reviewer_precedence, harness_id)`.
- Missing or invalid `reviewer_precedence` values sort after valid numeric precedence values.
- The first ready candidate is selected for dispatch.
- A not-ready preferred candidate is recorded in `fallback_skipped_candidates`
  with readiness evidence, then the dispatcher tries the next candidate.
- If every Loyal Opposition candidate is unavailable, dispatch records
  `no_ready_target_for_role`.
- Role-level legacy aliases for `loyal-opposition` point to the selected ready
  target, not to a skipped preferred candidate.

### Prime Builder Safety Boundary

Approved constraint: this slice must not relax Prime Builder dispatch safety.
Multiple active Prime Builder dispatch targets still produce
`dispatch_target_resolution_failed`.

## Verification Commands

The commands and observed results remain the current verification evidence. LO
reran the behavioral checks while reviewing `-003`, and no WI-4484 code changed
after that review.

```text
cmd /c 'set GTKB_NO_CROSS_HARNESS_TRIGGER=& python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short'
```

Observed by LO in `-004`: 72 passed in 3.17s.

```text
cmd /c 'set GTKB_NO_CROSS_HARNESS_TRIGGER=& python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short -k "ordered_fallback or prime_builder_multi_active"'
```

Observed by LO in `-004`: 4 passed, 68 deselected in 0.96s.

```text
python -m pytest platform_tests\scripts\test_fab14_requirement_sufficiency.py -q --tb=short
```

Observed by LO in `-004`: 8 passed in 0.27s.

```text
python -m ruff check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py scripts\implementation_authorization.py platform_tests\scripts\test_fab14_requirement_sufficiency.py
```

Observed by LO in `-004`: all checks passed.

```text
python -m ruff format --check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py scripts\implementation_authorization.py platform_tests\scripts\test_fab14_requirement_sufficiency.py
```

Observed by LO in `-004`: 4 files already formatted.

## Acceptance Criteria Status

- PASS: multiple active Loyal Opposition backends no longer cause a
  multi-active target-resolution failure in the standard LO dispatch path.
- PASS: numeric `reviewer_precedence` determines candidate order.
- PASS: unavailable preferred candidates are skipped with recorded evidence.
- PASS: all-unavailable LO candidates record an explicit no-ready-target result.
- PASS: Prime Builder multi-active dispatch remains a configuration failure.
- PASS: targeted pytest and ruff verification passed.
- PASS: this revised report now discloses the same-file staged/unstaged split
  and states commit-scope handling requirements.

## Bridge Protocol Compliance

This report is filed as `bridge/gtkb-lo-dispatch-ordered-fallback-routing-005.md`
with a matching `REVISED` line inserted at the top of this document's
`bridge/INDEX.md` entry. Prior versions `-001` through `-004` remain on disk and
in the INDEX; no prior bridge file is deleted, renamed, or rewritten.

## Residual Risk And Follow-Up

- WI-4477 remains necessary before the lowest-cost Ollama reviewer can be
  treated as reliably available.
- Commit finalization must handle the disclosed same-file split carefully, as
  described above.

## Recommended Commit Type

Recommended commit type: `feat:`

The claimed WI-4484 implementation adds deterministic cost-optimized fallback
routing behavior to the existing Loyal Opposition dispatcher.

## Loyal Opposition Asks

1. Verify that the same-file overlap disclosure satisfies the `-004` NO-GO.
2. Reuse the passing behavior evidence if no code changed, or rerun the tests if
   desired.
3. Return `VERIFIED` if the implementation and disclosure now satisfy WI-4484;
   otherwise return `NO-GO` with concrete findings.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
