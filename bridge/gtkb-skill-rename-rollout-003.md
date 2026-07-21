REVISED

bridge_kind: proposal
Document: gtkb-skill-rename-rollout
Version: 003
Date: 2026-07-20
Author: Prime Builder (goose/G)
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: goose-20260720-pb-skillrename
Responds to: bridge/gtkb-skill-rename-rollout-002.md
Work Item: WI-5640 (supersedes/absorbs WI-5584 config scope)
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
target_paths:
  - .claude/skills/**
  - .codex/skills/**
  - .agent/skills/**
  - .cursor/skills/**
  - .goose/skills/**
  - .api-harness/skills/**
  - config/agent-control/harness-capability-registry.toml
  - config/agent-control/command-surface.toml
  - config/agent-control/skill-scenarios.toml
  - config/agent-control/skill-rename-map.toml
  - groundtruth-kb/templates/skills/**/*.md
  - groundtruth-kb/templates/managed-artifacts.toml
  - groundtruth-kb/src/groundtruth_kb/project/doctor.py
  - groundtruth-kb/src/groundtruth_kb/project/upgrade.py
  - groundtruth-kb/src/groundtruth_kb/intake.py
  - groundtruth-kb/src/groundtruth_kb/modernization/workflow.py
  - groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py
  - groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml
  - scripts/check_harness_parity.py
  - scripts/generate_codex_skill_adapters.py
  - scripts/generate_antigravity_skill_adapters.py
  - scripts/generate_api_skill_adapters.py
  - scripts/session_self_initialization.py
  - scripts/verify_antigravity_dispatch.py
  - scripts/_dispatch_wi5241_006_verdict.py
  - scripts/harness_parity_phase2.py
  - .claude/rules/auto-finalization-sweep.md
  - .claude/rules/codex-review-gate.md
  - .claude/rules/file-bridge-protocol.md
  - .claude/rules/loyal-opposition.md
  - docs/gtkb-dashboard/session-wrapup-report.md
  - docs/procedures/per-thread-finalization-repair.md
  - docs/harness-parity-phase-2-matrix.md

# Canonical Skill Renaming Rollout (gtkb- prefix) - v003

## target_paths

Machine-readable approved target set (mirrors the front-matter `target_paths` list above):

```json
[
  ".claude/skills/**",
  ".codex/skills/**",
  ".agent/skills/**",
  ".cursor/skills/**",
  ".goose/skills/**",
  ".api-harness/skills/**",
  "config/agent-control/harness-capability-registry.toml",
  "config/agent-control/command-surface.toml",
  "config/agent-control/skill-scenarios.toml",
  "config/agent-control/skill-rename-map.toml",
  "groundtruth-kb/templates/skills/**/*.md",
  "groundtruth-kb/templates/managed-artifacts.toml",
  "groundtruth-kb/src/groundtruth_kb/project/doctor.py",
  "groundtruth-kb/src/groundtruth_kb/project/upgrade.py",
  "groundtruth-kb/src/groundtruth_kb/intake.py",
  "groundtruth-kb/src/groundtruth_kb/modernization/workflow.py",
  "groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py",
  "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml",
  "scripts/check_harness_parity.py",
  "scripts/generate_codex_skill_adapters.py",
  "scripts/generate_antigravity_skill_adapters.py",
  "scripts/generate_api_skill_adapters.py",
  "scripts/session_self_initialization.py",
  "scripts/verify_antigravity_dispatch.py",
  "scripts/_dispatch_wi5241_006_verdict.py",
  "scripts/harness_parity_phase2.py",
  ".claude/rules/auto-finalization-sweep.md",
  ".claude/rules/codex-review-gate.md",
  ".claude/rules/file-bridge-protocol.md",
  ".claude/rules/loyal-opposition.md",
  "docs/gtkb-dashboard/session-wrapup-report.md",
  "docs/procedures/per-thread-finalization-repair.md",
  "docs/harness-parity-phase-2-matrix.md"
]
```

## Summary
The 44 canonical skills in `.claude/skills/` are being renamed to a uniform `gtkb-` prefix. This v003 addresses NO-GO findings F1-F6 and absorbs WI-5584. The rest of the platform still references OLD names: the capability registry `canonical_source` paths, the five generated projection surfaces, the scaffolded managed-artifact surface, `command-surface.toml`, and docs/scripts. This umbrella rolls the rename out atomically across all coupling surfaces.

## NO-GO resolution mapping
- **F1 (map missing)**: `config/agent-control/skill-rename-map.toml` now committed as Slice 0 ground truth.
- **F2 (frontmatter not updated)**: corrected - Summary no longer claims all frontmatter updated; Slice 0 fixes `gtkb-batch/SKILL.md` frontmatter `kb-batch` -> `gtkb-batch` and renames 3 mismatched dirs to their frontmatter names.
- **F3 (name-map discrepancies)**: map below is built from ACTUAL on-disk frontmatter `name:` fields (canonical per Decision 7A/A1), not assumed transforms.
- **F4 (path errors)**: target_paths now list real dirs `.agent` (not `.agents`), and add `.cursor` + `.goose`. Projection surfaces = .agent, .codex, .api-harness, .cursor, .goose (Decision 7B/B1).
- **F5 (no work item)**: MemBase work item creation attempted via `backlog add-work-item` (all GOV-12/13 options supplied) but blocked: `resolve_changed_by` requires an open session envelope with worker-role provenance, which this ad-hoc Prime context does not hold. Work item will be created at Slice 0 implementation start under an authorized session envelope (or owner may create it). Tracked under bridge thread gtkb-skill-rename-rollout.
- **F6 (generator step omitted)**: verification plan now includes explicit execution of the three adapter generators.
- **WI-5584 conflict**: absorbed (Decision 7C/C1) - this umbrella owns harness-capability-registry.toml / command-surface.toml / managed-artifacts.toml canonicalization; WI-5584 scope folded in.

## Authoritative name map (dir -> canonical frontmatter name)
| Current dir | Canonical name | Action |
|---|---|---|
| `gtkb-adr` | `gtkb-adr` | aligned |
| `gtkb-advisory-disposition` | `gtkb-advisory-disposition` | aligned |
| `gtkb-advisory-intake` | `gtkb-advisory-intake` | aligned |
| `gtkb-advisory-proposal` | `gtkb-advisory-proposal` | aligned |
| `gtkb-alternatives-investigation` | `gtkb-alternatives-investigation` | aligned |
| `gtkb-arch-audit` | `gtkb-arch-audit` | aligned |
| `gtkb-assert` | `gtkb-assert` | aligned |
| `gtkb-assertion-triage` | `gtkb-assertion-triage` | aligned |
| `gtkb-batch` | `kb-batch` | **RENAME dir** |
| `gtkb-benchmarks` | `gtkb-benchmarks` | aligned |
| `gtkb-bridge` | `gtkb-bridge` | aligned |
| `gtkb-bridge-config` | `gtkb-bridge-config` | aligned |
| `gtkb-bridge-propose` | `gtkb-bridge-propose` | aligned |
| `gtkb-bridge-reconciliation` | `gtkb-bridge-reconciliation` | aligned |
| `gtkb-check-deliberations` | `gtkb-check-deliberations` | aligned |
| `gtkb-code-review-audit` | `gtkb-code-review-audit` | aligned |
| `gtkb-codex-report` | `gtkb-loyal-opposition-report` | **RENAME dir** |
| `gtkb-decision-capture` | `gtkb-decision-capture` | aligned |
| `gtkb-dispatcher-control` | `gtkb-dispatcher-control` | aligned |
| `gtkb-formal-artifact-packet-helper` | `gtkb-formal-artifact-packet-helper` | aligned |
| `gtkb-grill-me-for-clarification` | `gtkb-grill-me-for-clarification` | aligned |
| `gtkb-harness-parity-review` | `gtkb-harness-parity-review` | aligned |
| `gtkb-hygiene-investigation` | `gtkb-hygiene-investigation` | aligned |
| `gtkb-hygiene-reclaim` | `gtkb-hygiene-reclaim` | aligned |
| `gtkb-hygiene-sweep` | `gtkb-hygiene-sweep` | aligned |
| `gtkb-kb-work-item` | `gtkb-work-item` | **RENAME dir** |
| `gtkb-lo-hygiene-assessment` | `gtkb-lo-hygiene-assessment` | aligned |
| `gtkb-lo-opportunity-radar` | `gtkb-lo-opportunity-radar` | aligned |
| `gtkb-managed-skill-adoption-review` | `gtkb-managed-skill-adoption-review` | aligned |
| `gtkb-projects` | `gtkb-projects` | aligned |
| `gtkb-promote` | `gtkb-promote` | aligned |
| `gtkb-proposal-review` | `gtkb-proposal-review` | aligned |
| `gtkb-propose` | `gtkb-propose` | aligned |
| `gtkb-query` | `gtkb-query` | aligned |
| `gtkb-release-candidate-gate` | `gtkb-release-candidate-gate` | aligned |
| `gtkb-send-review` | `gtkb-send-review` | aligned |
| `gtkb-session-wrap` | `gtkb-session-wrap` | aligned |
| `gtkb-session-wrap-scan` | `gtkb-session-wrap-scan` | aligned |
| `gtkb-skill-governance-lifecycle` | `gtkb-skill-governance-lifecycle` | aligned |
| `gtkb-spec` | `gtkb-spec` | aligned |
| `gtkb-spec-intake` | `gtkb-spec-intake` | aligned |
| `gtkb-structural-hygiene-review` | `gtkb-structural-hygiene-review` | aligned |
| `gtkb-sweep-commit` | `gtkb-sweep-commit` | aligned |
| `gtkb-verify` | `gtkb-verify` | aligned |

## Phased slices
- **Slice 0 - Ground truth & reconciliation**: commit skill-rename-map.toml; fix gtkb-batch frontmatter -> gtkb-batch; rename mismatched dirs (gtkb-codex-report->gtkb-loyal-opposition-report, gtkb-kb-work-item->gtkb-work-item) so dir==frontmatter name; baseline-audit->gtkb-baseline-audit (D3).
- **Slice 1 - Registry + projections**: update all canonical_source/canonical_name in harness-capability-registry.toml (incl. WI-5584 config-canonicalization); update command-surface.toml + skill-scenarios.toml; regenerate all five projection surfaces; regenerate MANIFEST.json; refresh source_sha256; check_harness_parity.py green.
- **Slice 2 - Managed-artifact / scaffold / doctor**: rename templates/skills dirs to gtkb-*; update managed-artifacts.toml paths; update doctor.py hardcoded checks; upgrade.py adopter migration; regression tests.
- **Slice 3 - Docs/rules/dispatch refs**: update the 17 referencing files.
- **Slice 4 - Verification & release gating**: run generators explicitly; pytest -q --tb=short; ruff check .; ruff format --check .; check_harness_parity.py green; fresh-adopter scaffold + doctor roundtrip.

## Requirement Sufficiency
Existing requirements sufficient

## Specification Links
- GOV-FILE-BRIDGE-AUTHORITY-001 (blocking) - bridge-mediated implementation authority.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (blocking) - this spec linkage.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (blocking) - verification derived from linked specs.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 (blocking) - root/applications boundary; managed-artifact renames affect adopter scaffold under groundtruth-kb/templates.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - rename map + owner decisions preserved as durable artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - traceability across artifacts/tests.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - lifecycle states for renamed/retired skill artifacts.

## Specification-derived verification plan
- Adapter generation (F6): run `python scripts/generate_codex_skill_adapters.py`, `python scripts/generate_antigravity_skill_adapters.py`, `python scripts/generate_api_skill_adapters.py`; confirm .cursor + .goose surfaces regenerated.
- Harness parity: `python scripts/check_harness_parity.py` green across all harnesses.
- Managed-artifact lockstep: doctor registry parity + no-parallel-manifests tests; scaffold->upgrade->doctor roundtrip on a fresh adopter.
- No regressions: `python -m pytest -q --tb=short`, `ruff check .`, `ruff format --check .`.

## Risks
- Adopter breakage (High): renames to the 6 managed skills invalidate adopter doctor checks until upgrade.py migrates their tree.
- Parity-gate false-positives (Med): every adapter flags drifted until source_sha256 regenerates.
- Partial-rename hazard (Med): resolved by Slice 0 authoritative map + frontmatter/dir reconciliation.
