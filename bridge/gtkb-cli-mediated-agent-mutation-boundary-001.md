NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# CLI-Mediated Agent Mutation Boundary Proposal

bridge_kind: prime_proposal
Document: gtkb-cli-mediated-agent-mutation-boundary
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_*.py", "groundtruth-kb/src/groundtruth_kb/bridge*.py", "groundtruth-kb/src/groundtruth_kb/project/*.py", "scripts/*", ".claude/skills/**", ".codex/skills/**", ".agent/skills/**", ".api-harness/skills/**", ".claude/rules/**", "groundtruth-kb/templates/**", "config/agent-control/**", "platform_tests/**", "groundtruth-kb/tests/**", "bridge/gtkb-cli-mediated-agent-mutation-boundary-*.md"]

implementation_scope: cli_mediated_agent_mutation_boundary_design_constraint
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Mike added a design constraint during the no-index cleanup sweep:

> We want to avoid requiring any AI/agent to mutate GT-KB code in order to build and operate applications that rely on GT-KB, so all of our mutating change requirements must be captured by the CLI as our internal AI/agent system UI. That means we want the CLI to be underneath all of our skill implementations where it makes sense and we want to explicitly bar all agents from doing anything to GT-KB artifacts except via skills or direct access to the CLI.

This may not belong solely in the bridge-index-retirement umbrella, but it materially affects the cleanup design. The no-index work should not merely replace `bridge/INDEX.md` reads with better prose; it should move mutating bridge, dispatcher, project, spec, skill, and application-operation workflows toward deterministic CLI surfaces that skills call rather than asking agents to hand-edit GT-KB artifacts.

## Prior Deliberations

- `INTAKE-f8bc08a3` - Requirement candidate already captured as "Dispatcher/Bridge CLI as primary mutating UI for GT-KB artifact operations"; outcome is `deferred`, not yet confirmed as a formal spec.
- `DELIB-20263447` - Harness benchmark Dispatcher/Bridge CLI-first operation; relevant evidence that CLI-first behavior is already emerging as a benchmark/use-case requirement.
- `DELIB-20263438` - Owner requirement for corrected bridge-dispatch architecture; relevant because the dispatcher/config/status CLI work is the immediate context.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - Deterministic services principle: repetitive AI plumbing belongs in services, not ad hoc session work.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must still proceed through bridge GO and implementation-start authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge remains the governed lifecycle for implementation proposals, reports, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project/work authorization metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the governing requirements and identifies a new requirement candidate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any implementation must include spec-derived verification evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher/config/status/health CLI surfaces are the correct operation boundary for dispatch topology.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch routing uses declarative rule inputs rather than direct agent edits.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - cross-harness enforcement gaps remain relevant when barring raw artifact mutation across harnesses.

## Requirement Sufficiency

New or revised requirement required before implementation.

The owner statement is already captured as requirement candidate `INTAKE-f8bc08a3`, but it is still `outcome="deferred"` and has no confirmed `spec_id`. This proposal records the design constraint for the active no-index cleanup and asks Loyal Opposition to review the scope and sequencing. Source/config implementation should wait until either:

1. the candidate is confirmed into a formal governing spec, or
2. Loyal Opposition determines that existing specifications already cover the exact CLI-mediated mutation-boundary behavior and identifies those specifications.

## Proposed Design Constraint

Future GT-KB agent mutation design should prefer this hierarchy:

1. **CLI first:** mutating GT-KB operations are exposed as deterministic `gt ...` commands with validation, authorization checks, audit metadata, and machine-readable output.
2. **Skills as wrappers:** skills call the CLI where practical, adding routing/context but not becoming independent mutation implementations.
3. **Direct source/file edits only for platform implementation work:** agents may still edit GT-KB code through reviewed bridge proposals when the task is to build or repair the platform itself, but ordinary use of GT-KB to build/operate adopter applications should not require modifying GT-KB code.
4. **Artifact mutation boundary:** agents should be barred from mutating GT-KB artifacts except through governed skills or direct CLI access. Raw file/database edits should be treated as implementation work needing a specific bridge proposal, not as normal operation.

## Impact On Active No-Index Cleanup

The existing no-index cleanup proposals should account for this constraint:

- `gtkb-no-index-runtime-tooling-cleanout` should prefer shared CLI/resolver services over one-off script rewrites.
- `gtkb-no-index-skill-template-doc-cleanout` should make skills point to CLI-backed operations where available.
- `gtkb-no-index-startup-control-cleanout` should avoid telling agents to inspect or mutate internal files directly when a CLI status surface exists.
- `gtkb-no-index-lo-harness-prompt-cleanout` should route LO harnesses toward CLI/status commands and versioned bridge artifacts instead of direct artifact manipulation.
- `gtkb-no-index-dispatcher-trigger-cleanout` should preserve dispatcher operation behind stable CLI/config/rule APIs rather than agent prompt conventions.

## Spec-Derived Verification Plan

For this proposal review:

```powershell
gt deliberations get INTAKE-f8bc08a3 --json
gt bridge dispatch config
gt bridge dispatch status --json
rg -n "direct edit|hand-edit|mutate.*artifact|CLI|gt " .claude\skills .codex\skills .claude\rules groundtruth-kb\templates config\agent-control groundtruth-kb\src\groundtruth_kb
```

Expected review conclusions:

- Loyal Opposition confirms whether `INTAKE-f8bc08a3` is sufficient pending requirement evidence or whether a formal spec must be confirmed before implementation.
- Active no-index cleanup proposals are either accepted as compatible with CLI-first design or revised to narrow/remove raw artifact mutation assumptions.
- Any eventual implementation includes tests that show skills invoke or document CLI-backed mutation paths where such CLI paths exist.

## Risks

- This requirement is broader than the no-index cleanup and could become an umbrella project of its own. Overloading WI-4578 with every CLI migration would make the current bridge cleanup unfinishable.
- Barring direct artifact mutation too aggressively before CLI coverage exists could block platform repair work. The boundary should distinguish ordinary GT-KB operation from reviewed platform implementation.
- Some skills currently wrap Python helpers directly. Converting them all to CLI-backed surfaces should be sequenced, not bundled into a single cleanup patch.

## Rollback

This proposal is non-implementing unless and until it receives GO and an implementation-start packet. Rolling it back means superseding it with a revised proposal or rejecting it by NO-GO; do not delete the bridge file.
