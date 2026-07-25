REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T15-11-34Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal — WI-5665 clean five-test skill-rename recovery

bridge_kind: prime_proposal
Document: gtkb-wi5665-skill-rename-test-recovery
Version: 005
Responds to: bridge/gtkb-wi5665-skill-rename-test-recovery-004.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5665

target_paths: ["groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_upgrade_skills.py", "platform_tests/scripts/test_harness_skill_effectiveness.py", "platform_tests/scripts/test_gitattributes_lf_policy.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py"]

implementation_scope: tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Preserve the accepted five-module, evidence-backed test-only recovery slice.
It repairs stale canonical managed-path expectations and a broken canonical
registry fixture without reopening the unclassified 29-path inventory or
absorbing any dirty excluded test file.

## Claim

All five declared paths were clean at inspection. The former 29-target
proposal is superseded for this slice: only the five classified failures or
false-greens below may change after fresh GO and an implementation claim.

## Requirement Sufficiency

Existing requirements sufficient. The WI-5665 objective, active PAUTH,
DELIB-202667193 sweep authority, and DELIB-202667194 skill-rename-only
isolation define this bounded test recovery.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- ADR-CODEX-HOOK-PARITY-FALLBACK-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001

## Classified Inventory And Test Map

| Target | Classification and observed pre-change result | Post-change assertion |
| --- | --- | --- |
| groundtruth-kb/tests/test_managed_registry.py | false-green bridge managed records use retired bare paths | test_bridge_skill_records_are_managed_for_dual_agent_profiles asserts gtkb-bridge and no retired managed path. |
| groundtruth-kb/tests/test_upgrade_skills.py | false-green upgrade fixtures materialize bare bridge paths | bridge-propose, spec-intake, and bridge plan/execute selectors materialize gtkb-prefixed paths. |
| platform_tests/scripts/test_harness_skill_effectiveness.py | five selectors fail because the fixture creates harness-capability-registry.toml while code reads gtkb-harness-capability-registry.toml | fixture creates the canonical registry file and all five selectors pass. |
| platform_tests/scripts/test_gitattributes_lf_policy.py | false-green generated/scaffold list contains retired bridge-propose/verify paths | LF-policy selector checks canonical gtkb paths. |
| platform_tests/scripts/test_cross_harness_protocol_parity.py | dispatcher boundary selector fails trying retired .claude/skills/bridge/SKILL.md | Claude, Codex, and Agent references use gtkb-bridge and selector passes. |

## Lifecycle And Artifact-Governance Disposition

- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001: retain the version-002 NO-GO,
  five-file split, test results, and later immutable commit as linked artifacts;
  do not collapse them into a broad test sweep.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001: this REVISED lifecycle transition
  supersedes the rejected broad scope, while later GO/report/VERIFIED remain
  distinct required states.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001: preserve the dirty excluded paths as
  separate evidence; do not attribute their hunks to the clean recovery.

## Explicit Exclusions

- platform_tests/skills/test_bridge_propose_helper.py,
  platform_tests/scripts/test_gtkb_bridge_writer.py, and
  platform_tests/scripts/test_generate_codex_skill_adapters.py remain dirty,
  unowned, and excluded.
- Every other former target remains unclassified, including intentional
  legacy-input parser/detector cases.
- The unrelated baseline-audit failure in
  test_base_profile_no_skill_actions is excluded from acceptance.

## Specification-Derived Verification Plan

    groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_managed_registry.py::test_bridge_skill_records_are_managed_for_dual_agent_profiles groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_bridge_skill_files_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_execute_creates_missing_bridge_skill_files_at_same_version platform_tests/scripts/test_harness_skill_effectiveness.py platform_tests/scripts/test_gitattributes_lf_policy.py::test_generated_and_scaffold_artifacts_resolve_to_lf platform_tests/scripts/test_cross_harness_protocol_parity.py::test_dispatcher_status_rules_match_prime_and_lo_bridge_boundaries -q --tb=short
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check <five declared targets>
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <five declared targets>
    git diff --check -- <five declared targets>
    python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5665-skill-rename-test-recovery
    python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5665-skill-rename-test-recovery

## Acceptance Criteria

- The five declared test modules contain canonical managed expectations and
  fixtures; their focused selectors pass.
- No dirty excluded test, unclassified legacy negative, source file, or
  baseline-audit behavior changes.
- The implementation report records actual results and an immutable commit
  containing only these five paths before independent LO review.

## Cross-Harness Disposition

The canonical test assertions cover Claude, Codex, and Agent projections plus
the shared capability-registry fixture. No hook, adapter generation, runtime,
or typed waiver behavior is changed.

## Risks And Rollback

The risk is rewriting an intentional negative literal. The exact classification
and five-file baseline constrain the slice. Rollback is a governed revert of
only the later scoped test commit.

## Owner Decisions / Input

No additional owner input is required. DELIB-202667193 and DELIB-202667194
supply sweep authority and skill-rename-only isolation.

## Recommended Commit Type

test

