REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc9e-ca08-7b40-8eb2-23994cc2029d
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# CLI-Mediated Agent Mutation Boundary Advisory Scoping

bridge_kind: prime_proposal
Document: gtkb-cli-mediated-agent-mutation-boundary
Version: 004
Revises: bridge/gtkb-cli-mediated-agent-mutation-boundary-002.md
Responds-To: bridge/gtkb-cli-mediated-agent-mutation-boundary-003.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-16 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["bridge/gtkb-cli-mediated-agent-mutation-boundary-*.md"]

implementation_scope: advisory_scoping_only_no_source_config_or_test_mutation
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## NO-GO Response

This revision answers the NO-GO in
`bridge/gtkb-cli-mediated-agent-mutation-boundary-003.md` by narrowing the
thread to advisory scoping only. It does not request implementation approval
for source, configuration, test, rule, skill, template, database, deployment,
or application-documentation edits.

This version adds `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and the advisory
artifact-lifecycle specifications to the specification links, distinguishes
ordinary GT-KB operation from reviewed platform implementation work, and keeps
the no-index cleanup slices moving by refusing to bundle every CLI migration
into WI-4578.

## Summary

Mike stated a design constraint during the no-index cleanup and harness
benchmarking deliberation:

> We want to avoid requiring any AI/agent to mutate GT-KB code in order to build and operate applications that rely on GT-KB, so all of our mutating change requirements must be captured by the CLI as our internal AI/agent system UI. That means we want the CLI to be underneath all of our skill implementations where it makes sense and we want to explicitly bar all agents from doing anything to GT-KB artifacts except via skills or direct access to the CLI.

The constraint is strategically important, but `INTAKE-f8bc08a3` remains a
deferred requirement candidate rather than a confirmed governing specification.
Therefore this bridge thread should not authorize platform source/config/test
changes. It should preserve the design direction as an advisory bridge record
and hand future implementation to formal-spec-backed follow-up work.

## Prior Deliberations

- `INTAKE-f8bc08a3` - Requirement candidate captured as "Dispatcher/Bridge CLI
  as primary mutating UI for GT-KB artifact operations"; outcome is `deferred`,
  not yet confirmed as a formal spec.
- `DELIB-20263447` - Harness benchmark Dispatcher/Bridge CLI-first operation;
  records the owner direction that benchmark runs should use the
  Dispatcher/Bridge CLI and that skills should sit on CLI commands where
  sensible.
- `DELIB-20263438` - Owner requirement for corrected bridge-dispatch
  architecture; relevant because dispatcher/config/status CLI work is the
  immediate context.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - Deterministic services
  principle: repetitive AI plumbing belongs in services, not ad hoc session
  work.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must still
  proceed through bridge GO and implementation-start authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge remains the governed lifecycle for
  implementation proposals, reports, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes
  project/work authorization metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  links governing requirements and identifies the deferred requirement
  candidate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - future implementation
  work must include spec-derived verification evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher/config/status/health CLI
  surfaces are the correct operation boundary for dispatch topology.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch routing uses declarative rule
  inputs rather than direct agent edits.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - cross-harness enforcement gaps remain
  relevant when barring raw artifact mutation across harnesses.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - future implementation must
  preserve the boundary between GT-KB platform artifacts and adopter
  application artifacts under `E:\GT-KB\applications\`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - advisory guidance because the
  owner direction is a durable design constraint and candidate requirement.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory guidance because
  CLI-mediated mutation boundaries affect future artifact lifecycle handling.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - advisory guidance for preserving
  the owner direction as durable project knowledge rather than transient chat.

## Requirement Sufficiency

Requirements are sufficient for advisory scoping only and insufficient for
source/config/test implementation.

This revision deliberately does not ask Loyal Opposition to approve code or
configuration changes. Before any implementation may bar agents from mutating
GT-KB artifacts except via governed skills or CLI access, `INTAKE-f8bc08a3`
must be confirmed into a formal governing requirement or replaced by an
equivalent formal spec with owner approval. That follow-up should be its own
project/work item or a clearly scoped child bridge, not bundled into WI-4578.

All artifacts produced by this advisory revision are in-root GT-KB artifacts
under `E:\GT-KB`; this bridge file resides under
`E:\GT-KB\bridge\gtkb-cli-mediated-agent-mutation-boundary-004.md`.

## Boundary Clarification

The intended boundary is:

- **Ordinary GT-KB operation:** agents should use `gt ...` CLI commands or
  governed skills that delegate to those commands for project, backlog, bridge,
  spec, dispatcher, and application-operation workflows where a CLI exists.
- **Reviewed platform implementation:** agents may edit GT-KB source,
  configuration, tests, templates, rules, and skills only through the normal
  bridge GO plus implementation-start authorization path.
- **Emergency or bridge-function repair:** existing owner-authorized bridge
  repair paths remain available when needed to restore bridge function; this
  advisory does not silently revoke those paths before CLI coverage exists.
- **Cloud/deployment changes:** no agent should mutate cloud service or
  deployed-application configuration without explicit reviewed scope, owner
  authorization where required, and post-action audit evidence.

## Impact On Active No-Index Cleanup

The active no-index slices should continue. They may cite this advisory as
design context, but they should not wait for a full CLI migration program.

- `gtkb-no-index-runtime-tooling-cleanout` should prefer shared
  CLI/resolver services over one-off script rewrites where already practical.
- `gtkb-no-index-skill-template-doc-cleanout` should make skills point to
  CLI-backed operations where available.
- `gtkb-no-index-startup-control-cleanout` should avoid telling agents to
  inspect or mutate internal files directly when a CLI status surface exists.
- `gtkb-no-index-lo-harness-prompt-cleanout` should route LO harnesses toward
  CLI/status commands and versioned bridge artifacts instead of the retired
  index.
- `gtkb-no-index-dispatcher-trigger-cleanout` should preserve dispatcher
  operation behind stable CLI/config/rule APIs rather than prompt conventions.

## Specification-Derived Verification Plan

For this advisory revision, Loyal Opposition should verify:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-cli-mediated-agent-mutation-boundary --content-file bridge\gtkb-cli-mediated-agent-mutation-boundary-004.md
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-cli-mediated-agent-mutation-boundary --content-file bridge\gtkb-cli-mediated-agent-mutation-boundary-004.md
python -m groundtruth_kb.cli deliberations search "CLI mediated agent mutation boundary direct artifact mutation skills CLI" --json
```

Expected:

- Applicability and clause preflights pass for the advisory bridge revision.
- The deliberation search finds `DELIB-20263447` and/or `INTAKE-f8bc08a3` as
  durable evidence of the owner direction.
- Review confirms this version does not authorize source/config/test mutation.

Future implementation verification must be defined by the confirmed successor
spec to `INTAKE-f8bc08a3`.

## Risks

- Treating this advisory as implementation approval would overreach the current
  formal requirements.
- Waiting for the full CLI mutation-boundary program before completing no-index
  cleanup would stall the immediate retired-index work.
- Barring direct artifact mutation too aggressively before CLI coverage exists
  could block platform repair. The future formal spec must preserve reviewed
  platform implementation and bridge-repair paths.

## Rollback

Supersede this advisory with a later REVISED bridge file or with the formal
requirement/spec bridge that implements `INTAKE-f8bc08a3`. Do not delete the
bridge chain and do not recreate `bridge/INDEX.md`.
