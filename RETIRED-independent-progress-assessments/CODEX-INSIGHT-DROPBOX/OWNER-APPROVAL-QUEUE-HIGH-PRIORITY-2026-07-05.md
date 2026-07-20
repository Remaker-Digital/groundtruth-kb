# Owner Approval Queue - Open High-Priority Work Items

Generated: 2026-07-05
Author: Codex / Prime Builder
Scope: Open high-priority backlog items still carrying legacy `approval_state=unapproved`

## Claim

There are 43 open high-priority work items in the live backlog that are still unapproved under the legacy approval-state field.

This packet queues those items for owner review and batch selection. It does not itself authorize implementation, mutate work-item state, create PAUTH, or grant bridge authority.

Update 2026-07-05T16:59Z: Owner approved Batch A1. Approval was captured as `DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL`; formal approval packet `.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL.json` validated successfully. `WI-5027`, `WI-4979`, and `WI-4837` received new active PAUTH records; `WI-4356` already had active PAUTH and was not duplicated.

Update 2026-07-05T17:08Z: Owner directed continuation until all 43 items have governed disposition. Approval was captured as `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE`; formal approval packet `.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json` validated successfully. Batch A2 received governed disposition: `WI-5028`, `WI-4978`, `WI-5009`, `WI-4538`, `WI-4849`, `WI-4535`, and `WI-4802` received new active PAUTH records; `WI-4870` already had active PAUTH under `PROJECT-HARNESS-PARITY-PHASE-2` and was not duplicated.

Update 2026-07-05T17:18Z: Batch B received governed disposition. New active PAUTH records were created for `WI-4702`, `WI-4725`, `WI-4712`, `WI-4764`, `WI-4808`, `WI-4961`, `WI-4962`, and `WI-4981`, with project placement split across OPS Dispatcher Modernization, Bridge Protocol Reliability, Role Authority Dispatcher-Only Purge, and Harness Parity Phase 2. `WI-4725` still has an older active PAUTH on retired `PROJECT-GTKB-DISPATCHER-CONTROL-CLI`; the new OPS Dispatcher PAUTH is the current usable authorization, while old-PAUTH cleanup remains a later governance cleanup.

Update 2026-07-05T17:25Z: Batch C received governed disposition. New active PAUTH records were created for `WI-4965`, `WI-4966`, `WI-4968`, `WI-4970`, and `WI-4971` under `PROJECT-HARNESS-EQUIVALENCE-PHASE-3`, and for `WI-4791` and `WI-4792` under `PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1`. Audit note: resolved `WI-4969` is terminal evidence for the scorecard activation path and should feed `WI-4791`, not be reopened.

Update 2026-07-05T17:34Z: Remaining 16 items received governed disposition. `WI-3430`, `WI-3431`, `WI-3445`, and `WI-4784` were confirmed under existing active PAUTH and annotated with status-detail disposition. `WI-3407`, `WI-4650`, `WI-4409`, `WI-4562`, `WI-4563`, `WI-4823`, and `WI-4827` were owner-approved deferred/demoted to `P3` with explicit re-evaluation conditions. `WI-4369`, `WI-4193`, `WI-4274`, `WI-4308`, and `WI-4705` were retired as stale/superseded route-only or stale-count items. Final disposition across the original 43: 31 active-PAUTH implementation-authorized, 5 retired, 7 deferred/demoted. No item remains without owner-linked governed disposition.

Implementation remains gated by:

- live matching bridge `GO` where protected source/config/test mutation is involved;
- project authorization / implementation-start packet where applicable;
- owner decision evidence such as AUQ or Deliberation Archive record;
- `gt backlog authorize-implementation` or project authorization command execution after owner approval.

## Evidence

Live query used:

```powershell
gt backlog list --resolution-status open --json |
  ConvertFrom-Json |
  Where-Object { $_.priority -in @('P0','P1','P2','high') } |
  Select-Object id,priority,stage,project_name,title,approval_state |
  Sort-Object @{Expression={switch ($_.priority) {'P0'{0};'P1'{1};'P2'{2};'high'{3};default{9}}}}, id |
  ConvertTo-Json -Depth 4
```

Observed count:

- P0: 0
- P1: 0
- P2: 39
- legacy `high`: 4
- total: 43

Related authorization checks:

```powershell
gt backlog list --approval-state implementation_authorized --resolution-status open --json
gt backlog list --approval-state bridge_authorized --resolution-status open --json
```

Observed result: no open items in either already-authorized approval state.

Dispatcher/bridge orientation at queue creation:

- `gt bridge dispatch status --json`: health PASS; 0 pending; 0 live for LO:B, LO:C, PB:A.
- Prime bridge scan: no fresh PB implementation slice selected from this packet; the queue is owner-review preparation only.

## Approval Options

Recommended approval path: approve a small first batch that improves finalization, bridge integrity, and authorization hygiene, then continue through the remaining batches in dependency order.

Owner reply shapes this packet is designed to support:

- `Approve Batch A1`
- `Approve Batch A2`
- `Approve Batch B`
- `Approve WI-5027 only`
- `Defer Batch C`
- `Retire WI-4193`
- `Re-scope WI-4650 before approval`

## Batch A1 - Worktree And Finalization Hygiene

Recommended first batch. These items reduce accumulated finalization risk and make subsequent terminal-state work safer.

| ID | Priority | Project | Title |
| --- | --- | --- | --- |
| WI-5027 | P2 | none | Worktree finalization/commit-discipline lapse: 222 uncommitted bridge verdicts + accumulated cross-stream edits |
| WI-4979 | P2 | PROJECT-GTKB-RELIABILITY-FIXES | Work-tree hygiene Slice E: generalized recurring actuator with auto-resolve triage |
| WI-4356 | P2 | PROJECT-GTKB-RELIABILITY-FIXES | Define and implement recurring work-tree hygiene + stash-stray-cleanup mechanism |
| WI-4837 | P2 | none | Post-VERIFIED Prime-side finalization-recovery is gate-blocked (no re-auth path + cross-session snapshot block) |

Recommended disposition: approve as a focused reliability/finalization package, with WI-5027 first.

## Batch A2 - Bridge Governance Integrity

These items address bridge-verdict identity, filing validation, owner-decision queue cleanup, and bridge-linked resolution defects.

| ID | Priority | Project | Title |
| --- | --- | --- | --- |
| WI-5028 | P2 | none | Headless bridge-verdict filing mis-stamps durable author identity when GTKB_HARNESS_NAME is unset |
| WI-4978 | P2 | none | Codex bridge helper filing paths bypass the bridge-compliance-gate Requirement-Sufficiency (and mandatory-element) checks |
| WI-5009 | P2 | PROJECT-GTKB-RELIABILITY-FIXES | Harden spec-before-code bridge-derived platform_tests coverage against stale or rejected bridge path mentions |
| WI-4538 | P2 | none | Auto-clear/dedup pending-owner-decision queue entries when the underlying work is resolved (cross-session) |
| WI-4849 | P2 | none | Impl-start begin gate blocks on a peer LO lingering draft/review claim, delaying Prime post-GO implementation |
| WI-4870 | P2 | none | Project auto-retirement strands open GO bridge threads (PAUTH unattached), blocking implementation by headless workers in the live pipeline |
| WI-4535 | P2 | none | Reconciler linked_bridge_not_verified gate blocks resolution when a VERIFIED WI is co-linked to a terminal umbrella ADVISORY/advisory-GO thread |
| WI-4802 | P2 | none | VERIFIED backlog reconciler blocks WI resolution on WITHDRAWN/ADVISORY sibling threads |

Recommended disposition: approve after A1 or together with A1 if the owner wants a larger reliability authorization window.

## Batch B - Dispatcher, Bridge Runtime, And Harness Reliability

These items improve runtime correctness and harness continuity.

| ID | Priority | Project | Title |
| --- | --- | --- | --- |
| WI-4702 | P2 | none | bridge dispatch --reset-recipient default --state-dir mismatch yields silent false-green reset |
| WI-4725 | P2 | none | Dispatch-health stale FAIL: stored failed-launch (exit_failure_reason) reads as a live FAIL while new dispatch is suppressed (work_intent_already_held), never self-clearing |
| WI-4712 | P2 | none | test_cross_harness_bridge_trigger.py regression suite has 39/91 pre-existing failures in the run_trigger integration path |
| WI-4764 | P2 | none | Heartbeat automation re-resolves durable role mid-session causing role-confusion |
| WI-4808 | P2 | none | Optimize preflight._check_bridge_inflight: avoid O(n) full read of all bridge/ files (>8400) causing >30s test timeout |
| WI-4961 | P2 | none | Cleanse prompt-generation helpers, harness instructions, and memory to emit correctly-formed session-kickoff prompts |
| WI-4962 | P2 | none | Ollama-D harness reliability: fix subprocess_execution_failed + 540s session-budget worker_timeout so D completes dispatched LO reviews and draws down idle pre-paid cloud credits |
| WI-4981 | P2 | PROJECT-GTKB-RELIABILITY-FIXES | Mid-session ::init gtkb (pb\|lo) role switch silently no-ops (recognized but not persisted) |

Recommended disposition: approve after the A batches unless a live dispatcher outage recurs, in which case promote WI-4702, WI-4725, and WI-4808.

## Batch C - Harness Equivalence, Benchmarks, And Quality KPIs

These items align with the harness/model benchmarking and equivalence loop.

| ID | Priority | Project | Title |
| --- | --- | --- | --- |
| WI-4965 | P2 | PROJECT-HARNESS-EQUIVALENCE-PHASE-3 | Phase 3 gap 03: skill discoverability and effectiveness by activity |
| WI-4966 | P2 | PROJECT-HARNESS-EQUIVALENCE-PHASE-3 | Phase 3 gap 04: CLI compactness and source-of-truth size controls |
| WI-4968 | P2 | PROJECT-HARNESS-EQUIVALENCE-PHASE-3 | Phase 3 gap 06: activity and result envelope equivalence evidence |
| WI-4970 | P2 | PROJECT-HARNESS-EQUIVALENCE-PHASE-3 | Phase 3 gap 08: deterministic child-WI generator and checklist |
| WI-4971 | P2 | PROJECT-HARNESS-EQUIVALENCE-PHASE-3 | Phase 3 gap 09: evidence freshness and archival boundaries |
| WI-4791 | P2 | GTKB-DISPATCHER-COMPLETION | Phase 4 - Quality-KPI subsystem: consensus capture calibrated by seeded-flaw fixtures; compute relative quality inside the dispatcher and feed TAFE; per-activity quality-required floors |
| WI-4792 | P2 | GTKB-DISPATCHER-COMPLETION | Phase 5 - Harness-adaptation impact measurement: versioned adaptations + seeded-flaw fixture A/B for attributable KPI deltas; Cursor as first consumer |

Recommended disposition: approve as one harness-equivalence/quality loop only after confirming whether WI-4969 and WI-4791 should share a single disposition path for the 2026-07-03 harness/model benchmarking report.

## Batch D - Architecture, Topology, And Formal Artifact Control

These items affect durable architecture and formal artifact handling.

| ID | Priority | Project | Title |
| --- | --- | --- | --- |
| WI-3407 | P2 | GTKB-V1-RELEASE-STRATEGY-001 | Create decision-capture composite DELIB workflow skill (per owner agreement) |
| WI-3430 | P2 | PROJECT-GTKB-ENV-SOT-TOPOLOGY | Migrate Agent Red from 3-file SoT layout to single SoT + CLI-generated per-sub-app views |
| WI-3431 | P2 | PROJECT-GTKB-ENV-SOT-TOPOLOGY | Separate platform-level values from Agent Red application-level values in root .env.local |
| WI-4650 | P2 | none | Decide GT-KB multi-node / networked shared-root topology (gates A1-E2 multi-node capability gaps) |
| WI-4705 | P2 | none | 1,304 formal-artifact approval packets are untracked-local (.groundtruth/ blanket-ignored); narrative-artifact gate fails in fresh clones |
| WI-4784 | P2 | GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE | Phase 3 - Terminology purge: replace durable-role language; invert enumerated-override framing; update canonical-terminology.md |

Recommended disposition: approve only with architecture-alignment review, because these items can reshape GT-KB topology and formal artifact authority.

## Batch E - Protected Artifact Drift And Advisory Routing

These items are older high-priority advisory/protected-artifact issues that should be explicitly approved, deferred, retired, or superseded.

| ID | Priority | Project | Title |
| --- | --- | --- | --- |
| WI-4369 | P2 | PROJECT-GTKB-PROTECTED-ARTIFACT-DRIFT-ROLLUP | Protected-artifact drift rollup: govern 23-path accumulated drift via per-cluster AUQs |
| WI-4193 | high | none | Route LO advisory: INSIGHTS-2026-04-22-13-09-BRIDGE-SCAN-ROLE-AUTHORITY-GOV-FAILURE.md |
| WI-4274 | high | none | Route LO advisory: INSIGHTS-2026-06-03-14-27-GTKB-PROPOSE-SCAFFOLD-VALIDATION-GAP.md |
| WI-4308 | high | none | Route LO advisory: INSIGHTS-2026-06-04-13-20-test-suite-drift.md |
| WI-4409 | high | none | Route LO advisory: INSIGHTS-2026-06-09-19-03-arch-audit-findings.md |

Recommended disposition: start by checking whether each legacy `high` advisory is already superseded by later WI or project records; approve only the remainder.

## Batch F - Review Contract Follow-Through

This item is standalone and can be approved independently.

| ID | Priority | Project | Title |
| --- | --- | --- | --- |
| WI-3445 | P2 | none | Slice 2: Update CODEX-REVIEW contracts + 3 LO-advisory-emitting skills |

Recommended disposition: approve after deciding whether the associated LO-advisory-emitting skills still match the current bridge/dispatcher architecture.

## Full Item Inventory

| ID | Priority | Project | Approval State | Title |
| --- | --- | --- | --- | --- |
| WI-3407 | P2 | GTKB-V1-RELEASE-STRATEGY-001 | unapproved | Create decision-capture composite DELIB workflow skill (per owner agreement) |
| WI-3430 | P2 | PROJECT-GTKB-ENV-SOT-TOPOLOGY | unapproved | Migrate Agent Red from 3-file SoT layout to single SoT + CLI-generated per-sub-app views |
| WI-3431 | P2 | PROJECT-GTKB-ENV-SOT-TOPOLOGY | unapproved | Separate platform-level values from Agent Red application-level values in root .env.local |
| WI-3445 | P2 | none | unapproved | Slice 2: Update CODEX-REVIEW contracts + 3 LO-advisory-emitting skills |
| WI-4356 | P2 | PROJECT-GTKB-RELIABILITY-FIXES | unapproved | Define and implement recurring work-tree hygiene + stash-stray-cleanup mechanism |
| WI-4369 | P2 | PROJECT-GTKB-PROTECTED-ARTIFACT-DRIFT-ROLLUP | unapproved | Protected-artifact drift rollup: govern 23-path accumulated drift via per-cluster AUQs |
| WI-4535 | P2 | none | unapproved | Reconciler linked_bridge_not_verified gate blocks resolution when a VERIFIED WI is co-linked to a terminal umbrella ADVISORY/advisory-GO thread |
| WI-4538 | P2 | none | unapproved | Auto-clear/dedup pending-owner-decision queue entries when the underlying work is resolved (cross-session) |
| WI-4562 | P2 | none | unapproved | Add gt project doctor check for deliberation-search-backend health (ChromaDB usable + index fresh) |
| WI-4563 | P2 | none | unapproved | Mandatory deliberation search degrades silently to SQLite-LIKE; should fail loudly (governance gap) |
| WI-4650 | P2 | none | unapproved | Decide GT-KB multi-node / networked shared-root topology (gates A1-E2 multi-node capability gaps) |
| WI-4702 | P2 | none | unapproved | bridge dispatch --reset-recipient default --state-dir mismatch yields silent false-green reset |
| WI-4705 | P2 | none | unapproved | 1,304 formal-artifact approval packets are untracked-local (.groundtruth/ blanket-ignored); narrative-artifact gate fails in fresh clones |
| WI-4712 | P2 | none | unapproved | test_cross_harness_bridge_trigger.py regression suite has 39/91 pre-existing failures in the run_trigger integration path |
| WI-4725 | P2 | none | unapproved | Dispatch-health stale FAIL: stored failed-launch (exit_failure_reason) reads as a live FAIL while new dispatch is suppressed (work_intent_already_held), never self-clearing |
| WI-4764 | P2 | none | unapproved | Heartbeat automation re-resolves durable role mid-session causing role-confusion |
| WI-4784 | P2 | GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE | unapproved | Phase 3 - Terminology purge: replace durable-role language; invert enumerated-override framing; update canonical-terminology.md |
| WI-4791 | P2 | GTKB-DISPATCHER-COMPLETION | unapproved | Phase 4 - Quality-KPI subsystem: consensus capture calibrated by seeded-flaw fixtures; compute relative quality inside the dispatcher and feed TAFE; per-activity quality-required floors |
| WI-4792 | P2 | GTKB-DISPATCHER-COMPLETION | unapproved | Phase 5 - Harness-adaptation impact measurement: versioned adaptations + seeded-flaw fixture A/B for attributable KPI deltas; Cursor as first consumer |
| WI-4802 | P2 | none | unapproved | VERIFIED backlog reconciler blocks WI resolution on WITHDRAWN/ADVISORY sibling threads |
| WI-4808 | P2 | none | unapproved | Optimize preflight._check_bridge_inflight: avoid O(n) full read of all bridge/ files (>8400) causing >30s test timeout |
| WI-4823 | P2 | none | unapproved | Concurrent Prime sessions implemented same GO'd slice; report filed with another session's context id (WI-4810 collision) |
| WI-4827 | P2 | none | unapproved | Startup-disclosure relay emits FAILURE on init-keyword turn despite cryptographically-intact cache (TOCTOU: failure-check precedes same-turn regeneration) |
| WI-4837 | P2 | none | unapproved | Post-VERIFIED Prime-side finalization-recovery is gate-blocked (no re-auth path + cross-session snapshot block) |
| WI-4849 | P2 | none | unapproved | Impl-start begin gate blocks on a peer LO lingering draft/review claim, delaying Prime post-GO implementation |
| WI-4870 | P2 | none | unapproved | Project auto-retirement strands open GO bridge threads (PAUTH unattached), blocking implementation by headless workers in the live pipeline |
| WI-4961 | P2 | none | unapproved | Cleanse prompt-generation helpers, harness instructions, and memory to emit correctly-formed session-kickoff prompts |
| WI-4962 | P2 | none | unapproved | Ollama-D harness reliability: fix subprocess_execution_failed + 540s session-budget worker_timeout so D completes dispatched LO reviews and draws down idle pre-paid cloud credits |
| WI-4965 | P2 | PROJECT-HARNESS-EQUIVALENCE-PHASE-3 | unapproved | Phase 3 gap 03: skill discoverability and effectiveness by activity |
| WI-4966 | P2 | PROJECT-HARNESS-EQUIVALENCE-PHASE-3 | unapproved | Phase 3 gap 04: CLI compactness and source-of-truth size controls |
| WI-4968 | P2 | PROJECT-HARNESS-EQUIVALENCE-PHASE-3 | unapproved | Phase 3 gap 06: activity and result envelope equivalence evidence |
| WI-4970 | P2 | PROJECT-HARNESS-EQUIVALENCE-PHASE-3 | unapproved | Phase 3 gap 08: deterministic child-WI generator and checklist |
| WI-4971 | P2 | PROJECT-HARNESS-EQUIVALENCE-PHASE-3 | unapproved | Phase 3 gap 09: evidence freshness and archival boundaries |
| WI-4978 | P2 | none | unapproved | Codex bridge helper filing paths bypass the bridge-compliance-gate Requirement-Sufficiency (and mandatory-element) checks |
| WI-4979 | P2 | PROJECT-GTKB-RELIABILITY-FIXES | unapproved | Work-tree hygiene Slice E: generalized recurring actuator with auto-resolve triage |
| WI-4981 | P2 | PROJECT-GTKB-RELIABILITY-FIXES | unapproved | Mid-session ::init gtkb (pb\|lo) role switch silently no-ops (recognized but not persisted) |
| WI-5009 | P2 | PROJECT-GTKB-RELIABILITY-FIXES | unapproved | Harden spec-before-code bridge-derived platform_tests coverage against stale or rejected bridge path mentions |
| WI-5027 | P2 | none | unapproved | Worktree finalization/commit-discipline lapse: 222 uncommitted bridge verdicts + accumulated cross-stream edits |
| WI-5028 | P2 | none | unapproved | Headless bridge-verdict filing mis-stamps durable author identity when GTKB_HARNESS_NAME is unset |
| WI-4193 | high | none | unapproved | Route LO advisory: INSIGHTS-2026-04-22-13-09-BRIDGE-SCAN-ROLE-AUTHORITY-GOV-FAILURE.md |
| WI-4274 | high | none | unapproved | Route LO advisory: INSIGHTS-2026-06-03-14-27-GTKB-PROPOSE-SCAFFOLD-VALIDATION-GAP.md |
| WI-4308 | high | none | unapproved | Route LO advisory: INSIGHTS-2026-06-04-13-20-test-suite-drift.md |
| WI-4409 | high | none | unapproved | Route LO advisory: INSIGHTS-2026-06-09-19-03-arch-audit-findings.md |

## Not Included In The Batch Recommendations Yet

The following open high-priority items were included in the full inventory but not assigned to a recommended approval batch above because they likely need fresh scope validation before owner approval:

| ID | Priority | Project | Title | Why Hold For Scope Check |
| --- | --- | --- | --- | --- |
| WI-4562 | P2 | none | Add gt project doctor check for deliberation-search-backend health (ChromaDB usable + index fresh) | Related to deliberation-search reliability; should be grouped with WI-4563 or a deliberation-search project. |
| WI-4563 | P2 | none | Mandatory deliberation search degrades silently to SQLite-LIKE; should fail loudly (governance gap) | Related to WI-4562; approval should decide fail-loud behavior and fallback semantics together. |
| WI-4823 | P2 | none | Concurrent Prime sessions implemented same GO'd slice; report filed with another session's context id (WI-4810 collision) | Needs reconciliation against terminal WI-4810 and current work-intent collision behavior. |
| WI-4827 | P2 | none | Startup-disclosure relay emits FAILURE on init-keyword turn despite cryptographically-intact cache (TOCTOU: failure-check precedes same-turn regeneration) | Needs re-check after recent bridge/harness restoration work. |

## Recommended Next Decision

Approve Batch A1 first:

- WI-5027
- WI-4979
- WI-4356
- WI-4837

Reason: these items directly reduce finalization and worktree hygiene risk before larger protected implementation batches proceed.

Expected owner reply:

```text
Approve Batch A1
```

or

```text
Approve WI-5027 only
```

After owner approval, the next governed step is to capture the decision evidence and use the appropriate authorization command or project authorization flow before implementation begins.
