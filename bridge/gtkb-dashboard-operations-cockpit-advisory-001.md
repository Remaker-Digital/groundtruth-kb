ADVISORY

bridge_kind: loyal_opposition_advisory
Document: gtkb-dashboard-operations-cockpit-advisory
Version: 001
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-11 UTC
Source Work Item: WI-3433
Source Advisory: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-28-14-52-GTKB-DASHBOARD-OPERATIONS-COCKPIT-ADVISORY.md
Recommended commit type: docs:

# GT-KB Dashboard Operations Cockpit Advisory Handoff

## Claim

WI-3433 is ready for Prime Builder disposition under the LO advisory routing
workflow. The source advisory is not implementation approval; it is a P1
Loyal Opposition product/governance assessment recommending that Prime Builder
turn the GT-KB dashboard into a trustworthy operations cockpit.

Recommended disposition: `adapt`.

Prime should accept the advisory's core pattern - dashboard reliability,
scope clarity, workflow-first triage, and explicit bridge authority boundaries -
but adapt it into a smaller GT-KB-native implementation slice that starts with
metric correctness and scope clarity before broad visual redesign.

## Source Summary

The source advisory found that the current dashboard has useful data foundations
but mixes platform/adopter scope, contains hardcoded metric statuses that can
contradict displayed values, presents health counts before actionable workflow,
uses ambiguous bridge/contention counts, exposes unreliable local-path links,
and needs clearer refresh-control behavior and setup-mode separation.

The advisory's suggested bridge/work-item title was:

`GTKB-DASHBOARD Operations Cockpit Reliability and Scope-Clarity Slice`

## Recommended Prime Builder Response

Prime Builder should classify the advisory as `adapt` and file a normal `NEW`
implementation proposal for a first slice with this approximate scope:

1. Replace hardcoded `current_metrics` status strings with per-metric status
   functions and tests.
2. Add or expose dashboard subject/scope metadata so GT-KB platform state and
   active adopter/application state are not conflated.
3. Split bridge dashboard counts into exact queue semantics or explicitly label
   non-authoritative pressure counts.
4. Move the top-action workflow signal into the first viewport, with owner lane
   and evidence age.
5. Remove misleading local-path `Open` affordances or convert them into an
   explicit local workflow pattern.
6. Preserve broader visualization redesign, refresh-service hardening, and
   setup-mode cleanup as follow-on work unless Prime can keep the first slice
   small and testable.

## Why `adapt` Instead Of `adopt`

The source advisory contains a broad dashboard product direction and ten
ordered implementation steps. Adopting all of it as one proposal would risk a
large, UI-heavy change that mixes data correctness, scope modeling, Grafana
layout, local file controls, service behavior, and documentation cleanup.

An adapted first slice is lower risk: it lands the correctness and authority
semantics first, then lets later proposals redesign panels or workflow controls
against a trustworthy data layer.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes. The recommended `adapt` disposition implies future edits to dashboard
refresh/generation code, generated dashboard artifacts, docs, and tests.

### Grill-the-owner questions

Prime Builder must obtain durable AUQ-recorded answers to:

1. Should the default dashboard subject be GT-KB platform only, active
   adopter/application only, or combined operations with explicit badges?
2. Should local workspace file controls be copyable paths, read-only previews,
   or approved local-open actions?
3. Is the refresh service strictly loopback/local-only, or must the first slice
   harden it for exposed/shared use?
4. Should package-facing `gt dashboard` commands be the primary visible setup
   path even when running from the GT-KB source checkout?

### Required durable owner decisions

Before filing an implementation proposal, Prime Builder must preserve the
answers above in AskUserQuestion/AUQ evidence and carry them into the proposal's
mandatory `## Owner Decisions / Input` section.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this is a first-class ADVISORY bridge entry.
- `SPEC-ADVISORY-REPORT-TEMPLATE-001` - advisory reports are preserved as
  durable workflow inputs.
- `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` - dashboard bridge/advisory counters
  must distinguish ADVISORY from failed proposals and exact action queues.
- `DCL-ADVISORY-ROUTING-001` - ADVISORY routes to Prime disposition, not LO
  GO/NO-GO/VERIFIED review.
- `GOV-STANDING-BACKLOG-001` - WI-3433 is a governed backlog-routing item;
  capture is not implementation approval.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the follow-on
  Prime implementation proposal must carry concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the follow-on
  implementation report must carry spec-to-test mapping and executed evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this advisory preserves a candidate
  lifecycle trigger and defers implementation until Prime disposition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserve the decision path as a
  durable artifact instead of chat-only context.
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` - adopt/adapt advisory
  classifications require a Prime owner-grilling gate before implementation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - follow-on dashboard work must
  stay within `E:\GT-KB`.

## Prior Deliberations And Evidence

- `WI-3433` - open high-priority advisory-routing work item in
  `PROJECT-GTKB-LO-ADVISORY-ROUTING`.
- `PROJECT-GTKB-LO-ADVISORY-ROUTING` - owner-directed project for routing LO
  advisories through the five-state disposition workflow.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-28-14-52-GTKB-DASHBOARD-OPERATIONS-COCKPIT-ADVISORY.md`
  - source P1 advisory.
- `.claude/rules/peer-solution-advisory-loop.md` - disposition vocabulary and
  Prime response workflow.
- `bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-001.md` -
  precedent for an `adapt` disposition that files a separate implementation
  proposal instead of treating the disposition itself as implementation.

## Same-Session Guard

This ADVISORY is created by the current Loyal Opposition session. This session
must not later review or verify any proposal/report derived from this same
artifact. A later Prime Builder session should acknowledge and classify it; a
different Loyal Opposition session should review any resulting proposal or
implementation report.

## Specification-Derived Verification

This ADVISORY performs no source implementation and no MemBase mutation. Its
verification target is therefore the routing artifact shape, not dashboard
runtime behavior.

| Linked specification or rule | Verification evidence |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` has `Document: gtkb-dashboard-operations-cockpit-advisory` with latest `ADVISORY`; `show_thread_bridge.py` reports no drift. |
| `SPEC-ADVISORY-REPORT-TEMPLATE-001` and `DCL-ADVISORY-ROUTING-001` | First line is `ADVISORY`; `bridge_kind: loyal_opposition_advisory`; expected Prime response is acknowledgement/disposition, not GO/NO-GO/VERIFIED review. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The handoff lists concrete governing specifications and instructs Prime to carry concrete links into the follow-on implementation proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | No implementation report exists in this ADVISORY; follow-on verification is explicitly assigned to the future Prime implementation report. This no-source routing artifact is checked with bridge parser/preflight commands rather than `python -m pytest`. |
| `GOV-STANDING-BACKLOG-001` | `.gtkb-state/advisory-dispositions/WI-3433.md` records the single-WI routing inventory; no bulk backlog mutation is performed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All referenced live artifacts are under `E:\GT-KB`. |

Executed validation commands for this routing artifact:

```powershell
python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-dashboard-operations-cockpit-advisory --format json --preview-lines 80
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-dashboard-operations-cockpit-advisory --content-file bridge\gtkb-dashboard-operations-cockpit-advisory-001.md
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-dashboard-operations-cockpit-advisory --content-file bridge\gtkb-dashboard-operations-cockpit-advisory-001.md
python .claude\hooks\bridge-compliance-gate.py --audit-only --file bridge\gtkb-dashboard-operations-cockpit-advisory-001.md
```

## Expected Next Artifact

Prime Builder should file one of:

- a normal `NEW` implementation proposal converting this advisory into an
  adapted dashboard reliability/scope-clarity slice, or
- a documented `reject`, `defer`, or `monitor` disposition with rationale if
  Prime decides not to implement it now.

No owner decision is required merely to preserve this ADVISORY. Owner decisions
are required before the recommended `adapt` implementation proposal.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
