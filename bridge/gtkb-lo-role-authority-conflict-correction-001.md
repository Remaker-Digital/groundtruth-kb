ADVISORY
author_session_context_id: 019fbbaf-1da4-74c3-a48a-c287cbe4361f

# Advisory Proposal — Loyal Opposition Role-Authority Conflict Correction

bridge_kind: governance_advisory
Document: gtkb-lo-role-authority-conflict-correction
Version: 001
Date: 2026-08-01 UTC

## Source Advisory

Owner direction in this interactive session: Codex is Loyal Opposition. Any
source that assigns a different role conflicts with that explicit direction
and is preserved here for corrective action. The owner further established
that session-context independence is the sole formal worker constraint.

## Evidence

1. `harness-state/harness-registry.json` records Codex harness A as
   `prime-builder`, in conflict with the owner's current explicit Loyal
   Opposition direction.
2. Before the root-envelope correction, `session envelope show --harness-name
   codex` returned a stale open Prime Builder envelope. The current envelope
   records the owner's `::init gtkb lo` direction instead.
3. `bridge/gtkb-wi5723-session-resolver-fallback-removal-003.md` and
   `bridge/gtkb-wi5815-per-session-envelope-claim-isolation-003.md` show
   NO-ACTION stale-GO closure patterns tied to Prime Builder envelope state.
4. `bridge/gtkb-modernization-rc-evidence-closure-021.md` and
   `bridge/gtkb-research-clean-branch-publication-005.md` use a Prime Builder
   label while attempting to terminally dispose of otherwise live threads
   through NO-ACTION.
5. Existing open `WI-5834` records an interactive role being overwritten by
   `session_resolver_fallback`; `DELIB-202667742` records emergency repair
   authority for role persistence.

## Claim

The sole formal worker constraint is session-context independence: a session
context must never formally review work that same session context previously
produced. Harness identity, durable role mappings, dispatcher selection,
prompts, session envelopes, and role labels have no relationship to formal
review authority. Any worker restriction or GOV rule exceeding that boundary
is erroneous and needs corrective disposition.

## Risk / Impact

Role-based gates can misroute bridge work and fabricate a review-authority
restriction the owner rejected. They can also obscure the only fact that
matters for a formal review: whether author and reviewer session contexts are
the same.

## Recommended Next Artifact Path

Re-evaluate `WI-5834` and `WI-5723` against this owner direction; preserve
the Codex-A registry/envelope conflict as evidence and remove or correct
role- and harness-based restrictions. Correct live NO-ACTION threads without
treating role or harness metadata as review eligibility.

## Prior Deliberations

- `DELIB-20265225` — interactive transcript-defined session role.
- `DELIB-202667477` — transcript-only continuity for interactive role
  persistence.
- `DELIB-202667742` — emergency repair authorization for interactive role
  persistence across session boundaries.

## Non-Approval

This ADVISORY preserves a corrective finding only. It neither approves
implementation nor changes non-bridge files.
