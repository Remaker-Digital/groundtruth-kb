NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution

# Implementation Proposal - Skill: formal-artifact-packet-helper — generate/validate formal-artifact approval packets

bridge_kind: prime_proposal
Document: gtkb-wi4842-formal-artifact-packet-helper-scaffold
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Work Item: WI-4842

target_paths: [".claude/skills/formal-artifact-packet-helper/SKILL.md", ".codex/skills/formal-artifact-packet-helper/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_formal_artifact_packet_helper_skill.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-4842 adds a formal-artifact-packet-helper skill for governed approval packet generation and validation.

Work item description: Generate and validate formal-artifact approval packets with stable LF normalization and the expected required fields. Advisory opportunity #9 (token savings medium). Related to open WI-3279 and recurring approval-packet salience gaps in bridge history — coordinate scope with WI-3279. Recommended after skill-governance-lifecycle. Consideration candidate, not implementation-approved.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4842` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The older work-item description says this was a consideration candidate, but the later owner decision DELIB-20266596 and active PAUTH PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842 supersede that authority state for bounded implementation-proposal filing. The proposal remains limited to a scaffolded helper skill and must reuse existing formal-artifact packet validation authority rather than creating a second packet source of truth.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/skills/formal-artifact-packet-helper/SKILL.md`, `.codex/skills/formal-artifact-packet-helper/SKILL.md`, `.codex/skills/MANIFEST.json`, `config/agent-control/harness-capability-registry.toml`, `platform_tests/skills/test_formal_artifact_packet_helper_skill.py`.

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
- Existing packet tooling context: scripts/validate_formal_artifact_packet.py and formal-artifact approval gate tests are existing authority surfaces that this skill must reference instead of replacing.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842` - active project authorization covering `WI-4842`.


## Cross-Harness Disposition

- Claude Code: canonical skill source is `.claude/skills/formal-artifact-packet-helper/SKILL.md`; implementation must keep this as the authoritative managed-skill body.
- Codex: `.codex/skills/formal-artifact-packet-helper/SKILL.md` and `.codex/skills/MANIFEST.json` are generated/projection surfaces; implementation must regenerate them through `scripts/generate_codex_skill_adapters.py --update-registry` and verify load/catalog tests.
- Antigravity, Cursor, API harnesses: no direct skill adapter target is in this WI-4842 proposal. Their behavior is unchanged by this slice; any future projection to additional harness skill directories requires a separate target-path-covered proposal or typed parity waiver.
- Parity evidence required in the implementation report: canonical/adapted skill body equivalence, registry declaration, Codex manifest entry, existing formal-artifact packet validation linkage, and focused no-orphan/load-smoke tests.
## Proposed Scope

- Add a formal-artifact-packet-helper skill that generates and validates formal-artifact approval packet structure with stable LF normalization and required fields.
- Coordinate scope with existing formal-artifact packet validation tooling rather than introducing a second packet authority.
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
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run platform_tests/skills/test_skill_catalog_contract.py plus the new formal-artifact-packet-helper skill test. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842 is cited and the implementation remains within WI-4842 target paths. |
| `ADR-CROSS-HARNESS-PARITY-001` | Verify canonical Claude skill and generated Codex adapter remain behaviorally equivalent; document non-target harness disposition. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Include Cross-Harness Disposition and run adapter/catalog checks before VERIFIED. |

## Acceptance Criteria

- The formal-artifact-packet-helper skill exists as a canonical managed skill with generated Codex adapter and manifest/registry declarations.
- The skill routes users to existing packet validation/generation scripts and defines required packet fields, LF normalization, approval evidence, and non-bypass constraints.
- Focused tests prove registry/adapter/catalog invariants and that the skill references existing formal-artifact packet validation surfaces.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/skills/formal-artifact-packet-helper/SKILL.md`
- `.codex/skills/formal-artifact-packet-helper/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`
- `platform_tests/skills/test_formal_artifact_packet_helper_skill.py`

## Recommended Commit Type

`feat`