NO-GO

# Loyal Opposition Review - gt backlog add CLI

bridge_kind: lo_verdict
Document: gtkb-gt-backlog-add-cli
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-gt-backlog-add-cli-001.md`
Verdict: NO-GO

## Verdict

NO-GO. The proposal identifies the right feature, but the scoped CLI does not satisfy WI-3270's operative requirements for evidence preservation, dry-run behavior, candidate-state semantics, or project membership behavior.

## Reviewed Materials

- `bridge/INDEX.md`
- `bridge/gtkb-gt-backlog-add-cli-001.md`
- `groundtruth.db` current `WI-3270` row, queried with `KnowledgeDB.get_work_item("WI-3270")`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/tests/test_project_artifacts.py`
- Mandatory applicability and clause preflights below

## Prior Deliberations

- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - owner decision that future-work candidates flow to MemBase, not `MEMORY.md`, while implementation approval remains separate.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive formalizing backlog as DB-backed source of truth with provenance and linkage fields.
- `DELIB-1791` and `DELIB-1790` - prior NO-GOs on the GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH scoping thread; relevant to backlog source-of-truth and verification strictness.

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "WI-3270 gt backlog add CLI GOV-STANDING-BACKLOG" --limit 5`
- `python -m groundtruth_kb deliberations search "standing backlog formal source of truth work_items review consideration candidate dry-run related specs bridge threads" --limit 8`

## Findings

### F1 - P1 - The CLI omits WI-3270's required evidence and dry-run fields

Observation: The proposal says existing requirements are sufficient and cites WI-3270 plus `GOV-STANDING-BACKLOG-001` as fully specifying the surface (`bridge/gtkb-gt-backlog-add-cli-001.md:46`). The current WI-3270 row says the command should default to a review/consideration candidate state, require normal evidence fields, preserve source owner directive and related specs/bridge threads, support dry-run output, and emit the created WI id. The proposed CLI options are limited to `--title`, `--origin`, `--component`, `--description`, optional `--source-spec-id`, `--priority`, and `--project-name` (`bridge/gtkb-gt-backlog-add-cli-001.md:22`, `bridge/gtkb-gt-backlog-add-cli-001.md:66` through `bridge/gtkb-gt-backlog-add-cli-001.md:72`). The pseudocode writes only those fields plus status/stage defaults (`bridge/gtkb-gt-backlog-add-cli-001.md:75` through `bridge/gtkb-gt-backlog-add-cli-001.md:79`).

Deficiency rationale: The live work-item API already has the provenance fields the WI calls for: `source_owner_directive`, `source_deliberation_query`, `related_deliberation_ids`, `related_spec_ids_at_creation`, and `related_bridge_threads` (`groundtruth-kb/src/groundtruth_kb/db.py:3273` through `groundtruth-kb/src/groundtruth_kb/db.py:3277`). A creation CLI that omits these fields would institutionalize low-fidelity backlog rows at exactly the point where the owner asked for durable evidence.

Impact: Agents could capture future work in MemBase, but the resulting rows would lose the why/source/spec/thread context needed for later review, prioritization, and implementation proposals.

Recommended action: Revise the CLI scope to include the evidence fields required by WI-3270, add `--dry-run`, and define the default review/consideration candidate state explicitly. Tests should assert every required field is persisted and that `--dry-run` emits the would-create payload without mutating `work_items`.

### F2 - P1 - The project membership test cannot be satisfied by the proposed implementation

Observation: The verification plan requires `test_backlog_add_project_name_creates_membership` (`bridge/gtkb-gt-backlog-add-cli-001.md:97`), but the pseudocode only passes `project_name=project_name` into `db.insert_work_item()` (`bridge/gtkb-gt-backlog-add-cli-001.md:75` through `bridge/gtkb-gt-backlog-add-cli-001.md:79`). Live code treats `project_name` as a compatibility field that backfills project memberships during `KnowledgeDB` initialization (`groundtruth-kb/src/groundtruth_kb/db.py:930`). Existing tests verify that behavior only after closing and reopening the DB (`groundtruth-kb/tests/test_project_artifacts.py:103` through `groundtruth-kb/tests/test_project_artifacts.py:120`). A review probe confirmed `same_connection_memberships []` immediately after `insert_work_item(..., project_name="My Project")`, with membership appearing only after reopening the DB.

Deficiency rationale: If the command promises immediate membership attachment, it must call the project layer (`ProjectLifecycleService.add_project_item` or `db.link_project_work_item`) after creating the work item. That explicit API exists at `groundtruth-kb/src/groundtruth_kb/db.py:3707`, and the existing CLI exposes `gt projects add-item` at `groundtruth-kb/src/groundtruth_kb/cli.py:689`.

Impact: The proposed test either fails against the pseudocode or is weakened to rely on reopen-time compatibility backfill, leaving users with surprising behavior in the same CLI process.

Recommended action: Decide whether `--project-name` is only a compatibility string or an immediate first-class project membership. If it is membership, resolve or create the project and call the project membership service in the same command, then assert same-connection membership visibility. If it is only compatibility metadata, rename the test and user-facing wording so it does not claim membership attachment.

### F3 - P1 - The auto-ID race mitigation is asserted but not specified

Observation: The proposal says `WI-NNNN` is generated from the highest existing ID (`bridge/gtkb-gt-backlog-add-cli-001.md:22`) and the pseudocode calls `_next_wi_id(db)` before `db.insert_work_item(...)` (`bridge/gtkb-gt-backlog-add-cli-001.md:74` through `bridge/gtkb-gt-backlog-add-cli-001.md:75`). The risk section acknowledges rapid auto-ID generation could race and says the mitigation is a SQLite transaction around max-id plus insert (`bridge/gtkb-gt-backlog-add-cli-001.md:109`). But the proposal does not specify that transaction boundary or the locking mode, and `insert_work_item` commits its own insert path (`groundtruth-kb/src/groundtruth_kb/db.py:3380`).

Deficiency rationale: ID allocation from `MAX(id)` is only safe if allocation and insert are inside one transaction that prevents another writer from seeing the same max and inserting the same next ID. The proposal names the risk but does not define the required implementation invariant or test it.

Impact: A CLI meant for low-ceremony agent capture can fail or collide under parallel agent use, which is the same operating pattern this session is actively exercising.

Recommended action: Specify the transaction/locking approach, such as `BEGIN IMMEDIATE` around max-id allocation plus insert or a retry-on-unique-conflict loop, and add a concurrency regression test that exercises two simultaneous `gt backlog add` invocations.

### F4 - P2 - Applicability preflight still reports missing advisory specs

Observation: The mandatory preflight passes blocking specs, but reports missing advisory specs:

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

Deficiency rationale: The bridge protocol's pre-filing subsection expects both `missing_required_specs: []` and `missing_advisory_specs: []`; non-empty missing spec lists are self-detected defects to clear before filing.

Impact: The proposal is missing durable governance context for artifact-oriented backlog capture and lifecycle-trigger handling.

Recommended action: Cite the applicable advisory specs in the revised `Specification Links` section or document why each does not apply after revising the proposal text.

## Applicability Preflight

- packet_hash: `sha256:41ce61b55ba887e5f3fd6d7d57155bdeee2b5ca3fa4da2c48be1d305ad1e616b`
- bridge_document_name: `gtkb-gt-backlog-add-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-gt-backlog-add-cli-001.md`
- operative_file: `bridge/gtkb-gt-backlog-add-cli-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-gt-backlog-add-cli`
- Operative file: `bridge\gtkb-gt-backlog-add-cli-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate when evidence is absent and no owner waiver line is cited. No blocking gap was reported here.

## Verification Commands

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gt-backlog-add-cli` - passed blocking preflight, advisory specs missing as shown above.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gt-backlog-add-cli` - exit 0, no blocking gaps.
- `python -m pytest groundtruth-kb/tests/test_project_artifacts.py::test_compatibility_backfill_maps_project_strings_to_project_memberships -q --tb=short` - passed, confirming current reopen-time project-name compatibility behavior.
- Review probe against a temporary DB: immediate `list_project_work_items("PROJECT-MY-PROJECT")` returned `[]` after `insert_work_item(..., project_name="My Project")`; reopening the DB produced the membership row.
- `KnowledgeDB.get_work_item("WI-3270")` against root `groundtruth.db` - confirmed WI-3270 requires dry-run output, normal evidence fields, source owner directive, related spec/bridge-thread preservation, candidate-state semantics, and WI-id emission.
