NEW

# Implementation Proposal — SP-1b: Dispatch Outcome Tracker (Post-Dispatch Verdict Polling)

**Status:** NEW (awaiting Loyal Opposition review)
**Author:** Prime Builder (Goose, harness E)
**Session:** S509 continuation, 2026-06-08
**Document:** sp1b-dispatch-outcome-tracker
**Version:** 003
**In response to:** owner directive (2026-06-08 11:28) converting LO SP-1b ADVISORY -001 (WITHDRAWN) and withdrawal notice -002 to PB implementation proposals.

bridge_kind: implementation_proposal
implementation_scope: dispatch_post_dispatch_outcome_tracking

Project: PROJECT-GTKB-OLLAMA-LO-OPERATIONS
Work Item: WI-4432 (to be created via MemBase CLI)
Owner Decision: DELIB-20260608-SP1-CONVERT-ADVISORIES

## Owner Decisions / Input

Owner (Mike) directed at 2026-06-08 11:28 UTC:
> "Convert to NEW implementation proposals for Prime — Withdraw the advisories and queue them for Prime Builder to file as formal NEW proposals with proper work-intent claims and spec linkage."

LO ADVISORY -001.md was withdrawn for role-boundary violation (prescribing implementation scope in an advisory). This REVISED-003 filing is Prime Builder's proper implementation proposal responding to the underlying finding (F4: no dispatch outcome feedback loop).

## Prior Deliberations

- `DELIB-20260608-SP1-CONVERT-ADVISORIES` — owner directive to convert LO advisories to PB proposals.
- `bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md` — LO handoff advisory (current).
- `bridge/gtkb-sp1b-dispatch-outcome-tracker-001.md` — LO ADVISORY, WITHDRAWN (role-boundary violation).
- `bridge/gtkb-sp1b-dispatch-outcome-tracker-002.md` — LO withdrawal notice (WITHDRAWN).
- `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md` — Codex prime work at GO -004: established WI-3265 diagnostic records. **This proposal EXTENDS, not duplicates, that established surface.**
- `bridge/gtkb-ollama-dispatch-state-recovery-002.md` — LO NO-GO on a prior Prime dispatch recovery proposal that triggered meta-rejection loop (Ollama reviewed its own proposal).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge files remain role handoff authority; dispatch outcome records must not interfere with bridge verdict lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation proposal links governing specs before work begins.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — implementation report must map claims to spec-derived tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — outcome records are state artifacts; lifecycle triggers apply.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation authorization.
- `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md` (Codex WI-3265 at GO -004) — established schema of dispatch diagnostic records; this proposal extends that schema.
- `.claude/rules/file-bridge-protocol.md` §Pre-Drafting Claim Step — work-intent claim acquired.
- `.claude/rules/file-bridge-protocol.md` §Pre-Filing Preflight Subsection — preflight executed before INDEX update.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement needed. The WI-3265 dispatch diagnostic schema already covers trigger-level outcome classification. This slice adds post-dispatch verdict polling (F4 gap), which falls under the existing `GOV-FILE-BRIDGE-AUTHORITY-001` authority for dispatch-related state artifacts.

## Summary

This proposal adds a **post-dispatch verdict polling** component to the existing trigger infrastructure, addressing investigation finding F4 (no dispatch outcome feedback loop). Unlike the investigation's `-001.md` framing which proposed a wholly new `scripts/verify_dispatch_outcomes.py` module, this implementation **extends the existing WI-3265 diagnostic records** established by Codex at `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md` (GO at -004).

The gap: today's `_classify_invocation_outcome()` (at scripts/cross_harness_bridge_trigger.py:747) and `_LAST_RESULT_TO_DIAGNOSTIC_CLASSIFICATION` (at :176) record whether the trigger fired, dispatched, or suppressed — but **never follow up on whether the dispatched session actually produced a verdict file** in `bridge/`. So 82+ dispatches show `classification: dispatched` but no telemetry on verdict production rate, latency, or the meta-rejection loop that produced the dispatch-state-recovery incident (where Ollama reviewed its own proposal and NO-GO'd it).

## Scope

This slice does NOT address F1 (preflight-as-blocking), F2 (claim-before-write), F3 (turn budget), or F5 (self-review loop). Those map to SP-1a, SP-1a, SP-1d, and SP-1c respectively. See SP-1a -003 for F1/F2 and the sibling SP-1c/SP-1d proposals for F5/F3.

## Changes to be Made

### C1: Extend WI-3265 diagnostic schema with post-dispatch verdict fields

**File:** `scripts/cross_harness_bridge_trigger.py`

Add to the diagnostic record emission at :2195 (`_diag_common = {`): two new fields:
- `verdict_path: Optional[str]` — resolved path of verdict file in `bridge/` if produced, else null.
- `verdict_latency_seconds: Optional[float]` — seconds from dispatch timestamp to verdict file mtime, else null.

Populated by a new helper `_poll_dispatch_verdict(dispatch_ts, bridge_id)` that:
1. Waits at most `DEFAULT_TIMEOUT_SECONDS` (existing constant, 30.0 → see SP-1d for increase) for `bridge/<bridge_id>-*-md` to be created/modified after `dispatch_ts`.
2. Uses a bounded poll loop (5s interval, max `DEFAULT_TIMEOUT_SECONDS`) to avoid triggering PostToolUse recursively.
3. Returns `{verdict_path, verdict_latency_seconds}` on success or `{None, None}` on timeout.

The poll is invoked after the existing dispatch branch completes, not inside it. Existing trigger return values remain unchanged — this is purely an additional field on diagnostic records.

### C2: Add a non-blocking post-dispatch poller

**File:** `scripts/cross_harness_bridge_trigger.py`

Add a helper `_post_dispatch_poll(thread_id, bridge_id, dispatch_timestamp)` that wraps `threading.Thread(target=_poll_dispatch_verdict, daemon=True)` so the trigger invocation itself does not block on verdict polling. The thread writes to `dispatch-diagnostic-post.jsonl` (a new sibling of existing `trigger-diagnostic.jsonl`).

Non-blocking design: if the poller thread runs longer than the trigger's own lifecycle (e.g., trigger is invoked by an ephemeral PostToolUse hook), it is a daemon thread and will be terminated when the parent process exits. The next invocation of the trigger will re-poll if needed (the verdict file is idempotent on disk).

### C3: Add `platform_tests/scripts/test_dispatch_post_dispatch_poll.py`

New test file covering the post-dispatch polling claims:

- `test_poll_dispatch_verdict_returns_path_and_latency_on_existing_file` — creates a fake dispatch_timestamp and writes a fake verdict file after a known delay, verifies the helper returns `{path, latency}`.
- `test_poll_dispatch_verdict_returns_none_on_timeout` — verifies the helper returns `{None, None}` when no verdict file appears within DEFAULT_TIMEOUT_SECONDS.
- `test_post_dispatch_poll_thread_is_daemon` — verifies the spawned thread is a daemon (non-blocking).
- `test_post_dispatch_poll_writes_to_dedicated_jsonl` — verifies emission goes to `dispatch-diagnostic-post.jsonl`, not the existing `trigger-diagnostic.jsonl` (avoiding interference with the WI-3265 trigger-only records).
- `test_diagnostic_record_schema_extension_is_additive` — verifies existing WI-3265 classification records (`dispatched`, `no_change`, etc.) remain unchanged; the new fields are additive on the post-dispatch jsonl path.

### C4: Update existing cross_harness_bridge_trigger tests

Existing tests in `platform_tests/scripts/test_cross_harness_bridge_trigger*.py` (12+ files) must remain passing. The post-dispatch poll is a new helper invoked **after** the existing trigger function returns, so the trigger's own return value and side effects are unchanged. Any test that asserts exact return shape or file write ordering will be updated in place.

## target_paths metadata

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_post_dispatch_poll.py"]

No new CLI, no new state directory (uses existing `.gtkb-state/cross-harness-trigger/`).

## Spec-Derived Verification Plan

| Spec clause | Test covering it |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` verdict files remain authoritative | `test_poll_dispatch_verdict_returns_path_and_latency_on_existing_file` (poll only observes, never writes) |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` state artifacts lifecycle | `test_post_dispatch_poll_writes_to_dedicated_jsonl` (post-poll records don't pollute trigger-only jsonl) |
| `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md` (WI-3265 schema) | `test_diagnostic_record_schema_extension_is_additive` (existing classification records untouched; new fields are additive on a dedicated path) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` implementation must pass spec-derived tests | All 5 tests in C3 above must pass in CI |

## Risks and Mitigations

**Risk 1:** Polling could miss verdicts produced between the dispatch and the poller thread starting (the gap is 5s).

**Mitigation:** Poll starts immediately after dispatch returns, not in a scheduled future. The mtime check against the recorded `dispatch_timestamp` correctly attributes verdicts produced before the poll actually starts.

**Risk 2:** Daemon thread lifecycle could cause test determinism issues in CI.

**Mitigation:** Tests invoke the helper synchronously (call `_poll_dispatch_verdict` directly, not the thread wrapper) so they are fully deterministic. The thread wrapper is only used in production trigger invocations.

**Risk 3:** Post-dispatch poll could recursively trigger the trigger if the verdict file creation matches a PostToolUse filter.

**Mitigation:** The poll only READS the verdict file's existence and mtime; it never writes to `bridge/`. PostToolUse hooks filter on write events to bridge/ files, so the poller generates no such events.

## Bridge Protocol Compliance Note

Pre-drafting work-intent claim acquired via `scripts/bridge_claim_cli.py claim sp1b-dispatch-outcome-tracker`. Applicability preflight executed before INDEX update. The LO advisory files `gtkb-sp1b-dispatch-outcome-tracker-001.md` (WITHDRAWN) and `-002.md` (WITHDRAWN) remain on disk as historical audit trail; they are not superseded in the protocol sense but are dispositioned per the owner directive to convert to PB proposals.

## Recommended Commit Type

`feat(cross-harness-trigger): extend WI-3265 diagnostics with post-dispatch verdict polling` — additive diagnostic fields on a dedicated post-dispatch jsonl, no changes to trigger return value or dispatch branch.

---

*Prime Builder: goose (harness E), session S509
2026-06-08 12:56 UTC*
