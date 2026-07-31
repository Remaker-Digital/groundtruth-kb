author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 71381938-7713-42d8-b354-7ba25a5d8036
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

# LO Advisory — Cross-Harness Parity Goal Language + Fleet-State Findings

- Date: 2026-07-13 16:41 UTC
- Role: Loyal Opposition (harness B, claude-opus-4-8), interactive
- Session context: 71381938-7713-42d8-b354-7ba25a5d8036
- Specs: GOV-HARNESS-ONBOARDING-CONTRACT-001, ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, SPEC-CENTRALIZED-DISPATCH-SERVICE-001
- WIs: WI-5211 (referenced), WI-5222 (referenced), WI-4865 (parity program)
- Report kind: advisory + deliverable capture; no bridge/registry/KB mutation performed this session

## Session Summary

Owner-directed editorial task: improve the language of a cross-harness parity
goal. Produced a finalized goal statement (below). Along the way, verified live
bridge/harness state and surfaced two fleet-state findings. No mutations were
made: WI-5211-f was stood down (reserved for harness F), WI-5222 was read but
not reviewed, and the owner ended the session (`::wrap`) before authorizing any
of the follow-on actions offered.

## Deliverable — Finalized Cross-Harness Parity Goal Language

Owner decisions that fixed the wording (this session, in chat):
1. Honor the owner-calibrated **60-minute** D/F/H execution allowance
   (`DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE`), not "preserve"
   the superseded 8-hour value.
2. Reading **2b** — each in-scope harness must prove genuine governed operation
   in **both** Prime Builder and Loyal Opposition roles (capability parity),
   not only its currently-assigned role.
3. Cursor **E** out of scope (unavailable for the foreseeable future); Goose
   **G** excluded as a phantom (no real harness).

Final goal (full form):

> Prove that every real, available fleet harness — Codex **A**, Claude Code **B**,
> Antigravity **C**, Ollama **D**, OpenRouter **F**, and Alibaba **H** — performs
> **genuine, dispatcher-produced governed bridge work in both the Prime Builder
> and Loyal Opposition roles**. *Genuine* means a committed, substantive,
> target-authored bridge artifact — never a READY marker, canned response, or
> raw bridge-file write. (Cursor **E** is out of scope while unavailable; Goose
> **G** is a phantom registry record with no real harness and is excluded pending
> retirement.)
>
> Remediate every defect that **blocks** genuine governed operation through the
> full governed lifecycle — work item → spec-derived test → PAUTH → bridge
> proposal → GO → implementation → testing → independent verification →
> hunk-scoped focused commit — capturing non-blocking incidental defects to the
> backlog rather than widening scope.
>
> Complete the cross-harness parity phases (per
> `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` and the Phase-2 release-blocker
> directive `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE`) and restore
> healthy dispatch eligibility (`gt bridge dispatch health` returns to PASS for
> the six in-scope harnesses) while honoring the owner-calibrated generous D/F/H
> execution allowance — the 60-minute model window per
> `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE`, superseding the prior
> 8-hour value.
>
> **Done when:** each in-scope harness has at least one committed genuine governed
> proof in **each** role (Prime Builder and Loyal Opposition); the cross-harness
> parity phases are marked complete; `gt bridge dispatch health` reports PASS; and
> no blocking defect remains open.

Scope implication of 2b (flagged, not yet decided): dispatcher-produced work
routes by a harness's dispatcher/**default** role, and each harness holds only
one at a time. Proving a harness's non-default role therefore requires a governed
`gt mode set-role` flip for that harness at proof time. The proof set roughly
doubles (≈12 proofs: 6 harnesses × 2 roles).

## Finding 1 — Phantom harness G (goose) [P2, governance]

### Observation
The MemBase harnesses table still carries record **G** (`harness_name: goose`,
`harness_type: goose-desktop`, `status: suspended`, role `[loyal-opposition]`,
version 8) — visible in `harness-state/harness-registry.json` lines ~346-404.
Owner confirmed this session that goose "is a phantom and that harness doesn't
actually exist."

### Deficiency Rationale
This matches the canonical *Phantom Artifact* definition (a tracked entity with
no backing reality). It skews fleet-health signals: G is one of two `suspended`
records and inflates the harness count / parity denominators. It also appears to
be leftover from `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION` being redirected to the
Alibaba (H) adoption (H `harness_type: claude`, model `alibaba-deepseek-v4-pro`;
G `harness_type: goose-desktop`, model `goose-deepseek-v4-pro`).

### Proposed Solution
Retire record G via the governed path (`gt harness retire`), not a hand-edit of
the projection JSON (the file header forbids hand-edits; SoT is the MemBase
harnesses table). Confirm no live dispatcher rule / PAUTH still references G
before retirement.

### Option Rationale
Governed retirement preserves the append-only audit trail and regenerates the
projection cleanly. A hand-edit of `harness-registry.json` would violate the
"do not hand-edit; regenerate" contract and drift the projection from MemBase.

## Finding 2 — F "suspension" is on the dispatch-eligibility axis, not lifecycle [P2]

### Observation
Owner asked to "update the TAFE" because "OpenRouter is no longer suspended."
Canonical MemBase record `gt harness show --harness F` (rowid 315, version 41)
shows `status: active` already, but `can_receive_dispatch: false`, last changed
`2026-07-12T21:40:00Z` by `gt-bridge-dispatch-config-cli` with reason
"set dispatch eligibility via gt bridge dispatch config". All eight harnesses
currently have `can_receive_dispatch: false`; `gt bridge dispatch health` = FAIL,
selected candidates = (none), operator quiesce = cleared.

### Deficiency Rationale
The owner's mental model ("suspended") maps to the **dispatch-eligibility** axis,
not the lifecycle `status` axis. Running `gt harness resume F` would be a no-op /
error (F is already `active`) and would not restore dispatch. The correct lever
is `gt bridge dispatch config` to set F `can_receive_dispatch: true`.

### Proposed Solution
Set F dispatch eligibility to true via `gt bridge dispatch config` (the same CLI
that set it false on 2026-07-12), then confirm `gt bridge dispatch health` and
`gt bridge dispatch status` show F selectable. **NOT performed this session** —
owner ended the session before confirming; this is a governance mutation
affecting fleet dispatch and remains a pending owner-authorized action.

### Option Rationale
`gt bridge dispatch config` is the governed transaction surface for eligibility
and preserves audit provenance; a registry hand-edit is prohibited and a
`gt harness resume/activate` call targets the wrong axis.

## Finding 3 — WI-5211-f stand-down (record only) [informational]

### Observation
`bridge/gtkb-wi5211-f-governed-publication-functional-proof-001.md` (NEW,
`bridge_kind: governance_advisory`, authored by prime-builder/codex/A) is a
harness-functional-proof whose Expected Outcome reserves the verdict for
`author_harness_id: F`.

### Deficiency Rationale
Authoring a GO/NO-GO as harness B would defeat the proof (the proof exists to
demonstrate F can publish a genuine governed verdict). Per the reserved-verdict
stand-down pattern, the correct action for a non-target harness is zero bridge
mutation.

### Proposed Solution
Left untouched. Its resolution depends on Finding 2 — F cannot produce the proof
while `can_receive_dispatch: false`. Restoring F eligibility (Finding 2) is the
prerequisite for this proof to complete.

## Prime Builder / Owner Implementation Context

- Objective: settle parity goal language; restore F dispatch; retire phantom G.
- Evidence paths:
  - `harness-state/harness-registry.json` (F block ~lines 288-345; G block ~346-404)
  - `gt harness show --harness F` (rowid 315, v41)
  - `gt bridge state-report --markdown` (LO-actionable = WI-5211-f, WI-5222)
  - `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-001.md`
- Ordered next steps (all owner-gated; none done this session):
  1. Decide whether to persist the finalized goal as a Deliberation Archive
     owner-decision record and/or a project-goal artifact (approval-packet path).
  2. Authorize F `can_receive_dispatch: true` via `gt bridge dispatch config`.
  3. Authorize governed retirement of phantom harness G.
  4. Route WI-5222 (60-min envelope) through normal LO review once an eligible
     reviewer is available; note WI-5211-f awaits F eligibility.
- Rollback: none required (no state changed).

## Open Owner Decisions (carried forward)

1. Persist parity goal (deliberation and/or spec)? — undecided.
2. Restore F dispatch eligibility now? — undecided (owner's original ask,
   interrupted twice).
3. Capture/retire phantom harness G? — undecided.

## Prior Deliberations

- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` — owner authorization of the
  cross-harness parity program (WI-4865).
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` — Phase 2 as a release
  blocker.
- `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE` — controlling 60-minute
  allowance decision (basis for WI-5222).

Skills applied: codex-report

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
