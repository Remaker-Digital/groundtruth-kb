NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 4e30eeba-5f51-4cad-89fd-793ac8f59e98
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: Claude Code interactive; role=prime-builder; output_style=explanatory
author_metadata_source: interactive Claude runtime envelope plus hand-authored bridge proposal

# Implementation Proposal - WI-3217 Pipeline Lifecycle Metrics Data Model & Collection Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3217-pipeline-lifecycle-metrics-coverage
Version: 001 (NEW)
Date: 2026-06-25 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3217

target_paths: ["platform_tests/scripts/test_pipeline_events_spec2099_coverage.py"]

## Claim

WI-3217 should add explicit deterministic coverage for the live `SPEC-2099`
"Pipeline lifecycle metrics: data model and collection" contract and route that
evidence through the bridge for Loyal Opposition verification.

`SPEC-2099` is implemented GT-KB platform infrastructure (the `pipeline_events`
table and its collection methods in `groundtruth-kb/src/groundtruth_kb/db.py`),
not an Agent Red application feature. The owner authorization snapshot
nevertheless includes `WI-3217`, and the WI is still open/backlogged in
`PROJECT-AGENT-RED-TEST-COVERAGE-GAPS`. The WI was classified γ' (phantom-only
evidence) by the 16.B methodology review (`DELIB-0712`): MemBase maps `SPEC-2099`
only to `TEST-11218` ("Spec-derived test for SPEC-2099"), a placeholder with no
`test_file` path and no `assertion_runs`.

Current live state contradicts the historical "phantom-only" framing in one
important way that this proposal scopes around honestly: a real, comprehensive
suite already exists on disk at `groundtruth-kb/tests/test_pipeline_events.py`
(39 tests across the public `record_event` API, automatic emission from
KnowledgeDB mutations, transaction atomicity, query methods, metadata contracts,
export, indexes, and rollback atomicity). That suite covers the **behavioral
emission and collection surface** thoroughly, but it is not bridged/mapped to
`WI-3217`, and it does **not** deterministically assert four `SPEC-2099`
data-model clauses:

1. **Schema/data-model conformance** — the `pipeline_events` table carries the
   exact `SPEC-2099`-required column set with the required `NOT NULL` and
   primary-key constraints.
2. **Append-only / write-once** — `SPEC-2099` states "This table is append-only,
   write-once. Events are never updated or deleted." No existing test asserts the
   public API exposes no update/delete path and that each record is a distinct
   immutable row.
3. **`duration_ms` round-trip** — the timed-event column is never exercised by the
   existing suite.
4. **Full `event_type` vocabulary** — `SPEC-2099` enumerates 17 event types; the
   existing suite exercises only the auto-emitted subset plus arbitrary strings.

This proposal is therefore a bounded `test_addition` item. It adds one focused
platform test module that closes those four data-model gaps **without
duplicating** the existing behavioral-emission coverage (it references the
existing suite for that surface and asserts only a minimal side-effect-collection
contract). It expects no production source mutation: `groundtruth-kb/src/groundtruth_kb/db.py`
remains the read-only implementation surface under test.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-2099` (status `implemented`, P1) gives a complete data-model and collection
contract: the `pipeline_events` table column set, the append-only/write-once
discipline, the 17-value `event_type` enumeration, the `duration_ms` timed-event
field, the `metadata` JSON field, and the side-effect collection mechanism
("Events are recorded by existing hooks and KnowledgeDB methods as side effects.
No manual event recording required."). That is enough detail for deterministic
coverage.

The current WI is a test-coverage gap, not a new feature request. No owner
clarification is required because the proposal only adds tests over the
already-implemented, in-root platform behavior and does not add new work items,
formal artifacts, release state, deployment state, credentials, or Agent Red
application behavior.

Observed implementation extension (documented, not a defect, not in scope to
change): the live schema includes an additive `artifact_version INTEGER` column
that is not in the `SPEC-2099` column list. The new test recognizes it as an
implemented extension and asserts the spec-required columns are all present
rather than asserting the column set is closed.

## In-Root Placement Evidence

The implementation target is under the GT-KB root:

- `E:\GT-KB\platform_tests\scripts\test_pipeline_events_spec2099_coverage.py`

Read-only verification may inspect these in-root implementation and historical
evidence paths:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py` (pipeline_events table at
  line 782; `_record_event`, `record_event`, `list_events`,
  `get_events_for_artifact` at lines 7590-7699)
- `E:\GT-KB\groundtruth-kb\tests\test_pipeline_events.py` (existing behavioral
  suite)
- `E:\GT-KB\platform_tests\unit\test_knowledge_db_artifacts.py` (table-presence
  reference only)

## Specification Links

- `SPEC-2099` - Direct requirement: append-only `pipeline_events` table data
  model (column set, constraints), 17-value event-type vocabulary, `duration_ms`
  timed events, and side-effect collection mechanism.
- `GOV-08` - Canonical Knowledge Database / MemBase behavior; `pipeline_events`
  is a governed append-only MemBase table and the test asserts its canonical
  append-only discipline.
- `GOV-10` - Test artifacts must exercise live project interfaces; this proposal
  adds executable tests over the production `KnowledgeDB` event interface instead
  of phantom-only evidence.
- `SPEC-1649` - Master test plan / live-interface policy; the new test file
  provides deterministic repository-native coverage.
- `GOV-12` - Work-item remediation must create or map test evidence.
- `GOV-13` - Test visibility and phase governance; the new test file creates
  visible executable evidence for the WI.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - `pipeline_events` is an append-only
  source-of-truth surface; the test proves recorded events are durably and
  queryably preserved without overwrite.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner
  authorization is required but does not replace bridge review, `GO`, target
  paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies changed-file hygiene; Python
  coverage uses targeted pytest plus ruff check and ruff format checks on the
  touched test file.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner decisions are cited from existing
  AUQ-backed project authorization; this proposal requests no new owner decision.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority,
  role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this
  proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation
  verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project
  authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms all files are under
  `E:\GT-KB`; this proposal does not depend on out-of-root archives.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal
  uses the existing authorized WI and does not add project scope.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence
  for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and
  review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as
  a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project
authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`,
citing owner decision `DELIB-20265586` (2026-06-23), and remains inside
snapshot-bound project member `WI-3217`. The authorization's allowed mutation
classes include `test_addition`, which is the only mutation class this proposal
exercises.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red
  test-coverage-gap project; the standing authority for this WI's implementation.
- `DELIB-0712` - POR Step 16.B methodology review classifying `SPEC-2099` as γ'
  (phantom-only evidence) and scheduling it for live-interface remediation per
  GOV-10. This proposal is the remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected
  assertion-only verification for behavioral requirements; this proposal supplies
  executable test evidence rather than assertion-only coverage.
- Deliberation Archive search for "pipeline lifecycle events data model
  collection SPEC-2099 append-only" returned no WI/spec-specific record; the
  closest semantic hit is `DELIB-0018` (Project Progress Dashboard KPI Proposal),
  which motivated lifecycle metrics conceptually but predates the
  `pipeline_events` implementation and does not provide coverage for this WI.
- `gt bridge threads --wi WI-3217 --json` returned `match_count: 0` before this
  proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt projects show PROJECT-AGENT-RED-TEST-COVERAGE-GAPS --json` shows `WI-3217`
  open/backlogged among 7 remaining members (31 of 38 resolved); the PAUTH
  `included_work_item_ids` snapshot includes `WI-3217`.
- `gt spec show SPEC-2099` shows status `implemented`, type `requirement`,
  priority P1, and the full data-model + collection requirement text.
- `gt tests list --spec-id SPEC-2099` returns only `TEST-11218` ("Spec-derived
  test for SPEC-2099"), a phantom placeholder with no `test_file` path.
- `groundtruth-kb/src/groundtruth_kb/db.py:782` defines the `pipeline_events`
  table: `id TEXT PK NOT NULL, event_type TEXT NOT NULL, session_id TEXT,
  artifact_id TEXT, artifact_type TEXT, artifact_version INTEGER, timestamp TEXT
  NOT NULL, duration_ms INTEGER, metadata TEXT, changed_by TEXT NOT NULL`, plus
  indexes `idx_pe_event_type_ts`, `idx_pe_artifact`, `idx_pe_session_ts`.
- `groundtruth-kb/src/groundtruth_kb/db.py:7590-7699` implements `_record_event`
  (within-transaction, no commit), `record_event` (public, commits),
  `list_events`, and `get_events_for_artifact`. There is no public update or
  delete method for `pipeline_events`.
- `groundtruth-kb/tests/test_pipeline_events.py` already covers the behavioral
  emission and collection surface comprehensively but is not WI-bridged and does
  not assert the four data-model clauses enumerated in the Claim.

## Proposed Scope

1. Add `platform_tests/scripts/test_pipeline_events_spec2099_coverage.py`.
2. Schema/data-model conformance: open a temp `KnowledgeDB`, read
   `PRAGMA table_info('pipeline_events')`, and assert every `SPEC-2099`-required
   column is present (`id`, `event_type`, `session_id`, `artifact_id`,
   `artifact_type`, `timestamp`, `duration_ms`, `metadata`, `changed_by`); assert
   `id` is the primary key and that `id`, `event_type`, `timestamp`, `changed_by`
   are `NOT NULL`; assert the additive `artifact_version` column is present as a
   recognized implementation extension.
3. Index presence: assert `idx_pe_event_type_ts`, `idx_pe_artifact`, and
   `idx_pe_session_ts` exist via `PRAGMA index_list`.
4. Append-only / write-once: assert `KnowledgeDB` exposes no public
   `update_event`/`delete_event`/`remove_event` surface for `pipeline_events`;
   assert recording N events through `record_event` yields N distinct rows with
   unique UUID ids and that a subsequent insert never mutates or removes a prior
   row (count is monotonic; a pre-existing row is byte-stable after later
   inserts).
5. `duration_ms` round-trip: record a timed event with `duration_ms` and assert
   `list_events` / `get_events_for_artifact` return the stored value; record one
   without `duration_ms` and assert `NULL`/`None`.
6. Full `event_type` vocabulary: record each of the 17 `SPEC-2099`-enumerated
   event types through `record_event` and assert each is stored and queryable by
   `event_type`.
7. Collection mechanism (minimal side-effect contract, non-duplicative): assert
   one representative automatic emission (e.g. `insert_spec` emits a
   `spec_transition` row for the artifact) to prove the side-effect collection
   path is live, and reference `groundtruth-kb/tests/test_pipeline_events.py` for
   the exhaustive per-mutation emission coverage rather than re-asserting it.
8. Do not change production source, formal artifacts, project membership,
   release/deployment state, existing MemBase test rows, credentials, or Agent Red
   application behavior.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-2099` (data model) | `PRAGMA table_info` / `index_list` assertions prove the table carries the spec-required columns, constraints, primary key, and indexes (plus the additive `artifact_version`). |
| `SPEC-2099` (append-only/write-once) | Tests prove no public update/delete surface and that records are distinct, unique-id, and immutable across later inserts. |
| `SPEC-2099` (`duration_ms`, event-type vocabulary) | Tests round-trip `duration_ms` and record + query all 17 enumerated event types. |
| `SPEC-2099` (collection mechanism) | A representative automatic-emission assertion proves the side-effect path; exhaustive per-mutation coverage is referenced in the existing suite, not duplicated. |
| `GOV-08`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Append-only/immutability and queryable-preservation assertions prove the canonical SoT discipline of the table. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the live `KnowledgeDB` event interface, creating an explicit test file for WI-3217 rather than relying on phantom-only evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3217-pipeline-lifecycle-metrics-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check`, `ruff format --check`, targeted pytest, adjacent pytest, and a whitespace diff check on the touched file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest platform_tests/scripts/test_pipeline_events_spec2099_coverage.py -q --tb=short
python -m pytest platform_tests/scripts/test_pipeline_events_spec2099_coverage.py groundtruth-kb/tests/test_pipeline_events.py -q --tb=short
python -m ruff check platform_tests/scripts/test_pipeline_events_spec2099_coverage.py
python -m ruff format --check platform_tests/scripts/test_pipeline_events_spec2099_coverage.py
git diff --check -- platform_tests/scripts/test_pipeline_events_spec2099_coverage.py
```

## Acceptance Criteria

- PASS when `PRAGMA table_info('pipeline_events')` confirms all `SPEC-2099`
  required columns, the `id` primary key, and the `NOT NULL` constraints on
  `id`/`event_type`/`timestamp`/`changed_by`.
- PASS when the three required indexes are present.
- PASS when no public update/delete surface for `pipeline_events` exists and N
  recorded events yield N distinct immutable unique-id rows.
- PASS when `duration_ms` round-trips for timed events and is `None` when omitted.
- PASS when all 17 enumerated `event_type` values are recordable and queryable.
- PASS when a representative automatic emission proves the side-effect collection
  path is live.
- PASS when targeted pytest, adjacent pytest, ruff check, ruff format check, and
  diff whitespace checks pass.
- PASS when no production source, formal artifacts, project membership, new work
  items, credentials, release tags, deployment state, or Agent Red application
  behavior are changed.

## Risks / Rollback

Risk is low. This is additive test coverage over implemented platform behavior.
The main implementation risk is brittle coupling to SQLite schema internals; the
proposal mitigates that by asserting the spec-required column/constraint contract
via `PRAGMA` (tolerant of additive columns like `artifact_version`) rather than
asserting an exact closed schema string.

Rollback is to delete `platform_tests/scripts/test_pipeline_events_spec2099_coverage.py`.
Bridge audit files remain append-only.

## Files Expected To Change

- `platform_tests/scripts/test_pipeline_events_spec2099_coverage.py`

## Pre-Filing Preflight Evidence

Both mandatory preflights were run against this draft body
(`--content-file`) before filing. Loyal Opposition should rerun both against
the operative bridge file.

Applicability preflight (`scripts/bridge_applicability_preflight.py --content-file ... --json`):

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `work_items: ["WI-3217"]`
- `warnings.missing_parent_dirs: []`
- draft `packet_hash: sha256:a9a1f6b2a0f670870f6ba2a53ec6db0dac9fc3d3715dbc095dd4c3436cf60a76`
  (recorded for the draft; the operative bridge file's hash will differ once
  author metadata/Document headers settle — LO should recompute against the
  filed file).

Clause preflight (`scripts/adr_dcl_clause_preflight.py --content-file ...`):

- clauses evaluated: `5`
- must_apply: `4`, may_apply: `1`, not_applicable: `0`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

Phantom-spec sweep: all 19 cited SPEC/GOV/ADR/DCL ids confirmed present in the
live `specifications` table via `KnowledgeDB.get_spec()`.

## Recommended Commit Type

`test:`
