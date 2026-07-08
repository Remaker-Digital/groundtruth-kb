NEW
author_identity: claude
author_harness_id: B
author_session_context_id: claude-interactive-20260708-goose-slice1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Ollama Direct-Cloud Harness — Slice 1: Adoption ADR (direct cloud + Anthropic-compat full hooks)

Work Item: WI-5077
Umbrella Work Item: WI-5075
Project: PROJECT-GTKB-OLLAMA-DIRECT-CLOUD-HARNESS
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-DIRECT-CLOUD-HARNESS-20260708
target_paths: [".groundtruth/formal-artifact-approvals/2026-07-08-ADR-OLLAMA-DIRECT-CLOUD-HARNESS-ADOPTION-001.json"]

## Summary

Slice 1 of enhancing the Ollama harness (identity `D`) per owner direction and `SPEC-INTAKE-9ec893`: (A) replace the indirect path (GT-KB → local Windows Ollama service at `http://localhost:11434` → cloud) with **direct cloud access** to `https://ollama.com/api` using token authentication via an `Authorization` header keyed on the `OLLAMA_API_KEY` env var; and (B) adopt the **Anthropic-compatible endpoint** (`/v1/messages`) for a Claude-Code-style, full-native-hook integration, lifting the hook ceiling above the current guard-adapter floor. This slice authors `ADR-OLLAMA-DIRECT-CLOUD-HARNESS-ADOPTION-001` recording the decision, the firmed-up API contract, the cloud-Anthropic-endpoint spike, alternatives, and the slice plan. No source is modified in this slice; the ADR is the deliverable.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below derives tests from the linked specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline govern this proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the enhancement is modeled as durable artifacts (project, ADR, WIs).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across project, ADR, WIs, deliberations.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the superseded local-bridge access design is recorded with an explicit superseded lifecycle state.
- `SPEC-INTAKE-9ec893` — the confirmed governing principle: harness = integration+model+config; prefer non-GUI, maximal-hook integrations; direct cloud access. Ollama-direct-cloud (integration) + its cloud models + Anthropic-compatible endpoint (config).
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the onboarding contract the enhanced harness must continue to satisfy (Layers 1-3).
- `GOV-20` (Architecture Decision Governance) — governs ADR authoring.
- `GOV-ARTIFACT-APPROVAL-001` — the ADR is a formal artifact requiring a formal-artifact-approval packet before MemBase insert.
- `GOV-ENV-LOCAL-AUTHORITY-001` — `.env.local` is the authoritative env SoT; the harness references `OLLAMA_API_KEY` by env-key NAME (never value).
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` — the existing fail-closed guard-adapter floor; retained (part A) and potentially superseded by native hooks (part B).
- `ADR-OLLAMA-HARNESS-ADOPTION-001` — the original Ollama adoption ADR this enhances.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook-surface precedent; the Anthropic-compat path inherits the native hook system rather than the fallback guard.
- `.claude/rules/project-root-boundary.md` — all adoption artifacts remain within `E:\GT-KB`; External Harness Executable Resolution Exception governs external executable resolution.

## Prior Deliberations

- `DELIB-20260708-OLLAMA-DIRECT-CLOUD-ANTHROPIC-ENHANCEMENT` (owner_decision, 2026-07-08) — the owner decision this implements (scope both A+B under WI-5075) with the firmed-up API contract and the cloud-Anthropic-endpoint spike.
- `SPEC-INTAKE-9ec893` (governance, specified) — the principle this instantiates.
- `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION` — the non-GUI / maximal-hook direction.
- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` — the sibling Alibaba Cloud Studio harness (same Anthropic-compat direct-cloud pattern); this Ollama work is the second instance.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` and the Ollama Phase-1 integration bridge-thread series — the original adoption + guard-adapter pattern being enhanced.
- External reference (owner-supplied): upstream Ollama issue #16922 (`github.com/ollama/ollama/issues/16922`) + PR #16933 — the cloud Anthropic-compatible `/v1/messages` endpoint requires the `Authorization`-header token scheme and rejects `x-api-key`. Directly informs part B's client-auth configuration and retires the earlier local-only spike question.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-9ec893` fixes the direct-cloud / maximal-hook preference; `GOV-HARNESS-ONBOARDING-CONTRACT-001` defines the conformance target; `GOV-20` defines the ADR workflow; `DELIB-20260708-OLLAMA-DIRECT-CLOUD-ANTHROPIC-ENHANCEMENT` fixes the A+B intent and the firmed API contract. No new or revised requirement blocks this slice.

## Proposed Change / Scope

On GO, author `ADR-OLLAMA-DIRECT-CLOUD-HARNESS-ADOPTION-001` (MemBase spec, `type=architecture_decision`) via the governed formal-artifact flow. The ADR records:

1. **Decision (A - direct cloud):** the Ollama harness shim reaches `https://ollama.com/api` directly with token authentication via an `Authorization` header keyed on the `OLLAMA_API_KEY` env var (env-keyed, never literal), removing the `http://localhost:11434` Windows-service dependency; streaming, usage, and error handling per the direct-cloud contract. The shim currently defaults to localhost with no auth and speaks native `/api/chat`; this is a bounded auth + endpoint + protocol upgrade.
2. **Decision (B - Anthropic-compat full hooks):** adopt the Anthropic-compatible endpoint (`/v1/messages`, Anthropic Messages API format; tool-use + streaming supported per docs) to enable a Claude-Code-style full-native-hook integration, raising the hook ceiling above the guard-adapter floor.
3. **Cloud Anthropic-endpoint auth constraint (upstream evidence, issue #16922):** upstream Ollama issue #16922 confirms the cloud host DOES expose the Anthropic-compatible `/v1/messages` endpoint — so part B is architecturally available and the earlier local-only concern is retired. However, that cloud endpoint currently requires the native `Authorization`-header token scheme and REJECTS the `x-api-key` header that standard Anthropic clients send by default; upstream PR #16933 is proposed to accept `x-api-key`. Implication: a Claude-Code-style client must be configured to send the `Authorization`-header token rather than `x-api-key`, or a thin auth-translation surface is used, or the integration tracks upstream PR #16933. Slice 3 resolves the exact client-auth configuration and its effect on the achievable full-hook ceiling.
4. **Same-model-multiple-provider note:** DeepSeek V4 Pro already appears in routing.toml via ollama (`:cloud`), openrouter, and goose providers, and Kimi/Qwen/GLM cloud models are available — each (integration+model+config) is a distinct harness per `SPEC-INTAKE-9ec893`.
5. **Alternatives considered + rejected:** keep the localhost Windows-service bridge (rejected — unnecessary dependency, no headless-without-desktop, no auth boundary); direct cloud via native `/api` only, no Anthropic-compat (viable fallback if the spike fails, but caps hooks at the guard-adapter floor); OpenRouter route for the same models (a separate harness, not this one).
6. **Consequences + slice plan:** slice 2 (auth + endpoint + streaming/usage/errors upgrade to the harness shim + routing/registry updates), slice 3 (Anthropic-compat `/v1/messages` integration + native hook wiring, contingent on the spike; `DCL` update as needed), slice 4 (doctor `_check_ollama_harness` update + parity + tests). Alibaba Cloud Studio (sibling) and a possible shared "Anthropic-compatible direct-cloud" template remain related work.

## Owner Decisions / Input

- Owner review request (2026-07-08): review the current Ollama harness and propose enhancements.
- `AskUserQuestion` (2026-07-08): "How should I take the Ollama harness enhancement forward?" → **Scope both A+B under WI-5075** (`DELIB-20260708-OLLAMA-DIRECT-CLOUD-ANTHROPIC-ENHANCEMENT`).
- Owner env update (2026-07-08): `.env.local` env SoT is the source for `OLLAMA_API_KEY` (referenced by name only, per `GOV-ENV-LOCAL-AUTHORITY-001`).

These answers are the sole authorization for this proposal; implementation of each slice remains gated by Loyal Opposition GO plus an implementation-start packet, and formal-artifact creation remains gated by `GOV-ARTIFACT-APPROVAL-001` packets.

## Specification-Derived Verification

Slice 1's deliverable is the ADR (a decision artifact); its verification is a **spec-to-test mapping** of inspection assertions derived from the linked specifications. Executable `python -m pytest` coverage lands in slice 4 (updated `_check_ollama_harness` doctor check + a `test_ollama_direct_cloud_harness.py` regression asserting direct-cloud auth + conformance):

| Linked spec | Derived test / assertion | Command / evidence |
|---|---|---|
| `GOV-20` | ADR exists with `type=architecture_decision` and non-empty Decision / Rationale / Alternatives / Consequences | `gt spec show ADR-OLLAMA-DIRECT-CLOUD-HARNESS-ADOPTION-001` |
| `SPEC-INTAKE-9ec893` | ADR records the direct-cloud + Anthropic-compat maximal-hook architecture and the integration+model+config framing | inspection of ADR Decision |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | ADR preserves Layer 1-3 conformance across the enhancement and assigns each change to a slice | inspection of ADR Consequences |
| `GOV-ARTIFACT-APPROVAL-001` | formal-artifact-approval packet exists at the declared target path with matching content hash | inspection of the target packet |

No source is modified in this slice, so there is no `pytest`/`ruff` code gate to run here; the executable regression (`test_ollama_direct_cloud_harness.py`, `python -m pytest`, `ruff check`) is defined and run in slice 4.

## Acceptance Criteria

1. `ADR-OLLAMA-DIRECT-CLOUD-HARNESS-ADOPTION-001` authored in MemBase under GOV-20 with the six content elements above.
2. ADR records the direct-cloud (A) decision, the Anthropic-compat full-hook (B) architecture, and the `x-api-key`/`Authorization` auth constraint from upstream issue #16922 (part B client-auth configuration).
3. ADR records supersession of the localhost-bridge access design; cites `SPEC-INTAKE-9ec893` and `ADR-OLLAMA-HARNESS-ADOPTION-001`.
4. ADR scopes slices 2-4 with named target artifacts.
5. Formal-artifact-approval packet present at the declared target path (content-hash match).

## Risks / Rollback

- **Risk:** the cloud Anthropic-compatible `/v1/messages` endpoint rejects the `x-api-key` header standard Anthropic clients send by default (upstream issue #16922), so a stock Anthropic client is not drop-in. **Mitigation:** configure the client to send the `Authorization`-header token instead, or add a thin auth-translation surface, or track upstream PR #16933; the native-API direct-cloud path (A) is unaffected and ships regardless.
- **Risk:** direct cloud access changes the auth/error surface (rate limits, 429s, streaming framing) vs. the trusted-localhost path. **Mitigation:** slice 2 implements the streaming/usage/error handling from the direct-cloud contract with ret/backoff; the guard-adapter floor is retained.
- **Rollback:** the ADR is append-only in MemBase; a wrong decision is corrected by a superseding ADR. No source/config is mutated in this slice; the auth/endpoint/hook changes occur only in GO'd implementation slices.
