NEW
author_identity: claude
author_harness_id: B
author_session_context_id: claude-interactive-20260708-goose-slice1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Goose Harness Adoption — Slice 1: Adoption ADR + Guard/Dispatch Architecture

Work Item: WI-5073
Umbrella Work Item: WI-5072
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260708
target_paths: [".groundtruth/formal-artifact-approvals/2026-07-08-ADR-GOOSE-HARNESS-ADOPTION-001.json"]

## Summary

Slice 1 of promoting Goose (harness identity G) from a no-role desktop UI to a genuine GT-KB **headless-dispatchable operating harness** conformant to `GOV-HARNESS-ONBOARDING-CONTRACT-001`. This slice authors the foundational Architecture Decision Record `ADR-GOOSE-HARNESS-ADOPTION-001` recording (a) the owner decision to promote Goose, (b) the adopted fail-closed guard architecture, and (c) the headless dispatch mechanism — which together scope the remaining slices (capability-floor block, guard shim + tool-parity DCL, glossary + operating-model entry, doctor check). No source guard code is written in this slice; the ADR is the deliverable.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below derives tests from the linked specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline govern this proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — adoption work is modeled as durable artifacts (project, ADR, WIs) rather than transient conversation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability is preserved across the project, ADR, WIs, deliberations, and slices.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the superseded Goose-no-role decisions are recorded with an explicit superseded lifecycle state.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the onboarding contract Goose must satisfy (Layers 1-3); this project's target conformance standard.
- `GOV-20` (Architecture Decision Governance) — governs ADR authoring; ADR-GOOSE-HARNESS-ADOPTION-001 is created under this workflow.
- `GOV-ARTIFACT-APPROVAL-001` — the ADR is a formal artifact requiring a formal-artifact-approval packet before MemBase insert.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` — precedent adoption ADR (first concrete adoption of the onboarding contract); structural template.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` — precedent fail-closed guard-adapter contract; the Goose guard mirrors this (a GT-KB python shim mediating every mutating tool call through the canonical guard scripts). Slice 3 will author the analogous `DCL-GOOSE-TOOL-PARITY-GATE-001`.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — Prime Builder / Loyal Opposition are portable harness-assigned roles; Goose may hold an operating role.
- `.claude/rules/project-root-boundary.md` — all adoption artifacts remain within `E:\GT-KB`; the guard shim (slice 3) resolves external harness executables only under the registry-enumerated External Harness Executable Resolution Exception.
- `.claude/rules/canonical-terminology.md` / `DCL-CONCEPT-ON-CONTACT-001` — the "goose" operating-harness concept requires a glossary entry (authored in slice 2, named here as a consequence).

## Prior Deliberations

- `DELIB-20260708-GOOSE-PROMOTE-TO-OPERATING-HARNESS` (owner_decision, 2026-07-08) — the owner authorization for this project; directs promotion to a headless-dispatchable operating harness and supersedes the Goose-no-role decisions.
- `DELIB-FAB16-GOOSE-NO-ROLE-OPENROUTER-SDK-20260611` and `DELIB-FAB16-REMEDIATION-20260610` — the SUPERSEDED standing decisions (Goose = no-role OpenRouter desktop UI). The ADR must record these as the prior position and the supersession, including the accepted OpenRouter-F headless overlap.
- `DELIB-20260708-GOOSE-PARITY-ASSESSMENT-REVIEW` — the PB acceptance check that found Goose NON-CONFORMANT (blocking Layers 2 & 3) and surfaced the guard-adapter architectural gap.
- `INTAKE-97211546` — harness registrar role assignment + independent-review requirement; relevant because the 2026-07-08 registration originated from a Goose self-authored assessment (a harness recommending its own promotion), which the ADR should note as a governance lesson.
- Precedent adoption threads: the Ollama Phase-1 integration bridge-thread series (Ollama adoption, ADR + tool-parity DCL + doctor-check pattern).

## Requirement Sufficiency

Existing requirements sufficient. `GOV-HARNESS-ONBOARDING-CONTRACT-001` fully defines the conformance target (Layers 1-3), and `GOV-20` defines the ADR workflow. No new or revised requirement is needed before this slice; `ADR-GOOSE-HARNESS-ADOPTION-001` is a decision artifact authored under existing governance, not a new requirement. `DCL-GOOSE-TOOL-PARITY-GATE-001` (slice 3) is a derived design constraint, not a new owner requirement.

## Proposed Change / Scope

On GO, author `ADR-GOOSE-HARNESS-ADOPTION-001` (MemBase spec, `type=architecture_decision`) via the governed formal-artifact flow (`gt spec record` with a formal-artifact-approval packet at the declared target path). The ADR records:

1. **Decision:** Goose (G) is a headless-dispatchable GT-KB operating harness; supersede the Goose-no-role decisions.
2. **Guard architecture:** mirror the Ollama/Cursor precedent — a GT-KB python shim a Goose python shim (slice 3) that MUST route every mutating tool call (Write/Edit/Bash) through the canonical guard scripts (project-root containment, credential scan, bridge-compliance-gate, narrative-artifact-approval-gate, implementation-start-gate, destructive-gate, formal-artifact-approval-gate) before mutation, fail-closed. Formalized in slice 3 as `DCL-GOOSE-TOOL-PARITY-GATE-001`.
3. **Dispatch mechanism:** record the concrete headless invocation surface (registry `invocation_surfaces.headless.argv` pointing at a Goose python shim (slice 3)) and its execution path relative to the OpenRouter-F SDK dispatch path, including the accepted overlap.
4. **Alternatives considered + rejected:** interactive-only operating harness (rejected per owner AUQ); scoped waiver of Layer 3 (rejected); status-quo no-role UI (superseded).
5. **Consequences + slice plan:** enumerates slices 2 (capability-floor block + glossary + operating-model §3), 3 (guard shim + `DCL-GOOSE-TOOL-PARITY-GATE-001`), 4 (`_check_goose_harness` doctor check + parity + tests).

## Owner Decisions / Input

- `AskUserQuestion` (2026-07-08): "How should I dispose of the Goose onboarding non-conformance?" → **File tracking work item** (WI-5072 created).
- `AskUserQuestion` (2026-07-08): "WI-5072's build-to-conformance premise contradicts your standing decisions … how should I scope the proposal?" → **Supersede: promote Goose to real harness** (captured as `DELIB-20260708-GOOSE-PROMOTE-TO-OPERATING-HARNESS`).
- `AskUserQuestion` (2026-07-08): "What operating target should Goose be promoted to?" → **Headless-dispatchable operating harness** (accepting the OpenRouter-F overlap; guard = Ollama/Cursor shim pattern).

These answers are the sole authorization for this proposal; implementation of each slice remains gated by Loyal Opposition GO plus an implementation-start packet, and formal-artifact creation remains gated by `GOV-ARTIFACT-APPROVAL-001` packets.

## Specification-Derived Verification

Slice 1's deliverable is the ADR (a decision artifact); its verification is a **spec-to-test mapping** of inspection assertions derived from the linked specifications. Executable `python -m pytest` coverage for Goose conformance lands in slice 4 (the `_check_goose_harness` doctor check plus a `test_goose_harness.py` regression asserting Layer 2/3); this slice's spec-to-test mapping is:

| Linked spec | Derived test / assertion | Command / evidence |
|---|---|---|
| `GOV-20` | ADR exists with `type=architecture_decision` and non-empty Decision / Rationale / Alternatives / Consequences | `gt spec show ADR-GOOSE-HARNESS-ADOPTION-001` |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | ADR names all L1 required artifacts for Goose (capability-floor block, guard adapter, glossary, operating-model §3, ADR, `_check_goose_harness`) and assigns each to a slice | inspection of ADR Consequences |
| `GOV-ARTIFACT-APPROVAL-001` | formal-artifact-approval packet exists at the declared target path with matching content hash | inspection of the target packet |

No source is modified in this slice, so there is no `pytest`/`ruff` code gate to run here; the executable regression (`test_goose_harness.py`, `python -m pytest`, `ruff check`) is defined and run in slice 4 against the guard shim + doctor check.

## Acceptance Criteria

1. `ADR-GOOSE-HARNESS-ADOPTION-001` authored in MemBase under GOV-20 with the five content elements above.
2. ADR records the supersession of the two Goose-no-role deliberations and the accepted OpenRouter-F overlap.
3. ADR scopes slices 2-4 with named target artifacts.
4. Formal-artifact-approval packet present at the declared target path (content-hash match).

## Risks / Rollback

- **Risk:** the headless dispatch mechanism for a Goose python shim (slice 3) may prove infeasible or fully redundant with OpenRouter-F. **Mitigation:** the ADR records this as an open consequence resolved in slice 3; if slice-3 investigation shows infeasibility, the ADR is superseded by a follow-on decision (interactive-only or waiver) rather than shipping a non-functional shim.
- **Rollback:** the ADR is append-only in MemBase; a wrong decision is corrected by a superseding ADR, not deletion. No source/config is mutated in this slice, so there is nothing to revert beyond a superseding formal-artifact record.
