REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-58-11Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal — WI-5667 eleven managed scaffold skill artifacts

bridge_kind: prime_proposal
Document: gtkb-wi5667-scaffold-managed-skill-rename
Version: 003
Responds to: bridge/gtkb-wi5667-scaffold-managed-skill-rename-002.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5667

target_paths: ["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/templates/skills/gtkb-decision-capture/SKILL.md", "groundtruth-kb/templates/skills/gtkb-decision-capture/helpers/record_decision.py", "groundtruth-kb/templates/skills/gtkb-bridge-propose/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/gtkb-spec-intake/SKILL.md", "groundtruth-kb/templates/skills/gtkb-spec-intake/helpers/spec_intake.py", "groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_scaffold_skills.py", "groundtruth-kb/tests/test_upgrade_skills.py", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_doctor.py"]

implementation_scope: source | tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement WI-5667's actual owner-authorized rename: the managed registry and
templates emit exactly eleven gtkb-prefixed skill artifacts—two decision-capture,
two bridge-propose, two spec-intake, and five bridge artifacts. The proposal
uses existing temporary-project scaffold/upgrade tests as its fixture evidence.
Both scaffold_golden roots are quarantined evidence and are excluded; no
capture script is invoked and no golden fixture is regenerated.

## Claim

Prime Builder proposes only the bounded managed-artifact rename. The legacy
bare templates remain retained and inert. This slice neither deletes/moves
legacy paths nor changes WI-5640 policy, its untracked interpreter/tests, or
the distinct fixture-capture safety feature.

## Requirement Sufficiency

Existing requirements sufficient. DELIB-202667193 selects gtkb-prefixed
scaffold/template/managed-artifact names, and the active PAUTH covers WI-5667.
The test route creates fresh temporary adopter output; no new capture-control
requirement is needed.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Exact Eleven-Artifact Inventory

| Family | Template artifacts | Emitted managed destination |
| --- | --- | --- |
| decision-capture | SKILL.md; helpers/record_decision.py | .claude/skills/gtkb-decision-capture/** |
| bridge-propose | SKILL.md; helpers/write_bridge.py | .claude/skills/gtkb-bridge-propose/** |
| spec-intake | SKILL.md; helpers/spec_intake.py | .claude/skills/gtkb-spec-intake/** |
| bridge | SKILL.md; helpers/scan_bridge.py; helpers/revise_bridge.py; helpers/impl_report_bridge.py; helpers/show_thread_bridge.py | .claude/skills/gtkb-bridge/** |

The count is exactly eleven. No thirteenth artifact is implied or authorized.

## Proposed Implementation

- Materialize the eleven canonical template files from their corresponding
  retained bare templates, preserving content aside from canonical path
  references needed by the registry contract.
- Update the eleven managed-artifact registry rows so template_path and emitted
  target_path use the gtkb-prefixed locations.
- Update doctor’s explicit decision-capture, bridge-propose, and spec-intake
  presence expectations to the gtkb-prefixed destinations; bridge remains
  covered through the registry-driven lifecycle tests.
- Update only the declared temporary-project scaffold, upgrade, registry, and
  doctor tests to assert canonical outputs and reject stale managed outputs.
- Preserve bare template families untouched as retained migration sources.
  WI-5640 physical-alias policy and any fixture-recovery/baseline transaction
  are explicitly outside this GO request.

## Quarantine And Explicit Exclusions

- Do not read, modify, stage, attribute, regenerate, or commit any path under
  groundtruth-kb/tests/fixtures/scaffold_golden/local-only or
  groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent. The 38-path
  capture diff is quarantined evidence after the destructive capture invocation.
- Do not run scripts/_capture_scaffold_golden.py in any mode.
- Do not change config/file-reference-migration/wi5640.toml, its interpreter,
  its migration tests, generated adapters, canonical skills, or unrelated
  baseline-audit behavior.
- test_base_profile_no_skill_actions is not a selector for this slice because
  its current baseline-audit failure is outside the eleven-artifact inventory.

## Focused Specification-Derived Verification

Observed clean baseline:

    groundtruth-kb/.venv/Scripts/python.exe -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb/tests/test_scaffold_skills.py groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_bridge_propose_skill_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_spec_intake_skill_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_spec_intake_helper_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_execute_creates_missing_spec_intake_files_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_bridge_skill_files_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_execute_creates_missing_bridge_skill_files_at_same_version groundtruth-kb/tests/test_managed_registry.py::test_bridge_skill_records_are_managed_for_dual_agent_profiles groundtruth-kb/tests/test_managed_registry.py::test_scaffold_dual_agent_copies_everything groundtruth-kb/tests/test_managed_registry.py::test_upgrade_dual_agent_manages_full_set_including_gap_28_rules groundtruth-kb/tests/test_doctor.py::test_check_rules_with_files -q --tb=short
    17 passed

Post-change, rerun that exact selector set plus:

    groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_scaffold_skills.py groundtruth-kb/tests/test_upgrade_skills.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_doctor.py
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_scaffold_skills.py groundtruth-kb/tests/test_upgrade_skills.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_doctor.py
    git diff --check -- <all declared paths>
    python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5667-scaffold-managed-skill-rename
    python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5667-scaffold-managed-skill-rename

## Acceptance Criteria

- A fresh temporary dual-agent scaffold and upgrade create exactly the eleven
  canonical gtkb-prefixed managed artifacts.
- Registry records, template locations, doctor checks, and all declared
  temporary-project tests agree on the canonical names.
- No quarantined golden fixture, capture script, policy file, migration test,
  baseline-audit output, or unrelated source file changes.
- The implementation commit contains only declared paths and complete test/lint
  evidence before independent LO review.

## Cross-Harness Disposition

The registry emits shared Claude managed artifacts and the temporary-project
tests cover the dual-agent profile. No adapter regeneration or harness-local
runtime behavior changes are part of this slice.

## Risks And Rollback

The principal risk is a template/registry mismatch or accidental attribution of
the quarantined fixture diff. The exact eleven count, temporary-project test
route, and fixture exclusion fail closed. Rollback is a later governed revert
of only the reviewed implementation commit; retained templates and bridge
history remain intact.

## Owner Decisions / Input

- DELIB-202667193 authorizes the gtkb-prefixed managed scaffold outcome.
- The separate capture-control proposal remains unapproved and is not relied on
  here.

## Recommended Commit Type

fix

