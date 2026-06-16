NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# No-Index Skill, Template, And Documentation Cleanout Proposal

bridge_kind: prime_proposal
Document: gtkb-no-index-skill-template-doc-cleanout
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: [".claude/skills/bridge-propose/**", ".claude/skills/bridge/**", ".claude/skills/verify/SKILL.md", ".claude/skills/gtkb-propose/SKILL.md", ".claude/skills/send-review/SKILL.md", ".claude/skills/kb-session-wrap/**", ".codex/skills/bridge-propose/**", ".codex/skills/bridge/**", ".codex/skills/verify/SKILL.md", ".codex/skills/gtkb-propose/SKILL.md", ".codex/skills/send-review/SKILL.md", ".codex/skills/kb-session-wrap/**", ".agent/skills/**", ".api-harness/skills/**", "groundtruth-kb/templates/skills/**", "groundtruth-kb/templates/rules/**", "groundtruth-kb/templates/project/**", "groundtruth-kb/templates/hooks/**", "groundtruth-kb/templates/BRIDGE-INVENTORY.md", "groundtruth-kb/tests/fixtures/scaffold_golden/**", "README.md", "CONTRIBUTING.md", "CHANGELOG.md", "docs/gtkb-systems-and-tools.md", "applications/Agent_Red/docs/gtkb-systems-and-tools.md", "bridge/gtkb-no-index-skill-template-doc-cleanout-*.md"]

implementation_scope: skill_template_doc_no_index_cleanup
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

The no-index sweep found a large set of active skill, scaffold-template, adapter-manifest, and public-documentation surfaces that still present `bridge/INDEX.md` or a "generated compatibility view" as expected current behavior. These surfaces train future agents and scaffolded projects, so leaving them stale will recreate the same confusion in fresh sessions.

Representative evidence:

- `.claude/skills/bridge-propose/SKILL.md`, `.codex/skills/bridge-propose/SKILL.md`, `.agent/skills/bridge-propose/SKILL.md`, and `.api-harness/skills/bridge-propose/SKILL.md` describe proposal filing as publishing a `bridge/INDEX.md` compatibility entry.
- `.claude/skills/bridge/SKILL.md`, `.codex/skills/bridge/SKILL.md`, and `.agent/skills/bridge/SKILL.md` contain active steps instructing agents to read/update the retired index.
- `.claude/skills/bridge/helpers/scan_bridge.py`, `revise_bridge.py`, and `impl_report_bridge.py` still document and implement index-dependent helper behavior.
- `groundtruth-kb/templates/skills/**`, `groundtruth-kb/templates/rules/**`, and scaffold golden fixtures still teach new projects that index-based bridge state is current or canonical.
- README/CONTRIBUTING/CHANGELOG and systems-and-tools docs still link to or describe the retired file in ways that are not clearly historical.

This proposal intentionally overlaps a small part of `bridge/gtkb-no-index-dispatcher-trigger-cleanout-001.md` for the bridge skill itself. Loyal Opposition should require implementation to coordinate the overlap and avoid double-edit conflicts.

## Prior Deliberations

- `DELIB-20263438` - Owner requirement: corrected bridge-dispatch architecture and no role/dispatchability conflation.
- `DELIB-20261030` - GT-KB skills guidance compliance advisory; relevant to keeping skills accurate and non-misleading.
- `DELIB-20261027` - Advisory report on GT-KB skill use, coverage, and enforcement opportunities.
- `bridge/gtkb-no-index-dispatcher-trigger-cleanout-001.md` - Sibling proposal that includes bridge and bridge-config skill cleanup for dispatcher-trigger scope.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must proceed through a GO and live work-intent claim.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge lifecycle remains governed by proposal/review/report/verification files.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project/work authorization metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal links governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map tests to linked requirements.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher/status/health and harness registry surfaces are the dispatch topology authorities.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch routing uses roles, subjects, and activity rules.
- `GOV-AGENT-INSTRUCTION-SURFACE-CONSISTENCY-001` - agent-facing instruction surfaces must not teach contradictory current authority.

## Requirement Sufficiency

Existing requirements are sufficient. Mike's directive rejects backward compatibility for `bridge/INDEX.md`; therefore skill/template/doc references must either be removed from active guidance or explicitly marked as historical/audit-only. In scaffold templates, the steady-state instruction should be the current dispatcher/versioned-file model, not the old compatibility model.

## Pre-Filing Self-Check

The sweep used fixed-string searches because Windows path-guard logic blocks some regexes containing a Windows-style retired-index fragment. That guard behavior is not a blocker for implementation; use fixed-string `rg -F "INDEX.md"` searches and target-path scoped searches.

## Proposed Implementation

1. Update canonical `.claude/skills/**` sources first, then regenerate `.codex`, `.agent`, and `.api-harness` adapters/manifests through the established adapter pipeline.
2. Replace active "read/update/publish bridge/INDEX.md" instructions with:
   - versioned bridge files are the durable audit chain;
   - dispatcher/TAFE state and `gt bridge dispatch config|status|health` are live operation surfaces;
   - `bridge/INDEX.md` must not exist in current GT-KB and any helper requiring it is defective.
3. Update or retire bridge helper scripts that still require the index, or clearly mark them historical if they are preserved only for pre-cutover archive ingestion.
4. Update scaffold templates and golden fixtures so new installations do not inherit retired-index instructions.
5. Update public docs to avoid live links to a non-existent `bridge/INDEX.md`; any mention must say historical/pre-cutover/audit-only.

## Spec-Derived Verification Plan

Run:

```powershell
Test-Path bridge\INDEX.md
rg -n -F "bridge/INDEX.md" .claude\skills .codex\skills .agent\skills .api-harness\skills groundtruth-kb\templates groundtruth-kb\tests\fixtures\scaffold_golden README.md CONTRIBUTING.md CHANGELOG.md docs\gtkb-systems-and-tools.md applications\Agent_Red\docs\gtkb-systems-and-tools.md
rg -n -F "compatibility view" .claude\skills .codex\skills .agent\skills .api-harness\skills groundtruth-kb\templates README.md CONTRIBUTING.md CHANGELOG.md docs\gtkb-systems-and-tools.md applications\Agent_Red\docs\gtkb-systems-and-tools.md
python scripts\generate_codex_skill_adapters.py --check --update-registry
python -m pytest platform_tests\scripts\test_check_harness_parity.py platform_tests\scripts\test_check_skill_health.py platform_tests\skills -q --tb=short
python -m pytest groundtruth-kb\tests\test_scaffold_smoke.py groundtruth-kb\tests\test_scaffold_bridge_index.py groundtruth-kb\tests\test_scaffold_consumes_resolver.py -q --tb=short
```

Expected:

- `Test-Path bridge\INDEX.md` returns `False`.
- Active skills/templates/docs no longer instruct agents or scaffolded projects to read, update, publish, or expect the retired index.
- Remaining mentions are explicitly historical/audit-only or negative tests.
- Skill adapter and scaffold tests pass.

## Risks

- Skill adapters are generated; editing generated copies without regenerating from canonical sources would create parity drift.
- Some historical scaffold tests may be intentionally preserving pre-cutover behavior. Implementation must distinguish historical fixture assertions from current golden-fixture instructions.
- This proposal should be sequenced with `gtkb-no-index-dispatcher-trigger-cleanout` to avoid overlapping edits to bridge skills.

## Rollback

Revert changes in the target files. Do not recreate `bridge/INDEX.md`; restoring it would hide prompt-surface defects rather than fix them.
