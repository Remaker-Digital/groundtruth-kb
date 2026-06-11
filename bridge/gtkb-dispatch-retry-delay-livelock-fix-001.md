NEW
author_identity: claude
author_harness_id: B
author_session_context_id: ad3221a1-e3bc-4d3e-bcec-d3d608598322
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Defect-Fix Proposal - Cross-harness trigger retry-delay livelock: backoff measured against perpetually-rewritten updated_at permanently wedges a recipient after one failed launch

bridge_kind: prime_proposal
Document: gtkb-dispatch-retry-delay-livelock-fix
Version: 001
Date: 2026-06-11 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4459

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

## Claim

This proposal asserts that `scripts/cross_harness_bridge_trigger.py` contains a retry-delay livelock that permanently prevents bridge dispatch to a recipient after a single failed launch, in violation of `DCL-SMART-POLLER-AUTO-TRIGGER-001` ("auto-triggers harness when work waits"). Re-baselining the retry-backoff window on the recipient's last *launch* timestamp (`last_launch.launched_at`) instead of the per-evaluation-rewritten `updated_at` resolves the livelock without altering the actionable-signature dispatch semantics or any other dispatch behavior.

## Defect / Reproduction

**Root cause.** The retry-delay gate computes its elapsed window against the wrong timestamp:

- `scripts/cross_harness_bridge_trigger.py:2499` reads `prior_updated_at = prior.get("updated_at")` and computes `elapsed = now - updated_time` (line 2503).
- `scripts/cross_harness_bridge_trigger.py:2373` sets `recipient_state["updated_at"] = _now_iso()` on **every** trigger evaluation, including evaluations that only enforce the delay and `continue` (lines 2510-2516).

The trigger fires on every PostToolUse and Stop event across all active sessions. Under continuous platform activity, consecutive firings occur less than `OLLAMA_RETRY_DELAY_SECONDS` (default 300s) apart, so `elapsed < retry_delay_seconds` is always true: the delay is re-armed on every evaluation and `updated_at` is perpetually reset to "now". Because `failure_count` changes only on an actual launch (reset at line 2122, increment at line 2126) and the delay-enforcing `continue` prevents any launch, `failure_count` freezes at its first value (1). It never clears (no successful launch) and never reaches the circuit-breaker threshold (no further failed launches). The result is a permanent dispatch deadlock for that recipient.

**Observed reproduction (2026-06-11).** A single Codex (`loyal-opposition:A`) dispatch at 14:15:01Z exited code 1 (incidental: it was reviewing a since-VERIFIED Stage 0 entry), setting `failure_count = 1`. From then until 16:25Z (the last recorded evaluation, ~2h later), `.gtkb-state/bridge-poller/dispatch-state.json` shows the recipient stuck at `last_result: "retry_delay_enforced"`, with `last_dispatched_signature (c3f02244...)` not equal to the current actionable `signature (4f53cda...)`. Two freshly-actionable bridge entries (Stage 1 `-005`, Stage 2 `-003`) were never dispatched to Codex despite the trigger re-evaluating repeatedly. The platform required a manual Codex bridge scan to unblock.

The retry-delay backoff should be measured from the last *launch attempt*, a timestamp written only when a launch actually occurs (`last_launch.launched_at`, set at line 1866 and carried forward at line 2382). That baseline is stable across delay-only evaluations; the current `updated_at` baseline is not.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cross_harness_bridge_trigger.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements - `DCL-SMART-POLLER-AUTO-TRIGGER-001` (dispatch must auto-trigger the recipient harness when actionable work waits) and `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` (owner-out-of-loop dispatch) - already constrain the corrected behavior; this defect fix restores conformance to them. No new or revised requirement is required before implementation.

(Section added post-GO to satisfy the implementation-start gate's mandatory `## Requirement Sufficiency` check; the defect-fix scaffold omitted it. The fix scope and reviewed technical content are unchanged.)

## Specification Links

- `DCL-SMART-POLLER-AUTO-TRIGGER-001` - **Primary.** The constraint the livelock violates: the dispatch mechanism must auto-trigger the recipient harness when actionable work waits. The fix restores conformance by ensuring the retry-delay window actually elapses, so a wedged recipient resumes dispatching.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` - Governing architecture decision: the dispatch mechanism spawns headless harness instances when work is actionable, keeping the owner out of the loop. The livelock defeats this by forcing manual scans; the fix restores owner-out-of-loop dispatch.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is canonical workflow state; this fix changes only dispatch timing, never INDEX authority or the actionable-signature scheme.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites all relevant cross-cutting specs in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The Specification-Derived Verification Plan below maps each linked spec to an executable test.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization / Project / Work Item metadata present above.
- `GOV-STANDING-BACKLOG-001` - WI-4459 is the standing-backlog work item; admitted to PROJECT-GTKB-RELIABILITY-FIXES (membership `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4459`).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - The trigger is registered as PostToolUse + Stop hooks on both harnesses; this fix does not change hook registration or parity.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Defect captured as WI-4459 before implementation; this proposal is the artifact-lifecycle progression from captured defect to a scoped fix.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner approval to implement WI-4459 collected via AskUserQuestion (see Owner Decisions / Input).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target paths are platform paths under `E:\GT-KB`; no application-subtree placement concern.

## Prior Deliberations

- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - Slice 4 retirement of the smart poller in favor of the cross-harness event-driven trigger; established the trigger as the canonical dispatch substrate and that "dispatch-on-actionable-change is the load-bearing semantic." The livelock is a defect in that load-bearing semantic; this fix preserves it.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` (v2) and `DCL-SMART-POLLER-AUTO-TRIGGER-001` (v2) - The mechanism-agnostic supersede establishing the auto-trigger contract that the fix restores.
- No prior deliberation proposed or rejected re-baselining the retry-delay window; this is the first treatment of the retry-delay livelock specifically. Adjacent dispatch-reliability work (WI-4404 scheduled-poller restoration, WI-4408 deadlock-and-contention advisory, WI-4413 FAB-01 launchability) addresses different failure modes (interval policy, launchability) and does not name this `updated_at`-baseline livelock.

## Owner Decisions / Input

- **AskUserQuestion (2026-06-11, this session):** Owner authorized moving WI-4459 (the retry-delay livelock) into implementation scope. AUQ "Fix scope" answer selected "WI-4459 livelock (keystone)". This is the implementation-approval evidence per the backlog-approval-state rule (auq_resolved to implementation_authorized) and the AUQ-only enforcement stack.
- **AskUserQuestion (2026-06-11, this session):** Owner directed "fix hooks and bridge dispatch issues first, then resume backlog triage," and approved proceeding to file the proposal ("I'd prefer you just run it").
- Project authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active, project-wide; allows `source` + `test_addition`), covering WI-4459 via active project membership.

## Proposed Scope

**IP-1 - Re-baseline the retry-delay window on the last launch timestamp (`scripts/cross_harness_bridge_trigger.py`).**

In the retry-delay gate (lines ~2495-2516), replace the `prior["updated_at"]` baseline with the recipient's last launch timestamp:

- Read `last_launch = prior.get("last_launch")` and `last_launch_at = last_launch.get("launched_at")` when `last_launch` is a dict.
- When `last_launch_at` is present, compute `elapsed = now - parse(last_launch_at)` and set `is_delay_active = elapsed < retry_delay_seconds`.
- When `last_launch_at` is absent (defensive; should not occur while `failure_count > 0`, since `failure_count` increments only after a launch that sets `last_launch`), do **not** enforce the delay: fail open to dispatch so a recipient is never wedged by missing launch metadata.

No other behavior changes: the actionable-signature computation, kind-aware routing, active-session suppression, circuit-breaker threshold, and `OLLAMA_RETRY_DELAY_SECONDS` env override are all preserved.

**IP-2 - Regression test (`platform_tests/scripts/test_cross_harness_bridge_trigger.py`).**

Add a livelock regression test asserting the post-state dispatch behavior (a structural invariant, not a call-sequence check):

- Construct a prior `dispatch-state.json` recipient state with `failure_count = 1`, `last_launch.launched_at` set to a timestamp greater than `retry_delay_seconds` (300s) in the past, and `updated_at` set to "now".
- Provide a pending actionable bridge entry whose signature differs from `last_dispatched_signature`.
- Fire the trigger evaluation and assert the recipient **dispatches** (a launch is attempted; `last_result` is not `retry_delay_enforced`).
- Add a complementary test asserting the delay IS still enforced when `last_launch.launched_at` is recent (< 300s), so the fix does not disable backoff entirely.

## Specification-Derived Verification Plan

| Spec / Clause | Derived Test | Command |
|---|---|---|
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` (auto-trigger when work waits) | `test_retry_delay_clears_after_launch_window_elapses` - wedged-recipient state (old `last_launch` + fresh `updated_at`) dispatches | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -k retry_delay -q` |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` (backoff still honored) | `test_retry_delay_enforced_within_launch_window` - recent `last_launch` still yields `retry_delay_enforced` | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -k retry_delay -q` |
| `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` (no other behavior change) | existing trigger suite remains green (signature/routing/suppression unchanged) | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q` |
| Code quality | lint + format gates on changed files | `ruff check <changed.py>` and `ruff format --check <changed.py>` |

## Acceptance Criteria

1. The new regression test fails against the current code (livelock present) and passes against the fix.
2. The existing `test_cross_harness_bridge_trigger.py` suite remains fully green (no signature / routing / suppression regression).
3. `ruff check` and `ruff format --check` pass on both changed files.
4. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-retry-delay-livelock-fix` reports `missing_required_specs: []`.
5. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-retry-delay-livelock-fix` reports no blocking gaps.

## Risks / Rollback

- **Risk:** mis-reading the `last_launch` shape could throw. **Mitigation:** type-guarded `.get()` access with fail-open behavior; no new exception path introduced.
- **Risk:** the fail-open-when-no-launch branch could over-dispatch. **Mitigation:** bounded - `failure_count > 0` implies a prior launch (which sets `last_launch`), so the fail-open branch is effectively unreachable in normal operation; worst case is one immediate retry, which is the desired recovery behavior.
- **Risk:** changing backoff timing affects circuit-breaker accrual. **Mitigation:** the fix makes the breaker *reachable* (failures can now accrue past 1), which is the intended safety behavior; the threshold itself is unchanged.
- **Rollback:** single-function revert of the retry-delay gate; the new test is additive. No data migration, no schema change, no state-file format change.

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

## Recommended Commit Type

`fix`
