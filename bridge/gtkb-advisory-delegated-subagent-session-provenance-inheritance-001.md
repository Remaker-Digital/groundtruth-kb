NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
delegated_codex_thread_id: 019fb30a-3723-7c80-b4da-5e873f7d17c4
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; delegated subagent execution; governed attribution inherited from the owner-declared parent session; dispatcher deliberately disabled

bridge_kind: governance_review
Document: gtkb-advisory-delegated-subagent-session-provenance-inheritance
Version: 001
Date: 2026-07-30 UTC
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Related Work Items: WI-5749, WI-5750, WI-5751, WI-5790

target_paths: []
implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Advisory Proposal - Delegated subagent session provenance is not inherited automatically

## Executive Summary

A Prime Builder subagent delegated to perform governed project and work-item
intake inherited the repository and conversation context, but did not inherit
the parent GT-KB session identifier in the environment consumed by canonical
MemBase writers. The subagent ambient environment exposed only its child Codex
task id, `019fb30a-3723-7c80-b4da-5e873f7d17c4`, while the owner-declared and
governing interactive Prime Builder session was
`019fb19b-7814-73c1-8707-204e432cbf00`.

The governed `gt backlog add-work-item --dry-run` path correctly failed closed
before mutation with:

```text
Error: resolve_changed_by: Worker role provenance session id does not match the current session.
```

A bounded command-scoped workaround explicitly set
`GTKB_INHERITED_SESSION_ID=019fb19b-7814-73c1-8707-204e432cbf00`. The same
dry-run then succeeded, and the governed atomic command subsequently created
WI-5790, TEST-11757, and active project membership
`PWM-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI-5790`. No shared session
marker, envelope, harness identity, dispatcher, or TAFE state was rewritten.

The fail-closed attribution check is correct and must remain. The defect is the
missing automatic delegation handoff: a child agent that is explicitly acting
inside the parent's governed GT-KB session is not given the canonical inherited
session identity that existing resolver precedence already understands.

This proposal will be filed only as the first append-only numbered bridge file,
`bridge/gtkb-advisory-delegated-subagent-session-provenance-inheritance-001.md`,
through the typed writer. No prior numbered bridge file is deleted or rewritten.

## Advisory Classification

- Category: concurrent agent orchestration, session provenance, governed-writer
  liveness, delegation parity.
- Severity: high for safe parallel execution; medium for data integrity because
  the current writer fails closed rather than silently mutating.
- Affected boundary: mutating CLI calls executed by delegated Codex subagents
  inside an owner-declared interactive GT-KB session.
- Artifact posture: Prime Builder Advisory Proposal for independent review. It
  is not an implementation proposal, GO, PAUTH, implementation-start packet,
  or implementation authority.

## Claim

GT-KB's canonical attribution resolver supports an explicit inherited session
identifier, but the current Codex subagent delegation path does not populate it.
As a result, parallel Prime Builder work that reaches a governed MemBase writer
is either blocked or depends on a human/agent manually copying the parent
session id into every mutating command.

The correct repair is not to weaken identity matching and not to make the child
Codex task id authoritative by inference. The delegation boundary should emit
an explicit, auditable parent-to-child GT-KB session handoff whose identity is
automatically available to canonical writers while preserving the child task
id as execution provenance.

## Evidence E1 - The delegated environment selected the child task id

At the failure point, the delegated execution context exposed:

```text
CODEX_THREAD_ID=019fb30a-3723-7c80-b4da-5e873f7d17c4
```

It did not expose the governing parent's session id through
`GTKB_INHERITED_SESSION_ID`. The parent task had explicitly delegated the
bounded intake and identified its governed interactive session as:

```text
019fb19b-7814-73c1-8707-204e432cbf00
```

This is a normal and useful two-identity situation: the child task id identifies
the concrete worker execution, while the inherited parent id identifies the
GT-KB session envelope and role authority under which the work was delegated.
The current environment transmitted only the former.

## Evidence E2 - The canonical writer failed closed before mutation

The first governed dry-run used the normal work-item CLI and made no database
change. It failed with the exact provenance mismatch quoted above.

`scripts/_kb_attribution.py:31-56` shows the enforcement path. `_current_session_id()`
calls `resolve_session_id(order=BRIDGE_WORK_INTENT_ORDER)`, and
`resolve_changed_by()` passes that id to `resolve_worker_role_provenance()`.
Any envelope mismatch is converted to a `RuntimeError` before the mutation.

This behavior prevented false attribution. Replacing it with a permissive
fallback would turn a safe liveness defect into an integrity defect.

## Evidence E3 - Existing resolver precedence already supports the safe handoff

`scripts/gtkb_session_id.py:78-88` defines the relevant order. In a Codex child
context, `GTKB_INHERITED_SESSION_ID` precedes `CODEX_THREAD_ID`. Therefore the
bounded command-scoped value selected the canonical parent session without
changing persistent session state or suppressing the child's own task identity
outside the governed command.

With that one scoped environment value:

1. the repeated `gt backlog add-work-item --dry-run` succeeded;
2. the actual governed atomic add succeeded;
3. WI-5790 was attributed to `prime-builder/codex`;
4. TEST-11757 was created by the standard GOV-12 path; and
5. project membership row 4144 linked WI-5790 to the active, whole-project-
   authorized `PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729` project.

This proves the resolver and project lifecycle can already consume the right
identity. The missing link is automatic, typed propagation at delegation time.

## Evidence E4 - This is distinct from WI-5749, WI-5750, and WI-5751

The three named candidate carriers were inspected before recommending a route:

- WI-5749 concerns a shared `.claude/session/envelope.json` projection being
  overwritten across concurrent harnesses. No shared-envelope overwrite was
  observed here; the child process simply lacked an inherited parent identity.
- WI-5750 concerns a transcript-defined interactive role reverting to the
  durable registry during a later SessionStart boundary. No role transition or
  registry fallback occurred here; the mismatch was between two session ids.
- WI-5751 concerns `gt session envelope open --role` reporting success without
  persisting the requested repair. No envelope-open repair was attempted or
  needed in this incident.

None is a precise carrier. Expanding any one would blur its existing acceptance
boundary and make verification ambiguous.

## Prior Deliberation

`DELIB-202666850` recorded an earlier governed backlog-writer failure with the
same exact error string and identified the divergent session-id resolution path
as a follow-on investigation. That record did not establish the delegated
Codex parent/child reproduction captured here, but it confirms this error class
has recurred and is not unique to WI-5790 intake.

`DELIB-20260710-GTKB-INTERACTIVE-KB-ATTRIBUTION-GLOBAL-MARKER-COLLISION`
documents a related but different integrity hazard: a shared role marker caused
silent misattribution. Together the cases support an explicit session-scoped
handoff and fail-closed mismatch behavior, not reliance on global projections.

## Risk and Impact

### R1 - Parallel Prime Builder work is blocked at the safe write boundary

The owner explicitly requested subagent parallelization. Delegated workers can
investigate, but canonical mutations fail when the child task id is mistaken
for the governed session envelope id. This defeats the elapsed-time benefit at
the point where useful work becomes durable.

### R2 - Manual workarounds are fragile

Copying a parent session id into individual commands is easy to omit and easy to
apply to the wrong parent. It also spreads orchestration knowledge into every
skill and writer invocation instead of keeping it at the delegation boundary.

### R3 - A permissive fallback would corrupt provenance

Accepting any ambient child task id, reusing a shared marker, or silently
choosing an unrelated live envelope could misattribute author role, defeat
self-review isolation, or attach mutations to the wrong session. The existing
failure must remain fail closed when no explicit handoff exists.

### R4 - Retry and duplicate-work pressure

A delegated agent that sees only a generic provenance mismatch may retry the
same writer, recreate intake work in the parent, or attempt a noncanonical
write. Typed diagnostics should distinguish `missing delegation handoff` from
`conflicting session identity` and return the parent/child evidence without
exposing an unsafe bypass.

## Single Proposed Corrective Route

Create one new, non-duplicate work item under
`PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729`, only after Loyal Opposition
confirms this Advisory. Suggested title:

```text
Propagate canonical inherited GT-KB session identity into delegated subagents
```

The work item should cover exactly one correction boundary:

1. when an authenticated parent GT-KB session delegates a child agent, create a
   typed handoff binding parent session id, child execution id, harness, role,
   creation time, and delegation scope;
2. expose the parent id to the child as the canonical inherited-session input
   before any governed writer executes;
3. retain the child task id as distinct execution provenance rather than
   overwriting or pretending it is the parent id;
4. reject absent, expired, mismatched, cross-harness, or unrelated handoffs;
5. ensure nested delegation propagates the same governed parent session plus a
   verifiable child chain without adopting an ambient peer session;
6. provide diagnostics that distinguish missing handoff from actual role or
   envelope drift; and
7. make no dispatcher/TAFE activation or mutation part of the solution.

This is one proposed route only. This Advisory does not create the work item or
approve implementation. If confirmed, project membership would carry the
owner-approved whole-project PAUTH under the project's current authorization
model; no per-work-item PAUTH should be created.

## Specification-Derived Verification Plan

The future corrective work item must map the linked session-authority,
provenance, deterministic-service, and worktree-hygiene requirements to focused
tests. The expected executable lane is `python -m pytest` against the session
delegation, MemBase attribution, and bridge author-metadata test modules. This
Advisory reports no executed implementation tests because it proposes future
work and contains no implementation.

### A. Basic parent-to-child mutation

1. Open a canonical interactive Prime Builder session.
2. Spawn a delegated child with a distinct Codex task id.
3. Execute a governed work-item dry-run from the child without manually setting
   `GTKB_INHERITED_SESSION_ID`.
4. Assert it succeeds and attributes the mutation to the parent's governed role
   while recording the child task id as execution provenance.

### B. Fail-closed negative cases

Assert the writer rejects missing, malformed, expired, wrong-parent,
wrong-harness, wrong-role, and unrelated-concurrent-session handoffs. Assert no
database version, membership, test, claim, bridge artifact, or session marker is
mutated on every rejection.

### C. Nested and concurrent delegation

Run two sibling children and one nested grandchild. Assert all have distinct
execution ids, the intended governed parent chain is stable, writes are
correctly attributed, and no child can borrow the sibling's session handoff.

### D. Existing session-lifecycle non-regression

Re-run the WI-5749 shared-projection, WI-5750 transcript-role persistence, and
WI-5751 envelope-open persistence suites. The delegation correction must not
weaken or silently absorb those separate boundaries.

### E. Disabled dispatcher boundary

Keep TAFE/dispatcher disabled throughout the integration test. Assert no
process start, wake, enablement, configuration write, dispatch-state publication,
or TAFE mutation occurs.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - role authority must resolve from the
  correct session context.
- `DCL-SESSION-ROLE-RESOLUTION-001` - session identity and role resolution must
  be deterministic and fail closed on ambiguity.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - the owner's transcript-
  defined interactive role persists through contiguous delegated work.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - delegated execution must not
  silently revert or substitute role/session authority.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - formal artifacts require credible
  per-session author provenance.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - delegation identity propagation
  should be a deterministic service boundary, not repeated agent ceremony.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this Advisory must use the governed typed
  bridge writer and role-correct NEW status.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the reproduced concurrency defect
  warrants durable advisory capture.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the proposed handoff is a durable,
  testable lifecycle artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - confirmed implementation work should
  route to one project member work item after review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - any later proposal
  must trace its exact handoff contract to governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any later correction must
  prove parent, child, nested, concurrent, and rejection behavior.
- `GOV-WORK-TREE-HYGIENE-001` - concurrent child work must not overwrite or
  adopt another session's state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all governed artifacts and tests
  remain inside `E:\GT-KB`.

## Requirement Sufficiency

The existing specifications are sufficient to preserve and review the defect.
A later implementation proposal should make the typed parent-child handoff
schema and lifecycle explicit in its work-item acceptance criteria; no new
formal GOV, ADR, or DCL is requested by this Advisory.

## Owner Decisions / Input

No owner decision is required to file this Advisory Proposal. The owner already
directed that concurrency flaws be captured as Advisory Reports and approved
whole-project authorization for the Advisory Corrections project.

If Loyal Opposition confirms the finding and its non-duplication analysis,
Prime Builder should create exactly the single proposed work item under the
active project and proceed through the normal proposal, independent GO, claim,
implementation-start, and verification gates. No per-work-item approval should
be requested or created.

## Explicit Non-Approval and TAFE Exclusion

This Advisory Proposal is not a GO, PAUTH, implementation proposal,
implementation-start packet, commit authority, release authority, or deployment
authority. It authorizes no source, test, configuration, metadata, Git,
credential, external-system, dispatcher, or TAFE mutation. The TAFE dispatcher
remained deliberately disabled throughout the incident and workaround and must
remain outside any corrective scope.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
