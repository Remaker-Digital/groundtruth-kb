NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-pb-2026-06-03-inventory-proposal
author_model: GPT-5 Codex
author_model_version: 2026-06-03 runtime
author_model_configuration: Codex Desktop default reasoning; bridge proposal authoring
author_metadata_source: Codex bridge helper explicit metadata

bridge_kind: implementation_proposal
Document: gtkb-project-membership-reconciliation-slice-1-inventory-tool
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-03 UTC
Session: keep-working-pb-2026-06-03-inventory-proposal
Recommended commit type: chore

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-GOV-004

target_paths: ["scripts/inventory_project_membership_reconciliation.py", "platform_tests/scripts/test_inventory_project_membership_reconciliation.py"]

# Implementation Proposal - Project Membership Reconciliation Slice 1 Inventory Tool

## Claim

Implement the read-only inventory/source-test slice authorized by `bridge/gtkb-project-membership-reconciliation-slice-1-scoping-002.md`. This slice adds deterministic source/test tooling only: a script that fresh-reads canonical MemBase project/work-item state, classifies every non-terminal work item exactly once, and emits JSON plus Markdown dry-run inventory output.

This proposal does not authorize live `groundtruth.db` mutation, project creation, project membership insertion, work-item retirement, duplicate disposition, dependency updates, generated bridge filings, or any bulk MemBase operation. It also does not implement the tool in this session; it files the implementation proposal for Loyal Opposition review first.

## Precedence And Dependency Check

The preceding scoping proposal and GO establish that backlog/project membership reconciliation should precede bulk execution from the project priority queue because 712 non-terminal work items were outside active project membership in the 2026-06-02 report. The only active project dependency identified by that report remains `PROJECT-GTKB-ROLE-ENHANCEMENT` depending on `PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION`; this inventory tool must surface dependency-blocked candidates and must not reorder or execute role-enhancement work.

No future mutation slice can safely precede this read-only inventory slice, because membership backfill, new project creation, terminal-only cleanup, and obsolete/duplicate disposition all need a fresh candidate set first. Existing narrower orphan-membership tooling is not a substitute because it does not classify the whole non-terminal work-item corpus.

## Proposed Implementation

Add `scripts/inventory_project_membership_reconciliation.py` as a deterministic read-only CLI. The script should:

1. Open the configured MemBase database through existing repo-native project/backlog APIs or structured SQLite reads against current-state views.
2. Fresh-read current projects, project dependencies, current work items, and active project work-item memberships at runtime.
3. Select all non-terminal work items using the repository's existing terminal-status conventions.
4. Classify every selected work item into exactly one primary class from the Slice 1 scoping taxonomy.
5. Include evidence fields for the assigned classification: current work-item status/stage/priority, active membership ids, compatibility `project_name`/`subproject_name`, related bridge/spec/deliberation/test/source signals when present, candidate project ids when inferred, and decision reason.
6. Emit machine-readable JSON and human-readable Markdown summaries without mutating MemBase.
7. Fail if any non-terminal work item is omitted, duplicated, or assigned to multiple primary classes.

Required primary classifications:

- `already_active_project_member`
- `dangling_or_terminal_project_membership`
- `existing_project_candidate_exact`
- `existing_project_candidate_weak`
- `new_project_candidate_cluster`
- `single_wi_project_candidate`
- `obsolete_or_duplicate_candidate`
- `dependency_blocked_candidate`
- `needs_manual_triage`

The implementation should prefer deterministic conservative classification over speculative inference. Weak matches and obsolete/duplicate candidates are recommendations only; they must remain non-mutating inventory rows until a separate owner/governed disposition path exists.

## CLI Contract

Suggested command shape:

```text
python scripts\inventory_project_membership_reconciliation.py --format json
python scripts\inventory_project_membership_reconciliation.py --format markdown
python scripts\inventory_project_membership_reconciliation.py --output-json .gtkb-state\project-membership-reconciliation\inventory.json --output-markdown .gtkb-state\project-membership-reconciliation\inventory.md
```

The default output should go to stdout. Optional output paths may write runtime artifacts under `.gtkb-state/project-membership-reconciliation/`; those runtime outputs are not source artifacts and are not part of the committed target paths.

## Out Of Scope

This slice must not:

- call `gt projects add-item` or `ProjectLifecycleService.add_project_item`;
- create, update, retire, or reorder projects;
- update work-item status, stage, priority, supersession, or compatibility fields;
- write directly to `groundtruth.db` except for ordinary read-only connection behavior;
- file bridge reports or owner decision records;
- collapse weak matches into exact matches without evidence;
- treat the 2026-06-02 report counts as stable constants.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - backlog/project visibility and bulk-operation discipline.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` - MemBase is the canonical backlog/project data authority.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` - backlog/project data must use governed schema/current-state semantics.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped implementation authorization applies.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - allowed mutation classes must match the implementation; this proposal is limited to `cli_extension` and `test_addition` under the cited PAUTH.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass bridge review or verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal declares Project Authorization, Project, and Work Item metadata.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - motivates the reconciliation inventory and future membership repair.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - runtime counts and classifications must come from fresh canonical reads.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` - generated inventory/report output must prove fresh-read behavior.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation reports must map specs to executable verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - future project creation, membership, retirement, duplicate disposition, and dependency changes require separate lifecycle handling.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - dry-run packets and follow-on decisions must be durable artifacts when they cross the decision threshold.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge INDEX remains the canonical proposal/review state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation targets stay inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner direction to formalize the backlog as a structured, durable, queryable implementation queue.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - MemBase `work_items` as the canonical backlog source of truth.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-approved governance-hardening authorization including `GTKB-GOV-004` and allowing `cli_extension` plus `test_addition`.
- `DELIB-2521` - source-of-truth freshness principle; current project association must come from fresh canonical reads, not cached reports or compatibility fields alone.
- `DELIB-2509` - precedent for narrowing membership-remediation work to source/test tooling while deferring live canonical assignment/retire mutations.
- `DELIB-2631` and `bridge/gtkb-orphan-wi-membership-backfill-slice-2-implementation-004.md` - GO precedent for assign-only source/test tooling that excludes live canonical `--apply` and retire/exclude mutation.
- `DELIB-2757` and `bridge/gtkb-role-enhancement-isolation-dependency-reframe-005.md` - accepted precedence handling for the role-enhancement/isolation dependency.
- `bridge/gtkb-legacy-gov-wi-cleanup-003.md` and `bridge/gtkb-legacy-gov-wi-cleanup-004.md` - precedent that `GTKB-GOV-004` is active and that mutation-class mismatch must be resolved by narrowing scope or obtaining matching authorization.
- `bridge/gtkb-project-membership-reconciliation-slice-1-scoping-001.md` and `bridge/gtkb-project-membership-reconciliation-slice-1-scoping-002.md` - direct parent scoping proposal and GO for this source/test inventory proposal.

## Owner Decisions / Input

No new owner decision is needed for this read-only source/test proposal. Owner approval for the work item and PAUTH is already recorded in `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`, and the preceding GO authorizes filing this follow-on implementation proposal.

Future live membership insertion, project creation, work-item retirement, duplicate disposition, dependency mutation, or owner-decision packet filing remains out of scope and will require a separate proposal and matching authorization.

## Requirement Sufficiency

Existing requirements are sufficient for a read-only inventory CLI and tests under the cited PAUTH because the allowed mutation classes include `cli_extension` and `test_addition`, and `GTKB-GOV-004` is included in the active governance-hardening authorization.

Existing requirements are not sufficient for live MemBase mutation, project creation, project membership insertion, work-item retirement, duplicate disposition, or dependency updates. Those operations are expressly deferred.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Tool reads MemBase/project metadata only and must not print environment values or credentials. | Staged secret scan and fixture review. | |
| CQ-PATHS-001 | Yes | Source/test targets are inside `E:\GT-KB`; optional runtime outputs stay under `.gtkb-state/`. | Bridge applicability preflight and path assertions in tests. | |
| CQ-COMPLEXITY-001 | Yes | Keep classification logic decomposed into small functions for loading state, deriving evidence, classifying, rendering JSON, and rendering Markdown. | Focused unit tests for each classification family. | |
| CQ-CONSTANTS-001 | Yes | Classification labels should be explicit constants with tests covering the complete set. | Tests assert exact taxonomy coverage. | |
| CQ-SECURITY-001 | Yes | Read-only DB access only; no shelling out for mutation commands. | Tests monkeypatch/inspect no mutation paths and run CLI smoke. | |
| CQ-DOCS-001 | Yes | CLI help and Markdown summary should describe read-only/dry-run status without implying approval to mutate. | CLI `--help`/Markdown snapshot tests. | |
| CQ-TESTS-001 | Yes | Add platform tests using synthetic/project fixture data and one live smoke that does not assert unstable counts. | `python -m pytest platform_tests\scripts\test_inventory_project_membership_reconciliation.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | | | One-shot inventory CLI can emit structured output/errors; no long-running logging surface. |
| CQ-VERIFICATION-001 | Yes | Implementation report must map every governing spec to a concrete command or test. | Post-implementation report and LO verification. | |

## Specification-Derived Verification Plan

Implementation verification must include:

- Bridge state: read live `bridge/INDEX.md` and run `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-project-membership-reconciliation-slice-1-inventory-tool --format json`; expected result is an indexed latest NEW/GO chain with no drift before implementation, then latest REVISED after report filing.
- Project linkage: `groundtruth-kb\.venv\Scripts\gt.exe backlog show GTKB-GOV-004 --json`, `gt projects show PROJECT-GTKB-GOVERNANCE-HARDENING --json`, and `gt projects authorizations PROJECT-GTKB-GOVERNANCE-HARDENING --json` confirm active/open work item and active PAUTH coverage.
- Focused tests: `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_inventory_project_membership_reconciliation.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-project-membership-inventory`.
- CLI smoke: run the new script in JSON and Markdown modes and assert it exits 0, includes all taxonomy labels in summary metadata, and reports no duplicate/omitted non-terminal work items.
- Lint/format: `groundtruth-kb\.venv\Scripts\ruff.exe check scripts\inventory_project_membership_reconciliation.py platform_tests\scripts\test_inventory_project_membership_reconciliation.py` and matching `ruff format --check`.
- Staged governance checks before commit: whitespace check, staged secret scan, inventory-drift check, narrative-artifact evidence check, and staged ruff-format check.

## Acceptance Criteria

- `scripts/inventory_project_membership_reconciliation.py` exists and is a read-only CLI.
- `platform_tests/scripts/test_inventory_project_membership_reconciliation.py` covers all nine primary classifications, duplicate/omission failure handling, JSON rendering, Markdown rendering, and optional output-path behavior.
- The CLI fresh-reads current MemBase state at runtime and does not rely on the 2026-06-02 report counts as constants.
- Every non-terminal work item is represented exactly once in the JSON inventory.
- Output clearly separates safe existing-project candidates, weak candidates, new-project candidates, obsolete/duplicate candidates, terminal-only cleanup candidates, dependency-blocked candidates, and manual triage rows.
- No live project/work-item/database mutation path exists in this slice.
- The implementation report explicitly states that follow-on mutation slices still require separate authorization.

## Risks And Mitigations

- Risk: heuristic classification is mistaken for mutation approval. Mitigation: output labels are recommendations only, and the script has no apply/mutate mode.
- Risk: stale report metrics leak into tests. Mitigation: tests use synthetic fixture state for exact counts and live smoke tests assert invariants, not fixed live totals.
- Risk: weak matches are over-classified as exact. Mitigation: exact matches require durable evidence; ambiguous matches become `existing_project_candidate_weak` or `needs_manual_triage`.
- Risk: output volume becomes hard to review. Mitigation: JSON remains complete while Markdown groups by class/priority and summarizes decision-needed rows.
- Risk: future mutation slices bundle too much work. Mitigation: acceptance criteria preserve separate packets for membership backfill, project creation, obsolete/duplicate disposition, and terminal-only cleanup.

## Rollback

Rollback for this proposal is append-only bridge state: Loyal Opposition can issue NO-GO, or Prime Builder can file a REVISED/WITHDRAWN follow-up. If later implemented, code rollback is normal git revert of the script/test commit; no MemBase runtime state should have changed.

## Request To Loyal Opposition

Please review whether this proposal correctly implements the scoping GO as a read-only source/test inventory slice under the cited PAUTH. A GO should authorize only the two target paths and the read-only CLI/test implementation described here.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
