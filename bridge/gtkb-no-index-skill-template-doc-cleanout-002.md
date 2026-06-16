NO-GO

author_identity: loyal-opposition/codex-special-owner-authorized
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop special owner-authorized Loyal Opposition review

# Loyal Opposition Review - No-Index Skill, Template, And Documentation Cleanout

bridge_kind: loyal_opposition_review
Document: gtkb-no-index-skill-template-doc-cleanout
Version: 002
Reviewed Proposal: bridge/gtkb-no-index-skill-template-doc-cleanout-001.md
Verdict: NO-GO
Date: 2026-06-16 America/Los_Angeles

## Special Owner Authorization

This review is filed from Codex harness A under the owner's one-time
authorization to review corrections that restore Loyal Opposition to a good
state despite the current Codex role/configuration problem.

## Verdict

NO-GO.

The proposal is directionally correct, but it fails the required applicability
preflight because it touches application documentation without citing the
application-placement/root-boundary architecture decision.

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

- `bridge/gtkb-no-index-skill-template-doc-cleanout-001.md`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-no-index-skill-template-doc-cleanout --content-file bridge\gtkb-no-index-skill-template-doc-cleanout-001.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-no-index-skill-template-doc-cleanout --content-file bridge\gtkb-no-index-skill-template-doc-cleanout-001.md`

## Required Revision

File a REVISED proposal that:

- Adds `ADR-ISOLATION-APPLICATION-PLACEMENT-001` to Specification Links and
  explains why `applications/Agent_Red/docs/gtkb-systems-and-tools.md` is in
  scope.
- Keeps the no-index direction: do not restore or require `bridge/INDEX.md`.
- Clarifies sequencing with the already-approved dispatcher-trigger and runtime
  tooling cleanup so bridge skill/helper edits do not conflict.
- Preserves generated-adapter discipline: canonical `.claude` skill sources
  first, generated Codex/agent/API adapters through the established generator.
