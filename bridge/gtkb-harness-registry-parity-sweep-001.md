NEW
author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: 2026-06-01-S371-prime-builder-harness-registry-parity-sweep
author_model: Gemini 3.5 Flash
author_model_version: gemini-3.5-flash
author_model_configuration: explanatory output style; interactive Prime Builder session
author_metadata_source: Antigravity desktop session environment

# Implementation Proposal - Harness Capability Registry Parity

bridge_kind: implementation_report
Document: gtkb-harness-registry-parity-sweep
Version: 001 (NEW)
Date: 2026-06-01 UTC
Author: Prime Builder (Antigravity, harness C)

Project: PROJECT-GTKB-SKILL-MODERNIZATION
Work Item: WI-3459
Project Authorization: PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-SKILL-MODERNIZATION-SLICE-3-KB-WORK-ITEM-MIGRATION

target_paths: ["config/agent-control/harness-capability-registry.toml", ".codex/skills/gtkb-hygiene-sweep/SKILL.md", ".codex/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".agent/skills/MANIFEST.json"]

Recommended commit type: feat

## Implementation Plan

This is the implementation slice for resolving harness capability registry drift under `WI-3459` (Option 5), authorized by the owner's explicit session directive "authorize option 5" in session S371. This implementation registers the two extra skills (`gtkb-hygiene-sweep` and `loyal-opposition-hygiene-assessment`) in `config/agent-control/harness-capability-registry.toml` and generates their corresponding adapters to achieve full capability registry parity with zero warnings.

### Component 1 - Harness Capability Registry Registration

We will add two new capability blocks to `config/agent-control/harness-capability-registry.toml`:
1. `skill.gtkb-hygiene-sweep`: Scoped to `["prime-builder"]` and native on Claude Code.
2. `skill.loyal-opposition-hygiene-assessment`: Scoped to `["loyal-opposition"]` and native on Claude Code.

### Component 2 - Codex and Antigravity Skill Adapters

Using the deterministic generator scripts:
- `python scripts/generate_codex_skill_adapters.py --update-registry` will automatically generate `.codex/skills/gtkb-hygiene-sweep/SKILL.md`, `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md`, and update the registry's Codex blocks with computed SHA-256 hashes.
- `python scripts/generate_antigravity_skill_adapters.py --update-registry` will automatically generate `.agent/skills/loyal-opposition-hygiene-assessment/SKILL.md` (role-scoped for the LO-scoped capability) and update the registry's Antigravity blocks with computed SHA-256 hashes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this is a NEW implementation proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the capability registry and generated adapters are durable, governed artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan below maps every cited spec to executed verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item + Project Authorization metadata present in header.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are within `E:\GT-KB`; no `applications/**` paths touched.

## Prior Deliberations

- `DELIB-2505` - the options implementation deliberation in which the owner explicitly authorized Option 5.
- `DELIB-2079` - role-scoped capability parity design decisions for Antigravity LO-scoped skill registry.

## Owner Decisions / Input

- `S371 Owner Directive "authorize option 5" (2026-06-01)`: Mike explicitly authorized option 5 to register the two extra skills in the capability registry.

## Requirement Sufficiency

Existing requirements sufficient. No new GOV/SPEC/ADR/DCL is required.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One implementation proposal, one work item (WI-3459), adding two capabilities to `harness-capability-registry.toml`, and generating their adapter files via existing deterministic scripts.

## Specification-Derived Verification Plan

| Specification | Test or verification command | Evidence at post-impl |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | INDEX inspection: `gtkb-harness-registry-parity-sweep` thread NEW -> GO/NO-GO -> implementation -> VERIFIED | Bridge INDEX visible at `bridge/INDEX.md` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Harness parity check status: `python scripts/check_harness_parity.py --all --markdown` | Parity check output shows `PASS` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This Specification Links section + applicability preflight `preflight_passed: true` | Preflight output in post-impl report |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table; every cited spec maps to executed verification at post-impl | Post-impl table with command outputs |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata inspection (Project, Work Item, Project Authorization) | Header lines in this file |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths under `E:\GT-KB` | Header `target_paths` inspection |

## Test Plan and Spec-to-Test Mapping

Executable verification at post-impl:

```text
# 1. Run Codex skill generator
python scripts/generate_codex_skill_adapters.py --update-registry

# 2. Run Antigravity skill generator
python scripts/generate_antigravity_skill_adapters.py --update-registry

# 3. Check harness parity yields PASS with 0 EXTRA
python scripts/check_harness_parity.py --all --markdown

# 4. Verify test suite passes
python -m pytest platform_tests/scripts/test_generate_antigravity_skill_adapters.py -q --tb=short
```

Each command's output captured in the post-implementation report.

## Acceptance Criteria

1. Both skills are correctly registered in `config/agent-control/harness-capability-registry.toml`.
2. Generator scripts run cleanly and output generated skill files with identical content structure.
3. `.agent/skills/` contains only LO-scoped skill adapters, while `.codex/skills/` contains all skills.
4. Harness parity check status is `PASS` with 0 EXTRA skills.

## Risks / Rollback

- Risk: Generator scripts fail under Windows environment. Mitigation: Test suite is already verified to pass locally in under 1s.
- Rollback: Revert `config/agent-control/harness-capability-registry.toml`, delete `.codex/skills/gtkb-hygiene-sweep/`, `.codex/skills/loyal-opposition-hygiene-assessment/`, and `.agent/skills/loyal-opposition-hygiene-assessment/`.

## Files Changed

New files:
- `.codex/skills/gtkb-hygiene-sweep/SKILL.md`
- `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md`
- `.agent/skills/loyal-opposition-hygiene-assessment/SKILL.md`

Modified files:
- `config/agent-control/harness-capability-registry.toml`
- `.codex/skills/MANIFEST.json`
- `.agent/skills/MANIFEST.json`

## In-Root Placement Evidence

All target paths are within `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
