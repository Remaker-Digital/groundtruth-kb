ADVISORY

bridge_kind: loyal_opposition_advisory
Document: gtkb-ollama-cloud-routing-sot-drift-advisory
Version: 001 (ADVISORY)
Author: Loyal Opposition (Codex, session envelope LO)
Date: 2026-06-18 UTC
Work Item: WI-4669
Source Spec: GOV-SOURCE-OF-TRUTH-FRESHNESS-001
Affected Paths: [".claude/rules/canonical-terminology.md", "groundtruth-kb/docs/reference/canonical-terminology-detail.md", ".claude/rules/operating-model.md", ".api-harness/routing.toml"]

# Advisory: Ollama / OpenRouter Routing Canonical-Record Drift

## Claim

`WI-4669` correctly captures a live source-of-truth freshness defect, but its
current backlog posture is too low-visibility for an active dispatch-diagnosis
surface. The canonical terminology and operating-model records still describe
the Ollama harness as a local open-weight / single-model Phase-1 setup, while
live routing and verified bridge work show the current system is provider-aware,
cloud-backed for the default Ollama review route, and includes the OpenRouter F
harness.

This drift has already produced operator confusion: `provider_failure_backoff_active`
was interpreted as a local Ollama server issue, but the active default review
model is `kimi-k2.7-code:cloud`, so that failure class can be a cloud-provider
auth/rate-limit/outage condition.

## Evidence

Live `.api-harness/routing.toml`:

- `[routing.ollama].default_model = "kimi-k2-7-code-cloud"`.
- `[routing.ollama.skills].bridge-review = "kimi-k2-7-code-cloud"`.
- `models.kimi-k2-7-code-cloud.model_id = "kimi-k2.7-code:cloud"`,
  `provider = "ollama"`.
- Additional Ollama-provider cloud rows exist for
  `qwen3-coder-next:cloud` and `kimi-k2.6:cloud`; one local row remains
  `qwen3.6:latest`.
- `[routing.openrouter].default_model = "deepseek-v4-pro"` and skill routes
  point to `deepseek-v4-pro`.

Stale active records:

- `.claude/rules/canonical-terminology.md:1117` says Ollama "Locally hosts
  open-weight models" via localhost.
- `.claude/rules/canonical-terminology.md:1131` says routing maps
  "Ollama-served local models".
- `groundtruth-kb/docs/reference/canonical-terminology-detail.md:1164`
  through `:1165` repeats the local open-weight framing.
- `groundtruth-kb/docs/reference/canonical-terminology-detail.md:1187`
  through `:1188` repeats the "Ollama-served local models" framing.
- `.claude/rules/operating-model.md:104` says static routing has a single
  Phase-1 model, "Qwen 2.5 Coder 14B", and says there is no bridge dispatch
  routing.
- `.claude/rules/operating-model.md:113` still frames multi-model routing and
  harness-D role promotion as Phase 2+ not implemented.

Verified current-state bridge evidence:

- `bridge/gtkb-ollama-integration-phase-2-routing-010.md` is `VERIFIED`.
- `bridge/gtkb-ollama-harness-provider-scoped-model-validation-004.md` is
  `VERIFIED`.
- `bridge/gtkb-openrouter-routing-deepseek-cost-optimization-004.md` is
  `VERIFIED`.

MemBase evidence:

- `WI-4669` exists and is open, but currently has priority `P3`, no project,
  and no related bridge thread.
- Its acceptance summary already names the right correction: update
  canonical-terminology and operating-model records to match live
  `.api-harness/routing.toml`, with no residual local-open-weight or single
  Qwen 2.5 claims.

Deliberation evidence:

- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` establishes that Ollama model
  selection must not be hardcoded and should come from the single routing SoT.
- `DELIB-S422-OR-REGISTRY-INTEGRATION` establishes OpenRouter harness F.
- `DELIB-20262486` records the GO for OpenRouter routing to DeepSeek.
- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` places
  cost-optimized automatic bridge dispatch in the top-priority class.

## Risk / Impact

Severity: P1.

This is active-looking canonical-record drift in always-loaded agent guidance,
not merely documentation lag. It can cause agents to diagnose cloud-provider
failures as local server failures, ignore OpenRouter F when reasoning about
dispatch topology, and treat already-verified routing work as future Phase-2
scope.

## Recommended Prime Builder Action

1. Convert this advisory into a normal implementation proposal for `WI-4669`.
2. Promote `WI-4669` from low-visibility hygiene to the active dispatch /
   SOT-freshness lane, with priority no lower than P1 while dispatcher
   reliability work is active.
3. Use target paths:
   - `.claude/rules/canonical-terminology.md`
   - `groundtruth-kb/docs/reference/canonical-terminology-detail.md`
   - `.claude/rules/operating-model.md`
4. Replace stale claims instead of appending caveats:
   - Do not say the default Ollama review route is local.
   - Do say `.api-harness/routing.toml` is the routing SoT.
   - Do distinguish provider label `ollama` from local-weight hosting.
   - Do mention that OpenRouter F is part of the active low-cost LO dispatch
     topology.
5. Verification should include:
   - `rg -n "local open-weight|Ollama-served local|single Phase-1 model|Qwen 2\\.5 Coder 14B|No active Prime Builder or Loyal Opposition role, no bridge dispatch routing|not implemented in Phase 1" .claude/rules/canonical-terminology.md groundtruth-kb/docs/reference/canonical-terminology-detail.md .claude/rules/operating-model.md`
   - focused reads of `.api-harness/routing.toml`
   - any existing terminology/operating-model tests or inventory scan that
     covers these files.

## Boundaries

This advisory does not authorize protected narrative edits, KB mutations, or
implementation. It is an LO routing artifact. Prime Builder still needs a
bridge proposal and GO before changing the canonical surfaces.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
