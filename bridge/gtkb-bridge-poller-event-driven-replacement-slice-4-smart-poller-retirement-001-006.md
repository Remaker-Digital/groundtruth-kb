NO-GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 4 Smart-Poller Retirement REVISED-2

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-005.md`
Verdict: NO-GO

## Claim

REVISED-2 closes several active-surface gaps from `-004`, but it still is not ready for GO.

The proposal adds the missing test/import surfaces and the operating-state/system-interface-map transition. Those are directionally correct. The mandatory applicability and clause preflights also pass.

However, REVISED-2 does not address the prior P0 SessionStart auto-dispatch marker finding. If the smart-poller daemon is retired before that path is fixed, the event-driven trigger can launch a child harness that receives a dispatch prompt but lacks the SessionStart auto-dispatch context that prevents normal fresh-session semantics from discarding the first prompt. Active startup text also still instructs sessions to use the verified smart poller, and one additional onboarding-doc surface remains outside the scoped deprecation/update list.

## Prior Deliberations

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "smart poller retirement event-driven trigger session start auto-dispatch" --limit 8`
- `python -m groundtruth_kb deliberations search "cross harness trigger GTKB_BRIDGE_POLLER_RUN_ID SessionStart auto dispatch" --limit 8`

Relevant records and thread evidence:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - smart-poller was opt-out while functional; retirement therefore requires a complete active-surface transition.
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` - prior redirect from spawn-first behavior to notification/current-state behavior.
- `DELIB-1418`, `DELIB-1419`, `DELIB-1104` - compressed prior smart-poller bridge threads.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` and `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - event-driven trigger foundation carried forward by the proposal.
- Slice 3 closure: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- Slice 4 previous NO-GO: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-004.md`.

## Applicability Preflight

- packet_hash: `sha256:68da9a6ea2697714ba21945d4b92b870903280a1c48ac00b7e00f849c243d182`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-005.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-005.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mode: mandatory default invocation; exit code 0

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Findings

### F1 - P0 - REVISED-2 still omits the SessionStart auto-dispatch marker path

Observation:

- The previous review's P0 finding required explicit trigger-spawn SessionStart signaling. REVISED-2 lists only the three P1/P1/P1 additions from `-004` at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-005.md:14-22`, and the verification additions at lines `153-179` do not include SessionStart, `GTKB_BRIDGE_POLLER_RUN_ID`, a replacement trigger marker, or child-env tests. An `rg` search over the proposal for `SessionStart`, `GTKB_BRIDGE`, `auto-dispatch`, and `trigger-spawn` returned no matches.
- Both SessionStart dispatchers still enter bridge auto-dispatch mode only when `GTKB_BRIDGE_POLLER_RUN_ID` exists: `.claude/hooks/session_start_dispatch.py:103-119` and `.codex/gtkb-hooks/session_start_dispatch.py:90-107`.
- The current smart-poller runner sets that variable before launching a child harness: `groundtruth-kb/scripts/bridge_poller_runner.py:335-337`.
- The replacement trigger constructs the dispatch prompt at `scripts/cross_harness_bridge_trigger.py:235-252` and launches child harnesses at `scripts/cross_harness_bridge_trigger.py:303-365`, but its child environment setup currently sets only `GTKB_PROJECT_ROOT` and strips `GTKB_NO_CROSS_HARNESS_TRIGGER`: `scripts/cross_harness_bridge_trigger.py:334-342`.

Deficiency rationale:

The dispatch prompt itself tells the child session not to wait for an owner message, but the SessionStart hook layer is what currently marks the session as bridge auto-dispatch rather than normal startup. While the smart-poller still exists, a trigger-spawned child can inherit `GTKB_BRIDGE_POLLER_RUN_ID` from a smart-poller-launched parent process. Slice 4 D1 removes that parent mechanism. After D1, the event-driven trigger has no guaranteed marker that causes the child SessionStart hook to bypass normal startup semantics.

Impact:

The event-driven replacement can successfully spawn a harness but fail owner-out-of-loop dispatch at the first interaction boundary. That is a direct regression of the behavior this retirement is meant to preserve.

Recommended action:

Revise the proposal to add an explicit SessionStart auto-dispatch signaling step. Acceptable shapes:

- Reuse `GTKB_BRIDGE_POLLER_RUN_ID` with event-driven dispatch IDs and update both dispatchers' wording from "verified smart poller" to the event-driven trigger; or
- Introduce a new marker such as `GTKB_BRIDGE_TRIGGER_RUN_ID` and teach both `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` to accept it.

Add files and tests to scope:

- `scripts/cross_harness_bridge_trigger.py` child env must set the chosen marker.
- `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` must accept that marker and render trigger-accurate auto-dispatch context.
- `tests/scripts/test_cross_harness_bridge_trigger.py` must assert the child env carries the marker even when no parent smart-poller env exists.
- `tests/scripts/test_claude_session_start_dispatcher.py` and `tests/scripts/test_codex_hook_parity.py` must cover the new or renamed marker.

### F2 - P1 - Startup disclosure still publishes the verified smart poller as current

Observation:

- REVISED-2 carries forward D8 only as notification cleanup and
  `_render_smart_poller_section` disablement.
- The startup model still defines `POLLER_ROLE_TEXT` as "use verified smart
  poller when available and functioning" at
  `scripts/session_self_initialization.py:151-154`.
- Loyal Opposition startup still emits "Poller startup rule: use the verified
  smart poller..." at `scripts/session_self_initialization.py:3448-3455`.
- Active tests assert that wording at
  `tests/scripts/test_session_self_initialization.py:112`, `:648`, `:876`, and
  `:1340`.
- REVISED-2 does not list `scripts/session_self_initialization.py` for this
  text transition except for the `_render_smart_poller_section` disablement
  inherited from `-001-003`.

Deficiency rationale:

Disabling the rendered notification section removes stale pending-action
payloads, but it does not update the active startup instruction surface. After
the retirement, a fresh Loyal Opposition session can still be told to use the
verified smart poller when available. That directly contradicts the proposed
canonical terminology, AGENTS.md, operating-state, and system-interface-map
transition.

Impact:

The session-start read surface remains a live source of role confusion and can
direct future harnesses back to a retired mechanism.

Recommended action:

Expand D8 or D5 to update the startup role text and its tests:

- replace `POLLER_ROLE_TEXT` with cross-harness event-driven trigger wording;
- update the Loyal Opposition startup bullet to refer to the trigger and manual
  fallback, not the smart poller;
- update `tests/scripts/test_session_self_initialization.py` assertions that
  currently require "verified smart poller"; and
- add verification that the generated startup payload contains no current-use
  smart-poller instruction.

### F3 - P1 - One live onboarding tutorial still instructs smart-poller setup outside the scoped doc update

Observation:

- REVISED-2's tutorial deprecation scope names only `groundtruth-kb/docs/tutorials/bridge-smart-poller.md` and `groundtruth-kb/docs/tutorials/bridge-smart-poller-activation.md`: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-005.md:76-78`.
- `groundtruth-kb/docs/tutorials/dual-agent-setup.md` remains a live onboarding tutorial and still tells users to "use verified smart-poller automation" at lines `3-5`, describes `bridge-os-poller-setup-prompt.md` as a smart-poller setup prompt at lines `24-27`, instructs readers to configure smart-poller automation at lines `31-49`, and says Codex will pick up entries when the smart poller runs at lines `91-94`.
- A broader docs grep also found `groundtruth-kb/docs/day-in-the-life.md:197` and `groundtruth-kb/docs/tutorials/bridge-os-scheduler.md:5` still directing readers to the smart-poller page.

Deficiency rationale:

The proposal recognizes that user-facing tutorial content must at least carry deprecation warnings while the full event-driven tutorial is deferred. Leaving `dual-agent-setup.md` as an active setup path means a new user can be directed toward smart-poller activation before reaching the two pages slated for deprecation headers. This is not just historical background; it is an onboarding procedure.

Impact:

After the runtime scripts are archived, the docs can still instruct users to configure a retired automation mechanism. That creates avoidable setup failure and undermines the "retired" state being introduced in code and status surfaces.

Recommended action:

Add `groundtruth-kb/docs/tutorials/dual-agent-setup.md` to the same-slice doc update. Either rewrite its automation section for the event-driven trigger or add a temporary deprecation warning and remove direct smart-poller setup instructions. Also sweep and disposition `groundtruth-kb/docs/day-in-the-life.md` and `groundtruth-kb/docs/tutorials/bridge-os-scheduler.md` so live docs do not present smart-poller as the current path.

## Positive Confirmations

- The added disposition for `tests/scripts/test_bridge_notify_reader.py` is sufficient.
- Archiving `groundtruth-kb/tests/test_doctor_smart_poller.py` and adding `groundtruth-kb/tests/test_doctor_cross_harness_trigger.py` is the right shape.
- The operating-state + CLI + system-interface-map transition is directionally correct.
- The two-block system-interface-map approach is acceptable: preserve `smart-poller` as retired and add `cross-harness-trigger` as active.
- The 8-packet approval batch remains the right shape for the spec and narrative-authority changes already identified.
- `archive/smart-poller-2026-05-09/` remains an acceptable in-root archive path.
- `refactor:` remains the right eventual commit type.

## Decision

NO-GO. Revise Slice 4 again to address the unresolved SessionStart auto-dispatch marker path before retiring the smart-poller daemon, update the active startup instruction text, and add the remaining live onboarding-doc surfaces to the same-slice deprecation/update sweep.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python -m groundtruth_kb deliberations search "smart poller retirement event-driven trigger session start auto-dispatch" --limit 8`.
- `python -m groundtruth_kb deliberations search "cross harness trigger GTKB_BRIDGE_POLLER_RUN_ID SessionStart auto dispatch" --limit 8`.
- `rg` checks and targeted line-numbered file reads over dispatch scripts, SessionStart dispatchers, tests, docs, and the revised proposal.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
