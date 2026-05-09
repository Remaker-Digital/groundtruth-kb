NO-GO

# Loyal Opposition Review - Cross-Harness Trigger Active-Session Suppression - REVISED-1

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-003.md`
Verdict: NO-GO

## Claim

REVISED-1 fixes the critical state-machine defect from `-002`: suppressed signatures are no longer counted as dispatched, so the same actionable signature remains retryable after the active counterpart exits. The SessionStart/Stop lock direction is also a stronger active-session signal than the prior 120-second recent-tool-use heuristic.

However, the proposal still cannot receive GO because the proposed heartbeat lock path is not reconciled with the already-verified trigger state path. Implemented literally, heartbeat can write one directory while the trigger checks another, which would make the active-session suppression gate silently ineffective.

## Prior Deliberations

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "cross harness trigger active session suppression heartbeat lock session start stop dispatch signature" --limit 8`
- `python -m groundtruth_kb deliberations search "S337 active session suppression owner directive hook parity windows retest" --limit 10`

Relevant records and thread evidence:

- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - confirms Codex hook parity stance after empirical Windows hook support.
- `DELIB-1077` - prior session hook dispatcher repair context.
- `DELIB-0909` - prior Loyal Opposition smart bridge poller review context.
- Slice 2 signature dedup: `bridge/gtkb-bridge-poller-event-driven-replacement-009.md`, VERIFIED at `-010`.
- Slice 3 hook registration: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-005.md`, VERIFIED at `-006`, with hook commands using `.gtkb-state/bridge-poller`.
- Current thread `-002` - prior Codex NO-GO requiring suppressed signatures to remain retryable and requiring a stronger liveness model.

## Applicability Preflight

- packet_hash: `sha256:886e8e93e709cf964c041efc997731082aa83c392ae93d3e0c35a8957a82f1c9`
- bridge_document_name: `gtkb-cross-harness-trigger-active-session-suppression-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-003.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

- Bridge id: `gtkb-cross-harness-trigger-active-session-suppression-001`
- Operative file: `bridge\gtkb-cross-harness-trigger-active-session-suppression-001-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Findings

### F1 - P1 - Heartbeat and trigger can use different lock directories

Observation:

- The proposal says lock files live at `.gtkb-state/cross-harness-trigger/active-{role}-session.lock` (`-003`, line 53).
- The proposed heartbeat script takes optional `--state-dir` and writes `<state-dir>/active-{role}-session.lock` (`-003`, lines 86-87).
- The proposed trigger liveness check reads `state_dir / active-{counterpart_role}-session.lock` (`-003`, lines 139-141), and IP-3 passes the trigger's `state_dir` into that check (`-003`, line 206).
- The already-verified live trigger hooks pass `--state-dir` as `.gtkb-state/bridge-poller`, not `.gtkb-state/cross-harness-trigger`:
  - `.codex/hooks.json`, lines 85, 96, and 108.
  - `.claude/settings.json`, line 88.
  - `tests/scripts/test_slice_3_hook_registrations.py`, lines 32-35 and 243-249, explicitly pin the shared path to `.gtkb-state/bridge-poller`.
- IP-2 only says heartbeat hook commands include `--mode ... --role ...`; it does not say they pass the same state directory as the trigger (`-003`, lines 190-197).
- The test plan checks heartbeat behavior and hook ordering, but it does not include a test proving the heartbeat writer and trigger reader share the same lock directory (`-003`, lines 254-270).

Deficiency rationale:

This is not just documentation drift. If `active_session_heartbeat.py` defaults to `.gtkb-state/cross-harness-trigger` while `cross_harness_bridge_trigger.py --state-dir .gtkb-state/bridge-poller` calls `check_counterpart_active(..., state_dir)`, the trigger will look for active-session locks in `.gtkb-state/bridge-poller` and will not see the heartbeat locks. The suppression gate then fails open and continues spawning during active counterpart sessions.

The inverse implementation is also problematic: if the heartbeat silently writes `.gtkb-state/bridge-poller`, the proposal's stated lock-file location and isolation evidence are wrong.

Impact:

The slice can pass the proposed unit tests while failing its core operational purpose: preventing duplicate cross-harness subprocess dispatch during an active foreground counterpart session.

Recommended action:

Revise the proposal to make one directory contract explicit. Acceptable shapes:

1. Put heartbeat locks in the same `--state-dir` currently used by the trigger, `.gtkb-state/bridge-poller`, and update the proposal's path text accordingly.
2. Keep heartbeat locks in `.gtkb-state/cross-harness-trigger`, but add a separate explicit `--heartbeat-state-dir` or equivalent resolution path in the trigger and hook commands, rather than reusing dispatch `state_dir`.
3. Change both harness trigger registrations and tests to move the trigger's dispatch state to `.gtkb-state/cross-harness-trigger`, if Slice 4 is ready to retire the shared `.gtkb-state/bridge-poller` path in this thread.

Required test addition:

- Add `T-SUPPRESS-heartbeat-trigger-shared-lock-dir`: using the actual hook command shape or equivalent config-derived paths, create a heartbeat lock for one role and prove the trigger's counterpart-active check reads that exact file. This should fail if heartbeat defaults to `.gtkb-state/cross-harness-trigger` while trigger `--state-dir` remains `.gtkb-state/bridge-poller`.

### F2 - P2 - The new 3600-second sanity TTL is a material behavior change from the recorded 120-second owner input

Observation:

- The Owner Decisions / Input section records Mike's answer as "120 seconds" and says the longer 3600-second sanity TTL "does not require new owner authorization" (`-003`, line 74).
- The revised liveness model treats any lock younger than `GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS`, default 3600, as active (`-003`, lines 148-153).
- The test plan only checks that the sanity TTL env var can be overridden to 120 (`-003`, line 267). It does not require an owner decision or acceptance criterion for the new default one-hour crash-suppression window.

Impact:

If a harness crashes without Stop firing, dispatch to that role can be suppressed for up to one hour by default. That is a different operational tradeoff than the 120-second window the owner selected in the prior prompt, and it affects bridge latency during precisely the failure mode the trigger is meant to recover from.

Recommended action:

Either set the default sanity TTL to 120 seconds to match the recorded owner input, or add explicit Owner Decisions / Input evidence for the longer default. If the 3600-second default remains, add an acceptance criterion and test that document the one-hour crash-fail-open tradeoff as intentional.

## Positive Confirmations

- The F1 state-machine repair from `-002` is directionally correct: `last_dispatched_signature` as the dedup field and `last_suppressed_signature` as pending retry state preserves the Slice 2 invariant while allowing retry after active-session exit.
- The Stop ordering direction is correct: refresh, run trigger reconciliation, then remove self-lock.
- Keeping legacy `signature` updated only on real dispatch is the right backward-compat stance.
- The proposed retry test, `T-SUPPRESS-retry-after-counterpart-exits`, is the right load-bearing behavioral test for the prior NO-GO.

## Decision

NO-GO. Revise the path contract so the heartbeat writer and trigger reader use one explicit shared active-session lock directory, and test that exact integration. Also resolve or explicitly authorize the 3600-second sanity TTL default.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-active-session-suppression-001` - pass.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-active-session-suppression-001` - pass.
- `python -m groundtruth_kb deliberations search "cross harness trigger active session suppression heartbeat lock session start stop dispatch signature" --limit 8`.
- `python -m groundtruth_kb deliberations search "S337 active session suppression owner directive hook parity windows retest" --limit 10`.
- `Select-String` and line-numbered reads over the revised proposal, `.claude/settings.json`, `.codex/hooks.json`, `scripts/cross_harness_bridge_trigger.py`, and `tests/scripts/test_slice_3_hook_registrations.py`.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
