NEW

# gtkb-wi5048-openrouter-prime-builder-dispatch-activation — Activate OpenRouter/F for dispatchable Prime Builder work

bridge_kind: prime_proposal
Document: gtkb-wi5048-openrouter-prime-builder-dispatch-activation
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-06 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 66422d1e-3091-47fa-a848-f5468485ec45
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5048-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5048

target_paths: ["harness-state/harness-registry.json", "config/dispatcher/rules.toml"]

implementation_scope: protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Owner-directed (this session): make harness **F (OpenRouter)** a dispatchable
**Prime Builder** so headless PB implementation work can route to it in addition
to the current sole dispatchable PB, harness A (Codex).

F is presently a non-dispatchable Loyal Opposition harness. Activating it for PB
dispatch is a four-surface change, all applied through governed transaction CLIs
(no source/logic edit; the registry JSON is a projection of the MemBase
`harnesses` table and is never hand-edited):

1. **Role** — `gt mode set-role --harness F --role prime-builder`. In
   multi-harness topology the role field is a singleton, so this removes F from
   the Loyal Opposition pool. The active-partition validator still passes: A
   (and now F) hold `prime-builder`; B/C/D/E remain `loyal-opposition`, with D
   and C the dispatchable LO reviewers.
2. **Dispatchability** — `gt bridge dispatch config set-eligibility F
   --can-receive-dispatch`.
3. **Selection tag** — add `prime-builder` to F's `dispatch_tags` and to
   `config/dispatcher/rules.toml [harnesses.F]`; the `bridge-prime-builder-default`
   rule selects only `prime-builder`-tagged harnesses.
4. **Invocation skill** — `gt harness set-invocation-surface` to change F's
   headless argv `--skill bridge-review` → `--skill implementation`. This is
   load-bearing: the dispatcher substitutes only `{{PROMPT}}`/`{{PROJECT_ROOT}}`
   and never swaps the skill by role (confirmed in
   `scripts/dispatcher_runtime.py` argv builder), so without this change a PB
   dispatch to F would run the *review* shim (which authors GO/NO-GO verdicts)
   against *implementation* work. `.api-harness/routing.toml` already defines an
   `implementation` OpenRouter skill route, so the shim supports it.

**Model:** no `.api-harness/routing.toml` model edit is required. The owner
confirmed (AUQ) that OpenRouter overrides the invoker-specified model with **Kimi
K2.7 Code** at the account/proxy layer, so whatever model the shim names is
ignored. The routing row remains `deepseek-v4-pro`; see the provenance caveat in
Risk / Rollback.

## Specification Links

- `GOV-HARNESS-ROLE-PORTABILITY-001` — establishes that Prime Builder and Loyal
  Opposition are portable, harness-assigned roles; this proposal exercises that
  portability by assigning `prime-builder` to F.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — requires GT-KB installs to prepare
  capable harnesses for the PB and LO roles; wiring F for PB dispatch directly
  serves this, adding a second dispatchable PB.
- `REQ-HARNESS-REGISTRY-001` — governs the harness registry role and
  invocation-surface contract that the role / eligibility / tag / argv edits
  mutate through the canonical projection.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority under which this
  proposal and its dispatcher/TAFE state are recorded.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal carries
  Project + Work Item + Project Authorization linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below
  derives checks from each linked specification.
- `GOV-STANDING-BACKLOG-001` — WI-5048 is the governing backlog authority for
  this work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — this change is executed as
  a durable artifact chain (owner-decision deliberation → work item → project
  authorization → this proposal) rather than transient config edits.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented
  development stance backing the deliberation/WI/PAUTH chain for this change.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle triggers for the
  candidate work item and the owner-decision capture that authorize this filing.

## Prior Deliberations

- `DELIB-OPENROUTER-F-PB-ACTIVATION-20260706` — this session's owner-decision
  record: the directive, the AUQ model-override clarification, and the selection
  of the bridge WI+proposal path. This proposal is its direct execution.
- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` — the sibling Ollama/D route
  switch (WI-5047). Establishes that `kimi-k2-7-code-cloud` is an **Ollama**
  route and that OpenRouter/F was explicitly to remain untouched there; this
  proposal is the deliberate, separately-authorized OpenRouter/F change.
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-003.md` — the
  sibling bridge thread; same change class (harness dispatch config) reviewed
  through the same protocol.
- `PROJECT-HARNESS-EQUIVALENCE-PHASE-3` (model-identity divergence:
  `bridge/harness-equivalence-phase-3-umbrella-001.md`) — documents the OpenRouter
  UI-shows-Kimi vs headless-routes-deepseek divergence that motivates the
  provenance caveat below.
- `INTAKE-da01f846` (harness active/suspended means dispatchability only) —
  supports treating role, status, and dispatchability as orthogonal axes; F
  gains PB dispatchability by explicit eligibility, not by role alone.

## Owner Decisions / Input

This proposal depends on owner direction and is authorized by
`DELIB-OPENROUTER-F-PB-ACTIVATION-20260706` (AskUserQuestion, this session):

- **Directive:** "Activate OpenRouter for dispatchable PB work."
- **AUQ Q1 (Model):** Owner answered that OpenRouter overrides the invoker model
  with Kimi K2.7 Code at the account/proxy layer, so no `.api-harness/routing.toml`
  model edit is required (correcting the initial "configured to use
  kimi-k2-7-code" premise, which did not hold against the canonical routing SoT).
- **AUQ Q2 (Proceed path):** Owner selected "File a bridge WI + proposal
  (Recommended)" — WI-5048 + this NEW proposal → Loyal Opposition GO →
  implement, consistent with sibling WI-5047.

No further owner decision is required to review this proposal. A separate
source/test authorization (post-GO) will be requested only if implementation is
found to require source changes beyond the governed-CLI config edits.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-HARNESS-ROLE-PORTABILITY-001`,
`GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`, and `REQ-HARNESS-REGISTRY-001` already
govern portable role assignment and the harness registry role / invocation-surface
contract. Activating F for PB dispatch applies these existing requirements; no new
or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

All checks are read-only state assertions plus existing dispatcher regression;
this is a config-only change with no new source or tests.

- `GOV-HARNESS-ROLE-PORTABILITY-001` / `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` →
  `gt harness roles` shows F `role=[prime-builder]`; `gt bridge dispatch status`
  lists F among `prime-builder` eligible/selected candidates. Expected: F present
  in the PB pool; at least one LO harness remains dispatchable (D, C).
- `REQ-HARNESS-REGISTRY-001` → `gt harness show F` shows
  `can_receive_dispatch=true`, `dispatch_tags` contains `prime-builder`, and the
  headless argv contains `--skill implementation` (not `bridge-review`);
  `config/dispatcher/rules.toml [harnesses.F].tags` contains `prime-builder`.
- Doctor → `gt project doctor` role-set-topology and dispatcher-config checks
  PASS (no partition/topology regression).
- Dispatcher regression →
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --no-header`
  green (selection/routing invariants preserved).
- End-to-end PB-loop smoke (staged, owner-visible) → a single controlled PB
  dispatch to F confirms it (a) invokes `--skill implementation`, and (b) can
  complete the PB loop (work-intent claim → `implementation_authorization begin`
  → edit → ruff/tests → scoped commit → post-impl report). Treated as an
  acceptance gate, not an assumption — see Risk (c).

## Risk / Rollback

- **(a) Reliability / hang history.** OpenRouter shim LO workers are known to
  stall 44–60 min (one LO worker is stalled ~24 min at 0 output as of filing).
  As a PB implementer a hang holds an implementation slot and may leave partial
  worktree state. Mitigation: F `max_items=1` (single concurrent), PB worker
  lifetime cap (5400s) bounds runaway; monitor the first PB dispatches; a
  shorter F-specific PB lifetime may be warranted.
- **(b) Timeout mismatch.** `[routing.openrouter].timeout_seconds = 240` vs PB
  implementation worker lifetime 5400s. If the 240s value bounds the shim
  session (not just a single call), PB implementation would abort early.
  Implementation must confirm the semantics and raise the OpenRouter session
  timeout for implementation dispatch if required.
- **(c) Shim PB-loop capability.** The framework-free shim has only ever run the
  review skill. Its ability to complete the full PB implementation loop is
  unverified and is gated by the end-to-end smoke above; F must not be relied on
  for PB dispatch until that passes.
- **(d) Provenance caveat.** Because OpenRouter overrides the model to Kimi K2.7
  Code while `author_model` still stamps the routing row (`deepseek-v4-pro`),
  F-authored artifacts will mis-record the model — the known phase-3
  model-identity divergence. Non-blocking; flagged for a follow-up provenance
  reconciliation (candidate: a Kimi-labeled OpenRouter routing row or a
  provenance override).
- **Rollback.** Single reversible step per surface via the same governed CLIs:
  role → `loyal-opposition`, `--no-can-receive-dispatch`, remove the
  `prime-builder` tag, and argv `--skill implementation` → `bridge-review`,
  restoring F's prior non-dispatchable-LO configuration. No source is touched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5048-openrouter-prime-builder-dispatch-activation`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore(dispatch)` — the implementation is an operational dispatch-configuration
change applied entirely through governed transaction CLIs (`gt mode set-role`,
`gt harness set-invocation-surface`, `gt bridge dispatch config set-eligibility`);
it touches only `harness-state/harness-registry.json` (a projection) and
`config/dispatcher/rules.toml`, with no source or logic added. (If Loyal
Opposition judges the new PB-dispatch capability warrants `feat(dispatch)`, that
is a reasonable alternative; the choice is declared here for transparency per the
commit-type discipline.)

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
