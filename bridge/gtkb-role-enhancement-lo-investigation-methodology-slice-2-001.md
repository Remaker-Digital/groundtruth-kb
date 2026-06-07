NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-20260607T0705Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Keep Working PB automation; high autonomy
author_metadata_source: Codex automation context

# Implementation Proposal - Role Enhancement LO Investigation Methodology Slice 2

bridge_kind: implementation_proposal
Document: gtkb-role-enhancement-lo-investigation-methodology-slice-2
Version: 001
Date: 2026-06-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ROLE-ENHANCEMENT-POST-ISOLATION-SCOPING
Project: PROJECT-GTKB-ROLE-ENHANCEMENT
Work Item: GTKB-ROLE-ENHANCEMENT

target_paths: [".claude/rules/loyal-opposition.md", "groundtruth-kb/templates/rules/loyal-opposition.md", "platform_tests/scripts/test_lo_investigation_methodology.py"]

## Claim

This child proposal implements Slice 2 from the GO-approved parent
`bridge/gtkb-role-enhancement-004.md`: Loyal Opposition investigation authority
and methodology trail.

The implementation will clarify that Loyal Opposition may use read-only
repository inspection, scripts, tests, CLI queries, and database reads during
proposal review and implementation verification when those checks are needed to
substantiate a finding or positive confirmation. It will also require verdicts
to document enough methodology for a later reviewer to reproduce or exceed the
review depth.

This proposal does not authorize implementation by itself. Implementation may
start only after this child proposal receives GO and
`scripts/implementation_authorization.py begin --bridge-id gtkb-role-enhancement-lo-investigation-methodology-slice-2`
mints a valid packet.

## Scope Boundary

In scope:

- Update `.claude/rules/loyal-opposition.md` with an explicit read-only
  investigation authority and methodology-trail clause.
- Update `groundtruth-kb/templates/rules/loyal-opposition.md` so scaffolded or
  upgraded rule surfaces carry the same authority and methodology doctrine.
- Add focused tests in
  `platform_tests/scripts/test_lo_investigation_methodology.py` proving both
  target rule surfaces contain the required authority and methodology anchors.

Out of scope:

- Mutating `.claude/rules/report-depth-prime-builder-context.md`,
  `.claude/rules/file-bridge-protocol.md`, `.claude/rules/expedited-paths.md`,
  or any formal GOV, ADR, DCL, PB, SPEC, or requirement artifact.
- Direct MemBase mutation.
- Granting Loyal Opposition write authority beyond the existing file-safety
  and bridge-function exceptions already present in the rule.
- Production deployment, credential lifecycle action, destructive cleanup, or
  repository-history rewrite.
- Reviewing or verifying this proposal in the same Prime Builder session that
  files it.

The two narrative-rule/template targets are protected artifact surfaces. The
post-implementation report must include the applicable formal-artifact approval
evidence or explicitly show that the live governance gate did not require a
separate approval packet for the exact edit.

## Requirement Sufficiency

Existing requirements sufficient.

The parent GO at `bridge/gtkb-role-enhancement-004.md` authorizes child proposal
filing for LO investigation authority and methodology trail. `DELIB-S310-ROLE-DEFINITION-ASSESSMENT`
identifies LO investigation authority and methodology audit trail as
underdefined role-contract gaps. `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE`
confirms those gaps remain live and recommends sharpening review methodology
after the post-isolation dependency clears. No new owner decision is required
for this child proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this child proposal uses the live file
  bridge as the approval and review authority before any implementation.
- `GOV-STANDING-BACKLOG-001` - `GTKB-ROLE-ENHANCEMENT` remains the tracked open
  backlog item under `PROJECT-GTKB-ROLE-ENHANCEMENT`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the role-contract gap, owner
  decisions, implementation proposal, and future verification are preserved as
  durable artifacts.
- `GOV-ARTIFACT-APPROVAL-001` - implementation touches protected narrative
  rule/template surfaces and must carry approval evidence where the gate
  requires it.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the investigation-methodology
  contract is advanced through an explicit lifecycle artifact rather than ad
  hoc rule edits.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are within the
  GT-KB project root and no external project path is used.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the satisfied post-isolation
  dependency and parent GO trigger this child implementation proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries
  Project Authorization, Project, and Work Item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section links
  concrete governing specifications for the child scope.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps
  each linked rule contract to concrete tests and preflights.
- `SPEC-AUQ-POLICY-ENGINE-001` - existing owner decisions and the active
  project authorization are the approval evidence; no new owner question is
  required.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - generated or scaffolded rule surfaces
  must preserve Codex/Claude parity expectations by updating the template
  alongside the live Loyal Opposition rule.

## Prior Deliberations

- `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` - originating nine-gap role-definition
  assessment; identifies LO investigation authority and methodology audit trail
  as role-contract gaps.
- `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` - empirical update preserving
  the post-isolation sequencing constraint and confirming the role-contract
  gaps remain live.
- `DELIB-S381-ROLE-ENHANCEMENT-ISOLATION-DEPENDENCY-REFRAME` - owner decision
  that parked role enhancement until the Phase 9 dependency was satisfied.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - historical authorization
  lineage only; the active authorization for this proposal is the project
  authorization named above.
- `DELIB-2741` - prior role-enhancement review-depth bridge history, useful
  as methodology precedent but not a blocker for this slice.
- `bridge/gtkb-role-enhancement-004.md` - parent GO authorizing child proposal
  filing, not direct implementation.

## Owner Decisions / Input

- Mike's role-enhancement directive is preserved by
  `DELIB-S310-ROLE-DEFINITION-ASSESSMENT`.
- Mike's post-isolation sequencing decision is preserved by
  `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE`.
- Mike's dependency-chain path is preserved by
  `DELIB-S381-ROLE-ENHANCEMENT-ISOLATION-DEPENDENCY-REFRAME`.
- `PAUTH-PROJECT-GTKB-ROLE-ENHANCEMENT-POST-ISOLATION-SCOPING` is active and
  includes `GTKB-ROLE-ENHANCEMENT`.
- No new owner decision is requested. Loyal Opposition should decide GO/NO-GO
  on whether this child proposal is sufficient.

## Proposed Implementation

### IP-1 - Live Loyal Opposition Rule

Add a focused investigation-methodology clause to
`.claude/rules/loyal-opposition.md`.

Required anchors:

- LO may run read-only scripts, tests, CLI queries, repository inspection, and
  MemBase/database reads when needed to substantiate review findings.
- The authority is read-only unless an existing rule exception or explicit
  owner authorization permits mutation.
- Verdicts should document commands, files, queries, and inspection steps at a
  level sufficient for a later reviewer to reproduce or exceed the review.
- The methodology trail applies to proposal review and post-implementation
  verification.

### IP-2 - Scaffold Template Rule

Update `groundtruth-kb/templates/rules/loyal-opposition.md` with matching
doctrine so managed/scaffolded rule output does not drift from the live Loyal
Opposition rule.

### IP-3 - Focused Tests

Add `platform_tests/scripts/test_lo_investigation_methodology.py` with tests
that assert both target rule surfaces contain the methodology anchors:

- read-only scripts
- tests
- CLI queries
- repository inspection
- MemBase or database reads
- methodology trail
- reproduce or exceed review depth
- proposal review and implementation verification

The tests must also assert that the proposed target paths remain in the GT-KB
root and do not reference archive or external project roots.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use only rule text and synthetic test assertions; do not add credential-shaped fixtures. | Credential scanner/hook and focused test review. | |
| CQ-PATHS-001 | Yes | Mutate only the declared in-root rule, template, and test paths. | Implementation-start packet plus `git diff --name-only` review. | |
| CQ-COMPLEXITY-001 | Yes | Keep the implementation to narrative text and small deterministic assertions. | Ruff check and focused test review. | |
| CQ-CONSTANTS-001 | Yes | Keep any anchor-word list local to the focused test unless reuse appears. | Ruff check and test review. | |
| CQ-SECURITY-001 | Yes | Do not change authorization, credential, deploy, or bridge bypass behavior. | Diff review and bridge preflights. | |
| CQ-DOCS-001 | Yes | Update the rule/template text with concise, actionable methodology wording. | Focused tests assert required documentation anchors. | |
| CQ-TESTS-001 | Yes | Add a focused pytest module covering both target rule surfaces. | `python -m pytest platform_tests/scripts/test_lo_investigation_methodology.py -q --tb=short`. | |
| CQ-LOGGING-001 | Yes | Do not add logging behavior for this rule/template/test slice. | Diff review confirms no logging surface is introduced. | |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, scoped Ruff, bridge applicability preflight, and ADR/DCL clause preflight before report filing. | Commands and results are recorded in the implementation report. | |

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: run
  `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-role-enhancement-lo-investigation-methodology-slice-2 --format json --preview-lines 20`.
  Acceptance: the child thread is indexed with latest `NEW` after filing, then
  GO/NO-GO is left to Loyal Opposition.
- `GOV-STANDING-BACKLOG-001`: run
  `uv run --project groundtruth-kb gt backlog list --id GTKB-ROLE-ENHANCEMENT --json`
  and `uv run --project groundtruth-kb gt projects show PROJECT-GTKB-ROLE-ENHANCEMENT --json`.
  Acceptance: work item is open, project is active, and PAUTH includes the work
  item.
- `GOV-ARTIFACT-APPROVAL-001`: check formal-artifact approval evidence during
  implementation report filing. Acceptance: protected narrative edits are
  accompanied by required approval evidence or a gate-proven no-packet-required
  statement.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: run the focused tests in
  `platform_tests/scripts/test_lo_investigation_methodology.py`.
  Acceptance: target paths are in-root and no archive/external root is
  referenced.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run
  `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-enhancement-lo-investigation-methodology-slice-2`.
  Acceptance: no missing required specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run
  `python -m pytest platform_tests/scripts/test_lo_investigation_methodology.py -q --tb=short`.
  Acceptance: focused tests pass and cover both target surfaces.
- Template/live rule parity: run the same focused pytest command. Acceptance:
  live and template rule surfaces both carry the same required anchors.
- Python quality for the new test: run
  `python -m ruff check platform_tests/scripts/test_lo_investigation_methodology.py`
  and `python -m ruff format --check platform_tests/scripts/test_lo_investigation_methodology.py`.
  Acceptance: Ruff check and format check pass.
- Clause applicability: run
  `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-enhancement-lo-investigation-methodology-slice-2`.
  Acceptance: exit 0 with zero blocking gaps.

## Acceptance Criteria

- Loyal Opposition has explicit read-only investigation authority for proposal
  review and implementation verification.
- Verdicts are required to leave a methodology trail sufficient for a later
  reviewer to reproduce or exceed the review depth.
- The live Loyal Opposition rule and scaffold template carry matching doctrine.
- Focused tests fail if either target surface loses the core authority or
  methodology anchors.
- No implementation starts from this child proposal until GO and a valid
  implementation-start authorization packet exist.

## Risks / Rollback

- Risk: the rule text is misread as mutation authority. Mitigation: the
  implementation must explicitly preserve the read-only boundary and existing
  LO file-safety rule.
- Risk: template/live rule drift. Mitigation: focused tests assert both
  surfaces.
- Risk: protected narrative approval handling is missed. Mitigation: the
  implementation report must include the approval evidence or gate result for
  the protected rule/template edits.
- Rollback: revert the rule/template/test edits from the implementation report
  if Loyal Opposition rejects the implemented result; this proposal itself can
  be superseded or withdrawn before implementation starts.

## Pre-Filing Preflight

Candidate-content checks before live filing are performed by the helper-mediated
bridge write path and the follow-up live preflight commands recorded in this run.
Expected filing condition: the bridge-compliance audit passes before write,
then live applicability preflight passes with no missing required specs and
ADR/DCL clause preflight exits 0 with zero blocking gaps.

## Recommended Commit Type

docs
