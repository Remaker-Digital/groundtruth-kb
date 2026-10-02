# Governance Principles — Active Cross-Harness Operating Rules

This rule carries the active operating principles that every harness inherits
from the neutral baseline. It was split from a legacy role-compatibility rule
whose provenance content now lives in MemBase governance records (Phase A of
the baseline-neutralization program, per the anti-destruction verification
lens: active principles must keep an always-loaded baseline home).

## Deterministic Services Principle

`GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` establishes that repetitive,
deterministic work belongs in services, not sessions.

Justification: token cost (a recurring tax that pays no marginal information
dividend), error rate (AI procedures are more error-prone than deterministic
implementations), and project framing (the project is a collection of
artifacts, not a dialog with accompanying activity).

Operational mandate: when the implementing role notices repetitive plumbing
during a session — multi-step formalities where the AI's substantive
contribution is under ~20% of total work, patterns that require reconstructing
procedure from rule files plus hook code plus example packets, procedures with
steps expressible as "compute X from Y" — it must:

1. Surface the repetition explicitly.
2. File it at discovery through `gtkb-work-item` as a work item in
   `PROJECT-GTKB-NEW-WORK-INTAKE`, with its specification and an executable test
   in an active plan phase. Include the scope and tradeoff analysis. If it is
   not yet a reproducible defect, file an ADVISORY instead.
3. Not silently absorb the friction (which would make the cost invisible to
   governance).

This principle extends `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` with an
active-pursuit operational mandate. Existing owner direction takes effect through
current canonical domain state. Deterministic plumbing does not invent owner
choices or introduce an approval-evidence service.

The principle is a bias, not an absolute. One-off intelligent decisions,
operations that genuinely need session context unavailable to a service, and
cases where friction is itself the governance value remain appropriately
AI-mediated.

## Every Tool Use Is a Test Principle

Every invocation of a tool, skill, helper, or CLI is a test of an unproven
implementation. What is under test is not only whether the invocation returns:
it is the behavior, the output, the documentation, and the fitness of that tool
for the purpose it was reached for.

1. Inspect the output of every invocation and evaluate its utility. Never
   assume correctness, completeness, or optimality — including when the
   invocation appears to have succeeded.
2. A defect, gap, mislabel, incorrect description, or overlooked case is
   captured AT THE POINT OF DISCOVERY: a work item filed through
   `gtkb-work-item` in `PROJECT-GTKB-NEW-WORK-INTAKE`, or an ADVISORY if it is
   not yet a reproducible defect. It is not batched to session end, and it is
   not silently absorbed.
3. Capture at the point of discovery is not implementation approval. The
   captured item follows normal owner prioritization and the bridge protocol
   before any repair is implemented.
4. When a defect blocks the current task, file the corrective work item or
   ADVISORY before any workaround. Then use a lawful workaround if one exists,
   and disclose it.

Silent absorption is the failure mode this principle exists to prevent. A
defect that is worked around but never recorded leaves the next session to
rediscover it at full cost, and keeps that cost invisible to governance.

This principle extends `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`. Captured work
enters the standing backlog that `GOV-STANDING-BACKLOG-001` governs, in
`PROJECT-GTKB-NEW-WORK-INTAKE`.
Capture is not a grant to implement: current project ordering, owner-directed
scope, independent review, executable tests and artifact claims still apply.
Do not introduce an approval packet or per-mutation permission ledger.


## Simplicity Principle

Read the specification literally. Implement the nouns and verbs it contains. A marker is not a record; a trigger is not an object.

Justification: complexity drift follows a structural cost asymmetry: wherever a removal costs more process than an addition, elaboration accumulates unless a named, always-loaded principle makes excess citable in review.

Operational mandate: when two designs satisfy the specification, the one with fewer artifacts, fewer state locations, and fewer concepts wins by default. The more elaborate design must justify its excess against the specification text. The burden of proof falls on the addition, never on the removal. When an agent notices that an implementation exceeds its specification, it must:

1. Surface the excess explicitly.
2. File it at discovery through `gtkb-work-item` as a work item in
   `PROJECT-GTKB-NEW-WORK-INTAKE`, with its specification and an executable test
   in an active plan phase. Name the excess against the specification text. If
   it is not yet a reproducible defect, file an ADVISORY instead.
3. Not silently absorb the elaboration (which would make the cost invisible
   to governance).

This principle extends `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. Captured work enters the standing backlog that `GOV-STANDING-BACKLOG-001` governs, in `PROJECT-GTKB-NEW-WORK-INTAKE`. The principle does not authorize deleting protected behavior or settling a material owner choice. Apply existing direction through the current canonical writer and preserve independent verification; an approval-evidence artifact is not required.

## Event-Oriented Naming Principle

Name hook-triggered and event-shaped concepts for when they fire, not for what
they are. `init-trigger`, `on-init`, and `open-hook` are event names. A name that
answers "what kind of thing is it?" invites a record; a name that answers "when
does it fire?" does not.

Justification: naming choices drive structure. A noun implies a thing, a thing
implies a record, a record implies a store, a lifecycle, and eventually an
archive. The canonical glossary already defines `::init` and `::open` as markers
caught by a hook; the vocabulary that grew around them did not contradict those
definitions, it exploited the noun. An entity noun therefore attracts persistence
machinery the specification never asked for, and each increment is individually
defensible.

Operational mandate: when naming a concept that is triggered by a hook or fires
on an event, prefer a verb or event form. When an agent encounters an entity noun
standing for a triggered concept, it must:

1. Surface the naming mismatch explicitly.
2. File it at discovery through `gtkb-work-item` as a work item in
   `PROJECT-GTKB-NEW-WORK-INTAKE`, with its specification and an executable test
   in an active plan phase. Name the triggered concept and the persistence
   machinery the noun has attracted. If it is not yet a reproducible defect,
   file an ADVISORY instead.
3. Not silently extend the noun with further fields, records, or lifecycle
   state.

This principle extends the Simplicity Principle above and
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`. Capture concrete naming or persistence
defects through the current backlog writer, using current formal requirements
and independent review. Existing owner direction does not require a separate
approval-evidence artifact. Naming is a judgment about the actual behavior;
a structural assertion cannot establish complete behavioral conformance.

## Clean-Before-You-Leave Principle

After the authorized work and knowledge harvest, remove this context's temporary
output through the supported cleanup route. Preserve unrelated files, required
qualification evidence and current formal history. Put retained knowledge in
its established canonical source through the native writer and read it back;
a deliberation archive, bridge payload or session-memory file is not a durable
authority or a substitute for that source. Use the native scratch-teardown
operation described in `session-bootstrap.md`; it preserves the context binding.

## Session startup and wrap-up

Follow the canonical baseline `rules/session-bootstrap.md` for exact immutable
context binding, explicit transient activity, current startup disclosure and
proactive read-only wrap-up guidance. Preserve owner input. A harness has no
role mapping, and a lifecycle notification does not authorize mutations.

Current formal requirements are `GOV-SESSION-SELF-INITIALIZATION-001`,
`PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`,
`DCL-SESSION-STARTUP-TOKEN-BUDGET-001`, `PB-SESSION-WRAP-UP-PROACTIVE-001`,
and `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001`. Read their current records;
superseded lifecycle requirements and historical deliberations are not authority.

## Release And Adoption Work-Queue Principle

Per `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` and
`GOV-GTKB-ADOPTION-ENFORCEMENT-001`, new candidate skills, plug-ins, or doctor
checks identified during adoption work are adoption candidates. File adoption
candidates in the intake, `PROJECT-GTKB-NEW-WORK-INTAKE`. The owner orders work;
agents never reorder it.

## Retained working priorities

Technical work has elevated priority over creative/content work.
Implementation, executable tests, result analysis and working capabilities take
priority over marketing and cosmetic changes within the owner's selected work.

Removing obsolete material at its source is ordinary governed work: a work item,
independent review and verification.
Owner approval gates new artifacts, tables, gates and workflow steps. Temporary
output follows the current authorized cleanup scope and retention requirements.

Formal retrieval: SPEC-0282, SPEC-0735, SPEC-0472, SPEC-0744, SPEC-0850.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
