NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: eb4f5b12-588a-43b5-bf6b-5439c7a97cf0
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report

# Implementation Report: WI-4845 daemon passes per-role worker --lifetime override

Document: gtkb-wi4845-daemon-worker-lifetime-override
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Responds to: bridge/gtkb-wi4845-daemon-worker-lifetime-override-002.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4845
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4845-CONFIGURABLE-WORKER-LIFETIME-CAP
Recommended commit type: fix

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

## Summary

Implemented per the GO'd `-001` proposal (Cursor LO GO at `-002`). The daemon's live-spawn path (`gtkb_dispatcher_daemon.py` `_execute_live_spawns` -> `cross_harness_bridge_trigger._spawn_harness`) already threads `worker_lifetime_seconds(role)` into the `run_with_status.py --lifetime` argument (Variant A, VERIFIED at `gtkb-wi4845-configurable-worker-lifetime-004`, gave Loyal Opposition 1800s). This change completes the per-role override:

1. `worker_lifetime_seconds(role_label)` now returns the **Prime Builder** cap (default `PB_IMPL_WORKER_LIFETIME_SECONDS = 5400`, 90 min) in addition to the LO cap (1800, 30 min); every other role still returns `None` (run_with_status.py default 600s preserved).
2. Both caps are **env-configurable**: `GTKB_WORKER_LIFETIME_LO_SECONDS` / `GTKB_WORKER_LIFETIME_PB_SECONDS` (positive-int; invalid/non-positive falls back to the default).
3. `RESET_STRAGGLER_AGE_SECONDS` (the operator `--reset-recipient` straggler-reap floor, WI-4805) now tracks the **longest legitimate per-role lifetime** (env-aware: `max(LO, PB) + margin`, default 5700s) instead of the stale LO-only 2100s. Without this, a healthy 90-min PB worker would become reapable at ~35 min — the correctness coupling that adding PB=5400 introduces. The constant lives in the same in-scope file (`cross_harness_bridge_trigger.py`) and is required for the PB lifetime to be effective end-to-end.

`scripts/gtkb_dispatcher_daemon.py` needed no change: the daemon reuses `_spawn_harness`, so the per-role `--lifetime` flows through automatically. No change to dispatch decision logic.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — report filed as the next append-only numbered bridge file (NEW post-implementation report) for verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: specs carried forward from `-001`; tests mapped to the override.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: WI-4845 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: the override + per-role values + env-config map to executed derived tests.
- `ADR-DISPATCHER-ARCHITECTURE-001` — headless workers completing their unit of work (review/implementation) is required for the daemon to be a functioning dispatch substrate.
- `GOV-STANDING-BACKLOG-001` — WI-4845 is an authorized standing-backlog item under the active project.

## Spec-to-Test Mapping

| Spec / clause | Test (new) | Result |
|---|---|---|
| WI-4845 + Q3 per-role override (spawn command) | `test_daemon_spawn_passes_per_role_lifetime` | PASS: `_spawn_harness` wrapped command carries `--lifetime 1800` for an LO target and `--lifetime 5400` for a PB target (real spawn path; fake Popen captures the run_with_status command). |
| Env-configurability + per-role values + fallback | `test_daemon_worker_lifetime_env_override` | PASS: LO=1800/PB=5400 defaults; env overrides to 2400/7200; invalid/non-positive falls back; other roles / None -> None. |
| Non-regression | existing `test_gtkb_dispatcher_daemon.py` suite | PASS: 21 passed total (16 prior + 3 WI-4855 + 2 WI-4845). |

The spawn test exercises the production spawn path (`trigger._spawn_harness`, which the daemon's `_execute_live_spawns` reuses) per GOV-10/GOV-19 outside-in testing.

## Executed Commands

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
# 21 passed in 3.20s

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py platform_tests/scripts/test_dispatch_concurrency_cap.py -q
# 127 passed, 2 failed. Both failures (test_cap_gate_blocks_dispatch_at_or_over_limit, test_prime_spawn_creates_dispatch_authorization_packet_and_env) are PRE-EXISTING: confirmed they fail identically against HEAD's cross_harness_bridge_trigger.py (git stash of this change, re-run). NOT caused by WI-4845.

groundtruth-kb/.venv/Scripts/python.exe -m ruff check (cross_harness_bridge_trigger.py, test_gtkb_dispatcher_daemon.py)
# test file clean. trigger.py: 1 import-block error at L89 — PRE-EXISTING in HEAD (confirmed via git show HEAD ... piped to ruff check stdin); not within the WI-4845 hunk (L2411+).

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check (same 2 files)
# 2 files already formatted

## Pre-Existing Failures Flagged (not in scope; PHASE-Y risk)

`test_prime_spawn_creates_dispatch_authorization_packet_and_env` failing on HEAD means the Prime-spawn impl-auth-packet path has a failing test independent of WI-4845. Because PHASE Y's autonomous loop dispatches a headless PB implementer (which issues impl-auth packets via `_issue_dispatch_authorization_for_selected`), this is a PHASE-Y readiness risk worth investigating before the live-loop test. Captured as a follow-up; out of WI-4845 scope.

## Requirement Sufficiency

Existing requirements sufficient. WI-4845 specifies a configurable/raised worker-lifetime cap; Q3 of `DELIB-20266203` sets the per-role values (LO ~30 min, PB ~90 min, env-configurable) and the daemon-passes-override shape. No new requirement; this completes wiring the existing `run_with_status.py --lifetime` capability into the per-role spawn so the PB cap is effective.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4845-CONFIGURABLE-WORKER-LIFETIME-CAP` (active, includes WI-4845). The owner, in the S20260626 grill (`DELIB-20266203`, Q3), chose per-role generous worker-lifetime caps (LO ~30 min, PB ~90 min, env-configurable) with the daemon passing the override. Source-only defect fix; no formal-artifact / narrative mutation, so no separate artifact-approval packet is required.

## Prior Deliberations

- `DELIB-20266203` — Owner clarification (S20260626): autonomous-loop plan; this is X3 (worker-lifetime override), Q3 per-role generous caps.
- `DELIB-20266084` — WI-4787 daemon foundation; the daemon spawn path this augments.
- `DELIB-20266166` — WI-4804 scope split establishing daemon-program ownership of remediation/spawn behavior.
- bridge/gtkb-wi4845-daemon-worker-lifetime-override-001 (NEW), -002 (GO). Sibling thread gtkb-wi4845-configurable-worker-lifetime (VERIFIED) added the LO cap + the `_spawn_harness` wiring this builds on.

## Recommended Commit Type

`fix` — repairs the worker-kill-mid-work defect for PB workers (terminated at the 600s default because no PB override was passed) and corrects the straggler-reap floor coupling. No new capability surface beyond per-role wiring of an existing flag.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
