NEW

bridge_kind: proposal
Document: gtkb-skill-rename-rollout
Version: 001
Date: 2026-07-20
Author: Prime Builder (goose/G)
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: goose-20260720-pb-skillrename
target_paths:
  - .claude/skills/**
  - .codex/skills/**
  - .agents/skills/**
  - .api-harness/skills/**
  - config/agent-control/harness-capability-registry.toml
  - config/agent-control/command-surface.toml
  - config/agent-control/skill-scenarios.toml
  - config/agent-control/skill-rename-map.toml
  - groundtruth-kb/templates/skills/**
  - groundtruth-kb/templates/managed-artifacts.toml
  - groundtruth-kb/src/groundtruth_kb/project/doctor.py
  - groundtruth-kb/src/groundtruth_kb/project/upgrade.py
  - groundtruth-kb/src/groundtruth_kb/intake.py
  - groundtruth-kb/src/groundtruth_kb/modernization/workflow.py
  - groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py
  - groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml
  - scripts/check_harness_parity.py
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

# Canonical Skill Renaming Rollout (gtkb- prefix)

## Summary
The 44 canonical skills in `.claude/skills/` have been renamed to a uniform `gtkb-` prefix (frontmatter `name:` fields updated on disk). The rest of the platform still references the OLD names: the capability registry `canonical_source` paths, the generated harness projections (`.codex`, `.agents`, `.api-harness`), the scaffolded managed-artifact surface (`templates/`, `doctor.py`), `command-surface.toml`, and ~17 docs/scripts. This umbrella rolls the rename out atomically across all four coupling surfaces so the tree does not sit in a half-renamed state.

## Owner decisions (recorded this session)
- D1 = A: single umbrella work item, phased slices in one bridge chain.
- D2 = Yes: `.claude/skills/gtkb-batch/SKILL.md` frontmatter `name:` `kb-batch` -> `gtkb-batch`.
- D3 = A: scaffold-only `baseline-audit` -> `gtkb-baseline-audit` (templates + managed-artifacts.toml).
- D5 = C/D6 = B: pre-existing intentional reclaim sweep (281 staged paths) committed separately at ac8488ec with `--no-verify` per owner authorization; tree is now rename-only.

## Old -> New name map (authoritative)
| Old | New | On disk |
|---|---|---|
| `alternatives-investigation` | `gtkb-alternatives-investigation` | yes |
| `arch-audit` | `gtkb-arch-audit` | yes |
| `assertion-triage` | `gtkb-assertion-triage` | yes |
| `gtkb-bridge` | `gtkb-bridge` | yes |
| `bridge-config` | `gtkb-bridge-config` | yes |
| `dispatcher-control` | `gtkb-dispatcher-control` | yes |
| `gtkb-bridge-propose` | `gtkb-bridge-propose` | yes |
| `bridge-reconciliation` | `gtkb-bridge-reconciliation` | yes |
| `gtkb-propose` | `gtkb-propose` | yes |
| `check-deliberations` | `gtkb-check-deliberations` | yes |
| `code-review-audit` | `gtkb-code-review-audit` | yes |
| `lo-opportunity-radar` | `gtkb-lo-opportunity-radar` | yes |
| `loyal-opposition-report` | `gtkb-loyal-opposition-report` | **NO** |
| `gtkb-decision-capture` | `gtkb-decision-capture` | yes |
| `harness-parity-review` | `gtkb-harness-parity-review` | yes |
| `skill-governance-lifecycle` | `gtkb-skill-governance-lifecycle` | yes |
| `advisory-disposition` | `gtkb-advisory-disposition` | yes |
| `advisory-proposal` | `gtkb-advisory-proposal` | yes |
| `advisory-intake` | `gtkb-advisory-intake` | yes |
| `kb-adr` | `gtkb-adr` | yes |
| `kb-assert` | `gtkb-assert` | yes |
| `kb-batch` | `gtkb-batch` | yes |
| `kb-promote` | `gtkb-promote` | yes |
| `kb-query` | `gtkb-query` | yes |
| `kb-session-wrap` | `gtkb-session-wrap` | yes |
| `kb-session-wrap-scan` | `gtkb-session-wrap-scan` | yes |
| `kb-spec` | `gtkb-spec` | yes |
| `kb-work-item` | `gtkb-work-item` | **NO** |
| `projects` | `gtkb-projects` | yes |
| `proposal-review` | `gtkb-proposal-review` | yes |
| `release-candidate-gate` | `gtkb-release-candidate-gate` | yes |
| `send-review` | `gtkb-send-review` | yes |
| `gtkb-spec-intake` | `gtkb-spec-intake` | yes |
| `structural-hygiene-review` | `gtkb-structural-hygiene-review` | yes |
| `gtkb-benchmarks` | `gtkb-benchmarks` | yes |
| `grill-me-for-clarification` | `gtkb-grill-me-for-clarification` | yes |
| `gtkb-hygiene-investigation` | `gtkb-hygiene-investigation` | yes |
| `gtkb-hygiene-sweep` | `gtkb-hygiene-sweep` | yes |
| `gtkb-hygiene-reclaim` | `gtkb-hygiene-reclaim` | yes |
| `gtkb-sweep-commit` | `gtkb-sweep-commit` | yes |
| `loyal-opposition-hygiene-assessment` | `gtkb-loyal-opposition-hygiene-assessment` | **NO** |
| `gtkb-verify` | `gtkb-verify` | yes |
| `formal-artifact-packet-helper` | `gtkb-formal-artifact-packet-helper` | yes |
| `managed-skill-adoption-review` | `gtkb-managed-skill-adoption-review` | yes |

_Note: 3 registry names lack a clean 1:1 on-disk match and are resolved in Slice 0: see registry canonical_source below._


## Phased slices
- **Slice 0 - Ground truth**: commit `config/agent-control/skill-rename-map.toml`; reconcile anomalies (gtkb-batch frontmatter, baseline-audit, gtkb-bridge registry path).
- **Slice 1 - Registry + projections**: update all `canonical_source`/`canonical_name` in harness-capability-registry.toml; update command-surface.toml + skill-scenarios.toml; regenerate .codex/.agents/.api-harness via the three generate_*_skill_adapters.py; regenerate MANIFEST.json; refresh source_sha256; check_harness_parity.py green.
- **Slice 2 - Managed-artifact / scaffold / doctor**: rename templates/skills dirs to gtkb-*; update managed-artifacts.toml template_path/target_path; update doctor.py hardcoded checks (decision-capture, bridge-propose, spec-intake); add upgrade.py migration for existing adopters; regression tests (doctor registry parity, no-parallel-manifests, scaffold roundtrip).
- **Slice 3 - Docs/rules/dispatch refs**: update the 17 referencing files (rules, procedures, dispatch scripts, session_self_initialization.py, modernization/workflow.py, intake.py, deployability_preservation_gate.py, duplicated context/registries/v1 command-surface.toml).
- **Slice 4 - Verification & release gating**: pytest -q --tb=short; ruff check .; ruff format --check .; check_harness_parity.py green; fresh-adopter scaffold + doctor roundtrip.

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
- Harness parity (registry/projection lockstep) -> `python scripts/check_harness_parity.py` must be green across all harnesses.
- Managed-artifact lockstep (Gap 2.8) -> doctor registry parity + no-parallel-manifests tests; scaffold->upgrade->doctor roundtrip on a fresh adopter.
- No regressions -> `python -m pytest -q --tb=short`, `ruff check .`, `ruff format --check .`.

## Risks
- Adopter breakage (High): renames to the 6 managed skills invalidate adopter doctor checks until upgrade.py migrates their tree.
- Parity-gate false-positives (Med): every adapter flags drifted until source_sha256 regenerates.
- Partial-rename hazard (Med): gtkb-batch frontmatter mismatch shows the rename was not machine-validated; Slice 0 name-map commit closes this.
