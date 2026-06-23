NEW

# Dispatcher Control Skill - WI-4769

bridge_kind: prime_proposal
Document: gtkb-wi4769-dispatcher-control-skill
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef3a8-fefa-7382-a13c-c93e5ee51026
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex interactive session; approval_policy=never; sandbox=danger-full-access; resolved Prime Builder by owner init keyword ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4769
Project: PROJECT-GTKB-DISPATCHER-CONTROL-CLI
Work Item: WI-4769

target_paths: [".claude/skills/dispatcher-control/SKILL.md", ".codex/skills/dispatcher-control/SKILL.md", ".agent/skills/dispatcher-control/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_dispatcher_control_skill.py"]

implementation_scope: skill
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4769 by adding a canonical GT-KB dispatcher-control skill that makes the governed dispatcher reporting and configuration commands discoverable. The skill must point operators to `gt bridge dispatch report`, `status`, `health`, and the `gt bridge dispatch config ...` transaction subcommands added in WI-4765 and WI-4766, while explicitly routing away from direct reads or edits of `config/dispatcher/rules.toml` and dispatcher runtime JSON.

The implementation will add the canonical `.claude/skills/dispatcher-control/SKILL.md`, register it in `config/agent-control/harness-capability-registry.toml`, regenerate Codex and Antigravity adapters/manifests through the existing generator scripts, and add focused structural tests for the skill contract and adapter parity. It does not change dispatcher scheduling, ranking, caps, or live configuration.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - Requires all bridge-dispatcher reporting and configuration to be exposed through governed `gt bridge dispatch` CLI surfaces and a wrapping skill; WI-4769 satisfies acceptance criterion 5.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - Requires dispatcher configuration mutation only through the governed CLI transaction component; the skill must warn agents/operators away from direct rules.toml or runtime-state edits and point to CLI transactions instead.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires append-only numbered bridge files and role-authorized status tokens for implementation workflow.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires the proposal to cite concrete governing specs and map implementation/verification to them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires live Project Authorization, Project, and Work Item metadata in implementation-targeting proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires each linked spec to have derived tests or verification evidence before a VERIFIED verdict.
- `GOV-STANDING-BACKLOG-001` - Treats WI-4769 as the MemBase work authority for this slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Treats the accepted owner requirement and work item as durable artifacts rather than chat-only guidance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Supports preserving the reusable dispatcher-control procedure as a governed skill artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Classifies the owner-approved skill requirement as an artifact lifecycle trigger now being implemented through the bridge.

## Prior Deliberations

- `DELIB-20265795` - Owner AUQ-backed decision requiring all dispatcher reporting and configuration to be available through a governed CLI and wrapping skill.
- `INTAKE-f8bc08a3` - Earlier dispatcher/bridge CLI intake supporting the pattern of CLI surfaces as the primary artifact-operation UI.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` - Governs use of structurally compliant bridge proposal scaffolding.
- `DELIB-S364-SKILL-MODERNIZATION-SLICE-0-PAUTH` - Prior skill modernization authorization pattern for checking skill structure and parity without changing runtime behavior.

## Owner Decisions / Input

Owner approval is already captured by `DELIB-20265795` and implemented as `PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4769`. No new owner decision is required because this proposal implements the already captured WI-4769 scope: the dispatcher-control skill wrapping the governed CLI surfaces.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-DISPATCHER-CONTROL-SURFACE-001` explicitly requires "A skill surfaces the reporting + configuration commands," and `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` defines the direct-edit prohibition the skill must reinforce. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Specification / authority | Derived implementation obligation | Verification command / evidence |
|---|---|---|
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Canonical skill exists, names the reporting and configuration commands, and makes the skill wrapper discoverable. | `python -m pytest platform_tests/skills/test_dispatcher_control_skill.py -q --tb=short` must include assertions for skill existence, frontmatter trigger terms, report/status/health commands, config transaction commands, and skill adapter parity. |
| `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` | Skill tells agents/operators to use `gt bridge dispatch config` transaction commands and not directly edit `config/dispatcher/rules.toml` or runtime JSON. | Same focused pytest file must assert the direct-edit prohibition text and governed transaction routing text are present in the canonical skill and generated adapters. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal includes Project Authorization, Project, and Work Item lines tied to live MemBase state. | `python scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi4769-dispatcher-control-skill-001.md --bridge-id gtkb-wi4769-dispatcher-control-skill` must pass after filing. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Proposal cites specs and implementation report/VERIFIED evidence maps tests back to those specs. | `python scripts/adr_dcl_clause_preflight.py --content-file bridge/gtkb-wi4769-dispatcher-control-skill-001.md --bridge-id gtkb-wi4769-dispatcher-control-skill` must report zero blocking gaps. |
| Cross-harness skill parity | Codex and Antigravity adapters/manifests and harness capability registry converge from the canonical `.claude` skill. | `python scripts/generate_codex_skill_adapters.py --check --update-registry` and `python scripts/generate_antigravity_skill_adapters.py --check --update-registry` must pass after generation. |
| Existing generator behavior | Adding a new skill does not regress generator behavior. | `python -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_check_harness_parity.py -q --tb=short` must pass or any failure must be explained as unrelated existing drift. |

## Risk / Rollback

Primary risk: a skill that reads like documentation but fails to route operators to the exact governed commands could leave the old direct-file-edit habit intact. Mitigation: focused structural tests assert command names, direct-edit prohibition, and adapter parity.

Secondary risk: updating the harness capability registry or generated manifests could create parity drift. Mitigation: use the existing adapter generators and run their check modes plus parity tests.

Rollback: remove the new canonical skill, generated adapters, manifest/registry additions, and focused test file in one commit. No dispatcher runtime behavior or live config is changed.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4769-dispatcher-control-skill`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

Recommended commit type: `feat:`. The implementation adds a new operator-facing skill surface for an already specified dispatcher-control capability.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
