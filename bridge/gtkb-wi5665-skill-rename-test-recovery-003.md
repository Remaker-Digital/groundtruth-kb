REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-44-41Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal — WI-5665 evidence-backed clean test recovery slice

bridge_kind: prime_proposal
Document: gtkb-wi5665-skill-rename-test-recovery
Version: 003
Responds to: bridge/gtkb-wi5665-skill-rename-test-recovery-002.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5665

target_paths: ["groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_upgrade_skills.py", "platform_tests/scripts/test_harness_skill_effectiveness.py", "platform_tests/scripts/test_gitattributes_lf_policy.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py"]

implementation_scope: tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

This first WI-5665 recovery slice is restricted to five clean test modules with
observed stale skill-rename expectations or fixtures. It deliberately excludes
the three pre-existing dirty test paths and every unclassified literal from the
former 29-path proposal. A later slice, if needed, must independently classify
the remaining inventory.

## Claim

Prime Builder proposes only the five evidenced test repairs below. Each change
updates a production-facing expected path or temporary fixture to the canonical
gtkb-prefixed managed skill location; no intentional negative input is changed
in this slice.

## Requirement Sufficiency

Existing requirements sufficient. The WI-5665 test-recovery objective, the
active sweep authorization, the canonical skill rename map, and the observed
selector results below define this bounded test-only implementation. No new
owner decision is requested.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- ADR-CODEX-HOOK-PARITY-FALLBACK-001
- GOV-STANDING-BACKLOG-001

## Evidence-Derived Inventory And Test Mapping

| Target path | Classification | Current selector and observed result | Canonical expected assertion | Replacement selector |
| --- | --- | --- | --- | --- |
| groundtruth-kb/tests/test_managed_registry.py | Silent false-green managed-registry expectation | test_bridge_skill_records_are_managed_for_dual_agent_profiles passed while enumerating .claude/skills/bridge paths | The managed bridge files are under .claude/skills/gtkb-bridge | Same selector must prove canonical entries and absence of retired managed entries. |
| groundtruth-kb/tests/test_upgrade_skills.py | Silent false-green upgrade fixture | test_plan_upgrade_adds_missing_bridge_skill_files_at_same_version passed while creating bridge paths | Upgrade plan and fixture create gtkb-bridge files | That selector and test_execute_creates_missing_bridge_skill_files_at_same_version prove canonical plan and materialization. |
| platform_tests/scripts/test_harness_skill_effectiveness.py | Broken canonical-registry fixture | Five selectors failed with FileNotFoundError because the fixture creates harness-capability-registry.toml while the tested code loads gtkb-harness-capability-registry.toml | Fixture creates the canonical registry filename before evaluation | test_evaluate_maps_activity_skills_to_harness_skill_evidence, test_missing_skill_projection_is_reported_as_gap, test_typed_waiver_is_distinct_from_missing_projection, test_manifest_projection_can_supply_missing_harness_subtable, and test_markdown_report_includes_summary_gaps_weak_rows_and_waivers all pass. |
| platform_tests/scripts/test_gitattributes_lf_policy.py | Silent false-green generated/scaffold path list | test_generated_and_scaffold_artifacts_resolve_to_lf passed while listing bare bridge-propose and verify paths | Generated/scaffold artifact list uses canonical gtkb-bridge-propose and gtkb-verify paths | Same selector passes and checks canonical files. |
| platform_tests/scripts/test_cross_harness_protocol_parity.py | Broken cross-harness runtime expectation | test_dispatcher_status_rules_match_prime_and_lo_bridge_boundaries failed because .claude/skills/bridge/SKILL.md does not exist | Claude, Codex, and Agent bridge skill surface references use gtkb-bridge | Same selector passes against the canonical skill paths. |

## Explicit Exclusions

- platform_tests/skills/test_bridge_propose_helper.py,
  platform_tests/scripts/test_gtkb_bridge_writer.py, and
  platform_tests/scripts/test_generate_codex_skill_adapters.py are modified in
  the worktree and are excluded. No WI-5665 hunk may be staged or attributed
  in them before their current owners resolve the modifications.
- The other twenty-one former targets are excluded as unclassified. Some may
  contain intentional parser, migration, or detection negative literals; this
  revision makes no inference about them.
- groundtruth-kb/tests/test_upgrade_skills.py::test_base_profile_no_skill_actions
  currently fails because of an unrelated baseline-audit action. It is not
  acceptance evidence for this skill-rename slice and is not changed here.

## Cross-Harness Disposition

The selected assertions cover the canonical Claude, Codex, and Agent managed
skill projections plus the shared registry fixture. No hook, adapter, runtime
configuration, or typed waiver changes are requested.

## Specification-Derived Verification Plan

    groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_managed_registry.py::test_bridge_skill_records_are_managed_for_dual_agent_profiles groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_bridge_skill_files_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_execute_creates_missing_bridge_skill_files_at_same_version platform_tests/scripts/test_harness_skill_effectiveness.py platform_tests/scripts/test_gitattributes_lf_policy.py::test_generated_and_scaffold_artifacts_resolve_to_lf platform_tests/scripts/test_cross_harness_protocol_parity.py::test_dispatcher_status_rules_match_prime_and_lo_bridge_boundaries -q --tb=short
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_upgrade_skills.py platform_tests/scripts/test_harness_skill_effectiveness.py platform_tests/scripts/test_gitattributes_lf_policy.py platform_tests/scripts/test_cross_harness_protocol_parity.py
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_upgrade_skills.py platform_tests/scripts/test_harness_skill_effectiveness.py platform_tests/scripts/test_gitattributes_lf_policy.py platform_tests/scripts/test_cross_harness_protocol_parity.py
    python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5665-skill-rename-test-recovery
    python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5665-skill-rename-test-recovery

## Acceptance Criteria

- Every declared selector proves the canonical managed path or fixture, and
  fails its pre-change stale behavior for the reason recorded above.
- No retired path remains in a production-facing expected managed artifact or
  fixture in the five declared targets.
- No dirty excluded test file, unclassified target, source file, or unrelated
  baseline-audit behavior is touched.
- The implementation report records the actual focused results and an
  immutable scoped commit before independent LO review.

## Risks And Rollback

The risk is converting an intentional negative literal. The explicit
classification limits this slice to managed-path expectations and fixtures.
Rollback is a governed revert of only the later five-file test commit.

## Owner Decisions / Input

No additional input is needed. This proposal obeys the existing PAUTH while
splitting the formerly unbounded inventory into independently reviewable
slices.

## Recommended Commit Type

test

