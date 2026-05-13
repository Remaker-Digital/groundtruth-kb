REVISED

# Implementation Proposal Revision - Project-Scoped Implementation Authorization + Automatic Spec Backlog Intake

bridge_kind: implementation_proposal_revision
Document: gtkb-project-scoped-implementation-authorization
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Responds-To: `bridge/gtkb-project-scoped-implementation-authorization-002.md`
Supersedes Proposal Metadata: `bridge/gtkb-project-scoped-implementation-authorization-001.md`
Recommended commit type: `feat:`
target_paths: ["groundtruth.db", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/intake.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/project/authorization.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "scripts/bridge_applicability_preflight.py", ".claude/rules/codex-review-gate.md", ".claude/rules/file-bridge-protocol.md", ".claude/rules/canonical-terminology.md", ".claude/skills/projects/SKILL.md", ".claude/skills/spec-intake/SKILL.md", ".codex/skills/projects/SKILL.md", ".codex/skills/spec-intake/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", ".groundtruth/formal-artifact-approvals/**", "platform_tests/scripts/test_project_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/groundtruth_kb/test_spec_auto_backlog.py", "platform_tests/scripts/test_projects_cli.py", "platform_tests/scripts/test_check_harness_parity.py", "platform_tests/scripts/test_governing_specs_preserved.py"]

## Revision Claim

This is a metadata-only proposal revision. It carries forward the full approved
implementation scope from `bridge/gtkb-project-scoped-implementation-authorization-001.md`
and corrects the `## Requirement Sufficiency` section to include the exact
machine-readable operative state required by `scripts/implementation_authorization.py`:
`Existing requirements sufficient`.

No source, test, configuration, MemBase, rule, skill, or formal artifact
implementation has been performed under this thread. The attempted Prime
Builder implementation-start packet failed closed before protected edits with:

```text
Approved proposal is missing ## Requirement Sufficiency
```

The failure occurred because `-001` used prose wording ("Existing requirements
are sufficient") instead of the exact required phrase. This revision preserves
the bridge audit trail by superseding the proposal metadata through a new
`REVISED` file rather than editing the prior version.

## Specification Links

**Blocking / directly governing:**

- `GOV-FILE-BRIDGE-AUTHORITY-001` - live `bridge/INDEX.md` remains the authoritative bridge queue; this revision preserves the append-only thread.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain inside the active `E:/GT-KB` project root and platform/application boundary.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites the relevant governing specifications before implementation approval.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification requires tests derived from the linked specifications and proposed new specs.
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

- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` - direct owner decision for project-scoped implementation authorization, automatic backlog intake for implementation-bearing specs, deterministic project attachment where supported, and no bridge bypass.
- `DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION` - related owner authorization pattern for scoped spec creation.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - MemBase `work_items` is the canonical backlog source of truth.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive to formalize standing backlog as DB-backed source of truth.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive AI judgment work should become deterministic service behavior where practical.
- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - future-work candidates flow to MemBase backlog and do not become implementation approval without owner/governance approval.

## Owner Decisions / Input

- On 2026-05-13, the owner agreed with the clean design direction: project-scoped owner authorization should exist, but proposal-level bridge review and implementation-start controls should remain.
- The owner stated that when an as-yet unmet specification is added, it should automatically be added to the backlog if it is functional or otherwise implementation-bearing rather than an ADR/DCL-only constraint.
- The owner stated that if the new specification fits an existing project, a new project may not be required.
- The owner asked that this deliberation be recorded in the Deliberation Archive. It has been recorded as `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`.

No additional owner decision is required for this metadata correction. Any later
production deployment, credential lifecycle action, destructive cleanup,
external-system mutation, bulk historical backfill, or expansion beyond the
target paths still requires the normal separate approval path.

## Requirement Sufficiency

Existing requirements sufficient. The owner decision is preserved in
`DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`, and the existing
GT-KB specifications already govern bridge authority, backlog authority, spec
intake, work-item creation, DA citation, project/work/spec linkage, and
spec/test/implementation triad completeness. No new or revised requirement is
required before beginning implementation of the bounded scope described here.

The implementation must still create the dedicated MemBase specs and work item
listed below before source-code runtime behavior depends on the new semantics.

## Scope Carried Forward

This revision carries forward the `-001` scope without expansion:

1. Formalize governing MemBase records from `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`.
2. Add append-only project authorization storage and current-state views/helpers.
3. Add `gt projects` authorization commands and JSON output.
4. Integrate project authorization metadata with proposal/implementation-start tooling while preserving bridge `GO` and target-path enforcement.
5. Add automatic backlog intake for newly confirmed unmet implementation-bearing specs.
6. Add deterministic project-fit attachment without semantic, fuzzy, or LLM matching.
7. Update rules, glossary, skills, adapters, and approval packets as required by protected artifact gates.
8. Add owner-visible reconciliation in confirmation output, project show output, integrity checks, and the post-implementation report.

## Proposed New Specs And Work Item

Implementation must create these MemBase records before source behavior depends
on the new semantics:

1. `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped authorization is a bounded owner approval source, not a replacement for bridge review.
2. `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - project authorization records must name project id, owner-decision DA id, status, scope, included/excluded work classes, allowed mutation classes, forbidden operations, optional expiration/supersession, and audit evidence.
3. `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001` - confirming a new unmet implementation-bearing spec creates or links a canonical work item.
4. `SPEC-PROJECT-FIT-AUTO-ATTACHMENT-001` - auto-created work items attach to an existing active project only through deterministic fit evidence; otherwise they remain in unassigned implementation intake.
5. `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization must not bypass Loyal Opposition review, bridge `GO`, target-path authorization packets, spec-derived tests, or post-implementation verification.
6. New work item: `Implement project-scoped authorization and automatic spec backlog intake`, with `source_spec_id` pointing at the primary new governance/spec record, `related_deliberation_ids` including `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`, and `related_bridge_threads` including this bridge document.

If an ID already exists, Prime Builder may use a fresh ID with the same semantic
title and must report the final IDs, versions, types, statuses, and change
reasons in the implementation report.

## Bulk/Backlog Visibility Evidence

This revision itself is not a bulk backlog mutation. The approved implementation
does create a small, explicit set of governing specs and one canonical work item
for this bridge scope. The implementation report must include an inventory
artifact listing created or linked spec IDs, work item IDs, project
authorization IDs, formal-artifact-approval packet paths, and reconciliation
evidence. This REVISED file is the review packet for the metadata correction.
Bulk historical backfill for all prior specified specs remains out of scope and
is a DECISION DEFERRED item requiring a separate bridge proposal or explicit
dry-run inventory packet.

## Specification-Derived Verification Plan

Required focused tests and checks:

- `python -m pytest platform_tests/scripts/test_project_authorization.py -q`
- `python -m pytest platform_tests/groundtruth_kb/test_spec_auto_backlog.py -q`
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q`
- `python -m pytest platform_tests/scripts/test_projects_cli.py -q`
- `python scripts/generate_codex_skill_adapters.py --check --update-registry`
- `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q`
- `python -m pytest platform_tests/scripts/test_governing_specs_preserved.py -q`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization`

Spec-to-test mapping:

| Requirement / spec | Verification evidence |
| --- | --- |
| Project authorization is bounded owner approval, not bridge bypass | `test_project_authorization.py`, `test_implementation_start_gate.py`, updated rule text, and post-implementation bridge verification. |
| Project authorization has an append-only envelope | `test_project_authorization.py` validates schema, current view, lifecycle transitions, and owner-decision validation. |
| Confirmed unmet implementation-bearing specs create/link work items | `test_spec_auto_backlog.py` validates positive, negative, duplicate, and metadata-driven cases. |
| Project fit attaches only with deterministic evidence | `test_spec_auto_backlog.py` validates explicit project id, existing artifact link, no-match, and ambiguous-match behavior. |
| Project authorization does not broaden target paths | `test_implementation_start_gate.py` validates target-path enforcement remains proposal-scoped. |
| Skills/rules teach the new model | adapter generation check plus harness parity test. |
| DA and spec linkage are preserved | governance adoption or focused DB tests verify new rows cite `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`. |

## Acceptance Criteria

- DA decision `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` is cited by new specs and implementation evidence.
- New MemBase specs and a new work item are created for this implementation scope before runtime behavior depends on them.
- MemBase has append-only project authorization storage and current-state read APIs.
- `gt projects` exposes project authorization creation, listing/showing, and revocation/update behavior.
- Proposal/implementation-start tooling can carry project authorization metadata while preserving latest-`GO` and `target_paths` enforcement.
- Confirming an unmet implementation-bearing spec creates or links one canonical work item.
- ADR/DCL specs do not create implementation work by default.
- Deterministic project fit attaches work items only to exactly one active matching project; otherwise work remains unassigned/triaged.
- Skill/rule/glossary surfaces are updated, with generated Codex adapters current.
- All tests and preflights in the verification plan pass.
- Post-implementation report lists created specs, work items, project authorization IDs, file changes, commands, and reconciliation evidence.

## Risk And Rollback

Risk remains unchanged from `-001`:

- Over-broad authorization is mitigated by explicit project authorization records, bridge `GO`, target-path scoping, formal artifact approval packets where required, and post-implementation verification.
- Noisy or duplicate work-item creation is mitigated by deterministic implementation-bearing classification and duplicate checks by `source_spec_id`.
- Project-fit guesswork is excluded in this slice; only deterministic evidence may attach a work item to a project.
- Protected narrative artifact writes require formal artifact approval packets before mutation.

Rollback is to stop before implementation or revert source/rule/skill changes
before verification. MemBase changes are append-only; if created records need
rollback, use superseding versions that retire or supersede them rather than
destructive deletion.

## Out Of Scope

- Skipping Loyal Opposition review or bridge `GO` for implementation proposals.
- Expanding project authorization to production deployment, credential lifecycle, destructive cleanup, history rewrite, or external-system mutation without separate approval gates.
- Auto-creating projects for unmatched specs.
- Semantic, LLM, or fuzzy project-fit classification.
- Bulk retroactive creation of work items for all historical specified specs.
- Replacing `current_work_items` as backlog authority.
- Removing proposal-level `target_paths` checks.

## Pre-Filing Preflight Self-Check

Candidate-content preflights passed before INDEX update:

- Credential scan using the bridge-propose helper's credential catalog: no hits.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization --content-file bridge\gtkb-project-scoped-implementation-authorization-003.md --json`
  - `preflight_passed: true`
  - `missing_required_specs: []`
  - `missing_advisory_specs: []`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization --content-file E:\GT-KB\bridge\gtkb-project-scoped-implementation-authorization-003.md`
  - `must_apply: 5`
  - `Evidence gaps in must_apply clauses: 0`
  - `Blocking gaps (gate-failing): 0`

The clause preflight was invoked with an absolute content-file path because the
current preflight renderer raises a `ValueError` for relative pending-content
paths when rendering the operative file path. That renderer defect is outside
this revision's target scope.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
