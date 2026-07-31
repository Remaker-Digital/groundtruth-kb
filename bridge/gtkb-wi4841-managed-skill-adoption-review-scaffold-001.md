NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution

# Implementation Proposal - Skill: managed-skill-adoption-review — structural review for managed-artifact proposals

bridge_kind: prime_proposal
Document: gtkb-wi4841-managed-skill-adoption-review-scaffold
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Work Item: WI-4841

target_paths: [".claude/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_managed_skill_adoption_review_skill.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-4841 adds a managed-skill-adoption-review skill for structural review of managed-artifact proposals.

Work item description: Specialized structural review for skill/template/adopter managed-artifact proposals. Advisory opportunity #8 (token savings medium). Motivated by repeated NO-GOs around managed-artifact registry authority, target_paths omission, and stale Tier A registry assumptions (e.g., the gtkb-tier-a-managed-skill-adoption-apply thread). Recommended after skill-governance-lifecycle. Consideration candidate, not implementation-approved.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4841` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The older work-item description says this was a consideration candidate, but the later owner decision DELIB-20266596 and active PAUTH PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842 supersede that authority state for bounded implementation-proposal filing. The proposal remains limited to a scaffolded review skill and its registry/adapter/test evidence.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/skills/managed-skill-adoption-review/SKILL.md`, `.codex/skills/managed-skill-adoption-review/SKILL.md`, `.codex/skills/MANIFEST.json`, `config/agent-control/harness-capability-registry.toml`, `platform_tests/skills/test_managed_skill_adoption_review_skill.py`.

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
- Prior managed-artifact review context: repeated bridge NO-GOs around managed-artifact registry authority, target_paths omission, and stale Tier A registry assumptions are cited in the WI-4841 work item and must be represented in implementation evidence.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842` - active project authorization covering `WI-4841`.


## Cross-Harness Disposition

- Claude Code: canonical skill source is `.claude/skills/managed-skill-adoption-review/SKILL.md`; implementation must keep this as the authoritative managed-skill body.
- Codex: `.codex/skills/managed-skill-adoption-review/SKILL.md` and `.codex/skills/MANIFEST.json` are generated/projection surfaces; implementation must regenerate them through `scripts/generate_codex_skill_adapters.py --update-registry` and verify load/catalog tests.
- Antigravity, Cursor, API harnesses: no direct skill adapter target is in this WI-4841 proposal. Their behavior is unchanged by this slice; any future projection to additional harness skill directories requires a separate target-path-covered proposal or typed parity waiver.
- Parity evidence required in the implementation report: canonical/adapted skill body equivalence, registry declaration, Codex manifest entry, managed-artifact review checklist coverage, and focused no-orphan/load-smoke tests.
## Proposed Scope

- Add a managed-skill-adoption-review skill for structural review of skill/template/adopter managed-artifact proposals.
- Encode checks for managed-artifact registry authority, target_paths coverage, adapter/projection expectations, stale registry assumptions, and review evidence.
- Project the canonical skill to Codex through the adapter generator and declare it in the harness capability registry and Codex manifest.
- Sequence implementation to use the WI-4839 skill-governance-lifecycle scaffold recipe when available; if WI-4839 is not yet VERIFIED, implementation must preserve equivalent scaffold evidence inline.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run normal bridge proposal/report lifecycle; do not mutate protected skill/config/test files until LO GO and implementation-start packet. |
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
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run platform_tests/skills/test_skill_catalog_contract.py plus the new managed-skill-adoption-review skill test. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842 is cited and the implementation remains within WI-4841 target paths. |
| `ADR-CROSS-HARNESS-PARITY-001` | Verify canonical Claude skill and generated Codex adapter remain behaviorally equivalent; document non-target harness disposition. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Include Cross-Harness Disposition and run adapter/catalog checks before VERIFIED. |

## Acceptance Criteria

- The managed-skill-adoption-review skill exists as a canonical managed skill with generated Codex adapter and manifest/registry declarations.
- The skill provides deterministic structural review checks for managed skill/template/adopter proposals, including target_paths and registry/projection authority.
- Focused tests prove registry/adapter/catalog invariants and representative review checklist content for managed-artifact proposal risks.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/skills/managed-skill-adoption-review/SKILL.md`
- `.codex/skills/managed-skill-adoption-review/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`
- `platform_tests/skills/test_managed_skill_adoption_review_skill.py`

## Recommended Commit Type

`feat`