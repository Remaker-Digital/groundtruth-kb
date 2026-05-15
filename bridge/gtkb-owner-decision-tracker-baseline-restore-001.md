NEW

# Implementation Proposal - Owner-Decision-Tracker Baseline Restoration (WI-3277)

bridge_kind: implementation_proposal
Document: gtkb-owner-decision-tracker-baseline-restore
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3277

target_paths: [".claude/hooks/owner-decision-tracker.py", "platform_tests/hooks/test_owner_decision_tracker.py", "tests/hooks/test_owner_decision_tracker.py"]

This NEW proposal investigates and repairs the 21 pre-existing failures in `platform_tests/hooks/test_owner_decision_tracker.py` that are currently baseline-accounted (per bridge `gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md`).

## Claim

21 tests fail today on a clean checkout. They were baselined (accepted-as-known) rather than fixed during axis-2 surface landing. This proposal triages each failure into one of: (a) genuine test bug — fix the test; (b) genuine hook regression — fix the hook; (c) test-of-deprecated-behavior — retire the test with rationale.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` - tracker is part of policy engine.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - tracker uses deterministic patterns.
- `GOV-18` - assertion quality; baselined tests violate this when permanent.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3277 tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-APPROVAL-PACKET-ERGONOMICS authorization including WI-3277.

## Requirement Sufficiency

Existing requirements sufficient. WI-3277 description identifies the 21 baseline failures as the operative defect scope.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 (triage doc) + IP-2..IP-4 per-class fixes + IP-5 baseline-marker removal + IP-6 tests single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Triage matrix

Run `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py -v --tb=short` against clean checkout. Record each failure: test name, failure mode, classification (test-bug | hook-regression | deprecated-behavior). Emit as a markdown table in this thread's post-implementation report.

### IP-2: Fix test-bug class

For each test classified as test-bug (incorrect assertion, stale fixture, etc.), update the test.

### IP-3: Fix hook-regression class

For each test classified as hook-regression (real defect in `owner-decision-tracker.py`), patch the hook to restore correct behavior.

### IP-4: Retire deprecated-behavior class

For each test classified as deprecated-behavior (tests something the policy explicitly changed), mark `@pytest.mark.skip(reason="<rationale>")` with citation to the superseding spec.

### IP-5: Remove baseline marker

Remove the "21 pre-existing failures baselined" note from bridge thread + any in-test `xfail` markers.

### IP-6: Spec promotion check

No spec promotion in this WI (no source spec being promoted; this is defect-cluster fix).

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Triage matrix exists in post-impl report | manual verification — referenced by report URL |
| Test suite passes (all 21 + others) | `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py` exit 0 |
| Each fix preserves intent (sample 5 cases) | post-impl spot checks documented |
| No regression in non-baseline tests | full suite still passes |

Run: `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py tests/hooks/test_owner_decision_tracker.py -v`.

## Acceptance Criteria

- IP-1 triage matrix in post-impl report.
- IP-2..IP-4 individual fixes landed.
- IP-5 baseline markers removed.
- Full suite passes.
- Both preflights PASS.

## Risks / Rollback

- Risk: some failures may surface real spec ambiguity that requires owner input mid-triage. Mitigation: surface via AUQ if encountered; defer affected tests with explicit deferral marker.
- Rollback: revert per-test or per-hook changes; restore baseline markers if needed.

## Recommended Commit Type

`fix` - defect-cluster repair. Net LOC unknown (depends on triage); estimated 50-150.
