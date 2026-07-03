NO-GO

# WI-4985 Codex Headless Write Boundary — Proposal Review Verdict

bridge_kind: lo_verdict
Document: gtkb-wi4985-codex-headless-write-boundary
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4985-codex-headless-write-boundary-001.md (NEW)
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 901d970b-b437-4794-83bc-b84ac044f8d9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; ::init gtkb lo; ::open build; auto-process loop; resolved role loyal-opposition

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4985-CODEX-HEADLESS-WRITE-BOUNDARY
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4985

---

## Verdict Summary

**NO-GO — constructive; the diagnosis and direction are correct, one blocking
fix plus one hygiene fix.** This proposal correctly identifies a real,
runtime-verifiable defect: the Codex-A headless argv (registry projection,
generated 06:11Z) is
`codex exec --model gpt-5.5 -c approval_policy="never" -c model_reasoning_effort="xhigh" {{PROMPT}} --cd {{PROJECT_ROOT}}`
— it pins the model, reasoning, and non-interactive approval policy but carries
**no write-capable sandbox selector**. Under `approval_policy=never` with the
default sandbox, `apply_patch` rejecting an authorized in-root write with
"writing outside of the project; rejected by user approval settings" is the
expected failure. The remediation direction (add a project-root write-capable
sandbox mode while retaining the gpt-5.5 / never / xhigh pins) is sound, and the
change is correctly routed through MemBase (`groundtruth.db`) + projection
regeneration rather than a hand-edit of `harness-registry.json`. Authorization,
Requirement Sufficiency, In-Root Placement, and both preflights are all in
order, and review independence holds. One item blocks GO:

1. **Prior Deliberations placeholder (blocking, mechanical).** The
   `## Prior Deliberations` section is the uncurated auto-loader placeholder
   `_No prior deliberations auto-loaded; author must confirm before review._`,
   which satisfies neither the "candidate entries present" nor the
   `_No prior deliberations: <reason>._` justification condition — a mechanical
   NO-GO trigger under `.claude/rules/codex-review-gate.md` § Prior
   Deliberations Section Requirement. Remediation guidance in N1 below.

## Review Independence

- Proposal (`-001`) author session context: `019f247b-4dc8-7b32-a2ab-25839614d33f` (Codex, harness A).
- Review session context: `901d970b-b437-4794-83bc-b84ac044f8d9` (Claude, harness B).
- Distinct session contexts and distinct harnesses; review independence satisfied.

## Applicability Preflight

- operative_file: `bridge/gtkb-wi4985-codex-headless-write-boundary-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: `sha256:698b0bfb44982588f026754544a62d61af4601b2a2ec49d2cace2fb110a45e4b`

## Clause Applicability (Slice 2; mandatory gate)

- Operative file: `bridge/gtkb-wi4985-codex-headless-write-boundary-001.md`
- Evidence gaps in must_apply clauses: 0; Blocking gaps: 0; exit 0 (pass).

## Findings

### N1 — [P2, BLOCKING] Prior Deliberations uncurated placeholder

- **Observation.** Line 63 is the auto-loader placeholder
  `_No prior deliberations auto-loaded; author must confirm before review._`.
  It carries no candidate entries and is not the `_No prior deliberations:
  <reason>._` justification line.
- **Deficiency rationale.** Per `.claude/rules/codex-review-gate.md`, a NEW/REVISED
  proposal whose Prior Deliberations section is empty AND lacks the justification
  line is a mandatory NO-GO. The section anchors the proposal in prior-decision
  history; the placeholder leaves it unanchored.
- **Proposed solution.** Two acceptable paths:
  (a) **Cite the adjacent history.** This proposal is part of the live
  dispatch-stability / dispatcher-modernization cluster. Relevant priors:
  `DELIB-202665265` (the owner-decision evidence already cited in Owner
  Decisions), `WI-4977` (dispatch-stability, VERIFIED), the
  `gtkb-headless-dispatch-model-pinning` thread (**VERIFIED** — this proposal
  *builds on* its gpt-5.5 / xhigh pins and must preserve them), `WI-4986`
  (model-aware dispatch timers, sibling), and `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
  (Codex headless surface authority). OR
  (b) **Use the justification line.** A Deliberation Archive semantic search this
  session (`"codex headless dispatch write boundary sandbox apply_patch"`)
  returned **no direct matches**, so the explicit-empty convention is legitimate:
  `_No prior deliberations: no DA matches for the Codex headless write-boundary
  topic; adjacent landed/in-flight work is WI-4977 and gtkb-headless-dispatch-
  model-pinning (both VERIFIED) and sibling WI-4986._`
- **Prime Builder context.** Prior Deliberations section only; no source impact.

### N2 — [P3] Generic verification plan + auto-attached spec links

- **Observation.** 10 of 13 verification rows are the identical filler "Run
  candidate and live bridge applicability preflights; implementation report must
  add targeted tests." Several spec links are auto-attached with no concrete
  governing relationship to a Codex sandbox change (e.g.,
  `SPEC-AUQ-POLICY-ENGINE-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`).
- **Proposed solution.** Map concrete per-spec tests for the load-bearing specs:
  an assertion that the Codex headless argv contains the write-capable sandbox
  selector AND still contains `--model gpt-5.5` / `approval_policy=never` /
  `model_reasoning_effort=xhigh` (fail-closed if it regresses to the no-sandbox
  form); a bounded in-root `apply_patch` smoke proving an authorized write
  succeeds post-change; and the `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` mutation-
  class check. Curate the spec-link set to those with a real governing tie.
- **Prime Builder context.** Verification-plan + Specification-Links sections.

## Required Revisions

1. **N1** — Complete Prior Deliberations via path (a) citation or (b) the
   `_No prior deliberations: <reason>._` justification line.
2. **N2** — Concrete per-spec tests (argv sandbox+pins assertion, in-root
   apply_patch smoke, PAUTH mutation-class check); curate spec links.

## Positive Confirmations

- **Premise verified against runtime.** The current Codex-A headless argv lacks a
  write-capable sandbox selector; the `apply_patch` outside-project rejection is
  the expected failure. Diagnosis and remediation direction are correct.
- **Correct mutation path.** Routing the argv change through MemBase
  (`groundtruth.db`) + `harness_projection` regeneration honors the registry's
  "do not hand-edit; regenerate from the harnesses table" contract; listing both
  `groundtruth.db` and `harness-state/harness-registry.json` in `target_paths` is
  right for this change.
- Authorization (PAUTH cited, Project, WI-4985), Requirement Sufficiency, In-Root
  Placement evidence, both preflights (applicability
  `packet_hash sha256:698b0bfb…`; clause exit 0), and independence are all in
  order. Recommended commit type `feat` is appropriate.
- **No scope conflict.** `gtkb-headless-dispatch-model-pinning` is VERIFIED
  (landed), so this proposal extends completed work rather than colliding with an
  in-flight thread; no backlog-conflict finding is raised.

## Prior Deliberations

- Deliberation Archive semantic search this session
  (`"codex headless dispatch write boundary sandbox apply_patch"`) returned no
  direct matches.
- Governing/adjacent records: `DELIB-202665265` (owner-decision evidence, cited
  in the proposal), `WI-4977` (dispatch-stability, VERIFIED),
  `gtkb-headless-dispatch-model-pinning` (VERIFIED; this proposal preserves its
  pins), sibling `WI-4986` (model-aware dispatch timers, NO-GO),
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (Codex headless surface authority).

## Commands Executed

```
gt bridge show gtkb-wi4985-codex-headless-write-boundary        # NEW at -001
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4985-codex-headless-write-boundary   # preflight_passed: true; packet_hash sha256:698b0bfb…
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4985-codex-headless-write-boundary          # exit 0
gt bridge show gtkb-headless-dispatch-model-pinning             # VERIFIED (overlap check → no conflict)
gt deliberations search "codex headless dispatch write boundary sandbox apply_patch"   # no matches
# runtime evidence: harness-registry.json projection Codex-A headless argv has no write-capable sandbox selector
```

## Owner Decisions / Input

- Standing LO authority over actionable NEW bridge entries; no new owner decision
  required for this NO-GO. Owner-decision evidence `DELIB-202665265` is cited by
  the proposal and governs the underlying WI-4985 authorization.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
