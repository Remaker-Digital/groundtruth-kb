REVISED

# Dispatch repair: fast-trip the circuit breaker on non-transient worker failures (WI-4703) - REVISED

bridge_kind: implementation_proposal
Document: gtkb-wi4703-dispatch-non-transient-fast-trip
Version: 003 (REVISED; addresses NO-GO at -002)
Responds to: bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-002.md
Recommended commit type: fix:

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6f5bd1b5-1bca-4b08-8e9f-f8e684a62d12
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4703-DISPATCHER-FAST-TRIP-REPAIR
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4703

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_non_transient_fast_trip.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Findings Addressed (from -002 NO-GO)

### FINDING-P1-001: Missing implementation authorization metadata — RESOLVED

A bounded project authorization now exists and is cited in the metadata block above:
- Owner-decision deliberation: `DELIB-S20260620-WI4703-DISPATCH-REPAIR-AUTH` (source_type=owner_conversation, outcome=owner_decision), capturing the owner directive "tackle the dispatch repair and drive it through the bridge protocol to VERIFIED" with a validated formal-artifact approval packet.
- `Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4703-DISPATCHER-FAST-TRIP-REPAIR` — active, scoped to `PROJECT-GTKB-RELIABILITY-FIXES`, includes `WI-4703`, includes spec `GOV-AUTOMATION-VALUE-VS-COST-001`, allowed mutation classes `source` + `test`, forbids `deployment` + `file_deletion`.

This gives Prime Builder a machine-checkable implementation-start authorization path after GO.

### FINDING-P2-002: Predecessor work-item disposition — RESOLVED

WI-4703 is a **prerequisite-safe, independent narrow sub-slice**. It does NOT depend on, supersede, or conflict with WI-4697 or WI-4698:

- **WI-4697** (impl-start gate lacks an emergency-bridge-repair exemption): orthogonal. WI-4703 proceeds through the *normal* governed proposal→GO→impl-start path (this proposal + its PAUTH), so it does not need the emergency exemption WI-4697 tracks.
- **WI-4698** (LO reviewer pool can't do governance-grade reviews → capability-aware routing): orthogonal. WI-4703 changes *breaker sensitivity* (how the dispatcher reacts to a failed worker); it does not change *target selection / routing*, which is WI-4698's domain.

The three are complementary facets of dispatch reliability that compose cleanly and can land in any order. The `depends_on` tags on the WI-4703 backlog row were captured imprecisely as "related siblings"; they are not hard prerequisites. WI-4703 is implementable and verifiable on its own.

## Problem / Diagnosis

The cross-harness bridge dispatch repeatedly spawns headless workers that fail at runtime and keeps re-dispatching them, producing wasteful churn that tripped the prime-builder circuit breaker and rate-limited spawns. Evidence (`.gtkb-state/bridge-poller/dispatch-failures.jsonl` + `dispatch-runs/*`):

- **Prime-B (Claude) HTTP 401**: the spawned headless `claude` worker exits with `{"is_error":true,"api_error_status":401,"result":"Failed to authenticate. API Error: 401 Invalid authentication credentials","num_turns":1}` (stdout log). `failure_count` reached **26** before the breaker tripped.
- **LO-A (Codex)**: worker stderr contains Python `Traceback` and `max-turn exhaustion`; some runs exit `0x40010004` (Windows CTRL_C_EXIT / abrupt termination).
- A trivial 33-line WI-4682 wording correction churned **15 bridge versions over ~6h** because each new version re-armed dispatch and each spawn failed.

Root-cause separation: the **spawn mechanism works** (`launched: true`); the **spawned harness sessions fail at runtime**. A 401 auth failure and a worker crash/exhaustion are **non-transient** — re-spawning the same recipient fails identically until the underlying cause is fixed. The dispatcher's defect: `NON_RETRYABLE_WORKER_FAILURE_CLASSES = frozenset({"harness_unavailable_tier"})` (`scripts/cross_harness_bridge_trigger.py:206`) is too narrow, and the breaker only trips at `failure_count >= DEFAULT_DISPATCH_MAX_RETRIES` (=3, line 185/3203). So auth failures, max-turn exhaustion, and worker crashes are treated as retryable and spend up to 3 expensive spawns each before any brake engages — a direct violation of `GOV-AUTOMATION-VALUE-VS-COST-001`.

Out of scope (separately tracked as `WI-4707`): the headless-Claude 401 credential itself is environmental and needs owner credential diagnosis. This proposal makes the dispatcher fail FAST and recover cleanly regardless.

## Proposed Change

Add a "fast-trip" breaker tier for non-transient worker failures, preserving the existing half-open auto-recovery (no permanent suppression; self-heals once the cause is fixed; does not disable the active LO):

1. **Detect the 401 auth failure.** Add to `FATAL_WORKER_OUTPUT_MARKERS` (line 193): `("Invalid authentication credentials", "auth_failure")` and `("API Error: 401", "auth_failure")`. `_matched_worker_output_markers` already scans both stdout and stderr (line 660).
2. **Define the fast-trip classes.** Add `FAST_TRIP_FAILURE_CLASSES = frozenset({"auth_failure", "max_turn_exhaustion", "provider_failure", "provider_configuration_failure", "guard_denied_write", "guard_denial"})` near line 206.
3. **Trip the breaker on the first such failure.** In `_process_pending_exit_codes` (~line 3203), compute an effective threshold: `1` when `failure_reason in FAST_TRIP_FAILURE_CLASSES`, else `DEFAULT_DISPATCH_MAX_RETRIES`. Trip the breaker when `failure_count >= effective_threshold`.

This uses the **circuit breaker** (which half-opens after `DEFAULT_DISPATCH_RETRY_DELAY_SECONDS` = 300s for one probe), NOT the permanent `non_retryable_failure` path. Result: a 401 trips after one failure; ~one probe spawn per 5 minutes while broken (vs. churn); automatic reset on the first successful dispatch once auth is restored.

## Specification Links

- `GOV-AUTOMATION-VALUE-VS-COST-001` - the governing principle this fix implements: gate the expensive re-spawn behind a cheap deterministic failure-class check.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs this bridge filing and the numbered-file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in the verification plan below.
- `GOV-STANDING-BACKLOG-001` - WI-4703 is the governed backlog item for this work.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - the PAUTH links spec `GOV-AUTOMATION-VALUE-VS-COST-001`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files are under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory); `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory); `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

## Owner Decisions / Input

- Owner directive (2026-06-20, this interactive session): "Please tackle the dispatch repair and drive it through the bridge protocol to VERIFIED" (reaffirmed: "loop this task, repeat until complete"; "resume"). Captured as owner-decision deliberation `DELIB-S20260620-WI4703-DISPATCH-REPAIR-AUTH` with a validated formal-artifact approval packet, and operationalized as the bounded PAUTH cited above. No further owner decision is required to proceed once this proposal receives Loyal Opposition GO.

## Prior Deliberations

- `DELIB-S20260620-WI4703-DISPATCH-REPAIR-AUTH` - the owner-decision authorization for this work.
- `DELIB-20265287` - owner-decision anchor for `GOV-AUTOMATION-VALUE-VS-COST-001`; the principle this fix operationalizes.
- `DELIB-20263200`, `DELIB-20263376`, `DELIB-20261612`, `DELIB-2418` - prior dispatch suppression / claim-eligibility / trigger-lag bridge decisions surfaced by deliberation search (-002 Prior Deliberations); none rejects a breaker-sensitivity change.
- `bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-002.md` - the NO-GO addressed by this revision.
- `bridge/gtkb-wi4682-automation-value-cost-principle-014.md` - the 6-hour churn this proposal's diagnosis draws on (the live demonstration of the defect).

## Requirement Sufficiency

Existing requirements sufficient. `GOV-AUTOMATION-VALUE-VS-COST-001` is the governing requirement; this proposal derives a concrete dispatcher behavior from it. No new specification is required before implementation.

## Specification-Derived Verification Plan

New unit tests in `platform_tests/scripts/test_dispatch_non_transient_fast_trip.py` (spec-to-test mapping):

| Specification / behavior | Test | Expected |
| --- | --- | --- |
| `GOV-AUTOMATION-VALUE-VS-COST-001` - 401 detected as non-transient | feed a worker launch whose stdout contains the 401 result JSON to `_matched_worker_output_markers` | matched marker label == `auth_failure` |
| Fast-trip: non-transient class trips at failure_count 1 | drive `_process_pending_exit_codes` with one `auth_failure` failure | `circuit_breaker_tripped == True` after a single failure |
| Retryable class unchanged | drive one generic `subprocess_execution_failed` (not in fast-trip set) | breaker NOT tripped at failure_count 1; still trips at 3 |
| Half-open recovery preserved | tripped fast-trip breaker + elapsed retry delay | half-open probe allowed; success resets failure_count + breaker |
| max_turn_exhaustion fast-trips | one `max_turn_exhaustion` marker failure | breaker tripped at failure_count 1 |

Commands: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatch_non_transient_fast_trip.py -q --tb=short`; regression `... -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q`; `ruff check` + `ruff format --check` on changed files.

## Risk And Rollback

- Risk: over-suppressing a genuinely-transient failure that happened to be classed fast-trip. Mitigation: the half-open probe (300s) still retries once per window and auto-resets on success, so a transient blip recovers within ~5 min; only the wasteful 2nd/3rd immediate re-spawn is removed.
- Risk: disabling the active LO. Mitigation: this uses the breaker (half-open recovery), NOT the permanent `non_retryable_failure` path; Codex LO auto-recovers once it produces a successful dispatch.
- Rollback: revert the single source commit; the new test file is additive. No state migration; existing `dispatch-state.json` schema unchanged (reuses `circuit_breaker_tripped`/`failure_count`).

## Acceptance Criteria

- [ ] 401 auth output is classified `auth_failure` and is in the fast-trip set.
- [ ] A single fast-trip-class failure trips the breaker; a single generic failure does not.
- [ ] Half-open recovery and success-reset behavior are unchanged for both tiers.
- [ ] New unit tests pass; existing `test_cross_harness_bridge_trigger.py` regression passes; ruff check + format clean.
- [ ] No change to `non_retryable_failure` semantics; no permanent suppression introduced.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
