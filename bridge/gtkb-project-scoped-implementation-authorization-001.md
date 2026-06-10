# Implementation Proposal - Project-Scoped Implementation Authorization + Automatic Spec Backlog Intake

bridge_kind: prime_proposal
Document: gtkb-project-scoped-implementation-authorization
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Work Item: new MemBase work item to be created from `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`
target_paths: ["groundtruth.db", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/intake.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/project/authorization.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "scripts/bridge_applicability_preflight.py", ".claude/rules/codex-review-gate.md", ".claude/rules/file-bridge-protocol.md", ".claude/rules/canonical-terminology.md", ".claude/skills/projects/SKILL.md", ".claude/skills/spec-intake/SKILL.md", ".codex/skills/projects/SKILL.md", ".codex/skills/spec-intake/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", ".groundtruth/formal-artifact-approvals/**", "platform_tests/scripts/test_project_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/groundtruth_kb/test_spec_auto_backlog.py", "platform_tests/scripts/test_projects_cli.py", "platform_tests/scripts/test_check_harness_parity.py", "platform_tests/scripts/test_governing_specs_preserved.py"]

## Claim

Implement project-scoped implementation authorization and automatic backlog intake for unmet implementation-bearing specifications.

The owner should be able to authorize a bounded project once, then allow Prime Builder to produce and execute implementation proposals within that project without asking for owner approval on every individual proposal. This must not weaken Loyal Opposition review, bridge `GO`, target-path scoping, specification-derived tests, implementation reports, or verification.

When a new unmet specification is confirmed and the spec is implementation-bearing, GT-KB should automatically create or link a canonical MemBase work item. If the spec explicitly fits an existing active project, the work item should attach to that project. If it does not fit any existing project deterministically, the work item should remain in an explicit unassigned implementation-intake state rather than causing GT-KB to invent a project.

## Why Now

The current process correctly prevents uncontrolled implementation, but the authorization unit is too small. Requiring owner approval for every implementation proposal creates repeated decision overhead when the owner has already approved a coherent project. The result is avoidable friction and an opportunity for memory drift: agents must remember which work is truly authorized instead of reading a durable project authorization record.

This proposal tightens the process by making owner intent first-class in MemBase, keeping project/work/spec relationships fresh, and preserving the proposal-level review mechanics that catch recall and interpretation errors.

## Specification Links

**Blocking / directly governing:**

- `GOV-FILE-BRIDGE-AUTHORITY-001` - live `bridge/INDEX.md` remains the authoritative bridge queue; this proposal files the governed work before implementation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain inside the active GT-KB project root and platform/application boundary.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the relevant existing governing specs and names new specs to be created from the owner decision before code semantics depend on them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification requires created or identified tests derived from the linked specs and proposed specs.
- `GOV-STANDING-BACKLOG-001` - the standing backlog is the durable cross-session work authority.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` - MemBase is the canonical DB-backed backlog/project authority.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` - backlog/work-item fields and append-only versioning must remain schema-governed.
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - backlog work authority persists across sessions and must not be bypassed.
- `GOV-12` - work item creation triggers test creation.
- `SPEC-INTAKE-c9e997` - GT-KB extracts specifications from conversation in-session; this proposal closes the downstream gap after confirmation.
- `SPEC-INTAKE-2485e9` - spec creation/update events must be visible to the owner; automatic backlog intake must surface its effects.
- `GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001` - owner input can be formalized into specs through the governed path.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` - capture and confirmation effects must be visible, not silent.
- `DCL-SPEC-DA-CITATION-MANDATORY-001` - new specifications must have their originating DA evidence preserved.
- `DCL-SPEC-RELEVANCE-CLOSURE-001` - bridge proposal spec linkage must be relevance-complete.
- `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001` - spec/test/implementation linkage must be complete or explicitly tracked incomplete.

**Advisory / cross-cutting:**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`

## Prior Deliberations

- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` - owner decision approving project-scoped implementation authorization, automatic backlog intake for unmet implementation-bearing specs, deterministic project attachment when a spec fits an active project, and no bypass of proposal-level bridge review.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive AI judgment work should be converted to deterministic services where practical.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive to formalize backlog authority in MemBase.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - backlog/work-item authority pivot to MemBase current work items.
- `DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION` - recent owner authorization pattern for scoped spec creation while preserving governance boundaries.
- `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE` - future-work candidates flow to MemBase backlog and do not become implementation approval without owner/governance approval.

## Owner Decisions / Input

- On 2026-05-13, the owner agreed with the clean design direction: project-scoped owner authorization should exist, but proposal-level bridge review and implementation-start controls should remain.
- The owner stated that when an as-yet unmet specification is added, it should automatically be added to the backlog if it is functional or otherwise implementation-bearing rather than an ADR/DCL-only constraint.
- The owner stated that if the new specification fits an existing project, a new project may not be required.
- The owner asked that this deliberation be recorded in the Deliberation Archive. It has been recorded as `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`.

No additional owner decision is required before this proposal can be reviewed. Any later production deployment, credential lifecycle action, destructive cleanup, or expansion beyond the scope below still requires the normal separate approval path.

## Requirement Sufficiency

Existing requirements are sufficient to justify filing this implementation proposal and beginning formalization work because the owner decision is now preserved in the DA and the existing GT-KB specs already govern bridge authority, backlog authority, spec intake, work-item creation, DA citation, and spec/test/implementation triad completeness.

However, the new behavior is substantial enough that the implementation must create dedicated MemBase specs before source-code semantics depend on it. IP-1 therefore formalizes the owner decision into new specs and a new work item first. Source/config/test changes in IP-2 and later must cite those newly created specs in the implementation report and in any revised bridge packet if Loyal Opposition requires a revision.

## Current Implementation Baseline

- This bridge file resides under `E:/GT-KB/bridge/`, and every proposed `target_paths` entry is in-root under the active `E:/GT-KB` project root.
- `groundtruth-kb/src/groundtruth_kb/db.py` already has append-only `projects`, `project_work_item_memberships`, `project_dependencies`, and `project_artifact_links` tables plus current-state views. It does not have a project authorization table or current authorization view.
- The `projects` skill currently states that projects organize known work and do not replace `current_work_items` or create a second backlog authority. It does not define implementation authorization.
- `groundtruth-kb/src/groundtruth_kb/intake.py` confirmation creates a spec and a confirmation deliberation, but does not automatically create or link a work item for unmet implementation-bearing specs.
- `groundtruth-kb/src/groundtruth_kb/db.py` work items already support `source_spec_id`, `related_deliberation_ids`, `related_spec_ids_at_creation`, `related_bridge_threads`, project compatibility fields, dependencies, acceptance summaries, and completion evidence.
- `scripts/implementation_authorization.py` and `scripts/implementation_start_gate.py` are proposal-scoped. They validate a latest bridge `GO` and target paths, but they do not know whether a proposal is covered by an owner-authorized project.
- `bridge_applicability_preflight.py` checks relevance completeness through rules and target paths, but does not validate project authorization coverage.

## Proposed New Specs And Work Item

IP-1 must create these MemBase records from `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` before implementing runtime behavior:

1. `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped authorization is a bounded owner approval source, not a replacement for bridge review.
2. `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - project authorization records must name project id, owner-decision DA id, status, scope, included/excluded work classes, allowed mutation classes, forbidden operations, optional expiration/supersession, and audit evidence.
3. `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001` - confirming a new unmet implementation-bearing spec creates or links a canonical work item.
4. `SPEC-PROJECT-FIT-AUTO-ATTACHMENT-001` - auto-created work items attach to an existing active project only through deterministic fit evidence; otherwise they remain in unassigned implementation intake.
5. `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization must not bypass Loyal Opposition review, bridge `GO`, target-path authorization packets, spec-derived tests, or post-implementation verification.
6. New work item: `Implement project-scoped authorization and automatic spec backlog intake`, with `source_spec_id` pointing at the primary new governance/spec record, `related_deliberation_ids` including `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`, and `related_bridge_threads` including this bridge document.

If existing IDs conflict, the implementation may choose fresh IDs with the same semantic titles and must record the change in the implementation report.

## Scope

### IP-1: Formalize governing records

Create the new MemBase specs and work item listed above. Each new spec must cite `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` either directly in DA linkage or in source/metadata fields available to current MemBase. The implementation report must list the created IDs, versions, types, statuses, and change reasons.

This phase may also add a project artifact link from any active project selected for this governance work to the bridge thread. It must not auto-create a project for this proposal unless an existing approved project is explicitly selected by deterministic current-state evidence.

### IP-2: Project authorization data model

Add first-class append-only project authorization storage in MemBase. Preferred shape:

- `project_authorizations` table with `id`, `version`, `project_id`, `status`, `authorization_name`, `owner_decision_deliberation_id`, `scope_summary`, `allowed_mutation_classes`, `forbidden_operations`, `included_work_item_ids`, `excluded_work_item_ids`, `included_spec_ids`, `excluded_spec_ids`, `expires_at`, `supersedes`, `superseded_by`, `changed_by`, `changed_at`, and `change_reason`.
- `current_project_authorizations` view using max-version projection.
- `KnowledgeDB` helpers for insert/update/list/get.
- validation that the target project exists and the owner decision deliberation exists.

The implementation may instead use `project_artifact_links` only if Loyal Opposition accepts a revised proposal explaining why a dedicated table is unnecessary. The default design is a dedicated append-only table because authorization has lifecycle and safety semantics, not just artifact linkage.

### IP-3: Project authorization CLI and service surface

Extend `gt projects` with deterministic authorization commands, likely:

- `gt projects authorize <PROJECT-ID> --owner-decision <DELIB-ID> --name <text> --scope <text> --allowed-mutation <class> --forbid <operation> --change-reason <reason>`
- `gt projects authorizations <PROJECT-ID> --json`
- `gt projects revoke-authorization <AUTH-ID> --change-reason <reason>` or `gt projects update-authorization <AUTH-ID> --status revoked --change-reason <reason>`

`gt projects show --json` should include active authorizations or a stable summary so agents can read project authority without extra ad hoc SQL.

### IP-4: Proposal and implementation-start integration

Update proposal review/implementation-start mechanics so proposals may include a project authorization reference, for example:

```text
Project Authorization: PAUTH-...
Project: PROJECT-...
```

The mechanical checks must enforce:

- the authorization exists, is current, active, and not expired;
- the authorization points to an existing project;
- the proposal's work item is a member of the project or is explicitly included by the authorization envelope;
- target paths remain governed by the bridge proposal, not by the project authorization;
- bridge `GO` remains mandatory;
- formal artifact approval gates remain mandatory;
- missing or stale project authorization blocks the claim that no further owner approval is required, but does not block a proposal from requesting owner approval through the normal path.

`scripts/implementation_authorization.py begin` should record the project authorization id in the local packet when present, and `scripts/implementation_start_gate.py` should continue to enforce proposal target paths as the narrow write boundary.

### IP-5: Automatic backlog intake for implementation-bearing specs

Extend the spec confirmation path so a newly confirmed, unmet, implementation-bearing spec creates or links a canonical work item.

Definitions:

- "unmet" means the current spec status is `specified` and there is no active/current work item already linked by `source_spec_id` or equivalent relation.
- "implementation-bearing" must be deterministic. It should include ordinary functional/requirement/specification/protected-behavior records that require executable work. ADR/DCL records are excluded by default unless they explicitly carry implementation-bearing metadata. Governance specs may be implementation-bearing when their metadata or type-specific rules require code/config/test changes.
- The classifier must not use an LLM/API call. It may use spec type, status, section, tags, constraints metadata, source paths, and explicit project metadata.

Generated work item defaults:

- title: `Implement <spec id>: <spec title>` or a deterministic equivalent;
- origin: `new` unless a better existing taxonomy value is already established;
- stage/resolution: open/backlogged current-state values used by MemBase;
- `source_spec_id`: the confirmed spec id;
- `related_deliberation_ids`: originating DA id(s) when available;
- `related_spec_ids_at_creation`: the spec id plus any explicit affected-by/cross-cutting ids known at creation, with the existing rule that this is historical capture only;
- acceptance summary: derived from the spec title/description/testability at creation time.

### IP-6: Deterministic project-fit attachment

When automatic backlog intake creates or finds a work item, attempt project attachment only through deterministic evidence:

1. explicit spec metadata naming a project id;
2. existing project artifact link to the spec id;
3. exact active project membership rule recorded in project configuration or MemBase metadata;
4. a single unambiguous current work item/project relationship already present for the same spec family.

Do not use semantic similarity or title fuzzy matching for auto-attachment in this slice. If zero or multiple projects match, leave the work item unassigned and surface it in implementation-intake triage. Do not auto-create a new project.

### IP-7: Skill, rule, and glossary updates

Update the visible agent surfaces so future sessions consistently apply the new model:

- `.claude/rules/codex-review-gate.md` - distinguish project-scoped owner authorization from proposal-scoped bridge `GO`.
- `.claude/rules/file-bridge-protocol.md` - add optional Project Authorization section and review obligations.
- `.claude/rules/canonical-terminology.md` - define project authorization, implementation-bearing spec, and unassigned implementation intake.
- `.claude/skills/projects/SKILL.md` and generated Codex adapter - document project authorization commands.
- `.claude/skills/spec-intake/SKILL.md` and generated Codex adapter - document automatic backlog intake after confirmation.
- Harness capability registry and generated manifests as needed.

Protected narrative artifacts require formal artifact approval packets. This proposal authorizes preparing those packets as part of the implementation but does not waive the formal artifact approval gate.

### IP-8: Visibility and reconciliation

Add owner-visible and agent-readable outputs:

- spec confirmation output reports whether a work item was created, linked, skipped, or triaged;
- project show output lists active authorization status;
- integrity/triad checks can report specified implementation-bearing specs without linked active work items;
- post-implementation report must include created spec ids, work item ids, project authorization ids, and reconciliation evidence.

## Out Of Scope

- Skipping Loyal Opposition review or bridge `GO` for implementation proposals.
- Expanding project authorization to production deployment, credential lifecycle, destructive cleanup, history rewrite, or external-system mutation without separate approval gates.
- Auto-creating projects for unmatched specs.
- Semantic/LLM project-fit classification.
- Bulk retroactive creation of work items for all historical specified specs. This slice may add a read-only audit/dry-run command, but broad backfill requires a separate bridge proposal or explicit dry-run inventory packet.
- Replacing `current_work_items` as backlog authority.
- Removing proposal-level `target_paths` checks.

## Specification-Derived Verification Plan

### New tests

1. `platform_tests/scripts/test_project_authorization.py`
   - creates a project and owner-decision deliberation in a temporary DB;
   - authorizes the project;
   - verifies append-only versions, current view, active/revoked lifecycle, owner-decision validation, and JSON output.

2. `platform_tests/groundtruth_kb/test_spec_auto_backlog.py`
   - confirms a requirement/specification/protected-behavior spec creates or links exactly one work item;
   - confirms ADR/DCL records do not create implementation work unless explicit implementation-bearing metadata is present;
   - confirms duplicate confirmation or existing active `source_spec_id` does not create duplicate work items;
   - confirms deterministic project fit attaches to exactly one active project and ambiguous/no-fit cases remain unassigned.

3. `platform_tests/scripts/test_implementation_start_gate.py`
   - extends existing authorization tests to prove project authorization metadata can be recorded in packets;
   - proves stale/revoked/expired project authorization blocks any claim of project authorization coverage;
   - proves target paths remain proposal-scoped and are not broadened by project authorization.

4. `platform_tests/scripts/test_projects_cli.py`
   - covers new `gt projects authorize`, list/show authorization output, and revoke/update behavior.

5. `platform_tests/scripts/test_check_harness_parity.py`
   - confirms regenerated skill adapters and registry entries stay aligned.

6. `platform_tests/scripts/test_governing_specs_preserved.py` or a focused governance adoption test
   - verifies the new GOV/DCL/SPEC/PB rows exist with expected type/status and DA linkage.

### Required commands

- `python -m pytest platform_tests/scripts/test_project_authorization.py -q`
- `python -m pytest platform_tests/groundtruth_kb/test_spec_auto_backlog.py -q`
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q`
- `python -m pytest platform_tests/scripts/test_projects_cli.py -q`
- `python scripts/generate_codex_skill_adapters.py --check --update-registry`
- `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q`
- `python -m pytest platform_tests/scripts/test_governing_specs_preserved.py -q`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization`

### Spec-to-test mapping

| Requirement / spec | Verification evidence |
| --- | --- |
| Project authorization is bounded owner approval, not bridge bypass | `test_project_authorization.py`, `test_implementation_start_gate.py`, updated rule text, and post-implementation bridge verification. |
| Project authorization has an append-only envelope | `test_project_authorization.py` validates schema, current view, lifecycle transitions, and owner-decision validation. |
| Confirmed unmet implementation-bearing specs create/link work items | `test_spec_auto_backlog.py` validates positive, negative, duplicate, and metadata-driven cases. |
| Project fit attaches only with deterministic evidence | `test_spec_auto_backlog.py` validates explicit project id, existing artifact link, no-match, and ambiguous-match behavior. |
| Project authorization does not broaden target paths | `test_implementation_start_gate.py` validates target-path enforcement remains proposal-scoped. |
| Skills/rules teach the new model | adapter generation check plus harness parity test. |
| DA and spec linkage are preserved | governance adoption/focused DB tests verify new spec rows cite `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`. |

## Acceptance Criteria

- [ ] DA decision `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` is cited by new specs and implementation evidence.
- [ ] New MemBase specs and a new work item are created for this implementation scope before runtime behavior depends on them.
- [ ] MemBase has append-only project authorization storage and current-state read APIs.
- [ ] `gt projects` exposes project authorization creation, listing/showing, and revocation/update behavior.
- [ ] Proposal/implementation-start tooling can carry project authorization metadata while preserving latest-`GO` and `target_paths` enforcement.
- [ ] Confirming an unmet implementation-bearing spec creates or links one canonical work item.
- [ ] ADR/DCL specs do not create implementation work by default.
- [ ] Deterministic project fit attaches work items only to exactly one active matching project; otherwise work remains unassigned/triaged.
- [ ] Skill/rule/glossary surfaces are updated, with generated Codex adapters current.
- [ ] All tests and preflights in the verification plan pass.
- [ ] Post-implementation report lists created specs, work items, project authorization ids, file changes, commands, and reconciliation evidence.

## Risk And Rollback

### Risks

- **R1 (High): Authorization broadens too far.** Mitigation: authorization envelope is project-scoped, explicit, statused, revocable, and never replaces bridge `GO` or target paths.
- **R2 (High): Auto-backlog creates noisy or duplicate work.** Mitigation: deterministic implementation-bearing classifier, duplicate checks by `source_spec_id`, and unassigned triage rather than project invention.
- **R3 (Medium): Project fit becomes semantic guesswork.** Mitigation: this slice forbids fuzzy/LLM matching and requires explicit deterministic fit evidence.
- **R4 (Medium): Formal rule updates trip protected-artifact gates.** Mitigation: create formal artifact approval packets and include them in the post-implementation report.
- **R5 (Medium): Schema changes break existing project CLI behavior.** Mitigation: append-only additive schema, existing projects tests retained, and rollback by reverting implementation commit before data migration is relied upon.
- **R6 (Low): Skill adapter drift.** Mitigation: generated adapter check and harness parity tests.

### Rollback

If implementation fails before verification, revert source/rule/skill changes and leave the DA record as historical owner intent. Add a superseding work item or bridge revision if any MemBase spec/work-item rows were created and need retirement rather than deletion. Because MemBase is append-only, rollback of DB semantics should use new versions marking created records retired/superseded, not destructive deletion.

## Recommended Implementation Sequence

1. Create the governing MemBase specs and work item from `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`.
2. Add schema/current-view/helpers for project authorization.
3. Add CLI/service commands and JSON output.
4. Add automatic spec-to-work-item intake with deterministic implementation-bearing and project-fit classifiers.
5. Integrate project authorization metadata into bridge/implementation-start tooling without broadening target paths.
6. Update rules, glossary, skills, adapters, and approval packets.
7. Run focused tests and preflights.
8. File post-implementation report for Loyal Opposition verification.

## Prefiling Notes

This proposal intentionally keeps project authorization and proposal authorization separate:

- project authorization answers: "Has the owner authorized this bounded project of work?"
- bridge `GO` answers: "Is this particular implementation plan sound, sufficiently specified, and testable?"
- implementation-start authorization answers: "Is this session allowed to mutate these concrete target paths under the latest GO?"

The three layers should compose; none should erase another.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
