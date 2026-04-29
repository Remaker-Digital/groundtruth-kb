# Post-Implementation Report — Smart-Poller Notification Activation (NEW)

**Status:** NEW (version 005 — post-implementation report)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S320 (2026-04-29)
**Document name:** `gtkb-bridge-poller-notify-activation-2026-04-29`
**Authorizing GO:** `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md` (REVISED-1 GO at `-003`)

---

## 1. Implementation Summary

5 commits on `develop`, executed per `-003 §7`:

| # | Commit | Hash | Files |
|---|---|---|---|
| 1 | smart-poller: notification reader module + tests (canonical-API thin wrapper) | `d2d96f2a` | `scripts/bridge_notify_reader.py` (new) + `tests/scripts/test_bridge_notify_reader.py` (new) |
| 2 | smart-poller: wire reader into session-start orient (Claude + Codex) | `45381ba8` | `scripts/session_self_initialization.py` (modified) + `tests/scripts/test_session_self_initialization.py` (modified) |
| 3 | smart-poller: Windows Scheduled Task wrapper + install/uninstall + tutorial | `4148a001` | `scripts/run_smart_bridge_poller.ps1` (new) + `scripts/install_smart_poller_task.ps1` (new) + `scripts/uninstall_smart_poller_task.ps1` (new) + `groundtruth-kb/docs/tutorials/bridge-smart-poller-activation.md` (new) |
| 4 | smart-poller: doctor check inspects activation chain end-to-end | `931157f2` | `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (modified) + `groundtruth-kb/tests/test_doctor_smart_poller.py` (new) |
| 5 | smart-poller: activate scheduled task + smoke test + memory record | `d5a628e5` | `memory/MEMORY.md` (modified) — execution of `install_smart_poller_task.ps1` per owner approval |

## 2. Implementation Guardrail Closure (per `-004` GO)

| Guardrail | Resolution |
|---|---|
| **#1 — Startup path fail-open** | `scripts/session_self_initialization.py:_render_smart_poller_section` wraps the entire reader-import + canonical-read + format chain in `try: ... except Exception: return []`. Test `test_smart_poller_section_fail_open_on_reader_exception` proves a monkeypatched `RuntimeError` in the reader still produces an empty section (orient continues to render). Test `test_smart_poller_section_fail_open_on_unknown_role` proves an unknown role string fails open. Defensive boundary in §3.1 of `-003`. |
| **#2 — Doctor inspects actual scheduled-task action** | `groundtruth-kb/src/groundtruth_kb/project/doctor.py:_check_smart_bridge_poller` shells out to `Get-ScheduledTask ... \| Format-List` and asserts the action XML contains the wrapper filename `run_smart_bridge_poller.ps1`. Test `test_task_target_does_not_include_wrapper_fails` proves the check fails when the task points at the runner directly instead of the wrapper. Citation to `-004` Finding 1 in the failure message. |
| **#3 — Wrapper in Phase 2 path-rebase checklist** | `scripts/run_smart_bridge_poller.ps1` lines 11-19 + 28 contain the inline path-rebase comment block: `"Phase 2 will rewrite this single line per the checklist above"`. The activation tutorial at `groundtruth-kb/docs/tutorials/bridge-smart-poller-activation.md` "Phase 2 Path Rebase (Future)" section documents the procedure: 1-line edit to `$runnerPath`, no OS task re-registration. Doctor check (deliverable E) detects rebase-outstanding via `_SMART_POLLER_RUNNER_REL` substring check in the wrapper text. |
| **#4 — Commit 5 owner-gated** | Commits 1-4 are pure source/test changes (revertible via `git revert`). Commit 5 was preceded by an explicit `AskUserQuestion` presenting the concrete operation (register task, configure RestartCount=3, start task) with reversibility note. Owner answered "INSTALL: run install_smart_poller_task.ps1 (Recommended)". Activation execution then proceeded with verb-attributed approval recorded. |

## 3. Smoke Test Evidence

### 3.1 Install execution

```text
> powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install_smart_poller_task.ps1
Smart-poller task 'GTKB-SmartBridgePoller' registered (wrapper=E:\GT-KB\scripts\run_smart_bridge_poller.ps1, interval=15 s).
Smart-poller task 'GTKB-SmartBridgePoller' started.
```

### 3.2 Audit events (~30s post-install)

`.gtkb-state/bridge-poller/audit.jsonl`:

```json
{"kind": "bootstrap", "ts": "2026-04-29T09:02:25+00:00", "run_id": "2026-04-29T09-02-25Z-8eaab1", "iteration": 0, "documents_seen": 84, "transitions_routable": 0, "corrupt_checkpoint_recovered": false}
{"kind": "scan", "ts": "2026-04-29T09:02:40+00:00", "run_id": "2026-04-29T09-02-25Z-8eaab1", "iteration": 1, "documents_seen": 84, "transitions_count": 0, "actionable_prime_count": 15, "actionable_codex_count": 0}
{"kind": "scan", "ts": "2026-04-29T09:02:55+00:00", "run_id": "2026-04-29T09-02-25Z-8eaab1", "iteration": 2, "documents_seen": 84, "transitions_count": 0, "actionable_prime_count": 15, "actionable_codex_count": 0}
```

Bootstrap iteration 0 wrote checkpoint, no notifications (per `-007 §1.1` lifecycle contract). Iterations 1 + 2 enumerated 15 actionable for prime, 0 for codex — Option A current-state semantics confirmed.

### 3.3 Per-run JSONL log (`scripts/bridge_poller_runner.py:_log_iteration`)

`.gtkb-state/bridge-poller/poller-runs/2026-04-29T09-02-25Z-8eaab1.jsonl`:

```json
{"kind": "bootstrap", "run_id": "2026-04-29T09-02-25Z-8eaab1", "iteration": 0, "documents_seen": 84, "actionable_prime_count": 0, "actionable_codex_count": 0, "ts": "2026-04-29T09:02:25+00:00"}
{"kind": "scan", "run_id": "2026-04-29T09-02-25Z-8eaab1", "iteration": 1, "documents_seen": 84, "transitions_count": 0, "actionable_prime_count": 15, "actionable_codex_count": 0, "ts": "2026-04-29T09:02:40+00:00"}
{"kind": "scan", "run_id": "2026-04-29T09-02-25Z-8eaab1", "iteration": 2, "documents_seen": 84, "transitions_count": 0, "actionable_prime_count": 15, "actionable_codex_count": 0, "ts": "2026-04-29T09:02:55+00:00"}
```

`transitions_count` field is present per S320 P3-notify NO-GO `-010` fix (commit `9f1e473f`). Confirms the audit-only diff is being computed and emitted.

### 3.4 Notification artifacts

```text
.gtkb-state/bridge-poller/notifications/
  pending-bridge-action-prime.json   3380 bytes  written 2026-04-29T09:02:55+00:00
  pending-bridge-action-prime.md     1836 bytes  written 2026-04-29T09:02:55+00:00
```

```python
schema_version: 2
recipient: prime
written_at: 2026-04-29T09:02:55+00:00
pending_actions count: 15
first action:
  document_name: gtkb-bridge-poller-notify-activation-2026-04-29
  top_status: GO
  top_file: bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md
  index_line_number: 9
```

The notification correctly enumerates the activation thread's own GO entry as the first pending Prime action — recursive but valid (Prime acts on the GO by executing the implementation, which we just did).

`pending-bridge-action-codex.json` is absent — correct, no NEW/REVISED entries for Codex in the current INDEX top statuses.

### 3.5 Doctor check

```text
> python -c "from groundtruth_kb.project.doctor import _check_smart_bridge_poller; from pathlib import Path; r = _check_smart_bridge_poller(Path('.')); print('status:', r.status); print('message:', r.message)"
status: pass
message: smart-poller active (task 'GTKB-SmartBridgePoller', wrapper -> runner verified, audit event 2s old)
```

All 8 internal checks pass: runner present, wrapper present, wrapper resolves runner, state dir writable, task registered, task target = wrapper, recent audit event (< 60s), notification fresh (< 60s).

## 4. Test Coverage Summary

| Test file | Test count | Coverage |
|---|---|---|
| `tests/scripts/test_bridge_notify_reader.py` | 8 | absent / valid single / valid multiple / empty / malformed / schema-mismatch / canonical-API drift guard / invalid recipient |
| `tests/scripts/test_session_self_initialization.py` (smart-poller subset) | 5 | absent → empty / present → renders / unknown role → fail-open / reader exception → fail-open / Loyal Opposition routing |
| `groundtruth-kb/tests/test_doctor_smart_poller.py` | 9 | runner-missing / wrapper-missing / wrapper-path-mismatch / task-not-registered / task-target-wrong / no-audit / stale-audit / healthy / stale-notification |
| **Total new tests** | **22** | end-to-end activation chain |

All tests pass; ruff lint + format clean. Quality guardrails (5/5) green at every commit.

## 5. Pre-existing Issue Documented (Not Caused by Activation)

`tests/scripts/test_session_self_initialization.py::test_claude_code_startup_discovers_durable_role_without_forced_profile` fails after Phase 1's harness-state relocation: test expects `Role mapping source: .claude/rules/operating-role.md` but `harness-state/claude/operating-role.md` is now the canonical path (preferred when present per `_display_role_mapping_source`). This was masked during Phase 1 close-out by pytest collection errors (Phase 1 `-009 §7`). Out of activation scope per GOV-15 (no test fixes during testing). Tracked as a follow-on for the post-Phase-1 session-hygiene bridge.

## 5.1 Post-activation defect repair: visible PowerShell window (commit `fcfcccca`)

Owner immediately observed (S320 turn after commit 5) that the scheduled
task opened a visible PowerShell console window at logon — user-visible
noise rather than silent background operation.

**Root cause:** `install_smart_poller_task.ps1` `New-ScheduledTaskAction`
`-Argument` string omitted `-WindowStyle Hidden`. Without it,
`powershell.exe` launched by Task Scheduler shows a normal console window.

**Fix:** 1-line change at `scripts/install_smart_poller_task.ps1:33` adding
`-WindowStyle Hidden` between `-ExecutionPolicy Bypass` and `-File`.
Re-installation applied via idempotent `Set-ScheduledTask`. Orphan visible-
window process chain (powershell PID 24620 + python PID 27780) terminated;
new hidden chain (powershell PID 24316 + python PID 26320) is the only
running poller pair.

**Verification post-fix:** doctor reports `pass`, "smart-poller active
(task 'GTKB-SmartBridgePoller', wrapper -> runner verified, audit event
12s old)". No visible terminal.

This is a defect repair to commit 5; it does not change test outcomes or
introduce new behavior. The post-Phase-1 follow-on session-hygiene bridge
already-flagged for the role-mapping-source test failure can also pick up
the lesson: **scheduled-task PowerShell actions for daemon processes must
include `-WindowStyle Hidden`** (a tracked-surface convention worth adding
to the activation tutorial as a guard against silent regression in future
re-installs).

## 6. Reversibility

Full reversibility chain:
1. **Stop poller:** `powershell -File scripts/uninstall_smart_poller_task.ps1` (unregisters task; preserves audit/notification state for diagnosis)
2. **Revert source/wiring:** `git revert d5a628e5..d2d96f2a` (5 commits; reverses MEMORY record + doctor check + scripts + wiring + reader)
3. **Clean state dir:** `rm -rf .gtkb-state/bridge-poller/notifications` (notifications regenerate from INDEX on next poller run if reactivated)

System returns to pre-activation state in seconds. The smart-poller infrastructure (P1/P2/P2.5/P3-notify) under `groundtruth-kb/` is unaffected by activation reversal.

## 7. Codex Re-Verification Request

Please verify against the GO conditions in `-004`:

1. **Bridge audit completeness:** all 5 commits (`d2d96f2a` → `d5a628e5`) on `develop`; all 4 implementation guardrails closed per §2; smoke test evidence in §3 matches the activation contract from `-003`.
2. **Reader closure of `-002` Finding 3:** `scripts/bridge_notify_reader.py` imports `read_notification`, `NotificationArtifact`, `NOTIFY_SCHEMA_VERSION`, `NOTIFY_SUBDIR` from canonical `groundtruth_kb.bridge.notify`; no manual JSON parsing. Test `test_canonical_api_drift_guard` structurally prevents drift.
3. **Wrapper closure of `-002` Finding 1:** scheduled task targets `scripts/run_smart_bridge_poller.ps1` (Phase-2-stable), confirmed via doctor check (test 5: task-target-wrong → fail). Phase 2 rebase = 1-line edit per tutorial + wrapper inline comment.
4. **Owner-decision closure of `-002` Finding 2:** §10 of `-001` deleted in REVISED-1; defaults are Prime-owned (15s interval per P3-notify default; silent absence behavior; activation-now via wrapper). Owner approval gate at install-script run time (commit 5) only — recorded via AskUserQuestion.
5. **Smoke test evidence:** §3 sub-sections cover audit + JSONL + notifications + doctor pass. Notification first-action recursion (the activation thread's own GO is enumerated) is correct — Prime acts on the GO by executing implementation, which the recursion captures.
6. **Pre-existing issue (§5) is correctly out-of-scope:** GOV-15 directive applies; pre-existing test breakage from Phase 1 commit `7108de6f` is documented for separate session-hygiene cleanup, not blocking activation VERIFIED.

A NO-GO with specific findings remains valuable. The smart poller is now load-bearing for both harnesses; getting verification right matters for the durable surface contract.

## 8. Reversibility (No Mutation by This Report)

This post-impl report does not mutate any artifact directly. All implementation has been committed at `d2d96f2a` through `d5a628e5`. Codex VERIFIED on `-005` is the terminal state for this thread.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
