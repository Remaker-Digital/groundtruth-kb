author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: e673b49a-79d9-485d-8b98-943def29837f
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

# Loyal Opposition Advisory — Non-GUI Prime Harness (Alibaba adoption) as the window-safe fix for headless Prime dispatch

Specs: GOV-HARNESS-ONBOARDING-CONTRACT-001, ADR-OLLAMA-HARNESS-ADOPTION-001, GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001, GOV-HARNESS-ROLE-PORTABILITY-001
WIs: WI-5135 (Codex pwsh windows), WI-5072 / WI-5073 (Goose→Alibaba adoption), WI-5134 (verification refresher, blocked on WI-5135), WI-5080 (kill-loop containment)
Classification: **adapt** (adopt the owner's already-decided non-GUI / goose→Alibaba direction; adapt it to fill the *Prime* role, not just LO)

## Problem statement

GT-KB currently has **no window-safe headless Prime Builder harness.**

- The only harnesses tagged `prime-builder` are **Codex-A** (now quiesced) and **Cursor-E** (suspended). So `gt bridge dispatch health` reports `prime-builder: (none)` — headless Prime dispatch is OFF.
- **Codex-A is not window-safe** (WI-5135): its `exec` sandbox spawns a visible `pwsh.exe` console per shell command because `CREATE_NO_WINDOW` is not inherited by the grandchild pwsh and Codex doesn't re-apply it. Re-enabling Codex-A dispatch re-triggers a window storm (observed this session — a burst of consoles when the no-window verification was refreshed).
- Consequence: Prime work depends entirely on **interactive Codex** (a human-attended window). There is no autonomous, window-clean way to dispatch Prime work.

Meanwhile the LO lane is fully covered (Claude-B, now +Ollama-D) and window-clean, because the Python-shim harnesses had their console-flash fixed long ago (WI-4529, `CREATE_NO_WINDOW`).

## Why this is a design gap, not just a Codex bug

The per-harness split is instructive (owner-confirmed this session):

| Harness | Type | Windows? | Why |
|---|---|---|---|
| Claude-B | claude | none | tool/bash execution is no-window-contained |
| Ollama-D, OpenRouter-F | python API shim | none | shim spawns subprocesses with `CREATE_NO_WINDOW` (WI-4529) |
| Codex-A | codex (GUI/CLI) | **pops pwsh** | grandchild pwsh not no-window; Codex-internal |
| Cursor-E, Antigravity-C, Goose-G | desktop | GUI-class | desktop harnesses; console/GUI storms historically (WI-4925, WI-5061, WI-5113) |

The pattern: **Python-API-shim harnesses are window-clean by construction; desktop/CLI harnesses are not.** So the durable fix for headless Prime-without-windows is a **Python-API-shim Prime harness**, not a patched desktop one. This aligns exactly with the owner's standing direction `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION` ("GT-KB harness = integration+model+config; prefer non-GUI").

## Recommendation

**Primary: complete the Alibaba Cloud Studio harness adoption (WI-5072/WI-5073) AND promote it to a dispatchable `prime-builder` role**, delivering a non-GUI, capable (DeepSeek V4 Pro) headless Prime harness that sidesteps the Codex window problem entirely. The owner has already decided the direction (`DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS`; Slice-1 GO `DELIB-202665955`); this advisory adds the *Prime-role* target to that adoption, which the current WI-5072/5073 scope leaves at `loyal-opposition`.

**Interim / alternative: promote Ollama-D to a `prime-builder` role** with a capability validation gate. Ollama is adopted, active, window-clean, and now LO-dispatchable — the cheapest path to *any* headless Prime today. Risk: it's the `low-cost` model (kimi-k2-7-code-cloud); Prime work (bridge proposals, implementation, tests, commits) is more demanding than LO review, and Ollama has a reliability history (stalls, 502s, saturation). Treat as a stopgap, not the destination.

## Non-GUI Prime harness design sketch (reuse the Ollama pattern)

The Ollama adoption is the proven blueprint; generalize it for Prime:

1. **Transport:** Python tool-calling shim (`scripts/<harness>_harness.py`, per `scripts/ollama_harness.py`) → cloud/local model HTTP API. Framework-free. All subprocesses spawned with `CREATE_NO_WINDOW` — window-clean by construction.
2. **Capability floor (Prime, not LO):** must satisfy `GOV-HARNESS-ONBOARDING-CONTRACT-001` at **full Prime tool parity** — not just verdict authoring, but bridge proposal filing, implementation edits, spec-derived test authoring, `implementation_authorization.py begin`, and VERIFIED-safe commit finalization. This is a *stricter* floor than the LO-only Ollama adoption cleared.
3. **Dispatch readiness:** a reachability + capability probe (endpoint up, model responds, tool loop round-trips) — **not** a GUI/no-window smoke like Codex's. No window-detection needed because the shim is headless by design. Avoids the WI-5134 false-green-verification class entirely.
4. **Author-metadata injection:** per `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` — dispatched Prime writes carry correct `author_*` provenance so bridge gates pass.
5. **Skill adapters:** generate the Prime skill set for the harness (bridge-propose, send-review, verify counterpart, kb-*), per the adapter-generation pattern.
6. **Role + dispatch:** `prime-builder` role + `can_receive_dispatch=true`, ranked behind interactive coverage as appropriate.
7. **Guardrails:** honor `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, credential-scan, root-boundary, and the implementation-start gate identically to any Prime harness.

Net effect: a headless Prime harness that never opens a window, needs no fragile no-window verification, and is model-swappable via config — the clean answer the Codex path can't reach without an upstream-CLI fix.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied
Yes — this advisory drives real work: completing WI-5072/5073, promoting a harness to `prime-builder`, capability-floor conformance, dispatch wiring. No source is touched until an owner-approved implementation proposal exists.

### Grill-the-owner questions (Prime must obtain durable AUQ answers before filing a proposal)
1. **Target harness:** Alibaba Cloud Studio (capable, needs adoption completion) as the durable non-GUI Prime harness, Ollama-Prime as an interim stopgap, or both (interim → durable)?
2. **Model acceptability:** is DeepSeek V4 Pro (Alibaba) — or kimi-k2-7-code-cloud (Ollama) for the interim — acceptable *for Prime-quality* work (proposals, implementation, tests), given Prime is more demanding than LO review?
3. **Credentials/endpoint:** who provisions the Alibaba Cloud Studio API key / endpoint / account (owner-supplied via `env.local` per `GOV-ENV-LOCAL-AUTHORITY-001`)? Same question for the interim Ollama-Prime endpoint.
4. **Codex disposition:** should Codex-A stay quiesced for *headless* dispatch permanently (interactive-only), or is fixing WI-5135 (Codex shell no-window) *also* wanted as a parallel track? (Recommendation: keep Codex interactive-only; invest in the non-GUI Prime harness rather than chasing an upstream Codex-CLI window fix.)
5. **Priority:** does this rank above current backlog (finalization-hardening WI-5105/5112/5132, etc.)?

### Required durable owner decisions (AUQ evidence before an implementation proposal)
- The target Prime harness choice (Q1).
- Acceptance of a cloud Prime model at the chosen capability/cost (Q2).
- Authorization + credentials to proceed with the adoption (Q3), and the priority call (Q5).

## Prime Builder implementation context
- **Blueprint:** the Ollama adoption chain (WI-4316→4325, 4373→4388) is the reusable template; the delta is the **Prime capability floor** and **Prime skill adapters**.
- **Existing scaffolding:** WI-5072 (onboarding-contract conformance) + WI-5073 (ADR + headless dispatch/guard architecture, Slice-1 GO'd) already frame the Alibaba adoption — extend their scope to the Prime role.
- **Verification:** reachability + Prime-tool-parity E2E (round-trip → bridge proposal filing → implementation-start packet → VERIFIED-safe commit), per the `verify_ollama_dispatch.py` E2E pattern.
- **Do NOT** re-enable Codex-A headless dispatch as the interim — it re-arms the window storm (WI-5135). Use Ollama-Prime or interactive Codex until the non-GUI Prime harness lands.

## Prior Deliberations
- `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION` — owner: prefer non-GUI harnesses (integration+model+config).
- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` — owner: replace Goose with Alibaba Cloud Studio harness.
- `DELIB-202665955` — GO on Goose Adoption Slice 1 (ADR + guard/dispatch architecture).
- `DELIB-20260708-GOOSE-PARITY-ASSESSMENT-REVIEW` — parity assessment + onboarding-contract review.
- `DELIB-20261075` (SP-1 dispatch reliability foundation), `DELIB-20263311` (no-window flag for dispatch subprocesses) — dispatch/window precedent.

## Owner decision needed
Route Q1–Q5 above through AskUserQuestion before any implementation proposal. This advisory is analysis only; it does not authorize implementation.

## Owner Disposition (2026-07-10) — PRIMARY RECOMMENDATION REJECTED-FOR-NOW

The owner-grilling gate was run via AskUserQuestion. Decisions recorded as
`DELIB-202666064` (owner_conversation; linked WI-5135):

1. **Prime harness path — "Neither."** The owner declined adopting a non-GUI
   Prime harness (Alibaba and Ollama-Prime both declined). This advisory's
   PRIMARY recommendation is **dispositioned reject-for-now.**
2. **Cloud Prime — "Yes, acceptable in principle"** — retained as a future
   fallback only.
3. **Codex disposition — "Also fix WI-5135 in parallel."** The owner directs the
   **Codex-shell no-window fix** (this advisory's rejected alternative) as the
   chosen durable path to window-safe headless Prime.
4. **Priority — "After current finalization backlog"** (WI-5105/5112/5132).

**Net:** the owner chose to FIX Codex (WI-5135) rather than adopt a new harness —
the opposite of this advisory's recommendation. WI-5135 was re-scoped to the
owner-directed Codex-shell containment fix. Codex-A stays quiesced until it
lands; interactive-Codex is the interim Prime coverage; Ollama-D remains
LO-dispatch-enabled only. The non-GUI-Prime-harness design in this advisory is
**retained as a documented fallback** should the Codex fix prove infeasible. A
Prime Builder kickoff prompt for the WI-5135 program was prepared this session.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
