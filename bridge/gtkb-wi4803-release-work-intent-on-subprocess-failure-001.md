NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 130bf9ae-15f0-4373-a7b5-9286568dbc97
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

# gtkb-wi4803-release-work-intent-on-subprocess-failure — release the dispatched Prime worker's work-intent claim when the worker subprocess fails

bridge_kind: prime_proposal
Document: gtkb-wi4803-release-work-intent-on-subprocess-failure
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4803

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4803 (defect): a dispatched Prime worker that **launches and then fails** leaks its work-intent claim, leaving the bridge thread claim-blocked against re-dispatch until the claim's TTL expires. The cross-harness trigger pre-acquires the claim under `session_id = dispatch_id` (`_acquire_prime_work_intent_batch`), and the dispatched worker inherits that same id via `GTKB_BRIDGE_POLLER_RUN_ID` — so it is a single claim keyed to `dispatch_id`. The launch path releases that claim **only when the spawn fails to launch** (`cross_harness_bridge_trigger.py:4604-4613`, gated on `not launch.get("launched")`); because `_spawn_harness` is fire-and-forget, a *launched* worker that subsequently exits non-zero, is killed at the 600s lifetime cap (WI-4845, exit 124), or dies abruptly (4294967295) is never released. The fix releases the claim in `_process_pending_exit_codes` — the existing reconcile point where the trigger reads the worker's `.exit_code` status file and branches into its failure handler — so the claim is freed as soon as the trigger observes the worker's failure exit.

## Problem detail (for LO review)

- `cross_harness_bridge_trigger.py:4557` — `_acquire_prime_work_intent_batch` acquires the claim for the selected Prime thread(s) under `work_intent_session_id` (= `dispatch_id`, per `_work_intent_session_id`, line 1060-1061).
- `cross_harness_bridge_trigger.py:4604-4613` — the **only** release on the launch path; gated on `not launch.get("launched")`. A successfully-launched worker bypasses it.
- `_spawn_harness` (line 3225+) is fire-and-forget: it `Popen`s `run_with_status.py` and returns without waiting. `run_with_status.py` is a deliberately generic process wrapper (it knows nothing of slugs/claims/dispatch_id), so the release does NOT belong there.
- `_process_pending_exit_codes` (line 3724, called at line 4120 early in `run_trigger`) is the reconcile point: it reads `<dispatch_id>.exit_code`, sets `last_launch["exit_code"]`, and branches into a "Failure!" block (line 3806+) for non-zero exit / missing-status-with-dead-pid (4294967295) / fatal worker-output markers / LO `no_verdict_produced`. The failure block records the failure and trips the circuit breaker but never releases the leaked work-intent claim.
- `last_launch` already carries the data needed to release: `work_intent_slugs` (set at line 4632) and `work_intent_session_id` (set at line 4601). Only Prime dispatches populate these (the acquire batch is Prime-only, gated at line 4552), so presence of `work_intent_slugs` is a reliable Prime-launch discriminator.
- Compounding effect: WI-4845 cloud-LO workers killed at 600s, and any abruptly-dead Prime worker, currently leave a dangling claim; combined with `work_intent_already_held` suppression this contributes to the stale-FAIL / re-dispatch-blocked class (WI-4725 lineage).

## Proposed change

1. `scripts/cross_harness_bridge_trigger.py` — in `_process_pending_exit_codes`, inside the failure branch (the `else` at line 3806, after the failure is recorded), release the launch's work-intent claim when present:
   - read `wi_slugs = last_launch.get("work_intent_slugs")` and `wi_session = last_launch.get("work_intent_session_id")`;
   - if both are present, call `_release_prime_work_intents(list(wi_slugs), project_root=project_root, session_id=str(wi_session))` and stamp `last_launch["work_intent_released_on_failure"] = True` for audit/idempotency.
   - This is idempotent (`_release_prime_work_intents` swallows `WorkIntentRegistryError`) and fires only for Prime launches that actually held claims. The success branch is intentionally unchanged: on success the worker advances the thread (signature updates suppress re-dispatch) and the worker's own release / TTL handles the claim, so success-path release is out of scope for this defect.
2. `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — add a focused unit test exercising `_process_pending_exit_codes` directly (NOT the `run_trigger` integration path, which carries pre-existing failures tracked as WI-4712):
   - **failure-releases**: build a `recipients_state` with a Prime `last_launch` (`launched=True`, `work_intent_slugs=[slug]`, `work_intent_session_id=did`, no `exit_code_processed`); write a `<did>.exit_code` status file containing a non-zero code; call `_process_pending_exit_codes`; assert the claim for `slug` is released (the work-intent registry shows no holder, or `release_work_intent` was invoked with `(slug, did)`), and `last_launch["work_intent_released_on_failure"] is True`.
   - **abrupt-termination-releases**: omit the status file, set a dead `pid`; assert release on the synthesized `4294967295` path.
   - **success-does-not-release**: status file `0`; assert the claim is NOT released (failure-only scope locked).

No change to `run_with_status.py`, `_spawn_harness`, or the acquire path.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher architecture-of-record; the dispatched-worker claim lifecycle (acquire on dispatch, release on completion/failure) is part of the dispatch reliability contract this defect violates.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — centralized dispatch service requirement; a leaked claim that blocks re-dispatch is a dispatch-service reliability defect.
- `DCL-DISPATCH-ENVELOPE-RULES-001` — dispatch envelope rules governing the dispatch lifecycle.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file in the append-only versioned chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-4803 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266137` — owner authorization for this dispatcher-reliability drive (Fixes-then-Phases), the source authority for WI-4803 implementation under `PROJECT-GTKB-DISPATCHER-RELIABILITY`.
- WI-4845 / WI-4806 worker-lifetime lineage — the 600s lifetime cap (`run_with_status.py` `DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS`, exit 124) is a primary producer of the launched-then-failed condition this fix reconciles.
- WI-4725 — dispatch-health stale-FAIL / `work_intent_already_held` suppression lineage; a leaked claim is one input to that class.
- No prior deliberation directly decided the claim-release-on-failure mechanism; deliberation search ("work-intent claim release on dispatched worker subprocess failure") surfaced no on-point precedent.

## Owner Decisions / Input

- Authorized by `DELIB-20266137` (owner AUQ this session, 2026-06-26): implement WI-4803 under `PROJECT-GTKB-DISPATCHER-RELIABILITY` as the first item of the Fixes-then-Phases drive. Covered by `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26` (WI-4803 in `included_work_item_ids`). No further owner decision is required; the fix changes no dispatch-target selection or owner-facing behavior — it only frees a leaked coordination claim on worker failure.
- Topology this session: Claude (B) = Prime Builder; Cursor (E) = Loyal Opposition reviewer.

## Requirement Sufficiency

Existing requirements sufficient — `ADR-DISPATCHER-ARCHITECTURE-001` + `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` + `DCL-DISPATCH-ENVELOPE-RULES-001` establish that a dispatched-worker claim must not outlive a failed dispatch and block re-dispatch. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 / SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (claim must not outlive a failed dispatch) | `test_process_pending_exit_codes_releases_work_intent_on_failure` (new) | After a launched Prime worker records a non-zero exit, `_process_pending_exit_codes` releases the recorded `work_intent_slugs` under `work_intent_session_id`; the registry shows no holder and `last_launch["work_intent_released_on_failure"]` is True. |
| same (abrupt termination) | `test_process_pending_exit_codes_releases_work_intent_on_abrupt_termination` (new) | Missing status file + dead pid (4294967295 path) also releases the claim. |
| failure-only scope (no over-release) | `test_process_pending_exit_codes_keeps_work_intent_on_success` (new) | Exit code 0 does NOT release the claim (success path unchanged). |
| No-regression | existing `_process_pending_exit_codes` behavior (failure-count, circuit-breaker, dispatch-failures log) unaffected; targeted unit tests avoid the WI-4712 flaky `run_trigger` path; `ruff check` / `ruff format --check` on the changed test | green |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -k "work_intent" -q --tb=short`; `ruff check` then `ruff format --check` on the changed files.

## Risk / Rollback

- Risk: low. The release is additive in the existing failure branch, idempotent (errors swallowed), and fires only for Prime launches that recorded a claim. It cannot release another session's claim (release is keyed to the recorded `work_intent_session_id` = `dispatch_id`). It changes no dispatch-target selection, no signature/dedupe logic, and no success-path behavior.
- Rollback: revert the failure-branch release block and the new tests; prior behavior (claim lingers until TTL) returns. No schema change; append-only KB untouched.
- Out of scope: the WI-4845 lifetime-cap configurability (separate thread, concurrent session), success-path claim release (benign TTL expiry), `run_with_status.py` (kept generic), and storm-watchdog reaping (sibling WIs 4804/4805/4834).

## Recommended Commit Type

`fix:` — repairs a work-intent claim leak on dispatched-worker subprocess failure that blocked thread re-dispatch until TTL. No new capability surface; no behavior change on the success path.
