REVISED

# Implementation Proposal - Cross-Harness Trigger INDEX Edit Race + Quiesce Window (WI-3280)

bridge_kind: prime_proposal
Document: gtkb-cross-harness-trigger-index-edit-race-quiesce
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3280

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_quiesce.py"]

This REVISED proposal (`-003`) addresses the `-002` NO-GO on the WI-3280 quiesce-window work. It adds a quiesce window to the cross-harness trigger to prevent the INDEX edit race observed in S341+S342+S350: Prime writes a bridge document, the trigger fires on the Write, Codex updates INDEX before Prime's Edit lands, Prime's Edit fails with "File has been modified since read".

## Revision Notes

The `-002` NO-GO raised two findings. Both are addressed in `-003`:

- **F1 (P1 governance drift) - test path outside the active platform test lane.** Addressed. `target_paths` and the verification command are repointed from `tests/scripts/` to `platform_tests/scripts/`. The proposal now modifies the existing `platform_tests/scripts/test_cross_harness_bridge_trigger.py` and adds a focused companion file `platform_tests/scripts/test_cross_harness_bridge_trigger_quiesce.py`. `pyproject.toml` `testpaths` is `platform_tests` and `applications/Agent_Red/tests`, and `.github/workflows/groundtruth-kb-tests.yml` runs `python -m pytest platform_tests/ -q --tb=short`, so the new tests are exercised by the platform pytest lane and CI.
- **F2 (P1 governance drift) - quiesce semantics under-specified for Stop and reciprocal dispatch.** Addressed. The `## Proposed Scope` section below now fully specifies the quiesce key (derived from the hook payload: `session_id`, `hook_event_name`, originating harness/role), constrains quiesce to PostToolUse bursts only, states that `--stop-hook` reconciliation bypasses quiesce, and states that `last_dispatched_signature` is left unchanged on quiesce suppression (a separate retryable quiesce marker is used). New tests pin Stop reconciliation with a fresh quiesce record, the NEW->GO reciprocal-dispatch case, and per-role / per-session separation.

No scope change beyond the F1/F2 corrections: the change remains a single-function-scope quiesce window in `scripts/cross_harness_bridge_trigger.py` plus its regression tests.

## Claim

Add a configurable quiesce window (default 5 seconds) between PostToolUse trigger detection and counterpart-harness spawn. During the window, the trigger coalesces additional INDEX changes originating from the same session and same PostToolUse burst; this gives Prime time to complete its bridge proposal + INDEX update sequence atomically. The quiesce window applies ONLY to PostToolUse invocations. `--stop-hook` reconciliation always bypasses quiesce so the Stop safety net is never delayed or suppressed. The dispatch-on-actionable-change semantic is preserved: quiesce only delays a dispatch within the window; it never drops a dispatch.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness trigger is the active bridge-dispatch substrate; the quiesce window is added to that substrate.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; `bridge/INDEX.md` remains canonical workflow state.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` - dispatch-on-actionable-change semantic (preserved; quiesce only delays a dispatch within the window, never drops one).
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic policy engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root-only placement.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the verification plan below maps every linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - WI-3280 is a tracked standing-backlog work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, and linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the observed race triggered a work item which triggers this implementation proposal and its tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this fix is captured as governed work (WI-3280) with a bridge artifact and spec-derived tests.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - records the owner decision authorizing the project grouping `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` that includes WI-3280.
- `DELIB-1877` - records the related `gtkb-cross-harness-trigger-windows-rename-race-001` thread (latest status VERIFIED); the prior verified behavior includes signature-based loop prevention which the quiesce window must preserve.
- `DELIB-1497` / `DELIB-1498` / `DELIB-1499` - preserve the prior cross-harness-trigger rename/liveness review history (signature-based loop prevention, reciprocal dispatch, Stop reconciliation). The quiesce proposal preserves all of those contracts; quiesce applies only to PostToolUse, never to Stop reconciliation.

No prior deliberation rejected a PostToolUse quiesce window; this is the first proposal to add one.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

- 2026-05-14 UTC, S350+: owner approved the `GTKB-BRIDGE-PROTOCOL-RELIABILITY` project authorization including WI-3280, captured as the AskUserQuestion decision archived in `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` (formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`). Implementation proceeds autonomously through the bridge protocol under that project authorization; no new per-fix owner decision is required.

## Requirement Sufficiency

Existing requirements sufficient. WI-3280's description specifies the INDEX edit race and the quiesce-window remediation. No new or revised requirement or specification is created by this work; it implements an already-tracked work item against existing bridge-protocol specifications.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-defect source-and-test change. It is not a bulk backlog operation: it performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe the single work item WI-3280 and its governed filing path only. The applicable evidence pattern is a single-WI reliability-fix implementation proposal with formal-artifact-approval discipline preserved unchanged; the review-packet inventory is IP-1 + IP-2 in this single thread.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-003` REVISED line is inserted at the top of the `gtkb-cross-harness-trigger-index-edit-race-quiesce` document block in `bridge/INDEX.md`; no INDEX entry is removed or rewritten. The implementation does not change how `bridge/INDEX.md` records workflow state.

## Proposed Scope

### IP-1: Quiesce window in cross-harness trigger (PostToolUse only)

In `scripts/cross_harness_bridge_trigger.py`:

1. Add a `QUIESCE_WINDOW_SECONDS = 5` module constant, overridable via the environment variable `GTKB_TRIGGER_QUIESCE_SECONDS`.
2. **Quiesce applies to PostToolUse invocations only.** `run_trigger` already receives `invocation_source` (`"PostToolUse"` / `"Stop"` / `"manual"`); `main()` passes `"Stop"` under `--stop-hook` and `"PostToolUse"` otherwise. The quiesce check is gated on `invocation_source == "PostToolUse"`. When `invocation_source` is `"Stop"` (i.e., `--stop-hook` reconciliation) or `"manual"`, the quiesce check is skipped entirely and dispatch proceeds with the existing signature-dedup behavior. This guarantees the Stop reconciliation safety net is never delayed or suppressed by a fresh quiesce record.
3. **Quiesce key.** The quiesce record is keyed by a tuple derived from the hook payload, not a global timestamp:
   - `session_id` - read from the `GTKB_BRIDGE_POLLER_RUN_ID` environment variable (the existing session discriminator that `run_trigger` already records into the diagnostic instrumentation at the `session_id` field); empty string when absent.
   - `hook_event_name` - the `invocation_source` value (`"PostToolUse"`).
   - originating harness / role - the active harness ID and durable role label resolved from `harness-state/role-assignments.json` via the existing role-resolution path. This scopes the quiesce record per originating harness so a Prime-side PostToolUse burst does not quiesce a Codex-side burst (and vice versa).
   The composite quiesce key is `f"{hook_event_name}:{session_id}:{harness_id}:{role_label}"`.
4. **Quiesce state.** A new state file `.gtkb-state/bridge-poller/quiesce-state.json` stores, per quiesce key: `last_postooluse_seen_at`, `quiesce_until` (`= last_postooluse_seen_at + QUIESCE_WINDOW_SECONDS`), and `pending_quiesce_marker` (the actionable signature observed while quiesced, retryable; see step 6). The file is written with the existing atomic write-temp-then-rename helper. State is keyed by the composite quiesce key, so separate sessions / separate harnesses / separate roles have independent quiesce records.
5. **Quiesce decision (PostToolUse only).** On a PostToolUse invocation, before computing the per-recipient dispatch decision:
   - Read `quiesce-state.json` and look up the record for the current composite quiesce key.
   - If a record exists and `now < quiesce_until`: this PostToolUse invocation is **inside the quiesce window**. The trigger does NOT spawn a counterpart. It refreshes the record (`last_postooluse_seen_at = now`, `quiesce_until = now + QUIESCE_WINDOW_SECONDS`) so a rapid edit burst keeps extending the window, and it records the currently-observed actionable signature in `pending_quiesce_marker`. The trigger then returns a summary with `skipped: True, reason: "quiesce_window_active"`.
   - If no record exists, or `now >= quiesce_until`: this PostToolUse invocation is **outside the quiesce window**. The trigger proceeds to the normal dispatch decision. After the decision, it writes a fresh quiesce record (`last_postooluse_seen_at = now`, `quiesce_until = now + QUIESCE_WINDOW_SECONDS`, `pending_quiesce_marker = null`).
6. **`last_dispatched_signature` is left unchanged on quiesce suppression.** Quiesce suppression NEVER writes `last_dispatched_signature`. The dedup field `last_dispatched_signature` (and the legacy `signature` field) in `dispatch-state.json` is updated ONLY when a real dispatch occurs, exactly as today. The actionable signature observed while quiesced is recorded in the separate `pending_quiesce_marker` field of `quiesce-state.json` instead. Because `last_dispatched_signature` is untouched, when the next invocation lands past `quiesce_until` (PostToolUse, or a `--stop-hook` reconciliation, or a `manual` run) the normal signature-change detection still sees the change as undispatched and dispatches it. This preserves the dispatch-on-actionable-change semantic of `DCL-SMART-POLLER-AUTO-TRIGGER-001`: a coalesced burst is dispatched exactly once, after the session quiesces, by whichever invocation first lands past `quiesce_until`.
7. **Stop reconciliation interaction.** Because Stop bypasses the quiesce check (step 2), a `--stop-hook` reconciliation that lands while a PostToolUse quiesce record is still fresh proceeds straight to the normal dispatch decision. With `last_dispatched_signature` unchanged by suppression, the Stop reconciliation dispatches any still-undispatched actionable change. This is the intended fail-soft behavior: the Stop hook is the safety net that catches a burst whose final PostToolUse fell inside the window and never re-fired.

### IP-2: Tests (platform_tests lane)

Tests are added or modified under `platform_tests/scripts/`:

- The existing `platform_tests/scripts/test_cross_harness_bridge_trigger.py` is extended only as needed to keep prior assertions passing against the new code path.
- A focused companion file `platform_tests/scripts/test_cross_harness_bridge_trigger_quiesce.py` holds the new quiesce-specific tests.

## Specification-Derived Verification Plan

Each linked specification maps to at least one test. The verification command runs the platform test lane.

| Behavior / Spec coverage | Test | Covers |
|---|---|---|
| Rapid PostToolUse edits inside the window coalesce; only one dispatch occurs after the window | `test_postooluse_edits_coalesce_into_single_dispatch` | `DCL-SMART-POLLER-AUTO-TRIGGER-001`, `GOV-FILE-BRIDGE-AUTHORITY-001` |
| A PostToolUse invocation past `quiesce_until` dispatches the still-undispatched change | `test_dispatch_after_quiesce_expires` | `DCL-SMART-POLLER-AUTO-TRIGGER-001` |
| `GTKB_TRIGGER_QUIESCE_SECONDS` env var overrides the window | `test_env_var_override_quiesce_seconds` | IP-1 step 1 |
| First PostToolUse with no prior quiesce record dispatches immediately (no spurious delay) | `test_first_postooluse_no_quiesce_delay` | `DCL-SMART-POLLER-AUTO-TRIGGER-001` |
| `--stop-hook` reconciliation BYPASSES quiesce: a Stop invocation with a fresh PostToolUse quiesce record still dispatches the undispatched actionable change | `test_stop_hook_bypasses_fresh_quiesce_record` | `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `GOV-FILE-BRIDGE-AUTHORITY-001` |
| NEW->GO reciprocal dispatch: a Codex `GO` written within or after the quiesce window still wakes Prime (quiesce never suppresses the reciprocal dispatch) | `test_new_to_go_reciprocal_dispatch_through_quiesce` | `DCL-SMART-POLLER-AUTO-TRIGGER-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001` |
| Per-role / per-session separation: a PostToolUse burst keyed to one session/harness/role does not quiesce a burst keyed to a different session/harness/role | `test_quiesce_record_isolated_per_role_and_session` | `ADR-CODEX-HOOK-PARITY-FALLBACK-001` |
| Quiesce suppression leaves `last_dispatched_signature` unchanged; the retryable `pending_quiesce_marker` is used instead | `test_quiesce_suppression_preserves_last_dispatched_signature` | `DCL-SMART-POLLER-AUTO-TRIGGER-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| `quiesce-state.json` round-trips correctly via the atomic writer | `test_quiesce_state_file_round_trip` | IP-1 step 4 |
| In-root placement: no target path is outside `E:\GT-KB` | covered by `target_paths` enumeration above | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` |
| Proposal cites all governing specs; this is a tracked WI | covered by `## Specification Links` and the WI-3280 metadata above | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `GOV-STANDING-BACKLOG-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` |

Verification command:

```
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger_quiesce.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py
```

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py` - add the `QUIESCE_WINDOW_SECONDS` constant, the composite-quiesce-key derivation, the `quiesce-state.json` read/write, and the PostToolUse-only quiesce gate inside `run_trigger`.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` - extend only as needed to keep existing assertions passing against the new code path.
- `platform_tests/scripts/test_cross_harness_bridge_trigger_quiesce.py` - new focused companion test file holding the 9 quiesce-specific tests in the verification plan.

## Acceptance Criteria

- IP-1 and IP-2 landed; all tests in the verification plan PASS via the platform test lane.
- Both bridge preflights PASS on `-003`.
- Quiesce applies only to PostToolUse; `--stop-hook` reconciliation and `manual` runs bypass quiesce.
- `last_dispatched_signature` is never written by quiesce suppression; the dispatch-on-actionable-change semantic is preserved (a coalesced burst dispatches exactly once after the session quiesces).
- The NEW->GO reciprocal dispatch and the Stop safety net are demonstrably never suppressed by a fresh quiesce record.
- `ruff check` is clean on the changed source file.

## Risks / Rollback

- Risk: a 5-second quiesce adds latency to PostToolUse dispatch. Mitigation: 5 s is sub-perception relative to Codex's review latency; the Stop hook still dispatches without delay; the window is env-overridable.
- Risk: `quiesce-state.json` race between multiple Prime sessions. Mitigation: atomic write-temp-then-rename; the composite quiesce key is per-session / per-harness / per-role, so concurrent sessions have independent records.
- Risk: a quiesce record could mask a dispatch if `last_dispatched_signature` were updated on suppression. Mitigation: IP-1 step 6 - suppression never writes `last_dispatched_signature`; the separate `pending_quiesce_marker` is retryable and the next invocation past `quiesce_until` dispatches the change.
- Rollback: revert the single-function-scope quiesce additions in `scripts/cross_harness_bridge_trigger.py` and delete `quiesce-state.json`; the trigger reverts to immediate PostToolUse dispatch.

## Recommended Commit Type

`feat:` - reliability enhancement adding a new quiesce-window capability surface to the cross-harness trigger; net-new behavior plus tests.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` content after the `bridge/INDEX.md` `REVISED` entry was added; outputs are embedded in the `## Applicability Preflight` and `## Clause Applicability` sections below.

## Review Questions for Loyal Opposition

1. Is the composite quiesce key (`hook_event_name:session_id:harness_id:role_label`) the right scoping granularity, or should the harness/role component be dropped?
2. Is gating quiesce on `invocation_source == "PostToolUse"` the right mechanism to exempt Stop reconciliation, given `run_trigger` already receives `invocation_source`?
3. Is 5 seconds the right default window?

## Applicability Preflight

- packet_hash: `sha256:fb2d95f6dd9f11b1d265776aeb77e8d61b14280473482fb3a5a2e8f99bb2f803`
- bridge_document_name: `gtkb-cross-harness-trigger-index-edit-race-quiesce`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-003.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-cross-harness-trigger-index-edit-race-quiesce`
- Operative file: `bridge\gtkb-cross-harness-trigger-index-edit-race-quiesce-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Clause preflight exit code: 0 (pass; zero blocking gaps).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
