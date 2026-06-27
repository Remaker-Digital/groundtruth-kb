NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d5a77c21-caee-404a-8fb3-6629ba276960
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal

# gtkb-wi4856-daemon-status-liveness-accurate — Derive daemon status from process liveness + heartbeat freshness, and mode from the active substrate

Document: gtkb-wi4856-daemon-status-liveness-accurate
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4856
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4856-LIVENESS-ACCURATE-STATUS
Recommended commit type: fix

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`collect_daemon_status` in `scripts/gtkb_dispatcher_daemon.py` (the `gt bridge dispatch daemon status` truth source) reports two stale values:

1. **`running` is derived from lock-file presence only** (`status["running"] = True` whenever `daemon.lock` exists, line 596-602). It computes `heartbeat_age_seconds` (line 608) but never uses it, and never calls the existing `daemon_process_alive(state_dir)` PID probe (line 214-226, added by WI-4855). Go-live surfaced the defect: after the daemon process died, status reported `running=True` off a **stale lock** with no liveness check.
2. **`mode` is hardcoded to `"shadow"`** (line 592). It never reads `_active_substrate(project_root)` (line 69-82). Go-live surfaced: the CLI showed `mode=shadow` while the running daemon's `status.json` showed `mode=live`.

This proposal makes daemon status liveness-accurate and substrate-derived, reusing the daemon's own existing helpers (`daemon_process_alive`, `_active_substrate`, the heartbeat-age computation) so the read path (`collect_daemon_status`) and write path (`run_tick`, line 456-457) share one truth source.

### Behavior change (precise)

In `collect_daemon_status`:

- **Running** becomes `running = pid_alive or (lock_present and heartbeat_fresh)` where `pid_alive = daemon_process_alive(state_dir)` and `heartbeat_fresh = heartbeat_age_seconds is not None and heartbeat_age_seconds <= HEARTBEAT_STALE_SECONDS`. A new env-configurable module constant `HEARTBEAT_STALE_SECONDS` (default 180s ≈ 3× the 60s default tick; env `GTKB_DISPATCHER_DAEMON_HEARTBEAT_STALE_SECONDS`) bounds freshness. The `lock` payload and `heartbeat_age_seconds` remain in the status dict for diagnostics; only the `running` derivation changes.
  - Live daemon (PID alive) → `running=True` (no regression).
  - Cleanly stopped daemon (PID file removed AND lock released by `stop`) → `running=False` (preserves the WI-4855 stop test at line 462).
  - Crashed daemon stranding a stale lock + dead/absent PID + stale heartbeat → `running=False` (the WI-4856 fix).
- **Mode** becomes `active_substrate = _active_substrate(project_root)`; `mode = "live" if active_substrate == DAEMON_SUBSTRATE else "shadow"`; and `status["active_substrate"] = active_substrate` is added. This mirrors `run_tick` exactly (line 456-457). With no `bridge-substrate.json`, `_active_substrate` returns `DEFAULT_SUBSTRATE` (`cross_harness_trigger`) → `mode="shadow"` (preserves the existing CLI status test at line 149).

In `groundtruth-kb/src/groundtruth_kb/cli.py` `bridge_dispatch_daemon_status_cmd`: the existing line already echoes `payload['mode']` (now correct). One human-readable line is added — `Active substrate: {payload.get('active_substrate')}` — so the human-readable CLI surfaces the substrate too (the `--json` path already surfaces it via the payload). No other CLI behavior changes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next append-only numbered bridge file.
- `GOV-17` — Automation script modification approval gate; modifies the dispatcher daemon automation script + its CLI surface; bridge-reviewed and owner-authorized (DELIB-20266203, PAUTH cited).
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher persistent-daemon architecture; status accuracy (liveness + mode) is part of the daemon's operability contract.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — cites governing specs; tests mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-4856 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — liveness/mode behavior maps to derived tests.
- `GOV-STANDING-BACKLOG-001` — WI-4856 is an authorized standing-backlog item under the active project.

## Prior Deliberations

- `DELIB-20266203` — owner clarification / grilled plan for the autonomous PB/LO loop; Q2 authorizes the full daemon fix-chain including WI-4856 (liveness-accurate status) as Phase X step X4; this deliberation is the cited owner-decision evidence for the Phase X work items.
- `DELIB-20266208` — owner AUQ (S20260627) reprioritizing WI-4862 ahead of X4/X5; confirms the X4→X5 sequence continues after WI-4862.
- WI-4855 (`bridge/gtkb-wi4855-daemon-process-lifecycle-hardening-*`) — added `daemon_process_alive` / `_pid_is_running`, the liveness primitives reused here.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4856-LIVENESS-ACCURATE-STATUS` (active; includes WI-4856 + GOV-17 + ADR-DISPATCHER-ARCHITECTURE-001; cites `DELIB-20266203`). The owner approved the full Phase X daemon fix-chain (DELIB-20266203 Q2), of which WI-4856 is step X4. No additional owner decision is required for this proposal.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement (WI-4856 acceptance) is that daemon status report `running` from heartbeat freshness / process liveness rather than lock presence alone, and that the reported mode / active substrate derive from the active substrate selection. DELIB-20266203 Q2 authorizes the fix. No new requirement; this corrects the status read path to meet the existing acceptance criteria.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| WI-4856(1): stale lock + dead PID + stale heartbeat does not report running | `test_status_running_false_on_stale_lock_dead_daemon` (new) | lock present, `daemon.pid`=an unused/dead PID, heartbeat older than `HEARTBEAT_STALE_SECONDS` → `collect_daemon_status(...)["running"]` is `False`. |
| WI-4856(1): live process reports running | `test_status_running_true_when_pid_alive` (new) | `daemon.pid`=`os.getpid()` (a live process) → `running` is `True`. |
| WI-4856(1): fresh heartbeat + lock reports running when PID absent | `test_status_running_true_when_lock_and_heartbeat_fresh` (new) | no/dead PID, lock present, heartbeat just written → `running` is `True`. |
| WI-4856(2): mode=live + active_substrate when substrate=dispatcher_daemon | `test_status_mode_live_when_substrate_daemon` (new) | `bridge-substrate.json` substrate=`dispatcher_daemon` → `mode=="live"` and `active_substrate=="dispatcher_daemon"`. |
| WI-4856(2): mode=shadow when substrate=cross_harness_trigger | `test_status_mode_shadow_when_substrate_cross_harness` (new) | substrate=`cross_harness_trigger` → `mode=="shadow"`. |
| Non-regression: clean stop reports not-running | existing `test_daemon..._stop...` (line 462) | unchanged — PASS. |
| Non-regression: CLI status default mode | existing `test_daemon_control_cli_status_reports_state` (line 149) | unchanged — PASS (no substrate file → shadow). |

Commands (pre-report): targeted `pytest` over `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` via the repo venv; `ruff check` AND `ruff format --check` on the changed files. PID-liveness is simulated deterministically (`os.getpid()` for alive; a never-allocated PID for dead); heartbeat freshness via direct `heartbeat.txt` timestamp writes; substrate via `bridge-substrate.json` fixtures (no daemon process spawned).

## Risk / Rollback

- **Risk:** a freshly-crashed daemon (stale lock + dead PID + heartbeat still within the freshness window) reports `running=True` transiently until the heartbeat ages past `HEARTBEAT_STALE_SECONDS`. Acceptable: a sub-3-minute-old daemon is genuinely ambiguous; the window self-clears. The previous behavior reported `running=True` **indefinitely** off a stale lock.
- **Interaction:** `start`'s single-instance guard (`cli.py` line 942: `read_daemon_status(...).get("running") or daemon_process_alive(...)`) now treats a stale-lock-only state as not-running, so a restart after a crash is no longer blocked by a stale lock — an improvement consistent with WI-4855's live-but-lockless detection.
- **Rollback:** single-commit revert restores lock-presence `running` and hardcoded `mode`. No KB mutation (`kb_mutation_in_scope: false`); append-only bridge history untouched.

## Recommended Commit Type

`fix` — repairs stale daemon-status reporting (lock-only running; hardcoded shadow mode). No new capability surface; reuses existing liveness/substrate helpers.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
