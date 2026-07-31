NEW
author_identity: claude
author_harness_id: B
author_session_context_id: claude-interactive-20260708-goose-slice1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive prime-builder

# Reusable Direct-Cloud Harness Template — Slice 1: ADR + shared-runtime design (OpenRouter first adopter)

Work Item: WI-5079
Umbrella Work Item: WI-5078
Project: PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE
Project Authorization: PAUTH-PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE-20260708
target_paths: [".groundtruth/formal-artifact-approvals/2026-07-08-ADR-CLOUD-HARNESS-TEMPLATE-001.json"]

## Summary

Slice 1 of building a reusable, config-driven **cloud harness runtime template** per owner decision `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` and `SPEC-INTAKE-9ec893`. The current per-harness shim scripts are near-duplicates (~1164 / ~1312 / ~490 lines) that each hand-roll connection, retry, guard-adapter, and author-metadata logic. The template consolidates them into one base runtime that harnesses instantiate by config, varying only `{endpoint, auth-env-key, API dialect, model, hook tier}`. This slice authors `ADR-CLOUD-HARNESS-TEMPLATE-001` recording the template architecture and designs the first-adopter proof (the OpenRouter harness, already direct-cloud + token-auth). No source is modified in this slice; the ADR is the deliverable.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below derives tests from the linked specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline govern this proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the template is modeled as durable artifacts (project, ADR, WIs, shared module).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across the template, its adopters, and the confirmed principle.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the superseded per-harness hand-rolled shims are recorded with an explicit superseded lifecycle state as they consolidate.
- `SPEC-INTAKE-9ec893` — the confirmed governing principle the template operationalizes: harness = integration+model+config; prefer non-GUI, maximal-hook, direct-cloud integrations. The template makes the *integration* reusable so only model+config+endpoint+dialect+hook-tier vary.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the onboarding contract (esp. Layer 3 fail-closed guard adapter) the template's base runtime must satisfy for every adopter.
- `GOV-20` (Architecture Decision Governance) — governs ADR authoring.
- `GOV-ARTIFACT-APPROVAL-001` — the ADR is a formal artifact requiring a formal-artifact-approval packet before MemBase insert.
- `GOV-ENV-LOCAL-AUTHORITY-001` — `.env.local` is the authoritative env SoT; each adopter's auth key (e.g., `OPENROUTER_API_KEY`, `OLLAMA_API_KEY`, `ALIBABA_API_KEY`) is referenced by env-key NAME (never value).
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` — the existing fail-closed guard-adapter contract; the template generalizes this into the shared base (a `DCL` generalization is authored in a later slice).
- `ADR-OLLAMA-HARNESS-ADOPTION-001` — precedent adoption ADR + guard-adapter pattern the template abstracts.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook-surface precedent; the template's Anthropic-dialect path targets native hooks vs. the guard-adapter fallback floor.
- `.claude/rules/project-root-boundary.md` — all template + adopter artifacts remain within `E:\GT-KB`; External Harness Executable Resolution Exception governs external executable resolution.

## Prior Deliberations

- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` (owner_decision, 2026-07-08) — the owner directive this implements (build the template, not deferred; OpenRouter first adopter) with the three-harness design matrix and consolidation target.
- `SPEC-INTAKE-9ec893` (governance, specified) — the principle the template operationalizes.
- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` and `DELIB-20260708-OLLAMA-DIRECT-CLOUD-ANTHROPIC-ENHANCEMENT` — the sibling per-harness adoptions (Alibaba Cloud Studio slice-1 ADR + Ollama slice-1 ADR, both NEW) that will reference and build on this template.
- `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION` — the non-GUI / maximal-hook direction.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` and the Ollama Phase-1 integration bridge-thread series — the original per-harness pattern being generalized.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-9ec893` fixes the reusable-integration principle; `GOV-HARNESS-ONBOARDING-CONTRACT-001` defines the conformance floor every adopter must meet; `GOV-20` defines the ADR workflow; `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` fixes the template + first-adopter intent. No new or revised requirement blocks this slice.

## Proposed Change / Scope

On GO, author `ADR-CLOUD-HARNESS-TEMPLATE-001` (MemBase spec, `type=architecture_decision`) via the governed formal-artifact flow. The ADR records:

1. **Decision:** a shared, config-driven cloud-harness runtime base module that all cloud harnesses instantiate, replacing the per-harness hand-rolled shims. The base owns connection, retry/backoff, guard-adapter enforcement, author-metadata injection, and the tool-call loop; adopters supply config only.
2. **Varying axes (the template's config surface):** `endpoint`; `auth-env-key` (token auth via an `Authorization` header keyed on the adopter's env var, per `GOV-ENV-LOCAL-AUTHORITY-001`); `API dialect` (`ollama-native` | `openai-chat` | `anthropic-messages`); `model` routing; `hook tier` (guard-adapter floor | native full hooks for the Anthropic dialect).
3. **Three-harness matrix grounding the design:** Ollama (localhost bridge, native dialect, floor — needs direct-cloud + Anthropic); OpenRouter (direct-cloud, token auth, OpenAI dialect, floor — needs Anthropic for full hooks); Alibaba Cloud Studio (direct-cloud, token auth, Anthropic dialect, full-hook target). Same shape; different config.
4. **First-adopter proof (OpenRouter, F):** OpenRouter is the readiest adopter — already direct-cloud (`https://openrouter.ai/api/v1`) + token auth (`OPENROUTER_API_KEY`) + OpenAI dialect + guard-adapter floor + mature retry/backoff. Slice 2 re-bases the OpenRouter harness onto the shared runtime as the proof; its Anthropic-compatible full-hook path is evaluated with an openrouter.ai Anthropic-endpoint spike (same shape as Ollama issue #16922).
5. **Guard/hook contract:** the base runtime enforces the `GOV-HARNESS-ONBOARDING-CONTRACT-001` Layer-3 fail-closed guard adapter for every adopter by construction (generalizing `DCL-OLLAMA-TOOL-PARITY-GATE-001` into a `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE` in a later slice); the Anthropic-dialect path additionally targets native hooks where the endpoint supports it.
6. **Alternatives considered + rejected:** keep per-harness hand-rolled shims (rejected — ~2900 duplicate lines, divergent maturity, the very drift the principle warns against); reference-first extraction from one harness (rejected by owner AUQ in favor of template + first-adopter); a heavyweight framework dependency (rejected — the shims are framework-free by design per the Ollama adoption).
7. **Consequences + slice plan:** slice 2 (shared runtime base module + OpenRouter re-base proof), slice 3 (dialect abstraction incl. `anthropic-messages` + native-hook path + generalized tool-parity `DCL`), slice 4 (sibling adoptions — Alibaba Cloud Studio + Ollama re-based onto the template; consolidate remaining shims; doctor + tests). Cursor's shim is a later consolidation candidate.

## Owner Decisions / Input

- Owner review request (2026-07-08): review the Ollama harness and propose enhancements; then "I want a reusable harness template. I would like to evaluate OpenRouter next."
- `AskUserQuestion` (2026-07-08): "How should I take the Ollama harness enhancement forward?" → Scope both A+B under WI-5075 (the per-harness sibling).
- `AskUserQuestion` (2026-07-08): "How should I structure the reusable direct-cloud harness template program?" → **Template + OpenRouter as first adopter** (`DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE`).

These answers are the sole authorization for this proposal; implementation of each slice remains gated by Loyal Opposition GO plus an implementation-start packet, and formal-artifact creation remains gated by `GOV-ARTIFACT-APPROVAL-001` packets.

## Specification-Derived Verification

Slice 1's deliverable is the ADR (a decision artifact); its verification is a **spec-to-test mapping** of inspection assertions derived from the linked specifications. Executable `python -m pytest` coverage lands in slice 2+ (a `test_cloud_harness_template.py` regression asserting the base runtime enforces the guard-adapter floor for every configured adopter):

| Linked spec | Derived test / assertion | Command / evidence |
|---|---|---|
| `GOV-20` | ADR exists with `type=architecture_decision` and non-empty Decision / Rationale / Alternatives / Consequences | `gt spec show ADR-CLOUD-HARNESS-TEMPLATE-001` |
| `SPEC-INTAKE-9ec893` | ADR records the config-driven template (varying axes) and the integration-reuse rationale | inspection of ADR Decision |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | ADR commits the base runtime to enforcing the Layer-3 fail-closed guard adapter for every adopter, and assigns each change to a slice | inspection of ADR Consequences |
| `GOV-ARTIFACT-APPROVAL-001` | formal-artifact-approval packet exists at the declared target path with matching content hash | inspection of the target packet |

No source is modified in this slice, so there is no `pytest`/`ruff` code gate to run here; the executable regression (`test_cloud_harness_template.py`, `python -m pytest`, `ruff check`) is defined and run from slice 2.

## Acceptance Criteria

1. `ADR-CLOUD-HARNESS-TEMPLATE-001` authored in MemBase under GOV-20 with the seven content elements above.
2. ADR records the shared-runtime template, its config surface (varying axes), and the guard-adapter enforcement contract for all adopters.
3. ADR records the OpenRouter first-adopter proof plan + the Anthropic-endpoint spike, and names the sibling adoptions (Alibaba Cloud Studio, Ollama) that reference it.
4. ADR scopes slices 2-4 with named target artifacts and the shim-consolidation plan.
5. Formal-artifact-approval packet present at the declared target path (content-hash match).

## Risks / Rollback

- **Risk:** premature abstraction — a template that fits three known harnesses may over-fit and resist a future one. **Mitigation:** the OpenRouter first-adopter proof (slice 2) validates the base against a real re-base before sibling adoption; the config surface is deliberately the minimal varying-axes set.
- **Risk:** consolidating ~2900 lines of divergent shim behavior may regress harness-specific handling (e.g., OpenRouter's retry/backoff, guard details). **Mitigation:** slice 2 re-bases one harness at a time behind the guard-adapter floor with regression tests; no shim is deleted until its adopter passes on the base.
- **Rollback:** the ADR is append-only in MemBase; a wrong template decision is corrected by a superseding ADR. No source/config is mutated in this slice; the base module + re-bases occur only in GO'd implementation slices.
