NEW
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex Desktop default reasoning

# Post-Implementation Report - Tier A Managed-Skill Adoption Apply

bridge_kind: implementation_report
Document: gtkb-tier-a-managed-skill-adoption-apply
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Implemented from GO: `bridge/gtkb-tier-a-managed-skill-adoption-apply-004.md`
Approved proposal: `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md`
Implementation authorization packet: `sha256:079707d13e72905eb21a40ccca08c0f58268fa21fa002e389023de6eec370830`

## Implementation Claim

Implemented the approved GTKB-GOV-001 Tier A managed-skill adoption slice by adding the canonical `bridge` skill to the existing single-source managed-artifact registry and template tree. The registry now manages `.claude/skills/bridge/SKILL.md` plus the four bridge helper modules for dual-agent and dual-agent-webapp profiles through the existing scaffold and upgrade lifecycle.

No parallel registry, parallel manifest, or new apply CLI was introduced. The implementation extends `groundtruth-kb/templates/managed-artifacts.toml`, uses the existing `groundtruth_kb.project.managed_registry` loader and scaffold/upgrade consumers, and adds targeted tests for registry, scaffold, upgrade, doctor parity, and no-parallel-manifest behavior.

## Files Changed In This Implementation Scope

- `groundtruth-kb/templates/managed-artifacts.toml` - added five `class = "skill"` records for the managed `bridge` skill and helpers; updated registry count comments to the live 66-record manifest.
- `groundtruth-kb/templates/skills/bridge/SKILL.md` - new managed template copied from the canonical `.claude/skills/bridge/SKILL.md`.
- `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py` - new managed helper template.
- `groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py` - new managed helper template.
- `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` - new managed helper template.
- `groundtruth-kb/templates/skills/bridge/helpers/show_thread_bridge.py` - new managed helper template.
- `groundtruth-kb/tests/test_managed_registry.py` - updated registry totals/class counts and added a dual-agent scaffold/upgrade registry assertion for the bridge skill records.
- `groundtruth-kb/tests/test_scaffold_skills.py` - added an end-to-end scaffold assertion that dual-agent projects receive the bridge skill and all four helpers.
- `groundtruth-kb/tests/test_upgrade_skills.py` - added plan/execute upgrade assertions that missing bridge skill files are repaired at the current scaffold version.

Bridge filing also adds this post-implementation report as `bridge/gtkb-tier-a-managed-skill-adoption-apply-005.md` and updates `bridge/INDEX.md` with a new `NEW:` line for Loyal Opposition verification.

## Existing Dirty Target Note

Before this slice began, `groundtruth-kb/templates/managed-artifacts.toml` was already dirty with `hook.code-quality-baseline-proposal-check`, taking the live registry baseline to 61 records (`21` hooks, `6` skills). I did not revert or rewrite that existing work. This implementation adds five bridge-skill records on top of the live baseline, yielding the tested 66-record manifest (`21` hooks, `11` rules, `11` skills, `3` files, `16` settings-hook-registrations, `4` gitignore-patterns).

## Specification Links

- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - Tier A managed-skill adoption is the adoption capability this work lands.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the managed-artifact registry is the artifact-oriented source of truth for adopter scaffolding and upgrade.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governs the proposal, implementation report, and INDEX transition.
- `SPEC-AUQ-POLICY-ENGINE-001` - the registry/upgrade path is deterministic policy-engine-style behavior rather than an LLM-mediated apply surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files are in-root under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the approved proposal's governing specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each approved behavior to executed tests.
- `GOV-STANDING-BACKLOG-001` - GTKB-GOV-001 is the tracked work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the work item, bridge thread, registry records, templates, and tests form the durable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - adding the managed skill changes scaffold, upgrade, and doctor lifecycle triggers for adopter artifacts.

## Owner Decisions / Input

No new owner decision was required. This implementation carries forward `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`, which authorized the `PROJECT-GTKB-ADOPTER-EXPERIENCE` batch containing `GTKB-GOV-001`.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-approved batch authorization including `GTKB-GOV-001`.
- `DELIB-0852` / `DELIB-1243` - prior Tier A adoption apply thread history; relevant to the corrected premise in the approved revision.
- `DELIB-0724` / `DELIB-1204` - managed-artifact registry thread establishing the single-source registry model this implementation extends.
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md` - approved revised implementation proposal.
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-004.md` - Loyal Opposition GO verdict authorizing this implementation.

## Specification-Derived Verification Plan

| Specification / behavior | Test or command | Observed result |
|---|---|---|
| Registry remains the single source of truth and parses at the new current count | `test_registry_total_matches_current_manifest`, `test_registry_class_counts_match_proposal` | PASS in targeted suite |
| Bridge skill records are scaffolded and upgrade-managed for dual-agent profiles | `test_bridge_skill_records_are_managed_for_dual_agent_profiles` | PASS in targeted suite |
| Dual-agent scaffold copies bridge SKILL.md plus all four helpers | `test_dual_agent_project_has_bridge_skill` | PASS in targeted suite |
| Upgrade planner repairs missing bridge skill files at current scaffold version | `test_plan_upgrade_adds_missing_bridge_skill_files_at_same_version` | PASS in targeted suite |
| Upgrade execution copies bridge skill files to disk | `test_execute_creates_missing_bridge_skill_files_at_same_version` | PASS in targeted suite |
| No parallel managed manifest is introduced | `python -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb\tests\test_no_parallel_manifests.py -q --tb=short` | 1 passed |
| Doctor parity remains green | `python -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb\tests\test_doctor.py -q --tb=short` | 37 passed |
| Registry/scaffold/upgrade suite | `python -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_upgrade_skills.py groundtruth-kb\tests\test_scaffold_skills.py -q --tb=short` | 47 passed |
| Source lint | `python -m ruff check groundtruth-kb\templates\skills\bridge\helpers\scan_bridge.py groundtruth-kb\templates\skills\bridge\helpers\revise_bridge.py groundtruth-kb\templates\skills\bridge\helpers\impl_report_bridge.py groundtruth-kb\templates\skills\bridge\helpers\show_thread_bridge.py groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_upgrade_skills.py groundtruth-kb\tests\test_scaffold_skills.py` | All checks passed |
| Formatting | `python -m ruff format --check groundtruth-kb\templates\skills\bridge\helpers\scan_bridge.py groundtruth-kb\templates\skills\bridge\helpers\revise_bridge.py groundtruth-kb\templates\skills\bridge\helpers\impl_report_bridge.py groundtruth-kb\templates\skills\bridge\helpers\show_thread_bridge.py groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_upgrade_skills.py groundtruth-kb\tests\test_scaffold_skills.py` | 7 files already formatted |

## Commands Run

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-tier-a-managed-skill-adoption-apply` - authorization packet issued.
- `python -m ruff format groundtruth-kb\templates\skills\bridge\helpers\scan_bridge.py groundtruth-kb\templates\skills\bridge\helpers\revise_bridge.py groundtruth-kb\templates\skills\bridge\helpers\impl_report_bridge.py groundtruth-kb\templates\skills\bridge\helpers\show_thread_bridge.py groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_upgrade_skills.py groundtruth-kb\tests\test_scaffold_skills.py` - formatted changed Python files. The formatter reported a non-blocking Ruff cache write warning (`Access is denied`) once while still exiting 0.
- `python -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_upgrade_skills.py groundtruth-kb\tests\test_scaffold_skills.py -q --tb=short` - 47 passed.
- `python -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb\tests\test_doctor.py -q --tb=short` - 37 passed.
- `python -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb\tests\test_no_parallel_manifests.py -q --tb=short` - 1 passed.
- `python -m ruff check groundtruth-kb\templates\skills\bridge\helpers\scan_bridge.py groundtruth-kb\templates\skills\bridge\helpers\revise_bridge.py groundtruth-kb\templates\skills\bridge\helpers\impl_report_bridge.py groundtruth-kb\templates\skills\bridge\helpers\show_thread_bridge.py groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_upgrade_skills.py groundtruth-kb\tests\test_scaffold_skills.py` - all checks passed.
- `python -m ruff format --check groundtruth-kb\templates\skills\bridge\helpers\scan_bridge.py groundtruth-kb\templates\skills\bridge\helpers\revise_bridge.py groundtruth-kb\templates\skills\bridge\helpers\impl_report_bridge.py groundtruth-kb\templates\skills\bridge\helpers\show_thread_bridge.py groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_upgrade_skills.py groundtruth-kb\tests\test_scaffold_skills.py` - 7 files already formatted.
- Python registry sanity script using `groundtruth_kb.project.managed_registry._load_all_artifacts()` - observed 66 registry records with class counts `{'hook': 21, 'rule': 11, 'skill': 11, 'settings-hook-registration': 16, 'gitignore-pattern': 4, 'file': 3}`.

## Observed Results

```text
47 passed in 10.94s
37 passed in 3.00s
1 passed in 0.59s
All checks passed!
7 files already formatted
```

Registry sanity output:

```text
66
{'hook': 21, 'rule': 11, 'skill': 11, 'settings-hook-registration': 16, 'gitignore-pattern': 4, 'file': 3}
```

## Acceptance Criteria Status

1. The bridge skill template directory exists at `groundtruth-kb/templates/skills/bridge/`.
2. The template contains `SKILL.md` and the four approved helpers: `scan_bridge.py`, `revise_bridge.py`, `impl_report_bridge.py`, and `show_thread_bridge.py`.
3. `groundtruth-kb/templates/managed-artifacts.toml` includes five new `class = "skill"` records for those files, with dual-agent and dual-agent-webapp scaffold/upgrade profiles.
4. No parallel registry, parallel manifest, or `gt adoption apply` CLI was introduced.
5. Registry, scaffold, upgrade, no-parallel-manifest, and doctor tests pass.
6. `ruff check` and `ruff format --check` pass on the changed Python/test files.
7. Both bridge preflights will be run against this `-005` report after filing.

## Risks / Residual Notes

- The bridge helper templates are copied from the canonical `.claude/skills/bridge` implementation, then lint-cleaned in the template tree. Future canonical/template drift should be handled by a dedicated synchronization check if this pattern expands.
- This slice intentionally does not manage `proposal-review` or `send-review`, matching the GO watch item. Those skills still need separate normalization before becoming adopter-generic Tier A artifacts.
- Rollback path: remove the five `skill.bridge.*` records, remove `groundtruth-kb/templates/skills/bridge/`, and remove the bridge-skill-specific test assertions. Bridge audit files remain append-only.

## Recommended Commit Type

`feat:` - adds the bridge skill to the managed artifact scaffold/upgrade surface with regression coverage.
