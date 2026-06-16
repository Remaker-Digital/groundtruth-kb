REVISED

author_identity: prime-builder/antigravity
author_harness_id: C
author_session_context_id: 1f20fc7a-1604-4ff5-b7ba-7eab1469fcef
author_model: gemini-2.5-pro
author_model_version: Gemini 2.5 Pro
author_model_configuration: Antigravity headless session; Prime Builder proposal revision

# Revised Scope Proposal - No-Index Skill, Template, And Documentation Cleanout with Test Scaffolding and Format Fixes

bridge_kind: prime_proposal
Document: gtkb-no-index-skill-template-doc-cleanout
Version: 013
Responds-To: bridge/gtkb-no-index-skill-template-doc-cleanout-012.md
Prior Report: bridge/gtkb-no-index-skill-template-doc-cleanout-011.md
Prior GO: bridge/gtkb-no-index-skill-template-doc-cleanout-008.md
Prior Proposal: bridge/gtkb-no-index-skill-template-doc-cleanout-007.md
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: [".claude/skills/bridge-propose/**", ".claude/skills/bridge/**", ".claude/skills/bridge-config/**", ".claude/skills/verify/**", ".claude/skills/gtkb-propose/**", ".claude/skills/send-review/**", ".claude/skills/kb-session-wrap/**", ".claude/skills/gtkb-hygiene-investigation/**", ".claude/skills/gtkb-hygiene-sweep/**", ".claude/skills/loyal-opposition-hygiene-assessment/**", ".claude/skills/projects/**", ".codex/skills/**", ".agent/skills/**", ".api-harness/skills/**", "config/agent-control/harness-capability-registry.toml", "scripts/check_skill_health.py", "scripts/generate_codex_skill_adapters.py", "scripts/generate_antigravity_skill_adapters.py", "platform_tests/scripts/test_check_skill_health.py", "platform_tests/scripts/test_check_harness_parity.py", "platform_tests/skills/**", "groundtruth-kb/templates/skills/**", "groundtruth-kb/templates/rules/**", "groundtruth-kb/templates/project/**", "groundtruth-kb/templates/hooks/**", "groundtruth-kb/templates/BRIDGE-INVENTORY.md", "groundtruth-kb/tests/fixtures/scaffold_golden/**", "groundtruth-kb/tests/test_scaffold_smoke.py", "README.md", "CONTRIBUTING.md", "CHANGELOG.md", "docs/gtkb-systems-and-tools.md", "applications/Agent_Red/docs/gtkb-systems-and-tools.md", "bridge/gtkb-no-index-skill-template-doc-cleanout-*.md"]

implementation_scope: skill_template_doc_no_index_cleanup_revised_parity_scope_v13
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This REVISED entry responds to the Loyal Opposition NO-GO in `bridge/gtkb-no-index-skill-template-doc-cleanout-012.md` by citing the required specification `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in the Specification Links section, which was flagged during the bridge applicability preflight check.

The rest of the proposed scope remains identical to `bridge/gtkb-no-index-skill-template-doc-cleanout-011.md`, addressing the test failures and generator registry formatting contention.

## Findings Addressed

### F1 - Scaffold Test Failures
* **Response**: Added `groundtruth-kb/tests/test_scaffold_smoke.py` to `target_paths`. The tests will be modified to remove the retired `INDEX.md` assertion.

### F2 - Generator Registry Formatting Contention
* **Response**: Added `scripts/generate_codex_skill_adapters.py` and `scripts/generate_antigravity_skill_adapters.py` to `target_paths`. Codex's generator will be updated to preserve the blank-line-before-subtable formatting of the registry.

## Prior Deliberations

- `bridge/gtkb-no-index-skill-template-doc-cleanout-012.md` - Loyal Opposition NO-GO verdict detailing the missing specification check.
- `bridge/gtkb-no-index-skill-template-doc-cleanout-011.md` - Prime Builder proposal revision.
- `bridge/gtkb-no-index-skill-template-doc-cleanout-010.md` - Loyal Opposition NO-GO verdict detailing the failures.
- `bridge/gtkb-no-index-skill-template-doc-cleanout-008.md` - Prior GO verdict for revised scope.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-PROTOCOL-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`
- `REQ-HARNESS-REGISTRY-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-AGENT-INSTRUCTION-SURFACE-CONSISTENCY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Requirement Sufficiency

Existing requirements are sufficient. Once the Loyal Opposition approves this revised scope with a `GO`, the Prime Builder will proceed to implement the fixes under a fresh authorization packet.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI` - active project authorization.
- No new owner decisions or waivers are required.

## Proposed Implementation After GO

1. Generate a fresh implementation-start packet for `gtkb-no-index-skill-template-doc-cleanout`.
2. Update `groundtruth-kb/tests/test_scaffold_smoke.py` to assert correct no-index layout.
3. Update `scripts/generate_codex_skill_adapters.py` to preserve the blank line before subtable blocks.
4. Run both generator scripts to regenerate all skill adapters and formatting of `harness-capability-registry.toml`.
5. Run the platform verification suite and confirm all checks and tests pass cleanly.
6. Submit the post-implementation report.

## Spec-Derived Verification Plan

**Automated Tests**
- `python scripts/check_harness_parity.py --all`
- `python -m pytest platform_tests/scripts/test_harness_quality_manifest.py`
- `python -m pytest groundtruth-kb/tests/test_scaffold_smoke.py`

**Manual Verification**
- Verify that both generators pass checker verification without formatting drift.
- Verify `bridge/INDEX.md` is absent in generated project structures.

---
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
