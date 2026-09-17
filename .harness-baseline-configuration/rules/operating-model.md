# GT-KB operating model

This guide translates current formal requirements into agent practice. Read the
current records through `gt spec show <ID>` when their requirements matter to
the assigned work. This guide, projections, session logs and Bridge messages
do not replace those records or the current domain state.

## Purpose and work constitution

GT-KB is a knowledge-management platform for fleets of ephemeral agent contexts.
It provides the instructions, terminology, formal requirements, dependencies,
test instructions and current work state needed for a narrowly scoped assignment.
Continuity belongs to that canonical knowledge and the work product.

A program plans an outcome and sequences execution projects. It carries no
execution authorization and has no work-item membership or work-product commit.
A project defines a complete transition to a usable outcome and groups the
interdependent artifact, configuration and operational changes that finish
together. It is the authorization and coherent commit unit. A work item defines
one testable artifact or control-surface change, or an observable action, and has
exactly one execution-project parent. Names, labels and prose do not establish
membership or turn a program into a project.

Size work around complete results and real dependencies. Several files may form
one inseparable change. Predicted context exhaustion does not justify fragmented
work. A project containing work that cannot finish together requires membership
and scope reconciliation; it cannot be made complete by excluding unfinished work
through a separate completion permission or keep-open marker.

Sources: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`.

## Authority and current knowledge

Apply owner directions directly to the affected established source of truth:
formal requirements, projects, work items or other canonical domain records.
Interactive session logs retain the conversation for harvest when needed.
Do not create an approval archive or decision ledger, and do not use a
deliberation, transcript, Bridge message or prior agent's narrative as current
authority. Correct conflicting instructions and enforcement at their source.

Project authorization is the owner's `authorized` or `not authorized` field.
It controls ordering of new work. New execution projects default to authorized;
the standing hygiene-intake project remains not authorized. Membership and
formal-link changes preserve authorization unless the owner separately directs
its change. Programs have no authorization value. Apply an explicit owner choice
with `gt projects set-authorization`, naming the current project version.
The native project skill describes the fields and readback.

Dispatch selects the next agent action. Immediately before a NEW proposal,
check the current parent project's authorization. A headless refusal returns
BLOCKED for the dispatcher; an interactive context obtains the owner's direction.
A later authorization change does not revoke an already initiated chain.
Independent review, current formal requirements, executable tests and claims
remain separate requirements for the assigned action.

Use the ordinary CLI to read current records. `gt context work-item <WI-ID>`
loads the parent, current formal roots, test instructions and dependencies.
That explicit relationship set is the starting point for applicability
investigation. Independently investigate the complete affected formal closure;
stored proposal citations cannot hide a removed canonical relationship or
replace a missing, inactive or contradictory requirement.

Use `gt backlog record --id <WI-ID> --fields-file <JSON> --expected-version <N>
--actor <context> --change-reason <reason>` to amend current open work. Progress,
description, priority and predecessor changes preserve any existing evidence
gaps while they are reconciled. New implementation work and changes to its
specification or test links require a complete executable evidence pair and an
active test-plan phase. A planning amendment does not establish readiness:
proposal publication rechecks evidence and the current work-item version.
Read back the work and membership after the amendment. See
`DCL-STANDING-BACKLOG-DB-SCHEMA-001` and `GOV-STANDING-BACKLOG-001`.

Sources: `GOV-ARTIFACT-AUTHORITY-HIERARCHY-001`,
`GOV-SOT-SINGLETON-001`, `GOV-SPEC-CAPTURE-TRANSPARENCY-001`,
`DCL-CANONICAL-CARRIER-NONAUTHORITY-001`,
`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-SPEC-RELEVANCE-CLOSURE-001`.

## Ephemeral contexts and Bridge

The exact owner- or dispatch-supplied `::init gtkb pb` or `::init gtkb lo`
establishes the immutable role of the receiving context. Use its native context
identity for the canonical session binding. A harness name, vendor, model or
previous session cannot supply or change that role. Follow the separately
supplied activity and selected target; do not select work by inference.

Prime Builder investigates, proposes and implements. Loyal Opposition
independently reviews and tests. Agents author all proposals, reports and
verdicts. Writers validate complete authored content; they do not repair an
author's routing or invent a verdict. Dispatcher selects and delivers work but
does not author lifecycle messages. Until Dispatcher Next is qualified and
activated, the owner dispatches manually.

The ordinary implementation sequence is NEW, GO, READY, VERIFIED. A rejected
proposal returns NO-GO for revision; a rejected report returns NOT-READY for
correction. Use the complete Bridge contract for other transitions. Keep one
chain per work item. A claim reserves delivery of one exact next artifact with
a current predecessor, version, intended status and fence. It does not assign
ownership of a work item, thread or future action. A successor context obtains
its own claim from current state.

A bridge message is authoritative at receipt and has no continuing authority.
Re-query canonical domain state before later actions. The response is assigned
to an eligible successor context, never reserved for the previous author.

Harnesses are independent and unaware of peers. All coordination goes through
the CLI, Bridge and dispatcher; no harness contacts or inspects another harness.
Use only the current context's scratch and registered checkout. Preserve foreign
work. Revalidate current scope and formal inputs at protected effects.

Sources: `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-HARNESS-ISOLATION-001`,
`DCL-INIT-BOUND-SESSION-IDENTITY-001`, `DCL-BRIDGE-CLAIM-LIFECYCLE-001`.

## Verification, commitment and recovery

VERIFIED records independent review of the exact work described by the proposal
and applicable formal sources. Artifact identity includes each path's Git mode
and object ID, with an explicit absence for deletion. A passing test selection
alone is not complete verification or proof of a commit.

Every project member must be VERIFIED before the complete project commits once.
The CLI instructs the verifying Loyal Opposition context to create that commit
through normal hooks. Include every member's work-item citation. Exclude Bridge
payloads and generated projections; qualify that the exact baseline and projector
sources can produce their derivations. Canonical terminal state mirrors the
successful integrated Git commit. The commit activates the authored work product.
Operational projection refresh materializes derived output.

A precommit artifact change requires fresh independent verification of the
affected result. A failed commit records its specific failure in canonical
coordination state and requests fresh verification without a Dispatcher verdict.
Material formal-intent change after VERIFIED, before commitment, requires a fresh
proposal, review, implementation and verification attempt on the same uncommitted
work item. Preserve its identity, parent and existing bytes; inherit no GO or
effect authority. Unproven migration roots cannot carry prior attempt authority.
A committed work item remains terminal; later changes are new forward work.

After terminal closure remove disposable Bridge content and transient scope.
Retain only the minimal non-content identities needed for terminality, anti-replay
and final-delivery attribution. Bound diagnostics to their active verification
or incident purpose. Out-of-band backups provide recovery.

Sources: `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`,
`GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-WORK-ITEM-TERMINAL-STATE-001`.

## Platform and derived surfaces

The canonical harness-neutral baseline is `.harness-baseline-configuration`.
Named harness configuration is mechanically derived from it. Change baseline or
projector sources and regenerate; never manually edit a generated configuration
or load another harness's files as a fallback. Claims about installed capability
require actual installed behavior, not a directory, source test or registry label.

PostgreSQL behind the CLI and typed services is the canonical storage end state.
Follow current installation and authority configuration; do not fall back to
SQLite or raw tables when the service is unavailable. Installation, complete
import/readback, backup and recovery qualify the sole-authority cutover.

Applications managed by GT-KB remain separate products with their own formal
scope. A platform change does not silently retire application requirements.
Dashboards, search indexes, reports and architecture shards are derived views.
Do not publish an old feature inventory as current health. Read current canonical
state and inspect the actual consumer when assessing readiness or diagnosing a gap.

An architectural correction includes the affected formal sources, work topology,
implementation, tests, rules, skills, projectors and installed consumers. Remove
contradictory current material as part of that closure. Report partial selections
and incomplete capabilities precisely; neither implies platform qualification.

Sources: `GOV-SOT-SINGLETON-001`, `GOV-HARNESS-NEUTRAL-BASELINE-001`,
`REQ-GTKB-HARNESS-BASELINE-PROJECTION-CONTRACT-001`,
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
