---
author_identity: claude
author_harness_id: B
author_session_context_id: 28d30cb5-bfc4-4a97-acca-57d36d002533
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
---

# Handoff — 2026-06-12 — Backlog-triage program closed; WI-4472 proposal filed

## Program closeout (this session, interactive Prime 28d30cb5)

The directed program (priority fixes + backlog-triage Stages 0-3) is COMPLETE:
- WI-4459 dispatch livelock: VERIFIED, committed `16be9eb50` (concurrent session), resolved.
- WI-4461 Codex skill YAML: VERIFIED, committed `3281b07dd`, resolved.
- Stage 2 / WI-4456 disposition tool: VERIFIED, committed `324a6bc06` (WI left OPEN — 749-item `--apply` disposal is separate per-batch-AUQ work).
- Stage 3 / WI-4469 stop-the-leak: VERIFIED@-004, committed `ff51a5a4e`, **resolved** (closed out this session after the /loop session 544b584c implemented it but left commit+resolution incomplete).

Owner AUQ decisions this session: (1) Stage 3 strategy = approval-staged intake; (2) Stage 3 collision = yield to /loop session + verify; (3) next move = **continue solo, owner stops the /loop session**; (4) next item = **WI-4472**.

## Active: WI-4472 (P1 defect, dispatch-storm root-cause fix)

- Title: hard global concurrency cap on dispatched headless harness processes.
- Root cause: hung dispatched sessions stop refreshing their active-session lock → 120s TTL frees the target → re-dispatch; circuit breaker counts only launch FAILURES so hung-but-launched sessions are never throttled; nothing caps total live processes. 2026-06-11 incident: ~300 hung codex sessions, ~45GB.
- Authorization: linked WI-4472 to PROJECT-GTKB-RELIABILITY-FIXES; the standing PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is **project-wide** (empty included_work_item_ids → membership suffices; classes source/test_addition/hook_upgrade; DELIB-S351).
- **Filed `bridge/gtkb-cross-harness-dispatch-concurrency-cap-001.md` NEW@-001.** Both preflights GREEN (applicability preflight_passed:true; clause 0 blocking gaps). Awaiting Codex GO.
- **Design (target_paths = scripts/cross_harness_bridge_trigger.py + NEW platform_tests/scripts/test_dispatch_concurrency_cap.py):**
  - IP-1: in `_spawn_harness` (line ~1717) write a `<dispatch_id>.pid` sidecar after Popen; add `_pid_alive(pid)` (psutil → ctypes/os.kill fallback, fail-closed-to-not-alive) + `_count_live_dispatched_processes(runs_dir)` (pending `.exit_code` AND alive PID = live; prune dead/exited sidecars).
  - IP-2: env `GTKB_MAX_LIVE_DISPATCHED_PROCESSES` (default 8); early in `_spawn_harness` after dry_run, before authorization/Popen — if live>=cap, record `concurrency_cap_reached` to dispatch-failures.jsonl and return launched=False (no Popen). Fail-closed.
  - IP-3: new test file (clean test_addition); assert count semantics, cap skip (no Popen via sentinel), below-cap proceed (dry-run), env override + default fallback.
  - NOTE: `run_with_status.py` writes `<id>.exit_code` only on child EXIT, so hung children stay pending forever — that's why the count uses pending-AND-pid-alive.
- On GO: `implementation_authorization.py begin --bridge-id gtkb-cross-harness-dispatch-concurrency-cap`, implement IP-1/2/3, run new tests + ruff + git-stash-baseline no-regression on the existing flaky `test_cross_harness_bridge_trigger.py` (16 pre-existing unrelated failures — do NOT touch), file report → VERIFY.
- COLLISION CAUTION: this edits the LIVE dispatch path. Owner is stopping the /loop session; still claim the thread / watch for concurrent edits before implementing.

## Open captures this session
- WI-4471: work-intent claim doesn't cover in-flight implementation target_paths (concurrent-impl collision). Consideration, PROJECT-GTKB-RELIABILITY-FIXES.
- Post-VERIFIED closeout (commit + WI resolution) has no single owner across concurrent sessions — can silently stall (observed on Stage 3). Candidate sibling to WI-4471.
