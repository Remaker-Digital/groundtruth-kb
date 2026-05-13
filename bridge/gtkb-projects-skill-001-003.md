REVISED

# Implementation Proposal Revision - Projects Skill + gt projects Lifecycle Commands

bridge_kind: implementation_proposal
Document: gtkb-projects-skill-001
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Work Item: WI-3259
Responds To: bridge/gtkb-projects-skill-001-002.md
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/project/__init__.py", "groundtruth-kb/src/groundtruth_kb/cli.py", ".claude/skills/projects/SKILL.md", ".codex/skills/projects/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_projects_cli.py", "platform_tests/scripts/test_projects_skill_adapter.py", "platform_tests/scripts/test_check_harness_parity.py"]

## Revision Claim

This revision keeps the substantive scope of `bridge/gtkb-projects-skill-001-001.md` and addresses the sole blocking finding in `bridge/gtkb-projects-skill-001-002.md`: the proposal now includes gate-readable `target_paths` metadata, an exact `## Requirement Sufficiency` section, and an exact `## Specification-Derived Verification Plan` section so a future GO can produce a local implementation authorization packet with `python scripts/implementation_authorization.py begin --bridge-id gtkb-projects-skill-001`.

## Why Now

`GTKB-DETERMINISTIC-SERVICES-001` is converting repeated manual planning work into deterministic services. Projects and sub-projects are now the organizing layer above MemBase work items, but the current implementation only exposes `gt projects list` and `gt projects show`. The missing verbs force agents to keep doing manual DB writes or ad hoc scripts for routine project lifecycle work.

## Specification Links

**Blocking / directly governing:**

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` remains the authoritative bridge queue; this revision is filed as append-only bridge audit trail.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the relevant specifications and rules before implementation approval.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification requires spec-derived tests and observed command evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are under `E:/GT-KB`.
- `GOV-STANDING-BACKLOG-001` - the standing backlog is the durable cross-session work authority.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` - MemBase `current_work_items` and related project tables are the canonical backlog/project data surface.
- `DCL-CONCEPT-ON-CONTACT-001` - project/sub-project/work-item terminology must stay aligned with the glossary.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - the new skill surface must be portable across Claude Code and Codex harness roles.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` - Codex skill parity must remain aligned with the Claude skill surface.
- `.claude/rules/file-bridge-protocol.md` - requires target path metadata, requirement sufficiency, and spec-derived verification before protected implementation work.
- `.claude/rules/codex-review-gate.md` - requires a GO bridge entry and implementation-start authorization before protected changes.

**Advisory / cross-cutting:**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/canonical-terminology.md`

## Prior Deliberations

This revision carries forward the prior deliberation context from the initial proposal and the `NO-GO` review:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive AI procedure should become deterministic service-mediated infrastructure.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - supports MemBase-backed backlog and project authority.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` - supports generated Codex adapter parity from canonical Claude surfaces.
- `DELIB-1564` and `DELIB-1565` - bridge-skill unified precedent for canonical Claude skill plus generated Codex adapter review and verification.
- `DELIB-1791` - backlog-source review history reinforcing that this work must not create a second backlog authority.

Additional revision-time DA checks on 2026-05-13 searched for `WI-3259 projects skill gt projects lifecycle`, `implementation authorization target_paths Requirement Sufficiency project lifecycle`, and direct `WI-3259` linkage. No deliberation directly linked to `WI-3259` was found, and no search result contradicted the proposal direction. `INTAKE-67f93676` is relevant recent intake context for tight specification/test/implementation coupling, but it remains intake context rather than a governing approved specification.

## Owner Decisions / Input

- Owner current-priority heartbeat on 2026-05-13 identifies `GTKB-DETERMINISTIC-SERVICES-001` as the active project and lists `WI-3259` as the next safe P1 item after the topology-deferred `WI-3265`.
- `WI-3259` was created under owner-directed umbrella project creation on 2026-05-10 and names the exact target: "Projects skill + gt projects CLI group (8 verbs: create/show/list/update/add-item/reorder/retire/link-bridge)."
- This revision does not introduce new owner-decision scope. It corrects implementation-start metadata in response to Loyal Opposition finding F1.

## Requirement Sufficiency

Existing requirements sufficient.

The linked requirements and durable records above are sufficient for this implementation slice because the work item already names the desired eight verbs, the operating model defines project/sub-project/work-item/backlog terminology, the MemBase project tables already exist, and the bridge/governance rules define the implementation authorization and verification surfaces. No new or revised formal requirement is needed before implementation of this scoped CLI, service, skill, and test work.

## Current Implementation Baseline

- `groundtruth-kb/src/groundtruth_kb/cli.py` already defines `gt projects list` and `gt projects show`.
- `groundtruth-kb/src/groundtruth_kb/db.py` already contains MemBase project tables and methods for `insert_project`, `list_projects`, `get_project`, `link_project_work_item`, `list_project_work_items`, `add_project_dependency`, `list_project_dependencies`, `add_project_artifact_link`, and `list_project_artifact_links`.
- No `.claude/skills/projects/SKILL.md` or `.codex/skills/projects/SKILL.md` exists.
- No `groundtruth_kb/project/lifecycle.py` service module exists yet.

## Findings Addressed

### Finding F1 - Implementation-start metadata is missing or not in the accepted form

Response:

- Added exact `target_paths: [...]` metadata near the top of this revision using normalized in-root paths.
- Added exact `## Requirement Sufficiency` with the operative state `Existing requirements sufficient`.
- Added exact `## Specification-Derived Verification Plan` with spec-to-test mapping and command evidence expectations.
- Added `## Files Expected To Change` as a human-readable mirror of the same target path scope for review clarity.

Expected parser disposition after a future GO:

- `extract_target_paths(...)` can read the JSON metadata list.
- `requirement_sufficiency_state(...)` can read `Existing requirements sufficient`.
- `has_spec_derived_verification(...)` can read this revision's `## Specification-Derived Verification Plan` section.

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

The service must preserve append-only MemBase versioning. `update_project` and `retire_project` should create new project versions by carrying forward unchanged fields. `add_project_item` and `reorder_project_items` should create new membership versions rather than mutating existing rows in place. `link_bridge_thread` should add an artifact link with `artifact_type="bridge_thread"` and the document slug as `artifact_ref`.

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

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` - new service module.
- `groundtruth-kb/src/groundtruth_kb/project/__init__.py` - package export only if needed by the service or tests.
- `groundtruth-kb/src/groundtruth_kb/cli.py` - extend `gt projects`.
- `.claude/skills/projects/SKILL.md` - new canonical skill.
- `.codex/skills/projects/SKILL.md` - generated adapter.
- `.codex/skills/MANIFEST.json` - generated adapter manifest update.
- `config/agent-control/harness-capability-registry.toml` - add `skill.projects` capability.
- `platform_tests/scripts/test_projects_cli.py` - CLI and lifecycle command tests.
- `platform_tests/scripts/test_projects_skill_adapter.py` - focused skill adapter/parity test if existing parity coverage does not assert the new surface.
- `platform_tests/scripts/test_check_harness_parity.py` - parity regression update only if needed by the registry change.

## Specification-Derived Verification Plan

### Commands

1. `python -m pytest platform_tests/scripts/test_projects_cli.py -q`
2. `python scripts/generate_codex_skill_adapters.py --check --update-registry`
3. `python -m pytest platform_tests/scripts/test_projects_skill_adapter.py -q`
4. `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q`
5. `python -m pytest platform_tests/scripts/test_governing_specs_preserved.py -q`

If implementation proves an existing parity/governance test already covers the new skill surface, the implementation report may omit a redundant new test file, but it must explicitly map the executed existing test to the relevant spec rows.

### Spec-to-test mapping

| Specification / rule | Verifying evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This REVISED bridge proposal and later implementation report are filed through `bridge/INDEX.md`; bridge preflights run before filing and review. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight and this `## Specification Links` section show required governing specs are cited. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Commands 1-5 plus the implementation-report mapping must show each linked specification has executed verification evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target paths all stay under `E:/GT-KB`; tests run from project root and no live dependency uses an external checkout. |
| `GOV-STANDING-BACKLOG-001` | Command 1 verifies project operations organize existing work items without replacing backlog authority or performing broad backlog rewrites. |
| `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` | Command 1 verifies operations use MemBase project/work-item tables and append-only versioning. |
| `DCL-CONCEPT-ON-CONTACT-001` | Skill and CLI review in Commands 1-4 verify project/backlog/work-item terminology stays aligned to the glossary. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Commands 2-4 verify canonical Claude skill plus Codex adapter parity. |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` | Commands 2-4 verify Codex adapter registry and parity. |
| `.claude/rules/operating-model.md` | Command 1 and skill review verify project/backlog/work-item relationships remain aligned. |
| `.claude/rules/file-bridge-protocol.md` | Bridge helper filing and preflight evidence verify append-only `REVISED` filing and implementation-start metadata. |
| `.claude/rules/codex-review-gate.md` | A later GO plus `implementation_authorization.py begin` packet is required before protected implementation edits. |

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
- **R5 (Low):** Implementation-start metadata could drift from the parser. Mitigation: this revision uses the exact `target_paths`, `## Requirement Sufficiency`, and `## Specification-Derived Verification Plan` surfaces recognized by `scripts/implementation_authorization.py`.

### Rollback

Revert the implementation commit. The existing `gt projects list/show` behavior can remain if the revert is scoped, but a full revert restores the current two-verb surface.

## Pre-Filing Preflight Results

Ran against content file `E:\GT-KB\.gtkb-state\bridge-revisions\drafts\gtkb-projects-skill-001-003.md` before live filing:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-projects-skill-001 --content-file E:\GT-KB\.gtkb-state\bridge-revisions\drafts\gtkb-projects-skill-001-003.md`
  - PASS; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-projects-skill-001 --content-file E:\GT-KB\.gtkb-state\bridge-revisions\drafts\gtkb-projects-skill-001-003.md`
  - PASS; exit 0; evidence gaps in must-apply clauses: 0; blocking gaps: 0.

## Recommended Commit Type

`feat:` - adds a deterministic project lifecycle service, CLI verbs, and harness skill surface.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
