NEW
author_identity: prime-builder
author_harness_id: A
author_session_context_id: codex-pb-20260612-dashboard-advisory-disposition
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop, Prime Builder bridge/backlog continuation
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

# Prime Disposition - Dashboard Operations Cockpit Advisory (WI-3433)

bridge_kind: governance_advisory
Document: gtkb-dashboard-operations-cockpit-advisory-disposition
Version: 001 (NEW)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-12 UTC
Source: `bridge/gtkb-dashboard-operations-cockpit-advisory-001.md` and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-28-14-52-GTKB-DASHBOARD-OPERATIONS-COCKPIT-ADVISORY.md`
Source Work Item: WI-3433
Recommended commit type: `docs:`
target_paths: ["bridge/gtkb-dashboard-operations-cockpit-advisory-disposition-001.md"]

implementation_scope: governance_advisory
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
source_mutation_in_scope: false

---

## Summary

Prime Builder classifies the Dashboard Operations Cockpit advisory as **`adapt`**. Prime accepts the advisory's core product/governance direction: the GT-KB dashboard should become a trustworthy operations cockpit by fixing metric truthfulness, clarifying GT-KB platform versus adopter/application scope, and presenting actionable workflow signals before broader visual redesign.

Prime adapts the execution path into a smaller first implementation slice. The first slice should focus on dashboard reliability and scope clarity, not a sweeping Grafana redesign. However, WI-3433 is currently open and `approval_state='unapproved'`, and the source advisory itself requires owner-grilling before any implementation proposal. Therefore this disposition performs no source, generated-dashboard, database, docs, or MemBase mutation. It hands the decision to Loyal Opposition for review and preserves the exact owner decisions required before a future implementation proposal may exist.

## Advisory Source

- Latest bridge advisory: `bridge/gtkb-dashboard-operations-cockpit-advisory-001.md`, latest status `ADVISORY` in live `bridge/INDEX.md`.
- Source insight: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-28-14-52-GTKB-DASHBOARD-OPERATIONS-COCKPIT-ADVISORY.md`.
- Routed work item: WI-3433, priority `high`, resolution `open`, approval_state `unapproved` as read from MemBase on 2026-06-12.
- Source advisory recommendation: classify as `adapt` and file a first-slice implementation proposal only after owner-grilling questions are answered and carried into `## Owner Decisions / Input`.

## Classification

**`adapt`** is the correct disposition.

- **`adopt` rejected:** adopting the full advisory as one proposal would mix metric semantics, dashboard scope modeling, workflow layout, local file affordances, refresh-service behavior, setup flow, and visual redesign. That is too broad for a reliable first implementation slice.
- **`adapt` selected:** the first slice should adopt the advisory's core pattern but narrow it to data correctness and scope authority: per-metric status functions, explicit dashboard subject/scope metadata, exact bridge/dashboard queue semantics, and first-viewport action routing if it can stay small and testable.
- **`reject` rejected:** the advisory identifies real contradictions, including hardcoded metric statuses and GT-KB/Agent Red scope confusion, that can make the dashboard untrustworthy.
- **`defer` rejected:** dashboard reliability and scope clarity are useful now; no future milestone is a technical prerequisite. The current blocker is owner decision evidence before implementation, not uncertainty about the value of the work.
- **`monitor` rejected:** passive monitoring would leave the dashboard with known trust-eroding semantics and no Prime-owned path to repair.

## Required Owner-Grilling Gate

This disposition preserves, but does not yet answer, the source advisory's required owner questions. Before Prime Builder files the implementation proposal, the following must be answered in durable AUQ / owner-decision evidence and cited in that proposal:

1. Should the default dashboard subject be GT-KB platform only, active adopter/application only, or combined operations with explicit badges?
2. Should local workspace file controls be copyable paths, read-only previews, or approved local-open actions?
3. Is the refresh service strictly loopback/local-only, or must the first slice harden it for exposed/shared use?
4. Should package-facing `gt dashboard` commands be the primary visible setup path even when running from the GT-KB source checkout?

Until those answers exist, this GO/NO-GO disposition must not be treated as implementation authorization.

## Proposed Follow-On Implementation Thread

If Loyal Opposition returns GO on this disposition and the owner-grilling gate is satisfied later, Prime Builder should file a separate implementation proposal, tentatively named `gtkb-dashboard-operations-cockpit-reliability-scope-slice`, with a narrow first-slice scope:

- Replace hardcoded `current_metrics` status strings with per-metric status functions and tests for zero/warning/failure cases.
- Add or expose dashboard subject/scope metadata so GT-KB platform state and active adopter/application state are not conflated.
- Split bridge/advisory/dashboard counts into exact queue semantics or label non-authoritative pressure counts clearly.
- Move top-action workflow signal, owner lane, and evidence age into first-viewport priority only if it can be implemented without broad visual redesign.
- Remove misleading local-path `Open` affordances or convert them to the owner-approved local workflow pattern chosen during the grilling gate.
- Preserve refresh-service hardening, setup-mode cleanup, and broad visual redesign as follow-on slices unless owner answers make them part of the minimum first slice.

Likely future target paths include `scripts/gtkb_dashboard/refresh_dashboard_db.py`, `scripts/gtkb_dashboard/generate_grafana_dashboard.py`, `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json`, `docs/gtkb-dashboard/index.html`, `groundtruth-kb/docs/reference/cli.md`, and focused platform tests. These paths are **not** authorized by this disposition.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified) - this disposition uses the live bridge and live `bridge/INDEX.md` as the handoff authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) - this file links the governing requirements and explicitly separates disposition from implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) - future implementation verification must map metric/scope/dashboard requirements to tests; this disposition has no source implementation.
- `GOV-STANDING-BACKLOG-001` v5 (verified) - WI-3433 is a governed advisory-routing item and remains open until a later governed disposition / implementation path resolves it.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) - the future implementation proposal must include valid project-linkage metadata once PAUTH coverage exists; this `governance_advisory` file is metadata-exempt.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` v1 (specified) and `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` v1 (specified) - the source advisory is an adapt recommendation and includes the required grilling gate; this disposition carries it forward.
- `GOV-ARTIFACT-APPROVAL-001` v3 (verified) - any future formal artifact, protected narrative artifact, or generated-dashboard authority change remains subject to its normal approval evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 (specified) - dashboard work must distinguish GT-KB platform state from adopter/application state and keep active files under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1 (verified), `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1 (verified), and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 (verified) - this advisory becomes a durable lifecycle artifact with explicit follow-on state.
- `SPEC-ADVISORY-REPORT-TEMPLATE-001`, `SPEC-ADVISORY-DASHBOARD-COUNTERS-001`, and `DCL-ADVISORY-ROUTING-001` - cited by the source ADVISORY as the advisory/report routing surface.
- `.claude/rules/peer-solution-advisory-loop.md` - supplies the adopt/adapt/reject/defer/monitor vocabulary used by the routing workflow.
- `.claude/rules/file-bridge-protocol.md` - supplies the live-index, preflight, author-metadata, and spec-derived verification obligations.

## Prior Deliberations

- `bridge/gtkb-dashboard-operations-cockpit-advisory-001.md` - LO ADVISORY handoff recommending `adapt` and listing the required owner-grilling gate.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-28-14-52-GTKB-DASHBOARD-OPERATIONS-COCKPIT-ADVISORY.md` - source P1 advisory.
- WI-3433 - high-priority open advisory-routing work item.
- `PROJECT-GTKB-LO-ADVISORY-ROUTING` - owner-directed project for routing LO advisories through five-state dispositions.
- `.claude/rules/peer-solution-advisory-loop.md` - classification vocabulary and owner-grilling gate discipline.
- `bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-001.md` - precedent for an `adapt` disposition that separates routing from implementation.

## Owner Decisions / Input

- Current owner instruction, 2026-06-12: continue PB-actionable work from the bridge or backlog and hand it off via the bridge protocol. This authorizes Prime to file this routing handoff, not to bypass the source advisory's owner-grilling gate.
- Source ADVISORY `gtkb-dashboard-operations-cockpit-advisory-001.md` explicitly says no owner decision is required merely to preserve the ADVISORY, but owner decisions are required before the recommended `adapt` implementation proposal.
- No owner decision currently answers the four dashboard scope/control questions listed above. That is why this file is a `governance_advisory` disposition and not an implementation proposal.

## Clause Scope Clarification

This disposition is a single-advisory routing record. It does not resolve WI-3433, does not create or consume a PAUTH, does not mutate MemBase, does not regenerate the dashboard, and does not edit dashboard code, docs, generated JSON, tests, or refresh services. The only immediate artifacts are this bridge file and its live index entry.

## Requirement Sufficiency

Existing requirements sufficient for the routing disposition. The source advisory already states the implementation-facing owner questions and a narrow adaptation direction. New or revised requirements are not needed to record Prime's `adapt` disposition. A future implementation proposal must cite the owner decisions, project authorization, and concrete dashboard specifications once the scope is owner-set.

## Acceptance Criteria

1. Loyal Opposition confirms `adapt` is the correct disposition for the dashboard operations cockpit advisory.
2. Loyal Opposition confirms this file does not authorize implementation and correctly preserves the four required owner-grilling questions.
3. Loyal Opposition confirms the proposed first-slice implementation scope is narrow enough for a later proposal and does not collapse the whole advisory into one broad change.
4. Applicability preflight and ADR/DCL clause preflight pass for this bridge file.
5. Prime Builder can use the GO, if granted, to obtain owner answers and then file a separate PAUTH-backed implementation proposal.

## Specification-Derived Verification Plan

| Linked specification / rule | Verification evidence for this disposition |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live `bridge/INDEX.md` contains this disposition with latest `NEW`, and the source ADVISORY remains visible as its own bridge thread. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dashboard-operations-cockpit-advisory-disposition` must report no missing required or advisory specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | No source implementation occurs in this disposition; no `python -m pytest` lane applies here. The future implementation proposal must define metric/status/scope tests and execute them. |
| `GOV-STANDING-BACKLOG-001` | DB read-back confirms WI-3433 is open/high/unapproved; this file records the single-item routing state and does not perform bulk resolution. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` / `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | This file carries forward all four source-advisory owner-grilling questions as preconditions for implementation. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | The future implementation must distinguish GT-KB platform state from adopter/application state; this disposition mutates no application subtree. |
| Artifact-oriented governance specs | The advisory becomes a durable Prime disposition with an explicit lifecycle state and follow-on boundary. |

Verification commands for Loyal Opposition / Prime self-check:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dashboard-operations-cockpit-advisory-disposition
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dashboard-operations-cockpit-advisory-disposition
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-dashboard-operations-cockpit-advisory-disposition --format json
```

## Risk and Rollback

- **Risk: still too broad.** LO may decide the proposed first slice should be only metric semantics, leaving scope banner and top-action routing for later. If so, issue NO-GO and Prime will revise to narrower scope.
- **Risk: owner-grilling gap.** If Prime later files an implementation proposal without answering the four questions, LO should NO-GO that later proposal. This disposition is not a substitute for those answers.
- **Risk: generated-dashboard authority ambiguity.** If future work regenerates `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json`, the implementation proposal must state whether generated output is authoritative or derived and how it is verified.
- **Rollback:** remove this bridge file and index line before commit if LO rejects the routing approach. No source, test, DB, dashboard, or documentation rollback is needed because this disposition performs no such mutation.

End of proposal.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
