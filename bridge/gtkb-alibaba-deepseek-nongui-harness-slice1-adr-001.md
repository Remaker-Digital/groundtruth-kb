NEW
author_identity: claude
author_harness_id: B
author_session_context_id: claude-interactive-20260708-goose-slice1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Alibaba DeepSeek V4 Pro Non-GUI Harness — Slice 1: Adoption ADR + Guard/Dispatch Architecture

Work Item: WI-5073
Umbrella Work Item: WI-5072
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260708
target_paths: [".groundtruth/formal-artifact-approvals/2026-07-08-ADR-DEEPSEEK-ALIBABA-HARNESS-ADOPTION-001.json"]

## Summary

Slice 1 of making the **Alibaba-hosted DeepSeek V4 Pro** model available to the GT-KB dispatcher through a **non-GUI harness integration** with maximal hook / skill / governance capability, conformant to `GOV-HARNESS-ONBOARDING-CONTRACT-001`. Per owner direction, the dispatchable unit is the model, not the GUI: the Goose desktop GUI (identity G) is the current interim stopgap, and the target is a non-GUI, hook-capable integration. This slice authors `ADR-DEEPSEEK-ALIBABA-HARNESS-ADOPTION-001` recording (a) the adoption decision, (b) the fail-closed guard architecture, (c) the headless dispatch mechanism, and (d) the harness-identity decision (repurpose Goose G vs. register a model-provider identity). No source guard code is written in this slice; the ADR is the deliverable.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below derives tests from the linked specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline govern this proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — adoption work is modeled as durable artifacts (project, ADR, WIs, candidate principle) rather than transient conversation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability is preserved across the project, ADR, WIs, deliberations, and candidate spec.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the superseded Goose-no-role decisions and the superseded GUI-centric proposal are recorded with explicit superseded lifecycle states.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the onboarding contract the harness must satisfy (Layers 1-3); this project's target conformance standard.
- `GOV-20` (Architecture Decision Governance) — governs ADR authoring; `ADR-DEEPSEEK-ALIBABA-HARNESS-ADOPTION-001` is created under this workflow.
- `GOV-ARTIFACT-APPROVAL-001` — the ADR is a formal artifact requiring a formal-artifact-approval packet before MemBase insert.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — Prime Builder / Loyal Opposition are portable harness-assigned roles.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — capable harnesses are prepared for PB and LO roles; the maximal-hook target serves this.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` and `DCL-OLLAMA-TOOL-PARITY-GATE-001` — precedent adoption ADR + fail-closed guard-adapter contract; the DeepSeek guard mirrors this (a GT-KB python shim mediating every mutating tool call through the canonical guard scripts). Slice 3 authors the analogous `DCL-DEEPSEEK-ALIBABA-TOOL-PARITY-GATE-001`.
- `.claude/rules/project-root-boundary.md` — all adoption artifacts remain within `E:\GT-KB`; the guard shim (slice 3) resolves external harness executables only under the registry-enumerated External Harness Executable Resolution Exception.

## Prior Deliberations

- `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION` (owner_decision, 2026-07-08) — the owner direction that reframes this work: harness = integration+model+config; prefer non-GUI, maximal-hook integrations; GUI harnesses are interim; applies to Goose/Antigravity/Ollama.
- `INTAKE-6308b73f` (requirement_candidate, deferred) — the candidate governing principle capturing the harness=integration+model+config rule + non-GUI/maximal-hook preference, awaiting owner confirmation. The ADR references this candidate.
- `DELIB-20260708-GOOSE-PROMOTE-TO-OPERATING-HARNESS` (owner_decision) — authorized promotion to a headless-dispatchable operating harness (refined by the non-GUI direction above: the promotion target is the non-GUI model harness, not the GUI).
- `DELIB-FAB16-GOOSE-NO-ROLE-OPENROUTER-SDK-20260611` and `DELIB-FAB16-REMEDIATION-20260610` — SUPERSEDED standing decisions (Goose = no-role OpenRouter desktop UI). The ADR records these as prior position + supersession, including the accepted OpenRouter-F / Ollama-D commercial overlap (same model, different rates/terms = distinct harnesses).
- `DELIB-20260708-GOOSE-PARITY-ASSESSMENT-REVIEW` — PB acceptance check that found the harness NON-CONFORMANT (blocking Layers 2 & 3) and surfaced the guard-adapter architectural gap.
- Superseded proposal: `bridge/gtkb-goose-harness-adoption-slice1-adr-001.md` (WITHDRAWN) — the earlier GUI-centric framing of this same Slice-1 deliverable, replaced by this model-centric framing.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-HARNESS-ONBOARDING-CONTRACT-001` defines the conformance target (Layers 1-3); `GOV-20` defines the ADR workflow; the owner direction `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION` fixes the non-GUI / maximal-hook intent. The candidate principle `INTAKE-6308b73f` is a requirement candidate pending owner confirmation; this slice does not depend on its confirmation (it references it as motivating context). No new or revised requirement blocks this slice; the ADR is a decision artifact authored under existing governance.

## Proposed Change / Scope

On GO, author `ADR-DEEPSEEK-ALIBABA-HARNESS-ADOPTION-001` (MemBase spec, `type=architecture_decision`) via the governed formal-artifact flow (approval packet at the declared target path). The ADR records:

1. **Decision:** integrate the Alibaba-hosted DeepSeek V4 Pro model as a non-GUI, headless-dispatchable GT-KB operating harness with maximal hook/skill/governance capability; Goose desktop GUI is interim provenance, not the end-state; supersede the Goose-no-role decisions.
2. **Harness-identity decision:** whether to repurpose registry identity G (currently `goose-desktop`, no model pin, interactive-only) into a non-GUI DeepSeek/Alibaba harness type, or register a distinct model-provider identity and retire/repoint G. Record the (integration+model+config) uniqueness rationale — DeepSeek V4 Pro via Alibaba is a distinct harness from the same model via OpenRouter (F) or Ollama (D) due to differing commercial rates/terms.
3. **Guard architecture:** mirror the Ollama/Cursor precedent — a GT-KB python shim that MUST route every mutating tool call (Write/Edit/Bash) through the canonical guard scripts (project-root containment, credential scan, bridge-compliance-gate, narrative-artifact-approval-gate, implementation-start-gate, destructive-gate, formal-artifact-approval-gate) before mutation, fail-closed. Explicitly target **maximal hook support** (fuller than a shim-only guard where the integration surface allows). Formalized in slice 3 as `DCL-DEEPSEEK-ALIBABA-TOOL-PARITY-GATE-001`.
4. **Dispatch mechanism:** record the concrete headless invocation surface (registry `invocation_surfaces.headless.argv` pointing at the shim) and its execution path against the Alibaba DeepSeek endpoint, including the accepted commercial overlap with the OpenRouter-F and Ollama-D routes of the same model.
5. **Alternatives considered + rejected:** GUI-centric Goose promotion (superseded by owner non-GUI direction); interactive-only operating harness (rejected — owner wants dispatcher availability); scoped Layer-3 waiver (rejected); status-quo no-role UI (superseded).
6. **Consequences + slice plan:** enumerates slices 2 (capability-floor block + glossary + operating-model §3), 3 (guard shim + `DCL-DEEPSEEK-ALIBABA-TOOL-PARITY-GATE-001` + maximal hooks), 4 (`_check_*_harness` doctor check + parity + tests). Notes Antigravity (Gemini) and Ollama (Kimi) as sibling non-GUI/maximal-hook projects following the same pattern.

## Owner Decisions / Input

- `AskUserQuestion` (2026-07-08): dispose of Goose onboarding non-conformance → **File tracking work item** (WI-5072).
- `AskUserQuestion` (2026-07-08): WI-5072 premise vs standing decisions → **Supersede: promote Goose to real harness** (`DELIB-20260708-GOOSE-PROMOTE-TO-OPERATING-HARNESS`).
- `AskUserQuestion` (2026-07-08): operating target → **Headless-dispatchable operating harness** (accepting OpenRouter-F / Ollama-D commercial overlap).
- Owner direction (2026-07-08, `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION`): harness = integration+model+config; prefer non-GUI, maximal-hook integrations; GUI harnesses are interim; applies across Goose/Antigravity/Ollama.
- `AskUserQuestion` (2026-07-08): reconcile in-flight proposal → **Reframe Goose slice + capture principle** (this proposal; candidate principle `INTAKE-6308b73f`).

These answers are the sole authorization for this proposal; implementation of each slice remains gated by Loyal Opposition GO plus an implementation-start packet, and formal-artifact creation remains gated by `GOV-ARTIFACT-APPROVAL-001` packets.

## Specification-Derived Verification

Slice 1's deliverable is the ADR (a decision artifact); its verification is a **spec-to-test mapping** of inspection assertions derived from the linked specifications. Executable `python -m pytest` coverage for harness conformance lands in slice 4 (the `_check_*_harness` doctor check plus a `test_deepseek_alibaba_harness.py` regression asserting Layer 2/3); this slice's spec-to-test mapping is:

| Linked spec | Derived test / assertion | Command / evidence |
|---|---|---|
| `GOV-20` | ADR exists with `type=architecture_decision` and non-empty Decision / Rationale / Alternatives / Consequences | `gt spec show ADR-DEEPSEEK-ALIBABA-HARNESS-ADOPTION-001` |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | ADR names all L1 required artifacts for the harness (capability-floor block, guard adapter, glossary, operating-model §3, ADR, doctor check) and assigns each to a slice | inspection of ADR Consequences |
| `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION` | ADR records the non-GUI + maximal-hook target and the harness=integration+model+config uniqueness rationale | inspection of ADR Decision |
| `GOV-ARTIFACT-APPROVAL-001` | formal-artifact-approval packet exists at the declared target path with matching content hash | inspection of the target packet |

No source is modified in this slice, so there is no `pytest`/`ruff` code gate to run here; the executable regression (`test_deepseek_alibaba_harness.py`, `python -m pytest`, `ruff check`) is defined and run in slice 4.

## Acceptance Criteria

1. `ADR-DEEPSEEK-ALIBABA-HARNESS-ADOPTION-001` authored in MemBase under GOV-20 with the six content elements above.
2. ADR records the non-GUI / maximal-hook target, the harness=integration+model+config uniqueness rationale, and the harness-identity decision (repurpose G vs new identity).
3. ADR records the supersession of the two Goose-no-role deliberations and the GUI-centric proposal, and the accepted commercial overlap with OpenRouter-F / Ollama-D.
4. ADR scopes slices 2-4 with named target artifacts and names Antigravity/Ollama as sibling projects.
5. Formal-artifact-approval packet present at the declared target path (content-hash match).

## Risks / Rollback

- **Risk:** the headless dispatch mechanism against the Alibaba DeepSeek endpoint may prove infeasible or fully redundant with the OpenRouter-F / Ollama-D routes of the same model. **Mitigation:** the ADR records this as an open consequence resolved in slice 3; if slice-3 investigation shows infeasibility or unacceptable redundancy, the ADR is superseded by a follow-on decision rather than shipping a non-functional shim.
- **Risk:** "maximal hook support" for a non-GUI integration of a third-party desktop/CLI product may be bounded by the product's extensibility. **Mitigation:** the ADR records the achievable hook ceiling as a slice-3 finding; the guard-adapter shim is the fail-closed floor regardless.
- **Rollback:** the ADR is append-only in MemBase; a wrong decision is corrected by a superseding ADR, not deletion. No source/config is mutated in this slice.
