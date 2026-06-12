---
name: handoff-2026-06-12-cheap-harness-program-progress-and-wi4472-collision
description: Cheap-harness fix program progress (resume of session 39746c1a). WI-4473 proposal FILED (awaiting manual LO); WI-4473/4476 admitted to the existing reliability fast-lane; WI-4472 IMPLEMENTED by me but Antigravity concurrently filed the canonical post-impl report -005 (WI-4471 collision). Kill-switch + watchdog STILL ON (do not lift).
metadata:
  type: project
author_identity: prime-builder
author_harness_id: B
author_session_context_id: c6f54cd8-c03e-4eda-bb2f-97d2c392b40f
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context
---

# Continuation handoff — 2026-06-12 ~04:30Z (PB session, cheap-harness program)

Resume of session 39746c1a per `handoff-2026-06-12-cheap-harness-program-and-fab05-verify.md`.
Owner directive: drive cheap-harness fix program (WI-4472/4473/4476) to VERIFIED
autonomously; AUQ only for owner decisions. Cross-harness dispatch OFF
(`GTKB_NO_CROSS_HARNESS_TRIGGER=1` + `GTKB-HarnessStormWatchdog`); bridge VERIFY/review is MANUAL.

## SETUP — already existed; handoff was stale (interrogative-default win)

The handoff said "stand up a project + PAUTH for WI-4472/4473/4476." **It already
exists:** `PROJECT-GTKB-RELIABILITY-FIXES` + `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
(the reliability fast-lane; owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`,
governed by `GOV-RELIABILITY-FAST-LANE-001`). The PAUTH is **membership-based**:
`included_work_item_ids: null`, scope_summary "covers work items by active project
membership (no per-fix authorization)"; classes `source` + `test_addition` + `hook_upgrade`;
forbids `deploy`/`git_push_force`/`spec_deletion`. So **admission = authorization** — no
new project/PAUTH needed (would have been duplicate-authority drift).

- Admitted **WI-4473** + **WI-4476** to PROJECT-GTKB-RELIABILITY-FIXES via `gt projects add-item`
  (WI-4472 was already a member). Grooming, not implementation authority.

## WI-4473 (ollama provider-scoped validation) — PROPOSAL FILED, awaiting manual LO

- Root cause: `scripts/ollama_harness.py::load_routing_config` builds a `ModelRoute` for
  EVERY `[models.*]` row; `validate_advertised_models` checks all against local `/api/tags`.
  routing.toml now has `provider="openrouter"` rows → not local → exit 1 (508 failures).
  **Fix:** add provider filter mirroring `scripts/openrouter_harness.py:186-188`
  (`provider = row.get("provider", "ollama"); if provider != "ollama": continue`).
  Absent→"ollama" default (backward compat; openrouter uses strict `!= "openrouter"`).
  openrouter_harness.py is ALREADY provider-aware — fix isolated to ollama_harness.py.
- Filed `bridge/gtkb-ollama-harness-provider-scoped-model-validation-001.md` (NEW).
  Both preflights GREEN (applicability packet `sha256:6eeaa67c...`; clause exit 0).
  Cites `GOV-RELIABILITY-FAST-LANE-001` + Standing Fast-Lane Eligibility from the outset
  (the lesson from WI-4472's -002 NO-GO). Target paths: ollama_harness.py + new
  `platform_tests/scripts/test_ollama_provider_scoped_routing.py`. **NOT yet implemented;
  awaits manual LO GO** (dispatch OFF).

## WI-4472 (dispatch concurrency cap) — IMPLEMENTED BY ME, but CONCURRENT-COLLISION (WI-4471)

- Thread reached **GO@-004** (Antigravity/C as LO) DURING this turn. I minted the
  impl-start packet (`sha256:7377e8bf...`) and implemented the GO'd proposal -003:
  4 edits to `scripts/cross_harness_bridge_trigger.py` (constants + `_max_live_dispatched_processes`
  + `_pid_alive` + `_count_live_dispatched_processes` + `_safe_unlink` + cap gate in
  `_spawn_harness` after dry_run + `.pid` sidecar after Popen) + new
  `platform_tests/scripts/test_dispatch_concurrency_cap.py` (15 tests, all pass).
  Verified: 15/15 new; existing suite 29 failed/39 passed = HEAD baseline (NO regression,
  proven via backup→`git checkout HEAD`→measure→restore); `ruff format --check` clean;
  `ruff check` = 1 PRE-EXISTING B007 (`legacy_recipient` ~line 2421, in HEAD at 2278,
  unrelated, NOT fixed per fast-lane no-cleanup).
- **COLLISION:** Antigravity/C (session 614a39b8) concurrently filed the canonical
  post-impl report **`bridge/gtkb-cross-harness-dispatch-concurrency-cap-005.md` (NEW)**
  at ~21:24 local. My post-impl filer **failed-closed** (`validate_transition` blocks
  NEW-after-NEW; correct). Thread is now **NEW@-005 awaiting manual LO VERIFY** (LO queue,
  not Prime-actionable).
- **Tree/report mismatch:** the working tree has MY minimal impl (distinctive comments
  present; 29/39 existing). Antigravity's -005 CLAIMS 68/68 + a `run_trigger` dry_run
  change that is **NOT in the tree** (only my 148/3 diff). A proper LO VERIFY that re-runs
  the commands will get 29/39 + B007, contradicting -005 → expect NO-GO → corrected re-file.
  I did NOT overwrite -005 or the tree; reverting my edits would leave NO cap impl.
- My accurate-to-tree post-impl draft is parked at `.gtkb-state/_wi4472-postimpl-draft.md`
  (unfiled; slot taken).

## STATE / NEXT

- **OWNER DECISION (2026-06-12, AUQ):** on the WI-4472 collision — **"Let the bridge
  self-correct"**: keep my verified cap in the tree, do NOT disturb Antigravity's -005,
  let the manual LO VERIFY catch the report/tree mismatch (expected NO-GO on re-run →
  corrected report follows). I stood down on WI-4472. My accurate draft stays parked
  (unfiled) at `.gtkb-state/_wi4472-postimpl-draft.md` in case a corrected re-file is needed later.
- **Kill-switch + watchdog STILL ON.** WI-4472 NOT VERIFIED. Do NOT lift until VERIFIED
  AND owner-confirmed (separate gated step).
- Next actionable (Prime): none on WI-4472 (LO's turn). WI-4473 awaits manual LO GO → then
  implement. WI-4476 = routing.toml openrouter slug → `deepseek/deepseek-v4-pro` (trivial;
  owner-sequenced after kill-switch lift; note routing.toml is `.toml` config — confirm it
  maps to an allowed mutation class before its impl).
- Owner should be aware the multi-harness swarm is producing WI-4472-class collisions
  (validates WI-4471). Consider pausing peer Prime harnesses on shared threads while dispatch
  is off, OR landing WI-4471 (work-intent claim covering in-flight target_paths).

## REFRAME (owner directive 2026-06-12): top-priority program, peer with Fable

Owner: "reframe cost-optimized automatic dispatch as top-priority work, peer with the
Fable program; want it working ASAP." Enacted:

- Created **`PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`** ("Cost-Optimized Automatic Bridge
  Dispatch"), **rank=1** (top tier; peer of `PROJECT-FABLE-INVESTIGATION` which is the
  Fable FAB-01..23 program). Members (dual membership; reliability fast-lane PAUTH preserved
  via PROJECT-GTKB-RELIABILITY-FIXES): **WI-4472** (storm cap), **WI-4473** (ollama provider
  bug), **WI-4476** (openrouter slug→deepseek-v4-pro), **WI-4474** (watchdog promotion, P2),
  **WI-4477** (NEW: ollama-server readiness — `/api/tags` connection refused = local Ollama
  server DOWN; cheapest reviewer unavailable even after WI-4473's code fix; depends-on WI-4473).
- Coordinates with **FAB-01 (WI-4413)** "Restore bridge dispatch launchability" in the Fable
  program (adjacent; don't duplicate).

### PROGRESS UPDATE 2026-06-12 ~05:45Z (both GO'd items IMPLEMENTED this session)

- **WI-4472 storm cap → VERIFIED@-010.** The bridge self-corrected (per owner decision): -005→GO-006→NEW-007→NO-GO-008→NEW-009→VERIFIED-010. DONE.
- **WI-4473 ollama provider fix → IMPLEMENTED + REPORTED.** GO@-002 (Antigravity LO) → claimed + packet `sha256:a6a2865…` → edited `scripts/ollama_harness.py` (9-line provider filter) + new `test_ollama_provider_scoped_routing.py` (6 tests). Verified: 6/6 new, 38/38 existing ollama regression, ruff check+format clean. Post-impl report filed **NEW@-003** → awaits manual LO VERIFY.
- **WI-4476 openrouter→DeepSeek → IMPLEMENTED + REPORTED + LIVE-VERIFIED.** GO@-002 → packet `sha256:b2f978e…` → edited `.api-harness/routing.toml` (gemini/qwen → `deepseek/deepseek-v4-pro` + `deepseek-v4-flash`, default+skills) + new `test_openrouter_routing_deepseek.py` (6 tests). Verified: 6/6, ruff clean, **LIVE OpenRouter call HTTP 200** (deepseek-v4-pro replied "OK", tool accepted — 404 class CLOSED). Post-impl report filed **NEW@-003** → awaits manual LO VERIFY.
- Working tree (uncommitted, per discipline): `M scripts/ollama_harness.py`, `M .api-harness/routing.toml`, `?? test_ollama_provider_scoped_routing.py`, `?? test_openrouter_routing_deepseek.py`, + the WI-4472 tree changes.

### ✅ PROGRAM COMPLETE 2026-06-12 ~05:55Z — AUTO-DISPATCH RE-ENABLED

All 3 core blockers VERIFIED (WI-4472@-010, WI-4473@-004, WI-4476@-004; WI-4476 verdict
independently confirms live HTTP 200 + tool-calling on deepseek-v4-pro). Verified work
committed to `develop` by a concurrent sweep-commit (`17c7672e4` cap (WI-4472), `bb40cab85`
WI-4473+WI-4476+tests) — confirmed HEAD contains the cap, the `provider != "ollama"` filter,
and the deepseek routing.toml models.

**Owner AUQ (2026-06-12) → "Full re-enable, watchdog off". EXECUTED:**
- `GTKB-HarnessStormWatchdog` scheduled task → **Disabled** (reversible: `Enable-ScheduledTask`).
- `GTKB_NO_CROSS_HARNESS_TRIGGER` User-scope env var → **CLEARED**. Cross-harness auto-dispatch
  is ON for new sessions. Storm protection now relies SOLELY on the verified concurrency cap
  (default 8, `GTKB_MAX_LIVE_DISPATCHED_PROCESSES`).
- Dry-run verification (kill-switch unset): trigger `skipped=False`, would dispatch pending
  Prime work batched 2/fire, globally capped 8 (raw_pending 39 → bounded). Functional.
- **Activation semantics:** durable re-enable is live for NEW sessions; resumes as the owner's
  running sessions cycle/restart. THIS interactive session retains the process-scope var (=1)
  so it stays inert (won't burst mid-conversation). A fresh session dispatches immediately.
- Cost-optimization routing (precedence Ollama 10 / OpenRouter-DeepSeek 30 / Codex 20 backstop)
  configured; both cheap backends now fixed + verified.

### Remaining (non-blocking)
- **WI-4477** ollama server reliability (open; graceful-skip means it doesn't block dispatch).
- Watchdog is OFF — re-enable with `Enable-ScheduledTask -TaskName GTKB-HarnessStormWatchdog`
  if a storm safety-net is wanted back. The cap is the primary protection.

### (historical) Remaining path to working cost-optimized auto-dispatch

1. **WI-4473 + WI-4476** post-impl reports (both NEW@-003) → **need manual LO VERIFY** (last code gate).
2. **WI-4477** ollama server reliability (investigated; needs proposal) — does NOT block re-enable (dispatch degrades gracefully when ollama down; codex+openrouter still serve).
3. **ENABLEMENT GATE (owner-gated AUQ):** once WI-4473 + WI-4476 VERIFIED → lift `GTKB_NO_CROSS_HARNESS_TRIGGER` + disable `GTKB-HarnessStormWatchdog`. WI-4472 cap is already VERIFIED, so re-enable is safe once the two LO VERIFYs land.

### (historical) Critical path to working cost-optimized auto-dispatch

1. **WI-4473** ollama provider fix — proposal NEW@-001 filed → **needs manual LO GO** → I implement → VERIFIED.
2. **WI-4472** storm cap — implemented+verified in tree; report -005 (Antigravity's) + GO@-006 confused verdict → **needs manual LO VERIFY** (let-bridge-self-correct). Gates kill-switch lift.
3. **WI-4477** ollama server up + readiness check. **INVESTIGATED (recorded on WI-4477):** server INTERMITTENT (up now HTTP 200, was down 22:40Z); CLI at `…\Programs\Ollama\ollama.exe`; NO service/task (manual/app start); dispatch degrades gracefully (readiness probe skips ollama when down). Recommended: host autostart (`ollama serve` scheduled task/service) + doctor WARN surface. Needs proposal+GO to implement.
4. **WI-4476** openrouter routing.toml → DeepSeek. **PROPOSAL FILED** `bridge/gtkb-openrouter-routing-deepseek-cost-optimization-001.md` (NEW; both preflights green) → needs manual LO GO. Live-verified exact slugs: `deepseek/deepseek-v4-pro` ($0.44/$0.87, 1.05M ctx), `deepseek/deepseek-v4-flash` ($0.10/$0.20). `.api-harness/routing.toml` is NOT gate-protected (GO authorizes the edit; no impl-start packet needed for it); the new test is `test_addition` (fast-lane PAUTH covers). No test pins the model strings (FAB-01 hits are harness-type axes). Draft: `.gtkb-state/_wi4476-proposal-draft.md`.
5. **Enablement gate (owner-confirmed):** when WI-4472 VERIFIED + WI-4473 done + ollama up + WI-4476 done → lift `GTKB_NO_CROSS_HARNESS_TRIGGER` + disable `GTKB-HarnessStormWatchdog` → 3 backends dispatch (Ollama 10 / OpenRouter-DeepSeek 30 / Codex 20).

### BINDING CONSTRAINT = manual LO review (dispatch is OFF, chicken-and-egg)

Auto-dispatch is off, so the fixes that re-enable it need MANUAL LO review for GO/VERIFIED.
Manual LO sessions are running (~14 verdicts/hr) but haven't reached WI-4473's NEW@-001 yet.
Highest-leverage action: point a manual Codex/Antigravity LO scan at WI-4473 (NEW@-001) +
WI-4472 (report). The storm cap is ALREADY in the tree, so storm protection exists in code
now — but keep the kill-switch until WI-4472 is VERIFIED (do not re-enable dispatch early).

## Gotchas learned this turn

- `revise_bridge.py file` ONLY files REVISED-after-NO-GO. Post-impl report (NEW-after-GO)
  uses `scripts/gtkb_bridge_writer.py` primitives: `validate_transition(slug,"NEW",PRIME_ROLE_SLOT,root)`
  (line 336 allows NEW after GO) → `next_file_number` → `write_bridge_file` → `insert_index_status`.
- bridge-propose helper `propose_bridge(slug, body, pre_populate_prior_deliberations=False)`
  to avoid the `<fill in reason>` placeholder injection when you author your own Prior
  Deliberations. Set `GTKB_SESSION_ID` env for the work-intent claim.
- Author metadata: include all 6 fields in the body (`ensure_author_metadata` validates).
- Use canonical `## Specification Links` heading exactly (preflight `SPEC_LINK_HEADING_RE`
  won't match "Carried-Forward Specification Links").

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
