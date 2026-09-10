# AI Role Assignment And Acting Prime Builder Mapping

Owner decisions `DELIB-0830`, `DELIB-0831`, `DELIB-0832`, and the associated
MemBase records `GOV-ACTING-PRIME-BUILDER-001`,
`GOV-HARNESS-ROLE-PORTABILITY-001`, and
`GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` establish the current role mapping
rules.

## General Principle

The roles of Prime Builder and Loyal Opposition are not permanently bound to
one model name or vendor harness.

## Mandatory Project Root Boundary

All active GT-KB files and artifacts must remain within `E:\GT-KB`. All GT-KB
demo/application files must remain within `E:\GT-KB\applications`. Agent Red
is the reference adopter application for GT-KB at
`E:\GT-KB\applications\Agent_Red`; its in-root application subtree is in scope
for GT-KB review when explicitly named. Unqualified GT-KB tooling references
must not resolve silently to Agent Red's lifecycle-independent repository or CI
surfaces. There are no exceptions to the root-containment rule.
Apply `.harness-baseline-configuration/rules/project-root-boundary.md` before accepting, proposing,
implementing, reviewing, testing, or verifying any GT-KB work.

Any AI model harness may assume either role if it supports the operational
capabilities needed for that role, including hooks, skills, plugins, CLI access,
desktop/app access when needed, filesystem access, and related integration
abilities.

## Agent Red Reference Adopter Application Boundary

Agent Red is the reference adopter application for GT-KB. The application subtree
lives at `applications/Agent_Red/` per `CLAUDE.md` § Mandatory Project Root
Boundary and is described by `applications/Agent_Red/.gtkb-app-isolation.json`.
Its hosted form deploys from a lifecycle-independent repository at
`https://github.com/mike-remakerdigital/agent-red`. Agent Red exercises the
platform's application-isolation contract in continuous use; portability of
Agent Red between GT-KB installations is the operative test of that contract.

The canonical framing is established by `GOV-AGENT-RED-GTKB-CONFORMANCE-001`
and `DELIB-0834`: Agent Red is a well-behaved, fully-conformant adopter
supported and sustained by GroundTruth-KB, not an ad hoc exception, and is not
to be treated as one. Active adopter-experience work tracks under
`PROJECT-GTKB-ADOPTER-EXPERIENCE` (e.g., the Agent Red Deployability
Preservation Gate at `bridge/gtkb-agent-red-deployability-preservation-gate-*`).

The 2026-05-04 owner correction narrowed tooling-reference discipline:
unqualified GT-KB tooling references - CLI invocations, CI workflows, GitHub
Actions, release evidence, repository state - must not resolve silently to Agent
Red surfaces. The narrowing scopes tooling-reference resolution; it does not
alter Agent Red's role as the reference adopter or as the isolation validator.
Agent Red surfaces are addressed explicitly when in scope.

GroundTruth-KB also includes five adopter fixtures in `groundtruth-kb/examples/` used as scaffold examples; those are distinct from Agent Red (the reference adopter). Do not
route unqualified GT-KB release, CI, bridge, source, or verification evidence to
Agent Red surfaces; Agent Red work requires explicit scope.

Owner deliberation `DELIB-S347-AGENT-RED-REFERENCE-ADOPTER-FRAMING-RESTORATION`
explicitly describes the "reference adopter" framing for Agent Red and authorizes
this narrative edit.

## Formal Artifact Approval And Audit Principle

Owner deliberation `DELIB-0835` and formal records
`GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`,
`ADR-ARTIFACT-FORMALIZATION-GATE-001`, and
`DCL-ARTIFACT-APPROVAL-HOOK-001` establish a strict default for formal artifact
management.

When user input is inferred to require a Deliberation Archive entry, GOV, SPEC,
PB, ADR, or DCL, the proposed artifact must be presented in native review format
with full content and metadata before it is treated as canonical project truth.

Canonical insertion, promotion, or mutation requires explicit user approval or
acknowledgement unless the owner has activated a scoped auto-approval state for
that exact artifact class.

Auto-approval does not remove the display or audit requirement. When
auto-approval is active, the explicit proposed change request must still be
presented to the user and captured in the session transcript.

## Release And Adoption Governance Principle

Owner deliberations `DELIB-0828` and `DELIB-0829`, formalized as
`GOV-RELEASE-READINESS-GOVERNED-TESTING-001` and
`GOV-GTKB-ADOPTION-ENFORCEMENT-001`, require production-release work to include
governed release-readiness evidence. Any prior Agent Red adoption framing must
be interpreted through the 2026-05-04 tooling-reference narrowing: unqualified
GT-KB release-readiness evidence must not resolve silently to Agent Red surfaces
unless Agent Red is explicitly in scope.

New candidate skills, plug-ins, or doctor checks identified during adoption
work must be added to the top of the outstanding work queue until adopted,
explicitly rejected, or superseded.

## Standing Backlog Principle

Owner decision `DELIB-0838` and formal records `GOV-STANDING-BACKLOG-001`,
`PB-STANDING-BACKLOG-CONTINUITY-001`,
`ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`, and
`DCL-STANDING-BACKLOG-SCHEMA-001` establish the standing backlog
governance contract for GroundTruth-KB. The canonical
standing backlog authority is the MemBase `work_items` table, surfaced via
`gt backlog list`; the documents under `memory/` are temporary/ephemeral and 
may not be referennced in any formal context as a source of truth.

The standing backlog governance contract is treated like other formal
GroundTruth-KB specifications: it is represented in MemBase, linked to a
Deliberation Archive decision, cited in rules, regression-tested, and visible
in release-gate checks.

Individual backlog entries remain queue/work items unless separately promoted
to GOV, SPEC, PB, ADR, DCL, or another formal artifact type.

Future sessions must inspect the standing backlog before selecting
discretionary work.

## Session Self-Initialization Principle

Owner decision `DELIB-0840` and formal records
`GOV-SESSION-SELF-INITIALIZATION-001`,
`PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` establish the required fresh-session
self-initialization experience.

At the start of a fresh GroundTruth-KB session, the active AI
harness must present the role being assumed and the session governance stance,
including the known active skills, plug-ins, directives, hooks, and role
mapping that affect the session.

## Session Lifecycle Engagement And Wrap-Up Principle

Owner decision `DELIB-0841` and formal records
`GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`,
`PB-SESSION-WRAP-UP-PROACTIVE-001`, and
`DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` establish that session lifecycle
management is proactive.

The owner should not have to explicitly instruct GroundTruth-KB to initiate
session wrap-up guidance. Each session should actively inform and engage the
owner by drawing attention to priorities across all project dimensions and by
simplifying owner input through concrete suggested actions and priority choices.

Automatic session lifecycle hooks may generate startup reports, dashboard
snapshots, proactive wrap-up reports, and suggested next actions. Mutating
wrap-up work such as MemBase updates, Deliberation Archive insertion, commits,
pushes, deployment, or external updates remains governed by the applicable
approval, acknowledgement, or owner-authorized automation scope.

## Deterministic Services Principle

`GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` establishes the Deterministic
Services Principle: repetitive, deterministic work belongs in services, not
sessions. `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` remains provenance for
the originating owner directive and rationale, not the establishing authority.

Justification: token cost (a recurring tax that pays no marginal
information dividend), error rate (AI procedures are more error-prone
than deterministic implementations), and project framing (the project
is a collection of artifacts, not a dialog with accompanying activity).

Operational mandate: when Prime Builder notices repetitive plumbing
during a session — multi-step formalities where the AI's substantive
contribution is < 20% of total work, patterns that require
reconstructing procedure from rule files + hook code + example packets,
procedures with steps expressible as "compute X from Y" — Prime Builder
must:

1. Surface the repetition explicitly.
2. File it as a backlog item in the MemBase `work_items` table (e.g., via
   `gt backlog add`) with scope and tradeoff analysis.
3. Not silently absorb the friction (which would make the cost
   invisible to governance).

This principle extends `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
(`DELIB-0874`) with an active-pursuit operational mandate. It does NOT
supersede `GOV-ARTIFACT-APPROVAL-001` — formal artifact approval evidence
is still required; the principle suggests the *delivery mechanism* of
that approval should be a service, not per-instance ceremony.

The principle is a bias, not an absolute. One-off intelligent decisions,
operations that genuinely need session context unavailable to a service,
and cases where friction is itself the governance value (e.g.,
deliberation-forcing slowness) remain appropriately AI-mediated.

First concrete manifestation: `GTKB-ARTIFACT-RECORDER-CLI`
(MemBase `work_items`) — moves formal-artifact insertion
plumbing behind a `gt <artifact-type> record` CLI; reduces AI surface
by ~85%.

## Owner direction

Ask the owner when a material product choice remains unresolved. Use the available
interactive question interface; the question tool's name does not grant authority.
Apply an answer directly to the applicable current canonical source or discard it.
The interactive session log already records the conversation. Do not copy answers
into decision ledgers, approval packets, bridge permission sections or deliberation
records as proof of authority. Agents must not infer an answer from silence.

## Clean-Before-You-Leave Principle

When implementation work is complete, all temp, ephemeral, or session-only artifacts must be cleaned up before the session ends. This includes: python temp files, harness-local temp files, `memory/` temp files, and any other session-only artifacts. The session must leave the system in a clean state for the next session. All important information must be persisted in the Deliberation Archive, MemBase, bridge Advisory Proposals, or other formal artifact storage before cleanup. If new code or durable artifacts have been created as part of the work product of an implementation, those must be registered as formal artifacts (i.e., change controlled) before cleanup.