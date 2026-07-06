NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution

# Implementation Proposal - Skill: skill-governance-lifecycle — standardize new-skill scaffold

bridge_kind: prime_proposal
Document: gtkb-wi4839-skill-governance-lifecycle-scaffold
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Work Item: WI-4839

target_paths: [".claude/skills/skill-governance-lifecycle/SKILL.md", ".codex/skills/skill-governance-lifecycle/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_skill_governance_lifecycle_skill.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-4839 implements the enabler skill scaffold that standardizes future GT-KB managed-skill creation and projection.

Work item description: Meta-scaffold that standardizes new-skill work end to end: canonical .claude skill, generated .codex adapter, manifest entry, registry entry, codex load-smoke test, structural test, parity commands, and bridge evidence. Advisory opportunity #4 (token savings medium/high). This is the ENABLER for the other three helper skills (advisory-disposition, managed-skill-adoption-review, formal-artifact-packet-helper) — recommended to build first so they follow a standard recipe. Consideration candidate, not implementation-approved; files its own prime_proposal + PAUTH + spec-derived tests when prioritized.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4839` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The older work-item description says this was a consideration candidate, but the later owner decision DELIB-20266596 and active PAUTH PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842 supersede that authority state for bounded implementation-proposal filing. The work item and active project authorization define the implementation boundary; no missing membership or PAUTH state is created by this proposal.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/skills/skill-governance-lifecycle/SKILL.md`, `.codex/skills/skill-governance-lifecycle/SKILL.md`, `.codex/skills/MANIFEST.json`, `config/agent-control/harness-capability-registry.toml`, `platform_tests/skills/test_skill_governance_lifecycle_skill.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- DELIB-20265883 - owner-directed creation of PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT and grooming of the WI-4815 helper bucket into scoped skill-helper work items.
- DELIB-20266596 - owner AUQ approval for the bounded WI-4839 through WI-4842 skill-scaffold implementation authorization.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842` - active project authorization covering `WI-4839`.


## Cross-Harness Disposition

- Claude Code: canonical skill source is `.claude/skills/skill-governance-lifecycle/SKILL.md`; implementation must keep this as the authoritative managed-skill body.
- Codex: `.codex/skills/skill-governance-lifecycle/SKILL.md` and `.codex/skills/MANIFEST.json` are generated/projection surfaces; implementation must regenerate them through `scripts/generate_codex_skill_adapters.py --update-registry` and verify load/catalog tests.
- Antigravity, Cursor, API harnesses: no direct skill adapter target is in this WI-4839 proposal. Their behavior is unchanged by this slice; any future projection to additional harness skill directories requires a separate target-path-covered proposal or typed parity waiver.
- Parity evidence required in the implementation report: canonical/adapted skill body equivalence, registry declaration, Codex manifest entry, and focused no-orphan/load-smoke tests.
## Proposed Scope

- Add a managed skill-governance-lifecycle scaffold skill under the canonical .claude skill tree and project it to Codex through the existing adapter generator.
- Declare the skill in the harness capability registry and Codex manifest so no SKILL.md-bearing project skill is orphaned.
- Document the standard lifecycle recipe for new GT-KB skills: canonical source, generated adapters, registry entry, load-smoke coverage, structural tests, parity checks, and bridge evidence.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge preflight and normal bridge proposal/report lifecycle before protected source/test mutation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal header includes Project Authorization, Project, and Work Item machine-readable lines. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run platform_tests/skills/test_skill_catalog_contract.py plus the new scaffold test to prove registry/adapter/catalog invariants. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842 is cited and the implementation remains within WI-4839 target paths. |
| `ADR-CROSS-HARNESS-PARITY-001` | Verify the canonical Claude skill and generated Codex adapter remain behaviorally equivalent, and document non-target harness disposition. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run adapter generation/check tests and include a Cross-Harness Disposition section before filing. |

## Acceptance Criteria

- Skill-governance-lifecycle exists as a canonical managed skill with a generated Codex adapter and manifest entry.
- The harness capability registry declares the new skill with canonical source and Codex surface metadata.
- Focused tests prove the scaffold shape, registry declaration, adapter generation, and no-orphan catalog contract.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/skills/skill-governance-lifecycle/SKILL.md`
- `.codex/skills/skill-governance-lifecycle/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`
- `platform_tests/skills/test_skill_governance_lifecycle_skill.py`

## Recommended Commit Type

`feat`