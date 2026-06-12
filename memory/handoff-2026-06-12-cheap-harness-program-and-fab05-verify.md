---
name: handoff-2026-06-12-cheap-harness-program-and-fab05-verify
description: Continuation handoff after a marathon session (workstation crash + recovery). FAB-21 HYG-028/025 VERIFIED; FAB-05 committed + report-005 awaiting manual LO VERIFY; emergency dispatch-storm kill-switch + watchdog LIVE (dispatch OFF); cheap-harness fix program scoped (WI-4472/4473/4476). Owner chose to start the fix program next.
metadata:
  type: project
author_identity: prime-builder
author_harness_id: B
author_session_context_id: 39746c1a-10a0-4914-a27c-dc4251c74b08
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context
---

# Continuation handoff — 2026-06-12 ~02:20Z (PB session 39746c1a, post-crash marathon)

Long multi-window session that survived a **workstation crash** (resource
exhaustion). Owner directive history: drive the Fable program; then diagnosed the
crash; then diagnosed why the cheap harnesses (Ollama/OpenRouter) weren't
dispatching. Owner's chosen next work: **start the cheap-harness fix program.**

## Done + committed this session

1. **FAB-21 HYG-028** stale-pointer sweep → VERIFIED `-010` (commit `bfddafbab`).
2. **FAB-21 HYG-025** glossary core/detail IA → VERIFIED `-012` (commit `30870b02f`).
3. **FAB-05** rule-file retirement (HYG-018/026/027/038):
   - Implementation committed `4d31fcf6b` (`docs:`) — 8 protected rule edits + 8
     narrative packets + 22 poller scripts archived to `archive/os-poller-2026-04-25/`
     + 4 Cursor files archived to `independent-progress-assessments/archive/cursor-legacy/`
     + inventory regen. WI-3278 + WI-3465 retired.
   - Post-impl report `-005` + grep-absence test (12/12) committed `1c5807c1f`.
   - **`NEW@-005` is in the live working-tree INDEX. FAB-05 awaits a MANUAL LO
     VERIFY** (auto-dispatch is OFF — see below). Applicability preflight PASSES.

## EMERGENCY FIX — LIVE + DURABLE (do not remove without the root-cause fix)

**Root cause of the crash:** the cross-harness dispatch trigger re-dispatches to a
target whose active-session lock is stale (`GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS`
= 120s). A dispatched session that **hangs** stops refreshing its lock → re-dispatch
→ cascade. The per-recipient circuit breaker only counts launch FAILURES, so
hung-but-launched sessions are never throttled and nothing caps total processes. At
~16:44 on 2026-06-11 this produced ~300 hung `codex` sessions (~45 GB) → crash.

**Two-layer fix in place:**
- **Kill-switch:** `GTKB_NO_CROSS_HARNESS_TRIGGER=1` set at **User** env scope →
  every NEW session's cross-harness trigger no-ops. **Cross-harness auto-dispatch
  is OFF.** Bridge round-trips need MANUAL Codex/Antigravity scans until re-enabled.
- **Watchdog:** Windows scheduled task `GTKB-HarnessStormWatchdog` (every ~1 min,
  survives reboot) runs `.gtkb-state/ops/harness_storm_watchdog.ps1` — if `codex`
  process count > 15, kills the codex-family storm + re-asserts the kill-switch +
  logs to `.gtkb-state/ops/storm-watchdog.log`. NEVER kills `claude`.
- To re-enable dispatch AFTER the root-cause fix lands: clear the User env var +
  disable/remove the watchdog task.

## Cheap-harness fix program (OWNER'S CHOSEN NEXT WORK)

All three backends are VERIFIED working; the blockers are precisely known:

- **WI-4473 (P1, ollama-harness):** `scripts/ollama_harness.py::load_routing_config`
  loads ALL `[models.*]` rows from the shared `.api-harness/routing.toml` and
  `validate_advertised_models` (line 167/242) checks every model_id against the local
  Ollama `/api/tags`. routing.toml now also has provider='openrouter' models
  (google/gemini-2.5-pro, qwen/qwen-2.5-coder-32b-instruct) → not local → harness
  aborts before any work. **FIX:** read+respect the per-model `provider` field; load/
  validate only `provider=='ollama'`. Ollama backend PROVEN good: `qwen3-coder-next:cloud`
  → "OK"; local models `qwen3.6:latest`/`gemma4:latest` are FREE → prefer local where
  capable, cloud otherwise.
- **WI-4472 (P1, bridge-dispatch):** hard concurrency cap in
  `scripts/cross_harness_bridge_trigger.py` spawn path — count live headless harness
  processes, skip dispatch (fail-closed, logged) when >= N. This is the durable storm
  fix that lets `GTKB_NO_CROSS_HARNESS_TRIGGER` be removed safely.
- **WI-4476 (P1, openrouter-harness):** point `.api-harness/routing.toml` openrouter
  models at **`deepseek/deepseek-v4-pro`** (OWNER-CONFIRMED; $0.44/$0.87 per M, 1.05M
  ctx). OpenRouter now WORKS (owner widened the account guardrail; DeepSeek/Qwen are
  eligible — **Gemini/GPT are NOT available on this account**). `openrouter_harness.py`
  needs NO code change (already reaches the API; was 404 only because the guardrail
  blocked the configured models). Just the routing.toml slug. Verified working slugs:
  deepseek-v4-pro, deepseek-v4-flash ($0.10/$0.20, 1M ctx, cheapest), qwen3-235b-a22b-
  thinking-2507 ($0.10/$0.10).
- **WI-4474 (P2):** promote `.gtkb-state/ops/harness_storm_watchdog.ps1` to tracked
  `scripts/ops/` via a bridge proposal.

**Sequence:** implement WI-4473 + WI-4472 → VERIFIED → lift the kill-switch → all 3
LO reviewers active (Ollama cheapest preferred precedence 10, OpenRouter/DeepSeek 30,
Codex 20 backstop). WI-4476 routing.toml is a trivial slug change.

**SETUP NEEDED FIRST:** `PROJECT-GTKB-OLLAMA-INTEGRATION` is RETIRED. WI-4472/4473/4476
need a project home (new project, or admit to an active one e.g.
`PROJECT-ARCHITECTURE-IMPROVEMENT`) + a PAUTH (owner-decision-backed) before any
implementation proposal. With dispatch OFF, proposals need MANUAL LO review.

## Gotchas / facts

1. **Dispatch is OFF (kill-switch).** Bridge VERIFY/review = manual Codex/Antigravity scans.
2. **Session-id duality:** bridge claims use the transcript-UUID `session_id`
   (`~/.claude/projects/E--GT-KB/<uuid>.jsonl`), NOT `CLAUDE_CODE_SESSION_ID`. Find the
   newest transcript; claim with `bridge_claim_cli.py claim <slug> --session-id <uuid>`.
3. **.env.local** has `OPENROUTER_API_KEY` + `OLLAMA_API_KEY` (both valid/working).
   Grep gotcha: `Select-String -SimpleMatch 'A|B'` matches the literal pipe — use `-match`.
4. **Google Drive backs up E:\GT-KB** (physical SSD); `.driveignore` excludes only
   `.git/` + the SQLite triple. Drive restores git-deleted files + makes `(1)` conflict
   copies → races git moves/deletes. Durable consideration: exclude more of the repo from
   Drive (git remote is the proper backup, per `.driveignore`'s own `.git/` rationale).
5. **gt CLI invocation:** `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; $env:GTKB_HARNESS_NAME='claude';`
   then `groundtruth-kb\.venv\Scripts\python.exe -c "import sys; sys.argv=['gt',...]; from groundtruth_kb.cli import main; main()"`.
   For multi-line args, use a small `.gtkb-state/` helper with `main()` (PowerShell quoting breaks the `-c` one-liner).
6. **impl-start gate:** protected `scripts/`+`platform_tests/` Write/Edit need a live
   FAB auth packet (`python scripts/implementation_authorization.py begin --bridge-id <id>`).
   Non-gated runtime ops can live under `.gtkb-state/`.
7. Many `.gtkb-state/_fab*.py` + `_*.py` helper scratch files exist (gitignored) — safe to leave.

## Continuation prompt (ready to paste)

```text
::init gtkb pb

Resume from session 39746c1a (2026-06-12). Read
memory/handoff-2026-06-12-cheap-harness-program-and-fab05-verify.md before acting.

Context: cross-harness auto-dispatch is OFF (emergency kill-switch
GTKB_NO_CROSS_HARNESS_TRIGGER=1 + GTKB-HarnessStormWatchdog task) after a
dispatch-storm crash. Bridge VERIFY/review is manual until the fix program lands.

Standing directive: drive the cheap-harness fix program to VERIFIED autonomously;
AUQ only for owner decisions.

FIRST: stand up a project home + PAUTH for WI-4472 (storm concurrency cap in
cross_harness_bridge_trigger.py) + WI-4473 (ollama_harness.py provider-scoped
model validation) + WI-4476 (routing.toml openrouter -> deepseek/deepseek-v4-pro).
PROJECT-GTKB-OLLAMA-INTEGRATION is retired; create/admit to an active project. Then
file the WI-4473 + WI-4472 bridge proposals (manual LO review since dispatch is off);
on GO, implement; drive to VERIFIED; then lift the kill-switch + disable the watchdog
so Ollama (cheapest, prefer local) / OpenRouter (deepseek-v4-pro) / Codex are all live.

ALSO PENDING: FAB-05 -005 awaits a manual LO VERIFY (NEW@-005 in live INDEX).
```

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
