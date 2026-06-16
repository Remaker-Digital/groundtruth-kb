NO-GO
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 89edb78a-cd50-4039-8be5-69daca907578
author_model: gemini-2.5-pro
author_model_version: 2.5
author_model_configuration: default

# Loyal Opposition Review - Cross-Harness Trigger Active-Session Suppression

Reviewer: Loyal Opposition (Antigravity, harness C)
Date: 2026-06-16 UTC
Reviewed proposal: `bridge/gtkb-cross-harness-trigger-active-session-suppression-001.md`
Verdict: NO-GO

## Claim

The proposal identifies a real operational defect: the event-driven trigger can spawn a fresh counterpart harness while that counterpart is already being worked in an active foreground session. The general direction - suppress trigger-spawn when the recipient appears active - is correct.

However, the proposed state-machine contract is internally inconsistent. It requires the trigger to record the actionable signature even when a dispatch is suppressed, while also requiring a later retry to dispatch that same signature after the active session exits. With the current trigger's dedup model, those cannot both be true.

## Prior Deliberations

Deliberation search executed:

- `gt deliberations search suppression`

Relevant records and thread evidence:

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - event-driven trigger foundation after empirical Codex hook retest.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - parity stance refresh tied to the live hook behavior.
- `DELIB-2512` - Owner clarification: replace harness-wide active-session suppression with per-document leasing. The owner clarified that harness-wide active-session suppression is not desirable and should be replaced with per-document leasing (under `bridge_lease_registry.py`).
- Slice 2 signature dedup: `bridge/gtkb-bridge-poller-event-driven-replacement-009.md`, VERIFIED at `-010`.
- Slice 3 hook registration: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-005.md`, VERIFIED at `-006`.
- Current operational evidence from Slice 4: auto-dispatched Prime revisions can race with the in-session Prime.

## Applicability Preflight

- packet_hash: `sha256:e5d7ca4fcfc823e47fe9205bfb5802bc963a92f27090beaa1aad83589627d30d`
- bridge_document_name: `gtkb-cross-harness-trigger-active-session-suppression`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-active-session-suppression-001.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-active-session-suppression-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["tests/scripts/test_active_session_heartbeat.py", "tests/scripts/test_cross_harness_bridge_trigger.py", "tests/scripts/test_slice_3_hook_registrations.py"]
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-cross-harness-trigger-active-session-suppression`
- Operative file: `bridge\gtkb-cross-harness-trigger-active-session-suppression-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Citation Freshness

The citation freshness preflight detected the following stale bridge citations:

- `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`: cited version 9, latest version 20 (status VERIFIED).
- `gtkb-bridge-poller-event-driven-replacement`: cited version 9, latest version 10 (status VERIFIED).
- `gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations`: cited version 5, latest version 6 (status VERIFIED).
- `gtkb-governance-hygiene-bundle`: cited version 1, latest version 4 (status VERIFIED).

## Findings

### F1 - P0 - Recording the signature on suppression prevents the proposed later dispatch

Observation:

- The proposal says the gate fires after signature changes and "the `signature` field in dispatch-state.json is updated normally" even when dispatch is skipped.
- It also requires `T-SUPPRESS-reciprocal-after-exit`: after a fresh counterpart heartbeat suppresses dispatch, the heartbeat later goes stale and a later trigger fire dispatches the same pending work.
- The current trigger dedup contract stores one per-recipient `signature` and skips when the current signature equals the prior signature:
  - `scripts/cross_harness_bridge_trigger.py` reads `prior_signature`.
  - It builds the new recipient state with `signature`.
  - It returns `unchanged` when `prior_signature == signature`.
  - It writes that recipient state to `dispatch-state.json`.
- Therefore, if a fresh heartbeat causes the trigger to suppress dispatch but still stores the current actionable signature, the later trigger fire after heartbeat expiry sees the same signature and returns `unchanged`. It will not enter `_spawn_harness`.

Deficiency rationale:

The proposal combines "record the signature on skip" and "retry same signature after heartbeat expiry." The current state model treats recorded signature as already handled. It has no separate concept of "suppressed but still pending dispatch."

Impact:

The active-session gate can permanently suppress the very reciprocal dispatch it is meant to defer. In the Prime-NEW -> Codex-GO -> Prime workflow, a GO written while Prime is active can be marked handled without ever waking Prime after the foreground session exits.

Recommended action:

Revise the state model before implementation. Acceptable shapes:

- Split state fields into `observed_signature`, `last_dispatched_signature`, and `last_suppressed_signature`. Use `last_dispatched_signature` for loop-prevention dedup; do not let a suppressed signature count as dispatched.
- Or keep the existing `signature` field but add explicit retry logic: if `prior_signature == signature` and `last_result == "counterpart_active_session_present"` and the counterpart heartbeat is now stale, attempt dispatch instead of returning `unchanged`.

Required test changes:

- `T-SUPPRESS-signature-recorded-on-skip` must assert the chosen suppressed-state representation, not just that the normal dedup signature was overwritten.
- `T-SUPPRESS-reciprocal-after-exit` must use the exact same actionable signature on the retry after heartbeat expiry and prove `_spawn_harness` is entered.
- Existing unchanged-signature tests must still prove no relaunch after an actual dispatch has happened.

### F2 - P1 - "Active session" is implemented as recent tool activity, not session liveness

Observation:

- The proposal writes the heartbeat on PostToolUse and Stop, but not periodically while the harness is waiting, thinking, reading chat, or composing without tools.
- With a default freshness of 120 seconds, a foreground session with no tool use for more than 120 seconds is treated as inactive even though the session can still be open and in use.
- Conversely, the Stop hook writes a fresh heartbeat immediately before a session ends, which can suppress dispatch to a no-longer-active session for up to the freshness window.

Deficiency rationale:

This may be an acceptable heuristic, but it is not active-session liveness. The proposal names the behavior as "recipient harness already has an active session running," then implements "recipient harness had hook activity recently." The distinction matters because the stated defect is parallel foreground/subprocess work, not just rapid hook churn.

Impact:

The gate can still spawn parallel subprocesses during long quiet foreground sessions, and it can delay useful dispatch briefly after a session exits.

Recommended action:

Either:

- Reframe the proposal and tests as recent-activity suppression, explicitly accepting the 120-second false-negative/false-positive window; or
- Add a stronger liveness signal, such as session-start/session-stop markers with stale TTL semantics, process-aware checks where available, or periodic heartbeat if the harness supports it.

At minimum, update risk/acceptance text to state that 120 seconds is a recent-activity heuristic and add tests for "stale heartbeat but still open session is not detectable by this mechanism" as a documented limitation.

### F3 - P2 - Stale Citations to Sibling Threads

Observation:

- The pre-filing freshness preflight checks showed multiple stale citations in the proposal. Specifically, `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` is cited at version 9, but it has now reached version 20 and is `VERIFIED`.

Deficiency rationale:

Citing stale, un-updated bridge files introduces risk of design regression and misalignment with subsequent changes that were made in the sibling threads.

Impact:

Implementation might proceed based on an outdated assumption about the state of sibling hooks and pollers.

Recommended action:

Update the proposal to cite the current verified versions of all sibling and context threads, validating that the design remains compatible with their completed implementation.

## Positive Confirmations

- The operational problem is real and worth fixing before continuing Slice 4 and session-start formalization.
- The heartbeat-before-trigger ordering is the right ordering for this hook model.
- A 120-second default is reasonable as a first heuristic if the proposal explicitly treats it as recent-activity suppression rather than perfect liveness.
- `GTKB_ACTIVE_SESSION_FRESHNESS_SECONDS` is the right configuration shape for a narrow operational gate.
- A single DELIB packet for the owner directive is sufficient; this does not require new architectural specs if the state-machine behavior is corrected.

## Decision

NO-GO. Revise the suppression design so suppressed signatures remain retryable after heartbeat expiry, update stale sibling citations, and clarify the heartbeat model as recent-activity suppression or provide stronger session-liveness evidence.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-active-session-suppression`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-active-session-suppression`
- `python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-cross-harness-trigger-active-session-suppression`
- `gt deliberations search suppression`

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
