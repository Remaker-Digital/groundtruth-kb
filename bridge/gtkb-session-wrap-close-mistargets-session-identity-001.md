ADVISORY

# Advisory Proposal — Session Wrap/Close Mis-Targets Session Identity; Envelope Documents Diverge Across Harness Namespaces

bridge_kind: governance_advisory
Document: gtkb-session-wrap-close-mistargets-session-identity
Version: 001
Date: 2026-07-16 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2f6a0618-d857-497d-ac8c-a509f544007e
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; session-stated resolved role Prime Builder; ::init gtkb pb; ::open build. Filed under the same authorship-attribution note as the prior advisory this session: the work-intent claim for this thread resolved session_id 4a5e6c94-bfde-4bfb-bfcf-49a924bdbdb9 (harness scratchpad session id), distinct from this conversation's own session_id used as author_session_context_id. This discrepancy is itself in-scope evidence for the incident described below, not merely a filing footnote.

## Note On Authorship

This document is itself evidence of the very defect class it describes: this session has, across its duration, been unable to get consistent session-identity resolution from the tooling it depends on (see WI-5328 for the role-resolution half; this advisory for the wrap/close half). Filed as a Prime-Builder-authored ADVISORY under direct owner instruction, per the same convention established in this session's first advisory.

## Source

Live incident, this session, 2026-07-16, discovered while executing the owner's `::wrap` explicit hint. Full investigation performed at the owner's direction after the incident was reported.

## Incident Timeline (factual)

1. Owner issued `::wrap`.
2. `/kb-session-wrap` (the full 5-phase owner-triggered procedure named in CLAUDE.md's Session Wrap-Up & Handoff section) is registered `disable-model-invocation` and could not be invoked by this session directly.
3. Ran the deterministic wrap service instead — `gt session wrap --harness-name claude --json` — the mechanism `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` and this project's canonical-terminology.md tie directly to the `::wrap` trigger.
4. The command completed with `wrap_outcome: "manual_wrap"` and no reported error, but it archived and closed **session_id `2026-07-16T07-47-58Z-loyal-opposition-C-93f6ae`** — a different, unrelated, actively-running dispatched worker's session (harness C / antigravity, mid-verification of `WI-5288`'s implementation report) — **not** this conversation's own session (`2f6a0618-d857-497d-ac8c-a509f544007e`).
5. This session's own envelope remains un-wrapped; the owner's original `::wrap` request was not fulfilled by this action.
6. Investigation (at owner direction) confirmed the mis-targeted worker (PID 29796) was still `state: live`, `Responding: True` (direct OS process check), holding an active document lease per the dispatcher's own live-state tracking, mid-verification with normal stdout progress and empty stderr.
7. Investigation found **three separate envelope documents for the same session_id**, one under each of three different harness namespaces:
   - `harness-state/claude/session-envelopes/2026-07-16T07-47-58Z-loyal-opposition-C-93f6ae.json` — mutated by the wrap call: `status: "closed"`, `harness_name: "claude"`, `role: "loyal-opposition"`.
   - `harness-state/codex/session-envelopes/2026-07-16T07-47-58Z-loyal-opposition-C-93f6ae.json` — unaffected: `status: "open"`, `harness_name: "codex"`, `role: "prime-builder"`.
   - `harness-state/cursor/session-envelopes/2026-07-16T07-47-58Z-loyal-opposition-C-93f6ae.json` — unaffected: `status: "open"`, `harness_name: "cursor"`, `role: "loyal-opposition"`.

   One session_id, three documents, three different `role`/`harness_name` combinations. The worker itself self-identifies (in its own startup disclosure) as `Resolved Harness ID: C (antigravity)` — none of the three discovered documents carries that harness name.

## Impact Assessment (evidence-based, not a guarantee)

No observable harm to the mis-targeted worker's in-progress task was found: process alive and responding, dispatcher lease-tracking unaffected (a later dispatch attempt to C was correctly refused with `document_lease_held`), stdout showing normal progress, stderr empty. The specific file mutated (`claude` namespace) is unlikely to be the one a process self-identifying as `antigravity` actually reads for its own provenance checks. This assessment is based on direct evidence gathered after the fact, not on understanding the resolution mechanism well enough to guarantee no risk — in particular, it is not known whether that worker's eventual verdict-finalization step (`write_verdict.py --finalize-verified` or equivalent) consults any of these three documents, or a fourth location not yet found.

## Relationship To WI-5328

Same underlying architectural pattern as `WI-5328` (P0, this session) — ambiguous, non-session-scoped session-identity resolution — but a distinct failure mode. `WI-5328` is about role *resolution* silently falling back to the durable registry role on an open interactive session. This incident is about wrap/close *session-identity selection* grabbing an entirely unrelated session to archive, plus the newly-discovered three-namespace document divergence for a single dispatched-worker session_id, which `WI-5328`'s existing root-cause text does not explain or cover. Recommend cross-referencing, not merging: `WI-5328`'s fix is already precisely scoped (write back the transcript init-keyword before any role-authority check runs) and folding in this unfinished investigation would dilute that scope rather than sharpen it.

## Open Questions (explicitly unresolved — investigation needed before any fix can be scoped)

1. Why do three separate envelope documents exist for one session_id, under three different harness namespaces, with inconsistent `role`/`harness_name` values? Which, if any, is authoritative for a dispatched worker's own provenance checks — and is the answer different for a dispatched worker than for an interactive session?
2. How does `load_current(project_root, harness_name)` (the function `close_session` calls to find "the current envelope" to archive) resolve its result — and why did it resolve to an unrelated dispatched worker's session rather than either this session's own envelope, or failing closed when no unambiguous match exists? This looks like the same "single shared, last-writer-wins path" pattern already implicated in `WI-5328`, but confirming the exact resolution logic here was out of scope for this investigation.
3. **Safety question for the owner:** should `::wrap` / `gt session wrap` be treated as unsafe to invoke in a multi-harness, multi-concurrent-session environment until this is understood and fixed? Should an immediate stopgap safety check (e.g., assert the resolved session_id matches an expected/caller-asserted one before archiving anything) be added even before the full root cause is understood, given the demonstrated blast radius (an unrelated in-flight worker's canonical record can be silently overwritten with no error surfaced)?
4. Does the same mis-targeting risk apply to other consumers of `load_current`/equivalent "resolve the current envelope for harness X" logic beyond wrap specifically? Could an interactive session's own in-session checks be similarly confused by a concurrently-active dispatched worker under the same harness namespace, independent of the wrap-specific incident described here?

## Recommended Next Action

Per the pattern established by this session's first advisory: refer this Advisory Proposal, together with `WI-5328`, to a `/grill-me-for-clarification` session to resolve the open questions above — in particular Open Question 3, which is squarely an owner risk-tolerance call, not something to resolve unilaterally — before any implementation proposal is drafted for either the wrap/close mis-targeting or the three-namespace document divergence.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied
Yes, eventually — this advisory recommends investigating and likely fixing session-identity resolution in `close_session`/`load_current` and reconciling the three-namespace envelope divergence. No implementation proposal exists yet; this advisory is investigation-and-findings only.

### Grill-the-owner questions
Prime Builder must obtain durable AUQ-recorded answers to Open Questions 1-4 above, plus:
5. Should `::wrap` be paused (not invoked by any session) until this is resolved, or is the demonstrated low observed impact sufficient to keep using it with added caution?
6. Should the three-namespace envelope divergence be investigated as part of the same implementation program as `WI-5328`'s fix, or tracked as fully separate follow-on work once `WI-5328` lands?

### Required durable owner decisions
The following AUQ answers must exist before an implementation proposal can be filed:
- Resolution of Open Questions 1-4 and grill-questions 5-6 above.
- Explicit scope boundary for any resulting implementation: does it extend `WI-5328`'s PAUTH, or require its own.

## Filing And Verification Notes

This advisory is filed as the next numbered bridge file (`bridge/gtkb-session-wrap-close-mistargets-session-identity-001.md`) under the append-only, no-deletion, no-rewrite versioned bridge file chain, per `GOV-FILE-BRIDGE-AUTHORITY-001`.

No Specification-Derived Verification applies to this advisory: it makes no `VERIFIED` claim, proposes no `pytest`/`ruff`/`test_*.py` evidence, and performs no spec-to-test mapping, consistent with its Non-Approval Statement below. Verification-grade evidence will be required only for whatever implementation proposal, if any, is derived from this advisory after the recommended grilling session.

## Non-Approval Statement

This advisory is NOT implementation approval. It does not open an implementation-start packet, authorize protected edits, or bypass the bridge, project-authorization, owner-decision, root-boundary, credential-safety, formal-artifact, or verification gates. No corrective action beyond this investigation and report was taken; the mis-targeted worker's envelope was left as found, since further mutation without understanding the resolution mechanism risked compounding the incident.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this advisory remains in the numbered bridge lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the incident and investigation are preserved as durable artifacts.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` — the owner-grilling obligation applied above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all evidence remains under `E:/GT-KB`.
- `GOV-STANDING-BACKLOG-001` — `WI-5328` is the related backlog authority; this advisory is filed as a distinct, cross-referenced artifact rather than folded into it.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the NEW-to-disposition lifecycle this advisory follows once grilled.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — no verification claim is made by this advisory; cited for completeness per the mandatory applicability baseline.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-graph traceability across this advisory, WI-5328, and any eventual implementation.

## Prior Deliberations

- `DELIB-20260635` — "Dispatch/work-envelope design folded into the session-lifecycle envelope program" — the decision that folded dispatch-envelope and interactive session-envelope architecture into one shared mechanism, directly relevant background for why a dispatched worker's session and this interactive session share the same resolution machinery.
- `DELIB-2238`, `DELIB-2500` — the foundational `::init`/`::wrap` session-envelope convention designs.
- `DELIB-20265897` — "WI-4729 ::wrap/::close Mechanical Harvest Model" — prior owner ratification of the wrap/harvest model this incident occurred within.
- `DELIB-20261092`, `DELIB-20261235` — prior NO-GO verifications of the deterministic handoff-prompt service implementation; not read in full for this advisory, flagged as potentially containing prior known issues with the same service and worth checking during the grilling session.
- WI-5328 (this session) — the related, distinct root-cause finding for role-resolution failure on session open.
- Deliberation search performed before drafting (`gt deliberations search "session envelope wrap close mistarget dispatched worker session identity"`) returned no directly duplicating record for this specific incident.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner directed the investigation of the mis-targeted worker's task state before deciding next steps (this session, 2026-07-16).
- Owner confirmed, via direct question and explicit "yes" answer, that this incident is worth capturing as an Advisory Proposal, and directed drafting and filing it now.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
