REVISED

# Implementation Proposal - Cross-Harness Trigger INDEX Edit Race + Quiesce Window (WI-3280)

bridge_kind: implementation_proposal
Document: gtkb-cross-harness-trigger-index-edit-race-quiesce
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3280

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_quiesce.py"]

This REVISED proposal (`-005`) addresses the `-004` NO-GO on the WI-3280 quiesce-window work. It adds a quiesce window to the cross-harness trigger to prevent the INDEX edit race observed in S341+S342+S350: Prime writes a bridge document, the trigger fires on the Write, Codex updates INDEX before Prime's Edit lands, Prime's Edit fails with "File has been modified since read".

## Revision Notes

The `-004` NO-GO raised one finding (F1, P1). The `-002` round-1 findings (F1 test-lane, F2 quiesce semantics) were already resolved in `-003` and are carried forward unchanged here. The `-004` finding and its resolution:

- **`-004` F1 (P1 governance drift) - session scoping does not use hook payload evidence.** Addressed. The `-003`/`-004` text claimed the quiesce key was "derived from the hook payload" but then defined the `session_id` component as the value of the `GTKB_BRIDGE_POLLER_RUN_ID` environment variable. Codex correctly observed that (a) the live trigger has no `sys.stdin` / hook-payload JSON read path, (b) `GTKB_BRIDGE_POLLER_RUN_ID` is set by the trigger itself on the *child* auto-dispatch environment inside `_spawn_harness` (not derived from the current PostToolUse hook payload), so in a normal owner-session PostToolUse invocation it is absent and the session component collapses to an empty string. `-005` corrects this:
  - IP-1 step 2a (new) specifies that `main()` reads the real hook-event payload from `sys.stdin` once at entry, parses it as JSON, and extracts the documented `session_id` and `hook_event_name` fields. That hook context is passed into `run_trigger` as a new `hook_context` keyword argument.
  - IP-1 step 3 is rewritten: the `session_id` quiesce-key component now comes from the parsed stdin payload's `session_id` field. `GTKB_BRIDGE_POLLER_RUN_ID` is demoted to an explicit **fallback-only** discriminator, used only when stdin carries no payload (manual invocation, or a harness that does not deliver a stdin payload). The proposal now states plainly that `GTKB_BRIDGE_POLLER_RUN_ID` is fallback-only and is NOT the primary PostToolUse session discriminator.
  - IP-1 step 2b (new) specifies the stdin read is fail-soft: a missing/empty/unparseable stdin payload yields an empty hook context and the trigger proceeds (this preserves the fire-and-forget contract and the existing `--stop-hook` / `--diagnose` / manual paths). The stdin read happens before `run_trigger` and never blocks: `main()` reads stdin only when it is not a TTY, so an interactive manual invocation does not hang.
  - IP-2 adds three new stdin-payload tests (`test_session_id_from_stdin_hook_payload`, `test_session_id_fallback_when_no_stdin_payload`, `test_stop_path_reads_stdin_hook_context`) and tightens `test_quiesce_record_isolated_per_role_and_session` so it FAILS if `session_id` is sourced only from a mocked environment variable while a stdin payload carries a different `session_id`.

All other `-003` constraints are carried forward unchanged and remain in scope: PostToolUse-only quiesce; `--stop-hook` and `manual` bypass quiesce; quiesce suppression never writes `last_dispatched_signature` (a separate retryable `pending_quiesce_marker` is used); NEW->GO reciprocal dispatch is never suppressed by a fresh quiesce record; tests and `target_paths` stay in the `platform_tests/scripts/` lane.

No scope change beyond the `-004` F1 correction: the change remains a single-function-scope quiesce window plus a small fail-soft stdin-payload read at the `main()` entry of `scripts/cross_harness_bridge_trigger.py`, plus its regression tests. `target_paths` is unchanged.

## Claim

Add a configurable quiesce window (default 5 seconds) between PostToolUse trigger detection and counterpart-harness spawn. During the window, the trigger coalesces additional INDEX changes originating from the same hook session and same PostToolUse burst; this gives Prime time to complete its bridge proposal + INDEX update sequence atomically. The quiesce window applies ONLY to PostToolUse invocations. `--stop-hook` reconciliation always bypasses quiesce so the Stop safety net is never delayed or suppressed. The dispatch-on-actionable-change semantic is preserved: quiesce only delays a dispatch within the window; it never drops a dispatch. The "same originating session" guard is derived from the real hook-event payload read from `sys.stdin`, not from an environment variable.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness trigger is the active bridge-dispatch substrate; the quiesce window is added to that substrate, and the hook-payload stdin read is parity-compatible with both the Claude Code and Codex Stop/PostToolUse hook contracts.
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

No prior deliberation rejected a PostToolUse quiesce window; this is the first proposal to add one. No prior deliberation rejected reading the hook-event payload from stdin in the cross-harness trigger.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

- 2026-05-14 UTC, S350+: owner approved the `GTKB-BRIDGE-PROTOCOL-RELIABILITY` project authorization including WI-3280, captured as the AskUserQuestion decision archived in `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` (formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`). Implementation proceeds autonomously through the bridge protocol under that project authorization; no new per-fix owner decision is required.

## Requirement Sufficiency

Existing requirements sufficient. WI-3280's description specifies the INDEX edit race and the quiesce-window remediation. No new or revised requirement or specification is created by this work; it implements an already-tracked work item against existing bridge-protocol specifications.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-defect source-and-test change. It is not a bulk backlog operation: it performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe the single work item WI-3280 and its governed filing path only. The applicable evidence pattern is a single-WI reliability-fix implementation proposal with formal-artifact-approval discipline preserved unchanged; the review-packet inventory is IP-1 + IP-2 in this single thread.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-005` REVISED line is inserted at the top of the `gtkb-cross-harness-trigger-index-edit-race-quiesce` document block in `bridge/INDEX.md`; no INDEX entry is removed or rewritten. The implementation does not change how `bridge/INDEX.md` records workflow state.

## Proposed Scope

### IP-1: Quiesce window in cross-harness trigger (PostToolUse only)

In `scripts/cross_harness_bridge_trigger.py`:

1. Add a `QUIESCE_WINDOW_SECONDS = 5` module constant, overridable via the environment variable `GTKB_TRIGGER_QUIESCE_SECONDS`.
2. **Read the real hook-event payload from stdin at `main()` entry.**
   - **2a. Stdin payload read.** `main()` reads the hook-event payload from `sys.stdin` once, before invoking `run_trigger`. Claude Code and Codex deliver the PostToolUse / Stop hook payload as a single JSON object on the hook process's stdin (the same contract `.claude/hooks/owner-decision-tracker.py` consumes via `sys.stdin.read()` then `json.loads`). `main()` parses that JSON and extracts the documented fields `session_id` (string) and `hook_event_name` (string). The parsed result is assembled into a small `hook_context` dict (`{"session_id": ..., "hook_event_name": ...}`) and passed into `run_trigger` as a new keyword argument `hook_context: dict[str, str] | None`.
   - **2b. Fail-soft stdin read.** The stdin read is fail-soft. `main()` reads stdin only when `sys.stdin` is not a TTY (`sys.stdin.isatty()` is `False`), so an interactive manual invocation never blocks waiting for input. A missing payload, an empty payload, or a non-JSON payload yields `hook_context = None` (or a dict with empty string values); `run_trigger` then proceeds normally using the fallback discriminator in step 3. This preserves the existing fire-and-forget contract and the `--diagnose` / `--stop-hook` / manual code paths. The read is wrapped so any exception is swallowed and the trigger continues.
   - **2c. `run_trigger` signature.** `run_trigger` gains the keyword-only parameter `hook_context: dict[str, str] | None = None`. The parameter defaults to `None` so existing direct/programmatic callers (and existing tests that call `run_trigger` without it) are unaffected. `run_trigger` uses `hook_context` only to build the quiesce key (step 3) and to populate the diagnostic `session_id` field.
3. **Quiesce key.** The quiesce record is keyed by a tuple, not a global timestamp. Each component is sourced as follows:
   - `session_id` - the **primary** source is `hook_context["session_id"]` from the parsed stdin hook payload (step 2a). When `hook_context` is `None` or carries an empty `session_id` (manual invocation, or a harness that does not deliver a stdin payload), the trigger uses the **fallback-only** value `os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID", "")`. `GTKB_BRIDGE_POLLER_RUN_ID` is explicitly fallback-only: it is set by the trigger itself on the *child* auto-dispatch environment inside `_spawn_harness`, so it is meaningful for the child re-entry case but is NOT the primary discriminator for an owner-session PostToolUse invocation. The proposal does not rely on `GTKB_BRIDGE_POLLER_RUN_ID` being present in a normal owner PostToolUse hook environment.
   - `hook_event_name` - the **primary** source is `hook_context["hook_event_name"]` from the parsed stdin payload. When absent, the trigger uses the `invocation_source` value (`"PostToolUse"`) as the fallback, so the component is always populated.
   - originating harness / role - the active harness ID and durable role label resolved from `harness-state/role-assignments.json` via the existing role-resolution path. This scopes the quiesce record per originating harness so a Prime-side PostToolUse burst does not quiesce a Codex-side burst (and vice versa).
   The composite quiesce key is `f"{hook_event_name}:{session_id}:{harness_id}:{role_label}"`.
4. **Quiesce state.** A new state file `.gtkb-state/bridge-poller/quiesce-state.json` stores, per quiesce key: `last_postooluse_seen_at`, `quiesce_until` (`= last_postooluse_seen_at + QUIESCE_WINDOW_SECONDS`), and `pending_quiesce_marker` (the actionable signature observed while quiesced, retryable; see step 6). The file is written with the existing atomic write-temp-then-rename helper. State is keyed by the composite quiesce key, so separate sessions / separate harnesses / separate roles have independent quiesce records.
5. **Quiesce decision (PostToolUse only).** `run_trigger` already receives `invocation_source` (`"PostToolUse"` / `"Stop"` / `"manual"`); `main()` passes `"Stop"` under `--stop-hook` and `"PostToolUse"` otherwise. The quiesce check is gated on `invocation_source == "PostToolUse"`. When `invocation_source` is `"Stop"` (`--stop-hook` reconciliation) or `"manual"`, the quiesce check is skipped entirely and dispatch proceeds with the existing signature-dedup behavior. On a PostToolUse invocation, before computing the per-recipient dispatch decision:
   - Read `quiesce-state.json` and look up the record for the current composite quiesce key.
   - If a record exists and `now < quiesce_until`: this PostToolUse invocation is **inside the quiesce window**. The trigger does NOT spawn a counterpart. It refreshes the record (`last_postooluse_seen_at = now`, `quiesce_until = now + QUIESCE_WINDOW_SECONDS`) so a rapid edit burst keeps extending the window, and it records the currently-observed actionable signature in `pending_quiesce_marker`. The trigger then returns a summary with `skipped: True, reason: "quiesce_window_active"`.
   - If no record exists, or `now >= quiesce_until`: this PostToolUse invocation is **outside the quiesce window**. The trigger proceeds to the normal dispatch decision. After the decision, it writes a fresh quiesce record (`last_postooluse_seen_at = now`, `quiesce_until = now + QUIESCE_WINDOW_SECONDS`, `pending_quiesce_marker = null`).
6. **`last_dispatched_signature` is left unchanged on quiesce suppression.** Quiesce suppression NEVER writes `last_dispatched_signature`. The dedup field `last_dispatched_signature` (and the legacy `signature` field) in `dispatch-state.json` is updated ONLY when a real dispatch occurs, exactly as today. The actionable signature observed while quiesced is recorded in the separate `pending_quiesce_marker` field of `quiesce-state.json` instead. Because `last_dispatched_signature` is untouched, when the next invocation lands past `quiesce_until` (PostToolUse, or a `--stop-hook` reconciliation, or a `manual` run) the normal signature-change detection still sees the change as undispatched and dispatches it. This preserves the dispatch-on-actionable-change semantic of `DCL-SMART-POLLER-AUTO-TRIGGER-001`: a coalesced burst is dispatched exactly once, after the session quiesces, by whichever invocation first lands past `quiesce_until`.
7. **Stop reconciliation interaction.** Because Stop bypasses the quiesce check (step 5), a `--stop-hook` reconciliation that lands while a PostToolUse quiesce record is still fresh proceeds straight to the normal dispatch decision. With `last_dispatched_signature` unchanged by suppression, the Stop reconciliation dispatches any still-undispatched actionable change. This is the intended fail-soft behavior: the Stop hook is the safety net that catches a burst whose final PostToolUse fell inside the window and never re-fired.
8. **Diagnostic instrumentation.** The WI-3265 diagnostic record's `session_id` field is updated to record `hook_context["session_id"]` when available (falling back to `os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID", "")` only when absent), so the diagnostic stream reflects the same session discriminator the quiesce key uses. This is an observational change only; it does not influence dispatch.

### IP-2: Tests (platform_tests lane)

Tests are added or modified under `platform_tests/scripts/`:

- The existing `platform_tests/scripts/test_cross_harness_bridge_trigger.py` is extended only as needed to keep prior assertions passing against the new code path (the new `hook_context` parameter defaults to `None`, so existing `run_trigger` callers in that file remain valid).
- A focused companion file `platform_tests/scripts/test_cross_harness_bridge_trigger_quiesce.py` holds the new quiesce-specific tests, including the new stdin-payload tests.

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
| The quiesce-key `session_id` component is taken from the parsed stdin hook payload's `session_id` field (PostToolUse path) | `test_session_id_from_stdin_hook_payload` | `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, IP-1 steps 2a/3 |
| When stdin carries no payload, the quiesce-key `session_id` falls back to `GTKB_BRIDGE_POLLER_RUN_ID`; the test asserts the fallback is used ONLY in the no-stdin-payload case | `test_session_id_fallback_when_no_stdin_payload` | `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, IP-1 steps 2b/3 |
| The Stop path also parses the stdin hook payload and records its `session_id`/`hook_event_name` in the diagnostic context | `test_stop_path_reads_stdin_hook_context` | `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, IP-1 steps 2a/8 |
| Per-role / per-session separation: a PostToolUse burst keyed to one session/harness/role does not quiesce a burst keyed to a different session/harness/role. The test supplies DIFFERING `session_id` values via stdin payloads (not env vars); it fails if `session_id` is sourced only from a mocked `GTKB_BRIDGE_POLLER_RUN_ID` while the stdin payload carries a different `session_id` | `test_quiesce_record_isolated_per_role_and_session` | `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, IP-1 step 3 |
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

- `scripts/cross_harness_bridge_trigger.py` - add the `QUIESCE_WINDOW_SECONDS` constant; add the fail-soft stdin hook-payload read in `main()`; add the `hook_context` keyword parameter to `run_trigger`; add the composite-quiesce-key derivation (stdin-payload-primary, `GTKB_BRIDGE_POLLER_RUN_ID`-fallback); add the `quiesce-state.json` read/write; add the PostToolUse-only quiesce gate inside `run_trigger`; update the diagnostic `session_id` source.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` - extend only as needed to keep existing assertions passing against the new code path.
- `platform_tests/scripts/test_cross_harness_bridge_trigger_quiesce.py` - new focused companion test file holding the 12 quiesce-specific tests in the verification plan (9 from `-003` plus the 3 new stdin-payload tests).

## Acceptance Criteria

- IP-1 and IP-2 landed; all tests in the verification plan PASS via the platform test lane.
- Both bridge preflights PASS on `-005`.
- The quiesce-key `session_id` component is sourced from the real stdin hook payload's `session_id` field on the PostToolUse path; `GTKB_BRIDGE_POLLER_RUN_ID` is used ONLY as a fallback when stdin carries no payload, and `test_quiesce_record_isolated_per_role_and_session` fails if the env var is used while a stdin payload carries a different `session_id`.
- The stdin read is fail-soft and never blocks: a missing/empty/non-JSON payload yields an empty hook context, and an interactive manual invocation (TTY stdin) does not hang.
- Quiesce applies only to PostToolUse; `--stop-hook` reconciliation and `manual` runs bypass quiesce.
- `last_dispatched_signature` is never written by quiesce suppression; the dispatch-on-actionable-change semantic is preserved (a coalesced burst dispatches exactly once after the session quiesces).
- The NEW->GO reciprocal dispatch and the Stop safety net are demonstrably never suppressed by a fresh quiesce record.
- `ruff check` is clean on the changed source file.

## Risks / Rollback

- Risk: a 5-second quiesce adds latency to PostToolUse dispatch. Mitigation: 5 s is sub-perception relative to Codex's review latency; the Stop hook still dispatches without delay; the window is env-overridable.
- Risk: the stdin read could block a manual invocation that has no piped input. Mitigation: IP-1 step 2b - `main()` reads stdin only when `sys.stdin.isatty()` is `False`; the read is also exception-swallowed, so a closed/empty pipe yields an empty hook context and the trigger proceeds.
- Risk: a harness PostToolUse invocation may not deliver a stdin payload, leaving `session_id` empty. Mitigation: IP-1 step 3 - the fallback discriminator (`GTKB_BRIDGE_POLLER_RUN_ID`) and the always-populated harness/role components keep the quiesce key well-formed; an empty `session_id` only collapses the per-session granularity, never the per-harness/per-role granularity, and the Stop safety net still dispatches.
- Risk: `quiesce-state.json` race between multiple Prime sessions. Mitigation: atomic write-temp-then-rename; the composite quiesce key is per-session / per-harness / per-role, so concurrent sessions have independent records.
- Risk: a quiesce record could mask a dispatch if `last_dispatched_signature` were updated on suppression. Mitigation: IP-1 step 6 - suppression never writes `last_dispatched_signature`; the separate `pending_quiesce_marker` is retryable and the next invocation past `quiesce_until` dispatches the change.
- Rollback: revert the quiesce additions and the stdin-payload read in `scripts/cross_harness_bridge_trigger.py` and delete `quiesce-state.json`; the trigger reverts to immediate PostToolUse dispatch.

## Recommended Commit Type

`feat:` - reliability enhancement adding a new quiesce-window capability surface and a hook-payload stdin read to the cross-harness trigger; net-new behavior plus tests.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-005` content after the `bridge/INDEX.md` `REVISED` entry was added; outputs are embedded in the `## Applicability Preflight` and `## Clause Applicability` sections below.

## Review Questions for Loyal Opposition

1. Is reading the hook-event payload from `sys.stdin` in `main()` (the same contract `.claude/hooks/owner-decision-tracker.py` uses) the right mechanism to obtain the real `session_id`, given the trigger is registered as a PostToolUse + Stop hook in `.claude/settings.json` and `.codex/hooks.json`?
2. Is the stdin TTY-guard + exception-swallow the right fail-soft posture, or should manual invocation be detected another way?
3. Is the composite quiesce key (`hook_event_name:session_id:harness_id:role_label`) the right scoping granularity?

## Applicability Preflight

- packet_hash: `sha256:9ae1feab337a063176ccc0d78b926ff5af922f229b14d38a496903052901d102`
- bridge_document_name: `gtkb-cross-harness-trigger-index-edit-race-quiesce`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-005.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-cross-harness-trigger-index-edit-race-quiesce`
- Operative file: `bridge\gtkb-cross-harness-trigger-index-edit-race-quiesce-005.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Clause preflight exit code: 0 (pass; zero blocking gaps).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
