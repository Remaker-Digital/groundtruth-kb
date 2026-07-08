NEW
author_identity: claude
author_harness_id: B
author_session_context_id: claude-interactive-20260708-goose-slice1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Alibaba Cloud Studio Harness — Slice 1: Adoption ADR (Anthropic endpoint; new identity, retire Goose)

Work Item: WI-5073
Umbrella Work Item: WI-5072
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260708
target_paths: [".groundtruth/formal-artifact-approvals/2026-07-08-ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001.json"]

## Summary

Slice 1 of establishing a first-class **Alibaba Cloud Studio** harness (new registry identity `H`) that makes **DeepSeek V4 Pro** dispatchable and fully LO/PB-capable, built on the **Anthropic-compatible endpoint** (`ALIBABA_ANTHROPIC_COMPATIBLE_ENDPOINT` in `.env.local`) as a Claude-Code-style integration with maximal native hook capability. This replaces and obsoletes the clumsy "Goose" GUI-proxy work (retire identity `G`; remove the Goose shim script, `.goose/` adapters, and Goose capability entries). This slice authors `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` recording the decision, the Anthropic-endpoint hook architecture, the identity replacement, and the obsolescence + rebuild slice plan. No source is modified in this slice; the ADR is the deliverable.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below derives tests from the linked specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline govern this proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — adoption work is modeled as durable artifacts (project, ADR, WIs, confirmed principle).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability is preserved across the project, ADR, WIs, deliberations, and spec.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the obsoleted Goose work and superseded proposals are recorded with explicit superseded/retired lifecycle states.
- `SPEC-INTAKE-9ec893` — the confirmed governing principle: harness = integration+model+config; prefer non-GUI, maximal-hook integrations. Alibaba Cloud Studio (integration) + DeepSeek V4 Pro (model) + Anthropic-compatible endpoint (config) = this harness.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the onboarding contract identity `H` must satisfy (Layers 1-3).
- `GOV-20` (Architecture Decision Governance) — governs ADR authoring.
- `GOV-ARTIFACT-APPROVAL-001` — the ADR is a formal artifact requiring a formal-artifact-approval packet before MemBase insert.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — Prime Builder / Loyal Opposition are portable harness-assigned roles.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — capable harnesses are prepared for PB and LO roles; the Anthropic-endpoint full-hook path serves this.
- `GOV-ENV-LOCAL-AUTHORITY-001` — `.env.local` is the authoritative env SoT; the harness references `ALIBABA_ANTHROPIC_COMPATIBLE_ENDPOINT` and `ALIBABA_API_KEY` by env-key NAME (never value).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook-surface precedent; a Claude-Code-style Anthropic-endpoint harness inherits the native hook system rather than a fallback shim guard.
- `.claude/rules/project-root-boundary.md` — all adoption artifacts remain within `E:\GT-KB`; External Harness Executable Resolution Exception governs any external executable resolution.

## Prior Deliberations

- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` (owner_decision, 2026-07-08) — the owner decision this proposal implements: replace Goose with the Alibaba Cloud Studio harness on the Anthropic endpoint; new identity `H`, retire `G`; obsolete partial Goose work.
- `SPEC-INTAKE-9ec893` (governance, specified) — confirmed governing principle the harness instantiates.
- `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION` (owner_decision) — the non-GUI / maximal-hook direction this sharpens.
- `DELIB-20260708-GOOSE-PROMOTE-TO-OPERATING-HARNESS` and `DELIB-20260708-GOOSE-PARITY-ASSESSMENT-REVIEW` — the Goose-promotion + non-conformance history now obsoleted.
- Superseded proposals: `bridge/gtkb-goose-harness-adoption-slice1-adr-001.md` (WITHDRAWN, GUI-centric) and `bridge/gtkb-alibaba-deepseek-nongui-harness-slice1-adr-001.md` (WITHDRAWN, shim-centric) — this thread is the settled Alibaba Cloud Studio / Anthropic-endpoint framing.
- Precedent: the Ollama Phase-1 integration bridge-thread series (adoption ADR + tool-parity DCL + doctor-check pattern) — reused for structure, but the Anthropic-endpoint hook path is fuller than the Ollama shim.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-9ec893` fixes the harness-identity principle and the non-GUI/maximal-hook preference; `GOV-HARNESS-ONBOARDING-CONTRACT-001` defines the conformance target; `GOV-20` defines the ADR workflow; the owner decision `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` fixes the replace/new-identity/Anthropic-endpoint intent. No new or revised requirement blocks this slice.

## Proposed Change / Scope

On GO, author `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` (MemBase spec, `type=architecture_decision`) via the governed formal-artifact flow. The ADR records:

1. **Decision:** establish the Alibaba Cloud Studio harness (new identity `H`, `harness_name` "alibaba-cloud-studio") hosting DeepSeek V4 Pro via the Anthropic-compatible endpoint; retire Goose `G`; obsolete all partial Goose artifacts.
2. **Hook architecture (the reason to replace, not extend):** build GT-KB compatibility on the Anthropic-compatible endpoint using Claude-Code-style native tooling, so the harness inherits the FULL native hook system (SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop) plus the governed guard gates and skills — a higher hook ceiling than the guard-adapter shim floor used by Ollama/OpenRouter. Record the achievable hook surface as the slice-3 target.
3. **Identity replacement:** register `H` with the Anthropic-endpoint headless invocation surface (env-keyed credentials, never literal values) and the capability-floor block; retire `G`; remove the concurrently-added Goose headless/dispatch wiring on `G`.
4. **Obsolescence inventory:** the Goose shim script under scripts/, the `.goose/skills/` adapters, and any Goose capability-registry entries are removed in slice 2. Note: the Goose build-out was added out-of-protocol by a concurrent session (the slice-1 ADR was still NEW); coordinate before deletion.
5. **Alternatives considered + rejected:** extend the Goose GUI/shim (rejected — hook-ceiling-capped, clumsy proxy); OpenAI-compatible shim only (rejected — guard-adapter floor only, misses the Anthropic full-hook ceiling); keep same identity `G` repurposed (rejected per owner AUQ in favor of a clean new identity).
6. **Consequences + slice plan:** slice 2 (register `H` + retire `G` + capability-floor block + glossary + operating-model §3 + remove Goose artifacts), slice 3 (Anthropic-endpoint integration + native hook wiring + `DCL-ALIBABA-CLOUD-STUDIO-TOOL-PARITY-GATE-001` if a guard surface is still needed), slice 4 (`_check_alibaba_cloud_studio_harness` doctor check + parity + tests). Antigravity (WI-5074) and Ollama (WI-5075) remain sibling projects per `SPEC-INTAKE-9ec893`.

## Owner Decisions / Input

- `AskUserQuestion` (2026-07-08): dispose Goose non-conformance → File tracking work item (WI-5072).
- `AskUserQuestion` (2026-07-08): WI-5072 vs standing decisions → Supersede: promote to real harness.
- `AskUserQuestion` (2026-07-08): operating target → Headless-dispatchable operating harness.
- Owner direction (2026-07-08, `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION`): harness = integration+model+config; prefer non-GUI, maximal-hook; GUI harnesses interim.
- `AskUserQuestion` (2026-07-08): reconcile → Reframe + capture principle (confirmed as `SPEC-INTAKE-9ec893`).
- Owner env update (2026-07-08): `.env.local` provisioned with `ALIBABA_ANTHROPIC_COMPATIBLE_ENDPOINT` + `ALIBABA_API_KEY` (credentials owner-managed; referenced by name only).
- `AskUserQuestion` (2026-07-08): execute pivot → **New identity; retire Goose G** (`DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS`).

These answers are the sole authorization for this proposal; implementation of each slice remains gated by Loyal Opposition GO plus an implementation-start packet, and formal-artifact creation remains gated by `GOV-ARTIFACT-APPROVAL-001` packets.

## Specification-Derived Verification

Slice 1's deliverable is the ADR (a decision artifact); its verification is a **spec-to-test mapping** of inspection assertions derived from the linked specifications. Executable `python -m pytest` coverage for harness conformance lands in slice 4 (`_check_alibaba_cloud_studio_harness` doctor check + a `test_alibaba_cloud_studio_harness.py` regression asserting Layer 2/3):

| Linked spec | Derived test / assertion | Command / evidence |
|---|---|---|
| `GOV-20` | ADR exists with `type=architecture_decision` and non-empty Decision / Rationale / Alternatives / Consequences | `gt spec show ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` |
| `SPEC-INTAKE-9ec893` | ADR records the non-GUI + maximal-hook (Anthropic-endpoint) architecture and the integration+model+config identity | inspection of ADR Decision |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | ADR names all L1 required artifacts for identity `H` and assigns each to a slice; records `G` retirement + Goose obsolescence | inspection of ADR Consequences |
| `GOV-ARTIFACT-APPROVAL-001` | formal-artifact-approval packet exists at the declared target path with matching content hash | inspection of the target packet |

No source is modified in this slice, so there is no `pytest`/`ruff` code gate to run here; the executable regression (`test_alibaba_cloud_studio_harness.py`, `python -m pytest`, `ruff check`) is defined and run in slice 4.

## Acceptance Criteria

1. `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` authored in MemBase under GOV-20 with the six content elements above.
2. ADR records the Anthropic-endpoint full-hook architecture, the new-identity-`H` + retire-`G` decision, and the Goose obsolescence inventory (incl. the concurrent out-of-protocol build-out).
3. ADR records supersession/obsolescence of the two withdrawn proposals and the Goose-promotion history; cites `SPEC-INTAKE-9ec893`.
4. ADR scopes slices 2-4 with named target artifacts.
5. Formal-artifact-approval packet present at the declared target path (content-hash match).

## Risks / Rollback

- **Risk:** the Anthropic-compatible endpoint may not expose the full Claude-Code hook surface for a third-party model (achievable hook ceiling bounded by the endpoint's fidelity). **Mitigation:** slice-3 spike measures the achievable hook surface against the Anthropic endpoint; the guard-adapter floor (`DCL-...-TOOL-PARITY-GATE`) remains the fallback if native hooks are partial.
- **Risk:** deleting the concurrently-added Goose artifacts may collide with another active session still building Goose. **Mitigation:** slice 2 begins with a coordination check + a read-only obsolescence inventory before any deletion.
- **Rollback:** the ADR is append-only in MemBase; a wrong decision is corrected by a superseding ADR. No source/config is mutated in this slice; identity register/retire and deletions occur only in GO'd implementation slices.
