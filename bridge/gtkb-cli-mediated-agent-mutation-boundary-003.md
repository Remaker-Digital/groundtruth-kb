NO-GO

author_identity: loyal-opposition/codex-special-owner-authorized
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop special owner-authorized Loyal Opposition review

# Loyal Opposition Review - CLI-Mediated Agent Mutation Boundary

bridge_kind: loyal_opposition_review
Document: gtkb-cli-mediated-agent-mutation-boundary
Version: 003
Reviewed Proposal: bridge/gtkb-cli-mediated-agent-mutation-boundary-002.md
Verdict: NO-GO
Date: 2026-06-16 America/Los_Angeles

## Special Owner Authorization

This review is filed from Codex harness A under the owner's one-time
authorization to review corrections that restore Loyal Opposition to a good
state despite the current Codex role/configuration problem.

## Verdict

NO-GO.

The design direction is important, but this proposal still cannot receive GO as
an implementation proposal. It fails the required applicability gate and it
correctly admits that the governing requirement remains a deferred intake
candidate.

## Applicability Preflight

- preflight_passed: `false`
- missing_required_specs: `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- warnings.missing_parent_dirs: `[]`
- missing_advisory_specs:
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Clause Applicability

- Clauses evaluated: `5`
- must_apply: `3`
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps: `0`

The clause gate passes, but the applicability gate blocks GO.

## Evidence Reviewed

- `bridge/gtkb-cli-mediated-agent-mutation-boundary-001.md`
- `bridge/gtkb-cli-mediated-agent-mutation-boundary-002.md`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-cli-mediated-agent-mutation-boundary --content-file bridge\gtkb-cli-mediated-agent-mutation-boundary-002.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-cli-mediated-agent-mutation-boundary --content-file bridge\gtkb-cli-mediated-agent-mutation-boundary-002.md`
- `python -m groundtruth_kb.cli deliberations search "CLI mediated agent mutation boundary direct artifact mutation skills CLI" --json`

## Findings

The proposal is right to separate the design constraint from immediate no-index
cleanup. However, it targets broad project, skill, rule, template, script, and
test surfaces while omitting `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, which
the applicability preflight flags as required.

It also states that `INTAKE-f8bc08a3` remains deferred and not yet confirmed as
a formal governing spec. That means the broad "agents may mutate only through
skills or direct CLI access" rule should be promoted or otherwise formalized
before implementation changes are approved.

## Required Revision

File a REVISED proposal that:

- Adds `ADR-ISOLATION-APPLICATION-PLACEMENT-001` to Specification Links.
- Either confirms `INTAKE-f8bc08a3` into a formal governing requirement before
  implementation approval, or narrows the proposal to advisory design guidance
  that does not mutate source/config/test surfaces.
- Distinguishes ordinary GT-KB operation from reviewed platform implementation
  work so emergency/platform repairs are not accidentally blocked before CLI
  coverage exists.
- Keeps the no-index cleanup slices moving; do not bundle every CLI migration
  into WI-4578.
