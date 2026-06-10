REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-INTAKE-LO-ADVISORY-INTAKE-PARALLEL-BATCH
Project: PROJECT-GTKB-LO-ADVISORY-INTAKE
Work Item: WI-3303

# Implementation Proposal - LO Hygiene Assessment Skill Build

bridge_kind: prime_proposal
Document: gtkb-lo-hygiene-assessment-skill-build
Version: 002 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Source: `bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-002.md` GO and WI-3303 disposition routing
Recommended commit type: `feat:`
target_paths: [".claude/skills/loyal-opposition-hygiene-assessment/SKILL.md", "config/agent-control/harness-capability-registry.toml", ".codex/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".codex/skills/MANIFEST.json", ".groundtruth/formal-artifact-approvals/*loyal-opposition-hygiene-assessment*.json", "bridge/gtkb-lo-hygiene-assessment-skill-build-*.md"]

## Revision Summary

Author correction after preflight: `bridge/gtkb-lo-hygiene-assessment-skill-build-001.md` passed applicability preflight but failed `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-hygiene-assessment-skill-build` because the verification section did not include the detector-recognized `Specification-Derived Verification` or `spec-to-test` evidence phrase. This revision changes only that proposal evidence surface; implementation scope, target paths, acceptance criteria, owner-decision posture, and risk/rollback remain unchanged.

## Summary

Implement v1 of the `loyal-opposition-hygiene-assessment` skill as a manual Loyal Opposition advisory orchestration capability. The skill will synthesize existing hygiene surfaces into a Prime-facing action plan without giving Loyal Opposition routine mutation authority.

This proposal implements the build thread routed by `gtkb-lo-hygiene-assessment-skill-advisory-disposition`: the disposition classified the source advisory as `adapt`, preserved the narrower v1 scope, and kept this build separately reviewable. This proposal does not implement startup-pulse reporting, scheduling, command-surface aliases, or parity-class promotion.

## Scope

In scope:

- Add canonical skill source at `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md`.
- Add a capability-registry entry `skill.loyal-opposition-hygiene-assessment` with `required_for_roles = ["loyal-opposition"]` and initial `parity_class = "baseline"`.
- Generate the Codex adapter through `python scripts/generate_codex_skill_adapters.py --update-registry`.
- Preserve the advisory's v1 mode boundary: manual `overview` and `phase <id>` modes only.
- Define the nine hygiene phases, required read surfaces, report shape, ownership classes, and out-of-scope mutation guardrails in the skill body.
- Verify adapter freshness and harness parity.

Out of scope:

- No `verify <report-or-phase>` mode in v1.
- No `startup-pulse` mode in v1.
- No `::hygiene` command, `gt hygiene scan` CLI, scheduler, cron/automation, dashboard, or startup wiring.
- No promotion of `parity_class` from `baseline` to `required`.
- No deletion, merge, retirement, branch cleanup, broad rename, bridge-status mutation, or formal artifact mutation by the new skill itself.
- No application code under `applications/`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/peer-solution-advisory-loop.md`
- `.claude/rules/project-root-boundary.md`

## Project Authorization Evidence

- Project Authorization: `PAUTH-PROJECT-GTKB-LO-ADVISORY-INTAKE-LO-ADVISORY-INTAKE-PARALLEL-BATCH`
- Project: `PROJECT-GTKB-LO-ADVISORY-INTAKE`
- Work Item: `WI-3303`
- Owner decision evidence: `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`
- Included work item evidence: active authorization includes `WI-3303`.
- Included spec evidence: active authorization includes `GOV-FILE-BRIDGE-AUTHORITY-001` and `GOV-ARTIFACT-APPROVAL-001`.

This project authorization does not bypass the bridge. Implementation still requires Loyal Opposition GO, `scripts/implementation_authorization.py begin`, bounded target paths, implementation evidence, and a post-implementation report.

## Prior Deliberations

- `DELIB-1473` - "Loyal Opposition Advisory: LO Hygiene Assessment Skill"; the source advisory for WI-3303 and this build.
- `bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-001.md` - Prime `adapt` disposition proposal.
- `bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-002.md` - Loyal Opposition GO authorizing disposition closure and this follow-on proposal.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-approved project authorization evidence for the LO advisory intake batch.
- `DELIB-1470` - peer-solution advisory-loop family context.
- `DELIB-1478` - Prime advisory-loop bridge/disposition context.
- `DELIB-2077` - precedent for preserving peer-loop classification text while using the live Deliberation Archive schema vocabulary.

## Implementation Plan

1. Author `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md`.
   - Use the advisory's recommended name and description.
   - State read-only default behavior and explicit Loyal Opposition advisory boundary.
   - Define `overview` and `phase <id>` modes only for v1.
   - Include the nine-phase hygiene registry from `DELIB-1473`.
   - Require reports to include claim, scope, evidence, severity, hygiene phase, Prime implementation sequence, peer-Prime candidates, LO verification plan, do-not-touch/deferred areas, blocking owner decisions, and residual risk.

2. Add `skill.loyal-opposition-hygiene-assessment` to `config/agent-control/harness-capability-registry.toml`.
   - `canonical_source = ".claude/skills/loyal-opposition-hygiene-assessment/SKILL.md"`.
   - `required_for_roles = ["loyal-opposition"]`.
   - `parity_class = "baseline"`.
   - Codex adapter surface: `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md`.

3. Run `python scripts/generate_codex_skill_adapters.py --update-registry` and keep generated adapter/manifest changes.

4. Run verification commands listed below.

5. File an implementation report for Loyal Opposition verification.

## Formal Artifact Approval Plan

If the implementation touches a protected formal or narrative artifact surface that the approval gates require to be packet-backed, Prime Builder must create the corresponding formal-artifact approval packet during implementation and cite it in the report. Expected candidate: the capability registry entry, if governed by the active artifact approval gates. The canonical skill source and generated adapter must still flow through bridge implementation authorization and adapter parity checks even if no separate approval packet is required for them.

## Specification-Derived Verification Plan

Explicit spec-to-test mapping:

| Requirement | Verification evidence |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This proposal and the eventual report are filed under `bridge/` and indexed in live `bridge/INDEX.md`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal header cites `Project Authorization`, `Project`, and `Work Item` lines. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Active authorization readback shows `WI-3303` and the implementation waits for LO GO plus implementation-start authorization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Report must map verification commands to the requirements in this table. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched paths stay under `E:\GT-KB`; no `applications/` path is modified. |
| `.claude/rules/loyal-opposition.md` | Skill text preserves read-only advisory behavior and separates Prime action from LO verification. |
| `.claude/rules/peer-solution-advisory-loop.md` | Build follows the `adapt` disposition: core pattern accepted, v1 surface narrowed. |
| `GOV-ARTIFACT-APPROVAL-001` | Any approval-gated registry/formal artifact mutation includes a packet and report evidence. |

Required verification commands:

```text
python scripts/generate_codex_skill_adapters.py --update-registry --check
python scripts/check_harness_parity.py --all --markdown
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-hygiene-assessment-skill-build
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-hygiene-assessment-skill-build
rg -n "loyal-opposition-hygiene-assessment|skill.loyal-opposition-hygiene-assessment" .claude .codex config scripts platform_tests
```

Focused tests are optional if the implementation is limited to skill text plus registry/adapter projection, but the implementation report must explain why no Python source-test lane applies if no test files are changed.

## Acceptance Criteria

1. `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` exists and states manual `overview` plus `phase <id>` modes only.
2. The skill body includes the nine hygiene phases and report fields from `DELIB-1473`.
3. The skill body states that Loyal Opposition output is advisory/read-only by default and classifies actions as `prime-action`, `peer-prime-candidate`, or `lo-verification`.
4. The capability registry contains `skill.loyal-opposition-hygiene-assessment`, required for Loyal Opposition, with `parity_class = "baseline"`.
5. The generated Codex adapter exists and adapter freshness check passes.
6. Harness parity check passes or reports only unrelated pre-existing findings, which must be enumerated in the implementation report.
7. No startup, scheduler, command-surface, dashboard, application, or parity-class-promotion changes are included.
8. Any approval-gated artifact mutation is covered by a formal approval packet cited in the report.

## Risk and Rollback

Risk: the new orchestration skill duplicates narrower skills instead of orchestrating them. Mitigation: the skill must reference existing skills and scripts as inputs, not reimplement their logic.

Risk: the skill encourages Loyal Opposition mutation. Mitigation: make read-only/advisory behavior and out-of-scope actions explicit in the skill contract.

Risk: the adapter pipeline drifts. Mitigation: use the generator and verify with `--update-registry --check` plus harness parity.

Rollback: remove the registry entry, generated adapter, and canonical skill source in one revision if Loyal Opposition rejects the build. No data migration is required.

## Owner Decisions

No owner decision is required for this proposal. The owner-approved project authorization covers WI-3303 routing work, and this proposal waits for Loyal Opposition GO before implementation. Later startup-pulse, scheduling, command-surface, or parity-class-promotion work will need separate bridge review and any owner approval required by active governance.

End of proposal.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
