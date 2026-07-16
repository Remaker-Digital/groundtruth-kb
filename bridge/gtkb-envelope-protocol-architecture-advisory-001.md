ADVISORY
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 8256b1c3-d3ed-4e04-bbbb-707ab38a742a
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; session-stated role prime-builder via ::init gtkb pb; deliberation activity envelope; owner-directed advisory

# GT-KB Advisory Proposal - Envelope Protocol Architecture Refinement Program

bridge_kind: governance_advisory
Document: gtkb-envelope-protocol-architecture-advisory
Version: 001
Author: Prime Builder (Claude B), owner-directed
Date: 2026-07-16

## Source

Owner-directed deliberation session, 2026-07-16, interactive deliberation
activity envelope, harness B, session 8256b1c3-d3ed-4e04-bbbb-707ab38a742a.
The owner stated an envelope-architecture intent, requested a pros/cons
evaluation, and completed a grill-me-for-clarification interview. Seven
AskUserQuestion-recorded owner decisions were persisted:

- DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS
- DELIB-20260716-ENVELOPE-GRILL-B2-LINE-AUTHORING-AUTHORITY
- DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST
- DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION
- DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE
- DELIB-20260716-ENVELOPE-GRILL-B8-SCOPE-STAGED-HARD-BLOCK
- DELIB-20260716-ENVELOPE-GRILL-B9-MODERNIZATION-CHILD

This ADVISORY is Prime-actionable in interactive sessions only and is
non-dispatchable for headless runs.

## Claim

GT-KB's envelope handling and role determination should be refined so that
the bridge artifact itself manifests the worker session-context, per the
owner-ratified architecture below. This extends (and stays consistent with)
DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE.

| # | Decision | DA record |
| --- | --- | --- |
| B1 | Artifact-head `::init` names the RESPONDER worker role (NEW/REVISED/NO-ACTION carry lo; GO/NO-GO carry pb); binds headless workers; interactive owner direction supersedes | DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS |
| B2 | `::init` always writer-derived from status (never hand-set); `::open` author-declared from the closed activity vocabulary with a bridge_kind-derived default; both write-time validated | DELIB-20260716-ENVELOPE-GRILL-B2-LINE-AUTHORING-AUTHORITY |
| B3 | Status token stays line 1; envelope lines at fixed lines 2-3; historical files grandfathered by absence (legacy routing fallback); Body Status-Token Rule unchanged | DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST |
| B4 | `::open` always materialized (derived from B2+B3; recorded inside the B3 record) | see B3 record |
| B5 | Envelope packets are hook-fetched and injected at worker session start; role bootstrap loads before activity specialization; packet CLI manually runnable | DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION |
| B6 | Packets are a stable frame for the whole worker session; TTL (default 5 min, tunable) bounds fetch-cache reuse; explicit freshness carve-out: packets cover bootstrap knowledge, live state claims still require fresh canonical reads | DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE |
| B7 | Dispatcher contract (derived, no new decision needed): read-only over artifact content; envelope lines are selection input for harness/model/config; routing policy stays internal and excluded from worker context | DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE |
| B8 | Subject-scope enforcement staged: build subject->scope map (path prefixes + CLI verb classes + shared-surfaces tier), audit/warn first, hard-block headless workers after a clean owner-set observation window; interactive stays advisory | DELIB-20260716-ENVELOPE-GRILL-B8-SCOPE-STAGED-HARD-BLOCK |
| B9 | Program home: one new child under PROJECT-GTKB-PLATFORM-MODERNIZATION (working name PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL), reconciled with in-flight WIs 5310/5314/5328/5335 | DELIB-20260716-ENVELOPE-GRILL-B9-MODERNIZATION-CHILD |

## Owner Decision Needed

None to act on this advisory itself: the B1-B9 records above are the owner
ratification. The following DEFERRED decisions must be obtained by Prime
Builder via AskUserQuestion during the owner-grilling gate BEFORE the
corresponding implementation proposals are filed:

1. Packet composition specifics and token-budget ceilings per bundle
   (requires a measured baseline of current startup surfaces first; policy:
   hard cap vs advisory target, and the numbers).
2. Subject->scope map contents: exact allow/deny path prefixes, CLI verb
   classes, shared-surfaces tier membership (bridge/, groundtruth.db,
   .gtkb-state/, others), and the FP observation window length/criteria for
   the audit->hard-block flip.
3. Harness-parity fallback for weak-hook harnesses (Cursor, Antigravity,
   OpenRouter, Ollama): disclosed-fallback operation vs dispatch
   ineligibility until parity.
4. Migration sequencing: when (if ever) the legacy status-only routing
   fallback retires; treatment of in-flight threads spanning the cutover.
5. Packet CLI naming/surface and cache location (.gtkb-state/ placement).
6. Dispatcher pointer-prompt scope: what minimal prompt the dispatcher still
   composes once the artifact head carries the binding.

## Recommended Prime Action

Adopt. Prime Builder, in an interactive session with the owner, should:

1. Create the modernization child project record (per B9) through the
   governed project lifecycle path, linked to the B1-B9 DA records and to the
   Runtime Interfaces / Context Manifests charters it extends.
2. Execute the Required Prime Builder Owner-Grilling Gate below
   (grill-me-for-clarification or equivalent AUQ-recorded interview) to
   resolve the six deferred decisions.
3. Produce a program plan: enumerated work items with explicit order-of-work,
   spec-derived testing expectations per slice, post-implementation cleanup of
   stray or temporary artifacts (draft bodies, staging files, superseded
   markers, retired hook surfaces), and SoT updates (new/amended ADR/DCL/SPEC
   set, rule files, canonical-terminology glossary entries,
   SESSION-STARTUP-INDEX and role overlays, system-interface-map inventory).
4. File child implementation proposals through the normal bridge protocol
   (NEW -> LO review -> GO -> implementation-start packet -> report ->
   VERIFIED), one bounded slice per proposal.

Suggested work breakdown (advisory, non-binding):

- Slice A (authority): formal artifact set - envelope-line grammar
  specification (extends SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 to
  artifact-embedded lines at fixed positions), packet-contract DCL (bundle
  composition, ordering, TTL fetch-cache semantics, freshness carve-out
  amendment to GOV-SOURCE-OF-TRUTH-FRESHNESS-001), scope-map DCL, dispatcher
  read-only-input clause. All via formal-artifact approval packets. May
  proceed on the existing B1-B9 records alone.
- Slice B (writer): governed bridge writer derives/validates/materializes the
  envelope head (lines 2-3) on new dispatchable artifacts; bridge-compliance
  gate validation additions; grandfathering-by-absence reader fallback.
- Slice C (packet service): `gt` packet CLI building the session-envelope and
  activity-envelope bundles from existing surfaces (SESSION-STARTUP-INDEX,
  role overlays, activity-disposition-profiles, sharding config); fetch cache
  with TTL; measured token baseline per bundle.
- Slice D (hook injection): envelope interception hook fetches and injects
  packets at worker session start; role bootstrap before activity packet;
  cross-harness parity disposition for weak-hook harnesses.
- Slice E (dispatcher): consume envelope lines as selection input; read-only
  artifact access; retire prompt-composition of the init keyword in favor of a
  minimal pointer prompt (scope per deferred decision 6).
- Slice F (scope enforcement): subject->scope map; audit/warn deployment;
  FP burn-down; owner-gated flip to hard-block for headless workers.
- Slice G (cleanup + docs): retire superseded loading paths, remove temporary
  staging artifacts, update rules/glossary/runbooks, harness-parity re-check,
  regression suite over the whole protocol.

## Classification Slot

adopt

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes - this advisory recommends adopt of an owner-ratified architecture that
requires new specs/DCLs, governed-writer changes, a new packet CLI service,
hook changes, dispatcher changes, and staged enforcement gates across
multiple harnesses.

### Grill-the-owner questions

The six deferred decisions enumerated under Owner Decision Needed.

### Required durable owner decisions

Each of the six questions must land as an AskUserQuestion-recorded
Deliberation Archive record before the corresponding slice's implementation
proposal is filed. Slice A may proceed on the existing B1-B9 records alone.

## Owner Decisions / Input

Owner direction and ratification recorded 2026-07-16 (interactive
deliberation envelope, harness B):

- Owner transcript directive: evaluate the envelope-architecture intent, run
  the grilling session, and prepare this Advisory Proposal instructing Prime
  Builder to create the umbrella program and plan execution.
- AUQ "::init means" -> Responder role: DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS
- AUQ "Line author" -> Role derived, activity declared: DELIB-20260716-ENVELOPE-GRILL-B2-LINE-AUTHORING-AUTHORITY
- AUQ "Placement" -> Status first, envelope 2-3: DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST
- AUQ "Packet load" -> Hook-fetched + injected: DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION
- AUQ "TTL meaning" -> Stable frame + fetch cache: DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE
- AUQ "Scope bars" -> Staged to hard-block: DELIB-20260716-ENVELOPE-GRILL-B8-SCOPE-STAGED-HARD-BLOCK
- AUQ "Program home" -> New modernization child: DELIB-20260716-ENVELOPE-GRILL-B9-MODERNIZATION-CHILD

These records authorize advisory capture and program planning only.

## Prior Deliberations

- DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS - responder semantics of the artifact-head init line.
- DELIB-20260716-ENVELOPE-GRILL-B2-LINE-AUTHORING-AUTHORITY - writer-derived role line, author-declared activity line.
- DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST - status-first placement; B4 derivation recorded inside.
- DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION - hook-fetched packet injection.
- DELIB-20260716-ENVELOPE-GRILL-B6-TTL-STABLE-FRAME-FETCH-CACHE - stable-frame TTL semantics and freshness carve-out.
- DELIB-20260716-ENVELOPE-GRILL-B8-SCOPE-STAGED-HARD-BLOCK - staged subject-scope enforcement.
- DELIB-20260716-ENVELOPE-GRILL-B9-MODERNIZATION-CHILD - program placement under the modernization parent.
- DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE - prior owner decision: worker role comes from the explicit session envelope carried by the dispatched bridge item; dispatcher rules excluded from worker context; fail closed on ambiguity.
- DELIB-20260710-GTKB-PLATFORM-MODERNIZATION-PARENT-CHARTER - modernization program parent this child extends.
- DELIB-20260710-GTKB-MODERNIZATION-CONTEXT-MANIFESTS-CHARTER - context-manifest charter the packet service must reconcile with.
- DELIB-20265892 - owner ratification of the six seed activity disposition profiles.
- DELIB-20260648 - init-keyword optionality: subject mandatory, role optional.
- DELIB-20265225 - transcript-defined interactive role persists for the session.
- DELIB-20266631 - WI-4949 activity-envelope context sharding GO.

## In-Flight Reconciliation

The program plan must reconcile with, not duplicate:

- WI-5328 (session-envelope role writeback; implementation report at
  bridge/gtkb-wi5328-session-envelope-role-writeback-005.md pending LO
  verification) - the envelope writeback machinery this program extends.
- WI-5310 (Codex effective workspace profile; REVISED in review).
- WI-5314 (nonspawn session-envelope suppression; adjacent, not adopted).
- WI-5335 (loading-graph repeatability timeout; NEW in review) plus its
  WI-5347 baseline dependency - loading-graph evidence surfaces that packet
  work will touch.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - durable vs session-stated role authority split the responder line must respect.
- `DCL-SESSION-ROLE-RESOLUTION-001` - deterministic role resolution the packet bootstrap composes with.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` / `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` / `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - interactive supersession the B1 decision preserves.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - init-keyword grammar this program extends to artifact-embedded lines.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` / `DCL-TOPIC-ENVELOPE-ROUTING-001` - activity open/close grammar and closed vocabulary.
- `ADR-ENVELOPE-META-MODEL-001` / `DCL-SESSION-ENVELOPE-DURABILITY-001` - envelope anatomy and durability contract.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` / `DCL-ACTIVITY-DISPOSITION-PROFILE-001` / `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` - disposition-profile and interception surfaces the activity packet builds on.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - freshness principle requiring the explicit TTL carve-out (B6).
- `GOV-SESSION-SELF-INITIALIZATION-001` / `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - startup disclosure and token-budget surfaces the session packet consolidates.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - deterministic-service delivery of packet generation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail discipline; envelope head is additive to the versioned file chain.
- `GOV-STANDING-BACKLOG-001` - single work authority; B9 placement honors it.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - non-impairment constraint on all slices.
- `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - parity obligations for hook injection and scope gates.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` / `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` - the owner-grilling gate this advisory carries.
- `GOV-ARTIFACT-APPROVAL-001` - formal-artifact approval packets required for the Slice A spec set.
- Body Status-Token Rule (GTKB-GOV-PROPOSAL-STANDARDS Slice 1) - preserved unchanged per B3.

## Non-Approval Statement

This ADVISORY preserves owner-ratified architecture direction and instructs
program planning. It is NOT implementation approval. No source, test, hook,
configuration, dispatcher, or KB mutation is authorized by this entry. All
implementation requires: the B9 child project record and its project
authorization, per-slice NEW implementation proposals with complete
Specification Links, Loyal Opposition GO, implementation-start packets scoped
to approved target_paths, spec-derived tests, post-implementation reports,
and independent VERIFIED verdicts. Advisory capture does not bypass the
owner-grilling gate above.
