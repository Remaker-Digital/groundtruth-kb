NEW

# Implementation Proposal - Cross-Harness Trigger Dispatch-State Refresh Lag (WI-3265)

bridge_kind: implementation_proposal
Document: gtkb-cross-harness-trigger-dispatch-state-lag
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3265

target_paths: ["scripts/cross_harness_bridge_trigger.py", "tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", ".gtkb-state/bridge-poller/dispatch-state.json"]

This NEW proposal investigates and fixes the cross-harness trigger's dispatch-state refresh lag observed in Codex exec sessions. Symptom: Codex completes a cross-harness dispatch session (writes verdict + edits INDEX), but `dispatch-state.json` does not refresh until the next manual or interactive-session trigger fires.

## Claim

The cross-harness trigger's per-recipient dispatch-state write happens at trigger invocation time, not at counterpart-session completion. When Codex exec completes a dispatched review, the resulting Stop hook fires its own cross-harness-trigger pass, but the state may not reflect the just-completed action because: (a) the session's verdict-write tool call already updated INDEX before Stop, (b) Stop's trigger pass reads dispatch-state.json from before the session's edits.

Hypothesis: trigger needs a post-Write refresh or signature-recomputation step. This proposal lands a diagnostic + a targeted fix.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness trigger is the active dispatch substrate.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; dispatch state is monitoring infrastructure.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - dispatch reliability supports artifact-oriented governance.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3265 tracked.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - batch-3 authorization.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - empirical foundation that Codex hooks fire on Windows (enabling the trigger).

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner directive "Please continue with the next priority project" - authorizes this NEW.

## Requirement Sufficiency

Existing requirements sufficient. WI-3265 description + ADR-CODEX-HOOK-PARITY-FALLBACK-001 specify the trigger's role.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-DETERMINISTIC-SERVICES-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch3-deterministic-services-authorization.json`. Review-packet inventory: IP-1 (diagnostic) + IP-2 (fix) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-001.md`; new top entry prepended.

## Proposed Scope

### IP-1: Diagnostic instrumentation

In `scripts/cross_harness_bridge_trigger.py`, add structured logging (to `.gtkb-state/bridge-poller/trigger.log`) at:
- Entry: invocation source (PostToolUse/Stop/manual), invoking PID, current dispatch-state mtime.
- Pre-signature-compute: live INDEX mtime.
- Post-dispatch: new dispatch-state mtime, signature delta.

Log entries include UTC ISO timestamp and JSON-line format. Non-blocking; ~5 lines per invocation.

### IP-2: Fix candidate (subject to diagnostic feedback)

Hypothesis-driven fix: in the Stop-event branch, force a re-read of `bridge/INDEX.md` AFTER the agent's last Write to capture the most recent state. Currently the trigger may read a cached/pre-Write copy.

Concrete: open INDEX with `os.O_RDONLY` immediately before signature computation; do NOT cache the parse across invocations. Add a small file-mtime poll loop (max 200ms) waiting for INDEX mtime stabilization if a Write hook ran within the last second.

### IP-3: Tests + (no spec promotion - debug fix)

Tests cover: trigger invocation logging schema, signature computation freshness, mtime stabilization behavior, end-to-end dispatch after rapid INDEX edits.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Diagnostic log emits on every invocation | `test_trigger_emits_diagnostic_log_line_per_invocation` |
| Log format is JSON-line parseable | `test_trigger_log_is_jsonline_parseable` |
| Signature recomputed on every invocation | `test_trigger_recomputes_signature_no_caching` |
| Stop-mode reads INDEX fresh | `test_trigger_stop_mode_reads_index_fresh` |
| Rapid INDEX edits trigger dispatch update | `test_trigger_dispatches_after_rapid_index_edits` |
| Diagnostic captures sequence of mtime changes | `test_trigger_log_captures_mtime_sequence` |

Run: `python -m pytest tests/scripts/test_cross_harness_bridge_trigger.py -v`.

## Acceptance Criteria

- IP-1 diagnostic landed; logs visible in `.gtkb-state/bridge-poller/trigger.log`.
- IP-2 freshness fix landed; 6 tests PASS.
- No regression in existing cross-harness trigger tests.
- Both preflights PASS.

## Risks / Rollback

- Risk: mtime-stabilization poll-loop adds latency to every Stop event. Mitigation: 200ms cap; conditional on Write-within-1s.
- Risk: diagnostic log grows unbounded. Mitigation: rotation via `.jsonl` extension and a sibling cleanup script (out of scope for this WI).
- Rollback: revert IP-2 freshness changes; keep IP-1 diagnostic (independent value).

## Recommended Commit Type

`fix` - addresses a known reliability defect. ~80 LOC (instrumentation + freshness fix + tests).
