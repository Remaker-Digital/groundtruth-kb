# Implementation Proposal - Projects Skill + gt projects Lifecycle Commands

bridge_kind: implementation_proposal
Document: gtkb-projects-skill-001
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Work Item: WI-3259

## Claim

Implement the first-class project lifecycle surface requested by `WI-3259`: a `gt projects` CLI group with create, show, list, update, add-item, reorder, retire, and link-bridge verbs, plus matching Claude/Codex `projects` skill surfaces. The implementation should wrap the existing MemBase `projects`, `project_work_item_memberships`, `project_dependencies`, and `project_artifact_links` tables instead of creating a second backlog authority.

## Why Now

`GTKB-DETERMINISTIC-SERVICES-001` is converting repeated manual planning work into deterministic services. Projects and sub-projects are now the organizing layer above MemBase work items, but the current implementation only exposes `gt projects list` and `gt projects show`. The missing verbs force agents to keep doing manual DB writes or ad hoc scripts for routine project lifecycle work.

## Specification Links

**Blocking / directly governing:**

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` remains the authoritative bridge queue; this proposal files the governed work before implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the relevant specifications and rules before implementation approval.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification requires spec-derived tests and observed command evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - the standing backlog is the durable cross-session work authority.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` - MemBase `current_work_items` and related project tables are the canonical backlog/project data surface.
- `DCL-CONCEPT-ON-CONTACT-001` - project/sub-project/work-item terminology must stay aligned with the glossary.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - the new skill surface must be portable across Claude Code and Codex harness roles.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` - Codex skill parity must remain aligned with the Claude skill surface.

**Advisory / cross-cutting:**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive AI work is a defect; deterministic plumbing should replace repeated manual work.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive to formalize standing backlog as a DB-backed source of truth.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` - owner-approved Codex harness parity specification bundle.
- `DELIB-1564` - Loyal Opposition GO for the bridge skill unified work; useful precedent for adding a canonical Claude skill with generated Codex adapter.
- `DELIB-1565` - Loyal Opposition verification history for bridge skill unified work; useful precedent for parity adapter verification.
- `DELIB-1791` - GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH scoping review; useful background for avoiding a second backlog authority.

## Owner Decisions / Input

- Owner current-priority heartbeat on 2026-05-13 identifies `GTKB-DETERMINISTIC-SERVICES-001` as the active project and lists `WI-3259` as the next safe P1 item after the topology-deferred `WI-3265`.
- `WI-3259` was created under owner-directed umbrella project creation on 2026-05-10 and names the exact target: "Projects skill + gt projects CLI group (8 verbs: create/show/list/update/add-item/reorder/retire/link-bridge)."

No additional owner decision is required before implementation. This proposal does not create or approve a new canonical specification; it implements an already tracked deterministic-service backlog item through the bridge.

## Current Implementation Baseline

- `groundtruth-kb/src/groundtruth_kb/cli.py` already defines `gt projects list` and `gt projects show`.
- `groundtruth-kb/src/groundtruth_kb/db.py` already contains MemBase project tables and methods for `insert_project`, `list_projects`, `get_project`, `link_project_work_item`, `list_project_work_items`, `add_project_dependency`, `list_project_dependencies`, `add_project_artifact_link`, and `list_project_artifact_links`.
- No `.claude/skills/projects/SKILL.md` or `.codex/skills/projects/SKILL.md` exists.
- No `groundtruth_kb/project/lifecycle.py` service module exists yet.

## Scope

### IP-1: Project lifecycle service

Create `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` as a thin service over `KnowledgeDB` that provides typed, deterministic operations:

- `create_project`
- `show_project`
- `list_projects`
- `update_project`
- `add_project_item`
- `reorder_project_items`
- `retire_project`
- `link_bridge_thread`

The service must preserve append-only MemBase versioning. "Update" and "retire" should create new project versions by carrying forward unchanged fields. "Add item" and "reorder" should create new membership versions rather than mutating existing rows in place. `link_bridge_thread` should add an artifact link with `artifact_type="bridge_thread"` and the document slug as `artifact_ref`.

### IP-2: CLI verbs

Extend `gt projects` in `groundtruth-kb/src/groundtruth_kb/cli.py` to expose the eight verbs:

- `create`
- `show`
- `list`
- `update`
- `add-item`
- `reorder`
- `retire`
- `link-bridge`

Existing `list` and `show` behavior should remain backward compatible. New mutating verbs should require explicit `--change-reason` where practical and should emit machine-readable `--json` output for automation.

### IP-3: Skill surfaces and parity registry

Add a canonical Claude skill at `.claude/skills/projects/SKILL.md` describing the project lifecycle commands and safe usage. Add a `skill.projects` capability record to `config/agent-control/harness-capability-registry.toml`, then regenerate Codex adapters with `scripts/generate_codex_skill_adapters.py` so `.codex/skills/projects/SKILL.md` and `.codex/skills/MANIFEST.json` are generated from the canonical skill.

The skill must not redefine project/backlog terminology. It must defer to `.claude/rules/operating-model.md` and `.claude/rules/canonical-terminology.md` for the meaning of project, sub-project, work item, and backlog.

### IP-4: Backlog linkage

After implementation report verification, update `WI-3259` through MemBase work-item versioning with:

- `related_bridge_threads="gtkb-projects-skill-001"`
- `completion_evidence` citing the VERIFIED bridge version and executed test evidence
- terminal status only after Loyal Opposition VERIFIED, or by the mechanical bridge VERIFIED backlog retirement path if that reconciler applies

### IP-5: Bulk-operation visibility guard

This slice is not authorized to perform broad backlog rewrites. `reorder` is scoped to membership ordering inside one selected project, and `add-item` links one explicit work item at a time unless a later bridge-approved extension adds batch input.

If implementation discovers that any command would affect multiple projects or bulk-update work items, that operation must be split out or must emit a dry-run inventory artifact, a review packet, and a `DECISION DEFERRED` marker before any apply path. No formal-artifact-approval packet is requested by this proposal because no protected narrative artifact or owner-approved bulk backlog rewrite is in scope.

## Out Of Scope

- Replacing `current_work_items` as backlog authority.
- Adding a new project database table beyond the existing MemBase project tables.
- Bulk backlog rewrites across multiple projects or unbounded work-item sets.
- Editing protected narrative rule files under `.claude/rules/`.
- Implementing `WI-3260` bridge convenience verbs in this slice.
- Implementing `WI-3263` artifact recorder CLI in this slice.
- Changing release/deploy gates.

## Target Paths

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` - new service module.
- `groundtruth-kb/src/groundtruth_kb/cli.py` - extend `gt projects`.
- `.claude/skills/projects/SKILL.md` - new canonical skill.
- `.codex/skills/projects/SKILL.md` - generated adapter.
- `.codex/skills/MANIFEST.json` - generated adapter manifest update.
- `config/agent-control/harness-capability-registry.toml` - add `skill.projects` capability.
- `platform_tests/scripts/test_projects_cli.py` - CLI and lifecycle command tests.
- `platform_tests/scripts/test_check_harness_parity.py` or a focused adapter test - parity regression, if existing coverage is not sufficient.

## Test Plan

### Pre-implementation bridge gates

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-projects-skill-001 --content-file .gtkb-state/gtkb-projects-skill-001-draft.md`
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-projects-skill-001 --content-file .gtkb-state/gtkb-projects-skill-001-draft.md`

### Implementation tests

3. `python -m pytest platform_tests/scripts/test_projects_cli.py -q`
   - Covers create/show/list/update/add-item/reorder/retire/link-bridge behavior against a temporary MemBase database.
4. `python scripts/generate_codex_skill_adapters.py --check --update-registry`
   - Confirms the Codex skill adapter and manifest are current after generation.
5. `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q`
   - Confirms the new skill capability remains covered by harness parity checks.
6. `python -m pytest platform_tests/scripts/test_governing_specs_preserved.py -q`
   - Confirms governance/adoption surfaces still preserve required specs.

### Spec-to-test mapping

| Specification / rule | Verifying evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge proposal and later implementation report are filed through `bridge/INDEX.md`; preflight 1. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Preflight 1 and this Specification Links section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests 3-6 plus implementation-report spec-to-test mapping. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target paths all under `E:\GT-KB`; tests run from project root. |
| `GOV-STANDING-BACKLOG-001` | Test 3 verifies project operations organize existing work items without replacing backlog authority. |
| `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` | Test 3 verifies operations use MemBase project/work-item tables and append-only versioning. |
| `DCL-CONCEPT-ON-CONTACT-001` | Test/review confirms no new terminology is introduced outside existing glossary terms. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Tests 4-5 verify canonical Claude skill plus Codex adapter parity. |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` | Tests 4-5 verify Codex adapter registry and parity. |
| `.claude/rules/operating-model.md` | Test 3 and skill review verify project/backlog/work-item relationships remain aligned. |

## Acceptance Criteria

- [ ] `gt projects create/show/list/update/add-item/reorder/retire/link-bridge` exists and uses the existing MemBase project tables.
- [ ] Mutating commands preserve append-only versioning and require useful change reasons.
- [ ] `gt projects show --json` returns project, work_items, dependencies, and artifact_links.
- [ ] `gt projects link-bridge` records a bridge-thread artifact link without editing `bridge/INDEX.md`.
- [ ] `.claude/skills/projects/SKILL.md` exists and `.codex/skills/projects/SKILL.md` is generated from it.
- [ ] Harness capability registry includes `skill.projects` and adapter check passes.
- [ ] Spec-derived tests pass and are reported in the post-implementation bridge report.
- [ ] Loyal Opposition verifies the post-implementation report.

## Risk + Rollback

### Risks

- **R1 (Medium):** Scope expands into general backlog replacement. Mitigation: service must wrap existing MemBase project and work-item tables only; no new authority table.
- **R2 (Medium):** Reorder behavior could accidentally mutate current membership rows. Mitigation: append-only membership version tests.
- **R3 (Low):** Skill adapter drift if registry entry or generation is incomplete. Mitigation: run generator and harness parity tests.
- **R4 (Low):** CLI semantics could collide with existing `gt project` scaffold commands. Mitigation: keep plural `gt projects` for MemBase project lifecycle and leave singular `gt project` scaffold/doctor/upgrade commands unchanged.

### Rollback

Revert the implementation commit. The existing `gt projects list/show` behavior can remain if the revert is scoped, but a full revert restores the current two-verb surface.

## Prefiling Preflight Results

Ran against content file `E:\GT-KB\.gtkb-state\gtkb-projects-skill-001-draft.md` before live filing:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-projects-skill-001 --content-file E:\GT-KB\.gtkb-state\gtkb-projects-skill-001-draft.md`
  - PASS; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-projects-skill-001 --content-file E:\GT-KB\.gtkb-state\gtkb-projects-skill-001-draft.md`
  - PASS; exit 0; evidence gaps in must-apply clauses: 0; blocking gaps: 0.

## Recommended Commit Type

`feat:` - adds a deterministic project lifecycle service, CLI verbs, and harness skill surface.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
