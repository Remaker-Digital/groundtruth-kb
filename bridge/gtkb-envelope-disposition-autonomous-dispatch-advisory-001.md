NEW

# Program Advisory — Activity-Envelope Disposition & Autonomous Dispatch (governance_review)

bridge_kind: governance_advisory
Document: gtkb-envelope-disposition-autonomous-dispatch-advisory
Version: 001
Author: Prime Builder (Claude Code, harness B, durable role per registry: [prime-builder])
Date: 2026-06-19 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 61feff31-3776-417a-9639-4029c0e91dd0
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, interactive Prime Builder deliberation session

Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4684
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_program_advisory
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## Claim

This is the program advisory for `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH`
(WI-4682..WI-4694), the owner-designated "epicenter of the GT-KB roadmap." It is
the brief a Prime Builder executes: it frames the activity-envelope disposition
model, the single-active-envelope simplification, headless-safe `::init`, the
re-admitted `ops` activity, platform/application scope isolation, the dispatcher
default-fan-out operating mode, supersession hygiene, and the corrected
automation value/cost principle. It carries no source mutation (`target_paths:
[]`); GO is terminal for this thread, and each work item below is implemented
through its own NEW proposal carrying spec-derived verification.

This advisory does NOT itself authorize implementation. Per-WI implementation
requires: (a) the program's governing ADR/DCL (WI-4684) to exist as the linked
specification, (b) a project authorization citing that spec
(`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`), (c) a bridge GO on the WI's
own proposal, and (d) an implementation-start packet.

## Summary

GT-KB's envelope meta-model (`WI-4302` / `DCL-ENVELOPE-META-MODEL-001`) already
names three legs of every envelope — **invocation + intent_hint + payload** — and
the containment chain **dispatch contains session contains topic**. The runtime
(`groundtruth-kb/src/groundtruth_kb/session/envelope.py`) carries only
`route_target` + `preload_state` on an activity; the **intent_hint leg (what the
activity means for the agent's disposition) is unimplemented.** This program
specifies that missing leg and the operating consequences.

The activity hint is an **interpretation / acquisition / disposition frame, not
(necessarily) an action directive** (owner clarification): it tells the reader
how to interpret the payload, what to acquire, and what disposition to apply; the
agent then acts per role — emit AUQ options interactively, or execute headlessly.

## Disposition Sketch (normative seed for WI-4684; first guess, tune with use)

Each `::open <activity>` injects, at the `intent_hint` leg, a profile with six
levers: preload (acquire), stance, salient tools, decision-criteria, mode
(interactive/headless), route.

| Activity | Stance | Preload (acquire) | Salient tools | Decision-criteria -> act | Mode |
|---|---|---|---|---|---|
| deliberation | interrogative; AUQ-first; alternatives-required; capture-on-close; spec-language alert | DA search hits for the topic | grill-me-for-clarification, decision-capture, spec-intake | detect requirement language -> tee for capture; never auto-implement | interactive-only |
| spec | precision; disambiguate; test-derivability (GOV-04) | current specs, related proposals, templates | kb-spec, spec-intake, kb-adr | is it unambiguous + testable? | headless-eligible |
| build | implement-to-spec; conventional commits; code-quality gates; uniform parseable output | target WI spec + acceptance, pyproject/scaffold | bridge impl-start, ruff, pytest | does impl satisfy linked specs? | headless-eligible |
| test | outside-in (GOV-19); assertion quality (GOV-18); spec-derived | assertion history, failing assertions, inventory | kb-assert, pytest, verify | do tests exercise exposed interfaces + assert meaningfully? | headless-eligible |
| project | decompose; prioritize; dependency-order | authorizations, open WIs, memberships | projects, backlog | rank by dependency/readiness -> ordered plan OR drive-to-VERIFIED | interactive (autonomous variant = fan-out) |
| ops (re-admitted) | situational-awareness -> prioritized action | deployed-app status (health, scale, support cases, user activity, ops feedback) | ops/monitoring surfaces | apply rubric -> emit prioritized AUQ options (patch / scale / approve change / triage / evaluate feedback) | interactive-primary (headless = report-only) |

Mechanism: a `::open` UserPromptSubmit hook injects the profile (stance + preload
+ tool-bias) — hook-primary with agent fallback per
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`. `push` / `upgrade` remain CLI entry points
(`gt commit` / `gt project upgrade`) unless the vocab-reconcile WI re-admits them
as activities like `ops`.

## Program — ordered work items (WI-4682..WI-4694)

1. **WI-4682** Correct the automation value/cost principle + `bridge-essential.md`
   S308 wording. (governance; approval-gated narrative edit)
2. **WI-4683** Reconcile activity-vocabulary drift to one canonical closed set;
   re-admit `ops`. (foundational; gates WI-4687)
3. **WI-4684** Activity disposition-profile model — `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`
   + `DCL-ACTIVITY-DISPOSITION-PROFILE-001` (this advisory's sketch is the seed).
   This ADR is the program's governing specification (unblocks the PAUTH).
4. **WI-4685** Single-active activity-envelope invariant. (refines WI-4295)
5. **WI-4686** `::init` minimization + headless-safe (non-blocking); relocate
   interactive disclosure/options to `::open`. (refines WI-4291/4298)
6. **WI-4687** `ops` activity (depends on WI-4683).
7. **WI-4688** Scope-Transition operational procedure + project template (uses
   WI-4297 drive-to-VERIFIED).
8. **WI-4689** Standing SoT-deference rule (GT-KB-subject sessions defer to
   released Main, then issues/wiki).
9. **WI-4690** Application write-isolation (GT-KB read-only under `::init
   application`) + cross-scope advisory channel (extends WI-4589).
10. **WI-4691** Dispatcher default fan-out mode (reframes WI-4297; depends on the
    DELIB-20261120 substrate fix).
11. **WI-4692** Dispatcher GT-KB-scope suspension under active subject=application
    (drain-then-suspend; extends WI-4296).
12. **WI-4693** Supersession / obsolescence hygiene discipline.
13. **WI-4694** Validation-through-actual-use acceptance gate (release-gating).

Suggested execution order: WI-4682 + WI-4683 first (foundational), then WI-4684
(governing ADR/DCL — unblocks implementation authorization), then WI-4685/4686
(envelope refinements) and WI-4687 (ops); WI-4688..4692 (isolation + dispatch)
and WI-4693 (hygiene) in parallel as dependencies allow; WI-4694 closes the gate.

## Open Items (explicitly deferred by the owner)

- **Fan-out backpressure** (fan out both sides + global cap vs throttle to review
  capacity vs let review queue grow) — OPEN. Owner dismissed; do not assume.
- **Fan-out breadth** (all active authorized projects vs one focus project vs
  owner-pinned candidate list) — OPEN.

## Substrate Precondition

WI-4691 (default fan-out) depends on resolving `DELIB-20261120` (P1): the
dispatcher deadlocks in multi-harness topologies whose active harnesses lack
event-driven hooks. A topology-agnostic dispatch substrate is a prerequisite for
a reliable always-on fan-out default; fanning out more work onto a stranded
review queue worsens contention.

## Supersession Map (audit hygiene)

- WI-4685 (single-active) supersedes WI-4295 per-type concurrency + explicit-hint
  "up to 5 simultaneous".
- WI-4683 / WI-4687 (`ops`) reverse WI-4295's drop of {ops, push, upgrade}.
- WI-4686 (`::init` minimization) supersedes-in-part DELIB-20260636 #5 / WI-4298.
- WI-4691 (fan-out default) reframes WI-4297 (opt-in -> default-on).
- WI-4682 (corrected principle) supersedes `bridge-essential.md` S308 wording.

## Specification Links

Cross-cutting (blocking):

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (each program WI carries spec-derived verification in its own proposal; see the Verification Plan)
- `GOV-ARTIFACT-APPROVAL-001` (governs the downstream ADR/DCL + narrative writes)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (scope isolation)
- `GOV-STANDING-BACKLOG-001` (WI-4682..4694 are ranked backlog work)
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` (envelope open/close lifecycle)
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` (per-WI impl authorization gate)

Domain (extended/refined by this program):

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (hook-injection mechanism + fallback)
- Envelope program WI-4291..WI-4302 (init keyword, wrap, durability, router,
  dispatch element, project-completion drive, disclosure UI, glossary,
  implementation umbrella, meta-model ADR/DCL) and WI-4482 (explicit-hint layer)
- Agent-disposition program WI-4588..WI-4593 (protected-mutation guard,
  external-mutation gate, post-action receipts, bridge-disposition workflow,
  cross-harness parity, enforcement visibility)

Cross-cutting (advisory):

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (durable-artifact-driven work selection)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (supersession lifecycle states)
- `GOV-STANDING-BACKLOG-001`

New formal artifacts created downstream (owner-gated, WI-4684 + WI-4682):

- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` (architecture_decision)
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` (design_constraint)
- A governance record for the corrected value/cost principle

## Prior Deliberations

- `DELIB-20265287` (2026-06-19) — the anchor: the full AUQ-backed decision set
  (D1-D11, F1/F2, corrected value/cost principle, supersession-hygiene principle,
  deferred items, supersession map) this advisory consolidates.
- `DELIB-20260636` (2026-06-04, WI-3468 grilling) — the envelope program's six
  settled branches; this program refines #5 (minimal open) and re-opens the
  WI-4295 vocab drop.
- `DELIB-20260637` — envelope meta-model (3-part anatomy + containment); the
  `intent_hint` leg this program implements.
- `DELIB-20260612` — explicit-hint layer decision set (topic->activity rename;
  init-keyword v3; hook-primary interception).
- `DELIB-20260638` — standing v1.0 content goal includes the full envelope
  program incl. rule-driven dispatcher (release-gating alignment).
- `DELIB-20263438` — corrected bridge-dispatch architecture (role<->dispatchability
  orthogonal; rule-based dispatch over roles/subjects/activities; cost/quality
  selection) — basis for WI-4691.
- `DELIB-20261120` (P1) — dispatch deadlock & contention critique (substrate
  precondition for WI-4691).
- `DELIB-2238` / `DELIB-2500` — envelope-convention foundation.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20260635` — seed=search; owner_conversation; Dispatch/work-envelope design folded into the session-lifecycle envelope program
- DA: `DELIB-20262117` — seed=search; bridge_thread; Bridge thread: gtkb-dispatch-envelope-adr-specs (1 versions, ORPHAN)
- DA: `DELIB-20261806` — seed=search; bridge_thread; Bridge thread: gtkb-dispatch-envelope-adr-specs (2 versions, GO)
- DA: `DELIB-20265056` — seed=search; bridge_thread; Loyal Opposition Verification Verdict - Worker Packet Authorization Envelope Sli
- DA: `DELIB-20264022` — seed=search; bridge_thread; Bridge Dispatch Orthogonality, Configuration, and Status CLI Implementation Prop

## Owner Decisions / Input

This advisory is authorized by a fresh, durable owner-decision record — not a
precedent PAUTH:

- `DELIB-20265287` (source_type=owner_conversation, outcome=owner_decision,
  session 61feff31) captures the deliberation decision set collected across three
  AskUserQuestion rounds plus owner prose directives (the only valid
  owner-decision channel per the AUQ-only enforcement stack).
- Owner directive (2026-06-19): "bring all of this together in a fresh project
  (or umbrella project) ... capture it as release-gating work ... create the
  advisory proposal, add/remove/update ADRs or other specs, and any other
  artifacts required to move forward."
- Owner directive (2026-06-19): "Please proceed. I have a Prime Builder ready to
  take action on your advisory report."

Two open items remain owner-deferred (do not assume): fan-out backpressure and
fan-out breadth. Downstream owner-input dependencies: a formal-artifact-approval
packet each for `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`,
`DCL-ACTIVITY-DISPOSITION-PROFILE-001`, and the value/cost governance record; a
narrative-artifact-approval packet for the `bridge-essential.md` S308 correction.

## Requirement Sufficiency

Existing requirements sufficient for THIS advisory. The program decisions derive
from `DELIB-20265287` (owner AUQ) plus the GO-terminal / specified envelope +
agent-disposition + isolation artifacts. No new owner requirement is needed
before the per-WI proposals; the governing ADR/DCL (WI-4684) and the per-WI
implementations are owner-gated at their own approval packets and bridge GOs.

## Specification-Derived Verification Plan

This is a governance_review program advisory with `target_paths: []` and
`requires_verification: false`; GO is terminal for this thread (the
governance-review-terminal pattern). No follow-on post-impl report is required
for THIS thread. Each work item (WI-4682..WI-4694) carries its own spec-derived
verification in its own NEW proposal; WI-4684's ADR/DCL become the linked
specifications those per-WI verifications map to.

## Risk / Rollback

This advisory writes one bridge file. Rollback = `git restore` + `rm` + bridge
state revert. Blast radius is the advisory file itself; no source, no MemBase
mutation, no formal-artifact insert. The program's risk surface (envelope runtime
changes, dispatcher fan-out, scope isolation) is carried by each WI's own
proposal and bounded by the per-WI bridge GO + implementation-start packet, the
deferred backpressure/breadth decisions, and the DELIB-20261120 substrate
precondition.

## Bridge Filing

Filed as the first status-bearing numbered bridge file (`-001`) for this thread
through the governed no-index writer. Per `GOV-FILE-BRIDGE-AUTHORITY-001`, the
numbered bridge file chain plus dispatcher/TAFE state are the canonical bridge
workflow state; no aggregate INDEX or queue artifact is created or required, and
append-only versioning applies (no prior version is rewritten or deleted; the
pre-review compliance edits to this `-001` precede any verdict).

## Recommended Commit Type

`docs` — a governance program advisory; no source / test / config code is
modified by this thread.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
