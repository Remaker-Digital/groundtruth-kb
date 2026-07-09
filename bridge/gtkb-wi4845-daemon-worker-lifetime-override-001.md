NEW

# gtkb-wi4845-daemon-worker-lifetime-override — Daemon passes per-role worker-lifetime override so headless workers complete (no 600s mid-work kill)

bridge_kind: prime_proposal
Document: gtkb-wi4845-daemon-worker-lifetime-override
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: b3b723c1-9a52-424c-94f3-70c609bd1588
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4845-CONFIGURABLE-WORKER-LIFETIME-CAP
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4845

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`scripts/run_with_status.py` already accepts a `--lifetime <seconds>` argument (L94-104) and applies `DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS = 600` only when the dispatcher omits it. The daemon's live spawn path (`scripts/gtkb_dispatcher_daemon.py` `_execute_live_spawns` -> `cross_harness_bridge_trigger._spawn_harness`) does NOT pass `--lifetime`, so every headless worker runs under the 600s default and is killed mid-work (exit 124). A full Loyal Opposition review or a Prime Builder implementation routinely exceeds 600s, so the worker is terminated before it can emit a verdict or report — the root completion blocker for the autonomous PB/LO loop (the go-live finding behind WI-4845/WI-4860).

This proposal makes the daemon pass a **per-role** `--lifetime` override when it spawns workers: Loyal Opposition review ~1800s (30 min), Prime Builder implementation ~5400s (90 min), each env-configurable (e.g. `GTKB_WORKER_LIFETIME_LO_SECONDS` / `GTKB_WORKER_LIFETIME_PB_SECONDS`). The override threads through `_spawn_harness` (the shared spawn helper the daemon reuses) into the `run_with_status.py --lifetime` argument that already exists. No change to dispatch decision logic; only the spawn command gains the lifetime flag.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next append-only numbered bridge file.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites governing specs; tests mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: WI-4845 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: the override + per-role values map to derived tests.
- `ADR-DISPATCHER-ARCHITECTURE-001` — the daemon is the GT-KB-owned dispatch service; headless workers completing their unit of work (review/implementation) is required for the daemon to be a functioning dispatch substrate.
- `GOV-STANDING-BACKLOG-001` — WI-4845 is an authorized standing-backlog item under the active project.

## Prior Deliberations

- `DELIB-20266203` — Owner clarification (S20260626): autonomous-loop plan; this is X3 (worker-lifetime override) and Q3 resolved per-role generous caps (LO ~30 min, PB ~90 min, env-configurable).
- `DELIB-20266084` — WI-4787 daemon foundation; the daemon spawn path this proposal augments.
- `DELIB-20266166` — WI-4804 scope split establishing the daemon-program ownership of remediation/spawn behavior.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4845-CONFIGURABLE-WORKER-LIFETIME-CAP` (active, includes WI-4845). The owner, in the S20260626 grill (`DELIB-20266203`, Q3), chose per-role generous worker-lifetime caps (LO ~30 min, PB ~90 min, env-configurable) with the daemon passing the override. Source-only defect fix; no formal-artifact/narrative mutation, so no separate artifact-approval packet is required.

## Requirement Sufficiency

Existing requirements sufficient. WI-4845 specifies a configurable/raised worker-lifetime cap; Q3 of `DELIB-20266203` sets the per-role values and the daemon-passes-override shape. No new requirement; this wires the existing `run_with_status.py --lifetime` capability into the daemon spawn so the cap is effective per role.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| WI-4845 + Q3 per-role override | `test_daemon_spawn_passes_per_role_lifetime` (new) | the daemon live-spawn command for an LO target includes `--lifetime` = the LO value (default 1800); for a PB target = the PB value (default 5400). |
| Env-configurability | `test_daemon_worker_lifetime_env_override` (new) | `GTKB_WORKER_LIFETIME_LO_SECONDS` / `GTKB_WORKER_LIFETIME_PB_SECONDS` override the defaults in the spawn command. |
| `run_with_status` honors override | inspection/unit over `run_with_status.py` `_parse_lifetime` + `p.wait(timeout=lifetime_seconds)` | a passed `--lifetime` replaces the 600s default. |
| Non-regression | existing `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` + trigger spawn tests | PASS — dispatch decision logic unchanged; only the spawn command gains the flag. |

Commands (pre-report): targeted `pytest` over the daemon + trigger spawn suites via the repo venv; `ruff check` AND `ruff format --check` on changed Python files.

## Risk / Rollback

- **Risk:** a generous lifetime means a genuinely-hung worker runs longer before termination; mitigated by the tight single-thread safety posture (per-role concurrency cap = 1, kill-switch, reap via WI-4857) and by keeping the values env-tunable.
- **Clean base:** `gtkb_dispatcher_daemon.py` (X1, commit 4e2f36119) and `cross_harness_bridge_trigger.py` (WI-4858, commit 026f7c2b7) are committed clean, so this builds without entangling uncommitted work.
- **Rollback:** single-commit revert removes the `--lifetime` injection; the 600s default returns. No KB mutation (`kb_mutation_in_scope: false`); append-only bridge history untouched.

## Bridge Filing

Filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4845-daemon-worker-lifetime-override`; no prior version rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs the worker-kill-mid-work defect (workers terminated at the 600s default because the daemon passed no override). No new capability surface beyond wiring an existing flag.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
