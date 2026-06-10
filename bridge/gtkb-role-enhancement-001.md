NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-20260606T0900Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Keep Working PB automation; high autonomy
author_metadata_source: Codex automation context

# Scoping Proposal - GTKB-ROLE-ENHANCEMENT

bridge_kind: prime_proposal
Document: gtkb-role-enhancement
Version: 001
Date: 2026-06-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ROLE-ENHANCEMENT-POST-ISOLATION-SCOPING
Project: PROJECT-GTKB-ROLE-ENHANCEMENT
Work Item: GTKB-ROLE-ENHANCEMENT

target_paths: [".claude/rules/loyal-opposition.md", ".claude/rules/report-depth-prime-builder-context.md", ".claude/rules/file-bridge-protocol.md", ".claude/rules/expedited-paths.md", "groundtruth-kb/templates/rules/loyal-opposition.md", "groundtruth-kb/templates/rules/report-depth.md", "groundtruth-kb/templates/rules/file-bridge-protocol.md", "groundtruth-kb/templates/rules/expedited-paths.md", "groundtruth-kb/templates/managed-artifacts.toml", "platform_tests/"]

## Claim

The post-isolation gate for `GTKB-ROLE-ENHANCEMENT` is now satisfied:
`PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION` is retired, `GTKB-ISOLATION-017`
is resolved with `bridge/gtkb-isolation-017-adopter-packaging-006.md` VERIFIED
evidence, and the project dependency row has been updated to
`blocking_status=satisfied`.

This scoping proposal asks Loyal Opposition to approve the decomposition of the
role-contract enhancement program only. A GO on this parent thread would not
authorize direct rule-file implementation. It would authorize Prime Builder to
file child implementation proposals for the slices below, each with its own
target-path envelope, approval-packet handling, test mapping, implementation
report, and Loyal Opposition verification.

## Scope Boundary

In scope for this parent scoping thread:

- Carry forward the nine role-contract gaps from
  `DELIB-S310-ROLE-DEFINITION-ASSESSMENT`.
- Carry forward the S312 empirical update and its low-cost review-depth
  heuristic from `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE`.
- Treat `DELIB-S381-ROLE-ENHANCEMENT-ISOLATION-DEPENDENCY-REFRAME` as the owner
  decision that parked the work until Phase 9 and now provides the post-gate
  sequencing record.
- Decompose the program into child proposals with explicit target paths and
  test obligations.
- Preserve Prime Builder / Loyal Opposition role asymmetry and the existing file
  bridge state machine.

Out of scope for this parent scoping thread:

- No direct edits to `.claude/rules/`, `groundtruth-kb/templates/`, source, tests,
  hooks, or specs.
- No production deploy, credential lifecycle action, destructive cleanup, or
  history rewrite.
- No owner-waiver of existing bridge review or formal-artifact approval gates.
- No attempt to review this proposal in the same Prime Builder session that
  files it.

## In-Root Placement Evidence

All planned future target paths are inside `E:/GT-KB`. The proposed new rule
paths also stay inside the same rule/template families already used by GT-KB:

- `.claude/rules/loyal-opposition.md`
- `.claude/rules/report-depth-prime-builder-context.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/expedited-paths.md`
- `groundtruth-kb/templates/rules/loyal-opposition.md`
- `groundtruth-kb/templates/rules/report-depth.md`
- `groundtruth-kb/templates/rules/file-bridge-protocol.md`
- `groundtruth-kb/templates/rules/expedited-paths.md`
- `groundtruth-kb/templates/managed-artifacts.toml`
- `platform_tests/`

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
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this NEW proposal
  carries Project Authorization, Project, and Work Item metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision evidence is carried through
  the authorization and Owner Decisions / Input section.
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
  lineage but not as the active project authorization for this thread.
- `DELIB-2322` and `DELIB-2323` - prior review-depth-methodology bridge reviews
  that narrowed pre-isolation work to a deferred-status artifact rather than
  rule mutation.

## Owner Decisions / Input

- `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` records the owner directive: save the
  assessment and refer to it when creating the implementation proposal after
  GT-KB isolation completes.
- `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` records the owner-approved
  update and preserves the deferral until post-isolation.
- `DELIB-S381-ROLE-ENHANCEMENT-ISOLATION-DEPENDENCY-REFRAME` records that Mike
  selected the dependency-chain path instead of waiving the gate or retiring the
  project.
- `PAUTH-PROJECT-GTKB-ROLE-ENHANCEMENT-POST-ISOLATION-SCOPING` is active and
  includes `GTKB-ROLE-ENHANCEMENT` for this post-isolation scoping work.
- No new owner decision is requested by this parent scoping proposal. Loyal
  Opposition should decide GO/NO-GO on whether this decomposition is sufficient.

## Requirement Sufficiency

Existing requirements are sufficient for parent scoping. The parent scope is
derived from the saved S310/S312 role-contract analysis, the S381 owner decision,
and the active project authorization. Child implementation proposals may discover
that a specific clause needs a new GOV/ADR/DCL/PB artifact; if so, that child
must file the additional governance artifact through the normal approval path.

## Proposed Scope

### Slice 1 - Review-depth Methodology

Close the highest-leverage gap from S312: when a proposal includes an output
layout, artifact inventory, target-path inventory, or surface-coverage claim,
Loyal Opposition review must compare that contract against the proposal's
implementation/output list at proposal review time, not only at post-implementation
verification time.

Expected future target paths:

- `.claude/rules/report-depth-prime-builder-context.md`
- `groundtruth-kb/templates/rules/report-depth.md`
- focused tests or lint fixtures that prove proposal-review guidance remains
  installed and discoverable.

### Slice 2 - LO Investigation Authority And Methodology Trail

Clarify that Loyal Opposition may exercise read-only scripts, tests, queries, and
repository inspection during proposal review and implementation verification when
needed to substantiate findings. Require verdicts to document enough methodology
for a future reviewer to match or exceed the review depth.

Expected future target paths:

- `.claude/rules/loyal-opposition.md`
- `groundtruth-kb/templates/rules/loyal-opposition.md`
- role/checklist tests if a deterministic verifier exists or is added.

### Slice 3 - Conflict Resolution And NO-GO Cycle Escalation

Define when repeated NO-GO/REVISED cycles require explicit owner visibility or a
single-decision escalation path, without weakening Loyal Opposition's authority
to issue NO-GO findings.

Expected future target paths:

- `.claude/rules/file-bridge-protocol.md`
- `groundtruth-kb/templates/rules/file-bridge-protocol.md`
- tests or static checks for escalation language if the repository has a suitable
  rule-surface verifier.

### Slice 4 - Expedited Paths General Doctrine

Extract the emergency-path principle already learned from prior incident-response
work: a recurring or expedited execution path can bypass per-instance review only
when the class itself is pre-reviewed, bounded, audited, and followed by mandatory
post-execution Loyal Opposition verification.

Expected future target paths:

- `.claude/rules/expedited-paths.md`
- `groundtruth-kb/templates/rules/expedited-paths.md`
- `groundtruth-kb/templates/managed-artifacts.toml`
- any rule-index or startup-control surfaces needed to load the new rule.

### Slice 5 - Independence, State Access, And Same-Harness Attribution

Clarify the independence guarantee when the same harness can operate in different
roles across sessions, and specify what live state Loyal Opposition is expected to
consult before reviewing role-sensitive bridge work.

Expected future target paths:

- `.claude/rules/loyal-opposition.md`
- `.claude/rules/file-bridge-protocol.md`
- startup/control-map surfaces only if needed by the child proposal and approved
  through its own bridge thread.

## Specification-Derived Verification Plan

| Specification / Requirement | Parent-scope check | Child-scope requirement |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live `bridge/INDEX.md` gains one `NEW` entry for this parent scoping thread. | Each child thread follows NEW -> GO/NO-GO -> implementation -> NEW report -> VERIFIED. |
| `GOV-STANDING-BACKLOG-001` | `GTKB-ROLE-ENHANCEMENT` remains open/backlogged and linked to this bridge thread. | Child proposals update only their scoped work-item/project links. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | S310/S312/S381 decisions are cited here. | Child proposals cite the same source decisions plus any new owner decisions they require. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata resolves to an active project authorization and membership. | Every child implementation proposal carries its own project metadata. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This parent plan maps each future slice to a verification obligation. | Child implementation reports must include executed tests or explicit non-code verification evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All planned paths are under `E:/GT-KB`. | Child proposals must repeat path-boundary evidence for their exact targets. |

## Acceptance Criteria

- Loyal Opposition can determine from this parent proposal which child slices are
  expected and which role-contract gaps each slice addresses.
- The parent GO, if granted, is explicitly limited to decomposition approval and
  follow-on child proposal filing.
- The active role-enhancement project authorization is cited and bounded.
- The previous Phase 9 blocker is not silently ignored; its satisfied evidence is
  recorded in the Claim and Owner Decisions / Input sections.
- No direct source, rule, template, hook, spec, or test mutation is performed by
  this parent thread.

## Risks / Rollback

- Risk: the parent scope is too broad for useful review. Mitigation: the proposed
  slices are independently reviewable and can be split further by Loyal Opposition
  NO-GO without losing the parent record.
- Risk: a child slice needs a new formal GOV/ADR/DCL/PB artifact. Mitigation: the
  child proposal must identify that need and use the normal formal artifact
  approval path before implementation.
- Risk: existing template surfaces differ from live `.claude/rules` surfaces.
  Mitigation: each child proposal must inspect both live and template surfaces and
  state whether the child edits one or both.
- Rollback: withdraw or supersede this parent scoping thread before child work
  begins. If a child thread has already started, rollback is handled in that
  child's own bridge lifecycle.

## Files Expected To Change

This parent scoping proposal changes no implementation files. If Loyal Opposition
grants GO, future child proposals may target:

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

## Pre-Filing Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-role-enhancement --content-file .gtkb-state\bridge-propose-drafts\gtkb-role-enhancement-001.md
```

Observed before live filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `warnings.missing_parent_dirs: []`

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-role-enhancement --content-file .gtkb-state\bridge-propose-drafts\gtkb-role-enhancement-001.md
```

Observed before live filing:

- `must_apply: 4`
- `Evidence gaps in must_apply clauses: 0`
- `Blocking gaps (gate-failing): 0`
- Exit code: `0`

## Recommended Commit Type

`docs`
