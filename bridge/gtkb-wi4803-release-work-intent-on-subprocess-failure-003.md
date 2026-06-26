NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 130bf9ae-15f0-4373-a7b5-9286568dbc97
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

# gtkb-wi4803-release-work-intent-on-subprocess-failure — Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4803-release-work-intent-on-subprocess-failure
Version: 003

Responds-To: bridge/gtkb-wi4803-release-work-intent-on-subprocess-failure-002.md (GO)
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4803
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26
Recommended commit type: fix

## Implementation Report

Implemented per the `-002` GO within the authorized `target_paths`. Changes are staged in the working tree (uncommitted) for Loyal Opposition inspection; per the protocol the VERIFIED finalization helper creates the commit with the verified paths plus the verdict.

Verified paths (for the finalization helper `--include`):
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

## Files Changed

- `scripts/cross_harness_bridge_trigger.py`: in `_process_pending_exit_codes`, the failure branch (the `else` taken once a non-zero / abrupt-termination / over-lifetime exit has been observed via the `.exit_code` status file) now releases the launch's leaked work-intent claim. It reads `work_intent_slugs` + `work_intent_session_id` from `last_launch` and calls `_release_prime_work_intents(list(slugs), project_root=project_root, session_id=str(session))`, then stamps `last_launch["work_intent_released_on_failure"] = True`. Idempotent (`_release_prime_work_intents` swallows registry errors), keyed to the recorded dispatch session (frees only this launch's own claim), and gated on the flag so it fires once. Only Prime launches stamp `work_intent_slugs`, so it never fires for LO launches. The success branch is unchanged (failure-only scope, per the GO).
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`: added a `_prime_failure_last_launch` helper and 3 focused unit tests that exercise `_process_pending_exit_codes` directly (NOT the `run_trigger` integration path, which carries the WI-4712 pre-existing failures):
  - `test_process_pending_exit_codes_releases_work_intent_on_failure` — non-zero exit releases the claim (proven by a different session being able to re-acquire) and sets the audit flag.
  - `test_process_pending_exit_codes_releases_work_intent_on_abrupt_termination` — missing status file + dead pid (the synthesized `4294967295` path) also releases the claim.
  - `test_process_pending_exit_codes_keeps_work_intent_on_success` — exit `0` does NOT release (scope guard locking the failure-only behavior).

No change to `run_with_status.py`, `_spawn_harness`, the acquire path, or the success branch.

## Specification Links (carried forward from -001)

- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatched-worker claim lifecycle (acquire on dispatch, release on completion/failure).
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — a leaked claim that blocks re-dispatch is a dispatch-service reliability defect.
- `DCL-DISPATCH-ENVELOPE-RULES-001` — dispatch lifecycle rules.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file in the append-only chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied (links + spec-to-test mapping below).
- `GOV-STANDING-BACKLOG-001` — WI-4803 is the governing backlog item.

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 / SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (claim must not outlive a failed dispatch) | `test_process_pending_exit_codes_releases_work_intent_on_failure` | PASS |
| same (abrupt termination `4294967295`) | `test_process_pending_exit_codes_releases_work_intent_on_abrupt_termination` | PASS |
| failure-only scope (no over-release on success) | `test_process_pending_exit_codes_keeps_work_intent_on_success` | PASS |

## Verification Evidence (commands + observed results)

- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -k process_pending_exit_codes -q --tb=short` → **3 passed**, 100 deselected.
- Regression: `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -k "exit_code or work_intent or process_pending" -q --tb=short` → **5 passed**, 98 deselected (3 new + 2 existing work-intent tests; no regression in the related set).
- `python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py` → **All checks passed**.
- `python -m ruff format --check` (same two files) → **2 files already formatted**.

## Prior Deliberations

- `DELIB-20266137` — owner authorization for this dispatcher-reliability drive (Fixes-then-Phases); source authority for WI-4803.
- WI-4845 / WI-4806 worker-lifetime lineage — the 600s lifetime cap (exit 124) and abrupt worker death are the primary producers of the launched-then-failed condition this fix reconciles.
- `bridge/gtkb-wi4803-release-work-intent-on-subprocess-failure-002.md` (Cursor LO GO) — the verdict this report responds to.

## Owner Decisions / Input

- Authorized by `DELIB-20266137` (owner AUQ this session, 2026-06-26); `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26` covers WI-4803. No further owner decision is required; the fix changes no dispatch-target selection or owner-facing behavior — it frees a leaked coordination claim on worker failure.

## Requirement Sufficiency

Existing requirements sufficient (carried forward from `-001`). No new or revised requirement was needed; the linked dispatcher specs fully constrain the fix.

## Risk / Rollback

- Risk: low. Additive release in the existing failure branch; idempotent; keyed to the recorded dispatch session; success path and all other dispatch logic unchanged.
- Rollback: revert the failure-branch release block in `cross_harness_bridge_trigger.py` and the 3 added tests; prior behavior (claim lingers until TTL) returns. No schema change; append-only KB untouched.

## Recommended Commit Type

`fix:` — repairs a work-intent claim leak on dispatched-worker subprocess failure that blocked thread re-dispatch until TTL. No new capability surface; no success-path behavior change.
