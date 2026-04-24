NO-GO

# GTKB-ISOLATION-015 - Loyal Opposition Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-isolation-015-phase7-full-integration-003.md`
**Thread scope:** `gtkb-isolation-015-phase7-full-integration`

## Verdict

NO-GO.

`-003` resolves the three issues called out in `-002`, but it still leaves
blocking contract gaps for a thread titled and framed as the full Phase 7
integration proposal:

1. the revised bridge transition table still over-authorizes Prime Builder to
   write `NEW` from `any` prior status
2. typed `work_subject.set` control-plane integration is now explicitly
   deferred, even though the accepted Phase 7 plan requires subject/mode/session
   control-plane operations to use the Phase 5 typed registry
3. upstream GT-KB clean-adopter delivery is also explicitly deferred, even
   though the accepted Phase 7 plan says the implementation proposal should
   include that delivery and lists it as an acceptance criterion
4. the combined-green-claim rule is still under-specified: the proposal adds
   subject labels and an action-queue warning, but it does not clearly require
   release-readiness/report logic to reject unlabeled combined application +
   GT-KB green claims

## Verification Performed

Commands run from the Agent Red workspace:

```text
python -m pytest tests/scripts/test_gtkb_dashboard_control_plane.py -q --tb=short
-> 24 passed in 0.36s

python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short
-> 13 passed in 0.70s

python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
-> 18 passed, 3 skipped in 0.38s
```

These confirm the current baseline contracts that the proposal claims it will
extend: the Phase 5 registry is still the narrow three-operation slice, overlay
absence is still a normal live-files fallback, and the work-subject hook lane
is currently green.

## Findings

### P1 - The revised bridge transition table still allows invalid Prime `NEW` transitions

**Claim**

The proposal fixes the owner of the post-implementation `GO -> NEW` step, but
it still allows Prime Builder to write `NEW` from `any` prior status.

**Evidence**

- Proposal table: `bridge/gtkb-isolation-015-phase7-full-integration-003.md:109-115`
  defines Prime Builder `NEW` with permitted source statuses `any`.
- Proposal tests: `bridge/gtkb-isolation-015-phase7-full-integration-003.md:143-153`
  cover correct Prime ownership of post-implementation `NEW`, but they do not
  require rejection of invalid `NO-GO -> NEW` or `VERIFIED -> NEW` transitions.
- Bridge protocol: `.claude/rules/file-bridge-protocol.md:45-49` reserves
  `REVISED` for the post-`NO-GO` path, and
  `.claude/rules/file-bridge-protocol.md:90-93` defines `NEW` after a prior
  thread only for the post-implementation report after `GO`.
- The proposal itself says `VERIFIED -> *` must always be rejected:
  `bridge/gtkb-isolation-015-phase7-full-integration-003.md:117-123`.

**Risk / impact**

If implemented as written, the bridge writer could accept invalid transitions
such as `NO-GO -> NEW` or `VERIFIED -> NEW`, which would break the audit trail
and blur the distinction between revision, verification, and a new post-impl
report.

**Recommended action**

Revise the transition table and tests so Prime Builder `NEW` is accepted only:

- when no prior version exists for the document, or
- when the latest status is `GO` and Prime is filing the post-implementation report

Add explicit rejection tests for Prime `NEW` after `NO-GO`, `REVISED`, and
`VERIFIED`.

**Decision needed from owner**

None.

### P1 - Deferring typed `work_subject.set` leaves an explicit Phase 7 acceptance criterion unmet

**Claim**

The revision correctly rejects the ad hoc `record_operation()` side path, but it
then scopes typed `work_subject.set` control-plane integration out of this
bridge entirely. That is inconsistent with the accepted Phase 7 contract for a
proposal presented as the full integration thread.

**Evidence**

- Proposal defers typed control-plane work:
  `bridge/gtkb-isolation-015-phase7-full-integration-003.md:202-232`,
  `:282`, `:300`, `:317-318`, and `:325-326`.
- Phase 7 plan requires control-plane integration for subject changes:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:276-285`,
  `:356-360`, and `:398`.
- Phase 5 plan defines `work_subject.set` as a typed registry operation and
  requires mode/subject changes to apply through typed handlers with dry-run,
  audit, rollback, and counterpart-visibility semantics:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-005-PHASE5-DASHBOARD-CONTROL-PLANE-PLAN-2026-04-23.md:143`,
  `:255-263`.
- Live registry baseline remains only the Phase 5 first slice:
  `scripts/gtkb_dashboard/control_plane_registry.py:4-8`,
  `:152-180`;
  `python -m pytest tests/scripts/test_gtkb_dashboard_control_plane.py -q --tb=short`
  passed `24` tests against that current three-operation contract.

**Risk / impact**

Approving this proposal as the full Phase 7 integration plan would bless a
scope that still leaves subject/mode/session mutations outside the required
typed control-plane path. That would make the accepted Phase 7 acceptance
criteria unattainable on this thread.

**Recommended action**

Either:

- include the typed `work_subject.set` handler, registry expansion, and tests in
  this bridge, or
- explicitly re-scope and rename the bridge as a narrower partial Phase 7 slice
  instead of the full integration thread

**Decision needed from owner**

None.

### P1 - Deferring upstream GT-KB delivery leaves the clean-adopter requirement unmet

**Claim**

The revision still files upstream GT-KB delivery as a later bridge, which is
not aligned with the accepted Phase 7 requirement that the implementation
proposal include clean-adopter delivery.

**Evidence**

- Proposal defers upstream delivery:
  `bridge/gtkb-isolation-015-phase7-full-integration-003.md:259-262`,
  `:317-319`, and `:329`.
- Phase 7 plan says the eventual implementation proposal should include upstream
  GT-KB product work so clean adopters receive the behavior by default:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:329-344`.
- The same plan lists upstream GT-KB packaging as an acceptance criterion:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:401`.

**Risk / impact**

An Agent Red-only implementation would leave clean adopters without the Phase 7
behavior by default, which directly contradicts the portability requirement and
would produce a dogfood-only outcome instead of a GT-KB-delivered capability.

**Recommended action**

Either:

- include the upstream GT-KB template/scaffold/init/upgrade/doctor/test scope in
  this bridge, or
- re-scope the bridge so it no longer claims to be the full Phase 7 integration

**Decision needed from owner**

None.

### P2 - The combined-green-claim rule is still under-specified at the readiness/report layer

**Claim**

The revised proposal adds subject labels and an action-queue guard, but it does
not clearly require the release-readiness/report logic itself to reject
unlabeled combined application + GT-KB green claims.

**Evidence**

- Proposal identifies the current problem:
  `bridge/gtkb-isolation-015-phase7-full-integration-003.md:64-68`.
- Proposal changes only guarantee subject labels and say to
  `Block (warn)` the startup model action queue:
  `bridge/gtkb-isolation-015-phase7-full-integration-003.md:80-89`.
- Proposal verification matrix checks labels, but not readiness/report
  rejection of combined green claims:
  `bridge/gtkb-isolation-015-phase7-full-integration-003.md:286-300`.
- Phase 7 plan requires combined green claims to be disallowed unless both
  subjects were intentionally in scope and separately verified:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:245-251`.

**Risk / impact**

If only labels and action-queue warnings are added, the readiness/report layer
may still emit unlabeled or weakly-labeled combined green claims, leaving one of
the Phase 7 scoping guarantees unenforced.

**Recommended action**

Specify the release-readiness/report behavior explicitly: reject or hard-fail
unlabeled combined application + GT-KB green claims, and add regression tests
for that rule.

**Decision needed from owner**

None.

## Required Action Items

1. Tighten the bridge transition model so Prime `NEW` is legal only for a brand-new
   document or a post-`GO` implementation report, and add explicit invalid-transition
   tests.
2. Include typed `work_subject.set` registry integration in this bridge, or
   re-scope/rename the thread so it is no longer presented as the full Phase 7
   integration proposal.
3. Include upstream GT-KB clean-adopter delivery in this bridge, or re-scope/rename
   the thread so it is no longer presented as the full Phase 7 integration proposal.
4. Specify and test release-readiness/report rejection of unlabeled combined green
   claims.

## Decision Needed From Owner

None.
