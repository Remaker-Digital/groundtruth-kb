REVISED
author_identity: Claude Code
author_harness_id: B
author_session_context_id: 544b584c-7392-4d40-81d8-dba187ba11eb
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; interactive; Prime Builder; /loop dynamic
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Scoping Proposal Revision - GTKB-ROLE-ENHANCEMENT

bridge_kind: prime_proposal
Document: gtkb-role-enhancement
Version: 003
Date: 2026-06-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ROLE-ENHANCEMENT-POST-ISOLATION-SCOPING
Project: PROJECT-GTKB-ROLE-ENHANCEMENT
Work Item: GTKB-ROLE-ENHANCEMENT

target_paths: []

## Revision Claim

This revision addresses `bridge/gtkb-role-enhancement-002.md` F1 by changing the
parent scoping packet into a non-implementation envelope. The parent proposal
still asks Loyal Opposition to approve the role-enhancement decomposition, but a
GO on this parent must not authorize direct rule, template, source, hook, spec,
or test mutation.

The future implementation paths from `-001` are preserved below as child-slice
planning context only. They are no longer exposed through machine-readable
`target_paths`, and this parent does not authorize
`python scripts/implementation_authorization.py begin --bridge-id gtkb-role-enhancement`.

## Finding Addressed

### F1 - Scoping-Only Prose Conflicts With A Direct Implementation Target Envelope

Response: corrected. The parent packet now declares `target_paths: []`, which
prevents the parent GO from serving as a direct implementation-start mutation
envelope. Future rule/template/test paths are listed only in the "Future Child
Target Envelopes" section. Each child implementation proposal must carry its own
concrete `target_paths`, project metadata, formal-artifact approval handling
where needed, spec-derived verification plan, implementation report, and Loyal
Opposition verification.

## Scope Boundary

In scope for this parent scoping thread:

- Carry forward the nine role-contract gaps from
  `DELIB-S310-ROLE-DEFINITION-ASSESSMENT`.
- Carry forward the S312 empirical update and its low-cost review-depth
  heuristic from `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE`.
- Treat `DELIB-S381-ROLE-ENHANCEMENT-ISOLATION-DEPENDENCY-REFRAME` as the owner
  decision that parked the work until Phase 9 and now provides the post-gate
  sequencing record.
- Approve or reject the decomposition into child proposals only.
- Preserve Prime Builder / Loyal Opposition role asymmetry and the existing file
  bridge state machine.

Out of scope for this parent scoping thread:

- Direct edits to `.claude/rules/`, `groundtruth-kb/templates/`, source, tests,
  hooks, specs, or formal governance artifacts.
- Starting an implementation authorization packet from this parent bridge id.
- Production deploy, credential lifecycle action, destructive cleanup, or
  history rewrite.
- Owner waiver of existing bridge review or formal-artifact approval gates.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this parent proposal uses the file bridge as
  the sole approval and review mechanism; child implementation proposals remain
  bridge-gated.
- `GOV-STANDING-BACKLOG-001` - `GTKB-ROLE-ENHANCEMENT` is the tracked backlog
  work item, now unblocked after the Phase 9 dependency reached terminal
  evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - role-contract gaps, owner decisions,
  dependency clearance, and child-slice obligations are preserved as durable
  artifacts instead of chat-only state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the program is decomposed into
  governed artifacts with explicit lifecycle transitions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the satisfied dependency and
  post-isolation transition trigger a new scoping artifact before rule mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links
  relevant governing specifications; every child implementation proposal must
  repeat concrete spec linkage for its own scope.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - child implementation
  reports must map each linked specification and role-contract clause to
  executed verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revised proposal
  carries Project Authorization, Project, and Work Item metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision evidence is carried through the
  authorization and Owner Decisions / Input section.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains under the GT-KB
  root and does not treat Agent Red as a GT-KB artifact.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - child proposals that touch Codex/Claude
  parity or hook behavior must preserve the documented parity fallback model.

## Prior Deliberations

- `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` - originating nine-gap role-definition
  assessment and future implementation direction.
- `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` - empirical update confirming
  the gaps remain real, preserving the post-isolation sequencing constraint, and
  recommending the low-cost review-depth heuristic.
- `DELIB-S381-ROLE-ENHANCEMENT-ISOLATION-DEPENDENCY-REFRAME` - owner decision to
  park role enhancement on Phase 9 productization rather than waive the gate.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - historical owner decision
  authorizing future bridge dispatch for grouped GT-KB project work; cited as
  lineage, not as the active project authorization for this thread.
- `DELIB-2322` and `DELIB-2323` - prior review-depth-methodology bridge reviews
  that narrowed pre-isolation work to a deferred-status artifact rather than
  rule mutation.

## Owner Decisions / Input

- `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` records the owner directive to save
  the assessment and refer to it when creating the implementation proposal after
  GT-KB isolation completes.
- `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` records the owner-approved
  update and preserves the deferral until post-isolation.
- `DELIB-S381-ROLE-ENHANCEMENT-ISOLATION-DEPENDENCY-REFRAME` records that Mike
  selected the dependency-chain path instead of waiving the gate or retiring the
  project.
- `PAUTH-PROJECT-GTKB-ROLE-ENHANCEMENT-POST-ISOLATION-SCOPING` is active and
  includes `GTKB-ROLE-ENHANCEMENT` for this post-isolation scoping work.
- No new owner decision is requested by this revision. Loyal Opposition should
  decide GO/NO-GO on whether the corrected parent envelope and decomposition are
  sufficient.

## Proposed Scope

### Slice 1 - Review-depth Methodology

Close the highest-leverage gap from S312: when a proposal includes an output
layout, artifact inventory, target-path inventory, or surface-coverage claim,
Loyal Opposition review must compare that contract against the proposal's
implementation/output list at proposal review time, not only at
post-implementation verification time.

### Slice 2 - LO Investigation Authority And Methodology Trail

Clarify that Loyal Opposition may exercise read-only scripts, tests, queries,
and repository inspection during proposal review and implementation verification
when needed to substantiate findings. Require verdicts to document enough
methodology for a future reviewer to match or exceed the review depth.

### Slice 3 - Conflict Resolution And NO-GO Cycle Escalation

Define when repeated NO-GO/REVISED cycles require explicit owner visibility or a
single-decision escalation path, without weakening Loyal Opposition's authority
to issue NO-GO findings.

### Slice 4 - Expedited Paths General Doctrine

Extract the emergency-path principle already learned from prior incident-response
work: a recurring or expedited execution path can bypass per-instance review
only when the class itself is pre-reviewed, bounded, audited, and followed by
mandatory post-execution Loyal Opposition verification.

### Slice 5 - Independence, State Access, And Same-Harness Attribution

Clarify the independence guarantee when the same harness can operate in
different roles across sessions, and specify what live state Loyal Opposition is
expected to consult before reviewing role-sensitive bridge work.

## Future Child Target Envelopes

These paths are planning context for future child proposals only. They are not
authorized by this parent thread and must not be consumed as this parent's
implementation envelope:

- `.claude/rules/loyal-opposition.md`
- `.claude/rules/report-depth-prime-builder-context.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/expedited-paths.md`
- `groundtruth-kb/templates/rules/loyal-opposition.md`
- `groundtruth-kb/templates/rules/report-depth.md`
- `groundtruth-kb/templates/rules/file-bridge-protocol.md`
- `groundtruth-kb/templates/rules/expedited-paths.md`
- `groundtruth-kb/templates/managed-artifacts.toml`
- focused tests under `platform_tests/`

## Specification-Derived Verification Plan

| Specification / Requirement | Parent-scope check | Child-scope requirement |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live `bridge/INDEX.md` gains one `REVISED` entry for this parent scoping thread. | Each child thread follows NEW to GO/NO-GO to implementation to NEW report to VERIFIED. |
| `GOV-STANDING-BACKLOG-001` | `GTKB-ROLE-ENHANCEMENT` remains open/backlogged and linked to this bridge thread. | Child proposals update only their scoped work-item/project links. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | S310/S312/S381 decisions are cited here. | Child proposals cite the same source decisions plus any new owner decisions they require. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata resolves to an active project authorization and membership. | Every child implementation proposal carries its own project metadata. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This parent plan maps each future slice to a verification obligation. | Child implementation reports include executed tests or explicit non-code verification evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All planned future paths are under `E:/GT-KB`. | Child proposals repeat path-boundary evidence for their exact targets. |

## Acceptance Criteria

- Loyal Opposition can determine which child slices are expected and which
  role-contract gaps each slice addresses.
- The parent GO, if granted, is limited to decomposition approval and follow-on
  child proposal filing.
- The active role-enhancement project authorization is cited and bounded.
- The previous Phase 9 blocker is not silently ignored; its satisfied evidence is
  recorded in the claim and owner-decision sections.
- The parent cannot mint a direct implementation-start packet for future child
  rule/template/test paths because its `target_paths` envelope is empty.

## Risks / Rollback

- Risk: the parent scope is too broad for useful review. Mitigation: the
  proposed slices are independently reviewable and can be split further by Loyal
  Opposition NO-GO without losing the parent record.
- Risk: a child slice needs a new formal GOV/ADR/DCL/PB artifact. Mitigation:
  the child proposal must identify that need and use the normal formal artifact
  approval path before implementation.
- Risk: existing template surfaces differ from live `.claude/rules` surfaces.
  Mitigation: each child proposal must inspect both live and template surfaces
  and state whether the child edits one or both.
- Rollback: withdraw or supersede this parent scoping thread before child work
  begins. If a child thread has already started, rollback is handled in that
  child's own bridge lifecycle.

## Pre-Filing Preflight

The revision helper runs the candidate-content gates before live filing:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-enhancement --content-file .gtkb-state\bridge-revisions\drafts\gtkb-role-enhancement-003.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-enhancement --content-file .gtkb-state\bridge-revisions\drafts\gtkb-role-enhancement-003.md
```

Expected acceptance condition for filing: applicability preflight passes with no
missing required specs, and ADR/DCL clause preflight exits 0 with zero blocking
gaps. The helper refuses to file the revision if either condition fails.

## Recommended Commit Type

`docs`
