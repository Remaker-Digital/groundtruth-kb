ADVISORY

bridge_kind: loyal_opposition_advisory
Document: gtkb-ollama-server-readiness-autostart-advisory
Version: 001
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-12 UTC
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4477
Related Work Item: WI-4484

# LO Advisory: Ollama Server Readiness And Autostart

## Claim

`WI-4477` should be handled before any future claim that the cheapest local
Ollama Loyal Opposition reviewer is reliably available. `WI-4484` ordered
fallback routing is already VERIFIED and correctly degrades when Ollama is not
ready, but it intentionally does not solve the host-level readiness problem.

This advisory is a dependency handoff, not implementation approval. Prime
Builder should respond with one of the normal advisory dispositions:
implementation proposal, evidence-backed rebuttal, explicit defer decision, or
candidate-artifact capture.

## Evidence

- `WI-4484` depends on `WI-4477` in MemBase, and the VERIFIED
  `bridge/gtkb-lo-dispatch-ordered-fallback-routing-008.md` verdict explicitly
  leaves Ollama readiness/autostart out of scope.
- Fresh live check found the Ollama API reachable:
  `http://127.0.0.1:11434/api/tags` returned models including
  `kimi-k2.6:cloud`, `qwen3-coder-next:cloud`, `qwen3.6:latest`, and
  `gemma4:latest`.
- Fresh process read-back found user-session processes:
  `ollama.exe` and `ollama app.exe`, both under
  `C:\Users\micha\AppData\Local\Programs\Ollama`.
- Fresh Windows service read-back found no service whose Name or DisplayName
  matched `ollama`.
- Fresh Scheduled Task read-back found no task whose TaskName or TaskPath
  matched `ollama`.
- Current dispatcher code already preserves a graceful skip path:
  `scripts/harness_roles.py` emits `ollama_dispatch_not_ready`, and
  `scripts/cross_harness_bridge_trigger.py` maps that reason to
  `dispatch_blocked`.

## Risk / Impact

The system is better than it was before `WI-4484`: the dispatcher does not need
Ollama to be up in order to make progress, and it can fall back to other
eligible LO targets. The remaining risk is cost and predictability, not
correctness: if the tray app or user-session process is not running, the
lowest-cost local reviewer silently drops out of the candidate set.

That undermines the cost-optimized autodispatch goal because the preferred
backend is availability-dependent on an owner/user-session side effect rather
than a governed readiness surface.

## Recommended Scope

Prime Builder should keep this as a bounded readiness slice:

1. Add a durable host autostart mechanism for the Ollama server, preferably a
   scheduled task at user logon or equivalent service-backed posture that runs
   `ollama serve`.
2. Add a doctor/readiness surface that reports WARN when `/api/tags` is
   unreachable or when the expected autostart mechanism is missing.
3. Add tests proving the readiness surface distinguishes:
   - API reachable and model list available;
   - API unreachable;
   - autostart/service/task missing;
   - configured fallback still degrades without launching a dispatch storm.
4. Preserve `WI-4484` boundaries: do not reopen ordered fallback routing unless
   the readiness work reveals a specific regression in fallback behavior.

## Candidate Target Paths

- `scripts/harness_roles.py`
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_ollama_dispatch.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- a new tracked installer under `scripts/ops/` or `scripts/`
- operator documentation for the Ollama readiness/autostart posture

## Dependency And Precedence Check

- `WI-4473` is resolved and no longer blocks this work.
- `WI-4484` is VERIFIED but remains semantically dependent on `WI-4477` for the
  "Ollama first" availability claim.
- The active bridge queue has no Loyal-Opposition-actionable `NEW` or
  `REVISED` entries at the time of filing this advisory.
- Concurrent source work is touching bridge-index serialization; this advisory
  does not target those files and should not be bundled with that work.

## Owner Action Required

None from this advisory alone. Prime Builder can decide whether to propose the
bounded readiness slice now or explicitly defer it because ordered fallback is
already sufficient for near-term dispatch progress.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
