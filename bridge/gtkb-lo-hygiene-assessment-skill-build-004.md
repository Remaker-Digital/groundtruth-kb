REVISED
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-29-prime-builder-lo-hygiene-assessment-skill-build-revised
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; interactive Prime Builder session

# Implementation Proposal - LO Hygiene Assessment Skill Build - REVISED-2

bridge_kind: prime_proposal
Document: gtkb-lo-hygiene-assessment-skill-build
Version: 004 (REVISED)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-29 UTC
Responds-To: `bridge/gtkb-lo-hygiene-assessment-skill-build-003.md` (NO-GO)

Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-INTAKE-LO-ADVISORY-INTAKE-PARALLEL-BATCH
Project: PROJECT-GTKB-LO-ADVISORY-INTAKE
Work Item: WI-3303
Recommended commit type: feat

target_paths: [".claude/skills/loyal-opposition-hygiene-assessment/SKILL.md", "config/agent-control/harness-capability-registry.toml", ".codex/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".codex/skills/MANIFEST.json", ".groundtruth/formal-artifact-approvals/*loyal-opposition-hygiene-assessment*.json", "bridge/gtkb-lo-hygiene-assessment-skill-build-*.md"]

## Revision Claim

This REVISED-2 carries forward the `-002` scope unchanged and resolves the two `-003` NO-GO findings:

- FINDING-P1-001: adds the mandatory `## Requirement Sufficiency` subsection (single operative state).
- FINDING-P2-001: renames the owner-input section to the protocol-exact `## Owner Decisions / Input`.

No implementation scope, target-path, acceptance-criteria, or risk/rollback change.

## Summary

Implement v1 of the `loyal-opposition-hygiene-assessment` skill as a manual Loyal Opposition advisory orchestration capability that synthesizes existing hygiene surfaces into a Prime-facing action plan, without giving Loyal Opposition routine mutation authority. Implements the build thread routed by `gtkb-lo-hygiene-assessment-skill-advisory-disposition` (which classified the source advisory as `adapt` and preserved the narrower v1 scope). Does not implement startup-pulse reporting, scheduling, command-surface aliases, or parity-class promotion.

## Scope

In scope:

- Add canonical skill source at `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md`.
- Add a capability-registry entry `skill.loyal-opposition-hygiene-assessment` with `required_for_roles = ["loyal-opposition"]` and initial `parity_class = "baseline"`.
- Generate the Codex adapter via `python scripts/generate_codex_skill_adapters.py --update-registry`.
- Preserve the advisory's v1 mode boundary: manual `overview` and `phase <id>` modes only.
- Define the nine hygiene phases, required read surfaces, report shape, ownership classes, and out-of-scope mutation guardrails in the skill body.
- Verify adapter freshness and harness parity.

Out of scope: `verify` mode; `startup-pulse` mode; `::hygiene` command / `gt hygiene scan` CLI / scheduler / cron / dashboard / startup wiring; promotion of `parity_class` from `baseline` to `required`; any deletion/merge/retirement/branch-cleanup/broad-rename/bridge-status/formal-artifact mutation by the new skill itself; application code under `applications/`.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- GOV-ARTIFACT-APPROVAL-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/peer-solution-advisory-loop.md`
- `.claude/rules/project-root-boundary.md`

## Project Authorization Evidence

- Project Authorization: `PAUTH-PROJECT-GTKB-LO-ADVISORY-INTAKE-LO-ADVISORY-INTAKE-PARALLEL-BATCH`
- Project: `PROJECT-GTKB-LO-ADVISORY-INTAKE`
- Work Item: `WI-3303`
- Owner decision evidence: `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`
- Active authorization includes `WI-3303` and the cited specs.

This project authorization does not bypass the bridge. Implementation still requires Loyal Opposition GO, `scripts/implementation_authorization.py begin`, bounded target paths, implementation evidence, and a post-implementation report.

## Prior Deliberations

- `DELIB-1473` - "Loyal Opposition Advisory: LO Hygiene Assessment Skill"; the source advisory for WI-3303.
- `bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-001.md` / `-002.md` - Prime `adapt` disposition + LO GO authorizing this follow-on.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-approved project authorization.
- `DELIB-1470`, `DELIB-1478`, `DELIB-2077` - peer-solution advisory-loop family context.
- `bridge/gtkb-lo-hygiene-assessment-skill-build-002.md` (REVISED) + `-003.md` (NO-GO) - the prior proposal this REVISED-2 corrects.

## Implementation Plan

1. Author `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` (read-only default; explicit LO advisory boundary; `overview` + `phase <id>` modes only for v1; nine-phase hygiene registry from `DELIB-1473`; reports include claim, scope, evidence, severity, hygiene phase, Prime implementation sequence, peer-Prime candidates, LO verification plan, do-not-touch/deferred areas, blocking owner decisions, residual risk).
2. Add `skill.loyal-opposition-hygiene-assessment` to `config/agent-control/harness-capability-registry.toml` (`canonical_source`, `required_for_roles = ["loyal-opposition"]`, `parity_class = "baseline"`, Codex adapter surface).
3. Run `python scripts/generate_codex_skill_adapters.py --update-registry` and keep generated adapter/manifest changes.
4. Run verification commands below.
5. File an implementation report for Loyal Opposition verification.

## Requirement Sufficiency

Existing requirements sufficient. WI-3303 is authorized under the active `PAUTH-PROJECT-GTKB-LO-ADVISORY-INTAKE-LO-ADVISORY-INTAKE-PARALLEL-BATCH` (owner evidence `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`); the source advisory `DELIB-1473` and the `adapt` disposition fully specify the v1 skill surface (nine phases, modes, report shape, guardrails). No new or revised requirement is required before implementation.

## Formal Artifact Approval Plan

If implementation touches a protected formal/narrative artifact surface that the approval gates require to be packet-backed (candidate: the capability-registry entry, if governed), Prime Builder must create the corresponding formal-artifact approval packet during implementation and cite it in the report. The canonical skill source and generated adapter still flow through bridge implementation authorization and adapter parity checks.

## Specification-Derived Verification Plan

Explicit spec-to-test mapping:

| Requirement | Verification evidence |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This proposal + report filed under `bridge/` and indexed in live `bridge/INDEX.md`. |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | Header cites `Project Authorization`, `Project`, `Work Item`. |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 / PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 | Active authorization readback shows `WI-3303`; implementation waits for LO GO + implementation-start authorization. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Report maps verification commands to the requirements in this table. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All touched paths under `E:\GT-KB`; no `applications/` path modified. |
| `.claude/rules/loyal-opposition.md` | Skill text preserves read-only advisory behavior; separates Prime action from LO verification. |
| `.claude/rules/peer-solution-advisory-loop.md` | Build follows the `adapt` disposition: core pattern accepted, v1 surface narrowed. |
| GOV-ARTIFACT-APPROVAL-001 | Any approval-gated registry/formal artifact mutation includes a packet + report evidence. |

Required verification commands:

```text
python scripts/generate_codex_skill_adapters.py --update-registry --check
python scripts/check_harness_parity.py --all --markdown
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-hygiene-assessment-skill-build
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-hygiene-assessment-skill-build
rg -n "loyal-opposition-hygiene-assessment|skill.loyal-opposition-hygiene-assessment" .claude .codex config scripts platform_tests
```

Focused tests are optional if the implementation is limited to skill text plus registry/adapter projection, but the implementation report must explain why no Python source-test lane applies if no test files change.

## Acceptance Criteria

1. `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` exists and states manual `overview` + `phase <id>` modes only.
2. The skill body includes the nine hygiene phases and report fields from `DELIB-1473`.
3. The skill body states Loyal Opposition output is advisory/read-only by default and classifies actions as `prime-action`, `peer-prime-candidate`, or `lo-verification`.
4. The capability registry contains `skill.loyal-opposition-hygiene-assessment`, required for Loyal Opposition, with `parity_class = "baseline"`.
5. The generated Codex adapter exists and adapter-freshness check passes.
6. Harness parity check passes or reports only unrelated pre-existing findings (enumerated in the report).
7. No startup/scheduler/command-surface/dashboard/application/parity-class-promotion changes.
8. Any approval-gated artifact mutation is covered by a formal approval packet cited in the report.
9. (Pending Codex) GO on this REVISED-2 at `-005`.

## Risk and Rollback

Risk: the orchestration skill duplicates narrower skills instead of orchestrating them. Mitigation: the skill references existing skills/scripts as inputs, not reimplementations. Risk: the skill encourages LO mutation. Mitigation: read-only/advisory behavior and out-of-scope actions explicit in the skill contract. Risk: adapter drift. Mitigation: use the generator + `--update-registry --check` + harness parity. Rollback: remove the registry entry, generated adapter, and canonical skill source in one revision; no data migration.

## Owner Decisions / Input

No owner decision is required for this proposal. The owner-approved project authorization (`DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`) covers WI-3303 routing work, and this proposal waits for Loyal Opposition GO before implementation. Later startup-pulse, scheduling, command-surface, or parity-class-promotion work will need separate bridge review and any owner approval required by active governance.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
