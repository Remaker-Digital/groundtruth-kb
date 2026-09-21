# Session roles and platform scope

Prime Builder and Loyal Opposition are not permanently bound to a vendor,
model or harness. A role belongs to one session context and is established
only by the exact owner-supplied or dispatched `::init gtkb <pb|lo>` line.
The role is immutable for that context. A harness name, an unavailable
counterpart or a prior assignment cannot confer a role or change it.

Read the current records `GOV-ROLE-DETERMINATION-INIT-LINE-ONLY-001`,
`DCL-SESSION-ROLE-RESOLUTION-001` and `GOV-SESSION-SELF-INITIALIZATION-001`.
Independent review remains with a different context in the reviewing role.
There is no acting-role fallback and no whole-work-item agent ownership.

## Project and application boundaries

Resolve the selected GT-KB project root and apply
`.harness-baseline-configuration/rules/project-root-boundary.md` before
accepting, proposing, implementing, reviewing, testing or verifying work.
Project-relative paths must remain inside that root. Application work requires
the explicitly selected application root and its native application scope.

Agent Red is a well-behaved, fully-conformant adopter supported and sustained
by GroundTruth-KB. It is the reference adopter at `applications/Agent_Red/`,
with its application boundary declared in `.gtkb-app-isolation.json`.
Portability between GT-KB installations exercises the application-isolation
contract. Read `GOV-AGENT-RED-GTKB-CONFORMANCE-001` for current requirements.

Unqualified GT-KB CLI, CI, source, repository, release and verification
references resolve to the platform. Do not silently substitute Agent Red's
repository or CI. Name Agent Red explicitly when it is in scope. The three
adopter fixtures under `groundtruth-kb/examples/` are exercised scaffold
examples, distinct from Agent Red and from platform release evidence.

## Owner direction and native specification authority

Read current formal requirements through `gt spec show`. The owner directs
formal substance; an assigned scope already supported by owner direction does
not need a second per-artifact approval. Ask only about a material unresolved
choice. Draft text does not create a canonical requirement.

Apply directed changes through `gt spec record` with a freshly read version,
actual attribution and a concrete change reason, then compare a separate
canonical readback. `GOV-ARTIFACT-APPROVAL-001`,
`PB-ARTIFACT-APPROVAL-001`, `ADR-ARTIFACT-FORMALIZATION-GATE-001` and
`DCL-ARTIFACT-APPROVAL-HOOK-001` describe the native writer and current authority
contract under `GOV-ARTIFACT-AUTHORITY-HIERARCHY-001`.

The writer validates typed fields and expected versions and records the changed
row and its history atomically. Attribution does not grant permission. Current
requirement status is distinct from implementation verification. Reconcile a
stale write with current facts. Project relationships use their native route
and preserve project authorization. These operations retain independent
review, artifact-scoped claims, executable tests and project commit duties.

## Release, adoption and backlog

`GOV-RELEASE-READINESS-GOVERNED-TESTING-001` and
`GOV-GTKB-ADOPTION-ENFORCEMENT-001` require production-release work to include
governed release-readiness evidence. The evidence must address the named
platform or application. Record defects and missing capabilities through the
standing hygiene intake with current executable-test linkage. An observed
candidate tool or improvement does not reorder the owner's selected work.

`GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`,
`ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` and
`DCL-STANDING-BACKLOG-SCHEMA-001` govern the standing backlog. Read current
work items through `gt backlog list` and the exact native record. Operational
notes under `memory/` carry no canonical authority. Individual backlog entries
remain queue/work items; they do not become formal requirements by appearing
in a queue. Orientation does not select a target: follow the owner's dispatch
until Dispatcher Next is independently qualified and explicitly activated.

## Session startup and wrap-up

Follow `.harness-baseline-configuration/rules/session-bootstrap.md` for exact
immutable context binding, explicit transient activity, current startup
disclosure and proactive read-only wrap-up guidance. Preserve owner input.
A lifecycle notification does not authorize mutations.

Read `GOV-SESSION-SELF-INITIALIZATION-001`,
`PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`,
`DCL-SESSION-STARTUP-TOKEN-BUDGET-001`, `PB-SESSION-WRAP-UP-PROACTIVE-001`
and `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001`. Superseded lifecycle
requirements and historical deliberations confer no current authority.

## Deterministic services and owner questions

`GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` places repetitive deterministic
work in existing services. Surface recurring procedural friction and file a
bounded corrective intake with scope and tradeoffs. Use the native domain
writers; do not invent a second authority, approval-evidence mechanism or
mutable session-progress store. Automation preserves review and effect
boundaries. One-off judgment remains with the assigned agent or owner.

This principle extends `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` keep work organized around artifacts and
their current requirements. Do not turn it into agent ownership of a work item.

Ask the owner when a material product choice remains unresolved. Apply the
answer directly to the applicable canonical source or discard it. The session
conversation is not an execution dependency. Do not copy answers into a
decision ledger, permission packet, bridge authority section or deliberation
record as proof of approval. Never infer an answer from silence.

## Cleanup

Remove temporary, orphaned and session-only files once their active purpose
ends. Keep evidence needed by an active qualification or incident until its
recorded disposition; preserve original failed reports and frozen inputs.
Write enduring knowledge through the appropriate canonical domain writer.
Bridge messages, handoffs and scratch files are not durable authority.
Register authored work product through the existing registry route when
required. Exclude derived projections and bridge material from work-product
commits, and preserve formal history through amendment or retirement.
