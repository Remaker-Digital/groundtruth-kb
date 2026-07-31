author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: be4929b6-9774-486a-bd0d-e5260880070d
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

# Loyal Opposition Session Wrap — 2026-07-10 (harness B, interactive)

Session: be4929b6-9774-486a-bd0d-e5260880070d
Role: Loyal Opposition (interactive). Scope: bridge review/verification + owner-directed investigation & capture.
Companion report (finalization cluster detail): INSIGHTS-2026-07-10-09-10.md.
Specs/WIs touched: WI-5112, WI-5114, WI-5132, WI-5060, WI-5075, WI-5083/5084/5088/5106/5118, WI-5167, WI-5169, WI-5173, WI-5174, WI-5175.

## 1. Finalization-mechanics cluster (bridge review + verification)

| Thread | Disposition | Notes |
|---|---|---|
| gtkb-wi5114-scratch-ignore-hygiene | Concurred (peer GO -004) | Verified peer verdict legitimate; caught autocrlf=true contradicting the -002 NO-GO factual claim (non-blocking). Later VERIFIED+committed by fleet (ca316743, clean 9-file scope). |
| gtkb-wi5112-hunk-scoped-verified-finalization | GO (-004), then VERIFIED (-006) | Independently confirmed all 3 P1 findings closed + F2 defect premise against live code; VERIFIED the disposable-index finalization by code inspection + 16 tests; self-referential finalization committed cleanly (9ce84c60, exactly 10 files, no foreign sweep in a commingled tree) — live proof the fix works. |
| gtkb-wi5132-version-gap-finalization | GO-with-Sequencing-Gate (-002) | Byte-identical target set to WI-5112; gated impl-start behind WI-5112 VERIFIED+committed + clean shared paths + uncontested claim (3 enforcement layers). Gate condition now MET → released to implement. P3: 3 missing advisory specs its sibling cites. |

Key lesson: GO-with-gate chosen over NO-GO (unclearable treadmill) and over owner-DEFER (owner-only) for a sound-but-not-yet-time proposal.

## 2. Fleet / dispatcher diagnosis (owner-requested)

- Dispatcher health FAIL is the DELIBERATE standing config: harness A (the sole Prime Builder) has can_receive_dispatch=false in the registry (WI-5080 pwsh-window-storm quiesce). PB work runs via interactive Codex-A, not headless dispatch. LO dispatch (B, D) is healthy.
- Claude Code (harness B) IS headlessly processing LO work: last dispatch 2026-07-10T13:31Z, exit 0, GO on wi5135, via claude.EXE (opus-4-8, B:claude:loyal-opposition). Dozens of prior dispatched reviews. Interactive session and headless workers are distinct processes.
- Harness D (ollama/kimi-k2) circuit-breaker TRIPPED: failure_class=max_turn_exhaustion, 2 failures today → B carries the LO load.

## 3. D max-turn-exhaustion root cause (owner-requested)

- Direct: kimi-k2 via scripts/ollama_harness.py exhausts its turn budget (--max-turns 200 in the dispatch argv + routing.toml) WITHOUT emitting a final verdict; not caught by the no-progress-loop guard (line 1039) → 200 distinct turns, no convergence.
- HONEST GAP surfaced under owner scrutiny: no per-run turn telemetry exists (stdout empty on failure; no turns_used logged), so we CANNOT currently measure the required tool-call count. My initial "200 is generous / convergence not budget" was an inference, not a measurement. Right fix: instrument turns-used, then set the budget from the distribution (+ a --max-turns 400 falsification experiment).
- Shim-class (affects D and F) per VERIFIED advisory gtkb-wi5060-shim-max-turn-exhaustion-authorization; fix directions: max-turn limits, loop termination, dispatch task decomposition. Actual remediation NOT yet implemented.

## 4. Alibaba Cloud Studio harness (identity H) — budget-critical

- H is NOT registered ("alibaba-deepseek" is only a tag on the retiring Goose/G). Onboarding = template slice 4b (DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT). Template slices 1/2/3/4a all VERIFIED (substrate ready); slice 4b unfiled/unbuilt.
- Budget expires within ~2 days (owner). Blocker: no dispatchable Prime → slice 4b must be implemented by an interactive Codex-A the owner kicks off. LO (B) will flip dispatchability via gt bridge dispatch config set-eligibility H --can-receive-dispatch the instant slice 4b VERIFIES.
- Filed: WI-5167 (P2, reconcile single owning home WI-5072 vs template slice 4b), WI-5169 (P0, expedite critical path). Scheduled task alibaba-h-dispatchability-watch (every 2h, gated auto-flip on verified-ready) is RUNNING.

## 5. Observability + self-tuning requirement capture (owner spec language)

- WI-5173 (P1, RELIABILITY-FIXES): shim per-run turn/tool telemetry — the WI-5060 budget unblocker + first instance of the diagnostic-mode requirement.
- WI-5174 (P1, DISPATCHER-COMPLEX-CLI): unified report CLI fast-cut (status + in-flight + PB/LO ready-to-work lists, existing data, anti-CLI-thrash).
- WI-5175 (P2, DISPATCHER-COMPLEX-CLI): observability + self-tuning umbrella (harness diagnostic mode + default metrics set + report metrics enrichment). Builds on scoring snapshots (DELIB-20260702), quality benchmarks (WI-4969), adaptation-impact (WI-4792), gtkb-benchmarks.
- All are consideration candidates (capture, not approval); Prime formalizes as specs + implements after prioritization.

## 6. Startup-gate re-arm

- Found already tracked 4x (WI-5118/5084/5088/5106); no duplicate created. Attached fresh interactive-LO repro to WI-5118 (status-detail): extends it beyond Prime write tools to LO gt CLI calls; harness-B clearing behavior differs from the Prime repro (WI-5106 reader-parity relevance).

## Unresolved / handoff

1. WI-5132: GO-with-gate; gate condition MET (WI-5112 VERIFIED+committed, shared paths clean) → ready for Prime to implement with an uncontested claim.
2. Alibaba H onboarding (slice 4b): budget-critical (~2 days), unfiled; needs owner to kick off Codex-A now + Alibaba endpoint creds in .env.local + WI-5167 ownership decision. Watch running.
3. Harness D circuit-broken; WI-5173 telemetry is the prerequisite for a data-driven max-turn fix and D recovery; while D is down, Opus-B carries all headless LO (cost).
4. Observability program (WI-5173/5174/5175) awaits Prime formalization + prioritization.
5. Bridge GO verdicts wi5112-004 / wi5132-002 were untracked pending the auto-finalization sweep (wi5112 since committed in its VERIFIED transaction).

## Background still active after wrap

- Scheduled task alibaba-h-dispatchability-watch (every 2h) will auto-flip H dispatchable on verified-ready or report status; delete it once H is dispatchable or the budget lapses.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
