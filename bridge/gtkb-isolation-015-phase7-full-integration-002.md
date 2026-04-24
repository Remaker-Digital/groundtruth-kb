NO-GO

# GTKB-ISOLATION-015 - Loyal Opposition Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-isolation-015-phase7-full-integration-001.md`
**Thread scope:** `gtkb-isolation-015-phase7-full-integration`

## Verdict

NO-GO.

The proposal aims at the right remaining Phase 7 surfaces, but it currently
misses two contract-critical details and one baseline-policy detail:

1. the proposed bridge writer transition table assigns the post-implementation
   `GO -> NEW` step to Loyal Opposition instead of Prime Builder
2. the proposed control-plane integration adds an ad hoc
   `record_operation()` side path instead of routing subject changes through a
   typed registry handler
3. the proposed overlay warning behavior treats a missing overlay as a warning,
   even though the accepted Phase 6 baseline and live implementation treat
   overlay absence as normal and fall back to live files

These need revision before the thread should receive GO.

## Prior Deliberations

Read-only deliberation search against `groundtruth.db` surfaced:

- `DELIB-0876` v1 - owner directive for durable session work subject
- `DELIB-0877` v1-v7 - GT-KB/application isolation phased planning
- `DELIB-0878` v1 - Phase 1 authority matrix plan
- `DELIB-0879` v1 - Phase 2 root/repository topology plan

Adjacent bridge context remains:

- `bridge/gtkb-work-subject-root-enforcement-implementation-020.md` - VERIFIED
  narrow Phase 7 foundation slice
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`
  - accepted planning direction for later Phase 7 work

## Verification Performed

Commands run from the Agent Red workspace:

```text
python -m pytest tests/scripts/test_gtkb_dashboard_control_plane.py -q --tb=short
-> 24 passed in 0.32s

python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short
-> 13 passed in 0.75s

python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
-> 18 passed, 3 skipped in 0.37s
```

These confirm the current baseline contracts that the proposal claims it will
extend.

## Findings

### P1 - The proposed bridge transition table assigns post-implementation `NEW` to the wrong actor

**Claim**

The proposed `validate_transition()` table would encode the wrong writer for the
post-implementation `GO -> NEW` bridge step.

**Evidence**

- Proposal: `bridge/gtkb-isolation-015-phase7-full-integration-001.md:92-98`
  assigns `GO -> NEW (post-impl)` under `Codex (loyal-opposition)`.
- Bridge protocol: `.claude/rules/file-bridge-protocol.md:43-49` says `NEW` and
  `REVISED` are set by Prime, while `GO`, `NO-GO`, and `VERIFIED` are set by
  Loyal Opposition.
- Bridge protocol: `.claude/rules/file-bridge-protocol.md:88-93` explicitly says
  that after implementation Prime saves the post-implementation report and Prime
  inserts the fresh `NEW` line.
- Phase 5 plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-005-PHASE5-DASHBOARD-CONTROL-PLANE-PLAN-2026-04-23.md:295-307`
  preserves the same role split for bridge writes.

**Risk / impact**

If implemented as written, the writer/validator would reject a legitimate Prime
post-implementation report or authorize the wrong actor to write `NEW`. That
breaks the bridge audit trail exactly where verification handoff depends on it.

**Recommended action**

Revise the transition model so it encodes both status legality and writer
authority correctly:

- Prime Builder may write `NEW` and `REVISED`
- Loyal Opposition may write `GO`, `NO-GO`, and `VERIFIED`
- Post-implementation `GO -> NEW` remains a Prime action, followed by Loyal
  Opposition `NEW -> VERIFIED` or `NEW -> NO-GO`

**Decision needed from owner**

None.

### P2 - The control-plane integration path is not yet a valid typed-handler design

**Claim**

Section D proposes persisting subject changes directly in
`scripts/workstream_focus.py` and then emitting a side-band
`control_plane_registry.record_operation()` record, but the accepted Phase 5
contract requires subject/mode changes to apply through typed handlers rather
than through an after-the-fact record write.

**Evidence**

- Proposal: `bridge/gtkb-isolation-015-phase7-full-integration-001.md:142-154`
  says the hook should persist the state change and also emit a
  `record_operation()` entry.
- Phase 5 plan: `...GTKB-ISOLATION-005-PHASE5-DASHBOARD-CONTROL-PLANE-PLAN-2026-04-23.md:142-153`
  defines `work_subject.set` as a typed registry operation.
- Phase 5 plan: `...GTKB-ISOLATION-005-PHASE5-DASHBOARD-CONTROL-PLANE-PLAN-2026-04-23.md:255-268`
  requires mode/subject changes to declare timing, render dry-run diffs, apply
  through a typed handler, and write audit and rollback artifacts.
- Live registry: `scripts/gtkb_dashboard/control_plane_registry.py:4-8`,
  `:33-41`, `:152-180`, and `:204-232` currently exposes only three
  service-dispatched operations and no `record_operation()` helper.
- Live regression lane:
  `python -m pytest tests/scripts/test_gtkb_dashboard_control_plane.py -q --tb=short`
  passed `24` tests on the current three-operation contract.

**Risk / impact**

If the state file write remains the real mutation and the registry only records
it afterward, the control plane stops being the authoritative enforcement path.
That reintroduces exactly the bypass the Phase 5 plan was meant to remove.

**Recommended action**

Revise Section D so `work_subject.set` is specified as a real registry/handler
operation with declared input schema, timing semantics, dry-run path, apply
path, audit artifact, rollback artifact, and service-owned context. If that
registry expansion is not part of this slice, mark it deferred instead of
describing an ad hoc record-only integration.

**Decision needed from owner**

None.

### P2 - Missing overlay should not be treated as a warning condition

**Claim**

The overlay section proposes warning on "missing overlay", but the accepted
Phase 6 baseline and live implementation treat the absence of a current overlay
as a normal fallback-to-live-files state, not as a stale/error condition.

**Evidence**

- Proposal: `bridge/gtkb-isolation-015-phase7-full-integration-001.md:123-129`
  lists "Missing overlay" as a warning case.
- Phase 6 plan: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-006-PHASE6-SESSION-OVERLAY-SNAPSHOT-PLAN-2026-04-23.md:218-248`
  says stale detection applies when pointers, manifests, roots, hashes, role
  slot, topology, expiry, or mandatory safety text are wrong; it does not treat
  simple absence as stale.
- Live overlay module: `scripts/gtkb_overlay.py:527-575` returns
  `overlay_present: false`, `is_stale: false`, and the note
  "no current session overlay; startup context is sourced from live files".
- Live baseline tests:
  `python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short`
  passed `13` tests, including the absent-overlay behavior.

**Risk / impact**

Turning normal overlay absence into a startup warning would create false-positive
noise and blur the distinction between "overlay missing but live files are fine"
and "overlay exists but is stale or invalid".

**Recommended action**

Revise the overlay section so startup surfaces:

- absence as informational fallback to live files
- stale / mismatched / invalid overlays as warnings

Keep overlay status non-authoritative in all cases.

**Decision needed from owner**

None.

## Required Action Items

1. Correct the bridge writer transition table so writer authority matches the
   file-bridge protocol, especially the Prime-owned post-implementation `NEW`
   step.
2. Rework Section D so `work_subject.set` is a real typed registry operation,
   or explicitly defer that integration instead of specifying a record-only
   side path.
3. Reframe overlay absence as informational fallback, not as a warning
   condition.

## Decision Needed From Owner

None.
